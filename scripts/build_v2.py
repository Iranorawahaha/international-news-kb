#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 公司商业情报看板 构建脚本 V3（V2.11 表格化统一 UI · Ira 信息看板体系）
- 合并 /tmp/aihot_scan 下所有查询响应（selected 优先，空则用 all 回退）
- 公司扩展到 15 家（+华为、Kimi、MiniMax）
- 监管/科技博弈关键词命中条目需通过监管信号词过滤（剔除无关噪音）
- 输出 ai-news.html / ai-company-intel.html（统一表格化 UI，主题色橙）
"""
import json, glob, re, html, os
from datetime import datetime, timezone, timedelta

# V2.2 修复：抓取产物在 ${TMPDIR}/aihot_scan
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
KB_DIR = "/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50"
TEMPLATE_FILE = os.path.join(KB_DIR, "scripts", "_table_ui_template.html")
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
TODAY_START = datetime(NOW.year, NOW.month, NOW.day, 0, 0, 0, tzinfo=TZ)
TODAY_STAMP = TODAY_START.timestamp()

# AI 主题色（橙色）
THEME = {
    "primary": "#d97706",
    "primary_2": "#b45309",
    "primary_light": "#f59e0b",
    "primary_bg": "#fffbeb",
    "primary_bg_2": "#fde68a",
    "grad_1": "#7c2d12",
    "grad_2": "#b45309",
    "grad_3": "#d97706",
    "shadow_primary": "0 4px 20px rgba(217,119,6,0.15)",
    "row_hover": "rgba(245,158,11,0.10)",
}

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

REG_SIGNAL = re.compile(
    "监管|法案|法规|合规|限制令|禁令|制裁|出口管制|出口|管制|关税|走私|审查|下架|诉讼|起诉|"
    "法院|罚款|执法|封锁|禁运|国产替代|自主可控|反垄断|垄断|地缘|博弈|中美|欧盟|华盛顿|"
    "行为准则|GPAI|FCC|光刻机|安全政策|芯片管制|算力枢纽|国家安全",
    re.IGNORECASE,
)

# V3.1: 低价值信号黑名单
JUNK_TITLE = re.compile(
    "苹果库克|三星李在镕|Google Camp|Linux VPS|SGLang|财报电话会议|"
    "不限量免费|到店连Wi-Fi|免费Token|白嫖|白送|免费试用|免费领取|免费额度|免费用|"
    "限时免费|0元|零元|免费版|永久免费|促销|大促|秒杀|"
    "网红|奢华品牌|房价一晚|豪华之旅|花边|绯闻|吃瓜|恋情|"
    "斩杀|涨停|跌停|崩盘|爆仓|A股|港股|美股收盘|盘前|开盘|"
    "获利了结|抄底|逃顶|做空报告|"
    "QQ浏览器|浏览器更新|输入法更新|天气更新|"
    "有奖征集|有奖活动|抽奖|福利领取|薅羊毛",
    re.IGNORECASE,
)

CAT_ORDER = [
    ("industry", "行业动态", "⚖️"),
    ("ai-models", "模型与产品发布", "🏗️"),
    ("tip", "技巧与观点", "💡"),
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
            # 映射到公司
            c = kw_company.get(k.lower())
            if c:
                comps.add(c)
    return comps, kws

# V3.0: 行业动态过滤（保留命中关键词的 + 监管信号词的）
def industry_pass(it):
    text = ((it.get("title") or "") + " " + (it.get("summary") or "")).lower()
    for k in ALL_KW:
        if k.lower() in text:
            return True
    return bool(REG_SIGNAL.search(text))

# V3.0: 技巧与观点过滤
def tip_pass(it):
    title = it.get("title") or ""
    summary = it.get("summary") or ""
    if not title and not summary:
        return False
    return True

def add_items(items, via_reg=False):
    for it in items:
        iid = it.get("id")
        if not iid or iid in seen:
            continue
        comps, kws = classify_hits(it)
        if via_reg and not comps and not REG_SIGNAL.search((it.get("title") or "") + " " + (it.get("summary") or "")):
            continue
        if JUNK_TITLE.search(it.get("title") or ""):
            continue
        if not industry_pass(it):
            continue
        if not tip_pass(it):
            continue
        seen[iid] = it
        hit_company[iid] = comps
        hit_kws[iid] = kws
        if via_reg:
            it["_reg"] = True

# 读取所有 q*_sel.json + q*_all.json
for f in sorted(glob.glob(os.path.join(SCAN_DIR, "q*_sel.json"))):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    n_match = re.search(r"q(\d+)_sel", os.path.basename(f))
    if not n_match:
        continue
    n = int(n_match.group(1))
    items = d.get("items") or []
    via_reg = 109 <= n <= 116
    if items:
        add_items(items, via_reg=via_reg)
    af = os.path.join(SCAN_DIR, f"q{n}_all.json")
    if os.path.exists(af):
        try:
            d2 = json.load(open(af))
            add_items(d2.get("items") or [], via_reg=False)
        except Exception:
            pass

items_all = sorted(seen.values(), key=timeline_ts, reverse=True)

# V2.2: 写出 merged.json 供门户统计/日报使用
try:
    with open(os.path.join(SCAN_DIR, "merged.json"), "w", encoding="utf-8") as _mf:
        json.dump({"total": len(items_all), "items": items_all}, _mf, ensure_ascii=False)
except Exception:
    pass


# ---------------- 构造 NEWS_DATA + 注入模板 ----------------
def build_article_for_template(it):
    """将 aihot item 适配为通用模板的 article 结构"""
    url = ((it.get("links") or {}).get("original")) or ((it.get("links") or {}).get("aihot")) or ""
    src_name = ((it.get("source") or {}).get("name")) or "未知来源"
    pub = it.get("publishedAt") or ""
    disc = it.get("discoveredAt") or ""
    # 真实发布日（仅显示用）
    real_date = ""
    for s in (pub, disc):
        if s and len(s) >= 10:
            try:
                datetime.fromisoformat(s.replace("Z", "+00:00"))
                real_date = s[:10]
                break
            except Exception:
                real_date = s[:10]
                break
    # 收录日期（按 timeline_ts 的北京时间）
    ts_v = timeline_ts(it)
    if ts_v:
        col_date = datetime.fromtimestamp(ts_v, TZ).strftime("%Y-%m-%d")
    else:
        col_date = real_date or NOW.strftime("%Y-%m-%d")

    # 优先级：监管类=88；公司命中≥2=80；公司命中=72；否则=60
    comps = hit_company.get(it.get("id"), set())
    if it.get("_reg"):
        score = 88
    elif len(comps) >= 2:
        score = 80
    elif len(comps) == 1:
        score = 72
    else:
        score = 60

    cat = it.get("category") or "industry"
    if cat == "ai-products":
        cat = "ai-models"
    if cat == "paper":
        cat = "industry"

    return {
        "title": it.get("title") or "",
        "title_en": "",
        "title_zh": it.get("title") or "",
        "summary": it.get("summary") or "",
        "summary_zh": it.get("summary") or "",
        "source": src_name,
        "category": cat,
        "priority_score": score,
        "url": url,
        "date": real_date,
        "collectedAt": (disc or pub or ""),
        "keywords": sorted(list(hit_kws.get(it.get("id"), set())))[:6],
        "_reg": bool(it.get("_reg")),
    }


def build():
    # 按收录日期（北京时间）分组（V2.11：按抓取时间归档）
    archive = {}
    for it in items_all:
        a = build_article_for_template(it)
        col_date = (it.get("discoveredAt") or it.get("publishedAt") or "")
        ts_v = timeline_ts(it)
        col_date = datetime.fromtimestamp(ts_v, TZ).strftime("%Y-%m-%d") if ts_v else NOW.strftime("%Y-%m-%d")
        archive.setdefault(col_date, []).append(a)

    dates = sorted(archive.keys(), reverse=True)
    today = NOW.strftime("%Y-%m-%d")
    total_count = len(items_all)
    today_count = sum(1 for it in items_all if timeline_ts(it) >= TODAY_STAMP)
    high_count = sum(1 for it in items_all if it.get("_reg"))
    date_count = len(dates)

    # 7 天窗口裁剪
    cutoff_date = (NOW - timedelta(days=6)).strftime("%Y-%m-%d")
    archive = {d: v for d, v in archive.items() if d >= cutoff_date}
    dates = sorted(archive.keys(), reverse=True)
    date_count = len(dates)

    # 顶部统计表（AI 用 日期×分类 透视）
    cat_icon = {"industry": "⚖️", "ai-models": "🏗️", "tip": "💡"}
    cat_keys = ["industry", "ai-models", "tip"]
    pivot = {d: {c: 0 for c in cat_keys} for d in dates}
    for d in dates:
        for a in archive[d]:
            c = a.get("category", "industry")
            if c in pivot[d]:
                pivot[d][c] += 1
    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    pivot_headers = '<th>日期</th>' + ''.join(f'<th>{cat_icon.get(c, "📌")} {c}</th>' for c in cat_keys) + '<th>合计</th>'
    pivot_rows = []
    for d in dates:
        cells = ''.join(f'<td>{pivot[d][c] if pivot[d][c] else "—"}</td>' for c in cat_keys)
        total_row = sum(pivot[d].values())
        is_today = (d == today)
        today_dot = '<span class="today-dot"></span>' if is_today else ''
        try:
            from datetime import datetime as _dt
            wd = weekday_cn[_dt.strptime(d, "%Y-%m-%d").weekday()]
        except Exception:
            wd = ""
        pivot_rows.append(
            f'<tr><td class="date-cell">{d} {wd} {today_dot}</td>'
            + cells
            + f'<td class="count-cell">{total_row}</td></tr>'
        )
    stats_top = f'''<div class="pivot-wrapper">
        <div class="pivot-title">📅 各日按分类分布（AI · 橙版）</div>
        <div class="pivot-subtitle">行=日期，列=分类；点击表格行可在下方表格中按日期筛选</div>
        <table class="pivot-table">
            <thead><tr>{pivot_headers}</tr></thead>
            <tbody>{"".join(pivot_rows)}</tbody>
        </table>
    </div>'''

    # 左侧栏目侧边栏
    cat_counts = {c: 0 for c in cat_keys}
    for d in dates:
        for a in archive[d]:
            c = a.get("category", "industry")
            if c in cat_counts:
                cat_counts[c] += 1
    sidebar_items = [
        f'<button class="col-item active" data-column="all"><span class="ic">📚</span><span class="nm">全部栏目</span><span class="cnt">{total_count}</span></button>'
    ]
    for c, _, icon in CAT_ORDER:
        cnt = cat_counts.get(c, 0)
        sidebar_items.append(
            f'<button class="col-item" data-column="{c}"><span class="ic">{icon}</span><span class="nm">{c}</span><span class="cnt">{cnt}</span></button>'
        )
    column_sidebar = '\n'.join(sidebar_items)

    # 顶部日期按钮
    date_buttons = [f'<button class="date-btn active" data-date="all">全部日期 <span class="cnt">{total_count}</span></button>']
    for d in dates:
        cnt = len(archive.get(d, []))
        is_today = (d == today)
        label = f"{d[5:]} {'· 今' if is_today else ''} ({cnt})"
        date_buttons.append(f'<button class="date-btn" data-date="{d}">{label}</button>')
    date_head_buttons = '\n'.join(date_buttons)

    if dates:
        window_str = f"{dates[-1][5:]} ~ {dates[0]}（近 7 天）"
    else:
        window_str = NOW.strftime("%m-%d（暂无数据）")
    now_full = NOW.strftime("%Y-%m-%d %H:%M")

    # 读模板
    with open(TEMPLATE_FILE, encoding="utf-8") as f:
        template = f.read()

    news_data = {"archive": archive, "dates": dates, "today": today}
    news_json = json.dumps(news_data, ensure_ascii=False)
    news_json = news_json.replace("</", "<\\/")

    replacements = {
        "__TITLE__": "🤖 AI 动向看板 · Ira 信息看板",
        "__HEADER_H1__": "🤖 AI 动向看板",
        "__SUBTITLE__": "信源：AI HOT 公开 API · 33 组关键词（15 家中外 AI 公司 + 监管/科技博弈方向）· 3 大分类（行业动态 / 模型与产品发布 / 技巧与观点）· 该看板仅供 Ira 信息看板体系参考交流",
        "__NAVBAR_INTL_ACTIVE__": "",
        "__NAVBAR_AI_ACTIVE__": "active",
        "__SOURCE_NOTE__": "AI HOT 公开数据 · 33 组关键词检索 · 已过滤营销号/娱乐八卦/炒股财经等低价值信号。",
        "__STATS_TOP__": stats_top,
        "__SIDEBAR_HEADER__": "📂 栏目筛选",
        "__COLUMN_SIDEBAR__": column_sidebar,
        "__DATE_HEAD_BUTTONS__": date_head_buttons,
        "__TOTAL_COUNT__": str(total_count),
        "__TODAY_COUNT__": str(today_count),
        "__HIGH_COUNT__": str(high_count),
        "__DATE_COUNT__": str(date_count),
        "__NOW_STR__": window_str,
        "__NOW_FULL__": now_full,
        "__NEWS_DATA_JSON__": news_json,
        "__FOOTER__": "🤖 AI 动向看板 V2.11 · 表格化统一 UI · 数据更新于 " + now_full + " · 7天窗口 · Powered by Ira 信息看板体系",
        "__THEME_PRIMARY__": THEME["primary"],
        "__THEME_PRIMARY_2__": THEME["primary_2"],
        "__THEME_PRIMARY_LIGHT__": THEME["primary_light"],
        "__THEME_PRIMARY_BG__": THEME["primary_bg"],
        "__THEME_PRIMARY_BG_2__": THEME["primary_bg_2"],
        "__THEME_GRAD_1__": THEME["grad_1"],
        "__THEME_GRAD_2__": THEME["grad_2"],
        "__THEME_GRAD_3__": THEME["grad_3"],
        "__THEME_SHADOW_PRIMARY__": THEME["shadow_primary"],
        "__THEME_ROW_HOVER__": THEME["row_hover"],
    }
    for k, v in replacements.items():
        template = template.replace(k, v)

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(template)

    print(f"written: {OUT_HTML} ({len(template)} bytes)")
    print(f"  总 {total_count} 条 | 今日 {today_count} 条 | 高优 {high_count} 条")
    print(f"  日期数: {date_count} | 顶部统计表: {len(pivot_rows)} 行")


def main():
    try:
        build()
    except Exception as e:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()