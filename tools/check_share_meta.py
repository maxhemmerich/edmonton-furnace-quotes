#!/usr/bin/env python
# tools/check_share_meta.py - a committed check that the share card cannot rot (NEXT.md #18).
#
#   py -3.10 tools/check_share_meta.py             # check the tree AND fetch the live og:image
#   py -3.10 tools/check_share_meta.py --offline   # no network: check the committed og.png instead
#
# For every page the sitemap lists, it asserts:
#   1. the page has a canonical and it is that page's OWN url;
#   2. og:url is present and EQUALS that canonical;
#   3. a single, identical og:image url is used on EVERY page;
#   4. that image is the absolute SITE/assets/og.png;
#   5. og:image:width / og:image:height are declared 1200 / 630;
#   6. the image really is a 1200x630 image/png - fetched live (200 + Content-Type: image/png), or,
#      with --offline, read from the committed local PNG.
# The page list is read from sitemap.xml, so a page the site publishes cannot be skipped.
# Exits non-zero on any failure, printing every check it ran.
import os, re, struct, sys, urllib.request

TOOLS = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(TOOLS)
SITE = "https://maxhemmerich.github.io/edmonton-furnace-quotes"
OG_URL = SITE + "/assets/og.png"
OG_LOCAL = os.path.join(PROJECT, "assets", "og.png")
OFFLINE = "--offline" in sys.argv

fails = []
def check(ok, label, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", label, ("  -> " + detail) if detail else ""))
    if not ok:
        fails.append(label)

def attr(html, prop):
    m = re.search(r'<(?:meta|link)[^>]*\b' + prop + r'=["\']([^"\']+)["\']', html, re.I)
    return m.group(1).strip() if m else None

sm = open(os.path.join(PROJECT, "sitemap.xml"), encoding="utf-8").read()
LOCS = [u.split("<", 1)[0].strip() for u in sm.split("<loc>")[1:]]
LOCS = [u for u in LOCS if u.startswith("http")]
check(bool(LOCS), "sitemap lists at least one page", "%d pages" % len(LOCS))

og_images = []
for loc in LOCS:
    rel = loc[len(SITE):].lstrip("/")
    local = os.path.join(PROJECT, "index.html") if (rel == "" or rel.endswith("/")) \
        else os.path.join(PROJECT, rel.replace("/", os.sep))
    name = rel or "index.html"
    if not os.path.exists(local):
        check(False, "%s: page file exists" % name, local)
        continue
    html = open(local, encoding="utf-8").read()
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', html, re.I)
    canon = m.group(1).strip() if m else None
    ogurl = attr(html, 'property="og:url"[^>]*content')
    ogimg = attr(html, 'property="og:image"[^>]*content')
    w = attr(html, 'property="og:image:width"[^>]*content')
    h = attr(html, 'property="og:image:height"[^>]*content')
    check(canon == loc, "%s: canonical is the page's own url" % name, repr(canon))
    check(ogurl == canon, "%s: og:url equals canonical" % name, "og:url=%r canonical=%r" % (ogurl, canon))
    check(bool(canon), "%s: has a canonical" % name)
    check((w, h) == ("1200", "630"), "%s: og:image declared 1200x630" % name, "%s x %s" % (w, h))
    if ogimg:
        og_images.append((name, ogimg))

uniq = sorted(set(u for _, u in og_images))
check(len(uniq) == 1, "one single og:image url on every page", ", ".join(uniq) if uniq else "none found")
check(uniq == [OG_URL], "the og:image is %s" % OG_URL, ", ".join(uniq) if uniq else "none found")

def png_dims(data):
    if data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])

if OFFLINE:
    data = open(OG_LOCAL, "rb").read()
    check(data[:8] == b"\x89PNG\r\n\x1a\n", "committed assets/og.png is a PNG")
    check(png_dims(data) == (1200, 630), "committed assets/og.png is 1200x630", str(png_dims(data)))
    print("      (--offline: the live fetch of %s was skipped)" % OG_URL)
else:
    try:
        req = urllib.request.Request(OG_URL, headers={"User-Agent": "beta-share-meta-check"})
        with urllib.request.urlopen(req, timeout=30) as r:
            code, ctype, data = r.status, r.headers.get("Content-Type", ""), r.read()
        check(code == 200, "live og:image returns 200", "HTTP %s" % code)
        check(ctype.split(";")[0].strip().lower() == "image/png", "live og:image is image/png", ctype)
        check(png_dims(data) == (1200, 630), "live og:image is a 1200x630 PNG", str(png_dims(data)))
    except Exception as e:
        check(False, "live og:image fetch", "%s: %s" % (type(e).__name__, e))

print()
if fails:
    print("FAILED %d check(s): %s" % (len(fails), "; ".join(fails)))
    sys.exit(1)
print("ALL CHECKS PASSED (%d pages, image %s)" % (len(LOCS), OG_URL))
