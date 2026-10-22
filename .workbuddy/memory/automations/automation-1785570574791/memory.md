# 自动化执行记忆：国际新闻看板每日刷新

## 2026-10-20 刷新（周二，覆盖 10-19 09:30~10-20 09:30，V2.17）
- 官方源第 35 次源组丢失（脚本直出仅 40 条，国务院 10 / 白宫 2 / 财政部 0）→ `/tmp/us-official-backup-1020.json` 恢复 + merge 12 条新增（白宫 10-19 堪萨斯行/妇女健康行政令；国务院 10-19 制裁丁林伟关联五实体/美奥战略对话/萨那使馆被羁押五周年/C5+1 系列 8 条）→ **164 条 6 源齐全**（国务院82/白宫43/国防部27/USTR7/财政部4/商务部1），导航残留 0，中文缺失 0（含补 3 条历史条目摘要）
- 13 信源：RSS 10/13 通道 200（**WaPo world+tech 连续第 3 日 502、apnews RSS 403、politico1 403** → CNN/AP 走 WebFetch hub）；**路透 sitemap 10 片 1000 条**（`<news:title>` 空值第 7 次 → slug 匹配，窗口 443 条）；彭博 RSS **25 候选 → 入库 16 条**；FT 官方 RSS 3 条
- ⭐ **URL 硬断言捕获 30 条手写 URL**（BBC ID / NYT slug / Al Jazeera slug / Politico ID / 卫报 slug 全为自行拼写）→ 改「按 title_en 归一化在 RSS 权威集合回填」自动修复 29 条，1 条（Pope Leo）无匹配丢弃；**终态 0 条编造 URL**
- 窗口过滤：候选 103 → URL 不可信 1 + 窗口外 3（多为 10-18 稿）+ 已存重复 2 → **入库 97 条**，collectedAt 全 = 2026-10-20 09:30:00；池 198 → 295
- `update-news.sh --auto` → **397 条 / 6 天**；今日版面 **105 条 / 12 源**（路透31/彭博16/南华14/国务院10/卫报7/NYT7/BBC5/半岛5/美联社3/Politico3/白宫2/FT2）；地区局势30/AI·科技17/全球多边17/美国内政12/其他11/中美博弈9/中欧与盟友5/中国外交4；≥88 共 22
- ⚠️ **官方源 title 字段被写成英文**（12 条新条目 title 取 title_en、title_zh 却已正确）→ 前端标题栏渲染英文；同时 11 条含裸 `&hellip;`/`&nbsp;`/`&#8217;`。修复：deent 清理 + `title = title_zh`，再**单独提取第 4 步 GENERATE_HTML 段重跑**（`sed -n '893,1012p'`）→ 校验全绿
- 校验全绿：collectedAt≠今日 0 · date<昨天 0 · 与历史URL重复 0 · 版面内 URL/标题重复 0 · 彭博 16/16 collectedAt 正确 · **路透官网 31/31** · repost_from 0 · 模板摘要 0 · 裸HTML实体 0（页面层）· 黑名单 0 · 缺中文标题 0 · JS 0 错误 · 双端 HTML md5 一致
- git：`a269463`（--auto）→ `bd96f67`（池+HTML 修复，直连 push 成功）；ls-remote == HEAD；线上 `?t=` 200 / 416828 字符 md5 一致
- ⚠️ 飞书同步失败：lark-cli `token_missing / need_user_authorization`（**连续第 12 日**）→ 需用户 `lark-cli auth login --scope "base:record:create"` 后补跑 `sync_to_feishu.py`
- 交叉验证 3 组：**命中 1 条重大补录——DHS 下令联邦民用机构移除 DeepSeek（94★，已入池）**；CXMT/1260H 无新；美中关税制裁无窗口内新公告
- 固定附加项：`gen_reuters_recheck_list.py` → **连续第 20 日为空**（目标态达成）
- 头条：DHS 令联邦机构移除 DeepSeek(94) / 美制裁五家中国实体涉 AI 窃密(92) / 克里姆林宫称普习特或下月北京三方会晤(92) / 中国三季度 GDP 4.5% 超预期(90-92) / 中国商务部管制盾构机出口(90) / 央行隔夜回购利率「换锚」(88-90) / Z.AI 创始人涉英方指称机构资助研究(90)

