import 'package:flutter_test/flutter_test.dart';
import 'package:language_app/services/frame_service.dart';

void main() {
  group('FrameService.removeDiacritics', () {
    test('bỏ dấu tiếng Việt', () {
      expect(FrameService.removeDiacritics('Xin chào, Việt Nam đẹp quá!'),
          'Xin chao, Viet Nam dep qua!');
      expect(FrameService.removeDiacritics('ĐƯỜNG Ở NHÀ'), 'DUONG O NHA');
    });
    test('giữ nguyên chữ không dấu / CJK', () {
      expect(FrameService.removeDiacritics('Hello 你好'), 'Hello 你好');
    });
  });

  group('FrameService.wrapForFrame', () {
    test('xuống dòng theo từ', () {
      final lines = FrameService.wrapForFrame('one two three four five', 9, 4);
      expect(lines, ['one two', 'three', 'four five']);
    });
    test('chỉ giữ các dòng cuối', () {
      final lines = FrameService.wrapForFrame('aaa bbb ccc ddd eee', 3, 2);
      expect(lines, ['ddd', 'eee']);
    });
    test('cắt từ quá dài và chữ CJK (rộng 2)', () {
      expect(FrameService.wrapForFrame('abcdefgh', 3, 4), ['abc', 'def', 'gh']);
      expect(FrameService.wrapForFrame('你好世界', 4, 4), ['你好', '世界']);
    });
  });
}
