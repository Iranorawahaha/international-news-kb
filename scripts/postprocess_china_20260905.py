# -*- coding: utf-8 -*-
"""国内新闻看板 LLM 质量后处理 - 2026-09-05 版面
1) 删除低质/重复条目（21条）
2) URL 替换为 gov.cn 官方原文（丁薛祥/张国清/李强签署令）
3) 外交部记者会 URL 改 fyrbt 栏目 + title 尾部日期残留清理
4) 补 5 条真实摘要（据页面原文/官方通稿概括，禁编造）
"""
import json, re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
JSON_PATH = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json'

d = json.load(open(JSON_PATH, encoding='utf-8'))
today_arts = d['archive']['2026-09-05']
print('处理前今日条数:', len(today_arts))

# ---------- 1) 删除清单（URL 精确匹配） ----------
del_urls = {
    # 重复（tv.cctv 版 vs gov.cn 版，留 gov.cn）
    'https://tv.cctv.com/2026/09/04/VIDELc4NFTFzWHxL0st0DGtq260904.shtml',  # 中俄能源论坛贺信(tv) = [12] gov.cn
    'https://tv.cctv.com/2026/09/04/VIDEkC1bUGcRCJ9DZ8ggnIJK260904.shtml',  # 小喇叭贺信强调版(tv) = [5] gov.cn
    # 重复（视频/特稿/多稿合一）
    'https://news.cctv.com/2026/09/04/ARTIAiMooBZfAOoD46G9hZKi260904.shtml',  # 时政纪录片 = [7] gov.cn纪实
    'https://news.cctv.com/2026/09/05/ARTIRucdgv6vOi1G1M8KOZKR260905.shtml',  # 视频画报（微视频类）
    'https://www.zaobao.com/news/china/story20260904-9627865',  # 特稿：从上合到金砖（分析性特稿）
    'https://www.zaobao.com/news/china/story20260905-9629967',  # 特朗普称偕妻访美 = [4] 企代表团(同源)
    'https://www.gov.cn/zhengce/content/202609/content_7080188.htm',  # 电力条例全文页 = [44]签署令新闻
    # 台湾地方政治
    'https://www.zaobao.com/news/china/story20260904-9627018',  # 何志勇参选新竹市长
    # 地方琐事 / 个人叙事 / 地方软稿
    'https://www.zaobao.com/news/china/story20260905-9630026',  # 滁州高空音爆
    'https://news.cctv.com/2026/09/04/ARTIpEuwvpTtOpQZpUHqzxfv260904.shtml',  # 退伍请战书（个人叙事）
    'https://news.cctv.com/2026/09/05/ARTINWMr61AoVoYMWqWlbxw8260905.shtml',  # 福建以汛为令（地方软稿）
    'https://news.cctv.com/2026/09/04/ARTIhWrKeeXdU1iwBhctPjRv260904.shtml',  # 福建省下拨5000万（省级，历史只收中央部委动作）
    # 蹲点故事化 / 专栏 / 综述 / 评述
    'https://news.cctv.com/2026/09/05/ARTIEJ4zcyGpswrUIUwQHYzn260905.shtml',  # 餐厨废油大循环
    'https://news.cctv.com/2026/09/04/ARTIHb67KHxKyPzTn1m5di3p260904.shtml',  # 六张网（经济聚焦专栏）
    'https://jingji.cctv.com/2026/09/05/ARTIiYbGlAEadIq8Gqjppwbf260905.shtml',  # 光伏图景（综述体）
    'https://news.cctv.com/2026/09/04/ARTIrnSeTEomJH2sk73ysyzV260904.shtml',  # 商业航天揽才（故事化）
    'https://news.cctv.com/2026/09/05/ARTIApf9ZUdasQzrGoxBNftS260905.shtml',  # 看指数识经济·物流（栏目化）
    'https://news.cctv.com/2026/09/04/ARTIvcfaTFJMJZ63MElvJVoM260904.shtml',  # 一只鹅产出清单
    'https://news.cctv.com/2026/09/04/ARTIeuSbQ7X5b1cNVB1lxOkP260904.shtml',  # 赛事小票根
    'https://news.cctv.com/2026/09/05/ARTIaCfRHJ5LLfPo8jQ1wqjM260905.shtml',  # 金融政策组合拳（评述体）
    'https://www.zaobao.com/news/china/story20260904-9626162',  # 多家AI服务宕机（科技事件非政务）
}

# 注意：中俄能源论坛保留 gov.cn [12] content_7080210；小喇叭保留 gov.cn [5] content_7080199
kept = [a for a in today_arts if a.get('url') not in del_urls]
removed = [a for a in today_arts if a.get('url') in del_urls]
print('删除条数:', len(removed))
for a in removed:
    print('  -', a.get('category'), '|', (a.get('title') or '')[:45])

