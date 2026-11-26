#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内看板 LLM 后处理 2026-11-26（V2.11 窗口：date ∈ {2026-11-25, 2026-11-26}）"""
import json, re, datetime, sys

DATA = "data/china-news.json"
ORIG = "data/china-news.json.bak-20261126-pre"
TODAY = "2026-11-26"
YEST = "2026-11-25"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

d = json.load(open(DATA, encoding="utf-8"))
# 幂等：始终从预处理的原始快照重跑
o = json.load(open(ORIG, encoding="utf-8"))
d["archive"][TODAY] = o["archive"][TODAY]
today_items = d["archive"][TODAY]
print(f"初始 {len(today_items)} 条")

# ---------- 1. 删除规则 ----------
DROP_TITLE_KW = [
    # 元首理论宣传产品/栏目体
    "一见·", "习言道", "此行间", "近镜头", "循着总书记足迹", "时习之",
    "总书记的人民情怀", "深刻领会", "学习贯彻党的二十届五中全会精神）",
    # 评论/方法论/栏目体
    "经济新方位", "八大重点任务看落实", "金观平", "人民论坛", "人民时评",
    "评论员观察", "数说经济", "晶采观察", "新华视评", "记者手记",
    "微镜头", "文化中国行", "XX观察", "民生一件事", "焦点访谈",
    "署名文章", "观察之一", "开好局起好步", "在基层】",
    # 地方叙事/蹲点
    "青岛以科技创新引领产业创新",
    # 台湾地方政治（联合早报微观）
    "沈伯洋", "蒋万安", "选前之夜", "双城论坛",
    # 地方琐事
    "方言被认定违纪",
    # 旧稿/与已收重复
    "王毅同英国外交大臣米利班德通电话",
    # 联合早报转述版（人民日报王毅会谈稿已收）
    "王毅：希望荷兰为中企提供公平透明可预期营商环境",
]
DROP_URL_KW = [
    "story20261125-10054978",  # 解码中华 陈吉宁
    "story20261125-10056195",  # 深圳金融风险
]

kept = []
dropped = []
for it in today_items:
    t = it["title"]
    hit = next((k for k in DROP_TITLE_KW if k in t), None)
    if not hit:
        hit = next((k for k in DROP_URL_KW if k in it["url"]), None)
    if hit:
        dropped.append((hit, t))
    else:
        kept.append(it)
print(f"删除 {len(dropped)} 条")
for k, t in dropped:
    print(f"  - [{k}] {t[:52]}")

# ---------- 2. 修正/升级（按 URL 或标题定位） ----------
def find(items, url_kw=None, title_kw=None):
    for it in items:
        if url_kw and url_kw in it["url"]:
            return it
        if title_kw and title_kw in it["title"]:
            return it
    return None

