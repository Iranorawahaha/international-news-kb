# -*- coding: utf-8 -*-
"""0922 官方源合并：备份 116 条恢复 + 并入窗口内 5 条新增（补 title_zh/summary_zh）"""
import json

COL = '2026-09-22 09:30:00'
old = json.load(open('/tmp/us-official-backup-0922.json', encoding='utf-8'))
print('backup:', len(old))
from collections import Counter
print(Counter(x.get('source') for x in old))

NEW = [
 {
  'source': '白宫', 'category': '美国内政', 'column': '美国内政', 'priority_score': 76,
  'title': '白宫回应媒体诉讼：进入白宫是特权而非权利',
  'title_zh': '白宫回应媒体诉讼：进入白宫是特权而非权利',
  'title_en': 'White House Access Is a Privilege — Not a Right',
  'summary': 'Last week, President Donald J. Trump removed CNN, MS NOW, and Politico from the White House grounds after years of false reporting.',
  'summary_en': 'Last week, President Donald J. Trump removed CNN, MS NOW, and Politico from the White House grounds after years of false reporting.',
  'summary_zh': '白宫发布声明回应媒体诉讼，称上周已将 CNN、MS NOW 与 Politico 逐出白宫场地，并强调进入白宫采访是"特权而非权利"，援引第一修正案为自身做法辩护。该声明发布在相关媒体起诉政府之后。',
  'url': 'https://www.whitehouse.gov/releases/2026/09/white-house-access-is-a-privilege-not-a-right/',
  'date': '2026-09-21', 'collectedAt': COL, 'keywords': ['白宫', '媒体禁令', '第一修正案'],
  'is_summit_level': False, 'importance': '中', 'is_official': True, 'collection_method': 'us_official',
 },
 {
  'source': '美国国务院', 'category': '全球多边', 'column': '全球多边', 'priority_score': 82,
  'title': '鲁比奥在纽约会见北极盟友 协调北极安全投资',
  'title_zh': '鲁比奥在纽约会见北极盟友 协调北极安全投资',
  'title_en': "Secretary Rubio's Meeting with Arctic Allies",
  'summary': 'Secretary of State Marco Rubio met today with the Foreign Ministers of Canada, Denmark, the Faroe Islands, Finland, Greenland, Iceland, Norway, and Sweden in New York. The meeting reinforced the strategic imperative of sustained allied investment and coordination on shared challenges in the Arctic.',
  'summary_en': 'Secretary of State Marco Rubio met today with the Foreign Ministers of Canada, Denmark, the Faroe Islands, Finland, Greenland, Iceland, Norway, and Sweden in New York. The meeting reinforced the strategic imperative of sustained allied investment and coordination on shared challenges in the Arctic.',
  'summary_zh': '美国国务卿鲁比奥在纽约会见加拿大、丹麦、法罗群岛、芬兰、格陵兰、冰岛、挪威与瑞典外长，强调盟国持续投资与协调应对北极共同挑战的战略必要性。会晤发生在美丹格陵兰安全协议签署前夕，北极安全与关键矿产成为核心议题。',
  'url': 'https://www.state.gov/releases/office-of-the-spokesman/2026/09/secretary-rubios-meeting-with-arctic-allies/',
  'date': '2026-09-21', 'collectedAt': COL, 'keywords': ['北极', '格陵兰', '鲁比奥', '盟友协调'],
  'is_summit_level': False, 'importance': '中', 'is_official': True, 'collection_method': 'us_official',
 },
 {
  'source': '美国国务院', 'category': '中美博弈', 'column': '中美博弈', 'priority_score': 82,
  'title': '鲁比奥与意大利签署关键矿产合作备忘录',
  'title_zh': '鲁比奥与意大利签署关键矿产合作备忘录',
  'title_en': 'Secretary Rubio and Italian Deputy PM and FM Antonio Tajani at a Critical Minerals MOU Signing Ceremony',
  'summary': 'Secretary Rubio and Italian Deputy Prime Minister and Foreign Minister Antonio Tajani signed a Memorandum of Understanding on critical minerals.',
  'summary_en': 'Secretary Rubio and Italian Deputy Prime Minister and Foreign Minister Antonio Tajani signed a Memorandum of Understanding on critical minerals.',
  'summary_zh': '美国国务卿鲁比奥与意大利副总理兼外长塔亚尼签署关键矿产合作谅解备忘录。鲁比奥称这一议题"持续受到关注"，协议旨在推动关键矿产供应链多元化、降低对单一来源的依赖，是美方在稀土等领域联合盟友的最新动作。',
  'url': 'https://www.state.gov/releases/office-of-the-spokesman/2026/09/secretary-rubio-and-italian-deputy-pm-and-fm-antonio-tajani-at-a-critical-minerals-mou-signing-ceremony/',
  'date': '2026-09-21', 'collectedAt': COL, 'keywords': ['关键矿产', '意大利', '供应链', 'MOU'],
  'is_summit_level': False, 'importance': '中', 'is_official': True, 'collection_method': 'us_official',
 },
 {
  'source': '美国国务院', 'category': '地区局势', 'column': '地区局势', 'priority_score': 74,
  'title': '鲁比奥会见伊拉克总理 讨论解散民兵与主权问题',
  'title_zh': '鲁比奥会见伊拉克总理 讨论解散民兵与主权问题',
  'title_en': "Secretary Rubio's Meeting with Iraqi Prime Minister Al-Zaidi",
  'summary': 'Secretary of State Marco Rubio met with Iraqi Prime Minister Ali al-Zaidi today to discuss the future of the U.S.-Iraq partnership. The Secretary and Prime Minister agreed on the importance of Iraq dismantling terrorist militias, preventing attacks from Iraqi territory, and fully exercising its sovereignty.',
  'summary_en': 'Secretary of State Marco Rubio met with Iraqi Prime Minister Ali al-Zaidi today to discuss the future of the U.S.-Iraq partnership. The Secretary and Prime Minister agreed on the importance of Iraq dismantling terrorist militias, preventing attacks from Iraqi territory, and fully exercising its sovereignty.',
  'summary_zh': '美国国务卿鲁比奥会见伊拉克总理扎伊迪，讨论美伊伙伴关系前景。双方一致认为伊拉克有必要解散恐怖民兵组织、阻止从其领土发动的袭击并充分行使主权。会晤在联大高级别周期间举行。',
  'url': 'https://www.state.gov/releases/office-of-the-spokesman/2026/09/secretary-rubios-meeting-with-iraqi-prime-minister-al-zaidi/',
  'date': '2026-09-21', 'collectedAt': COL, 'keywords': ['伊拉克', '民兵', '鲁比奥', '主权'],
  'is_summit_level': False, 'importance': '中', 'is_official': True, 'collection_method': 'us_official',
 },
 {
  'source': '美国国务院', 'category': '中欧与盟友', 'column': '中欧与盟友', 'priority_score': 74,
  'title': '鲁比奥会见肯尼亚总统 谈关键矿产与商业外交',
  'title_zh': '鲁比奥会见肯尼亚总统 谈关键矿产与商业外交',
  'title_en': "Secretary Rubio's Meeting with Kenyan President Ruto",
  'summary': 'Secretary of State Marco Rubio met with Kenyan President William Ruto to discuss commercial diplomacy and regional peace and security. They spoke about how critical minerals opportunities in Kenya can position the country as a key player in the sector while presenting opportunities for U.S. firms.',
  'summary_en': 'Secretary of State Marco Rubio met with Kenyan President William Ruto to discuss commercial diplomacy and regional peace and security. They spoke about how critical minerals opportunities in Kenya can position the country as a key player in the sector while presenting opportunities for U.S. firms.',
  'summary_zh': '美国国务卿鲁比奥会见肯尼亚总统鲁托，讨论商业外交与地区和平安全。双方谈及肯尼亚的关键矿产机遇如何使该国成为该领域重要参与者，同时为美国企业提供机会。这是美方在关键矿产领域拉拢非洲伙伴的延续动作。',
  'url': 'https://www.state.gov/releases/office-of-the-spokesman/2026/09/secretary-rubios-meeting-with-kenyan-president-ruto-2/',
  'date': '2026-09-21', 'collectedAt': COL, 'keywords': ['肯尼亚', '关键矿产', '商业外交', '鲁比奥'],
  'is_summit_level': False, 'importance': '中', 'is_official': True, 'collection_method': 'us_official',
 },
]

oldurls = {x.get('url') for x in old}
merged = list(old)
added = 0
for n in NEW:
    if n['url'] in oldurls:
        print('already present, skip:', n['title_zh'])
        continue
    merged.append(n)
    added += 1
print('added:', added, '| total:', len(merged))
print(Counter(x.get('source') for x in merged))

json.dump(merged, open('data/us-official.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
