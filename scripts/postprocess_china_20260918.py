#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国内看板 LLM 质量后处理 — 2026-09-18
33 条 -> 删 18 / 修 9 / 补录 9 = 25 条
"""
import json, re, os, sys

BASE = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50"
JSON_FILE = os.path.join(BASE, "data", "china-news.json")
TODAY = "2026-09-18"
YESTERDAY = "2026-09-17"

# ---------- 1. 删除清单（URL 精确匹配） ----------
DELETE_URLS = [
    # 元首线栏目体/述评
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081402.htm",   # 民族工作重要思想指引（署名述评）
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081384.htm",   # 总书记为先进制造业指明方向（新华社述评，与主稿重复）
    # 丁薛祥东博会：报道+全文结构 → 只留报道主稿
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081391.htm",   # 致辞全文
    "http://paper.people.com.cn/rmrb/pc/content/202609/18/content_30181791.html",  # 人民日报致辞版
    "https://www.zaobao.com/news/china/story20260918-9694961",        # 联合早报丁薛祥亚细安版
    # 跨日重复（9-16 版面已收同事件）
    "https://www.zaobao.com/news/china/story20260917-9691309",        # 陈振声再会石泰峰
    "https://news.cctv.com/2026/09/17/ARTIkVY3oiuA3sU0LlGnBRCP260917.shtml",  # 香港五年规划"写在...之际"评论
    # 栏目体 / 评论体
    "https://news.cctv.com/2026/09/17/ARTIFggB6yUy1cokpdh8EcPv260917.shtml",  # 焦点访谈
    "https://news.cctv.com/2026/09/17/ARTIczZOMnNAhnA2JPxbc3KR260917.shtml",  # 习言道
    "https://news.cctv.com/2026/09/18/ARTIZ23OV72FzkQPRbF2czqf260917.shtml",  # 大国制造气象万千（栏目体）
    "https://news.cctv.com/2026/09/17/ARTICyha41tG4Zit38yXAiHp260917.shtml",  # 活力中国调研行（栏目体+地方）
    # 同事件重复（先进制造业）
    "http://paper.people.com.cn/rmrb/pc/content/202609/18/content_30181784.html",  # 人民日报版
    # 分类错误 / 低质
    "https://news.cctv.com/2026/09/17/ARTIj0XjLgntSevFTLF8Ug1X260917.shtml",  # 考古（文化类，非经贸）
    "https://news.cctv.com/2026/09/17/ARTISG8YIQ03JLQIW7MH9vqj260917.shtml",  # 物流供应链金融预测稿
    "http://paper.people.com.cn/rmrb/pc/content/202609/18/content_30181798.html",  # WTO 研讨会（学术场次）
    # 联合早报微观 / 署名评论
    "https://www.zaobao.com/news/china/story20260917-9694202",        # 新津贸易额（新加坡地方）
    "https://www.zaobao.com/news/china/story20260918-9694415",        # 韩咏红署名评论 + AI 线
]

# ---------- 2. 修正清单 ----------
# key = 原 URL（匹配用），value = 要覆盖的字段
FIXES = {
    # 习近平先进制造业：tv.cctv 视频聚合页 -> gov.cn 原文
    "https://tv.cctv.com/2026/09/17/VIDE2JRf0TFEQzOIGCXYT4ov260917.shtml": {
        "url": "https://www.gov.cn/yaowen/liebiao/202609/content_7081344.htm",
        "source": "中国政府网·要闻",
        "date": "2026-09-17",
        "category": "元首动态",
        "priority_score": 100,
        "summary": "新华社北京9月17日电。中共中央总书记、国家主席、中央军委主席习近平近日就发展先进制造业作出重要指示，强调坚持智能化、绿色化、融合化方向，持续做大做强先进制造业，提升产业链自主可控水平，加快构建以先进制造业为骨干的现代化产业体系，为推进中国式现代化提供有力支撑。全国先进制造业大会9月16日至17日在京召开，会上传达习近平重要指示，中共中央政治局常委、国务院总理李强出席会议并讲话。",
    },
    # 习近平访美预告：补摘要
    "https://www.zaobao.com/news/china/story20260918-9694978": {
        "summary": "联合早报9月18日报道，据香港媒体消息，美国总统特朗普表示，习近平主席抵达华盛顿访问时，他将亲自到机场迎接。报道称，美方正在为下阶段中美高层交往做安排，双方经贸团队亦就相关议题保持密切交流。",
    },
    # 丁薛祥东博会：tv.cctv 视频页 -> gov.cn 报道主稿
    "https://tv.cctv.com/2026/09/17/VIDEahRJdnYopg8proEuUUNg260917.shtml": {
        "url": "https://www.gov.cn/yaowen/liebiao/202609/content_7081369.htm",
        "source": "中国政府网·要闻",
        "date": "2026-09-17",
        "category": "高层动态",
        "priority_score": 95,
        "summary": "新华社南宁9月17日电。第23届中国—东盟博览会暨中国—东盟商务与投资峰会17日在广西南宁开幕，中共中央政治局常委、国务院副总理丁薛祥出席并致辞。围绕建设更高水平中国—东盟自贸区，他提出推动区域开放水平全面提升、贸易投资合作提质升级、新兴领域合作走深走实、互联互通更加便捷高效四点建议。缅甸副总统纽梭、越南常务副总理范家肃、老挝常务副总理沙伦赛、东盟秘书长高金洪出席并致辞。16日下午丁薛祥分别会见三国政要。",
    },
    # 王毅-鲁比奥：联合早报 -> 外交部官方源
    "https://www.zaobao.com/news/china/story20260917-9694096": {
        "url": "https://www.mfa.gov.cn/wjbzhd/202609/t20260917_12024847.shtml",
        "source": "外交部",
        "date": "2026-09-17",
        "category": "高层动态",
        "priority_score": 95,
        "summary": "2026年9月17日，中共中央政治局委员、外交部长王毅同美国国务卿鲁比奥通电话，双方着重就两国高层交往进行深入讨论。王毅表示，一段时间来中美关系总体沿着两国元首确定的建设性战略稳定轨道前行；强调元首外交是中美关系的定盘星，双方要本着平等、尊重、互惠精神筹备好下阶段高层交往，加强沟通、推进合作、管控分歧，尊重彼此核心利益。双方还就中东局势等问题交换意见。",
    },
    # 谌贻琴：tv.cctv 视频页 -> gov.cn 原文
    "https://tv.cctv.com/2026/09/17/VIDEVyMOqwb05KEHRJ0zWdau260917.shtml": {
        "url": "https://www.gov.cn/yaowen/liebiao/202609/content_7081368.htm",
        "source": "中国政府网·要闻",
        "date": "2026-09-17",
        "title": "谌贻琴会见越南妇联主席黎氏水",
        "category": "高层动态",
        "priority_score": 95,
        "summary": "新华社北京9月17日电。国务委员、全国妇联主席谌贻琴17日在京会见越共中央委员、越南祖国阵线中央委员会副主席、越南妇联主席黎氏水。谌贻琴表示，中方愿同越方一道落实好两党两国最高领导人重要共识，弘扬全球妇女峰会精神，深化妇女领域交流合作，推动中越命运共同体建设走深走实。黎氏水赞赏中国妇女发展成就，表示愿加强交流互鉴。",
    },
    # 郑栅洁会见卢胡特：补摘要
    "https://www.ndrc.gov.cn/xwdt/xwfb/202609/t20260917_1407697.html": {
        "summary": "9月17日，国家发展改革委主任郑栅洁会见印度尼西亚国家经济委员会主席卢胡特，双方就深化中印尼发展战略对接、推进重点领域务实合作等交换意见。",
    },
    # 戴玉林被查：补官方通报摘要（含中纪委同日多起通报）
    "https://www.zaobao.com/news/china/story20260917-9692634": {
        "title": "辽宁省政协原副主席戴玉林接受审查调查",
        "url": "https://www.chinanews.com/gn/2026/09-17/10698460.shtml",
        "source": "中国新闻网",
        "date": "2026-09-17",
        "category": "人事任免",
        "priority_score": 87,
        "summary": "中央纪委国家监委网站9月17日通报，辽宁省政协原党组副书记、副主席戴玉林涉嫌严重违纪违法，目前正接受中央纪委国家监委纪律审查和监察调查。戴玉林1959年4月生，江苏南京人，曾任大连市委常委、副市长，丹东市委书记，辽宁省委常委、省总工会主席，2017年1月起任辽宁省政协副主席。同日该网站还通报新疆生产建设兵团卫健委原副主任刘惟接受审查调查，江西省政协原常委王江军、吉林省白城市委原常委鲍长山被开除党籍。",
    },
    # 外交部记者会：死链修复（同 article ID 换路径）
    "https://www.mfa.gov.cn/web/wjdt_674879/202609/t20260917_12024556.shtml": {
        "url": "https://www.mfa.gov.cn/fyrbt_673021/202609/t20260917_12024556.shtml",
        "date": "2026-09-17",
        "title": "2026年9月17日外交部发言人郭嘉昆主持例行记者会",
        "summary": "外交部发言人郭嘉昆9月17日主持例行记者会。今年是习近平主席提出全球治理倡议一周年，也是《无障碍环境建设法》实施三周年，中国将向人权理事会再次主提无障碍决议。就美众议院通过涉俄制裁法案、授权对俄油气主要买家征收最高100%关税（潜在对象包括中国），郭嘉昆表示中国历来在平等互利基础上同各国开展正常经贸合作，既不针对第三方也不受第三方干扰胁迫，一贯反对没有国际法依据、未经联合国安理会授权的非法单边制裁和长臂管辖。",
    },
    # 三部门农业品牌方案：补全摘要
    "https://news.cctv.com/2026/09/17/ARTIKHktgj5SiSrShfDXNI8S260917.shtml": {
        "summary": "三部门联合印发方案，部署四大任务加强农业品牌保护。在品牌农产品质量安全监管执法方面，全面落实承诺达标合格证制度，健全问题通报和协查机制，强化产地准出分类监管。",
    },
    # 凌激上合经贸部长会：补摘要 + 升分
    "https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_a91a9ea59d744f288c992c6602ab2925.html": {
        "priority_score": 85,
        "summary": "9月17日，商务部副部长兼国际贸易谈判副代表凌激出席上海合作组织成员国第二十五次经贸部长会议，就深化上合组织区域经贸合作、推进贸易投资便利化等议题与各方交换意见。",
    },
    # 绿色贸易报告：升分
    "https://news.cctv.com/2026/09/17/ARTI7EXsPvegfJmEi3xwnBQo260917.shtml": {
        "priority_score": 85,
        "summary": "商务部国际贸易经济合作研究院9月17日发布《中国绿色贸易发展报告（2026）》。报告显示，我国绿色贸易进出口额规模居全球首位，绿色产品出口五年接近翻番，在我国货物出口中的比重持续提高，中国制造绿色装备出海提速。",
    },
    # 王文涛视频会谈：补摘要 + 升分
    "https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_82466aa0597b4a90bf9447e9d27feb8d.html": {
        "priority_score": 85,
        "summary": "9月17日，商务部部长王文涛与欧委会贸易和经济安全委员谢夫乔维奇举行视频会谈，双方就中欧经贸关系及相关经贸议题交换意见。此前商务部在9月17日例行发布会上表示，中方注意到欧委会发布《公共采购法》立法草案并设置欧洲优先条款，中方对此高度关切。",
    },
}

# ---------- 3. 补录清单 ----------
ADDS = [
    {
        "title": "国新办举行“开局起步‘十五五’”发布会 介绍加快推动广播电视和网络视听高质量发展",
        "url": "https://my-h5news.app.xinhuanet.com/h5/article.html?articleId=202609171b40b75b2f7849019849556b4282b1e9",
        "source": "新华社", "date": "2026-09-17", "category": "重要会议", "priority_score": 88,
        "summary": "国务院新闻办9月17日举行“开局起步‘十五五’”系列主题新闻发布会，国家广播电视总局副局长何飚等介绍“十五五”时期加快推动广播电视和网络视听高质量发展有关情况。截至去年底全国网络视听用户10.99亿人、网民日均观看超200分钟、行业市场规模突破1.2万亿元；全国微短剧用户超8亿。广电总局将推进广播电视与网络视听深度融合，把握意识形态、公共服务、技术产业三大属性，统筹四个业务层次，并会同工信部制定一体化电视技术标准。",
    },
    {
        "title": "国务院办公厅印发《关于进一步加强烟花爆竹全链条安全监管的意见》",
        "url": "https://www.gov.cn/yaowen/liebiao/202609/content_7081360.htm",
        "source": "中国政府网·要闻", "date": "2026-09-17", "category": "政策发布", "priority_score": 80,
        "summary": "新华社北京9月17日电。国务院办公厅日前印发《关于进一步加强烟花爆竹全链条安全监管的意见》，对防范化解重大安全风险、有效遏制事故发生作出部署。意见就生产、储存、经营、运输、燃放等各环节提出全链条监管措施，要求严格生产企业准入许可审批、严控生产过程安全风险，严防普通货运和寄递渠道运输烟花爆竹，严禁生产经营超药量、超规格等不符合国家标准的产品。",
    },
    {
        "title": "公安部公布打击整治网络违法犯罪10起典型案例",
        "url": "https://news.cctv.com/2026/09/17/ARTI19Kvgo4YfZawO3DsVrNh260917.shtml",
        "source": "央视新闻", "date": "2026-09-17", "category": "部委动态", "priority_score": 88,
        "summary": "今年以来全国公安机关网安部门持续深化“净网—2026”专项行动，截至日前累计侦办网络违法犯罪案件3.6万余起，其中侵犯公民个人信息案件4100余起、黑客案件3900余起、涉事故灾害和涉经济民生网络谣言案件1.1万余起、网络暴力案件2500余起。公安部9月17日公布10起典型案例，涉及虚假摆拍网络谣言、网暴抗洪救灾村干部、网暴运动员、借“护剧”名义实施舆情敲诈等。",
    },
    {
        "title": "市场监管总局印发网络食品销售相关经营者《食品安全风险管控清单》",
        "url": "https://www.samr.gov.cn/zw/zfxxgk/fdzdgknr/spscs/art/2026/art_810e123ddaa84ae89bc733a15b14c412.html",
        "source": "市场监管总局", "date": "2026-09-17", "category": "政策发布", "priority_score": 80,
        "summary": "市场监管总局办公厅印发网络食品销售相关经营者《食品安全风险管控清单》，聚焦直播电商平台经营者、网络食品交易第三方平台提供者、入网食品生产销售企业三类主体，逐一明确风险控制环节、风险点、管控措施、管控目标和管控频次。清单为直播电商平台划出十一项宣传禁止性要求，要求第三方平台至少每六个月核验更新一次商家入网资质，对入网企业实行从进货到配送全流程管控，并鼓励平台间共享黑名单信息。",
    },
    {
        "title": "文化和旅游部印发《文化和旅游发展“十五五”规划》",
        "url": "https://www.mct.gov.cn/whzx/whyw/202609/t20260916_967163.htm",
        "source": "文化和旅游部", "date": "2026-09-17", "category": "政策发布", "priority_score": 80,
        "summary": "文化和旅游部印发《文化和旅游发展“十五五”规划》，锚定文化强国、旅游强国建设目标，对繁荣艺术创作生产、加强文化遗产保护传承、完善文化和旅游公共服务、大力发展文化和旅游产业、统筹市场培育监管、推动科技赋能、推进交流合作、促进区域城乡协调发展等八方面重点任务作出部署，设计54个重点工程项目。规划提出到2030年居民年人均接受公共文化设施服务达3.5次、国内出游达83亿人次、入境旅游达1.9亿人次。",
    },
    {
        "title": "国家统计局发布《统计改革发展“十五五”规划》",
        "url": "https://www.stats.gov.cn/zt_18555/zthd/sjtjr/tjr17/tjgg/202609/t20260917_1965353.html",
        "source": "国家统计局", "date": "2026-09-17", "category": "政策发布", "priority_score": 80,
        "summary": "国家统计局发布《统计改革发展“十五五”规划》，从健全统计制度方法体系、完善国民经济核算制度、健全现代化产业统计、深化统计重点领域改革等方面作出部署。规划提出强化社会民生领域统计，建立健全投资于人统计指标体系和监测制度；完善新就业形态统计、加强灵活就业统计监测；将反映消费新业态新模式的商品和服务及时纳入居民消费价格统计调查，缩短CPI基期轮换周期；完善碳排放统计核算制度，严查严治统计数据造假行为。",
    },
    {
        "title": "全国夏粮收购小麦超1亿吨 秋粮收购准备就绪",
        "url": "https://www.lswz.gov.cn/html/mtsy2026year/2026-09/17/content_295300.shtml",
        "source": "国家粮食和物资储备局", "date": "2026-09-17", "category": "部委动态", "priority_score": 85,
        "summary": "国家粮食和物资储备局9月16日发布数据，目前全国累计收购小麦1亿吨、早籼稻1200万吨，进度略快于上年，夏粮旺季收购接近尾声，秋粮收购各项准备工作已基本就绪，市场化收购占比在95%以上。8月以来国家有关部门在江西、湖南启动早籼稻最低收购价执行预案，在河南、安徽启动小麦最低收购价执行预案，已收购最低收购价小麦120万吨、早籼稻90万吨。今年秋粮旺季收购将从9月下旬持续至明年4月底，预计收购量3.5亿吨左右。",
    },
    {
        "title": "今年新型政策性金融工具8000亿元首批资金加快投放",
        "url": "https://tv.cctv.cn/2026/09/17/VIDE6EiJPkWdVZoGCwvdQsXs260917.shtml",
        "source": "央视新闻", "date": "2026-09-17", "category": "经贸动向", "priority_score": 85,
        "summary": "近日今年新型政策性金融工具首批资金已启动投放，一批智能制造和基础设施项目相继获得首批资金支持。该工具是国家为支持重大战略、补充重点项目资本金而创设，通过资本金杠杆放大投资总量，由国家开发银行、农业发展银行、进出口银行负责投放。目前已在云南、福建、四川等多地加快投放，今年总投资规模从去年的5000亿元增加到8000亿元，据测算预计将撬动项目总投资规模约10万亿元。",
    },
    {
        "title": "我国成功发射卫星互联网低轨25组卫星",
        "url": "https://news.cctv.com/2026/09/17/ARTIvWflocyj9Uw543RBlUtO260917.shtml",
        "source": "央视新闻", "date": "2026-09-17", "category": "部委动态", "priority_score": 85,
        "summary": "北京时间9月17日8时32分，我国在海南商业航天发射场使用长征十二号运载火箭，成功将卫星互联网低轨25组卫星发射升空，卫星顺利进入预定轨道。长征十二号是我国首款4米级箭径、单芯级运载火箭，全长约62米，700公里太阳同步轨道运载能力不低于6吨，本次是长征系列运载火箭第667次发射。同日10时40分，我国在酒泉卫星发射中心使用快舟十一号遥三运载火箭成功发射天仪51、52星。",
    },
]


def clean_text(s):
    if not s:
        return s
    s = s.replace("&mdash;", "—").replace("&nbsp;", " ").replace("&amp;", "&")
    s = s.replace("&ldquo;", "“").replace("&rdquo;", "”").replace("&quot;", '"')
    s = re.sub(r"&[a-z]+;", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def trim(s, n=159):
    s = clean_text(s)
    if len(s) > n:
        s = s[:n - 1].rstrip("，。；、 ") + "…"
    return s


def main():
    with open(JSON_FILE, encoding="utf-8") as f:
        data = json.load(f)

    board = data["archive"][TODAY]
    print(f"初始今日版面: {len(board)} 条")

    # --- 删除 ---
    delset = set(DELETE_URLS)
    before = len(board)
    removed = [it for it in board if it.get("url") in delset]
    board = [it for it in board if it.get("url") not in delset]
    print(f"删除: {before - len(board)} 条（清单 {len(delset)}，命中 {len(removed)}）")
    if len(removed) != len(delset):
        missing = delset - {it.get("url") for it in removed}
        print("  ⚠️ 未命中:", missing)

    # --- 修正 ---
    fixed = 0
    for it in board:
        fx = FIXES.get(it.get("url"))
        if fx:
            it.update(fx)
            fixed += 1
    print(f"修正: {fixed} 条")

    # --- 补录 ---
    existing = {it.get("url") for it in board}
    for a in ADDS:
        if a["url"] in existing:
            print("  ⚠️ 已存在，跳过:", a["title"][:30])
            continue
        a = dict(a)
        a["collectedAt"] = TODAY + " 09:30"
        board.append(a)
    print(f"补录后: {len(board)} 条")

    # --- 清理与校验 ---
    for it in board:
        it["title"] = clean_text(it.get("title", ""))
        it["summary"] = trim(it.get("summary", ""))
        it.setdefault("source", "")
        it.setdefault("category", "")
        it["priority_score"] = int(it.get("priority_score") or 0)

    data["archive"][TODAY] = board
    data["todayCount"] = len(board)

    # stats 重算
    st = data.get("stats", {})
    st["totalArticles"] = sum(len(v) for v in data["archive"].values())
    st["todayCount"] = len(board)
    data["stats"] = st
    data["lastUpdated"] = "2026-09-18 09:45"

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    # --- 校验输出 ---
    print("\n=== 校验 ===")
    bad_date = [it["title"][:30] for it in board if it.get("date") not in (TODAY, YESTERDAY)]
    bad_col = [it["title"][:30] for it in board if not (it.get("collectedAt", "").startswith(TODAY))]
    no_sum = [it["title"][:30] for it in board if not it.get("summary")]
    long_sum = [(it["title"][:25], len(it["summary"])) for it in board if len(it["summary"]) > 163]
    short_t = [it["title"][:30] for it in board if len(it.get("title", "")) < 8]
    print(f"date 越界: {len(bad_date)} {bad_date}")
    print(f"collectedAt 越界: {len(bad_col)} {bad_col}")
    print(f"无摘要: {len(no_sum)} {no_sum}")
    print(f"摘要超长: {len(long_sum)} {long_sum}")
    print(f"标题过短: {len(short_t)} {short_t}")

    hi = [it for it in board if it["priority_score"] >= 85]
    print(f"条数: {len(board)} | ≥85 分: {len(hi)} ({len(hi)*100//len(board)}%)")
    from collections import Counter
    print("分类:", dict(Counter(it["category"] for it in board)))
    print("信源:", dict(Counter(it["source"] for it in board)))
    print("分数:", sorted([it["priority_score"] for it in board], reverse=True))

    # 历史版面未改动校验
    for d in ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17"]:
        print(f"  历史 {d}: {len(data['archive'][d])} 条")


if __name__ == "__main__":
    main()
