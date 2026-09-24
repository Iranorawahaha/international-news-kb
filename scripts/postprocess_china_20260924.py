# -*- coding: utf-8 -*-
"""
国内看板 LLM 质量后处理 —— 2026-09-24 版面
42 条初抓 → 删 32 / 修 10 / 补录 8 → 18 条
规则依据：.workbuddy/memory/boards/china.md（V5.8）+ V2.11 归档窗口
"""
import json, html, shutil, os, sys

BASE = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50"
JSON = os.path.join(BASE, "data/china-news.json")
TODAY = "2026-09-24"

shutil.copy(JSON, JSON + ".bak-20260924-pre")

with open(JSON, encoding="utf-8") as f:
    data = json.load(f)

items = data["archive"][TODAY]
print("初抓:", len(items))

# ---------------- 1. 删除（URL 精确匹配） ----------------
DELETE = [
    # 元首栏目体 / 视觉产品 / 故事类
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081860.htm",          # 中美人民友好事业的故事
    "https://news.cctv.com/2026/09/23/ARTIUrzsW3sCiWR4LbgAZ5xg260923.shtml",  # 此行间·100秒
    "https://news.cctv.com/2026/09/24/ARTIJ1vmTCwp7rHYr0dQXMf2260924.shtml",  # 大国外交进行时（预热）
    # 习近平访美 同源重复（留 gov.cn 官方版）
    "https://www.zaobao.com/news/china/story20260924-9725916",  # 抵美 蔡奇王毅随行
    "https://www.zaobao.com/news/china/story20260924-9725991",  # 抵美书面讲话
    "https://www.zaobao.com/news/china/story20260923-9724389",  # 赴美 特朗普接机
    "https://www.zaobao.com/news/china/story20260923-9722951",  # 今下午离京
    "https://news.cctv.com/2026/09/24/ARTI7MruZSDsGh0koErYQp7r260924.shtml",  # 抵达华盛顿 央视简版
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081944.htm",           # 书面讲话全文（并入抵美综合条目）
    # 世赛（9-23 版面综合条目已覆盖）
    "https://tv.cctv.com/2026/09/23/VIDEcSaqyCt1Ym3RFLVxYqRV260923.shtml",    # 致贺信
    "https://tv.cctv.com/2026/09/23/VIDEO3EhJPBxdFH6LQS2TEyl260923.shtml",   # 世界技能大会开幕式
    "https://tv.cctv.com/2026/09/23/VIDE8YYXG6lM80jmlIQkgZhO260923.shtml",   # 世赛开幕
    "https://news.cctv.com/2026/09/23/ARTIFKdAwJ4POIp52Gdxrs97260923.shtml",  # 职业奥林匹克看点
    # 学习活动 / 访谈反响 / 栏目体
    "http://paper.people.com.cn/rmrb/pc/content/202609/24/content_30182834.html",  # 地方人大常委会学习班
    "http://paper.people.com.cn/rmrb/pc/content/202609/24/content_30182821.html",  # "美中两国都将受益"访谈
    "https://news.cctv.com/2026/09/23/ARTIZCLeZHhjqoIXTT0mKnTO260923.shtml",  # 活力中国调研行
    # 数据综述栏目体（同 9-23 发票数据删除口径）
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081899.htm",           # 前8个月工业经济（发票数据）
    "https://news.cctv.com/2026/09/23/ARTIsujCV3JjEOSIV7ctWnCp260923.shtml",  # 民营经济成绩单综述
    # 涉台 / 台湾事务
    "https://www.zaobao.com/news/china/story20260923-9722669",  # 台湾捐菲海巡舰
    "https://www.zaobao.com/news/china/story20260923-9724102",  # 国台办中秋联谊
    "https://www.zaobao.com/news/china/story20260923-9723753",  # 萧美琴 AI
    # 记者会子稿（并入记者会主稿）
    "https://news.cctv.com/2026/09/23/ARTIpRpE4fAKOV9Hm2jxd5Wd260923.shtml",
    "https://news.cctv.com/2026/09/23/ARTIxYsLHCs0rgtfVRcJLGPk260923.shtml",
    # 同政策解读稿（9-23 版面已收《轻工纺织产业发展"十五五"规划》）
    "https://news.cctv.com/2026/09/23/ARTII4FuDf5oAUQ6TbRYZxQ8260923.shtml",
    # 产业综述 / 股市 / 地方软稿 / 蹲点故事化
    "https://news.cctv.com/2026/09/23/ARTIqzZv1IxuPNGFLmD2WlGK260923.shtml",  # 新能源汽车引领合作
    "https://www.zaobao.com/news/china/story20260923-9723208",               # 中国AI股走势
    "https://news.cctv.com/2026/09/24/ARTIQuBYIqnUHRYyX2nighhk260924.shtml", # 亚运赛场中国制造
    "https://news.cctv.com/2026/09/23/ARTIGuvLaOFDliH4iNkrkphb260923.shtml", # 粮袋子钱袋子
    "https://www.zaobao.com/news/china/story20260923-9724348",               # 央行流动性（例行操作）
    "http://paper.people.com.cn/rmrb/pc/content/202609/24/content_30182815.html",  # 大连氢能
    "https://news.cctv.com/2026/09/23/ARTIxUIPAOLTcq7F3YwXLVzC260923.shtml", # 钢铁产业综述
    "https://news.cctv.com/2026/09/24/ARTIm3hXwbyTVSiTPHhxpFyi260923.shtml", # 鲜食玉米
]

