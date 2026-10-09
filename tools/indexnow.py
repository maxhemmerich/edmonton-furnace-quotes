#!/usr/bin/env python
# tools/indexnow.py - tell IndexNow (Bing/Yandex and the engines that share it) about this
# site's URLs. No account, no cost, no key service.
#
#   py -3.10 tools/indexnow.py --dry-run    # print the payload only, no request
#   py -3.10 tools/indexnow.py              # verify the key file is live, then POST
#   py -3.10 tools/indexnow.py --no-verify  # POST without the live key-file check
#
# IndexNow needs no account: you host a file whose NAME is the key and whose CONTENT is the key,
# then POST the URL list and point the engines at that file with `keyLocation`. This site lives on
# a subpath of maxhemmerich.github.io, so the key file must sit inside this project's own subpath
# - nothing can be placed at the host root - and `keyLocation` is how the engines find it anyway:
#
#     https://maxhemmerich.github.io/edmonton-furnace-quotes/<key>.txt
#
# The URL list is read straight out of the built sitemap.xml, so this cannot fall out of step with
# the site: add a page, rebuild sitemap.xml, and it is submitted here too.
#
# Re-run command after ANY ship that adds or edits a page:
#     py -3.10 tools/indexnow.py
# The key file never needs re-publishing; only the URL list changes.
import json, os, sys, urllib.request, urllib.error

TOOLS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(TOOLS)          # the site root GitHub Pages serves
ENDPOINT = "https://api.indexnow.org/indexnow"
HOST = "maxhemmerich.github.io"
SITE = "https://%s/edmonton-furnace-quotes" % HOST

key_path = os.path.join(PROJECT, "indexnow.key")
if not os.path.exists(key_path):
    sys.exit("indexnow.key is missing - refusing to run. The key must not be regenerated silently: "
             "a new key means a new key file at a new URL, which invalidates what engines already saw.")
KEY = open(key_path, encoding="utf-8").read().strip()
if len(KEY) < 8:
    sys.exit("indexnow.key does not hold a usable key (%r)" % KEY)

# The hosted key file, inside this project's own subpath. Written from indexnow.key so the two
# cannot drift: the file's name and its content are the same string.
key_file = os.path.join(PROJECT, "%s.txt" % KEY)
open(key_file, "w", newline="\n", encoding="utf-8").write(KEY + "\n")

# URL list: straight out of the built sitemap. "<loc>" matches the page <loc> only, never the
# image-sitemap "<image:loc>".
sm = open(os.path.join(PROJECT, "sitemap.xml"), encoding="utf-8").read()
URLS = [u.split("<", 1)[0].strip() for u in sm.split("<loc>")[1:]]
URLS = [u for u in URLS if u.startswith("http")]
if not URLS:
    sys.exit("no URLs found in sitemap.xml")

KEYLOC = "%s/%s.txt" % (SITE, KEY)
payload = {"host": HOST, "key": KEY, "keyLocation": KEYLOC, "urlList": URLS}
body = json.dumps(payload).encode("utf-8")

print("key file   : %s  (local: %s)" % (KEYLOC, os.path.relpath(key_file, PROJECT).replace("\\", "/")))
print("endpoint   : %s" % ENDPOINT)
print("urls (%d)  : %s" % (len(URLS), ", ".join(URLS)))
print("payload    : %s" % body.decode("utf-8"))

if "--dry-run" in sys.argv:
    sys.exit(0)

# Honest guard: IndexNow rejects a POST whose keyLocation is not already retrievable and holding
# the key. Verify the file is live BEFORE submitting, so a later "403" can never be mistaken for a
# channel that does not work.
if "--no-verify" not in sys.argv:
    try:
        with urllib.request.urlopen(KEYLOC, timeout=30) as r:
            served = r.read().decode("utf-8", "replace")
            if r.status != 200 or served.strip() != KEY:
                sys.exit("key file at %s did not verify (HTTP %s, body %r). Commit and push the key "
                         "file, wait for Pages to serve it, then re-run." % (KEYLOC, r.status, served[:64]))
        print("key check  : %s -> 200, serves the key" % KEYLOC)
    except SystemExit:
        raise
    except Exception as e:
        sys.exit("key file at %s is not live yet (%s: %s). Commit and push it, wait for Pages, then "
                 "re-run - or pass --no-verify to skip this check." % (KEYLOC, type(e).__name__, e))

req = urllib.request.Request(ENDPOINT, data=body, method="POST",
                             headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        code, text = r.status, r.read().decode("utf-8", "replace")
except urllib.error.HTTPError as e:
    code, text = e.code, e.read().decode("utf-8", "replace")
except Exception as e:
    print("REQUEST FAILED: %s: %s" % (type(e).__name__, e))
    sys.exit(2)
print("HTTP       : %s" % code)
print("body       : %r" % text)
if code not in (200, 202):
    sys.exit("IndexNow did not accept the submission (HTTP %s). Nothing was submitted for indexing." % code)
print("OK         : submitted %d URLs; HTTP %s is the accepted status." % (len(URLS), code))
