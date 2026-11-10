# 自动化执行记忆：国际新闻看板每日刷新

## 2026-10-28 刷新（周三，覆盖 10-27 09:30~10-28 09:30，V2.17）
- 官方源**第 44 次源组丢失**（直出 31 条，国务院仅 2 / 白宫 1）→ `cp` 备份恢复 + merge 3 条新增（白宫治安调查 / 国务院巴拿马通话·圣文森特国庆）→ **219 条 6 源齐全**、导航残留 0、中文 0 缺失
- 13 信源：**路透 sitemap 全分片 401**（非往年 slug 问题，是入口整体拒绝）→ Google News 发现 100 条 + WebSearch 逐条反查转载，**7 条全部实测 HTTP 200**（AOL×2 / 印度经济时报 / U.S. News / NewsBreak / Geo News / WSJ 官网 1）；彭博 RSS **21 候选 → 入库 4**（jina.ai 本轮**恢复可用**，正文 lede 正常取到）；FT RSS 3 条；RSS 11 通道 200（WaPo 连续第 13 日 502）；CNN/AP hub 可用条目少
- 交叉验证命中 1 条重大补录：**财政部对外投资新版拟议规则（新增生物技术/高超音速/超算，SI 替代 AI 定义）94★** → 经 Federal Register API 取**真实 html_url**（自拼 URL 虽返 200 但并非该文档）
- 今日版面 **55 条 / 13 源**（南华20/路透7→修正后6/卫报5/BBC4/彭博4/Politico4/纽约3/FT3/国务院2/白宫1/财政部1/半岛1/WSJ1）；中美5/AI8/中国外交5/中欧5/地区9/美国内政8/全球多边7/其他8；≥88 共 20
- 校验全绿：cAt≠今日 0 · 历史URL重复 0 · 版面内 URL/标题重复 0 · 彭博 4/4 · 官方 4 条中文摘要齐全 · title≠title_zh 0 · 模板摘要 0 · 裸实体 0 · 来源错标 0 · JS 0 错误 · 双端 832853 字节 md5 一致
- git：`d2e2ee2`（auto）→ `c01f5b3`（repost 回填）→ `4484f72`（--auto 纳入财政部条）→ `57aea63`（repost 再回填）→ `1de6c6f`（来源修正），全部直连 push 成功
- ⚠️ 飞书 `token_missing` **连续第 21 日**；路透反查清单 **7 条待用户回报官网 URL**（连续 27 日为空后首次非空）
- **新经验**：① **路透入口可能整体 401**，不要只重试 sitemap，直接切 Google News + WebSearch 通道 ② **自拼 URL 返 200 不代表是目标文档**，须走官方 API（如 Federal Register `/api/v1/documents.json`）取真实 html_url ③ 本轮 `repost_from` 被整合层丢弃**两次**（每次 --auto 后都要回填）④ 手工写 source 仍会错标（本轮 2 条 SCMP 标成半岛/路透）→ 收尾必跑「域名→source」覆盖 ⑤ 终端输出约 550-2000 字节即被截断，长脚本须拆成多段 `cat >>` 追加写入

## 2026-10-28 第二轮刷新（同日 10:23 触发，覆盖 10-28 09:30~10:30）
- 触发原因：当日 09:30 首轮已出 55 条，本轮为第二次刷新（同一日期版面叠加）
- 官方源**第 45 次源组丢失**（直出 31 条，国防部 21 条霸榜 / 国务院 2 / 白宫 1）→ 备份恢复 220 条 + 补 2 条新增（国务院汤加会见 / 白宫能源交易），**222 条 6 源齐全**
- 13 信源：**Reuters 官网整体 401**（sitemap/首页全拒）→ Google News 100 条发现 + WebSearch 反查，仅 1 条合格转载入库（AOL 甲骨文芯片）；**FT 官网 403 但 `ft.com/rss/home` 25 条 200 可用**（此前一直误判 FT 只能走 jina）；彭博 RSS **16 候选 → 入库 2**；WaPo 官网+RSS 双双不可用 → Google News 标题可见但 URL 无法解析，**14 条全部放弃（宁缺毋滥）**；CNN/AP hub 可用条目极少
- **关键教训：403 ≠ 失效**。一度严格按"HTTP 200"过滤，结果 72 条只剩 22 条（FT/彭博/南华/纽时/Politico 全线 403），按规则回退为"403 保留、404 剔除"，最终 64 条
- 今日版面 **64 条 / 13 源**（南华21/路透6/卫报6/彭博5/BBC5/Politico5/纽约4/FT4/国务院3/半岛2/WSJ1/白宫1/CNN1）；AI10/地区10/美国内政9/全球多边9/其他9/中美6/中欧6/中国外交5；≥88 共 21
- 校验全绿：cAt≠今日 0 · date<昨天 0 · 历史URL重复 0 · 版面内URL重复 0 · title空 0 · summary空 0 · 来源错标 0 · 模板摘要 0 · 裸实体 0 · JS 0 错误 · 双端 md5 一致（532330 字节）
- git：`81ce4af`（--auto）→ `2cde049`（修 null 字段+归档）→ `d89ac4e`（repost 回填）；**push 直连连续 3 次失败（Failed to connect / Failure when receiving data）→ 改走 7890 代理成功**
- ⚠️ 飞书 `token_missing` 连续第 22 日；路透反查清单 **6 条待用户回报官网 URL**
- **本轮新经验（重要）**：① **整合层会把 `title`/`summary` 写成 null**（只有 title_zh/summary_zh），前端标题直接空白 → 收尾必查 `title null / summary null` 并回填 ② **date 早于昨天的官文仍会进今日版面**（白宫奥列什基条 date=10-23 混入）→ 手动移回对应版面 ③ `repost_from` 连续第 2 日被整合层清空，回填后**必须再跑一次 GENERATE_HTML** 才在前端出现 ④ 抓 Google News 的 `site:xxx when:2d` 可拿到标题+时间，但**跳转页已不含原始 URL**，无法据此反推官网链接 ⑤ 自己"拼"FT/纽时/WaPo 的 URL slug 会大量 404，必须从 RSS 取真实 UUID/路径