keep, removed = [], []
for it in items:
    if it.get("url") in DELETE:
        removed.append(it["title"][:44])
    else:
        keep.append(it)
print("删除:", len(removed), "剩余:", len(keep))
for r in removed:
    print("   -", r)

# ---------------- 2. 修正 ----------------
by_url = {it["url"]: it for it in keep}

def upd(key, **kw):
    it = by_url.get(key)
    if not it:
        print("  !! 未找到待修正条目:", key)
        return
    it.update(kw)

# [离京] tv.cctv → gov.cn 原文
upd("https://tv.cctv.com/2026/09/23/VIDEixpLN7ffuej9bmZeKDaG260923.shtml",
    url="https://www.gov.cn/yaowen/liebiao/202609/content_7081886.htm",
    source="中国政府网·要闻",
    title="习近平离京对美国进行国事访问",
    summary="9月23日下午，国家主席习近平乘专机离开北京，应美国总统特朗普邀请，对美国进行国事访问。"
            "陪同习近平出访的有：习近平主席夫人彭丽媛，中共中央政治局常委、中央办公厅主任蔡奇，"
            "中共中央政治局委员、外交部部长王毅等。")

# [抵美] 综合条目（报道 + 书面讲话合并，贯通叙述）
upd("https://www.gov.cn/yaowen/liebiao/202609/content_7081919.htm",
    source="中国政府网·要闻（综合）",
    title="习近平抵达华盛顿对美国进行国事访问",
    summary="当地时间9月23日下午，国家主席习近平乘专机抵达华盛顿安德鲁斯空军基地，应美国总统特朗普邀请"
            "对美国进行国事访问。特朗普和夫人梅拉尼娅热情迎接，美方举行隆重迎接仪式，礼兵分列红毯两侧致敬，"
            "军乐团奏中美两国国歌，现场鸣放21响礼炮、战机飞越致敬。习近平发表书面讲话指出，中美两国人民"
            "长期友好交往、双方利益深度交融，两国应该成为伙伴而不是对手，实现中华民族伟大复兴和让美国再次伟大"
            "完全可以并行不悖、相互成就、造福世界；双方应相向而行，推动形成合作为主、竞争有度、分歧可控、"
            "和平可期的稳定关系。蔡奇、王毅等陪同人员同机抵达，先期抵达的何立峰、中国驻美大使谢锋到机场迎接。")

# [李强会见吉尔吉斯斯坦总理]
upd("https://www.gov.cn/yaowen/liebiao/202609/content_7081896.htm",
    summary="9月23日下午，国务院总理李强在杭州会见来华出席第五届全球数字贸易博览会的吉尔吉斯斯坦总理"
            "卡瑟马利耶夫。李强表示，中吉关系稳步向前，双方合作进入快速发展的“黄金期”，中方愿同吉方"
            "抓紧落实元首访问成果，加强发展战略对接，继续高质量共建“一带一路”，推进中吉乌铁路、"
            "口岸现代化改造等项目建设，拓展人工智能、数字经济、绿色能源、金融等领域合作。"
            "卡瑟马利耶夫表示，吉方坚定恪守一个中国原则，愿同中方深化贸易投资、互联互通等各领域合作，"
            "积极推进中吉乌铁路建设。")

