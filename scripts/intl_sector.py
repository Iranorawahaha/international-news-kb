#!/usr/bin/env python3
"""
intl_sector.py — 国际新闻 7 大板块分类器（L2 数据层归一核心）

背景（2026-09-02 用户拍板）：
  旧分类（全球经济/地缘政治/科技竞争/AI科技/中美关系…13 种）是采集端 LLM 打的自由标签，
  三轴杂糅（关系维/议题维/地域维并行）导致日报与看板观感散乱。
  新方案：互斥 7 大板块，任何一条只落一处，板块序 = 日报与看板展示先后序。

板块（阅读序，信息价值递减）：
  P1 中美博弈    中美直接对峙/谈判（高层外交、G20 涉中交锋、关税贸易战、双边制裁、
                  出口管制政治层宣布、台海中美角力、涉华安全指控如中远海运情报）
  P2 AI·科技     AI/芯片/半导体产业与公司、大模型、科技巨头、产业层面 AI/芯片管制落地
                  （边界：纯政治经贸层宣布→P1；产业/公司/技术层→P2）
  P3 中国外交    中国元首/外长出访、上合等多边外交、涉台涉港立场表态
                  （主角是中国；中美直接博弈除外）
  P4 中欧与盟友  欧盟/德国/法国/加拿大/日韩澳英等第三方涉华、及盟友圈对美摩擦
                  （主角是第三方；含 Shein/Temu 等涉华平台管制）
  P5 美国内政    特朗普政府国内政策、美选举/国会、公司人事、美军动态、美国社会
  P6 地区局势    中东/俄乌/半岛等冲突与安全（无涉中主线）
  P7 全球多边    世界经济/能源气候/人道灾难/他国内政/资本市场/国际组织与其他国家间议题

判定顺序（优先级从高到低，命中即返回）：
  P2(AI 强信号) → P1(中美) → P3(涉台港/上合/出访) → P6(冲突) → P4(欧加日韩澳英)
  → P5(美国主体) → P7(全球多边) → 旧 category 兜底 → 其他

用法：
  from intl_sector import classify_sector, SECTOR_ORDER, SECTOR_RANK, UNKNOWN_SECTOR
  本模块同时被 update-news.sh INTEGRATE_V121 与 scripts/intl_sector_dryrun.py 使用。
"""

SECTOR_ORDER = [
    '中美博弈',
    'AI·科技',
    '中国外交',
    '中欧与盟友',
    '美国内政',
    '地区局势',
    '全球多边',
]
SECTOR_RANK = {s: i for i, s in enumerate(SECTOR_ORDER)}
UNKNOWN_SECTOR = '其他'


import re


def _hit(text, words):
    return any(w in text for w in words)


def _hit_all(text, groups):
    """groups 中每组（AND 关系）各自至少命中一个词 → 全部满足才 True"""
    return all(_hit(text, g) for g in groups)


def _word_hit(text, words):
    """词级命中（英文按单词边界，避免 'ai' 撞 'airport/aide'、'llm' 撞词组等子串误伤）"""
    for w in words:
        if re.search(r'(?<![a-z0-9])' + re.escape(w) + r'(?![a-z0-9])', text):
            return True
    return False


def classify_sector(art):
    """把一篇文章归一到 7 板块之一。返回板块名（未命中 → 旧 category 兜底 → '其他'）。"""
    t_zh = (art.get('title_zh') or art.get('title') or '')
    t_en = (art.get('title_en') or '')
    s_zh = (art.get('summary_zh') or art.get('summary') or '')
    s_en = (art.get('summary_en') or '')
    cat = (art.get('category') or '')
    title = f"{t_zh} {t_en}".lower()
    text = f"{title} {s_zh} {s_en}".lower()

    sec = _match(title, text)
    if sec:
        return sec

    # ---- 兜底：旧 category 中语义明确的板块标签 ----
    cat_map = {
        '中美关系': '中美博弈', '经贸制裁': '中美博弈', '中美贸易': '中美博弈',
        'AI科技': 'AI·科技', '科技竞争': 'AI·科技', '半导体': 'AI·科技', '人工智能': 'AI·科技',
        '中国外交': '中国外交', '中欧关系': '中欧与盟友', '中欧经贸': '中欧与盟友',
        '中东局势': '地区局势', '安全冲突': '地区局势',
    }
    return cat_map.get(cat, UNKNOWN_SECTOR)


