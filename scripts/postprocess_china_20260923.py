#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内新闻看板 LLM 质量后处理 2026-09-23（V5.8 规则）48 -> 定稿"""
import json, html, os
from collections import Counter

BASE = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50"
DATA = os.path.join(BASE, "data/china-news.json")
TODAY, YESTERDAY = "2026-09-23", "2026-09-22"
STAMP = "2026-09-23 09:35:00"
XI_KW = ["习近平", "国家主席", "中央军委主席", "总书记", "元首外交"]

d = json.load(open(DATA, encoding="utf-8"))
board = d["archive"][TODAY]
print("初抓:", len(board))

def is_summit(t):
    return any(k in t for k in XI_KW)

# ---------- 1) 删除 ----------
DEL_KEYS = [
    "咱们这个国家再现代化", "愿做跨越太平洋的友谊使者", "习近平主席引领推进中美人民友好事业的故事",
    "共同擘画中美关系新篇章", "推动中美关系迈向更美好未来",
    "深入学习贯彻习近平总书记重要回信精神",          # 人民日报版，与王小洪条同事件
    "美媒：习近平访美预计不率企业家代表团随行",
    "遇见习近平", "杨丹旭",
    "李强上海调研 强调纵深推进",
    "中国商务部：扩大开放为外企在华经营提供确定性", "中国工信部旗下平台",
    "为倒渣土抄近路损毁明长城", "外交部领事保护中心提醒",
    "据报中国调查DeepSeek", "据报DeepSeek本周将向联合国安理会",
    "“铁路运费票”物流金融产品上线", "到2030年 我国电气化率将跃居",
    "发票数据亮眼", "多点发力创新金融服务", "多项经济民生数据发布",
    "学习手记丨答好保障粮食安全", "守住管好“大国粮仓”",
    "国家发展改革委举行9月份新闻发布会",
    "李强会见世界技能组织主席和首席执行官",           # tv.cctv 版，并入综合条目
    "张国清出席2026年全国食品安全宣传周主场活动",      # tv.cctv 简版
    "习近平向第48届世界技能大赛致贺信",              # 已并入综合条目
    "习近平：鼓励引导更多青年人走技能成才之路",        # zaobao 版贺信，重复
    "李强会见世界技能组织主席乌汉和首席执行官霍伊",      # 已并入综合条目（同属世赛事件）
]
kept, removed = [], []
for x in board:
    if any(k in x.get("title", "") for k in DEL_KEYS):
        removed.append(x["title"]); continue
    kept.append(x)
print("删除:", len(removed))

def find(pred):
    for x in kept:
        if pred(x): return x
    return None

def upd(x, **kw):
    if x: x.update(kw)

# ---------- 2) 修改 ----------
upd(find(lambda i: "王小洪在全国公安机关视频会议" in i.get("title", "")),
    title="王小洪在全国公安机关视频会议上强调 坚决扛牢守百姓幸福护家国平安重任",
    category="高层动态", priority_score=95, is_summit_level=False, source="中国政府网·要闻",
    url="https://www.gov.cn/yaowen/liebiao/202609/content_7081810.htm", date=YESTERDAY,
    summary="全国公安机关视频会议22日召开，中共中央书记处书记、公安部部长王小洪出席并讲话。他强调，要深入学习贯彻习近平总书记给福建省“漳州110”全体队员重要回信精神，坚定拥护“两个确立”、坚决做到“两个维护”，坚持人民至上，坚决扛牢守百姓幸福、护家国平安的重任。会议要求深入推进夏季治安打击整治行动，严打突出违法犯罪，严密社会面整体防控，深化公共安全治理，为人民群众欢度中秋国庆营造安全稳定环境。")

