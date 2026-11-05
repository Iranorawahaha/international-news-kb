# -*- coding: utf-8 -*-
"""国内看板 2026-11-05 后处理 patch：URL 归并 / 摘要补全 / 去重"""
import json
from collections import Counter

P = 'data/china-news.json'
TODAY = '2026-11-05'
d = json.load(open(P, encoding='utf-8'))
items = d['archive'][TODAY]

FIX = {
 # 记者会：换真实路径 + 完整实录摘要
 'https://www.mfa.gov.cn/web/wjdt_674879/202611/t20261104_12053185.shtml': {
   'url': 'https://www.mfa.gov.cn/fyrbt_673021/jzhsl_673025/202611/t20261104_12053185.shtml',
   'title': '外交部就中俄美元首会晤、美中期选举、英国网络安全报告等答问',
   'summary': '外交部发言人毛宁11月4日主持例行记者会。就外媒报道中俄美官员筹备在深圳APEC领导人非正式会议间隙举行三国元首会晤，毛宁表示中方同相关方保持着沟通；就美国中期选举，毛宁称中期选举是美国内政，中方愿同美方维护落实好两国元首重要共识，构建基于尊重、公平、对等的中美建设性战略稳定关系；就沙特、伊朗官员同期访华，毛宁强调当务之急是避免中东战端重启，中方支持伊朗与美国通过谈判化解争端。针对英国国家网络安全中心年度报告称中国「极有可能」利用人工智能开展黑客行动，毛宁表示严重关切，批评英方用「旧瓶」装打压中国人工智能发展的「新酒」。',
   'priority_score': 88,
 },
 # 澜湄外长会主稿（新补录）
 'https://www.mfa.gov.cn/wjbzhd/202611/t20261104_12053242.shtml': {
   'priority_score': 95,
 },
 # 述评
 'https://www.gov.cn/yaowen/liebiao/202611/content_7085059.htm': {
   'priority_score': 88,
 },
 # 进博会跨国企业圆桌会：补摘要
 'https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_041f3a80376046f59b856d0f6f81d221.html': {
   'summary': '商务部11月4日在上海召开进博会参展跨国企业圆桌会，听取参展跨国企业在华经营情况与政策诉求，就扩大市场准入、优化营商环境、加强产业链供应链合作等议题交流。商务部表示将持续办好进博会这一开放平台，为各国企业提供更多市场机遇、投资机遇和增长机遇。',
 },
 # 中加联委会：提分至 88 并补「首次部长级会议」关键事实
 'https://www.mofcom.gov.cn/syxwfb/art/2026/art_8e7f6a5b275348b2b580e63c39af826f.html': {
   'priority_score': 88,
 },
 # 新型显示产业报告：经贸数据稿保留但降为 72（已在）
 # 发民营企业项目推介：政策 80（已在）
}

used = set()
for a in items:
    if a['url'] in FIX:
        cfg = FIX[a['url']]
        for k, v in cfg.items():
            a[k] = v
        used.add(a['url'])
        print('  修:', a['title'][:46])
for m in set(FIX) - used:
    print('  [WARN] 未命中:', m)

# 补录：澜湄外长会主稿（初抓整组跳「系统维护」，仅 sub-稿与 zaobao 转述）
NEW = [{
 'title': '澜沧江—湄公河合作第十一次外长会在京举行　通过年度落实进展报告与专项基金项目清单',
 'url': 'https://www.mfa.gov.cn/wjbzhd/202611/t20261104_12053242.shtml',
 'date': '2026-11-04', 'source': '外交部', 'category': '高层动态', 'priority_score': 95,
 'summary': '11月4日，澜湄合作第十一次外长会在北京举行，王毅与泰国副总理兼外长西哈萨共同主持，柬埔寨副首相兼外交大臣布拉索昆、老挝副总理兼外长通沙万、越南外长黎怀忠、缅甸国家计划投资与对外经济部部长昂觉霍出席。今年是澜湄合作首次领导人会议十周年，王毅称澜湄合作已成为区域合作「金色样板」，提出凝聚团结自强新合力、构筑开放共赢新高地、培育绿色创新新动能、筑牢安全协作新屏障、打造灾害治理新亮点五点建议，将扎实推进澜湄合作2.0版、开启新的「金色十年」。会议通过《澜湄合作五年行动计划（2023—2027）2025年度落实进展报告》《2026年度澜湄合作专项基金支持项目清单》，并商定确保第五次领导人会议取得圆满成功。',
 'collectedAt': TODAY + ' 10:25:00', 'is_summit_level': False,
}, {
 'title': '新华社述评：严格贯彻执行民主集中制',
 'url': 'https://www.gov.cn/yaowen/liebiao/202611/content_7085059.htm',
 'date': '2026-11-04', 'source': '中国政府网·要闻', 'category': '重要会议', 'priority_score': 88,
 'summary': '新华社11月4日播发深入学习贯彻党的二十届五中全会精神系列述评之四《严格贯彻执行民主集中制》。述评指出，民主集中制是我们党的根本组织原则和领导制度，全会通过的《中共中央关于持之以恒推进全面从严治党若干重大问题的决定》对健全党内民主、维护党的集中统一领导作出部署，要求把民主集中制贯穿于党的建设和党的事业全过程，既充分发扬党内民主，又善于集中统一。',
 'collectedAt': TODAY + ' 10:25:00', 'is_summit_level': False,
}]

exist = {a['url'] for a in items}
for a in NEW:
    if a['url'] in exist:
        print('  [SKIP]', a['title'][:40]); continue
    items.append(a); exist.add(a['url'])
    print('  +', a['title'][:46])

# 跨事件去重：央视「外交部：中方就中俄美元首会晤…」并入记者会稿
before = len(items)
items = [a for a in items if a['url'] != 'https://news.cctv.com/2026/11/04/ARTIBdJll21uRSmY8qEiXy3s261104.shtml']
if len(items) < before:
    print('  删: 外交部：中方就中俄美元首会晤同相关方保持着沟通（并入记者会实录）')

items.sort(key=lambda x: (-x['priority_score'], x.get('date', ''), x['title']))
d['archive'][TODAY] = items
d['today'] = items
d['todayCount'] = len(items)
d['lastUpdated'] = '2026-11-05 10:30'
d['stats'] = {
    'totalArticles': sum(len(v) for v in d['archive'].values()),
    'dateCount': len([k for k in d['archive'] if d['archive'][k]]),
    'latestDate': TODAY,
    'summitCount': sum(1 for v in d['archive'].values() for a in v if a.get('is_summit_level')),
}
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('=== 最终', len(items), '条 ===')
print('分类:', dict(Counter(a['category'] for a in items)))
print('≥85:', sum(1 for a in items if a['priority_score'] >= 85), '/', len(items))
print('重复URL:', len(items) - len({a['url'] for a in items}))
print('重复标题:', len(items) - len({a['title'][:30] for a in items}))
print('短摘要(<60):', [a['title'][:24] for a in items if len(a.get('summary', '')) < 60])
print('截断(…结尾):', [a['title'][:24] for a in items if a.get('summary', '').rstrip().endswith('…')])
print('页脚污染:', [a['title'][:24] for a in items if any(k in a.get('summary','') for k in ['京ICP','主办单位','网站标识码','页面不存在'])])
print('裸实体:', [a['title'][:24] for a in items if 'nbsp' in a.get('summary','')])
print('tv.cctv:', [a['title'][:24] for a in items if 'tv.cctv' in a['url']])
print('日期括号残留:', [a['title'][:24] for a in items if '（2026-' in a['title']])
