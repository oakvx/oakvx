#!/usr/bin/env python3
"""Build every Wii System Menu asset used by the profile README.

Usage:
    python tools/build_wii_assets.py            # all assets
    python tools/build_wii_assets.py -o menu    # one group

The script only reads the repository's own Mii artwork (assets/mii) and the
OFL fonts vendored in tools/fonts. Nothing is downloaded at build time.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

import wii_channels as wc  # noqa: E402
import wii_menu as wm  # noqa: E402
import wii_screens as ws  # noqa: E402
from wiilib import load_mii_frames, mii_head, save_gif  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "wii"

MENU_SIZE = (960, 540)
MII_SCREEN = (1000, 560)
MII_SCREEN_OUT = (800, 448)


def prepare_mii():
    frames = load_mii_frames(ROOT / "assets/mii/standing.gif", every=2, height=520)
    wc.MII_HEAD = mii_head(ROOT / "assets/mii/showing.png", 180)
    ws.MII_HEAD = wc.MII_HEAD
    return frames


# --------------------------------------------------------------------------
# groups
# --------------------------------------------------------------------------


def build_channels(mii_frames):
    out = OUT / "channels"
    out.mkdir(parents=True, exist_ok=True)
    for ch in wc.CHANNELS:
        frame = mii_frames[0] if ch["key"] == "mii" else None
        im = wc.render_channel(ch["key"], 480, 320, ss=2, pad=18, mii_frame=frame)
        save_channel_png(im, out / f"{ch['key']}.png")
    print(f"  channels: {len(wc.CHANNELS)} tiles")


def save_channel_png(im: Image.Image, path: Path):
    # True-colour: palette quantisation puts visible steps in the subtle
    # gradients that run across each channel artwork.
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, optimize=True)


def build_headings():
    out = OUT / "headings"
    ws.heading_images(out)
    print(f"  headings: {len(ws.HEADINGS)} x 2")


def build_menu_static(mii_frames):
    wm.TileCache.reset()
    base = wm.render_background()
    frame = wm.compose_frame(base.convert("RGBA"), "yag", 1.0, mii_frames[0], (198, 118))
    frame.save(OUT / "menu-static.png", optimize=True)
    print("  menu-static.png")


def build_mii_screen(mii_frames, animated=True):
    # A dedicated Mii Channel scene, animated with the real avatar artwork.
    dance = load_mii_frames(ROOT / "assets/mii/idlewainting.gif", every=1, height=430)
    bg = ws.mii_plaza_background(*MII_SCREEN)
    static = ws.compose_mii_screen(bg, dance[0], x=500, floor_y=506, height=396)
    static.resize(MII_SCREEN_OUT, Image.LANCZOS).save(OUT / "mii-channel.png", optimize=True)

    if not animated:
        return
    frames = []
    for frame in dance:
        im = ws.compose_mii_screen(bg, frame, x=500, floor_y=506, height=396)
        frames.append(im.convert("RGB").resize(MII_SCREEN_OUT, Image.LANCZOS))
    save_gif(frames, OUT / "mii-channel.gif", duration=85, colors=128)
    print(f"  mii channel: {len(frames)} frames")


def build_screens():
    ws.render_settings().save(OUT / "settings.png", optimize=True)
    ws.render_message_board().save(OUT / "message-board.png", optimize=True)
    ws.render_internet().save(OUT / "internet-channel.png", optimize=True)
    ws.render_contact().save(OUT / "contact.png", optimize=True)
    print("  screens: settings, message board, internet channel, contact")


# --------------------------------------------------------------------------
# hero animation
# --------------------------------------------------------------------------

POINTER_PATH = [
    (0.00, (520, 610)),
    (0.90, (198, 118)),
    (2.10, (198, 118)),
    (2.70, (404, 118)),
    (3.80, (404, 118)),
    (4.40, (612, 118)),
    (5.40, (612, 118)),
    (6.00, (200, 262)),
    (7.40, (200, 262)),
    (8.00, (520, 610)),
    (8.40, (520, 610)),
]

SELECT_WINDOWS = [
    ("yag", 0.80, 2.25),
    ("synk", 2.52, 3.95),
    ("brat", 4.22, 5.55),
    ("mii", 5.82, 7.55),
]


def _fade_window(t, start, end, fade=0.18):
    if t <= start or t >= end:
        return 0.0
    return min(1.0, (t - start) / fade, (end - t) / fade)


def build_menu_gif(mii_frames, fps=10):
    total = 8.4
    n = int(total * fps)
    wm.TileCache.reset()
    base = wm.render_background()
    frames = []
    t0 = time.time()
    for i in range(n):
        t = i / fps
        # Mii tile idles slowly (real frames from standing.gif)
        mi = mii_frames[int(t * 2.6) % len(mii_frames)]
        amounts = {key: _fade_window(t, a, b) for key, a, b in SELECT_WINDOWS}
        selected = max(amounts, key=amounts.get) if max(amounts.values()) > 0 else None
        sel = amounts.get(selected, 0.0) if selected else 0.0
        pulse = 0.004 * sel * (0.5 + 0.5 * __import__("math").sin(t * 5.2))
        from wiilib import keyframe_xy
        pos = keyframe_xy(POINTER_PATH, t)
        alpha = 1.0
        if t < 0.55:
            alpha = max(0.0, (t - 0.25) / 0.30)
        if t > 7.75:
            alpha = max(0.0, 1 - (t - 7.75) / 0.28)
        frame = wm.compose_frame(base.convert("RGBA"), selected, sel, mi, pos, alpha, pulse)
        frames.append(frame)
    print(f"  menu frames rendered in {time.time() - t0:.1f}s")
    save_gif(frames, OUT / "menu.gif", duration=int(1000 / fps), colors=96)
    print(f"  menu.gif: {len(frames)} frames")


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--only",
        choices=["channels", "headings", "menu", "mii", "screens", "all"],
        default="all",
    )
    parser.add_argument("--no-animation", action="store_true", help="skip GIF rendering")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    mii_frames = prepare_mii()
    t0 = time.time()

    if args.only in ("channels", "all"):
        print("channels")
        build_channels(mii_frames)
    if args.only in ("headings", "all"):
        print("headings")
        build_headings()
    if args.only in ("screens", "all"):
        print("screens")
        build_screens()
    if args.only in ("mii", "all"):
        print("mii channel")
        build_mii_screen(mii_frames, animated=not args.no_animation)
    if args.only in ("menu", "all"):
        print("menu")
        build_menu_static(mii_frames)
        if not args.no_animation:
            build_menu_gif(mii_frames)

    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"done in {time.time() - t0:.1f}s · assets/wii = {total / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
