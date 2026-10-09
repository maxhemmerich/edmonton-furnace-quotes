#!/usr/bin/env python3
"""Guard the intent hand-off in assets/app.js (the job pre-select).

Offline. The hand-off maps four single-intent pages to one option in the form's
"what do you need?" menu, by file name. Three things can rot silently:

  A. a mapped job string stops matching the option it names in index.html, so the
     pre-select quietly does nothing;
  B. a mapped page is renamed or removed, so the key can never fire;
  C. a mapped page is not in sitemap.xml, so the page the map trusts is not one
     the site actually publishes (or was dropped from it).

This asserts all three, so the map cannot drift away from the form and the pages.

Run:  py -3.10 tools/check_intent_prefill.py
"""
import os, re, sys, xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "assets", "app.js")
INDEX = os.path.join(ROOT, "index.html")
SITEMAP = os.path.join(ROOT, "sitemap.xml")

fails = []
oks = 0


def ok(msg):
    global oks
    oks += 1
    print("  ok    " + msg)


def bad(msg):
    fails.append(msg)
    print("  FAIL  " + msg)


def read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return fh.read()


def main():
    app = read(APP)

    # The map literal: the block between "var FROM_PAGE_JOB = {" and the first "};".
    m = re.search(r"FROM_PAGE_JOB\s*=\s*\{(.*?)\}\s*;", app, re.S)
    if not m:
        bad("assets/app.js no longer carries a FROM_PAGE_JOB map")
        return
    body = m.group(1)
    pairs = re.findall(r'"([^"]+\.html)"\s*:\s*"((?:[^"\\]|\\.)*)"', body)
    if not pairs:
        bad("FROM_PAGE_JOB carries no page -> job pairs")
        return
    ok("FROM_PAGE_JOB carries %d page -> job pair(s)" % len(pairs))

    # JS string escapes (\u2014) -> the character it names.
    def unesc(s):
        return re.sub(r"\\u([0-9a-fA-F]{4})", lambda x: chr(int(x.group(1), 16)), s)

    mapped = [(page, unesc(job)) for page, job in pairs]

    # A. every mapped job string is an option in index.html's #job select.
    idx = read(INDEX)
    sel = re.search(r'<select[^>]*id="job"[^>]*>(.*?)</select>', idx, re.S)
    if not sel:
        bad("index.html has no #job <select>")
        return
    options = [unesc(o) for o in re.findall(r"<option[^>]*>(.*?)</option>", sel.group(1), re.S)]
    options = [o.strip() for o in options]
    ok("index.html #job carries %d option(s)" % len(options))
    for page, job in mapped:
        if job in options:
            ok("A  %s -> %r is an option in index.html" % (page, job))
        else:
            bad("A  %s -> %r is NOT an option in index.html (options: %s)" % (page, job, options))

    # published pages, from sitemap.xml
    tree = ET.parse(SITEMAP)
    locs = [(e.text or "").strip() for e in tree.getroot().iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    leaves = set(l.split("/")[-1] or "index.html" for l in locs)

    # B. every mapped page exists on disk.
    for page, job in mapped:
        if os.path.isfile(os.path.join(ROOT, page)):
            ok("B  %s exists on disk" % page)
        else:
            bad("B  %s is mapped but does not exist on disk" % page)

    # C. every mapped page is published (in sitemap.xml).
    for page, job in mapped:
        if page in leaves:
            ok("C  %s is listed in sitemap.xml" % page)
        else:
            bad("C  %s is mapped but not in sitemap.xml" % page)

    # D. every mapped page actually offers the form (so the hand-off can happen).
    for page, job in mapped:
        p = os.path.join(ROOT, page)
        if not os.path.isfile(p):
            continue
        if 'href="index.html#request"' in read(p):
            ok("D  %s offers the form (index.html#request)" % page)
        else:
            bad("D  %s is mapped but carries no index.html#request link" % page)

    print("")
    if fails:
        print("RESULT: FAILED - %d failure(s), %d ok" % (len(fails), oks))
        for f in fails:
            print("   - " + f)
        sys.exit(1)
    print("RESULT: PASSED - %d ok, every mapped page offers the form and every mapped job is an option" % oks)


if __name__ == "__main__":
    main()
