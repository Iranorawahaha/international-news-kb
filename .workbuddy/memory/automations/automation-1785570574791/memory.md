# 自动化执行记忆：国际新闻看板每日刷新

## 2026-09-16 刷新（12:03 自动，V2.16，一次会话完成）
- 官方源：源组丢失第 17 次复发（新输出仅 37 条：国务院9/国防部21/财政部3/商务部1/USTR3，白宫 curl 失败）→ /tmp/us-official-backup-0916.json 恢复 104 + merge 3 条窗口内实质新增（国务院 09-15：鲁比奥-阿曼外长通话 / 鲁比奥-叙利亚外长通话 / 涉种族歧视新签证限制政策）→ **107 条 6 源齐全**（国务院46/国防部27/白宫26/USTR4/财政部3/商务部1）；6 条 National Day 程序性贺电按 San Marino/Eswatini 先例剔除；3 条新增全补 title_zh+summary_zh
- 官方源窗口内剔除：白宫 09-15 两条（梅拉尼娅 Ashe County 访问 / Memphis 治安 PR）无新闻价值 → 剔除；war.gov 最新 09-15（MQ-25A 首产合同 5.62 亿 / USS St. Louis 边境任务 / 工业基础备忘录）非涉华非 AI 经贸 → 如实空缺；commerce.gov 最新 09-02 出窗口；USTR 最新 09-09 出窗口
- ⭐ **路透官网 URL 直取法升级（sitemap 自带 `<news:title>`）**：抓前 10 片（600/700 首次失败需重试）→ 1000 条解析出 (loc, lastmod, title) 三元组 → **直接按标题关键词筛选，不再用 slug 命中率匹配**（精度更高）；筛出 123 条相关，取 11 条入池全为官网 URL，**repost_from = 0，反查清单连续第二日为空**；反向挖出 RSS 未覆盖的香港五年规划/先正达港股 IPO/印尼对华钢铁反倾销 3 条
- WebFetch 11 源仍大面积失败 → 代理 7890 RSS 兜底（BBC/Guardian/AJ/NYT/WaPo/Politico 全 200；**SCMP /rss/4/feed 首次 502 需重试**，/rss/91|5 直通）；CNN 走 WebFetch edition.cnn.com/world + /business/tech（拿到 4 条 09-15）；AP 走 WebFetch apnews.com/world-news
- ⚠️ **WSJ 官网 sitemap 403（DataDome）**，RSS 旧稿禁用 → 走 GN RSS 候选 + WebSearch 定位 finwire.io 转载（Investing.com 电头）收录墨西哥 AI 硬件独家；WSJ 当日仅 1 条，如实偏低
- ⚠️ **AP 官网 curl 403 且 WebFetch 返回导航样板（正文+日期均被截断）** → 无法解析发布日；仅收录 2 条日期经多源同日交叉确认者（立陶宛无人机 / 盖茨基金会 10 亿 AI）+ 1 条 Fed 加息预告，共 3 条
- 收录 59 条 webfetch（date∈{09-15,09-16}）：路透11/SCMP10/NYT6/BBC5/卫报5/AJ5/Politico5/CNN4/WaPo4/AP3/WSJ1；交叉验证补录 1 条（Export Compliance Daily：BIS 无需正式立法即可管制芯片远程访问，86★）→ 池 1178→1238
- 交叉验证 3 组：①CXMT/1260H 无窗口内新（返回 6-7 月旧闻）②美中关税制裁无新（govinfo 钢货架反倾销行政复审终裁属程序性，按先例不收）③**AI 远程算力命中 1 条**（ECD 09-15，已补录）
- update-news.sh --auto 成功：260 条/6 天/今日版面 **63 条**（地区局势19/AI·科技17/美国内政7/中美博弈6/全球多边6/中国外交4/中欧与盟友2/其他2；元首级 6）；三零全绿（collectedAt≠今日0 · date<昨天0 · URL重复0）；官方条目 0 缺字段/0 模板摘要；导航残留 0；JS 0 错误；HTML 双端一致 396577B
- ⚠️ **转载标签被全量 update 丢弃（已知坑复发）**：WSJ finwire 条目的 repost_from 被脚本重建条目时抹掉 → 直接改 data/news-data.json 补字段 + 单独运行 GENERATE_HTML_V12 段（sed 提取 909-1010 行）+ check_js_syntax + inject_nav.py，**不重跑全量 update**
- git：主 commit c8d687f（push 成功）→ 补提交 610aa31（webfetch 1238 / 官方源 107 / news-data / 双端 HTML）推达远程一致
- 飞书：①--today 同步 10 条 ②全量同步首次报 **800030005**（来源选项缺 "Export Compliance Daily"）→ field-get 拿全 29 选项 → 追加 1 项（hue=Gray）→ field-update full PUT → 30 选项 → 重跑全量成功 **53 条**（10+53=63 全覆盖）
- 线上 ?t= HTTP 200 **396577B**，与本地 `on==loc` 逐字节一致；今日 63 条线上命中 63 条；lastUpdated 2026-09-16 12:18
- 头条：英伟达CEO将出席特朗普为习近平举办的晚宴（95★）/ 贝森特确认周末会何立峰（92★）/ 董军香山论坛对美语调趋缓（92★）/ 中国防长吁遏制历史倒退（90★）/ 美承认在轨武器（88★）/ 约翰逊反对AI暂停令（88★）/ 中国新五年规划押注芯片AI（88★）/ 美施压墨西哥封锁中国AI硬件（88★）/ 中国出境新规（86★）/ 伊朗外长访华会王毅（86★）/ CNN「若AI真能毁灭人类为何对华让步」（86★）/ BIS 远程算力管制（86★）

