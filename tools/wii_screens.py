"""Full-screen Wii scenes: Mii Channel, Wii Settings, Message Board, Internet
Channel and the contact note. Also section headings."""

from __future__ import annotations


from PIL import Image, ImageDraw, ImageFilter

from wiilib import (
    CYAN,
    INK,
    Pen,
    glow_image,
    mask_at,
    radial_glow,
    shadow_image,
)
from wii_channels import MII_HEAD, render_heading

# --------------------------------------------------------------------------
# shared chrome
# --------------------------------------------------------------------------


def _bg(W, H, top=(255, 255, 255, 255), bottom=(230, 241, 244, 255), dots=(170, 200, 207, 40)):
    p = Pen(W, H, ss=2)
    p.fill_gradient([(0, top), (0.65, (247, 252, 253, 255)), (1, bottom)])
    dd = ImageDraw.Draw(p.im)
    step = 7 * p.ss
    for y in range(step, H * p.ss, step):
        for x in range(step, W * p.ss, step):
            dd.point((x, y), fill=dots)
    return p


def _wordmark(p: Pen, x, y, text, size=30, color=(38, 56, 62, 255), accent=(20, 150, 181, 255)):
    p.text((x, y), text, p.f("round", 800, size), color, anchor="ls")
    p.rrect((x, y + 8, x + 46, y + 12), 2, fill=accent)


def _icon_circle(p: Pen, cx, cy, r):
    p.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(247, 251, 252, 255), outline=(198, 220, 226, 255), width=1.5)


def icon_monitor(p, cx, cy, s, color=(34, 150, 180, 255), width=2.0):
    p.rrect((cx - s * 0.5, cy - s * 0.38, cx + s * 0.5, cy + s * 0.22), s * 0.08, outline=color, width=width)
    p.line([(cx - s * 0.18, cy + s * 0.42), (cx + s * 0.18, cy + s * 0.42)], color, width)
    p.line([(cx, cy + s * 0.22), (cx, cy + s * 0.42)], color, width)


def icon_code(p, cx, cy, s, color=(34, 150, 180, 255), width=2.0):
    p.line([(cx - s * 0.14, cy - s * 0.30), (cx - s * 0.46, cy), (cx - s * 0.14, cy + s * 0.30)], color, width, joint="curve")
    p.line([(cx + s * 0.14, cy - s * 0.30), (cx + s * 0.46, cy), (cx + s * 0.14, cy + s * 0.30)], color, width, joint="curve")
    p.line([(cx + s * 0.10, cy - s * 0.34), (cx - s * 0.10, cy + s * 0.34)], color, width)


def icon_db(p, cx, cy, s, color=(34, 150, 180, 255), width=2.0):
    p.ellipse((cx - s * 0.4, cy - s * 0.44, cx + s * 0.4, cy - s * 0.16), outline=color, width=width)
    p.line([(cx - s * 0.4, cy - s * 0.3), (cx - s * 0.4, cy + s * 0.3)], color, width)
    p.line([(cx + s * 0.4, cy - s * 0.3), (cx + s * 0.4, cy + s * 0.3)], color, width)
    p.arc((cx - s * 0.4, cy + s * 0.18, cx + s * 0.4, cy + s * 0.44), 0, 180, fill=color, width=int(width))
    p.arc((cx - s * 0.4, cy - s * 0.02, cx + s * 0.4, cy + s * 0.24), 0, 180, fill=color, width=int(width))


def icon_chip(p, cx, cy, s, color=(34, 150, 180, 255), width=2.0):
    p.rrect((cx - s * 0.36, cy - s * 0.36, cx + s * 0.36, cy + s * 0.36), s * 0.10, outline=color, width=width)
    for i in range(3):
        off = -s * 0.22 + i * s * 0.22
        p.line([(cx + off, cy - s * 0.36), (cx + off, cy - s * 0.52)], color, width)
        p.line([(cx + off, cy + s * 0.36), (cx + off, cy + s * 0.52)], color, width)
        p.line([(cx - s * 0.36, cy + off), (cx - s * 0.52, cy + off)], color, width)
        p.line([(cx + s * 0.36, cy + off), (cx + s * 0.52, cy + off)], color, width)
    p.ellipse((cx - s * 0.1, cy - s * 0.1, cx + s * 0.1, cy + s * 0.1), fill=color)