## 2026-10-29 刷新（周四，覆盖 10-28 09:30~10-29 09:30，V2.17）
- 官方源**第 46 次源组丢失**（直出 28 条，仅国防部/USTR/财政部/商务部，白宫+国务院全失）→ 备份恢复 + **URL 键合并** → **222 条 6 源齐全**、导航残留 0、中文 0 缺失
- 13 信源：**Reuters 官网整体 401**（连续第 2 日）→ Google News 90 条发现 + WebSearch 反查，**5 条入库全部实测 200**（Straits Times/Euronext/NewsBreak/Internazionale/Yahoo Sports）；彭博 RSS **16 候选 → 入库 5**；FT RSS 12 条 → 入库 5；WaPo RSS 连续第 14 日 502；CNN/AP hub 可用条目少
- 交叉验证命中 1 条重大补录：**商务部对华厢式拖车双反税令（合计 265.61%，叠加 232 约 290%）93★** → 走 Bloomberg 官网 URL
- 今日版面 **45 条 / 9 源**（南华10/彭博5/FT5/路透5/卫报5/BBC5/半岛4/纽时3/Politico3）；中欧与盟友10/AI·科技8/地区局势7/全球多边7/其他5/中国外交3/美国内政3/中美博弈2；≥88 共 11
- 校验全绿：cAt≠今日 0 · date<昨天 0 · 历史URL重复 0 · 版面内URL/标题重复 0 · title≠title_zh 0 · 模板摘要 0 · 裸实体 0 · 来源错标 0 · JS 0 错误 · 双端 md5 一致（752456 字节）
- git：`6d0be31`（--auto）→ `b84a1d9`（repost 回填 + 官方池 + HTML 重生成），直连 push 成功
- ⚠️ 飞书 `token_missing` **连续第 23 日**；路透反查清单 **5 条待用户回报官网 URL**
- **新经验**：① 官方源恢复必须用「URL 键合并」（直接覆盖会丢白宫/国务院历史）② `repost_from` 连续第 3 日被整合层清空，回填后须**单独重跑 GENERATE_HTML_V12 段** ③ **URL 路径日期段比 RSS pubDate 更可信**（两条纽时稿 date 写错被窗口过滤）④ Politico 链接不能手拼 slug，缺 ID 后缀即 404，找不到就删条 ⑤ `--auto` 的 git add 仍不含 `data/us-official.json`

## 2026-10-30 刷新（周五，覆盖 10-29 09:30~10-30 09:30，V2.17）
- 官方源**第 47 次源组丢失**（直出 31 条，**国务院 HTTP 407**、白宫仅 3、财政部 0）→ `cp` 备份 + **URL 键合并** → **225 条 6 源齐全**（国务院109/白宫65/国防部31/USTR9/财政部8/商务部3），新增 3 条白宫稿（GDP 通稿 / 美芬技术繁荣协议 MOU / 选前宣传稿），已补中文标题+摘要
- 13 信源：**Reuters 官网整体 401（连续第 3 日）**，sitemap 与 world 首页全 401 → Google News 100 条发现 + WebSearch 反查，**3 条合格转载**（Central Oregon Daily/FCC、CNBC TV18/巴西稀土、Daily Sabah/特朗普对加拿大）；**WSJ RSS 再次确认返回 2025-01 旧稿（禁用）**；WaPo RSS **连续第 15 日 502**；CNN hub 仅视频稿、AP hub 无日期（两者弃用）；FT `ft.com/rss/home` 10 条 200；彭博 RSS **26 候选 → 入库 3**（jina.ai **退化**：返回导航菜单而非正文，改为 RSS description + 已知事实撰写摘要）
- **RSS 主力化**：SCMP 三通道（4/91/5）+ Politico 双通道 + Politico EU feed，共汇总 365 条、去历史后 329 新，窗口内涉华候选 115 条
- 交叉验证 3 组：① 命中 **FCC 禁中国实验室 93★**（已于 SCMP 覆盖）② 中国 AI 出口管制稿正文为 10-16 发布，**属旧闻未收录**（路透 10-28 版本亦已在上轮）③ CXMT HBM3E 为 10-28 路透旧稿，未收录。补录彭博 2 条（政治局补员 / 中国临床试验）
- 今日版面 **33 条 / 9 源**（南华14/白宫3/路透3/彭博3/BBC3/卫报2/纽时2/Politico2/FT1）；中欧与盟友7/AI·科技6/美国内政5/中美博弈4/中国外交4/地区局势4/其他2/全球多边1；**≥88 未单列统计**
- 校验全绿：cAt≠今日 0 · date<昨天 0 · 历史URL重复 0 · 版面内URL重复 0 · title空 0 · summary空 0 · title≠title_zh 0 · 模板摘要 0 · 裸实体 0 · **彭博 3/3** · repost 3 · JS 0 错误 · **线上线下 699929 字节 md5 完全一致**
- git：`0fea120`（--auto）→ `ce8dad5`（--auto 二次纳入彭博 2 条）→ `fbaf4e3`（repost 回填 + 官方池中文 + HTML 重生成），全部直连 push 成功
- ⚠️ 飞书 `token_missing` **连续第 24 日**（需用户跑 `lark-cli auth login`）；路透反查清单 **3 条待用户回报官网 URL**
- **新经验（本轮关键）**：① **Bash heredoc 长内容会被静默截断**（约 2000 字符），写中文长摘要必须用 `Write` 工具落 JSON 文件，不要用 `python3 <<PY` 内联大段文本 ② `Write` 单次内容过长同样会被截断（出现无 file_path 报错）→ **一个文件只放 1-3 条**，多批累积 ③ **手拼 SCMP slug 必 404**（`.../article/3372591/china-promotes-general-zhang-shengmin-politburo` 实际缺 `-pla-antigraft` 段）→ 必须从 `/tmp/rss_all.json` 取 RSS 原文链接 ④ `repost_from` **连续第 4 日**被整合层清空，回填后须单独 `sed -n '910,1011p' update-news.sh > /tmp/gen_html.py && python3 /tmp/gen_html.py` 重生成 ⑤ 彭博 jina.ai 通道不稳定：本轮返回导航页，摘要退化为 RSS description + 交叉来源，**不可凭 URL 编造**

