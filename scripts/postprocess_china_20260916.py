#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
postprocess_china_20260916.py — 国内看板 2026-09-16 LLM 质量后处理

初抓 52 条 → 删 38 / 修 12 / 合并补录 7 → 今日 21 条

删除依据：
  · 元首复述/栏目体 6（制造强国述评、习言道、金砖纪实、国际社会高度评价、此行间100秒）
  · 跨版面（国际线/AI线）6（黄仁勋国宴、人民日报AI专利、中美关税、美众议长AI、赖清德AI岛、顺丰发债）
  · 与 9-15 版面重复 4（王毅两通电话 ×2、电子信息制造业规划 ×2）
  · 同数据多稿 7（8月国民经济 8 稿只留 gov.cn 要闻主稿）
  · 同事件重复 4（郑栅洁座谈会 zaobao 版、香港五年规划 zaobao 版、回信全文、吉大贺信）
  · 栏目体/评论/故事化 5（骨架评论、7组数字图解、小羽绒蹲点、国台办剧集回应、闽宁理论学习研讨）
  · 记者会子稿 1（外空问答并入记者会主稿）
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "china-news.json")
TODAY = "2026-09-16"
COLLECTED = "2026-09-16 12:16:20"

DELETE_URLS = [
    # 元首复述/栏目体
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081156.htm",          # 制造强国述评
    "https://news.cctv.com/2026/09/16/ARTI76985nqU0QQUS3gpdqbN260916.shtml",  # 习言道
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081079.htm",          # 金砖出访纪实
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081091.htm",          # 国际社会高度评价
    "https://news.cctv.com/2026/09/16/ARTILuEhOXx67xS9F0TfqEw9260916.shtml",  # 此行间100秒
    # 跨版面（国际线/AI线）
    "https://www.zaobao.com/news/china/story20260916-9682409",               # 黄仁勋出席国宴
    "https://www.zaobao.com/news/china/story20260916-9682621",               # 人民日报AI专利
    "https://www.zaobao.com/news/china/story20260916-9682737",               # 中美削减关税
    "https://www.zaobao.com/news/china/story20260916-9682434",               # 美众议长谈AI
    "https://www.zaobao.com/news/china/story20260916-9683358",               # 赖清德AI岛
    "https://www.zaobao.com/news/china/story20260916-9683136",               # 顺丰发债
    # 与 9-15 版面重复
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081094.htm",          # 王毅同拉脱维亚外长通电话
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081093.htm",          # 王毅同法国外长通电话
    "https://www.gov.cn/lianbo/202609/content_7081208.htm",                  # 电子信息制造业规划 gov.cn
    "https://news.cctv.com/2026/09/15/ARTILqgYthDg7OUUePNHP3tU260915.shtml",  # 电子信息制造业规划 央视
    # 同数据多稿（8月国民经济只留 gov.cn 要闻主稿）
    "https://www.gov.cn/lianbo/202609/content_7081120.htm",
    "https://jingji.cctv.com/2026/09/16/ARTISZCG9ZOo30rLK6M9NS4q260916.shtml",
    "https://news.cctv.com/2026/09/15/ARTIgmyHRJH4AYcbdlj2GHg8260915.shtml",
    "https://news.cctv.com/2026/09/15/ARTIOY6cdKfcvUcPDpwoC9a2260915.shtml",
    "http://paper.people.com.cn/rmrb/pc/content/202609/16/content_30181324.html",
    "https://news.cctv.com/2026/09/15/ARTI8N5O6SKpKVsiuGJzdwPa260915.shtml",
    "https://news.cctv.com/2026/09/15/ARTIq9MD9mI4hhCNUdcLo1aM260915.shtml",
    "https://news.cctv.com/2026/09/16/ARTI740lT20soOezGjfLBN3z260916.shtml",
    # 同事件重复
    "https://www.zaobao.com/news/china/story20260916-9682597",               # 郑栅洁座谈会 zaobao 版
    "https://www.zaobao.com/news/china/story20260916-9683644",               # 香港五年规划 zaobao 版
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081127.htm",          # 漳州110 回信全文（并入报道）
    "https://tv.cctv.com/2026/09/15/VIDEkreotJQ4C4OuMwXmZuXF260915.shtml",   # 漳州110 央视视频版（并入）
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081263.htm",          # 吉大贺信全文（并入报道）
    "https://www.zaobao.com/news/china/story20260916-9682927",               # 破除圈子文化（并入求是文章）
    # 栏目体/评论/故事化/理论学习
    "http://paper.people.com.cn/rmrb/pc/content/202609/16/content_30181319.html",  # 骨架 评论
    "https://www.gov.cn/zhengce/jiedu/tujie/202609/content_7081201.htm",     # 7组数字图解
    "https://news.cctv.com/2026/09/16/ARTIyV3peQllLIoCjW9as5ld260916.shtml",  # 小羽绒蹲点
    "https://www.zaobao.com/news/china/story20260916-9683392",               # 国台办谈谍战剧
    "https://news.cctv.com/2026/09/15/ARTIgYVUWWuOT33jcRYmmLq1260915.shtml",  # 闽宁理论学习研讨
    "https://www.zaobao.com/news/china/story20260916-9682476",               # 董建华治丧安排
    "https://www.zaobao.com/news/china/story20260916-9683018",               # 携程太空船票
    # 记者会子稿
    "https://news.cctv.com/2026/09/15/ARTId3d5ckwiTF0NeBvzcNKJ260915.shtml",  # 外空问答并入记者会
]

