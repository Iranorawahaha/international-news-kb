# -*- coding: utf-8 -*-
"""1008 官方源：从 HEAD 恢复 6 源 + 合并窗口内新增（collectedAt=今日）"""
import json, re, os, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = '2026-10-08'
COLLECTED = TODAY + ' 09:30:00'

spec = importlib.util.spec_from_file_location('_p1008_e2', os.path.join(HERE, '_p1008_e2.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

base = json.load(open('/tmp/us-official-HEAD.json'))
print('HEAD base:', len(base))
from collections import Counter
print(Counter(i.get('source') for i in base))

def norm(u):
    return (u or '').strip().rstrip('/').lower()

idx = {norm(i.get('url')): i for i in base}
added = []
for o in m.OFFICIAL:
    u = norm(o['u'])
    if u in idx:
        print('  already exists, skip:', o['zh'][:30]); continue
    it = {
        'title': o['zh'], 'title_en': o['en'], 'title_zh': o['zh'],
        'summary': o['s_en'], 'summary_en': o['s_en'], 'summary_zh': o['s'],
        'url': o['u'], 'date': o['d'], 'source': o['src'], 'category': o['c'],
        'column': o['c'], 'priority_score': o['p'], 'is_summit_level': False,
        'importance': '高' if o['p'] >= 88 else '中',
        'keywords': [w for w in ['中国', '美国', 'AI', '投资审查', '出口管制', '贸易', '制裁', '产能过剩'] if w in o['zh']][:6] or ['官方'],
        'is_official': True, 'collectedAt': COLLECTED,
        'collection_method': 'webfetch_official',
    }
    base.append(it); added.append(it['title_zh'])

print('added:', len(added))
for a in added: print('  +', a)
print('total:', len(base))
print(Counter(i.get('source') for i in base))

json.dump(base, open('/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/us-official.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written data/us-official.json')
