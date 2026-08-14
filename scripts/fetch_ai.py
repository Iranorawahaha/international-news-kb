#!/usr/bin/env python3
"""
fetch_ai.py — AI 看板数据采集
从 aihot API merged.json + 国际新闻看板中提取 AI 条目
合并去重、按 V3 标准分类打分、按 collectedAt 日期归档
输出: data/ai-news.json
"""

import json
import os
import re
import hashlib
from datetime import datetime, timezone, timedelta
from collections import defaultdict

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = timezone(timedelta(hours=8))
TODAY = datetime.now(TZ).strftime('%Y-%m-%d')
NOW = datetime.now(TZ).strftime('%Y-%m-%d %H:%M')

# 15 家重点公司
KEY_COMPANIES = [
    'NVIDIA', 'AMD', 'Intel', 'Apple', 'Amazon', 'Microsoft', 'Google', 'Meta',
    'OpenAI', 'Anthropic', 'xAI',
    'DeepSeek', '华为', '字节跳动', '阿里巴巴', '腾讯',
]
KEY_COMPANIES_LOWER = [c.lower() for c in KEY_COMPANIES]

# 高优先关键词
HIGH_SIGNALS = [
    '收购', 'acquis', '并购', 'deal',
    '芯片', 'chip', '处理器', 'processor', 'GPU', 'CPU', 'AI加速', 'accelerator',
    '发布', 'release', 'launch', '推出', 'announce',
    '大模型', 'LLM', 'GPT', 'Claude', 'Gemini', '文心', '通义', '百川',
    '万亿参数', 'trillion', '参数', 'parameter',
    '监管', 'regulation', '法案', 'act', '禁令', 'ban', 'restrict',
    '出口管制', 'export control', '制裁', 'sanction',
    '科技战', 'tech war', '国家安全', 'national security',
    '突破', 'breakthrough', '首次', 'first', '创造纪录', 'record',
    '黄仁勋', 'Jensen Huang',
    '华为', 'Huawei', '昇腾', 'Ascend', '鸿蒙',
    '投资', 'invest', '融资', 'funding', 'IPO',
]

# 高优先重大事件信号（V2.0 精细化：仅"行业监管·科技博弈·重大突破"层面）
HIGH_EVENTS = [
    # 行业监管 / 国家科技博弈
    '监管', 'regulation', '法案', 'act', '合规', 'compliance',
    '禁令', 'ban', '禁止', '禁止令',
    '制裁', 'sanction',
    '出口管制', 'export control', '实体清单',
    '科技战', 'tech war', '中美', 'US-China',
    '反垄断', 'antitrust', '垄断', 'monopoly',
    '调查', 'investigation', '起诉', 'sue', 'lawsuit', '诉讼',
    '听证', 'hearing', '国会', 'congress', '参议院', 'senate',
    '国家', 'national', '政府', 'government',
    '安全', 'security', '国安', 'national security',
    # 重大突破
    '突破', 'breakthrough', '首次', 'first', '前所', '创纪录', 'record',
    '万亿参数', 'trillion', '新架构', 'architecture',
    '碾压', '超越', '超过', '超车', '反超',
    '收购', 'acquis', '并购', 'M&A',
    'IPO', '上市', '战略配售', '募资',
    # 黄仁勋/重大事件
    '黄仁勋', 'Jensen Huang', 'GTC',
    # 重大格局变化
    '降价', 'price cut', '免费', 'free',
    '估值', 'valuation', '融资', 'funding', '融资额',
]

# 降权信号（属于产品小更新/评测/教程 → 不该被归高）
DEMOTE_SIGNALS = [
    # 评测/benchmark 类
    'benchmark', '评测', '测评', '排行', 'ranking', '分数', '榜单',
    'baseline', '对比', '比较评测',
    # 教程/科普
    '博客', 'blog', '教你', 'how to', 'howto',
    'GitHub', '代码', 'code', 'demo', '示例',
    '专访', 'interview', '对话', 'podcast',
    '应用案例', '使用技巧', '教程', 'tutorial', '指南', 'guide',
    '个人观点', '看法', '观点', 'opinion',
    '纪念', '周年', 'history', '历史回顾',
    '版本', 'v6', 'v7', 'patch', '更新', '升级',
    # 过度吹捧/水评
    '过度吹捧', '被吹', '被高估', 'overhyped', '过度炒作',
    '宣称', '声称', '号称',
    # 框架评测
    '框架', 'framework', 'sdk', 'SDK',
    # 普通产品更新
    '小升级', '小更新', '新增', '新功能', '小功能',
    '防诈骗', '防骚扰', '防护',  # 华为鸿蒙那种小功能
    '个人理财', '食谱', '娱乐',
]

