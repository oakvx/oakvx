"""The Wii System Menu screen: wallpaper, 4x3 channel grid, silver footer."""

from __future__ import annotations

from PIL import Image, ImageDraw

from wiilib import (
    CYAN,
    Pen,
    mask_at,
    radial_glow,
    vertical_gradient,
)
from wii_channels import CHANNELS, pointer_anchor, render_channel, render_empty_slot, render_pointer

# layout, in output pixels
W, H = 960, 540
TILE_W, TILE_H = 192, 128
GAP_X, GAP_Y = 13, 13
GRID_X, GRID_Y = 44, 16
FOOTER_Y = 432
TRAY_X0, TRAY_X1, TRAY_DEPTH = 280.0, 680.0, 46.0
ARROW_BOX = (879, 192, 917, 246)
POINTER_H = 56

SLOTS = []
for i, ch in enumerate(CHANNELS):
    col, row = i % 4, i // 4
    SLOTS.append((ch["key"], GRID_X + col * (TILE_W + GAP_X), GRID_Y + row * (TILE_H + GAP_Y)))
EMPTY_ROW_Y = GRID_Y + 2 * (TILE_H + GAP_Y)


def _tray_curve(steps=96):
    """Smooth, shallow U for the central tray; horizontal tangents at both ends."""
    import math

    x0, x1, d = TRAY_X0, TRAY_X1, TRAY_DEPTH
    pts = []
    for i in range(steps + 1):
        t = i / steps
        y = FOOTER_Y + d * math.sin(math.pi * t) ** 2
        pts.append((x0 + (x1 - x0) * t, y))
    return pts


def render_background():
    """Everything static: wallpaper, empty channels, footer, page arrow."""
    S = 2
    p = Pen(W, H, ss=S)

    # silver footer behind everything
    p.im.alpha_composite(vertical_gradient(p.im.size, [
        (0, (226, 227, 225, 255)),
        (0.18, (210, 211, 209, 255)),
        (0.58, (196, 197, 195, 255)),
        (0.9, (206, 207, 205, 255)),
        (1, (226, 227, 225, 255)),
    ]))

    # white content panel + central tray, built as one mask
    shape = Image.new("L", (W * 4, H * 4), 0)
    sd = ImageDraw.Draw(shape)
    sd.rounded_rectangle((0, -160, W * 4, FOOTER_Y * 4), radius=30 * 4, fill=255)
    tray = [(x * 4, y * 4) for x, y in _tray_curve()]
    sd.polygon(tray + [(TRAY_X1 * 4, -160), (TRAY_X0 * 4, -160)], fill=255)
    shape = shape.resize((W, H), Image.LANCZOS)

    panel_face = vertical_gradient((W, H), [
        (0, (255, 255, 255, 255)),
        (0.45, (253, 253, 252, 255)),
        (0.8, (248, 248, 246, 255)),
        (1, (243, 243, 241, 255)),
    ])
    dots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dots)
    for y in range(7, int(FOOTER_Y + TRAY_DEPTH + 20), 7):
        for x in range(7, W, 7):
            dd.point((x, y), fill=(224, 224, 221, 135))
    panel_face = Image.alpha_composite(panel_face, dots)
    content = Image.composite(panel_face, Image.new("RGBA", (W, H), (0, 0, 0, 0)), shape)
    content = Image.alpha_composite(
        content,
        radial_glow((W, H), (W / 2, -H * 0.12), W * 0.95, (255, 255, 255), 30),
    )
    p.im.alpha_composite(content.resize(p.im.size, Image.LANCZOS))

    # cyan seam tracing the panel: horizontal edge, tray curve, horizontal edge
    seam_pts = [(0, FOOTER_Y)] + _tray_curve() + [(W, FOOTER_Y)]
    seam = Image.new("RGBA", p.im.size, (0, 0, 0, 0))
    ImageDraw.Draw(seam).line([(x * S, y * S) for x, y in seam_pts], fill=(83, 194, 222, 235), width=max(1, int(1.6 * S)), joint="curve")
    p.im.alpha_composite(seam)

    # empty channel row, exactly like unused System Menu slots
    for col in range(4):
        x = GRID_X + col * (TILE_W + GAP_X)
        empty = render_empty_slot(TILE_W, TILE_H, ss=2)
        p.paste(empty, (x, EMPTY_ROW_Y))

    # central tray label
    p.text((W / 2, FOOTER_Y + 9), "Wii Menu", p.f("round", 700, 21), CYAN, anchor="ma", tracking=1.8)

    # footer buttons
    _round_button(p, 58, 492, 31, kind="wii")
    _sd_card(p, 124, 492)
    _round_button(p, W - 58, 492, 31, kind="mail")

    # time and date, on the silver like the original
    p.text((W / 2, 506), "Mon 16/11", p.f("ui", 700, 23), (96, 100, 102, 255), anchor="mm", tracking=0.3)

    # page arrow
    ax0, ay0, ax1, ay1 = ARROW_BOX
    p.paste(_arrow((ax1 - ax0, ay1 - ay0)), (ax0, ay0))

    return p.finish((W, H))


