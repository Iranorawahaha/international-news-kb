#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-10-30 后处理补丁：恢复公报全文主稿 + 清理重复稿
问题：postprocess 把人民日报《中共二十届五中全会在京举行》（含公报全文）误删，
      导致公报主线缺失。此脚本补回 gov.cn 公报全文主稿，并把「将于30日举行发布会」
      预告稿改为不单独占用会议位（保留但降级为信息补充）。
"""
import json, re, html

PATH = 'data/china-news.json'
TODAY = '2026-10-30'
YDAY = '2026-10-29'
d = json.load(open(PATH, encoding='utf-8'))
arr = d['archive'][TODAY]


def key(u):
    u = (u or '').strip().rstrip('/')
    return re.sub(r'^https?://', '', u)


existing = {key(it['url']) for it in arr}

GONGBAO = dict(
    category='重要会议', priority_score=88, is_summit_level=True,
    title='党的二十届五中全会公报：审议通过全面从严治党《决定》 二十一大2027年下半年召开',
    source='中国政府网·要闻',
    url='https://www.gov.cn/yaowen/liebiao/202610/content_7084479.htm',
    date='2026-10-29',
    collectedAt='2026-10-30 11:25:00',
    summary=('中国共产党第二十届中央委员会第五次全体会议于2026年10月26日至29日在北京举行，出席中央委员162人、候补中央委员117人。'
             '全会听取和讨论习近平受中央政治局委托所作的工作报告，审议通过《中共中央关于持之以恒推进全面从严治党若干重大问题的决定》，'
             '习近平就《决定（讨论稿）》向全会作说明。全会决定党的二十一次全国代表大会于2027年下半年在北京召开，增选张升民为中央政治局委员，'
             '递补卢东亮、包钢、邢善萍等10名候补委员为中央委员；审议通过中央纪委关于马兴瑞、蓝天立、刘建超等18人和中央军委关于张又侠、'
             '刘振立等16人严重违纪违法问题的审查报告，确认中央政治局此前开除党籍及给予李云泽撤销党内职务的处分。全会强调做好岁末年初各项工作，'
             '确保完成今年经济社会发展主要目标任务，实现“十五五”良好开局。'),
)

if key(GONGBAO['url']) not in existing:
    arr.append(GONGBAO)
    existing.add(key(GONGBAO['url']))
    print('+ 补回公报主稿')

# 「将于30日举行发布会」预告稿：发布会已于今日 10:00 召开，预告稿信息已被发布会实况覆盖
for it in list(arr):
    if '将于30日上午举行新闻发布会' in it['title']:
        arr.remove(it)
        print('- 删预告稿（发布会实况已收录）')

# 「永葆清醒坚定…与会同志谈」—— 学习贯彻系列稿，并入公报主线，删除
for it in list(arr):
    if it['title'].startswith('永葆清醒坚定'):
        arr.remove(it)
        print('- 删系列稿（与会同志谈，属宣传产品）')

# 海南自贸港：政策发布 80 保留；检查是否有两个 gov.cn/央视重复（当前仅 1 条，无需处理）

# ---------- 清洗 ----------
def clean(s):
    if not s:
        return ''
    s = html.unescape(s)
    s = s.replace('\u00a0', ' ').replace('&nbsp;', ' ')
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', s).strip()


for it in arr:
    it['title'] = clean(it.get('title'))
    it['summary'] = clean(it.get('summary'))

CAT_ORDER = ['元首动态', '高层动态', '重要会议', '人事任免', '政策发布', '部委动态', '经贸动向']
arr.sort(key=lambda x: (-x.get('priority_score', 0),
                        CAT_ORDER.index(x['category']) if x['category'] in CAT_ORDER else 9))
d['archive'][TODAY] = arr
d['todayCount'] = len(arr)
d['stats'] = {
    'totalArticles': sum(len(v) for v in d['archive'].values()),
    'dateCount': len(d['archive']),
    'latestDate': TODAY,
    'summitCount': sum(1 for i in arr if i.get('is_summit_level')),
}
d['lastUpdated'] = '2026-10-30 11:25:00'
json.dump(d, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

from collections import Counter

print(f'== 补丁完成：{len(arr)} 条')
print('分类:', dict(Counter(i['category'] for i in arr)))
hi = sum(1 for i in arr if i.get('priority_score', 0) >= 85)
print(f'≥85: {hi}/{len(arr)} = {hi*100//len(arr)}%')
print('collectedAt≠今日:', [i['title'][:25] for i in arr if not (i.get('collectedAt') or '').startswith(TODAY)])
print('date<昨日:', [i['title'][:25] for i in arr if i['date'] < YDAY])
print('无摘要:', [i['title'][:25] for i in arr if not i.get('summary')])
urls = Counter(key(i['url']) for i in arr)
print('URL重复:', [u for u, c in urls.items() if c > 1])
t2 = Counter(i['title'][:26] for i in arr)
print('标题重复:', [t for t, c in t2.items() if c > 1])
print()
for i, x in enumerate(arr):
    print(i, x['priority_score'], '|', x['category'], '|', x['date'], '|', x['title'][:46])
