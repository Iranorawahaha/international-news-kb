#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内看板 LLM 后处理 — 2026-10-28"""
import json, shutil, sys

P = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json'
TODAY = '2026-10-28'
YDAY = '2026-10-27'

d = json.load(open(P, encoding='utf-8'))
today = d['archive'][TODAY]
yday = d['archive'][YDAY]
yday_urls = {x['url'] for x in yday}

# 历史全部 URL（用于跨期去重）
hist_urls = set()
for k, v in d['archive'].items():
    if k != TODAY:
        hist_urls |= {x['url'] for x in v}

def norm(u):
    return u.split('://')[-1]

before = len(today)

# ---------- 1. 删除 ----------
DEL_TITLES = [
    # 元首宣传产品 / 学习活动类
    '习言道｜这样的苹果，习近平说“现在也不能吃”',
    '依靠顽强斗争夺取新的伟大胜利——论学习贯彻习近平总书记在纪念中国工农红军长征胜利90周年大会上重要讲话精神',
    # 算力网同题多稿（保留“东数西算”主稿）
    '八大算力枢纽“落子”东西南北 数字中国“拔节生长”',
    '算力网加速织就 一批项目建设迎新进展',
    '数字“活水”流进千家万户 算力“算” 出来的民生红利铺展美好生活',
    # 前三季度经济数据拼盘 / 栏目体 / 评论式
    '“大国重器”获得新突破 重大工程刷新“进度条” 中国经济稳中有进底气足',
    '“数”说我国批发和零售业平稳增长 城乡市场活跃 国货潮品广受青睐',
    '一组数据 看我国经济动能向新',
    '从“锁边”到“富边” 新疆沙漠产业结出“累累硕果”改善生态、助增收',
    '从利润增长15.5%透视工业生产稳中有进 产业结构向新、向优、向好升级',
    '从多组“硬核”数据透视高质量发展成绩单 中国经济持续向绿向新向优',
    '向新向优向好 多维度数据看前三季度中国经济活力',
    '宏观政策更加积极有为落地显效 全国规模以上工业企业利润增长驶上“快车道”',
    '透过前三季度全国电力市场交易电量看“变化” 中国经济澎湃发展新动能',
    '金秋十月秋色如画勾勒出秋日盛景图 “生态美”带动“产业兴”实现“百姓富”',
    # 蹲点/一线见闻栏目体
    '小家电产业焕新升级（先进制造业发展一线见闻）',
    # 跨版面（AI 线，已在 AI 看板）
    '新闻1+1丨人工智能时代，如何减缓岗位替代？',
]
# 央行稳债市工具 → 10-27 版面已收 BNSF 设立（88 分）
DEL_URL_PARTS = ['ARTIhYRhhPJHrBDI7tn25Qhw']

keep = []
for x in today:
    if x['title'] in DEL_TITLES:
        continue
    if any(part in x['url'] for part in DEL_URL_PARTS):
        continue
    keep.append(x)
today = keep