def _round_button(p: Pen, cx, cy, r, kind="wii"):
    p.ellipse((cx - r - 2, cy - r + 2, cx + r + 3, cy + r + 6), fill=(116, 120, 120, 50))
    body = Pen(int(r * 2 + 6), int(r * 2 + 6), ss=4)
    body.ellipse((2, 2, r * 2 + 2, r * 2 + 2), fill=(240, 241, 239, 255))
    shade = vertical_gradient(body.im.size, [
        (0.0, (255, 255, 255, 255)),
        (0.5, (246, 247, 245, 255)),
        (1, (206, 208, 206, 255)),
    ])
    m = mask_at(body.im.size, (2 * 4, 2 * 4, (r * 2 + 2) * 4, (r * 2 + 2) * 4), r * 4)
    body.im.alpha_composite(Image.composite(shade, Image.new("RGBA", shade.size, (0, 0, 0, 0)), m))
    p.paste(body.finish((int(r * 2 + 6), int(r * 2 + 6))), (cx - r - 3, cy - r - 3))
    p.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(86, 197, 223, 255), width=2)

    if kind == "wii":
        p.text((cx, cy + 1), "Wii", p.f("round", 700, r * 0.70), (132, 137, 139, 255), anchor="mm")
    else:
        ew, eh = r * 1.02, r * 0.70
        p.rrect((cx - ew / 2, cy - eh / 2, cx + ew / 2, cy + eh / 2), 2.5, fill=(152, 158, 160, 255))
        p.line(
            [(cx - ew / 2 + 1, cy - eh / 2 + 1), (cx, cy + eh * 0.08), (cx + ew / 2 - 1, cy - eh / 2 + 1)],
            (242, 243, 241, 255),
            2,
        )


def _sd_card(p: Pen, cx, cy):
    w, h = 25, 33
    p.rrect((cx - w / 2 + 1, cy - h / 2 + 2, cx + w / 2 + 1, cy + h / 2 + 2), 3, fill=(110, 118, 120, 45))
    p.rrect((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 3, fill=(250, 251, 250, 255), outline=(127, 190, 207, 255), width=1.4)
    p.polygon([(cx + w / 2 - 8, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy - h / 2 + 8)], fill=(127, 190, 207, 255))
    p.rrect((cx - w * 0.34, cy - h * 0.10, cx + w * 0.24, cy + h * 0.34), 1.5, fill=(43, 152, 199, 255))
    p.text((cx - w * 0.05, cy + h * 0.12), "SD", p.f("ui", 800, 6.4), (255, 255, 255, 255), anchor="mm")


def _arrow(size):
    w, h = size
    p = Pen(w, h, ss=4)
    p.rrect((1, 1, w - 1, h - 1), 12, fill=(234, 248, 252, 255), outline=(126, 204, 222, 255), width=1.6)
    p.rrect((3, 3, w - 3, h - 3), 10, fill=(255, 255, 255, 80))
    cx, cy = w / 2, h / 2
    p.polygon([(cx - 5, cy - 9), (cx + 7, cy), (cx - 5, cy + 9)], fill=(67, 176, 204, 255))
    return p.finish((w, h))


# --------------------------------------------------------------------------
# frame composition
# --------------------------------------------------------------------------


class TileCache:
    """Static channels are rendered once; the selected one is re-rendered."""

    rest = {}
    sel = {}
    pointer_img = None

    @classmethod
    def reset(cls):
        cls.rest.clear()
        cls.sel.clear()
        cls.pointer_img = None

    @classmethod
    def get_rest(cls, key):
        if key not in cls.rest:
            cls.rest[key] = render_channel(key, TILE_W, TILE_H, ss=2, glow=0, pad=12)
        return cls.rest[key]

    @classmethod
    def get_selected(cls, key, grow, glow, mii_frame=None):
        k = (key, round(grow, 3), round(glow, 2))
        if k not in cls.sel:
            cls.sel[k] = render_channel(
                key,
                TILE_W * grow,
                TILE_H * grow,
                ss=2,
                glow=glow,
                pad=max(14, 16 * grow),
                mii_frame=mii_frame,
            )
        return cls.sel[k]

    @classmethod
    def get_mii_rest(cls, mii_frame):
        return render_channel("mii", TILE_W, TILE_H, ss=2, glow=0, pad=12, mii_frame=mii_frame)

    @classmethod
    def get_pointer(cls):
        if cls.pointer_img is None:
            cls.pointer_img = render_pointer(POINTER_H)
        return cls.pointer_img


def compose_frame(base, selected_key, sel_amount, mii_frame, pointer_pos, pointer_alpha=1.0, pulse=0.0):
    frame = base.copy()
    for key, x, y in SLOTS:
        if key == selected_key:
            continue
        if key == "mii":
            tile = TileCache.get_mii_rest(mii_frame)
        else:
            tile = TileCache.get_rest(key)
        frame.alpha_composite(tile, (int(x - 12), int(y - 12)))

    if selected_key:
        grow = 1.0 + 0.05 * sel_amount + pulse
        tile = TileCache.get_selected(selected_key, grow, max(0.0, min(1.0, sel_amount)), mii_frame if selected_key == "mii" else None)
        x, y = next((x, y) for key, x, y in SLOTS if key == selected_key)
        cx, cy = x + TILE_W / 2, y + TILE_H / 2
        frame.alpha_composite(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)))

    if pointer_pos is not None:
        ptr = TileCache.get_pointer()
        if pointer_alpha < 1.0:
            ptr = _fade(ptr, pointer_alpha)
        ax, ay = pointer_anchor(ptr)
        frame.alpha_composite(ptr, (int(pointer_pos[0] - ax), int(pointer_pos[1] - ay)))
    return frame.convert("RGB")


def _fade(im, alpha):
    out = im.copy()
    a = out.getchannel("A").point(lambda v: int(v * alpha))
    out.putalpha(a)
    return out