## 2026-10-31 刷新（周六，覆盖 10-30 09:30~10-31 09:30，V2.17）
- 官方源**第 48 次源组丢失**（直出 28 条且**全部是 8 月旧稿**，白宫+国务院全失、财政部仅 3 条旧稿）→ `cp` 备份 + URL 键合并 23 条新增（白宫3/国务院9/财政部3/国防部6/USTR2）→ **248 条 6 源齐全**、中文 0 缺失
- **网络故障新形态（重要）**：直连与 7890 代理**同时 000**（连 bbc/reuters/白宫全挂，国内站 200）→ 一度误判为出口故障。**真实原因＝ClashX 正在切换节点（09:25 刚启动）**，等约 5 分钟后代理自行恢复（google 302 / bbc 200）。教训：**代理 000 先看 `ps aux | grep ClashX` 启动时间与 9090 控制口节点列表，别急着判定外网不可达**
- 13 信源：**Reuters 官网整体 401（连续第 4 日）** → Google News 3 组关键词发现 60+ 条 → WebSearch 英文精确反查转载，**6 条全部合格**（NewsBreak/Straits Times/The Standard/RTÉ/AnewZ/Yahoo）；**FT `ft.com/rss/home` 11 条 200**（入库5）；彭博 RSS **22 候选 → 入库 5**；WaPo RSS **502 第 16 日**；WSJ RSS 仍 2025-01 旧稿（禁用）；CNN/AP hub 可用条目少
- RSS 9 通道汇总 387 条（SCMP 三通道 150 / BBC 39 / 卫报 45 / 纽时 54 / 半岛 25 / Politico 74），窗口内 243 条
- 交叉验证 3 组：**「中国禁国家出资数据中心用外国AI芯片」为近期稿但日期不可证实，按旧闻规则不收录**；FCC 电信新规已于 10-30 版面覆盖；232 机器人公告与 10-29 条重复
- 今日版面 **57 条 / 13 源**（南华8/国务院7/路透6/BBC6/FT5/彭博5/半岛4/卫报4/Politico4/纽时3/财政部3/国防部1/白宫1）；地区局势18/AI·科技11/美国内政8/中欧与盟友6/中美博弈6/全球多边4/中国外交3/其他1
- 校验全绿：cAt≠今日 0 · date<昨天 0 · 历史URL重复 0 · 版面内URL/标题重复 0 · title≠title_zh 0 · 模板摘要 0 · 裸实体 0 · 来源错标 0 · 彭博 5/5 · 官方中文摘要齐全 · repost 6 · JS 0 错误 · **线上线下 719106 字节 md5 完全一致**
- git：`d914779`（--auto）→ `ac10f47`（过期条目移出 + repost 回填 + HTML 重生成），直连 push 成功
- ⚠️ 飞书 `token_missing` **连续第 25 日**；路透反查清单 **6 条待用户回报官网 URL**
- **新经验**：① **手写 SCMP/BBC/卫报/纽时/半岛的 URL slug 几乎必错**（本轮 pool_1 有 10 条 URL 是推断的 → 一条条回 RSS 取真实链接；pool_2 批量替换还出现 key 错位把卫报换成 BBC 的 URL）→ **一律从 `/tmp/rss_all.json` 按标题匹配取 url，禁止手拼** ② 官方源恢复后**必须先按 date 过滤再进池**，本轮 8 条 10-26~10-29 的旧稿混进今日版面 ③ `sed -n '909,1011p'` 多取了一行 `python3 << 'GENERATE_HTML_V12'` 导致 NameError，正确是 **910,1010** ④ 代理节点切换会造成「全网 000 假象」，详见上条

