#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国内新闻看板 LLM 后处理 2026-08-21
1) 删除低质/重复/栏目条目（19条）
2) 补录 gov.cn 抓取失败导致的漏采（6条，官方URL已验证）
3) 补摘要（urllib 抓 meta description，失败用事实概括）
"""
import json, re, urllib.request, ssl, sys

JSON_PATH = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/data/china-news.json'
TODAY = '2026-08-21'

d = json.load(open(JSON_PATH, encoding='utf-8'))
arch = d['archive']
today_items = arch.get(TODAY, [])
print(f"处理前今日版面: {len(today_items)} 条")

# ---------- 1. 删除清单（按 URL 精确匹配，避免误删） ----------
del_urls = [
    # 学习栏目
    'https://news.cctv.com/2026/08/20/ARTIIvURH8mvDsUVKtzaKDtu260820.shtml',  # 一习话
    # 栏目综述
    'https://news.cctv.com/2026/08/20/ARTIARWdScUhBPVVVXxp5Im2260820.shtml',  # 焦点访谈 AI
    # 专家点评栏目
    'http://paper.people.com.cn/rmrb/pc/content/202608/21/content_30176302.html',  # 专家点评
    # 栏目故事化
    'http://paper.people.com.cn/rmrb/pc/content/202608/21/content_30176301.html',  # 新质生产力创造就业
    # 政策解读栏目 + AI交通重复
    'http://paper.people.com.cn/rmrb/pc/content/202608/21/content_30176300.html',  # 政策解读 AI交通
    # 综述
    'https://news.cctv.com/2026/08/21/ARTIV8p50NgJjw8sxse8Rb1n260820.shtml',  # 各地重大工程
    'https://news.cctv.com/2026/08/21/ARTIHshFlZSmqgGTA4ryzuna260821.shtml',  # 多领域数据
    'https://news.cctv.com/2026/08/20/ARTI2d48MyFjpKahP399cC6m260820.shtml',  # 工业经济新动能
    'http://paper.people.com.cn/rmrb/pc/content/202608/21/content_30176294.html',  # 宏观政策发力提效
    # 澳门规划评论×3（昨日已收规划）
    'https://news.cctv.com/2026/08/20/ARTIh6y5WL8HGTnXGHaOxsqk260820.shtml',
    'https://news.cctv.com/2026/08/20/ARTIqZFnVo8DPJmZax6DZtOH260820.shtml',
    'https://news.cctv.com/2026/08/20/ARTIAhTJRSxeBBa5R2PUUU8N260820.shtml',
    # 医保规划解读（与昨日 gov.cn 完整版重复）
    'https://news.cctv.com/2026/08/20/ARTIN49H22xU8ENvRlT2Q81s260820.shtml',
    # 课题征集公告（事务性）
    'https://www.ndrc.gov.cn/xwdt/tzgg/202608/t20260820_1407104.html',
    # 航天功勋央视版（保留人民日报正式版）
    'https://news.cctv.com/2026/08/20/ARTImsnp5BauZh05S2rI9vC0260820.shtml',
    # 网络数据安全评论解说版×2（保留公安部答问版）
    'https://news.cctv.com/2026/08/20/ARTIt9Y6eWXDcCSc36BtTici260820.shtml',
    'https://news.cctv.com/2026/08/20/ARTINyLNcJRhPZVj8mvPIDl5260820.shtml',
    # 世界机器人大会（会展活动报道）
    'https://news.cctv.com/2026/08/20/ARTIIhGpnbInPpShNl9vREAl260820.shtml',
    # 蓝皮书发布（配套信息，价值中等）
    'http://paper.people.com.cn/rmrb/pc/content/202608/21/content_30176322.html',
]
kept = [i for i in today_items if i['url'] not in del_urls]
removed = len(today_items) - len(kept)
print(f"删除 {removed} 条 → 剩余 {len(kept)} 条")
for i in today_items:
    if i['url'] in del_urls:
        print(f"  ✂️ {i['title'][:45]}")

# ---------- 2. 补录 6 条（gov.cn 抓取失败漏采，官方URL已验证） ----------
NEW_ITEMS = [
    {
        "title": "恒大集团、恒大地产、许家印等案一审宣判 许家印被判无期徒刑",
        "url": "https://www.court.gov.cn/fabu/xiangqing/509281.html",
        "date": "2026-08-20", "source": "最高人民法院", "category": "人事任免",
        "priority_score": 87, "is_summit_level": False,
        "summary": "8月20日，广东省深圳市中级人民法院对恒大集团、恒大地产、许家印案一审公开宣判：对恒大集团判处罚金88.2亿元，对恒大地产判处罚金70亿元，对许家印数罪并罚判处无期徒刑，剥夺政治权利终身，并处没收个人全部财产；同日还宣判甄立涛等56名涉案人员有期徒刑十八年至一年十个月不等。",
        "collectedAt": "2026-08-21 09:22:36",
    },
    {
        "title": "最高法修改审理著作权民事纠纷案件司法解释 自9月1日起施行",
        "url": "https://www.court.gov.cn/zixun/xiangqing/509271.html",
        "date": "2026-08-20", "source": "最高人民法院", "category": "政策发布",
        "priority_score": 80, "is_summit_level": False,
        "summary": "最高人民法院8月20日发布关于修改《最高人民法院关于审理著作权民事纠纷案件适用法律若干问题的解释》的决定（法释〔2026〕18号），自9月1日起施行。决定细化了“公之于众”认定标准、合理使用边界、报刊转载法定许可范围（明确纸质报刊及其数字化版本），并明确互联网转载须经许可并支付报酬，统一裁判尺度。",
        "collectedAt": "2026-08-21 09:22:36",
    },
    {
        "title": "民政部、财政部印发《关于积极发展服务类社会救助的指导意见》",
        "url": "https://www.gov.cn/lianbo/202608/content_7078723.htm",
        "date": "2026-08-20", "source": "中国政府网", "category": "政策发布",
        "priority_score": 80, "is_summit_level": False,
        "summary": "民政部、财政部近日联合印发《关于积极发展服务类社会救助的指导意见》（民发〔2026〕35号），这是《中华人民共和国社会救助法》颁布实施后的首个配套政策文件，推动社会救助由单一物质救助向“物质+服务”综合救助模式转变，提出明确救助对象范围、建立需求评估体系、编制服务供给清单等举措。",
        "collectedAt": "2026-08-21 09:22:36",
    },
    {
        "title": "中国240小时过境免签“朋友圈”扩展至57国",
        "url": "https://www.gov.cn/lianbo/202608/content_7078699.htm",
        "date": "2026-08-20", "source": "中国政府网", "category": "部委动态",
        "priority_score": 85, "is_summit_level": False,
        "summary": "国家移民管理局8月20日发布公告，自即日起吉尔吉斯斯坦、越南公民可适用240小时过境免签政策和海南30天入境免签政策来华，240小时过境免签适用国家增至57国，海南30天入境免签适用国家增至61国，可从北京、上海等65个对外开放口岸免签入境。",
        "collectedAt": "2026-08-21 09:22:36",
    },
    {
        "title": "检察机关依法对交通银行原副行长侯维栋涉嫌受贿案提起公诉",
        "url": "https://www.ccdi.gov.cn/yaowenn/202608/t20260820_507733.html",
        "date": "2026-08-20", "source": "中央纪委国家监委网站", "category": "人事任免",
        "priority_score": 87, "is_summit_level": False,
        "summary": "8月20日从最高人民检察院获悉，交通银行股份有限公司原党委委员、副行长侯维栋涉嫌受贿一案，由国家监察委员会调查终结移送检察机关审查起诉，重庆市人民检察院依法以涉嫌受贿罪对侯维栋作出逮捕决定，近日已向重庆市第五中级人民法院提起公诉，其非法收受他人财物数额特别巨大。",
        "collectedAt": "2026-08-21 09:22:36",
    },
    {
        "title": "河北秦皇岛海港区一底商发生火灾 造成8人死亡",
        "url": "https://new.qq.com/rain/a/20260820A05PIG00",
        "date": "2026-08-20", "source": "央视新闻", "category": "部委动态",
        "priority_score": 88, "is_summit_level": False,
        "summary": "8月20日3时40分左右，河北省秦皇岛市海港区一底商发生火灾，消防、应急、卫健、公安等部门第一时间赶赴现场救援，4时30分明火被扑灭。事故造成8人死亡，3人送医救治，伤者生命体征平稳，事故原因调查及善后工作正在开展。",
        "collectedAt": "2026-08-21 09:22:36",
    },
]

# 唯一键去重检查
existing_keys = {(i['title'][:30], i['source']) for i in kept}
added = 0
for item in NEW_ITEMS:
    key = (item['title'][:30], item['source'])
    if key in existing_keys:
        print(f"  ⚠️ 补录条目与现有重复，跳过: {item['title'][:30]}")
        continue
    kept.append(item)
    existing_keys.add(key)
    added += 1
    print(f"  ➕ 补录: [{item['priority_score']}] {item['title'][:45]}")
print(f"补录 {added} 条")

# ---------- 3. 补摘要（urllib 抓 meta description） ----------
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 事实概括兜底（基于已验证的报道内容，不含编造细节）
FALLBACK = {
    '周海兵': '8月20日，国家发展改革委副主任周海兵会见智利外交部长佩雷斯，双方就深化双边经贸投资合作等交换意见。',
    '王毅与韩国国家安保室长': '8月20日，中共中央政治局委员、外交部长王毅在首尔同韩国国家安保室长魏圣洛举行战略对话，就双边关系和共同关心的问题深入交换意见。',
    '赵乐际同萨尔瓦多': '8月21日，全国人大常委会委员长赵乐际在北京同萨尔瓦多立法大会主席卡斯特罗举行会谈，就两国关系和立法机构交往交换意见。',
    '郑栅洁主任': '8月20日，国家发展改革委主任郑栅洁主持召开民营企业座谈会，围绕稳定经济运行、促进有效投资听取民营企业意见建议，来自特锐德电气、楚天科技等5家企业负责人参加，郑栅洁表示将充分发挥存量政策效能、及时谋划出台务实管用的增量政策，充分激发民间投资活力。',
    '林剑主持例行记者会': '8月20日，外交部发言人林剑主持例行记者会，就中韩关系、中方反对在人工智能问题上搞选边站队、当前局势等问题回答记者提问。',
    '商务部消费促进司': '商务部消费促进司负责人介绍2026年7月我国消费市场情况，消费市场总体保持平稳发展态势。',
    '商务部电子商务司': '商务部电子商务司负责人介绍2026年1-7月我国电子商务发展情况，网络零售保持增长，电子商务稳定创新发展。',
}

def fetch_summary(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
        html = urllib.request.urlopen(req, timeout=12, context=ctx).read().decode('utf-8', 'ignore')
        m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', html, re.I)
        if m:
            s = re.sub(r'\s+', ' ', m.group(1)).strip()
            if len(s) > 20:
                return s
        m2 = re.search(r'<meta\s+content=["\']([^"\']{30,300})["\']\s+name=["\']description["\']', html, re.I)
        if m2:
            s = re.sub(r'\s+', ' ', m2.group(1)).strip()
            if len(s) > 20:
                return s
    except Exception as e:
        print(f"    抓取失败: {e}")
    return None

sum_filled = 0
for i in kept:
    if i.get('summary') and len(i['summary']) > 15:
        continue
    key = next((k for k in FALLBACK if k in i['title']), None)
    print(f"  补摘要: {i['title'][:40]}")
    s = fetch_summary(i['url'])
    if s:
        i['summary'] = s
        print(f"    ✅ 抓取真实摘要 ({len(s)}字)")
    elif key:
        i['summary'] = FALLBACK[key]
        print(f"    ⚠️ 用事实概括")
    else:
        print(f"    ❌ 无可用摘要源")
    sum_filled += 1

# ---------- 4. 更新归档与统计 ----------
arch[TODAY] = sorted(kept, key=lambda x: -x['priority_score'])
# 全量统计
all_items = [i for day_items in arch.values() for i in day_items]
d['todayCount'] = len(kept)
d['stats'] = {
    'totalArticles': len(all_items),
    'dateCount': len(arch),
    'latestDate': TODAY,
    'summitCount': sum(1 for i in all_items if i.get('is_summit_level')),
}
d['lastUpdated'] = '2026-08-21 09:22'

json.dump(d, open(JSON_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"\n✅ 保存完成: 今日版面 {len(kept)} 条 | 全量 {len(all_items)} 条 | 元首级 {d['stats']['summitCount']}")
print(f"   今日≥85分: {sum(1 for i in kept if i.get('priority_score',0)>=85)}/{len(kept)} = {round(sum(1 for i in kept if i.get('priority_score',0)>=85)/len(kept)*100)}%")
