#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-05 官方源数据补全（一次性）：
1. 更新 data/us-official-webfetch.json：新增财政部/商务部/USTR/国防部 4 条（含中文）
2. 重跑 fetch_us_official.py 合并
3. 为白宫/国务院 16 条补 title_zh/summary_zh（中文翻译），修复 Spain 模板摘要
"""
import json, subprocess, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WBF = os.path.join(BASE, 'data', 'us-official-webfetch.json')
USO = os.path.join(BASE, 'data', 'us-official.json')

def norm_summary(s):
    return s.replace('&#8217;', '\u2019').replace('&quot;', '"').replace('&#8211;', '\u2013')

# ---------- 1. 更新 webfetch 文件 ----------
with open(WBF, encoding='utf-8') as f:
    wf = json.load(f)

existing_urls = {w.get('url') for w in wf}
new_items = [
    {
        "title": "U.S.-UK Financial Regulatory Working Group Summer 2026: Joint Statement",
        "title_zh": "美英金融监管工作组发布2026年夏季联合声明",
        "summary": "The U.S.-UK Financial Regulatory Working Group issued a joint statement following its Summer 2026 meeting, reaffirming continued cooperation on financial regulation, cross-border market access and supervisory coordination between the two countries.",
        "summary_zh": "美英金融监管工作组在2026年夏季会议后发布联合声明，重申两国在金融监管、跨境市场准入与监管协调方面的持续合作。",
        "url": "https://home.treasury.gov/news/press-releases/sb0586",
        "date": "2026-08-04", "source": "美国财政部", "is_official": True,
        "category": "经济金融", "keywords": ["美英", "金融监管", "金融合作"],
        "collection_method": "webfetch"
    },
    {
        "title": "Trump Administration Secures an Additional $100 Billion U.S. Semiconductor Manufacturing Investment for a Total of $265 Billion from TSMC",
        "title_zh": "台积电再投1000亿美元 在美半导体投资总额达2650亿美元",
        "summary": "As a result of the historic U.S.-Taiwan trade and investment deal, TSMC announced an incremental $100 billion investment for a total of $265 billion in the United States, adding four advanced semiconductor manufacturing facilities and bringing the total to 12 leading-edge facilities.",
        "summary_zh": "得益于美台贸易与投资协议，台积电宣布新增1000亿美元对美投资，在美投资总额达2650亿美元，将新增4座先进半导体制造设施，全美总计达12座先进制程与封测设施。",
        "url": "https://www.commerce.gov/news/press-releases/2026/07/trump-administration-secures-additional-100-billion-us-semiconductor",
        "date": "2026-07-16", "source": "美国商务部", "is_official": True,
        "category": "经贸制裁", "keywords": ["台积电", "半导体", "对美投资", "TSMC"],
        "collection_method": "webfetch"
    },
    {
        "title": "American Steelworkers, Manufacturers, and Farmers Praise President Trump's Tariff Action to Combat Forced Labor in Global Supply Chains",
        "title_zh": "美国钢铁工人、制造商与农民支持特朗普打击全球供应链强迫劳动的关税行动",
        "summary": "USTR highlighted support from American steelworkers, manufacturers and farmers for President Trump's tariff action targeting forced labor in global supply chains, including tariffs on imports produced with forced labor.",
        "summary_zh": "美国贸易代表办公室援引美国钢铁工人、制造商与农民对特朗普总统针对全球供应链强迫劳动的关税行动的支持，该行动对使用强迫劳动生产的进口商品加征关税。",
        "url": "https://ustr.gov/about/policy-offices/press-office/press-releases/2026/july/american-steelworkers-manufacturers-and-farmers-praise-president-trumps-tariff-action-combat-forced",
        "date": "2026-07-24", "source": "USTR", "is_official": True,
        "category": "经贸制裁", "keywords": ["强迫劳动", "关税", "供应链"],
        "collection_method": "webfetch"
    },
    {
        "title": "The Office of Strategic Capital Signs $820 Million Conditional Loan Commitment with Performance Drone Works to Expand Domestic Drone Component Manufacturing",
        "title_zh": "战略资本办公室与Performance Drone Works签署8.2亿美元贷款承诺 扩大本土无人机零部件制造",
        "summary": "The Office of Strategic Capital signed an $820 million conditional loan commitment with Performance Drone Works to expand domestic manufacturing of drone components, strengthening the resilience of the U.S. defense supply chain.",
        "summary_zh": "美国国防部战略资本办公室（OSC）与Performance Drone Works签署8.2亿美元有条件贷款承诺，用于扩大美国本土无人机零部件制造产能，强化国防供应链韧性。",
        "url": "https://www.war.gov/News/Releases/Release/Article/4561771/the-office-of-strategic-capital-signs-820-million-conditional-loan-commitment-w/",
        "date": "2026-07-31", "source": "美国国防部(war.gov)", "is_official": True,
        "category": "国防安全", "keywords": ["无人机", "国防供应链", "战略资本"],
        "collection_method": "webfetch"
    },
]

added = 0
for it in new_items:
    if it["url"] not in existing_urls:
        wf.append(it)
        added += 1
with open(WBF, 'w', encoding='utf-8') as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
print(f"webfetch 新增 {added} 条（当前 {len(wf)} 条）")

# ---------- 2. 重跑 fetch_us_official.py 合并 ----------
r = subprocess.run(
    ['/Users/xiaoxiao/.workbuddy/binaries/python/versions/3.13.12/bin/python3',
     os.path.join(BASE, 'scripts', 'fetch_us_official.py')],
    capture_output=True, text=True, cwd=BASE)
print(r.stdout[-800:])
if r.returncode != 0:
    print('STDERR:', r.stderr[-800:])
    raise SystemExit(1)

# ---------- 3. 补白宫/国务院中文 + 修复模板摘要 ----------
translations = {
    "Presidential Message on the Birthday of the United States Coast Guard": (
        "总统就美国海岸警卫队成立236周年发表致辞",
        "8月4日是美国海岸警卫队成立236周年。白宫发布总统致辞，向海岸警卫队官兵致敬，称赞其作为美国执法先锋、海上安全与国土保卫力量的历史贡献。"),
    "Manufacturing Jobs Flock to the U.S. Thanks to President Trump": (
        "制造业岗位涌入美国：特朗普“美国优先”经济议程见效",
        "白宫表示，随着特朗普总统经济议程落地，美国制造业正经历复苏，新增制造业就业岗位持续回流美国，凸显关税保护与产业政策推动“再工业化”的成效。"),
    "Under President Trump, U.S. Factories Expand at Fastest Clip in More Than Four Years": (
        "特朗普治下美国工厂以四年多来最快速度扩张",
        "美国7月制造业活动以四年多来最强速度扩张，受益于需求激增、关税保护与政策激励，进一步印证制造业回流趋势加速。"),
    "Establishing the President": (
        "特朗普签署行政令成立“军人配偶委员会”",
        "总统签署行政令设立军人配偶委员会，旨在改善军人配偶的就业、教育及生活保障，缓解军属家庭负担，强化军队人才保留。"),
    "To Facilitate Positive Adjustment to Competition from Imports of Quartz Surface Products": (
        "美国对石英台面产品进口实施贸易救济公告",
        "总统发布公告，对石英表面产品进口采取贸易救济调整措施（关税），以帮助美国国内产业应对进口竞争，保护本土制造业。"),
    "President Trump Hosts Historic Cabinet Meeting at Camp David": (
        "特朗普在戴维营主持召开历史性内阁会议",
        "特朗普总统首次在戴维营举行电视直播内阁会议，内阁成员逐一汇报各部门进展，围绕经济、移民与国家安全等议题展开讨论。"),
    "ICYMI: Confirm Todd Blanche as Attorney General": (
        "白宫敦促参议院尽快确认托德·布兰奇出任司法部长",
        "白宫发布“ICYMI”汇总，敦促美国参议院不拖延地确认特朗普提名的司法部长人选托德·布兰奇。"),
    "Presidential Permit: Authorizing Cameron County, Texas, To Own, Operate, and Maintain the Brownsville and Matamoros Bridge": (
        "总统许可：授权得州卡梅伦县运营布朗斯维尔-马塔莫罗斯跨境大桥",
        "总统授权得克萨斯州卡梅伦县拥有、运营并维护连接美国布朗斯维尔与墨西哥马塔莫罗斯的跨境大桥，涉及美墨边境基础设施管理与贸易通道。"),
    "Secretary of State Marco Rubio and Paraguayan Foreign Minister Rubén Ramírez Lezcano at the Signing of a Memorandum of Understanding for Strategic Civil Nuclear Cooperation": (
        "鲁比奥与巴拉圭外长签署战略民用核能合作谅解备忘录",
        "美国国务卿鲁比奥与巴拉圭外长拉米雷斯·莱斯卡诺共同签署关于战略民用核能合作的谅解备忘录，双方承诺加强民用核能领域合作。"),
    "Secretary Rubio": (
        "国务卿鲁比奥与巴拉圭总统培尼亚通话",
        "美国国务院发言人表示，国务卿鲁比奥与巴拉圭总统培尼亚通话，讨论双边关系及地区事务。"),
    "Continuing to Advance Venezuela": (
        "美国继续推进委内瑞拉制度性民主过渡",
        "美国欢迎委内瑞拉2015年国民议会8月1日声明及国际社会相关表态，重申支持委内瑞拉恢复民主制度与法治秩序。"),
    "Cook Islands National Day": (
        "美国祝贺库克群岛国庆日",
        "美国代表全体人民向库克群岛人民致以61周年国庆祝贺，重申美库双边友好关系。"),
    "Spain: Travel Advisory Updated to Raise Ceuta to Level 3": (
        "国务院更新西班牙旅行警告：休达地区升至3级",
        "美国国务院将西班牙整体旅行建议维持在2级（因恐怖主义与骚乱提高警惕），并将休达（Ceuta）升至3级“重新考虑旅行”。因摩洛哥大量移民涌入休达可能引发不可预测的安全局势，西班牙已部署军队、国家警察和国民警卫队应对，建议美国公民慎重前往该地区。"),
    "Benin National Day": (
        "美国祝贺贝宁国庆66周年",
        "美国自豪地同贝宁人民一道庆祝其独立66周年，重申两国长期友好关系与合作承诺。"),
    "Switzerland National Day": (
        "美国祝贺瑞士国庆日",
        "美国代表全体人民向瑞士人民致以国庆祝贺，重申两国长期友好的伙伴关系。"),
    "U.S. Welcomes Italy Into Pax Silica Initiative": (
        "美国欢迎意大利加入“石英和平”倡议",
        "美国欢迎意大利加入“Pax Silica”半导体原材料供应链倡议，意大利在布林迪西签署《石英和平宣言》，该倡议旨在保障全球半导体关键原材料供应链安全。"),
}

with open(USO, encoding='utf-8') as f:
    data = json.load(f)

fixed_zh = 0
fixed_summary = 0
for item in data:
    t = norm_summary(item.get('title', ''))
    key = None
    for k in translations:
        if t.startswith(k):
            key = k
            break
    if key:
        zh_title, zh_summary = translations[key]
        if not item.get('title_zh'):
            item['title_zh'] = zh_title
            item['summary_zh'] = zh_summary
            fixed_zh += 1
        if not item.get('summary') or '[官方信源]' in str(item.get('summary', '')):
            item['summary'] = zh_summary  # 用中文真实摘要兜底（英文原文缺失时）
            fixed_summary += 1
    elif not item.get('summary') or '[官方信源]' in str(item.get('summary', '')):
        # 非白宫/国务院条目的模板摘要兜底
        item['summary'] = item.get('summary_zh') or item.get('title_zh') or item.get('title', '')
        fixed_summary += 1

with open(USO, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"补中文 title_zh/summary_zh: {fixed_zh} 条；修复模板摘要: {fixed_summary} 条")

# 校验
no_zh = [i for i in data if not i.get('title_zh')]
tpl = [i for i in data if '[官方信源]' in str(i.get('summary', ''))]
print(f"最终：总 {len(data)} 条 | 缺中文 {len(no_zh)} | 模板摘要 {len(tpl)}")
