from __future__ import annotations

import argparse
import json
import os
from datetime import date, timedelta
from pathlib import Path


PALETTE = {
    "bg": "#050816",
    "primary": "#00F7FF",
    "secondary": "#2DD4BF",
    "text": "#D7F9FF",
}
RAMP = ["#111827", "#073B3A", "#087E8B", "#00AFC1", "#00F7FF", "#69F0FF"]


def load_days(path: Path) -> dict[str, dict[str, object]]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {str(day["date"]): day for day in payload.get("days", [])}


def grid_dates() -> list[list[date]]:
    today = date.today()
    start = today - timedelta(days=370)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    weeks: list[list[date]] = []
    cursor = start
    for _ in range(53):
        week = []
        for _day in range(7):
            week.append(cursor)
            cursor += timedelta(days=1)
        weeks.append(week)
    return weeks


def render(data_path: Path, output: Path) -> None:
    static = os.getenv("STATIC") == "1"
    days = load_days(data_path)
    weeks = grid_dates()
    cell = 11
    gap = 4
    left = 52
    top = 42
    grid_w = 53 * cell + 52 * gap
    grid_h = 7 * cell + 6 * gap
    width = 860
    height = 190
    total = sum(int(day.get("count", 0)) for day in days.values())
    active_days = sum(1 for day in days.values() if int(day.get("count", 0)) > 0)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Loganth GitHub contribution heatmap">',
        f'<rect width="100%" height="100%" rx="12" fill="{PALETTE["bg"]}"/>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="none" stroke="{PALETTE["primary"]}" stroke-opacity="0.35"/>',
        f'<text x="28" y="25" font-family="Consolas, Menlo, monospace" font-size="13" fill="{PALETTE["text"]}">contributions.sh --user LoganthP --year rolling</text>',
        f'<g transform="translate({left},{top})">',
    ]

    for x, week in enumerate(weeks):
        for y, current in enumerate(week):
            item = days.get(current.isoformat(), {})
            level = min(5, int(item.get("level", 0)))
            opacity = "1" if current <= date.today() else "0.25"
            delay = (x + y) * 0.01
            lines.append(
                f'<rect x="{x * (cell + gap)}" y="{y * (cell + gap)}" width="{cell}" height="{cell}" rx="3" fill="{RAMP[level]}" opacity="{opacity}">'
            )
            if not static:
                lines.append(f'<animate attributeName="opacity" from="0" to="{opacity}" dur="0.35s" begin="{delay:.2f}s" fill="freeze"/>')
            lines.append("</rect>")
    lines.append("</g>")

    footer_y = top + grid_h + 35
    lines.append(f'<text x="28" y="{footer_y}" font-family="Consolas, Menlo, monospace" font-size="12" fill="{PALETTE["text"]}" opacity="0.9">{total} contributions | {active_days} active days | generated from public GitHub data</text>')
    legend_x = width - 208
    lines.append(f'<text x="{legend_x}" y="{footer_y}" font-family="Consolas, Menlo, monospace" font-size="11" fill="{PALETTE["text"]}" opacity="0.75">less</text>')
    for i, color in enumerate(RAMP):
        lines.append(f'<rect x="{legend_x + 36 + i * 18}" y="{footer_y - 10}" width="11" height="11" rx="3" fill="{color}"/>')
    lines.append(f'<text x="{legend_x + 154}" y="{footer_y}" font-family="Consolas, Menlo, monospace" font-size="11" fill="{PALETTE["text"]}" opacity="0.75">more</text>')
    lines.append("</svg>")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a GitHub contribution heatmap SVG.")
    parser.add_argument("--input", default="data/contributions.json")
    parser.add_argument("--output", default="loganthp-heatmap.svg")
    args = parser.parse_args()
    render(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()
