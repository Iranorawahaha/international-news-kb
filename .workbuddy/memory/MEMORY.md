# Ira 信息看板体系 - 项目记忆

## 项目总览
- **仓库**: github.com/Iranorawahaha/international-news-kb（单仓库承载 4 看板：国际/国内/AI/使领馆）
- **Pages**: https://iranorawahaha.github.io/international-news-kb/
- **推送坑**: 本地 git 配置了 http.proxy=127.0.0.1:7890 但常无服务 → 用 `git -c http.proxy= -c https.proxy= push origin main`
- **Python**: /Users/xiaoxiao/.workbuddy/binaries/python/versions/3.13.12/bin/python3

## 看板1 国际新闻 (V1.2.3)
- 入口根目录；11 英文信源全必选（路透/BBC/SCMP/卫报/CNN/NYT/WSJ/半岛/Politico/WaPo/AP）
- 飞书永久存档 https://my.feishu.cn/base/A2fdb93HLamcKgslr2rcopjRnfd（表 tblCocvO66XoPsm1）
- 更新 `./update-news.sh`；单文件 HTML 架构（CSS/JS 内联防 404）
- 官方源（白宫/国务院/USTR/财政部/商务部/国防部）必须 agent 翻译补 title_zh/summary_zh，日期用页面真实发布日
- WSJ 反爬：WebSearch 拿真实 URL（绝不编造）；重大新闻可用第三方转载真实 URL（finwire.io），source 仍标华尔街日报

## 看板3 AI 动向（V5，每日 9:30 自动化 automation-1785566963833）
- **⚠️ 生产路径**（2026-08-18 锁定，禁止改用其他脚本）：
  `bash /Users/xiaoxiao/WorkBuddy/2026-08-01-14-08-40/refresh_board.sh` → 该目录 `build_v2.py` → ai-company-intel-board.html → 部署到 `KB_DIR/ai-news.html` + `ai-company-intel.html`（双写）→ inject_nav → 门户统计 → git push
- 模板：`_table_ui_template.html`（KB_DIR/scripts/，与国内共用）
- 渲染自检：refresh_board.sh 内嵌 `check_render.js`（jsdom 真实渲染），检查 pivot-cell 带 data-date/data-cat 等 5 项，**失败自动中止部署**
- 顶部透视表 V5（2026-08-18 锁定）：日期在左 / 行业·模型·技巧 / 中间仅数字 / 0 值 `–` / 今日行高亮 / 点击跳转到对应日期区块（scrollIntoView + flash 高亮）
- 15 家重点公司（NVIDIA/AMD/Intel/Apple/Amazon/MS/Google/Meta/OpenAI/Anthropic/xAI/DeepSeek/华为/字节/阿里/腾讯）
- 数据来源：AI HOT 33 组关键词 selected+all 双流（数据量 380+，比废弃链路 fetch_ai.py 的 270 多）

## ⚠️ AI 看板防回退铁律（2026-08-18 踩坑 3 次换来的）
- ✅ **唯一正式链路**：`refresh_board.sh`（2026-08-01-14-08-40 目录）→ `build_v2.py`（同目录）→ ai-news.html
- ❌ **禁止**跑 `update-ai.sh` / `fetch_ai.py` / `build_ai.py` / KB_DIR `scripts/build_v2.py`（旧链路数据量小会覆盖正式版；改这些脚本无效）
- ❌ **build_ai.py + ai_template.html 是废弃边缘链路**（数据 274 条 vs 生产 382 条；模板未与生产 CSS 同步）—— 别再改这个
- ❌ **严禁回退 V4 胶囊式透视表**（图标+英文+数字横排）—— 曾因 emoji（⚖️🏗️💡）在 macOS 渲染成豆腐块 + 英文 industry/ai-models/tip 被用户投诉
- ✅ **V5 透视表已锁定**为唯一版本：日期在左、分类在上（行业/模型/技巧 2 字短名）、中间仅数字、0 值 `–`、今日行高亮
- ✅ **改动前必读**：自动化 prompt `automation-1785566963833` 已锁定 V5 设计规范 + 自查项；改动后跑 `bash refresh_board.sh` 端到端验证 jsdom 自检通过

