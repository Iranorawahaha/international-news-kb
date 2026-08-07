#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_china.py — 国内新闻看板 · 权威信源抓取器 v4（Ira 信息看板体系）

数据源（国家级权威 + 严格过滤）：
  1. 中国政府网·要闻      https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json
  2. 中国政府网·最新政策  https://www.gov.cn/zhengce/zuixin/ZUIXINZHENGCE.json
  3. 央视新闻             https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/china_1.jsonp
  4. 人民日报             http://paper.people.com.cn/rmrb/pc/layout/{YYYYMM}/dd 头版+要闻版
  5. 外交部官网           https://www.mfa.gov.cn（发言人记者会 / 领导人活动 / 驻外使领馆动态）
  6. 部委官网             https://www.mofcom.gov.cn（商务部） / www.ndrc.gov.cn（发改委） / www.cac.gov.cn（网信办）

v4 改进（2026-08-04 用户反馈）：
  - ❌ 彻底删除凤凰新闻信源（不再收集）
  - ✅ 新增"使领馆动向"类别（最高优先级）：
      · 大使离到任/递交国书（外交部官网权威渠道，每日抓取）
      · 外交部召见/约见/谈话等与驻华使馆互动（中等）
      · 使馆参与/牵头的大型文化活动（最次）
  - ✅ 加强重要会议筛选：剔除"（人民论坛）"等报纸评论栏目标记（非真正会议）
  - ✅ 人事任免补强：高层任免 + 高官反贪腐（审查调查/双开/落马等）
  - ✅ 部委动态拓展：商务部/发改委/网信办官网（通报/要闻/答记者问）
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
# v4: 外交部官网（使领馆动向核心信源）
MFA_HOME = "https://www.mfa.gov.cn/web/"
MFA_SPOKES = "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/"       # 发言人例行记者会
MFA_LEADER = "https://www.mfa.gov.cn/web/wjdt_674879/gjldrhd_674881/"     # 领导人活动（含任免大使/递交国书）
MFA_DSRM = "https://www.mfa.gov.cn/web/wjdt_674879/dsrm_674893/"          # 大使任免（驻华大使离到任权威栏目）
# v4: 关注部委官网
MOFCOM_NEWS = "https://www.mofcom.gov.cn/xwfb/"                            # 商务部·新闻发布
NDRC_NEWS = "https://www.ndrc.gov.cn/xwdt/"                                # 发改委·新闻动态
CAC_NEWS = "https://www.cac.gov.cn/"                                       # 网信办·要闻

# 信源权威优先级（去重时保留优先级高的）
SOURCE_PRIORITY = {
    "中国政府网·要闻": 1, "中国政府网·最新政策": 1, "央视新闻": 2, "人民日报": 3,
    "外交部": 2, "商务部": 3, "国家发改委": 3, "网信办": 3,
}

# ============ 领导人名单 ============
XI_KEYWORDS = ["习近平", "国家主席", "中央军委主席", "总书记"]
PSC_KEYWORDS = ["李强", "赵乐际", "王沪宁", "蔡奇", "丁薛祥", "李希",
                "何立峰", "王毅", "李干杰", "张国清", "陈文清", "刘国中", "石泰峰",
                "黄坤明", "陈吉宁", "袁家军", "尹力", "马兴瑞", "信长星", "梁言顺", "王君正",
                "李书磊", "穆虹", "秦刚", "刘建超", "李尚福", "王小洪", "张又侠", "何卫东",
                "张春贤", "王东明", "彭清华", "郑建邦", "郝明金", "蔡达峰", "何维", "武维华",
                "铁凝", "雪克来提", "洛桑江村", "国务院副总理", "国务院国务委员", "政治局委员",
                # V5 扩展：更多高层职务/活动信号
                "国务院总理", "全国政协", "全国人大", "中央军委", "国务委员",
                "在福建调研", "在山东调研", "在安徽调研", "在云南调研", "在河北调研",
                "在江苏调研", "在内蒙古调研", "在四川调研", "在甘肃调研", "在陕西调研",
                "在新疆调研", "在西藏调研", "在青海调研", "在江西调研", "在湖南调研",
                "主持召开", "出席会议", "会见", "同…会谈", "致贺信", "作出批示",
                "对…作出重要指示", "会见出席", "应约", "与…通电话", "通电话",
]
# 部委关键词（V5扩展：教育部/科技部/财政部/人社部/自然资源部/住建部/央行）
BUWEI_KEYWORDS = [
    # 用户点名部委（直接出现在标题中）
    "工信部", "工业和信息化部", "网信办", "国家网信办", "中央网信办", "发改委",
    "国家发展改革委", "发展改革委", "国办", "国务院办公厅", "中办", "中共中央办公厅",
    "商务部", "外交部", "外交部发言人",
    # V5 新增部委
    "教育部", "科技部", "财政部", "人社部", "人力资源社会保障部",
    "自然资源部", "住建部", "住房城乡建设部", "交通运输部", "水利部",
    "农业农村部", "卫健委", "国家卫健委", "文旅部", "文化和旅游部",
    "央行", "中国人民银行", "证监会", "银保监会", "国家金融监管总局",
    # 部委特定行动
    "对外贸易", "国家安全调查", "反倾销", "反补贴", "保障措施调查",
    "中美贸易", "贸易战", "经济制裁", "实体清单", "出口管制", "关税",
    # 政策/监管动作（V5扩展）
    "AI治理", "人工智能治理", "AI监管", "数据安全法", "网络安全审查",
    "发文", "印发", "出台", "发布…通知", "公布…办法", "修订…规定",
    # 部委行动信号
    "部署", "调度", "约谈", "通报", "督导", "专项整治", "集中整治",
    "暗访", "巡检", "联合检查", "约见企业", "答记者问", "新闻发布会",
]

