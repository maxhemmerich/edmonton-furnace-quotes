# Builds the one-page contractor lead sheet for Edmonton Furnace Quotes.
# Run: py -3.10 tools/make_lead_sheet.py
#
# 2026-10-09: this file is the artifact that leaves the site with a contractor — it is what the
# outreach SMS and the follow-up email carry — so it has to carry the same two things the live
# contractor page carries. It was the only contractor-facing surface that did NOT show what a
# request looks like, and the only one with no way back to the site. Both are fixed here:
# a labelled example request (the form's own field labels and its own placeholder values) and
# the live URL, drawn as a real link annotation.
# No price, lead count, testimonial, contractor name or new claim was added — the example block
# is built only from strings the request form itself prints.
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics

W, H = letter
M = 46.0
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "edmonton-furnace-lead-sheet.pdf")

SITE = "https://maxhemmerich.github.io/edmonton-furnace-quotes/"

NAVY = (0.055, 0.082, 0.114)
AMBER = (0.949, 0.627, 0.239)
AMBER_D = (0.722, 0.478, 0.169)
INK = (0.09, 0.11, 0.14)
GREY = (0.42, 0.47, 0.53)
LINE = (0.80, 0.83, 0.86)
SOFT = (0.965, 0.972, 0.980)
MUTED = (0.30, 0.35, 0.40)

REG, BOLD = "Helvetica", "Helvetica-Bold"

BOTTOM_LIMIT = 84.0  # nothing may be drawn below this; the footer rule sits at y=70


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


def para(c, text, x, y, width, size=8.6, leading=11.4, font=REG, color=INK):
    c.setFont(font, size)
    c.setFillColorRGB(*color)
    for ln in wrap(text, font, size, width):
        c.drawString(x, y, ln)
        y -= leading
    return y


def rule(c, y, x0=M, x1=W - M, color=LINE, w=0.6):
    c.setStrokeColorRGB(*color)
    c.setLineWidth(w)
    c.line(x0, y, x1, y)


def label(c, text, y):
    c.setFont(REG, 7.4)
    c.setFillColorRGB(*AMBER_D)
    spaced = "  ".join(text.upper())
    c.drawString(M, y, spaced)
    rule(c, y - 5, color=LINE)
    return y - 18


c = canvas.Canvas(OUT, pagesize=letter)
c.setTitle("Edmonton Furnace Quotes — contractor lead sheet")
c.setAuthor("Max Hemmerich")
c.setSubject("What a furnace quote request contains, what it looks like, when it is billable, "
             "and what it costs")

# ---------- header band ----------
c.setFillColorRGB(*NAVY)
c.rect(0, H - 92, W, 92, stroke=0, fill=1)
c.setFillColorRGB(*AMBER)
c.rect(0, H - 95, W, 3, stroke=0, fill=1)

c.setFont(BOLD, 15.0)
c.setFillColorRGB(1, 1, 1)
c.drawString(M, H - 40, "EDMONTON FURNACE QUOTES")

c.setFont(REG, 8.6)
c.setFillColorRGB(0.66, 0.72, 0.79)
c.drawString(M, H - 56, "Lead sheet  ·  furnace replacement and no-heat requests  ·  Edmonton, Alberta")
c.drawString(M, H - 71, "What a request contains, what it looks like, when it is billable, and what it costs.")

c.setFont(BOLD, 12.5)
c.setFillColorRGB(*AMBER)
c.drawRightString(W - M, H - 42, "$45 / qualified lead")
c.setFont(REG, 8.6)
c.setFillColorRGB(0.66, 0.72, 0.79)
c.drawRightString(W - M, H - 58, "or $400 / month, your area exclusively")
c.drawRightString(W - M, H - 72, "first three qualified leads free")

# ---------- what a lead contains ----------
y = label(c, "What a lead contains", H - 120)

fields = [
    ("Name", "the homeowner's name, as they typed it"),
    ("Callback number", "phone, checked for a full 10 digits before it is passed on"),
    ("Email", "if they left one; the phone is the channel that matters"),
    ("Postal code", "full code plus the forward sortation area, so you can see the drive first"),
    ("Job", "replacement / no heat — urgent / major repair / tune-up / thermostat or ductwork / AC"),
    ("Timing", "as soon as possible / within a week / this month / pricing for now"),
    ("Description", "what the furnace is doing, in the homeowner's own words, make and rough age when known"),
    ("Consent + time", "consent box ticked, with the date and time recorded in Edmonton time"),
]
for name, desc in fields:
    c.setFont(BOLD, 9)
    c.setFillColorRGB(*INK)
    c.drawString(M, y, name)
    c.setFont(REG, 9)
    c.setFillColorRGB(*MUTED)
    for i, ln in enumerate(wrap(desc, REG, 9, W - M - 150 - 6)):
        c.drawString(M + 150, y - (i * 10.0), ln)
        if i:
            y -= 10.0
    y -= 11.6

