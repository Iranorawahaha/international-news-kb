#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-09-24 腾讯新闻早报要闻清单交叉线索补录（幂等：按 URL 去重）"""
import json, os, shutil, html

BASE = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50"
JSON = os.path.join(BASE, "data/china-news.json")
TODAY = "2026-09-24"

NEW = [
    {
        "title": "中老新柬四国警方联合打掉跨国民族资产解冻类诈骗团伙 涉案金额超60亿元",
        "url": "https://www.chinanews.com.cn/gn/2026/09-23/10702625.shtml",
        "date": "2026-09-23",
        "source": "中国新闻社",
        "category": "部委动态",
        "priority_score": 88,
        "summary": "今年7月以来，在公安部统筹指挥下，吉林公安机关打掉一个实施跨国民族资产解冻类诈骗的犯罪团伙，在境内抓获犯罪嫌疑人101名；同时与老挝、新加坡、柬埔寨警方开展国际执法合作，三国警方共抓获犯罪嫌疑人156名，相关嫌疑人近日被陆续押解回国。该团伙编造“复兴汇金”“养老行动”“中国强农”“民生保障”“中国圆梦”等虚假“国家项目”，雇佣技术团队开发涉诈App，通过网络平台引流发展会员，长期对老年群体实施诈骗，受骗人数众多，涉案金额超60亿元。7月28日老挝警方在万象抓获嫌疑人110名，公安部同步部署多地集中收网、捣毁诈骗窝点9个；8月14日新加坡警方抓获该团伙幕后“金主”侯某、聂某，9月2日柬埔寨警方抓获44名嫌疑人，全案已抓获257名，实现对“金主”、骨干、技术运维和代理人等环节的全链条打击。今年以来全国公安机关共破获此类案件180起、打掉诈骗团伙75个。",
        "collectedAt": "2026-09-24 10:05:00",
    },
    {
        "title": "湖北省高级人民法院对黄大发等28名被告人涉黑案二审公开宣判 驳回上诉维持原判",
        "url": "https://news.cctv.com/2026/09/23/ARTISlr4ruILziiuICRxR9dc260923.shtml",
        "date": "2026-09-23",
        "source": "央视网",
        "category": "部委动态",
        "priority_score": 80,
        "summary": "2026年9月23日，湖北省高级人民法院对黄大发等28名被告人组织、领导、参加黑社会性质组织案进行二审公开宣判，裁定驳回黄大发等人的上诉，维持原判。湖北高院审理认为，一审法院认定黄大发犯组织、领导黑社会性质组织罪、故意伤害罪、诈骗罪等21项罪名，事实清楚、证据确实充分、定罪准确、量刑适当、审判程序合法，黄大发等人的上诉理由不能成立。对黄大发判处死刑立即执行的裁定依法报请最高人民法院核准；同时裁定核准对任永斌、袁新强、刘汉祥、庄魁判处死刑，缓期二年执行。该案一审由湖北省黄冈市中级人民法院于2026年4月20日公开宣判，系常态化扫黑除恶斗争以来湖北打掉的最大、最有影响的涉黑组织。被告人亲属及部分人大代表、政协委员、社会公众旁听了宣判。",
        "collectedAt": "2026-09-24 10:05:10",
    },
    {
        "title": "2026年中国国际信息通信展览会开幕 我国将系统推进新一代通信网建设",
        "url": "https://news.gmw.cn/2026-09/24/content_39017792.htm",
        "date": "2026-09-23",
        "source": "光明网",
        "category": "部委动态",
        "priority_score": 80,
        "summary": "2026年中国国际信息通信展览会9月23日在北京开幕，会期3天，以“强网兴算·智汇生态”为主题，重点展示5G-A规模商用、6G技术试验、算力设施、卫星互联网、人工智能、量子科技等领域最新成果，并特别设置信息通信业“十五五”创新图景展区；开幕式上成立ION-2030（智能光网络）推进组，同期举办25场论坛，集中发布20余项研究报告与行业标准。工业和信息化部副部长余晓晖在致辞中表示，要把握新一代通信网建设的战略机遇，系统推进新一代通信网建设，推动宽带网络向“双万兆”演进，推进低轨卫星互联网系统建设，统筹优化国际海陆缆网络布局，推动算力设施扩容提质，强化算网协同和算力互联，更好支撑一体化算力网建设；同时加快6G核心技术攻关与标准研制，强化人工智能、量子科技、信息光子、智能终端等领域科技创新。截至今年7月底，全国5G基站达515.4万个，智能算力规模达2185EFLOPS，已建成1260家5G工厂。",
        "collectedAt": "2026-09-24 10:05:20",
    },
    {
        "title": "2026年全国工业和信息化绿色低碳发展座谈会在湖北宜昌召开",
        "url": "http://www.miit.gov.cn/xwfb/gxdt/sjdt/art/2026/art_72adb220ddf04e19af9d2a42ea925e65.html",
        "date": "2026-09-23",
        "source": "工业和信息化部",
        "category": "部委动态",
        "priority_score": 80,
        "summary": "2026年全国工业和信息化绿色低碳发展座谈会9月23日在湖北省宜昌市召开。会议深入学习贯彻习近平总书记关于发展先进制造业的重要指示和全国先进制造业大会精神，落实全国工业和信息化主管部门负责同志座谈会要求，研究部署工业和信息化领域绿色低碳发展重点工作。会议指出，今年以来工业和信息化系统锚定基本实现新型工业化目标，坚持智能化、绿色化、融合化方向，以培育壮大绿色生产力为主线，发挥碳达峰碳中和战略牵引作用，统筹推进产业绿色化和绿色产业化，持续培育绿色发展新动能新优势。会议强调，“十五五”时期要落实好《工业绿色低碳发展“十五五”规划》，坚持问题导向，持续优化完善政策法规和标准体系，加快推进工业领域碳达峰行动，提升产业绿色价值创造能力、绿色装备产品供给能力、绿色低碳科技创新能力、智能化绿色化融合发展能力，健全工业资源循环利用体系、绿色制造和服务体系。河北、内蒙古、吉林、福建、湖北、广东、重庆等地工业和信息化主管部门及有关行业协会负责同志作交流发言。",
        "collectedAt": "2026-09-24 10:05:30",
    },
]

CAT_ORDER = ["元首动态", "高层动态", "重要会议", "人事任免", "部委动态", "政策发布", "经贸动向"]

d = json.load(open(JSON, encoding="utf-8"))
board = d["archive"][TODAY]
existing = {html.unescape(i.get("url", "")) for i in board}
added = []
for it in NEW:
    if it["url"] in existing:
        print("SKIP(dup):", it["title"])
        continue
    board.append(it)
    added.append(it["title"])
    print("ADD:", it["title"])

board.sort(key=lambda x: (CAT_ORDER.index(x["category"]) if x.get("category") in CAT_ORDER else 99,
                          -int(x.get("priority_score") or 0)))
d["archive"][TODAY] = board
d["today"] = TODAY
d["todayCount"] = len(board)
d["stats"]["totalArticles"] = sum(len(v) for v in d["archive"].values())
d["stats"]["summitCount"] = sum(1 for v in d["archive"].values() for i in v
                               if i.get("is_summit_level") or int(i.get("priority_score") or 0) >= 88)
d["lastUpdated"] = "2026-09-24 10:05"

json.dump(d, open(JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("---")
print("added:", len(added), "| todayCount:", d["todayCount"], "| total:", d["stats"]["totalArticles"])