# ---------- 2. 修正 ----------
FIX = {
    # 元首要闻 → gov.cn 原文
    '习近平向日本前首相福田康夫遗属致唁电': {
        'url': 'https://www.gov.cn/yaowen/liebiao/202610/content_7084342.htm',
        'source': '中国政府网·要闻',
        'summary': '10月27日，国家主席习近平向日本前首相福田康夫遗属致唁电，对福田康夫逝世表示哀悼，向其遗属表示慰问。习近平指出，福田先生是日本有信义、有担当的政治家，也是中国人民的老朋友，长期心系中日友好、秉持正确历史观，在任期间同中方签署中日第四个政治文件，为两国关系发展明确了重要原则；他曾担任博鳌亚洲论坛理事长，为促进亚洲地区交流合作发挥重要作用。中方将铭记他为中日关系和亚洲发展所作的贡献，期待遗属继承遗志继续致力于中日友好事业，并希望日本当政者珍视老一辈政治家的心血和努力，恪守中日四个政治文件，切实维护双边关系政治基础。',
    },
    '习近平致电祝贺卢拉当选连任巴西总统': {
        'url': 'https://www.gov.cn/yaowen/liebiao/202610/content_7084340.htm',
        'source': '中国政府网·要闻',
        'summary': '10月27日，国家主席习近平致电卢拉，祝贺他当选连任巴西联邦共和国总统。习近平指出，卢拉总统为推动中巴关系发展作出重要贡献，近年来两人通过不同方式保持密切沟通，共同引领携手构建更公正世界和更可持续星球的中巴命运共同体取得新进展，两国关系的全球性、战略性、长远性更加突出，成为全球南方国家团结合作的典范。习近平表示高度重视中巴关系发展，愿同卢拉总统一道努力，引领中巴命运共同体建设不断迈上新台阶，为两国全方位战略协作开辟更广阔前景。同日，国家副主席韩正向巴西连任副总统阿尔克明致贺电。',
    },
    # 外交部记者会：去标题日期残留 + 换正文直链 + 补摘要
    '2026年10月27日外交部发言人郭嘉昆主持例行记者会（2026-10-27）': {
        'title': '2026年10月27日外交部发言人郭嘉昆主持例行记者会',
        'url': 'https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202610/t20261027_12047706.shtml',
        'summary': '10月27日，外交部发言人郭嘉昆主持例行记者会。就纪念东京审判开庭80周年图片展在联合国总部举行，郭嘉昆表示，承认和接受东京审判是战后日本重归国际社会的前提，中方坚定守护历史真相、维护战后国际秩序。就中国驻英国大使馆发布出入境检查安全提醒，郭嘉昆表示，近期英方对中国公民无端盘查、羁押情况频发，中方对英国警方任意、过度执法行为表示强烈不满，已提出严正交涉，要求英方切实保障在英中国公民合法权益。',
    },
    # 中央纪委通报：人事任免 → 补数据摘要
    '2026年9月全国查处违反中央八项规定精神问题32940起': {
        'summary': '中央纪委国家监委10月27日公布2026年9月全国查处违反中央八项规定精神问题汇总情况：当月共查处相关问题32940起，批评教育和处理43280人，其中给予党纪政务处分28160人。从问题类型看，履职不力、不担当不作为等形式主义、官僚主义问题仍较突出，违规收送名贵特产和礼品礼金、违规发放津补贴或福利、违规吃喝等享乐奢靡问题增量集中在基层，通报要求持续紧盯节点、深化整治。',
    },
    # 知识产权“十五五”规划：评论式标题 → 事实性标题
    '每万人口高价值发明专利拥有量如何大幅跃升（解码“十五五”专项规划）': {
        'title': '国务院印发《知识产权保护和运用“十五五”规划》 高价值发明专利每万人将超22件',
        'summary': '近日国务院印发《知识产权保护和运用“十五五”规划》，将每万人口高价值发明专利拥有量指标设定为大于22件，较“十四五”末的16件增长6件以上。规划同时就严把专利授权质量、提升审查效率、强化专利转化运用和知识产权保护等作出部署，明确以高价值专利支撑高水平科技自立自强和产业升级。',
    },
    # 国开行：经贸 → 部委动态
    '国开行：已完成今年3650亿元新型政策性金融工具投放任务': {
        'category': '部委动态',
        'summary': '国家开发银行10月27日介绍，截至当日已完成2026年3650亿元新型政策性金融工具投放任务，资金全部用于补充项目资本金，涉及项目总投资5.5万亿元，有效发挥主力行作用，助力扩大有效投资、推动经济持续回升向好。',
    },
    # 进出口银行：经贸 → 部委动态
    '进出口银行完成2026年新型政策性金融工具投放': {
        'category': '部委动态',
        'summary': '中国进出口银行10月27日介绍，已完成2026年新型政策性金融工具投放任务，支持项目超500个，投放金额1200亿元，拉动项目总投资逾1.7万亿元，杠杆撬动作用显著，重点支持外贸、先进制造和基础设施等领域项目资本金补充。',
    },
}

