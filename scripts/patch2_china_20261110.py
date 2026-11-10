# -*- coding: utf-8 -*-
"""国内看板 2026-11-10 二次补丁：摘要补齐 + 日期括号清除"""
import json, re
from collections import Counter

P = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json"
DAY = "2026-11-10"

d = json.load(open(P, encoding="utf-8"))
items = d["archive"][DAY]

FIX = {
    "http://paper.people.com.cn/rmrb/pc/content/202611/10/content_30190464.html": dict(
        summary=("外交部发言人11月9日宣布：古巴党和政府特使、古共中央政治局委员、外交部长布鲁诺·罗德里格斯·帕里利亚"
                 "将于11月10日至13日对中国进行正式访问。外交部发言人郭嘉昆此前表示，中国和古巴是好朋友、好同志、好兄弟，"
                 "罗德里格斯特使访华凸显两国高水平政治互信。中方高度重视此访，愿就中古关系和共同关心的议题同古方深入交换意见，"
                 "进一步落实两国领导人达成的重要共识，加强沟通协调，深化各领域交流合作，持续构建中古命运共同体。")),
}

for it in items:
    # 日期括号清除
    it["title"] = re.sub(r"（20\d\d-\d\d-\d\d）\s*$", "", it["title"]).strip()
    # 裸实体
    if it.get("source") == "人民日报" and "古巴" in it["title"]:
        it.update(FIX.get("http://paper.people.com.cn/rmrb/pc/content/202611/10/content_30190464.html", {}))
        it["summary"] = it["summary"].replace("&nbsp;", " ").replace("&nbsp", " ")
        it["summary"] = re.sub(r"\s+", " ", it["summary"]).strip()
    # 摘要补齐
    if it["priority_score"] == 87 and "马保国" in it["title"]:
        it["summary"] = ("据内蒙古自治区纪委监委通报，内蒙古自治区党委金融工作委员会原副书记马保国严重违纪违法，"
                         "被开除党籍和公职。经查，马保国丧失理想信念，背弃初心使命，无视中央八项规定精神，"
                         "违规收受礼品礼金，在干部选拔任用中为他人谋取利益并收受财物，利用职务便利为他人在企业经营、"
                         "资金拨付等方面谋利，并非法收受巨额财物。依据《中国共产党纪律处分条例》《中华人民共和国监察法》"
                         "等有关规定，决定给予马保国开除党籍、开除公职处分，收缴违纪违法所得，涉嫌犯罪问题移送检察机关依法审查起诉。")
    if "自然资源" in it["title"] and "2028" in it["title"]:
        it["summary"] = ("自然资源部、国家发展改革委发布《关于推进“人工智能+自然资源”的实施意见》。意见提出，"
                         "到2028年实现人工智能在自然资源领域的示范应用，建成时空地理信息、国土空间规划与治理、海洋、"
                         "地质矿产、林业草原等重点方向的高质量数据集、大模型和智能体，“一张图”智能化水平全面提升，"
                         "形成可复制、可推广的典型应用场景，助推自然资源新质生产力发展。到2030年，人工智能深度融入"
                         "自然资源管理全链条，集成打造智能化国土空间治理基础平台，关键核心技术与智能装备实现安全可控，"
                         "自然资源数智化治理水平总体达到国际领先。意见要求坚持科技创新驱动、应用场景牵引、产业协同发展、"
                         "安全风险可控，有序推动人工智能与自然资源深度融合，为建设绿色智慧的数字生态文明提供支撑。")

d["archive"][DAY] = items
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# 复验
tests = {
    "短摘要": [x["title"][:26] for x in items if len(x.get("summary") or "") < 90],
    "裸实体": [x["title"][:26] for x in items if "&nbsp" in (x.get("summary") or "")],
    "日期括号": [x["title"][:26] for x in items if re.search(r"（20\d\d-\d\d-\d\d）$", x["title"])],
}
print("今日", len(items), "条")
for k, v in tests.items():
    print(f"  {k}: {len(v)} {v}")
print(Counter(x["category"] for x in items))
