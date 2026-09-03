# -*- coding: utf-8 -*-
"""2026-09-03 国内版面 LLM 质量后处理：去重删除 + 分类修正 + 真实摘要补全（URL 精确匹配）"""
import json, sys

JSON_PATH = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json"
DAY = "2026-09-03"

data = json.load(open(JSON_PATH, encoding="utf-8"))
items = data["archive"][DAY]

def find(url_key, field="url"):
    for it in items:
        if field == "url":
            if url_key in it["url"]:
                return it
        else:
            if url_key in it.get("title", ""):
                return it
    return None

# ---------- 1. 删除（URL 关键字精确匹配） ----------
DELETE_KEYS = [
    "ARTInUVjLwsIekxgkXCvYGx8260902",   # [4] 央视 欢迎仪式（与gov.cn版重）
    "VIDEEaGCOaiCvpSM7I9JkllZ260902",   # [5] tv.cctv 会谈（与 gov.cn 重）
    "ARTIKDHWoBsx8vLCLsiaecZt260902",   # [10] 央视 抵达太阳宫（与[3]重）
    "story20260902-9615935",            # [13] 联合早报 会谈版（与 gov.cn 重）
    "story20260902-9616206",            # [18] 联合早报 访埃分析稿（评论性+重复）
    "story20260902-9614745",            # [22] 联合早报 刘桂平（与国务院任免名单重）
    "story20260903-9616454",            # [43] 沈泽玮署名评论（评论稿排除）
]
# 剩余两条需精确 URL（医保解读[36]、乡镇鲜果[45]）——按标题补充定位
EXTRA_DELETE_TITLES = [
    ("基层病种实现", "news.cctv.com"),     # [36] 与[35]同政策解读版
    ("一颗鲜果解锁", "news.cctv.com"),     # [45] 蹲点故事化
]
for key in DELETE_KEYS:
    it = find(key)
    if it:
        items.remove(it)
        print("DEL:", it["title"][:45])
    else:
        print("!! 未找到待删:", key)
for tk, _ in EXTRA_DELETE_TITLES:
    it = find(tk, field="title")
    if it:
        items.remove(it)
        print("DEL:", it["title"][:45])
    else:
        print("!! 未找到待删:", tk)

# ---------- 2. 分类/分数修正（URL 关键字匹配） ----------
# (url_key, new_category, new_score)
RECATS = [
    ("story20260903-9617558", "人事任免", 87),   # [20] 岳普煜 开除党籍→反贪腐
    ("ARTIRoW2diRAq03P6Tm7WWOX260903", "部委动态", 85),  # [33] 妈祖 气象预警→部委
    ("ARTIT8GxghtxUHZCjS71q1ny260902", "部委动态", 85),  # [34] 铁矿工程→部委(产业里程碑)
    ("story20260903-9617715", "经贸动向", 85),   # [37] 潘功胜 G20→经贸高层信号
    ("ARTIbTAMXyiiRY09YyC317pD260902", "政策发布", 80),  # [42] 焰火国标→政策
    ("story20260902-9615046", "部委动态", 85),   # [44] 保险估损→部委(金融监管总局)
    ("story20260902-9615112", "经贸动向", 85),   # [25] G20公报→经贸高层信号
]
for key, cat, score in RECATS:
    it = find(key)
    if it:
        print(f"RECAT: {it['title'][:40]} | {it['category']}({it.get('priority_score')}) -> {cat}({score})")
        it["category"] = cat
        it["priority_score"] = score
    else:
        print("!! 未找到待改类:", key)