def icon_desktop(p, cx, cy, s, color=(34, 150, 180, 255), width=2.0):
    p.rrect((cx - s * 0.46, cy - s * 0.36, cx + s * 0.46, cy + s * 0.22), s * 0.08, outline=color, width=width)
    p.line([(cx - s * 0.54, cy + s * 0.42), (cx + s * 0.54, cy + s * 0.42)], color, width)
    p.line([(cx, cy + s * 0.22), (cx, cy + s * 0.42)], color, width)


def icon_check(p, cx, cy, s, color=(34, 150, 180, 255), width=2.0):
    p.rrect((cx - s * 0.42, cy - s * 0.42, cx + s * 0.42, cy + s * 0.42), s * 0.12, outline=color, width=width)
    p.line([(cx - s * 0.2, cy + s * 0.02), (cx - s * 0.03, cy + s * 0.2), (cx + s * 0.24, cy - s * 0.2)], color, width + 0.4, joint="curve")


# --------------------------------------------------------------------------
# Mii Channel screen
# --------------------------------------------------------------------------


def mii_plaza_background(W=1000, H=560):

    p = _bg(W, H, (255, 255, 255, 255), (229, 245, 250, 255), (150, 195, 207, 30))
    floor_y = H * 0.70
    # plaza floor
    p.rect((0, floor_y, W, H), fill=(248, 253, 254, 190))
    p.ellipse((-W * 0.22, floor_y - 52, W * 1.22, H * 2.1), fill=(255, 255, 255, 190))
    p.ellipse((-W * 0.22, floor_y - 52, W * 1.22, H * 2.1), outline=(176, 219, 228, 105), width=1.6)
    # soft perspective grid on the floor
    vx, vy = W / 2, floor_y - 40
    for i in range(-6, 7):
        x = W / 2 + i * 105
        p.line([(vx, vy), (x, H + 40)], fill=(190, 226, 234, 30), width=1)
    for k in range(1, 4):
        y = floor_y + (H - floor_y) * (k / 3.2)
        p.ellipse((W * 0.10 - k * 26, y - 16, W * 0.90 + k * 26, y + 16), outline=(190, 226, 234, 26), width=1)
    # gentle light behind the avatar
    p.fill_image(radial_glow((W * p.ss, H * p.ss), (W * 0.42 * p.ss, H * 0.52 * p.ss), W * 0.28 * p.ss, (206, 240, 247), 70).resize((W, H)))
    # wordmark, same language as the section headings
    p.rrect((40, 34, 46, 66), 3, fill=(22, 182, 216, 255))
    p.text((62, 64), "Mii Channel", p.f("round", 800, 34), (44, 62, 68, 255), anchor="ls", tracking=-0.6)
    p.text((64, 90), "PERSONAL MII", p.f("ui", 800, 13), (24, 148, 179, 255), anchor="ls", tracking=2.2)
    p.text((66, H - 32), "oakvx · my own Mii, unchanged", p.f("ui", 600, 13.5), (112, 136, 143, 255), anchor="ls", tracking=0.2)
    return p.finish((W, H))


