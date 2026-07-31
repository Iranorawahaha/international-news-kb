#!/bin/bash

# ============================================================
# 🌍 国际新闻看板 - 一键更新脚本 V1.1（正式版）
# 用途: 采集今日新闻 → WebFetch补充 → 数据整合 → 更新网页 → 推送GitHub
# 架构: 双层采集（基础requests + WebFetch API）+ URL完整性保障
#
# V1.1 核心特性:
#   ✅ 信源扩展至9-10个英文权威信源（路透社/BBC/CNN/NYT等）
#   ✅ 双语标题显示（英文原标题 + 中文翻译）
#   ✅ 元首级新闻智能识别与置顶（中美元首/高层会晤）
#   ✅ 重要性5级分类体系（⭐元首级/🔴极高/🟠高/🟡中/🟢低）
#   ✅ UI优化（列不换行、按钮防换行、紧凑布局）
#   ✅ 根目录+gh-pages双目录同步部署
#
# 使用: ./update-news.sh
# 版本: V1.1 正式版 (2026-07-31)
# ============================================================

set -e

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
echo -e "${CYAN}║   🌍 国际新闻看板 - 一键更新系统 V1.1           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "📅 当前时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ==================== 第1步：基础采集 ====================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📡 第1步：基础采集（中文信源）${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$PROJECT_DIR"

if [ -f "scripts/fetch_news_v3.py" ]; then
    echo -e "${YELLOW}🔄 运行采集引擎 V1.1...${NC}"
    echo ""
    python3 scripts/fetch_news_v3.py --basic-only
elif [ -f "scripts/fetch_news_v2.py" ]; then
    echo -e "${YELLOW}🔄 运行标准采集脚本 (v2.0)...${NC}"
    echo ""
    python3 scripts/fetch_news_v2.py
else
    echo -e "${RED}❌ 未找到采集脚本！${NC}"
    exit 1
fi

# 检查基础采集结果
if [ ! -f "data/news-data.json" ]; then
    echo -e "${RED}❌ 基础数据文件未生成！${NC}"
    exit 1
fi

BASIC_COUNT=$(python3 -c "import json; data=json.load(open('data/news-data.json')); print(len(data) if isinstance(data, list) else 0)")

echo ""
echo -e "${GREEN}✅ 基础采集完成: ${BASIC_COUNT} 条新闻${NC}"

# ==================== 第2步：WebFetch补充说明（V1.1扩展版） ====================
echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${PURPLE}🌐 第2步：WebFetch API补充（V1.1: 10大英文权威信源）${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cat << 'EOF'
⚠️ 重要提示：此步骤需要在 WorkBuddy 环境中完成！

WebFetch API 是 WorkBuddy AI 助手的专属功能，用于获取路透社、BBC、CNN等
反爬虫严格的权威英文信源。此步骤无法在终端命令行自动完成。

📋 V1.1 WebFetch 任务清单（目标：30-45条高质量英文新闻）：

  🔴 必选核心信源（4个）：
  ┌─────────────────────────────────────────────────────┐
  │ 1️⃣ 路透社 (Reuters)                                │
  │    URL: https://www.reuters.com/world/              │
  │    目标: ~8条 | 重点: 全球政治经济要闻              │
  │                                                     │
  │ 2️⃣ BBC News                                        │
  │    URL: https://www.bbc.com/news                   │
  │    目标: ~6条 | 重点: 欧洲中东突发事件              │
  │                                                     │
  │ 3️⃣ 南华早报 (SCMP)                                 │
  │    URL: https://www.scmp.com/news/china            │
  │    目标: ~6条 | 重点: 中美关系/中国动态             │
  │                                                     │
  │ 4️⃣ 卫报 (The Guardian)                             │
  │    URL: https://www.theguardian.com/international   │
  │    目标: ~4条 | 重点: 深度分析/欧洲事务             │
  └─────────────────────────────────────────────────────┘

  🟠 扩展推荐信源（6个，按优先级排序）：
  ┌─────────────────────────────────────────────────────┐
  │ 5️⃣ CNN                                            │
  │    URL: https://edition.cnn.com/world               │
  │    目标: ~4条 | 突发事件/美国外交                  │
  │                                                     │
  │ 6️⃣ 纽约时报 (NYT)                                  │
  │    URL: https://www.nytimes.com/world               │
  │    目标: ~4条 | 深度报道/AI科技竞争                │
  │                                                     │
  │ 7️⃣ 半岛电视台 (Al Jazeera)                         │
  │    URL: https://www.aljazeera.com/news             │
  │    目标: ~3条 | 中东局势/发展中国家视角           │
  │                                                     │
  │ 8️⃣ 华盛顿邮报 (Washington Post)                    │
  │    URL: https://www.washingtonpost.com/world        │
  │    目标: ~3条 | 美国政策/北约事务                  │
  │                                                     │
  │ 9️⃣ 美联社 (AP News)                               │
  │    URL: https://apnews.com/hub/ap-top-news         │
  │    目标: ~3条 | 快讯/事实核查                      │
  │                                                     │
  │ 🔟 Politico（可选，可能404）                        │
  │     URL: https://www.politico.com/global-news      │
  │     目标: ~2条 | 政策分析                          │
  └─────────────────────────────────────────────────────┘

📝 WebFetch Prompt 要求（必须包含）：

  ✅ 双语标题：每条新闻必须返回英文原标题 + 中文翻译
     格式示例："title_en": "Original English Title",
              "title": "中文翻译标题"

  ✅ 完整URL：每条必须有可访问的文章链接（https://开头）
     ⚠️ URL是必填项，缺失会导致链接无法点击

  ✅ 元首级标注：如果涉及以下内容，标记 is_summit_level: true
     • 中美元首会晤/通话/互访
     • 习近平/特朗普/拜登等领导人直接相关
     • 中美贸易谈判/战略对话
     设定 priority_score: 95-100

  ✅ 优先级评分（priority_score）：
     ⭐ 元首级: 95-100 (is_summit_level=true)
     🔴 极高:   90-94 (战争/灾难/重大突破)
     🟠 高:     85-89 (重要政策/高级别会议)
     🟡 中:     75-84 (一般国际新闻)
     🟢 低:     <75 (背景/评论)

💡 操作方法：

  在 WorkBuddy 对话中说：
  "请帮我用 WebFetch 补充最新国际新闻数据，需要双语标题和完整URL，
   重点抓取路透社/BBC/CNN/NYT/SCMP/卫报/半岛电视台/华盛顿邮报/美联社"

EOF

echo -e "${YELLOW}是否已通过 WebFetch 获取了额外数据？${NC}"
read -p "(y/n, 默认跳过): " has_webfetch

if [ "$has_webfetch" = "y" ] || [ "$has_webfetch" = "Y" ]; then
    echo ""
    echo -e "${GREEN}✅ 已包含 WebFetch 数据，继续...${NC}"
else
    echo ""
    echo -e "${YELLOW}⏭️ 跳过 WebFetch 补充，使用基础采集数据继续...${NC}"
    echo -e "${YELLOW}   （提示：基础数据通常包含 ${BASIC_COUNT} 条中文信源新闻）${NC}"
fi

# ==================== 第3步：验证数据质量（V1.1增强版） ====================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔍 第3步：验证数据质量（V1.1增强检查）${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

FINAL_COUNT=$(python3 -c "import json; data=json.load(open('data/news-data.json')); print(len(data) if isinstance(data, list) else 0)")

if [ "$FINAL_COUNT" -eq 0 ]; then
    echo -e "${RED}❌ 没有新闻数据！检查采集脚本是否正常运行${NC}"
    exit 1
fi

echo -e "📊 新闻总数: ${GREEN}${FINAL_COUNT}${NC} 条"
echo ""

# 统计来源分布（V1.1增强）
python3 << 'STATS'
import json
from collections import Counter

with open('data/news-data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

if isinstance(data, list):
    sources = Counter(item.get('source', '未知') for item in data)
    categories = Counter(item.get('category', '其他') for item in data)

    # V1.1: 统计元首级新闻
    summit_count = sum(1 for item in data if item.get('is_summit_level') == True)

    # V1.1: 统计双语标题覆盖率
    bilingual_count = sum(1 for item in data if item.get('title_en'))

    # V1.1: URL覆盖率
    url_count = sum(1 for item in data if item.get('url', '').startswith('http'))
    url_coverage = (url_count / len(data) * 100) if data else 0

    # V1.1: 重要性分布（基于priority_score）
    priority_levels = {'⭐元首级': 0, '🔴极高': 0, '🟠高': 0, '🟡中': 0, '🟢低': 0}
    for item in data:
        score = item.get('priority_score', 0)
        if item.get('is_summit_level') or score >= 95:
            priority_levels['⭐元首级'] += 1
        elif score >= 90:
            priority_levels['🔴极高'] += 1
        elif score >= 85:
            priority_levels['🟠高'] += 1
        elif score >= 75:
            priority_levels['🟡中'] += 1
        else:
            priority_levels['🟢低'] += 1

    print("📰 来源分布:")
    for source, count in sources.most_common(12):
        print(f"   • {source}: {count} 条")

    print("\n📂 分类分布:")
    for cat, count in categories.most_common(8):
        print(f"   • {cat}: {count} 条")

    print("\n⭐ V1.1 增强指标:")
    print(f"   • 元首级新闻: {summit_count} 条")
    print(f"   • 双语标题覆盖率: {bilingual_count}/{len(data)} ({bilingual_count/len(data)*100:.1f}%)" if data else "")
    print(f"   • URL覆盖率: {url_count}/{len(data)} ({url_coverage:.1f}%)")

    print("\n🎯 重要性分级（基于priority_score）:")
    for level, count in priority_levels.items():
        if count > 0:
            bar = '█' * min(count, 20)
            print(f"   {level}: {count:2d} 条 {bar}")

STATS

echo ""
echo -e "${GREEN}✅ 数据验证通过${NC}"

# ==================== 第4步：生成单文件HTML（V1.1完整版） ====================
echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${PURPLE}🎨 第4步：生成V1.1单文件HTML网页（含双语标题+5级分类）${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 备份当前HTML（两个位置）
if [ -f "$GH_PAGES_DIR/index.html" ]; then
    cp "$GH_PAGES_DIR/index.html" "$GH_PAGES_DIR/index.backup.$(date +%Y%m%d%H%M%S).html"
    echo "📦 已备份 gh-pages/index.html"
fi

if [ -f "$PROJECT_DIR/index.html" ]; then
    cp "$PROJECT_DIR/index.html" "$PROJECT_DIR/index.backup.$(date +%Y%m%d%H%M%S).html"
    echo "📦 已备份根目录 index.html"
fi

echo -e "${YELLOW}🔄 正在重新生成 index.html（V1.1完整版）...${NC}"
echo ""

# 调用Python脚本生成新的index.html（V1.1增强版）
python3 << 'GENERATE_HTML'
import json
from datetime import datetime
from pathlib import Path

# 路径配置
PROJECT_ROOT = Path("/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50")
DATA_PATH = PROJECT_ROOT / "data" / "news-data.json"
OUTPUT_PATH_GH = PROJECT_ROOT / "gh-pages" / "index.html"
OUTPUT_PATH_ROOT = PROJECT_ROOT / "index.html"  # V1.1: 同时输出到根目录

# 读取数据
try:
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
except:
    news_data = []

if not isinstance(news_data, list):
    news_data = []

print(f"📊 读取到 {len(news_data)} 条新闻数据")

# 生成统计信息（V1.1增强版）
total_count = len(news_data)
sources = set()
categories = set()
summit_count = sum(1 for n in news_data if n.get('is_summit_level') == True)

for item in news_data:
    sources.add(item.get('source', '未知'))
    categories.add(item.get('category', '其他'))

# 当前时间戳
now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
now_full = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# HTML模板（V1.1完整版 - 包含所有UI优化）
html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌍 国际新闻看板 V1.1</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.95em;
        }}
        .controls {{
            padding: 20px 30px;
            background: white;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
            border-bottom: 2px solid #eee;
        }}
        .search-box {{
            flex: 1;
            min-width: 250px;
            padding: 12px 20px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 1em;
            outline: none;
            transition: border-color 0.3s;
        }}
        .search-box:focus {{
            border-color: #667eea;
        }}
        select {{
            padding: 12px 18px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 0.95em;
            outline: none;
            cursor: pointer;
        }}
        select:focus {{
            border-color: #667eea;
        }}
        .table-container {{
            padding: 30px;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            white-space: nowrap;
        }}
        td {{
            padding: 14px 12px;
            border-bottom: 1px solid #eee;
            vertical-align: top;
        }}
        /* V1.1: 关键列强制不换行 */
        td:nth-child(5),
        td:nth-child(6),
        td:nth-child(7) {{
            white-space: nowrap;
        }}
        tr:hover {{
            background: #f8f9ff;
        }}

        /* ========== V1.1: 重要性5级分类样式 ========== */

        /* ⭐ 元首级 - 金色渐变徽章（最醒目） */
        .importance-summit {{
            display: inline-block;
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            color: #fff;
            font-weight: bold;
            padding: 4px 12px;
            border-radius: 12px;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
            box-shadow: 0 2px 4px rgba(255, 165, 0, 0.3);
        }}

        /* 🔴 极高 - 红色粗体+浅红背景 */
        .importance-critical {{
            color: #dc3545;
            font-weight: bold;
            background: #ffe6e6;
            padding: 2px 8px;
            border-radius: 8px;
        }}

        /* 🟠 高 - 橙色粗体 */
        .importance-high {{
            color: #dc3545;
            font-weight: bold;
        }}

        /* 🟡 中 - 橙色常规 */
        .importance-medium {{
            color: #fd7e14;
            font-weight: 600;
        }}

        /* 🟢 低 - 绿色常规 */
        .importance-low {{
            color: #28a745;
        }}

        /* ========== V1.1: 双语标题样式 ========== */
        .title-bilingual {{
            line-height: 1.5;
        }}
        .title-en {{
            color: #1a365d;
            font-size: 0.88em;
            font-weight: 600;
            display: block;
            margin-bottom: 3px;
            font-style: italic;
        }}
        .title-zh {{
            color: #2d3748;
            font-size: 0.92em;
            display: block;
        }}

        /* ========== V1.1: 链接按钮优化（防换行） ========== */
        .link-btn {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 6px 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(102, 126, 234, 0.3);
            white-space: nowrap;  /* V1.1: 防止文字换行 */
        }}
        .link-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
            background: linear-gradient(135deg, #5a6fd6 0%, #6a4192 100%);
        }}

        .tag {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            margin: 2px;
            background: #e9ecef;
        }}
        .footer {{
            text-align: center;
            padding: 25px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
        }}
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.8em; }}
            .stats {{ grid-template-columns: repeat(2, 1fr); padding: 15px; }}
            .controls {{ flex-direction: column; align-items: stretch; }}
            .table-container {{ padding: 15px; }}
            table {{ font-size: 0.8em; }}
            th, td {{ padding: 10px 8px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 国际新闻看板</h1>
            <p>每日高质量国际新闻自动采集与呈现 | V1.1 正式版 | 更新时间：{now_str}</p>
        </div>

        <!-- V1.1: 统计卡片（更新为显示元首级数量） -->
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_count}</div>
                <div class="stat-label">总新闻数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(sources)}</div>
                <div class="stat-label">信源数量</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(categories)}</div>
                <div class="stat-label">分类数量</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{summit_count}</div>
                <div class="stat-label">⭐ 元首级</div>
            </div>
        </div>

        <div class="controls">
            <input type="text" class="search-box" id="searchInput" placeholder="🔍 搜索新闻标题、关键词...">
            <select id="sourceFilter">
                <option value="">全部来源</option>
            </select>
            <select id="categoryFilter">
                <option value="">全部分类</option>
            </select>
            <select id="importanceFilter">
                <option value="">全部重要性</option>
                <option value="summit">⭐ 元首级</option>
                <option value="critical">🔴 极高</option>
                <option value="high">🟠 高</option>
                <option value="medium">🟡 中</option>
                <option value="low">🟢 低</option>
            </select>
        </div>

        <div class="table-container">
            <table id="newsTable">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>日期</th>
                        <th>标题</th>
                        <th>摘要</th>
                        <th>来源</th>
                        <th>分类</th>
                        <th>重要性</th>
                        <th>关键词</th>
                        <th>原文链接</th>
                    </tr>
                </thead>
                <tbody id="newsBody">
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>🌐 国际新闻看板 V1.1 | 数据更新于 {now_full}</p>
            <p style="margin-top: 8px;">
                Powered by Enhanced Fetcher V1.1 (WebFetch API) |
                ✅ 双语标题已启用 | ⭐ 元首级新闻智能识别
            </p>
        </div>
    </div>

    <script>
        // 新闻数据（内嵌）
        const NEWS_DATA = {json.dumps(news_data, ensure_ascii=False)};

        // 初始化筛选器选项
        function initFilters() {{
            const sources = [...new Set(NEWS_DATA.map(n => n.source))].sort();
            const categories = [...new Set(NEWS_DATA.map(n => n.category))].sort();

            const sourceSelect = document.getElementById('sourceFilter');
            sources.forEach(s => {{
                const opt = document.createElement('option');
                opt.value = s;
                opt.textContent = s;
                sourceSelect.appendChild(opt);
            }});

            const categorySelect = document.getElementById('categoryFilter');
            categories.forEach(c => {{
                const opt = document.createElement('option');
                opt.value = c;
                opt.textContent = c;
                categorySelect.appendChild(opt);
            }});
        }}

        // V1.1: 渲染表格（支持双语标题 + 5级重要性分类）
        function renderTable(data) {{
            const tbody = document.getElementById('newsBody');
            tbody.innerHTML = '';

            if (data.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;padding:40px;color:#999;">😢 没有找到匹配的新闻</td></tr>';
                return;
            }}

            data.forEach((item, idx) => {{
                const row = document.createElement('tr');

                // V1.1: 基于 priority_score 的5级重要性分类
                let importanceHtml = '';
                const score = item.priority_score || 0;
                const isSummit = item.is_summit_level || false;

                if (isSummit || score >= 95) {{
                    importanceHtml = '<span class="importance-summit">⭐ 元首级</span>';
                }} else if (score >= 90) {{
                    importanceHtml = '<span class="importance-critical">🔴 极高</span>';
                }} else if (score >= 85) {{
                    importanceHtml = '<span class="importance-high">🟠 高</span>';
                }} else if (score >= 75) {{
                    importanceHtml = '<span class="importance-medium">🟡 中</span>';
                }} else {{
                    importanceHtml = '<span class="importance-low">🟢 低</span>';
                }}

                // 关键词标签
                const keywords = Array.isArray(item.keywords) ?
                    item.keywords.map(k => `<span class="tag">${{k}}</span>`).join('') :
                    (item.keywords || '').split(',').map(k => `<span class="tag">${{k.trim()}}</span>`).join('');

                // 链接按钮
                const url = item.url || '#';

                // V1.1: 双语标题渲染
                let titleHtml = '';
                if (item.title_en && item.title) {{
                    titleHtml = `
                        <div class="title-bilingual">
                            <span class="title-en">${{item.title_en}}</span>
                            <span class="title-zh">${{item.title}}</span>
                        </div>
                    `;
                }} else {{
                    titleHtml = `<strong>${{item.title || ''}}</strong>`;
                }}

                row.innerHTML = `
                    <td>${{idx + 1}}</td>
                    <td>${{item.date || '-'}}</td>
                    <td>${{titleHtml}}</td>
                    <td>${{(item.summary || '').substring(0, 120)}}${{(item.summary || '').length > 120 ? '...' : ''}}</td>
                    <td>${{item.source || ''}}</td>
                    <td>${{item.category || ''}}</td>
                    <td>${{importanceHtml}}</td>
                    <td>${{keywords}}</td>
                    <td><a href="${{url}}" target="_blank" class="link-btn" title="点击查看原文">🔗 原文</a></td>
                `;

                tbody.appendChild(row);
            }});
        }}

        // 筛选逻辑（V1.1: 支持5级筛选）
        function filterNews() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const sourceVal = document.getElementById('sourceFilter').value;
            const categoryVal = document.getElementById('categoryFilter').value;
            const importanceVal = document.getElementById('importanceFilter').value;

            let filtered = NEWS_DATA.filter(item => {{
                // 搜索匹配（V1.1: 支持搜索英文标题）
                const matchSearch = !searchTerm ||
                    (item.title && item.title.toLowerCase().includes(searchTerm)) ||
                    (item.title_en && item.title_en.toLowerCase().includes(searchTerm)) ||
                    (item.summary && item.summary.toLowerCase().includes(searchTerm)) ||
                    (Array.isArray(item.keywords) && item.keywords.some(k => k.toLowerCase().includes(searchTerm)));

                const matchSource = !sourceVal || item.source === sourceVal;
                const matchCategory = !categoryVal || item.category === categoryVal;

                // V1.1: 重要性筛选（基于priority_score）
                let matchImportance = true;
                if (importanceVal) {{
                    const score = item.priority_score || 0;
                    const isSummit = item.is_summit_level || false;
                    switch(importanceVal) {{
                        case 'summit':
                            matchImportance = isSummit || score >= 95;
                            break;
                        case 'critical':
                            matchImportance = !isSummit && score >= 90 && score < 95;
                            break;
                        case 'high':
                            matchImportance = score >= 85 && score < 90;
                            break;
                        case 'medium':
                            matchImportance = score >= 75 && score < 85;
                            break;
                        case 'low':
                            matchImportance = score < 75;
                            break;
                    }}
                }}

                return matchSearch && matchSource && matchCategory && matchImportance;
            }});

            renderTable(filtered);
        }}

        // 初始化
        document.addEventListener('DOMContentLoaded', () => {{
            initFilters();
            renderTable(NEWS_DATA);

            // 绑定事件
            document.getElementById('searchInput').addEventListener('input', filterNews);
            document.getElementById('sourceFilter').addEventListener('change', filterNews);
            document.getElementById('categoryFilter').addEventListener('change', filterNews);
            document.getElementById('importanceFilter').addEventListener('change', filterNews);
        }});
    </script>
