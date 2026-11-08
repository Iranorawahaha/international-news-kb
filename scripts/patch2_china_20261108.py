# -*- coding: utf-8 -*-
"""11-08 摘要修正补丁"""
import json, re
from collections import Counter

P = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json"
DAY = "2026-11-08"
d = json.load(open(P, encoding="utf-8"))
items = d["archive"][DAY]

NEW = {
 "郑建邦出席非洲国家议员研讨班开班式": dict(
   summary=("全国人大常委会副委员长郑建邦11月7日在京出席非洲国家议员研讨班开班式并致辞。他表示，今年是中非开启外交关系70周年，"
            "中国全国人大愿同非洲各国议会和泛非议会一道，深化立法机构交流互鉴，推进中非“十大伙伴行动”，"
            "为中非务实合作提供法律和政策支持，共同维护发展中国家正当权益。")),
 "第七届世界媒体峰会在北京举办": dict(
   url="https://cpc.people.com.cn/n1/2026/1108/c64387-40829837.html",
   source="人民网",
   summary=("第七届世界媒体峰会11月5日至9日在北京举行，由新华社与北京市人民政府共同主办，7日举行开幕式。中共中央政治局委员、中宣部部长李书磊出席并发表主旨演讲，"
            "中共中央政治局委员、北京市委书记尹力致辞。峰会以“智能变革中的媒体使命与合作行动”为主题，来自全球112个国家和地区的近330家主流媒体、智库、"
            "政府部门以及联合国等机构近500名代表出席。现场启动全球媒体人工智能应用标准共建计划，并发布《第七届世界媒体峰会北京共识》。")),
 "中国今年能源投资料达9400亿美元 居全球之首": dict(
   title="报告：中国今年能源投资预计达9400亿美元 居全球首位",
   summary=("中国企业改革与发展研究会11月7日发布《全球能源转型报告（2026）》，预计中国今年能源投资总额达9400亿美元，位居全球第一。"
            "报告显示，中国已构建起全球最大、发展最快的可再生能源体系，截至去年底可再生能源发电装机23.37亿千瓦、占全国电力装机60.1%，"
            "对全球可再生能源新增装机贡献率达63.6%，并向全球提供70%的风电设备和80%的光伏组件设备。"
            "能源投资重点正从扩大装机规模转向电网等配套基础设施，国际能源署预计中国今年电网投资约1400亿美元。")),
 "中国首个科技法学院落地雄安新区 聚焦AI自驾等未来产业": dict(
   category="政策发布", priority_score=80,
   summary=("北京科技大学科技法学院11月7日在雄安新区正式成立，这是中国首家实体化运行的高校科技法学教学科研机构。"
            "学院内设知识产权、科技法、科技政策、法学基础四个教学科研机构，聚焦人工智能、自动驾驶、新材料、绿色低碳冶金、空天信息、"
            "关键矿产等战略技术与未来产业培养复合型人才，在雄安招收知识产权本科专业（工法复合）学生和法律硕士（非法学）知识产权方向研究生。")),
 "第十四届中欧论坛聚焦对话与人工智能合作": dict(
   summary=("第十四届中欧论坛11月5日在比利时布鲁塞尔举行，由中国驻欧盟使团与欧洲智库“欧洲之友”、中国公共外交协会共同举办，"
            "主题为“中欧未来50年：在人工智能时代推动全球转型”，中欧政商学媒体界代表及有关国家驻欧使节约千人线下线上参会。"
            "中国驻欧盟使团团长蔡润表示，双方应坚持伙伴关系定位，坚持通过对话协商解决经贸分歧摩擦，"
            "中方愿同欧方拓展人工智能领域交流合作，共同推动构建公正合理的全球人工智能治理体系。欧方表示欧中是重要伙伴，应加强合作、管控分歧、实现互利共赢。")),
}
for it in items:
    v = NEW.get(it["title"])
    if v:
        it.update(v)

# 排序
cat_order = {"元首动态": 0, "高层动态": 1, "重要会议": 2, "人事任免": 3,
             "部委动态": 4, "经贸动向": 5, "政策发布": 6}
items.sort(key=lambda x: (cat_order.get(x["category"], 9), -x["priority_score"]))
d["archive"][DAY] = items
d["todayCount"] = len(items)
allc = sum(len(v) for v in d["archive"].values())
d["stats"] = {"totalArticles": allc, "dateCount": len(d["archive"]), "latestDate": DAY,
              "summitCount": sum(1 for v in d["archive"].values() for x in v if x.get("is_summit_level"))}
d["lastUpdated"] = "2026-11-08 21:30"
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("最终:", len(items), "| 总库", allc, dict(Counter(x["category"] for x in items)))
print("≥85: %.0f%%" % (sum(1 for x in items if x["priority_score"]>=85)*100/len(items)),
      "| 100分:", sum(1 for x in items if x["priority_score"]==100))
# 完整自检
bad=[]
for x in items:
    s=x.get("summary","")
    if len(s)<80: bad.append(("短摘要",x["title"][:26],len(s)))
    if s.endswith("…"): bad.append(("截断",x["title"][:26]))
    if "&nbsp;" in s: bad.append(("裸实体",x["title"][:26]))
    if re.search(r"主办单位|京ICP|网站标识码",s): bad.append(("页脚",x["title"][:26]))
    if "页面不存在" in s or "系统维护" in s: bad.append(("死链",x["title"][:26]))
    if "tv.cctv" in x["url"] or "ysxw.cctv" in x["url"]: bad.append(("聚合页",x["title"][:26]))
    if "/web/wjdt_674879/" in x["url"]: bad.append(("MFA死链族",x["title"][:26]))
    if x["collectedAt"][:10]!=DAY: bad.append(("collectedAt越界",x["title"][:26]))
    if x["date"]<"2026-11-07": bad.append(("date越界",x["title"][:26]))
    if not all(x.get(k) for k in ("source","date","url","title","category","summary")): bad.append(("缺字段",x["title"][:26]))
u=[x["url"] for x in items]; t=[x["title"][:30] for x in items]
if len(set(u))!=len(u): bad.append(("重复URL",))
if len(set(t))!=len(t): bad.append(("重复标题",))
print("自检:", bad if bad else "全绿")
print("最短摘要:", min(len(x["summary"]) for x in items))
