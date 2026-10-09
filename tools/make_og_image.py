# Builds the 1200x630 Open Graph / Twitter share card for Edmonton Furnace Quotes.
# Run: py -3.10 tools/make_og_image.py
#
# Brand only: the brand name, the city, the service line the site already prints,
# and the "not a contractor" column the site already carries. No price, no claim.
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "og.png")

# palette, lifted from assets/styles.css
BG_TOP = (0x0A, 0x10, 0x17)
BG_BOT = (0x08, 0x0C, 0x12)
LINE = (0x22, 0x30, 0x3F)
LINE2 = (0x33, 0x47, 0x5C)
TEXT = (0xE8, 0xEE, 0xF6)
MUTED = (0x93, 0xA5, 0xB8)
HEAT = (0xF2, 0xA0, 0x3D)
HEAT_DIM = (0xB8, 0x7A, 0x2B)
FOOT = (0x5E, 0x73, 0x85)
RAIL = (0x1D, 0x29, 0x37)

FONTS = "C:/Windows/Fonts"
BOLD = os.path.join(FONTS, "segoeuib.ttf")   # Segoe UI Bold — closest to Archivo 800 here
SEMI = os.path.join(FONTS, "seguisb.ttf")
MONO = os.path.join(FONTS, "consolab.ttf")
MONO_R = os.path.join(FONTS, "consola.ttf")


def f(path, size):
    return ImageFont.truetype(path, size)


def tw(d, s, font):
    return d.textbbox((0, 0), s, font=font)[2]


def spaced(d, s, font, gap):
    """Draw s with an extra gap between glyphs (the mono letterspacing in the CSS)."""
    x = 0
    for ch in s:
        d.text((x, 0), ch, font=font, fill=(0, 0, 0))
        x += d.textlength(ch, font=font) + gap
    return x - gap if s else 0


def measure_spaced(d, s, font, gap):
    return sum(d.textlength(c, font=font) for c in s) + gap * (len(s) - 1)


def draw_spaced(d, xy, s, font, gap, fill):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + gap


img = Image.new("RGB", (W, H), BG_BOT)
d = ImageDraw.Draw(img)

# ---------- ground: vertical gradient ----------
for y in range(H):
    t = y / (H - 1.0)
    d.line([(0, y), (W, y)],
           fill=tuple(int(round(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t)) for i in range(3)))

# ---------- the tick rail down the left edge (the page's only decoration) ----------
x0 = 0
for y in range(0, H, 14):
    d.line([(x0, y), (x0 + 9, y)], fill=RAIL)

# ---------- amber bar across the very top ----------
d.rectangle([0, 0, W, 5], fill=HEAT)

M = 84  # margin

# ---------- brand row ----------
by = 96
d.rectangle([M, by - 2, M + 16, by + 14], fill=HEAT)
d.rectangle([M, by - 2, M + 16, by + 14], outline=(0x4A, 0x2F, 0x10))

brand = f(BOLD, 40)
d.text((M + 30, by - 12), "Edmonton Furnace Quotes", font=brand, fill=TEXT)
bx = M + 30 + tw(d, "Edmonton Furnace Quotes", brand) + 20
mono_s = f(MONO_R, 20)
draw_spaced(d, (bx, by - 2), "YEG", mono_s, 3.0, MUTED)

# rule under the brand row
d.line([(M, by + 62), (W - M, by + 62)], fill=LINE)

# ---------- eyebrow ----------
ey = 232
mono_e = f(MONO, 19)
draw_spaced(d, (M + 2, ey), "EDMONTON, ALBERTA", mono_e, 4.6, HEAT)
d.line([(M + measure_spaced(d, "EDMONTON, ALBERTA", mono_e, 4.6) + 26, ey + 12),
        (W - M, ey + 12)], fill=LINE)

# ---------- headline ----------
hl = f(BOLD, 92)
d.text((M, 288), "Furnace quotes,", font=hl, fill=TEXT)
d.text((M, 384), "Edmonton.", font=hl, fill=TEXT)

# ---------- service line ----------
sl = f(SEMI, 31)
y = 512
segs = [("Replacement", TEXT), ("  \u00b7  ", HEAT_DIM), ("Repair", TEXT),
        ("  \u00b7  ", HEAT_DIM), ("No heat", TEXT)]
x = M + 2
for s, col in segs:
    d.text((x, y), s, font=sl, fill=col)
    x += tw(d, s, sl)

# ---------- footer ----------
d.line([(M, 566), (W - M, 566)], fill=LINE)
fs = f(SEMI, 24)
d.text((M, 584), "a quote-request service in Edmonton, Alberta", font=fs, fill=MUTED)
fr = f(MONO_R, 17)
txt = "NOT A CONTRACTOR  \u00b7  NOT A UTILITY"
draw_spaced(d, (W - M - measure_spaced(d, txt, fr, 2.4), 590), txt, fr, 2.4, FOOT)

img.save(OUT, "PNG", optimize=True)
print("wrote", OUT, os.path.getsize(OUT), "bytes", img.size)
