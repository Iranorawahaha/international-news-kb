#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
postprocess_china_20260916c.py — 2026-09-16 第三轮：外交部栏目复核补录

复核 mfa.gov.cn 7 个栏目后发现「领导人活动」9-15 有 1 条漏采：
  韩正出席第十三届北京香山论坛欢迎晚宴并致辞（国家副主席，高层动态 95）
其余栏目（部领导活动 9-15 王毅会见东盟秘书长 / 记者会 9-15 / 外事日程 9-15 伊朗外长访华）
均已在版面或已补录；大使任免（8-28）、政策解读（8-15）、业务动态（9-14）确无新文。
商务部 6 子栏目最新条目均为 9-14 或更早，已在历史版面覆盖 → 0 条属实。
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "china-news.json")
TODAY = "2026-09-16"
COLLECTED = "2026-09-16 12:16:20"

ADD = [
    {
        "title": "韩正出席第十三届北京香山论坛欢迎晚宴并致辞",
        "url": "https://www.mfa.gov.cn/web/wjdt_674879/gjldrhd_674881/202609/t20260915_12023027.shtml",
        "date": "2026-09-15",
        "source": "外交部",
        "category": "高层动态",
        "priority_score": 95,
        "is_summit_level": False,
        "summary": "9月15日，国家副主席韩正出席第十三届北京香山论坛欢迎晚宴并致辞。韩正表示，习近平主席提出构建人类命运共同体理念和四大全球倡议，为解决人类面临的共同问题指明了方向，和平、发展、合作、共赢的时代潮流不可阻挡。韩正提出四点建议：坚持维护联合国宪章宗旨和原则，坚持真正的多边主义，坚持通过对话协商化解分歧和争端，坚持以人为本、科技向善。中央军委副主席张升民、国防部长董军出席欢迎晚宴。",
        "collectedAt": COLLECTED,
    },
]


def main():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    arts = data["archive"][TODAY]
    existing = {(a.get("url") or "").strip().rstrip("/") for a in arts}
    n = 0
    for item in ADD:
        if item["url"].rstrip("/") in existing:
            continue
        arts.append(dict(item))
        n += 1

    arts.sort(key=lambda x: -(x.get("priority_score") or 0))
    data["archive"][TODAY] = arts
    data["todayCount"] = len(arts)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"补录 {n} 条 → 今日 {len(arts)} 条")
    print("摘要长度:", sorted(len(a.get("summary") or "") for a in arts))
    print("摘要>168:", [(a["title"][:18], len(a.get("summary") or "")) for a in arts
                     if len(a.get("summary") or "") > 168])
    sc = [a.get("priority_score") or 0 for a in arts]
    print("≥85 占比: %.0f%%  100分: %d 条" % (100.0 * sum(1 for x in sc if x >= 85) / len(sc),
                                          sum(1 for x in sc if x == 100)))
    print("分类分布:", {c: sum(1 for a in arts if a.get("category") == c)
                     for c in ["元首动态", "高层动态", "重要会议", "人事任免", "部委动态", "政策发布", "经贸动向"]})


if __name__ == "__main__":
    main()
