#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国内看板 2026-09-09 LLM 后处理（V2.11 归档规则）
===================================================
今日版面初抓 53 条 → 删除 24 条低质/重复/栏目体 → 保留 29 条（修正 10 处）
+ AI 补录 4 条重大漏采（董建华逝世讣告/金湘军死缓/李百安公诉/市监总局反不正当竞争年报）
= 33 条（央视多角度拼盘与外贸同事件四连发为本次主要删源）
"""
import json

JSON_PATH = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json'
TODAY = '2026-09-09'
DATE_OK = ('2026-09-08', '2026-09-09')

d = json.load(open(JSON_PATH, encoding='utf-8'))
archive = d['archive']
items = archive[TODAY]
print(f'处理前今日版面: {len(items)} 条')

# ============ 1. 删除清单（URL 精确匹配防误删） ============
del_urls = [
    # [0] 习近平同英首相通话 zaobao 版 —— 与 [1] gov.cn 要闻版同事件，留权威版
    'https://www.zaobao.com/news/china/story20260908-9646721',
    # [3] 朝鲜国庆贺电 zaobao 版 —— 与 [2] gov.cn 要闻版同事件，留权威版
    'https://www.zaobao.com/news/china/story20260909-9648094',
    # [4] 出访特稿述评"携手推进平等有序的世界多极化" —— 9-8 已删同类述评（同一 URL 被 fetch 重复入池）
    'https://www.gov.cn/yaowen/liebiao/202609/content_7080395.htm',
    # [6] 丁薛祥教材会议 zaobao 版 —— 与 [5] gov.cn 要闻版同事件，留权威版
    'https://www.zaobao.com/news/china/story20260909-9648115',
    # [15] 王毅中东表态 zaobao 摘句 —— 系 [13] 王毅同卡塔尔首相会谈的子集，表态并入 [13] 摘要
    'https://www.zaobao.com/news/china/story20260908-9646021',
    # [18] 张新当选中国羽毛球协会主席 —— 体育社团换届，看板无先例且非政务人事任免
    'https://news.cctv.com/2026/09/08/ARTI0u8yQOoHW76IUVNoOEcu260908.shtml',
    # [28] 武汉通报查封非法辅助生殖场所 —— 地方卫生执法（联合早报微观），非全国性专项行动通报
    'https://www.zaobao.com/news/china/story20260908-9645889',
    # [31] 17.6%外贸多角度央视稿 —— 同 [23] gov.cn 外贸数据事件，删重复
    'https://news.cctv.com/2026/09/08/ARTIPFgZ988OKGitikhNe5b7260908.shtml',
    # [33] 中国8月进出口 zaobao 版 —— 同 [23] 事件，删重复
    'https://www.zaobao.com/news/china/story20260908-9646031',
    # [34] 中国服务贸易如何转型升级 —— 与 [39] 前7个月服务贸易同稿问答体，留 [39] 数据正式版
    'https://news.cctv.com/2026/09/08/ARTIpHEGLefIlghFuRakHMRD260908.shtml',
    # [35] 中国经济底盘稳 —— 宏观述评（jingji.cctv 栏目体，无事件无数据锚点）
    'https://jingji.cctv.com/2026/09/09/ARTIms2RKIJTJOBfBupu40Qs260908.shtml',
    # [36] 外贸17.6%央视消息稿 —— 同 [23] 事件，删重复
    'https://news.cctv.com/2026/09/08/ARTIBYT6fFpTT27Wh9tgLMcz260908.shtml',
    # [38] 数字技术赋能时尚产业 —— 时装周商贸展故事化（会展栏目体）
    'https://news.cctv.com/2026/09/08/ARTIHuMZfTFj3TChhGW7g0pP260908.shtml',
    # [40] 十万卡集群国产算力 —— 同 [20][21] 工信部信息通信"十五五"规划多角度稿（同文件）
    'https://news.cctv.com/2026/09/09/ARTI7ajAcOAjohTcp7eU11t0260909.shtml',
    # [41] 外资企业深度融入产业链 —— 外资观察综述（无具体事件）
    'https://news.cctv.com/2026/09/08/ARTIOl2jqWBWG4vYVgJWwcln260908.shtml',
    # [42] 资本项目开放举措 —— 主题含 8 月末外储数据（9-7 央行增持黄金条目已收录该数据）+开放举措综述
    'https://news.cctv.com/2026/09/08/ARTI69TQRz8wzmzlPczKoPX4260908.shtml',
    # [43] 奔向中国 投资中国 —— 投洽会片花式短稿（标题过短无实质新闻）
    'https://news.cctv.com/2026/09/08/ARTIgN0xSukT96fZ7UDhdEVA260908.shtml',
    # [44] 我国服务贸易新格局加速成型 —— 述评栏目体（引述讲话无事件，[39] 已收数据版）
    'https://news.cctv.com/2026/09/08/ARTIQgIQel9ulD8LIvXPcKLc260908.shtml',
    # [46] 绿色金融"点碳成金" —— 栏目体故事化（绿色贷款数据述评）
    'https://news.cctv.com/2026/09/08/ARTIPfRpSLE09De45lp8EWnv260908.shtml',
    # [47] 观察 | 四者叠加共筑外贸韧性 —— "观察|"栏目体 + 同 [23] 事件
    'https://news.cctv.com/2026/09/08/ARTITOSC5OjVcuqOUtsqaTwa260908.shtml',
    # [48] 财政部贴现国债（五十七期） —— 例行国债发行公告
    'https://news.cctv.com/2026/09/08/ARTIXWKXd9gHR7sOzH495TtP260908.shtml',
    # [49] 财政部贴现国债（五十八期） —— 例行国债发行公告
    'https://news.cctv.com/2026/09/08/ARTIaY1YZomC8qw859yzRAyw260908.shtml',
    # [50] 进出口双双大涨 外贸韧性 —— 同 [23] 事件多角度稿
    'https://news.cctv.com/2026/09/09/ARTI3KM9ApOzSSjPXHiMALQJ260908.shtml',
    # [51] 采购周期缩短50% AI供应链 —— 中物联报告生产应用故事化
    'https://news.cctv.com/2026/09/09/ARTIqvdLSQ82fWr21aBYVCet260909.shtml',
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
    # [7] 周海兵会见芬兰部长：95 高层动态 → 85 部委动态（发改委副主任会见，参照王文涛先例）+ 补摘要
    if 't20260908_1407472' in u:
        a['category'] = '部委动态'
        a['priority_score'] = 85
        a['summary'] = ('9月7日上午，国家发展改革委副主任周海兵在委内会见芬兰经济事务与就业部经济事务部长普伊斯托，就中芬循环'
                        '经济合作、扩大双边投资等共同关心议题交流。周海兵表示，中方高度重视循环经济发展，双方合作基础良好、'
                        '机制运行顺畅，愿同芬方加强政策和技术交流互鉴，欢迎芬兰企业来华投资兴业；普伊斯托表示，芬方高度重视'
                        '循环经济领域对华合作，愿支持两国机构、企业、专家深化循环经济与投资合作。')
        print('✅ [7] 周海兵：高层动态95→部委动态85，摘要补全（ndrc 原文）')
    # [12] 王小洪：zaobao 摘句版 → gov.cn content_7080467 新华社通稿（第五次中国—太平洋岛国执法合作部级对话）
    if 'story20260909-9648277' in u:
        a['url'] = 'https://www.gov.cn/yaowen/liebiao/202609/content_7080467.htm'
        a['source'] = '中国政府网·要闻'
        a['date'] = '2026-09-08'
        a['title'] = '第五次中国－太平洋岛国执法能力与警务合作部级对话在京举行'
        a['summary'] = ('新华社北京9月8日电（记者 董雪）第五次中国－太平洋岛国执法能力与警务合作部级对话8日在京举行，国务'
                        '委员、公安部部长王小洪与瓦努阿图内政部部长纳珀特担任共同主席。王小洪在主旨讲话中指出，该机制建立4年'
                        '来双方互信根基不断筑牢、培训交流走深走实、执法合作务实有效；中方愿同各方认真落实习近平主席和太平洋'
                        '岛国领导人达成的重要共识，积极践行全球发展倡议等四大全球倡议，深化部级对话机制建设，为构建中国－太平'
                        '洋岛国命运共同体作出更大贡献。同日王小洪还分别会见了来华出席全球公共安全合作论坛（连云港）2026年大会'
                        '的国际刑警组织主席菲利普、秘书长乌尔基萨和瓦努阿图内政部部长纳珀特。')
        print('✅ [12] 王小洪：URL→gov.cn content_7080467（新华社通稿），source 中国政府网·要闻，date→9-8，摘要补全')
    # [13] 王毅同卡塔尔会谈：摘要追加中东局势表态（[15] 删除后并入）
    if 'content_7080474.htm' in u:
        a['summary'] = (a.get('summary') or '') + ('会谈中，王毅还就当前中东局势阐述中方立场，强调枪炮施压不是出路，对话谈判'
                       '才是正途，中方支持卡方继续发挥斡旋作用，推动局势降温、早日实现停火止战。')
        print('✅ [13] 王毅卡塔尔：摘要追加中东表态要点（原 [15] 合并）')
    # [16] 韩正会见三国政要：补摘要（mofcom 转载新华社厦门电）
    if 'art_d73541326aba4468b0ecf906147e8f67' in u:
        a['summary'] = ('新华社厦门9月7日电 国家副主席韩正7日下午在厦门分别会见来华出席第二十六届投洽会的保加利亚副总理兼'
                        '经济、投资和工业部长普列夫、柬埔寨副首相兼发展理事会第一副主席孙占托、塞尔维亚副总理兼经济部长梅萨'
                        '罗维奇。韩正表示，愿同保方扩大双边贸易规模、深化互利合作，希望保方积极推动中欧经贸关系健康稳定发展；'
                        '愿落实中柬两国领导人共识、发挥政府间协调委员会作用，深化各领域务实合作、促进贸易投资一体化；今年是'
                        '中塞全面战略伙伴关系建立10周年，愿用好双边自贸协定优惠安排，深化经贸、基础设施、新兴产业等领域合作。')
        print('✅ [16] 韩正会见：摘要补全（新华社厦门电全文要点）')
    # [17] 王祥喜：zaobao 主观标题版 → chinanews 官方通报版，title 中性化 + 摘要（官方通报全文）
    if 'story20260908-9645527' in u:
        a['url'] = 'https://www.chinanews.com.cn/gn/2026/09-08/10692779.shtml'
        a['source'] = '中国新闻网'
        a['title'] = '应急管理部原部长王祥喜严重违纪违法被开除党籍和公职'
        a['summary'] = ('中国官方9月8日通报，应急管理部原党委书记、部长王祥喜严重违纪违法被开除党籍和公职。经查，王祥喜丧失'
                        '理想信念，无视中央八项规定精神，违规收受礼金、接受可能影响公正执行公务的宴请；违反组织原则，在干部'
                        '职务晋升工作中违规为他人谋取利益；廉洁底线失守，利用职务影响为特定关系人经营活动谋取利益；毫无纪法'
                        '底线，将公权力异化为谋取私利的工具，利用职务便利为他人在工程项目承揽、职务晋升等方面谋利，并非法收'
                        '受巨额财物。经中央纪委常委会会议研究并报中央政治局会议审议，决定给予王祥喜开除党籍处分，由国家监委'
                        '给予其开除公职处分，终止其党的二十大代表资格，收缴违纪违法所得，涉嫌犯罪问题移送检察机关依法审查'
                        '起诉。王祥喜2022年12月起任应急管理部部长，2026年1月被查。')
        print('✅ [17] 王祥喜：URL→chinanews 官方通报，source 中国新闻网，title 中性化，摘要补全')
    # [19] 外交部例行记者会：URL 死链 → 顶层 fyrbt_673021 正确栏目，title 去日期残留，摘要补全（实录要点）
    if 'wjdt_674879/202609/t20260908_12018501' in u:
        a['url'] = 'https://www.mfa.gov.cn/fyrbt_673021/202609/t20260908_12018501.shtml'
        a['title'] = '2026年9月8日外交部发言人毛宁主持例行记者会'
        a['summary'] = ('9月8日外交部发言人毛宁主持例行记者会：①就日本政府近期围绕二战历史表态指出，《联合国宪章》"敌国条款"'
                        '至今仍然有效，今年是东京审判开庭80周年，日本应同军国主义彻底切割、以实际行动取信亚洲邻国和国际社会；'
                        '②介绍尼泊尔救灾援助最新进展，第四批紧急援助物资当日启运，中国乡村发展基金会赴尼搭建临时安置点；'
                        '③介绍卡塔尔首相兼外交大臣穆罕默德访华情况，李强总理、王毅外长分别同其会见会谈；④回应金砖峰会，表示'
                        '中方重视金砖合作、支持印度成功举办今年金砖国家领导人会晤；⑤驳斥赖清德歪曲联大2758号决议言论，台湾'
                        '从来不是一个国家，今后也绝无可能；⑥介绍新一期人工智能能力建设研讨班9月7日至12日在北京大学举办，'
                        '落实习近平主席宣布的未来5年面向发展中国家提供5000个人工智能专题研修培训名额。')
        print('✅ [19] 记者会：URL→fyrbt_673021 顶层栏目，title 去残留，摘要补全（9-8 实录要点）')
    # [24] 外交部阿富汗特使：URL 死链 → sjxw_674887 业务动态栏目，title 去日期残留，补真实摘要
    if 'wjdt_674879/202609/t20260908_12018081' in u:
        a['url'] = 'https://www.mfa.gov.cn/web/wjdt_674879/sjxw_674887/202609/t20260908_12018081.shtml'
        a['title'] = '外交部阿富汗事务特使岳晓勇赴巴基斯坦和沙特磋商'
        a['summary'] = ('据外交部消息，2026年8月30日至9月5日，外交部阿富汗事务特使岳晓勇赴巴基斯坦和沙特磋商，与两国主管'
                        '官员就阿富汗局势及共同关心的问题深入交换意见。')
        print('✅ [24] 阿富汗特使：URL→sjxw_674887 栏目，title 去残留，摘要补全（外交部消息稿）')
    # [37] 放心消费培育：72 经贸故事化标题 → 80 政策发布（政策本体：市监总局《通知》）
    if 'ARTIgxH9jDx6lRFsNJzUPSCr260908' in u:
        a['title'] = '市场监管总局发文全面启动放心消费单元和集聚区培育工作'
        a['category'] = '政策发布'
        a['priority_score'] = 80
        a['summary'] = ('国家市场监督管理总局9月8日发布《关于全面开展放心消费单元和集聚区培育的通知》，全面启动放心消费'
                        '主体培育工作：聚焦餐饮、零售、电商、旅游、养老等民生消费领域，培育一批放心消费单元和集聚区，计划'
                        '到2030年全国放心消费集聚区达到5000个以上，推动形成"信用激励+金融支持"等长效治理机制，让守信经营者'
                        '得实惠。')
        print('✅ [37] 放心消费：title→政策本体，72经贸→80政策发布，摘要修正')
    # [45] 欧盟 deadline：补摘要（路透社要点）
    if 'story20260909-9648127' in u:
        a['summary'] = ('据路透社报道，欧盟贸易专员谢夫乔维奇9月8日表示，欧盟将寻求中国承诺采取措施缓解双边日益扩大的贸易'
                        '失衡，争取北京在10月初前采取初步行动，并计划下月初访问北京磋商。磋商优先事项包括应对中国出口激增与'
                        '对欧贸易逆差扩大、消除欧盟商品进入中国市场的障碍，以及明确中国对稀土、成熟制程芯片等关键物资的出口'
                        '安排，可先针对部分出口产品开展试点。谢夫乔维奇警告，若磋商无法取得成效，欧盟将面临寻找其他解决办法'
                        '的巨大政治压力。数据显示，中国去年对欧盟贸易顺差达3606亿欧元，同比增长15%，今年上半年又扩大9%。')
        print('✅ [45] 欧盟 deadline：摘要补全（路透社要点）')
    # [52] 韩正出席投洽会开幕式并致辞：72 经贸 → 95 高层动态（国家副主席新华社通稿）
    if 'content_30179934' in u:
        a['category'] = '高层动态'
        a['priority_score'] = 95
        print('✅ [52] 韩正投洽会开幕式：经贸动向72→高层动态95（新华社通稿）')

# ============ 3. AI 补录 4 条重大漏采（均 curl/WebFetch 验证官方源可达） ============
NEW_ITEMS = [
    {  # A. 董建华逝世讣告（原全国政协副主席、香港首任特首，9-8 晚辞世 9-9 凌晨讣闻）
        "title": "香港特别行政区首任行政长官、全国政协前副主席董建华逝世 享年89岁",
        "url": "https://www.chinanews.com.cn/gn/2026/09-09/10692991.shtml",
        "date": "2026-09-09",
        "source": "中国新闻网",
        "category": "高层动态",
        "priority_score": 95,
        "is_summit_level": False,
        "summary": ('据董建华办公室9月9日凌晨发布消息，全国政协前副主席、香港特别行政区首任行政长官董建华于2026年9月8日'
                    '晚10时许，在亲人陪伴下于医院安详辞世，享年89岁。董建华1937年生于上海，1996年当选香港特别行政区首任'
                    '行政长官人选，1997年7月1日就任香港特区首任行政长官并连任至2005年，后任中国人民政治协商会议第十届、'
                    '十一届全国委员会副主席。'),
        "collectedAt": "2026-09-09 09:45:00"
    },
    {  # B. 山西省原省长金湘军受贿案一审宣判死缓（9-8 信阳中院，1.48亿）
        "title": "山西省原省长金湘军受贿案一审宣判：死刑缓期二年执行",
        "url": "https://www.chinanews.com.cn/gn/2026/09-08/10692780.shtml",
        "date": "2026-09-08",
        "source": "中国新闻网",
        "category": "人事任免",
        "priority_score": 87,
        "is_summit_level": False,
        "summary": ('9月8日，河南省信阳市中级人民法院一审公开宣判山西省委原副书记、省政府原省长金湘军受贿案，以受贿罪判处'
                    '死刑，缓期二年执行，剥夺政治权利终身，并处没收个人全部财产。经审理查明，2004年上半年至2025年4月，'
                    '金湘军利用担任广西玉林市市长、市委书记，防城港市委书记，天津市副市长、市委副书记，山西省委副书记、'
                    '省长等职务便利，为有关单位和个人在企业经营、工程承揽、职务晋升等事项上提供帮助，非法收受财物共计折合'
                    '人民币1.48亿余元。鉴于其受贿犯罪具有未遂情节，归案后如实供述、主动交代监察机关尚未掌握的绝大部分受贿'
                    '事实，认罪悔罪且部分赃款已追缴，对其判处死刑可不立即执行。'),
        "collectedAt": "2026-09-09 09:45:00"
    },
    {  # C. 招商局集团原副总经理李百安涉嫌受贿被提起公诉（最高检指定山东管辖）
        "title": "招商局集团原副总经理李百安涉嫌受贿被提起公诉",
        "url": "https://www.spp.gov.cn/spp/qwfb/202609/t20260908_736302.shtml",
        "date": "2026-09-08",
        "source": "最高人民检察院",
        "category": "人事任免",
        "priority_score": 87,
        "is_summit_level": False,
        "summary": ('招商局集团有限公司原党委委员、副总经理李百安涉嫌受贿一案，由国家监察委员会调查终结，移送检察机关审查'
                    '起诉。经最高人民检察院指定管辖，山东省人民检察院依法以涉嫌受贿罪对李百安作出逮捕决定，近日山东省烟台'
                    '市人民检察院已向烟台市中级人民法院提起公诉。检察机关起诉指控：李百安利用担任中国建筑工程总公司人事部'
                    '副经理、企管部总经理，中国建筑股份有限公司副总经理、投资部总经理，中国中建地产有限公司执行董事、总'
                    '经理，招商局集团有限公司党委委员、副总经理等职务便利及职权地位形成的便利条件，通过其他国家工作人员'
                    '职务上的行为为有关单位和个人谋取利益，非法收受他人财物，数额特别巨大。'),
        "collectedAt": "2026-09-09 09:45:00"
    },
    {  # D. 市场监管总局发布《中国反不正当竞争执法年度报告（2025）》：查处不正当竞争案件1.47万件
        "title": "市场监管总局发布反不正当竞争执法年度报告：2025年查处不正当竞争案件1.47万件",
        "url": "https://www.samr.gov.cn/zt/ndzt/2026n/2026nzggpjzzcxcz/mtbd/art/2026/art_947a8446dba5452881d6d61d6d12c417.html",
        "date": "2026-09-08",
        "source": "市场监管总局",
        "category": "部委动态",
        "priority_score": 85,
        "is_summit_level": False,
        "summary": ('国家市场监督管理总局9月8日发布《中国反不正当竞争执法年度报告（2025）》（中英文版）。报告显示，2025年'
                    '我国共查处各类不正当竞争案件1.47万件、罚没款6.15亿元，其中查处网络不正当竞争案件1932件。该报告在'
                    '2026年全国公平竞争大会期间举行的"强化反不正当竞争 提升反内卷治理效能"专题会议上发布。2025年，市场监管'
                    '总局发布《医药企业防范商业贿赂风险合规指引》，部署开展整治网络不正当竞争行为专项行动，深入推进老年人'
                    '药品、保健品虚假宣传专项整治，遏制私域直播"坑老骗老"乱象。'),
        "collectedAt": "2026-09-09 09:45:00"
    },
]
urls_now = {a.get('url') for a in kept}
for it in NEW_ITEMS:
    if it['url'] not in urls_now:
        kept.append(it)
        print(f"✅ AI 补录: {it['title'][:32]}...")
    else:
        print(f"ℹ️ 补录条目已存在，跳过: {it['title'][:32]}")

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
d['lastUpdated'] = '2026-09-09 09:45'

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
HIST = {'2026-09-03': 36, '2026-09-04': 22, '2026-09-05': 24, '2026-09-06': 10, '2026-09-07': 6, '2026-09-08': 24}
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
