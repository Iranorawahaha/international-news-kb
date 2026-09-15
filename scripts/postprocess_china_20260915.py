#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
postprocess_china_20260915.py — 国内看板 2026-09-15 LLM 质量后处理

背景：refresh_china_news.sh（v5）初抓 38 条（collectedAt=2026-09-15 09:21，date∈{09-14,09-15}）。
窗口 = 2026-09-14 11:08 ~ 2026-09-15 09:31（上次 cn 执行 9-14 11:08）。

核心问题：
  1. 元首动态 9 条全部是 9-14《新闻联播》对 9-12~9-13 金砖峰会/回京的**复述与视觉产品**
     （联播重播、纪实、述评、金句海报、金色相框、视频画报），9-14 版面已完整覆盖该出访
     → 跨版面重复 + 栏目体/视觉产品，全数剔除；今日窗口无新元首事件，元首动态 0 条属客观正常。
  2. 服贸会闭幕、供应链发展报告 = 9-14 版面已收同事件（跨版面重复）。
  3. 智能家居方案 3 稿（通知/解读/焕新潮）、电子信息规划 2 稿、央行金融数据 2 稿 → 各留 1。
  4. 外交部记者会 URL 死链（wjdt_674879 路径）+ 标题残留 + 摘要为空；王毅两通电话用人民日报转载
     → 统一升级为外交部官网原文 URL（curl 全 200）。
  5. 《新闻联播》9-14"联播快讯"档系统性漏采 → 补录 3 条（提级调查/网安周开幕式/回款难吹风会）。

