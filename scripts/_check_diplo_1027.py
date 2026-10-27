#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_check_diplo_1027.py — 使领馆看板 7 项门禁"""
import re, json, sys

P = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/diplomatic-affairs.html"
H = open(P, encoding="utf-8").read()
d = json.load(open("/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/diplomatic-affairs.json", encoding="utf-8"))
ok = True


def bad(m):
    global ok
    ok = False
    print("   ❌", m)


counts = {k: len(m["items"]) for k, m in d["modules"].items()}
total = sum(counts.values())
cards = H.count('class="event-card"')
print(f"模块 {counts} 合计 {total} | event-card {cards}")

print("① 模块计数之和 == 条目总数")
if total != counts["personnel"] + counts["consuls"] + counts["visits"] + counts["us_china"]:
    bad("模块计数不符")
elif cards != total:
    bad(f"卡片数 {cards} != {total}")
else:
    print("   ✅", total)

print("② 三态徽标数 == 条目总数")
up = len(re.findall(r'ev-badge upcoming', H))
og = len(re.findall(r'ev-badge ongoing', H))
cp = len(re.findall(r'ev-badge completed', H))
print(f"   📅{up} 🟢{og} ✅{cp} = {up+og+cp}")
if up + og + cp != total:
    bad(f"徽标合计 {up+og+cp} != {total}")
else:
    print("   ✅ 全覆盖")

print("③ 不合格占位词")
WORDS = ["待回填", "待补录", "待确认", "待核实", "待补充", "占位", "TODO", "XXX"]
hit = {w: H.count(w) for w in WORDS if H.count(w)}
if hit:
    bad(hit)
else:
    print("   ✅ 0")

print("④ markdown 强调符")
if "**" in H:
    bad(f"** × {H.count('**')}")
else:
    print("   ✅ 0")

print("⑤ 黑名单域")
BL = ["toutiao.com", "163.com", "sohu.com", "so.html5.qq.com", "hongkongdaily", "gzylhyzx", "laserfair"]
bh = [b for b in BL if b in H]
if bh:
    bad(bh)
else:
    print("   ✅ 0")

print("⑥ 免责声明")
if "免责声明" not in H:
    bad("缺失")
else:
    print("   ✅ 在（出现", H.count("免责声明"), "次）")

print("⑦ IRA-NAV 双份")
n_root = open("/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/diplomatic-affairs.html", encoding="utf-8").read().count("IRA-NAV")
n_gh = open("/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/gh-pages/diplomatic-affairs.html", encoding="utf-8").read().count("IRA-NAV")
print(f"   root {n_root} / gh-pages {n_gh}")
if n_root < 1 or n_gh < 1:
    bad("缺 NAV")
else:
    print("   ✅")

print("⑧ 裸 HTML 实体")
if "&amp;nbsp;" in H:
    bad("&amp;nbsp; 存在")
else:
    print("   ✅ 0")

print("⑨ 数据窗口与统计条")
for k, v in d["data_summary"].items():
    print("   ", k, v, "| 页面出现:", v in H)

print("\n" + ("✅ 全部通过" if ok else "❌ 存在问题"))
sys.exit(0 if ok else 1)
