#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_china.py — 国内新闻看板 · 权威信源抓取器 v3（Ira 信息看板体系）

数据源（国家级权威 + 严格过滤）：
  1. 中国政府网·要闻      https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json
  2. 中国政府网·最新政策  https://www.gov.cn/zhengce/zuixin/ZUIXINZHENGCE.json
  3. 央视新闻             https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/china_1.jsonp
  4. 人民日报             http://paper.people.com.cn/rmrb/pc/layout/{YYYYMM}/dd 头版+要闻版
  5. 凤凰新闻             https://news.ifeng.com/（严格过滤）

v3 改进（2026-08-01 用户反馈）：
  - 摘要: 每条记录抓取正文首段作精简摘要（央视用 brief 字段）
  - 权威去重: 跨信源同题去重，保留权威优先（政府网 > 央视 > 人民日报 > 凤凰）
  - 分类重构:
    · 元首动态: 仅限习近平总书记相关
    · 高层动态: 政治局常委 + 政治局委员/副国级（何立峰/王毅等）
    · 部委动态: 工信部/网信办/发改委/国办/中办/商务部/外交部等
    · 人事任免: 中央到地方高层（含陈新武任重庆市代市长等）
    · 政策发布 / 经贸动向 / 重要会议 / 其他
  - 强化过滤: 天气/文旅/非遗/民俗/猎奇等杂项剔除
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

GOV_YAOWEN = "https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json"
GOV_ZHENGCE = "https://www.gov.cn/zhengce/zuixin/ZUIXINZHENGCE.json"
CCTV_CHINA = "https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/china_1.jsonp"
RMRB_LAYOUT = "http://paper.people.com.cn/rmrb/pc/layout/{date_path}/node_{node:02d}.html"
IFENG_HOME = "https://news.ifeng.com/"

# 信源权威优先级（去重时保留优先级高的）
SOURCE_PRIORITY = {"中国政府网·要闻": 1, "中国政府网·最新政策": 1, "央视新闻": 2, "人民日报": 3, "凤凰新闻": 4}

# ============ 领导人名单 ============
# 元首动态：仅习近平总书记相关
XI_KEYWORDS = ["习近平", "国家主席", "中央军委主席", "总书记"]
# 高层动态：政治局常委 + 政治局委员/副国级
PSC_KEYWORDS = ["李强", "赵乐际", "王沪宁", "蔡奇", "丁薛祥", "李希",
                "何立峰", "王毅", "李干杰", "张国清", "陈文清", "刘国中", "石泰峰",
                "黄坤明", "陈吉宁", "袁家军", "尹力", "马兴瑞", "信长星", "梁言顺", "王君正",
                "李书磊", "穆虹", "秦刚", "刘建超", "李尚福", "王小洪", "张又侠", "何卫东",
                "张春贤", "王东明", "彭清华", "郑建邦", "郝明金", "蔡达峰", "何维", "武维华",
                "铁凝", "雪克来提", "洛桑江村", "国务院副总理", "国务院国务委员", "政治局委员"]
# 部委关键词（V3.1 聚焦用户点名 7 大部委 + 中美贸易/经济制裁/AI/信息通信话题）
BUWEI_KEYWORDS = [
    # 用户点名部委
    "工信部", "工业和信息化部", "网信办", "国家网信办", "中央网信办", "发改委",
    "国家发展改革委", "发展改革委", "国办", "国务院办公厅", "中办", "中共中央办公厅",
    "商务部", "外交部", "外交部发言人",
    # 中美贸易/经济制裁/AI/信息通信话题
    "中美贸易", "贸易战", "经济制裁", "实体清单", "出口管制", "关税",
    "AI", "人工智能", "大模型", "芯片", "半导体", "信息通信", "5G", "6G",
    "集成电路", "算力", "数据安全", "网络安全",
]
# 经贸关键词
ECONOMY_KEYWORDS = [
    "经济", "贸易", "关税", "进出口", "外贸", "外资", "央行", "财政", "金融",
    "货币", "产业", "投资", "人民币", "汇率", "GDP", "发改委", "商务部",
    "市场监管", "税收", "减税", "补贴", "制造业", "供应链", "一带一路",
    "自贸区", "RCEP", "WTO", "中美经贸", "营商环境",
    "宏观政策", "政策发力", "扩内需", "促消费", "稳增长", "保供稳价",
    "经济增长", "经济工作", "经济形势", "新质生产力", "高质量发展",
    "电力市场", "能源市场", "粮食安全", "进出口贸易", "关税壁垒", "经济制裁",
    "对华关税", "贸易战", "实体清单", "出口管制", "反倾销", "贸易顺差",
]

