#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V1.5 补丁：栏目侧边栏 + 日期表头按钮 + 新占位符"""
import re

p = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/update-news.sh'
src = open(p, encoding='utf-8').read()

# 1. 栏目胶囊生成改为侧边栏列表项
old = """# V1.4: 栏目胶囊组（大号分段控件）
column_tabs_html = '<button class="pill active" data-column="all"><span class="pill-icon">\\U0001f4cb</span>全部<span class="pill-count">%d</span></button>' % total_count
for _c in COLUMN_ORDER:
    _icon = COLUMN_ICONS.get(_c, '\\U0001f4cc')
    _cnt = column_counts.get(_c, 0)
    column_tabs_html += '<button class="pill" data-column="%s"><span class="pill-icon">%s</span>%s<span class="pill-count">%d</span></button>' % (_c, _icon, _c, _cnt)"""
new = """# V1.5: 左侧栏目侧边栏列表（悬浮 sticky）
column_tabs_html = '<button class="col-item active" data-column="all"><span class="ic">\\U0001f4cb</span><span class="nm">全部</span><span class="cnt">%d</span></button>' % total_count
for _c in COLUMN_ORDER:
    _icon = COLUMN_ICONS.get(_c, '\\U0001f4cc')
    _cnt = column_counts.get(_c, 0)
    column_tabs_html += '<button class="col-item" data-column="%s"><span class="ic">%s</span><span class="nm">%s</span><span class="cnt">%d</span></button>' % (_c, _icon, _c, _cnt)"""
assert old in src, 'column_tabs_html V1.4 段未找到'
src = src.replace(old, new)
print('✅ 1. 栏目侧边栏列表已生成')

# 2. 日期 tab/下拉改为日期表头按钮
old2 = """# 构建日期下拉 options（V1.4: 日期筛选改为独立下拉选择器）
tabs_html = '<option value=\"all\">全部日期（%d 条）</option>' % total_count
for d in dates:
    count = len(archive.get(d, []))
    tabs_html += '<option value=\"%s\">%s（%d 条）</option>' % (d, d.replace('2026-', '2026/'), count)"""
new2 = """# V1.5: 顶部日期表头按钮（横向）
tabs_html = '<button class=\"date-btn active\" data-date=\"all\">\\U0001f4c5 全部日期（%d）</button>' % total_count
for d in dates:
    count = len(archive.get(d, []))
    tabs_html += '<button class=\"date-btn\" data-date=\"%s\">%s（%d）</button>' % (d, d.replace('2026-', '8'), count)"""
assert old2 in src, 'tabs_html V1.4 段未找到'
src = src.replace(old2, new2)
print('✅ 2. 日期表头按钮已生成')

# 3. 模板加载改为 V1.5 占位符
old3 = "TEMPLATE_PATH = PROJECT_ROOT / \"scripts\" / \"intl_template_v14.html\""
new3 = "TEMPLATE_PATH = PROJECT_ROOT / \"scripts\" / \"intl_template_v15.html\""
assert old3 in src
src = src.replace(old3, new3)
print('✅ 3. 模板路径已切换 v15')

# 4. 增加占位符：TODAY_COUNT + COLUMN_SIDEBAR + DATE_HEAD_BUTTONS
old4 = """html_content = html_content.replace('__NOW_STR__', now_str)
html_content = html_content.replace('__COLUMN_TABS__', column_tabs_html)
html_content = html_content.replace('__DATE_OPTIONS__', tabs_html)
html_content = html_content.replace('__TOTAL_COUNT__', str(total_count))
html_content = html_content.replace('__SOURCE_COUNT__', str(len(sources)))
html_content = html_content.replace('__CATEGORY_COUNT__', str(len(categories)))
html_content = html_content.replace('__SUMMIT_COUNT__', str(summit_count))
html_content = html_content.replace('__DATE_COUNT__', str(stats.get('dateCount', len(dates))))
html_content = html_content.replace('__NOW_FULL__', now_full)
html_content = html_content.replace('__NEWS_DATA_JSON__', json.dumps(v12_data, ensure_ascii=False))
html_content = html_content.replace('COLUMN_TABS_HOLDER', column_tabs_html)"""
new4 = """# 计算今日新增（北京时间今日）
from datetime import datetime, timezone, timedelta as _td
_TZ = timezone(_td(hours=8))
_today = datetime.now(_TZ).strftime('%Y-%m-%d')
_today_count = 0
for _d, _arts in archive.items():
    for _a in _arts:
        if _a.get('date') == _today:
            _today_count += 1

html_content = html_content.replace('__NOW_STR__', now_str)
html_content = html_content.replace('__NOW_FULL__', now_full)
html_content = html_content.replace('__TOTAL_COUNT__', str(total_count))
html_content = html_content.replace('__TODAY_COUNT__', str(_today_count))
html_content = html_content.replace('__SOURCE_COUNT__', str(len(sources)))
html_content = html_content.replace('__CATEGORY_COUNT__', str(len(categories)))
html_content = html_content.replace('__SUMMIT_COUNT__', str(summit_count))
html_content = html_content.replace('__DATE_COUNT__', str(stats.get('dateCount', len(dates))))
html_content = html_content.replace('__COLUMN_SIDEBAR__', column_tabs_html)
html_content = html_content.replace('__DATE_HEAD_BUTTONS__', tabs_html)
html_content = html_content.replace('__NEWS_DATA_JSON__', json.dumps(v12_data, ensure_ascii=False))"""
assert old4 in src, '占位符替换段未找到'
src = src.replace(old4, new4)
print('✅ 4. V1.5 占位符已替换（新增 TODAY_COUNT/COLUMN_SIDEBAR/DATE_HEAD_BUTTONS）')

# 5. print 标题改为 V1.5
old5 = "print(f\"\\U0001f4ca 生成V1.4 HTML: {total_count}条新闻, {len(dates)}天, 栏目: {column_counts}\")"
new5 = "print(f\"\\U0001f4ca 生成V1.5 HTML: {total_count}条新闻, {len(dates)}天, 栏目: {column_counts}\")"
assert old5 in src
src = src.replace(old5, new5)
print('✅ 5. 日志标题已改为 V1.5')

open(p, 'w', encoding='utf-8').write(src)
print('\n✅ V1.5 补丁完成')
