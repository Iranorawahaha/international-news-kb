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

def deduplicate_articles(articles, archive=None):
    """去重处理（URL 规范化 + 跨日期去重 + 跨信源同题合并）

    1) URL 规范化：清洗 markdown 包裹 [url](url)，统一尾部斜杠
    2) 跨日期去重：URL 已存在于历史归档任意日期 → 跳过（每条新闻仅出现一次）
    3) 跨信源同题合并：不同媒体报道同一事件（标题相似度 ≥0.68），
       保留最权威信源（Reuters/AP 优先），其余同题移除
    返回: (unique_articles, duplicate_count)
    """
    import re as _re
    from difflib import SequenceMatcher as _SM

    # 权威信源优先级（同题合并时保留高优先级）
    AUTHORITY_ORDER = ['路透社', '美联社', 'BBC', 'CNN', '华盛顿邮报', '纽约时报',
                       '华尔街日报', '卫报', '半岛电视台', '南华早报', 'Politico']

    def _norm_url(u):
        """清洗 URL：解 markdown 包裹、去尾部斜杠、统一小写"""
        u = (u or '').strip()
        m = _re.match(r'^\[(.+?)\]\((.+?)\)$', u)
        if m:
            u = m.group(2)
        return u.rstrip('/').lower()

    def _norm_title(t):
        """规范化标题：去标点/空格/常见修饰词，仅留核心词"""
        t = (t or '').lower()
        # 去引号/标点/英文停用词
        t = _re.sub(r'[^a-z0-9\u4e00-\u9fff ]', ' ', t)
        t = _re.sub(r'\b(says?|said|to|on|in|for|the|a|an|of|and|with|as|at|by|from|after|before)\b', ' ', t)
        t = _re.sub(r'\s+', ' ', t).strip()
        return t[:50]

    def _similar(a, b):
        if not a or not b:
            return 0.0
        return _SM(None, a, b).ratio()

    seen_keys = set()
    hist_urls = set()
    if archive:
        for _date, _arts in archive.items():
            for _a in _arts:
                _u = _norm_url(_a.get('url'))
                if _u:
                    hist_urls.add(_u)

    unique_articles = []
    duplicate_count = 0

    for art in articles:
        title = art.get('title', '') or ''
        source = art.get('source', '') or '未知'
        url = _norm_url(art.get('url'))
        unique_key = (title[:30], source)
        url_key = f"URL::{url}" if url else None

        # 1) 跨日期去重（URL 规范化后）
        if url_key and url in hist_urls:
            duplicate_count += 1
            print(f"    🔁 跨日期重复跳过: {title[:40]}... (已在历史归档)")
            continue

        # 2) 跨信源同题合并：与已保留文章标题相似度过高 → 同题
        norm_t = _norm_title(title)
        merged = False
        for kept in unique_articles:
            kept_t = _norm_title(kept.get('title', ''))
            if kept_t and _similar(norm_t, kept_t) >= 0.68:
                # 同题：保留权威性更高的
                kept_src = kept.get('source', '')
                src_rank = AUTHORITY_ORDER.index(source) if source in AUTHORITY_ORDER else 99
                kept_rank = AUTHORITY_ORDER.index(kept_src) if kept_src in AUTHORITY_ORDER else 99
                if src_rank < kept_rank:
                    # 新来的更权威 → 替换
                    unique_articles[unique_articles.index(kept)] = art
                    print(f"    🔁 同题替换(更权威): {title[:40]}... (来源: {source})")
                else:
                    duplicate_count += 1
                    print(f"    🔁 同题合并: {title[:40]}... (来源: {source} → 保留{kept_src})")
                merged = True
                break
        if merged:
            continue

        # 3) 当天内去重：标题+来源 或 URL
        dup_this = unique_key in seen_keys or (url_key is not None and url_key in seen_keys)
        if not dup_this:
            seen_keys.add(unique_key)
            if url_key:
                seen_keys.add(url_key)
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
    # V1.3 修复：跨日期去重的"历史"应排除今天自身（否则今天已有数据被误判为历史重复清空）
    hist_archive = {d: v for d, v in data.get('archive', {}).items() if d != today}
    unique_articles, dup_count = deduplicate_articles(all_today_articles, archive=hist_archive)
    if dup_count > 0:
        print(f"     移除 {dup_count} 条重复记录")
    print(f"     ✅ 去重后剩余: {len(unique_articles)} 条")
    
    print(f"\n  📊 按重要性排序...")
    sorted_articles = sort_by_importance(unique_articles)
    
    data['archive'][today] = sorted_articles
    
    summit_count = sum(1 for a in sorted_articles if a.get('is_summit_level'))
    print(f"     ✅ 排序完成: {len(sorted_articles)} 条 ({summit_count} ⭐元首级)")

    # 真实报道日期重分配：URL 含更早日期（如 reuters/washingtonpost/news.cn）且该日期
    # 在保留窗口内 → 移到真实报道日期，避免 8/3 版面混入 7/31 已报道的旧闻
    import re as _re_url
    def _url_real_date(u):
        if not u: return None
        m = _re_url.search(r'(20\d{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])', u)
        if m: return f'{m.group(1)}-{m.group(2)}-{m.group(3)}'
        m2 = _re_url.search(r'/(20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])/', u)
        if m2: return f'{m2.group(1)}-{m2.group(2)}-{m2.group(3)}'
        return None

    _min_date = min(data['archive'].keys()) if data['archive'] else today
    _reassigned = 0
    for _art in list(data['archive'].get(today, [])):
        _real = _url_real_date(_art.get('url'))
        if _real and _real < today and _real >= _min_date:
            data['archive'].setdefault(_real, []).append(_art)
            data['archive'][today].remove(_art)
            _reassigned += 1
    if _reassigned > 0:
        print(f"     🔁 真实报道日期重分配: {_reassigned} 条移到 {_min_date}~{today} 对应日期")

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

