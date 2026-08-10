#!/usr/bin/env python3
"""
send_morning_brief.py — Ira 信息看板 · 每日早报发送器

流程：
  1) 读取国际 + 国内数据
  2) 生成 HTML 邮件
  3) PREVIEW 模式：保存 morning-brief-preview.html 供用户确认
  4) SEND 模式：通过 QQ SMTP 发送

用法：
  python3 scripts/send_morning_brief.py --preview      # 仅生成预览
  python3 scripts/send_morning_brief.py --send          # 直接发送
  python3 scripts/send_morning_brief.py --preview --send  # 生成预览后发送（自动化默认）
"""

import json
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta

# ── 配置 ────────────────────────────────────
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
TODAY = NOW.strftime('%Y-%m-%d')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTL_DATA = os.path.join(BASE, "data", "news-data.json")
CHINA_DATA = os.path.join(BASE, "data", "china-news.json")
PREVIEW_HTML = os.path.join(BASE, "morning-brief-preview.html")
LOG_FILE = os.path.join(BASE, "data", "morning-brief-log.json")

SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465
SMTP_USER = "2027674540@qq.com"
SMTP_PASS = "rsdsoaxfejsjbcjc"
TO_EMAIL = "2027674540@qq.com"

WEEKDAY_CN = {0: '星期一', 1: '星期二', 2: '星期三', 3: '星期四', 4: '星期五', 5: '星期六', 6: '星期日'}

INTL_MIN_SCORE = 88
DOM_MIN_SCORE = 80


def load_articles():
    """加载国际高优 + 国内≥80分"""
    intl, dom = [], []

    with open(INTL_DATA) as f:
        nd = json.load(f)
    a10 = nd['archive'].get(TODAY, nd['archive'].get(max(nd['archive'].keys(), key=lambda k: k), []))
    intl = [a for a in a10 if a.get('priority_score', 0) >= INTL_MIN_SCORE]
    intl_total = sum(len(v) for v in nd['archive'].values())
    intl_today = len(nd['archive'].get(TODAY, []))

    with open(CHINA_DATA) as f:
        cd = json.load(f)
    c10 = cd['archive'].get(TODAY, cd['archive'].get(max(cd['archive'].keys(), key=lambda k: k), []))
    dom = [a for a in c10 if a.get('priority_score', 0) >= DOM_MIN_SCORE]
    dom_total = len(c10)

    return intl, dom, intl_today, intl_total, dom_total


