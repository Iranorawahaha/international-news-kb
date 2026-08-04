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

    # ============== 主内容区（按日期分组） ==============
    main_panels = []
    # "全部" 面板：按日期分组
    all_items_html = []
    if dates:
        for d in dates:
            items = archive.get(d, [])
            if not items:
                continue
            # 日期分组表头
            is_today = (d == today)
            d_cls = "date-group-header today" if is_today else "date-group-header"
            d_label = "🆕 今天" if is_today else d
            all_items_html.append(f'<div class="{d_cls}">📅 {d_label} <span class="date-count">{len(items)} 条</span></div>')
            for idx, it in enumerate(items, 1):
                all_items_html.append(article_card(it, idx))
    empty_panel_html = '<div class="empty-panel">暂无要闻</div>'
    main_panels.append('<div class="cat-panel active" id="cat-panel-all">' + ("".join(all_items_html) if all_items_html else empty_panel_html) + '</div>')

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
<title>国内新闻看板 · 中国国内重要政治动向（近 7 天）</title>
<style>
  :root {{
    --font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    --bg: #f4f5f7;
    --bg-soft: #f8f9fb;
    --panel: #fff;
    --line: #e4e7ee;
    --line-soft: #f0f2f6;
    --ink: #1c2434;
    --muted: #64707f;
    --muted-soft: #8a96a8;
    --main: #1e40af;
    --main-dark: #1e3a8a;
    --main-2: #2563eb;
    --main-soft: #eff4ff;
    --blue-grad-1: #1e3a8a;
    --blue-grad-2: #1e40af;
    --blue-grad-3: #2563eb;
    --today: #fbbf24;
    --today-bg: #fef3c7;
    --today-text: #92400e;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: var(--font); background: var(--bg); color: var(--ink); line-height: 1.65; }}
  .wrap {{ max-width: 1280px; margin: 0 auto; padding: 16px 16px 60px; }}

  /* 顶栏 */
  header.hero {{ background: linear-gradient(135deg, var(--blue-grad-1) 0%, var(--blue-grad-2) 55%, var(--blue-grad-3) 100%); color: #fff; border-radius: 14px; padding: 22px 28px 18px; box-shadow: 0 8px 22px rgba(30,58,138,.18); position: relative; overflow: hidden; }}
  header.hero::after {{ content: ""; position: absolute; right: -60px; top: -60px; width: 220px; height: 220px; border-radius: 50%; background: rgba(255,255,255,.06); }}
  .hero-back {{ display: flex; align-items: center; gap: 8px; font-size: 12.5px; margin-bottom: 12px; position: relative; z-index: 1; flex-wrap: wrap; }}
  .hero-back a {{ color: #fff; text-decoration: none; background: rgba(255,255,255,.16); padding: 4px 12px; border-radius: 999px; font-weight: 600; transition: background .15s; }}
  .hero-back a:hover {{ background: rgba(255,255,255,.3); }}
  .hero-back-sep {{ opacity: .6; }}
  .hero-back-cur {{ background: rgba(255,255,255,.1); padding: 4px 12px; border-radius: 999px; }}
  .hero h1 {{ font-size: 21px; font-weight: 700; letter-spacing: .5px; }}
  .hero .sub {{ font-size: 12.5px; opacity: .88; margin-top: 5px; }}
  .hero .hero-meta {{ display: flex; gap: 10px; margin-top: 13px; flex-wrap: wrap; font-size: 12px; position: relative; z-index: 1; }}
  .hero .hero-meta span {{ background: rgba(255,255,255,.15); padding: 3px 11px; border-radius: 999px; }}

  /* 刷新条（绿）+ KPI 网格 */
  .refresh-strip {{ background: #e8f7ee; border: 1px solid #bfe6cd; color: #1d7a46; border-radius: 10px; padding: 9px 16px; font-size: 12.5px; margin: 14px 0; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .rs-dot {{ width: 8px; height: 8px; border-radius: 50%; background: #22a35e; box-shadow: 0 0 0 3px rgba(34,163,94,.18); }}

  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 18px; }}
  .kpi-card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; }}
  .kpi-num {{ font-size: 24px; font-weight: 800; }}
  .kpi-main .kpi-num {{ color: var(--main); }}
  .kpi-label {{ font-size: 11.5px; color: var(--muted); margin-top: 2px; }}

  /* ============== 主布局：sidebar + content ============== */
  .layout {{ display: grid; grid-template-columns: 240px 1fr; gap: 16px; align-items: start; }}

  /* 左侧 sidebar（sticky 悬浮） */
  .sidebar {{
    position: sticky;
    top: 16px;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 10px;
    max-height: calc(100vh - 32px);
    overflow-y: auto;
    box-shadow: 0 4px 14px rgba(28,36,52,.05);
  }}
  .sidebar-title {{ font-size: 11px; font-weight: 700; letter-spacing: 1.2px; color: var(--muted-soft); text-transform: uppercase; padding: 8px 10px 10px; display: flex; align-items: center; gap: 6px; }}
  .sidebar-title::after {{ content: ""; flex: 1; height: 1px; background: var(--line-soft); }}
  .col-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 10px 12px;
    margin-bottom: 4px;
    border-radius: 10px;
    border: 1px solid transparent;
    background: transparent;
    color: var(--ink);
    font-size: 13.5px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all .15s ease-out;
    text-align: left;
  }}
  .col-item:hover {{ background: var(--main-soft); color: var(--main); border-color: var(--main-soft); }}
  .col-item:active {{ transform: scale(0.98); }}
  .col-item.active {{
    background: linear-gradient(135deg, var(--main-dark), var(--main-2));
    color: #fff;
    box-shadow: 0 4px 14px rgba(30,64,175,.25);
  }}
  .col-item .ic {{ font-size: 16px; line-height: 1; }}
  .col-item .cnt {{
    margin-left: auto;
    font-family: ui-monospace, monospace;
    font-size: 11px;
    background: rgba(142,160,191,.18);
    padding: 2px 8px;
    border-radius: 99px;
    color: var(--muted);
    font-weight: 700;
  }}
  .col-item.active .cnt {{ background: rgba(255,255,255,.22); color: #fff; }}

  /* 右侧主内容 */
  .main-content {{ min-width: 0; }}
  .cat-panel {{ display: none; }}
  .cat-panel.active {{ display: block; }}

  /* 日期分组表头 */
  .date-group-header {{
    background: linear-gradient(90deg, var(--main-soft), transparent);
    border-left: 4px solid var(--main);
    padding: 9px 14px 9px 16px;
    margin: 18px 0 10px;
    font-size: 13.5px;
    font-weight: 700;
    color: var(--main-dark);
    border-radius: 0 8px 8px 0;
    letter-spacing: 0.3px;
    display: flex; align-items: center; gap: 10px;
  }}
  .date-group-header:first-child {{ margin-top: 0; }}
  .date-group-header.today {{ background: linear-gradient(90deg, var(--today-bg), transparent); border-left-color: var(--today); color: var(--today-text); }}
  .date-group-header .date-count {{ font-family: ui-monospace, monospace; font-size: 11.5px; color: var(--muted); background: var(--panel); padding: 2px 9px; border-radius: 99px; font-weight: 600; }}
  .date-group-header.today .date-count {{ background: var(--today); color: #fff; }}

  /* 卡片（增强样式 + 醒目时间徽章） */
  .card {{ display: flex; gap: 12px; background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 13px 14px; margin-bottom: 10px; transition: transform .15s, box-shadow .15s; align-items: flex-start; }}
  .card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(28,36,52,.08); }}
  .card.imp-summit {{ border-left: 4px solid #c9a227; background: linear-gradient(90deg, #fdfaf0, var(--panel)); }}
  .card.imp-high {{ border-left: 4px solid var(--main); }}
  .card-idx {{ flex: 0 0 26px; height: 26px; border-radius: 8px; background: #f1f3f8; color: var(--muted); font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; }}
  .card-body {{ flex: 1; min-width: 0; }}
  .card-title-row {{ display: flex; gap: 12px; align-items: flex-start; justify-content: space-between; }}
  .card-title {{ font-size: 14.5px; font-weight: 650; line-height: 1.5; flex: 1; min-width: 0; }}
  .card-meta-right {{ display: flex; flex-direction: column; gap: 6px; align-items: flex-end; flex-shrink: 0; }}

  /* ⭐ 醒目时间徽章 */
  .date-badge {{
    font-family: ui-monospace, monospace;
    font-size: 12.5px;
    font-weight: 700;
    color: var(--main-dark);
    background: var(--main-soft);
    padding: 5px 12px;
    border-radius: 8px;
    border: 1px solid rgba(30,64,175,.18);
    white-space: nowrap;
    letter-spacing: 0.3px;
  }}
  .date-badge.today {{
    background: var(--today);
    color: #fff;
    border-color: var(--today);
    box-shadow: 0 0 0 2px rgba(251,191,36,.2);
  }}

  .card-link {{ font-size: 12px; color: var(--main); text-decoration: none; font-weight: 600; padding: 4px 11px; border: 1px solid var(--main); border-radius: 8px; transition: all .15s; white-space: nowrap; }}
  .card-link:hover {{ background: var(--main); color: #fff; }}

  .card-summary {{ font-size: 12.5px; color: #4a5568; line-height: 1.65; margin-top: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
  .card-meta {{ display: flex; gap: 10px; margin-top: 6px; flex-wrap: wrap; align-items: center; }}
  .meta-cat {{ font-size: 11.5px; color: var(--main); background: var(--main-soft); padding: 2px 9px; border-radius: 999px; font-weight: 600; }}
  .meta-src {{ font-size: 11.5px; color: var(--muted); }}
  .meta-imp {{ font-size: 11.5px; color: var(--muted-soft); font-family: ui-monospace, monospace; }}
  .tag-today {{ background: var(--today); color: #fff; font-size: 10.5px; padding: 2px 8px; border-radius: 999px; margin-left: 6px; vertical-align: 1px; font-weight: 600; }}

  .empty-panel {{ text-align: center; color: var(--muted); padding: 60px 0; font-size: 13px; }}

  /* 响应式：移动端 sidebar 转顶横排 */
  @media (max-width: 880px) {{
    .layout {{ grid-template-columns: 1fr; }}
    .sidebar {{ position: static; max-height: none; }}
    .col-item {{
      display: inline-flex;
      width: auto;
      margin-bottom: 0;
      margin-right: 6px;
      padding: 8px 12px;
      font-size: 12.5px;
    }}
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
      <a href="https://iranorawahaha.github.io/international-news-kb/ai-company-intel.html" target="_blank" rel="noopener noreferrer">🤖 AI 动向看板</a>
      <span class="hero-back-sep">|</span>
      <span class="hero-back-cur">🇨🇳 国内新闻看板</span>
    </div>
    <h1>国内新闻看板 · 中国国内重要政治动向</h1>
    <p class="sub">信源：中国政府网要闻 + 最新政策 + 央视新闻 + 人民日报 + 外交部官网 + 商务部/发改委/网信办官网（国家级权威信源）· 聚焦元首动态、高层动态、使领馆动向、重要会议、人事任免、部委动态、政策发布、经贸动向 · Ira 信息看板 · 仅供参考交流</p>
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
    <b>今日新增 {today_new} 条</b> ·
    数据快照，滚动 7 天窗口
  </div>

  <div class="kpi-grid">
    <div class="kpi-card" style="border-left:4px solid #22a35e; background:linear-gradient(180deg,#f0fdf4,#fff);"><div class="kpi-num" style="color:#16a34a;">{today_new}</div><div class="kpi-label">🆕 今日新增</div></div>
    <div class="kpi-card kpi-main"><div class="kpi-num">{total}</div><div class="kpi-label">要闻总数（去重后）</div></div>
    <div class="kpi-card"><div class="kpi-num">{summit_count}</div><div class="kpi-label">⭐ 元首级要闻</div></div>
    <div class="kpi-card"><div class="kpi-num">{len(dates)}</div><div class="kpi-label">覆盖天数</div></div>
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
    colItems.forEach(function(item) {{
      item.addEventListener('click', function() {{
        // 切换 active
        colItems.forEach(function(x) {{ x.classList.remove('active'); }});
        item.classList.add('active');
        // 切换面板
        var cat = item.dataset.cat;
        document.querySelectorAll('.cat-panel').forEach(function(p) {{ p.classList.remove('active'); }});
        var panel = document.getElementById('cat-panel-' + (cat === 'all' ? 'all' : cat));
        if (panel) panel.classList.add('active');
      }});
    }});
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