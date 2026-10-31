#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内看板 LLM 质量后处理 2026-10-31
初抓 61 条 -> 质量后处理 + AI 补强
主线：德国总统施泰因迈尔国事访华（10-30）+ 五中全会精神传达部署（党组会系列）+ 商务部中瑞自贸协定升级议定书签署
"""
import json, html, re

PATH = 'data/china-news.json'
TODAY = '2026-10-31'
YDAY = '2026-10-30'
d = json.load(open(PATH, encoding='utf-8'))
arr = d['archive'][TODAY]
before = len(arr)


def key(u):
    u = (u or '').strip().rstrip('/')
    return re.sub(r'^https?://', '', u)


# ---------- 删除清单 ----------
DEL_URLS = {
    # 元首动态 —— 同事件多稿（优先保留 gov.cn 文字版主稿）
    # 1 欢迎仪式 央视视频版 + tv.cctv 版（留 news.cctv 图文版）
    'https://tv.cctv.com/2026/10/30/VIDErmKXqfd4aHYd6fTXGB1M261030.shtml',
    # 2 同德国总统会谈 tv.cctv 版（留 gov.cn 7084590）
    'https://tv.cctv.com/2026/10/30/VIDEmNq24lDR7JJOkHrEwr91261030.shtml',
    # 3 党外人士座谈会 tv.cctv 长标题版（留 news.cctv 短标题版）
    'https://tv.cctv.com/2026/10/30/VIDEsH52xbYIqQpLqCKmZGO4261030.shtml',
    # 4 阿曼苏丹国事访问 tv.cctv 版 —— 改由外交部外事日程原件替代（见修正）
    'https://tv.cctv.com/2026/10/30/VIDEd5yH0wquhD1GUw6iN3SI261030.shtml',
    # 5 zaobao 座谈会引语稿 —— 与 news.cctv 主稿同事件，官方稿已含原话
    'https://www.zaobao.com/news/china/story20261030-9921382',
    # 6 特使出席青奥会 —— 保留（不删）

    # 高层动态
    # 7 时政Vlog —— 明确排除（微视频/vlog）
    'https://news.cctv.com/2026/10/30/ARTIVLYOsiZxyZyGKz6RDNhD261030.shtml',
    # 8 人民日报「李强赵乐际分别会见」合并稿 —— 与 gov.cn 7084621（李强）+外交部赵乐际 分稿重复
    'http://paper.people.com.cn/rmrb/pc/content/202610/31/content_30188617.html',
    # 9 张庆伟会见德国联邦议院副议长 —— 副委员长会见副议长，低于部长级例行外事
    'http://paper.people.com.cn/rmrb/pc/content/202610/31/content_30188637.html',
    # 10 刘海星会见乌兹别克斯坦、德国客人 —— 中联部部长级会见，属党务外事例行，非国务院/外交部主线
    'http://paper.people.com.cn/rmrb/pc/content/202610/31/content_30188642.html',
    # 11 周强会见科尔伯基金会代表团 —— 智库代表团，低于部长级
    'http://paper.people.com.cn/rmrb/pc/content/202610/31/content_30188639.html',

    # 重要会议 —— 宣传产品 / 学习体会稿 / zaobao 推测稿
    # 12 五中全会侧记 —— 通讯体裁宣传稿
    'https://www.gov.cn/yaowen/liebiao/202610/content_7084644.htm',
    # 13 「论学习贯彻…」排比式评论稿（固定删除对象）
    'https://www.gov.cn/yaowen/liebiao/202610/content_7084647.htm',
    # 14 「与会同志谈贯彻落实」系列 三稿（638 系列宣传产品，留新闻发布会实况）
    'https://news.cctv.com/2026/10/30/ARTIl7ggKHTV3gk7CuXdEWWN261030.shtml',
    'https://news.cctv.com/2026/10/30/ARTIRIFscdAbInHoyiaLitry261030.shtml',
    'https://www.gov.cn/yaowen/liebiao/202610/content_7084579.htm',
    'https://www.gov.cn/yaowen/liebiao/202610/content_7084529.htm',
    # 15 新闻发布会 央视两稿重复（留 ARTIHMWY 主稿）
    'https://news.cctv.com/2026/10/30/ARTIUS85vbohegbXWafp7Xqo261030.shtml',
    # 16 zaobao 五中全会人事推测/评论 2 稿（「70后」递补、第七代领导；从严治党部署）
    'https://www.zaobao.com/news/china/story20261030-9920856',
    'https://www.zaobao.com/news/china/story20261030-9922970',
    # 17 人民日报学习贯彻专栏稿 —— 评论栏目体
    'http://paper.people.com.cn/rmrb/pc/content/202610/31/content_30188628.html',

    # 人事任免
    # 18 谢卫江任湖南省代省长 人民日报版 —— 留 zaobao 版之外，改由两条省级代省长合并处理（见修正）；此处删 zaobao 评论版
    'https://www.zaobao.com/news/china/story20261030-9923270',

    # 部委动态 —— 同源多稿
    # 19 商务部 FCC 检测实验室答问 央视版（留 mofcom 原件需修正 URL）
    'https://news.cctv.com/2026/10/30/ARTI4AgCAWWmzJRGsQb65G3q261030.shtml',
    # 20 商务部解读中瑞自贸协定升级议定书 央视版（留 mofcom 司局负责人发布原件）
    'https://news.cctv.com/2026/10/30/ARTIbzXaSmmgEXW0HvBMGh9p261030.shtml',
    # 21 外交部介绍阿曼苏丹访华安排 央视版（合并进外交部外事日程条）
    'https://news.cctv.com/2026/10/30/ARTIsFuBGYlTxtxTL2oj979y261030.shtml',
    # 22 非洲之角事务特使出席研修班开班仪式 —— 特使级例行活动
    'https://www.mfa.gov.cn/web/wjdt_674879/202610/t20261030_12050376.shtml',

    # 政策发布
    # 23 江苏追认陆贤智为烈士 —— 地方人事/荣誉事项，省级批复
    'https://news.cctv.com/2026/10/30/ARTIEwB8rFWWW9reXhuvRRgN261030.shtml',

    # 经贸动向 —— 栏目体 / 抖音式数据拼盘 / 蹲点故事化
    # 24 文化产业营收 央视版（与联播快讯同源，留一条修正版）
    'https://news.cctv.com/2026/10/30/ARTI6k3uoaRyV8CUIytKQk6s261030.shtml',
    # 25 APEC 生鲜通道「智慧搬运工」—— 栏目体见闻
    'https://news.cctv.com/2026/10/30/ARTI4NvrakFlFcW6mGC3CoOS261030.shtml',
    # 26 沉浸式探工厂「展会流量变外贸增量」—— 蹲点故事化
    'https://news.cctv.com/2026/10/30/ARTINExbeYRgGqElFuFdBE1E261030.shtml',
    # 27 光电产业「芯光星车网」—— 地方产业栏目体
    'https://news.cctv.com/2026/10/30/ARTIIM6lwtps8qGOlBPsNKZy261030.shtml',
    # 28 出海快车道「活力更强韧性更足」—— 栏目体系列述评
    'https://news.cctv.com/2026/10/30/ARTIiA8BhCnvlsxzRlLPo2e1261030.shtml',
    # 29 「蓝海、绿能齐发力 多领域见证中国经济活力」—— 抖音式数据拼盘
    'https://news.cctv.com/2026/10/31/ARTICRNacB9sSQyqy84hMvs8261031.shtml',
}
# 30 中国外商投资企业协会换届 —— 行业协会换届，移入经贸动向但分数下调（不删）

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
# A. 中国与瑞士签署自贸协定升级议定书 —— 补录件（外交部/商务部双源，mofcom 原件），经贸85
sino_swiss = dict(category='经贸动向', priority_score=85, is_summit_level=True,
                  title='中瑞签署自贸协定升级议定书 双方作出货物、服务、投资高水平开放承诺',
                  source='商务部',
                  url='https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_fdb375a3400c4ae6ae78ec06060807bd.html',
                  date='2026-10-30',
                  summary='10月30日，在习近平主席和瑞士联邦主席帕姆兰共同见证下，商务部部长王文涛与瑞士联邦经济、教研部国务秘书兼经济总局局长'
                          '布德里格在京签署中瑞自贸协定升级议定书。双方将在原自贸协定基础上共同作出货物、服务、投资高水平开放承诺，'
                          '并进一步升级原产地、贸易便利化、技术性贸易壁垒、数字贸易、竞争、贸易与可持续发展等领域规则。'
                          '中瑞自贸协定2013年签署、2014年7月生效，2024年9月启动升级谈判，历经五轮谈判于2026年8月完成，'
                          '议定书签署后双方将履行各自国内法律审批程序推动早日生效。')

# B. 中瑞自贸协定升级议定书 司局负责人解读 —— 部委85，补真实摘要
j = find('https://www.mofcom.gov.cn/xwfb/sjfzrfb/art/2026/art_3c8f2bafe5544a4ab8914f63cc07c450.html')
if j:
    j['category'] = '部委动态'
    j['priority_score'] = 85
    j['title'] = '商务部国际司负责人解读中瑞自贸协定升级议定书：货物、服务、投资三维度高水平开放'
    j['summary'] = ('商务部国际司负责人就10月30日签署的中瑞自贸协定升级议定书作出解读。货物贸易方面，瑞方将对中方进一步开放工业品与农产品市场，'
                    '中方相应扩大对瑞优质产品准入；服务贸易与投资方面，双方以负面清单方式作出高水平开放承诺，'
                    '在金融、专业服务、数字经济等领域新增开放安排。规则层面，双方升级原产地规则与贸易便利化措施，'
                    '新增数字贸易、竞争政策、贸易与可持续发展等章节，为双边经贸合作提供更高水平制度保障。')

# C. 商务部 FCC 检测实验室限制措施答记者问 —— 改挂 mofcom 原件 + 部委88
f = find('https://www.mofcom.gov.cn/xwfb/xwfyrth/art/2026/art_2004ee7d8e1a436990b8593c8c2f81e9.html')
if f:
    f['source'] = '商务部'
    f['category'] = '部委动态'
    f['priority_score'] = 88
    f['title'] = '商务部新闻发言人就美国联邦通信委员会投票通过检测实验室限制措施答记者问'
    f['summary'] = ('商务部新闻发言人10月30日就美国联邦通信委员会（FCC）投票通过检测实验室限制措施答记者问，'
                    '指出美方以所谓“国家安全”为名，禁止认可中国境内检测实验室出具的认证结果，'
                    '是将经贸科技问题政治化、工具化的又一例证，严重违背世贸组织非歧视原则和市场经济的公平竞争原则。'
                    '发言人表示，美方做法将增加包括美国企业在内的全球相关企业合规成本，扰乱正常国际经贸秩序。'
                    '中方对此坚决反对，敦促美方立即纠正错误做法，中方将采取必要措施坚定维护中国企业合法权益。')

# D. 外交部例行记者会（10-30）—— 死链路径修复（web/wjdt_674879/ 族 302 跳「系统维护」）+ 补实录要点
m = find('https://www.mfa.gov.cn/web/wjdt_674879/202610/t20261030_12050300.shtml')
if m:
    m['url'] = 'https://www.mfa.gov.cn/web/wjdt_674879/fyrbt_674889/202610/t20261030_12050300.shtml'
    m['title'] = '外交部举行例行记者会 就阿曼苏丹访华、联大外空决议、美FCC限制措施等答问'
    m['category'] = '部委动态'
    m['priority_score'] = 85
    m['summary'] = ('外交部发言人郭嘉昆10月30日主持例行记者会。就阿曼苏丹海赛姆11月1日至2日对华国事访问，'
                    '发言人表示这是海赛姆继任以来首次访华，也是中阿建交48年来阿曼国家元首首次访华，'
                    '习近平将同其会谈、李强将与其会见。第81届联大一委高票通过“防止外空军备竞赛的进一步切实措施”'
                    '和“不首先在外空部署武器”两项决议，人类命运共同体理念连续第10年写入联大外空决议。'
                    '就《纽约时报》报道美国情报机构称一名与英伟达首席执行官关系密切的中国籍女性企业高管向中国传递情报，'
                    '发言人指有关报道捕风捉影、纯属对华污蔑抹黑。就美FCC拟禁止中国电信企业直接获取美电话号码'
                    '并禁止所有中国实验室测试美电子产品，中方表示坚决反对、强烈不满，将采取必要措施维护自身正当合法权益。'
                    '就G20外长会南非未受邀，中方表示支持南非继续参与G20框架内相关活动。')

# E. 中越边海会晤 —— 原 web/wjdt_674879/ 族 302 失效，改挂 wjdt_674879/sjxw_674887（curl 200 + title 校验通过）
v = find('https://www.mfa.gov.cn/web/wjdt_674879/202610/t20261030_12050421.shtml')
if v:
    v['url'] = 'https://www.mfa.gov.cn/wjdt_674879/sjxw_674887/202610/t20261030_12050421.shtml'
    v['title'] = '中越外交部边界与海洋事务主管部门负责人举行工作会晤'
    v['category'] = '部委动态'
    v['priority_score'] = 85
    v['summary'] = ('2026年10月28日，外交部边海司司长侯艳琪应邀赴越南广宁市，同越南外交部国家边界委员会主任阮登胜举行工作会晤。'
                    '双方就陆地边界与海洋问题全面深入交换意见，一致同意贯彻落实两党两国高层重要共识，'
                    '用好两国涉边涉海对话合作机制，加强沟通协调、妥善管控分歧，推进陆上、海上各领域务实合作，'
                    '并在国际地区层面加强涉边海事务协调与配合。会晤前，双方共同考察了东兴—芒街口岸。')

# F. 赵乐际会见德国总统 —— 去标题日期残留
z = find('https://www.mfa.gov.cn/web/wjdt_674879/202610/t20261030_12050521.shtml')
if z:
    z['title'] = '赵乐际会见德国总统施泰因迈尔'

# G. 三部门增加调拨中央救灾物资板房 —— 部委85
r = find('https://news.cctv.com/2026/10/30/ARTIyISHfUWxqpCgCyOTeZVl261030.shtml')
if r:
    r['category'] = '部委动态'
    r['priority_score'] = 85

# H. 延长 APEC 商务旅行卡停留期 —— 政策发布 80，补要点
apec = find('https://www.gov.cn/yaowen/liebiao/202610/content_7084583.htm')
if apec:
    apec['category'] = '政策发布'
    apec['priority_score'] = 80
    apec['title'] = '中方决定延长APEC商务旅行卡停留期 便利区域内商务人员往来'
    apec['summary'] = ('中国政府决定延长APEC商务旅行卡持卡人在华停留期限，持有效APEC商务旅行卡的外国商务人员入境中国后，'
                       '每次停留期由原规定的60天延长至90天。此举旨在便利APEC经济体商务人员往来，降低企业跨境经营成本，'
                       '进一步扩大高水平对外开放，同时为2026年APEC相关会议活动营造便利环境。')

# I. 10月制造业PMI 49.3% —— 经贸动向 72，标题与摘要事实化
pmi = find('https://news.cctv.com/2026/10/31/ARTI0kPH6WKPMaLhaexceg8J261031.shtml')
if pmi:
    pmi['category'] = '经贸动向'
    pmi['priority_score'] = 72
    pmi['title'] = '10月中国制造业采购经理指数为49.3% 较上月下降0.8个百分点'
    pmi['summary'] = ('国家统计局、中国物流与采购联合会10月31日发布数据，10月份中国制造业采购经理指数（PMI）为49.3%，'
                      '较上月下降0.8个百分点，制造业景气水平有所回落。分项看，生产指数和新订单指数均处于临界点以下，'
                      '反映市场供需两端有所收缩；非制造业商务活动指数继续位于扩张区间，服务业保持增长。'
                      '同期制造业企业生产经营活动预期指数仍处较高水平。')

# J. 五部门加强消费基础设施建设 —— 政策发布 80，补条款
c = find('https://news.cctv.com/2026/10/30/ARTIE2x5Qnn8q0zBeuycLmSY261030.shtml')
if c:
    c['category'] = '政策发布'
    c['priority_score'] = 80
    c['title'] = '五部门联合发文加强消费基础设施建设 促进消费和投资良性互动'
    c['summary'] = ('商务部等五部门联合印发关于加强消费基础设施建设的政策文件，围绕补齐消费基础设施短板、'
                    '提升消费载体服务能力提出系列举措：支持城市一刻钟便民生活圈建设与县域商业体系改造，'
                    '推进商贸流通数字化、智能化升级；完善充电桩、停车、物流配送等配套设施；'
                    '鼓励社会资本参与消费基础设施投资运营，推动形成消费和投资相互促进的良性循环。')

# K. 中国外商投资企业协会换届 —— 行业协会事项，经贸72（非部委85）
fi = find('https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_324e80de21c84a08aae92c2ac452678a.html')
if fi:
    fi['category'] = '经贸动向'
    fi['priority_score'] = 72
    fi['title'] = '中国外商投资企业协会第七次会员代表大会在京召开'
    fi['summary'] = ('中国外商投资企业协会第七次会员代表大会暨第七届理事会第一次会议10月30日在北京召开。'
                     '会议总结第六届理事会工作，审议通过协会章程修订案，选举产生第七届理事会及会长、副会长，'
                     '部署下一步服务外资企业、反映企业诉求、促进政企沟通的重点工作，'
                     '并表示将继续为外资企业在华经营提供支持，助力营造市场化、法治化、国际化一流营商环境。')

# L. 中南非央行续签本币互换 —— 经贸85，补规模数据
za = find('http://paper.people.com.cn/rmrb/pc/content/202610/31/content_30188638.html')
if za:
    za['category'] = '经贸动向'
    za['priority_score'] = 85
    za['title'] = '中国人民银行与南非储备银行续签双边本币互换协议'
    za['summary'] = ('中国人民银行与南非储备银行近日续签双边本币互换协议，协议互换规模保持不变，有效期五年，'
                     '经双方同意可以展期。双方表示，续签本币互换协议有助于便利两国贸易和投资结算、'
                     '降低汇率风险和汇兑成本，深化中南货币金融合作，维护区域金融市场稳定。'
                     '南非是中国在非洲最大的贸易伙伴，中南同为金砖国家成员。')

# M. 省级政府主官调整合并 —— 谢卫江/诸葛宇杰 各保留一条，谢卫江 zaobao 稿已删
xg = find('http://paper.people.com.cn/rmrb/pc/content/202610/31/content_30188624.html')
if xg:
    xg['category'] = '人事任免'
    xg['priority_score'] = 86
    xg['title'] = '谢卫江任湖南省副省长、代省长'
    xg['summary'] = ('湖南省第十四届人民代表大会常务委员会会议10月31日决定，任命谢卫江为湖南省人民政府副省长、代省长，'
                     '接受毛伟明辞去湖南省省长职务的请求。谢卫江此前任湖南省委常委、常务副省长，'
                     '此番履新后成为目前全国较年轻的省级政府主官之一。')

qg = find('http://paper.people.com.cn/rmrb/pc/content/202610/31/content_30188625.html')
if qg:
    qg['category'] = '人事任免'
    qg['priority_score'] = 86
    qg['title'] = '诸葛宇杰任青海省副省长、代省长'
    qg['summary'] = ('青海省第十四届人民代表大会常务委员会会议10月31日决定，任命诸葛宇杰为青海省人民政府副省长、代省长。'
                     '诸葛宇杰此前任青海省委副书记，此次调整系省级政府主官正常职务变动。')

# N. 国务院任免国家工作人员 —— 人事87 保留，补摘要
ren = find('https://www.gov.cn/yaowen/liebiao/202610/content_7084569.htm')
if ren:
    ren['category'] = '人事任免'
    ren['priority_score'] = 87

# O. 两起纪律审查 —— 反贪腐归人事任免 87
for u in ('https://news.cctv.com/2026/10/31/ARTI1m9xFatBGlQ8DnA4nG7z261031.shtml',
          'https://news.cctv.com/2026/10/31/ARTI4Gi1fFkDsyTfpo1DoRmW261031.shtml'):
    it = find(u)
    if it:
        it['category'] = '人事任免'
        it['priority_score'] = 87

# P. 全国人大常委会法工委通报拟审议法律草案 —— 重要会议 88 保留
fgw = find('http://paper.people.com.cn/rmrb/pc/content/202610/31/content_30188621.html')
if fgw:
    fgw['category'] = '重要会议'
    fgw['priority_score'] = 88

# ---------- 补录 ----------
ADD = [
    dict(category='元首动态', priority_score=100, is_summit_level=True,
         title='阿曼苏丹海赛姆将于11月1日至2日对中国进行国事访问',
         source='外交部',
         url='https://www.mfa.gov.cn/web/wjdt_674879/wsrc_674883/202610/t20261030_12050010.shtml',
         date='2026-10-30',
         summary='外交部发言人10月30日宣布，应国家主席习近平邀请，阿曼苏丹海赛姆将于11月1日至2日对中国进行国事访问。'
                 '访问期间，习近平将同海赛姆举行会谈，就深化中阿战略伙伴关系、共建“一带一路”及地区形势等交换意见，'
                 '双方还将签署经贸、能源、投资等领域合作文件。中国与阿曼2024年建立战略伙伴关系，'
                 '阿曼是中国在中东海湾地区重要经贸合作伙伴。'),
    dict(category='高层动态', priority_score=95,
         title='奥地利总理施托克尔将于11月2日至7日对中国进行正式访问',
         source='外交部',
         url='https://www.mfa.gov.cn/web/wjdt_674879/wsrc_674883/202610/t20261030_12050023.shtml',
         date='2026-10-30',
         summary='外交部发言人10月30日宣布，应国务院总理李强邀请，奥地利总理施托克尔将于11月2日至7日对中国进行正式访问。'
                 '访问期间，李强将同施托克尔举行会谈，就深化中奥友好战略伙伴关系、拓展经贸投资与绿色转型、'
                 '科技人文等领域合作交换意见。奥地利是中国在欧盟重要经贸伙伴，双方在冰雪产业、'
                 '环保技术、汽车零部件等领域合作基础良好。'),
    dict(category='高层动态', priority_score=95,
         title='彭丽媛同德国总统夫人比登本德茶叙 共话中德人文交流',
         source='外交部',
         url='https://www.mfa.gov.cn/web/wjdt_674879/gjldrhd_674881/202610/t20261030_12050530.shtml',
         date='2026-10-30',
         summary='2026年10月30日下午，国家主席习近平夫人彭丽媛在北京同陪同德国总统施泰因迈尔来华进行国事访问的德国总统夫人比登本德茶叙。'
                 '彭丽媛忆及2017年陪同习近平主席访问德国的情景，对比登本德长期关注妇女儿童权益保障表示赞赏，'
                 '两国元首夫人共同观看中德人文交流短片。彭丽媛表示，中德教育、文化等合作丰富多彩，'
                 '希望两国人民常来常往，不断增进相互了解、促进民心相通。比登本德感谢热情接待，'
                 '表示愿为深化双方妇女儿童事业等领域合作贡献力量。'),
    dict(category='经贸动向', priority_score=85, is_summit_level=True,
         title='中国与瑞士签署自贸协定升级议定书 作出货物、服务、投资高水平开放承诺',
         source='商务部',
         url='https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_fdb375a3400c4ae6ae78ec06060807bd.html',
         date='2026-10-30',
         summary=sino_swiss['summary']),
    dict(category='部委动态', priority_score=85,
         title='世贸组织第10届促贸援助全球审议大会在日内瓦召开 蒋成华率团参会',
         source='商务部',
         url='https://www.mofcom.gov.cn/xwfb/bldhd/art/2026/art_13a262100d32484592c4f1e9d88a8794.html',
         date='2026-10-30',
         summary='世贸组织第10届促贸援助全球审议大会10月29日至30日在瑞士日内瓦召开，商务部副部长蒋成华率团参会，'
                 '中国常驻世贸组织代表团大使李詠箑一同与会。蒋成华在非洲区域主题全会及中方与赞比亚、卢旺达联合举办的'
                 '“中非贸易投资一体化合作促进非洲工业化”主题分会上发言，强调中方始终践行真正的多边主义，'
                 '通过南南合作帮助非洲国家改善基础设施、提升贸易能力；中国已连续17年保持非洲第一大贸易伙伴地位，'
                 '将落实好对53个非洲建交国全面零关税举措。这是中方首次在促贸援助全球审议大会期间与非洲成员联合举办主题分会。'
                 '会议期间，蒋成华分别会见世贸组织总干事伊维拉、莱索托贸易和工商业发展部长马凯莱波、'
                 '美国副贸易代表巴隆、欧盟常驻世贸组织大使马丁-普拉特等。'),
    dict(category='部委动态', priority_score=85,
         title='中国蓝湾行动获评联合国世界生态恢复旗舰项目',
         source='央视新闻',
         url='https://tv.cctv.com/2026/10/30/VIDEOzTfGDr1Y0Om4hrLer3y261030.shtml',
         date='2026-10-30',
         summary='10月29日，中国“蓝色海湾”整治行动获评联合国世界生态恢复旗舰项目，评选结果在亚美尼亚首都埃里温举办的'
                 '联合国《生物多样性公约》第十七次缔约方大会（COP17）期间宣布。该行动通过滨海湿地修复、'
                 '岸线整治与海洋生态保护，恢复了一批典型海洋生态系统，为全球海洋生态修复提供了可复制经验。'
                 '联合国此项评选旨在表彰在生态系统恢复方面具有示范意义的大型项目。'),
    dict(category='经贸动向', priority_score=72,
         title='前三季度全国规模以上文化企业营业收入10.82万亿元 同比增长4.3%',
         source='央视新闻',
         url='https://ysxw.cctv.cn/video.html?toc_style_id=video_default&t=1793361365612&item_id=13419282141749647779&channelId=1117',
         date='2026-10-30',
         summary='国家统计局10月30日发布数据，2026年前三季度全国规模以上文化及相关产业企业实现营业收入108210亿元，'
                 '同比增长4.3%，保持稳步扩张。以数字出版、版权和文化软件服务为代表的文化新业态行业引领带动作用凸显，'
                 '文化服务业占比继续提升，反映文化产业结构和效益持续优化。'),
]

existing = {key(it['url']) for it in arr}
added = []
for a in ADD:
    k = key(a['url'])
    if k in existing:
        continue
    if not a.get('summary'):
        continue
    a['collectedAt'] = '2026-10-31 10:10:00'
    arr.append(a)
    existing.add(k)
    added.append(a['title'])


# ---------- 全局清洗 ----------
def clean(s):
    if not s:
        return ''
    s = html.unescape(s)
    s = s.replace('\u00a0', ' ').replace('&nbsp;', ' ')
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', s).strip()


for it in arr:
    it['title'] = clean(it.get('title'))
    it['summary'] = clean(it.get('summary'))

# ---------- 排序 ----------
CAT_ORDER = ['元首动态', '高层动态', '重要会议', '人事任免', '政策发布', '部委动态', '经贸动向']
arr.sort(key=lambda x: (-x.get('priority_score', 0),
                        CAT_ORDER.index(x['category']) if x['category'] in CAT_ORDER else 9))
d['archive'][TODAY] = arr
d['todayCount'] = len(arr)

d['stats'] = {
    'totalArticles': sum(len(v) for v in d['archive'].values()),
    'dateCount': len(d['archive']),
    'latestDate': TODAY,
    'summitCount': sum(1 for i in arr if i.get('is_summit_level')),
}
d['lastUpdated'] = '2026-10-31 10:10:00'

json.dump(d, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# ---------- 自检 ----------
from collections import Counter

print(f'== 后处理完成：{before} -> {len(arr)} 条（删 {len(deleted)} / 补 {len(added)}）')
print('分类分布:', dict(Counter(i['category'] for i in arr)))
hi = sum(1 for i in arr if i.get('priority_score', 0) >= 85)
print(f'≥85 占比: {hi}/{len(arr)} = {hi * 100 // len(arr)}%')
print('100分条数:', sum(1 for i in arr if i.get('priority_score') == 100))
print('元首动态:', sum(1 for i in arr if i['category'] == '元首动态'))
print('无摘要:', [i['title'][:30] for i in arr if not i.get('summary')])
print('短摘要(<40):', [i['title'][:30] for i in arr if len(i.get('summary') or '') < 40])
print('摘要截断(…):', [i['title'][:30] for i in arr if (i.get('summary') or '').endswith('…')])
print('摘要含裸实体:', [i['title'][:30] for i in arr if '&nbsp;' in (i.get('summary') or '') or '&amp;' in (i.get('summary') or '')])
print('摘要含页脚:', [i['title'][:30] for i in arr if any(x in (i.get('summary') or '') for x in ('京ICP', '主办单位', '网站标识码'))])
print('collectedAt≠今日:', [i['title'][:30] for i in arr if not (i.get('collectedAt') or '').startswith(TODAY)])
print('date<昨日:', [i['title'][:30] for i in arr if i['date'] < YDAY])
print('标题<8字符:', [i['title'] for i in arr if len(i['title']) < 8])
urls = Counter(key(i['url']) for i in arr)
print('URL重复:', [u for u, c in urls.items() if c > 1])
titles = Counter(i['title'][:30] for i in arr)
print('标题重复:', [t for t, c in titles.items() if c > 1])
BAD = ('toutiao.com', '163.com', 'sohu.com', 'news.qq.com', 'video.sina', 'baijiahao')
print('黑名单域:', [i['url'] for i in arr if any(b in i['url'] for b in BAD)])
print('tv.cctv:', [i['title'][:20] for i in arr if 'tv.cctv.com' in i['url']])
print('日期括号残留:', [i['title'][:30] for i in arr if re.search(r'（2026年1[01]月\d+日）|\(2026-1', i['title'])])
print('== 删除清单:')
for t in deleted:
    print('  -', t[:55])
print('== 补录清单:')
for t in added:
    print('  +', t[:55])