def esc(text):
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_html(intl, dom, intl_today, intl_total, dom_total):
    """生成 邮件 HTML（含毛玻璃 masthead + 真实URL + 双语标题）"""

    day_num = NOW.day
    month_num = NOW.month
    weekday = WEEKDAY_CN[NOW.weekday()]
    week_num = NOW.isocalendar()[1]
    vol_num = f"Vol. {month_num} · No. {day_num}"
    total_selected = len(intl) + len(dom)

    def intl_card(i, a):
        n = i + 1
        te = esc(a.get('title_en', '') or a.get('title', ''))
        tz = esc(a.get('title_zh', '') or a.get('title', ''))
        url = esc(a.get('url', '#'))
        src = esc(a.get('source', ''))
        # 摘要：优先 summary_zh，其次 summary_en/summary
        summary = esc(a.get('summary_zh', '') or a.get('summary_en', '') or a.get('summary', ''))
        # 如果摘要太短，用 summary_en 兜底
        if not summary or len(summary) < 10:
            summary = esc(a.get('summary_en', '') or a.get('summary', ''))
        if not summary:
            summary = "暂无摘要"
        return f'''
    <div class="card">
      <span class="card-num">{n}</span>
      <div class="card-title-en">{te}</div>
      <div class="card-title-zh"><a href="{url}" target="_blank">{tz}</a></div>
      <div class="card-meta"><span class="tag tag-src">{src}</span></div>
      <div class="card-summary">{summary}</div>
    </div>'''

    def dom_card(i, a):
        n = i + 1
        t = esc(a.get('title', ''))
        url = esc(a.get('url', '#'))
        src = esc(a.get('source', ''))
        cat = esc(a.get('category', '其他'))
        summary = esc(a.get('summary', '') or '暂无摘要')
        return f'''
    <div class="card">
      <span class="card-num">{n}</span>
      <div class="card-title-zh"><a href="{url}" target="_blank">{t}</a></div>
      <div class="card-meta"><span class="tag tag-cat">{cat}</span><span class="tag tag-src">{src}</span></div>
      <div class="card-summary">{summary}</div>
    </div>'''

    intl_cards = '\n'.join(intl_card(i, a) for i, a in enumerate(intl))
    dom_cards = '\n'.join(dom_card(i, a) for i, a in enumerate(dom))

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ira 信息看板 · 每日早报 {TODAY}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700;9..144,900&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  body {{ font-family: "Inter", -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif; background: linear-gradient(135deg, #fef9f3 0%, #f0f4f8 100%); min-height: 100vh; color: #1a1a2e; line-height: 1.7; padding: 24px 16px; margin: 0; }}
  .masthead {{
    position: relative; background: linear-gradient(140deg, #0c1426 0%, #1e2952 40%, #0a3060 100%);
    border-radius: 20px; padding: 36px 28px 28px; margin: 0 auto 24px; max-width: 720px;
    overflow: hidden; isolation: isolate;
    box-shadow: 0 24px 60px -20px rgba(12,20,38,.5), 0 4px 12px rgba(12,20,38,.25);
  }}
  .masthead::before {{
    content: ""; position: absolute; inset: 0; z-index: -1;
    background:
      radial-gradient(circle at 12% 20%, rgba(244,114,182,.18), transparent 35%),
      radial-gradient(circle at 90% 80%, rgba(56,189,248,.20), transparent 40%),
      radial-gradient(circle at 75% 15%, rgba(251,191,36,.12), transparent 30%);
    pointer-events: none;
  }}
  .masthead::after {{
    content: ""; position: absolute; inset: 1px; border-radius: 19px;
    background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.02));
    z-index: -1; pointer-events: none;
  }}
  .brand-line {{ display: flex; align-items: center; gap: 10px; font-size: 11px; font-weight: 600; letter-spacing: 2.5px; text-transform: uppercase; color: rgba(255,255,255,.55); margin-bottom: 20px; }}
  .brand-line .dot {{ width: 6px; height: 6px; border-radius: 50%; background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }}
  .brand-line .vol {{ margin-left: auto; font-family: "Fraunces", serif; font-style: italic; font-weight: 500; letter-spacing: .5px; text-transform: none; color: rgba(255,255,255,.7); }}
  .head-title {{ font-family: "Fraunces", "PingFang SC", serif; font-size: 36px; font-weight: 700; font-style: italic; color: #fff; letter-spacing: -0.5px; line-height: 1.05; margin: 0 0 20px; }}
  .head-title .en {{ font-style: normal; font-weight: 500; color: rgba(255,255,255,.55); font-size: 22px; letter-spacing: 0.5px; margin-left: 10px; }}
  .glass-row {{ display: grid; grid-template-columns: 1.1fr 1fr; gap: 12px; margin-top: 8px; }}
  .glass-card {{
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    backdrop-filter: blur(20px) saturate(180%);
    background: rgba(255,255,255,.10); border: 1px solid rgba(255,255,255,.18);
    border-radius: 16px; padding: 18px 18px; color: #fff;
    box-shadow: 0 8px 24px rgba(0,0,0,.15), inset 0 1px 0 rgba(255,255,255,.15);
  }}
  .date-card {{ display: flex; align-items: center; gap: 16px; }}
  .date-card .big-day {{
    font-family: "Fraunces", serif; font-weight: 900; font-size: 56px; line-height: 1; letter-spacing: -2px;
    background: linear-gradient(180deg, #fff 0%, #fed7aa 100%);
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
  }}
  .date-card .day-meta {{ display: flex; flex-direction: column; gap: 4px; }}
  .date-card .weekday {{ font-family: "Fraunces", serif; font-style: italic; font-weight: 500; font-size: 17px; color: #fef3c7; letter-spacing: 1px; }}
  .date-card .date-str {{ font-size: 12px; color: rgba(255,255,255,.7); font-weight: 500; }}
  .count-card {{ display: flex; flex-direction: column; justify-content: center; gap: 8px; }}
  .count-row {{ display: flex; align-items: baseline; gap: 8px; }}
  .count-num {{ font-family: "Fraunces", serif; font-weight: 700; font-size: 28px; color: #fef3c7; line-height: 1; }}
  .count-label {{ font-size: 12px; color: rgba(255,255,255,.8); }}
  .intro {{ margin: 18px 0 0; padding: 0; font-size: 13.5px; color: rgba(255,255,255,.85); line-height: 1.85; }}
  .intro a {{ color: #fbbf24; text-decoration: none; border-bottom: 1px solid rgba(251,191,36,.4); }}
  .intro b {{ color: #fef3c7; font-weight: 700; }}
  .section {{ margin-bottom: 22px; }}
  .section-title {{ display: flex; align-items: baseline; gap: 12px; margin: 0 auto 14px; max-width: 720px; padding-bottom: 8px; border-bottom: 1.5px solid #1a1a2e; }}
  .section-title .ch {{ font-family: "Fraunces", serif; font-weight: 700; font-size: 22px; color: #1a1a2e; letter-spacing: -0.3px; }}
  .section-title .en {{ font-family: "Fraunces", serif; font-style: italic; font-weight: 500; font-size: 14px; color: #9ca3af; }}
  .section-title.intl .ch {{ color: #1e3a8a; }}
  .section-title.dom .ch {{ color: #dc2626; }}
  .card {{ max-width: 720px; margin: 0 auto 10px; background: #fff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 16px 18px; box-shadow: 0 2px 4px rgba(0,0,0,.02); }}
  .card-num {{ display: inline-block; min-width: 22px; height: 22px; padding: 0 6px; border-radius: 6px; background: #f1f5f9; color: #64748b; font-family: "Fraunces", serif; font-weight: 700; font-size: 12px; text-align: center; line-height: 22px; margin-right: 10px; vertical-align: text-top; }}
  .card-title-en {{ font-size: 12.5px; color: #94a3b8; margin-bottom: 3px; font-style: italic; font-family: "Fraunces", serif; }}
  .card-title-zh {{ font-size: 15px; font-weight: 650; line-height: 1.5; }}
  .card-title-zh a {{ color: #1a1a2e; text-decoration: none; }}
  .card-meta {{ display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }}
  .card-summary {{ font-size: 13px; color: #4b5563; margin-top: 8px; line-height: 1.75; }}
  .tag {{ font-size: 11px; padding: 2px 8px; border-radius: 999px; font-weight: 600; }}
  .tag-src {{ background: #dbeafe; color: #1e40af; }}
  .tag-cat {{ background: #fef3c7; color: #92400e; }}
  .footer-block {{ max-width: 720px; margin: 24px auto 0; }}
  .nav-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 14px; }}
  .nav-card {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px 12px; text-align: center; text-decoration: none; display: block; transition: all .2s; }}
  .nav-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,.08); }}
  .nav-icon {{ font-size: 22px; }}
  .nav-name {{ font-size: 13px; font-weight: 700; margin-top: 4px; }}
  .nav-desc {{ font-size: 11px; color: #6b7280; margin-top: 2px; }}
  .nav-intl .nav-name {{ color: #1e3a8a; }}
  .nav-dom .nav-name {{ color: #dc2626; }}
  .nav-ai .nav-name {{ color: #7c3aed; }}
  .sources-box {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px 18px; margin-bottom: 14px; }}
  .sources-title {{ font-size: 13px; font-weight: 700; color: #374151; margin-bottom: 8px; font-family: "Fraunces", serif; }}
  .sources-list {{ font-size: 11.5px; color: #6b7280; line-height: 1.85; }}
  .sources-list b {{ color: #1a1a2e; }}
  .footer-credits {{ text-align: center; font-size: 11px; color: #9ca3af; padding: 20px 0; line-height: 1.8; font-family: "Fraunces", serif; font-style: italic; }}
  .footer-credits a {{ color: #1d4ed8; text-decoration: none; }}
</style>
</head>
<body>
<div class="masthead">
  <div class="brand-line">
    <span class="dot"></span><span>Ira Daily Brief</span>
    <span class="vol">{vol_num}</span>
  </div>
  <h1 class="head-title">每日早报<span class="en">Morning Brief</span></h1>
  <div class="glass-row">
    <div class="glass-card date-card">
      <div class="big-day">{day_num}</div>
      <div class="day-meta">
        <div class="weekday">{weekday}</div>
        <div class="date-str">{NOW.year} 年 {month_num} 月 · 第 {week_num} 周</div>
      </div>
    </div>
    <div class="glass-card count-card">
      <div class="count-row">
        <div class="count-num">{total_selected}</div>
        <div class="count-label">条精选新闻</div>
      </div>
      <div style="font-size:11px; color:rgba(255,255,255,.55);">🌍 国际 {len(intl)} &nbsp;·&nbsp; 🇨🇳 国内 {len(dom)}</div>
    </div>
  </div>
  <div class="intro">
    <a href="https://iranorawahaha.github.io/international-news-kb/">Ira 信息看板</a>
    每日追踪中美关系、地缘政治、经贸制裁、AI 科技等国际国内重大动向。
    过去 24 小时各版面新增 <b>{intl_today}</b> 篇国际新闻、<b>{dom_total}</b> 篇国内要闻，以下为较高重要性新闻速览。
  </div>
</div>

<div class="section">
  <div class="section-title intl">
    <span class="ch">🌍 国际要闻</span>
    <span class="en">World · {len(intl)} stories</span>
  </div>
  {intl_cards}
</div>

<div class="section">
  <div class="section-title dom">
    <span class="ch">🇨🇳 国内要闻</span>
    <span class="en">China · {len(dom)} stories</span>
  </div>
  {dom_cards}
</div>

<div class="footer-block">
  <div class="nav-grid">
    <a href="https://iranorawahaha.github.io/international-news-kb/international-news.html" class="nav-card nav-intl">
      <div class="nav-icon">🌍</div>
      <div class="nav-name">国际新闻看板</div>
      <div class="nav-desc">{intl_today} 篇 · 全外媒</div>
    </a>
    <a href="https://iranorawahaha.github.io/international-news-kb/china-news.html" class="nav-card nav-dom">
      <div class="nav-icon">🇨🇳</div>
      <div class="nav-name">国内新闻看板</div>
      <div class="nav-desc">{dom_total} 篇 · 国家级权威</div>
    </a>
    <a href="https://iranorawahaha.github.io/international-news-kb/ai-news.html" class="nav-card nav-ai">
      <div class="nav-icon">🤖</div>
      <div class="nav-name">AI 动向看板</div>
      <div class="nav-desc">关注行业前沿</div>
    </a>
  </div>
  <div class="sources-box">
    <div class="sources-title">📡 今日信源（14 家）</div>
    <div class="sources-list">
      <b>国际外媒：</b>Reuters · AP News · BBC · CNN · The Guardian · The New York Times · The Wall Street Journal · Financial Times · South China Morning Post · Al Jazeera · The Washington Post · Politico<br>
      <b>中国官方与权威：</b>中国政府网（要闻 / 最新政策）· 央视新闻 · 人民日报 · 外交部 · 国家发改委 · 商务部 · 联合早报（海外中文权威）
    </div>
  </div>
  <div class="footer-credits">
    📮 Ira 信息看板 · 每日自动生成 · 仅供参考交流<br>
    🌐 <a href="https://iranorawahaha.github.io/international-news-kb/">iranorawahaha.github.io/international-news-kb</a>
  </div>
</div>
</body>
</html>'''
    return html


def send_email(html_body, intl_count, dom_count):
    """通过 QQ SMTP 发送邮件"""
    from email.header import Header

    total = intl_count + dom_count
    subject = Header(f'Ira 早报 · {TODAY} · {total}条精选', 'utf-8')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f'Ira Daily Brief <{SMTP_USER}>'
    msg['To'] = TO_EMAIL

    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, [TO_EMAIL], msg.as_string())
        print(f'✅ 邮件已发送 → {TO_EMAIL}')
        return True
    except Exception as e:
        print(f'❌ 发送失败: {e}')
        return False


def total_approx(html):
    """粗略统计卡片数"""
    return str(html.count('<div class="card">'))


def save_log(intl_count, dom_count, sent):
    log = {
        'date': TODAY,
        'time': NOW.strftime('%H:%M'),
        'intlCount': intl_count,
        'domCount': dom_count,
        'totalCount': intl_count + dom_count,
        'sent': sent,
    }
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def main():
    preview = '--preview' in sys.argv
    do_send = '--send' in sys.argv

    if not preview and not do_send:
        print('用法: --preview (预览) / --send (发送) / --preview --send (预览+发送)')
        return 1

    print(f'📰 Ira 早报生成中... {TODAY}')

    intl, dom, intl_today, intl_total, dom_total = load_articles()
    print(f'   🌍 国际: {len(intl)} 篇高优 (今日新增 {intl_today} / 总 {intl_total})')
    print(f'   🇨🇳 国内: {len(dom)} 篇 ≥{DOM_MIN_SCORE}分 (今日 {dom_total})')

    html = build_html(intl, dom, intl_today, intl_total, dom_total)

    if preview:
        with open(PREVIEW_HTML, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'✅ 预览已生成: {PREVIEW_HTML}')

    sent = False
    if do_send:
        sent = send_email(html, len(intl), len(dom))

    save_log(len(intl), len(dom), sent)

    return 0 if not do_send or sent else 1


if __name__ == '__main__':
    sys.exit(main())
