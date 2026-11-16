#!/usr/bin/env python3
"""Dựng bộ mockup màn hình app Lingua (Flutter) -> PNG.

Nguồn sự thật: mobile/lib (theme.dart, screens/*, widgets/*). Mọi chuỗi UI, màu,
kích thước lấy từ code; icon dùng bộ Material Design Icons.
"""
import re, sys, pathlib
from playwright.sync_api import sync_playwright

ICONS = pathlib.Path("/usr/local/lib/python3.12/dist-packages/material/templates/.icons/material")
OUT = pathlib.Path("/home/claude/mockups/out")
(OUT / "framed").mkdir(parents=True, exist_ok=True)
(OUT / "flat").mkdir(parents=True, exist_ok=True)

_icache = {}
def ic(name, size=24, color="currentColor", extra=""):
    if name not in _icache:
        svg = (ICONS / f"{name}.svg").read_text()
        _icache[name] = re.search(r'<path d="([^"]+)"', svg).group(1)
    return (f'<svg class="ic" viewBox="0 0 24 24" width="{size}" height="{size}" '
            f'fill="{color}" style="{extra}"><path d="{_icache[name]}"/></svg>')

CSS = """
:root{--paper:#F8F5EF;--sand:#EEE8DD;--ivory:#FFFDF9;--moss:#1B4B43;--coral:#F26B5E;--tint:#FBE0D8;
--sage:#A9B9AC;--line:#D9D0C4;--cran:#A74443;--green:#2E9E5B}
*{box-sizing:border-box;margin:0;padding:0}
body{background:transparent;font-family:Inter,'Noto Sans CJK JP',sans-serif;color:var(--moss);
-webkit-font-smoothing:antialiased}
.serif{font-family:'Noto Serif CJK JP','DejaVu Serif',serif}
.ic{display:block;flex:none}
.phone{display:inline-block;background:#111514;padding:10px;border-radius:50px;position:relative}
.screen{width:390px;height:844px;background:var(--paper);border-radius:40px;position:relative;
overflow:hidden;display:flex;flex-direction:column}
.flat .phone{padding:0;background:none;border-radius:0}.flat .screen{border-radius:0}
.status{height:34px;flex:none;display:flex;align-items:center;justify-content:space-between;
padding:6px 24px 0 28px;font-size:13px;font-weight:600;position:relative;z-index:5}
.status .r{display:flex;gap:4px;align-items:center}
.hole{position:absolute;top:12px;left:50%;width:14px;height:14px;margin-left:-7px;border-radius:50%;
background:#111514;z-index:20}
.gest{position:absolute;bottom:7px;left:50%;width:124px;height:4px;margin-left:-62px;border-radius:3px;
background:#1b1f1e;opacity:.75;z-index:30}
.body{flex:1;min-height:0;position:relative;overflow:hidden;display:flex;flex-direction:column}
.scroll{flex:1;min-height:0;overflow:hidden;padding:4px 16px 16px}
/* nav */
.nav{flex:none;background:var(--ivory);height:96px;padding-bottom:20px;display:flex;
box-shadow:0 -2px 10px rgba(27,75,67,.10);position:relative;z-index:6}
.nav .d{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;
font-size:11px;font-weight:800;color:rgba(27,75,67,.55)}
.nav .d .p{width:64px;height:32px;border-radius:16px;display:flex;align-items:center;justify-content:center}
.nav .d.on{color:var(--moss)}.nav .d.on .p{background:var(--tint)}
/* appbar */
.appbar{height:56px;flex:none;display:flex;align-items:center;padding:0 4px 0 16px;gap:0}
.appbar.back{padding-left:4px}.appbar.back .t{margin-left:12px}
.appbar .t{font-size:22px;font-weight:700;flex:1}
.ib{width:48px;height:48px;display:flex;align-items:center;justify-content:center;position:relative}
.txtbtn{font-weight:800;font-size:14px;padding:0 12px;height:40px;display:flex;align-items:center;gap:6px}
/* generic */
.card{background:var(--ivory);border-radius:22px;border:1px solid var(--line);box-shadow:0 1px 3px rgba(27,75,67,.13)}
.btn{height:52px;border-radius:15px;background:var(--coral);color:var(--ivory);font-weight:800;font-size:15px;
display:flex;align-items:center;justify-content:center;gap:8px}
.btn.sm{height:36px;padding:0 14px;font-size:13px;display:inline-flex;border-radius:15px}
.btn.m44{height:44px;padding:0 20px;display:inline-flex}
.btn.out{background:transparent;color:var(--moss);border:1px solid var(--line);height:48px}
.btn.cran{background:var(--cran)}
.brand{display:flex;align-items:center;gap:12px}
.tile{width:48px;height:48px;border-radius:16px;background:var(--moss);color:var(--ivory);display:flex;
align-items:center;justify-content:center}
.tile.c{width:40px;height:40px;border-radius:13px}
.brand .n{font-size:25px;font-weight:800;letter-spacing:-.5px}
.dark .tile{background:var(--coral);color:var(--moss)}.dark .brand .n{color:var(--ivory)}
.avatar{width:40px;height:40px;border-radius:13px;background:var(--tint);border:1px solid var(--coral);color:var(--coral);
display:flex;align-items:center;justify-content:center;font-weight:900;font-size:16px}
.dot{width:9px;height:9px;border-radius:50%;position:absolute;right:11px;top:11px;border:1.5px solid var(--paper)}
.pill{display:inline-block;border-radius:999px;padding:2px 9px;font-size:10.5px;font-weight:800;
background:#DCEFE2;color:#1C7A45}
.pill.sand{background:var(--sand);color:rgba(27,75,67,.6)}.pill.tint{background:var(--tint);color:var(--cran)}
.strip{display:flex;align-items:center;gap:8px;background:var(--sand);border:1px solid var(--line);border-radius:12px;
padding:8px 12px;margin-bottom:10px;font-size:12px;font-weight:700;color:rgba(27,75,67,.75)}
.strip b{color:var(--coral);font-weight:900;padding:2px 6px}
/* translate */
.langbar{background:var(--sand);border-radius:18px;padding:8px;display:flex;align-items:center;gap:12px}
.langbar .l{flex:1;background:var(--ivory);border:1px solid var(--line);border-radius:13px;height:44px;
display:flex;align-items:center;justify-content:center;font-weight:800;font-size:15px;padding-left:6px}
.langbar .sw{width:38px;height:38px;border-radius:50%;background:var(--ivory);display:flex;align-items:center;
justify-content:center;margin:0 -6px}
.input{background:var(--ivory);border:1px solid var(--line);border-radius:20px;padding:12px 16px 10px;margin-top:12px}
.input .tx{font-size:19px;line-height:1.45;min-height:55px}
.input hr{border:0;border-top:1px solid var(--line);margin:18px 0 10px}
.input .row{display:flex;align-items:center;justify-content:space-between;min-height:30px}
.vp{display:flex;align-items:center;gap:6px;background:var(--tint);color:var(--cran);font-weight:800;font-size:13px;
border-radius:999px;padding:8px 14px}
.vp.rec{background:var(--cran);color:var(--ivory)}
.clr{width:30px;height:30px;border-radius:50%;background:var(--sand);display:flex;align-items:center;justify-content:center}
.result{background:var(--moss);border-radius:20px;padding:16px;margin-top:12px;color:var(--ivory)}
.result .h{display:flex;align-items:center;gap:8px;font-size:11.5px;font-weight:800;letter-spacing:1.1px;color:rgba(255,253,249,.55)}
.result .h i{margin-left:auto}.result .h .ci{width:32px;height:32px;border-radius:50%;background:rgba(255,253,249,.12);
display:flex;align-items:center;justify-content:center;color:var(--ivory)}
.result .h .ci+.ci{margin-left:0}
.result .tx{font-size:21px;font-weight:700;line-height:1.4;margin-top:8px}
/* history / vocab */
.hcard{background:var(--ivory);border-radius:16px;padding:12px 6px 8px 15px;margin-bottom:10px}
.hcard .top{display:flex;align-items:center;gap:8px}.hcard .top span.tm{font-size:11.5px;color:rgba(27,75,67,.45)}
.srow{display:flex;align-items:flex-start}
.srow .s{flex:1;font-weight:700;font-size:14px;line-height:1.43;padding-top:8px}
.srow.t .s{padding-top:0}
.srow .cp{width:40px;height:34px;display:flex;align-items:center;justify-content:center;color:rgba(27,75,67,.6)}
.w{text-decoration:underline dotted rgba(27,75,67,.35);text-underline-offset:3px}
.w.sel{background:var(--tint);color:var(--coral);font-weight:900;text-decoration:none}
.tb{display:flex;align-items:center;gap:6px;font-weight:800;font-size:14px;height:40px;padding:0 12px 0 8px}
.selbar{flex:none;background:var(--ivory);box-shadow:0 -3px 10px rgba(27,75,67,.14);padding:8px 12px 8px 16px;
display:flex;align-items:center;position:relative;z-index:4}
.selbar .c{flex:1;font-weight:800;font-size:14px}
.tabs{display:flex;padding:0 16px}.tabs div{flex:1;text-align:center;font-size:13.5px;font-weight:800;padding:14px 0 12px;
color:rgba(27,75,67,.45);border-bottom:3px solid transparent}
.tabs div.on{color:var(--coral);border-bottom-color:var(--coral)}
.wcard{background:var(--ivory);border:1px solid var(--line);border-radius:16px;padding:12px 8px 12px 15px;margin-bottom:10px;
display:flex;align-items:center}
.wcard .m{flex:1;min-width:0}.wcard .wd{display:flex;align-items:center;gap:8px;font-size:16px;font-weight:800}
.wcard .ph{font-size:12px;font-weight:400;color:rgba(27,75,67,.5)}
.wcard .mean{font-size:13.5px;margin-top:3px}.wcard .dir{font-size:11px;color:rgba(27,75,67,.45);margin-top:2px}
.wcard .a{width:40px;height:40px;display:flex;align-items:center;justify-content:center;color:rgba(27,75,67,.6)}
.chips{display:flex;gap:8px;padding:0 16px;margin:0 0 6px}
.chip{border-radius:999px;padding:6px 14px;font-size:13px;font-weight:700;background:var(--ivory);
border:1px solid var(--line);color:rgba(27,75,67,.75)}
.chip.on{background:var(--moss);border-color:var(--moss);color:var(--ivory)}
.search{margin:12px 16px 8px;height:44px;border:1px solid var(--line);background:var(--ivory);border-radius:14px;
display:flex;align-items:center;gap:10px;padding:0 12px;font-size:14px;color:rgba(27,75,67,.4)}
/* ai */
.ubub{display:flex;justify-content:flex-end;padding:8px 0}
.ubub div{max-width:288px;border-left:3px solid var(--coral);padding-left:10px;color:var(--coral);font-weight:700;font-size:15px;line-height:1.4}
.abub{display:flex;padding:8px 0}
.abub div{max-width:288px;background:var(--ivory);border-radius:16px;padding:13px 15px;font-size:14.5px;line-height:1.55;
box-shadow:0 1px 4px rgba(27,75,67,.06)}
.composer{flex:none;background:var(--ivory);border-top:1px solid var(--line);padding:10px 16px 16px;display:flex;gap:8px;align-items:flex-end}
.composer .in{flex:1;height:48px;border:1px solid var(--line);background:var(--ivory);border-radius:16px;display:flex;align-items:center;
gap:10px;padding:0 14px;font-size:16px;color:rgba(27,75,67,.5)}
.composer .send{width:52px;height:52px;border-radius:50%;background:var(--coral);color:var(--ivory);display:flex;align-items:center;justify-content:center}
.ico72{width:72px;height:72px;border-radius:24px;background:var(--tint);display:flex;align-items:center;justify-content:center;color:var(--coral)}
.center{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:32px}
.h5{font-size:25px;font-weight:700;line-height:1.16}
.sub{font-size:14px;line-height:1.4;color:rgba(27,75,67,.64)}
.sugg{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-top:22px}
.sugg span{display:flex;align-items:center;gap:6px;background:var(--sand);border:1px solid var(--line);border-radius:12px;
padding:8px 12px;font-size:14px;font-weight:700}
/* auth */
.field{position:relative;height:58px;border:1px solid var(--line);background:var(--ivory);border-radius:16px;display:flex;
align-items:center;gap:12px;padding:0 12px 0 14px;margin-bottom:14px}
.field.f{border:1.5px solid var(--moss)}
.field .fl{position:absolute;left:46px;top:-8px;font-size:12px;font-weight:700;padding:0 4px;
background:linear-gradient(var(--paper) 50%,var(--ivory) 50%)}
.field .v{flex:1;font-size:16px}
.field .hp{position:absolute;left:16px;bottom:-19px;font-size:12px;color:rgba(27,75,67,.6)}
/* sheets / dialogs */
.scrim{position:absolute;inset:0;background:rgba(0,0,0,.32);z-index:10}
.sheet{position:absolute;left:0;right:0;bottom:0;background:var(--paper);border-radius:28px 28px 0 0;z-index:11;padding-bottom:28px}
.sheet .hd{width:32px;height:4px;border-radius:2px;background:rgba(27,75,67,.4);margin:16px auto 12px}
.lti{height:56px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;font-weight:700;font-size:16px}
.dialog{position:absolute;left:40px;right:40px;top:50%;transform:translateY(-50%);background:var(--paper);border-radius:28px;
padding:24px;z-index:11}
.dialog h2{font-size:25px;font-weight:700;line-height:1.16}
.dlgact{display:flex;justify-content:flex-end;gap:8px;margin-top:20px;font-weight:800;font-size:14px}
.dlgact span{padding:10px 12px}
.ofield{position:relative;height:54px;border:1px solid var(--line);border-radius:16px;background:var(--ivory);display:flex;
align-items:center;padding:0 14px;font-size:16px;margin-top:14px}
.ofield .fl{position:absolute;left:12px;top:-8px;font-size:12px;font-weight:700;padding:0 4px;
background:linear-gradient(var(--paper) 50%,var(--ivory) 50%)}
/* list tile cards */
.ptile{display:flex;align-items:center;gap:16px;padding:7px 16px;min-height:72px}
.ptile .bx{width:40px;height:40px;border-radius:13px;background:var(--sand);display:flex;align-items:center;justify-content:center}
.ptile .tt{flex:1;font-weight:800;font-size:16px}.ptile .st{font-size:12px;color:rgba(27,75,67,.56);font-weight:400;margin-top:2px;line-height:1.35}
.ptile.d .tt{color:var(--cran)}.ptile.d .bx{background:rgba(167,68,67,.1);color:var(--cran)}
.sep{height:1px;background:var(--line);margin:0 16px 0 62px}
.h6{font-size:16px;font-weight:800;margin:24px 0 10px}
.spin{width:24px;height:24px;border-radius:50%;border:2px solid var(--coral);border-right-color:transparent;border-bottom-color:transparent;transform:rotate(30deg)}
.bar{height:4px;border-radius:2px;background:rgba(242,107,94,.25);margin-top:6px;overflow:hidden}.bar i{display:block;height:100%;background:var(--coral)}
.sw2{width:52px;height:32px;border-radius:16px;background:var(--moss);position:relative;flex:none}
.sw2:after{content:"";position:absolute;right:4px;top:4px;width:24px;height:24px;border-radius:50%;background:var(--ivory)}
"""

