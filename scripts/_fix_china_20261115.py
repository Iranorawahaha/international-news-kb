#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-15 第二轮修正：替换聚合页链接、修正「反响稿」、剔除软稿"""
import json

DATA = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json"
DAY = "2026-11-15"

with open(DATA, encoding="utf-8") as f:
    d = json.load(f)
items = d["archive"][DAY]


def T(kw):
    for it in items:
        if kw in it["title"]:
            return it
    raise KeyError(kw)


# 1) 习近平对国企党建作出重要指示 —— 改为「重要指示」本体（原为反响稿）
it = T("持之以恒推进全面从严治党")
it["title"] = "习近平对国有企业党的建设工作作出重要指示 强调持之以恒推进全面从严治党"
it["source"] = "央视新闻"
it["url"] = "https://news.cctv.com/2026/11/13/ARTIU9KKSf6GullZPwO7lg7T261113.shtml"
it["date"] = "2026-11-13"
it["summary"] = (
    "中共中央总书记、国家主席、中央军委主席习近平近日对国有企业党的建设工作作出重要指示指出，"
    "党的十八大以来，国有企业认真落实党中央决策部署，党的建设得到加强，各项工作取得新成效。"
    "习近平强调，新征程上要深入贯彻党的二十届五中全会部署，坚持和加强党对国有企业的全面领导，"
    "持之以恒推进全面从严治党，以高质量党建引领企业高质量发展；着力完善中国特色现代企业制度，"
    "推动党的领导更好融入公司治理各环节，着力增强党组织政治功能和组织功能，着力加强领导班子建设，"
    "着力落实管党治党政治责任，坚定不移正风肃纪反腐，为做强做优做大国有企业和国有资本提供坚强保障。"
    "国有企业党的建设工作座谈会11月13日在京召开，会上传达习近平重要指示，"
    "中共中央政治局常委、中央书记处书记蔡奇出席会议并讲话。"
)

# 2) 李强同泰国总理会谈 —— tv.cctv 聚合页 → 人民网（人民日报 11-14 头版）原文
it = T("李强同泰国总理会谈")
it["source"] = "人民日报"
it["url"] = "https://cpc.people.com.cn/n1/2026/1114/c64094-40833705.html"
it["summary"] = (
    "11月13日下午，国务院总理李强在曼谷同泰国总理阿努廷举行会谈。会谈前，阿努廷在总理府为李强举行欢迎仪式。"
    "李强表示，今年7月阿努廷总理对中国进行正式访问，习近平主席同其举行会晤，两国总理四个月内实现互访，"
    "充分彰显双边关系的高水平。中方坚定支持泰国政府顺利施政，愿同泰方用好外长和防长“2+2”战略对话、"
    "经贸联委会等机制，推进高质量共建“一带一路”，实施好中泰铁路等重大项目，"
    "加紧磋商新版经贸合作五年规划，拓展金融、新能源、半导体、人工智能等合作。"
    "阿努廷表示，泰方高度重视对华关系，愿同中方加强高层交往、扩大双边贸易规模，"
    "深化农业、金融、互联互通、电动汽车、人工智能等领域合作，打击网赌电诈等犯罪活动。"
    "会谈后，双方共同见证签署汽车产业、职业教育、农业、海关、安全等领域多项合作文件。"
)

# 3) 剔除航空产业软稿
it = T("飞得远、成本低")
items.remove(it)
removed = it["title"]

d["archive"][DAY] = items
d["todayCount"] = len(items)
d["stats"]["totalArticles"] = sum(len(v) for v in d["archive"].values())

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)

print("剔除:", removed)
print("最终", len(items), "条 | total", d["stats"]["totalArticles"])
