# 自动化执行记忆：国际新闻看板每日刷新

## 2026-09-08 执行摘要（09:23 开始，一次会话完成）
- 官方源：源组丢失第 13 次复发（新输出仅 29 条：白宫1/国防部21/财政部3/商务部1/USTR3/国务院0）→ /tmp/us-official-backup-0908.json 恢复 89 条 6 源齐全（白宫22/国务院33/国防部27/财政部3/商务部1/USTR3）；唯一候选白宫 Labor Day 2026 文告(09-07) 程序性假日文告按 San Marino/Eswatini 先例剔除；美东 Labor Day 联邦假日政府不发文，窗口内官方新增=0 合理；war.gov(最新09-03)/商务部(G20 09-02)/USTR(08-13) WebFetch 确认窗口内 0 新
- WebFetch 11 源：RSS 兜底（Guardian/AJ/NYT/BBC/SCMP 本地代理全 200；CNN RSS 第 3 次返回 2023 缓存旧稿→弃用改 WebFetch edition.cnn.com/world）；AP WebFetch 无涉华头条空缺；反爬四家 fetch_paywall_sources.py 候选 + WebSearch 定位转载
- 收录 20 条全部 date∈{09-07,09-08}：SCMP 8（Xi 峰会前外交攻势88★summit 含 SCO/埃及/金砖行程/日二氯硅烷反倾销86/王毅墨西哥第三方84/台美国支持网军82/东京防务台湾80/华为三折叠Tau麒麟79/中俄雪龙2号北极78/小米18 Fold76）、路透 5 转载均验证 200 带 repost_from（台芯片外交86 TheEdge/中国AI四小龙英伟达85 FinancialExpress/储能暂停84 HinduBusinessLine/人形机器人82 印度经济时报/大豆82 YahooFinance）、Asia Times 补录 Aivres 漏洞 90★summit、NYT 秘鲁反华极限85、卫报 美加关税82+俄朝桥78、BBC Arm 芯片短缺76、AJ 鲁比奥拉美78、CNN 伊朗封锁76；webfetch 940→960
- 交叉验证 3 组命中重大遗漏：NYT 9-06 Aivres/Inspur 调查（浪潮加州子公司规避实体清单出口 $5.6B 含 $3B Blackwell，服务字节/阿里）昨日漏抓且 date=09-06 出窗口 → 改收 Asia Times 09-08 跟进稿（含 RASA/云漏洞/9-24 Xi 白宫行/峰会 AI 芯片议题），date 窗口内合规；NYT 原文 URL 反爬无法验证宁缺毋滥
- update-news.sh --auto 成功：242 条/8 天/今日 20/三零全绿（collectedAt≠今日0·date<昨天0·URL重复0）/JS 0 错误/HTML 双端一致 337244B/嵌入 NEWS_DATA 一致
- git：主 commit 93d3f2a push 首失败（瞬时）重试见 up-to-date → ls-remote 核对已被国内 c82fcb6 连带推达；补提交 pool 38ae21a（webfetch+20/官方报告）、脚本 12e5a65（sync 映射修复）；远程 main=12e5a65 一致
- 飞书三修：①source 字段 field-update 补 Asia Times/The Information/华盛顿审查者报/韩国中央日报 → 27 选项（full PUT 需先 field-get 拿全定义）②CATEGORY_MAPPING 补 "中欧关系"→地区动态（sync_to_feishu.py 加一行）③--today 仅同步 date==today 1 条，19 条 date=09-07 首次入池会漏 → 补跑全量同步 170 条（8 天窗口存档补齐）；线上 ?t= HTTP 200 337244B lastUpdated 09:31 今日全在线
## 经验增量
- CNN RSS 端点已多次返回 2023 缓存旧稿 → 固化：CNN 直接走 WebFetch edition.cnn.com/world，勿再 curl 其 RSS
- Asia Times 官网 URL 代理 curl -L 可 200（301→带斜杠 URL），datePublished UTC 需注意（09-07T22:38Z=北京 09-08 06:38，页面显示 9-8）
- NYT 重大调查常在 technology/business 频道而非 world → 交叉验证组 c 之外，重大 AI 芯片调查可加搜 "nytimes investigation AI chips China" 线索
- 飞书补充源条目（The Information/Asia Times/Washington Examiner/韩中央日报）同步必报 800030005 → source 选项与 CATEGORY_MAPPING 需随收录节奏维护；全量 sync 是 8 天窗口补档的正规手段（--today 会漏 date≠today 首次入池条目）


