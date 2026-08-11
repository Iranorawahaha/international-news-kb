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


def load_articles(intl_exclude=None, dom_exclude=None):
    """加载国际高优 + 国内≥80分
    intl_exclude / dom_exclude: 排除的位置索引集合（从1开始）
    """
    intl_exclude = intl_exclude or set()
    dom_exclude = dom_exclude or set()

    with open(INTL_DATA) as f:
        nd = json.load(f)
    a10 = nd['archive'].get(TODAY, nd['archive'].get(max(nd['archive'].keys(), key=lambda k: k), []))
    intl_full = [a for a in a10 if a.get('priority_score', 0) >= INTL_MIN_SCORE]
    intl = [a for i, a in enumerate(intl_full) if (i + 1) not in intl_exclude]
    intl_total = sum(len(v) for v in nd['archive'].values())
    intl_today = len(nd['archive'].get(TODAY, []))

    with open(CHINA_DATA) as f:
        cd = json.load(f)
    c10 = cd['archive'].get(TODAY, cd['archive'].get(max(cd['archive'].keys(), key=lambda k: k), []))
    dom_full = [a for a in c10 if a.get('priority_score', 0) >= DOM_MIN_SCORE]
    dom = [a for i, a in enumerate(dom_full) if (i + 1) not in dom_exclude]
    dom_total = len(c10)

    return intl, dom, intl_today, intl_total, dom_total


def esc(text):
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_html(intl, dom, intl_today, intl_total, dom_total):
    """生成 预览用 HTML（web 浏览器查看，保留设计感）"""

    day_num = NOW.day
    month_num = NOW.month
    weekday = WEEKDAY_CN[NOW.weekday()]
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
      <div class="card-meta">{src}</div>
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
      <div class="card-meta">{cat} <span class="sep">|</span> {src}</div>
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


