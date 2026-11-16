"""Channel artwork and channel frames for the Wii System Menu tribute.

Each channel is a landscape tile with the proportions of the original System
Menu (3:2), a glossy white frame, a soft drop shadow and cyan selection glow.
Artwork is drawn from primitives at final resolution with supersampling.
"""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter

from wiilib import (
    CYAN,
    FRAME_BORDER,
    INK,
    Pen,
    glow_image,
    mask_at,
    pinstripes,
    radial_glow,
    shadow_image,
    vertical_gradient,
)

CHANNELS = [
    dict(
        key="yag",
        name="YAG",
        subtitle="AI Gateway",
        href="https://github.com/oakvx/yag",
        alt="YAG channel: an AI gateway written in C17, with OpenAI- and Anthropic-compatible adapters.",
    ),
    dict(
        key="synk",
        name="synk",
        subtitle="Salon Automation",
        href="https://github.com/oakvx/synkris",
        alt="synk channel: on-premise salon booking and messaging platform with Google Calendar and WhatsApp.",
    ),
    dict(
        key="brat",
        name="Brat Animator",
        subtitle="Creative Studio",
        href="https://github.com/oakvx/bratAnimator",
        alt="Brat Animator channel: a local-only lyric-video studio that runs entirely in the browser.",
    ),
    dict(
        key="middleman",
        name="middleManPS4",
        subtitle="Reverse Engineering",
        href="https://github.com/oakvx/middleManPS4",
        alt="middleManPS4 channel: PS4 payload tooling and offline ELF, Orbis and NID analysis.",
    ),
    dict(
        key="mii",
        name="Mii Channel",
        subtitle="About Me",
        href="#mii-channel",
        alt="Mii Channel: about Gabriele Lucia, with his Mii avatar standing in the plaza.",
    ),
    dict(
        key="settings",
        name="Wii Settings",
        subtitle="Tech Stack",
        href="#wii-settings",
        alt="Wii Settings channel: the languages, frameworks and tools Gabriele works with.",
    ),
    dict(
        key="board",
        name="Message Board",
        subtitle="Development Activity",
        href="#message-board",
        alt="Message Board channel: current projects, release candidates and study notes.",
    ),
    dict(
        key="internet",
        name="Internet Channel",
        subtitle="Portfolio",
        href="#internet-channel",
        alt="Internet Channel: links to the portfolio, case studies and contact pages.",
    ),
]

CHANNEL_BY_KEY = {c["key"]: c for c in CHANNELS}


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------


def _dots(p, w, h, color=(255, 255, 255, 26), step=9):
    d = ImageDraw.Draw(p.im)
    s = p.ss
    for y in range(int(step * s), int(h * s), int(step * s)):
        for x in range(int(step * s), int(w * s), int(step * s)):
            d.point((x, y), fill=color)


def _grid_lines(p, w, h, color=(255, 255, 255, 16), step=12):
    s = p.ss
    d = ImageDraw.Draw(p.im)
    for x in range(0, int(w * s), int(step * s)):
        d.line((x, 0, x, int(h * s)), fill=color, width=1)
    for y in range(0, int(h * s), int(step * s)):
        d.line((0, y, int(w * s), y), fill=color, width=1)


def _fit_size(p, text, family, weight, max_w, start, minimum=7):
    size = start
    while size > minimum:
        f = p.f(family, weight, size)
        if p.textsize(text, f)[0] <= max_w:
            return size
        size -= 0.5
    return minimum


def _caps(p, xy, text, size, color, tracking=1.3, weight=800, anchor="ls", max_w=None):
    if max_w:
        while size > 6 and p.textsize(text, p.f("ui", weight, size), tracking)[0] > max_w:
            size -= 0.5
    p.text(xy, text, p.f("ui", weight, size), color, anchor=anchor, tracking=tracking)


