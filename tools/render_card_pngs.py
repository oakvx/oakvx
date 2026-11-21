#!/usr/bin/env python3
"""Render missing card PNGs from assets/cards/*.svg.

Existing PNGs are never overwritten: the committed cards carry brand-font
rasterizations (Continuum Bold), which can only be produced locally with the
fonts available there. This tool only renders PNGs for cards that do NOT have
one yet (i.e. newly added cards), with the system fonts standing in for the
brand font, so CI can keep the pipeline from leaving new cards without an
image.

Usage (from repository root):

    python3 tools/render_card_pngs.py
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CARDS_DIR = REPO / "assets" / "cards"
CONFIG = CARDS_DIR / "cards.json"

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def find_fonts():
    found = [f for f in FONT_CANDIDATES if Path(f).is_file()]
    if not found:
        # fall back to a recursive scan for any TTF
        for font_dir in ("/usr/share/fonts", "/usr/local/share/fonts"):
            for f in Path(font_dir).rglob("*.ttf"):
                found.append(str(f))
        found = found[:2]
    if not found:
        return []
    return found


def render_one(card_slug, svg_path, png_path, fonts):
    import resvg_py

    src = svg_path.read_text(encoding="utf-8")
    # swap brand fonts for the system faces: Continuous Bold → DejaVu Bold
    src = src.replace(
        ".title { font-family: 'Continuum Bold', 'Inter', sans-serif; font-size: 40px; font-weight: 400;",
        ".title { font-family: 'DejaVu Sans', sans-serif; font-size: 40px; font-weight: 700;",
    )
    src = src.replace("'Inter', sans-serif", "'DejaVu Sans', sans-serif")
    src = src.replace(".tag { font-size: 12px; font-weight: 500;", ".tag { font-size: 12px; font-weight: 700;")
    src = src.replace(".number { font-size: 13px; font-weight: 600;", ".number { font-size: 13px; font-weight: 700;")
    png = resvg_py.svg_to_bytes(
        svg_string=src,
        width=680,
        height=300,
        skip_system_fonts=True,
        font_files=fonts,
    )
    png_path.write_bytes(png)
    print(f"rendered {png_path.relative_to(REPO)} ({len(png)} bytes)")


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    fonts = find_fonts()
    if not fonts:
        print("no fonts found; cannot render new card PNGs (skipping)", file=sys.stderr)
        return

    rendered = 0
    for card in config.get("cards", []):
        slug = str(card.get("slug", "")).strip()
        if not slug:
            continue
        svg_path = CARDS_DIR / f"{slug}.svg"
        png_path = REPO / "assets" / f"{slug}.png"
        if not svg_path.is_file():
            print(f"skip {slug}: no SVG found", file=sys.stderr)
            continue
        if png_path.is_file():
            continue  # committed, brand-font PNG: never overwrite
        render_one(slug, svg_path, png_path, fonts)
        rendered += 1
    if rendered == 0:
        print("all card PNGs already exist; nothing to render")


if __name__ == "__main__":
    main()
