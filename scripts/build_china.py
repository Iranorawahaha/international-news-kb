#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_china.py — 国内重大新闻看板 单文件 HTML 构建器 v2（Ira 信息看板体系）

视觉规范（v5 用户偏好）：
- 浅色底 + 蓝色主色调顶部
- 左侧 sidebar（sticky 悬浮）+ 右侧主内容
- 透视表式日期×类别交叉筛选交互
- 表格要素齐全；大标题不花哨

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
OUT_HTML = os.path.join(BASE_DIR, "china-news.html")


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    archive = data.get("archive", {})
    dates = data.get("dates", [])
    stats = data.get("stats", {})
    total = stats.get("totalArticles", 0)
    summit_count = stats.get("summitCount", 0)
    today = data.get("today", NOW.strftime("%Y-%m-%d"))
    today_new = data.get("todayCount", 0)

    # 7 类分类体系（v5）
    cat_order = ["元首动态", "高层动态", "重要会议", "人事任免", "部委动态", "政策发布", "经贸动向"]

    # 分类计数
    per_cat = {}
    for d in dates:
        for it in archive.get(d, []):
            per_cat[it.get("category", "其他")] = per_cat.get(it.get("category", "其他"), 0) + 1

    def cat_icon(c):
        return {"元首动态": "👑", "高层动态": "🧭", "重要会议": "🏛",
                "人事任免": "📋", "部委动态": "🏢", "政策发布": "📜", "经贸动向": "💹"}.get(c, "📌")

    # ============== 透视表数据预计算 ==============
    pivot = {}  # {date: {cat: count}}
    for d in dates:
        pivot[d] = {}
        for c in cat_order:
            pivot[d][c] = 0
        for it in archive.get(d, []):
            c = it.get("category", "")
            if c in pivot[d]:
                pivot[d][c] += 1

    # ============== 卡片渲染 ==============
    def article_card(it, idx):
        title = esc(it.get("title", ""))
        url = esc(it.get("url", "#"))
        src = esc(it.get("source", ""))
        cat = it.get("category", "其他")
        score = it.get("priority_score", 0)
        summit = "⭐" if it.get("is_summit_level") else ""
        date_str = esc(it.get("date", ""))
        summary = esc(it.get("summary", "") or "")
        if score >= 95:
            cls = "imp-summit"
        elif score >= 85:
            cls = "imp-high"
        else:
            cls = ""
        is_today = (it.get("date") == today)
        date_label_class = "date-badge today" if is_today else "date-badge"
        date_label = f'<span class="{date_label_class}">📅 {date_str}</span>'
        today_mark = '<span class="tag-today">🆕 今日</span>' if is_today else ""
        summary_html = f'<p class="card-summary">{summary}</p>' if summary else ""
        return f'''<div class="card {cls}" data-cat="{esc(cat)}" data-date="{date_str}">
          <div class="card-idx">{idx}</div>
          <div class="card-body">
            <div class="card-title-row">
              <h3 class="card-title">{summit}{title}{today_mark}</h3>
              <div class="card-meta-right">
                {date_label}
                <a class="card-link" href="{url}" target="_blank" rel="noopener noreferrer">原文 ↗</a>
              </div>
            </div>
            {summary_html}
            <div class="card-meta">
              <span class="meta-cat">{cat_icon(cat)} {cat}</span>
              <span class="meta-src">📰 {src}</span>
              <span class="meta-imp">权重 {score}</span>
            </div>
          </div>
        </div>'''

    # ============== 左侧 sidebar ==============
    sidebar_items = []
    today_archive = archive.get(today, [])
    today_per_cat = {}
    for it in today_archive:
        c = it.get("category", "其他")
        today_per_cat[c] = today_per_cat.get(c, 0) + 1
    today_total = len(today_archive)
    sidebar_items.append(
        f'<button class="col-item active" data-cat="all"><span class="ic">📋</span>全部<span class="cnt">新增{today_total}</span></button>')
    for c in cat_order:
        cnt = today_per_cat.get(c, 0)
        icon = cat_icon(c)
        sidebar_items.append(
            f'<button class="col-item" data-cat="{esc(c)}"><span class="ic">{icon}</span>{esc(c)}<span class="cnt">新增{cnt}</span></button>')

    # ============== 透视表渲染 ==============
    weekday_map = {0: '周一', 1: '周二', 2: '周三', 3: '周四', 4: '周五', 5: '周六', 6: '周日'}
    pivot_rows = []
    # 表头
    pivot_headers = '<th class="pv-th pv-date-hd">日期</th>'
    for c in cat_order:
        pivot_headers += f'<th class="pv-th pv-cat-hd">{cat_icon(c)} {c[:2]}</th>'
    pivot_headers += '<th class="pv-th pv-total-hd">合计</th>'
    # 数据行
    for d in dates:
        dt = datetime.strptime(d, '%Y-%m-%d')
        wd = weekday_map[dt.weekday()]
        is_today = (d == today)
        row_cls = 'pv-row today' if is_today else 'pv-row'
        date_label = f'<span class="pv-date">{dt.month}月{dt.day}日</span><span class="pv-wd">{wd}</span>'
        if is_today:
            date_label += '<span class="pv-today-dot"></span>'
        cells = f'<td class="pv-cell pv-date-cell">{date_label}</td>'
        row_total = 0
        for c in cat_order:
            cnt = pivot[d].get(c, 0)
            row_total += cnt
            if cnt > 0:
                cells += f'<td class="pv-cell pv-num-cell" data-date="{d}" data-cat="{esc(c)}"><span class="pv-num">{cnt}</span><span class="pv-label">条</span></td>'
            else:
                cells += f'<td class="pv-cell pv-zero-cell">—</td>'
        cells += f'<td class="pv-cell pv-total-cell"><span class="pv-total-num">{row_total}</span></td>'
        pivot_rows.append(f'<tr class="{row_cls}">{cells}</tr>')

    pivot_html = f'''<div class="pivot-wrapper">
      <table class="pivot-table">
        <thead><tr>{pivot_headers}</tr></thead>
        <tbody>{"".join(pivot_rows)}</tbody>
      </table>
    </div>'''

    # ============== 主内容区 ==============
    main_panels = []
    # "全部" 面板
    all_items_html = []
    for d in dates:
        items = archive.get(d, [])
        if not items: continue
        is_today = (d == today)
        d_cls = "date-group-header today" if is_today else "date-group-header"
        d_label = "🆕 今天" if is_today else d
        all_items_html.append(
            f'<div class="{d_cls}" data-date="{d}">📅 {d_label} <span class="date-count">{len(items)} 条</span></div>')
        for idx, it in enumerate(items, 1):
            all_items_html.append(article_card(it, idx))
    empty_panel_html = '<div class="empty-panel">暂无要闻</div>'
    main_panels.append(
        '<div class="cat-panel active" id="cat-panel-all">' + (
            "".join(all_items_html) if all_items_html else empty_panel_html) + '</div>')

    # 每个 日期×类别 交叉面板
    for d in dates:
        for c in cat_order:
            cat_items_in_date = [it for it in archive.get(d, []) if it.get("category") == c]
            items = []
            for idx, it in enumerate(cat_items_in_date, 1):
                items.append(article_card(it, idx))
            panel_id = f"cat-panel-{d}-{esc(c)}"
            main_panels.append(
                f'<div class="cat-panel" id="{panel_id}">' + (
                    "".join(items) if items else f'<div class="empty-panel">暂无{c}类新闻</div>') + '</div>')

    # 日期信息
    window_start = dates[-1] if dates else NOW.strftime("%Y-%m-%d")
    window_end = dates[0] if dates else NOW.strftime("%Y-%m-%d")

    doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>国内重大新闻看板 · Ira 信息看板</title>