# V1.5: 顶部日期表头按钮（横向）
tabs_html = '<button class="date-btn active" data-date="all">\U0001f4c5 全部日期（%d）</button>' % total_count
for d in dates:
    count = len(archive.get(d, []))
    tabs_html += '<button class="date-btn" data-date="%s">%s（%d）</button>' % (d, d.replace('2026-', '8'), count)

# 六大栏目统计（用于栏目 tab）
COLUMN_ORDER = ["中国", "美国", "欧洲", "地区热点", "国际会议", "其他"]
COLUMN_ICONS = {"中国": "🇨🇳", "美国": "🇺🇸", "欧洲": "🇪🇺", "地区热点": "🌍", "国际会议": "🏛️", "其他": "📌"}
column_counts = {c: 0 for c in COLUMN_ORDER}
for _d, _arts in archive.items():
    for _a in _arts:
        _col = _a.get('column', '其他')
        column_counts[_col] = column_counts.get(_col, 0) + 1
# V1.5: 左侧栏目侧边栏列表（悬浮 sticky）
column_tabs_html = '<button class="col-item active" data-column="all"><span class="ic">\U0001f4cb</span><span class="nm">全部</span><span class="cnt">%d</span></button>' % total_count
for _c in COLUMN_ORDER:
    _icon = COLUMN_ICONS.get(_c, '\U0001f4cc')
    _cnt = column_counts.get(_c, 0)
    column_tabs_html += '<button class="col-item" data-column="%s"><span class="ic">%s</span><span class="nm">%s</span><span class="cnt">%d</span></button>' % (_c, _icon, _c, _cnt)

print(f"📊 生成V1.2 HTML: {total_count}条新闻, {len(dates)}天, 栏目: {column_counts}")

# ⭐ V1.4 HTML模板（深色情报指挥风）— 从独立模板文件加载，占位符替换
TEMPLATE_PATH = PROJECT_ROOT / "scripts" / "intl_template_v15.html"
with open(TEMPLATE_PATH, 'r', encoding='utf-8') as _tf:
    html_content = _tf.read()

# 占位符替换
# 计算今日新增（北京时间今日）
from datetime import datetime, timezone, timedelta as _td
_TZ = timezone(_td(hours=8))
_today = datetime.now(_TZ).strftime('%Y-%m-%d')
_today_count = 0
for _d, _arts in archive.items():
    for _a in _arts:
        if _a.get('date') == _today:
            _today_count += 1

html_content = html_content.replace('__NOW_STR__', now_str)
html_content = html_content.replace('__NOW_FULL__', now_full)
html_content = html_content.replace('__TOTAL_COUNT__', str(total_count))
html_content = html_content.replace('__TODAY_COUNT__', str(_today_count))
html_content = html_content.replace('__SOURCE_COUNT__', str(len(sources)))
html_content = html_content.replace('__CATEGORY_COUNT__', str(len(categories)))
html_content = html_content.replace('__SUMMIT_COUNT__', str(summit_count))
html_content = html_content.replace('__DATE_COUNT__', str(stats.get('dateCount', len(dates))))
html_content = html_content.replace('__COLUMN_SIDEBAR__', column_tabs_html)
html_content = html_content.replace('__DATE_HEAD_BUTTONS__', tabs_html)
html_content = html_content.replace('__NEWS_DATA_JSON__', json.dumps(v12_data, ensure_ascii=False))

print(f"\U0001f4ca 生成V1.5 HTML: {total_count}条新闻, {len(dates)}天, 栏目: {column_counts}")

with open(OUTPUT_PATH_GH,'w',encoding='utf-8') as f: f.write(html_content)
with open(OUTPUT_PATH_ROOT,'w',encoding='utf-8') as f: f.write(html_content)

print(f"✅ V1.4 HTML已生成:")
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