def _match(title, text):
    """核心判定（title=标题文本，text=标题+摘要全文）"""
    # ========== P2 AI·科技（最专属性强信号，最先判定） ==========
    # AI/LLM 等英文词级匹配（防 'ai' 撞 airport/aide/aircraft、'llm' 子串误伤）
    if _word_hit(title, ['ai', 'llm']):
        return 'AI·科技'
    if _hit(title, [
        'openai', 'anthropic', 'nvidia', '英伟达', 'deepseek', 'qwen', '通义', '月之暗面', 'kimi',
        'hbm', '台积电', 'tsmc', 'asml', '光刻', '光刻机',
        '人工智能', 'artificial intelligence', '大模型', 'chatgpt', 'claude', 'gemini',
        'copilot', '生成式', '芯片', 'chip', 'chips', 'chipmaker', 'semiconductor', '半导体',
        '算力', 'compute', '数据中心', 'data center', '脑机接口', 'neuralink',
        'telepathy', '量子', 'quantum', '机器人', 'robot',
    ]):
        return 'AI·科技'
    # 摘要级 AI 信号（标题无 AI 词但摘要强 AI 语境）
    if _hit(text, [
        'open-source ai', '开源 ai', '开源人工智能', 'ai chip', 'ai芯片', 'ai 芯片',
        'ai export', 'ai export control', 'cloud access', '云计算', 'frontier model', '前沿模型',
    ]):
        return 'AI·科技'

    # ========== P1 中美博弈 ==========
    # 1) G20/峰会场合中美攻防（批评/拒绝/顺差/公报难产/孤立）
    if _hit_all(text, [['g20', 'g-20', '财长会', '财长'],
                       ['china', 'chinese', '中国', 'beijing', '北京', 'xi', '习近平'],
                       ['critici', 'reject', 'blame', 'dispute', 'disagreement', 'stalemate', 'clash',
                        'criticism', '批评', '指责', '回绝', '拒绝', '分歧', '僵局', '争吵', '孤立',
                        '联合公报', 'communique', 'declaration', '声明', 'surplus', '顺差',
                        'dumping', '倾销', 'tariff', '关税', 'bessent', '贝森特']]):
        return '中美博弈'
    # 2) 中美贸易战/关税/制裁/出口管制政治层（中美双边，无第三方）
    if _hit_all(text, [['tariff', 'tariffs', 'trade war', 'trade surplus', 'export control', 'export controls',
                        'sanction', 'sanctions', 'entity list', 'blacklist', '关税', '贸易战', '出口管制',
                        '制裁', '贸易顺差', 'dumping', '倾销', 'restrict', 'restriction', '限制',
                        'retaliate', '报复', 'retaliation'],
                       ['china', 'chinese', '中国', 'beijing', '北京', 'xi', '习近平', 'huawei', '华为'],
                       ['us ', 'u.s.', 'america', 'american', '美国', 'washington', '华盛顿',
                        'trump', '特朗普', 'bessent', '贝森特', 'u.s. commerce', 'us commerce',
                        'us commerce department', 'white house', '白宫', 'pentagon', '五角大楼']]):
        return '中美博弈'
    # 3) 涉华安全指控（中远海运军事情报等）
    if _hit_all(text, [['china', 'chinese', '中国', 'beijing', '北京', 'cosco', '中远'],
                       ['military', 'intelligence', 'spy', 'espionage', 'warship', 'vessel', '军事', '情报',
                        '间谍', '舰', '船'],
                       ['us ', 'u.s.', 'america', '美国', 'pentagon', '五角大楼', 'navy', '海军']]):
        return '中美博弈'
    # 4) 台海中美角力（美对台军售/涉台美中角力）——"海峡/strait"单字过宽
    #    （会撞"霍尔木兹海峡"），必须出现显式台湾词
    if _hit_all(text, [['taiwan', 'taiwanese', '台湾', '台海', 'taiwan strait', '台湾海峡'],
                       ['us ', 'u.s.', 'america', '美国', 'trump', '特朗普', 'washington', '华盛顿',
                        'congress', '国会', 'arms', '军售', 'weapon', '武器']]):
        return '中美博弈'
    # 5) 中美高层会晤/对峙（仅标题级：标题同时含中美主体词，避免摘要宽泛误伤上合条）
    if _hit_all(title, [['china', 'chinese', '中国', 'beijing', '北京', 'xi', '习近平', '中方'],
                        ['us ', 'u.s.', 'america', 'american', '美国', 'trump', '特朗普', 'bessent', '贝森特',
                         'washington', '华盛顿', 'white house', '白宫']]):
        return '中美博弈'

    # ========== P3 中国外交 ==========
    # 1) 涉台涉港（中国主权/政治语境）——只认"主权政治语境"，屏蔽"地点性提及"：
    #    ⚠️ 禁裸 '港'（撞 '港股/港口'）；'在香港上市'（Shein）、公司落地香港均非涉港政治
    if (not _hit(text, ['上市', 'ipo', '股价', '股市', '港股', '估值', '市值', '挂牌', '股票',
                        'shares', 'listing', 'debut', 'stock market'])) and \
       _hit_all(text, [['taiwan', 'taiwanese', '台湾', '台海', '两岸', 'hong kong', '香港'],
                       ['警告', 'warn', '后果', 'consequence', '承认', 'recogni', '主权', 'sovereignty',
                        '独立', 'independence', '邦交', 'diplomatic', '分裂', '中国', 'chinese', 'china',
                        '北京', 'beijing', '中方', '北京当局', '外交部', 'mfa', '国台办', '白皮书',
                        '认罪', 'plead', '判刑', 'sentence', '法院', 'court', '检方', 'prosecutor',
                        '活动人士', 'activist', '抗议', 'protest', '示威', '国安法', 'national security',
                        '立法', 'legislation', '黄之锋', 'joshua wong', '上诉', 'appea', '刑期',
                        '监管', 'pacific islands forum', '太平洋岛国论坛', '出席', '论坛']]):
        # 无美国行动主体（军售/制裁/批评）时归中国外交；有则已由 P1.4 先行接走
        if not _hit_all(text, [['us ', 'u.s.', 'america', '美国', 'trump', '特朗普'],
                               ['arms', '军售', 'weapon', '武器', 'sanction', '制裁', 'critici', '批评', '指责']]):
            return '中国外交'
    # 2) 上合组织相关（习近平出席/上合宣言等；中美两峰会对比除外）
    if _hit(title, ['上合', 'sco', '上海合作组织', '比什凯克', 'bishkek']):
        if not _hit(title, ['分庭抗礼', '两场峰会', '两种全球秩序', 'global order']):
            return '中国外交'
    # 3) 中国元首/外长出访（标题级）
    if _hit_all(title, [['xi', '习近平', 'wang yi', '王毅', 'china', 'chinese', '中国', '北京'],
                        ['visit', 'state visit', '国事访问', '访问', '首访', '抵达', '启程', '行程',
                         '会见', 'meet', 'meeting', 'talks', '会谈', '到访']]):
        # 中美高层会晤已在 P1.5 接走；此处防标题同含美国主体被 P1 误判已先行
        return '中国外交'

    # ========== P6 地区局势（冲突与安全，无涉中主线） ==========
    if _hit(text, ['gaza', 'hamas', 'israel', 'israeli', 'netanyahu', 'west bank', 'hezbollah', 'houthi',
                   '加沙', '以色列', '内塔尼亚胡', '真主党', '胡塞', '以军', '空袭', '轰炸', '军事打击',
                   'iran', 'iranian', '德黑兰', '伊朗', 'strike', 'strikes', 'airstrike', 'missile', '导弹',
                   'ukraine', 'russia', 'russian', 'putin', 'zelensky', 'kremlin', 'moscow', 'kyiv',
                   '俄乌', '乌克兰', '普京', '泽连斯基', '克里姆林宫', '俄军', '俄方', '无人机袭击',
                   'north korea', 'korean', '朝鲜', '半岛', 'drone', 'drone attack']):
        # 中美俄三方叙事（如 APEC 三方会晤）已在 P1 接走；涉台等已先行
        return '地区局势'

    # ========== P4 中欧与盟友（欧/加/日韩澳英涉华，或盟友圈对美摩擦） ==========
    if _hit(text, ['europe', 'eu', 'european', 'germany', 'german', 'france', 'french', 'italy', 'italian',
                   'uk ', 'britain', 'british', 'canada', 'canadian', 'japan', 'japanese', 'australia',
                   'australian', 'south korea', 'india', '欧盟', '欧洲', '德国', '法国', '英国', '加拿大',
                   '日本', '澳大利亚', '韩国', '印度']):
        if _hit(text, ['china', 'chinese', '中国', 'beijing', '北京', 'taiwan', '台湾', 'hong kong', '香港',
                       '对华', '对中', '涉华', 'tariff', '关税', 'trade war', '贸易战', 'curb', '约束',
                       'export', '出口', 'sanction', '制裁', 'market', '市场', 'joint venture', '合资',
                       'buy european', '买欧洲', 'shein', 'temu', 'tiktok', '快时尚', 'duty', 'duties',
                       '附加费', 'levy', '反倾销', 'anti-dumping', '报复', 'retaliat', 'dumping', '倾销',
                       '摩擦', 'friction', 'restrict', '限制', 'trade', '贸易']):
            return '中欧与盟友'

    # ========== P5 美国内政（美国主体行动） ==========
    # 0) 美国大公司人事变动（苹果 CEO 等；AI/芯片系公司已在 P2 前置接走）
    #    ⚠️ 不进 P2：苹果/微软/谷歌等属消费科技，CEO 换代是公司人事而非 AI/芯片产业事件
    if _hit_all(title, [
        ['ceo', 'executive officer', 'chairman', '接替', '接任', '卸任', '辞职', '辞去', '出任', '任命',
         'succeeds', 'steps down', 'resigns', 'named', 'appointed'],
        ['apple', '苹果', 'microsoft', '微软', 'google', '谷歌', 'meta', 'facebook', 'amazon', '亚马逊',
         'tesla', '特斯拉', 'ibm', 'morgan stanley', '摩根士丹利', 'goldman', '高盛', 'jpmorgan',
         '摩根大通', 'citigroup', '花旗', 'bank of america', '美银']]):
        return '美国内政'
    if _hit(title, ['trump', '特朗普', 'white house', '白宫', 'congress', 'senate', 'house of representatives',
                    '美国国会', 'us government', 'u.s. government', '美政府', 'federal', '美国联邦',
                    'president', '总统', 'donald', 'secretary', '部长', 'us officials', '美官员',
                    'us military', '美军', 'us navy', 'navy', '航母', 'aircraft carrier', 'pentagon',
                    '五角大楼', 'state department', '国务院', 'us envoy', '美方', '美国',
                    'america', 'american']):
        # ⚠️ 不用裸 '美'（会撞 '亿美元'，如 Shein 港股 IPO 条）；'america/american' 补位美媒英文标题
        # 排除已被 P6 冲突语境吸走的美伊空袭类（P6 已先行，此处安全）；
        # 排除纯贸易/关税词已由 P1/P4 先行接走
        if not _hit_all(text, [['gaza', 'israel', 'iran', 'ukraine', '加沙', '以色列', '伊朗', '乌克兰']]):
            return '美国内政'

    # ========== P7 全球多边 ==========
    if _hit(text, ['world bank', 'imf', 'oecd', 'united nations', 'climate', 'cop', '世行', '货币基金',
                   '经合组织', '联合国', '气候', 'wto', '世界贸易组织', '世界银行',
                   'global economy', 'world economy', '全球经济', '世界经济', 'inflation', '通胀',
                   'central bank', '央行', '美联储', 'oil price', '油价', 'opec', '欧佩克', '石油',
                   'manufacturing', 'factory', 'factories', '工厂', '制造业', 'jobs', '就业', '岗位',
                   '供应链', 'supply chain', 'pmi', 'solar', '光伏', '太阳能', 'renewable', '风电',
                   'flood', 'floods', 'flooding', '洪水', '山洪', 'landslide', '泥石流', 'earthquake',
                   '地震', 'typhoon', '台风', 'humanitarian', '人道', '救灾', 'victims', '遇难',
                   'ipo', '上市', '股价', 'shares', 'share price', 'stock', '股市', '估值',
                   'canada', '加拿大', 'uk ', 'britain', '英国', 'election', '选举', '补选', 'by-election',
                   'parliament', '议员', 'resign', '辞职', '退党']):
        return '全球多边'

    return None
