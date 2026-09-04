#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内新闻 2026-09-04 LLM 质量后处理（自动化任务内嵌，仿 9-03 postprocess 模式）
- 去重/剔除 19 条：发布会不会议子集、同稿多形态、评论栏目、特写/蹲点、外方主体分流、地方琐事、程序性通知
- 分类修正 1 条：人工智能中小企业创业支持计划 经贸72 → 部委85（工信部行动，产业技术归部委）
- 补真实摘要 4 条（均来自页面真实内容/官方实录核实）
- 补录 1 条：商务部就法国"反超快时尚"法表态（9-3 例行发布会实录核实，重大经贸反制）
"""
import json, sys

JSON_PATH = "data/china-news.json"
DATE = "2026-09-04"

d = json.load(open(JSON_PATH, encoding="utf-8"))
items = d["archive"][DATE]
assert len(items) == 40, f"今日条目数异常: {len(items)}"

def find_today(sub, field="url"):
    """按子串在今日条目中定位，返回 index；要求唯一"""
    idxs = [i for i, it in enumerate(items) if sub in str(it.get(field, ""))]
    assert len(idxs) == 1, f"定位失败/不唯一: {sub} -> {idxs}"
    return idxs[0]

# ---------- 1) URL 精确删除（发布会不会议子集/死链重复） ----------
del_urls = [
    "t20260903_12015595",             # 外交部·王毅谈：页面已失效(302→不存在)，与 gov.cn 圆满成功通稿重复
    "ARTIKxjnW3zkx6l9qJP03msz260903", # 央视·王毅谈：与 gov.cn 要闻通稿重复（gov.cn 优先）
    "story20260903-9623160",          # 联合早报·韩国光州双年展：9-3 记者会会后问答子集
    "ARTIOhWFvAWJaqAl03f31Poq260903", # 央视·日本军国主义：9-3 记者会日本问答子集
]
for u in del_urls:
    idx = find_today(u)
    items.pop(idx)

# ---------- 2) 标题关键词删除（低质/重复/分流；要求唯一命中） ----------
del_titles = [
    "家长班级群",                  # 保定卫健委 地方琐事
    "图表：2026年前7个月",          # gov.cn 图表 = 商务部服贸司发布数据重复
    "换届及征集委员",               # 网信办 委员征集通知 = 程序性通知
    "十部门印发",                  # 央视版规划 = gov.cn 要闻版重复
    "按病种付费3.0版",             # 央视·解读版 = 同病同付解读重复（留 #基层病种同病同付）
    "“激活”一条街",               # 央视 体育产业特写（=国新办发布会角度稿，与 #33 重复）
    "下午察",                     # 联合早报 评论栏目
    "今年已发布新兴产业国家标准",    # 人民日报 数据综述
    "德国社民党",                 # 外方主体对华政策动作、无中方主场 → 国际版覆盖
    "一杯咖啡",                   # 央视 消费软特写
    "蓝色粮仓",                   # 央视 "第一网鲜" 蹲点故事化
    "美学者：中国",               # 联合早报 学者观点评论稿
    "航空货运“新”观察",           # 央视 观察专栏
    "观察 | 新赛道",              # 央视 观察专栏
    "高盛：人民币料",             # 联合早报 外方投行预测观点（无中方主场）
]
for t in del_titles:
    idx = find_today(t, "title")
    items.pop(idx)

print(f"删除后剩余: {len(items)}")

# ---------- 3) 分类修正 ----------
i = find_today("人工智能中小企业创业支持计划", "title")
assert items[i]["category"] == "经贸动向", items[i]["category"]
items[i]["category"] = "部委动态"      # 工信部启动的产业计划 → 部委动态（V5.8 产业技术归部委）
items[i]["priority_score"] = 85
print("分类修正: 人工智能中小企业创业支持计划 → 部委动态85")

# ---------- 4) 补真实摘要 ----------
def set_summary(sub, field, text):
    idx = find_today(sub, field)
    items[idx]["summary"] = text
    print(f"补摘要: {items[idx]['title'][:36]}")

set_summary("美贸易代表", "title",
    "美国贸易代表格里尔9月3日透露，习近平主席本月访美期间（预计9月24日访问华盛顿），美中预计将宣布农业贸易及相关非关税壁垒方面的安排，以促进美国农产品对华销售。格里尔称，美方无意与中国达成庞大而全面的贸易协议，而是希望管控好双边关系。（联合早报，据路透社）")
set_summary("t20260903_12015775", "url",
    "9月3日外交部例行记者会上，发言人郭嘉昆宣布墨西哥外长贝拉斯科将于9月6日至7日访华；介绍习近平主席访埃成果，中埃发表深化全面战略伙伴关系联合声明；通报对尼泊尔第三批紧急援助物资已启运；正告日本右翼势力，坚决遏止日本“新型军国主义”滋长成势；会后回应韩国光州双年展涉台错误做法，表示中方已向韩方提出严正交涉，要求立即纠正。")
set_summary("art_5c319d06cbc3478688b14ffc3444ab25", "url",
    "2026年1-7月我国服务进出口总额44467.1亿元，同比增长8.3%。其中出口17732.3亿元，增长17.1%；进口26734.8亿元，增长3.2%。旅行和运输服务出口对整体服务出口增长的贡献率超50%；知识密集型服务出口占比过半，个人文化和娱乐服务、知识产权使用费出口增速最快。")
set_summary("t20260903_1407399", "url",
    "9月2日，国家发展改革委副主任岳修虎主持召开“六张网”重大项目协调推进机制会，研究完善政银企协作机制和项目库建设：推动各牵头部门和地方加快建设“六张网”项目库、加强与金融机构信息共享实现高效“投贷联动”，同步完善价费机制和配套政策，更好发挥政府投资撬动作用。工信部、住建部、水利部、国资委、金融监管总局、国家能源局及多家金融机构、地方发改委和企业负责同志参会。")

# ---------- 5) 补录：商务部回应法国"反超快时尚"法（9-3 例行发布会） ----------
new_item = {
    "title": "商务部：敦促法方立即停止实施“反超快时尚”法 否则将采取必要措施维护中企权益",
    "url": "https://www.mofcom.gov.cn/xwfbzt/2026/swbzklxxwfbh2026n9y3r/index.html",
    "date": "2026-09-03",
    "source": "商务部",
    "category": "部委动态",
    "priority_score": 88,   # 商务部反制/贸易壁垒类（重大）88
    "is_summit_level": False,
    "summary": "9月3日例行新闻发布会上，就法国“反超快时尚”法9月1日生效、对纺织产品征收环境罚款，商务部发言人黄玲表示强烈不满和坚决反对，指该法以“环保”“可持续”为名行双重标准之实，涉嫌违反世贸组织非歧视原则，已给相关中资企业造成重大经营损失；中方敦促法方立即停止实施该法，如法方一意孤行，中方将采取必要措施维护中资企业正当权益。",
    "collectedAt": "2026-09-04 09:25",
}
items.append(new_item)
items.sort(key=lambda x: -(x.get("priority_score") or 0))   # 与抓取排序一致（分数降序）
print(f"补录后今日条目: {len(items)}")

# ---------- 6) 统计字段同步 ----------
d["todayCount"] = len(items)
total = 0
summit = 0
for k, lst in d["archive"].items():
    total += len(lst)
    for it in lst:
        if it.get("is_summit_level") is True:
            summit += 1
d["stats"]["totalArticles"] = total
d["stats"]["summitCount"] = summit
d["lastUpdated"] = "2026-09-04 09:32"
json.dump(d, open(JSON_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"保存完成: totalArticles={total} summitCount={summit} todayCount={len(items)}")

# ---------- 7) 校验 ----------
d2 = json.load(open(JSON_PATH, encoding="utf-8"))
items2 = d2["archive"][DATE]
assert len(items2) == len(items)
assert d2["todayCount"] == len(items2)
bad = [it for it in items2 if not it.get("summary", "").strip()]
print(f"校验: 今日 {len(items2)} 条, 空摘要 {len(bad)} 条")
cats = {}
for it in items2:
    cats[it.get("category")] = cats.get(it.get("category"), 0) + 1
print("分类分布:", cats)
PY_CALL = None
