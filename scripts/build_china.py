#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_china.py — 国内新闻看板 单文件 HTML 构建器（Ira 信息看板体系）

读取 data/china-news.json，生成 china-news.html（单文件，纯内联 CSS/JS，无外部资源）。
视觉与 AI 动向看板统一（政务深红风格 + 统一 IRA-NAV 导航）。
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

    cat_order = ["元首动态", "常委动态", "重要会议", "人事任免", "政策发布", "其他"]
    cat_map_zh = {"元首动态": "元首动态", "常委动态": "常委动态", "重要会议": "重要会议",
                  "人事任免": "人事任免", "政策发布": "政策发布", "其他": "其他"}

    def cat_icon(c):
        return {"元首动态": "👑", "常委动态": "🧭", "重要会议": "🏛", "人事任免": "📋", "政策发布": "📜", "其他": "📌"}.get(c, "📌")

    # 生成卡片 HTML
    def article_card(it, idx):
        title = esc(it.get("title", ""))
        url = esc(it.get("url", "#"))
        src = esc(it.get("source", ""))
        cat = it.get("category", "其他")
        score = it.get("priority_score", 0)
        summit = "⭐" if it.get("is_summit_level") else ""
        today_mark = '<span class="tag-today">🆕 今日</span>' if it.get("date") == today else ""
        # 高分色
        if score >= 95:
            cls = "imp-summit"
        elif score >= 85:
            cls = "imp-high"
        else:
            cls = ""
        return f'''<div class="card {cls}">
          <div class="card-idx">{idx}</div>
          <div class="card-body">
            <h3 class="card-title">{summit}{title}{today_mark}</h3>
            <div class="card-meta">
              <span class="meta-cat">{cat_icon(cat)} {cat}</span>
              <span class="meta-src">来源：{src}</span>
            </div>
          </div>
          <a class="card-link" href="{url}" target="_blank" rel="noopener noreferrer">原文 ↗</a>
        </div>'''

    # 生成分类 tab 面板
    tabs = []
    panels = []
    for c in cat_order:
        cnt = per_cat.get(c, 0)
        active = " active" if c == "其他" else ""
        tabs.append(f'<button class="tab{active}" data-cat="{c}">{cat_icon(c)} {cat_map_zh[c]}（{cnt}）</button>')
        items = []
        idx = 0
        for d in dates:
            for it in archive.get(d, []):
                if it.get("category") == c:
                    idx += 1
                    items.append(article_card(it, idx))
        panel_cls = "tab-panel " + ("active" if c == "其他" else "")
        panels.append(f'<div class="{panel_cls}" id="panel-{c}">{"".join(items) if items else f"<div class=\"empty-panel\">暂无{c}类新闻</div>"}</div>')

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
    --bg: #f4f5f7; --panel: #fff; --line: #e4e7ee; --ink: #1c2434; --muted: #64707f;
    --main: #8a1f1f; --main-dark: #6e1414; --main-soft: #fdf0ef;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: var(--font); background: var(--bg); color: var(--ink); line-height: 1.65; }}
  .wrap {{ max-width: 1120px; margin: 0 auto; padding: 20px 16px 60px; }}

  /* 顶栏 */
  header.hero {{ background: linear-gradient(135deg, #6e1414 0%, #8a1f1f 55%, #b04a42 100%); color: #fff; border-radius: 14px; padding: 24px 26px 20px; box-shadow: 0 8px 22px rgba(110,20,20,.18); position: relative; overflow: hidden; }}
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

  /* 刷新条 */
  .refresh-strip {{ background: #e8f7ee; border: 1px solid #bfe6cd; color: #1d7a46; border-radius: 10px; padding: 9px 16px; font-size: 12.5px; margin: 14px 0; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .rs-dot {{ width: 8px; height: 8px; border-radius: 50%; background: #22a35e; box-shadow: 0 0 0 3px rgba(34,163,94,.18); }}

  /* 说明条 */
  .tip-strip {{ background: var(--panel); border: 1px solid var(--line); border-left: 4px solid var(--main); border-radius: 10px; padding: 10px 16px; font-size: 12.5px; color: var(--muted); margin-bottom: 16px; }}

  /* KPI */
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 18px; }}
  .kpi-card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; }}
  .kpi-num {{ font-size: 24px; font-weight: 800; }}
  .kpi-main .kpi-num {{ color: var(--main); }}
  .kpi-label {{ font-size: 11.5px; color: var(--muted); margin-top: 2px; }}

  /* 分类 tab */
  .tabbar {{ position: sticky; top: 0; z-index: 50; background: rgba(244,245,247,.92); backdrop-filter: blur(8px); padding: 10px 0 8px; margin-bottom: 14px; }}
  .tabbar-inner {{ display: flex; gap: 8px; overflow-x: auto; scrollbar-width: none; }}
  .tabbar-inner::-webkit-scrollbar {{ display: none; }}
  .tab {{ flex: 0 0 auto; display: inline-flex; align-items: center; gap: 6px; border: 1px solid var(--line); background: var(--panel); color: var(--ink); font-size: 13px; font-weight: 600; padding: 9px 14px; border-radius: 999px; cursor: pointer; transition: all .15s; font-family: inherit; }}
  .tab.active {{ background: var(--main); border-color: var(--main); color: #fff; }}
  .tab:hover {{ border-color: var(--main); }}

  /* 面板 */
  .tab-panel {{ display: none; }}
  .tab-panel.active {{ display: block; }}
  .empty-panel {{ text-align: center; color: var(--muted); padding: 40px 0; font-size: 13px; }}

  /* 卡片 */
  .card {{ display: flex; gap: 12px; background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; margin-bottom: 10px; transition: transform .15s, box-shadow .15s; align-items: center; }}
  .card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(28,36,52,.08); }}
  .card.imp-summit {{ border-left: 4px solid #c9a227; background: linear-gradient(90deg, #fdfaf0, var(--panel)); }}
  .card.imp-high {{ border-left: 4px solid var(--main); }}
  .card-idx {{ flex: 0 0 26px; height: 26px; border-radius: 8px; background: #f1f3f8; color: var(--muted); font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; }}
  .card-body {{ flex: 1; min-width: 0; }}
  .card-title {{ font-size: 14.5px; font-weight: 650; line-height: 1.5; }}
  .card-meta {{ display: flex; gap: 10px; margin-top: 6px; flex-wrap: wrap; }}
  .meta-cat {{ font-size: 11.5px; color: var(--main); background: var(--main-soft); padding: 2px 9px; border-radius: 999px; font-weight: 600; }}
  .meta-src {{ font-size: 11.5px; color: var(--muted); }}
  .card-link {{ flex: 0 0 auto; font-size: 12px; color: var(--main); text-decoration: none; font-weight: 600; padding: 5px 12px; border: 1px solid var(--main); border-radius: 8px; transition: all .15s; }}
  .card-link:hover {{ background: var(--main); color: #fff; }}
  .tag-today {{ background: #22a35e; color: #fff; font-size: 10.5px; padding: 1px 7px; border-radius: 999px; margin-left: 6px; vertical-align: 1px; }}

  @media (max-width: 720px) {{
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
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
    <p class="sub">信源：中国政府网要闻 + 最新政策（国家级权威信源）· 聚焦元首及政治局常委动态、重要会议、人事任免、政策发布 · Ira 信息看板 · 仅供参考交流</p>
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

  <div class="tip-strip">💡 <b>数据源说明：</b>全部来自中国政府网（gov.cn）官方要闻与最新政策频道，已过滤营销号/文娱/小道消息等非权威内容。⭐ 为元首级（习近平/国家主席/中央军委相关），高亮卡片为高分要闻。</div>

  <div class="kpi-grid">
    <div class="kpi-card kpi-main"><div class="kpi-num">{total}</div><div class="kpi-label">要闻总数（去重后）</div></div>
    <div class="kpi-card"><div class="kpi-num">{summit_count}</div><div class="kpi-label">⭐ 元首级要闻</div></div>
    <div class="kpi-card"><div class="kpi-num">{today_new}</div><div class="kpi-label">今日新增</div></div>
    <div class="kpi-card"><div class="kpi-num">{len(dates)}</div><div class="kpi-label">覆盖天数</div></div>
  </div>

  <div class="tabbar"><div class="tabbar-inner">{''.join(tabs)}</div></div>

  {''.join(panels)}

</div>
<script>
  (function() {{
    var tabs = document.querySelectorAll('.tab');
    tabs.forEach(function(t) {{
      t.addEventListener('click', function() {{
        tabs.forEach(function(x) {{ x.classList.remove('active'); }});
        t.classList.add('active');
        var panels = document.querySelectorAll('.tab-panel');
        panels.forEach(function(p) {{ p.classList.remove('active'); }});
        var panel = document.getElementById('panel-' + t.getAttribute('data-cat'));
        if (panel) panel.classList.add('active');
      }});
    }});
  }})();
</script>
</body>
</html>'''

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)

    # JS 语法自检（防空白事故）
    import subprocess as sp
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

    print(f"=== 国内新闻看板 ===")
    print(f"总条数: {total} | 分类: {per_cat}")
    print(f"written: {OUT_HTML} {len(doc)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(build())