### 经验增量（10-20）
- ⭐⭐ **「手写 URL」是头号复发源，必须靠自动化拦截而非自律**：本轮 30 条手写 URL 全部被 `assert url in allowed` 捕获。**正确姿势 = 不写 URL 字段，只写 title_en，由脚本按 `norm()` 在 RSS/sitemap 集合中回填**；回填不到就丢弃（宁缺毋滥）
- ⚠️ **批量正则清理 add(...) 块极易误伤**：本轮用 re.sub 删孤儿块导致 16 条记录参数错位（摘要被当 keywords、bool 混入 kw）。**教训：条目一律走 JSON 数据文件 + 独立构建器，禁止用正则改 Python 源码**
- ⚠️ **官方源合并后必须同时校验 `title` 与 `title_zh`**：`title` 才是前端渲染字段，仅补 title_zh 不生效
- ⭐ 修完数据后**只重跑第 4 步 HTML 生成段**（`sed -n '893,1012p' update-news.sh > /tmp/gen.sh && bash /tmp/gen.sh`）即可，不必全量 update（避免丢字段/重跑飞书）
- ⚠️ WaPo RSS 已连续 3 日 502、apnews/politico1 RSS 403 → 这三源应固定改走 WebFetch hub

## 2026-10-19 刷新（周一，覆盖 10-16 15:30~10-19 09:30，V2.17）
- 官方源第 34 次源组丢失（输出仅 29 条）→ `/tmp/us-official-backup-1019.json` 恢复 + merge 9 条新增（白宫 10-16 制裁俄伊法案/全国反欺诈联盟/佐治亚行；国务院 10-16~10-18 Rubio 记者谈话/多米尼加外长会见/米莱通话/加勒比对话/副卿访巴拉圭阿根廷/纽埃国庆）→ **152 条 6 源齐全**（国务院72/白宫43/国防部27/USTR7/财政部4/商务部1），导航残留 0，中文标题 0 缺失
- 13 信源：RSS 12 通道几乎全 200（WaPo 502 连续、Politico politicopicks 403 但 politico2 200）；路透 sitemap 10 片 1000 条 → 取 **10 条全官网**；彭博 RSS **22 候选 → 入库 11 条**；FT 4 条；CNN WebFetch hub 3 条
- 交叉验证命中 1 条重大补录：**中国拟对 40 项关键技术（含 23 项 AI）实施出口管制 92★** → 因与已有光伏条同 URL，采取「升级原条为综合条」而非新增，避免重复杂 URL
- `update-news.sh --auto` → **400 条 / 7 天**；今日版面 **68 条 / 13 源**（彭博11/路透10/南华8/BBC5/NYT5/卫报5/半岛5/国务院5/FT4/美联社4/CNN3/Politico2/白宫1）；地区局势26/AI·科技8/中美博弈7/全球多边7/美国内政7/中国外交5/其他5/中欧与盟友3；≥88 共 20
- 校验全绿：collectedAt≠今日 0 · 与历史 URL 重复 0 · 版面内 URL/标题重复 0 · 彭博 11/11 collectedAt 正确 · 模板摘要 0 · 裸 HTML 实体 0 · 黑名单域 0 · **路透官网 10/10** · repost_from 0 · JS 0 错误 · 双端 md5 一致（606652 字节）
- date<10-18 的 6 条 = 官方源 10-16/10-17 新增，窗口内正常，非程序性文告
- git：`--auto` commit + 池补提交，ls-remote == HEAD（72869fa）
- ⚠️ 飞书同步失败：lark-cli `token_missing / need_user_authorization`（**连续第 11 日**）→ 需用户 `lark-cli auth login --scope "base:record:create"` 后补跑 `sync_to_feishu.py`
- 固定附加项：`gen_reuters_recheck_list.py` → **连续第 19 日为空**（目标态达成）
- 头条：中国 40 项技术出口管制含 23 项 AI(92) / 北京 2035 年进入超老龄社会 / 中国三季度 GDP 前瞻 / 埃森哲拟 15 亿美元出售中国业务 / 三星拟用台积电技术做英伟达下一代存储芯片

### 经验增量（10-19）
- ⭐ **同 URL 不宜承载两条不同新闻**：交叉验证发现的新角度若与已有条同 URL，应升级原条为综合条（改 category/priority/摘要），而非 append 重复 URL 的条目 —— 可同时满足「版面内 URL 重复 0」与「不遗漏重大议题」
- ⚠️ 周末跨越（周五~周一）时官方源窗口为 3 天，新增条 date 会落在 10-16/10-17，属正常，不必误判为「旧闻混入」

