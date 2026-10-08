#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国内看板 2026-10-08 后处理（LLM 质量后处理）
初抓 15 条 → 定稿 7 条（全部重建；初抓 15 条全部剔除，0 条保留）

背景：自动化自 2026-09-28 后未执行（国庆假期），本次为节后首跑，
      V2.11 窗口 = date ∈ {2026-10-07, 2026-10-08}，9-29~10-06 内容按规则不回收。

删 15（全部初抓）：
  · 元首动态 4 全删 —— 习近平文化思想理论综述/述评 2 + 央视「学习·故事」栏目体 1 +
    人民日报「大道之行」外方反响栏目体 1（均为理论宣传产品，非事实性元首动态）
  · 假日综述软稿 4 —— 央视「假日跨境贸易火热」「出行热 体验丰 门市旺」+ 人民日报「港口繁忙」
    「一增一降里的新能源汽车充电新趋势（新场景里看活力）」
  · 跨版面归属 2 —— 英国对华二氧化钛反倾销建议（国际线经贸）· 蔡崇信吁欧洲加码算力（AI 线）
  · 中国香港地方政治 1 —— 香港选委会选举提名
  · 署名评论 1 —— 沈泽玮（联合早报）
  · 社会琐事 1 —— 大学生新疆徒步失联
  · 超窗口（原始发布日 < 10-07）1 —— 新型电池产业「十五五」规划（9-28 印发）
  · 重复/超窗口数据稿 1 —— 电力市场交易电量 19.2%（国家能源局 9-22 发布）

补录 7（全部 curl 200 验证；date ∈ {10-07, 10-08}）：
  1. 帕特鲁舍夫将访华（外交部外事日程 10-07）高层动态 95
  2. 9月末外汇储备 34003 亿美元 + 央行连续 23 个月增持黄金（综合条目）经贸 85
  3. 中老铁路累计进出口货值突破 1000 亿元（昆明海关 10-07）经贸 85
  4. 我国科学家率先研制成功核光钟（《自然》10-07 在线）部委 85
  5. 巴彦油田日产原油首破 5000 吨（中国石油 10-07）经贸 85
  6. 国庆假期全国社会治安秩序良好（公安部 10-07）部委 85
  7. 两部门印发《医疗康复护理扩容提升工程实施方案》（10-08 新华社）政策 80