## 2026-11-02 刷新（周一，覆盖 10-31 09:30~11-02 09:30，V2.17）
- 官方源**第 49 次源组丢失**（直出 29 条、国务院 HTTP 407、白宫仅 1）→ `cp` 备份 + URL 键合并 → **249 条 6 源齐全**、导航残留 0、中文 0 缺失；唯一新增＝白宫诸圣节致辞（程序性，75★）
- 13 信源：**Reuters 官网 `/world/china/` WebFetch 首次成功（打破连续 5 日 401）**，拿到 20 条真实官网 URL；但 `/world/`、`/asia-pacific/`、文章详情页仍 fetch failed → 部分稿走 Google News + WebSearch 转载（Straits Times / Korea Herald 实测 200）。彭博 RSS **16 候选 → 入库 8**；FT `ft.com/rss/home` 9 条 200 入库 4；WaPo RSS 502 第 17 日、Politico RSS 首轮 000 重试后 200、CNN RSS 000 改 hub、AP 无日期弃用
- 交叉验证命中 2 条重大补录：**联邦公报 11-02 刊登机器人/工业机械 232 公告 11077（90★，/d/ 链接实测 200）**、**中国拟将 23 项 AI 技术列入出口管制目录（11-15 截止，91★）**；另核实中国 AI 出口管制草案为 10-16 发布（非当日稿，未当新闻收录）
- 今日版面 **47 条 / 13 源**（南华14/彭博8/路透6/BBC5/FT4/半岛3/白宫1/WSJ1/工商时报1/商务部1/卫报1/纽时1/CNN1）；地区局势11/AI·科技9/全球多边8/中国外交5/美国内政5/中美博弈4/中欧3/其他2；≥88 共 18
- 校验全绿：cAt≠今日 0 · date<昨天 0 · 历史URL重复 0 · 版面内URL/标题重复 0 · title/summary 空 0 · title≠title_zh 0 · 模板摘要 0 · 裸实体 0 · 来源错标 0 · JS 0 错误 · **线上线下 355800 字节完全一致**
- git：`5bfd946`（--auto）→ `3b999dc`（--auto 二次纳入补录）→ `f922507`（移出过期 + HTML 重生成），直连 push 成功
- ⚠️ 飞书 `token_missing` **连续第 26 日**；路透反查清单 **2 条待用户回报官网 URL**（官网占比 4/6）
- **新经验（重要）**：① **update-news.sh 的 V2.11.3 窗口过滤对 `news-webfetch.json` 池不生效**（clean_articles 无 date 判断，430 行过滤点在 dedupe 之后失效）→ 写入池时必须自己把 date 卡在 {昨天,今天}，否则 10-30/31 旧稿混入今日版面（本轮复发 2 次）② **详情页普遍 403/401，列表页可抓**：Reuters 分类页 WebFetch 可用、文章页不可用 → 摘要只能靠 RSS description + 列表页信息 ③ jina.ai 本轮 **401 封禁（AS53667 网络信誉）**，彭博正文通道不可用 → 退回 RSS description ④ `/tmp/pool_*.json` 会跨日残留，`glob` 前必须先清理否则混入前一日数据 ⑤ 手拼 BBC/卫报/SCMP/半岛 URL 仍必错，一律从 `/tmp/rss_all_1102.json` 取

## 2026-11-03 刷新（周二，V2.17）
- **网络**：GitHub 直连 000、7890 代理 200 → 全程走代理（含 git push `-c http.proxy=`）
- 官方源**第 50 次源组丢失**（直出 31 条、国务院 HTTP 407、财政部 0 条）→ `cp` 备份 + URL 键合并 → **251 条 6 源齐全**、导航残留 0、template 0；新增 2 条白宫稿（巡访通稿 / 成绩单，均宣传性 75 档）
- 13 信源：**Reuters 官网 curl 全 401，但 WebFetch `/world/china/` 唯一可用**（拿到 20 条真实官网 URL，`/world/`、`/business/`、`/technology/` 仍 fetch failed）→ **路透 10 条全部官网 URL、repost=0，反查清单首次为空**（达目标态）
- **新媒体通道（新发现，重要）**：`https://feeds.content.dowjones.io/public/rss/RSSWorldNews`（+ `/WSJcomUSBusiness`、`/RSSWSJD`）返回 **WSJ 当日真实 RSS 188 条** → 旧「WSJ RSS 返回 2025-01 旧稿」结论只适用于 `feeds.a.dj.com`；`www.wsj.com/rss/world` 仍 403
- 其余：BBC/卫报/NYTimes/SCMP 三通道/FT/Politico(congress+defense+eu)/半岛 RSS 全 200；Politico 主 RSS `politicopicks.xml` 403 但 `rss.politico.com/*.xml` 可用；WaPo RSS **301 跳首页、连续第 18 日不可用**（弃）；CNN/AP hub 无可用日期条目（弃）
- 彭博 RSS **21 候选 → 入库 14**（jina.ai 仍 401 AS53667 封禁 → 摘要基于 RSS description + 跨源事实）；FT 6 条
- 交叉验证 3 组：UFLPA 新增华大基因/华大智造/华大集团为 **10-28 旧闻**（已在前版面）未收录；中国 AI 出口管制 23 项仍属 10-16 旧闻；第三组无窗口内新规 → **本轮零补录**
- 今日版面 **77 条 / 11 源**（彭博14/南华12/路透10/BBC9/WSJ6/FT6/纽约5/卫报5/半岛5/Politico3/白宫2）；AI·科技18/地区局势16/美国内政12/全球多边11/中美博弈9/中国外交8/中欧3；≥88 共 34
- 校验全绿：cAt≠今日 0 · date<昨天 0 · 历史URL重复 0 · 版面内URL重复 0 · title/summary 空 0 · title≠title_zh 0 · 模板摘要 0 · 裸实体 0 · 彭博 14/14 · JS 0 错误 · **线上线下 560443 字节 md5 完全一致**
- git：`ccb8179`（--auto）→ `86fa725`（白宫标题中文化 + pool 归档）→ `6275a3b`（栏目修正），全走代理 push 成功
- ⚠️ 飞书 `token_missing` **连续第 27 日**；路透反查清单 **0 条**（首次达成目标态）
- **本轮新经验**：① **整合层会忽略池内 category**，14 条自定义分类被打成「其他」→ 收尾必须按「其他」逐条复核并重归类，再单独跑 GENERATE_HTML ② **官方源 title 字段可能仍是英文**（title_zh 已中文但 title 未同步）→ 必查 `title != title_zh` ③ **WSJ 走 dowjones 新 RSS 域可直取当日稿**，勿再只试 `feeds.a.dj.com`（那是 2025-01 死源）④ Politico 不必依赖 403 的主 picks feed，`rss.politico.com/politics-news|congress|defense.xml` 均 200 ⑤ Reuters 单频道可用时即可让今日路透 100% 官网化，优先保 `/world/china/`

