#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内看板 2026-10-12 LLM 后处理：删除低质/重复/跨版面 + 修正 + 补录"""
import json, html, shutil, os, re, sys

BASE = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50"
JSON = os.path.join(BASE, "data/china-news.json")
BAK = os.path.join(BASE, "data/china-news.json.bak-20261012")

TODAY = "2026-10-12"
YESTERDAY = "2026-10-11"

if not os.path.exists(BAK):
    shutil.copy(JSON, BAK)
    print("备份已创建:", BAK)

d = json.load(open(JSON, encoding="utf-8"))
today = d["archive"][TODAY]
print("处理前今日版面:", len(today), "条")

# 历史版面全部 URL（防跨日重复）
hist_urls = set()
for day, arts in d["archive"].items():
    if day == TODAY:
        continue
    for a in arts:
        hist_urls.add(a["url"])
print("历史版面 URL 数:", len(hist_urls))

def norm(u):
    return u.rstrip('/')

# ============ 1. 删除清单（按标题关键词精确匹配） ============
DELETE_TITLES = [
    # 元首宣传产品/述评稿（非事实性元首动态）
    "坚持人民至上、生命至上——习近平总书记引领健康中国建设",
    "大道致远，笃行不怠——记中国元首外交金秋繁忙季",
    # 假日/经济数据栏目体与综述
    "“扩张”“上涨”“上行”……从一系列经济数据透视中国经济发展活力",
    "先行指标看经济 | 各项稳投资政策打出“组合拳” 经济内生增长动能不断积蓄",
    "向新、向优、韧性强！透过数据看我国经济回升向好态势持续巩固",
    # 蹲点/地方叙事/海洋经济观察
    "产业“加速跑”人才供给如何跟上？校企协同缩短“课本到大海”的距离",
    "做活“农头工尾”“粮头食尾”大文章 全产业链提升粮食价值助农增收",
    "昔日偏僻边境乡，如今产业兴旺，看雪域边疆幸福变迁",
    "高新产业接续落地 续写西藏高质量发展新篇章",
    # 栏目体/方法论
    "把握规律，因地制宜发展新质生产力",
    "越来越多村民足不出村、快捷收件（经济新方位）",
    "明德战略对话：中国经济韧性与活力给世界带来新机遇",
    # 跨版面 AI 线
    "消息：蚂蚁AI开启小范围内测 对标Meta智能体Muse",
]
# 经贸动向同数据多稿：中国物流业景气指数、水网投资已由 gov.cn 版覆盖
DELETE_TITLES += [
    "“十五五”时期 国家水网建设投资需求将突破6万亿元",
    "我国氢能产业进入发展快车道",
]

deleted = []
kept = []
for a in today:
    if a["title"] in DELETE_TITLES:
        deleted.append(a["title"])
        continue
    kept.append(a)
print("\n删除", len(deleted), "条")
for t in deleted:
    print("  ✗", t[:70])

# ============ 2. 修正（URL/分类/摘要/标题） ============
FIX = {
    # 王沪宁会见越南国会主席 —— 人民日报版保留，URL 规范 + 摘要清理
    "王沪宁会见越南国会主席陈青敏": {
        "url": "https://www.mfa.gov.cn/wjdt_674879/gjldrhd_674881/202610/t20261011_12038253.shtml",
        "source": "外交部·领导人活动",
        "category": "高层动态",
        "priority_score": 95,
        "summary": "全国政协主席王沪宁10月11日在京会见越南国会主席陈青敏。王沪宁表示，近年来习近平总书记、国家主席同苏林总书记、国家主席保持密切战略沟通，引领中越关系在世界百年变局中破浪前行；中方愿同越方遵循两党两国最高领导人战略共识，赓续传统友谊，深化各领域务实合作，加强立法机构交流，推动具有战略意义的中越命运共同体建设走深走实。陈青敏表示，越方高度重视对华关系，愿同中方加强立法机构交往，为越中关系发展作出积极贡献。",
    },
    # 哈药股份总裁芦传有被留置 —— 联合早报 → 中国网官方通报（原 zaobao 无摘要）
    "中国大型药企哈药股份总裁芦传有被留置": {
        "title": "哈药股份董事、总裁芦传有被立案并实施留置",
        "url": "https://news.china.com.cn/2026-10/12/content_118729597.shtml",
        "source": "中国网",
        "category": "人事任免",
        "priority_score": 86,
        "summary": "10月11日，哈药集团股份有限公司（600664）发布公告称，公司于近日收到相关监察委员会关于公司董事、总裁芦传有的《立案通知书》和《留置通知书》。芦传有1962年生，2023年12月起任总裁，2025年税前薪酬296.68万元，任期原至2026年12月。公司表示已对相关工作妥善安排，董事长及其他高管正常履职，董事会运作正常，生产经营情况正常，该事项不会对公司生产经营管理产生重大影响。",
    },
    # 食品安全法修订草案征求意见 —— 补真实摘要
    "食品安全法修订草案公开征求意见 回应了这些民生关切": {
        "category": "政策发布",
        "priority_score": 80,
        "summary": "市场监管总局10月10日就《中华人民共和国食品安全法（修订草案征求意见稿）》向社会公开征求意见。此次征求意见稿涉及人工智能监管、网络食品经营等多个方面，重点回应校园餐如何管得更严、直播间销售食品安全责任归属等民生关切，拟进一步压实平台与经营者责任、完善新业态食品安全监管规则。",
    },
}
for a in kept:
    f = FIX.get(a["title"]) or FIX.get(a.get("_orig_title", ""))
    if f:
        for k, v in f.items():
            if k == "title":
                a["_orig_title"] = a["title"]
            a[k] = v