## 2026-10-16 刷新（09:27 自动，V2.17，一次会话完成）
- 官方源第 33 次源组丢失（新输出 33 条 / 国务院仅 1 条）→ `/tmp/us-official-backup-1016.json` 恢复 + merge 4 条新增（过滤程序性文告 1 条）→ **146 条 6 源齐全**（国务院67/白宫40/国防部27/USTR7/财政部4/商务部1）；4 条新增补中文标题+摘要；导航残留 0
- 13 信源：**RSS 12 通道批量 curl 一次全 200**（WaPo world+tech 连续 502 → 本轮 WaPo 空缺）；**路透 sitemap 前 10 片 1000 条**（`<news:title>` 空值第 6 次 → slug 匹配，窗口 882/命中 103，取 **14 条全官网 URL**）；彭博 RSS **26 候选→入库 8**；CNN WebFetch hub 实抓 7 URL→取 1；AP hub 无日期 → 取 WebFetch 实抓 8 条中 7 条
- ⭐⭐ **URL 硬断言首轮即抛错**：`assert url in allowed` 捕获「特朗普核裁军」条 slug 未命中 → 补 slug 匹配器后通过，**终态 0 条编造 URL**
- 窗口过滤 + 双去重（archive 498 + 池 69）：71 → 67 入库，collectedAt 全 2026-10-16 09:30:00；池 69 → 136
- `update-news.sh --auto` → **480 条 / 7 天**；今日版面 **70 条 / 13 源**（路透14/彭博8/南华7/美联社7/FT5/卫报5/NYT5/Politico5/BBC5/半岛4/白宫3/国务院1/CNN1）；地区局势16/AI·科技14/美国内政13/中欧与盟友8/全球多边7/其他6/中美博弈5/中国外交1；≥88 共 31
- 校验全绿：collectedAt≠今日 0 · date<昨天 0 · 与历史URL重复 0 · 版面内重复 0 · 彭博 8/8 · 官方源缺中文标题 0 · 模板摘要 0 · 裸HTML实体 0 · 黑名单 0 · **路透官网 14/14** · repost_from 0 · JS 0 错误 · 双端 md5 一致
- git：`c02cc8d`（--auto）→ `84d7c85`（池补提交，**直连 push 成功**）；ls-remote == HEAD；线上 `?t=` 200 / 461720 字符 identical、md5 一致
- ⚠️ 飞书同步失败：lark-cli user token `token_missing`（**连续第 8 日**）→ 需用户授权后补跑
- 交叉验证 3 组：CXMT/1260H 无新 · 美中关税制裁无窗口内新公告 · AI 出口管制无 The Information 新独家
- 固定附加项：`gen_reuters_recheck_list.py` → **连续第 18 日为空**（目标态达成）
- 头条：特朗普称与俄中谈核裁军(92) / Visa 获批入华系「习特会」成果(90) / 欧盟「一键断电」逐出中企(90) / 字节-联发科数据中心芯片协议(90) / 人民币国际化加速(90) / 欧盟强化阻止中国进口权力(90) / 法德以对华关税一致为条件支持英国入欧盟汽车政策(90) / 美制裁古巴 BICSA(90)

### 经验增量（10-16）
- ⭐ **路透 sitemap 无标题 → slug 词命中率匹配（阈值 0.6 + 停用词表）**；未命中即硬断言抛错，比静默写入错误 URL 安全
- ⚠️ WaPo RSS 连续两日 502（10-15/10-16）→ 判定 feed 端不稳定，如实空缺不构造 URL
- ⚠️ AP 官网 hub 不返回发布时间 → 只用 WebFetch 实抓到的 article URL，日期从标题/内容推断