## 2026-11-04 刷新（周三，覆盖 11-03 09:30~11-04 09:30，V2.17）
- **网络**：GitHub 直连 000、7890 代理 200 → 全程走代理（含 git push `-c http.proxy=`）；`--auto` 内置 push 直连超时 75s 失败，手工代理 push 补推成功
- 官方源**第 51 次源组丢失**（直出 34 条、国务院 HTTP 407、财政部 0）→ `cp` 备份 + URL 键合并 → **257 条 6 源齐全**、导航残留 0；新增 6 条白宫稿（反共周/太空自由宣言/法案签署/2 条 ICYMI/制造业通稿）
- **反共周文告属程序性文告 → 按 V2.13.1 从版面剔除**（其余白宫稿保留，降权 75~88）
- 13 信源：**Reuters 官网全入口 401**（world/china、world、technology、business、sitemap 全挂）→ Google News 88 条发现 + WebSearch 英文精确反查，**合格转载仅 2 条**（凤凰网转述 SK 海力士 / 中央社转述 IPO 暂停），均实测可读
- **WSJ 走 `feeds.content.dowjones.io/public/rss/RSSWorldNews` 直取当日真实 URL 188 条**（含 UUID 哈希后缀）→ 入库 5；旧结论「WSJ RSS 是 2025-01 死源」仅适用 `feeds.a.dj.com`
- 其余 RSS：BBC/卫报/纽时/SCMP 三通道/FT/半岛/Politico(politics-news) 全 200；WaPo RSS **502 第 19 日**；CNN/AP hub 无可用日期（弃）
- 彭博 RSS **21 候选 → 入库 15**（本轮未走 jina 正文，摘要基于 RSS description + 跨源事实）
- 交叉验证 3 组命中 1 条重大补录：**英伟达划出 49% 算力红线（单数据中心对华客户算力不得超总量 49%）92★** → 经腾讯新闻转述 FT Technology News 收录；另核实商务部 11-02 李成钢会见美国农产品代表团（date=11-02 < 昨天，按窗口规则未入今日版面）
- 今日版面 **72 条 / 10 源**（南华16/彭博15/FT7/卫报6/纽时6/白宫5/WSJ5/BBC5/半岛5/路透2）；AI·科技17/地区局势16/美国内政14/全球多边7/中国外交6/中美博弈6/中欧与盟友6；≥88 共 17；元首级 4
- 校验全绿：cAt≠今日 0 · date<昨天 0 · 历史URL重复 0 · 版面内URL/标题重复 0 · title≠title_zh 0 · 模板摘要 0 · 裸实体 0 · 彭博 15/15 · repost 3 · JS 0 错误 · **线上线下 359703 字节 md5 完全一致**
- git：`91ec3d0`（--auto）→ `8c55064`（补 Bai 字段 + 分类校正 + 交叉补录），代理 push 成功
- ⚠️ 飞书 `token_missing` **连续第 28 日**；路透反查清单 **2 条待用户回报官网 URL**（官网占比 0/2）
- **本轮新经验（重要）**：① **整合层把 `summary` 字段整列写成 None**（仅 summary_zh 有值）→ 前端摘要空白，收尾必须用 `summary=summary_zh` 回填 66 条 ② **整合层按标题关键词重排 category**，本轮 8 条错位（SK 海力士→AI、伊朗银行→地区、卡尼→中欧等）→ 收尾需按池内 category 逐条对齐，并把「其他」全部归位 ③ **白宫/官方稿的 title_zh 缺失且 title 仍是英文** → 需按 URL 子串（非全等，URL 带 query）匹配补写 ④ `node` 截图脚本因缺 `node_modules/puppeteer-core` 已不可用，截图能力当前不可用

