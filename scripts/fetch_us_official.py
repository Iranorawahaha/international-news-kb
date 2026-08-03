#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_us_official.py — 美国官方信源采集器 V1.3（Ira 信息看板 · 国际新闻扩充）

V1.3 改进：
1. 抓取每个 URL 页面 HTML，提取真实发布日期（"JULY 31, 2026" → "2026-07-31"）
2. 提取页面正文/摘要（替代模板 [官方信源] 发布：标题）
3. 分离 title/title_en（清爽双语结构）
4. 标题占位：title_zh = None（由 9:30 自动任务 WebFetch 工具 + AI 翻译补全）

六大官方信源：
  1. 白宫      https://www.whitehouse.gov/news/             ✅ curl
  2. 国务院    https://www.state.gov/press-releases/        ✅ curl
  3. 财政部    https://home.treasury.gov/news/press-releases ✅ curl
  4. USTR      https://ustr.gov/                             ⚠️ WebFetch
  5. 商务部    https://www.commerce.gov/news/press-releases  ⚠️ WebFetch
  6. 国防部    https://www.defense.gov/News/Press-Releases/  ⚠️ WebFetch

输出:
  - data/us-official.json           curl 站点（含真实日期/摘要）
  - data/us-official-webfetch.json  WebFetch 站点（由自动化任务维护）
  - data/us-official-report.json    信源执行清单
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_FILE = os.path.join(BASE_DIR, "data", "us-official.json")
WEBFETCH_FILE = os.path.join(BASE_DIR, "data", "us-official-webfetch.json")
REPORT_FILE = os.path.join(BASE_DIR, "data", "us-official-report.json")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

CURL_SOURCES = {
    "whitehouse": {
        "name": "白宫",
        "url": "https://www.whitehouse.gov/news/",
        "category": "美国",
        "url_patterns": ["/briefings-statements/", "/presidential-actions/", "/fact-sheets/", "/releases/"],
    },
    "state": {
        "name": "美国国务院",
        "url": "https://www.state.gov/press-releases/",
        "category": "美国",
        "url_patterns": ["/releases/"],
    },
    "treasury": {
        "name": "美国财政部",
        "url": "https://home.treasury.gov/news/press-releases",
        "category": "美国",
        "url_patterns": ["/news/press-releases/"],
    },
}

WEBFETCH_SOURCES = {
    "commerce": {"name": "美国商务部", "url": "https://www.commerce.gov/news/press-releases", "category": "美国"},
    "defense": {"name": "美国国防部(war.gov)", "url": "https://www.defense.gov/News/Press-Releases/", "category": "美国"},
    "ustr": {"name": "美国贸易代表办公室(USTR)", "url": "https://ustr.gov/", "category": "美国"},
}

NAV_WORDS = ["skip to", "menu", "search", "twitter", "facebook", "youtube", "instagram",
             "subscribe", "newsletter", "privacy", "terms", "home", "about us", "contact",
             "careers", "organizational chart", "role of the", "bureau of", "office of the",
             "tax administration", "international affairs", "terrorism and financial",
             "tribal and native", "alcohol and tobacco", "engraving", "fiscal service",
             "internal revenue", "comptroller", "inspector general", "countries &",
             "bureaus &", "the secretary of", "counselor of", "executive secretariat",
             "deputy secretary", "under secretary", "arms control", "aukus", "narcotics",
             "state department home", "president donald", "first lady", "vice president",
             "second lady", "office of management", "office of science", "nominations",
             "presidential actions", "presidential memoranda", "briefings & statements",
             "nominations & appointments", "ratepayer protection", "lab leak",
             "january 6", "arrested: worst", "criminal aliens", "medicaid",
             "executive orders", "365 days of wins", "remarks and statements"]

MONTH_MAP = {
    'january': '01', 'february': '02', 'march': '03', 'april': '04',
    'may': '05', 'june': '06', 'july': '07', 'august': '08',
    'september': '09', 'october': '10', 'november': '11', 'december': '12',
}


def fetch_http(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_links(html, domain, url_patterns):
    items = []
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.S):
        url, text = m.group(1), re.sub(r'<[^>]+>', '', m.group(2)).strip()
        text = re.sub(r'\s+', ' ', text).strip()
        if not text or len(text) < 15:
            continue
        if url.startswith('#') or 'javascript' in url or 'mailto' in url:
            continue
        if not url.startswith('http'):
            url = f'https://{domain}{url}' if url.startswith('/') else url
        if not any(p in url for p in url_patterns):
            continue
        # V1.3.2: 必须包含具体文章路径（日期段或新闻 slug）
        # 排除目录页（如 whitehouse.gov/briefings-statements/ 本身）
        # 规则：URL 必须含 /YYYY/MM/ 日期段 或 文章 slug（letters-digits）
        if not (re.search(r'/(20\d{2})/(0[1-9]|1[0-2])', url) or re.search(r'/\d{3,5}/', url)):
            continue
        # 排除目录归档（如 /2026/july/ 结尾，无文章 slug）
        if re.search(r'/20\d{2}/[a-z]+/?$', url) or re.search(r'/20\d{2}$', url):
            continue
        # 排除 trailing slash 目录页（但允许文章 URL 带 trailing slash，
        # 如白宫 /releases/2026/01/.../prosperity/）
        if url.endswith('/'):
            # 仅当 URL 路径段 ≤ 3 时视为目录页
            path = url.rstrip('/').split('://', 1)[-1].split('/', 1)[-1]  # 去掉域名的路径
            segments = [s for s in path.split('/') if s]
            if len(segments) <= 3:
                continue
        tl = text.lower()
        if any(w in tl for w in NAV_WORDS):
            continue
        items.append((text, url))
    return items


