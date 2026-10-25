#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内新闻 LLM 质量后处理 - 2026-10-25（周日）

初抓 32 条 → 目标 ~22 条

删除：
  1. 元首宣传产品 / 人物特写（"一见·总书记这样数说长征"、"经纬线·让总书记驻足的长征故事"）
  2. 反响稿（重要讲话引发热烈反响）
  3. 同事件多稿（比利时贺信 cctv 两稿 → 保留 MFA 版；商务部美投资限制 cctv 两稿 + zaobao 一稿 → 保留商务部原件）
  4. 金正恩访丹东三稿（人民日报 / zaobao）→ 保留 MFA 详版
  5. 地震救援三稿（10-24 抢险 / 10-25 物资 / gov.cn 落实）→ 合并 1 条
  6. 栏目体 / 蹲点故事（纱线千亿集群、图木舒克产业富民、集成式出海、低空经济）
  7. 评论体（中国经济面面观·出口首破8万亿）
  8. 联合早报微观 / 台湾地方政治（台湾特稿 AI 介选、庄兆林履新江西三把手、靳伟履新湖南省委副书记）
  9. 部委级以下例行（翟隽会见沙特外交部顾问、青海杂多 5.3 级地震水利部调度、福建终止防台风响应）
修正：
  - 全面从严治党纪实：tv.cctv 反响稿 → 昨日版面已收 gov.cn 版，本日删除
  - 王沪宁陪同金正恩访丹东：人民日报 → MFA 详版
  - 唐登杰当选山西省委书记 / 陈小江当选新疆党委书记：补真实摘要
  - 《国家信息化"十五五"规划》：人民日报版 → gov.cn 7084172（昨日版面已收，本日删除）
  - 南方区域电力市场：补联播快讯口径摘要
补录（curl 全 200）：
  - 湖南、云南省委主要负责同志职务调整 人事86（新华社，王志军/莫高义）
  - 陈文清主持召开扫黑除恶专题会议 高层95（gov.cn 7084229）
  - 商务部就美新版对外投资限制拟议规则答记者问 部委88（mofcom 原件，脚本漏采）
  - 二十届中央第八轮巡视对象公布 部委88（32 家单位）
  - 民航 2026/2027 冬春航季 10-25 起执行 部委85
  - 2027 年度中央机关公开遴选和公开选调公务员 政策80