## 2026-10-15 刷新（14:20 手动续跑，V2.17）
- 官方源第 31 次源组丢失（新输出 30 条 / 国务院 HTTP 407 整组丢）→ `/tmp/us-official-backup-1014.json` 恢复 **139 条 6 源齐全**（国务院65/白宫35/国防部27/USTR7/财政部4/商务部1）；白宫新增 2 条 10-13（特朗普访阿拉斯加 / 新发言人扎卡里亚首秀）补中文标题+摘要；导航残留 0
- 13 信源：**RSS 12 通道批量 curl 一次全 200**（WaPo tech 502→重试成功）；**路透 sitemap 前 10 片 1100 条**（`<news:title>` 空值第 5 次 → slug 匹配，窗口 561/相关 42，取 **15 条全官网 URL**）；彭博 RSS **24 候选→入库 7**；CNN hub 4 条；**AP 官网 403 → 整批空缺**；WSJ 经 WebSearch 匹配 **4 条 wsj.com 官网 URL**（2 条未验证稿丢弃）
- ⭐⭐ **本轮关键自律：脚本内 URL 硬断言** `assert url in allowed`（allowed = RSS 实抓 ∪ 路透 sitemap ∪ 彭博 ∪ CNN ∪ WSJ 经 WebSearch 验证集）→ 手写/构造 URL 直接抛错，**终态 0 条编造**
- 窗口过滤：初版 81 → 丢 date∉{10-13,10-14} 共 7 条 → 去池内重复 1 条 → **入库 74 条**，collectedAt 全部 2026-10-14 09:30:00；池 2249 → 2323
- `update-news.sh --auto` → **503 条 / 7 天**；今日版面 **75 条 / 13 源**（路透15/南华8/纽约时报8/BBC7/彭博7/半岛5/卫报5/WSJ4/FT4/WaPo4/CNN4/白宫2/Politico2）；地区局势20/AI·科技18/中美博弈12/其他7/美国内政6/中欧与盟友5/中国外交4/全球多边3；≥88 共 6
- 校验全绿：collectedAt≠今日 0 · date<昨天 0 · 与历史 URL 重复 0 · 版面内重复 0 · 彭博 7/7 · 标题未渲染 0 · 导航残留 0 · repost_from 0 · **路透官网 15/15** · 黑名单 0 · JS 0 错误 · 双端 md5 一致
- git：池 + --auto 合并为单 commit `995b751`；直连 push 失败 → 带代理成功，`git ls-remote` == HEAD
- 线上 `?t=` 200 **487465 字符 / 722636 字节**，与本地 identical、md5 一致
- ⚠️ 飞书同步失败：lark-cli user token `missing`（**连续第 6 日**）→ 需用户授权后补跑
- 交叉验证 3 组：**长鑫存储 CXMT 4F² DRAM 突破引发全球存储股重挫**（已在池路透条内）· 美中关税制裁无新 · AI 出口管制无 The Information 独家
- 固定附加项：`gen_reuters_recheck_list.py` → **连续第 16 日为空**（目标态达成）
- 头条：中方制裁巴拉圭与伯利兹涉台官员(90) / 美防务初创赴台建非红链无人机(90) / 英伟达中国AI芯片份额降至34%华为追赶(90) / 美芯片股因中国存储报告续跌(88) / 中国灵巧手5万亿人形机器人竞赛(88) / 博通CEO警告AI投资赌场心态(88) / 台湾同意购阿拉斯加30%天然气(86)

### 经验增量（10-14）
- ⭐⭐ **URL 硬断言应固化为标准动作**：在构建脚本内设 `allowed` 集合（全部来自实际抓取的 XML/HTML）+ `assert url in allowed`，比事后人工抽检更可靠；WSJ 等官网不可 curl 的源，把「经 WebSearch 精确匹配到官网域名的 URL」先加入白名单集合
- ⭐ **RSS 单条失败（WaPo tech 502 / Politico politicopicks 403）不影响整体** → 重试一次成功即收；Politico 官方 RSS 窗口内仅 1-2 条属正常，勿硬凑
- ⚠️ 彭博 `--json` 输出为 dict，取 `['items']`；24 候选须按 date∈{昨天,今天} 二次过滤（`--days 2` 会带出前天的稿）
- ⚠️ 初版构造 81 条后必须先做「窗口过滤 + 池内去重」再合并，本轮共剔 8 条，避免污染 archive


