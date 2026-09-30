#!/usr/bin/env python3
"""Builds the installable styles from midnight-overleaf.css, with the
background images embedded so they need no hosting.

    python3 build.py

Always writes midnight-overleaf.user.css (glows and stars). If there's a
picture background as well, bg-overleaf@2x.png here or in ../qtcreator (made
by `python3 make-art.py --overleaf` there), it also writes
midnight-overleaf-custom.user.css with the picture in the editor. That one is
git-ignored, so a picture you don't own can't be pushed by accident.

Uses `cwebp` (brew install webp) to shrink the images if it's installed;
otherwise embeds the PNGs as they are, which works but makes the style bigger.
"""
import base64, os, shutil, struct, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PICTURES = [os.path.join(HERE, "bg-overleaf@2x.png"),
            os.path.join(HERE, "..", "qtcreator", "bg-overleaf@2x.png")]
QUALITY = "88"                   # WebP quality for the colours (alpha is kept at 90)


def data_uri(path):
    if shutil.which("cwebp"):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "img.webp")
            subprocess.run(["cwebp", "-quiet", "-q", QUALITY, "-alpha_q", "90", path, "-o", out],
                           check=True)
            data, mime = open(out, "rb").read(), "image/webp"
    else:
        data, mime = open(path, "rb").read(), "image/png"
    return f'"data:{mime};base64,{base64.b64encode(data).decode()}"'


def css_size(path):
    """The image's size in CSS px: half its pixel size, as it's a @2x image."""
    w, h = struct.unpack(">II", open(path, "rb").read()[16:24])
    return f"{w // 2}px {h // 2}px"


def build(out_name, editor_image, editor_pos):
    images = {"@BG_EDITOR@": editor_image,
              "@STARS_SIDEBAR@": os.path.join(HERE, "stars-sidebar@2x.png")}
    css = open(os.path.join(HERE, "midnight-overleaf.css")).read()
    css = css.replace("@BG_EDITOR_POS@", editor_pos)
    for key, path in images.items():
        css = css.replace(key[:-1] + "_SIZE@", css_size(path)).replace(key, data_uri(path))
    open(os.path.join(HERE, out_name), "w").write(css)
    print(f"wrote {out_name} ({len(css) // 1024} KB)")


build("midnight-overleaf.user.css", os.path.join(HERE, "stars-editor@2x.png"), "right top")
picture = next((p for p in PICTURES if os.path.exists(p)), None)
if picture:
    build("midnight-overleaf-custom.user.css", picture, "right bottom")