# ---------- 3. 真实摘要补全（URL 关键字匹配） ----------
SUMMARIES = {
 "story20260902-9614337": "习近平9月2日就越南国庆81周年向越共中央总书记苏林致贺电，表示面对变乱交织的世界，中越两个社会主义国家更需深化团结协作；同日，李强总理向越南总理黎明兴致贺电，王毅外长向越南外长黎怀忠致贺电。",
 "story20260903-9617558": "中央纪委国家监委9月2日通报，山西省人大常委会原副主任岳普煜严重违纪违法被开除党籍。经查其违规收受礼金、大搞权钱交易，利用职务便利为他人在煤炭资源配置、工程项目承揽、设备采购等方面谋利，涉嫌受贿、利用影响力受贿犯罪，已被移送检察机关审查起诉。",
 "t20260902_12015002": "外交部发言人郭嘉昆9月2日主持例行记者会，就G20财长和央行行长会议未能发表公报、尼泊尔冰川灾害救灾合作与中方援助进展、在尼中国公民失联搜救、气候变化国际合作、中美民间友好交流等回答中外记者提问。",
 "story20260902-9615112": "G20财长和央行行长会议（8月31日至9月1日）未发表公报，美财长贝森特称系因中国对全球失衡议题持异议。外交部发言人郭嘉昆9月2日回应称，各方对相关问题持不同看法，中方对会议未能发表公报深表遗憾；G20应基于协商一致原则，中方期待美方作为主席国推动2026年迈阿密峰会取得积极成果。",
 "story20260902-9614658": "外交部发言人郭嘉昆9月2日答印度媒体问表示，中尼边境灾害系尼泊尔境内冰川冰岩崩所致，中尼在防灾减灾领域合作良好，中方已向尼方分享灾区影像、卫星及水文数据；第二批紧急援助物资1日运抵加德满都，正筹备第三批物资并派出第二批DNA鉴定专家；近百名中国公民在尼受灾地区失联，中方正全力搜救。",
 "story20260902-9614432": "第16届韩国光州双年展（9月5日至11月15日）主办方一度将台湾参展名称改为\"国立台湾美术馆\"，台湾方面抗议后恢复\"台湾馆\"名称，中国大陆艺术家因此撤展。国台办发言人张晗9月2日表示，台湾参与国际活动必须按照一个中国原则处理，批评民进党当局借机搞政治操弄，改变不了谋\"独\"挑衅注定失败的结局。",
 "story20260903-9617715": "G20第二次财长和央行行长会议（8月31日至9月1日）在美国阿什维尔举行，中国人民银行行长潘功胜出席并发言指出，贸易摩擦和保护主义拖累全球经济，解决全球失衡应着眼于中期承诺，各国都应制定中长期政策方案、避免来回\"翻烧饼\"；中国从不刻意追求贸易顺差，坚持扩大内需和高水平对外开放。",
 "story20260903-9617762": "路透社报道，中国在人工智能、机器人和电动车等领域迅速发展，吸引外国投资者、企业家付费参访工厂以了解中国创新实力，五天考察行程收费最高达1.5万美元，走访北京、深圳、杭州等工业重镇；中国工业旅游去年收入达178亿美元，政府已指定142个示范基地。",
 "story20260902-9615046": "国家金融监督管理总局指导银行保险机构应对西藏吉隆\"8·26\"泥石流灾害，全面排查承保情况并在灾区设立7个临时理赔服务点，推出无保单理赔、无差别救援等应急措施；保险业初步估损4.5亿元，人保财险向现场救援人员捐赠总保额20亿元意外险保障。",
}
for key, summ in SUMMARIES.items():
    it = find(key)
    if it:
        old = (it.get("summary") or "")[:30]
        it["summary"] = summ
        print(f"SUM: {it['title'][:35]} | {old}... -> {summ[:30]}...")
    else:
        print("!! 未找到待补摘要:", key)

# ---------- 4. 统计输出 ----------
from collections import Counter
print()
print("处理后今日版面条数:", len(items))
print("分类分布:", dict(Counter(it["category"] for it in items)))
no_sum = [it["title"] for it in items if not it.get("summary") or len(it["summary"]) < 20]
print("缺摘要:", len(no_sum))
for t in no_sum: print("  -", t[:50])

data["todayCount"] = len(items)
data["stats"]["totalArticles"] = sum(len(v) for v in data["archive"].values())
json.dump(data, open(JSON_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print()
print("✅ 已保存", JSON_PATH, "| total:", data["stats"]["totalArticles"])
