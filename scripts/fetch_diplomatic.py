#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_diplomatic.py — 使领馆事务数据采集器 v1.0（Ira 信息看板体系）

每日 08:00 运行，从权威公开信源采集：
1. 外交代表人事变化（驻华大使任命/到任/递交国书/离任等）
2. 驻上海、驻广州总领事人事变化
3. 外国重要高级官员实际访华
4. 中美高级官员互动

信源优先级：
- 中国外交部 (fmprc.gov.cn) - 外交动态/礼宾日程/发言人表态
- 中国政府网 (gov.cn) - 要闻
- 新华社 (xinhuanet.com) - 政治
- 各驻华使馆官网
- 权威外媒交叉验证

运行模式：
- 默认检查最近 72 小时（3天窗口）
- 首次运行/数据文件不存在则回看 7 天
- --window N 指定天数窗口
- --from YYYY-MM-DD --to YYYY-MM-DD 指定日期范围
"""
import json
import os
import re
import sys
import hashlib
import argparse
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
TODAY = NOW.strftime("%Y-%m-%d")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "diplomatic-affairs.json")

# ============== 配置 ==============
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# 外交部关键页面（2026-09-03 修复：fmprc.gov.cn 旧域名栏目已失效跳同页，改用 mfa.gov.cn 新栏目路径）
# 频道 wjdt_674879（外交动态）下子栏目：
#   wjbxw_674885 = 部领导新闻 | wsrc_674883 = 外事日程(访华预告) | fyrbt_674889 = 例行记者会
MFA_URLS = {
    "外交动态": "https://www.mfa.gov.cn/web/wjdt_674879/wjbxw_674885/",
    "外事日程": "https://www.mfa.gov.cn/web/wjdt_674879/wsrc_674883/",
    "例行记者会": "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/",
}

# gov.cn 要闻
GOV_YAOWEN_URL = "https://www.gov.cn/yaowen/liebiao/"

# 搜索关键词（中文）
DIPLOMATIC_KEYWORDS_CN = [
    # 大使人事
    "驻华大使", "新任大使", "递交国书", "国书副本", "大使离任", "大使到任",
    "大使任命", "驻华使馆", "使节", "礼宾司",
    # 总领事人事
    "驻上海总领事", "驻广州总领事", "总领事到任", "总领事离任",
    # 高级访华
    "访华", "来华", "会见", "会谈", "拜会", "抵京", "抵沪",
    # 中美互动
    "中美", "王毅", "布林肯", "耶伦", "雷蒙多", "沙利文",
]

# 职级关键词（用于筛选高级官员）
SENIOR_TITLES_CN = [
    "总统", "总理", "首相", "国王", "王后", "王储", "主席",
    "副总统", "副总理", "副首相",
    "部长", "大臣", "国务卿", "议长", "外长", "财长",
    "防长", "央行行长", "最高法院院长", "首席大法官",
    "检察长", "特使",
]


def fetch_url(url, timeout=15):
    """基础 HTTP GET 请求"""
    try:
        ctx = ssl.create_default_context()
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read()
            # 尝试解码
            for enc in ["utf-8", "gb2312", "gbk"]:
                try:
                    return raw.decode(enc)
                except UnicodeDecodeError:
                    continue
            return raw.decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ⚠️ 获取失败 {url}: {e}")
        return None


def extract_links_from_html(html, base_url=""):
    """从 HTML 中提取链接和标题"""
    links = []
    # 简单正则匹配 <a> 标签
    pattern = re.compile(
        r'<a[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        re.IGNORECASE | re.DOTALL
    )
    for match in pattern.finditer(html):
        href = match.group(1).strip()
        title = re.sub(r'<[^>]+>', '', match.group(2)).strip()
        if not title or not href:
            continue
        # 排除javascript/non-article links
        if href.startswith("javascript:") or href.startswith("#"):
            continue
        # 补全 URL
        if href.startswith("/"):
            if base_url:
                from urllib.parse import urljoin
                href = urljoin(base_url, href)
        links.append({"title": title, "url": href})
    return links


def is_in_window(date_str, window_start, window_end):
    """判断日期是否在窗口内"""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        ws = datetime.strptime(window_start, "%Y-%m-%d")
        we = datetime.strptime(window_end, "%Y-%m-%d")
        return ws <= d <= we
    except ValueError:
        return False


def make_id(item):
    """生成事件唯一 ID"""
    key = json.dumps(item, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(key.encode()).hexdigest()[:12]


# ============== 主采集逻辑 ==============

def collect_from_govcn(window_start, window_end):
    """
    从中国政府网采集外交/使领馆相关新闻。
    只做基础 URL 发现，详细内容由 WebFetch/agent 在对话中补强。
    """
    items = []
    print(f"\n📡 中国政府网 (gov.cn) 要闻采集...")
    html = fetch_url(GOV_YAOWEN_URL)
    if not html:
        return items

    links = extract_links_from_html(html, GOV_YAOWEN_URL)
    
    for link in links:
        title = link["title"]
        url = link["url"]
        
        # 关键词匹配
        matched = False
        for kw in DIPLOMATIC_KEYWORDS_CN:
            if kw in title:
                matched = True
                break
        if not matched:
            continue
        
        # 尝试从 URL 提取日期
        date_match = re.search(r'(\d{4})(\d{2})(\d{2})', url) or re.search(r'(\d{4})[-/](\d{2})[-/](\d{2})', url)
        if date_match:
            event_date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
        else:
            event_date = TODAY  # URL 无日期时用当天
        
        if not is_in_window(event_date, window_start, window_end):
            continue
        
        item = {
            "title": title,
            "url": url,
            "event_date": event_date,
            "source": "中国政府网",
            "collected_at": NOW.isoformat(),
        }
        items.append(item)
    
    print(f"  发现 {len(items)} 条候选")
    return items


def collect_from_mfa(window_start, window_end):
    """
    从外交部官网采集外交动态。
    """
    items = []
    print(f"\n📡 外交部 (fmprc.gov.cn) 外交动态采集...")
    
    for page_name, url in MFA_URLS.items():
        html = fetch_url(url)
        if not html:
            continue
        links = extract_links_from_html(html, url)
        
        for link in links:
            title = link["title"]
            link_url = link["url"]
            
            matched = False
            for kw in DIPLOMATIC_KEYWORDS_CN:
                if kw in title:
                    matched = True
                    break
            if not matched:
                continue
            
            date_match = re.search(r'(\d{4})(\d{2})(\d{2})', link_url) or re.search(r'(\d{4})[-/](\d{2})[-/](\d{2})', link_url)
            if date_match:
                event_date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
            else:
                event_date = TODAY
            
            if not is_in_window(event_date, window_start, window_end):
                continue
            
            item = {
                "title": title,
                "url": link_url,
                "event_date": event_date,
                "source": f"外交部·{page_name}",
                "collected_at": NOW.isoformat(),
            }
            items.append(item)
    
    print(f"  发现 {len(items)} 条候选")
    return items


# ============== 结构化整理 ==============

def classify_and_structure(raw_items):
    """
    将原始采集结果分类到四个模块。
    基础分类：后续由 agent/LLM 在 WorkBuddy 对话中补强和核验。
    """
    structured = {
        "personnel": [],
        "consuls": [],
        "visits": [],
        "us_china": [],
    }
    
    for item in raw_items:
        title = item.get("title", "")
        
        # 中美互动（优先级最高，可能是访华的一个子集）
        if any(kw in title for kw in ["中美", "王毅", "布林肯", "耶伦", "雷蒙多", "沙利文",
                                         "通话", "会见", "磋商", "对话"]):
            if any(kw in title for kw in ["王毅", "布林肯", "耶伦", "雷蒙多", "沙利文", "拜登", "特朗普"]):
                structured["us_china"].append({
                    "country": "美国",
                    "cn_person": "",
                    "us_person": "",
                    "interaction_type": "",
                    "event_date": item.get("event_date", TODAY),
                    "description": title,
                    "mutual_confirmed": False,
                    "cn_emphasis": "",
                    "us_emphasis": "",
                    "outcomes": "",
                    "sources": [{"title": item.get("source", ""), "url": item.get("url", "")}],
                    "confirmed": False,
                })
                continue
        
        # 大使/外交代表人事
        if any(kw in title for kw in ["驻华大使", "大使", "国书", "礼宾司", "使节", "离任", "到任"]):
            structured["personnel"].append({
                "country": "",
                "event_type": _guess_event_type(title),
                "current_status": "",
                "event_date": item.get("event_date", TODAY),
                "person_name": "",
                "description": title,
                "sources": [{"title": item.get("source", ""), "url": item.get("url", "")}],
                "confirmed": False,
            })
            continue
        
        # 总领事
        if any(kw in title for kw in ["总领事", "驻上海", "驻广州"]):
            post = "上海" if "上海" in title else "广州" if "广州" in title else ""
            structured["consuls"].append({
                "country": "",
                "post": post,
                "event_type": _guess_event_type(title),
                "current_status": "",
                "event_date": item.get("event_date", TODAY),
                "person_name": "",
                "description": title,
                "sources": [{"title": item.get("source", ""), "url": item.get("url", "")}],
                "confirmed": False,
            })
            continue
        
        # 高级官员访华
        if any(kw in title for kw in ["访华", "来华", "抵京", "抵沪", "会见"]):
            # 进一步检查是否有高级职级
            has_senior = any(t in title for t in SENIOR_TITLES_CN)
            if not has_senior:
                continue  # 跳过职级不够的
            
            structured["visits"].append({
                "country": _guess_country(title),
                "person_name": "",
                "position": "",
                "event_date": item.get("event_date", TODAY),
                "description": title,
                "ambassador_participation": "",
                "outcomes": "",
                "sources": [{"title": item.get("source", ""), "url": item.get("url", "")}],
                "confirmed": False,
            })
    
    return structured


def _guess_event_type(title):
    """根据标题猜测人事事件类型"""
    patterns = [
        ("递交国书", "递交国书"),
        ("国书副本", "递交国书副本"),
        ("递交国书副本", "递交国书副本"),
        ("抵华", "抵华"),
        ("到任", "到任履职"),
        ("离任", "离任"),
        ("任命", "任命"),
        ("提名", "提名"),
        ("履职", "正式履职"),
    ]
    for kw, label in patterns:
        if kw in title:
            return label
    return "人事变化"


def _guess_country(title):
    """根据标题猜测国家"""
    countries = [
        ("美国", "美国"), ("日本", "日本"), ("韩国", "韩国"), ("英国", "英国"),
        ("法国", "法国"), ("德国", "德国"), ("俄罗斯", "俄罗斯"), ("印度", "印度"),
        ("巴西", "巴西"), ("澳大利亚", "澳大利亚"), ("加拿大", "加拿大"),
        ("意大利", "意大利"), ("西班牙", "西班牙"), ("荷兰", "荷兰"),
        ("沙特", "沙特阿拉伯"), ("阿联酋", "阿联酋"), ("伊朗", "伊朗"),
        ("土耳其", "土耳其"), ("印尼", "印度尼西亚"), ("泰国", "泰国"),
        ("越南", "越南"), ("马来西亚", "马来西亚"), ("新加坡", "新加坡"),
        ("菲律宾", "菲律宾"), ("巴基斯坦", "巴基斯坦"), ("南非", "南非"),
        ("埃及", "埃及"), ("尼日利亚", "尼日利亚"), ("墨西哥", "墨西哥"),
        ("阿根廷", "阿根廷"), ("智利", "智利"),
        ("欧盟", "欧盟"), ("东盟", "东盟"), ("联合国", "联合国"),
    ]
    for kw, name in countries:
        if kw in title:
            return name
    return ""


# ============== 数据合并去重 ==============

def merge_with_existing(new_data, existing_file):
    """合并新数据到已有数据，按 id 去重"""
    if os.path.exists(existing_file):
        with open(existing_file, encoding="utf-8") as f:
            old = json.load(f)
    else:
        old = {"meta": {}, "modules": {"personnel": {"items": []}, "consuls": {"items": []},
                                         "visits": {"items": []}, "us_china": {"items": []}},
               "highlights": [], "data_summary": {}, "supplementary_notes": []}
    
    existing_ids = set()
    for module_key in ["personnel", "consuls", "visits", "us_china"]:
        for item in old.get("modules", {}).get(module_key, {}).get("items", []):
            if item.get("id"):
                existing_ids.add(item["id"])
    
    # 合并新项（给每个新项分配 ID）
    for module_key in ["personnel", "consuls", "visits", "us_china"]:
        for item in new_data.get(module_key, []):
            item["id"] = make_id(item)
            if item["id"] not in existing_ids:
                old["modules"][module_key]["items"].append(item)
                existing_ids.add(item["id"])
    
    return old


# ============== 入口 ==============

def main():
    parser = argparse.ArgumentParser(description="使领馆事务数据采集器")
    parser.add_argument("--window", type=int, default=3, help="回溯天数（默认3天）")
    parser.add_argument("--from", dest="from_date", help="起始日期 YYYY-MM-DD")
    parser.add_argument("--to", dest="to_date", help="结束日期 YYYY-MM-DD")
    parser.add_argument("--first-run", action="store_true", help="首次运行（回看7天）")
    args = parser.parse_args()
    
    # 确定时间窗口
    if args.first_run or not os.path.exists(DATA_FILE):
        window_days = 7
    else:
        window_days = args.window
    
    if args.from_date and args.to_date:
        window_start = args.from_date
        window_end = args.to_date
    else:
        window_end = TODAY
        window_start = (NOW - timedelta(days=window_days)).strftime("%Y-%m-%d")
    
    print(f"=== 使领馆事务数据采集 V1.0 ===")
    print(f"时间窗口: {window_start} ~ {window_end} ({window_days} 天)")
    print(f"执行时间: {NOW.strftime('%Y-%m-%d %H:%M:%S')} 北京时间")
    
    # 步骤 1: 从各信源采集原始数据
    raw_items = []
    raw_items.extend(collect_from_govcn(window_start, window_end))
    raw_items.extend(collect_from_mfa(window_start, window_end))
    
    print(f"\n📊 共采集 {len(raw_items)} 条候选数据")
    
    # 步骤 2: 分类和结构化
    structured = classify_and_structure(raw_items)
    
    personnel_count = len(structured["personnel"])
    consuls_count = len(structured["consuls"])
    visits_count = len(structured["visits"])
    uscn_count = len(structured["us_china"])
    
    print(f"  人事变化: {personnel_count} | 总领事: {consuls_count} | 访华: {visits_count} | 中美互动: {uscn_count}")
    
    # 步骤 3: 合并到已有数据
    merged = merge_with_existing(structured, DATA_FILE)
    
    # 步骤 4: 更新元数据
    merged["meta"] = {
        "version": "1.0.0",
        "generated": NOW.isoformat(),
        "window_start": window_start,
        "window_end": window_end,
        "collection_method": "auto + agent",
        "candidate_count": len(raw_items),
    }
    
    # 生成 data_summary
    parts = {}
    if personnel_count: parts["外交代表人事变化"] = f"{personnel_count}项"
    if consuls_count: parts["驻沪穗总领事人事"] = f"{consuls_count}项"
    if visits_count: parts["高级官员访华"] = f"{visits_count}项"
    if uscn_count: parts["中美互动"] = f"{uscn_count}项"
    merged["data_summary"] = parts
    
    # 写入文件
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    
    total = sum([personnel_count, consuls_count, visits_count, uscn_count])
    print(f"\n✅ 数据已写入: {DATA_FILE}")
    print(f"   总事件: {total}（需 agent 核验补强后正式收录）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
