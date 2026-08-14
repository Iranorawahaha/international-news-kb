#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_china.py — 国内重大新闻看板 · 权威信源抓取器 v5（Ira 信息看板体系）

数据源（国家级权威 + 严格过滤，聚焦7大类别）：
  1. 中国政府网·要闻      https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json
  2. 中国政府网·最新政策  https://www.gov.cn/zhengce/zuixin/ZUIXINZHENGCE.json
  3. 央视新闻             https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/china_1.jsonp
  4. 人民日报             http://paper.people.com.cn/rmrb/pc/layout/{YYYYMM}/dd 头版+要闻版
  5. 外交部官网           https://www.mfa.gov.cn（发言人记者会 / 领导人活动）
  6. 部委官网             https://www.mofcom.gov.cn（商务部）/ www.ndrc.gov.cn（发改委）
                          www.cac.gov.cn（网信办）/ www.miit.gov.cn（工信部）
  7. 联合早报中文网       https://www.zaobao.com/news/china（人事/高层补充信源）

v5 改进（2026-08-10 用户需求驱动）：
  - ❌ 删除「使领馆动向」类别及所有相关代码（大使任免/递交国书/微信公众号外交部使团办）
  - ✅ 分类从 8 类精简为 7 类
  - ✅ 部委动态聚焦 5 部委：网信办/工信部/发改委/商务部/外交部
  - ✅ 加强反贪腐/人事任免关键词
  - ✅ 新增黑名单：评论回顾/微观叙事类关键词
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
# v5.1: 外交部官网 — 外交动态全栏目监控
MFA_SPOKES = "https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/"       # 例行记者会（低优先级）
MFA_LEADER = "https://www.mfa.gov.cn/web/wjdt_674879/gjldrhd_674881/"     # 领导人活动（高优先级）
# V5.2: 外交部全子栏目
MFA_WSRC   = "https://www.mfa.gov.cn/web/wjdt_674879/wsrc_674883/"        # 外事日程（高优先级）
MFA_DSRM   = "https://www.mfa.gov.cn/web/wjdt_674879/dsrm_674893/"        # 大使任免（高优先级）
MFA_BLDHD  = "https://www.mfa.gov.cn/web/wjdt_674879/bldhd_674885/"       # 部领导活动（高优先级）
MFA_ZCJD   = "https://www.mfa.gov.cn/web/wjdt_674879/zcjd_674887/"        # 政策解读（高优先级）
MFA_YWDT   = "https://www.mfa.gov.cn/web/wjdt_674879/ywdt_674891/"        # 业务动态（低优先级）
# V5.1: 商务部新版URL（网站已改版）
MOFCOM_XWFB = "https://www.mofcom.gov.cn/xwfb/"                            # 商务部·新闻发布（新版）
NDRC_NEWS = "https://www.ndrc.gov.cn/xwdt/"                                # 发改委·新闻动态
CAC_NEWS = "https://www.cac.gov.cn/"                                       # 网信办·要闻
MIIT_HOME = "https://www.miit.gov.cn/"                                     # 工信部·首页（全量新闻）
# V5: 联合早报中文网 — 人事任免/中国政治动态权威海外信源
ZAOBAO_CHINA = "https://www.zaobao.com/news/china"

# 信源权威优先级（去重时保留优先级高的）
SOURCE_PRIORITY = {
    "中国政府网·要闻": 1, "中国政府网·最新政策": 1, "央视新闻": 2, "人民日报": 3,
    "商务部": 3, "国家发改委": 3, "网信办": 3, "工信部": 3,
    "联合早报": 4,
}