MEDIUM_SIGNALS = [
    '产品', 'product', '功能', 'feature', '更新', 'update',
    '合作', 'partner', '开源', 'open source', '论文', 'paper',
    '招聘', 'hire',
]


def url_hash(url):
    if not url:
        return ''
    clean = url.strip().lower().rstrip('/').split('?')[0].split('#')[0]
    return hashlib.md5(clean.encode()).hexdigest()[:12]


def classify_ai_importance(art):
    """V2.0 精细化 AI 重要性评分
    高优标准：行业监管 · 国家科技博弈 · 重大突破
    仅命中15家重点公司不够，必须 + 重大事件信号
    """
    text = (art.get('title', '') + ' ' + art.get('title_en', '') +
            art.get('summary', '') + art.get('summary_en', '')).lower()

    # ── 1. 检查是否命中 15 家重点公司 ──
    matched_companies = []
    for c, cl in zip(KEY_COMPANIES, KEY_COMPANIES_LOWER):
        if cl in text:
            matched_companies.append(c)
    has_key_company = bool(matched_companies)

    if not has_key_company:
        has_ai = any(k in text for k in ['AI', '人工智能', 'artificial intelligence', '大模型', 'LLM'])
        return (50, [], 'low') if not has_ai else (60, [], 'medium')

    # ── 2. 重大事件信号 ──
    high_hits = [k for k in HIGH_EVENTS if k.lower() in text]
    demote_hits = [k for k in DEMOTE_SIGNALS if k.lower() in text]

    # Special: NVIDIA / 华为 任何重大事件 → 高
    nvidia_hit = 'NVIDIA' in matched_companies
    huawei_hit = any(c in matched_companies for c in ['华为', 'Huawei'])

    # ── 3. 判定优先级 ──
    # 3a. 强监管/突破类（永远高优先级，不受 demote 影响）
    # 关键：用词边界/正则避免误匹配（如"突破口"、"研发"等）
    import re as _re
    super_patterns = [
        (r'监管', 'regulation'), (r'法案', 'act'), (r'出口管制', 'export control'),
        (r'制裁', 'sanction'), (r'科技战', 'tech war'), (r'反垄断', 'antitrust'),
        (r'起诉', 'sue'), (r'诉讼', 'lawsuit'), (r'实体清单', 'entity list'),
        (r'万亿参数', 'trillion'), (r'黄仁勋', 'Jensen Huang'),
        (r'收购', 'acqui'), (r'并购', 'M&A'), (r'IPO', 'IPO'),
        (r'上市.*(配售|发行|定价)', 'IPO'), (r'募资', 'funding'),
        (r'(重大|重大|关键|革命性).*突破', 'breakthrough'), (r'突破性', 'breakthrough'),
        (r'打破.*纪录', 'record'), (r'创纪录', 'record'),
        (r'首次(突破|实现|达成)', 'first'),
        (r'超越(人类|专家|对手)', 'surpass'),
    ]
    has_super = False
    for pat, _ in super_patterns:
        if _re.search(pat, text, _re.I):
            has_super = True
            break
    # 兼容简单的 super 关键词（避免遗漏）
    simple_super = ['起诉', 'lawsuit', 'sue', 'antitrust', '反垄断',
                    'IPO', '上市', '募资', '收购', 'acquis', '黄仁勋', 'Jensen Huang',
                    '万亿', 'trillion', '出口管制', '实体清单', '制裁', 'sanction',
                    '监管', '法案', 'act', '科技战', 'tech war', '出口管控']
    if not has_super:
        has_super = any(s.lower() in text for s in simple_super)

    # 3b. 纯产品/评测/教程类（强制中）
    if demote_hits and not has_super:
        return 65, matched_companies, 'medium'

    # 3c. NVIDIA + 强信号 → 高（用户原则：NVIDIA 监管/突破类高优）
    if nvidia_hit and has_super:
        return 92, matched_companies, 'high'

    # 3d. 华为 + 强信号 → 高
    if huawei_hit and has_super:
        return 92, matched_companies, 'high'

    # 3e. 有超级信号 → 高
    if has_super:
        return 92, matched_companies, 'high'

    # 3f. 有普通 high_hits（如 合作/融资 但非强信号）→ 中（避免产品动态归高）
    if high_hits:
        return 65, matched_companies, 'medium'

    # 3g. 仅有 15 公司提及 → 中
    return 65, matched_companies, 'medium'


