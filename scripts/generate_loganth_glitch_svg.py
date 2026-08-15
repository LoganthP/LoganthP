from __future__ import annotations

import html
import random
from pathlib import Path


WORD = "LOGANTH"
SEED = 190719
VIEWBOX_WIDTH = 860
VIEWBOX_HEIGHT = 220

BG = "#000000"
CARD = "#0A0E1A"
BORDER = "#22D3EE"
BRICK = "#F5F7FA"
BRICK_STROKE = "#CBD5E1"
CYAN = "#22D3EE"
MAGENTA = "#F472B6"

CELL = 14
PITCH_X = 17
PITCH_Y = 17
GLYPH_COLS = 6
GLYPH_ROWS = 8
LETTER_GAP = 14
TEXT_X = 31
TEXT_Y = 42

FONT = {
    "L": [
        "100000",
        "100000",
        "100000",
        "100000",
        "100000",
        "100000",
        "100000",
        "111111",
    ],
    "O": [
        "011110",
        "100001",
        "100001",
        "100001",
        "100001",
        "100001",
        "100001",
        "011110",
    ],
    "G": [
        "011110",
        "100001",
        "100000",
        "100000",
        "100111",
        "100001",
        "100001",
        "011110",
    ],
    "A": [
        "001100",
        "010010",
        "100001",
        "100001",
        "111111",
        "100001",
        "100001",
        "100001",
    ],
    "N": [
        "100001",
        "110001",
        "101001",
        "100101",
        "100101",
        "100011",
        "100001",
        "100001",
    ],
    "T": [
        "111111",
        "001100",
        "001100",
        "001100",
        "001100",
        "001100",
        "001100",
        "001100",
    ],
    "H": [
        "100001",
        "100001",
        "100001",
        "100001",
        "111111",
        "100001",
        "100001",
        "100001",
    ],
}


def attrs(**items: object) -> str:
    parts = []
    for key, value in items.items():
        if value is None:
            continue
        name = key.rstrip("_").replace("_", "-")
        parts.append(f'{name}="{html.escape(str(value), quote=True)}"')
    return " ".join(parts)


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def iter_cells(rng: random.Random):
    glyph_step = GLYPH_COLS * PITCH_X + LETTER_GAP
    for glyph_index, char in enumerate(WORD):
        glyph_x = TEXT_X + glyph_index * glyph_step
        for row, bits in enumerate(FONT[char]):
            for col, bit in enumerate(bits):
                if bit != "1":
                    continue

                w = CELL * rng.uniform(0.92, 1.1)
                h = CELL * rng.uniform(0.91, 1.09)
                x = glyph_x + col * PITCH_X + rng.uniform(-1.0, 1.0)
                y = TEXT_Y + row * PITCH_Y + rng.uniform(-1.0, 1.0)
                rx = rng.uniform(1.0, 2.8)
                flicker = rng.random() < 0.5
                jitter = rng.random() < 0.34
                yield {
                    "char": char,
                    "glyph_index": glyph_index,
                    "row": row,
                    "col": col,
                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h,
                    "rx": rx,
                    "flicker": flicker,
                    "jitter": jitter,
                    "flicker_dur": rng.uniform(2.55, 3.95),
                    "flicker_begin": rng.uniform(0.0, 3.7),
                    "jitter_dur": rng.uniform(2.7, 4.0),
                    "jitter_begin": rng.uniform(0.05, 3.6),
                    "jitter_shift": rng.choice([-2, -1.5, -1, 1, 1.5, 2]),
                }


def rect_with_animation(cell: dict[str, object], suffix: str = "") -> str:
    rect_id = (
        f'cell-{cell["char"]}{cell["glyph_index"]}-r{cell["row"]}c{cell["col"]}{suffix}'
    )
    rect = [
        "      <rect "
        + attrs(
            id=rect_id,
            x=fmt(cell["x"]),
            y=fmt(cell["y"]),
            width=fmt(cell["w"]),
            height=fmt(cell["h"]),
            rx=fmt(cell["rx"]),
            ry=fmt(cell["rx"]),
            fill=BRICK,
            stroke=BRICK_STROKE,
            stroke_width=1,
        )
        + ">"
    ]
    if cell["flicker"]:
        rect.append(
            "        <animate "
            + attrs(
                attributeName="opacity",
                values="1;1;0.28;1;0.04;1;1",
                keyTimes="0;0.42;0.46;0.5;0.56;0.6;1",
                dur=f'{fmt(cell["flicker_dur"])}s',
                begin=f'{fmt(cell["flicker_begin"])}s',
                repeatCount="indefinite",
            )
            + " />"
        )
    if cell["jitter"]:
        shift = fmt(cell["jitter_shift"])
        rect.append(
            "        <animateTransform "
            + attrs(
                attributeName="transform",
                type="translate",
                values=f"0 0;0 0;{shift} 0;0 0;{-float(shift)} 0;0 0",
                keyTimes="0;0.61;0.64;0.68;0.74;1",
                dur=f'{fmt(cell["jitter_dur"])}s',
                begin=f'{fmt(cell["jitter_begin"])}s',
                repeatCount="indefinite",
                additive="sum",
            )
            + " />"
        )
    rect.append("      </rect>")
    return "\n".join(rect)