# [第七届全国少数民族文艺会演闭幕]
upd("https://www.gov.cn/yaowen/liebiao/202609/content_7081909.htm",
    summary="历时一个多月的第七届全国少数民族文艺会演23日晚在北京民族剧院落下帷幕，中共中央政治局常委、"
            "全国政协主席王沪宁出席闭幕式文艺晚会。本届文艺会演由国家民委、文化和旅游部、国家广播电视总局、"
            "中央广播电视总台、北京市人民政府联合主办，8月18日至9月23日共有48台优秀剧目在北京14个剧场"
            "演出114场，剧目数量创历届新高，线上线下观演人数约18万人次。尹力、李干杰、李书磊、洛桑江村、"
            "雪克来提·扎克尔、谌贻琴、巴特尔、咸辉分别出席开、闭幕式文艺晚会。")

# [王东明会见乌兹别克斯坦工会联合会代表团] 清理 &nbsp;
upd("http://paper.people.com.cn/rmrb/pc/content/202609/24/content_30182822.html",
    summary="9月23日，全国人大常委会副委员长、中华全国总工会主席王东明在京会见乌兹别克斯坦工会联合会主席"
            "库德拉提拉·拉菲科夫率领的乌工联代表团一行。双方就认真落实两国元首共识，进一步加强交流合作，"
            "更好服务两国现代化建设等交换意见。")

# [中央纪委国家监委通报六起] 86 → 87（反腐档）
upd("http://paper.people.com.cn/rmrb/pc/content/202609/24/content_30182832.html",
    priority_score=87,
    summary="中秋、国庆将至，中央纪委国家监委日前对6起违反中央八项规定精神典型问题进行公开通报。其中包括："
            "国务院国资委原副部长级干部潘良多次违规接受私营企业主安排的宴请、打高尔夫球和娱乐活动，"
            "违规收受礼品，被开除党籍并移送检察机关审查起诉；贵州省黔南州原副州长、福泉市委原书记黄桂林"
            "政绩观错位搞“政绩工程”“形象工程”，将路灯工程预算由78万元增至1400余万元，受到开除党籍、"
            "开除公职处分；新疆维吾尔自治区地质局原党组副书记、副局长孙新春，山西省霍州市人大常委会原党组书记、"
            "主任张伟兴，云南省勐海县副县长余俊锋等人分别受到相应党纪政务处分。")

# [王东伟任安徽省代理省长]
upd("http://paper.people.com.cn/rmrb/pc/content/202609/24/content_30182840.html",
    title="王东伟任安徽省代理省长",
    summary="安徽省第十四届人民代表大会常务委员会第二十六次会议9月23日决定：接受梁言顺辞去安徽省人大常委会"
            "主任职务的请求，接受王清宪辞去安徽省人民政府省长职务的请求，安徽省人民政府副省长王东伟任代理省长。")

# [国办"高效办成一件事"清单] 部委动态 88 → 政策发布 80
upd("https://www.gov.cn/zhengce/content/202609/content_7081880.htm",
    category="政策发布",
    priority_score=80,
    summary="国务院办公厅印发《“高效办成一件事”2026年度第二批重点事项清单》（国办函〔2026〕84号），"
            "涵盖经营主体和个人共13个事项，其中涉经营主体5项、涉个人8项。经营主体事项包括开办超市便利店"
            "准入准营、专精特新“小巨人”企业培育服务、用地用林用草用湿用海联动审批、企业出海服务；"
            "个人事项包括工程建设领域执业人员注册、租房购房提取住房公积金、携带宠物出境、二手车流通交易、"
            "报废机动车回收注销、残疾儿童康复救助申请、失能人员长期护理保险服务等。通知要求推动在建设"
            "全国统一大市场、扩大高水平对外开放、优化营商环境等领域更大范围实现“高效办成一件事”。")