# ============ 领导人名单 ============
XI_KEYWORDS = ["习近平", "国家主席", "中央军委主席", "总书记",
               "元首外交",  # V5.1: 捕获"中国元首外交的世界情怀"等系列报道
]
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
                # V5.1: 高层活动关键信号
                "党中央国务院", "北戴河", "国务院成立", "国务院部署",
]
# 部委关键词（V5 聚焦：网信/工信/发改/商务/外交 5部委 + 国办/中办）
BUWEI_KEYWORDS = [
    # 1. 部委名称（直接出现即命中）
    "工信部", "工业和信息化部", "网信办", "国家网信办", "中央网信办", "发改委",
    "国家发展改革委", "发展改革委", "国办", "国务院办公厅", "中办", "中共中央办公厅",
    "商务部", "外交部", "外交部发言人",
    # 2. 网信办特定动作
    "数据安全", "AI治理", "人工智能治理", "AI监管",
    "网络安全审查", "算法推荐", "个人信息保护", "数据出境",
    # 3. 工信部特定动作
    "5G", "6G", "智能制造", "工业互联网", "新能源汽车",
    "信息通信", "集成电路", "数字化转型",
    # 4. 商务部特定动作
    "对外贸易", "反倾销", "反补贴", "保障措施调查", "贸易救济",
    "外资准入", "负面清单", "出口管制",
    # 5. 部委通用行动信号
    "约谈", "通报", "答记者问", "新闻发布会",
    # 6. 重大产业/科技政策（归部委）
    "算力网", "算力节点", "全国算力", "一体化算力", "东数西算",
    "算力调度", "智算中心", "超算中心", "算力枢纽", "算力集群",
    # 7. 网信/工信监管动作
    "专项整治", "集中整治", "联合检查",
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
    # V5.1: 联合早报等海外媒体表述
    "被罢", "罢免",
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
    "自贸区", "RCEP", "WTO", "中美经贸", "中美贸易", "营商环境",
    "宏观政策", "政策发力", "扩内需", "促消费", "稳增长", "保供稳价",
    "经济增长", "经济工作", "经济形势", "新质生产力",
    # V5.1: 移除"高质量发展"（过于宽泛，匹配到很多非经贸标题）
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
    # V5: 过滤评论回顾类——非时事新闻
    "人民情怀", "关切事", "专题片丨", "纪实丨", "系列述评",
    "述评之一", "述评之二", "述评之三", "述评之四",
    "思想理论品格", "理论品格",
    "治国理政纪实", "新发展理念",
    # V5.3: 微视频/总书记心系等微观叙事→不予收录
    "微视频", "总书记心系", "总书记的", "枝叶总关情", "时政微镜头",
    "温暖的回响", "心系", "微镜头", "vlog",
    # V5.4: 纪事/读画等非新闻文体→不予收录（侧记不在此列，如北戴河侧记是重大事项）
    "纪事", "读画", "侧写",
    # V5.4: 纯外宣/外国政府发言人（与中国无关的域外事务）→ 不收录
    "伊朗外交部发言人", "朝鲜外务省", "古巴外交部", "委内瑞拉外交部", "叙利亚外交部",
    "经济思想", "党建思想", "外交思想", "法治思想", "生态文明思想",
    "强军思想", "破浪前行", "行稳致远",
    "夯实基础——习近平总书记引领",  # 综述评论标题
    #   地方微观服务（"个人身后金融事"）
    "身后金融事", "个人身后", "一站式查询系统",
]

# V5.3: 联合早报微观/地方新闻过滤（主要作为人事任免补充，其他需重大事件）
ZAOBAO_MICRO_PATTERNS = [
    # 大学/医院层级的人事/案件 → 太微观
    ("大学", "院长"), ("大学", "被查"), ("医院", "被查"), ("医院", "院长"),
    # 地方城管/执法事件
    "城管", "协管员", "天桥打人",
    # 台湾地方政治
    ("台湾", "经济部长"), ("台湾", "电价"), ("台湾", "民生"),
    "台湾经济部长",
    # 地方个案（非全国性）
    ("南华大学",),
]

def is_zaobao_micro(title):
    """检查联合早报标题是否为微观/地方新闻，不应收录"""
    for pat in ZAOBAO_MICRO_PATTERNS:
        if isinstance(pat, tuple):
            if all(p in title for p in pat):
                return True
        elif pat in title:
            return True
    return False

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