# 按原 URL 匹配后整条替换字段
PATCH = {
    # 张国清：tv.cctv 视频聚合页 → gov.cn 原文 + 补摘要
    "https://tv.cctv.com/2026/09/15/VIDERb83NEWMIgQ8xk4uU4Gr260915.shtml": {
        "url": "https://www.gov.cn/yaowen/liebiao/202609/content_7081222.htm",
        "source": "中国政府网·要闻",
        "summary": "新华社长沙9月15日电 第五届北斗规模应用国际峰会15日在湖南株洲开幕。中共中央政治局委员、国务院副总理张国清出席开幕式并致辞。张国清表示，中国愿同各方一道，进一步提高北斗技术创新水平，加强北斗与人工智能、卫星互联网等技术融合，持续推进系统迭代升级，推动北斗产业健康有序发展，加速北斗应用提质扩面，完善卫星导航全球治理。开幕式前，张国清会见出席峰会的马达加斯加总理拉乔纳里松。本届峰会以“同世界·共北斗——赋能全球”为主题，约900人参加开幕式。",
    },
    # 郑栅洁座谈会：95 高层 → 85 部委（部长级），补发改委原文摘要
    "https://www.ndrc.gov.cn/xwdt/xwfb/202609/t20260915_1407645.html": {
        "category": "部委动态",
        "priority_score": 85,
        "summary": "9月15日，国家发展改革委主任郑栅洁主持召开民营企业座谈会，围绕优化发展环境、拓展投资空间听取意见建议，来自电气设备、算力基础设施、文化旅游服务、养老服务、商业航天领域的德力西集团、润泽科技、清明上河园、瑞芝康健、蓝箭航天等5家企业负责人参加。企业就进一步开放应用场景、优化审批流程、拓宽融资渠道、盘活存量资产、强化要素保障、健全标准体系等提出意见建议。郑栅洁表示，民间投资是扩大有效投资的有力支撑，越是转型关口越要坚定信心，发改委将分行业分领域常态化推介优质投资项目，有序开放重点领域应用场景。",
    },
    # 记者会：死链 → 正确栏目路径 + 去导航残留 + 补实录要点
    "https://www.mfa.gov.cn/web/wjdt_674879/202609/t20260915_12022859.shtml": {
        "url": "https://www.mfa.gov.cn/web/fyrbt_673021/jzhsl_673025/202609/t20260915_12022859.shtml",
        "title": "2026年9月15日外交部发言人郭嘉昆主持例行记者会",
        "summary": "外交部发言人郭嘉昆9月15日主持例行记者会并宣布：巴西总统首席特别顾问阿莫林将于9月16日至17日访华，王毅将同其举行会见。就2026年服贸会闭幕，郭嘉昆表示本届服贸会吸引1830余家企业线下参展、5300余家企业线上参展，达成1200余项成果。就日本首相高市早苗涉台错误言行，中方强调这是当前中日关系面临严重困难的最大症结。就菲方南海声明，中方重申南沙群岛是中国固有领土，“南海仲裁案”裁决非法无效。就美方称已在太空部署武器，中方敦促美方停止在外空扩军备战。",
    },
    # 王毅会见东盟秘书长：修复 161 字截断
    "http://paper.people.com.cn/rmrb/pc/content/202609/16/content_30181267.html": {
        "summary": "本报北京9月15日电 中共中央政治局委员、外交部长王毅15日在北京会见东盟秘书长高金洪。王毅说，中方高度重视东盟并将东盟作为周边外交的优先方向，将继续支持东盟团结和共同体建设，支持东盟在区域架构中的中心地位，愿同东盟一道推动构建更为紧密的中国—东盟命运共同体，愿同东盟国家一道落实好《南海各方行为宣言》，推进“南海行为准则”磋商进程。高金洪说，中国是东盟值得信赖和倚重的合作伙伴，东盟愿同中方继续深化拓展务实合作，共同维护南海和平稳定。",
    },
    # 石泰峰会见新加坡防长：修复截断
    "http://paper.people.com.cn/rmrb/pc/content/202609/16/content_30181269.html": {
        "summary": "本报北京9月15日电 中共中央政治局委员、中央组织部部长石泰峰15日在北京会见新加坡公共服务统筹部长兼国防部长陈振声。石泰峰表示，中方愿同新方一道，认真落实两国领导人重要共识，加强战略沟通，深化务实合作，推动中新全方位高质量的前瞻性伙伴关系取得更大发展，并介绍了中国共产党深入学习贯彻习近平党建思想、开展树立和践行正确政绩观学习教育的情况。陈振声表示，新方愿同中方加强交流互鉴，深化人才培训等领域合作，更好惠及两国人民。",
    },
    # 张庆伟：经贸72 → 高层95（全国人大常委会副委员长）
    "http://paper.people.com.cn/rmrb/pc/content/202609/16/content_30181272.html": {
        "category": "高层动态",
        "priority_score": 95,
        "summary": "新华社乌鲁木齐9月15日电 全国人大常委会副委员长张庆伟15日上午在新疆乌鲁木齐出席2026上合组织数字经济论坛开幕式并发表主旨演讲。张庆伟指出，习近平主席在2026比什凯克峰会上的重要讲话，为深化上合组织数字经济合作指明了前进方向，希望各方秉持“上海精神”，落实元首理事会达成的共识。本次论坛由上海合作组织睦邻友好合作委员会、国家数据局等共同主办，主题为“数智融合 合作共赢”。",
    },
    # 求是文章：修复截断，补文章要点
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081174.htm": {
        "title": "《求是》杂志发表习近平总书记重要文章《在加强基础研究座谈会上的讲话》",
        "summary": "9月16日出版的第18期《求是》杂志发表中共中央总书记、国家主席、中央军委主席习近平的重要文章《在加强基础研究座谈会上的讲话》。文章指出，基础研究是整个科学体系的源头、所有技术问题的总机关、全球科技竞争的前沿阵地，要成为世界科技强国基础研究必须搞上去。文章从充分认识重要性紧迫性、优化系统布局、壮大人才队伍、加强支持保障、拓展国际合作五方面作出部署，要求破除“圈子文化”和“学阀”做派，扭转唯论文、唯顶刊、唯帽子、唯奖项倾向。",
    },
    # 国台办：补真实摘要
    "https://news.cctv.com/2026/09/16/ARTIBAPDIhV0b0usOT1Hy6pv260916.shtml": {
        "title": "国台办回应台湾学生历史认知问题：反对“去中国化”教育",
        "summary": "国务院台办9月16日举行例行新闻发布会，发言人朱凤莲回应台湾学生把“桃园三结义”理解为桃园市结盟等问题时表示，中华文化是台湾同胞的精神家园，也是台湾经济社会发展的精神动力；民进党当局推行“去中国化”教育，刻意割裂台湾青少年与中华文化的历史联结，只会遭到台湾同胞的反对。朱凤莲强调，两岸同胞同根同源、同文同种，任何“台独”分裂行径都改变不了台湾是中国一部分的事实。",
    },
    # 发改委 3000 万海南：补真实摘要
    "https://news.cctv.com/2026/09/15/ARTIRCis0Aw5pDWKYdT8K5rq260915.shtml": {
        "summary": "近期受持续强降雨影响，海南省多地发生洪涝灾害。9月15日，国家防减救灾委、应急管理部启动国家四级救灾应急响应。为贯彻落实习近平总书记关于防汛救灾工作的重要指示精神，根据《国家自然灾害救助应急预案》和海南省灾害损失情况，国家发展改革委紧急安排3000万元中央预算内投资，支持海南省做好暴雨洪涝灾害灾后应急恢复，重点用于灾区受损道路、水利等基础设施和学校、医院等公共服务设施灾后应急恢复建设。",
    },
    # 香港五年规划：补真实摘要
    "https://news.cctv.com/2026/09/16/ARTI5x3j8RdD12UyczWQeQlz260916.shtml": {
        "title": "香港特区首个五年规划正式公布",
        "summary": "香港特区行政长官李家超9月16日在立法会公布《香港特别行政区经济和社会发展第一个五年规划（2026—2030年）》，并随之发表《行政长官2026年施政报告》。规划分7篇28章，确立经济发展取得新突破、国际竞争力和影响力持续提升、北部都会区建设加速提效、民生福祉显著改善、融入和服务国家发展大局取得重大进展五大目标，提出巩固提升“四中心、一高地”，即国际金融、航运、贸易中心和国际航空枢纽地位，加快建设国际创新科技中心，打造国际高端人才集聚高地。",
    },
    # 8月国民经济：gov.cn 要闻主稿保留并补全
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081246.htm": {
        "title": "8月我国国民经济运行总体平稳、发展向新向优",
        "summary": "国务院新闻办9月15日举行新闻发布会，国家统计局数据显示，8月份国民经济运行总体平稳，延续动能向新、结构向优的发展态势。8月份全国规模以上工业增加值同比增长5.2%，比上月加快0.7个百分点，其中装备制造业和高技术制造业快速增长，锂离子电池、工业机器人产品产量同比分别增长57.2%、34.6%。前8个月高技术产业投资同比增长5.2%，累计增速连续三个月加快；社会消费品零售总额接近33万亿元。8月份规模以上工业单位增加值能耗同比下降7.2%。",
    },
}

