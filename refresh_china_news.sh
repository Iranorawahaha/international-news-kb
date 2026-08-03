#!/bin/bash
# ============================================================
# 国内新闻看板 · 一键刷新 + 自动部署脚本（Ira 信息看板体系）
# 1) 抓取中国政府网·要闻 + 最新政策（国家级权威信源）
# 2) 生成 china-news.html（单文件，深红政务风）
# 3) 部署到 GitHub Pages（国际新闻看板仓库内嵌页面）
# 4) 更新门户统计（国内新闻今新增 + 日报要点）
# 默认 9:30 自动刷新（自动化任务）
# ============================================================
set -e

OUT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_HTML="$OUT_DIR/china-news.html"
BUILD_PY="$OUT_DIR/scripts/build_china.py"
KB_DIR="$OUT_DIR"  # 国内新闻看板直接位于国际新闻看板仓库内
KB_PAGE="$KB_DIR/china-news.html"
PY="/Users/xiaoxiao/.workbuddy/binaries/python/versions/3.13.12/bin/python3"
[ -x "$PY" ] || PY="python3"
export PY

mkdir -p "/tmp/aihot_scan"
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

echo "== [1/3] 抓取中国政府网权威信源 =="
"$PY" "$OUT_DIR/scripts/fetch_china.py"

echo ""
echo "== [2/3] 生成国内新闻看板 =="
cd "$OUT_DIR"
# JS 语法自检在 build_china.py 内部已做
"$PY" "$BUILD_PY"

echo ""
echo "== [3/3] 部署到 GitHub Pages =="
if [ ! -d "$KB_DIR/.git" ]; then
    echo "⚠️  国际新闻看板仓库不存在，跳过部署: $KB_DIR"
    exit 0
fi

# 同步 gh-pages 副本
cp "$OUT_HTML" "$KB_DIR/gh-pages/china-news.html"

cd "$KB_DIR"
# 注入统一导航（幂等）
"$PY" "$KB_DIR/scripts/inject_nav.py" "$KB_PAGE" "$KB_DIR/gh-pages/china-news.html"

# 更新门户统计：国内新闻今日新增 + 看板最近刷新时间
echo "== 更新门户统计（国内新闻字段）=="
CN_TODAY=$("$PY" -c "
import json
try:
    d = json.load(open('$KB_DIR/data/china-news.json'))
    print(d.get('todayCount', '--'))
except Exception:
    print('--')
")
CN_LAST=$(date '+%Y-%m-%d %H:%M')
"$PY" "$KB_DIR/scripts/update_portal_stats.py" \
    --cn-today "$CN_TODAY" \
    --cn-date "$CN_LAST" \
    --latest "$CN_LAST"
cp "$KB_DIR/index.html" "$KB_DIR/gh-pages/index.html"

# 更新门户今日日报（国内新闻要点）
"$PY" "$KB_DIR/scripts/daily_brief.py" --cn

# git 提交推送
git add china-news.html gh-pages/china-news.html index.html gh-pages/index.html \
    data/china-news.json scripts/fetch_china.py scripts/build_china.py

if git diff --cached --quiet; then
    echo "ℹ️  内容无变化，跳过提交"
else
    git commit -m "🇨🇳 国内新闻看板自动刷新 - $(date '+%Y-%m-%d %H:%M')

📊 数据快照更新（gov.cn 要闻 + 最新政策 近 7 天）"
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
echo "   线上地址: https://iranorawahaha.github.io/international-news-kb/china-news.html"
echo "   生成时间: $(date '+%Y-%m-%d %H:%M:%S %Z')"

# ===== C 方案：记录本次执行（供错过补跑检查） =====
"$PY" /Users/xiaoxiao/WorkBuddy/2026-08-01-14-08-40/scripts/record_run.py cn --status ok
