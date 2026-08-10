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
        summary = esc(a.get('summary_zh', '') or a.get('summary_en', '') or a.get('summary', ''))
        if not summary or len(summary) < 10:
            summary = esc(a.get('summary_en', '') or a.get('summary', ''))
        if not summary:
            summary = "暂无摘要"
        num = f"{n:02d}"
        return f'''<div class="card">
      <div class="card-head"><span class="card-num">{num}</span></div>
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
        num = f"{n:02d}"
        return f'''<div class="card">
      <div class="card-head"><span class="card-num">{num}</span></div>
      <div class="card-title-zh"><a href="{url}" target="_blank">{t}</a></div>
      <div class="card-meta"><span class="tag tag-cat">{cat}</span><span class="tag tag-src">{src}</span></div>
      <div class="card-summary">{summary}</div>
    </div>'''

    intl_cards = '\n'.join(intl_card(i, a) for i, a in enumerate(intl))
    dom_cards = '\n'.join(dom_card(i, a) for i, a in enumerate(dom))

    # 从模板文件加载，替换占位符
    template_path = os.path.join(BASE, 'scripts', 'morning_brief_template.html')
    with open(template_path, encoding='utf-8') as f:
        template = f.read()

    rom = lambda n: f"Vol. {month_num} · No. {day_num}" if n == 'vol' else ''
    html = template
    html = html.replace('{{WEEKDAY}}', weekday)
    html = html.replace('{{DATE_STR}}', f'{NOW.year} 年 {month_num} 月 {day_num} 日')
    html = html.replace('{{VOL}}', vol_num)
    html = html.replace('{{COUNT}}', str(total_selected))
    html = html.replace('{{INTL_COUNT}}', str(len(intl)))
    html = html.replace('{{DOM_COUNT}}', str(len(dom)))
    html = html.replace('{{INTL_TODAY}}', str(intl_today))
    html = html.replace('{{DOM_TOTAL}}', str(dom_total))
    html = html.replace('{{INTL_CARDS}}', intl_cards)
    html = html.replace('{{DOM_CARDS}}', dom_cards)
    html = html.replace('{{TODAY}}', TODAY)
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
