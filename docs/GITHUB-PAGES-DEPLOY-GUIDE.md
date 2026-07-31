# GitHub Pages 部署指南

## 📋 部署概览

**项目信息**:
- **仓库名称**: `international-news-kb`
- **GitHub用户名**: `Iranorawahaha`
- **最终访问地址**: `https://iranorawahaha.github.io/international-news-kb/`
- **本地仓库路径**: `/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/gh-pages/`

**已准备文件** (7个):
```
✅ index.html          - 主页面（9.8KB）
✅ style.css           - 样式表（10.8KB）
✅ app.js              - 主应用逻辑（32KB）
✅ embedded-data.js    - 嵌入式数据（30.2KB）
✅ news-data.json      - 新闻数据（20.4KB）
✅ README.md           - 项目说明
✅ .gitignore          - Git忽略规则
```

---

## 🚀 3步完成部署

### 第1步：在GitHub上创建新仓库

1. 打开浏览器访问: **https://github.com/new**
2. 填写信息:
   - **Repository name**: `international-news-kb`
   - **Description**: `国际新闻知识库 - 每日高质量国际新闻自动采集与呈现`
   - **选择 Private** (仅自己可见) 或 **Public** (同事可访问)
3. **⚠️ 不要勾选** "Add a README file"、"Add .gitignore"、"Choose a license"
4. 点击 **Create repository**

### 第2步：推送代码到GitHub

打开终端（Terminal），执行以下命令：

```bash
# 进入项目目录
cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/gh-pages

# 添加远程仓库地址
git remote add origin https://github.com/Iranorawahaha/international-news-kb.git

# 推送代码到GitHub（首次推送需要登录）
git push -u origin main
```

**如果提示输入用户名密码**:
- **用户名**: 输入你的GitHub用户名 `Iranorawahaha`
- **密码**: 输入 **Personal Access Token** (不是GitHub密码)

> 💡 **如何生成Token?**
> 1. 访问 https://github.com/settings/tokens
> 2. 点击 "Generate new token (classic)"
> 3勾选 `repo` 权限
> 4. 复制生成的Token作为密码使用

### 第3步：启用GitHub Pages

1. 打开仓库页面: https://github.com/Iranorawahaha/international-news-kb
2. 点击 **Settings** (设置) 标签页
3. 左侧菜单找到 **Pages** 选项
4. 配置如下:
   - **Source**: 选择 `Deploy from a branch`
   - **Branch**: 选择 `main` 分支
   - **Folder**: 选择 `/ (root)` (根目录)
5. 点击 **Save**

等待1-2分钟后，访问: **https://iranorawahaha.github.io/international-news-kb/**

---

## ✅ 验证部署成功

看到以下界面说明部署成功:

- ✅ 渐变色标题栏显示"国际新闻知识库"
- ✅ 统计卡片显示"24条新闻"
- ✅ 表格展示完整新闻列表
- ✅ 搜索框、筛选器正常工作
- ✅ 手机端访问自适应布局

---

## 🔄 后续更新流程

当需要更新新闻数据时：

```bash
cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/gh-pages

# 1. 更新数据文件（从主项目复制最新数据）
cp ../data/news-data.json ./news-data.json
cp ../js/embedded-data.js ./embedded-data.js

# 2. 提交更改
git add .
git commit -m "📰 更新新闻数据 - YYYY-MM-DD"

# 3. 推送到GitHub（自动触发Pages更新）
git push origin main
```

**更新后生效时间**: 约1-2分钟

---

## 🔗 分享给同事

### 方式1：直接分享链接（推荐）

将此链接发送给同事：

```
https://iranorawahaha.github.io/international-news-kb/
```

**优点**:
- ✅ 无需任何安装或配置
- ✅ 支持电脑/手机/平板访问
- ✅ 自动HTTPS加密
- ✅ 全球CDN加速

**适用场景**:
- 日常浏览查看
- 会议演示
- 快速分享

### 方式2：GitHub仓库协作

如果你希望同事也能编辑或维护：

1. 将仓库设置为 **Public** 或添加 **Collaborators**
2. 同事可以通过Pull Request贡献内容
3. 所有更改自动更新到网站

**添加协作者步骤**:
- Settings → Collaborators → Add people → 输入同事GitHub用户名

---

## ⚙️ 高级配置（可选）

### 自定义域名（可选）

如果你有自己的域名，可以绑定到GitHub Pages：

1. 在仓库根目录创建 `CNAME` 文件，内容为你的域名:
   ```
   news.yourcompany.com
   ```
2. 在域名DNS服务商添加CNAME记录:
   - Host: `news`
   - Value: `iranorawahaha.github.io`
3. 在GitHub Pages设置中启用Custom domain

### 启用HTTPS（推荐）

GitHub Pages默认提供HTTPS证书，无需额外配置。

### 访问统计（可选）

可以使用以下工具统计访问量：
- **Google Analytics**: 在index.html中添加跟踪代码
- **Cloudflare Analytics**: 通过自定义域名使用

---

## 🛠️ 故障排除

### 问题1：页面显示404

**原因**: Pages还未部署完成或配置错误

**解决**:
1. 确认分支名称正确（应该是 `main`，不是 `master`）
2. 等待2-3分钟（首次部署较慢）
3. 检查Settings → Pages查看部署日志

### 问题2：样式丢失

**原因**: 文件路径问题

**解决**: 确认所有CSS/JS文件都已推送到仓库根目录

### 问题3：推送时认证失败

**原因**: 密码错误或Token过期

**解决**:
1. 重新生成Personal Access Token
2. 使用GitHub CLI (`gh`) 免密推送: `brew install gh && gh auth login`

### 问题4：更新后网页未变化

**原因**: 浏览器缓存

**解决**:
- 强制刷新: `Cmd + Shift + R` (Mac) / `Ctrl + Shift + R` (Windows)
- 或清除浏览器缓存后访问

---

## 📊 项目结构说明

```
gh-pages/
├── index.html          # 主页面入口
├── style.css           # 完整样式表
├── app.js              # 应用逻辑（搜索/筛选/排序）
├── embedded-data.js    # 嵌入的24条新闻数据
├── news-data.json      # JSON格式数据备份
├── README.md           # 项目说明文档
└── .gitignore          # Git忽略规则
```

**技术特点**:
- ✅ 纯静态HTML/CSS/JS，无需服务器
- ✅ 单页面应用，加载速度快
- ✅ 数据嵌入JS文件，减少HTTP请求
- ✅ 响应式设计，支持移动端
- ✅ 支持离线访问（打开一次后可离线浏览）

---

## 🎯 下一步建议

1. **定期更新**: 设置每日定时任务自动采集并推送
2. **权限管理**: 根据需要调整仓库可见性（Private/Public）
3. **团队协作**: 添加同事为Collaborators共同维护
4. **功能增强**: 可考虑添加评论系统、订阅通知等

---

## 📞 技术支持

如遇到问题，请检查：

1. **GitHub状态页**: https://www.githubstatus.com/
2. **GitHub Pages文档**: https://docs.github.com/en/pages
3. **部署日志**: 仓库 → Actions → Pages build and deployment

---

**部署日期**: 2026-07-30
**版本**: v1.0
**维护者**: Iranorawahaha
