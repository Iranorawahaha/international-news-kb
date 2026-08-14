#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 公司商业情报看板 构建脚本 v2
- 合并 /tmp/aihot_scan 下所有查询响应（selected 优先，空则用 all 回退）
- 公司扩展到 15 家（+华为、Kimi、MiniMax）
- 监管/科技博弈关键词命中条目需通过监管信号词过滤（剔除无关噪音）
- 输出单文件 HTML：KPI + 固定分类 tab + 动态流
"""
import json, glob, re, html, os
from datetime import datetime, timezone, timedelta

# V2.2 修复（2026-08-02）：抓取产物在 ${TMPDIR}/aihot_scan（macOS TMPDIR=/var/folders/...），
# 不再硬编码 /tmp。兜底：若 TMPDIR 无数据则尝试 /tmp/aihot_scan。
def _scan_dir():
    cands = []
    t = os.environ.get("TMPDIR")
    if t:
        cands.append(os.path.join(t, "aihot_scan"))
    cands.append("/tmp/aihot_scan")
    for c in cands:
        if os.path.isdir(c) and glob.glob(os.path.join(c, "q*_sel.json")):
            return c
    return cands[0]

SCAN_DIR = _scan_dir()
OUT_HTML = "/Users/xiaoxiao/WorkBuddy/2026-08-01-14-08-40/ai-company-intel-board.html"
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
TODAY_START = datetime(NOW.year, NOW.month, NOW.day, 0, 0, 0, tzinfo=TZ)
TODAY_STAMP = TODAY_START.timestamp()

# ---------------- 关键词体系 ----------------
COMPANY_KEYWORDS = {
    "OpenAI": ["OpenAI", "ChatGPT", "GPT-5.1", "GPT-5.2", "GPT-5", "GPT-5o", "GPT-4o", "o3-pro", "o1", "o3", "o4", "Sora", "Operator", "gpt-oss"],
    "Anthropic": ["Anthropic", "Claude Code", "Claude", "Sonnet", "Opus", "Haiku", "MCP"],
    "Google/DeepMind": ["Project Astra", "DeepMind", "Google", "Gemini", "Veo", "Imagen", "AlphaFold", "AlphaEvolve", "TensorFlow", "TPU", "PaLM", "Gemma", "NotebookLM"],
    "Meta": ["Meta", "Llama", "SAM 2", "SAM2", "Segment Anything", "Ray-Ban", "Hyperscale"],
    "Microsoft": ["Microsoft", "Copilot", "Azure", "Phi-4", "Phi-5", "MAI-1", "MatterGen", "Muse"],
    "NVIDIA": ["NVIDIA", "CUDA", "GB300", "Blackwell", "Rubin", "Grace", "NVLink", "DGX", "NIM"],
    "xAI": ["xAI", "Grok"],
    "DeepSeek": ["DeepSeek", "深度求索"],
    "阿里通义": ["通义千问", "Alibaba", "Qwen", "通义", "阿里", "QwQ"],
    "字节豆包": ["字节跳动", "ByteDance", "豆包", "Doubao", "即梦", "火山引擎"],
    "腾讯混元": ["腾讯元宝", "Hunyuan", "混元", "Tencent", "腾讯"],
    "智谱GLM": ["AutoGLM", "CogVideo", "CogView", "CogAgent", "GLM-4", "Zhipu", "智谱", "GLM"],
    "华为": ["Huawei", "华为", "Ascend", "昇腾", "盘古", "Pangu", "麒麟", "鸿蒙", "HarmonyOS", "小艺"],
    "Kimi(月之暗面)": ["Kimi", "月之暗面", "Moonshot"],
    "MiniMax": ["MiniMax", "海螺", "Hailuo"],
}
ALL_KW = sorted(set(k for kws in COMPANY_KEYWORDS.values() for k in kws), key=len, reverse=True)
KW_RE = re.compile("|".join(re.escape(k) for k in ALL_KW), re.IGNORECASE)

# 监管/科技博弈信号词（用于过滤监管类回退命中；含强信号才保留）
REG_SIGNAL = re.compile(
    "监管|法案|法规|合规|限制令|禁令|制裁|出口管制|出口|管制|关税|走私|审查|下架|诉讼|起诉|"
    "法院|罚款|执法|封锁|禁运|国产替代|自主可控|反垄断|垄断|地缘|博弈|中美|欧盟|华盛顿|"
    "行为准则|GPAI|FCC|光刻机|安全政策|芯片管制|算力枢纽|国家安全",
    re.IGNORECASE,
)

# 明确无关词（标题命中即剔除）
# V3.1: 低价值信号黑名单（活动促销/小版本更新/炒股财经/娱乐八卦）
JUNK_TITLE = re.compile(
    "苹果库克|三星李在镕|Google Camp|Linux VPS|SGLang|财报电话会议|"
    # 活动促销
    "不限量免费|到店连Wi-Fi|免费Token|白嫖|白送|免费试用|免费领取|免费额度|免费用|"
    "限时免费|0元|零元|免费版|永久免费|促销|大促|秒杀|"
    # 娱乐八卦
    "网红|奢华品牌|房价一晚|豪华之旅|花边|绯闻|吃瓜|恋情|"
    # 炒股财经
    "斩杀|涨停|跌停|崩盘|爆仓|A股|港股|美股收盘|盘前|开盘|"
    "获利了结|抄底|逃顶|做空报告|"
    # 无关产品更新
    "QQ浏览器|浏览器更新|输入法更新|天气更新|"
    # 低质活动
    "有奖征集|有奖活动|抽奖|福利领取|薅羊毛",
    re.IGNORECASE,
)

CAT_ORDER = [
    ("industry", "行业动态", "⚖️", "AI 行业监管 · 国家科技博弈（置顶关注）"),
    ("ai-models", "模型与产品发布", "🏗️", "重大模型/产品发布（仅高关注度）"),
    ("tip", "技巧与观点", "💡", "高关注度行业观点与言论"),
]

def timeline_ts(it):
    pa, da = it.get("publishedAt"), it.get("discoveredAt")
    def ts(s):
        if not s: return None
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
        except Exception:
            return None
    pa_t, da_t = ts(pa), ts(da)
    if pa_t is None: return da_t or 0
    if da_t is None: return pa_t
    if da_t - pa_t > 72 * 3600: return pa_t
    return da_t

# ---------------- 读取与合并 ----------------
seen = {}
hit_company = {}
hit_kws = {}
kw_company = {}
for comp, kws in COMPANY_KEYWORDS.items():
    for k in kws:
        kw_company[k.lower()] = comp

def classify_hits(it):
    text = ((it.get("title") or "") + " " + (it.get("summary") or "")).lower()
    comps, kws = set(), set()
    for k in ALL_KW:
        if k.lower() in text:
            kws.add(k)
            comps.add(kw_company[k.lower()])
    return comps, kws

# V3.1: 行业动态强化过滤——高价值信号优先（政治/监管/诉讼/立法/重大数据）
INDUSTRY_HIGH_SIGNAL = re.compile(
    # 政治监管
    "法案|法规|监管|框架|评估|合规|立法|国会|政府|商务部|"
    "白宫|总统令|行政令|规则生效|透明度|罚款|处罚|违规|"
    "调查|诉讼|起诉|起诉书|禁令|法院|判决|和解|"
    "出口管制|出口|管制|制裁|封锁|关税|实体清单|"
    "地缘|博弈|中美|欧盟|华盛顿|布鲁塞尔|"
    # 重大数据里程碑
    "亿|万亿|百万亿|创纪录|突破|里程碑|新高|首次|第一|"
    "市场|份额|估值|融资|IPO|上市|收购|并购|"
    # 行业分析
    "报告|白皮书|分析|解读|趋势|预测|展望",
    re.IGNORECASE,
)
# V3.1: 低价值信号（活动/促销/小更新/娱乐/炒股/无关事件）
INDUSTRY_LOW_SIGNAL = re.compile(
    "上线|发布|推出|上新|到店|Wi-Fi|扫码|注册即|领取|"
    "退款|优惠|打折|免费获取|抢购|限量发售|预约|"
    "小版本|热更新|补丁|Patch|patch|hotfix|"
    "崩溃|宕机|故障|异常|报错|502|503|504|loading|"
    "网红|奢华|豪华|花边|八卦|恋情|绯闻|豪宅|游艇|"
    "涨停|跌停|炒股|买入|卖出|持仓|空仓|牛市|熊市|"
    "福利|白送|赠送|送礼|礼品|有奖|免费抽|免费用",
    re.IGNORECASE,
)
def industry_pass(it):
    cat = it.get("category") or ""
    if cat != "industry":
        return True  # 非行业动态不过滤
    text = ((it.get("title") or "") + " " + (it.get("summary") or "")).lower()
    # 1) 必须有公司关键词
    comps, kws = classify_hits(it)
    if not comps and not REG_SIGNAL.search(text):
        return False
    # 2) 必须有高价值信号（政治/监管/诉讼/立法/数据里程碑）
    if not INDUSTRY_HIGH_SIGNAL.search(text):
        return False
    # 3) 排除低价值信号
    if INDUSTRY_LOW_SIGNAL.search(text):
        return False
    return True

# V3.1: 技巧与观点过滤——排除娱乐八卦、活动促销、低信号帖
TIP_LOW_SIGNAL = re.compile(
    "网红|奢华|豪华|房价一晚|花边|八卦|恋情|"
    "活动|派对|晚宴|招待会|酒会|庆典|"
    "促销|打折|免费|退款|福利|白送|赠送|"
    "炒股|涨停|跌停|持仓|牛市|熊市|"
    "抽奖|有奖|薅羊毛|白嫖",
    re.IGNORECASE,
)
def tip_pass(it):
    cat = it.get("category") or ""
    if cat != "tip":
        return True  # 非技巧与观点不过滤
    text = ((it.get("title") or "") + " " + (it.get("summary") or "")).lower()
    # 0) 排除娱乐八卦/活动促销/炒股/低质内容
    if TIP_LOW_SIGNAL.search(text):
        return False
    # 1) 必须有公司关键词 或 高关注度信号词
    comps, kws = classify_hits(it)
    if comps:
        return True
    # 2) 高关注度信号：KOL/独家观点/深度分析/成长故事
    high_engagement = re.compile(
        "独家|深度|重磅|分析|解读|趋势|预判|展望|报告|裁员|估值|融资|"
        "\$\d+[亿百千万][美元]|"
        "CEO|创始人|总裁|CXO|首席|VP|副总裁|"
        "拒绝.*邀请|回国创业|创业故事|经历|口述|独家专访",
        re.IGNORECASE,
    )
    if high_engagement.search(text):
        return True
    # 3) 来源检查：社交媒体短帖且无公司词 → 丢弃
    src_name = ((it.get("source") or {}).get("name") or "").lower()
    social_sources = ["twitter", "x.com", "x平台", "@", "substack", "reddit"]
    if any(s in src_name for s in social_sources):
        if len(text) < 200 and not comps:
            return False
    return True

def add_items(items, via_reg=False):
    for it in items:
        iid = it.get("id")
        if not iid or iid in seen:
            continue
        comps, kws = classify_hits(it)
        # 监管回退条目：必须命中公司关键词 或 命中监管信号词 才保留
        if via_reg and not comps and not REG_SIGNAL.search((it.get("title") or "") + " " + (it.get("summary") or "")):
            continue
        if JUNK_TITLE.search(it.get("title") or ""):
            continue
        # V3.0: 行业动态 + 技巧与观点过滤
        if not industry_pass(it):
            continue
        if not tip_pass(it):
            continue
        seen[iid] = it
        hit_company[iid] = comps
        hit_kws[iid] = kws
        if via_reg:
            it["_reg"] = True

for f in sorted(glob.glob(os.path.join(SCAN_DIR, "q*_sel.json"))):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    n = re.search(r"q(\d+)_sel", os.path.basename(f)).group(1)
    items = d.get("items") or []
    # 监管/博弈检索区间 q109-q116；q101-q108 是新增公司检索（华为/Kimi/MiniMax）
    via_reg = 109 <= int(n) <= 116
    if items:
        add_items(items, via_reg=via_reg)
    # V2.2 修复（2026-08-02）：all 全量流补充当日实时条目（今日新增来源）
    # all 流是关键词检索结果，已限定主题，不套用 via_reg 严格过滤
    # （否则大量不含公司名的今日 AI 新闻被过滤，导致"今日新增=0"）
    # 注意：add_items 按 id 去重，sel 已收录的不会重复添加
    af = os.path.join(SCAN_DIR, f"q{n}_all.json")
    if os.path.exists(af):
        try:
            d2 = json.load(open(af))
            add_items(d2.get("items") or [], via_reg=False)
        except Exception:
            pass

items_all = sorted(seen.values(), key=timeline_ts, reverse=True)

# V2.2（2026-08-02）：写出 merged.json 供门户统计/日报使用（路径与 SCAN_DIR 一致）
try:
    with open(os.path.join(SCAN_DIR, "merged.json"), "w", encoding="utf-8") as _mf:
        json.dump({"total": len(items_all), "items": items_all}, _mf, ensure_ascii=False)
except Exception:
    pass

# 分类分组
groups = {slug: [] for slug, _, _, _ in CAT_ORDER}
for it in items_all:
    cat = it.get("category") or "industry"
    # V3.0: ai-products 合并到 ai-models（模型与产品发布统一类目）
    if cat == "ai-products":
        cat = "ai-models"
    # V3.0: paper 论文研究类目删除，不再收录
    if cat == "paper":
        continue
    if cat not in groups:
        cat = "industry"
    groups[cat].append(it)

# ---------------- 输出辅助 ----------------
def esc(s):
    return html.escape(s or "", quote=True)

def highlight(text):
    if not text:
        return ""
    out, pos = [], 0
    for m in re.finditer(KW_RE, text):
        out.append(esc(text[pos:m.start()]))
        out.append(f"<mark>{esc(m.group())}</mark>")
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)

def rel_time(it):
    pa, da = it.get("publishedAt"), it.get("discoveredAt")
    def ts(s):
        if not s: return None
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
        except Exception:
            return None
    pa_t, da_t = ts(pa), ts(da)
    if pa_t is None: use_ts = da_t
    elif da_t is None: use_ts = pa_t
    else: use_ts = pa_t if (da_t - pa_t > 72*3600) else da_t
    if use_ts is None:
        return "时间未知", ""
    dt = datetime.fromtimestamp(use_ts, TZ)
    diff = NOW - dt
    secs = diff.total_seconds()
    if secs < 0: rel = "刚刚"
    elif secs < 3600: rel = f"{int(secs//60)} 分钟前"
    elif secs < 86400: rel = f"{int(secs//3600)} 小时前"
    elif secs < 172800: rel = "昨天"
    else: rel = f"{int(secs//86400)} 天前"
    return rel, dt.strftime("%Y-%m-%d %H:%M")

def truncate_summary(s, limit=160):
    s = re.sub(r"\s+", " ", (s or "")).strip()
    if not s:
        return "", False
    if len(s) <= limit:
        return s, False
    return s[: limit - 1].rstrip(), True

# ---------------- KPI ----------------
per_company = {}
for comps in hit_company.values():
    for c in comps:
        per_company[c] = per_company.get(c, 0) + 1
per_company = dict(sorted(per_company.items(), key=lambda x: -x[1]))
per_category = {slug: len(groups[slug]) for slug, _, _, _ in CAT_ORDER}
total = len(items_all)
max_c = max(per_company.values()) if per_company else 1
# 今日新增（北京时间当天时间轴口径）
today_new = sum(1 for it in items_all if timeline_ts(it) >= TODAY_STAMP)

# ---------------- HTML 组装 ----------------
# V2.11: 按日期分版面（用户确认）——按收录日期（北京时间）归档分组，日期 tab 切换
_cat_name_map = dict((s, n) for s, n, _, _ in CAT_ORDER)
date_groups = {}
for it in items_all:
    _dk = datetime.fromtimestamp(timeline_ts(it), TZ).strftime('%Y-%m-%d')
    date_groups.setdefault(_dk, []).append(it)
date_keys = sorted(date_groups.keys(), reverse=True)
for _dk in date_keys:
    date_groups[_dk].sort(key=timeline_ts, reverse=True)
WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
_active_key = NOW.strftime('%Y-%m-%d')
if _active_key not in date_groups and date_keys:
    _active_key = date_keys[0]

seq = 0
cards_by_day = {}
for dk in date_keys:
    rows = []
    for it in date_groups[dk]:
        seq += 1
        title_h = highlight(it.get("title") or "")
        sum_txt, truncated = truncate_summary(it.get("summary"))
        sum_h = highlight(sum_txt) if sum_txt else '<span class="no-summary">（无摘要）</span>'
        rel, ttitle = rel_time(it)
        links = it.get("links") or {}
        link = links.get("original") or links.get("aihot")
        link_href = esc(link) if link else "#"
        badges = []
        if timeline_ts(it) >= TODAY_STAMP:
            badges.append('<span class="tag tag-today" title="北京时间今日收录">🆕 今日</span>')
        if it.get("_reg"):
            badges.append('<span class="tag tag-reg" title="监管/科技博弈相关（关键词检索命中）">⚖️ 监管/博弈</span>')
        if not it.get("selected"):
            badges.append('<span class="tag tag-fallback" title="此条未进入 AI HOT 精选池">全量池收录</span>')
        _cat_t = it.get("category") or "industry"
        if _cat_t == "ai-products":
            _cat_t = "ai-models"
        if _cat_t == "paper":
            _cat_t = "industry"
        if _cat_t not in _cat_name_map:
            _cat_t = "industry"
        badges.append(f'<span class="tag tag-cat">{esc(_cat_name_map[_cat_t])}</span>')
        rows.append(f'''
        <article class="card" id="item-{seq}">
          <div class="card-idx">{seq}</div>
          <div class="card-body">
            <h3 class="card-title">{title_h}</h3>
            <div class="card-meta">
              <span class="meta-src">{esc((it.get("source") or {}).get("name") or "未知来源")}</span>
              <span class="dot">·</span>
              <span class="meta-time" title="北京时间 {ttitle}">{esc(rel)}</span>
              {''.join(badges)}
            </div>
            <p class="card-summary">{sum_h}{' <span class="ellip">…</span>' if truncated else ''}</p>
            <a class="card-link" href="{link_href}" target="_blank" rel="noopener noreferrer">阅读原文 ↗</a>
          </div>
        </article>''')
    cards_by_day[dk] = "".join(rows)

# 日期 tab 导航 + 面板（V2.11 按日期分版面）
tabs = []
panels = []
for dk in date_keys:
    cnt = len(date_groups[dk])
    active = " active" if dk == _active_key else ""
    wd = WEEKDAY_CN[datetime.strptime(dk, '%Y-%m-%d').weekday()]
    disp = dk[5:]
    is_today = " · 今日" if dk == NOW.strftime('%Y-%m-%d') else ""
    tabs.append(f'<button class="tab{active}" data-day="{dk}">📅 {disp} {wd}{is_today}<span class="tab-count">{cnt}</span></button>')
    panels.append(f'''
    <section class="cat-panel{active}" id="panel-{dk}" data-day="{dk}">
      <div class="panel-head"><h2>📅 {dk} {wd}<span class="cat-count">{cnt} 条</span></h2><p class="panel-desc">按北京时间收录日期归档（收录日期 = 抓取/收录时间，真实发布时间见卡片时间）</p></div>
      <div class="cat-list">{cards_by_day[dk] or '<div class="cat-empty">本日暂无收录内容</div>'}</div>
    </section>''')

bars = []
for comp, cnt in per_company.items():
    pct = round(cnt / max_c * 100)
    bars.append(f'<div class="kpi-row"><span class="kpi-row-name" title="{esc(comp)}">{esc(comp)}</span><div class="kpi-bar"><div class="kpi-bar-fill" style="width:{pct}%"></div></div><span class="kpi-row-val">{cnt}</span></div>')

cat_chips = []
for slug, name, icon, _ in CAT_ORDER:
    cnt = per_category.get(slug, 0)
    cat_chips.append(f'<div class="cat-chip"><span class="cat-chip-icon">{icon}</span><span class="cat-chip-name">{esc(name)}</span><span class="cat-chip-val">{cnt}</span></div>')

window_start = (NOW - timedelta(days=7)).strftime("%m-%d")
window_end = NOW.strftime("%m-%d")

doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>中外主要 AI 公司动态 · 商业情报看板（近 7 天）</title>
<style>
  :root {{
    --bg: #f4f5f7; --panel: #ffffff; --ink: #17233b; --muted: #64707f;
    --accent: #b4251a; --accent-dark: #8f1b12; --accent-soft: #fdf0ef;
    --line: #e3e6ec; --mark-bg: #fff2c2; --mark-ink: #6b4d00;
    --reg-bg: #eef4ff; --reg-ink: #1d4ed8;
    --nav-h: 52px;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--ink); font-family: "PingFang SC", "Microsoft YaHei", "Segoe UI", -apple-system, sans-serif; line-height: 1.62; }}
  .wrap {{ max-width: 1120px; margin: 0 auto; padding: 20px 16px 60px; }}

  /* 顶栏 */
  header.hero {{ background: linear-gradient(135deg, #7a1212 0%, #b4251a 55%, #d6453b 100%); color: #fff; border-radius: 14px; padding: 24px 26px 20px; box-shadow: 0 8px 22px rgba(150,30,20,.18); position: relative; overflow: hidden; }}
  header.hero::after {{ content: ""; position: absolute; right: -60px; top: -60px; width: 220px; height: 220px; border-radius: 50%; background: rgba(255,255,255,.06); }}
  .hero-back {{ display: flex; align-items: center; gap: 8px; font-size: 12.5px; margin-bottom: 12px; position: relative; z-index: 1; }}
  .hero-back a {{ color: #fff; text-decoration: none; background: rgba(255,255,255,.16); padding: 4px 12px; border-radius: 999px; font-weight: 600; transition: background .15s; }}
  .hero-back a:hover {{ background: rgba(255,255,255,.3); }}
  .hero-back-sep {{ opacity: .6; }}
  .hero-back-cur {{ background: rgba(255,255,255,.1); padding: 4px 12px; border-radius: 999px; }}
  .hero h1 {{ font-size: 21px; font-weight: 700; letter-spacing: .5px; }}
  .hero .sub {{ font-size: 12.5px; opacity: .88; margin-top: 5px; }}
  .hero .hero-meta {{ display: flex; gap: 10px; margin-top: 13px; flex-wrap: wrap; font-size: 12px; position: relative; z-index: 1; }}
  .hero .hero-meta span {{ background: rgba(255,255,255,.15); padding: 3px 11px; border-radius: 999px; }}

  /* 固定分类 tab */
  .tabbar {{ position: sticky; top: 0; z-index: 50; background: rgba(244,245,247,.92); backdrop-filter: blur(8px); padding: 10px 0 8px; margin-bottom: 14px; }}
  .tabbar-inner {{ display: flex; gap: 8px; overflow-x: auto; scrollbar-width: none; }}
  .tabbar-inner::-webkit-scrollbar {{ display: none; }}
  .tab {{ flex: 0 0 auto; display: inline-flex; align-items: center; gap: 6px; border: 1px solid var(--line); background: var(--panel); color: var(--ink); font-size: 13px; font-weight: 600; padding: 9px 14px; border-radius: 999px; cursor: pointer; transition: all .15s; font-family: inherit; }}
  .tab:hover {{ border-color: var(--accent); color: var(--accent); transform: translateY(-1px); }}
  .tab.active {{ background: var(--accent); border-color: var(--accent); color: #fff; box-shadow: 0 3px 10px rgba(180,37,26,.25); }}
  .tab-count {{ background: rgba(0,0,0,.07); border-radius: 999px; padding: 0 7px; font-size: 11px; font-weight: 700; }}
  .tab.active .tab-count {{ background: rgba(255,255,255,.22); }}

  /* KPI */
  .kpi-grid {{ display: grid; grid-template-columns: 1fr 1.7fr 1fr; gap: 12px; margin-bottom: 12px; }}
  .kpi-card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 15px 16px; text-align: center; }}
  .kpi-main {{ background: linear-gradient(180deg, var(--accent-soft), #fff); border-color: #f0c9c5; }}
  .kpi-num {{ font-size: 30px; font-weight: 800; color: var(--accent); line-height: 1.2; }}
  .kpi-num.kpi-sm {{ font-size: 16px; font-weight: 700; color: var(--ink); }}
  .kpi-label {{ font-size: 12px; color: var(--muted); margin-top: 3px; }}
  .kpi-panel {{ display: grid; grid-template-columns: 1fr 1.15fr; gap: 12px; margin-bottom: 16px; }}
  .kpi-half {{ background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 15px 16px; }}
  .kpi-half h3 {{ font-size: 12.5px; color: var(--muted); font-weight: 600; margin-bottom: 10px; }}
  .cat-chips {{ display: grid; grid-template-columns: 1fr 1fr; gap: 7px; }}
  .cat-chip {{ display: flex; align-items: center; gap: 7px; background: #f7f8fa; border: 1px solid var(--line); border-radius: 9px; padding: 7px 10px; font-size: 12.5px; }}
  .cat-chip-name {{ flex: 1; }}
  .cat-chip-val {{ font-weight: 700; color: var(--accent); }}
  .kpi-bars {{ display: flex; flex-direction: column; gap: 5px; }}
  .kpi-row {{ display: flex; align-items: center; gap: 8px; font-size: 12px; }}
  .kpi-row-name {{ width: 92px; text-align: right; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .kpi-bar {{ flex: 1; height: 11px; background: #eef0f4; border-radius: 6px; overflow: hidden; }}
  .kpi-bar-fill {{ height: 100%; background: linear-gradient(90deg, #b4251a, #e0726a); border-radius: 6px; }}
  .kpi-row-val {{ width: 22px; font-weight: 700; color: var(--accent); }}

  /* 分类面板 */
  .cat-panel {{ display: none; }}
  .cat-panel.active {{ display: block; animation: fadeIn .25s ease; }}
  @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
  .panel-head {{ margin-bottom: 12px; }}
  .panel-head h2 {{ display: flex; align-items: center; gap: 8px; font-size: 17px; font-weight: 700; }}
  .panel-head .cat-count {{ font-size: 12px; font-weight: 600; color: var(--muted); margin-left: auto; background: #f1f3f7; padding: 2px 10px; border-radius: 999px; }}
  .panel-desc {{ font-size: 12.5px; color: var(--muted); margin-top: 4px; }}
  .cat-list {{ display: flex; flex-direction: column; gap: 9px; }}
  .card {{ display: flex; gap: 14px; background: var(--panel); border: 1px solid var(--line); border-radius: 11px; padding: 13px 15px; transition: all .15s; }}
  .card:hover {{ border-color: #d8a39d; box-shadow: 0 4px 14px rgba(150,30,20,.07); transform: translateY(-1px); }}
  .card-idx {{ flex: 0 0 32px; height: 32px; border-radius: 8px; background: var(--accent-soft); color: var(--accent); font-weight: 800; font-size: 13px; display: flex; align-items: center; justify-content: center; }}
  .card-body {{ flex: 1; min-width: 0; }}
  .card-title {{ font-size: 14.5px; font-weight: 650; line-height: 1.5; }}
  .card-meta {{ display: flex; align-items: center; flex-wrap: wrap; gap: 6px; font-size: 12px; color: var(--muted); margin: 4px 0 6px; }}
  .meta-src {{ font-weight: 600; color: #3a4356; }}
  .card-summary {{ font-size: 13.5px; color: #3d4757; }}
  .no-summary {{ color: #9aa3b2; font-style: italic; }}
  .card-link {{ display: inline-block; margin-top: 7px; font-size: 12.5px; color: var(--accent); text-decoration: none; font-weight: 600; }}
  .card-link:hover {{ text-decoration: underline; }}
  mark {{ background: var(--mark-bg); color: var(--mark-ink); border-radius: 3px; padding: 0 2px; }}
  .tag {{ font-size: 11px; padding: 1px 8px; border-radius: 999px; font-weight: 600; white-space: nowrap; }}
  .tag-today {{ background: #e9f7ef; color: #0d7a45; border: 1px solid #bfe6d0; }}
  .tag-reg {{ background: var(--reg-bg); color: var(--reg-ink); }}
  .tag-fallback {{ background: #fef3c7; color: #92400e; }}
  .tag-cat {{ background: #eef2f7; color: #475569; border: 1px solid #dbe3ee; }}
  .refresh-strip {{ background: #fff; border: 1px solid #e8d9d7; border-left: 4px solid var(--accent); border-radius: 10px; padding: 10px 14px; font-size: 12.5px; color: #3d4757; margin-bottom: 14px; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }}
  .refresh-strip b {{ color: var(--accent-dark); }}
  .rs-dot {{ width: 8px; height: 8px; border-radius: 50%; background: #22a35e; flex: 0 0 auto; box-shadow: 0 0 0 3px rgba(34,163,94,.15); }}
  .cat-empty {{ background: var(--panel); border: 1px dashed var(--line); border-radius: 11px; padding: 22px; text-align: center; color: var(--muted); font-size: 13px; }}
  .tip-strip {{ background: var(--accent-soft); border: 1px solid #f0c9c5; color: #7c2a22; border-radius: 10px; padding: 10px 14px; font-size: 12.5px; margin-bottom: 14px; }}
  .tip-strip b {{ color: var(--accent-dark); }}
  footer {{ text-align: center; font-size: 12px; color: var(--muted); margin-top: 32px; }}
  footer a {{ color: var(--accent); text-decoration: none; }}
  @media (max-width: 760px) {{
    .kpi-grid {{ grid-template-columns: 1fr 1fr; }}
    .kpi-panel {{ grid-template-columns: 1fr; }}
    .cat-chips {{ grid-template-columns: 1fr; }}
    .wrap {{ padding: 12px 10px 44px; }}
    .hero h1 {{ font-size: 17px; }}
    .card {{ padding: 11px; gap: 9px; }}
    .card-idx {{ flex-basis: 27px; height: 27px; font-size: 12px; }}
    .kpi-row-name {{ width: 76px; }}
  }}
</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <div class="hero-back">
      <a href="https://iranorawahaha.github.io/international-news-kb/" target="_blank" rel="noopener noreferrer">🏠 Ira 信息看板</a>
      <span class="hero-back-sep">|</span>
      <a href="https://iranorawahaha.github.io/international-news-kb/international-news.html" target="_blank" rel="noopener noreferrer">🌍 国际新闻看板</a>
      <span class="hero-back-sep">|</span>
      <span class="hero-back-cur">🤖 AI 动向看板</span>
    </div>
    <h1>中外主要 AI 公司动态 · AI 动向看板</h1>
    <p class="sub">数据源：AI HOT 精选资讯 · 全文检索 15 家中外 AI 公司 + 监管/科技博弈关键词 · Ira 信息看板 · 仅供参考交流</p>
    <div class="hero-meta">
      <span>📅 时间窗：{esc(window_start)} ~ {esc(window_end)}（近 7 天）</span>
      <span>🎯 命中总数：{total} 条（去重）</span>
      <span>🆕 今日新增：{today_new} 条</span>
      <span>🕗 时间口径：北京时间</span>
    </div>
  </header>

  <div class="refresh-strip">
    <span class="rs-dot"></span>
    <b>最近刷新：</b>{esc(NOW.strftime("%Y-%m-%d %H:%M"))} 北京时间（每日自动刷新） ·
    <b>今日新增 {today_new} 条</b>（带「🆕 今日」标记）·
    数据快照，滚动 7 天窗口
  </div>

  <div class="tip-strip">💡 <b>按日期归档：</b>版面按北京时间收录日期分组（X日版面 = X日收录的内容），默认展示今日；卡片「🕐 时间」为真实发布时间（显示用），⚖️ 标签为监管/博弈相关条目，🏷️ 分类标签为 AI 行业动态 / 模型与产品发布 / 技巧与观点。</div>

  <div class="kpi-grid">
    <div class="kpi-card kpi-main"><div class="kpi-num">{total}</div><div class="kpi-label">命中动态总数（去重后）</div></div>
    <div class="kpi-card"><div class="kpi-num kpi-sm">{esc(window_start)} ~ {esc(window_end)}</div><div class="kpi-label">统计时间窗 · 近 7 天</div></div>
    <div class="kpi-card"><div class="kpi-num kpi-sm">{len(per_company)}</div><div class="kpi-label">覆盖公司数</div></div>
  </div>



  <nav class="tabbar">
    <div class="tabbar-inner">{''.join(tabs)}</div>
  </nav>

  <main>{''.join(panels)}</main>

  <footer>
    数据来源：<a href="https://aihot.virxact.com" target="_blank" rel="noopener noreferrer">AI HOT</a> · 条目按 id 去重，按收录日期归档 · 高亮为命中关键词 · 摘要 ≤160 字 · 完整内容点击「阅读原文」
  </footer>
</div>
<script>
(function () {{
  var tabs = document.querySelectorAll(".tab");
  var panels = document.querySelectorAll(".cat-panel");
  tabs.forEach(function (tab) {{
    tab.addEventListener("click", function () {{
      var day = tab.getAttribute("data-day");
      tabs.forEach(function (t) {{ t.classList.toggle("active", t === tab); }});
      panels.forEach(function (p) {{ p.classList.toggle("active", p.getAttribute("data-day") === day); }});
      window.scrollTo({{ top: 0, behavior: "smooth" }});
    }});
  }});
}})();
</script>
</body>
</html>'''

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(doc)

# V2.1: JS 语法自检（防 <script> 语法错误导致页面空白，2026-08-01 事故教训）
import subprocess, sys as _sys
_js_blocks = re.findall(r"<script>(.*?)</script>", doc, re.S)
_ok = True
for _i, _js in enumerate(_js_blocks, 1):
    try:
        _r = subprocess.run(["node", "--check"], input=_js.encode("utf-8"), capture_output=True, timeout=10)
        if _r.returncode != 0:
            _ok = False
            print(f"❌ JS 语法错误 (script#{_i}): {(_r.stderr or b'').decode('utf-8', 'replace')[:200]}")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # 无 node 时退化为括号配对
        if _js.count("{") != _js.count("}"):
            _ok = False
            print(f"❌ JS 大括号不匹配 (script#{_i}): {_js.count('{')} vs {_js.count('}')}")
if _ok:
    print("✅ JS 语法自检通过")
else:
    print("❌ JS 语法自检失败，终止构建")
    _sys.exit(1)

print("=== v2 看板 ===")
print("去重总数:", total)
print("分类分布:", per_category)
print("公司分布:", per_company)
print("written:", OUT_HTML, len(doc), "bytes")
