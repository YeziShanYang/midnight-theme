#!/usr/bin/env python3
"""Builds the page background and embeds it in ../moonlight.sty.

    python3 make-background.py picture.jpg

Keeps the top of the picture (the moon) and its bottom (the flowers) and
cross-fades them through the middle, so every page gets both. Then it frosts
the result like glass (blurred, with a milky layer) and darkens it for
readable text. The background goes into moonlight.sty as a small text-only
PDF, between the "% >>> background" and "% <<< background" lines, so the .sty
works on its own. Needs Pillow (pip install pillow).
"""
import base64, io, os, re, sys
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
STY = os.path.join(HERE, "..", "moonlight.sty")

PAGE_W, PAGE_H = 1500, 2121      # pixels for an A4 page (about 180 dpi)
TOP = (0.0, 0.40)                # part of the picture kept at the top (0..1 down)
BOTTOM = (0.63, 0.965)           # kept at the bottom (stops above the signature)
BLEND = 0.10                     # fraction of the page height the two cross-fade over
TRIM = 0.012                     # fraction cut off each side (the picture has a dark edge)
KNEE, SQUASH = 0.42, 0.55        # brightness above KNEE (0..1) is squashed by SQUASH, so
                                 # the moon and flowers glow without drowning the text
FROST = 5                        # blur radius in px: how "frosted" the glass is
FROST_MIX = 0.55                 # 0 = sharp picture, 1 = fully blurred
MILK = ((236, 222, 255), 0.06)   # pale layer that makes the glass look frosted
VEIL = ((14, 9, 28), 0.34)       # dark layer so the text stays readable
FADE = 0.30                      # how far the whole picture fades into the page colour
PAGE_COLOUR = (18, 12, 34)       # bgc in moonlight.sty
QUALITY = 84                     # JPEG quality


def compose(src):
    w, h = src.size
    src = src.crop((round(TRIM * w), 0, round((1 - TRIM) * w), h))
    w = src.width
    src = src.resize((PAGE_W, round(h * PAGE_W / w)), Image.LANCZOS)
    h = src.height
    top = src.crop((0, round(TOP[0] * h), PAGE_W, round(TOP[1] * h)))
    bot = src.crop((0, round(BOTTOM[0] * h), PAGE_W, round(BOTTOM[1] * h)))
    # scale both parts up if needed so they fill the page with at least BLEND of
    # overlap; if they're taller than that, they just overlap more
    k = max(1.0, (PAGE_H * (1 + BLEND)) / (top.height + bot.height))
    if k > 1:
        tw = round(PAGE_W * k)
        top = top.resize((tw, round(top.height * k)), Image.LANCZOS)
        bot = bot.resize((tw, round(bot.height * k)), Image.LANCZOS)
        x = (tw - PAGE_W) // 2                       # crop the sides that got wider
        top, bot = top.crop((x, 0, x + PAGE_W, top.height)), bot.crop((x, 0, x + PAGE_W, bot.height))
    blend = top.height + bot.height - PAGE_H
    page = Image.new("RGB", (PAGE_W, PAGE_H))
    page.paste(bot, (0, PAGE_H - bot.height))
    mask = Image.new("L", (PAGE_W, top.height), 255)
    for y in range(top.height - blend, top.height):
        t = (y - (top.height - blend)) / blend
        mask.paste(round(255 * (1 - t * t * (3 - 2 * t))), (0, y, PAGE_W, y + 1))
    page.paste(top, (0, 0), mask)
    return page


def frost(page):
    knee = round(KNEE * 255)
    page = page.point(lambda v: v if v <= knee else round(knee + (v - knee) * SQUASH))
    page = Image.blend(page, page.filter(ImageFilter.GaussianBlur(FROST)), FROST_MIX)
    for colour, amount in (MILK, VEIL, (PAGE_COLOUR, FADE)):
        page = Image.blend(page, Image.new("RGB", page.size, colour), amount)
    return page


def text_pdf(jpeg, w, h):
    """A one-page PDF showing the JPEG, using only printable ASCII."""
    stream = base64.a85encode(jpeg, wrapcol=0) + b"~>"
    stream = b"\n".join(stream[i:i + 120] for i in range(0, len(stream), 120)) + b"\n"
    content = b"q %d 0 0 %d 0 0 cm /Im0 Do Q\n" % (w, h)
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] "
        b"/Resources << /XObject << /Im0 4 0 R >> >> /Contents 5 0 R >>" % (w, h),
        b"<< /Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace /DeviceRGB "
        b"/BitsPerComponent 8 /Filter [/ASCII85Decode /DCTDecode] /Length %d >>\nstream\n"
        % (w, h, len(stream)) + stream + b"endstream",
        b"<< /Length %d >>\nstream\n" % len(content) + content + b"endstream",
    ]
    out, offsets = b"%PDF-1.4\n", []
    for n, obj in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % n + obj + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
    return out.decode("ascii")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    page = frost(compose(Image.open(sys.argv[1]).convert("RGB")))
    buf = io.BytesIO()
    page.save(buf, "JPEG", quality=QUALITY, optimize=True, progressive=False)
    page.save(os.path.join(HERE, "background-preview.jpg"), quality=90)
    pdf = text_pdf(buf.getvalue(), PAGE_W, PAGE_H)
    assert "\\end{filecontents" not in pdf
    sty = open(STY).read()
    block = ("% >>> background (written by tools/make-background.py; don't edit by hand)\n"
             "\\begin{filecontents*}[overwrite]{moonlight-background.pdf}\n"
             + pdf + "\\end{filecontents*}\n% <<< background\n")
    sty, n = re.subn(r"% >>> background.*?% <<< background\n", lambda m: block, sty, flags=re.S)
    if n != 1:
        sys.exit("moonlight.sty has no '% >>> background' ... '% <<< background' block")
    open(STY, "w").write(sty)
    print(f"embedded a {PAGE_W}x{PAGE_H} background ({len(pdf) // 1024} KB) in moonlight.sty")
