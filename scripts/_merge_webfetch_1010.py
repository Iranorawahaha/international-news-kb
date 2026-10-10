#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, glob, os, sys

TODAY = '2026-10-10'
COLLECTED = TODAY + ' 09:30:00'
POOL = 'data/news-webfetch.json'
ARCHIVE = 'data/news-data.json'

def norm(s):
    if not s: return ''
    return (s.replace('\u2018', "'").replace('\u2019', "'")
             .replace('\u201c', '"').replace('\u201d', '"')
             .replace('\u2014', '-').replace('\u2013', '-'))

# existing urls
seen = set()
nd = json.load(open(ARCHIVE, encoding='utf-8'))
for k, v in nd['archive'].items():
    for x in v:
        seen.add(norm(x.get('url', '')))
pool = json.load(open(POOL, encoding='utf-8'))
for x in pool:
    seen.add(norm(x.get('url', '')))
print('existing urls:', len(seen))

rows = []
bad = 0
for f in sorted(glob.glob('/tmp/p1010/pool_*.txt')):
    for i, line in enumerate(open(f, encoding='utf-8'), 1):
        line = line.rstrip('\n')
        if not line.strip(): continue
        parts = line.split('|')
        if len(parts) != 10:
            print('!! BAD', f, i, 'NF=', len(parts)); bad += 1; continue
        rows.append(parts)
print('parsed rows:', len(rows), 'bad:', bad)

CATS = {'AI·科技','中美博弈','地区局势','中欧与盟友','美国内政','中国外交','全球多边','其他'}
new_items = []
dup = 0
for r in rows:
    source, category, prio, tzh, ten, szh, url, date, kw, summit = r
    if category not in CATS:
        print('!! BAD CATEGORY', category, tzh[:30]); continue
    if not url.startswith('https://'):
        print('!! BAD URL', url[:60]); continue
    if date not in ('2026-10-09', '2026-10-10'):
        print('!! OUT OF WINDOW', date, tzh[:40]); continue
    u = norm(url)
    if u in seen:
        dup += 1; print('   skip dup:', tzh[:40]); continue
    seen.add(u)
    it = {
        'title': tzh,
        'title_zh': tzh,
        'title_en': ten,
        'summary': szh,
        'summary_zh': szh,
        'source': source,
        'category': category,
        'keywords': [k for k in kw.split(',') if k],
        'url': url,
        'date': date,
        'collectedAt': COLLECTED,
        'priority_score': int(prio),
        'is_summit_level': summit == '1',
    }
    new_items.append(it)

print('new items:', len(new_items), 'dups skipped:', dup)
pool.extend(new_items)
json.dump(pool, open(POOL, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('pool now:', len(pool))

from collections import Counter
print(Counter(x['source'] for x in new_items))
print(Counter(x['category'] for x in new_items))
