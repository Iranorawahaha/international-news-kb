#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_china.py — 国内新闻看板 · 权威信源抓取器 v2（Ira 信息看板体系）

数据源（国家级权威 + 严格过滤）：
  1. 中国政府网·要闻      https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json
  2. 中国政府网·最新政策  https://www.gov.cn/zhengce/zuixin/ZUIXINZHENGCE.json
  3. 央视新闻             https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/china_1.jsonp
  4. 人民日报             http://paper.people.com.cn/rmrb/pc/layout/{YYYYMM}/dd 头版+要闻版（HTML 解析）
  5. 凤凰新闻             https://news.ifeng.com/（HTML 解析，严格过滤标题党/猎奇）

过滤标准（严格，用户红线）：
  - 标题黑名单: 营销/文娱/小道/八卦/震惊/猎奇等词剔除
  - 重要度分级: 元首级(习近平/国家主席/中央军委) > 常委级(李强/赵乐际等) >
               部委级(国务院常务会议) > 重要会议 > 人事任免 > 经贸政策 > 一般
  - 分类: 元首动态 / 常委动态 / 重要会议 / 人事任免 / 政策发布 / 经贸动向 / 其他

输出: data/china-news.json (archive 按日期分组, 7 天滚动)
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "china-news.json")

# ============ 信源配置 ============
GOV_YAOWEN = "https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json"
GOV_ZHENGCE = "https://www.gov.cn/zhengce/zuixin/ZUIXINZHENGCE.json"
CCTV_CHINA = "https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/china_1.jsonp"
RMRB_LAYOUT = "http://paper.people.com.cn/rmrb/pc/layout/{date_path}/node_{node:02d}.html"
IFENG_HOME = "https://news.ifeng.com/"

# ============ 领导人名单 ============
SUMMIT_LEADERS = ["习近平", "国家主席", "中央军委", "总书记"]
PSC_LEADERS = ["李强", "赵乐际", "王沪宁", "蔡奇", "丁薛祥", "李希"]

# 经贸动向关键词
ECONOMY_KEYWORDS = [
    "经济", "贸易", "关税", "进出口", "外贸", "外资", "央行", "财政", "金融",
    "货币", "产业", "投资", "人民币", "汇率", "GDP", "发改委", "商务部",
    "市场监管", "税收", "减税", "补贴", "制造业", "供应链", "一带一路",
    "自贸区", "RCEP", "WTO", "中美经贸", "营商环境",
    "宏观政策", "政策发力", "扩内需", "促消费", "稳增长", "保供稳价",
    "经济增长", "经济工作", "经济形势", "新质生产力", "高质量发展",
    "电力市场", "能源市场", "粮食安全", "春耕", "秋收", "进出口贸易",
]

# 营销号/文娱/小道消息/猎奇黑名单（标题含则剔除）
JUNK_KEYWORDS = [
    # 营销/带货
    "带货", "促销", "打折", "秒杀", "福利", "抽奖", "优惠券", "直播间", "网红店",
    # 娱乐/明星/八卦
    "娱乐圈", "明星", "八卦", "绯闻", "吃瓜", "剧透", "演唱会", "票房", "综艺",
    "粉丝", "应援", "爱豆", "男团", "女团", "热搜爆", "恋情",
    # 猎奇/标题党/负面猎奇
    "震惊", "太可怕", "万万没想到", "看完沉默了", "重磅内幕", "独家爆料", "小道消息",
    "爆仓", "暴跌", "崩盘", "炼金", "秘术", "判刑", "被捕", "诈骗", "盗墓",
    "报警", "警察上门", "命案", "跳楼", "轻生", "悲剧", "惨案", "尸体",
    # 养生/伪科学
    "养生", "偏方", "神医", "风水", "星座", "生肖运势", "减肥", "美白", "祛痘",
    "长寿秘诀", "排毒", "抗癌秘方",
    # 软文/广告
    "限时", "独家优惠", "免费领取", "点击领取",
    "投资者关系", "京ICP", "ICP证", "版权所有", "联系我们", "关于我们", "隐私政策", "网站地图",
]

