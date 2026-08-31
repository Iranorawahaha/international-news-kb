# Ira 信息看板体系 - 项目记忆

## 项目总览
- 仓库: github.com/Iranorawahaha/international-news-kb（单仓库 4 看板）；Pages: https://iranorawahaha.github.io/international-news-kb/
- Python: /Users/xiaoxiao/.workbuddy/binaries/python/versions/3.13.12/bin/python3
- 推送坑: 本地 git 配 http.proxy=127.0.0.1:7890 常无服务 → 先用 `nc -z 127.0.0.1 7890` 探测，不通 `open /Applications/ClashX.app`；代理通时 plain `git push`，禁代理直连 github 会超时
- 与其他看板自动化并发写同一仓库，push 前 `git add` 精确文件（HTML×N + JSON）；出现 "Everything up-to-date" 用 `git ls-remote origin main` 核对
- 线上 CDN 有 ~30s 延迟，验证 curl 带 `?t=$(date +%s)`；WebFetch 有 15min 缓存勿用于即时验证

## 看板1 国际新闻（V2.12）
- 11 英文源全必选（路透/BBC/SCMP/卫报/CNN/NYT/WSJ/半岛/Politico/WaPo/AP）；彻底排除中文信源与自媒体；黑名单含 cnnbc.com/cnnbc.cn 仿冒域
- ⚠️ 交叉验证防遗漏（V2.12）：WebFetch 后必做 3 组 WebSearch（freshness=d2）兜底——①`China AI chips export controls 1260H CXMT YMTC` ②`US China tariffs sanctions announcement` ③`AI export control remote access compute China The Information`；命中立即补录重跑
- The Information/SemiAnalysis=重点主题补充源（AI芯片/出口管制/远程算力必查），付费墙用 WebSearch 转载 URL，source 标 The Information
- 路透双频道：重大日补抓 /technology 与 /business（涉华重大常在 business/legal 频道）
- 官方源（白宫/国务院/USTR/财政部/商务部/国防部）必须翻译补 title_zh/summary_zh，日期用页面真实发布日；WSJ 反爬用 WebSearch 拿真实 URL（绝不编造）
- ⚠️ fetch_us_official.py 源组丢失坑：某源失败时整组被覆盖丢失 → 运行后必检 us-official.json 是否含全部 6 源，缺失则 `git show <昨日commit>:data/us-official.json` 恢复
- ⚠️ 环境代理双刃剑：全局 HTTP_PROXY=7890 存在；官方源失败先 `env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY curl` 测直连
- 飞书永久存档 A2fdb93HLamcKgslr2rcopjRnfd（表 tblCocvO66XoPsm1）；同步 record-batch-create 25 条/批；字段选项缺失整批失败（800030005）先 field-update 补选项，type 传字符串 "select"
- 更新 `./update-news.sh`；单文件 HTML 架构（CSS/JS 内联防 404）

## 看板3 AI 动向（V5，automation-1785566963833）
- ⚠️ 唯一正式链路（禁改）：`bash /Users/xiaoxiao/WorkBuddy/2026-08-01-14-08-40/refresh_board.sh` → 同目录 `build_v2.py` → 部署到 KB_DIR/ai-news.html + ai-company-intel.html（双写）→ inject_nav → 门户统计 → push
- ❌ 禁止 update-ai.sh/fetch_ai.py/build_ai.py/KB_DIR scripts/build_v2.py（旧链路数据量小会覆盖正式版）；build_ai.py+ai_template.html 废弃边缘链路
- 渲染自检：refresh_board.sh 内嵌 check_render.js（jsdom），失败自动中止
- 顶部透视表 V5 锁定：日期在左/行业·模型·技巧在上/中间仅数字/0 值 `–`/今日行高亮/点击跳转；❌ 严禁回退 V4 胶囊版（emoji 豆腐块+英文标签被投诉）
- 15 家重点公司（NVIDIA/AMD/Intel/Apple/Amazon/MS/Google/Meta/OpenAI/Anthropic/xAI/DeepSeek/华为/字节/阿里/腾讯）

## 看板2 国内新闻（V5.5，automation-1785577010192）
- 入口 china-news.html；`./refresh_china_news.sh`；数据 data/china-news.json
- 7 分类：元首100/高层95/会议88/人事87(反贪腐)/部委88(重大执法)/政策80/经贸85/一般72；gov.cn 要闻 GOV_BOOST 自动取分类最高档
- 排除：学习栏目/数据综述/评论稿/文化专栏/个人叙事/蹲点故事化；联合早报微观过滤（大学医院层级/城管执法/台湾地方政治）；外交部 7 子栏目（驻外不收录）；商务部 6 子栏目
- 透视表 V5：日期在左/分类在上/中间仅数字/0 值 `–`/今日行高亮红点/数字+合计+行空白可点击；V4 胶囊版废弃（"太繁复"）
- ⚠️ 删除定位必须精确（8-27 误删教训）：find_by_title 模糊匹配会误删权威版 → 带 source 条件或用 URL 精确匹配；删除前缀勿带引号/全角字符；误删用 `git show HEAD:data/china-news.json` 恢复