upd(find(lambda i: "丁薛祥会见哈萨克斯坦第一副总理" in i.get("title", "")),
    title="丁薛祥会见哈萨克斯坦第一副总理纳利巴耶夫",
    source="中国政府网·要闻", url="https://www.gov.cn/yaowen/liebiao/202609/content_7081779.htm",
    summary="中共中央政治局常委、国务院副总理丁薛祥22日下午在北京会见哈萨克斯坦第一副总理纳利巴耶夫。丁薛祥表示，中哈是山水相连、命运与共的好邻居、好朋友、好伙伴。今年7月习近平主席同托卡耶夫总统再次会晤，为中哈关系发展作出新部署。中方愿同哈方落实好两国元首重要共识，加强发展战略对接，深化能源、经贸、互联互通、人文等领域合作。纳利巴耶夫表示，哈方坚定恪守一个中国原则，愿同中方深化务实合作，共同办好哈中合作委员会相关会议。")

upd(find(lambda i: i.get("title", "").startswith("李强会见世界技能组织主席乌汉")),
    title="李强会见世界技能组织主席乌汉和首席执行官霍伊",
    source="中国政府网·要闻", url="https://www.gov.cn/yaowen/liebiao/202609/content_7081778.htm",
    summary="国务院总理李强22日下午在上海会见来华出席第48届世界技能大赛的世界技能组织主席乌汉和首席执行官霍伊。李强表示，举办第48届世界技能大赛是习近平主席亲自关心、亲自推动的，中方有信心向世界奉献一届精彩盛会。中国愿同世界技能组织加强合作，推动技能领域国际交流，让技能更好促进发展和民生。乌汉和霍伊表示，世界技能组织高度赞赏中国对技能事业的重视和投入，愿同中方深化合作，共同推动全球技能事业发展。")

upd(find(lambda i: "李强在上海调研时强调" in i.get("title", "")),
    title="李强在上海调研时强调 加快培育壮大新兴产业和未来产业 持续做大做强先进制造业",
    source="中国政府网·要闻", url="https://www.gov.cn/yaowen/liebiao/202609/content_7081777.htm",
    summary="中共中央政治局常委、国务院总理李强9月22日在上海调研。他强调，要深入贯彻落实习近平总书记关于发展先进制造业的重要指示和全国先进制造业大会精神，坚持创新驱动，加快培育壮大新兴产业和未来产业，持续做大做强先进制造业，为高质量发展提供坚实支撑。李强先后来到上海人工智能实验室、中国商飞上海飞机制造有限公司等地，了解技术攻关、成果转化和产业应用情况，并召开座谈会听取意见建议。")

upd(find(lambda i: "张国清在出席2026年全国食品安全宣传周" in i.get("title", "")),
    title="张国清在出席2026年全国食品安全宣传周主场活动时强调 深化食品安全全链条监管 以严管严治提升监管质效",
    source="中国政府网·要闻", url="https://www.gov.cn/yaowen/liebiao/202609/content_7081767.htm",
    summary="2026年全国食品安全宣传周主场活动22日在京举办，中共中央政治局委员、国务院副总理张国清出席并讲话。他强调，要深入贯彻习近平总书记关于食品安全的重要论述，落实“四个最严”要求，深化食品安全全链条监管，以严管严治提升监管质效。要强化源头治理和过程监管，严把从农田到餐桌的每一道防线；加大重点领域突出问题整治力度，严惩重处违法犯罪行为；压紧压实属地管理和企业主体责任，推动食品安全形势持续稳定向好。")

upd(find(lambda i: "韩正会见柬埔寨国王" in i.get("title", "")),
    title="韩正会见柬埔寨国王西哈莫尼和太后莫尼列", source="外交部", date=YESTERDAY,
    url="https://www.mfa.gov.cn/web/wjdt_674879/gjldrhd_674881/202609/t20260922_12028499.shtml",
    summary="9月22日，国家副主席韩正在北京会见柬埔寨国王西哈莫尼和太后莫尼列。韩正转达了习近平主席和夫人彭丽媛的亲切问候和良好祝愿，表示中柬铁杆友谊由中国老一辈领导人和西哈努克太皇共同缔造和精心培育，历久弥坚。中方愿同柬方落实好两国领导人重要共识，深化各领域务实合作，办好“中柬人文交流年”活动，推动中柬命运共同体建设走深走实。西哈莫尼和莫尼列感谢中方长期以来的宝贵支持，表示柬方坚定奉行一个中国政策，愿同中方携手深化柬中全面战略合作伙伴关系。")

