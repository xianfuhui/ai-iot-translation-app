#!/usr/bin/env python3
"""Mô phỏng góc nhìn người đeo kính Brilliant Labs Frame (1 tròng có màn hiển thị).

Bố cục chữ port từ mobile/lib/services/frame_service.dart (wrapForFrame, removeDiacritics):
màn 640x400, tối đa 4 dòng, 24 đơn vị/dòng (CJK tính 2), cách dòng 60px, bỏ dấu tiếng Việt.
Dùng: python3 build_glasses_view.py [out.png]
"""
import sys, pathlib, re, unicodedata
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "glasses-lens.png")
MAX_LINES, LINE_UNITS, LINE_H = 4, 24, 60

def remove_diacritics(s):
    s = s.replace("đ", "d").replace("Đ", "D").replace("ß", "ss")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def wrap(text, max_units=LINE_UNITS, max_lines=MAX_LINES):
    w = lambda r: 2 if ord(r) >= 0x2E80 else 1
    width = lambda s: sum(w(c) for c in s)
    lines = []
    for para in text.split("\n"):
        cur, cw = "", 0
        def flush():
            nonlocal cur, cw
            if cur: lines.append(cur)
            cur, cw = "", 0
        for word in re.split(r"\s+", para):
            if not word: continue
            ww = width(word)
            if ww > max_units:
                for ch in word:
                    if cw + w(ch) > max_units: flush()
                    cur += ch; cw += w(ch)
                continue
            need = ww if cw == 0 else cw + 1 + ww
            if need > max_units: flush(); cur, cw = word, ww
            else: cur = word if cw == 0 else cur + " " + word; cw = need
        flush()
    return lines[-max_lines:] if len(lines) > max_lines else lines

TEXT = "Sân bay gần nhất ở đâu? Đi taxi hết bao nhiêu tiền? Tôi cần đến khách sạn trước sáu giờ."
lines = wrap(remove_diacritics(TEXT))

# --- hình học: kính 1 tròng (mắt phải) ---
W, H = 1600, 900
LX, LY, LW, LH = 520, 150, 880, 600           # tròng kính
DW, DH = 640, 400                              # màn Frame
DX, DY = LX + (LW - DW) // 2 + 20, LY + (LH - DH) // 2
text_svg = "".join(
    f'<text x="{DX+24}" y="{DY+58+i*LINE_H}" class="t">{l}</text>' for i, l in enumerate(lines))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
 <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2d4a46"/><stop offset="1" stop-color="#0e1f1d"/></linearGradient>
 <radialGradient id="glass" cx=".35" cy=".3" r=".9"><stop offset="0" stop-color="#16312e" stop-opacity=".55"/><stop offset="1" stop-color="#050b0a" stop-opacity=".92"/></radialGradient>
 <linearGradient id="shine" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".18"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/></linearGradient>
 <linearGradient id="frame" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2f2e"/><stop offset="1" stop-color="#0c0f0e"/></linearGradient>
 <filter id="blur"><feGaussianBlur stdDeviation="14"/></filter>
 <filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <clipPath id="lens"><rect x="{LX}" y="{LY}" width="{LW}" height="{LH}" rx="280"/></clipPath>
 <style>.t{{font:600 36px 'DejaVu Sans',sans-serif;fill:#d8ffe3;letter-spacing:.5px}}
 .s{{font:600 22px Inter,sans-serif;fill:#9fb8b2}}</style>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<!-- cảnh nền mờ: người đối diện -->
<g filter="url(#blur)" opacity=".75">
 <ellipse cx="560" cy="560" rx="210" ry="260" fill="#6e8a83"/>
 <circle cx="560" cy="330" r="105" fill="#c9a98e"/>
 <rect x="1180" y="120" width="260" height="420" rx="30" fill="#40655e"/>
 <rect x="80" y="640" width="1440" height="260" fill="#14282a"/>
</g>
<!-- gọng: cầu mũi, gọng ngang, càng kính -->
<rect x="{LX-120}" y="{LY+LH//2-26}" width="150" height="52" rx="26" fill="url(#frame)"/>
<path d="M{LX-120} {LY+LH//2} q-60 40 -70 130" stroke="#1b2120" stroke-width="16" fill="none" stroke-linecap="round"/>
<rect x="{LX+LW-30}" y="{LY+LH//2-30}" width="330" height="60" rx="30" fill="url(#frame)"/>
<!-- tròng: viền + kính -->
<rect x="{LX-26}" y="{LY-26}" width="{LW+52}" height="{LH+52}" rx="306" fill="url(#frame)"/>
<rect x="{LX}" y="{LY}" width="{LW}" height="{LH}" rx="280" fill="url(#glass)"/>
<g clip-path="url(#lens)">
 <rect x="{LX}" y="{LY}" width="{LW}" height="{LH}" fill="url(#shine)"/>
 <path d="M{LX+60} {LY+LH} L{LX+330} {LY} L{LX+400} {LY} L{LX+130} {LY+LH} Z" fill="#fff" opacity=".05"/>
</g>
<!-- vùng hiển thị 640x400 -->
<rect x="{DX}" y="{DY}" width="{DW}" height="{DH}" rx="10" fill="none" stroke="#7fe3a5" stroke-opacity=".28" stroke-dasharray="6 8"/>
<g filter="url(#glow)">{text_svg}</g>
<text x="{DX}" y="{DY+DH+44}" class="s">Màn hiển thị 640×400 · tối đa 4 dòng · đã bỏ dấu tiếng Việt</text>
<text x="40" y="{H-36}" class="s" opacity=".8">Mô phỏng: góc nhìn người đeo Brilliant Labs Frame (1 tròng)</text>
</svg>'''

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
    pg.set_content(f'<html><body style="margin:0">{svg}</body></html>')
    pg.screenshot(path=str(OUT))
    b.close()
print("wrote", OUT, lines)
