#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fill_translations.py — V1.5.5 白宫 + 国务院官方源中文化
"""
import json

# 翻译数据（key = URL，value = 中文 title/summary）
TRANSLATIONS = {
    # 白宫
    "https://www.whitehouse.gov/presidential-actions/2026/07/to-facilitate-positive-adjustment-to-competition-from-imports-of-quartz-surface-products/": {
        "title_zh": "促进对进口石英台面产品竞争的积极调整",
        "date": "2026-05-18",
        "summary_zh": "白宫于2026年5月18日发布公告，基于美国国际贸易委员会（ITC）依据《1974年贸易法》第202条对进口石英台面产品（QSP）的调查结果，对相关进口产品实施积极的关税调整措施，以保护美国国内产业免受不公平进口竞争的影响。",
        "summary_en": "On May 18, 2026, the White House issued a proclamation based on the ITC's investigation under Section 202 of the Trade Act of 1974 on imports of quartz surface products (QSP), implementing positive adjustments to tariffs on these imports to protect U.S. domestic industry from unfair import competition.",
    },
    "https://www.whitehouse.gov/releases/2026/07/president-trump-hosts-historic-cabinet-meeting-at-camp-david/": {
        "title_zh": "特朗普总统在戴维营主持历史性内阁会议",
        "date": "2026-07-31",
        "summary_zh": "唐纳德·特朗普总统2026年7月31日在马里兰州戴维营召开了首次电视直播的内阁会议。会议开场特朗普总统重点介绍了本届政府为美国家庭带来的一系列标志性成就，强调本届政府在执行法律、支持警察和打击犯罪方面的不懈努力。",
        "summary_en": "On July 31, 2026, President Donald J. Trump convened his Cabinet for the first live, televised Cabinet meeting at Camp David, Maryland. The President opened the meeting by highlighting his Administration's signature achievements for American families, including efforts to enforce the rule of law, back the police, and fight crime.",
    },
    "https://www.whitehouse.gov/releases/2026/07/icymi-confirm-todd-blanche-as-attorney-general/": {
        "title_zh": "今日回顾：确认 Todd Blanche 出任司法部长",
        "date": "2026-07-31",
        "summary_zh": "白宫2026年7月31日发布回顾文章，呼吁参议院迅速确认总统提名的司法部长候选人 Todd Blanche。广泛的法律执法组织、州检察长、前司法部官员、编辑委员会、法律专家、倡导团体和国会议员组成的联盟一致要求迅速确认其提名。",
        "summary_en": "On July 31, 2026, the White House urged the Senate to swiftly confirm President Trump's nominee for Attorney General, Todd Blanche. A broad coalition of law enforcement organizations, state attorneys general, former DOJ officials, editorial boards, legal experts, advocacy groups, and Members of Congress is united in demanding his expeditious confirmation.",
    },
    "https://www.whitehouse.gov/presidential-actions/2026/07/presidential-permit-authorizing-cameron-county-texas-to-own-operate-and-maintain-the-brownsville-and-matamoros-bridge-in-brownsville-texas/": {
        "title_zh": "总统许可证：授权德州 Cameron County 拥有运营美墨边境大桥",
        "date": "2026-07-30",
        "summary_zh": "特朗普总统2026年7月30日发布总统许可证，授权德克萨斯州 Cameron County 拥有、运营和维护布朗斯维尔与墨西哥马塔莫罗斯之间的边境大桥。许可证涵盖了跨越里约热内卢河的桥梁，包括连接美墨边境的四个车道和行人通道设施。",
        "summary_en": "On July 30, 2026, President Trump issued a Presidential Permit authorizing Cameron County, Texas to own, operate, and maintain the Brownsville-Matamoros Bridge connecting downtown Brownsville, Texas and Matamoros, Mexico. The permit covers bridges over the Rio Grande River including a four-lane vehicle and pedestrian crossing.",
    },
    "https://www.whitehouse.gov/presidential-actions/2026/07/presidential-determination-pursuant-to-section-101-of-the-defense-production-act-of-1950-as-amended-on-recoverable-critical-minerals-and-materials/": {
        "title_zh": "依据《国防生产法》第 101 节关于可回收关键矿产的总统决定",
        "date": "2026-07-30",
        "summary_zh": "特朗普总统2026年7月30日向商务部长签发总统决定备忘录，依据1950年《国防生产法》第101节（经修订）的授权，认定可回收关键矿产和材料对国防至关重要，以保障美国国防工业基础的供应链韧性。",
        "summary_en": "On July 30, 2026, President Trump issued a memorandum to the Secretary of Commerce, pursuant to Section 101 of the Defense Production Act of 1950 (as amended), determining that recoverable critical minerals and materials are essential to national defense, to secure supply chain resilience for America's defense industrial base.",
    },
    "https://www.whitehouse.gov/releases/2026/07/the-white-house-government-transparency-task-force-fact-sheet/": {
        "title_zh": "白宫政府透明度专案组情况说明书",
        "date": "2026-07-30",
        "summary_zh": "白宫2026年7月30日发布政府透明度专案组情况说明书，概述联邦政府提升运作透明度、打击政府浪费与欺诈、公开政府数据等措施的进展和具体行动计划。",
        "summary_en": "On July 30, 2026, the White House released a fact sheet from the Government Transparency Task Force, outlining progress and concrete action plans for improving federal government transparency, combating government waste and fraud, and opening government data.",
    },
    "https://www.whitehouse.gov/briefings-statements/2026/07/presidential-message-on-the-birthday-of-alexis-de-tocqueville/": {
        "title_zh": "总统祝词：纪念 Alexis de Tocqueville 诞辰",
        "date": "2026-07-29",
        "summary_zh": "特朗普总统2026年7月29日发表祝词，纪念伟大的政治思想家 Alexis de Tocqueville 的诞辰。Tocqueville 回到法国后发表了《论美国的民主》，成为对政治与人性最深刻反思之一。总统强调 Tocqueville 的思想对美国民主的持久影响。",
        "summary_en": "On July 29, 2026, President Trump issued a presidential message honoring the birthday of Alexis de Tocqueville, a great political thinker. Tocqueville returned to France and published Democracy in America, one of the most profound reflections on political and human nature, with enduring influence on American democracy.",
    },
    "https://www.whitehouse.gov/releases/2026/07/crime-plummets-another-historic-low-under-president-trump/": {
        "title_zh": "特朗普总统任内犯罪率再创历史新低",
        "date": "2026-07-30",
        "summary_zh": "特朗普总统任内，美国暴力犯罪率以现代美国历史上前所未有的速度下降，犯罪飙升时代彻底结束。这不是偶然，而是本届政府不懈执行法治、支持警察、调配资源打击犯罪的结果。",
        "summary_en": "Under President Trump, violent crime is plummeting at a pace unmatched in modern American history. The decade-long crime surge has decisively ended. This is the direct result of the Trump Administration's relentless efforts to enforce the rule of law, back the police, and surge resources against crime.",
    },
    # 国务院
    "https://www.state.gov/releases/office-of-the-spokesperson/2026/08/spain-travel-advisory-updated-to-raise-ceuta-to-level-3/": {
        "title_zh": "西班牙旅行建议更新：将休达提升至 3 级",
        "date": "2026-08-01",
        "summary_zh": "美国国务院2026年8月1日将西班牙休达地区旅行建议提升至3级（重新考虑前往），主因是当地移民涌入和局势不稳。建议旅客避免示威和人群，并提高警惕，特别是在休达边境地区。",
        "summary_en": "On August 1, 2026, the U.S. Department of State raised the Travel Advisory for Spain's Ceuta region to Level 3 (Reconsider Travel) due to migrant influx and instability. Travelers are advised to avoid demonstrations and crowds, and to exercise increased caution, particularly in the Ceuta border region.",
    },
    "https://www.state.gov/releases/office-of-the-spokesperson/2026/08/switzerland-national-day/": {
        "title_zh": "瑞士国庆贺词",
        "date": "2026-08-01",
        "summary_zh": "美国国务卿代表美利坚合众国，于2026年8月1日瑞士国庆日之际，向瑞士人民致以诚挚祝贺，重申美国对瑞士伙伴关系及共同价值观的坚定承诺。",
        "summary_en": "On August 1, 2026, on behalf of the United States, the Secretary of State extended heartfelt congratulations to the Swiss people on their National Day, reaffirming America's steadfast commitment to the Swiss partnership and shared values.",
    },
    "https://www.state.gov/releases/office-of-the-spokesperson/2026/08/benin-national-day/": {
        "title_zh": "贝宁国庆贺词",
        "date": "2026-08-01",
        "summary_zh": "美国国务卿代表美国政府，于2026年8月1日贝宁独立65周年之际向贝宁人民致以诚挚祝贺。强调美贝伙伴关系，致力于建设和平、繁荣、安全的世界。",
        "summary_en": "On August 1, 2026, on behalf of the U.S. government, the Secretary of State congratulated the people of Benin on the 65th anniversary of their independence. The statement emphasized the U.S.-Benin partnership based on a common pursuit of a more peaceful, prosperous, and secure world.",
    },
    "https://www.state.gov/releases/office-of-the-spokesperson/2026/07/us-welcomes-italy-into-pax-silica-initiative/": {
        "title_zh": "美国欢迎意大利加入 Pax Silica 倡议",
        "date": "2026-07-31",
        "summary_zh": "意大利2026年7月31日在布林迪西签署 Pax Silica 宣言，正式确认参与该倡议。美意两国承诺利用意大利先进制造业专长，加强关键矿产和半导体供应链合作。",
        "summary_en": "On July 31, 2026, Italy signed the Pax Silica Declaration in Brindisi, officially acknowledging Italy's participation. The U.S. and Italy affirmed their commitment to leveraging Italy's advanced manufacturing expertise to strengthen critical minerals and semiconductor supply chains.",
    },
    "https://www.state.gov/releases/office-of-the-spokesperson/2026/07/alert-to-countries-companies-and-other-entities-regarding-north-korean-it-workers/": {
        "title_zh": "关于朝鲜 IT 工作者的国家、公司和其他实体警示",
        "date": "2026-07-31",
        "summary_zh": "美国国务院2026年7月31日发布警示，朝鲜依赖部署在朝鲜境内外的高技能 IT 工作者网络，通过获取虚假身份远程赚取收入，为朝鲜非法核武器和弹道导弹计划提供资金。",
        "summary_en": "On July 31, 2026, the U.S. State Department issued an alert that North Korea relies on a global network of skilled IT workers, deployed within and outside North Korea, to obtain false identities and remotely earn income to fund North Korea's unlawful nuclear weapons and ballistic missile programs.",
    },
    "https://www.state.gov/releases/office-of-the-spokesperson/2026/07/statement-by-members-of-the-high-level-mission-of-oas-member-states-to-bolivia/": {
        "title_zh": "美洲国家组织成员国高层访问玻利维亚声明",
        "date": "2026-07-30",
        "summary_zh": "美国、阿根廷、加拿大、智利、巴拿马、秘鲁和乌拉圭政府2026年7月30日发布联合声明，阐述美洲国家组织（OAS）成员国高层代表团访问玻利维亚的相关立场。",
        "summary_en": "On July 30, 2026, the Governments of the United States, Argentina, Canada, Chile, Panama, Peru, and Uruguay released a joint statement on the High-Level Mission of OAS Member States to Bolivia.",
    },
}

# 读取并更新
data = json.load(open('data/us-official.json'))
for it in data:
    url = it.get('url', '').rstrip('/').lower()
    # 兼容 trailing slash
    for t_url, fields in TRANSLATIONS.items():
        t_norm = t_url.rstrip('/').lower()
        if url == t_norm or url + '/' == t_norm or url == t_norm + '/' or url[:-1] == t_norm:
            for k, v in fields.items():
                it[k] = v
            print(f'  ✓ {it.get("source","")[:8]} {it.get("title","")[:30]} | title_zh={bool(it.get("title_zh"))}')

json.dump(data, open('data/us-official.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\n✅ 已翻译 {len(TRANSLATIONS)} 条官方源')

# 验证
from collections import Counter
total_zh = sum(1 for it in data if it.get('title_zh'))
print(f'含 title_zh 字段: {total_zh}/{len(data)}')