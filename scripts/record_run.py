#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
record_run.py — 看板刷新任务执行状态记录（C 方案：错过补跑）

用法: python3 record_run.py <task> [--status ok|failed]
  <task>: news | ai | cn

将执行状态写入 ~/.workbuddy/ira_runs.json:
  {"news": {"date": "2026-08-03", "time": "09:31", "status": "ok"},
   "ai":   {"date": "2026-08-03", "time": "09:32", "status": "ok"},
   "cn":   {"date": "2026-08-03", "time": "09:33", "status": "failed"}}

check_missed_runs.py 据此判断"今天某任务是否已执行"，未执行则补跑。
"""
import json
import os
import sys
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.workbuddy/ira_runs.json")
VALID_TASKS = ("news", "ai", "cn")


def load():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save(data):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in VALID_TASKS:
        print("用法: record_run.py <news|ai|cn> [--status ok|failed]")
        return 1
    task = sys.argv[1]
    status = "ok"
    if "--status" in sys.argv:
        i = sys.argv.index("--status")
        if i + 1 < len(sys.argv) and sys.argv[i + 1] in ("ok", "failed"):
            status = sys.argv[i + 1]

    now = datetime.now()
    data = load()
    data[task] = {"date": now.strftime("%Y-%m-%d"), "time": now.strftime("%H:%M"), "status": status}
    save(data)
    print(f"✅ 已记录 {task} 执行: {data[task]['date']} {data[task]['time']} ({status})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