def _shine(p, w, h, strength=16):
    """One soft gloss band across the top of a channel, like the Wii frames."""
    g = vertical_gradient(p.im.size, [
        (0.0, (255, 255, 255, strength)),
        (0.14, (255, 255, 255, max(0, strength // 4))),
        (0.26, (255, 255, 255, 0)),
    ])
    p.im.alpha_composite(g)


# --------------------------------------------------------------------------
# channel artwork
# --------------------------------------------------------------------------


def art_yag(p, w, h):
    p.fill_gradient([(0, (9, 18, 32, 255)), (0.55, (16, 34, 57, 255)), (1, (23, 52, 82, 255))])
    p.fill_image(radial_glow((w * p.ss, h * p.ss), (w * p.ss * 0.78, h * p.ss * 0.62), h * p.ss * 0.62, (48, 196, 224), 58).resize((w, h)))
    _grid_lines(p, w, h, (255, 255, 255, 13), step=w * 0.075)

    # gateway icon: an arch feeding a small routing bus
    cx, cy = w * 0.79, h * 0.50
    s = h * 0.40
    bar = s * 0.155
    p.rrect((cx - s / 2, cy - s / 2, cx - s / 2 + bar, cy + s * 0.22), bar / 2, fill=(71, 214, 239, 255))
    p.rrect((cx + s / 2 - bar, cy - s / 2, cx + s / 2, cy + s * 0.22), bar / 2, fill=(71, 214, 239, 255))
    p.rrect((cx - s / 2, cy - s / 2, cx + s / 2, cy - s / 2 + bar), bar / 2, fill=(71, 214, 239, 255))
    p.line([(cx - s / 2, cy + s * 0.20), (cx + s / 2, cy + s * 0.20)], (71, 214, 239, 255), bar)
    for i in range(3):
        nx = cx - s * 0.28 + i * s * 0.28
        p.line([(nx, cy + s * 0.22), (nx, cy + s * 0.35)], (120, 228, 246, 190), max(1, h * 0.008))
        p.ellipse((nx - h * 0.021, cy + s * 0.35 - h * 0.021, nx + h * 0.021, cy + s * 0.35 + h * 0.021), fill=(120, 228, 246, 235))

    p.text((w * 0.075, h * 0.575), "YAG", p.f("round", 900, h * 0.30), (255, 255, 255, 255), anchor="ls")
    _caps(p, (w * 0.082, h * 0.700), "AI GATEWAY", h * 0.090, (108, 222, 242, 255), tracking=1.5)
    _caps(p, (w * 0.082, h * 0.812), "C17 · ROUTING", h * 0.070, (156, 189, 204, 255), tracking=1.0, weight=700)
    _shine(p, w, h, 12)


def art_synk(p, w, h):
    p.fill_gradient([(0, (255, 255, 255, 255)), (0.7, (238, 250, 252, 255)), (1, (224, 245, 249, 255))])
    p.fill_image(radial_glow((w * p.ss, h * p.ss), (w * p.ss * 0.8, h * p.ss * 0.45), h * p.ss * 0.48, (120, 220, 236), 60).resize((w, h)))

    # icon: chat bubble holding a calendar
    cx, cy = w * 0.79, h * 0.47
    bw, bh = w * 0.265, h * 0.42
    p.rrect((cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2), bh * 0.22, fill=(255, 255, 255, 255), outline=(16, 164, 194, 255), width=max(1.6, h * 0.014))
    p.polygon([(cx - bw * 0.12, cy + bh / 2 - 1), (cx + bw * 0.1, cy + bh / 2 - 1), (cx - bw * 0.02, cy + bh / 2 + h * 0.075)], fill=(16, 164, 194, 255))
    # calendar inside
    iw, ih = bw * 0.62, bh * 0.48
    ix, iy = cx - iw / 2, cy - ih / 2 + bh * 0.02
    p.rrect((ix, iy, ix + iw, iy + ih), ih * 0.18, fill=(255, 255, 255, 255), outline=(16, 164, 194, 255), width=max(1.2, h * 0.009))
    p.line([(ix, iy + ih * 0.28), (ix + iw, iy + ih * 0.28)], (16, 164, 194, 255), max(1.2, h * 0.009))
    for r in range(2):
        for c in range(3):
            dx = ix + iw * (0.22 + c * 0.28)
            dy = iy + ih * (0.5 + r * 0.25)
            p.ellipse((dx - h * 0.008, dy - h * 0.008, dx + h * 0.008, dy + h * 0.008), fill=(16, 164, 194, 220))
    # chat dots on the bubble's upper area
    for i in range(3):
        dx = cx - bw * 0.11 + i * bw * 0.11
        p.ellipse((dx - h * 0.012, cy - bh * 0.36, dx + h * 0.012, cy - bh * 0.36 + h * 0.024), fill=(16, 164, 194, 255))

    p.text((w * 0.075, h * 0.55), "synk", p.f("round", 900, h * 0.29), (31, 45, 50, 255), anchor="ls")
    _caps(p, (w * 0.082, h * 0.690), "SALON BOOKING", h * 0.086, (52, 112, 125, 255), tracking=1.2, max_w=w * 0.52)



def art_brat(p, w, h):
    p.fill_gradient([(0, (150, 214, 8, 255)), (0.55, (139, 205, 0, 255)), (1, (122, 185, 0, 255))])
    _dots(p, w, h, (255, 255, 255, 22), step=w * 0.035)

    # a tiny video screen: white body, lime play triangle
    cx, cy = w * 0.795, h * 0.46
    sw, sh = w * 0.30, h * 0.34
    p.rrect((cx - sw / 2 + h * 0.012, cy - sh / 2 + h * 0.018, cx + sw / 2 + h * 0.012, cy + sh / 2 + h * 0.018), sh * 0.14, fill=(72, 110, 0, 46))
    p.rrect((cx - sw / 2, cy - sh / 2, cx + sw / 2, cy + sh / 2), sh * 0.14, fill=(255, 255, 255, 255))
    p.polygon([
        (cx - sw * 0.12, cy - sh * 0.22),
        (cx + sw * 0.24, cy),
        (cx - sw * 0.12, cy + sh * 0.22),
    ], fill=(139, 205, 0, 255))
    # timeline rail under the screen
    p.rrect((cx - sw / 2, cy + sh * 0.78, cx + sw / 2, cy + sh * 0.78 + h * 0.014), h * 0.007, fill=(255, 255, 255, 110))
    p.rrect((cx - sw / 2, cy + sh * 0.78, cx - sw * 0.06, cy + sh * 0.78 + h * 0.014), h * 0.007, fill=(255, 255, 255, 235))

    p.text((w * 0.07, h * 0.60), "brat", p.f("ui", 900, h * 0.36), (255, 255, 255, 255), anchor="ls", tracking=-1.4)
    _caps(p, (w * 0.078, h * 0.735), "ANIMATOR", h * 0.100, (255, 255, 255, 255), tracking=2.0)
    _caps(p, (w * 0.078, h * 0.845), "LOCAL-FIRST STUDIO", h * 0.070, (48, 70, 0, 255), tracking=0.8, weight=800)


def art_middleman(p, w, h):
    p.fill_gradient([(0, (0, 44, 120, 255)), (0.55, (3, 66, 154, 255)), (1, (5, 84, 180, 255))])
    _grid_lines(p, w, h, (255, 255, 255, 14), step=w * 0.062)
    p.fill_image(radial_glow((w * p.ss, h * p.ss), (w * p.ss * 0.79, h * p.ss * 0.45), h * p.ss * 0.45, (110, 190, 255), 42).resize((w, h)))

    # chip with a verification mark
    cx, cy = w * 0.848, h * 0.43
    s = h * 0.222
    for i in range(4):
        off = -s / 2 + s * (0.16 + i * 0.225)
        for dx in (-1, 1):
            p.line([(cx + dx * s / 2, cy + off), (cx + dx * (s / 2 + h * 0.045), cy + off)], (196, 222, 255, 210), max(1.2, h * 0.009))
            p.line([(cx + off, cy + dx * s / 2), (cx + off, cy + dx * (s / 2 + h * 0.045))], (196, 222, 255, 210), max(1.2, h * 0.009))
    p.rrect((cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2), s * 0.18, fill=(5, 60, 140, 255), outline=(255, 255, 255, 245), width=max(1.8, h * 0.014))
    p.line([(cx - s * 0.2, cy + s * 0.02), (cx - s * 0.04, cy + s * 0.2), (cx + s * 0.26, cy - s * 0.2)], (255, 255, 255, 255), max(2, h * 0.02), joint="curve")

    size = _fit_size(p, "middleManPS4", "ui", 800, w * 0.52, h * 0.160)
    p.text((w * 0.075, h * 0.49), "middleManPS4", p.f("ui", 800, size), (255, 255, 255, 255), anchor="ls", tracking=-0.4)
    _caps(p, (w * 0.078, h * 0.625), "REVERSE", h * 0.082, (178, 216, 255, 255), tracking=1.4)
    _caps(p, (w * 0.078, h * 0.725), "ENGINEERING", h * 0.082, (178, 216, 255, 255), tracking=1.4)



def art_mii(p, w, h):
    p.fill_gradient([(0, (238, 250, 253, 255)), (0.6, (226, 246, 251, 255)), (1, (206, 238, 247, 255))])
    _dots(p, w, h, (122, 195, 213, 45), step=w * 0.032)
    # plaza floor
    p.ellipse((w * 0.40, h * 0.76, w * 1.05, h * 1.22), fill=(255, 255, 255, 72))
    p.ellipse((w * 0.40, h * 0.76, w * 1.05, h * 1.22), outline=(126, 198, 216, 55), width=max(1, h * 0.005))

    p.text((w * 0.075, h * 0.56), "Mii", p.f("round", 900, h * 0.32), (44, 62, 68, 255), anchor="ls")
    _caps(p, (w * 0.082, h * 0.690), "CHANNEL", h * 0.094, (18, 148, 180, 255), tracking=2.0)
    _caps(p, (w * 0.082, h * 0.805), "ABOUT ME", h * 0.070, (100, 126, 133, 255), tracking=1.0, weight=700)


def art_settings(p, w, h):
    p.fill_gradient([(0, (255, 255, 255, 255)), (0.7, (241, 245, 245, 255)), (1, (228, 236, 237, 255))])
    _grid_lines(p, w, h, (126, 160, 166, 22), step=w * 0.048)

    # Wii Remote
    cx, cy = w * 0.80, h * 0.50
    rw, rh = w * 0.085, h * 0.56
    p.rrect((cx - rw / 2 + h * 0.02, cy - rh / 2 + h * 0.025, cx + rw / 2 + h * 0.02, cy + rh / 2 + h * 0.025), rw / 2, fill=(120, 132, 134, 45))
    p.rrect((cx - rw / 2, cy - rh / 2, cx + rw / 2, cy + rh / 2), rw / 2, fill=(253, 254, 254, 255), outline=(151, 162, 164, 255), width=max(1.2, h * 0.009))
    p.rrect((cx - rw / 2 + rw * 0.22, cy - rh / 2 + rh * 0.03, cx + rw / 2 - rw * 0.22, cy - rh / 2 + rh * 0.09), rw * 0.2, fill=(226, 232, 232, 255))
    # power
    p.ellipse((cx - rw * 0.16, cy - rh * 0.32, cx + rw * 0.16, cy - rh * 0.32 + rw * 0.32), fill=(34, 190, 219, 255))
    # d-pad
    p.rrect((cx - rw * 0.3, cy - rh * 0.11, cx + rw * 0.3, cy + rh * 0.0), rw * 0.16, fill=(232, 237, 237, 255), outline=(189, 198, 199, 255), width=max(1, h * 0.006))
    # A button
    p.ellipse((cx - rw * 0.19, cy + rh * 0.09, cx + rw * 0.19, cy + rh * 0.09 + rw * 0.38), fill=(242, 247, 247, 255), outline=(160, 172, 174, 255), width=max(1, h * 0.007))
    # speaker
    for i in range(4):
        dx = cx - rw * 0.24 + i * rw * 0.16
        p.ellipse((dx, cy + rh * 0.31, dx + rw * 0.07, cy + rh * 0.31 + rw * 0.07), fill=(186, 196, 197, 255))
    # gear
    gx, gy, gr = w * 0.655, h * 0.74, h * 0.115
    p.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), fill=(255, 255, 255, 240), outline=(31, 154, 182, 255), width=max(1.3, h * 0.01))
    p.ellipse((gx - gr * 0.4, gy - gr * 0.4, gx + gr * 0.4, gy + gr * 0.4), outline=(31, 154, 182, 255), width=max(1.2, h * 0.009))
    for k in range(8):
        import math

        a = k * math.pi / 4
        p.line(
            [(gx + math.cos(a) * gr * 0.72, gy + math.sin(a) * gr * 0.72),
             (gx + math.cos(a) * gr * 1.06, gy + math.sin(a) * gr * 1.06)],
            (31, 154, 182, 255), max(1.2, h * 0.009),
        )

    p.text((w * 0.075, h * 0.475), "Wii", p.f("round", 700, h * 0.145), (78, 88, 91, 255), anchor="ls")
    p.text((w * 0.075, h * 0.645), "Settings", p.f("round", 900, h * 0.185), (44, 58, 62, 255), anchor="ls", tracking=-0.8)
    _caps(p, (w * 0.080, h * 0.795), "TECH STACK", h * 0.078, (20, 144, 172, 255), tracking=1.4)


def art_board(p, w, h):
    p.fill_gradient([(0, (255, 255, 253, 255)), (0.65, (247, 250, 251, 255)), (1, (231, 241, 244, 255))])
    _dots(p, w, h, (116, 166, 178, 40), step=w * 0.03)

    # one pinned note, the Message Board's signature object
    nw, nh = w * 0.30, h * 0.47
    n = Pen(nw, nh, ss=4)
    n.rrect((2, 2, nw - 2, nh - 2), nh * 0.055, fill=(255, 255, 255, 255), outline=(180, 194, 198, 255), width=1.4)
    n.line([(2, nh * 0.12), (nw - 2, nh * 0.12)], (218, 228, 231, 255), 1)
    if MII_HEAD is not None:
        head = MII_HEAD.resize((int(nw * 0.20), int(nw * 0.20)), Image.LANCZOS)
        n.paste(head, (nw * 0.10, nh * 0.20))
    for i, (x0, x1) in enumerate([(0.38, 0.86), (0.38, 0.74), (0.38, 0.82), (0.12, 0.70)]):
        y = nh * (0.30 + i * 0.15)
        n.line([(nw * x0, y), (nw * x1, y)], (214, 225, 228, 255), max(1, nh * 0.013))
    # pin
    n.ellipse((nw * 0.43, -nh * 0.055, nw * 0.57, nh * 0.075), fill=(221, 73, 57, 255))
    n.ellipse((nw * 0.465, -nh * 0.02, nw * 0.505, nh * 0.02), fill=(255, 255, 255, 90))
    note = n.finish((nw, nh)).rotate(-5, resample=Image.BICUBIC, expand=True)
    p.paste(note, (w * 0.635, h * 0.13))

    p.text((w * 0.075, h * 0.49), "Message", p.f("round", 800, h * 0.165), (34, 60, 74, 255), anchor="ls")
    p.text((w * 0.075, h * 0.645), "Board", p.f("round", 800, h * 0.165), (34, 60, 74, 255), anchor="ls")
    _caps(p, (w * 0.080, h * 0.780), "DEVELOPMENT", h * 0.072, (44, 130, 152, 255), tracking=1.0, weight=700)
    _caps(p, (w * 0.080, h * 0.875), "ACTIVITY", h * 0.072, (44, 130, 152, 255), tracking=1.0, weight=700)


def art_internet(p, w, h):
    p.fill_gradient([(0, (255, 255, 255, 255)), (0.7, (240, 249, 252, 255)), (1, (219, 240, 247, 255))])
    p.fill_image(radial_glow((w * p.ss, h * p.ss), (w * p.ss * 0.80, h * p.ss * 0.45), h * p.ss * 0.50, (120, 210, 232), 52).resize((w, h)))

    cx, cy, r = w * 0.795, h * 0.47, h * 0.25
    p.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(232, 248, 253, 255), outline=(19, 125, 182, 255), width=max(1.8, h * 0.013))
    p.ellipse((cx - r * 0.45, cy - r, cx + r * 0.45, cy + r), outline=(19, 125, 182, 190), width=max(1, h * 0.008))
    p.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(19, 125, 182, 0), width=1)
    p.line([(cx - r, cy), (cx + r, cy)], (19, 125, 182, 190), max(1, h * 0.008))
    p.arc((cx - r, cy - r * 0.55, cx + r, cy + r * 0.55), 0, 360, fill=(19, 125, 182, 140), width=max(1, h * 0.007))
    p.arc((cx - r * 0.55, cy - r, cx + r * 0.55, cy + r), 0, 360, fill=(19, 125, 182, 120), width=max(1, h * 0.006))

    p.text((w * 0.075, h * 0.47), "Internet", p.f("round", 800, h * 0.145), (13, 108, 160, 255), anchor="ls")
    p.text((w * 0.075, h * 0.625), "Channel", p.f("round", 800, h * 0.145), (13, 108, 160, 255), anchor="ls")
    _caps(p, (w * 0.080, h * 0.785), "PORTFOLIO · OAKVX", h * 0.070, (76, 108, 119, 255), tracking=0.9, weight=700)


