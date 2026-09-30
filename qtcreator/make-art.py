#!/usr/bin/env python3
"""Builds bg-editor.png: art.jpg against the editor's right edge, its misty
aura faded into the Midnight background and its lake extended along the whole
bottom, with the starfield from make-stars.py on top.

    python3 make-art.py              (writes bg-editor.png and bg-editor@2x.png)
    python3 make-art.py --overleaf   (writes bg-overleaf.png and bg-overleaf@2x.png,
                                      for midnight-overleaf: stronger, and with
                                      the tree peeking in from the right)

Swap art.jpg for any picture and rerun. Uses macOS `sips` to read the image;
otherwise pure Python.
"""
import importlib.util, math, os, random, struct, subprocess, tempfile, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("stars", os.path.join(HERE, "make-stars.py"))
stars = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stars)

ART = os.path.join(HERE, "art.jpg")
CANVAS_W, CANVAS_H = 1400, 900   # logical px, pinned to the editor's bottom-right
ART_H = 1150                     # picture height (its top is cropped to fit); width follows
ART_BOTTOM = 0.965               # crop the picture below this (0..1 down; drops the signature)
CUT_RIGHT = 0.0                  # fraction of the picture hidden past the editor's right edge
# Logical px of mist and lake added right of the picture, so the tree can sit
# further from the editor's right edge; the picture's right side fades into it
EXTEND_RIGHT = 0
FADE_RIGHT = 50                  # logical px the picture blends into its edge colours over
EDGE_SOFT = 30                   # logical px the edge colours are smoothed over, up and down
OPACITY = 0.62                   # strength of the tree at its most visible
FADE_LEFT = 0.80                 # fraction of the picture's width the tree fades in over
FADE_TOP = 0.15                  # fraction of the canvas height that fades in at the top
# The pale misty "aura" behind the tree darkens into the editor background the
# further it is from the trunk; the trunk and blossoms keep their strength
TRUNK = (0.80, 0.55)             # centre of the tree in the picture (0..1)
AURA_FADE = 0.85                 # 0 = leave the mist alone, 1 = fade it out fully at the edges
AURA_REACH = 0.55                # how far from the trunk the mist stays bright
AURA_COLOUR = (26, 14, 52)       # dark violet the mist fades towards
# A soft lavender haze under everything that reaches left from the tree and
# tapers into the dark, so there's no sharp bright/dark split
HAZE_COLOUR = (58, 42, 112)
HAZE_MAX = 0.30                  # haze strength at the tree
HAZE_REACH = 750                 # logical px the haze extends left of the picture
HAZE_INTO = 0.45                 # fraction of the picture's width it ramps up over
# Left of the picture the lake is continued with short horizontal strips cut
# from the picture's own water, so it keeps the painted brush strokes
WATER_TOP = 0.77                 # where the water starts in the picture (0..1 down)
WATER_SOFT = 80                  # logical px over which the far shore fades in
LAKE_SOURCE = 0.40               # fraction of the picture's width the strips come from
LAKE_STRIP = (40, 140)           # strip length range, logical px
LAKE_BAND = (2, 7)               # strip height range, logical px
LAKE_OVERLAP = 18                # logical px strips cross-fade over
LAKE_BLEND = 160                 # logical px over which the real picture blends into the strips
LAKE_OPACITY = 0.32
LAKE_DARKEN = 0.85
LAKE_DETAIL = 0.65               # 1 = strips at full contrast, 0 = plain averaged water
# The generated water only keeps the strips' brightness, smeared sideways, so
# the ripple lines survive but reflections (vertical shapes) and blossom
# colours don't; then a soft mist is laid over it, thickest at the horizon
LAKE_SMEAR = 28                  # logical px the strips are smeared over, each side
MIST_COLOUR = (72, 58, 128)
MIST_MAX = 0.35                  # mist strength at the horizon
MIST_BOTTOM = 0.15               # mist strength at the bottom edge
BLOSSOM_BOOST = 0.6              # makes purple blossoms stand out more than the grey mist
TINT = (40, 20, 90)              # pulls the colours towards Midnight violet
TINT_AMOUNT = 0.25
DARKEN = 0.95


def read_png(path):
    """Minimal decoder for the 8-bit RGB/RGBA PNGs that sips writes."""
    data = open(path, "rb").read()
    pos, idat = 8, b""
    while pos < len(data):
        n, tag = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if tag == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
            assert depth == 8 and ctype in (2, 6), "unexpected PNG format"
        elif tag == b"IDAT":
            idat += body
        pos += 12 + n
    bpp = 3 if ctype == 2 else 4
    raw, stride = zlib.decompress(idat), w * bpp
    out, prev = bytearray(), bytearray(stride)
    for y in range(h):
        f, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1:   line[i] = (line[i] + a) & 255
            elif f == 2: line[i] = (line[i] + b) & 255
            elif f == 3: line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        out += line
        prev = line
    return w, h, bpp, out


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def load_art(height):
    if not os.path.exists(ART):
        raise SystemExit("art.jpg not found: save the picture you want as art.jpg next to "
                         "make-art.py (see README), then rerun.")
    with tempfile.TemporaryDirectory() as tmp:
        png = os.path.join(tmp, "art.png")
        subprocess.run(["sips", "--resampleHeight", str(height), "-s", "format", "png",
                        ART, "--out", png], check=True, capture_output=True)
        return read_png(png)


