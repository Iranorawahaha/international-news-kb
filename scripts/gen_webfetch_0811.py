#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-11 构建 news-webfetch.json：保留昨日 48h 窗口有效条目 + 今日新增采集"""
import json, html, re

BASE = 'data/news-webfetch.json'

def has_zh(s):
    return any('\u4e00' <= c <= '\u9fff' for c in (s or ''))

def clean(s):
    if not s: return ''
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# ============ 读取昨日数据，保留 8-09 及以后 ============
with open(BASE) as f:
    old_items = json.load(f)
kept = [it for it in old_items if (it.get('date') or '') >= '2026-08-09']
print(f"昨日 {len(old_items)} 条 → 保留 48h 窗口内 {len(kept)} 条")

# ============ 今日新增条目 ============
NEW_ITEMS = [
# ---------------- 路透社 (8-10/8-11) ----------------
{"title_en":"Trump flew secretly from Turkey due to Iranian threat","title_zh":"特朗普因伊朗威胁曾秘密从土耳其乘军机返美","summary":"《华盛顿邮报》报道，受伊朗威胁影响，特朗普总统上月曾从土耳其秘密乘坐军用航班返美，而当时白宫对外宣称其乘坐的是空军一号。该消息引发对其安全态势与信息公开的讨论。","source":"路透社","category":"地缘政治","keywords":"特朗普,伊朗,秘密航班,威胁,白宫","url":"https://www.reuters.com/business/aerospace-defense/trump-flew-secretly-turkey-due-iranian-threat-washington-post-reports-2026-08-11/","priority_score":90,"is_summit_level":True,"column":"美国","date":"2026-08-11"},
{"title_en":"Hopes for Hormuz deal fade as Trump demands Iranian reparations","title_zh":"特朗普要求伊朗赔偿，霍尔木兹协议希望渐淡","summary":"特朗普总统要求伊朗就美军伤亡作出赔偿，使重开霍尔木兹海峡的谈判前景趋于黯淡。此前伊朗提出包括撤军、解冻资产等多项强硬条件，美伊谈判陷入僵局。","source":"路透社","category":"地缘政治","keywords":"伊朗,霍尔木兹,特朗普,赔偿,谈判","url":"https://www.reuters.com/world/middle-east/iran-ties-hormuz-reopening-us-concessions-several-demands-2026-08-09/","priority_score":88,"is_summit_level":True,"column":"地区热点","date":"2026-08-11"},
{"title_en":"More than 100 killed after strongest quake this century hits western Colombia","title_zh":"哥伦比亚西部遭遇本世纪最强地震，逾100人遇难","summary":"哥伦比亚西部发生7.4级强震，系该国本世纪最强地震，已造成逾100人死亡，多栋建筑坍塌，救援工作正在进行。","source":"路透社","category":"国际","keywords":"哥伦比亚,地震,7.4级,灾害,救援","url":"https://www.reuters.com/world/earthquake-pacific-coast-shakes-colombian-capital-2026-08-10/","priority_score":70,"is_summit_level":False,"column":"地区热点","date":"2026-08-10"},
{"title_en":"Poland and Baltics shield infrastructure, fearing a Russian false-flag strike","title_zh":"波兰与波罗的海国家防范俄罗斯\"假旗\"袭击，加固基础设施","summary":"波兰和波罗的海国家正在加固关键基础设施，防范俄罗斯可能的\"假旗\"袭击。此前莱比锡机场爆炸案被美方情报指向俄罗斯，地区安全担忧升温。","source":"路透社","category":"地缘政治","keywords":"波兰,波罗的海,俄罗斯,假旗袭击,基础设施","url":"https://www.reuters.com/world/europe/poland-baltics-shield-infrastructure-fearing-russian-false-flag-strike-2026-08-10/","priority_score":78,"is_summit_level":False,"column":"欧洲","date":"2026-08-10"},
{"title_en":"Oman says grounded tanker oil spill covers 400 square km","title_zh":"阿曼称搁浅油轮泄漏已覆盖400平方公里","summary":"阿曼表示，一艘因受对俄制裁拖累的油轮搁浅后发生泄漏，浮油面积已达约400平方公里。该油轮据信属于俄罗斯\"影子船队\"。","source":"路透社","category":"国际","keywords":"阿曼,油轮,漏油,俄罗斯,影子船队","url":"https://www.reuters.com/business/energy/oil-spill-off-oman-tanker-under-sanctions-against-russia-spreads-over-huge-area-2026-08-10/","priority_score":72,"is_summit_level":False,"column":"地区热点","date":"2026-08-10"},
{"title_en":"US judge dismisses criminal case against Indian billionaire Adani","title_zh":"美国法官驳回对印度亿万富翁阿达尼的刑事起诉","summary":"美国一名法官驳回对印度亿万富翁高塔姆·阿达尼的刑事起诉。该案涉及美国检察官指控的欺诈与行贿计划，此次驳回标志其法律胜利。","source":"路透社","category":"国际","keywords":"美国,印度,阿达尼,司法,起诉","url":"https://www.reuters.com/legal/government/us-judge-dismisses-criminal-case-against-indian-billionaire-adani-2026-08-10/","priority_score":65,"is_summit_level":False,"column":"美国","date":"2026-08-10"},
{"title_en":"Turkish parliament passes landmark law to advance PKK peace process","title_zh":"土耳其议会通过里程碑式法案推进库尔德工人党和解进程","summary":"土耳其议会通过一项具有里程碑意义的法案，为数千名库尔德工人党（PKK）成员提供类似赦免的安排，以推进与库尔德武装的和解进程。","source":"路透社","category":"国际","keywords":"土耳其,库尔德工人党,和平进程,议会,法案","url":"https://www.reuters.com/world/middle-east/turkish-parliament-passes-landmark-law-advance-pkk-peace-process-2026-08-10/","priority_score":72,"is_summit_level":False,"column":"欧洲","date":"2026-08-10"},

# ---------------- BBC ----------------
{"title_en":"Nvidia gets $500bn from major investors to develop AI infrastructure","title_zh":"英伟达获5000亿美元投资者资金用于AI基础设施建设","summary":"英伟达从多家大型投资机构获得5000亿美元资金，用于开发AI基础设施。这是AI算力竞赛中规模最大的融资之一，凸显全球AI基建投资热潮。","source":"BBC","category":"科技","keywords":"英伟达,AI,基础设施,融资,芯片","url":"https://www.bbc.com/news/articles/c78gr0jv0mdo","priority_score":92,"is_summit_level":False,"column":"科技竞争","date":"2026-08-10"},
{"title_en":"Trump signs order to limit childhood vaccines and split MMR shots","title_zh":"特朗普签署行政令限制儿童疫苗并拆分麻腮风疫苗","summary":"特朗普总统签署行政令，对儿童疫苗建议作出调整并拆分MMR联合疫苗，美国儿科学会称该建议\"危险\"，医学界普遍反对，认为其违背科学共识。","source":"BBC","category":"美国","keywords":"特朗普,疫苗,行政令,儿童,医疗","url":"https://www.bbc.com/news/articles/ce3q5vl581wo","priority_score":85,"is_summit_level":True,"column":"美国","date":"2026-08-10"},
{"title_en":"No evidence of data breach after Chinese-made component found in Navy drones, MoD says","title_zh":"英国防部：海军无人机发现中国产部件但无数据泄露证据","summary":"英国国防部表示，在海军无人机中发现中国制造的部件，但未发现数据泄露的证据。此事凸显西方军方供应链对华依赖引发的安全关切。","source":"BBC","category":"科技","keywords":"英国,无人机,中国,供应链,安全","url":"https://www.bbc.com/news/articles/c4gwl3n7ne7o","priority_score":80,"is_summit_level":False,"column":"科技竞争","date":"2026-08-10"},
{"title_en":"At least 111 killed in Colombia's largest earthquake in years","title_zh":"哥伦比亚多年来最强地震致至少111人遇难","summary":"哥伦比亚西部乔科省附近发生7.4级地震，至少111人遇难、数十人受伤，震感波及数百公里外的城市，救援工作持续进行。","source":"BBC","category":"国际","keywords":"哥伦比亚,地震,灾害,遇难,救援","url":"https://www.bbc.com/news/articles/c20e360lx0vo","priority_score":70,"is_summit_level":False,"column":"地区热点","date":"2026-08-10"},
{"title_en":"Tech leaders say AI means less work - their staff say they work up to 90 hours a week","title_zh":"科技领袖称AI将减少工作量，但员工称每周工作90小时","summary":"科技公司高管宣称AI将让人们工作更少，但其员工披露实际每周工作高达90小时。报道质疑科技行业自身并未践行其AI减少工作量的主张。","source":"BBC","category":"科技","keywords":"AI,科技公司,工作时长,员工,硅谷","url":"https://www.bbc.com/news/articles/cvgx4yd1gl2o","priority_score":75,"is_summit_level":False,"column":"科技竞争","date":"2026-08-10"},
{"title_en":"China evacuates one million from homes as massive storm arrives","title_zh":"强台风来袭，中国紧急转移百万人","summary":"强台风\"海豚\"登陆中国东部沿海，约100万人被紧急转移避险，多地航班取消、学校停课，这是今年影响中国的最强台风。","source":"BBC","category":"国际","keywords":"中国,台风,海豚,转移,灾害","url":"https://www.bbc.com/news/articles/cx2rgzyplg2o","priority_score":72,"is_summit_level":False,"column":"中国","date":"2026-08-10"},

# ---------------- 南华早报 ----------------
{"title_en":"China moves to join Brazil's WTO fight over Trump's forced labour tariffs","title_zh":"中国加入巴西在WTO挑战特朗普\"强迫劳动\"关税的诉讼","summary":"中国宣布加入巴西在世界贸易组织（WTO）就特朗普政府\"强迫劳动\"关税提起的诉讼，此举是中国利用多边机制反制美国关税措施的最新动作。","source":"南华早报","category":"经贸","keywords":"中国,巴西,WTO,关税,强迫劳动","url":"https://www.scmp.com/news/us/article/3363585/china-moves-join-brazils-wto-fight-over-trumps-forced-labour-tariffs","priority_score":92,"is_summit_level":False,"column":"经贸制裁","date":"2026-08-10"},
{"title_en":"Chinese national pleads guilty to trying to export US military gear to China","title_zh":"中国公民承认试图向中国出口美国军用装备","summary":"一名中国公民在美国认罪，承认试图向中国出口美国军用装备。该案反映美国对华技术出口管制的执行力度，也凸显涉军技术转移的敏感监管。","source":"南华早报","category":"科技","keywords":"中国,出口管制,军用装备,美国,认罪","url":"https://www.scmp.com/news/china/diplomacy/article/3363584/chinese-national-pleads-guilty-trying-export-us-military-equipment-china","priority_score":85,"is_summit_level":False,"column":"科技竞争","date":"2026-08-10"},
{"title_en":"China's Long March 7A rocket explodes after launch, satellite lost","title_zh":"长征七号甲运载火箭发射后爆炸，卫星损毁","summary":"中国长征七号甲运载火箭发射后发生爆炸，所载中星4B通信卫星损毁。这是新一代火箭罕见失败，结束其一段连续成功发射纪录。","source":"南华早报","category":"科技","keywords":"中国,长征七号,火箭,卫星,航天","url":"https://www.scmp.com/news/china/military/article/3363574/chinas-long-march-7a-rocket-explodes-after-launch-satellite-lost","priority_score":82,"is_summit_level":False,"column":"科技竞争","date":"2026-08-11"},
{"title_en":"US visa revocations hit 175,000, on pace for new record under Trump","title_zh":"美国吊销签证达17.5万份，特朗普治下或创纪录","summary":"美国国务院表示，2026年被吊销签证总数将超过去年创下的纪录，特朗普总统正持续推进其移民打击政策，签证吊销数量持续攀升。","source":"南华早报","category":"美国","keywords":"美国,签证,移民,特朗普,国务院","url":"https://www.scmp.com/news/us/politics/article/3363583/us-visa-revocations-hit-175000-pace-new-record-under-trump","priority_score":85,"is_summit_level":False,"column":"美国","date":"2026-08-10"},
{"title_en":"Powerful anti-drone laser spotted on PLA amphibious ship in South China Sea","title_zh":"解放军南海两栖舰现强力反无人机激光","summary":"分析人士称，解放军在南沙黄岩岛演习期间，在一艘两栖舰上部署LY-1反无人机激光装备，意在向马尼拉和华盛顿传递信号。","source":"南华早报","category":"军事","keywords":"解放军,南海,激光,反无人机,黄岩岛","url":"https://www.scmp.com/news/china/military/article/3363564/powerful-anti-drone-laser-spotted-pla-amphibious-ship-south-china-sea","priority_score":88,"is_summit_level":False,"column":"中国","date":"2026-08-10"},
{"title_en":"Why India's new Himalayan border map threatens a fragile thaw in China ties","title_zh":"印度新版喜马拉雅边界地图威胁中印关系脆弱解冻","summary":"印度公布阿鲁纳恰尔邦（藏南地区）新地名清单，涉及与中国的争议边界敏感地点，可能威胁中印两国关系近期出现的脆弱缓和态势。","source":"南华早报","category":"地缘政治","keywords":"印度,中国,边界,喜马拉雅,藏南","url":"https://www.scmp.com/news/china/diplomacy/article/3363541/why-indias-new-himalayan-border-map-threatens-fragile-thaw-china-ties","priority_score":85,"is_summit_level":False,"column":"中国","date":"2026-08-10"},
{"title_en":"China's 'little Nvidia' plans Hong Kong listing after 147% revenue jump","title_zh":"中国\"小英伟达\"摩尔线程营收增147%后计划赴港上市","summary":"被称为中国\"小英伟达\"的GPU公司摩尔线程在营收大幅增长后计划赴香港上市，此举被视为中国AI芯片企业寻求更多融资、应对外部限制的重要动向。","source":"南华早报","category":"科技","keywords":"摩尔线程,GPU,港交所,AI芯片,上市","url":"https://www.scmp.com/tech/tech-trends/article/3363448/moore-threads-plans-hong-kong-listing-after-posting-147-jump-first-half-revenue","priority_score":88,"is_summit_level":False,"column":"科技竞争","date":"2026-08-09"},
{"title_en":"Enterprise AI costs hit yearly low driven by price wars, open-source models","title_zh":"价格战与开源模型推动企业AI成本创年内新低","summary":"研究显示，受中国开源模型竞争与价格战影响，企业使用AI的成本降至年内低点，反映全球大模型市场降价潮持续，开源模型对企业AI落地形成有力推动。","source":"南华早报","category":"科技","keywords":"AI,企业,成本,开源模型,价格战","url":"https://www.scmp.com/tech/tech-trends/article/3363549/enterprise-ai-costs-hit-2026-low-driven-price-wars-chinese-open-source-models-research","priority_score":85,"is_summit_level":False,"column":"科技竞争","date":"2026-08-10"},

# ---------------- 卫报 ----------------
{"title_en":"Trump demands Iran pay compensation for decades of US soldier deaths","title_zh":"特朗普要求伊朗为数十年来美军士兵伤亡赔偿","summary":"特朗普总统发表声明，要求伊朗为数十年来美军士兵死亡进行赔偿。此举被视作美伊战争与霍尔木兹海峡重开谈判陷入僵局的最新信号。","source":"卫报","category":"地缘政治","keywords":"特朗普,伊朗,赔偿,霍尔木兹,谈判","url":"https://www.theguardian.com/world/2026/aug/10/trump-demands-iran-pay-compensation-for-decades-of-us-soldier-deaths","priority_score":90,"is_summit_level":True,"column":"美国","date":"2026-08-10"},
{"title_en":"Chinese EV sales surge to new high in Europe putting tariffs under scrutiny","title_zh":"中国电动汽车欧洲销量创新高，关税政策面临审视","summary":"中国电动汽车在欧洲销量创下历史新高，使欧盟对华电动车关税政策再度受到审视，贸易紧张与市场需求之间的张力凸显。","source":"卫报","category":"经贸","keywords":"中国,电动车,欧洲,关税,贸易","url":"https://www.theguardian.com/business/2026/aug/09/chinese-electric-car-sales-surge-to-a-record-high-in-europe","priority_score":88,"is_summit_level":False,"column":"经贸制裁","date":"2026-08-09"},
{"title_en":"Ukraine drone strike on oil refinery deep inside Russia kills at least 13","title_zh":"乌克兰无人机袭击俄腹地炼油厂致至少13死","summary":"乌克兰对俄罗斯境内深处的一座炼油厂发动无人机袭击，造成至少13人死亡，是俄乌冲突中最致命的此类打击之一，基辅试图以此扼制俄罗斯经济。","source":"卫报","category":"地缘政治","keywords":"乌克兰,俄罗斯,无人机,炼油厂,袭击","url":"https://www.theguardian.com/world/2026/aug/10/ukraine-drone-strike-on-oil-refinery-russia","priority_score":78,"is_summit_level":False,"column":"欧洲","date":"2026-08-10"},
{"title_en":"US intelligence 'believes Russia was behind Leipzig airport drone bomb'","title_zh":"美情报机构认为莱比锡机场无人机炸弹事件系俄罗斯所为","summary":"美国情报机构认为，德国莱比锡机场的无人机炸弹袭击未遂事件背后有俄罗斯的指使。该机场是北约关键货运枢纽，事件暴露了后方反无人机防御的漏洞。","source":"卫报","category":"地缘政治","keywords":"美国,俄罗斯,莱比锡,无人机,北约","url":"https://www.theguardian.com/world/2026/aug/10/us-intelligence-russia-leipzig-airport-drone-bomb","priority_score":80,"is_summit_level":False,"column":"欧洲","date":"2026-08-10"},
{"title_en":"Typhoon Dolphin: more than a million people evacuated in China as record rainfall dumped on Shanghai","title_zh":"台风\"海豚\"：中国逾百万人撤离，上海遭遇创纪录降雨","summary":"台风\"海豚\"袭击中国，超过100万人被疏散，上海遭遇创纪录降雨并出现严重内涝，多趟航班取消，灾害影响仍在扩大。","source":"卫报","category":"国际","keywords":"中国,台风,海豚,上海,撤离","url":"https://www.theguardian.com/world/2026/aug/10/typhoon-dolphin-china-shanghai-flooding-evacuations","priority_score":72,"is_summit_level":False,"column":"中国","date":"2026-08-10"},

# ---------------- CNN ----------------
{"title_en":"Iran shakes up military leadership as Strait of Hormuz talks seem to stall","title_zh":"霍尔木兹谈判停滞，伊朗改组军事领导层","summary":"伊朗在美伊紧张局势升级背景下改组军事领导层，同时围绕霍尔木兹海峡的谈判似乎陷入停滞，加剧地区地缘政治不确定性。","source":"CNN","category":"地缘政治","keywords":"伊朗,军事领导层,霍尔木兹,谈判,美伊","url":"https://edition.cnn.com/2026/08/10/world/live-news/iran-war-trump","priority_score":88,"is_summit_level":False,"column":"地区热点","date":"2026-08-10"},
{"title_en":"Trump's Iran strategy depends on economic pain. The pain is mounting","title_zh":"特朗普对伊战略依赖经济施压，压力正不断累积","summary":"报道分析特朗普政府通过制裁等经济手段向伊朗施压的战略，指出经济痛苦正在累积，但该战略的实际成效仍存疑问，美伊对抗持续。","source":"CNN","category":"地缘政治","keywords":"特朗普,伊朗,制裁,经济,战略","url":"https://edition.cnn.com/2026/08/10/middleeast/trump-iran-economic-pain-intl","priority_score":85,"is_summit_level":True,"column":"美国","date":"2026-08-10"},
{"title_en":"Meta just picked a side in a big debate over the future of AI","title_zh":"Meta在AI未来重大辩论中表明立场","summary":"Meta在AI开放与封闭模型之争中作出关键选择，扎克伯格警告AI权力集中风险。这一立场将影响全球AI竞争格局与监管走向。","source":"CNN","category":"科技","keywords":"Meta,AI,扎克伯格,开源,监管","url":"https://edition.cnn.com/2026/08/10/tech/meta-glimmer-mark-zuckerberg-future-of-ai","priority_score":85,"is_summit_level":False,"column":"科技竞争","date":"2026-08-10"},
{"title_en":"Israel rejects Trump's Gaza peace plan, saying no withdrawal until Hamas disarms","title_zh":"以色列拒绝特朗普加沙和平计划，称哈马斯解除武装前不撤军","summary":"以色列政府拒绝特朗普提出的加沙和平计划，明确表示在哈马斯解除武装之前不会撤军，凸显美国斡旋努力面临的重大障碍与美以分歧。","source":"CNN","category":"地缘政治","keywords":"以色列,加沙,特朗普,哈马斯,和平计划","url":"https://edition.cnn.com/2026/08/09/middleeast/israel-gaza-trump-netanyahu-plan-intl","priority_score":85,"is_summit_level":True,"column":"地区热点","date":"2026-08-09"},
{"title_en":"Netanyahu calculates upsetting Trump is his least-bad option","title_zh":"内塔尼亚胡权衡后认为得罪特朗普是最不坏的选择","summary":"分析文章指出，内塔尼亚胡在特朗普加沙和平计划上权衡政治与战略选项后，判定拒绝美方方案是其\"最不坏\"的选择，尽管这可能损害美以关系。","source":"CNN","category":"地缘政治","keywords":"内塔尼亚胡,特朗普,加沙,美以关系,战略","url":"https://edition.cnn.com/2026/08/09/middleeast/netanyahu-decision-trump-gaza-plan-analysis-latam-intl","priority_score":80,"is_summit_level":False,"column":"地区热点","date":"2026-08-09"},
{"title_en":"The US Navy's plan for almost 20 guided-missile subs and why that will matter around China","title_zh":"美海军拟建近20艘导弹潜艇，对中国周边格局意义重大","summary":"报道分析美国海军建造近20艘导弹潜艇的计划及其对印太地区、尤其中国周边军事平衡的深远影响，涉及中美军事竞争的重要议题。","source":"CNN","category":"军事","keywords":"美国海军,潜艇,中国,印太,军事","url":"https://edition.cnn.com/2026/08/08/world/us-navy-guided-missile-submarines-china-intl-hnk-ml","priority_score":85,"is_summit_level":False,"column":"美国","date":"2026-08-08"},

# ---------------- 纽约时报 ----------------
{"title_en":"Taiwan Gingerly Tests How It Would Cope if China Choked Its Internet","title_zh":"台湾首次演练网络管制：若大陆切断互联网如何应对","summary":"台湾举行首次移动网络管制演练，模拟中国大陆网络攻击或入侵情境下民众通讯中断30分钟，以测试民众应对能力，此举引发关于战备与言论自由的讨论。","source":"纽约时报","category":"地缘政治","keywords":"台湾,网络,演练,中国大陆,通讯","url":"https://www.nytimes.com/2026/08/10/world/asia/taiwan-internet-china-invasion-drill.html","priority_score":85,"is_summit_level":False,"column":"中国","date":"2026-08-10"},
{"title_en":"The Places Where the Bombs Have Rarely Stopped Falling in Iran","title_zh":"伊朗南部格什姆岛等地遭美军持续空袭","summary":"报道称，尽管伊朗大部分地区战事缓和，但美国在格什姆岛等南部地区的空袭几乎未停，当地民众生活与生计遭受重创。","source":"纽约时报","category":"地缘政治","keywords":"伊朗,美军,空袭,格什姆岛,战争","url":"https://www.nytimes.com/2026/08/10/world/middleeast/iran-south-bombing-strait-hormuz.html","priority_score":85,"is_summit_level":False,"column":"地区热点","date":"2026-08-10"},
{"title_en":"Ukrainian Drone Attack Deep Into Russia Is Among Its Deadliest of the War","title_zh":"乌克兰深入俄境无人机袭击系开战以来最致命之一","summary":"乌克兰对俄鞑靼斯坦工业中心发动无人机袭击，造成至少13人死亡，是俄乌冲突中最致命的深入俄境打击之一。","source":"纽约时报","category":"地缘政治","keywords":"乌克兰,俄罗斯,无人机,袭击,鞑靼斯坦","url":"https://www.nytimes.com/2026/08/10/world/europe/ukraine-drone-attack-russia.html","priority_score":78,"is_summit_level":False,"column":"欧洲","date":"2026-08-10"},
{"title_en":"Netanyahu Walks 'Political Tightrope' on Trump's Gaza Disarmament Deal","title_zh":"内塔尼亚胡在特朗普加沙解除武装协议上走\"政治钢丝\"","summary":"以色列总理内塔尼亚胡面临即将到来的大选压力，试图在右翼基本盘与特朗普总统的加沙协议之间取得平衡，其立场反复引发关注。","source":"纽约时报","category":"地缘政治","keywords":"内塔尼亚胡,加沙,特朗普,大选,以色列","url":"https://www.nytimes.com/2026/08/10/world/middleeast/netanyahu-trump-israel-gaza-disarmament.html","priority_score":80,"is_summit_level":False,"column":"地区热点","date":"2026-08-10"},
{"title_en":"Iran Insists Strait Will Stay Closed Until U.S. Agrees to Demands","title_zh":"伊朗坚持美国同意其要求前霍尔木兹海峡保持关闭","summary":"伊朗外交部发言人表示，与阿曼关于海峡航运的谈判与全面重开水道的讨论是\"分开的\"，强调在美国满足其条件前海峡将继续关闭。","source":"纽约时报","category":"地缘政治","keywords":"伊朗,霍尔木兹,美国,阿曼,谈判","url":"https://www.nytimes.com/2026/08/10/world/middleeast/iran-strait-of-hormuz-us-oman-talks.html","priority_score":88,"is_summit_level":False,"column":"地区热点","date":"2026-08-10"},
{"title_en":"Iran's Old Guard May Be Entrenching Power With Promotion of Commander","title_zh":"伊朗提升革命卫队指挥官，或显示旧势力巩固权力","summary":"伊朗任命资深军事指挥官穆赫辛·雷扎伊出任重要安全职位，表明伊朗体制内旧势力正巩固权力，为下一阶段美伊博弈埋下变量。","source":"纽约时报","category":"地缘政治","keywords":"伊朗,革命卫队,权力,安全,雷扎伊","url":"https://www.nytimes.com/2026/08/09/world/middleeast/iran-security-council-guards-commander.html","priority_score":80,"is_summit_level":False,"column":"地区热点","date":"2026-08-09"},

# ---------------- 华尔街日报 (真实URL确认) ----------------
{"title_en":"Apple Tests Memory Chips From China's CXMT to Ease AI-Driven Supply Crunch","title_zh":"苹果测试中国长鑫存储芯片以缓解AI驱动的供应紧张","summary":"据《华尔街日报》报道，苹果已在iPhone和MacBook等多条产品线测试中国长鑫存储（CXMT）的DRAM芯片，并就供应进行初步洽谈，希望获得白宫批准用于中国市场设备。美国出口管制限制苹果定制芯片，但可采购标准品；长鑫今年产能已满负荷，优先供给字节跳动、腾讯、小米等国内客户。","source":"华尔街日报","category":"科技","keywords":"苹果,长鑫存储,CXMT,DRAM,AI,芯片,出口管制","url":"https://finwire.io/news/stock-markets-news/apple-tests-memory-chips-from-chinas-cxmt-to-ease-ai-driven-supply-crunch-wsj","priority_score":95,"is_summit_level":False,"column":"科技竞争","date":"2026-08-10"},
{"title_en":"Trump Thought Opening the Strait of Hormuz Was Imminent. Iran Had Other Plans.","title_zh":"特朗普曾认为霍尔木兹海峡开放近在眼前，伊朗另有打算","summary":"《华尔街日报》披露，数周来特朗普政府一直在为伊朗全面重开霍尔木兹海峡即宣布胜利做准备，甚至愿意在无核协议下收场；但伊朗坚持开战以来最高条件，要求美方赔偿、撤军并解除海上封锁。","source":"华尔街日报","category":"地缘政治","keywords":"特朗普,伊朗,霍尔木兹,核协议,谈判","url":"https://www.wsj.com/world/middle-east/trump-strait-of-hormuz-opening-iran-negotiations-b6a43ad6","priority_score":90,"is_summit_level":True,"column":"美国","date":"2026-08-10"},

# ---------------- 半岛电视台 ----------------
{"title_en":"Trump claims Strait of Hormuz is open, will seek compensation from Tehran","title_zh":"特朗普宣称霍尔木兹海峡已开放，将向德黑兰索赔","summary":"特朗普总统在实时更新中宣称霍尔木兹海峡已开放，并表示将就战争伤亡向伊朗寻求赔偿，但伊朗方面坚持海峡在美方满足条件前不会重开。","source":"半岛电视台","category":"地缘政治","keywords":"特朗普,伊朗,霍尔木兹,赔偿,停火","url":"https://www.aljazeera.com/news/liveblog/2026/8/11/iran-war-live-trump-claims-the-strait-is-open-seeks-iranian-compensation","priority_score":90,"is_summit_level":True,"column":"地区热点","date":"2026-08-11"},
{"title_en":"Iran hierarchy consolidation as IRGC veteran tapped for key security role","title_zh":"伊朗任命革命卫队元老出任要职，权力加速整合","summary":"伊朗最高领袖办公室任命新的安全负责人并确立战时指挥官岗位，革命卫队元老出任关键安全职务，显示伊朗体制在战争期间加速权力集中。","source":"半岛电视台","category":"地缘政治","keywords":"伊朗,革命卫队,安全,权力,领导层","url":"https://www.aljazeera.com/news/2026/8/10/iran-hierarchy-consolidation-as-irgc-veteran-tapped-for-key-security-role","priority_score":80,"is_summit_level":False,"column":"地区热点","date":"2026-08-10"},
{"title_en":"Oman trying to contain extensive oil spill from stricken tanker","title_zh":"阿曼努力控制失事油轮大规模漏油","summary":"阿曼正努力控制一艘失事油轮的大规模漏油，该油轮据信属于俄罗斯规避西方制裁的\"影子船队\"，泄漏面积已相当可观。","source":"半岛电视台","category":"国际","keywords":"阿曼,油轮,漏油,俄罗斯,影子船队","url":"https://www.aljazeera.com/news/2026/8/10/oman-trying-to-contain-extensive-oil-spill-from-stricken-tanker","priority_score":72,"is_summit_level":False,"column":"地区热点","date":"2026-08-10"},
{"title_en":"Trump says relationship is good even as Netanyahu rejects Gaza peace plan","title_zh":"内塔尼亚胡拒绝加沙和平计划，特朗普称美以关系依然良好","summary":"尽管内塔尼亚胡公开拒绝特朗普的加沙和平计划，特朗普仍表示美以关系良好，淡化两国在哈马斯解除武装与以色列撤军问题上的严重分歧。","source":"半岛电视台","category":"地缘政治","keywords":"特朗普,内塔尼亚胡,加沙,美以关系,和平计划","url":"https://www.aljazeera.com/news/2026/8/10/trump-says-relationship-is-good-even-as-netanyahu-rejects-gaza-peace-plan","priority_score":85,"is_summit_level":True,"column":"地区热点","date":"2026-08-10"},
{"title_en":"US appeals court says social media addiction lawsuits can proceed","title_zh":"美国上诉法院裁定社交媒体成瘾诉讼可继续审理","summary":"美国上诉法院裁定，针对社交媒体平台成瘾的诉讼可以继续推进，此案涉及Instagram和YouTube等平台，或对科技公司责任认定产生深远影响。","source":"半岛电视台","category":"科技","keywords":"美国,社交媒体,成瘾,诉讼,平台责任","url":"https://www.aljazeera.com/news/2026/8/10/us-appeals-court-says-social-media-addiction-lawsuits-can-proceed","priority_score":70,"is_summit_level":False,"column":"科技竞争","date":"2026-08-10"},

# ---------------- Politico ----------------
{"title_en":"Zuckerberg warns against centralizing AI power","title_zh":"扎克伯格警告AI权力集中风险","summary":"马克·扎克伯格就AI权力集中化发出警告，认为将AI权力集中在少数实体手中可能带来风险，反映科技界围绕AI治理与开放模式的持续争论。","source":"Politico","category":"科技","keywords":"扎克伯格,AI,权力,监管,开源","url":"https://www.politico.com/news/2026/08/10/mark-zuckerberg-ai-power-01030904","priority_score":85,"is_summit_level":False,"column":"科技竞争","date":"2026-08-10"},
{"title_en":"Pakistan says new defense pact with Saudi Arabia and Turkey is 'purely defensive'","title_zh":"巴基斯坦称与沙特、土耳其新防务协议\"纯属防御性质\"","summary":"巴基斯坦表示，其与沙特阿拉伯和土耳其签署的新防务协议\"纯属防御性质\"。该协议或改变南亚及中东安全格局，引发地区对军事平衡的关注。","source":"Politico","category":"地缘政治","keywords":"巴基斯坦,沙特,土耳其,防务协议,安全","url":"https://www.politico.com/news/2026/08/09/pakistan-says-new-defense-pact-with-saudi-arabia-and-turkey-is-purely-defensive-01030194","priority_score":80,"is_summit_level":False,"column":"地区热点","date":"2026-08-09"},
{"title_en":"Germany battling 'daily' hybrid warfare attacks, minister warns","title_zh":"德国部长警告正应对\"日常\"混合战攻击","summary":"德国一位部长警告称，德国正面临\"日常\"的混合战攻击，包括网络攻击、虚假信息等，凸显欧洲在传统军事威胁之外面临的新型安全挑战。","source":"Politico","category":"地缘政治","keywords":"德国,混合战,网络攻击,虚假信息,安全","url":"https://www.politico.eu/article/germany-battling-daily-hybrid-warfare-attacks-minister-warns/","priority_score":78,"is_summit_level":False,"column":"欧洲","date":"2026-08-10"},
{"title_en":"Nagasaki marks 81st atomic bomb anniversary as mayor says nuclear deterrence only increases risk","title_zh":"长崎纪念原子弹爆炸81周年，市长称核威慑只会增加风险","summary":"日本长崎举行原子弹爆炸81周年纪念活动，市长在活动中表示核威慑只会增加风险，呼吁国际社会重新审视核武器政策，与当前地缘紧张形成对照。","source":"Politico","category":"地缘政治","keywords":"长崎,核武器,核威慑,纪念,日本","url":"https://www.politico.com/news/2026/08/09/nagasaki-marks-81st-atomic-bomb-anniversary-as-mayor-says-nuclear-deterrence-only-increases-risk-01030195","priority_score":70,"is_summit_level":False,"column":"地区热点","date":"2026-08-09"},

# ---------------- 华盛顿邮报 ----------------
{"title_en":"Contradicting public statements, Trump took secret flight from Turkey amid Iranian threat","title_zh":"与公开声明相矛盾：特朗普在伊朗威胁期间从土耳其秘密乘机","summary":"《华盛顿邮报》独家报道，特朗普总统在面临伊朗威胁期间从土耳其乘坐秘密航班，此前其公开声称乘坐空军一号。行动引发对总统安全措施与决策透明度的质疑。","source":"华盛顿邮报","category":"地缘政治","keywords":"特朗普,伊朗,秘密航班,空军一号,安全","url":"https://www.washingtonpost.com/national-security/2026/08/10/trump-flew-secrecy-amid-iran-threat-air-force-one-became-decoy/","priority_score":90,"is_summit_level":True,"column":"美国","date":"2026-08-10"},
{"title_en":"Chaos at Spain's border underscores how migrant flows can be weaponized","title_zh":"西班牙边境混乱凸显移民流动如何被武器化","summary":"报道分析西班牙边境（休达）爆发的混乱事件，指出移民流动可能被国家用作地缘政治武器，对欧盟与美国构成新安全挑战。","source":"华盛顿邮报","category":"地缘政治","keywords":"西班牙,休达,移民,边境,地缘政治","url":"https://www.washingtonpost.com/world/2026/08/10/spain-border-collapse-reveals-risk-weaponized-migration-eu-us/","priority_score":75,"is_summit_level":False,"column":"欧洲","date":"2026-08-10"},
{"title_en":"At least 111 dead as 7.4-magnitude earthquake strikes Colombia","title_zh":"哥伦比亚7.4级强震致至少111人死亡","summary":"哥伦比亚太平洋沿岸发生7.4级强震，造成至少111人死亡，波及厄瓜多尔、巴拿马和委内瑞拉等国，多栋建筑倒塌。","source":"华盛顿邮报","category":"国际","keywords":"哥伦比亚,地震,7.4级,灾害,南美","url":"https://www.washingtonpost.com/world/2026/08/10/74-magnitude-earthquake-colombia-kills-least-20/","priority_score":70,"is_summit_level":False,"column":"地区热点","date":"2026-08-10"},
{"title_en":"Iran says deal with Oman is close — but its demands leave Hormuz opening uncertain","title_zh":"伊朗称与阿曼协议接近达成，但要求使霍尔木兹开放前景不明","summary":"伊朗表示与阿曼就霍尔木兹海峡问题即将达成协议，但坚持要求美国赔偿与解除制裁等多项让步，使海峡重新开放前景仍充满不确定性。","source":"华盛顿邮报","category":"地缘政治","keywords":"伊朗,阿曼,霍尔木兹,制裁,谈判","url":"https://www.washingtonpost.com/world/2026/08/08/iran-says-deal-with-oman-is-close-its-demands-leave-hormuz-opening-uncertain/","priority_score":85,"is_summit_level":False,"column":"地区热点","date":"2026-08-08"},

# ---------------- 美联社 ----------------
{"title_en":"Trump scoffs at Iran's demand for war reparations and other Mideast developments","title_zh":"特朗普对伊朗战争赔款要求嗤之以鼻，中东局势持续演变","summary":"特朗普对伊朗提出的战争赔款要求表示不屑，同时中东地区围绕霍尔木兹海峡重开的紧张局势持续，多项事态并行发展。","source":"美联社","category":"地缘政治","keywords":"特朗普,伊朗,赔款,中东,霍尔木兹","url":"https://apnews.com/article/iran-us-strait-hormuz-august-10-2026-0bdaae8f1d7b781918e76dca4317c897","priority_score":88,"is_summit_level":True,"column":"地区热点","date":"2026-08-10"},
{"title_en":"Ukrainian drone attack on an oil hub deep inside Russia kills 13, officials say","title_zh":"乌无人机袭击俄腹地石油枢纽，官方称13人死亡","summary":"乌克兰对俄罗斯境内深处的石油枢纽发动无人机袭击，官方称已造成13人死亡，是俄乌冲突中乌对俄纵深打击的最新一例。","source":"美联社","category":"地缘政治","keywords":"乌克兰,俄罗斯,无人机,石油,袭击","url":"https://apnews.com/article/russia-ukraine-war-drones-oil-d0e7dc74936cf153e8e473444cc09366","priority_score":78,"is_summit_level":False,"column":"欧洲","date":"2026-08-10"},
{"title_en":"Russian court bars from parliamentary ballot the only party opposing the conflict in Ukraine","title_zh":"俄法院禁止唯一反战政党\"亚博卢\"参选议会","summary":"俄罗斯最高法院裁定禁止\"亚博卢\"党参加即将举行的议会选举，该党是俄罗斯唯一公开反对乌克兰冲突的政党，此举进一步压缩国内政治反对空间。","source":"美联社","category":"地缘政治","keywords":"俄罗斯,亚博卢,议会选举,反对党,乌克兰","url":"https://apnews.com/article/russia-yabloko-political-party-parliament-election-fffdd68de22ad70cebc81e5aa308202c","priority_score":75,"is_summit_level":False,"column":"欧洲","date":"2026-08-10"},
{"title_en":"Turkey's parliament approves a pardon-like bill for thousands of PKK militants","title_zh":"土耳其议会通过类赦免法案，惠及数千名库尔德工人党武装分子","summary":"土耳其议会通过一项类似赦免的法案，涉及数千名库尔德工人党（PKK）武装分子，是土耳其政府推动库尔德和平进程的一部分。","source":"美联社","category":"地缘政治","keywords":"土耳其,库尔德工人党,赦免,和平进程,议会","url":"https://apnews.com/article/turkey-parliament-bill-pkk-peace-effort-a9addfb69c8126f1d661d4f37ef74827","priority_score":75,"is_summit_level":False,"column":"欧洲","date":"2026-08-10"},
{"title_en":"Congressional Democrats launch probe into efforts to deport US military members and their families","title_zh":"国会民主党人启动对驱逐美军成员及其家属问题的调查","summary":"国会民主党人宣布就特朗普政府驱逐美军成员及其家属的行为展开调查，该调查涉及移民政策在军事人员群体中的执行情况。","source":"美联社","category":"美国","keywords":"美国,国会,民主党,驱逐,军人","url":"https://apnews.com/article/immigration-military-families-deport-trump-democrats-86087b0394dc8fe01cfec877903d266b","priority_score":70,"is_summit_level":False,"column":"美国","date":"2026-08-10"},
{"title_en":"Magnitude 7.4 quake rocks western Colombia, killing at least 111 people","title_zh":"7.4级强震袭击哥伦比亚西部，至少111人遇难","summary":"一场7.4级强烈地震袭击哥伦比亚西部，造成至少111人死亡、数百栋建筑受损，哥伦比亚总统宣布进入国家紧急状态，救援工作持续。","source":"美联社","category":"国际","keywords":"哥伦比亚,地震,7.4级,遇难,紧急状态","url":"https://apnews.com/article/colombia-ecuador-earthquake-26fd40f93272d834fced47a4a673edc9","priority_score":70,"is_summit_level":False,"column":"地区热点","date":"2026-08-10"},
]