# ---------- what a request looks like ----------
# A labelled example. Every value is a string the request form itself prints: its own field
# names, its own placeholders ("First and last name", "780 555 0134", "T5K 1A1"), its own
# consent wording. Nothing here is invented and nothing here is a real request.
y -= 6
y = label(c, "What a request looks like — an example, not a real request", y)

ex_rows = [
    ("head", "EXAMPLE REQUEST  —  placeholder values, not a real request"),
    (("Name", "First and last name"), ("Phone", "780 555 0134"), ("Email", "you@example.com")),
    (("Postal code", "T5K 1A1   (area T5K)"), ("Job", "Furnace replacement"), None),
    (("Timing", "As soon as possible"), ("Consent + time", "ticked; date and time recorded")),
    (("Description", "Make and rough age if you know it. What it's doing — what a technician would want."),),
]
ex_top = y + 11
ex_h = 11 + (len(ex_rows) * 9.6) + 9
c.setFillColorRGB(*SOFT)
c.rect(M, ex_top - ex_h, W - 2 * M, ex_h, stroke=0, fill=1)
c.setStrokeColorRGB(*LINE)
c.setLineWidth(0.7)
c.rect(M, ex_top - ex_h, W - 2 * M, ex_h, stroke=1, fill=0)
c.setStrokeColorRGB(*AMBER_D)
c.setLineWidth(2.0)
c.line(M, ex_top, M, ex_top - ex_h)

X1, X2, X3 = M + 10, M + 200, M + 360
yy = ex_top - 13
for row in ex_rows:
    if row[0] == "head":
        c.setFont(BOLD, 7.2)
        c.setFillColorRGB(*AMBER_D)
        c.drawString(X1, yy, row[1])
    else:
        pairs = [p for p in row if p]
        for i, (k, v) in enumerate(pairs):
            xx = (X1, X2, X3)[i]
            c.setFont(BOLD, 8.0)
            c.setFillColorRGB(*INK)
            c.drawString(xx, yy, k)
            c.setFont(REG, 8.0)
            c.setFillColorRGB(*MUTED)
            c.drawString(xx + 4 + tw(k, BOLD, 8.0), yy, v)
    yy -= 9.6
y = ex_top - ex_h - 8

# ---------- qualification rule ----------
y = label(c, "A request is billable only when all four are true", y)

rules = [
    ("1.  The postal code is in your coverage area",
     "Edmonton T5A-T6X, or the metro codes T7X, T8A, T8B, T8N, T9E. Anything outside is not billed."),
    ("2.  The job is one you actually do",
     "Furnace replacement, no-heat, or a major furnace repair. Tune-ups and AC-only calls are filtered out; if one slips through it is free."),
    ("3.  The homeowner engages",
     "They answer your call or reply to you within 48 hours of receiving it."),
    ("4.  You claim it inside the window",
     "Six hours on a shared request; yours alone on the retainer. No claim, no charge."),
]
for head, body in rules:
    c.setFont(BOLD, 9.2)
    c.setFillColorRGB(*INK)
    c.drawString(M, y, head)
    y -= 10.6
    y = para(c, body, M + 14, y, W - M - 14 - M, size=8.6, leading=10.2, color=MUTED)
    y -= 4.0

# ---------- price boxes ----------
y = label(c, "The two ways to buy", y)
box_h = 96
gap = 14
bw = (W - 2 * M - gap) / 2.0
top = y + 4

for i, (tag, price, sub, bullets, accent) in enumerate([
    ("START HERE", "$45", "per qualified lead",
     ["Pay only for leads that pass the four rules.",
      "First three qualified leads free.",
      "Shared with at most one other contractor.",
      "Invoiced monthly by e-transfer, after delivery.",
      "Cancel by one email. No notice period."], AMBER_D),
    ("EXCLUSIVE AREA", "$400", "per month, your area only",
     ["Exclusive: every qualifying request in your",
      "cluster comes to you alone, no other contractor.",
      "A cluster is roughly 3-5 forward sortation areas.",
      "A month with zero requests is free.",
      "Month-to-month. Cancel before the month starts."], (0.15, 0.42, 0.31)),
]):
    x0 = M + i * (bw + gap)
    c.setFillColorRGB(*SOFT)
    c.rect(x0, top - box_h, bw, box_h, stroke=0, fill=1)
    c.setStrokeColorRGB(*LINE)
    c.setLineWidth(0.7)
    c.rect(x0, top - box_h, bw, box_h, stroke=1, fill=0)
    c.setStrokeColorRGB(*accent)
    c.setLineWidth(2.2)
    c.line(x0, top, x0 + bw, top)

    c.setFont(REG, 7.2)
    c.setFillColorRGB(*accent)
    c.drawString(x0 + 12, top - 15, tag)

    c.setFont(BOLD, 19.5)
    c.setFillColorRGB(*INK)
    c.drawString(x0 + 12, top - 37, price)
    c.setFont(REG, 8.6)
    c.setFillColorRGB(*MUTED)
    c.drawString(x0 + 12 + tw(price, BOLD, 19.5) + 7, top - 37, sub)

    yb = top - 52
    c.setFont(REG, 8.4)
    for b in bullets:
        c.setFillColorRGB(*MUTED)
        c.drawString(x0 + 12, yb, b)
        yb -= 9.4

