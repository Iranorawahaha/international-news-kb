#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-11 第四步必做校验（archive 结构版）：官方源字段/真实日期/前端渲染/模板摘要"""
import json, re, subprocess
from collections import Counter

def has_zh(s):
    return any('\u4e00' <= c <= '\u9fff' for c in (s or ''))

print("=" * 70)
print("【校验1】官方源字段完整性 (news-data.json 中 is_official=True)")
with open('data/news-data.json') as f:
    data = json.load(f)
archive = data.get('archive', {})
items = [it for day in archive.values() for it in day]
print(f"  总条数: {len(items)}")
official = [it for it in items if it.get('is_official')]
no_zh = [it for it in official if not has_zh(it.get('title_zh'))]
tpl = [it for it in official if '[官方信源]' in (it.get('summary') or '')]
print(f"  官方源总数: {len(official)}")
print(f"  缺中文标题: {len(no_zh)}")
for it in no_zh[:5]:
    print(f"    - {it.get('title','')[:60]}")
print(f"  模板摘要数: {len(tpl)}")
for it in tpl[:5]:
    print(f"    - {it.get('title','')[:60]}")

print()
print("【校验2】官方源真实日期归档（date 与归档组一致性）")
mismatch = 0
for day, day_items in archive.items():
    for it in day_items:
        if it.get('is_official') and it.get('date') != day:
            mismatch += 1
            if mismatch <= 3:
                print(f"  ⚠️ {day} 组含 {it.get('date')} 官方条目: {it.get('title_zh','')[:30]}")
print(f"  官方源日期-归档不匹配: {mismatch}")
# 官方源按日期分布
od = Counter(it.get('date') for it in official)
print("  官方源 date 分布:", dict(sorted(od.items(), reverse=True)[:6]))

print()
print("【校验3】前端渲染数据")
html = open('international-news.html').read()
# 尝试多种嵌入模式
m = re.search(r'NEWS_DATA\s*=\s*(\{.*?\})\s*;', html, re.S) or \
    re.search(r'NEWS_DATA\s*=\s*(\[.*?\])\s*;', html, re.S)
if not m:
    m = re.search(r'__NEWS_DATA__\s*=\s*(\{.*?\})\s*;', html, re.S)
if m:
    try:
        nd = json.loads(m.group(1))
        # 可能是 archive 结构或列表
        if isinstance(nd, dict) and 'archive' in nd:
            nd_items = [it for day in nd['archive'].values() for it in day]
        else:
            nd_items = nd
        print(f"  嵌入 JSON 解析 OK: {len(nd_items)} 条")
        tpl_all = [it for it in nd_items if '[官方信源]' in (it.get('summary') or '')]
        print(f"  模板摘要: {len(tpl_all)}")
        zh_rate = sum(1 for it in nd_items if has_zh(it.get('title_zh') or it.get('title',''))) / max(1, len(nd_items))
        print(f"  中文标题率: {zh_rate*100:.1f}%")
        nav_words = ['Executive Orders', '365 Days of Wins', 'Briefings', 'State Department Home']
        nav = [it for it in nd_items if any(w in (it.get('title_zh','') + it.get('title','')) for w in nav_words)]
        print(f"  导航残留: {len(nav)}")
    except Exception as e:
        print(f"  JSON 解析失败: {e}")
else:
    # 检查 HTML 是否含数据（可能模板占位符替换）
    import re as _re
    m2 = _re.search(r'var newsData\s*=\s*(\[.*?\]);', html, _re.S) or _re.search(r'const newsData\s*=\s*(\[.*?\]);', html, _re.S)
    if m2:
        try:
            nd = json.loads(m2.group(1))
            print(f"  嵌入 JSON (newsData) 解析 OK: {len(nd)} 条")
        except Exception as e:
            print(f"  newsData 解析失败: {e}")
    else:
        print("  未找到 NEWS_DATA 嵌入模式，HTML 大小:", len(html), "字节")
        # 检查是否有中文标题示例
        zh_count = len(_re.findall(r'[\u4e00-\u9fff]{6,}', html))
        print(f"  HTML 中文字符块数量: {zh_count}")

print()
print("【校验4】JS 语法检查")
r = subprocess.run(['/Users/xiaoxiao/.workbuddy/binaries/python/versions/3.13.12/bin/python3',
                    'scripts/check_js_syntax.py', 'international-news.html'],
                   capture_output=True, text=True)
print("  ", r.stdout.strip()[-200:] if r.stdout.strip() else "（无输出）")

print()
print("【校验5】六大栏目分布与今日概况")
cols = Counter(it.get('column', '未分类') for it in items)
for c, n in sorted(cols.items(), key=lambda x: -x[1]):
    print(f"    {c}: {n}")
dates = Counter(it.get('date') for it in items)
print("  日期组:", dict(sorted(dates.items(), reverse=True)[:8]))
print(f"  今日 (8-11) 条数: {data.get('todayCount', '?')}")
print(f"  高分条目 (≥88): {sum(1 for it in items if it.get('priority_score',0) >= 88)}")
