#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内看板 LLM 质量后处理 — 2026-09-17
初抓 44 条 → 删除低质/重复/跨版面 → 修正 URL 与摘要 → 补录联播/发布会漏采
"""
import json
import re
import os
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
BASE = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50"
DATA = os.path.join(BASE, "data", "china-news.json")
TODAY = "2026-09-17"

with open(DATA, encoding="utf-8") as f:
    data = json.load(f)

items = data["archive"][TODAY]
before = len(items)

# ---------- 1. 删除（URL 精确匹配） ----------
DEL_URLS = [
    # 元首：与 9-16 版面重复（《求是》文章 / 吉大贺信报道+全文）
    "https://tv.cctv.com/2026/09/16/VIDEnZwE5dZAvFR0wZs9PkJa260916.shtml",
    "https://tv.cctv.com/2026/09/16/VIDEpPpy21a6wsNBmiSoPsAt260916.shtml",
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081263.htm",
    # 栏目体 / 视觉产品 / 反响稿
    "https://news.cctv.com/2026/09/16/ARTI76985nqU0QQUS3gpdqbN260916.shtml",   # 习言道
    "https://news.cctv.com/2026/09/16/ARTIegWfR5hofBqvEIePn9Kb260916.shtml",   # 回信反响
    "https://news.cctv.com/2026/09/16/ARTILuEhOXx67xS9F0TfqEw9260916.shtml",   # 此行间100秒
    # 同事件重复（王毅伊朗，留央视版）
    "https://www.zaobao.com/news/china/story20260916-9685671",
    "https://www.zaobao.com/news/china/story20260916-9687605",                 # 学者分析稿
    "https://www.zaobao.com/news/china/story20260917-9688875",                 # 王毅中巴（同[13]）
    # 数据栏目体 / 8月经济同源
    "https://news.cctv.com/2026/09/16/ARTIcYsQ7pM2JHvrWfodtaOU260916.shtml",   # 权威数读
    "https://news.cctv.com/2026/09/16/ARTIj8ZUFAIEoyuj0mKAMdzK260916.shtml",   # 数说中国经济8月报
    "https://news.cctv.com/2026/09/16/ARTIOEuxwNYm8TDC0rBrRIUR260916.shtml",   # 八月份经济（9-16版已收）
    "https://news.cctv.com/2026/09/16/ARTIwV7qjtQfgguyGuOyAVia260916.shtml",   # 权威解读前8月
    # 体育/社会/地方/台湾
    "https://www.zaobao.com/news/china/story20260917-9688570",                 # 亚运旗手
    "https://www.zaobao.com/news/china/story20260917-9688781",                 # 拉萨代市长
    "https://www.zaobao.com/news/china/story20260916-9687153",                 # 医科大坠楼
    "https://www.zaobao.com/news/china/story20260916-9686048",                 # 台湾设办事处
    "https://news.cctv.com/2026/09/16/ARTILs7HK4UyjnpKfkRPA0Qs260916.shtml",   # 海南省级拨款
    "https://www.zaobao.com/news/china/story20260916-9687772",                 # 广州公交外放
    # 跨日重复：电子信息制造业十五五规划（9-15版已收）
    "http://paper.people.com.cn/rmrb/pc/content/202609/17/content_30181521.html",
    # 跨日重复：香港首个五年规划（9-16版已收）4 稿
    "https://www.zaobao.com/news/china/story20260916-9687130",
    "https://news.cctv.com/2026/09/16/ARTIGLvQGhCyHwa8GLRIzDTr260916.shtml",
    "http://paper.people.com.cn/rmrb/pc/content/202609/17/content_30181541.html",
    "https://news.cctv.com/2026/09/16/ARTIRzpWLDCqa3klGIYenhUo260916.shtml",
    # 涉企行政执法（并入 S1 国新办发布会综合条目）
    "https://www.zaobao.com/news/china/story20260916-9686320",
    # 个人叙事 / 评论 / 故事化 / 栏目体
    "http://paper.people.com.cn/rmrb/pc/content/202609/17/content_30181518.html",  # 产业里的年轻人
    "http://paper.people.com.cn/rmrb/pc/content/202609/17/content_30181519.html",  # 子夜走笔
    "https://news.cctv.com/2026/09/16/ARTIMne8ShcRhvbsPuJ1KzUg260916.shtml",   # 徐霞客AI
    "https://news.cctv.com/2026/09/16/ARTI3rFLrLIQTHwsS0UaS6JJ260916.shtml",   # 新思想引领新征程
    "https://news.cctv.com/2026/09/16/ARTIyV3peQllLIoCjW9as5ld260916.shtml",   # 小羽绒
    "https://news.cctv.com/2026/09/16/ARTI0Q4wz3mRnih43Pi3WQoK260916.shtml",   # 评论：骨架
    "https://news.cctv.com/2026/09/16/ARTI740lT20soOezGjfLBN3z260916.shtml",   # 高技术制造业综述
    "https://news.cctv.com/2026/09/16/ARTIddGU0IfhvcrgvjIHSuN5260916.shtml",   # 中国东盟庆祝活动软稿
    # 跨版面 AI 线（数字能源/AI 用电）
    "https://news.cctv.com/2026/09/16/ARTIlpLCA9E3Fi7dYZKtvZ5T260916.shtml",
]

del_set = set(DEL_URLS)
kept, removed = [], []
for it in items:
    if it.get("url") in del_set:
        removed.append(it)
    else:
        kept.append(it)
print(f"删除 {len(removed)} 条，保留 {len(kept)} 条")
missing = del_set - {it.get("url") for it in removed}
if missing:
    print("⚠️ 未命中的删除 URL:", missing)

# ---------- 2. 修正 ----------
def clean(txt):
    if not txt:
        return ""
    t = (txt.replace("&nbsp;", " ").replace("&mdash;", "—").replace("&ndash;", "–")
         .replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
         .replace("&ldquo;", "“").replace("&rdquo;", "”"))
    return re.sub(r"\s+", " ", t).strip()

def trim(txt, n=163):
    t = clean(txt)
    if len(t) <= n:
        return t
    cut = t[:n]
    for sep in ["。", "；", "，", "、"]:
        idx = cut.rfind(sep)
        if idx > n * 0.55:
            return cut[:idx + 1]
    return cut.rstrip("，、；") + "…"

FIX = {
    # 丁薛祥出席平陆运河通航仪式 → gov.cn 原文
    "https://tv.cctv.com/2026/09/16/VIDE1BoFXIqRQOrxt5UedePq260916.shtml": {
        "url": "https://www.gov.cn/yaowen/liebiao/202609/content_7081291.htm",
        "source": "中国政府网·要闻",
        "summary": "9月16日上午，中共中央政治局常委、国务院副总理丁薛祥在广西钦州出席平陆运河通航仪式。10时25分，丁薛祥宣布平陆运河通航。丁薛祥表示，习近平总书记高度重视平陆运河建设，要求打造优质工程、绿色工程、廉洁工程；要以运河建成通航为契机，高水平打造北部湾国际门户港，推动西部地区扩大开放。他还登船巡航考察运河航道运行、沿岸生态环境保护等情况，指出平陆运河是西部陆海新通道的骨干工程，要充分发挥陆海统筹、内外联动优势。",
    },
    # 丁薛祥将出席东博会开幕式 → 外交部外事日程原文
    "https://tv.cctv.com/2026/09/16/VIDEO1jCUcoRWvJjSUgpJmDb260916.shtml": {
        "url": "https://www.mfa.gov.cn/web/wjdt_674879/wsrc_674883/202609/t20260916_12023478.shtml",
        "source": "外交部",
        "summary": "外交部发言人宣布：中共中央政治局常委、国务院副总理丁薛祥将于9月17日出席在广西南宁举行的第23届中国—东盟博览会暨中国—东盟商务与投资峰会开幕式并致辞。缅甸副总统纽梭，越共中央政治局委员、政府常务副总理范家肃，老挝党中央政治局委员、政府常务副总理沙伦赛等外国领导人和高级官员以及东盟秘书长高金洪等将出席开幕式。今年是中国—东盟建立全面战略伙伴关系5周年，本届东博会主题为“共享3.0机遇，共创美好生活”。",
    },
    # 外交部记者会：死链修复 + 去导航残留 + 实录要点
    "https://www.mfa.gov.cn/web/wjdt_674879/202609/t20260916_12023724.shtml": {
        "url": "https://www.mfa.gov.cn/web/fyrbt_673021/jzhsl_673025/202609/t20260916_12023724.shtml",
        "title": "2026年9月16日外交部发言人郭嘉昆主持例行记者会",
        "summary": "郭嘉昆宣布丁薛祥将于9月17日出席第23届中国—东盟博览会暨中国—东盟商务与投资峰会开幕式并致辞。就日本二战受害劳工后代起诉日企，敦促日方正视历史、反省罪责，妥善处理历史遗留问题；就欧洲电信企业联署公开信反对欧盟《网络安全法案》修订案，指出保护主义换不来竞争力，希望欧盟倾听理性声音、避免歧视性限制措施；就台湾当局筹划在菲律宾宿务设“办事处”，强调民进党当局搞“外交突破”注定失败，并敦促菲方恪守一个中国原则。",
    },
    # 比亚迪随习近平访美（联合早报）
    "https://www.zaobao.com/news/china/story20260917-9688558": {
        "summary": "据联合早报9月17日报道，中国据悉正考虑让比亚迪加入随国家主席习近平访美的企业高管代表团。报道称此举反映在中美经贸摩擦背景下，新能源汽车与绿色产业合作成为双方关注议题之一。相关安排尚待官方确认。",
    },
    # 王毅同伊朗外长阿拉格齐会谈（央视）
    "https://news.cctv.com/2026/09/16/ARTI5M2UCupwAlkWkQR5Zd46260916.shtml": {
        "summary": "中共中央政治局委员、外交部长王毅9月16日在北京同伊朗外长阿拉格齐举行会谈。王毅表示，中方不希望地区紧张局势向也门和红海方向外溢，主张通过对话协商解决分歧，维护地区和平稳定。双方还就中伊关系及共同关心的国际和地区问题交换意见。",
    },
    # 张升民会见越南副总理兼国防部长
    "http://paper.people.com.cn/rmrb/pc/content/202609/17/content_30181529.html": {
        "summary": "中央军委副主席张升民9月16日在京会见出席第十三届北京香山论坛的越南副总理兼国防部长潘文江。张升民说，中越两军要围绕落实两党两国最高领导人重要共识，坚持从战略高度看待和处理两国关系，加强边防、海上等各层级交流合作，共同维护地区和平稳定。潘文江表示，越方愿同中方深化防务安全合作，推动越中命运共同体建设不断走深走实。",
    },
    # 王毅会见巴西总统首席特别顾问阿莫林
    "http://paper.people.com.cn/rmrb/pc/content/202609/17/content_30181528.html": {
        "summary": "中共中央政治局委员、中央外办主任王毅9月16日在北京会见巴西总统首席特别顾问阿莫林。王毅转达习近平主席对卢拉总统的亲切问候，表示在两国元首战略引领下，中巴关系保持良好发展势头，中方欢迎巴方加入世界人工智能合作组织，愿同巴方加强战略协作，带动全球南方实现联合自强。阿莫林表示，巴中关系已超越双边范畴，愿同中方深化各领域务实合作，共同落实两国元首共识。",
    },
}

fixed = 0
for it in kept:
    f = FIX.get(it.get("url"))
    if not f:
        continue
    for k, v in f.items():
        it[k] = v
    fixed += 1
print(f"修正 {fixed} 条")

# 全量清理 HTML 实体 + 收敛摘要长度
for it in kept:
    it["title"] = clean(it.get("title"))
    it["summary"] = trim(it.get("summary"))
    it["source"] = clean(it.get("source"))
    it.setdefault("keywords", [])
    if not it["summary"]:
        print("⚠️ 空摘要:", it["title"])

# ---------- 3. 补录 ----------
ADD = [
    {
        "title": "国新办举行“开局起步‘十五五’”系列主题新闻发布会 介绍推进全面依法治国任务落实和司法行政工作",
        "url": "https://www.xinhuanet.com/legal/20260916/ae969f639a32499092eb392bd972795f/c.html",
        "date": "2026-09-16",
        "source": "新华社",
        "category": "重要会议",
        "priority_score": 88,
        "is_summit_level": False,
        "summary": "9月16日国新办举行发布会，司法部介绍“十五五”推进全面依法治国任务落实和司法行政工作。今年以来司法部已审查完成37件立法项目，金融法、道路交通安全法等提请全国人大常委会审议；正牵头起草全国统一大市场建设条例。去年以来牵头开展规范涉企行政执法专项行动，全国查纠涉企执法突出问题案件9万多件，为企业挽回经济损失近310亿元，已转入常态化推进阶段。（综合新华社、光明日报、中央纪委国家监委网站、央视《新闻联播》报道）",
        "collectedAt": "2026-09-17 09:35:00",
    },
    {
        "title": "空客天津第二条A320总装线交付首架飞机 由中国东方航空接收运营",
        "url": "http://www.caacnews.com.cn/1/6/202609/t20260916_1397318.html",
        "date": "2026-09-16",
        "source": "中国民航网",
        "category": "经贸动向",
        "priority_score": 85,
        "is_summit_level": False,
        "summary": "9月16日，空中客车天津A320系列飞机第二条总装线完成总装的首架A320neo飞机顺利交付，由中国东方航空接收运营。该总装线2025年10月投产，标志天津进入空客单通道飞机双线运营阶段。空客在华首条总装线2008年投运，已累计交付超800架A320系列飞机；目前空客A320系列全球共10条总装线，其中2条位于中国。",
        "collectedAt": "2026-09-17 09:35:00",
    },
    {
        "title": "亚太经合组织（APEC）青年创业者大会在杭州开幕",
        "url": "https://www.news.cn/20260916/3982490debb44588b650f2dcf9186815/c.html",
        "date": "2026-09-16",
        "source": "新华社",
        "category": "部委动态",
        "priority_score": 85,
        "is_summit_level": False,
        "summary": "9月16日，亚太经合组织（APEC）青年创业者大会在杭州开幕，来自APEC经济体的青年创业者、投资人及各方代表约200人出席，围绕人工智能、轻创业、数字贸易等议题交流研讨。大会以“创业驱动，青年创变：共塑普惠繁荣亚太”为主题，是中国作为2026年APEC东道主推动举办的青年领域特色活动，由中国人民对外友好协会、浙江省人民政府主办。",
        "collectedAt": "2026-09-17 09:35:00",
    },
]

existing_urls = {it.get("url") for it in kept}
for a in ADD:
    if a["url"] in existing_urls:
        print("⚠️ 补录重复跳过:", a["title"][:30])
        continue
    kept.append(a)
print(f"补录 {len(ADD)} 条")

# ---------- 4. 排序（分数降序，同分按类别顺序） ----------
CAT_ORDER = {"元首动态": 0, "高层动态": 1, "重要会议": 2, "人事任免": 3,
             "部委动态": 4, "政策发布": 5, "经贸动向": 6}
kept.sort(key=lambda x: (-x.get("priority_score", 0), CAT_ORDER.get(x.get("category"), 9)))
data["archive"][TODAY] = kept
data["todayCount"] = len(kept)

# ---------- 5. 统计 ----------
dates = data.get("dates", [])
total = sum(len(data["archive"].get(d, [])) for d in dates)
data["stats"] = {
    "totalArticles": total,
    "dateCount": len(dates),
    "latestDate": TODAY,
    "summitCount": len(kept),
}
data["lastUpdated"] = datetime.now(TZ).strftime("%Y-%m-%d %H:%M")

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n== 最终 {TODAY}：{before} → {len(kept)} 条 ==")
cats = {}
for it in kept:
    cats[it["category"]] = cats.get(it["category"], 0) + 1
print("分类分布:", cats)
hi = sum(1 for it in kept if it.get("priority_score", 0) >= 85)
print(f"≥85 分: {hi}/{len(kept)} = {hi/len(kept)*100:.0f}%")
print(f"摘要完整: {sum(1 for it in kept if it.get('summary'))}/{len(kept)}")
print(f"最长摘要: {max(len(it.get('summary','')) for it in kept)} 字")
