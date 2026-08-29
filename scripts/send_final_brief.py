#!/usr/bin/env python3
"""
send_final_brief.py — 生成精美的 Outlook 友好版早报并发送

用法：
  python3 scripts/send_final_brief.py            # 生成精美版 + 发送邮件
  python3 scripts/send_final_brief.py --preview  # 仅生成 HTML 不发送
"""
import json
import os
import sys
import time
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
TODAY = NOW.strftime('%Y-%m-%d')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTL_DATA = os.path.join(BASE, "data", "news-data.json")
CHINA_DATA = os.path.join(BASE, "data", "china-news.json")
OUT_HTML = os.path.join(BASE, "morning-brief-final.html")
PDF_DIR = os.path.join(BASE, "日报PDF")

SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465
SMTP_USER = "2027674540@qq.com"
SMTP_PASS = "rsdsoaxfejsjbcjc"
TO_EMAIL = "2027674540@qq.com"

# 默认收件人（2026-08-21 规则变更）：仅发送 QQ 邮箱一个地址
# 原因：华为企业邮箱网关拦截 QQ SMTP 发出的富 HTML 邮件（文本版可到、HTML 版被丢弃），
# 群发 24 人名单无法可靠送达 → 改为仅发 2027674540@qq.com，由用户人工确认后自行分发。
DEFAULT_RECIPIENTS = [
    "2027674540@qq.com",
]

# 发送机制参数（QQ SMTP 群发风控经验值）
SEND_DELAY = 6.0     # 每封间隔秒数（约每分钟 10 封，低于此值易触发风控）
RETRY_DELAY = 70     # 触发风控后重试等待秒数
MAX_RETRIES = 3      # 每封最多尝试次数

WEEKDAY_CN = {0: '星期一', 1: '星期二', 2: '星期三', 3: '星期四', 4: '星期五', 5: '星期六', 6: '星期日'}

INTL_MIN_SCORE = 88
DOM_MIN_SCORE = 80

# 用户删减指令（位置索引，从 1 开始）
# 注意：每日删减通过「飞书确认」环节人工增减，不在此硬编码（否则位置索引会误删次日内容）
INTL_EXCLUDE = set()
DOM_EXCLUDE = set()

# 数据就绪门禁：国际看板今日最低条数（低于此值视为「看板尚未刷新完成」）
INTL_MIN_TODAY = 10
IRA_RUNS_FILE = os.path.expanduser("~/.workbuddy/ira_runs.json")

# 使领馆看板数据文件（日报「使领馆动态」板块来源，有则展示、无则省略）
DIPLO_DATA = os.path.join(BASE, "data", "diplomatic-affairs.json")

# 当天手动调整配置（可选）：调整国际条目顺序 + 额外纳入低分条目
BRIEF_OVERRIDE = os.path.join(BASE, "data", "brief-override.json")


def _norm_url(u):
    return (u or '').strip().rstrip('/').lower()


def load_override():
    """读取当天手动调整配置（可选）。仅当 date == 今日 时生效。"""
    if not os.path.exists(BRIEF_OVERRIDE):
        return None
    try:
        with open(BRIEF_OVERRIDE) as f:
            ov = json.load(f)
    except Exception:
        return None
    if ov.get('date') != TODAY:
        return None
    return ov


