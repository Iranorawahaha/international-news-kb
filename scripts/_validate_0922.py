# -*- coding: utf-8 -*-
"""0922 第四步校验：归档三零 + 官方字段 + 模板摘要 + 黑名单 + 彭博 collectedAt"""
import json, re
from collections import Counter

TODAY = '2026-09-22'
YEST = '2026-09-21'
nd = json.load(open('data/news-data.json', encoding='utf-8'))
arch = nd['archive']
dates = sorted(arch.keys())
print('archive dates:', dates)
today_key = TODAY if TODAY in arch else dates[-1]
cur = arch[today_key]
print(f'\n== 今日版面 {today_key}: {len(cur)} 条 ==')

# 1. collectedAt != today
bad_col = [x for x in cur if (x.get('collectedAt') or '')[:10] != TODAY]
print('1) collectedAt != today :', len(bad_col))
for x in bad_col[:5]:
    print('   ', x.get('source'), x.get('collectedAt'), x.get('title_zh', '')[:50])

# 2. date < yesterday
bad_date = [x for x in cur if (x.get('date') or '') < YEST]
print('2) date < 昨天 :', len(bad_date))
for x in bad_date[:5]:
    print('   ', x.get('source'), x.get('date'), x.get('title_zh', '')[:50])

# 3. URL dup with history
hist = set()
for k, v in arch.items():
    if k == today_key:
        continue
    for x in v:
        hist.add(x.get('url'))
dups = [x for x in cur if x.get('url') in hist]
print('3) 与历史版面 URL 重复 :', len(dups))
for x in dups[:5]:
    print('   ', x.get('source'), x.get('url', '')[:100])

# 4. self dup inside current
seen = {}
sd = []
for x in cur:
    u = x.get('url')
    if u in seen:
        sd.append(x)
    seen[u] = 1
print('4) 版面内自身重复 :', len(sd))

# 5. official field completeness
off = [x for x in cur if x.get('is_official')]
print(f'\n5) 官方源条目 {len(off)} 条')
nozh = [x for x in off if not (x.get('title_zh') or '').strip()]
nosum = [x for x in off if not (x.get('summary_zh') or '').strip() or len(x.get('summary_zh') or '') < 25]
print('   缺 title_zh:', len(nozh), '| 缺/过短 summary_zh:', len(nosum))
for x in nozh + nosum:
    print('   !', x.get('source'), x.get('title', '')[:60])

# 6. template summary
tpl = [x for x in cur if re.search(r'^\[官方信源\]|发布[:：]\s*$|^[^，。]{0,10}发布：', x.get('summary_zh') or '')]
print('\n6) 模板式摘要 :', len(tpl))
for x in tpl[:5]:
    print('   ', x.get('source'), (x.get('summary_zh') or '')[:80])

# 7. blacklist domains
BL = ['toutiao.com', '163.com', 'sohu.com', 'qq.com', 'hongkongdaily', 'gzylhyzx', 'laserfair',
      'cnnbc.com', 'cnnbc.cn', 'newsx.com', 'esaa.org.eg', 'xinhuanet', 'news.cn']
bl = [x for x in cur if any(b in (x.get('url') or '') for b in BL)]
print('7) 黑名单域名 :', len(bl))
for x in bl[:5]:
    print('   ', x.get('url', '')[:110])

# 8. source distribution
print('\n8) 今日版面来源分布:')
for k, v in Counter(x.get('source') for x in cur).most_common():
    print(f'   {k}: {v}')

# 9. category distribution
print('\n9) 栏目分布:')
for k, v in Counter(x.get('category') for x in cur).most_common():
    print(f'   {k}: {v}')

# 10. bloomberg collectedAt
bb = [x for x in cur if x.get('source') == '彭博社']
print(f'\n10) 彭博社 {len(bb)} 条；collectedAt 非今日:', len([x for x in bb if (x.get('collectedAt') or '')[:10] != TODAY]))
for x in bb:
    print('   ', x.get('date'), (x.get('collectedAt') or '')[:10], x.get('title_zh', '')[:60])

# 11. repost_from count
rp = [x for x in cur if x.get('repost_from')]
print('\n11) repost_from 条目:', len(rp))
for x in rp:
    print('   ', x.get('source'), '->', x.get('repost_from'), x.get('url', '')[:80])

# 12. reuters official ratio
rt = [x for x in cur if x.get('source') == '路透社']
ro = [x for x in rt if 'reuters.com' in (x.get('url') or '')]
print(f'\n12) 路透社 {len(rt)} 条，官网 URL {len(ro)} 条')

# 13. title/summary missing
mt = [x for x in cur if not (x.get('title_zh') or '').strip()]
ms = [x for x in cur if not (x.get('summary_zh') or '').strip()]
print('\n13) 缺中文标题:', len(mt), '| 缺中文摘要:', len(ms))