# [外交部记者会 9-23] 死链修复 + 标题去残留 + 实录要点
upd("https://www.mfa.gov.cn/web/wjdt_674879/202609/t20260923_12029529.shtml",
    url="https://www.mfa.gov.cn/web/fyrbt_673021/jzhsl_673025/202609/t20260923_12029529.shtml",
    title="2026年9月23日外交部发言人郭嘉昆主持例行记者会",
    summary="外交部发言人郭嘉昆9月23日主持例行记者会。就第48届世界技能大赛，郭嘉昆介绍大赛吸引68个国家和地区"
            "近1400名选手参赛、规模空前，习近平主席致贺信、李强总理出席世界技能大会开幕式并致辞，"
            "中方愿同各方推动建设世界技能创新中心、拓展“一带一路”南南合作技能开发。就日本首相高市早苗在"
            "联合国大会发言呼吁删除《联合国宪章》“敌国条款”，郭嘉昆表示日本现政权否认侵略历史、持续强军扩武，"
            "已成为威胁地区和平稳定的突出因素，“敌国条款”时至今日仍具有重要现实意义。就美方威胁制裁允许"
            "伊朗航班降落的国家，郭嘉昆表示中方坚决反对没有国际法依据、未经安理会授权的非法单边制裁。")

# [对外直接投资统计公报] 经贸72 → 部委动态85 + 官网原文
upd("https://news.cctv.com/2026/09/24/ARTIo1A2j1T9FqjuwBiH9WYP260924.shtml",
    url="https://www.mofcom.gov.cn/tjsj/gwjjhztj/art/2026/art_843d632d3e024bc99bc84796122f0d22.html",
    source="商务部",
    category="经贸动向",
    priority_score=85,
    title="商务部、国家统计局和国家外汇局联合发布《2025年度中国对外直接投资统计公报》",
    summary="9月23日，商务部、国家统计局和国家外汇管理局联合发布《2025年度中国对外直接投资统计公报》。"
            "2025年中国对外直接投资流量2135.8亿美元，比上年增长11.1%；对外投资存量3.4万亿美元，"
            "连续9年保持全球前三，占全球投资的比重增加到7.4%；新增股权投资1227.4亿美元、增长68%，"
            "创历史新高。截至2025年末，我国在境外设立企业5.8万家，遍布189个国家和地区，境外企业从业员工"
            "476.1万人，其中雇用外方员工296.5万人。2025年中国企业对共建“一带一路”国家直接投资460.5亿美元，"
            "占当年对外投资流量的21.6%。")

# ---------------- 3. 补录 ----------------
template = dict(keep[0])
def new_item(**kw):
    it = json.loads(json.dumps(template, ensure_ascii=False))
    it.update({
        "date": "2026-09-23",
        "collectedAt": "2026-09-24 09:40:40",
        "is_summit_level": False,
    })
    it.update(kw)
    return it

