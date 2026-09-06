#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国内看板 2026-09-06 LLM 后处理（V2.11 归档规则）
=================================================
今日版面 32 条 → 删除 23 条低质/重复 → 保留 9 条 + 修正 2 处 + AI 补录 1 条 = 10 条
"""
import json, sys, datetime

JSON_PATH = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json'
TODAY = '2026-09-06'

d = json.load(open(JSON_PATH, encoding='utf-8'))
archive = d['archive']
items = archive[TODAY]
print(f'处理前今日版面: {len(items)} 条')

# ============ 1. 删除清单（按 URL 精确匹配，防误删） ============
del_urls = [
    # [01] 小喇叭贺信"引发热烈反响"反响稿 —— 贺信本体 9-5 版面 gov.cn 版已收，反响稿信息增量 0
    'https://news.cctv.com/2026/09/05/ARTIbJqvwNr9dJrjp6paZy3k260905.shtml',
    # [04] 访问纪实央视版 —— 与 9-5 版面 gov.cn content_7080285 同文（新华社通稿），跨版面重复
    'https://news.cctv.com/2026/09/06/ARTI63A471GQqpCbCu3HC93r260906.shtml',
    # [05] 向新之翼"科学的未来在青年" —— 人民情怀/故事化系列（总书记关心青年故事）
    'https://news.cctv.com/2026/09/05/ARTIvTfaAoxsHIKtXX1HIcGr260905.shtml',
    # [06] 时代·人民·文明——思想启迪 —— 新华社署名述评（"题："模式），与[03]国际反响特稿功能重叠
    'https://www.gov.cn/yaowen/liebiao/202609/content_7080286.htm',
    # [07] 视频画报|开罗时间 —— 视觉产品（视频画报），访问活动已充分覆盖
    'https://news.cctv.com/2026/09/05/ARTIRucdgv6vOi1G1M8KOZKR260905.shtml',
    # [10] 黄坤明广东实践 —— 地方主官论坛讲话（广东省委书记本地发展叙事），无摘要
    'https://www.zaobao.com/news/china/story20260905-9631749',
    # [13] 应急部调度（人民日报版）—— 与[14]央视版同事件重复
    'http://paper.people.com.cn/rmrb/pc/content/202609/06/content_30179378.html',
    # [16] 福建"以汛为令" —— 地方软稿（9-5 已删同题）
    'https://news.cctv.com/2026/09/05/ARTINWMr61AoVoYMWqWlbxw8260905.shtml',
    # [17] 福建终止防汛响应 —— 省级进展动作（只收中央部委动作）
    'https://news.cctv.com/2026/09/05/ARTIqBlvRNGxCAM0kEh1r76i260905.shtml',
    # [18] 莴笋染色立案6家 —— 地方市场监管执法+摘要为栏目模板残留（非中央部委动作）
    'https://news.cctv.com/2026/09/06/ARTIxWAlDbeGcdSoSSIZv4iB260906.shtml',
    # [19] 西藏吉隆泥石流救援推进 —— 9-5 版面已收吉隆线（应急部保供），跨版面跟踪重复
    'https://news.cctv.com/2026/09/05/ARTIX8gLloOOwrcdyW26qPmV260905.shtml',
    # [20] 台湾中科院采购网遭黑客 —— 台湾事务（中山科学研究院），非大陆政务
    'https://www.zaobao.com/news/china/story20260906-9633331',
    # [21] "50.9%、132.3点多组数据" —— 数据拼盘栏目体（看经济综述）
    'https://news.cctv.com/2026/09/05/ARTIH8GXIERpSRPWsdvufoxi260905.shtml',
    # [22] 餐厨废油"飞上天" —— 故事化报道（9-5 已删同题）
    'https://news.cctv.com/2026/09/05/ARTIEJ4zcyGpswrUIUwQHYzn260905.shtml',
    # [23] 动力电池多点突破 —— 产业综述（无具体事件，记者观察式）
    'https://news.cctv.com/2026/09/06/ARTI6LyFR4RKBlOw0xwumhRU260906.shtml',
    # [25] 节水账本 —— 软文综述
    'https://news.cctv.com/2026/09/06/ARTI5EWNA36zhR8zaDx7LLPn260906.shtml',
    # [26] 光伏成第一大电源图景 —— "多领域亮点"拼盘（9-5 已删光伏图景同类）
    'https://jingji.cctv.com/2026/09/05/ARTIiYbGlAEadIq8Gqjppwbf260905.shtml',
    # [27] 中国股票衍生品需求升温 —— 市场交易观察（联合早报，非政策/高层线）
    'https://www.zaobao.com/news/china/story20260906-9633439',
    # [28] 湖北多措并举产业就业 —— 地方正面报道（人民日报地方稿）
    'http://paper.people.com.cn/rmrb/pc/content/202609/06/content_30179350.html',
    # [29] 看指数识经济|物流业 —— 栏目体（9-5 已删物流指数栏目同类）
    'https://news.cctv.com/2026/09/05/ARTIApf9ZUdasQzrGoxBNftS260905.shtml',
    # [30] 求职背调灰产 —— 社会调查专题（非政务线）
    'https://news.cctv.com/2026/09/06/ARTIMnkXlMZdO26tF3UVyFVM260906.shtml',
    # [31] 能源绿色低碳转型（经济新方位）—— 人民日报专栏文
    'http://paper.people.com.cn/rmrb/pc/content/202609/06/content_30179359.html',
    # [32] 金融政策"组合拳"评述 —— 评述综述（9-5 已删金融组合拳评述同类）
    'https://news.cctv.com/2026/09/05/ARTIaCfRHJ5LLfPo8jQ1wqjM260905.shtml',
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

# ============ 2. [08] 丁薛祥 URL 修正（tv.cctv → gov.cn 原文） ============
for a in kept:
    u = a.get('url', '')
    if 'VIDELI1aC0snGA9F1Nn9HyCo260905' in u:  # [08] tv.cctv 视频聚合页
        a['url'] = 'https://www.gov.cn/yaowen/liebiao/202609/content_7080270.htm'
        a['summary'] = ('新华社符拉迪沃斯托克9月5日电 当地时间9月2日至4日，中共中央政治局常委、国务院副总理丁薛祥'
                        '在符拉迪沃斯托克会见俄罗斯总统普京，同俄罗斯第一副总理曼图罗夫共同主持中俄投资合作委员会'
                        '第十三次会议，同俄罗斯副总理诺瓦克共同主持中俄能源合作委员会第二十三次会议，并出席第八届'
                        '中俄能源商务论坛开幕式。丁薛祥转达习近平主席的亲切问候；普京请丁薛祥转达对习近平主席的'
                        '诚挚问候。')
        print('✅ [08] URL 已修正为 gov.cn content_7080270，摘要已更新')

    # ============ 3. [24] 中美AI安全对话：补真实摘要 + 提分 ============
    if 'story20260905-9632319' in u:
        a['summary'] = ('据路透社消息人士报道，中美正筹备预计9月中旬举行的人工智能安全对话，为两国元首9月下旬'
                        '峰会铺垫，系特朗普第二任期以来首次聚焦AI的官方双边会谈。美方代表团或由财长贝森特率领，'
                        '中方或由副总理何立峰或丁薛祥牵头；议题包括合作监测AI主导的网络攻击、要求中美AI企业'
                        '"自我监管"及美方提出中方以"蒸馏"方式获取美国AI模型能力的问题。两国元首5月会面时已同意'
                        '就人工智能展开政府间对话。')
        a['priority_score'] = 85
        print('✅ [24] 摘要已补全（联合早报原文），分数 72→85')

# ============ 4. AI 补录：发改委紧急安排 2000 万元支持江西 ============
new_item = {
    "title": "国家发展改革委紧急安排2000万元支持江西暴雨洪涝灾害灾后应急恢复",
    "url": "http://www.jx.xinhuanet.com/20260905/2eb83f49cd124d6f93c8020ccafd6af9/c.html",
    "date": "2026-09-05",
    "source": "新华网",
    "category": "部委动态",
    "priority_score": 85,
    "is_summit_level": False,
    "summary": ("新华社消息 受近期强降雨影响，江西省南昌、吉安等多地发生洪涝灾害，9月5日国家防减救灾委、应急管理部"
                "启动国家自然灾害救助四级应急响应和国家地质灾害四级应急响应。为贯彻落实习近平总书记关于防汛救灾工作"
                "的重要指示精神，国家发展改革委紧急安排中央预算内投资2000万元，支持江西省暴雨洪涝灾害灾后应急恢复，"
                "重点用于灾区受损道路、水利等基础设施和学校、医院等公共服务设施抢修建设。"),
    "collectedAt": "2026-09-06 12:50:00"
}
# URL 防重
urls_now = {a.get('url') for a in kept}
if new_item['url'] not in urls_now:
    kept.append(new_item)
    print('✅ AI 补录: 发改委2000万支持江西（微信通道线索，date=9-5）')
else:
    print('ℹ️ 补录条目已存在，跳过')

# ============ 5. 排序（按分数降序保持版面顺序） ============
kept.sort(key=lambda x: -x.get('priority_score', 0))
archive[TODAY] = kept

# ============ 6. 更新元数据 ============
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
d['lastUpdated'] = '2026-09-06 12:50'

# ============ 7. 归档规则校验 ============
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
            if dt not in ('2026-09-05', '2026-09-06'):
                print(f'  ⚠️ 今日版面 date 超窗口: {a.get("title","")[:30]} date={dt}')
                err += 1
        else:
            if dt >= TODAY:
                print(f'  ⚠️ 历史版面混入今日 date: {day} | {a.get("title","")[:30]} date={dt}')
                err += 1
print(f'  违规数: {err}')

# ============ 8. 分类/分数分布输出 ============
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
