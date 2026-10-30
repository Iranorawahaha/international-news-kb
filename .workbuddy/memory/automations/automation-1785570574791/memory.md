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