# ============ 垃圾/杂项黑名单（v3 强化） ============
JUNK_KEYWORDS = [
    # 营销/带货
    "带货", "促销", "打折", "秒杀", "福利", "抽奖", "优惠券", "直播间", "网红店",
    # 娱乐/明星/八卦
    "娱乐圈", "明星", "八卦", "绯闻", "吃瓜", "剧透", "演唱会", "票房", "综艺",
    "粉丝", "应援", "爱豆", "男团", "女团", "恋情", "追星",
    # 猎奇/标题党/负面猎奇
    "震惊", "太可怕", "万万没想到", "看完沉默了", "重磅内幕", "独家爆料", "小道消息",
    "爆仓", "暴跌", "崩盘", "炼金", "秘术", "判刑", "被捕", "诈骗", "盗墓",
    "报警", "警察上门", "命案", "跳楼", "轻生", "悲剧", "惨案", "尸体", "出轨",
    # 天气/自然灾害日常预报（非重大灾害）
    "台风", "暴雨预警", "黄色预警", "蓝色预警", "高温天气", "降温", "降雨", "降雨量",
    "桑拿天", "闷热", "冰雹", "预警升级", "火云", "天气", "气象台", "气温", "酷暑", "寒潮",
    # 文旅/非遗/民俗/民生杂项
    "漂流", "夜漂", "非遗", "守艺人", "文旅", "打卡", "旅游", "景区", "美食", "小吃",
    "民俗", "庙会", "灯会", "烟花", "节庆", "乡村游", "研学", "文创", "国潮",
    # 养生/伪科学
    "养生", "偏方", "神医", "风水", "星座", "生肖运势", "减肥", "美白", "祛痘",
    "长寿秘诀", "排毒", "抗癌秘方",
    # 软文/广告
    "限时", "独家优惠", "免费领取", "点击领取",
    # 页面噪音
    "投资者关系", "京ICP", "ICP证", "版权所有", "联系我们", "关于我们", "隐私政策", "网站地图",
    # 非中国国内内容（他国国内事务/领导人，非涉华报道）
    "俄外交部", "乌克兰", "乌军", "基辅", "莫斯科", "特朗普发", "普京", "拜登",
    "泽连斯基", "内塔尼亚胡", "莫迪", "马斯克发", "美国国务卿", "英媒", "美媒报",
    # 民生琐事/社会花边/文旅剩余
    "大爷", "大妈", "女子", "男子", "司机", "快递小哥", "外卖", "宠物", "猫咪", "狗狗",
    "圈粉", "市井风情", "烟火气", "出圈", "走红", "网红", "打卡地", "风景线",
    "夏日", "清凉", "避暑", "采摘", "丰收节", "乡村", "田园", "古镇", "老街",
    # 天气继续加强
    "红色山洪", "山洪", "洪水", "内涝", "应急响应", "防汛", "汛情", "灾情", "天气预警",
]

