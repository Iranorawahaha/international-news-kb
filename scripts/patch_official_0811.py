#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-08-11 官方源中文化补丁：为白宫/国务院 14 条英文条目补 title_zh/summary_zh"""
import json, re

PATH = 'data/us-official.json'

TRANSLATIONS = {
    # 白宫
    "Presidential Message on National Shooting Sports Month": {
        "title_zh": "总统就全国射击运动月发表致辞",
        "summary_zh": "本月为全国射击运动月，特朗普总统在致辞中赞扬美国休闲射击与狩猎的光荣传统，强调第二修正案所保障的持枪权利。",
    },
    "Delivering Gold Standard Childhood Vaccine Recommendations for Americans": {
        "title_zh": "行政令：为美国人提供金标准儿童疫苗建议",
        "summary_zh": "特朗普总统签署行政令，要求为美国儿童提供\"金标准\"疫苗建议，下令拆分麻疹-腮腺炎-风疹（MMR）联合疫苗，此举引发美国儿科学会等医学界的强烈反对，认为其违背科学共识。",
    },
    "One Year Later, President Trump Has Delivered on Making D.C. Safe Again": {
        "title_zh": "一年后：特朗普总统兑现让华盛顿特区重归安全的承诺",
        "summary_zh": "在特朗普总统宣布哥伦比亚特区犯罪紧急状态并启动\"让特区安全美丽\"工作组一周年之际，白宫总结打击犯罪成果，称特区治安已显著改善。",
    },
    "Continuing to Protect the Meaning and Value of American Citizenship": {
        "title_zh": "行政令：继续保护美国公民身份的意义与价值",
        "summary_zh": "特朗普总统签署行政令，进一步收紧与公民身份相关的移民政策，限制在美出生儿童自动获得公民身份的途径，延续其限制非法移民的政策路线。",
    },
    "Ending Birth Tourism": {
        "title_zh": "行政令：终结\"生育旅游\"",
        "summary_zh": "特朗普总统签署行政令终止\"生育旅游\"，禁止外国人以在美生子获取公民身份为目的的旅行安排，收紧签证审核并打击相关中介行为。",
    },
    # 国务院
    "Joint Statement of the United States of America, the Republic of Armenia, and the Republic of Azerbaijan on the One-Year Anniversary of the White House Peace Summit": {
        "title_zh": "美、亚美尼亚、阿塞拜疆就白宫和平峰会一周年发表联合声明",
        "summary_zh": "美国、亚美尼亚与阿塞拜疆三国就白宫和平峰会召开一周年发表联合声明，回顾一年前特朗普主持的峰会成果，重申继续推进地区和平与关系正常化进程。",
    },
    "Diplomatic Security Leads Investigation Resulting in Guilty Plea for Threats Against Secretary of State Marco Rubio": {
        "title_zh": "外交安全局主导调查：威胁国务卿卢比奥者认罪",
        "summary_zh": "迈阿密一名男子上周就三项跨州传播威胁言论罪名认罪，其曾在社交媒体X上多次公开发帖威胁包括国务卿马尔科·卢比奥在内的政府高官，案件由国务院外交安全局主导侦办。",
    },
    "State Department Revokes More Than 175,000 Visas": {
        "title_zh": "国务院已吊销逾17.5万份签证",
        "summary_zh": "在特朗普总统领导下，美国国务院已吊销逾17.5万名违反签证条款、犯罪、煽动针对美国公民暴力或危害国家安全的外国人签证，多数吊销源于执法接触。",
    },
    "Ecuador National Day": {
        "title_zh": "厄瓜多尔国庆日贺词",
        "summary_zh": "值厄瓜多尔独立217周年之际，美国国务院发表贺词，重申两国深厚的历史纽带，并表示在特朗普政府领导下双方在打击跨国犯罪与反毒品恐怖主义方面的合作进一步深化。",
    },
    "United States Advances Trusted Digital Infrastructure at CANTO 2026": {
        "title_zh": "美国在2026年CANTO大会上推进可信数字基础设施建设",
        "summary_zh": "美国本周与加勒比地区官员、监管机构及行业领袖齐聚多米尼加蓬塔卡纳，出席加勒比国家电信组织（CANTO）年会，重申对加勒比地区安全可信数字基础设施的承诺。",
    },
    "China’s “Administrative Measures” at Scarborough Reef": {
        "title_zh": "国务院声明：反对中国在黄岩岛的\"行政措施\"",
        "summary_zh": "美国国务院发表声明，拒绝中国在黄岩岛实施\"国家自然保护区\"的单边行径及其阻碍菲律宾渔民进入传统渔场的行为，指其以可疑的环境与法律借口、倚仗武力推进扩张主张，违反2016年仲裁裁决。",
    },
    "Singapore National Day": {
        "title_zh": "新加坡国庆日贺词",
        "summary_zh": "值新加坡8月9日第61个国庆日之际，美国向新加坡人民致以祝贺，今年适逢美新建交60周年，两国以相互尊重与共同利益为纽带的外交关系具有特殊意义。",
    },
    "The Anniversary of a Historic Breakthrough and the Trump Route for International Peace and Prosperity (TRIPP)": {
        "title_zh": "历史性突破一周年与特朗普国际和平繁荣路线（TRIPP）",
        "summary_zh": "一年前的今天，特朗普总统在白宫见证阿塞拜疆总统阿利耶夫与亚美尼亚总理帕希尼扬签署历史性和平协议，值此一周年之际，国务院回顾\"特朗普国际和平繁荣路线\"（TRIPP）的成果。",
    },
    "A New Era in U.S.-Colombia Relations": {
        "title_zh": "美哥关系进入新时代",
        "summary_zh": "由代理司法部长托德·布兰奇率领的总统代表团出席8月7日哥伦比亚总统阿贝拉尔多·德·拉·埃斯普列利亚的就职典礼，彰显美国重振美哥关系、深化安全与经济伙伴关系的承诺。",
    },
}

def has_zh(s):
    return any('\u4e00' <= c <= '\u9fff' for c in (s or ''))

def main():
    with open(PATH) as f:
        items = json.load(f)
    updated = 0
    for it in items:
        t = it.get('title', '')
        # 匹配标题（精确或前缀）
        key = None
        for k in TRANSLATIONS:
            if t == k or t.startswith(k[:50]):
                key = k
                break
        if key and not has_zh(it.get('title_zh')):
            it['title_zh'] = TRANSLATIONS[key]['title_zh']
            it['summary_zh'] = TRANSLATIONS[key]['summary_zh']
            # 同步双语 title 字段
            it['title'] = f"{it.get('title_en') or t} {TRANSLATIONS[key]['title_zh']}"
            updated += 1
            print(f"  ✓ [{it['source']}] {TRANSLATIONS[key]['title_zh'][:40]}")
    with open(PATH, 'w') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"\n共更新 {updated} 条")
    # 校验
    missing = [it for it in items if not has_zh(it.get('title_zh'))]
    print(f"仍缺中文: {len(missing)} 条")

if __name__ == '__main__':
    main()