# ---------- helpers ----------
def words(text, sel=()):
    def r(m):
        cls = "w sel" if m.group(0).lower() in sel else "w"
        return f'<span class="{cls}">{m.group(0)}</span>'
    return re.sub(r"\w+(?:['\-]\w+)*", r, text)

def status(dark=False):
    c = "#fff" if dark else "#1a1c1b"
    return (f'<div class="status" style="color:{c}"><span>9:41</span><span class="r">'
            f'{ic("wifi",15)}{ic("signal-cellular-3",15)}{ic("battery-80",17)}</span></div>')

def screen(body, nav=None, dark=False, bg=None, extra="", overlay=""):
    navh = ""
    if nav is not None:
        items = [("translate","Dịch"),("history","Lịch sử"),("creation","AI"),("bookmark-outline","Sổ tay"),("account-outline","Cá nhân")]
        navh = '<div class="nav">' + "".join(
            f'<div class="d {"on" if i==nav else ""}"><div class="p">{ic(n,22)}</div>{l}</div>'
            for i,(n,l) in enumerate(items)) + "</div>"
    st = f' style="background:{bg}"' if bg else ""
    gest = f'<div class="gest" style="{"background:#fff;opacity:.8" if dark else ""}"></div>'
    return (f'<div class="phone"><div class="screen {"dark" if dark else ""}"{st}>{status(dark)}'
            f'<div class="body">{body}{extra}</div>{navh}{overlay}<div class="hole"></div>{gest}</div></div>')