def compose_mii_screen(bg, frame, x=500, floor_y=505, height=380):
    im = bg.copy()
    f = frame.copy()
    scale = height / f.height
    f = f.resize((max(1, round(f.width * scale)), int(height)), Image.LANCZOS)
    # shadow on the plaza
    sh_w, sh_h = int(f.width * 0.95), 34
    pad_s = 24
    sh = Image.new("RGBA", (sh_w + 2 * pad_s, sh_h + 2 * pad_s), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((pad_s, pad_s, pad_s + sh_w, pad_s + sh_h), fill=(70, 100, 108, 55))
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    im.alpha_composite(sh, (int(x - sh.width / 2), int(floor_y - sh_h / 2 - pad_s)))
    im.alpha_composite(f, (int(x - f.width / 2), int(floor_y - f.height)))
    return im


# --------------------------------------------------------------------------
# Wii Settings screen
# --------------------------------------------------------------------------


SETTINGS_ROWS = [
    ("monitor", "Web", "HTML · CSS · JavaScript · React · TypeScript"),
    ("code", "Backend & AI", "Node.js · Express · PHP · C17 · CMake · libcurl"),
    ("db", "Data", "PostgreSQL · MySQL · SQL Server (T-SQL)"),
    ("chip", "Reverse engineering", "Python · ELF / Orbis / PSF / NID · Ghidra"),
    ("desktop", "Systems", "Windows · Active Directory · PLC basics"),
    ("check", "Principles", "Local-first · Explicit states · Evidence first"),
]


def render_settings(W=1000, H=540):
    p = _bg(W, H, (255, 255, 255, 255), (239, 246, 247, 255), (150, 175, 181, 26))
    # header
    p.rrect((54, 30, 59, 60), 2, fill=(22, 182, 216, 255))
    p.text((70, 62), "Wii Settings", p.f("round", 800, 36), (52, 62, 65, 255), anchor="ls", tracking=-0.8)
    p.text((70, 88), "SYSTEM · TOOLBOX · PRINCIPLES", p.f("ui", 800, 13.5), (99, 138, 148, 255), anchor="ls", tracking=1.6)
    p.text((W - 54, 84), "Point at a panel with the Wii Remote", p.f("ui", 500, 13), (154, 168, 172, 255), anchor="rs")

    left, right = 54, W - 54
    gap = 22
    row_w = (right - left - gap) / 2
    row_h = 98
    top = 122
    vgap = 18
    for i, (icon, title, sub) in enumerate(SETTINGS_ROWS):
        col, row = i % 2, i // 2
        x = left + col * (row_w + gap)
        y = top + row * (row_h + vgap)
        box = (x, y, x + row_w, y + row_h)
        selected = i == 0
        if selected:
            p.paste_ss(
                glow_image(
                    p.im.size,
                    tuple(v * p.ss for v in box),
                    14 * p.ss,
                    spread=7 * p.ss,
                    opacity=150,
                    ring=0.01 * p.ss,
                    ring_opacity=0,
                ),
                (0, 0),
            )
        # shadow + white row
        p.paste_ss(
            shadow_image(
                p.im.size,
                tuple(v * p.ss for v in box),
                14 * p.ss,
                dy=3 * p.ss,
                blur=4 * p.ss,
                opacity=44,
                ss=1,
            ),
            (0, 0),
        )
        p.fill_rounded_gradient(box, 14, [(0, (255, 255, 255, 255)), (1, (248, 250, 250, 255))])
        if selected:
            p.rrect(box, 14, outline=(64, 196, 226, 255), width=2.2)
        else:
            p.rrect(box, 14, outline=(196, 204, 205, 255), width=1.4)

        cx, cy = x + 47, y + row_h / 2
        _icon_circle(p, cx, cy, 28)
        fn = {
            "monitor": icon_monitor,
            "code": icon_code,
            "db": icon_db,
            "chip": icon_chip,
            "desktop": icon_desktop,
            "check": icon_check,
        }[icon]
        fn(p, cx, cy, 28, (32, 157, 186, 255), 2.0)
        p.text((x + 88, y + 42), title, p.f("ui", 800, 20), (56, 66, 69, 255), anchor="ls")
        p.text((x + 88, y + 66), sub, p.f("ui", 500, 13.2), (116, 130, 134, 255), anchor="ls")

    # footer hints
    fy = H - 44
    p.text((left, fy + 8), "Wii Menu", p.f("round", 700, 17), CYAN, anchor="ls")
    p.text((left + 92, fy + 8), "·  Back", p.f("ui", 600, 15), (135, 148, 151, 255), anchor="ls")
    _ab_button(p, W - 188, fy, "A", "Open")
    _ab_button(p, W - 96, fy, "B", "Back")
    return p.finish((W, H))


def _ab_button(p: Pen, x, y, letter, label):
    p.ellipse((x, y, x + 30, y + 30), fill=(252, 253, 253, 255), outline=(186, 204, 208, 255), width=1.2)
    p.text((x + 15, y + 15), letter, p.f("ui", 800, 13), (110, 126, 130, 255), anchor="mm")
    p.text((x + 38, y + 17), label, p.f("ui", 600, 15), (128, 141, 145, 255), anchor="lm")


# --------------------------------------------------------------------------
# Message Board screen
# --------------------------------------------------------------------------


BOARD_NOTES = [
    ("NOW BUILDING", "YAG v0.1.0-rc.2", "C17 AI gateway · web console"),
    ("IN TESTING", "synk 1.2.0-rc.6", "Salon booking · Calendar · WhatsApp"),
    ("RESEARCH", "middleManPS4 v0.17", "PS4 payloads · offline analysis"),
    ("CREATIVE", "Brat Animator", "Local-first lyric-video studio"),
    ("STUDYING", "Computer Engineering", "UNIMORE · from 2026"),
    ("DESIGN", "Portfolio & demos", "oakvx.github.io · case studies"),
]


def _note_card(w, h, category, title, desc):
    pad = 16
    p = Pen(w, h, ss=4)
    body = (0, pad, w, h)
    p.fill_rounded_gradient(body, 9, [(0, (255, 255, 255, 255)), (1, (252, 252, 250, 255))])
    p.rrect(body, 9, outline=(190, 202, 205, 255), width=1.4)
    p.ellipse((w / 2 - 13, 0, w / 2 + 13, 26), fill=(222, 76, 60, 255))
    p.ellipse((w / 2 - 7, 6, w / 2 + 1, 14), fill=(255, 255, 255, 80))
    # washi tape strip, like a note stuck to the board
    p.rrect((20, pad + 16, 22 + 92, pad + 34), 4, fill=(226, 246, 250, 255))
    p.text((28, pad + 30), category, p.f("ui", 800, 12.5), (44, 141, 161, 255), anchor="ls", tracking=1.4)
    p.text((22, pad + 62), title, p.f("ui", 800, 19 if len(title) < 20 else 16.5), (48, 60, 64, 255), anchor="ls", tracking=-0.3)
    p.text((22, pad + 90), desc, p.f("ui", 500, 12.5), (120, 134, 138, 255), anchor="ls")
    return p.finish((w, h))


def render_message_board(W=1000, H=540):
    p = _bg(W, H, (255, 255, 253, 255), (238, 245, 247, 255), (140, 175, 184, 34))
    p.text((54, 56), "Message Board", p.f("round", 800, 27), (42, 58, 66, 255), anchor="ls")
    p.text((54, 80), "CURRENT PROJECTS · RELEASES", p.f("ui", 800, 12), (88, 136, 150, 255), anchor="ls", tracking=1.4)
    p.text((W / 2, 50), "Mon 16/11", p.f("ui", 700, 20), (100, 112, 116, 255), anchor="ms", tracking=0.2)
    p.polygon([(W - 84, 42), (W - 72, 54), (W - 84, 66)], fill=(116, 188, 205, 255))
    p.polygon([(34, 250), (22, 262), (34, 274)], fill=(206, 224, 229, 255))
    p.polygon([(W - 22, 250), (W - 34, 262), (W - 22, 274)], fill=(116, 188, 205, 255))

    note_w, note_h = 272, 158
    gap_x, gap_y = 26, 16
    grid_w = note_w * 3 + gap_x * 2
    x0 = (W - grid_w) / 2
    y0 = 108
    for i, (cat, title, desc) in enumerate(BOARD_NOTES):
        col, row = i % 3, i // 3
        x = x0 + (note_w + gap_x) * col
        y = y0 + row * (note_h + gap_y)
        card = _note_card(note_w, note_h, cat, title, desc)
        sh = Image.new("RGBA", (note_w + 10, note_h + 14), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((5, 20, note_w + 4, note_h + 9), radius=10, fill=(120, 136, 140, 48))
        sh = sh.filter(ImageFilter.GaussianBlur(4))
        p.paste(sh, (x - 5, y - 3))
        p.paste(card.rotate(-1.4 if i % 2 == 0 else 1.0, resample=Image.BICUBIC, expand=False), (x, y))

    # footer: silver bar with a cyan seam, like the System Menu
    fy = H - 58
    p.fill_rounded_gradient((0, fy, W, H), 0, [(0, (228, 229, 227, 255)), (0.5, (209, 210, 208, 255)), (1, (226, 227, 225, 255))])
    p.line([(0, fy + 1), (W, fy + 1)], (110, 198, 220, 210), 1.4)
    _round(p, 46, fy + 29, 22)
    _round(p, W - 46, fy + 29, 22)
    p.rrect((W - 58, fy + 23, W - 34, fy + 37), 1.5, fill=(154, 160, 162, 255))
    p.line([(W - 58, fy + 24), (W - 46, fy + 31), (W - 34, fy + 24)], (246, 247, 245, 255), 1.6)
    # calendar button
    p.rrect((90, fy + 16, 122, fy + 42), 2, fill=(252, 253, 252, 255), outline=(140, 150, 152, 255), width=1.2)
    p.rect((90, fy + 16, 122, fy + 22), fill=(120, 196, 212, 255))
    p.text((106, fy + 36), "16", p.f("ui", 700, 10), (120, 132, 136, 255), anchor="mm")
    p.text((W / 2, fy + 34), "Wii Message Board", p.f("round", 700, 18), (96, 102, 104, 255), anchor="mm", tracking=0.4)
    return p.finish((W, H))


def _round(p: Pen, cx, cy, r):
    p.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(250, 251, 250, 255), outline=(120, 196, 213, 255), width=1.8)
    p.text((cx, cy + 1), "Wii", p.f("round", 700, 10.5), (146, 154, 156, 255), anchor="mm")


# --------------------------------------------------------------------------
# Internet Channel
# --------------------------------------------------------------------------


def render_internet(W=1000, H=330):
    p = _bg(W, H, (250, 253, 253, 255), (226, 242, 247, 255), (150, 190, 200, 34))
    box = (36, 22, W - 36, H - 24)
    p.paste_ss(
        shadow_image(p.im.size, tuple(v * p.ss for v in box), 15 * p.ss, dy=4 * p.ss, blur=7 * p.ss, opacity=55, ss=1),
        (0, 0),
    )
    p.rrect(box, 15, fill=(252, 252, 250, 255), outline=(188, 198, 199, 255), width=1.4)
    p.rrect((box[0] + 2, box[1] + 2, box[2] - 2, box[3] - 2), 13, outline=(255, 255, 255, 220), width=1)

    # toolbar
    p.fill_rounded_gradient((44, 30, W - 44, 86), 11, [(0, (249, 250, 248, 255)), (1, (232, 236, 234, 255))])
    p.rect((52, 84, W - 52, 86), fill=(203, 209, 207, 255))
    # globe mark
    gx, gy, gr = 66, 58, 13
    p.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), fill=(28, 166, 196, 255))
    p.ellipse((gx - gr * 0.45, gy - gr, gx + gr * 0.45, gy + gr), outline=(255, 255, 255, 220), width=1.2)
    p.line([(gx - gr, gy), (gx + gr, gy)], (255, 255, 255, 220), 1.2)
    p.ellipse((gx - gr, gy - gr * 0.55, gx + gr, gy + gr * 0.55), outline=(255, 255, 255, 200), width=1.1)
    p.text((92, 57), "Internet Channel", p.f("round", 800, 21), (52, 66, 71, 255), anchor="ls")
    p.text((92, 74), "oakvx.github.io", p.f("ui", 600, 11), (122, 139, 144, 255), anchor="ls")

    # round browser buttons, like the console's chrome: reload, back, forward
    for i, glyph in enumerate(("reload", "back", "forward")):
        cx = W - 66 - (2 - i) * 32
        cy = 58
        p.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(255, 255, 255, 255), outline=(177, 193, 196, 255), width=1.2)
        if glyph == "reload":
            p.arc((cx - 6, cy - 6, cx + 6, cy + 6), 40, 330, fill=(88, 120, 128, 255), width=1.6)
            p.polygon([(cx + 5, cy - 8), (cx + 8, cy - 2), (cx + 2, cy - 2)], fill=(88, 120, 128, 255))
        elif glyph == "back":
            p.line([(cx + 4, cy - 6), (cx - 3, cy), (cx + 4, cy + 6)], (88, 120, 128, 255), 1.7, joint="curve")
        else:
            p.line([(cx - 4, cy - 6), (cx + 3, cy), (cx - 4, cy + 6)], (88, 120, 128, 255), 1.7, joint="curve")

    # address bar
    p.rrect((64, 96, W - 64, 132), 18, fill=(255, 255, 255, 255), outline=(180, 196, 199, 255), width=1.2)
    p.ellipse((78, 107, 92, 121), outline=(70, 150, 170, 255), width=1.3)
    p.line([(85, 107), (85, 121)], (70, 150, 170, 200), 1.1)
    p.text((102, 119), "https://oakvx.github.io", p.f("ui", 600, 14), (64, 84, 90, 255), anchor="ls")
    p.ellipse((W - 112, 100, W - 84, 128), fill=(28, 166, 196, 255))
    p.line([(W - 103, 114), (W - 94, 114)], (255, 255, 255, 255), 1.8)
    p.line([(W - 98, 109), (W - 93, 114), (W - 98, 119)], (255, 255, 255, 255), 1.6, joint="curve")

    # bookmarks side panel
    p.rect((52, 140, 268, 276), fill=(241, 245, 244, 255))
    p.line([(268, 140), (268, 276)], (208, 216, 215, 255), 1)
    p.text((68, 158), "BOOKMARKS", p.f("ui", 800, 9.5), (116, 137, 142, 255), anchor="ls", tracking=1.6)
    bookmarks = ["Portfolio", "Chi sono", "Fuori orario", "Case studies", "Demos", "Contact"]
    for i, label in enumerate(bookmarks):
        y = 180 + i * 16
        p.ellipse((70, y - 3.5, 77, y + 3.5), fill=(28, 166, 196, 235))
        p.text((86, y), label, p.f("ui", 600, 11.5), (66, 86, 92, 255), anchor="lm")

    # page
    p.rect((268, 140, W - 52, 276), fill=(255, 255, 255, 255))
    p.text((290, 166), "Gabriele Lucia", p.f("round", 800, 24), (46, 62, 68, 255), anchor="ls")
    p.text((290, 185), "Computer Engineering @ UNIMORE", p.f("ui", 600, 12.5), (96, 120, 126, 255), anchor="ls")
    p.text((290, 206), "Portfolio, case studies, demos and contact.", p.f("ui", 500, 12.5), (110, 128, 133, 255), anchor="ls")
    for i, (label, y) in enumerate((("oakvx.github.io", 230), ("github.com/oakvx", 247), ("gabrielelucia07@gmail.com", 264))):
        p.ellipse((292, y - 3, 298, y + 3), fill=(28, 166, 196, 220))
        p.text((306, y), label, p.f("ui", 600, 11.5), (40, 132, 156, 255), anchor="lm")
    # soft globe watermark
    gx, gy, gr = 858, 210, 44
    p.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), fill=(244, 251, 253, 255), outline=(174, 219, 230, 255), width=1.4)
    p.ellipse((gx - gr * 0.45, gy - gr, gx + gr * 0.45, gy + gr), outline=(174, 219, 230, 255), width=1.1)
    p.line([(gx - gr, gy), (gx + gr, gy)], (174, 219, 230, 255), 1.1)
    p.ellipse((gx - gr, gy - gr * 0.55, gx + gr, gy + gr * 0.55), outline=(174, 219, 230, 230), width=1.1)
    p.ellipse((gx - 22, gy - 20, gx - 2, gy + 8), fill=(196, 231, 206, 230))
    p.ellipse((gx + 8, gy - 26, gx + 30, gy - 2), fill=(196, 231, 206, 210))

    # browser status strip
    p.fill_rounded_gradient((44, 282, W - 44, 304), 5, [(0, (246, 247, 245, 255)), (1, (230, 233, 231, 255))])
    p.rect((52, 281, W - 52, 283), fill=(207, 214, 212, 255))
    p.ellipse((64, 289, 70, 295), fill=(70, 186, 210, 255))
    p.text((78, 296), "Done", p.f("ui", 500, 10), (116, 134, 139, 255), anchor="ls")
    p.text((W - 64, 296), "oakvx · Internet Channel", p.f("ui", 600, 10), (116, 134, 139, 255), anchor="rs")
    return p.finish((W, H))

