# -*- coding: utf-8 -*-
"""2026-08-18 WebFetch 手工采集追加（23 条精选）"""
import json

COLLECTED_AT = "2026-08-18 09:35:00"

new_items = [
    # ===== Reuters 5 条 =====
    {
        "title": "Iran threatens new offensive while US rules out extending ceasefire deal",
        "title_en": "Iran threatens new offensive while US rules out extending ceasefire deal",
        "title_zh": "伊朗威胁发动新攻势 美国排除延长临时停火协议",
        "summary": "一名伊朗高级官员称，因与美国就结束战争的谈判陷入停滞，伊朗将转向\"全面进攻\"军事姿态；华盛顿则排除延长临时停火协议。",
        "source": "路透社",
        "category": "中东",
        "keywords": ["伊朗", "美伊冲突", "停火协议"],
        "url": "https://www.reuters.com/world/middle-east/iran-threatens-go-offensive-strait-hormuz-if-diplomacy-with-us-fails-2026-08-17/",
        "priority_score": 88,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    {
        "title": "Trump approval falls to 33%, lowest of his presidency, Reuters/Ipsos poll finds",
        "title_en": "Trump approval falls to 33%, lowest of his presidency, Reuters/Ipsos poll finds",
        "title_zh": "路透/益普索民调：特朗普支持率跌至33% 创任期新低",
        "summary": "路透社与益普索联合民调显示，特朗普支持率降至33%，为就任以来最低水平，反映连月战争与通胀压力对其选情的影响。",
        "source": "路透社",
        "category": "美国",
        "keywords": ["特朗普", "支持率", "民调"],
        "url": "https://www.reuters.com/world/us/trump-approval-falls-33-lowest-his-presidency-reutersipsos-poll-finds-2026-08-17/",
        "priority_score": 75,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    {
        "title": "Trump says North Korea's Kim has responded to his overtures",
        "title_en": "Trump says North Korea's Kim has responded to his overtures",
        "title_zh": "特朗普称金正恩已对其示好作出回应",
        "summary": "特朗普表示，朝鲜最高领导人金正恩已对其外交示好作出回应。此前他下令大幅缩减美韩联合军演，引发外界对美朝重启对话的猜测。",
        "source": "路透社",
        "category": "地区热点",
        "keywords": ["特朗普", "金正恩", "美朝关系"],
        "url": "https://www.reuters.com/world/china/trump-says-north-koreas-kim-has-responded-his-overtures-2026-08-17/",
        "priority_score": 85,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    {
        "title": "Erdogan urges Trump to pursue talks with Iran, offers support",
        "title_en": "Erdogan urges Trump to pursue talks with Iran, offers support",
        "title_zh": "埃尔多安敦促特朗普与伊朗继续谈判 并表示愿意提供支持",
        "summary": "土耳其总统埃尔多安敦促美国总统特朗普继续与伊朗进行谈判，并表示愿意提供支持，以缓解美伊紧张局势。",
        "source": "路透社",
        "category": "中东",
        "keywords": ["埃尔多安", "土耳其", "美伊谈判"],
        "url": "https://www.reuters.com/world/asia-pacific/erdogan-urges-trump-pursue-talks-with-iran-offers-support-2026-08-17/",
        "priority_score": 70,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    {
        "title": "Russia jails anti-war politician for 11 years in further clampdown on dissent",
        "title_en": "Russia jails anti-war politician for 11 years in further clampdown on dissent",
        "title_zh": "俄罗斯判处反战政治家11年监禁 进一步打压异见",
        "summary": "俄罗斯以\"诋毁俄军\"罪名判处反战政治家列夫·施洛斯伯格11年监禁，他谴责这一判决是对其政治立场的惩罚。",
        "source": "路透社",
        "category": "俄乌冲突",
        "keywords": ["俄罗斯", "反战", "异见打压"],
        "url": "https://www.reuters.com/business/media-telecom/russia-jails-opposition-politician-11-years-anti-war-comments-mediazona-says-2026-08-17/",
        "priority_score": 72,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    # ===== BBC 1 条 =====
    {
        "title": "Trump threatens to bomb US ally Oman if it 'gets in the way' over Iran deal",
        "title_en": "Trump threatens to bomb US ally Oman if it 'gets in the way' over Iran deal",
        "title_zh": "特朗普威胁轰炸美国盟友阿曼 若其\"碍事\"阻挠伊朗协议",
        "summary": "特朗普威胁称，如果阿曼在伊朗协议问题上\"碍事\"就将对其轰炸。阿曼一直与伊朗就重开霍尔木兹海峡举行会谈，而为期60天的和平谈判窗口即将到期。",
        "source": "BBC",
        "category": "中东",
        "keywords": ["特朗普", "阿曼", "霍尔木兹海峡"],
        "url": "https://www.bbc.com/news/articles/cy5dzk0ryzdo",
        "priority_score": 85,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    # ===== SCMP 4 条 =====
    {
        "title": "Claims Hegseth close to exit raise questions over future US-China defence ties",
        "title_en": "Claims Hegseth close to exit raise questions over future US-China defence ties",
        "title_zh": "独家：赫格塞斯或将离任引发对美中国防关系走向的质疑",
        "summary": "南华早报独家报道，美国国防部长赫格塞斯或将离任的传闻引发外界对美中国防关系未来走向的担忧，正值美中关系敏感时期。",
        "source": "南华早报",
        "category": "中美关系",
        "keywords": ["赫格塞斯", "美国国防部", "美中军事关系"],
        "url": "https://www.scmp.com/news/china/diplomacy/article/3364313/claims-hegseth-verge-losing-job-raise-questions-about-future-us-china-defence-ties",
        "priority_score": 88,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    {
        "title": "Taiwan teams up with US start-up on underwater drones to boost island's defences",
        "title_en": "Taiwan teams up with US start-up on underwater drones to boost island's defences",
        "title_zh": "台湾与美国初创公司合作研发水下无人机 强化岛内防务",
        "summary": "台湾地区与美国初创公司Vatn Systems合作开发水下无人机，旨在强化不对称作战能力，以应对北京日益增长的军事压力。",
        "source": "南华早报",
        "category": "台海",
        "keywords": ["台湾", "水下无人机", "不对称作战"],
        "url": "https://www.scmp.com/news/china/military/article/3364328/taiwan-teams-us-start-underwater-drones-boost-islands-defences",
        "priority_score": 85,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    {
        "title": "Chinese team aims to put 'smart' diabetes probiotic on US shelves within 2 years",
        "title_en": "Chinese team aims to put 'smart' diabetes probiotic on US shelves within 2 years",
        "title_zh": "中国团队研发\"智能\"糖尿病益生菌 拟两年内进入美国市场",
        "summary": "中国科研团队研发的\"智能\"糖尿病益生菌可感知高血糖并自动释放降糖激素，计划两年内进入美国市场，展现中国生物科技出海势头。",
        "source": "南华早报",
        "category": "科技",
        "keywords": ["糖尿病", "益生菌", "生物科技"],
        "url": "https://www.scmp.com/news/china/science/article/3364322/chinese-team-aims-put-smart-diabetes-probiotic-us-shelves-within-2-years",
        "priority_score": 68,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    {
        "title": "China's economy cools amid debate about risks of global crisis",
        "title_en": "China's economy cools amid debate about risks of global crisis",
        "title_zh": "中国经济放缓 引发全球危机风险之争",
        "summary": "7月经济数据进一步显示中国经济放缓迹象，同时美国前贸易代表称中国过度依赖出口对全球构成风险，引发关于全球危机风险的讨论。",
        "source": "南华早报",
        "category": "中国",
        "keywords": ["中国经济", "放缓", "出口依赖"],
        "url": "https://www.scmp.com/plus/economy/china-economy/article/3364282/chinas-economy-cools-amid-debate-about-risks-global-crisis",
        "priority_score": 78,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    # ===== Guardian 1 条 =====
    {
        "title": "Trump's move to gut South Korea alliance is 'inane, haphazard decision', lawmakers say",
        "title_en": "Trump's move to gut South Korea alliance is 'inane, haphazard decision', lawmakers say",
        "title_zh": "美议员批评特朗普削弱美韩同盟是\"愚蠢、草率的决定\"",
        "summary": "美国国会议员批评特朗普下令缩减美韩联合军演是\"愚蠢且草率的决定\"，担忧此举削弱美韩同盟与地区安全威慑，并向朝鲜传递错误信号。",
        "source": "卫报",
        "category": "美国",
        "keywords": ["特朗普", "美韩同盟", "军演削减"],
        "url": "https://www.theguardian.com/us-news/2026/aug/17/trump-south-korea-alliance",
        "priority_score": 75,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    # ===== CNN 2 条 =====
    {
        "title": "Top Russian economist replaced after warning of economic costs of Ukraine war",
        "title_en": "Top Russian economist replaced after warning of economic costs of Ukraine war",
        "title_zh": "俄顶级经济学家警告乌克兰战争经济代价后被替换",
        "summary": "俄罗斯顶级经济学家安德烈·克莱帕奇在警告乌克兰战争的经济代价后被撤换，反映俄内部对战争成本存在分歧。",
        "source": "CNN",
        "category": "俄乌冲突",
        "keywords": ["俄罗斯", "经济学家", "战争代价"],
        "url": "https://edition.cnn.com/2026/08/17/europe/andrey-klepach-top-russian-economist-replaced-intl",
        "priority_score": 70,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    {
        "title": "Exclusive: Ukraine reveals its Achilles' heel to CNN as Patriot missile launchers run dry",
        "title_en": "Exclusive: Ukraine reveals its Achilles' heel to CNN as Patriot missile launchers run dry",
        "title_zh": "独家：乌军爱国者导弹发射器耗尽 向CNN透露致命弱点",
        "summary": "乌克兰向CNN独家透露其致命弱点：爱国者导弹发射器已耗尽，防空能力面临严峻挑战，可能影响抵御俄军空袭的能力。",
        "source": "CNN",
        "category": "俄乌冲突",
        "keywords": ["乌克兰", "爱国者导弹", "防空"],
        "url": "https://edition.cnn.com/2026/08/17/europe/ukraine-patriot-missile-launchers-run-dry-intl",
        "priority_score": 75,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    # ===== NYT 2 条 =====
    {
        "title": "Nvidia to Back Ohio Data Center With as Much as $105 Billion",
        "title_en": "Nvidia to Back Ohio Data Center With as Much as $105 Billion",
        "title_zh": "英伟达拟斥资高达1050亿美元支持俄亥俄州数据中心",
        "summary": "英伟达将投入高达1050亿美元支持俄亥俄州的数据中心项目（涉及OpenAI），这是AI基础设施领域的重大投资，凸显AI算力军备竞赛白热化。",
        "source": "纽约时报",
        "category": "科技",
        "keywords": ["英伟达", "数据中心", "AI投资"],
        "url": "https://www.nytimes.com/2026/08/17/technology/nvidia-ohio-data-center-openai.html",
        "priority_score": 95,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    {
        "title": "Sick of A.I. Slop? So Are Tech Giants.",
        "title_en": "Sick of A.I. Slop? So Are Tech Giants.",
        "title_zh": "厌倦AI垃圾内容？科技巨头们也是",
        "summary": "Spotify、LinkedIn等科技公司正在努力清理由人工智能生成的低质量\"AI垃圾\"内容，反映AI内容泛滥对平台生态的冲击。",
        "source": "纽约时报",
        "category": "科技",
        "keywords": ["AI内容", "平台治理", "垃圾内容"],
        "url": "https://www.nytimes.com/2026/08/17/technology/ai-slop.html",
        "priority_score": 72,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    # ===== WSJ 2 条 =====
    {
        "title": "Trump Tries Old Move to Woo a More Powerful Kim Jong Un",
        "title_en": "Trump Tries Old Move to Woo a More Powerful Kim Jong Un",
        "title_zh": "特朗普重施旧招拉拢实力更强的金正恩",
        "summary": "特朗普重拾2018年的老套路，下令缩减美韩军演以拉拢金正恩。但朝鲜军事威胁比当年显著增强：核武库扩大、导弹产量增加并获俄战场经验，风险远高于从前。",
        "source": "华尔街日报",
        "category": "地区热点",
        "keywords": ["特朗普", "金正恩", "美朝关系"],
        "url": "https://www.wsj.com/world/asia/trump-tries-old-move-to-woo-a-more-powerful-kim-jong-un-3e7a3bde",
        "priority_score": 85,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    {
        "title": "Iran's Secret Plan to Escalate the War",
        "title_en": "Iran's Secret Plan to Escalate the War",
        "title_zh": "WSJ独家：伊朗的秘密战争升级计划",
        "summary": "截获的通讯和其他情报显示，伊朗强硬派领导层正进行战略调整：革命卫队加强对正规军控制、加速导弹和无人机生产、将战场从霍尔木兹扩展至红海，旨在让美国及其地区盟友付出更高代价。",
        "source": "华尔街日报",
        "category": "中东",
        "keywords": ["伊朗", "战争升级", "革命卫队"],
        "url": "https://www.wsj.com/world/middle-east/iran-plan-escalate-war-cc657664",
        "priority_score": 92,
        "is_summit_level": False,
        "date": "2026-08-16",
        "collectedAt": COLLECTED_AT
    },
    # ===== 半岛 3 条 =====
    {
        "title": "Trump rejects MoU extension with Iran as US claims total control of Hormuz",
        "title_en": "Trump rejects MoU extension with Iran as US claims total control of Hormuz",
        "title_zh": "特朗普拒绝延长与伊朗谅解备忘录 美方宣称完全控制霍尔木兹海峡",
        "summary": "特朗普拒绝延长与伊朗的谅解备忘录，并宣称美国已完全控制霍尔木兹海峡，要求伊朗\"举白旗投降\"。两国谅解备忘录于周一到期。",
        "source": "半岛电视台",
        "category": "中东",
        "keywords": ["特朗普", "伊朗", "霍尔木兹海峡"],
        "url": "https://www.aljazeera.com/news/liveblog/2026/8/18/iran-war-live-trump-rejects-mou-extension-as-us-claims-control-of-hormuz",
        "priority_score": 90,
        "is_summit_level": False,
        "date": "2026-08-18",
        "collectedAt": COLLECTED_AT
    },
    {
        "title": "'We will not allow Gaza to be rebuilt' until Hamas disarms, Kushner says",
        "title_en": "'We will not allow Gaza to be rebuilt' until Hamas disarms, Kushner says",
        "title_zh": "库什纳：哈马斯不解除武装 加沙就不会重建",
        "summary": "特朗普特使兼女婿库什纳表示，在哈马斯解除武装之前，将不允许加沙重建，给加沙和平进程划定新条件。",
        "source": "半岛电视台",
        "category": "中东",
        "keywords": ["库什纳", "加沙", "哈马斯"],
        "url": "https://www.aljazeera.com/news/2026/8/17/we-will-not-allow-gaza-to-be-rebuilt-until-hamas-disarms-kushner-says",
        "priority_score": 75,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    {
        "title": "Russia maintains election ban on opposition Yabloko, jails deputy head",
        "title_en": "Russia maintains election ban on opposition Yabloko, jails deputy head",
        "title_zh": "俄罗斯维持对反对党亚博卢的参选禁令 副主席被判入狱",
        "summary": "俄最高法院维持对反对党亚博卢的参选禁令，并判处其副主席监禁，进一步打压9月议会选举前的政治反对力量。",
        "source": "半岛电视台",
        "category": "俄乌冲突",
        "keywords": ["俄罗斯", "亚博卢党", "选举打压"],
        "url": "https://www.aljazeera.com/news/2026/8/17/russia-maintains-election-ban-on-opposition-yabloko-jails-deputy-head",
        "priority_score": 70,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    # ===== Politico 1 条 =====
    {
        "title": "Xi Jinping will skip UN ahead of Trump summit",
        "title_en": "Xi Jinping will skip UN ahead of Trump summit",
        "title_zh": "习近平将缺席联合国大会 此前将举行特习会",
        "summary": "报道称，中国国家主席习近平将缺席联合国大会，这一决定发生在与特朗普举行峰会之前，引发对中美高层外交安排的新关注。",
        "source": "Politico",
        "category": "中美关系",
        "keywords": ["习近平", "联合国大会", "特习会"],
        "url": "https://www.politico.com/news/2026/08/17/xi-jinping-skip-unga-trump-summit-01039237",
        "priority_score": 92,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    # ===== AP 2 条 =====
    {
        "title": "Ukraine takes aim at Russia's economy and morale by attacking online retailer",
        "title_en": "Ukraine takes aim at Russia's economy and morale by attacking online retailer",
        "title_zh": "乌克兰攻击俄罗斯电商平台 打击俄经济与士气",
        "summary": "乌克兰通过网络攻击俄罗斯在线零售商Wildberries，以打击俄罗斯经济与民众士气，开辟对俄经济战新战线。",
        "source": "美联社",
        "category": "俄乌冲突",
        "keywords": ["乌克兰", "网络攻击", "经济战"],
        "url": "https://apnews.com/article/russia-ukraine-war-putin-wildberries-kim-48c331f100a1d981959c5d75a1397d21",
        "priority_score": 70,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
    {
        "title": "After killing hundreds in boat strikes, US military expands campaign on land in Latin America",
        "title_en": "After killing hundreds in boat strikes, US military expands campaign on land in Latin America",
        "title_zh": "美军在船艇打击致数百人死亡后 将行动扩展至拉美陆上",
        "summary": "美军在对拉美船艇的打击行动中造成数百人死亡后，将军事行动扩展至拉丁美洲陆上，西半球反毒与安全行动显著升级。",
        "source": "美联社",
        "category": "地区热点",
        "keywords": ["美军", "拉丁美洲", "军事行动"],
        "url": "https://apnews.com/article/trump-military-operations-latin-american-western-hemisphere-a1fccf4414e44341d3dbd54e19ae1ba4",
        "priority_score": 72,
        "is_summit_level": False,
        "date": "2026-08-17",
        "collectedAt": COLLECTED_AT
    },
]

# 追加（去重）
wf = json.load(open('data/news-webfetch.json'))
existing_urls = {x.get('url') for x in wf}
added = 0
for it in new_items:
    if it['url'] not in existing_urls:
        wf.append(it)
        existing_urls.add(it['url'])
        added += 1
json.dump(wf, open('data/news-webfetch.json', 'w'), ensure_ascii=False, indent=2)
print(f"追加 {added} 条，webfetch 现有 {len(wf)} 条")
