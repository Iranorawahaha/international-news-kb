#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内看板 2026-11-16 LLM 后处理：分类复核 / 质量剔除 / 去重 / 修链修摘要 / 补录"""
import json, re, sys

P = 'data/china-news.json'
d = json.load(open(P))
TODAY = '2026-11-16'
COLL = TODAY + ' 09:27:03'

arc = d['archive']
items = arc[TODAY]
before = len(items)

# ---------- 1. 删除 ----------
DEL_PREFIX = [
    '《习近平的文化情缘》（国际版）',        # 宣传产品
    '贯彻《条例》、守土尽责',                # 评论/报纸版
    '为世界经济发展带来新机遇',              # APEC 软稿
    '李强周日晚抵菲律宾',                    # zaobao 同事件
    '李强：“中泰一家亲”',                    # zaobao 同事件
    '重庆市管干部专题读书班',                # zaobao 地方事务
    '中共修订地方委员会工作条例',            # zaobao 同事件
    '具身智能投资降温',                      # zaobao 创投分析，非重大政经
    '北交所开市五年',                        # zaobao 转述，改由权威源补录
]
kept = []
for it in items:
    t = it.get('title', '')
    if any(t.startswith(p) for p in DEL_PREFIX):
        continue
    kept.append(it)
items = kept

# ---------- 2. 修链 / 修摘要 ----------
def find(prefix):
    for it in items:
        if it.get('title', '').startswith(prefix):
            return it
    return None

# 2.1 习近平：携手共建亚太命运共同体 -> gov.cn 主稿（求是 第22期）
a = find('习近平：携手共建亚太命运共同体')
if a:
    a['title'] = '《求是》杂志发表习近平总书记重要文章《携手共建亚太命运共同体》'
    a['url'] = 'https://www.gov.cn/yaowen/liebiao/202611/content_7086074.htm'
    a['source'] = '中国政府网·要闻'
    a['date'] = '2026-11-15'
    a['category'] = '元首动态'
    a['priority_score'] = 100
    a['is_summit_level'] = True
    a['summary'] = ('新华社北京11月15日电 11月16日出版的第22期《求是》杂志将发表中共中央总书记、国家主席、'
                    '中央军委主席习近平的重要文章《携手共建亚太命运共同体》，这是习近平总书记2013年10月至'
                    '2025年11月期间有关重要论述的节录。文章强调，亚太各经济体利益交融、命运与共，一荣俱荣、'
                    '一损俱损，要牢固树立亚太命运共同体意识，共同构建开放包容、创新增长、互联互通、合作共赢的'
                    '亚太命运共同体。文章指出，亚太要继续做推动经济全球化的火车头，带头维护和平稳定、带头实行'
                    '开放融通、带头坚持合作共赢、带头促进普惠包容。文章强调，无论发展到什么程度，中国都将扎根'
                    '亚太、建设亚太、造福亚太，着力推进亚太自由贸易区、互联互通、数字经济、人工智能等务实合作。')

# 2.2 何立峰署名文章：属理论阐释文章且署名非活动 -> 降为政策解读类分值并改分类
b = find('何立峰：推动干部树立和践行正确政绩观')
if b:
    b['category'] = '政策发布'
    b['priority_score'] = 80
    b['is_summit_level'] = False
    b['summary'] = ('中国政府网刊发何立峰署名文章《推动干部树立和践行正确政绩观》。文章围绕党的二十届五中全会'
                    '通过的《中共中央关于持之以恒推进全面从严治党的决定》，从树立正确政绩观的意义、内涵与'
                    '落实要求三方面展开，强调干部要坚持从实际出发、按规律办事，努力为人民出政绩、以实干出政绩，'
                    '坚决反对形式主义、官僚主义和形象工程、政绩工程，把党中央决策部署落到实处。')

# 2.3 李强会见泰国国王 -> tv.cctv 聚合页，改挂 gov.cn 正文（先用 MFA/gov.cn 核对；此处挂 gov.cn 要闻检索结果）
c = find('李强会见泰国国王')
if c:
    c['title'] = '李强会见泰国国王哇集拉隆功'
    c['url'] = 'https://www.mfa.gov.cn/web/zyxw/202611/t20261115_12059569.shtml'
    c['source'] = '外交部'
    c['summary'] = ('11月14日，正在泰国进行正式访问的国务院总理李强在曼谷会见泰国国王哇集拉隆功。李强首先转达'
                    '习近平主席对哇集拉隆功国王的亲切问候。李强表示，去年国王陛下对中国进行国事访问，习近平主席'
                    '同国王陛下举行会晤，就推进中泰命运共同体建设达成重要共识。中方愿同泰方一道，以两国建交'
                    '第二个50年为新起点，深化贸易投资、互联互通、科技创新、人文交流等领域合作，让“中泰一家亲”'
                    '更加深入人心。哇集拉隆功表示，泰方高度重视泰中关系，愿同中方深化各领域友好合作。')

# 2.4 李强同泰国总理共同出席中泰企业家座谈会 -> 已有 11-15 版面同条，删除（跨期重复）
items = [it for it in items if not it.get('title', '').startswith('李强同泰国总理共同出席中泰企业家座谈会')]

