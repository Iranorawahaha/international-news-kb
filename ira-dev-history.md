# Ira 信息看板 · 全开发历程

> 本文档记录 Ira 信息看板的完整开发过程，涵盖 Prompt、功能、脚本、自动化、设计、经验教训。用于知识传承与后续迭代参考。

**维护者**：小潇（华为公共及政府事务部）
**构建工具**：WorkBuddy AI
**在线地址**：https://iranorawahaha.github.io/international-news-kb/
**仓库**：https://github.com/Iranorawahaha/international-news-kb

---

## 一、项目定位

面向公共及政府事务研究的情报聚合平台。三大板块覆盖国际政经动态、AI 产业动向、中国国内政治动向。每日 9:30 自动刷新，7 天滚动存档。

| 板块 | 定位 | 信源数 | 入口 |
|------|------|--------|------|
| 🌍 国际 | 中美关系、经贸制裁、地缘政治 | 17 家（11 外媒 + 6 美国官方） | `international-news.html` |
| 🇨🇳 国内 | 元首动态、人事、经贸政策 | 5 路国家级权威 | `china-news.html` |
| 🤖 AI | 15 家关键公司动态+监管 | AI HOT 平台 | `ai-news.html` |

---

## 二、核心 Prompt（提供给 AI 的执行指令）

### 2.1 国际新闻收集（fetch_news_v3.py）

```python
# 每个信源对应一个独立 prompt
{
    'url': 'https://www.reuters.com/world/china/',
    'prompt': '提取今天关于中国和国际的重要新闻...列出6条新闻，每条包含：标题（英文原标题+中文翻译）、摘要、关键词、完整URL。⚠️ 新增要求：同时输出 body_en（英文原文正文前1500字）。用中文输出。'
}

# 信源定义（仅11个英文必选）
AUTHORITATIVE_SOURCES = [
    ("Reuters", "https://www.reuters.com/"),
    ("BBC", "https://www.bbc.com/"),
    ("SCMP", "https://www.scmp.com/"),
    ("The Guardian", "https://www.theguardian.com/"),
    ("CNN", "https://www.cnn.com/"),
    ("NYT", "https://www.nytimes.com/"),
    ("WSJ", "https://www.wsj.com/"),
    ("Al Jazeera", "https://www.aljazeera.com/"),
    ("Politico", "https://www.politico.com/"),
    ("Washington Post", "https://www.washingtonpost.com/"),
    ("AP News", "https://apnews.com/"),
]
```

### 2.2 国内新闻收集（fetch_china.py）

```python
# 分类 prompt（内置）
YUANSHOU_KEYWORDS = ["习近平", "国家主席", "中央军委", "总书记"]
MEETING_KEYWORDS = ["座谈会", "全会", "常务会议", "政治局会议", "峰会"]
ECONOMY_KEYWORDS = ["经济", "贸易", "关税", "进出口", "外贸", "外资"]
JUNK_KEYWORDS = ["侧写", "纪事", "读画", "微视频", "vlog", ...]  # 36 词

# 权重系统
GOV_BOOST = {"元首动态": 100, "高层动态": 95, "重要会议": 88,
    "人事任免": 87, "部委动态": 88, "政策发布": 80, "经贸动向": 85}
```

### 2.3 早报系统（send_morning_brief.py）

```python
# 筛选阈值
INTL_MIN_SCORE = 88   # 国际：仅高优先级
DOM_MIN_SCORE = 80     # 国内：权重≥80
```

---

## 三、完整脚本清单

### 3.1 核心采集

| 脚本 | 用途 | 输出 |
|------|------|------|
| `scripts/fetch_news_v3.py` | 11 外媒 WebFetch 配置 | `data/news-webfetch.json` |
| `scripts/fetch_us_official.py` | 6 美国官方源 curl 直连 | `data/us-official.json` |
| `scripts/fetch_china.py` | 5 路国内权威采集+过滤+评分 | `data/china-news.json` |
| `scripts/fetch_ai.py` | AI HOT API 拉取+交叉填充 | `data/ai-news.json` |
| `scripts/fetch_body.py` | 抓取原文全文（urllib 反爬） | `data/article-bodies.json` |

### 3.2 核心构建