def url_real_date(url):
    """从 URL 路径中提取真实发布日（YYYY-MM-DD）"""
    m = re.search(r'(20\d{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])', url)
    if m:
        return f'{m.group(1)}-{m.group(2)}-{m.group(3)}'
    m2 = re.search(r'/(20\d{2})/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/', url)
    if m2:
        return f'{m2.group(1)}-{m2.group(2)}-{m2.group(3)}'
    m3 = re.search(r'/(20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])/', url)
    if m3:
        return f'{m3.group(1)}-{m3.group(2)}-{m3.group(3)}'
    return None


def extract_page_meta(html, url):
    """从新闻页面 HTML 提取真实发布日期 + 摘要（英文原文）

    Returns: (real_date, summary_en) 失败时 (None, None)
    """
    # 1. 真实发布日期（多种格式）
    real_date = None

    # URL 路径提取（wh.gov/2026/07/31/、state.gov/.../2026/07/.../)
    m_url = re.search(r'/(20\d{2})/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])', url)
    if m_url:
        real_date = f'{m_url.group(1)}-{m_url.group(2)}-{m_url.group(3)}'

    # HTML 页面内的日期（白宫/国务院/财政部常见格式）
    for pat in [
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4})',
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',
        r'<time[^>]+datetime=[\"\'](20\d{2}-\d{2}-\d{2})[\"\']',
        r'发布.*?(\d{4})[年\-](\d{1,2})[月\-](\d{1,2})',
    ]:
        m = re.search(pat, html, re.I)
        if m:
            if len(m.groups()) == 3 and m.group(1).isalpha():
                mo = MONTH_MAP.get(m.group(1).lower())
                if mo:
                    real_date = f'{m.group(3)}-{mo}-{int(m.group(2)):02d}'
                    break
            elif len(m.groups()) == 3 and m.group(1).isdigit():
                real_date = f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'
                break
            elif len(m.groups()) == 1:
                real_date = m.group(1)
                break

    # 2. 摘要（meta description 或第一个 <p> 段落）
    summary = None

    # meta description
    meta = re.search(r'<meta[^>]+(?:name|property)=["\']description["\'][^>]*content=["\']([^"\']{20,500})["\']', html, re.I)
    if meta:
        summary = re.sub(r'\s+', ' ', meta.group(1)).strip()
    else:
        # OG description
        og = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]*content=["\']([^"\']{20,500})["\']', html, re.I)
        if og:
            summary = re.sub(r'\s+', ' ', og.group(1)).strip()

    # 备用：找页面正文（排除页眉/导航）
    if not summary:
        # 删去 nav/header/footer/script/style
        body_html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S)
        body_html = re.sub(r'<style[^>]*>.*?</style>', '', body_html, flags=re.S)
        body_html = re.sub(r'<header[^>]*>.*?</header>', '', body_html, flags=re.S)
        body_html = re.sub(r'<footer[^>]*>.*?</footer>', '', body_html, flags=re.S)
        body_html = re.sub(r'<nav[^>]*>.*?</nav>', '', body_html, flags=re.S)
        # 找 <article> 或 <main> 区域
        article = re.search(r'<article[^>]*>(.*?)</article>', body_html, re.S) or \
                  re.search(r'<main[^>]*>(.*?)</main>', body_html, re.S)
        region = article.group(1) if article else body_html
        # 收集 <p> 段落
        paras = re.findall(r'<p[^>]*>(.*?)</p>', region, re.S)
        for p in paras:
            text = re.sub(r'<[^>]+>', ' ', p).strip()
            text = re.sub(r'\s+', ' ', text)
            if len(text) < 80:
                continue
            tl = text.lower()
            if any(w in tl for w in ['cookie', 'navigation', 'subscribe', 'privacy', 'terms of use']):
                continue
            summary = text[:280] + ('...' if len(text) > 280 else '')
            break

    return real_date, summary


def calc_score(title, url):
    """计算 priority_score 与 summit"""
    text = f"{title} {url}"
    cn = any(k in title for k in ["China", "Chinese", "中国", "Beijing", "Taiwan", "台湾", "TikTok", "Huawei"])
    summit = any(k in title for k in ["President", "Trump", "Xi", "习近平", "Biden", "普京", "Putin"])
    if "Mariana" in title or "Mariana" in url:
        summit = True
    score = 98 if (cn and summit) else (92 if cn else (88 if summit else 75))
    if any(w in text.lower() for w in ["sanction", "tariff", "export control", "forced labor", "301", "embargo"]):
        score = max(score, 90)
    return score, summit


