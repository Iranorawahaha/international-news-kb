# Ira 信息看板体系 - 项目记忆

## 项目总览
- **仓库**: github.com/Iranorawahaha/international-news-kb（单仓库承载国际+国内两个看板）
- **GitHub Pages**: https://iranorawahaha.github.io/international-news-kb/
- **定位**: 个人使用 + 向同事分享（华为公共及政府事务部）
- **认证**: Personal Access Token (repo 权限)；推送失败时检查 `$https_proxy` 环境变量

## 看板1: 国际新闻看板 (V1.2.3, 2026-08-01)
- **入口**: https://iranorawahaha.github.io/international-news-kb/
- **V1.2.3**: 彻底移除中文信源（BASIC_SOURCES=[]），11个英文信源全必选（路透/BBC/SCMP/卫报/CNN/NYT/WSJ/半岛/Politico/WaPo/AP）
- **V1.2.2**: 智能打分 `_calculate_priority_score`（默认55分，极高92/高78/元首95）、智能分类、黑名单25+关键词、5条过滤规则
- **V1.2.1**: 飞书去重修复（88→66条）；质量体系固化（is_garbage/clean/dedup/sort 4函数）
- **核心功能**: 7天数据保留(日期Tab) + 飞书Base永久存档 + 双语标题 + 元首级置顶 + 重要性5级 + 单文件HTML
- **飞书存档**: https://my.feishu.cn/base/A2fdb93HLamcKgslr2rcopjRnfd（表ID tblCocvO66XoPsm1，名称"新闻存档"）
- **更新**: `./update-news.sh`（6步：抓取→筛选→去重→排序→飞书归档→HTML生成→Git推送，3-5分钟；WebFetch步骤需在WorkBuddy中执行）
- **使用流程**: 基础采集(终端) → WebFetch补充(对话) → 整合 → 网页生成 → 飞书同步 → git push

## 看板2: 国内新闻看板（Ira 体系，每日9:30自动刷新）
- **入口**: https://iranorawahaha.github.io/international-news-kb/china-news.html
- **一键脚本**: `./refresh_china_news.sh`（3步：抓取 gov.cn 要闻+最新政策 → build_china.py 生成深红政务风单文件看板 → 部署+门户统计+git push）
- **数据**: data/china-news.json；生成: china-news.html（根目录+gh-pages副本）
- **自动化**: automation-1785577010192 每日 09:30 执行（模型 deepseek-v4-flash）
- **质量**: JUNK_KEYWORDS 黑名单过滤营销/文娱/明星八卦/养生内容；严禁修改信源/过滤规则/构建脚本

## 技术架构
- 前端: 单文件自包含 HTML（CSS+JS+数据内嵌，无外部依赖）
- 采集: Python 3.13.12 (/Users/xiaoxiao/.workbuddy/binaries/python/versions/3.13.12/bin/python3)
- 数据: JSON 按日期分组 {archive:{date:[...]}}；7天滚动窗口 + 飞书永久存档双轨制
- 版本控制: Git + GitHub Pages；根目录与 gh-pages/ 双同步

## 质量体系要点
- 唯一键: (title[:30], source)；同步前查询飞书已有记录去重
- 双层质量控制: 采集时过滤 + 整合时再过滤
- 双层排序: Python层 + JS渲染层
- URL完整性4道防线: WebFetch要求URL + validate_urls + 渲染原文链接列 + ≥95%覆盖率检查

## 用户偏好
- 关注: 中美关系 > 经贸制裁 > AI竞争 > 外交资讯
- 语言: 英文资讯双语保存；仅权威信源，禁自媒体/营销号
- 更新: 每日2次（9:30+17:00），手动控制时机

## 已解决问题
- GitHub Pages CSS/JS 404 → 单文件HTML架构
- 11条缺URL(42%) → URL保障机制(100%覆盖)
- 飞书22条重复 → 批量删除+同步前去重
- 中文信源低质(20条仅2可用) → 智能打分+黑名单(90%过滤)
- 版本混乱 → V1.0正式版统一

## 关键经验
1. WebFetch必须明确要求返回URL字段
2. 整合前检查关键字段完整性（尤其url）
3. 静态站优先单文件架构
4. 推送失败先查 $https_proxy 代理端口
5. 定期清理工作空间（历史备份/临时文件）
6. 黑名单关键词是质量生命线（导航页/营销/软文）

## 待优化
- 每日17:00自动邮件日报（用户延后配置）
- macOS LaunchAgent 定时提醒 / WorkBuddy Automation 半自动
- 修复不可用信源（4 URL失效+2 SSL+3反爬）
- 移动端PWA / RSS输出 / 多语言

## V1.3-V1.5 关键经验（官方源+栏目重构，2026-08-04 固化）

