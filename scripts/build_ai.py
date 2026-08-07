#!/usr/bin/env python3
"""
build_ai.py — 从 ai-news.json + ai_template.html 渲染最终 HTML
"""
import json, os, re
from datetime import datetime, timezone, timedelta

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(PROJ, 'scripts', 'ai_template.html')
DATA_FILE = os.path.join(PROJ, 'data', 'ai-news.json')
OUTPUT = os.path.join(PROJ, 'ai-news.html')
TZ = timezone(timedelta(hours=8))

KEY_COMPANIES = [
    'NVIDIA', 'AMD', 'Intel', 'Apple', 'Amazon', 'Microsoft', 'Google', 'Meta',
    'OpenAI', 'Anthropic', 'xAI',
    'DeepSeek', '华为', '字节跳动', '阿里巴巴', '腾讯',
]

def main():
    print('🏗️ build_ai.py')

    # Load data
    with open(DATA_FILE, encoding='utf-8') as f:
        data = json.load(f)

    with open(TEMPLATE, encoding='utf-8') as f:
        html = f.read()

    # Stats
    total = data['stats']['totalArticles']
    high = data['stats']['highCount']
    dates = data['dates']
    today = data.get('today', dates[0] if dates else '')
    today_count = data.get('todayCount', len(data['archive'].get(today, [])) if today else 0)
    source_count = data['stats']['sourceCount']

    # Company chips HTML
    chips = []
    for c in KEY_COMPANIES:
        cnt = sum(1 for v in data['archive'].values() for a in v if c in (a.get('company_tags', []) or []))
        chips.append(f'<div class="cat-chip" data-company="{c}"><span class="cat-chip-name">{c}</span><span class="cat-chip-cnt">{cnt}</span></div>')
    company_html = '\n        '.join(chips)

    # Company options
    opts = '\n          '.join(f'<option value="{c}">{c}</option>' for c in KEY_COMPANIES)

    now = datetime.now(TZ)
    now_str = now.strftime('%Y-%m-%d %H:%M')
    now_full = now.strftime('%Y-%m-%d %H:%M:%S')

    # Replace placeholders
    html = html.replace('__NEWS_DATA__', json.dumps(data, ensure_ascii=False))
    html = html.replace('__HIGH_COUNT__', str(high))
    html = html.replace('__TODAY_COUNT__', str(today_count))
    html = html.replace('__DATE_COUNT__', str(len(dates)))
    html = html.replace('__SOURCE_COUNT__', str(source_count))
    html = html.replace('__COMPANY_COUNT__', str(len(KEY_COMPANIES)))
    html = html.replace('__COMPANY_CHIPS__', company_html)
    html = html.replace('__COMPANY_OPTIONS__', opts)
    html = html.replace('__NOW_STR__', now_str)
    html = html.replace('__NOW_FULL__', now_full)

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'✅ {OUTPUT}')
    print(f'   {total} 条 | {len(dates)} 天 | 🔴{high}')


if __name__ == '__main__':
    main()
