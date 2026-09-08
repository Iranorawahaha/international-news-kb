#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国内看板 2026-09-08 LLM 后处理（V2.11 归档规则）
===================================================
今日版面初抓 39 条 → 删除 20 条低质/重复 → 保留 19 条（修正 8 处） + AI 补录 5 条 = 24 条
（周一窗口：出访回顾反响稿/特稿集中涌现；AI 补录 9-7 重大漏采：反腐判决/部委文件/平陆运河）
"""
import json

JSON_PATH = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json'
TODAY = '2026-09-08'
DATE_OK = ('2026-09-07', '2026-09-08')

d = json.load(open(JSON_PATH, encoding='utf-8'))
archive = d['archive']
items = archive[TODAY]
print(f'处理前今日版面: {len(items)} 条')

# ============ 1. 删除清单（URL 精确匹配防误删） ============
del_urls = [
    # [0] 中埃命运共同体——埃及各界人士高度评价 —— 出访反响稿（各界受访评价），9-5/9-6/9-7 连续删除同类
    'https://www.gov.cn/yaowen/liebiao/202609/content_7080333.htm',
    # [1] 携手推进平等有序的世界多极化 —— 新华社"特稿｜"出访总结述评（无新事件，9-7 删过思想启迪同类署名述评）
    'https://www.gov.cn/yaowen/liebiao/202609/content_7080395.htm',
    # [5] 李强：支持卡塔尔调解斡旋中东局势 —— 与 [4] gov.cn 李强会见卡塔尔首相同事件（联合早报摘句版），留 gov.cn 权威版
    'https://www.zaobao.com/news/china/story20260907-9640731',
    # [8] 王毅：中墨关系不应受第三方影响 —— 与 [7] 人民日报王毅同墨西哥外长会谈同事件（联合早报摘句版），留权威版
    'https://www.zaobao.com/news/china/story20260907-9641306',
    # [10] 商务部新闻发言人就反倾销初裁答记者问 —— 与 [16] 央视"存在倾销"消息稿同事件重复，留 [16]（初裁本体）
    'https://news.cctv.com/2026/09/07/ARTIhGI5N1iPmIH8ePz6pAhp260907.shtml',
    # [15] 中宣部、发改委联合发布"诚信之星" —— 年度评选发布活动，非政策/执法/事件性新闻
    'https://news.cctv.com/2026/09/07/ARTIvtCHsKz1gPiGUoqk5yx4260907.shtml',
    # [20] 财政部应急部拨付2.4亿人民日报版 —— 与 [14] 央视两部门拨付2.4亿同事件（报纸见报延迟版），留央视版
    'http://paper.people.com.cn/rmrb/pc/content/202609/08/content_30179755.html',
    # [21] 为变乱交织的世界提供中国方案（外媒看中国） —— 人民日报评论栏目体（"外媒看中国"）
    'http://paper.people.com.cn/rmrb/pc/content/202609/08/content_30179739.html',
    # [23] 共识聚势 亚太有声——专家热议新华国际传播指数平台报告 —— 论坛活动+专家热议栏目体
    'https://news.cctv.com/2026/09/07/ARTIdW0maEdZsDBRo2QmFHrc260907.shtml',
    # [26] 中国首次针对历史经典产业制定政策文件 —— 与 [19] gov.cn 要闻国新办发布会同事件（联合早报版），留 gov.cn
    'https://www.zaobao.com/news/china/story20260907-9639649',
    # [27] 人工智能让"中国智造"更具吸引力 —— 大湾区科技创新成果展展会报道（地方展会栏目体）
    'https://news.cctv.com/2026/09/07/ARTIjkQiqS8Tljl1sFbNcolQ260907.shtml',
    # [29] 多个重大工程建设"进度条"刷新 —— 综述拼盘（9-5/9-6 删过同类图景/拼盘）
    'https://news.cctv.com/2026/09/07/ARTIRm75CHMwEq7l6qCNgIPp260907.shtml',
    # [30] 夜间经济热度高涨 文艺新玩法亮相上海街市 —— 上海地方文旅（微观地方新闻）
    'https://jingji.cctv.com/2026/09/07/ARTITZrFTIm2tsyo4Yt2rLkT260907.shtml',
    # [32] 高端智能农机装备产业从单点突破迈向全面铺开 —— 黑龙江产业综述（无事件）
    'https://news.cctv.com/2026/09/07/ARTIcrE5zwkK37AFvDlHeULA260907.shtml',
    # [33] 沙丘变身村民增收"致富林" —— 新疆和田故事化报道（蹲点/致富叙事）
    'https://news.cctv.com/2026/09/07/ARTIIYtdKjnyMFupZ58dSxsS260907.shtml',
    # [34] 科技企业"创新出海"加速跑 —— 柏林IFA展中国企业综述（展会栏目体）
    'https://news.cctv.com/2026/09/07/ARTILXESmYH1E4hyxRSlAZGr260907.shtml',
    # [35] 第二十六届投洽会亮点抢先看 —— 预热栏目体（韩正会见投洽会外宾 [9] 已隐含事件，开幕正式稿待后续版面）
    'https://news.cctv.com/2026/09/07/ARTImoazwnDMx9GXzkYMhabP260907.shtml',
    # [36] 第五届数贸会预告央视版 —— 与 [28] 人民日报权威发布同场国新办发布会（数贸会），留权威发布版
    'https://news.cctv.com/2026/09/07/ARTIdDk6b8heK67Sa3jFwp5N260907.shtml',
    # [37] 观察 | 前瞻布局资本落地 —— 央视"观察|"栏目体（8家金融企业增资3600亿事件归 9-6，超今日窗口不入）
    'https://news.cctv.com/2026/09/07/ARTIEVc2WdmlhqJai8f0NC3V260907.shtml',
    # [38] 通道优势赋能产业发展（深入实施自由贸易试验区提升战略） —— 人民日报系列专栏稿
    'http://paper.people.com.cn/rmrb/pc/content/202609/08/content_30179729.html',
]

kept, deleted = [], []
for a in items:
    if a.get('url') in del_urls:
        deleted.append(a)
    else:
        kept.append(a)
print(f'删除: {len(deleted)} 条 | 保留: {len(kept)} 条')

del_set = set(del_urls)
hit = {a.get('url') for a in deleted}
missing = del_set - hit
if missing:
    print('⚠️ 未命中 URL:')
    for u in missing:
        print('  ', u)

# ============ 2. 修正（URL 片段匹配） ============
for a in kept:
    u = a.get('url', '')
    # [2] 王小洪：tv.cctv 视频 URL → gov.cn content_7080367 新华社通稿 + 补真实摘要
    if 'VIDEjQQ0GSmQpG5AxU5AeyLJ260907' in u:
        a['url'] = 'https://www.gov.cn/yaowen/liebiao/202609/content_7080367.htm'
        a['summary'] = ('新华社北京9月7日电 中国—中亚公安内务部长会晤机制非正式会晤9月7日在京举行，国务委员、公安部部长王小洪主持'
                        '并作主旨讲话。王小洪表示，愿同中亚各国合力打击"三股势力"，深化打击跨国犯罪、移民管理、海外利益保护、'
                        '执法能力建设等领域务实合作，加强高质量共建"一带一路"重大项目安保。会上举行中国—中亚执法培训基地视频'
                        '揭牌仪式，王小洪为哈、乌内务部长颁授公安部金质"长城纪念章"，并分别会见吉尔吉斯斯坦、哈萨克斯坦内务部长。')
        print('✅ [2] 王小洪：URL→gov.cn content_7080367，摘要补全（新华社通稿）')
    # [6] 王文涛会见芬兰：95 高层动态 → 85 部委动态（商务部部领导活动，参照 9-4 商务部条目先例）+ 补摘要
    if 'art_bb9622ec1747435d91cab1cca41976d9' in u:
        a['category'] = '部委动态'
        a['priority_score'] = 85
        a['summary'] = ('9月7日上午，商务部部长王文涛会见芬兰经济事务部长普伊斯托，双方就中芬、中欧经贸关系交换意见。王文涛表示，'
                        '欢迎芬兰担任第二十六届中国国际投资贸易洽谈会主宾国，愿用好中芬经贸联委会等机制深化清洁能源、循环经济、'
                        '智能制造、生物制药等领域合作，希望芬方继续为中国企业在芬投资营造公平、开放、非歧视的营商环境；当前形势'
                        '下保持中欧经贸关系总体稳定具有重大意义。')
        print('✅ [6] 王文涛：高层动态95→部委动态85，摘要补全（mofcom 部领导活动页原文）')
    # [11] 李海鹰：URL→四川省纪委监委官方通报，source/date 修正，补官方摘要
    if 'story20260908-9641937' in u:
        a['url'] = 'https://scjc.gov.cn/scjc/scdc/2026/9/7/c5a73c885cb242feaa9bb846cf523e34.shtml'
        a['source'] = '四川省纪委监委'
        a['date'] = '2026-09-07'
        a['summary'] = ('据四川省纪委监委消息，四川航空集团有限责任公司原党委书记、董事长李海鹰涉嫌严重违纪违法，目前正接受四川省'
                        '纪委监委纪律审查和监察调查。李海鹰2015年12月起任川航集团党委书记、董事长，2023年2月退休。')
        print('✅ [11] 李海鹰：URL→scjc.gov.cn 官方通报，source=四川省纪委监委，date→9-7，摘要补全')
    # [12] 外交部记者会：URL wjdt_674879 死链 → fyrbt_673021 正确栏目（同文），title 去日期残留，补真实要点摘要
    if 't20260907_12017452' in u:
        a['url'] = 'https://www.mfa.gov.cn/fyrbt_673021/202609/t20260907_12017452.shtml'
        a['title'] = '2026年9月7日外交部发言人毛宁主持例行记者会'
        a['summary'] = ('9月7日外交部发言人毛宁主持例行记者会：①介绍禁化武组织总干事等8月31日至9月5日访华，赴吉林珲春、敦化、'
                        '哈尔巴岭实地察看日遗化武挖掘回收、销毁作业现场，支持督促日方全面彻底销毁遗弃化武；②回应菲防长涉华言论，'
                        '表示中方不搞大国对抗；③批驳台湾当局对帕劳搞"金元外交"；④强调中委合作受国际法和两国法律保护，中方在委'
                        '合法权益必须得到保护；⑤就中美AI会谈问题表示"中美就人工智能问题保持着沟通"；⑥介绍组织8家外媒记者进入'
                        '西藏吉隆泥石流灾区采访、将及时发布灾情救援最新情况。')
        print('✅ [12] 记者会：URL→fyrbt_673021 正确栏目，title 去残留，摘要补全（9-7 实录要点）')
    # [13] 信息通信行业"十五五"规划：补真实摘要（据央视原文）
    if 'ARTIvF7wZfDfaVw0IbZyyKO3260907' in u:
        a['summary'] = ('工业和信息化部9月7日发布《信息通信行业发展"十五五"规划》。规划提出，预计到2030年全面建成覆盖完善、'
                        '性能领先的新一代通信网，为到2035年基本实现信息通信行业现代化奠定坚实基础。')
        print('✅ [13] 信息通信规划：摘要补全')
    # [16] 反倾销初裁：85 → 88（商务部反倾销=重大执法，参照反制裁/反倾销权重88），补真实摘要
    if 'ARTIIVoIXDPBfkCbbyn2L2l5260907' in u:
        a['priority_score'] = 88
        a['summary'] = ('9月7日，商务部公布对原产于日本的进口二氯二氢硅反倾销调查初步裁定：调查机关初步认定被调查产品存在倾销，'
                        '国内二氯二氢硅产业受到实质损害。自9月8日起，进口经营者在进口被调查产品时，应依据初裁决定确定的各公司'
                        '保证金比率向海关提供相应保证金。')
        print('✅ [16] 反倾销初裁：85→88（重大执法档），摘要补全')
    # [17] 发改委与埃及签署合作文件：补真实摘要（ndrc 发布页原文：习近平访埃期间签署）
    if 't20260907_1407449' in u:
        a['summary'] = ('据国家发展改革委9月7日消息，9月2日在中埃两国元首共同见证下，发改委主任郑栅洁与埃及外交、国际合作和'
                        '海外侨民部负责人签署《关于共建"一带一路"倡议与"2030愿景"对接的重点合作事项谅解备忘录》；习近平主席'
                        '访问埃及期间，郑栅洁还代表国家数据局与埃及通讯和信息技术部负责人签署《关于加强数字经济合作的谅解备忘录》。')
        print('✅ [17] 发改委埃及：摘要补全（ndrc 原文）')
    # [25] 央行增持黄金：补真实摘要（9-7 央行/外汇局数据）
    if 'story20260907-9641433' in u:
        a['summary'] = ('9月7日央行数据显示，8月末我国黄金储备报7673万盎司，环比增加65万盎司（约20.22吨），为2023年10月以来'
                        '单月最大增持量，至此央行已连续第22个月增持黄金。国家外汇局数据显示，截至8月末我国外汇储备规模34383亿'
                        '美元，较7月末上升195亿美元，升幅0.57%。')
        print('✅ [25] 央行黄金：摘要补全')
    # [31] 南宁港外贸首靠：补真实摘要（中新社：平陆运河江海联运前奏）
    if 'story20260908-9641714' in u:
        a['summary'] = ('9月7日晚，巴拿马籍外贸船舶"北港南宁博润"靠泊广西南宁港六景作业区，南宁港迎来历史上首次外贸船舶靠泊'
                        '作业，装卸完成后将开往越南芹苴港。南宁市交通运输局称，此举打通内河外贸通航通道，助力南宁由内陆腹地城市'
                        '向区域性开放门户转型，为平陆运河全线通航、江海联运常态化运营积累实践经验。')
        print('✅ [31] 南宁港：摘要补全（中新社）')

# ============ 3. AI 补录 5 条（date=9-7 重大漏采，均 curl 验证 URL 200） ============
NEW_ITEMS = [
    {  # A. 证监会原副主席王建军受贿案一审无期（9-7 潍坊中院宣判，副部级反腐判决）
        "title": "中国证监会原副主席王建军受贿案一审宣判 获无期徒刑",
        "url": "https://news.cctv.com/2026/09/07/ARTI30aNbJ3M30KMjCzwmTBy260907.shtml",
        "date": "2026-09-07",
        "source": "央视新闻",
        "category": "人事任免",
        "priority_score": 87,
        "is_summit_level": False,
        "summary": ('9月7日，山东省潍坊市中级人民法院一审公开宣判中国证监会原党委委员、副主席王建军受贿案，以受贿罪判处其'
                    '无期徒刑，剥夺政治权利终身，并处没收个人全部财产。经审理查明，2005年上半年至2019年9月，王建军利用担任'
                    '证监会云南监管局副局长、办公厅副主任、市场监管部主任等职务便利，为有关单位和个人在公司上市、企业融资等'
                    '方面谋利，非法收受财物共计9340万余元；鉴于其到案后如实供述、认罪悔罪、部分赃款追缴，依法从轻处罚。'),
        "collectedAt": "2026-09-08 09:26:00"
    },
    {  # B. 六部门乡村振兴投入机制实施方案（农业农村部等 9-7 印发）
        "title": "农业农村部等六部门联合印发《坚持农业农村优先发展 完善乡村振兴投入机制实施方案》",
        "url": "https://www.gov.cn/lianbo/202609/content_7080359.htm",
        "date": "2026-09-07",
        "source": "中国政府网",
        "category": "政策发布",
        "priority_score": 80,
        "is_summit_level": False,
        "summary": ('新华社北京9月7日电 农业农村部、中央农办、国家发展改革委、财政部、中国人民银行、金融监管总局近日联合印发'
                    '《坚持农业农村优先发展 完善乡村振兴投入机制实施方案》，提出到2030年基本建立与农业农村发展水平相适应、'
                    '结构合理、方式科学、质效并重的乡村振兴投入机制；从强化政府资金优先保障、发挥债券资金支农作用、提升信贷'
                    '资金支农效能、用好保险支农政策工具、激发民间投资活力、盘活用好农村资源资产六方面健全多元投入格局。'),
        "collectedAt": "2026-09-08 09:26:00"
    },
    {  # C. 工信部+市场监管总局 汽车账期管理通知（国家层面首个行业账期管理文件）
        "title": "工信部、市场监管总局联合发文 推动汽车企业规范供应商账款支付优化账期管理",
        "url": "https://www.chinanews.com.cn/cj/2026/09-07/10692257.shtml",
        "date": "2026-09-07",
        "source": "中国新闻网",
        "category": "政策发布",
        "priority_score": 80,
        "is_summit_level": False,
        "summary": ('工业和信息化部、市场监管总局9月7日联合发布《关于推动汽车企业规范供应商账款支付 优化账期管理的通知》，系'
                    '国家层面首个面向行业领域的账期管理文件。通知明确账期自供应商交付货物并验收合格之日起算，一般生产性物料'
                    '应在3个工作日内完成验收，鼓励汽车企业自验收合格之日起30天内完成中小企业供应商货款支付、最长不超过60天，'
                    '不得强迫或变相强迫供应商接受商业承兑汇票、供应链票据等非现金支付方式。'),
        "collectedAt": "2026-09-08 09:26:00"
    },
    {  # D. 最高法涉AI纠纷案件意见（首部国家最高审判机构 AI 司法裁判规则文件）
        "title": "最高法发布《关于依法审理涉人工智能纠纷案件的意见》 首部涉AI司法裁判规则文件",
        "url": "https://www.court.gov.cn/zixun/xiangqing/511101.html",
        "date": "2026-09-07",
        "source": "最高人民法院",
        "category": "政策发布",
        "priority_score": 80,
        "is_summit_level": False,
        "summary": ('最高人民法院9月7日发布《关于依法审理涉人工智能纠纷案件的意见》，系首部由国家最高审判机构发布的涉人工智能'
                    '司法裁判规则文件，共5部分24条。意见聚焦"AI换脸拟声""AI幻觉"侵权、"网络开盒""大数据杀熟"、自动驾驶、'
                    '模型训练、开源软件等突出问题，明确涉AI侵权归责原则，依法规制利用生成式AI侵害姓名权、肖像权、声音权益、'
                    '名誉权、隐私权等行为，明确生成式AI服务提供者责任及自动驾驶交通事故赔偿等实体裁判和诉讼程序规则。'),
        "collectedAt": "2026-09-08 09:26:00"
    },
    {  # E. 平陆运河 9-16 建成通航（世纪工程，西部陆海新通道骨干工程）
        "title": "平陆运河将于9月16日建成通航 我国西南新增江海联运大通道",
        "url": "https://www.cnr.cn/newscenter/local/dftj/20260907/t20260907_527806941.shtml",
        "date": "2026-09-07",
        "source": "央广网",
        "category": "经贸动向",
        "priority_score": 85,
        "is_summit_level": False,
        "summary": ('9月7日广西壮族自治区政府新闻发布会宣布：新中国成立以来我国首条国家层面统筹建设的通江达海运河工程——平陆'
                    '运河将于9月16日建成通航。运河2022年8月28日开工，总投资约727亿元，全长134.2公里，北起南宁横州市平塘'
                    '江口、沿钦江南至北部湾，按内河I级标准建设可通航5000吨级船舶，全线建成马道、企石、青年三大梯级枢纽；通航'
                    '后西南货物经运河出海缩短内河航程560公里以上，综合物流成本降低18%—30%。'),
        "collectedAt": "2026-09-08 09:26:00"
    },
]
urls_now = {a.get('url') for a in kept}
for it in NEW_ITEMS:
    if it['url'] not in urls_now:
        kept.append(it)
        print(f"✅ AI 补录: {it['title'][:30]}...")
    else:
        print(f"ℹ️ 补录条目已存在，跳过: {it['title'][:30]}")

# ============ 4. 排序（分数降序） ============
kept.sort(key=lambda x: -x.get('priority_score', 0))
archive[TODAY] = kept

# ============ 5. 更新元数据 ============
all_items = []
for day, arts in archive.items():
    all_items.extend(arts)
d['todayCount'] = len(kept)
d['stats'] = {
    'totalArticles': len(all_items),
    'dateCount': len(archive),
    'latestDate': TODAY,
    'summitCount': sum(1 for a in all_items if a.get('is_summit_level')),
}
d['lastUpdated'] = '2026-09-08 09:40'

# ============ 6. 归档规则校验 ============
print()
print('=== 归档校验 ===')
err = 0
for day, arts in archive.items():
    for a in arts:
        ca = str(a.get('collectedAt', ''))[:10]
        dt = a.get('date', '')
        if day == TODAY:
            if ca != TODAY:
                print(f'  ⚠️ 今日版面 collectedAt≠今日: {a.get("title","")[:30]} ca={ca}')
                err += 1
            if dt not in DATE_OK:
                print(f'  ⚠️ 今日版面 date 超窗口: {a.get("title","")[:30]} date={dt}')
                err += 1
        else:
            if dt >= TODAY:
                print(f'  ⚠️ 历史版面混入今日 date: {day} | {a.get("title","")[:30]} date={dt}')
                err += 1
print(f'  违规数: {err}')

# 历史版面条数快照（防误动）
HIST = {'2026-09-04': 22, '2026-09-05': 24, '2026-09-06': 10, '2026-09-07': 6}
for day, expect in HIST.items():
    n = len(archive.get(day, []))
    mark = '✅' if n == expect else '⚠️ 变动!'
    print(f'  {day}: {n} 条（应 {expect}）{mark}')

# ============ 7. 分类/分数分布 ============
cats = {}
for a in kept:
    cats.setdefault(a.get('category'), 0)
    cats[a.get('category')] += 1
scores = [a.get('priority_score', 0) for a in kept]
high = sum(1 for s in scores if s >= 85)
print(f'  分类: {cats}')
print(f'  分数≥85: {high}/{len(kept)} = {high/len(kept)*100:.0f}%')
nosum = [a.get('title', '')[:30] for a in kept if not a.get('summary')]
print(f'  无摘要: {len(nosum)}', nosum if nosum else '')

# gov.cn 要闻 boost 校验
print('=== gov.cn 要闻 boost 校验 ===')
for a in kept:
    if a.get('source') == '中国政府网·要闻':
        ok = (a.get('category') in ('人事任免',) and a.get('priority_score', 0) >= 87) or \
             (a.get('category') in ('部委动态',) and a.get('priority_score', 0) >= 88) or \
             (a.get('category') in ('经贸动向',) and a.get('priority_score', 0) >= 85) or \
             a.get('category') in ('元首动态', '高层动态', '重要会议')
        print(f"  {'✅' if ok else '⚠️'} {a.get('title','')[:35]} | {a.get('category')} | {a.get('priority_score')}")

json.dump(d, open(JSON_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print()
print(f'✅ 已保存 {JSON_PATH} | 今日版面: {len(kept)} 条')
