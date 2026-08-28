#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_diplomatic.py — 使领馆事务看板 单文件 HTML 构建器 v1.0（Ira 信息看板体系）

视觉规范：
- 浅色底 + 青绿色（teal）主色调（#0d9488），区别于国际蓝/国内红/AI琥珀
- 顶部蓝色 Header（统一Ira体系导航）+ 模块化简报内容
- "有则展示、无则省略"原则：空模块完全不渲染
- 事件卡格式严格遵循规格文档

读取 data/diplomatic-affairs.json，生成 diplomatic-affairs.html（单文件，纯内联 CSS/JS，无外部资源）。
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
DATA_FILE = os.path.join(BASE_DIR, "data", "diplomatic-affairs.json")
OUT_HTML = os.path.join(BASE_DIR, "diplomatic-affairs.html")

# ⚠️ 不可靠信源黑名单（2026-08-28 用户确认剔除）
# hongkongdaily.net：香港新闻网，曾返回不真实新闻（如"外交部美大司吹风会沙利文访华"假报道）
SOURCE_BLACKLIST = [
    "hongkongdaily.net",
    "gzylhyzx.com",          # 可疑仿冒聚合站
    "wx.laserfair.com",      # 激光展会站转载央视（非官方）
    "toutiao.com",           # 头条号转载（非一手）
]


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def filter_sources(sources):
    """剔除黑名单信源（不可靠源不放上看板）"""
    if not sources:
        return []
    out = []
    for s in sources:
        u = (s.get("url") or "").lower()
        if any(b in u for b in SOURCE_BLACKLIST):
            print(f"    🗑️ 黑名单信源剔除: {s.get('title','')[:40]} | {u[:70]}")
            continue
        out.append(s)
    return out


def sort_items_by_date(items):
    """每个小版面（模块）内按 event_date 降序排列（新→旧）；缺失日期的条目排最后。

    event_date 为 ISO 格式 YYYY-MM-DD，字符串降序排序即时间降序。
    """
    def key(it):
        ed = (it.get("event_date") or "").strip()
        return (ed == "", ed)  # 无日期 → (True,...) 排后；有日期 → (False, 日期) 按字符串降序
    return sorted(items, key=key, reverse=True)


# 事件时间阶段：区分「预告 / 进行中 / 已发生」，避免预告与已发生混淆
PHASE_MAP = {
    "upcoming": ("📅 预告", "upcoming"),
    "ongoing": ("🟢 进行中", "ongoing"),
    "completed": ("✅ 已发生", "completed"),
}


def phase_badge(phase):
    label, cls = PHASE_MAP.get(phase, ("✅ 已发生", "completed"))
    return f'<span class="ev-badge {cls}">{label}</span>'


# ============== 模块渲染 ==============

def render_personnel(items, module_title="外交代表人事变化"):
    """渲染大使/外交代表人事变化模块"""
    if not items:
        return ""
    cards = []
    for it in items:
        country = esc(it.get("country", ""))
        event_type = esc(it.get("event_type", ""))
        status = esc(it.get("current_status", ""))
        date = esc(it.get("event_date", ""))
        person = esc(it.get("person_name", "") or "")
        desc = esc(it.get("description", ""))
        sources = filter_sources(it.get("sources", []))
        confirmed = it.get("confirmed", True)
        phase = it.get("phase", "completed")
        
        confirm_badge = '<span class="ev-badge confirmed">✓ 已确认</span>' if confirmed else '<span class="ev-badge unconfirmed">⚠ 待核实</span>'
        phase_html = phase_badge(phase)
        person_line = f'<span class="ev-person">{person}</span>' if person else ""
        
        src_html = ""
        if sources:
            src_links = []
            for s in sources[:3]:
                stitle = esc(s.get("title", "来源"))
                surl = esc(s.get("url", "#"))
                src_links.append(f'<a href="{surl}" target="_blank" rel="noopener noreferrer">{stitle}</a>')
            src_html = '<div class="ev-sources">📎 ' + " · ".join(src_links) + '</div>'
        
        cards.append(f'''<div class="event-card">
          <div class="ev-header">
            <span class="ev-country">{country}</span>
            <span class="ev-divider">｜</span>
            <span class="ev-type">{event_type}</span>
            {phase_html}
            {confirm_badge}
          </div>
          <div class="ev-status">当前状态：<b>{status}</b> · 日期：{date}</div>
          {person_line}
          <p class="ev-desc">{desc}</p>
          {src_html}
        </div>''')
    
    return f'''<section class="module" id="mod-personnel">
      <h2 class="module-title">🌐 {module_title}<span class="mod-count">{len(items)} 项</span></h2>
      {"".join(cards)}
    </section>'''


