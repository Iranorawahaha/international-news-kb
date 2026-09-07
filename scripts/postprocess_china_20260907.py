#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国内看板 2026-09-07 LLM 后处理（V2.11 归档规则）
=================================================
今日版面 25 条 → 删除 20 条低质/重复 → 保留 5 条 + 修正 3 处 + AI 补录 1 条 = 6 条
（周日-周一窗口：出访回顾栏目体井喷，元首动态无新事件属客观正常）
"""
import json

JSON_PATH = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json'
TODAY = '2026-09-07'
DATE_OK = ('2026-09-06', '2026-09-07')

d = json.load(open(JSON_PATH, encoding='utf-8'))
archive = d['archive']
items = archive[TODAY]
print(f'处理前今日版面: {len(items)} 条')

# ============ 1. 删除清单（URL 精确匹配防误删） ============
del_urls = [
    # [00] 习近平中亚中东之旅"难忘瞬间" —— 出访回顾栏目体（视觉总结），出访正稿 9-4/9-5/9-6 版已充分覆盖
    'https://news.cctv.com/2026/09/06/ARTI7q9gXVEssdwUeRXD4XFP260906.shtml',
    # [01] 众行致远破题 —— 央视随访系列述评（9-6 版已收"国际社会高度评价"收官稿，功能重叠）
    'https://news.cctv.com/2026/09/06/ARTIhd6TdFbEJz7YXtCbvTGM260906.shtml',
    # [02] 访问纪实央视版 —— 9-5 版面 gov.cn content_7080285 已收新华社通稿同文，跨版面重复（9-6 删过同类）
    'https://news.cctv.com/2026/09/06/ARTI63A471GQqpCbCu3HC93r260906.shtml',
    # [03] 时代·人民·文明思想启迪 —— 新华社"题："署名述评（9-6 已删同类）
    'https://www.gov.cn/yaowen/liebiao/202609/content_7080286.htm',
    # [04] 100秒看亚非之行 —— 视频产品
    'https://news.cctv.com/2026/09/06/ARTIbYhtv7jgRLmRdwgfKDU5260906.shtml',
    # [07] 莴笋果绿 甘肃榆中6家 —— 县级地方执法（9-6 已删同题）
    'https://news.cctv.com/2026/09/06/ARTIVVqaflItr2JL7OltMz1A260906.shtml',
    # [09] 联合早报增资版 —— 与 [08] 央视版同事件重复，留央视版
    'https://www.zaobao.com/news/china/story20260907-9636442',
    # [10] 红十字总会调拨2000件 —— 群团组织救灾物资（灾害线只收中央部委动作；9-6 版已收发改委2000万+应急部调度）
    'https://news.cctv.com/2026/09/06/ARTI7niIXvgeK14f0bbg3JXy260906.shtml',
    # [11] 动力电池产业体系 gov.cn —— 工信部数据综述（无具体事件，9-6 删过动力电池同题）
    'https://www.gov.cn/yaowen/liebiao/202609/content_7080306.htm',
    # [12] 构建新型电力系统 —— 政论综述体（无事件）
    'https://news.cctv.com/2026/09/06/ARTI4BTM3CPzs9UM4YnqzrPJ260906.shtml',
    # [13] 莴笋官方通报版 —— 与 [07] 同事件 + 摘要为栏目模板残留（"每天8点央视网为您梳理"）
    'https://news.cctv.com/2026/09/06/ARTIxWAlDbeGcdSoSSIZv4iB260906.shtml',
    # [14] 解码十五五碳达峰 —— 人民日报"解码"专栏解读体；《"十五五"碳达峰行动方案》国务院 7月已印发（超窗口旧政策）
    'http://paper.people.com.cn/rmrb/pc/content/202609/07/content_30179387.html',
    # [15] 动力电池多点突破 —— 产业综述无事件（同 [11]，9-6 删过同题）
    'https://news.cctv.com/2026/09/06/ARTI6LyFR4RKBlOw0xwumhRU260906.shtml',
    # [16] 节水账本 —— 软文综述（9-5/9-6 删过同类）
    'https://news.cctv.com/2026/09/06/ARTI5EWNA36zhR8zaDx7LLPn260906.shtml',
    # [17] 紫金矿业"人民币政府"致歉 —— 企业舆情非政务
    'https://www.zaobao.com/news/china/story20260906-9634163',
    # [18] 人工智能中小企业创业支持计划 —— 9-4 版面已收同政策（跨版面重复，公众号/报纸转载延迟）
    'http://paper.people.com.cn/rmrb/pc/content/202609/07/content_30179394.html',
    # [19] 戴庆成署名评论 —— 联合早报评论员文章直接剔除
    'https://www.zaobao.com/news/china/story20260907-9635150',
    # [20] 港财政司长贸易占比 —— 香港特区政府官员言论（特区层面非中央政务）
    'https://www.zaobao.com/news/china/story20260906-9634354',
    # [21] 焦点访谈AI机器人 —— 央视栏目专题（非事件新闻）
    'https://news.cctv.com/2026/09/06/ARTISrR1qaPMQRabXSfqA7qd260906.shtml',
    # [22] 求职背调灰产 —— 社会调查专题（9-6 已删同类）
    'https://news.cctv.com/2026/09/06/ARTIMnkXlMZdO26tF3UVyFVM260906.shtml',
]

kept, deleted = [], []
for a in items:
    if a.get('url') in del_urls:
        deleted.append(a)
    else:
        kept.append(a)
print(f'删除: {len(deleted)} 条 | 保留: {len(kept)} 条')

# 校验删除 URL 全命中
del_set = set(del_urls)
hit = {a.get('url') for a in deleted}
missing = del_set - hit
if missing:
    print('⚠️ 未命中 URL:')
    for u in missing:
        print('  ', u)

# ============ 2. 修正 [06] 湖北卫健委案：人事任免87 → 部委动态88（反垄断重大执法）+ 补真实摘要 ============
for a in kept:
    u = a.get('url', '')
    # [06] 市场监管总局 9-4 公布第二批7案，湖北卫健委案列首（联合早报 9-6 16:04 报道）
    if 'story20260906-9634510' in u:
        a['category'] = '部委动态'
        a['priority_score'] = 88
        a['summary'] = ('综合中国经营网等报道，市场监管总局9月4日公布《破除妨碍统一市场和公平竞争卡点堵点专项行动案件'
                        '（第二批）》，曝光七起滥用行政权力排除、限制竞争典型案例，首案为总局直接查处的湖北省卫健委'
                        '行政垄断案：2025年11月该委擅自编制药品鼓励应用目录，将26种本地企业药品纳入并设置进院绿色'
                        '通道，以产地而非质量疗效价格倾斜，违反《反垄断法》。总局向湖北省政府制发行政建议书，经督促'
                        '目录已废止、公平竞争秩序恢复，相关责任人被政务处分。')
        print('✅ [06] 湖北卫健委案：人事任免→部委动态88，摘要已补全（官方通报为据）')
    # [23] 财政部向人寿太平注资 420亿 —— 72 → 85（财政部注资中央金融企业=高层经济信号，与[08]增资线同类）
    if 'ARTIFntpIOVPT4Zk27GWcYyd260906' in u:
        a['priority_score'] = 85
        print('✅ [23] 财政部注资人寿太平 72→85')
    # [24] 国家反诈AI App —— 分类 经贸72 → 部委动态85（公安部刑侦局指导国家级反诈AI助手，部委政务动作）
    if 'ARTIHHnxJ5xEXOiKPW97OSbZ260906' in u:
        a['category'] = '部委动态'
        a['priority_score'] = 85
        print('✅ [24] 国家反诈AI：经贸动向→部委动态85')

# ============ 3. AI 补录：卡塔尔首相访华预告（外事日程栏目 classify 缺口，curl 验证 9-6 新文） ============
new_item = {
    "title": "卡塔尔首相兼外交大臣穆罕默德将访华",
    "url": "https://www.mfa.gov.cn/web/wjdt_674879/wsrc_674883/202609/t20260906_12016936.shtml",
    "date": "2026-09-06",
    "source": "外交部",
    "category": "高层动态",
    "priority_score": 95,
    "is_summit_level": False,
    "summary": ("外交部消息，卡塔尔首相兼外交大臣穆罕默德将于9月7日至8日应邀访问中国。"
                "（此系外交部外事日程栏目预告，官方页面原文）"),
    "collectedAt": "2026-09-07 09:30:00"
}
urls_now = {a.get('url') for a in kept}
if new_item['url'] not in urls_now:
    kept.append(new_item)
    print('✅ AI 补录: 卡塔尔首相穆罕默德 9月7-8日访华（外交部外事日程 9-6 发布，curl 验证栏目页/文章页均可达）')
else:
    print('ℹ️ 补录条目已存在，跳过')

# ============ 4. 排序（分数降序，稳定保持原顺序） ============
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
d['lastUpdated'] = '2026-09-07 09:35'

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
for day in ['2026-09-04', '2026-09-05', '2026-09-06']:
    print(f'  {day}: {len(archive.get(day, []))} 条（应保持 22/24/10 不变）')

# ============ 7. 分类/分数分布输出 ============
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