## 2026-11-05 刷新（周四，覆盖 11-04 09:30~11-05 09:30，V2.17）
- **网络**：GitHub 直连 200（少见），7890 代理亦可用；`--auto` push 直连一次成功
- 官方源**第 52 次源组丢失**（直出 30 条、白宫 1 / 国务院 1 / 财政部 3 且多为旧稿）→ `cp` 备份 + URL 键合并 → **259 条 6 源齐全**、导航残留 0；新增 2 条（白宫选后动员通稿 75★ / 国务院制裁伊朗影子船队 90★），已补中文
- **jina.ai 通道恢复**：彭博 20 条正文全部取到（HTTP 200 / 约 16–21KB），摘要基于正文 lede 撰写
- 13 信源：**Reuters `/world/` 与 `/world/china/` WebFetch 均成功**（各 20 条真实官网 URL；`/technology/` 仍 failed）→ **路透 12 条全部官网 URL、repost=0，反查清单为空（达目标态）**；WSJ 走 `feeds.content.dowjones.io` 71 条；SCMP 三通道 150 条；Politico `rss.politico.com/*` 90 条；WaPo RSS **502 第 20 日**（弃）；CNN/AP hub 无可用日期（弃）
- 彭博 RSS **20 候选 → 入库 17**；FT `ft.com/rss/home` 13 条 → 入库 6
- 交叉验证 3 组命中 2 条重大补录：**The Information 韩制 HBM 经香港走私入华为供应链（昇腾960DT / 单颗 HBM3E 黑市 4000 美元）93★**、**178 项对华 301 豁免 11-09 到期（USTR 未公告延期）91★**
- 今日版面 **85 条 / 14 源**（彭博17/南华14/路透12/卫报7/WSJ6/FT6/BBC6/半岛5/Politico4/纽时4/白宫1/国务院1/The Information1/USTR1）；美国内政20/AI·科技17/地区局势15/中欧11/中美10/全球多边7/中国外交5；≥88 共 17，元首级 4
- 校验全绿：cAt≠今日 0 · date<昨天 0 · 历史URL重复 0 · 版面内URL/标题重复 0 · title≠title_zh 0 · 模板摘要 0 · 裸实体 0 · 来源错标 0 · 彭博 17/17 · repost 2 · JS 0 错误 · **线上线下 406306 字节完全一致**
- git：`222ac7f`（--auto）→ `3a10a35`（栏目校正 43 条 + 官方中文 + repost 回填 + HTML 重生成）→ `316a646`（官方池 8 条历史条目补中文），全部直连 push 成功
- ⚠️ 飞书 `token_missing` **连续第 29 日**；路透反查清单 **0 条**
- **本轮新经验**：① **RSS 的 `<link>` 才是真 URL，RSS 里 slug 与 article-title 常不一致**（WSJ `oil-prices-sink` 标题配的是 `oil-prices-rise` 的 URL；SCMP 15 条手写 slug 全部需按 RSS 回填），**手写 slug 一律先按 RSS 索引前缀匹配替换** ② **Politico RSS `pubDate` 缺失（90 条全空）** → 用 URL 的 `/YYYY/MM/DD/` 段作 date，靠前正文页的日期段可能比官宣日早一天 ③ **整合层仍把池内 category 打散**（本轮 43 条需回调，Politico 全被塞进「地区局势/全球多边」）④ 官方池历史条目的 `title_zh` 可能长期为 null（本轮 8 条），会在校验项 1 报错但**不影响当日版面**，须单独补写

## 2026-11-06 刷新（周五，覆盖 11-05 09:30~11-06 09:30，V2.17）
- **网络**：GitHub 直连 000、7890 代理全程可用（含 git push `-c http.proxy=`）
- 官方源**第 53 次源组丢失**（直出 34 条、国务院 5 / 白宫 1 / 财政部 3）→ `cp` 备份 + URL 键合并 → **265 条 6 源齐全**、导航残留 0；新增 6 条（白宫椭圆办公室纪念区 / 国务院悬赏 Tren de Aragua·太子集团·古巴制裁×2·鲁比奥-安瓦尔通话），全部补中文
- 13 信源：**Reuters 官网全入口 401**（world/china、world、sitemap 全挂）→ Google News 103 条发现 + WebSearch 反查，合格转载 2 条（中央社）；WSJ 走 `feeds.content.dowjones.io` 73 条；SCMP 三通道 150 条；WaPo RSS **502 第 21 日**（弃）；CNN/AP hub 无可用日期（弃）
- 彭博 RSS **25 候选 → 入库 15**；**jina.ai 本轮被 CAPTCHA 拦截**（返回 "Are you a robot?" ~1.1KB）→ 摘要退回 RSS description + 跨源事实
- FT：**官网 RSS 无相关涉华稿，改走 `fetch_paywall_sources.py` + WebSearch 交叉印证** → 抓到 FT 独家「甲骨文取消腾讯 70 亿美元芯片租赁」经 Straits Times 转载入库
- 交叉验证命中 2 条重大补录：**路透独家 60 万颗 H200 滞留香港（95★）**、**The Information/黄仁勋国会闭门简报（92★）**；另核实**中国商务部对美正丙醇续征双反税 5 年（88★，税率 254.4–267.4% / 34.2–37.7%）**
- 今日版面 **70 条 / 13 源**（南华20/彭博15/FT5/WSJ5/国务院4/卫报5/半岛5/BBC3/路透2/纽时2/Politico2/商务部1/白宫1）；AI·科技22/地区局势14/美国内政13/中美博弈9/中欧6/中国外交5/全球多边1；≥88 共 19，元首级 6，repost 3
- 校验全绿：cAt≠今日 0 · date<昨天 0 · 历史URL重复 0 · 版面内URL/标题重复 0 · title空 0 · title≠title_zh 0 · summary空 0 · 模板摘要 0 · 裸实体 0 · 官方中文缺 0 · **彭博 15/15** · JS 0 错误 · **线上线下 679477 字节完全一致**
- git：`73b67d8`（--auto 首轮 358 条，池丢 52）→ `0078822`（修字段后 412 条）→ `4e4ce17`（栏目归位 29 条 + 古巴条合并 + repost 回填 + HTML 重生成），代理 push 成功
- ⚠️ 飞书 `token_missing` **连续第 30 日**；路透反查清单 **2 条待用户回报官网 URL**（官网占比 0/2）
- **本轮新经验（极重要，必查）**：① **池条目缺 `title` 字段会被 `is_garbage_article` 判为「标题过短」整条丢弃** —— 只写 `title_zh` 不写 `title` 时 69 条池只进 17 条，静默无声，是本轮最大坑 → **写池时必须同时写 `title=title_zh` 与 `summary=summary_zh`** ② 同源「声明 + Fact Sheet」两条 URL 仅差尾斜杠，脚本 `rstrip('/')` 后仍判不同 → 手工合并为一条 ③ jina.ai 会返回 CAPTCHA 页（200 但仅 1.1KB），**以 size 判断有效性，勿只看状态码** ④ FT 官网 RSS 常无当日涉华稿，改用 `fetch_paywall_sources.py` 的 Google News 层捕 FT 独家