# 合并补录条目（collectedAt=今日；date=真实发布日）
ADD = [
    {
        "title": "习近平给福建省“漳州110”全体队员回信强调 坚守为民初心矢志担当奉献 做党和人民的忠诚卫士",
        "url": "http://cpc.people.com.cn/n1/2026/0916/c64094-40799512.html",
        "date": "2026-09-15",
        "source": "人民日报",
        "category": "元首动态",
        "priority_score": 100,
        "is_summit_level": True,
        "summary": "近日，中共中央总书记、国家主席、中央军委主席习近平给福建省“漳州110”全体队员回信，对他们予以亲切勉励并提出殷切期望。习近平在回信中说，“漳州110”是公安系统的一张亮丽名片，你们扎根警务一线，在服务群众、护民安宁等方面辛勤付出，得到了广泛赞许；守百姓幸福，护家国平安，人民公安重任在肩，希望广大公安干警坚守为民初心、弘扬优良传统、矢志担当奉献，做党和人民的忠诚卫士。“漳州110”现为福建省漳州市公安局漳州110支队，1990年以来持续优化110报警服务快速反应机制，是全国公安机关优秀基层单位代表。",
        "collectedAt": COLLECTED,
    },
    {
        "title": "第十三届北京香山论坛开幕 董军出席并作主旨发言",
        "url": "https://www.chinanews.com.cn/gn/2026/09-16/10697347.shtml",
        "date": "2026-09-16",
        "source": "中国新闻网",
        "category": "重要会议",
        "priority_score": 88,
        "is_summit_level": False,
        "summary": "第十三届北京香山论坛9月16日在北京国际会议中心开幕，国务委员兼国防部长董军出席论坛并作主旨发言。董军说，今年是北京香山论坛创办20周年，当前世界百年变局加速演进，国际安全处于脆弱时刻，习近平主席提出的人类命运共同体理念和四大全球倡议愈发彰显引领历史航向的时代价值；我们应坚持以新安全观凝聚共识、以多边主义维护稳定、以历史清醒防范风险、以对话协商解决问题、以共同发展打牢根基、以行动导向深化合作。本届论坛主题为“凝聚稳定共识 同促安全治理”，来自100余个国家和地区、国际组织的官方代表、专家学者和观察员等约2000名嘉宾出席。",
        "collectedAt": COLLECTED,
    },
    {
        "title": "国家网信办发布近期网络安全、数据安全、个人信息保护等领域执法典型案例",
        "url": "https://www.chinanews.com.cn/gn/2026/09-15/10696925.shtml",
        "date": "2026-09-15",
        "source": "中国新闻网",
        "category": "部委动态",
        "priority_score": 88,
        "is_summit_level": False,
        "summary": "国家网信办9月15日通报近期网络安全、数据安全、个人信息保护等领域10起执法典型案例，涉及网页篡改、设置恶意程序、数据泄露、违法收集使用个人信息、违法出境个人信息、未落实人工智能生成合成内容标识要求、新技术新应用未经评估上线提供服务等情形。案例包括上海某电子公司网页篡改案、北京某网络科技公司应用程序被植入恶意程序案、安徽某数据产业公司2400余份内部文件被窃取案、河南某医院数据泄露风险案等，属地网信部门已依法作出罚款、警告等处置，涉嫌违法犯罪线索移送公安机关。",
        "collectedAt": COLLECTED,
    },
    {
        "title": "市场监管总局会同文化和旅游部对在线酒店预订平台服务行业开展行政指导",
        "url": "https://www.samr.gov.cn/xw/zj/art/2026/art_df94d15242ad470bb6c4dd96ab47fcbb.html",
        "date": "2026-09-15",
        "source": "市场监管总局",
        "category": "部委动态",
        "priority_score": 88,
        "is_summit_level": False,
        "summary": "9月15日，市场监管总局会同文化和旅游部召开在线酒店预订平台服务行业行政指导会，要求美团、抖音、京东、携程、同程、飞猪等平台企业严格落实合规主体责任，防范化解独家合作、“全网最低价”等“内卷”问题和竞争风险，维护健康有序的旅游市场环境。会议指出，公平竞争是市场经济的法治基石，各平台企业要以案为鉴、对照自查，严格遵守反垄断法、反不正当竞争法、电子商务法、旅游法等法律规定，共同营造优质优价、良性竞争的市场秩序。北京、上海、江苏、浙江等地市场监管部门有关负责同志参加会议。",
        "collectedAt": COLLECTED,
    },
    {
        "title": "国家医保局：我国将试行高水平新技术新产品医疗服务价格项目预立项制度",
        "url": "https://www.nhsa.gov.cn/art/2026/9/15/art_105_22143.html",
        "date": "2026-09-15",
        "source": "国家医疗保障局",
        "category": "政策发布",
        "priority_score": 80,
        "is_summit_level": False,
        "summary": "国家医疗保障局近日印发《关于试行高水平新技术新产品医疗服务价格项目预立项制度的通知》（医保发〔2026〕23号）。制度将价格立项受理节点前移：医疗新技术获准进入临床研究、新产品获准进入药监部门创新医疗器械特别审查程序之日起至正式获批临床应用前，省级医保部门可依申请开展价格预立项，实现获批应用与价格立项无缝衔接。适用范围为临床价值大、诊疗手段突破的新技术，满足临床重大需求的新设备，以及填补诊疗空白的新耗材；采用“一省申请、全国参照”模式。",
        "collectedAt": COLLECTED,
    },
    {
        "title": "伊朗外长阿拉格齐将于9月16日访华 王毅将同其举行会谈",
        "url": "https://cpc.people.com.cn/n1/2026/0916/c64387-40799556.html",
        "date": "2026-09-15",
        "source": "人民日报",
        "category": "高层动态",
        "priority_score": 95,
        "is_summit_level": False,
        "summary": "外交部发言人9月15日宣布：伊朗外长阿拉格齐将于9月16日访华，中共中央政治局委员、外交部长王毅将同其举行会谈。当前中东局势持续紧张，美伊冲突、霍尔木兹海峡通航安全等问题备受国际关注，访问期间双方将就中伊关系及共同关心的国际和地区问题深入交换意见。（截至发稿，访问为预告安排）",
        "collectedAt": COLLECTED,
    },
    {
        "title": "平陆运河正式通航 西南地区出海缩短内河航程560公里以上",
        "url": "https://news.cctv.com/2026/09/16/ARTIub8BupPuTpiPn89WwL33260916.shtml",
        "date": "2026-09-16",
        "source": "央视新闻",
        "category": "经贸动向",
        "priority_score": 85,
        "is_summit_level": False,
        "summary": "9月16日上午，西部陆海新通道骨干工程——平陆运河正式通航。平陆运河2022年8月28日开工建设，全长134.2公里，总投资约727亿元，按内河Ⅰ级航道标准建设，可通航5000吨级船舶，是国内通航等级最高的运河，全线建成马道、企石、青年三大梯级枢纽，创下世界同类运河通航能力最强等四项“世界之最”。通航后西南地区货物经运河出海较传统路径缩短内河航程560公里以上，综合物流成本降低18%—30%，每年可节约社会运输费用超50亿元。",
        "collectedAt": COLLECTED,
    },
]