## 2026-09-04 执行摘要
- 官方源：白宫/国务院源组再次丢失（第 9 次复发）→ 备份(80)恢复 + merge 国务院 5 新增 - 剔 San Marino 程序性贺电 → 84 条 6 源齐全（白宫19/国务院31/国防部27/财政部3/商务部1/USTR3）；窗口内国务院 4 条（古巴制裁×2、Foundry School×2）全补 title_zh，预检 0 缺
- 反爬站点：war.gov 今日无窗口内涉华稿如实空缺；商务部 G20 创新声明 date=09-02 出窗口不收；USTR 无新
- WebFetch 11 源大面积 fetch failed → RSS 兜底 5 源(BBC/Guardian/AJ/NYT/CNN) + SCMP RSC headline + GN RSS + WebSearch 定位转载 → 22 条入池（webfetch 842→864）；覆盖 10/11 源 + 官方源；临时构造的 Reuters Anthropic URL 已自查移除（无编造）
- 转载收录：月之暗面IPO(YahooF)/汽车禁令(DetroitNews)/中国军舰日本(HindustanTimes)/台湾防务预算(Yahoo)/字节内蒙古DC(ChosunBiz)，均带 repost_from
- update-news.sh --auto 成功：309 条/8 天/今日 26/push 74ae831/Pages built；补提交 pool dee9d24 推达远程一致；线上 ?t= 200 首条=月之暗面IPO
- 三零校验全绿：collectedAt≠今日 0 / date<昨日 0 / URL 重复 0；高优(≥88) 11 条无文告水稿；JS 0 错误
- 交叉验证 3 组无新遗漏；飞书同步 0 条（今日条目 date=09-03，date==today 过滤为空，属正常）

## 经验固化
- 白宫/国务院源组丢失已第 9 次复发 → 备份恢复是标准流程（cp 到 /tmp + merge URL 去重）
- WebFetch 大面积失败时 RSS 兜底（BBC/Guardian/AJ/NYT/CNN 端点全 200，代理 curl 直接可用）
- SCMP 3.3MB RSC 流 URL 转义存储难解析 → 用 GN RSS(标题线索) + WebSearch "scmp.com+关键词" 定位官网 URL
- 构造/猜测 URL 违反纪律 → 写入后必须自查（今日 1 条临时构造 Reuters URL 已移除，宁缺毋滥）
- 转载 URL 用知名平台：Yahoo Finance/News、Hindustan Times、Detroit News、ChosunBiz 均验证可达；低质聚合站禁用
- 飞书 --today 按 date==today 过滤；若版面全是 date=昨日(09-03) 则同步为空属正常（09-03 已定向同步过）

## 2026-09-04 下午增量：URL 替换 + 同事补录
- 用户手动找到 2 条路透官网原文 URL（月之暗面 IPO / 美车企禁令），已替换 webfetch+news-data 双端并移除 repost_from；教训：路透转载定位优先再试一轮"GN RSS site:reuters.com + 关键词"从 khanlist/转载页内链反查原链
- 同事补录 4 条（Greer 农业表态/美伊双轨不愿动中国/万斯称中方愿意配合/G20 人民币不贬值），全部 date=09-03 在窗口内，今日版面 26→30，commit 65d2e03，线上验证通过
- 漏抓根因：①官员媒体访谈不在官网 release 页 ②中国角度藏在伊朗长文正文、标题级关键词漏 ③Washington Examiner 非必选源 ④SCMP 当日采集失败且 GN 兜底未覆盖 SCMP
- 后续刷新建议：交叉验证关键词组之外，对 USTR/白宫官员名字跑一轮 GN RSS（site:reuters.com OR site:scmp.com when:2d）；RSS 兜底固定加 GN RSS site:scmp.com when:2d