def appbar(title, actions="", back=False):
    lead = f'<div class="ib">{ic("arrow-left",24)}</div>' if back else ""
    return f'<div class="appbar serif{" back" if back else ""}">{lead}<div class="t">{title}</div>{actions}</div>'

def brand(compact=False, dark=False):
    return (f'<div class="brand"><div class="tile{" c" if compact else ""}">{ic("translate",22 if compact else 27)}</div>'
            + ("" if compact else '<div class="n serif">lingua</div>') + "</div>")

def guest_strip():
    return f'<div class="strip">{ic("account-outline",16)}<span style="flex:1">Chế độ khách · dữ liệu chỉ lưu trên máy này</span><b>Đăng nhập</b></div>'

# ---------- translate family ----------
def translate_body(src, dst, tgt="Tiếng Nhật", tgt_label=None, live=False, glasses=False, srcl="Tiếng Anh", extra_top=""):
    hdr = f'<div style="display:flex;align-items:center;padding:8px 16px 10px">{brand(True)}'
    if live:
        hdr += (f'<span style="width:8px;height:8px;border-radius:50%;background:var(--cran);margin-left:12px"></span>'
                f'<span style="font-size:12px;font-weight:800;margin-left:5px">Đang nghe</span>')
    gl = (f'<div class="ib">{ic("glasses",24,"var(--moss)" if glasses else "rgba(27,75,67,.45)")}'
          + ('<span class="dot" style="background:var(--green)"></span>' if glasses else "") + "</div>")
    hdr += (f'<div style="flex:1"></div>{gl}<div class="ib" style="margin-right:4px">{ic("volume-high",24)}</div>'
            f'<div class="avatar">N</div></div>')
    vp = (f'<div class="vp rec">{ic("stop-circle-outline",16)}Dừng nghe</div>' if live
          else f'<div class="vp">{ic("microphone-outline",16)}Nói để dịch</div>')
    clear = "" if live else f'<div class="clr">{ic("close",16)}</div>'
    res = ""
    if dst:
        res = (f'<div class="result"><div class="h"><span>{(tgt_label or tgt).upper()}</span><i></i>'
               f'<div class="ci">{ic("volume-high",15)}</div><div class="ci">{ic("content-copy",15)}</div></div>'
               f'<div class="tx">{dst}</div></div>')
    return (hdr + f'<div class="scroll">{extra_top}<div class="langbar"><div class="l">{srcl}{ic("menu-down",20)}</div>'
            f'<div class="sw">{ic("swap-horizontal",20)}</div><div class="l">{tgt}{ic("menu-down",20)}</div></div>'
            f'<div class="input"><div class="tx">{src}</div><hr><div class="row">{vp}{clear}</div></div>{res}</div>')