ADD = [
    new_item(
        title="刘国中在湖北调研并出席2026年中国农民丰收节全国主场活动",
        url="https://www.gov.cn/yaowen/liebiao/202609/content_7081893.htm",
        source="中国政府网·要闻", category="高层动态", priority_score=95,
        summary="中共中央政治局委员、国务院副总理刘国中21日至23日到湖北调研，并出席2026年中国农民丰收节"
                "全国主场活动。刘国中先后来到襄阳襄州区、枣阳市，实地调研秋粮生产、农机服务、农村人居环境"
                "整治提升等情况，并与农民群众一起参加丰收节庆祝活动。他强调，今年是“十五五”开局之年，"
                "我国克服自然灾害等不利影响，夏粮产量再创新高、早稻保持稳定、秋粮丰收在望，要抓好秋粮后期"
                "田管和防灾减灾，精心组织收获和收购，确保全年粮食丰收。刘国中还到十堰丹江口市了解南水北调"
                "中线水源地保护和引江补汉工程建设情况。"),
    new_item(
        title="国新办“开局起步‘十五五’”发布会：锚定蓝图 加快建设教育强国",
        url="https://www.gov.cn/yaowen/liebiao/202609/content_7081901.htm",
        source="中国政府网·要闻", category="重要会议", priority_score=88,
        summary="国务院新闻办9月23日举行“开局起步‘十五五’”系列主题新闻发布会，教育部相关负责人介绍"
                "加快推进教育强国建设有关情况。据介绍，我国已建成世界上规模最大且有质量的教育体系，"
                "接受过高等教育的人口达2.7亿；《教育发展“十五五”规划》对未来五年教育改革发展作出系统部署。"
                "“十五五”时期将重点做好六方面工作：全面落实立德树人根本任务、办强办优基础教育、"
                "推动高等教育提质扩容、加快建设现代职业教育体系、培养造就高水平教师队伍、持续深化改革开放。"),
    new_item(
        title="国新办“开局起步‘十五五’”发布会：推进“十五五”民政事业高质量发展",
        url="https://www.news.cn/politics/20260923/f85fc42f02af4fe887ba39ba45134576/c.html",
        source="新华社", category="重要会议", priority_score=88,
        summary="国新办9月23日举行“开局起步‘十五五’”系列主题新闻发布会，民政部部长李常官等介绍“十五五”"
                "时期推进民政事业高质量发展有关情况。李常官表示，“十五五”时期将推动修订老年人权益保障法、"
                "推动制定养老服务法，健全分级分类、普惠可及、覆盖城乡、持续发展的养老服务体系；推动社会救助"
                "从“保生存”向“保基本、防风险、促发展”拓展。民政部提出实施“五千工程”，到“十五五”末全国村和"
                "社区一级养老服务设施覆盖率要达到70%、养老机构护理型床位占比要达到73%。"),
    new_item(
        title="安徽等3省省委主要负责同志职务调整",
        url="http://politics.people.com.cn/n1/2026/0923/c461001-40804304.html",
        source="人民网", category="人事任免", priority_score=86,
        summary="新华社北京9月23日电 日前，中共中央决定：李乐成同志任安徽省委委员、常委、书记，梁言顺同志"
                "不再担任安徽省委书记、常委、委员职务；周祖翼同志任河南省委委员、常委、书记，不再担任福建省委"
                "书记、常委、委员职务；刘宁同志不再担任河南省委书记、常委、委员职务；赵龙同志任福建省委书记。"),
    new_item(
        title="工业和信息化部印发《创新型产业集群建设管理办法》",
        url="https://www.miit.gov.cn/zwgk/zcwj/wjfb/tz/art/2026/art_c3b698fbaf0d42259de3e48d36a0d107.html",
        source="工业和信息化部", category="政策发布", priority_score=80,
        summary="工业和信息化部印发修订后的《创新型产业集群建设管理办法》（工信部高新〔2026〕163号）。"
                "办法明确，创新型产业集群须满足较强科技供给能力、较强企业创新能力、较强成果转化能力、"
                "较强产业竞争力、较强治理服务水平五方面要求，量化标准包括：省级及以上科技创新平台原则上"
                "不少于3家，上下游企业总数原则上不少于30家且专精特新中小企业、高新技术企业、制造业单项冠军"
                "企业占比不低于1/3，近三年年均研发投入与营业收入之比不低于4%，近三年年均营业收入原则上"
                "不低于300亿元。办法还明确了申报条件、认定流程和动态管理机制，对已认定集群每三年评估一次。"),
    new_item(
        title="第五届全球数字贸易博览会在杭州开幕",
        url="http://expo.ce.cn/gd/202609/t20260923_3231898.shtml",
        source="中国经济网", category="经贸动向", priority_score=85,
        summary="9月23日至27日，第五届全球数字贸易博览会在杭州大会展中心举行。这是国内唯一以数字贸易为主题的"
                "国家级、全球性展会，本届以“在数贸会遇见AI未来”为年度主题，展览总面积17万平方米，"
                "超2000家国内外企业参展、其中AI参展企业占比超三分之一，来自163个国家和地区的超5万名专业客商"
                "报名、国际客商超1.2万人。展会设置1个主题馆和丝路电商、人工智能、数智出行、数智文娱、数智医疗、"
                "空间智能等6个特色产业展区，并首次设立词元（Token）专区，呈现词元制造、分发、调用、应用全产业链。"),
    new_item(
        title="公安部：前8个月立案侦办危害粮食安全刑事案件3700起",
        url="http://society.people.com.cn/n1/2026/0923/c1008-40804306.html",
        source="人民网", category="部委动态", priority_score=85,
        summary="记者从公安部获悉，今年以来公安机关持续依法严厉打击非法占用农用地、私挖盗采黑土泥炭、"
                "制售假劣农资等犯罪活动。1月至8月，共立案侦办相关刑事案件3700起，公安部对16起案件挂牌督办，"
                "推动各地侦办一批重大案件、打掉一批犯罪团伙。公安机关建立完善“专业+机制+大数据”新型警务"
                "运行模式，持续开展守护耕地安全“金风”行动、打击破坏黑土资源行动，并与自然资源、农业农村、"
                "市场监管等部门联合印发《涉嫌破坏耕地犯罪案件移送指引》，形成共治合力。"),
    new_item(
        title="“两高一部”印发《关于办理涉芬太尼类物质刑事案件适用法律等若干问题的意见》",
        url="https://www.spp.gov.cn/xwfbh/wsfbt/202609/t20260923_737391.shtml",
        source="最高人民检察院", category="部委动态", priority_score=88,
        summary="最高人民法院、最高人民检察院、公安部近日联合印发《关于办理涉芬太尼类物质刑事案件适用法律等"
                "若干问题的意见》（法发〔2026〕12号），自9月23日起施行。意见共18条，主要明确了芬太尼类物质"
                "犯罪的定罪量刑数量标准，将芬太尼类物质分为药用和非药用两类，药用的参照有关芬太尼的数量标准、"
                "非药用的参照刑法规定的有关海洛因的数量标准；还规定了芬太尼类物质的范围、证据收集基本要求、"
                "认定明知的基本规则、违法所得追缴、关联案件管辖等内容。意见要求公安机关有针对性地与重点国家"
                "开展办案协作，共同打击跨国走私芬太尼类物质犯罪。最高检、公安部同时印发芬太尼类物质犯罪案件"
                "立案追诉标准的规定。"),
]

