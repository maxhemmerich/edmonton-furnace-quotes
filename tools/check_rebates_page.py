#!/usr/bin/env python
# tools/check_rebates_page.py - rot check for every government page quoted on
# alberta-furnace-rebates.html.
#
#   py -3.10 tools/check_rebates_page.py
#
# For each cited government URL this fetches the page and asserts BOTH:
#   1. HTTP 200, and
#   2. the quoted phrase is still present on the page.
# It fails loudly, naming the URL and the exact phrase, when a quotation rots.
#
# Why this exists: the page prints a figure or an eligibility line only as a quotation from a
# named government page, with the URL and the date it was read ("9 October 2026"). A government
# page can move, change or close. A quotation whose source no longer says it is exactly the
# invented-figure failure the project forbids -- so the quotation is checked, not trusted.
#
# Matching rule: the served HTML is reduced to the text a reader sees -- tags become spaces,
# HTML entities are decoded, runs of whitespace collapse to one space -- and the phrase is
# looked for in that text, whitespace-normalised the same way. A quotation is "present" only if
# it is present as visible text. Nothing here is a paraphrase check: the phrase must appear
# character-for-character (modulo whitespace).
#
# When a check fails, the honest fix is NOT to loosen the check. Re-read the government page,
# and either re-quote what it now says (updating the "read on" date on the page) or remove the
# line. The page must never carry a figure its named source does not.
import html as _html
import re
import sys
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
READ_ON = "9 October 2026"

# The citations as they stand on alberta-furnace-rebates.html. One tuple per source URL; the
# list is every phrase the page attributes to that URL. Any edit to a quotation on the page
# must be reflected here in the same commit, or this check no longer protects anything.
CITED = [
    ("https://natural-resources.canada.ca/energy-efficiency/home-energy-efficiency/"
     "canada-greener-homes-initiative/canada-greener-homes-grant-glance-0",
     ["Applications were open from May 2021 to February 2024, and the deadline for "
      "participants to submit documentation was December 31, 2025."]),

    ("https://natural-resources.canada.ca/energy-efficiency/home-energy-efficiency/"
     "canada-greener-homes-initiative",
     ["No further applications can be approved. Applications that have already been approved "
      "are not affected.",
      "The full cost of recommended retrofits will be covered for eligible households. That "
      "means that participants will not be asked to pay out of pocket to participate.",
      "January 20, 2026, was the last day to apply for this program."]),

    ("https://natural-resources.canada.ca/energy-efficiency/home-energy-efficiency/"
     "canada-greener-homes-initiative/oil-heat-pump-affordability-program",
     ["You may be eligible to receive an upfront payment of up to $10,000 to switch from oil "
      "heating to new, energy-efficient heat pumps",
      "July 31, 2026, was the last day to apply to the Oil to Heat Pump Affordability program."]),

    ("https://natural-resources.canada.ca/energy-efficiency/home-energy-efficiency/"
     "canada-greener-homes-initiative/"
     "eligibility-criteria-oil-heat-pump-affordability-program",
     ["Heating fuels that are ineligible for this program include natural gas, propane, coal "
      "and wood."]),

    ("https://natural-resources.canada.ca/energy-efficiency/home-energy-efficiency/"
     "canada-greener-homes-initiative/canada-greener-homes-affordability-program",
     ["provides low-to-median-income homeowners and tenants with no-cost home retrofits, such "
      "as insulation and heat pumps",
      "began delivery in 2025 through participating provinces and territories"]),

    ("https://ceip.abmunis.ca/residential/locations/edmonton",
     ["Residential property owners and owners of multi-unit residential buildings (MURBs) can "
      "finance a minimum of $3,000 and up to $50,000 of retrofits through the program.",
      "High-efficiency gas furnace (unless combined with a heat pump)"]),

    ("https://www.calgary.ca/environment/programs/clean-energy-improvement-program.html",
     ["CEIP is not a rebate program. You must pay back all of the funding that you borrow."]),

    ("https://www.alberta.ca/alberta-energy-rebate",
     ["to help with the cost of groceries, fuel and other everyday essentials"]),
]

_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def visible_text(src):
    """The text a reader sees: tags -> space, entities decoded, whitespace collapsed."""
    text = _TAG.sub(" ", src)
    text = _html.unescape(text)
    return _WS.sub(" ", text).strip()


def normalise(s):
    return _WS.sub(" ", _html.unescape(s)).strip()


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept-Language": "en-CA,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def check(cited, timeout=30, out=print):
    """Return the number of failures. Print one line per URL and one per phrase."""
    failures = 0
    for url, phrases in cited:
        try:
            status, body = fetch(url, timeout=timeout)
        except urllib.error.HTTPError as e:
            out("FAIL  HTTP %s   %s" % (e.code, url))
            failures += len(phrases)
            continue
        except Exception as e:
            out("FAIL  fetch error (%s: %s)   %s" % (type(e).__name__, e, url))
            failures += len(phrases)
            continue
        if status != 200:
            out("FAIL  HTTP %s   %s" % (status, url))
            failures += len(phrases)
            continue
        out("ok    HTTP 200   %s" % url)
        text = visible_text(body)
        for phrase in phrases:
            if normalise(phrase) in text:
                out("  ok    phrase present")
            else:
                failures += 1
                out("  FAIL  PHRASE NOT ON PAGE: %r" % phrase)
                out("        source URL: %s" % url)
                out("        (read on %s; re-read the page and re-quote or delete the line)"
                    % READ_ON)
    return failures


def main():
    print("check_rebates_page.py - quotations cited on alberta-furnace-rebates.html")
    print("source URLs: %d   phrases: %d" % (len(CITED), sum(len(p) for _, p in CITED)))
    print("-" * 72)
    failures = check(CITED)
    print("-" * 72)
    if failures:
        print("RESULT: FAILED - %d quotation(s) no longer present on their named source. "
              "alberta-furnace-rebates.html must be re-read against the live government pages."
              % failures)
        return 1
    print("RESULT: PASSED - every quoted phrase is still present on its named source, "
          "every source answers HTTP 200.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
