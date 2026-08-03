#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_missed_runs.py — 看板任务「错过补跑」检查器（C 方案）

读取 ~/.workbuddy/ira_runs.json，对比北京时间"今天"，找出今天尚未执行（或执行失败）
的任务，并按需补跑。

任务 → 刷新脚本映射：
  news → /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/update-news.sh --auto
  ai   → /Users/xiaoxiao/WorkBuddy/2026-08-01-14-08-40/refresh_board.sh
  cn   → /Users/xiaoxiao/WorkBuddy/2026-08-01-14-08-40/refresh_china_news.sh

用法:
  python3 check_missed_runs.py            # 检查并补跑缺失任务（逐个串行）
  python3 check_missed_runs.py --dry-run  # 只报告缺失，不执行
  python3 check_missed_runs.py --task news # 只补跑指定任务
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
STATE_FILE = os.path.expanduser("~/.workbuddy/ira_runs.json")

# 主仓库根目录（本脚本所在仓库）
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# AI 看板仓库（独立工作目录）
AI_REPO = "/Users/xiaoxiao/WorkBuddy/2026-08-01-14-08-40"

# 任务配置：基于仓库根目录解析（不再硬编码绝对路径，随仓库迁移）
TASKS = {
    "news": {
        "name": "国际新闻看板",
        "cmd": [os.path.join(REPO_ROOT, "update-news.sh"), "--auto"],
        "cwd": REPO_ROOT,
    },
    "ai": {
        "name": "AI 动向看板",
        "cmd": ["bash", os.path.join(AI_REPO, "refresh_board.sh")],
        "cwd": AI_REPO,
    },
    "cn": {
        "name": "国内新闻看板",
        "cmd": ["bash", os.path.join(REPO_ROOT, "refresh_china_news.sh")],
        "cwd": REPO_ROOT,
    },
}


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def today():
    return datetime.now(TZ).strftime("%Y-%m-%d")


def find_missed(state):
    """返回今天缺失或失败的任务列表"""
    t = today()
    missed = []
    for key, cfg in TASKS.items():
        rec = state.get(key) or {}
        if rec.get("date") != t or rec.get("status") != "ok":
            missed.append((key, cfg, rec))
    return missed


def run_task(key, cfg):
    print(f"\n🔄 补跑 [{key}] {cfg['name']} ...")
    try:
        r = subprocess.run(cfg["cmd"], cwd=cfg["cwd"], timeout=3600)
        ok = r.returncode == 0
    except Exception as e:
        print(f"  ❌ 补跑异常: {e}")
        ok = False
    # 记录结果（复用 record_run.py）
    rec = os.path.join(os.path.dirname(os.path.abspath(__file__)), "record_run.py")
    subprocess.run([sys.executable, rec, key, "--status", "ok" if ok else "failed"])
    print(f"  {'✅ 补跑成功' if ok else '❌ 补跑失败'}")
    return ok


def main():
    dry = "--dry-run" in sys.argv
    only = None
    if "--task" in sys.argv:
        i = sys.argv.index("--task")
        if i + 1 < len(sys.argv):
            only = sys.argv[i + 1]

    state = load_state()
    missed = find_missed(state)
    if only:
        missed = [m for m in missed if m[0] == only]
        # 若指定任务今天已 ok，也列出（允许强制重跑）
        if not missed and only in TASKS:
            rec = state.get(only) or {}
            missed = [(only, TASKS[only], rec)]

    if not missed:
        print(f"✅ [{today()}] 三个看板任务均已执行，无需补跑。")
        return 0

    print(f"📋 [{today()}] 检测到 {len(missed)} 个任务今日未完成:")
    for key, cfg, rec in missed:
        last = f"{rec.get('date','?')} {rec.get('time','?')} ({rec.get('status','?')})" if rec else "无记录"
        print(f"  - [{key}] {cfg['name']} | 上次: {last}")

    if dry:
        print("\n(--dry-run 模式，未执行补跑)")
        return 0

    print("\n🚀 开始串行补跑...")
    results = {key: run_task(key, cfg) for key, cfg, _ in missed}
    failed = [k for k, ok in results.items() if not ok]
    if failed:
        print(f"\n⚠️ 部分补跑失败: {failed}（可稍后重试）")
        return 1
    print("\n🎉 全部补跑完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
