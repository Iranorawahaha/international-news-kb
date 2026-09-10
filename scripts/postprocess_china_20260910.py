#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
postprocess_china_20260910.py — 国内看板 2026-09-10 LLM 质量后处理

来源：refresh_china_news.sh 初抓 35 条
目标：剔除低质/重复/跨版面/栏目体，修正错误分类与 URL，补录官方漏采条目
"""
import json
import os
import sys
import shutil
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "china-news.json")
TODAY = "2026-09-10"

# ---------- 删除清单（title 前缀精确匹配）----------
DELETE_PREFIX = [
    "习近平向全国广大教师和教育工作者致以节日祝贺和诚挚问候",          # 人民日报版，与 gov.cn 版重复
    "丁薛祥：严格中国教材编审出版管理",                                # 9-9 版面已收（丁薛祥全国教材工作会议）
    "商务部新闻发言人就对美国联邦通信委员会",                          # ⚠️ 实为 2026-08-05 旧文，超出窗口
    "中国商务部：蒸馏是AI领域通行做法",                                # 联合早报版，留商务部官网原文
    "中国外交部：中美都是AI大国",                                      # 联合早报版，并入 9-9 记者会
    "商务部就美发布中国人工智能企业对美蒸馏活动相关网络安全公告答记者问",  # 央视版，留商务部官网原文
    "瑞幸咖啡拟进军台湾",                                              # 联合早报版，留央视国台办版
    "美指中企蒸馏AI模型",                                              # 联合早报版，留商务部官网原文
    "2026年铁路中秋国庆假期运输方案公布",                              # 服务性公告（新闻联播快讯级）
    "AI需求强劲 台湾8月出口",                                          # 台湾地区经济数据，非国内版面
    "一度电看江西",                                                    # 地方栏目体
    "中国服务贸易如何转型升级",                                        # 问句式评述栏目
    "中国经济底盘稳",                                                  # 综述体
    "十万卡集群将越来越多",                                            # 标题党，内容=9-7 已收《信息通信行业十五五规划》
    "广州全力推进重大产业项目建设",                                    # 地方+栏目体
    "我国加快新兴领域知识产权保护",                                    # 年会采访综述体
    "携手推进全球服务贸易开放创新合作",                                # 人民日报述评
    "系统性规范电声性能",                                              # 低价值国标发布
    "谷立言：台海若爆冲突",                                            # 美国官员涉台言论，属国际线
    "进出口双双大涨 中国外贸韧性持续释放",                              # 与前 8 月外贸 17.6% 同事件跨版面重复
    "采购周期缩短50%以上",                                              # 行业协会报告综述
    "中央统战部：未来五年引导中国民企发展新质生产力",                    # 联合早报版，改官方国新办发布会版
    "纵容子女谋取私利 内蒙古自治区党委原书记孙绍骋被双开",              # 联合早报版，改央视官方版
]

# ---------- 修正清单 ----------
# title 前缀 -> {字段: 新值}
FIX = {
    "2026年9月9日外交部发言人毛宁主持例行记者会": {
        "title": "2026年9月9日外交部发言人毛宁主持例行记者会",
        "url": "https://www.mfa.gov.cn/web/fyrbt_673021/202609/t20260909_12019125.shtml",
        "summary": ("外交部发言人毛宁9月9日主持例行记者会。就所谓中国对南方国家“抽梯子”论回应：中国从不会抽走"
                    "任何国家发展的“梯子”，而是致力于搭“梯子”，通过共建“一带一路”、零关税等政策分享市场机遇。"
                    "就美方指责深度求索、月之暗面等中国企业“窃取”美国大模型技术表示：中国人工智能发展是高水平"
                    "科技自立自强的成果，希望美方落实两国元首重要共识，不要对中国进行不实指责和抹黑；中美都是"
                    "人工智能大国，应当加强合作。就菲律宾防长涉“南海仲裁案”言论表示：菲方单方面提起仲裁是对"
                    "《联合国海洋法公约》争端解决机制的扭曲和滥用，奉劝菲方个别人停止哗众取宠、挑事生非。"),
        "category": "部委动态",
        "priority_score": 85,
    },
    "商务部新闻发言人就美发布中国人工智能企业对美蒸馏活动相关网络安全公告答记者问": {
        "title": "商务部新闻发言人就美发布中国人工智能企业对美蒸馏活动相关网络安全公告答记者问",
        "summary": ("针对美东时间9月8日美国家安全局、网络安全与基础设施安全局、联邦调查局联合发布公告，指责中国"
                    "人工智能企业对美开展“工业规模”蒸馏，商务部新闻发言人9月9日回应：美方指控于事无凭、于法无据，"
                    "是将蒸馏这一业内正常技术和商业问题政治化、工具化，并搞双重标准。蒸馏是各模型间互相学习的"
                    "通行做法，包括美企在内的全球模型企业都在使用；美企模型研发报告亦披露其大量蒸馏中国模型。"
                    "美方由安全部门发布公告，是以打击蒸馏为名行产业垄断之实，动用国家力量维护科技霸权和算力垄断。"
                    "中方坚决反对；如美方实施遏压中国人工智能企业的行动，中方必将坚决采取措施予以反制。"),
        "category": "部委动态",
        "priority_score": 88,
    },
    "国家发展改革委召开“六张网”重大项目协调推进会": {
        "summary": ("国家发展改革委党组成员、副主任岳修虎主持召开“六张网”重大项目协调推进会，研究加强要素保障"
                    "工作。会议提出，要充分发挥各级要素保障机制作用，主动加强与项目单位的对接，精准高效做好用地、"
                    "用海、环评等要素保障，共同推动“六张网”重大项目加快落地实施。国家发展改革委、财政部、自然资源部、"
                    "生态环境部、中国人民银行、国家能源局、国家数据局、国家林草局有关司局负责同志参加会议。"),
        "category": "部委动态",
        "priority_score": 85,
    },
    "蒋成华副部长出席数字贸易发展趋势和前沿论坛": {
        "summary": ("9月9日，“数字贸易发展趋势和前沿论坛”在2026年中国国际服务贸易交易会期间举行，商务部副部长"
                    "蒋成华出席并致开幕辞。蒋成华表示，中方于2023年10月同有关国家共同发布《数字经济和绿色发展"
                    "国际经贸合作框架倡议》，目前《框架》已有54个国家参与、3个国际组织支持。中国正通过实际行动"
                    "与全球南方国家分享数字和绿色发展经验，愿进一步发挥《框架》发起方积极作用，深化数字与绿色"
                    "领域国际经贸务实合作。"),
        "category": "部委动态",
        "priority_score": 85,
    },
    "国务院任免国家工作人员（2026年9月9日）": {
        "priority_score": 87,   # 中国政府网·要闻 boost（人事任免档）
        "category": "人事任免",
    },
    "与11家外资银行签约 人民币跨境支付系统进一步扩容": {
        "summary": ("9月8日，人民币跨境支付系统（CIPS）与11家外资银行直接参与者签约，首次覆盖卢旺达、土耳其、"
                    "乌兹别克斯坦等国家，人民币跨境支付系统全球服务能力进一步提升。"),
        "category": "经贸动向",
        "priority_score": 85,
    },
    "中国代表赴韩考察投资 聚焦光伏二次电池等领域": {
        "summary": ("由20余家中国光伏、二次电池、信息通信技术企业组成的投资考察团9月9日至11日访问韩国，实地考察"
                    "中韩产业合作园区“新万金产业园区”，中国商务部及驻韩使馆人员随行。考察团由中国机电产品进出口"
                    "商会副会长施永宏带队，此行是落实今年1月《关于深化韩中产业合作的谅解备忘录》、去年11月两国"
                    "首脑会谈关于激活新万金园区投资共识的后续行动；10日举行中韩商务圆桌论坛和新万金投资论坛。"),
        "category": "经贸动向",
        "priority_score": 85,
    },
}

# ---------- 补录清单 ----------
ADD = [
    {
        "title": "国新办举行“开局起步‘十五五’”发布会 介绍发展社会主义民主有关情况",
        "url": "https://news.cctv.com/2026/09/09/ARTI24pVixUw3NzAus1WOgmq260909.shtml",
        "date": "2026-09-09",
        "source": "央视新闻",
        "category": "重要会议",
        "priority_score": 88,
        "is_summit_level": False,
        "summary": ("国务院新闻办公室9月9日举行“开局起步‘十五五’”系列主题新闻发布会，中央统战部、中央社会工作部、"
                    "全国人大常委会办公厅、全国政协办公厅、国家民委有关负责人介绍“十五五”时期发展社会主义民主"
                    "有关情况。中央统战部表示将联合全国工商联开展“十五五”规划纲要专题宣讲和“创新型成长型民营企业"
                    "赋能行动”，引导民营企业因企制宜发展新质生产力；中央社会工作部将引导各方有序参与基层治理、"
                    "规范基层权责边界；全国人大将聚焦教育、就业、医疗、养老、社会保障等统筹做好立法监督；全国政协"
                    "将围绕健康中国、高水平对外开放等10项重点任务持续开展民主监督。"),
        "collectedAt": "2026-09-10 09:21:21",
    },
    {
        "title": "十四届全国人大社会建设委员会原副主任委员孙绍骋严重违纪违法被开除党籍和公职",
        "url": "https://news.cctv.com/2026/09/09/ARTIXfVdIa68YtqwGuDnUE6d260909.shtml",
        "date": "2026-09-09",
        "source": "央视新闻",
        "category": "人事任免",
        "priority_score": 87,
        "is_summit_level": False,
        "summary": ("中央纪委国家监委网站9月9日通报，经中共中央批准，对第二十届中央委员、十四届全国人大社会建设"
                    "委员会原副主任委员孙绍骋严重违纪违法问题立案审查调查。经查，孙绍骋贯彻落实党中央重大决策部署"
                    "打折扣、搞变通，对抗组织审查，搞迷信活动；违规收受礼金、出入私人会所；纵容、默许子女利用其"
                    "职务影响谋取私利，利用职权为亲属经营活动谋利；违规干预插手司法活动；利用职务便利为他人在"
                    "项目审批、工程承揽等方面谋利并非法收受巨额财物。决定给予其开除党籍、开除公职处分，终止其党的"
                    "二十大代表资格，收缴违纪违法所得，涉嫌犯罪问题移送检察机关依法审查起诉。"),
        "collectedAt": "2026-09-10 09:21:21",
    },
    {
        "title": "8月份CPI同比上涨0.8% PPI同比涨幅扩大至3.8%",
        "url": "https://www.stats.gov.cn/xxgk/jd/sjjd2020/202609/t20260909_1965261.html",
        "date": "2026-09-09",
        "source": "国家统计局",
        "category": "经贸动向",
        "priority_score": 85,
        "is_summit_level": False,
        "summary": ("国家统计局9月9日发布数据：8月份全国居民消费价格指数（CPI）环比由上月下降0.1%转为上涨0.4%，"
                    "同比涨幅回升至0.8%，涨幅比上月扩大0.3个百分点，主要受能源价格涨幅由0.6%扩大至4.1%影响；"
                    "扣除食品和能源价格的核心CPI同比涨幅回升至1.0%。受算力需求快速增长等因素影响，移动电话机、"
                    "平板电脑、数据存储设备价格分别上涨2.3%、2.1%和2.1%。工业生产者出厂价格指数（PPI）环比由上月"
                    "下降0.7%转为上涨0.4%，同比涨幅扩大至3.8%，连续6个月同比上涨。"),
        "collectedAt": "2026-09-10 09:21:21",
    },
    {
        "title": "人力资源社会保障部等部门发布第八批新职业 含11个新职业23个新工种",
        "url": "https://www.mohrss.gov.cn/SYrlzyhshbzb/dongtaixinwen/buneiyaowen/rsxw/202609/t20260909_583608.html",
        "date": "2026-09-09",
        "source": "人力资源和社会保障部",
        "category": "部委动态",
        "priority_score": 85,
        "is_summit_level": False,
        "summary": ("人力资源社会保障部等部门9月9日发布船舶岸基管理工程技术人员等11个新职业、社区工作者等23个新工种，"
                    "并调整变更农产品经纪人等6个职业（工种）信息。11个新职业包括数字孪生工程技术人员、具身智能机器人"
                    "应用技术员、工业产品数字建模师、运动数据分析师、微电网管理员、氢燃料电池制造工、电解水制氢工等，"
                    "其中数字职业5个（占45.5%）、绿色职业3个（占27.3%）。自2019年以来我国已累计发布八批共121个新职业，"
                    "发布的数字职业已达113个、绿色职业142个。"),
        "collectedAt": "2026-09-10 09:21:21",
    },
    {
        "title": "中韩自贸协定第二阶段第16轮谈判在北京举行",
        "url": "https://www.mofcom.gov.cn/syxwfb/art/2026/art_60737ac9cf37427c9ca250b790c7577c.html",
        "date": "2026-09-09",
        "source": "商务部",
        "category": "经贸动向",
        "priority_score": 85,
        "is_summit_level": False,
        "summary": ("2026年8月31日—9月4日，中韩自贸协定第二阶段第16轮谈判在北京举行。双方围绕跨境服务贸易和负面清单"
                    "市场准入等问题开展深入磋商，取得积极进展。双方同意加快推进并力争早日完成谈判，进一步提升中韩"
                    "服务投资领域开放水平，助力中韩经贸关系健康稳定发展。"),
        "collectedAt": "2026-09-10 09:21:21",
    },
    {
        "title": "四部门印发《医疗机构麻醉药品和精神药品管理规定》 11章73条10月1日起实施",
        "url": "https://app.xinhuanet.com/news/article.html?articleId=20260909705a6f0a835f4917bd785c3c8efc2cce",
        "date": "2026-09-09",
        "source": "新华网",
        "category": "政策发布",
        "priority_score": 80,
        "is_summit_level": False,
        "summary": ("国家卫生健康委、国家中医药局、国家疾控局、中央军委后勤保障部近日联合印发《医疗机构麻醉药品和"
                    "精神药品管理规定》，共11章73条，将于2026年10月1日起实施。主要修订：将适用范围由药用类麻醉药品、"
                    "第一类精神药品扩大至全部药用类麻精药品（含第二类精神药品）；细化医疗机构内部管理体系和培训考核"
                    "要求；增加知情同意规定，为未成年人开具麻精药品处方需取得监护人书面知情同意；发挥信息化在麻精"
                    "药品全流程管理中的作用。2005年发布实施的原规定同时废止。"),
        "collectedAt": "2026-09-10 09:21:21",
    },
]

# 版面内排序（与脚本抓取顺序一致）
CAT_ORDER = ["元首动态", "高层动态", "重要会议", "人事任免", "部委动态", "政策发布", "经贸动向"]


def main():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    arts = data["archive"][TODAY]
    print(f"初抓：{len(arts)} 条")

    # 1) 删除 + 修正
    kept = []
    deleted, fixed = [], []
    for a in arts:
        t = a.get("title", "")
        if any(t.startswith(p) for p in DELETE_PREFIX):
            deleted.append(t)
            continue
        for pref, patch in FIX.items():
            if t.startswith(pref):
                a.update(patch)
                fixed.append(t)
                break
        kept.append(a)

    # 2) 补录（去重：同 title[:30] 已存在则跳过）
    existing = {(x.get("title", "")[:30]) for x in kept}
    added = []
    for item in ADD:
        if item["title"][:30] in existing:
            continue
        kept.append(dict(item))
        added.append(item["title"])
        existing.add(item["title"][:30])

    # 3) 排序：分类顺序 → 分数降序
    kept.sort(key=lambda x: (CAT_ORDER.index(x["category"]) if x.get("category") in CAT_ORDER else 99,
                             -int(x.get("priority_score") or 0)))

    data["archive"][TODAY] = kept
    data["todayCount"] = len(kept)
    data["lastUpdated"] = datetime.now(TZ).strftime("%Y-%m-%d %H:%M")
    # stats 重算
    st = data.setdefault("stats", {})
    st["totalArticles"] = sum(len(v) for v in data["archive"].values())
    st["dateCount"] = len([d for d, v in data["archive"].items() if v])
    st["latestDate"] = max(data["archive"].keys())

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n删除 {len(deleted)} 条：")
    for t in deleted:
        print("  -", t[:60])
    print(f"\n修正 {len(fixed)} 条：")
    for t in fixed:
        print("  *", t[:60])
    print(f"\n补录 {len(added)} 条：")
    for t in added:
        print("  +", t[:60])
    print(f"\n最终今日 {len(kept)} 条")

    from collections import Counter
    print("分类：", dict(Counter(x["category"] for x in kept)))
    print("分数≥85：", sum(1 for x in kept if (x.get("priority_score") or 0) >= 85), "/", len(kept))
    print("无摘要：", sum(1 for x in kept if not (x.get("summary") or "").strip()))
    print("collectedAt≠今日：", sum(1 for x in kept if not str(x.get("collectedAt", "")).startswith(TODAY)))
    print("date<9-9：", sum(1 for x in kept if x.get("date", "") < "2026-09-09"))


if __name__ == "__main__":
    main()