# 使领馆关键词（保持不变）
EMBASSY_KEYWORDS = [
    "递交国书", "接受国书", "新任驻华大使", "驻华大使", "递交国书副本", "国书副本",
    "驻华大使到任", "驻华大使离任",
    "驻华使馆", "驻华使团", "驻华使节", "使团办", "外交部礼宾司", "召见", "约见",
    "驻华使馆文化", "驻华使团", "驻华外交官",
]

# 人事任免 + 反贪腐关键词（V5 扩展）
PERSONNEL_KEYWORDS = [
    "任免", "任命", "免去", "担任", "任命决定", "提请任命", "代市长", "代省长", "代县长",
    "履新", "出任", "接任", "当选", "辞去", "代理", "任国家工作人员",
    # 反贪腐
    "接受审查调查", "审查调查", "纪律审查", "监察调查", "双开", "开除党籍",
    "开除公职", "违纪违法", "涉嫌严重违纪", "落马", "被查", "留置", "立案审查",
    # V5 扩展：职务变动信号
    "调任", "转任", "交流任职", "不再担任", "另有任用", "任前公示",
    "拟任", "提拔", "晋升", "升任", "兼任", "挂职",
    # 机构任命
    "国务院任免", "中共中央决定", "组织部", "任免通知", "职务任免",
]
# 重要会议关键词（V5 扩展：增加实际会议类型，降低误杀）
MEETING_KEYWORDS = [
    "座谈会", "研讨会", "集体学习", "中央经济工作会议",
    "全国两会", "人代会", "政协会", "传达学习", "峰会", "联席会议", "领导小组会议",
    "全会", "常务会议", "国务院会议", "政治局会议",
    # V5 扩展
    "国务院常务会议", "中央政治局", "政治局常委", "深改委", "改革委",
    "中央财经委", "中央军委", "中央外事", "中央农村工作", "中央统战",
    "全国政协常委会", "全国人大常委", "委员长会议", "主席会议",
    "国务院召开", "国务院部署", "国务院发布", "国务院印发",
    "部际联席会议", "协调机制", "推进会", "动员部署", "总结表彰",
    "新闻发布会", "国新办", "政府工作报告", "预算报告",
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
    # V4.1: AI/科技产业竞争话题（不归部委的行业新闻默认归经贸）
    "AI", "人工智能", "大模型", "芯片", "半导体", "信息通信", "5G", "6G",
    "集成电路", "算力", "霸榜", "排名", "竞争力", "市场份额",
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
    # V4.1: 用户反馈——非实事新闻（采访总结/微视角/个人叙事）
    "联合采访", "微视角", "亲历者说", "记者手记", "蹲点日记",
    "讲述", "回忆", "往事", "人物专访", "口述", "亲历",
    # V4.2: 用户反馈——
    #   "学习习近平总书记关于..." → 外围学习活动，非元首动态
    #   （注意：fetch 阶段可能截断标题，缩短匹配词作为兜底）
    "学习习近平总书记关于", "学习习近平",
    #   地方微观服务（"个人身后金融事"）
    "身后金融事", "个人身后", "一站式查询系统",
    #   驻外大使拜会外国议长/出席学术活动（非重点国，不重要）
    "议会议长",  # 命中"驻X国大使拜会X国议会议长"
    "中国经济学会",  # 命中"驻爱尔兰大使出席全欧中国经济学会"
]

