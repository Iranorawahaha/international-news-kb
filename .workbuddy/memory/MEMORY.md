# Ira 信息看板体系 · 项目记忆（索引）

> **⚠️ 开工前必读**：本文件为索引 + 跨看板规则。各看板详细排错规则见 `boards/`：
> - `boards/intl.md` 国际新闻看板 V2.16（update-news.sh）
> - `boards/china.md` 国内新闻看板 V5.8（refresh_china_news.sh）
> - `boards/ai.md` AI 动向看板 V5（refresh_board.sh）
> - `boards/diplo.md` 使领馆看板 V1.0（refresh_diplomatic.sh）
> - `boards/brief.md` 邮件日报《信息日报》（send_final_brief.py）
> 修改任一板块规则时同步更新对应 boards 文件，本索引只留跨板块要点。

## 0 总览
- 仓库 github.com/Iranorawahaha/international-news-kb（单仓库 4 看板）；Pages https://iranorawahaha.github.io/international-news-kb/
- Python `/Users/xiaoxiao/.workbuddy/binaries/python/versions/3.13.12/bin/python3`
- 推送：先 `nc -z 127.0.0.1 7890`，不通则 `open /Applications/ClashX.app`；多自动化并发写同仓库 → `git add` 只加精确文件；"Everything up-to-date" 用 `git ls-remote origin main` 核对
- 线上 CDN ~30s 延迟，验证带 `?t=$(date +%s)`；WebFetch 有 15min 缓存，勿用于即时验证
- 经验固化三处同步：MEMORY.md（+boards/）+ 自动化 prompt + skill

## 1 四看板速查
| 看板 | 版本/自动化 | 关键约束 |
|---|---|---|
| 国际 | V2.16 / update-news.sh | 12 英文源全必选、彻底排除中文信源；路透 URL 首选官方 sitemap-index 直取 |
| 国内 | V5.8 / automation-1785577010192 | 权重 元首100>高层95>会议88/部委88>经贸85>政策80；央视特稿硬排 |
| AI | V5 / automation-1785566963833 | 唯一链路 refresh_board.sh，禁旧链路；15 家公司 |
| 使领馆 | V1.0 / automation-1786431384487 | 部长级+；预告即收录三态；信源仅官方+权威媒体 |
| 日报 | 邮件模式 / automation-1786358746788 | 国际≥88 + 国内≥80；仅发 2027674540@qq.com；无签名无引导语无使领馆 |

## 2 补强通道与用户偏好
- 4 层 AI 补强：xwlb 接口 TLS 失败 → WebSearch 兜底；tencent-news API Key 未配置 → 跳过；toutiao-hot-news / wechat-article-search 正常（cheerio 在 ~/workbuddy/binaries/node/workspace/node_modules，需 NODE_PATH）
- 关注优先级：中美关系 > 经贸制裁 > AI 竞争 > 外交资讯
- 硬性要求：双语标题（中文为主+英文辅）、按**真实发布日**归档、真实摘要（禁模板式）、导航残留 0、仅权威信源、预告即收录并标注三态
- 设计：浅色底+蓝色主调、透视表式交互、Noto Serif SC、NYT/FT 简约高级风；反对大面积深色/玻璃拟态/渐变
- 工作方式：重要改动先以表格（中英对照+改动前后+版本号）确认再执行；分阶段迭代每次聚焦 1-2 板块；Bug 复发要求根因诊断表；决策果断（全删优于补丁）
- ⭐ **综合条目固定动作（9-14 用户拍板"固化为之后综合新闻的固定动作"）**：发现①同一事件多源报道 ②官方「报道+全文」结构 ③同主题多篇关联表态 → 一律合并为 1 条综合条目（国际 `intl_custom` / 国内 `dom_custom`：`category` 定板块 + `priority_score=1000` 置该板块最前 + `items:[{media,title}]` 在标题下罗列各来源 + `urls` 全保留 + 摘要写成一段贯通叙述严禁拼接 + 原条目 URL 入 exclude）。**生成预览时必须主动查重并在汇报中单列"建议综合"**，不等用户提。详见 `boards/brief.md` 与 skill `brief-item-synthesis`

## 3 跨看板高频坑（详见各 boards 文件）
- ⚠️ 摘要 160-161 字截断（gov.cn/央视）→ 生成前 WebFetch 原文重写（9-07/9-09/9-11 连续复发）
- ⚠️ 官方源 curl 不可用时的替代：WebFetch / 同内容央视·新华网页面（ccdi 验证码、nhc 412、mofcom 403、gov.cn JS 化）
- ⚠️ 删除条目一律用 URL 精确匹配（编号/标题模糊匹配会误删）；误删用 `git show HEAD:<file>` 恢复
- ⚠️ 黑名单域（toutiao/163/sohu/qq/hongkongdaily/gzylhyzx/laserfair）会被静默剔除 → 必须回溯一手域
- ⭐ **路透官网 URL 直取（9-15 固化，最新首选）**：`reuters.com/arc/outboundfeeds/sitemap-index/?outputType=xml` → 抓前 10 片 `?outputType=xml&from=0..900`（1000 条含 lastmod）→ slug 词命中率匹配（≥0.6 命中；slug 必须 `rstrip('/')` 后取末段）。无需抓正文，sitemap 收录即 URL 真实存在 → 9-15 路透 10 条全官网、repost_from=0
- ⚠️ RSS 候选标题/URL 禁止手抄（显示按 120 字符截断）→ 脚本从 XML 取 `link`；入库前与 webfetch 池 + archive 全量 URL 去重（AP 头条页会重新露出旧文）
- ⚠️ 官方源窗口判断须回页面核对发布日（脚本 date 解析会误判；9-15 白宫/国务院各 1 条标错）
- ⭐ **外交部栏目清单（9-16 补齐，9-17 增补，跨板通用）**：`wjdt_674879/` 下 **部领导活动 wjbxw_674885**｜**外事日程 wsrc_674883**（访华预告主通道，**且「中方领导人将出席XX多边活动」通稿含多国政要名单，须读正文非只看标题**）｜**例行记者会 fyrbt_674889**｜**司局级新闻 sjxw_674887**（司长会见外国驻华大使/离任辞行 —— 9-16 前缺失，致大使人事整批漏抓）｜礼宾司相关新闻 `wjb_673085/zzjg_673183/lbs_674685/xgxw_674687`（递交国书副本，⚠️ **列表页有滞后**，实际发布域 `mfa.gov.cn/wjbxw_new/YYYYMM/`，须 WebSearch 补查）｜记者会亦有 `fyrbt_673021` 镜像路径。**防长级来华走国防部渠道**（新华社「董军同出席XX论坛客人举行会谈」一稿含多国防长），外交部栏目不覆盖
- ⭐ **「外交部不预告」的部长级访华窗口共 4 类（9-17 补全）**：①展会（投洽会/服贸会/进博会）②多边防务论坛（香山论坛）③多边经贸展会（东博会）④国际科技/专业论坛（浦江创新论坛）。补强三通道：**部委官网 + 省市政府外办 + 来源国官方通讯社/政府新闻网**。「候任大使」类人事同样走来源国官方通讯社（如巴基斯坦 APP app.com.pk）
- ⚠️ **每轮 build 后必查「黑名单信源剔除」计数为 0**（转载稿误用 toutiao/sohu/163 域会被静默剔除，9-06/9-11/9-17 三次复现）；`inject_nav.py` 不带参数一次即处理 root + gh-pages 两份