def render_consuls(items, module_title="驻上海、驻广州总领事人事"):
    """渲染总领事人事变化"""
    if not items:
        return ""
    cards = []
    for it in items:
        country = esc(it.get("country", ""))
        post = esc(it.get("post", ""))  # 上海 or 广州
        event_type = esc(it.get("event_type", ""))
        status = esc(it.get("current_status", ""))
        date = esc(it.get("event_date", ""))
        person = esc(it.get("person_name", "") or "")
        desc = esc(it.get("description", ""))
        sources = filter_sources(it.get("sources", []))
        confirmed = it.get("confirmed", True)
        
        confirm_badge = '<span class="ev-badge confirmed">✓ 已确认</span>' if confirmed else '<span class="ev-badge unconfirmed">⚠ 待核实</span>'
        person_line = f'<span class="ev-person">{person}</span>' if person else ""
        
        src_html = ""
        if sources:
            src_links = []
            for s in sources[:3]:
                stitle = esc(s.get("title", "来源"))
                surl = esc(s.get("url", "#"))
                src_links.append(f'<a href="{surl}" target="_blank" rel="noopener noreferrer">{stitle}</a>')
            src_html = '<div class="ev-sources">📎 ' + " · ".join(src_links) + '</div>'
        
        cards.append(f'''<div class="event-card">
          <div class="ev-header">
            <span class="ev-country">{country}</span>
            <span class="ev-post-badge">驻{post}</span>
            <span class="ev-divider">｜</span>
            <span class="ev-type">{event_type}</span>
            {confirm_badge}
          </div>
          <div class="ev-status">当前状态：<b>{status}</b> · 日期：{date}</div>
          {person_line}
          <p class="ev-desc">{desc}</p>
          {src_html}
        </div>''')
    
    return f'''<section class="module" id="mod-consuls">
      <h2 class="module-title">🏢 {module_title}<span class="mod-count">{len(items)} 项</span></h2>
      {"".join(cards)}
    </section>'''


def render_visits(items, module_title="外国重要高级官员访华"):
    """渲染高级官员访华模块"""
    if not items:
        return ""
    cards = []
    for it in items:
        country = esc(it.get("country", ""))
        person = esc(it.get("person_name", ""))
        position = esc(it.get("position", ""))
        visit_date = esc(it.get("event_date", ""))
        desc = esc(it.get("description", ""))
        ambassador = esc(it.get("ambassador_participation", "") or "")
        outcomes = esc(it.get("outcomes", "") or "")
        sources = filter_sources(it.get("sources", []))
        confirmed = it.get("confirmed", True)
        phase = it.get("phase", "completed")
        
        confirm_badge = '<span class="ev-badge confirmed">✓ 已确认</span>' if confirmed else '<span class="ev-badge unconfirmed">⚠ 待核实</span>'
        phase_html = phase_badge(phase)
        
        ambassador_html = ""
        if ambassador:
            amb_class = "amb-confirmed" if "已确认" in ambassador else "amb-unknown"
            ambassador_html = f'<div class="ev-ambassador {amb_class}">🎯 驻华大使参与：{ambassador}</div>'
        
        outcomes_html = ""
        if outcomes:
            outcomes_html = f'<div class="ev-outcomes">📋 官方明确成果：{outcomes}</div>'
        
        src_html = ""
        if sources:
            src_links = []
            for s in sources[:3]:
                stitle = esc(s.get("title", "来源"))
                surl = esc(s.get("url", "#"))
                src_links.append(f'<a href="{surl}" target="_blank" rel="noopener noreferrer">{stitle}</a>')
            src_html = '<div class="ev-sources">📎 ' + " · ".join(src_links) + '</div>'
        
        cards.append(f'''<div class="event-card visit-card">
          <div class="ev-header">
            <span class="ev-country">{country}</span>
            <span class="ev-divider">｜</span>
            <span class="ev-person-title">{person} · {position}</span>
            {phase_html}
            {confirm_badge}
          </div>
          <div class="ev-status">日期：{visit_date}</div>
          <p class="ev-desc">{desc}</p>
          {ambassador_html}
          {outcomes_html}
          {src_html}
        </div>''')
    
    return f'''<section class="module" id="mod-visits">
      <h2 class="module-title">✈️ {module_title}<span class="mod-count">{len(items)} 项</span></h2>
      {"".join(cards)}
    </section>'''


