import 'dart:async';
import 'dart:convert';
import 'dart:io' show Platform;
import 'dart:typed_data';

import 'package:flutter/foundation.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';
import 'package:permission_handler/permission_handler.dart';

import '../core/local_store.dart';

/// Trạng thái kết nối với kính.
enum FrameLinkState { idle, scanning, connecting, connected }

/// Kết nối kính phiên dịch **Brilliant Labs Frame** qua Bluetooth LE và đẩy
/// bản dịch lên màn hình của kính theo thời gian thực.
///
/// Giao thức (BLE UART kiểu Nordic của Frame):
///  - Service  `7a230001-…`
///  - TX       `7a230002-…`  (điện thoại ghi → kính, chuỗi Lua được chạy ngay)
///  - RX       `7a230003-…`  (kính thông báo → điện thoại, kết quả `print`)
///  - Byte `0x03` = ngắt chương trình Lua đang chạy.
///
/// Không cần nạp script Lua lên kính: mỗi lần cập nhật chỉ gửi vài lệnh
/// `frame.display.text(...)` + `frame.display.show()` — giống app Frame gốc
/// (frame_flutter_translate_host) nhưng không phụ thuộc gói simple_frame_app.
///
/// MƯỢT: giống app Frame, chỉ giữ **bản mới nhất** — nếu đang gửi dở mà có chữ
/// mới thì bỏ các bản trung gian, không xếp hàng, nên chữ không bị trễ khi
/// người nói nhanh.
///
/// Là singleton: kết nối sống qua các màn hình, không bị ngắt khi đổi tab.
class FrameService extends ChangeNotifier {
  FrameService._();
  static final FrameService instance = FrameService._();

  static final _serviceUuid = Guid('7a230001-5475-a6a4-654c-8431f6ad49c4');
  static final _txUuid = Guid('7a230002-5475-a6a4-654c-8431f6ad49c4');
  static final _rxUuid = Guid('7a230003-5475-a6a4-654c-8431f6ad49c4');

  // --- Bố cục chữ trên màn hình 640x400 của kính (giống frame_app.lua gốc) ---
  static const _lineHeight = 60; // px giữa các dòng
  static const _maxLines = 4; // hiện tối đa 4 dòng cuối
  static const _lineUnits = 24; // số "ký tự" mỗi dòng (CJK tính 2)
  static const _minInterval = Duration(milliseconds: 90); // chống tràn BLE
  static const _prefLastDevice = 'frame_last_device';
  static const _prefStrip = 'frame_strip_diacritics';

  final _store = LocalStore();

  FrameLinkState _state = FrameLinkState.idle;
  FrameLinkState get state => _state;
  bool get isConnected => _state == FrameLinkState.connected;
  bool get isBusy =>
      _state == FrameLinkState.scanning || _state == FrameLinkState.connecting;

  String? _deviceName;
  String? get deviceName => _deviceName;

  String? _error;
  String? get error => _error;

  List<ScanResult> _results = const [];
  List<ScanResult> get results => _results;

  /// Font mặc định của kính chủ yếu vẽ được chữ Latin cơ bản, nên bỏ dấu tiếng
  /// Việt (và các dấu Latin khác) trước khi gửi. Tắt nếu firmware kính của bạn
  /// đã có font đầy đủ.
  bool _stripDiacritics = true;
  bool get stripDiacritics => _stripDiacritics;

  BluetoothDevice? _device;
  BluetoothCharacteristic? _tx;
  int _maxPayload = 20;
  StreamSubscription<List<ScanResult>>? _scanSub;
  StreamSubscription<BluetoothConnectionState>? _connSub;
  StreamSubscription<List<int>>? _rxSub;
  bool _initialized = false;

  // --- hàng đợi "chỉ giữ bản mới nhất" ---
  String? _latest;
  String? _lastSent;
  bool _pumping = false;
  Timer? _autoClearTimer;

  // ===== Khởi tạo / thiết lập =====

  /// Đọc cài đặt đã lưu và (nếu quyền Bluetooth đã có sẵn) tự nối lại kính dùng
  /// lần trước. Không bao giờ hiện hộp xin quyền lúc mở app.
  Future<void> init() async {
    if (_initialized) return;
    _initialized = true;
    try {
      final strip = await _store.readJson(_prefStrip);
      if (strip is bool) _stripDiacritics = strip;
      notifyListeners();
      final last = await _store.readJson(_prefLastDevice);
      if (last is Map && last['id'] is String) {
        if (!await _hasBluetoothPermission(request: false)) return;
        if (FlutterBluePlus.adapterStateNow != BluetoothAdapterState.on) return;
        final device = BluetoothDevice.fromId(last['id'] as String);
        await connect(device, name: last['name'] as String?, silent: true);
      }
    } catch (_) {}
  }