## 2026-09-05 执行摘要（首次运行 09-05，跨两次会话）
- 官方源：白宫/国务院源组第 10 次丢失（仅 33 条）→ 备份(84)恢复 + merge 今日新增 5 条（白宫 3 行政令/声明 + 国务院 2 制裁·鲁比奥拉美行，均 date=09-04）→ 89 条 6 源齐全（白宫22/国务院33/国防部27/财政部3/商务部1/USTR3）；5 条新增全补 title_zh+summary_zh+summary_en（白宫行政令内容经 WebFetch 核实：牧场主/牲畜市场两令为内政、伊朗制裁涉土耳其银行非涉华）
- 反爬站点 WebFetch：商务部(最新 G20 声明 09-02 出窗口)/USTR(无新)/war.gov(Contracts 等程序性) 三源如实空缺
- WebFetch 11 源：BBC/SCMP/Guardian/NYT/AJ fetch failed → 本地代理 127.0.0.1:7890 curl RSS 全通（此前无代理直 curl 全 HTTP 000）；Reuters/WSJ/WaPo/Politico 走 fetch_paywall_sources.py 候选 + WebSearch 定位转载（印度经济时报/Internazionale/Yahoo Finance/AOL/Unite.AI/腾讯新闻/Export Compliance Daily 等，全部验证 200 带 repost_from）
- **重大独家全收**：中美9月中旬AI安全对话(95★,贝森特率团)、习率大型CEO代表团访美(94★ summit)、稀土供应商暂停对美发货(92★)、字节296亿美元AI贷款、中资行购美债、Stellantis×华为×江淮洽玛莎拉蒂、OpenAI智能体劫持DseWiki、太平洋岛国论坛关切中国导弹试射
- **交叉验证命中 The Information 远程算力新规**（美国拟封堵中企远程调用泰国/新加坡AI算力，95★，关联月之暗面 Kimi K3）→ 腾讯新闻转载收录 + 鲁特尼克表态(90★,Export Compliance Daily) → 2 条补录
- 今日版面 46 条/六大栏目（中国5/美国22/地区热点11/国际会议3/欧洲3/其他2）13 信源（路透9/SCMP8/BBC4/卫报4/AJ4/CNN3/NYT3/白宫3/国务院2/WSJ2/AP2/The Information1/Politico1）
- update-news.sh --auto 成功：318 条/8 天/今日 46/push 806b668/线上 12:09 生效；补提交 pool eb680e0（webfetch +42→910、us-official 89、report）推达远程一致
- 三零校验全绿：collectedAt≠今日 0 / date<昨天 0 / URL 重复 0；官方条目字段完整 0 缺；HTML 嵌入 NEWS_DATA 与 news-data.json 一致；"Executive Orders" 仅现于白宫行政令条目原始 EN summary（文档标题本身，非导航残留）；data['today']/todayCount 为遗留陈旧字段（前端高亮用浏览器 TODAY_DATE 实时计算，无影响）
- 线上 ?t= 二次请求 HTTP 200：含 09-05 版面/稀土/AI安全对话/CEO代表团，lastUpdated 12:09

## 2026-09-05 经验增量
- 无代理直 curl RSS 全 000，带 http_proxy/https_proxy=127.0.0.1:7890 后全 200 → RSS 兜底必须走本地代理
- fetch_us_official.py 源组丢失（第 10 次）仍在复发 → 备份恢复流程已完全固化，当日新增 merge 后必须逐一补 title_zh/summary_zh 并复核 6 源计数
- Politico 官网 URL 可用 WebSearch 真实定位（勿构造）；构造 URL 已自查移除/替换

