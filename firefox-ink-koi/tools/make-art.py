#!/usr/bin/env python3
"""Builds the theme's pictures from an ink painting on white.

    python3 tools/make-art.py              (uses art.webp, art.png or art.jpg)
    python3 tools/make-art.py <picture>

A second, optional picture, stroke.webp (or .png/.jpg), is a single brush
stroke that's laid along the top of the window.

The white paper becomes transparent and the ink becomes one flat ink
colour whose strength follows the painting, so the koi sit on the theme's
own paper in light mode and turn to pale ink on black in dark mode.
Anything clearly red, such as a seal, keeps the theme's vermilion.

If the picture is a sticker with a grey die-cut outline, the outline is
removed: everything light that touches the white surround is cleared,
while dark ink splatters there are kept.

Writes into chrome/ink-koi/:
  koi-pair-{light,dark}.png   the whole painting
  koi-wide-{light,dark}.png   the painting turned on its side, without the
                              seal and faded, to sit behind the new tab
                              page's search box
  seal.png                    the red seal on its own, for the tab strip
                              (only if the painting has one)
  stroke-{light,dark}.png     the brush stroke, faded (only with stroke.*)
and into wallpaper/:
  ink-koi-{light,dark}.png    2560x1600 wallpapers

Needs Pillow (pip install pillow).
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ART = ROOT / "chrome" / "ink-koi"
WALL = ROOT / "wallpaper"

PALETTES = {
    "light": {"paper": (243, 240, 232), "ink": (27, 26, 24)},
    "dark": {"paper": (20, 20, 19), "ink": (236, 232, 222)},
}
RED = (194, 58, 43)

WHITE = 245      # this light and lighter is paper
BLACK = 40       # this dark and darker is full-strength ink
REDNESS = 45     # how much redder than green and blue a pixel must be to count as seal
OUTLINE = 175    # around the surround, anything lighter than this is outline, not ink
OUTLINE_PX = 7   # how far in from the surround the outline reaches
MARGIN = 12      # padding left around the painting after cropping
WIDE_TURN = 90       # degrees the new-tab version is turned, anticlockwise
WIDE_STRENGTH = 0.30 # how strong its ink is (0..1), so the search box stays readable
STROKE_WHITE = 210   # the stroke's paper cutoff: lower than WHITE, which also
                     # clears the grey squares of a fake-transparency checkerboard
STROKE_STRENGTH = 0.16


def find(stem):
    for ext in ("webp", "png", "jpg", "jpeg"):
        if (ROOT / f"{stem}.{ext}").exists():
            return ROOT / f"{stem}.{ext}"
    return None


def find_picture():
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    return find("art") or sys.exit(
        "No picture: save it as firefox-ink-koi/art.webp (or .png/.jpg), or pass its path.")


def surround(grey):
    """The paper outside the painting: the white connected to the edges,
    grown by OUTLINE_PX so it takes in a sticker's outline."""
    w, h = grey.size
    mask = grey.point(lambda v: 255 if v >= 250 else 0)
    for corner in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        if mask.getpixel(corner) == 255:
            ImageDraw.floodfill(mask, corner, 128)
    outside = mask.point(lambda v: 255 if v == 128 else 0)
    return outside.filter(ImageFilter.MaxFilter(OUTLINE_PX * 2 + 1))


def separate(src, white=WHITE):
    """Returns (ink, red): two alpha masks the size of the picture."""
    rgb = src.convert("RGB")
    grey = rgb.convert("L")
    outside = surround(grey)
    w, h = rgb.size
    ink = Image.new("L", (w, h))
    red = Image.new("L", (w, h))
    px, gp, op = rgb.load(), grey.load(), outside.load()
    ip, rp = ink.load(), red.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            v = gp[x, y]
            if op[x, y] and v > OUTLINE:
                continue
            redness = r - max(g, b)
            if redness > REDNESS:
                rp[x, y] = min(255, redness * 2)
                continue
            a = (white - v) / (white - BLACK)
            ip[x, y] = int(255 * min(1.0, max(0.0, a)))
    return ink, red


def paint(ink, red, colour):
    """Flat ink colour through the ink mask, with vermilion on top."""
    out = Image.new("RGBA", ink.size, colour + (0,))
    out.putalpha(ink)
    seal = Image.new("RGBA", ink.size, RED + (0,))
    seal.putalpha(red)
    return Image.alpha_composite(out, seal)


def fade(img, strength):
    alpha = img.getchannel("A").point(lambda v: round(v * strength))
    img.putalpha(alpha)
    return img


def crop_box(mask, size):
    box = mask.getbbox()
    if not box:
        sys.exit("The picture looks blank: is it ink on white?")
    x0, y0, x1, y1 = box
    w, h = size
    return (max(0, x0 - MARGIN), max(0, y0 - MARGIN), min(w, x1 + MARGIN), min(h, y1 + MARGIN))


def save(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, optimize=True)
    print("wrote", path.relative_to(ROOT), f"{img.width}x{img.height}")


def main():
    pic = find_picture()
    src = Image.open(pic)
    ink, red = separate(src)

    both = Image.new("L", ink.size)
    both.paste(255, mask=ink.point(lambda v: 255 if v > 8 else 0))
    both.paste(255, mask=red.point(lambda v: 255 if v > 8 else 0))
    box = crop_box(both, ink.size)

    for mode, pal in PALETTES.items():
        art = paint(ink, red, pal["ink"]).crop(box)
        save(art, ART / f"koi-pair-{mode}.png")

        # Wallpaper: the painting low on the right of a sheet of paper.
        W, H = 2560, 1600
        scale = H * 0.82 / art.height
        big = art.resize((round(art.width * scale), round(art.height * scale)), Image.LANCZOS)
        wall = Image.new("RGBA", (W, H), pal["paper"] + (255,))
        wall.alpha_composite(big, (W - big.width - round(W * 0.07), H - big.height - round(H * 0.06)))
        save(wall.convert("RGB"), WALL / f"ink-koi-{mode}.png")

        # New tab: on its side, no seal, faded.
        bare = Image.new("L", ink.size)
        wide = paint(ink, bare, pal["ink"]).crop(crop_box(ink, ink.size))
        wide = fade(wide.rotate(WIDE_TURN, expand=True, resample=Image.BICUBIC), WIDE_STRENGTH)
        save(wide, ART / f"koi-wide-{mode}.png")

    stroke = find("stroke")
    if stroke:
        s_ink, _ = separate(Image.open(stroke), white=STROKE_WHITE)
        for mode, pal in PALETTES.items():
            img = paint(s_ink, Image.new("L", s_ink.size), pal["ink"]).crop(crop_box(s_ink, s_ink.size))
            save(fade(img, STROKE_STRENGTH), ART / f"stroke-{mode}.png")

    # The seal on its own, if there is one big enough to be a seal.
    seal_box = red.point(lambda v: 255 if v > 60 else 0).getbbox()
    if seal_box and (seal_box[2] - seal_box[0]) * (seal_box[3] - seal_box[1]) > 400:
        x0, y0, x1, y1 = seal_box
        pad = 3
        crop = (x0 - pad, y0 - pad, x1 + pad, y1 + pad)
        seal = Image.new("RGBA", ink.size, RED + (0,))
        seal.putalpha(red)
        save(seal.crop(crop), ART / "seal.png")
    else:
        (ART / "seal.png").unlink(missing_ok=True)
        print("no red seal found; the tab strip stays plain")


if __name__ == "__main__":
    main()