目标：剔除低质/重复/栏目体，修正错误分类与 URL，补录官方漏采条目
"""
import json
import os
from collections import Counter
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "china-news.json")
TODAY = "2026-09-15"
PREV = "2026-09-14"

CAT_ORDER = ["元首动态", "高层动态", "重要会议", "人事任免", "部委动态", "政策发布", "经贸动向"]

# ---------- 删除清单（URL 精确匹配）----------
DELETE_URLS = {
    # ① 元首动态：9-14《新闻联播》对 9-12~9-13 金砖出访的复述（9-14 版面已收同事件）
    "https://tv.cctv.com/2026/09/14/VIDEmp3yikvTOeendyE2ZffO260914.shtml",   # 为全球南方聚力（联播版，9-14版面[00]同事件）
    "https://tv.cctv.com/2026/09/14/VIDEBC88hUqmZQVjuzJkY0OO260914.shtml",   # 回到北京（联播版，9-14版面[07]同事件）
    "https://news.cctv.com/2026/09/14/ARTIaX8D5pVnKTnIS6SAADoY260914.shtml",  # 开启第三个"金色十年"（摘要仅26字+跨版面重复）
    # ② 元首动态：新华社述评/纪实（非事件性新闻）
    "https://www.gov.cn/yaowen/liebiao/202609/content_7080986.htm",          # 习近平主席指引"大金砖"筑牢务实合作根基（述评）
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081079.htm",          # 勇做时代先锋…出访纪实（纪实栏目体）
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081005.htm",          # 防汛抗洪救灾纪实（综述/纪实）
    # ③ 元首动态：央视视觉产品（视频画报/金句海报/金色相框）
    "https://news.cctv.com/2026/09/15/ARTIiKbM2iVVrcLvWirTPaZS260915.shtml",  # 视频画报
    "https://news.cctv.com/2026/09/14/ARTIfksqQVhqH9bj4jXynYXV260914.shtml",  # 金句海报
    "https://news.cctv.com/2026/09/14/ARTIVYCnUcq5tPiKMFeAg8lG260914.shtml",  # 金色相框
    # ④ 栏目体/观察体
    "https://news.cctv.com/2026/09/14/ARTIIqA45mJrsghHYSRaSGU9260914.shtml",  # "十五五"开局之年5G工厂发展观察
    "https://news.cctv.com/2026/09/14/ARTIeZCU46N2g3jOWFPycgTw260914.shtml",  # 关键词解锁服贸会上的经济新机遇（栏目体）
    "https://news.cctv.com/2026/09/14/ARTISzYaP4O7ui794jUw7pt5260914.shtml",  # 小肉鸭"孵"出富民大产业（蹲点故事化）
    # ⑤ 跨版面重复（9-14 版面已收同事件）
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081001.htm",           # 中国供应链发展报告（9-14版面[30]已收）
    "https://photo.cctv.com/2026/09/14/PHOA4p0dkAUfJK8Ow1uKKFLu260914.shtml",  # 服贸会闭幕（图片页，9-14版面[19]已收）
    # ⑥ 同政策/同数据多稿（留主稿）
    "https://www.mofcom.gov.cn/xwfb/sjfzrfb/art/2026/art_73bcf2958e424c238054ddec9edccab8.html",  # 智能家居解读稿（留通知本体）
    "https://news.cctv.com/2026/09/14/ARTIquyRcMYlXrECLpGExhWi260914.shtml",  # 智能家居"焕新潮"（与通知本体重复）
    "https://news.cctv.com/2026/09/15/ARTI9fXzz7VwAyAkUJbFy8d8260915.shtml",  # 电子信息规划（与两部门印发稿重复）
    "https://jingji.cctv.com/2026/09/14/ARTIUCO53Cstt3KvCnNMbtbo260914.shtml",  # 前8个月贷款10.44万亿（与央行金融总量稿重复）
    # ⑦ 程序性/技术性公告与低价值服务信息
    "https://www.ndrc.gov.cn/xwdt/tzgg/202609/t20260914_1407622.html",        # 发改委研究课题入选公告
    "https://news.cctv.com/2026/09/14/ARTIDYbuLY40Csg3OTZp7xAG260914.shtml",  # 婴幼儿配方乳粉核查要点征求意见
    "https://news.cctv.com/2026/09/14/ARTIjZhL33lk5LeYHVcx16Ot260914.shtml",  # 认证信息报送和证书查询管理改革
    "https://news.cctv.com/2026/09/14/ARTIdgdqmuYBEuf63vYsPPqS260914.shtml",  # 民政部辟谣风险提示
    "https://news.cctv.com/2026/09/14/ARTIa8cJEuyQiNDnOzyLs9QQ260914.shtml",  # 领事提醒（塔阿边境）
    # ⑧ 记者会子稿（要点并入记者会本体）
    "https://news.cctv.com/2026/09/14/ARTIUvB6RG7ZBPEWa30T03Va260914.shtml",  # 在台湾问题上踩线越界必将承担严重后果
    # ⑨ 学习类读物
    "http://paper.people.com.cn/rmrb/pc/content/202609/15/content_30181089.html",  # 《军营理论热点怎么看·2026》印发全军
    # ⑩ 地方政策（非中央层面）
    "https://jingji.cctv.com/2026/09/14/ARTIXqteHkNecQlyUOV6UKLM260914.shtml",  # 上海17项举措推进科技金融
}

# ---------- 修正清单（URL 精确匹配）----------
FIXES = {
    # 商务部副部长会见美国企业董事长：95 高层动态 → 85 部委动态（副部长级），补真实摘要（WebFetch 官网）
    "https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_3e6dedeecd6d47a6acec78184a2f3123.html": {
        "category": "部委动态",
        "priority_score": 85,
        "summary": "9月14日，商务部副部长兼国际贸易谈判副代表凌激会见美国艺康集团董事长、总裁兼首席执行官柯思博，双方就艺康扩大在华业务、清洁环保合作及中美经贸关系等议题进行了交流。",
    },
    # 王毅同拉脱维亚外长通电话：人民日报转载 → 外交部官网原文 + 真实摘要
    "http://paper.people.com.cn/rmrb/pc/content/202609/15/content_30181077.html": {
        "url": "https://www.mfa.gov.cn/web/wjdt_674879/gjldrhd_674881/202609/t20260914_12022157.shtml",
        "source": "外交部",
        "summary": "2026年9月14日，中共中央政治局委员、外交部长王毅应约同拉脱维亚外长布拉泽通电话。布拉泽感谢中方就尼泊尔和中国西藏泥石流灾害所作通报和搜救工作，称33名拉脱维亚公民在灾害中失联。王毅表示，中方对中外人员一视同仁、全力以赴开展救助，将尽最大努力继续搜救外方失联人员并妥善做好后续处置；中方愿同拉方以建交35周年为契机，为中拉关系注入新的时代内涵。",
    },
    # 王毅同法国外长巴罗通电话：人民日报转载 → 外交部官网原文 + 真实摘要
    "http://paper.people.com.cn/rmrb/pc/content/202609/15/content_30181076.html": {
        "url": "https://www.mfa.gov.cn/web/wjdt_674879/gjldrhd_674881/202609/t20260914_12022150.shtml",
        "source": "外交部",
        "summary": "2026年9月14日，中共中央政治局委员、外交部长王毅应约同法国外长巴罗通电话。王毅指出，一个中国原则是中法全面战略伙伴关系的政治基础，希望法方以实际行动恪守一个中国原则，不同台湾进行任何形式的官方往来，不向“台独”势力发出错误信号；中欧应坚持伙伴定位、坚持互利共赢，以建设性对话妥善解决当前经贸摩擦，避免升级对抗。巴罗表示法方坚定奉行一个中国政策。",
    },
    # 外交部例行记者会：死链路径 → fyrbt_673021 正确栏目 + 标题去导航残留 + 实录要点摘要
    "https://www.mfa.gov.cn/web/wjdt_674879/202609/t20260914_12021744.shtml": {
        "url": "https://www.mfa.gov.cn/web/fyrbt_673021/jzhsl_673025/202609/t20260914_12021744.shtml",
        "title": "2026年9月14日外交部发言人郭嘉昆主持例行记者会",
        "summary": "9月14日外交部发言人郭嘉昆主持例行记者会。郭嘉昆表示，习近平主席同莫迪总理已连续三年成功会晤，新德里会晤是对中印关系发展的“再确认”，达成的最重要共识是中印要做伙伴；就巴拿马部分议员成立所谓“巴台跨党派交流小组”表示，在台湾问题上踩线越界必将承担严重后果；并就也门局势、人工智能治理、吉隆泥石流失联外籍人员搜救等答问。",
    },
    # 智能家居消费行动方案：85 部委动态 → 80 政策发布
    "https://news.cctv.com/2026/09/14/ARTIMZcEGPl7rI5sIdaaxYSw260914.shtml": {
        "category": "政策发布",
        "priority_score": 80,
    },
    # 电子信息制造业"十五五"规划：补真实摘要（官网/新华社口径）
    "https://news.cctv.com/2026/09/15/ARTIIgrBdubyxh1i38MFa8vI260915.shtml": {
        "title": "两部门印发《电子信息制造业发展“十五五”规划》",
        "summary": "工业和信息化部、国家发展改革委联合印发《电子信息制造业发展“十五五”规划》，按照“筑基、提质、育新、治理”思路部署17项任务、9个专栏。到2030年，规模以上企业营业收入突破30万亿元，产业研发投入强度达到3.5%，在集成电路、先进计算、消费电子、基础电子、能源电子等领域涌现一批长板技术和产品。",
    },
    # 健康中国国新办发布会：80 政策发布 → 88 重要会议
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081066.htm": {
        "category": "重要会议",
        "priority_score": 88,
    },
    # 数字经济人才培养：72 经贸动向 → 80 政策发布
    "https://news.cctv.com/2026/09/14/ARTIlCTGzXXosGmX5spKpxkn260914.shtml": {
        "category": "政策发布",
        "priority_score": 80,
    },
    # AI+脑机接口标准：72 经贸动向 → 85 部委动态，标题去"！"
    "https://news.cctv.com/2026/09/15/ARTIa6Ihq1oolMHJJadIUxcM260914.shtml": {
        "category": "部委动态",
        "priority_score": 85,
        "title": "全球首个“人工智能+脑机接口”医疗器械标准由中国首发",
    },
}

# ---------- 补录清单（《新闻联播》9-14 漏采 + 国新办吹风会）----------
ADD = [
    {
        "title": "国务院对中国船舶集团青岛北海造船有限公司“9·10”重大火灾事故提级调查",
        "url": "https://www.gov.cn/yaowen/liebiao/202609/content_7081052.htm",
        "date": "2026-09-14",
        "source": "中国政府网·要闻",
        "category": "部委动态",
        "priority_score": 88,
        "is_summit_level": False,
        "summary": "9月10日11时15分许，中国船舶集团青岛北海造船有限公司一艘外籍货轮靠港维修期间发生火灾，造成25人死亡、5人受伤。为贯彻落实习近平总书记重要指示精神，按照李强总理等中央领导同志批示要求，国务院成立事故调查组，由应急管理部牵头，外交部、工业和信息化部、公安部、交通运输部、国务院国资委、全国总工会、国家消防救援局和山东省人民政府等参加，对该起事故提级调查。9月14日下午，调查组召开第一次全体会议。",
        "collectedAt": "2026-09-15 10:05:00",
    },
    {
        "title": "2026年国家网络安全宣传周开幕式在山东济南举行",
        "url": "https://www.gov.cn/lianbo/202609/content_7081054.htm",
        "date": "2026-09-14",
        "source": "中国政府网",
        "category": "部委动态",
        "priority_score": 85,
        "is_summit_level": False,
        "summary": "以“网络安全为人民，网络安全靠人民——智能时代 网安护航”为主题的2026年国家网络安全宣传周开幕式14日在山东济南举行。开幕式上集中发布《人工智能安全治理框架3.0》《2026年人工智能技术赋能网络安全应用测试结果》和消费类网联摄像头网络安全标识备案产品等成果。宣传周由中央宣传部、中央网信办等十部门联合举办，9月14日至20日在全国范围内统一开展。",
        "collectedAt": "2026-09-15 10:05:00",
    },
    {
        "title": "国新办举行政策例行吹风会 多部门合力治理中小企业回款难",
        "url": "https://news.cctv.com/2026/09/14/ARTI7IWogZPkRS2MpnOxqvwv260914.shtml",
        "date": "2026-09-14",
        "source": "央视新闻",
        "category": "重要会议",
        "priority_score": 88,
        "is_summit_level": False,
        "summary": "国务院新闻办公室9月14日举行国务院政策例行吹风会，工业和信息化部、中国人民银行、国务院国资委、市场监管总局、中国证监会介绍加强中小企业回款难问题治理有关工作情况。今后将健全行业账款支付规则、分行业明确合理账期，引导龙头企业率先发布并践行对中小企业“60日付现承诺”，加强大型企业支付行为监管，对故意拉长账期的大型企业开展联合约谈整治，并将应收账款电子凭证最长付款期限压减至6个月。",
        "collectedAt": "2026-09-15 10:05:00",
    },
]


def main():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    arts = data["archive"][TODAY]
    print(f"初抓：{len(arts)} 条")

    kept, deleted, fixed = [], [], []
    for a in arts:
        u = (a.get("url") or "").strip().rstrip("/")
        if u in {x.rstrip("/") for x in DELETE_URLS}:
            deleted.append(a.get("title", ""))
            continue
        if u in FIXES:
            a.update(FIXES[u])
            fixed.append(a.get("title", ""))
        kept.append(a)

    existing = {(x.get("title", "") or "")[:30] for x in kept}
    existing_urls = {(x.get("url") or "").strip().rstrip("/").lower() for x in kept}
    added = []
    for item in ADD:
        u = item["url"].strip().rstrip("/").lower()
        if item["title"][:30] in existing or u in existing_urls:
            continue
        kept.append(dict(item))
        added.append(item["title"])
        existing.add(item["title"][:30])
        existing_urls.add(u)

    kept.sort(key=lambda x: (CAT_ORDER.index(x["category"]) if x.get("category") in CAT_ORDER else 99,
                             -int(x.get("priority_score") or 0)))

    data["archive"][TODAY] = kept
    data["todayCount"] = len(kept)
    data["lastUpdated"] = datetime.now(TZ).strftime("%Y-%m-%d %H:%M")
    st = data.setdefault("stats", {})
    st["totalArticles"] = sum(len(v) for v in data["archive"].values())
    st["dateCount"] = len([d for d, v in data["archive"].items() if v])
    st["latestDate"] = max(data["archive"].keys())
    st["summitCount"] = sum(1 for v in data["archive"].values()
                            for x in v if x.get("is_summit_level"))

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n删除 {len(deleted)} 条：")
    for t in deleted:
        print("  -", t[:66])
    print(f"\n修正 {len(fixed)} 条：")
    for t in fixed:
        print("  *", t[:66])
    print(f"\n补录 {len(added)} 条：")
    for t in added:
        print("  +", t[:66])

    print(f"\n最终今日 {len(kept)} 条")
    print("分类：", dict(Counter(x["category"] for x in kept)))
    print("分数≥85：", sum(1 for x in kept if (x.get("priority_score") or 0) >= 85), "/", len(kept))
    print("无摘要：", sum(1 for x in kept if not (x.get("summary") or "").strip()))
    print("摘要>170字：", [x["title"][:24] for x in kept if len(x.get("summary") or "") > 170])
    print("collectedAt≠今日：", sum(1 for x in kept if not str(x.get("collectedAt", "")).startswith(TODAY)))
    print("date<昨日：", sum(1 for x in kept if x.get("date", "") < PREV))
    print("元首动态：", sum(1 for x in kept if x["category"] == "元首动态"))
    print("URL 重复：", len(kept) - len({(x.get("url") or "").rstrip("/").lower() for x in kept}))


if __name__ == "__main__":
    main()