## 2026-09-06 执行摘要（12:39 开始，一次会话完成）
- 官方源：源组丢失第 11 次复发（fetch 输出仅 29 条，白宫 0/国务院 1）→ /tmp/us-official-backup-0906.json 恢复 89 条 6 源齐全（白宫22/国务院33/国防部27/财政部3/商务部1/USTR3）；窗口内(date∈09-05/09-06)新增=0 实质条目——美东周六政府不发文，白宫/国务院/财政部最新均为 09-04 已在池；唯一候选国务院 Eswatini National Day 贺电(09-06)为程序性内容按 San Marino 先例剔除；war.gov/商务部/USTR WebFetch 确认窗口内 0 新
- WebFetch 11 源再次大面积失败 → 本地代理 7890 curl RSS 兜底（BBC/Guardian/AJ/NYT/SCMP 全 200；CNN RSS 返回 2023 缓存旧稿弃用，改 WebFetch edition.cnn.com/world 成功）；反爬四家走 fetch_paywall_sources.py 候选 + WebSearch 定位（Politico 官网 URL、Reuters 走 Fidelity/Yahoo 转载均验证）
- 收录 16 条全部 date∈{09-05,09-06}：WaPo 白宫为 Xi 访美拆北门廊帷幔(88 summit)、Reuters OpenAI 维基事件承认(90)、SCMP 中加两军 8 年首谈(85)、Politico 加拿大关键矿产杠杆(84)、Reuters 富士康 Q3(82)、NYT 中国毕业生 AI(82)、BBC 普京会晤后赴基辅(82)、WSJ 中国 AI 社会成本(80)、AJ 德国 AfD 州选(80)、SCMP 台湾最危险(80)、SCMP Tesla Cybercab(78)、CNN/AP 美击伊朗油轮×2(76)、SCMP 铁尾矿(75)、卫报 欧洲消耗战(74)、BBC 灰狼令(70)；webfetch 910→926
- 交叉验证 3 组无窗口内新遗漏（长鑫 1260H 起诉 8-28 已收；The Information 远程算力 8 月底已收；无人机关税 9-3 生效出窗口无合格外媒新稿→如实空缺）
- update-news.sh --auto 成功：300 条/8 天/今日 16/三零全绿(collectedAt≠今日0·date<昨天0·URL重复0)/11 源全覆盖；飞书同步 5 条；JS 0 错误；HTML 双端一致(国际+gh-pages, 397160B)
- git：主 commit c05f6f6 与国内看板自动化 0c8c95a 并发交错（远程一致）；补提交 pool 5804fc0（webfetch+16/官方报告）；线上 ?t= HTTP 200 今日条目全在线

