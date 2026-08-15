from __future__ import annotations

import argparse
import html
import os
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps


PALETTE = {
    "bg": "#050816",
    "primary": "#00F7FF",
    "secondary": "#2DD4BF",
    "text": "#D7F9FF",
}

# Bright to dense. The left side intentionally starts with visible characters
# so light shirt/background regions do not render as missing chunks.
RAMP = "..::--==++**ccss##%%@@"


def crop_portrait(image: Image.Image) -> Image.Image:
    width, height = image.size
    side = int(width * 0.84)
    left = int((width - side) / 2)
    right = left + side
    top = int(height * 0.16)
    bottom = top + side
    if bottom > height:
        bottom = height
        top = height - side
    return image.crop((left, top, right, bottom))


def image_to_rows(path: Path, width: int, height: int) -> list[str]:
    image = Image.open(path).convert("RGB")
    image = crop_portrait(image)
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.55)
    gray = ImageEnhance.Sharpness(gray).enhance(2.0)

    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.autocontrast(edges)
    edges = ImageEnhance.Contrast(edges).enhance(1.8)
    detail = ImageChops.screen(ImageOps.invert(gray), edges)

    # Characters are taller than they are wide, so resize through a larger
    # grayscale buffer before sampling to preserve face proportions.
    sampled = detail.resize((width, height), Image.Resampling.LANCZOS)
    rows: list[str] = []
    for y in range(height):
        chars = []
        for x in range(width):
            pixel = sampled.getpixel((x, y))
            index = round(pixel / 255 * (len(RAMP) - 1))
            chars.append(RAMP[index])
        rows.append("".join(chars))
    return rows


def write_text_preview(rows: list[str], output: Path) -> None:
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")


def render_svg(rows: list[str], output: Path) -> None:
    static = os.getenv("STATIC") == "1"
    char_w = 5.85
    line_h = 8.25
    pad_x = 214
    pad_y = 38
    portrait_w = len(rows[0]) * char_w
    portrait_h = len(rows) * line_h
    width = 860
    height = 500

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Animated ASCII portrait">',
        f'<rect width="100%" height="100%" rx="10" fill="{PALETTE["bg"]}"/>',
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="10" fill="none" stroke="{PALETTE["primary"]}" stroke-opacity="0.88"/>',
        f'<rect x="8" y="8" width="{width - 16}" height="{height - 16}" rx="8" fill="none" stroke="{PALETTE["secondary"]}" stroke-opacity="0.18"/>',
        '<defs>',
        f'<clipPath id="portrait-wipe"><rect x="{pad_x}" y="{pad_y - line_h}" width="{portrait_w}" height="{portrait_h + line_h}">',
    ]
    if not static:
        lines.append(f'<animate attributeName="width" values="0;{portrait_w};{portrait_w};0" keyTimes="0;0.45;0.82;1" dur="8s" repeatCount="indefinite"/>')
    lines.extend(["</rect></clipPath>", "</defs>"])

    lines.append(f'<g font-family="Consolas, Menlo, monospace" font-size="7.7" fill="{PALETTE["primary"]}" opacity="0.96" clip-path="url(#portrait-wipe)">')
    for i, row in enumerate(rows):
        y = pad_y + i * line_h
        lines.append(f'<text x="{pad_x}" y="{y}">{html.escape(row)}</text>')
    lines.append("</g>")

    if not static:
        lines.append(f'<rect x="{pad_x}" y="{pad_y - 8}" width="9" height="{line_h + 1}" fill="{PALETTE["text"]}" opacity="0.9">')
        lines.append(f'<animate attributeName="x" values="{pad_x};{pad_x + portrait_w};{pad_x + portrait_w};{pad_x}" keyTimes="0;0.45;0.82;1" dur="8s" repeatCount="indefinite"/>')
        lines.append(f'<animate attributeName="y" values="{pad_y - 8};{pad_y + portrait_h - 8};{pad_y + portrait_h - 8};{pad_y - 8}" keyTimes="0;0.45;0.82;1" dur="8s" repeatCount="indefinite"/>')
        lines.append("</rect>")

    lines.append("</svg>")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a prepared portrait as animated ASCII SVG.")
    parser.add_argument("--input", default="assets/profile.jpg")
    parser.add_argument("--output", default="loganthp-ascii.svg")
    parser.add_argument("--preview", default="data/ascii-preview.txt")
    parser.add_argument("--width", type=int, default=74)
    parser.add_argument("--height", type=int, default=52)
    args = parser.parse_args()

    rows = image_to_rows(Path(args.input), args.width, args.height)
    write_text_preview(rows, Path(args.preview))
    render_svg(rows, Path(args.output))


if __name__ == "__main__":
    main()
