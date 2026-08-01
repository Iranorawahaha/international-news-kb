# 🗂️ Ira 信息看板 — 华为公共及政府事务部情报聚合平台

## 🌐 在线地址

| 页面 | 链接 |
|------|------|
| **🏠 Ira 信息看板（门户）** | https://iranorawahaha.github.io/international-news-kb/ |
| 🌍 国际新闻看板 | https://iranorawahaha.github.io/international-news-kb/international-news.html |
| 🤖 AI 动向看板 | https://iranorawahaha.github.io/international-news-kb/ai-company-intel.html |

---

## 📋 系统架构

```
Ira 信息看板（index.html 门户）
├── 🌍 国际新闻看板 (international-news.html)
│   ├── 采集: WebFetch API 11 大英文权威信源（路透/BBC/南华早报/卫报/CNN/NYT/WSJ/半岛/Politico/华盛顿邮报/AP）
│   ├── 整合: update-news.sh（去重/清洗/排序/7天存档）
│   ├── 存储: data/news-data.json（本地7天）+ 飞书 Base（永久）
│   └── 部署: GitHub Pages (main 分支根目录)
└── 🤖 AI 动向看板 (ai-company-intel.html)
    ├── 采集: AI HOT v1 API（15 家公司 + 监管/科技博弈关键词）
    ├── 构建: build_v2.py（分类/高亮/监管标签）
    └── 部署: refresh_board.sh → GitHub Pages
```

## 🔄 自动刷新机制

**每天早上 9:30**，两个任务并行刷新（WorkBuddy Automation）：

| 任务 | 命令 | 说明 |
|------|------|------|
| 国际新闻 | `WebFetch 采集 → bash update-news.sh --auto` | 采集11信源→整合→生成→飞书→推送 |
| AI 动向 | `bash refresh_board.sh` | 抓取 AI HOT→构建→部署→更新门户统计 |

> 手动刷新：`./update-news.sh --auto`（国际新闻，无人值守）／ `./refresh_board.sh`（AI 动向）

## 🔧 关键脚本

| 脚本 | 职责 |
|------|------|
| `update-news.sh` | 国际新闻一键更新（支持 `--auto` 无人值守） |
| `scripts/fetch_news_v3.py` | WebFetch 采集引擎（信源配置/prompt/优先级打分） |
| `scripts/normalize_schema.py` | 数据 schema 统一（历史字段映射） |
| `scripts/inject_nav.py` | Ira 统一导航注入（幂等） |
| `scripts/sync_to_feishu.py` | 飞书 Base 永久存档同步 |
| `refresh_board.sh` | AI 动向看板刷新+部署（位于 2026-08-01-14-08-40 工作区） |
| `build_v2.py` | AI 看板单文件 HTML 构建器 |

## 📁 数据文件

- `data/news-data.json` — 主数据（7天滚动存档，V1.3 统一 schema）
- `data/news-webfetch.json` — WebFetch 当日采集结果（临时）
- `data/.feishu_config` — 飞书凭证（**已被 gitignore，不入库**）

## 🔒 安全说明

- 飞书凭证存储在 `data/.feishu_config`（本地），已从 git 历史移除并加入 `.gitignore`
- ⚠️ 历史 commit 仍残留旧 token，建议轮换飞书 base token

## 📜 版本历史

- **V1.3** (2026-08-01): Ira 统一门户 · 双看板统一视觉 · --auto 无人值守 · 构建健康检查 · schema 统一 · 安全加固
- **V1.2.3** (2026-08-01): 全英文必选版（移除中文信源）
- **V1.2** (2026-07-31): 7天存档 + 日期Tab + 飞书同步
- **V1.1** (2026-07-29): 双语标题 + 元首级标注 + 5级分类

---

*由 WorkBuddy 自动构建维护 · 详情见 docs/ 与 scripts/*.py*
