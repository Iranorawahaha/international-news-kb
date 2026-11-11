# -*- coding: utf-8 -*-
"""国内看板 2026-11-11 收尾补丁"""
import json, re

JSON_PATH = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json'
TODAY = '2026-11-11'
data = json.load(open(JSON_PATH, encoding='utf-8'))
items = data['archive'][TODAY]

# 1) 删发改委残留拆条
items = [x for x in items if '进一步完善重要民生商品价格调控机制' not in x.get('title', '')]

# 2) 张国清调研：11-10 版面已用 gov.cn 7085693 收录 → 今日纸版重复，删除
items = [x for x in items if not x.get('title', '').startswith('持续提升产业创新能力')]

# 3) 删「学习贯彻五中全会精神在基层」天津河北民生稿（栏目体蹲点）
items = [x for x in items if '多问一句、多跑一趟、多想一层' not in x.get('title', '')]

# 4) 联合早报《论减贫脱贫》稿：与 gov.cn 主稿同事件，且 zaobao 为转述 → 删除（保留 gov.cn 主要篇目介绍）
items = [x for x in items if 'zaobao.com' not in x.get('url', '')]

for it in items:
    t = it.get('title', '')
    # 记者会标题去日期括号
    if '外交部发言人郭嘉昆主持例行记者会' in t:
        it['title'] = '外交部发言人郭嘉昆主持例行记者会 回应“中国间谍”论调与中俄美元首会晤安排'
    # 外贸条目补齐截断摘要
    if t.startswith('前10个月我国货物贸易进出口44.81万亿元'):
        it['category'] = '经贸动向'
        it['priority_score'] = 85
        it['summary'] = ('据海关统计，2026年前10个月我国货物贸易进出口总值44.81万亿元，同比增长20%，保持强劲增长态势。'
                         '其中出口25.99万亿元、增长17.6%，进口18.82万亿元、增长23.6%，'
                         '10月当月进出口增速达31.2%，进口、出口已连续6个月保持两位数增长。')
    if t.startswith('前10个月全国二手房'):
        it['source'] = '央视新闻'

# 5) 补录：习近平《论减贫脱贫》出版发行（用 gov.cn 原件，与「主要篇目介绍」合并为一条综合）
main = None
for it in items:
    if '主要篇目介绍' in it.get('title', ''):
        main = it
if main:
    main['title'] = '习近平同志《论减贫脱贫》出版发行 收入重要文稿55篇'
    main['category'] = '元首动态'
    main['priority_score'] = 100
    main['source'] = '中国政府网·要闻'
    main['date'] = '2026-11-10'
    main['summary'] = ('中共中央党史和文献研究院编辑的习近平同志《论减贫脱贫》一书，近日由中央文献出版社出版并在全国发行，'
                       '收入习近平同志2012年11月至2026年7月期间关于减贫脱贫的重要文稿55篇，'
                       '其中部分文稿是首次公开发表。该书系统反映了习近平总书记关于扶贫脱贫工作的重要思想，'
                       '为总结中国减贫经验、推进巩固拓展脱贫攻坚成果同乡村振兴有效衔接提供了理论读本。')

CAT_ORDER = {'元首动态': 0, '高层动态': 1, '重要会议': 2, '人事任免': 3, '部委动态': 4, '经贸动向': 5, '政策发布': 6}
items.sort(key=lambda x: (-(x.get('priority_score') or 0), CAT_ORDER.get(x.get('category'), 9)))
data['archive'][TODAY] = items
data['todayCount'] = len(items)
json.dump(data, open(JSON_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

from collections import Counter
print('最终条数:', len(items))
print('分类:', dict(Counter(x.get('category') for x in items)))
sc = [x.get('priority_score') or 0 for x in items]
print('≥85:', sum(1 for s in sc if s >= 85), f'({sum(1 for s in sc if s>=85)/len(sc)*100:.0f}%)')
print('100分:', sc.count(100))
print('最短摘要:', min(len(x.get('summary') or '') for x in items))
for x in items:
    print(' ', x['priority_score'], x['category'], '|', x['title'][:50])
