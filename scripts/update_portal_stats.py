#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_portal_stats.py — Ira 信息看板门户统计更新器（共享工具 v2）

设计：两个刷新通道各自更新自己负责的字段，互不覆盖：
  - 国际新闻通道 (update-news.sh):  --news-count <N> --news-date "<YYYY-MM-DD HH:MM>"
  - AI 动向通道 (refresh_board.sh): --ai-count <N> --ai-date "<MM-DD HH:MM>"
  - 任一通道可更新: --latest "<YYYY-MM-DD HH:MM>"

同时更新两处（保证一致性）：
  1. JS PLACEHOLDERS 对象（门户渲染数据源，关键）
  2. HTML 内 <b id> 元素（无 JS 环境的兜底）

用法示例:
  python3 scripts/update_portal_stats.py --news-count 86 --news-date "2026-08-01 15:55"
  python3 scripts/update_portal_stats.py --ai-count 72 --ai-date "08-01 16:00" --latest "2026-08-01 16:00"
"""
import argparse
import os
import re

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTAL_FILES = [
    os.path.join(REPO_DIR, "index.html"),
    os.path.join(REPO_DIR, "gh-pages", "index.html"),
]

# 字段 -> (JS key 名, HTML id 名)
FIELD_SPECS = {
    "news_count": ("newsCount", "stat-news-count"),
    "ai_count": ("aiCount", "stat-ai-count"),
    "latest": ("latest", "stat-latest"),
    "news_date": ("newsDate", "meta-news-date"),
    "ai_date": ("aiDate", "meta-ai-date"),
}


def update_file(path, updates):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    changed = False
    for key, value in updates.items():
        js_key, html_id = FIELD_SPECS[key]
        # 1) 更新 JS PLACEHOLDERS 对象:  key: "..."  ->  key: "value"
        js_pattern = r'(%s:\s*")[^"]*(")' % re.escape(js_key)
        content, n1 = re.subn(js_pattern, r"\g<1>%s\g<2>" % value, content)
        # 2) 更新 HTML <b id="..."> 元素
        html_pattern = r'(<b id="%s">)[^<]*(</b>)' % html_id
        content, n2 = re.subn(html_pattern, r"\g<1>%s\g<2>" % value, content)
        if n1 > 0 or n2 > 0:
            changed = True
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Ira 门户统计更新器")
    parser.add_argument("--news-count", help="国际新闻近7日条数")
    parser.add_argument("--news-date", help="国际新闻最近更新 (YYYY-MM-DD HH:MM)")
    parser.add_argument("--ai-count", help="AI 动态近7日条数")
    parser.add_argument("--ai-date", help="AI 动向最近更新 (MM-DD HH:MM)")
    parser.add_argument("--latest", help="最近数据刷新 (YYYY-MM-DD HH:MM)")
    args = parser.parse_args()

    updates = {k: v for k, v in vars(args).items() if v is not None and k in FIELD_SPECS}
    if not updates:
        print("⚠️  未指定任何要更新的字段")
        return 1

    for path in PORTAL_FILES:
        if os.path.exists(path):
            ok = update_file(path, updates)
            fields = ", ".join(f"{k}={v}" for k, v in updates.items())
            print(f"  {'✅' if ok else '⏭️ '} {path} [{fields}]")
        else:
            print(f"  ⏭️  跳过（不存在）: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
