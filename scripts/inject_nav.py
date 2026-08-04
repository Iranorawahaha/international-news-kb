#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inject_nav.py — Ira 信息看板体系 统一导航注入脚本（v4 · 三色区分）
国际=蓝色 / 国内=红色 / AI=琥珀金 · 单行紧凑型
"""
import sys, os, re

MARKER = "IRA-NAV-V4"

NAV_SNIPPET = '''<!-- ===== IRA-NAV-V4: Ira 信息看板 统一导航（自动注入，勿删） ===== -->
<div class="ira-nav-v4" style="max-width:1400px;margin:8px auto 0;padding:7px 16px;background:#fff;border:1px solid #e4e7ee;border-radius:12px;box-shadow:0 1px 6px rgba(28,36,52,.05);display:flex;align-items:center;gap:10px;flex-wrap:wrap;font-size:13px;">
  <a href="./" style="font-weight:700;color:#4b5563;text-decoration:none;padding:0 6px 0 0;border-right:1px solid #e5e7eb;margin-right:2px;">🏠 Ira 信息看板</a>
  <a href="international-news.html" style="color:#2563eb;text-decoration:none;font-weight:600;padding:5px 14px;border-radius:8px;background:#eff6ff;border:1px solid #bfdbfe;">🌍 国际</a>
  <a href="china-news.html" style="color:#c41230;text-decoration:none;font-weight:600;padding:5px 14px;border-radius:8px;background:#fff5f5;border:1px solid #fecaca;">🇨🇳 国内</a>
  <a href="ai-company-intel.html" style="color:#d97706;text-decoration:none;font-weight:600;padding:5px 14px;border-radius:8px;background:#fffbeb;border:1px solid #fde68a;">🤖 AI动向</a>
  <span style="color:#9ca3af;margin-left:auto;font-size:11.5px;">每日 09:30 刷新 · 滚动 7 天</span>
</div>
<!-- ===== /IRA-NAV-V4 ===== -->'''


def inject(content: str) -> str:
    if MARKER in content:
        return content
    # 清除所有旧版导航
    content = re.sub(r"<!-- ===== IRA-NAV.*?/IRA-NAV(?:-V\d)? ===== -->\s*", "", content, flags=re.S)
    content = re.sub(r"<!-- ===== KB-NAV:.*?/KB-NAV ===== -->\s*", "", content, flags=re.S)
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
            print(f"  ✅ 已含V4导航，跳过: {t}")
        else:
            with open(t, "w", encoding="utf-8") as f:
                f.write(new)
            print(f"  🔗 已注入V4导航: {t}")


if __name__ == "__main__":
    main()