def render_us_china(items, module_title="中美高级官员互动"):
    """渲染中美互动模块"""
    if not items:
        return ""
    cards = []
    for it in items:
        cn_person = esc(it.get("cn_person", ""))
        us_person = esc(it.get("us_person", ""))
        interaction_type = esc(it.get("interaction_type", ""))
        date = esc(it.get("event_date", ""))
        desc = esc(it.get("description", ""))
        mutual = it.get("mutual_confirmed", False)
        cn_emphasis = esc(it.get("cn_emphasis", "") or "")
        us_emphasis = esc(it.get("us_emphasis", "") or "")
        outcomes = esc(it.get("outcomes", "") or "")
        sources = filter_sources(it.get("sources", []))
        
        mutual_label = "双方共同确认" if mutual else "单方发布"
        mutual_class = "mutual" if mutual else "unilateral"
        
        cn_html = f'<div class="ev-stance"><span class="stake-label cn">中方重点</span>{cn_emphasis}</div>' if cn_emphasis else ""
        us_html = f'<div class="ev-stance"><span class="stake-label us">美方重点</span>{us_emphasis}</div>' if us_emphasis else ""
        
        outcomes_html = ""
        if outcomes:
            outcomes_html = f'<div class="ev-outcomes">📋 官方明确结果：{outcomes}</div>'
        
        src_html = ""
        if sources:
            src_links = []
            for s in sources[:4]:
                stitle = esc(s.get("title", "来源"))
                surl = esc(s.get("url", "#"))
                src_links.append(f'<a href="{surl}" target="_blank" rel="noopener noreferrer">{stitle}</a>')
            src_html = '<div class="ev-sources">📎 ' + " · ".join(src_links) + '</div>'
        
        cards.append(f'''<div class="event-card uscn-card">
          <div class="ev-header">
            <span class="ev-cn-person">🇨🇳 {cn_person}</span>
            <span class="ev-vs">—</span>
            <span class="ev-us-person">🇺🇸 {us_person}</span>
            <span class="ev-divider">｜</span>
            <span class="ev-type">{interaction_type}</span>
            <span class="ev-badge {mutual_class}">{mutual_label}</span>
          </div>
          <div class="ev-status">日期：{date}</div>
          <p class="ev-desc">{desc}</p>
          {cn_html}
          {us_html}
          {outcomes_html}
          {src_html}
        </div>''')
    
    return f'''<section class="module" id="mod-uscn">
      <h2 class="module-title">🇨🇳🇺🇸 {module_title}<span class="mod-count">{len(items)} 项</span></h2>
      {"".join(cards)}
    </section>'''


def render_highlights(items):
    """渲染本期重点"""
    if not items:
        return ""
    lines = []
    for i, h in enumerate(items[:3], 1):
        lines.append(f'<li><b>#{i}</b> {esc(h)}</li>')
    return f'''<section class="highlights">
      <h2>📌 本期重点</h2>
      <ul>{"".join(lines)}</ul>
    </section>'''


def render_data_summary(summary):
    """渲染简要数据"""
    if not summary:
        return ""
    parts = []
    for k, v in summary.items():
        if v:
            parts.append(f'{esc(k)}：{esc(str(v))}')
    if not parts:
        return ""
    return f'<section class="data-summary"><span>📊</span> {"｜".join(parts)}</section>'


def render_supplementary(notes):
    """渲染补充观察"""
    if not notes:
        return ""
    lines = []
    for n in notes[:3]:
        lines.append(f'<li>{esc(n)}</li>')
    return f'''<section class="supplementary">
      <h2>🔍 补充观察</h2>
      <ul>{"".join(lines)}</ul>
    </section>'''


