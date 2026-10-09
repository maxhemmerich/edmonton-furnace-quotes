#!/usr/bin/env python
# tools/check_citations_cover.py - keep the citation checks in step with the pages they protect.
#
#   py -3.10 tools/check_citations_cover.py             # check the tree
#   py -3.10 tools/check_citations_cover.py --root DIR  # check a copy (used to prove it can fail)
#
# Why this exists: tools/check_rebates_page.py and tools/check_permit_page.py guard the government
# quotations printed on alberta-furnace-rebates.html and furnace-permit-edmonton.html - but each
# hard-codes its phrases. Edit a quotation on a page without editing its checker and the checker
# goes on passing while it silently stops protecting that line: the exact failure it exists to
# catch, one level up. This is the instrument that watches the watchers.
#
# It is OFFLINE: it never fetches a source page. Its whole job is that the page and its checker
# still describe the same quotations. (The live HTTP check that each phrase is still on its named
# source is items 26/28 - check_rebates_page.py and check_permit_page.py.)
#
# For each page it asserts, against that page's own checker's CITED list:
#
#   A. URL COVERAGE   - every source URL the page links with <a class="kv"> is a URL the checker
#                       guards. A page citing a new source the checker does not know is a failure.
#   B. QUOTE COVERAGE - every SOURCED quotation on the page appears (whitespace-normalised,
#                       case-insensitive, trailing sentence punctuation ignored) in the checker's
#                       CITED phrases. A quotation edited or added on the page without the checker
#                       is a failure, named with its line.
#   C. PAGE COVERAGE  - every CITED phrase still appears in the page's own visible text, so a
#                       checker phrase whose line was deleted from the page cannot keep "passing".
#
# What it deliberately does NOT count as a sourced quotation: the page's own scare-quotes and the
# short labels used inside its "Source:" sentences to say which line comes from which URL (e.g. the
# "full cost" line is from ...). Those are listed by name in NON_CITATION below, and the tool says
# out loud when one of them leaves the page so the exclusion cannot quietly go stale. Everything
# else between &ldquo; and &rdquo; on a citation page is treated as a quotation that must be guarded.
import html
import importlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "--root" in sys.argv:
    ROOT = sys.argv[sys.argv.index("--root") + 1]

# page file  ->  checker module under tools/ whose CITED list guards it
PAGES = [
    ("alberta-furnace-rebates.html", "check_rebates_page"),
    ("furnace-permit-edmonton.html", "check_permit_page"),
]

# Quoted spans on a page that are NOT source quotations: the page's own scare-quotes, and the short
# labels it uses inside a "Source:" sentence to say which line came from which URL. Keyed by the
# page file; values are already in canonical form (lower-case, whitespace collapsed). Keep this list
# short and current - everything not named here must be covered by the checker's CITED list.
NON_CITATION = {
    "alberta-furnace-rebates.html": {
        "full cost",             # label: 'the "full cost" line is from <the Greener Homes page>'
        "no-cost home retrofits",  # label: 'the "no-cost home retrofits" ... lines are from <CGHAP>'
        "began delivery",        # label: 'and "began delivery" lines are from <CGHAP page>'
        "not a rebate",          # label: 'On the "not a rebate" point, the City of Calgary ...'
        "alberta rebate",        # scare-quote: 'seen an "Alberta rebate" advertised in 2026'
    },
    "furnace-permit-edmonton.html": set(),
}

_SPAN = re.compile(r"&ldquo;(.*?)&rdquo;", re.S)
_NOTE = re.compile(r'<div[^>]*\bclass="[^"]*\bnote\b[^"]*"[^>]*>.*?</div>', re.S)
_ANCHOR = re.compile(r"<a\b[^>]*>", re.I)
_KV_CLASS = re.compile(r'\bclass="[^"]*\bkv\b[^"]*"')
_HREF = re.compile(r'\bhref="([^"]*)"')
_SCRIPT = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def canon(s):
    """One comparison key for a quotation or a phrase: tags off, entities decoded, whitespace
    collapsed, surrounding quotation marks and a trailing sentence punctuation mark dropped,
    case-folded. Trailing full stops are dropped because a checker phrase may omit the period the
    page prints inside the quote ('...territories' vs '...territories.')."""
    s = html.unescape(s)
    s = _TAG.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    s = s.strip("\u201c\u201d\"' ")
    s = s.rstrip(".,;:!? ")
    return s.lower()


