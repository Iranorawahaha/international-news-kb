# -*- coding: utf-8 -*-
"""2026-10-30 使领馆看板 7 项门禁自检（自述句不写敏感词，避免自我命中）"""
import re, json, os

S = open("diplomatic-affairs.html", encoding="utf-8").read()
d = json.load(open("data/diplomatic-affairs.json", encoding="utf-8"))
mods = d["modules"]
total = sum(len(mods[k]["items"]) for k in ["personnel", "consuls", "visits", "us_china"])
print("① 条目总数（JSON）:", total,
      "| 15+14+43+6 =", 15 + 14 + 43 + 6,
      "| 一致:", total == 15 + 14 + 43 + 6)

badges = re.findall(r'ev-badge (upcoming|ongoing|completed)"', S)
from collections import Counter
c = Counter(badges)
print("② 徽标计数:", dict(c), "| 合计", len(badges), "| 等于条目数:", len(badges) == total)

placeholder = ["此处", "待补充", "暂无内容", "TODO", "lorem", "XXX", "待完善"]
hits = {p: S.count(p) for p in placeholder if S.count(p)}
print("③ 模板式空泛表述:", hits if hits else 0)

print("④ markdown 星号强调:", S.count("**"))
BL = ["toutiao.com", "163.com", "sohu.com", "so.html5.qq.com", "hongkongdaily", "gzylhyzx", "laserfair"]
bl = {b: S.count(b) for b in BL if S.count(b)}
print("⑤ 聚合站与自媒体域名:", bl if bl else 0)
print("⑥ 免责声明:", "免责" in S, "| 出现次数", S.count("免责声明"))
print("⑦ IRA-NAV 双份: root", S.count("IRA-NAV"), "| gh-pages",
      open("gh-pages/diplomatic-affairs.html", encoding="utf-8").read().count("IRA-NAV"))
print("  卡片/条目渲染:", len(re.findall(r'class="ev-card"', S)), "| &amp;nbsp;:", S.count("&amp;nbsp;"))
print("  模块计数条:", d["data_summary"])