# ============== 主构建函数 ==============

def build():
    if not os.path.exists(DATA_FILE):
        # 无数据文件时生成空状态页面
        return build_empty()

    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("meta", {})
    modules = data.get("modules", {})
    highlights = data.get("highlights", [])
    data_summary = data.get("data_summary", {})
    supplementary = data.get("supplementary_notes", [])
    
    window_start = meta.get("window_start", NOW.strftime("%Y-%m-%d"))
    window_end = meta.get("window_end", NOW.strftime("%Y-%m-%d"))
    generated = meta.get("generated", NOW.strftime("%Y-%m-%d %H:%M"))
    version = meta.get("version", "1.0.0")
    
    # 判断是否为多日窗口
    is_multi_day = (window_start != window_end)
    highlight_label = "本期重点" if is_multi_day else "今日重点"
    title_suffix = f"{window_start}—{window_end}" if is_multi_day else window_end
    
    # 决定标题标签
    if is_multi_day:
        date_label = f"覆盖时间：{window_start} — {window_end}（北京时间）"
    else:
        date_label = f"日期：{window_end}"

    # 渲染各模块（每个小版面内按 event_date 降序：日期近的排前面）
    mod_personnel = render_personnel(sort_items_by_date(modules.get("personnel", {}).get("items", [])))
    mod_consuls = render_consuls(sort_items_by_date(modules.get("consuls", {}).get("items", [])))
    mod_visits = render_visits(sort_items_by_date(modules.get("visits", {}).get("items", [])))
    mod_uscn = render_us_china(sort_items_by_date(modules.get("us_china", {}).get("items", [])))
    
    # 计算是否有任何模块有内容
    all_modules_html = mod_personnel + mod_consuls + mod_visits + mod_uscn
    has_content = bool(all_modules_html.strip())
    
    # 渲染辅助区块
    highlights_html = render_highlights(highlights)
    summary_html = render_data_summary(data_summary)
    supp_html = render_supplementary(supplementary)
    
    # 如果窗口是多日，调整highlights的标签
    if is_multi_day and highlights_html:
        highlights_html = highlights_html.replace("📌 本期重点", f"📌 {highlight_label}")
    
    if not has_content:
        # 完全没有符合条件的事件
        body = '<div class="empty-state">本期时间窗口内无符合收录标准的事件。</div>'
    else:
        body = highlights_html + summary_html + all_modules_html + supp_html
    
    # 免责声明
    disclaimer = ("本摘要基于合法公开、可回溯的信息来源整理，部分内容由人工智能辅助生成，"
                  "仅供个人学习、研究及固定小范围交流参考，不构成新闻发布、专业意见或对事实完整性的保证。"
                  "摘要不包含非公开信息、内部材料或未经合法授权获取的内容。"
                  "人物姓名译法、职务、事件状态、会谈议题及具体成果，请以相关机构最新官方原文为准。"
                  "未经重新进行合规评估，不应将本摘要用于面向不特定公众的发布、公开订阅或商业传播。")

    doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>使领馆事务看板 · Ira 信息看板</title>