# ---------- 2) URL 替换为 gov.cn 原文 ----------
url_map = {
    'https://tv.cctv.com/2026/09/04/VIDEotqiFKIQbj8klmA0wdvB260904.shtml': 'https://www.gov.cn/yaowen/liebiao/202609/content_7080164.htm',  # 丁薛祥东方经济论坛
    'https://tv.cctv.com/2026/09/04/VIDE5J6JkKdRheYIje4yPAMl260904.shtml': 'https://www.gov.cn/yaowen/liebiao/202609/content_7080184.htm',  # 张国清APEC
    'https://tv.cctv.com/2026/09/04/VIDEAjd5xu5O1B3ZaSJNBW1b260904.shtml': 'https://www.gov.cn/yaowen/liebiao/202609/content_7080196.htm',  # 李强签署国务院令
    'https://www.mfa.gov.cn/web/wjdt_674879/202609/t20260904_12016447.shtml': 'https://www.mfa.gov.cn/fyrbt_673021/202609/t20260904_12016447.shtml',  # 外交部记者会栏目
}
for a in kept:
    if a.get('url') in url_map:
        a['url'] = url_map[a['url']]
        print('  URL→', a.get('title','')[:30], '|', a['url'])

# ---------- 3) title 清理（记者会尾部日期残留） ----------
for a in kept:
    t = a.get('title', '')
    if t.endswith('（2026-09-04）'):
        a['title'] = t[:-len('（2026-09-04）')]
        print('  TITLE清理:', a['title'])

# ---------- 4) 补真实摘要 ----------
sum_map = {
    'https://www.zaobao.com/news/china/story20260905-9630065':
        '路透社9月4日引述两名知情者称，习近平拟于9月24日访问华盛顿时率领庞大中国企业代表团随行，此举旨在显示中国愿意支持在美国投资并建立商业关系，也为白宫在中期选举前提供潜在经济获益。一名美国官员称白宫未在追踪一个中国企业高管代表团；路透社无法确定哪些高管将随行。习近平2015年访美曾率包括马云、马化腾及银行与国企高管在内的庞大企业团，签署采购300架波音飞机的协议。',
    'https://www.zaobao.com/news/china/story20260905-9630376':
        '据中央纪委国家监委网站9月5日消息，中国建筑集团有限公司党组成员、副总经理陈勇涉嫌严重违纪违法，目前正接受中央纪委国家监委纪律审查和监察调查。陈勇生于1974年，长期任职建筑行业，2025年任中国建筑集团有限公司副总经理、党组成员及中国建筑股份有限公司副总裁。',
    'https://www.zaobao.com/news/china/story20260905-9630542':
        '中共中央政治局常委、中央纪委书记李希9月1日至3日在贵州调研，强调纪检监察机关要深入学习贯彻习近平党建思想，抓深抓实全面从严治党和反腐败工作；要抓实政治监督，以严明纪律保障换届风清气正，锲而不舍落实中央八项规定精神，一体推进不敢腐、不能腐、不想腐，扎实开展"纪检监察工作规范化法治化正规化建设年"行动。调研期间李希参观遵义会议会址，并在贵阳主持召开座谈会。',
    'https://www.ndrc.gov.cn/xwdt/xwfb/202609/t20260904_1407416.html':
        '9月3日，国家发展改革委副主任岳修虎主持召开"十五五"规划《纲要》重大工程建设推进会议，调度109项重大工程建设进展，加快推进在建项目实施，推动一批新项目尽早开工建设，强化要素保障，压实项目质量和安全管理责任，为实现"十五五"良好开局提供有力支撑。教育部、科技部、工业和信息化部、交通运输部等多部门参加会议。',
    'https://www.mfa.gov.cn/fyrbt_673021/202609/t20260904_12016447.shtml':
        '外交部发言人郭嘉昆9月4日主持例行记者会：回应新加坡52名公民在华被捕（中方依法查处在华外国公民违法犯罪案件并保障当事人权利）；回应美贸易代表格里尔称中美元首会晤将发布农业公告（无信息可提供，双方应共同落实两国元首重要共识）；回应太平洋岛国就导弹试射关切（中方坚持防御性国防政策，从不搞军事扩张，愿同南太国家维护地区和平稳定）；回应越南就西沙群岛声明（西沙群岛是中国固有领土，不存在任何争议）。会后回应韩国光州双年展涉台错误做法（已向韩方提出严正交涉）。',
}
filled = 0
for a in kept:
    if a.get('url') in sum_map and not a.get('summary'):
        a['summary'] = sum_map[a['url']]
        filled += 1
        print('  补摘要:', a.get('title','')[:35])

# ---------- 5) 校验 ----------
print('处理后今日条数:', len(kept))
# 无摘要检查
no_sum = [a for a in kept if not a.get('summary')]
print('仍有空摘要:', len(no_sum), [a.get('title','')[:25] for a in no_sum])
# 归档合规：collectedAt=今日，date∈{9-4,9-5}
bad = []
for a in kept:
    if not str(a.get('collectedAt','')).startswith('2026-09-05'):
        bad.append(('collectedAt', a.get('title','')[:30]))
    if a.get('date') not in ('2026-09-04', '2026-09-05'):
        bad.append(('date', a.get('title','')[:30]))
print('归档违规:', bad if bad else '无')

d['archive']['2026-09-05'] = kept
d['todayCount'] = len(kept)
d['today'] = '2026-09-05'
# stats.totalArticles 重算
total = sum(len(v) for v in d['archive'].values())
d['stats']['totalArticles'] = total
print('stats.totalArticles:', total)

json.dump(d, open(JSON_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('✅ 已保存', JSON_PATH)
