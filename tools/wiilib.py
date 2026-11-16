"""Drawing toolkit for the Wii System Menu tribute assets.

Everything is drawn from primitives with Pillow. Coordinates are given in the
final image space; :class:`Pen` multiplies them by a supersampling factor so
rounded corners, thin borders and text stay crisp when the result is
downsampled with Lanczos.

The geometry and palette are measured against the original Wii System Menu
(2006): light grey dotted wallpaper, glossy white channel frames, silver
footer, cyan selection glow and the bright System Menu blue (#16b6dd).
"""

from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageSequence

TOOLS_DIR = Path(__file__).resolve().parent
ROOT_DIR = TOOLS_DIR.parent
FONT_DIR = TOOLS_DIR / "fonts"

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------

INK = (62, 68, 71, 255)          # system menu dark grey text
INK_SOFT = (110, 119, 123, 255)
INK_FAINT = (150, 158, 161, 255)
CYAN = (22, 182, 216, 255)       # original profile accent
CYAN_BRIGHT = (64, 208, 236, 255)
CYAN_PALE = (194, 237, 245, 255)
PAPER = (255, 255, 255, 255)
WALL = (243, 243, 241, 255)
FRAME_BORDER = (190, 192, 190, 255)
SILVER_TOP = (228, 229, 227, 255)
SILVER_BOTTOM = (198, 199, 197, 255)


# --------------------------------------------------------------------------
# Fonts
# --------------------------------------------------------------------------


@lru_cache(maxsize=256)
def font(family: str, weight: int, size: int) -> ImageFont.FreeTypeFont:
    """Load a variable font at a given weight.

    ``family`` is ``"ui"`` (Nunito Sans, neutral humanist: menu text) or
    ``"round"`` (Nunito, soft rounded: wordmarks and headings).
    """
    path = FONT_DIR / ("NunitoSans-Variable.ttf" if family == "ui" else "Nunito-Variable.ttf")
    f = ImageFont.truetype(str(path), max(1, int(size)))
    if family == "ui":
        f.set_variation_by_axes([weight, 100.0, 12.0, 0.0])
    else:
        f.set_variation_by_axes([weight])
    return f


def tracked_width(f: ImageFont.FreeTypeFont, text: str, tracking: float) -> float:
    if not text:
        return 0.0
    return sum(f.getlength(ch) for ch in text) + tracking * (len(text) - 1)


# --------------------------------------------------------------------------
# Pen
# --------------------------------------------------------------------------