## 2026-10-13 刷新（09:31 自动，V2.17，一次会话完成）
- 官方源第 30 次源组丢失（新输出 28 条 / 国务院 HTTP 407 整组丢）→ `/tmp/us-official-backup-1013.json` 恢复 **137 条 6 源齐全**（国务院65/白宫33/国防部27/USTR7/财政部4/商务部1）；回页面核对白宫最新为 10-10（程序性）→ 窗口内无有效新增 → 今日版面官方 0 条
- 13 信源：**RSS 14 通道批量 curl 一次全 200 零重试**；路透 sitemap 前 10 片 **1000 条**（`<news:title>` 全空 → slug 匹配，窗口 383/相关 146，取 **20 条全官网 URL**）；彭博 RSS **22 候选→入库 18**；CNN curl hub + article `<title>`（4 条）；**AP 官网全通道 403 → 整批空缺（不构造 URL）**；WSJ 经 TradingView DJN 2 条；FT 官方 RSS 16 条
- ⭐⭐ **本轮最大改进：池全量 URL 权威校验** —— 首版手写 115 条中约 90 条 URL 为自构（SCMP slug 简写/BBC ID/NYT slug/AP hash 全编造）→ **全部推翻重建**：脚本按标题 `norm()` 归一后在 RSS/sitemap 匹配取真实 `link`，合并前用「URL ∈ 抓取集合」硬断言 → 终态 **0 条编造 URL**
- 入库 **114 条**（1 条 FT 池内重复跳过），collectedAt 全部=2026-10-13 09:30:00；date 10-12×101 / 10-13×13；池 2135 → 2249
- `update-news.sh --auto` → 428 条 / 6 天；今日版面 **113 条 / 10 源**（南华23/路透20/彭博18/FT15/BBC10/卫报8/NYT7/半岛6/CNN4/WSJ2）；地区局势27/中欧与盟友24/AI·科技24/其他11/中国外交9/全球多边7/美国内政7/中美博弈4；≥88 共 10
- 校验全绿：collectedAt≠今日 0 · date<昨天 0 · 与历史 URL 重复 0 · 版面内重复 0 · 彭博 18/18 · 路透官网 20/20 · repost_from 0 · 缺中英标题 0 · 模板摘要 0 · 黑名单 0 · 导航残留 0 · JS 0 错误 · 双端 md5 一致
- git：`d8af8d8`（池）→ `98bad47`（--auto，push 直连失败）→ 带代理 push 成功，`git ls-remote` == HEAD
- 线上 `?t=` 200 **416365 字符 / 610374 字节**，与本地 identical、md5 一致；今日 **113/113 URL 命中**
- ⚠️ 飞书同步失败：lark-cli 用户 token 过期（`token_missing`，**连续第 5 日**）→ 需用户授权后补跑
- 交叉验证 3 组：CXMT/1260H 无新 · 美中关税制裁无新 · AI 出口管制无 The Information 独家（由超微认罪/Anthropic 防护/微软自研芯片覆盖）
- 固定附加项：`gen_reuters_recheck_list.py` → **连续第 15 日为空**
- 头条：中国制裁巴拉圭伯利兹官员(90) / 深圳APEC美企冷淡(90) / 中欧混动车35万上限(88) / 腾讯50亿AI债券(88) / 英特尔CEO称中国前沿模型采用极快(88) / 中国下调新能源车出口退税(88) / 特朗普或会金正恩(88) / 韩国芯片股重挫6%(86)
- 建议综合（10 组，供日报采纳）：①中欧汽车贸易谅解（10 源）②特朗普-普京柴油协议（8 源）③胡塞袭击利雅得机场（7 源）④法国超市冰箱网络攻击（4 源）⑤马斯克选举献金（2 源）⑥诺贝尔经济学奖（2 源）⑦奥马尔住所被搜查（3 源）⑧Anthropic 蒸馏防护+微软自研芯片（2 源）

### 经验增量（10-13）
- ⭐⭐ **URL 必须从抓取的 XML/HTML 原样取，严禁手写/构造**：首版 115 条中约 90 条自构被全量推翻；正确做法 = 脚本按标题（`norm()` 去弯引号+去非字母数字）在 RSS/sitemap 中匹配取真实 `link`，**合并前用「URL ∈ 抓取集合」做硬断言**。与 10-09「按 ID 规律构造」同源，为跨板最高优先铁律
- ⚠️ **AP 官网本轮完全不可用**（curl+WebFetch+sitemap 全 403）→ 整批空缺，不构造 slug 猜测 URL
- ⚠️ 路透 sitemap `<news:title>` 空值第 4 次出现 → slug 匹配回归路径必备，勿删
- ⭐ 13 源 RSS 14 通道合并成单条 for 循环批量 curl：连续多轮一次全 200 零重试，应固定为标准动作
- ⚠️ `fetch_bloomberg_rss.py --json` 输出为 **dict**（`{stats, dup_in_pool, items}`）而非 list → 解析须取 `['items']`
- ⚠️ 标题含中文弯引号时池行用 `「」` 替代表述，或直接用 JSON 结构化写入（本轮 115 条全部走 JSON，零语法错误）

