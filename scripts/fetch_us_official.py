#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_us_official.py — 美国官方信源采集器（Ira 信息看板 · 国际新闻扩充）

六大官方信源：
  1. 白宫      https://www.whitehouse.gov/news/             ✅ curl 可抓
  2. 国务院    https://www.state.gov/press-releases/        ✅ curl 可抓
  3. USTR      https://ustr.gov/about-us/policy-offices/press-office/press-releases  ✅ curl 可抓
  4. 财政部    https://home.treasury.gov/news/press-releases ✅ curl 可抓
  5. 商务部    https://www.commerce.gov/news/press-releases  ⚠️ curl 403（WAF），需 WebFetch
  6. 国防部    https://www.defense.gov/News/Press-Releases/  ⚠️ curl 403（WAF），需 WebFetch

输出:
  - data/us-official.json        curl 可抓信源的结果
  - data/us-official-webfetch.json  需 WebFetch 的信源（商务/国防），由自动化任务 WebFetch 后覆盖
  - 信源执行清单 us-official-report.json: 成功/失败站点 + 抓取条数
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

# curl 直连信源（HTML 解析）
CURL_SOURCES = {
    "whitehouse": {
        "name": "白宫",
        "url": "https://www.whitehouse.gov/news/",
        "category": "美国",
    },
    "state": {
        "name": "美国国务院",
        "url": "https://www.state.gov/press-releases/",
        "category": "美国",
    },
    "treasury": {
        "name": "美国财政部",
        "url": "https://home.treasury.gov/news/press-releases",
        "category": "美国",
    },
}

# 需 WebFetch 的信源（curl 403）
WEBFETCH_SOURCES = {
    "commerce": {
        "name": "美国商务部",
        "url": "https://www.commerce.gov/news/press-releases",
        "category": "美国",
    },
    "defense": {
        "name": "美国国防部(war.gov)",
        "url": "https://www.defense.gov/News/Press-Releases/",
        "category": "美国",
    },
    "ustr": {
        "name": "美国贸易代表办公室(USTR)",
        "url": "https://ustr.gov/",  # USTR 首页含最新新闻（press-releases 子页 404）
        "category": "美国",
        "note": "USTR 对 curl 反爬(404伪装)，仅 WebFetch 可抓",
    },
}


def fetch_http(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_links(html, domain):
    """从 HTML 提取 (标题, URL, 日期) 列表"""
    items = []
    # 通用 <a href> + 标题模式
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.S):
        url, text = m.group(1), re.sub(r'<[^>]+>', '', m.group(2)).strip()
        text = re.sub(r'\s+', ' ', text).strip()
        if not text or len(text) < 15:
            continue
        if url.startswith('#') or 'javascript' in url or 'mailto' in url:
            continue
        if not url.startswith('http'):
            url = f'https://{domain}{url}' if url.startswith('/') else url
        # 过滤归档目录链接（如 USTR 的 .../2026/july/ 结尾无文章 slug）
        if re.search(r'/20\d{2}/[a-z]+/?$', url) or re.search(r'/20\d{2}$', url):
            continue
        items.append((text, url))
    return items


def extract_date(html):
    """从页面提取发布日期（页面含多个日期时取第一条匹配）"""
    for pat in [r'(20\d{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])',
                r'(0[1-9]|1[0-2])[/-](0[1-9]|[12]\d|3[01])[/-](20\d{2})']:
        m = re.search(pat, html)
        if m:
            return f'{m.group(1)}-{m.group(2)}-{m.group(3)}'
    return NOW.strftime("%Y-%m-%d")


def make_item(title, url, date, source, category):
    return {
        "title": title,
        "url": url,
        "date": date,
        "source": source,
        "category": category,
        "is_official": True,
        "collectedAt": NOW.strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    report = {"timestamp": NOW.strftime("%Y-%m-%d %H:%M"), "sites": []}
    all_items = []
    succeeded, failed = [], []

    # ---------- 1. curl 直连信源 ----------
    for key, cfg in CURL_SOURCES.items():
        try:
            html = fetch_http(cfg["url"])
            items = parse_links(html, key)
            # 过滤导航/无用链接，保留带标题的文章链接
            valid = []
            skip_words = ["skip to", "menu", "search", "twitter", "facebook", "youtube",
                          "instagram", "subscribe", "newsletter", "privacy", "terms",
                          "2026", "2025", "2024"]
            prefix = cfg.get("link_prefix", "")
            for t, u in items:
                tl = t.lower()
                if any(w in tl for w in skip_words):
                    continue
                if len(t) < 20:
                    continue
                if prefix and prefix not in u:
                    continue
                valid.append(make_item(t, u, NOW.strftime("%Y-%m-%d"), cfg["name"], cfg["category"]))
            all_items.extend(valid[:15])
            succeeded.append({"site": cfg["name"], "url": cfg["url"], "status": "✅ 成功", "count": len(valid[:15])})
            print(f"  ✅ {cfg['name']}: {len(valid[:15])} 条")
        except Exception as e:
            failed.append({"site": cfg["name"], "url": cfg["url"], "status": "❌ 失败", "error": str(e)[:100]})
            print(f"  ❌ {cfg['name']}: {e}")

    # ---------- 2. WebFetch 信源（写任务清单，由自动化任务 WebFetch 补充） ----------
    webfetch_tasks = []
    for key, cfg in WEBFETCH_SOURCES.items():
        webfetch_tasks.append({
            "source": cfg["name"],
            "url": cfg["url"],
            "category": cfg["category"],
            "note": f"{cfg['name']} 有 WAF 反爬（curl 403），需用 WebFetch 工具抓取后写入 us-official-webfetch.json",
        })
        # 尝试合并已有 webfetch 结果（若存在）
    if os.path.exists(WEBFETCH_FILE):
        try:
            wf = json.load(open(WEBFETCH_FILE))
            if isinstance(wf, list):
                all_items.extend(wf)
                print(f"  ✅ 合并 WebFetch 信源结果: {len(wf)} 条")
        except Exception:
            pass

    # ---------- 3. 写输出 ----------
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    # 信源执行清单
    report["sites"] = succeeded + failed
    report["webfetch_required"] = webfetch_tasks
    report["total"] = len(all_items)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n📊 官方信源执行清单:")
    print(f"  ✅ 成功 {len(succeeded)} | ❌ 失败 {len(failed)} | 待 WebFetch {len(webfetch_tasks)}")
    print(f"  采集总数: {len(all_items)} 条")
    print(f"  💾 输出: {OUT_FILE}")
    print(f"  📋 报告: {REPORT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
