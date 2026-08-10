#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
官方源中文化补全 (2026-08-07)
为 data/us-official.json 中白宫/国务院全英文条目补 title_zh / summary_zh
仅做翻译补全，不改动脚本逻辑/信源配置/清洗规则
"""
import json, re, sys

PATH = 'data/us-official.json'
data = json.load(open(PATH, encoding='utf-8'))
items = data if isinstance(data, list) else data.get('items', [])

# (英文标题关键词匹配, 中文标题, 中文摘要)
TRANSLATIONS = [
    # ===== 白宫 2026-08-06 =====
    ("Continuing to Protect the Meaning and Value of American Citizenship",
     "继续保护美国公民身份的意义与价值",
     "特朗普总统签署行政令，要求联邦机构加强美国公民身份证明核查，防止非法移民通过出生地等方式获取公民身份及相关福利，进一步收紧移民与入籍政策。"),
    ("Ending Birth Tourism",
     "终止\"生育旅游\"",
     "特朗普总统签署行政令，指示国务院和国土安全部收紧签证审查，打击外国孕妇以获取美国国籍为目的的\"生育旅游\"行为，并限制相关签证的签发。"),
    ("Adjusting Imports of Polysilicon and its Derivatives into the United States",
     "调整美国多晶硅及其衍生物进口",
     "特朗普总统发布公告，对进口多晶硅及其衍生物调整关税政策，旨在保护美国本土太阳能供应链、应对海外产能过剩，涉及中美清洁能源产业链竞争。"),
    ("National Purple Heart Day, 2026",
     "2026年全国紫心勋章日",
     "特朗普总统发布公告，宣布2026年8月7日为全国紫心勋章日，向在战斗中负伤或牺牲的美国军人致敬。"),
    ("Private Sector Answers President Trump's Call to Lower Prices for American Families",
     "私营部门响应特朗普总统号召为美国家庭降低物价",
     "白宫发布简报，称私营企业响应总统号召宣布降价，涵盖食品杂货、日用品等多个领域，以缓解通胀对美国家庭的冲击。"),
    ("Fraud.gov: Track the Trump Administration's Relentless War on Fraud",
     "Fraud.gov：追踪特朗普政府打击欺诈的持续行动",
     "白宫宣布上线 Fraud.gov 平台，供公众举报政府支出欺诈与浪费，展示特朗普政府在打击欺诈、追回纳税人资金方面的成果。"),
    # ===== 白宫 2026-08-05 =====
    ("President Trump and Republicans Deliver Big Wins for the Silver State",
     "特朗普总统与共和党人为内华达州带来重大胜利",
     "白宫发布简报，列举内华达州在特朗普执政下的成就，包括历史性减税、边境安全强化及制造业回流等政策红利。"),
    ("FBI Secretly Opened Probe Alleging Trump Fired Comey Because He Was a Russian Asset, Declassified Memos Show",
     "解密备忘录显示：FBI 曾秘密立案指控特朗普因科米被指为俄资产而解雇他",
     "白宫公布约翰·所罗门的文章称，解密备忘录显示FBI曾在2017年5月秘密对特朗普立案调查，指控其解雇科米是因为科米被视为俄罗斯资产，引发对FBI政治化的争议。"),
    # ===== 国务院 2026-08-06 =====
    ("United States Announces Historic $2 Billion in Health and Humanitarian Assistance to Faith-Based Organizations",
     "美国宣布向信仰组织提供20亿美元健康与人道主义援助（历史性）",
     "美国宣布与提供全球健康和人道主义援助的信仰及社区组织建立近20亿美元的合作伙伴关系，为历史上规模最大的对信仰组织全球健康外援拨款。"),
    ("Welcoming Talks in Caracas to Advance Venezuela's Political Transition",
     "欢迎加拉加斯会谈推进委内瑞拉政治过渡",
     "美国欢迎委内瑞拉2015年国民议会代表团抵达加拉加斯，与临时政府展开面对面会谈，称直接会谈为推进委内瑞拉政治过渡提供了独特机遇。"),
    ("Targeting Enablers of the Cuban Regime's Arms Imports and Foreign Military Cooperation",
     "打击古巴政权武器进口与对外军事合作的支持者",
     "美国国务院宣布针对古巴政权的军火进口及对外军事合作支持者实施制裁，称古巴政权是支持恐怖主义的国家，此举旨在遏制其在西半球的活动。"),
    ("United States to Host Ministerial Launch Event for IAEA's Maritime Nuclear Initiative in Washington",
     "美国将在华盛顿主办国际原子能机构海事核倡议部长级启动活动",
     "美国将于8月26-27日在华盛顿主办国际原子能机构\"海上核技术许可应用\"（ATLAS）倡议的高级别论坛，推动海事核能技术合作。"),
    ("Jamaica National Day",
     "牙买加国庆日贺词",
     "美国祝贺牙买加庆祝独立64周年，重申美牙在安全、繁荣和地区稳定方面的持久伙伴关系。"),
    ("Bolivia National Day",
     "玻利维亚国庆日贺词",
     "美国祝贺玻利维亚总统罗德里戈·帕斯及人民庆祝独立201周年，称这是近二十年来美玻两国首次能够共同庆祝的玻利维亚独立日。"),
    ("Targeting Enablers of the Cuban Regime's Arms Imports and Foreign Military Cooperation Fact Sheet",
     "打击古巴政权武器进口支持者：事实清单（新增制裁指定）",
     "国务院宣布指定5个实体和8名个人，进一步推动特朗普政府终结古巴政权恶意活动的行动，目标包括国有企业、军工企业及部门官员。"),
    # ===== 国务院 2026-08-05 =====
    ("U.S. Participation in Special Meeting at the OAS Permanent Council on Nicaragua",
     "美国参加美洲国家组织常设理事会尼加拉瓜问题特别会议",
     "美国西半球事务高级官员科扎克在美洲国家组织常设理事会特别会议上发言，就尼加拉瓜政权对西半球和平与安全的威胁表明美方立场。"),
    ("Secretary Rubio's Meeting with UK Foreign Secretary Miliband",
     "国务卿卢比奥会见英国外交大臣米利班德",
     "美国国务卿卢比奥与英国外交大臣米利班德会晤，讨论欧洲应在自身安全中承担更大角色，并重申对霍尔木兹海峡安全通行等问题的共同承诺。"),
    ("Degrading CJNG: Announcing over $100 Million in Reward Offers and Visa Restrictions",
     "打击CJNG贩毒集团：宣布逾1亿美元悬赏与签证限制",
     "美国国务院国际麻醉品和执法事务局宣布对CJNG贩毒集团头目提供逾1亿美元悬赏，并实施签证限制，支持特朗普总统铲除威胁美国人民的毒枭恐怖组织的行动。"),
]

def zh_summary_fallback(en_summary, title_zh):
    """无翻译匹配时生成简单中文摘要（备选）"""
    return title_zh

updated = 0
for it in items:
    if it.get('title_zh'):
        continue  # 已有中文
    title = it.get('title', '')
    norm = title.replace('\u2019', "'").replace('\u2018', "'")
    for kw, tzh, szh in TRANSLATIONS:
        norm_kw = kw.replace('\u2019', "'").replace('\u2018', "'")
        # 用标题前60字符匹配（处理弯引号差异）
        if norm[:60].startswith(norm_kw[:60]) or norm_kw in norm:
            it['title_zh'] = tzh
            it['summary_zh'] = szh
            it['summary'] = it.get('summary_en') or it.get('summary')  # 保留英文真实摘要
            updated += 1
            break
    else:
        # 未匹配：至少给个中文标题
        print(f"⚠️ 未匹配翻译: {title[:70]}")

# 写回
if isinstance(data, list):
    json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
else:
    data['items'] = items
    json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"✅ 补全中文: {updated} 条")