# v4: 报纸评论栏目标记（非真正会议/新闻，剔除）
COMMENT_COLUMN_MARKS = [
    "（人民论坛）", "（人民时评）", "（评论员观察）", "（今日谈）", "（思想纵横）",
    "（国际论坛）", "（钟声）", "（望海楼）", "（国纪平）", "（仲音）",
    "人民论坛", "人民时评", "评论员观察",
    # V4.1: 用户反馈——非实事新闻栏目（个人视角/采访总结/微观视角）
    "（亲历者说）", "（高质量发展微视角）", "（一线调研）", "（蹲点日记）",
    # V4.2: 用户反馈——新闻回顾/评论专栏（非实事）
    "时习之", "时习之丨",
]

# 分类规则（按优先级顺序，v4 重构：使领馆动向置顶）
CATEGORY_RULES = [
    # 1. 元首动态：仅习近平相关
    ("元首动态", XI_KEYWORDS),
    # 2. 高层动态：政治局常委 + 政治局委员
    ("高层动态", PSC_KEYWORDS),
    # 3. 使领馆动向（v4 新增，用户最高优先级）
    ("使领馆动向", EMBASSY_KEYWORDS),
    # 4. 重要会议（v4：剔除"论坛"类评论栏目标记，见 make_item 前置过滤）
    ("重要会议", MEETING_KEYWORDS),
    # 5. 人事任免（中央到地方高层 + 反贪腐）
    ("人事任免", PERSONNEL_KEYWORDS),
    # 6. 部委动态（工信/网信/发改/国办/中办/商务/外交等）
    ("部委动态", BUWEI_KEYWORDS),
    # 7. 政策发布
    ("政策发布", ["印发", "通知", "规划", "意见", "方案", "条例", "规定", "办法", "决定", "批复", "白皮书"]),
    # 8. 经贸动向
    ("经贸动向", ECONOMY_KEYWORDS),
]

