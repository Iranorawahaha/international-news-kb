# -*- coding: utf-8 -*-
"""1008 国际看板池合并：从 RSS/sitemap/彭博 结构化数据精确取 URL，写入 news-webfetch.json"""
import json, re, sys, os, importlib.util

TODAY = '2026-10-08'
COLLECTED = TODAY + ' 09:30:00'
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

def load_mod(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

reuters = json.load(open('/tmp/rsm1008/window.json'))
rss = json.load(open('/tmp/rss1008/window.json'))
bbg = json.load(open('/tmp/bbg1008.json'))['items']

FEEDMAP = {
    'scmp': ['scmp4', 'scmp91', 'scmp5'],
    'nyt': ['nyt'], 'guardian': ['guardian'], 'bbc': ['bbc'], 'aj': ['aj'],
    'politicoeu': ['politicoeu'], 'wapo': ['wapo'], 'wapotech': ['wapotech'],
    'ftworld': ['ftworld'], 'ftchina': ['ftchina'], 'ftcompanies': ['ftcompanies'],
    'fttech': ['fttech'],
}
SRC = {
    'reuters': '路透社', 'scmp': '南华早报', 'nyt': '纽约时报', 'guardian': '卫报',
    'bbc': 'BBC', 'aj': '半岛电视台', 'politicoeu': 'Politico', 'wapo': '华盛顿邮报',
    'wapotech': '华盛顿邮报', 'ftworld': '金融时报', 'ftchina': '金融时报',
    'ftcompanies': '金融时报', 'fttech': '金融时报', 'bbg': '彭博社',
}

def clean_url(u):
    u = (u or '').strip()
    u = re.sub(r'[?&](utm_source|utm_medium|utm_campaign|utm_term|utm_content|traffic_source|syn-[0-9a-z]+|itid|wpisrc|s_cid|ns_mchannel|at_medium)=[^&]*', '', u)
    return u.rstrip('?&').rstrip('/')

def norm(s):
    s = (s or '').lower()
    s = s.replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"')
    return re.sub(r'[^a-z0-9]', '', s)

def find_reuters(q):
    nq = norm(q)
    for r in reuters:
        if nq in norm(r['title']):
            return clean_url(r['url']), r['title'], r['date']
    return None, None, None

def find_rss(f, q):
    feeds = FEEDMAP.get(f, [])
    nq = norm(q)
    for r in rss:
        if r['feed'] in feeds and nq in norm(r['title']):
            return clean_url(r['link']), r['title'], r['date']
    return None, None, None

def find_bbg(q):
    nq = norm(q)
    for r in bbg:
        if nq in norm(r['title_en']):
            return clean_url(r['url']), r['title_en'], r['date']
    return None, None, None

def kw_of(zh, en):
    ks = []
    for w in ['中国', '美国', 'AI', '芯片', '关税', '出口管制', '贸易', '制裁', '半导体', '台海',
              '欧盟', '稀土', '算力', '英伟达', '数据', '能源', '中东', '俄罗斯', '乌克兰']:
        if w in zh:
            ks.append(w)
    if not ks:
        ks = [en.split()[0] if en else '国际']
    return ks[:6]

out = []
missing = []
parts = ['_p1008_a1', '_p1008_a2', '_p1008_b1', '_p1008_b2', '_p1008_c1', '_p1008_c2',
         '_p1008_c3', '_p1008_c4', '_p1008_d1', '_p1008_d2', '_p1008_d3', '_p1008_e1', '_p1008_e2']
for pn in parts:
    mod = load_mod(pn)
    for it in getattr(mod, 'ITEMS', []) + getattr(mod, 'WSJ', []):
        f = it['f']
        if f == 'hard':
            url, ten, tdate = it['u'], it['en'], it['d']
        elif f == 'reuters':
            url, ten, tdate = find_reuters(it['q'])
        elif f == 'bbg':
            url, ten, tdate = find_bbg(it['q'])
        else:
            url, ten, tdate = find_rss(f, it['q'])
        if not url:
            missing.append((pn, f, it['q']))
            continue
        src = it.get('s_') or SRC.get(f, '')
        d = it.get('d') or tdate
        item = {
            'title': it['zh'], 'title_zh': it['zh'], 'title_en': it.get('en') or ten,
            'summary': it['s'], 'summary_zh': it['s'], 'summary_en': it.get('en') or ten,
            'url': url, 'date': d, 'source': src, 'category': it['c'],
            'keywords': kw_of(it['zh'], it.get('en') or ten),
            'priority_score': it['p'], 'is_summit_level': False,
            'importance': '高' if it['p'] >= 88 else ('中' if it['p'] >= 80 else '低'),
            'is_official': False, 'collectedAt': COLLECTED,
            'collection_method': 'rss_sitemap_bloomberg_websearch',
        }
        if it.get('repost'):
            item['repost_from'] = it['repost']
        out.append(item)

print('resolved:', len(out), '| missing:', len(missing))
for m in missing:
    print('  MISSING', m)

# URL 去重（保留首次出现）
seen = set(); dedup = []
for it in out:
    k = clean_url(it['url']).lower()
    if k in seen:
        continue
    seen.add(k); dedup.append(it)
print('after dedup:', len(dedup))

from collections import Counter
print('by source:', Counter(i['source'] for i in dedup).most_common())
print('by date:', Counter(i['date'] for i in dedup).most_common())
print('by category:', Counter(i['category'] for i in dedup).most_common())

json.dump(dedup, open('/tmp/pool1008_new.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written /tmp/pool1008_new.json')
