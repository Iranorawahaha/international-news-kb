#!/bin/bash

# ============================================================
# 🌍 国际新闻看板 - 一键更新脚本 V1.3（Ira 信息看板版）
# 用途: 11个必选英文信源采集 → 清洗去重 → 排序 → 7天存档 → 生成网页 → 飞书同步 → GitHub推送
#
# V1.3 (2026-08-01):
#   ✅ 支持 --auto 无人值守模式（配合每日 9:30 自动刷新任务）
#   ✅ 数据整合 Python 语法修复（data['archive'] 缺括号）
#   ✅ 输出到 international-news.html（门户 index.html 不被覆盖）
#
# V1.2.3 (2026-08-01):
#   ✅ 彻底移除中文信源（BASIC_SOURCES 清空）
#   ✅ 全部11个英文信源改为必选（required: True）
#
# 使用: ./update-news.sh            # 交互模式（默认）
#       ./update-news.sh --auto    # 无人值守（跳过 read 提示）
# 版本: V1.3 (2026-08-01)
# ============================================================

set -e

# 参数解析: --auto 无人值守模式
AUTO_MODE=0
for _arg in "$@"; do
    case "$_arg" in
        --auto) AUTO_MODE=1 ;;
    esac
done

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 项目路径
PROJECT_DIR="/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50"
GH_PAGES_DIR="$PROJECT_DIR/gh-pages"

echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   🌍 国际新闻看板 - 一键更新系统 V1.3           ${NC}"
if [ "$AUTO_MODE" = "1" ]; then
    echo -e "${CYAN}║   🤖 无人值守模式 (--auto)                       ${NC}"
fi
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "📅 当前时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ==================== 第1步：基础采集 ====================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📡 第1步：基础采集（⚠️ 中文信源已弃用）${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⚠️ V1.2.3: 中文信源已弃用，跳过基础采集${NC}"
echo -e "${YELLOW}   所有新闻将通过 WebFetch API 从英文权威信源获取${NC}"
echo ""

