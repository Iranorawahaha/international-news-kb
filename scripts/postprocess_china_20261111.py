# -*- coding: utf-8 -*-
"""国内看板 2026-11-11 后处理：删除低质/重复条目 + 修复死链与摘要 + 补录漏采硬新闻"""
import json, re, io, sys

JSON_PATH = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json'
TODAY = '2026-11-11'

data = json.load(open(JSON_PATH, encoding='utf-8'))
today = data['archive'][TODAY]
hist = {d: items for d, items in data['archive'].items() if d != TODAY}

# ---------- 删除清单（按标题前缀匹配，唯一命中才删） ----------
DELETE = [
    # 1) 跨期重复：11-10 版面已用 gov.cn / MFA 原件收录，今日又以 tv.cctv 聚合页 / 人民日报纸版二次收录
    '习近平同志《论减贫脱贫》出版发行',
    '何立峰与加拿大财政部长商鹏飞、国际贸易部长西杜共同主持第二次中加经济财金战略对话',
    '张国清在上海调研时强调',
    '王毅同斯洛伐克外长布拉纳尔会谈',
    '王毅同法国外长巴罗通电话',
    '王沪宁会见老挝建国阵线中央委员会副主席布沙迪',
    '赵乐际会见哥伦比亚多党干部考察团',
    # 2) 宣传产品 / 评论体
    '拾光纪',                      # 央视宣传产品（孙中山诞辰 160 周年短片）
    '严格贯彻执行民主集中制',        # 学习贯彻全会精神评论员文章
    # 3) 中央宣讲团（6 条同主题只保留 1 条汇总稿，全部删除后补 1 条汇总）
    '学习贯彻党的二十届五中全会精神中央宣讲团',
    '中央宣讲团',
    # 4) 数据拼盘 / 栏目体 / 蹲点稿
    'APEC深圳之约',
    '“数”里行间解锁前10个月中国外贸',
    '中国接住全球创新让其长成为下一个产业起点',
    '各地精准发力瞄准特色产业发展',
    '新疆塔克拉玛干沙漠生态成果持续释放产业效益',
    '筑牢底座物理AI基础设施加速构建',
    # 5) 同事件多稿（外贸 44.81 万亿保留央视经济频道权威版 1 条）
    '同比增长20% 我国外贸活力持续彰显',
    '货物贸易进出口总值同比增20%',
    # 6) 微观 / 社会个案
    '安徽合肥市肥东县发生3.0级地震',
    '工信部批复10家企业开展号码保护服务业务试点',
    '市场监管总局发布《自愿性认证合同汇编（示范文本）》',
    # 7) 署名理论文章
    '石泰峰：增强党性是全面从严治党的根本性任务',
    # 8) 联合早报（转述/时政外溢/微观）
    '加拿大总理卡尼将向习近平提出中国干预内政问题',
    '日媒：高市与习近平深圳APEC会谈协调不顺',
    'APEC峰会前夕 深港澳加强保安',
    '中国科技企业亮相全球网络峰会',
    '台媒：宏碁创办人施振荣将出任台湾APEC领袖代表',
    '履新两个月转正 钟得志当选广西首府南宁市长',
    '新加坡与江苏签署23项合作文件',
    '安世半导体CEO：仍有可能与中国业务重新整合',
    '王毅与法外长通话：中欧合则两利斗则俱伤',   # 与人民日报/外交部版重复
    '王毅同法国外长通话 吁发挥作用推动中欧经贸合作',  # 同上
    # 9) 汇编/评论类进博会综述
    '为世界经济注入更多确定性和正能量',
]

def norm(t):
    return re.sub(r'[\s，。、；：“”‘’（）()《》·|—\-]', '', t or '')

kept, removed = [], []
for it in today:
    t = it.get('title') or ''
    if any(t.startswith(p) or p in t for p in DELETE):
        removed.append(t)
    else:
        kept.append(it)

# ---------- 修复 ----------
def find(title_kw):
    for it in kept:
        if title_kw in it.get('title', ''):
            return it
    return None

