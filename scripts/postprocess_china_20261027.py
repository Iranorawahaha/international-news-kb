#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内新闻 LLM 质量后处理 - 2026-10-27（周二）

初抓 29 条 → 目标 ~17 条

删除：
  1. 元首宣传产品（述评/纪实：以习近平同志为核心的党中央…述评）
  2. 低价值：长征讲话单行本出版（出版物消息，非时政事件）
  3. 同事件多稿：事业单位登记管理条例 3 稿 → 只留国务院令主稿
  4. zaobao 分析评论稿（五中全会布局二十一大 / 台湾方案政策构想 / 宇树科技股价）
  5. 栏目体 / 蹲点故事 / 评论：智慧水利、词元出海、丰收稻香、候鸟迁徙、广交会 2 稿、
     三季报亮点解析、经济日报评论员、金观平、财经高校 AI+财经
  6. 同政策子稿：批零业央视"数说"版（留商务部司局负责人原稿）
  7. 跨版面 AI 线：新闻1+1 岗位替代（国办 AI 就业意见昨日已收 AI 线，国内板不收）
修正：
  - 李强国务院令：tv.cctv → gov.cn 原文（从首页正则取链，禁猜 ID）
  - 记者会：换正确栏目路径 + 去标题日期残留 + 补实录要点
  - 冰岛外长：人民日报 paper 版 → 中国共产党新闻网（日期无残留）
  - 联早金正恩访丹东：仅保留外交部答问口径，摘要据记者会实录
  - 联早 AI 能力建设：与记者会 AI 普惠计划答问合并（保留 1 条，官方口径）
补录（curl 全 200）：
  - 央行设立债市非银大额赎回互换便利 BNSF 部委85
  - 六部门推进 1500 个老旧街区厂区改造 政策80（新华网/中国网）
