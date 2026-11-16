import 'package:flutter/material.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';

import '../core/theme.dart';
import '../services/frame_service.dart';

/// Bottom sheet quản lý kết nối kính phiên dịch (Brilliant Labs Frame).
Future<void> showFrameConnectSheet(BuildContext context) {
  return showModalBottomSheet<void>(
    context: context,
    showDragHandle: true,
    isScrollControlled: true,
    builder: (_) => const FrameConnectSheet(),
  );
}

class FrameConnectSheet extends StatefulWidget {
  const FrameConnectSheet({super.key});

  @override
  State<FrameConnectSheet> createState() => _FrameConnectSheetState();
}

class _FrameConnectSheetState extends State<FrameConnectSheet> {
  final _frame = FrameService.instance;

  @override
  void dispose() {
    _frame.stopScan();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListenableBuilder(
        listenable: _frame,
        builder: (context, _) => Padding(
          padding: const EdgeInsets.fromLTRB(
            AppTheme.spaceMd,
            0,
            AppTheme.spaceMd,
            AppTheme.spaceMd,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Kính phiên dịch',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 4),
              Text(
                'Kết nối kính Brilliant Labs Frame để bản dịch hiện ngay trước mắt, '
                'theo từng chữ khi bạn đang nói.',
                style: TextStyle(
                  fontSize: 13,
                  color: AppTheme.moss.withValues(alpha: .7),
                ),
              ),
              const SizedBox(height: 14),
              _buildStatus(),
              if (_frame.error != null && !_frame.isConnected) ...[
                const SizedBox(height: 10),
                Text(
                  _frame.error!,
                  style: const TextStyle(
                    fontSize: 12.5,
                    color: AppTheme.cranberry,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
              const SizedBox(height: 12),
              if (_frame.isConnected) _buildConnected() else _buildScan(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatus() {
    final (label, color) = switch (_frame.state) {
      FrameLinkState.connected => (
          'Đã kết nối · ${_frame.deviceName ?? 'Frame'}',
          AppTheme.moss,
        ),
      FrameLinkState.connecting => ('Đang kết nối…', AppTheme.coral),
      FrameLinkState.scanning => ('Đang tìm kính…', AppTheme.coral),
      FrameLinkState.idle => ('Chưa kết nối', AppTheme.cranberry),
    };
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: AppTheme.sand,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        children: [
          Container(
            width: 10,
            height: 10,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              label,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
            ),
          ),
          if (_frame.isBusy)
            const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
        ],
      ),
    );
  }

  Widget _buildScan() {
    final scanning = _frame.state == FrameLinkState.scanning;
    final connecting = _frame.state == FrameLinkState.connecting;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (_frame.results.isNotEmpty)
          ConstrainedBox(
            constraints: const BoxConstraints(maxHeight: 220),
            child: ListView(
              shrinkWrap: true,
              children: _frame.results.map(_buildResultTile).toList(),
            ),
          ),
        const SizedBox(height: 8),
        SizedBox(
          width: double.infinity,
          child: FilledButton.icon(
            onPressed: connecting
                ? null
                : (scanning ? _frame.stopScan : _frame.startScan),
            icon: Icon(scanning ? Icons.stop_rounded : Icons.bluetooth_searching_rounded),
            label: Text(scanning ? 'Dừng quét' : 'Tìm kính'),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Mẹo: tháo kính khỏi sạc, đeo hoặc mở nắp để kính sáng, và đóng các app '
          'khác đang giữ kết nối với kính.',
          style: TextStyle(
            fontSize: 12,
            color: AppTheme.moss.withValues(alpha: .6),
          ),
        ),
      ],
    );
  }

  Widget _buildResultTile(ScanResult r) {
    final name = r.device.platformName.isNotEmpty
        ? r.device.platformName
        : (r.advertisementData.advName.isNotEmpty
            ? r.advertisementData.advName
            : 'Frame');
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: const Icon(Icons.vrpano_rounded, color: AppTheme.moss),
      title: Text(name, style: const TextStyle(fontWeight: FontWeight.w800)),
      subtitle: Text('Tín hiệu ${r.rssi} dBm'),
      trailing: const Icon(Icons.chevron_right_rounded),
      onTap: _frame.state == FrameLinkState.connecting
          ? null
          : () => _frame.connect(r.device, name: name),
    );
  }

  Widget _buildConnected() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SwitchListTile(
          contentPadding: EdgeInsets.zero,
          value: _frame.stripDiacritics,
          onChanged: _frame.setStripDiacritics,
          title: const Text(
            'Bỏ dấu khi hiện trên kính',
            style: TextStyle(fontWeight: FontWeight.w800),
          ),
          subtitle: const Text(
            'Font mặc định của kính chưa vẽ được dấu tiếng Việt. Tắt nếu firmware '
            'kính của bạn đã hỗ trợ.',
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: _frame.sendTest,
                icon: const Icon(Icons.send_rounded),
                label: const Text('Gửi thử'),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: FilledButton.icon(
                style: FilledButton.styleFrom(backgroundColor: AppTheme.cranberry),
                onPressed: _frame.disconnect,
                icon: const Icon(Icons.link_off_rounded),
                label: const Text('Ngắt kết nối'),
              ),
            ),
          ],
        ),
      ],
    );
  }
}