| 脚本 | 用途 |
|------|------|
| `scripts/build_china.py` | 国内 HTML 构建（透视表+分类面板） |
| `scripts/build_ai.py` | AI 看板 HTML 构建 |
| `scripts/build_diplomatic.py` | 使领馆动态 HTML 构建 |
| `scripts/data_converter_v12.py` | 国际数据标准化 |
| `scripts/normalize_schema.py` | Schema 统一（STANDARD_KEYS 必须含 is_official/title_zh 等） |
| `scripts/classify_columns.py` | 六大栏目分类器（国际/美国/欧洲/地区热点/国际会议/其他） |
| `scripts/send_morning_brief.py` | 早报生成+QQ SMTP 发送 |

### 3.3 辅助工具

| 脚本 | 用途 |
|------|------|
| `scripts/sync_to_feishu.py` | 飞书 Base 归档 |
| `scripts/inject_nav.py` | 统一导航注入各 HTML |
| `scripts/check_js_syntax.py` | JS 语法预检 |
| `scripts/record_run.py` | 运行日志记录 |
| `scripts/update_portal_stats.py` | 门户统计更新 |
| `scripts/fill_translations.py` | 缺失中文补翻 |
| `scripts/check_missed_runs.py` | 定时检查是否有看板漏跑 |

### 3.4 Shell 调度

| 脚本 | 用途 |
|------|------|
| `update-news.sh` | 国际新闻主流程（官方源→WebFetch→整合→去重→分类→build→推送→飞书） |
| `refresh_china_news.sh` | 国内新闻主流程（fetch→build→gh-pages→push） |
| `refresh_diplomatic.sh` | 使领馆动态流程 |
| `update-ai.sh` | AI 看板流程 |
| `start-server.sh` / `stop-server.sh` | 本地预览 HTTP 服务 |

### 3.5 前端模板

| 文件 | 用途 |
|------|------|
| `scripts/intl_template_v15.html` | 国际看板 HTML 模板（占位符 `__XXX__` 模式） |
| `scripts/morning_brief_template.html` | 早报 HTML 邮件模板（10 个 `{{占位符}}`） |

---

## 四、自动化任务体系

| 自动化 ID | 名称 | 时间 | 命令 |
|------|------|------|------|
| `automation-1785570574791` | 国际新闻看板每日刷新 | 9:30 | `update-news.sh --auto` |
| `automation-1785577010192` | 国内新闻看板每日刷新 | 9:30 | `refresh_china_news.sh` |
| `automation-1785566963833` | AI 动向看板每日刷新 | 9:30 | `update-ai.sh` |
| `automation-1786358746788` | Ira 每日早报（生成+发送） | 10:00 | `send_morning_brief.py --preview → 飞书确认 → --send` |
| `automation-1785719988592` | 看板错过补跑检查 | 12:00 / 17:00 | 检查各看板是否正常刷新 |
| `automation-1786357057388` | fetch_body 双语截图积累 | 每 3 天 | 抓取高优文章原文 |

---

## 五、设计系统

### 5.1 前端设计规范

- **主题**：浅色底 + 蓝色主色调 + 侧浮导航 + 按日期分组 + 黄/红色主题色板头
- **字体**：中文字体优先 Noto Serif SC，正文 PingFang SC
- **风格**：门户简约高级风（NYT/FT 灵感），避免大面积深色/玻璃拟态/渐变
- **前端模板**：外置为独立 HTML 文件（`intl_template_v15.html`），用 `__XXX__` 占位符替换

### 5.2 重要度三级体系（V3）

| 等级 | Pixel 颜色 | 触发条件 |
|------|-----------|----------|
| 🔴 高 | priority_score ≥ 88 | 涉华+重大信号（元首/制裁/芯片/台海） |
| 🟡 中 | ≥ 65 | 涉华常规/台港疆/美欧内政 |
| ⚪ 低 | < 65 | 美伊/俄乌/巴以全部归低 |

### 5.3 早报邮件设计（V8 终版）

- **风格**：报刊门户风（Noto Serif SC 思源宋体）
- **顶部**：一行品牌名 + 深色日期徽章（红底数字）
- **卡片**：白底圆角 + 左侧 3px 色边 + 极浅阴影
- **底部**：三看板跳转卡片 + 14 家信源列表
- **SMTP**：QQ 邮箱（`2027674540@qq.com`），RFC 2047 编码

---

## 六、核心经验教训

### 6.1 官方源字段保留（最高优先级）

> **normalize_schema.py 的 STANDARD_KEYS 必须包含**：`is_official`、`title_zh`、`summary_zh`、`title_en`、`summary_en`、`column`  
> 缺失任何一个，整合时字段被重建丢失 → 看板官方源变英文/模板摘要。

