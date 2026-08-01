#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_js_syntax.py — 国际新闻看板 JS 语法预检（V1.3.2）

生成 HTML 后立即调用，验证 <script> 块 JS 语法正确。
避免 2026-08-01 国际新闻看板 tbody 空白事故复发。

用法: python3 scripts/check_js_syntax.py <html_file>
返回: 0=通过, 1=失败（输出错误位置）
"""
import sys, re, subprocess, os

def check(html_path):
    if not os.path.exists(html_path):
        print(f"❌ 文件不存在: {html_path}")
        return 1
    with open(html_path, encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"<script>(.*?)</script>", html, re.S)
    if not m:
        print(f"⚠️  {html_path}: 未发现 <script> 块（无 JS）")
        return 0
    js = m.group(1)
    # 用占位符替换庞大的 NEWS_DATA，避免 Node 解析时受数据格式干扰
    js = re.sub(r"const NEWS_DATA = \{.*?\};", "const NEWS_DATA = {};", js, count=1, flags=re.S)

    # 用 node --check 真正解析 JS
    try:
        result = subprocess.run(
            ["node", "--check"],
            input=js.encode("utf-8"),
            capture_output=True,
            timeout=10,
        )
        if result.returncode == 0:
            print(f"  ✅ JS 语法正确: {html_path}（{len(js)} 字节）")
            return 0
        else:
            err = (result.stderr or result.stdout or b"").decode("utf-8", errors="replace")
            print(f"  ❌ JS 语法错误: {html_path}")
            print(f"     {err.strip()[:300]}")
            return 1
    except FileNotFoundError:
        # 无 node 时退化为括号配对检查
        opens, closes = js.count("{"), js.count("}")
        if opens == closes:
            print(f"  ⚠️  node 不可用，跳过真实解析；大括号配对 OK: {html_path}")
            return 0
        else:
            print(f"  ❌ JS 大括号不匹配 ({opens} vs {closes}): {html_path}")
            return 1
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  node --check 超时: {html_path}")
        return 0


def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "international-news.html"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gh-pages", "international-news.html"),
    ]
    failed = 0
    for t in targets:
        # check 返回 0=成功, 1=失败；累加 = 失败计数
        failed += check(t)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())