# ==================== 第2步：WebFetch补充说明 ====================
echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${PURPLE}🌐 第2步：WebFetch API（11大英文权威信源V1.2.3）${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cat << 'EOF'
⚠️ 此步骤需要在 WorkBuddy 环境中完成！

📋 WebFetch 任务清单（V1.2.3 全部信源均为必选）：

  🔴 必选(11): 路透社 / BBC / 南华早报 / 卫报 / CNN / 纽约时报 / 华尔街日报 / 半岛电视台 / Politico / 华盛顿邮报 / 美联社

📝 全部信源必须完成！中文信源已弃用，仅依赖英文权威信源。
✅ 要求: 双语标题 + 完整URL + 元首级标注 + priority_score

💡 在 WorkBuddy 中说:
  "请用 WebFetch 从11个必选英文信源收集最新国际新闻"

EOF

# V1.3: --auto 无人值守模式直接跳过交互提示，使用已有 webfetch 数据
if [ "$AUTO_MODE" = "1" ]; then
    if [ -f "$PROJECT_DIR/data/news-webfetch.json" ]; then
        echo -e "${GREEN}✅ [--auto] 使用已有 WebFetch 数据: data/news-webfetch.json${NC}"
    else
        echo -e "${YELLOW}⚠️ [--auto] 未找到 webfetch 数据，使用现有存档继续${NC}"
    fi
else
    read -p "是否已通过 WebFetch 获取了额外数据？(y/n, 默认跳过): " has_webfetch
    if [ "$has_webfetch" = "y" ] || [ "$has_webfetch" = "Y" ]; then
        echo -e "${GREEN}✅ 已包含 WebFetch 数据${NC}"
    else
        echo -e "${YELLOW}⏭️ 跳过 WebFetch，使用基础采集数据继续...${NC}"
    fi
fi

# ==================== 第3步：V1.2.1 数据整合（质量控制版）====================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📦 第3步：V1.2.1 数据整合（去重+清洗+排序）${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

python3 << 'INTEGRATE_V121'
import json
import sys
import re
from datetime import datetime, timedelta
from collections import OrderedDict

DATA_FILE = 'data/news-data.json'
RETENTION_DAYS = 7

# ==================== 质量控制常量 ====================
MIN_TITLE_LENGTH = 5              # 最小标题长度
MIN_PRIORITY_SCORE = 1            # 最小重要性分数（0分为垃圾）

# 导航页面关键词黑名单（这些不是真实新闻）
NAVIGATION_KEYWORDS = [
    '导航', '首页', '首页导航', '网站地图', 'sitemap',
    '联系我们', '关于我们', '版权声明', '隐私政策',
    '用户协议', '登录', '注册', '搜索', '更多'
]

# 过期事件关键词（历史新闻，不应混入当日）
EXPIRED_EVENT_KEYWORDS = [
    'APEC领导人非正式会议',
    '对韩国进行国事访问',
    '对朝鲜进行国事访问',
    '出席博鳌亚洲论坛',
    '出席G20峰会',
    '出席金砖峰会'
]

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"  ⚠️ 无法加载数据文件: {e}")
        return {"version": "1.2", "archive": {}, "dates": [], "stats": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def convert_v11_to_v12(old_list):
    archive = {}
    for article in old_list:
        date_str = article.get('date', datetime.now().strftime('%Y-%m-%d'))
        if date_str not in archive:
            archive[date_str] = []
        archive[date_str].append(article)
    for date_str in archive:
        archive[date_str].sort(key=lambda x: x.get('priority_score', 0), reverse=True)
    return archive

def cleanup_old(archive):
    cutoff = (datetime.now() - timedelta(days=RETENTION_DAYS)).strftime('%Y-%m-%d')
    return {d: arts for d, arts in archive.items() if d >= cutoff}

def is_garbage_article(article):
    """判断是否为垃圾文章"""
    title = article.get('title', '') or ''
    title_en = article.get('title_en', '') or ''
    score = article.get('priority_score', 0)
    
    if len(title.strip()) < MIN_TITLE_LENGTH and len(title_en.strip()) < MIN_TITLE_LENGTH:
        return True, "标题过短"
    
    if score == 0:
        combined_text = (title + ' ' + title_en).lower()
        for kw in NAVIGATION_KEYWORDS:
            if kw.lower() in combined_text:
                return True, f"导航页面(关键词: {kw})"
    
    combined_text = (title + ' ' + title_en)
    for kw in EXPIRED_EVENT_KEYWORDS:
        if kw in combined_text:
            return True, f"过期事件(关键词: {kw})"
    
    return False, None

def clean_articles(articles):
    """清洗文章列表，移除垃圾文章"""
    cleaned = []
    removed_count = 0
    removal_reasons = {}
    
    for art in articles:
        is_garbage, reason = is_garbage_article(art)
        if is_garbage:
            removed_count += 1
            removal_reasons[reason] = removal_reasons.get(reason, 0) + 1
            print(f"    🗑️  移除垃圾: {art.get('title', '')[:40]}... ({reason})")
        else:
            cleaned.append(art)
    
    return cleaned, removed_count, removal_reasons

def deduplicate_articles(articles):
    """去重处理（基于唯一键: title前30字符 + source）"""
    seen_keys = set()
    unique_articles = []
    duplicate_count = 0
    
    for art in articles:
        title = art.get('title', '') or ''
        source = art.get('source', '') or '未知'
        unique_key = (title[:30], source)
        
        if unique_key not in seen_keys:
            seen_keys.add(unique_key)
            unique_articles.append(art)
        else:
            duplicate_count += 1
            print(f"    🔁 重复移除: {title[:40]}... (来源: {source})")
    
    return unique_articles, duplicate_count

def sort_by_importance(articles):
    """按重要性排序（元首级优先，然后按priority_score降序）"""
    def sort_key(art):
        summit = 1 if art.get('is_summit_level') else 0
        score = art.get('priority_score') or 0
        return (-summit, -score)
    
    return sorted(articles, key=sort_key)

def update_stats(data):
    total = sum(len(arts) for arts in data['archive'].values())
    data['dates'] = sorted(data['archive'].keys(), reverse=True)
    data['stats'] = {
        'totalArticles': total,
        'dateCount': len(data['dates']),
        'latestDate': data['dates'][0] if data['dates'] else None,
        'oldestDate': data['dates'][-1] if data['dates'] else None,
    }

# ==================== 主逻辑 ====================
print("🔄 正在执行 V1.2.1 数据整合（含质量控制）...")
print("=" * 60)

data = load_data()

if isinstance(data, list):
    print("  📝 检测到V1.1格式，正在转换为V1.2...")
    old_archive = convert_v11_to_v12(data)
    data = {
        "version": "1.2",
        "lastUpdated": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "retentionDays": RETENTION_DAYS,
        "archive": old_archive,
        "dates": [],
        "stats": {}
    }

if 'archive' not in data:
    data['archive'] = {}

today = datetime.now().strftime('%Y-%m-%d')

# 尝试从基础采集输出读取新数据
new_articles = []
temp_files = ['data/news-basic.json', 'data/news-webfetch.json']

for temp_file in temp_files:
    try:
        with open(temp_file, 'r', encoding='utf-8') as f:
            temp_data = json.load(f)
        
        if isinstance(temp_data, list):
            new_articles.extend(temp_data)
            print(f"  📥 从 {temp_file} 读取 {len(temp_data)} 条新闻")
        elif isinstance(temp_data, dict) and 'articles' in temp_data:
            new_articles.extend(temp_data['articles'])
            print(f"  📥 从 {temp_file} 读取 {len(temp_data['articles'])} 条新闻")
        # 关键词 schema 标准化：WebFetch 返回的 keywords 是字符串（如 "k1,k2,k3"），
        # 统一转为数组，避免前端 renderTable 抛 "keywords.map is not a function" 错误
        for art in new_articles[-len(temp_data) if isinstance(temp_data, list) else len(temp_data.get("articles", [])):]:
            kw = art.get("keywords") if isinstance(art, dict) else None
            if isinstance(kw, str):
                art["keywords"] = [k.strip() for k in kw.replace("，", ",").split(",") if k.strip()]
            elif kw is None:
                art["keywords"] = []
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"  ⚠️ 读取 {temp_file} 失败: {e}")

print(f"\n  📊 新获取新闻: {len(new_articles)} 条")