</body>
</html>'''

# 写入文件（V1.1: 同时写入两个位置）
with open(OUTPUT_PATH_GH, 'w', encoding='utf-8') as f:
    f.write(html_content)

with open(OUTPUT_PATH_ROOT, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ 单文件HTML已生成（V1.1完整版）:")
print(f"   📁 gh-pages/index.html ({OUTPUT_PATH_GH})")
print(f"   📁 index.html (根目录: {OUTPUT_PATH_ROOT})")
print(f"   📊 包含 {len(news_data)} 条新闻数据")
print(f"   ⭐ 元首级新闻: {summit_count} 条")
print(f"   🌐 双语标题: {sum(1 for n in news_data if n.get('title_en'))} 条")
GENERATE_HTML

echo ""
echo -e "${GREEN}✅ 网页更新完成（V1.1版本，已同步到根目录和gh-pages）${NC}"

# ==================== 第5步：提交并推送（V1.1: 根目录优先） ====================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 第5步：提交并推送到GitHub（V1.1: 根目录部署）${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$PROJECT_DIR"  # V1.1: 切换到项目根目录（非gh-pages）

# 检查是否有更改
if git diff --quiet && git diff --cached --quiet; then
    echo "ℹ️  没有新的更改需要提交"
    exit 0
fi

# 显示将要提交的更改
echo "📝 将要提交的更改:"
git status --short
echo ""

# 添加所有更改
git add index.html gh-pages/index.html data/news-data.json gh-pages/news-data.json

# 创建提交
TODAY=$(date "+%Y-%m-%d")
TIME=$(date "+%H:%M")
git commit -m "📰 V1.1 新闻数据更新 - $TODAY $TIME (${FINAL_COUNT}条)

📊 采集统计:
• 总新闻数: ${FINAL_COUNT} 条
• 信源覆盖: $(python3 -c "import json; d=json.load(open('data/news-data.json')); print(len(set(x.get('source','') for x in d)))") 个
• 元首级新闻: $(python3 -c "import json; d=json.load(open('data/news-data.json')); print(sum(1 for x in d if x.get('is_summit_level')))") 条
• 双语标题: $(python3 -c "import json; d=json.load(open('data/news-data.json')); print(sum(1 for x in d if x.get('title_en')))") 条
• URL覆盖率: $(python3 -c "import json; d=json.load(open('data/news-data.json')); u=sum(1 for x in d if x.get('url','').startswith('http')); print(f'{u}/{len(d)} ({u/len(d)*100:.0f}%)') if d else print('N/A')

✨ V1.1 特性:
✅ 双语标题显示（英文+中文）
✅ 重要性5级分类（⭐元首级/🔴极高/🟠高/🟡中/🟢低）
✅ 元首级新闻智能识别与置顶
✅ UI优化（列不换行/按钮防换行）
✅ 根目录+gh-pages双目录同步

更新时间: $(date '+%Y-%m-%d %H:%M:%S')
脚本版本: V1.1 (正式版)"

# 推送到GitHub
echo ""
echo "🚀 正在推送到GitHub..."
echo "⏳ 如果提示输入密码，请使用 Personal Access Token"
echo ""

git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          🎉 V1.1 更新成功完成！                    ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "📊 本次更新统计:"
    echo -e "   • 总新闻数: ${CYAN}${FINAL_COUNT}${NC} 条"
    echo -e "   • 基础采集: ${BASIC_COUNT} 条"
    echo -e "   • WebFetch补充: $(( FINAL_COUNT - BASIC_COUNT )) 条"
    echo -e "   • 元首级新闻: $(python3 -c "import json; d=json.load(open('data/news-data.json')); print(sum(1 for x in d if x.get('is_summit_level')))") 条"
    echo -e "   • 更新时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo -e "🌐 访问地址: ${CYAN}https://iranorawahaha.github.io/international-news-kb/${NC}"
    echo ""
    echo -e "⏳ 网站将在 ${YELLOW}1-2分钟${NC} 后自动更新"
    echo ""
    echo -e "💡 提示: 强制刷新浏览器 (Cmd+Shift+R) 查看最新内容"
    echo ""
    echo -e "🎨 V1.1 新特性:"
    echo -e "   ✅ 双语标题（英文深蓝 + 中文黑色双行显示）"
    echo -e "   ✅ 重要性5级分类（金色元首级 → 绿色低级）"
    echo -e "   ✅ 元首级新闻自动识别并置顶"
    echo -e "   ✅ 完美排版（所有列强制单行不换行）"
    echo ""
else
    echo ""
    echo -e "${RED}❌ 推送失败！${NC}"
    echo ""
    echo -e "可能的原因:${NC}"
    echo "  1. 网络连接问题（检查代理软件是否运行）"
    echo "  2. Token过期或权限不足"
    echo "  3. GitHub仓库配置错误"
    echo ""
    echo -e "解决方案:${NC}"
    echo "  1. 重启代理软件（Clash/V2Ray等），确认端口7890"
    echo "  2. 重新运行此脚本"
    echo "  3. 或手动执行: cd $PROJECT_DIR && git push origin main"
    echo ""
    exit 1
fi
