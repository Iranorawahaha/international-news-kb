#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ira 信息看板 · 每日早报生成与发送
用法：python3 send_daily_brief.py [--dry-run]

V2 版式：三大版面（国际 / 国内 / AI 动态），涉华优先，来源突出，摘要完整
"""

import json
import re
import smtplib
import ssl
import sys
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path

# ─── 配置 ──────────────────────────────────────────
PROJ = Path('/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50')
TZ = timezone(timedelta(hours=8))
TODAY = datetime.now(TZ).strftime('%Y-%m-%d')
WEEKDAY_CN = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
WEEKDAY = WEEKDAY_CN[datetime.now(TZ).weekday()]
NOW_STR = datetime.now(TZ).strftime('%Y-%m-%d %H:%M')

SMTP = {
    'host': 'smtp.qq.com', 'port': 465,
    'sender': '2027674540@qq.com',
    'auth_code': 'jlvcmkfkikpddehi',
    'receiver': '2027674540@qq.com',
}

PORTAL = 'https://iranorawahaha.github.io/international-news-kb/'
BOARDS = {
    'intl':  {'name': '国际新闻看板', 'url': f'{PORTAL}international-news.html', 'icon': '🌍', 'color': '#1e3a8a'},
    'ai':    {'name': 'AI 动向看板',   'url': f'{PORTAL}ai-news.html',     'icon': '🤖', 'color': '#d97706'},
    'china': {'name': '国内新闻看板',   'url': f'{PORTAL}china-news.html',           'icon': '🇨🇳', 'color': '#c41230'},
}

# ─── 数据加载 ────────────────────────────────────────
def load_json(fname):
    try:
        return json.load(open(PROJ / 'data' / fname))
    except:
        return {}

# ─── 国际新闻 ────────────────────────────────────────
intl_data = load_json('news-data.json')
intl_today = intl_data.get('archive', {}).get(TODAY, [])

# 涉华信号（国际新闻排序权重最高）
CN_SIGNALS = [
    '中国','习近平','Xi','中美','中俄','中欧','中日','中韩','台海','台湾',
    '涉华','对华','China','Chinese','Beijing','北京','北戴河','beidaihe',
    '政治局','外交部','商务部','USTR','制裁','实体清单','出口管制','关税',
    '华为','Huawei','中芯','TikTok','DeepSeek','Qwen','半导体',
    '301条款','UFLPA','新疆','维吾尔',
    '王毅','何立峰','拜登','Biden',
]

def is_cn_related(art):
    t = f"{art.get('title_zh','') or art.get('title','')} {art.get('title_en','')}".lower()
    return any(k.lower() in t for k in CN_SIGNALS)

def intl_sort_key(art):
    """排序：涉华 > 美方强主体 > 地区热点 > 一般"""
    cn = 100 if is_cn_related(art) else 0
    score = art.get('priority_score') or 0
    official = 50 if art.get('is_official') else 0
    summit = 30 if art.get('is_summit_level') else 0
    return -(cn + score + official + summit)

intl_sorted = sorted(intl_today, key=intl_sort_key)

# 精选：要闻 5 条（总共有料才取）、简讯从剩余取最多 5 条
intl_yaowen = []
seen_topics = {}
for a in intl_sorted:
    tz = a.get('title_zh') or a.get('title') or ''
    # 话题归类（防止 3 条以上同一话题）
    for kw, topic in [('霍尔木兹','霍尔木兹'), ('Hormuz','霍尔木兹'), ('伊朗','伊朗'),
                      ('Iran','伊朗'), ('台海','台海'), ('Taiwan','台海'), ('PLA','台海'),
                      ('特朗普','特朗普'), ('Trump','特朗普'), ('AI','AI科技'), ('芯片','芯片'),
                      ('制裁','制裁'), ('关税','关税'), ('俄乌','俄乌'), ('Ukraine','俄乌'),
                      ('基辅','俄乌'), ('Kyiv','俄乌'), ('以色列','中东'), ('Israel','中东'),
                      ('加沙','中东'), ('Gaza','中东'), ('巴西','拉美'), ('Argentina','拉美')]:
        if kw in tz:
            seen_topics[topic] = seen_topics.get(topic, 0) + 1
            if seen_topics[topic] <= 2:  # 每话题最多 2 条
                intl_yaowen.append(a)
            break
    else:
        intl_yaowen.append(a)
    if len(intl_yaowen) >= 5:
        break

intl_jianxun = [a for a in intl_sorted if a not in intl_yaowen][:5]

# ─── 国内新闻 ────────────────────────────────────────
china_data = load_json('china-news.json')
china_today = china_data.get('archive', {}).get(TODAY, [])

# 国内优先级：元首动态 > 部委动态 > 重要会议 > 经贸 > 其他
CN_PRIORITY = {'元首动态': 5, '部委动态': 4, '重要会议': 3, '人事变动': 3,
               '经贸动向': 2, '政策发布': 2, '使领馆动向': 2, '其他': 1}
china_sorted = sorted(china_today,
    key=lambda a: -(CN_PRIORITY.get(a.get('category', ''), 0)))

# ─── AI 动态 ─────────────────────────────────────────
def extract_ai_articles():
    """从 ai-news.html 提取今日文章"""
    try:
        html = open(PROJ / 'ai-news.html').read()
        raw = re.findall(
            r'<h3 class="card-title">(.*?)</h3>.*?<p class="card-summary">(.*?)</p>',
            html, re.DOTALL)
        arts = []
        for title, summary in raw[:15]:
            t = re.sub(r'<[^>]+>', '', title).strip()
            s = re.sub(r'<[^>]+>', '', summary).strip()
            s = re.sub(r'…\s*$', '', s).strip()
            if t and not any(skip in t for skip in ['🧵', '👇']):
                arts.append({'title': t, 'summary': s})
        return arts
    except:
        return []

ai_articles = extract_ai_articles()

# ─── 统计 ───────────────────────────────────────────
intl_total = intl_data.get('stats', {}).get('totalArticles',
    sum(len(v) for v in intl_data.get('archive', {}).values()))
cn_total = china_data.get('stats', {}).get('totalArticles', len(china_today))
try:
    ai_html = open(PROJ / 'ai-news.html').read()
    ai_new_m = re.search(r'新增[：:]\s*(\d+)', ai_html)
    ai_total_m = re.search(r'总[数條计][：:]\s*(\d+)', ai_html)
    ai_new = int(ai_new_m.group(1)) if ai_new_m else '--'
    ai_total = int(ai_total_m.group(1)) if ai_total_m else '--'
except:
    ai_new, ai_total = '--', '--'


# ═══════════════════════════════════════════════════════
#  HTML 渲染
# ═══════════════════════════════════════════════════════

def _badge(text, bg='#1e3a8a'):
    return f'<span style="display:inline-block;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:600;color:#fff;background:{bg};">{text}</span>'

def _source_pill(source, color='#64748b'):
    return f'<span style="display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;color:{color};background:{color}15;border:1px solid {color}30;">{source}</span>'

def render_intl_yaowen():
    if not intl_yaowen:
        return ''
    rows = []
    for a in intl_yaowen:
        tz = a.get('title_zh') or a.get('title') or ''
        te = a.get('title_en') or ''
        sz = a.get('summary_zh') or a.get('summary') or ''
        src = a.get('source', '')
        url = a.get('url', '')
        col = a.get('column', '')
        is_cn = is_cn_related(a)
        tag_bg = '#c41230' if is_cn else '#ea580c'
        tag_text = '涉华' if is_cn else '高优'
        rows.append(f'''
    <tr>
      <td style="padding:16px 20px; border-bottom:1px solid #e2e8f0;">
        <div style="margin-bottom:6px;">
          {_badge(tag_text, tag_bg)}
          <span style="font-size:11px;color:#94a3b8;margin-left:6px;">[{col}]</span>
          {_source_pill(src, '#1e3a8a')}
          {f'<span style="font-size:11px;color:#ef4444;margin-left:4px;">★ 官方信源</span>' if a.get('is_official') else ''}
        </div>
        <div style="font-size:15px;font-weight:600;color:#1e293b;line-height:1.6;margin:6px 0;">{tz}</div>
        {f'<div style="font-size:13px;color:#475569;line-height:1.75;margin:8px 0;">{sz[:200]}</div>' if sz else ''}
        <a href="{url}" target="_blank" style="display:inline-block;margin-top:4px;padding:5px 14px;background:#1e3a8a;color:#fff;text-decoration:none;border-radius:6px;font-size:12px;font-weight:500;">查看原文 →</a>
      </td>
    </tr>''')
    return f'''
      <tr>
        <td style="padding:14px 20px 6px;background:#fef2f2;">
          <div style="font-size:15px;font-weight:700;color:#b91c1c;">📌 国际要闻</div>
        </td>
      </tr>
      {''.join(rows)}'''

def render_intl_jianxun():
    if not intl_jianxun:
        return ''
    rows = []
    for a in intl_jianxun:
        tz = a.get('title_zh') or a.get('title') or ''
        sz = a.get('summary_zh') or a.get('summary') or ''
        src = a.get('source', '')
        url = a.get('url', '')
        rows.append(f'''
    <tr>
      <td style="padding:10px 20px; border-bottom:1px solid #f1f5f9;">
        <div style="font-size:13.5px;color:#334155;font-weight:500;line-height:1.5;">{tz}</div>
        <div style="margin-top:4px;">
          {_source_pill(src, '#64748b')}
          <a href="{url}" target="_blank" style="color:#1e3a8a;font-size:11px;text-decoration:none;margin-left:8px;">详情 →</a>
        </div>
        {f'<div style="font-size:12px;color:#64748b;line-height:1.6;margin-top:4px;">{sz[:150]}</div>' if sz else ''}
      </td>
    </tr>''')
    return f'''
      <tr>
        <td style="padding:14px 20px 6px;background:#fefce8;">
          <div style="font-size:14px;font-weight:700;color:#854d0e;">📋 国际简讯</div>
        </td>
      </tr>
      {''.join(rows)}'''

def render_china_section():
    if not china_today:
        return '<tr><td style="padding:20px;text-align:center;color:#94a3b8;">暂无今日国内新闻</td></tr>'
    rows = []
    for a in china_sorted[:5]:
        tz = a.get('title_zh') or a.get('title') or ''
        sz = a.get('summary_zh') or a.get('summary') or ''
        src = a.get('source', '')
        url = a.get('url', '')
        cat = a.get('category', '')
        rows.append(f'''
    <tr>
      <td style="padding:14px 20px; border-bottom:1px solid #fee2e2;">
        <div style="margin-bottom:4px;">
          {_badge(cat, '#c41230')}
          {_source_pill(src, '#c41230')}
        </div>
        <div style="font-size:14px;font-weight:600;color:#1e293b;line-height:1.6;">{tz}</div>
        {f'<div style="font-size:13px;color:#475569;line-height:1.75;margin:6px 0;">{sz[:200]}</div>' if sz else ''}
        <a href="{url}" target="_blank" style="display:inline-block;margin-top:4px;padding:5px 14px;background:#c41230;color:#fff;text-decoration:none;border-radius:6px;font-size:12px;font-weight:500;">查看原文 →</a>
      </td>
    </tr>''')
    return f'''
      <tr>
        <td style="padding:14px 20px 6px;background:#fef2f2;">
          <div style="font-size:15px;font-weight:700;color:#b91c1c;">🏛️ 国内要闻</div>
        </td>
      </tr>
      {''.join(rows)}'''

def render_ai_section():
    if not ai_articles:
        return '<tr><td style="padding:20px;text-align:center;color:#94a3b8;">暂无今日 AI 动态</td></tr>'
    rows = []
    for a in ai_articles[:6]:
        tz = a['title']
        sz = a.get('summary', '')
        # 去重（同一话题只保留一条）
        rows.append(f'''
    <tr>
      <td style="padding:14px 20px; border-bottom:1px solid #fef3c7;">
        <div style="margin-bottom:4px;">
          {_badge('AI 动态', '#d97706')}
        </div>
        <div style="font-size:14px;font-weight:600;color:#1e293b;line-height:1.6;">{tz}</div>
        {f'<div style="font-size:13px;color:#475569;line-height:1.75;margin:6px 0;">{sz[:200]}</div>' if sz else ''}
      </td>
    </tr>''')
    return f'''
      <tr>
        <td style="padding:14px 20px 6px;background:#fffbeb;">
          <div style="font-size:15px;font-weight:700;color:#b45309;">🤖 AI 动态</div>
        </td>
      </tr>
      {''.join(rows)}'''

# ─── 主 HTML ─────────────────────────────────────────
def render_email():
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:20px 0;">
  <tr><td align="center">
    <table width="640" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden;">

      <tr>
        <td style="background:linear-gradient(135deg,#1e3a8a,#2563eb);padding:24px 28px 18px;">
          <div style="font-size:22px;font-weight:700;color:#fff;">📧 Ira 信息看板早报</div>
          <div style="font-size:13px;color:rgba(255,255,255,0.85);margin-top:4px;">{TODAY} {WEEKDAY} · 国际 / 国内 / AI 三版精选</div>
        </td>
      </tr>

      <tr>
        <td style="padding:12px 28px;background:#f8fafc;border-bottom:1px solid #e2e8f0;">
          <table width="100%" cellpadding="0" cellspacing="0"><tr>
            <td style="font-size:13px;color:#64748b;">
              🌍 国际 <strong style="color:#1e3a8a;">+{len(intl_today)}</strong> &nbsp;&nbsp;
              🇨🇳 国内 <strong style="color:#c41230;">+{len(china_today)}</strong> &nbsp;&nbsp;
              🤖 AI <strong style="color:#d97706;">+{ai_new}</strong>
            </td>
            <td align="right" style="font-size:11px;color:#94a3b8;">每日 9:40 自动发送</td>
          </tr></table>
        </td>
      </tr>

      <!-- 国际要闻 -->
      {render_intl_yaowen()}

      <!-- 国际简讯 -->
      {render_intl_jianxun()}

      <!-- 国内要闻 -->
      {render_china_section()}

      <!-- AI 动态 -->
      {render_ai_section()}

      <!-- 快速跳转 -->
      <tr>
        <td style="padding:20px 28px;background:#f8fafc;border-top:1px solid #e2e8f0;">
          <div style="font-size:13px;font-weight:600;color:#64748b;margin-bottom:10px;">🔗 快速跳转</div>
          <table width="100%" cellpadding="0" cellspacing="0"><tr>
            <td align="center">
              <a href="{BOARDS['intl']['url']}" style="display:inline-block;padding:8px 16px;background:#1e3a8a;color:#fff;text-decoration:none;border-radius:8px;font-size:13px;font-weight:500;margin:4px;">🌍 国际新闻</a>
              <a href="{BOARDS['china']['url']}" style="display:inline-block;padding:8px 16px;background:#c41230;color:#fff;text-decoration:none;border-radius:8px;font-size:13px;font-weight:500;margin:4px;">🇨🇳 国内新闻</a>
              <a href="{BOARDS['ai']['url']}" style="display:inline-block;padding:8px 16px;background:#d97706;color:#fff;text-decoration:none;border-radius:8px;font-size:13px;font-weight:500;margin:4px;">🤖 AI 动向</a>
              <a href="{PORTAL}" style="display:inline-block;padding:8px 16px;background:#475569;color:#fff;text-decoration:none;border-radius:8px;font-size:13px;font-weight:500;margin:4px;">🏠 门户</a>
            </td>
          </tr></table>
        </td>
      </tr>

      <!-- 页脚 -->
      <tr>
        <td style="padding:14px 28px;background:#f1f5f9;text-align:center;">
          <div style="font-size:11px;color:#94a3b8;">© 2026 Ira 信息看板 · 基于 <a href="https://github.com/Iranorawahaha/international-news-kb" style="color:#1e3a8a;">GitHub Pages</a> · {NOW_STR}</div>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body></html>'''

# ─── SMTP 发送 ────────────────────────────────────────
def send_email(html_content, subject):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = SMTP['sender']
    msg['To'] = SMTP['receiver']
    msg['Date'] = formatdate(localtime=True)
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP['host'], SMTP['port'], context=ctx) as s:
        s.login(SMTP['sender'], SMTP['auth_code'])
        s.send_message(msg)
    print(f'✅ 邮件已发送 → {SMTP["receiver"]}')

# ─── 入口 ─────────────────────────────────────────────
if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv

    cn_related = sum(1 for a in intl_yaowen if is_cn_related(a))
    print(f'📧 Ira 信息看板早报 · {TODAY} {WEEKDAY}')
    print(f'   国际 +{len(intl_today)} | 国内 +{len(china_today)} | AI +{ai_new}')
    print(f'   国际要闻 {len(intl_yaowen)} 条（涉华 {cn_related}） + 简讯 {len(intl_jianxun)}')
    print(f'   国内要闻 {min(len(china_today), 5)} 条 | AI 动态 {min(len(ai_articles), 6)} 条')
    # 验证涉华优先
    if intl_yaowen:
        first = intl_yaowen[0]
        print(f'   首条: {("涉华 ✅" if is_cn_related(first) else "⚠️非涉华")} — {(first.get("title_zh") or first.get("title",""))[:50]}')
    print()

    if dry_run:
        out = '/tmp/ira_daily_brief_v2.html'
        with open(out, 'w', encoding='utf-8') as f:
            f.write(render_email())
        print(f'🏜️ [DRY RUN] 已保存 {out}')
    else:
        subject = f'📧 Ira看板信息早报 · {TODAY} {WEEKDAY}'
        html = render_email()
        send_email(html, subject)
