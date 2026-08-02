#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inject_nav.py — Ira 信息看板体系 统一导航注入脚本（v3）
幂等：若目标 HTML 已包含 NAV-MARKER，则跳过，不重复注入。
处理对象：international-news.html / ai-company-intel.html / china-news.html
导航结构：Ira 信息看板（门户） | 国际新闻看板 | AI 动向看板 | 国内新闻看板
用法: python3 scripts/inject_nav.py [html路径...]
     不传路径时默认处理项目根目录与 gh-pages/ 下的三个子看板页面
"""
import sys, os, re

MARKER = "IRA-NAV"

NAV_SNIPPET = '''<!-- ===== IRA-NAV: Ira 信息看板 统一导航（自动注入，勿删） ===== -->
<div class="ira-nav" style="max-width:1400px;margin:14px auto 0;padding:9px 18px;background:#fff;border:1px solid #e4e7ee;border-radius:12px;box-shadow:0 2px 8px rgba(28,36,52,.06);display:flex;align-items:center;gap:6px;flex-wrap:wrap;font-size:13px;">
  <span style="font-weight:700;color:#1c2434;margin-right:4px;background:linear-gradient(120deg,#3b4a8c,#8a1f1f,#b4251a);-webkit-background-clip:text;background-clip:text;color:transparent;">Ira 信息看板</span>
  <a href="./" style="color:#3b4a8c;text-decoration:none;font-weight:600;padding:4px 12px;border-radius:8px;background:#eef0fa;">🏠 门户首页</a>
  <a href="international-news.html" style="color:#3b4a8c;text-decoration:none;font-weight:600;padding:4px 12px;border-radius:8px;background:#eef0fa;">🌍 国际新闻看板</a>
  <a href="ai-company-intel.html" style="color:#b4251a;text-decoration:none;font-weight:600;padding:4px 12px;border-radius:8px;background:#fdf0ef;">🤖 AI 动向看板</a>
  <a href="china-news.html" style="color:#8a1f1f;text-decoration:none;font-weight:600;padding:4px 12px;border-radius:8px;background:#fdf0ef;">🇨🇳 国内新闻看板</a>
  <span style="color:#a0a8b5;margin-left:auto;font-size:12px;">每日 09:30 自动刷新</span>
</div>
<!-- ===== /IRA-NAV ===== -->'''


def inject(content: str) -> str:
    if MARKER in content:
        return content  # 已注入，幂等跳过
    # 移除旧版 KB-NAV / 旧 IRA-NAV
    content = re.sub(r"<!-- ===== KB-NAV:.*?/KB-NAV ===== -->\s*", "", content, flags=re.S)
    content = re.sub(r"<!-- ===== IRA-NAV:.*?/IRA-NAV ===== -->\s*", "", content, flags=re.S)
    body_match = re.search(r"<body[^>]*>", content)
    if body_match:
        pos = body_match.end()
        return content[:pos] + "\n" + NAV_SNIPPET + content[pos:]
    return NAV_SNIPPET + "\n" + content


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    targets = sys.argv[1:] if len(sys.argv) > 1 else [
        os.path.join(base, "international-news.html"),
        os.path.join(base, "gh-pages", "international-news.html"),
        os.path.join(base, "ai-company-intel.html"),
        os.path.join(base, "gh-pages", "ai-company-intel.html"),
        os.path.join(base, "china-news.html"),
        os.path.join(base, "gh-pages", "china-news.html"),
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
