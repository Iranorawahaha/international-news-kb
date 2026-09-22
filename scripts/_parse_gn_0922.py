# -*- coding: utf-8 -*-
"""Parse Google News RSS for ap/wsj/ft -> title + pubDate + gn link; print window items."""
import re, html, json
import xml.etree.ElementTree as ET

MON = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07',
       'Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

def pdate(s):
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", s or "")
    if not m:
        return ""
    return f"{m.group(3)}-{MON.get(m.group(2).capitalize(),'')}-{int(m.group(1)):02d}"

allout = {}
for name in ('ap', 'wsj', 'ft'):
    try:
        root = ET.parse(f'/tmp/rss0922/gn-{name}.xml').getroot()
    except Exception as e:
        print(name, 'FAIL', e); continue
    rows = []
    for it in root.iter('item'):
        t = html.unescape((it.findtext('title') or '').strip())
        l = it.findtext('link') or ''
        d = it.findtext('pubDate') or ''
        # GN title is "Headline - Source"
        src = ''
        m = re.match(r'^(.*?)\s+-\s+([^-]+)$', t)
        if m:
            t, src = m.group(1).strip(), m.group(2).strip()
        rows.append({'title': t, 'src': src, 'link': l, 'date': pdate(d), 'pubDate': d})
    allout[name] = rows
    win = [r for r in rows if r['date'] in ('2026-09-21', '2026-09-22')]
    print(f"=== {name}: {len(rows)} total, {len(win)} in window ===")
    for r in win:
        print(f"  {r['date']} | {r['title'][:110]} | {r['src']}")
    print()

json.dump(allout, open('/tmp/rss0922/gn_all.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
