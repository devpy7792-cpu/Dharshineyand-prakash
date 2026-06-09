# -*- coding: utf-8 -*-
"""Generate all image assets for the Dharshiny & Prakash wedding site.
- Organizes the 5 source photos into images/ with clean names
- Applies a subtle warm, matte 'film' grade for cohesion (farmhouse palette)
- Splits the Ghibli diptych into bride / groom panels (+ keeps the full art)
- Composes an elegant, downloadable invitation card (images/invitation.jpg)
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

SRC = "."
OUT = "images"
os.makedirs(OUT, exist_ok=True)

F = "C:/Windows/Fonts/"
def font(name, size):
    return ImageFont.truetype(F + name, size)

# ---------------------------------------------------------------- warm grade
def warm_grade(im, strength=1.0):
    """Subtle warm, slightly matte editorial grade. strength scales the effect."""
    im = im.convert("RGB")
    a = np.asarray(im).astype(np.float32)
    # gentle S-curve contrast
    a = (a - 128) * (1 + 0.10 * strength) + 128
    # warm white balance: lift R, ease B
    a[..., 0] *= (1 + 0.045 * strength)
    a[..., 1] *= (1 + 0.008 * strength)
    a[..., 2] *= (1 - 0.050 * strength)
    a = np.clip(a, 0, 255)
    # matte fade: lift blacks, drop highlights a touch -> filmic
    lo, hi = 12 * strength, 248 - 4 * strength
    a = lo + a * ((hi - lo) / 255.0)
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    out = ImageEnhance.Color(out).enhance(1 + 0.10 * strength)   # saturation
    out = out.filter(ImageFilter.UnsharpMask(radius=1.4, percent=70, threshold=2))
    return out

def save(im, name, q=88):
    p = os.path.join(OUT, name)
    im.save(p, quality=q, optimize=True, progressive=True)
    print("  wrote", p, im.size)

print("Grading photos...")
m = {
    "WhatsApp Image 2026-06-07 at 10.51.30 AM.jpeg": "proposal.jpg",      # kneel + flowers
    "WhatsApp Image 2026-06-07 at 10.51.32 AM.jpeg": "tracks-walk.jpg",   # walking the rails (hero)
    "WhatsApp Image 2026-06-07 at 10.51.36 AM.jpeg": "cottage-facing.jpg",# facing by the cottage
}
for src, dst in m.items():
    save(warm_grade(Image.open(os.path.join(SRC, src))), dst)

# 38: strip black letterbox bars (content rows 257..1340)
im38 = Image.open(SRC + "/WhatsApp Image 2026-06-07 at 10.51.38 AM.jpeg").crop((0, 257, 720, 1341))
save(warm_grade(im38), "cottage-walk.jpg")

# 39: Ghibli diptych -> bride (left) / groom (right) / full. Gutter cols 493..519.
d = Image.open(SRC + "/WhatsApp Image 2026-06-07 at 10.51.39 AM.jpeg").convert("RGB")
save(d.crop((31, 203, 492, 1247)), "ghibli-bride.jpg")
save(d.crop((520, 203, 985, 1247)), "ghibli-groom.jpg")
save(d.crop((31, 203, 985, 1247)), "ghibli-diptych.jpg")

# ---------------------------------------------------------------- invitation
print("Composing invitation card...")
CREAM   = (246, 239, 226)
INK     = (47, 42, 34)
TERRA   = (176, 92, 58)
SAGE    = (122, 134, 99)
GOLD    = (181, 142, 70)

W, H = 1080, 1528
card = Image.new("RGB", (W, H), CREAM)
# faint warm paper vignette
vg = Image.new("L", (W, H), 0)
vgd = ImageDraw.Draw(vg)
vgd.ellipse((-W*0.3, -H*0.3, W*1.3, H*1.3), fill=22)
card = Image.composite(Image.new("RGB", (W, H), (236, 226, 208)), card, vg.filter(ImageFilter.GaussianBlur(120)))
dr = ImageDraw.Draw(card)

# double frame
dr.rectangle((54, 54, W-54, H-54), outline=TERRA, width=2)
dr.rectangle((68, 68, W-68, H-68), outline=GOLD, width=1)

def leaf_sprig(cx, cy, scale=1.0, color=SAGE):
    """A slim eucalyptus-style sprig: thin pointed leaves alternating along a stem."""
    span = 150 * scale
    dr.line((cx, cy - span/2, cx, cy + span/2), fill=color, width=2)
    n = 7
    for i in range(n):
        t = i / (n - 1)
        ly = cy - span/2 + t * span
        side = 1 if i % 2 == 0 else -1
        length = (1 - abs(t - 0.5) * 1.1) * 60 * scale   # taper toward the tips
        lw = max(6, int(length))
        leaf = Image.new("RGBA", (130, 60), (0, 0, 0, 0))
        ld = ImageDraw.Draw(leaf)
        ld.ellipse((10, 22, 10 + lw, 38), fill=color + (255,))   # thin oval -> leaf
        ang = side * (38 + (t - 0.5) * 18)
        leaf = leaf.rotate(ang, expand=True, resample=Image.BICUBIC)
        card.paste(leaf, (int(cx + side * 3 - leaf.width/2), int(ly - leaf.height/2)), leaf)

leaf_sprig(W//2, 150, 0.6)

def ctext(y, txt, fnt, fill, ls=0):
    """centered text with optional letter spacing"""
    if ls == 0:
        w = dr.textlength(txt, font=fnt)
        dr.text((W/2 - w/2, y), txt, font=fnt, fill=fill)
        return
    widths = [dr.textlength(c, font=fnt) for c in txt]
    total = sum(widths) + ls * (len(txt) - 1)
    x = W/2 - total/2
    for c, cw in zip(txt, widths):
        dr.text((x, y), c, font=fnt, fill=fill)
        x += cw + ls

ctext(250, "TOGETHER WITH THEIR FAMILIES", font("GARA.TTF", 26), SAGE, ls=6)

# names: Garamond + Corsiva ampersand
dharshiny = font("GARA.TTF", 132)
amp = font("MTCORSVA.TTF", 150)
ctext(312, "Dharshiny", dharshiny, INK)
ctext(452, "&", amp, TERRA)
ctext(560, "Prakash", dharshiny, INK)

# divider with diamond
cy = 740
dr.line((W/2 - 180, cy, W/2 - 26, cy), fill=GOLD, width=2)
dr.line((W/2 + 26, cy, W/2 + 180, cy), fill=GOLD, width=2)
dr.polygon([(W/2, cy-9), (W/2+11, cy), (W/2, cy+9), (W/2-11, cy)], outline=TERRA, width=2)

ctext(792, "request the pleasure of your company", font("GARAIT.TTF", 38), INK)
ctext(842, "at their Wedding Reception", font("GARAIT.TTF", 38), INK)

ctext(940, "SUNDAY", font("GARA.TTF", 30), SAGE, ls=8)
ctext(982, "21 JUNE 2026", font("GARABD.TTF", 88), TERRA)
ctext(1092, "Six Thirty in the Evening", font("GARAIT.TTF", 36), INK)

cy = 1175
dr.line((W/2 - 150, cy, W/2 + 150, cy), fill=GOLD, width=1)

ctext(1212, "ASHIRVAD HALL", font("GARA.TTF", 40), INK, ls=3)
ctext(1264, "First Floor, Pearl Restaurant", font("GARAIT.TTF", 32), SAGE)
ctext(1306, "Coimbatore, Tamil Nadu", font("GARAIT.TTF", 32), SAGE)

leaf_sprig(W//2, 1432, 0.55)

card.save(os.path.join(OUT, "invitation.jpg"), quality=92, optimize=True, progressive=True)
print("  wrote", os.path.join(OUT, "invitation.jpg"), card.size)

# ---------------------------------------------------------------- hero (floral arch)
# Source assets live in assest/ (the floral arch PNG, a flower cluster, and an
# AI-composed couple photo). These build the home-page hero composition.
print("Processing hero assets...")
A = "assest"
hero_jobs = [
    ("ChatGPT Image Jun 9, 2026, 07_39_36 AM.png", "hero-couple.jpg", (1000, 1500), "jpg"),
    ("660613120a4f1857e7aadcfe_Wedding Arch 91.webp", "arch.png", (1000, 1000), "png"),
    ("6605b6015cf7e99ec21a4898_flower decoration 2.webp", "flower.png", (420, 420), "png"),
    ("6606d0bc26c2741b458e6e72_String.webp", "string.png", (2200, 2200), "png"),  # clothesline rope
]
for src, dst, box, kind in hero_jobs:
    p = os.path.join(A, src)
    if not os.path.exists(p):
        print("  skip (missing):", p); continue
    im = Image.open(p)
    if kind == "jpg":
        im = im.convert("RGB"); im.thumbnail(box)
        im.save(os.path.join(OUT, dst), quality=88, optimize=True, progressive=True)
    else:
        im = im.convert("RGBA"); im.thumbnail(box)
        im.save(os.path.join(OUT, dst), optimize=True)
    print("  wrote", os.path.join(OUT, dst), Image.open(os.path.join(OUT, dst)).size)
print("Done.")
