#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内看板 2026-11-12 收尾补丁"""
import json

DATA = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json'
TODAY = '2026-11-12'
d = json.load(open(DATA, encoding='utf-8'))
t = d['archive'][TODAY]

# 1. 删除重复的国台办央视版（保留官方表述更全的那条）
t = [x for x in t if x['title'] != '国台办：将一如既往支持广大台商台企来大陆投资兴业']

for x in t:
    # 2. 央行货币政策执行报告：补摘要、提分
    if '中国央行：加大政策支持力度' in x['title']:
        x['title'] = '央行三季度货币政策执行报告：加大政策支持力度 力争实现全年经济社会发展目标'
        x['category'] = '经贸动向'
        x['priority_score'] = 85
        x['summary'] = ('中国人民银行发布的2026年第三季度中国货币政策执行报告显示，前三季度我国社会融资规模增量保持'
                        '合理增长，普惠小微、制造业中长期贷款增速高于各项贷款。报告提出，下阶段将保持流动性合理充裕，'
                        '加大政策支持力度，强化逆周期调节，巩固拓展经济回升向好势头，力争实现全年经济社会发展目标。')

    # 3. 无人机：真实发布日以新华社稿为准（11-12 发稿，11-11 首飞）
    if '轻骑兵' in x['title']:
        x['date'] = '2026-11-11'
        x['priority_score'] = 82

    # 4. 彭清华会见：全国人大常委会副委员长，归高层但给 88（非党中央序列，档位低于政治局委员）
    if '彭清华会见' in x['title']:
        x['priority_score'] = 88

    # 5. 孙清良：省管干部监察调查，摘要补全
    if '孙清良' in x['title']:
        x['summary'] = ('据湖南省纪委监委11月12日消息，湖南省邵阳市政协副主席孙清良涉嫌严重职务违法，主动向组织交代问题，'
                        '目前正接受湖南省监察委员会监察调查。')

    # 6. 自然资源部实施意见：日期以印发日 11-04 为准？公开日 11-10 → 保留 11-10（在窗口内）
    x['collectedAt'] = TODAY

t.sort(key=lambda x: ({'元首动态': 0, '高层动态': 1, '重要会议': 2, '人事任免': 3,
                       '部委动态': 4, '经贸动向': 5, '政策发布': 6}.get(x['category'], 9),
                      -x.get('priority_score', 0)))
d['archive'][TODAY] = t
json.dump(d, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

from collections import Counter
c = Counter(x['category'] for x in t)
print('最终', len(t), '条 |', dict(c))
hi = [x for x in t if x['priority_score'] >= 85]
print(f'≥85: {len(hi)}/{len(t)} = {len(hi)*100//len(t)}% | 100分: {sum(1 for x in t if x["priority_score"]==100)}')
print('最短摘要:', min(len(x['summary']) for x in t), '| 空摘要:', sum(1 for x in t if not x['summary'].strip()))
print('date<11-11:', [x['title'][:20] for x in t if x['date'] < '2026-11-11'])
for x in t:
    print(' ', x['priority_score'], x['category'], '|', x['date'], '|', x['title'][:50])