def s_translate():
    return screen(translate_body("Good morning, how are you today?", "おはようございます、今日はどうですか？"), nav=0)

def s_voice():
    return screen(translate_body("Where is the nearest airport? How much does a taxi cost", "Sân bay gần nhất ở đâu? Đi taxi hết bao nhiêu tiền",
                                 tgt="Tiếng Việt", live=True, glasses=True), nav=0)

def s_picker():
    rows = "".join(f'<div class="lti"><span>{n}</span>{ic("check",24,"var(--coral)") if n=="Tiếng Nhật" else ""}</div>'
                   for n in ["Tiếng Anh","Tiếng Việt","Tiếng Nhật"])
    ov = f'<div class="scrim"></div><div class="sheet"><div class="hd"></div>{rows}</div>'
    return screen(translate_body("Good morning, how are you today?", "おはようございます、今日はどうですか？"), nav=0, overlay=ov)

def frame_sheet(connected):
    if connected:
        st = ('<div style="display:flex;align-items:center;gap:10px;background:var(--sand);border-radius:14px;padding:12px 14px">'
              '<span style="width:10px;height:10px;border-radius:50%;background:var(--moss)"></span>'
              '<span style="font-weight:800;font-size:14px">Đã kết nối · Frame 7B</span></div>')
        bodyh = (f'<div style="display:flex;align-items:center;gap:12px;margin-top:12px;padding:8px 0">'
                 f'<div style="flex:1"><div style="font-weight:800;font-size:16px">Bỏ dấu khi hiện trên kính</div>'
                 f'<div style="font-size:14px;color:rgba(27,75,67,.7);line-height:1.4;margin-top:3px">Font mặc định của kính chưa vẽ được dấu tiếng Việt. Tắt nếu firmware kính của bạn đã hỗ trợ.</div></div>'
                 f'<div class="sw2"></div></div>'
                 f'<div style="display:flex;gap:10px;margin-top:16px"><div class="btn out" style="flex:1">{ic("send",18)}Gửi thử</div>'
                 f'<div class="btn cran" style="flex:1">{ic("link-off",18)}Ngắt kết nối</div></div>')
    else:
        st = ('<div style="display:flex;align-items:center;gap:10px;background:var(--sand);border-radius:14px;padding:12px 14px">'
              '<span style="width:10px;height:10px;border-radius:50%;background:var(--coral)"></span>'
              '<span style="font-weight:800;font-size:14px;flex:1">Đang tìm kính…</span><div class="spin" style="width:16px;height:16px"></div></div>')
        bodyh = (f'<div style="margin-top:12px">'
                 f'<div style="display:flex;align-items:center;gap:16px;height:64px">{ic("glasses",24,"var(--moss)")}'
                 f'<div style="flex:1"><div style="font-weight:800;font-size:16px">Frame 7B</div><div style="font-size:14px;color:rgba(27,75,67,.7)">Tín hiệu -58 dBm</div></div>{ic("chevron-right",24)}</div>'
                 f'<div class="btn" style="margin-top:8px">{ic("stop",20)}Dừng quét</div>'
                 f'<div style="font-size:12px;color:rgba(27,75,67,.6);margin-top:8px;line-height:1.4">Mẹo: tháo kính khỏi sạc, đeo hoặc mở nắp để kính sáng, và đóng các app khác đang giữ kết nối với kính.</div></div>')
    sheet = (f'<div class="sheet" style="padding:0 16px 28px"><div class="hd"></div>'
             f'<div style="font-size:20px;font-weight:900">Kính phiên dịch</div>'
             f'<div style="font-size:13px;color:rgba(27,75,67,.7);margin:4px 0 14px;line-height:1.4">Kết nối kính Brilliant Labs Frame để bản dịch hiện ngay trước mắt, theo từng chữ khi bạn đang nói.</div>'
             f'{st}{bodyh}</div>')
    return screen(translate_body("Where is the nearest airport?", "Sân bay gần nhất ở đâu?", tgt="Tiếng Việt", glasses=connected),
                  nav=0, overlay='<div class="scrim"></div>' + sheet)