def visible_text(src):
    s = _SCRIPT.sub(" ", src)
    s = _TAG.sub(" ", s)
    s = html.unescape(s)
    return _WS.sub(" ", s).strip()


def quoted_spans(src):
    """(char_offset, raw_inner_text) for every &ldquo; ... &rdquo; span."""
    return [(m.start(), m.group(1)) for m in _SPAN.finditer(src)]


def note_ranges(src):
    return [(m.start(), m.end()) for m in _NOTE.finditer(src)]


def kv_urls(src):
    urls = []
    for m in _ANCHOR.finditer(src):
        tag = m.group(0)
        if _KV_CLASS.search(tag):
            h = _HREF.search(tag)
            if h:
                urls.append(h.group(1))
    return urls


def line_of(src, pos):
    return src.count("\n", 0, pos) + 1


def check_page(page_file, checker_name, out=print):
    """Return the number of failures for one page. Print one line per finding."""
    path = os.path.join(ROOT, page_file)
    if not os.path.exists(path):
        out("FAIL  page missing: %s" % path)
        return 1
    src = open(path, encoding="utf-8").read()

    sys.path.insert(0, os.path.join(ROOT, "tools"))
    mod = importlib.import_module(checker_name)
    cited = mod.CITED
    guarded_urls = {u for u, _ in cited}
    phrases = [p for _, ps in cited for p in ps]
    covered = {canon(p) for p in phrases}

    out("%s  (guarded by tools/%s.py - %d URL(s), %d phrase(s))"
        % (page_file, checker_name, len(guarded_urls), len(phrases)))

    failures = 0

    # A. every source URL on the page is guarded
    for u in kv_urls(src):
        if u not in guarded_urls:
            failures += 1
            out("  FAIL  A  source URL not in the checker: %s" % u)

    # B. every sourced quotation is covered by a CITED phrase
    notes = note_ranges(src)
    spans = quoted_spans(src)
    exclusions = NON_CITATION.get(page_file, set())
    covered_spans = 0
    for pos, inner in spans:
        key = canon(inner)
        if not key:
            continue
        if any(a <= pos < b for a, b in notes):
            continue                      # a scare-quote inside the page's own note block
        if key in exclusions:
            continue                      # a named non-citation (see NON_CITATION)
        covered_spans += 1
        if key in covered:
            out("  ok    B  quotation covered: %s" % (key[:72] + ("..." if len(key) > 72 else "")))
        else:
            failures += 1
            out("  FAIL  B  SOURCED QUOTATION NOT IN THE CHECKER (line %d):" % line_of(src, pos))
            out("           %r" % canon(inner))
            out("           (add it to tools/%s.py CITED, or it is no longer a quotation)"
                % checker_name)

    # C. every CITED phrase still appears on the page
    page_text = visible_text(src).lower()
    for p in phrases:
        if canon(p) not in page_text:
            failures += 1
            out("  FAIL  C  CITED phrase no longer on the page: %r" % p)
            out("           (tools/%s.py guards a line %s no longer prints)"
                % (checker_name, page_file))

    # stale exclusions are printed, not fatal: they name the page's own prose, not a citation
    present = {canon(inner) for _, inner in spans}
    for key in sorted(exclusions):
        if key not in present:
            out("  NOTE  exclusion no longer on the page (prose changed): %r" % key)

    out("  -> %d sourced quotation(s) checked on this page, %d failure(s)"
        % (covered_spans, failures))
    return failures


def main():
    print("check_citations_cover.py - do the citation checks still cover their pages?")
    print("root: %s" % ROOT)
    print("-" * 72)
    total = 0
    for page_file, checker_name in PAGES:
        total += check_page(page_file, checker_name)
        print("-" * 72)
    if total:
        print("RESULT: FAILED - %d uncovered item(s). A page and its checker have drifted apart: "
              "re-quote the page and update the checker's CITED list in the same commit." % total)
        return 1
    print("RESULT: PASSED - every source URL and every sourced quotation on both pages is covered "
          "by its checker's CITED list, and every CITED phrase is still printed on its page.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