# 分类规则（按优先级顺序，v5 重构：7类）
CATEGORY_RULES = [
    # 1. 元首动态：仅习近平相关
    ("元首动态", XI_KEYWORDS),
    # 2. 高层动态：政治局常委 + 政治局委员
    ("高层动态", PSC_KEYWORDS),
    # 3. 重要会议（剔除"论坛"类评论栏目标记，见 make_item 前置过滤）
    ("重要会议", MEETING_KEYWORDS),
    # 4. 人事任免（中央到地方高层 + 反贪腐）
    ("人事任免", PERSONNEL_KEYWORDS),
    # 5. 部委动态（聚焦网信/工信/发改/商务/外交5部委）
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


def is_comment_column(title):
    """v4: 报纸评论栏目标记（人民论坛等）→ 剔除，非真正会议/新闻"""
    t = title or ""
    return any(mark in t for mark in COMMENT_COLUMN_MARKS)


def classify(title):
    # V4.2: "会议"不匹配"议会"（非国内重要会议）
    for cat, kws in CATEGORY_RULES:
        for kw in kws:
            if kw in title:
                if cat == "重要会议" and "议会" in title:
                    continue  # 跳过：非国内重要会议
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
            if cat == "重要会议":
                score = 88
            elif cat == "人事任免":
                if any(k in title for k in ["审查调查", "双开", "开除党籍", "落马", "被查", "违纪违法"]):
                    score = 87  # 反贪腐
                else:
                    score = 86
            elif cat == "部委动态":
                # V5.3: 重大执法行动加权 → 88分
                if any(k in title for k in ["对外贸易", "国家安全调查", "反倾销", "反补贴", "保障措施调查", "实体清单", "出口管制", "反制裁", "反制措施", "反制"]):
                    score = 88
                else:
                    score = 85
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
    # V5.3: 联合早报微观/地方新闻过滤
    if source == "联合早报" and is_zaobao_micro(title):
        return None
    cat = classify(title)
    if cat is None:
        return None  # 未命中任何关注分类 → 丢弃
    score = assess_importance(title, cat)
    # V5.3: 中国政府网·要闻 — 无论何类目，均取最高分一档
    GOV_BOOST = {
        "元首动态": 100, "高层动态": 95, "重要会议": 88,
        "人事任免": 87, "部委动态": 88, "政策发布": 80, "经贸动向": 85,
    }
    if source == "中国政府网·要闻" and cat in GOV_BOOST:
        score = max(score, GOV_BOOST[cat])
    return {
        "title": title,
        "url": url,
        "date": date,
        "source": source,
        "category": cat,
        "priority_score": score,
        "is_summit_level": is_summit(title),
        "summary": (summary or "").strip(),
        "collectedAt": NOW.strftime("%Y-%m-%d %H:%M:%S"),
    }


def fetch_gov(url, source_name, max_age_days=7):
    """中国政府网 JSON 接口 + 抓正文摘要"""
    items = []
    try:
        data = json.loads(fetch(url))
        lst = data if isinstance(data, list) else data.get("listArrP") or data.get("data") or []
        cutoff = (NOW - timedelta(days=max_age_days - 1)).strftime("%Y-%m-%d")
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
        age_label = f"近{max_age_days}天"
        print(f"  ✅ {source_name}: {len(lst)} 条({age_label} {len(items)} 条) → 抓取摘要...")
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


# ==================== 外交部/部委官网通用解析工具 ====================
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
    """通用解析外交部/部委官网列表页（<a href> + 标题）
    url_filters: URL 必须包含的关键词，设为空元组 () 则匹配所有链接
    """
    items = []
    cutoff = (NOW - timedelta(days=6)).strftime("%Y-%m-%d")
    seen_urls = set()
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', h, re.S):
        u, t = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
        t = re.sub(r"\s+", " ", t).strip()
        if not t or len(t) < 10:
            continue
        if url_filters and not any(f in u for f in url_filters):
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
    """外交部官网 — 外交动态全栏目监控（v5.2）
    
    高优先级：领导人活动 / 外事日程 / 部领导活动 / 政策解读 / 大使任免
    低优先级：业务动态 / 例行记者会
    不予收录：驻外报道
    """
    items = []
    # 驻外/使馆导航过滤词
    EMBASSY_FILTERS = ("常驻", "代表团", "办事处", "代办处", "联合国", "事务办公室")
    
    # 定义所有子栏目: (显示名, URL, 优先级)
    sections = [
        # --- 高优先级 ---
        ("领导人活动", MFA_LEADER, "high"),
        ("外事日程",   MFA_WSRC,   "high"),
        ("部领导活动", MFA_BLDHD,  "high"),
        ("政策解读",   MFA_ZCJD,   "high"),
        ("大使任免",   MFA_DSRM,   "high"),
        # --- 低优先级 ---
        ("业务动态",   MFA_YWDT,   "low"),
        ("例行记者会", MFA_SPOKES, "low"),
    ]
    
    high_count = 0
    low_count = 0
    
    for name, url, priority in sections:
        try:
            h = fetch(url, headers={"Referer": "https://www.mfa.gov.cn/"})
            # 提取URL的目录部分作为base，用于拼接相对链接
            base_parts = url.rstrip("/").rsplit("/", 1)
            base = base_parts[0] + "/" if len(base_parts) > 1 else url
            
            it = parse_mfa_list(h, base, "外交部", 
                                url_filters=("shtml",),
                                title_filters=EMBASSY_FILTERS)
            items += it
            
            if priority == "high":
                high_count += len(it)
            else:
                low_count += len(it)
            print(f"  {'🔴' if priority == 'high' else '🟡'} 外交部·{name}: 采纳 {len(it)} 条")
        except Exception as e:
            print(f"  ❌ 外交部·{name}: {e}")
    
    # 抓摘要（限量）
    total = len(items)
    print(f"  📥 外交部共 {total} 条（高优先 {high_count} | 低优先 {low_count}）→ 抓取摘要...")
    for it in items[:25]:
        if not it.get("summary"):
            it["summary"] = extract_summary_from_url(it["url"])
    return items


# ==================== v5.1: 部委官网（新版商务部 + 工信部首页） ====================
def extract_date_from_mofcom_article(url):
    """从商务部新版文章页提取发布日期（meta publishdate）"""
    try:
        h = fetch(url, timeout=6)
        dm = re.search(r'<meta[^>]+name="publishdate"[^>]+content="(\d{4}-\d{2}-\d{2})', h, re.I)
        if not dm:
            dm = re.search(r'<meta[^>]+name="pubdate"[^>]+content="(\d{4}-\d{2}-\d{2})', h, re.I)
        return dm.group(1) if dm else None
    except Exception:
        return None


def fetch_mofcom_v2():
    """商务部·新闻发布（6个子栏目全量监控，日期从meta提取）
    
    覆盖栏目：
      /xwfb/ldrhd/    — 领导人活动
      /xwfb/bldhd/    — 部领导活动
      /xwfb/rcxwfb/   — 日常新闻发布
      /xwfb/xwfyrth/  — 新闻发言人谈话
      /xwfb/sjfzrfb/  — 司局负责人发布
      /xwfb/ztxwfbh/  — 专题新闻发布会
      /xwfb/lxxwfbh/  — 例行新闻发布会
    
    注意：首页 /xwfb/index.html 已聚合全部子栏目，无需逐个抓取。
    """
    items = []
    MOFCOM_CATEGORIES = {
        "ldrhd": "领导人活动", "bldhd": "部领导活动",
        "rcxwfb": "日常新闻发布", "xwfyrth": "新闻发言人谈话",
        "sjfzrfb": "司局负责人发布", "ztxwfbh": "专题新闻发布会",
        "lxxwfbh": "例行新闻发布会",
    }
    
    try:
        h = fetch(MOFCOM_XWFB, timeout=12,
                  headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                           "Referer": "https://www.mofcom.gov.cn/",
                           "Accept-Language": "zh-CN,zh;q=0.9"})
        # 匹配所有子栏目的文章链接: /xwfb/<category>/art/<year>/art_<hash>.html
        art_blocks = re.findall(
            r'href="(/xwfb/([^/"]+)/art/\d{4}/[^"]*\.html)"[^>]*>\s*(.{15,200}?)</a>', h)
        seen_urls = set()
        cutoff = (NOW - timedelta(days=6)).strftime("%Y-%m-%d")
        cat_count = {}  # 按栏目统计

        for link, cat, raw_block in art_blocks:
            url = "https://www.mofcom.gov.cn" + link
            if url in seen_urls:
                continue
            seen_urls.add(url)
            title = re.sub(r'<[^>]+>', '', raw_block).strip()
            title = re.sub(r'\s+', ' ', title)
            if not title or len(title) < 10:
                continue
            # 从文章页提取日期
            d = extract_date_from_mofcom_article(url)
            if d is None or d < cutoff:
                continue
            item = make_item(title, url, d, "商务部")
            if item:
                items.append(item)
                cat_count[cat] = cat_count.get(cat, 0) + 1

        # 输出各栏目采纳详情
        cat_detail = " | ".join(f"{MOFCOM_CATEGORIES.get(c, c)}:{n}" for c, n in sorted(cat_count.items()))
        print(f"  ✅ 商务部(V2): 文章块 {len(art_blocks)} → 采纳 {len(items)} 条 [{cat_detail}]")
    except Exception as e:
        print(f"  ❌ 商务部(V2): {e}")
    return items