FIX = {
    # 记者会：死链前缀 wjdt_674879 → fyrbt_673021，补实录要点
    "fyrbt": dict(
        url_kw="t20261125_12066982",
        url="https://www.mfa.gov.cn/fyrbt_673021/202611/t20261125_12066982.shtml",
        title="外交部就神舟二十四号中巴联合飞行、美方加征关税、BBNJ秘书处选址等答问",
        summary="外交部发言人郭嘉昆11月25日主持例行记者会。就神舟二十四号中巴航天员联合飞行，他表示中国空间站首次迎来外籍航天员，是中国载人航天工程国际合作新的里程碑，习近平主席在贺电中指出两国航天员携手叩问苍穹是中巴深厚友谊的生动体现。就美方将宣布对中国等国商品加征关税，他强调关税战、贸易战不符合任何一方利益，双方应在平等、尊重、互惠基础上协商解决，所谓“产能过剩”是伪命题，反对以此为借口进行政治操弄。就美国支持比利时、智利合并申办《海洋生物多样性协定》秘书处，他指出美国既非《联合国海洋法公约》也非《协定》缔约国，对选址事宜没有发言权，比利时、智利此举至少存在6个“不符合”。",
        score=88, category="部委动态",
    ),
    # 中美农业工作组：补摘要 + 升 85
    "agri": dict(
        url_kw="art_6e6ac6c48c544802b6f2b68e4ef07522",
        summary="中美贸易理事会项下农业工作组首次会议11月25日在京举行。双方围绕农产品贸易便利化、检验检疫合作等议题交换意见，就推动双边农产品贸易稳定发展形成共识。该工作组系落实中美经贸磋商机制项下贸易理事会共识设立，是两国农业领域恢复机制化对话后的首次专门会议。",
        score=85, category="经贸动向",
    ),
    # 陈文清：留人民日报版，升 95 保持
    "chenwenqing": dict(
        url_kw="content_30193192",
        title="陈文清赴德国出席第六次中德高级别安全对话",
        summary="当地时间11月24日，第六次中德高级别安全对话在德国柏林举行，中共中央政治局委员、中央政法委书记陈文清与德国联邦总理府部长瓦尔肯共同出席并致辞。陈文清表示，在习近平主席与德国领导人重要共识引领下，中德关系保持良好发展势头，双方在坚持多边主义、维护地区和平稳定等问题上立场相近。对话期间双方就反恐、网络安全、打击跨国有组织犯罪等议题深入交换意见，并就下阶段安全领域合作作出安排。",
    ),
    # 6G 两条合并保留一条（国家层面）
    "6g": dict(
        url_kw="ARTInN6WvdEasuPV2lOFeuk8261125",
        title="工信部启动6G创新发展部省协同试点 多地获批开展",
        summary="工业和信息化部11月24日正式启动6G创新发展部省协同试点，8个省市获批开展试点工作。试点将推动6G技术走出实验室，在更多场景开展创新、培育与拓展，探索特色化发展路径，为未来商用落地提供支撑。全国按“一盘棋”思路统筹推进6G创新，重点围绕技术验证、应用场景培育和产业生态构建展开，浙江等地已明确先行先试方案。",
        score=85, category="部委动态",
    ),
}

for key, cfg in FIX.items():
    it = find(kept, url_kw=cfg.get("url_kw"))
    if not it:
        print(f"  ⚠️ FIX 未命中: {key}")
        continue
    for f in ("url", "title", "summary", "score", "category"):
        if f in cfg:
            it["priority_score" if f == "score" else f] = cfg[f]
    print(f"  ✏️ FIX {key}: ok")

# 6G 重复：删掉另一条
kept = [x for x in kept if "ARTITe3MhkGWyVfAD9RjTDt6261125" not in x["url"]]

# 国台办发布会 3 条 → 合并 1 条综合
gtb = [x for x in kept if "国台办" in x["title"]]
if len(gtb) >= 2:
    base = gtb[0]
    base["title"] = "国台办回应两岸经贸合作与“台独”分裂行径：政治操弄徒劳无功"
    base["summary"] = ("国务院台办11月25日举行例行新闻发布会。发言人张晗表示，大陆产业门类齐全、供应链完整，"
                       "任何图谋“脱钩断链”、唱衰两岸经济合作的政治操弄都徒劳无功；国台办与中国进出口银行已签署"
                       "《“十五五”时期促进两岸融合发展金融合作协议》，将从金融层面支持台胞台企在大陆发展。"
                       "针对“台独”分裂言行，张晗强调搞“台独”分裂没有市场更没有出路，维护两岸同胞共同利益是两岸关系发展的根本出发点。")
    base["score"] = base["priority_score"] = 85
    base["category"] = "部委动态"
    base["urls"] = [x["url"] for x in gtb]
    base["items"] = [{"media": x["source"], "title": x["title"]} for x in gtb]
    for x in gtb[1:]:
        kept.remove(x)
    print(f"  🔗 国台办 {len(gtb)} 合 1")

# ---------- 3. 补录 ----------
def mk(title, url, source, date, category, score, summary, **kw):
    o = dict(title=title, title_en="", summary=summary, source=source, category=category,
             url=url, priority_score=score, importance="高" if score >= 88 else "中",
             date=date, collectedAt=NOW, is_summit_level=score >= 100)
    o.update(kw)
    return o