## 2026-09-07 执行摘要（09:23 开始，一次会话完成）
- 官方源：源组丢失第 12 次复发（新输出仅 29 条：白宫 0/国务院 1/国防部 21/财政部 3/商务部 1/USTR 3）→ /tmp/us-official-backup-0907.json 恢复 89 条 6 源齐全（白宫22/国务院33/国防部27/财政部3/商务部1/USTR3）；窗口内唯一候选国务院 Eswatini National Day 贺电(09-06) 按 San Marino 先例剔除（美东 Labor Day 长周末政府不发文，官方新增=0 合理）；war.gov(最新09-03)/商务部(G20 09-02 出窗口)/USTR(08-13) WebFetch 确认窗口内 0 新
- WebFetch 11 源大面积失败 → 本地代理 7890 curl RSS 兜底（BBC/Guardian/AJ/NYT/SCMP 全 200；pubDate 含 +0000/GMT 两种格式，解析必须宽松只取日期段）；CNN 走 WebFetch edition.cnn.com/world；反爬四家 fetch_paywall_sources.py 候选 + WebSearch 定位转载
- 收录 14 条全部 date∈{09-06,09-07}：路透 中国财政部540亿美元注资银行保险(90,TheEdgeMalaysia 转载)、路透 普京-特朗普-习三方会晤不排除/11月深圳APEC(88,印度经济时报转载)、卫报 欧盟30万岗位流失警告中国"殖民"供应链(85)、卫报 美军可及澳洲过半军事基地(82)、SCMP 穆迪中国AI每美元算力(86)/罗布泊基地扩建隐身战机(84)/中吉乌铁路隧道贯通(82)/军校AI"为战育人"(78)、BBC AfD东德州选44%(80)/伊朗威胁更快更重报复(76)、NYT AI开始谋划(76)、Politico 肯尼迪抨击AI开发者(72)、AJ 朝鲜部署军舰(74)、CNN 吉隆口岸洪灾(72)；BBC Zelensky 稿 URL 与昨日特使稿相同自动去重；webfetch 926→940
- 反爬空缺（如实）：WaPo Xi"稳定替代"外交攻势稿两次 WebSearch 无合格转载 URL→空缺（昨日已收 WaPo 白宫帷幔稿）；WSJ 三大航亏损无合格英文转载→空缺；美东周末涉华稿少符合宁缺毋滥
- 交叉验证 3 组无窗口内新遗漏（返回均为 1月 HR2683/8月稀土博弈旧闻解读）
- update-news.sh --auto 成功：260 条/8 天/今日 14/六大栏目（中国5/地区热点3/欧洲2/其他2/美国1/国际会议1）；三零全绿；官方字段 0 缺；HTML 双端一致 273818B；JS 0 错误；飞书同步 2 条（date==today 过滤，正常）
- git：主 commit ee16761 首次 push 网络失败（Failure when receiving data）→ 代理通后重试成功；补提交 pool 1894ad6（webfetch/官方报告）推达远程一致；线上 ?t= HTTP 200 首条=财政部注资 lastUpdated 09:32
## 经验增量
- git push 偶发 "Failure when receiving data from the peer" 属瞬时网络错误，代理连通时直接重试即可（勿反复开关代理）
- 本地与线上 HTML 文件用 python len() 实测一致（curl -w size_download 显示值含传输统计偏差，勿据此判断不一致）

## 2026-09-08 下午增量：路透官网 URL A 方案落地（用户拍板）
- 背景：用户发现最近路透全转载，追问为何拿不到原站链接。诊断：9-02 起 DataDome 域名级 JS 挑战（全路径含 sitemap/pf-API 恒 401、WebFetch fetch failed、无代理 000、robots.txt 200 例外）；8-01~9-01 的官网 URL 是 WebFetch 直抓时代产物；9-04/9-07 官网 URL 均系用户手动提供
- **方法论纠错：「401=页面存在」验证法无效**（DataDome 路由前拦截，不存在路径也 401）——已在 memory 声明勿再用
- A 方案（固化）：官网 URL 只定位不抓取，唯一可信来源 = 第三方可见背书（WebSearch 收录聚合页/转载页列出的 reuters.com 原文链接，slug 与标题逐字对应+日期吻合）或用户浏览器；禁构造 URL（Breakingviews 构造案例弃用）；转载页 canonical 带 tag:reuters.com newsml_XXX 可验真（非 URL）
- 首落成果：今日人形机器人稿 URL 印度经济时报 → reuters.com/world/china/dance-floor-war-china-readies-humanoid-robots-combat-2026-09-07/（经情报聚合页背书，其 SCMP URL 与 RSS 实测一致证明非编造）；commit 2171160 双端+HTML 重建+线上 ?t= 已验证 337187B
- 反查 SOP：候选标题 → WebSearch 精确标题/关键词变体（可加「原文链接」中文词命中外媒情报聚合页）→ 命中即换官网 URL 移除 repost_from → miss 落全文转载（AOL/印度经济时报/ET，正文可作摘要）

## 2026-09-08 晚增量：每日汇报固定附带项 = 路透转载「一键搜官网」清单（用户拍板执行）
- **每次刷新收尾汇报必须附带**：当日仍为转载的路透条目反查清单，含编号/中英标题/当前转载URL + Google 与 Bing 的 `"完整英文标题" site:reuters.com` 一键搜索链接
- 生成器：`python3 scripts/gen_reuters_recheck_list.py`（默认取 archive 最新版面日 dates[0]；勿依赖 data['today'] 字段——该字段仅 V2.6 护栏移动条目时更新，9-03 起陈旧，前端今日高亮用本地 TODAY_DATE 不消费它，无碍渲染但脚本默认值勿取它）
- 用户回报格式：「编号: reuters.com 官网URL」→ 收到后走 A 方案替换流程（双端换 url + pop repost_from + GENERATE_HTML_V12 段重建 + check_js/inject_nav + git push + 线上 ?t= 验证）
- 今日首落：4 条（芯片外交/AI四小龙/储能/大豆）已随汇报附清单

