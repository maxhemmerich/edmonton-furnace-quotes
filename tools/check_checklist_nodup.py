#!/usr/bin/env python
# tools/check_checklist_nodup.py - the gate for the homeowner "what your written furnace quote
# should contain" checklist (a keepable one-pager + its front-door page).
#
# Why this exists: the checklist is drawn from lists the site already prints, so by construction it
# carries nothing new. The one thing it must NOT be is a re-cut of a whole page - the thin duplicate
# this repo has already refused twice (see NEXT.md item 29). This measures exactly that: how big the
# checklist is next to each page it is drawn from, and how much of it each page already prints.
#
#   py -3.10 tools/check_checklist_nodup.py
#   py -3.10 tools/check_checklist_nodup.py --items FILE   # score a candidate (JSON array of strings)
#   py -3.10 tools/check_checklist_nodup.py --root DIR     # score a copy of the tree
#
# It reads the two written-quote lists straight out of the pages:
#   furnace-repair.html      <section id="quote">   -> the 5 written-repair-quote items
#   furnace-replacement.html <section id="quote">   -> the 5 written-replacement-quote items
# and reports, for their union ("the checklist"):
#   * coverage   - how many checklist items each page already prints
#   * size       - the checklist as a share of each page's visible body words. "Merely repeats a
#                  whole page" would show up here as ~100%; a section shows up small.
#   * novelty    - checklist items printed nowhere on the site (expected 0: the list is drawn from
#                  the pages, and that is the point - it must not invent anything).
# Verdict is THIN DUPLICATE - and the tool exits 1 - only when the checklist reproduces a whole
# page (>= 50% of a source page's body words); that is the case the order says not to ship.
import os, re, html, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "--root" in sys.argv:
    ROOT = sys.argv[sys.argv.index("--root") + 1]

SOURCES = ["furnace-repair.html", "furnace-replacement.html", "repair-or-replace.html"]
WHOLE_PAGE_SHARE = 50.0  # % of a page's body words at which "checklist" == "that page"


def read(name):
    return open(os.path.join(ROOT, name), encoding="utf-8").read()


def norm(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    for a, b in (("\u2014", "-"), ("\u2013", "-"), ("\u2019", "'"), ("\u201c", '"'), ("\u201d", '"')):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip().lower()


def section(doc, sid):
    m = re.search(r'<section id="%s">(.*?)</section>' % re.escape(sid), doc, re.S)
    return m.group(1) if m else ""


def list_items(block):
    ul = re.search(r'<ul class="checks"[^>]*>(.*?)</ul>', block, re.S)
    return [norm(li) for li in re.findall(r"<li[^>]*>(.*?)</li>", ul.group(1), re.S)] if ul else []


def body_words(doc):
    body = re.sub(r"<script.*?</script>", " ", doc, flags=re.S)
    body = re.sub(r"<style.*?</style>", " ", body, flags=re.S)
    return len(norm(body).split())


texts = {s: norm(read(s)) for s in SOURCES}
bodies = {s: body_words(read(s)) for s in SOURCES}

if "--items" in sys.argv:
    checklist = [norm(x) for x in json.load(open(sys.argv[sys.argv.index("--items") + 1], encoding="utf-8"))]
    src = "candidate file"
else:
    checklist = list_items(section(read("furnace-repair.html"), "quote")) + \
                list_items(section(read("furnace-replacement.html"), "quote"))
    src = "the two pages' own quote lists"

if not checklist:
    sys.exit("no checklist items to score")

cw = sum(len(i.split()) for i in checklist)
print("checklist      : %d items, %d words  (%s)\n" % (len(checklist), cw, src))

shares = {}
for s in SOURCES:
    hit = [i for i in checklist if i in texts[s]]
    shares[s] = 100.0 * cw / max(1, bodies[s])
    print("%-26s %2d/%d items already printed (%3.0f%% of the checklist);  checklist = %5.1f%% of the page's body words"
          % (s, len(hit), len(checklist), 100.0 * len(hit) / len(checklist), shares[s]))

novel = [i for i in checklist if not any(i in texts[s] for s in SOURCES)]
print("\nnovel items (printed nowhere on the site): %d/%d" % (len(novel), len(checklist)))
print("checklist size vs. the smallest source page: %.1f%%" % min(shares.values()))

verdict = "THIN DUPLICATE" if max(shares.values()) >= WHOLE_PAGE_SHARE else "OK - re-cut of the pages' own lists, not a page"
print("VERDICT: %s" % verdict)
if verdict.startswith("THIN DUPLICATE"):
    print("  -> the checklist reproduces a whole page; do not ship it as a page or handout.")
else:
    print("  -> no source page is reproduced: the checklist is the site's two quote lists on one\n"
          "     page (novelty is expected to be 0 - it is drawn from those pages on purpose).")
sys.exit(1 if verdict.startswith("THIN DUPLICATE") else 0)
