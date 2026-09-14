# 国际新闻看板（V2.15）· 详细规则
> 脚本 update-news.sh；数据 data/news-data.json（archive[YYYY-MM-DD]）

- ⚠️ `--auto` 的 git add 不含 data/news-webfetch.json 与 us-official.json → 收尾精确补提交
- ⚠️ 每日刷新前先试跑：前日提交可能引入 NameError（09-10：`category_counts` 被误写成 `column_counts`，`set -e` 下 HTML 不生成、后续全断）
- 信源 12 英文全必选（路透/BBC/SCMP/卫报/CNN/NYT/WSJ/半岛/Politico/WaPo/AP/FT）；彻底排除中文信源/自媒体；黑名单 cnnbc.com、cnnbc.cn
- V2.13 7 板块 L2 归一（仅当日版面）；飞书同步前核对 options（缺则映射防 800030005）
- **FT 通道**：官网对终端恒 403（Cloudflare+付费墙），WebFetch/curl/archive.today 均不可达 → 无自动正文通道；`https://r.jina.ai/<FT原文URL>` 可取 Title+Published Time → WebSearch 找 3+ 转述媒体交叉核实 → 用户浏览器供全文最优。已登记 config.json（id=ft, pri=32）。严禁凭 URL 编造标题/摘要
- **反爬替代通道（fetch_paywall_sources.py）**：路透/WSJ/Politico/WaPo 官网恒 401/403 严禁硬抓 → ①线索 Google News RSS `site: when:2d`；②真实 URL：路透→economictimes/finwire/sedaily/asiae/koreatimes，WSJ→TradingView DJN_DN/finwire，Politico→politico.eu，WaPo→官网(WebSearch)/zetik；③禁低质聚合；转载加 repost_from；窗口内无涉华稿如实空缺
- **V2.15 路透官网 URL**：DataDome 域名级拦截（全路径 401、无代理 000）→「401=存在」验证法无效；官网 URL 只取第三方背书（聚合/转载页列出的 reuters.com 链接且 slug 与标题逐字对应 / 用户浏览器提供），禁构造；Yahoo/AOL canonical 的 `tag:reuters.com,2026:newsml_XXX` 可验真。反查 SOP：候选标题→WebSearch 精确变体→命中即换官网 URL 并清 repost_from→miss 落转载；每日附「一键搜官网」清单（gen_reuters_recheck_list.py）。`data['today']` 会陈旧，当日取 `dates[0]`
- ⚠️ **9-11 新增路透官网定位法**：`html.duckduckgo.com/html/?q=site:reuters.com+<标题关键词>`（urllib+代理）可直接列出 reuters.com 官方 slug，9-11 借此取得 AI 芯片涨价与机器人冠军两条官网 URL（均 /world/asia-pacific/...-2026-09-10/）
- ⚠️ **9-14 新增路透官网定位法（首选，优于上两条）**：直接用 `WebSearch` 搜**完整英文标题**即可返回 reuters.com 官网 URL（9-14 命中 `reuters.com/world/europe/trump-says-very-negative-forces-raising-exaggerated-concerns-over-ai-2026-09-13/`，slug 与标题逐字对应）→ **路透条目第一优先动作 = WebSearch 完整标题 → 结果含 reuters.com 即直接采用、免 repost_from**；未命中再走 DuckDuckGo 端点 / 转载通道。9-14 实测合格转载域名：Yahoo News、Euronext Live、Channel NewsAsia、Livemint、New Straits Times、TechNode Global、Seoul Economic Daily、RBC-Ukraine
- ⚠️ **9-14 转载匹配坑**：RSS 标题用弯引号（U+2019/U+201C），按标题匹配 URL 前**必须归一化**（`’‘→'`、`“”→"`、`—–→-`），否则大面积匹配失败（9-14 首轮 12/59 失败）；另 WSJ 候选来自 Google News RSS，**标题常被截断**（如 `...Monumental Crisis for...`），必须二次搜索确认完整标题才可入库，禁凭猜测补全
- 交叉验证（V2.12）：WebFetch 后必做 3 组 WebSearch(d2)：①China AI chips export controls 1260H CXMT YMTC ②US China tariffs sanctions announcement ③AI export control remote access compute China The Information
- The Information/SemiAnalysis = 主题补充源（AI芯片/出口管制/远程算力必查）；路透重大日补 /technology /business
- 官方源必补 title_zh/summary_zh（页面真实日期）；WSJ 反爬用 WebSearch 拿真实 URL 绝不编造
- ⚠️ fetch_us_official.py：某源失败整组被覆盖 → 跑后必检 6 源齐全，缺则 `git show <昨日commit>:data/us-official.json` 恢复；失败先 `env -u http_proxy -u https_proxy curl` 测直连
- ⚠️ V2.11.3 窗口校验：webfetch 混入 date<昨天旧报道；collectedAt 须 startswith 前缀匹配；删今日条目四步同步（news-data.json + 根/gh-pages 两 HTML 的 NEWS_DATA + webfetch.json 源头）+ HTML 统计修正
- V2.13.1 程序性白宫文告（Presidential Message / Proclamation on National XX Month|Week|Day）→ `_is_procedural` 不入池 + 降权 75
- RSS：SCMP `/rss/4|91|5/feed` 必须 `-L` 跟 301；WSJ RSS 返旧稿 → 弃用；CNN→edition.cnn.com/world，AP→apnews.com/world-news
- **RSS 兜底清单（代理 7890）**：BBC feeds.bbci.co.uk/news/world/rss.xml、Guardian /world/rss、AJ /xml/rss/all.xml、NYT /services/xml/rss/nyt/World.xml、WaPo feeds.washingtonpost.com/rss/world（+/rss/business/technology）、Politico politico.com/rss/politicopicks.xml 与 rss.politico.com/politics-news.xml —— 后两家 RSS 代理直取 200 且带真实官网 URL，可直接上板
- HTML 重建免全流程：`awk '/^python3 << .GENERATE_HTML_V12.$/{f=1;next} /^GENERATE_HTML_V12$/{f=0} f' update-news.sh > /tmp/gen.py && python3 /tmp/gen.py`，之后仍跑 check_js_syntax.py + inject_nav.py
- 飞书存档 A2fdb93HLamcKgslr2rcopjRnfd（tblCocvO66XoPsm1）25 条/批；选项维护 `+field-get`→append→`+field-update` full PUT，**hue 只能 Gray**；单批 ≤200 行，>200 按 date 定向
