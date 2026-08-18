#!/usr/bin/env python3
"""
build_ai.py — 从 ai-news.json + ai_template.html 渲染最终 HTML
"""
import json, os, re
from datetime import datetime, timezone, timedelta
from html import escape

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

# AI 看板 3 分类（industry/ai-models/tip 翻译为中文）
AI_CAT_ORDER = ["industry", "ai-models", "tip"]
AI_CAT_CN = {"industry": "产业", "ai-models": "模型", "tip": "技巧"}

# company → category 映射（fetch_ai.py 不生成 category 字段，build 时按 company 推断）
# 行业（产业）：硬件/平台/云厂商 → industry
# 模型：大模型/AI 公司 → ai-models
# 技巧：默认（教程/小道/杂项） → tip
COMPANY_TO_CAT = {
    "NVIDIA": "industry", "AMD": "industry", "Intel": "industry", "Apple": "industry",
    "Amazon": "industry", "Microsoft": "industry", "Google": "industry", "Meta": "industry",
    "OpenAI": "ai-models", "Anthropic": "ai-models", "xAI": "ai-models",
    "DeepSeek": "ai-models", "华为": "ai-models", "字节跳动": "ai-models",
    "阿里巴巴": "ai-models", "腾讯": "ai-models",
}
# 关键词 fallback
KEYWORD_TO_CAT = {
    "industry": ["芯片", "GPU", "硬件", "收购", "并购", "上市", "IPO", "融资", "监管", "制裁", "出口管制"],
    "ai-models": ["GPT", "Claude", "Gemini", "文心", "通义", "百川", "大模型", "LLM", "参数", "万亿参数", "昇腾", "鸿蒙"],
}


def infer_category(article):
    """从 company_tags + 关键词推断 category（fetch_ai.py 未填字段的兜底）"""
    cats = list(article.get("company_tags") or [])
    for c in cats:
        if c in COMPANY_TO_CAT:
            return COMPANY_TO_CAT[c]
    text = (article.get("title", "") + " " + article.get("summary", "")).lower()
    for cat, kws in KEYWORD_TO_CAT.items():
        for kw in kws:
            if kw.lower() in text:
                return cat
    return "tip"


def build_pivot(dates, today, archive):
    """V5 透视表：日期在左、分类在上、中间仅数字（V5 · 与国内/AI 通用模板一致）"""
    # 统计：日期 × 分类（自动推断 category 字段）
    pivot = {d: {c: 0 for c in AI_CAT_ORDER} for d in dates}
    for d in dates:
        for a in archive.get(d, []):
            c = a.get("category") or infer_category(a)
            if c in pivot[d]:
                pivot[d][c] += 1

    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    thead_cells = ['<th class="pivot-th first">日期</th>']
    for c in AI_CAT_ORDER:
        cn = AI_CAT_CN.get(c, c)
        thead_cells.append(f'<th class="pivot-th" title="{escape(cn)}">{escape(cn)}</th>')
    thead_cells.append('<th class="pivot-th total">合计</th>')

    pivot_rows = []
    for d in sorted(dates, reverse=True):
        is_today = (d == today)
        total_row = sum(pivot[d].values())
        try:
            wd = weekday_cn[datetime.strptime(d, "%Y-%m-%d").weekday()]
        except Exception:
            wd = ""
        date_label = d[5:]
        today_dot = '<span class="today-dot"></span>' if is_today else ''
        cells_html = []
        for c in AI_CAT_ORDER:
            cnt = pivot[d].get(c, 0)
            cn = AI_CAT_CN.get(c, c)
            if cnt:
                cells_html.append(
                    f'<td class="pivot-td">'
                    f'<span class="pivot-cell" '
                    f'data-date="{escape(d)}" data-cat="{escape(c)}" '
                    f'title="点击查看 {d} · {cn}（{cnt} 条）">{cnt}</span>'
                    f'</td>'
                )
            else:
                cells_html.append(f'<td class="pivot-td zero">–</td>')
        row_cls = "pivot-row today" if is_today else "pivot-row"
        pivot_rows.append(
            f'<tr class="{row_cls}" data-date="{escape(d)}" '
            f'title="点击查看 {d} 全部新闻（{total_row} 条）">'
            f'<td class="pivot-td date"><b>{date_label}</b><span class="weekday">{wd}</span>{today_dot}</td>'
            f'{"".join(cells_html)}'
            f'<td class="pivot-td total"><span class="pivot-total" data-date="{escape(d)}" '
            f'title="点击查看 {d} 全部新闻（{total_row} 条）">{total_row}</span></td>'
            f'</tr>'
        )
    return f'''<div class="pivot-wrapper">
        <div class="pivot-title">📅 AI · 各日分类分布</div>
        <div class="pivot-subtitle">点击数字跳转当日该类新闻 · 点击合计跳转当日全部</div>
        <table class="pivot-table">
            <thead><tr>{"".join(thead_cells)}</tr></thead>
            <tbody>{"".join(pivot_rows)}</tbody>
        </table>
    </div>'''


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
    archive = data.get('archive', {})

    # Company chips HTML
    chips = []
    for c in KEY_COMPANIES:
        cnt = sum(1 for v in archive.values() for a in v if c in (a.get('company_tags', []) or []))
        chips.append(f'<div class="cat-chip" data-company="{escape(c)}"><span class="cat-chip-name">{escape(c)}</span><span class="cat-chip-cnt">{cnt}</span></div>')
    company_html = '\n        '.join(chips)

    # Company options
    opts = '\n          '.join(f'<option value="{escape(c)}">{escape(c)}</option>' for c in KEY_COMPANIES)

    now = datetime.now(TZ)
    now_str = now.strftime('%Y-%m-%d %H:%M')
    now_full = now.strftime('%Y-%m-%d %H:%M:%S')

    # V5 透视表（日期在左、分类在上、中间仅数字）
    stats_top = build_pivot(dates, today, archive)

    # Replace placeholders
    html = html.replace('__NEWS_DATA__', json.dumps(data, ensure_ascii=False))
    html = html.replace('__STATS_TOP__', stats_top)
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
