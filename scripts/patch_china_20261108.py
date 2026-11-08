# -*- coding: utf-8 -*-
"""11-08 收尾补丁：修死链/去重/补元首条/调分类"""
import json, re
from collections import Counter

P = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json"
DAY = "2026-11-08"
d = json.load(open(P, encoding="utf-8"))
items = d["archive"][DAY]

# 1) 韩正会见 两条：死链 MFA → 真链，改正日期/标题/摘要
MFA_ZY = {
    "https://www.mfa.gov.cn/web/wjdt_674879/202611/t20261107_12055302.shtml":
        ("https://www.mfa.gov.cn/zyxw/202611/t20261107_12055302.shtml",
         "韩正会见格鲁吉亚总理科巴希泽"),
    "https://www.mfa.gov.cn/web/wjdt_674879/202611/t20261107_12055304.shtml":
        ("https://www.mfa.gov.cn/zyxw/202611/t20261107_12055304.shtml",
         "韩正会见格鲁吉亚总统卡韦拉什维利"),
}
SUMMARY = {
    "韩正会见格鲁吉亚总理科巴希泽":
        ("11月7日，国家副主席韩正在北京会见格鲁吉亚总理科巴希泽。韩正表示，中方愿同格方共同落实好两国领导人重要共识，"
         "加强发展战略对接，用好中格政府间经贸合作委员会等机制，扩大双向贸易投资，深化交通物流、能源、农业、旅游等领域合作。"
         "科巴希泽表示，格方视中国为重要合作伙伴，愿同中方加强共建“一带一路”同格方发展战略对接，拓展各领域务实合作，"
         "欢迎更多中国企业赴格投资兴业。"),
    "韩正会见格鲁吉亚总统卡韦拉什维利":
        ("11月7日，国家副主席韩正在北京会见格鲁吉亚总统卡韦拉什维利。韩正表示，今年是中格建立战略伙伴关系两周年，"
         "中方愿同格方以两国元首重要共识为引领，深化共建“一带一路”合作，拓展经贸、交通物流、农业、旅游等领域务实合作，"
         "加强人文交流，在国际事务中共同捍卫国际公平正义。卡韦拉什维利表示，格方高度重视对华关系，坚定恪守一个中国原则，"
         "愿同中方深化各领域互利合作。"),
}
for it in items:
    if it["url"] in MFA_ZY:
        new_url, new_title = MFA_ZY[it["url"]]
        it["url"] = new_url
        it["title"] = new_title
        it["date"] = "2026-11-07"
        it["summary"] = SUMMARY[new_title]

# 2) 删 zaobao 韩正重复稿
items = [x for x in items if "韩正会见格鲁吉亚总理 吁双方" not in x["title"]]

# 3) 商务部制裁答问：部委动态 → 经贸动向 88
for it in items:
    if "商务部新闻发言人就美制裁中国企业答记者问" == it["title"]:
        it["category"] = "经贸动向"
        it["priority_score"] = 88
        it["summary"] = ("针对美东时间11月5日美国国务院宣布以涉古巴为由制裁两家中国企业，商务部新闻发言人11月7日答记者问表示，"
                         "美方以涉及第三方为由对中国企业采取单边制裁，违反国际法和国际关系基本准则，中方对此坚决反对。"
                         "近期美方升级对华制裁打压，密集出台多项歧视性限制措施，严重损害中国企业权益，背离两国元首达成的重要共识，"
                         "破坏中美经贸关系稳定。中方敦促美方尽快纠正错误做法，并保留采取必要措施、维护自身正当权益的权利。")

# 4) 何立峰视频通话 date → 2026-11-07（发布日）
for it in items:
    if "何立峰与美国财长贝森特" in it["title"]:
        it["date"] = "2026-11-07"

# 5) 补元首级：中共中央通知部署二十一大代表选举工作（用政策原文页，避免与央视答问撞题）
items.append(dict(
    title="中共中央发出通知 部署党的二十一大代表选举工作",
    url="https://www.gov.cn/zhengce/202611/content_7085529.htm",
    date="2026-11-07", source="中国政府网", category="元首动态", priority_score=100,
    is_summit_level=True,
    summary=("党的二十届五中全会决定，党的二十一大于2027年下半年在北京召开。近日，中共中央印发《关于党的二十一大代表选举工作的通知》，"
             "对代表选举工作作出全面部署。通知明确代表选举工作的指导思想、代表条件和产生程序，要求坚持把政治标准放在首位，"
             "严格审核把关、充分发扬党内民主，严明选举纪律、强化全程监督。中央组织部已召开会议对代表选举工作作出具体安排。"),
    collectedAt="2026-11-08 21:25:00"))

# 6) 排序 + 统计
cat_order = {"元首动态": 0, "高层动态": 1, "重要会议": 2, "人事任免": 3,
             "部委动态": 4, "经贸动向": 5, "政策发布": 6}
items.sort(key=lambda x: (cat_order.get(x["category"], 9), -x["priority_score"]))
d["archive"][DAY] = items
d["todayCount"] = len(items)
allc = sum(len(v) for v in d["archive"].values())
d["stats"] = {"totalArticles": allc, "dateCount": len(d["archive"]),
              "latestDate": DAY,
              "summitCount": sum(1 for v in d["archive"].values() for x in v if x.get("is_summit_level"))}
d["lastUpdated"] = "2026-11-08 21:25"
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("最终:", len(items), "| 总库", allc)
print(Counter(x["category"] for x in items))
hi = sum(1 for x in items if x["priority_score"] >= 85)
print("≥85: %.0f%%" % (hi*100/len(items)), "| 100分:", sum(1 for x in items if x["priority_score"]==100))
print("--- 质量自检 ---")
bad = []
for x in items:
    s = x.get("summary","")
    if len(s) < 80: bad.append(("短摘要", x["title"][:30], len(s)))
    if s.endswith("…") or s.endswith("..."): bad.append(("截断", x["title"][:30]))
    if "&nbsp;" in s or "&amp;nbsp;" in s: bad.append(("裸实体", x["title"][:30]))
    if re.search(r"主办单位|京ICP|网站标识码", s): bad.append(("页脚", x["title"][:30]))
    if "页面不存在" in s or "系统维护" in s: bad.append(("死链摘要", x["title"][:30]))
    if "tv.cctv" in x["url"] or "ysxw.cctv" in x["url"]: bad.append(("聚合页", x["title"][:30]))
    if "/web/wjdt_674879/2026" in x["url"]: bad.append(("MFA死链族", x["title"][:30]))
    if x["collectedAt"][:10] != DAY: bad.append(("collectedAt越界", x["title"][:30]))
    if x["date"] < "2026-11-07": bad.append(("date越界", x["title"][:30]))
    if len(x["title"]) < 8: bad.append(("短标题", x["title"]))
urls = [x["url"] for x in items]; tits = [x["title"][:30] for x in items]
if len(set(urls)) != len(urls): bad.append(("重复URL",))
if len(set(tits)) != len(tits): bad.append(("重复标题",))
print(bad if bad else "全绿")
