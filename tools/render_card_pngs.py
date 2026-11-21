#!/usr/bin/env python3
"""Render card PNGs from assets/cards/*.svg with the Continuum (Wii) font.

The brand cards use 'Continuum Bold' for titles. At build time this tool
first fetches contb.ttf from fontmeme.com (see tools/fonts.py) and renders
each card with it, so the PNGs actually carry the brand font instead of a
system stand-in.

Behaviour:
    python3 tools/render_card_pngs.py --missing   # only cards with no PNG yet (safe default)
    python3 tools/render_card_pngs.py --all       # re-render every card PNG
                                                 # (brand-font titles;
                                                 #   falls back to DejaVu + warning if
                                                 #   the brand font could not be fetched)
    python3 tools/render_card_pngs.py --force      # re-render every card PNG,
                                                 #   overwriting committed PNGs

The downloaded font never leaves the build: it lives in .cache/fonts/ (gitignored)
and is never committed.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CARDS_DIR = REPO / "assets" / "cards"
CONFIG = CARDS_DIR / "cards.json"

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/dejavu",
]

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def find_system_fonts():
    found = [f for f in FONT_CANDIDATES if Path(f).is_file()]
    if found:
        return found
    for font_dir in FONT_DIRS:
        if Path(font_dir).is_dir():
            for f in Path(font_dir).glob("*.ttf"):
                found.append(str(f))
            if found:
                return found
    return found


def load_continuum():
    try:
        sys.path.insert(0, str(REPO / "tools"))
        from fonts import ensure_continuum
    except ImportError as e:
        print(f"cannot import tools/fonts.py: {e}", file=sys.stderr)
        return None, None
    font_path, family = ensure_continuum()
    if font_path and family:
        return font_path, family
    return None, None


def render_card(card, svg_path, png_path, fonts, brand, brand_family):
    import resvg_py

    src = svg_path.read_text(encoding="utf-8")
    title_family = brand_family if brand else "DejaVu Sans"
    # Medium/Light carry the 400 weight themselves; only bump to 700 for
    # bold-faced brand fonts (e.g. contb.ttf)
    if brand_family and re.search(r"(medium|light|regular|light)", brand_family, re.I):
        title_weight = 400
    else:
        title_weight = 700

    # swap brand fonts for the render copy
    src = src.replace(
        ".title { font-family: 'Continuum Bold', 'Inter', sans-serif; font-size: 40px; font-weight: 400;",
        f".title {{ font-family: '{title_family}', sans-serif; font-size: 40px; font-weight: {title_weight};",
    )
    src = src.replace("'Inter', sans-serif", "'DejaVu Sans', sans-serif")
    src = src.replace(".tag { font-size: 12px; font-weight: 500;", ".tag { font-size: 12px; font-weight: 700;")
    src = src.replace(".number { font-size: 13px; font-weight: 600;", ".number { font-size: 13px; font-weight: 700;")
    if brand_family:
        # title + brand font load; body fonts stay system
        font_files = list(fonts) + [brand]
    else:
        font_files = list(fonts)

    png = resvg_py.svg_to_bytes(
        svg_string=src,
        width=680,
        height=300,
        skip_system_fonts=True,
        font_files=font_files,
    )
    png_path.write_bytes(png)
    return len(png)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--missing", action="store_true",
                      help="render PNGs only for cards without one (safe default)")
    mode.add_argument("--all", action="store_true",
                      help="re-render every card (falls back to system fonts if Continuum is unavailable)")
    mode.add_argument("--force", action="store_true",
                      help="re-render every card, overwriting brand-font PNGs")
    args = parser.parse_args()

    mode_all = args.all or args.force

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    system_fonts = find_system_fonts()
    if not system_fonts:
        print("no system fonts found; cannot render card PNGs", file=sys.stderr)
        return 1

    brand_path, brand_family = load_continuum()
    brand_available = bool(brand_path and brand_family)

    if brand_available:
        print(f"using continuum font: {brand_path} (family={brand_family!r})")
    else:
        print("WARNING: Continuum font could not be fetched from fontmeme.com - "
              "using system DejaVu fonts instead.", file=sys.stderr)

    rendered = skipped = 0
    for card in config.get("cards", []):
        slug = str(card.get("slug", "")).strip()
        if not slug:
            continue
        svg_path = CARDS_DIR / f"{slug}.svg"
        png_path = REPO / "assets" / f"{slug}.png"
        if not svg_path.is_file():
            print(f"skip {slug}: no SVG found", file=sys.stderr)
            continue
        exists = png_path.is_file()

        if not exists:
            # brand-new card: render now, best-effort (system fonts stand in
            # for the brand font until the font lands)
            size = render_card(card, svg_path, png_path, system_fonts, brand_path, brand_family)
            print(f"rendered {png_path.relative_to(REPO)} ({size} bytes)")
            rendered += 1
            continue

        if not mode_all:
            skipped += 1  # committed brand-font PNG: keep as-is
            continue

        if not brand_available and args.all:
            # never downgrade a committed brand-font PNG to DejaVu stand-ins
            print(f"skip {slug}: committed PNG exists and brand font unavailable", file=sys.stderr)
            skipped += 1
            continue

        size = render_card(card, svg_path, png_path, system_fonts, brand_path, brand_family)
        print(f"rendered {png_path.relative_to(REPO)} ({size} bytes)")
        rendered += 1

    if rendered == 0 and skipped == 0:
        print("nothing to render")
    elif rendered:
        print(f"rendered {rendered} card PNG(s); kept (already exist): {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
