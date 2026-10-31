"""Generate light-mode copies of the profile README artwork.

Every original (dark) asset is left untouched. For each one a sibling file
with a ``-light`` suffix is written, and README.md switches between the two
with ``<picture>`` + ``prefers-color-scheme`` so GitHub shows the right one
for the viewer's theme.

Run from the repository root:

    python scripts/make_light_variants.py              # everything
    python scripts/make_light_variants.py --skip-jet   # offline (no fetch)

The script is idempotent: re-running it simply rewrites the *-light files.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

JET_SOURCE_URL = "https://raw.githubusercontent.com/LoganthP/JetCommit/main/dist/github-jet.svg"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def swap_colors(text: str, mapping: dict[str, str]) -> str:
    """Replace hex colours case-insensitively in a single pass.

    A single regex pass means a colour that is produced by one rule can never
    be re-mapped by another rule (no A->B->C chains).
    """
    lookup = {k.lower(): v for k, v in mapping.items()}
    pattern = re.compile("|".join(re.escape(k) for k in lookup), re.IGNORECASE)
    return pattern.sub(lambda m: lookup[m.group(0).lower()], text)


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)}")


# --------------------------------------------------------------------------
# 1. LOGANTH chromatic name banner
# --------------------------------------------------------------------------

CHROMATIC_MAP = {
    "#0A0E1A": "#F6F9FC",  # banner background -> soft paper white
    "#EAF1FA": "#0F172A",  # letter blocks (rest colour) -> deep slate
    "#FFFFFF": "#0B1220",  # flicker frame + block outline
    "#BFEFFF": "#0E7490",  # flicker frame -> deep teal
    "#80F7FF": "#0891B2",  # flicker frame -> teal
    "#FFE08A": "#B45309",  # flicker frame -> burnt amber
    "#B9C6D6": "#475569",  # inner block grid lines
    "#8CFBFF": "#06B6D4",  # block glow
    "#22D3EE": "#0891B2",  # frame / sweep accents
    "#38E1F5": "#0891B2",  # chromatic offset outline (cyan)
    "#F5A524": "#D97706",  # chromatic offset outline (amber)
    "#F472B6": "#DB2777",  # spark
}


def make_chromatic() -> None:
    src = ROOT / "loganth-chromatic.svg"
    text = swap_colors(src.read_text(encoding="utf-8"), CHROMATIC_MAP)
    # Glow filters hard-code their colour in a colour matrix; retint them to
    # teal and soften them a little so they read as a glow on white paper.
    text = text.replace(
        'values="0 0 0 0 0.133 0 0 0 0 0.827 0 0 0 0 0.933 0 0 0 0.6 0"',
        'values="0 0 0 0 0.031 0 0 0 0 0.569 0 0 0 0 0.698 0 0 0 0.45 0"',
    )
    text = text.replace(
        'values="0 0 0 0 0.40 0 0 0 0 0.95 0 0 0 0 1 0 0 0 1.35 0"',
        'values="0 0 0 0 0.024 0 0 0 0 0.714 0 0 0 0 0.831 0 0 0 0.9 0"',
    )
    write(ROOT / "loganth-chromatic-light.svg", text)


# --------------------------------------------------------------------------
# 2. Cyberpunk ASCII portrait + info card
# --------------------------------------------------------------------------
# The portrait lives inside its own terminal window. ASCII art encodes the
# photo through character density, so it only reads correctly as light text
# on a dark screen; that terminal window is kept exactly as it is (a dark
# terminal inside a light card looks intentional). Everything around it --
# the outer card and the info panel -- is recoloured for light mode.

ASCII_FRAME_MAP = {
    "#050816": "#F6F8FA",  # outer card
    "#00F7FF": "#0891B2",  # border + divider
    "#FF007F": "#DB2777",  # inner pink border
}

ASCII_PANEL_MAP = {
    "#0b1021": "#FFFFFF",  # info panel background
    "#00F7FF": "#0E7490",  # labels, borders, row lines
    "#E6EDF3": "#1F2328",  # values
    "#D7F9FF": "#1F2328",  # title bar text
}

LEFT_PANEL_START = '<g clip-path="url(#left-panel-clip)">'
RIGHT_PANEL_START = '<g transform="translate(243.4 8.0)">'


def make_ascii_card() -> None:
    src = ROOT / "loganthp-ascii_cyberpunk.svg"
    text = src.read_text(encoding="utf-8")
    left = text.find(LEFT_PANEL_START)
    right = text.find(RIGHT_PANEL_START)
    if left == -1 or right == -1 or right < left:
        print("  ! ascii card layout changed; skipping (update markers in script)")
        return
    head, portrait, panel = text[:left], text[left:right], text[right:]
    head = swap_colors(head, ASCII_FRAME_MAP)
    # Make the outer border a little stronger / divider softer on white.
    head = head.replace('stroke-opacity="0.60" stroke-width="1.2"', 'stroke-opacity="0.45" stroke-width="1.2"')
    # Softer drop shadow under the terminal window on a light card.
    portrait = portrait.replace('flood-color="#000000" flood-opacity="0.45"', 'flood-color="#0F172A" flood-opacity="0.25"')
    panel = swap_colors(panel, ASCII_PANEL_MAP)
    panel = panel.replace('stroke-opacity="0.10"', 'stroke-opacity="0.16"')
    panel = panel.replace('fill-opacity="0.10"', 'fill-opacity="0.08"')
    write(ROOT / "loganthp-ascii_cyberpunk-light.svg", head + portrait + panel)


# --------------------------------------------------------------------------
# 3. Footer wave
# --------------------------------------------------------------------------

FOOTER_MAP = {
    "#050816": "#F6F8FA",  # background
    "#1F4068": "#CDEFF7",  # back wave
    "#00F7FF": "#0891B2",  # front wave + stars
    "#FFFFFF": "#0F172A",  # tagline
}


def make_footer() -> None:
    src = ROOT / "assets" / "footer.svg"
    text = swap_colors(src.read_text(encoding="utf-8"), FOOTER_MAP)
    text = text.replace('fill-opacity="0.18"', 'fill-opacity="0.22"')
    write(ROOT / "assets" / "footer-light.svg", text)


# --------------------------------------------------------------------------
# 4. AI & RAG tech logos (match skillicons.dev light tiles)
# --------------------------------------------------------------------------

TILE_LIGHT = "#F4F2ED"   # same tile colour skillicons uses with theme=light
INK = "#1F2328"

LOGO_MAPS: dict[str, dict[str, str]] = {
    "rag": {
        "#202638": TILE_LIGHT,
        "#F8FAFC": "#FFFFFF",
        "#70E3FF": "#22B8DC",
        "#FFD45A": "#E0A100",
    },
    "faiss": {
        "#202638": TILE_LIGHT,
        "#F8FAFC": INK,
        "#FFB4CC": "#F06292",
        "#FF4F86": "#E91E63",
    },
    "langchain": {
        "#202638": TILE_LIGHT,
        "#D9E2EA": "#64748B",
        "#AAB7C4": "#475569",
        "#F8FAFC": INK,
        "#D8DDE5": "#64748B",
    },
    "chromadb": {
        "#202638": TILE_LIGHT,
        "#F8FAFC": INK,
    },
}


def make_logos() -> None:
    folder = ROOT / "assets" / "tech-logos"
    for name, mapping in LOGO_MAPS.items():
        src = folder / f"{name}.svg"
        text = swap_colors(src.read_text(encoding="utf-8"), mapping)
        if name == "rag":
            # Give the white page an outline so it doesn't vanish on the tile,
            # and keep the check-mark dark on the cyan badge.
            text = text.replace(
                '<rect x="11" y="9" width="18" height="22" rx="3" fill="#FFFFFF"/>',
                '<rect x="11" y="9" width="18" height="22" rx="3" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1"/>',
            )
            text = text.replace(
                f'font-weight="800" fill="#FFFFFF">RAG',
                f'font-weight="800" fill="{INK}">RAG',
            )
            text = text.replace('stroke="#F4F2ED" stroke-width="1.7"', 'stroke="#0F172A" stroke-width="1.7"')
        write(folder / f"{name}-light.svg", text)
    make_n8n_png(folder)


def make_n8n_png(folder: Path) -> None:
    try:
        from PIL import Image
    except ImportError:  # pragma: no cover
        print("  ! Pillow not installed; skipping n8n-light.png")
        return
    src = Image.open(folder / "n8n.png").convert("RGBA")
    light_bg = (244, 242, 237)
    out = Image.new("RGBA", src.size)
    px_in, px_out = src.load(), out.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = px_in[x, y]
            # How "logo-pink" this pixel is (0 = tile background, 1 = logo).
            pink = max(0.0, min(1.0, (r - max(g, b) - 10) / 140))
            # Tile background is a dark navy gradient; flip its lightness so
            # the gentle gradient survives on the light tile.
            lum = (r + g + b) / 3
            bg = tuple(max(0, min(255, int(c - (lum - 30) * 0.6))) for c in light_bg)
            nr, ng, nb = (int(pink * c_logo + (1 - pink) * c_bg) for c_logo, c_bg in zip((r, g, b), bg))
            px_out[x, y] = (nr, ng, nb, a)
    out.save(folder / "n8n-light.png")
    print(f"  wrote {(folder / 'n8n-light.png').relative_to(ROOT)}")


# --------------------------------------------------------------------------
# 5. JetCommit heatmap (lives in the LoganthP/JetCommit repo)
# --------------------------------------------------------------------------

JET_MAP = {
    "#0d1117": "#FFFFFF",  # background (GitHub dark canvas -> light canvas)
    "#03001c": "#F6F8FA",  # cells the jet has already cleared
    "#8b949e": "#8C959F",  # twinkling stars
}


def make_jet() -> None:
    target = ROOT / "jetcommit-light.svg"
    try:
        with urllib.request.urlopen(JET_SOURCE_URL, timeout=30) as resp:
            text = resp.read().decode("utf-8")
    except Exception as exc:  # network hiccup: keep the last good copy
        print(f"  ! could not fetch JetCommit SVG ({exc}); keeping existing {target.name}")
        return
    if "<svg" not in text:
        print("  ! JetCommit response is not an SVG; keeping existing file")
        return
    write(target, swap_colors(text, JET_MAP))


# --------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skip-jet", action="store_true", help="don't fetch the JetCommit heatmap")
    args = parser.parse_args()

    print("Generating light-mode variants")
    make_chromatic()
    make_ascii_card()
    make_footer()
    make_logos()
    if not args.skip_jet:
        make_jet()
    return 0


if __name__ == "__main__":
    sys.exit(main())
