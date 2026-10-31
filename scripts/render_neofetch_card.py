"""Render the neofetch-style profile card (dark + light) for the README.

Edit DETAILS / CONTACT below, then run:
    python scripts/render_neofetch_card.py --photo assets/profile-cutout.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance

# Groups are separated by a faint divider. Keys follow neofetch's own labels.
DETAILS = [
    [
        ("OS", "B.E. CSE @ VVCE, Mysuru"),
        ("Host", "Radar Engineering Intern @ LRDE–DRDO"),
        ("Kernel", "Cybersecurity · AI · Full Stack"),
        ("Uptime", "2023 → 2027"),
    ],
    [
        ("Packages", "Python · C/C++ · Java · React · Node.js"),
        ("Cloud", "AWS · GCP · Docker · Kubernetes"),
        ("Shell", "Git · Linux · Postman · n8n"),
        ("AI", "RAG · LangChain · FAISS · ChromaDB"),
    ],
    [
        ("Awards", "3rd place · GLYTCH National Hackathon"),
        ("Status", "Building secure, intelligent systems"),
    ],
]
CONTACT = [
    ("Email", "loganthp55@gmail.com"),
    ("Phone", "+91 70136 60227"),
]

MONO = "Consolas, 'Cascadia Code', 'Fira Code', Menlo, Monaco, monospace"
THEMES = {
    "dark": dict(panel="#0A1022", chrome="#111827", ink="#E6EDF3", dim="#7D8A99",
                 accent="#00F7FF", accent2="#FF2E88", line="#00F7FF", cursor="#E6EDF3"),
    "light": dict(panel="#FFFFFF", chrome="#EAEEF2", ink="#1F2328", dim="#6E7781",
                  accent="#0E7490", accent2="#C0266D", line="#0E7490", cursor="#1F2328"),
}
PALETTE = (["#1F2937", "#EF4444", "#22C55E", "#EAB308", "#3B82F6", "#D946EF", "#06B6D4", "#E5E7EB"],
           ["#4B5563", "#F87171", "#4ADE80", "#FDE047", "#60A5FA", "#F0ABFC", "#67E8F9", "#FFFFFF"])

CHAR_W = 7.8          # approx. advance of a 13px monospace glyph
LINE = 21             # info line height
KEY_COL = 10          # characters reserved for keys ("Packages" + colon + space)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def portrait_cells(photo: Path, cols: int):
    cut = Image.open(photo).convert("RGBA")
    w, h = cut.size
    # head-and-shoulders square, centred on the subject's bounding box
    left, top, right, _ = cut.getbbox()
    side = min(right - left, h)
    cx = (left + right) // 2
    box = (max(0, cx - side // 2), max(0, top - 22), min(w, cx + side // 2), min(h, top - 22 + side))
    bust = cut.crop(box)
    im = bust.resize((cols, cols), Image.Resampling.LANCZOS)
    rgb = ImageEnhance.Color(ImageEnhance.Contrast(im.convert("RGB")).enhance(1.25)).enhance(1.25)
    pal = rgb.quantize(colors=20, method=Image.Quantize.MEDIANCUT).convert("RGB")
    rows = []
    for y in range(cols):
        row = []
        for x in range(cols):
            if im.getpixel((x, y))[3] >= 110:
                r, g, b = pal.getpixel((x, y))
                row.append((x, f"#{r:02x}{g:02x}{b:02x}"))
        rows.append(row)
    return rows


def render(theme: str, rows) -> str:
    t = THEMES[theme]
    cols, cell = len(rows), 4.95
    W = 880
    px = 360                                      # info column x
    n_lines = 2 + sum(len(g) for g in DETAILS) + len(CONTACT)
    gaps = len(DETAILS)                           # dividers incl. one before contact
    info_h = n_lines * LINE + gaps * 14 + 40      # + palette
    body_h = max(cols * cell, info_h)
    H = int(70 + body_h + 56)
    oy_info = 92
    oy_img = oy_info - 14 + max(0, (info_h - cols * cell) / 2)
    ox_img = 34

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'role="img" aria-label="Neofetch-style terminal card for Loganth" font-family="{MONO}">',
         f'<rect width="{W}" height="{H}" rx="12" fill="{t["panel"]}"/>',
         f'<rect x="0.75" y="0.75" width="{W-1.5}" height="{H-1.5}" rx="12" fill="none" stroke="{t["line"]}" stroke-opacity="0.35"/>',
         f'<path d="M0.75 12.75A12 12 0 0 1 12.75 0.75H{W-12.75}A12 12 0 0 1 {W-0.75} 12.75V34H0.75Z" fill="{t["chrome"]}"/>',
         '<circle cx="22" cy="18" r="5" fill="#FF5F56"/><circle cx="40" cy="18" r="5" fill="#FFBD2E"/><circle cx="58" cy="18" r="5" fill="#27C93F"/>',
         f'<text x="{W/2}" y="22" font-size="11.5" fill="{t["dim"]}" text-anchor="middle">loganth@github: ~</text>',
         f'<defs><clipPath id="type"><rect x="24" y="44" width="0" height="20">'
         f'<animate attributeName="width" from="0" to="250" dur="0.9s" begin="0.2s" fill="freeze"/></rect></clipPath></defs>',
         f'<text x="24" y="58" font-size="13" clip-path="url(#type)"><tspan fill="{t["accent"]}" font-weight="700">loganth@github</tspan>'
         f'<tspan fill="{t["ink"]}">:~$ neofetch</tspan></text>']

    # portrait, printed row by row
    s.append('<g shape-rendering="crispEdges">')
    for y, row in enumerate(rows):
        if not row:
            continue
        rects = "".join(f'<rect x="{ox_img + x*cell:.1f}" y="{oy_img + y*cell:.1f}" width="{cell+0.6:.2f}" '
                        f'height="{cell+0.6:.2f}" fill="{c}"/>' for x, c in row)
        s.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{1.2 + y*0.022:.3f}s" fill="freeze"/>{rects}</g>')
    s.append('</g>')

    # info column
    t0 = 1.35
    y = oy_info
    s.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t0}s" fill="freeze"/>'
             f'<text x="{px}" y="{y}" font-size="14" font-weight="700"><tspan fill="{t["accent"]}">loganth</tspan>'
             f'<tspan fill="{t["ink"]}">@</tspan><tspan fill="{t["accent"]}">github</tspan></text>'
             f'<text x="{px}" y="{y + LINE}" font-size="13" fill="{t["dim"]}">{"-" * 14}</text></g>')
    y += LINE * 2
    i = 0

    def kv(key, val, y, begin, key_fill):
        pad = " " * (KEY_COL - len(key) - 1)
        return (f'<g opacity="0"><set attributeName="opacity" to="1" begin="{begin:.2f}s" fill="freeze"/>'
                f'<text x="{px}" y="{y}" font-size="13" xml:space="preserve"><tspan fill="{key_fill}" font-weight="700">{esc(key)}</tspan>'
                f'<tspan fill="{t["dim"]}">:{pad}</tspan><tspan fill="{t["ink"]}">{esc(val)}</tspan></text></g>')

    for group in DETAILS:
        for key, val in group:
            s.append(kv(key, val, y, t0 + 0.12 + i * 0.07, t["accent"]))
            y += LINE
            i += 1
        s.append(f'<line x1="{px}" y1="{y - 8}" x2="{W - 36}" y2="{y - 8}" stroke="{t["line"]}" '
                 f'stroke-opacity="0.16" stroke-dasharray="2 4"/>')
        y += 14
    # contact block uses the second accent so it stands out
    for key, val in CONTACT:
        s.append(kv(key, val, y, t0 + 0.12 + i * 0.07, t["accent2"]))
        y += LINE
        i += 1

    # neofetch colour blocks
    yb = y + 4
    bt = t0 + 0.12 + i * 0.07 + 0.1
    blocks = "".join(f'<rect x="{px + k*24}" y="{yb}" width="24" height="12" fill="{c}"/>' for k, c in enumerate(PALETTE[0]))
    blocks += "".join(f'<rect x="{px + k*24}" y="{yb+12}" width="24" height="12" fill="{c}"/>' for k, c in enumerate(PALETTE[1]))
    s.append(f'<g opacity="0" shape-rendering="crispEdges"><set attributeName="opacity" to="1" begin="{bt:.2f}s" fill="freeze"/>{blocks}</g>')

    # fresh prompt with blinking cursor
    yp = H - 22
    s.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{bt + 0.3:.2f}s" fill="freeze"/>'
             f'<text x="24" y="{yp}" font-size="13"><tspan fill="{t["accent"]}" font-weight="700">loganth@github</tspan>'
             f'<tspan fill="{t["ink"]}">:~$</tspan></text>'
             f'<rect x="{24 + 18 * CHAR_W:.0f}" y="{yp - 11}" width="8" height="14" fill="{t["cursor"]}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/></rect></g>')
    s.append('</svg>')
    return "\n".join(s)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--photo", default="assets/profile-cutout.png", help="background-removed portrait (PNG with alpha)")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--cols", type=int, default=58, help="portrait resolution in pixels across")
    args = ap.parse_args()
    rows = portrait_cells(Path(args.photo), args.cols)
    out = Path(args.out_dir)
    for theme, name in (("dark", "loganthp-neofetch.svg"), ("light", "loganthp-neofetch-light.svg")):
        (out / name).write_text(render(theme, rows), encoding="utf-8")
        print("wrote", out / name)


if __name__ == "__main__":
    main()
