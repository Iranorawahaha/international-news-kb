# 📘 Ira 信息看板 · 系统说明

> **Ira 信息看板**（Ira Intel Hub）是一个面向公共及政府事务研究的情报聚合平台，每日 9:30 自动刷新。三大板块覆盖国际政经动态、AI 产业动向、中国国内政治动向。

---

## 🌐 在线访问

| 板块 | 链接 |
|------|------|
| 🏠 **门户首页** | https://iranorawahaha.github.io/international-news-kb/ |
| 🌍 国际新闻看板 | https://iranorawahaha.github.io/international-news-kb/international-news.html |
| 🤖 AI 动向看板 | https://iranorawahaha.github.io/international-news-kb/ai-company-intel.html |
| 🇨🇳 国内新闻看板 | https://iranorawahaha.github.io/international-news-kb/china-news.html |

---

## 📰 三大板块

### 🌍 国际新闻看板

| 项 | 说明 |
|---|---|
| **定位** | 全球权威媒体聚合：中美关系、经贸制裁、地缘政治、外交动态 |
| **数据源** | 路透社 / BBC / 南华早报 / 卫报 / CNN / 纽约时报 / 华尔街日报 / 半岛电视台 / Politico / 华盛顿邮报 / 美联社（11 大英文权威信源） |
| **采集方式** | WorkBuddy WebFetch 远程抓取（每日 9:30 由 AI 任务执行） |
| **核心特性** | 双语标题 · 元首级标注 · 7 天滚动存档 · 顶层日期 Tab 切换 |
| **筛选标准** | 元首级（⭐）优先 · 政务情报风 · 严禁个人账号 / 营销号 / 娱乐八卦 |

### 🤖 AI 动向看板

| 项 | 说明 |
|---|---|
| **定位** | 中外主要 AI 公司动态 + AI 监管/科技博弈 |
| **数据源** | AI HOT 精选资讯 API（aihot.virxact.com） |
| **检索关键词** | 15 家 AI 公司（OpenAI / Anthropic / Google·DeepMind / Meta / Microsoft / NVIDIA / xAI / DeepSeek / 阿里通义 / 字节豆包 / 腾讯混元 / 智谱GLM / 华为 / Kimi·月之暗面 / MiniMax·海螺）+ 8 组监管/博弈关键词 |
| **分类** | 行业动态 / 模型发布 / 产品发布 / 论文研究 / 技巧观点 |
| **核心特性** | 关键词高亮 · 今日新增标识 · 6 大分类 tab · 政务情报风 |

### 🇨🇳 国内新闻看板

| 项 | 说明 |
|---|---|
| **定位** | 中国国内重要政治动向 + 重大经贸政策：元首及政治局常委动态、重大会议、人事任免、政策发布、经贸动向 |
| **数据源** | **国家级权威信源（5 路）** |
| · 中国政府网·要闻 | `https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json`（习近平/李强/常委动态、通令） |
| · 中国政府网·最新政策 | `https://www.gov.cn/zhengce/zuixin/ZUIXINZHENGCE.json`（国务院文件、规划、批复） |
| · 央视新闻 | `https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/china_1.jsonp`（500 条实时国内要闻） |
| · 人民日报 | `http://paper.people.com.cn/rmrb/pc/layout/.../node_01~04.html`（头版 + 要闻版） |
| · 凤凰新闻 | `https://news.ifeng.com/`（严格过滤，仅采纳时政/经贸，剔除标题党） |
| **采集方式** | 官方 JSON/JSONP 接口 + 版面 HTML 解析（公开，无需鉴权） |
| **核心特性** | ⭐ 元首级高亮 · **7 大分类 tab** · 7 天滚动 · 每条含摘要/日期/媒体 |
| **分类标签（V3.2）** | 👑 元首动态（仅习近平）/ 🧭 高层动态（政治局常委+委员）/ 🏛 重要会议 / 📋 人事任免（中央到地方）/ 🏢 部委动态 / 📜 政策发布 / 💹 经贸动向（**无"其他"类**，未命中即剔除） |

---

## 🛡️ 信源筛选标准（严格白名单）

### 国家A级权威信源（可直接采信）

