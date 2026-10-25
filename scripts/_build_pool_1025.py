#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-10-25 国际看板池构建（V2.17 归档规则）
- 所有 URL 均来自实际抓取的 RSS / sitemap / WebFetch（硬断言）
- 官方源条目只写 us-official.json，不进池
"""
import json, re, datetime

TODAY = '2026-10-25'
COL = f'{TODAY} 09:30:00'

# ---------- 权威 URL 集合 ----------
def load_allowed():
    allowed = set()
    # 1) RSS 抓取（/tmp/rss1025/*.xml）
    import glob, html, email.utils
    for f in glob.glob('/tmp/rss1025/*.xml'):
        if 'reuters_' in f or f.endswith('reuters_hits.json'):
            continue
        t = open(f, encoding='utf-8', errors='ignore').read()
        for m in re.finditer(r'<link>(.*?)</link>', t, re.S):
            u = m.group(1).strip()
            if u.startswith('http'):
                allowed.add(u)
        for m in re.finditer(r'<guid[^>]*>(.*?)</guid>', t, re.S):
            u = m.group(1).strip()
            if u.startswith('http'):
                allowed.add(u)
    # 2) 路透 sitemap
    for h in json.load(open('/tmp/rss1025/reuters_hits.json')):
        allowed.add(h['url'])
    # 3) 彭博 RSS 输出
    for line in open('/tmp/bloomberg_urls_1025.txt', encoding='utf-8'):
        u = line.strip()
        if u.startswith('http'):
            allowed.add(u)
    return allowed

ALLOWED = load_allowed()
# 4) 经 WebSearch / WebFetch 原文页验证的精确 URL（Politico、AP、路透精确 slug）
EXACT_VERIFIED = [
    # 路透（sitemap 精确 slug，逐字取自 RSS/sitemap 原文）
    'https://www.reuters.com/technology/moonshot-curbs-hacking-ability-new-kimi-model-fears-grow-over-ai-powered-2026-10-24/',
    'https://www.reuters.com/world/china/tougher-discipline-xis-authority-key-chinas-communist-partys-fifth-plenum-2026-10-23/',
    'https://www.reuters.com/world/middle-east/iran-has-ramped-up-efforts-target-us-personnel-intelligence-memo-warns-2026-10-24/',
    'https://www.reuters.com/world/middle-east/yemens-houthis-renew-warning-against-using-riyadh-airport-2026-10-24/',
    # 南华早报（RSS 精确 slug）
    'https://www.scmp.com/news/china/diplomacy/article/3372036/fandom-vs-flag-why-young-chinese-embrace-japanese-pop-culture-reject-war-era-symbolsreject-war-era-symbols',
    'https://www.scmp.com/news/china/science/article/3371706/chinas-j-20-stealth-jet-designers-plan-put-powerful-radar-aircraft-wingft-wing',
    'https://www.scmp.com/news/china/money-wealth/article/3372032/leading-chinese-economic-commentator-ren-zepings-social-media-account-restricted-account-restricted',
    'https://www.scmp.com/news/china/diplomacy/article/3371535/washington-misreading-beijing-decline-us-visits-china-sparks-concernoncern',
    'https://www.scmp.com/news/china/diplomacy/article/3372023/systematically-dismantled-hegseths-new-offensive-against-chinas-confucius-institutess-confucius-institutes',
    'https://www.scmp.com/news/china/politics/article/3372015/thousands-evacuated-and-flights-grounded-typhoon-champi-hits-eastern-chinastern-china',
    'https://www.scmp.com/news/hong-kong/hong-kong-economy/article/3372073/hong-kong-seeks-bigger-role-yuan-regional-trade-treasury-chief-sayseasury-chief-says',
    'https://www.scmp.com/week-asia/politics/article/3371980/filipinos-split-marcos-south-china-sea-handling-amid-row-over-jing-quans-remarksng-quans-remarks',
    'https://www.scmp.com/news/world/united-states-canada/article/3372051/trump-hails-tariffs-new-us42-billion-audi-plant-georgiargia',
    'https://www.scmp.com/opinion/asia-opinion/article/3371802/seouls-useless-placation-warning-all-us-trade-partnersade-partners',
    # Politico（WebSearch 原文页 200 且标题逐字一致）
    'https://www.politico.com/newsletters/national-security-daily/2026/10/23/beijing-locks-in-laos-01134092',
    'https://www.politico.com/newsletters/prescription-pulse/2026/10/23/proposed-rules-target-us-china-biotech-ties-01132547',
    'https://www.politico.eu/article/the-cyber-flaw-scramble-that-brought-the-ai-threat-to-life/',
    # 美联社（WebFetch apnews.com/world-news 列表实抓）
    'https://apnews.com/article/russia-ukraine-war-starlink-drones-a3a0139dfc23365550306dd66fe43daa',
]
ALLOWED |= set(EXACT_VERIFIED)
print('authority url set:', len(ALLOWED))

def norm(u):
    u = (u or '').strip()
    u = re.sub(r'[?#].*$', '', u)
    if u.endswith('/'):
        u = u[:-1]
    return u.lower()

ALLOWED_N = {norm(u) for u in ALLOWED}

items = []
bad = []

def add(title_en, title_zh, summary_zh, source, category, keywords, score, date, url, summit=False):
    if norm(url) not in ALLOWED_N:
        bad.append((title_en, url))
        return
    items.append(dict(
        title=title_zh, title_zh=title_zh, title_en=title_en,
        summary=summary_zh, summary_zh=summary_zh,
        source=source, category=category, keywords=keywords,
        priority_score=int(score), is_summit_level=bool(summit),
        date=date, url=url, collectedAt=COL,
    ))

# ================= 路透社 (sitemap 官网 URL) =================
add('China urges US to halt proposed expansion of outbound investment curbs',
    '中国商务部敦促美方停止扩大对华投资限制',
    '中国商务部24日发表声明，敦促美国停止扩大限制本国资本对华投资，称美国财政部23日发布的拟议规则将破坏中美经贸关系。该规则拟将生物技术纳入受限领域，并扩大对高性能计算与高超音速系统的覆盖范围。商务部指该提案"歧视性"扩大涉华投资限制、加大限制力度，对此坚决反对并保留采取未指明反制措施的权利，同时称其违背两国元首近半年两次会晤达成的共识。美方则称措施并非只针对中国，目的是防止美国资本支持外国对手发展可能威胁美国国家安全的军民两用战略技术。',
    '路透社', '中美博弈', '对外投资限制;生物技术;商务部;中美经贸', 92, '2026-10-24',
    'https://www.reuters.com/world/china/china-urges-us-halt-proposed-expansion-outbound-investment-curbs-2026-10-24/')

add("China's Communist Party names new provincial chiefs ahead of fifth plenum",
    '五中全会前中共集中调整六省党政一把手',
    '中共在二十届五中全会（10月26日至29日在北京闭幕式）召开前，于24日宣布六个省份的党政主要负责人调整，涉及两名新任省委书记和六名拟任省长（省政府党组书记）的人选。国务院副秘书长王志军（二十届中央委员）任湖南省委书记，接替沈晓明；中宣部副部长、国新办主任莫高义任云南省委书记，接替王宁。此外湖南谢卫江、福建郭宁宁、青海诸葛宇杰、江西陈永奇、河北赵辰昕、云南刘奇凡分获省政府党组书记任命，均指向省长接任。省级人大尚需履行正式选举程序，但通常属程序性步骤。',
    '路透社', '中国外交', '五中全会;人事调整;省委书记;省长', 90, '2026-10-24',
    'https://www.reuters.com/world/china/chinas-communist-party-names-new-provincial-chiefs-ahead-fifth-plenum-2026-10-24/')

add('Exclusive: TSMC seeks factory-equipment alternatives to thwart China rare earths grip, sources say',
    '台积电寻求设备无稀土方案 降低对华稀土依赖',
    '路透社独家报道，三名知情人士称台积电正探索在工厂设备中替换含稀土部件，以降低北京出口管制可能扰乱其最先进芯片产线的风险。稀土磁体广泛用于驱动机台活动部件的电机，一旦短缺可能波及手机、AI 系统、数据中心与国防供应链客户。三名听取简报的业内高管称，台积电已就自动化设备采用无稀土电机征询供应商意见，其中一人称动因是担心中国可能断供；讨论仍处早期阶段，尚未大规模部署，台积电不予置评。此前美台均已表态要降低对中国稀土与关键矿产供应链的依赖，台湾工研院计划三年内建试验产线，可满足岛内约五成需求。',
    '路透社', 'AI·科技', '台积电;稀土;出口管制;半导体供应链', 92, '2026-10-22',
    'https://www.reuters.com/world/china/tsmc-seeks-factory-equipment-alternatives-thwart-chinas-rare-earths-grip-sources-2026-10-22/')

add('US blocks two devices with Chinese-made surveillance chips',
    '美FCC首次依新规封杀两款含海思监控芯片设备',
    '美国联邦通信委员会（FCC）22日宣布，禁止两款内置中国华为旗下海思半导体监控芯片的设备进入美国市场，这是该机构首次援引今年7月通过的新规行使相关权力。被禁设备分别是一款行车记录仪和一款无线视频传输设备，均使用海思芯片；FCC 指海思将该芯片宣传为"专为监控市场设计"并内置人脸检测算法。FCC 主席卡尔称，含有国安威胁清单所列企业生产监控芯片的视频设备"对国家和人民构成明显且无法接受的风险"。新规将禁令从整机下延至关键硬件组件，堵住此前含清单企业零部件的设备仍可入美的"组件漏洞"。',
    '路透社', '中美博弈', 'FCC;海思;华为;监控芯片;设备禁令', 90, '2026-10-22',
    'https://www.reuters.com/world/us-blocks-two-devices-with-chinese-made-surveillance-chips-2026-10-22/')

add("US military bans BYD vehicles from strategic air base in Japan",
    '美军以数据泄露风险禁止比亚迪车辆进入嘉手纳基地',
    '驻日美军宣布，自10月26日起禁止所有中国比亚迪（BYD）制造的车辆进入冲绳嘉手纳空军基地，涵盖私家车、承包商车辆、出租车与配送车，不设任何例外，由第18安全部队中队在各入口执行拦截。基地发言人称，比亚迪车辆对官兵与军事任务构成"不可接受的风险"，美方顾虑来自车载摄像头、传感器与联网能力可能收集并外泄基地设施布局、人员活动规律与敏感装备位置。美国国防部今年6月已将比亚迪列入"中国军事企业"清单，为后续限制提供制度依据。该禁令可能扩至普天间等其他驻日美军基地，甚至驻韩美军基地。',
    '路透社', '中美博弈', '比亚迪;嘉手纳;驻日美军;联网汽车;数据安全', 90, '2026-10-23',
    'https://www.reuters.com/world/asia-pacific/us-bans-byd-air-base-japan-over-security-concern-news-report-says-2026-10-23/')

add("Moonshot curbs hacking ability in new Kimi model as fears grow over AI-powered cyberattacks",
    '月之暗面发布 Kimi K3.1 Pro 主动削弱网络攻击能力',
    '中国 AI 初创企业月之暗面24日发布旗舰模型 Kimi K3.1 Pro，并称已在发布前削弱其网络攻击能力。公司表示已从训练语料库与强化学习环境中删除网络攻击相关数据，同时保留通用编程能力，目标是"不发布会拓展网络能力绝对前沿的开源权重"。该模型总参数 2.8 万亿、采用 MoE 架构（每次激活 1040 亿参数），支持 100 万 Token 上下文，并同步推出速度提升约 2 至 3 倍的 Highspeed 版本，完整权重计划 11 月 4 日前开放。公司内部基准测得该版本网络攻防得分 81.0%，未做风险削减的同类版本为 90.5%，结果尚未经第三方独立验证。此前一周中国已提出对 AI 驱动恶意软件生成与漏洞发现工具的出口管制草案。',
    '路透社', 'AI·科技', '月之暗面;Kimi K3.1 Pro;开源权重;AI网络安全', 92, '2026-10-24',
    'https://www.reuters.com/technology/moonshot-curbs-hacking-ability-new-kimi-model-fears-grow-over-ai-powered-2026-10-24/')

add('China says US should stop discriminatory measures against Chinese research',
    '商务部要求美方停止对中国科研机构的歧视性措施',
    '针对美国国防部10月19日公布的高校科研安全审查结果——称相关高校已全面终止与"1286清单"实体（其中含大量中国科研机构）的合作，中国商务部23日以发言人答记者问形式回应。发言人表示中方一贯反对美方泛化国家安全概念，将科研交流政治化、武器化、工具化，并对中国科研机构作无理"污名化"指责；美方做法实质是胁迫美国科研机构"选边站队"，蓄意破坏中美正常科研合作，只会削弱美自身科技进步与创新能力。中方敦促美方立即停止歧视性、限制性措施，并将采取必要措施维护中国科研机构合法权益。',
    '路透社', '中美博弈', '1286清单;科研安全;国防部;学术脱钩', 90, '2026-10-23',
    'https://www.reuters.com/world/china/china-says-us-should-stop-discriminatory-measures-against-chinese-research-2026-10-23/')

add("China's Xi calls for qualitative improvement, measurable growth in economy",
    '习近平强调经济质的提升与可衡量增长',
    '据路透社报道，中国国家主席习近平22日就经济工作表态，强调推动经济实现质的有效提升与量的合理增长，把发展质量与实际成效放在更突出位置。此番表态在中共二十届五中全会（10月26日至29日）召开前夕作出，会议将聚焦党的治理与纪律建设，也被视为为明年全国党代会人事布局做准备。市场关注五中全会是否就"十五五"规划方向与扩大内需、科技自立自强等议题释放更明确信号。',
    '路透社', '中国外交', '习近平;经济增长;五中全会;十五五', 88, '2026-10-22',
    'https://www.reuters.com/world/china/chinas-xi-calls-qualitative-improvement-measurable-growth-economy-2026-10-22/')

add("China's foreign minister urges stronger governance of deep sea, outer space",
    '王毅呼吁加强深海与外空全球治理',
    '中国外交部长23日呼吁加强对深海与outer space（外空）等新兴领域的全球治理，主张在联合国框架下完善规则制定，防止少数国家垄断规则解释权与资源开发权。中方同时重申反对太空军备竞赛的立场，强调应通过多边协商保障发展中国家在深海资源与外空活动中的正当权益。相关表态出现在美方持续推动太空军事化、并加紧布局深海采矿规则的背景下。',
    '路透社', '全球多边', '王毅;深海治理;外空;全球治理', 80, '2026-10-23',
    'https://www.reuters.com/world/china/chinas-foreign-minister-urges-stronger-governance-deep-sea-outer-space-2026-10-23/')

add('Taiwan says China using militia boats to expand battlefield preparation, Western official says',
    '台湾称大陆用民兵船扩大"战场准备"',
    '台湾方面23日称，中国大陆正通过海上民兵船只扩大所谓"战场准备"，一名西方官员称相关活动已从单纯的海上存在展示转向更具实战意味的协同演练。台方指这些船只常与海警、海军行动配合，用于测试台方反应时间与海域管控能力。大陆方面一贯表示相关活动属正常渔业与巡航管理，反对任何"台独"分裂行径与外部干涉。',
    '路透社', '地区局势', '台海;海上民兵;战场准备;两岸', 85, '2026-10-23',
    'https://www.reuters.com/world/china/taiwan-says-china-using-militia-boats-expand-battlefield-preparation-western-2026-10-23/')

add('China opposes arms race in space, official document shows',
    '中方文件重申反对太空军备竞赛',
    '路透社查阅的官方文件显示，中国重申反对太空军备竞赛，主张通过谈判达成防止外空军备竞赛的国际法律文书，反对将外空武器化、战场化。文件强调应保障各国和平利用外空的平等权利，反对单边制裁与技术封锁妨碍发展中国家航天能力建设。这一立场与中方在联合国裁军谈判会议上的长期主张一致，也与美方推进太空军事力量建设形成对照。',
    '路透社', '全球多边', '外空军备竞赛;裁军;联合国;太空安全', 76, '2026-10-23',
    'https://www.reuters.com/world/china/china-opposes-arms-race-space-official-document-shows-2026-10-23/')

add('How China October 26-29 Communist Party plenum works',
    '解读：中共二十届五中全会如何运作',
    '路透社23日发布解读稿，梳理中共二十届五中全会（10月26日至29日在北京举行）的运作机制。文章介绍，全会由中央委员会全体成员出席，闭门进行，官方主题预计聚焦党的治理与纪律建设，人事议题亦可能涉及。会议形成的文件通常为下一阶段政策定调，并就明年全国党代会的人事与制度安排作前期准备，外界关注其对"十五五"规划、科技自立自强与内需政策的表述。',
    '路透社', '中国外交', '五中全会;中央委员会;治理与纪律', 78, '2026-10-23',
    'https://www.reuters.com/world/china/how-chinas-october-26-29-communist-party-plenum-works-2026-10-23/')

add('Tougher discipline, Xi authority key to China Communist Party fifth plenum',
    '更严纪律与习近平权威被视为五中全会主线',
    '路透社23日报道，中共二十届五中全会（10月26日至29日）预计以强化党内纪律与维护习近平核心权威为主线。此前政治局会议提前召开并强调反腐，多个省份在全会前完成党政一把手调整。分析人士认为，会议在聚焦治理与纪律的同时，也将为明年全国党代会的人事布局与制度安排铺路，并可能就"十五五"规划方向释放信号。',
    '路透社', '中国外交', '五中全会;党内纪律;反腐;人事布局', 80, '2026-10-23',
    'https://www.reuters.com/world/china/tougher-discipline-xis-authority-key-chinas-communist-partys-fifth-plenum-2026-10-23/')

add('EU ministers vow to tackle China shock 2.0 through talks with Beijing',
    '欧盟部长承诺通过对华谈判应对"中国冲击2.0"',
    '欧盟各国贸易部长23日承诺，将通过与中国谈判而非单纯加征关税的方式应对所谓"中国冲击2.0"，即中国在新能源、电动车与高端制造领域出口激增对欧洲产业的压力。部长们强调要与北京建立"有管理的贸易关系"，同时保留在谈判无进展时动用贸易防御工具的权利。此前欧盟已对中国电动车加征关税，并讨论本地化含量与最低价格等替代方案。',
    '路透社', '中欧与盟友', '欧盟;中国冲击;贸易防御;电动车', 86, '2026-10-23',
    'https://www.reuters.com/world/china/eu-ministers-vow-tackle-china-shock-20-through-talks-with-beijing-2026-10-23/')

add('How can EU limit impact of China shock 2.0',
    '分析：欧盟如何限制"中国冲击2.0"影响',
    '路透社23日刊发分析稿，梳理欧盟可用于限制"中国冲击2.0"影响的政策工具与难点。文章指出，欧盟在关税、反补贴调查、本地含量要求与政府采购限制之间权衡，但成员国意见分歧明显：德国等出口导向国家担忧反制伤及自身，法国与南欧国家则主张更强硬。分析认为，欧方更可能选择"谈判+有限防御工具"的组合路径，同时加快单一市场与产业政策改革。',
    '路透社', '中欧与盟友', '欧盟;中国冲击;产业政策;贸易工具', 78, '2026-10-23',
    'https://www.reuters.com/world/china/how-can-eu-limit-impact-china-shock-20-2026-10-23/')

add('HKEX launches AI semiconductor indexes, licenses AI index to China',
    '港交所推出 AI 与半导体指数 向内地授权 AI 指数',
    '香港交易所23日推出人工智能与半导体相关指数，并将一项 AI 指数授权给中国内地机构使用，以扩大香港在科技主题指数与衍生品市场的覆盖。此举被视作港交所深化与内地资本市场互联、丰富科技资产配置工具的一步，也呼应了近期港股科技板块活跃、南向资金持续流入的态势。',
    '路透社', '中欧与盟友', '港交所;AI指数;半导体;资本市场', 72, '2026-10-23',
    'https://www.reuters.com/world/asia-pacific/hkex-launches-ai-semiconductor-indexes-licenses-ai-index-china-2026-10-23/')

add("China's January-September fiscal revenue up 5.1% y/y",
    '中国前三季度财政收入同比增长5.1%',
    '路透社援引官方数据报道，中国1至9月财政收入同比增长5.1%，在税收收入温和修复与非税收入支撑下延续正增长。同期财政支出保持强度，用于基建投资、民生保障与地方化债。数据发布之际，市场关注四季度增量财政政策力度，以及五中全会后"十五五"规划对财政可持续性的安排。',
    '路透社', '中国外交', '财政收入;前三季度;财政政策', 74, '2026-10-23',
    'https://www.reuters.com/world/asia-pacific/chinas-january-september-fiscal-revenue-up-51-yy-2026-10-23/')

add('Foreign investment flows into China fall 4.3% y/y first three quarters',
    '前三季度中国实际使用外资同比下降4.3%',
    '路透社援引商务部数据报道，今年前三季度中国实际使用外资金额同比下降4.3%，延续两位数收窄后的负增长态势。分析认为，地缘政治紧张、供应链多元化布局与美方对外投资限制预期共同抑制外资流入，而高技术制造业与服务业仍是结构性亮点。数据发布前一日，中国商务部刚就美方拟扩大对华投资限制表达坚决反对。',
    '路透社', '中国外交', '外商直接投资;FDI;外资;经贸环境', 80, '2026-10-22',
    'https://www.reuters.com/world/asia-pacific/foreign-investment-flows-into-china-fall-43-yy-first-three-quarters-2026-10-22/')

add("China's BYD plans to double capacity at Brazilian plant",
    '比亚迪拟将巴西工厂产能翻倍',
    '路透社23日报道，中国比亚迪计划将其巴西工厂产能翻倍，以应对拉美市场需求增长并规避当地进口关税上升。比亚迪在巴伊亚州卡马萨里设有整车厂，此前因进口整车关税上调而加快本地化生产。扩产计划涵盖整车组装与本地供应链培育，是其在美洲推进本地制造战略的关键一步。',
    '路透社', '中欧与盟友', '比亚迪;巴西;产能扩张;本地化', 74, '2026-10-23',
    'https://www.reuters.com/business/autos-transportation/chinas-byd-plans-double-capacity-brazilian-plant-2026-10-23/')

add("China's Chery expects overseas-manufactured vehicles to top 50% of exports, exec says",
    '奇瑞预计海外本地生产车辆将占出口过半',
    '路透社23日报道，中国奇瑞汽车一位高管表示，公司预计海外本地化生产的车辆将超过其出口总量的一半，反映其在多国落地组装与产能布局的推进速度。奇瑞近年加速在东南亚、南美与欧洲布局本地工厂，以应对关税壁垒与本地含量要求。这一转向也代表中国车企从"整车出口"向"海外制造+本地供应链"的整体迁移趋势。',
    '路透社', '中欧与盟友', '奇瑞;汽车出口;海外制造;本地化', 72, '2026-10-23',
    'https://www.reuters.com/business/autos-transportation/chinas-chery-expects-overseas-manufactured-vehicles-top-50-exports-exec-says-2026-10-23/')

add('China calls on oil, gas firms to boost output and build strategic supply bases',
    '中国要求油气企业增产并建设战略供应基地',
    '路透社23日报道，中国已要求国内石油与天然气企业加大勘探开发力度、提升产量，并加快建设战略性供应基地，以增强能源安全与应对国际局势波动的能力。要求提出之际，中东局势紧张推高油价，霍尔木兹海峡与红海航运风险上升，中国作为全球最大原油进口国对进口通道安全的关注同步上升。',
    '路透社', '中国外交', '能源安全;油气增产;战略储备', 78, '2026-10-23',
    'https://www.reuters.com/business/energy/china-calls-oil-gas-firms-boost-output-build-strategic-supply-bases-2026-10-23/')

add("China's Sigenergy to build inverter, battery storage plants in India",
    '中国思格新能源将在印度建逆变器与储能工厂',
    '路透社23日报道，中国储能企业思格新能源（Sigenergy）计划在印度建设逆变器与电池储能工厂，以进入这一快速增长的市场并规避贸易壁垒。印度近年对中国企业投资审查趋严，本地化生产成为中企进入印度市场的主要路径。该项目反映中国储能产业链向海外扩张、寻求新兴市场需求增量的趋势。',
    '路透社', '中欧与盟友', '储能;思格新能源;印度;本地制造', 70, '2026-10-23',
    'https://www.reuters.com/business/energy/chinas-sigenergy-build-inverter-battery-storage-plants-india-2026-10-23/')

add('China aims to stabilise number of new births with policy support',
    '中国拟以政策支持稳定新出生人口规模',
    '路透社23日报道，中国正通过育儿补贴、托育服务扩容、住房与税收支持等一揽子政策稳定新出生人口规模，以缓解出生人口持续下滑与人口老龄化加速的压力。报道指出，相关措施已纳入地方考核，多地推出一次性生育补贴与延长产假。北京近期多次强调建设"生育友好型社会"，人口结构变化也被视为影响中长期潜在增长率的关键变量。',
    '路透社', '中国外交', '生育政策;人口;老龄化;育儿补贴', 82, '2026-10-23',
    'https://www.reuters.com/business/healthcare-pharmaceuticals/china-aims-stabilise-number-new-births-with-policy-support-2026-10-23/')

add('GLP-1 boom in China, India, Brazil could create $22 bln market by 2035, JPMorgan says',
    '摩根大通：中印巴 GLP-1 市场2035年或达220亿美元',
    '路透社23日报道，摩根大通在最新研究报告中预计，随着减重与糖尿病用药需求上升，中国、印度与巴西三国 GLP-1 类药物市场到2035年可能达到220亿美元规模。报告指出，本土仿制药与生物类似药上市、可及性提升与支付能力改善是主要驱动因素，但价格下行压力与产能约束也将影响利润空间。中国本土多家药企正加速 GLP-1 管线布局。',
    '路透社', '其他', 'GLP-1;减重药;医药市场;摩根大通', 70, '2026-10-23',
    'https://www.reuters.com/business/healthcare-pharmaceuticals/glp-1-boom-china-india-brazil-could-create-22-bln-market-by-2035-jp-morgan-says-2026-10-23/')

add('Baidu tests robotaxi on London streets',
    '百度在伦敦测试自动驾驶出租车',
    '路透社23日报道，中国百度已在伦敦街头测试其自动驾驶出租车（Robotaxi）服务，这被视为中国自动驾驶企业进入欧洲市场的重要一步。百度旗下 Apollo Go 此前已在中国多个城市与中东地区开展无人驾驶运营，此次伦敦测试需符合英国相关监管要求并分阶段推进。中国自动驾驶方案的海外落地正成为中欧科技竞争与合作的新焦点。',
    '路透社', 'AI·科技', '百度;自动驾驶;Robotaxi;伦敦', 82, '2026-10-23',
    'https://www.reuters.com/business/finance/chinas-baidu-tests-robotaxi-london-streets-2026-10-23/')

add('China urges government agencies to mitigate AI job displacement',
    '中国要求政府部门应对 AI 就业替代',
    '路透社23日报道，中国已要求政府部门采取措施缓解人工智能对就业的替代效应，包括加强职业技能培训、完善社会保障与失业监测、推动"AI+就业"协同。报道称相关要求在稳就业政策框架下提出，反映决策层对 AI 快速渗透制造业与服务业岗位的警觉。中国今年高校毕业生规模再创新高，结构性就业压力与 AI 替代叠加成为政策关注点。',
    '路透社', 'AI·科技', 'AI就业;就业政策;技能培训;社会保障', 85, '2026-10-23',
    'https://www.reuters.com/business/world-at-work/china-urges-government-agencies-mitigate-ai-job-displacement-2026-10-23/')

add('North Korea Kim Jong Un arrives in Dandong, China, Yonhap says',
    '金正恩抵达中国丹东 朝中关系受关注',
    '据韩联社消息，朝鲜最高领导人金正恩24日抵达中国边境城市丹东，为其一年多来首次访华。朝中双方均强调传统友谊并呼吁加强合作。此次行程发生在下月朝鲜重要政治日程之前，路透社另报道称金正恩经新开通的边境大桥进入中国，朝中贸易往来同步升温。',
    '路透社', '地区局势', '金正恩;中朝关系;丹东;边境贸易', 88, '2026-10-24',
    'https://www.reuters.com/world/china/north-koreas-kim-jong-un-arrives-dandong-china-yonhap-says-2026-10-24/')

add('Typhoon Champi sweeps past Taiwan, leaving 1 dead, 500 injured',
    '台风"海鸥"掠过台湾致1死500伤',
    '路透社24日报道，台风"海鸥"（Champi）掠过台湾，造成1人死亡、约500人受伤。台风此前导致台湾多地停班停课、数百架次航班取消，随后减弱并朝日本方向移动。台湾气象部门已解除部分警报，但提醒沿海与山区注意强降雨与地质灾害风险。',
    '路透社', '地区局势', '台风海鸥;台湾;航班取消;灾害', 76, '2026-10-24',
    'https://www.reuters.com/business/environment/typhoon-champi-sweeps-past-taiwan-leaving-1-dead-500-injured-2026-10-24/')

add('Earthquake of magnitude 7 strikes China Tibet',
    '西藏发生7级地震 死亡人数暂为16人',
    '路透社报道，中国西藏地区发生7级地震，造成人员伤亡与基础设施损坏。后续报道显示，地震死亡人数维持在16人，受伤人数上升约65%。救援力量已进入震区开展搜救与安置，当地通信、道路与电力部分中断。西藏地处高原，平均海拔高、气候寒冷，救援与物资投送难度较大。',
    '路透社', '其他', '西藏;地震;应急救援;灾情', 74, '2026-10-22',
    'https://www.reuters.com/business/environment/earthquake-magnitude-7-strikes-chinas-tibet-2026-10-22/')

add('Beijing deputy mayor placed under probe, China anti-graft watchdog says',
    '北京市一名副市长被查',
    '路透社22日报道，中国反腐机构对北京市一名副市长立案调查，指其涉嫌严重违纪违法。通报未披露具体案情，但此类案件通常涉及工程、土地或国企资源等领域。此次调查发生在政治局会议提前召开、强调强化反腐与纪律建设之际，也是五中全会前人事与纪律整顿的一部分。',
    '路透社', '中国外交', '反腐;北京市;纪律审查', 78, '2026-10-22',
    'https://www.reuters.com/world/asia-pacific/beijing-deputy-mayor-placed-under-probe-chinas-anti-graft-watchdog-says-2026-10-22/')

add('China-backed Shanghai International offers to buy 51% stake in Haitong Unitrust',
    '上海国际集团拟收购海通恒信51%股权',
    '路透社23日报道，具有上海国资背景的上海国际集团提出收购海通恒信国际租赁（Haitong Unitrust）51%股权，交易尚待监管与股东批准。此举被视为上海推进地方金融机构整合、理顺融资租赁板块股权结构的一步，也与海通证券与国泰君安合并后的资产重整相关。',
    '路透社', '中国外交', '上海国际集团;海通恒信;股权收购;金融整合', 66, '2026-10-23',
    'https://www.reuters.com/world/asia-pacific/china-backed-shanghai-international-offers-buy-51-stake-haitong-unitrust-12-2026-10-23/')

add('Citi wins licence to set up wholly owned China securities unit',
    '花旗获批设立全资中国证券子公司',
    '路透社23日报道，花旗集团获得监管批准，将在华设立全资证券子公司。此举使花旗成为中国放开外资券商持股比例限制后，又一家实现全资控股在华证券业务的外资机构。花旗此前已将在华个人银行业务出售，此次获批标志着其在中国市场重心转向企业与机构业务。',
    '路透社', '中欧与盟友', '花旗;外资券商;金融开放;证券', 76, '2026-10-23',
    'https://www.reuters.com/world/china/citi-wins-licence-set-up-fully-owned-china-securities-unit-2026-10-23/')

add('South Africa trade with China surges after duty-free deal',
    '南非对华贸易在零关税安排后激增',
    '路透社22日报道，南非与中国的贸易在双方达成零关税安排后显著增长，南非对华出口的农产品与矿产品增幅明显。分析认为，该安排增强了南非在中国市场的价格竞争力，但也引发对南非本土制造业受到中国商品冲击的担忧。相关进展是中国深化与全球南方国家经贸关系的具体案例。',
    '路透社', '中欧与盟友', '南非;零关税;中南贸易;全球南方', 74, '2026-10-22',
    'https://www.reuters.com/world/asia-pacific/south-africas-trade-with-china-surges-after-duty-free-deal-2026-10-22/')

add('US expected to remove 50% tariffs on some Canadian agricultural, forestry goods, WSJ reports',
    '美拟下调部分加拿大农产品与林产品关税',
    '路透社援引《华尔街日报》报道，美国预计将取消对部分加拿大农产品与林产品加征的50%关税，以缓解与渥太华的贸易摩擦。此举发生在中期选举临近、缅因等州相关产业承压的背景下。此前特朗普政府已就加拿大部分商品调整第338条款关税范围，汽车与木材领域仍是争议焦点。',
    '路透社', '美国内政', '美加贸易;关税;第338条款;中期选举', 72, '2026-10-23',
    'https://www.reuters.com/business/us-expected-remove-50-tariffs-some-canadian-agricultural-forestry-goods-wsj-2026-10-23/')

add('Trump set to announce plan by Audi to build US factory in Georgia, source says',
    '特朗普将宣布奥迪在佐治亚州建厂',
    '路透社援引消息人士报道，美国总统特朗普将在佐治亚州竞选集会上宣布大众汽车旗下奥迪品牌在美建厂计划，投资规模约42亿美元。特朗普以此论证关税政策促使制造业回流，称"20万辆车"将在美国生产。该消息发布之际正值中期选举冲刺阶段，佐治亚是关键摇摆州之一。',
    '路透社', '美国内政', '奥迪;佐治亚;制造业回流;关税', 74, '2026-10-24',
    'https://www.reuters.com/business/autos-transportation/trump-set-announce-plan-by-audi-build-us-factory-georgia-source-says-2026-10-24/')

add('Iran has detailed plans to hit Gulf undersea cables if war resumes, officials say',
    '官员称伊朗已制定战时打击海湾海底电缆方案',
    '路透社23日援引多名官员报道，伊朗已就一旦战事重启时打击海湾海底通信电缆制定详细方案。官员称相关计划涉及多条承载区域互联网与金融数据传输的关键线路，一旦实施将严重影响海湾国家的通信与金融基础设施。此番披露正值美伊紧张升级、也门胡塞武装与沙特冲突加剧之际，地区航运与能源通道风险同步上升。',
    '路透社', '地区局势', '伊朗;海底电缆;海湾;基础设施安全', 88, '2026-10-23',
    'https://www.reuters.com/world/middle-east/iran-has-detailed-plans-hit-gulf-undersea-cables-if-war-resumes-officials-say-2026-10-23/')

add('Iran has ramped up efforts to target US personnel, intelligence memo warns',
    '情报备忘录警告伊朗加大针对美方人员力度',
    '路透社24日报道，一份美国情报备忘录警告，伊朗已加大针对美国人员的行动力度，风险等级上升。备忘录发布之际，美方与以色列对伊政策协调加强，伊朗国内亦在评估临时协议失败后的应对。美方官员称正评估在中东地区的部队防护与人员安全措施。',
    '路透社', '地区局势', '伊朗;美国人员;情报预警;中东安全', 84, '2026-10-24',
    'https://www.reuters.com/world/middle-east/iran-has-ramped-up-efforts-target-us-personnel-intelligence-memo-warns-2026-10-24/')

add('Yemen Houthis renew warning against using Riyadh airport',
    '胡塞武装再次警告勿使用利雅得机场',
    '路透社24日报道，也门胡塞武装再次警告各方不要使用利雅得机场，称其仍属打击范围。此前胡塞方面已多次对沙特境内目标发动袭击，沙特防空系统拦截多枚导弹与无人机。警告对区域航空运输构成直接威胁，多家航司已调整相关航线。',
    '路透社', '地区局势', '胡塞武装;利雅得机场;也门;沙特', 80, '2026-10-24',
    'https://www.reuters.com/world/middle-east/yemens-houthis-renew-warning-against-using-riyadh-airport-2026-10-24/')

# ================= 南华早报 =================
add("How China's regional leadership changes offer clues to the future of the Communist Party",
    '中国省级人事更替如何透露中共未来走向',
    '南华早报25日报道，中国的五年领导周期正在省级层面展开，新班子陆续到位，为观察全国层面中共走向提供重要线索。上周安徽、河南、山西、新疆四省区完成党代会并产生新一届党委常委会，会议在10月26日至29日举行的二十届五中全会前一周召开。文章指出，省级党代会将确定未来五年发展规划与官员去留，全部流程预计明年6月完成，年底前有14个省份开会；明年直辖市党代会将为全国党代会人事安排提供关键线索，新任省级党政主官几乎确定进入中央委员会。',
    '南华早报', '中国外交', '省级党代会;人事布局;五中全会;中央委员会', 88, '2026-10-25',
    'https://www.scmp.com/news/china/politics/article/3372064/how-chinas-regional-leadership-changes-offer-clues-future-communist-party')

add('Beijing pledges to back Taiwan pro-unification patriots as it marks key anniversary',
    '北京纪念台湾光复81周年 承诺支持岛内统派',
    '南华早报25日报道，北京在纪念日本殖民统治结束81周年之际，承诺支持台湾岛内的促统力量，并同步展开集中宣传活动。10月25日这一纪念日由北京于去年正式设立。报道称，大陆方面通过纪念活动与舆论宣传强化"两岸同属一个中国"的叙事，同时批评台湾当局的"去中国化"做法。',
    '南华早报', '地区局势', '台湾光复;统一;纪念日;两岸关系', 86, '2026-10-25',
    'https://www.scmp.com/news/china/politics/article/3372065/beijing-commemorates-end-japanese-rule-over-taiwan-call-reunification')

add("Will China's 4 peace principles for tackling African conflicts work?",
    '中国就非洲冲突提出四项和平原则 成效待观察',
    '南华早报25日报道，中国国家主席习近平本月在多哥总统福雷访华期间，提出以四项原则为核心的应对非洲冲突与热点问题方案，把和平与发展相联结。报道梳理四原则内涵及其在非洲之角、萨赫勒等地区的适用性，并指出中方主张"非洲问题非洲解决"、反对外部干涉，同时以基础设施与安全合作作为支撑。分析认为，该框架的实际效果取决于资金投入与地区国家配合度。',
    '南华早报', '全球多边', '非洲;和平原则;习近平;中非合作', 82, '2026-10-25',
    'https://www.scmp.com/news/china/diplomacy/article/3372047/will-chinas-4-peace-principles-tackling-african-conflicts-work')

add('Fandom vs flag: why young Chinese embrace Japanese pop culture but reject war-era symbols',
    '中国年轻人为何接受日本流行文化却拒绝战前象征',
    '南华早报25日报道，中国年轻人喜爱动漫、音乐等日本流行文化，但对日本军国主义象征划出明确界限。这一界限近期在莫斯科国立大学一次事件中受到考验——中国留学生与一名佩戴日本旭日旗图案的同学发生对峙。报道认为，这种"文化接受与政治拒斥并存"的态度，反映历史记忆在代际中的延续方式发生变化。',
    '南华早报', '中国外交', '中日关系;流行文化;历史记忆;青年', 70, '2026-10-25',
    'https://www.scmp.com/news/china/diplomacy/article/3372036/fandom-vs-flag-why-young-chinese-embrace-japanese-pop-culture-reject-war-era-symbols')

add("China's next generation of leaders waiting in the wings for more senior roles",
    '中共"下一代"领导层正待更高级别岗位',
    '南华早报24日报道，中央委员会全会是中国政治日历上的重大事件，而更年轻的官员群体正在为更高层岗位积累资历。文章梳理省级党代会中新任省委常委的年龄结构，指出"63岁""58岁"两条惯例年龄线正在发挥作用，同时也有超龄留任的特殊案例。作者认为，明年全国党代会前的省级人事布局，将决定二十一届中央委员会的构成。',
    '南华早报', '中国外交', '人事布局;年龄线;中央委员会;党代会', 82, '2026-10-24',
    'https://www.scmp.com/news/china/politics/article/3372013/chinas-next-generation-leaders-waiting-wings-more-senior-roles')

add("China's J-20 stealth jet designers plan to put powerful radar into aircraft wing",
    '歼-20 设计团队拟将强功率雷达嵌入机翼',
    '南华早报24日报道，中国歼-20隐身战斗机设计团队正研究把主雷达嵌入机翼结构，以突破传统机头雷达罩的空间限制并提升探测孔径。文章指出，机翼具备较大表面积，但气动、结构与散热难题需同步解决。若实现，将有助于提升战机的态势感知与反隐身对抗能力。该研究由中国航空工业相关院所团队推进，具体工程化时间表未公开。',
    '南华早报', '地区局势', '歼-20;机翼雷达;隐身战机;解放军空军', 84, '2026-10-24',
    'https://www.scmp.com/news/china/science/article/3371706/chinas-j-20-stealth-jet-designers-plan-put-powerful-radar-aircraft-wing')

add("Leading Chinese economic commentator Ren Zeping's social media account restricted",
    '知名经济评论人任泽平社交媒体账号被限制',
    '南华早报24日报道，中国知名经济学家任泽平的社交媒体账号被限制，网民于周六发现其微信公众号已无法正常访问或发布内容。报道称，此举是北京加强对金融市场"网红"与投资意见领袖监管的一部分。任泽平以直言评论宏观经济与资本市场著称，此前其部分观点曾引发争议。',
    '南华早报', '中国外交', '任泽平;社交媒体;金融监管;意见领袖', 78, '2026-10-24',
    'https://www.scmp.com/news/china/money-wealth/article/3372032/leading-chinese-economic-commentator-ren-zepings-social-media-account-restricted')

add("Ukraine's Starlink woes should be a wake-up call for Taiwan, analysts say",
    '分析：乌克兰"星链"困境应为台湾敲响警钟',
    '南华早报24日报道，分析人士警告，台湾不应在战时关键通信上依赖单一外国卫星服务商。此前马斯克旗下"星链"（Starlink）使用受限，扰乱了乌克兰无人机作战；马斯克本人随后承认曾限制乌方连接速度，服务已恢复。分析认为，台湾应加快自主卫星通信与备份链路建设，并评估商业卫星服务在冲突情境下的可用性风险。',
    '南华早报', '地区局势', '星链;台湾防务;卫星通信;乌克兰', 84, '2026-10-24',
    'https://www.scmp.com/news/china/military/article/3372016/ukraines-starlink-woes-should-be-wake-call-taiwan-analysts-say')

add('North Korean leader Kim Jong-un pays unexpected visit to Chinese border city of Dandong',
    '金正恩突访中国边境城市丹东',
    '南华早报24日报道，朝鲜最高领导人金正恩24日访问中国边境城市丹东，双方强调传统友谊并呼吁加强合作。这是金正恩一年多来首次访华，行程发生在下月朝鲜重要政治日程之前。报道称，金正恩此行经新开通的朝中边境大桥入境，双方贸易往来近期明显升温，被视为朝中关系回暖的信号。',
    '南华早报', '地区局势', '金正恩;中朝关系;丹东;边境', 88, '2026-10-24',
    'https://www.scmp.com/news/china/diplomacy/article/3372026/north-korean-leader-kim-jong-un-visits-chinese-border-city-dandong')

add('Is Washington misreading Beijing? Decline in US visits to China sparks concern',
    '美国访华人数下降引发"误读北京"担忧',
    '南华早报24日报道，美国赴华访问人数明显下降，引发对华盛顿"误读北京"的担忧。文章以退役美国海军陆战队上校、安全分析师 Grant Newsham 近期受访时称中国经济崛起"是虚幻的"、并称"至少6亿中国人每天生活费不超过5美元"的言论为例，指出缺乏实地接触易导致认知偏差与政策误判。报道呼吁恢复学术、商界与地方层面的交流渠道。',
    '南华早报', '中美博弈', '中美交流;认知偏差;实地访问;政策误判', 82, '2026-10-24',
    'https://www.scmp.com/news/china/diplomacy/article/3371535/washington-misreading-beijing-decline-us-visits-china-sparks-concern')

add("'Systematically dismantled': Hegseth's new offensive against China Confucius Institutes",
    '赫格塞斯加大对孔子学院打击力度',
    '南华早报24日报道，在特朗普今年第二次访华、与习近平第三次会晤前数周，其政府正加强对孔子学院的打击。美国国防部此前要求30所高校审查与"外国关注实体"（含更名后的孔子学院）的合作，多所高校已宣布终止相关合作。文章引述学者称，此举或影响两国人文交流与中文教学，也被视为美方在元首会晤前保留施压筹码。',
    '南华早报', '中美博弈', '孔子学院;赫格塞斯;人文交流;国防部', 86, '2026-10-24',
    'https://www.scmp.com/news/china/diplomacy/article/3372023/systematically-dismantled-hegseths-new-offensive-against-chinas-confucius-institutes')

add('Thousands evacuated and flights grounded as Typhoon Champi hits eastern China',
    '台风"海鸥"袭击中国东部 数万人转移逾百航班取消',
    '南华早报24日报道，台风"海鸥"持续袭击中国东部沿海，导致上海等地机场逾百架次航班取消，当局转移数万人。台风在向日本方向移动过程中逐渐减弱。中央气象台此前发布台风预警，浙江、福建、上海等地启动应急响应，部分沿海景区与轮渡停运。',
    '南华早报', '中国外交', '台风海鸥;上海;航班取消;应急响应', 76, '2026-10-24',
    'https://www.scmp.com/news/china/politics/article/3372015/thousands-evacuated-and-flights-grounded-typhoon-champi-hits-eastern-china')

add('Hong Kong seeks bigger role for yuan in regional trade, treasury chief says',
    '香港拟扩大人民币在区域贸易中的角色',
    '南华早报25日报道，香港财政司司长表示，港府官员在上周 APEC 会议期间与文莱等经济体的财长及代表讨论减少对美元依赖、扩大本币与人民币在双边贸易结算中的使用。报道称，香港正争取在区域贸易结算、离岸人民币产品与相关金融基础设施上发挥更大作用，配合国家推动人民币国际化的整体部署。',
    '南华早报', '中欧与盟友', '人民币国际化;香港;APEC;贸易结算', 84, '2026-10-25',
    'https://www.scmp.com/news/hong-kong/hong-kong-economy/article/3372073/hong-kong-seeks-bigger-role-yuan-regional-trade-treasury-chief-says')

add('Filipinos split on Marcos South China Sea handling amid row over Jing Quan remarks',
    '民调显示菲民众对马科斯南海处理分歧明显',
    '南华早报25日报道，一项新调查显示，菲律宾民众对马科斯政府处理对华海上争端的表现几乎各半，但近四分之三受访者倾向以外交而非对抗方式解决。这一偏好在菲方官员景泉（Jing Quan）相关言论引发争议后更具现实意义。调查同时显示，民众对美菲同盟在南海问题上的作用看法分歧。',
    '南华早报', '地区局势', '菲律宾;南海;民调;马科斯', 82, '2026-10-25',
    'https://www.scmp.com/week-asia/politics/article/3371980/filipinos-split-marcos-south-china-sea-handling-amid-row-over-jing-quans-remarks')

add('Trump hails tariffs for new US$4.2 billion Audi plant in Georgia',
    '特朗普以奥迪42亿美元佐治亚建厂为关税政策背书',
    '南华早报25日报道，美国总统特朗普在佐治亚州竞选集会上为关税政策辩护，称其让美国更富裕，并宣布大众汽车同意在该州新建一座投资42亿美元的奥迪工厂。特朗普称"想想看，20万辆车"，以此论证关税促使制造业回流。该州是关键摇摆州，集会发生在中期选举前两周。',
    '南华早报', '美国内政', '奥迪;佐治亚;关税;中期选举', 74, '2026-10-25',
    'https://www.scmp.com/news/world/united-states-canada/article/3372051/trump-hails-tariffs-new-us42-billion-audi-plant-georgia')

add('Seoul useless placation is a warning for all US trade partners',
    '评论：首尔的无用安抚对所有美国贸易伙伴都是警示',
    '南华早报24日刊发评论，指出韩国在美国压力下于去年11月签署3500亿美元投资协议，换取10个百分点的关税下调，并将其包装为"战略同盟"。不到一年，这一安排的实际效果已大幅缩水。文章认为，首尔的经验对其他美国贸易伙伴具有警示意义：以巨额投资换取关税让步，难以获得稳定预期，反而可能形成持续的让利压力。',
    '南华早报', '中欧与盟友', '韩国;对美投资;关税;贸易谈判', 78, '2026-10-24',
    'https://www.scmp.com/opinion/asia-opinion/article/3371802/seouls-useless-placation-warning-all-us-trade-partners')

add('How to share AI wealth? Neither the US nor Asia has the answer',
    '评论：AI 财富如何分配 美亚均无答案',
    '南华早报24日刊发评论，指出 AI 创造的财富如何在公共与私人之间分配，美国与亚洲均未给出成熟答案。文章举例称，Anthropic 于10月18日承诺将5%股份投入公益基金，马斯克次日承诺明年向"每个孩子"赠送一股 SpaceX 股票。作者认为，这类承诺缺乏制度约束，真正的分配机制应来自税收、公共服务与劳动者技能投资。',
    '南华早报', 'AI·科技', 'AI财富分配;公益基金;科技巨头;社会政策', 72, '2026-10-24',
    'https://www.scmp.com/opinion/world-opinion/article/3371822/how-share-ai-wealth-neither-us-nor-asia-has-answer')

add('What next for Hong Kong developers in mainland China?',
    '香港开发商在内地下一步怎么走',
    '南华早报25日报道，香港主要地产商正把在内地的投资从住宅项目转向商业资产，包括酒店与长租公寓等。报道称，住宅销售疲弱、优质投资机会减少，促使开发商聚焦存量物业运营与经常性收入，而非继续大规模拿地开发。这一转向也反映内地房地产行业深度调整对港资房企战略的影响。',
    '南华早报', '中欧与盟友', '香港地产;内地投资;商业地产;房地产调整', 70, '2026-10-25',
    'https://www.scmp.com/property/article/3371965/whats-next-hong-kong-developers-mainland-china')

# ================= 金融时报 (官方 RSS) =================
add("Luxury groups' value drops by €250bn as Chinese consumer demand fades",
    '中国消费需求走弱 奢侈品集团市值蒸发2500亿欧元',
    '英国《金融时报》25日报道，随着中国消费者需求减弱，全球奢侈品集团市值累计蒸发约2500亿欧元。报道称，中国市场需求曾是推动奢侈品行业多年高增长的核心动力，如今消费者支出趋于谨慎、出境购物减少，令路威酩轩、开云等集团业绩承压。分析师担忧，需求疲软可能从周期性因素转为结构性变化，行业需要重新评估对中国市场的增长假设。',
    '金融时报', '其他', '奢侈品;中国消费;市值蒸发;需求走弱', 86, '2026-10-25',
    'https://www.ft.com/content/1c3065cf-538f-433a-9749-0355a3642c7c')

add("North Korea's Kim crosses new China border bridge to reaffirm ties",
    '金正恩经新边境大桥访华 重申朝中关系',
    '英国《金融时报》24日报道，朝鲜最高领导人金正恩经新开通的朝中边境大桥进入中国，重申两国传统友好关系。报道称，此次访问是金正恩一年多来首次访华，象征双边往来在疫情后逐步恢复，双方贸易与人员交流近期同步升温。访问发生在朝鲜下月重要政治日程之前，外界关注朝中在经贸与安全领域的合作动向。',
    '金融时报', '地区局势', '金正恩;朝中关系;边境大桥;东北亚', 86, '2026-10-24',
    'https://www.ft.com/content/fd106d25-3abf-4729-be26-683d1d115d2e')

add('Bolsonaro and Lula face off in knife-edge Brazil election',
    '巴西大选胶着 博索纳罗与卢拉对决',
    '英国《金融时报》25日报道，巴西大选进入决战阶段，卢拉与博索纳罗家族候选人对决，选情势均力敌。报道称，选举结果将影响巴西的财政政策走向、亚马逊雨林保护与对外经贸关系，包括与中国的农产品与矿产贸易格局。市场高度关注选举结果对巴西雷亚尔与主权债务的影响。',
    '金融时报', '地区局势', '巴西大选;卢拉;博索纳罗;拉美政治', 74, '2026-10-25',
    'https://www.ft.com/content/29033fb9-2dc7-4af0-a2ff-55d1bdd5dece')

add('Martin Wolf on the US midterms: What is at stake for the world?',
    '马丁·沃尔夫：美国中期选举对世界意味着什么',
    '英国《金融时报》25日刊发首席经济评论员马丁·沃尔夫的文章，分析美国中期选举对全球经济与秩序的潜在影响。文章认为，若共和党失去国会控制权，特朗普政府的关税政策、财政扩张与对外施压路径可能受限；反之，贸易保护与对外强硬或进一步制度化。作者指全球市场与盟友都在为两种情形做准备，而选举结果对多边体系走向具有溢出效应。',
    '金融时报', '美国内政', '中期选举;马丁·沃尔夫;关税;全球秩序', 78, '2026-10-25',
    'https://www.ft.com/content/01119d92-0d23-4d91-8a66-44ebd94c2356')

# ================= 彭博社 (专用 RSS 通道) =================
add('Chinese Manufacturer Dongshan Raises $1.3 Billion in HK Listing',
    '苏州东山精密香港上市募资13亿美元',
    '彭博社25日报道，印制电路板制造商苏州东山精密制造在香港上市，募资约99亿港元（13亿美元），成为近期香港新股市场的重要交易之一。报道称，该公司产品应用于消费电子与新能源汽车等领域，此次上市反映港股对硬科技与制造类企业的融资吸引力回升，也与年内南向资金持续流入、IPO市场回暖的态势一致。',
    '彭博社', '中欧与盟友', '东山精密;港股IPO;印制电路板;融资', 80, '2026-10-25',
    'https://www.bloomberg.com/news/articles/2026-10-25/chinese-manufacturer-dongshan-raises-1-3-billion-in-hk-listing')

add('Sinking Profits Turn China $3.5 Trillion Stock Rout Into Trap',
    '盈利下滑使中国3.5万亿美元股市抛售沦为陷阱',
    '彭博社25日报道，中国企业盈利持续下滑，令市值约3.5万亿美元的中国股市抛售难以止息，投资者陷入"越跌越不敢买"的困境。报道称，市场对中国股票的悲观情绪弥漫，抛售加深且看不到尽头，投资者正面盈利下修、地产拖累与外部压力等多重挑战。分析师认为，在盈利拐点明确之前，估值修复缺乏基本面支撑。',
    '彭博社', '其他', '中国股市;盈利下滑;抛售;估值', 90, '2026-10-25',
    'https://www.bloomberg.com/news/articles/2026-10-25/sinking-profits-turn-china-s-3-5-trillion-stock-rout-into-trap')

add('Goldman Cuts Kospi 12-Month Target by 25% as AI Trade Unravels',
    '高盛下调韩国综指12个月目标25% AI交易瓦解',
    '彭博社25日报道，高盛策略师将韩国综合股价指数（Kospi）12个月目标点位下调25%，此前该行曾上调预期。报道称，AI 相关交易出现瓦解迹象，存储芯片与算力供应链估值承压，韩国作为存储芯片核心产地首当其冲。分析认为，AI 资本开支持续性的疑虑正从美国科技股向亚洲供应链传导。',
    '彭博社', 'AI·科技', '高盛;韩国综指;AI交易;存储芯片', 86, '2026-10-25',
    'https://www.bloomberg.com/news/articles/2026-10-25/goldman-cuts-kospi-12-month-target-by-25-as-ai-trade-unravels')

add('AI Provides Zero Payoff to S&P 493 Outside Tech, Apollo Economist Says',
    '阿波罗经济学家：AI 对科技股以外企业"零回报"',
    '彭博社25日报道，阿波罗全球管理公司经济学家表示，尽管企业在人工智能上投入巨额资本，但对标普500指数中科技板块以外的493家公司而言，AI 带来的回报"为零"。报道称，这一判断对"AI 提升全行业生产率"的叙事构成质疑，也解释了为何资本开支集中于少数超大规模科技公司，而更广泛的企业盈利未见明显改善。',
    '彭博社', 'AI·科技', 'AI回报;生产率;阿波罗;资本开支', 84, '2026-10-25',
    'https://www.bloomberg.com/news/articles/2026-10-25/ai-provides-zero-payoff-to-s-p-493-outside-tech-apollo-economist-says')

add('China Hits Back at US Proposal to Tighten Investment Limits',
    '中国回击美方收紧对华投资限制提案',
    '彭博社24日报道，中国对美国财政部拟扩大并加严对外投资限制的提案表示"坚决反对"。报道称，该提案将生物技术新增为受限领域，并扩大高性能计算与高超音速系统的覆盖范围，中方指其歧视性扩大涉华限制、违背两国元首共识，并保留采取反制措施的权利。美方称措施并非只针对中国，旨在防止美国资本支持对手发展军民两用技术。',
    '彭博社', '中美博弈', '对外投资限制;生物技术;中美经贸;反制', 90, '2026-10-24',
    'https://www.bloomberg.com/news/articles/2026-10-24/china-hits-back-at-us-proposal-to-tighten-investment-limits')

add('Venezuela to Restart a Crucial Power Plant With China Help',
    '委内瑞拉将在中国帮助下重启关键电厂',
    '彭博社24日报道，一家中国工程企业即将部分重启委内瑞拉一座大型电厂，该电厂长期停运已加剧当地电力短缺。报道称，这一合作是中国在拉美基础设施领域持续存在的又一例证，也发生在美方加大对委施压、推动其政治过渡的背景下。项目进展与资金安排细节尚未完全公开。',
    '彭博社', '中欧与盟友', '委内瑞拉;电力;中企;拉美基础设施', 76, '2026-10-24',
    'https://www.bloomberg.com/news/articles/2026-10-24/venezuela-to-restart-a-crucial-power-plant-with-china-s-help')

add('SoftBank Son Plans $50 Billion Malaysia Tech Outlay, PM Says',
    '孙正义计划在马来西亚投资500亿美元科技项目',
    '彭博社25日报道，马来西亚总理称，软银集团创始人孙正义选定马来西亚多地作为500亿美元科技投资的目的地。报道称，投资将覆盖数据中心、人工智能基础设施等领域，是马来西亚打造区域数字枢纽战略的重要支撑。该项目规模在东南亚科技投资中位居前列，也反映全球算力基础设施向东南亚扩散的趋势。',
    '彭博社', 'AI·科技', '软银;马来西亚;数据中心;AI基础设施', 82, '2026-10-25',
    'https://www.bloomberg.com/news/articles/2026-10-25/softbank-s-son-plans-50-billion-malaysia-tech-outlay-pm-says')

add('Trump Defends Tariffs at Rally as He Touts New US Audi Plant',
    '特朗普集会上为关税辩护并宣扬奥迪在美建厂',
    '彭博社25日报道，美国总统特朗普在佐治亚州竞选集会上为关税政策辩护，称关税让美国更富有，并宣布大众汽车将在该州新建奥迪工厂，投资42亿美元。报道称，特朗普把制造业回流作为中期选举的核心叙事，而关税成本转嫁与盟友反制仍是争议焦点。集会发生在选举前两周的关键时点。',
    '彭博社', '美国内政', '特朗普;关税;奥迪;中期选举', 74, '2026-10-25',
    'https://www.bloomberg.com/news/articles/2026-10-25/trump-defends-tariffs-at-rally-as-he-says-audi-to-build-us-plant')

add('Fed Set to Lead G7 Trio in Hawkish Rate Pause: Eco Week Ahead',
    '美联储料领衔 G7 鹰派式按兵不动',
    '彭博社24日刊发"一周经济前瞻"，预计美联储与欧元区、日本央行将在下周议息会议上一同维持利率不变，形成 G7 "鹰派式暂停"格局。报道称，通胀回落缓慢与就业韧性使决策者倾向延长观望期，市场对年内降息的定价已明显收敛。这一组合将影响全球资本流动与新兴市场汇率，对人民币与亚洲资产亦有传导。',
    '彭博社', '其他', '美联储;G7;利率;货币政策', 78, '2026-10-24',
    'https://www.bloomberg.com/news/articles/2026-10-24/fed-set-to-lead-g7-trio-in-hawkish-rate-pause-eco-week-ahead')

# ================= 半岛电视台 =================
add('Saudi Arabia intercepts missiles and drones as fighting with Houthis rages',
    '沙特拦截导弹与无人机 与胡塞交火持续',
    '半岛电视台25日报道，沙特阿拉伯拦截多枚导弹与无人机，与也门胡塞武装的交火持续升级。报道称，胡塞方面此前再次警告各方勿使用利雅得机场，沙特民防部门一度在麦加、吉达与塔伊夫发布警报后宣布危险已过。地区紧张升级推动海湾股市下挫，投资者对航运与能源通道风险的担忧上升。',
    '半岛电视台', '地区局势', '沙特;胡塞武装;导弹拦截;红海', 84, '2026-10-25',
    'https://www.aljazeera.com/news/2026/10/25/saudi-arabia-intercepts-missiles-and-drones-as-fighting-with-houthis-rages')

add("Iran's authorities take self-sacrifice mobilisation campaign nationwide",
    '伊朗当局将"自我牺牲"动员活动推向全国',
    '半岛电视台25日报道，伊朗伊斯兰革命卫队表示，将在全国31个省份首府的主要广场开展"Janfada"（自我牺牲）动员活动，将其推向全国范围。报道称，此举发生在伊朗与美以紧张持续升级、国内对临时协议失败不满上升的背景下，被视为当局强化社会动员与凝聚力的一部分。',
    '半岛电视台', '地区局势', '伊朗;革命卫队;社会动员;美伊紧张', 76, '2026-10-25',
    'https://www.aljazeera.com/news/2026/10/25/irans-authorities-take-self-sacrifice-mobilisation-campaign-nationwide')

# ================= BBC =================
add('Musk says SpaceX restricted Ukraine Starlink connection as service restored',
    '马斯克承认 SpaceX 曾限制乌克兰星链连接',
    'BBC 25日报道，马斯克表示 SpaceX 曾限制乌克兰的"星链"连接，目前服务已恢复。此前乌方称卫星接入仍受限，与特朗普宣称已恢复的说法不符。此事引发对商业卫星服务在冲突中可用性的广泛讨论，台湾方面亦据此检讨对单一外国卫星服务商的依赖风险。',
    'BBC', '地区局势', '星链;马斯克;乌克兰;卫星通信', 84, '2026-10-25',
    'https://www.bbc.co.uk/news/articles/cvx28ljp8n4xo')

# ================= 纽约时报 =================
add('Kim Jong-un Makes First Visit to China in Over a Year',
    '金正恩一年多来首次访华',
    '《纽约时报》24日报道，朝鲜最高领导人金正恩对华进行一年多来首次访问，经新开通的朝中边境大桥进入中国。报道称，此访凸显朝中关系回暖，双方在贸易与安全领域的互动增加。访问时间安排在朝鲜下月重要政治日程之前，外界关注其对东北亚格局与朝美接触前景的影响。',
    '纽约时报', '地区局势', '金正恩;中朝关系;东北亚;边境', 88, '2026-10-24',
    'https://www.nytimes.com/2026/10/24/world/asia/north-korea-kim-jong-un-china.html')

# ================= 卫报 =================
add('Kim Jong-un crosses newly opened bridge into China',
    '金正恩经新开通大桥进入中国',
    '英国《卫报》24日报道，朝鲜最高领导人金正恩经新开通的朝中边境大桥进入中国，为一年多来首次访华。报道称，双方强调传统友谊并呼吁扩大合作，边贸往来同步恢复。此访发生在朝鲜下月重要会议之前，被视为平壤在对外关系上寻求更多经济与安全支撑的信号。',
    '卫报', '地区局势', '金正恩;中朝边境;大桥;东北亚', 84, '2026-10-24',
    'https://www.theguardian.com/world/2026/oct/24/kim-jong-un-crosses-newly-opened-bridge-into-china')

# ================= Politico =================
add('Beijing locks in Laos',
    'Politico：北京正在锁定老挝',
    'Politico 旗下"国家安全日报"23日刊文称，特朗普政府正在"失去老挝"，而这一问题在下月特朗普赴马尼拉出席东盟峰会前更显突出。文章称中国上月启用了在老挝的空军基地，为其在东南亚的第二个军事基地，同时美方因波斯湾冲突将兵力移出亚洲。多名前美方官员与亚洲外交官表示，美国自奥巴马政府后期起逐步从老挝收缩，特朗普第二任期进一步削减接触（包括列入旅行禁令名单、终止 USAID 相关项目、自1月起无驻老挝大使），这"为北京创造了机会"。一名泰国前外长称"老挝已成为中国的附庸国"；五角大楼前中国事务主管称"美国已把老挝和柬埔寨输给了中国"。',
    'Politico', '地区局势', '老挝;中国军事基地;东盟峰会;美国收缩', 90, '2026-10-23',
    'https://www.politico.com/newsletters/national-security-daily/2026/10/23/beijing-locks-in-laos-01134092')

add('Proposed rules target US-China biotech ties',
    'Politico：拟议规则瞄准中美生物技术投资',
    'Politico "处方脉动"栏目23日详述美国财政部22日提出的对华生物技术投资限制规则。若最终落地，将是美国首次对制药行业的外资限制：禁止涉及"特定生物衍生化合物或材料"、生物制造设备与设施、生物设计与测序相关技术的交易，同时禁止投资"自动化科学发现或实验"软件设备，脑机接口与生物信息学工具亦纳入。报道指出，该提案出台前制药业进行了数月游说反对，辉瑞、百时美施贵宝、罗氏今年均与中国药企达成数十亿美元授权交易；财政部官员称规则不涉及授权许可交易，但未澄清共同开发与共同商业化协议是否适用。规则须在明年3月前定稿。',
    'Politico', '中美博弈', '生物技术;对外投资限制;财政部;医药授权', 88, '2026-10-23',
    'https://www.politico.com/newsletters/prescription-pulse/2026/10/23/proposed-rules-target-us-china-biotech-ties-01132547')

add('Inside the cyber flaw scramble that brought the AI threat to life',
    'Politico：AI 网络威胁从假设变为现实',
    'Politico 欧洲版刊文，梳理近期一轮软件漏洞应急响应如何让"AI 加速网络攻击"的威胁从理论走向现实。报道称，安全团队在短时间内遭遇由自动化工具辅助发现与利用的漏洞集中披露，响应节奏与人力配置均受到冲击。文章指出，具备代码编写与工具操作能力的模型可显著降低攻击成本，各国政府正加快评估监管路径，而开源权重的扩散使事后管控更加困难。',
    'Politico', 'AI·科技', 'AI网络攻击;漏洞披露;开源模型;安全监管', 80, '2026-10-24',
    'https://www.politico.eu/article/the-cyber-flaw-scramble-that-brought-the-ai-threat-to-life/')

# ================= 美联社 =================
add("Musk says he was behind Starlink speed restriction after service in Ukraine is restored",
    '马斯克称限制乌克兰星链速度系其决定',
    '美联社25日报道，马斯克表示在乌克兰"星链"服务恢复后，此前的速度限制是其本人作出的决定。报道称，乌方一度称卫星接入仍受限，与美方宣称已恢复的说法存在出入。该事件再度引发对商业卫星通信在冲突情境下可靠性的讨论，多国正评估对单一供应商的依赖风险。',
    '美联社', '地区局势', '星链;马斯克;乌克兰;通信安全', 82, '2026-10-25',
    'https://apnews.com/article/russia-ukraine-war-starlink-drones-a3a0139dfc23365550306dd66fe43daa')

# ================= 输出 =================
if bad:
    print('!! ILLEGAL URLS:')
    for t, u in bad:
        print('  ', t, '|', u)

POOL = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/news-webfetch.json'
pool = json.load(open(POOL, encoding='utf-8'))
exist = {norm(i.get('url')) for i in pool}
new = []
for it in items:
    if norm(it['url']) in exist:
        continue
    exist.add(norm(it['url']))
    new.append(it)

pool.extend(new)
json.dump(pool, open(POOL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'built {len(items)} | new {len(new)} | pool {len(pool)}')
assert not bad, f'{len(bad)} illegal urls'
