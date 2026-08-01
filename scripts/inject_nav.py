#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inject_nav.py — 国际新闻看板 ↔ AI 公司情报看板 双向导航注入脚本
幂等：若 index.html 已包含 AI 看板导航入口，则跳过，不重复注入。
用法: python3 scripts/inject_nav.py [index.html路径...]
     不传路径时默认处理项目根目录 index.html 与 gh-pages/index.html
"""
import sys, os, re

NAV_SNIPPET = '''<!-- ===== KB-NAV: 国际新闻看板 ↔ AI 情报看板（自动注入，勿删） ===== -->
<div class="kb-nav" style="max-width:1400px;margin:14px auto 0;padding:8px 18px;background:#fff;border-radius:10px;box-shadow:0 2px 6px rgba(0,0,0,.07);display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:13px;">
  <span style="font-weight:600;color:#555;">🗂️ 看板导航</span>
  <a href="./" style="color:#667eea;text-decoration:none;font-weight:500;padding:4px 12px;border-radius:6px;background:#f0f1ff;">🌍 国际新闻看板</a>
  <a href="ai-company-intel.html" style="color:#b4251a;text-decoration:none;font-weight:500;padding:4px 12px;border-radius:6px;background:#fdf0ef;">🤖 AI 公司情报看板</a>
  <span style="color:#aaa;margin-left:auto;font-size:12px;">每日 09:40 自动刷新</span>
</div>
<!-- ===== /KB-NAV ===== -->'''

MARKER = "KB-NAV"

def inject(content: str) -> str:
    if MARKER in content:
        return content  # 已注入，幂等跳过
    # 插入到 body 开始之后（若存在 body 标签）；否则插到 head 前
    body_match = re.search(r"<body[^>]*>", content)
    if body_match:
        pos = body_match.end()
        return content[:pos] + "\n" + NAV_SNIPPET + content[pos:]
    return NAV_SNIPPET + "\n" + content

def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "index.html"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gh-pages", "index.html"),
    ]
    for t in targets:
        if not os.path.exists(t):
            print(f"  ⏭️  跳过（不存在）: {t}")
            continue
        with open(t, encoding="utf-8") as f:
            content = f.read()
        new = inject(content)
        if new == content:
            print(f"  ✅ 已含导航，跳过: {t}")
        else:
            with open(t, "w", encoding="utf-8") as f:
                f.write(new)
            print(f"  🔗 已注入导航: {t}")

if __name__ == "__main__":
    main()