def esc(text):
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def load_articles():
    override = load_override()
    intl_order = (override or {}).get('intl_order') or []
    intl_include = (override or {}).get('intl_include') or []
    intl_exclude = (override or {}).get('intl_exclude') or []

    with open(INTL_DATA) as f:
        nd = json.load(f)
    a10 = nd['archive'].get(TODAY, nd['archive'].get(max(nd['archive'].keys()), []))
    intl_full = [a for a in a10 if a.get('priority_score', 0) >= INTL_MIN_SCORE]

    # 额外纳入的低分条目（用户手动指定，即使 score < 88）
    if intl_include:
        include_urls = {_norm_url(u) for u in intl_include}
        for a in a10:
            if _norm_url(a.get('url')) in include_urls and a not in intl_full:
                intl_full.append(a)

    # 排除 + 按 override 指定顺序重排
    intl_exclude_set = set(INTL_EXCLUDE) | set(intl_exclude)
    intl = [a for i, a in enumerate(intl_full) if (i + 1) not in intl_exclude_set]
    if intl_order:
        order_map = {_norm_url(u): idx for idx, u in enumerate(intl_order)}
        indexed = [(a, i) for i, a in enumerate(intl)]
        indexed.sort(key=lambda ai: (0, order_map[_norm_url(ai[0].get('url'))]) if _norm_url(ai[0].get('url')) in order_map else (1, ai[1]))
        intl = [a for a, _ in indexed]

    with open(CHINA_DATA) as f:
        cd = json.load(f)
    c10 = cd['archive'].get(TODAY, cd['archive'].get(max(cd['archive'].keys()), []))
    dom_full = [a for a in c10 if a.get('priority_score', 0) >= DOM_MIN_SCORE]
    dom_exclude = set(DOM_EXCLUDE) | set((override or {}).get('dom_exclude') or [])
    dom = [a for i, a in enumerate(dom_full) if (i + 1) not in dom_exclude]
    return intl, dom


