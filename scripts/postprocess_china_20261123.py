#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内看板 LLM 后处理 2026-11-23（删/修/补）"""
import json, io, sys

P = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json'
D = json.load(open(P, encoding='utf-8'))
TODAY = '2026-11-23'
today = D['archive'][TODAY]
COLLECT = '2026-11-23 09:28:12'
COLLECT2 = '2026-11-23 09:50:00'

del_frag = [
    # ---- 元首级软稿/拆条 ----
    '为共创亚太美好未来汇聚力量——习近平主席在亚太经合组织会议期间发表的重要讲话引发热烈反响',
    '习近平引领亚太共同体建设迈入新阶段',
    '金色相框',
    # ---- 五中全会精神/基层花絮 ----
    '五中全会精神在基层丨理旧账也是创新绩',
    '关注一块防滑垫 查清一笔民生账',
    # ---- 联合早报微观/评论/跨版面 ----
    '戴庆成：深圳APEC峰会，香港错过了什么',
    '陈文清出访德国和奥地利',
    '华为推出新子品牌星芒',
    # ---- 评论/方法论体 ----
    '对外贸易“加速”，节能方案走俏',
    '"数"看先进制造业强劲势头',
    '“数”看先进制造业强劲势头',
    '“中国是区域经济增长与合作的引领者”',
    '“中国服务”迈上新台阶',
    '“六张网”投资发力',
    '“深圳周期”→“产业沃土”→“智慧场景”',
    '“零碳暖流”、AI控温',
    '不靠海，却打开一片外贸蓝海',
    '中国经济看“新”丨从“尝鲜”到“潮流”',
    '共识向场外延伸！看产能、找配套、谈合作',
    '可用，不可见！首批可信数据空间',
    '打开串联城乡的“观鸟地图”',
    '数智技术为“老手艺”装上“新引擎”',
    '理响中国·聚焦2026中国经济',
    '竞争力无法替代，外资坚定加码',
    '金色渐染，定格瞬间',
    '黄土高原上，苹果正在长成现代化大产业',
]

def hit(t, frags):
    return any(f in t for f in frags)

keep, removed = [], []
for it in today:
    if hit(it['title'], del_frag):
        removed.append(it['title'])
    else:
        keep.append(it)

print('=== 删除 %d 条' % len(removed))
for r in removed:
    print('  -', r[:70])

# ---------- MODIFY ----------
def find(items, kw):
    for i in items:
        if kw in i['title']:
            return i
    return None

m = find(keep, '丁薛祥会见新加坡总理黄循财')
if m:
    m['title'] = '丁薛祥访问新加坡并会见新加坡总理黄循财 共同主持中新双边合作机制会议'
    m['summary'] = ('11月22日，中共中央政治局常委、国务院副总理丁薛祥在新加坡会见新加坡总理黄循财。丁薛祥表示，'
                    '此访主要任务是同新加坡副总理颜金勇共同主持中新双边合作机制会议，落实两国领导人共识；'
                    '中方愿将"十五五"规划同新方发展优先事项对接，深化人工智能、绿色发展等领域合作。'
                    '黄循财表示期待加强人工智能和数字经济合作，明年新加坡担任东盟轮值主席国，将积极推进东盟同中国合作。')
    m['priority_score'] = 95

m = find(keep, '陈文清将赴德国')
if m:
    m['source'] = '外交部'
    m['url'] = 'https://www.mfa.gov.cn/web/wjdt_674879/wsrc_674883/202611/t20261122_12064666.shtml'
    m['summary'] = ('中共中央政治局委员、中央政法委书记陈文清将于11月22日至28日赴德国出席第六次中德高级别安全对话并访问德国、奥地利。'
                    '中德高级别安全对话是中德关系框架下的重要机制性安排，此前已举行五轮，聚焦反恐、网络安全、执法合作等议题。')
    m['priority_score'] = 95

m = find(keep, '尹弘当选中共江西省委书记')
if m:
    m['summary'] = ('中共江西省第十五届委员会第一次全体会议选举尹弘为江西省委书记。尹弘，1963年10月生，'
                    '曾任河南省省长等职，2022年起任江西省委书记。此次系江西省委换届后的首次全会。')

m = find(keep, '商务部新闻发言人就美国联邦通信委员会')
if m:
    m['priority_score'] = 88
    m['summary'] = ('针对美国联邦通信委员会（FCC）拟禁止中国电信运营商直接获取美国互联网电话号码资源，商务部新闻发言人11月22日表示，'
                    'FCC滥用监管权力，肆意污蔑、恶意打压中国电信企业在美运营，中方对此坚决反对，'
                    '敦促美方立即撤销有关措施，回到通过磋商解决问题的正确道路上。')

m = find(keep, '前10月铁路完成固定资产投资')
if m:
    m['priority_score'] = 80
    m['summary'] = ('国铁集团数据显示，今年1至10月全国铁路完成固定资产投资6773亿元，同比增长约5%，'
                    '一批重点在建项目加快推进，为稳投资、扩内需提供支撑。')

