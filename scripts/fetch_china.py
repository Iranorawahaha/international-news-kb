#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_china.py — 国内新闻看板 · 权威信源抓取器（Ira 信息看板体系）

数据源（国家级权威信源，仅白名单）：
  1. 中国政府网·要闻   https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json
  2. 中国政府网·最新政策 https://www.gov.cn/zhengce/zuixin/ZUIXINZHENGCE.json

过滤标准（严格）：
  - 标题黑名单: 含营销/文娱/小道/八卦/震惊等词剔除
  - 重要度分级: 元首级(习近平/国家主席/中央军委) > 常委级(李强/赵乐际等政治局常委) >
              部委级(国务院常务会议/国务院印发) > 一般政策
  - 分类: 元首动态 / 常委动态 / 重要会议 / 人事任免 / 政策发布 / 其他

输出: data/china-news.json (与看板共用，archive 按日期分组)
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "china-news.json")

SOURCES = [
    {
        "name": "中国政府网·要闻",
        "url": "https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json",
        "kind": "yaowen",
    },
    {
        "name": "中国政府网·最新政策",
        "url": "https://www.gov.cn/zhengce/zuixin/ZUIXINZHENGCE.json",
        "kind": "zhengce",
    },
]

# 领导人名单（用于分级与过滤）
SUMMIT_LEADERS = ["习近平", "国家主席", "中央军委", "总书记"]
PSC_LEADERS = ["李强", "赵乐际", "王沪宁", "蔡奇", "丁薛祥", "李希", "全国政协主席", "全国人大常委会委员长", "国务院总理"]

# 营销号/文娱/小道消息黑名单（标题含则剔除）
JUNK_KEYWORDS = [
    "震惊", "太可怕", "万万没想到", "看完沉默了", "重磅内幕", "独家爆料", "小道消息",
    "娱乐圈", "明星", "八卦", "绯闻", "吃瓜", "剧透", "演唱会", "票房", "综艺",
    "带货", "促销", "打折", "秒杀", "福利", "抽奖", "养生", "偏方", "神医",
    "风水", "星座", "生肖运势", "减肥", "美白", "祛痘",
]

# 分类规则：按标题关键词映射
CATEGORY_RULES = [
    ("元首动态", ["习近平", "国家主席", "中央军委", "总书记", "出席", "考察", "会见"]),
    ("常委动态", ["李强", "赵乐际", "王沪宁", "蔡奇", "丁薛祥", "李希"]),
    ("重要会议", ["会议", "全会", "座谈会", "研讨会", "论坛", "学习贯彻"]),
    ("人事任免", ["任免", "任命", "免去", "担任", "任命决定"]),
    ("政策发布", ["印发", "通知", "规划", "意见", "方案", "条例", "规定", "办法", "决定"]),
]

CATEGORY_PRIORITY = {"元首动态": 0, "常委动态": 1, "重要会议": 2, "人事任免": 3, "政策发布": 4, "其他": 5}


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Ira-Intel/1.0)"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def classify(title):
    for cat, kws in CATEGORY_RULES:
        for kw in kws:
            if kw in title:
                return cat
    return "其他"


def assess_importance(title, cat):
    """重要度 0-100"""
    score = 50
    for kw in SUMMIT_LEADERS:
        if kw in title:
            score = 100
            break
    else:
        for kw in PSC_LEADERS:
            if kw in title:
                score = 95
                break
        else:
            if cat == "重要会议":
                score = 85
            elif cat == "人事任免":
                score = 80
            elif cat == "政策发布":
                score = 75
    if "【视频】" in title:
        score = min(score + 2, 100)
    return score


def is_summit(title):
    return any(kw in title for kw in SUMMIT_LEADERS)


def is_junk(title):
    return any(kw in title for kw in JUNK_KEYWORDS)


def main():
    all_items = []
    for src in SOURCES:
        try:
            data = fetch_json(src["url"])
            items = data if isinstance(data, list) else data.get("listArrP") or data.get("data") or []
            print(f"  ✅ {src['name']}: {len(items)} 条")
            for it in items:
                title = (it.get("TITLE") or "").strip()
                url = (it.get("URL") or "").strip()
                date = (it.get("DOCRELPUBTIME") or "").strip()[:10]
                if not title or not url or is_junk(title):
                    continue
                cat = classify(title)
                all_items.append({
                    "title": title,
                    "url": url,
                    "date": date,
                    "source": src["name"],
                    "category": cat,
                    "priority_score": assess_importance(title, cat),
                    "is_summit_level": is_summit(title),
                    "collectedAt": NOW.strftime("%Y-%m-%d %H:%M:%S"),
                })
        except Exception as e:
            print(f"  ❌ {src['name']}: {e}")

    # 去重（URL 去重 + 标题相似去重：视频版与文字版合并）
    seen, unique = set(), []
    for it in all_items:
        # 标题去【视频】前缀后比较（视频版与文字版算同一条）
        norm_title = re.sub(r"^【视频】", "", it["title"]).strip()
        key = norm_title[:40]
        if key in seen:
            continue
        seen.add(key)
        # 若之前已加入，替换为文字版（保留 URL 更完整的一条）
        unique.append(it)

    # 按日期归档
    archive = {}
    for it in unique:
        d = it["date"] or NOW.strftime("%Y-%m-%d")
        archive.setdefault(d, []).append(it)
    for d in archive:
        archive[d].sort(key=lambda x: (-x["priority_score"], x["title"]))

    # 7 天保留
    cutoff = (NOW - timedelta(days=7)).strftime("%Y-%m-%d")
    archive = {d: v for d, v in archive.items() if d >= cutoff}

    dates = sorted(archive.keys(), reverse=True)
    total = sum(len(v) for v in archive.values())
    today = NOW.strftime("%Y-%m-%d")

    data = {
        "version": "1.0",
        "lastUpdated": NOW.strftime("%Y-%m-%d %H:%M"),
        "retentionDays": 7,
        "archive": archive,
        "dates": dates,
        "today": today,
        "todayCount": len(archive.get(today, [])),
        "stats": {
            "totalArticles": total,
            "dateCount": len(dates),
            "latestDate": dates[0] if dates else None,
            "summitCount": sum(1 for v in archive.values() for x in v if x.get("is_summit_level")),
        },
    }

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n📊 国内新闻抓取完成:")
    print(f"  总计: {total} 条 | 覆盖 {len(dates)} 天 | 今日 {data['todayCount']} 条 | ⭐元首级 {data['stats']['summitCount']} 条")
    print(f"  日期分布:")
    for d in dates:
        summit = sum(1 for x in archive[d] if x.get("is_summit_level"))
        print(f"    • {d}: {len(archive[d])} 条 ({summit} ⭐)")
    print(f"  💾 已保存: {DATA_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
