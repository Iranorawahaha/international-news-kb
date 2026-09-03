#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际新闻看板 V1.2.1 - 飞书多维表格同步脚本（去重增强版）
将 news-data.json 中的新闻数据增量同步到飞书Base存档表

V1.2.1 更新 (2026-07-31):
  ✅ 新增智能去重功能（基于title[:30]+source唯一键）
  ✅ 同步前自动查询飞书已有记录，过滤重复文章
  ✅ 详细去重日志输出，便于审计
  ✅ 解决重复累积问题（88条→66条）

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

# 飞书配置（从本地配置文件 data/.feishu_config 读取，不硬编码）
FEISHU_BASE_TOKEN = os.environ.get("FEISHU_BASE_TOKEN", "")
FEISHU_TABLE_ID = os.environ.get("FEISHU_TABLE_ID", "")

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
# 飞书表可用选项：中美关系、地缘政治、全球经济、科技竞争、安全冲突、地区动态、中东局势、其他
CATEGORY_MAPPING = {
    # → 中美关系
    "中美关系": "中美关系",
    "经贸制裁": "中美关系",
    "外交资讯": "中美关系",
    "外交": "中美关系",
    # → 地缘政治
    "地缘政治": "地缘政治",
    "国际政治": "地缘政治",
    "地缘冲突": "地缘政治",
    # → 全球经济
    "全球经济": "全球经济",
    # → 科技竞争
    "科技竞争": "科技竞争",
    "科技与地缘政治": "科技竞争",
    "AI科技": "科技竞争",
    # → 安全冲突
    "军事": "安全冲突",
    "国防安全": "安全冲突",
    "俄乌": "安全冲突",
    "安全冲突": "安全冲突",
    # → 地区动态
    "亚太": "地区动态",
    "亚太动态": "地区动态",
    "欧洲": "地区动态",
    "欧洲事务": "地区动态",
    "美洲": "地区动态",
    "非洲": "地区动态",
    "中国外交": "地区动态",
    "美国": "地区动态",
    "地区动态": "地区动态",
    # → 两岸 / 中国
    "两岸关系": "中美关系",
    "中东局势": "中东局势",
    "其他地区": "其他",
    "气候变化": "其他",
    "美国政治": "其他",
    "中国": "其他",
    # → V1.2 板块分类（intl_sector）映射到飞书既有选项
    "中美博弈": "中美关系",
    "中欧与盟友": "地区动态",
    "地区局势": "地区动态",
    "全球多边": "地区动态",
    "AI·科技": "科技竞争",
    "美国内政": "其他",
}

