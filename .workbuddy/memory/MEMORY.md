# Ira 信息看板体系 - 项目记忆

## 0 总览
- 仓库 github.com/Iranorawahaha/international-news-kb（单仓库 4 看板）；Pages https://iranorawahaha.github.io/international-news-kb/
- Python `/Users/xiaoxiao/.workbuddy/binaries/python/versions/3.13.12/bin/python3`
- 推送：代理 `127.0.0.1:7890` 常无服务 → 先 `nc -z 127.0.0.1 7890`，不通 `open /Applications/ClashX.app`；多自动化并发写同仓库 → `git add` 只加精确文件，"Everything up-to-date" 用 `git ls-remote origin main` 核对
- 线上 CDN ~30s 延迟，验证带 `?t=$(date +%s)`；WebFetch 有 15min 缓存勿用于即时验证
- 经验固化三处同步：MEMORY.md + 自动化 prompt + skill

## 1 国际新闻看板（V2.15，update-news.sh）
- ⚠️ `--auto` 的 git add **不含** data/news-webfetch.json 与 us-official.json → 收尾必须精确补提交两 pool 文件
- ⚠️ 每日刷新前先试跑：前日新提交可能引入 NameError（09-10 实例：GENERATE_HTML_V12 段 `category_counts` 被误写成 `column_counts` → `set -e` 下 HTML 不生成、后续全断，需手工改回）
- 信源 12 英文全必选（路透/BBC/SCMP/卫报/CNN/NYT/WSJ/半岛/Politico/WaPo/AP/**FT**）；**彻底排除中文信源/自媒体**；黑名单 cnnbc.com / cnnbc.cn
- V2.13 7 板块 L2 归一（仅当日版面生效）；飞书同步前核对 options（缺则映射防 800030005）
- **FT 通道**：官网对终端恒 403 Security Verification（Cloudflare+付费墙），WebFetch/curl 均 failed、archive.today 不可达 → **无自动正文通道**；`https://r.jina.ai/<FT原文URL>` 可拿 Title+Published Time → 路径：r.jina.ai 取标题/日期 → WebSearch 精确匹配找 3+ 转述媒体交叉核实 → 用户浏览器供全文最优。已登记 config.json（id=ft, pri=32）。严禁凭 URL 编造标题/摘要
- **反爬替代通道（fetch_paywall_sources.py）**：路透/WSJ/Politico/WaPo 官网恒 401/403 严禁硬抓 → ①线索：Google News RSS `site: when:2d`；②真实 URL：路透→economictimes/finwire/sedaily/asiae/koreatimes，WSJ→TradingView DJN_DN/finwire，Politico→politico.eu（WebFetch 可用），WaPo→官网(WebSearch)/zetik；③禁低质聚合；转载加 repost_from；窗口内无涉华稿如实空缺
- **V2.15 路透官网 URL**：DataDome 域名级拦截（全路径 401、无代理 000、robots.txt 200 例外）→ **「401=存在」验证法无效**；官网 URL 只取第三方背书（①WebSearch 命中的聚合/转载页列出的 reuters.com 链接，slug 与标题逐字对应 ②用户浏览器提供），禁构造 URL；Yahoo/AOL canonical 带 `tag:reuters.com,2026:newsml_XXX` 可验真。反查 SOP：候选标题→WebSearch 精确变体→命中即换官网 URL 并清 repost_from→miss 落转载；每日固定附「一键搜官网」清单（gen_reuters_recheck_list.py）。`data['today']` 会陈旧，当日取 `dates[0]`
- 交叉验证（V2.12）：WebFetch 后必做 3 组 WebSearch(d2)：①China AI chips export controls 1260H CXMT YMTC ②US China tariffs sanctions announcement ③AI export control remote access compute China The Information
- The Information/SemiAnalysis = 主题补充源（AI芯片/出口管制/远程算力必查）；路透重大日补 /technology /business
- 官方源必补 title_zh/summary_zh（页面真实日期）；WSJ 反爬用 WebSearch 拿真实 URL 绝不编造
- ⚠️ fetch_us_official.py：某源失败整组被覆盖 → 跑后必检 6 源齐全，缺则 `git show <昨日commit>:data/us-official.json` 恢复；失败先 `env -u http_proxy -u https_proxy curl` 测直连
- ⚠️ V2.11.3 窗口校验：webfetch 混入 date<昨天旧报道；collectedAt 须 startswith 前缀匹配；删今日条目四步同步（news-data.json + 根/gh-pages 两 HTML 的 NEWS_DATA + webfetch.json 源头）+ HTML 统计修正
- V2.13.1 程序性白宫文告（Presidential Message/Proclamation on National XX Month|Week|Day）→ `_is_procedural` 不入池 + 评分降权 75
- RSS：SCMP `/rss/4|91|5/feed` 必须 `-L` 跟 301 才 200；WSJ RSS 返 2025-01 旧稿 → 弃用；CNN→edition.cnn.com/world，AP→apnews.com/world-news
- **RSS 兜底清单（本地代理 7890；09-11 扩展）**：BBC feeds.bbci.co.uk/news/world/rss.xml、Guardian theguardian.com/world/rss、AJ aljazeera.com/xml/rss/all.xml、NYT rss.nytimes.com/services/xml/rss/nyt/World.xml、**WaPo feeds.washingtonpost.com/rss/world（+ /rss/business/technology）、Politico politico.com/rss/politicopicks.xml 与 rss.politico.com/politics-news.xml** —— 后两家 RSS 代理直取 200 且带真实官网 URL，免 WebSearch 定位（官网 curl 仍 403/000，但 RSS 内链接可直接上板）
- HTML 重建免全流程：`awk '/^python3 << .GENERATE_HTML_V12.$/{f=1;next} /^GENERATE_HTML_V12$/{f=0} f' update-news.sh > /tmp/gen.py && python3 /tmp/gen.py`，之后仍跑 check_js_syntax.py + inject_nav.py
- 飞书存档 A2fdb93HLamcKgslr2rcopjRnfd（tblCocvO66XoPsm1）25 条/批；选项维护 `+field-get`→append→`+field-update` full PUT，**hue 只能 Gray**（Grey 报 800010701）；单批 ≤200 行，>200 按 date 定向

## 2 国内新闻看板（V5.8，automation-1785577010192，refresh_china_news.sh）
- 权重：元首100/高层95/会议88/人事87/部委88/政策80/经贸85/一般72；gov.cn 要闻 GOV_BOOST 最高档
- 排除：学习栏目/数据综述/评论稿/文化专栏/个人叙事/蹲点故事化；联合早报微观过滤；外交部 7 子栏目；商务部 6 子栏目
- V5.8 硬规则：央视特稿栏目（大国外交最前线/时政新闻眼/平语近人/独家视频/学习卡/传习录/习语）JUNK 硬排；外方主体涉华且无中方主场→不收录；彭丽媛+92 归元首；经贸只留真经贸（招聘/综述剔除，国台办归部委）；词表冲突：JUNK 禁天气灾害词、MEETING「改革委」抢发改委、PSC 禁「全国人大/政协」裸词（用「常委会」）、政策发布禁「规定」「决定」裸词
- 透视表 V5：日期在左/分类在上/数字/0 值 `–`/今日高亮；V4 胶囊版废弃
- ⚠️ 删除定位（8-27 误删教训）：find_by_title 模糊匹配会误删权威版 → 带 source 或 URL 精确匹配；误删 `git show HEAD:data/china-news.json` 恢复
- ⚠️ 外交部栏目 URL：bldhd_674885→wjbxw_674885、zcjd_674887→zcjd、ywdt_674891→sjxw_674887；fyrbt_674889 有效。补录后禁重跑 fetch_china.py（覆盖 AI 补录），只跑 build_china.py + inject_nav + update_portal_stats
- ⚠️ **外事日程 classify 缺口（待 V5.9）**：MFA_WSRC「XX将访华/将访问」预告被 classify()=None 丢弃（卡塔尔首相 9.7-8 漏抓）→ 建议外事日程预置「高层动态95」或加「将访华/将访问/将对中国进行国事访问」
- ⚠️ **mofcom 混入旧文（9-10）**：`xwfyrth`/`bldhd` 列表页混历史旧文，fetch 不校验发布时间 → 9-10 把 08-05「就对美 FCC/DHS 反制答记者问」当新文入池。后处理必须逐条核对「来源/类型/发布时间」，超窗口删
- ⚠️ **xwlb 接口 TLS 故障标准替代（9-10 固化）**：hotspot.api4claw.com 返 000 时用 WebSearch「新闻联播 YYYYMMDD 全文/速览」拿完整节目单+联播快讯 → 比接口更稳，固定纳入补强
- ⚠️ **官方源 curl 不可验时（9-10）**：ccdi.gov.cn 返验证码、nhc.gov.cn 返 412、mfa.gov.cn 栏目层 302 → 改同内容央视 news.cctv.com 文本页 / 新华网 app 页（均 200），source 相应标注

## 3 AI 动向看板（V5，automation-1785566963833）
- ⚠️ 唯一正式链路（禁改）：`/Users/xiaoxiao/WorkBuddy/2026-08-01-14-08-40/refresh_board.sh` → build_v2.py → 部署 KB_DIR/ai-news.html + ai-company-intel.html（双写）→ inject_nav → 门户统计 → push
- ❌ 禁 update-ai.sh/fetch_ai.py/build_ai.py（旧链路会覆盖正式版）；渲染自检 check_render.js（jsdom）失败中止
- 透视表 V5 锁定：日期在左/分类在上/仅数字/0 值 `–`/今日高亮/点击跳转；禁回退 V4
- 15 家重点公司：NVIDIA/AMD/Intel/Apple/Amazon/MS/Google/Meta/OpenAI/Anthropic/xAI/DeepSeek/华为/字节/阿里/腾讯

## 4 使领馆看板 V1.0（automation-1786431384487，refresh_diplomatic.sh）
- 入口 diplomatic-affairs.html；青绿主题；模块 personnel人事/consuls领事(沪穗)/visits访华(部长级+)/us_china中美互动；窗口 72h；页底保留免责声明；visit 加 headline（fetch merge 可能丢）
- 关键区分：任命≠到任、副本≠国书、抵华≠履职、单方发布≠双方确认
- 预告即收录：官方预告填 phase=upcoming/ongoing/completed 三态如实标注，每次刷新流转，成果回填 outcomes；信源仅官方+权威媒体；黑名单 hongkongdaily.net/gzylhyzx.com/wx.laserfair.com/toutiao.com/163.com/sohu.com/so.html5.qq.com
- 构建链：fetch_diplomatic.py → build_diplomatic.py → **cp HTML → gh-pages 再 inject_nav.py（双份）** → push
- ⚠️ 源 URL（9-03 修复）：fmprc.gov.cn/wjdt 旧路径 302 → 改 mfa.gov.cn `web/wjdt_674879/wjbxw_674885/` + `wsrc_674883/` + `fyrbt_674889/`；跑完核对 candidate_count>0；gov.cn/yaowen 已 JS 化 0 链接属正常
- ⚠️ **展会窗口漏抓坑（9-10 固化，9-11 扩展）**：投洽会/进博会/服贸会期间是部长级以上访华高发窗口，但外交部「外事日程」**不预告**「来华出席展会+双边会见」→ 只查外交部会整批漏抓（9-10 一次漏 4 国副总理/外长级）。通道：①WebSearch「韩正/省长 会见 来华出席 投洽会/进博会/服贸会」②新华社/人民日报会见电稿 ③省级政府网/人民网地方频道「会见参加XX会的部分嘉宾」名单页 ④**「丁薛祥/韩正 出席 XX 峰会并会见与会外国政要」一条通稿即含多国政要**（服贸会 9/9 一稿含津巴布韦副总统+保加利亚副总理）⑤中新社各语种展会稿+央视新闻联播。**9-11 新增：同一批政要常「厦门投洽会→北京服贸会」连轴转（保加利亚普列夫两场都到），核验须跨城追踪同一人行程**
- ⚠️ **一手域 URL 强制（9-11 复现）**：source 用黑名单域（so.html5.qq.com / toutiao.com / sohu / 163）会被 build **静默剔除**（日志出现「🗑️ 黑名单信源剔除」）→ 转载稿必须回溯一手域：商务部 `mofcom.gov.cn/syxwfb/art/...`、广东省商务厅 `com.gd.gov.cn/zwgk/gzdt/content/post_XXXX.html`、省外办 `gdfao.gov.cn`。⚠️ 转载稿发布日期≠事件日期（南方+ 9/10 发稿、粤芬交流会实为 9/8）→ 事件日期以主办方通稿为准
- ⚠️ fetch 每轮再生重复候选（王毅同XX会谈：卡塔尔 133160a19803、墨西哥 c377b067ee42）须每轮删；且外方访华会谈常被误标 country=美国 归 us_china，须逐条核验
- 口径边界：中方驻外代表（大使/总领事递交国书副本、履新）不属本板（本板仅「外国驻华大使」）；低于部长级、国际组织负责人、多国使节集体参访均不收录。**9-11 新增两处待用户定夺**：①欧盟驻华代表团团长（大使级、非主权国家）已按模块名「外交代表人事变化」收录 ②挪威国务秘书（副部长级）按「正式双边机制会议+展会主宾国」收录——口径若严守「正部长级」需剔除。**另：官方表述「视频或现场致辞」且无中方会见报道者（如布隆迪总统 9/9 服贸会），无法确认是否来华，不收录**

## 5 邮件日报《信息日报》（automation-1786358746788，send_final_brief.py）
- 形态=**邮件模式**（Outlook 友好，PDF 废弃）；`skip_diplo:true`；确认=WorkBuddy 对话（「确认」/「-N」/「+标题」）；**仅发 2027674540@qq.com，绝不群发**
- SMTP smtp.qq.com:465；From `formataddr((Header('信息日报','utf-8'),SMTP_USER))`；主题 `信息日报-{日期}`；间隔 6s+（约 10 封后触发风控）
- 阈值：国际 ≥88 / 国内 ≥80。override（data/brief-override.json，date=今日才生效）字段：intl_include / intl_exclude_urls / intl_order / intl_custom / dom_include / dom_exclude_urls / dom_order / dom_custom / coverage_note
- ⚠️ 编辑 override 后必须 json.load 校验（Edit 截断 `}` → 脚本静默回退默认配置、条数假象）；国际源可能在生成期间被并发刷新（URL 升级）→ 以「渲染清单核对」为准
- 排版：报纸刊头（宋体大标+英文副题+红墨双线+红底白字日期徽章）；双标签=独立 table cell+8-10px 间距列；国内暗红 #A32D2D / 徽章双线 #c8102e；国际分类蓝底白字；CAT_ORDER 元首→高层→人事→会议→部委→经贸→政策
- 摘要 14px、标题 17px；**必留完整摘要 + 🔗 完整 URL（可复制，不做标题跳转）**
- **永久模板规则**：①开头无引导语块 ②结尾不署「—— 小潇」无任何签名 ③无使领馆板块
- **iOS Outlook 适配终极结论（V3.3.3）**：iOS Outlook 不解析 `<style>`/media query，且把 `max-width` 反解释为「目标宽度」→ **删一切固定宽度/mso ghost/max-width，纯 `width:100%` 流体 + 简单单列 + inline 字号直接 mobile 化（标题17/摘要16/链接14）+ URL 用 word-break 而非 ZWSP**。代价：桌面 Windows Outlook 变全宽
- 备份：send_final_brief.py.bak-20260829-v3 / .bak-20260909-pre-v33 / -pre-v331 / -pre-v332 / -pre-v333
- 常见坑：gov.cn/央视摘要 160-161 字截断「…」→ 生成前必须 WebFetch 原文重写（9-07/9-09 连续复发，建议修 fetch_china.py）；gov.cn 摘要偶含「主办单位/网站标识码」页脚残留须剔除；CCTV URL 含大写需 norm() 匹配；用户「添加了 XX 文章」通常=已手动录入看板池（collection_method=user_provided），先搜池核对再决定 include/custom

## 6 补强通道与用户偏好
- 4 层 AI 补强：xwlb 接口 TLS 失败 → WebSearch 兜底；tencent-news API Key 未配置 → 跳过；toutiao-hot-news / wechat-article-search 正常（cheerio 在 ~/workbuddy/binaries/node/workspace/node_modules，需 NODE_PATH）
- 关注优先级：中美关系 > 经贸制裁 > AI 竞争 > 外交资讯
- 硬性要求：双语标题（中文为主+英文辅）、按**真实发布日**归档、真实摘要（禁模板式「[官方信源] X 发布：{title}」）、导航残留 0、仅权威信源、预告即收录并标注三态
- 设计：浅色底+蓝色主调、透视表式交互、Noto Serif SC、NYT/FT 简约高级风；反对大面积深色/玻璃拟态/渐变
- 工作方式：重要改动先以表格（中英对照+改动前后+版本号）确认再执行；分阶段迭代每次聚焦 1-2 板块；Bug 复发要求根因诊断表；决策果断（全删优于补丁）
