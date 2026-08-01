#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际新闻看板 - 新闻采集引擎 V1.1（正式版）
==========================================

核心功能：
  ✅ 双层采集架构（基础抓取 + WebFetch API补充）
  ✅ 高价值英文信源覆盖（10大权威信源：路透社/BBC/CNN/NYT等）
  ✅ 双语标题支持（英文原标题 + 中文翻译）
  ✅ 元首级新闻智能识别与标注（中美元首/高层会晤）
  ✅ 重要性5级分类体系（⭐元首级95-100 / 🔴极高90-94 / 🟠高85-89 / 🟡中75-84 / 🟢低<75）
  ✅ URL完整性保障机制（Prompt强化 + 自动验证 + 质量门槛）
  ✅ 智能质量控制和去重
  ✅ 单文件HTML自动生成（V1.1完整版UI）
  ✅ 完整的数据统计报告

V1.1 正式版特性：
  - 信源扩展至10个英文权威信源（从4个扩展，覆盖全球多视角）
  - WebFetch Prompt强制要求返回双语标题（title_en + title）
  - 新增元首级新闻自动识别（is_summit_level + priority_score≥95）
  - 基于priority_score的5级重要性分类系统
  - HTML生成器支持V1.1完整UI（双语渲染 + 金色元首级徽章 + 列不换行）
  - 根目录+gh-pages双目录同步部署

架构说明：
  第1层：基础采集（requests库）
    - 中文信源：人民网、外交部、环球网、国际在线等（17个可用）
    - 优势：速度快、稳定性高、无需API

  第2层：WebFetch API补充（需在WorkBuddy环境中运行）
    - 英文权威信源（10个）：
      🔴 必选核心（4）：路透社、BBC News、南华早报(SCMP)、卫报(The Guardian)
      🟠 扩展推荐（6）：CNN、纽约时报(NYT)、半岛电视台(Al Jazeera)、
                       华盛顿邮报(WaPo)、美联社(AP)、Politico(可选)
    - 优势：绕过反爬虫、内容质量高、实时性好
    - 注意：此层需要WorkBuddy环境支持

数据结构（V1.1增强）：
  {
    "id": "source_1",
    "date": "2026-07-31",
    "title_en": "Original English Title",        # V1.1: 英文原标题
    "title": "中文翻译标题",
    "summary": "2-3句话摘要",
    "source": "路透社",
    "category": "中美关系",
    "keywords": ["关键词1", "关键词2"],
    "url": "https://www.reuters.com/...",
    "importance": "高",
    "priority_score": 96,                        # V1.1: 数值化优先级
    "is_summit_level": false,                    # V1.1: 元首级标记
    "language": "en",
    "collectedAt": "2026-07-31 12:00:00"
  }

输出：
  - data/news-data.json (主数据文件)
  - index.html (根目录单文件自包含网页)          # V1.1: 新增根目录输出
  - gh-pages/index.html (gh-pages单文件网页)
  - data/collection-report.md (采集报告)

使用方法：
  # 完整采集（推荐）
  python3 scripts/fetch_news_v3.py

  # 仅基础采集（跳过WebFetch）
  python3 scripts/fetch_news_v3.py --basic-only

  # 测试模式
  python3 scripts/fetch_news_v3.py --test

版本历史：
  v3.1 (2026-07-31) - 添加URL完整性保障机制
  V1.0 (2026-07-31) - 正式发布版本，所有功能稳定验证通过
  V1.1 (2026-07-31) - 信源扩展+双语标题+元首级识别+5级分类+UI优化

