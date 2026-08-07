#!/bin/bash
# update-ai.sh — AI 看板每日更新
# 流程: fetch_ai.py (采集+分类) → build_ai.py (渲染) → gh-pages 同步 → git push
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🤖 AI 看板更新 · $(date '+%Y-%m-%d %H:%M')"

# 1. 采集 + 分类
echo ""
echo "📡 第1步: 数据采集与分类..."
python3 scripts/fetch_ai.py

# 2. 渲染 HTML
echo ""
echo "🏗️ 第2步: 渲染HTML..."
python3 scripts/build_ai.py

# 3. 同步到 gh-pages
if [ -d "gh-pages" ]; then
    cp ai-news.html gh-pages/ai-news.html
    echo "📋 已同步到 gh-pages/"
fi

# 4. Git commit
echo ""
echo "📤 第3步: 提交推送..."
git add data/ai-news.json ai-news.html gh-pages/ai-news.html 2>/dev/null || true
git commit -m "🤖 AI 看板更新 - $(date '+%Y-%m-%d %H:%M')" 2>/dev/null || echo "  (无变更)"
git push 2>/dev/null || echo "  ⚠️ 推送失败（手动重试）"

echo ""
echo "✅ AI 看板更新完成"
echo "🌐 https://iranorawahaha.github.io/international-news-kb/ai-news.html"
