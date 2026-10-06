# Edmonton Furnace Quotes

Quote-request intake for furnace replacement and no-heat jobs in Edmonton, Alberta.
A homeowner fills in the form; the request goes to Max Hemmerich, who passes it to
Edmonton heating contractors that quote that work.

Not a contractor. Not a directory. One trade, one city.

## Pages

- `index.html` — the homeowner side: the request form, what happens next, who receives it.
- `contractors.html` — the contractor side: what a lead contains, the qualification rule, pricing.
- `assets/edmonton-furnace-lead-sheet.pdf` — the one-page lead sheet, download from the contractor page.

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
