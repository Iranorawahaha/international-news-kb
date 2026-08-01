# 🚀 GitHub Pages 快速部署命令

## 一键执行（复制粘贴即可）

### 1️⃣ 创建GitHub仓库
浏览器打开: https://github.com/new
- Repository name: **international-news-kb**
- 选择 Private 或 Public
- ❌ 不要勾选 README / .gitignore / license
- 点击 **Create repository**

---

### 2️⃣ 推送代码（在终端执行）

```bash
# 进入目录
cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/gh-pages

# 添加远程地址
git remote add origin https://github.com/Iranorawahaha/international-news-kb.git

# 推送到GitHub
git push -u origin main
```

**登录提示**: 用户名输入 `Iranorawahaha`，密码输入 Personal Access Token

---

### 3️⃣ 启用Pages

1. 打开: https://github.com/Iranorawahaha/international-news-kb/settings/pages
2. Source: **Deploy from a branch**
3. Branch: **main** → **/ (root)**
4. 点击 **Save**

---

### ✅ 访问网站

**等待2分钟后访问**:
```
https://iranorawahaha.github.io/international-news-kb/
```

---

## 📦 以后更新只需3条命令

```bash
cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/gh-pages

# 复制最新数据
cp ../data/news-data.json ./news-data.json
cp ../js/embedded-data.js ./embedded-data.js

# 提交并推送
git add .
git commit -m "📰 更新新闻数据"
git push origin main
```

**1-2分钟后自动更新！**

---

## 🔗 分享链接

直接发送给同事：
```
https://iranorawahaha.github.io/international-news-kb/
```

✅ 无需安装 · ✅ 支持手机 · ✅ 全球加速

---

## ⚠️ 常见问题

**Q: 忘记密码怎么办？**
A: 使用Token，不是GitHub密码。生成地址：https://github.com/settings/tokens

**Q: 推送失败？**
A: 检查Token是否有 `repo` 权限

**Q: 页面不更新？**
A: 强制刷新 `Cmd + Shift + R`，或等待2分钟

**Q: 想要自定义域名？**
A: 在仓库根目录创建 `CNAME` 文件，写入你的域名

---

**完整文档**: 查看 `docs/GITHUB-PAGES-DEPLOY-GUIDE.md`