| 信源 | 网址 | 适用板块 |
|------|------|----------|
| 路透社 | reuters.com | 国际 |
| BBC News | bbc.com | 国际 |
| 南华早报 | scmp.com | 国际 |
| 卫报 | theguardian.com | 国际 |
| CNN | cnn.com | 国际 |
| 纽约时报 | nytimes.com | 国际 |
| 华尔街日报 | wsj.com | 国际 |
| 半岛电视台 | aljazeera.com | 国际 |
| Politico | politico.com | 国际 |
| 华盛顿邮报 | washingtonpost.com | 国际 |
| 美联社 | apnews.com | 国际 |
| **中国政府网** | **gov.cn** | **国内** |
| **央视新闻** | **news.cctv.com** | **国内** |
| **人民日报** | **paper.people.com.cn** | **国内** |
| **凤凰新闻** | **news.ifeng.com**（严格过滤） | **国内** |
| AI HOT | aihot.virxact.com | AI |

> ℹ️ **国内看板说明**：新华社（xinhuanet/news.cn）因页面为静态缓存（数据陈旧）未接入，其核心内容已被 gov.cn 要闻频道覆盖；凤凰新闻为商业媒体，仅采纳时政/经贸类且通过 12 条红线 + 黑名单严格过滤（首页大量"爆仓/炼金/盗墓"类猎奇标题会被剔除）。

### 12 条强制红线（绝不可碰）

1. ❌ 任何营销号 / 自媒体 / 公众号转载
2. ❌ 个人账号（推特/X、微博、知乎等非认证账号）
3. ❌ 娱乐明星 / 八卦 / 绯闻 / 追剧 / 综艺 / 演唱会
4. ❌ 养生 / 偏方 / 减肥 / 祛痘 / 神医
5. ❌ 风水 / 星座 / 生肖运势
6. ❌ 带货 / 促销 / 打折 / 秒杀 / 福利 / 抽奖
7. ❌ 标题党（震惊 / 万万没想到 / 看完沉默了 / 重磅内幕 / 独家爆料 / 小道消息）
8. ❌ 转载娱乐小道 / 娱乐圈
9. ❌ 未经官方信源交叉验证的"独家""爆料"
10. ❌ 缺乏 URL 的二手转载
11. ❌ 社交平台匿名爆料
12. ❌ 任何非白名单的中文自媒体（所有中文新闻必须来自 gov.cn）

### 国内新闻自动化过滤规则（`scripts/fetch_china.py`）

```
JUNK_KEYWORDS = [
    "震惊", "太可怕", "万万没想到", "看完沉默了", "重磅内幕", "独家爆料", "小道消息",
    "娱乐圈", "明星", "八卦", "绯闻", "吃瓜", "剧透", "演唱会", "票房", "综艺",
    "带货", "促销", "打折", "秒杀", "福利", "抽奖", "养生", "偏方", "神医",
    "风水", "星座", "生肖运势", "减肥", "美白", "祛痘",
]
```

**重要度分级**（自动）：
- ⭐ 元首级（score=100）：习近平 / 国家主席 / 中央军委 / 总书记
- ⭐ 常委级（score=95）：李强 / 赵乐际 / 王沪宁 / 蔡奇 / 丁薛祥 / 李希
- 🔴 重要会议（score=88）：全会 / 座谈会 / 集体学习
- 🟠 人事任免（score=82）：任免 / 任命 / 担任
- 🟢 政策发布（score=80）：印发 / 规划 / 条例 / 规定
- 💹 经贸动向（score=72~85）：涉中央/国务院层面的经贸政策 85 分，一般经贸动向 72 分

**经贸动向关注范围**（新增话题）：
- 宏观经济：经济增长 / 经济形势 / 宏观政策 / 扩内需 / 促消费 / 稳增长 / 新质生产力 / 高质量发展
- 财政金融：央行 / 财政 / 金融监管 / 货币 / 汇率 / 人民币 / 税收 / 减税
- 外贸外资：贸易 / 关税 / 进出口 / 外贸 / 外资 / 供应链 / 自贸区 / RCEP / WTO / 一带一路
- 产业市场：产业 / 制造业 / 电力市场 / 能源市场 / 粮食安全 / 营商环境 / 市场监管
- 中美经贸：中美经贸 / 商务部回应 / 涉疆法案 / 实体清单 / 制裁

