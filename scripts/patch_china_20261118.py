# -*- coding: utf-8 -*-
import json
P = "data/china-news.json"
TODAY = "2026-11-18"
d = json.load(open(P, encoding="utf-8"))
arr = d["archive"][TODAY]

def find(prefix):
    for it in arr:
        if it["title"].startswith(prefix):
            return it
    print("MISS:", prefix); return None

# 秘鲁会见：改挂 gov.cn 真链 7086391
p = find("习近平会见秘鲁总统")
p.update(url="https://www.gov.cn/yaowen/liebiao/202611/content_7086391.htm",
         source="中国政府网·要闻",
         summary="11月17日下午，国家主席习近平在深圳会见来华出席亚太经合组织领导人非正式会议的秘鲁总统藤森庆子。习近平指出，今年是中秘建交55周年，中国已连续12年成为秘鲁最大贸易伙伴和最大出口目的地国，中秘自贸协定升级议定书两周前正式生效，钱凯港有力促进了亚洲和拉美经贸合作。习近平提出密切友好交往、加强战略对接、促进人文交流、加强多边协作四方面工作，表示愿同秘方挖掘新能源、人工智能等新兴合作潜力。藤森庆子表示秘鲁坚定恪守一个中国原则，欢迎更多中资企业赴秘投资兴业，感谢中方支持秘鲁应对厄尔尼诺挑战。")

# zaobao 秘鲁援助稿：删除（与上条同事件，属转述）
arr = [it for it in arr if not it["title"].startswith("习近平见秘鲁总统 承诺援助")]

# 删除人民日报 11-18 与 11-17 谌贻琴重复稿
arr = [it for it in arr if not it["title"].startswith("锚定全年发展主要目标任务")]

# zaobao 司法稿：删除（与人民法院重要指示同事件）
arr = [it for it in arr if not it["title"].startswith("习近平：深化改革并加快建设公正高效司法制度")]

# 记者会：改真链并写摘要
f = find("2026年11月17日外交部发言人郭嘉昆主持例行记者会")
if f:
    f["title"] = "外交部例行记者会：回应美半导体出口管制、中加经贸成果、免签政策等"
    f["summary"] = "11月17日，外交部发言人郭嘉昆主持例行记者会，共回答记者提问十余个。针对美方11月16日发布限制远程获取先进半导体措施，发言人表示中方强烈不满、坚决反对，若美方一意孤行将采取必要措施维护自身正当权益；就中加经贸磋商成果，发言人表示这体现双方通过对话协商解决分歧的积极意愿，中方愿同加方共同推动双边经贸关系健康稳定发展；关于部分国家对中国公民免签政策年底到期，发言人表示中方将继续本着互惠原则为人员往来提供便利。"

# 商务部再生资源：分类回部委动态（政策原文+发布会）
f = find("商务部等9部门深入推进再生资源回收体系建设")
if f:
    f["category"] = "政策发布"

# 西部陆海新通道指数降为 85（部委统计类）
f = find("连续6年稳步上行")
if f:
    f["priority_score"] = 85
    f["category"] = "经贸动向"

arr.sort(key=lambda x: -x["priority_score"])
d["archive"][TODAY] = arr
d["today"] = arr
d["todayCount"] = len(arr)
d["lastUpdated"] = "2026-11-18 10:35"
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("最终:", len(arr))
from collections import Counter
print(Counter(i["category"] for i in arr))
for i, it in enumerate(arr, 1):
    print(i, it["priority_score"], it["category"], it["source"], "|", it["title"][:55], "| sum", len(it["summary"]))
