# -*- coding: utf-8 -*-
"""2026-08-18 官方源补丁：白宫 2 条补中文 + war.gov 2 条新条目追加"""
import json

# ===== 1. 给白宫 2 条补 title_zh/summary_zh =====
d = json.load(open('data/us-official.json'))
for x in d:
    if x.get('source') == '白宫':
        t = x.get('title_en') or x.get('title', '')
        if 'USS Lincoln' in t:
            x['title_zh'] = '美中央司令部司令发文：《林肯号航母：划时代的表现》'
            x['summary_zh'] = '美国中央司令部司令布拉德·库珀上将发表专栏文章，分享其登上“林肯号”航空母舰的第一手见闻，赞扬舰员在部署中的表现。'
            x['category'] = '美国'
            x['column'] = '美国'
            x['priority_score'] = 72
            x['importance'] = '中'
            x['keywords'] = '林肯号航母,中央司令部,库珀,美军部署'
        elif 'Prescription Drug' in t:
            x['title_zh'] = '特朗普宣布60多年来最大规模处方药降价'
            x['summary_zh'] = '特朗普总统曾承诺削减处方药价格，最新数据显示处方药价格刚录得60多年来的最大降幅，白宫称其竞选承诺已兑现。'
            x['category'] = '美国'
            x['column'] = '美国'
            x['priority_score'] = 75
            x['importance'] = '中'
            x['keywords'] = '处方药,药价,特朗普,医疗政策'
json.dump(d, open('data/us-official.json', 'w'), ensure_ascii=False, indent=2)
print('白宫 2 条已补中文')

# ===== 2. war.gov 2 条新条目追加到 webfetch =====
wf = json.load(open('data/us-official-webfetch.json'))
new_items = [
    {
        "title": "Department of War Orders Research Security Audits at 30 Academic Institutions",
        "title_en": "Department of War Orders Research Security Audits at 30 Academic Institutions",
        "title_zh": "美国战争部下令对30所高校开展科研安全审计 审查对华学术合作",
        "summary": "The Department of War has issued formal notifications to 30 domestic academic institutions, directing them to initiate immediate and comprehensive reviews of their academic, financial and research collaborations with foreign entities of concern, including organizations associated with rebranded Confucius Institutes. The audits aim to protect American taxpayer-funded research from unauthorized technology transfer and intellectual property theft.",
        "summary_en": "The Department of War has issued formal notifications to 30 domestic academic institutions, directing them to initiate immediate and comprehensive reviews of their academic, financial and research collaborations with foreign entities of concern, including organizations associated with rebranded Confucius Institutes. The audits aim to protect American taxpayer-funded research from unauthorized technology transfer and intellectual property theft.",
        "summary_zh": "美国战争部已向30所美国高校发出正式通知，要求其对与“受关注外国实体”（依据FY19 NDAA第1286条，含更名后的孔子学院）的学术、财务和科研合作立即进行全面审查，以保护纳税人资助的研究免受未经授权的技术转让和知识产权窃取。相关高校须在2026年8月31日前向战争部报告审查结果。",
        "url": "https://www.war.gov/News/Releases/Release/Article/4575019/department-of-war-orders-research-security-audits-at-30-academic-institutions/",
        "date": "2026-08-17",
        "source": "美国国防部(war.gov)",
        "category": "中美关系",
        "column": "中美关系",
        "priority_score": 90,
        "is_summit_level": False,
        "importance": "高",
        "keywords": "科研安全,学术审查,孔子学院,技术转让,美国战争部",
        "is_official": True,
        "collectedAt": "2026-08-18 09:21:00",
        "collection_method": "webfetch"
    },
    {
        "title": "Department of War and RTX Accelerate Critical Munitions Production Through Navy Tomahawk Award",
        "title_en": "Department of War and RTX Accelerate Critical Munitions Production Through Navy Tomahawk Award",
        "title_zh": "美国战争部与RTX签署229亿美元战斧导弹合同 加速关键弹药生产",
        "summary": "The Department of War has announced a $22.9 billion contract with Raytheon, an RTX business, awarded by the U.S. Navy, to accelerate production of the Tomahawk missile, a critical long-range strike capability.",
        "summary_en": "The Department of War has announced a $22.9 billion contract with Raytheon, an RTX business, awarded by the U.S. Navy, to accelerate production of the Tomahawk missile, a critical long-range strike capability.",
        "summary_zh": "美国战争部宣布，美国海军授予雷神公司（RTX旗下企业）一份价值229亿美元的合同，用于加速生产战斧导弹——一项关键的远程打击能力，以扩大弹药产能、强化联合部队装备。",
        "url": "https://www.war.gov/News/Releases/Release/Article/4573544/department-of-war-and-rtx-accelerate-critical-munitions-production-through-navy/",
        "date": "2026-08-17",
        "source": "美国国防部(war.gov)",
        "category": "军事安全",
        "column": "军事安全",
        "priority_score": 78,
        "is_summit_level": False,
        "importance": "中",
        "keywords": "战斧导弹,RTX,雷神,弹药生产,美国海军",
        "is_official": True,
        "collectedAt": "2026-08-18 09:21:00",
        "collection_method": "webfetch"
    }
]
existing_urls = {x.get('url') for x in wf}
added = 0
for it in new_items:
    if it['url'] not in existing_urls:
        wf.append(it)
        existing_urls.add(it['url'])
        added += 1
json.dump(wf, open('data/us-official-webfetch.json', 'w'), ensure_ascii=False, indent=2)
print(f'war.gov 新条目追加: {added} 条，webfetch 现有 {len(wf)} 条')

# ===== 3. 合并回 us-official.json =====
d2 = json.load(open('data/us-official.json'))
d2_urls = {x.get('url') for x in d2}
merged = 0
for it in new_items:
    if it['url'] not in d2_urls:
        d2.append(it)
        d2_urls.add(it['url'])
        merged += 1
json.dump(d2, open('data/us-official.json', 'w'), ensure_ascii=False, indent=2)
print(f'us-official.json 合并追加: {merged} 条，现有 {len(d2)} 条')