# 1) 外交部 11-10 例行记者会：改挂真链 + 补写实录摘要
mfa = find('外交部发言人郭嘉昆主持例行记者会')
if mfa:
    mfa['url'] = 'https://www.mfa.gov.cn/wjdt_674879/fyrbt_674889/202611/t20261110_12056801.shtml'
    mfa['source'] = '外交部'
    mfa['date'] = '2026-11-10'
    mfa['category'] = '部委动态'
    mfa['priority_score'] = 88
    mfa['summary'] = (
        '外交部发言人郭嘉昆11月10日主持例行记者会，就中美元首互动、大熊猫合作等答问。'
        '就大熊猫“平平”“福双”在亚特兰大动物园正式与公众见面，他表示这是习近平主席9月对美国进行国事访问期间宣布的合作成果，'
        '相信新一轮中美大熊猫合作将推进全球生物多样性保护、增进中美人民友谊。'
        '就所谓“中国间谍”论调，他强调纯属捕风捉影、污蔑抹黑；'
        '关于中美元首会晤及中俄美三方会晤安排，他表示中方同相关方保持着沟通，目前没有可提供的信息。'
    )

# 2) 非洲之角特使（司局级、链接失效）已在 DELETE 之外单列 —— 直接移除
kept = [it for it in kept if '非洲之角事务特使' not in it.get('title', '')]

# 3) 发改委三条拆条 → 合并为 1 条发布会主稿
ndrc_items = [it for it in kept if '国家发展改革委' in it.get('title', '') and '民生' not in it.get('title', '')]
ndrc_main = [it for it in kept if '国家发展改革委：140亿元中央预算内投资投向养老托育设施' in it.get('title', '')]
if ndrc_items:
    base = ndrc_main[0] if ndrc_main else ndrc_items[0]
    for it in ndrc_items:
        if it is not base:
            kept.remove(it)
    base['title'] = '国家发展改革委举行“十五五”民生福祉发布会：140亿元投向养老托育，多渠道增加高中学位'
    base['category'] = '部委动态'
    base['priority_score'] = 85
    base['source'] = '央视新闻'
    base['date'] = '2026-11-10'
    base['summary'] = (
        '国家发展改革委11月10日召开奋进“十五五”系列新闻发布会，介绍增进民生福祉有关情况。'
        '会议披露，“十五五”时期将安排140亿元中央预算内投资投向养老托育设施建设，'
        '多渠道增加普通高中和高等教育学位供给以缓解学位供需矛盾，'
        '并进一步完善重要民生商品价格调控机制，实施更加公平普惠、精准有力的社会政策。'
    )

# 4) 基金会管理条例：保留央视答记者问，标题/摘要规范化
fd = find('基金会管理条例')
if fd:
    fd['title'] = '司法部、民政部负责人就修订后的《基金会管理条例》答记者问'
    fd['category'] = '政策发布'
    fd['priority_score'] = 85
    fd['summary'] = (
        '修订后的《基金会管理条例》自2027年1月1日起施行。司法部、民政部负责人11月10日就条例修订答记者问，'
        '介绍修订在规范基金会设立与治理、强化公开透明、完善监督管理、健全法律责任等方面的主要考虑，'
        '并就登记管理权限、慈善财产使用、信息公开义务等社会关切作出说明。'
    )

# 5) 刘海星会见：中联部部长属正部级，保留但摘要规范化
lx = find('刘海星分别会见')
if lx:
    lx['summary'] = (
        '中共中央对外联络部部长刘海星11月10日在北京分别会见刚果劳动党总书记穆萨和意大利前总理达莱马，'
        '就落实双方领导人共识、加强党际交流合作、推动中非和中欧关系发展等交换意见。'
    )

