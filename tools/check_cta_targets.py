#!/usr/bin/env python
# tools/check_cta_targets.py - every "request form" link must open the form.
#
# Why this exists: the site's own convention is that a link offering the request form
# carries the fragment (index.html#request), which is what the hero CTA on every intent
# page uses. Nine pages carried a footer line reading "The request form ->" whose href was
# a bare index.html, so tapping it landed at the top of the landing page - on a phone, the
# form is a screen further down - while the same page's hero CTA went straight to the form.
# That is a link that promises the form and does not deliver it. It was found by hand-driving
# the live funnel on 2026-10-09 ~11:20 and fixed the same wake; this is the check that keeps
# it fixed.
#
#   py -3.10 tools/check_cta_targets.py            # check the tree
#   py -3.10 tools/check_cta_targets.py --root DIR # check a copy (used to prove it can fail)
#
# It asserts, for every page listed in sitemap.xml (so a new page cannot be skipped):
#   * no anchor whose visible text mentions the request form points at a bare landing page
#     (index.html / "./" / the site root) - it must carry the #request fragment;
#   * every page other than the landing page itself and contractors.html carries at
#     least one link to index.html#request (a route to the form that a visitor can take).
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "--root" in sys.argv:
    ROOT = sys.argv[sys.argv.index("--root") + 1]

BASE = "https://maxhemmerich.github.io/edmonton-furnace-quotes/"
sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
locs = re.findall(r"<loc>\s*(.*?)\s*</loc>", sm)
pages = []
for loc in locs:
    name = loc.replace(BASE, "").strip("/") or "index.html"
    if not name.endswith(".html"):
        name = "index.html"
    pages.append(name)

fails, passes = [], []
def check(ok, label):
    (passes if ok else fails).append(label)

print("pages from sitemap.xml: %d -> %s" % (len(pages), ", ".join(pages)))

FORM_RE = re.compile(r"request\s+form|request\s+a\s+furnace\s+quote|go\s+to\s+the\s+request", re.I)
BARE_LANDING = {"index.html", "./", ".", "", BASE, BASE.rstrip("/")}

for p in pages:
    path = os.path.join(ROOT, p)
    if not os.path.exists(path):
        check(False, "%s exists (listed in sitemap.xml)" % p)
        continue
    html = open(path, encoding="utf-8").read()

    n_form_links = 0
    n_to_form = 0
    for m in re.finditer(r"<a\b[^>]*>(.*?)</a>", html, re.S):
        tag = m.group(0)
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()
        hm = re.search(r'href\s*=\s*"([^"]*)"', tag, re.I)
        href = hm.group(1) if hm else ""
        if href.endswith("index.html#request") or href == "#request":
            n_to_form += 1
        if FORM_RE.search(text):
            n_form_links += 1
            ok = href.endswith("#request")
            check(ok, '%s: "%s" -> %s carries the #request fragment' % (p, text[:42], href))

    if p not in ("index.html", "contractors.html"):
        check(n_to_form >= 1,
              "%s carries at least one index.html#request link (%d)" % (p, n_to_form))

for x in passes:
    print("  ok    %s" % x)
for x in fails:
    print("  FAIL  %s" % x)
print("\n%d/%d checks passed on %s" % (len(passes), len(passes) + len(fails), ROOT))
sys.exit(1 if fails else 0)
