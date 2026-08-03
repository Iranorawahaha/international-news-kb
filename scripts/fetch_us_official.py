#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_us_official.py — 美国官方信源采集器 V1.2（Ira 信息看板 · 国际新闻扩充）

六大官方信源（新闻公告页）：
  1. 白宫      https://www.whitehouse.gov/news/             ✅ curl 可抓（新闻公告）
  2. 国务院    https://www.state.gov/press-releases/        ✅ curl 可抓（Press Releases）
  3. 财政部    https://home.treasury.gov/news/press-releases ✅ curl 可抓（Press Releases）
  4. USTR      https://ustr.gov/                             ⚠️ curl 反爬（404 伪装），需 WebFetch
  5. 商务部    https://www.commerce.gov/news/press-releases  ⚠️ curl 403（WAF），需 WebFetch
  6. 国防部    https://www.defense.gov/News/Press-Releases/  ⚠️ curl 403（WAF），需 WebFetch

只抓「新闻公告」链接（URL 含 /news/ /releases/ /presidential-actions/ /fact-sheets/
/briefings-statements/ /press-releases/ 等特征），过滤导航菜单。

输出:
  - data/us-official.json           curl 可抓信源的结果（标准字段）
  - data/us-official-webfetch.json  需 WebFetch 的信源（由自动化任务 WebFetch 后覆盖）
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

# curl 直连信源
CURL_SOURCES = {
    "whitehouse": {
        "name": "白宫",
        "url": "https://www.whitehouse.gov/news/",
        "category": "美国",
        # 白宫新闻 URL 特征
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

# 需 WebFetch 的信源（curl 403/404 反爬）
WEBFETCH_SOURCES = {
    "commerce": {"name": "美国商务部", "url": "https://www.commerce.gov/news/press-releases", "category": "美国"},
    "defense": {"name": "美国国防部(war.gov)", "url": "https://www.defense.gov/News/Press-Releases/", "category": "美国"},
    "ustr": {"name": "美国贸易代表办公室(USTR)", "url": "https://ustr.gov/", "category": "美国"},
}

# 导航/无意义词（过滤）
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


def fetch_http(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_links(html, domain, url_patterns):
    """从 HTML 提取符合 url_patterns 的新闻链接 (标题, URL)"""
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
        # URL 必须匹配新闻公告特征
        if not any(p in url for p in url_patterns):
            continue
        # 过滤归档目录（如 .../2026/july/ 结尾无文章 slug）
        if re.search(r'/20\d{2}/[a-z]+/?$', url) or re.search(r'/20\d{2}$', url):
            continue
        # 过滤导航词
        tl = text.lower()
        if any(w in tl for w in NAV_WORDS):
            continue
        items.append((text, url))
    return items


def url_real_date(url):
    """从 URL 提取发布日期 YYYY-MM-DD（reuters/wp/news.cn 等 URL 含日期）"""
    if not url:
        return None
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


def make_item(title, url, date, source, category):
    """标准字段（含 priority_score/is_summit_level/keywords/column，供看板直接渲染）"""
    score = 70  # 官方信源默认较高分（权威性加成）
    # 涉华/元首级识别
    text = f"{title} {url}"
    summit = any(k in title for k in ["President", "Trump", "Xi", "习近平", "Biden", "普京", "Putin"])
    cn = any(k in title for k in ["China", "Chinese", "中国", "Beijing", "Beijing", "Taiwan", "台湾", "TikTok", "Huawei"])
    if cn:
        score = 92
        if summit:
            score = 98
    elif summit:
        score = 88
    if "sanction" in text.lower() or "tariff" in text.lower() or "export control" in text.lower() or "forced labor" in text.lower():
        score = max(score, 90)
    return {
        "title": title,
        "title_en": title,
        "summary": f"[官方信源] {source} 发布：{title}",
        "url": url,
        "date": date or NOW.strftime("%Y-%m-%d"),
        "source": source,
        "category": category,
        "column": "美国",
        "priority_score": score,
        "is_summit_level": bool(summit),
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

    # ---------- 1. curl 直连信源 ----------
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
                date = url_real_date(u) or NOW.strftime("%Y-%m-%d")
                valid.append(make_item(t, u, date, cfg["name"], cfg["category"]))
            all_items.extend(valid[:20])
            succeeded.append({"site": cfg["name"], "url": cfg["url"], "status": "✅ 成功", "count": len(valid[:20])})
            print(f"  ✅ {cfg['name']}: {len(valid[:20])} 条")
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
            "note": f"{cfg['name']} 有 WAF/反爬（curl 不可达），需用 WebFetch 工具抓取后写入 us-official-webfetch.json",
        })
    if os.path.exists(WEBFETCH_FILE):
        try:
            wf = json.load(open(WEBFETCH_FILE))
            if isinstance(wf, list):
                # V1.2: WebFetch 信源字段补全（与 make_item 标准一致）
                for art in wf:
                    if not isinstance(art, dict):
                        continue
                    if art.get("priority_score") is None or art.get("priority_score") == "":
                        t = art.get("title", "")
                        cn = any(k in t for k in ["China", "Chinese", "中国", "Beijing", "Taiwan", "台湾", "TikTok", "Huawei"])
                        sm = any(k in t for k in ["President", "Trump", "Xi", "Biden", "普京", "Putin"])
                        art["priority_score"] = 98 if (cn and sm) else (92 if cn else (88 if sm else 75))
                    if art.get("is_summit_level") is None:
                        art["is_summit_level"] = any(k in art.get("title", "") for k in ["President", "Trump", "Xi", "Biden", "普京", "Putin"])
                    if not art.get("column"):
                        art["column"] = "美国"
                    if not art.get("title_en"):
                        art["title_en"] = art.get("title", "")
                    if not art.get("summary"):
                        art["summary"] = f"[官方信源] {art.get('source','')} 发布：{art.get('title','')}"
                    art.setdefault("is_official", True)
                    art.setdefault("collection_method", "us_official")
                    art.setdefault("keywords", [])
                all_items.extend(wf)
                print(f"  ✅ 合并 WebFetch 信源结果: {len(wf)} 条（字段已补全）")
        except Exception:
            pass

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
