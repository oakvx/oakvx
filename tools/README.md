# Wii System Menu asset pipeline

Every graphic in the profile README is generated from code in this directory.
There are no downloaded images and no AI-generated artwork: the channel art,
menu, footer, screens and headings are drawn with [Pillow](https://python-pillow.org/),
and the Mii is the repository's own avatar from `assets/mii/`, reused unchanged.

```
tools/
  build_wii_assets.py   # CLI: builds everything into assets/wii/
  validate_readme.py    # static checks for assets, anchors, HTML and tables
  wiilib.py             # supersampled pen, palette, fonts, shadows, GIF export
  wii_channels.py       # the eight channel artworks, frames, pointer
  wii_menu.py           # System Menu screen, footer and animation frames
  wii_screens.py        # Mii Channel, Settings, Message Board, Internet, contact
  fonts/                # Nunito + Nunito Sans (SIL OFL 1.1) and licence texts
```

## Build

```bash
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements.txt
.venv/bin/python tools/build_wii_assets.py
.venv/bin/python tools/validate_readme.py
```

Options:

```bash
# one group only: channels | headings | screens | mii | menu | all
python tools/build_wii_assets.py -o channels

# static frames only, skip the GIFs
python tools/build_wii_assets.py --no-animation
```

The whole build takes ~10 s and writes ~2 MB into `assets/wii/`.

## Design notes

- **Geometry** follows the original System Menu: a 4×3 channel lattice, 3:2
  channel frames, glossy white borders, a dotted wallpaper, a silver footer
  with a central tray, a cyan seam and round Wii / Message Board buttons.
- **Palette**: `#F3F3F1` wall, `#16B6DD` system blue, warm greys, silver
  hardware. Channel art is allowed its own accent (navy for YAG, salon cyan,
  brat lime, PlayStation blue) because real Wii channels did the same.
- **Type**: Nunito and Nunito Sans (SIL Open Font License) approximate the
  humanist, slightly rounded system UI of the console. See `fonts/OFL-*.txt`.
- **Animation**: the pointer path and selection windows are keyframed in
  `build_wii_assets.py`. Frames are rendered as RGB, quantised to one shared
  palette, and the GIF encoder merges unchanged frames — the 8.4 s menu loop is
  ~380 KB, the calm Mii Channel loop ~200 KB.
- **Accessibility**: every generated image has a text description in the
  README; the two animations also ship a static frame used through
  `<picture media="(prefers-reduced-motion: reduce)">`.
- The animated menu has no clickable regions. On GitHub that is impossible, so
  the README pairs it with a separate table of individually linked channels.

## Editing

Channel names, links and alternate text live in `CHANNELS` in
`wii_channels.py`. Section headings are listed in `HEADINGS` in
`wii_screens.py`. Menu timing is in `POINTER_PATH` / `SELECT_WINDOWS` in
`build_wii_assets.py`. Rebuild and re-run the validator after any change.
