#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LLM 质量后处理 - 国内看板 2026-08-26"""
import json, copy

PATH = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json'
data = json.load(open(PATH, encoding='utf-8'))
today_items = data['archive']['2026-08-26']

# ============ 1. 删除 7 条（低质/学习栏目/评论/综述/旧闻重复/个人新闻/地方专栏） ============
del_titles = [
    '时政微观察丨这项任务，总书记强调“久久为功”',   # 央视学习栏目
    '努力实现“十五五”良好开局——从计划执行报告看下半年经济工作重点',  # 解读评论
    '中印重申寻求边界一揽子方案 学者：美国因素推动关系回暖',  # 联合早报评论，权威版覆盖
    '中国拟修订对外投资办法 管理对象首纳居民个人',  # 8-22 已收旧闻重复
    '从投资热土到产业高地——天津经开区围绕产业链“筑基、强链、育新”',  # 地方专栏
    '从生产到研发，外资企业拥抱中国“指数级”机遇',  # 外资综述
    '马云据报增持逾6亿港元阿里股票 力挺AI战略布局',  # 个人/企业新闻
]
kept = []
removed = []
for item in today_items:
    if item.get('title') in del_titles:
        removed.append(item.get('title'))
    else:
        kept.append(item)
today_items = kept
print(f'删除 {len(removed)} 条: {removed}')

# ============ 2. 权威化：王毅会见 → 中印特代会晤外交部版 ============
for item in today_items:
    if '王毅会见印度国安顾问' in item.get('title',''):
        item['title'] = '中印边界问题特别代表第25次会晤在北京举行'
        item['source'] = '外交部'
        item['url'] = 'https://www.mfa.gov.cn/wjbzhd/202608/t20260825_12010205.shtml'
        item['date'] = '2026-08-25'
        item['category'] = '高层动态'
        item['priority_score'] = 95
        item['summary'] = '8月25日，中印边界问题特别代表第25次会晤在北京举行。中方特别代表、中央外办主任王毅同印方特别代表、国家安全顾问多瓦尔就中印边界问题和双边关系等全面深入、友好坦诚沟通，重申按2005年政治指导原则寻求公平合理、双方都能接受的边界问题一揽子解决方案，商定2027年在印度举行第26次会晤。'
        print('权威化: 王毅会见 → 外交部中印特代会晤版')

# ============ 3. 分类修正 ============
for item in today_items:
    if '党政领导干部生态环境损害责任追究办法' in item.get('title',''):
        item['category'] = '政策发布'
        item['priority_score'] = 80   # 中办国办两办文件=重大政策（政策发布最高档）
        print('分类修正: 两办生态环境办法 部委动态88 → 政策发布80')

# ============ 4. 分数提升 ============
for item in today_items:
    if '数字产业收入超20万亿元' in item.get('title',''):
        item['priority_score'] = 85   # 宏观官方数据=高层经济信号
        print('分数提升: 数字产业收入 经贸72 → 85')

# ============ 5. 补摘要 ============
for item in today_items:
    if '六网协同' in item.get('title',''):
        item['summary'] = '8月25日，国家发展改革委副主任岳修虎主持召开“六网协同”协调推进工作会，专题研究完善“六张网”多元化投融资模式，分类细化财政、金融、投资、价格等支持政策，创新政策工具、优化政策组合，推动建立与不同领域不同类型工程项目相适配的投融资机制，为重大工程项目加快开工建设提供有力支撑。'
    elif '例行记者会（2026-08-25）' in item.get('title',''):
        item['summary'] = '外交部发言人林剑8月25日主持例行记者会，就中印边界问题特别代表会晤、中外交往及国际地区问题等回答记者提问。'
    elif '香港7月出口' in item.get('title',''):
        item['summary'] = '在人工智能（AI）相关电子产品需求持续强劲下，香港今年7月商品出口货值同比增长50.7%。'
    elif '香港与秘鲁自由贸易协定' in item.get('title',''):
        item['summary'] = '香港与秘鲁签订的自由贸易协定将于9月1日生效。'
print('补摘要完成（六网协同/例行记者会/香港出口/香港秘鲁FTA）')