def build_email_html(intl, dom, intl_today, dom_total):
    """生成 Outlook 兼容版 邮件 HTML（table 布局 + 内联样式 + 系统字体）
    
    与 build_html() 的区别：
    - <table> 替代 flexbox/grid 布局
    - 所有 CSS 内联（style="" 属性），不依赖 <style> 块
    - 系统字体栈（无 Google Fonts）
    - 无 border-radius / box-shadow / gap / rgba 透明度
    - mso 兼容的背景色和边框
    """
    total = len(intl) + len(dom)
    weekday = WEEKDAY_CN[NOW.weekday()]
    month_num = NOW.month
    day_num = NOW.day
    date_str = f'{NOW.year} 年 {month_num} 月 {day_num} 日'
    vol_str = f'Vol. {month_num} &middot; No. {day_num}'

    def intl_card_ol(i, a):
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
        return f'''              <!-- Card {num} -->
              <tr>
                <td style="padding:16px 18px; border-bottom:1px solid #e5e7eb; border-left:4px solid #1e3a8a; background:#ffffff;">
                  <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                      <td style="width:32px; vertical-align:top;">
                        <table cellpadding="0" cellspacing="0" border="0"><tr>
                          <td style="background:#1e3a8a; color:#ffffff; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif; font-size:12px; font-weight:700; padding:4px 8px;">{num}</td>
                        </tr></table>
                      </td>
                      <td style="padding-left:12px;">
                        <p style="margin:0 0 4px 0; font-family:Georgia,'Times New Roman',serif; font-size:12px; font-style:italic; color:#9ca3af; line-height:1.4;">{te}</p>
                        <p style="margin:0 0 6px 0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei','SimHei',sans-serif; font-size:16px; font-weight:700; line-height:1.5;">
                          <a href="{url}" target="_blank" style="color:#1a1a2e; text-decoration:none;">{tz}</a>
                        </p>
                        <p style="margin:0 0 8px 0; font-size:11px; color:#6b7280;">{src}</p>
                        <p style="margin:0; font-family:'PingFang SC','Microsoft YaHei','SimHei',sans-serif; font-size:13px; color:#4b5563; line-height:1.8;">{summary}</p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>'''

    def dom_card_ol(i, a):
        n = i + 1
        t = esc(a.get('title', ''))
        url = esc(a.get('url', '#'))
        src = esc(a.get('source', ''))
        cat = esc(a.get('category', '其他'))
        summary = esc(a.get('summary', '') or '暂无摘要')
        num = f"{n:02d}"
        return f'''              <!-- Card {num} -->
              <tr>
                <td style="padding:16px 18px; border-bottom:1px solid #e5e7eb; border-left:4px solid #dc2626; background:#ffffff;">
                  <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                      <td style="width:32px; vertical-align:top;">
                        <table cellpadding="0" cellspacing="0" border="0"><tr>
                          <td style="background:#dc2626; color:#ffffff; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif; font-size:12px; font-weight:700; padding:4px 8px;">{num}</td>
                        </tr></table>
                      </td>
                      <td style="padding-left:12px;">
                        <p style="margin:0 0 6px 0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei','SimHei',sans-serif; font-size:16px; font-weight:700; line-height:1.5;">
                          <a href="{url}" target="_blank" style="color:#1a1a2e; text-decoration:none;">{t}</a>
                        </p>
                        <p style="margin:0 0 8px 0; font-size:11px; color:#6b7280;">{cat} <span style="color:#d4d4d8; margin:0 6px;">|</span> {src}</p>
                        <p style="margin:0; font-family:'PingFang SC','Microsoft YaHei','SimHei',sans-serif; font-size:13px; color:#4b5563; line-height:1.8;">{summary}</p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>'''

    intl_rows = '\n'.join(intl_card_ol(i, a) for i, a in enumerate(intl))
    dom_rows = '\n'.join(dom_card_ol(i, a) for i, a in enumerate(dom))

    # ※※※ Outlook 兼容邮件 HTML（全内联样式 + table 布局）※※※
    email_html = f'''<!DOCTYPE html>
<html lang="zh-CN" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="UTF-8">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
<title>Ira 信息看板 · 每日早报</title>
</head>
<body style="margin:0; padding:0; background:#f5f4f0; font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei','SimHei',sans-serif; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%;">
  <!--[if mso]><table role="presentation" cellpadding="0" cellspacing="0" border="0" width="660" align="center"><tr><td><![endif]-->
  <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width:660px; margin:0 auto;">
    
    <!-- 顶部 -->
    <tr>
      <td style="padding:24px 20px 20px; background:#1a1a2e;">
        <table cellpadding="0" cellspacing="0" border="0" width="100%">
          <tr>
            <td style="font-family:Georgia,'Times New Roman','Noto Serif SC',serif; font-size:22px; font-weight:700; color:#ffffff;">
              Ira <span style="font-weight:500; font-family:'PingFang SC','Microsoft YaHei','SimHei',sans-serif;">信息看板</span>
            </td>
            <td align="right" style="font-family:Georgia,serif; font-style:italic; font-size:12px; color:#9ca3af;">{vol_str}</td>
          </tr>
        </table>
        <table cellpadding="0" cellspacing="0" border="0" style="margin-top:12px;">
          <tr>
            <td style="background:#b91c1c; font-family:Georgia,serif; font-size:28px; font-weight:900; color:#ffffff; padding:6px 14px; line-height:1;">{day_num}</td>
            <td style="padding-left:10px; color:#ffffff;">
              <table cellpadding="0" cellspacing="0" border="0">
                <tr><td style="font-size:15px; font-weight:700; padding-bottom:2px;">{weekday}</td></tr>
                <tr><td style="font-size:11px; color:#a0a5b0;">{date_str}</td></tr>
              </table>
            </td>
            <td width="100%" align="right" style="font-family:Georgia,serif; font-size:12px; color:#a0a5b0; font-style:italic;">{total} 条精选</td>
          </tr>
        </table>
      </td>
    </tr>

    <tr><td style="height:4px; background:#b91c1c;"></td></tr>

    <!-- 引语 -->
    <tr>
      <td style="padding:20px 20px 28px; background:#ffffff; border-left:3px solid #b91c1c; margin-left:20px;">
        <p style="margin:0; font-size:14px; color:#374151; line-height:1.85;">每日追踪中美关系、地缘政治、经贸制裁、AI 科技等国际国内重大动向。以下为较高重要性新闻速览。</p>
      </td>
    </tr>

    <!-- ===== 国际 ===== -->
    <tr>
      <td style="padding:32px 20px 0; background:#ffffff;">
        <table cellpadding="0" cellspacing="0" border="0" width="100%">
          <tr>
            <td style="border-bottom:2px solid #1e3a8a; padding-bottom:8px; font-size:20px; font-weight:700; color:#1e3a8a;">国际要闻</td>
            <td align="right" style="border-bottom:2px solid #1e3a8a; padding-bottom:8px; font-family:Georgia,serif; font-style:italic; font-size:12px; color:#9ca3af;">{len(intl)} stories</td>
          </tr>
        </table>
        <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:16px;">
{intl_rows}
        </table>
      </td>
    </tr>

    <!-- ===== 国内 ===== -->
    <tr>
      <td style="padding:32px 20px 0; background:#ffffff;">
        <table cellpadding="0" cellspacing="0" border="0" width="100%">
          <tr>
            <td style="border-bottom:2px solid #dc2626; padding-bottom:8px; font-size:20px; font-weight:700; color:#dc2626;">国内要闻</td>
            <td align="right" style="border-bottom:2px solid #dc2626; padding-bottom:8px; font-family:Georgia,serif; font-style:italic; font-size:12px; color:#9ca3af;">{len(dom)} stories</td>
          </tr>
        </table>
        <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:16px;">
{dom_rows}
        </table>
      </td>
    </tr>

    <!-- 看板入口 -->
    <tr><td style="height:20px;"></td></tr>
    <tr>
      <td style="padding:0 20px;">
        <table cellpadding="0" cellspacing="0" border="0" width="100%">
          <tr>
            <td width="33%" style="padding-right:8px; vertical-align:top;">
              <a href="https://iranorawahaha.github.io/international-news-kb/international-news.html" target="_blank" style="text-decoration:none;">
                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                  <tr><td style="padding:14px 10px; background:#ffffff; border:1px solid #e5e7eb; border-left:3px solid #1e3a8a; text-align:center;">
                    <p style="margin:0 0 4px 0; font-size:22px;">&#127758;</p>
                    <p style="margin:0; font-size:12px; font-weight:700; color:#1e3a8a;">国际看板</p>
                  </td></tr>
                </table>
              </a>
            </td>
            <td width="33%" style="padding-right:8px; vertical-align:top;">
              <a href="https://iranorawahaha.github.io/international-news-kb/china-news.html" target="_blank" style="text-decoration:none;">
                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                  <tr><td style="padding:14px 10px; background:#ffffff; border:1px solid #e5e7eb; border-left:3px solid #dc2626; text-align:center;">
                    <p style="margin:0 0 4px 0; font-size:22px;">&#127464;&#127475;</p>
                    <p style="margin:0; font-size:12px; font-weight:700; color:#dc2626;">国内看板</p>
                  </td></tr>
                </table>
              </a>
            </td>
            <td width="33%" style="vertical-align:top;">
              <a href="https://iranorawahaha.github.io/international-news-kb/ai-news.html" target="_blank" style="text-decoration:none;">
                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                  <tr><td style="padding:14px 10px; background:#ffffff; border:1px solid #e5e7eb; border-left:3px solid #7c3aed; text-align:center;">
                    <p style="margin:0 0 4px 0; font-size:22px;">&#129302;</p>
                    <p style="margin:0; font-size:12px; font-weight:700; color:#7c3aed;">AI 看板</p>
                  </td></tr>
                </table>
              </a>
            </td>
          </tr>
        </table>
      </td>
    </tr>

    <!-- 底部 -->
    <tr><td style="height:20px;"></td></tr>
    <tr>
      <td align="center" style="padding:20px; background:#1a1a2e; font-size:11px; color:#9ca3af; line-height:1.8;">
        <p style="margin:0 0 6px 0;" dir="ltr">&#128238; Ira 信息看板 &middot; 每日自动生成 &middot; 仅供参考交流</p>
        <p style="margin:0;" dir="ltr"><a href="https://iranorawahaha.github.io/international-news-kb/" target="_blank" style="color:#9ca3af;">irano...haha.github.io/international-news-kb</a></p>
      </td>
    </tr>
  </table>
  <!--[if mso]></td></tr></table><![endif]-->
</body>
</html>'''
    return email_html