class Pen:
    """Supersampled RGBA canvas."""

    def __init__(self, width: int, height: int, ss: int = 3, bg=(0, 0, 0, 0)):
        self.w = int(width)
        self.h = int(height)
        self.ss = ss
        self.im = Image.new("RGBA", (self.w * ss, self.h * ss), bg)
        self.d = ImageDraw.Draw(self.im)

    # -- coordinate helpers ------------------------------------------------
    def box(self, xy):
        return tuple(int(round(v * self.ss)) for v in xy)

    def pts(self, seq):
        return [(int(round(x * self.ss)), int(round(y * self.ss))) for x, y in seq]

    # -- shapes ------------------------------------------------------------
    def rect(self, xy, fill=None, outline=None, width=1):
        self.d.rectangle(self.box(xy), fill=fill, outline=outline, width=max(1, int(round(width * self.ss))))

    def rrect(self, xy, radius, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(
            self.box(xy),
            radius=radius * self.ss,
            fill=fill,
            outline=outline,
            width=max(1, int(round(width * self.ss))) if outline else 0,
        )

    def ellipse(self, xy, fill=None, outline=None, width=1):
        self.d.ellipse(self.box(xy), fill=fill, outline=outline, width=max(1, int(round(width * self.ss))))

    def line(self, seq, fill, width=1, joint="curve"):
        self.d.line(self.pts(seq), fill=fill, width=max(1, int(round(width * self.ss))), joint=joint)

    def polygon(self, seq, fill=None, outline=None):
        self.d.polygon(self.pts(seq), fill=fill, outline=outline)

    def arc(self, xy, start, end, fill, width=1):
        self.d.arc(self.box(xy), start, end, fill=fill, width=max(1, int(round(width * self.ss))))

    def text(self, xy, text, f, fill, anchor="la", tracking=0.0, stroke_width=0, stroke_fill=None):
        if not text:
            return
        x, y = xy
        if tracking:
            # Pillow has no letter spacing; draw glyph by glyph. Only used for
            # short all-caps labels, so the cost is irrelevant.
            if anchor[0] == "m":
                x -= tracked_width(f, text, tracking) / (2 * self.ss)
            elif anchor[0] == "r":
                x -= tracked_width(f, text, tracking) / self.ss
            for ch in text:
                self.d.text(
                    (x * self.ss, y * self.ss),
                    ch,
                    font=f,
                    fill=fill,
                    anchor="l" + anchor[1],
                    stroke_width=stroke_width,
                    stroke_fill=stroke_fill,
                )
                x += (f.getlength(ch) + tracking) / self.ss
        else:
            self.d.text(
                (x * self.ss, y * self.ss),
                text,
                font=f,
                fill=fill,
                anchor=anchor,
                stroke_width=stroke_width,
                stroke_fill=stroke_fill,
            )

    def f(self, family, weight, size):
        """Font at final-space ``size``, rendered at the pen's resolution."""
        return font(family, weight, int(round(size * self.ss)))

    def fill_gradient(self, stops):
        g = vertical_gradient(self.im.size, stops)
        self.im.alpha_composite(g)

    def fill_image(self, im):
        self.im.alpha_composite(im.resize(self.im.size, Image.BICUBIC))

    def fill_rounded_gradient(self, xy, radius, stops):
        g = vertical_gradient(self.im.size, stops)
        mask = Image.new("L", self.im.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            tuple(int(round(v * self.ss)) for v in xy), radius=radius * self.ss, fill=255
        )
        self.im.alpha_composite(Image.composite(g, Image.new("RGBA", self.im.size, (0, 0, 0, 0)), mask))

    def textsize(self, text, f, tracking=0.0):
        if tracking:
            return tracked_width(f, text, tracking) / self.ss, f.size / self.ss
        box = self.d.textbbox((0, 0), text, font=f)
        return (box[2] - box[0]) / self.ss, (box[3] - box[1]) / self.ss

    # -- composition -------------------------------------------------------
    def paste(self, im, xy):
        """Paste a final-space (1x) image at final-space coordinates."""
        im = im.convert("RGBA")
        if im.size != (im.width, im.height):
            raise ValueError("bad image size")
        im = im.resize((max(1, im.width * self.ss), max(1, im.height * self.ss)), Image.LANCZOS)
        self.im.alpha_composite(im, (int(round(xy[0] * self.ss)), int(round(xy[1] * self.ss))))

    def paste_ss(self, im, xy):
        """Paste an image that is already at pen resolution."""
        self.im.alpha_composite(im.convert("RGBA"), (int(xy[0]), int(xy[1])))

    def paste_masked(self, im, xy, mask):
        """Paste ``im`` at final-space ``xy``, keeping only ``mask`` (1x or ss)."""
        im = im.convert("RGBA")
        if im.size != self.im.size:
            layer = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
            layer.paste(im, (int(round(xy[0] * self.ss)), int(round(xy[1] * self.ss))))
        else:
            layer = im
        if mask.size != self.im.size:
            mask = mask.resize(self.im.size, Image.LANCZOS)
        self.im.alpha_composite(Image.composite(layer, Image.new("RGBA", self.im.size, (0, 0, 0, 0)), mask))

    def paste_masked_final(self, im, xy, mask):
        """Like :meth:`paste_masked`, but ``im`` is in final-space pixels."""
        im = im.convert("RGBA").resize(
            (max(1, im.width * self.ss), max(1, im.height * self.ss)), Image.LANCZOS
        )
        self.paste_masked(im, xy, mask)

    def finish(self, size=None, resample=Image.LANCZOS):
        out = self.im
        if size is not None and tuple(size) != out.size:
            out = out.resize((int(size[0]), int(size[1])), resample)
        return out

    def layer(self):
        return self.im


# --------------------------------------------------------------------------
# Gradients, masks, shadows
# --------------------------------------------------------------------------


def vertical_gradient(size, stops):
    """``stops`` is a list of ``(position_0_to_1, (r, g, b, a))``."""
    w, h = int(size[0]), int(size[1])
    col = Image.new("RGBA", (1, h))
    px = col.load()
    stops = sorted(stops)
    for y in range(h):
        t = y / max(1, h - 1)
        c = stops[-1][1]
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1 or (i == len(stops) - 2 and t > p1):
                f = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
                f = min(1.0, max(0.0, f))
                c = tuple(int(round(c0[k] + (c1[k] - c0[k]) * f)) for k in range(4))
                break
        px[0, y] = c
    return col.resize((w, h), Image.NEAREST)


def radial_glow(size, center, radius, color, opacity=255):
    """Soft radial light, used for channel artwork backgrounds."""
    w, h = int(size[0]), int(size[1])
    scale = 0.25
    sw, sh = max(2, int(w * scale)), max(2, int(h * scale))
    img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = center[0] * scale, center[1] * scale
    r = radius * scale
    steps = 24
    for i in range(steps, 0, -1):
        f = i / steps
        a = int(opacity * (1 - f) ** 1.8)
        d.ellipse((cx - r * f, cy - r * f, cx + r * f, cy + r * f), fill=color[:3] + (a,))
    img = img.filter(ImageFilter.GaussianBlur(sw / 16))
    return img.resize((w, h), Image.BICUBIC)


def rounded_mask(size, box, radius, ss=2):
    w, h = int(size[0]), int(size[1])
    m = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle(
        tuple(int(round(v * ss)) for v in box),
        radius=radius * ss,
        fill=255,
    )
    return m.resize((w, h), Image.LANCZOS)


def shadow_image(size, box, radius, dy=3, blur=4, color=(30, 40, 44), opacity=64, ss=2):
    w, h = int(size[0]), int(size[1])
    m = rounded_mask(size, (box[0], box[1] + dy, box[2], box[3] + dy), radius, ss=ss)
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    tint = Image.new("RGBA", (w, h), color[:3] + (opacity,))
    tint.putalpha(ImageChops.multiply(m, Image.new("L", (w, h), opacity)))
    return tint


def glow_image(size, box, radius, color=CYAN_BRIGHT, spread=7, opacity=170, ring=2.2, ring_opacity=230):
    """Cyan halo used for the selected channel."""
    w, h = int(size[0]), int(size[1])
    ss = 2
    hi = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(hi)
    r = tuple(int(round(v * ss)) for v in box)
    d.rounded_rectangle(r, radius=radius * ss, outline=color[:3] + (opacity,), width=max(2, int(spread * ss)))
    hi = hi.filter(ImageFilter.GaussianBlur(spread * ss * 0.75))
    hi = hi.resize((w, h), Image.LANCZOS)

    ring_im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ring_im)
    d.rounded_rectangle(box, radius=radius, outline=color[:3] + (ring_opacity,), width=max(1, int(round(ring))))
    return Image.alpha_composite(hi, ring_im)