# ============ 合并 + 去重 (title[:30], source) ============
all_items = list(kept)
seen = {}
for it in all_items:
    key = (it.get('title_en','')[:30] or it.get('title','')[:30], it.get('source',''))
    seen[key] = True

added_new = 0
for it in NEW_ITEMS:
    t_en = clean(it.get('title_en',''))
    if not t_en:
        continue
    key = (t_en[:30], it['source'])
    if key in seen:
        print(f"  跳过重复: [{it['source']}] {t_en[:40]}")
        continue
    # 构造完整字段
    item = {
        "title_en": t_en,
        "title_zh": it['title_zh'],
        "summary": it['summary'],
        "source": it['source'],
        "category": it['category'],
        "keywords": it['keywords'],
        "url": it['url'],
        "priority_score": it['priority_score'],
        "is_summit_level": it['is_summit_level'],
        "column": it['column'],
        "date": it['date'],
        "title": f"{t_en} {it['title_zh']}",
    }
    all_items.append(item)
    seen[key] = True
    added_new += 1

print(f"\n新增 {added_new} 条，合并后总条数: {len(all_items)}")

# 按信源统计
from collections import Counter
print("按信源:", dict(Counter(it.get('source') for it in all_items)))

# URL 完整性校验
no_url = [it for it in all_items if not (it.get('url') or '').startswith('https://')]
print(f"URL 缺失/非法: {len(no_url)}")

with open(BASE, 'w') as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)
print("已写入 data/news-webfetch.json")