CATEGORY_ICONS = {
    "元首动态": "👑", "高层动态": "🧭", "使领馆动向": "🕊️", "重要会议": "🏛", "人事任免": "📋",
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


def is_comment_column(title):
    """v4: 报纸评论栏目标记（人民论坛等）→ 剔除，非真正会议/新闻"""
    t = title or ""
    return any(mark in t for mark in COMMENT_COLUMN_MARKS)


def classify(title):
    # V4.2: "会议"不匹配"议会"（驻外大使拜会议长 ≠ 重要会议）
    for cat, kws in CATEGORY_RULES:
        for kw in kws:
            if kw in title:
                if cat == "重要会议" and "议会" in title:
                    continue  # 跳过：驻X大使拜会议长 不是国内重大会议
                return cat
    return None  # 未匹配任何关注分类 → 丢弃


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
            if cat == "使领馆动向":
                # 递交国书/大使离到任最高，召见次之，文化活动最低
                if any(k in title for k in ["递交国书", "接受国书", "新任驻华大使", "大使离任", "大使到任", "任免大使", "驻外大使"]):
                    score = 90
                elif any(k in title for k in ["召见", "约见", "照会", "交涉"]):
                    score = 82
                else:
                    score = 70
            elif cat == "重要会议":
                score = 88
            elif cat == "人事任免":
                if any(k in title for k in ["审查调查", "双开", "开除党籍", "落马", "被查", "违纪违法"]):
                    score = 86  # 反贪腐
                else:
                    score = 85
            elif cat == "部委动态":
                # V4.1: 重要部委行动加权——对外贸易调查/反倾销/反补贴/反制等商务部重大执法 → 88分
                if any(k in title for k in ["对外贸易", "国家安全调查", "反倾销", "反补贴", "保障措施调查", "实体清单", "出口管制", "反制裁", "反制措施", "反制"]):
                    score = 88
                else:
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
    # v4: 剔除报纸评论栏目标记（人民论坛/人民时评等非新闻）
    if is_comment_column(title):
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
        cutoff = (NOW - timedelta(days=6)).strftime("%Y-%m-%d")
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
        cutoff = (NOW - timedelta(days=6)).strftime("%Y-%m-%d")
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


# ==================== v4 新增：外交部官网（使领馆动向核心信源） ====================
def extract_date_from_url(url):
    """从 URL 提取日期：t20260731_xxx.shtml → 2026-07-31；/2026-07/31/ → 2026-07-31；art/2026/xxx 兜底"""
    m = re.search(r"t(20\d{2})(\d{2})(\d{2})_", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.search(r"/(20\d{2})/(\d{2})/(\d{2})/", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.search(r"/(20\d{2})-(\d{2})/(\d{2})/", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def parse_mfa_list(h, base_url, source_name, url_filters=("shtml",), title_filters=()):
    """通用解析外交部/部委官网列表页（<a href> + 标题）"""
    items = []
    cutoff = (NOW - timedelta(days=6)).strftime("%Y-%m-%d")
    seen_urls = set()
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', h, re.S):
        u, t = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
        t = re.sub(r"\s+", " ", t).strip()
        if not t or len(t) < 10:
            continue
        if not any(f in u for f in url_filters):
            continue
        if any(f in t for f in title_filters):
            continue
        if u.startswith("//"):
            u = "https:" + u
        elif not u.startswith("http"):
            u = base_url.rstrip("/") + "/" + u.lstrip("./")
        # 规范化 URL（去锚点）
        u = u.split("#")[0]
        if u in seen_urls:
            continue
        seen_urls.add(u)
        d = extract_date_from_url(u)
        if d is None:
            # 标题里可能带日期（2026年7月31日 或 （2026-07-31））
            md = re.search(r"（(20\d{2}-\d{2}-\d{2})）", t)
            if md:
                d = md.group(1)
            else:
                md = re.search(r"(20\d{2})年(\d{1,2})月(\d{1,2})日", t)
                if md:
                    d = f"{md.group(1)}-{int(md.group(2)):02d}-{int(md.group(3)):02d}"
        if d is None or d < cutoff:
            continue
        item = make_item(t, u, d, source_name)
        if item:
            items.append(item)
    return items


def fetch_mfa():
    """外交部官网：大使任免 + 发言人记者会 + 领导人活动 + 首页驻外使领馆动态"""
    items = []
    # 0. 大使任免栏目（最高优先级：驻华大使离到任/递交国书）
    try:
        h = fetch(MFA_DSRM, headers={"Referer": "https://www.mfa.gov.cn/"})
        it = parse_mfa_list(h, "https://www.mfa.gov.cn/web/wjdt_674879/dsrm_674893",
                            "外交部", url_filters=("shtml",))
        items += it
        print(f"  ✅ 外交部·大使任免: 采纳 {len(it)} 条")
    except Exception as e:
        print(f"  ❌ 外交部·大使任免: {e}")

    # 1. 发言人例行记者会（部委动态/使领馆互动）
    try:
        h = fetch(MFA_SPOKES, headers={"Referer": "https://www.mfa.gov.cn/"})
        it = parse_mfa_list(h, "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889",
                            "外交部", url_filters=("shtml",))
        items += it
        print(f"  ✅ 外交部·发言人记者会: 采纳 {len(it)} 条")
    except Exception as e:
        print(f"  ❌ 外交部·发言人记者会: {e}")

    # 2. 领导人活动（含"国家主席习近平任免驻外大使"/递交国书等）
    try:
        h = fetch(MFA_LEADER, headers={"Referer": "https://www.mfa.gov.cn/"})
        it = parse_mfa_list(h, "https://www.mfa.gov.cn/web/wjdt_674879/gjldrhd_674881",
                            "外交部", url_filters=("shtml",))
        items += it
        print(f"  ✅ 外交部·领导人活动: 采纳 {len(it)} 条")
    except Exception as e:
        print(f"  ❌ 外交部·领导人活动: {e}")

    # 3. 外交部首页（驻外使领馆动态：驻X国大使...）
    try:
        h = fetch(MFA_HOME, headers={"Referer": "https://www.mfa.gov.cn/"})
        it = parse_mfa_list(h, "https://www.mfa.gov.cn/web",
                            "外交部", url_filters=("shtml",))
        items += it
        print(f"  ✅ 外交部·首页/驻外动态: 采纳 {len(it)} 条")
    except Exception as e:
        print(f"  ❌ 外交部·首页: {e}")

    # 抓摘要（限量）
    print(f"  📥 外交部共 {len(items)} 条 → 抓取摘要...")
    for it in items[:25]:
        if not it.get("summary"):
            it["summary"] = extract_summary_from_url(it["url"])
    return items


# ==================== v4 新增：关注部委官网 ====================
def fetch_buwei_sites():
    """商务部 / 发改委 / 网信办 官网（通报/要闻/答记者问）"""
    items = []
    sites = [
        ("商务部", MOFCOM_NEWS, "https://www.mofcom.gov.cn/xwfb", ("art", "html")),
        ("国家发改委", NDRC_NEWS, "https://www.ndrc.gov.cn/xwdt", ("html",)),
        ("网信办", CAC_NEWS, "https://www.cac.gov.cn", ("shtml", "html", "htm")),
    ]
    for src, url, base, filters in sites:
        try:
            h = fetch(url, headers={"Referer": "https://www.gov.cn/"})
            it = parse_mfa_list(h, base, src, url_filters=filters)
            items += it
            print(f"  ✅ {src}: 采纳 {len(it)} 条")
        except Exception as e:
            print(f"  ❌ {src}: {e}")

    print(f"  📥 部委官网共 {len(items)} 条 → 抓取摘要...")
    for it in items[:30]:
        if not it.get("summary"):
            it["summary"] = extract_summary_from_url(it["url"])
    return items


# ==================== v4.1：微信公众号搜索（外交部使团事务办公室）====================
def fetch_wechat():
    """微信公众号搜索：外交部使团事务办公室（外国驻华大使离到任/递交国书核心信源）"""
    items = []
    cutoff = (NOW - timedelta(days=6)).strftime("%Y-%m-%d")
    keywords = [
        "外交部使团事务办公室",  # 核心权威信源公众号
    ]
    import subprocess
    script = os.path.join(BASE_DIR, "..", ".workbuddy", "skills", "wechat-article-search", "scripts", "search_wechat.js")
    # 调整路径
    if not os.path.exists(script):
        script = os.path.join(os.path.expanduser("~"), ".workbuddy", "skills", "wechat-article-search", "scripts", "search_wechat.js")
    if not os.path.exists(script):
        print("  ⚠️  微信搜索脚本未找到，跳过")
        return items

    node = "/Users/xiaoxiao/.workbuddy/binaries/node/versions/22.22.2/bin/node"
    node_modules = os.path.join(os.path.expanduser("~"), ".workbuddy", "skills", "wechat-article-search", "node_modules")
    seen_urls = set()

    for kw in keywords:
        try:
            r = subprocess.run(
                [node, script, kw, "-n", "10"],
                capture_output=True, text=True, timeout=30,
                cwd=os.path.dirname(script),
                env={**dict(os.environ), "NODE_PATH": node_modules}
            )
            data = json.loads(r.stdout) if r.returncode == 0 else None
            if not data:
                continue
            for art in data.get("articles", []):
                t = (art.get("title") or "").strip()
                s = (art.get("summary") or "").strip()
                d_str = (art.get("datetime") or "")[:10]
                src_name = art.get("source", "外交部使团事务办公室")
                u = (art.get("url") or "").strip()
                if not t or len(t) < 8 or d_str < cutoff:
                    continue
                if u in seen_urls:
                    continue
                seen_urls.add(u)
                # 强制来源过滤：只采纳"外交部使团事务办公室"公众号（排除自媒体）
                if src_name != "外交部使团事务办公室":
                    continue
                # 该公众号所有文章直接归入"使领馆动向"（用户指定）
                item = make_item(t, u, d_str, src_name, summary=s[:100] + ("…" if len(s) > 100 else ""))
                if item:
                    item["category"] = "使领馆动向"
                    # 调整重要度：驻华大使相关 = 90，一般活动 = 75
                    if any(k in t + s for k in ["递交国书", "国书副本", "新任大使", "离任", "到任", "驻华大使"]):
                        item["priority_score"] = 90
                    else:
                        item["priority_score"] = 75
                    items.append(item)
            print(f"  🔍 微信搜索「{kw[:20]}」→ {len(items)} 条")
        except Exception as e:
            print(f"  ⚠️  微信搜索「{kw[:20]}」失败: {e}")
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
    print(f"🕗 {NOW.strftime('%Y-%m-%d %H:%M')} 北京时间 · 国内新闻抓取开始（v4）\n")

    all_items = []
    all_items += fetch_gov(GOV_YAOWEN, "中国政府网·要闻")
    all_items += fetch_gov(GOV_ZHENGCE, "中国政府网·最新政策")
    all_items += fetch_cctv()
    all_items += fetch_rmrb()
    all_items += fetch_mfa()
    all_items += fetch_buwei_sites()
    all_items += fetch_wechat()

    # 跨信源去重：标题相似（规范化后）时保留权威优先级高的
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
    cutoff = (NOW - timedelta(days=6)).strftime("%Y-%m-%d")
    archive = {d: v for d, v in archive.items() if d >= cutoff}

    dates = sorted(archive.keys(), reverse=True)
    total = sum(len(v) for v in archive.values())
    today = NOW.strftime("%Y-%m-%d")

    per_cat = {}
    for d in dates:
        for it in archive[d]:
            per_cat[it["category"]] = per_cat.get(it["category"], 0) + 1

    data = {
        "version": "4.0",
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

    print(f"\n📊 国内新闻抓取完成（v4）:")
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