for i in keep:
    if '第五期人工智能能力建设研讨班' in i['title']:
        i['priority_score'] = 80   # 国际合作类，非经贸一般稿
        i['summary'] = ('第五期人工智能能力建设研讨班11月举行，系落实中方在联合国大会提出的"人工智能能力建设普惠计划"，'
                        '面向发展中国家政府官员与技术人员开展培训，内容涵盖AI治理、算力基础设施与产业应用。')

# ---------- ADD ----------
def mk(title, cat, score, source, url, summary, date=TODAY, coll=COLLECT2):
    return {'title': title, 'category': cat, 'priority_score': score, 'source': source,
            'url': url, 'summary': summary, 'date': date, 'collectedAt': coll,
            'is_summit_level': score >= 95}

new_items = [
    mk('沪深北交易所下调融资保证金比例下限至80% 稳市场政策集中落地', '政策发布', 85,
       '中国经济网', 'https://www.ce.cn/xwzx/gnsz/gdxw/202611/t20261123_3302092.shtml',
       '11月22日，经中国证监会批准，上交所、深交所、北交所同步发布《关于调整融资保证金比例等相关安排的通知》，'
       '将融资保证金比例下限由100%降至80%，自2026年11月30日起实施，融资杠杆上限由1倍升至1.25倍，'
       '理论上可带来增量资金近4000亿元。同日，深交所就《创业板股票做市交易业务细则》公开征求意见，'
       '沪深交易所推出新一批降费措施、全年合计让利超46亿元，中国结算继续暂免三类公司债券相关费用。'),
    mk('我国启动具身智能数据国家标准研制 十五五期间将形成20余项专项标准', '部委动态', 85,
       '国家数据局', 'https://www.nda.gov.cn/sjj/swdt/mtsy/1122/20261122201646034268538_pc.html',
       '国家数据局11月22日表示，具身智能数据国家标准研制正式启动，"十五五"期间将陆续形成20余项专项国家标准，'
       '同步开展标准试点验证，未来支撑人形机器人、特种作业机器人、工业协作机械臂等多类应用场景落地，'
       '着力解决具身智能数据采集、标注、质量评价与跨本体复用等基础性规范缺失问题。'),
    mk('五部门印发国家公园评估办法（试行） 每五年开展一次"生态体检"', '政策发布', 80,
       '国家林业和草原局', 'https://www.forestry.gov.cn/lyj/1/gsgg/20261120/697181.html',
       '国家林草局、自然资源部、生态环境部、水利部、农业农村部近日联合印发《国家公园自然资源和生态环境状况评估办法（试行）》，'
       '明确每五年对国家公园自然资源状况、生态环境质量、生物多样性、生态系统原真性和完整性、生态安全风险等六大方面开展评估，'
       '由专业机构形成报告并经五部门论证后依法公布，评估指标含土地利用、旗舰物种种群数量、碳固定量等27项。'),
    mk('我国自主研制全球首套35千伏IGBT串联型静止全功率发生器在延安投运', '部委动态', 82,
       '央视新闻', 'https://big5.cctv.com/gate/big5/tv.cctv.cn/2026/11/22/VIDENDzC7p2vikXf9ZxmYvhA261122.shtml',
       '全球首套35千伏/30兆伏安IGBT串联型静止全功率发生器近日在陕西延安正式投运。该装备具有完全自主知识产权，'
       '破解高比例新能源并网场景下的电网稳定控制难题，投运后延安北部地区每年可新增新能源上网电量约0.6亿千瓦时，'
       '为构网型电力电子装备国产化提供工程样板。'),
    mk('中越海军舰艇编队完成第41次北部湾联合巡逻', '部委动态', 80,
       '央视新闻', 'https://military.cctv.com/2026/11/22/ARTIQCbHl5WMeOy6IypTiPZS261122.shtml',
       '11月21日，中国海军与越南海军舰艇编队圆满完成第41次北部湾联合巡逻。此次联合巡逻为期2天，航行32小时，'
       '总航程351海里，中越双方各派2艘舰艇参加，中方任务兵力为海军梧州舰和恩施舰。双方沿分界线巡航并分阶段转换指挥权，'
       '以两国渔船遇险为背景开展联合搜救演练，并完成编队运动训练。中越北部湾联合巡逻自2006年首次实施至今已20年，实现机制化常态化。'),
]

cov_titles = [i['title'] for i in keep]
cov_urls = [i['url'] for i in keep]
added = 0
for n in new_items:
    if n['title'] in cov_titles or n['url'] in cov_urls:
        print('  跳过(已存在):', n['title'][:40])
        continue
    keep.append(n); added += 1
print('=== 新增 %d 条' % added)

keep.sort(key=lambda x: -x.get('priority_score', 0))
D['archive'][TODAY] = keep
D['todayCount'] = len(keep)
D['today'] = TODAY
# dates 为字符串数组，仅用于顶部日期导航，无需重建
if D.get('dates') and TODAY not in D['dates']:
    D['dates'].insert(0, TODAY)

json.dump(D, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('最终今日条数:', len(keep))
from collections import Counter
print('分类:', Counter(i['category'] for i in keep))
print('分数>=85 占比: %.0f%%' % (100*sum(1 for i in keep if i['priority_score']>=85)/len(keep)))
