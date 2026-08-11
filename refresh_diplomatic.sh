#!/bin/bash
# ============================================================
# 使领馆事务看板 · 一键刷新 + 自动部署脚本（Ira 信息看板体系 v1.0）
# 1) 抓取外交部/中国政府网/新华社等权威信源
# 2) 生成 diplomatic-affairs.html（单文件，青绿色专业风）
# 3) 部署到 GitHub Pages（国际新闻看板仓库内嵌页面）
# 4) 更新门户统计
# 默认 08:00 自动刷新（自动化任务）
# ============================================================
set -e

OUT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_HTML="$OUT_DIR/diplomatic-affairs.html"
BUILD_PY="$OUT_DIR/scripts/build_diplomatic.py"
KB_DIR="$OUT_DIR"  # 与国际新闻看板同一仓库
KB_PAGE="$KB_DIR/diplomatic-affairs.html"
PY="/Users/xiaoxiao/.workbuddy/binaries/python/versions/3.13.12/bin/python3"
[ -x "$PY" ] || PY="python3"
export PY

mkdir -p "/tmp/diplomatic_scan"
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

echo "== [1/3] 采集使领馆事务数据 =="
"$PY" "$OUT_DIR/scripts/fetch_diplomatic.py" --window 3

echo ""
echo "== [2/3] 生成使领馆事务看板 =="
cd "$OUT_DIR"
"$PY" "$BUILD_PY"

echo ""
echo "== [3/3] 部署到 GitHub Pages =="
if [ ! -d "$KB_DIR/.git" ]; then
    echo "⚠️  国际新闻看板仓库不存在，跳过部署: $KB_DIR"
    exit 0
fi

# 同步 gh-pages 副本
cp "$OUT_HTML" "$KB_DIR/gh-pages/diplomatic-affairs.html"

cd "$KB_DIR"

# git 提交推送
git add diplomatic-affairs.html gh-pages/diplomatic-affairs.html \
    data/diplomatic-affairs.json \
    scripts/fetch_diplomatic.py scripts/build_diplomatic.py

if git diff --cached --quiet; then
    echo "ℹ️  内容无变化，跳过提交"
else
    git commit -m "🏛 使领馆事务看板自动刷新 v1.0 - $(date '+%Y-%m-%d %H:%M')

📊 外交人事 · 官员访华 · 中美互动 · 自动采集更新"
    if git push origin main 2>&1; then
        echo "✅ 已推送 GitHub Pages"
    else
        echo "⚠️  推送失败（可能存在并行更新），尝试同步后重推..."
        git fetch origin
        git stash 2>/dev/null || true
        git rebase origin/main 2>&1 | head -3 || git pull --no-rebase origin main 2>&1 | head -3
        git stash pop 2>/dev/null || true
        git push origin main 2>&1 | tail -3
    fi
fi

echo ""
echo "✅ 刷新完成: $OUT_HTML"
echo "   线上地址: https://iranorawahaha.github.io/international-news-kb/diplomatic-affairs.html"
echo "   生成时间: $(date '+%Y-%m-%d %H:%M:%S %Z')"

# 记录本次执行
"$PY" "$(cd "$(dirname "$0")" && pwd)/scripts/record_run.py" diplomatic --status ok 2>/dev/null || true
