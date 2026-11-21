#!/usr/bin/env python3
"""Fetch the Continuum (Wii) font from fontmeme.com for card rendering.

The brand cards use 'Continuum Bold' for titles (the Wii font by Brøderbund
Software, free download at fontmeme.com/continuum-font/). The build must not
rely on a locally installed copy: this helper downloads contb.ttf into a
git-ignored cache dir and returns its path so render_card_pngs.py can use it.

Deliberately guarded:
- the downloaded font is never committed (render tools never stage it);
- if every candidate URL fails, it prints the URLs tried and returns [],
  so callers can fall back to the system fonts instead of failing the build.

Usage:

    python3 tools/fonts.py        # prints paths, exit code 0 even if download failed
"""
import re
import ssl
import sys
import struct
import tempfile
import urllib.request
import urllib.error
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO / ".cache" / "fonts"
FONT_NAME = "contb.ttf"
FONT_URLS = [
    "https://fontmeme.com/fonts/static/15360/contb.ttf",
    "https://fontmeme.com/fonts/static/15360/contb.ttf.download",
    "https://fontmeme.com/fonts/continuum-font/contb.ttf",
    "https://fontmeme.com/fonts/contb.ttf",
    "https://fontmeme.com/fonts/continuum-font/download/contb.ttf",
    "https://fontmeme.com/download/contb.ttf",
]


def ttf_magic_ok(data: bytes) -> bool:
    return len(data) > 4 and (data[:4] == b"\x00\x01\x00\x00" or data[:4] == b"true" or data[:4] == b"OTTO")


def read_family_name(ttf_path):
    """Read the family name from a TTF/OTF name table (Windows platform)."""
    data = Path(ttf_path).read_bytes()
    num_tables = struct.unpack(">H", data[4:6])[0]
    table_offset = 12
    name_offset = None
    for i in range(num_tables):
        rec = data[table_offset + i * 16: table_offset + (i + 1) * 16]
        tag = rec[:4]
        offset = struct.unpack(">I", rec[8:12])[0]
        if tag == b"name":
            name_offset = offset
            break
    if name_offset is None:
        return None
    count = struct.unpack(">H", data[name_offset + 2:name_offset + 4])[0]
    string_offset = name_offset + struct.unpack(">H", data[name_offset + 4:name_offset + 6])[0]
    best = None
    for i in range(count):
        rec = data[name_offset + 6 + i * 12: name_offset + 6 + (i + 1) * 12]
        platform, encoding, language, name_id, length, offset = struct.unpack(">HHHHHH", rec)
        if platform != 3 or name_id not in (1, 16):
            continue
        raw = data[string_offset + offset: string_offset + offset + length]
        try:
            text = raw.decode("utf-16-be").strip()
        except UnicodeDecodeError:
            continue
        if text:
            best = text
            if name_id == 16:
                return text  # typographic family wins
            break
    return best


PAGE_URL = "https://fontmeme.com/fonts/continuum-font/"


def page_candidate_urls():
    """Discover the download link straight from the fontmeme page."""
    try:
        req = urllib.request.Request(
            PAGE_URL,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Firefox/121.0"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"failed to fetch font page {PAGE_URL} -> {e}", file=sys.stderr)
        return []
    urls = []
    for m in re.finditer(r'href=["\']([^"\']+contb\.ttf[^"\']*)["\']', html, re.I):
        url = m.group(1).strip()
        if url.startswith("https://"):
            urls.append(url)
        elif url.startswith("//"):
            urls.append("https:" + url)
        elif url.startswith("/"):
            urls.append("https://fontmeme.com" + url)
        else:
            urls.append("https://fontmeme.com/" + url)
    return urls


def download_font(destination, urls):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    discovered = page_candidate_urls()
    if discovered:
        print(f"discovered {len(discovered)} .ttf link(s) from fontmeme page")
    # try page-discovered URLs first (they are the real links), then the static guesses
    ordered = discovered + [u for u in urls if u not in discovered]
    for url in ordered:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Firefox/121.0"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            if not ttf_magic_ok(data):
                print(f"rejected (not a font): {url}", file=sys.stderr)
                continue
            destination.write_bytes(data)
            print(f"downloaded {FONT_NAME} from {url} ({len(data)} bytes)")
            return True
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ssl.SSLError, TimeoutError) as e:
            print(f"failed: {url} -> {e}", file=sys.stderr)
    return False


def ensure_continuum(cache_dir=None):
    """Return (font_path, family_name) for the Continuum bold font, or (None, None)."""
    cache_dir = Path(cache_dir or CACHE_DIR)
    destination = cache_dir / FONT_NAME
    if not destination.is_file():
        if not download_font(destination, FONT_URLS):
            return None, None
    family = read_family_name(destination)
    return str(destination), family


def main():
    """Never fail the build: a missing brand font degrades gracefully.

    Returns 0 either way, but exits non-zero via a loudly-printed marker when
    the font could not be fetched — stderr output makes the degraded build
    visible in CI logs (render_card_pngs.py then renders missing PNGs with
    system fonts and keeps committed brand PNGs untouched).
    """
    font, family = ensure_continuum()
    if font and family:
        print(f"continuum font: {font} (family={family!r})")
        return 0
    print("WARNING: cannot fetch the Continuum font from fontmeme.com (see URLs tried above); "
          "PNGs will render with system fonts. The committed brand-font PNGs are kept as-is.",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