def main():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    arts = data["archive"][TODAY]
    before = len(arts)

    # 1) 删除
    delset = {u.rstrip("/") for u in DELETE_URLS}
    kept = [a for a in arts if (a.get("url") or "").strip().rstrip("/") not in delset]
    deleted = before - len(kept)

    # 2) 打补丁
    patched = 0
    for a in kept:
        u = (a.get("url") or "").strip().rstrip("/")
        if u in PATCH:
            a.update(PATCH[u])
            patched += 1

    # 3) 合并补录（URL 去重）
    existing = {(a.get("url") or "").strip().rstrip("/") for a in kept}
    added = 0
    for item in ADD:
        if item["url"].rstrip("/") in existing:
            continue
        kept.append(dict(item))
        added += 1

    # 4) 排序：分数降序（同分保持原序）
    kept.sort(key=lambda x: -(x.get("priority_score") or 0))

    data["archive"][TODAY] = kept
    data["todayCount"] = len(kept)
    if isinstance(data.get("dates"), list) and TODAY in data["dates"]:
        pass

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # ---- 报告 ----
    print(f"今日版面: {before} → {len(kept)} 条（删 {deleted} / 修 {patched} / 补录 {added}）")
    print()
    for i, a in enumerate(kept, 1):
        s = a.get("summary") or ""
        print(f"[{i:02d}] {a.get('category')} | {a.get('priority_score')} | {a.get('date')} | {a.get('source')}")
        print(f"     {a.get('title')}")
        print(f"     {a.get('url')}")
        print(f"     摘要{len(s)}字")
    print()
    # 校验
    scores = [a.get("priority_score") or 0 for a in kept]
    print("≥85 分占比: %.0f%%" % (100.0 * sum(1 for x in scores if x >= 85) / len(scores)))
    print("100 分条数:", sum(1 for x in scores if x == 100))
    print("无摘要:", [a["title"][:20] for a in kept if not (a.get("summary") or "").strip()])
    print("摘要>170:", [a["title"][:20] for a in kept if len(a.get("summary") or "") > 170])
    print("摘要<60:", [(a["title"][:20], len(a.get("summary") or "")) for a in kept
                     if len(a.get("summary") or "") < 60])
    print("摘要结尾无标点:", [a["title"][:20] for a in kept
                        if (a.get("summary") or "")[-1:] not in "。！？”）)"])
    print("归档违规(collectedAt≠今日):", [a["title"][:20] for a in kept
                                   if not (a.get("collectedAt") or "").startswith(TODAY)])
    print("date<2026-09-15:", [a["title"][:20] for a in kept if (a.get("date") or "") < "2026-09-15"])
    print("分类分布:", {c: sum(1 for a in kept if a.get("category") == c)
                     for c in ["元首动态", "高层动态", "重要会议", "人事任免", "部委动态", "政策发布", "经贸动向"]})


if __name__ == "__main__":
    main()