for x in today:
    f = FIX.get(x['title'])
    if not f:
        continue
    for k, v in f.items():
        x[k] = v

# ---------- 3. 补录 ----------
ADD = [
    {
        'title': '我国风光累计装机容量突破20亿千瓦 达20.1亿千瓦',
        'url': 'https://cpc.people.com.cn/n1/2026/1028/c64387-40823062.html',
        'date': '2026-10-28',
        'source': '人民日报',
        'category': '部委动态',
        'priority_score': 85,
        'summary': '国家能源局数据显示，截至9月底全国累计发电装机容量41.3亿千瓦，同比增长11.2%，其中风电和太阳能发电累计装机容量达20.1亿千瓦，风电7.0亿千瓦、同比增长20.4%，太阳能发电13.1亿千瓦、同比增长16.5%。前三季度全国风光发电量19333亿千瓦时，同比增加1937亿千瓦时，风光发电增量占全社会新增用电量的64%，我国风光装机规模约占全球新能源总装机的一半。',
    },
    {
        'title': '蒋成华副部长代表中国政府签署《联合国可转让货物单证公约》 中国成首批签约国',
        'url': 'https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_efb4af97a1bc4c279a5f631dd8d2bffe.html',
        'date': '2026-10-27',
        'source': '商务部',
        'category': '部委动态',
        'priority_score': 85,
        'summary': '当地时间10月26日，《联合国可转让货物单证公约》签约仪式在加纳阿克拉举行，商务部副部长蒋成华出席并代表中国政府签署公约，包括中国、加纳在内的26个国家成为首批签约国。该公约由中国发起并引领达成，经第80届联合国大会于2025年12月审议通过，通过在国际规则层面创设适用于所有跨境运输方式的“可转让货物单证”，打破数百年来只有海运提单才能代表货权的制度壁垒，填补国际规则空白，将有效降低跨境陆上贸易交易成本。',
    },
    {
        'title': '李成钢出席第九届世界投资论坛 呼吁重塑更富韧性更普惠的全球价值链',
        'url': 'https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_6f82a4ff7e194f9fa128d7ffb566466c.html',
        'date': '2026-10-27',
        'source': '商务部',
        'category': '部委动态',
        'priority_score': 85,
        'summary': '10月25日至27日，由联合国贸发会议和卡塔尔政府联合主办的第九届世界投资论坛在多哈举行，商务部国际贸易谈判代表（正部长级）兼副部长李成钢出席开幕式并在“重塑全球价值链，促进增长与韧性”高级别会议发言。李成钢指出，当前国际投资不振、全球价值链碎片化政治化、发展中国家被边缘化等风险突出，中方呼吁坚持多边主义为价值链稳定畅通提供规则保证、坚持开源开放提升新兴产业价值链韧性、坚持发展导向让全球南方更好受益。会议期间李成钢与卡塔尔外贸事务国务大臣、贸发会议秘书长、世贸组织总干事等举行会见。',
    },
    {
        'title': '民政部部署开展“寒冬送温暖”专项救助行动 至2027年3月15日',
        'url': 'https://www.chinanews.com/gn/2026/10-28/10721963.shtml',
        'date': '2026-10-28',
        'source': '人民日报',
        'category': '政策发布',
        'priority_score': 80,
        'summary': '民政部办公厅近日印发通知，部署开展“寒冬送温暖”专项救助行动，行动自即日起至2027年3月15日（东北、西北地区可视情延长），保障生活无着的流散人员安全过冬。通知要求建立气象预警联动机制，会同公安、城市管理、卫生健康、应急等部门对车站码头、地下通道、桥梁涵洞、废弃房屋等重点区域拉网式排查，极端天气前和夜间加密巡查；构建市县乡村发现报告网络，动员环卫工人、快递员、出租车司机等提供线索，可依托福彩站点设临时救助点；对危重病人、精神障碍患者按“先救治、后救助”送定点医院。',
    },
    {
        'title': '周海兵副主任会见法国财政总署署长杜蒙',
        'url': 'https://www.ndrc.gov.cn/xwdt/xwfb/202610/t20261027_1408419.html',
        'date': '2026-10-27',
        'source': '国家发展改革委',
        'category': '部委动态',
        'priority_score': 85,
        'summary': '10月27日，国家发展改革委副主任周海兵会见法国财政总署署长杜蒙，双方就宏观经济形势、中法经贸与投资合作、绿色低碳转型和第三方市场合作等议题交换意见。中方表示愿同法方落实两国元首共识，用好既有对话机制，扩大双向投资和产业合作，共同维护多边贸易体制。',
    },
    {
        'title': '第140届广交会第二期线下展闭展 27.8万名境外采购商到会',
        'url': 'https://news.cctv.com/2026/10/27/ARTIL5ppuvPs5v6g12745co4261027.shtml',
        'date': '2026-10-27',
        'source': '央视新闻',
        'category': '经贸动向',
        'priority_score': 85,
        'summary': '第140届广交会第二期线下展10月27日闭展，聚焦“品质家居”主题，展览总面积51.5万平方米、超2.5万个展位。截至当日17时，共有来自218个国家和地区的27.8万名境外采购商到会，比上届同期增长13.4%；出口展参展企业约1.1万家，其中专精特新、单项冠军等优质企业超3600家、同比增长约7.6%。本期举办178场新品首发活动，首发新品较上届增长约15%，第三期将于10月31日至11月4日举行。',
    },
]

