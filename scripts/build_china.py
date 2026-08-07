#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_china.py — 国内新闻看板 单文件 HTML 构建器（Ira 信息看板体系）

参照国际新闻 V1.5 视觉规范：
- 浅色底 + 蓝色顶部
- 左侧 sidebar（sticky 悬浮）+ 右侧主内容
- 发布时间右侧醒目徽章

读取 data/china-news.json，生成 china-news.html（单文件，纯内联 CSS/JS，无外部资源）。
"""
import json
import os
import re
import sys
import subprocess
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

    # 分类计数
    per_cat = {}
    for d in dates:
        for it in archive.get(d, []):
            per_cat[it.get("category", "其他")] = per_cat.get(it.get("category", "其他"), 0) + 1

    cat_order = ["元首动态", "高层动态", "使领馆动向", "重要会议", "人事任免", "部委动态", "政策发布", "经贸动向"]
    cat_map_zh = {c: c for c in cat_order}

    def cat_icon(c):
        return {"元首动态": "👑", "高层动态": "🧭", "使领馆动向": "🕊️", "重要会议": "🏛",
                "人事任免": "📋", "部委动态": "🏢", "政策发布": "📜", "经贸动向": "💹"}.get(c, "📌")

    # ============== 卡片渲染（按日期分组 + 醒目时间） ==============
    def article_card(it, idx):
        title = esc(it.get("title", ""))
        url = esc(it.get("url", "#"))
        src = esc(it.get("source", ""))
        cat = it.get("category", "其他")
        score = it.get("priority_score", 0)
        summit = "⭐" if it.get("is_summit_level") else ""
        date_str = esc(it.get("date", ""))
        summary = esc(it.get("summary", "") or "")
        # 高分色
        if score >= 95:
            cls = "imp-summit"
        elif score >= 85:
            cls = "imp-high"
        else:
            cls = ""
        # 是否今天（更醒目）
        is_today = (it.get("date") == today)
        date_label_class = "date-badge today" if is_today else "date-badge"
        date_label = f'<span class="{date_label_class}">📅 {date_str}</span>'
        # 🆕 今日标记
        today_mark = '<span class="tag-today">🆕 今日</span>' if is_today else ""
        summary_html = f'<p class="card-summary">{summary}</p>' if summary else ""
        return f'''<div class="card {cls}">
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

    # ============== 左侧 sidebar（sticky 栏目） ==============
    sidebar_items = []
    # V2.1: 栏目数字标签改为当日新增
    today_archive = archive.get(today, [])
    today_per_cat = {}
    for it in today_archive:
        c = it.get("category", "其他")
        today_per_cat[c] = today_per_cat.get(c, 0) + 1
    today_total = len(today_archive)
    sidebar_items.append(f'<button class="col-item active" data-cat="all"><span class="ic">📋</span>全部<span class="cnt">新增{today_total}</span></button>')
    for c in cat_order:
        cnt = today_per_cat.get(c, 0)
        icon = cat_icon(c)
        sidebar_items.append(f'<button class="col-item" data-cat="{esc(c)}"><span class="ic">{icon}</span>{esc(c)}<span class="cnt">新增{cnt}</span></button>')

    # ============== 日期标签栏 ==============
    weekday_map = {0: '周日', 1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六'}
    date_tabs = []
    for d in dates:
        dt = datetime.strptime(d, '%Y-%m-%d')
        wd = weekday_map[dt.weekday()]
        is_today = (d == today)
        total_in_date = len(archive.get(d, []))
        active_cls = 'active' if is_today else ''
        date_tabs.append(f'<button class="date-tab {active_cls}" data-date="{d}">{dt.month}月{dt.day}日 {wd}<span class="date-tab-cnt">{total_in_date}</span></button>')
    date_tabs_html = '\n        '.join(date_tabs)

    # ============== 主内容区（按日期分组） ==============
    main_panels = []
    # "全部" 面板：按日期分组
    all_items_html = []
    for d in dates:
        items = archive.get(d, [])
        if not items: continue
        is_today = (d == today)
        d_cls = "date-group-header today" if is_today else "date-group-header"
        d_label = "🆕 今天" if is_today else d
        all_items_html.append(f'<div class="{d_cls}">📅 {d_label} <span class="date-count">{len(items)} 条</span></div>')
        for idx, it in enumerate(items, 1):
            all_items_html.append(article_card(it, idx))
    empty_panel_html = '<div class="empty-panel">暂无要闻</div>'
    main_panels.append('<div class="cat-panel active" id="cat-panel-all">' + ("".join(all_items_html) if all_items_html else empty_panel_html) + '</div>')

    # 每个日期的面板
    for d in dates:
        items = archive.get(d, [])
        date_html = []
        for idx, it in enumerate(items, 1):
            date_html.append(article_card(it, idx))
        main_panels.append(f'<div class="cat-panel" id="cat-panel-date-{d}">' + ("".join(date_html) if date_html else empty_panel_html) + '</div>')

    # 每个分类面板（也按日期分组）
    for c in cat_order:
        items = []
        for d in dates:
            cat_items = [it for it in archive.get(d, []) if it.get("category") == c]
            if not cat_items:
                continue
            is_today = (d == today)
            d_cls = "date-group-header today" if is_today else "date-group-header"
            d_label = "🆕 今天" if is_today else d
            items.append(f'<div class="{d_cls}">📅 {d_label} <span class="date-count">{len(cat_items)} 条</span></div>')
            for idx, it in enumerate(cat_items, 1):
                items.append(article_card(it, idx))
        empty_for_cat = '<div class="empty-panel">暂无' + c + '类新闻</div>'
        main_panels.append('<div class="cat-panel" id="cat-panel-' + esc(c) + '">' + ("".join(items) if items else empty_for_cat) + '</div>')

    # 日期信息
    window_start = dates[-1] if dates else NOW.strftime("%Y-%m-%d")
    window_end = dates[0] if dates else NOW.strftime("%Y-%m-%d")

    doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>国内新闻看板 · Ira 信息看板</title>
<style>
  :root {{
    --font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    --bg: #fdf2f2;
    --bg-soft: #fef8f8;
    --panel: #fff;
    --line: #f5d0d0;
    --line-soft: #fce8e8;
    --ink: #1c2434;
    --muted: #64707f;
    --muted-soft: #8a96a8;
    --main: #dc2626;
    --main-dark: #991b1b;
    --main-2: #ef4444;
    --main-soft: #fef2f2;
    --red-grad-1: #991b1b;
    --red-grad-2: #b91c1c;
    --red-grad-3: #dc2626;
    --today: #dc2626;
    --today-bg: #fef2f2;
    --today-text: #991b1b;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: var(--font); background: var(--bg); color: var(--ink); line-height: 1.65; }}
  .wrap {{ max-width: 1280px; margin: 0 auto; padding: 16px 16px 60px; }}

  /* 顶栏 — 红色 */
  header.hero {{ background: linear-gradient(135deg, var(--red-grad-1) 0%, var(--red-grad-2) 55%, var(--red-grad-3) 100%); color: #fff; border-radius: 14px; padding: 22px 28px 18px; box-shadow: 0 8px 22px rgba(153,27,27,.25); position: relative; overflow: hidden; }}
  header.hero::after {{ content: ""; position: absolute; right: -60px; top: -60px; width: 220px; height: 220px; border-radius: 50%; background: rgba(255,255,255,.06); }}
  .hero-back {{ display: flex; align-items: center; gap: 8px; font-size: 12.5px; margin-bottom: 12px; position: relative; z-index: 1; flex-wrap: wrap; }}
  .hero-back a {{ color: #fff; text-decoration: none; background: rgba(255,255,255,.16); padding: 4px 12px; border-radius: 999px; font-weight: 600; transition: background .15s; }}
  .hero-back a:hover {{ background: rgba(255,255,255,.3); }}
  .hero-back-sep {{ opacity: .6; }}
  .hero-back-cur {{ background: rgba(255,255,255,.1); padding: 4px 12px; border-radius: 999px; }}
  .hero h1 {{ font-size: 21px; font-weight: 700; letter-spacing: .5px; }}
  .hero .hero-meta {{ display: flex; gap: 10px; margin-top: 13px; flex-wrap: wrap; font-size: 12px; position: relative; z-index: 1; }}
  .hero .hero-meta span {{ background: rgba(255,255,255,.15); padding: 3px 11px; border-radius: 999px; }}

  /* 搜索框 */
  .search-bar {{ margin: 10px 0; }}

  /* 日期标签栏 */
  .date-tabs {{
    display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px;
  }}
  .date-tab {{
    padding: 7px 14px; border: 1px solid var(--line); border-radius: 10px;
    background: var(--panel); color: var(--ink); font-size: 13px; font-weight: 600;
    font-family: var(--font); cursor: pointer; transition: all .15s;
    display: flex; align-items: center; gap: 6px;
  }}
  .date-tab:hover {{ border-color: var(--main); background: var(--main-soft); }}
  .date-tab.active {{
    background: linear-gradient(135deg, var(--main-dark), var(--main-2));
    color: #fff; border-color: var(--main); box-shadow: 0 4px 12px rgba(220,38,38,.25);
  }}
  .date-tab-cnt {{
    font-family: ui-monospace, monospace; font-size: 11px;
    background: rgba(0,0,0,.06); padding: 1px 7px; border-radius: 99px; font-weight: 700;
  }}
  .date-tab.active .date-tab-cnt {{ background: rgba(255,255,255,.2); }}
  .search-bar {{ margin: 10px 0; }}
  .search-bar input {{
    width: 100%; padding: 8px 16px; border: 2px solid var(--line);
    border-radius: 10px; font-size: 14px; font-family: var(--font);
    outline: none; transition: border-color .15s;
  }}
  .search-bar input:focus {{ border-color: var(--main); }}

  /* 刷新条 */
  .refresh-strip {{ background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; border-radius: 10px; padding: 9px 16px; font-size: 12.5px; margin: 14px 0; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .rs-dot {{ width: 8px; height: 8px; border-radius: 50%; background: #dc2626; box-shadow: 0 0 0 3px rgba(220,38,38,.18); }}

  /* KPI */
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 18px; }}
  .kpi-card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; }}
  .kpi-num {{ font-size: 24px; font-weight: 800; }}
  .kpi-main .kpi-num {{ color: var(--main); }}
  .kpi-label {{ font-size: 11.5px; color: var(--muted); margin-top: 2px; }}

  /* 主布局 */
  .layout {{ display: grid; grid-template-columns: 240px 1fr; gap: 16px; align-items: start; }}
  .sidebar {{
    position: sticky; top: 16px; background: var(--panel);
    border: 1px solid var(--line); border-radius: 12px; padding: 10px;
    max-height: calc(100vh - 32px); overflow-y: auto;
    box-shadow: 0 4px 14px rgba(153,27,27,.08);
  }}
  .sidebar-title {{ font-size: 11px; font-weight: 700; letter-spacing: 1.2px; color: var(--muted-soft); text-transform: uppercase; padding: 8px 10px 10px; display: flex; align-items: center; gap: 6px; }}
  .sidebar-title::after {{ content: ""; flex: 1; height: 1px; background: var(--line-soft); }}
  .col-item {{
    display: flex; align-items: center; gap: 10px; width: 100%;
    padding: 10px 12px; margin-bottom: 4px; border-radius: 10px;
    border: 1px solid transparent; background: transparent;
    color: var(--ink); font-size: 13.5px; font-weight: 600;
    font-family: inherit; cursor: pointer; transition: all .15s ease-out;
    text-align: left;
  }}
  .col-item:hover {{ background: var(--main-soft); color: var(--main); border-color: var(--main-soft); }}
  .col-item:active {{ transform: scale(0.98); }}
  .col-item.active {{
    background: linear-gradient(135deg, var(--main-dark), var(--main-2));
    color: #fff; box-shadow: 0 4px 14px rgba(220,38,38,.35);
  }}
  .col-item .ic {{ font-size: 16px; line-height: 1; }}
  .col-item .cnt {{
    margin-left: auto; font-family: ui-monospace, monospace;
    font-size: 11px; background: rgba(180,150,150,.18);
    padding: 2px 8px; border-radius: 99px; color: var(--muted); font-weight: 700;
  }}
  .col-item.active .cnt {{ background: rgba(255,255,255,.22); color: #fff; }}

  /* 主内容 */
  .main-content {{ min-width: 0; }}
  .cat-panel {{ display: none; }}
  .cat-panel.active {{ display: block; }}

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
  .card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(153,27,27,.1); }}
  .card.imp-summit {{ border-left: 4px solid #c9a227; background: linear-gradient(90deg, #fdfaf0, var(--panel)); }}
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
    border: 1px solid rgba(220,38,38,.18); white-space: nowrap; letter-spacing: 0.3px;
  }}
  .date-badge.today {{ background: var(--today); color: #fff; border-color: var(--today); box-shadow: 0 0 0 2px rgba(220,38,38,.2); }}
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
    <h1>国内新闻看板</h1>
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
    信源权重：中国政府网 &gt; 部委官网 &gt; 媒体 · 已排除"人民情怀"回顾评述栏目
  </div>

  <div class="kpi-grid">
    <div class="kpi-card" style="border-left:4px solid #dc2626; background:linear-gradient(180deg,#fef2f2,#fff);"><div class="kpi-num" style="color:#dc2626;">{today_new}</div><div class="kpi-label">🆕 今日新增</div></div>
    <div class="kpi-card kpi-main"><div class="kpi-num">{total}</div><div class="kpi-label">要闻总数（去重后）</div></div>
    <div class="kpi-card"><div class="kpi-num">{summit_count}</div><div class="kpi-label">⭐ 元首级要闻</div></div>
    <div class="kpi-card"><div class="kpi-num">{len(dates)}</div><div class="kpi-label">覆盖天数</div></div>
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
      <div class="date-tabs" id="dateTabs">
        <button class="date-tab active" data-date="all">📅 全部</button>
        {date_tabs_html}
      </div>
      <div class="search-bar">
        <input type="text" id="searchBox" placeholder="🔍 搜索标题、信源、摘要..." oninput="doSearch()">
      </div>
      {''.join(main_panels)}
    </main>
  </div>

</div>
<script>
  (function() {{
    var colItems = document.querySelectorAll('.col-item');
    var dateTabs = document.querySelectorAll('#dateTabs .date-tab');
    var activeCat = 'all';
    var activeDate = 'all';

    function switchPanel() {{
      var targetId;
      if (activeDate !== 'all') {{
        targetId = 'cat-panel-date-' + activeDate;
      }} else {{
        targetId = 'cat-panel-all';
      }}
      document.querySelectorAll('.cat-panel').forEach(function(p) {{ p.classList.remove('active'); }});
      var panel = document.getElementById(targetId);
      if (panel) panel.classList.add('active');
      doSearch();
    }}

    // 栏目切换
    colItems.forEach(function(item) {{
      item.addEventListener('click', function() {{
        colItems.forEach(function(x) {{ x.classList.remove('active'); }});
        item.classList.add('active');
        activeCat = item.dataset.cat;
        switchPanel();
      }});
    }});

    // 日期切换
    dateTabs.forEach(function(tab) {{
      tab.addEventListener('click', function() {{
        dateTabs.forEach(function(t) {{ t.classList.remove('active'); }});
        tab.classList.add('active');
        activeDate = tab.dataset.date;
        switchPanel();
      }});
    }});

    window.doSearch = function() {{
      var q = (document.getElementById('searchBox').value || '').toLowerCase();
      var activePanel = document.querySelector('.cat-panel.active');
      if (!activePanel) return;
      var cards = activePanel.querySelectorAll('.card');
      var headers = activePanel.querySelectorAll('.date-group-header');
      // 筛选栏目
      if (activeCat !== 'all') {{
        cards.forEach(function(c) {{
          var catEl = c.querySelector('.meta-cat');
          var cat = catEl ? catEl.textContent.trim() : '';
          if (!cat.includes(activeCat)) c.classList.add('hidden');
          else c.classList.remove('hidden');
        }});
      }}
      if (!q) {{
        cards.forEach(function(c) {{ c.classList.remove('hidden'); }});
        if (headers.length) headers.forEach(function(h) {{ h.classList.remove('hidden'); }});
        // 重新 apply 栏目筛选
        if (activeCat !== 'all') {{
          cards.forEach(function(c) {{
            var catEl = c.querySelector('.meta-cat');
            var cat = catEl ? catEl.textContent.trim() : '';
            if (!cat.includes(activeCat)) c.classList.add('hidden');
          }});
        }}
        return;
      }}
      cards.forEach(function(c) {{
        var t = (c.textContent || '').toLowerCase();
        if (t.includes(q)) c.classList.remove('hidden');
        else c.classList.add('hidden');
        // 同时筛选栏目
        if (activeCat !== 'all' && !c.classList.contains('hidden')) {{
          var catEl = c.querySelector('.meta-cat');
          var cat = catEl ? catEl.textContent.trim() : '';
          if (!cat.includes(activeCat)) c.classList.add('hidden');
        }}
      }});
      // 隐藏空日期分组
      if (headers.length) {{
        headers.forEach(function(h) {{
          var next = h.nextElementSibling;
          var anyVisible = false;
          while (next && !next.classList.contains('date-group-header')) {{
            if (!next.classList.contains('hidden')) anyVisible = true;
            next = next.nextElementSibling;
          }}
          h.classList.toggle('hidden', !anyVisible);
        }});
      }}
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

    print(f"=== 国内新闻看板（侧边栏 V2.0）===")
    print(f"总条数: {total} | 分类: {per_cat}")
    print(f"written: {OUT_HTML} {len(doc)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(build())