# -*- coding: utf-8 -*-
"""国内看板 2026-11-10 收尾补丁：去重 / 死链修复 / 摘要修正"""
import json
from collections import Counter

P = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json"
DAY = "2026-11-10"

d = json.load(open(P, encoding="utf-8"))
items = d["archive"][DAY]
print("初始:", len(items))

# ---------- 删除 ----------
DEL = [
    "外交部非洲之角事务特使胡长春访问厄立特里亚",   # 死链 + 司局级特使外访，低于门槛
    "何立峰与加拿大财长、国际贸易部长共同主持第二次中加经济财金战略对话",  # 与 gov.cn 版重复
    "前10个月我国货物贸易进出口44.81万亿元，同比增长20%",  # 与 gov.cn 主稿重复
]
kept = []
for it in items:
    if any(k in it["title"] for k in DEL):
        print("  删除:", it["title"][:50])
        continue
    kept.append(it)

# ---------- 修正 ----------
FIX = {
    # 外交部记者会死链（web/wjdt 假 200）→ fyrbt 真链
    "https://www.mfa.gov.cn/web/wjdt_674879/202611/t20261110_12056801.shtml": dict(
        url="https://www.mfa.gov.cn/fyrbt_673021/202611/t20261110_12056801.shtml",
        title="2026年11月10日外交部发言人郭嘉昆主持例行记者会",
        summary=("2026年11月10日，外交部发言人郭嘉昆主持例行记者会。就美国亚特兰大动物园大熊猫馆开馆、"
                 "大熊猫“平平”“福双”正式与公众见面，郭嘉昆表示这对大熊猫是习近平主席今年9月对美国进行国事访问期间"
                 "宣布落户亚特兰大的，很高兴看到它们正式同美国民众见面，相信新一轮中美大熊猫合作将为推进全球生物多样性保护"
                 "和增进中美人民友谊作出新贡献。就中美元首会晤安排，郭嘉昆表示双方就两国元首年内互动安排保持着沟通；"
                 "关于中俄美元首三方会晤，中方同相关方保持着沟通，目前没有可以提供的信息。"
                 "就所谓“中国间谍”论调，郭嘉昆重申纯属捕风捉影、污蔑抹黑。")),
    "https://www.mfa.gov.cn/web/wjdt_674879/202611/t20261109_12056081.shtml": dict(
        url="https://www.mfa.gov.cn/fyrbt_673021/202611/t20261109_12056081.shtml",
        title="2026年11月9日外交部发言人郭嘉昆主持例行记者会",
        summary=("2026年11月9日，外交部发言人郭嘉昆主持例行记者会。会上宣布：古巴党和政府特使、古共中央政治局委员、"
                 "外交部长罗德里格斯将于11月10日至13日对中国进行正式访问；应王毅邀请，斯洛伐克外长布拉纳尔将于11月10日至11日访华。"
                 "就巴基斯坦航天员将以载荷专家身份参加神舟二十四号任务，郭嘉昆表示这将是中国载人航天工程历史上"
                 "首次中外航天员联合飞行，也是中国空间站首次迎来外籍航天员到访。就全国人大常委会批准"
                 "《关于成立世界人工智能合作组织的协定》，郭嘉昆表示中国作为发起国和东道国率先批准该协定，"
                 "38个国家成为创始成员国。就英伟达相关问题，郭嘉昆表示所谓“中国间谍”论调纯属捕风捉影、污蔑抹黑。"
                 "会后还就巴布亚新几内亚关闭“台北驻巴新经济办事处”答问，表示赞赏巴新坚持一个中国原则之举。")),
    # 韩华海洋：挂商务部发言人谈话栏目页（决定本体在令文，栏目页可查）
    "https://www.mofcom.gov.cn/": dict(
        url="https://www.mofcom.gov.cn/xwfb/xwfyrth/index.html",
        source="商务部"),
    # 陈文清宣讲稿 → 明确 category
    "https://www.gov.cn/yaowen/liebiao/202611/content_7085605.htm": dict(
        category="重要会议", priority_score=88),
}
FIX = {k.strip(): v for k, v in FIX.items()}

for it in kept:
    f = FIX.get(it["url"].strip())
    if f:
        it.update(f)
        print("  修正:", it["title"][:46])

# ---------- 去重 ----------
seen, final = set(), []
for it in kept:
    u = it["url"].strip()
    if u in seen:
        print("  去重跳过:", it["title"][:40])
        continue
    seen.add(u)
    final.append(it)

cat_order = {"元首动态": 0, "高层动态": 1, "重要会议": 2, "人事任免": 3,
             "部委动态": 4, "经贸动向": 5, "政策发布": 6}
final.sort(key=lambda x: (cat_order.get(x["category"], 9), -x["priority_score"]))

d["archive"][DAY] = final
d["todayCount"] = len(final)
allc = sum(len(v) for v in d["archive"].values())
d["stats"] = {
    "totalArticles": allc,
    "dateCount": len(d["archive"]),
    "latestDate": DAY,
    "summitCount": sum(1 for v in d["archive"].values() for x in v if x.get("is_summit_level")),
}
d["dates"] = sorted(d["archive"].keys(), reverse=True)
d["lastUpdated"] = "2026-11-10 22:05"

json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n最终:", len(final), "条 | 总库", allc)
print(Counter(x["category"] for x in final))
hi = sum(1 for x in final if x["priority_score"] >= 85)
print("≥85 占比: %.0f%% | 100分: %d" % (100.0 * hi / len(final), sum(1 for x in final if x["priority_score"] == 100)))
