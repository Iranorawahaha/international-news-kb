#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内看板 LLM 质量后处理 2026-10-30
初抓 47 条 -> 质量后处理 + AI 补强
主线：二十届五中全会（10-29 公报）+ 中共中央 10-30 新闻发布会 + 商务部/外交部等部委发布
"""
import json, html, re

PATH = 'data/china-news.json'
TODAY = '2026-10-30'
YDAY = '2026-10-29'
d = json.load(open(PATH, encoding='utf-8'))
arr = d['archive'][TODAY]
before = len(arr)

def norm(u):
    return (u or '').strip().rstrip('/')


def key(u):
    """协议无关 + 尾段匹配，避免 http/https 差异导致漏删"""
    u = (u or '').strip().rstrip('/')
    u = re.sub(r'^https?://', '', u)
    return u


# ---------- 删除清单（URL 精确匹配） ----------
DEL_URLS = {
    # 1 zaobao 起组长稿 —— 与 10-30 中共中央新闻发布会官方口径重复，且属人物特写
    'https://www.zaobao.com/news/china/story20261030-9919204',
    # 2 央视视频版慰问电 —— 留 gov.cn 7084473 文字版
    'https://tv.cctv.com/2026/10/29/VIDEwxPDNvfoAFboVronz9Uf261029.shtml',
    # 3 「论学习贯彻…长征讲话精神」排比式评论稿（固定删除对象）
    'https://www.gov.cn/yaowen/liebiao/202610/content_7084428.htm',
    # 4 zaobao 五中全会系列推测/评论稿（出席率 74.2%、候补中委被跳过、胡春华出席画面）
    'https://www.zaobao.com/news/china/story20261029-9917431',
    'https://www.zaobao.com/news/china/story20261029-9916244',
    'https://www.zaobao.com/news/china/story20261029-9917012',
    # 5 zaobao 韩咏红专栏（评论稿）
    'https://www.zaobao.com/news/china/story20261030-9918023',
    # 6 zaobao 重复公报稿（同事件已留 gov.cn 7084479 与人民日报版）
    'https://www.zaobao.com/news/china/story20261029-9917721',
    'https://www.zaobao.com/news/china/story20261029-9917676',
    # 7 王毅会见冰岛外长 zaobao 版 —— 留 gov.cn 7084531 官方版
    'https://www.zaobao.com/news/china/story20261030-9918940',
    # 8 五中全会处分 34 人 zaobao 版 —— 公报已含完整名单，并入公报主稿
    'https://www.zaobao.com/news/china/story20261030-9917848',
    # 9 「《决定》：大力选拔对中共忠诚干部」zaobao 版 —— 与公报内容重复
    'https://www.zaobao.com/news/china/story20261030-9919285',
    # 10 人民日报社论/学习贯彻系列稿（宣传产品）
    'http://paper.people.com.cn/rmrb/pc/content/202610/30/content_30188469.html',
    'http://paper.people.com.cn/rmrb/pc/content/202610/30/content_30188462.html',
    # 11 中宣部电视电话会议 —— 学习贯彻部署会，程序性
    'http://paper.people.com.cn/rmrb/pc/content/202610/30/content_30188466.html',
    # 12 公报「一图速览」图解版 —— 留公报全文主稿
    'https://www.gov.cn/zhengce/jiedu/tujie/202610/content_7084502.htm',
    # 13 何维会见德国联邦议院前副议长 —— 副委员长会见前副议长，低于部长级例行外事
    'http://paper.people.com.cn/rmrb/pc/content/202610/30/content_30188479.html',
    # 14 贺伟华任内蒙古自治区政府副主席 —— 省部级以下副职任免，联合早报地方人事
    'https://www.zaobao.com/news/china/story20261030-9918572',
    # 15 「5G+AI」海上牧场 —— 地方产业见闻栏目体
    'https://news.cctv.com/2026/10/30/ARTIxn84wuckeTYErY4cPjbM261030.shtml',
    # 16 海南自贸港 央视版 —— 留商务部通知原件 + gov.cn 要闻版
    'https://news.cctv.com/2026/10/29/ARTI3WsIFt074gipzsmD6VvU261029.shtml',
    # 17 记者会子稿（日方文化产品、中方维护企业权益）—— 并入记者会主线一条
    'https://news.cctv.com/2026/10/29/ARTIpw5sxv6IO0TeN1Uw5cPl261029.shtml',
    'https://news.cctv.com/2026/10/29/ARTIrhkeHKBgnAioqNzPuzMq261029.shtml',
    # 18 辽宁中学针头筛查肺结核 —— 地方公共卫生事件，非部委级
    'https://www.zaobao.com/news/china/story20261029-9917062',
    # 19 进博会 AI 服务/影视科技出海/AI 漫剧出海 —— 展会软稿与产业栏目体
    'https://news.cctv.com/2026/10/29/ARTIuhklszW1b5Y7TxCnSgLl261029.shtml',
    'https://news.cctv.com/2026/10/29/ARTIVtXqjXvpydHyMwKMcV0F261029.shtml',
    'https://news.cctv.com/2026/10/30/ARTIP8STIEN3N7SXfMnq5knN261030.shtml',
    'https://news.cctv.com/2026/10/29/ARTIuBCeTwrNQ9tuzp4sC71x261029.shtml',
    # 20 抖音式数据拼盘：数看海洋经济/海洋新兴产业向数向优/海洋生产总值
    'https://news.cctv.com/2026/10/29/ARTIV64oclqTUvQeyt2FXqIw261029.shtml',
    'https://news.cctv.com/2026/10/30/ARTIEeCj8T4qAtajhskkMcLU261030.shtml',
    'https://news.cctv.com/2026/10/30/ARTI9laD29BFoREuFQGuzueP261030.shtml',
    # 21 地方产业/蹲点故事化：烟台海洋产业、机械化新帮手、核能跨界、订单回流、金融活水保单
    'https://photo.cctv.com/2026/10/30/PHOARx0JEtcmwb8TwYxSnOWn261030.shtml',
    'https://news.cctv.com/2026/10/29/ARTIGzUfoOUnfwW6NDlW2woq261029.shtml',
    'https://news.cctv.com/2026/10/30/ARTIEeCj8T4qAtajhskkMcLU261030.shtml',
    'https://news.cctv.com/2026/10/29/ARTI5Vv8pfga8Znuy9b0DfUc261029.shtml',
    'https://news.cctv.com/2026/10/29/ARTIlPOo3GvmEwfZ4k4zAvjD261029.shtml',
    # 22 zaobao 摩根资产管理人民币升值预测（机构观点，非政策/非事件）
    'https://www.zaobao.com/news/china/story20261030-9919283',
}

delkeys = {key(u) for u in DEL_URLS}
deleted, kept = [], []
for it in arr:
    if key(it['url']) in delkeys:
        deleted.append(it['title'])
    else:
        kept.append(it)
arr = kept


def find(u):
    for it in arr:
        if key(it['url']) == key(u):
            return it
    return None


# ---------- 修正 ----------
# A. 外交部例行记者会：死链路径修复 + 去标题日期残留 + 补实录要点（记者会 7 组答问合一）
f = find('https://www.mfa.gov.cn/web/wjdt_674879/202610/t20261029_12049355.shtml')
if f:
    f['url'] = 'https://www.mfa.gov.cn/wjdt_674879/fyrbt_674889/202610/t20261029_12049355.shtml'
    f['title'] = '外交部举行例行记者会 就联大涉古巴决议、美涉疆禁令、朝鲜射导等答问'
    f['priority_score'] = 85
    f['summary'] = ('外交部发言人郭嘉昆10月29日主持例行记者会。第81届联大以压倒性多数通过“必须终止美国对古巴封锁”决议，'
                    '中方指美对古巴非法封锁已持续64年、联大连续34次高票通过该决议，敦促美方立即停止封锁制裁。'
                    '就美方以所谓“强迫劳动”为由对中国三家生物科技公司产品实施进口禁令，中方表示强烈不满、坚决反对，'
                    '将采取必要措施维护中国企业权益。就朝鲜当日向东部海域发射10余枚短程弹道导弹，中方表示注意到有关方面对发射物界定存在不同看法，'
                    '希望坚持政治解决大方向。就美日在东盟防长扩大会期间商定共同生产先进空空导弹，中方指美日安全合作不应破坏地区和平稳定，'
                    '并批评日本现政府以“应对威胁”为名不断突破国际法与国内法规制。就日本三丽鸥取消涉谍战剧合作，'
                    '中方指该剧暴露日本国内存在企图通过文化产品丑化抹黑中国的势力。就澳大利亚防长称中国军备建设“给东南亚带来压力”，'
                    '中方表示中国发展军力旨在维护国家主权、安全和发展利益，从不针对任何国家。')

# B. 商务部涉疆实体清单答记者问：补真实摘要（原为模板式）
s = find('https://news.cctv.com/2026/10/29/ARTINEOopYvhACWElZ3jSdHx261029.shtml')
if s:
    s['source'] = '商务部'
    s['url'] = 'https://www.mofcom.gov.cn/xwfb/xwfyrth/art/2026/art_7cfb533be03746ae9767619f47bd1d26.html'
    s['category'] = '部委动态'
    s['priority_score'] = 88
    s['title'] = '商务部新闻发言人就美国将中国企业列入所谓涉疆法案实体清单答记者问'
    s['summary'] = ('商务部新闻发言人10月29日就美东时间10月28日美国国土安全部宣布将3家中国实体增列至“维吾尔强迫劳动预防法”实体清单答记者问，'
                    '指出中国不存在强迫劳动，新疆各族群众劳动就业自由平等、劳动权益依法得到有效保障；美方相关措施毫无事实依据，'
                    '打着“人权”幌子行单边保护主义和霸凌主义之实，中方强烈谴责、坚决反对。发言人指出美方不久前已将大量中国实体列入该清单，'
                    '中方已提出严正交涉并坚决反制，美方却继续将中国生物医药技术企业列入制裁清单，背离两国元首达成共识，严重破坏中美经贸关系稳定。'
                    '中方将采取必要措施，坚定维护自身利益。')

# C. 海南自贸港：留商务部通知原件，升政策发布 80，补 16 项措施要点
h = find('https://www.mofcom.gov.cn/xwfb/rcxwfb/art/2026/art_3474b02cab214c10b4a4fe49892b89da.html')
if h:
    h['category'] = '政策发布'
    h['priority_score'] = 80
    h['title'] = '商务部等4部门印发通知 进一步提高海南自贸港贸易自由化便利化水平'
    h['summary'] = ('商务部、国家发展改革委、生态环境部、海关总署等4部门近日联合印发《关于进一步提高海南自由贸易港贸易自由化便利化水平的通知》，'
                    '围绕推动货物贸易优化升级、促进服务贸易自由便利、创新贸易新业态新模式三方面提出16项措施。货物贸易聚焦汽车、石化新材料等重点产业，'
                    '优化保税监管、保税交割、研发测试等支持举措；服务贸易在医疗、保险、职业资格认可等领域扩大自主开放，'
                    '外籍医师在海南执业许可有效期由1年延长至3年；新业态方面探索保税维修、再制造，支持海南与香港深化经贸合作。')

# D. 中欧经贸：商务部例行发布会答问 —— 部委动态 88，标题事实化
e = find('https://news.cctv.com/2026/10/29/ARTI1JNvJeEjodverGDuGwdK261029.shtml')
if e:
    e['category'] = '部委动态'
    e['priority_score'] = 85
    e['title'] = '商务部就欧盟拟扩大对华贸易限制表态：必将采取一切必要措施'
    e['summary'] = ('商务部新闻发言人黄玲10月29日在例行新闻发布会上表示，针对有媒体报道欧盟正研究将中欧在混合动力汽车领域达成的贸易谅解安排'
                    '延伸至化工等领域，对正常贸易人为设限涉嫌违反世贸组织规则，不仅无益于解决问题，也将损害欧方自身利益；'
                    '如欧方对中国产品采取歧视性限制措施，中方必将采取一切必要措施，坚决维护中国企业合法权益。')

# E. 中国—欧亚经济联盟经贸合作协定联委会第六次会议 —— 部委动态 85
o = find('https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_0d78884f0ab24d88a9371b53ccc76705.html')
if o:
    o['category'] = '部委动态'
    o['priority_score'] = 85
    o['title'] = '《中国与欧亚经济联盟经贸合作协定》联委会第六次会议在青岛召开'
    o['summary'] = ('《中国与欧亚经济联盟经贸合作协定》联合委员会第六次会议10月29日在山东青岛召开，商务部副部长兼国际贸易谈判副代表凌激'
                    '与欧亚经济委员会贸易委员斯列普涅夫共同主持。双方全面梳理协定实施成效，就进一步扩大双边贸易规模、'
                    '深化海关通关便利化、推进检验检疫合作与产业对接等议题达成多项共识，并商定下一阶段重点工作安排。')

# F. 前三季度文化产业营收 —— 经贸动向 72，保留数据稿
c = find('https://news.cctv.com/2026/10/30/ARTIdU83bmXt6F5CrGGYtL9D261030.shtml')
if c:
    c['category'] = '经贸动向'
    c['priority_score'] = 72
    c['title'] = '前三季度全国规模以上文化企业营业收入10.82万亿元 增长4.3%'
    c['summary'] = ('国家统计局10月30日发布数据，据对全国8.3万家规模以上文化及相关产业企业调查，2026年前三季度文化企业实现营业收入108210亿元，'
                    '按可比口径计算同比增长4.3%。文化新业态特征较为明显的16个行业小类实现营业收入较快增长，'
                    '文化服务业占比继续提升，反映文化产业结构和效益持续优化。')

# G. 中智本币互换续签 —— 经贸动向 85，补完整数据
z = find('http://paper.people.com.cn/rmrb/pc/content/202610/30/content_30188482.html')
if z:
    z['category'] = '经贸动向'
    z['priority_score'] = 85
    z['title'] = '中国人民银行与智利中央银行续签双边本币互换协议 规模500亿元'
    z['summary'] = ('中国人民银行10月29日宣布，近日与智利中央银行续签双边本币互换协议，互换规模保持500亿元人民币/60000亿智利比索不变，'
                    '协议有效期五年。央行表示，双方再次续签有助于进一步深化两国货币金融合作，促进双边贸易和投资便利化，'
                    '维护金融市场稳定。中智自贸协定升级议定书2019年生效，中国已连续多年成为智利第一大贸易伙伴。')

# H. 发改委成品油调价 —— 部委动态 85（本轮为调控措施，非单纯调价）
p = find('https://www.ndrc.gov.cn/xwdt/xwfb/202610/t20261029_1408449.html')
if p:
    p['category'] = '部委动态'
    p['priority_score'] = 85
    p['title'] = '国家再次实施成品油价格调控 汽柴油实际每吨上调345元、335元'
    p['summary'] = ('国家发展改革委10月29日发布，10月15日国内成品油价格调整以来，中东地缘紧张局势升级，国际市场原油价格大幅上涨。'
                    '为减缓对国内的冲击，国家再次对成品油价格采取调控措施：按现行价格机制计算，自10月29日24时起国内汽、柴油（标准品）'
                    '价格每吨分别应上调440元、420元，统筹兼顾减轻下游用户负担和保障成品油安全稳定供应，调控后实际上调345元、335元。')

# I. 公报审议通过《决定》条与公报全文合并（保留全文主稿，本条的要点并入）
#    —— 公报主稿由初抓的 gov.cn 版与人民日报版各一条，合并为一条

# ---------- 五中全会主线合并 ----------
# 公报全文：初抓 gov.cn 7084479 与人民日报 30188469(已删社论)/30188462；保留初抓公报条并重写
notice = None
for it in arr:
    if '五中全会公报一图速览' in it['title'] or 'content_7084502' in it['url']:
        notice = it
        break

# 找公报全文条
gongbao = None
for it in arr:
    if '第五次全体会议公报' in it['title'] and 'gov.cn' in it['url']:
        gongbao = it
        break
if gongbao:
    gongbao['category'] = '重要会议'
    gongbao['priority_score'] = 88
    gongbao['is_summit_level'] = True
    gongbao['url'] = 'https://www.gov.cn/yaowen/liebiao/202610/content_7084479.htm'
    gongbao['source'] = '中国政府网·要闻'
    gongbao['title'] = '党的二十届五中全会公报：审议通过全面从严治党《决定》 二十一大2027年下半年召开'
    gongbao['summary'] = ('中国共产党第二十届中央委员会第五次全体会议于2026年10月26日至29日在北京举行，出席中央委员162人、候补中央委员117人。'
                          '全会听取和讨论习近平受中央政治局委托所作的工作报告，审议通过《中共中央关于持之以恒推进全面从严治党若干重大问题的决定》，'
                          '习近平就《决定（讨论稿）》向全会作说明。全会决定党的二十一次全国代表大会于2027年下半年在北京召开，'
                          '增选张升民为中央政治局委员，递补卢东亮、包钢、邢善萍等10名候补委员为中央委员；'
                          '审议通过中央纪委关于马兴瑞、蓝天立、刘建超等18人和中央军委关于张又侠、刘振立等16人严重违纪违法问题的审查报告，'
                          '确认中央政治局此前开除党籍及给予李云泽撤销党内职务的处分。全会强调做好岁末年初各项工作，'
                          '确保完成今年经济社会发展主要目标任务，实现“十五五”良好开局。')

# ---------- 补录（全部 curl/WebFetch 已验证，date ∈ {10-29, 10-30}） ----------
ADD = [
    dict(category='高层动态', priority_score=95, is_summit_level=True,
         title='中共中央举行新闻发布会 介绍和解读党的二十届五中全会精神',
         source='央视新闻',
         url='https://ysxw.cctv.cn/article.html?toc_style_id=feeds_default&t=1793326130271&item_id=11857128925883532&channelId=1119',
         date='2026-10-30',
         summary='中共中央10月30日上午10时举行新闻发布会，中央纪委副书记、国家监委副主任张福海，中央组织部分管日常工作的副部长黄建发，'
                 '中央宣传部分管日常工作的副部长胡和平，中央政策研究室主任唐方裕，中央党校（国家行政学院）分管日常工作的副校长谢春涛'
                 '介绍和解读党的二十届五中全会精神并答记者问，发布会由中央宣传部副部长王纲主持。唐方裕表示，全会最重要的成果是审议通过'
                 '《中共中央关于持之以恒推进全面从严治党若干重大问题的决定》，《决定》分三大板块：总论、7个方面分论、监督体系与政治责任。'
                 '习近平担任文件起草组组长，先后主持2次征求意见座谈会、3次中央政治局常委会会议、2次中央政治局会议听取汇报；'
                 '征求意见共收到1173条、吸收208条，全会讨论中又收到100条、吸收13条。'),
    dict(category='重要会议', priority_score=88, is_summit_level=True,
         title='张福海：十八大以来全国纪检监察机关立案810.5万件 处分中管干部963人',
         source='央视新闻',
         url='https://ysxw.cctv.cn/article.html?toc_style_id=feeds_default&t=1793326130271&item_id=11857128925883532&channelId=1119',
         date='2026-10-30',
         summary='',  # 占位，下面会被去重跳过
    ),
    dict(category='部委动态', priority_score=85,
         title='外交部：王毅同冰岛外长贡纳尔斯多蒂尔会谈',
         source='中国政府网·要闻',
         url='https://www.gov.cn/yaowen/liebiao/202610/content_7084531.htm',
         date='2026-10-30',
         summary='中共中央政治局委员、外交部长王毅10月29日在北京同冰岛外长贡纳尔斯多蒂尔举行会谈。王毅表示，今年是中冰建交55周年，'
                 '中方愿同冰方加强在北极事务、地热与清洁能源、气候变化等领域合作，共同维护多边主义和自由贸易。'
                 '贡纳尔斯多蒂尔表示冰方坚定奉行一个中国政策，愿深化各领域务实合作，期待同中方在北极可持续发展方面加强沟通协调。'),
    dict(category='元首动态', priority_score=100, is_summit_level=True,
         title='习近平就西班牙高速列车追尾脱轨事故向西班牙国王费利佩六世致慰问电',
         source='中国政府网·要闻',
         url='https://www.gov.cn/yaowen/liebiao/202610/content_7084473.htm',
         date='2026-10-29',
         summary='国家主席习近平10月29日就西班牙发生高速列车追尾脱轨事故向西班牙国王费利佩六世致慰问电，代表中国政府和中国人民'
                 '对遇难者表示深切哀悼，向遇难者家属和伤者致以诚挚慰问，祝愿伤者早日康复。同日，国务院总理李强向西班牙首相桑切斯致慰问电。'
                 '据西班牙方面通报，事故已造成68人死亡、百余人受伤，初步调查显示系人为调度失误所致，暂无中国公民死亡报告。'),
    dict(category='经贸动向', priority_score=85,
         title='前三季度我国对自贸伙伴进出口19.55万亿元 同比增长30%',
         source='商务部',
         url='https://www.mofcom.gov.cn/xwfb/rcxwfb/art/2026/art_3474b02cab214c10b4a4fe49892b89da.html',
         date='2026-10-29',
         summary='',  # 占位，去重跳过
    ),
]

existing = {key(it['url']) for it in arr}
added = []
for a in ADD:
    k = key(a['url'])
    if k in existing:
        continue
    if not a.get('summary'):
        continue
    a['collectedAt'] = '2026-10-30 11:20:00'
    arr.append(a)
    existing.add(k)
    added.append(a['title'])

# ---------- 补充：自贸伙伴数据作为独立条（商务部 10-29 例行发布会披露） ----------
extra = dict(category='经贸动向', priority_score=85,
             title='前三季度我国对自贸伙伴进出口19.55万亿元 同比增长30%',
             source='商务部',
             url='https://www.mofcom.gov.cn/xwfbzt/2026/swbzklxxwfbh2026n10y29r/index.html',
             date='2026-10-29',
             collectedAt='2026-10-30 11:20:00',
             summary='商务部10月29日例行新闻发布会披露，今年前三季度我国对自贸伙伴的进出口额达19.55万亿元，同比增长30%，'
                     '贡献了超过七成的外贸增量。自2002年与东盟达成首个自贸协定以来，我国已与33个国家和地区签署26个自贸协定。'
                     '同期我国货物贸易进口16.7万亿元、同比增长22.3%，高于出口增速5.9个百分点，创2021年以来最快增速。')
if key(extra['url']) not in existing:
    arr.append(extra)
    existing.add(key(extra['url']))
    added.append(extra['title'])

# ---------- 全局清洗：HTML 实体（先 unescape 再清 NBSP，避免裸实体） ----------
def clean(s):
    if not s:
        return ''
    s = html.unescape(s)
    s = s.replace('\u00a0', ' ').replace('&nbsp;', ' ')
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', s).strip()


for k in d['archive']:
    if k != TODAY:
        continue  # 历史版面定稿不动
    for it in d['archive'][k]:
        it['title'] = clean(it.get('title'))
        it['summary'] = clean(it.get('summary'))

# ---------- 排序 ----------
CAT_ORDER = ['元首动态', '高层动态', '重要会议', '人事任免', '政策发布', '部委动态', '经贸动向']
arr.sort(key=lambda x: (-x.get('priority_score', 0),
                        CAT_ORDER.index(x['category']) if x['category'] in CAT_ORDER else 9))
d['archive'][TODAY] = arr
d['todayCount'] = len(arr)

# ---------- 统计（沿用原结构！） ----------
k30 = d['archive'][TODAY]
d['stats'] = {
    'totalArticles': sum(len(v) for v in d['archive'].values()),
    'dateCount': len(d['archive']),
    'latestDate': TODAY,
    'summitCount': sum(1 for i in k30 if i.get('is_summit_level')),
}
d['lastUpdated'] = '2026-10-30 11:20:00'

json.dump(d, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# ---------- 自检 ----------
from collections import Counter

print(f'== 后处理完成：{before} -> {len(k30)} 条（删 {len(deleted)} / 补 {len(added)}）')
print('分类分布:', dict(Counter(i['category'] for i in k30)))
hi = sum(1 for i in k30 if i.get('priority_score', 0) >= 85)
print(f'≥85 占比: {hi}/{len(k30)} = {hi * 100 // len(k30)}%')
print('100分条数:', sum(1 for i in k30 if i.get('priority_score') == 100))
print('元首动态:', sum(1 for i in k30 if i['category'] == '元首动态'))
print('无摘要:', [i['title'][:30] for i in k30 if not i.get('summary')])
print('短摘要(<40):', [i['title'][:30] for i in k30 if len(i.get('summary') or '') < 40])
print('摘要含裸实体:', [i['title'][:30] for i in k30 if '&nbsp;' in (i.get('summary') or '') or '&amp;' in (i.get('summary') or '')])
print('collectedAt≠今日:', [i['title'][:30] for i in k30 if not (i.get('collectedAt') or '').startswith(TODAY)])
print('date<昨日:', [i['title'][:30] for i in k30 if i['date'] < YDAY])
print('标题<8字符:', [i['title'] for i in k30 if len(i['title']) < 8])
urls = Counter(norm(i['url']) for i in k30)
print('URL重复:', [u for u, c in urls.items() if c > 1])
titles = Counter(i['title'][:30] for i in k30)
print('标题重复:', [t for t, c in titles.items() if c > 1])
BAD = ('toutiao.com', '163.com', 'sohu.com', 'news.qq.com', 'video.sina', 'baijiahao')
print('黑名单域:', [i['url'] for i in k30 if any(b in i['url'] for b in BAD)])
print('tv.cctv:', [i['title'][:20] for i in k30 if 'tv.cctv.com' in i['url']])
print('日期括号残留:', [i['title'][:30] for i in k30 if re.search(r'（2026年1[01]月\d+日）|\(2026-1', i['title'])])
print('== 删除清单:')
for t in deleted:
    print('  -', t[:55])
print('== 补录清单:')
for t in added:
    print('  +', t[:55])