ADD = [
    # 神舟二十四号（11-25 08:18 发射，联播主档，脚本漏采）—— 与贺电同事件但从"任务执行"角度，独立成条
    mk("神舟二十四号载人飞船发射取得圆满成功 中外航天员首次“太空会师”",
       "https://news.cctv.com/2026/11/25/ARTIqTnc7WJ08MdPRh5mRRsm261125.shtml",
       "央视新闻", "2026-11-25", "高层动态", 95,
       "11月25日8时18分，搭载神舟二十四号载人飞船的长征二号F遥二十四运载火箭在酒泉卫星发射中心点火发射，约10分钟后船箭分离、进入预定轨道，发射取得圆满成功。飞船于11时56分成功对接天和核心舱前向端口，对接历时约3.5小时；14时35分神舟二十三号乘组打开“家门”，汤洪波、武毅和巴基斯坦航天员穆罕默德·齐尚·阿里顺利入驻中国空间站，中外航天员实现首次“太空握手”，这是中国航天史上第9次“太空会师”，也是“天宫”首次迎来外籍航天员。任务期间计划开展90项科学实验和技术试验，涵盖空间生命科学、空间材料科学、微重力流体物理与燃烧科学等领域。"),
    # 中长期护理保险
    mk("我国加快推进长期护理保险制度建设 2028年底前基本实现全国全覆盖",
       "https://www.gov.cn/yaowen/liebiao/202611/content_7087310.htm",
       "中国政府网", "2026-11-25", "政策发布", 85,
       "2026年度长期照护师职业技能等级认定第四次省际联考近日举行，全国2.6万余名考生报名参加。国家医保局持续推动长期照护师队伍建设，为全面推开长期护理保险制度夯实人才基础。按计划，到2028年底长期护理保险将基本实现全国全覆盖，为失能人员提供基本生活照料和相关医疗护理保障。"),
    # 中葡经贸混委会
    mk("中国—葡萄牙经贸混委会第11次会议在里斯本召开",
       "https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_5a6820746b0f4c6eb86270bf2309e6d9.html",
       "商务部", "2026-11-25", "经贸动向", 85,
       "11月24日，商务部副部长兼国际贸易谈判副代表凌激与葡萄牙经济与国土融合部经济国务秘书费雷拉在里斯本共同主持召开中葡经贸混委会第11次会议。凌激表示，中葡经贸合作韧性强、动力足，双方在绿色能源、基础设施、金融保险等领域标志性项目顺利实施，中方愿扩大进口葡优质产品和技术，深化科技创新、数字经济、服务贸易、跨境电商及第三方市场合作，并希望葡方作为欧盟成员为中欧经贸关系稳定健康发展发挥建设性作用。费雷拉表示中国是葡在亚洲最大贸易伙伴，希中方扩大进口葡优质农产品、对葡开展绿地投资，葡方将为中国投资者提供公平、非歧视营商环境。"),
    # 三峡水运新通道
    mk("国家发展改革委召开会议 研究推进三峡水运新通道建设",
       "https://www.ndrc.gov.cn/xwdt/xwfb/202611/t20261125_1409064.html",
       "国家发改委", "2026-11-25", "部委动态", 85,
       "国家发展改革委11月25日组织召开三峡水运新通道建设有关会议，研究推进项目前期工作与建设实施安排。三峡水运新通道是长江黄金水道扩能的关键工程，建成后将缓解三峡船闸通过能力饱和问题，提升长江上游地区与中下游的物流通道效率，对推动长江经济带高质量发展、降低全社会物流成本具有支撑作用。"),
    # 中欧宏观经济政策对话
    mk("第十次中欧宏观经济政策对话举行 王昌林与欧盟总司长共同主持",
       "https://www.ndrc.gov.cn/xwdt/xwfb/202611/t20261125_1409066.html",
       "国家发改委", "2026-11-25", "经贸动向", 85,
       "国家发展改革委副主任王昌林与欧盟委员会经济与金融事务总司长沃威11月25日共同主持第十次中欧宏观经济政策对话。双方围绕中国与欧盟宏观经济形势、财政货币政策取向、结构性改革进展及全球经济治理等议题深入交换意见，就加强宏观政策沟通协调、共同维护多边贸易体制和国际经济秩序形成共识。该对话机制是中欧在经济财金领域开展政策交流的常态化渠道。"),
    # 全民国防教育规划（印发主稿+答记者问合一，删答问子稿）
    # 该条已在池中，仅升级
]