### 刷新流程避免错误清单（每步检查）
1. **官方源字段保留**：normalize_schema.py STANDARD_KEYS 必须含 is_official/title_zh/summary_zh/title_en/summary_en/column —— 缺失即整合丢字段（官方源变英文/模板摘要）
2. **去重权威顺序**：AUTHORITY_ORDER 官方源（白宫/国务院/USTR/财政部/商务部/国防部）必须排最前，否则同题合并被媒体源覆盖
3. **终极防线**：update-news.sh save_data 后强制读 us-official.json 升级官方源字段（is_official/title_zh/summary_zh 覆盖 + 修正日期）
4. **真实日期**：官方源 date 用页面真实发布日（extract_page_meta 解析 "JULY 31, 2026"→2026-07-31），绝不用 NOW
5. **cleanup_old 按 date 字段**而非归档 key（7-16 老新闻挂 8-3 群无法清理）
6. **官方解析 URL 白名单**：只抓含日期路径的文章 URL；trailing slash + 路径段>3=文章（白宫习惯带尾斜杠），段≤3=目录页；过滤导航词
7. **中文翻译**：curl 官方源只有英文 → 需补 title_zh/summary_zh（agent 翻译）；白宫/国务院 WebFetch 反爬(404) → Python urllib + agent 翻译
8. **前端排序**：①日期分组 ②summit ③columnPriority ④priority_score；缺日期分组→8-2 混入 8-3
9. **JS 选择器限定**：#dateTabs .tab-btn（勿用宽泛 .tab-btn 误绑栏目 tab）
10. **HTML 模板外置**：intl_template_v15.html 占位符模式（__XXX__），勿在 heredoc 内嵌大模板

### 六大栏目判定（classify_columns.py）
国际会议 > 美国强主体 > 中国强主体 > 热点主语 > 欧洲主体 > 美方行动 > 泛涉华
（特朗普→美国；伊朗袭击美军→地区热点；习近平通话→中国；欧盟加税→欧洲）

### 官方信源每日采集
- curl 直连：白宫/国务院/财政部
- WebFetch 通道：USTR/商务部/国防部（反爬）
- 导航残留词：Executive Orders / 365 Days of Wins / Briefings & Statements / State Department Home 等

## V1.5 每日刷新补充经验（2026-08-06 固化）

### 飞书同步（易踩坑）
1. **补同步每次必须重新拉取飞书全量唯一键**（(title[:30],source)），不可复用上次 keys，否则重复插入（本次 8-04 重复 150 条教训）
2. **record-batch-create 25 条/批**：100 条/批易网络超时（read tcp 超时）；分批次避免
3. **字段选项缺失即整批失败**（800030005 not_found）：同步前先对比待同步条目的 分类/来源 全集与飞书字段选项，缺失先 field-update 补（分类字段 fldYsZLBdJ，来源 fldZHYgBHt）
   - **field-update 的 type 必须传字符串 "select"**（传数字 3 报 800010701 Invalid discriminator value）
   - **已知分类全集会随当日内容变化**：8-11 新增「国际」值需补选项；同步前用 `base +field-list` 拉取实际选项比对（注意字段输出在 data.fields，非 data.items）
4. **历史旧分类值**：地区热点→地缘政治 / 中国→中美关系 / 军事安全→安全冲突 / 社会文化→社会 / 英国政治→地区动态 / 科技产业→科技竞争（8-03 遗留）
5. **update-news.sh 飞书步骤误报成功**（sync 失败但 exit 0）：每次需人工核对飞书实际入库数（--filter-json 按新闻日期查询）
6. **8-03 遗留 1293 条重复待清理**（本地仅 74 条；8-10 已全表清理至 539 唯一，8-11 已修复去重查询，后续正常）

### 官方源中文化
- fetch_us_official.py 白宫/国务院输出全英文 → **必须 agent 翻译补 title_zh/summary_zh**（本次补 18+4 条）
- 无中文校验：`any('\u4e00'<=c<='\u9fff' for c in title)` 遍历 us-official.json 与 news-data.json

### WSJ 反爬
- wsj.com 需 JS 无法 WebFetch → 用 WebSearch site:wsj.com + 第三方引用获取**真实 URL**（绝不编造 URL）；RSS 是 2025 缓存不可用
- **8-11 反爬升级**：/world、/news/world、sitemap、RSS 全被 DataDome captcha 拦截 → 仅能 WebSearch 确认新闻内容；重大新闻（如苹果测试长鑫CXMT）用第三方转载真实 URL（finwire.io）收录，source 仍标华尔街日报
- 本次获 4 篇真实 URL（乌克兰安全保障 a79336dc / 金属废料 e2d38838 / 爱国者社论 e60b223f / 15年安保 e9d3acc1）

