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

MEDIUM_SIGNALS = [
    '产品', 'product', '功能', 'feature', '更新', 'update',
    '合作', 'partner', '融资', 'funding',
    '开源', 'open source', '论文', 'paper',
    '招聘', 'hire',
]


def url_hash(url):
    if not url:
        return ''
    clean = url.strip().lower().rstrip('/').split('?')[0].split('#')[0]
    return hashlib.md5(clean.encode()).hexdigest()[:12]


def classify_ai_importance(art):
    """V3 AI重要性评分"""
    text = (art.get('title', '') + ' ' + art.get('title_en', '') +
            art.get('summary', '') + art.get('summary_en', '')).lower()
    
    # ── 1. 检查是否命中 15 家重点公司 ──
    has_key_company = False
    matched_companies = []
    for c, cl in zip(KEY_COMPANIES, KEY_COMPANIES_LOWER):
        if cl in text:
            has_key_company = True
            matched_companies.append(c)
    
    if not has_key_company:
        # 不涉及15家重点公司 → 检查是否AI通用动态
        has_ai = any(k in text for k in ['AI', '人工智能', 'artificial intelligence', '大模型', 'LLM'])
        if not has_ai:
            return 50, [], 'low'
        # 有AI但无重点公司 → 中
        return 65, [], 'medium'
    
    # ── 2. 高优先判定 ──
    high_hits = [k for k in HIGH_SIGNALS if k.lower() in text]
    
    # Special: NVIDIA/Huang Renxun any news → high priority
    if any(c in matched_companies for c in ['NVIDIA']) and len(high_hits) >= 0:
        has_high_relevance = any(k in text for k in [
            '黄仁勋', 'jensen', '芯片', 'chip', 'GPU', '收购', 'acquis',
            '发布', 'release', '制裁', 'sanction', '突破', 'record',
            '投资', 'invest', '合作', 'partner', '监管', 'regulation',
        ])
        if has_high_relevance:
            return 92, matched_companies, 'high'
    
    # Huawei any major news → high
    if any(c in matched_companies for c in ['华为', 'Huawei']):
        return 92, matched_companies, 'high'
    
    # Chip/acquisition/model/regulation + key company → high
    major_signals = ['收购', 'acquis', '芯片', 'chip', '大模型', 'LLM', 'GPT',
                     '监管', 'regulation', '法案', 'act', '禁令', 'ban',
                     '出口管制', '制裁', 'sanction', '科技战',
                     '突破', 'breakthrough', '参数', 'parameter']
    if any(s.lower() in text for s in major_signals):
        return 92, matched_companies, 'high'
    
    # DeepSeek/OpenAI/Anthropic very significant → high
    if any(c in matched_companies for c in ['DeepSeek', 'OpenAI', 'Anthropic']):
        return 88, matched_companies, 'high'
    
    # ── 3. 中优先 ──
    med_hits = [k for k in MEDIUM_SIGNALS if k.lower() in text]
    if med_hits:
        return 72, matched_companies, 'medium'
    
    # 有重点公司提及 → 至少中
    if has_key_company:
        return 65, matched_companies, 'medium'
    
    return 50, matched_companies, 'low'


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

    # 4. 按 collectedAt 归档
    archive = defaultdict(list)
    for a in articles:
        col_date = (a.get('collectedAt') or a.get('date') or TODAY)[:10]
        if col_date:
            a['date'] = col_date
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