# 分类规则（按优先级顺序，v3 重构）
CATEGORY_RULES = [
    # 1. 元首动态：仅习近平相关
    ("元首动态", XI_KEYWORDS),
    # 2. 高层动态：政治局常委 + 政治局委员
    ("高层动态", PSC_KEYWORDS),
    # 3. 重要会议
    ("重要会议", ["会议", "全会", "座谈会", "研讨会", "论坛", "学习贯彻", "集体学习", "中央经济工作会议", "全国两会", "人代会", "政协会"]),
    # 4. 人事任免（中央到地方高层）
    ("人事任免", ["任免", "任命", "免去", "担任", "任命决定", "提请任命", "代市长", "代省长", "代县长",
                   "履新", "出任", "接任", "当选", "辞去", "代理"]),
    # 5. 部委动态（工信/网信/发改/国办/中办/商务/外交等）
    ("部委动态", BUWEI_KEYWORDS),
    # 6. 政策发布
    ("政策发布", ["印发", "通知", "规划", "意见", "方案", "条例", "规定", "办法", "决定", "批复", "白皮书"]),
    # 7. 经贸动向
    ("经贸动向", ECONOMY_KEYWORDS),
]

CATEGORY_ICONS = {
    "元首动态": "👑", "高层动态": "🧭", "重要会议": "🏛", "人事任免": "📋",
    "部委动态": "🏢", "政策发布": "📜", "经贸动向": "💹", "其他": "📌",
}


def fetch(url, headers=None, timeout=12):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Referer": "https://www.gov.cn/",
        "Accept-Language": "zh-CN,zh;q=0.9",
    })
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def classify(title):
    for cat, kws in CATEGORY_RULES:
        for kw in kws:
            if kw in title:
                return cat
    return None  # 未匹配任何关注分类 → 丢弃（彻底删除"其他"类目）


def assess_importance(title, cat):
    """重要度 0-100"""
    score = 50
    for kw in XI_KEYWORDS:
        if kw in title:
            score = 100
            break
    else:
        for kw in PSC_KEYWORDS:
            if kw in title:
                score = 95
                break
        else:
            if cat == "重要会议":
                score = 88
            elif cat == "人事任免":
                score = 85
            elif cat == "部委动态":
                score = 78
            elif cat == "政策发布":
                score = 80
            elif cat == "经贸动向":
                if any(k in title for k in ["国务院", "中央", "习近平", "李强", "政治局"]):
                    score = 85
                else:
                    score = 72
    return score


def is_summit(title):
    return any(kw in title for kw in XI_KEYWORDS)


def is_junk(title):
    return any(kw in title for kw in JUNK_KEYWORDS)


def extract_summary_from_url(url, max_len=100):
    """抓取文章页正文首段作精简摘要"""
    try:
        h = fetch(url, timeout=8)
        h = re.sub(r"<script.*?</script>", "", h, flags=re.S)
        h = re.sub(r"<style.*?</style>", "", h, flags=re.S)
        # 人民日报: enpcontent 标记
        m = re.search(r"enpcontent(.*?)enpcontent", h, re.S)
        if m:
            paras = re.findall(r"<p[^>]*>([^<]{15,300})</p>", m.group(1))
        else:
            paras = re.findall(r"<p[^>]*>([^<]{15,300})</p>", h)
        for p in paras:
            p = re.sub(r"<[^>]+>", "", p).strip()
            p = p.replace("　", " ").replace("\n", " ").strip()
            # 跳过导航/占位
            if not p or "版" in p[:12] or p.startswith("■"):
                continue
            if len(p) >= 15:
                return p[:max_len] + ("…" if len(p) > max_len else "")
        return ""
    except Exception:
        return ""


def make_item(title, url, date, source, summary=None):
    if not title or not url or is_junk(title):
        return None
    title = re.sub(r"^【[^】]*】\s*", "", title).strip()
    title = re.sub(r"^\[[^\]]*\]\s*", "", title).strip()
    if len(title) < 8:
        return None
    cat = classify(title)
    if cat is None:
        return None  # 未命中任何关注分类 → 丢弃
    return {
        "title": title,
        "url": url,
        "date": date,
        "source": source,
        "category": cat,
        "priority_score": assess_importance(title, cat),
        "is_summit_level": is_summit(title),
        "summary": (summary or "").strip(),
        "collectedAt": NOW.strftime("%Y-%m-%d %H:%M:%S"),
    }


