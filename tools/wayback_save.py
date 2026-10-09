#!/usr/bin/env python
# tools/wayback_save.py - place (and verify) a permanent third-party reference for every public
# page: a Wayback Machine snapshot. No account, no cost, no key.
#
#   py -3.10 tools/wayback_save.py --dry-run     # print the URL list only
#   py -3.10 tools/wayback_save.py               # Save Page Now each page, then verify it
#   py -3.10 tools/wayback_save.py --check-only  # verify only (no new saves)
#   py -3.10 tools/wayback_save.py --delay 10    # spacing between saves (default 8s)
#
# Why this exists next to tools/indexnow.py: IndexNow *tells* an engine a page exists; a Wayback
# snapshot *is* a third-party citation of it, reachable without the host root. This site lives on a
# subpath of maxhemmerich.github.io and nothing can be placed at the host root (that needs a
# maxhemmerich.github.io user-site repo, Max's call), so a crawler that reads no robots.txt has to
# guess the subpath. A reference that names the page - and does not depend on the host root - is the
# account-free discovery move this lane can still pull.
#
# The URL list is read straight out of the built sitemap.xml, so it cannot fall out of step with the
# site: add a page, rebuild sitemap.xml, and it is referenced here too. The "<loc>" split matches the
# page <loc> only, never the image-sitemap "<image:loc>".
#
# Two honest rules, both measured:
#   - A save only counts when the provider redirects to a real snapshot URL
#     (web.archive.org/web/<14-digit timestamp>/<page>); a 200 that is a rate-limit or queue page is
#     NOT a save, so the save is retried once.
#   - A page only counts as referenced when the availability API returns
#     {"available": true, "status": "200"} for it. That API lags a fresh save by seconds to a minute,
#     so verification is retried with a wait (the final pass), never read once.
import json, os, sys, time, urllib.parse, urllib.request, urllib.error

TOOLS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(TOOLS)          # the site root GitHub Pages serves
SAVE = "https://web.archive.org/save/"
AVAIL = "https://archive.org/wayback/available?url="
UA = "edmonton-furnace-quotes-discovery/1.0 (+https://maxhemmerich.github.io/edmonton-furnace-quotes/)"

sm = open(os.path.join(PROJECT, "sitemap.xml"), encoding="utf-8").read()
URLS = [u.split("<", 1)[0].strip() for u in sm.split("<loc>")[1:]]
URLS = [u for u in URLS if u.startswith("http")]
if not URLS:
    sys.exit("no URLs found in sitemap.xml")

delay = 6
if "--delay" in sys.argv:
    delay = float(sys.argv[sys.argv.index("--delay") + 1])

print("pages (%d): %s" % (len(URLS), ", ".join(URLS)))

if "--dry-run" in sys.argv:
    sys.exit(0)

check_only = "--check-only" in sys.argv


def http_get(url, timeout=180):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=timeout)


def save_one(url):
    """Save Page Now once. Return the snapshot URL if the redirect lands on a real snapshot."""
    try:
        r = http_get(SAVE + url)
        final, code = r.geturl(), r.status
        r.read(1024)
        r.close()
    except urllib.error.HTTPError as e:
        return None, "HTTP %s" % e.code
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, e)
    # A real snapshot redirect looks like /web/20261009085645/https://...
    marker = "/web/"
    parts = final.split(marker, 1)
    if code == 200 and len(parts) == 2 and parts[1][:14].isdigit():
        return final, "saved"
    return None, "no snapshot redirect (final %s)" % final


def verify_one(url, attempts=5, wait=15):
    """Ask the availability API, retrying: a fresh save is not indexed there instantly.
    Return (ok, detail)."""
    last = "no snapshot"
    for a in range(attempts):
        try:
            r = http_get(AVAIL + urllib.parse.quote(url, safe=""), timeout=60)
            data = json.loads(r.read().decode("utf-8", "replace"))
            r.close()
            closest = (data.get("archived_snapshots") or {}).get("closest") or {}
            if closest.get("available") is True and closest.get("status") == "200":
                return True, closest.get("timestamp")
            last = closest.get("timestamp") or "no snapshot"
        except Exception as e:
            last = "%s: %s" % (type(e).__name__, e)
        if a < attempts - 1:
            time.sleep(wait)
    return False, last


# ---- place the references (unless --check-only) ----
save_failures = []
if not check_only:
    for i, url in enumerate(URLS):
        snap, note = None, None
        for attempt in (1, 2):              # a 200 that is a queue page is not a save: retry once
            snap, note = save_one(url)
            if snap:
                break
            print("SAVE   retry(%d) %s -> %s" % (attempt, url, note))
            time.sleep(delay)
        if snap:
            print("SAVE   ok    %s" % url)
            print("              -> %s" % snap)
        else:
            print("SAVE   FAIL  %s -> %s" % (url, note))
            save_failures.append(url)
        if i < len(URLS) - 1:
            time.sleep(delay)

# ---- verify every page (with retries); this is what the task asks to confirm ----
print("-" * 72)
failures = list(save_failures)
for url in URLS:
    ok, detail = verify_one(url)
    print("VERIFY %s %s  (timestamp %s)" % ("ok  " if ok else "FAIL", url, detail))
    if not ok and url not in failures:
        failures.append(url)

print("-" * 72)
if failures:
    print("INCOMPLETE - %d/%d pages referenced:" % (len(URLS) - len(failures), len(URLS)))
    for u in failures:
        print("  missing: %s" % u)
    sys.exit(1)
print("OK         : all %d pages have a Wayback snapshot (available, status 200)." % len(URLS))