def fetch_from_aihot():
    """读取 aihot merged.json"""
    paths = [
        os.path.join(os.environ.get('TMPDIR', '/tmp'), 'aihot_scan', 'merged.json'),
        '/tmp/aihot_scan/merged.json',
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                data = json.loads(open(p, encoding='utf-8').read())
                items = data if isinstance(data, list) else data.get('items', [])
                # Filter to 7 days
                cutoff = (datetime.now(TZ) - timedelta(days=7))
                result = []
                for it in items:
                    ts = it.get('publishedAt') or it.get('discoveredAt') or ''
                    if ts:
                        try:
                            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                            if dt < cutoff:
                                continue
                        except:
                            pass
                    result.append(it)
                print(f'  📡 aihot: {len(items)} 条 → 7天窗口 {len(result)} 条')
                return result
            except Exception as e:
                print(f'  ⚠️ aihot读取失败: {e}')
                return []
    print('  ⚠️ aihot merged.json 未找到')
    return []


def fetch_from_international():
    """从国际新闻看板提取 AI 相关条目"""
    intl_path = os.path.join(PROJ, 'data', 'news-data.json')
    if not os.path.exists(intl_path):
        return []
    try:
        data = json.loads(open(intl_path, encoding='utf-8').read())
        archive = data.get('archive', {})
        ai_articles = []
        ai_keywords = ['AI', '人工智能', '芯片', 'chip', '半导体', 'semiconductor',
                       'NVIDIA', 'GPU', '大模型', 'LLM', 'DeepSeek', '华为', 'Huawei',
                       'OpenAI', 'TikTok', '字节', '出口管制', '实体清单',
                       '制裁', 'sanction']
        for d, arts in archive.items():
            for a in arts:
                text = (a.get('title_zh', '') + ' ' + a.get('title_en', '') +
                        a.get('summary_zh', '') + a.get('summary', '')).lower()
                if any(k.lower() in text for k in ai_keywords):
                    # Check if it involves key companies
                    if any(c.lower() in text for c in KEY_COMPANIES_LOWER):
                        ai_articles.append(a)
        print(f'  🌍 国际版: {sum(len(v) for v in archive.values())} 条 → AI相关 {len(ai_articles)} 条')
        return ai_articles
    except Exception as e:
        print(f'  ⚠️ 国际版读取失败: {e}')
        return []


def merge_and_dedupe(aihot_items, intl_items):
    """合并去重：标题 + URL 哈希去重，国际源优先"""
    seen_hashes = set()
    seen_titles = set()
    merged = []
    from_intl = 0
    from_aihot = 0
    dup_count = 0

    # 先处理国际源（优先级更高）
    for a in intl_items:
        uh = url_hash(a.get('url', ''))
        title = (a.get('title_zh', '') or a.get('title', '')).strip().lower()[:80]
        th = hashlib.md5(title.encode()).hexdigest()[:8]
        if uh in seen_hashes or th in seen_titles:
            dup_count += 1
            continue
        seen_hashes.add(uh)
        seen_titles.add(th)
        a['origin'] = 'international'
        merged.append(a)
        from_intl += 1

    # 再处理 aihot（国际源优先，同样内容跳过）
    for a in aihot_items:
        uh = url_hash((a.get('links', {}) or {}).get('original', '') or
                      (a.get('links', {}) or {}).get('aihot', ''))
        title = (a.get('title', '') or '').strip().lower()[:80]
        th = hashlib.md5(title.encode()).hexdigest()[:8]
        if uh in seen_hashes or th in seen_titles:
            dup_count += 1
            continue
        seen_hashes.add(uh)
        seen_titles.add(th)
        a['origin'] = 'aihot'
        merged.append(a)
        from_aihot += 1

    print(f'  📦 合并: 国{from_intl} + a{from_aihot} = {len(merged)} 条 (去重 {dup_count} 条)')
    return merged


def normalize_article(item):
    """统一 schema"""
    if item.get('origin') == 'international':
        return {
            'id': item.get('id', ''),
            'date': item.get('date', ''),
            'title': item.get('title_zh', '') or item.get('title', ''),
            'title_en': item.get('title_en', '') or '',
            'summary': item.get('summary_zh', '') or item.get('summary', ''),
            'summary_en': item.get('summary', '') or '',
            'source': item.get('source', ''),
            'url': item.get('url', ''),
            'original_url': item.get('url', ''),
            'collectedAt': item.get('collectedAt', ''),
            'origin': 'international',
            'keywords': item.get('keywords', []),
            'company_tags': [],
        }
    else:  # aihot
        links = item.get('links', {}) or {}
        source = (item.get('source', {}) or {}).get('name', 'AI HOT')
        title = item.get('title', '') or ''
        # Try to extract English title
        title_en = ''
        if ' - ' in title:
            parts = title.split(' - ')
            if any(c in parts[-1].strip() for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
                title_en = parts[-1].strip()
        return {
            'id': item.get('id', ''),
            'date': (item.get('publishedAt') or item.get('discoveredAt') or '')[:10],
            'title': title,
            'title_en': title_en,
            'summary': item.get('summary', '') or '',
            'summary_en': '',
            'source': source,
            'url': links.get('aihot', '') or links.get('original', ''),
            'original_url': links.get('original', '') or '',
            'collectedAt': (item.get('discoveredAt') or item.get('publishedAt') or '')[:19],
            'origin': 'aihot',
            'keywords': [],
            'company_tags': [],
        }


def main():
    output_path = os.path.join(PROJ, 'data', 'ai-news.json')
    print(f'🤖 fetch_ai.py · {NOW}')
    print()

    # 1. 采集
    aihot_items = fetch_from_aihot()
    intl_items = fetch_from_international()

    # 2. 合并去重
    merged = merge_and_dedupe(aihot_items, intl_items)

    # 3. 标准化 + 分类 + 打分
    articles = []
    high_count = med_count = low_count = 0
    dup_fix = set()
    for item in merged:
        art = normalize_article(item)
        score, companies, importance = classify_ai_importance(art)
        art['priority_score'] = score
        art['importance'] = importance
        art['company_tags'] = companies[:3]

        # 去重（标准化后）
        uh = url_hash(art.get('url', '') or art.get('original_url', ''))
        if uh in dup_fix:
            continue
        dup_fix.add(uh)

        if importance == 'high':
            high_count += 1
        elif importance == 'medium':
            med_count += 1
        else:
            low_count += 1

        articles.append(art)

    print(f'\n📊 分类: 🔴{high_count} 🟡{med_count} ⚪{low_count} → 共 {len(articles)} 条\n')

    # V2.9 归档规则：X日版面 = 抓取时间决定归档（今天抓的 → 今天版面）
    # 页面真实发布日期保留在 date 字段仅用于显示（X日版面下可含X-1日内容）
    archive = defaultdict(list)
    for a in articles:
        col_date = (a.get('collectedAt') or TODAY)[:10]
        if col_date:
            archive[col_date].append(a)

    # 每组内按重要性排序
    for d in archive:
        archive[d].sort(key=lambda x: (-x['priority_score'], x.get('title', '')))

    dates = sorted(archive.keys(), reverse=True)
    total = sum(len(v) for v in archive.values())

    data = {
        'archive': dict(archive),
        'dates': dates,
        'stats': {
            'totalArticles': total,
            'dateCount': len(dates),
            'highCount': high_count,
            'mediumCount': med_count,
            'lowCount': low_count,
            'sourceCount': len(set(a.get('source', '') for a in articles)),
            'keyCompanies': KEY_COMPANIES,
        },
        'lastUpdated': NOW,
        'today': dates[0] if dates else TODAY,
        'todayCount': len(archive.get(dates[0], [])) if dates else 0,
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'💾 {output_path}')
    for d in dates:
        print(f'   {d}: {len(archive[d])} 条')
    print(f'   🔴{high_count} 🟡{med_count} ⚪{low_count}')

    # 5. 输出高优先条目供确认
    print(f'\n🔴 高优先条目 ({high_count} 条):')
    for d in sorted(archive.keys(), reverse=True):
        for a in archive[d]:
            if a['importance'] == 'high':
                tags = ','.join(a['company_tags'][:2]) if a['company_tags'] else '-'
                print(f'  [{d}] [{tags}] {a["title"][:80]} (score={a["priority_score"]})')


if __name__ == '__main__':
    main()
