# 🌍 国际新闻看板 - 每日更新操作手册

> **版本**: V1.0 (正式版)
> **系统名称**: 国际新闻看板 (International News Dashboard)
> **适用场景**: 每日手动更新，每日2次（9:30 + 17:00）
> **最后更新**: 2026-07-31

---

## 📋 目录

1. [快速开始](#快速开始)
2. [完整操作流程](#完整操作流程)
3. [第1步：基础采集](#第1步基础采集中文信源)
4. [第2步：WebFetch补充](#第2步webfetch-api补充高价值英文信源) ⭐
5. [第3步：数据整合](#第3步数据整合与质量验证)
6. [第4步：网页生成](#第4步生成单文件html)
7. [第5步：推送部署](#第5步推送到github-pages)
8. [一键脚本说明](#一键脚本说明)
9. [常见问题](#常见问题)
10. [技术细节](#技术细节)

---

## 🚀 快速开始

### 如果你只有30秒

```bash
cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50
./update-news.sh
```

**输入y/n确认是否包含WebFetch数据 → 完成！**

---

### 如果你有5分钟（推荐）

按照本文档的**完整操作流程**执行，可以获得更高质量的数据。

---

## 完整操作流程

```
┌─────────────────────────────────────────────────────┐
│  🌍 国际新闻知识库每日更新流程                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  第1步: 基础采集 (终端命令)                          │
│    ↓ 采集中文信源（人民网、外交部等）                 │
│    ↓ 预计获得: 10-15条新闻                           │
│                                                     │
│  第2步: WebFetch补充 (WorkBuddy对话中)               │
│    ↓ 获取路透社、BBC、卫报、南华早报                  │
│    ↓ 预计获得: 20-24条高质量新闻                     │
│                                                     │
│  第3步: 数据整合                                     │
│    ↓ 合并去重、质量验证                              │
│    ↓ 预计最终: 25-35条精选新闻                      │
│                                                     │
│  第4步: 网页生成                                     │
│    ↓ 自动生成单文件HTML（内嵌所有数据和样式）         │
│                                                     │
│  第5步: 推送部署                                     │
│    ↓ git push到GitHub                               │
│    ↓ 1-2分钟后网站自动更新                           │
│                                                     │
│  ✅ 总耗时: 3-5分钟                                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 第1步：基础采集（中文信源）

### 操作方式

打开终端，执行：

```bash
cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50

# 运行v3.0增强版采集脚本（仅基础部分）
python3 scripts/fetch_news_v3.py --basic-only
```

### 预期输出

```
🌍 国际新闻知识库 - 增强版采集系统 v3.0

============================================================
📡 第1层：基础采集（中文信源）
============================================================

🔍 [人民网-国际] 正在连接... ✅ 成功 (8 条)
🔍 [中国日报网] 正在连接... ✅ 成功 (6 条)
🔍 [环球网] 正在连接... ✅ 成功 (4 条)
🔍 [国际在线] 正在连接... ✅ 成功 (3 条)
🔍 [中国外交部] 正在连接... ✅ 成功 (4 条)

✅ 基础采集完成：25 条原始素材

⏭️ 跳过WebFetch补充（--basic-only 模式）

🔄 数据合并与质量控制

📊 合并统计:
   - 原始总数: 25 条
   - 去重后: 18 条
   - 基础采集: 18 条
   - WebFetch补充: 0 条

💾 数据已保存: data/news-data.json
   总计: 18 条新闻
📊 报告已生成: data/collection-report.md

✅ 采集完成

📊 最终结果: 18 条新闻
📁 数据文件: data/news-data.json
📊 采集报告: data/collection-report.md
```

### 技术说明

| 项目 | 说明 |
|------|------|
| **使用的库** | Python requests |
| **信源数量** | 6个主要中文信源 |
| **预计获取量** | 10-20条 |
| **内容类型** | 中文新闻（标题+摘要） |
| **优势** | 稳定快速，无需API |

### 可能遇到的问题

#### 问题1：`ModuleNotFoundError: No module named 'requests'`

**解决**：
```bash
pip3 install requests beautifulsoup4
```

#### 问题2：某些信源连接超时

**原因**：网络波动或信源服务器响应慢  
**解决**：正常现象，脚本会跳过失败的信源继续运行其他信源

#### 问题3：SSL证书错误

**解决**：
```bash
# 方法1：忽略SSL验证（不推荐生产环境）
export PYTHONHTTPSVERIFY=0

# 方法2：更新证书（推荐）
pip3 install --upgrade certifi
```

---

## 第2步：WebFetch API补充（高价值英文信源）⭐

### ⚠️ 重要提示

**此步骤必须在 WorkBuddy AI 助手对话环境中完成！**

WebFetch 是 WorkBuddy 的专属功能，可以绕过反爬虫机制访问路透社、BBC等权威英文信源。

### 操作方法

#### 方法A：在当前对话中直接请求（最简单）

直接对我说：

> "请帮我用 WebFetch 补充以下信源的最新新闻：
> 1. 路透社 https://www.reuters.com/world/
> 2. BBC https://www.bbc.com/news
> 3. 南华早报 https://www.scmp.com/news/china
> 4. 卫报 https://www.theguardian.com/international"

我会自动执行并整合数据。

#### 方法B：使用预定义任务列表

我可以读取 `fetch_news_v3.py` 中已配置的 WebFetch 任务列表并逐一执行。

### WebFetch 任务详情

| # | 信源 | URL | 目标数量 | 重点内容 | 优先级 |
|---|------|-----|---------|----------|--------|
| 1 | **路透社** | https://www.reuters.com/world/ | ~8条 | 中美关系、地缘政治、AI科技、经贸制裁 | ⭐⭐⭐ |
| 2 | **BBC News** | https://www.bbc.com/news | ~6条 | AI科技、中美关系、全球政治 | ⭐⭐⭐ |
| 3 | **南华早报** | https://www.scmp.com/news/china | ~6条 | 中国外交、亚太局势、中美关系 | ⭐⭐ |
| 4 | **卫报** | https://www.theguardian.com/international | ~4条 | 全球政治、气候变化、经济危机 | ⭐ |

### 预期输出示例

```
📥 接收 路透社 的数据: 8 条
✅ 路透社 数据已添加

📥 接收 BBC News 的数据: 6 条
✅ BBC News 数据已添加

📥 接收 南华早报 的数据: 6 条
✅ 南华早报 数据已添加

📥 接收 卫报 的数据: 4 条
✅ 卫报 数据已添加
```

### 为什么需要这一步？

| 对比项 | 仅基础采集 | 基础 + WebFetch |
|--------|-----------|-----------------|
| **新闻总数** | 10-18条 | **25-35条** |
| **来源多样性** | 主要中文媒体 | **中英权威媒体全覆盖** |
| **国际视角** | 偏中国视角 | **多角度平衡报道** |
| **高价值内容** | 较少 | **路透社/BBC独家深度报道** |
| **数据质量** | 一般标题 | **100-150字高质量摘要** |
| **覆盖范围** | 中美经贸为主 | **全球热点全覆盖** |

### 如果跳过此步骤会怎样？

❌ **不会导致错误**，但数据质量会降低：
- 新闻数量减少约40%
- 缺少路透社、BBC等顶级国际信源
- 英文权威媒体报道缺失
- 国际视角不够全面

**建议**：只要时间允许，**强烈建议执行此步骤**

---

## 第3步：数据整合与质量验证

### 自动化处理

当你使用 `update-news.sh` 一键脚本时，以下步骤**全自动完成**：

```bash
# 脚本内部执行的逻辑（无需手动操作）
1. 读取 data/news-data.json（包含基础采集 + WebFetch数据）
2. 统计总数量
3. 分析来源分布（哪些信源贡献了多少条）
4. 分析分类分布（中美关系/AI科技/外交等）
5. 分析重要性分布（高/中/低比例）
6. 输出统计报告
```

### 手动验证（可选）

如果想查看详细统计：

```bash
cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50

# 查看采集报告
cat data/collection-report.md

# 快速统计
python3 << 'EOF'
import json
from collections import Counter

with open('data/news-data.json', 'r') as f:
    data = json.load(f)

print(f"📊 总数: {len(data)} 条\n")

print("📰 来源分布:")
for source, count in Counter(n['source'] for n in data).most_common(8):
    print(f"   • {source}: {count} 条")

print("\n📂 分类分布:")
for cat, count in Counter(n['category'] for n in data).most_common(5):
    print(f"   • {cat}: {count} 条")

print("\n⭐ 重要性:")
for level in ['高', '中', '低']:
    count = sum(1 for n in data if n.get('importance') == level)
    print(f"   {level}: {count} 条")
EOF
```

### 预期输出示例

```
📊 总数: 32 条

📰 来源分布:
   • 路透社: 8 条
   • BBC News: 6 条
   • 南华早报: 6 条
   • 人民网-国际: 5 条
   • 卫报: 4 条
   • 中国外交部: 3 条

📂 分类分布:
   • 中美关系: 8 条
   • 国际政治: 7 条
   • AI与科技竞争: 6 条
   • 外交资讯: 5 条
   • 经贸制裁: 4 条
   • 亚太动态: 2 条

⭐ 重要性:
   高: 12 条
   中: 14 条
   低: 6 条
```

### 质量标准检查清单

- [ ] 总数 ≥ 20条（否则数据不足）
- [ ] 高重要性 ≥ 8条（否则重点不突出）
- [ ] 信源 ≥ 4个（否则来源单一）
- [ ] 分类 ≥ 4个（否则覆盖面窄）
- [ ] 包含路透社或BBC（否则缺少国际权威视角）
- [ ] **URL覆盖率 ≥ 95%（否则需要补全缺失的URL）** ⭐新增
- [ ] **所有WebFetch获取的文章都有完整URL（否则需重新抓取）** ⭐新增

> 🔗 **URL完整性说明（2026-07-31更新）**：
> - 每条新闻都应该有可点击的"原文链接"
> - URL必须是完整的文章地址（https://开头），不是首页
> - 如果URL覆盖率 < 95%，说明WebFetch步骤可能遗漏了URL字段
> - **解决方案**：重新执行WebFetch，并在请求中明确要求返回完整URL

---

## 第4步：生成单文件HTML

### 自动化处理

`update-news.sh` 脚本会**自动执行**此步骤：

```bash
# 脚本内部逻辑：
1. 备份旧的 index.html（保留历史版本）
2. 读取最新的 news-data.json
3. 将数据嵌入HTML模板（CSS + JS + 数据全部内嵌）
4. 生成新的 index.html（完全自包含的单文件）
```

### 手动生成（如果需要）

```bash
cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/gh-pages

# 使用Python脚本生成
python3 << 'PYEOF'
import json
from datetime import datetime
from pathlib import Path

DATA_PATH = Path("../data/news-data.json")
OUTPUT_PATH = Path("index.html")

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    news_data = json.load(f)

print(f"📊 读取 {len(news_data)} 条新闻")

# ... （HTML生成代码同 update-news.sh 内嵌逻辑）

print("✅ HTML生成完成")
PYEOF
```

### 生成的HTML特点

| 特性 | 说明 |
|------|------|
| **单文件** | 所有CSS/JS/数据内嵌在一个HTML文件中 |
| **无依赖** | 不需要外部文件路径（解决了之前的404问题） |
| **响应式** | 支持电脑/手机/平板自适应 |
| **功能完整** | 搜索、筛选、排序全部可用 |
| **大小** | 约35KB（24条新闻） |

---

## 第5步：推送到GitHub Pages

### 方式A：使用一键脚本（推荐）

```bash
./update-news.sh
```

脚本会在最后一步**自动推送**。

### 方式B：手动推送

```bash
cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/gh-pages

# 检查更改
git status

# 添加并提交
git add .
git commit -m "📰 更新新闻数据 - $(date +%Y-%m-%d)"

# 推送
git push origin main
```

### 认证信息

推送时会提示输入：

```
Username for 'https://github.com': Iranorawahaha
Password for 'https://Iranorawahaha@github.com': 
```

- **Username**: `Iranorawahaha`
- **Password**: 你的 **Personal Access Token**（不是GitHub密码）

> 🔑 Token生成地址：https://github.com/settings/tokens  
> 权限勾选：`repo`

### 推送成功标志

```
Enumerating objects: 11, done.
Counting objects: 100% (11/11), done.
...
To https://github.com/Iranorawahaha.github.io/international-news-kb.git
 * [new branch]      main -> main
```

### 推送后验证

**等待1-2分钟**（GitHub Pages构建时间），然后：

1. 打开浏览器访问：https://iranorawahaha.github.io/international-news-kb/
2. **强制刷新**：`Cmd + Shift + R`（Mac）或 `Ctrl + Shift + R`（Windows）
3. 检查：
   - [ ] 页面显示正常（渐变色界面）
   - [ ] 统计卡片显示正确数量
   - [ ] 新闻列表表格完整显示
   - [ ] 搜索和筛选功能可用
   - [ ] 手机端布局正常

---

## 一键脚本说明

### 脚本位置

```
/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/update-news.sh
```

### 使用方法

```bash
cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50

# 添加执行权限（只需一次）
chmod +x update-news.sh

# 运行
./update-news.sh
```

### 脚本执行流程

```
./update-news.sh
    │
    ├─ 第1步: 基础采集（自动）
    │   └─ python3 scripts/fetch_news_v3.py --basic-only
    │   └─ 获得: 10-18条中文新闻
    │
    ├─ 第2步: WebFetch补充（交互式询问）
    │   └─ 提示: "是否已通过WebFetch获取了额外数据？(y/n)"
    │   └─ 输入 y → 包含已有的WebFetch数据
    │   └─ 输入 n → 跳过，仅用基础数据
    │
    ├─ 第3步: 数据验证（自动）
    │   └─ 统计数量、来源、分类、重要性
    │   └─ 显示详细统计报告
    │
    ├─ 第4步: 网页生成（自动）
    │   └─ 备份旧文件
    │   └─ 读取最新数据
    │   └─ 生成新的单文件index.html
    │
    └─ 第5步: 推送部署（自动）
        ├─ git add .
        ├─ git commit -m "📰 更新新闻数据..."
        └─ git push origin main
            └─ 输入用户名和Token
            └─ ✅ 完成！
```

### 脚本输出示例

```
╔══════════════════════════════════════════════╗
║   🌍 国际新闻知识库 - 增强版更新系统 v2.0     ║
╚══════════════════════════════════════════════╝

📅 当前时间: 2026-07-30 09:30:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📡 第1步：基础采集（中文信源）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 运行增强版采集脚本 (v3.0)...

🌍 国际新闻知识库 - 增强版采集系统 v3.0

[... 采集过程输出 ...]

✅ 基础采集完成: 18 条新闻

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 第2步：WebFetch API补充（高价值英文信源）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 重要提示：此步骤需要在 WorkBuddy 环境中完成！

[... WebFetch说明 ...]

是否已通过 WebFetch 获取了额外数据？(y/n, 默认跳过): y

✅ 已包含 WebFetch 数据，继续...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 第3步：验证数据质量
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 新闻总数: 32 条

📰 来源分布:
   • 路透社: 8 条
   • BBC News: 6 条
   [...]

✅ 数据验证通过

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 第4步：更新单文件HTML网页
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 已备份当前网页
🔄 正在重新生成 index.html（嵌入最新数据）...

✅ 单文件HTML已生成
   包含 32 条新闻数据

✅ 网页更新完成

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 第5步：提交并推送到GitHub
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 将要提交的更改:
 M index.html
 M news-data.json

🚀 正在推送到GitHub...
⏳ 如果提示输入密码，请使用 Personal Access Token

Username for 'https://github.com': Iranorawahaha
Password for 'https://Iranorawahaha@github.com': 
Enumerating objects: 11, done.
Counting objects: 100% (11/11), done.
To https://github.com/Iranorawahaha.github.io/international-news-kb.git
 * [new branch]      main -> main

╔══════════════════════════════════════════════╗
║           🎉 更新成功完成！                      ║
╚══════════════════════════════════════════════╝

📊 本次更新统计:
   • 总新闻数: 32 条
   • 基础采集: 18 条
   • WebFetch补充: 14 条
   • 更新时间: 2026-07-30 09:35:22

🌐 访问地址: https://iranorawahaha.github.io/international-news-kb/

⏳ 网站将在 1-2分钟后 自动更新

💡 提示: 强制刷新浏览器 (Cmd+Shift+R) 查看最新内容
```

---

## 每日更新时间表

### 推荐时间安排

| 时间 | 用途 | 预计耗时 | 详细说明 |
|------|------|----------|----------|
| **09:30** | 早间更新 | 3-5分钟 | 覆盖隔夜重要新闻（欧美时段） |
| **17:00** | 下午更新 | 3-5分钟 | 覆盖当日最新动态（亚洲时段） |

### 早间更新（09:30）重点关注

- 🌙 **美国/欧洲隔夜要闻**
- 📈 **美股/欧股收盘情况**
- 🗳️ **白宫/国务院最新声明**
- 🤖 **科技公司夜间发布**

### 下午更新（17:00）重点关注

- ☀️ **亚洲当日要闻**
- 🇨🇳 **中国外交部例行记者会**
- 📊 **A股/港股收盘总结**
- 🌏 **亚太地区动态**

---

## 常见问题

### Q1：每次都需要执行完整的5步吗？

**答**：不一定。有两种简化方案：

**方案A：一键脚本（推荐日常使用）**
```bash
./update-news.sh
```
一条命令完成所有步骤（除了WebFetch需要单独请求）。

**方案B：仅更新网页（如果数据已经是最新的）**
```bash
cd gh-pages && python3 -c "
import json
from datetime import datetime
# ... 重新生成HTML ...
" && git add . && git commit -m "刷新页面" && git push origin main
```

---

### Q2：WebFetch步骤必须每次都做吗？

**答**：强烈建议，但不是强制性的。

| 场景 | 建议 |
|------|------|
| **时间充足**（≥5分钟） | ✅ 执行WebFetch，获得最佳质量 |
| **时间紧张**（≤3分钟） | ⏭️ 可跳过，仅用基础采集 |
| **首次使用** | ✅ 必须执行，体验完整效果 |
| **紧急更新** | ⏭️ 可跳过，先保证时效性 |

---

### Q3：推送失败怎么办？

**错误1：代理502**
```
fatal: unable to access '...github.com...': CONNECT tunnel failed, response 502
```
**解决**：
1. 重启代理软件（Clash/V2Ray等）
2. 等待10秒后重新推送

**错误2：认证失败**
```
Authentication failed
```
**解决**：
1. 检查Token是否过期
2. 重新生成Token：https://github.com/settings/tokens
3. 确保勾选了`repo`权限

**错误3：网络超时**
```
Failed to connect to github.com port 443 after 75000 ms
```
**解决**：
1. 检查网络连接
2. 确认代理软件正在运行
3. 尝试切换网络（WiFi/有线）

---

### Q4：如何查看历史更新记录？

```bash
cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/gh-pages

# 查看提交历史
git log --oneline -10

# 查看某次更新的详情
git show HEAD --stat

# 回滚到某个历史版本（谨慎操作）
git checkout <commit-hash>
```

---

### Q5：数据文件太大怎么办？

**正常大小参考**：
- 20条新闻：~15KB
- 30条新闻：~25KB
- 50条新闻：~40KB

**如果异常大（>100KB）**：
```bash
# 检查是否有重复或无效数据
python3 << 'EOF'
import json
with open('data/news-data.json', 'r') as f:
    data = json.load(f)
print(f"总数: {len(data)}")
print(f"平均每条大小: {len(json.dumps(data)) / len(data):.0f} bytes")
EOF
```

---

### Q6：能否设置定时自动更新？

**答**：可以，但需要额外配置。两种方案：

**方案A：macOS LaunchAgent（系统级）**
```xml
<!-- 创建 ~/Library/LaunchAgents/com.news-kb.update.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.news-kb.update</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50 && ./update-news.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>
</dict>
</plist>
```

**方案B：cron任务（简单）**
```bash
# 编辑crontab
crontab -e

# 添加两行（每天9:30和17:00执行）
30 9 * * * cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50 && ./update-news.sh >> /tmp/news-update.log 2>&1
0 17 * * * cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50 && ./update-news.sh >> /tmp/news-update.log 2>&1
```

⚠️ **注意**：自动更新无法执行WebFetch步骤（需要在WorkBuddy环境），只能进行基础采集。

---

### Q7：如何避免新闻缺少原文链接？（重要！）

**答**：这是2026-07-31日发现并修复的重要问题。

#### 问题现象

部分新闻（特别是通过WebFetch获取的英文信源文章）的"原文链接"列显示"暂无"，无法点击跳转到原始文章。

#### 根本原因

WebFetch API返回的是页面内容摘要，**不会自动提取每篇文章的完整URL**。如果在请求时没有明确要求返回URL，助手可能只填写标题和摘要而遗漏url字段。

#### 解决方案（已固化到脚本中）

✅ **修复1：WebFetch Prompt已强化（fetch_news_v3.py v3.1）**

所有4个英文信源的prompt模板现在都包含强制URL要求：
```python
# 示例：路透社prompt（已更新）
'prompt': '...列出最重要的8-10条新闻，每条必须包含：标题、摘要、关键词、**完整的原文链接URL（必须是https://开头的完整文章地址）**。⚠️ URL是必填项...'
```

✅ **修复2：新增URL完整性验证步骤（fetch_news_v3.py v3.1）**

脚本现在会在数据合并后自动执行URL检查：
```
🔗 URL完整性验证
============================================================
📊 URL覆盖率统计:
   - 总文章数: 26 条
   - 有URL: 26 条 (100.0%)
   - 缺失URL: 0 条 (0.0%)

✅ 所有文章都有有效URL！
```

如果覆盖率 < 80%，会显示红色警告；< 95%会显示黄色警告。

✅ **修复3：HTML生成器已支持链接列（update-news.sh v2.1）**

生成的网页现在包含第9列"原文链接"：
- 有URL的文章：显示紫色渐变按钮"🔗 链接"（可点击跳转）
- 无URL的文章：显示灰色文字"暂无"

✅ **修复4：质量标准已更新（DAILY-UPDATE-MANUAL.md v3.1）**

检查清单新增2项URL相关指标：
- [ ] URL覆盖率 ≥ 95%
- [ ] 所有WebFetch文章都有完整URL

#### 如果仍然遇到URL缺失怎么办？

**步骤1：检查验证输出**
```bash
python3 scripts/fetch_news_v3.py --basic-only
# 查看是否有"⚠️ 警告：X 条新闻缺少有效URL！"提示
```

**步骤2：如果缺失率 > 5%，重新执行WebFetch**
在WorkBuddy对话中说：
> "请重新用 WebFetch 抓取南华早报和卫报的新闻，**特别注意每条新闻必须包含完整的原文链接URL**"

**步骤3：手动补全（最后手段）**
编辑 `data/news-data.json`，为缺失URL的文章手动添加url字段。

#### 预防措施

| 措施 | 说明 | 状态 |
|------|------|------|
| Prompt强制要求 | WebFetch prompt明确要求URL | ✅ 已实施 |
| 自动化验证 | 脚本自动检查URL覆盖率 | ✅ 已实施 |
| 可视化警告 | 缺失URL时显示红色/黄色警告 | ✅ 已实施 |
| 质量门槛 | 覆盖率 < 80% 时强烈建议重新抓取 | ✅ 已实施 |
| 文档记录 | 操作手册记录问题和解决方案 | ✅ 已完成 |

---

## 技术细节

### 架构图

```
┌──────────────────────────────────────────────────────────────┐
│                    国际新闻知识库 v3.0                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────┐    ┌──────────────────────────────┐ │
│  │  第1层：基础采集     │    │  第2层：WebFetch API补充      │ │
│  │  (Python requests)  │    │  (WorkBuddy专属功能)          │ │
│  ├────────────────────┤    ├──────────────────────────────┤ │
│  │ • 人民网           │    │ • 路透社 (Reuters)           │ │
│  │ • 中国日报         │    │ • BBC News                   │ │
│  │ • 环球网           │    │ • 南华早报 (SCMP)            │ │
│  │ • 国际在线         │    │ • 卫报 (The Guardian)        │ │
│  │ • 外交部           │    │                              │ │
│  │ • 新华网           │    │ 优势：                       │ │
│  │                    │    │ ✓ 绕过反爬虫                │ │
│  │ 产出：             │    │ ✓ 内容质量高                │ │
│  │ 10-18条中文新闻    │    │ ✓ 多角度国际视角            │ │
│  └────────┬───────────┘    └──────────────┬───────────────┘ │
│           │                                │                 │
│           ▼                                ▼                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              第3步：数据整合引擎                         │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ • 合并两层结果                                          │ │
│  │ • 标题相似度去重                                        │ │
│  │ • 自动分类（中美关系/AI科技/外交等）                    │ │
│  │ • 重要性评分（高/中/低）                                │ │
│  │ • 关键词提取                                            │ │
│  │                                                        │ │
│  │ 产出：25-35条精选高质量新闻                             │ │
│  └───────────────────────┬────────────────────────────────┘ │
│                          ▼                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           第4步：单文件HTML生成器                        │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ • 内嵌CSS样式（~200行）                                 │ │
│  │ • 内嵌JavaScript（~150行）                              │ │
│  │ • 内嵌JSON数据（所有新闻）                              │ │
│  │ • 响应式设计                                            │ │
│  │ • 搜索/筛选/排序功能                                    │ │
│  │                                                        │ │
│  │ 产出：index.html (~35KB)                               │ │
│  └───────────────────────┬────────────────────────────────┘ │
│                          ▼                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          第5步：GitHub Pages部署                        │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ • git add → git commit → git push                     │ │
│  │ • GitHub Actions自动构建                               │ │
│  │ • 全球CDN分发                                          │ │
│  │ • HTTPS加密                                            │ │
│  │                                                        │ │
│  │ 访问：https://iranorawahaha.github.io/...              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 文件结构

```
/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/
│
├── scripts/
│   ├── fetch_news_v3.py        ← 增强版采集脚本（核心）
│   ├── fetch_news_v2.py        ← 标准版采集脚本（备用）
│   └── server.py               ← 本地开发服务器
│
├── data/
│   ├── news-data.json          ← 主数据文件（最重要）
│   ├── config.json             ← 信源配置（30个信源）
│   └── collection-report.md    ← 采集报告（每次生成）
│
├── js/
│   └── embedded-data.js        ← 前端嵌入式数据（备用格式）
│
├── gh-pages/                   ← GitHub Pages部署目录
│   ├── index.html              ← 单文件自包含网页（最终产物）
│   ├── news-data.json          ← 数据副本（可选）
│   └── index.backup.*.html     ← 历史备份
│
├── update-news.sh              ← 一键更新脚本 ⭐
├── start-server.sh             ← 本地服务器启动脚本
├── stop-server.sh              ← 本地服务器停止脚本
│
└── docs/
    ├── DAILY-UPDATE-MANUAL.md  ← 本文档（每日操作手册）
    ├── COMPLETE-WORKFLOW-GUIDE.md
    ├── GITHUB-PAGES-DEPLOY-GUIDE.md
    └── GITHUB-PAGES-CHEATSHEET.md
```

### 关键代码片段

#### 1. 基础采集核心逻辑

```python
# fetch_news_v3.py - EnhancedNewsFetcher类
def fetch_basic_sources(self):
    """第1层：基础采集"""
    for source in BASIC_SOURCES:
        try:
            response = self.session.get(source['url'], timeout=12)
            articles = self._extract_basic_content(response.text, source)
            self.basic_results.extend(articles)
        except Exception as e:
            print(f"❌ [{source['name']}] 失败: {e}")
```

#### 2. WebFetch任务准备

```python
# fetch_news_v3.py - prepare_webfetch_tasks()
WEBFETCH_SOURCES = [
    {
        'name': '路透社',
        'url': 'https://www.reuters.com/world/',
        'prompt': '提取今天最重要的国际新闻...',
        'expected_count': 8,
    },
    # ... 更多信源
]
```

#### 3. 数据合并去重

```python
# fetch_news_v3.py - merge_and_deduplicate()
def merge_and_deduplicate(self):
    all_articles = self.basic_results + self.webfetch_results
    
    seen_titles = set()
    unique_articles = []
    
    for article in all_articles:
        title_key = re.sub(r'[^\u4e0-\u9fa5a-zA-Z]', '', article['title']).lower()
        
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_articles.append(article)
    
    return unique_articles
```

#### 4. HTML生成器

```python
# update-news.sh 内嵌的Python代码
html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <style>{css_styles}</style>
</head>
<body>
    <script>
        const NEWS_DATA = {json.dumps(news_data)};
        // ... 渲染逻辑
    </script>
</body>
</html>
'''
```

---

## 附录

### A. 快速参考卡

打印此页贴在显示器旁边：

```
╔═══════════════════════════════════════╗
║  🌍 每日更新快速参考                   ║
╠═══════════════════════════════════════╣
║                                         ║
║  1. 打开终端                            ║
║  $ cd ~/WorkBuddy/2026-07-29-17-06-50  ║
║                                         ║
║  2. 运行更新脚本                        ║
║  $ ./update-news.sh                     ║
║                                         ║
║  3. 输入 y/n（是否含WebFetch数据）       ║
║                                         ║
║  4. 输入Git认证信息                      ║
║  用户名: Iranorawahaha                  ║
║  密码: Personal Access Token            ║
║                                         ║
║  5. 等待1-2分钟                         ║
║                                         ║
║  6. 访问网站                            ║
║  https://iranorawahaha.github.io/...   ║
║                                         ║
║  ⏱ 总耗时: 3-5分钟                     ║
║                                         ║
╚═══════════════════════════════════════╝
```

### B. 错误代码速查表

| 错误代码 | 含义 | 解决方案 |
|---------|------|---------|
| HTTP 401 | 需要认证 | 跳过该信源或使用WebFetch |
| HTTP 403 | 反爬虫拦截 | 使用WebFetch替代 |
| HTTP 404 | URL失效 | 更新config.json中的URL |
| SSL Error | 证书问题 | 安装`certifi`或忽略验证 |
| Proxy 502 | 代理故障 | 重启代理软件 |
| Auth Failed | Git认证失败 | 检查Token是否有效 |
| Timeout | 连接超时 | 检查网络或重试 |

### C. 性能基准

| 指标 | 基础采集 | 基础+WebFetch |
|------|---------|--------------|
| **耗时** | 30-60秒 | 2-3分钟 |
| **新闻数** | 10-18条 | 25-35条 |
| **信源数** | 4-6个 | 8-10个 |
| **高重要性占比** | 20-30% | 35-45% |
| **国际视角** | 偏中国 | 平衡多元 |
| **数据质量** | ★★★☆☆ | ★★★★★ |

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| **V1.0** | **2026-07-31** | **⭐ 正式版发布：系统名称定为"国际新闻看板"、URL完整性保障机制（4道防线）、所有功能稳定验证通过、工作空间清理优化** |
| v3.1 | 2026-07-31 | URL完整性保障：Prompt强化、自动验证、HTML链接列、质量标准更新 |
| v3.0 | 2026-07-30 | 双层架构（基础+WebFetch）、单文件HTML、一键脚本 |
| v2.0 | 2026-07-29 | 添加质量标准、筛选规则 |
| v1.0 | 2026-07-29 | 初始版本，基础采集 |

---

## 联系与支持

如有问题，请查阅：
- 📖 完整工作流指南：`docs/COMPLETE-WORKFLOW-GUIDE.md`
- 🚀 GitHub Pages部署指南：`docs/GITHUB-PAGES-DEPLOY-GUIDE.md`
- 💾 Skill技能文档：`~/.workbuddy/skills/international-news-collect-v2/SKILL.md`

---

**祝使用愉快！** 🎉

*国际新闻看板 V1.0 正式版 | 最后更新：2026-07-31 11:00*