幂等守卫：若今日版面已含补录标题则中止。
"""
import json, shutil, sys, os, html, re
from collections import Counter

BASE = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50"
JSON = os.path.join(BASE, "data/china-news.json")
TODAY = "2026-10-08"

shutil.copy(JSON, "/tmp/china-news-1008-pre-postprocess.json")

d = json.load(open(JSON, encoding="utf-8"))
cur = d["archive"][TODAY]

# ---- 幂等守卫 ----
GUARD = "帕特鲁舍夫将访华"
if any(GUARD in (a.get("title") or "") for a in cur):
    print("!! 今日版面已含补录内容，脚本已执行过，中止（避免重复追加）")
    sys.exit(1)
print(f"初抓今日 {len(cur)} 条 → 开始重建定稿")


def A(cat, score, date, source, title, url, summary, **kw):
    o = {
        "title": title.strip(),
        "url": url.strip(),
        "source": source.strip(),
        "date": date,
        "category": cat,
        "priority_score": score,
        "is_summit_level": False,
        "summary": summary.strip(),
        "collectedAt": f"{TODAY} 09:40:00",
    }
    o.update(kw)
    return o


final = []

# ---------- 1. 高层动态 95 ----------
final.append(A(
    "高层动态", 95, "2026-10-07", "外交部",
    "俄罗斯总统助理、海事委员会主席帕特鲁舍夫将访华",
    "https://www.mfa.gov.cn/web/wjdt_674879/wsrc_674883/202610/t20261007_12035918.shtml",
    "外交部发言人10月7日宣布：俄罗斯总统助理、海事委员会主席帕特鲁舍夫将于10月8日至13日访问中国，中共中央政治局委员、中央外办主任王毅将与其会谈交流。帕特鲁舍夫同时兼任俄罗斯海事委员会主席，此次访华是节后中俄高层交往的又一项安排。",
))

# ---------- 2. 经贸动向 85（综合条目：外汇储备 + 黄金储备，同一「9月末官方储备资产」发布周期） ----------
final.append(A(
    "经贸动向", 85, "2026-10-07", "国家外汇管理局·中国人民银行（综合）",
    "9月末我国外汇储备3.40万亿美元 央行连续第23个月增持黄金",
    "https://www.gov.cn/lianbo/202610/content_7082669.htm",
    "国家外汇管理局10月7日公布，截至2026年9月末，我国外汇储备规模为34003亿美元，较8月末下降381亿美元、降幅1.11%。国家外汇局表示，9月受全球宏观经济环境、主要经济体货币政策等因素影响，美元指数上涨2.0%至101.5，全球主要金融资产价格总体下跌，汇率折算和资产价格变化等因素综合作用导致当月外汇储备规模下降；我国经济运行总体平稳、动能向新、结构向优，有利于外汇储备规模保持基本稳定。同日中国人民银行数据显示，9月末黄金储备为7747万盎司，环比增加74万盎司，高于8月单月增持的65万盎司，为连续第23个月增持黄金。",
))

# ---------- 3. 经贸动向 85（联播快讯档漏采类型：通道运量里程碑） ----------
final.append(A(
    "经贸动向", 85, "2026-10-07", "央视新闻",
    "中老铁路累计进出口货值突破1000亿元",
    "https://ysxw.cctv.cn/video.html?toc_style_id=video_default&t=1791372624771&item_id=8759287317624858823&channelId=1117",
    "据昆明海关10月7日消息，中老铁路自开通运营以来，已运送进出口货物超2077万吨，货值超1004亿元，进出口规模年均增长超24%，辐射19个国家和地区，进出口品类达3900余种。中老铁路是共建“一带一路”标志性工程，客货运输持续增长带动中国与东盟跨境贸易结构向新动能转变。",
))

# ---------- 4. 部委动态 85（重大原创科技突破） ----------
final.append(A(
    "部委动态", 85, "2026-10-07", "新华社",
    "我国科学家在国际上率先研制成功核光钟",
    "https://my-h5news.app.xinhuanet.com/h5/article.html?articleId=2026100765ab398f85b748e1a5965c8bff08f5c2",
    "新华社北京10月7日电，清华大学物理系丁世谦团队利用自主研制的148纳米连续波真空紫外激光以及与合作团队共同研制的掺钍-229氟化钙晶体，在国际上率先研制出核光钟并实现稳定运行，将量子精密测量由电子跃迁拓展至原子核跃迁，相关成果7日晚在线发表于国际权威期刊《自然》。团队将激光频率稳定锁定至核跃迁，实现核光钟秒级稳定度优于同期欧洲团队接近一个数量级，性能国际领先，且单次晶体生长所用核素仅为欧洲团队的二百分之一。核光钟有望成为继原子微波钟、原子光钟之后的新一代时间频率基准，固态核光钟具备小型化、工程化优势，未来有望为卫星导航、深空探测提供高精度时间频率基准，并为基础物理规律检验提供新的精密探测平台。",
))

# ---------- 5. 经贸动向 85（能源增储上产里程碑） ----------
final.append(A(
    "经贸动向", 85, "2026-10-07", "央视网",
    "内蒙古河套盆地巴彦油田日产原油首次突破5000吨",
    "https://news.cctv.cn/2026/10/07/ARTI38YzuQoewEtg0fSEPxSi261007.shtml",
    "中国石油10月7日披露，位于内蒙古河套盆地的巴彦油田日产原油达到5080吨，首次突破5000吨大关，创历史新高，标志华北油田新区增储上产迈上新台阶。巴彦油田主力油藏平均埋深超过5000米，是我国埋藏最深的整装陆相碎屑岩油藏，自2018年钻获首口高产工业油流井以来，先后落实两个亿吨级整装优质储量，建成内蒙古西部首个年产百万吨油田。截至9月底，华北油田今年原油产量达386万吨，其中巴彦油田产量同比增长14%，日产水平占华北油田日产量比重已近三分之一。",
))

# ---------- 6. 部委动态 85（公安部假期安保通报） ----------
final.append(A(
    "部委动态", 85, "2026-10-07", "新华社（公安部）",
    "国庆假期全国社会治安秩序良好 刑事警情同比下降23.7%",
    "https://www.xinhuanet.com/politics/20261007/b21f4c61653f430887269bc4d6927f00/c.html",
    "新华社北京10月7日电，记者从公安部获悉，截至10月7日16时，国庆期间全国社会治安秩序良好，刑事、治安警情同比分别下降23.7%、7%，2700余场大型活动安全顺利，全国道路交通总体平稳有序，旅游景区秩序井然。假期期间各地公安机关日均投入社会面巡控警力42万人次，加大对电信网络诈骗和“盗抢骗”“黄赌毒”等节日期间易发违法犯罪的打击整治力度；公安交管部门日均投入警力18万人次，严查“三超一疲劳”、酒驾醉驾等交通违法行为，确保4500余家重点景区秩序良好。",
))

# ---------- 7. 政策发布 80（节后首日新出台政策） ----------
final.append(A(
    "政策发布", 80, "2026-10-08", "国家卫生健康委·国家发展改革委",
    "两部门印发《医疗康复护理扩容提升工程实施方案》",
    "https://ysxw.cctv.cn/article.html?item_id=15550525119445866190",
    "经国务院批复同意（国函〔2026〕99号），国家卫生健康委、国家发展改革委近日联合印发《医疗康复护理扩容提升工程实施方案》（国卫规划发〔2026〕24号）。《方案》以扩容医疗康复护理资源、提升服务能力水平为着力点，提出6部分13项任务举措，聚焦“扩容、提质、均衡、连续”，坚持尽力而为、量力而行，以基层为重点统筹增加康复护理资源供给。工作目标是到2030年基本建成功能完备、上下联动、中西医结合、高效可及的康复护理服务体系，力争每千人口康复护理床位数达0.48张左右，每万人口康复医师达0.7人、康复治疗师达1.6人，人口较多、老龄化程度较深的地市至少设立1所公立康复医院和护理院。《方案》同时提出加快脑机接口、具身智能、仿生驱动等前沿技术布局，推进康复护理服务标准化规范化与医保支付方式改革、完善多元支付体系，并鼓励有条件的地方在医保支付、人才培养激励等方面加大改革力度。",
))

# ================= 校验 =================
errs = []
if not (5 <= len(final) <= 30):
    errs.append(f"条数越界 {len(final)}")
for a in final:
    for f in ("source", "date", "url", "title", "category", "summary"):
        if not a.get(f):
            errs.append(f"缺字段 {f}: {a.get('title')}")
    if len(a["title"]) < 8:
        errs.append(f"标题过短: {a['title']}")
    if a["date"] not in ("2026-10-07", "2026-10-08"):
        errs.append(f"date 越界: {a['title']} {a['date']}")
    if not a["collectedAt"].startswith(TODAY):
        errs.append(f"collectedAt 越界: {a['title']}")
    if re.search(r"\[官方信源\]|发布：", a["summary"]):
        errs.append(f"模板摘要: {a['title']}")
    if re.search(r"&nbsp;|&ldquo;|当前位置：首页", a["summary"]):
        errs.append(f"实体残留: {a['title']}")
    if len(a["summary"]) < 40:
        errs.append(f"摘要过短: {a['title']} {len(a['summary'])}")
    if a["category"] not in ("元首动态", "高层动态", "重要会议", "人事任免",
                             "部委动态", "政策发布", "经贸动向"):
        errs.append(f"分类非法: {a['title']} {a['category']}")
    if re.search(r"人民论坛|人民时评|评论员观察|时习之|记者手记|微镜头|微视频|vlog", a["title"]):
        errs.append(f"禁用栏目: {a['title']}")

titles = [a["title"] for a in final]
if len(set(titles)) != len(titles):
    errs.append("今日版面标题重复")

if errs:
    print("!! 校验失败：")
    for e in errs:
        print("  -", e)
    sys.exit(1)

# ================= 写入 =================
for day, arts in d["archive"].items():
    for a in arts:
        if a.get("summary"):
            a["summary"] = re.sub(r"[ \t]+", " ", html.unescape(a["summary"])).strip()
        if a.get("title"):
            a["title"] = html.unescape(a["title"]).strip()

d["archive"][TODAY] = final
d["today"] = TODAY
d["todayCount"] = len(final)
d["dates"] = sorted(d["archive"].keys(), reverse=True)[:7]
d["stats"] = {
    "totalArticles": sum(len(v) for k, v in d["archive"].items() if k in d["dates"]),
    "dateCount": len(d["dates"]),
    "latestDate": d["dates"][0],
    "summitCount": sum(1 for k in d["dates"] for a in d["archive"][k]
                       if a.get("is_summit_level")),
}
d["lastUpdated"] = "2026-10-08 09:40"

json.dump(d, open(JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print(f"✅ 定稿今日 {len(final)} 条（初抓 {len(cur)} 条 → 重建 {len(final)} 条）")
print("   分类分布:", dict(Counter(a["category"] for a in final)))
print("   ≥85 分:", sum(1 for a in final if a["priority_score"] >= 85), "/", len(final))
print("   总分档:", dict(Counter(a["priority_score"] for a in final)))
print("   dates:", d["dates"], "| todayCount:", d["todayCount"], "| total:", d["stats"]["totalArticles"])