## 2026-09-09 刷新（09:23 自动，V2.15）
- 官方源：源组丢失第 14 次复发（新输出仅36条）→ 备份恢复 89 + merge 4 实质新增 + 剔除 4 程序性文告；防务/商务/USTR 窗口内 0 涉华
- 今日版面 32 条（28 webfetch + 4 官方），校验全 0；push e7603a4；Pages built；线上 ?t= 验证通过
- 头条：NSA/FBI/CISA AA26-251A 六家中国AI公司蒸馏公告（CISA官网URL source=NSA/FBI/CISA ★95）；华为案 9/8 布鲁克林开审（SCMP ★95）；中国8月出口+25%；北京注资3600亿；美加贸易战升级；习近平-伯纳姆首通话；董建华逝世
- 反爬源：路透2转载（HL/Euronext）WSJ1转载（Morningstar DJN全文）CNN1转载（KTEN）其余空缺；交叉验证无新遗漏

## 2026-09-10 刷新（09:23 自动，V2.15）
- 官方源：源组丢失第 15 次复发（新输出仅 34 条：白宫2/国务院4/国防部21/财政部3/商务部1/USTR3）→ /tmp/us-official-backup-0910.json 恢复 93 + merge 4 实质新增（国务院：美波40亿FMF贷款担保 / 制裁7名厄瓜多尔前官员 / Los Tiguerones FTO / OFAC制裁中文平台"新币担保"）→ 97 条 6 源齐全；剔除 2 条无新闻价值（Patriot Day 文告、白宫"两年政绩"PR稿）；4 条新增全补 title_zh+summary_zh
- ⚠️ **update-news.sh 崩溃（昨日 V1.6 升级引入）**：GENERATE_HTML_V12 段第 1002 行 `print(f"...栏目: {column_counts}")` 引用未定义变量 → NameError，因 `set -e` 导致 HTML 未生成、后续步骤全断。修复：`column_counts` → `category_counts`（纯笔误，非逻辑改动）→ 重跑成功。**教训：每日刷新前若脚本有前一日新提交，先跑一次确认 HTML 段无 NameError**
- WebFetch 11 源仍大面积 fetch failed → 本地代理 7890 curl RSS 兜底（BBC/Guardian/AJ/NYT 全 200；**SCMP /rss/4/feed 需 -L 跟随 301 才 200**，3 个频道各 50 条；WSJ RSS 返回 2025-01 缓存旧稿→弃用）；CNN/AP 走 WebFetch（edition.cnn.com/world、apnews.com/world-news）成功
- 收录 32 条全部 date∈{09-09,09-10}：SCMP 15（农产品采购92★summit/无人机禁令84/台海155mm 84/高超音速84/南海斥菲82/特金会82/西伯利亚力量2号82/日本扩军80/巴西包裹税78/PPI 78/F-16滞留76/EV占比65% 76/蜂群74/香港生物医药74）、美联社 中方驳斥蒸馏指控 90★summit、路透 DeepSeek科创板IPO 88（**官网 reuters.com URL 经腾讯转载"文章来源"背书取得**）、金融时报 CXMT/YMTC囤DUV 86（Wccftech转载）、路透 OpenAI失控智能体 82（The Star转载）、国务院4条官方、BBC 4、CNN 2、NYT 1、AJ 1、卫报 1
- 交叉验证 3 组：①CXMT/1260H 命中 FT「CXMT+YMTC囤积三年用量ASML DUV」→ 补录 86★；②美中关税制裁 无窗口内新遗漏（govinfo 钢格栅反补贴日落复审属程序性）；③AI 远程算力 无新（RASA/云漏洞已于 09-08 经 Asia Times 收录）
- update-news.sh --auto 成功：199 条/8 天/今日 32/三零全绿（collectedAt≠今日0·date<昨天0·URL重复0）/官方字段0缺/模板摘要0/导航残留0/JS 0 错误/HTML 双端一致 304727B
- git：主 commit f86eaa7 push 首失败（Failure when receiving data）→ 代理重试成功；补提交 e3abc74（webfetch 988→1016 / 官方源 97 / update-news.sh 修复）；远程 main=5b4faaa（AI 看板自动化接续提交）一致
- 飞书：①来源字段补 2 选项「金融时报」「NSA/FBI/CISA」→ 29 选项（**hue 必须用 Gray 不是 Grey**，否则 800010701）②--today 仅同步 1 条（date==today）→ 补跑全量同步 61 条（8 天窗口补档）
- 线上 ?t= 二次请求 HTTP 200 304727B lastUpdated 09:27，今日 32 条全在线