<style>
  :root {{
    --font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    --bg: #f8fafc;
    --bg-soft: #f0f4ff;
    --panel: #fff;
    --line: #dbeafe;
    --line-soft: #e0e7ff;
    --ink: #1e293b;
    --muted: #64748b;
    --muted-soft: #94a3b8;
    --main: #2563eb;
    --main-dark: #1d4ed8;
    --main-2: #3b82f6;
    --main-soft: #eff6ff;
    --blue-grad-1: #1e3a5f;
    --blue-grad-2: #1d4ed8;
    --blue-grad-3: #3b82f6;
    --today: #2563eb;
    --today-bg: #eff6ff;
    --today-text: #1d4ed8;
    --summit: #f59e0b;
    --summit-bg: #fffbeb;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: var(--font); background: var(--bg); color: var(--ink); line-height: 1.65; }}
  .wrap {{ max-width: 1320px; margin: 0 auto; padding: 16px 16px 60px; }}

  /* 顶栏 — 蓝色 */
  header.hero {{ background: linear-gradient(135deg, var(--blue-grad-1) 0%, var(--blue-grad-2) 55%, var(--blue-grad-3) 100%); color: #fff; border-radius: 14px; padding: 22px 28px 18px; box-shadow: 0 8px 22px rgba(37,99,235,.25); position: relative; overflow: hidden; }}
  header.hero::after {{ content: ""; position: absolute; right: -60px; top: -60px; width: 220px; height: 220px; border-radius: 50%; background: rgba(255,255,255,.06); }}
  .hero-back {{ display: flex; align-items: center; gap: 8px; font-size: 12.5px; margin-bottom: 12px; position: relative; z-index: 1; flex-wrap: wrap; }}
  .hero-back a {{ color: #fff; text-decoration: none; background: rgba(255,255,255,.16); padding: 4px 12px; border-radius: 999px; font-weight: 600; transition: background .15s; }}
  .hero-back a:hover {{ background: rgba(255,255,255,.3); }}
  .hero-back-sep {{ opacity: .6; }}
  .hero-back-cur {{ background: rgba(255,255,255,.1); padding: 4px 12px; border-radius: 999px; }}
  .hero h1 {{ font-size: 21px; font-weight: 700; letter-spacing: .5px; }}
  .hero .hero-meta {{ display: flex; gap: 10px; margin-top: 13px; flex-wrap: wrap; font-size: 12px; position: relative; z-index: 1; }}
  .hero .hero-meta span {{ background: rgba(255,255,255,.15); padding: 3px 11px; border-radius: 999px; }}

  /* 刷新条 */
  .refresh-strip {{ background: var(--main-soft); border: 1px solid #bfdbfe; color: var(--main-dark); border-radius: 10px; padding: 9px 16px; font-size: 12.5px; margin: 14px 0; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .rs-dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--main); box-shadow: 0 0 0 3px rgba(37,99,235,.18); }}

  /* KPI */
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 18px; }}
  .kpi-card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; }}
  .kpi-num {{ font-size: 24px; font-weight: 800; }}
  .kpi-main .kpi-num {{ color: var(--main); }}
  .kpi-label {{ font-size: 11.5px; color: var(--muted); margin-top: 2px; }}

  /* ===== 透视表 ===== */
  .pivot-wrapper {{ margin-bottom: 20px; overflow-x: auto; border: 1px solid var(--line); border-radius: 12px; background: var(--panel); box-shadow: 0 2px 8px rgba(37,99,235,.06); }}
  .pivot-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  .pivot-table thead {{ background: linear-gradient(180deg, var(--main-soft), #fff); }}
  .pv-th {{ padding: 10px 8px; font-weight: 700; font-size: 11.5px; color: var(--muted); border-bottom: 2px solid var(--line); text-align: center; white-space: nowrap; letter-spacing: 0.3px; }}
  .pv-date-hd {{ text-align: left; padding-left: 14px; min-width: 100px; }}
  .pv-cat-hd {{ min-width: 60px; }}
  .pv-total-hd {{ min-width: 50px; color: var(--main-dark); }}
  .pv-row {{ transition: background .15s; }}
  .pv-row:hover {{ background: var(--main-soft); }}
  .pv-row.today {{ background: linear-gradient(90deg, var(--today-bg), transparent); }}
  .pv-cell {{ padding: 6px 8px; text-align: center; border-bottom: 1px solid var(--line-soft); }}
  .pv-date-cell {{ text-align: left; padding-left: 14px; }}
  .pv-date {{ font-weight: 700; font-size: 13.5px; color: var(--ink); }}
  .pv-wd {{ font-size: 10.5px; color: var(--muted-soft); margin-left: 6px; }}
  .pv-today-dot {{ display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--main); margin-left: 8px; vertical-align: middle; }}
  .pv-num-cell {{ cursor: pointer; transition: all .15s; border-radius: 4px; }}
  .pv-num-cell:hover {{ background: var(--main); color: #fff; }}
  .pv-num-cell.active {{ background: var(--main); color: #fff; }}
  .pv-num-cell .pv-num {{ font-weight: 800; font-size: 15px; font-family: ui-monospace, monospace; }}
  .pv-num-cell .pv-label {{ font-size: 10px; margin-left: 1px; }}
  .pv-num-cell:hover .pv-label {{ color: #fff; }}
  .pv-num-cell.active .pv-label {{ color: #fff; }}
  .pv-zero-cell {{ color: var(--muted-soft); font-size: 11px; }}
  .pv-total-cell {{ font-weight: 700; }}
  .pv-total-num {{ font-family: ui-monospace, monospace; color: var(--main-dark); font-size: 14px; }}

  /* 搜索框 */
  .search-bar {{ margin: 10px 0; }}
  .search-bar input {{
    width: 100%; padding: 8px 16px; border: 2px solid var(--line);
    border-radius: 10px; font-size: 14px; font-family: var(--font);
    outline: none; transition: border-color .15s;
  }}
  .search-bar input:focus {{ border-color: var(--main); }}

  /* 主布局 */
  .layout {{ display: grid; grid-template-columns: 220px 1fr; gap: 16px; align-items: start; }}
  .sidebar {{
    position: sticky; top: 16px; background: var(--panel);
    border: 1px solid var(--line); border-radius: 12px; padding: 10px;
    max-height: calc(100vh - 32px); overflow-y: auto;
    box-shadow: 0 4px 14px rgba(37,99,235,.08);
  }}
  .sidebar-title {{ font-size: 11px; font-weight: 700; letter-spacing: 1.2px; color: var(--muted-soft); text-transform: uppercase; padding: 8px 10px 10px; display: flex; align-items: center; gap: 6px; }}
  .sidebar-title::after {{ content: ""; flex: 1; height: 1px; background: var(--line-soft); }}
  .col-item {{
    display: flex; align-items: center; gap: 10px; width: 100%;
    padding: 10px 12px; margin-bottom: 4px; border-radius: 10px;
    border: 1px solid transparent; background: transparent;
    color: var(--ink); font-size: 13px; font-weight: 600;
    font-family: inherit; cursor: pointer; transition: all .15s ease-out;
    text-align: left;
  }}
  .col-item:hover {{ background: var(--main-soft); color: var(--main); border-color: var(--main-soft); }}
  .col-item:active {{ transform: scale(0.98); }}
  .col-item.active {{
    background: linear-gradient(135deg, var(--main-dark), var(--main-2));
    color: #fff; box-shadow: 0 4px 14px rgba(37,99,235,.35);
  }}
  .col-item .ic {{ font-size: 16px; line-height: 1; }}
  .col-item .cnt {{
    margin-left: auto; font-family: ui-monospace, monospace;
    font-size: 11px; background: rgba(37,99,235,.1);
    padding: 2px 8px; border-radius: 99px; color: var(--muted); font-weight: 700;
  }}
  .col-item.active .cnt {{ background: rgba(255,255,255,.22); color: #fff; }}

  /* 主内容 */
  .main-content {{ min-width: 0; }}
  .cat-panel {{ display: none; }}
  .cat-panel.active {{ display: block; }}

  /* 透视表选中信息 */
  .pivot-info {{
    display: flex; align-items: center; gap: 8px;
    padding: 8px 14px; margin-bottom: 14px;
    background: var(--main-soft); border: 1px solid var(--line);
    border-radius: 10px; font-size: 13px; color: var(--main-dark);
  }}
  .pivot-info .pi-badge {{
    background: var(--main); color: #fff; padding: 1px 8px; border-radius: 99px;
    font-size: 11.5px; font-weight: 600;
  }}
  .pivot-info .pi-clear {{
    margin-left: auto; background: none; border: 1px solid var(--main);
    color: var(--main); padding: 3px 10px; border-radius: 99px;
    font-size: 11px; cursor: pointer; font-weight: 600; transition: all .15s;
  }}
  .pivot-info .pi-clear:hover {{ background: var(--main); color: #fff; }}

  /* 日期分组 */
  .date-group-header {{
    background: linear-gradient(90deg, var(--main-soft), transparent);
    border-left: 4px solid var(--main); padding: 9px 14px 9px 16px;
    margin: 18px 0 10px; font-size: 13.5px; font-weight: 700;
    color: var(--main-dark); border-radius: 0 8px 8px 0;
    letter-spacing: 0.3px; display: flex; align-items: center; gap: 10px;
  }}
  .date-group-header:first-child {{ margin-top: 0; }}
  .date-group-header.today {{ background: linear-gradient(90deg, var(--today-bg), transparent); border-left-color: var(--today); color: var(--today-text); }}
  .date-group-header .date-count {{ font-family: ui-monospace, monospace; font-size: 11.5px; color: var(--muted); background: var(--panel); padding: 2px 9px; border-radius: 99px; font-weight: 600; }}
  .date-group-header.today .date-count {{ background: var(--today); color: #fff; }}

  /* 卡片 */
  .card {{ display: flex; gap: 12px; background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 13px 14px; margin-bottom: 10px; transition: transform .15s, box-shadow .15s; align-items: flex-start; }}
  .card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(37,99,235,.1); }}
  .card.imp-summit {{ border-left: 4px solid var(--summit); background: linear-gradient(90deg, var(--summit-bg), var(--panel)); }}
  .card.imp-high {{ border-left: 4px solid var(--main); }}
  .card-idx {{ flex: 0 0 26px; height: 26px; border-radius: 8px; background: var(--main-soft); color: var(--main-dark); font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; }}
  .card-body {{ flex: 1; min-width: 0; }}
  .card-title-row {{ display: flex; gap: 12px; align-items: flex-start; justify-content: space-between; }}
  .card-title {{ font-size: 14.5px; font-weight: 650; line-height: 1.5; flex: 1; min-width: 0; }}
  .card-meta-right {{ display: flex; flex-direction: column; gap: 6px; align-items: flex-end; flex-shrink: 0; }}
  .date-badge {{
    font-family: ui-monospace, monospace; font-size: 12.5px; font-weight: 700;
    color: var(--main-dark); background: var(--main-soft);
    padding: 5px 12px; border-radius: 8px;
    border: 1px solid rgba(37,99,235,.18); white-space: nowrap; letter-spacing: 0.3px;
  }}
  .date-badge.today {{ background: var(--today); color: #fff; border-color: var(--today); box-shadow: 0 0 0 2px rgba(37,99,235,.2); }}
  .card-link {{ font-size: 12px; color: var(--main); text-decoration: none; font-weight: 600; padding: 4px 11px; border: 1px solid var(--main); border-radius: 8px; transition: all .15s; white-space: nowrap; }}
  .card-link:hover {{ background: var(--main); color: #fff; }}
  .card-summary {{ font-size: 12.5px; color: #4a5568; line-height: 1.65; margin-top: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
  .card-meta {{ display: flex; gap: 10px; margin-top: 6px; flex-wrap: wrap; align-items: center; }}
  .meta-cat {{ font-size: 11.5px; color: var(--main); background: var(--main-soft); padding: 2px 9px; border-radius: 999px; font-weight: 600; }}
  .meta-src {{ font-size: 11.5px; color: var(--muted); }}
  .meta-imp {{ font-size: 11.5px; color: var(--muted-soft); font-family: ui-monospace, monospace; }}
  .tag-today {{ background: var(--today); color: #fff; font-size: 10.5px; padding: 2px 8px; border-radius: 999px; margin-left: 6px; vertical-align: 1px; font-weight: 600; }}
  .hidden {{ display: none !important; }}
  .empty-panel {{ text-align: center; color: var(--muted); padding: 60px 0; font-size: 13px; }}

  @media (max-width: 880px) {{
    .layout {{ grid-template-columns: 1fr; }}
    .sidebar {{ position: static; max-height: none; }}
    .col-item {{ display: inline-flex; width: auto; margin-bottom: 0; margin-right: 6px; padding: 8px 12px; font-size: 12.5px; }}
    .sidebar-title {{ display: none; }}
    .pivot-wrapper {{ overflow-x: auto; }}
    .pivot-table {{ min-width: 700px; }}
  }}
  @media (max-width: 720px) {{
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .card-title-row {{ flex-direction: column; }}
    .card-meta-right {{ flex-direction: row; align-self: flex-start; }}
  }}
</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <div class="hero-back">
      <a href="https://iranorawahaha.github.io/international-news-kb/" target="_blank" rel="noopener noreferrer">🏠 Ira 信息看板</a>
      <span class="hero-back-sep">|</span>
      <a href="https://iranorawahaha.github.io/international-news-kb/international-news.html" target="_blank" rel="noopener noreferrer">🌍 国际新闻看板</a>
      <span class="hero-back-sep">|</span>
      <a href="https://iranorawahaha.github.io/international-news-kb/ai-news.html" target="_blank" rel="noopener noreferrer">🤖 AI 动向看板</a>
      <span class="hero-back-sep">|</span>
      <span class="hero-back-cur">🇨🇳 国内新闻看板</span>
    </div>
    <h1>国内重大新闻看板</h1>
    <div class="hero-meta">
      <span>📅 时间窗：{esc(window_start)} ~ {esc(window_end)}（近 7 天）</span>
      <span>🎯 要闻总数：{total} 条（去重）</span>
      <span>🆕 今日新增：{today_new} 条</span>
      <span>⭐ 元首级：{summit_count} 条</span>
    </div>
  </header>

  <div class="refresh-strip">
    <span class="rs-dot"></span>
    <b>最近刷新：</b>{esc(NOW.strftime("%Y-%m-%d %H:%M"))} 北京时间（每日自动刷新） ·
    <b>今日新增 {today_new} 条</b> · 滚动 7 天窗口 ·
    信源：中国政府网 > 5部委官网 > 央媒 · V5 聚焦 7 大类别
  </div>

  <div class="kpi-grid">
    <div class="kpi-card" style="border-left:4px solid #2563eb; background:linear-gradient(180deg,#eff6ff,#fff);"><div class="kpi-num" style="color:#2563eb;">{today_new}</div><div class="kpi-label">🆕 今日新增</div></div>
    <div class="kpi-card kpi-main"><div class="kpi-num">{total}</div><div class="kpi-label">要闻总数（去重后）</div></div>
    <div class="kpi-card" style="border-left:4px solid #f59e0b; background:linear-gradient(180deg,#fffbeb,#fff);"><div class="kpi-num" style="color:#f59e0b;">{summit_count}</div><div class="kpi-label">⭐ 元首级要闻</div></div>
    <div class="kpi-card"><div class="kpi-num">{len(dates)}</div><div class="kpi-label">覆盖天数</div></div>
  </div>

  <!-- 透视表 -->
  {pivot_html}

  <!-- 透视表筛选状态 -->
  <div class="pivot-info hidden" id="pivotInfo">
    📌 当前筛选：<span class="pi-badge" id="piDate"></span> × <span class="pi-badge" id="piCat"></span>
    <button class="pi-clear" onclick="clearPivot()">✕ 清除筛选</button>
  </div>

  <div class="search-bar">
    <input type="text" id="searchBox" placeholder="🔍 搜索标题、信源、摘要..." oninput="doSearch()">
  </div>

  <div class="layout">
    <aside class="sidebar" id="sidebar">
      <div class="sidebar-title">🗂️ 栏目导航</div>
      {''.join(sidebar_items)}
    </aside>
    <main class="main-content">
      {''.join(main_panels)}
    </main>
  </div>

</div>
<script>
  (function() {{
    var colItems = document.querySelectorAll('.col-item');
    var pivotCells = document.querySelectorAll('.pv-num-cell');
    var activeCat = 'all';
    var activeDate = 'all';
    var activePanelId = 'cat-panel-all';

    function switchPanel(panelId) {{
      activePanelId = panelId;
      document.querySelectorAll('.cat-panel').forEach(function(p) {{ p.classList.remove('active'); }});
      var panel = document.getElementById(panelId);
      if (panel) panel.classList.add('active');
      doSearch();
    }}

    // 透视表点击
    pivotCells.forEach(function(cell) {{
      cell.addEventListener('click', function() {{
        // 去激活所有透视单元格
        pivotCells.forEach(function(c) {{ c.classList.remove('active'); }});
        cell.classList.add('active');

        activeDate = cell.dataset.date;
        activeCat = cell.dataset.cat;

        // 更新透视表信息条
        var pi = document.getElementById('pivotInfo');
        pi.classList.remove('hidden');
        document.getElementById('piDate').textContent = activeDate;
        document.getElementById('piCat').textContent = activeCat;

        // 侧边栏取消激活
        colItems.forEach(function(x) {{ x.classList.remove('active'); }});

        // 切换到对应面板
        switchPanel('cat-panel-' + activeDate + '-' + activeCat);
      }});
    }});

    // 清除透视表筛选
    window.clearPivot = function() {{
      pivotCells.forEach(function(c) {{ c.classList.remove('active'); }});
      document.getElementById('pivotInfo').classList.add('hidden');
      activeDate = 'all';
      activeCat = 'all';
      colItems.forEach(function(x) {{ x.classList.remove('active'); }});
      var allBtn = document.querySelector('.col-item[data-cat="all"]');
      if (allBtn) allBtn.classList.add('active');
      switchPanel('cat-panel-all');
    }};

    // 侧边栏切换
    colItems.forEach(function(item) {{
      item.addEventListener('click', function() {{
        colItems.forEach(function(x) {{ x.classList.remove('active'); }});
        item.classList.add('active');
        activeCat = item.dataset.cat;

        // 透视表筛选被覆盖时清除透视状态
        pivotCells.forEach(function(c) {{ c.classList.remove('active'); }});
        document.getElementById('pivotInfo').classList.add('hidden');
        activeDate = 'all';

        switchPanel('cat-panel-all');
      }});
    }});

    window.doSearch = function() {{
      var q = (document.getElementById('searchBox').value || '').toLowerCase();
      var activePanel = document.querySelector('.cat-panel.active');
      if (!activePanel) return;
      var cards = activePanel.querySelectorAll('.card');
      var headers = activePanel.querySelectorAll('.date-group-header');

      // 重置全部可见
      cards.forEach(function(c) {{ c.classList.remove('hidden'); }});
      headers.forEach(function(h) {{ h.classList.remove('hidden'); }});

      // 栏目筛选（从侧边栏）
      if (activeCat !== 'all') {{
        cards.forEach(function(c) {{
          if (c.dataset.cat !== activeCat) c.classList.add('hidden');
        }});
      }}

      // 搜索词筛选
      if (q) {{
        cards.forEach(function(c) {{
          if (!c.classList.contains('hidden')) {{
            var t = (c.textContent || '').toLowerCase();
            if (!t.includes(q)) c.classList.add('hidden');
          }}
        }});
      }}

      // 隐藏空日期分组
      headers.forEach(function(h) {{
        var next = h.nextElementSibling;
        var anyVisible = false;
        while (next && !next.classList.contains('date-group-header')) {{
          if (!next.classList.contains('hidden')) anyVisible = true;
          next = next.nextElementSibling;
        }}
        h.classList.toggle('hidden', !anyVisible);
      }});
    }};
  }})();
</script>
</body>
</html>'''

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)

    # JS 语法自检
    js_blocks = re.findall(r"<script>(.*?)</script>", doc, re.S)
    ok = True
    for i, js in enumerate(js_blocks, 1):
        try:
            r = sp.run(["node", "--check"], input=js.encode("utf-8"), capture_output=True, timeout=10)
            if r.returncode != 0:
                ok = False
                print(f"❌ JS 语法错误 (script#{i}): {(r.stderr or b'').decode('utf-8','replace')[:150]}")
        except Exception:
            if js.count("{") != js.count("}"):
                ok = False
    print("✅ JS 语法自检通过" if ok else "❌ JS 语法自检失败")
    if not ok:
        return 1

    print(f"=== 国内重大新闻看板 V5（蓝色透视表）===")
    print(f"总条数: {total} | 分类(7类): {per_cat}")
    print(f"written: {OUT_HTML} {len(doc)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(build())
