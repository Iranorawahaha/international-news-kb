#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
normalize_schema.py — 国际新闻看板 数据 schema 统一工具（V1.3）
将历史两种字段命名统一为标准 schema：
  V1.2 旧(飞书回读): record_id/archive_date/news_date → id/date
  V1.3 新(采集入库): id/date/collectedAt/collection_method 保持不变
用法: python3 scripts/normalize_schema.py [--dry-run]
"""
import json, os, sys
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(PROJECT_DIR, "data", "news-data.json")

# 字段映射：旧字段 → 标准字段
FIELD_MAP = {
    "record_id": "id",
    "archive_date": "date",
    "news_date": "date",
}

# 标准字段集（缺失时补默认值）
STANDARD_KEYS = [
    "id", "date", "title", "title_en", "summary", "source", "category",
    "keywords", "url", "priority_score", "is_summit_level", "importance",
    "collectedAt", "collection_method", "column",
]

def normalize_article(art, default_date):
    out = {}
    for k in STANDARD_KEYS:
        v = art.get(k)
        if v is None:
            # 旧字段映射
            if k in FIELD_MAP and FIELD_MAP[k] in art:
                v = art[FIELD_MAP[k]]
            elif k == "id" and art.get("record_id"):
                v = art["record_id"]
            elif k == "date" and art.get("news_date"):
                v = art["news_date"]
            elif k == "date":
                v = default_date
            elif k == "collectedAt":
                v = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elif k == "collection_method":
                v = "legacy"
            elif k == "importance":
                v = "中"
            elif k == "keywords":
                v = []
            elif k == "priority_score":
                v = 0
            elif k == "is_summit_level":
                v = False
            elif k == "column":
                v = "其他"
        out[k] = v
    # 清理空值 id（避免去重 key 失效）
    if not out.get("id"):
        out["id"] = f"auto_{out.get('date','')}_{abs(hash(out.get('url','') or out.get('title',''))) % 100000}"
    # 确保 date 非空
    if not out.get("date"):
        out["date"] = default_date
    return out

def main():
    dry_run = "--dry-run" in sys.argv
    if not os.path.exists(DATA_FILE):
        print(f"❌ 数据文件不存在: {DATA_FILE}")
        return 1

    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    if "archive" not in data:
        print("❌ 非 V1.2+ 格式（无 archive 字段）")
        return 1

    changed = 0
    for date_str, articles in data["archive"].items():
        new_list = []
        for art in articles:
            std = normalize_article(art, date_str)
            if std != art:
                changed += 1
            new_list.append(std)
        data["archive"][date_str] = new_list

    # 更新 stats
    total = sum(len(v) for v in data["archive"].values())
    data["dates"] = sorted(data["archive"].keys(), reverse=True)
    data["stats"] = {
        "totalArticles": total,
        "dateCount": len(data["dates"]),
        "latestDate": data["dates"][0] if data["dates"] else None,
        "oldestDate": data["dates"][-1] if data["dates"] else None,
    }
    data["lastUpdated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    if dry_run:
        print(f"🔍 [dry-run] 将标准化 {changed} 条记录 | 总 {total} 条")
        return 0

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ schema 统一完成: 标准化 {changed} 条 | 总 {total} 条")
    return 0

if __name__ == "__main__":
    sys.exit(main())