def fetch_gov(url, source_name):
    """中国政府网 JSON 接口 + 抓正文摘要"""
    items = []
    try:
        data = json.loads(fetch(url))
        lst = data if isinstance(data, list) else data.get("listArrP") or data.get("data") or []
        # 政府网只保留近 7 天
        cutoff = (NOW - timedelta(days=7)).strftime("%Y-%m-%d")
        for it in lst:
            t = (it.get("TITLE") or "").strip()
            u = (it.get("URL") or "").strip()
            d = (it.get("DOCRELPUBTIME") or "").strip()[:10]
            if d < cutoff:
                continue
            item = make_item(t, u, d, source_name)
            if item:
                items.append(item)
        # 抓摘要（限量，避免请求过多）
        print(f"  ✅ {source_name}: {len(lst)} 条(近7天 {len(items)} 条) → 抓取摘要...")
        for it in items[:40]:
            if not it.get("summary"):
                it["summary"] = extract_summary_from_url(it["url"])
    except Exception as e:
        print(f"  ❌ {source_name}: {e}")
    return items


def fetch_cctv():
    """央视新闻 JSONP 接口（brief 即摘要）"""
    items = []
    try:
        raw = fetch(CCTV_CHINA)
        m = re.match(r"[a-zA-Z_]+\((.*)\)\s*$", raw, re.S)
        if not m:
            print("  ❌ 央视: JSONP 解析失败")
            return items
        d = json.loads(m.group(1))
        lst = d.get("data", {}).get("list", [])
        cutoff = (NOW - timedelta(days=7)).strftime("%Y-%m-%d")
        for it in lst:
            t = (it.get("title") or "").strip()
            u = (it.get("url") or "").strip()
            d = (it.get("focus_date") or "")[:10]
            if d < cutoff:
                continue
            brief = (it.get("brief") or "").strip()
            item = make_item(t, u, d, "央视新闻", summary=brief[:100] + ("…" if len(brief) > 100 else ""))
            if item:
                items.append(item)
        print(f"  ✅ 央视新闻: {len(lst)} 条 → 采纳 {len(items)} 条（含 brief 摘要）")
    except Exception as e:
        print(f"  ❌ 央视新闻: {e}")
    return items


def fetch_rmrb():
    """人民日报 头版+要闻版（node_01~04）+ 正文摘要"""
    items = []
    d = NOW.strftime("%Y%m%d")
    date_path = NOW.strftime("%Y%m") + "/" + NOW.strftime("%d")
    for node in (1, 2, 3, 4):
        url = RMRB_LAYOUT.format(date_path=date_path, node=node)
        try:
            h = fetch(url, timeout=8)
            for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>([^<]{8,80})</a>', h):
                u, t = m.group(1), m.group(2).strip()
                if "content_" in u and "版" not in t:
                    full_u = u if u.startswith("http") else (
                        f"http://paper.people.com.cn/rmrb/pc/{u.lstrip('./')}" if u.startswith(".") else
                        f"http://paper.people.com.cn/rmrb/pc/layout/{date_path}/{u}"
                    )
                    item = make_item(t, full_u, NOW.strftime("%Y-%m-%d"), "人民日报")
                    if item:
                        items.append(item)
        except Exception as e:
            print(f"  ⚠️  人民日报 node_{node}: {e}")
    # 抓摘要
    print(f"  ✅ 人民日报(头版+要闻): 采纳 {len(items)} 条 → 抓取摘要...")
    for it in items[:20]:
        if not it.get("summary"):
            it["summary"] = extract_summary_from_url(it["url"])
    return items