# 来源字段值映射（基于飞书表实际选项）
# 飞书表可用：路透社、BBC、南华早报、卫报、CNN、纽约时报、半岛电视台、华盛顿邮报、美联社、人民网、外交部、环球网、国际在线、其他
SOURCE_MAPPING = {
    "路透社": "路透社",
    "BBC News": "BBC",
    "BBC": "BBC",
    "南华早报": "南华早报",
    "卫报": "卫报",
    "CNN": "CNN",
    "纽约时报": "纽约时报",
    "半岛电视台": "半岛电视台",
    "华盛顿邮报": "华盛顿邮报",
    "美联社": "美联社",
    "人民网": "人民网",
    "人民网-国际": "人民网",
    "外交部": "外交部",
    "中国外交部": "外交部",
    "环球网": "环球网",
    "国际在线": "国际在线",
    "新华网": "其他",
    "中国日报网": "其他",
    "韩国中央日报": "其他",
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


def get_existing_unique_keys():
    """
    获取飞书中已有的 (title[:30], source) 唯一键集合
    用于去重判断，避免重复同步相同新闻

    V1.2.2 修复 (2026-08-11):
      lark-cli 1.0.82 不再支持 --format csv（validation error）
      → 改用 --format json + 分页(offset) 解析 data.data 二维数组
      → 列名动态映射（中文标题/来源），兼容字段顺序变化
      → 网络抖动自动重试（3次）

    Returns:
        set: 已存在的唯一键集合 {(title, source), ...}
    """
    import subprocess
    import re
    import time

    print("  📋 正在查询飞书表已有记录（用于去重）...")

    def _extract_cell(v):
        """解析 lark-cli json 单元格值（dict/list/标量）"""
        if isinstance(v, dict):
            return v.get('text') or v.get('value') or ''
        if isinstance(v, list):
            return ' '.join(str(x.get('text', '') if isinstance(x, dict) else x) for x in v)
        return '' if v is None else str(v)

    existing_keys = set()
    total_rows = 0

    for attempt in range(1, 4):  # 网络抖动重试 3 次
        offset = 0
        try:
            while True:
                cmd = [
                    'lark-cli', 'base', '+record-list',
                    '--base-token', FEISHU_BASE_TOKEN,
                    '--table-id', FEISHU_TABLE_ID,
                    '--as', 'user',
                    '--limit', '200',
                    '--offset', str(offset),
                    '--format', 'json'
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)

                if result.returncode != 0:
                    print(f"  ⚠️ 查询失败(rc={result.returncode})，跳过去重检查: {result.stderr[:120]}")
                    return set()

                try:
                    payload = json.loads(result.stdout)
                except json.JSONDecodeError:
                    print(f"  ⚠️ 输出 JSON 解析失败（第 {attempt} 次重试）")
                    break  # 跳出 while，进入外层重试

                if not payload.get('ok'):
                    print(f"  ⚠️ API错误: {payload.get('error', {}).get('message', '')[:120]}，跳过去重检查")
                    return set()

                data_node = payload.get('data', {})
                fields = data_node.get('fields', [])
                rows = data_node.get('data', [])

                # 动态定位列索引（不硬编码，兼容字段顺序变化）
                try:
                    idx_title = fields.index('中文标题')
                    idx_source = fields.index('来源')
                except ValueError:
                    print("  ⚠️ 未找到字段列（中文标题/来源），跳过去重检查")
                    return set()

                for row in rows:
                    if len(row) <= max(idx_title, idx_source):
                        continue
                    title_clean = _extract_cell(row[idx_title])[:30].strip()
                    source_clean = re.sub(r'[\[\]"\'\"]', '', _extract_cell(row[idx_source])).strip()
                    if title_clean and source_clean:
                        existing_keys.add((title_clean, source_clean))
                        total_rows += 1

                if not data_node.get('has_more') or not rows:
                    break
                offset += len(rows)

            print(f"  ✅ 查询完成，飞书表已有 {total_rows} 条记录（{len(existing_keys)} 组唯一键）")
            return existing_keys

        except Exception as e:
            print(f"  ⚠️ 查询异常（{e}），第 {attempt} 次重试...")
            time.sleep(2)

    print("  ⚠️ 重试3次仍失败，跳过去重检查")
    return set()


def deduplicate_articles(articles, existing_keys):
    """
    基于唯一键去重：过滤掉飞书中已存在的文章

    Args:
        articles: 待同步的文章列表
        existing_keys: 飞书已有的 (title[:30], source) 集合

    Returns:
        tuple: (去重后的文章列表, 过滤掉的重复数量)
    """
    if not existing_keys:
        return articles, 0

    unique_articles = []
    duplicate_count = 0
    dup_titles = []

    for art in articles:
        title_key = (art.get('title', '') or '')[:30].strip()
        source_key = (art.get('source', '') or '').strip()
        unique_key = (title_key, source_key)

        if unique_key in existing_keys:
            duplicate_count += 1
            if len(dup_titles) < 5:  # 只记录前5条重复标题
                dup_titles.append(art.get('title', '未知')[:30])
        else:
            unique_articles.append(art)

    if duplicate_count > 0:
        print(f"\n  🔍 去重结果:")
        print(f"     • 输入: {len(articles)} 条")
        print(f"     • 重复: {duplicate_count} 条 (已过滤)")
        print(f"     • 新增: {len(unique_articles)} 条")
        if dup_titles:
            print(f"     • 重复示例:")
            for t in dup_titles:
                print(f"       - {t}...")
    else:
        print(f"  ✅ 无重复，{len(articles)} 条全部为新增")

    return unique_articles, duplicate_count


def sync_to_feishu(articles, dry_run=False):
    """
    将文章列表同步到飞书多维表格（含去重检查）
    使用 lark-cli base +record-batch-create 批量写入

    流程:
    1. 查询飞书表已有记录的唯一键
    2. 基于唯一键去重，过滤已存在的文章
    3. 仅同步新增的文章
    """
    import subprocess
    import tempfile

    if not articles:
        print("  ℹ️ 没有需要同步的数据")
        return 0

    # ⭐ V1.2新增：去重检查
    print("\n  🔄 执行去重检查...")
    existing_keys = get_existing_unique_keys()
    articles_to_sync, dup_count = deduplicate_articles(articles, existing_keys)

    if not articles_to_sync:
        print("\n  ℹ️ 所有文章均已存在，无需同步")
        return 0

    # 转换为飞书记录格式（仅转换去重后的数据）
    records = [convert_article_to_record(art) for art in articles_to_sync]
    
    if dry_run:
        print(f"\n📋 预览模式 - 将同步 {len(records)} 条记录 (已去重，原{len(articles)}条):")
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
