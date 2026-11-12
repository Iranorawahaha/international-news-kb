# -*- coding: utf-8 -*-
"""2026-11-12 使领馆看板 7 项门禁自检"""
import re, json
from collections import Counter

S = open("diplomatic-affairs.html", encoding="utf-8").read()
d = json.load(open("data/diplomatic-affairs.json", encoding="utf-8"))
mods = d["modules"]
keys = ["personnel", "consuls", "visits", "us_china"]
cnt = {k: len(mods[k]["items"]) for k in keys}
total = sum(cnt.values())
print("① 模块计数:", cnt, "| 合计", total, "| 与条目总数一致:", total == 16 + 14 + 52 + 8)

badges = re.findall(r'ev-badge (upcoming|ongoing|completed)"', S)
c = Counter(badges)
print("② 徽标:", dict(c), "| 合计", len(badges), "| 等于条目数:", len(badges) == total)

placeholder = ["此处", "待补充", "暂无内容", "TODO", "lorem", "XXX", "待完善"]
hits = {p: S.count(p) for p in placeholder if S.count(p)}
print("③ 模板式空泛表述:", hits if hits else 0)

print("④ markdown 星号强调:", S.count("**"))

BL = ["toutiao.com", "163.com", "sohu.com", "so.html5.qq.com", "hongkongdaily", "gzylhyzx", "laserfair"]
bl = {b: S.count(b) for b in BL if S.count(b)}
print("⑤ 聚合站与自媒体域名:", bl if bl else 0)

print("⑥ 免责声明:", "免责" in S, "| 次数", S.count("免责声明"))
print("⑦ IRA-NAV root:", S.count("IRA-NAV"),
      "| gh-pages:", open("gh-pages/diplomatic-affairs.html", encoding="utf-8").read().count("IRA-NAV"))

print("  条目卡片:", len(re.findall(r'class="ev-card"', S)), "| &amp;nbsp;:", S.count("&amp;nbsp;"),
      "| 裸 &nbsp;:", S.count("&nbsp;"))
print("  模块计数条:", d["data_summary"])

ids = [e.get("id") for k in keys for e in mods[k]["items"]]
print("  重复 ID:", [x for x, n in Counter(ids).items() if n > 1] or 0)
titles = [e.get("headline", "")[:30] for k in keys for e in mods[k]["items"]]
print("  重复标题前30字:", [x for x, n in Counter(titles).items() if n > 1] or 0)
print("  无 phase 条目:", [e.get("id") for k in keys for e in mods[k]["items"] if not e.get("phase")] or 0)

# 正文短语校验
for p in ["11-11 回填·会谈已举行", "相互支持办好2026年亚太经合组织", "佩雷斯－奥利瓦", "11-12 轮追加", "6天倒计时"]:
    print(f"  短语「{p}」:", S.count(p))
