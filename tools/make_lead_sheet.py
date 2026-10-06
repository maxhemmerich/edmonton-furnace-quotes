# Builds the one-page contractor lead sheet for Edmonton Furnace Quotes.
# Run: py -3.10 tools/make_lead_sheet.py
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics

W, H = letter
M = 46.0
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "edmonton-furnace-lead-sheet.pdf")

NAVY = (0.055, 0.082, 0.114)
AMBER = (0.949, 0.627, 0.239)
AMBER_D = (0.722, 0.478, 0.169)
INK = (0.09, 0.11, 0.14)
GREY = (0.42, 0.47, 0.53)
LINE = (0.80, 0.83, 0.86)

REG, BOLD = "Helvetica", "Helvetica-Bold"


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
c.setSubject("What a furnace quote request contains, when it is billable, and the price")

# ---------- header band ----------
c.setFillColorRGB(*NAVY)
c.rect(0, H - 108, W, 108, stroke=0, fill=1)
c.setFillColorRGB(*AMBER)
c.rect(0, H - 111, W, 3, stroke=0, fill=1)

c.setFont(BOLD, 15.5)
c.setFillColorRGB(1, 1, 1)
c.drawString(M, H - 46, "EDMONTON FURNACE QUOTES")

c.setFont(REG, 8.8)
c.setFillColorRGB(0.66, 0.72, 0.79)
c.drawString(M, H - 63, "Lead sheet  ·  furnace replacement and no-heat requests  ·  Edmonton, Alberta")

c.setFont(REG, 8.8)
c.setFillColorRGB(0.66, 0.72, 0.79)
c.drawString(M, H - 80, "What a request contains, when it is billable, and what it costs.")

c.setFont(BOLD, 13)
c.setFillColorRGB(*AMBER)
c.drawRightString(W - M, H - 50, "$45 / qualified lead")
c.setFont(REG, 8.6)
c.setFillColorRGB(0.66, 0.72, 0.79)
c.drawRightString(W - M, H - 66, "or $400 / month, your area exclusively")
c.drawRightString(W - M, H - 80, "first three qualified leads free")

# ---------- what a lead contains ----------
y = label(c, "What a lead contains", H - 140)

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
    c.setFillColorRGB(0.30, 0.35, 0.40)
    for i, ln in enumerate(wrap(desc, REG, 9, W - M - 150 - 6)):
        c.drawString(M + 150, y - (i * 10.4), ln)
        if i:
            y -= 10.4
    y -= 13.6

# ---------- qualification rule ----------
y -= 6
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
    y -= 11.6
    y = para(c, body, M + 14, y, W - M - 14 - M, size=8.6, leading=10.8, color=(0.30, 0.35, 0.40))
    y -= 5.5

# ---------- price boxes ----------
y -= 4
y = label(c, "The two ways to buy", y)
box_h = 104
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
    c.setFillColorRGB(0.965, 0.972, 0.980)
    c.rect(x0, top - box_h, bw, box_h, stroke=0, fill=1)
    c.setStrokeColorRGB(*LINE)
    c.setLineWidth(0.7)
    c.rect(x0, top - box_h, bw, box_h, stroke=1, fill=0)
    c.setStrokeColorRGB(*accent)
    c.setLineWidth(2.2)
    c.line(x0, top, x0 + bw, top)

    c.setFont(REG, 7.2)
    c.setFillColorRGB(*accent)
    c.drawString(x0 + 12, top - 16, tag)

    c.setFont(BOLD, 21)
    c.setFillColorRGB(*INK)
    c.drawString(x0 + 12, top - 40, price)
    c.setFont(REG, 8.6)
    c.setFillColorRGB(0.30, 0.35, 0.40)
    c.drawString(x0 + 12 + tw(price, BOLD, 21) + 7, top - 40, sub)

    yy = top - 56
    c.setFont(REG, 8.4)
    for b in bullets:
        c.setFillColorRGB(0.30, 0.35, 0.40)
        c.drawString(x0 + 12, yy, b)
        yy -= 10.2

y = top - box_h - 24

# ---------- how it reaches you + what we don't do ----------
colw = (W - 2 * M - gap) / 2.0
c.setFont(BOLD, 9)
c.setFillColorRGB(*INK)
c.drawString(M, y, "How it reaches you")
c.drawString(M + colw + gap, y, "What we do not do")

para(c, "A text and an email to the number and address you give us, the moment a request lands. "
        "You get six hours to claim it; unclaimed requests move to the next contractor on the list.",
     M, y - 12, colw, size=8.4, leading=10.4, color=(0.30, 0.35, 0.40))

para(c, "No bought lists and no scraped numbers. Every request comes from the homeowner filling in the form. "
        "No homeowner detail is sold or handed to anyone but the contractors quoting the job. No reviews or "
        "testimonials are written for this service.",
     M + colw + gap, y - 12, colw, size=8.4, leading=10.4, color=(0.30, 0.35, 0.40))

# ---------- how to start ----------
y2 = y - 66
y2 = label(c, "How to start", y2)
sw = (W - 2 * M - 2 * 12) / 3.0
steps = [
    ("Send one email", "Business name, Alberta trade licence number, the postal codes you cover, and how you want requests delivered."),
    ("We list your codes", "You go on the list for those areas. On the retainer, nobody else gets your cluster at all."),
    ("Requests arrive", "Text and email the moment one lands. Six-hour claim window, then it moves on to the next contractor."),
]
for i, (h, b) in enumerate(steps):
    x0 = M + i * (sw + 12)
    c.setFont(BOLD, 8.8)
    c.setFillColorRGB(*INK)
    c.drawString(x0, y2, "%d.  %s" % (i + 1, h))
    para(c, b, x0, y2 - 11, sw, size=8.2, leading=10.0, color=(0.30, 0.35, 0.40))

# ---------- footer ----------
rule(c, 70, color=(0.85, 0.87, 0.89))
c.setFont(REG, 8.2)
c.setFillColorRGB(*GREY)
c.drawString(M, 56, "Max Hemmerich  ·  maxhemmerich@gmail.com  ·  Edmonton, Alberta")
c.drawString(M, 44, "Ask for the next batch, or ask what requests have come through — the count is real and both of us can check it.")
c.setFont(REG, 7.4)
c.drawString(M, 31, "Requests are gathered with the homeowner's consent and passed on only to quote the work. Contractors quoting")
c.drawString(M, 21, "are expected to hold a valid Alberta trade licence for that work.")

c.showPage()
c.save()
print("wrote", OUT)