upd(find(lambda i: "2026年9月22日外交部发言人郭嘉昆" in i.get("title", "")),
    title="2026年9月22日外交部发言人郭嘉昆主持例行记者会",
    category="部委动态", priority_score=85, is_summit_level=False, source="外交部",
    url="https://www.mfa.gov.cn/web/fyrbt_673021/jzhsl_673025/202609/t20260922_12028748.shtml",
    summary="外交部发言人郭嘉昆22日主持例行记者会。他宣布：国家副主席韩正将于9月24日至26日赴纽约出席第81届联合国大会一般性辩论，与会期间将出席中方举办的全球发展倡议5周年高级别对话会；第48届世界技能大赛9月22日至27日在上海举行，第五届全球数字贸易博览会9月23日至27日在杭州举行，马来西亚总理安瓦尔、吉尔吉斯斯坦总理卡瑟马利耶夫等将出席有关活动。答问环节，郭嘉昆就中美经贸磋商讨论建立人工智能对话机制、美方对伊朗航空制裁、第23届东博会与平陆运河合作前景、中美建设性战略稳定等作出回应，重申中方一贯反对没有国际法依据、没有联合国安理会授权的非法单边制裁。")

upd(find(lambda i: "宋朝华" in i.get("title", "")),
    title="四川省人大常委会原副主任宋朝华受贿1.48亿余元 一审被判死缓",
    category="人事任免", priority_score=87, is_summit_level=False, source="中国新闻网", date=YESTERDAY,
    url="https://www.chinanews.com/gn/2026/09-22/10701550.shtml",
    summary="9月22日，贵州省贵阳市中级人民法院一审公开宣判四川省人大常委会原党组成员、副主任宋朝华受贿案，对宋朝华以受贿罪判处死刑，缓期二年执行，剥夺政治权利终身，并处没收个人全部财产；受贿所得财物及孳息依法追缴。法院查明，1993年至2025年，宋朝华利用担任大邑县委书记、新津县委书记、成都市成华区委书记、眉山市市长、南充市委书记、四川省人大常委会副主任等职务便利，为相关单位和个人在企业经营、项目承揽等事项上提供帮助，非法收受财物共计折合人民币1.48亿余元。鉴于其有未遂情节、如实供述、认罪悔罪、积极退赃，判处死刑可不立即执行。")

upd(find(lambda i: "查处违反中央八项规定精神问题29171起" in i.get("title", "")),
    title="2026年8月全国查处违反中央八项规定精神问题29171起",
    category="人事任免", priority_score=87, is_summit_level=False, source="央视新闻",
    summary="9月22日，中央纪委国家监委公布2026年8月全国查处违反中央八项规定精神问题汇总情况。8月，全国共查处违反中央八项规定精神问题29171起，批评教育和处理37495人，其中党纪政务处分24071人。从查处问题类型看，履职尽责、服务经济社会发展和生态环境保护方面不担当、不作为、乱作为、假作为问题，以及违规收送名贵特产和礼品礼金、违规吃喝问题较为突出。中央纪委国家监委强调，要持续紧盯节点、常抓不懈，对顶风违纪行为严查快处，推动作风建设常态化长效化。")

upd(find(lambda i: "马来西亚总理安瓦尔等外国领导人将出席" in i.get("title", "")),
    title="马来西亚总理安瓦尔等外国领导人将出席第48届世界技能大赛和第五届全球数字贸易博览会",
    category="高层动态", priority_score=95, is_summit_level=False, source="人民日报", date=YESTERDAY,
    summary="外交部发言人9月22日宣布：第48届世界技能大赛将于9月22日至27日在上海举行，第五届全球数字贸易博览会将于9月23日至27日在浙江杭州举行。应中方邀请，马来西亚总理安瓦尔将出席世界技能大赛开幕式和全球数字贸易博览会启动仪式，吉尔吉斯斯坦总理卡瑟马利耶夫将出席全球数字贸易博览会启动仪式。")

