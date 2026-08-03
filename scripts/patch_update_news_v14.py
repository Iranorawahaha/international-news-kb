#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修改 update-news.sh: 模板改为从文件加载 + 栏目胶囊生成"""
import sys

p = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/update-news.sh'
src = open(p, encoding='utf-8').read()

# 1. 栏目 tab 生成改为大号胶囊结构
old = """column_tabs_html = '<button class="tab-btn active" data-column="all">全部(%d)</button>' % total_count
for _c in COLUMN_ORDER:
    column_tabs_html += '<button class="tab-btn" data-column="%s">%s %s(%d)</button>' % (_c, COLUMN_ICONS.get(_c, ''), _c, column_counts.get(_c, 0))"""
new = """# V1.4: 栏目胶囊组（大号分段控件）
column_tabs_html = '<button class="pill active" data-column="all"><span class="pill-icon">\\U0001f4cb</span>全部<span class="pill-count">%d</span></button>' % total_count
for _c in COLUMN_ORDER:
    _icon = COLUMN_ICONS.get(_c, '\\U0001f4cc')
    _cnt = column_counts.get(_c, 0)
    column_tabs_html += '<button class="pill" data-column="%s"><span class="pill-icon">%s</span>%s<span class="pill-count">%d</span></button>' % (_c, _icon, _c, _cnt)"""
assert old in src, 'column_tabs_html 段未找到'
src = src.replace(old, new)
print('✅ 1. 栏目胶囊生成已改')

# 2. 模板加载：定位模板段并替换
start_marker = "# ⭐ V1.2 HTML模板"
idx_start = src.find(start_marker)
assert idx_start != -1, '模板起始标记未找到'
# 找 GENERATE_HTML_V12 结束标记（下一个出现的）
idx_end = src.find("GENERATE_HTML_V12", idx_start)
assert idx_end != -1, 'GENERATE_HTML_V12 结束标记未找到'

new_gen = """# ⭐ V1.4 HTML模板（深色情报指挥风）— 从独立模板文件加载，占位符替换
TEMPLATE_PATH = PROJECT_ROOT / "scripts" / "intl_template_v14.html"
with open(TEMPLATE_PATH, 'r', encoding='utf-8') as _tf:
    html_content = _tf.read()

# 占位符替换
html_content = html_content.replace('__NOW_STR__', now_str)
html_content = html_content.replace('__COLUMN_TABS__', column_tabs_html)
html_content = html_content.replace('__DATE_OPTIONS__', tabs_html)
html_content = html_content.replace('__TOTAL_COUNT__', str(total_count))
html_content = html_content.replace('__SOURCE_COUNT__', str(len(sources)))
html_content = html_content.replace('__CATEGORY_COUNT__', str(len(categories)))
html_content = html_content.replace('__SUMMIT_COUNT__', str(summit_count))
html_content = html_content.replace('__DATE_COUNT__', str(stats.get('dateCount', len(dates))))
html_content = html_content.replace('__NOW_FULL__', now_full)
html_content = html_content.replace('__NEWS_DATA_JSON__', json.dumps(v12_data, ensure_ascii=False))
html_content = html_content.replace('COLUMN_TABS_HOLDER', column_tabs_html)

print(f"\\U0001f4ca 生成V1.4 HTML: {total_count}条新闻, {len(dates)}天, 栏目: {column_counts}")
"""
src = src[:idx_start] + new_gen + src[idx_end:]
open(p, 'w', encoding='utf-8').write(src)
print('✅ 2. 模板加载与占位符替换已写入')
