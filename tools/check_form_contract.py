#!/usr/bin/env python
# tools/check_form_contract.py - the request form must never submit natively.
#
# Why this exists: a native form submission whose target is the mailto: address is what a
# browser turns into its full-page "the information you're about to submit is not secure"
# warning (measured, by hand, in Chrome - see the report), and a native POST to the page URL
# is a 405 on GitHub Pages. Either one loses the lead, silently, only in the JavaScript-off /
# script-blocked path - exactly the path nobody looks at. So the contract is checked here.
#
#   py -3.10 tools/check_form_contract.py            # check the tree
#   py -3.10 tools/check_form_contract.py --root DIR # check a copy (used to prove it can fail)
#
# It asserts, in index.html and assets/app.js:
#   * #qform carries no action / method / enctype attribute (no native submit target)
#   * there is no type="submit" control anywhere in the form
#   * the submit control is <button ... type="button" ... id="prepare">
#   * a <noscript> block carries a plain mailto: link to the receiving address (the safe,
#     JavaScript-off path - a link is never an insecure form submission)
#   * assets/app.js prevents the form's own submit and Enter key, and drives #prepare
#   * the result panel offers #mailto, #copy and #save
#   * assets/styles.css hides .no-js #prepare (no dead control for a JavaScript-off visitor)
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "--root" in sys.argv:
    ROOT = sys.argv[sys.argv.index("--root") + 1]

html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
js = open(os.path.join(ROOT, "assets", "app.js"), encoding="utf-8").read()
css = open(os.path.join(ROOT, "assets", "styles.css"), encoding="utf-8").read()

# the form element and the region up to its </form>
fm = re.search(r"<form\b[^>]*>", html)
form_tag = fm.group(0) if fm else ""
form_body = html[fm.start():html.find("</form>", fm.start())] if fm else ""

fails, passes = [], []
def check(ok, label):
    (passes if ok else fails).append(label)

check(bool(fm), "index.html has a <form>")
check('id="qform"' in form_tag, "the form carries id=qform")
check(not re.search(r"\saction\s*=", form_tag, re.I), "the form has NO action attribute")
check(not re.search(r"\smethod\s*=", form_tag, re.I), "the form has NO method attribute")
check(not re.search(r"\senctype\s*=", form_tag, re.I), "the form has NO enctype attribute")
check('type="submit"' not in form_body, "the form contains no type=submit control")
check(re.search(r'<button[^>]*\bid="prepare"[^>]*\btype="button"|<button[^>]*\btype="button"[^>]*\bid="prepare"', form_body),
      "the submit control is button[type=button] id=prepare")

ns = re.search(r"<noscript>(.*?)</noscript>", form_body, re.S)
check(bool(ns), "a <noscript> block exists inside the form")
check(bool(ns) and re.search(r'href="mailto:maxhemmerich@gmail\.com', ns.group(1)),
      "the noscript block carries a mailto link to the receiving address")

check("preventDefault" in js and '.addEventListener("submit"' in js,
      "app.js prevents the form's own submit event")
check('addEventListener("click", submitRequest)' in js and 'id="prepare"' not in js,
      "app.js drives #prepare by click, not by a native submit")
check('e.key === "Enter"' in js, "app.js stops the Enter key from submitting natively")
for ident in ("mailto", "copy", "save"):
    check(('id="%s"' % ident) in html, 'the result panel offers #%s' % ident)

check(re.search(r"\.no-js\s+#prepare\s*\{[^}]*display\s*:\s*none", css) is not None,
      "styles.css hides .no-js #prepare (no dead control without JavaScript)")

for p in passes:
    print("  ok    %s" % p)
for f in fails:
    print("  FAIL  %s" % f)
print("\n%d/%d checks passed on %s" % (len(passes), len(passes) + len(fails), ROOT))
sys.exit(1 if fails else 0)