SUM_FIX = {
    "扎尔达里": "11月25日，国家主席习近平同巴基斯坦总统扎尔达里互致贺电，就中巴航天员执行联合飞行任务表示祝贺。习近平指出，两国航天员携手叩问苍穹，是中巴深厚友谊的生动体现，也是两国合作新的重要成果。当日神舟二十四号载人飞船发射成功，巴基斯坦航天员穆罕默德·齐尚·阿里成为中国空间站首位到访的外籍航天员，中巴航天合作由此拓展至载人飞行新领域。",
    "陈文清：": "当地时间11月24日，第六次中德高级别安全对话在德国柏林举行，中共中央政治局委员、中央政法委书记陈文清出席。陈文清表示，中方愿同德方共同促进国际和地区和平稳定，在坚持多边主义、维护地区安全、打击跨国有组织犯罪等领域深化务实合作，推动中德全方位战略伙伴关系健康稳定发展。",
    "新公海": "外交部发言人郭嘉昆11月25日表示，美国既不是《联合国海洋法公约》缔约国，也不是《海洋生物多样性协定》缔约国，对《协定》秘书处选址事宜没有发言权。中方指出比利时、智利合并申办存在不符合协定规定、不符合程序正义等6个“不符合”，秘书处选址应由缔约方大会集体决定，反对将申办工作政治化、对抗化。",
    "三峡水运": "国家发展改革委11月25日组织召开三峡水运新通道建设有关会议，研究推进项目前期工作与建设实施安排。三峡水运新通道是长江黄金水道扩能的关键工程，建成后将缓解三峡船闸通过能力饱和问题，提升长江上游与中下游物流通道效率，对推动长江经济带高质量发展、降低全社会物流成本具有支撑作用。",
    "邓锡军": "外交部亚洲事务特使邓锡军11月26日同缅甸民族团结与实现和平协商委员会秘书敏乃举行会谈，双方就缅甸局势、推动政治对话与民族和解进程等议题交换意见。中方重申尊重缅甸主权与领土完整，支持缅甸各方通过和平协商解决分歧，愿继续为缅方维护稳定、发展经济提供力所能及的帮助。",
    "产能过剩是伪命题": "针对美方将宣布对中国等国商品加征关税，外交部发言人郭嘉昆11月25日回应称，中美经贸问题上的立场一贯明确，关税战、贸易战不符合任何一方利益，双方应在平等、尊重、互惠基础上协商解决。所谓“产能过剩”是伪命题，中方反对以此为借口进行政治操弄，中美应共同落实好两国元首达成的重要共识，维护经贸关系稳定发展态势。",
    "全社会用电量": "国家能源局数据显示，前10个月全社会用电量保持平稳增长，其中高端制造业、互联网数据服务业用电量增长较快，反映新质生产力加快形成。用电结构持续优化，高技术及装备制造业用电增速明显高于全社会平均水平，数据中心、算力等新型基础设施用电需求成为新的增长点。",
    "日本关西": "日本关西经济界人士表示，日中关系对双方都十分重要，两国经济互补性强，本可互利双赢。关西地区与中国经贸往来密切，企业界普遍希望双方保持沟通、稳定经贸合作环境，避免政治因素干扰正常商业活动，在绿色低碳、老龄化服务、第三方市场等领域拓展合作空间。",
    "朱光耀": "财政部原副部长朱光耀表示，人工智能时代的竞争关键在于规则制定权，亚洲国家应有紧迫感，但无须照搬欧美路径。他主张亚洲经济体在数据治理、AI安全标准、跨境算力合作等方面加强协调，形成符合本地区发展阶段和治理理念的规则方案，提升在全球AI治理中的话语权。",
    "李成钢": "商务部国际贸易谈判代表兼副部长李成钢表示，中国坚定维护以世界贸易组织为核心的多边贸易体制，反对单边主义和保护主义。中方支持对世贸组织进行必要改革，推动争端解决机制恢复正常运转，愿与各成员共同维护全球产业链供应链稳定畅通，为世界经济增长注入确定性。",
    "王昌林": "国家发展改革委副主任王昌林与欧盟委员会经济与金融事务总司长沃威11月25日共同主持第十次中欧宏观经济政策对话。双方围绕中欧宏观经济形势、财政货币政策取向、结构性改革及全球经济治理等议题深入交换意见，就加强宏观政策沟通协调、维护多边贸易体制形成共识。",
    "6G迈向产业落地": "8个省市获批开展6G创新发展部省协同试点，标志着6G技术将走出实验室，在更多场景开展创新、培育与拓展，探索特色化发展路径，为未来商用落地提供支撑。作为试点之一，浙江将在应用场景开放、测试验证平台建设等方面先行先试，推动6G与垂直行业融合。",
}

