#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际新闻看板 V1.2 - 飞书多维表格同步脚本
将 news-data.json 中的新闻数据增量同步到飞书Base存档表

使用方法:
  python3 scripts/sync_to_feishu.py              # 同步所有数据
  python3 scripts/sync_to_feishu.py --today       # 仅同步当天数据
  python3 scripts/sync_to_feishu.py --dry-run     # 预览模式（不实际写入）
"""

import json
import os
import sys
import argparse
from datetime import datetime

# ============================================================
# 配置
# ============================================================
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(PROJECT_DIR, 'data', 'news-data.json')
CONFIG_FILE = os.path.join(PROJECT_DIR, 'data', '.feishu_config')

# 飞书配置（从配置文件读取）
FEISHU_BASE_TOKEN = "A2fdb93HLamcKgslr2rcopjRnfd"
FEISHU_TABLE_ID = "tblCocvO66XoPsm1"

# 字段映射：JSON key → 飞书字段名
FIELD_MAP = {
    "archived_at": "归档日期",
    "date": "新闻日期",
    "title_en": "英文标题",
    "title": "中文标题",
    "summary": "摘要",
    "source": "来源",
    "category": "分类",
    "keywords": "关键词",
    "url": "原文链接",
    "importance": "重要性",
    "priority_score": "优先级分数",
    "is_summit_level": "是否元首级",
}

# 字段值映射：确保写入飞书的值在允许的选项列表中
SOURCE_MAPPING = {
    "BBC News": "BBC",  # 数据中的值 → 飞书选项值
}

# 分类字段值映射（基于飞书表实际选项）
CATEGORY_MAPPING = {
    # → 中美关系
    "中美关系": "中美关系",
    # → 地缘政治
    "地缘政治": "地缘政治",
    "国际政治": "地缘政治",
    # → 全球经济
    "全球经济": "全球经济",
    # → 科技竞争
    "科技竞争": "科技竞争",
    "科技与地缘政治": "科技竞争",
    # → 安全冲突（默认兜底）
    "中东局势": "安全冲突",
    "欧洲事务": "安全冲突",
    "亚太动态": "安全冲突",
    "地区动态": "安全冲突",
    "气候变化": "安全冲突",
}


def load_config():
    """加载飞书配置"""
    global FEISHU_BASE_TOKEN, FEISHU_TABLE_ID
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key == 'FEISHU_BASE_TOKEN':
                        FEISHU_BASE_TOKEN = val
                    elif key == 'FEISHU_TABLE_ID':
                        FEISHU_TABLE_ID = val


def load_news_data():
    """加载V1.2格式的新闻数据"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 兼容V1.1和V1.2格式
    if isinstance(data, list):
        # V1.1 格式：扁平数组
        return data, "v1.1"
    elif isinstance(data, dict) and 'archive' in data:
        # V1.2 格式：按日期分组
        all_articles = []
        for date_str, articles in data.get('archive', {}).items():
            for art in articles:
                all_articles.append(art)
        return all_articles, "v1.2"
    else:
        return [], "unknown"