def send_email(html_body, intl_count, dom_count, to_email=None):
    """通过 QQ SMTP 发送邮件"""
    from email.header import Header

    if to_email is None:
        to_email = TO_EMAIL

    total = intl_count + dom_count
    subject = Header(f'Ira 早报 · {TODAY} · {total}条精选', 'utf-8')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f'Ira Daily Brief <{SMTP_USER}>'
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


def parse_exclude(arg):
    """解析 --exclude-intl/--exclude-dom 参数，如 '1,2,4' → {1,2,4}"""
    if not arg:
        return set()
    return set(int(x.strip()) for x in arg.split(',') if x.strip())


def main():
    preview = '--preview' in sys.argv
    do_send = '--send' in sys.argv

    # 解析可选参数
    intl_exclude = set()
    dom_exclude = set()
    to_email = None
    for i, arg in enumerate(sys.argv):
        if arg == '--exclude-intl' and i + 1 < len(sys.argv):
            intl_exclude = parse_exclude(sys.argv[i+1])
        if arg == '--exclude-dom' and i + 1 < len(sys.argv):
            dom_exclude = parse_exclude(sys.argv[i+1])
        if arg == '--to' and i + 1 < len(sys.argv):
            to_email = sys.argv[i+1]

    if not preview and not do_send:
        print('用法: --preview (预览) / --send (发送) / --preview --send (预览+发送)')
        print('      --exclude-intl 1,2,4   (排除国际第N条)')
        print('      --exclude-dom 1,2,6    (排除国内第N条)')
        print('      --to user@example.com  (自定义收件人)')
        return 1

    print(f'📰 Ira 早报生成中... {TODAY}')
    if to_email:
        print(f'   📬 收件人: {to_email}')
    if intl_exclude:
        print(f'   ⛔ 国际排除位置: {sorted(intl_exclude)}')
    if dom_exclude:
        print(f'   ⛔ 国内排除位置: {sorted(dom_exclude)}')

    intl, dom, intl_today, intl_total, dom_total = load_articles(intl_exclude, dom_exclude)
    print(f'   🌍 国际: {len(intl)} 篇高优 (今日新增 {intl_today} / 总 {intl_total})')
    print(f'   🇨🇳 国内: {len(dom)} 篇 ≥{DOM_MIN_SCORE}分 (今日 {dom_total})')

    # 预览用网页版模板（保留设计感），发送用 Outlook 兼容版
    if preview:
        html = build_html(intl, dom, intl_today, intl_total, dom_total)
        with open(PREVIEW_HTML, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'✅ 预览已生成: {PREVIEW_HTML}')

    sent = False
    if do_send:
        email_html = build_email_html(intl, dom, intl_today, dom_total)
        sent = send_email(email_html, len(intl), len(dom), to_email)

    save_log(len(intl), len(dom), sent)

    return 0 if not do_send or sent else 1


if __name__ == '__main__':
    sys.exit(main())
