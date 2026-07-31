#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际新闻看板 - 用户使用说明 PDF生成器
生成专业的PDF文档用于向同事分享
"""

from fpdf import FPDF
import os

class NewsDashboardPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        # 页眉
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'International News Dashboard V1.1 - User Guide', 0, 0, 'R')
        self.ln(15)

    def footer(self):
        # 页脚
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(31, 73, 125)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(70, 70, 70)
        self.cell(0, 8, title, 0, 1, 'L')
        self.ln(1)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def bullet_point(self, text, indent=10):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        self.set_x(indent)
        self.multi_cell(0, 6, f"• {text}")
        self.ln(1)

    def source_item(self, name, desc, lang=''):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(31, 73, 125)
        self.cell(50, 6, name, 0, 0)
        if lang:
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(100, 100, 100)
            self.cell(20, 6, f"({lang})", 0, 0)
        self.ln()
        self.set_font('Helvetica', '', 9)
        self.set_text_color(80, 80, 80)
        self.set_x(20)
        self.multi_cell(0, 5, desc)
        self.ln(2)


def create_user_guide():
    pdf = NewsDashboardPDF()
    pdf.add_page()

    # ========== 封面/标题 ==========
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(31, 73, 125)
    pdf.ln(20)
    pdf.cell(0, 15, 'International News', 0, 1, 'C')
    pdf.cell(0, 15, 'Dashboard', 0, 1, 'C')

    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, '(KJ-)', 0, 1, 'C')
    pdf.ln(10)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(70, 70, 70)
    pdf.cell(0, 8, 'V1.1 User Guide', 0, 1, 'C')
    pdf.ln(5)

    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, '2026-07-31', 0, 1, 'C')
    pdf.ln(30)

    # 分隔线
    pdf.set_draw_color(200, 200, 200)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(10)

    # ========== 访问地址 ==========
    pdf.chapter_title('1. Access URL')
    pdf.body_text(
        "The dashboard is deployed on GitHub Pages with global CDN acceleration and HTTPS encryption."
    )
    pdf.ln(2)
    pdf.set_fill_color(240, 248, 255)
    pdf.set_font('Courier', 'B', 11)
    pdf.set_text_color(31, 73, 125)
    pdf.cell(0, 10, 'https://iranorawahaha.github.io/international-news-kb/', 1, 1, 'C', fill=True)
    pdf.ln(5)
    pdf.body_text(
        "The page is a single-file self-contained HTML (no external dependencies), ensuring fast loading "
        "and compatibility across devices (desktop/tablet/mobile)."
    )

    # ========== 页面功能介绍 ==========
    pdf.add_page()
    pdf.chapter_title('2. Page Features Overview')

    pdf.section_title('2.1 Statistics Cards (Top)')
    pdf.body_text("Four key metrics displayed at the top of the page:")
    pdf.bullet_point("Total news count: Number of articles in current update")
    pdf.bullet_point("Source count: Number of media sources covered")
    pdf.bullet_point("Category count: News topic categories covered")
    pdf.bullet_point("Summit-level news: Highest priority items marked with gold star")

    pdf.section_title('2.2 Bilingual Titles')
    pdf.body_text(
        "All English-source articles display bilingual titles for easy cross-reference:"
    )
    pdf.ln(1)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(31, 73, 125)
    pdf.set_x(20)
    pdf.multi_cell(0, 6, "English Original Title (dark blue italic)")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.set_x(20)
    pdf.multi_cell(0, 6, "Chinese Translation (black regular)")
    pdf.ln(3)
    pdf.body_text(
        "This design enables users to search original English content while understanding the Chinese context."
    )

    pdf.section_title('2.3 Five-Level Importance Classification')
    pdf.body_text("News importance is classified into 5 levels based on priority_score:")
    pdf.ln(1)

    # 表格：5级分类
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_fill_color(255, 215, 0)  # 金色
    pdf.set_text_color(0, 0, 0)
    pdf.cell(40, 7, ' Summit Level', 1, 0, 'C', fill=True)
    pdf.cell(30, 7, ' >=95', 1, 0, 'C', fill=True)
    pdf.cell(110, 7, ' China-US summit / Head-of-state level news', 1, 1, 'C', fill=True)

    pdf.set_fill_color(220, 53, 69)  # 红色
    pdf.set_text_color(255, 255, 255)
    pdf.cell(40, 7, ' Extremely High', 1, 0, 'C', fill=True)
    pdf.cell(30, 7, ' 90-94', 1, 0, 'C', fill=True)
    pdf.cell(110, 7, ' Major breaking news / Geopolitical events', 1, 1, 'C', fill=True)

    pdf.set_fill_color(255, 140, 0)  # 橙色
    pdf.set_text_color(0, 0, 0)
    pdf.cell(40, 7, ' High', 1, 0, 'C', fill=True)
    pdf.cell(30, 7, ' 85-89', 1, 0, 'C', fill=True)
    pdf.cell(110, 7, ' Important policy / Economic developments', 1, 1, 'C', fill=True)

    pdf.set_fill_color(255, 193, 7)  # 黄色
    pdf.cell(40, 7, ' Medium', 1, 0, 'C', fill=True)
    pdf.cell(30, 7, ' 75-84', 1, 0, 'C', fill=True)
    pdf.cell(110, 7, ' Noteworthy regional news', 1, 1, 'C', fill=True)

    pdf.set_fill_color(40, 167, 69)  # 绿色
    pdf.set_text_color(255, 255, 255)
    pdf.cell(40, 7, ' Low', 1, 0, 'C', fill=True)
    pdf.cell(30, 7, ' <75', 1, 0, 'C', fill=True)
    pdf.cell(110, 7, ' Background / Reference information', 1, 1, 'C', fill=True)
    pdf.ln(5)

    pdf.section_title('2.4 Table Columns (9 columns)')
    columns = [
        ("No.", "Serial number"),
        ("Date", "Publication date (YYYY-MM-DD)"),
        ("Title", "Bilingual display (EN + ZH)"),
        ("Summary", "Key points (first 120 chars)"),
        ("Source", "Media outlet name"),
        ("Category", "Topic classification"),
        ("Importance", "5-level classification badge"),
        ("Keywords", "Tag-style keywords"),
        ("Link", "Original article link button"),
    ]
    for col_name, col_desc in columns:
        pdf.bullet_point(f"{col_name}: {col_desc}")

    # ========== 机制说明 ==========
    pdf.add_page()
    pdf.chapter_title('3. Collection Mechanism')

    pdf.section_title('3.1 Dual-Layer Architecture')
    pdf.body_text(
        "The system employs a dual-layer collection strategy to ensure comprehensive coverage "
        "and high-quality content:"
    )
    pdf.ln(2)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(31, 73, 125)
    pdf.cell(0, 8, 'Layer 1: Basic Collection (requests library)', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.bulletPoint("Chinese sources: People's Daily, MFA, Global Times, etc.")
    pdf.bulletPoint("Advantages: Fast speed, high stability, no API required")
    pdf.bulletPoint("Coverage: 17 available sources from 30 configured")
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(31, 73, 125)
    pdf.cell(0, 8, 'Layer 2: WebFetch API Supplement (WorkBuddy Environment)', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.bulletPoint("English authoritative sources: Reuters, BBC, SCMP, Guardian, CNN, NYT, etc.")
    pdf.bulletPoint("Advantages: Bypasses anti-scraping, high quality, real-time")
    pdf.bulletPoint("Coverage: 8-10 premium English sources")
    pdf.ln(3)

    pdf.section_title('3.2 Quality Control System')
    pdf.body_text("Multi-stage quality assurance mechanism:")

    quality_steps = [
        ("Deduplication", "Automatic removal of duplicate articles by title similarity"),
        ("URL Validation", "Mandatory URL field check (>=95% coverage requirement)"),
        ("Importance Scoring", "AI-assisted priority scoring based on content analysis"),
        ("Category Classification", "Automatic tagging into 6+ categories"),
        ("Summit Detection", "Auto-marking China-US head-of-state level news"),
    ]
    for step_name, step_desc in quality_steps:
        pdf.bullet_point(f"{step_name}: {step_desc}")

    pdf.section_title('3.3 Update Frequency')
    pdf.body_text(
        "Manual updates twice daily to ensure data freshness:\n"
        "- Morning update: 09:30 (covers overnight US/Europe news)\n"
        "- Afternoon update: 17:00 (covers same-day Asia dynamics)\n\n"
        "Each update cycle takes 3-5 minutes, producing 30-60 curated articles."
    )

    # ========== 信源清单 ==========
    pdf.add_page()
    pdf.chapter_title('4. Source List')

    pdf.section_title('4.1 English Authoritative Sources (Primary)')
    pdf.body_text(
        "High-value English media outlets collected via WebFetch API, "
        "providing global perspective and original reporting:"
    )
    pdf.ln(2)

    english_sources = [
        ("Reuters", "World's leading news agency, strong in finance/politics", "English"),
        ("BBC News", "British public broadcaster, balanced international coverage", "English"),
        ("South China Morning Post", "Hong Kong-based, expert on China/Asia affairs", "English"),
        ("The Guardian", "UK quality press, in-depth analysis pieces", "English"),
        ("CNN", "US 24-hour news network, breaking news leader", "English"),
        ("New York Times", "US newspaper of record, influential commentary", "English"),
        ("Al Jazeera", "Qatar-based, unique Middle East/South perspective", "English"),
        ("Washington Post", "US prestige paper, strong politics coverage", "English"),
        ("Associated Press", "US news cooperative, factual reporting", "English"),
    ]

    for src_name, src_desc, src_lang in english_sources:
        pdf.source_item(src_name, src_desc, src_lang)

    pdf.ln(3)
    pdf.section_title('4.2 Chinese Sources (Supplementary)')
    pdf.body_text("Domestic Chinese media for official positions and local context:")
    pdf.ln(2)

    chinese_sources = [
        ("People's Daily (人民网)", "Official CPC mouthpiece, policy announcements"),
        ("China MFA (外交部)", "Official diplomatic statements, spokesperson briefings"),
        ("Global Times (环球网)", "Nationalistic tabloid, opinion pieces"),
        ("CRI Online (国际在线)", "State-owned international communication"),
    ]

    for src_name, src_desc in chinese_sources:
        pdf.source_item(src_name, src_desc)

    # ========== 新闻筛选标准 ==========
    pdf.add_page()
    pdf.chapter_title('5. News Selection Criteria')

    pdf.section_title('5.1 Content Quality Standards')
    criteria_quality = [
        "Authoritative sources only (no social media/self-media)",
        "Original reporting preferred over reposts/aggregation",
        "Factual accuracy over sensationalism",
        "Substantive content (minimum 150 characters summary)",
        "Complete metadata (title, date, source, URL mandatory)",
    ]
    for criterion in criteria_quality:
        pdf.bullet_point(criterion)

    pdf.ln(3)
    pdf.section_title('5.2 Topic Prioritization')
    pdf.body_text("Topics are weighted by relevance to target audience:")
    pdf.ln(1)

    priorities = [
        ("Highest Priority", "China-US relations, trade negotiations, summit diplomacy"),
        ("High Priority", "Economic sanctions, AI/tech competition, geopolitical shifts"),
        ("Medium Priority", "Regional security, multilateral organizations, energy"),
        ("Background", "Culture, education, environment, development news"),
    ]
    for prio_level, prio_desc in priorities:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(31, 73, 125)
        pdf.cell(35, 6, prio_level + ":", 0, 0)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, prio_desc)
        pdf.ln(1)

    pdf.ln(3)
    pdf.section_title('5.3 Category Coverage (6 major categories)')
    categories = [
        "China-US Relations",
        "Geopolitics & Diplomacy",
        "Global Economy & Trade",
        "Technology & AI Competition",
        "Security & Conflicts",
        "Regional Dynamics (Europe/Middle East/Asia-Pacific)",
    ]
    for cat in categories:
        pdf.bullet_point(cat)

    pdf.ln(3)
    pdf.section_title('5.4 Summit-Level Identification Criteria')
    pdf.body_text(
        "Articles are marked as 'Summit Level' (gold star badge) when they meet ANY criterion:"
    )
    summit_criteria = [
        "Direct involvement of China/US heads of state (Xi Jinping, Trump/Biden)",
        "High-level diplomatic meetings (cabinet-level or above)",
        "Summit preparation/follow-up activities",
        "Major policy decisions affecting bilateral relations",
        "Historic significance in China-US relations context",
    ]
    for criterion in summit_criteria:
        pdf.bullet_point(criterion)

    # ========== 使用提示 ==========
    pdf.add_page()
    pdf.chapter_title('6. Usage Tips')

    pdf.section_title('6.1 Browsing Recommendations')
    tips_browse = [
        "Start from top: Summit-level news (gold badges) are most important",
        "Use bilingual titles: Click English title links for original articles",
        "Check source diversity: Mix of Western and Asian perspectives",
        "Pay attention to dates: News updated twice daily (09:30/17:00)",
        "Use Ctrl+F: Search keywords within page for specific topics",
    ]
    for tip in tips_browse:
        pdf.bullet_point(tip)

    pdf.ln(3)
    pdf.section_title('6.2 Understanding Importance Badges')
    pdf.body_text(
        "The five-level color-coded system helps quickly identify news priority:\n\n"
        "Gold star = Must-read for leadership briefing\n"
        "Red = Breaking developments requiring immediate attention\n"
        "Orange = Important trends affecting policy decisions\n"
        "Yellow = Useful context for comprehensive understanding\n"
        "Green = Reference material for deeper research"
    )

    pdf.ln(3)
    pdf.section_title('6.3 Technical Notes')
    tech_notes = [
        "Page loads completely offline after first visit (service worker ready)",
        "Mobile-responsive design optimized for tablets and phones",
        "All external links open in new tabs (original source articles)",
        "Browser cache: Press Cmd+Shift+R (Mac) / Ctrl+Shift+R (Windows) to force refresh",
        "HTTPS encrypted connection ensures secure browsing",
    ]
    for note in tech_notes:
        pdf.bullet_point(note)

    pdf.ln(5)

    # ========== 联系方式/反馈 ==========
    pdf.set_draw_color(200, 200, 200)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(8)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(70, 70, 70)
    pdf.cell(0, 8, 'Feedback & Suggestions', 0, 1, 'C')
    pdf.ln(3)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 6,
        "This dashboard is maintained for internal sharing purposes.\n"
        "If you have suggestions for new sources, feature requests, or content feedback,\n"
        "please contact the maintainer directly.",
        align='C'
    )

    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, 'Document generated: 2026-07-31 | Version: V1.1 | Engine: International News Dashboard', 0, 1, 'C')

    # 保存PDF
    output_path = '/Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50/docs/User-Guide-V1.1.pdf'
    pdf.output(output_path)
    print(f"PDF generated successfully: {output_path}")
    return output_path


if __name__ == '__main__':
    output_file = create_user_guide()
    print(f"\n✅ User guide PDF created: {output_file}")
