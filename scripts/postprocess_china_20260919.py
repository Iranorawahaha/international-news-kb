#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国内新闻看板 · LLM 质量后处理（2026-09-19）
- 今日版面初抓 42 条 → 删 27（含 3 条并入综合条目）/ 修 15 / 补录 6
- 历史版面（9-14~9-18）不动
- 归档规则 V2.11：collectedAt=2026-09-19；date ∈ {2026-09-18, 2026-09-19}
"""
import json
import os
import sys

REPO = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50"
JSON_PATH = os.path.join(REPO, "data", "china-news.json")
TODAY = "2026-09-19"
COLLECTED = "2026-09-19"

d = json.load(open(JSON_PATH, encoding="utf-8"))
archive = d["archive"]
today_items = archive[TODAY]
by_url = {it.get("url", ""): it for it in today_items}

# ---------------------------------------------------------------- 删除
DEL_URLS = [
    # [00] 新华社述评/栏目体（民族工作思想指引）
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081402.htm",
    # [02] 先进制造业重要指示「引发热烈反响」栏目体（9-18 版面已收指示主稿）
    "https://news.cctv.com/2026/09/18/ARTIDQU3WlCIbbitUIpDuhiS260918.shtml",
    # [03] 学习活动类报道（学习贯彻…座谈会）
    "http://paper.people.com.cn/rmrb/pc/content/202609/19/content_30181991.html",
    # [04] 时政微观察栏目体
    "https://news.cctv.com/2026/09/18/ARTIag76VbLs4BDQPJoG8CQv260918.shtml",
    # [07] 李强国常会 商务部转载版（与 gov.cn 要闻版重复）
    "https://www.mofcom.gov.cn/xwfb/ldrhd/art/2026/art_ca1820fdeaad47daa4efca40ed96ef16.html",
    # [09] 王毅会见印尼卢胡特 AI 包容发展（=9-18 版面已收同一会见，跨日重复）
    "https://www.zaobao.com/news/china/story20260919-9701694",
    # [12] 全国人大代表学习班（学习活动类）
    "http://paper.people.com.cn/rmrb/pc/content/202609/19/content_30181996.html",
    # [14] 美国拟推迟对台军售（跨版面·国际线）
    "https://www.zaobao.com/news/china/story20260919-9701325",
    # [19][20][24] 外交部 9-18 记者会子稿（并入记者会实录一条）
    "https://news.cctv.com/2026/09/18/ARTIrZbcqihOjJbavpqXpiIA260918.shtml",
    "https://news.cctv.com/2026/09/18/ARTIvX36JZ2OCtmwMkmtZeVb260918.shtml",
    "https://news.cctv.com/2026/09/18/ARTI5LbyUPup8E9UmhFFXWu8260918.shtml",
    # [21] 广交会作用 商务部回应子稿（并入广交会主稿）
    "https://news.cctv.com/2026/09/18/ARTIiFXfck6baol3Rgaaf1UQ260918.shtml",
    # [23] gov.cn 要闻评论「持续做大做强先进制造业」
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081526.htm",
    # [25] 新华社特稿「中国十五五规划，为世界提供新机遇」
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081427.htm",
    # [29] 香港五年规划（9-16 版面已收，跨日重复）
    "https://news.cctv.com/2026/09/18/ARTIaIydMRfQZzw9JzmrhJxb260918.shtml",
    # [31][32][34][37] 产业综述 / 评论员文章 / 技术产业稿
    "https://news.cctv.com/2026/09/19/ARTIvpfYojxXg1CSdqb9pzhL260919.shtml",
    "https://news.cctv.com/2026/09/19/ARTI00tSFsamyvqUuZrqW0Qm260919.shtml",
    "https://news.cctv.com/2026/09/19/ARTIWvv3hUd4dPSnkWlCpYiE260919.shtml",
    "https://news.cctv.com/2026/09/19/ARTIH1ncSFdsXBGpxByARVJ8260919.shtml",
    # [33] 中国—东盟自贸区 3.0 版蓝皮书（9-17 事件，与 9-18 版面东博会线重复）
    "https://news.cctv.com/2026/09/19/ARTIx37yXbK6iYFKxSAwOk1h260919.shtml",
    # [38][39] 农业丰收栏目体 / 地方产业故事化
    "https://news.cctv.com/2026/09/18/ARTIxBnZqSjnlsETMAVWXfSx260918.shtml",
    "https://news.cctv.com/2026/09/19/ARTIEEawVjyPAP0vnNRmAqPU260919.shtml",
    # [40] 财政资金民生叙事稿
    "https://news.cctv.com/2026/09/19/ARTIvRhhCpSIQYOW1Ztd3DFs260919.shtml",
    # [41] 高技术产业引资（与「1—8月全国吸收外资」同源子角度）
    "https://news.cctv.com/2026/09/19/ARTIMBNlWoLuq8G3L6pfDgeV260919.shtml",
    # [01][06][11] 中美经贸磋商多源稿 → 并入综合条目（保留 gov.cn 官方主稿）
    "https://www.zaobao.com/news/china/story20260919-9700893",
    "https://www.zaobao.com/news/china/story20260919-9700923",
    "https://www.zaobao.com/news/china/story20260919-9700840",
]

kept = [it for it in today_items if it.get("url", "") not in DEL_URLS]
missing = [u for u in DEL_URLS if u not in by_url]
if missing:
    print("⚠️ 待删 URL 未命中（请核对）：")
    for u in missing:
        print("   ", u)

# ---------------------------------------------------------------- 修正
def setf(it, **kw):
    for k, v in kw.items():
        it[k] = v


# [05] 白宫公布习近平下周访美行程
setf(by_url["https://www.zaobao.com/news/china/story20260919-9701443"],
     priority_score=100, category="元首动态", date="2026-09-19",
     summary="白宫公布习近平访美行程：习近平与夫人彭丽媛将于9月23日抵达华盛顿特区外的安德鲁斯联合基地，"
             "特朗普将到机场迎接并共同出席在军事基地举行的欢迎仪式；9月24日两人在白宫会晤，"
             "随后在玫瑰园出席检阅仪式并进行双边会晤，特朗普傍晚在白宫东厅设国宴，"
             "贝索斯、奥尔特曼、库克、马斯克、黄仁勋等美国科技企业负责人将出席；"
             "9月25日特朗普伉俪与习近平伉俪茶叙后赴国家档案馆参阅美国建国文档，习近平当日启程回国。")

# [08] 李强主持召开国务院常务会议（中国政府网·要闻）
setf(by_url["https://www.gov.cn/yaowen/liebiao/202609/content_7081464.htm"],
     priority_score=95, category="高层动态", date="2026-09-18",
     summary="国务院总理李强9月18日主持召开国务院常务会议，听取老龄工作情况汇报，研究推动体育赛事健康发展有关工作，"
             "部署实施医疗康复护理扩容提升工程，审议通过《中医药传统知识保护条例（草案）》，"
             "讨论并原则通过《〈中华人民共和国突发事件应对法〉等15部法律的修正案（草案）》并将提请全国人大常委会审议。"
             "会议提出健全多层次多支柱养老保险体系、扩大普惠养老服务、培育银发消费新场景，"
             "增加高质量体育赛事供给并推动赛事与文化、旅游、商务融合发展，"
             "以基层为重点建强医疗康复护理服务体系，全面加强中医药传统知识保护管理。")

# [10] 赵乐际、王沪宁分别会见埃及参议长法里德
setf(by_url["http://paper.people.com.cn/rmrb/pc/content/202609/19/content_30181974.html"],
     priority_score=95, category="高层动态", date="2026-09-19",
     summary="全国人大常委会委员长赵乐际、全国政协主席王沪宁9月18日在北京分别会见埃及参议长法里德。"
             "赵乐际表示，本月初习近平主席对埃及成功进行历史性访问，两国元首一致同意推进中埃命运共同体建设；"
             "中国全国人大愿同埃及议会加强立法、监督等经验交流。王沪宁表示，中方愿同埃方落实好两国元首重要共识，"
             "深化共建“一带一路”和各领域务实合作，加强治国理政经验交流。")

# [13] 中美经贸磋商（综合条目：官方主稿 + 联合早报/路透多源贯通）
setf(by_url["https://www.gov.cn/yaowen/liebiao/202609/content_7081527.htm"],
     priority_score=95, category="高层动态", date="2026-09-19",
     source="中国政府网·要闻（综合）",
     title="何立峰将于9月19日至23日率团赴美举行中美经贸磋商",
     summary="经中美双方商定，中共中央政治局委员、国务院副总理何立峰将于9月19日至23日率团赴美国与美方举行经贸磋商，"
             "双方将以两国元首重要共识为引领，就彼此关心的经贸问题开展磋商（商务部新闻发言人答记者问，中国政府网）。"
             "据路透社引述知情人士，美国财政部长贝森特本周末在纽约与何立峰会晤，讨论人工智能、贸易、稀土等议题，"
             "美国贸易代表格里尔亦将参与；双方预计重点讨论延长11月10日到期的关税休战协议、改善中国稀土磁体与关键矿产供应。"
             "另据报道，中美正讨论降低或取消中国对美国液化天然气征收的15%关税，相关措施可能纳入一揽子能源和农业协议，"
             "双方还可能分别下调涉及约300亿美元商品的关税，但磋商尚未敲定。贝森特称愿就避免共同风险及避免两国体系分化展开讨论。")

# [15] 张文兵跨省履新江苏省委常委
setf(by_url["https://www.zaobao.com/news/china/story20260919-9701826"],
     priority_score=86, category="人事任免", date="2026-09-19",
     summary="中共中央批准，二十届中央候补委员、湖北省委常委、常务副省长张文兵任江苏省委委员、常委。"
             "张文兵现年54岁，安徽霍邱人，在职研究生学历、管理学博士，曾在安徽高校工作20余年，"
             "2016年进入中央部委，历任国家质检总局产品质量监督司司长、国家市场监管总局产品质量安全监督管理司司长、"
             "标准技术管理司司长，2020年赴湖北任副省长，2021年末任湖北省委常委、组织部部长，2025年6月转任常务副省长。")

# [16] 外交部 9-18 例行记者会（URL 死链修复 + 去导航残留 + 补实录要点）
setf(by_url["https://www.mfa.gov.cn/web/wjdt_674879/202609/t20260918_12025801.shtml"],
     url="https://www.mfa.gov.cn/web/fyrbt_673021/202609/t20260918_12025801.shtml",
     title="2026年9月18日外交部发言人郭嘉昆主持例行记者会",
     priority_score=85, category="部委动态", date="2026-09-18",
     summary="外交部发言人郭嘉昆9月18日主持例行记者会。就美国向中方返还64件（套）文物艺术品和古生物化石，"
             "郭嘉昆表示中美依据防止中国文物非法入境美国的政府间谅解备忘录开展务实合作，"
             "已实现超过20批次共700余件（套）流失美国文物回归，此次返还是落实两国元首北京会晤共识的最新成果。"
             "就中美高层交往，郭嘉昆表示中美双方就年内元首互动安排保持着沟通。"
             "针对日本历史问题“否认主义”倾向滋长蔓延，郭嘉昆表示绝不允许日本军国主义死灰复燃、绝不允许历史悲剧重演。")

# [17] 网信办涉企信息专项整治（源升级为网信办官网 + 第二批典型案例）
setf(by_url["https://www.zaobao.com/news/china/story20260919-9701222"],
     url="https://www.cac.gov.cn/2026-09/19/c_1791481878005956.htm",
     source="网信办", priority_score=88, category="部委动态", date="2026-09-19",
     title="国家网信办公开曝光“清朗·优化营商网络环境 整治恶意炒作涉企信息”专项行动第二批典型案例",
     summary="国家网信办通报“清朗·优化营商网络环境 整治恶意炒作涉企信息”专项行动进展：专项行动期间，"
             "各级网信部门和重点商业网站平台清理涉企侵权信息156万余条，处置违法违规账号2.6万余个，"
             "并有针对性治理企业“内卷式”竞争。通报的四类典型案例包括：发布涉企负面不实信息并要挟企业支付“宣传费”牟取非法利益；"
             "被行政处罚后拒不改正、持续散布贬损企业信息并挑动消费群体对立；在企业新品上市节点捏造散布经营困难、产品质量不佳等虚假信息；"
             "恶意集纳涉企负面信息、翻炒企业旧闻旧事。所涉账号已被依法依约关闭或采取处置措施。")

# [18] 商务部就欧盟希中国自愿限制混动汽车对欧出口答记者问
setf(by_url["https://news.cctv.com/2026/09/18/ARTIGq5b9ASmBg3OBy9viMiq260918.shtml"],
     url="https://www.mofcom.gov.cn/syxwfb/art/2026/art_836c456aba344f6abef9943ff5da5999.html",
     source="商务部", priority_score=85, category="部委动态", date="2026-09-18",
     summary="商务部新闻发言人就媒体称欧盟希望中国自愿限制混合动力汽车对欧出口答记者问，"
             "指出中方一贯主张通过对话协商妥善处理中欧经贸分歧，反对以所谓“产能过剩”为由采取贸易限制措施，"
             "强调中国新能源汽车产业的发展是技术创新、产业链完整和市场竞争的结果，"
             "希欧方恪守自由贸易原则、慎用贸易救济措施，共同维护中欧经贸合作大局。")

# [22] 应急管理部针对四川启动国家地质灾害四级应急响应
setf(by_url["https://news.cctv.com/2026/09/19/ARTI7oLw09QOHTYHenp2NXCB260919.shtml"],
     priority_score=85, category="部委动态", date="2026-09-19",
     summary="9月19日凌晨，四川攀枝花市盐边县格萨拉乡支六河村石家沟隧道附近突发泥石流，有人员失联。"
             "据气象部门预测，未来三天四川东北部有大雨、局地暴雨，经与自然资源部联合会商研判，"
             "四川东北部局部地区发生地质灾害的风险较高。根据《国家突发地质灾害应急预案》及有关规定，"
             "应急管理部启动国家地质灾害四级应急响应，并派出工作组赶赴现场指导抢险救援。")

# [26] 网信办未成年人网络保护规定征求意见（清导航残留）
setf(by_url["https://www.cac.gov.cn/2026-09/18/c_1791482017777471.htm"],
     priority_score=80, category="政策发布", date="2026-09-18",
     summary="国家互联网信息办公室就《国务院关于保障未成年人健康安全使用网络的规定（征求意见稿）》公开征求意见。"
             "征求意见稿依据未成年人保护法、网络安全法、个人信息保护法等法律制定，"
             "旨在加强未成年人网络保护、营造有利于未成年人身心健康的网络环境、保障未成年人合法权益，"
             "重点规范网络产品和服务提供者的未成年人保护义务、网络信息内容管理及个人信息处理等活动。")

# [27] 多部门联合印发通知稳妥推进煤矿复产达产
setf(by_url["https://news.cctv.com/2026/09/18/ARTIMZz6k8OIMQWT4LuirHiZ260918.shtml"],
     priority_score=80, category="政策发布", date="2026-09-18",
     summary="国家发展改革委、国家能源局等多部门近日联合印发通知，要求各产煤省份和煤炭企业"
             "在确保安全的前提下稳妥推进煤矿复产达产，全力做好煤炭稳产保供相关工作，"
             "保障今冬明春能源电力安全稳定供应，并统筹抓好安全生产与产能释放。")

# [28] 《文化产业发展“十五五”规划》
setf(by_url["https://news.cctv.com/2026/09/19/ARTIsV1cCSThTYWbKwWMWwkP260918.shtml"],
     priority_score=80, category="政策发布", date="2026-09-18",
     summary="文化和旅游部印发《文化产业发展“十五五”规划》，明确“十五五”时期文化产业发展的总体要求、重点任务和保障措施，"
             "从壮大文化市场主体、推动数字文化新业态发展、促进文化消费、加强文化贸易与交流合作等方面部署七方面重点任务，"
             "系统安排文化和旅游系统的文化产业发展工作，推动文化产业高质量发展。")

# [30] 1—8月全国吸收外资4799.5亿元（官方 URL 升级）
setf(by_url["https://news.cctv.com/2026/09/18/ARTIAgERJxInibsLwxvZMNO2260918.shtml"],
     url="https://www.mofcom.gov.cn/syxwfb/art/2026/art_a2d8ba8791a943fba8234fde09b443f4.html",
     source="商务部", priority_score=85, category="经贸动向", date="2026-09-18",
     summary="商务部数据显示，2026年1—8月全国新设立外商投资企业42582家，同比增长0.3%；"
             "实际使用外资金额4799.5亿元人民币，同比下降5.3%。制造业实际使用外资1195.5亿元，服务业3504.2亿元；"
             "高技术产业实际使用外资2002.6亿元，同比增长35.1%，占全国实际使用外资的41.7%，较去年同期提升12.4个百分点，"
             "其中研发与设计服务、科技成果转化服务、电子及通信设备制造业分别增长74%、64.2%、41.9%；"
             "法国、瑞士、韩国实际对华投资分别增长39.2%、16.7%、16.5%。")

# [35] 市场监管总局公布质量认证领域违法违规典型案例
setf(by_url["https://news.cctv.com/2026/09/18/ARTITeN5wanIA3xUWTvyf7vT260918.shtml"],
     priority_score=88, category="部委动态", date="2026-09-18",
     summary="市场监管总局公布质量认证领域违法违规典型案例。近年来市场监管部门持续加大质量认证领域违法行为查办力度，"
             "严厉打击认证机构出具虚假或严重失实认证结论、超出批准范围从事认证活动、减少遗漏认证程序等违法行为，"
             "此次公布的典型案例涉及多家认证机构及从业人员，旨在规范质量认证市场秩序，"
             "营造诚信守法、公平竞争的市场环境。")

# [36] 市场监管总局打击劣质低价专项行动
setf(by_url["https://news.cctv.com/2026/09/19/ARTI7MJGBT5tFBRL0lqljLzO260918.shtml"],
     priority_score=88, category="部委动态", date="2026-09-19",
     summary="市场监管总局通报打击劣质低价专项行动成效：各级市场监管部门深入整治劣质低价突出问题，"
             "共立案查处价格、竞争、质量、认证认可等领域违法案件2.9万件，罚没2.8亿元，退还群众1600余万元，"
             "重点治理以次充好、低价倾销、虚假宣传等扰乱市场秩序行为，维护公平竞争市场环境和消费者合法权益。")

# ---------------------------------------------------------------- 补录
ADD = [
    dict(
        title="第140届广交会将于10月15日至11月4日在广州举办",
        url="https://www.gov.cn/lianbo/202609/content_7081488.htm",
        source="中国政府网", category="重要会议", priority_score=88, date="2026-09-18",
        collectedAt=COLLECTED, keywords=[], is_summit_level=False,
        summary="国务院新闻办公室9月18日举行新闻发布会，介绍第140届中国进出口商品交易会有关情况。"
                "第140届广交会将于10月15日至11月4日分三期在广州举办，迎来创办70周年的重要时点。"
                "本届广交会3.2万家参展企业中，专精特新、单项冠军等优质企业超1.1万家，64%的参展企业应用工业互联网、人工智能等新技术，"
                "新产品和绿色产品占比分别达23.2%、26%，均创历史新高；首次推出22个智慧应用场景和16项AI特色应用，"
                "在国内展览业率先实现全馆展位级导航和展位AR信息展示，并首次在贸易服务展区实现10大类生产性服务业全覆盖。"
                "商务部部长助理张力介绍，已有196个国家和地区超21万名采购商预登记。",
    ),
    dict(
        title="美国向我国返还64件（套）文物艺术品和古生物化石",
        url="https://news.cctv.com/2026/09/18/ARTI0y2KJBSqHhFRyvurccGp260918.shtml",
        source="央视新闻", category="部委动态", priority_score=85, date="2026-09-18",
        collectedAt=COLLECTED, keywords=[], is_summit_level=False,
        summary="北京时间9月16日和18日，国家文物局在华盛顿、纽约分别接收美国国土安全调查局、"
                "纽约曼哈顿区检察官办公室向我国返还的2批次共计64件（套）文物艺术品和古生物化石，"
                "包括天龙山第17窟西壁北侧菩萨身躯以及造像、陶俑、恐龙骨架化石、鱼类化石、恐龙蛋化石等，"
                "均为美国执法部门在工作中查获。文化和旅游部副部长、国家文物局局长饶权代表中方签署返还接收确认书。"
                "中方表示，此次返还是中美两国在文化遗产领域共同贯彻落实中美元首北京会晤共识的最新成果，"
                "也是“中美建设性战略稳定关系”在人文领域的具体体现；依据2009年签署并连续3次续签的相关谅解备忘录，"
                "中美已实现超过20批次共700余件（套）流失美国文物回归中国。",
    ),
    dict(
        title="中央网信办印发《关于加强涉企侵权信息管理 持续推动营商网络环境优化的通知》",
        url="https://www.cac.gov.cn/2026-09/18/c_1791396347229199.htm",
        source="网信办", category="政策发布", priority_score=80, date="2026-09-18",
        collectedAt=COLLECTED, keywords=[], is_summit_level=False,
        summary="中央网信办秘书局9月15日印发《关于加强涉企侵权信息管理 持续推动营商网络环境优化的通知》。"
                "通知要求网站平台健全信息内容管理制度、完善优化平台社区规则，将涉企信息纳入日常内容审核处置范围，"
                "强化账号、MCN机构管理；明确重点清理涉企拉踩引战信息、集纳翻炒的企业旧闻旧事和负面信息、"
                "已被平台处置过的涉企侵权信息、机器人账号与网络水军账号发布的涉企评论信息，"
                "以及明显违背公序良俗抹黑诋毁企业、企业家的信息。网信部门要落实属地管理责任，"
                "对重视程度不足、落实力度不够特别是网民反映问题集中的网站平台依法依规从严处理。",
    ),
    dict(
        title="余晓晖出任工业和信息化部副部长",
        url="https://www.miit.gov.cn/xwfb/bldhd/art/2026/art_c6aff1cc2d094936aaca2f131389d3f8.html",
        source="工业和信息化部", category="人事任免", priority_score=86, date="2026-09-18",
        collectedAt=COLLECTED, keywords=[], is_summit_level=False,
        summary="据工业和信息化部9月18日党组会议和干部大会公开信息，中国信息通信研究院原院长、党委副书记余晓晖"
                "已出任工业和信息化部副部长（部领导），其排序位于副部长单忠德之后、总经济师高东升之前。"
                "余晓晖为教授级高级工程师、第十四届全国政协委员，长期从事电信网规划、信息通信产业、数字经济、"
                "工业互联网、人工智能与算力基础设施等领域研究，曾参与国家中长期科技发展规划、宽带中国、"
                "工业互联网等多项国家级重大规划的研究起草，2026年1月曾就前瞻布局和发展未来产业为中央政治局集体学习作讲解。",
    ),
    dict(
        title="中俄经贸合作分委会第二十九次会议召开",
        url="https://www.mofcom.gov.cn/syxwfb/art/2026/art_f7da35d851e64ae7a2bcd59e5550221c.html",
        source="商务部", category="经贸动向", priority_score=85, date="2026-09-18",
        collectedAt=COLLECTED, keywords=[], is_summit_level=False,
        summary="9月18日，商务部部长王文涛与俄罗斯经济发展部部长列舍特尼科夫以视频方式共同主持召开"
                "中俄总理定期会晤委员会经贸合作分委会第二十九次会议。双方就落实两国元首重要共识、"
                "推动双边经贸合作提质升级、扩大相互市场准入、深化能源矿产与互联互通等领域合作交换意见，"
                "会后共同签署《会议纪要》。",
    ),
    dict(
        title="中国—塔吉克斯坦政府间经贸合作委员会第十四次会议在杜尚别召开",
        url="https://www.mofcom.gov.cn/syxwfb/art/2026/art_62031a46718849c7ac2513a9d7cfa502.html",
        source="商务部", category="经贸动向", priority_score=85, date="2026-09-18",
        collectedAt=COLLECTED, keywords=[], is_summit_level=False,
        summary="9月18日，商务部副部长兼国际贸易谈判副代表凌激与塔吉克斯坦经济发展和贸易部部长阿卜杜拉赫蒙佐达"
                "在杜尚别市共同主持召开中塔政府间经贸合作委员会第十四次会议。凌激表示，中方愿与塔方一道积极落实"
                "《2030年前中塔经贸合作规划》，加快培育服务贸易、数字贸易、跨境电商等新业态，"
                "推动新版《中塔投资协定》赋能投资合作，发掘绿色矿产、清洁能源、数字经济、互联互通等领域合作潜能，"
                "并加强中国—中亚机制框架下合作。塔方表示中国是塔第一大贸易伙伴和投资来源地，愿扩大对华优质农产品出口、"
                "吸引更多中国企业赴塔投资。会后双方共同签署会议纪要。",
    ),
]

for a in ADD:
    kept.append(a)

# ---------------------------------------------------------------- 写回
archive[TODAY] = kept
d["todayCount"] = len(kept)

# stats 重算
total = sum(len(v) for v in archive.values())
summit = 0
for dt, items in archive.items():
    for it in items:
        if it.get("is_summit_level"):
            summit += 1
d["stats"] = {
    "totalArticles": total,
    "dateCount": len(d["dates"]),
    "latestDate": TODAY,
    "summitCount": summit,
    "todayCount": len(kept),
}
d["lastUpdated"] = "2026-09-19 17:10"

json.dump(d, open(JSON_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---------------------------------------------------------------- 校验
print(f"今日 {len(today_items)} → {len(kept)} 条（删 {len(today_items)-len(kept)+len(ADD)} / 补录 {len(ADD)}）")
bad_arch = [it["title"][:40] for it in kept
            if it.get("collectedAt") != COLLECTED or it.get("date") not in ("2026-09-18", "2026-09-19")]
print("归档违规:", bad_arch or "0")
no_sum = [it["title"][:40] for it in kept if not (it.get("summary") or "").strip()]
print("无摘要:", no_sum or "0")
tpl = [it["title"][:40] for it in kept if "发布：" in (it.get("summary") or "")]
print("模板摘要:", tpl or "0")
cats = {}
for it in kept:
    cats[it["category"]] = cats.get(it["category"], 0) + 1
print("分类分布:", cats)
ge85 = sum(1 for it in kept if (it.get("priority_score") or 0) >= 85)
print(f"≥85 分: {ge85}/{len(kept)} = {ge85*100//len(kept)}%")
print("元首级:", sum(1 for it in kept if (it.get("priority_score") or 0) >= 100))
print("日期集合:", sorted({it["date"] for it in kept}))
