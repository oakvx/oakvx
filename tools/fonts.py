#!/usr/bin/env python3
"""Fetch the Continuum (Wii) font at build time for card rendering.

The brand cards use the Continuum family (by Brøderbund Software) for
titles. The build must not rely on a locally installed copy: this helper
downloads the font file from CDNFonts (primary, pointed at by the project)
into a git-ignored cache dir and returns its path so render_card_pngs.py
can use it.

The fontmeme.com route is kept as a legacy fallback (in case CDNFonts is
unreachable); it reads the download URL from the fontmeme page when
possible.

Deliberately guarded:
- the downloaded font is never committed (render tools never stage it);
- if every candidate URL fails, it prints the URLs tried and exits 0 with
  a warning, so callers can fall back to the system fonts instead of
  failing the build.

Usage:

    python3 tools/fonts.py        # prints the font path/family, exits 0 either way
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

# Continuum (Wii font) via CDNFonts.com — the source pointed at by the user.
CDNFONTS_CSS_URL = "https://fonts.cdnfonts.com/css/continuum-medium"
CDNFONTS_FONT_NAME = "continuum-medium.woff"
# The brand family (Continuum Bold) was never served by the CDN; Medium is the
# closest brand-weight available there. The weights explicitly listed on the
# source estimate are 'Continuum Light' and 'Continuum Medium'.

# Fallback: the original fontmeme.com route (unreachable from sandboxes).
FONTMEME_CSS_URL = "https://fontmeme.com/fonts/continuum-font/"
FONTMEME_FONT_NAME = "contb.ttf"
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


def download(url, destination, max_bytes=8 * 1024 * 1024):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Firefox/121.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise OSError("font download too large")
    return data


def validate_font(data, kind):
    # WOFF/WOFF2 or TrueType magic bytes
    if kind == "woff":
        return data[:4] in (b"wOFF", b"wOF2")
    return data[:4] in (b"\x00\x01\x00\x00", b"true", b"OTTO")


def fetch_cdnfonts():
    """Fetch the Continuum font file from CDNFonts."""
    try:
        css = download(CDNFONTS_CSS_URL, None)
    except Exception as e:
        print(f"failed to fetch CDNFonts CSS {CDNFONTS_CSS_URL} -> {e}", file=sys.stderr)
        return None, None
    if isinstance(css, bytes):
        css = css.decode("utf-8", "replace")
    m = re.search(r"url\('([^']+\.(?:woff2?|ttf|otf))'\)", css, re.I)
    if not m:
        print("no .ttf/.woff link found in CDNFonts CSS", file=sys.stderr)
        return None, None
    woff_url = re.sub(r"\\(.)", r"\1", m.group(1))  # unescape CSS url() string
    if woff_url.startswith("//"):
        woff_url = "https:" + woff_url
    print(f"CDNFonts @font-face src: {woff_url}")
    try:
        data = download(woff_url, None)
        if not validate_font(data, "woff"):
            print("CDNFonts font file rejected (not a WOFF)", file=sys.stderr)
            return None, None
    except Exception as e:
        print(f"failed to download CDNFonts font from {woff_url} -> {e}", file=sys.stderr)
        return None, None
    family_m = re.search(r"font-family:\s*'([^']+)'", css)
    family = family_m.group(1) if family_m else "Continuum Medium"
    return data, family


def fetch_fontmeme():
    """Fallback: try the fontmeme.com route from the original request."""
    for url in page_candidate_urls() + FONT_URLS:
        try:
            data = download(url, None)
            if not validate_font(data, "ttf"):
                print(f"rejected (not a font): {url}", file=sys.stderr)
                continue
            return data, None
        except Exception as e:
            print(f"failed: {url} -> {e}", file=sys.stderr)
    return None, None


def convert_woff_to_ttf(woff_path, ttf_path):
    """Convert a WOFF font to TTF using fontTools.

    resvg (the renderer) silently ignores WOFF files, so the brand font must
    be TTF before rendering. Returns True on success; False on failure —
    callers then treat the CDN route as unavailable and fall back.
    """
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        print("fontTools not installed - cannot convert WOFF to TTF "
              "(this needs `pip install fonttools`)", file=sys.stderr)
        return False
    try:
        font = TTFont(str(woff_path))
        # force a plain TTF (not WOFF) regardless of filename or the source flavor
        font.flavor = None
        font.save(str(ttf_path))
        print(f"converted {woff_path.name} -> {ttf_path.name}")
        return True
    except Exception as e:
        print(f"WOFF -> TTF conversion failed ({e})", file=sys.stderr)
        return False


def ensure_continuum(cache_dir=None):
    """Return (font_path, family_name) for the Continuum brand font, or (None, None).

    The renderer (resvg) silently ignores WOFF files, so the CDN route converts
    the downloaded WOFF to TTF before anything else can use it; only a TTF
    is ever returned.
    """
    cache_dir = Path(cache_dir or CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # CDN route (primary)
    woff_dest = cache_dir / CDNFONTS_FONT_NAME
    ttf_dest = cache_dir / "continuum-medium.ttf"
    if not ttf_dest.is_file():
        if not woff_dest.is_file():
            data, _ = fetch_cdnfonts()
            if data:
                woff_dest.write_bytes(data)
                print(f"downloaded Continuum font from CDNFonts: {woff_dest} ({len(data)} bytes)")
        if woff_dest.is_file():
            convert_woff_to_ttf(woff_dest, ttf_dest)
    if ttf_dest.is_file():
        family = read_family_name(ttf_dest) or "Continuum Medium"
        return str(ttf_dest), family
    # CDN route failed: fall back to fontmeme
    print("CDNFonts route unavailable (download or conversion failed) — trying fontmeme.com",
          file=sys.stderr)

    # fontmeme fallback
    meme_dest = cache_dir / FONTMEME_FONT_NAME
    if not meme_dest.is_file():
        data, _ = fetch_fontmeme()
        if data:
            meme_dest.write_bytes(data)
            print(f"downloaded Continuum font from fontmeme: {meme_dest} ({len(data)} bytes)")
    if meme_dest.is_file():
        family = read_family_name(meme_dest)
        if family:
            return str(meme_dest), family
        # magic-validated TTF whose family could not be read; pass the file
        # through with the CSS family as a last resort
        return str(meme_dest), "Continuum Bold"

    return None, None


def main():
    """Never fail the build: a missing brand font degrades gracefully.

    Returns 0 either way. On total failure it prints the URLs tried and a
    warning, so CI logs show why the brand font was missing and
    render_card_pngs.py keeps committed brand-font PNGs untouched.
    """
    font, family = ensure_continuum()
    if font and family:
        print(f"continuum font: {font} (family={family!r})")
        return 0
    print("WARNING: cannot fetch the Continuum font (see URLs tried above); "
          "PNGs will render with system fonts. The committed brand-font PNGs are kept as-is.",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
