#!/usr/bin/env python3
"""Builds the installable styles from ink-koi-claude.css, with the koi
embedded so they need no hosting.

    python3 build.py

Always writes ink-koi-claude.user.css, which is the whole style without
the koi. The greeting font and the send-button seal in assets/ go into
both. If the Firefox theme's koi have been built
(../firefox-ink-koi/chrome/ink-koi/koi-wide-*.png, made by
`python3 tools/make-art.py` there), it also writes
ink-koi-claude-custom.user.css with them in. That one is git-ignored, so
a picture you don't own can't be pushed by accident.

Uses `cwebp` (brew install webp) to shrink the pictures if it's installed,
or Pillow if that is; otherwise embeds the PNGs as they are, which works
but makes the style bigger.
"""
import base64, io, os, shutil, struct, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
KOI = os.path.join(HERE, "..", "firefox-ink-koi", "chrome", "ink-koi")
ASSETS = os.path.join(HERE, "assets")   # made by tools/make-assets.py
QUALITY = 85                     # WebP quality for the colour (alpha is kept at 90)
TURN = 180                       # seconds for the koi to circle once (0 = still)
TURN_CHAT = 270                  # the same in conversations, where they're blurred


def data_uri(path, width=0):
    """The picture as a data: URI, as WebP if possible; `width` resizes it."""
    if shutil.which("cwebp"):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "img.webp")
            resize = ["-resize", str(width), "0"] if width else []
            subprocess.run(["cwebp", "-quiet", "-q", str(QUALITY), "-alpha_q", "90", *resize, path, "-o", out],
                           check=True)
            data, mime = open(out, "rb").read(), "image/webp"
    else:
        try:
            from PIL import Image
            buf = io.BytesIO()
            img = Image.open(path)
            if width:
                img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
            img.save(buf, "WEBP", quality=QUALITY, alpha_quality=90)
            data, mime = buf.getvalue(), "image/webp"
        except ImportError:
            data, mime = open(path, "rb").read(), "image/png"
    return f'"data:{mime};base64,{base64.b64encode(data).decode()}"'


def turning(path, turn, scale=1):
    """The koi in an SVG that turns them slowly, anticlockwise, the way
    they swim. The square leaves room for the painting's corners as it
    turns, and the turning stops when the system asks for reduced motion.
    The CSS sizes the square on the assumption that the painting is about
    1.27 times as wide as it is tall."""
    w, h = struct.unpack(">II", open(path, "rb").read()[16:24])
    side = round((w * w + h * h) ** 0.5)
    assert abs(side / w - 1.272) < 0.02, "the CSS's koi size assumes a 1.27:1 painting"
    inner = data_uri(path, round(w * scale) if scale != 1 else 0).strip('"')
    spin = (f"<style>g{{transform-box:view-box;transform-origin:50% 50%;animation:t {turn}s linear infinite}}"
            f"@keyframes t{{to{{transform:rotate(-360deg)}}}}"
            f"@media (prefers-reduced-motion:reduce){{g{{animation:none}}}}</style>") if turn else ""
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {side} {side}'>{spin}<g>"
           f"<image href='{inner}' x='{(side - w) / 2}' y='{(side - h) / 2}' width='{w}' height='{h}'/></g></svg>")
    for ch, code in (("%", "%25"), ("#", "%23"), ('"', "%22"), ("<", "%3C"), (">", "%3E")):
        svg = svg.replace(ch, code)
    return '"data:image/svg+xml,' + svg + '"'


def raw_uri(path, mime):
    return f'"data:{mime};base64,{base64.b64encode(open(path, "rb").read()).decode()}"'


# The font and the seal are the style's own, so both builds get them.
OWN = {"@GREETING_FONT@": raw_uri(os.path.join(ASSETS, "liujianmaocao-latin.woff2"), "font/woff2"),
       "@SEAL_LIGHT@": raw_uri(os.path.join(ASSETS, "send-seal-light.png"), "image/png"),
       "@SEAL_DARK@": raw_uri(os.path.join(ASSETS, "send-seal-dark.png"), "image/png")}


def build(out_name, koi):
    css = open(os.path.join(HERE, "ink-koi-claude.css")).read()
    for key, value in koi.items():
        css = css.replace(f"url(@{key}@)", value)
    for key, uri in OWN.items():
        css = css.replace(key, uri)
    open(os.path.join(HERE, out_name), "w").write(css)
    print(f"wrote {out_name} ({len(css) // 1024} KB)")


KOI_KEYS = ("KOI_LIGHT", "KOI_DARK", "KOI_CHAT_LIGHT", "KOI_CHAT_DARK")
build("ink-koi-claude.user.css", dict.fromkeys(KOI_KEYS, "none"))
light, dark = (os.path.join(KOI, f"koi-wide-{m}.png") for m in ("light", "dark"))
if os.path.exists(light) and os.path.exists(dark):
    build("ink-koi-claude-custom.user.css", {
        "KOI_LIGHT": f"url({turning(light, TURN)})", "KOI_DARK": f"url({turning(dark, TURN)})",
        "KOI_CHAT_LIGHT": f"url({turning(light, TURN_CHAT, 0.5)})",
        "KOI_CHAT_DARK": f"url({turning(dark, TURN_CHAT, 0.5)})"})
else:
    print("No koi built yet, so only the plain style was written.")
    print("See \"The picture\" in ../firefox-ink-koi/README.md to add them.")