# ============ 3. 补录（curl 全 200 验证） ============
ADD = [
    # 高层动态
    # ⚠️ 中法战略对话（10-10 举行）= 10-10 版面漏采，date<昨日 → 按 V2.11 硬规则不入今日版面，不伪造日期
    {
        "title": "应习近平邀请 博茨瓦纳总统博科10月12日起对中国进行国事访问",
        "title_en": "Botswana's President Boko Begins State Visit to China",
        "url": "https://world.people.com.cn/n1/2026/1012/c1002-40812442.html",
        "source": "人民日报",
        "date": "2026-10-12",
        "category": "元首动态",
        "priority_score": 100,
        "summary": "应国家主席习近平邀请，博茨瓦纳共和国总统杜马·希代翁·博科于10月12日至17日对中国进行国事访问，这是博科总统就任以来首次访华。杜马·希代翁·博科，男，57岁，法学硕士，2024年11月起担任博茨瓦纳共和国总统。访问期间，习近平主席将为博科总统举行欢迎仪式和欢迎宴会，两国元首将举行会谈；李强总理、赵乐际委员长将分别会见博科总统，博科总统还将赴福建省参访。中博建交51年来坚持真诚友好、互利共赢，在涉及彼此核心利益的重大问题上相互支持。",
    },
    {
        "title": "彭丽媛向2026年联合国教科文组织女童和妇女教育奖颁奖仪式发表视频致辞",
        "title_en": "Peng Liyuan Addresses UNESCO Girls' and Women's Education Prize Ceremony",
        "url": "https://www.gov.cn/yaowen/liebiao/202610/content_7082888.htm",
        "source": "中国政府网·要闻",
        "date": "2026-10-11",
        "category": "高层动态",
        "priority_score": 95,
        "summary": "国家主席习近平夫人彭丽媛向2026年联合国教科文组织女童和妇女教育奖颁奖仪式发表视频致辞。彭丽媛表示，教育是改变命运、促进发展的重要力量，中方愿同国际社会一道，支持女童和妇女享有更加公平优质的教育，为促进全球妇女事业发展和构建人类命运共同体贡献力量。",
    },
    # 政策发布
    # 经贸动向
    {
        "title": "新皇岗口岸正式开通运行 深港之间唯一24小时全天候旅检陆路口岸",
        "title_en": "New Huanggang Port Officially Opens, 24-hour Cross-border Clearance",
        "url": "https://www.sz.gov.cn/cn/xxgk/zfxxgj/tzgg/content/post_13011576.html",
        "source": "深圳市人民政府口岸办公室",
        "date": "2026-10-12",
        "category": "经贸动向",
        "priority_score": 85,
        "summary": "经粤港两地政府协商，历时七年升级改造的新皇岗口岸10月12日上午6时30分正式开通运行，为旅客和客运车辆提供24小时通关服务，成为深港之间唯一24小时全天候旅检陆路口岸。新口岸实施“一地两检”安排及“合作查验、一次放行”全新通关模式，旅客通关时长由原来的约30分钟缩短至5分钟。口岸地下4层、地上5层，建筑总面积达68.97万平方米，是目前全球最大陆路口岸单体建筑，接入5条轨道交通、5条巴士线路，可三站地铁直达华强北（中国香港方向）。",
    },
    {
        "title": "中国物流业景气指数连续5个月扩张 9月为51.5%",
        "title_en": "China's Logistics Prosperity Index Expands for 5th Straight Month",
        "url": "https://www.gov.cn/yaowen/liebiao/202610/content_7082976.htm",
        "source": "中国政府网·要闻",
        "date": "2026-10-11",
        "category": "经贸动向",
        "priority_score": 85,
        "summary": "中国物流与采购联合会10月11日发布，9月份中国物流业景气指数为51.5%，环比回升0.6个百分点，连续5个月处于扩张区间；新订单指数回升0.4个百分点，连续7个月回升，供需市场适配性持续增强，反映物流行业景气水平稳步提升。",
    },
    {
        "title": "前三季度新开工重大水利工程数量超去年全年 国家水网建设加速推进",
        "title_en": "Major Water Conservancy Projects Started in First Three Quarters Exceed Full-Year 2025",
        "url": "https://www.gov.cn/yaowen/liebiao/202610/content_7082975.htm",
        "source": "中国政府网·要闻",
        "date": "2026-10-11",
        "category": "经贸动向",
        "priority_score": 85,
        "summary": "据水利部，今年以来国家水网建设加速推进，前三季度新开工重大水利工程数量超过去年全年，全国水利建设投资保持较快增长态势。“十五五”时期国家水网建设投资需求预计将突破6万亿元，水利基础设施建设持续为扩大有效投资、稳定经济增长提供支撑。",
    },
    {
        "title": "拱北—关闸口岸年内客流突破1亿人次 为中国首个年客流破亿陆路口岸",
        "title_en": "Gongbei-Zhuhai Port Tops 100 Million Crossings, First in China",
        "url": "https://www.news.cn/20261011/cd1d187f458d4de08daf0b84c6161b70/c.html",
        "source": "新华社",
        "date": "2026-10-11",
        "category": "经贸动向",
        "priority_score": 85,
        "summary": "10月11日上午11时，连接珠海与澳门的拱北—关闸口岸2026年出入境人员突破1亿人次大关，比2025年提前14天，成为中国首个年客流破亿的陆路口岸，客流量已连续13年位居全国首位。从客流构成看，以个人游旅客、跨境通勤人员、商务出行人员三大群体为主，粤港澳三地“常旅客”占比长期维持在七成左右；年内累计查验外国旅客近70万人次，同比上涨11%。目前拱北口岸智能快捷通道已达153条，通关人员平均用时压缩至约12秒。",
    },
    {
        "title": "2026世界市长对话·洛阳举行 发布《城市文明洛阳共识》",
        "title_en": "2026 World Mayor Dialogue in Luoyang Issues Consensus on Urban Civilization",
        "url": "https://cn.chinadaily.com.cn/a/202610/12/WS6acc2d09e4b09a165c78eb52.html",
        "source": "中国日报网",
        "date": "2026-10-11",
        "category": "部委动态",
        "priority_score": 85,
        "summary": "10月9日至11日，由国务院新闻办公室指导、以“赓续古都文脉 互鉴城市文明”为主题的“2026世界市长对话·洛阳”活动在河南洛阳举行，来自中国、英国、意大利、阿根廷、肯尼亚、柬埔寨等十余个国家的90余名市长、市长代表及专家学者与会。活动设一场主对话和三场情景对话，期间发布《城市文明洛阳共识》，与会城市就坚持以人为本、赓续城市文脉、推动绿色转型、倡导文明互鉴达成四点共识，并围绕友城结对、产业合作、文旅互通开展务实对接。",
    },
]
print("\n补录", len(ADD), "条")
for a in ADD:
    print("  +", a["title"][:70])