def lake_strips(width, top, bottom, period, scale, rng):
    """Returns bands of (first row, height, (source col A, source col B, weight of B) per column)."""
    bands, y = [], top
    ov = LAKE_OVERLAP * scale
    while y < bottom:
        band = rng.randint(*LAKE_BAND) * scale
        a_col, b_col, w = [0] * width, [0] * width, [0.0] * width
        x = 0
        seg = None
        while x < width:
            length = min(period, rng.randint(*LAKE_STRIP) * scale)
            src = rng.randint(0, period - length)
            for i in range(length):
                if x + i >= width:
                    break
                col = src + i
                if seg is not None and i < ov and seg[1] + i < period:
                    # cross-fade from the previous strip's continuation into this one
                    a_col[x + i], b_col[x + i], w[x + i] = seg[1] + i, col, (i + 1) / (ov + 1)
                else:
                    a_col[x + i] = b_col[x + i] = col
            seg = (x, src + length)
            x += length
        bands.append((y, band, (a_col, b_col, w)))
        y += band
    bands.append((y, 1, bands[-1][2]))
    return bands


def build(scale):
    W, H = CANVAS_W * scale, CANVAS_H * scale
    aw, ah, bpp, art = load_art(ART_H * scale)
    ext = EXTEND_RIGHT * scale
    x0 = W - ext - int(aw * (1 - CUT_RIGHT))
    xr = x0 + aw                             # the picture's right edge
    top = int(ART_BOTTOM * ah) - H           # picture row shown at the canvas top
    water = int(WATER_TOP * ah)
    period = int(aw * LAKE_SOURCE)
    blend = LAKE_BLEND * scale
    bands = lake_strips(x0 + ext, max(water, top), top + H, period, scale, random.Random(stars.SEED))
    band_of = {}
    for n, (by, bh, _) in enumerate(bands[:-1]):
        for yy in range(by, by + bh):
            band_of[yy] = (n, (yy - by) / bh)

    def pixel(iy, ix):
        i = (iy * aw + ix) * bpp
        return art[i:i + 3]

    def strip(pattern, iy, x):
        ca_, cb_, w = pattern
        pa, pb = pixel(iy, ca_[x]), pixel(iy, cb_[x])
        return [pa[j] * (1 - w[x]) + pb[j] * w[x] for j in range(3)]

    def water_row(iy, n, tv, avg):
        """The generated water for one row: columns left of the picture, then
        (with EXTEND_RIGHT) the ones right of it."""
        cols = x0 + ext
        lum = []
        for x in range(cols):
            # blend this band's strips into the next band's, row by row
            p1, p2 = strip(bands[n][2], iy, x), strip(bands[n + 1][2], iy, x)
            lum.append(sum(p1[j] * (1 - tv) + p2[j] * tv for j in range(3)) / 3)
        acc = [0.0]
        for v in lum:
            acc.append(acc[-1] + v)
        r, avg_l = LAKE_SMEAR * scale, max(1.0, sum(avg) / 3)
        f = smooth((iy - water) / (top + H - water))
        m = MIST_MAX + (MIST_BOTTOM - MIST_MAX) * f
        gen = []
        for x in range(cols):
            a, b = max(0, x - r), min(cols, x + r + 1)
            k = 1 + LAKE_DETAIL * ((acc[b] - acc[a]) / (b - a) / avg_l - 1)
            gen.append([avg[j] * k * LAKE_DARKEN * (1 - m) + MIST_COLOUR[j] * m for j in range(3)])
        return gen

    # colours along the picture's right edge, smoothed up and down, which fill
    # the space right of it (with EXTEND_RIGHT) and fade out into the glow
    edge_col = []
    if ext:
        er, soft = 2 * LAKE_SMEAR * scale, EDGE_SOFT * scale
        raw = [[sum(pixel(iy, aw - 1 - ix)[j] for ix in range(er)) / er for j in range(3)]
               for iy in range(top, top + H)]
        for y in range(H):
            rows = raw[max(0, y - soft):y + soft + 1]
            edge_col.append([sum(r[j] for r in rows) / len(rows) for j in range(3)])

    def misty(ix, iy, px):
        """How much of the pale mist to darken at this spot of the picture."""
        # how far this spot is from the trunk, and how misty the pixel is
        d = math.hypot((ix / aw - TRUNK[0]) / 0.8, (iy / ah - TRUNK[1]) / 0.7)
        lum = (max(px) + min(px)) / 510
        sat = (max(px) - min(px)) / 255
        haze = smooth((lum - 0.25) / 0.3) * (1 - smooth(sat / 0.35))
        aura = AURA_FADE * haze * smooth((d - AURA_REACH * 0.4) / AURA_REACH)
        return aura * 0.4 if iy >= water else aura   # keep the lake's shine

    # starfield along the top (same sky as the stars-only version)
    sky = stars.sky(CANVAS_W, 320, 200, 11, True, random.Random(stars.SEED))
    _, _, starpx = stars.render(sky, CANVAS_W, CANVAS_H, scale)

    out = bytearray(W * H * 4)
    for y in range(H):
        iy = y + top
        fade_top = smooth(y / (FADE_TOP * H))
        a_water = LAKE_OPACITY * smooth((iy - water) / (WATER_SOFT * scale))
        if iy in band_of:
            n, tv = band_of[iy]
            row = [pixel(iy, ix) for ix in range(period)]
            avg = [sum(p[j] for p in row) / period for j in range(3)]
            gen = water_row(iy, n, tv, avg)
            er = 2 * LAKE_SMEAR * scale
            edge = [sum(pixel(iy, ix)[j] for ix in range(er)) / er for j in range(3)]
            edge_r = [sum(pixel(iy, aw - 1 - ix)[j] for ix in range(er)) / er for j in range(3)]
        for x in range(W):
            k = (y * W + x) * 4
            ca, aa, aura = (0, 0, 0), 0.0, 0.0
            ha = HAZE_MAX * fade_top * smooth((x - (x0 - HAZE_REACH * scale))
                                              / (HAZE_REACH * scale + HAZE_INTO * aw)) ** 1.6
            if x0 <= x < xr or (x >= xr and a_water == 0):
                ix = min(x - x0, aw - 1)
                if x < xr:
                    px = pixel(iy, ix)
                    if ext:
                        # blend the picture's right side into its edge colours
                        tr = smooth((xr - 1 - x) / (FADE_RIGHT * scale))
                        e = edge_r if a_water > 0 else edge_col[y]
                        px = [px[j] * tr + e[j] * (1 - tr) for j in range(3)]
                else:
                    px = edge_col[y]
                aa = max(OPACITY * smooth(ix / aw / FADE_LEFT) * fade_top, a_water)
                if x >= xr:
                    aa *= 1 - smooth((x - xr) / ext)         # fade out into the glow
                aura = misty(ix, iy, px)
            elif x >= xr:
                # the lake continued right of the picture
                px = gen[x0 + x - xr]
                t = smooth((xr + blend - 1 - x) / blend)     # 1 next to the picture
                if t > 0:
                    px = [px[j] * (1 - t) + edge_r[j] * t for j in range(3)]
                aa = a_water + (OPACITY * fade_top - a_water) * t
                aura = misty(aw - 1, iy, edge_r) * t
            elif a_water > 0:
                # blend this band's strips into the next band's, row by row
                px = gen[x]
                t = smooth((x - (x0 - blend)) / blend)       # 1 next to the picture
                if t > 0:
                    real = edge                      # the painting's own water at its edge
                    px = [px[j] * (1 - t) + real[j] * t for j in range(3)]
                aa = a_water
            if aa > 0:
                sat = (max(px) - min(px)) / 255
                aa = min(1.0, aa * (1 + BLOSSOM_BOOST * (sat - 0.3)) * (1 - 0.5 * aura))
                ca = tuple(((px[j] * DARKEN) * (1 - TINT_AMOUNT) + TINT[j] * TINT_AMOUNT)
                           * (1 - aura) + AURA_COLOUR[j] * aura for j in range(3))
            # picture over haze
            pa = aa + ha * (1 - aa)
            if pa > 0:
                ca = tuple((ca[j] * aa + HAZE_COLOUR[j] * ha * (1 - aa)) / pa for j in range(3))
            aa = pa
            # stars over everything
            sa = starpx[k + 3] / 255
            a = sa + aa * (1 - sa)
            if a > 0:
                rgb = (int((starpx[k + j] * sa + ca[j] * aa * (1 - sa)) / a) for j in range(3))
                out[k:k + 4] = bytes((*rgb, int(a * 255 + 0.5)))
    return W, H, out


if __name__ == "__main__":
    import sys
    name = "bg-editor"
    if "--overleaf" in sys.argv:
        # Overleaf's editor is usually about as narrow as the picture itself,
        # so push the tree part-way out past its right edge
        name = "bg-overleaf"
        CUT_RIGHT = 0.18
        ART_BOTTOM = 0.89                # lower in the editor, less lake
        OPACITY = 0.50
        LAKE_OPACITY = 0.28
    for scale, suffix in ((1, ""), (2, "@2x")):
        W, H, px = build(scale)
        stars.write_png(os.path.join(HERE, f"{name}{suffix}.png"), W, H, px)
        print(f"wrote {name}{suffix}.png ({W}x{H})")
