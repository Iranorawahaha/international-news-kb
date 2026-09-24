#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""官方源修复：恢复备份 + merge 09-23 窗口内新增（源组丢失第 22 次复发标准动作）"""
import json, shutil, os
from collections import Counter

ROOT = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50'
BAK = '/tmp/us-official-backup-0924.json'
DST = os.path.join(ROOT, 'data/us-official.json')

backup = json.load(open(BAK, encoding='utf-8'))
items = backup if isinstance(backup, list) else backup.get('items', [])
print(f'备份恢复 {len(items)} 条')

NEW = [
    {
        'source': '美国国务院',
        'date': '2026-09-23',
        'url': 'https://www.state.gov/releases/office-of-the-spokesman/2026/09/joint-statement-on-the-launch-of-the-andes-atlantic-corridor/',
        'title': '美国与阿根廷启动"安第斯-大西洋走廊"',
        'title_zh': '美国与阿根廷启动"安第斯-大西洋走廊"',
        'title_en': 'Joint Statement on the Launch of the Andes-Atlantic Corridor',
        'summary': 'Today, U.S. Deputy Secretary of State Christopher Landau and Argentine Minister of Foreign Affairs Pablo Quirno launched the Andes-Atlantic Corridor, a joint initiative to strengthen and modernize infrastructure linking Argentina\'s vital economic sectors to major Atlantic ports and Western markets.',
        'summary_en': 'Today, U.S. Deputy Secretary of State Christopher Landau and Argentine Minister of Foreign Affairs Pablo Quirno launched the Andes-Atlantic Corridor, a joint initiative to strengthen and modernize infrastructure linking Argentina\'s vital economic sectors to major Atlantic ports and Western markets.',
        'summary_zh': '美国副国务卿兰道与阿根廷外长基尔诺在联大高级别周期间启动"安第斯-大西洋走廊"倡议，旨在通过美国投资改造阿根廷铁路、水路、港口与能源基础设施，扩大矿产、石油与天然气出口，并依托《美阿关键矿产框架》推进关键矿产开采与加工以实现供应链多元化。该走廊属七国集团全球基础设施与投资伙伴关系的一部分，与印度-中东-欧洲走廊、洛比托走廊等并列。',
        'category': '中美博弈',
        'priority_score': 90,
        'is_official': True,
        'is_summit_level': False,
        'collectedAt': '2026-09-24 09:30:00',
        'collection_method': 'official',
        'keywords': ['关键矿产', '供应链', '阿根廷', '基础设施'],
    },
    {
        'source': '美国国务院',
        'date': '2026-09-23',
        'url': 'https://www.state.gov/releases/office-of-the-spokesman/2026/09/the-united-states-announces-civil-nuclear-initiatives-on-the-margins-of-the-united-nations-general-assembly/',
        'title': '联大期间美国宣布民用核能合作倡议',
        'title_zh': '联大期间美国宣布民用核能合作倡议',
        'title_en': 'The United States Announces Civil Nuclear Initiatives on the Margins of the United Nations General Assembly',
        'summary': 'Today, on the margins of the United Nations General Assembly in New York, and following the Trilateral Ministerial meeting between the United States, Japan, and the Republic of Korea, the United States is pleased to announce the establishment of an Implementation Plan in support of the Memorandum of Cooperation on Small Modular Reactor Deployments in Other Countries.',
        'summary_en': 'Today, on the margins of the United Nations General Assembly in New York, and following the Trilateral Ministerial meeting between the United States, Japan, and the Republic of Korea, the United States is pleased to announce the establishment of an Implementation Plan in support of the Memorandum of Cooperation on Small Modular Reactor Deployments in Other Countries.',
        'summary_zh': '美国在联大期间宣布，为美日韩三边小型模块化反应堆合作备忘录建立实施计划，推动SMR舰队部署以满足全球能源需求；同时欢迎GE-Vernova、日立、三星物产与波兰SGE签署产业合作框架，在欧洲推进BWRX-300反应堆部署，预计带动逾1500亿美元反应堆投资。',
        'category': '全球多边',
        'priority_score': 84,
        'is_official': True,
        'is_summit_level': False,
        'collectedAt': '2026-09-24 09:30:00',
        'collection_method': 'official',
        'keywords': ['核能', 'SMR', '美日韩', '能源'],
    },
    {
        'source': '美国国务院',
        'date': '2026-09-23',
        'url': 'https://www.state.gov/releases/office-of-the-spokesman/2026/09/secretary-rubios-meeting-with-russian-foreign-minister-lavrov-3/',
        'title': '鲁比奥在联大期间会见俄罗斯外长拉夫罗夫',
        'title_zh': '鲁比奥在联大期间会见俄罗斯外长拉夫罗夫',
        'title_en': "Secretary Rubio's Meeting with Russian Foreign Minister Lavrov",
        'summary': 'Secretary of State Marco Rubio met today with Russian Foreign Minister Sergey Lavrov on the sidelines of UNGA. The Secretary discussed the Russia-Ukraine war and the U.S.-Russia bilateral relationship.',
        'summary_en': 'Secretary of State Marco Rubio met today with Russian Foreign Minister Sergey Lavrov on the sidelines of UNGA. The Secretary discussed the Russia-Ukraine war and the U.S.-Russia bilateral relationship.',
        'summary_zh': '美国国务卿鲁比奥在联大期间会见俄罗斯外长拉夫罗夫，双方讨论了俄乌战争与美俄双边关系。此次会晤发生在美方邀请普京出席G20峰会、并寻求重启对俄高层接触的背景下。',
        'category': '地区局势',
        'priority_score': 84,
        'is_official': True,
        'is_summit_level': False,
        'collectedAt': '2026-09-24 09:30:00',
        'collection_method': 'official',
        'keywords': ['鲁比奥', '拉夫罗夫', '俄乌', '美俄'],
    },
    {
        'source': '美国国务院',
        'date': '2026-09-23',
        'url': 'https://www.state.gov/releases/office-of-the-spokesman/2026/09/secretary-rubios-meeting-with-indian-external-affairs-minister-jaishankar-4/',
        'title': '鲁比奥会见印度外长苏杰生 讨论对俄制裁外溢影响',
        'title_zh': '鲁比奥会见印度外长苏杰生 讨论对俄制裁外溢影响',
        'title_en': "Secretary Rubio's Meeting with Indian External Affairs Minister Jaishankar",
        'summary': 'Secretary Rubio met today with Indian External Affairs Minister Jaishankar in New York. The two officials reaffirmed the important role the U.S.-India strategic partnership continues to play in promoting a safe, secure, and prosperous Indo-Pacific.',
        'summary_en': 'Secretary Rubio met today with Indian External Affairs Minister Jaishankar in New York. The two officials reaffirmed the important role the U.S.-India strategic partnership continues to play in promoting a safe, secure, and prosperous Indo-Pacific.',
        'summary_zh': '美国国务卿鲁比奥在纽约会见印度外长苏杰生，双方重申美印战略伙伴关系对"安全、稳定与繁荣的印太"的重要作用，并就中东局势、对与俄罗斯和伊朗有经济往来国家可能实施的制裁交换意见。鲁比奥强调美方有能力帮助地区伙伴应对能源安全挑战。',
        'category': '中欧与盟友',
        'priority_score': 82,
        'is_official': True,
        'is_summit_level': False,
        'collectedAt': '2026-09-24 09:30:00',
        'collection_method': 'official',
        'keywords': ['美印', '鲁比奥', '苏杰生', '制裁', '印太'],
    },
    {
        'source': '美国国务院',
        'date': '2026-09-23',
        'url': 'https://www.state.gov/releases/office-of-the-spokesman/2026/09/protecting-the-sanctity-of-u-s-citizenshipa-new-visa-restriction-policy-for-those-who-engage-in-or-facilitate-birth-tourism/',
        'title': '美国宣布针对"生育旅游"的新签证限制政策',
        'title_zh': '美国宣布针对"生育旅游"的新签证限制政策',
        'title_en': 'Protecting the Sanctity of U.S. Citizenship: A New Visa Restriction Policy for Those Who Engage in or Facilitate Birth Tourism',
        'summary': 'Today, I am announcing a new visa restriction policy under Section 212(a)(3)(C) of the Immigration and Nationality Act. This policy targets individuals who knowingly engage in, have engaged in, or facilitate birth tourism to the United States.',
        'summary_en': 'Today, I am announcing a new visa restriction policy under Section 212(a)(3)(C) of the Immigration and Nationality Act. This policy targets individuals who knowingly engage in, have engaged in, or facilitate birth tourism to the United States.',
        'summary_zh': '美国国务卿鲁比奥宣布依据《移民与国籍法》212(a)(3)(C)条款实施新的签证限制政策，针对明知参与或协助"生育旅游"的人员，包括商业中介网络的经营者与管理者、教唆申请人造假的签证"包装"顾问、协助相关行程与欺诈使用医疗补助的境外医疗机构等，部分家庭成员亦可能被纳入限制范围。',
        'category': '美国内政',
        'priority_score': 80,
        'is_official': True,
        'is_summit_level': False,
        'collectedAt': '2026-09-24 09:30:00',
        'collection_method': 'official',
        'keywords': ['签证限制', '生育旅游', '移民'],
    },
]

exist = {i.get('url') for i in items}
added = 0
for n in NEW:
    if n['url'] in exist:
        print('  ⏭ 已存在:', n['title'])
        continue
    items.append(n)
    added += 1

json.dump(items, open(DST, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'新增 {added} 条 → 共 {len(items)} 条')
print('源组分布:', dict(Counter(i.get('source') for i in items)))