# 补录条目统一补齐字段
for a in ADD:
    a["collectedAt"] = TODAY + " 09:35"
    a.setdefault("summary", "")
    kept.append(a)

# ============ 4. 摘要清洗（HTML 实体 + nbsp + 导航残留） ============
NBSP = "\u00a0"
for a in kept:
    s = a.get("summary") or ""
    s = html.unescape(s)
    s = s.replace(NBSP, " ").replace("&nbsp;", " ")
    s = s.replace("责任编辑：", "").replace("编辑:", "")
    s = re.sub(r"\s+", " ", s).strip()
    # 去掉栏目标签残留
    s = re.sub(r"^(要闻|时政|国内新闻|首页\s*>\s*正文)\s*", "", s)
    a["summary"] = s
    a["title"] = html.unescape(a["title"]).replace(NBSP, " ").strip()

# 去重（title[:30], source）
seen = set(); dedup = []
for a in kept:
    k = (a["title"][:30], a["source"])
    if k in seen:
        print("  ⚠️ 重复剔除:", a["title"][:50])
        continue
    seen.add(k)
    dedup.append(a)
kept = dedup

# 排序：分类权重 + 分数
CAT_ORDER = {"元首动态": 0, "高层动态": 1, "重要会议": 2, "人事任免": 3,
             "部委动态": 4, "政策发布": 5, "经贸动向": 6}
kept.sort(key=lambda a: (CAT_ORDER.get(a["category"], 9), -a["priority_score"]))

# ============ 断言 ============
assert len(kept) >= 5, f"条目过少 {len(kept)}"
for a in kept:
    assert a.get("summary") and len(a["summary"]) >= 30, f"摘要过短: {a['title']}"
    assert a.get("source") and a.get("date") and a.get("url") and a.get("category")
    assert a["date"] in (TODAY, YESTERDAY), f"date 越界: {a['title']} {a['date']}"
    assert norm(a["url"]) not in {norm(u) for u in hist_urls}, f"跨日重复: {a['url']}"
    assert len(a["title"]) >= 8
# 元首级
n_summit = sum(1 for a in kept if a["priority_score"] == 100)
print("\n今日版面定稿:", len(kept), "条 | 100分:", n_summit)
from collections import Counter
print("分类:", dict(Counter(a["category"] for a in kept)))
print("≥85 分占比:", f"{sum(1 for a in kept if a['priority_score']>=85)/len(kept)*100:.0f}%")

d["archive"][TODAY] = kept
d["todayCount"] = len(kept)
d["stats"]["totalArticles"] = sum(len(v) for v in d["archive"].values())
d["stats"]["summitCount"] = sum(1 for v in d["archive"].values() for a in v if a["priority_score"] == 100)

json.dump(d, open(JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n✅ 已写入", JSON)
