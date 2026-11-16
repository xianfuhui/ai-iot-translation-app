#!/usr/bin/env python3
"""Dựng sơ đồ Data Model của Lingua -> docs/data-model.png

Nguồn sự thật: backend/src/models/*.js (field, enum, index) và
backend/scripts/sync-db.js (validator). Dùng: python3 build_data_model.py [out.png]
"""
import sys, pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "data-model.png")

MOSS, CORAL, PAPER, IVORY, LINE, TINT, SAND = "#1B4B43", "#F26B5E", "#F8F5EF", "#FFFDF9", "#D9D0C4", "#FBE0D8", "#EEE8DD"
MUTED = "#6B7F7A"
W, HEAD, ROW = 440, 46, 26
SANS, MONO = "Inter, sans-serif", "'DejaVu Sans Mono', monospace"

# field = (name, type, flag, note) ; flag in PK FK UK ref '' ; ("emb", title, [fields]) = embedded array
ENT = {}

def entity(key, x, y, title, subtitle, fields, indexes):
    ENT[key] = dict(x=x, y=y, title=title, sub=subtitle, fields=fields, idx=indexes)

entity("users", 640, 130, "users", "Tài khoản (user / admin)", [
    ("_id", "ObjectId", "PK", ""),
    ("fullName", "String", "", ""),
    ("email", "String", "UK", "lowercase"),
    ("password", "String", "", "bcrypt, select:false"),
    ("role", "enum", "", "user | admin"),
    ("isActive", "Boolean", "", ""),
    ("lastLoginAt", "Date", "", ""),
    ("createdAt / updatedAt", "Date", "", ""),
], ["unique {email}"])

entity("hist", 40, 130, "translationhistories", "Lịch sử dịch (đa hình theo type)", [
    ("_id", "ObjectId", "PK", ""),
    ("user", "ObjectId", "FK", "→ users"),
    ("type", "enum", "", "text|speech|ai_chat|conversation"),
    ("sourceLanguage", "String", "ref", "≈ languages.code"),
    ("targetLanguage", "String", "ref", "≈ languages.code"),
    ("sourceText", "String", "", "type ≠ conversation"),
    ("translatedText", "String", "", "type ≠ conversation"),
    ("startedAt / endedAt", "Date", "", "chỉ conversation"),
    ("summary", "String", "", "tóm tắt do AI"),
    ("segments[]", "embedded", "emb", "type = conversation, ≥ 1 lượt", [
        ("sourceText", "String"), ("translatedText", "String"), ("at", "Date")]),
    ("createdAt / updatedAt", "Date", "", ""),
], ["{user, createdAt:-1}", "{createdAt:-1}"])

entity("ai", 40, 700, "aiconversations", "Phiên chat với Gemini", [
    ("_id", "ObjectId", "PK", ""),
    ("user", "ObjectId", "FK", "→ users"),
    ("title", "String", "", ""),
    ("summary", "String", "", "tóm tắt do Gemini"),
    ("messages[]", "embedded", "emb", "tối đa 400 (app chặn 200)", [
        ("role", "enum: user | assistant"), ("content", "String"), ("createdAt / updatedAt", "Date")]),
    ("createdAt / updatedAt", "Date", "", ""),
], ["{user, updatedAt:-1}"])

entity("vocab", 1240, 130, "vocabularies", "Từ vựng cá nhân", [
    ("_id", "ObjectId", "PK", ""),
    ("user", "ObjectId", "FK", "→ users"),
    ("word", "String", "", ""),
    ("meaning", "String", "", ""),
    ("phonetic", "String", "", ""),
    ("audioUrl", "String", "", ""),
    ("sourceLanguage", "String", "ref", "≈ languages.code"),
    ("targetLanguage", "String", "ref", "≈ languages.code"),
    ("source", "enum", "", "conversation | manual"),
    ("inFlashcard", "Boolean", "", ""),
    ("createdAt / updatedAt", "Date", "", ""),
], ["unique {user, word, targetLanguage}", "{user, createdAt:-1}"])

