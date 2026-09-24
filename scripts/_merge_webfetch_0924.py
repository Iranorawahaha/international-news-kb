#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并 09-24 采集池：解析 -> 校验 -> 去重 -> 追加 news-webfetch.json"""
import json, glob, os, sys

ROOT = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50'
POOL = os.path.join(ROOT, 'data/news-webfetch.json')
ND = os.path.join(ROOT, 'data/news-data.json')
COLLECTED = '2026-09-24 09:30:00'

FIELDS = ['source','category','priority','title_zh','title_en','summary_zh','url','date','keywords','is_summit_level','repost_from']

def norm_url(u):
    u = (u or '').strip()
    for p in ('?utm_source=rss_feed','?at_medium=RSS&at_campaign=rss'):
        if u.endswith(p):
            u = u[:-len(p)]
    return u.rstrip('/')

items = []
bad = 0
for f in sorted(glob.glob('/tmp/pool0924/*.txt')):
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        line = line.rstrip('\n')
        if not line.strip():
            continue
        parts = line.split('|')
        if len(parts) != len(FIELDS):
            print(f'  ⚠️ 字段数异常 {os.path.basename(f)}:{ln} -> {len(parts)}')
            bad += 1
            continue
        d = dict(zip(FIELDS, parts))
        items.append(d)

print(f'解析 {len(items)} 条，字段异常 {bad} 条')

# 批内去重
seen = set()
uniq = []
for d in items:
    k = norm_url(d['url'])
    if k in seen:
        print(f'  🔁 批内重复跳过: {d["title_zh"][:40]}')
        continue
    seen.add(k)
    uniq.append(d)
print(f'批内去重后 {len(uniq)} 条')

# 与池 + archive 去重
pool = json.load(open(POOL, encoding='utf-8'))
if isinstance(pool, dict):
    pool_items = pool.get('items', [])
    pool_is_dict = True
else:
    pool_items = pool
    pool_is_dict = False
exist = {norm_url(i.get('url')) for i in pool_items}

nd = json.load(open(ND, encoding='utf-8'))
arch = nd.get('archive', {})
for k, v in arch.items():
    for i in v:
        exist.add(norm_url(i.get('url')))

new = []
for d in uniq:
    if norm_url(d['url']) in exist:
        print(f'  ⏭ 与池/存档重复跳过: {d["title_zh"][:40]}')
        continue
    new.append(d)
print(f'与池/存档去重后新增 {len(new)} 条')

out = []
for d in new:
    rec = {
        'title': d['title_zh'],
        'title_zh': d['title_zh'],
        'title_en': d['title_en'],
        'summary': d['summary_zh'],
        'summary_zh': d['summary_zh'],
        'source': d['source'],
        'category': d['category'],
        'priority_score': int(d['priority']),
        'is_summit_level': d['is_summit_level'] == '1',
        'keywords': [k for k in d['keywords'].split(',') if k],
        'url': norm_url(d['url']),
        'date': d['date'],
        'collectedAt': COLLECTED,
        'collection_method': 'webfetch',
    }
    if d.get('repost_from'):
        rec['repost_from'] = d['repost_from']
    out.append(rec)

if pool_is_dict:
    pool['items'] = pool_items + out
    json.dump(pool, open(POOL, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
else:
    json.dump(pool_items + out, open(POOL, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print(f'✅ 池 {len(pool_items)} -> {len(pool_items) + len(out)}')
from collections import Counter
print('来源分布:', dict(Counter(r['source'] for r in out)))
print('日期分布:', dict(Counter(r['date'] for r in out)))
print('category 分布:', dict(Counter(r['category'] for r in out)))
