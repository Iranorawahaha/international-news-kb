# -*- coding: utf-8 -*-
"""0922: parse all RSS in /tmp/rss0922, output candidates with real pubDate + official URL."""
import glob, re, html, json, os
import xml.etree.ElementTree as ET

out = []
for f in sorted(glob.glob("/tmp/rss0922/*.xml")):
    name = os.path.basename(f).replace(".xml", "")
    raw = open(f, "rb").read()
    if len(raw) < 300:
        print(name, "TOO SMALL", len(raw)); continue
    if raw.lstrip()[:15].lower().startswith(b"<!doctype") or b"Just a moment" in raw:
        print(name, "BLOCKED"); continue
    try:
        root = ET.fromstring(raw)
    except Exception as e:
        print(name, "PARSE FAIL", str(e)[:80]); continue
    n = 0
    for it in root.iter("item"):
        t = it.findtext("title") or ""
        l = it.findtext("link") or ""
        d = it.findtext("pubDate") or ""
        desc = it.findtext("description") or ""
        if not l:
            continue
        l = re.sub(r"[?&](utm_source|utm_medium|utm_campaign|utm_term|utm_content|outputType|itid|wpisrc|pwapi_token|s_cid|ns_mchannel|ns_campaign|ns_source|at_medium|at_campaign)=[^&]*", "", l).rstrip("?&")
        desc = html.unescape(re.sub(r"<[^>]+>", " ", desc))
        desc = re.sub(r"\s+", " ", desc).strip()
        out.append({"feed": name, "title": html.unescape(t).strip(), "link": l,
                    "pubDate": d, "desc": desc[:500]})
        n += 1
    print(f"{name}: {n} items")

print("\nTOTAL:", len(out))
json.dump(out, open("/tmp/rss0922/all_items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def pdate(s):
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", s or "")
    if not m:
        return ""
    mon = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07',
           'Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    mm = mon.get(m.group(2).capitalize(), '')
    if not mm:
        return ""
    return f"{m.group(3)}-{mm}-{int(m.group(1)):02d}"


WINDOW = {'2026-09-21', '2026-09-22'}
inw = []
for r in out:
    r['date'] = pdate(r['pubDate'])
    if r['date'] in WINDOW:
        inw.append(r)

print("\n=== in window (09-21/09-22):", len(inw), "===")
from collections import Counter
print(Counter(r['feed'] for r in inw))
for r in sorted(inw, key=lambda x: (x['date'], x['feed']), reverse=True):
    print(f"[{r['feed']}] {r['date']} | {r['title'][:105]} | {r['link'][:130]}")
json.dump(inw, open("/tmp/rss0922/window.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