## 2026-11-08 刷新（周日，覆盖 11-06 09:30~11-08 20:09，V2.17）
- 触发时间 20:09（周末晚场，非常规 09:30），今日版面为新建日 2026-11-08
- **网络**：GitHub 直连首查 200 但 push 两次 `Failed to connect` / `Failure when receiving data` → **改走 7890 代理 push 成功**（`git -c http.proxy=http://127.0.0.1:7890 -c https.proxy=...`）；`--auto` 内置 push 同样直连失败
- 官方源**第 54 次源组丢失**（直出 28 条，白宫 0 / 国务院 0 / 财政部 0，且全部是 7–8 月旧稿）→ `cp` 备份 + URL 键合并 → **265 条 6 源齐全**（国务院124/白宫79/国防部37/财政部11/USTR11/商务部3），**本次 0 新增**（WebFetch 白宫/国务院/财政部列表页最新稿均为 11-07 及更早，已在池中）
- 13 信源：**Reuters 官网全入口 401**（world/china、world、asia-pacific 全 fetch failed）→ Google News + WebSearch 反查，**合格转载 2 条**（The Financial Express 转稀土/农产、The Star 转人大）；WSJ 走 `feeds.content.dowjones.io` 71 条；SCMP 三通道 150 条；**WaPo RSS 第 22 日后首次恢复 200**（11 条）；Politico 主 picks 403 但 `rss.politico.com/*` 与 `politico.eu/feed` 可用；CNN/AP hub 弃用
- 彭博 RSS **11 候选 → 入库 3**（26 条涉华关键词过滤后）；**jina.ai 通道恢复**（19KB 正文，Party Congress / 能源投资 / AI 资金流向三条 lede 全部取到）
- 交叉验证 3 组命中重大补录：**美国务院首次以涉古巴为由制裁两家中国企业（中方 11-07 回应，93★）**、**中美经贸高层 6 日晚视频通话为深圳 APEC 会晤铺路（财政部原文+路透+中央社+工商时报四源，95★）**、**十国涉港联合声明（黄之锋判10年，88★）**
- 今日版面 **52 条 / 14 源**（南华13/华尔街6/纽约5/BBC4/卫报4/半岛4/彭博3/FT3/Politico3/路透2/华盛顿邮报2/中央社1/工商时报1/环球时报1）；地区局势17/AI·科技11/中美博弈7/中欧与盟友5/中国外交4/美国内政4/全球多边3/其他1；≥88 共 10，元首级 5，repost 2
- 校验全绿：cAt≠今日 0 · date<昨天 0 · 历史URL重复 0 · 版面内URL重复 0 · title≠title_zh 0 · title/summary 空 0 · 模板摘要 0 · 裸实体 0 · 官方中文缺 0 · **彭博 3/3** · JS 0 错误 · **线上线下 432271 字节 md5 完全一致**
- git：`2f810ad`（--auto 407 条）→ `f864e4b`（栏目归位 19 条 + repost 回填 2 + 移出 3 条过期官方稿至其发布日版面 + HTML 重生成），代理 push 成功
- ⚠️ 飞书 `token_missing` **连续第 31 日**；路透反查清单 **2 条待用户回报官网 URL**（官网占比 0/2）
- **本轮新经验**：① **周末场次仍要按 48h 窗口取稿**，但 13 源 RSS 中 11-06 的稿不少（94 条）→ 严格卡 `date∈{昨天,今天}` 会砍掉一半候选，需靠**交叉验证补重大稿**补足体量 ② **官方池「0 新增」是正常态**（周末国务院/白宫不发稿），不要为凑数把旧稿塞进今日版面 ③ `git add` 对 `data/us-official.json` 无改动时静默跳过，`git diff --cached` 必须逐项核对 ④ 整合层本轮把 **19 条栏目打散**（南海→其他、能源投资→其他、赫格塞斯→全球多边等），池内 category 需在 --auto 后全量比对回写 ⑤ `gen_html.py` 正确行范围仍是 **910,1010**

## 2026-11-09 刷新（周一，覆盖 11-08 09:30~11-09 09:30，V2.17）
- **网络**：GitHub 直连 000、外网直连全 000（RSS WebFetch 全 fetch failed）→ `open -a ClashX` 拉起 7890 后全通；`--auto` 内置 push 直连超时 75s 失败，手工代理 push 补推成功（两次均如此）
- 官方源**第 55 次源组丢失**（直出 30 条、国务院/财政部均 read timed out）→ `cp` 备份 + URL 键合并 → **267 条 6 源齐全**（国务院124/白宫81/国防部37/财政部11/USTR11/商务部3）；新增 2 条白宫稿（ICYMI 布兰奇脱口秀 / 排灯节致辞）
- 13 信源：**Reuters WebFetch `/world/china/` fetch failed**（同前，官网全挂）→ WebSearch 反查得 1 条合格转载（AOL 路透电头，关税延期稿）；CNN `/world` + AP `/world-news` WebFetch 可用但多为非涉华；RSS 全通道 200（BBC/卫报/半岛/纽时/SCMP三通道/WaPo/WSJ dwj/FT home/Politico politics-news）
- 彭博 RSS **28 候选 → 入库 14**；**jina.ai 被 CAPTCHA 拦截**（返回 373 字节，10 条全部）→ 摘要退回 RSS description + 跨源事实
- 交叉验证 3 组命中 1 条重大稿：**税委会 2026 年第 6 号公告（24% 关税续停 2 个月、保留 10%，11-10 13:01 生效）96★**，经 AOL/彭博双源交叉；另核实 1260H/YMTC 组无窗口内新规
- 今日版面 **59 条 / 12 源**（南华17/彭博14/半岛9/FT5/WaPo4/WSJ2/卫报2/白宫2/路透1/纽时1/BBC1/AP1）；地区局势15/AI·科技11/美国内政10/中国外交9/中美博弈6/全球多边3/其他3/中欧2；≥88 共 19，元首级 1，repost 1
- 校验全绿：cAt≠今日 0 · date<昨天 0 · 历史URL重复 0 · 版面内URL/标题重复 0 · title≠title_zh 0 · 摘要空 0 · 模板摘要 0 · 裸实体 0 · 官方中文缺 0 · **彭博 14/14** · JS 0 错误 · **线上线下 724217 字节完全一致**
- git：`ab7498d`（--auto 426 条）→ `2143938`（栏目归位 28 条 + 官方中文回填 2 条 + 池归档），代理 push 成功
- ⚠️ 飞书 `token_missing` **连续第 32 日**；路透反查清单 **1 条待用户回报官网 URL**（关税延期稿，官网占比 0/1）
- **本轮新经验**：① **官方源条目走 official 通道会覆盖池内 title_zh/summary_zh 为 null 且标题仍是英文**（本轮白宫 2 条全中，摘要还被截成英文半句）→ 收尾必须按 URL 从池回写 ② 整合层**再次把 28 条栏目打散**（含「其他」9 条），已固化「--auto 后逐条按池 category 回写」为必做动作 ③ `sed -n '910,1010p'` 是 GENERATE_HTML 正确行范围（909 起会带上 heredoc 首行报 NameError）④ WebFetch 对 SCMP 文章页全失败、curl 只回 6KB 骨架 → SCMP 摘要只能靠 RSS description + 跨源 ⑤ 工作日 13:00 场次 date 分布 31/28（今日31、昨日28），属正常

