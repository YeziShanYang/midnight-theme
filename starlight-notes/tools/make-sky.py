#!/usr/bin/env python3
"""Draw the starlight background and embed it in starlight.sty.

Usage: python3 tools/make-sky.py

The sky is a vertical gradient (dark navy at the top, fading to lavender
at the bottom), a soft glow low on the left, and a few thousand stars, all
drawn as vector art in a one-page PDF. The PDF is written as printable
ASCII and placed between the '% >>> background' and '% <<< background'
lines of starlight.sty, so the .sty works on its own. Uses only the Python
standard library.
"""
import base64, os, random, re, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
STY = os.path.join(HERE, "..", "starlight.sty")

W, H = 595, 842                  # an A4 page in PDF points
SEED = 1152                      # change for a different star field
# gradient stops, 0 = top of the page, 1 = bottom (sampled from the photo)
STOPS = [(0.00, "1D2639"), (0.12, "222C43"), (0.25, "263047"), (0.38, "293149"),
         (0.48, "2E354E"), (0.57, "343B56"), (0.66, "3E4665"), (0.75, "4B5479"),
         (0.84, "5C6793"), (0.92, "727BAC"), (1.00, "858ABA")]
PAGE_COLOUR = "141B30"           # bgc in starlight.sty
FADE = 0.38                      # how far the gradient fades into the page colour,
                                 # so light text stays readable at the bottom
GLOW = ("8A86C4", 0.20, (0.02, 0.22), 0.75)  # colour, strength, centre (x, y from
                                             # bottom, as page fractions), radius / W
FAINT_STARS = 4000               # tiny dim stars
STARS = 600                      # small stars
BRIGHT_STARS = 26                # the few bright ones, with a halo
STAR_COLOURS = ["F4F7FF", "E6EDFF", "DCE4FF", "FFF6E4"]


def rgb(h, fade=0.0):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    p = [int(PAGE_COLOUR[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [round(a * (1 - fade) + b * fade, 4) for a, b in zip(c, p)]


def fmt(xs):
    return " ".join(f"{x:g}" for x in xs)


def gradient_function():
    """A stitching function over STOPS, with t = 0 at the bottom of the page."""
    stops = [(1 - t, c) for t, c in reversed(STOPS)]
    parts = [f"<< /FunctionType 2 /Domain [0 1] /C0 [{fmt(rgb(a, FADE))}] "
             f"/C1 [{fmt(rgb(b, FADE))}] /N 1 >>"
             for (_, a), (_, b) in zip(stops, stops[1:])]
    bounds = [t for t, _ in stops[1:-1]]
    return (f"<< /FunctionType 3 /Domain [0 1] /Functions [{' '.join(parts)}] "
            f"/Bounds [{fmt(bounds)}] /Encode [{fmt([0, 1] * len(parts))}] >>")


def stars():
    rnd = random.Random(SEED)
    alphas = {}                  # opacity -> ExtGState name
    ops = []

    def dot(x, y, d, colour, a):
        a = round(a, 2)
        gs = alphas.setdefault(a, f"/a{len(alphas)}")
        # a zero-length line with round caps draws a dot of diameter d
        ops.append(f"{gs} gs {fmt(rgb(colour))} RG {d:.2f} w {x:.1f} {y:.1f} m {x:.1f} {y:.1f} l S")

    for _ in range(FAINT_STARS):
        dot(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.35, 0.75),
            rnd.choice(STAR_COLOURS), rnd.choice([0.25, 0.35, 0.45, 0.55]))
    for _ in range(STARS):
        dot(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.8, 1.3),
            rnd.choice(STAR_COLOURS), rnd.choice([0.55, 0.7, 0.85]))
    for _ in range(BRIGHT_STARS):
        x, y, c = rnd.uniform(0, W), rnd.uniform(0, H), rnd.choice(STAR_COLOURS)
        s = rnd.uniform(1.4, 2.0)
        for k, a in ((5.0, 0.03), (4.0, 0.04), (3.1, 0.06), (2.3, 0.1), (1.6, 0.18)):
            dot(x, y, s * k, c, a)
        dot(x, y, s, c, 1.0)
    return ops, alphas


def sky_pdf():
    """A one-page PDF of the sky, using only printable ASCII."""
    ops, alphas = stars()
    gc, gs, (gx, gy), gr = GLOW
    content = "\n".join(["q", f"0 0 {W} {H} re W n /Sky sh",
                         f"q /Glow gs {fmt(rgb(gc, FADE))} rg 0 0 {W} {H} re f Q",
                         "1 J", *ops, "Q", ""])
    states = " ".join(f"{n} << /CA {a:g} /ca {a:g} >>" for a, n in alphas.items())
    sky = (f"<< /ShadingType 2 /ColorSpace /DeviceRGB /Coords [0 0 0 {H}] "
           f"/Function {gradient_function()} /Extend [true true] >>")
    # the glow is a flat colour seen through a soft mask that fades out radially
    cx, cy, r = gx * W, gy * H, gr * W
    mask = (f"<< /ShadingType 3 /ColorSpace /DeviceGray /Coords [{fmt([cx, cy, 0, cx, cy, r])}] "
            f"/Function << /FunctionType 2 /Domain [0 1] /C0 [{gs:g}] /C1 [0] /N 2 >> "
            f"/Extend [false true] >>")
    objs = [  # (dictionary, stream or None)
        ("<< /Type /Catalog /Pages 2 0 R >>", None),
        ("<< /Type /Pages /Kids [3 0 R] /Count 1 >>", None),
        (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {W} {H}] /Resources << "
         f"/Shading << /Sky {sky} >> /ExtGState << {states} /Glow << /ca 1 /SMask "
         f"<< /Type /Mask /S /Luminosity /G 5 0 R >> >> >> >> /Contents 4 0 R >>", None),
        ("<<", content),
        (f"<< /Type /XObject /Subtype /Form /BBox [0 0 {W} {H}] "
         f"/Group << /S /Transparency /CS /DeviceGray >> "
         f"/Resources << /Shading << /M {mask} >> >> >>", f"0 0 {W} {H} re W n /M sh\n"),
    ]
    out, offsets = "%PDF-1.4\n", []
    for n, (d, s) in enumerate(objs, 1):
        offsets.append(len(out))
        if s is not None:
            s = base64.a85encode(zlib.compress(s.encode(), 9), wrapcol=120).decode() + "~>\n"
            d = (d.removesuffix(">>") if d != "<<" else d) + \
                f" /Filter [/ASCII85Decode /FlateDecode] /Length {len(s)} >>\nstream\n{s}endstream"
        out += f"{n} 0 obj\n{d}\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n"
    out += "".join(f"{o:010d} 00000 n \n" for o in offsets)
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return out


if __name__ == "__main__":
    pdf = sky_pdf()
    assert "\\end{filecontents" not in pdf
    sty = open(STY).read()
    block = ("% >>> background (written by tools/make-sky.py; don't edit by hand)\n"
             "\\begin{filecontents*}[overwrite]{starlight-sky.pdf}\n"
             + pdf + "\\end{filecontents*}\n% <<< background\n")
    sty, n = re.subn(r"% >>> background.*?% <<< background\n", lambda m: block, sty, flags=re.S)
    if n != 1:
        sys.exit("starlight.sty has no '% >>> background' ... '% <<< background' block")
    open(STY, "w").write(sty)
    print(f"embedded the sky ({len(pdf) // 1024} KB) in starlight.sty")