<style>
  :root {{
    --font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Microsoft YaHei", sans-serif;
    --bg: #f6f9f8;
    --panel: #ffffff;
    --line: #e2e8e7;
    --line-soft: #eef2f1;
    --ink: #1e293b;
    --muted: #64748b;
    --muted-soft: #94a3b8;
    /* Teal 青绿色系 */
    --teal: #0d9488;
    --teal-dark: #0f766e;
    --teal-light: #14b8a6;
    --teal-soft: #f0fdfa;
    --teal-border: #99f6e4;
    --teal-grad-1: #0f766e;
    --teal-grad-2: #0d9488;
    --teal-grad-3: #14b8a6;
    /* 辅助色 */
    --gold: #f59e0b;
    --gold-bg: #fffbeb;
    --red: #ef4444;
    --red-soft: #fef2f2;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font);
    background: var(--bg);
    color: var(--ink);
    line-height: 1.7;
    min-height: 100vh;
    background-image:
      radial-gradient(500px 300px at 85% 5%, rgba(13,148,136,.04), transparent),
      radial-gradient(400px 250px at 5% 90%, rgba(15,118,110,.03), transparent);
  }}
  .wrap {{ max-width: 1100px; margin: 0 auto; padding: 16px 20px 60px; }}

  /* ===== 顶部青绿 Header（Ira体系统一） ===== */
  header.hero {{
    background: linear-gradient(135deg, #0f766e 0%, #0d9488 50%, #14b8a6 100%);
    color: #fff;
    border-radius: 16px;
    padding: 24px 32px 22px;
    box-shadow: 0 8px 24px rgba(15,118,110,.3);
    position: relative;
    overflow: hidden;
    margin-bottom: 20px;
  }}
  header.hero::after {{
    content: "";
    position: absolute;
    right: -60px; top: -60px;
    width: 260px; height: 260px;
    border-radius: 50%;
    background: rgba(255,255,255,.06);
  }}
  .hero-nav {{
    display: flex; gap: 8px; flex-wrap: wrap;
    margin-bottom: 14px; position: relative; z-index: 1;
  }}
  .hero-nav a {{
    padding: 5px 14px; border-radius: 99px;
    background: rgba(255,255,255,.12);
    color: rgba(255,255,255,.85);
    text-decoration: none; font-size: 13px; font-weight: 500;
    transition: all .15s;
  }}
  .hero-nav a:hover {{ background: rgba(255,255,255,.22); color: #fff; }}
  .hero-nav a.active {{ background: #fff; color: #0f766e; font-weight: 700; }}
  .hero-nav-sep {{ opacity: .5; padding: 5px 2px; color: rgba(255,255,255,.6); }}
  .hero h1 {{ font-size: 24px; font-weight: 800; letter-spacing: -.3px; position: relative; z-index: 1; }}
  .hero-meta {{
    display: flex; gap: 10px; margin-top: 13px; flex-wrap: wrap;
    font-size: 12.5px; position: relative; z-index: 1;
  }}
  .hero-meta span {{
    background: rgba(255,255,255,.15);
    padding: 4px 12px; border-radius: 99px;
  }}

  /* ===== 简报容器 ===== */
  .brief-container {{
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 28px 32px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04), 0 4px 16px rgba(0,0,0,.05);
    margin-bottom: 20px;
  }}
  .brief-header {{
    text-align: center;
    padding-bottom: 20px;
    margin-bottom: 24px;
    border-bottom: 2px solid var(--line-soft);
  }}
  .brief-header h1 {{
    font-size: 22px; font-weight: 800;
    color: var(--teal-dark); letter-spacing: .3px;
  }}
  .brief-header .brief-date {{
    font-size: 13px; color: var(--muted); margin-top: 6px;
  }}

  /* ===== 本期重点 ===== */
  .highlights {{
    background: linear-gradient(135deg, var(--teal-soft), #fff);
    border: 1px solid var(--teal-border);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 24px;
  }}
  .highlights h2 {{
    font-size: 14px; font-weight: 700; color: var(--teal-dark);
    margin-bottom: 10px;
  }}
  .highlights ul {{
    list-style: none; padding: 0;
  }}
  .highlights li {{
    font-size: 13.5px; color: var(--ink); padding: 4px 0;
    line-height: 1.6;
  }}
  .highlights li b {{ color: var(--teal); margin-right: 4px; }}

  /* ===== 简要数据 ===== */
  .data-summary {{
    font-size: 12.5px; color: var(--muted);
    background: #f8faf9;
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom: 20px;
    display: flex; align-items: center; gap: 8px;
    flex-wrap: wrap;
  }}

  /* ===== 模块 ===== */
  .module {{
    margin-bottom: 28px;
  }}
  .module:last-child {{ margin-bottom: 0; }}
  .module-title {{
    font-size: 17px; font-weight: 750;
    color: var(--ink);
    padding-bottom: 10px;
    margin-bottom: 14px;
    border-bottom: 2px solid var(--teal-border);
    display: flex; align-items: center; gap: 10px;
  }}
  .mod-count {{
    font-size: 12px; font-weight: 600;
    background: var(--teal-soft); color: var(--teal);
    padding: 2px 10px; border-radius: 99px;
    margin-left: auto;
  }}

  /* ===== 事件卡 ===== */
  .event-card {{
    background: var(--panel);
    border: 1px solid var(--line);
    border-left: 4px solid var(--teal);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 12px;
    transition: box-shadow .15s;
  }}
  .event-card:hover {{ box-shadow: 0 4px 12px rgba(13,148,136,.08); }}
  .event-card.visit-card {{ border-left-color: #6366f1; }}
  .event-card.uscn-card {{ border-left-color: #dc2626; }}

  .ev-header {{
    display: flex; align-items: center; gap: 8px;
    flex-wrap: wrap; margin-bottom: 6px;
  }}
  .ev-country {{
    font-size: 14px; font-weight: 700; color: var(--ink);
  }}
  .ev-post-badge {{
    font-size: 11px; font-weight: 600;
    background: var(--teal-soft); color: var(--teal);
    padding: 1px 8px; border-radius: 99px;
  }}
  .ev-type {{
    font-size: 13px; color: var(--teal-dark); font-weight: 600;
  }}
  .ev-person-title {{
    font-size: 13px; color: var(--ink); font-weight: 600;
  }}
  .ev-cn-person {{
    font-size: 13.5px; font-weight: 700; color: #dc2626;
  }}
  .ev-us-person {{
    font-size: 13.5px; font-weight: 700; color: #2563eb;
  }}
  .ev-vs {{
    color: var(--muted-soft); font-weight: 400;
  }}
  .ev-divider {{
    color: var(--muted-soft); font-size: 12px;
  }}
  .ev-badge {{
    font-size: 10.5px; font-weight: 600;
    padding: 2px 8px; border-radius: 99px;
  }}
  .ev-badge.confirmed {{
    background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0;
  }}
  .ev-badge.unconfirmed {{
    background: var(--red-soft); color: #dc2626; border: 1px solid #fecaca;
  }}
  .ev-badge.mutual {{
    background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe;
  }}
  .ev-badge.unilateral {{
    background: #fffbeb; color: #d97706; border: 1px solid #fde68a;
  }}
  .ev-badge.upcoming {{
    background: #fff7ed; color: #c2410c; border: 1px solid #fed7aa;
  }}
  .ev-badge.ongoing {{
    background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0;
  }}
  .ev-badge.completed {{
    background: #f0fdfa; color: #0f766e; border: 1px solid #99f6e4;
  }}

  .ev-status {{
    font-size: 12.5px; color: var(--muted);
    margin-bottom: 6px;
  }}
  .ev-status b {{ color: var(--teal-dark); }}
  .ev-person {{
    display: inline-block;
    font-size: 13px; font-weight: 600;
    background: #f1f5f9; color: var(--ink);
    padding: 3px 10px; border-radius: 6px;
    margin-bottom: 6px;
  }}
  .ev-desc {{
    font-size: 13.5px; color: var(--ink); line-height: 1.7;
    margin-bottom: 8px;
  }}
  .ev-ambassador {{
    font-size: 12.5px; padding: 6px 12px;
    border-radius: 8px; margin-bottom: 6px;
  }}
  .ev-ambassador.amb-confirmed {{
    background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0;
  }}
  .ev-ambassador.amb-unknown {{
    background: #f8fafc; color: var(--muted); border: 1px solid var(--line);
  }}
  .ev-outcomes {{
    font-size: 12.5px; padding: 6px 12px;
    background: #fffbeb; color: #92400e;
    border: 1px solid #fde68a; border-radius: 8px;
    margin-bottom: 6px;
  }}
  .ev-stance {{
    font-size: 12.5px; padding: 6px 12px;
    margin-bottom: 4px; border-radius: 8px;
    line-height: 1.6;
  }}
  .stake-label {{
    display: inline-block;
    font-size: 10.5px; font-weight: 700;
    padding: 1px 7px; border-radius: 99px;
    margin-right: 8px;
  }}
  .stake-label.cn {{
    background: #fef2f2; color: #dc2626; border: 1px solid #fecaca;
  }}
  .stake-label.us {{
    background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe;
  }}
  .ev-sources {{
    font-size: 12px; color: var(--muted);
    margin-top: 8px; padding-top: 8px;
    border-top: 1px dashed var(--line-soft);
  }}
  .ev-sources a {{
    color: var(--teal); text-decoration: none; font-weight: 600;
  }}
  .ev-sources a:hover {{ text-decoration: underline; }}

  /* ===== 补充观察 ===== */
  .supplementary {{
    margin-top: 28px; padding-top: 20px;
    border-top: 2px dashed var(--line);
  }}
  .supplementary h2 {{
    font-size: 14px; font-weight: 700; color: var(--muted);
    margin-bottom: 10px;
  }}
  .supplementary ul {{
    list-style: none; padding: 0;
  }}
  .supplementary li {{
    font-size: 12.5px; color: var(--muted);
    padding: 3px 0; padding-left: 16px;
    position: relative;
  }}
  .supplementary li::before {{
    content: "·"; position: absolute; left: 4px; color: var(--muted-soft);
  }}

  /* ===== 空状态 & 免责声明 ===== */
  .empty-state {{
    text-align: center; padding: 60px 20px;
    color: var(--muted); font-size: 14px;
  }}
  .disclaimer {{
    margin-top: 28px; padding: 14px 18px;
    background: #f8faf9; border: 1px solid var(--line-soft);
    border-radius: 10px;
    font-size: 11.5px; color: var(--muted-soft);
    line-height: 1.7; text-align: center;
  }}

  footer {{
    text-align: center; font-size: 12px; color: var(--muted);
    padding: 20px 0; margin-top: 20px;
    border-top: 1px solid var(--line);
  }}
  footer a {{ color: var(--muted); }}

  @media (max-width: 768px) {{
    .wrap {{ padding: 10px 12px 40px; }}
    .brief-container {{ padding: 20px 16px; }}
    header.hero {{ padding: 18px 20px 16px; }}
    .ev-header {{ flex-direction: column; align-items: flex-start; gap: 4px; }}
  }}
</style>
</head>
<body>
<div class="wrap">

  <header class="hero">
    <div class="hero-nav">
      <a href="https://iranorawahaha.github.io/international-news-kb/">🏠 Ira 门户</a>
      <span class="hero-nav-sep">|</span>
      <a href="https://iranorawahaha.github.io/international-news-kb/international-news.html">🌍 国际新闻</a>
      <span class="hero-nav-sep">|</span>
      <a href="https://iranorawahaha.github.io/international-news-kb/china-news.html">🇨🇳 国内新闻</a>
      <span class="hero-nav-sep">|</span>
      <a href="https://iranorawahaha.github.io/international-news-kb/ai-news.html">🤖 AI 动向</a>
      <span class="hero-nav-sep">|</span>
      <a class="active" href="diplomatic-affairs.html">🏛 使领馆事务</a>
    </div>
    <h1>🏛 使领馆事务看板</h1>
    <div class="hero-meta">
      <span>📅 {esc(date_label)}</span>
      <span>🕐 生成时间：{esc(generated)} 北京时间</span>
      <span>🔄 每日 09:30 自动刷新</span>
    </div>
  </header>

  <div class="brief-container">
    <div class="brief-header">
      <h1>国际事务公开信息摘要｜{esc(title_suffix)}</h1>
      <div class="brief-date">{esc(date_label)}</div>
    </div>
    {body}
    <div class="disclaimer">{esc(disclaimer)}</div>
  </div>

  <footer>
    数据来自权威公开信源 · 仅供个人参考交流 · 版权归原作者所有<br>
    由 WorkBuddy 自动构建 · <a href="https://github.com/Iranorawahaha/international-news-kb" target="_blank" rel="noopener noreferrer">项目仓库</a>
  </footer>

</div>
</body>
</html>'''

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)

    # JS 语法自检（页面无复杂JS，跳过node检查，只做基本校验）
    print(f"=== 使领馆事务看板 V1.0 ===")
    print(f"时间窗: {window_start} ~ {window_end}")
    print(f"模块: personnel={len(modules.get('personnel',{}).get('items',[]))}, "
          f"consuls={len(modules.get('consuls',{}).get('items',[]))}, "
          f"visits={len(modules.get('visits',{}).get('items',[]))}, "
          f"us_china={len(modules.get('us_china',{}).get('items',[]))}")
    print(f"written: {OUT_HTML} ({len(doc)} bytes)")
    return 0


def build_empty():
    """生成空状态页面"""
    window_end = NOW.strftime("%Y-%m-%d")
    doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>使领馆事务看板 · Ira 信息看板</title>
<style>
  :root {{
    --font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Microsoft YaHei", sans-serif;
    --bg: #f6f9f8; --panel: #fff; --line: #e2e8e7; --ink: #1e293b; --muted: #64748b;
    --teal: #0d9488; --teal-dark: #0f766e; --teal-soft: #f0fdfa; --teal-border: #99f6e4;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: var(--font); background: var(--bg); color: var(--ink); line-height: 1.7; min-height: 100vh; }}
  .wrap {{ max-width: 1100px; margin: 0 auto; padding: 16px 20px 60px; }}
  header.hero {{
    background: linear-gradient(135deg, #0f766e 0%, #0d9488 50%, #14b8a6 100%);
    color: #fff; border-radius: 16px; padding: 24px 32px 22px;
    box-shadow: 0 8px 24px rgba(15,118,110,.3); margin-bottom: 20px;
  }}
  .hero-nav {{
    display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px;
  }}
  .hero-nav a {{
    padding: 5px 14px; border-radius: 99px;
    background: rgba(255,255,255,.12); color: rgba(255,255,255,.85);
    text-decoration: none; font-size: 13px; font-weight: 500;
  }}
  .hero-nav a:hover {{ background: rgba(255,255,255,.22); color: #fff; }}
  .hero-nav a.active {{ background: #fff; color: #0f766e; font-weight: 700; }}
  .hero-nav-sep {{ opacity: .5; padding: 5px 2px; color: rgba(255,255,255,.6); }}
  .hero h1 {{ font-size: 24px; font-weight: 800; }}
  .hero-meta {{
    display: flex; gap: 10px; margin-top: 13px; flex-wrap: wrap; font-size: 12.5px;
  }}
  .hero-meta span {{ background: rgba(255,255,255,.15); padding: 4px 12px; border-radius: 99px; }}
  .brief-container {{
    background: var(--panel); border: 1px solid var(--line); border-radius: 16px;
    padding: 28px 32px; box-shadow: 0 1px 3px rgba(0,0,0,.04);
  }}
  .empty-state {{
    text-align: center; padding: 80px 20px; color: var(--muted);
  }}
  .empty-state .emoji {{ font-size: 48px; margin-bottom: 16px; }}
  .empty-state h2 {{ font-size: 18px; font-weight: 700; margin-bottom: 8px; color: var(--ink); }}
  .empty-state p {{ font-size: 14px; color: var(--muted); max-width: 400px; margin: 0 auto; }}
  footer {{
    text-align: center; font-size: 12px; color: var(--muted);
    padding: 20px 0; margin-top: 20px; border-top: 1px solid var(--line);
  }}
</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <div class="hero-nav">
      <a href="https://iranorawahaha.github.io/international-news-kb/">🏠 Ira 门户</a>
      <span class="hero-nav-sep">|</span>
      <a href="https://iranorawahaha.github.io/international-news-kb/international-news.html">🌍 国际新闻</a>
      <span class="hero-nav-sep">|</span>
      <a href="https://iranorawahaha.github.io/international-news-kb/china-news.html">🇨🇳 国内新闻</a>
      <span class="hero-nav-sep">|</span>
      <a href="https://iranorawahaha.github.io/international-news-kb/ai-news.html">🤖 AI 动向</a>
      <span class="hero-nav-sep">|</span>
      <a class="active">🏛 使领馆事务</a>
    </div>
    <h1>🏛 使领馆事务看板</h1>
    <div class="hero-meta">
      <span>📅 日期：{esc(window_end)}</span>
      <span>🔄 每日 09:30 自动刷新</span>
    </div>
  </header>
  <div class="brief-container">
    <div class="empty-state">
      <div class="emoji">🏛</div>
      <h2>等待首次数据采集</h2>
      <p>使领馆事务看板正在进行首次数据采集与核验，完成后将自动更新。</p>
    </div>
  </div>
  <footer>由 WorkBuddy 自动构建 · 项目仓库</footer>
</div>
</body>
</html>'''

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"=== 使领馆事务看板 V1.0（空状态）===")
    print(f"written: {OUT_HTML} ({len(doc)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(build())