upd(find(lambda i: "雪克来提" in i.get("title", "")),
    title="雪克来提·扎克尔出席全球可持续交通高峰论坛（2026）开幕式、跨里海国际运输走廊高级别会议",
    source="人民日报", category="高层动态", priority_score=95, is_summit_level=False,
    summary="全国人大常委会副委员长雪克来提·扎克尔22日在京出席全球可持续交通高峰论坛（2026）开幕式、跨里海国际运输走廊高级别会议并致辞。他表示，中方愿同各方一道落实元首外交重要共识，持续推进全球交通互联互通，深化跨里海国际运输走廊务实合作，共同维护国际物流供应链稳定畅通，为促进区域经济发展和民生改善注入新动力。")

upd(find(lambda i: "2026北京文化论坛开幕" in i.get("title", "")),
    title="2026北京文化论坛开幕 李书磊出席并发表主旨演讲",
    category="高层动态", priority_score=95, is_summit_level=False, source="央视新闻",
    summary="2026北京文化论坛22日在京开幕，中共中央政治局委员、中宣部部长李书磊出席并发表主旨演讲。李书磊指出，要深入学习贯彻习近平文化思想，坚持守正创新，推动文化传承发展，促进文明交流互鉴。论坛以“传承·创新·互鉴”为主题，中外嘉宾围绕文化遗产保护、数字文化发展、文明交流互鉴等议题展开研讨。")

upd(find(lambda i: "轻工纺织产业发展“十五五”规划" in i.get("title", "")),
    title="工信部等三部门印发《轻工纺织产业发展“十五五”规划》",
    category="政策发布", priority_score=80, is_summit_level=False, source="中国政府网",
    url="https://www.gov.cn/zhengce/zhengceku/202609/content_7081805.htm",
    summary="工业和信息化部、国家发展改革委、商务部联合印发《轻工纺织产业发展“十五五”规划》。规划提出，轻工纺织产业是国民经济传统优势产业和重要民生产业，“十五五”时期要以高端化、智能化、绿色化为方向，加快关键技术攻关和数字化转型，培育一批世界级产业集群和知名品牌。规划明确，到2030年轻工纺织产业规模以上企业营业收入有望超过30万亿元，在稳增长、促就业、扩消费、惠民生等方面发挥更重要作用。")

upd(find(lambda i: "凌激赴北京市开展调研" in i.get("title", "")),
    title="商务部副部长凌激赴北京调研并主持召开外资企业圆桌会",
    category="经贸动向", priority_score=85, is_summit_level=False, source="商务部",
    summary="商务部副部长兼国际贸易谈判副代表凌激近日赴北京市开展调研并主持召开外资企业圆桌会。凌激实地了解外资企业经营发展情况，听取企业意见建议，表示中国坚定不移推进高水平对外开放，将持续优化营商环境，为外资企业在华经营提供更多确定性和便利。针对企业提出的问题，商务部将逐项梳理、推动解决，并会同有关部门落实好外资企业国民待遇，保障外资企业依法平等参与政府采购和标准制定，支持外资企业深耕中国市场、共享发展机遇。")

upd(find(lambda i: "王文涛部长会见德国汽车工业协会主席穆勒" in i.get("title", "")),
    title="王文涛部长会见德国汽车工业协会主席穆勒",
    category="经贸动向", priority_score=85, is_summit_level=False, source="商务部",
    summary="商务部部长王文涛9月22日会见德国汽车工业协会主席穆勒，双方就中德汽车产业合作、欧盟对华电动汽车贸易措施等问题交换意见。王文涛表示，中国汽车市场开放度高，欢迎包括德国企业在内的各国企业扩大在华投资合作。中方始终主张通过对话磋商妥善处理经贸分歧，反对将经贸问题政治化、泛安全化。希望德国汽车工业协会发挥积极作用，推动欧方秉持理性务实态度，共同维护中德、中欧汽车产业互利共赢的合作格局。")