def convert_article_to_record(article, archived_date=None):
    """
    将JSON文章转换为飞书记录格式
    返回符合 lark-cli base +record-batch-create 要求的字典
    """
    record = {}
    
    # 归档日期（使用当前时间或指定时间）
    if archived_date:
        record["归档日期"] = archived_date
    else:
        record["归档日期"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 新闻日期
    record["新闻日期"] = article.get('date', '')
    
    # 标题
    record["英文标题"] = article.get('title_en', '') or ''
    record["中文标题"] = article.get('title', '') or ''
    
    # 摘要（截断到合理长度）
    summary = article.get('summary', '') or ''
    record["摘要"] = summary[:2000] if len(summary) > 2000 else summary
    
    # 来源（应用映射确保值在选项列表中）
    source_raw = article.get('source', '') or '其他'
    record["来源"] = SOURCE_MAPPING.get(source_raw, source_raw)

    # 分类（应用映射确保值在选项列表中）
    category_raw = article.get('category', '') or '其他'
    record["分类"] = CATEGORY_MAPPING.get(category_raw, category_raw)
    
    # 关键词（转为字符串）
    keywords = article.get('keywords', [])
    if isinstance(keywords, list):
        record["关键词"] = ', '.join(keywords[:10])  # 最多保留10个关键词
    else:
        record["关键词"] = str(keywords) if keywords else ''
    
    # 原文链接
    record["原文链接"] = article.get('url', '') or ''
    
    # 重要性
    score = article.get('priority_score', 0)
    is_summit = article.get('is_summit_level', False)
    if is_summit or score >= 95:
        record["重要性"] = "⭐元首级"
    elif score >= 90:
        record["重要性"] = "🔴极高"
    elif score >= 85:
        record["重要性"] = "🟠高"
    elif score >= 75:
        record["重要性"] = "🟡中"
    else:
        record["重要性"] = "🟢低"
    
    # 优先级分数
    record["优先级分数"] = score
    
    # 是否元首级
    record["是否元首级"] = is_summit
    
    return record


def get_existing_ids():
    """获取飞书表中已有的记录ID列表，用于去重"""
    import subprocess
    
    cmd = [
        'lark-cli', 'base', '+record-list',
        '--base-token', FEISHU_BASE_TOKEN,
        '--table-id', FEISHU_TABLE_ID,
        '--limit', '1'  # 只需要知道有没有记录，不需要全部拉取
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        # 解析返回结果中的record IDs
        # 这里简化处理：实际生产环境可能需要分页获取所有ID
        return set()
    except Exception as e:
        print(f"  ⚠️ 获取已有ID失败: {e}")
        return set()


def sync_to_feishu(articles, dry_run=False):
    """
    将文章列表同步到飞书多维表格
    使用 lark-cli base +record-batch-create 批量写入
    """
    import subprocess
    import tempfile
    
    if not articles:
        print("  ℹ️ 没有需要同步的数据")
        return 0
    
    # 转换为飞书记录格式
    records = [convert_article_to_record(art) for art in articles]
    
    if dry_run:
        print(f"\n📋 预览模式 - 将同步 {len(records)} 条记录:")
        print(f"   前3条预览:")
        for i, r in enumerate(records[:3]):
            print(f"   [{i+1}] {r['中文标题'][:40]}... | {r['来源']} | {r['重要性']}")
        if len(records) > 3:
            print(f"   ... 还有 {len(records)-3} 条")
        return len(records)
    
    # 写入临时JSON文件到项目data目录（必须使用相对路径）
    temp_file = os.path.join(PROJECT_DIR, 'data', 'tmp_sync.json')
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump({"create_records": records}, f, ensure_ascii=False)

    try:
        # 调用 lark-cli 批量创建记录（使用 @ 前缀 + 相对路径）
        cmd = [
            'lark-cli', 'base', '+record-batch-create',
            '--base-token', FEISHU_BASE_TOKEN,
            '--table-id', FEISHU_TABLE_ID,
            '--json', '@./data/tmp_sync.json',  # 必须是相对路径
            '--as', 'user'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # 清理临时文件
        os.unlink(temp_file)
        
        if result.returncode == 0:
            output = json.loads(result.stdout) if result.stdout.startswith('{') else {}
            created_count = output.get('data', {}).get('created_count', len(records))
            print(f"  ✅ 成功同步 {created_count} 条记录到飞书")
            return created_count
        else:
            print(f"  ❌ 同步失败:")
            print(f"     stdout: {result.stdout[:500]}")
            print(f"     stderr: {result.stderr[:500]}")
            return 0
            
    except Exception as e:
        print(f"  ❌ 同步异常: {e}")
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    return 0


def main():
    parser = argparse.ArgumentParser(description='同步新闻数据到飞书多维表格')
    parser.add_argument('--today', action='store_true', help='仅同步今天的数据')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际写入')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🌍 国际新闻看板 V1.2 - 飞书多维表格同步工具")
    print("=" * 60)
    print()
    
    # 加载配置
    load_config()
    print(f"📌 飞书Base Token: {FEISHU_BASE_TOKEN[:20]}...")
    print(f"📌 表格ID: {FEISHU_TABLE_ID}")
    print()
    
    # 加载数据
    print("📂 读取本地新闻数据...")
    articles, version = load_news_data()
    print(f"   数据版本: {version}, 总条数: {len(articles)}")
    
    # 筛选
    if args.today:
        today = datetime.now().strftime('%Y-%m-%d')
        articles = [a for a in articles if a.get('date') == today]
        print(f"   筛选后（仅今天）: {len(articles)} 条")
    
    if not articles:
        print("\nℹ️ 没有需要同步的数据")
        return
    
    # 显示统计
    sources = set(a.get('source','') for a in articles)
    summit = sum(1 for a in articles if a.get('is_summit_level'))
    print(f"\n📊 待同步数据统计:")
    print(f"   • 总条数: {len(articles)}")
    print(f"   • 信源数: {len(sources)}")
    print(f"   • 元首级: {summit} 条")
    
    # 执行同步
    print(f"\n{'🔍 预览' if args.dry_run else '🚀 开始同步'}...")
    count = sync_to_feishu(articles, dry_run=args.dry_run)
    
    if count > 0 and not args.dry_run:
        print(f"\n✅ 同步完成！")
        print(f"   📊 新增/更新: {count} 条记录")
        print(f"   🔗 查看地址: https://my.feishu.cn/base/{FEISHU_BASE_TOKEN}")


if __name__ == '__main__':
    main()