def channel_rect(cell: dict[str, object], color: str, opacity: float, dx: float, dy: float) -> str:
    return (
        "      <rect "
        + attrs(
            x=fmt(float(cell["x"]) + dx),
            y=fmt(float(cell["y"]) + dy),
            width=fmt(cell["w"]),
            height=fmt(cell["h"]),
            rx=fmt(cell["rx"]),
            ry=fmt(cell["rx"]),
            fill=color,
            opacity=opacity,
        )
        + " />"
    )


def build_svg() -> str:
    rng = random.Random(SEED)
    cells = list(iter_cells(rng))
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" '
        + attrs(viewBox=f"0 0 {VIEWBOX_WIDTH} {VIEWBOX_HEIGHT}", width=VIEWBOX_WIDTH, height=VIEWBOX_HEIGHT, role="img")
        + ">",
        "  <title>LOGANTH blocky glitch pixel-brick animation</title>",
        "  <desc>Hand-authored bitmap glyphs rendered as individually jittered animated rect cells.</desc>",
        f'  <rect width="{VIEWBOX_WIDTH}" height="{VIEWBOX_HEIGHT}" fill="{BG}" />',
        "  <rect "
        + attrs(x=1, y=1, width=VIEWBOX_WIDTH - 2, height=VIEWBOX_HEIGHT - 2, rx=18, ry=18, fill=CARD, stroke=BORDER, stroke_width=1.5)
        + " />",
        '  <g id="word-rgb-split" aria-hidden="true">',
        f'    <g id="glyph-cyan-offset" opacity="0.12">',
        '      <animate attributeName="opacity" values="0.04;0.14;0.04;0.18;0.05" keyTimes="0;0.2;0.56;0.62;1" dur="3.4s" begin="0.18s" repeatCount="indefinite" />',
        '      <animateTransform attributeName="transform" type="translate" values="1 0;1 0;2 0;1 0;0 0;1 0" keyTimes="0;0.36;0.4;0.45;0.72;1" dur="3.4s" begin="0.18s" repeatCount="indefinite" additive="sum" />',
    ]
    for cell in cells:
        lines.append(channel_rect(cell, CYAN, 0.72, 1.2, 0.0))
    lines.extend(
        [
            "    </g>",
            f'    <g id="glyph-magenta-offset" opacity="0.1">',
            '      <animate attributeName="opacity" values="0.02;0.12;0.03;0.15;0.04" keyTimes="0;0.3;0.5;0.66;1" dur="3.1s" begin="0.73s" repeatCount="indefinite" />',
            '      <animateTransform attributeName="transform" type="translate" values="-1 0;-1 0;-2 0;-1 0;0 0;-1 0" keyTimes="0;0.26;0.31;0.36;0.78;1" dur="3.1s" begin="0.73s" repeatCount="indefinite" additive="sum" />',
        ]
    )
    for cell in cells:
        lines.append(channel_rect(cell, MAGENTA, 0.68, -1.2, 0.0))
    lines.extend(["    </g>", "  </g>", '  <g id="word-base">'])

    glyph_step = GLYPH_COLS * PITCH_X + LETTER_GAP
    for glyph_index, char in enumerate(WORD):
        lines.append(f'    <g id="glyph-{char}" data-char="{char}">')
        glyph_cells = [cell for cell in cells if cell["glyph_index"] == glyph_index]
        for cell in glyph_cells:
            lines.append(rect_with_animation(cell))
        lines.append("    </g>")

    lines.extend(
        [
            "  </g>",
            "  <rect "
            + attrs(id="status-cursor", x=824, y=184, width=14, height=14, rx=1.5, ry=1.5, fill=BORDER)
            + ">",
            '    <animate attributeName="opacity" values="1;1;0.16;0.16;1" keyTimes="0;0.48;0.5;0.82;0.84" dur="1.25s" repeatCount="indefinite" />',
            "  </rect>",
            "</svg>",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    output = Path(__file__).resolve().parents[1] / "loganth-glitch.svg"
    output.write_text(build_svg(), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