for it in ADD:
    # 仅替换同一条目（同一 URL）的旧稿，避免误删同主题不同稿件
    dup = [x for x in kept if x["url"] == it["url"]]
    for x in dup:
        kept.remove(x)
        print(f"  ♻️ 替换旧稿: {x['title'][:38]}")
    kept.append(it)
    print(f"  ➕ ADD {it['title'][:40]}")

# ---------- 4. 全民国防教育：留主稿删答问子稿 ----------
gfd = [x for x in kept if "全民国防教育" in x["title"]]
if len(gfd) >= 2:
    main = next((x for x in gfd if "答记者问" not in x["title"]), gfd[0])
    for x in gfd:
        if x is not main:
            kept.remove(x)
    main["score"] = main["priority_score"] = 88
    main["category"] = "政策发布"
    main["summary"] = ("中央宣传部、中央军委国防动员部近日联合印发《全民国防教育“十五五”规划》，明确“十五五”时期全民国防教育的总体要求、重点任务和保障措施。"
                       "《规划》是新时代全民国防教育领导体制机制改革以来、新修订的《国防教育法》颁布实施后首次出台的五年规划，"
                       "围绕健全领导体制、完善教育体系、加强阵地建设、强化保障措施等作出系统部署，强调推动全民国防教育对象、地域、时间、内容、手段“五个全覆盖”。")
    print("  🔗 全民国防教育 2 合 1")

# ---------- 5. 修正分类 ----------
for it in kept:
    if "涉案金额超150亿元" in it["title"]:
        it["category"] = "部委动态"
        it["priority_score"] = 85
    if "高质量认证项目" in it["title"]:
        it["category"] = "部委动态"; it["priority_score"] = 85
    if "数字产业收入" in it["title"]:
        it["category"] = "经贸动向"; it["priority_score"] = 85
    if "个人信息保护合规审计" in it["title"]:
        it["category"] = "部委动态"; it["priority_score"] = 85
    if "财政等五部门" in it["title"] or "帮扶资金绩效评价" in it["title"]:
        it["category"] = "政策发布"; it["priority_score"] = 80
    if "提升粮食安全保障能力" in it["title"]:
        it["category"] = "政策发布"; it["priority_score"] = 80
    if "用电量" in it["title"]:
        it["category"] = "经贸动向"; it["priority_score"] = 80
    if "海洋产业投融资" in it["title"]:
        it["category"] = "政策发布"; it["priority_score"] = 80
    if "朱光耀" in it["title"] or "日本关西" in it["title"]:
        it["category"] = "经贸动向"; it["priority_score"] = 72
    if "李成钢" in it["title"]:
        if not it["summary"]:
            it["summary"] = SUM_FIX["李成钢"]
        it["category"] = "经贸动向"; it["priority_score"] = 72