ART = {
    "yag": art_yag,
    "synk": art_synk,
    "brat": art_brat,
    "middleman": art_middleman,
    "mii": art_mii,
    "settings": art_settings,
    "board": art_board,
    "internet": art_internet,
}

MII_KEY = "mii"
MII_HEAD: Image.Image | None = None
# Where the avatar stands inside the Mii Channel artwork (fractions of the art).
MII_BOX = (0.475, 0.075, 1.0, 0.945)


# --------------------------------------------------------------------------
# frame
# --------------------------------------------------------------------------


def render_channel(
    key,
    w=240,
    h=160,
    ss=3,
    glow=0.0,
    pad=14,
    mii_frame: Image.Image | None = None,
):
    """Render one channel tile, including its frame, shadow and optional glow."""
    total_w, total_h = int(w + pad * 2), int(h + pad * 2)
    S = ss
    p = Pen(total_w, total_h, ss=S)
    box = (pad, pad, pad + w, pad + h)
    radius = h * 0.075
    box_ss = tuple(v * S for v in box)

    if glow > 0.01:
        halo = glow_image(
            (total_w * S, total_h * S),
            box_ss,
            radius * S,
            color=(78, 208, 236),
            spread=max(2, h * 0.07 * S),
            opacity=int(205 * min(1.0, glow)),
            ring=max(2, h * 0.013 * S),
            ring_opacity=int(245 * min(1.0, glow)),
        )
        p.paste_ss(halo, (0, 0))

    p.paste_ss(
        shadow_image(
            (total_w * S, total_h * S),
            box_ss,
            radius * S,
            dy=max(1, h * 0.024 * S),
            blur=max(1.5, h * 0.026 * S),
            opacity=72,
            ss=1,
        ),
        (0, 0),
    )

    # frame
    p.fill_rounded_gradient(box, radius, [(0, (255, 255, 255, 255)), (0.55, (253, 253, 252, 255)), (1, (244, 245, 243, 255))])
    p.rrect(box, radius, outline=FRAME_BORDER, width=max(1, h * 0.009))

    inset = max(2.4, h * 0.033)
    art_box = (box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset)
    art_w, art_h = int(round(w - inset * 2)), int(round(h - inset * 2))
    art = Pen(art_w, art_h, ss=S)
    ART[key](art, art_w, art_h)
    art_img = art.im  # already at S resolution

    if key == MII_KEY and mii_frame is not None:
        fx, fy = art_w * MII_BOX[0], art_h * MII_BOX[1]
        fw, fh = art_w * (MII_BOX[2] - MII_BOX[0]), art_h * (MII_BOX[3] - MII_BOX[1])
        fw_ss, fh_ss = fw * S, fh * S
        scale = min(fw_ss / mii_frame.width, fh_ss / mii_frame.height)
        frame = mii_frame.resize(
            (max(1, round(mii_frame.width * scale)), max(1, round(mii_frame.height * scale))),
            Image.LANCZOS,
        )
        # soft contact shadow, like the Mii Channel floor.  Pad the canvas so
        # the blur fades to zero instead of ending on a visible rectangle.
        sh_w, sh_h = int(frame.width * 0.92), max(10, int(frame.height * 0.15))
        pad_s = int(sh_h * 1.6)
        sh = Image.new("RGBA", (sh_w + 2 * pad_s, sh_h + 2 * pad_s), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse(
            (pad_s, pad_s, pad_s + sh_w, pad_s + sh_h), fill=(66, 96, 104, 38)
        )
        sh = sh.filter(ImageFilter.GaussianBlur(sh_h / 2.2))
        art_img.alpha_composite(
            sh,
            (
                int((fx + fw / 2) * S - sh.width / 2),
                int((fy + fh) * S - pad_s - sh_h * 0.65),
            ),
        )
        art_img.alpha_composite(frame, (int((fx + fw / 2) * S - frame.width / 2), int((fy + fh) * S - frame.height)))

    mask = mask_at((total_w * S, total_h * S), tuple(v * S for v in art_box), max(1.0, radius - inset * 0.55) * S)
    layer = Image.new("RGBA", (total_w * S, total_h * S), (0, 0, 0, 0))
    layer.paste(art_img, (int(art_box[0] * S), int(art_box[1] * S)))
    p.im.alpha_composite(Image.composite(layer, Image.new("RGBA", layer.size, (0, 0, 0, 0)), mask))

    # inner lip + gloss on the frame only
    p.rrect(art_box, max(1.0, radius - inset * 0.55), outline=(0, 0, 0, 30), width=1)
    p.rrect((art_box[0] + 1, art_box[1] + 1, art_box[2] - 1, art_box[3] - 1), max(1.0, radius - inset * 0.55), outline=(255, 255, 255, 60), width=1)
    p.rrect(box, radius, outline=(255, 255, 255, 210), width=1)

    gloss = vertical_gradient(p.im.size, [
        (0, (255, 255, 255, 34)),
        (0.14, (255, 255, 255, 16)),
        (0.5, (255, 255, 255, 0)),
    ])
    gloss_mask = mask_at((total_w * S, total_h * S), tuple(v * S for v in (box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1)), (radius - 1) * S)
    p.im.alpha_composite(Image.composite(gloss, Image.new("RGBA", gloss.size, (0, 0, 0, 0)), gloss_mask))

    return p.finish((total_w, total_h))


def render_empty_slot(w=196, h=130, ss=3, pad=0):
    total_w, total_h = int(w + pad * 2), int(h + pad * 2)
    p = Pen(total_w, total_h, ss=ss)
    box = (pad, pad, pad + w, pad + h)
    radius = h * 0.075
    p.fill_rounded_gradient(box, radius, [(0, (238, 239, 237, 255)), (0.5, (245, 245, 243, 255)), (1, (249, 249, 247, 255))])
    stripes = pinstripes(p.im.size, (210, 210, 208, 80), step=2)
    mask = mask_at(p.im.size, tuple(v * ss for v in box), radius * ss)
    p.im.alpha_composite(Image.composite(stripes, Image.new("RGBA", stripes.size, (0, 0, 0, 0)), mask))
    p.rrect(box, radius, outline=(211, 212, 210, 255), width=max(1, h * 0.009))
    p.text(
        (total_w / 2, total_h / 2 + h * 0.055),
        "Wii",
        p.f("round", 700, h * 0.16),
        (214, 215, 213, 255),
        anchor="ms",
    )
    return p.finish((total_w, total_h))


# --------------------------------------------------------------------------
# Wii pointer
# --------------------------------------------------------------------------


def render_pointer(height=56):
    """The System Menu hand pointer: white glove, dark outline, soft halo.

    Drawn from primitives (no ripped artwork). The fingertip sits at 47% of the
    image width and 2.5% of its height, which is the anchor used when moving it.
    """
    design_w, design_h = 62.0, 84.0
    f = height / design_h
    w = max(8, int(round(design_w * f)))
    ss = 6
    S = f * ss
    p = Pen(w, height, ss=ss)
    size = (w * ss, height * ss)

    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)

    def rr(box, radius):
        d.rounded_rectangle(tuple(int(round(v * S)) for v in box), radius=radius * S, fill=255)

    def el(box):
        d.ellipse(tuple(int(round(v * S)) for v in box), fill=255)

    rr((25.5, 3, 36, 45), 5.2)        # index finger
    rr((17.5, 30, 44.5, 61), 12.5)    # palm
    el((9, 37, 24, 50))                # thumb
    for cy in (38, 47, 56):           # curled fingers
        el((38, cy - 7.5, 53, cy + 7.5))
    rr((23.5, 54, 39.5, 79), 7)       # wrist

    # contact shadow
    sh = m.filter(ImageFilter.GaussianBlur(2.5 * ss))
    sh_im = Image.new("RGBA", size, (46, 62, 66, 255))
    sh_im.putalpha(sh.point(lambda v: int(v * 0.30)))
    p.im.alpha_composite(sh_im, (int(2.2 * S), int(3.4 * S)))

    # cyan halo
    halo = m.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(2.2 * ss))
    halo_im = Image.new("RGBA", size, (96, 208, 234, 255))
    halo_im.putalpha(halo.point(lambda v: int(v * 0.55)))
    p.im.alpha_composite(halo_im)

    # dark outline
    k = max(5, int(round(2.6 * S)))
    k += 1 if k % 2 == 0 else 0
    outline = m.filter(ImageFilter.MaxFilter(k))
    out_im = Image.new("RGBA", size, (47, 58, 62, 255))
    out_im.putalpha(outline)
    p.im.alpha_composite(out_im)

    # white glove with a cool shade at the wrist
    fill = vertical_gradient(size, [(0, (255, 255, 255, 255)), (0.6, (251, 253, 253, 255)), (1, (225, 235, 237, 255))])
    fill.putalpha(m)
    p.im.alpha_composite(fill)

    # glove seams: thumb crease and knuckles, drawn with the same outline colour
    detail = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(detail)
    seam = (72, 88, 93, 225)
    wdt = max(1, int(1.5 * S))

    def line(pts):
        p.d.line([(x * S, y * S) for x, y in pts], fill=seam, width=wdt, joint="curve")

    line([(22, 44), (24, 50), (27, 55)])
    line([(42, 42), (45, 45)])
    line([(43, 50), (46, 53)])
    line([(42, 58), (45, 61)])
    img = p.finish((w, height))
    # a slight tilt makes it read as a pointing hand, not a raised fist
    return img.rotate(-9, resample=Image.BICUBIC, expand=True)


def pointer_anchor(im):
    """Pixel position of the fingertip in a rendered pointer image."""
    alpha = im.getchannel("A")
    w, h = im.size
    for y in range(h):
        xs = [x for x in range(w) if alpha.getpixel((x, y)) > 90]
        if xs:
            return (sum(xs) / len(xs), y)
    return (w / 2, 0)


# --------------------------------------------------------------------------
# section heading (same visual language as the original profile headings)
# --------------------------------------------------------------------------


def render_heading(text, color=INK, accent=CYAN, height=48, ss=3):
    probe = Pen(10, 10, ss=1)
    size = height * 0.56
    f = probe.f("round", 800, size)
    tw = probe.textsize(text, f)[0]
    width = int(round(tw + height * 0.46 + 6))
    p = Pen(width, height, ss=ss)
    bar_w = height * 0.125
    p.rrect((1, height * 0.19, 1 + bar_w, height * 0.81), bar_w / 2, fill=accent)
    p.text((bar_w + height * 0.31, height * 0.5), text, p.f("round", 800, size), color, anchor="lm", tracking=-0.5)
    return p.finish((width, height))