## 2026-11-10 刷新（周二，21:16 晚间场，覆盖 11-09 09:30~11-10 21:16，V2.17）
- **网络**：7890 代理全程可用（GitHub/NYT/WSJ/彭博直连均需代理）；`--auto` 内置 push 一次成功
- 官方源**第 56 次源组丢失**（直出 28 条、国务院 HTTP 407、白宫 read timeout、财政部 0，且**全部 8 月旧稿**）→ `cp` 备份 + URL 键合并 + WebFetch 补 11-09 新增 → **271 条 6 源齐全**（国务院127/白宫82/国防部37/财政部11/USTR11/商务部3）；新增 4 条（白宫参院提名公告 / 国务院赫尔伯格印太行·鲁比奥会见法德外长）
- 13 信源：**Reuters 官网 WebFetch 全入口 fetch failed** → `fetch_paywall_sources.py` Google News 发现 100+ 条（涉华极高密度）→ WebSearch 反查，**3 条合格转载全部实测 200**（Yahoo Finance 顺差 / AOL 微软光模块 / 中央社 NDAA 三法案）；**RSS 15 通道全 200 共 588 条**（含 SCMP 三通道 150、WSJ dwj 双通道 155、WaPo 27、FT 12）；彭博 RSS **25 候选 → 入库 4**（jina.ai **仍 AS53667 401 封禁**，摘要改 RSS description + 跨源事实）
- 交叉验证 3 组全命中重大稿：① **The Information 独家：白宫或放行对华 AI 芯片新管制（DAADD 条款 + 光刻设备 + 远程算力两项立规）94★** ② **微软施压阻止中国光模块禁令（FCC 牵头，3.2Tbps 阈值）93★** ③ **中国贸易顺差首破 1 万亿（前10月 1.04 万亿、10 月出口 +35.2%）95★**
- 今日版面 **38 条 / 14 源**（南华10/彭博4/WSJ3/路透3/BBC3/FT3/国务院3/纽约2/卫报2/The Information1/Politico1/法新社1/半岛1/白宫1）；中美博弈14/AI·科技10/中欧6/地区3/美国内政2/全球多边2/中国外交1；≥88 共 23，元首级 4，repost 5
- 校验全绿：cAt≠今日 0 · date<昨天 0 · 历史URL重复 0 · 版面内URL/标题重复 0 · title空 0 · summary空 0 · title≠title_zh 0 · 模板摘要 0 · 裸实体 0 · 官方中文缺 0 · **彭博 4/4** · 来源错标 0 · JS 0 错误 · **双端 693370 字节 md5 完全一致**；线上二次带参 200 且已含今日标题（字节略滞后于 CDN）
- git：`e5d8920`（--auto 394 条）→ `3786dd0`（栏目归位 16 条 + 官方池中文 + repost 回填 + HTML 重生成），全部代理 push 成功
- ⚠️ 飞书 `token_missing` **连续第 33 日**；路透反查清单 **3 条待用户回报官网 URL**（官网占比 0/3）
- **本轮新经验**：① **Google News 对 Reuters 的覆盖率在本轮达到峰值**（100+ 条涉华标题可见），是官网 401 时唯一可靠发现层，但**跳转页无原始 URL**，必须逐条 WebSearch 反查转载 ② **`pool_10` 那批用 `Write` 时只写了 summary 未写 summary_zh**，靠合并阶段 `setdefault` 兜底修复 → 批量落池后必须统一跑字段补全 ③ **整合层本轮把 16 条栏目打散**（中美博弈↔AI·科技互换居多，还含国务院条被塞进 AI·科技）→ 回写 category 后**必须再跑一次 GENERATE_HTML** ④ **同题合并会静默丢条**（NYT 顺差稿被路透同题合并掉），属正常去重但需在汇报中说明 ⑤ 彭博条目里 `bloomberg.com/news/articles/2026-11-09/china-chipmakers-to-debut...` 的 slug 与标题不一致（脚本已按 URL 日期取 date），沿用为正常
