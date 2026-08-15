from __future__ import annotations

import html
import os
from pathlib import Path


PALETTE = {
    "bg": "#050816",
    "primary": "#00F7FF",
    "secondary": "#2DD4BF",
    "text": "#F8FBFF",
    "blue": "#2B7CFF",
    "red": "#FF3B6B",
}

GLYPHS = str.maketrans(
    {
        "#": "\u2588",
        "<": "\u2554",
        ">": "\u2557",
        "|": "\u2551",
        "=": "\u2550",
        "\\": "\u255a",
        "/": "\u255d",
    }
)

RAW_LOGANTH = [
    "##>      ######>  ######>  #####> ###>   ##>########>##>  ##>",
    "##|     ##<===##>##<====/ ##<==##>####>  ##|\\==##<==/##|  ##|",
    "##|     ##|   ##|##|  ###>#######|##<##> ##|   ##|   #######|",
    "##|     ##|   ##|##|   ##|##<==##|##|\\##>##|   ##|   ##<==##|",
    "#######>\\######</\\######</##|  ##|##| \\####|   ##|   ##|  ##|",
    "\\======/ \\=====/  \\=====/ \\=/  \\=/\\=/  \\===/   \\=/   \\=/  \\=/",
]

LOGANTH = [row.translate(GLYPHS) for row in RAW_LOGANTH]


def add_text_layer(
    lines: list[str],
    *,
    x: int,
    y: int,
    fill: str,
    opacity: str,
    transform: str = "",
    glitch: bool = False,
    begin: str = "0s",
) -> None:
    transform_attr = f' transform="{transform}"' if transform else ""
    lines.append(
        f'<g{transform_attr} font-family="Consolas, Cascadia Mono, Courier New, monospace" '
        f'font-size="16" font-weight="700" fill="{fill}" opacity="{opacity}" xml:space="preserve">'
    )
    if glitch:
        lines.append(
            f'<animate attributeName="opacity" values="0;0.48;0;0.26;0;0" '
            f'keyTimes="0;0.04;0.08;0.13;0.18;1" dur="1.15s" begin="{begin}" repeatCount="indefinite"/>'
        )
    for index, row in enumerate(LOGANTH):
        lines.append(f'<text x="{x}" y="{y + index * 20}">{html.escape(row)}</text>')
    lines.append("</g>")


def main() -> None:
    static = os.getenv("STATIC") == "1"
    width = 860
    height = 190
    x = 118
    y = 55
    reveal_x = 104
    reveal_y = 34
    reveal_w = 660

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="LOGANTH ANSI shadow name banner">',
        f'<rect width="100%" height="100%" rx="10" fill="{PALETTE["bg"]}"/>',
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="10" fill="none" stroke="{PALETTE["primary"]}" stroke-opacity="0.88"/>',
        f'<rect x="12" y="12" width="{width - 24}" height="{height - 24}" rx="8" fill="#0B1220" opacity="0.88" stroke="{PALETTE["secondary"]}" stroke-opacity="0.22"/>',
        "<defs>",
        f'<clipPath id="name-reveal"><rect x="{reveal_x}" y="{reveal_y}" width="{reveal_w}" height="130">',
    ]
    if not static:
        lines.append(
            f'<animate attributeName="width" values="0;{reveal_w};{reveal_w};0" '
            f'keyTimes="0;0.36;0.88;1" dur="6s" repeatCount="indefinite"/>'
        )
    lines.extend(
        [
            "</rect></clipPath>",
            '<filter id="ansi-glow" x="-5%" y="-24%" width="110%" height="148%">',
            '<feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="#00F7FF" flood-opacity="0.28"/>',
            "</filter>",
            "</defs>",
            '<g clip-path="url(#name-reveal)" filter="url(#ansi-glow)">',
        ]
    )

    if not static:
        add_text_layer(lines, x=x - 3, y=y, fill=PALETTE["blue"], opacity="0", transform="translate(-2 0)", glitch=True)
        add_text_layer(lines, x=x + 3, y=y, fill=PALETTE["red"], opacity="0", transform="translate(2 0)", glitch=True, begin="0.06s")

    add_text_layer(lines, x=x, y=y, fill=PALETTE["text"], opacity="1")
    lines.append("</g>")

    lines.append(f'<rect x="{reveal_x}" y="166" width="10" height="12" fill="{PALETTE["primary"]}" opacity="0.85">')
    if not static:
        lines.append(
            f'<animate attributeName="x" values="{reveal_x};{reveal_x + reveal_w - 10};{reveal_x + reveal_w - 10};{reveal_x}" '
            f'keyTimes="0;0.36;0.88;1" dur="6s" repeatCount="indefinite"/>'
        )
        lines.append('<animate attributeName="opacity" values="0.9;0.9;0.15;0.9" dur="0.8s" repeatCount="indefinite"/>')
    lines.append("</rect>")
    lines.append("</svg>")

    Path("loganthp-name.svg").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
