#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse Reuters sitemap shards (0922) -> candidates with (loc, lastmod, title, url_date)."""
import re, glob, json, sys

rows = []
for fn in sorted(glob.glob('/tmp/rsm0922/shard-*.xml')):
    xml = open(fn, encoding='utf-8', errors='ignore').read()
    for m in re.finditer(r'<url>(.*?)</url>', xml, re.S):
        blk = m.group(1)
        loc = re.search(r'<loc>(.*?)</loc>', blk)
        lm = re.search(r'<lastmod>(.*?)</lastmod>', blk)
        ti = re.search(r'<news:title>(.*?)</news:title>', blk, re.S)
        if not loc:
            continue
        url = loc.group(1).strip()
        # unescape common entities
        url = url.replace('&amp;', '&')
        title = ti.group(1).strip() if ti else ''
        title = (title.replace('&amp;', '&').replace('&quot;', '"')
                      .replace('&#039;', "'").replace('&apos;', "'")
                      .replace('&lt;', '<').replace('&gt;', '>'))
        # url date
        d = re.search(r'/(\d{4})-(\d{2})-(\d{2})/?$', url)
        udate = f'{d.group(1)}-{d.group(2)}-{d.group(3)}' if d else ''
        rows.append({'url': url, 'lastmod': lm.group(1) if lm else '', 'title': title, 'date': udate})

# dedupe by url
seen = set(); out = []
for r in rows:
    if r['url'] in seen:
        continue
    seen.add(r['url']); out.append(r)

print('total parsed:', len(out))
from collections import Counter
print('url-date distribution:', Counter(r['date'] for r in out).most_common(12))

json.dump(out, open('/tmp/rsm0922/parsed.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# relevant keywords
KW = ['china', 'chinese', 'beijing', 'xi ', 'xi-', 'trump', 'tariff', 'sanction', 'export',
      'chip', 'semiconductor', 'nvidia', 'huawei', 'taiwan', 'artificial-intelligence',
      'ai-', 'trade', 'huawei', 'rare-earth', 'rare earth', 'byd', 'alibaba', 'tencent',
      'tiktok', 'foxconn', 'tsmc', 'apple', 'hong-kong', 'yuan', 'yuan-', 'pentagon',
      'missile', 'military', 'russia', 'ukraine', 'iran', 'israel', 'gaza', 'nato',
      'fed-', 'federal-reserve', 'inflation', 'oil', 'opec', 'european-union', 'eu-',
      'japan', 'korea', 'india', 'saudi', 'venezuela', 'north-korea', 'climate',
      'cyber', 'hack', 'election', 'congress', 'senate', 'white-house', 'state-department',
      'kissinger', 'greenland', 'canada', 'mexico', 'brazil', 'argentina', 'africa']
kwre = re.compile('|'.join(re.escape(k) for k in KW), re.I)
rel = [r for r in out if kwre.search(r['url']) or kwre.search(r['title'])]
# also keep recent (lastmod within 2 days)
rel.sort(key=lambda r: (r['date'], r['lastmod']), reverse=True)
print('\nrelevant:', len(rel))
for r in rel[:120]:
    print(f"{r['date']} | {r['lastmod'][:10]} | {r['title'][:110]} | {r['url'][:150]}")
json.dump(rel, open('/tmp/rsm0922/relevant.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
