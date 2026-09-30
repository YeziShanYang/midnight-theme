#!/usr/bin/env python3
"""Draws the transparent starfield PNGs used by midnight-glow.qss.

    python3 make-stars.py      (writes stars-*.png and stars-*@2x.png)

Change SEED for a different sky, or the counts below for more/fewer stars.
Pure Python, no extra packages needed.
"""
import math, random, struct, zlib

SEED = 106


def write_png(path, w, h, rgba):
    raw = b"".join(b"\0" + bytes(rgba[y * w * 4:(y + 1) * w * 4]) for y in range(h))
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(raw, 9)))
        f.write(chunk(b"IEND", b""))


def sky(w, h, count, bright, anchor_right, rng):
    """Returns a list of stars (x, y, size, alpha, colour, sparkle), in logical px."""
    tints = [(255, 255, 255)] * 6 + [(228, 220, 255)] * 3 + [(255, 214, 240)]
    stars = []
    for i in range(count):
        v = rng.random() ** 1.6                      # denser near the top
        u = rng.random() ** 0.8                      # a little denser on the anchored side
        x = (1 - u) * w if not anchor_right else u * w
        y = v * h
        fade = (1 - v) ** 1.3                        # dims out towards the bottom
        sparkle = i < bright
        size = rng.uniform(1.0, 1.5) if sparkle else rng.uniform(0.35, 0.9)
        alpha = (rng.uniform(0.75, 1.0) if sparkle else rng.uniform(0.25, 0.8)) * fade
        stars.append((x, y, size, alpha, rng.choice(tints), sparkle))
    return stars


def render(stars, w, h, scale):
    W, H = w * scale, h * scale
    a = [0.0] * (W * H)      # coverage (alpha)
    wsum = [0.0] * (W * H)   # total weight, to average the tints
    col = [[0.0, 0.0, 0.0] for _ in range(W * H)]

    def plot(px, py, v, c):
        if 0 <= px < W and 0 <= py < H and v > 0.002:
            k = py * W + px
            a[k] = min(1.0, a[k] + v)
            wsum[k] += v
            for j in range(3):
                col[k][j] += c[j] * v

    for x, y, size, alpha, c, sparkle in stars:
        cx, cy, r = x * scale, y * scale, size * scale
        # soft core + faint halo
        reach = int(r * 4) + 2
        for py in range(int(cy) - reach, int(cy) + reach + 1):
            for px in range(int(cx) - reach, int(cx) + reach + 1):
                d2 = ((px + 0.5 - cx) ** 2 + (py + 0.5 - cy) ** 2) / (r * r)
                v = math.exp(-d2 * 1.6) + 0.12 * math.exp(-d2 * 0.18)
                plot(px, py, alpha * v, c)
        if sparkle:
            # four-point twinkle
            length = r * 7
            for t in range(1, int(length)):
                v = alpha * 0.55 * (1 - t / length) ** 2
                for dx, dy in ((t, 0), (-t, 0), (0, t), (0, -t)):
                    plot(int(cx + dx), int(cy + dy), v, c)

    out = bytearray(W * H * 4)
    for k in range(W * H):
        if a[k] > 0:
            rgb = (int(col[k][j] / wsum[k]) for j in range(3))
            out[k * 4:k * 4 + 4] = bytes((*rgb, int(a[k] * 255)))
    return W, H, out


def build(name, w, h, count, bright, anchor_right, seed):
    stars = sky(w, h, count, bright, anchor_right, random.Random(seed))
    for scale, suffix in ((1, ""), (2, "@2x")):
        W, H, px = render(stars, w, h, scale)
        write_png(f"{name}{suffix}.png", W, H, px)
        print(f"wrote {name}{suffix}.png ({W}x{H})")


if __name__ == "__main__":
    build("stars-editor", 1400, 320, count=200, bright=11, anchor_right=True, seed=SEED)
    build("stars-sidebar", 420, 220, count=55, bright=4, anchor_right=False, seed=SEED + 1)