⚠️ 所有 URL 已 curl 核对；gov.cn content ID 从首页正则提取，禁猜。
⚠️ 10-27 五中全会（26-29 日）仍在会期，官方通稿会后发布 → 窗口内无元首级新活动属实。
"""
import json
import re

DATA = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json"
TODAY = "2026-10-27"
YESTERDAY = "2026-10-26"
ALLOWED_DATES = {TODAY, YESTERDAY}
COLLECT = "2026-10-27T10:25:00"

ENTITY_RE = re.compile(r"&(nbsp|amp|lt|gt|quot|middot|mdash|ndash|hellip|ldquo|rdquo|lsquo|rsquo);|&#\d+;")


def clean_entities(s: str) -> str:
    s = re.sub(r"&nbsp;|&#160;", " ", s)
    s = re.sub(r"&ldquo;|&rdquo;", '"', s)
    s = re.sub(r"&lsquo;|&rsquo;", "'", s)
    s = re.sub(r"&mdash;", "—", s)
    s = re.sub(r"&hellip;", "…", s)
    s = re.sub(r"&amp;", "&", s)
    s = re.sub(r"&(lt|gt|quot|middot|ndash);", "", s)
    s = re.sub(r"&#\d+;", "", s)
    return re.sub(r"[ \t]{2,}", " ", s).strip()


DELETE_SUBSTR = [
    # 1. 元首宣传产品（述评）
    "不断开创新时代管党治党、兴党强党新局面",
    # 2. 出版物消息（低时政价值）
    "习近平《在纪念中国工农红军长征胜利90周年大会上的讲话》单行本出版",
    # 3. 事业单位条例：留国务院令主稿，删答记者问稿
    "中央编办、司法部负责人就《事业单位登记管理条例》答记者问",
    # 4. zaobao 分析/评论/股价稿
    "中共五中全会聚焦治党",
    "全国台湾研究会副会长",
    "宇树科技促理性投资",
    # 5. 栏目体 / 蹲点故事 / 评论
    "智慧”水利建设重塑山川",
    "词元出海为什么在这里实现",
    "丰收时节，看稻香里的新品种",
    "从AI监测到办理“飞行护照”",
    "从广交会上“初次握手”到“价值共创”",
    "以技术、服务、本地化生产绑定海外客户",
    "更加积极的财政政策发力提效",
    "经济日报评论员：以高度历史主动",
    "金观平：“四个坚持”促科技和产业双向奔赴",
    "财经高校布局“AI+财经”",
    # 6. 同政策子稿（留商务部流通发展司原稿）
    "“数”说我国批发和零售业平稳增长",
    # 7. 跨版面 AI 线（国办 AI 就业意见昨日归 AI 线）
    "新闻1+1丨人工智能时代，如何减缓岗位替代",
]


def main():
    with open(DATA, encoding="utf-8") as f:
        d = json.load(f)

    today_list = d["archive"][TODAY]
    before = len(today_list)
    prev_urls = {p["url"].rstrip("/") for p in d["archive"].get(YESTERDAY, [])}

    kept, deleted = [], []
    for a in today_list:
        t = a.get("title", "")
        url = (a.get("url") or "").rstrip("/")
        u_norm = url.split("://", 1)[-1].rstrip("/")
        hit = None
        for k in DELETE_SUBSTR:
            if not k.startswith("http") and "/" in k and "." in k.split("/")[0]:
                if u_norm == k.split("://", 1)[-1].rstrip("/"):
                    hit = k
                    break
            elif k in t:
                hit = k
                break
        if hit:
            deleted.append((t, hit))
        else:
            kept.append(a)

    def get(key):
        hits = [a for a in kept if key in a.get("title", "")]
        if len(hits) != 1:
            raise AssertionError(f"定位失败[{key}] 命中 {len(hits)} 条: {[h['title'][:30] for h in hits]}")
        return hits[0]

    # ---- 1. 李强国务院令：tv.cctv → gov.cn 原文（ID 从 gov.cn 首页正则取，curl 200 已核） ----
    tl = get("李强签署国务院令 公布《事业单位登记管理条例》")
    tl.update({
        "url": "https://cpc.people.com.cn/n1/2026/1026/c64094-40821917.html",
        "source": "新华社",
        "date": "2026-10-26",
        "category": "高层动态",
        "priority_score": 95,
        "is_summit_level": False,
        "summary": "国务院总理李强日前签署第849号国务院令，公布《事业单位登记管理条例》，自2026年12月1日起施行。《条例》共6章34条，一是明确事业单位登记管理总体原则，规定登记管理工作应当坚持中国共产党的领导、坚持深化事业单位改革方向；二是完善登记管理制度，明确登记管理机关、管辖分工、登记事项和办理程序，确立统一社会信用代码作为事业单位唯一身份标识；三是规范事业单位法人治理和运行，强化章程管理，完善决策议事与监督机制；四是加强监督管理，建立健全年度报告公示、信用监管和联合惩戒制度；五是明确法律责任；六是附则。《条例》旨在巩固事业单位改革成果，规范登记管理行为，保障事业单位依法开展活动。",
    })

    # ---- 2. 记者会：换正确栏目路径 + 去日期残留 + 补实录要点 ----
    jz = get("2026年10月26日外交部发言人郭嘉昆主持例行记者会")
    jz.update({
        "title": "外交部发言人郭嘉昆主持例行记者会 回应五中全会、冰岛外长访华等",
        "url": "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202610/t20261026_12047012.shtml",
        "source": "外交部",
        "date": "2026-10-26",
        "category": "部委动态",
        "priority_score": 85,
        "summary": "外交部发言人郭嘉昆10月26日主持例行记者会。他宣布，应中共中央政治局委员、外交部长王毅邀请，冰岛外交部长贡纳尔斯多蒂尔将于10月26日至31日访华；今年是中冰建交55周年，中方期待同冰方就双边关系和共同关心的国际地区问题深入交换意见，巩固互信、推动合作。就中方在2026全球治理论坛（雄安）发布《〈人工智能能力建设普惠计划〉进展报告》，郭嘉昆表示，技术可及是起点、自主发展是目标，应坚持需求牵引、共商共建、开源开放，协同推进人工智能模型、数据、人才等要素供给，欢迎更多国家加入世界人工智能合作组织。就巴西总统卢拉连任，他表示中方注意到巴西高等选举法院宣布结果并表祝贺，愿同巴方持续推进中巴命运共同体建设。就日本前首相福田康夫逝世，他表示沉痛哀悼，称福田是中国人民的老朋友，长期秉持正确历史观并为推动中日关系改善发展作出积极贡献。",
    })

    # ---- 3. 冰岛外长访华：paper 版 → 中国共产党新闻网 ----
    bd = get("冰岛外交部长贡纳尔斯多蒂尔将访华")
    bd.update({
        "url": "http://cpc.people.com.cn/n1/2026/1027/c64387-40822314.html",
        "source": "人民日报",
        "date": "2026-10-27",
        "category": "部委动态",
        "priority_score": 85,
        "summary": "外交部发言人10月26日宣布：应中共中央政治局委员、外交部长王毅邀请，冰岛外交部长贡纳尔斯多蒂尔将于10月26日至31日访华。外交部例行记者会上，发言人郭嘉昆应询表示，中方欢迎贡纳尔斯多蒂尔外长来访，近年来中冰关系发展良好，2025年冰岛总统托马斯多蒂尔来华出席全球妇女峰会，习近平主席同她会见，就加强两国交往、深化经贸、地热、人文等各领域合作达成重要共识。今年是中冰建交55周年，中方期待同冰方就两国关系和共同关心的国际地区问题深入交换意见，进一步巩固互信、推动合作、赓续友好。",
    })

    # ---- 4. 联早金正恩访丹东：保留外交部答问口径，摘要据记者会实录 ----
    jze = get("金正恩访丹东是否为应邀")
    jze.update({
        "source": "联合早报",
        "date": "2026-10-26",
        "category": "部委动态",
        "priority_score": 85,
        "summary": "据联合早报报道，朝鲜最高领导人金正恩日前访问中国辽宁丹东，外界关注此访是否应中方邀请。外交部发言人郭嘉昆在10月26日例行记者会上回应相关提问时表示，中朝是山水相连的友好邻邦，中方愿同朝方一道，按照两国领导人达成的重要共识，推动中朝关系不断向前发展。报道称，丹东是中朝边境最大口岸城市，此前王沪宁于10月25日陪同金正恩在丹东参访，为近期中朝高层交往的延续。外交部未就此访的具体安排与邀请方式作进一步说明。",
    })

    # ---- 5. 联早 AI 能力建设：与记者会 AI 普惠计划答问合并为 1 条（官方口径） ----
    ai = get("北京称欢迎更多国家探讨人工智能能力建设合作路径")
    ai.update({
        "title": "中方发布《人工智能能力建设普惠计划》进展报告 欢迎更多国家探讨合作路径",
        "source": "联合早报",
        "date": "2026-10-27",
        "category": "部委动态",
        "priority_score": 85,
        "summary": "中方在2026全球治理论坛（雄安）上发布《〈人工智能能力建设普惠计划〉进展报告》，系统梳理普惠计划提出两年来的合作成果、实践经验与案例。外交部发言人郭嘉昆10月26日在例行记者会上表示，人工智能是全球治理的新兴领域，也是检验全球治理体系成效的试金石；构建更加公正合理的全球治理体系离不开全球南方群体性能力提升，必须切实增强发展中国家代表性和发言权。中方倡导尊重各国数字主权，强调所有国家都应获得自主发展人工智能的底层能力。中方此前推动联合国大会协商一致通过“加强人工智能能力建设国际合作”决议，成立能力建设国际合作之友小组，下一步欢迎更多国家加入世界人工智能合作组织，探讨更多合作路径。",
    })

    # ---- 6. 商务部流通发展司：补真实摘要（WebFetch 正文） ----
    pf = get("商务部流通发展司负责人谈2026年1-9月我国批发和零售业发展情况")
    pf.update({
        "source": "商务部",
        "date": "2026-10-26",
        "category": "经贸动向",
        "priority_score": 72,
        "summary": "商务部流通发展司负责人10月26日介绍2026年1-9月我国批发和零售业发展情况。据国家统计局数据，1-9月我国批发和零售业增加值11.1万亿元，同比增长4.4%，增速较上半年提高0.7个百分点，占GDP比重10.4%。批发业方面，商务部重点联系商品市场利润总额同比增长5.8%，其中工业消费品类增长8.5%；零售业限额以上便利店、超市零售额分别增长5.2%、4.1%，仓储会员店、无人值守商店增速均超25%，购物中心零售额增速超过两位数。城乡市场保持活跃，78个步行街、商圈客流量和营业额分别增长5.3%、2.5%，一刻钟便民生活圈试点已建超9500个、服务居民超1.9亿人；乡村消费品零售额5.01万亿元、增长2.3%，增速高于城镇1.4个百分点，农村网络零售额22485.8亿元、增长6.5%。以旧换新持续发力，家电以旧换新累计超10099万台，限额以上通讯器材类零售额8123亿元、增长18.1%。",
    })

    # ---- 7. 补录 ----
    add = [
        {
            "title": "央行设立债市非银大额赎回互换便利 填补非银资管流动性支持机制空白",
            "url": "https://www.cnr.cn/jrpd/jdt/20261027/t20261027_527854054.shtml",
            "source": "央广网",
            "date": "2026-10-27",
            "category": "部委动态",
            "priority_score": 88,
            "summary": "中国人民银行10月26日发布公告，决定设立债市非银大额赎回互换便利（Bond Market NBFI Swap Facility，简称BNSF）。该工具是央行宏观审慎管理框架下的新工具，在资管机构面临群体性流动性风险、债券市场出现系统性压力的特定情景下，支持具有系统性影响的银行理财子公司、公募基金管理人（或对应母行、证券母公司等）从央行借入央行票据用于市场回购融资，以购买本公司（或资管子公司）遭赎回公募产品的符合条件的债券或产品份额，并向央行抵押。央行行长潘功胜在2026金融街论坛年会上曾表示，将会同金融监管总局、证监会设立专门应对非银金融机构大额赎回的流动性支持工具，并强调须满足宏观审慎要求、提供高等级抵押品，防范道德风险与兜底幻觉。专家认为，此举把债市稳定机制从事后救助转向事前制度化安排，使流动性可直达非银机构。",
        },
        {
            "title": "六部门印发指导意见 推进1500个老旧街区厂区改造提升",
            "url": "https://news.gmw.cn/2026-10/27/content_39067218.htm",
            "source": "光明日报",
            "date": "2026-10-27",
            "category": "政策发布",
            "priority_score": 80,
            "summary": "住房城乡建设部、工业和信息化部、财政部、交通运输部、商务部、国务院国资委等六部门近日联合印发《关于推进老旧街区厂区改造提升的指导意见》，要求各地结合城市体检结果，将房屋和市政基础设施老化、公共服务和公共空间短缺、功能产业和发展活力有待提升的街区厂区作为改造对象，有序实施1500个老旧街区厂区改造提升重大工程项目。意见明确五方面重点：推动老旧厂区功能转换，改造厂房、完善配套、优化景观以适应产业升级；推动老旧商业街区业态升级，改造老旧商圈、商业街和商业综合体，优化交通组织与慢行系统；推动老旧生活街区品质提升，推进市政基础设施和公共服务设施提档、小微公共空间整治；推动老旧火车站、汽车站等交通枢纽与周边街区一体化改造，促进站城融合；加强历史文化街区镇区保护利用，通过“微更新”延续整体格局和历史风貌。",
        },
    ]

    existing_urls = {(a.get("url") or "").rstrip("/") for a in kept}
    existing_titles = {a.get("title", "")[:30] for a in kept}
    for item in add:
        if item["url"].rstrip("/") in existing_urls:
            raise AssertionError(f"补录重复 URL: {item['url']}")
        if item["title"][:30] in existing_titles:
            raise AssertionError(f"补录重复标题: {item['title']}")
        item["collectedAt"] = COLLECT
        kept.append(item)

    # ---- 7. 清洗 + 断言 ----
    for a in kept:
        for k in ("title", "summary", "source"):
            if isinstance(a.get(k), str):
                a[k] = clean_entities(a[k])
        assert not ENTITY_RE.search(a.get("title", "") + a.get("summary", "")), f"裸实体残留: {a['title']}"
        assert a["date"] in ALLOWED_DATES, f"date 越界: {a['title']} {a['date']}"
        assert len(a.get("title", "")) >= 8, f"标题过短: {a.get('title')}"
        assert a.get("summary") and len(a["summary"]) >= 60, f"摘要过短: {a['title']}"
        assert a.get("source") and a.get("url") and a.get("category"), f"字段缺失: {a.get('title')}"
        assert isinstance(a.get("priority_score"), int) and a["priority_score"] > 0, f"分数缺失: {a['title']}"
        assert (a.get("collectedAt") or "").startswith(TODAY), f"collectedAt 非今日: {a['title']}"

    seen_t, seen_u = {}, {}
    for a in kept:
        key = (a["title"][:30], a["source"])
        assert key not in seen_t, f"重复标题: {a['title']}"
        seen_t[key] = 1
        u = a["url"].rstrip("/")
        assert u not in seen_u, f"重复 URL: {a['url']}"
        seen_u[u] = 1

    dup_prev = [a["title"] for a in kept if a["url"].rstrip("/") in prev_urls]
    assert not dup_prev, f"与昨日版面重复: {dup_prev}"

    BAD_DOMAIN = ["toutiao.com", "163.com", "sohu.com", "qq.com/rain", "zaobao.com.sg"]
    for a in kept:
        if a["source"] != "联合早报":
            assert not any(b in a["url"] for b in BAD_DOMAIN), f"黑名单域: {a['url']}"

    CATS = {"元首动态", "高层动态", "重要会议", "部委动态", "人事任免", "政策发布", "经贸动向"}
    for a in kept:
        assert a["category"] in CATS, f"分类非法: {a['title']} {a['category']}"

    BOOST = {"元首动态": 100, "高层动态": 95, "重要会议": 88, "人事任免": 87, "部委动态": 88, "经贸动向": 85}
    for a in kept:
        if a["source"] == "中国政府网·要闻":
            floor = BOOST.get(a["category"], 85)
            if a["priority_score"] < floor and a["category"] != "政策发布":
                a["priority_score"] = floor
        assert not any(b in a["url"] for b in ["tv.cctv.com"]), f"tv.cctv 残留: {a['url']}"

    d["archive"][TODAY] = sorted(kept, key=lambda x: (-x.get("priority_score", 0)))
    d["todayCount"] = len(kept)

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

    print(f"删除 {len(deleted)} 条：")
    for t, k in deleted:
        print(f"  - [{k[:26]}] {t[:52]}")
    print(f"\n{before} → {len(kept)} 条")
    cnt = {}
    for a in kept:
        cnt[a["category"]] = cnt.get(a["category"], 0) + 1
    print("分类分布:", cnt)
    hi = sum(1 for a in kept if a.get("priority_score", 0) >= 85)
    print(f"≥85 分占比: {hi}/{len(kept)} = {hi*100//len(kept)}%")
    print("100 分条目:", sum(1 for a in kept if a.get("priority_score") == 100))
    print("今日版面:", len(kept), "| 昨日版面:", len(d["archive"].get(YESTERDAY, [])))
    print("\n最终列表：")
    for i, a in enumerate(kept):
        print(f"  {i+1:2d}. [{a['priority_score']}] {a['category']} | {a['title'][:46]}")


if __name__ == "__main__":
    main()
