# 🌍 国际新闻知识库 - GitHub Pages 部署指南

## ✨ 在线预览地址

**部署后您的网站将可以通过以下地址访问：**
```
https://[您的用户名].github.io/[仓库名]/
```

## 📦 快速部署步骤（3分钟）

### 方式A：使用GitHub CLI（推荐）

```bash
# 1. 初始化Git仓库
cd gh-pages
git init

# 2. 添加所有文件
git add .
git commit -m "🎉 初始部署：国际新闻知识库 v1.0 (24条新闻)"

# 3. 创建GitHub仓库并推送
gh repo create international-news-library --public --source=. --push
# 或者使用私有仓库：
# gh repo create international-news-library --private --source=. --push
```

### 方式B：手动部署（无CLI）

```bash
# 1. 初始化仓库
cd gh-pages
git init
git add .
git commit -m "初始部署"

# 2. 在GitHub上创建新仓库（空仓库）
# 仓库名: international-news-library

# 3. 添加远程仓库并推送
git remote add origin https://github.com/[您的用户名]/international-news-library.git
git branch -M main
git push -u origin main
```

### 4. 启用GitHub Pages

1. 打开仓库页面：`https://github.com/[您的用户名]/international-news-library`
2. 点击 **Settings** (设置)
3. 左侧菜单选择 **Pages**
4. **Source** 选择：Deploy from a branch
5. **Branch** 选择：main / (root)
6. 点击 **Save**

### 5. 等待部署完成（1-2分钟）

访问：`https://[您的用户名].github.io/international-news-library/`

---

## 🔧 自定义域名（可选）

如果您有自己的域名，可以绑定到GitHub Pages：

```bash
# 在gh-pages目录创建CNAME文件
echo "news.yourdomain.com" > CNAME
git add CNAME
git commit -m "添加自定义域名"
git push
```

然后在域名DNS管理中添加CNAME记录指向：
```
[您的用户名].github.io
```

---

## 📊 网站特性

✅ **完全免费** - GitHub Pages提供无限流量  
✅ **全球CDN加速** - 访问速度快  
✅ **HTTPS加密** - 自动配置SSL证书  
✅ **自动备份** - Git版本控制  
✅ **无需服务器** - 不需要自己的电脑运行  

### 功能支持：

- ✅ 响应式设计（手机/平板/电脑）
- ✅ 实时搜索和筛选
- ✅ 按分类/来源/重要性过滤
- ✅ 导出为JSON/CSV/Excel
- ✅ 24条高质量国际新闻
- ✅ 4大顶级信源覆盖

---

## 🔄 更新数据流程

当您采集了新的新闻后，更新网站的步骤：

```bash
cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/gh-pages

# 1. 复制最新数据
cp ../js/embedded-data.js .
cp ../data/news-data.json .

# 2. 提交更改
git add .
git commit -m "📰 更新新闻数据 (日期: $(date +%Y-%m-%d))"
git push

# 3. 自动部署（1-2分钟后生效）
```

或者使用一键脚本（需要先创建）：

```bash
./update-website.sh  # 自动复制+提交+推送
```

---

## ⚠️ 注意事项

### 公开 vs 私有仓库

| 类型 | 访问权限 | 适用场景 |
|------|---------|---------|
| **公开仓库** | 所有人可访问 | 公开分享、团队展示 |
| **私有仓库** | 仅您和协作者 | 内部使用、敏感信息 |

**建议**: 
- 如果只是给同事看 → 使用**私有仓库** + 分享链接
- 如果希望公开 → 使用**公开仓库**

### 数据安全

- ✅ config.json中的账号密码**未包含**在部署包中
- ✅ 仅包含前端静态文件和数据
- ⚠️ news-data.json中的新闻内容会公开可见（如使用公开仓库）

---

## 💡 高级功能（可选）

### 1. 添加访问统计

使用Google Analytics或百度统计：

```html
<!-- 在index.html的<head>中添加 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
```

### 2. 添加自定义域名

参考上方"自定义域名"章节

### 3. 设置自动部署（GitHub Actions）

创建 `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
      - uses: actions/deploy-pages@v4
```

这样每次push都会自动更新网站！

---

## 🆘 故障排查

### 问题1：页面显示404

**解决方案**:
- 检查Settings → Pages是否启用
- 确认Branch设置为main/(root)
- 等待2-3分钟让部署完成

### 问题2：样式丢失

**解决方案**:
- 确认css/style.css已上传
- 检查浏览器控制台是否有404错误
- 清除浏览器缓存后刷新

### 问题3：数据未更新

**解决方案**:
- 确认已执行 `git push`
- 查看Actions标签页确认部署状态
- 强制刷新浏览器 (Cmd+Shift+R)

---

## 📞 技术支持

如有问题，请查看：
- GitHub Pages官方文档：https://docs.github.com/pages
- 本项目完整说明书：`docs/SYSTEM-MANUAL-v3.1.md`
- 访问指南：`docs/ACCESS-GUIDE.md`

---

## 🎉 部署成功！

恭喜！您的国际新闻知识库现在拥有了一个**永久免费的在线网址**！

**分享给同事**：
```
📰 国际新闻知识库 v1.0

🌐 在线地址：https://[您的用户名].github.io/international-news-library/

📊 数据：24条最新国际新闻
📰 信源：路透社 / BBC / 南华早报 / 卫报
⏰ 更新：2026-07-30

💡 无需登录，直接打开即可查看！
```

祝使用愉快！🚀