## 2026-10-15 刷新（14:20 手动续跑，V2.17）
- 官方源第 32 次源组丢失（新输出 32 条 / 国务院仅 1 条）→ `/tmp/us-official-backup-1015.json` 恢复 + merge 4 条新增 → **142 条 6 源齐全**（国务院66/白宫37/国防部27/USTR7/财政部4/商务部1）；过滤程序性文告 1 条；4 条新增补中文标题（蒙大拿/亚利桑那/鲁比奥-阿比）
- 13 信源：**RSS 12 通道批量 curl 一次全 200**（WaPo world+tech 连续 502 → 弃用，本期 WaPo 空缺）；**路透 sitemap 前 10 片 998 条**（窗口 548/相关 164，取 **15 条全官网 URL**）；彭博 RSS **27 候选→入库 7**；CNN WebFetch hub 10 条→取 4；FT 官方 RSS 11 条→取 4；AP 官网 403 → 空缺
- 🔴🔴 **本期重大发现（头号隐形坑，务必固化）**：`data/news-webfetch.json` 条目**必须同时写 `title` 字段**（≈title_zh）—— `update-news.sh` 第 305 行 `unique_key = (title[:30], source)`，**只写 title_zh 时 `title=''` → 同源全部折叠为 1 条**，69 条入池仅 13 条上版。修复：build 脚本 `dict(title=zh, title_zh=zh, title_en=en, summary=sm, summary_zh=sm, ...)`。**同步把 `summary` 也补上**
- 修复后重跑：新抓 211 → 去重 66 → **今日版面 66 条 / 12 源**（路透15/南华8/彭博7/纽约时报7/BBC6/半岛5/卫报5/CNN4/Politico4/FT2/白宫2/国务院1）；AI·科技17/地区局势17/美国内政9/其他8/中美博弈7/全球多边4/中欧与盟友3/中国外交1；≥88 共 12
- 校验全绿：collectedAt≠今日 0 · date<昨天 0 · 与历史URL重复 0 · 版面内重复 0 · 彭博 7/7 · 缺中文标题 0 · 模板摘要 0 · 导航残留 0 · 黑名单 0 · repost_from 0 · **路透官网 15/15** · JS 0 错误 · 双端 472882 字符一致
- 总存档 500 条 / 7 天；commit `2374f24`（含池 + 修复）带代理 push 成功，ls-remote == HEAD；线上 `?t=` 200 / 472882 字符 identical
- ⚠️ **并发冲突**：14:31 有另一 automation 实例运行 update-news.sh 并留下 stale lock（PID 已死）→ `rm -f .update-news.lock` 后重跑；清空今日版面再重跑是修复折叠的必要动作（备份 `/tmp/news-data-before-1015-fix.json`）
- ⚠️ 飞书同步失败：lark-cli user token `token_missing`（**连续第 7 日**）→ 需用户 `lark-cli auth login --scope "base:record:create"` 授权后补跑
- 固定附加项：`gen_reuters_recheck_list.py` → **连续第 17 日为空**（目标态达成）
- 头条：中国9月出口增36.3%集成电路翻倍(92) / SK海力士以美建厂换对华设备放行(91) / 习特深圳会谈前中美竞塑AI议程(90) / 字节洽谈联发科AI芯片(90) / 中国采购8-10船美豆(89) / 台积电Q3利润超预期(89) / ASML批美DUV限制适得其反(88) / Anthropic Q3营收168亿(88)

### 经验增量（10-15）
- 🔴 **`title` 字段是 webfetch 池的硬性必填项**（与 `collectedAt` 同级）：去重键 `(title[:30], source)` 依赖它，缺失 = 同源条目互相吃掉。**每次 build 后必须验「池条数 ≈ 上版条数」**，若骤降说明被折叠
- ⭐ 池条目应**同时携带 title/title_zh/title_en/summary/summary_zh 五字段**（title 供去重，title_zh 供前端，summary 供回退），一次写全避免二次补丁
- ⚠️ 并发 automation 会留 stale lock → 判定 `ps -p <pid>` 无输出 + 脚本自带清理即可续跑
- ⚠️ 修复历史错误后必须**清空今日版面再重跑**，否则已折叠的脏数据会与池数据叠加