upd(find(lambda i: "北斗产业规模5年内超万亿元" in i.get("title", "")),
    title="我国将推动北斗产业规模5年内超万亿元",
    category="经贸动向", priority_score=85, is_summit_level=False, source="人民日报",
    summary="记者从国家发展改革委获悉：2025年我国北斗产业总体产值突破6290亿元，北斗产业企事业单位达3万多家，从业人员超200万人。“十五五”时期，我国将推动北斗产业规模5年内突破1万亿元，加快北斗与人工智能、大数据、低空经济等融合发展，拓展在智能交通、精准农业、防灾减灾、大众消费等领域的规模化应用，持续提升北斗系统服务性能和产业国际竞争力。")

upd(find(lambda i: "RCEP" in i.get("title", "") or "区域全面经济伙伴关系协定" in i.get("title", "")),
    title="RCEP生效实施后第五次部长级会议在菲律宾马尼拉举行",
    category="经贸动向", priority_score=85, is_summit_level=False, source="商务部",
    summary="9月21日，《区域全面经济伙伴关系协定》（RCEP）生效实施后第五次部长级会议在菲律宾马尼拉举行。会议回顾RCEP实施成效，就进一步推动协定全面高质量实施、提升区域经济一体化水平等议题交换意见。中方表示，RCEP生效以来持续释放制度红利，为区域贸易投资增长提供了有力支撑；中方愿与各方一道，推动协定升级和扩员，维护多边主义和自由贸易，共同构建更加开放、包容、平衡、共赢的区域经济格局。")

upd(find(lambda i: "习特二会" in i.get("title", "")),
    title="“习特二会”前中美对延长贸易休战有分歧 在稀土问题拉锯",
    category="经贸动向", priority_score=85, is_summit_level=False, source="联合早报",
    summary="据联合早报报道，在习近平主席即将对美国进行国事访问前夕，中美双方对延长贸易休战安排仍存分歧，并在稀土供应问题上持续拉锯。报道称，美方希望中方进一步放宽稀土出口管制并扩大农产品和能源采购，中方则要求美方取消单边加征关税、放宽对华科技出口限制。两国经贸团队已在纽约举行磋商，并就人工智能有关问题开展对话，外界关注中美元首会晤能否就延长休战达成阶段性安排。")

# 全量 HTML 实体清洗
for x in kept:
    for f in ("title", "summary"):
        if x.get(f):
            x[f] = html.unescape(x[f]).replace("\u00a0", " ").strip()

# ---------- 3) 综合条目：第48届世界技能大赛 ----------
syn = find(lambda i: "第48届世界技能大赛在上海隆重开幕" in i.get("title", ""))
upd(syn, title="第48届世界技能大赛在上海开幕 习近平致贺信 李强出席并宣布开幕",
    category="元首动态", priority_score=100, is_summit_level=True,
    source="中国政府网·要闻（综合）", date=TODAY,
    url="https://www.gov.cn/yaowen/liebiao/202609/content_7081833.htm",
    summary="9月22日，国家主席习近平向第48届世界技能大赛致贺信，指出新一轮科技革命和产业变革加速突破给全球技能发展带来深刻影响，世界技能大赛紧密对接产业需求，为各国技能人才精进技艺、互学互鉴搭建了有益平台，鼓励引导更多青年人走技能成才、技能报国之路。22日下午，国务院总理李强在上海会见来华出席大赛的世界技能组织主席乌汉和首席执行官霍伊，表示举办第48届世界技能大赛是习近平主席亲自关心、亲自推动的，中方有信心向世界奉献一届精彩盛会。当晚，第48届世界技能大赛在上海隆重开幕，开幕式上宣读了习近平主席的贺信，李强出席并宣布开幕。大赛于9月22日至27日举行，应中方邀请，马来西亚总理安瓦尔等外国领导人出席开幕式。")
print("综合条目: 第48届世界技能大赛")