# 分类规则（按优先级顺序）
CATEGORY_RULES = [
    ("元首动态", ["习近平", "国家主席", "中央军委", "总书记", "出席", "考察", "会见", "通令"]),
    ("常委动态", ["李强", "赵乐际", "王沪宁", "蔡奇", "丁薛祥", "李希"]),
    ("重要会议", ["会议", "全会", "座谈会", "研讨会", "论坛", "学习贯彻", "集体学习"]),
    ("人事任免", ["任免", "任命", "免去", "担任", "任命决定", "提请任命"]),
    ("政策发布", ["印发", "通知", "规划", "意见", "方案", "条例", "规定", "办法", "决定", "批复"]),
    ("经贸动向", ECONOMY_KEYWORDS),
]

CATEGORY_ICONS = {
    "元首动态": "👑", "常委动态": "🧭", "重要会议": "🏛", "人事任免": "📋",
    "政策发布": "📜", "经贸动向": "💹", "其他": "📌",
}


def fetch(url, headers=None):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Referer": "https://www.gov.cn/",
        "Accept-Language": "zh-CN,zh;q=0.9",
    })
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def classify(title):
    for cat, kws in CATEGORY_RULES:
        for kw in kws:
            if kw in title:
                return cat
    return "其他"


def assess_importance(title, cat):
    """重要度 0-100"""
    score = 50
    for kw in SUMMIT_LEADERS:
        if kw in title:
            score = 100
            break
    else:
        for kw in PSC_LEADERS:
            if kw in title:
                score = 95
                break
        else:
            if cat == "重要会议":
                score = 88
            elif cat == "人事任免":
                score = 82
            elif cat == "政策发布":
                score = 80
            elif cat == "经贸动向":
                # 经贸：涉中央/国务院层面加高
                if any(k in title for k in ["国务院", "中央", "习近平", "李强", "政治局"]):
                    score = 85
                else:
                    score = 72
    return score


def is_summit(title):
    return any(kw in title for kw in SUMMIT_LEADERS)


def is_junk(title):
    return any(kw in title for kw in JUNK_KEYWORDS)


def make_item(title, url, date, source):
    if not title or not url or is_junk(title):
        return None
    title = re.sub(r"^【[^】]*】\s*", "", title).strip()  # 去【视频】等前缀
    if len(title) < 8:  # 太短忽略
        return None
    cat = classify(title)
    return {
        "title": title,
        "url": url,
        "date": date,
        "source": source,
        "category": cat,
        "priority_score": assess_importance(title, cat),
        "is_summit_level": is_summit(title),
        "collectedAt": NOW.strftime("%Y-%m-%d %H:%M:%S"),
    }


def fetch_gov(url, source_name):
    """中国政府网 JSON 接口"""
    items = []
    try:
        data = json.loads(fetch(url))
        lst = data if isinstance(data, list) else data.get("listArrP") or data.get("data") or []
        for it in lst:
            t = (it.get("TITLE") or "").strip()
            u = (it.get("URL") or "").strip()
            d = (it.get("DOCRELPUBTIME") or "").strip()[:10]
            item = make_item(t, u, d, source_name)
            if item:
                items.append(item)
        print(f"  ✅ {source_name}: {len(lst)} 条 → 采纳 {len(items)} 条")
    except Exception as e:
        print(f"  ❌ {source_name}: {e}")
    return items


def fetch_cctv():
    """央视新闻 JSONP 接口"""
    items = []
    try:
        raw = fetch(CCTV_CHINA)
        m = re.match(r"[a-zA-Z_]+\((.*)\)\s*$", raw, re.S)
        if not m:
            print("  ❌ 央视: JSONP 解析失败")
            return items
        d = json.loads(m.group(1))
        lst = d.get("data", {}).get("list", [])
        for it in lst:
            t = (it.get("title") or "").strip()
            u = (it.get("url") or "").strip()
            d = (it.get("focus_date") or "")[:10]
            item = make_item(t, u, d, "央视新闻")
            if item:
                items.append(item)
        print(f"  ✅ 央视新闻: {len(lst)} 条 → 采纳 {len(items)} 条")
    except Exception as e:
        print(f"  ❌ 央视新闻: {e}")
    return items