# --------------------------------------------------------------------------
# Texture
# --------------------------------------------------------------------------


def wallpaper(size, base=WALL, dot=(224, 224, 221), step=7, dot_alpha=130):
    """The System Menu wallpaper: a very light wall with a fine dot grid."""
    w, h = int(size[0]), int(size[1])
    img = vertical_gradient((w, h), [(0, base[:3] + (255,)), (1, (248, 248, 246, 255))])
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(step // 2, h, step):
        for x in range(step // 2, w, step):
            d.point((x, y), fill=dot[:3] + (dot_alpha,))
    return Image.alpha_composite(img, layer)


def pinstripes(size, color=(210, 210, 208, 90), step=2):
    w, h = int(size[0]), int(size[1])
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(0, h, step):
        d.line((0, y, w, y), fill=color)
    return layer


# --------------------------------------------------------------------------
# Mii frames
# --------------------------------------------------------------------------


def load_mii_frames(path, every=1, height=None):
    """Load a Mii animation, normalising frames to one transparent canvas.

    The repository's Mii GIFs are the single source of truth for the avatar;
    nothing here redraws or restyles the character.
    """
    src = Image.open(path)
    frames = []
    for i, frame in enumerate(ImageSequence.Iterator(src)):
        if i % every:
            continue
        frames.append(frame.convert("RGBA"))
    # Union bounding box over all frames keeps the character anchored.
    union = None
    for f in frames:
        bbox = f.getbbox()
        if bbox is None:
            continue
        union = bbox if union is None else (
            min(union[0], bbox[0]), min(union[1], bbox[1]),
            max(union[2], bbox[2]), max(union[3], bbox[3]),
        )
    if union is None:
        return frames
    out = [f.crop(union) for f in frames]
    if height:
        scale = height / out[0].height
        size = (max(1, round(out[0].width * scale)), int(height))
        out = [f.resize(size, Image.LANCZOS) for f in out]
    return out


def mii_head(path, size=160):
    """Crop the head of the Mii portrait, for small badges and notes."""
    im = Image.open(path).convert("RGBA")
    bbox = im.getbbox()
    im = im.crop(bbox)
    # The portrait is a full-body pose; the head sits in the upper middle.
    head = im.crop((int(im.width * 0.285), 0, int(im.width * 0.94), int(im.height * 0.465)))
    head = head.crop(head.getbbox())
    scale = size / head.height
    return head.resize((round(head.width * scale), size), Image.LANCZOS)


# --------------------------------------------------------------------------
# Timing
# --------------------------------------------------------------------------


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_in_out(t):
    t = clamp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def keyframe_xy(frames, t):
    """Piecewise smooth interpolation over ``[(time, (x, y)), ...]``."""
    if t <= frames[0][0]:
        return frames[0][1]
    if t >= frames[-1][0]:
        return frames[-1][1]
    for (t0, p0), (t1, p1) in zip(frames, frames[1:]):
        if t0 <= t <= t1:
            f = ease_in_out((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
            return (p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f)
    return frames[-1][1]


def keyframe_value(frames, t):
    if t <= frames[0][0]:
        return frames[0][1]
    if t >= frames[-1][0]:
        return frames[-1][1]
    for (t0, v0), (t1, v1) in zip(frames, frames[1:]):
        if t0 <= t <= t1:
            f = smooth((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
            return v0 + (v1 - v0) * f
    return frames[-1][1]


# --------------------------------------------------------------------------
# Image export
# --------------------------------------------------------------------------


def save_png(im, path, colors=256):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if colors and im.mode == "RGBA":
        im = im.quantize(colors=colors, method=Image.MEDIANCUT)
        im = im.convert("RGBA")
    im.save(path, optimize=True)
    return path


def save_gif(frames, path, duration=100, colors=96, dither=Image.Dither.NONE):
    """Save RGB frames with one shared palette, so colours never flicker."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not frames:
        raise ValueError("no frames")
    # Build the palette from a montage of every 4th frame: stable and neutral.
    sample = frames[:: max(1, len(frames) // 6)]
    montage = Image.new("RGB", (frames[0].width, frames[0].height * len(sample)))
    for i, f in enumerate(sample):
        montage.paste(f, (0, i * frames[0].height))
    palette = montage.quantize(colors=colors, method=Image.MEDIANCUT)
    qframes = [f.quantize(palette=palette, dither=dither) for f in frames]
    qframes[0].save(
        path,
        save_all=True,
        append_images=qframes[1:],
        duration=duration,
        loop=0,
        optimize=True,
        disposal=1,
    )
    return path


def mask_at(size, box, radius):
    """Anti-aliased rounded-rectangle mask at exactly ``size`` pixels."""
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle(tuple(int(round(v)) for v in box), radius=radius, fill=255)
    return m