def make_item(title, url, date, source, category, summary_en=None):
    """构造标准官方数据条目（标题字段为英文，title_zh 留给自动任务补全）"""
    score, summit = calc_score(title, url)
    final_date = date or NOW.strftime("%Y-%m-%d")
    return {
        "title": title,                # 英文原标题（保持前端兼容）
        "title_en": title,             # 英文原标题
        "title_zh": None,              # 中文翻译（由 9:30 自动任务补全）
        "summary": summary_en or f"[官方信源] {source} 发布的相关公告",
        "summary_en": summary_en or "",
        "summary_zh": None,            # 留给自动任务补全
        "url": url,
        "date": final_date,
        "source": source,
        "category": category,
        "column": "美国",
        "priority_score": score,
        "is_summit_level": summit,
        "importance": "⭐元首级" if summit else ("高" if score >= 85 else "中"),
        "keywords": [],
        "is_official": True,
        "collectedAt": NOW.strftime("%Y-%m-%d %H:%M:%S"),
        "collection_method": "us_official",
    }


def main():
    report = {"timestamp": NOW.strftime("%Y-%m-%d %H:%M"), "sites": []}
    all_items = []
    succeeded, failed = [], []

    # ---------- 1. curl 直连信源：抓列表 + 抓页面详情 ----------
    for key, cfg in CURL_SOURCES.items():
        try:
            html = fetch_http(cfg["url"])
            items = parse_links(html, key, cfg.get("url_patterns", []))
            valid = []
            seen_urls = set()
            for t, u in items:
                if u in seen_urls:
                    continue
                seen_urls.add(u)
                # 抓页面获取真实日期 + 摘要
                page_date, page_summary = (None, None)
                try:
                    page_html = fetch_http(u)
                    page_date, page_summary = extract_page_meta(page_html, u)
                except Exception:
                    pass
                url_dt = url_real_date(u)
                final_date = page_date or url_dt or NOW.strftime("%Y-%m-%d")
                valid.append(make_item(t, u, final_date, cfg["name"], cfg["category"], page_summary))
            all_items.extend(valid[:20])
            succeeded.append({"site": cfg["name"], "url": cfg["url"], "status": "✅ 成功", "count": len(valid[:20])})
            print(f"  ✅ {cfg['name']}: {len(valid[:20])} 条（已抓页面详情）")
        except Exception as e:
            failed.append({"site": cfg["name"], "url": cfg["url"], "status": "❌ 失败", "error": str(e)[:100]})
            print(f"  ❌ {cfg['name']}: {e}")

    # ---------- 2. WebFetch 信源（任务清单 + 合并已有结果） ----------
    webfetch_tasks = []
    for key, cfg in WEBFETCH_SOURCES.items():
        webfetch_tasks.append({
            "source": cfg["name"],
            "url": cfg["url"],
            "category": cfg["category"],
            "note": f"{cfg['name']} 有 WAF/反爬（curl 不可达），需用 WebFetch 工具抓取每个公告页（含中文翻译、真实日期、摘要）后写入 us-official-webfetch.json",
        })
    if os.path.exists(WEBFETCH_FILE):
        try:
            wf = json.load(open(WEBFETCH_FILE))
            if isinstance(wf, list):
                # 字段补全/标准化
                for art in wf:
                    if not isinstance(art, dict):
                        continue
                    if art.get("priority_score") is None or art.get("priority_score") == "":
                        score, _ = calc_score(art.get("title", ""), art.get("url", ""))
                        art["priority_score"] = score
                    if art.get("is_summit_level") is None:
                        _, summit = calc_score(art.get("title", ""), art.get("url", ""))
                        art["is_summit_level"] = summit
                    art.setdefault("column", "美国")
                    art.setdefault("is_official", True)
                    art.setdefault("collection_method", "us_official")
                    art.setdefault("keywords", [])
                    # title_en 缺则用 title
                    if not art.get("title_en") and art.get("title"):
                        art["title_en"] = art["title"]
                all_items.extend(wf)
                print(f"  ✅ 合并 WebFetch 信源结果: {len(wf)} 条")
        except Exception as e:
            print(f"  ⚠️ WebFetch 合并失败: {e}")

    # ---------- 3. 写输出 ----------
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    report["sites"] = succeeded + failed
    report["webfetch_required"] = webfetch_tasks
    report["total"] = len(all_items)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n📊 官方信源执行清单:")
    print(f"  ✅ 成功 {len(succeeded)} | ❌ 失败 {len(failed)} | 待 WebFetch {len(webfetch_tasks)}")
    print(f"  采集总数: {len(all_items)} 条（含 WebFetch 合并）")
    print(f"  💾 输出: {OUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