y = top - box_h - 20

# ---------- how it reaches you + what we don't do ----------
colw = (W - 2 * M - gap) / 2.0
c.setFont(BOLD, 9)
c.setFillColorRGB(*INK)
c.drawString(M, y, "How it reaches you")
c.drawString(M + colw + gap, y, "What we do not do")

para(c, "A text and an email to the number and address you give us, the moment a request lands. "
        "You get six hours to claim it; unclaimed requests move to the next contractor on the list.",
     M, y - 11, colw, size=8.4, leading=9.9, color=MUTED)

para(c, "No bought lists and no scraped numbers. Every request comes from the homeowner filling in the form. "
        "No homeowner detail is sold or handed to anyone but the contractors quoting the job. No reviews or "
        "testimonials are written for this service.",
     M + colw + gap, y - 11, colw, size=8.4, leading=9.9, color=MUTED)

# ---------- how to start ----------
y2 = y - 56
y2 = label(c, "How to start", y2)
sw = (W - 2 * M - 2 * 12) / 3.0
steps = [
    ("Send one email", "Business name, Alberta trade licence number, the postal codes you cover, and how you want requests delivered."),
    ("We list your codes", "You go on the list for those areas. On the retainer, nobody else gets your cluster at all."),
    ("Requests arrive", "Text and email the moment one lands. Six-hour claim window, then it moves on to the next contractor."),
]
step_bottom = y2
for i, (h, b) in enumerate(steps):
    x0 = M + i * (sw + 12)
    c.setFont(BOLD, 8.8)
    c.setFillColorRGB(*INK)
    c.drawString(x0, y2, "%d.  %s" % (i + 1, h))
    step_bottom = min(step_bottom, para(c, b, x0, y2 - 10.5, sw, size=8.2, leading=9.6, color=MUTED))

# ---------- the way back to the site (a real link annotation) ----------
link_y = step_bottom - 12
prefix = "The offer, coverage list, the same example and both reply buttons:  "
c.setFont(REG, 8.0)
c.setFillColorRGB(*MUTED)
c.drawString(M, link_y, prefix)
lx = M + tw(prefix, REG, 8.0)
c.setFont(BOLD, 8.0)
c.setFillColorRGB(*AMBER_D)
url_text = "maxhemmerich.github.io/edmonton-furnace-quotes"
c.drawString(lx, link_y, url_text)
c.linkURL(SITE, (lx - 1, link_y - 3, lx + tw(url_text, BOLD, 8.0) + 1, link_y + 9), thickness=0, relative=0)
c.setStrokeColorRGB(*AMBER_D)
c.setLineWidth(0.5)
c.line(lx, link_y - 3, lx + tw(url_text, BOLD, 8.0), link_y - 3)

y_end = link_y

# ---------- footer ----------
rule(c, 70, color=(0.85, 0.87, 0.89))
c.setFont(REG, 8.2)
c.setFillColorRGB(*GREY)
c.drawString(M, 56, "Max Hemmerich  ·  maxhemmerich@gmail.com  ·  Edmonton, Alberta")
c.drawString(M, 44, "Ask for the next batch, or ask what requests have come through — the count is real and both of us can check it.")
c.setFont(REG, 7.4)
c.drawString(M, 31, "Requests are gathered with the homeowner's consent and passed on only to quote the work. Contractors quoting")
c.drawString(M, 21, "are expected to hold a valid Alberta trade licence for that work.")

if y_end < BOTTOM_LIMIT:
    raise SystemExit("REFUSED: content would reach y=%.1f and collide with the footer "
                     "(limit %.1f). Re-cut the spacing, do not shrink the text." % (y_end, BOTTOM_LIMIT))

c.showPage()
c.save()
print("wrote", OUT, "| content ends at y=%.1f" % y_end)
