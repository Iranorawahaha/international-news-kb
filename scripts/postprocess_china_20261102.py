#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内看板 LLM 质量后处理 2026-11-02
初抓 40 条 -> 质量后处理 + AI 补强
主线：五中全会《决定》全文及习近平说明公布（11-01）+ 阿曼苏丹海赛姆国事访华（11-01~02）
补强重点：G20 外长会（外交部原文死链改 /wjbxw_new/ 路径）、中秘自贸协定升级议定书 11-01 生效、
        乌镇峰会开幕、南水北调中线年度供水完成、"妈祖"2.0、载人月球探测方案、前三季度物流数据
"""
import json, html, re
from collections import Counter

PATH = 'data/china-news.json'
TODAY = '2026-11-02'
YDAY = '2026-11-01'
COLLECT = '2026-11-02 09:40:00'

d = json.load(open(PATH, encoding='utf-8'))
arr = d['archive'][TODAY]
before = len(arr)


def key(u):
    u = (u or '').strip().rstrip('/')
    u = re.sub(r'^https?://', '', u)
    return u.replace('www.', '', 1) if u.startswith('www.') else u


# ---------- 删除清单（按 URL 精确匹配） ----------
DEL_URLS = {
    # ===== 元首动态：宣传产品 / 同事件多稿 =====
    # 1 黄河流域生态保护「纪实/通讯」体裁宣传产品（非元首活动本身）
    'https://www.gov.cn/yaowen/liebiao/202611/content_7084713.htm',
    # 2 CBA/新闻联播视频版《说明》（留 gov.cn 7084692 文字版）
    'https://tv.cctv.com/2026/11/01/VIDEQGPgxD2S2j4TQf77Zu5f261101.shtml',
    # 3 gov.cn 7084692（带"习近平："前缀的说明全文）—— 统一并入 7084714 综合条目
    'https://www.gov.cn/yaowen/liebiao/202611/content_7084692.htm',
    # 4 zaobao 引语稿 —— 《决定》说明已在综合条目覆盖，且无摘要
    'https://www.zaobao.com/news/china/story20261101-9929402',

    # ===== 重要会议：评论员/反响稿（固定删除类） =====
    # 5 世界政党政要评价 —— 国际反响稿
    'https://www.gov.cn/yaowen/liebiao/202611/content_7084679.htm',
    # 6 中央和国家机关、人民团体学习贯彻 —— 反响稿
    'https://news.cctv.com/2026/11/01/ARTId7AbpwDJzuS4PzP6ZJvl261101.shtml',
    # 7 人民日报评论员：坚持服务党的使命任务 —— 「论学习贯彻…」排比式评论
    'https://www.gov.cn/yaowen/liebiao/202611/content_7084671.htm',
    # 8 新华社评论员：深刻把握… —— 同上
    'https://www.gov.cn/yaowen/liebiao/202611/content_7084677.htm',
    # 9 以管党治党新成效开创事业发展新局面 —— 学习体会稿（标题即栏目体，摘要仅39字）
    'https://news.cctv.com/2026/11/02/ARTIaqMA53NNW1K0ef8dKY5m261102.shtml',
    # 10 人民日报 永葆生机活力… —— 学习贯彻反响稿
    'http://paper.people.com.cn/rmrb/pc/content/202611/02/content_30188812.html',
    # 11 解读｜全面从严治党 五中全会作出重要部署 —— 「解读|」栏目体，与《决定》全文重复
    'https://news.cctv.com/2026/11/01/ARTIT5wHkMMnyyUnj5RP2Azj261101.shtml',

    # ===== 部委动态：跨版面 / 错误分类 / 死链 =====
    # 12 台湾研议扩大先进半导体对陆出口管制 —— 半导体管制属 AI/国际线，且 zaobao 单源无摘要
    'https://www.zaobao.com/news/china/story20261101-9930406',
    # 13 港媒：美第一夫人料不随特朗普赴深圳出席 APEC —— 港媒推测稿，且分类错置（非重要会议）
    'https://www.zaobao.com/news/china/story20261102-9931358',
    # 14 APEC 致函差别对待 台外交部抗议 —— 台湾地方政治/涉台争议，按规则排除
    'https://www.zaobao.com/news/china/story20261101-9929404',
    # 15~18 外交部马朝旭 G20 外长会 4 稿 —— 原 URL 全部跳「系统维护」死链，改由 /wjbxw_new/ 原件单条替代
    'https://www.mfa.gov.cn/web/wjdt_674879/202611/t20261101_12050885.shtml',
    'https://www.mfa.gov.cn/web/wjdt_674879/202611/t20261101_12050887.shtml',
    'https://www.mfa.gov.cn/web/wjdt_674879/202611/t20261101_12050889.shtml',
    'https://www.mfa.gov.cn/web/wjdt_674879/202611/t20261101_12050891.shtml',

    # ===== 政策发布：zaobao 评论 / 重复 / 涉台琐事 =====
    # 19 zaobao 全面从严治党决定解读 —— 与《决定》全文综合条重复
    'https://www.zaobao.com/news/china/story20261101-9930614',
    # 20 zaobao 载人登月方案「分析：中美太空竞争料加剧」—— 评论稿，官方口径见央视条
    'https://www.zaobao.com/news/china/story20261101-9930192',
    # 21 zaobao 高雄市长选战民调 —— 台湾地方政治，明确排除
    'https://www.zaobao.com/news/china/story20261102-9931229',
    # 22 《决定》单行本出版 —— 出版消息类，非政策本体（且摘要含 gov.cn 页脚）
    'https://www.gov.cn/yaowen/liebiao/202611/content_7084708.htm',

    # ===== 人事任免 =====
    # 23 zaobao 厦门市委换届 —— 地市级党委换届，低于门槛 + 无摘要
    'https://www.zaobao.com/news/china/story20261101-9930626',

    # ===== 经贸动向：zaobao 传闻 / 栏目体 =====
    # 24 zaobao「据报三大金融监管部门周一开会研究稳定股市」—— 传闻稿，无官方源
    'https://www.zaobao.com/news/china/story20261101-9930004',
    # 25 zaobao 机器人产业融资 —— 属 AI 线且为行业分析稿，跨版面
    'https://www.zaobao.com/news/china/story20261102-9931333',
    # 26 AI 检测让好品质榴莲解锁进博入场券 —— 进博会软稿
    'https://news.cctv.com/2026/11/01/ARTIwJluoJbvwgFX9L6bl6Ku261031.shtml',
    # 27 毛衫产业「组团接单」出海 —— 广交会蹲点故事化稿
    'https://news.cctv.com/2026/11/01/ARTIzAvIaJo1deiaAUEKglJ6261101.shtml',
    # 28 火热订单从展馆直达生产车间 —— 同上，广交会软稿（另有多稿）
    'https://news.cctv.com/2026/11/01/ARTI83Qoh52Yhx1pnXiMwhzP261101.shtml',
    # 29 广交会第三期开展 —— 保留（展会节点、数据完整）
    # 30 银发游「黄金季」—— 民生蹲点稿
    'https://news.cctv.com/2026/11/01/ARTIqGBouqlkOvuF7e6dbCUs261101.shtml',
    # 31 问诊机器人、AI 眼镜…消费新场景 —— 栏目体，且属 AI 线
    'https://news.cctv.com/2026/11/01/ARTIuOmA3sphqTVeEsr6Ozc9261101.shtml',
    # 32 我国人工智能推理数据量首超训练数据量 —— 属 AI 线，跨版面
    'https://news.cctv.com/2026/11/01/ARTIHkeO9UQ4kuSs6cePZUb1261101.shtml',
}

deleted = []
keep = []
for it in arr:
    if key(it['url']) in {key(u) for u in DEL_URLS}:
        deleted.append(it['title'])
    else:
        keep.append(it)
arr = keep

# ---------- 修正清单（按 URL 定位） ----------
FIX = {
    # 高志丹特使出席青奥会：gov.cn 原文，元首动态 100，补真实摘要
    'www.gov.cn/yaowen/liebiao/202611/content_7084681.htm': {
        'title': '习近平主席特使、国家体育总局局长高志丹出席第四届青奥会开幕式',
        'source': '中国政府网·要闻',
        'date': '2026-11-01',
        'category': '元首动态',
        'priority_score': 100,
        'is_summit_level': True,
        'summary': '应塞内加尔共和国政府邀请，习近平主席特使、国家体育总局局长高志丹10月31日在塞内加尔首都达喀尔出席第四届青奥会开幕式。当天上午，塞内加尔总统法耶在达喀尔会见高志丹。高志丹向法耶转达习近平主席的亲切问候和良好祝愿，表示中方高度重视发展中塞、中非关系，愿不断丰富中塞全面战略合作伙伴关系内涵，积极发挥奥林匹克运动促和平、促团结、促包容的独特作用。法耶请高志丹转达对习近平主席的诚挚问候，感谢习近平主席派特使出席开幕式，表示中国是塞内加尔最重要的合作伙伴之一。',
    },
    # 新华社受权全文播发《决定》+《说明》—— 合并为一条综合条目
    'www.gov.cn/yaowen/liebiao/202611/content_7084714.htm': {
        'title': '新华社受权全文播发《中共中央关于持之以恒推进全面从严治党若干重大问题的决定》和习近平所作的说明',
        'source': '中国政府网·要闻',
        'date': '2026-11-01',
        'category': '元首动态',
        'priority_score': 100,
        'is_summit_level': True,
        'summary': '新华社11月1日受权全文播发《中共中央关于持之以恒推进全面从严治党若干重大问题的决定》和中共中央总书记习近平所作的《关于〈决定〉的说明》。《决定》由党的二十届五中全会10月29日通过，约1.7万字，除开头语和结束语外分三大板块：总论阐明重要性紧迫性与总体要求、并提出7条原则；分论由第二至第八部分部署增强党性、严格贯彻民主集中制、锻造高素质干部队伍、建设严密组织体系、驰而不息正风肃纪、一体推进不敢腐不能腐不想腐、坚持制度治党依规治党等战略任务；第三板块完善党和国家监督体系、落实全面从严治党政治责任。习近平在说明中介绍，文件起草组今年1月成立、由他担任组长，王沪宁、蔡奇、李希任副组长，2月6日召开第一次全体会议启动起草；8月3日《决定》稿下发党内一定范围征求意见，各方面提出的意见被逐条研究、能吸收的尽量吸收。',
    },
    # 贺劲红/韩劲红：纪检通报，人事87 档（反贪腐）
    'news.cctv.com/2026/11/02/ARTIOFMszu6AVfXLdxwaKoqX261102.shtml': {
        'title': '教育部教师工作司原副司长韩劲红接受纪律审查和监察调查',
        'source': '央视新闻',
        'date': '2026-11-02',
        'category': '人事任免',
        'priority_score': 87,
        'is_summit_level': False,
        'summary': '中央纪委国家监委网站通报，据中央纪委国家监委驻教育部纪检监察组、浙江省纪委监委消息：教育部教师工作司原副司长韩劲红涉嫌严重违纪违法，主动投案，目前正接受中央纪委国家监委驻教育部纪检监察组纪律审查和浙江省监委监察调查。',
    },
    # 设施农用地通知：政策发布 80，补真实摘要
    'news.cctv.com/2026/11/02/ARTIVP3zz9bXq5VsDeDEgg8M261102.shtml': {
        'title': '自然资源部等三部门联合印发《关于完善设施农用地管理的通知》',
        'source': '央视新闻',
        'date': '2026-11-02',
        'category': '政策发布',
        'priority_score': 80,
        'is_summit_level': False,
        'summary': '自然资源部、农业农村部、国家林业和草原局近日联合印发《关于完善设施农用地管理的通知》，以"设施农业使用土地正面清单"区分用地方式实行差异化管理：未破坏耕作层的按原土地用途管理、无需办理用地手续；破坏耕作层且直接为农业生产服务的生产及附属设施按设施农用地管理、办理县级备案；未纳入正面清单的须办理建设用地审批。通知要求依托国土空间规划"一张图"明确通则式选址要求，鼓励使用戈壁荒漠盐碱地等未利用地、存量建设用地，允许占用永久基本农田以外的耕地；对生产设施规模不作限制，对附属设施实行用地比例和规模上限控制；将备案层级提高到县级，并建立全链条、全生命周期监管模块。',
    },
    # 载人月球探测：政策发布 → 部委动态 85（国家重大工程方案，非政策文本）
    'news.cctv.com/2026/11/01/ARTI35N3BlXXAOOdnhAIKG9K261101.shtml': {
        'title': '我国载人月球探测工程采用"两次发射、环月对接"方案',
        'source': '央视新闻',
        'date': '2026-11-01',
        'category': '部委动态',
        'priority_score': 85,
        'is_summit_level': False,
        'summary': '记者从10月31日开幕的第七届载人航天学术大会获悉，我国载人月球探测工程采用"两次发射、环月对接"方案：两枚火箭分别将揽月月面着陆器与梦舟载人飞船送入地月转移轨道，之后在环月轨道交会对接，航天员从梦舟飞船进入揽月着陆器实施着陆。中国载人航天工程副总设计师、月球探测工程总设计师王翔表示，该方案与现有技术能力和设施手段相匹配，两器分开研制有利于标准化与形成系列型谱。目前长征十号运载火箭、梦舟飞船、揽月着陆器研制进展顺利，已完成梦舟飞船零高度逃逸、揽月着陆器着陆起飞、长征十号低空演示验证与最大动压逃逸飞行等大型试验，后续将完成三者首飞任务。',
    },
    # 广交会第三期：保留，经贸 85（国家级展会节点 + 70 周年）
    'news.cctv.com/2026/11/01/ARTIHJ9OA7aqe7FNzjxrRsGX261101.shtml': {
        'title': '第140届广交会第三期开展 恰逢广交会创办70周年',
        'source': '央视新闻',
        'date': '2026-11-01',
        'category': '经贸动向',
        'priority_score': 85,
        'is_summit_level': False,
        'summary': '10月31日，第140届中国进出口商品交易会第三期线下展正式开展，本届展会恰逢广交会创办70周年。第三期延续"美好生活"主题，展品涵盖玩具及孕婴童、时尚、家用纺织品、文具、健康休闲5大板块21个展区，展览面积51.5万平方米。展会现场外贸订单加速落地，广交会签下的意向协议正快速传导至企业生产车间，转化为出口订单并陆续发运。',
    },
    # 中非贸易 3121.1 亿美元：经贸 85（海关/商务部数据类）
    'news.cctv.com/2026/11/01/ARTIwmTjjDpSSZID2jIUtzWo261101.shtml': {
        'title': '今年前9个月中非贸易额达3121.1亿美元 同比增长22%',
        'source': '央视新闻',
        'date': '2026-11-01',
        'category': '经贸动向',
        'priority_score': 85,
        'is_summit_level': False,
        'summary': '今年前9个月，中非贸易额达3121.1亿美元，同比增长22%。在总量增长的同时，贸易结构持续优化，越来越多非洲特色农产品和消费品进入中国市场，丰富了中国消费者的选择。中非经贸合作在贸易、投资、基础设施等领域同步推进，成为南南合作的典范。',
    },
    # 委内瑞拉第二批救灾物资：部委 85，补足摘要
    'news.cctv.com/2026/11/01/ARTIz0ZSAv37t4Zni6CzjF92261101.shtml': {
        'title': '中国对委内瑞拉第二批人道主义救灾物资运抵卡贝略港',
        'source': '央视新闻',
        'date': '2026-11-01',
        'category': '部委动态',
        'priority_score': 85,
        'is_summit_level': False,
        'summary': '当地时间10月31日，中国政府援助委内瑞拉第二批人道主义救灾物资交接仪式在该国卡贝略港举行。本批援助物资总重约5000吨，包括1800套活动板房、87台重型车辆设备等，用于支持委内瑞拉震后重建与受灾民众安置。委内瑞拉6月24日接连发生两次强震，震级分别为7.2级和7.5级。',
    },
    # 中秘自贸协定（商务部司局负责人）：补真实摘要 + 事实化标题
    'mofcom.gov.cn/xwfb/sjfzrfb/art/2026/art_7338bac32107453b9462d434db2409b8.html': {
        'title': '中国—秘鲁自贸协定升级议定书11月1日正式生效 商务部介绍实施安排',
        'source': '商务部',
        'date': '2026-11-01',
        'category': '经贸动向',
        'priority_score': 85,
        'is_summit_level': False,
        'summary': '中国—秘鲁自贸协定升级议定书于2026年11月1日正式生效。中秘自贸协定于2009年4月签署，是我国与拉美国家签署的首个全面自贸协定；2018年11月双方宣布启动升级谈判，2024年6月实质性完成，2024年11月正式签署升级议定书。经过共同努力，双方均已完成各自国内程序，议定书如期生效。商务部表示，在当前国际形势下，这体现出两国共同维护多边主义和自由贸易的决心，升级议定书的实施将促进中秘经贸关系深入发展，丰富两国全面战略合作伙伴关系内涵，为双方企业创造更加有利的营商环境和贸易投资合作机会。',
    },
}

# URL 归一：FIX 键省略协议与 www 前缀，两侧统一走 key()
FIX = {key(k): v for k, v in FIX.items()}

fixed = []
for it in arr:
    f = FIX.get(key(it['url']))
    if not f:
        continue
    it.update(f)
    it['collectedAt'] = COLLECT
    fixed.append(it['title'])

# ---------- 补录清单 ----------
existing = {key(i['url']) for i in arr}
# 昨日版面（11-01）不存在的 11-01 内容可入今日版面
added = []


def add(url, title, source, date, category, score, summary, summit=False):
    if key(url) in existing:
        print('  ⏭ 已存在，跳过:', title[:30])
        return
    arr.append({
        'title': title, 'url': url, 'source': source, 'date': date,
        'category': category, 'priority_score': score, 'is_summit_level': summit,
        'summary': summary, 'collectedAt': COLLECT,
    })
    existing.add(key(url))
    added.append(title)


# 1 阿曼苏丹海赛姆抵京（11-01 晚）—— 元首级国事访问开启，今日将举行会谈
add('https://www.cnr.cn/newscenter/native/gd/20261101/t20261101_527859543.shtml',
    '阿曼苏丹海赛姆抵达北京 开启为期两天国事访问',
    '央广网', '2026-11-01', '元首动态', 100,
    '应国家主席习近平邀请，阿曼苏丹海赛姆11月1日晚乘机抵达北京首都国际机场，开启为期两天的国事访问。此次访问是海赛姆苏丹继任以来首次访华，也是中阿两国建交48年来阿曼国家元首首次访华，对促进双边关系发展具有重要意义。访问期间，习近平主席将同海赛姆苏丹举行会谈，就两国关系和共同关心的问题深入交换意见；李强总理将同海赛姆苏丹会见。中阿两国传统友谊深厚，近年来两国政治互信不断巩固、互利合作稳步推进、人文交流日益密切，在国际和地区事务中保持良好沟通。',
    summit=True)

# 2 G20 外长会（外交部原始正确路径 /wjbxw_new/）
add('https://www.mfa.gov.cn/wjbxw_new/202611/t20261101_12050885.shtml',
    '外交部副部长马朝旭出席二十国集团外长会 阐述中方全球安全与产供链主张',
    '外交部', '2026-11-01', '部委动态', 85,
    '10月30日至31日，外交部副部长马朝旭在美国亚特兰大出席二十国集团外长会。会议由2026年二十国集团轮值主席国美国国务卿鲁比奥主持，各方就地缘政治紧张局势、能源、供应链等议题深入讨论；因分歧严重，本次外长会未发表联合公报。马朝旭表示，当前国际形势深刻演变、地缘政治局势紧张、发展议程严重滞后，中方提出全球安全倡议，倡导共同、综合、合作、可持续的安全观，走对话而不对抗、结伴而不结盟、共赢而非零和的新型安全之路；二十国集团要担负应有责任，做维护世界和平稳定的力量，推动地区热点问题缓局降温。他强调保护主义没有赢家，搞筑墙设垒、脱钩断链只会扰乱全球产业链供应链稳定畅通，G20成员应深化政策协调、加强贸易畅通、挖掘创新赋能、推动普惠发展，防止将经贸问题政治化、武器化、泛安全化。马朝旭还就中东地区局势、乌克兰危机等阐述中方立场。')

# 3 乌镇峰会开幕（11-02）—— 我国主办的国际会议，网信办主线
add('https://cn.wicinternet.org/2026-09/30/content_39030205.htm',
    '2026年世界互联网大会乌镇峰会11月2日至5日举行 聚焦人工智能开源开放',
    '世界互联网大会', '2026-11-02', '重要会议', 88,
    '2026年世界互联网大会乌镇峰会于11月2日至5日在浙江乌镇举行，主题为"开源开放 共建共享——携手构建网络空间命运共同体"。峰会围绕人工智能开源开放发展的理念与实践，设置27场分论坛，主论坛设"人工智能乌镇对话"环节，邀请领军科技企业与开源大模型企业负责人就全球人工智能开源生态构建等议题展开讨论。"互联网之光"博览会同期举办，以"智能互联、智见未来"为主题，来自54个国家和地区的670余家企业参展，展示发布1000余项技术成果，20余款产品现场首发。峰会还首次面向公众推出"乌镇大讲堂""乌镇Talk·开源青年说"，并建设全国首个开源主题生态体验馆。')

# 4 前三季度社会物流总额 280.0 万亿元（国统口径行业数据，经贸 85）
add('https://www.gov.cn/yaowen/liebiao/202611/content_7084717.htm',
    '前三季度全国社会物流总额280.0万亿元 同比增长4.9%',
    '中国政府网·要闻', '2026-11-01', '经贸动向', 85,
    '中国物流与采购联合会11月1日发布2026年前三季度物流运行数据：全国社会物流总额280.0万亿元，按可比价格计算同比增长4.9%，装备制造业和高技术制造业引领作用突出，工业品物流总额同比增长5.3%、对社会物流总额增长贡献率达78%。社会物流总费用与GDP比率回落至13.8%、较上年同期下降0.2个百分点，全社会物流成本节约超2100亿元。物流业总收入达11.1万亿元、同比增长4.3%，9月物流业业务活动预期指数为56.2%、环比回升1.8个百分点。')

# 5 南水北调中线完成年度供水（水利部/南水北调集团）
add('https://news.youth.cn/gn/202611/t20261102_16944346.htm',
    '南水北调中线完成2025—2026年度供水任务 累计供水72.64亿立方米',
    '中国青年网（转人民日报）', '2026-11-02', '部委动态', 85,
    '记者从中国南水北调集团有限公司获悉：截至10月31日，南水北调中线工程完成2025—2026年度供水任务，年度累计向受水区河南、河北、北京、天津供水72.64亿立方米，工程惠及沿线27座大中城市，受益人口近1.18亿人。本年度中线工程在保证口门供水基础上，利用汛前及汛期富余水量，相机向沿线清河、贾峪河、滏阳河、七里河、泜河等15条河流及相关地区实施生态补水，超额完成水利部下达的夏季集中补水计划。2026—2027年度调水任务同步启动。')

# 6 "妈祖"海洋预报数值模式 2.0（自然资源部）
add('https://www.news.cn/tech/20261101/168023aec7ec46b3a1559d59804988d6/c.html',
    '我国自主研发"妈祖"海洋预报数值模式升级至2.0版本',
    '新华网', '2026-11-01', '部委动态', 85,
    '国家海洋环境预报中心11月1日在第十一届世界妈祖文化论坛上正式发布"妈祖"海洋预报数值模式2.0版本，标志着自然资源部组织实施的我国海洋预报"芯片"工程再获重大突破。经5年迭代攻关，"妈祖·海流"2.0发展了统一动力核心数值模拟技术，支持可变分辨率模拟，推动我国海洋环境预报向全球公里级分辨率迭代，并新增海冰、海洋生态模拟模块；"妈祖·海浪"2.0引入新的海浪成长与耗散物理方案，提升台风大浪过程模拟精度，拓展涌浪及最大波高预报场景，并实现国产信创设备适配。经院士专家评审，新版本海水温度、盐度和流速预报效果已达国际先进水平，海浪有效波高预报精度与国际权威模式相当，并已在"雪龙2"号科考船完成船载运行测试。')

# ---------- 全局清洗 ----------
def clean(s):
    if not s:
        return ''
    s = html.unescape(s)
    s = s.replace('\u00a0', ' ').replace('&nbsp;', ' ')
    s = re.sub(r'<[^>]+>', '', s)
    s = re.split(r'主办单位：|网站标识码|京ICP', s)[0]
    return re.sub(r'\s+', ' ', s).strip()


for it in arr:
    it['title'] = clean(it.get('title'))
    it['summary'] = clean(it.get('summary'))

# ---------- 断言：归档窗口 ----------
bad_date = [i['title'][:30] for i in arr if i['date'] < YDAY]
assert not bad_date, f'date<昨日: {bad_date}'
bad_col = [i['title'][:30] for i in arr if not (i.get('collectedAt') or '').startswith(TODAY)]
assert not bad_col, f'collectedAt 越界: {bad_col}'

# ---------- 排序 ----------
CAT_ORDER = ['元首动态', '高层动态', '重要会议', '人事任免', '政策发布', '部委动态', '经贸动向']
arr.sort(key=lambda x: (-x.get('priority_score', 0),
                        CAT_ORDER.index(x['category']) if x['category'] in CAT_ORDER else 9))
d['archive'][TODAY] = arr
d['todayCount'] = len(arr)
d['stats'] = {
    'totalArticles': sum(len(v) for v in d['archive'].values()),
    'dateCount': len(d['archive']),
    'latestDate': TODAY,
    'summitCount': sum(1 for i in arr if i.get('is_summit_level')),
}
d['lastUpdated'] = COLLECT

json.dump(d, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# ---------- 自检 ----------
print(f'== 后处理完成：{before} -> {len(arr)} 条（删 {len(deleted)} / 修正 {len(fixed)} / 补 {len(added)}）')
print('分类分布:', dict(Counter(i['category'] for i in arr)))
hi = sum(1 for i in arr if i.get('priority_score', 0) >= 85)
print(f'≥85 占比: {hi}/{len(arr)} = {hi * 100 // len(arr)}%')
print('100分条数:', sum(1 for i in arr if i.get('priority_score') == 100))
print('元首动态:', sum(1 for i in arr if i['category'] == '元首动态'))
print('无摘要:', [i['title'][:30] for i in arr if not i.get('summary')])
print('短摘要(<40):', [i['title'][:30] for i in arr if len(i.get('summary') or '') < 40])
print('摘要截断(…):', [i['title'][:30] for i in arr if (i.get('summary') or '').endswith('…')])
print('摘要含页脚:', [i['title'][:30] for i in arr if any(x in (i.get('summary') or '') for x in ('京ICP', '主办单位', '网站标识码'))])
print('摘要含"页面不存在":', [i['title'][:30] for i in arr if '页面不存在' in (i.get('summary') or '')])
print('collectedAt≠今日:', [i['title'][:30] for i in arr if not (i.get('collectedAt') or '').startswith(TODAY)])
print('date<昨日:', [i['title'][:30] for i in arr if i['date'] < YDAY])
print('标题<8字符:', [i['title'] for i in arr if len(i['title']) < 8])
urls = Counter(key(i['url']) for i in arr)
print('URL重复:', [u for u, c in urls.items() if c > 1])
titles = Counter(i['title'][:30] for i in arr)
print('标题重复:', [t for t, c in titles.items() if c > 1])
BAD = ('toutiao.com', '/163.com', 'sohu.com', 'news.qq.com', 'video.sina', 'baijiahao', 'zaobao.com')
print('黑名单域:', [i['url'] for i in arr if any(b in i['url'] for b in BAD)])
print('tv.cctv:', [i['title'][:20] for i in arr if 'tv.cctv.com' in i['url']])
print('日期括号残留:', [i['title'][:30] for i in arr if re.search(r'（2026年1[01]月\d+日）|\(2026-1', i['title'])])
print('== 删除清单:')
for t in deleted:
    print('  -', t[:58])
print('== 补录清单:')
for t in added:
    print('  +', t[:58])
print('== 最终版面:')
for n, i in enumerate(arr, 1):
    print(f"{n:2d} [{i['priority_score']:3d}] {i['category']} | {i['source']} | {i['date']} | {i['title'][:50]} [{len(i.get('summary') or '')}]")