## 2026-09-11 刷新（09:23 自动，V2.15）
- 官方源：源组丢失第 16 次复发（新输出仅 30 条：白宫2/国务院0/国防部21/财政部3/商务部1/USTR3）→ /tmp/us-official-backup-0911.json 恢复 97 + merge 2 条白宫新增（S.858 国家荣誉勋章纪念碑选址法案 / Trump Dividend 5000 美元现金计划）→ 99 条 6 源齐全；2 条均补 title_zh+summary_zh；无程序性文告混入
- 反爬官方站窗口内 0 涉华：war.gov 最新 9/11 五角大楼纪念地临时关闭（程序性）+ 9/9 海军微型反应堆；commerce.gov 最新 G20 09-02 出窗口；USTR 最新 09-08 加拿大声明出窗口
- **WebFetch 11 源仍大面积失败 → 新固化通道：WaPo（feeds.washingtonpost.com/rss/world）与 Politico（politico.com/rss/politicopicks.xml）RSS 可代理 curl 直取 200 并带真实官网 URL**，不必再走 WebSearch 兜底；BBC/Guardian/AJ/NYT 本地代理 RSS 全 200；SCMP /rss/4|91|5/feed 需 -L；CNN 走 WebFetch edition.cnn.com/world；AP 走 WebFetch apnews.com/world-news
- 收录 46 条全部 date∈{09-10,09-11}（SCMP 10/NYT 6/BBC 5/卫报4/Politico4/WaPo4/AJ4/AP3/路透2/WSJ2/CNN2）；1 条卫报道琼斯稿被模糊标题去重（与 CNN 同事件）→ 上板 45
- 转载（验证 200 带 repost_from）：路透 HBM 芯片涨价→AOL 全文；路透 天工Ultra→共同社英文网；WSJ GLP-1→印度铸币报；WSJ 星环科技→TradingView DJN；美联社 300 亿美元降税→雅虎 AP 稿
- 交叉验证 3 组：①无窗口内新（命中 HBM 涨价已收）②**命中美联社「中方望早日达成 300 亿美元对等降税」+ USTR 格里尔 9/24 公布降税清单预告**（AP 稿已收）③AI 远程算力无新（RASA 仍待参议院、BIS 子公司规则为 5-31 旧规）
- update-news.sh --auto 成功：208 条/7 天/今日 47/三零全绿/官方字段 0 缺/导航残留 0/JS 0 错误/HTML 双端一致 234337B；push dc2dd0c + 补提交 ea2fba9；飞书 --today 仅 2 条 → 全量补档 +46；线上 ?t= 200 lastUpdated 09:26

## 经验增量（09-11）
- WaPo / Politico 官方 RSS 可代理直取（此前依赖 WebSearch 定位），加入 RSS 兜底固定清单
- 路透官网 URL 反查清单固定输出（本日 2 条：HBM 芯片涨价 88★ / 天工Ultra 86★），已随汇报附出
- 官方源组丢失已第 16 次 → 备份恢复 + merge + 逐条补中文仍是标准动作