# ---------- 4) 补录 ----------
ADD = [
 dict(category="元首动态", priority_score=100, date=YESTERDAY, source="中国政府网·要闻",
      title="习近平向全国广大农民和工作在“三农”战线上的同志们致以节日祝贺和诚挚问候",
      url="https://www.gov.cn/yaowen/liebiao/202609/content_7081753.htm",
      summary="在第九个“中国农民丰收节”到来之际，中共中央总书记、国家主席、中央军委主席习近平代表党中央，向全国广大农民和工作在“三农”战线上的同志们致以节日祝贺和诚挚问候。习近平指出，今年我国夏粮产量再创新高，早稻保持稳产，秋粮丰收在望。习近平强调，各级党委和政府要认真贯彻党中央决策部署，扎实推进乡村全面振兴，提高强农惠农富农政策效能，着力提升农业综合生产能力和质量效益，拓宽农民增收致富渠道，因地制宜建设宜居宜业和美乡村，努力让广大农民生活更加幸福美好。"),
 dict(category="高层动态", priority_score=95, date=YESTERDAY, source="外交部",
      title="韩正将出席第81届联合国大会一般性辩论",
      url="https://www.mfa.gov.cn/web/wjdt_674879/wsrc_674883/202609/t20260922_12028387.shtml",
      summary="外交部发言人9月22日宣布：国家副主席韩正将于9月24日至26日赴纽约出席第81届联合国大会一般性辩论。与会期间，韩正副主席将出席中方举办的全球发展倡议5周年高级别对话会，会见联合国秘书长、第81届联大主席及有关国家领导人。今年是新中国恢复联合国合法席位55周年，中方将全面阐释对当前国际形势、重大国际和地区问题以及联合国工作的看法主张，推动国际社会重振联合国权威与作用，汇聚改革完善全球治理的更大合力。"),
 dict(category="重要会议", priority_score=88, date=YESTERDAY, source="中国政府网·要闻",
      title="国新办“开局起步‘十五五’”发布会：安全高效永续利用自然资源",
      url="https://www.gov.cn/yaowen/liebiao/202609/content_7081825.htm",
      summary="国务院新闻办22日举行“开局起步‘十五五’”系列主题新闻发布会，介绍促进自然资源安全高效永续利用有关情况。发布会介绍，“十五五”时期将严守耕地和生态保护红线，全国重点区域生态保护红线保护成效显著；推动发展动力从“土地财政”转向“时空经济”，深化自然资源资产产权制度改革，健全自然资源有偿使用制度，提升资源要素配置效率和保障能力，为高质量发展提供空间和资源支撑。"),
 dict(category="人事任免", priority_score=86, date=TODAY, source="人民网",
      title="西藏等3省区党委主要负责同志职务调整",
      url="https://politics.people.com.cn/n1/2026/0923/c461001-40803805.html",
      summary="日前，中共中央决定：胡昌升同志任西藏自治区党委委员、常委、书记，不再担任甘肃省委书记、常委、委员职务；王君正同志不再担任西藏自治区党委书记、常委、委员职务。吴晓军同志任甘肃省委委员、常委、书记，不再担任青海省委书记、常委、委员职务。罗东川同志任青海省委书记。"),
 dict(category="部委动态", priority_score=85, date=YESTERDAY, source="中国政府网",
      title="2026年全国国庆文化和旅游消费月启动 发放超3.1亿元消费券",
      url="https://www.gov.cn/lianbo/202609/content_7081774.htm",
      summary="2026年全国国庆文化和旅游消费月22日启动，主场活动在云南弥勒举行。消费月从9月下旬持续至10月底，各地将举办超过2万场次文旅活动，发放超3.1亿元消费券等消费补贴，推出景区门票减免、演出票务优惠、旅游线路折扣等惠民举措，为居民和游客提供更丰富的选择和体验，进一步释放文化和旅游消费潜力。"),
 dict(category="部委动态", priority_score=85, date=YESTERDAY, source="中国政府网",
      title="生态环境部：推动固体废物和新污染物治理取得新成效",
      url="https://www.gov.cn/lianbo/202609/content_7081817.htm",
      summary="生态环境部22日介绍，将推动固体废物和新污染物治理取得新成效。“十五五”时期将持续推进“无废城市”建设，加强危险废物、医疗废物、尾矿等风险防控，深化塑料污染全链条治理；落实新污染物治理行动方案，推进化学物质环境风险筛查评估和管控，强化源头准入和过程监管，切实防范环境与健康风险。"),
 dict(category="政策发布", priority_score=80, date=YESTERDAY, source="中国政府网",
      title="《非物质文化遗产保护传承“十五五”规划》印发 明确六方面重点任务",
      url="https://www.gov.cn/lianbo/202609/content_7081710.htm",
      summary="文化和旅游部近日印发《非物质文化遗产保护传承“十五五”规划》，提出到2030年初步形成非遗系统性保护新格局，非遗融入现代生活的广度、深度不断提升。规划明确六方面重点任务：巩固保护基础，完善非遗项目保护体系；增强传承能力，优化非遗传承人才培育体系；服务国家重大战略，融入文化遗产大保护格局；激活发展潜力，搭建非遗融入现代生活新场景；深化科技赋能，提升数智化保护水平；增强传播效能，提高非遗传播力影响力。规划还就推进修订非物质文化遗产法、建立全国非遗保护工作者轮训机制等作出安排。"),
 dict(category="政策发布", priority_score=80, date=YESTERDAY, source="商务部",
      title="商务部等5部门调整《向特定国家（地区）出口易制毒化学品管理目录》 新增2个管制品种",
      url="https://www.mofcom.gov.cn/zcfb/blgg/art/2026/art_de33e6b9aacc459082dc7aa3b4c7c1d6.html",
      summary="商务部、公安部、应急管理部、海关总署、国家药监局9月22日发布公告（商务部公告2026年第40号），对《向特定国家（地区）出口易制毒化学品管理目录》进行调整，新增1-苯乙基-4-氧-3-哌啶甲酸甲酯、1-苯乙基-4-氧-3-哌啶甲酸乙酯等2个品种至附件1第一部分。自公告发布之日起，向美国、墨西哥、加拿大出口附件1第一部分所列化学品的，向缅甸、老挝、阿富汗出口附件1第二部分所列化学品的，应按照《向特定国家（地区）出口易制毒化学品暂行管理规定》申请许可。"),
 dict(category="政策发布", priority_score=80, date=YESTERDAY, source="央视新闻",
      title="我国将在10个行业开展数据资源开发利用攻坚行动",
      url="https://news.cctv.cn/2026/09/22/ARTIFwD28NfXynFh2FArcKgu260922.shtml",
      summary="国家数据局22日介绍，国家层面将推出新举措，重点在工业制造、医疗健康、金融服务、交通物流、现代农业、能源电力、文化旅游、教育、商贸流通、公共事业10个行业开展数据资源开发利用攻坚行动。将加快推动国家数据基础制度在地方和重点行业落地，鼓励组建行业数据创新联合体，围绕行业高价值场景推动公共数据与企业数据、社会数据融合应用，构建符合人工智能发展需求的治数用数模式，创新数据、模型、智能体一体化服务能力。首轮攻坚任务率先在安徽启动，重点围绕汽车和医疗健康两个行业展开。"),
 dict(category="经贸动向", priority_score=85, date=YESTERDAY, source="商务部",
      title="第25次中国—东盟经贸部长会议在马尼拉召开",
      url="https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_3c9cf44ef54744279950e0221e8fedeb.html",
      summary="9月21日，第25次中国—东盟经贸部长会议在东盟轮值主席国菲律宾首都马尼拉举行，商务部副部长鄢东与菲律宾贸工部长罗克共同主持，东盟国家经贸部门负责人和东盟秘书长出席。会议围绕全球和区域经济形势、中国—东盟经贸合作发展方向、自贸区建设等议题深入交换意见。鄢东表示，中国的经济发展将继续为东盟带来“中国机遇2.0”，中方愿与东盟方坚持开放合作，携手应对单边主义和保护主义。东盟方表示，中国连续17年保持为东盟最大贸易伙伴，期待《中国—东盟自贸区3.0版升级议定书》尽早生效。"),
 dict(category="经贸动向", priority_score=85, date=YESTERDAY, source="商务部",
      title="王文涛部长与欧洲汽车工业协会主席康林松举行视频通话",
      url="https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_e99e2aed4ac744fea702d63c7e96a2ac.html",
      summary="商务部部长王文涛9月22日与欧洲汽车工业协会主席康林松举行视频通话，就中欧汽车产业合作、欧盟对华电动汽车贸易措施等交换意见。王文涛表示，中欧汽车产业互补性强、合作基础深厚，中方始终主张通过对话磋商妥善解决经贸分歧，反对滥用贸易救济措施。希望欧洲汽车工业协会发挥建设性作用，推动欧方秉持理性务实态度，共同维护中欧汽车产业互利共赢格局，为全球绿色转型作出贡献。"),
 dict(category="经贸动向", priority_score=85, date=TODAY, source="人民日报",
      title="我国将推动北斗产业规模5年内超万亿元",
      url="http://paper.people.com.cn/rmrb/pc/content/202609/23/content_30182630.html",
      summary="记者从国家发展改革委获悉：2025年我国北斗产业总体产值突破6290亿元，北斗产业企事业单位达3万多家，从业人员超200万人。“十五五”时期，我国将推动北斗产业规模5年内突破1万亿元，加快北斗与人工智能、大数据、低空经济等融合发展，拓展在智能交通、精准农业、防灾减灾、大众消费等领域的规模化应用，持续提升北斗系统服务性能和产业国际竞争力。"),
]
have = {x.get("url") for x in kept}
added = 0
for a in ADD:
    if a["url"] in have:
        print("跳过(URL已存在):", a["title"][:36]); continue
    a.update(is_summit_level=is_summit(a["title"]), collectedAt=STAMP)
    kept.append(a); added += 1