# ---------- history ----------
def hist_cards(sel=()):
    def trans(dir_, tm, s, t, sl="x"):
        return (f'<div class="hcard"><div class="top"><span class="pill">{dir_}</span><span class="tm">{tm}</span></div>'
                f'<div class="srow"><div class="s">{words(s, sel)}</div><div class="cp">{ic("content-copy",18)}</div></div>'
                f'<div class="srow t"><div class="s">{words(t, sel)}</div><div class="cp">{ic("content-copy",18)}</div></div></div>')
    conv = ('<div class="hcard"><div class="top"><span class="pill">EN → VI</span><span class="pill sand">4 lượt nói</span>'
            '<span class="tm">8:15</span></div>'
            '<div style="font-weight:700;font-size:14px;padding:8px 9px 0 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">08:15:02  Where is the nearest airport?</div>'
            f'<div style="display:flex"><div class="tb">{ic("content-copy",16)}Chép nguồn</div><div class="tb">{ic("content-copy",16)}Chép đích</div></div>'
            f'<div class="tb" style="padding-left:4px">{ic("chevron-right",18)}Chi tiết · có tóm tắt</div></div>')
    return (trans("EN → JA","8:28","Good morning, how are you today?","おはようございます、今日はどうですか？") + conv +
            trans("VI → EN","15/11","Tôi có một cuộc họp vào sáng mai.","I have a meeting tomorrow morning.") +
            trans("EN → JA","14/11","Thank you very much","どうもありがとうございます"))

def s_history(sel=False):
    selset = ("morning", "today") if sel else ()
    act = f'<div class="txtbtn">Xóa tất cả</div>'
    bar = ('<div class="selbar"><div class="c">Đã chọn 2 từ</div><div class="txtbtn" style="margin-right:4px">Bỏ chọn</div>'
           '<div class="btn m44">Lưu vào sổ tay</div></div>') if sel else ""
    body = appbar("Lịch sử", act) + f'<div class="scroll" style="padding-top:8px">{hist_cards(selset)}</div>' + bar
    return screen(body, nav=1)

def s_conv():
    segs = [("08:15:02","+0:00","Where is the nearest airport?","Sân bay gần nhất ở đâu?"),
            ("08:15:21","+0:19","How much does a taxi cost?","Đi taxi hết bao nhiêu tiền?"),
            ("08:16:03","+1:01","Thank you very much","Cảm ơn bạn rất nhiều"),
            ("08:16:41","+1:39","Have a nice day","Chúc một ngày tốt lành")]
    rows = "".join(f'<div style="background:var(--ivory);border:1px solid var(--line);border-radius:14px;padding:10px 14px;margin-bottom:8px">'
                   f'<div style="font-size:11.5px;color:rgba(27,75,67,.5);font-weight:700">{a} · {b}</div>'
                   f'<div style="font-weight:700;font-size:14px;margin-top:3px">{s}</div>'
                   f'<div style="font-size:14px;margin-top:2px;color:rgba(27,75,67,.75)">→ {t}</div></div>' for a,b,s,t in segs)
    stat = lambda l,v: f'<div style="flex:1"><div style="font-size:11px;color:rgba(27,75,67,.5);font-weight:700">{l}</div><div style="font-size:14px;font-weight:800;margin-top:2px">{v}</div></div>'
    body = (appbar("Hội thoại", f'<div class="ib">{ic("content-copy",24)}</div><div class="ib">{ic("delete-outline",24)}</div>', back=True) +
            f'<div class="scroll" style="padding-top:8px">'
            f'<div class="card" style="padding:14px 16px"><div style="font-weight:900;font-size:16px">Tiếng Anh → Tiếng Việt</div>'
            f'<div style="display:flex;margin-top:10px">{stat("Bắt đầu","08:15:02")}{stat("Kết thúc","08:16:41")}{stat("Thời lượng","1 phút 39 giây")}</div></div>'
            f'<div style="display:flex;align-items:center;gap:8px;margin:18px 0 6px"><span style="font-weight:800;font-size:16px">Các lượt nói (4)</span></div>'
            f'<div style="font-size:12px;color:rgba(27,75,67,.55);margin-bottom:10px;line-height:1.4">Chạm một lượt để xem chi tiết. Trong chi tiết, chạm một hoặc nhiều từ rồi bấm "Lưu vào sổ tay".</div>'
            f'{rows}'
            f'<div style="display:flex;align-items:center;gap:8px;margin:14px 0 8px">{ic("creation",18,"var(--coral)")}<span style="font-weight:800;font-size:16px">Tóm tắt</span></div>'
            f'<div class="card" style="padding:12px 14px;font-size:13.5px;line-height:1.5">Người nói hỏi đường tới sân bay gần nhất và giá taxi, sau đó cảm ơn và chào tạm biệt.</div>'
            f'</div>')
    return screen(body)

# ---------- AI ----------
def ai_appbar(summ=False):
    return appbar("Luyện cùng AI", (f'<div class="ib">{ic("creation",24)}</div>' if summ else "") + '<div style="width:6px"></div>')

def s_ai_empty():
    sug = (f'<div class="sugg"><span>{ic("arrow-top-right",15,"var(--coral)")}Sửa câu này giúp mình</span>'
           f'<span>{ic("arrow-top-right",15,"var(--coral)")}Luyện hội thoại ngắn</span></div>')
    body = (ai_appbar() + f'<div class="center"><div class="ico72">{ic("creation",32)}</div>'
            f'<div class="h5 serif" style="margin-top:20px">Một người bạn để<br>luyện ngôn ngữ.</div>'
            f'<div class="sub" style="margin-top:10px">Hỏi về ngữ pháp, thử một cuộc hội thoại, hoặc nhờ AI sửa câu cho bạn.</div>{sug}</div>'
            f'<div class="composer"><div class="in">{ic("chat-outline",22)}Viết tin nhắn cho AI…</div>'
            f'<div class="send">{ic("arrow-up",24)}</div></div>')
    return screen(body, nav=2)