## LLM 后处理流程（脚本后必做）
删个人叙事/评论稿/文化专栏/学习栏目/台湾地方政治/数据综述 → 跨信源查重（联合早报 vs 央视留央视；同政策 gov.cn 版优先）→ 分类修正（受贿判刑→人事87；灾情应急→部委88；救灾资金→部委85）→ 缺摘要用 urllib 抓 meta description 真实摘要（禁模板）→ 微信搜索发现漏采补 WebSearch 官方 URL → 唯一键 (title[:30],source)，0 导航残留，标题≥8字 → 发布会报道去重（留人民日报权威版+央视核心版）→ 涉台重大表态（国台办/国安部）靠热榜+微信线索补录

## 邮件日报《信息日报》（8-29 最终版，automation-1786358746788）
- ⚠️ 最终形态=邮件模式（Outlook 友好），❌ PDF 已废弃；❌ 取消使领馆动态板块（skip_diplo: true）；确认环节=WorkBuddy 对话审阅（回复 确认/-N/+标题）
- **仅发 2027674540@qq.com 一个邮箱**（华为企业邮箱网关拦截 QQ SMTP 富 HTML；24 人名单群发不可靠），用户确认后 `send_final_brief.py --to 2027674540@qq.com`；绝不群发；QQ 群发风控约 10 封后 SMTP 被拒需 10min 恢复，6s+ 间隔
- QQ SMTP: smtp.qq.com:465 SSL；中文 From 必须 `formataddr((str(Header('信息日报','utf-8')), SMTP_USER))` RFC2047；主题 `信息日报-{日期}`
- V3.2 排版：报纸刊头（宋体大标+英文副题+红墨双线+红底白字日期徽章）；双标签=独立 table cell+10px 透明间距列（inline span 的 margin 被 Outlook 忽略）；国内亮红 #c8102e → 暗红 #A32D2D（报头双线/日期徽章保留 #c8102e）；国际分类蓝底白字+来源浅蓝；国内按 CAT_ORDER 排序（元首→高层→人事→会议→部委→经贸→政策）
- 可点击卡片：`<a>` 绝不能包 `<table>`（Word 引擎破坏结构）；外层 table/td 边框背景，内层 `<a display:block>` 只包 span 文字
- 必保留：摘要（13px 行距 1.8）+ 原文链接（🔗 完整 URL）；内容块 max-width 700px
- 敏感词清洗已停用（8-29 用户"保留原意"）；回退备份 scripts/send_final_brief.py.bak-20260829-v3
- ⚠️ 国际补录编号坑：用户口语编号与看板序号可能 ±1 → 按标题关键词精确定位 URL

## 使领馆看板 V1.0（automation-1786431384487）
- 入口 diplomatic-affairs.html；青绿主题；模块：人事/领事(沪穗)/访华(部长级以上)/中美互动
- 关键规则：任命≠到任、副本≠国书、抵华≠履职、单方发布≠双方确认
- **预告即收录**（8-18 规则）：官方/权威信源发布的外交预告（访华/任命）立即填入，phase 三态如实标注——upcoming=📅预告/ongoing=🟢进行中/completed=✅已发生；状态流转每次刷新据实更新，会谈成果落地回填 outcomes；信源仅官方渠道（外交部/gov.cn/新华社/央视/人民日报）+权威媒体（路透/共同社），自媒体不收录
- 构建链：fetch_diplomatic.py → build_diplomatic.py → **cp 主目录 HTML → gh-pages 再 inject_nav.py（双份，gh-pages 不会自动同步内容）** → git push
- 访华职级门槛部长级及以上（预告同门槛）；数据窗口过去 72 小时（首次 7 天）；免责声明必须保留页面底部
- 黑名单（转载站全剔除，8-28 用户确认）：hongkongdaily.net/gzylhyzx.com/wx.laserfair.com/toutiao.com/163.com/sohu.com/so.html5.qq.com
- 日报标题用「动态」而非「国名」：visit 条目加 headline 字段（人工写入，fetch merge 可能丢失）

## 4 层 AI 补强通道
- xwlb: 第三方接口连续多日 TLS 失败 → 如实记录不编造；tencent-news: API Key 未配置（需人工获取）→ 跳过标注；toutiao-hot-news/wechat-article-search: 正常（cheerio 在 ~/workbuddy/binaries/node/workspace/node_modules，需 NODE_PATH）

## 用户偏好
- 关注：中美关系 > 经贸制裁 > AI 竞争 > 外交资讯；双语标题/真实日期归档/真实摘要/仅权威信源
- 看板设计：浅色底+蓝色主色调（国内版）、透视表式日期×类别交互、Noto Serif SC、NYT/FT 简约高级风
- 排错后经验固化到 MEMORY.md + 自动化 prompt + skill；重要改动先表格（中英对照+前后对比+版本号）确认再执行

## 待优化
- PWA/RSS/多语言；使领馆 headline 由 fetch/build 自动生成
