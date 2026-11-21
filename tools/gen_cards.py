#!/usr/bin/env python3
"""Regenerate the project-card SVGs in assets/cards/ from assets/cards/cards.json.

Each entry describes one card (number, title, description, pill chips, accent,
illustration markup). The generator renders the same fixed layout used by the
existing cards (background, card shell, pill row, glowing cyan panel, concentric
circles, line-art illustration, "A Open" mark), so the output stays byte-for-byte
compatible with the hand-authored reference cards.

Run from the repository root:

    python3 tools/gen_cards.py

It rewrites every assets/cards/<slug>.svg from the config. Illustrations are
kept verbatim in the config (with @@ACCENT@@ as the accent placeholder) so a
card can be re-skinned by changing one hex value.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CARDS_DIR = REPO / "assets" / "cards"
CONFIG = CARDS_DIR / "cards.json"

HEADER = '''<svg xmlns="http://www.w3.org/2000/svg" width="680" height="300" viewBox="0 0 680 300">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#f8fafa"/><stop offset="1" stop-color="#f0f4f4"/></linearGradient>
    <linearGradient id="card" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#ffffff"/><stop offset="1" stop-color="#f8fafa"/></linearGradient>
    <pattern id="dots" width="34" height="28" patternUnits="userSpaceOnUse"><circle cx="10" cy="12" r="0.75" fill="#d8e0e1" fill-opacity="0.52"/></pattern>
    <filter id="shadow" x="-20%" y="-30%" width="140%" height="170%"><feDropShadow dx="0" dy="7" stdDeviation="7" flood-color="#8da3a9" flood-opacity="0.24"/></filter>
    <filter id="tileShadow" x="-35%" y="-35%" width="170%" height="180%"><feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="#68848c" flood-opacity="0.22"/></filter>
    <filter id="glow" x="-70%" y="-70%" width="240%" height="240%"><feGaussianBlur stdDeviation="6"/></filter>
    <style>
      text { font-family: 'Inter', sans-serif; }
      .number { font-size: 13px; font-weight: 600; fill: #7a8589; letter-spacing: .1px; }
      .title { font-family: 'Continuum Bold', 'Inter', sans-serif; font-size: {title_size}; font-weight: 400; fill: #3e4447; letter-spacing: -.55px; }
      .description { font-size: 16px; font-weight: 400; fill: #6d787c; letter-spacing: -.12px; }
      .tag { font-size: 12px; font-weight: 500; fill: #626e72; }
      .open { font-size: 13px; font-weight: 400; fill: #7b868a; }
      .key { font-size: 10px; font-weight: 600; fill: #20a9c4; }
    </style>
  </defs>'''

BODY_TOP = '''  <rect width="680" height="300" fill="url(#bg)"/>
  <rect width="680" height="300" fill="url(#dots)"/>
  <rect x="24" y="22" width="632" height="254" rx="25" fill="url(#card)" stroke="#dce3e4" filter="url(#shadow)"/>'''

BODY_BOTTOM = '''  <rect x="474" y="59" width="152" height="152" rx="28" fill="none" stroke="#16c2e3" stroke-width="9" opacity=".48" filter="url(#glow)"/>
  <g filter="url(#tileShadow)"><rect x="475" y="60" width="150" height="150" rx="27" fill="#fbfcfc" stroke="#16bad8" stroke-width="4"/></g>
  <rect x="481" y="66" width="138" height="138" rx="22" fill="none" stroke="#c2edf3"/>
  <circle cx="550" cy="135" r="50" fill="#f7f9f9" stroke="#e3e9ea"/>
  <circle cx="550" cy="135" r="44" fill="none" stroke="#edf1f1"/>
  <g transform="translate(550 135)"><g fill="none" stroke="#{accent}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
{illustration}
    </g></g>
  <circle cx="566" cy="232" r="11" fill="#f8fbfb" stroke="#c5d5d8"/>
  <text x="566" y="236" class="key" text-anchor="middle">A</text>
  <text x="587" y="238" class="open">Open</text>
</svg>'''


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def description_svg(lines):
    out = []
    for i, d in enumerate(lines):
        y = 169 + i * 24
        # line 1 is indented two spaces; later lines (if any) are at column 0
        indent = "  " if i == 0 else ""
        out.append(f'{indent}<text x="58" y="{y}" class="description">{esc(d)}</text>')
    return "\n".join(out)


def pills_svg(pills):
    out = []
    for i, p in enumerate(pills):
        if i == 0:
            out.append(f'  <rect x="{p["x"]}" y="216" width="{p["width"]}" height="31" rx="15.5" fill="#fbfcfc" stroke="#d8dfe1"/>')
        text = f'      <text x="{p["cx"]}" y="236" class="tag" text-anchor="middle">{esc(p["label"])}</text>'
        if i + 1 < len(pills):
            nxt = pills[i + 1]
            out.append(f'{text}<rect x="{nxt["x"]}" y="216" width="{nxt["width"]}" height="31" rx="15.5" fill="#fbfcfc" stroke="#d8dfe1"/>')
        else:
            out.append(text)
    return "\n".join(out)


def render_card(card):
    accent = card["accent"].lstrip("#")
    illustration = card["illustration"].replace("@@ACCENT@@", accent)
    return (
        HEADER.replace("{title_size}", card["title_size"])
        + "\n"
        + BODY_TOP
        + f'\n  <text x="58" y="66" class="number">{esc(card["number"])}</text>'
        + f'\n  <text x="58" y="132" class="title">{esc(card["title"])}</text>'
        + "\n"
        + description_svg(card["description"])
        + "\n"
        + pills_svg(card["pills"])
        + "\n"
        + BODY_BOTTOM.replace("{accent}", accent).replace("{illustration}", illustration)
    )


def auto_pills(labels):
    """Derive pill geometry (x, width, cx) for string-list pills.

    width ≈ len * 7.2 + 34, clamped to a readable minimum (46px) and maximum (160px).
    Pills start at x=58 with 10px spacing, centred so long labels wrap nowhere.
    """
    x = 58
    pills = []
    for label in labels:
        w = int(round(len(str(label)) * 7.2 + 34))
        w = max(46, min(160, w))
        pills.append({"label": str(label), "x": str(x), "width": str(w),
                      "cx": f"{x + w / 2:.1f}".rstrip(".0").rstrip(".")})
        x += w + 10
    return pills


def normalize_pills(card):
    """Return pills in the explicit {label,x,width,cx} shape used by the SVG writer."""
    raw = card["pills"]
    if not raw:
        raise ValueError("at least one pill is required")
    out = []
    for item in raw:
        if isinstance(item, str):
            raise ValueError("pills as plain strings are not supported directly; use the auto-size form at the config level")
        if isinstance(item, dict):
            label = str(item.get("label", "")).strip()
            if not label:
                raise ValueError("pill is missing a label")
            try:
                x = int(item["x"])
                width = int(item["width"])
                cx = item.get("cx")
                cx = f"{x + width / 2:.1f}".rstrip(".0").rstrip(".") if cx is None else str(cx)
            except (KeyError, ValueError, TypeError) as e:
                raise ValueError(f"pill '{label}': invalid x/width ({e})")
            out.append({"label": label, "x": str(x), "width": str(width), "cx": cx})
            continue
        raise ValueError(f"pill must be a string or an object with label/x/width, got: {item!r}")
    return out


def normalize_card(card):
    if not isinstance(card, dict):
        raise SystemExit("each card in cards.json must be an object")
    slug = str(card.get("slug", "")).strip()
    if not slug or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise SystemExit(f"card '{slug or '?'}': slug must be lowercase letters, digits and dashes")
    title = str(card.get("title", "")).strip()
    if not title:
        raise SystemExit(f"card '{slug}': missing title")
    number = str(card.get("number", "")).strip()
    if not re.fullmatch(r"[0-9]{1,2}", number):
        raise SystemExit(f"card '{slug}': number must be 1-2 digits, got {number!r}")
    title_size = str(card.get("title_size", "40px")).strip()
    if not re.fullmatch(r"[0-9]+px", title_size):
        raise SystemExit(f"card '{slug}': title_size must look like '40px', got {title_size!r}")
    accent = str(card.get("accent", "")).strip().lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", accent):
        raise SystemExit(f"card '{slug}': accent must be a 6-digit hex colour, got {accent!r}")
    illustration = card.get("illustration", "")
    if not isinstance(illustration, str) or not illustration.strip():
        raise SystemExit(f"card '{slug}': missing illustration markup")
    description = card.get("description", "")
    if isinstance(description, str):
        description = [description]
    if not isinstance(description, list) or not description or any(not str(d).strip() for d in description):
        raise SystemExit(f"card '{slug}': description must be a string or a list of strings")
    if len(description) > 2:
        raise SystemExit(f"card '{slug}': max 2 description lines, got {len(description)}")
    pills = card.get("pills", [])
    if isinstance(pills, list) and pills and all(isinstance(p, str) for p in pills):
        pills = auto_pills(pills)
    pills = normalize_pills({"pills": pills})
    out = {
        "slug": slug,
        "number": number,
        "title": title,
        "title_size": title_size,
        "accent": accent,
        "illustration": illustration,
        "description": [str(d) for d in description],
        "pills": pills,
    }
    return out


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    raw_cards = config.get("cards")
    if isinstance(raw_cards, list):
        cards = [normalize_card(c) for c in raw_cards]
    else:
        raise SystemExit("cards.json must contain a 'cards' list")
    slugs = [c["slug"] for c in cards]
    if len(set(slugs)) != len(slugs):
        raise SystemExit("duplicate slugs in cards.json: " + ", ".join(sorted({s for s in slugs if slugs.count(s) > 1})))
    for card in cards:
        svg = render_card(card)
        target = CARDS_DIR / f"{card['slug']}.svg"
        target.write_text(svg, encoding="utf-8")
        print(f"wrote {target.relative_to(REPO)}")


if __name__ == "__main__":
    main()
