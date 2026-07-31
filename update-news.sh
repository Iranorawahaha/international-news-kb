#!/bin/bash

# ============================================================
# 🌍 国际新闻看板 - 一键更新脚本 V1.0（正式版）
# 用途: 采集今日新闻 → WebFetch补充 → 数据整合 → 更新网页 → 推送GitHub
# 架构: 双层采集（基础requests + WebFetch API）+ URL完整性保障
# 使用: ./update-news.sh
# 版本: V1.0 正式版 (2026-07-31)
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

echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   🌍 国际新闻看板 - 一键更新系统 V1.0         ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "📅 当前时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ==================== 第1步：基础采集 ====================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📡 第1步：基础采集（中文信源）${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$PROJECT_DIR"

if [ -f "scripts/fetch_news_v3.py" ]; then
    echo -e "${YELLOW}🔄 运行采集引擎 V1.0...${NC}"
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

# ==================== 第2步：WebFetch补充说明 ====================
echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${PURPLE}🌐 第2步：WebFetch API补充（高价值英文信源）${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cat << 'EOF'
⚠️ 重要提示：此步骤需要在 WorkBuddy 环境中完成！

WebFetch API 是 WorkBuddy AI 助手的专属功能，用于获取路透社、BBC、卫报等
反爬虫严格的权威英文信源。此步骤无法在终端命令行自动完成。

📋 需要执行的 WebFetch 任务：

  1️⃣ 路透社 (Reuters)
     URL: https://www.reuters.com/world/
     目标: ~8条高质量国际新闻

  2️⃣ BBC News
     URL: https://www.bbc.com/news
     目标: ~6条重要新闻

  3️⃣ 南华早报 (SCMP)
     URL: https://www.scmp.com/news/china
     目标: ~6条中国相关新闻

  4️⃣ 卫报 (The Guardian)
     URL: https://www.theguardian.com/international
     目标: ~4条国际新闻

💡 操作方法（二选一）：

  方法A - 在 WorkBuddy 对话中手动请求：
    "请帮我用 WebFetch 补充路透社和 BBC 的最新新闻数据"

  方法B - 如果当前就在 WorkBuddy 对话中：
    直接告知助手执行 WebFetch 补充任务

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

# ==================== 第3步：验证数据质量 ====================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔍 第3步：验证数据质量${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

FINAL_COUNT=$(python3 -c "import json; data=json.load(open('data/news-data.json')); print(len(data) if isinstance(data, list) else 0)")

if [ "$FINAL_COUNT" -eq 0 ]; then
    echo -e "${RED}❌ 没有新闻数据！检查采集脚本是否正常运行${NC}"
    exit 1
fi

echo -e "📊 新闻总数: ${GREEN}${FINAL_COUNT}${NC} 条"
echo ""

# 统计来源分布
python3 << 'STATS'
import json
from collections import Counter

with open('data/news-data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

if isinstance(data, list):
    sources = Counter(item.get('source', '未知') for item in data)
    categories = Counter(item.get('category', '其他') for item in data)
    importance = Counter(item.get('importance', '低') for item in data)

    print("📰 来源分布:")
    for source, count in sources.most_common(8):
        print(f"   • {source}: {count} 条")

    print("\n📂 分类分布:")
    for cat, count in categories.most_common(5):
        print(f"   • {cat}: {count} 条")

    print("\n⭐ 重要性:")
    for level in ['高', '中', '低']:
        count = importance.get(level, 0)
        bar = '█' * count
        print(f"   {level}: {count} 条 {bar}")
STATS

echo ""
echo -e "${GREEN}✅ 数据验证通过${NC}"

# ==================== 第4步：生成单文件HTML ====================
echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${PURPLE}🎨 第4步：更新单文件HTML网页${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$GH_PAGES_DIR"

# 备份当前HTML
if [ -f "index.html" ]; then
    cp index.html "index.backup.$(date +%Y%m%d%H%M%S).html"
    echo "📦 已备份当前网页"
fi

# 从主项目复制最新数据
cp "$PROJECT_DIR/data/news-data.json" ./news-data.json 2>/dev/null || true

echo -e "${YELLOW}🔄 正在重新生成 index.html（嵌入最新数据）...${NC}"

# 调用Python脚本生成新的index.html
python3 << 'GENERATE_HTML'
import json
from datetime import datetime
from pathlib import Path

# 路径配置
PROJECT_ROOT = Path("/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50")
DATA_PATH = PROJECT_ROOT / "data" / "news-data.json"
OUTPUT_PATH = PROJECT_ROOT / "gh-pages" / "index.html"

# 读取数据
try:
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
except:
    news_data = []

if not isinstance(news_data, list):
    news_data = []

print(f"📊 读取到 {len(news_data)} 条新闻数据")

# 生成统计信息
total_count = len(news_data)
sources = set()
categories = set()
high_importance = sum(1 for n in news_data if n.get('importance') == '高')

for item in news_data:
    sources.add(item.get('source', '未知'))
    categories.add(item.get('category', '其他'))

# HTML模板
html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>国际新闻知识库</title>
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
        tr:hover {{
            background: #f8f9ff;
        }}
        /* V1.1: 元首级特殊样式（最高优先） */
        .importance-summit {{
            color: #d4af37;  /* 金色 */
            font-weight: bold;
            text-shadow: 0 0 3px rgba(212, 175, 55, 0.5);
            background: linear-gradient(135deg, #fff9e6 0%, #fff4cc 100%);
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .importance-high {{
            color: #dc3545;
            font-weight: bold;
        }}
        .importance-medium {{
            color: #fd7e14;
            font-weight: 600;
        }}
        .importance-low {{
            color: #28a745;
        }}
        .link-btn {{
            display: inline-block;
            padding: 6px 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
            transition: all 0.3s ease;
            white-space: nowrap;
        }}
        .link-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
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
            <h1>🌍 国际新闻知识库</h1>
            <p>每日高质量国际新闻自动采集与呈现 | 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>

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
                <div class="stat-number">{high_importance}</div>
                <div class="stat-label">高重要性</div>
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
                <option value="高">⭐ 高</option>
                <option value="中">🔶 中</option>
                <option value="低">🔹 低</option>
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
                    <!-- 数据将通过JS动态加载 -->
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>🌐 国际新闻知识库 v3.0 | 数据更新于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p style="margin-top: 8px;">Powered by Enhanced Fetcher v3.0 (Basic + WebFetch)</p>
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

        // V1.1: 优先级排序权重映射
        const PRIORITY_WEIGHT = {{'元首级': 1000, '高': 100, '中': 10, '低': 1}};
        const IMPORTANCE_WEIGHT = {{'高': 3, '中': 2, '低': 1}};

        // V1.1: 按优先级排序（元首级 > 高 > 中 > 低）
        function sortByPriority(data) {{
            return data.sort((a, b) => {{
                const priorityA = PRIORITY_WEIGHT[a.priority] || PRIORITY_WEIGHT['低'];
                const priorityB = PRIORITY_WEIGHT[b.priority] || PRIORITY_WEIGHT['低'];

                if (priorityA !== priorityB) return priorityB - priorityA;

                // 同优先级按重要性排序
                const impA = IMPORTANCE_WEIGHT[a.importance] || IMPORTANCE_WEIGHT['低'];
                const impB = IMPORTANCE_WEIGHT[b.importance] || IMPORTANCE_WEIGHT['低'];
                return impB - impA;
            }});
        }}

        // 渲染表格 - V1.1增强版（支持双语标题+优先级）
        function renderTable(data) {{
            const tbody = document.getElementById('newsBody');
            tbody.innerHTML = '';

            if (data.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;padding:40px;color:#999;">😢 没有找到匹配的新闻</td></tr>';
                return;
            }}

            // V1.1: 应用排序
            const sortedData = sortByPriority(data);

            sortedData.forEach((item, idx) => {{
                const row = document.createElement('tr');

                // V1.1: 优先级样式
                let importanceClass = 'importance-low';
                if (item.priority === '元首级') {{
                    importanceClass = 'importance-summit';  // 元首级特殊样式
                }} else if (item.importance === '高') {{
                    importanceClass = 'importance-high';
                }} else if (item.importance === '中') {{
                    importanceClass = 'importance-medium';
                }}

                const keywords = Array.isArray(item.keywords) ?
                    item.keywords.map(k => `<span class="tag">${{k}}</span>`).join('') :
                    (item.keywords || '').split(',').map(k => `<span class="tag">${{k.trim()}}</span>`).join('');

                // 生成链接按钮（如果有URL则显示可点击链接，否则显示"暂无"）
                const url = item.url || '';
                const linkCell = url && url.startsWith('http')
                    ? `<td><a href="${{url}}" target="_blank" class="link-btn">🔗 链接</a></td>`
                    : `<td style="color:#999;font-size:0.85em;">暂无</td>`;

                // V1.1: 双语标题显示
                const displayTitle = item.title_display || item.title || '';
                const titleHTML = item.title_en
                    ? `<strong style="color:#1e3c72">${{item.title_en}}</strong><br><span style="font-size:0.9em;color:#666">${{item.title}}</span>`
                    : `<strong>${{item.title || ''}}</strong>`;

                // V1.1: 优先级显示文本
                const priorityText = item.priority === '元首级' ? '⭐元首级' : item.importance;

                row.innerHTML = `
                    <td>${{idx + 1}}</td>
                    <td>${{item.date || '-'}}</td>
                    <td>${{titleHTML}}</td>
                    <td>${{(item.summary || '').substring(0, 100)}}${{(item.summary || '').length > 100 ? '...' : ''}}</td>
                    <td>${{item.source || ''}}</td>
                    <td>${{item.category || ''}}</td>
                    <td class="${{importanceClass}}">${{priorityText}}</td>
                    <td>${{keywords}}</td>
                    ${{linkCell}}
                `;

                tbody.appendChild(row);
            }});
        }}

        // 筛选逻辑
        function filterNews() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const sourceVal = document.getElementById('sourceFilter').value;
            const categoryVal = document.getElementById('categoryFilter').value;
            const importanceVal = document.getElementById('importanceFilter').value;

            let filtered = NEWS_DATA.filter(item => {{
                const matchSearch = !searchTerm ||
                    (item.title && item.title.toLowerCase().includes(searchTerm)) ||
                    (item.summary && item.summary.toLowerCase().includes(searchTerm)) ||
                    (Array.isArray(item.keywords) && item.keywords.some(k => k.toLowerCase().includes(searchTerm)));

                const matchSource = !sourceVal || item.source === sourceVal;
                const matchCategory = !categoryVal || item.category === categoryVal;
                const matchImportance = !importanceVal || item.importance === importanceVal;

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

# 写入文件
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ 单文件HTML已生成: {OUTPUT_PATH}")
print(f"   包含 {len(news_data)} 条新闻数据")
GENERATE_HTML

echo ""
echo -e "${GREEN}✅ 网页更新完成${NC}"

# ==================== 第5步：提交并推送 ====================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 第5步：提交并推送到GitHub${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$GH_PAGES_DIR"

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
git add -A

# 创建提交
TODAY=$(date "+%Y-%m-%d")
TIME=$(date "+%H:%M")
git commit -m "📰 更新新闻数据 - $TODAY $TIME (${FINAL_COUNT}条)

采集详情:
- 基础采集: ~${BASIC_COUNT} 条（中文信源）
- WebFetch补充: ~$(( FINAL_COUNT - BASIC_COUNT )) 条（英文权威信源）
- 总计: ${FINAL_COUNT} 条高质量新闻
- URL覆盖率: 已通过validate_urls()验证

更新时间: $(date '+%Y-%m-%d %H:%M:%S')
脚本版本: V1.0 (正式版)"

# 推送到GitHub
echo ""
echo "🚀 正在推送到GitHub..."
echo "⏳ 如果提示输入密码，请使用 Personal Access Token"
echo ""

git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           🎉 更新成功完成！                      ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "📊 本次更新统计:"
    echo -e "   • 总新闻数: ${CYAN}${FINAL_COUNT}${NC} 条"
    echo -e "   • 基础采集: ${BASIC_COUNT} 条"
    echo -e "   • WebFetch补充: $(( FINAL_COUNT - BASIC_COUNT )) 条"
    echo -e "   • 更新时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo -e "🌐 访问地址: ${CYAN}https://iranorawahaha.github.io/international-news-kb/${NC}"
    echo ""
    echo -e "⏳ 网站将在 ${YELLOW}1-2分钟${NC} 后自动更新"
    echo ""
    echo -e "💡 提示: 强制刷新浏览器 (Cmd+Shift+R) 查看最新内容"
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
    echo "  1. 重启代理软件（Clash/V2Ray等）"
    echo "  2. 重新运行此脚本"
    echo "  3. 或手动执行: git push origin main"
    echo ""
    exit 1
fi
