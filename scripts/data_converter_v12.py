#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际新闻看板 V1.2 数据结构转换器
将 V1.1 扁平数组格式转换为 V1.2 按日期分组格式

V1.1 格式: [ {article1}, {article2}, ... ]
V1.2 格式:
{
    "version": "1.2",
    "lastUpdated": "2026-07-31 17:00",
    "archive": {
        "2026-07-31": [ {articles...} ],
        "2026-07-30": [ {articles...} ],
        ...
    },
    "dates": ["2026-07-31", "2026-07-30", ...],
    "stats": {
        "totalArticles": 156,
        "dateCount": 7,
        "latestDate": "2026-07-31"
    }
}
"""

import json
import os
from datetime import datetime, timedelta
from collections import OrderedDict

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(PROJECT_DIR, 'data', 'news-data.json')
RETENTION_DAYS = 7


def load_v11_data(filepath):
    """加载 V1.1 格式的扁平数组数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 如果已经是 V1.2 格式，直接返回
    if isinstance(data, dict) and 'archive' in data:
        return data

    # V1.1 格式：扁平数组
    if isinstance(data, list):
        return data

    raise ValueError("无法识别的数据格式")


def convert_to_v12(articles_list):
    """将 V1.1 扁平数组转换为 V1.2 按日期分组格式"""

    # 按日期分组
    archive = OrderedDict()
    for article in articles_list:
        date_str = article.get('date', 'unknown')
        if date_str not in archive:
            archive[date_str] = []
        archive[date_str].append(article)

    # 对每个日期内的文章按 priority_score 降序排序
    for date_str in archive:
        archive[date_str].sort(
            key=lambda x: x.get('priority_score', 0),
            reverse=True
        )

    # 获取日期列表（降序：最新在前）
    dates = sorted(archive.keys(), reverse=True)

    # 清理超过7天的旧数据
    cutoff_date = (datetime.now() - timedelta(days=RETENTION_DAYS)).strftime('%Y-%m-%d')
    cleaned_archive = OrderedDict()
    for date_str in dates:
        if date_str >= cutoff_date:
            cleaned_archive[date_str] = archive[date_str]

    # 统计信息
    total_articles = sum(len(arts) for arts in cleaned_archive.values())

    # 构建 V1.2 结构
    v12_data = {
        "version": "1.2",
        "lastUpdated": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "retentionDays": RETENTION_DAYS,
        "archive": dict(cleaned_archive),
        "dates": list(cleaned_archive.keys()),
        "stats": {
            "totalArticles": total_articles,
            "dateCount": len(cleaned_archive),
            "latestDate": dates[0] if dates else None,
            "oldestDate": dates[-1] if dates else None,
        }
    }

    return v12_data


def append_new_data(v12_data, new_articles):
    """将新文章追加到现有 V1.2 数据中（增量更新）"""
    today = datetime.now().strftime('%Y-%m-%d')

    if today not in v12_data['archive']:
        v12_data['archive'][today] = []

    existing_ids = set()
    for date_arts in v12_data['archive'].values():
        for art in date_arts:
            existing_ids.add(art.get('id'))

    added_count = 0
    for article in new_articles:
        if article.get('id') not in existing_ids:
            v12_data['archive'][today].append(article)
            existing_ids.add(article.get('id'))
            added_count += 1

    # 排序当天数据
    v12_data['archive'][today].sort(
        key=lambda x: x.get('priority_score', 0),
        reverse=True
    )

    # 更新日期列表和统计
    v12_data['dates'] = sorted(v12_data['archive'].keys(), reverse=True)
    cleanup_old_data(v12_data)
    v12_data['lastUpdated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    _update_stats(v12_data)

    return added_count


def cleanup_old_data(v12_data):
    """清理超过7天的旧数据"""
    cutoff_date = (datetime.now() - timedelta(days=RETENTION_DAYS)).strftime('%Y-%m-%d')
    to_remove = [d for d in v12_data['dates'] if d < cutoff_date]

    for date_str in to_remove:
        del v12_data['archive'][date_str]

    v12_data['dates'] = sorted(v12_data['archive'].keys(), reverse=True)


def _update_stats(v12_data):
    """更新统计信息"""
    total = sum(len(arts) for arts in v12_data['archive'].values())
    v12_data['stats'] = {
        "totalArticles": total,
        "dateCount": len(v12_data['dates']),
        "latestDate": v12_data['dates'][0] if v12_data['dates'] else None,
        "oldestDate": v12_data['dates'][-1] if v12_data['dates'] else None,
    }


def flatten_for_html(v12_data, selected_date=None):
    """
    将 V1.2 数据展平为 HTML 渲染用的数组
    如果指定日期，只返回该日期；否则返回全部（按日期分组）
    """
    if selected_date and selected_date in v12_data['archive']:
        return v12_data['archive'][selected_date], selected_date

    # 返回所有数据，按日期顺序
    all_articles = []
    for date_str in v12_data['dates']:
        for article in v12_data['archive'][date_str]:
            all_articles.append(article)

    return all_articles, 'all'


def save_v12_data(v12_data, filepath):
    """保存 V1.2 格式数据到文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(v12_data, f, ensure_ascii=False, indent=2)


def main():
    """主函数：执行 V1.1 → V1.2 转换"""
    print("=" * 60)
    print("🔄 国际新闻看板 V1.1 → V1.2 数据结构转换")
    print("=" * 60)

    # 加载现有数据
    print(f"\n📂 读取数据文件: {DATA_FILE}")
    raw_data = load_v11_data(DATA_FILE)

    if isinstance(raw_data, dict) and 'archive' in raw_data:
        print("✅ 数据已是 V1.2 格式，无需转换")
        print(f"   当前包含 {raw_data['stats']['totalArticles']} 条新闻")
        print(f"   覆盖 {raw_data['stats']['dateCount']} 天")
        return raw_data

    # 转换
    print(f"📊 检测到 V1.1 格式，共 {len(raw_data)} 条文章")
    v12_data = convert_to_v12(raw_data)

    # 显示转换结果
    print(f"\n✅ 转换完成！")
    print(f"   版本: V1.2")
    print(f"   总条数: {v12_data['stats']['totalArticles']}")
    print(f"   天数: {v12_data['stats']['dateCount']}")
    print(f"   最新日期: {v12_data['stats']['latestDate']}")
    print(f"   最旧日期: {v12_data['stats']['oldestDate']}")
    print(f"\n   日期分布:")
    for date_str in v12_data['dates']:
        count = len(v12_data['archive'][date_str])
        summit = sum(1 for a in v12_data['archive'][date_str] if a.get('is_summit_level'))
        print(f"     • {date_str}: {count} 条 ({summit} 条元首级)")

    # 保存
    save_v12_data(v12_data, DATA_FILE)
    print(f"\n💾 已保存到: {DATA_FILE}")

    return v12_data


if __name__ == '__main__':
    main()
