# 上下文压缩摘要 · 国际/国内/AI/使领馆 看板维护（截至 2026-09-17 15:00）

> 用途：长对话上下文压缩件。后续接手只需读本文件 + `.workbuddy/memory/boards/*.md`，无需回溯全部聊天。

## 1. 项目坐标
- 主项目：`/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50`（国际/国内/使领馆 + 门户）
- AI 看板：`/Users/xiaoxiao/WorkBuddy/2026-08-01-14-08-40`
- 线上：https://iranorawahaha.github.io/international-news-kb/ （仓库 Iranorawahaha/international-news-kb）
- 代理：`127.0.0.1:7890`（git push / 境外抓取失败时必用）
- 自动化：9:30 抓取 → 10:30《信息日报》PDF 邮件（仅发 2027674540@qq.com）

## 2. 本轮（9-17 下午）已完成项
| # | 事项 | 落地 |
|---|---|---|
| 1 | 转载类信源清理 | 剔 163/sohu/so.html5.qq.com 共 6 条；空源补官方一手链接；黑名单 7 域（hongkongdaily/gzylhyzx/wx.laserfair/toutiao/163/sohu/so.html5.qq.com）→ commit ad196ab |
| 2 | 8-30 四看板刷新 | 国际 318 / 国内 38 / AI 406 / 使领馆；线上确认（用户所见"未刷新"为浏览器缓存）|
| 3 | 国内摘要缺失根治 | `fetch_china.py` V5.6：fetch_retry + meta fallback + 段落拼接 160 字 + NAV_NOISE 过滤；修正外交部发布会 URL（`fyrbt_673021`）→ commit 5fa19f7 |
| 4 | 国际板 V1.6 UI | 侧边栏改横向栏目 tab（7 板块 `CATEGORY_ORDER`）；每行加「⧉ 复制要点」（data-clip = 【媒体：标题】\n摘要\nURL）→ commit 7df9c9a |
| 5 | 金融时报补录 + 入信源 | 官网 403 → `r.jina.ai` 取题名/日期 + WebSearch 交叉核实；双写池+存档；FT 登记 config.json → commit e994df8 |
| 6 | 彭博社接入 V2.17 | "登记≠接入"三层断点（config 有登记但抓取清单遗漏 / AUTHORITY_ORDER 缺项 / 7 天窗口滚出）；RSS 5 栏目全通各 20 条；新增 `scripts/fetch_bloomberg_rss.py`；AUTHORITY_ORDER 插「彭博社」于美联社后；信源 11→13 → commit da2cbee |
| 7 | **9-17 版面回填（已完成）** | 彭博社 7 条入 9-17 版面（65→**72**），池 1300→1307；`update-news.sh --auto` 全链路跑通；日报链路**未触碰**（`morning-brief-final.html` 保持 11:35 版）→ commit **736b248**，远端 main = 736b248 ✅，线上 200 / 485320B，彭博社命中 21 处、9-17 日期 99 处 |

## 3. 关键技术事实（避免重复踩坑）
- **彭博社**：官网恒 403（Cloudflare）；RSS `https://feeds.bloomberg.com/{politics|technology|economics|markets|industries}/news.rss`（走 7890）可用；URL 自带 `/YYYY-MM-DD/` 日期路径；RSS 摘要仅 1 句 → 用 `https://r.jina.ai/<url>`（走代理）可拿正文前 2–4 段（实测 HTTP 200，约 17KB），用于写中文摘要。
- **FT**：官网 403 + 付费墙，通道同上（r.jina.ai + WebSearch 转述）。
- **摘要提取**：meta description / og:description 多 pattern fallback > 单段落正则；内联 HTML 标签要剥离。
- **归档规则（V2.11）**：版面 X 日 = `collectedAt == today` 的新抓内容；`date` 仅作真实发布日显示；`date < 昨天` 的条目会被移回旧版面 → 回填时 date 必须是今天或昨天。
- **同题合并**：`AUTHORITY_ORDER = 白宫>国务院>USTR>财政部>商务部>国防部>路透社>美联社>彭博社>BBC>CNN>华盛顿邮报>纽约时报>华尔街日报>卫报>半岛>南华早报>Politico`，标题相似度 ≥0.68 时保留更权威者。
- **板块/栏目**：`scripts/intl_sector.py` 每日对今日版面重跑（P2 AI·科技 → P1 中美博弈 → P3 涉台港/出访 → P6 冲突 → P4 欧加日韩 → P5 美国 → P7 全球多边）；`column` 字段国际模板已不渲染。
- **部署链路**：`update-news.sh --auto`（第3步整合 → 第4步 HTML → 第5步飞书 → 第6步 commit+push+构建健康检查）。

## 4. 待办 / 遗留
- ⚠️ **路透转载替换（未完成）**：用户给了两条官网原文（月之暗面港股 IPO、美车企联盟游说禁中国车）要求核验替换看板及日报 URL —— 当时因模型报错中断，尚未执行。
- ✅ 9-17 版面回填已完成并上线（见 §2 第 7 项），无需重跑。
- 日报规则：**仅发 2027674540@qq.com**；用户对话中审阅确认后再发；不收使领馆板块。
- `git push` 偶发 `.git/index.lock` / `refs/remotes/origin/main.lock` 残留 → 判定口径：`lsof` 无持有者 + mtime 滞后 > 20 分钟即可安全 `rm -f`；推送后若 `git status` 仍显示未同步，先 `git ls-remote origin main` 核实远端真实哈希，再 `git update-ref refs/remotes/origin/main <hash>` 修正本地缓存。

## 5. 用户硬性偏好（复述给未来会话）
- 严格日期归类（X 日版面 = X-1 日 9:30 → X 日 9:30 抓取窗口；迟到抓取归实际抓取日）。
- 国际板全员英文权威源，禁中文信源与自媒体；双语标题 + 中文摘要 + 中文摘要要"详尽"。
- 改动前先给中英对照/前后对比表 + 版本号，确认后再执行；bug 复发要根因诊断 + 经验固化。
- 交付用 present_files + 结构化总结；线上链接带 `?ts=` 防缓存。
