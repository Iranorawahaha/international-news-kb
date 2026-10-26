#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内新闻 LLM 质量后处理 - 2026-10-26（周一）

初抓 21 条 → 目标 ~19 条

删除：
  1. 元首宣传产品（"一见·总书记这样数说长征"）
  2. 反响稿（重要讲话引发热烈反响）
  3. 同事件多稿：比利时贺信（cctv 2 稿 + gov.cn 1 稿 → 保留 gov.cn 要闻版）
  4. 同事件多稿：巴青地震救灾 3 稿 → 合并 1 条
  5. 栏目体 / 蹲点故事（纱线千亿集群、图木舒克产业富民、集成式出海 2 稿、低空经济）
  6. 评论体（中国经济面面观·出口首破8万亿）
  7. 栏目体（新央企如何释放数据要素价值·经济新方位）
  8. 部委级以下例行（翟隽会见沙特外交部顾问哈立德亲王）
  9. 地方响应（福建终止防台风应急响应）
补录（curl 全 200）：
  - 央行 10-26 开展 7000 亿元 MLF 操作 部委85（当日新发）
⚠️ 所有 URL 已 curl 核对（title 与条目一致）；gov.cn 首页正则取链，禁猜 ID。
⚠️ 10-26 五中全会开幕无官方通稿（会期 26-29 日，通稿一般会后发），本条按联合早报口径收 1 条，
   分类 重要会议 88；窗口内无元首级活动属客观正常。