# 清洗现有今日数据
if today in data['archive']:
    existing_today = data['archive'][today]
    print(f"\n  🧹 清洗现有今日数据 ({len(existing_today)} 条)...")
    cleaned_existing, removed_exist, reasons_exist = clean_articles(existing_today)
    if removed_exist > 0:
        print(f"     移除 {removed_exist} 条垃圾文章:")
        for reason, count in reasons_exist.items():
            print(f"       • {reason}: {count} 条")
        data['archive'][today] = cleaned_existing
    else:
        print(f"     ✅ 现有数据质量良好")

# 清洗新数据
if new_articles:
    print(f"\n  🧹 清洗新获取数据 ({len(new_articles)} 条)...")
    cleaned_new, removed_new, reasons_new = clean_articles(new_articles)
    if removed_new > 0:
        print(f"     移除 {removed_new} 条垃圾文章:")
        for reason, count in reasons_new.items():
            print(f"       • {reason}: {count} 条")
    print(f"     ✅ 清洗后剩余: {len(cleaned_new)} 条")
else:
    cleaned_new = []
    print(f"\n  ℹ️ 无新数据需要处理")

# 去重处理
all_today_articles = []
if today in data['archive']:
    all_today_articles.extend(data['archive'][today])
all_today_articles.extend(cleaned_new)

if all_today_articles:
    print(f"\n  🔍 去重处理 (共 {len(all_today_articles)} 条)...")
    unique_articles, dup_count = deduplicate_articles(all_today_articles)
    if dup_count > 0:
        print(f"     移除 {dup_count} 条重复记录")
    print(f"     ✅ 去重后剩余: {len(unique_articles)} 条")
    
    print(f"\n  📊 按重要性排序...")
    sorted_articles = sort_by_importance(unique_articles)
    
    data['archive'][today] = sorted_articles
    
    summit_count = sum(1 for a in sorted_articles if a.get('is_summit_level'))
    print(f"     ✅ 排序完成: {len(sorted_articles)} 条 ({summit_count} ⭐元首级)")

# 清理超过7天的旧数据
print(f"\n  🗑️ 清理超过{RETENTION_DAYS}天的旧数据...")
before_cleanup = sum(len(v) for v in data['archive'].values())
data['archive'] = cleanup_old(data['archive'])
after_cleanup = sum(len(v) for v in data['archive'].values())
cleaned_count = before_cleanup - after_cleanup

if cleaned_count > 0:
    print(f"     清理了 {cleaned_count} 条过期数据")
else:
    print(f"     ✅ 无需清理")

update_stats(data)
data['lastUpdated'] = datetime.now().strftime('%Y-%m-%d %H:%M')

save_data(data)

print("\n" + "=" * 60)
print(f"✅ V1.2.1 数据整合完成！")
print(f"   总新闻数: {data['stats']['totalArticles']} 条")
print(f"   覆盖天数: {data['stats']['dateCount']} 天")
print(f"   最新日期: {data['stats']['latestDate']}")
print(f"   最旧日期: {data['stats']['oldestDate']}")

if data['dates']:
    print(f"\n   📅 日期分布:")
    for d in data['dates']:
        count = len(data['archive'][d])
        summit = sum(1 for a in data['archive'][d] if a.get('is_summit_level'))
        high_priority = sum(1 for a in data['archive'][d] if (a.get('priority_score') or 0) >= 90)
        print(f"     • {d}: {count} 条 ({summit} ⭐ | {high_priority} 🔴高重要)")

INTEGRATE_V121

echo ""
echo -e "${GREEN}✅ 数据整合完成（V1.2.1 - 含去重/清洗/排序）${NC}"

# V1.3: schema 统一（历史旧字段映射到标准字段）
echo ""
echo -e "${YELLOW}🧹 数据 schema 统一（record_id/archive_date → id/date）${NC}"
if [ -f "$PROJECT_DIR/scripts/normalize_schema.py" ]; then
    python3 "$PROJECT_DIR/scripts/normalize_schema.py"
else
    echo -e "${YELLOW}⚠️ 未找到 normalize_schema.py，跳过 schema 规范化${NC}"
fi

