#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-10-25 官方源恢复 + 合并当日新增（V2.11）
- 从备份恢复 6 源全集，再 merge 本轮真实新增
- 新增条目必须 title==title_zh、summary_zh 为中文、collectedAt=今日
"""
import json, shutil

TODAY = '2026-10-25'
COL = f'{TODAY} 09:30:00'
OFF = 'data/us-official.json'
BAK = '/tmp/us-official-backup-1025.json'

old = json.load(open(BAK, encoding='utf-8'))
new = json.load(open(OFF, encoding='utf-8'))
oldt = old if isinstance(old, list) else old.get('items', [])
newt = new if isinstance(new, list) else new.get('items', [])
oldurls = {i.get('url') for i in oldt}

def E(title_zh, title_en, summary_zh, summary_en, source, category, keywords, score, date, url, importance='中'):
    return dict(
        title=title_zh, title_zh=title_zh, title_en=title_en,
        summary=summary_zh, summary_zh=summary_zh, summary_en=summary_en,
        source=source, category=category, column='官方发布', keywords=keywords,
        priority_score=int(score), is_summit_level=False, is_official=True,
        importance=importance, date=date, url=url,
        collectedAt=COL, collection_method='webfetch',
    )

adds = [
    E('白宫发布"美国优先"海产品战略并上线 Seafood.gov',
      'Fact Sheet: President Donald J. Trump Announces the America First Seafood Strategy and Seafood.gov',
      '白宫10月23日发布"美国优先"海产品战略并同步上线 Seafood.gov 门户，落实"恢复美国海产品竞争力"行政令。战略要点包括：协调联邦政策与科研扩大国内可持续捕捞、降低合规成本、重建加工与岸线基础设施、以政府采购与"Eat American Seafood"全国推广扩大内需；FDA 同日提出"美国捕捞海产品"自愿标签方案，USDA 提供逾50亿美元担保贷款用于肉类与海产品加工现代化。战略同时强化进口监测与打击非法、不报告、不受管制（IUU）捕捞，并通过 USTR 等渠道争取对等市场准入。',
      'The White House released the America First Seafood Strategy and launched Seafood.gov on Oct 23, implementing the Executive Order Restoring American Seafood Competitiveness. Key elements include expanding sustainable domestic harvest, cutting compliance costs, rebuilding processing and shoreside infrastructure, a voluntary "U.S. Caught Seafood" label proposed by FDA, and more than $5 billion in USDA guaranteed loans for processing modernization.',
      '白宫', '美国内政', '海产品战略;Seafood.gov;NOAA;IUU捕捞;关税与进口监测', 76, '2026-10-23',
      'https://www.whitehouse.gov/fact-sheets/2026/10/fact-sheet-president-donald-j-trump-announces-the-america-first-seafood-strategy-and-seafood-gov/'),

    E('美国欢迎巴拉圭成为《Pax Silica 宣言》第26个签署国',
      'United States Welcomes Paraguay as Newest Pax Silica Signatory',
      '美国国务院10月23日发表媒体声明，欢迎巴拉圭成为《Pax Silica 宣言》第26个签署国。巴拉圭外长拉米雷斯当日在华盛顿国务院出席签署仪式，由负责经济事务的副国务卿赫尔伯格见证，巴拉圭正式启动参与该倡议。双方确认将利用巴拉圭的关键矿产与水电资源，在美洲构建"超级智能"基础设施。Pax Silica 是美方主导的硅基供应链与算力盟友网络，签署方主要围绕关键矿产、半导体与 AI 基础设施开展合作。',
      'The United States welcomed Paraguay as the 26th signatory to the Pax Silica Declaration. Paraguayan Foreign Minister Ramírez signed at the State Department alongside Under Secretary for Economic Affairs Jacob Helberg. The two countries affirmed a commitment to leveraging Paraguay\'s critical minerals and hydropower to build super-intelligence infrastructure in the Americas.',
      '美国国务院', '中美博弈', 'Pax Silica;巴拉圭;关键矿产;算力基础设施', 74, '2026-10-23',
      'https://www.state.gov/releases/office-of-the-spokesman/2026/10/united-states-welcomes-paraguay-as-newest-pax-silica-signatory/'),

    E('商务部发布"美国优先"海产品战略 强化进口监测与渔业竞争力',
      'Trump Administration Releases America First Seafood Strategy',
      '美国商务部10月23日发布"美国优先"海产品战略，由 NOAA 主导落实，目标是扩大国内海产品生产、现代化基础设施、改善美国捕捞者与加工商的市场准入，并确保国内外市场公平竞争。商务部长卢特尼克称，该战略要让美国海产品的未来由美国渔民、美国工人和美国产业构建，"而不是由外国进口"；并称将改进海产品进口监测计划（SIMP），以先进工具锁定高风险进口，打击海产品欺诈、错标与非法捕捞，同时通过 USTR 等机构争取美国出口的对等市场准入。战略依托现有法定权限推进，不新增支出计划。',
      'The Commerce Department released the America First Seafood Strategy, implemented by NOAA, to expand domestic seafood production, modernize infrastructure, improve market access for American harvesters and processors, and ensure fair competition. Secretary Lutnick said the future of U.S. seafood must be built by American fishermen, workers and industry "not by foreign imports." The strategy strengthens the Seafood Import Monitoring Program against high-risk imports.',
      '美国商务部', '美国内政', '海产品;NOAA;进口监测;贸易公平', 72, '2026-10-23',
      'https://www.commerce.gov/news/press-releases/2026/10/trump-administration-releases-america-first-seafood-strategy'),

    E('美国与墨西哥宣布阿мпhenol Optimize 工厂快速响应劳工机制案件解决',
      'United States Announces Successful Resolution of Rapid Response Labor Mechanism Matter at Amphenol Optimize',
      'USTR 10月23日宣布，美墨加协定快速响应劳工机制（RRM）项下阿мпhenol Optimize 工厂案件已成功解决，墨方采取补救措施后相关关税清算恢复。该机制允许美方就特定工厂的劳工权利侵害问题要求墨西哥审查并整改，是美方把贸易协定劳工条款用于电子制造领域的又一案例。',
      'The United States announced the successful resolution of the USMCA Rapid Response Labor Mechanism matter at the Amphenol Optimize facility, with Mexico having taken remediation measures and tariff liquidation resuming.',
      'USTR', '美国内政', '快速响应劳工机制;美墨加协定;电子制造', 66, '2026-10-23',
      'https://ustr.gov/about/policy-offices/press-office/press-releases/2026/october/united-states-announces-successful-resolution-rapid-response-labor-mechanism-matter-amphenol'),

    E('美国与墨西哥宣布米内拉佩尼亚斯基托矿区补救方案',
      'United States and Mexico Announce Course of Remediation at Minera Peñasquito',
      'USTR 10月23日宣布，美国与墨西哥就米内拉佩尼亚斯基托（Minera Peñasquito）矿区劳工权利问题公布补救方案，要求企业采取具体措施纠正此前认定的权利侵害。该案依美墨加协定快速响应劳工机制推进，是美方把贸易协定劳工条款延伸至矿业领域的案例之一。',
      'The United States and Mexico announced a course of remediation at the Minera Peñasquito facility, requiring concrete measures to address previously identified labor rights denials under the USMCA Rapid Response Labor Mechanism.',
      'USTR', '美国内政', '快速响应劳工机制;矿业;美墨加协定', 64, '2026-10-23',
      'https://ustr.gov/about/policy-offices/press-office/press-releases/2026/october/united-states-and-mexico-announce-course-remediation-minera-penasquito'),

    E('美国战争部公布2026年度"战争部长维护奖"获奖单位',
      'DoW Announces 2026 Secretary of War Maintenance Awards Winners',
      '美国战争部10月23日公布2026年度"战争部长维护奖"获奖单位，表彰在装备维护、后勤保障与战备水平方面表现突出的部队与机构。该奖项为战争部年度例行表彰，评估维度包括装备完好率、维修周期与部署支援效率。',
      'The Department of War announced the winners of the 2026 Secretary of War Maintenance Awards, recognizing units and organizations for excellence in equipment maintenance, logistics support and readiness.',
      '美国国防部(war.gov)', '美国内政', '战争部;装备维护;战备', 55, '2026-10-23',
      'https://www.war.gov/News/Releases/Release/Article/4632673/dow-announces-2026-secretary-of-war-maintenance-awards-winners/'),

    E('美国战争部与海军敲定17亿美元汉普顿锚地军营项目',
      'DoW, Navy Close on $1.7 Billion Hampton Roads Barracks Project',
      '美国战争部与海军10月23日就汉普顿锚地17亿美元军营项目达成协议，将新建与改造水兵住宿设施，以缓解该地区驻军住房紧张与设施老化问题。汉普顿锚地为美国大西洋舰队核心母港群所在地，项目属海军基础设施现代化计划的一部分。',
      'The Department of War and the Navy closed on a $1.7 billion barracks project in Hampton Roads to build and modernize sailor housing, addressing aging infrastructure at one of the Navy\'s principal Atlantic fleet homeport complexes.',
      '美国国防部(war.gov)', '美国内政', '海军;军营建设;汉普顿锚地;基础设施', 60, '2026-10-23',
      'https://www.war.gov/News/Releases/Release/Article/4632102/dow-navy-close-on-17-billion-hampton-roads-barracks-project/'),

    E('美国战争部发布第七批"不明异常现象"档案',
      'Department of War Publishes Seventh Release of Unidentified Anomalous Phenomena Files on WAR.GOV/UFO',
      '美国战争部10月23日在其官网 UFO 专区发布第七批"不明异常现象"（UAP）相关档案，延续此前分批公开影像与记录的做法。该系列公开行动源于国会就 UAP 问题施加的透明度要求，内容包括军方拍摄的影像资料与相关说明文件。',
      'The Department of War published its seventh release of Unidentified Anomalous Phenomena files on WAR.GOV/UFO, continuing a series of public disclosures driven by congressional transparency requirements.',
      '美国国防部(war.gov)', '美国内政', 'UAP;不明异常现象;信息公开', 58, '2026-10-23',
      'https://www.war.gov/News/Releases/Release/Article/4632058/department-of-war-publishes-seventh-release-of-unidentified-anomalous-phenomena/'),
]

added = [a for a in adds if a['url'] not in oldurls]
merged = oldt + added
json.dump(merged, open(OFF, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

from collections import Counter
print('restored+merged:', len(merged), Counter(i.get('source') for i in merged))
print('added:', len(added))