⚠️ 所有 URL 已 curl 核对；MFA 直链必须含 202610/ 月份段。
"""
import json
import re

DATA = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json"
TODAY = "2026-10-25"
YESTERDAY = "2026-10-24"
ALLOWED_DATES = {TODAY, YESTERDAY}
COLLECT = "2026-10-25T19:45:00"

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
    # 1. 元首宣传产品 / 人物特写 / 反响稿
    "一见·总书记这样“数”说长征",
    "经纬线·让总书记驻足的长征故事",
    "习近平主席在纪念中国工农红军长征胜利90周年大会上的重要讲话引发热烈反响",
    "永葆赶考清醒 赢得历史主动",                       # 昨日版面已收 gov.cn 7084202
    # 2. 同事件多稿：比利时贺信（保留 MFA 版，两条 cctv 皆删）
    "news.cctv.com/2026/10/25/ARTITF76RZgwurzPRQeZ9Jb1261025.shtml",
    "news.cctv.com/2026/10/25/ARTIpf9mifVZpLFlAPpXT1zw261025.shtml",
    "习近平向2026全球治理论坛（雄安）致信",              # 昨日版面已收 gov.cn 7084127
    # 3. 同事件多稿：商务部美投资限制（保留 mofcom 原件）
    "商务部：美歧视性扩大对华投资限制范围 坚决反对！",
    "美拟扩大对华投资限制 中国商务部：损害美企自身利益",
    "news.cctv.com/2026/10/24/ARTIBezOZOj8fpWS6GvysrtH261024.shtml",  # cctv 简版，保留 mofcom 原件
    # 4. 金正恩访丹东（MFA 详版保留；此处只删 zaobao 版，人民日报版走 FIX 换 URL）
    "王沪宁陪同金正恩访丹东 参观抗美援朝纪念馆和车厂",
    # 5. 地震救援合并
    "西藏巴青地震救灾物资陆续集结 伤员得到有序救治",
    "西藏那曲市巴青县7.0级地震抢险救灾工作加紧进行",
    # 6. 栏目体 / 蹲点故事
    "一根纱线“缝”出千亿级产业集群",
    "新疆图木舒克：产业富民“润”戈壁",
    "期待值拉满！从卖零件到卖整房",
    "解锁长空之上的“生命密钥”",
    # 7. 评论体
    "中国经济面面观丨出口首破8万亿",
    # 8. 联合早报微观 / 台湾地方政治
    "台湾特稿：从助选到介选",
    "庄兆林履新江西省委三把手",
    "北京副市长靳伟履新湖南省委副书记",
    "陈文清：推进“打伞破网”“打财断血” 铲除黑恶势力滋生土壤",   # zaobao 版，保留 gov.cn 7084229 主稿
    # 9. 部委级以下例行 / 弱政务
    "中国政府中东问题特使翟隽会见沙特外交部顾问哈立德亲王",
    "青海省玉树州杂多县发生5.3级地震",
    "福建省终止防台风应急响应",
    # 10. 与昨日版面重复 / 栏目体
    #   《国家信息化"十五五"规划》：昨日版面已收 gov.cn 7084172，本条人民日报版保留为不同信源重复→删除
    "paper.people.com.cn/rmrb/pc/content/202610/25/content_30187517.html",
    "扩投资、促消费、强数字动能 一组数据展现今年前三季度经济活力",
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
            if "." in k.split("/")[0] and "/" in k:      # URL 型键（含域名，去协议形式）
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

    # ---- 1. 王沪宁陪同金正恩访丹东：MFA 详版 ----
    wang = get("王沪宁陪同朝鲜最高领导人金正恩访问丹东")
    wang.update({
        "url": "www.mfa.gov.cn/web/wjdt_674879/gjldrhd_674881/202610/t20261024_12046338.shtml",
        "source": "外交部",
        "date": "2026-10-24",
        "category": "高层动态",
        "priority_score": 95,
        "summary": "2026年10月24日，中共中央政治局常委、全国政协主席王沪宁陪同朝鲜劳动党总书记、国务委员会委员长金正恩访问丹东，转达习近平总书记、国家主席的亲切问候和良好祝愿。当天上午，王沪宁在抗美援朝纪念馆广场迎接并陪同金正恩向抗美援朝纪念塔敬献花篮，现场奏响中朝两国国歌，花篮缎带上用朝文书写“永远铭记中国人民志愿军烈士”，全体人员向中国人民志愿军烈士默哀。随后，王沪宁陪同金正恩参观抗美援朝纪念馆，并考察丹东当地企业。金正恩表示，朝中两国是唇齿相依的友好邻邦，愿同中方一道，把两党两国老一辈领导人缔造的朝中传统友谊不断传承发扬下去。",
    })

    # ---- 2. 唐登杰当选山西省委书记：补真实摘要 ----
    td = get("唐登杰当选中共山西省委书记")
    td.update({
        "source": "人民日报",
        "date": "2026-10-25",
        "category": "人事任免",
        "priority_score": 86,
        "summary": "中国共产党山西省第十二届委员会第九次全体会议10月24日在太原举行，全会通过了关于调整省委书记的决定，选举唐登杰同志为中共山西省委委员、常委、书记。唐登杰此前任山西省委副书记、省长，长期在工业和信息化部、国家发展改革委等部门及地方工作，曾担任工业和信息化部副部长、国家国防科技工业局局长等职务。全会强调，要深入学习贯彻党的二十届四中全会精神，紧紧围绕“十五五”规划编制实施，扎实做好煤炭产业绿色转型、能源革命综合改革试点、黄河流域生态保护等重点工作，奋力谱写中国式现代化山西篇章。",
    })

    # ---- 3. 陈小江当选新疆党委书记：补真实摘要 ----
    cxj = get("陈小江当选新疆维吾尔自治区党委书记")
    cxj.update({
        "source": "人民日报",
        "date": "2026-10-25",
        "category": "人事任免",
        "priority_score": 86,
        "summary": "中共新疆维吾尔自治区第十届委员会第十次全体会议10月24日在乌鲁木齐举行，全会选举陈小江同志为中共新疆维吾尔自治区委员会书记。陈小江此前任新疆维吾尔自治区党委副书记、自治区主席，曾长期在水利系统工作，担任过水利部副部长、国家民族事务委员会主任等职务。全会强调，要完整准确全面贯彻新时代党的治疆方略，坚持以铸牢中华民族共同体意识为主线，扎实推动新疆经济社会高质量发展，深化对外开放和丝绸之路经济带核心区建设，深入推进文化润疆，坚决维护社会稳定和长治久安。",
    })

    # ---- 4. 南方区域电力市场：补联播快讯口径摘要 ----
    dl = get("南方区域电力市场顺利“转正”")
    dl.update({
        "source": "央视新闻",
        "date": "2026-10-24",
        "category": "经贸动向",
        "priority_score": 85,
        "summary": "10月24日，南方区域电力市场正式运行，成为我国首个正式运行的区域电力市场。该市场打通广东、广西、云南、贵州、海南五个省区的电力市场，把水电、风电、火电等各类电源放到一个市场里买卖，按同一套规则竞价交易、统一出清，电力交易更加便捷、灵活。此前南方区域电力市场已开展长周期结算试运行，实现了跨省区电力资源的市场化配置，水电富集时段可向缺电省份送电，新能源大发时段可通过市场消纳，有效提升区域电力资源优化配置能力和清洁能源利用率。",
    })

    # ---- 5. 补录 ----
    add = [
        {
            "title": "习近平同比利时国王菲利普就中比建交55周年互致贺信",
            "url": "www.mfa.gov.cn/web/wjdt_674879/gjldrhd_674881/202610/t20261025_12046441.shtml",
            "source": "外交部",
            "date": "2026-10-25",
            "category": "元首动态",
            "priority_score": 100,
            "is_summit_level": True,
            "summary": "2026年10月25日，国家主席习近平同比利时国王菲利普互致贺信，庆祝两国建交55周年。习近平指出，建交55年来，中国和比利时坚持相互尊重、平等相待、互利共赢，两国关系平稳发展，双方各领域交流合作亮点纷呈、成果丰硕，两国人民交往日益密切。我高度重视中比关系发展，愿同菲利普国王一道努力，以两国建交55周年为契机，引领中比全方位友好合作伙伴关系不断迈上新台阶，为推动中欧关系健康稳定发展作出新贡献。菲利普表示，建交以来比中建立起广泛、多层次的合作关系，比方愿同中方深化各领域交往，共同推动两国关系取得更大发展。",
        },
        {
            "title": "国家能源局主要负责同志赴广东调研新型电网建设 强调抓好能源电力安全保供",
            "url": "https://www.nbd.com.cn/articles/2026-10-25/4616274.html",
            "source": "每日经济新闻",
            "date": "2026-10-24",
            "category": "部委动态",
            "priority_score": 85,
            "summary": "据国家能源局微信公众号10月25日消息，10月24日国家能源局党组书记、局长王宏志带队赴广东调研新型电网建设等工作。王宏志一行与广东省政府、南方电网等有关方面围绕新型电力系统建设情况交流，实地调研南方电网科技交流中心、国家新型储能创新中心、棠下电力运维中心，详细了解电力科技创新、储能产业发展、新型电网建设等情况。王宏志强调，要加快推进新型电网建设，推动主配微电网协同发展，持续扩大能源有效投资；持续抓好能源电力安全保供，发挥南方区域电力市场在保供应、促转型、优化资源配置等方面的作用；推动能源科技创新与产业创新深度融合，促进人工智能与能源双向赋能，拓展算电协同市场化应用；大力支持新型储能关键技术攻关，丰富多场景应用。同日，南方区域电力市场转入正式运行暨高质量发展推进会在广州召开。",
        },
        {
            "title": "湖南、云南省委主要负责同志职务调整 王志军、莫高义分别任省委书记",
            "url": "http://ipaper.ce.cn/pc/content/202610/25/content_340818.html",
            "source": "中国经济网",
            "date": "2026-10-25",
            "category": "人事任免",
            "priority_score": 86,
            "summary": "据新华社北京10月24日电，日前，中共中央决定：王志军同志任湖南省委委员、常委、书记，沈晓明同志不再担任湖南省委书记、常委、委员职务；莫高义同志任云南省委委员、常委、书记，王宁同志不再担任云南省委书记、常委、委员职务。王志军此前任北京市委常委、常务副市长，曾因长峰医院重大火灾事故被问责；莫高义此前任中央宣传部副部长、国务院新闻办公室主任，长期在宣传思想文化系统工作。此前，湖南、云南两省政府党组书记已分别由谢卫江、郭宁宁担任，本次省委书记调整后两省党政主要负责人同步完成更替。",
        },
        {
            "title": "陈文清主持召开专题会议 部署推进深化扫黑除恶专项斗争",
            "url": "https://www.gov.cn/yaowen/liebiao/202610/content_7084229.htm",
            "source": "中国政府网·要闻",
            "date": "2026-10-25",
            "category": "高层动态",
            "priority_score": 95,
            "summary": "中共中央政治局委员、中央政法委书记陈文清10月24日主持召开专题会议，强调要深入学习贯彻习近平总书记关于扫黑除恶斗争的重要指示精神，有序推进深化扫黑除恶专项斗争走深走实，用实实在在的成效回应人民群众期待。陈文清充分肯定专项斗争开展以来取得的阶段性成效，强调要牢牢把握扫黑除恶斗争的人民性、法治性和复杂性，把专项治理与系统治理、依法治理、综合治理、源头治理结合起来，始终保持高压态势。他要求深化线索摸排、强化侦查攻坚，把打击锋芒对准群众反映最强烈的黑恶势力犯罪，坚持集群打击、组织类案打击、推进大案攻坚；坚持依法办理，明晰新型黑恶犯罪认定标准，确保是黑恶一个不漏、不是黑恶一个不凑；坚持标本兼治，一体推进“打伞破网”“打财断血”和行业治理。王小洪出席会议并讲话，张军、应勇出席。",
        },
        {
            "title": "商务部就美发布新版对外投资限制拟议规则答记者问 坚决反对歧视性做法",
            "url": "https://www.mofcom.gov.cn/xwfb/xwfyrth/art/2026/art_d56e28ed788c4c8a887875dbfc287fe3.html",
            "source": "商务部",
            "date": "2026-10-25",
            "category": "部委动态",
            "priority_score": 88,
            "summary": "针对美东时间10月21日美国财政部发布新版对外投资限制拟议规则，商务部新闻发言人10月24日答记者问表示，中方注意到有关情况。该拟议规则歧视性扩大对华投资限制范围、加大限制力度，是典型的泛化国家安全做法，违背两国元首达成的重要共识，干扰中美两国企业正常经贸合作，破坏国际经贸秩序。中方对此表示严重关切、坚决反对，将密切关注事态后续发展，保留采取相应措施的权利。发言人强调，中国拥有超大规模市场，蕴含巨大消费和投资潜力，投资中国就是投资未来；美方限制对华投资既不利于中美经贸合作，也会损害美国企业自身利益。中方敦促美方尊重市场经济规律，停止泛化国家安全概念，停止将经贸问题政治化、武器化，为中美经贸合作创造良好环境。",
        },
        {
            "title": "二十届中央第八轮巡视对象公布 将对教育部及31所中管高校开展常规巡视",
            "url": "news.cctv.com/2026/10/24/ARTITKgkd1lym9l3rsSbOG9a261024.shtml",
            "source": "央视新闻",
            "date": "2026-10-24",
            "category": "部委动态",
            "priority_score": 88,
            "summary": "经党中央批准，二十届中央第八轮巡视对象10月24日公布，将对教育部、北京大学、清华大学、中国人民大学、北京师范大学、复旦大学、上海交通大学、西安交通大学、中国科学技术大学、中国农业大学、北京理工大学、北京航空航天大学、西北工业大学、哈尔滨工业大学、浙江大学、南京大学、四川大学、南开大学、天津大学、武汉大学、中山大学、西北农林科技大学、吉林大学、华中科技大学、山东大学、东南大学、厦门大学、同济大学、中南大学、大连理工大学、重庆大学、兰州大学等32家单位党组织开展常规巡视，即以教育部和中管高校为主的教育领域。此前，中共中央政治局常委、中央巡视工作领导小组组长李希出席二十届中央第八轮巡视工作动员部署会并讲话，会议传达学习习近平总书记听取中央第七轮巡视情况汇报时的重要讲话精神，强调要深入检查落实立德树人根本任务、一体推进教育科技人才发展情况和从严管党治校情况。",
        },
        {
            "title": "全国民航10月25日起执行冬春航季航班计划 每周安排11.6万班",
            "url": "http://www.caacnews.com.cn/tt/202610/t20261024_1397985.html",
            "source": "中国民航网",
            "date": "2026-10-24",
            "category": "部委动态",
            "priority_score": 85,
            "summary": "据中国民航局消息，自2026年10月25日起至2027年3月27日，全国民航正式执行2026/2027年冬春航季航班计划，216家国内外航空公司计划每周安排客货运航班11.6万班。国内方面，61家航空公司计划每周安排国内航班9.4万班（客运91454班、货运2812班）；34家航空公司计划新开288条国内航线，多集中在西北、东北、西南与华东、中南地区之间的干支衔接航线上。国际方面，191家航空公司计划通航85个国家，每周安排国际航班21812班；至中亚、南亚、北美、欧洲、东南亚、拉美客运航班同比增长，与哈萨克斯坦、印度、加拿大、比利时等17个国家间航班量增幅超40%，并将新开至冰岛、马达加斯加、约旦定期客运航线。民航局印发的《国内航线航班评审优化措施》自本次换季起实施，从增加总量供给转向精准调控。",
        },
        {
            "title": "2027年度中央机关公开遴选和公开选调公务员报名10月28日启动",
            "url": "https://m.gmw.cn/2026-10/25/content_1304578953.htm",
            "source": "光明网",
            "date": "2026-10-24",
            "category": "政策发布",
            "priority_score": 80,
            "summary": "据新华社消息，2027年度中央机关公开遴选和公开选调公务员报名即将开始，考生可于2026年10月28日8:00至11月6日18:00期间登录专题网站（http://subb.scs.gov.cn/lx2027）进行网上报名，笔试将于11月28日在全国各直辖市、省会城市和自治区首府同时举行。本次共有42个中央机关部门参加，计划选拔213人，其中公开遴选职位包括副处长职务和一级调研员及以下职级，计划选拔197人；公开选调职位为一级至四级调研员职级，计划选拔16人。本次工作坚持新时代好干部标准，突出政治标准，坚持基层导向和队伍稳定相统一、组织推荐和竞争择优相结合，兼顾优化上级机关队伍结构与稳定基层队伍。",
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

    # ---- 6. 清洗 + 断言 ----
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
