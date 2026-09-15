#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
postprocess_china_0915c.py — 国内看板 2026-09-15 摘要补丁（第二轮）

① 收敛 3 条仍超长的摘要（177~199 → ≤165），保持卡片行高一致
② 修复 1 条 101 字处截断的摘要（智能家居行动方案，央视 fetch 截断于"…和智能化"）
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "china-news.json")
TODAY = "2026-09-15"

PATCH = {
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081013.htm": {
        "summary": "近日，中共中央办公厅、国务院办公厅、中央军委办公厅印发《退役军人服务和保障“十五五”规划》，对“十五五”时期做好退役军人工作作出部署安排。《规划》围绕健全退役军人事务治理体系、推进退役军人高质量安置就业、提高拥军优属工作水平、提升退役军人服务保障效能等方面部署一批重点任务，并提出退役军人服务中心（站）提质增效、优抚医疗康养体系能力提升等工程项目。",
    },
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081066.htm": {
        "summary": "国务院新闻办公室9月14日举行“开局起步‘十五五’”系列主题新闻发布会，国家卫生健康委等单位介绍推动健康中国建设取得决定性进展有关情况。国家卫生健康委介绍，到2035年建成健康中国是党中央作出的战略决策，“十五五”是实现这一目标的关键时期；我国已建成世界上规模最大的医疗服务体系，90%以上的居民可在15分钟内到达最近的医疗服务点。",
    },
    "https://www.gov.cn/yaowen/liebiao/202609/content_7081052.htm": {
        "summary": "9月10日11时15分许，中国船舶集团青岛北海造船有限公司一艘外籍货轮靠港维修期间发生火灾，造成25人死亡、5人受伤。国务院成立事故调查组，由应急管理部牵头，外交部、工业和信息化部、公安部、交通运输部、国务院国资委、国家消防救援局和山东省人民政府等参加，对该起事故提级调查；9月14日下午调查组召开第一次全体会议。",
    },
    "https://news.cctv.com/2026/09/14/ARTIMZcEGPl7rI5sIdaaxYSw260914.shtml": {
        "summary": "商务部、国家发展改革委等8部门9月14日联合印发《促进智能家居消费行动方案》，落实“十五五”规划纲要关于丰富智能家居场景、支持老旧房屋适老化改造和智能化升级等要求，从扩大优质智能家居供给、完善智能家居标准体系、支持智能家居消费、畅通废旧回收服务链条、发展适老化智能家居等七个方面提出举措，推动更多智能家居产品走入百姓家庭。",
    },
}


def main():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    arts = data["archive"][TODAY]
    n = 0
    for a in arts:
        u = (a.get("url") or "").strip().rstrip("/")
        if u in PATCH:
            a.update(PATCH[u])
            n += 1
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"打补丁 {n} 条")
    print("摘要长度分布：", sorted(len(x.get("summary") or "") for x in arts))
    print("摘要>168：", [x["title"][:22] for x in arts if len(x.get("summary") or "") > 168])
    print("疑似截断（结尾无标点）：",
          [x["title"][:22] for x in arts
           if (x.get("summary") or "")[-1:] not in "。！？”）"])


if __name__ == "__main__":
    main()
