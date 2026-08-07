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
    """按新闻 date 字段清理超期数据（而非按归档 key）"""
    cutoff = (datetime.now() - timedelta(days=RETENTION_DAYS)).strftime('%Y-%m-%d')
    cleaned = {}
    for d, arts in archive.items():
        # 保留归档日本身在窗口内
        if d < cutoff:
            continue
        # 但清理掉新闻 date 字段超窗口的条目
        kept = []
        for art in arts:
            art_date = art.get('date') or d
            if art_date >= cutoff:
                kept.append(art)
        if kept:
            cleaned[d] = kept
    return cleaned

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
    # V1.5.3: 美国官方信源（白宫/国务院/USTR/财政部/商务部/国防部）放最前
    # —— 因为官方源有真实中文摘要/日期，媒体源是二手报道
    AUTHORITY_ORDER = ['白宫', '美国国务院', '美国贸易代表办公室(USTR)', '美国财政部',
                       '美国商务部', '美国国防部(war.gov)',
                       '路透社', '美联社', 'BBC', 'CNN', '华盛顿邮报', '纽约时报',
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
    # V1.5.3: 跨日期去重时，记录 archive 中每个 URL 对应的"档案位置"
    # 当新版本有 is_official + title_zh 时，覆盖旧版本（保证官方源中文字段保留）
    archive_index = {}  # url -> (date, article_dict)
    if archive:
        for _date, _arts in archive.items():
            for _a in _arts:
                _u = _norm_url(_a.get('url'))
                if _u:
                    hist_urls.add(_u)
                    archive_index[_u] = (_date, _a)

    unique_articles = []
    duplicate_count = 0

    for art in articles:
        title = art.get('title', '') or ''
        source = art.get('source', '') or '未知'
        url = _norm_url(art.get('url'))
        unique_key = (title[:30], source)
        url_key = f"URL::{url}" if url else None

        # 1) 跨日期去重：URL 已存在于历史归档
        if url_key and url in hist_urls:
            # V1.5.3: 如果新条目是官方源（is_official=True）且有 title_zh 翻译
            # 而历史版本无 is_official/title_zh → 用新版本覆盖历史版本
            old_date, old_art = archive_index.get(url, (None, None))
            if (art.get('is_official') and art.get('title_zh')
                    and old_art and not old_art.get('title_zh')):
                # 用新版本覆盖旧版本（替换字段）
                for k in art.keys():
                    old_art[k] = art[k]
                duplicate_count += 1
                print(f"    🔁 官方源覆盖升级: {title[:35]}...")
                continue
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
# V1.5.2: 接入美国官方信源（白宫/国务院/USTR/财政部/商务部/国防部）
temp_files = ['data/news-basic.json', 'data/news-webfetch.json', 'data/us-official.json']

# 官方信源导航残留过滤词（只过滤非新闻公告标题）
OFFICIAL_NAV_WORDS = ["briefings & statements", "executive orders", "remarks and statements",
                      "secretary statements & remarks", "presidential actions", "nominations & appointments",
                      "presidential memoranda", "state department home", "countries & areas",
                      "bureaus & offices", "organizational chart", "role of the treasury",
                      "365 days of wins"]

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
            if not isinstance(art, dict):
                continue
            kw = art.get("keywords")
            if isinstance(kw, str):
                art["keywords"] = [k.strip() for k in kw.replace("，", ",").split(",") if k.strip()]
            elif kw is None:
                art["keywords"] = []
            # 官方信源字段补全（score/is_summit_level/column）
            if art.get("is_official"):
                if art.get("priority_score") is None or art.get("priority_score") == "":
                    t = art.get("title", "")
                    cn = any(k in t for k in ["China", "Chinese", "中国", "Beijing", "Taiwan", "台湾", "TikTok", "Huawei"])
                    sm = any(k in t for k in ["President", "Trump", "Xi", "Biden", "普京", "Putin"])
                    art["priority_score"] = 98 if (cn and sm) else (92 if cn else (88 if sm else 75))
                if art.get("is_summit_level") is None:
                    art["is_summit_level"] = any(k in art.get("title", "") for k in ["President", "Trump", "Xi", "Biden", "普京", "Putin"])
                if not art.get("column"):
                    art["column"] = "美国"
                if not art.get("title_en"):
                    art["title_en"] = art.get("title", "")
                if not art.get("summary"):
                    art["summary"] = f"[官方信源] {art.get('source','')} 发布：{art.get('title','')}"
                # 导航残留过滤（从 new_articles 移除）
                tl = (art.get("title", "") or "").lower()
                if any(w in tl for w in OFFICIAL_NAV_WORDS):
                    new_articles.pop()
                    print(f"    🗑️ 官方导航残留移除: {art.get('title','')[:40]}")
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

    # V2.5 日期归类：X日版面覆盖 X-1日 9:30 ~ X日 9:30
    # 新抓到"昨天发表"的文章 → 归入今天版（用户不会倒回去查昨天版面）
    # 更早日期的文章保持原日期不变（已是历史存档）
    from datetime import datetime as _dt_v25, timedelta as _td_v25
    _yesterday = (_dt_v25.now() - _td_v25(days=1)).strftime('%Y-%m-%d')
    _reassigned = 0
    for _a in cleaned_new:
        _ad = _a.get('date', '')
        # 仅重归类昨天的——昨天 9:30 后发表、今天才抓到的，实际属于今天的资讯窗口
        if _ad and _ad == _yesterday:
            _a['date'] = today
            _reassigned += 1
    if _reassigned:
        print(f"  🔄 日期重归类: {_reassigned} 条（昨天发表→归入今天版面）")
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

    # V2.0: 高优先级计数（替代旧版元首级）
    _high_priority = sum(1 for a in sorted_articles if (a.get('is_official') or a.get('is_summit_level') or (a.get('priority_score') or 0) >= 88))
    print(f"     ✅ 排序完成: {len(sorted_articles)} 条 (高优先级 {_high_priority} 条)")

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

# V1.7: 重新跑六大栏目分类器（WebFetch LLM 用了旧标签 "热点/泛涉华/经济金融"，
# 俄乌冲突需归"地区热点"——手动旧分类会失效，统一用分类器重置）
import os as _os_rc, sys as _sys_rc
_proj_dir = _os_rc.environ.get('PROJECT_DIR') or _os_rc.getcwd()
if _sys_rc.path[0] != _proj_dir:
    _sys_rc.path.insert(0, _proj_dir)
try:
    from scripts.classify_columns import classify_column as _classify_rc
    _rc_count = 0
    _rc_ru_ua = 0
    for _rc_dt, _rc_as in data['archive'].items():
        for _rc_a in _rc_as:
            _rc_title = _rc_a.get('title_zh') or _rc_a.get('title', '') or ''
            _rc_title_en = _rc_a.get('title_en', '') or ''
            _rc_summary = _rc_a.get('summary_zh') or _rc_a.get('summary', '') or ''
            _rc_new = _classify_rc(_rc_title, _rc_title_en, _rc_summary)
            if _rc_a.get('column') != _rc_new:
                _rc_a['column'] = _rc_new
                _rc_count += 1
                _rc_is_ru_ua = any(k in _rc_title+_rc_title_en for k in ['俄乌','乌克兰','Ukraine','Russia','泽连斯基','Zelensky','普京','Putin'])
                if _rc_new == '地区热点' and _rc_is_ru_ua:
                    _rc_ru_ua += 1
    if _rc_count:
        print(f"  🔁 V1.7 重新分类: {_rc_count} 条已重置为六栏标准（其中俄乌相关 {_rc_ru_ua} 条归入地区热点）")
    else:
        print(f"  ✅ V1.7 重新分类: 所有条目已符合六栏标准")
except Exception as _rc_e:
    print(f"  ⚠️ V1.7 重新分类失败: {_rc_e}")

update_stats(data)
data['lastUpdated'] = datetime.now().strftime('%Y-%m-%d %H:%M')

save_data(data)

# V1.5.4 终极防线：用 us-official.json 强制升级官方源字段
# （防止 dedupe/整合丢失 is_official/title_zh/summary_zh）
import json as _json_ff
import re as _re_ff
try:
    with open('data/us-official.json', 'r', encoding='utf-8') as _ff:
        _us = _json_ff.load(_ff)
    _ff_norm = lambda u: (_re_ff.match(r'^\[(.+?)\]\((.+?)\)$', (u or '').strip()) and _re_ff.match(r'^\[(.+?)\]\((.+?)\)$', (u or '').strip()).group(2) or (u or '').strip()).rstrip('/').lower()
    _ff_idx = {}
    for _fdt, _fits in data['archive'].items():
        for _fit in _fits:
            _ff_idx[_ff_norm(_fit.get('url'))] = (_fdt, _fit)
    _ff_added, _ff_upgraded = 0, 0
    _cutoff_str = (datetime.now() - timedelta(days=RETENTION_DAYS)).strftime('%Y-%m-%d')
    for _f_src in _us:
        _furl = _ff_norm(_f_src.get('url'))
        if not _furl: continue
        # V2.5: 用 collectedAt 日期做归档（而非发表日 date），与昨日文章归今天版面一致
        _ftarget = (_f_src.get('collectedAt') or '')[:10] or _f_src.get('date', '')
        if not _ftarget: continue
        # V1.5.7: 终极防线也严格按 7 天窗口过滤（防止 5-18 等超期数据被加回）
        if _ftarget < _cutoff_str: continue
        if _ftarget not in data['archive']:
            data['archive'][_ftarget] = []
        if _furl in _ff_idx:
            _fodt, _foart = _ff_idx[_furl]
            if _f_src.get('is_official') or _f_src.get('title_zh') or _f_src.get('summary_zh'):
                for _fk in ('title','title_en','title_zh','summary','summary_en','summary_zh','date','source','category','column','priority_score','is_summit_level','importance','keywords','url','is_official','collectedAt','collection_method','body_en'):
                    if _fk in _f_src:
                        _foart[_fk] = _f_src[_fk]
                if _fodt != _ftarget:
                    data['archive'][_fodt] = [x for x in data['archive'][_fodt] if _ff_norm(x.get('url')) != _furl]
                    data['archive'][_ftarget].append(_foart)
                _ff_upgraded += 1
        else:
            data['archive'][_ftarget].append(_f_src)
            _ff_added += 1
    for _fdt in list(data['archive'].keys()):
        if not data['archive'][_fdt]:
            del data['archive'][_fdt]

    # V2.5 终极重归类：按 collectedAt 归档 + 确保 date 字段 = archive key
    from collections import defaultdict as _dd_rc
    _rc_v25_reassigned = 0
    _rc_v25_fixed_date = 0
    _rc_v25_by_target = _dd_rc(list)
    for _rc_dt in list(data['archive'].keys()):
        for _rc_a in list(data['archive'][_rc_dt]):
            _rc_col = (_rc_a.get('collectedAt') or '')[:10]
            # 情况1：collectedAt 指向不同日期组 → 移到目标组
            if _rc_col and _rc_col != _rc_dt:
                _rc_a['date'] = _rc_col
                _rc_v25_by_target[_rc_col].append(_rc_a)
                data['archive'][_rc_dt].remove(_rc_a)
                _rc_v25_reassigned += 1
            # 情况2：在正确的组但 date 字段不对齐（force-upgrade 可能覆盖回去）→ 修正字段
            elif _rc_a.get('date') != _rc_dt:
                _rc_a['date'] = _rc_dt
                _rc_v25_fixed_date += 1
    # 把移动出去的加到目标组
    for _rc_target, _rc_arts in _rc_v25_by_target.items():
        if _rc_target not in data['archive']:
            data['archive'][_rc_target] = []
        data['archive'][_rc_target].extend(_rc_arts)
    # 删除空组
    for _rc_dt in list(data['archive'].keys()):
        if not data['archive'][_rc_dt]:
            del data['archive'][_rc_dt]
    if _rc_v25_reassigned or _rc_v25_fixed_date:
        print(f"  📅 V2.5 终极重归类: {_rc_v25_reassigned} 条归位, {_rc_v25_fixed_date} 条修正date字段")

    save_data(data)
    if _ff_added or _ff_upgraded:
        print(f"  🛡️ 官方源字段升级: 新增 {_ff_added} 条, 升级 {_ff_upgraded} 条")
except FileNotFoundError:
    pass
except Exception as _ff_e:
    print(f"  ⚠️ 官方源字段升级失败: {_ff_e}")

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
        high_priority = sum(1 for a in data['archive'][d] if (a.get('is_official') or a.get('is_summit_level') or (a.get('priority_score') or 0) >= 88))
        print(f"     • {d}: {count} 条 (高优先级 {high_priority} 条)")

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
# V3.0: 高优先级要闻数（V3 标准：仅涉华重大 / 台海冲突，priority_score >= 88）
def _is_high_priority(a):
    if a.get('is_official'): return True
    if (a.get('priority_score') or 0) >= 88: return True
    return False
high_count = sum(1 for a in all_articles if _is_high_priority(a))

# V1.5: 顶部日期表头按钮（横向）
tabs_html = '<button class="date-btn active" data-date="all">\U0001f4c5 全部日期（%d）</button>' % total_count
for d in dates:
    count = len(archive.get(d, []))
    tabs_html += '<button class="date-btn" data-date="%s">%s（%d）</button>' % (d, d.replace('2026-', '').replace('-', '/'), count)

# 六大栏目统计（用于栏目 tab）
COLUMN_ORDER = ["中国", "美国", "欧洲", "地区热点", "国际会议", "其他"]
COLUMN_ICONS = {"中国": "🇨🇳", "美国": "🇺🇸", "欧洲": "🇪🇺", "地区热点": "🌍", "国际会议": "🏛️", "其他": "📌"}
column_counts = {c: 0 for c in COLUMN_ORDER}
for _d, _arts in archive.items():
    for _a in _arts:
        _col = _a.get('column', '其他')
        column_counts[_col] = column_counts.get(_col, 0) + 1
# V1.5.6: 左侧栏目侧边栏列表（当日新增数量）
_today_str = dates[0] if dates else ''
_today_archive = archive.get(_today_str, [])
_all_today_count = len(_today_archive)
column_tabs_html = '<button class="col-item active" data-column="all"><span class="ic">📋</span><span class="nm">全部</span><span class="cnt">新增%d</span></button>' % _all_today_count
for _c in COLUMN_ORDER:
    _icon = COLUMN_ICONS.get(_c, '📌')
    _today_cnt = sum(1 for _a in _today_archive if _a.get('column') == _c)
    column_tabs_html += '<button class="col-item" data-column="%s"><span class="ic">%s</span><span class="nm">%s</span><span class="cnt">新增%d</span></button>' % (_c, _icon, _c, _today_cnt)

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
html_content = html_content.replace('__HIGH_COUNT__', str(high_count))
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
print(f"   📊 {total_count}条新闻 | {len(dates)}天存档 | {high_count}条高优先级")
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
• 高优先级新闻: $(python3 -c "import json;d=json.load(open('data/news-data.json'));print(sum(1 for v in d.get('archive',{}).values() for x in v if x.get('is_official') or (x.get('priority_score') or 0) >= 88))") 条

✨ V1.2 新特性:
✅ 7天数据存档（不再清空历史）
✅ 顶部日期Tab栏切换查看
✅ 按日期分组的数据结构
✅ 自动清理超过7天的旧数据
✅ 飞书Base永久存档（增量同步）⭐
✅ V2.0 体系：高/中/低 三档重要性 + 俄乌归地区热点 + 自动重新分类

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
