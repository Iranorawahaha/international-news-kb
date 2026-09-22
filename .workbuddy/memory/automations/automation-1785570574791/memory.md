# 自动化执行记忆：国际新闻看板每日刷新

## 2026-09-18 刷新（09:23 自动，V2.17，一次会话完成）
- 官方源：源组丢失第 19 次复发（新输出仅 37 条：国防部21/国务院5/白宫4/财政部3/USTR3/商务部1）→ /tmp/us-official-backup-0918.json 恢复 110 + merge 1 条窗口内新增（国务院 09-17「鲁比奥与立陶宛外长关键矿产框架 MOU 签署」）→ **111 条 6 源齐全**（国务院49/白宫27/国防部27/USTR4/财政部3/商务部1）；新增条补 title_zh+summary_zh 并令 `title=title_zh`
- 官方源窗口内剔除：白宫 09-17 四条（海水垂钓行政令 / 狩猎传统行政令 / 向参议院送交撤回提名 / 「信仰群体 250 项胜利」PR）无新闻价值；国务院「伊朗制裁规避网络 Operation Economic Outcast」「古巴矿业制裁 + Fact Sheet」「鲁比奥会见哥斯达黎加外长」非涉华非核心 → 剔除
- ⭐ **路透 sitemap 法连续第四日全官网**：前 10 片 1000 条一次成功（含 `<news:title>` 与 lastmod），筛 105 条相关 → 取 13 条入池全为 reuters.com 官网 URL，**repost_from = 0，「一键搜官网」清单连续第四日为空**
- WebFetch 11 源仍大面积失败 → 代理 7890 RSS 兜底：BBC/Guardian/AJ/NYT/WaPo/Politico/**SCMP 4·91·5 三片全 200 一次成功（无重试）**；**CNN 改用 curl `edition.cnn.com/world`（4.97MB）+ 正则提链与标题**（4 条，优于 WebFetch）；AP 走 WebFetch `apnews.com/hub/world-news` 取官方 URL + GN RSS `site:apnews.com when:2d` 取真实 pubDate
- 彭博社 `fetch_bloomberg_rss.py --days 2`：候选 20 条 → 按窗口(09-17/09-18)筛 → **入库 7 条**（全官网 URL）；FT 走 `r.jina.ai/https://www.ft.com/{world|china|companies}` 提官网 URL（GN RSS 链接为混淆串不可用）+ WebSearch 2 家以上转述交叉比对撰摘要 → **入库 6 条（5 条官网 URL）**
- 收录 78 条（全部 date∈{09-17,09-18}）；剔除 5 条 date=09-16（NYT F-35/伊朗外长、卫报南非签证、CNN OpenAI、Politico 两党 AI 分歧）→ 均已被窗口内其他源覆盖，不硬凑
- ⭐⭐ **重大根因发现：`title` 字段缺失 → 每源只上 1 条**。首轮 78 条只上板 13 条（恰 == 信源数 13，且每源恰为最高分那条）。日志特征「🔁 重复移除: ... (来源: 路透社)」**标题为空**。根因：去重第 3 步 `unique_key` 由 `art.get('title','')` 生成，我只写了 `title_zh`/`title_en` 未写 `title` → 同源 unique_key 全等。补 `title=title_zh` + `summary=summary_zh` 后重跑即恢复 78 条。已固化 boards/intl.md（列为与 collectedAt 并列的第二号丢条原因）
- update-news.sh --auto 成功：331 条/6 天/今日版面 **78 条**（AI·科技26/中美博弈22/地区局势12/中欧与盟友9/美国内政3/中国外交2/全球多边2/其他2；元首级 5，≥88 共 12 条）；三零全绿（collectedAt≠今日0 · date<昨天0 · URL重复0 · 版面内自身重复0）；官方 1 条 0 缺字段/0 模板摘要；导航残留 0；无中文/英文标题 0；黑名单域名 0；JS 0 错误；HTML 双端一致 361973B
- git：主 commit c40169d（update 自动 push）→ 补提交 d75e519（webfetch 1385 / 官方源 111 / us-official-report），`git ls-remote` 核实远程一致
- 飞书：`--today` 同步 0 条（今日版面多为 date=昨日，属既有约定）→ 补跑全量（331→去重 255→新增 76），76 条覆盖今日版面；无需新增 source 选项
- 线上 ?t= 二次请求 HTTP 200 **361973B**，与本地逐字节一致；今日 78 条线上命中 78/78；lastUpdated 2026-09-18 09:34
- 头条：特朗普将在安德鲁斯联合基地迎接习近平（92★）/ 美推迟产能过剩关税至习特会之后（92★）/ 华为称 AI 芯片需求超供给（92★）/ 习特会谈什么（90★）/ 中美或宣布加强两军关系（90★）/ 交易员聚焦习特会寻 AI 与人民币线索（86★）/ 华为徐直军称中国 AI 尚不足以感知前沿风险（88★）/ 俄中否决联合国对伊监督授权（88★）/ 中国回击美涉俄制裁关税法案（88★）/ 美盟友忧特朗普在台湾问题上让步（88★）
- **建议综合（当日同事件多源，供日报/人工采纳）**：①华为 Connect 大会徐直军表态（路透92+路透88+FT86，3 源）②俄中否决联合国伊朗监督授权（路透88+NYT88+AJ86，3 源）③中美元首会晤前瞻（SCMP92+彭博92+路透90+彭博86，4 源）④加拿大-欧盟「准成员」（BBC80+NYT80+WaPo80+卫报78+AP78，5 源）⑤Anthropic Claude 参与自身研发（WaPo84+彭博80，2 源）⑥AI 行业放缓路线分歧（BBC86+AP82+彭博78，3 源）⑦美众议院涉俄制裁法案与中印（SCMP88+BBC82，2 源）⑧卡尼欧盟演讲（卫报78+AP78+WaPo80，3 源）
- 固定附加项：`gen_reuters_recheck_list.py` 输出「今日无路透转载条目（全官网或空缺），无需反查」——连续第四日为空

## 经验增量（09-18）
- ⭐⭐ **入库 schema 必须含 `title`（= title_zh）与 `summary`（= summary_zh）**，不能只写 `title_zh`/`summary_zh`；否则同源条目在去重第 3 步全部判为重复，每源只剩 1 条。**判据：今日版面条数 == 信源数 → 立即查 title 字段**
- FT 官网 URL 获取法（9-18 验证）：GN RSS 链接是混淆串，**改用 `curl -x 7890 https://r.jina.ai/https://www.ft.com/{world|china|companies}` 抓栏目页 markdown，正则提 `[标题](https://www.ft.com/content/<uuid>)` 即可拿到官网 URL**；正文仍为付费墙 → 摘要走 WebSearch 找 2 家以上转述交叉比对
- CNN 最优通道再确认：`curl edition.cnn.com/world`（4.97MB）→ 正则 `href="(/2026/09/1[78]/[^"]{10,120})"` 提链 + 邻近 `<a>` 文本提标题，比 WebFetch 稳定
- 官方源新增条 `title` 字段需显式设为中文标题（官方源约定：title=中文标题、summary=英文原文、summary_zh=中文摘要），否则同样触发同源去重
- 09-17 版面定稿后未再增补；archive 6 天窗口正常

## 2026-09-17 刷新（09:23 自动，V2.17，一次会话完成）
- 官方源：源组丢失第 18 次复发（新输出仅 37 条：国防部21/白宫6/国务院3/财政部3/USTR3/商务部1）→ /tmp/us-official-backup-0917.json 恢复 107 + merge 3 条 09-16 实质新增（白宫「政府采购互惠备忘录」（针对加拿大 Buy Canadian，清出联邦采购）/ 国务院「制裁巴勒斯坦权力机构与巴解组织官员」/ 国务院「MSMT 11 国联合声明：朝鲜海外劳工多集中中国与俄罗斯」）→ **110 条 6 源齐全**（国务院48/白宫27/国防部27/USTR4/财政部3/商务部1）；3 条新增全补 title_zh+summary_zh
- 官方源窗口内剔除：白宫 09-16 其余 5 条（Constitution Day / POW-MIA Day 程序性文告、S.32+S.307 法案签署、水质行政令、北卡政绩 PR）无新闻价值 → 剔除；国务院「Mexico National Day」按 National Day 先例剔除；war.gov 最新 08-17 出窗口；商务部最新 07-16 出窗口；USTR 最新 08-13 出窗口
- ⭐ **AP 通道升级（解决长期最弱通道）**：AP 官网 curl 恒 403（含 sitemap/news-sitemap，Cloudflare）→ **WebFetch `apnews.com/hub/world-news` 可返回真实 `apnews.com/article/<slug>-<hash>` 官方 URL（含标题不含日期）**，与 GN RSS `site:apnews.com when:2d`（标题+真实 pubDate）按标题匹配 → 当日收录 **5 条**（此前多日仅 2-3 条），全部官方 URL
- WebFetch 11 源仍大面积失败（CNN/AP 均 fetch failed）→ 代理 7890 RSS 兜底：BBC/Guardian/AJ/NYT/WaPo/Politico/scmp91/scmp5 全 200（**scmp4 /rss/4/feed 首次 000 需重试**，wapotech/politico 首次 000 重试即 200）；**CNN 改用 curl `edition.cnn.com/world` 得 3.4MB HTML + `lite.cnn.com` 提取标题**（比 WebFetch 稳）
- ⭐ **路透 sitemap 法连续第三日全官网**：前 10 片 1000 条一次成功（无分片失败），解 `<news:title>` 筛相关 373 条 → 取 11 条入池全为 reuters.com 官网 URL，**repost_from = 0，「一键搜官网」清单连续第三日为空**
- ⚠️ **WSJ 仍为最弱通道**：TradingView DJN 仅覆盖道琼斯电讯稿 → 当日 WSJ 仅 2 条（Fed/Warsh 相关，转载标注）。WSJ 深度特稿（中国黑客公司 AI 网络间谍、Driscoll's 蓝莓被中国偷种）**无合格转载**（仅 threatbeat.com/realnarrativenews.com 等低质聚合）→ 按纪律空缺
- 收录 62 条 webfetch（全部 date∈{09-16,09-17}）：路透11/SCMP11/BBC6/NYT6/Politico5/AP5/卫报4/AJ4/WaPo4/CNN3/WSJ2/FT1；1 条 CNN 评论（date=09-15）出窗口剔除；与池+archive 去重剔除 2 条 → 池 1238→1300
- ⭐ **交叉验证补录 1 条（AI 出口管制专题）**：FT「US-China AI regulation remains difficult despite shared concerns」（09-16，AI 治理/出口管制/远程算力，用户点名必查主题）→ 用 WebSearch 定位转述媒体（tmcnet insight + aisengtech brief，2 家内容一致）取第三方背书的 ft.com URL → **「金融时报」为飞书已有来源选项，无需新增**；另据 Reuters Factbox 充实「AI 竞争阴影笼罩习特会」摘要（蒸馏指控/远程算力/H200 例外/监管分歧五要点）。CXMT/1260H 无窗口内新；美中关税制裁无新（govinfo L-lysine 反倾销令按 09-16 程序性贸易救济先例不收）
- update-news.sh --auto 成功：292 条/6 天/今日版面 **65 条**（AI·科技19/中美博弈13/地区局势11/中欧与盟友10/美国内政7/中国外交2/全球多边2/其他1；元首级 7，≥88 共 19 条）；三零全绿（collectedAt≠今日0 · date<昨天0 · URL重复0 · 版面内自身重复0）；官方 3 条 0 缺字段/0 模板摘要；导航残留 0；无中文标题 0 / 无英文标题 0；JS 0 错误；HTML 双端一致 470724B
- ⚠️ **转载标签被全量 update 丢弃（已知坑复发）**：2 条 WSJ TradingView 条目的 repost_from 被抹掉 → 改 data/news-data.json 按 URL 补字段 + `sed -n '909,1010p' update-news.sh` 单独跑 GENERATE_HTML_V12 段 + check_js_syntax + inject_nav.py，**未重跑全量 update**；修复后线上含「TradingView（道琼斯电头）」标签 2 处
- ⚠️ git 首次 push 失败（`Failure when receiving data from the peer`）→ 重试即成功。主 commit 07a8df1 → 补提交 4337a46（webfetch 1300 / 官方源 110 / us-official-report / news-data / 双端 HTML），远程一致
- 飞书：①`--today` 同步 5 条 ②补跑全量（292→去重232→新增 60），5+60=65 全覆盖；无需新增 source 选项
- 线上 ?t= 二次请求 HTTP 200 **470724B**，与本地逐字节一致；今日 65 条线上命中 65/65；lastUpdated 2026-09-17 09:34
- 头条：美国会通过对俄制裁法案剑指中印能源买家（95★）/ AI 竞争阴影笼罩习特会（92★）/ 贝森特称愿就 AI 共同风险与中方沟通（92★）/ 中国防长香山论坛避开热点（92★）/ 北京在峰会前接待伊朗外长（92★）/ 美军白宫为习近平到访彩排（90★）/ 美情报机构警告售沙特 F-35 或致中国窃取技术（90★）/ FT 中美 AI 监管分歧难弥合（88★）/ 华为在美受审指控窃取 T-Mobile 机器人技术（88★）/ 五角大楼不顾警告推进 AI（88★）/ 美联储三年多来首次加息（88★）
- **建议综合（当日同事件多源，供日报/人工采纳）**：①对俄制裁法案涉中印能源买家（SCMP95+路透88+卫报88+Politico88+AJ86+CNN84，6 源）②美联储首次加息（BBC88+Politico84+半岛82+WSJ82+CNN80+WSJ78，6 源）③加拿大「准成员」与特朗普对欧关税威胁（Politico84+WaPo84+BBC82+NYT82+AP82+白宫80，6 源）④王毅会见伊朗外长（NYT92+路透88+SCMP88，3 源）⑤中国防长香山论坛（SCMP92+路透90，2 源）⑥奥特曼 AI 安全表态（BBC86+WaPo84，2 源）⑦对以军售一吨级炸弹（NYT80+卫报80，2 源）⑧俄暗杀图谋（BBC82+AP82，2 源）
- 固定附加项：`gen_reuters_recheck_list.py` 输出「今日无路透转载条目（全官网或空缺），无需反查」——反查清单连续第三日为空

## 经验增量（09-17）
- ⭐ **AP 通道升级已写入 boards/intl.md**：WebFetch `apnews.com/hub/world-news` 取官方 URL + GN RSS 取标题与日期，标题匹配合并 → 取代「AP 只能靠多源交叉确认少量收录」的旧结论
- CNN 最优通道 = curl `edition.cnn.com/world`（3.4MB 全文）+ `lite.cnn.com`（标题干净、URL 带日期）→ 优于 WebFetch（fetch failed）与其 RSS（2023 缓存旧稿）
- WSJ 深度特稿无合格转载时按纪律空缺；TradingView DJN 仅覆盖道琼斯电讯稿
- FT 条目构造：转述媒体页面常直接标注 `URL: https://www.ft.com/content/<uuid>` → 2 家以上转述交叉比对后撰写摘要，严禁凭 URL 编造
- HTML 统计条「今日新增」= `date == 今日` 条数（非 collectedAt），9-16/9-17 口径一致，属既有约定勿误判为 Bug

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

## 2026-09-19 执行摘要（成功）
- 官方源：fetch_us_official.py 后源组丢失复现（111→37）→ 备份恢复+合并 5 条 09-18 新增（H-1B 行政令/格雷厄姆法案/鲁比奥会韩外长/联大行程/WFP 任命），116 条 6 源齐全
- 13 信源：RSS 通道 11 源 228 条窗口内 + 路透 sitemap 直取（103 命中）+ 彭博 RSS 22 候选→入库 9 + CNN lite + AP hub + FT 栏目页 + WSJ 3 条（Livemint/Yahoo 转载+官网直链）
- 入库 75 条（1 重复跳过），collectedAt 全部=2026-09-19 09:30
- 今日版面 80 条：路透10/SCMP9/彭博9/BBC7/NYT6/CNN5/Politico5/WaPo5/FT4/AJ4/AP4/卫报4/WSJ3/官方5；归档校验三项 0；导航/模板残留 0（H-1B 条目 summary 装饰文字清理 3 轮后清零，注意 summary 与 summary_en 两个字段都要改）
- 3 commit 推送（ba3c5e2/a94c579/0f5daef/bdea5d3），线上与本地 len 一致
- 飞书：--today 16 条 + 全量补 76 条（date=09-18 部分）
- 路透 recheck：今日无转载条目（全官网），repost_from=0
- 教训：合并脚本里字符串内含中文引号时用 Write 写 .py 文件而非 heredoc；update-news.sh --auto 后必须精确补提交两个 pool 文件

## 2026-09-20 刷新（09:23 自动，V2.17，一次会话完成）
- 官方源：源组丢失第 20 次复发（新输出仅 29 条）→ /tmp/us-official-backup-0920.json 恢复 116 条 6 源齐全；窗口内唯一新增为国务院「Saint Kitts and Nevis National Day」→ 按 National Day 先例剔除（未入 us-official.json，但 fetch 脚本直写 news-data.json 混入今日版面 → 用 URL 精确删除 + sed 910-1011 重跑 GENERATE_HTML_V12 段修复，今日版面 61→60）
- 13 信源：RSS 通道 7 家 152 条窗口内（BBC/卫报/AJ/NYT/WaPo/Politico×2/SCMP×3 全 200）+ 路透 sitemap 直取（1000 条，标题筛 16 条相关）+ 彭博 RSS 10 候选→入库 6 + CNN lite 59 候选 + AP hub 官网 URL + WSJ 经 WebSearch 拿 2 条官网 URL（Dario/Jensen AI 减速之争 88★、德国重整军备 76★）+ FT 栏目页 4 条官网 URL
- 入库 63 条（8 条与池重复跳过），collectedAt 全部=2026-09-20 09:30；date 分布 09-19×60 / 09-20×3
- 今日版面 60 条：路透10/SCMP6/彭博6/AP5/NYT5/BBC5/Politico5/WaPo4/AJ4/卫报4/WSJ2/FT2/CNN2；AI·科技19/地区局势16/美国内政9/中美博弈8；元首级5，≥88 共6条；三零全绿+与历史版面重复0+黑名单0+模板摘要0
- ⚠️ 本次坑：news-data.json 已升级 V1.2 dict 结构（archive 按日期为 key、dates 为 list），校验脚本须按 nd['archive']['2026-09-20'] 取数，勿再用列表假设
- git：update 自动 commit ec30f23 → 补提交 cce7ac7（webfetch 1523/官方源116/news-data/双端HTML），git ls-remote 核实一致；线上 ?t= HTTP 200 743890B 与本地逐字节一致
- 飞书：--today 3 条 + 全量补 69 条
- 交叉验证 3 组：①CXMT/1260H 无窗口内新 ②对俄制裁法案签署（09-18）+商务部回应已由彭博「中国痛批美对俄伊制裁新法」覆盖 ③AI 远程算力无窗口内新（均为旧 PDF/报告）
- 固定附加项：gen_reuters_recheck_list.py 输出「今日无路透转载条目」——连续第五日为空，repost_from=0
- 头条：习特会前中方筹码更足（SCMP 92）/ 贝森特-何立峰周日摩根大通总部会晤（路透92）/ 美中贸易团队纽约磋商 AI 与伊朗（彭博92）/ 习近平下周抵华府 特朗普亲赴机场迎接（AP 90）/ 特习对决笼罩世界经济（彭博88）/ 达里奥 vs 黄仁勋 AI 减速之争（WSJ 88）/ 中国痛批美对俄伊制裁新法（彭博86）/ AI 放缓反垄断诉讼（CNN86/AP84）/ 特朗普格陵兰协议意在增加对华筹码（SCMP84）/ 胡塞重大升级袭击利雅得（NYT84）
- 建议综合（同事件多源）：①AI Force/AI 沙皇（SCMP+路透+BBC+卫报+Politico+彭博+CNN，7 源）②胡塞袭击利雅得（NYT+BBC+卫报+SCMP+AJ+AP，6 源）③格陵兰安全协议（路透+NYT×2+BBC+卫报+AJ+FT，7 源）④习特会前瞻（SCMP92+彭博92+AP90+SCMP90，多源）⑤贝森特-何立峰会晤（路透92+彭博92，2 源）⑥白宫媒体禁令（路透+BBC+Politico×2+CNN+彭博，6 源）⑦Gemini 入侵真实系统（SCMP+BBC+FT，3 源）⑧AI 放缓反垄断诉讼（CNN86+AP84，2 源）
- 教训：①RSS 标题含弯引号 ‘’ 时 find 匹配须用无引号片段 ②fetch_us_official.py 会直写 news-data.json（绕过 us-official.json 池），剔除窗口外程序性文告后必须检查 news-data.json 是否被混入

## 2026-09-22 刷新（14:09 自动，V2.17，一次会话完成）
- 官方源：源组丢失第 21 次复发（新输出仅 38 条）→ /tmp/us-official-backup-0922.json 恢复 116 + merge 5 条窗口内新增（白宫「进入白宫是特权而非权利」回应媒体诉讼 / 国务院「鲁比奥会见北极盟友」/「与意大利签关键矿产 MOU」/「会见伊拉克总理扎伊迪」/「会见肯尼亚总统鲁托」）→ **121 条 6 源齐全**；剔除 Mali National Day（先例）、白宫 G20 能源部长会回顾稿（09-16 事件无新进展）、意大利双边读稿（与 MOU 稿重复）、玻利维亚总统会见（非重点国例行读稿）
- 13 信源：RSS 通道 7 家（BBC/卫报/AJ/NYT/WaPo/SCMP×3 全 200）+ 路透 sitemap 直取（1000 条，窗口内相关 211 条，取 11 条全官网 URL）+ 彭博 RSS 25 候选→入库 7 + CNN curl edition.cnn.com/world（5 条）+ AP hub world-news/china 官网 URL + GN RSS 取日期（5 条）+ WSJ 经 WebSearch 拿 1 条官网 URL + FT 栏目页 r.jina.ai 提官网 URL（5 条）+ Politico 改走 politico.eu/feed/（4 条）
- 入库 74 条，collectedAt 全部=2026-09-22 09:30:00；date 分布 09-21×48 / 09-22×26
- 今日版面 79 条（74 webfetch + 5 官方）：AI·科技21/中美博弈18/地区局势15/美国内政9/中欧与盟友5/其他5/全球多边5/中国外交1；元首级 11，≥88 共 21 条；三零全绿 + 与历史版面重复 0 + 版面内重复 0 + 黑名单 0 + 模板摘要 0 + 缺中英文标题 0 + repost_from 0 + 路透官网 11/11
- ⚠️ archive 无 09-21 键（周一未跑）：09-21 内容按 V2.11 自然归入 09-22 版面
- git：主 commit 874fce5 → 补提交 7ac9063（webfetch 1597/官方源121/report），远程一致；线上 ?t= HTTP 200 706259B 与本地逐字节一致，79/79 命中；lastUpdated 2026-09-22 14:20
- 飞书：--today 26 条 + 全量补 65 条
- 交叉验证 3 组：①CXMT/1260H 无窗口内新 ②美中关税制裁无新（镀锡板反倾销初裁属程序性）③**AI 出口管制/远程算力命中 1 条**（SCMP 09-21 美国权衡将技术封锁扩展至云计算）→ 已补录；另补 SCMP 海光边缘 AI 芯片
- 固定附加项：gen_reuters_recheck_list.py 输出「今日无路透转载条目」——连续第五日为空
- 头条：习要求特朗普依 1982 公报停止对台军售（93★）/ 稀土摩擦或拖累贸易休战延期（92★）/ 特习 AI·贸易·伊朗摩擦但求稳定（92★）/ 贝森特称两月后深圳再开 AI 安全会谈（92★）/ 美中就 AI 达成对话安排（92★）/ 北京确认习本周国事访问（90★）/ 阿里发新一代自研 AI 芯片（90★）/ 五角大楼黑名单成特习 AI 会谈棘手议题（90★）
- 建议综合（8 组，供日报采纳）：①元首会晤前瞻与贸易休战（7 源）②美中 AI 安全对话（5 源）③对台军售与台海（5 源）④稀土与关键矿产（5 源）⑤军队高层开除党籍（3 源）⑥白宫媒体禁令与诉讼（5 源）⑦也门胡塞攻势（5 源）⑧俄罗斯议会选举（4 源）

### 经验增量（09-22）
- ⭐ **FT 真实发布日核实法**：`curl -x 7890 https://r.jina.ai/https://www.ft.com/content/<uuid>` 返回 `Published Time` 字段 → 据此剔除 09-18 / 08-20 两条出窗口旧稿（FT 栏目页只给标题+URL）
- ⭐ **Politico 通道更新**：`politico.com/rss/politicopicks.xml` 已被 Cloudflare 拦截（`Just a moment...`）→ 改走 `https://www.politico.eu/feed/`（200，10 条真实 pubDate + politico.eu 官网 URL）
- ⚠️ **GN RSS pubDate ≠ 页面发布日**：WSJ《Burned Out and Unemployed…》GN 标 09-22，实际 09-20 16:03 UTC → 必须第三方核实
- ⚠️ **Write 工具单次内容上限约 4KB**：74 条池拆 17 个 `/tmp/pool0922/*.txt` 分块（管道分隔）+ 合并脚本，比逐条 dict 更稳
- ⚠️ **路透 sitemap 日期正则坑**：`/(\d{4})-(\d{2})-(\d{2})/?$` 带前导斜杠 → 996 条 date 全空；正确 `(\d{4})-(\d{2})-(\d{2})/?$`（已固化到 skill 并 bump v1.0.1）
- 收尾：boards/intl.md 已补 09-22 经验增量（commit 8e7afd1，远程核实一致）