def fetch_rmrb():
    """人民日报 头版+要闻版（node_01~04）"""
    items = []
    d = NOW.strftime("%Y%m%d")
    date_path = NOW.strftime("%Y%m") + "/" + NOW.strftime("%d")
    for node in (1, 2, 3, 4):  # 头版 + 3 个要闻版
        url = RMRB_LAYOUT.format(date_path=date_path, node=node)
        try:
            h = fetch(url)
            # 提取文章链接（content_*.html）
            for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>([^<]{8,80})</a>', h):
                u, t = m.group(1), m.group(2).strip()
                if "content_" in u and "版" not in t:
                    full_u = u if u.startswith("http") else (
                        f"http://paper.people.com.cn/rmrb/pc/{u.lstrip('./')}" if u.startswith(".") else f"http://paper.people.com.cn/rmrb/pc/layout/{date_path}/{u}"
                    )
                    item = make_item(t, full_u, NOW.strftime("%Y-%m-%d"), "人民日报")
                    if item:
                        items.append(item)
        except Exception as e:
            print(f"  ⚠️  人民日报 node_{node}: {e}")
    print(f"  ✅ 人民日报(头版+要闻): 采纳 {len(items)} 条")
    return items


def fetch_ifeng():
    """凤凰新闻（严格过滤，仅采纳时政/经贸类）"""
    items = []
    try:
        h = fetch(IFENG_HOME)
        titles = re.findall(r'"title":"([^"]{8,80})"', h)
        urls = re.findall(r'"url":"(https?://[^"]{15,120})"', h)
        # 尽量配对 title 与 url（同序）
        for i, t in enumerate(titles):
            if len(urls) > i:
                item = make_item(t, urls[i], NOW.strftime("%Y-%m-%d"), "凤凰新闻")
                if item and item["category"] in ("时政", "元首动态", "常委动态", "重要会议", "经贸动向", "政策发布"):
                    items.append(item)
        # 去重
        seen = set()
        uniq = []
        for it in items:
            if it["title"] not in seen:
                seen.add(it["title"])
                uniq.append(it)
        print(f"  ✅ 凤凰新闻: 标题 {len(titles)} 条 → 采纳 {len(uniq)} 条（严格过滤）")
        return uniq
    except Exception as e:
        print(f"  ❌ 凤凰新闻: {e}")
    return items


def main():
    print(f"🕗 {NOW.strftime('%Y-%m-%d %H:%M')} 北京时间 · 国内新闻抓取开始\n")

    all_items = []
    all_items += fetch_gov(GOV_YAOWEN, "中国政府网·要闻")
    all_items += fetch_gov(GOV_ZHENGCE, "中国政府网·最新政策")
    all_items += fetch_cctv()
    all_items += fetch_rmrb()
    all_items += fetch_ifeng()

    # 去重（标题相似去重）
    seen, unique = set(), []
    for it in all_items:
        norm = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", it["title"])[:40]
        if norm in seen:
            continue
        seen.add(norm)
        unique.append(it)

    # 按日期归档
    archive = {}
    for it in unique:
        d = it["date"] or NOW.strftime("%Y-%m-%d")
        archive.setdefault(d, []).append(it)
    for d in archive:
        archive[d].sort(key=lambda x: (-x["priority_score"], x["title"]))

    # 7 天保留
    cutoff = (NOW - timedelta(days=7)).strftime("%Y-%m-%d")
    archive = {d: v for d, v in archive.items() if d >= cutoff}

    dates = sorted(archive.keys(), reverse=True)
    total = sum(len(v) for v in archive.values())
    today = NOW.strftime("%Y-%m-%d")

    per_cat = {}
    for d in dates:
        for it in archive[d]:
            per_cat[it["category"]] = per_cat.get(it["category"], 0) + 1

    data = {
        "version": "2.0",
        "lastUpdated": NOW.strftime("%Y-%m-%d %H:%M"),
        "retentionDays": 7,
        "archive": archive,
        "dates": dates,
        "today": today,
        "todayCount": len(archive.get(today, [])),
        "stats": {
            "totalArticles": total,
            "dateCount": len(dates),
            "latestDate": dates[0] if dates else None,
            "summitCount": sum(1 for v in archive.values() for x in v if x.get("is_summit_level")),
        },
    }

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n📊 国内新闻抓取完成:")
    print(f"  总计: {total} 条 | 覆盖 {len(dates)} 天 | 今日 {data['todayCount']} 条 | ⭐元首级 {data['stats']['summitCount']} 条")
    print(f"  分类分布: {per_cat}")
    print(f"  信源分布:")
    src_cnt = {}
    for v in archive.values():
        for x in v:
            src_cnt[x["source"]] = src_cnt.get(x["source"], 0) + 1
    for s, c in sorted(src_cnt.items(), key=lambda kv: -kv[1]):
        print(f"    • {s}: {c} 条")
    print(f"  💾 已保存: {DATA_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