### 官方源中文化补充（8-11）
- **HTML 实体坑**：国务院声明标题含 `&#8217;/&#8220;`（如黄岩岛声明），翻译匹配前须先 `html.unescape()`
- war.gov 每日有实质新条目（演讲/声明类优先收录），USTR/商务部无新内容时保留既有条目

### 国内新闻看板 V5 重构（2026-08-10）

#### 关键决策
- **删除使领馆动向类别**：用户表示后续另起炉灶，V5 不再收录大使任免/递交国书/驻华使馆动态
- **分类 8→7 类**：元首动态/高层动态/重要会议/人事任免/部委动态/政策发布/经贸动向
- **部委聚焦 5 部委**：网信办/工信部/发改委/商务部/外交部（删除教育部/科技部/财政部等扩展部委）
- **视觉重构**：红色政府风 → 蓝色专业风（#2563eb）+ 透视表式日期×类别交叉筛选
- **直接替换旧版** china-news.html（不保留旧版并行）

#### 修改文件
- `scripts/fetch_china.py`: v4→v5，删除 EMBASSY_KEYWORDS/fetch_wechat()/MFA_DSRM，BUWEI_KEYWORDS 精简
- `scripts/build_china.py`: 完全重写，CSS 红色→蓝色，新增透视表交互
- `refresh_china_news.sh`: 更新注释和 commit message
- 自动化 `automation-1785577010192`: prompt 更新为 4 层补强 + LLM 后处理

#### 备份
- `scripts/fetch_china.py.bak-v4`
- `scripts/build_china.py.bak-red`

#### 自动化 Prompt 关键要点
- 需包含 4 层 AI 补强：xwlb / tencent-news / toutiao-hot-news / wechat-article-search
- LLM 后处理 4 步：分类复核/质量检查/摘要补全/去重
- 明确禁止收录：使领馆内容、学习活动类报道、评论栏目、地方琐事
- 并发执行防护：提醒不要与自动化系统同时跑 refresh_china_news.sh

### V5.3 赋分机制调整（2026-08-10）

#### 分值变更
- 反贪腐人事: 86→87 | 一般任免: 85→86 | 一般部委: 78→85
- 外交部全栏目监控（7子栏目: 5高+2低，驻外报道不收录）
- 商务部全栏目监控（6子栏目，首页聚合）

#### 中国政府网·要闻 boost（核心规则）
无论分类到何类目，自动取该类最高分一档：
元首100/高层95/会议88/人事87/部委88/政策80/经贸85
实现方式：`make_item()` 内置 `GOV_BOOST` 字典，`max(score, boost_score)`

#### 联合早报微观过滤
新增 `ZAOBAO_MICRO_PATTERNS` + `is_zaobao_micro()`:
- 大学/医院层级人事案件（"大学院长"/"医院被查"）
- 地方城管/执法事件（"城管"/"协管员"）
- 台湾地方政治（"台湾经济部长"/"电价民生"）
在 `make_item` 中 source=="联合早报" 时优先执行过滤

### V5.4 每日刷新补充经验（2026-08-11 固化）

#### AI 补强通道状态（4 层）
- **xwlb**：hotspot.api4claw.com TLS 握手失败（curl/urllib/WebFetch 全挂）→ 第三方服务故障，失败时如实记录不编造
- **tencent-news**：CLI 已装 `~/.tencent-news-cli/bin/tencent-news-cli`，但 **API Key 未配置**（需人工访问 news.qq.com/exchange?scene=appkey 获取后 `apikey-set KEY`）→ 待用户配置
- **toutiao-hot-news**：正常，top20 获取（`python3 -c` 直接调 hot-board API，limit 可改 20）
- **wechat-article-search**：正常，依赖 cheerio 已装至 `~/workbuddy/binaries/node/workspace/node_modules`（NODE_PATH 指定）

#### LLM 后处理手动流程（脚本后必做）
1. 先看今日新增 → 删个人叙事/评论稿/文化专栏（北戴河副教授/每日读画/经济评论）
2. 跨信源查重：联合早报 vs 央视同事件（藏南标准名称）→ 删联合早报版保留央视权威版
3. 同事件多信源：gov.cn 要闻 85 分版 vs 发改委通知 80 分版 → 保留 gov.cn 要闻版
4. 分类修正：受贿判刑属人事任免（反贪腐87）非经贸动向
5. 缺摘要：优先 `urllib` 抓页面 meta description 真实摘要；页面不可达（外交部 SSL）用事实概括
6. 补强缺口：微信搜索发现的部委要闻（脚本首页解析常漏）→ WebSearch 拿官方 URL → curl 验证 200 → 按真实日期补充

#### 已解决问题
- 外交部高优先 5 栏目 0 条 ≠ 故障：先 curl 验证栏目页最新文章日期，无新文即正常
- 网信办/工信部首页 JS 渲染 → 经常 0 条 → 依赖 AI 补强通道弥补