print("补录:", added)

# ---------- 5) 校验 ----------
hist = set()
for dt, arr in d["archive"].items():
    if dt != TODAY:
        hist |= {it.get("url") for it in arr}
dup = [x for x in kept if x.get("url") in hist]
if dup:
    print("⚠️ 与历史版面重复，剔除:", [x["title"][:40] for x in dup])
    kept = [x for x in kept if x.get("url") not in hist]

for x in kept:
    x.pop("priority", None)
bad = [x for x in kept if x.get("collectedAt", "")[:10] != TODAY or x.get("date", "") < YESTERDAY]
print("归档违规:", len(bad))
for b in bad: print("   !", b.get("collectedAt"), b.get("date"), b.get("title")[:40])

seen, final = set(), []
for x in kept:
    k = (x.get("title", "")[:30], x.get("source", ""))
    if k in seen:
        print("去重:", x.get("title")[:50]); continue
    seen.add(k); final.append(x)

ORDER = {"元首动态":0,"高层动态":1,"重要会议":2,"人事任免":3,"部委动态":4,"政策发布":5,"经贸动向":6}
final.sort(key=lambda x: (ORDER.get(x.get("category"), 9), -(x.get("priority_score") or 0)))

d["archive"][TODAY] = final
d["todayCount"] = len(final)
d["lastUpdated"] = "2026-09-23 09:35"
d["stats"]["totalArticles"] = sum(len(v) for v in d["archive"].values())
d["stats"]["dateCount"] = len(d["dates"])
d["stats"]["latestDate"] = TODAY
d["stats"]["summitCount"] = sum(1 for v in d["archive"].values() for x in v if x.get("is_summit_level"))
json.dump(d, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

n = len(final)
hi = sum(1 for x in final if (x.get("priority_score") or 0) >= 85)
print(f"\n=== 定稿 {n} 条 ===")
print(Counter(x.get("category") for x in final).most_common())
print(f"≥85: {hi}/{n} = {round(hi/n*100)}%")
print("无摘要:", [x["title"][:36] for x in final if not x.get("summary")])
print("日期:", Counter(x.get("date") for x in final).most_common())
print("is_summit:", [x["title"][:36] for x in final if x.get("is_summit_level")])
for i, x in enumerate(final, 1):
    print(f"{i:2d} [{x.get('category')}] {x.get('priority_score')} {x.get('date')} | {x.get('title')[:54]} | {x.get('source')}")
