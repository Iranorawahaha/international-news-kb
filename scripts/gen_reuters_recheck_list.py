#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_reuters_recheck_list.py — 每日刷新汇报固定附带项生成器（V2.15 A 方案配套）

功能：列出某版面日中「source=路透社 但 URL 非 reuters.com 官网」的转载条目，
      并为每条生成 Google/Bing 的 `"完整英文标题" site:reuters.com` 一键搜索链接。
      用户浏览器打开链接搜到官网原链后，回复「编号 + 官网 URL」即可走 A 方案替换。

用法：
  python3 scripts/gen_reuters_recheck_list.py            # 默认 d['today']（刷新当天）
  python3 scripts/gen_reuters_recheck_list.py --date 2026-09-08

背景（V2.15 固化，勿回退）：
  - 路透 9-02 起 DataDome 域名级 JS 挑战，终端无抓取通道；官网 URL 只取「第三方可见背书」
    或用户浏览器人工提供；禁构造 URL；「401=存在」验证法无效勿再用。
  - 用户拍板：每日刷新汇报固定附带此清单，作为官网 URL 的稳定增量来源。

替换流程（用户回报官网 URL 后）：
  1) 双端 data/news-webfetch.json + data/news-data.json 中该条目 url 换官网 + pop repost_from
  2) awk 提取 update-news.sh 的 GENERATE_HTML_V12 段重建 HTML（勿重跑全量 update，会丢字段）
  3) scripts/check_js_syntax.py + scripts/inject_nav.py
  4) git add 精确文件 + commit + push（与国内/AI 自动化并发同仓库，push 前核对）
  5) curl 线上 ?t=$(date +%s) 二次验证
"""
import argparse
import json
import sys
import urllib.parse
from datetime import datetime

KB_DIR = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50"
NEWS_DATA = f"{KB_DIR}/data/news-data.json"

# 反爬源 → 官网域映射（当前痛点路透；WSJ/WaPo/Politico 后续若需要可扩）
SITE_MAP = {
    "路透社": "reuters.com",
    "Reuters": "reuters.com",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="版面日 YYYY-MM-DD，默认 archive 最新版面日 dates[0]")
    args = ap.parse_args()

    d = json.load(open(NEWS_DATA, encoding="utf-8"))
    arc = d["archive"]
    # 注意：data['today'] 字段陈旧（仅 V2.6 护栏移动条目时才更新，可能停数天前），
    # 默认日须取 dates[0]（最新版面日），勿用 today 字段
    day = args.date or d.get("dates", [None])[0] or max(arc.keys())

    rows = []
    for a in arc.get(day, []):
        src = str(a.get("source", ""))
        url = str(a.get("url", ""))
        dom = SITE_MAP.get(src)
        if dom and f"{dom}/" not in url:
            rows.append(a)

    if not rows:
        print(f"[{day}] 今日无路透转载条目（全官网或空缺），无需反查。")
        return

    print(f"[{day}] 路透转载待反查 {len(rows)} 条 — 点击链接搜官网，命中回复「编号: reuters.com 官网URL」即可替换\n")
    for i, a in enumerate(rows, 1):
        t = a.get("title_en") or a.get("title") or ""
        cur = str(a.get("url", ""))  # 每轮重新取值，勿用循环外残留变量
        dom = SITE_MAP.get(str(a.get("source", "")), "reuters.com")
        q = urllib.parse.quote(f'"{t}" site:{dom}')
        g = f"https://www.google.com/search?q={q}"
        b = f"https://www.bing.com/search?q={q}"
        print(f"[{i}] {a.get('priority_score', '')}★ {a.get('title_zh', '')[:44]}")
        print(f"    标题: {t}")
        print(f"    当前: {cur}")
        print(f"    Google: {g}")
        print(f"    Bing  : {b}")
        print()


if __name__ == "__main__":
    main()