# 同事件跨源分岔：陈文清（人民日报）vs 联合早报转述 → 只留人民日报版
_cwq = [x for x in kept if "陈文清" in x["title"]]
if len(_cwq) > 1:
    _keep = next((x for x in _cwq if x["source"] == "人民日报"), _cwq[0])
    if not _keep.get("summary"):
        _keep["summary"] = SUM_FIX["陈文清："]
    for x in _cwq:
        if x is not _keep:
            kept.remove(x)
    print("  🔗 陈文清 2 合 1")


# ---------- 5b. 摘要补全（人民日报稿去首句电头；无摘要按事实重写） ----------
def clean_sum(s):
    s = (s or "").replace("&nbsp;", " ").replace("&amp;nbsp;", " ")
    s = re.sub(r"^新华社北京1?1?月\d+日电\s*", "", s)
    s = re.sub(r"^本报北京1?1?月\d+日电\s*（[^）]*）\s*", "", s)
    s = re.sub(r"^本报柏林1?1?月\d+日电\s*（[^）]*）\s*", "", s)
    return re.sub(r"\s{2,}", " ", s).strip()



for it in kept:
    s = clean_sum(it.get("summary"))
    for k, v in SUM_FIX.items():
        if k in it["title"]:
            s = v
            break
    it["summary"] = s


# ---------- 6. 去重（URL / title[:30]） ----------
seen, final = set(), []
for it in kept:
    k1 = it["url"].strip().rstrip("/").lower()
    k2 = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", it["title"])[:30]
    if k1 in seen or k2 in seen:
        print(f"  ⏭️ 重复删除: {it['title'][:40]}")
        continue
    seen.add(k1); seen.add(k2)
    final.append(it)

# ---------- 7. 断言 ----------
errs = []
for it in final:
    if not it.get("url") or not it.get("title") or not it.get("source"):
        errs.append(f"字段缺失: {it.get('title')}")
    if len(it["title"]) < 8:
        errs.append(f"标题过短: {it['title']}")
    if it["collectedAt"][:10] != TODAY:
        errs.append(f"collectedAt≠今日: {it['title']}")
    if it["date"] < YEST:
        errs.append(f"date越界: {it['title']} {it['date']}")
    if "&nbsp;" in (it.get("summary") or "") or "&amp;nbsp;" in (it.get("summary") or ""):
        errs.append(f"裸HTML实体: {it['title']}")
    if len((it.get("summary") or "")) < 60:
        errs.append(f"摘要过短: {it['title']}")
    if re.search(r"(官方信源|发布$)", it.get("summary") or "") and len(it.get("summary") or "") < 80:
        errs.append(f"模板摘要: {it['title']}")

if errs:
    print("\n❌ 断言失败：")
    for e in errs:
        print("  ", e)
    sys.exit(1)

final.sort(key=lambda x: (-x["priority_score"], x["title"]))
d["archive"][TODAY] = final
d["todayCount"] = len(final)
d["lastUpdated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
tot = sum(len(v) for v in d["archive"].values())
d["stats"] = d.get("stats") or {}
d["stats"]["total"] = tot
d["stats"]["today"] = len(final)
d["stats"]["highPriority"] = sum(1 for x in final if x["priority_score"] >= 85)

json.dump(d, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

from collections import Counter
cats = Counter(x["category"] for x in final)
print(f"\n✅ 最终 {len(final)} 条（总 {tot}）")
print("   分类:", dict(cats))
print("   ≥85:", sum(1 for x in final if x["priority_score"] >= 85), f"/{len(final)}")
print("   100分:", sum(1 for x in final if x["priority_score"] >= 100))
for i, x in enumerate(final, 1):
    print(f"  {i:2d}|{x['priority_score']:3d}|{x['category']}|{x['date']}|{x['source']}|{x['title'][:52]}")
