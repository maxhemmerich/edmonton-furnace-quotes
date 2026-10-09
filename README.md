# Edmonton Furnace Quotes

**Live: https://maxhemmerich.github.io/edmonton-furnace-quotes/**

One short form, sent to Edmonton heating contractors who do furnace replacement and repair;
a quote-request service, not a contractor.

Quote-request intake for furnace replacement and no-heat jobs in Edmonton, Alberta.
A homeowner fills in the form; the request goes to Max Hemmerich, who passes it to
Edmonton heating contractors that quote that work.

Not a contractor. Not a directory. One trade, one city.

## Pages

- [index.html](https://maxhemmerich.github.io/edmonton-furnace-quotes/) — the homeowner side: the request form, what happens next, who receives it.
- [contractors.html](https://maxhemmerich.github.io/edmonton-furnace-quotes/contractors.html) — the contractor side: what a lead contains, the qualification rule, pricing.
- [service-areas.html](https://maxhemmerich.github.io/edmonton-furnace-quotes/service-areas.html) — the postal codes the request service covers.
- [no-heat.html](https://maxhemmerich.github.io/edmonton-furnace-quotes/no-heat.html) — a furnace that is not heating.
- [furnace-replacement.html](https://maxhemmerich.github.io/edmonton-furnace-quotes/furnace-replacement.html) — a furnace being replaced.
- [furnace-repair.html](https://maxhemmerich.github.io/edmonton-furnace-quotes/furnace-repair.html) — a furnace that still heats but is misbehaving.
- [furnace-tune-up.html](https://maxhemmerich.github.io/edmonton-furnace-quotes/furnace-tune-up.html) — an annual tune-up visit.
- [repair-or-replace.html](https://maxhemmerich.github.io/edmonton-furnace-quotes/repair-or-replace.html) — the repair-or-replace decision.
- [alberta-furnace-rebates.html](https://maxhemmerich.github.io/edmonton-furnace-quotes/alberta-furnace-rebates.html) — Alberta and federal rebates and grants, each printed with its government source.
- [furnace-permit-edmonton.html](https://maxhemmerich.github.io/edmonton-furnace-quotes/furnace-permit-edmonton.html) — whether replacing a furnace in Edmonton needs a permit, from the City of Edmonton's pages.
- [furnace-quote-checklist.html](https://maxhemmerich.github.io/edmonton-furnace-quotes/furnace-quote-checklist.html) — what a written furnace quote should contain.
- [assets/edmonton-furnace-lead-sheet.pdf](https://maxhemmerich.github.io/edmonton-furnace-quotes/assets/edmonton-furnace-lead-sheet.pdf) — the one-page lead sheet, download from the contractor page.
- [downloads/furnace-quote-checklist.pdf](https://maxhemmerich.github.io/edmonton-furnace-quotes/downloads/furnace-quote-checklist.pdf) — the one-page quote checklist as a PDF.

## How a request is captured

There is no server behind this site. The form validates the input in the browser, composes the
request, and hands it to the visitor's email app (`mailto:`), with a copy-to-clipboard fallback.
Nothing is sent until the visitor acts, and no data is posted to any third party.

`assets/requests.json` holds the counted number of requests received, shown on the contractor page.
It is a count from this form — never an estimate.

## Rebuild the PDF

```
py -3.10 tools/make_lead_sheet.py
```

Requires `reportlab`.
