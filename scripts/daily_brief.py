#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
daily_brief.py — Ira 信息看板 门户「今日日报」生成器

从两个数据源提取当天（北京时间）新增资讯的要点简报，注入门户 index.html：
  - 国际新闻: data/news-data.json 中 archive[今天] 的条目（标题 + 来源 + 原文链接）
  - AI 动向:   /tmp/aihot_scan/merged.json 中 timeline_ts >= 今日0点 的条目

用法:
  python3 scripts/daily_brief.py --news   # 只更新国际新闻日报
  python3 scripts/daily_brief.py --ai     # 只更新 AI 动向日报
  python3 scripts/daily_brief.py          # 两者都更新（默认）

说明: 双通道互不覆盖——新闻通道调用 --news，AI 通道调用 --ai。
"""
import argparse
import html
import json
import os
import re
from datetime import datetime, timezone, timedelta

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTAL_FILES = [
    os.path.join(REPO_DIR, "index.html"),
    os.path.join(REPO_DIR, "gh-pages", "index.html"),
]
NEWS_FILE = os.path.join(REPO_DIR, "data", "news-data.json")
import os as _os
_AI_CANDS = []
_t = _os.environ.get("TMPDIR")
if _t:
    _AI_CANDS.append(_os.path.join(_t, "aihot_scan", "merged.json"))
_AI_CANDS.append("/tmp/aihot_scan/merged.json")
AI_FILE = next((c for c in _AI_CANDS if _os.path.exists(c)), _AI_CANDS[0])
CN_FILE = os.path.join(REPO_DIR, "data", "china-news.json")

TZ = timezone(timedelta(hours=8))
MAX_ITEMS = 12  # 每个板块最多展示条数


def esc(s):
    return html.escape(s or "", quote=True)


def build_news_brief():
    """国际新闻当天要点简报"""
    today = datetime.now(TZ).strftime("%Y-%m-%d")
    try:
        with open(NEWS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("archive", {}).get(today, [])
    except Exception:
        items = []
    if not items:
        return f'<div class="daily-empty">今日暂无新增国际新闻</div>', 0, today
    # 按重要性排序，取前 MAX_ITEMS
    items = sorted(items, key=lambda a: (
        -(1 if a.get("is_summit_level") else 0),
        -(a.get("priority_score") or 0),
    ))[:MAX_ITEMS]
    lis = []
    for it in items:
        title = it.get("title") or it.get("title_en") or ""
        src = it.get("source") or "未知"
        url = it.get("url") or "#"
        summit = "⭐" if it.get("is_summit_level") else ""
        lis.append(
            f'<div class="daily-item"><span class="d-dot"></span>'
            f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(summit)}{esc(title)}</a>'
            f'<span class="d-src">{esc(src)}</span></div>'
        )
    return "".join(lis), len(items), today


def _ts(it):
    pa, da = it.get("publishedAt"), it.get("discoveredAt")

    def t(s):
        if not s:
            return None
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
        except Exception:
            return None
    pa_t, da_t = t(pa), t(da)
    if pa_t is None:
        return da_t or 0
    if da_t is None:
        return pa_t
    return pa_t if (da_t - pa_t > 72 * 3600) else da_t


def build_ai_brief():
    """AI 动向当天要点简报"""
    today_start = datetime.now(TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    today_stamp = today_start.timestamp()
    try:
        with open(AI_FILE, encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("items", [])
    except Exception:
        items = []
    today_items = [it for it in items if _ts(it) >= today_stamp]
    if not today_items:
        return '<div class="daily-empty">今日暂无新增 AI 动态</div>', 0, today_start.strftime("%Y-%m-%d")
    today_items = sorted(today_items, key=_ts, reverse=True)[:MAX_ITEMS]
    lis = []
    for it in today_items:
        title = it.get("title") or ""
        src = (it.get("source") or {}).get("name") or "AI HOT"
        url = (it.get("links") or {}).get("original") or (it.get("links") or {}).get("aihot") or "#"
        cat = it.get("category") or ""
        cat_map = {"ai-models": "模型", "ai-products": "产品", "industry": "行业", "paper": "论文", "tip": "观点"}
        tag = cat_map.get(cat, "")
        lis.append(
            f'<div class="daily-item"><span class="d-dot"></span>'
            f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(title)}</a>'
            f'<span class="d-src">{esc(tag)} · {esc(src)}</span></div>'
        )
    return "".join(lis), len(today_items), today_start.strftime("%Y-%m-%d")


def build_china_brief():
    """国内新闻当天要点简报"""
    today = datetime.now(TZ).strftime("%Y-%m-%d")
    try:
        with open(CN_FILE, encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("archive", {}).get(today, [])
        last_updated = data.get("lastUpdated", "")
    except Exception:
        items = []
    if not items:
        return '<div class="daily-empty">今日暂无新增国内新闻</div>', 0, today
    items = sorted(items, key=lambda a: (-(1 if a.get("is_summit_level") else 0), -(a.get("priority_score") or 0)))[:MAX_ITEMS]
    lis = []
    for it in items:
        title = it.get("title") or ""
        src = it.get("source") or ""
        url = it.get("url") or "#"
        cat = it.get("category") or ""
        summit = "⭐" if it.get("is_summit_level") else ""
        summary = (it.get("summary") or "").strip()
        # 简报中显示摘要头 50 字
        summ_html = f'<div class="d-summ">{esc(summary[:55] + ("…" if len(summary) > 55 else ""))}</div>' if summary else ""
        lis.append(
            f'<div class="daily-item"><span class="d-dot"></span>'
            f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(summit)}{esc(title)}</a>'
            f'<span class="d-src">{esc(cat)} · {esc(src)}</span>{summ_html}</div>'
        )
    return "".join(lis), len(items), today, last_updated


def update_portal(news_html=None, news_count=None, ai_html=None, ai_count=None,
                  cn_html=None, cn_count=None, cn_date=None, daily_date=None):
    for path in PORTAL_FILES:
        if not os.path.exists(path):
            print(f"  ⏭️  跳过（不存在）: {path}")
            continue
        with open(path, encoding="utf-8") as f:
            content = f.read()
        changed = False
        # 标记法替换：精确替换 <!--DAILY_*_START--> 与 <!--DAILY_*_END--> 之间的内容
        if news_html is not None:
            content, n = re.subn(
                r"(<!--DAILY_NEWS_START-->)(.*?)(<!--DAILY_NEWS_END-->)",
                lambda m: m.group(1) + news_html + m.group(3),
                content, count=1, flags=re.S)
            if n:
                changed = True
            else:
                print("  ⚠️  未找到 DAILY_NEWS_START 标记，跳过新闻日报")
            content, n2 = re.subn(
                r'(<span class="daily-count" id="daily-news-count">)[^<]*(</span>)',
                lambda m: m.group(1) + str(news_count) + " 条" + m.group(2),
                content, count=1)
            if n2: changed = True
        if ai_html is not None:
            content, n = re.subn(
                r"(<!--DAILY_AI_START-->)(.*?)(<!--DAILY_AI_END-->)",
                lambda m: m.group(1) + ai_html + m.group(3),
                content, count=1, flags=re.S)
            if n:
                changed = True
            else:
                print("  ⚠️  未找到 DAILY_AI_START 标记，跳过 AI 日报")
            content, n2 = re.subn(
                r'(<span class="daily-count" id="daily-ai-count">)[^<]*(</span>)',
                lambda m: m.group(1) + str(ai_count) + " 条" + m.group(2),
                content, count=1)
            if n2: changed = True
        if cn_html is not None:
            content, n = re.subn(
                r"(<!--DAILY_CN_START-->)(.*?)(<!--DAILY_CN_END-->)",
                lambda m: m.group(1) + cn_html + m.group(3),
                content, count=1, flags=re.S)
            if n:
                changed = True
            else:
                print("  ⚠️  未找到 DAILY_CN_START 标记，跳过国内日报")
            content, n2 = re.subn(
                r'(<span class="daily-count" id="daily-cn-count">)[^<]*(</span>)',
                lambda m: m.group(1) + str(cn_count) + " 条" + m.group(2),
                content, count=1)
            if n2: changed = True
        if daily_date:
            content, n3 = re.subn(
                r'(<span class="daily-date" id="daily-date">)[^<]*(</span>)',
                lambda m: m.group(1) + daily_date + m.group(2),
                content, count=1)
            if n3: changed = True
        if cn_date:
            content, n4 = re.subn(
                r'(<b id="meta-cn-date">)[^<]*(</b>)',
                lambda m: m.group(1) + cn_date + m.group(2),
                content, count=1)
            if n4: changed = True
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✅ 已更新日报: {path}")
        else:
            print(f"  ⏭️  无需更新: {path}")


def main():
    parser = argparse.ArgumentParser(description="Ira 门户今日日报生成器")
    parser.add_argument("--news", action="store_true", help="只更新国际新闻日报")
    parser.add_argument("--ai", action="store_true", help="只更新 AI 动向日报")
    parser.add_argument("--cn", action="store_true", help="只更新国内新闻日报")
    args = parser.parse_args()

    do_news = args.news or (not args.ai and not args.cn)
    do_ai = args.ai or (not args.news and not args.cn)
    do_cn = args.cn or (not args.news and not args.ai)

    news_html = news_count = None
    ai_html = ai_count = None
    cn_html = cn_count = cn_date = None
    daily_date = None

    if do_news:
        news_html, news_count, d = build_news_brief()
        daily_date = d
        print(f"  🌍 国际新闻今日要点: {news_count} 条")
    if do_ai:
        ai_html, ai_count, d = build_ai_brief()
        daily_date = daily_date or d
        print(f"  🤖 AI 动向今日要点: {ai_count} 条")
    if do_cn:
        cn_html, cn_count, d, cn_date = build_china_brief()
        daily_date = daily_date or d
        print(f"  🇨🇳 国内新闻今日要点: {cn_count} 条")

    update_portal(news_html=news_html, news_count=news_count,
                  ai_html=ai_html, ai_count=ai_count,
                  cn_html=cn_html, cn_count=cn_count, cn_date=cn_date,
                  daily_date=daily_date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