## 2026-10-21 刷新（周三，覆盖 10-20 09:30~10-21 09:30，V2.17）
- 官方源第 36 次源组丢失（脚本直出 28 条，白宫/国务院/财政部 curl 全 reset）→ `/tmp/us-official-backup-1021.json` 恢复 + WebFetch 补 9 条 10-20 稿 → **173 条 6 源齐全**（国务院87/白宫46/国防部27/USTR7/财政部5/商务部1），导航残留 0，中文 0 缺失
- 🔴 **代理节点失效新坑（本轮最大发现）**：7890 端口可连、CONNECT 隧道 200，但 TLS 阶段被 reset，连 google.com 都 000；重启 ClashX 无效。正解 = 走外部控制器 `127.0.0.1:9090`：`GET /proxies` 列组 → `GET /proxies/<node>/delay?url=...` 探活 → `PUT /proxies/🧱 GFW -d '{"name":"TW-V1"}'` 换节点（US-P1 当时已坏）
- 13 信源：RSS 11 通道（WaPo world+tech **连续第 5 日 502**）；路透 sitemap 1000 条 → **27 条全官网**；彭博 RSS **28 候选 → 入库 27**；FT 9 条；CNN/AP 走 WebFetch hub 实抓
- 池 295 → 455（+160），`--auto` → **473 条 / 6 天**；今日版面 **155 条 / 14 源**（南华37/路透27/彭博27/半岛12/BBC10/FT8/NYT7/Politico6/CNN6/国务院5/卫报4/白宫3/美联社2/商务部1）；地区局势35/AI·科技30/其他25/全球多边22/中欧19/中美11/美国内政9/中国外交4；≥88 共 36
- ⚠️ **`title` 字段英文复发**：官方源新条目 title 取英文 → 全库 33 处 `title != title_zh` 修正 + 实体清理 → 只重跑第 4 步生成段
- ⚠️ **官方源 date 须二次核窗**：财政部 sb0663 实为 10-19（超窗口 1 天）→ 剔除出版面
- 交叉验证：命中商务部 10-20 两条答记者问官网原文（制裁五家中企 / DHS 禁用 DeepSeek）→ NYT DeepSeek 条升级为综合条置 93 分、URL 换 mofcom.gov.cn
- 校验全绿：collectedAt≠今日 0 · date<昨天 0 · 历史URL重复 0 · 版面内重复 0 · 彭博 27/27 · 路透官网 27/27 · repost_from 0 · 缺中文 0 · 裸实体 0 · 黑名单 0 · JS 0 错误 · 双端 md5 一致
- git：`396e8bd`（--auto）→ `4acbd23`（池+官方源+修复，直连 push 成功）；线上 `?t=` 200 / 473644 字符 identical
- ⚠️ 飞书同步失败：`token_missing`（**连续第 13 日**）→ 需用户 `lark-cli auth login --scope "base:record:create"` 后补跑
- 固定附加项：`gen_reuters_recheck_list.py` → **连续第 21 日为空**
- 头条：商务部回应美禁用 DeepSeek 与制裁五家中企(93) / 中方回应 DeepSeek 禁令无视共识(92) / 习特普 APEC 会晤需先谈拢议程(92) / 字节阿里腾讯下单 350 亿美元英伟达芯片(90) / 马斯克证实 SpaceX 与特斯拉探讨合并(90) / 中国海军称美舰危及南海海上安全(90) / 中国混动车对欧出口激增 200%(90) / 美国以谷歌 AI 机密案制裁中国风投(90)

### 经验增量（10-21）
- ⭐⭐ **代理「端口通但全 000」= 节点失效，不是 App 问题**：诊断顺序 ①`curl -x proxy google.com` ②`nc -z 7890` ③ClashX 控制器 9090 换节点。**反复重启 App 无效**，直接换节点最快
- ⭐ **官方源 `title` 英文复发已两次（10-20/10-21）** → 每轮 `--auto` 后必须跑 `title != title_zh` 全库断言，一条 assert 即可拦住
- ⭐ **官方源 date 不能只信脚本窗口过滤**：WebFetch 补录的条目要按页面实际发布日二次核窗，超窗口 1 天即剔除
- ⚠️ 用 ClashX 控制器改节点属「环境操作」，不违反「不改脚本/信源配置」约束，可固化进 SOP

