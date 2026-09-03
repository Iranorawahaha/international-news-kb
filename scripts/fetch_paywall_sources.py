#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际新闻看板 - 反爬/付费墙四家信源替代通道采集器 V1.0 (2026-09-03)
=====================================================================

【背景 / 根因】
  路透社(reuters.com) 官网 curl/WebFetch 恒 401、华尔街日报(wsj.com) 401、
  Politico(politico.com) 403、华盛顿邮报(washingtonpost.com) 000(超时)。
  —— 用户浏览器登录态对终端/代理无效，官网直抓不可行，导致这四家每天缺失。

【攻克方案 = 替代通道】
  经 2026-09-03 实测验证的稳定通道（走代理 127.0.0.1:7890 均 200 可达）：
    ① 统一线索发现器：Google News RSS `site:<domain> when:2d`
       → 稳定返回四家信源的最新稿【标题 + 真实发布时间 + 来源署名】
       (news.google.com/rss/search?q=site:reuters.com%20when:2d&hl=en-US&gl=US&ceid=US:en)
    ② 华尔街日报 → TradingView (tradingview.com/news/) 直抓 Dow Jones Newswires 电头
       (页面内嵌 JSON: title/storyPath/published 时间戳, provider=dow-jones)
    ③ Politico → politico.eu 官网直抓 (200 可达, 真实 URL politico.eu/article/...)
    ④ 路透社 → Yahoo News (news.yahoo.com 聚合路透电头) + 专业转载站
       (sedaily.com / asiae.co.kr / koreatimes.co.kr / livemint.com / ibtimes.com)
    ⑤ 华盛顿邮报 → Google News RSS 线索 + WebSearch 找转载

【用法】
  python3 scripts/fetch_paywall_sources.py              # 输出四家候选清单(涉华过滤)
  python3 scripts/fetch_paywall_sources.py --all        # 不过滤, 输出全部最新稿
  python3 scripts/fetch_paywall_sources.py --json       # 输出 JSON 到 stdout

【输出字段】
  title(title_zh占位)/source(中文名)/date/pubDate/gn_link(Google News线索)/channel(通道)
  真实 URL 由 agent 用 WebSearch 按标题精确定位转载(或直接通道抓取), 防编造。
"""
import sys, re, json, ssl, html, argparse
import urllib.request

PROXY = 'http://127.0.0.1:7890'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'

# 四家信源: domain -> (中文名, Google News site: 查询)
SOURCES = {
    'reuters.com':      ('路透社',   'site:reuters.com'),
    'wsj.com':          ('华尔街日报', 'site:wsj.com'),
    'politico.com':     ('Politico', 'site:politico.com'),
    'washingtonpost.com': ('华盛顿邮报', 'site:washingtonpost.com'),
}

# 涉华/关注领域关键词（用户关注：中美关系/经贸制裁/AI竞争/外交）
CN_KW = ['china', 'chinese', 'beijing', 'xi ', "xi's", 'taiwan', 'hong kong',
         'tariff', 'chip', 'semiconductor', 'ai ', 'artificial intelligence',
         'export control', 'trade', 'sanction', 'biden', 'trump', 'nvidia',
         'huawei', 'h20', 'deepseek', 'openai', 'tsmc', 'asml', 'quantum',
         'u.s.-china', 'us-china', 'us china', 'brics', 'apec', 'g20', 'shanghai']

def _opener():
    proxy = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
    return urllib.request.build_opener(proxy, urllib.request.HTTPSHandler(context=ssl._create_unverified_context()))

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    r = _opener().open(req, timeout=timeout)
    body = r.read().decode('utf-8', 'ignore')
    r.close()
    return body

def _tag(tag, item):
    m = re.search(r'<%s[^>]*>(.*?)</%s>' % (tag, tag), item, re.S)
    return html.unescape(m.group(1)).strip() if m else ''

def fetch_gn_rss(domain, days=2):
    """Google News RSS 线索发现：返回 [{title, date, pubDate, gn_link, source}]"""
    q = f'{SOURCES[domain][1]} when:{days}d'
    url = f'https://news.google.com/rss/search?q={urllib.request.quote(q)}&hl=en-US&gl=US&ceid=US:en'
    xml = fetch(url)
    items = re.findall(r'<item>(.*?)</item>', xml, re.S)
    out = []
    for it in items:
        title = _tag('title', it)
        src = _tag('source', it)
        if ' - ' in title:
            title = title.rsplit(' - ', 1)[0].strip()
        pd = _tag('pubDate', it)
        link = _tag('link', it)
        # 解析日期 YYYY-MM-DD (pubDate 形如 "Wed, 02 Sep 2026 22:57:00 GMT")
        m = re.search(r'(\d{1,2}) (\w{3}) (\d{4})', pd)
        date = ''
        if m:
            mon = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',
                   'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}[m.group(2)]
            date = f"{m.group(3)}-{mon}-{int(m.group(1)):02d}"
        out.append({'title': title, 'date': date, 'pubDate': pd,
                    'gn_link': link, 'source': SOURCES[domain][0],
                    'domain': domain})
    return out

def fetch_tradingview_dowjones():
    """华尔街日报替代通道: TradingView Dow Jones Newswires 电头"""
    body = fetch('https://www.tradingview.com/news/')
    # 内嵌 JSON: {"id":"DJN_DN...","title":"...","storyPath":"/news/...","published":ts,"provider":{"id":"dow-jones"}}
    rows = []
    for m in re.finditer(r'\{"id":"(DJN_DN\d+:\d+)","title":"([^"]{10,180})","storyPath":"([^"]+)".*?"published":(\d+).*?"name":"([^"]+)"', body):
        gid, title, path, ts, provider = m.groups()
        if provider.lower() != 'dow jones newswires':
            continue
        rows.append({'title': html.unescape(title), 'url': f'https://www.tradingview.com{path}',
                     'provider': provider, 'ts': int(ts), 'date': _ts2date(int(ts)),
                     'source': '华尔街日报', 'channel': 'TradingView(DowJones)'})
    return rows

def _ts2date(ts):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d')

def is_relevant(title):
    t = title.lower()
    return any(k in t for k in CN_KW)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--all', action='store_true', help='不过滤涉华关键词, 输出全部')
    ap.add_argument('--json', action='store_true', help='输出 JSON')
    ap.add_argument('--days', type=int, default=2)
    args = ap.parse_args()

    results = []
    for dom in SOURCES:
        try:
            rows = fetch_gn_rss(dom, args.days)
            results.extend(rows)
        except Exception as e:
            print(f'[ERR] {dom}: {e}', file=sys.stderr)

    # 追加 TradingView 直接通道(华尔街日报补充)
    try:
        results.extend(fetch_tradingview_dowjones())
    except Exception as e:
        print(f'[ERR] tradingview: {e}', file=sys.stderr)

    if not args.all:
        results = [r for r in results if is_relevant(r['title'])]

    # 去重(按标题前缀)
    seen = set(); dedup = []
    for r in results:
        k = r['title'][:40].lower()
        if k in seen: continue
        seen.add(k); dedup.append(r)
    results = dedup

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=1))
        return

    print(f'共 {len(results)} 条候选(涉华/关注领域过滤{"关" if not args.all else "开"}):\n')
    for r in results:
        print(f"[{r.get('date','')}] {r['source']:<5} | {r['title'][:70]}")
        if r.get('url'):
            print(f"          URL: {r['url'][:90]}")
        else:
            print(f"          GN:  {r.get('gn_link','')[:70]}")

if __name__ == '__main__':
    main()