# V1.3.1: 更新 Ira 门户统计（国际新闻字段，AI 字段由 refresh_board.sh 更新，互不覆盖）
echo ""
echo -e "${YELLOW}🏠 更新 Ira 门户统计（国际新闻字段）${NC}"
if [ -f "$PROJECT_DIR/scripts/update_portal_stats.py" ]; then
    _news_total=$(python3 -c "import json;d=json.load(open('$PROJECT_DIR/data/news-data.json'));print(d.get('stats',{}).get('totalArticles','--'))" 2>/dev/null || echo "--")
    _news_last=$(python3 -c "import json;d=json.load(open('$PROJECT_DIR/data/news-data.json'));print(d.get('lastUpdated','--'))" 2>/dev/null || echo "--")
    # 今日新增：当天的新闻条数
    _today=$(date '+%Y-%m-%d')
    _news_today=$(python3 -c "
import json
d = json.load(open('$PROJECT_DIR/data/news-data.json'))
arc = d.get('archive', {})
print(len(arc.get('$_today', [])))
" 2>/dev/null || echo "--")
    python3 "$PROJECT_DIR/scripts/update_portal_stats.py" \
        --news-count "$_news_total" --news-date "$_news_last" \
        --news-today "$_news_today" \
        --latest "$(date '+%Y-%m-%d %H:%M')"
else
    echo -e "${YELLOW}⚠️ 未找到 update_portal_stats.py，跳过门户统计更新${NC}"
fi

# V1.4: 更新门户「今日日报」国际新闻要点（AI 要点由 refresh_board.sh 更新，互不覆盖）
if [ -f "$PROJECT_DIR/scripts/daily_brief.py" ]; then
    echo -e "${YELLOW}📰 更新门户今日日报（国际新闻要点）${NC}"
    python3 "$PROJECT_DIR/scripts/daily_brief.py" --news
else
    echo -e "${YELLOW}⚠️ 未找到 daily_brief.py，跳过日报更新${NC}"
fi

echo ""
echo -e "${GREEN}✅ 数据整合完成（V1.2追加模式）${NC}"

# ==================== 第4步：生成V1.2 HTML（含日期Tab栏）====================
echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${PURPLE}🎨 第4步：生成V1.2 HTML网页（V1.1经典UI风格）${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 备份当前HTML（国际新闻看板独立页面 international-news.html）
for f in "$GH_PAGES_DIR/international-news.html" "$PROJECT_DIR/international-news.html"; do
    if [ -f "$f" ]; then
        cp "$f" "$f.backup.$(date +%Y%m%d%H%M%S).html"
    fi
done
echo "📦 已备份现有HTML文件"

# 调用Python脚本生成V1.2 HTML（严格遵循V1.1简洁专业风格）
python3 << 'GENERATE_HTML_V12'
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50")
DATA_PATH = PROJECT_ROOT / "data" / "news-data.json"
# V1.3: 国际新闻看板独立页面，根目录 index.html 为「Ira 信息看板」门户，不被覆盖
OUTPUT_PATH_GH = PROJECT_ROOT / "gh-pages" / "international-news.html"
OUTPUT_PATH_ROOT = PROJECT_ROOT / "international-news.html"

# 读取V1.2格式数据
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    v12_data = json.load(f)

archive = v12_data.get('archive', {})
dates = v12_data.get('dates', [])
stats = v12_data.get('stats', {})
now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
now_full = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 展平所有文章用于内嵌
all_articles = []
for date_str in dates:
    for article in archive.get(date_str, []):
        all_articles.append(article)

total_count = len(all_articles)
sources = set(a.get('source','未知') for a in all_articles)
categories = set(a.get('category','其他') for a in all_articles)
summit_count = sum(1 for a in all_articles if a.get('is_summit_level'))

# 构建日期Tab HTML
tabs_html = '<button class="tab-btn active" data-date="all">全部(%d)</button>' % total_count
for d in dates:
    count = len(archive.get(d, []))
    tabs_html += '<button class="tab-btn" data-date="%s">%s(%d)</button>' % (d, d.replace('2026-', ''), count)

print(f"📊 生成V1.2 HTML: {total_count}条新闻, {len(dates)}天")

# ⭐ V1.2 HTML模板（严格遵循V1.1简洁专业风格）
html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌍 国际新闻看板 V1.2</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        
        /* 头部 - V1.1经典深蓝渐变 */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            text-align: center;
            color: white;
        }
        .header h1 { font-size: 28px; margin-bottom: 10px; font-weight: 600; }
        .header .subtitle { font-size: 14px; opacity: 0.95; line-height: 1.6; }
        
        /* ⭐ V1.2新增：日期Tab栏（V1.1简洁风格） */
        .date-tabs-container {
            background: white;
            border-radius: 8px;
            padding: 15px 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        .date-tabs-label {
            font-size: 13px;
            color: #333;
            margin-bottom: 10px;
            font-weight: 500;
        }
        .date-tabs {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }
        .tab-btn {
            padding: 6px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background: white;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
            color: #666;
        }
        .tab-btn:hover {
            border-color: #667eea;
            color: #667eea;
        }
        .tab-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: transparent;
            font-weight: 500;
        }
        .tab-btn .count {
            font-size: 11px;
            opacity: 0.8;
            margin-left: 4px;
        }
        
        /* 统计卡片 - V1.1简洁风格 */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        .stat-number { font-size: 32px; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; font-size: 14px; margin-top: 5px; }
        
        /* 筛选工具栏 - V1.1风格 */
        .filters {
            background: white;
            border-radius: 8px;
            padding: 15px 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }
        .search-box {
            flex: 1;
            min-width: 250px;
            padding: 10px 15px;
            border: 1px solid #e0e0e0;
            border-radius: 20px;
            font-size: 14px;
            outline: none;
        }
        .search-box:focus { border-color: #667eea; }
        .filter-select {
            padding: 10px 15px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            font-size: 14px;
            background: white;
            outline: none;
        }
        .filter-select:focus { border-color: #667eea; }
        
        /* 表格容器 */
        .table-container {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        table { width: 100%; border-collapse: collapse; }
        thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        th {
            padding: 15px 10px;
            text-align: left;
            font-weight: 500;
            font-size: 13px;
            white-space: nowrap;
        }
        td {
            padding: 12px 10px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 13px;
            vertical-align: top;
        }
        tr:hover { background: #f8f9ff; }
        
        /* 列宽定义 - V1.1标准9列布局 */
        th:nth-child(1), td:nth-child(1) { width: 40px; }   /* # */
        th:nth-child(2), td:nth-child(2) { width: 90px; }   /* 日期 */
        th:nth-child(3), td:nth-child(3) { width: 280px; }  /* 标题 */
        th:nth-child(4), td:nth-child(4) { width: auto; }   /* 摘要 */
        th:nth-child(5), td:nth-child(5) { width: 80px; }   /* 来源 */
        th:nth-child(6), td:nth-child(6) { width: 80px; }   /* 分类 */
        th:nth-child(7), td:nth-child(7) { width: 80px; }   /* 重要性 */
        th:nth-child(8), td:nth-child(8) { width: 120px; }  /* 关键词 */
        th:nth-child(9), td:nth-child(9) { width: 70px; }   /* 原文链接 */
        
        /* ⭐ 日期分隔行 - V1.1简洁风格 */
        .date-separator {
            background: #f0f4ff !important;
            font-weight: 600;
            color: #1a237e;
        }
        .date-separator td {
            padding: 10px 15px !important;
            font-size: 13px;
            border-bottom: 2px solid #667eea !important;
        }
        
        /* 标题样式 - V1.1标准 */
        .title-en {
            color: #1a237e;
            font-style: italic;
            font-size: 13px;
            margin-bottom: 3px;
            line-height: 1.4;
        }
        .title-zh {
            color: #333;
            font-weight: 500;
            font-size: 13px;
            line-height: 1.4;
        }
        
        /* 摘要样式 - V1.1标准 */
        .summary-text {
            color: #666;
            font-size: 12px;
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        /* 重要性标签 - V1.1标准配色 */
        .importance-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
            white-space: nowrap;
        }
        .badge-summit { background: #fff3e0; color: #e65100; }
        .badge-critical { background: #ffebee; color: #c62828; }
        .badge-high { background: #fff8e1; color: #f57f17; }
        .badge-medium { background: #e3f2fd; color: #1565c0; }
        .badge-low { background: #f5f5f5; color: #757575; }
        
        /* 链接按钮 - V1.1标准 */
        .link-btn {
            display: inline-block;
            padding: 5px 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 15px;
            font-size: 11px;
            white-space: nowrap;
        }
        .link-btn:hover { opacity: 0.9; }
        
        /* 关键词标签 - V1.1标准 */
        .keyword-tag {
            display: inline-block;
            padding: 2px 8px;
            background: #f0f0f0;
            border-radius: 10px;
            font-size: 11px;
            margin: 2px 2px;
            color: #555;
        }
        
        /* 页脚 - V1.1标准 */
        .footer {
            background: white;
            border-radius: 8px;
            padding: 15px 20px;
            margin-top: 20px;
            text-align: center;
            color: #666;
            font-size: 13px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .header h1 { font-size: 22px; }
            table { font-size: 12px; }
            th, td { padding: 8px 5px; }
        }
    </style>
</head>
<body>
<div class="container">
    <!-- 头部 - V1.1经典深蓝渐变 -->
    <div class="header">
        <h1>🌍 国际新闻看板</h1>
        <div class="subtitle">
            每日高质量国际新闻自动采集与呈现 | 
            <strong>V1.2 正式版（数据存档版）</strong> | 
            更新时间：<strong>''' + now_str + '''</strong>
        </div>
    </div>
    
    <!-- ⭐ V1.2新增：日期Tab栏（V1.1简洁风格） -->
    <div class="date-tabs-container">
        <div class="date-tabs-label">📅 选择查看日期：</div>
        <div class="date-tabs" id="dateTabs">
            ''' + tabs_html + '''
        </div>
    </div>
    
    <!-- 统计卡片 - V1.1简洁风格（5个卡片） -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">''' + str(total_count) + '''</div>
            <div class="stat-label">总新闻数</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">''' + str(len(sources)) + '''</div>
            <div class="stat-label">信源数量</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">''' + str(len(categories)) + '''</div>
            <div class="stat-label">分类数量</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">''' + str(summit_count) + '''</div>
            <div class="stat-label">⭐ 元首级</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">''' + str(stats.get('dateCount', len(dates))) + '''</div>
            <div class="stat-label">存档天数</div>
        </div>
    </div>
    
    <!-- 筛选工具栏 - V1.1风格 -->
    <div class="filters">
        <input type="text" class="search-box" id="searchBox" placeholder="🔍 搜索新闻标题、关键词..." oninput="filterNews()">
        <select class="filter-select" id="sourceFilter" onchange="filterNews()">
            <option value="">全部来源</option>
        </select>
        <select class="filter-select" id="categoryFilter" onchange="filterNews()">
            <option value="">全部分类</option>
        </select>
        <select class="filter-select" id="importanceFilter" onchange="filterNews()">
            <option value="">全部重要性</option>
            <option value="summit">⭐元首级</option>
            <option value="critical">🔴极高</option>
            <option value="high">🟠高</option>
            <option value="medium">🟡中</option>
            <option value="low">🟢低</option>
        </select>
    </div>
    
    <!-- 新闻表格 - 9列布局（V1.1标准） -->
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th style="width:40px">#</th>
                    <th style="width:90px">日期</th>
                    <th style="width:280px">标题</th>
                    <th>摘要</th>
                    <th style="width:80px">来源</th>
                    <th style="width:80px">分类</th>
                    <th style="width:80px">重要性</th>
                    <th style="width:120px">关键词</th>
                    <th style="width:70px">原文链接</th>
                </tr>
            </thead>
            <tbody id="newsTableBody">
                <!-- JavaScript动态填充 -->
            </tbody>
        </table>
    </div>
    
    <!-- 页脚 - V1.1标准 -->
    <div class="footer">
        🌐 国际新闻看板 V1.2 | 数据更新于 ''' + now_full + ''' | 
        Powered by Enhanced Fetcher V1.2 (WebFetch API) | 
        ✅ 双语标题已启用 | ⭐ 元首级新闻智能识别 | 📅 支持7天数据存档
    </div>
</div>

<script>
// V1.2 数据结构（按日期分组）
const NEWS_DATA = ''' + json.dumps(v12_data, ensure_ascii=False) + ''';

// 当前选中的日期
let selectedDate = 'all';

// 初始化筛选下拉框
function initFilters() {
    const sourceSet = new Set();
    const categorySet = new Set();
    
    Object.values(NEWS_DATA.archive).forEach(articles => {
        articles.forEach(art => {
            if (art.source) sourceSet.add(art.source);
            if (art.category) categorySet.add(art.category);
        });
    });
    
    const sourceFilter = document.getElementById('sourceFilter');
    [...sourceSet].sort().forEach(s => {
        const opt = document.createElement('option');
        opt.value = s; opt.textContent = s;
        sourceFilter.appendChild(opt);
    });
    
    const categoryFilter = document.getElementById('categoryFilter');
    [...categorySet].sort().forEach(c => {
        const opt = document.createElement('option');
        opt.value = c; opt.textContent = c;
        categoryFilter.appendChild(opt);
    });
}

// Tab切换事件
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        selectedDate = this.dataset.date;
        filterNews();
    });
});

// 获取重要性等级
function getImportance(score, isSummit) {
    if (isSummit || score >= 95) return { level: 'summit', label: '⭐元首级', cls: 'badge-summit' };
    if (score >= 90) return { level: 'critical', label: '🔴极高', cls: 'badge-critical' };
    if (score >= 85) return { level: 'high', label: '🟠高', cls: 'badge-high' };
    if (score >= 75) return { level: 'medium', label: '🟡中', cls: 'badge-medium' };
    return { level: 'low', label: '🟢低', cls: 'badge-low' };
}

// 过滤和渲染新闻（V1.2.1 - 含智能排序）
function filterNews() {
    const searchText = document.getElementById('searchBox').value.toLowerCase();
    const sourceFilter = document.getElementById('sourceFilter').value;
    const categoryFilter = document.getElementById('categoryFilter').value;
    const importanceFilter = document.getElementById('importanceFilter').value;

    let filteredArticles = [];

    // 根据选中日期获取数据
    if (selectedDate === 'all') {
        // 全部日期：按日期分组展示
        const sortedDates = Object.keys(NEWS_DATA.archive).sort().reverse();
        sortedDates.forEach(dateStr => {
            const articles = NEWS_DATA.archive[dateStr] || [];
            // 先添加日期分隔行
            filteredArticles.push({ _isDateSeparator: true, _date: dateStr, _count: articles.length });
            // 再添加该日期的文章（已按重要性预排序）
            filteredArticles.push(...articles.map(a => ({...a, _date: dateStr })));
        });
    } else {
        // 特定日期
        filteredArticles = (NEWS_DATA.archive[selectedDate] || []).map(a => ({...a, _date: selectedDate }));
    }

    // 应用筛选条件
    filteredArticles = filteredArticles.filter(item => {
        if (item._isDateSeparator) return true; // 保留分隔行

        if (sourceFilter && item.source !== sourceFilter) return false;
        if (categoryFilter && item.category !== categoryFilter) return false;

        const imp = getImportance(item.priority_score || 0, item.is_summit_level);
        if (importanceFilter && imp.level !== importanceFilter) return false;

        if (searchText) {
            const searchIn = [(item.title || ''), (item.title_en || ''), (item.summary || ''), (item.keywords || []).join(' ')].join(' ').toLowerCase();
            if (!searchIn.includes(searchText)) return false;
        }

        return true;
    });

    // ⭐ V1.2.1 新增：按重要性排序（确保元首级优先，然后按分数降序）
    filteredArticles = sortArticlesByImportance(filteredArticles);

    renderTable(filteredArticles);
}

// ⭐ V1.2.1 新增：按重要性排序函数
function sortArticlesByImportance(articles) {
    let result = [];
    let tempBatch = [];

    for (const item of articles) {
        if (item._isDateSeparator) {
            // 遇到日期分隔时，先排序当前批次，再添加分隔行
            if (tempBatch.length > 0) {
                tempBatch.sort((a, b) => {
                    // 1. 元首级排最前
                    const aSummit = a.is_summit_level ? -1 : 0;
                    const bSummit = b.is_summit_level ? -1 : 0;
                    if (aSummit !== bSummit) return aSummit - bSummit;
                    // 2. 同级别按priority_score降序
                    return (b.priority_score || 0) - (a.priority_score || 0);
                });
                result.push(...tempBatch);
                tempBatch = [];
            }
            result.push(item); // 添加分隔行
        } else {
            tempBatch.push(item);
        }
    }

    // 处理最后一个批次
    if (tempBatch.length > 0) {
        tempBatch.sort((a, b) => {
            const aSummit = a.is_summit_level ? -1 : 0;
            const bSummit = b.is_summit_level ? -1 : 0;
            if (aSummit !== bSummit) return aSummit - bSummit;
            return (b.priority_score || 0) - (a.priority_score || 0);
        });
        result.push(...tempBatch);
    }

    return result;
}

// 渲染表格（9列布局 - V1.1标准）
function renderTable(articles) {
    const tbody = document.getElementById('newsTableBody');
    tbody.innerHTML = '';
    
    let globalIndex = 0;
    
    articles.forEach((item) => {
        const tr = document.createElement('tr');
        
        if (item._isDateSeparator) {
            // 日期分隔行
            tr.className = 'date-separator';
            tr.innerHTML = `<td colspan="9">📅 ${item._date} (共 ${item._count} 条新闻)</td>`;
        } else {
            globalIndex++;
            const imp = getImportance(item.priority_score || 0, item.is_summit_level);
            // 兼容 keywords 为字符串（如 "k1,k2,k3"）或数组
            let kws = item.keywords;
            if (typeof kws === 'string') kws = kws.replace(/，/g, ',').split(',').map(s => s.trim()).filter(Boolean);
            if (!Array.isArray(kws)) kws = [];
            const keywords = kws.slice(0, 3);
            
            // 9列完整布局（V1.1标准）
            tr.innerHTML = `
                <td>${globalIndex}</td>
                <td style="white-space:nowrap">${item._date || ''}</td>
                <td>
                    <div class="title-en">${item.title_en || ''}</div>
                    <div class="title-zh">${item.title || ''}</div>
                </td>
                <td>
                    <div class="summary-text">${item.summary || '-'}</div>
                </td>
                <td style="white-space:nowrap">${item.source || ''}</td>
                <td style="white-space:nowrap">${item.category || ''}</td>
                <td><span class="importance-badge ${imp.cls}">${imp.label}</span></td>
                <td>${keywords.map(k => `<span class="keyword-tag">${k}</span>`).join('')}</td>
                <td>${item.url ? `<a href="${item.url}" target="_blank" class="link-btn">原文</a>` : '-'}</td>
            `;
        }
        
        tbody.appendChild(tr);
    });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    initFilters();
    filterNews();
});
</script>
</body>
</html>'''

with open(OUTPUT_PATH_GH,'w',encoding='utf-8') as f: f.write(html_content)
with open(OUTPUT_PATH_ROOT,'w',encoding='utf-8') as f: f.write(html_content)

print(f"✅ V1.3 HTML已生成:")
print(f"   📁 gh-pages/international-news.html")
print(f"   📁 international-news.html (根目录)")
print(f"   📊 {total_count}条新闻 | {len(dates)}天存档 | {summit_count}条元首级")
GENERATE_HTML_V12

# V1.3.2: 生成后立即 JS 语法预检（独立脚本，防 <script> 语法错误导致页面空白）
_HTML_OUTPUT="$PROJECT_DIR/international-news.html"
if [ -f "$PROJECT_DIR/scripts/check_js_syntax.py" ]; then
    if ! python3 "$PROJECT_DIR/scripts/check_js_syntax.py" "$_HTML_OUTPUT"; then
        echo -e "${RED}❌ JS 语法预检失败！中止部署，请检查第 4 步模板${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}✅ V1.2 网页已生成（V1.1经典UI + 日期Tab栏 + 7天存档）${NC}"

# ==================== 第4.5步：注入看板双向导航（幂等）⭐ ====================
echo ""
echo -e "${YELLOW}🔗 注入看板导航（国际新闻看板 ↔ AI 公司情报看板）${NC}"
if [ -f "$PROJECT_DIR/scripts/inject_nav.py" ]; then
    python3 "$PROJECT_DIR/scripts/inject_nav.py"
    echo -e "${GREEN}✅ 看板导航已就绪${NC}"
else
    echo -e "${YELLOW}⚠️ 未找到 scripts/inject_nav.py，跳过导航注入${NC}"
fi

# ==================== 第5步：飞书Base同步（增量追加）⭐ NEW ====================
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}☁️ 第5步：飞书Base同步（永久存档库）${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f "scripts/sync_to_feishu.py" ]; then
    echo -e "${YELLOW}🔄 正在同步数据到飞书Base表...${NC}"
    echo ""
    
    # 执行飞书同步（默认同步今天的数据）
    python3 scripts/sync_to_feishu.py --today
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ 飞书Base同步完成！${NC}"
        echo ""
        echo -e "📊 飞书存档表地址:"
        echo -e "   ${CYAN}https://my.feishu.cn/base/A2fdb93HLamcKgslr2rcopjRnfd${NC}"
        echo ""
        echo -e "💡 提示:"
        echo -e "   • 所有新闻将永久保存，不会清空"
        echo -e "   • 支持按日期/来源/分类/重要性筛选"
        echo -e "   • 可随时在飞书中查看历史记录"
    else
        echo ""
        echo -e "${RED}❌ 飞书同步失败！${NC}"
        echo -e "${YELLOW}⚠️ 不影响其他步骤，可稍后手动执行:${NC}"
        echo -e "   python3 scripts/sync_to_feishu.py --today"
    fi
else
    echo -e "${YELLOW}⚠️ 未找到飞书同步脚本 scripts/sync_to_feishu.py${NC}"
    echo -e "${YELLOW}   跳过飞书同步步骤...${NC}"
fi

# ==================== 第6步：提交并推送 ====================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 第6步：推送到GitHub Pages${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$PROJECT_DIR"

if git diff --quiet && git diff --cached --quiet; then
    echo "ℹ️  没有新的更改需要提交"
    exit 0
fi

FINAL_COUNT=$(python3 -c "import json;d=json.load(open('data/news-data.json'));print(sum(len(v) for v in d.get('archive',{}).values()) if isinstance(d,dict) else len(d))")

git add index.html international-news.html gh-pages/index.html gh-pages/international-news.html ai-company-intel.html gh-pages/ai-company-intel.html china-news.html gh-pages/china-news.html scripts/inject_nav.py scripts/update_portal_stats.py scripts/normalize_schema.py scripts/daily_brief.py scripts/fetch_china.py scripts/build_china.py data/news-data.json data/china-news.json scripts/data_converter_v12.py scripts/sync_to_feishu.py

TODAY=$(date "+%Y-%m-%d")
TIME=$(date "+%H:%M")
git commit -m "📰 V1.2 新闻更新 - $TODAY $TIME (${FINAL_COUNT}条)

📊 V1.2 存档统计:
• 总新闻数: ${FINAL_COUNT} 条
• 存档天数: $(python3 -c "import json;d=json.load(open('data/news-data.json'));print(len(d.get('dates',[])))") 天
• 信源覆盖: $(python3 -c "import json;d=json.load(open('data/news-data.json'));print(len(set(x.get('source','') for v in d.get('archive',{}).values() for x in v)))") 个
• 元首级新闻: $(python3 -c "import json;d=json.load(open('data/news-data.json'));print(sum(1 for v in d.get('archive',{}).values() for x in v if x.get('is_summit_level')))") 条

✨ V1.2 新特性:
✅ 7天数据存档（不再清空历史）
✅ 顶部日期Tab栏切换查看
✅ 按日期分组的数据结构
✅ 自动清理超过7天的旧数据
✅ 飞书Base永久存档（增量同步）⭐
✅ 保留V1.1所有特性（双语/5级分类/元首级/V1.1UI）

更新时间: $(date '+%Y-%m-%d %H:%M:%S')
脚本版本: V1.2 Final (数据存档版)"

echo ""
echo "🚀 正在推送到GitHub..."
git push origin main 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          🎉 V1.2 更新成功完成！                    ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "📊 本次更新:"
    echo -e "   • 总新闻数: ${CYAN}${FINAL_COUNT}${NC} 条"
    echo -e "   • 存档天数: $(python3 -c "import json;d=json.load(open('data/news-data.json'));print(len(d.get('dates',[])))") 天"
    echo -e "   • 更新时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo -e "🌐 GitHub Pages: ${CYAN}https://iranorawahaha.github.io/international-news-kb/${NC}"
    echo -e "📊 飞书存档表:   ${CYAN}https://my.feishu.cn/base/A2fdb93HLamcKgslr2rcopjRnfd${NC}"

    # V1.3: 构建健康检查（等待 CDN 构建完成后校验状态）
    echo ""
    echo -e "${YELLOW}🏗️ 执行 GitHub Pages 构建健康检查...${NC}"
    echo -e "   ⏳ 等待构建启动（约 45 秒）..."
    sleep 45
    _gh_token=$(echo "protocol=https
host=github.com
" | git credential fill 2>/dev/null | sed -n 's/^password=//p')
    if [ -n "$_gh_token" ]; then
        _build_status=$(curl -s -H "Authorization: token $_gh_token" \
            "https://api.github.com/repos/Iranorawahaha/international-news-kb/pages/builds" 2>/dev/null \
            | python3 -c "import json,sys;d=json.load(sys.stdin);print(d[0].get('status','unknown') if d else 'no-build')" 2>/dev/null || echo "unknown")
        if [ "$_build_status" = "built" ]; then
            echo -e "   ${GREEN}✅ 构建成功 (built) — 线上页面已更新${NC}"
        elif [ "$_build_status" = "building" ]; then
            echo -e "   ${YELLOW}⏳ 构建进行中 (building) — 稍后刷新页面即可${NC}"
        elif [ "$_build_status" = "errored" ]; then
            echo -e "   ${RED}❌ 构建失败 (errored)！请检查仓库文件${NC}"
        else
            echo -e "   ${YELLOW}⚠️ 无法获取构建状态 ($_build_status)${NC}"
        fi
    else
        echo -e "   ${YELLOW}⚠️ 未获取到 GitHub 凭证，跳过构建检查${NC}"
    fi
    echo ""
    echo -e "💡 V1.2 新功能:"
    echo -e "   ✅ 点击顶部日期Tab切换查看不同日期的新闻"
    echo -e "   ✅ 历史数据自动保留7天（本地）/ 永久（飞书）"
    echo -e "   ✅ 支持按日期筛选 + 搜索 + 分类过滤"
    echo -e "   ✅ 所有新闻自动同步到飞书Base存档库"
    # ===== C 方案：记录本次执行（供错过补跑检查） =====
    python3 "$(dirname "$0")/scripts/record_run.py" news --status ok
else
    echo -e "${RED}❌ 推送失败！请检查网络和代理设置${NC}"
    exit 1
fi
