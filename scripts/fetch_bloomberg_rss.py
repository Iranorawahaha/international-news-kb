#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际新闻看板 - 彭博社（Bloomberg）RSS 通道采集器 V1.0 (2026-09-17)
=====================================================================

【背景 / 根因】
  用户反馈"看板长期未见彭博社消息"。2026-09-17 实测定位三层断点：
    ① config.json 有登记（id=bloomberg, enabled=true, pri 17）—— 但日常抓取清单是
       11 源硬编码，彭博从未列入 → 从未主动抓取过
    ② update-news.sh 的 AUTHORITY_ORDER（同题合并权威序）无彭博 → index() else 99
       取最低优先级 → 即便条目进来也会被其他源同题替换/丢弃（已修：插入美联社之后）
    ③ archive retentionDays=7，历史仅 2 条彭博条目（均为 Yahoo/financefeeds 第三方转载）
       是 8-25/8-26，早已滚出窗口
  —— 结论：登记 ≠ 接入，三处须同步。

【通道实测（2026-09-17）】
  ❌ 官网 https://www.bloomberg.com/world → 403 "Are you a robot?"（Cloudflare）；
     直连（不走代理）→ 000。正文/列表抓取通道不存在，严禁反复硬抓。
  ✅ RSS 通道全通（走代理 127.0.0.1:7890，均 HTTP 200）：
     https://feeds.bloomberg.com/{markets|politics|technology|economics|industries}/news.rss
     （wealth 栏目返回 0 条，已弃用）

【RSS 质量（实测 100 条样本）】
  - 图文稿 /news/articles/ 80 条 + 视频稿 /news/videos/ 20 条 → 本脚本默认过滤视频

  - 无摘要仅 2 条（98% 带 description）
  - URL 100% 指向 bloomberg.com 且 100% 含真实日期路径 /YYYY-MM-DD/ → 日期可直接从 URL 取
  - 发布日期集中在近 48h，涉华/中美/AI 相关约 27 条/轮

【产出字段】
  title_en / url / date / summary_en / source(彭博社) / feed / guid
  ⚠️ RSS 只提供英文标题与英文摘要 —— title_zh 与 summary_zh 须由入库流程翻译生成
     （严禁凭 URL 编造内容；摘要须基于 description 原意）。

【用法】
  python3 scripts/fetch_bloomberg_rss.py                # 涉华/关注领域过滤（默认）
  python3 scripts/fetch_bloomberg_rss.py --all          # 不过滤，输出全部图文稿
  python3 scripts/fetch_bloomberg_rss.py --json         # JSON 输出（供入库流程消费）
  python3 scripts/fetch_bloomberg_rss.py --days 2       # 只保留近 N 天的稿（默认 2）
  python3 scripts/fetch_bloomberg_rss.py --no-dedup     # 跳过与池/存档的 URL 去重