### 6.2 去重权威源顺序

> `update-news.sh` 的 `AUTHORITY_ORDER` **官方源必须排最前**（白宫/国务院/USTR/财政部/商务部/国防部 > 路透/美联社/BBC）  
> 否则官方源被媒体源（同题合并）覆盖。

### 6.3 日期窗口规则（V2.6 终极护栏）

> **X 日栏目 = 实际发布日期 X-1 9:30 ~ X 9:30**
>
> - 国际版：`collectedAt` 为今天但 archive 组不是今天的 → 强制移到今天（`update-news.sh` V2.6）
> - 国内版：`collectedAt` 为今天 **且** `date` 为昨天 → 移到今天（`fetch_china.py` V2.6）
> - 国内版额外限制：更早日期（如 8/5）被重新抓取时不动，防止全量重抓干扰

### 6.4 JS `in` 操作符陷阱

> `'foo' in someString` 会抛 TypeError——`in` 检查对象属性，不是子串搜索。  
> 正确写法：`someString.includes('foo')`

### 6.5 早报邮件链接规则

> **必须用真实 URL**（从 `data/news-data.json` / `china-news.json` 读取）  
> 严禁占位符 URL（如 `https://www.scmp.com` 不带 article 路径）

### 6.6 国内排序安全网

> `build_china.py` V5.4 在渲染前强制按 `priority_score` 降序排列  
> 防止数据在多个修复脚本中被写成未排序状态

### 6.7 美伊冲突浓度控制（V2.7）

> 每日期组内 ≥3 篇纯美伊（无涉华）→ 仅留 top 2 高优，其余降为中优  
> 若美伊 + 中国相关内容（中美伊三方），不触发降维

### 6.8 前端模板外部化

> Python heredoc 内嵌大模板难维护、易语法错（`'''` 三引号冲突）。  
> 国际看板：`intl_template_v15.html`  
> 早报：`morning_brief_template.html`

---

## 七、版本演进速览

| 版本 | 日期 | 关键变化 |
|------|------|----------|
| V1.0 | 7/29 | 初版：国际新闻双语 + 飞书归档 |
| V1.2.3 | 8/1 | 全英文必选版国际新闻（移除中文信源） |
| V1.3 | 8/1 | 新增国内新闻看板 + 三大门户 + 日报 |
| V1.5 | 8/4 | 官方源终极防线（force-upgrade 兜底） |
| V1.7 | 8/5 | 重新分类 + 官方源也走分类器 |
| V2.0 | 8/6 | 元首级→三级重要性体系（高/中/低） |
| V2.5 | 8/7 | V3 重要性重分类 + 日期归档重构 |
| V2.6 | 8/11 | 日期护栏：collectedAt=today → 强制归今天 |
| V2.7 | 8/11 | 美伊浓度控制 top 2 + 国内排序安全网 |
| V5.4 | 8/11 | 国内过滤：侧写/纪事/读画/纯外宣 |

---

## 八、早报确认流程

```
10:00  早报脚本生成预览 HTML
       ↓
       飞书推送给小潇（ou_af83e27f16fe0a9cc57bb4b3458725bb）
       消息含：标题列表 + 操作说明
       ↓
小潇回复「确认」→ 脚本检测 → 发送邮件
小潇回复「删N」→ 调整后再推
小潇回复「+标题」→ 添加后再推
小潇回复「取消」→ 不发送
```

---

## 九、GitHub Pages 部署

- 仓库：`Iranorawahaha/international-news-kb` (Public)
- 推送后 CDN 缓存约 5-10 分钟
- 7 天滚动保留 + 飞书永久存档
- 每次构建后自动 JS 语法预检 + GitHub Pages 健康检查

---

## 十、信源完整白名单

### 国际外媒（11 家）
Reuters · AP News · BBC · CNN · The Guardian · The New York Times · The Wall Street Journal · Financial Times · South China Morning Post · Al Jazeera · The Washington Post · Politico

### 美国官方（6 家）
White House · State Department · USTR · Treasury · Commerce · Defense

### 中国官方与权威（5 路）
中国政府网（要闻 / 最新政策）· 央视新闻 · 人民日报 ·外交部 · 商务部 · 国家发改委 · 联合早报（海外中文权威）

### AI 数据
AI HOT 平台（aihot.virxact.com）

---

_最后更新：2026-08-12 · 由 WorkBuddy 自动构建维护_