# 跨期/今日去重
cur_urls = {norm(x['url']) for x in today}
for a in ADD:
    if norm(a['url']) in cur_urls:
        print('SKIP dup in today:', a['title']); continue
    if norm(a['url']) in {norm(u) for u in hist_urls}:
        print('SKIP dup in history:', a['title']); continue
    a['collectedAt'] = '2026-10-28 09:40:00'
    today.append(a)

# ---------- 断言 ----------
errs = []
for x in today:
    if x['collectedAt'][:10] != TODAY:
        errs.append(('collectedAt', x['title']))
    if x['date'] not in (TODAY, YDAY):
        errs.append(('date', x['title'], x['date']))
    if not (x.get('summary') or '').strip() or len(x['summary']) < 30:
        errs.append(('summary', x['title'], len(x.get('summary') or '')))
    if x['url'] in yday_urls:
        errs.append(('yday-url', x['title']))
    if x['url'].startswith('https://tv.cctv.com'):
        errs.append(('tv.cctv', x['title']))
    if '（2026-' in x['title'] or '(2026-' in x['title']:
        errs.append(('title-date', x['title']))
    if '&nbsp;' in (x.get('summary') or '') or '&amp;nbsp;' in (x.get('summary') or ''):
        errs.append(('entity', x['title']))
ts = [x['title'] for x in today]
us = [norm(x['url']) for x in today]
if len(ts) != len(set(ts)): errs.append(('dup-title', len(ts) - len(set(ts))))
if len(us) != len(set(us)): errs.append(('dup-url', len(us) - len(set(us))))

if errs:
    print('ASSERT FAIL:')
    for e in errs: print('  ', e)
    sys.exit(1)

# 政府网要闻分数校验
from collections import defaultdict
best = defaultdict(int)
for x in today:
    best[x['category']] = max(best[x['category']], x['priority_score'])
for x in today:
    if '中国政府网' in x['source'] and x['priority_score'] < best[x['category']]:
        print('WARN gov.cn score', x['title'], x['priority_score'], best[x['category']])

d['archive'][TODAY] = today
if d.get('today') == TODAY:
    d['todayCount'] = len(today)
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

from collections import Counter
c = Counter(x['category'] for x in today)
hi = sum(1 for x in today if x['priority_score'] >= 85)
print(f'BEFORE {before} -> AFTER {len(today)} (del {before - len(today) + len(ADD)}, add {len(ADD)})')
print('categories', dict(c))
print(f'>=85: {hi}/{len(today)} = {hi * 100 // len(today)}%   100分: {sum(1 for x in today if x["priority_score"] == 100)}')
print('yday untouched:', len(yday))
