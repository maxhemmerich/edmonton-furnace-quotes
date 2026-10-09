# Builds the homeowner one-page checklist for Edmonton Furnace Quotes.
# Run: py -3.10 tools/make_quote_checklist.py
#
# The two lists are read out of the pages themselves - furnace-replacement.html #quote and
# furnace-repair.html #quote - so the handout cannot drift from what the site prints. Nothing is
# invented here: the PDF carries only the site's own words, plus the coverage line and the receiving
# address it already prints. No price is stated, because the site states none.
import os, re, html
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "downloads", "furnace-quote-checklist.pdf")

W, H = letter
M = 46.0

NAVY = (0.055, 0.082, 0.114)
AMBER = (0.949, 0.627, 0.239)
AMBER_D = (0.722, 0.478, 0.169)
INK = (0.09, 0.11, 0.14)
GREY = (0.42, 0.47, 0.53)
SUB = (0.30, 0.35, 0.40)
LINE = (0.80, 0.83, 0.86)
REG, BOLD = "Helvetica", "Helvetica-Bold"


def clean(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    for a, b in (("\u2014", "\u2014"), ("\u2019", "'"), ("\u201c", '"'), ("\u201d", '"'), ("&middot;", "\u00b7")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def section(doc, sid):
    m = re.search(r'<section id="%s">(.*?)</section>' % re.escape(sid), doc, re.S)
    return m.group(1) if m else ""


def li_items(page, sid):
    block = section(open(os.path.join(ROOT, page), encoding="utf-8").read(), sid)
    ul = re.search(r'<ul class="checks"[^>]*>(.*?)</ul>', block, re.S)
    items = []
    for li in re.findall(r"<li[^>]*>(.*?)</li>", ul.group(1), re.S):
        li = re.sub(r"<a\b.*?</a>", " ", li, flags=re.S)   # drop navigational link text (e.g. "what the City requires ->")
        m = re.search(r'<strong class="d">(.*?)</strong>', li, re.S)
        title = clean(m.group(1)) if m else clean(li)
        body = clean(li[m.end():]) if m else ""
        items.append((title, body))
    return items


REPLACEMENT = li_items("furnace-replacement.html", "quote")
REPAIR = li_items("furnace-repair.html", "quote")
if len(REPLACEMENT) != 5 or len(REPAIR) != 5:
    raise SystemExit("expected 5 replacement and 5 repair items; got %d and %d" % (len(REPLACEMENT), len(REPAIR)))

if not os.path.isdir(os.path.dirname(OUT)):
    os.makedirs(os.path.dirname(OUT))


def tw(s, f, size):
    return pdfmetrics.stringWidth(s, f, size)


def wrap(text, f, size, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(t, f, size) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


c = canvas.Canvas(OUT, pagesize=letter)
c.setTitle("What your written furnace quote should contain \u2014 Edmonton checklist")
c.setAuthor("Max Hemmerich")
c.setSubject("A one-page checklist drawn from the quote lists on edmonton-furnace-quotes")

# ---------- header band ----------
c.setFillColorRGB(*NAVY)
c.rect(0, H - 104, W, 104, stroke=0, fill=1)
c.setFillColorRGB(*AMBER)
c.rect(0, H - 107, W, 3, stroke=0, fill=1)
c.setFont(BOLD, 15.5)
c.setFillColorRGB(1, 1, 1)
c.drawString(M, H - 44, "EDMONTON FURNACE QUOTES")
c.setFont(REG, 9.2)
c.setFillColorRGB(0.66, 0.72, 0.79)
c.drawString(M, H - 62, "What your written furnace quote should contain  \u00b7  a one-page checklist")
c.drawString(M, H - 79, "Edmonton, Alberta  \u00b7  furnace replacement and repair")
c.setFont(BOLD, 10.5)
c.setFillColorRGB(*AMBER)
c.drawRightString(W - M, H - 48, "no charge to you")
c.setFont(REG, 8.2)
c.setFillColorRGB(0.66, 0.72, 0.79)
c.drawRightString(W - M, H - 64, "we do not quote the work")

y = H - 128
c.setFont(REG, 8.4)
c.setFillColorRGB(*SUB)
for ln in wrap("We do not do the work and we do not quote for it, so there is no price here. A licensed "
               "contractor quotes you. These are the things worth having on paper before you agree to anything.",
               REG, 9.0, W - 2 * M):
    c.drawString(M, y, ln)
    y -= 11.2
y -= 8


def rule(yy):
    c.setStrokeColorRGB(*LINE)
    c.setLineWidth(0.6)
    c.line(M, yy, W - M, yy)


def label(text, yy):
    c.setFont(REG, 8.0)
    c.setFillColorRGB(*AMBER_D)
    c.drawString(M, yy, "  ".join(text.upper()))
    rule(yy - 6)
    return yy - 21


def items(items, yy):
    for title, body in items:
        # tick box
        c.setStrokeColorRGB(*AMBER_D)
        c.setLineWidth(0.9)
        c.rect(M, yy - 1.5, 8, 8, stroke=1, fill=0)
        c.setStrokeColorRGB(*AMBER)
        c.setLineWidth(1.4)
        c.line(M + 1.6, yy + 3.2, M + 3.2, yy + 1.4)
        c.line(M + 3.2, yy + 1.4, M + 6.6, yy + 5.4)
        c.setFont(BOLD, 10.2)
        c.setFillColorRGB(*INK)
        for i, ln in enumerate(wrap(title, BOLD, 10.2, W - M - 14 - M)):
            c.drawString(M + 15, yy - i * 11.6, ln)
            if i:
                yy -= 11.6
        yy -= 12.0
        c.setFont(REG, 9.0)
        c.setFillColorRGB(*SUB)
        for ln in wrap(body, REG, 9.0, W - M - 14 - M):
            c.drawString(M + 15, yy, ln)
            yy -= 10.8
        yy -= 6.4
    return yy


y = label("A written replacement quote should contain", y)
y = items(REPLACEMENT, y)
y -= 2
y = label("A written repair quote should contain", y)
y = items(REPAIR, y)
y -= 4
y = label("What this list is not", y)
for t in ("We do not install, repair or service furnaces, and we do not quote for them \u2014 a licensed contractor does that.",
          "There is no price on the site this list is drawn from, and no contractor is named, rated or reviewed on it.",
          "There is no charge to you, and you are never obligated to buy."):
    for ln in wrap(t, REG, 9.0, W - 2 * M):
        c.setFont(REG, 9.0)
        c.setFillColorRGB(*SUB)
        c.drawString(M, y, ln)
        y -= 11.2
    y -= 1.8

# ---------- footer ----------
rule(76)
c.setFont(REG, 8.0)
c.setFillColorRGB(*GREY)
c.drawString(M, 62, "Coverage: Edmonton T5A\u2013T6X, plus T7X (Spruce Grove), T8A and T8B (Sherwood Park), T8N (St. Albert) and T9E (Leduc and Nisku).")
c.drawString(M, 51, "Request a quote at maxhemmerich.github.io/edmonton-furnace-quotes  \u00b7  maxhemmerich@gmail.com")
c.drawString(M, 40, "Edmonton Furnace Quotes is not a contractor, not a utility, and does not quote the work. No price is stated \u2014 a licensed contractor quotes you.")

c.showPage()
c.save()
print("wrote", OUT, os.path.getsize(OUT), "bytes")
if y < 70:
    print("WARNING: checklist ran to y=%.1f, near/below the footer rule at 76 \u2014 check the page fits." % y)
else:
    print("fits: content ended at y=%.1f (footer rule at 76)." % y)
