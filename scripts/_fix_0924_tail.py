#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09-24 收尾修复：
1) 删除今日版面中与 09-22 联大演讲重复的白宫条目（URL 精确匹配）
2) 按 URL 补回被全量 update 抹掉的 repost_from 字段
"""
import json

ROOT = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50'
ND = f'{ROOT}/data/news-data.json'
TODAY = '2026-09-24'

DROP_URL = 'https://www.whitehouse.gov/releases/2026/09/president-trump-delivers-powerful-america-first-message-to-the-united-nations/'

REPOST = {
    'https://www.yahoo.com/news/politics/articles/us-diplomats-told-term-super-205927068.html': 'Yahoo News（美联社稿）',
    'https://www.tradingview.com/news/DJN_DN20260923008606:0/': 'TradingView（道琼斯电头）',
    'https://www.tradingview.com/news/DJN_DN20260923008569:0/': 'TradingView（道琼斯电头）',
}

nd = json.load(open(ND, encoding='utf-8'))
t = nd['archive'][TODAY]

# 1) 删除重复白宫条目
before = len(t)
kept = [i for i in t if i.get('url') != DROP_URL]
removed = before - len(kept)
nd['archive'][TODAY] = kept
print(f'删除重复白宫条目 {removed} 条 → 今日版面 {len(kept)} 条')

# 2) 补 repost_from
fixed = 0
for i in kept:
    u = i.get('url')
    if u in REPOST and not i.get('repost_from'):
        i['repost_from'] = REPOST[u]
        fixed += 1
        print(f'  ✅ 补 repost_from: {i.get("source")} | {i.get("title_zh")[:40]}')
print(f'补 repost_from {fixed} 条')

# 3) 同步 news-webfetch 池中的 repost_from（防下次 update 再丢）
WP = f'{ROOT}/data/news-webfetch.json'
wp = json.load(open(WP, encoding='utf-8'))
items = wp if isinstance(wp, list) else wp.get('items', [])
pf = 0
for i in items:
    u = i.get('url')
    if u in REPOST and not i.get('repost_from'):
        i['repost_from'] = REPOST[u]
        pf += 1
print(f'池中补 repost_from {pf} 条')

json.dump(nd, open(ND, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
json.dump(wp, open(WP, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('✅ 已写回 news-data.json / news-webfetch.json')