def load_diplo_updates(lookback_days=2):
    """读取使领馆看板近 N 天的新增动态（有则返回列表，无则空列表）。"""
    if not os.path.exists(DIPLO_DATA):
        return []
    try:
        with open(DIPLO_DATA) as f:
            dd = json.load(f)
    except Exception:
        return []
    cutoff = (NOW - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
    updates = []
    for module in (dd.get('modules') or {}).values():
        for item in (module.get('items') or []):
            ed = item.get('event_date') or ''
            if ed and ed >= cutoff:
                updates.append({
                    'module': module.get('title', ''),
                    'country': item.get('country', ''),
                    'event_type': item.get('event_type') or item.get('interaction_type') or '',
                    'person': item.get('person_name') or item.get('cn_person') or '',
                    'headline': item.get('headline', ''),
                    'date': ed,
                    'description': item.get('description', ''),
                })
    return updates


def count_intl_today():
    """统计国际看板今日条数"""
    with open(INTL_DATA) as f:
        nd = json.load(f)
    return len(nd.get('archive', {}).get(TODAY, []))


def load_ira_runs():
    try:
        with open(IRA_RUNS_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def ensure_data_ready(wait_minutes=15, max_rounds=2):
    """数据就绪门禁：确保国际看板今日已刷新完成，未就绪则补跑/等待。

    返回 (就绪, 今日国际条数)。
    """
    for round_no in range(max_rounds + 1):
        cnt = count_intl_today()
        if cnt >= INTL_MIN_TODAY:
            print(f'   ✅ 国际看板今日已就绪（{cnt} 条）')
            return True, cnt

        state = load_ira_runs()
        news_rec = state.get('news') or {}
        news_ok = news_rec.get('date') == TODAY and news_rec.get('status') == 'ok'
        news_failed = news_rec.get('date') == TODAY and news_rec.get('status') == 'failed'

        if news_ok:
            # 看板已成功刷新但条数少 → 真实数据少，接受
            print(f'   ⚠️ 国际看板今日已刷新但仅 {cnt} 条（可能信源异常），继续生成')
            return True, cnt

        if news_failed or round_no >= 1:
            # 明确失败，或已等待一轮仍不足 → 触发补跑
            print(f'   ⏳ 国际看板今日未就绪（当前 {cnt} 条），触发补跑...')
            try:
                subprocess.run(
                    [sys.executable, os.path.join(BASE, 'scripts', 'check_missed_runs.py'), '--task', 'news'],
                    cwd=BASE, timeout=3600,
                )
            except Exception as e:
                print(f'   ❌ 补跑异常: {e}')
            cnt = count_intl_today()
            if cnt >= INTL_MIN_TODAY:
                print(f'   ✅ 补跑后国际看板就绪（{cnt} 条）')
                return True, cnt

        # 可能 9:30 的刷新仍在进行 → 等待后再检查
        if round_no < max_rounds:
            print(f'   ⏳ 等待 {wait_minutes} 分钟后再次检查...')
            time.sleep(wait_minutes * 60)

    cnt = count_intl_today()
    print(f'   ⚠️ 国际看板今日数据仍不足（{cnt} 条），继续生成（国际篇数可能偏少）')
    return False, cnt


def intl_row(i, a):
    n = i + 1
    te = esc(a.get('title_en', '') or a.get('title', ''))
    tz = esc(a.get('title_zh', '') or a.get('title', ''))
    url = esc(a.get('url', '#'))
    src = esc(a.get('source', ''))
    summary = esc(a.get('summary_zh', '') or a.get('summary_en', '') or a.get('summary', ''))
    if not summary:
        summary = "暂无摘要"
    num = f"{n:02d}"
    # 标题纯文本（不再点击跳转），原文链接列明（PDF 中可点击）
    return f'''<tr>
  <td style="padding:20px 22px; border-bottom:1px solid #ecebe6; border-left:4px solid #1e3a8a; background:#ffffff;">
    <table cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
      <td style="width:34px; vertical-align:top; padding-top:2px;">
        <table cellpadding="0" cellspacing="0" border="0"><tr>
          <td align="center" style="background:#1e3a8a; color:#ffffff; font-family:Georgia,'Times New Roman',serif; font-size:12px; font-weight:700; letter-spacing:0.5px; padding:5px 7px;">{num}</td>
        </tr></table>
      </td>
      <td style="padding-left:14px;">
        <p style="margin:0 0 5px 0; font-family:Georgia,'Times New Roman',serif; font-size:11.5px; font-style:italic; color:#9aa0ac; line-height:1.45;">{te}</p>
        <p style="margin:0 0 7px 0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei','SimHei',sans-serif; font-size:15.5px; font-weight:700; line-height:1.5; color:#1a1a2e;">
          {tz}
        </p>
        <p style="margin:0 0 9px 0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif; font-size:11px; color:#8a8f9a; letter-spacing:0.3px;">{src}</p>
        <p style="margin:0 0 6px 0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei','SimHei',sans-serif; font-size:13px; color:#4b5563; line-height:1.8;">{summary}</p>
        <p style="margin:0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif; font-size:11px; line-height:1.5; word-break:break-all;">🔗 原文链接：<a href="{url}" style="color:#1e3a8a; text-decoration:underline;">{url}</a></p>
      </td>
    </tr></table>
  </td>
</tr>'''


def dom_row(i, a):
    n = i + 1
    t = esc(a.get('title', ''))
    url = esc(a.get('url', '#'))
    src = esc(a.get('source', ''))
    cat = esc(a.get('category', '其他'))
    summary = esc(a.get('summary', '') or '暂无摘要')
    num = f"{n:02d}"
    return f'''<tr>
  <td style="padding:20px 22px; border-bottom:1px solid #ecebe6; border-left:4px solid #c8102e; background:#ffffff;">
    <table cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
      <td style="width:34px; vertical-align:top; padding-top:2px;">
        <table cellpadding="0" cellspacing="0" border="0"><tr>
          <td align="center" style="background:#c8102e; color:#ffffff; font-family:Georgia,'Times New Roman',serif; font-size:12px; font-weight:700; letter-spacing:0.5px; padding:5px 7px;">{num}</td>
        </tr></table>
      </td>
      <td style="padding-left:14px;">
        <p style="margin:0 0 7px 0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei','SimHei',sans-serif; font-size:15.5px; font-weight:700; line-height:1.5; color:#1a1a2e;">
          {t}
        </p>
        <p style="margin:0 0 9px 0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif; font-size:11px; color:#8a8f9a; letter-spacing:0.3px;">{cat} <span style="color:#d5d4cf; padding:0 6px;">|</span> {src}</p>
        <p style="margin:0 0 6px 0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei','SimHei',sans-serif; font-size:13px; color:#4b5563; line-height:1.8;">{summary}</p>
        <p style="margin:0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif; font-size:11px; line-height:1.5; word-break:break-all;">🔗 原文链接：<a href="{url}" style="color:#c8102e; text-decoration:underline;">{url}</a></p>
      </td>
    </tr></table>
  </td>
</tr>'''


def diplo_row(i, d):
    n = i + 1
    country = esc(d.get('country', ''))
    etype = esc(d.get('event_type', ''))
    headline = esc(d.get('headline', ''))
    mod = esc(d.get('module', ''))
    person = esc(d.get('person', ''))
    date = esc(d.get('date', ''))
    desc = esc(d.get('description', ''))
    num = f"{n:02d}"
    title = headline or (f'{country} · {etype}' if (country or etype) else person)
    return f'''<tr>
  <td style="padding:20px 22px; border-bottom:1px solid #ecebe6; border-left:4px solid #0d9488; background:#ffffff;">
    <table cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
      <td style="width:34px; vertical-align:top; padding-top:2px;">
        <table cellpadding="0" cellspacing="0" border="0"><tr>
          <td align="center" style="background:#0d9488; color:#ffffff; font-family:Georgia,'Times New Roman',serif; font-size:12px; font-weight:700; letter-spacing:0.5px; padding:5px 7px;">{num}</td>
        </tr></table>
      </td>
      <td style="padding-left:14px;">
        <p style="margin:0 0 7px 0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei','SimHei',sans-serif; font-size:15.5px; font-weight:700; line-height:1.5;">{title}</p>
        <p style="margin:0 0 9px 0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif; font-size:11px; color:#8a8f9a; letter-spacing:0.3px;">{mod} <span style="color:#d5d4cf; padding:0 6px;">|</span> {person} <span style="color:#d5d4cf; padding:0 6px;">|</span> {date}</p>
        <p style="margin:0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei','SimHei',sans-serif; font-size:13px; color:#4b5563; line-height:1.8;">{desc}</p>
      </td>
    </tr></table>
  </td>
</tr>'''


def build_email_html(intl, dom, diplo=None):
    diplo = diplo or []
    total = len(intl) + len(dom)
    weekday = WEEKDAY_CN[NOW.weekday()]
    month_num = NOW.month
    day_num = NOW.day
    date_str = f'{NOW.year} 年 {month_num} 月 {day_num} 日'
    vol_str = f'Vol. {month_num} &middot; No. {day_num}'

    intl_rows = '\n'.join(intl_row(i, a) for i, a in enumerate(intl))
    dom_rows = '\n'.join(dom_row(i, a) for i, a in enumerate(dom))
    diplo_rows = '\n'.join(diplo_row(i, d) for i, d in enumerate(diplo))
    diplo_block = ''
    if diplo:
        diplo_block = f'''
  <!-- ===== 使领馆动态 ===== -->
  <tr>
    <td style="padding:30px 28px 14px; background:#ffffff;">
      <table cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
        <td style="border-bottom:2px solid #0d9488; padding-bottom:9px; font-size:19px; font-weight:700; color:#0d9488; letter-spacing:0.5px;">使领馆动态</td>
        <td align="right" style="border-bottom:2px solid #0d9488; padding-bottom:9px; font-family:Georgia,'Times New Roman',serif; font-style:italic; font-size:12px; color:#9aa0ac; white-space:nowrap;">{len(diplo)} updates</td>
      </tr></table>
      <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:16px; border-top:1px solid #ecebe6;">
{diplo_rows}
      </table>
    </td>
  </tr>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="UTF-8">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="x-apple-disable-message-reformatting">
<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch><o:AllowPNG/></o:OfficeDocumentSettings></xml></noscript><![endif]-->
<title>信息日报 · 每日早报</title>
</head>
<body style="margin:0; padding:0; background:#f5f4f0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei','SimHei',sans-serif; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%;">
<!--[if mso]><table role="presentation" cellpadding="0" cellspacing="0" border="0" width="660" align="center"><tr><td><![endif]-->
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width:660px; margin:0 auto; background:#f5f4f0;">

  <!-- ===== 顶部 报纸刊头 masthead ===== -->
  <tr>
    <td style="padding:32px 28px 18px; background:#ffffff;">
      <table cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
        <td align="center" style="font-family:'Songti SC','STSong','SimSun',Georgia,'Times New Roman',serif; font-size:34px; font-weight:700; color:#1a1a2e; letter-spacing:8px; line-height:1.25;">信息日报</td>
      </tr></table>
      <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:5px;"><tr>
        <td align="center" style="font-family:Georgia,'Times New Roman',serif; font-style:italic; font-size:10.5px; color:#9aa0ac; letter-spacing:3px;">DAILY INFORMATION BRIEF</td>
      </tr></table>
      <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:18px;"><tr>
        <td style="height:3px; font-size:0; line-height:3px; background:#c8102e;">&nbsp;</td>
      </tr></table>
      <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:3px;"><tr>
        <td style="height:1px; font-size:0; line-height:1px; background:#1a1a2e;">&nbsp;</td>
      </tr></table>
      <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:16px;"><tr>
        <td align="center" style="font-family:'Songti SC','STSong','SimSun',Georgia,'Times New Roman',serif; font-size:18px; font-weight:700; color:#1a1a2e; letter-spacing:2px;">{date_str} &middot; {weekday}</td>
      </tr></table>
      <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:6px;"><tr>
        <td align="center" style="font-family:Georgia,'Times New Roman',serif; font-style:italic; font-size:11px; color:#9aa0ac; letter-spacing:1px;">{vol_str} &middot; {total} 条精选</td>
      </tr></table>
    </td>
  </tr>
  <tr><td style="height:18px; line-height:18px; font-size:0; background:#f5f4f0;">&nbsp;</td></tr>

  <!-- ===== 引语 ===== -->
  <tr>
    <td style="padding:20px 28px 6px; background:#ffffff; border-left:3px solid #c8102e;">
      <p style="margin:0 0 8px 0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif; font-size:11.5px; color:#8a8f9a; letter-spacing:0.5px;">点击标题可跳转原文 &middot; 底部入口进入信息看板</p>
      <p style="margin:0; font-size:13.5px; color:#374151; line-height:1.85;">每日追踪<b style="color:#c8102e;">中美关系</b>、<b style="color:#c8102e;">地缘政治</b>、<b style="color:#c8102e;">经贸制裁</b>、<b style="color:#c8102e;">AI 科技</b>等国际国内重大动向。以下为今日较高重要性新闻速览。</p>
    </td>
  </tr>

  <!-- ===== 国际要闻 ===== -->
  <tr>
    <td style="padding:30px 28px 14px; background:#ffffff;">
      <table cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
        <td style="border-bottom:2px solid #1e3a8a; padding-bottom:9px; font-size:19px; font-weight:700; color:#1e3a8a; letter-spacing:0.5px;">国际要闻</td>
        <td align="right" style="border-bottom:2px solid #1e3a8a; padding-bottom:9px; font-family:Georgia,'Times New Roman',serif; font-style:italic; font-size:12px; color:#9aa0ac; white-space:nowrap;">{len(intl)} stories</td>
      </tr></table>
      <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:16px; border-top:1px solid #ecebe6;">
{intl_rows}
      </table>
    </td>
  </tr>

  <!-- ===== 国内要闻 ===== -->
  <tr>
    <td style="padding:30px 28px 14px; background:#ffffff;">
      <table cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
        <td style="border-bottom:2px solid #c8102e; padding-bottom:9px; font-size:19px; font-weight:700; color:#c8102e; letter-spacing:0.5px;">国内要闻</td>
        <td align="right" style="border-bottom:2px solid #c8102e; padding-bottom:9px; font-family:Georgia,'Times New Roman',serif; font-style:italic; font-size:12px; color:#9aa0ac; white-space:nowrap;">{len(dom)} stories</td>
      </tr></table>
      <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:16px; border-top:1px solid #ecebe6;">
{dom_rows}
      </table>
    </td>
  </tr>
{diplo_block}
  <!-- ===== 看板入口 ===== -->
  <tr><td style="height:16px; line-height:16px; font-size:0; background:#ffffff;">&nbsp;</td></tr>
  <tr>
    <td style="padding:0 28px 28px; background:#ffffff;">
      <table cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
        <td width="33%" style="padding-right:8px; vertical-align:top;">
          <table cellpadding="0" cellspacing="0" border="0" width="100%" style="border:1px solid #e5e7eb; border-left:3px solid #1e3a8a; background:#ffffff;"><tr>
            <td align="center" style="padding:18px 8px;">
              <a href="https://iranorawahaha.github.io/international-news-kb/international-news.html" target="_blank" style="display:block; text-decoration:none; color:#1e3a8a; line-height:1.6;">
                <span style="font-size:22px;">&#127758;</span><br>
                <span style="font-size:12px; font-weight:700;">国际看板</span>
              </a>
            </td>
          </tr></table>
        </td>
        <td width="33%" style="padding-right:8px; vertical-align:top;">
          <table cellpadding="0" cellspacing="0" border="0" width="100%" style="border:1px solid #e5e7eb; border-left:3px solid #c8102e; background:#ffffff;"><tr>
            <td align="center" style="padding:18px 8px;">
              <a href="https://iranorawahaha.github.io/international-news-kb/china-news.html" target="_blank" style="display:block; text-decoration:none; color:#c8102e; line-height:1.6;">
                <span style="font-size:22px;">&#127464;&#127475;</span><br>
                <span style="font-size:12px; font-weight:700;">国内看板</span>
              </a>
            </td>
          </tr></table>
        </td>
        <td width="33%" style="vertical-align:top;">
          <table cellpadding="0" cellspacing="0" border="0" width="100%" style="border:1px solid #e5e7eb; border-left:3px solid #7c3aed; background:#ffffff;"><tr>
            <td align="center" style="padding:18px 8px;">
              <a href="https://iranorawahaha.github.io/international-news-kb/ai-news.html" target="_blank" style="display:block; text-decoration:none; color:#7c3aed; line-height:1.6;">
                <span style="font-size:22px;">&#129302;</span><br>
                <span style="font-size:12px; font-weight:700;">AI 看板</span>
              </a>
            </td>
          </tr></table>
        </td>
      </tr></table>
    </td>
  </tr>

  <!-- ===== 底部 ===== -->
  <tr>
    <td align="center" style="padding:22px 20px; background:#1a1a2e; font-size:11px; color:#8f95a3; line-height:1.9;">
      <p style="margin:0 0 5px 0;" dir="ltr">&#128238; 信息日报 &middot; 每日自动生成 &middot; 仅供参考交流</p>
      <p style="margin:0;" dir="ltr"><a href="https://iranorawahaha.github.io/international-news-kb/" target="_blank" style="color:#a0a5b0; text-decoration:none;">irano...haha.github.io/international-news-kb</a></p>
    </td>
  </tr>
</table>
<!--[if mso]></td></tr></table><![endif]-->
</body>
</html>'''
    return html


def send_email(html_body, total, to_email=None):
    if to_email is None:
        to_email = TO_EMAIL
    subject = Header(f'信息日报-{TODAY}', 'utf-8')
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = formataddr((str(Header('信息日报', 'utf-8')), SMTP_USER))
    msg['To'] = to_email
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, [to_email], msg.as_string())
        print(f'✅ 邮件已发送 → {to_email}')
        return True
    except Exception as e:
        print(f'❌ 发送失败: {e}')
        return False


def generate_pdf(html_body, pdf_path):
    """将精美版日报 HTML 渲染为 A4 PDF（保留超链接，供微信发送）"""
    import tempfile

    # PDF 专用：加宽内容区至 730px 并收窄页边距，减少 A4 两侧留白（仅影响 PDF，不影响邮件版）
    pdf_html = html_body.replace('max-width:660px', 'max-width:730px')
    # PDF 专用：字号整体放大，提升阅读体验（仅影响 PDF，不影响邮件版）
    pdf_html = pdf_html.replace('font-size:15.5px;', 'font-size:18px;')  # 新闻标题
    pdf_html = pdf_html.replace('font-size:13px;', 'font-size:15px;')    # 摘要
    pdf_html = pdf_html.replace('font-size:13.5px;', 'font-size:15px;')  # 导语
    pdf_html = pdf_html.replace('font-size:11.5px;', 'font-size:13px;')  # 英文标题
    pdf_html = pdf_html.replace('font-size:11px;', 'font-size:12px;')    # 来源/链接行
    pdf_html = pdf_html.replace('font-size:19px;', 'font-size:22px;')    # 板块标题
    pdf_html = pdf_html.replace('font-size:34px;', 'font-size:36px;')    # 报头大标题

    with tempfile.NamedTemporaryFile('w', suffix='.html', encoding='utf-8', delete=False) as f:
        f.write(pdf_html)
        tmp_html = f.name

    node_script = r'''
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 1600 } });
  await page.goto('file://' + process.argv[1], { waitUntil: 'networkidle', timeout: 60000 });
  await page.pdf({
    path: process.argv[2],
    format: 'A4',
    printBackground: true,
    margin: { top: '12mm', bottom: '12mm', left: '8mm', right: '8mm' },
    displayHeaderFooter: false
  });
  await browser.close();
  console.log('PDF_OK');
})();
'''
    node_bin = "/Users/xiaoxiao/.workbuddy/binaries/node/versions/22.22.2/bin/node"
    if not os.path.exists(node_bin):
        node_bin = "node"
    env = dict(os.environ)
    env["NODE_PATH"] = "/Users/xiaoxiao/.workbuddy/binaries/node/workspace/node_modules"

    try:
        r = subprocess.run(
            [node_bin, '-e', node_script, tmp_html, pdf_path],
            capture_output=True, text=True, env=env, timeout=120,
        )
        os.unlink(tmp_html)
        if 'PDF_OK' in r.stdout:
            print(f'✅ PDF 已生成: {pdf_path}')
            return True
        print(f'❌ PDF 生成失败: {r.stdout} {r.stderr}')
        return False
    except Exception as e:
        os.unlink(tmp_html)
        print(f'❌ PDF 生成异常: {e}')
        return False


def main():
    preview = '--preview' in sys.argv
    do_pdf = '--pdf' in sys.argv
    to_emails = []
    for i, arg in enumerate(sys.argv):
        if arg == '--to' and i + 1 < len(sys.argv):
            to_emails = [e.strip() for e in sys.argv[i + 1].split(',') if e.strip()]

    # 数据就绪门禁：发送/生成PDF 模式下先确保国际看板今日已刷新；预览模式仅提示
    if not preview:
        print('🔍 检查看板数据是否就绪...')
        ensure_data_ready()
    else:
        cnt = count_intl_today()
        if cnt < INTL_MIN_TODAY:
            print(f'⚠️ 国际看板今日仅 {cnt} 条，可能尚未刷新完成；正式发送时会自动补跑/等待。')

    intl, dom = load_articles()
    ov = load_override()
    if ov and ov.get('skip_diplo'):
        diplo = []
    else:
        diplo = load_diplo_updates()
        if ov:
            diplo_exclude = set(ov.get('diplo_exclude') or [])
            if diplo_exclude:
                diplo = [d for i, d in enumerate(diplo) if (i + 1) not in diplo_exclude]
    total = len(intl) + len(dom)
    print(f'📰 精美 Outlook 版生成中... {TODAY}')
    print(f'   🌍 国际: {len(intl)} 篇 | 🇨🇳 国内: {len(dom)} 篇 | 🏛 使领馆: {len(diplo)} 条动态')

    html = build_email_html(intl, dom, diplo)
    with open(OUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'✅ HTML 已生成: {OUT_HTML}')

    if do_pdf:
        os.makedirs(PDF_DIR, exist_ok=True)
        pdf_path = os.path.join(PDF_DIR, f'信息日报-{TODAY}.pdf')
        generate_pdf(html, pdf_path)
        return 0

    if not preview:
        if not to_emails:
            to_emails = list(DEFAULT_RECIPIENTS)
        print(f'   📬 收件人 {len(to_emails)} 个，开始逐个发送（间隔 {SEND_DELAY:.0f}s）...')
        ok = 0
        failed = []
        for idx, em in enumerate(to_emails, 1):
            sent = False
            for attempt in range(1, MAX_RETRIES + 1):
                if attempt > 1:
                    print(f'   ⏳ {em} 发送失败，等待 {RETRY_DELAY}s 后重试（第 {attempt} 次）...')
                    time.sleep(RETRY_DELAY)
                if send_email(html, total, em):
                    ok += 1
                    sent = True
                    break
            if not sent:
                failed.append(em)
            if idx < len(to_emails):
                time.sleep(SEND_DELAY)
        print(f'   ✅ 成功 {ok}/{len(to_emails)} 封')
        if failed:
            print('   ❌ 失败收件人: ' + ', '.join(failed))
            return 1
        return 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