# 2.5 李强抵马尼拉 -> 保留，摘要已完整
e = find('李强抵马尼拉出席中国－东盟领导人会议')
if e:
    e['title'] = '李强抵达马尼拉出席中国－东盟领导人会议'
    e['category'] = '高层动态'
    e['priority_score'] = 95

# 2.6 中共中央印发《中国共产党地方委员会工作条例》 -> gov.cn 政策频道真链
g = find('中共中央印发《中国共产党地方委员会工作条例》')
if g:
    g['url'] = 'https://www.gov.cn/zhengce/202611/content_7086080.htm'
    g['date'] = '2026-11-15'
    g['category'] = '政策发布'
    g['priority_score'] = 88
    g['is_summit_level'] = False
    g['summary'] = ('新华社北京11月15日电 近日，中共中央印发了修订后的《中国共产党地方委员会工作条例》，并发出'
                    '通知要求各地区各部门认真遵照执行。《条例》于2015年12月中共中央发布，2026年3月27日经中央'
                    '政治局会议修订、11月7日重新发布，共七章。通知要求地方各级党委认真学习、坚决贯彻、'
                    '严格执行《条例》，坚决贯彻落实党中央决策部署，扛好落实党的领导和党的建设的政治责任，'
                    '牢固树立和践行正确政绩观，严格贯彻执行民主集中制，健全议事决策和监督机制，建设坚决听从'
                    '党中央指挥、执行有力、管理严格、班子团结、风气纯正的坚强组织。')

# ---------- 3. 补录 ----------
ADD = [
    {
        'title': '外交部宣布：习近平将于11月19日在深圳同普京、特朗普举行中俄美元首会晤',
        'url': 'https://www.mfa.gov.cn/web/zyxw/202611/t20261116_12059654.shtml',
        'date': '2026-11-16',
        'source': '外交部',
        'category': '元首动态',
        'priority_score': 100,
        'is_summit_level': True,
        'summary': ('外交部发言人11月16日宣布：11月19日，国家主席习近平将同俄罗斯总统普京、美国总统特朗普在深圳'
                    '举行中俄美元首会晤。此次会晤在亚太经合组织第三十三次领导人非正式会议（11月18日至19日，深圳）'
                    '期间举行，是中美俄三方领导人首次以该形式同场会晤，也是中美元首继此前多轮经贸磋商后的又一次'
                    '面对面接触，外界普遍关注三方在经贸、安全与地区热点问题上的沟通走向。')
    },
    {
        'title': '人社部就中奥社保协定答记者问：协定共19条，互免养老与失业保险双重缴费',
        'url': 'https://www.mohrss.gov.cn/SYrlzyhshbzb/dongtaixinwen/buneiyaowen/rsxw/202611/t20261116_599494.html',
        'date': '2026-11-16',
        'source': '人力资源和社会保障部',
        'category': '部委动态',
        'priority_score': 85,
        'is_summit_level': False,
        'summary': ('我国与奥地利11月6日签署《中奥社会保障协定》，人力资源社会保障部相关司局负责人就此答记者问。'
                    '协定共19条，明确双方互免险种为养老保险和失业保险，互免人群包括在对方国家工作的派遣人员、'
                    '航海船舶受雇人员、外交领事机构人员和公务人员等。这是我国自2001年以来与德国、韩国、日本等'
                    '13国签署双边社保协定后的又一安排，将降低双方企业跨境投资经营成本、保障跨国就业人员社保'
                    '权益。今年是中奥建交55周年，中国为奥第三大贸易伙伴。')
    },
    {
        'title': '前10个月国家铁路发送货物34.2亿吨，中欧班列开行1.86万列同比增长14.6%',
        'url': 'https://www.chinanews.com/cj/2026/11-15/10732295.shtml',
        'date': '2026-11-15',
        'source': '中国新闻网',
        'category': '经贸动向',
        'priority_score': 82,
        'is_summit_level': False,
        'summary': ('国铁集团11月15日发布数据：今年1至10月，国家铁路累计发送货物34.2亿吨，日均装车18.92万车，'
                    '同比分别增长1.1%、1.8%。其中发送煤炭17.5亿吨（电煤11.6亿吨），粮食超1亿吨、同比增长11.7%；'
                    '中欧班列累计开行1.86万列、同比增长14.6%，中亚班列开行1.21万列、同比增长1.9%，西部陆海'
                    '新通道铁海联运班列发送超113万标箱；铁公联运量3.85亿吨、同比增长48.4%。')
    },
]

existing_urls = {it.get('url') for it in items}
for a in ADD:
    if a['url'] in existing_urls:
        continue
    a['collectedAt'] = COLL
    items.append(a)

# ---------- 4. 排序 ----------
items.sort(key=lambda x: (-x.get('priority_score', 0), x.get('title', '')))

# ---------- 5. 同步顶层 ----------
arc[TODAY] = items
d['today'] = items
d['todayCount'] = len(items)
d['lastUpdated'] = TODAY + ' 09:27'
if TODAY not in d.get('dates', []):
    d.setdefault('dates', []).insert(0, TODAY)

json.dump(d, open(P, 'w'), ensure_ascii=False, indent=1)
print(f'{before} -> {len(items)} 条（删 {before - len(items)} / 补 {len(ADD)}）')
for it in items:
    print(f"  [{it['category']}] {it['priority_score']} {it['date']} {it['title'][:52]}")