## 经验增量（09-16）
- ⭐ **路透 sitemap 的 `<news:title>` 优于 slug 匹配**——直接解标题关键词筛选，一次拿全官网 URL+原始标题+真实日期，并能反向挖出 RSS/GN 未覆盖条目；已写入 skill `reuters-official-url-lookup` v1.1
- sitemap 分片（600/700）偶发抓取失败，**必须逐片重试并核对总条数 ≈ 100×片数**
- SCMP `/rss/4/feed` 会偶发 502，重试即 200（91/5 直通）
- WSJ 官网 sitemap 403、RSS 旧稿禁用 → 只能 GN RSS + WebSearch 定位 finwire.io/TradingView 转载，当日条数必然偏低
- **AP 是当日最弱通道**：curl 403 + WebFetch 只返回导航样板（日期/正文截断）→ 只能靠多源同日交叉确认日期后少量收录，勿硬凑
- 全量 update 会抹掉非固定字段（repost_from 等）→ 收尾必须核对并按「改 json + 只跑 HTML 段 + inject_nav」修复
- 飞书 800030005 = 来源选项缺失；流程固定为 field-get → 追加选项（hue 用合法值如 Gray）→ field-update full PUT → 重跑全量

## 2026-09-15 刷新（09:23 自动，V2.15，一次会话完成）
- 官方源：源组丢失第 18 次复发（新输出仅 35 条：白宫2/国务院5/国防部21/财政部3/商务部1/USTR3）→ /tmp/us-official-backup-0915.json 恢复 99 条 6 源齐全 → 合并 5 条窗口内新增（国务院 4：吉布提阿尔忒弥斯协定 / 制裁俄 VTB 银行 / 美日澳印 Quad 东京后勤推演联合声明 / 美越五年卫生 MOU；USTR 1：2027 NTE 外国贸易壁垒公众意见征集）→ 104 条；4 条国务院均补 title_zh+summary_zh
- 官方源窗口内剔除（回页面核对发布日）：白宫「Congressional Bills…」实为 09-11 发布且纯内政程序性 → 剔除；国务院「Iran's Terrorist Proxies」实为 09-10 → 剔除；白宫「Warrior Ethos…DUDE 44 Bravo」人物特写/PR → 剔除；war.gov 最新 09-14（Contracts/9·11 特稿/UAP 法律豁免公告）非涉华非 AI 经贸 → 如实空缺；commerce.gov 最新 09-02 出窗口
- **重大方法升级：路透官网 URL 直取（sitemap-index）**——`reuters.com/arc/outboundfeeds/sitemap-index/?outputType=xml` → 前 10 片（from=0..900，共 1000 条，lastmod 覆盖 09-11~09-15）→ slug 词命中率匹配；**本次 10 条路透全部拿到官网 URL，repost_from = 0，「一键搜官网」清单首次为空**。坑：slug 取法必须 `rstrip('/')` 否则末尾斜杠致 slug 为空、全 0 分
- WebFetch 11 源仍大面积失败 → 代理 7890 RSS 兜底（BBC/Guardian/AJ/NYT/SCMP/WaPo/Politico 全 200；SCMP /rss/4/feed 首次 000 需重试）；CNN 走 WebFetch edition.cnn.com/world、AP 走 WebFetch apnews.com/world-news
- 收录 56 条 webfetch（全部 date∈{09-14,09-15}）：路透 10 / SCMP 10 / NYT 7 / CNN 5 / 卫报 5 / AP 4 / WaPo 4 / AJ 4 / BBC 3 / Politico 3 / WSJ 1；AP 头条页露出的 Anthropic 五角大楼稿经 URL 去重剔除（8-28 已收）
- 交叉验证 3 组：①CXMT/1260H 无窗口内新（返回 6-7 月旧闻）②美中关税制裁无新（tariffcharts 载 7.5% 产能过剩关税仍待 9-24 峰会前公布）③AI 远程算力无新（RASA 仍待参议院）→ 无补录；The Information 相关经路透「Palantir/Nvidia 限制外部 AI 模型」一条覆盖
- update-news.sh --auto 成功：229 条/6 天/今日版面 **61 条**（美国23/地区热点16/中国7/其他7/国际会议4/欧洲4；AI·科技 21 条为最大类）；三零全绿（collectedAt≠今日 0 · date<昨天 0 · URL 重复 0）；官方条目字段 0 缺、模板摘要 0；JS 0 错误；HTML 双端一致 339026B
- git：主 commit 3216908（push 成功）→ 补提交 7518eb8（webfetch 1122→1178 / 官方源 104 / report）推达远程一致（中途被其他自动化推到 34e1c17，正常交错）
- 飞书：--today 同步 6 条 → 补跑全量 229 条去重后新增 55 条（6+55=61 全覆盖 8 天窗口）；无需新增 source 选项
- 线上 ?t= 二次请求 HTTP 200 339026B，与本地字节数一致；抽查 4 条今日头条均在页面内
- 头条：中国官媒批 Anthropic「放缓 AI」是冷战手段（88★）/ 华为在美受审陪审团遴选（88★）/ 特朗普否认中国实体助伊朗（86★）/ 中国如何防 AI 失控（86★）/ 中国情报主管警告 AI 威胁执政安全（86★）/ DeepSeek 聘 CFO 筹备 IPO（85★）/ 中国拒绝 AI「设定节奏」（86★）

## 经验增量（09-15）
- 路透 sitemap 法为最新首选，优于 9-14 的 WebSearch 完整标题法（后者只能逐条命中，sitemap 一次批量拿全且可反向挖漏）
- RSS 标题/URL 禁止手抄（120 字符截断）→ 一律脚本从 XML 取 `link`；入库前与池+archive 全量 URL 去重（AP 头条页会重新露出旧文）
- 官方源窗口判断须回页面核对发布日（脚本 date 解析 09-15 两次误判为 09-15，实为 09-11 / 09-10）