def s_ai_chat():
    msgs = ('<div class="ubub"><div>Fix this sentence: I goes to school yesterday</div></div>'
            '<div class="abub"><div>Câu đúng là: "I went to school yesterday."<br><br>Hai lỗi nhỏ cần sửa:<br>'
            '• "goes" → "went": có "yesterday" nên dùng thì quá khứ đơn.<br>'
            '• Với chủ ngữ "I", động từ không thêm -es.<br><br>Bạn thử đặt thêm một câu với "went" nhé?</div></div>'
            '<div class="ubub"><div>I went to the market with my friend last weekend.</div></div>'
            '<div class="abub"><div>Rất tốt! Câu này hoàn toàn chính xác. Bạn có thể nói tự nhiên hơn với "I went to the market with a friend last weekend."</div></div>')
    body = (ai_appbar(True) + f'<div class="scroll" style="padding-top:8px">{msgs}</div>'
            f'<div class="composer"><div class="in">{ic("chat-outline",22)}Viết tin nhắn cho AI…</div>'
            f'<div class="send">{ic("arrow-up",24)}</div></div>')
    return screen(body, nav=2)

def s_ai_guest():
    body = (appbar("Luyện cùng AI") + f'<div class="center"><div class="ico72">{ic("cloud-off-outline",32)}</div>'
            f'<div class="h5 serif" style="margin-top:20px">AI cần tài khoản<br>và kết nối mạng.</div>'
            f'<div class="sub" style="margin-top:10px">Bạn đang ở chế độ khách. Dịch, từ vựng và flashcard vẫn dùng được hoàn toàn ngoại tuyến; đăng nhập để trò chuyện với AI.</div>'
            f'<div class="btn" style="margin-top:22px;width:100%">Đăng nhập / Đăng ký</div></div>')
    return screen(body, nav=2)

# ---------- vocab ----------
WORDS = [("morning","/ˈmɔːrnɪŋ/","buổi sáng","EN → VI",True),
         ("hello","/həˈloʊ/","xin chào","EN → VI",False),
         ("beautiful","/ˈbjuːtɪfəl/","xinh đẹp","EN → VI",False),
         ("journey","/ˈdʒɜːrni/","hành trình","EN → VI",False),
         ("airport","/ˈɛrpɔːrt/","sân bay","EN → VI",False),
         ("ありがとう","","cảm ơn","JA → VI",False)]
def wcard(w, ph, m, d, fresh=False, saved=None):
    pill = '<span class="pill tint">mới lưu</span>' if fresh else ""
    if saved is not None:
        pill = '<span class="pill">đã lưu</span>' if saved else ""
        right = f'<div class="a">{ic("volume-high",20)}</div><div class="a">{ic("bookmark" if saved else "bookmark-plus-outline",20, "var(--coral)" if saved else "currentColor")}</div>'
    else:
        right = f'<div class="a">{ic("volume-high",20)}</div><div class="a">{ic("delete-outline",20)}</div>'
    return (f'<div class="wcard"><div class="m"><div class="wd">{w}<span class="ph">{ph}</span>{pill}</div>'
            f'<div class="mean">{m}</div><div class="dir">{d}</div></div>{right}</div>')

def vocab_head(tab):
    return (f'<div class="serif h5" style="padding:8px 16px 4px">Từ vựng</div>'
            f'<div class="tabs"><div class="{"on" if tab==0 else ""}">Sổ tay của tôi</div><div class="{"on" if tab==1 else ""}">Kho hệ thống</div></div>'
            f'<div style="height:1px;background:var(--line)"></div>')

def add_btn():
    return (f'<div class="btn out sm" style="height:36px;gap:4px;color:var(--moss);font-weight:800">{ic("plus",18)}Thêm từ</div>')

def vocab_my(overlay=""):
    head = (f'<div style="display:flex;align-items:center;padding:10px 16px 4px"><span style="font-size:12.5px;color:rgba(27,75,67,.5)">{len(WORDS)} từ đã lưu</span>'
            f'<span style="flex:1"></span>{add_btn()}<span style="width:8px"></span><div class="btn sm">Luyện Flashcard</div></div>')
    cards = "".join(wcard(*w[:3], w[3], w[4]) for w in WORDS)
    return screen(vocab_head(0) + head + f'<div class="scroll" style="padding-top:4px">{cards}</div>', nav=3, overlay=overlay)

def s_vocab_sys():
    chips = '<div class="chips"><span class="chip on">Tất cả</span><span class="chip">giao tiếp</span><span class="chip">du lịch</span><span class="chip">công việc</span></div>'
    items = [("hello","/həˈloʊ/","xin chào","EN → VI",True),("thank you","/θæŋk juː/","cảm ơn","EN → VI",False),
             ("airport","/ˈɛrpɔːrt/","sân bay","EN → VI",True),("passport","/ˈpæspɔːrt/","hộ chiếu","EN → VI",False),
             ("meeting","/ˈmiːtɪŋ/","cuộc họp","EN → VI",False),("deadline","/ˈdedlaɪn/","hạn chót","EN → VI",False)]
    cards = "".join(wcard(w,p,m,d,saved=s) for w,p,m,d,s in items)
    body = (vocab_head(1) + f'<div class="search">{ic("magnify",20,"rgba(27,75,67,.5)")}Tìm từ trong kho hệ thống…</div>' + chips +
            '<div style="font-size:12px;color:rgba(27,75,67,.45);padding:6px 16px 4px">8 từ trong kho hệ thống</div>' +
            f'<div class="scroll" style="padding-top:4px">{cards}</div>')
    return screen(body, nav=3)

def s_add_word():
    dlg = (f'<div class="scrim"></div><div class="dialog"><h2 class="serif">Thêm từ mới</h2>'
           f'<div class="ofield" style="margin-top:18px"><span class="fl">Từ *</span>serendipity</div>'
           f'<div style="display:flex;gap:10px"><div class="ofield" style="flex:1;font-size:14px"><span class="fl">Ngôn ngữ của từ</span>Tiếng Anh{ic("menu-down",20,extra="margin-left:auto")}</div>'
           f'<div class="ofield" style="flex:1;font-size:14px"><span class="fl">Ngôn ngữ của nghĩa</span>Tiếng Việt{ic("menu-down",20,extra="margin-left:auto")}</div></div>'
           f'<div class="ofield" style="border:1.5px solid var(--moss)"><span class="fl">Nghĩa của từ *</span><span style="flex:1">sự tình cờ may mắn</span>{ic("creation",20,"var(--coral)")}</div>'
           f'<div style="font-size:12px;color:rgba(27,75,67,.6);margin:6px 0 0 14px">Đã gợi ý tự động, bạn có thể sửa lại</div>'
           f'<div class="dlgact"><span>Hủy</span><span style="background:var(--coral);color:var(--ivory);border-radius:15px;padding:10px 18px">Lưu vào sổ tay</span></div></div>')
    return vocab_my(dlg)