def fetch_buwei_sites():
    """发改委 / 网信办 / 工信部 官网"""
    items = []
    # 发改委 + 网信办 + 工信部（v5.1: 工信部改用首页，子页面JS渲染无法用requests）
    other_sites = [
        ("国家发改委", NDRC_NEWS, "https://www.ndrc.gov.cn/xwdt"),
        ("网信办", CAC_NEWS, "https://www.cac.gov.cn"),
        ("工信部", MIIT_HOME, "https://www.miit.gov.cn"),
    ]
    for src, url, base in other_sites:
        try:
            h = fetch(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                                      "Referer": base})
            # 网信办 URL 无 shtml/html 扩展名，用空过滤匹配所有链接
            filters = () if src == "网信办" else ("shtml", "html", "htm")
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


# ==================== v5.1 修复：联合早报中文网（自定义解析器 + make_item） ====================
def fetch_zaobao():
    """联合早报中文网——中国政治/人事任免动态"""
    items = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Referer": "https://www.zaobao.com/",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        h = fetch(ZAOBAO_CHINA, headers=headers)
        stories = re.findall(r'href="(/news/china/story\d+-\d+)"[^>]*>(.*?)</a>', h)
        seen = set()
        for link, raw_title in stories:
            url = "https://www.zaobao.com" + link
            title = re.sub(r'<[^>]+>', '', raw_title).strip()
            if not title or len(title) < 10 or title in seen:
                continue
            seen.add(title)
            date_match = re.search(r'story(\d{8})-\d+', link)
            date_str = date_match.group(1) if date_match else NOW.strftime("%Y%m%d")
            date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            # 通过 make_item 走正常分类/评分流程
            item = make_item(title, url, date_fmt, "联合早报")
            if item:
                items.append(item)
        print(f"  ✅ 联合早报·中国: 采纳 {len(items)} 条")
    except Exception as e:
        print(f"  ❌ 联合早报: {e}")
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
    print(f"🕗 {NOW.strftime('%Y-%m-%d %H:%M')} 北京时间 · 国内新闻抓取开始（v5）\n")

    all_items = []
    all_items += fetch_gov(GOV_YAOWEN, "中国政府网·要闻")
    all_items += fetch_gov(GOV_ZHENGCE, "中国政府网·最新政策", max_age_days=14)
    all_items += fetch_cctv()
    all_items += fetch_rmrb()
    all_items += fetch_mfa()
    all_items += fetch_mofcom_v2()
    all_items += fetch_buwei_sites()
    all_items += fetch_zaobao()

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

    # V2.11 归档规则（用户确认）：X日版面 = 本次更新新出现的内容
    # ① 仅 collectedAt=today 的算"本次新抓"（历史缓存内容自动排除）
    # ② URL 已在历史版面的跳过（增量去重，防老内容重复进今日）
    # ③ date 字段保留真实发布日仅用于显示
    archive = {}
    _today_v29 = NOW.strftime("%Y-%m-%d")
    # 读取历史 archive 作为基线（防止全量重抓把 7 天窗口老内容塞进今日）
    _prev_urls = set()
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as _pf:
                _prev_data = json.load(_pf)
            for _pd, _parts in _prev_data.get("archive", {}).items():
                if _pd == _today_v29:
                    continue  # 今日版面今天重建
                archive[_pd] = _parts
                for _pa in _parts:
                    _u = (_pa.get("url") or "").strip().rstrip("/").lower()
                    if _u:
                        _prev_urls.add(_u)
        except Exception as _pe:
            print(f"  ⚠️ 读取历史失败（重建）: {_pe}")

    _new_count = 0
    _dup_skip = 0
    for it in unique:
        _u = (it.get("url") or "").strip().rstrip("/").lower()
        _c = (it.get("collectedAt") or "")[:10]
        # 非今日抓取 → 不进今日版面
        if _c != _today_v29:
            continue
        # 已在历史版面 → 跳过（增量去重）
        if _u and _u in _prev_urls:
            _dup_skip += 1
            continue
        archive.setdefault(_today_v29, []).append(it)
        _new_count += 1
        if _u:
            _prev_urls.add(_u)
    if _new_count:
        print(f"  🆕 今日版面({_today_v29}): {_new_count} 条新内容（collectedAt=今日）")
        if _dup_skip:
            print(f"  ⏭️ {_dup_skip} 条已在历史版面，跳过")
    else:
        print(f"  ℹ️ 今日无新内容（缓存中非今日抓取或全部已在历史版面）")
    for d in archive:
        archive[d].sort(key=lambda x: (-x["priority_score"], x["title"]))

    # 7 天保留
    cutoff = (NOW - timedelta(days=6)).strftime("%Y-%m-%d")
    archive = {d: v for d, v in archive.items() if d >= cutoff}

    # 重新排序
    today = _today_v29
    dates = sorted(archive.keys(), reverse=True)

    total = sum(len(v) for v in archive.values())

    per_cat = {}
    for d in dates:
        for it in archive[d]:
            per_cat[it["category"]] = per_cat.get(it["category"], 0) + 1

    data = {
        "version": "5.0",
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

    print(f"\n📊 国内新闻抓取完成（v5）:")
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
