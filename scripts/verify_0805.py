#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-05 第四步校验：官方源字段完整性 + 日期归档 + 前端渲染数据质量"""
import json, os, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. news-data.json 官方源校验
nd = json.load(open(os.path.join(BASE, 'data', 'news-data.json')))
items = []
for k, v in nd.items():
    if isinstance(v, list):
        items.extend(v)

official = [x for x in items if x.get('is_official')]
no_zh = [x for x in official if not x.get('title_zh')]
tpl = [x for x in official if '[官方信源]' in str(x.get('summary', ''))]
short_sum = [x for x in official if len(str(x.get('summary', ''))) < 20]
print(f"=== news-data.json 校验 ===")
print(f"总条目 {len(items)} | 官方源 {len(official)} | 缺中文 {len(no_zh)} | 模板摘要 {len(tpl)} | 摘要过短 {len(short_sum)}")
for x in (no_zh + tpl)[:8]:
    print('  ⚠️', x.get('source'), '|', str(x.get('title'))[:60])

# 2. 官方源按日期归档
from collections import Counter
dates = Counter(x.get('date','?') for x in official)
print(f"官方源日期分布: {dict(sorted(dates.items()))}")

# 3. 今日(2026-08-04/05)条目数
today = [x for x in items if x.get('date') in ('2026-08-04', '2026-08-05')]
print(f"今日(8-04/8-05)条目: {len(today)}")

# 4. HTML 中文化检查
html_path = os.path.join(BASE, 'international-news.html')
if os.path.exists(html_path):
    with open(html_path, encoding='utf-8') as f:
        h = f.read()
    tpl_hits = h.count('[官方信源]')
    zh_hits = len(re.findall(r'[\u4e00-\u9fff]', h))
    print(f"=== international-news.html ===")
    print(f"大小 {len(h)/1024:.0f}KB | 模板摘要残留 {tpl_hits} | 中文字符数 {zh_hits}")
else:
    print('⚠️ international-news.html 不存在')
