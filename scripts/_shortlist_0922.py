# -*- coding: utf-8 -*-
"""0922 shortlist: score window RSS items by board relevance, print compact."""
import json, re

items = json.load(open('/tmp/rss0922/window.json', encoding='utf-8'))

HIGH = ['china', 'chinese', 'beijing', 'xi jinping', 'trump', 'tariff', 'sanction', 'export control',
        'chip', 'semiconductor', 'nvidia', 'huawei', 'taiwan', 'artificial intelligence', ' ai ',
        'rare earth', 'trade war', 'trade deal', 'byd', 'alibaba', 'tiktok', 'tsmc', 'pentagon',
        'xi-trump', 'trump-xi', 'united nations', 'unga', 'nato', 'greenland', 'russia', 'ukraine',
        'iran', 'israel', 'gaza', 'houthi', 'north korea', 'venezuela', 'federal reserve', 'fed ',
        'inflation', 'oil price', 'european union', 'europe', 'japan', 'korea', 'india', 'saudi',
        'climate', 'cyber', 'hack', 'election', 'congress', 'senate', 'white house', 'rubio',
        'bessent', 'he lifeng', 'critical minerals', 'data centre', 'data center', 'ai ',
        'military', 'missile', 'drone', 'warsh', 'merz', 'macron', 'zelenskiy', 'putin']
NOISE = ['sport', 'football', 'cricket', 'soccer', 'nfl', 'tennis', 'golf', 'olympic',
         'celebrity', 'fashion', 'recipe', 'travel', 'horoscope', 'weather', 'typhoon kill',
         'obituary', 'lottery', 'royal', 'tv show', 'music', 'film fest', 'style']

def score(it):
    t = (it['title'] + ' ' + it.get('desc', '')).lower()
    s = 0
    for k in HIGH:
        if k in t:
            s += 3 if k in ('china', 'chinese', 'trump', 'xi jinping', 'tariff', 'sanction', 'chip', 'semiconductor', 'export control', 'rare earth', 'taiwan', 'artificial intelligence', 'nvidia', 'huawei') else 1
    for k in NOISE:
        if k in t:
            s -= 4
    return s

for it in items:
    it['score'] = score(it)

sel = [it for it in items if it['score'] >= 2]
sel.sort(key=lambda x: (-x['score'], x['feed']))
print('shortlist:', len(sel), '/', len(items))
for i, it in enumerate(sel):
    print(f"{i:3d} [{it['feed']:12s}] {it['date']} s={it['score']:2d} | {it['title'][:100]}")
    print(f"      {it['link'][:150]}")
json.dump(sel, open('/tmp/rss0922/shortlist.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