keep.extend(ADD)

# ---------------- 4. 排序（分类序 → 分数降序） ----------------
CAT_ORDER = ["元首动态", "高层动态", "重要会议", "人事任免", "部委动态", "政策发布", "经贸动向"]
keep.sort(key=lambda x: (CAT_ORDER.index(x["category"]) if x["category"] in CAT_ORDER else 99,
                         -int(x.get("priority_score") or 0)))

# ---------------- 5. 全量 HTML 实体清洗 + 字段完整性 ----------------
for day in data["archive"]:
    for it in data["archive"][day]:
        for k in ("title", "summary", "source"):
            if isinstance(it.get(k), str):
                it[k] = html.unescape(it[k]).replace("\u00a0", " ").strip()
        if it.get("summary") is None:
            it["summary"] = ""

# ---------------- 6. 落盘 ----------------
data["archive"][TODAY] = keep
data["today"] = TODAY
data["todayCount"] = len(keep)
data["lastUpdated"] = "2026-09-24 09:55"
data["stats"]["totalArticles"] = sum(len(v) for v in data["archive"].values())
data["stats"]["dateCount"] = len(data["archive"])
data["stats"]["latestDate"] = TODAY
data["stats"]["summitCount"] = sum(
    1 for v in data["archive"].values() for it in v if it.get("is_summit_level")
)

with open(JSON, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n最终今日:", len(keep))
from collections import Counter
print(Counter(x["category"] for x in keep))
print("≥85 分:", sum(1 for x in keep if x["priority_score"] >= 85), "/", len(keep))
print("100 分:", sum(1 for x in keep if x["priority_score"] == 100))
print("空摘要:", sum(1 for x in keep if not x["summary"]))
print("归档违规(collectedAt!=今日):", sum(1 for x in keep if not x["collectedAt"].startswith(TODAY)))
print("归档违规(date<9-23):", sum(1 for x in keep if x["date"] < "2026-09-23"))
for x in keep:
    print(f"  {x['priority_score']:>3} | {x['category']} | {x['date']} | {x['title'][:52]}")