"""

import argparse
import html
import json
import os
import re
import ssl
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

PROXY = 'http://127.0.0.1:7890'
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL_PATH = os.path.join(PROJECT_ROOT, 'data', 'news-webfetch.json')
ARCHIVE_PATH = os.path.join(PROJECT_ROOT, 'data', 'news-data.json')

SOURCE_NAME = '彭博社'
TZ_BJ = timezone(timedelta(hours=8))

FEEDS = {
    'politics': 'https://feeds.bloomberg.com/politics/news.rss',
    'technology': 'https://feeds.bloomberg.com/technology/news.rss',
    'economics': 'https://feeds.bloomberg.com/economics/news.rss',
    'markets': 'https://feeds.bloomberg.com/markets/news.rss',
    'industries': 'https://feeds.bloomberg.com/industries/news.rss',
}

# 涉华/关注领域关键词（中美关系 / 经贸制裁 / AI 竞争 / 外交）
# ⚠️ 用词边界正则，避免朴素 substring 的假阳性（实测坑：'ai ' 会命中 'Thai '、
#    'Xi ' 会命中 'Mexico '）—— 9-17 首轮试跑即复现，故改用 \b 定界
CN_KW_PATTERNS = [
    r'\bai\b', r'\bxi\b', r"xi's", r'\bprc\b', r'\bccp\b',
    r'\bchina\b', r'\bchinese\b', r'\bbeijing\b', r'\bshanghai\b', r'\bshenzhen\b',
    r'\btaiwan\b', r'\btaiwanese\b', r'\bhong kong\b', r'\bmacau\b', r'\bmacao\b',
    r'\btariff', r'\bchip', r'\bsemiconductor', r'\bwafer',
    r'artificial intelligence', r'\bexport control', r'\bentity list\b',
    r'\btrade\b', r'\bsanction', r'\bembargo\b', r'\banti-dumping\b',
    r'\btrump\b', r'\bbiden\b', r'\bnvidia\b', r'\bhuawei\b', r'\bh20\b',
    r'\bdeepseek\b', r'\bopenai\b', r'\btsmc\b', r'\basml\b', r'\bquantum\b',
    r'u\.s\.-china', r'us-china', r'\bbrics\b', r'\bapec\b', r'\bg20\b', r'\bg7\b',
    r'\bbyd\b', r'\bcatl\b', r'rare earth', r'\byuan\b', r'\brenminbi\b',
    r'\bmoonshot\b', r'\balibaba\b', r'\btencent\b', r'\bxiaomi\b',
]
CN_KW_RE = re.compile('|'.join(CN_KW_PATTERNS), re.I)


def _opener():
    proxy = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
    return urllib.request.build_opener(
        proxy, urllib.request.HTTPSHandler(context=ssl._create_unverified_context()))


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    r = _opener().open(req, timeout=timeout)
    body = r.read().decode('utf-8', 'ignore')
    r.close()
    return body


def _tag(tag, item):
    m = re.search(r'<%s[^>]*>(.*?)</%s>' % (tag, tag), item, re.S)
    if not m:
        return ''
    raw = m.group(1)
    raw = re.sub(r'^<!\[CDATA\[(.*?)\]\]>$', r'\1', raw.strip(), flags=re.S)
    text = re.sub(r'<[^>]+>', '', raw)
    return html.unescape(text).strip()


def _date_from_url(url):
    """Bloomberg URL 自带日期路径 /YYYY-MM-DD/ —— 最可靠的日期来源"""
    m = re.search(r'/(\d{4}-\d{2}-\d{2})/', url)
    return m.group(1) if m else ''


def _date_from_pubdate(pub):
    """pubDate 形如 'Wed, 17 Sep 2026 09:30:00 +0000' → 转北京时间日期"""
    m = re.search(r'(\d{1,2}) (\w{3}) (\d{4}) (\d{2}):(\d{2}):(\d{2})', pub)
    if not m:
        return ''
    mon = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
           'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}.get(m.group(2))
    if not mon:
        return ''
    try:
        dt = datetime(int(m.group(3)), mon, int(m.group(1)),
                      int(m.group(4)), int(m.group(5)), int(m.group(6)), tzinfo=timezone.utc)
    except ValueError:
        return ''
    return dt.astimezone(TZ_BJ).strftime('%Y-%m-%d')


def load_seen_urls():
    """已入池 / 已存档的 URL 集合（归一化），用于去重"""
    seen = set()

    def _norm(u):
        return (u or '').strip().rstrip('/').lower()

    if os.path.exists(POOL_PATH):
        try:
            for x in json.load(open(POOL_PATH, encoding='utf-8')):
                if isinstance(x, dict) and x.get('url'):
                    seen.add(_norm(x['url']))
        except Exception as e:
            print(f'[WARN] 读取池失败: {e}', file=sys.stderr)
    if os.path.exists(ARCHIVE_PATH):
        try:
            d = json.load(open(ARCHIVE_PATH, encoding='utf-8'))
            for arts in (d.get('archive') or {}).values():
                for a in arts:
                    if a.get('url'):
                        seen.add(_norm(a['url']))
        except Exception as e:
            print(f'[WARN] 读取存档失败: {e}', file=sys.stderr)
    return seen


def fetch_feed(name, url, days):
    """抓取单个 feed，返回图文稿列表（过滤 /videos/）"""
    xml = fetch(url)
    items = re.findall(r'<item>(.*?)</item>', xml, re.S)
    out = []
    cutoff = (datetime.now(TZ_BJ) - timedelta(days=days)).strftime('%Y-%m-%d')
    for it in items:
        link = _tag('link', it)
        title = _tag('title', it)
        if not link or not title:
            continue
        # 过滤视频稿（用户偏好图文资讯，视频条目价值低）
        if '/videos/' in link or link.endswith('-video'):
            continue
        pub = _tag('pubDate', it)
        date = _date_from_url(link) or _date_from_pubdate(pub)
        if not date or date < cutoff:
            continue
        out.append({
            'title_en': title,
            'url': link,
            'date': date,
            'summary_en': _tag('description', it),
            'source': SOURCE_NAME,
            'feed': name,
            'guid': _tag('guid', it),
        })
    return out


def is_relevant(title, summary=''):
    return bool(CN_KW_RE.search(f'{title} {summary}'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--all', action='store_true', help='不过滤涉华关键词，输出全部图文稿')
    ap.add_argument('--json', action='store_true', help='输出 JSON')
    ap.add_argument('--days', type=int, default=2, help='只保留近 N 天（默认 2）')
    ap.add_argument('--no-dedup', action='store_true', help='跳过与池/存档的 URL 去重')
    args = ap.parse_args()

    seen = set() if args.no_dedup else load_seen_urls()
    results, stats = [], {}
    for name, url in FEEDS.items():
        try:
            rows = fetch_feed(name, url, args.days)
            stats[name] = len(rows)
            results.extend(rows)
        except Exception as e:
            stats[name] = f'ERR({type(e).__name__})'
            print(f'[ERR] {name}: {e}', file=sys.stderr)

    # URL 去重（feed 之间可能重复；另剔除已入池/已存档）
    uniq, seen_url = [], set()
    dup_pool = 0
    for r in results:
        u = r['url'].rstrip('/').lower()
        if u in seen_url:
            continue
        seen_url.add(u)
        if u in seen:
            dup_pool += 1
            continue
        uniq.append(r)

    if not args.all:
        uniq = [r for r in uniq if is_relevant(r['title_en'], r['summary_en'])]

    uniq.sort(key=lambda r: (r['date'], r['feed']), reverse=True)

    if args.json:
        print(json.dumps({'stats': stats, 'dup_in_pool': dup_pool, 'items': uniq},
                         ensure_ascii=False, indent=1))
        return

    print(f'📡 彭博社 RSS 采集（近 {args.days} 天 · 已过滤视频稿）')
    print(f'   各栏目: {stats}')
    print(f'   去重后候选 {len(uniq)} 条（已剔除池/存档中已有的 {dup_pool} 条）')
    print(f'   过滤: {"关（全部）" if args.all else "开（涉华/中美/AI/经贸）"}\n')
    for r in uniq:
        print(f"[{r['date']}] {r['feed']:<11} {r['title_en'][:78]}")
        print(f"            {r['url']}")
        if r['summary_en']:
            print(f"            {r['summary_en'][:110]}...")
    print(f'\n合计 {len(uniq)} 条')


if __name__ == '__main__':
    main()
