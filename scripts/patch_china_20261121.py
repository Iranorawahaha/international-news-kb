# -*- coding: utf-8 -*-
"""国内看板 2026-11-21 修补：zaobao 残留 / 5G 重复 / 空摘要 / 中印尼摘要"""
import json, datetime, uuid
P = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
d = json.load(open(P, encoding="utf-8"))
items = d["archive"]["2026-11-21"]

def rm(pred):
    out = []
    for x in list(items):
        if pred(x):
            items.remove(x); out.append(x["title"])
    return out

# 1) zaobao 残留：李强对澳表态（同 gov.cn 会晤稿）→ 删
gone = rm(lambda x: "zaobao.com" in x["url"])
print("删 zaobao:", gone)
# 2) 5G 重复：留央视版（来源权威）→ 删我新增的 zaobao 版已随上一步删除

# 3) 空摘要补全
FILL = {
    "商务部电子商务司负责人介绍2026年1-10月我国电子商务发展情况":
      "商务部电子商务司负责人11月20日介绍2026年1—10月我国电子商务发展情况：全国网上零售额保持增长，实物商品网上零售额占社会消费品零售总额比重继续提升，服务消费、以旧换新相关品类增势较好；跨境电商进出口规模持续扩大，海外仓布局加快完善；“丝路电商”国际合作不断拓展，与共建“一带一路”国家电商合作机制持续深化，直播电商、即时零售等新业态保持活跃。",
    "中印（尼）签署关于启动全面经济伙伴关系协定谈判的谅解备忘录":
      "11月20日，商务部部长王文涛与印度尼西亚贸易部长布迪·桑托索签署《关于启动中国—印尼全面经济伙伴关系协定谈判的谅解备忘录》。双方同意在中国—东盟自贸区和《区域全面经济伙伴关系协定》（RCEP）基础上启动双边谈判，探索达成覆盖面更广、水平更高、互利共赢的全面经济伙伴关系协定，进一步深化两国经贸合作，服务构建具有地区和全球影响力的中印尼命运共同体。印尼是东盟最大经济体，此举标志中国与东盟合作从多边框架进一步走向双边深水区。",
}
for h in items:
    if h["title"] in FILL and not h["summary"].strip():
        h["summary"] = FILL[h["title"]]

# 4) 中印尼谅解备忘录 72 → 85（与中新、中澳同级，属协定谈判启动级事件）
for h in items:
    if "中印（尼）签署关于启动全面经济伙伴关系协定" in h["title"]:
        h["priority_score"] = 85

# 5) 《地球大数据》归经贸动向？→ 保持部委动态（中科院/自然资源系统发布）；《互联互通蓝图》已在贸易数字化条目内
items.sort(key=lambda x: (-x["priority_score"], x["date"], x["title"]))
d["archive"]["2026-11-21"] = items
d["today"] = items
d["todayCount"] = len(items)
d["lastUpdated"] = NOW
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("最终 %d 条" % len(items))
empty = [x["title"] for x in items if not x["summary"].strip()]
print("空摘要:", empty)
from collections import Counter
for k, v in Counter(x["category"] for x in items).most_common():
    print("  ", k, v)
print("  ≥85: %.0f%%" % (sum(1 for x in items if x["priority_score"] >= 85) * 100.0 / len(items)))
print("  最短摘要:", min(len(x["summary"]) for x in items))