# ============ 6. 补录 3 条 ============
collected = '2026-08-26 09:21:53'
new_items = [
    {
        'title': '道路交通安全法修订草案首次提请审议 增设自动驾驶汽车专章',
        'url': 'https://society.people.com.cn/n1/2026/0825/c1008-40785802.html',
        'date': '2026-08-25',
        'source': '人民网',
        'category': '政策发布',
        'priority_score': 80,
        'is_summit_level': False,
        'summary': '8月25日提请十四届全国人大常委会会议初次审议的道路交通安全法修订草案设置“自动驾驶汽车的特别规定”专章，首次在国家法律层面明确自动驾驶汽车法律地位、上道路行驶条件及违法责任归属：自动驾驶功能激活状态下发生道路交通违法行为的，由生产企业、进口企业接受处理；未激活或仅具辅助驾驶功能的汽车按非自动驾驶汽车规定管理。',
        'collectedAt': collected,
    },
    {
        'title': '中央网信办“清朗·网络娱乐团播乱象整治”累计处置违规直播间7200余个',
        'url': 'https://epaper.gmw.cn/gmrb/html/content/202608/25/content_23231.html',
        'date': '2026-08-25',
        'source': '光明日报',
        'category': '部委动态',
        'priority_score': 88,
        'is_summit_level': False,
        'summary': '中央网信办“清朗·网络娱乐团播乱象整治”专项行动启动以来，累计处置团播违规直播间7200余个、严惩违规账号2200余个，清退处置一批问题严重的团播MCN机构，发布治理公告17期；坚持整治与规范并重，娱乐团播低俗内容大幅下降，诱导刺激打赏等违规行为得到有效遏制，团播生态明显转好。',
        'collectedAt': collected,
    },
    {
        'title': '工信部就《国家人形机器人产业标准体系建设指南（2026版）》公开征求意见',
        'url': 'http://scitech.ce.cn/sy/zx/202608/t20260825_3169016.shtml',
        'date': '2026-08-25',
        'source': '中国经济网',
        'category': '部委动态',
        'priority_score': 85,
        'is_summit_level': False,
        'summary': '工信部科技司8月24日发布《国家人形机器人产业标准体系建设指南（2026版）》（征求意见稿），8月25日至9月23日公开征求意见。提出到2028年完成至少100项关键标准制定，重点突破基础共性、类脑与智算、肢体与部组件、整机与系统、应用、安全伦理等领域标准研制，开展标准宣贯和实施推广的企业超200家。',
        'collectedAt': collected,
    },
]
existing_keys = {(i.get('title','')[:30], i.get('source','')) for i in today_items}
added = 0
for ni in new_items:
    key = (ni['title'][:30], ni['source'])
    if key in existing_keys:
        print(f'跳过重复: {ni["title"][:40]}')
        continue
    today_items.append(ni)
    existing_keys.add(key)
    added += 1
print(f'补录 {added} 条')

# ============ 7. 重算统计 ============
data['archive']['2026-08-26'] = today_items
# 收集全部条目
all_items = []
for d in data['archive']:
    for it in data['archive'][d]:
        if it not in all_items:
            all_items.append(it)
# 按日期排序归档（倒序）
data['archive'] = dict(sorted(data['archive'].items(), key=lambda kv: kv[0], reverse=True))
data['dates'] = sorted(data['archive'].keys(), reverse=True)
data['today'] = '2026-08-26'
data['todayCount'] = len(today_items)
data['lastUpdated'] = '2026-08-26 09:42'
summit = sum(1 for i in all_items if i.get('is_summit_level'))
stats = data.get('stats', {})
stats['totalArticles'] = len(all_items)
stats['dateCount'] = len(data['archive'])
stats['latestDate'] = '2026-08-26'
stats['summitCount'] = summit
data['stats'] = stats

json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\n✅ 完成: 今日版面 {len(today_items)} 条 | 全量 {len(all_items)} 条 | 元首级 {summit}')

# ============ 8. 校验 ============
# 唯一键
keys = [(i.get('title','')[:30], i.get('source','')) for d in data['archive'] for i in data['archive'][d]]
dups = [k for k in keys if keys.count(k) > 1]
print('唯一键重复:', set(dups) if dups else '无')
# 字段完整性
missing = [i.get('title','') for d in data['archive'] for i in data['archive'][d] if not all(i.get(f) for f in ['title','url','date','source','category','summary'])]
print('缺字段:', missing if missing else '无')
# 今日 date 校验
bad_date = [i.get('title','') for i in today_items if i.get('date','') < '2026-08-25' or i.get('date','') > '2026-08-26']
print('今日 date 越界:', bad_date if bad_date else '无')
bad_collected = [i.get('title','') for i in today_items if not str(i.get('collectedAt','')).startswith('2026-08-26')]
print('今日 collectedAt≠今日:', bad_collected if bad_collected else '无')
# 分数分布
scores = [i.get('priority_score',0) for i in today_items]
high = sum(1 for s in scores if s >= 85)
print(f'今日分数分布: {scores}')
print(f'今日 ≥85 分: {high}/{len(scores)} = {high*100//max(len(scores),1)}%')
# 元首级
summit_today = sum(1 for i in today_items if i.get('is_summit_level'))
print(f'今日元首级: {summit_today}')