def fetch_ifeng():
    """凤凰新闻（严格过滤，仅采纳时政/高层/部委/经贸/会议/人事）"""
    items = []
    try:
        h = fetch(IFENG_HOME, timeout=10)
        titles = re.findall(r'"title":"([^"]{8,80})"', h)
        urls = re.findall(r'"url":"(https?://[^"]{15,120})"', h)
        keep_cats = ("元首动态", "高层动态", "重要会议", "人事任免", "部委动态", "政策发布", "经贸动向")
        for i, t in enumerate(titles):
            if len(urls) > i:
                item = make_item(t, urls[i], NOW.strftime("%Y-%m-%d"), "凤凰新闻")
                if item and item["category"] in keep_cats:
                    items.append(item)
        seen, uniq = set(), []
        for it in items:
            if it["title"] not in seen:
                seen.add(it["title"])
                uniq.append(it)
        print(f"  ✅ 凤凰新闻: 标题 {len(titles)} 条 → 采纳 {len(uniq)} 条（严格过滤）")
        return uniq
    except Exception as e:
        print(f"  ❌ 凤凰新闻: {e}")
    return items


def normalize_title_for_dedup(title):
    """标题规范化（去栏目前缀/标点/同义词归一），用于跨信源去重"""
    t = title or ""
    # 去栏目前缀（学习卡丨 / 时政新闻眼丨 / 传习录丨 / 习语丨 等）
    t = re.sub(r"^[^丨]{0,8}丨", "", t)
    t = re.sub(r"^(学习卡|时政新闻眼|传习录|习语|焦点访谈|新闻联播|联播快讯|央视快评)[丨:：]", "", t)
    # 去【】标注
    t = re.sub(r"^【[^】]*】", "", t)
    t = re.sub(r"^\[[^\]]*\]", "", t)
    # 同义词归一
    t = t.replace("国务院办公厅", "国办").replace("工业和信息化部", "工信部")
    t = t.replace("国家发展改革委", "发改委").replace("中共中央办公厅", "中办")
    t = t.replace("习近平：", "").replace("习近平:", "")
    # 去标点/空格，仅留中英文数字
    t = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", t)
    return t[:30]


def main():
    print(f"🕗 {NOW.strftime('%Y-%m-%d %H:%M')} 北京时间 · 国内新闻抓取开始（v3）\n")

    all_items = []
    all_items += fetch_gov(GOV_YAOWEN, "中国政府网·要闻")
    all_items += fetch_gov(GOV_ZHENGCE, "中国政府网·最新政策")
    all_items += fetch_cctv()
    all_items += fetch_rmrb()
    all_items += fetch_ifeng()

    # 跨信源去重：标题相似（规范化后）时保留权威优先级高的（政府网 > 央视 > 人民日报 > 凤凰）
    seen, unique = {}, []
    for it in all_items:
        norm = normalize_title_for_dedup(it["title"])
        if not norm:
            continue
        # 子串匹配：已有条目是当前条目前缀（或反之）也视为重复
        matched_key = None
        for k in seen:
            if k in norm or norm in k:
                matched_key = k
                break
        if matched_key:
            old = seen[matched_key]
            old_pri = SOURCE_PRIORITY.get(old["source"], 99)
            new_pri = SOURCE_PRIORITY.get(it["source"], 99)
            if new_pri < old_pri:
                idx = unique.index(old)
                unique[idx] = it
                seen[matched_key] = it
            continue
        seen[norm] = it
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
        "version": "3.0",
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

    print(f"\n📊 国内新闻抓取完成（v3）:")
    print(f"  总计: {total} 条 | 覆盖 {len(dates)} 天 | 今日 {data['todayCount']} 条 | ⭐元首级 {data['stats']['summitCount']} 条")
    print(f"  分类分布: {per_cat}")
    print(f"  信源分布:")
    src_cnt = {}
    for v in archive.values():
        for x in v:
            src_cnt[x["source"]] = src_cnt.get(x["source"], 0) + 1
    for s, c in sorted(src_cnt.items(), key=lambda kv: -kv[1]):
        print(f"    • {s}: {c} 条")
    with_sum = sum(1 for v in archive.values() for x in v if x.get("summary"))
    print(f"  有摘要: {with_sum}/{total} 条")
    print(f"  💾 已保存: {DATA_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