  Future<void> setStripDiacritics(bool value) async {
    _stripDiacritics = value;
    _lastSent = null; // vẽ lại với kiểu chữ mới
    notifyListeners();
    try {
      await _store.writeJson(_prefStrip, value);
    } catch (_) {}
  }

  Future<bool> _hasBluetoothPermission({required bool request}) async {
    if (!Platform.isAndroid) return true; // iOS tự hỏi khi dùng lần đầu
    final perms = [
      Permission.bluetoothScan,
      Permission.bluetoothConnect,
      Permission.locationWhenInUse, // cần cho Android ≤ 11
    ];
    if (!request) {
      final scan = await Permission.bluetoothScan.status;
      final conn = await Permission.bluetoothConnect.status;
      return scan.isGranted && conn.isGranted;
    }
    final res = await perms.request();
    final scan = res[Permission.bluetoothScan];
    final conn = res[Permission.bluetoothConnect];
    return !(scan?.isPermanentlyDenied == true ||
        conn?.isPermanentlyDenied == true);
  }

  // ===== Quét & kết nối =====

  Future<void> startScan() async {
    if (isBusy || isConnected) return;
    _error = null;
    _results = const [];
    if (!await _hasBluetoothPermission(request: true)) {
      _error = 'Chưa được cấp quyền Bluetooth. Hãy cấp quyền trong Cài đặt.';
      notifyListeners();
      return;
    }
    if (!await _ensureAdapterOn()) {
      _error = 'Hãy bật Bluetooth rồi thử lại.';
      notifyListeners();
      return;
    }
    _setState(FrameLinkState.scanning);
    try {
      await _scanSub?.cancel();
      _scanSub = FlutterBluePlus.scanResults.listen((list) {
        _results = list.where(_looksLikeFrame).toList()
          ..sort((a, b) => b.rssi.compareTo(a.rssi));
        notifyListeners();
      });
      await FlutterBluePlus.startScan(
        withServices: [_serviceUuid],
        timeout: const Duration(seconds: 12),
      );
      // startScan trả về khi hết giờ (hoặc bị stopScan).
    } catch (e) {
      _error = 'Không quét được: $e';
    } finally {
      await _scanSub?.cancel();
      _scanSub = null;
      if (_state == FrameLinkState.scanning) {
        _state = FrameLinkState.idle;
        if (_results.isEmpty && _error == null) {
          _error = 'Không thấy kính. Hãy mở nắp hộp/đeo kính cho kính sáng lên, '
              'ngắt kết nối khỏi app khác rồi quét lại.';
        }
      }
      notifyListeners();
    }
  }

  Future<void> stopScan() async {
    try {
      await FlutterBluePlus.stopScan();
    } catch (_) {}
  }

  bool _looksLikeFrame(ScanResult r) {
    if (r.advertisementData.serviceUuids.contains(_serviceUuid)) return true;
    return r.device.platformName.toLowerCase().contains('frame');
  }

