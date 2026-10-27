#!/usr/bin/env python3
"""Makes the style's small built-in assets, which build.py embeds.

    python3 tools/make-assets.py

Writes into assets/:
  liujianmaocao-latin.woff2   Liu Jian Mao Cao, cut down to Latin letters
                              and punctuation, for the new-chat greeting
  send-seal-{light,dark}.png  the send button: a round seal stamp with 送
                              ("send") in Ma Shan Zheng, in vermilion

Both fonts are from Google Fonts under the SIL Open Font License (copies of
the licence are in assets/). They're downloaded into tools/.cache the first
time. The results are committed, so this only needs running to change them.

Needs Pillow and fontTools with Brotli (pip install pillow fonttools brotli).
"""

import random
import urllib.request
from math import cos, pi, sin
from pathlib import Path

from fontTools import subset
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
CACHE = HERE / ".cache"
GF = "https://github.com/google/fonts/raw/main/ofl/"
FONTS = {"LiuJianMaoCao": "liujianmaocao/LiuJianMaoCao-Regular.ttf",
         "MaShanZheng": "mashanzheng/MaShanZheng-Regular.ttf"}

REDS = {"light": (194, 58, 43), "dark": (210, 74, 53)}
SIZE = 200          # the seal is drawn at this size and shown at about 36px
RING = 9            # ring thickness, before the wobble
WOBBLE = 1.6        # how far the ring's edge strays, in px
SPECKLE = 0.10      # share of the ink that's missing, as on a worn stamp
TILT = -4           # degrees


def fetch(name):
    path = CACHE / Path(FONTS[name]).name
    if not path.exists():
        CACHE.mkdir(exist_ok=True)
        print("downloading", FONTS[name])
        urllib.request.urlretrieve(GF + FONTS[name], path)
    lic = ASSETS / f"OFL-{name}.txt"
    if not lic.exists():
        urllib.request.urlretrieve(GF + FONTS[name].split("/")[0] + "/OFL.txt", lic)
    return path


def greeting_font():
    out = ASSETS / "liujianmaocao-latin.woff2"
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    font = subset.load_font(str(fetch("LiuJianMaoCao")), opts)
    sub = subset.Subsetter(opts)
    # Basic Latin, Latin-1, curly quotes, dashes and the ellipsis.
    sub.populate(unicodes=[*range(0x20, 0x7F), *range(0xA0, 0x100),
                           0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026])
    sub.subset(font)
    subset.save_font(font, str(out), opts)
    print("wrote", out.relative_to(HERE.parent), f"{out.stat().st_size // 1024} KB")


def noise(size, scale, seed):
    """Smooth random noise, 0..255, with blobs about `scale` px across."""
    rnd = random.Random(seed)
    small = max(2, size // scale)
    img = Image.new("L", (small, small))
    img.putdata([rnd.randrange(256) for _ in range(small * small)])
    return img.resize((size, size), Image.BICUBIC)


def ring_mask():
    S, c, R = SIZE, SIZE / 2, SIZE / 2 - 12
    rnd = random.Random(7)
    k = [rnd.uniform(0, 2 * pi) for _ in range(4)]
    def edge(r, t, phase):
        return r + WOBBLE * (sin(3 * t + k[phase]) + 0.6 * sin(7 * t + k[phase + 1]))
    pts = 360
    width = [RING * (1 + 0.25 * sin(2 * t + k[2]) + 0.12 * sin(5 * t)) for t in
             (2 * pi * i / pts for i in range(pts))]
    outer, inner = [], []
    for i in range(pts):
        t = 2 * pi * i / pts
        ro, ri = edge(R, t, 0), edge(R - width[i], t, 2)
        outer.append((c + ro * cos(t), c + ro * sin(t)))
        inner.append((c + ri * cos(t), c + ri * sin(t)))
    mask = Image.new("L", (S, S))
    d = ImageDraw.Draw(mask)
    d.polygon(outer, fill=255)
    d.polygon(inner, fill=0)
    return mask


def char_mask():
    S = SIZE
    font = ImageFont.truetype(str(fetch("MaShanZheng")), round(S * 0.6))
    mask = Image.new("L", (S, S))
    d = ImageDraw.Draw(mask)
    x0, y0, x1, y1 = d.textbbox((0, 0), "送", font=font)
    d.text(((S - (x1 - x0)) / 2 - x0, (S - (y1 - y0)) / 2 - y0), "送", font=font, fill=255)
    return mask


def seal():
    mask = ImageChops.lighter(ring_mask(), char_mask())
    mask = mask.filter(ImageFilter.GaussianBlur(0.6))
    # Worn-stamp texture: fine specks plus a few larger dry patches.
    fine = noise(SIZE, 3, 1).point(lambda v: 0 if v < 255 * SPECKLE else 255)
    dry = noise(SIZE, 40, 2).point(lambda v: 90 if v < 40 else 255)
    texture = ImageChops.multiply(fine, dry).filter(ImageFilter.GaussianBlur(0.5))
    mask = ImageChops.multiply(mask, texture)
    mask = mask.rotate(TILT, resample=Image.BICUBIC)
    for mode, red in REDS.items():
        img = Image.new("RGBA", (SIZE, SIZE), red + (0,))
        img.putalpha(mask.point(lambda v: round(v * 0.94)))
        out = ASSETS / f"send-seal-{mode}.png"
        img.save(out, optimize=True)
        print("wrote", out.relative_to(HERE.parent))


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    greeting_font()
    seal()