entity("sysv", 1240, 640, "systemvocabularies", "Kho từ hệ thống (admin quản lý)", [
    ("_id", "ObjectId", "PK", ""),
    ("word", "String", "", ""),
    ("meaning", "String", "", ""),
    ("phonetic", "String", "", ""),
    ("audioUrl", "String", "", ""),
    ("category", "String", "", "chủ đề"),
    ("sourceLanguage", "String", "ref", "≈ languages.code"),
    ("targetLanguage", "String", "ref", "≈ languages.code"),
    ("createdBy", "ObjectId", "FK", "→ users (admin)"),
    ("createdAt / updatedAt", "Date", "", ""),
], ["{category, createdAt:-1}"])

entity("lang", 640, 520, "languages", "Ngôn ngữ hỗ trợ", [
    ("_id", "ObjectId", "PK", ""),
    ("code", "String", "UK", "en, vi, ja, zh-CN…"),
    ("name", "String", "", ""),
    ("isActive", "Boolean", "", "soft-delete"),
    ("createdAt / updatedAt", "Date", "", ""),
], ["unique {code}"])

entity("model", 640, 880, "models", "Catalog model offline (Vosk / ML Kit)", [
    ("_id", "ObjectId", "PK", ""),
    ("type", "enum", "", "vosk | mlkit"),
    ("languageCode", "String", "ref", "≈ languages.code"),
    ("name", "String", "", ""),
    ("identifier", "String", "", ""),
    ("downloadUrl", "String", "", "link ngoài"),
    ("fileName / originalFileName", "String", "", "file admin upload"),
    ("sizeMB", "Number", "", ""),
    ("description", "String", "", ""),
    ("isActive", "Boolean", "", ""),
    ("createdAt / updatedAt", "Date", "", ""),
], ["unique {type, languageCode, identifier}"])

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

rowy = {}   # (key, fieldname) -> absolute y centre
def layout(k):
    e = ENT[k]; y = e["y"] + HEAD; rows = []
    for f in e["fields"]:
        rows.append(("f", y, f)); rowy[(k, f[0])] = y + ROW / 2; y += ROW
        if f[2] == "emb":
            for sub in f[4]:
                rows.append(("s", y, sub)); y += ROW
    e["idx_y"] = y
    e["h"] = (y - e["y"]) + 12 + (22 * len(e["idx"]) + 30)
    e["rows"] = rows

for k in ENT: layout(k)

svg = []
def add(s): svg.append(s)