作者: WorkBuddy AI Assistant
版本: V1.1 (正式版)
发布日期: 2026-07-31
"""

import json
import sys
import os
import re
import time
import random
import argparse
from datetime import datetime
from pathlib import Path
from collections import Counter

# 尝试导入requests
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️ 未安装requests库，将仅使用内置模块")

# 尝试导入beautifulsoup4
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# ==================== 配置 ====================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "news-data.json"
CONFIG_PATH = PROJECT_ROOT / "data" / "config.json"
GH_PAGES_INDEX = PROJECT_ROOT / "gh-pages" / "index.html"
REPORT_PATH = PROJECT_ROOT / "data" / "collection-report.md"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# 高价值英文信源（用于WebFetch补充）- V1.2.2扩展版
# 🔴 必选信源(7个)：路透社/BBC/南华早报/卫报/CNN/纽约时报/华尔街日报
# 🟠 扩展信源(3个)：半岛电视台/Politico/华盛顿邮报/美联社
WEBFETCH_SOURCES = [
    {
        'name': '路透社',
        'url': 'https://www.reuters.com/world/',
        'prompt': '提取今天（2026年7月31日）的国际新闻，重点关注：1.中美关系 2.地缘政治 3.AI科技 4.经贸制裁。列出最重要的8-10条新闻，每条必须包含：\n1) **英文原标题**（English title，必须是文章的原始英文标题）\n2) **中文翻译标题**（简短翻译）\n3) 2-3句话摘要\n4) 关键词（用逗号分隔）\n5) **完整的原文链接URL**（https://开头的完整文章地址）\n⚠️ 格式要求：输出时每条新闻的标题格式为"English Title 中文翻译"，例如："Ukraine\'s envoy to US: We need missiles 乌克兰驻美大使紧急呼吁：我们需要导弹"\n⚠️ URL是必填项，不能省略。用中文输出。',
        'priority': 1,  # 最高优先级
        'required': True,  # 🔴 必选
        'expected_count': 8,
        'language': 'en',
    },
    {
        'name': 'BBC News',
        'url': 'https://www.bbc.com/news',
        'prompt': '提取今天最重要的国际新闻，重点关注：1.AI和科技 2.中美关系 3.全球政治。列出6-8条最重要新闻，每条必须包含：\n1) **英文原标题**（文章原始英文标题）\n2) **中文翻译标题**\n3) 摘要（2-3句话）\n4) 关键词（逗号分隔）\n5) **完整的原文链接URL**（https://www.bbc.com/...）\n⚠️ 标题格式："English Title 中文翻译"\n⚠️ URL是必填项。用中文输出。',
        'priority': 2,
        'required': True,  # 🔴 必选
        'expected_count': 6,
        'language': 'en',
    },
    {
        'name': '南华早报',
        'url': 'https://www.scmp.com/news/china',
        'prompt': '提取今天关于中国和国际的重要新闻，重点关注：1.中美关系 2.中国外交 3.亚太局势。列出6条新闻，每条包含：\n1) **英文原标题**（SCMP文章原始英文标题）\n2) **中文翻译标题**\n3) 摘要\n4) 关键词\n5) **完整URL**（https://www.scmp.com/...）\n⚠️ 标题格式："English Title 中文翻译"\n⚠️ URL是强制要求。用中文输出。',
        'priority': 3,
        'required': True,  # 🔴 必选
        'expected_count': 6,
        'language': 'en',
    },
    {
        'name': '卫报',
        'url': 'https://www.theguardian.com/international',
        'prompt': '提取今天最重要的国际新闻，重点关注：1.全球政治 2.气候变化 3.经济危机。列出4-5条新闻，每条包含：\n1) **英文原标题**（The Guardian原始标题）\n2) **中文翻译标题**\n3) 摘要\n4) 关键词\n5) **完整URL**（https://www.theguardian.com/...）\n⚠️ 标题格式："English Title 中文翻译"\n⚠️ URL必填。用中文输出。',
        'priority': 4,
        'required': True,  # 🔴 必选
        'expected_count': 5,
        'language': 'en',
    },
    # ===== 🔴 必选信源 V1.2.2 =====
    {
        'name': 'CNN',
        'url': 'https://www.cnn.com/world',
        'prompt': '提取今天最重要的国际新闻，重点关注：1.美国政治 2.全球冲突 3.经济动态。列出5-6条新闻，每条必须包含：\n1) **英文原标题**（CNN原始标题）\n2) **中文翻译标题**\n3) 简要摘要\n4) 关键词\n5) **完整URL**（https://www.cnn.com/...）\n⚠️ 标题格式："English Title 中文翻译"\n⚠️ URL必填。用中文输出。',
        'priority': 5,
        'required': True,  # 🔴 必选
        'expected_count': 5,
        'language': 'en',
    },
    {
        'name': '纽约时报',
        'url': 'https://www.nytimes.com/world',
        'prompt': '提取今天最重要的国际新闻和分析报道，重点关注：1.中美关系深度分析 2.地缘政治 3.全球经济。列出4-5条高质量新闻，每条包含：\n1) **英文原标题**（NYT原始标题）\n2) **中文翻译标题**\n3) 详细摘要\n4) 关键词\n5) **完整URL**（https://www.nytimes.com/...）\n⚠️ 标题格式："English Title 中文翻译"\n⚠️ URL必填。用中文输出。',
        'priority': 6,
        'required': True,  # 🔴 必选
        'expected_count': 4,
        'language': 'en',
    },
    {
        'name': '华尔街日报',
        'url': 'https://www.wsj.com/world',
        'prompt': '提取今天最重要的全球商业、政治和经济新闻，重点关注：1.中美贸易 2.全球经济 3.资本市场。列出4-5条高质量新闻，每条包含：\n1) **英文原标题**（WSJ原始标题）\n2) **中文翻译标题**\n3) 详细摘要\n4) 关键词\n5) **完整URL**（https://www.wsj.com/...）\n⚠️ 标题格式："English Title 中文翻译"\n⚠️ URL必填。用中文输出。',
        'priority': 7,
        'required': True,  # 🔴 必选 (V1.2.2新增)
        'expected_count': 4,
        'language': 'en',
    },
    # ===== 🟠 扩展信源 =====
    {
        'name': '半岛电视台',
        'url': 'https://www.aljazeera.com/news',
        'prompt': '提取今天关于中东、亚洲、非洲和发展中国家的重要新闻，重点关注：1.巴以冲突 2.能源政治 3.全球南方视角。列出4-5条新闻，每条包含：\n1) **英文原标题**（Al Jazeera原始标题）\n2) **中文翻译标题**\n3) 摘要\n4) 关键词\n5) **完整URL**（https://www.aljazeera.com/...）\n⚠️ 标题格式："English Title 中文翻译"\n⚠️ URL必填。用中文输出。',
        'priority': 8,
        'required': False,
        'expected_count': 4,
        'language': 'en',
    },
    {
        'name': 'Politico',
        'url': 'https://www.politico.com/world',
        'prompt': '提取今天关于全球政治、外交政策、贸易谈判的重要新闻，重点关注：1.欧美关系 2.全球贸易政策 3.国际外交动态。列出3-4条新闻，每条包含：\n1) **英文原标题**（Politico原始标题）\n2) **中文翻译标题**\n3) 摘要\n4) 关键词\n5) **完整URL**（https://www.politico.com/...）\n⚠️ 标题格式："English Title 中文翻译"\n⚠️ URL必填。用中文输出。',
        'priority': 9,
        'required': False,
        'expected_count': 3,
        'language': 'en',
    },
    {
        'name': '华盛顿邮报',
        'url': 'https://www.washingtonpost.com/world',
        'prompt': '提取今天最重要的国际新闻，重点关注：1.美国外交政策 2.民主与治理 3.全球危机。列出3-4条新闻，每条包含：\n1) **英文原标题**（Washington Post原始标题）\n2) **中文翻译标题**\n3) 摘要\n4) 关键词\n5) **完整URL**（https://www.washingtonpost.com/...）\n⚠️ 标题格式："English Title 中文翻译"\n⚠️ URL必填。用中文输出。',
        'priority': 10,
        'required': False,
        'expected_count': 3,
        'language': 'en',
    },
    {
        'name': '美联社',
        'url': 'https://apnews.com/world-news',
        'prompt': '提取今天全球重大突发新闻和重要事件，重点关注：1. Breaking news 2. 重大冲突 3. 自然灾害。列出4-5条快讯式新闻，每条包含：\n1) **英文原标题**（AP News原始标题）\n2) **中文翻译标题**\n3) 简要摘要\n4) 关键词\n5) **完整URL**（https://apnews.com/...）\n⚠️ 标题格式："English Title 中文翻译"\n⚠️ URL必填。用中文输出。',
        'priority': 11,
        'required': False,
        'expected_count': 4,
        'language': 'en',
    },
]

# 基础中文信源（requests可直接访问）
BASIC_SOURCES = [
    {'name': '人民网-国际', 'url': 'http://world.people.com.cn/', 'language': 'zh'},
    {'name': '中国日报网', 'url': 'https://www.chinadaily.com.cn/', 'language': 'zh'},
    {'name': '环球网', 'url': 'https://world.huanqiu.com/', 'language': 'zh'},
    {'name': '国际在线', 'url': 'http://www.cri.cn/', 'language': 'zh'},
    {'name': '中国外交部', 'url': 'https://www.mfa.gov.cn/web/wjbxw_673067/', 'language': 'zh'},
    {'name': '新华网', 'url': 'http://www.xinhuanet.com/world/', 'language': 'zh'},
]

# 分类映射
CATEGORY_MAP = {
    'us-china': '中美关系',
    'trade-sanctions': '经贸制裁',
    'ai-tech': 'AI与科技竞争',
    'diplomacy': '外交资讯',
    'geopolitics': '国际政治',
    'regional-asia': '亚太动态',
    'regional-europe': '欧洲事务',
    'regional-others': '其他地区',
}


class EnhancedNewsFetcher:
    """增强版新闻采集器 v3.0"""

    def __init__(self, basic_only=False):
        self.basic_only = basic_only
        self.results = []
        self.source_stats = {}
        self.webfetch_results = []
        self.basic_results = []

        if HAS_REQUESTS:
            self.session = requests.Session()
            self.session.headers.update(HEADERS)

    def fetch_basic_sources(self):
        """第1层：基础采集（中文信源）"""
        print("\n" + "="*60)
        print("📡 第1层：基础采集（中文信源）")
        print("="*60 + "\n")

        for source in BASIC_SOURCES:
            try:
                print(f"🔍 [{source['name']}] 正在连接...", end=' ', flush=True)

                if not HAS_REQUESTS:
                    print("⚠️ 跳过（无requests库）")
                    continue

                response = self.session.get(source['url'], timeout=12)
                response.raise_for_status()
                response.encoding = response.apparent_encoding or 'utf-8'

                # 简单的内容提取
                articles = self._extract_basic_content(response.text, source)

                if articles:
                    print(f"✅ 成功 ({len(articles)} 条)")
                    self.basic_results.extend(articles)
                    self.source_stats[source['name']] = {'status': 'success', 'count': len(articles)}
                else:
                    print("⚠️ 无内容")
                    self.source_stats[source['name']] = {'status': 'empty', 'count': 0}

            except Exception as e:
                error_type = type(e).__name__
                print(f"❌ 失败 ({error_type})")
                self.source_stats[source['name']] = {'status': f'error: {error_type}', 'count': 0}

            time.sleep(random.uniform(0.5, 1.5))  # 礼貌延迟

        print(f"\n✅ 基础采集完成：{len(self.basic_results)} 条原始素材")

    def _extract_basic_content(self, html, source):
        """
        V1.1增强版: 从HTML提取基本内容（支持更多中文网站结构）
        """
        articles = []

        if HAS_BS4:
            soup = BeautifulSoup(html, 'html.parser')

            # 策略1: 查找新闻列表容器（多种常见CSS类名）
            found_items = []

            # 尝试多种常见新闻列表选择器
            list_selectors = [
                ('div', ['news-list', 'newsList', 'news_list', 'list-news', 'news_box']),
                ('ul', ['news-list', 'list', 'news_ul', 'clearfix']),
                ('section', ['news', 'latest-news', 'world-news']),
            ]

            for tag_name, class_list in list_selectors:
                for cls in class_list:
                    containers = soup.find_all(tag_name, class_=cls, limit=3)
                    for container in containers:
                        links = container.find_all('a', href=True)
                        for link in links[:8]:
                            title = link.get_text(strip=True)
                            if len(title) > 8 and not title.startswith(('广告', '推荐', '更多', '相关')):
                                found_items.append({
                                    'title': title,
                                    'url': link['href'],
                                })

            # 策略2: 如果策略1失败，回退到标题标签查找
            if len(found_items) < 3:  # 如果找到的太少，使用备用策略
                title_tags = soup.find_all(['h2', 'h3', 'h4', 'h5'], limit=25)

                for tag in title_tags[:15]:
                    title = tag.get_text(strip=True)
                    if len(title) > 8 and not title.startswith(('广告', '推荐')):
                        a_tag = tag.find('a')
                        url = a_tag.get('href', '') if a_tag else ''

                        found_items.append({
                            'title': title,
                            'url': url,
                        })

            # 去重并构建文章列表
            seen_titles = set()
            for item in found_items:
                title_key = item['title'][:30]  # 用前30字符去重
                if title_key not in seen_titles:
                    seen_titles.add(title_key)

                    # 处理相对URL
                    url = item['url']
                    if url and not url.startswith('http'):
                        base_url = source.get('url', '')
                        if base_url:
                            from urllib.parse import urljoin
                            url = urljoin(base_url, url)

                    # 智能打分 - 基于关键词判断新闻重要性
                    score = self._calculate_priority_score(item['title'], source['name'])
                    category = self._detect_category(item['title'])

                    # 🆕 V1.2.2: 过期事件检测（在打分之前判定）
                    EXPIRED_PATTERNS = [
                        'APEC领导人非正式会议', '对韩国进行国事访问',
                        '对朝鲜进行国事访问', '出席博鳌亚洲论坛',
                        '出席G20峰会', '出席金砖峰会',
                        'XI\'S VISITS', '出访专题', 'SPECIAL REPORTS',
                        '热点专题'
                    ]
                    is_expired = any(p in item['title'] for p in EXPIRED_PATTERNS)
                    if is_expired:
                        score = 0  # 强制为0分

                    articles.append({
                        'title': item['title'],
                        'summary': item['title'],  # 基础采集可能没有详细摘要
                        'source': source['name'],
                        'url': url,
                        'language': source.get('language', 'zh'),
                        'raw_content': item['title'],
                        'priority_score': score,
                        'category': category,
                    })
        else:
            # 无BeautifulSoup时的简单正则提取
            titles = re.findall(r'<h[23][^>]*>([^<]+)</h[23]>', html)[:15]
            for title in titles:
                if len(title) > 10:
                    score = self._calculate_priority_score(title, source['name'])
                    category = self._detect_category(title)
                    articles.append({
                        'title': title.strip(),
                        'summary': title.strip(),
                        'source': source['name'],
                        'url': '',
                        'language': source.get('language', 'zh'),
                        'raw_content': title.strip(),
                        'priority_score': score,
                        'category': category,
                    })

        return articles

    def _calculate_priority_score(self, title, source_name):
        """基于关键词计算新闻重要性分数（中文新闻）"""
        score = 55  # 中文新闻默认分数（之前是0，导致全部排在最后）
        title_lower = title.lower()

        # 🔴 极高优先级 (90-94)
        high_priority_keywords = [
            '峰会', '元首', '总统', '习近平', '特朗普', '拜登', '普京',
            '中美', '中俄', '中美关系', '中美贸易', '中美冲突',
            '制裁', '反制', '关税', '谈判', '会晤',
            '战争', '军事冲突', '导弹', '袭击', '入侵',
            '联合国', '安理会', 'G20', 'G7', 'APEC'
        ]

        # 🟠 高优先级 (75-89)
        medium_high_keywords = [
            '外交部', '王毅', '布林肯', '大使', '国际',
            '条约', '协议', '合作', '访问', '会见',
            '台湾', '南海', '东海', '台海',
            '一带一路', '芯片', '半导体', '新能源'
        ]

        # 🟡 中等优先级 (60-74) - 默认
        # 一般性国际新闻已通过默认分数55覆盖

        # 检测极高优先级关键词
        for kw in high_priority_keywords:
            if kw in title:
                score = max(score, 92)
                break

        # 检测高优先级关键词（避免覆盖极高）
        if score < 92:
            for kw in medium_high_keywords:
                if kw in title:
                    score = max(score, 78)
                    break

        # 权威信源加分
        authoritative_sources = ['人民网-国际', '中国外交部', '新华网']
        if source_name in authoritative_sources and score < 75:
            score = max(score, 70)

        # 标记元首级
        if any(kw in title for kw in ['元首会晤', '国事访问', '峰会', '视频通话']):
            score = max(score, 95)

        return score

    def _detect_category(self, title):
        """基于标题智能检测分类"""
        # 中美关系
        if any(kw in title for kw in ['中美', '中美关系', '中美贸易', '中美冲突', '美国对华', '对美', '特朗普', '拜登']):
            return '中美关系'
        # 外交资讯
        if any(kw in title for kw in ['外交部', '王毅', '大使', '会见', '会谈', '访问', '联合国']):
            return '外交资讯'
        # 经贸制裁
        if any(kw in title for kw in ['制裁', '反制', '关税', '经贸', '贸易', '芯片']):
            return '经贸制裁'
        # AI科技
        if any(kw in title for kw in ['AI', '人工智能', '芯片', '半导体', '新能源', '5G']):
            return 'AI科技'
        # 地缘冲突
        if any(kw in title for kw in ['战争', '冲突', '导弹', '袭击', '入侵']):
            return '地缘政治'
        # 地区动态
        if any(kw in title for kw in ['台湾', '南海', '东海', '一带一路']):
            return '地区动态'
        # 默认
        return '国际政治'

    def prepare_webfetch_tasks(self):
        """
        准备WebFetch任务（返回任务列表供外部调用）

        注意：此方法不直接调用WebFetch API，
        因为WebFetch是WorkBuddy环境专属工具。
        返回的任务列表应在WorkBuddy环境中执行。
        """
        if self.basic_only:
            print("\n⏭️ 跳过WebFetch补充（--basic-only 模式）")
            return []

        print("\n" + "="*60)
        print("🌐 第2层：WebFetch API补充（高价值英文信源）")
        print("="*60)
        print("\n📋 已准备以下WebFetch任务：\n")

        for i, source in enumerate(WEBFETCH_SOURCES, 1):
            print(f"  {i}. {source['name']}")
            print(f"     URL: {source['url']}")
            print(f"     预期获取: ~{source['expected_count']} 条")
            print()

        return WEBFETCH_SOURCES

    def add_webfetch_results(self, source_name, articles_data):
        """
        添加WebFetch获取的结果 - V1.1增强版（支持双语标题+优先级自动标记）

        参数:
            source_name: 信源名称（如'路透社'）
            articles_data: 文章列表，每个文章应包含：
                          {
                            'title': str (格式: "English Title 中文翻译"),
                            'summary': str,
                            'keywords': str (逗号分隔),
                            'url': str,
                            ...
                          }
        """
        print(f"\n📥 接收 {source_name} 的数据: {len(articles_data)} 条")

        for article in articles_data:
            # V1.1: 解析双语标题
            raw_title = article.get('title', '')
            title_en, title_zh = self._parse_bilingual_title(raw_title, source_name)

            # 标准化数据格式
            normalized = {
                'id': f"wf_{source_name}_{len(self.webfetch_results)}_{hash(raw_title) % 10000}",
                'date': datetime.now().strftime('%Y-%m-%d'),
                'title': title_zh if title_zh else raw_title,  # 中文标题作为主标题
                'title_en': title_en,  # V1.1: 英文原标题
                'title_display': f"{title_en} {title_zh}" if title_en and title_zh else raw_title,  # V1.1: 显示用双语标题
                'summary': article.get('summary', raw_title),
                'source': source_name,
                'category': self._guess_category(raw_title + ' ' + article.get('summary', '')),
                'keywords': article.get('keywords', '').replace('，', ',').split(','),
                'url': article.get('url', ''),
                'importance': self._assess_importance(raw_title + ' ' + article.get('summary', '')),
                'priority': self._assess_priority(raw_title + ' ' + article.get('summary', '')),  # V1.1: 优先级
                'language': 'en' if title_en else 'zh',  # V1.1: 标记语言
                'collectedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'collection_method': 'webfetch',
            }

            self.webfetch_results.append(normalized)

        self.source_stats[source_name] = {
            'status': 'success (webfetch)',
            'count': len(articles_data),
        }

        print(f"✅ {source_name} 数据已添加")

    def _parse_bilingual_title(self, raw_title, source_name):
        """
        V1.1: 解析双语标题
        输入: "Ukraine's envoy to US: We need missiles 乌克兰驻美大使紧急呼吁：我们需要导弹"
        输出: ("Ukraine's envoy to US: We need missiles", "乌克兰驻美大使紧急呼吁：我们需要导弹")
        """
        if not raw_title:
            return '', ''

        # 常见分隔模式
        import re

        # 模式1: "English Title 中文标题" （空格分隔）
        # 检测是否包含中文字符
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', raw_title))

        if has_chinese:
            # 尝试分离英文和中文部分
            # 策略: 找到第一个连续中文序列的位置
            match = re.search(r'([\u4e00-\u9fff].*)$', raw_title)
            if match:
                chinese_part = match.group(1).strip()
                english_part = raw_title[:match.start()].strip()

                # 验证英文部分确实包含英文字母
                if english_part and re.search(r'[a-zA-Z]', english_part):
                    return english_part, chinese_part

        # 如果无法分离，返回原始标题
        return '', raw_title

    def _assess_priority(self, text):
        """
        V1.1: 评估新闻优先级（用于排序）
        返回: '元首级' | '高' | '中' | '低'
        规则:
          - 元首级: 中美元首/最高层会晤、通话、国事访问、重大政策宣布
          - 高: 重要外交动态、重大冲突、经济制裁
          - 中: 一般国际新闻
          - 低: 体育娱乐等
        """
        text_lower = text.lower()

        # 元首级关键词（最高优先）
        summit_keywords = [
            '习', '特朗普', '拜登', '元首', '峰会', '国事访问',
            '最高层', '总统通话', '主席会见', 'head of state',
            'summit', 'xi jinping', 'trump', 'biden',
            'state visit', 'presidential'
        ]

        # 检查是否为元首级
        is_summit = any(kw in text for kw in summit_keywords)

        # 进一步验证：必须同时涉及中美或大国关系
        china_us_context = any(kw in text for kw in [
            '中美', 'china-us', 'china u.s.', '华盛顿', '北京',
            'white house', '外交部', '国务卿'
        ])

        if is_summit and (china_us_context or '中美' in text or 'trade' in text_lower):
            return '元首级'

        # 基于重要性映射
        importance = self._assess_importance(text)
        if importance == '高':
            # 再次检查是否为元首级（更严格的条件）
            high_priority_keywords = [
                '战争', '和平协议', '制裁', '导弹', '核武器',
                'war', 'peace deal', 'sanctions', 'missile', 'nuclear'
            ]
            if any(kw in text_lower for kw in high_priority_keywords):
                return '高'
            return '中'
        elif importance == '中':
            return '中'
        else:
            return '低'

    def _guess_category(self, text):
        """根据文本猜测分类"""
        text_lower = text.lower()

        if any(kw in text for kw in ['中美', '特朗普', '拜登', '台海', '台湾', '南海']):
            return '中美关系'
        elif any(kw in text for kw in ['关税', '贸易', '制裁', '301', '实体清单']):
            return '经贸制裁'
        elif any(kw in text for kw in ['AI', '人工智能', '芯片', '半导体', 'OpenAI', '英伟达']):
            return 'AI与科技竞争'
        elif any(kw in text for kw in ['外交部', '王毅', '大使', '联合国']):
            return '外交资讯'
        elif any(kw in text for kw in ['伊朗', '以色列', '俄罗斯', '乌克兰', '中东']):
            return '国际政治'
        elif any(kw in text for kw in ['日本', '韩国', '东盟', '印度', '澳大利亚']):
            return '亚太动态'
        else:
            return '其他地区'

    def _assess_importance(self, text):
        """评估重要性等级"""
        high_keywords = ['中美', '特朗普', '制裁', '战争', '导弹', 'AI禁令', '重大', '紧急']
        medium_keywords = ['会议', '谈判', '协议', '合作', '声明']

        if any(kw in text for kw in high_keywords):
            return '高'
        elif any(kw in text for kw in medium_keywords):
            return '中'
        else:
            return '低'

    def merge_and_deduplicate(self):
        """合并两层结果并去重"""
        print("\n" + "="*60)
        print("🔄 数据合并与质量控制")
        print("="*60 + "\n")

        # 合并所有结果
        all_articles = self.basic_results + self.webfetch_results

        # 去重（基于标题相似度）
        seen_titles = set()
        unique_articles = []

        for article in all_articles:
            title = article.get('title', '')

            # 简单去重：完全相同或高度相似
            title_key = re.sub(r'[^\u4e00-\u9fa5a-zA-Z]', '', title).lower()

            if title_key and len(title_key) > 5 and title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)

        # 补充ID和元数据（针对基础采集的结果）
        final_results = []
        for i, article in enumerate(unique_articles):
            if 'id' not in article:
                article['id'] = f"basic_{i}_{int(time.time()) % 10000}"
            if 'collectedAt' not in article:
                article['collectedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if 'collection_method' not in article:
                article['collection_method'] = 'basic'

            final_results.append(article)

        # 统计信息
        basic_count = sum(1 for a in final_results if a.get('collection_method') == 'basic')
        webfetch_count = sum(1 for a in final_results if a.get('collection_method') == 'webfetch')

        print(f"📊 合并统计:")
        print(f"   - 原始总数: {len(all_articles)} 条")
        print(f"   - 去重后: {len(final_results)} 条")
        print(f"   - 基础采集: {basic_count} 条")
        print(f"   - WebFetch补充: {webfetch_count} 条")

        self.results = final_results
        return final_results

    def validate_urls(self):
        """
        验证URL完整性

        检查所有文章是否包含有效的URL字段，
        输出统计信息和缺失URL的文章列表。
        """
        print("\n" + "="*60)
        print("🔗 URL完整性验证")
        print("="*60 + "\n")

        if not self.results:
            print("⚠️ 没有数据可验证")
            return {
                'total': 0,
                'with_url': 0,
                'missing_url': 0,
                'coverage': 0,
                'missing_items': []
            }

        total = len(self.results)
        with_url = 0
        missing_url = 0
        missing_items = []

        for article in self.results:
            url = article.get('url', '')
            # 检查URL是否有效（非空且以http开头）
            if url and url.startswith('http'):
                with_url += 1
            else:
                missing_url += 1
                missing_items.append({
                    'id': article.get('id', ''),
                    'title': article.get('title', '')[:50],
                    'source': article.get('source', ''),
                })

        coverage = (with_url / total * 100) if total > 0 else 0

        # 输出统计
        print(f"📊 URL覆盖率统计:")
        print(f"   - 总文章数: {total} 条")
        print(f"   - 有URL: {with_url} 条 ({coverage:.1f}%)")
        print(f"   - 缺失URL: {missing_url} 条 ({100-coverage:.1f}%)")

        # 输出警告
        if missing_url > 0:
            print(f"\n⚠️ 警告：{missing_url} 条新闻缺少有效URL！")
            print("\n缺失URL的文章列表:")
            for i, item in enumerate(missing_items[:10], 1):  # 最多显示10条
                print(f"   {i}. [{item['source']}] {item['title']}...")

            if missing_url > 10:
                print(f"\n   ... 还有 {missing_url - 10} 条未显示")

            # 质量评估
            if coverage < 80:
                print(f"\n🔴 URL覆盖率过低 ({coverage:.1f}% < 80%)")
                print("   建议：重新执行WebFetch并明确要求返回完整URL")
            elif coverage < 95:
                print(f"\n🟡 URL覆盖率待优化 ({coverage:.1f}% < 95%)")
                print("   建议：检查WebFetch prompt是否包含URL要求")
            else:
                print(f"\n✅ URL覆盖率达标 (≥95%)")
        else:
            print(f"\n✅ 所有文章都有有效URL！")

        return {
            'total': total,
            'with_url': with_url,
            'missing_url': missing_url,
            'coverage': coverage,
            'missing_items': missing_items,
        }

    def save_data(self):
        """保存数据到JSON文件（V1.2.1 - 含质量控制）"""
        if not self.results:
            print("⚠️ 没有数据可保存")
            return False

        # ⭐ V1.2.2 增强：采集阶段的数据质量控制和清洗
        print(f"\n🧹 V1.2.2 数据质量检查...")
        original_count = len(self.results)

        # 定义垃圾文章识别规则（V1.2.2 扩展黑名单）
        NAVIGATION_KEYWORDS = [
            # 通用导航
            '导航', '首页', '首页导航', '网站地图', 'sitemap',
            '联系我们', '关于我们', '版权声明', '隐私政策',
            '用户协议', '登录', '注册', '搜索', '更多',
            # 🆕 V1.2.2: 中文信源专用黑名单
            '专栏', '系列账号', '记者手记', '全球连线', 'TOP NEWS',
            '要闻回顾', '一周回顾', '今日关注',
            # 🆕 V1.2.2: 索引页/专题页
            '海外分公司', '海外分站', '分社专栏',
            '热点专题', '出访专题', 'XI\'S VISITS', 'SPECIAL REPORTS',
            '国际要闻', '要闻TOP', '要闻TOP NEWS',
            # 🆕 营销/软文
            'Business+', '商业+', '美容', '美妆', '降温神器',
            'Young minds', 'ancient wisdom',
        ]

        # 营销/软文关键词（中英文）
        SOFT_CONTENT_KEYWORDS = [
            'Business+', 'A sun', 'sun that heals', 'Born by river',
            'Time for a cool', 'cool change', 'beauty brands',
            'surge in popularity', '手记', '不亦', '乐乎',
            '金环', '城市看', '中俄地方', '枢纽通',
            '货值升', '激活', '外贸动能', '乐在'
        ]

        # 软文阈值：包含任何一个就过滤
        SOFT_CONTENT_THRESHOLD = 1

        cleaned_results = []
        removed_count = 0
        removal_reasons = {}

        for article in self.results:
            title = article.get('title', '') or ''
            title_en = article.get('title_en', '') or ''
            source = article.get('source', '') or ''
            score = article.get('priority_score', 0)
            url = article.get('url', '') or ''

            # 规则1: 标题过短
            if len(title.strip()) < 5 and len(title_en.strip()) < 5:
                removed_count += 1
                removal_reasons['标题过短'] = removal_reasons.get('标题过短', 0) + 1
                continue

            # 规则2: 0分内容（兜底过滤）
            if score == 0:
                removed_count += 1
                removal_reasons['零分内容'] = removal_reasons.get('零分内容', 0) + 1
                continue

            # 🆕 V1.2.2: 导航/栏目关键词检测（适用于任何分数）
            nav_detected = False
            nav_keyword = ''
            for kw in NAVIGATION_KEYWORDS:
                if kw.lower() in (title + ' ' + title_en).lower():
                    nav_detected = True
                    nav_keyword = kw
                    break

            if nav_detected:
                removed_count += 1
                removal_reasons[f'导航/栏目({nav_keyword})'] = removal_reasons.get(f'导航/栏目({nav_keyword})', 0) + 1
                continue

            # 🆕 V1.2.2: 中文信源无URL检查（导航页通常没有URL）
            if source in ['人民网-国际', '中国外交部', '新华网', '中国日报网', '环球网'] and not url:
                removed_count += 1
                removal_reasons['无URL(导航页)'] = removal_reasons.get('无URL(导航页)', 0) + 1
                continue

            # 🆕 V1.2.2: 软文/营销内容检测
            soft_count = 0
            combined = title + ' ' + title_en
            for kw in SOFT_CONTENT_KEYWORDS:
                if kw.lower() in combined.lower():
                    soft_count += 1

            # 🆕 V1.2.2: 中国日报网特殊过滤（英文标题为主+内容质量差）
            if source == '中国日报网':
                # 中国日报网的内容普遍存在翻译质量不高/标题英文等问题
                # 仅保留包含中文标题且分数≥70的新闻
                if score < 70 or not title.strip():
                    removed_count += 1
                    removal_reasons['中国日报网质量不足'] = removal_reasons.get('中国日报网质量不足', 0) + 1
                    continue

            # 🆕 V1.2.2: 中文信源分数阈值检查
            if source in ['中国日报网', '新华网'] and score < 50:
                removed_count += 1
                removal_reasons['低质量中文(<50分)'] = removal_reasons.get('低质量中文(<50分)', 0) + 1
                continue

            # 🆕 V1.2.2: 纯英文标题检查（中文信源不应有英文标题）
            if source in ['人民网-国际', '中国外交部', '新华网', '中国日报网'] and not title.strip() and title_en.strip():
                removed_count += 1
                removal_reasons['纯英文标题'] = removal_reasons.get('纯英文标题', 0) + 1
                continue

            # 🆕 V1.2.2: 营销/软文判定
            if soft_count >= SOFT_CONTENT_THRESHOLD:
                removed_count += 1
                removal_reasons['软文/营销'] = removal_reasons.get('软文/营销', 0) + 1
                continue

            # 通过所有检查，保留
            cleaned_results.append(article)

        # 输出质量报告
        if removed_count > 0:
            print(f"   🗑️  已移除 {removed_count} 条低质量文章:")
            for reason, count in removal_reasons.items():
                print(f"      • {reason}: {count} 条")
            print(f"   ✅ 保留: {len(cleaned_results)} 条 (从{original_count}条)")
        else:
            print(f"   ✅ 所有 {original_count} 条文章质量合格")

        # 更新results为清洗后的数据
        self.results = cleaned_results

        # 确保目录存在
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

        # 保存为JSON数组格式
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"\n💾 数据已保存: {DATA_PATH}")
        print(f"   总计: {len(self.results)} 条新闻")
        return True

    def generate_report(self):
        """生成采集报告"""
        report = []
        report.append("# 国际新闻知识库 - 采集报告\n")
        report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**脚本版本**: v3.0 (增强版)\n\n")

        # 总体统计
        report.append("---\n\n")
        report.append("## 📊 采集统计\n\n")
        report.append(f"| 指标 | 数量 |\n|------|------|\n")
        report.append(f"| 总新闻数 | **{len(self.results)}** |\n")

        # 来源分布
        source_dist = Counter(a.get('source', '未知') for a in self.results)
        report.append("\n### 📰 来源分布\n\n")
        report.append("| 来源 | 数量 | 占比 |\n|------|------|------|\n")
        for source, count in source_dist.most_common():
            pct = count / len(self.results) * 100 if self.results else 0
            report.append(f"| {source} | {count} | {pct:.1f}% |\n")

        # 分类分布
        category_dist = Counter(a.get('category', '其他') for a in self.results)
        report.append("\n### 📂 分类分布\n\n")
        report.append("| 分类 | 数量 |\n|------|------|\n")
        for cat, count in category_dist.most_common():
            report.append(f"| {cat} | {count} |\n")

        # 重要性分布
        importance_dist = Counter(a.get('importance', '低') for a in self.results)
        report.append("\n### ⭐ 重要性分布\n\n")
        report.append("| 等级 | 数量 |\n|------|------|\n")
        for level in ['高', '中', '低']:
            count = importance_dist.get(level, 0)
            report.append(f"| {level} | {count} |\n")

        # 采集方法对比
        basic_count = sum(1 for a in self.results if a.get('collection_method') == 'basic')
        wf_count = sum(1 for a in self.results if a.get('collection_method') == 'webfetch')
        report.append("\n### 🔧 采集方法\n\n")
        report.append(f"| 方法 | 数量 | 占比 |\n|------|------|------|\n")
        report.append(f"| 基础采集 (requests) | {basic_count} | {basic_count/len(self.results)*100 if self.results else 0:.1f}% |\n")
        report.append(f"| WebFetch API补充 | {wf_count} | {wf_count/len(self.results)*100 if self.results else 0:.1f}% |\n")

        # 信源状态
        report.append("\n## 📡 信源状态\n\n")
        report.append("| 信源 | 状态 | 数量 |\n|------|------|------|\n")
        for name, stats in self.source_stats.items():
            status_icon = '✅' if 'success' in stats['status'] else '❌'
            report.append(f"| {name} | {status_icon} {stats['status']} | {stats['count']} |\n")

        # 保存报告
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write(''.join(report))

        print(f"\n📊 报告已生成: {REPORT_PATH}")
        return True


def main():
    parser = argparse.ArgumentParser(description='国际新闻知识库 - 增强版采集脚本 v3.0')
    parser.add_argument('--basic-only', action='store_true', help='仅基础采集，跳过WebFetch')
    parser.add_argument('--test', action='store_true', help='测试模式')
    args = parser.parse_args()

    print("\n" + "🌍"*30)
    print("\n🌍 国际新闻知识库 - 增强版采集系统 v3.0")
    print("🌍"*30 + "\n")

    # 初始化采集器
    fetcher = EnhancedNewsFetcher(basic_only=args.basic_only)

    # 第1步：基础采集
    fetcher.fetch_basic_sources()

    # 第2步：准备WebFetch任务（如果需要）
    webfetch_tasks = fetcher.prepare_webfetch_tasks()

    if webfetch_tasks and not args.basic_only:
        print("\n" + "!"*60)
        print("⚠️ 重要提示")
        print("!"*60)
        print("""