def s_flash(flipped):
    mean = (f'<div style="font-size:23px;font-weight:800;color:var(--coral);margin-top:14px">hành trình</div>' if flipped else
            '<div style="font-size:13px;color:rgba(27,75,67,.45);margin-top:14px">Chạm vào thẻ để xem nghĩa</div>')
    body = (appbar("Flashcard", back=True) + '<div class="scroll" style="padding:16px;text-align:center">'
            '<div style="font-size:13px;font-weight:700;color:rgba(27,75,67,.55)">Ôn tập hôm nay · 4 / 6</div>'
            '<div style="margin-top:16px;background:var(--ivory);border-radius:26px;min-height:300px;padding:24px;display:flex;flex-direction:column;'
            'align-items:center;justify-content:center;box-shadow:0 8px 24px rgba(27,75,67,.08)">'
            '<div style="font-size:30px;font-weight:800">journey</div>'
            '<div style="font-size:14px;color:rgba(27,75,67,.5);margin-top:6px">/ˈdʒɜːrni/</div>' + mean + '</div>'
            f'<div style="display:flex;gap:12px;margin-top:20px"><div class="btn out" style="flex:1">{ic("volume-high",18)}Phát âm</div>'
            f'<div class="btn" style="flex:1">Thẻ tiếp theo{ic("arrow-right",18)}</div></div></div>')
    return screen(body)

# ---------- profile / offline ----------
def banner(name, line):
    return (f'<div style="background:var(--moss);border-radius:22px;padding:24px;display:flex;align-items:center;gap:16px;color:var(--ivory)">'
            f'<div style="width:64px;height:64px;border-radius:20px;background:var(--coral);display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:900">{name[0]}</div>'
            f'<div><div style="font-size:20px;font-weight:900">{name}</div><div style="font-size:13px;opacity:.72;margin-top:4px">{line}</div></div></div>')

def ptile(icon, title, sub, destructive=False):
    return (f'<div class="ptile{" d" if destructive else ""}"><div class="bx">{ic(icon,20)}</div>'
            f'<div class="tt">{title}<div class="st">{sub}</div></div>{ic("chevron-right",24,"rgba(27,75,67,.35)")}</div>')

def about():
    return (f'<div class="h6">Về Lingua</div><div class="card" style="padding:16px;display:flex;gap:12px;align-items:center">{ic("creation",24,"var(--coral)")}'
            f'<div style="font-size:14px;line-height:1.4">Một góc nhỏ để dịch, luyện tập và giữ lại những từ đáng nhớ.</div></div>')

def s_profile(guest=False):
    off = (f'<div class="h6">Ngoại tuyến</div><div class="card">{ptile("download-circle-outline","Gói ngoại tuyến","Đã tải: Dịch: Tiếng Anh, Tiếng Việt, Tiếng Nhật<br>Giọng nói: Tiếng Anh, Tiếng Việt")}</div>')
    if guest:
        acc = (ptile("login","Đăng nhập / Đăng ký","Đồng bộ từ vựng và lịch sử, dùng AI") + '<div class="sep"></div>' +
               ptile("logout","Thoát chế độ khách","Dữ liệu khách vẫn được giữ trên máy này", True))
        top = banner("Người học", "Chế độ khách · dữ liệu lưu trên máy này") + '<div style="height:24px"></div>' + guest_strip()
        top = top.replace('<div style="height:24px"></div>','<div style="height:20px"></div>')
    else:
        acc = (ptile("sync","Đồng bộ ngay","Gửi các thay đổi đã lưu khi ngoại tuyến lên máy chủ") + '<div class="sep"></div>' +
               ptile("lock-outline","Đổi mật khẩu","Cập nhật thông tin bảo mật (cần mạng)") + '<div class="sep"></div>' +
               ptile("logout","Đăng xuất","Thoát khỏi tài khoản trên thiết bị này", True))
        top = banner("Nguyễn Văn A", "user1@example.com")
    first = off.replace('<div class="h6">', '<div class="h6" style="margin-top:20px">', 1) if guest else off
    body = (appbar("Cá nhân") + f'<div class="scroll" style="padding-top:8px">{top}{first}'
            f'<div class="h6">Tài khoản</div><div class="card">{acc}</div>{about()}</div>')
    return screen(body, nav=4)

def s_offline():
    def row(name, state, kind="done", pct=0):
        if kind == "done":
            sub, trail = "Đã tải · dùng được ngoại tuyến", ic("delete-outline",24,"rgba(27,75,67,.6)")
            extra = ""
        elif kind == "dl":
            sub, trail = f"Đang tải… {pct}%", '<span style="font-weight:800;font-size:14px;padding:0 12px">Hủy</span>'
            extra = f'<div class="bar"><i style="width:{pct}%"></i></div>'
        else:
            sub, trail = "Chưa tải về máy", '<div class="btn sm" style="height:40px;border-radius:15px;padding:0 18px">Tải</div>'
            extra = ""
        return (f'<div style="display:flex;align-items:center;padding:12px 8px 12px 16px;border-bottom:1px solid var(--line)">'
                f'<div style="flex:1"><div style="font-weight:800;font-size:16px">{name}</div>'
                f'<div style="font-size:12.5px;color:rgba(27,75,67,.6);margin-top:2px">{sub}</div>{extra}</div>{trail}</div>')
    ml = row("Tiếng Anh","", "done") + row("Tiếng Việt","","done") + row("Tiếng Nhật","","dl",42)
    vk = row("Tiếng Anh","","done") + row("Tiếng Việt","","done") + row("Tiếng Nhật","","none")
    body = (appbar("Gói ngoại tuyến", back=True) + '<div class="scroll" style="padding-top:8px">'
            '<div style="background:var(--sand);border-radius:14px;padding:16px;font-size:14px;line-height:1.4">Tải một lần khi có mạng. Sau đó dịch và nhận diện giọng nói chạy hoàn toàn trên máy — không cần mạng hay máy chủ.</div>'
            f'<div class="h6" style="margin-top:20px">Dịch văn bản (ML Kit)</div><div class="card" style="overflow:hidden">{ml}</div>'
            f'<div class="h6">Nhận diện giọng nói (Vosk)</div><div class="card" style="overflow:hidden">{vk}</div></div>')
    return screen(body)