  Future<bool> _ensureAdapterOn() async {
    if (FlutterBluePlus.adapterStateNow == BluetoothAdapterState.on) return true;
    try {
      if (Platform.isAndroid) await FlutterBluePlus.turnOn();
      await FlutterBluePlus.adapterState
          .firstWhere((s) => s == BluetoothAdapterState.on)
          .timeout(const Duration(seconds: 6));
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<void> connect(
    BluetoothDevice device, {
    String? name,
    bool silent = false,
  }) async {
    if (_state == FrameLinkState.connecting || isConnected) return;
    await stopScan();
    _error = null;
    _setState(FrameLinkState.connecting);
    try {
      await device.connect(timeout: const Duration(seconds: 15));
      // flutter_blue_plus tự xin MTU lớn trên Android; nếu vẫn thấp thì xin lại.
      try {
        if (Platform.isAndroid && device.mtuNow < 100) await device.requestMtu(247);
      } catch (_) {}
      final services = await device.discoverServices();
      BluetoothCharacteristic? tx, rx;
      for (final s in services) {
        if (s.uuid != _serviceUuid) continue;
        for (final c in s.characteristics) {
          if (c.uuid == _txUuid) tx = c;
          if (c.uuid == _rxUuid) rx = c;
        }
      }
      if (tx == null || rx == null) {
        throw Exception('Thiết bị này không phải kính Frame (thiếu dịch vụ BLE).');
      }

      await rx.setNotifyValue(true);
      await _rxSub?.cancel();
      _rxSub = rx.onValueReceived.listen((data) {
        if (kDebugMode) debugPrint('[Frame] ${utf8.decode(data, allowMalformed: true)}');
      });

      _device = device;
      _tx = tx;
      _maxPayload = (device.mtuNow - 3).clamp(20, 512);
      _deviceName = name ??
          (device.platformName.isNotEmpty ? device.platformName : 'Frame');

      await _connSub?.cancel();
      _connSub = device.connectionState.listen((s) {
        if (s == BluetoothConnectionState.disconnected) _handleDisconnected();
      });

      // Dừng mọi chương trình Lua đang chạy trên kính rồi chào.
      await _write(Uint8List.fromList([0x03]));
      await Future<void>.delayed(const Duration(milliseconds: 150));
      _lastSent = null;
      _setState(FrameLinkState.connected);
      unawaited(_store.writeJson(
        _prefLastDevice,
        {'id': device.remoteId.str, 'name': _deviceName},
      ));
      await _draw('Lingua da ket noi');
      _scheduleAutoClear(const Duration(seconds: 3));
    } catch (e) {
      try {
        await device.disconnect();
      } catch (_) {}
      _clearLink();
      if (!silent) _error = 'Không kết nối được kính: $e';
      _setState(FrameLinkState.idle);
    }
  }

  Future<void> disconnect() async {
    _autoClearTimer?.cancel();
    try {
      if (isConnected) await _draw(' ');
    } catch (_) {}
    try {
      await _device?.disconnect();
    } catch (_) {}
    _clearLink();
    try {
      await _store.writeJson(_prefLastDevice, null); // không tự nối lại nữa
    } catch (_) {}
    _setState(FrameLinkState.idle);
  }

  void _handleDisconnected() {
    if (_state == FrameLinkState.idle) return;
    _clearLink();
    _error = 'Kính đã ngắt kết nối.';
    _setState(FrameLinkState.idle);
  }

  void _clearLink() {
    _connSub?.cancel();
    _rxSub?.cancel();
    _connSub = null;
    _rxSub = null;
    _device = null;
    _tx = null;
    _deviceName = null;
    _latest = null;
    _lastSent = null;
    _autoClearTimer?.cancel();
  }

  void _setState(FrameLinkState s) {
    _state = s;
    notifyListeners();
  }

  // ===== Hiển thị chữ =====

  /// Hiện [text] lên kính. Gọi liên tục được (mỗi partial) — chỉ bản mới nhất
  /// được gửi. [autoClear]: sau chừng đó không có chữ mới thì xoá màn hình kính
  /// (hợp với hội thoại trực tiếp); null = giữ nguyên.
  void showText(String text, {Duration? autoClear}) {
    if (!isConnected) return;
    final t = text.trim();
    if (t.isEmpty) {
      clear();
      return;
    }
    _latest = t;
    _scheduleAutoClear(autoClear);
    if (!_pumping) unawaited(_pump());
  }

  /// Xoá màn hình kính.
  void clear() {
    if (!isConnected) return;
    _autoClearTimer?.cancel();
    _latest = ' ';
    if (!_pumping) unawaited(_pump());
  }

  /// Gửi thử một câu để kiểm tra kết nối.
  void sendTest() => showText('Xin chao! Hello! 你好', autoClear: const Duration(seconds: 6));

  void _scheduleAutoClear(Duration? d) {
    _autoClearTimer?.cancel();
    if (d == null) return;
    _autoClearTimer = Timer(d, clear);
  }

  Future<void> _pump() async {
    _pumping = true;
    try {
      while (_latest != null && isConnected) {
        final t = _latest!;
        _latest = null;
        if (t == _lastSent) continue;
        await _draw(t);
        _lastSent = t;
        await Future<void>.delayed(_minInterval);
      }
    } catch (e) {
      if (kDebugMode) debugPrint('[Frame] gửi lỗi: $e');
    } finally {
      _pumping = false;
    }
  }

  Future<void> _draw(String text) async {
    final prepared = _stripDiacritics ? removeDiacritics(text) : text;
    final lines = wrapForFrame(prepared, _lineUnits, _maxLines);
    // Mỗi lệnh Lua phải nằm trọn trong 1 lần ghi BLE (kính chạy ngay khi nhận).
    final budget = _maxPayload - 40; // chừa chỗ cho `frame.display.text("",1,999)`
    final statements = <String>[];
    for (var i = 0; i < lines.length; i++) {
      final line = _fitBytes(lines[i], budget);
      if (line.isEmpty) continue;
      statements.add(
        'frame.display.text("${_luaEscape(line)}",1,${i * _lineHeight + 1})',
      );
    }
    if (statements.isEmpty) statements.add('frame.display.text(" ",1,1)');
    statements.add('frame.display.show()');

    // Gộp càng nhiều lệnh càng tốt vào mỗi lần ghi (ít vòng BLE -> mượt hơn).
    var chunk = StringBuffer();
    for (final s in statements) {
      final candidate = chunk.isEmpty ? s : ';$s';
      if (chunk.isNotEmpty &&
          utf8.encode(chunk.toString()).length + utf8.encode(candidate).length >
              _maxPayload) {
        await _write(utf8.encode(chunk.toString()));
        chunk = StringBuffer();
        chunk.write(s);
      } else {
        chunk.write(candidate);
      }
    }
    if (chunk.isNotEmpty) await _write(utf8.encode(chunk.toString()));
  }

  Future<void> _write(List<int> data) async {
    final tx = _tx;
    if (tx == null) return;
    await tx.write(data, withoutResponse: true);
  }

  String _fitBytes(String s, int maxBytes) {
    if (maxBytes < 4) return '';
    if (utf8.encode(s).length <= maxBytes) return s;
    final out = StringBuffer();
    var used = 0;
    for (final r in s.runes) {
      final ch = String.fromCharCode(r);
      final n = utf8.encode(ch).length;
      if (used + n > maxBytes) break;
      out.write(ch);
      used += n;
    }
    return out.toString();
  }

  String _luaEscape(String s) {
    final b = StringBuffer();
    for (final r in s.runes) {
      if (r == 0x5C) {
        b.write(r'\\');
      } else if (r == 0x22) {
        b.write(r'\"');
      } else if (r < 0x20 || r == 0x7F) {
        b.write(' ');
      } else {
        b.writeCharCode(r);
      }
    }
    return b.toString();
  }

  // ===== Tiện ích chữ (công khai để dễ test) =====

  /// Xuống dòng theo độ rộng ([maxUnits] đơn vị/dòng; chữ CJK/emoji rộng = 2) và
  /// chỉ giữ [maxLines] dòng CUỐI — chữ mới nhất luôn nằm trong tầm nhìn, dòng cũ
  /// cuộn lên như phụ đề.
  @visibleForTesting
  static List<String> wrapForFrame(String text, int maxUnits, int maxLines) {
    int w(int rune) => rune >= 0x2E80 ? 2 : 1;
    int width(String s) => s.runes.fold(0, (a, r) => a + w(r));

    final lines = <String>[];
    for (final paragraph in text.split('\n')) {
      var cur = '';
      var curW = 0;
      void flush() {
        if (cur.isNotEmpty) lines.add(cur);
        cur = '';
        curW = 0;
      }

      for (final word in paragraph.split(RegExp(r'\s+'))) {
        if (word.isEmpty) continue;
        final ww = width(word);
        if (ww > maxUnits) {
          // Từ dài / chữ không có dấu cách (CJK): cắt theo ký tự.
          for (final r in word.runes) {
            final cw = w(r);
            if (curW + cw > maxUnits) flush();
            cur += String.fromCharCode(r);
            curW += cw;
          }
          continue;
        }
        final need = curW == 0 ? ww : curW + 1 + ww;
        if (need > maxUnits) {
          flush();
          cur = word;
          curW = ww;
        } else {
          cur = curW == 0 ? word : '$cur $word';
          curW = need;
        }
      }
      flush();
    }
    if (lines.length > maxLines) return lines.sublist(lines.length - maxLines);
    return lines;
  }

  static const _from =
      'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
      'ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ'
      'äöüÄÖÜçÇñÑëËïÏ';
  static const _to =
      'aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd'
      'AAAAAAAAAAAAAAAAAEEEEEEEEEEEIIIIIOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYD'
      'aouAOUcCnNeEiI';

  /// Bỏ dấu Latin / tiếng Việt: "Xin chào, Việt Nam" -> "Xin chao, Viet Nam".
  @visibleForTesting
  static String removeDiacritics(String s) {
    final b = StringBuffer();
    for (final r in s.runes) {
      if (r == 0x00DF) {
        b.write('ss');
      } else {
        b.write(_diacriticMap[r] ?? String.fromCharCode(r));
      }
    }
    return b.toString();
  }

  static final Map<int, String> _diacriticMap = () {
    final f = _from.runes.toList();
    final t = _to.runes.toList();
    assert(f.length == t.length);
    return {for (var i = 0; i < f.length; i++) f[i]: String.fromCharCode(t[i])};
  }();
}
