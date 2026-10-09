#!/usr/bin/env python
# tools/check_permit_page.py - rot check for every City of Edmonton page quoted on
# furnace-permit-edmonton.html.
#
#   py -3.10 tools/check_permit_page.py
#
# Same contract as tools/check_rebates_page.py: for each cited URL, assert HTTP 200 AND that the
# quoted phrase is still present as visible text, failing loudly with the URL and the phrase.
# It re-uses that tool's fetcher and matcher so the two checks cannot drift apart.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_rebates_page import check  # noqa: E402

GAS = "https://www.edmonton.ca/residential_neighbourhoods/gas-permit"
HVAC = ("https://www.edmonton.ca/residential_neighbourhoods/heating-ventilation-permit")

# Every phrase furnace-permit-edmonton.html attributes to each City page. Any edit to a
# quotation on that page must be mirrored here in the same commit.
CITED = [
    (GAS, [
        "A gas permit is required under the provincial Safety Codes Act when installing, "
        "altering or relocating gas equipment such as: furnaces, water heaters, meters, "
        "piping and lines, dryers, BBQs, garage heaters, ranges, patio heaters, fireplaces, "
        "space heaters, and fire pits.",
        "A homeowner may not install a new gas line. Only a qualified contractor may do the work.",
        "A homeowner gas permit is for renovations and or re-test of an existing gas system in "
        "a single detached house only.",
        "A permit must be applied for and issued prior to starting any work and requesting an "
        "inspection.",
        "Contractors must be licensed with the City of Edmonton.",
    ]),
    (HVAC, [
        "A heating and ventilating permit is required under the Safety Codes Permit Bylaw when "
        "installing, repairing, or altering any heating, ventilation, or air conditioning "
        "undertaking such as but not limited to",
        "A permit must be obtained before starting any work and booking an inspection.",
        "A heating and ventilating permit is not required for: Installation of a gas-fired or "
        "solid-fuel-burning appliance, unless there is duct work attached to the appliance "
        "other than the combustion air duct.",
        "A Home Improvement Permit is required.",
    ]),
]


def main():
    print("check_permit_page.py - quotations cited on furnace-permit-edmonton.html")
    print("source URLs: %d   phrases: %d" % (len(CITED), sum(len(p) for _, p in CITED)))
    print("-" * 72)
    failures = check(CITED)
    print("-" * 72)
    if failures:
        print("RESULT: FAILED - %d quotation(s) no longer present on their named City page. "
              "furnace-permit-edmonton.html must be re-read against the live pages." % failures)
        return 1
    print("RESULT: PASSED - every quoted phrase is still present on its named City of Edmonton "
          "page, every source answers HTTP 200.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