"""
import json
import re

DATA = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json"
TODAY = "2026-10-26"
YESTERDAY = "2026-10-25"
ALLOWED_DATES = {TODAY, YESTERDAY}
COLLECT = "2026-10-26T10:05:00"

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
    # 1. 元首宣传产品 / 反响稿
    "一见·总书记这样“数”说长征",
    "以青春之志 在新长征路上续写奋斗篇章",
    # 2. 比利时贺信：保留 gov.cn 要闻版（content_7084243），删两条 cctv 版
    "news.cctv.com/2026/10/25/ARTITF76RZgwurzPRQeZ9Jb1261025.shtml",
    # 3. 巴青地震：保留"西藏那曲市巴青县7.0级地震抢险救援有序进行"
    "西藏巴青地震救灾物资陆续集结 伤员得到有序救治",
    # 4. 栏目体 / 蹲点故事 / 评论
    "一根纱线“缝”出千亿级产业集群",
    "新疆图木舒克：产业富民“润”戈壁",
    "期待值拉满！从卖零件到卖整房",
    "解锁长空之上的“生命密钥”",
    "中国经济面面观丨出口首破8万亿",
    "新央企如何加快释放数据要素价值",
    "为加强全球经济金融治理贡献智慧",
    "从“卖出去”到“扎下去” 贸投融合助推中企产业出海",
    # 5. 部委级以下例行 / 地方响应
    "中国政府中东问题特使翟隽会见沙特外交部顾问哈立德亲王",
    "福建省终止防台风应急响应",
    # 6. 跨版面重复：昨日版面已收 mofcom 原件（88），本条央视版删除
    "商务部：美歧视性扩大对华投资限制范围",
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

    # ---- 1. 比利时贺信：gov.cn 要闻版（元首100，已符合 boost） ----
    bl = get("习近平同比利时国王菲利普就中比建交55周年互致贺信")
    bl.update({
        "url": "https://www.gov.cn/yaowen/liebiao/202610/content_7084243.htm",
        "source": "中国政府网·要闻",
        "date": "2026-10-25",
        "category": "元首动态",
        "priority_score": 100,
        "is_summit_level": True,
        "summary": "2026年10月25日，国家主席习近平同比利时国王菲利普互致贺信，庆祝两国建交55周年。习近平指出，建交55年来，中国和比利时坚持相互尊重、平等相待、互利共赢，两国关系平稳发展，双方各领域交流合作亮点纷呈、成果丰硕，两国人民交往日益密切。我高度重视中比关系发展，愿同菲利普国王一道努力，以两国建交55周年为契机，引领中比全方位友好合作伙伴关系不断迈上新台阶，为推动中欧关系健康稳定发展作出新贡献。菲利普表示，建交以来比中建立起广泛、多元的合作关系，习近平主席2014年对Belgium的国事访问给他留下美好回忆；坚信双方将在过去55年基础上继续推进开放对话、拓展务实合作、增进相互理解，比方愿同中方发展均衡互利关系，应对全球共同挑战。",
    })
    # 修正国名用词（避免中英混排）
    bl["summary"] = bl["summary"].replace("对Belgium的国事访问", "对比利时的国事访问")

    # ---- 2. 五中全会开幕：补真实摘要（联合早报据央视报道口径） ----
    wzh = get("中共五中全会今起在北京召开")
    wzh.update({
        "source": "联合早报",
        "date": "2026-10-26",
        "category": "重要会议",
        "priority_score": 88,
        "summary": "中国共产党第二十届中央委员会第五次全体会议10月26日在北京召开，会期四天至10月29日结束。据央视新闻报道，全会主要议程是中共中央政治局向中央委员会报告工作，研究持之以恒推进全面从严治党若干重大问题。这是党的二十大以来首次由中央全会专门研究全面从严治党，将围绕健全全面从严治党体系作出部署。由于去年10月召开的四中全会已审议通过“十五五”规划建议，本次全会承接过去较常在六中全会讨论的党建议题。全会开幕当天，人民日报刊发任仲平文章《在新征程上持之以恒推进全面从严治党》。",
    })

    # ---- 3. 巴青地震救援：合并版摘要 ----
    dz = get("西藏那曲市巴青县7.0级地震抢险救援有序进行")
    dz.update({
        "source": "央视新闻",
        "date": "2026-10-25",
        "category": "部委动态",
        "priority_score": 88,
        "summary": "西藏那曲市巴青县7.0级地震抢险救援各项工作有序推进。10月24日20时30分左右，震区电力供应已全面恢复。截至10月25日15时，西藏军区官兵在玛如乡片区累计完成7个村共计475户搜救排查，并同步开展医疗救助。玛如乡2村受灾严重，当地首批60套安置板房已搭建完成，群众陆续从帐篷搬入，剩余180套板房于10月26日上午全部完成。救援人员持续为受灾群众提供常态化热食、热水供应。本次地震已造成16人遇难、76人受伤，中央组织部从代中央管理党费中划拨2500万元，财政部、应急管理部拨付5000万元中央自然灾害救灾资金，国家发展改革委安排3000万元中央预算内投资支持灾后应急恢复。",
    })

    # ---- 4. 庄兆林履新：补真实摘要（组织部部长级人事，属可收层级） ----
    zzl = get("庄兆林履新江西省委三把手")
    zzl.update({
        "source": "联合早报",
        "date": "2026-10-25",
        "category": "人事任免",
        "priority_score": 86,
        "summary": "据联合早报报道，江西省日前完成省委领导班子调整：庄兆林出任江西省委副书记，成为省委“三把手”；刘金波任江西省委常委、组织部部长，填补该省组织部长空缺。庄兆林此前长期在江苏工作，曾任徐州市委书记、江苏省委常委、省委秘书长等职，2024年调任江西省委常委、常务副省长。刘金波此前在中央组织部任职。此次调整是近期省级党委领导班子集中调整的组成部分，同期湖南、云南、山西、新疆、河南、安徽等省区党委书记已完成更替。",
    })

    # ---- 5. 赵辰昕任河北省代省长：官方口径摘要 ----
    zcx = get("赵辰昕任河北省代省长")
    zcx.update({
        "source": "光明网",
        "date": "2026-10-25",
        "category": "人事任免",
        "priority_score": 86,
        "summary": "据新华社石家庄10月25日电，河北省第十四届人民代表大会常务委员会第二十四次会议10月25日决定：接受王正谱辞去河北省人民政府省长职务的请求，赵辰昕代理河北省人民政府省长。同日，河北省人大常委会决定任命陈少波为河北省人民政府副省长。此前10月24日消息，中共中央批准赵辰昕同志任河北省委副书记，河北省委决定其任省政府党组书记。赵辰昕生于1969年9月，曾任国家发展改革委副秘书长、秘书长，2022年5月任国家发展改革委副主任，2025年5月任河北省委常委、常务副省长。",
        "url": "https://news.gmw.cn/2026-10/26/content_39064602.htm",
    })

    # ---- 6. 商务部美投资限制答问：昨日版面已收 mofcom 原件，本条为央视版 → 删除（不再 FIX） ----
    #   已加入 DELETE_SUBSTR（"商务部：美歧视性扩大对华投资限制范围"），此处无操作

    # ---- 7. 广交会集成式出海：栏目体 → 删除（已在 DELETE 中）；此处无操作 ----

    # ---- 8. 补录 ----
    add = [
        {
            "title": "央行10月26日开展7000亿元中期借贷便利操作 期限1年",
            "url": "http://bgimg.ce.cn/xwzx/gnsz/gdxw/202610/t20261026_3271043.shtml",
            "source": "中国经济网",
            "date": "2026-10-26",
            "category": "部委动态",
            "priority_score": 85,
            "summary": "中国人民银行10月26日以固定数量、利率招标、多重价位中标方式开展7000亿元中期借贷便利（MLF）操作，期限为1年期，旨在保持银行体系流动性充裕。中期借贷便利是中央银行提供中期基础货币的货币政策工具，可通过招标方式开展，利率发挥中期政策利率作用，引导金融机构向符合国家政策导向的实体经济部门提供低成本资金。本月MLF为缩量续作，与到期量相比净回笼2000亿元，为连续第二个月净回笼，市场人士认为这体现货币政策继续坚持支持性立场的同时，更注重存量结构优化与精准滴灌。",
        },
        {
            "title": "国家发展改革委、自然资源部发布《中国海洋经济发展报告2026》",
            "url": "https://www.gov.cn/lianbo/202610/content_7084222.htm",
            "source": "中国政府网·政务联播",
            "date": "2026-10-25",
            "category": "部委动态",
            "priority_score": 85,
            "summary": "国家发展改革委、自然资源部近日发布《中国海洋经济发展报告2026》，系统总结我国“十四五”时期海洋经济发展成效。报告显示，2025年我国海洋生产总值突破11万亿元，占国内生产总值比重为7.9%，海洋经济已成为国民经济重要增长极。船舶与海洋工程装备、海洋交通运输、海洋渔业等产业国际竞争力不断增强，海上风电并网装机规模、新增装机规模保持世界首位，海水淡化工程日产规模突破300万吨，自主研发海洋药物品类占全球28%。“蛟龙”号、“奋斗者”号载人潜水器协同完成我国首次北极冰区载人深潜。全国大陆自然岸线保有率稳定在35%以上，划定海洋生态保护红线15.1万平方千米，建立涉海自然保护地352个，新建黄岩岛国家级自然保护区。我国已与50多个国家和国际组织签署海洋领域合作协议。",
        },
        {
            "title": "中欧班列“东通道”年内通行量突破6000列 创历史同期新高",
            "url": "https://www.jingjiribao.cn/static/detail.jsp?id=692314",
            "source": "经济日报",
            "date": "2026-10-25",
            "category": "经贸动向",
            "priority_score": 85,
            "summary": "中国铁路哈尔滨局集团有限公司10月24日发布消息，截至10月23日，今年以来中欧班列“东通道”通行班列达6024列，同比增长40.3%，年内通行量首次突破6000列。今年2月、4月、9月，单月增幅分别达53.3%、55.3%、57.2%，多个月份保持五成以上高位增长。出口货物由日用百货、轻工纺织、五金工具等初加工产品，拓展至家电、商品汽车、汽车零部件等高附加值产品，进口货物由初期板材拓展至化肥、大豆等品类。作为中国规模最大的中欧班列口岸集群，“东通道”三大口岸持续升级通关能力：满洲里站落实“铁路快通”模式、实行7×24小时预约通关；绥芬河站今年前9个月开行班列714列、同比增长82%；同江北站实现“快装快卸、快进快出”。目前通行线路达27条，覆盖波兰、德国、荷兰等14个国家，联通国内长沙、郑州、成都等60余个城市。",
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

    # ---- 9. 清洗 + 断言 ----
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
