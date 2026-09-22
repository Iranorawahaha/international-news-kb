# -*- coding: utf-8 -*-
"""0922 池合并：解析 /tmp/pool0922/*.txt -> 追加 data/news-webfetch.json（含 URL 去重）"""
import json, glob, os

COL = '2026-09-22 09:30:00'
rows = []
for f in sorted(glob.glob('/tmp/pool0922/*.txt')):
    for line in open(f, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        p = [x.strip() for x in line.split(' | ')]
        if len(p) != 10:
            print('!! BAD LINE', os.path.basename(f), len(p), line[:90])
            continue
        src, cat, pri, tz, te, sz, url, date, kw, summit = p
        rows.append({
            'source': src, 'category': cat, 'column': cat, 'priority_score': int(pri),
            'title_zh': tz, 'title_en': te, 'title': tz,
            'summary_zh': sz, 'summary': sz,
            'url': url, 'date': date, 'collectedAt': COL,
            'keywords': [k.strip() for k in kw.split(',') if k.strip()],
            'is_summit_level': summit == '1',
            'collection_method': 'webfetch',
        })

print('parsed:', len(rows))
from collections import Counter
print('by source:', Counter(r['source'] for r in rows).most_common())
print('by date:', Counter(r['date'] for r in rows).most_common())

# ---- dedupe inside batch ----
seen, uniq = set(), []
for r in rows:
    if r['url'] in seen:
        print('DUP in batch:', r['url'][:110])
        continue
    seen.add(r['url'])
    uniq.append(r)
print('after in-batch dedupe:', len(uniq))

# ---- dedupe against pool + archive ----
pool = json.load(open('data/news-webfetch.json', encoding='utf-8'))
known = {x.get('url') for x in pool}
nd = json.load(open('data/news-data.json', encoding='utf-8'))
for k, v in nd.get('archive', {}).items():
    for x in v:
        known.add(x.get('url'))
print('known urls:', len(known))

final, skipped = [], 0
for r in uniq:
    if r['url'] in known:
        skipped += 1
        print('SKIP known:', r['source'], r['title_zh'][:60])
        continue
    final.append(r)
print('final new:', len(final), '| skipped:', skipped)

pool.extend(final)
json.dump(pool, open('data/news-webfetch.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('pool size now:', len(pool))