# ---------- auth / splash ----------
def s_splash():
    body = ('<div style="position:absolute;top:-90px;right:-70px;width:230px;height:230px;border-radius:50%;background:var(--coral)"></div>'
            '<div style="position:absolute;bottom:-110px;left:-85px;width:260px;height:260px;border-radius:50%;background:rgba(255,253,249,.08)"></div>'
            f'<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center">{brand(dark=True)}'
            '<div class="serif h5" style="color:var(--ivory);text-align:center;margin-top:22px;line-height:1.18">Ngôn ngữ mở ra<br>những cuộc gặp gỡ.</div>'
            '<div class="spin" style="margin-top:34px"></div></div>')
    return screen(body, dark=True, bg="var(--moss)")

def s_login(register=False):
    title = "Tạo không gian<br>học của riêng bạn." if register else "Chào mừng<br>quay trở lại."
    sub = "Lưu lại từ mới, luyện nói và theo dõi tiến bộ mỗi ngày." if register else "Tiếp tục hành trình học ngôn ngữ của bạn, từng câu một."
    name = (f'<div class="field"><span class="fl">Họ và tên</span>{ic("account-outline",24)}<span class="v">Nguyễn Văn A</span></div>' if register else "")
    pw = ('<div class="field f" style="margin-bottom:' + ('30px' if register else '14px') + '"><span class="fl">Mật khẩu</span>'
          f'{ic("lock-outline",24)}<span class="v" style="letter-spacing:2px">••••••••</span>{ic("eye-off-outline",24)}'
          + ('<span class="hp">Tối thiểu 6 ký tự</span>' if register else '') + '</div>')
    btn = "Bắt đầu học" if register else "Đăng nhập"
    q, a = ("Đã có tài khoản?", "Đăng nhập") if register else ("Chưa có tài khoản?", "Đăng ký ngay")
    body = (f'<div style="padding:{ "16px" if register else "30px" } 24px 16px">{brand()}<div style="height:{ "24px" if register else "44px"}"></div>'
            f'<div class="serif" style="font-size:30px;line-height:1.12;font-weight:700">{title}</div>'
            f'<div style="font-size:16px;line-height:1.45;color:rgba(27,75,67,.66);margin:12px 0 {"22px" if register else "30px"}">{sub}</div>'
            f'{name}<div class="field"><span class="fl">Email</span>{ic("at",24)}<span class="v">{"nguyenvana@example.com" if register else "user1@example.com"}</span></div>{pw}'
            f'<div style="height:{ "4px" if register else "10px"}"></div><div class="btn">{btn}</div>'
            f'<div class="btn out" style="margin-top:12px">{ic("account-outline",20)}Dùng với tư cách khách</div>'
            f'<div style="font-size:12px;line-height:1.4;text-align:center;color:rgba(27,75,67,.55);margin-top:6px">Không cần tài khoản hay mạng: dịch offline, lưu từ vựng và lịch sử ngay trên máy. Đăng nhập sau để đồng bộ.</div>'
            f'<div style="display:flex;justify-content:center;align-items:center;gap:4px;margin-top:6px;height:48px;font-size:14px"><span style="color:rgba(27,75,67,.65)">{q}</span><b style="font-weight:800;padding:0 8px">{a}</b></div>'
            f'<div style="text-align:center;font-size:12px;font-weight:700;letter-spacing:.6px;color:rgba(27,75,67,.42);margin-top:{"8px" if register else "20px"}">Dịch • Luyện tập • Ghi nhớ</div></div>')
    return screen(body)

SCREENS = [
 ("01-splash", s_splash), ("02-login", s_login), ("03-register", lambda: s_login(True)),
 ("04-translate", s_translate), ("05-translate-voice-live", s_voice), ("06-language-picker", s_picker),
 ("07-history", s_history), ("08-history-select-words", lambda: s_history(True)), ("09-conversation-detail", s_conv),
 ("10-ai-empty", s_ai_empty), ("11-ai-chat", s_ai_chat), ("12-ai-guest-lock", s_ai_guest),
 ("13-vocabulary-my", vocab_my), ("14-vocabulary-system", s_vocab_sys), ("15-add-word-dialog", s_add_word),
 ("16-flashcard-front", lambda: s_flash(False)), ("17-flashcard-back", lambda: s_flash(True)),
 ("18-profile", s_profile), ("19-profile-guest", lambda: s_profile(True)),
 ("20-offline-packs", s_offline), ("21-glasses-scan", lambda: frame_sheet(False)), ("22-glasses-connected", lambda: frame_sheet(True)),
]

def page(inner, flat=False):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body class="{"flat" if flat else ""}">{inner}</body></html>'

if __name__ == "__main__":
    only = set(sys.argv[1:])
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, fn in SCREENS:
            if only and not any(o in name for o in only): continue
            inner = fn()
            for mode, flat in (("framed", False), ("flat", True)):
                pg = b.new_page(viewport={"width": 460, "height": 920}, device_scale_factor=2)
                pg.set_content(page(inner, flat)); pg.wait_for_timeout(120)
                pg.locator(".phone").screenshot(path=str(OUT / mode / f"{name}.png"), omit_background=True)
                pg.close()
            print("ok", name)
        b.close()
