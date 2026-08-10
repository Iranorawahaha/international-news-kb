#!/usr/bin/env python3
"""
fetch_body.py — 抓取新闻原文全文（Python 端无 CORS 限制）
存入 data/article-bodies.json，供双语截图页面使用
"""

import json
import re
import sys
import urllib.request
from pathlib import Path
from datetime import datetime, timezone, timedelta

PROJ = Path('/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50')
OUTPUT = PROJ / 'data' / 'article-bodies.json'
NEWS_DATA = PROJ / 'data' / 'news-data.json'
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
TODAY = NOW.strftime('%Y-%m-%d')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8',
}


def load_existing():
    try:
        return json.loads(OUTPUT.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def fetch_page(url, timeout=15):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode('utf-8', errors='ignore')


def extract_body(html, url):
    """从 HTML 中提取正文（通用版，兼容多数新闻网）"""
    # 移除 script/style/nav/footer
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S | re.I)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.S | re.I)
    html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.S | re.I)
    html = re.sub(r'<footer[^>]*>.*?</footer>', '', html, flags=re.S | re.I)

    # 找正文容器（常见 class/id）
    body_candidates = re.findall(
        r'<article[^>]*>(.*?)</article>|<div[^>]*(?:article-body|story-body|article__body|'
        r'content-body|main-content|article-content|story-content|post-content|entry-content|'
        r'wysiwyg|RichTextBody|ArticleText)[^>]*>(.*?)</div>',
        html, re.S | re.I)

    candidates = []
    for m in body_candidates:
        candidates.extend([g for g in m if g and len(g) > 200])

    # 找 <p> 标签
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.S)
    if not candidates and paragraphs:
        # 用最长的连续段落群
        clean_paras = [re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs]
        clean_paras = [p for p in clean_paras if len(p) > 20]
        candidates = ['\n\n'.join(clean_paras)]

    # 取最长的候选
    if not candidates:
        return ''

    best = max(candidates, key=len)
    # 清理标签
    text = re.sub(r'<[^>]+>', '', best)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&#8217;', "'", text)
    text = re.sub(r'&hellip;', '...', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # 截断到 5000 字符（正文太长没用）
    if len(text) > 5000:
        text = text[:5000].rsplit(' ', 1)[0] + '...'

    return text


def url_key(url):
    """标准化 URL 做 key"""
    return (url or '').strip().rstrip('/').split('?')[0].split('#')[0]


def main():
    print(f'📥 fetch_body.py · {NOW.strftime("%Y-%m-%d %H:%M")}')
    print(f'   目标: 今天 ({TODAY}) 的高优新闻\n')

    # 加载新闻数据
    news = json.loads(NEWS_DATA.read_text(encoding='utf-8'))
    archive = news.get('archive', {})
    today_arts = archive.get(TODAY, [])

    # 只取高优（score ≥ 88）或官方源
    targets = [a for a in today_arts
               if (a.get('priority_score') or 0) >= 88 or a.get('is_official')]

    if not targets:
        # 退而求其次：取今天全部
        targets = today_arts[:10]
        print(f'  ⚠️ 今日无高优文章，取前 {len(targets)} 条')

    print(f'  目标文章: {len(targets)} 条\n')

    # 加载已有 body 缓存
    bodies = load_existing()
    new_count = 0
    skip_count = 0
    fail_count = 0

    for i, a in enumerate(targets, 1):
        title = a.get('title_zh') or a.get('title', '') or ''
        url = a.get('url', '')
        key = url_key(url)

        if not url or not key:
            skip_count += 1
            continue

        if key in bodies and bodies[key].get('body') and len(bodies[key].get('body', '')) > 200:
            skip_count += 1
            continue

        print(f'  [{i}/{len(targets)}] {title[:50]}...')
        try:
            body = fetch_page(url)
            text = extract_body(body, url)
            if len(text) < 100:
                raise Exception(f'正文太短 ({len(text)} chars)')

            bodies[key] = {
                'url': url,
                'title': title,
                'body': text,
                'fetched_at': NOW.isoformat(),
            }
            new_count += 1
            print(f'    ✅ {len(text)} chars')
        except Exception as e:
            fail_count += 1
            print(f'    ❌ {e}')

    # 清理 7 天前的旧缓存
    cutoff = (NOW - timedelta(days=7)).isoformat()
    bodies = {k: v for k, v in bodies.items() if v.get('fetched_at', '') >= cutoff}

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(bodies, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'\n📊 统计: 新增 {new_count} · 跳过 {skip_count} · 失败 {fail_count}')
    print(f'   总缓存: {len(bodies)} 条')
    print(f'   💾 {OUTPUT}')


if __name__ == '__main__':
    main()