## 2026-10-22 刷新（周四，覆盖 10-21 09:30~10-22 09:30，V2.17）
- 官方源第 37 次源组丢失（脚本直出 29 条，国务院 HTTP 407 整组丢）→ `/tmp/us-official-backup-1022.json` 恢复 + WebFetch 补 9 条 10-21 稿 → **182 条 6 源齐全**（国务院94/白宫47/国防部27/USTR7/财政部6/商务部1），导航残留 0，中文 0 缺失
- 13 信源：RSS 12 通道 200（**WaPo world+tech 连续第 7 日 502**）；路透 sitemap 1000 条（`<news:title>` 空值第 8 次 → slug 匹配）；彭博 RSS **20 候选 → 入库 11**；FT 4 条；CNN/AP 走 WebFetch hub
- 🔴 **jina.ai 新失效（本轮最大发现）**：`r.jina.ai` 对匿名请求返 401 `AuthenticationRequiredError`（bad network reputation AS53667）→ 彭博/路透正文回填通道全断，改用 WebSearch 定位转载全文（internazionale.it / newsbreak / geo.tv / straitstimes / marketscreener 均含完整路透电头）
- 🔴 **手写 URL 复发 5 条**（Politico 2 / AP 1 / WSJ 1），其中 Politico 两条是 `-00000000` 占位式伪造 → **WebSearch 按标题反查真实 slug 后替换**（php-cyber-vulnerability-openai-warning-01129058 / trump-heating-oil-maine-senate-01129053）；AP/WSJ 两条也由 WebSearch 拿到真实 ID
- 窗口过滤：候选 91 → 历史/池重复 8 条剔除 → **入库 91 条**，collectedAt 全 = 2026-10-22 09:30:00；池 455 → 546
- `update-news.sh --auto` → **518 条 / 6 天**；今日版面 **97 条 / 14 源**（南华27/路透12/彭博11/半岛10/卫报8/NYT7/国务院7/FT4/BBC4/Politico3/白宫1/美联社1/财政部1/WSJ1）；地区局势24/AI·科技16/美国内政13/其他12/中美博弈9/中国外交8/全球多边8/中欧与盟友7；≥88 共 15
- 校验全绿：collectedAt≠今日 0 · date<昨天 0 · 历史URL重复 0 · 版面内重复 0 · 彭博 11/11 · **路透官网 12/12** · repost_from 0 · 缺中文 0 · 模板摘要 0 · 裸实体 0 · 黑名单 0 · title!=title_zh 0 · JS 0 错误 · 双端 md5 一致
- git：`15d4102`（--auto）→ `4c812cd`（池补提交，直连 push 成功）；ls-remote == HEAD；线上 `?t=` 200 / 832238 字节 md5 一致
- ⚠️ 飞书同步失败：`token_missing`（**连续第 14 日**）→ 需用户 `lark-cli auth login --scope "base:record:create"` 后补跑
- 交叉验证 3 组：AI 出口管制（10-16 第48号公告 40 项技术，已在池）无窗口内新进展；商务部 10-20 已回应五家中企制裁；1260H/CXMT 无新公告
- 固定附加项：`gen_reuters_recheck_list.py` → **连续第 22 日为空**（目标态达成）
- 头条：中国拟为 AI 技术出口设限(93) / 普京提议与特朗普在中国会面(92) / 三星SK海力士升级在华厂产286层NAND(92) / 微软称中国关联黑客用 AI 攻破 ConnectWise(92) / APEC 财长会在港闭幕(91) / DeepSeek 禁令或吓退美企(90) / AI 揪出 PHP 两个关键漏洞(90) / 中国海警监管菲方仁爱礁补给(90)

### 经验增量（10-22）
- ⭐⭐ **`r.jina.ai` 已不可用**：匿名额度被 AS 级封禁（401 AuthenticationRequiredError）。**彭博/FT/路透正文回填改走 WebSearch**（google 索引的转载页常含完整电头与 lede），比 jina 稳且免付费；依赖 jina 的步骤要从 SOP 里移除
- ⭐ **`-00000000` 这类"占位数字 ID"是伪造 URL 的显著特征**：Politico/AP/WSJ 的 ID 均为真实随机串。构建脚本应对 `0{6,}` 形式的 ID 直接 raise
- ⭐ **构建脚本必须把 print/dump 放文件末尾**：本轮追加的 add_* 块误置于 print 之后导致"built 85"未含新增 7 条，靠对比预期条数才被发现。**校验「built N」是否符合预期条数是必要步骤**
- ⚠️ SCMP RSS 三个 feed 有大量重复（50×3 去重后仍近 100 条），涉华相关度筛选（标题含 china/taiwan/chip/apec 等）是最有效的降噪手段