def draw_entity(k):
    e = ENT[k]; x, y, h = e["x"], e["y"], e["h"]
    add(f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="{W}" height="{h}" rx="16" fill="{IVORY}" stroke="{LINE}"/></g>')
    add(f'<path d="M{x},{y+16} a16,16 0 0 1 16,-16 h{W-32} a16,16 0 0 1 16,16 v{HEAD-16} h-{W} z" fill="{MOSS}"/>')
    add(f'<text x="{x+18}" y="{y+21}" font-family="{MONO}" font-weight="700" font-size="16" fill="#fff">{e["title"]}</text>')
    add(f'<text x="{x+18}" y="{y+38}" font-family="{SANS}" font-size="11" fill="#BBD0CA">{esc(e["sub"])}</text>')
    for i, (kind, ry, f) in enumerate(e["rows"]):
        cy = ry + ROW / 2 + 4
        if kind == "f":
            name, typ, flag, note = f[0], f[1], f[2], f[3]
            if flag == "emb":
                add(f'<rect x="{x+1}" y="{ry}" width="{W-2}" height="{ROW}" fill="{SAND}"/>')
            # badge
            if flag in ("PK", "FK", "UK", "ref"):
                col = {"PK": MOSS, "FK": CORAL, "UK": "#B07A1E", "ref": "#7E8E88"}[flag]
                lab = {"PK": "PK", "FK": "FK", "UK": "UQ", "ref": "REF"}[flag]
                bw = 28 if lab != "REF" else 32
                add(f'<rect x="{x+14}" y="{ry+5}" width="{bw}" height="16" rx="8" fill="{col}"/>')
                add(f'<text x="{x+14+bw/2}" y="{ry+17}" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="9.5" fill="#fff">{lab}</text>')
            add(f'<text x="{x+52}" y="{cy}" font-family="{MONO}" font-size="12.5" font-weight="{700 if flag in ("PK","FK","emb") else 500}" fill="{MOSS}">{esc(name)}</text>')
            add(f'<text x="{x+W-14}" y="{cy}" text-anchor="end" font-family="{MONO}" font-size="11.5" fill="{MUTED}">{esc(typ)}</text>')
            if note:
                add(f'<text x="{x+52}" y="{cy+0}" dx="0" font-family="{SANS}" font-size="0" fill="none"></text>')
            if flag == "emb":
                add(f'<text x="{x+210}" y="{cy}" font-family="{SANS}" font-size="10" fill="{MUTED}" text-anchor="middle" style="display:none"></text>')
        else:
            add(f'<line x1="{x+30}" y1="{ry}" x2="{x+30}" y2="{ry+ROW}" stroke="{CORAL}" stroke-width="2"/>')
            add(f'<text x="{x+44}" y="{cy}" font-family="{MONO}" font-size="12" fill="{MOSS}">{esc(f[0])}</text>')
            add(f'<text x="{x+W-14}" y="{cy}" text-anchor="end" font-family="{MONO}" font-size="11.5" fill="{MUTED}">{esc(f[1])}</text>')
    # notes (right of name, small)  -> rendered second pass for alignment
    for kind, ry, f in e["rows"]:
        if kind == "f" and f[3]:
            cy = ry + ROW / 2 + 4
            add(f'<text x="{x+W-92}" y="{cy}" text-anchor="end" font-family="{SANS}" font-size="10" fill="{MUTED}">{esc(f[3])}</text>')
    # indexes
    iy = e["idx_y"] + 8
    add(f'<line x1="{x+14}" y1="{iy}" x2="{x+W-14}" y2="{iy}" stroke="{LINE}"/>')
    add(f'<text x="{x+16}" y="{iy+19}" font-family="{SANS}" font-weight="700" font-size="10" fill="{MUTED}" letter-spacing=".8">INDEXES</text>')
    for j, t in enumerate(e["idx"]):
        add(f'<text x="{x+16}" y="{iy+38+22*j}" font-family="{MONO}" font-size="11.5" fill="{MOSS}">▸ {esc(t)}</text>')

# ---------- connectors ----------
def one_end(x, y, s, col):   # "đúng một": 2 vạch, s = hướng đường đi ra khỏi entity
    return (f'<line x1="{x+s*9}" y1="{y-8}" x2="{x+s*9}" y2="{y+8}" stroke="{col}" stroke-width="2"/>'
            f'<line x1="{x+s*15}" y1="{y-8}" x2="{x+s*15}" y2="{y+8}" stroke="{col}" stroke-width="2"/>')

def many_end(x, y, s, col):  # chân chim
    return (f'<path d="M{x+s*16},{y} L{x},{y-9} M{x+s*16},{y} L{x},{y} M{x+s*16},{y} L{x},{y+9}" stroke="{col}" stroke-width="2" fill="none"/>'
            f'<line x1="{x+s*22}" y1="{y-8}" x2="{x+s*22}" y2="{y+8}" stroke="{col}" stroke-width="2"/>')

def conn(parent, pside, py, child, cside, cy, bus, dashed=False, col=MOSS, halo=False):
    px = ENT[parent]["x"] + (W if pside == "R" else 0)
    cx = ENT[child]["x"] + (W if cside == "R" else 0)
    ps = 1 if pside == "R" else -1
    cs = 1 if cside == "R" else -1
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    d = f"M{px+ps*15},{py} L{bus},{py} L{bus},{cy} L{cx+cs*22},{cy}"
    if halo:
        add(f'<path d="{d}" fill="none" stroke="{PAPER}" stroke-width="7"/>')
    add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2"{dash}/>')
    add(one_end(px, py, ps, col)); add(many_end(cx, cy, cs, col))

def ry_(k, f): return rowy[(k, f)]

# build drawing: connectors first (under cards)
body_start = len(svg)

# users 1—N
u = ENT["users"]
urow = lambda n: u["y"] + 60 + 14 * n
conn("users", "L", urow(0), "hist", "R", ry_("hist", "user"), 590)
conn("users", "L", urow(2), "ai", "R", ry_("ai", "user"), 570)
conn("users", "R", urow(0), "vocab", "L", ry_("vocab", "user"), 1170)
conn("users", "R", urow(2), "sysv", "L", ry_("sysv", "createdBy"), 1190)

# soft refs -> languages.code (nét đứt)
lang_y = ry_("lang", "code")
CORAL_D = "#C0574D"
conn("lang", "L", lang_y, "hist", "R", ry_("hist", "targetLanguage"), 530, True, CORAL_D, True)
conn("lang", "R", lang_y, "vocab", "L", ry_("vocab", "targetLanguage"), 1130, True, CORAL_D, True)
conn("lang", "R", lang_y + 14, "sysv", "L", ry_("sysv", "targetLanguage"), 1110, True, CORAL_D, True)
# models.languageCode -> languages.code (thẳng đứng)
lx = ENT["lang"]["x"] + W / 2
ty = ENT["lang"]["y"] + ENT["lang"]["h"]
my = ENT["model"]["y"]
add(f'<line x1="{lx}" y1="{ty+15}" x2="{lx}" y2="{my-22}" stroke="{CORAL_D}" stroke-width="2" stroke-dasharray="7 5"/>')
add(f'<g transform="translate({lx},{ty}) rotate(0)">' + '<line x1="-8" y1="9" x2="8" y2="9" stroke="%s" stroke-width="2"/><line x1="-8" y1="15" x2="8" y2="15" stroke="%s" stroke-width="2"/></g>' % (CORAL_D, CORAL_D))
add(f'<path d="M{lx},{my-16} L{lx-9},{my} M{lx},{my-16} L{lx},{my} M{lx},{my-16} L{lx+9},{my}" stroke="{CORAL_D}" stroke-width="2" fill="none"/>'
    f'<line x1="{lx-8}" y1="{my-22}" x2="{lx+8}" y2="{my-22}" stroke="{CORAL_D}" stroke-width="2"/>')

for k in ENT: draw_entity(k)

# ---------- labels / notes ----------
def pill(x, y, t, col=MOSS, w=None):
    w = w or (len(t) * 6.4 + 18)
    add(f'<rect x="{x-w/2}" y="{y-10}" width="{w}" height="20" rx="10" fill="{IVORY}" stroke="{col}"/>')
    add(f'<text x="{x}" y="{y+4}" text-anchor="middle" font-family="{SANS}" font-size="10.5" font-weight="600" fill="{col}">{t}</text>')

pill(lx, (ty + my) / 2, "languageCode ≈ code", CORAL_D)

# header + legend + design notes
head = f'''
<text x="40" y="60" font-family="'Noto Serif CJK JP','DejaVu Serif',serif" font-size="34" font-weight="700" fill="{MOSS}">Lingua · Data Model</text>
<text x="40" y="88" font-family="{SANS}" font-size="14" fill="{MUTED}">MongoDB 7 · database <tspan font-family="{MONO}">language_app</tspan> · 7 collections · khớp với <tspan font-family="{MONO}">backend/src/models</tspan> và validator trong <tspan font-family="{MONO}">scripts/sync-db.js</tspan></text>
'''
lg_x, lg_y = 1240, 1060
legend = f'''
<g transform="translate({lg_x},{lg_y})">
 <rect width="{W}" height="330" rx="16" fill="{IVORY}" stroke="{LINE}"/>
 <text x="18" y="30" font-family="{SANS}" font-weight="700" font-size="12" fill="{MUTED}" letter-spacing=".8">CHÚ GIẢI</text>
 <rect x="18" y="44" width="28" height="16" rx="8" fill="{MOSS}"/><text x="32" y="56" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="9.5" fill="#fff">PK</text>
 <text x="58" y="57" font-family="{SANS}" font-size="12.5" fill="{MOSS}">Khóa chính (_id)</text>
 <rect x="18" y="70" width="28" height="16" rx="8" fill="{CORAL}"/><text x="32" y="82" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="9.5" fill="#fff">FK</text>
 <text x="58" y="83" font-family="{SANS}" font-size="12.5" fill="{MOSS}">Tham chiếu ObjectId (ref → users)</text>
 <rect x="18" y="96" width="28" height="16" rx="8" fill="#B07A1E"/><text x="32" y="108" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="9.5" fill="#fff">UQ</text>
 <text x="58" y="109" font-family="{SANS}" font-size="12.5" fill="{MOSS}">Trường có unique index</text>
 <rect x="18" y="122" width="32" height="16" rx="8" fill="#7E8E88"/><text x="34" y="134" text-anchor="middle" font-family="{SANS}" font-weight="700" font-size="9.5" fill="#fff">REF</text>
 <text x="58" y="135" font-family="{SANS}" font-size="12.5" fill="{MOSS}">Tham chiếu mềm theo mã ngôn ngữ (không phải ObjectId)</text>
 <line x1="18" y1="158" x2="18" y2="178" stroke="{CORAL}" stroke-width="2"/><rect x="18" y="158" width="28" height="20" fill="{SAND}"/>
 <text x="58" y="172" font-family="{SANS}" font-size="12.5" fill="{MOSS}">Mảng nhúng (embedded), đọc cùng document cha</text>
 {one_end(30,205,1,MOSS).replace('x1="39"','x1="39"')}
 <path d="M18,205 L120,205" stroke="{MOSS}" stroke-width="2" fill="none"/>
 <text x="136" y="209" font-family="{SANS}" font-size="12.5" fill="{MOSS}">1 — N, tham chiếu bằng ObjectId</text>
 <path d="M18,235 L120,235" stroke="{CORAL_D}" stroke-width="2" stroke-dasharray="7 5"/>
 <text x="136" y="239" font-family="{SANS}" font-size="12.5" fill="{MOSS}">1 — N, tham chiếu mềm theo <tspan font-family="{MONO}">code</tspan></text>
 <text x="18" y="274" font-family="{SANS}" font-size="11.5" fill="{MUTED}">Mọi collection đều có <tspan font-family="{MONO}">createdAt/updatedAt</tspan> (timestamps).</text>
 <text x="18" y="294" font-family="{SANS}" font-size="11.5" fill="{MUTED}">Tạo bởi Mongoose + <tspan font-family="{MONO}">$jsonSchema</tspan> trên cả 7 collection;</text>
 <text x="18" y="312" font-family="{SANS}" font-size="11.5" fill="{MUTED}">xóa user cascade trong application code (transaction).</text>
</g>'''
# legend's marker examples use the real glyphs
total_w = 1720
total_h = max(e["y"] + e["h"] for e in ENT.values())
total_h = max(total_h, lg_y + 330) + 40

doc = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}">
<defs><filter id="sh" x="-5%" y="-5%" width="110%" height="115%"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="{MOSS}" flood-opacity=".14"/></filter></defs>
<rect width="100%" height="100%" fill="{PAPER}"/>
{head}
{"".join(svg)}
{legend}
</svg>'''

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": total_w, "height": total_h}, device_scale_factor=2)
    pg.set_content(f'<html><body style="margin:0;background:{PAPER}">{doc}</body></html>')
    pg.screenshot(path=str(OUT), clip={"x": 0, "y": 0, "width": total_w, "height": total_h})
    b.close()
print("wrote", OUT, total_w, total_h)