## 看板2 国内新闻（V5.5，每日 9:30 自动化 automation-1785577010192）
- 入口 china-news.html；脚本 `./refresh_china_news.sh`；数据 data/china-news.json
- 7 分类：元首100/高层95/会议88/人事87(反贪腐)/部委88(重大执法)/政策80/经贸85(高层信号)/一般72
- **gov.cn 要闻 boost**：make_item 内置 GOV_BOOST，自动取所在分类最高档
- 联合早报微观过滤：大学医院层级/城管执法/**台湾地方政治**（"台湾经济部长"等）
- 排除：看图学习/拾光纪等学习栏目、透过数据/城市更新跑出加速度类综述、评论稿、文化专栏、个人叙事、蹲点故事化报道
- 外交部 7 子栏目（高优先5+低2，驻外不收录）；商务部 6 子栏目；部委聚焦网信办/工信部/发改委/商务部/外交部
- 信源：gov.cn要闻+政策、央视、人民日报、外交部、商务部、发改委、网信办、工信部、联合早报
- **顶部透视表 V5 优化**（2026-08-17，迭代自 V4 胶囊版）：
  - **布局**：日期在左、分类在上、中间仅数字的真·透视表矩阵（`<table class="pivot-table">`）
  - **0 值**：淡化 `–` 代替"—"占位；数字 12px 居中
  - **可点击**：① 数字（日期+分类）② 合计（仅日期）③ 行空白（仅日期）→ 同步顶部日期按钮 + 左侧栏目 + 清空搜索筛选 + 滚动到表格
  - **样式**：今日行浅主题色底 + 红点；hover 行/单元格 浅底；数字 hover 翻转主题色+白字
  - 短名：元首/高层/会议/人事/部委/政策/经贸（国内）/ 产业/模型/技巧（AI）
  - V4 胶囊版废弃（用户反馈"太繁复"）
- V4 胶囊版已废弃（用户反馈"太繁复"），历史记录保留供回溯

## 4 层 AI 补强通道状态
- **xwlb**: hotspot.api4claw.com TLS 握手失败（连续多日第三方故障）→ 如实记录不编造
- **tencent-news**: CLI 已装，**API Key 未配置**（需人工 news.qq.com/exchange 获取）→ 跳过并标注
- **toutiao-hot-news**: 正常（hot-board API top10，线索交叉验证）
- **wechat-article-search**: 正常（cheerio 在 ~/workbuddy/binaries/node/workspace/node_modules，需 NODE_PATH）

## LLM 后处理流程（脚本后必做）
1. 删个人叙事/评论稿/文化专栏/学习栏目/台湾地方政治/数据综述
2. 跨信源查重：联合早报 vs 央视同事件 → 保留央视权威版；同政策 gov.cn 要闻版优先
3. 分类修正：受贿判刑→人事任免(87)非经贸
4. 缺摘要：urllib 抓 meta description 真实摘要；页面不可达（外交部 SSL）用事实概括（禁模板）
5. 微信搜索发现漏采部委要闻 → WebSearch 官方 URL → curl 验证 → 按真实日期补充
6. 唯一键 (title[:30],source)；0 导航残留；标题≥8字符

## 飞书同步（国际看板）
- 补同步必须重新拉飞书全量唯一键；record-batch-create 25 条/批防超时
- 字段选项缺失整批失败（800030005）：先 field-update 补选项，type 必须传字符串 "select"
- 同步后人工核对实际入库数（脚本可能误报成功）

## Outlook 邮件日报（8-13 更新，含两个关键坑）
- 模板：全 table 布局 + 关键样式 inline + 系统字体栈；题头用「报纸刊头」风格（宋体大标居中 + 双线 3px红/1px墨 + 三栏信息条）
- **可点击卡片（Outlook 可靠模式）**：`<a>` 绝不能包 `<table>`（Word 引擎破坏结构 → 整块点击无反应）。正确：外层 table/td 提供边框+背景，内层 `<a style="display:block">` 只包 span 文字/emoji
- **中文发件人显示名**：QQ SMTP 拒绝未编码中文 From（550）→ 必须 `formataddr((str(Header('信息日报','utf-8')), SMTP_USER))` RFC2047 编码
- QQ SMTP：smtp.qq.com:465 SSL；收件人任意域名；发送脚本 send_final_brief.py 支持 `--to` 指定收件人
- 邮件产品名《信息日报》，主题格式 `信息日报-{日期}`（非「Ira 早报」）
- **发送机制已固化**（scripts/send_final_brief.py）：默认 24 人名单 `DEFAULT_RECIPIENTS`（PACD 团队）；`SEND_DELAY=6s` 逐封发送 + 失败自动重试（`RETRY_DELAY=70s` × `MAX_RETRIES=3`）；无 `--to` 时默认发给 24 人
- **QQ 群发风控**：连续发约 10 封后 SMTP 被拒（Connection unexpectedly closed），约 10 分钟自动恢复；务必 6s+ 间隔

## 使领馆看板 V1.0（每日 9:30 automation-1786431384487）
- 入口 diplomatic-affairs.html；青绿主题；"有则展示、无则省略"
- 关键规则：任命≠到任、副本≠国书、抵华≠履职、单方发布≠双方确认
- **预告即收录**（2026-08-18 规则变更，用户明确要求）：官方/权威信源发布的外交预告（访华/任命）一经公布立即填入看板，按预告时间填写，用 `phase` 字段标注三态，绝不等到发生后补录
  - `upcoming`=📅预告 / `ongoing`=🟢进行中 / `completed`=✅已发生（build_diplomatic.py 三态徽标，渲染于人事+访华模块）
  - 状态流转：每次刷新据实更新——预告成行→ongoing，访问结束→completed，会谈成果落地→回填 outcomes
  - 信源门槛：仅官方渠道（外交部/中国政府网/新华社/央视/人民日报）+ 权威媒体（路透/共同社等）；自媒体传闻、无出处小道消息仍不收录
  - 访华职级门槛：部长级及以上（预告同门槛）
- 构建链：fetch_diplomatic.py → build_diplomatic.py（重写 HTML 会去掉导航）→ inject_nav.py 补注导航 → 同步 gh-pages 副本 → git push
- **日报标题用「动态」而非「国名」**（2026-08-18 用户要求）：data/diplomatic-affairs.json 的 visit 条目加 `headline` 字段（如「厄瓜多尔总统诺沃亚对华国事访问（8.16-23）」），send_final_brief.py 的 diplo_row 主标题优先读 headline，fallback `{country} · {event_type}`。⚠️ headline 目前人工写入，fetch_diplomatic.py merge 可能丢失，后续应在 fetch/build 自动生成

## 用户偏好
- 关注：中美关系 > 经贸制裁 > AI竞争 > 外交资讯
- 双语标题（英文资讯）、真实日期归档、真实摘要、仅权威信源禁自媒体
- 看板设计：浅色底+蓝色主色调（国内版）、透视表式日期×类别交互
- 排错后经验必须固化到 MEMORY.md + 自动化 prompt + skill

## 待优化
- 17:00 自动邮件日报（延后）；不可用信源修复；PWA/RSS/多语言
