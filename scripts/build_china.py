#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_china.py — 国内重大新闻看板 单文件 HTML 构建器 V4（Ira 信息看板体系）

视觉规范（V2.11 用户偏好）：
- 浅色底 + 红色主色调政务风（与国际/AI 统一表格化 UI，各版主题色不变）
- 左侧栏目侧边栏（sticky 悬浮）+ 右侧表格主体
- 上部日期选择 + 搜索框 + 来源/分类/重要性筛选
- 表格表头：# / 日期 / 标题 / 摘要 / 来源 / 分类 / 重要性 / 关键词 / 原文
- 顶部保留日期×分类统计表（国内特色）

读取 data/china-news.json，生成 china-news.html（单文件，纯内联 CSS/JS，无外部资源）。
"""
import json
import os
import re
import sys
import subprocess as sp
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "china-news.json")
TEMPLATE_FILE = os.path.join(BASE_DIR, "scripts", "_table_ui_template.html")
OUT_HTML = os.path.join(BASE_DIR, "china-news.html")

# 国内主题色（红色政务风）
THEME = {
    "primary": "#c41230",
    "primary_2": "#991b1b",
    "primary_light": "#ef4444",
    "primary_bg": "#fef2f2",
    "primary_bg_2": "#fecaca",
    "grad_1": "#7f1d1d",
    "grad_2": "#991b1b",
    "grad_3": "#c41230",
    "shadow_primary": "0 4px 20px rgba(196,18,48,0.15)",
    "row_hover": "rgba(239,68,68,0.10)",
}


def esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


def build():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    archive = data.get("archive", {})
    dates = data.get("dates", [])
    stats = data.get("stats", {})
    today = data.get("today", NOW.strftime("%Y-%m-%d"))
    today_count = data.get("todayCount", 0)
    total_count = stats.get("totalArticles", 0)
    date_count = stats.get("dateCount", len(dates))

    # 7 类分类体系
    cat_order = ["元首动态", "高层动态", "重要会议", "人事任免", "部委动态", "政策发布", "经贸动向"]
    cat_icon = {"元首动态": "👑", "高层动态": "🧭", "重要会议": "🏛",
                "人事任免": "📋", "部委动态": "🏢", "政策发布": "📜", "经贸动向": "💹"}

    # 数据规范化：每条 article 补 keywords（默认空数组）；计算高优先级条数
    high_count = 0
    for d in dates:
        for it in archive.get(d, []):
            it.setdefault("keywords", [])
            it.setdefault("title_en", "")
            it.setdefault("summary_zh", it.get("summary", ""))
            it.setdefault("title_zh", it.get("title", ""))
            if (it.get("priority_score") or 0) >= 88:
                high_count += 1
            # 按 V2.11: collectedAt 已是抓取时间字段；date 是真实发布日

    # 统计表数据：日期 × 分类
    pivot = {}
    for d in dates:
        pivot[d] = {c: 0 for c in cat_order}
        for it in archive.get(d, []):
            c = it.get("category", "")
            if c in pivot[d]:
                pivot[d][c] += 1

    # 构建顶部日期×分类统计表 HTML（V4 简洁版 · 0 值隐藏 + 可点击跳转）
    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    # 分类短名（更紧凑的展示）
    cat_short = {"元首动态": "元首", "高层动态": "高层", "重要会议": "会议",
                 "人事任免": "人事", "部委动态": "部委", "政策发布": "政策", "经贸动向": "经贸"}
    pivot_rows = []
    for d in sorted(dates, reverse=True):
        is_today = (d == today)
        cells_html = []
        for c in cat_order:
            cnt = pivot[d].get(c, 0)
            if not cnt:
                continue  # 0 值不展示，简化视觉
            icon = cat_icon.get(c, "📌")
            short = cat_short.get(c, c)
            cells_html.append(
                f'<span class="pivot-cell" '
                f'data-date="{esc(d)}" data-cat="{esc(c)}" '
                f'title="点击查看 {d} · {esc(c)}（{cnt} 条）">'
                f'<span class="ic">{icon}</span><span class="nm">{esc(short)}</span><b>{cnt}</b>'
                f'</span>'
            )
        total_row = sum(pivot[d].values())
        try:
            from datetime import datetime as _dt
            wd = weekday_cn[_dt.strptime(d, "%Y-%m-%d").weekday()]
        except Exception:
            wd = ""
        today_dot = '<span class="today-dot"></span>' if is_today else ''
        row_cls = "pivot-row today" if is_today else "pivot-row"
        pivot_rows.append(
            f'<div class="{row_cls}" data-date="{esc(d)}" title="点击查看 {d} 全部新闻（{total_row} 条）">'
            f'<div class="pivot-date"><b>{d}</b><span class="weekday">{wd}</span>{today_dot}</div>'
            f'<div class="pivot-cells">{"".join(cells_html)}</div>'
            f'<div class="pivot-total" data-date="{esc(d)}" title="点击查看 {d} 全部新闻">{total_row}</div>'
            f'</div>'
        )
    stats_top = f'''<div class="pivot-wrapper">
        <div class="pivot-title">📅 国内 · 各日按分类分布</div>
        <div class="pivot-subtitle">点击分类胶囊跳转当日该类新闻；点击行或总计跳转当日全部新闻</div>
        <div class="pivot-rows">{"".join(pivot_rows)}</div>
    </div>'''

    # 左侧栏目侧边栏
    cat_counts = {}
    for d in dates:
        for it in archive.get(d, []):
            c = it.get("category", "")
            if c in cat_order:
                cat_counts[c] = cat_counts.get(c, 0) + 1
    sidebar_items = [
        '<button class="col-item active" data-column="all"><span class="ic">📚</span><span class="nm">全部栏目</span><span class="cnt">' + str(total_count) + '</span></button>'
    ]
    for c in cat_order:
        cnt = cat_counts.get(c, 0)
        sidebar_items.append(
            f'<button class="col-item" data-column="{esc(c)}"><span class="ic">{cat_icon.get(c, "📌")}</span><span class="nm">{esc(c)}</span><span class="cnt">{cnt}</span></button>'
        )
    column_sidebar = '\n'.join(sidebar_items)

    # 顶部日期按钮
    date_buttons = ['<button class="date-btn active" data-date="all">全部日期 <span class="cnt">' + str(total_count) + '</span></button>']
    for d in sorted(dates, reverse=True):
        cnt = len(archive.get(d, []))
        is_today = (d == today)
        label = f"{d[5:]} {'· 今' if is_today else ''} ({cnt})"
        date_buttons.append(f'<button class="date-btn" data-date="{d}">{label}</button>')
    date_head_buttons = '\n'.join(date_buttons)

    # 构造 window_str / now_full
    if dates:
        window_str = f"{dates[-1][5:]} ~ {dates[0][5]}（近 7 天）"
    else:
        window_str = NOW.strftime("%m-%d（暂无数据）")
    now_full = NOW.strftime("%Y-%m-%d %H:%M")

    # 读模板
    with open(TEMPLATE_FILE, encoding="utf-8") as f:
        template = f.read()

    # 数据 JSON（escape </script> 防止 JS 注入）
    news_data = {"archive": archive, "dates": dates, "today": today}
    news_json = json.dumps(news_data, ensure_ascii=False)
    news_json = news_json.replace("</", "<\\/")

    replacements = {
        "__TITLE__": "🇨🇳 国内重大新闻看板 · Ira 信息看板",
        "__HEADER_H1__": "🇨🇳 国内重大新闻看板",
        "__SUBTITLE__": "信源：中国政府网·要闻 / 央视 / 人民日报 / 外交部全栏目 / 商务部全栏目 / 发改委 / 联合早报 等 · 7 大分类（元首/高层/会议/人事/部委/政策/经贸）· 该看板仅供 Ira 信息看板体系参考交流",
        "__NAVBAR_INTL_ACTIVE__": "active",
        "__NAVBAR_AI_ACTIVE__": "",
        "__SOURCE_NOTE__": "国内权威信源（中国政府网/央视/外交部/商务部/联合早报）· 已过滤营销号/娱乐八卦/养生伪科学/地方琐事等非权威内容。",
        "__STATS_TOP__": stats_top,
        "__SIDEBAR_HEADER__": "📂 栏目筛选",
        "__COLUMN_SIDEBAR__": column_sidebar,
        "__DATE_HEAD_BUTTONS__": date_head_buttons,
        "__TOTAL_COUNT__": str(total_count),
        "__TODAY_COUNT__": str(today_count),
        "__HIGH_COUNT__": str(high_count),
        "__DATE_COUNT__": str(date_count),
        "__NOW_STR__": window_str,
        "__NOW_FULL__": now_full,
        "__NEWS_DATA_JSON__": news_json,
        "__FOOTER__": "🇨🇳 国内新闻看板 V2.11 · 表格化统一 UI · 数据更新于 " + now_full + " · 7天存档 · Powered by Ira 信息看板体系",
        "__THEME_PRIMARY__": THEME["primary"],
        "__THEME_PRIMARY_2__": THEME["primary_2"],
        "__THEME_PRIMARY_LIGHT__": THEME["primary_light"],
        "__THEME_PRIMARY_BG__": THEME["primary_bg"],
        "__THEME_PRIMARY_BG_2__": THEME["primary_bg_2"],
        "__THEME_GRAD_1__": THEME["grad_1"],
        "__THEME_GRAD_2__": THEME["grad_2"],
        "__THEME_GRAD_3__": THEME["grad_3"],
        "__THEME_SHADOW_PRIMARY__": THEME["shadow_primary"],
        "__THEME_ROW_HOVER__": THEME["row_hover"],
    }
    for k, v in replacements.items():
        template = template.replace(k, v)

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(template)

    print(f"written: {OUT_HTML} ({len(template)} bytes)")
    print(f"  总 {total_count} 条 | 今日 {today_count} 条 | 高优 {high_count} 条")
    print(f"  日期数: {date_count} | 顶部统计表: {len(pivot_rows)} 行")


def main():
    try:
        build()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()