#!/usr/bin/env python3
"""
fetch_body_batch.py — 按日期窗口批量抓取近3天高优新闻原文（临时脚本）
复用 fetch_body.py 的抓取/提取函数，每次最多 10 篇
用法: python3 fetch_body_batch.py <batch_index 0-based> [days]
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
import fetch_body as fb

PROJ = Path('/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50')
NEWS_DATA = PROJ / 'data' / 'news-data.json'
OUTPUT = PROJ / 'data' / 'article-bodies.json'

BATCH = 10  # 每批最多 10 篇


def main():
    batch_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    days_back = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    news = json.loads(NEWS_DATA.read_text(encoding='utf-8'))
    arch = news.get('archive', {})
    now = datetime.now(fb.TZ)
    today = now.date()

    # 收集近 N 天高优文章（priority_score>=88），按日期倒序
    targets = []
    for d in sorted(arch.keys(), reverse=True):
        dd = datetime.strptime(d, '%Y-%m-%d').date()
        if (today - dd).days > days_back:
            continue
        if (today - dd).days < 0:
            continue
        for a in arch[d]:
            if (a.get('priority_score') or 0) >= 88:
                targets.append((d, a))
    targets.sort(key=lambda x: x[0], reverse=True)

    bodies = fb.load_existing()

    # 过滤已抓取
    todo = []
    for d, a in targets:
        url = fb.url_key(a.get('url', ''))
        if not url:
            continue
        b = bodies.get(url, {})
        if b.get('body') and len(b.get('body', '')) > 200:
            continue
        todo.append((d, a))
    todo.sort(key=lambda x: x[0], reverse=True)

    total = len(todo)
    batch = todo[batch_idx * BATCH:(batch_idx + 1) * BATCH]
    if not batch:
        print(f'✅ 无待抓取文章（batch {batch_idx} 为空），共 {total} 篇待抓')
        return

    print(f'📥 fetch_body_batch · {now.strftime("%Y-%m-%d %H:%M")}')
    print(f'   近{days_back}天高优待抓: {total} 篇 | 本批: {len(batch)} 篇 (第 {batch_idx + 1} 批)\n')

    new_count = 0
    fail_count = 0
    for i, (d, a) in enumerate(batch, 1):
        title = a.get('title_zh') or a.get('title', '') or ''
        url = a.get('url', '')
        key = fb.url_key(url)
        print(f'  [{batch_idx * BATCH + i}/{total}] {d} | {title[:50]}...')
        try:
            body = fb.fetch_page(url)
            text = fb.extract_body(body, url)
            if len(text) < 100:
                raise Exception(f'正文太短 ({len(text)} chars)')
            bodies[key] = {
                'url': url,
                'title': title,
                'body': text,
                'fetched_at': now.isoformat(),
            }
            new_count += 1
            print(f'    ✅ {len(text)} chars')
        except Exception as e:
            fail_count += 1
            print(f'    ❌ {e}')

    # 保留 7 天内的缓存（同原脚本），其余清理
    cutoff = (now - timedelta(days=7)).isoformat()
    bodies = {k: v for k, v in bodies.items() if v.get('fetched_at', '') >= cutoff}

    OUTPUT.write_text(json.dumps(bodies, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\n📊 本批: 新增 {new_count} · 失败 {fail_count} | 总缓存: {len(bodies)} 条')


if __name__ == '__main__':
    main()