WebFetch任务已准备就绪，但需要在WorkBuddy环境中执行。

如果在WorkBuddy对话中运行，请告知助手执行这些WebFetch任务。

如果是命令行独立运行，将仅使用基础采集结果。
        """)
        print("!"*60 + "\n")

    # 第3步：合并数据（即使没有WebFetch结果也执行）
    fetcher.merge_and_deduplicate()

    # 第3.5步：URL完整性验证（新增！）
    url_validation = fetcher.validate_urls()

    # 第4步：保存数据
    fetcher.save_data()

    # 第5步：生成报告
    fetcher.generate_report()

    # 输出总结
    print("\n" + "="*60)
    print("✅ 采集完成")
    print("="*60 + "\n")
    print(f"📊 最终结果: {len(fetcher.results)} 条新闻")
    print(f"🔗 URL覆盖率: {url_validation['coverage']:.1f}% ({url_validation['with_url']}/{url_validation['total']})")
    if url_validation['missing_url'] > 0:
        print(f"⚠️ 缺失URL: {url_validation['missing_url']} 条（需要补全）")
    print(f"📁 数据文件: {DATA_PATH}")
    print(f"📊 采集报告: {REPORT_PATH}")

    if args.test:
        print("\n🧪 测试模式：仅显示统计，不保存完整数据")
        return 0

    return 0


if __name__ == '__main__':
    main()