---

## 🔄 自动化机制

### 每日 9:30（北京时间）三个自动任务并行运行

| 任务 | 自动化 ID | 工作目录 | 命令 |
|------|-----------|---------|------|
| 🌍 国际新闻 | automation-1785570574791 | 国际新闻看板仓库 | `update-news.sh --auto` |
| 🤖 AI 动向 | automation-1785566963833 | AI 看板仓库 | `refresh_board.sh` |
| 🇨🇳 国内新闻 | automation-1785577010192 | 国际新闻看板仓库 | `refresh_china_news.sh` |

### 防护机制

| 防护点 | 实现 |
|--------|------|
| JS 语法自检 | build_v2.py / build_china.py / build_china 内置 `node --check`（防 tbody 空白事故） |
| 构建健康检查 | update-news.sh 推送后调用 GitHub Pages API 校验 `built/errored` |
| 双通道门户更新 | 统计/日报分通道注入，互不覆盖 |
| 数据 schema 统一 | normalize_schema.py 标准化字段 |

---

## 📦 仓库结构

```
international-news-kb/
├── index.html                          # 门户（Ira 信息看板）
├── international-news.html             # 国际新闻看板
├── ai-company-intel.html               # AI 动向看板
├── china-news.html                     # 国内新闻看板
├── data/
│   ├── news-data.json                  # 国际新闻（7 天滚动）
│   ├── china-news.json                 # 国内新闻（7 天滚动）
│   ├── webfetch.json                   # WebFetch 当日数据
│   └── .feishu_config                  # 飞书凭证（已 gitignore）
├── scripts/
│   ├── fetch_china.py                  # 国内新闻抓取（gov.cn）
│   ├── build_china.py                  # 国内新闻构建
│   ├── update_portal_stats.py          # 门户统计更新器
│   ├── daily_brief.py                  # 今日日报生成器
│   ├── inject_nav.py                   # 统一导航注入
│   ├── check_js_syntax.py              # JS 预检
│   ├── normalize_schema.py             # 数据标准化
│   ├── fetch_news_v3.py                # 国际新闻配置
│   ├── data_converter_v12.py           # 数据处理
│   └── sync_to_feishu.py               # 飞书同步
├── update-news.sh                      # 国际新闻刷新
├── refresh_china_news.sh               # 国内新闻刷新
├── inject_nav.py …                     # 共享工具
└── README.md                           # 项目说明
```

---

## 🔒 安全说明

- 飞书凭证（`data/.feishu_config`）已加入 `.gitignore`，不再入库
- ⚠️ 历史旧 commit 中仍残留旧 token，建议轮换飞书 base token
- 仓库为 public，但 sections 已不含敏感信息

---

## 📐 设计原则

1. **权威优先**：所有信源均为国家或国际级权威媒体；国内仅采信 gov.cn
2. **零营销**：12 条强制红线 + 自动化黑名单过滤
3. **零文娱**：明示拒绝娱乐八卦、养生星座、标题党
4. **来源可溯**：每条新闻包含原始 URL，点击直达发布机构
5. **隐私保护**：国内新闻看板仅采用公开发布的官方 JSON 接口，无任何爬虫/抓取行为
6. **仅供参考交流**：所有内容仅供个人研究学习使用，不构成决策依据

---

## 📜 版本历史

| 版本 | 日期 | 关键变化 |
|------|------|----------|
| **V1.3** | 2026-08-01 | 新增国内新闻看板（gov.cn 权威信源）+ 三大门户集成 + 今日日报多板块 |
| V1.2.3 | 2026-08-01 | 全英文必选版国际新闻 |
| V1.2 | 2026-07-31 | 7 天滚动 + 日期 Tab + 飞书存档 |
| V1.0 | 2026-07-29 | 初版：国际新闻双语 + 元首级标注 |

---

## ✉️ 反馈

- GitHub: https://github.com/Iranorawahaha/international-news-kb
- 由 WorkBuddy 自动构建维护

**信赖来源 · 严谨筛选 · 仅供参考交流** 🤝