for it in kept:
    s = it.get('summary') or ''
    s = s.replace('&nbsp;', ' ').replace('&amp;nbsp;', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    it['summary'] = s

# ---------- 补录 ----------
ADD = [
    dict(
        title='中国海警舰艇首次对马来西亚进行港口访问 三都舰抵达槟城',
        source='央视新闻', date='2026-11-10', category='部委动态', priority_score=85,
        url='https://ysxw.cctv.cn/article.html?toc_style_id=feeds_default&item_id=10305326459971263913&channelId=1119',
        summary='11月10日，中国海警三都舰抵达马来西亚槟城瑞典咸港，开始为期四天的友好访问，这是中国海警舰艇首次对马来西亚进行港口访问。'
                '马来西亚海事执法局及当地华人华侨在港口举行欢迎仪式并登舰参观，双方将首次开展海上搜救、专业研讨、编队训练等课目交流，'
                '访问期间还将举行舰艇开放日和甲板招待会，进一步深化海上执法务实合作。'
    ),
    dict(
        title='宁波舟山港年集装箱吞吐量再破4000万标箱 较去年提前22天',
        source='中国政府网·要闻', date='2026-11-10', category='经贸动向', priority_score=85,
        url='https://news.china.com.cn/2026-11/10/content_118769299.shtml',
        summary='截至11月10日，宁波舟山港2026年集装箱吞吐量突破4000万标箱，连续第二年站上这一量级，较去年提前22天。'
                '目前全港集装箱航线超310条，连接全球200多个国家和地区的700多个港口，港口连通性指数居全球第二；'
                '海铁联运线路达115条、辐射16省71市，今年运量超180万标箱，中欧北极快航通航季完成8个航次、单程20天抵欧。'
    ),
    dict(
        title='前10个月全国二手房交易网签面积同比增长11.4%',
        source='央视新闻', date='2026-11-10', category='经贸动向', priority_score=72,
        url='https://tv.cctv.com/2026/11/10/VIDE0Fo6dZ6TdNIyG7G1CWL1261110.shtml',
        summary='住房城乡建设部11月10日披露，今年前10个月全国二手房交易网签面积67971万平方米，同比增长11.4%，'
                '全国二手房单月交易量已连续7个月同比增长超过10%，反映存量房市场活跃度持续回升。'
    ),
    dict(
        title='国家卫健委等四部门印发通知 优化创新药进院流程、不限制药品品规总量',
        source='央视新闻', date='2026-11-10', category='政策发布', priority_score=80,
        url='https://tv.cctv.com/2026/11/10/VIDE0Fo6dZ6TdNIyG7G1CWL1261110.shtml',
        summary='国家卫生健康委等四部门11月10日联合印发通知，要求各地二级以上医疗机构优化创新药进院流程，按需纳入用药目录，'
                '并明确不限制医疗机构药品品规总量，优化临床使用环境，加强创新药安全合理配备使用。'
    ),
    dict(
        title='2026年第九期、第十期储蓄国债（电子式）11月10日起发行',
        source='央视新闻', date='2026-11-10', category='政策发布', priority_score=72,
        url='https://tv.cctv.com/2026/11/10/VIDE0Fo6dZ6TdNIyG7G1CWL1261110.shtml',
        summary='财政部、中国人民银行安排发行的2026年第九期和第十期储蓄国债（电子式）11月10日起发行，为今年最后一批储蓄国债。'
                '第九期期限3年、票面年利率1.63%，第十期期限5年、票面年利率1.70%，发行期至11月19日，'
                '单一国债账户购买单期金额上限为50万元。'
    ),
    dict(
        title='学习贯彻党的二十届五中全会精神中央宣讲团在各地各部门宣讲',
        source='央视新闻', date='2026-11-10', category='重要会议', priority_score=88,
        url='https://tv.cctv.com/2026/11/10/VIDEU4YRvvFeBeGobdH0jMj4261110.shtml',
        summary='连日来，学习贯彻党的二十届五中全会精神中央宣讲团在全国人大机关、国务院办公厅机关、全国政协机关、'
                '中央军委机关以及广西、四川、宁夏等地宣讲，并与基层干部群众互动交流，推动全会精神学习走深走实。'
                '李鸿忠、吴政隆、穆虹、张玉卓、谢春涛、周新群等分别作宣讲报告。'
    ),
]
existing_urls = {it['url'] for it in kept}
existing_titles = {norm(it['title'])[:30] for it in kept}
for a in ADD:
    if a['url'] in existing_urls or norm(a['title'])[:30] in existing_titles:
        continue
    a['collectedAt'] = '2026-11-11'
    kept.append(a)
    existing_urls.add(a['url'])
    existing_titles.add(norm(a['title'])[:30])

# ---------- 排序 ----------
CAT_ORDER = {'元首动态': 0, '高层动态': 1, '重要会议': 2, '人事任免': 3, '部委动态': 4, '经贸动向': 5, '政策发布': 6}
kept.sort(key=lambda x: (-(x.get('priority_score') or 0), CAT_ORDER.get(x.get('category'), 9)))

data['archive'][TODAY] = kept

# ---------- 统计 ----------
from collections import Counter
cats = Counter(it.get('category') for it in kept)
sc = [it.get('priority_score') or 0 for it in kept]
print('删除:', len(removed), '保留+补录:', len(kept))
for r in removed:
    print('  DEL', r[:50])
print('分类:', dict(cats))
print('≥85:', sum(1 for s in sc if s >= 85), '/', len(sc), f'({sum(1 for s in sc if s>=85)/len(sc)*100:.0f}%)')
print('100分:', sc.count(100))
print('摘要最短:', min(len((it.get('summary') or '')) for it in kept))
bad = [it['title'] for it in kept if not it.get('summary') or len(it['summary']) < 40]
print('摘要异常:', bad)

data['todayCount'] = len(kept)
data['stats'] = data.get('stats', {})
json.dump(data, open(JSON_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('已写回', JSON_PATH)
