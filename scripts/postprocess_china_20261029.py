#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内看板 LLM 质量后处理 2026-10-29
初抓 38 条 -> 质量后处理 + AI 补强
"""
import json, html, re, sys

PATH = 'data/china-news.json'
TODAY = '2026-10-29'
YDAY = '2026-10-28'
d = json.load(open(PATH, encoding='utf-8'))
arr = d['archive'][TODAY]
before = len(arr)

def norm(u):
    return (u or '').strip().rstrip('/')

# ---------- 删除清单（URL 精确匹配） ----------
DEL_URLS = {
    # 1 学习类/论学习贯彻讲话精神（排比式评论稿）
    'https://www.gov.cn/yaowen/liebiao/202610/content_7084428.htm',
    # 2 zaobao 微观/评论稿：福田唁电规格推测
    'https://www.zaobao.com/news/china/story20261028-9908152',
    # 3 zaobao 文体八卦（姆巴佩），非政务情报
    'https://www.zaobao.com/news/china/story20261028-9908385',
    # 4 蔡康永/台湾艺人 —— 与国台办发布会同源子稿，舆情琐碎
    'https://www.zaobao.com/news/china/story20261028-9908998',
    'https://www.zaobao.com/news/china/story20261028-9910511',
    # 5 巴基斯坦对台关闭领空（第三国涉台动作，非中方发布）
    'https://www.zaobao.com/news/china/story20261028-9911366',
    # 6 央视「党旗在基层一线高高飘扬」栏目体人物稿（抗震救灾个人叙事）
    'https://news.cctv.com/2026/10/28/ARTIXSRSDell1O96WlIOO0sz261028.shtml',
    # 7 系列述评/观察栏目体：「向新而行」「民生为大」「专项规划观察之五」
    'https://www.gov.cn/yaowen/liebiao/202610/content_7084427.htm',
    'https://news.cctv.com/2026/10/28/ARTIyPl77k9D76NNj5BjbJ7v261028.shtml',
    # 8 外空治理：央视「记者观察」评论稿（政策本体 10-23 雄安论坛已发布）
    'https://news.cctv.com/2026/10/28/ARTI0QMhCgMSF8H3dG61Niy0261028.shtml',
    # 9 抖音式数据拼盘：一组数据/多维度数据/向新向优向好
    'https://jingji.cctv.com/2026/10/28/ARTIwPXFr9691vMY06LaHqpR261028.shtml',
    'https://news.cctv.com/2026/10/28/ARTIoSFFXp0Ir7OwAiwotmwJ261028.shtml',
    # 10 以旧换新 同事件三稿 -> 只留商务部会议主稿（见下修正）
    'https://news.cctv.com/2026/10/28/ARTIhMqofbP40aJF35PniSmt261028.shtml',
    'https://news.cctv.com/2026/10/29/ARTIfjeA6Ehhz6dGddM8LUAB261029.shtml',
    # 11 8000 亿政策性金融工具 同事件两稿 -> 留 gov.cn
    'https://jingji.cctv.com/2026/10/29/ARTI13oYRcDhVKbWKyVnrs8G261028.shtml',
    # 12 算力网建设：栏目体（「六张网」系列短视频稿，10-26 已收同类）
    'https://news.cctv.com/2026/10/28/ARTISACixeHdzCisvUeC1DKf261027.shtml',
    # 13 蹲点故事化：「沙海资源正转化为富民产业」沙漠水产
    'https://news.cctv.com/2026/10/28/ARTIPWCgmO1aZXYsB0728JFQ261028.shtml',
    # 14 人民日报「先进制造业发展一线见闻」栏目体（丹阳眼镜）
    'http://paper.people.com.cn/rmrb/pc/content/202610/29/content_30188308.html',
    # 15 AI 应用综述「深阅读」栏目体（非政策/非博弈）
    'http://paper.people.com.cn/rmrb/pc/content/202610/29/content_30188334.html',
    # 16 秋粮收获进度：农业生产常规播报
    'https://news.cctv.com/2026/10/28/ARTIn0V2MS3t2EPsoOvGDlFt261028.shtml',
    # 17 zaobao 宏观评述（无新增事实）
    'https://www.zaobao.com/news/china/story20261028-9907978',
    # 18 证监会私募母基金：央视「财经老王」观察体
    'https://news.cctv.com/2026/10/28/ARTI6VHcVdJuj6m39ij96L57261028.shtml',
}

# 清理（不存在于当前版面也没关系）
deleted = []
kept = []
for it in arr:
    if norm(it['url']) in DEL_URLS:
        deleted.append(it['title'])
    else:
        kept.append(it)
arr = kept

def find(url):
    for it in arr:
        if norm(it['url']) == norm(url):
            return it
    return None

# ---------- 修正 ----------
# A. 记者会死链修复（同 ID 换路径）+ 去标题日期残留 + 补真实摘要
f = find('https://www.mfa.gov.cn/web/wjdt_674879/202610/t20261028_12048462.shtml')
if f:
    f['url'] = 'https://www.mfa.gov.cn/web/fyrbt_673021/jzhsl_673025/202610/t20261028_12048462.shtml'
    f['title'] = '外交部举行例行记者会 就中瑞关系、默茨涉华表态、也门局势等答问'
    f['summary'] = ('外交部发言人郭嘉昆10月28日主持例行记者会。就瑞士联邦主席帕姆兰10月30日至11月1日来华工作访问，'
                    '郭嘉昆表示习近平主席将会见帕姆兰，今年是中瑞建立创新战略伙伴关系10周年，瑞士8月率先同中方完成自贸协定升级谈判。'
                    '针对德国总理默茨呼吁欧亚中等强国建立战略联盟、减少“不健康单方面依赖”，中方表示中德中欧经济互补产业互嵌，'
                    '希望德方欧方保持客观理性、通过对话磋商化解分歧。就也门胡塞武装袭击沙特目标，中方反对攻击民航机场等民用设施。')

# B. 元首动态：zaobao 瑞士访华（无摘要）-> gov.cn 官方版
s = find('https://www.zaobao.com/news/china/story20261028-9908377')
if s:
    s['url'] = 'https://www.gov.cn/yaowen/liebiao/202610/content_7084400.htm'
    s['source'] = '中国政府网·要闻'
    s['title'] = '瑞士联邦主席帕姆兰将访华 习近平将会见'
    s['summary'] = ('外交部发言人10月28日宣布：瑞士联邦主席帕姆兰将于10月30日至11月1日来华进行工作访问，'
                    '习近平主席将同他会见。今年是中国同瑞士建立创新战略伙伴关系10周年，瑞士是最早同中国签订自贸协定的欧洲大陆国家，'
                    '今年8月又率先同中方完成自贸协定升级谈判。')

# C. 高层动态：商务部王文涛会见朗格 —— 提高层动态95 且补摘要
w = find('https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_614dbefc8e8a4f77a06dea59e046ba3e.html')
if w:
    w['priority_score'] = 95
    w['category'] = '高层动态'
    w['summary'] = ('商务部部长王文涛10月28日在京会见欧洲议会国际贸易委员会主席贝恩德·朗格，双方就中欧经贸关系、'
                    '双边贸易投资合作及 WTO 改革等议题交换意见。同日，全国人大常委会副委员长李鸿忠、蔡达峰也分别会见了朗格一行。')

# D. 产业基础能力提升「十五五」规划 —— 政策发布 80（八部门联合印发）
p = find('https://news.cctv.com/2026/10/28/ARTIxE0GFrPiFNAr1rtkEreX261028.shtml')
if p:
    p['category'] = '政策发布'
    p['priority_score'] = 80
    p['title'] = '八部门印发《产业基础能力提升“十五五”规划》 提出22项重点任务'
    p['summary'] = ('工业和信息化部等八部门近日印发《产业基础能力提升“十五五”规划》，围绕提升产业基础自主可控能力、'
                    '增强产业基础创新能力等7个方面提出22项重点任务，明确到2030年我国产业基础自主可控能力全面提升。')

# E. 南方区域电力市场复函 —— 政策发布 80 + 补摘要
e = find('https://www.ndrc.gov.cn/xwdt/tzgg/202610/t20261028_1408425.html')
if e:
    e['category'] = '政策发布'
    e['priority_score'] = 80
    e['summary'] = ('国家发展改革委、国家能源局10月28日复函同意南方区域电力市场转入正式运行，'
                    '标志着继国家电网经营区后，南方区域电力现货市场建设由试运行阶段进入正式运行，'
                    '为全国统一电力市场体系建设提供区域性实践样本。')

# F. 交通固定资产投资 2.4 万亿 —— 部委动态 85
t = find('http://paper.people.com.cn/rmrb/pc/content/202610/29/content_30188312.html')
if t:
    t['category'] = '部委动态'
    t['priority_score'] = 85
    t['title'] = '前三季度交通固定资产投资完成2.4万亿元'
    t['summary'] = ('交通运输部10月28日披露，在一系列重大工程带动下，前三季度全国交通固定资产投资完成2.4万亿元，'
                    '其中公路、水运分别完成1.6万亿元和1571亿元，投资保持高位运行。')

# G. 外资企业投资深圳 —— 见闻栏目体，删除（已不入库，如存在则删）
g = find('http://paper.people.com.cn/rmrb/pc/content/202610/29/content_30188320.html')
if g:
    arr.remove(g); deleted.append(g['title'])

# H. 廖岷 IMF 副总裁 —— 补摘要 + 规范化标题
lm = find('https://www.zaobao.com/news/china/story20261029-9912194')
if lm:
    lm['title'] = 'IMF总裁提议财政部副部长廖岷接任IMF副总裁 12月1日生效'
    lm['summary'] = ('国际货币基金组织总裁格奥尔基耶娃10月28日宣布，副总裁李波将于11月30日任期结束后离任，'
                     '提议由现任中国财政部副部长廖岷接任，自12月1日起生效。廖岷2018年起任财政部副部长，'
                     '并于2023年起任人民银行货币政策委员会委员，将成为IMF第四位中国籍副总裁。')

# I. 台湾相声演员子稿/国台办 —— 保留国台办发布会主体，标题去栏目化
gt = find('https://news.cctv.com/2026/10/28/ARTImozHyal4b2OAA4dq7w8Q261028.shtml')
if gt:
    gt['summary'] = ('国务院台办10月28日举行例行新闻发布会。发言人表示祖国终将统一也必将统一的历史大势不可阻挡，'
                     '就台湾艺人在大陆相关争议、所谓“跨境镇压”说法等作出回应，强调主权问题不容模糊。')

# ---------- 补录（全部 curl/WebFetch 已验证，date 落在 {10-28,10-29}） ----------
ADD = [
    dict(category='高层动态', priority_score=95, is_summit_level=True,
         title='国务院原副总理刘延东同志逝世 享年81岁',
         source='中国政府网·要闻',
         url='https://www.gov.cn/yaowen/liebiao/202610/content_7084388.htm',
         date='2026-10-28',
         summary='中国共产党的优秀党员，久经考验的忠诚的共产主义战士，我党统一战线工作和我国教育科技、医疗卫生、妇女儿童工作的杰出领导人，'
                 '中国共产党第十七届、十八届中央政治局委员，第十届全国政协副主席，原国务委员、国务院原副总理刘延东同志，'
                 '因病于2026年10月28日14时53分在北京逝世，享年81岁。'),
    dict(category='部委动态', priority_score=85,
         title='国家文物局在堪培拉接收澳大利亚返还的2件流失文物',
         source='国家文物局',
         url='http://www.ncha.gov.cn/art/2026/10/28/art_722_205502.html',
         date='2026-10-28',
         summary='当地时间10月28日，国家文物局在堪培拉接收澳大利亚国家美术馆返还的2件中国流失文物，'
                 '分别为北宋皇陵永裕陵武官像头部和永昌陵文官像头部。国家文物局会同公安部及河南文物、公安部门调查取证，'
                 '2025年正式启动追索，在联合国教科文组织1970年公约框架下实现回归。'),
    dict(category='部委动态', priority_score=85,
         title='退役军人事务部确认8位在韩志愿军烈士身份 累计44位找到亲人',
         source='央视新闻',
         url='https://ysxw.cctv.cn/article.html?toc_style_id=feeds_default&t=1793154265968&item_id=2867686303280675238&channelId=1119',
         date='2026-10-28',
         summary='退役军人事务部10月28日举行褒扬纪念工作专题新闻发布会，介绍在韩中国人民志愿军烈士遗骸鉴定新进展：'
                 '施志成、夏小龙、张振法等8位烈士身份得到确认。2014年以来我国已连续13年迎回13批1023位烈士遗骸，'
                 '截至目前累计为44位烈士确认身份、找到亲人，烈士寻亲一体化平台将于年底前正式上线。'),
    dict(category='经贸动向', priority_score=85,
         title='第140届广交会第二期闭展 27.8万名境外采购商到会增长13.4%',
         source='央视新闻',
         url='https://news.cctv.cn/2026/10/28/ARTILtLYyO3omxWbnfxVeDr1261028.shtml',
         date='2026-10-28',
         summary='第140届广交会第二期线下展10月27日闭展。截至27日17时，共有来自218个国家和地区的27.8万名境外采购商到会，'
                 '较上届同期增长13.4%；本期出口展1.1万家企业参展，专精特新、单项冠军等优质企业超3600家、同比增长约7.6%，'
                 '举办178场新品首发活动。第三期将于10月31日至11月4日举办。'),
    dict(category='部委动态', priority_score=85,
         title='商务部召开全国消费品以旧换新工作推进电视电话会议',
         source='商务部',
         url='https://www.mofcom.gov.cn/syxwfb/art/2026/art_7362348394ab40a9a6f8bab24b6b2e46.html',
         date='2026-10-28',
         summary='商务部10月28日召开全国消费品以旧换新工作推进电视电话会议，商务部部长助理袁晓明出席并讲话。'
                 '会议指出，2026年以来消费品以旧换新带动相关品类销售额超2万亿元、惠及超2.5亿人次；'
                 '要求各地加快补贴兑付、创新线下消费场景，保障全年工作圆满收官。'),
]

existing_urls = {norm(it['url']) for it in arr}
added = []
for a in ADD:
    if norm(a['url']) in existing_urls:
        continue
    a['collectedAt'] = '2026-10-29 09:55:00'
    arr.append(a)
    added.append(a['title'])

# ---------- 全局清洗：HTML 实体 ----------
def clean(s):
    if not s: return s
    s = html.unescape(s)
    s = s.replace('\u00a0', ' ')
    return re.sub(r'\s+', ' ', s).strip()

for k in d['archive']:
    for it in d['archive'][k]:
        it['title'] = clean(it.get('title'))
        it['summary'] = clean(it.get('summary'))

# ---------- 排序 ----------
CAT_ORDER = ['元首动态', '高层动态', '重要会议', '人事任免', '政策发布', '部委动态', '经贸动向']
arr.sort(key=lambda x: (-x.get('priority_score', 0), CAT_ORDER.index(x['category']) if x['category'] in CAT_ORDER else 9))
d['archive'][TODAY] = arr
d['todayCount'] = len(arr)

# ---------- 统计 ----------
k = d['archive'][TODAY]
d["stats"] = {
    'totalArticles': sum(len(v) for v in d['archive'].values()),
    'dateCount': len(d['archive']),
    'latestDate': TODAY,
    'summitCount': sum(1 for i in k if i.get('is_summit_level')),
}
d['lastUpdated'] = '2026-10-29 09:55:00'

json.dump(d, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# ---------- 自检 ----------
from collections import Counter
k = d['archive'][TODAY]
print(f'== 后处理完成：{before} -> {len(k)} 条（删 {len(deleted)} / 补 {len(added)}）')
print('分类分布:', dict(Counter(i['category'] for i in k)))
hi = sum(1 for i in k if i.get('priority_score', 0) >= 85)
print(f'≥85 占比: {hi}/{len(k)} = {hi*100//len(k)}%')
print('100分条数:', sum(1 for i in k if i.get('priority_score') == 100))
print('元首动态:', sum(1 for i in k if i['category'] == '元首动态'))
print('无摘要:', [i['title'][:30] for i in k if not i.get('summary')])
print('摘要含实体:', [i['title'][:30] for i in k if '&nbsp;' in (i.get('summary') or '') or '&amp;' in (i.get('summary') or '')])
print('collectedAt≠今日:', [i['title'][:30] for i in k if not (i.get('collectedAt') or '').startswith(TODAY)])
print('date<昨日:', [i['title'][:30] for i in k if i['date'] < YDAY])
print('标题<8字符:', [i['title'] for i in k if len(i['title']) < 8])
urls = Counter(norm(i['url']) for i in k)
print('URL重复:', [u for u, c in urls.items() if c > 1])
print('== 删除清单:')
for t in deleted: print('  -', t[:60])
print('== 补录清单:')
for t in added: print('  +', t[:60])