# --------------------------------------------------------------------------
# Contact note
# --------------------------------------------------------------------------


def render_contact(W=1000, H=250):
    p = _bg(W, H, (255, 255, 253, 255), (242, 248, 249, 255), (150, 180, 188, 26))
    # paper
    box = (54, 30, W - 54, H - 30)
    p.paste_ss(
        shadow_image(p.im.size, tuple(v * p.ss for v in box), 16 * p.ss, dy=4 * p.ss, blur=6 * p.ss, opacity=52, ss=1),
        (0, 0),
    )
    p.fill_rounded_gradient(box, 16, [(0, (255, 255, 255, 255)), (1, (250, 251, 249, 255))])
    p.rrect(box, 16, outline=(196, 205, 206, 255), width=1.4)
    p.ellipse((96, 20, 128, 52), fill=(222, 76, 60, 255))
    p.ellipse((104, 27, 116, 39), fill=(255, 255, 255, 80))
    p.text((96, 124), "Got a project, a job or a weird idea?", p.f("round", 800, 30), (50, 62, 66, 255), anchor="ls")
    p.rrect((96, 150, 486, 200), 25, fill=(251, 254, 254, 255), outline=(78, 195, 217, 255), width=1.6)
    p.text((114, 181), "gabrielelucia07@gmail.com", p.f("ui", 700, 17.5), (22, 154, 182, 255), anchor="ls")
    p.ellipse((446, 158, 480, 192), fill=(22, 182, 216, 255))
    p.rrect((455, 168, 471, 182), 1.5, fill=(255, 255, 255, 255))
    p.line([(455, 169), (463, 175), (471, 169)], (22, 182, 216, 255), 1.4)
    if MII_HEAD is not None:
        # circular Mii badge, like the Mii Channel portrait frames
        bx, by, bs = W - 76 - 148, 36, 148
        p.ellipse((bx - 3, by + 2, bx + bs + 3, by + bs + 6), fill=(120, 136, 140, 45))
        p.ellipse((bx, by, bx + bs, by + bs), fill=(238, 249, 252, 255))
        hh = 118
        head = MII_HEAD.resize((round(MII_HEAD.width * hh / MII_HEAD.height), hh), Image.LANCZOS)
        mask = mask_at(p.im.size, tuple(v * p.ss for v in (bx + 8, by + 8, bx + bs - 8, by + bs - 8)), 9999)
        p.paste_masked_final(head, ((bx + bs / 2 - head.width / 2), by + 21), mask)
        p.ellipse((bx + 3, by + 3, bx + bs - 3, by + bs - 3), outline=(150, 214, 229, 255), width=2)
    return p.finish((W, H))


# --------------------------------------------------------------------------
# headings
# --------------------------------------------------------------------------

HEADINGS = [
    ("home-menu", "Home Menu"),
    ("mii-channel", "Mii Channel"),
    ("software-channels", "Software Channels"),
    ("wii-settings", "Wii Settings"),
    ("message-board", "Message Board"),
    ("internet-channel", "Internet Channel"),
    ("after-hours", "After Hours"),
]


def heading_images(out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, label in HEADINGS:
        light = render_heading(label, INK, CYAN, 48, ss=3)
        light.save(out_dir / f"{key}-light.png", optimize=True)
        dark = render_heading(label, (240, 245, 246, 255), (34, 190, 220, 255), 48, ss=3)
        dark.save(out_dir / f"{key}-dark.png", optimize=True)
