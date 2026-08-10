#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
classify_columns.py — 国际新闻六大栏目分类器（Ira 信息看板）

六大栏目（用户定义）：
  1. 中国：中国元首/外交部/商务部等高层涉外事务动向（出访、发声、会谈）
  2. 美国：美国内政外交，尤其涉华动向、经贸制裁、科技战、特朗普言行（高优先）
  3. 欧洲：欧洲各国/欧盟内政外交，涉华法案、官方表态、选举动态
  4. 地区热点：中美欧以外区域地缘事件（中东冲突、俄乌冲突、多国大选）
  5. 国际会议：G7/慕安会/APEC/QUAD/G20 等重量级多边国际会议
  6. 其他：无法归入以上五类的全球性重大突发新闻

跨区域复合新闻判定原则：以核心决策主体归属栏目，不要拆分。
  例：特朗普提议周一与伊朗谈判 →【美国】（特朗普相关均放美国）
      沙特王储敦促特朗普"优先对话" →【美国】（涉及特朗普决策）
      鲁比奥绕行计划 →【美国】
      伊朗对美国军队发动突袭导弹攻击 →【地区热点】（主体是伊朗）
      俄军袭击基辅 →【地区热点】（俄乌战争，2026-08 修复）
      欧盟对俄制裁 →【欧洲】（欧盟主语，非俄乌战争主语）

栏目内优先级排序：
  ① 元首+涉华（最高） ② 仅涉华 ③ 仅元首 ④ 其余
"""
import re

COLUMNS = ["中国", "美国", "欧洲", "地区热点", "国际会议", "其他"]

# ---------- 美国相关（核心决策主体：特朗普/美国官员/美国政府） ----------
US_LEADERS = ["特朗普", "Trump", "美国总统", "白宫", "鲁比奥", "Rubio", "卢特尼克", "Lutnick",
              "美国国务卿", "美财政部长", "贝森特", "Bessent", "格里尔", "Greer",
              "美国", "美方", "美政府", "U.S.", "U.S.A", "Washington", "华盛顿",
              "万斯", "Vance", "美国贸易代表", "美国国防部长", "赫格塞斯", "Hegseth",
              "美国政府", "美国务院", "美国商务部", "美国财政部", "美方", "USA", "U.S.",
              "拜登", "Biden", "哈里斯", "Harris", "美国国会", "参议院", "众议院", "美国议员",
              "美议员", "美联储", "美国制裁", "美制裁", "美国对", "美对", "五角大楼", "美军",
              "美国公司", "美国企业", "TSMC", "台积电", "英伟达", "NVIDIA", "OpenAI", "马斯克",
              "美中", "中美", "美国与", "美国-", "美伊", "美俄", "美欧", "美日", "美韩", "美以"]

# ---------- 中国相关（核心决策主体：中国元首/外交部/商务部/中国高层） ----------
CN_LEADERS = ["习近平", "国家主席", "中国元首", "中国外交部", "外交部发言人", "中国商务部",
              "商务部新闻发言人", "王毅", "中国国防部", "中国人民解放军", "中国海军", "中国空军",
              "中方", "中国代表", "中国驻", "中国大使", "中国总理", "李强", "中国国务委员",
              "中国大陆", "中国海警", "中俄", "中欧", "中日", "中韩", "中澳", "中印",
              "中越", "中非", "中国与", "中国-", "中国台海", "台海", "台湾问题",
              # 泛涉华（无美方主体时的中国动向）
              "中国", "北京", "Beijing", "China", "Chinese", "中国科技", "中国制造",
              "中国公司", "中国企业", "中国军方", "解放军", "南海", "中国AI", "中国人工智能",
              "中国芯片", "中国半导体", "中国汽车", "中国电动车", "中国稀土", "中国关税"]

# ---------- 欧洲相关 ----------
EU_LEADERS = ["欧盟", "European Union", "欧洲议会", "欧洲委员会", "欧盟委员会", "冯德莱恩",
              "von der Leyen", "德国", "默克尔", "朔尔茨", "Scholz", "马克龙", "Macron",
              "法国", "英国", "英国首相", "斯塔默", "Starmer", "意大利", "西班牙", "葡萄牙",
              "荷兰", "比利时", "瑞典", "挪威", "丹麦", "芬兰", "波兰",  # ← 移走"乌克兰""泽连斯基"（俄乌战争当事方，不属于欧洲主体）
              "匈牙利", "奥班", "Orban", "希腊", "奥地利", "瑞士",
              "爱尔兰", "捷克", "斯洛伐克", "罗马尼亚", "保加利亚", "克罗地亚", "塞尔维亚",
              "北约", "NATO", "英法", "法德", "英国脱欧", "欧洲央行", "欧央行", "欧元区"]

# ---------- 国际会议 ----------
CONFERENCE_KEYS = ["G7", "G20", "APEC", "QUAD", "四方安全", "慕尼黑安全", "慕安会",
                   "达沃斯", "世界经济论坛", "联合国大会", "联大", "联合国安理会", "安理会",
                   "金砖", "BRICS", "上合", "上海合作组织", "东盟峰会", "东亚峰会", "北约峰会",
                   "G7峰会", "G20峰会", "亚太经合", "亚欧会议", "COP26", "COP27", "COP28",
                   "COP29", "COP30", "巴黎气候", "世界卫生大会", "世贸组织", "WTO部长级",
                   "IMF", "世界银行年会", "国际货币基金组织", "联合国气候"]

# ---------- 地区热点（中美欧以外） ----------
HOTSPOT_KEYS = ["中东", "伊朗", "以色列", "加沙", "哈马斯", "真主党", "胡塞", "沙特", "阿联酋",
                "卡塔尔", "土耳其", "叙利亚", "伊拉克", "黎巴嫩", "也门", "霍尔木兹", "红海",
                "俄罗斯", "俄乌", "克里姆林宫", "普京", "Putin", "朝鲜", "金正恩", "韩国",
                "日本首相", "石破茂", "印度", "莫迪", "Modi", "巴基斯坦", "阿富汗", "塔利班",
                "缅甸", "菲律宾", "马科斯", "越南", "印尼", "新加坡", "马来西亚", "泰国",
                "澳大利亚", "阿尔巴尼斯", "新西兰", "加拿大", "特鲁多", "巴西", "卢拉",
                "墨西哥", "阿根廷", "智利", "秘鲁", "哥伦比亚", "委内瑞拉", "古巴", "尼日利亚",
                "肯尼亚", "埃塞俄比亚", "南非", "埃及", "利比亚", "苏丹", "索马里", "刚果",
                "导弹袭击", "空袭", "冲突", "战争", "爆发冲突", "武装", "民兵", "叛军", "枪击",
                "袭击事件", "爆炸", "暗杀", "政变", "大选结果", "选举结果", "伊朗对", "伊朗发动",
                "俄军", "乌军", "以军", "哈马斯袭击", "无人机袭击",
                # 俄乌战争英文主语（避免纯英文标题漏识别）
                "Russia", "Russian", "Ukraine", "Ukrainian", "Kyiv", "Kiev",
                "Zelensky", "Zelenskyy", "Moscow", "Kremlin",
                "Donetsk", "Luhansk", "Kherson", "Mariupol",
                "Russian forces", "Russian missile", "Russian drone", "Russian attack",
                "Ukrainian forces", "Ukrainian capital"]

# 涉华信号（用于优先级①/②判定）
CN_SIGNALS = ["中国", "中方", "中美", "中俄", "中欧", "中日", "中韩", "台海", "台湾",
              "习近平", "中国外交部", "中国商务部", "王毅", "涉华", "对华", "中国-", "Chinese",
              "China", "Beijing", "北京", "TikTok", "微信", "抖音", "华为", "Huawei",
              "大疆", "DJI", "宁德时代", "比亚迪", "吉利", "中芯", "SMIC", "长江存储",
              "中国关税", "中国进口", "中国出口", "中国制造", "Made in China", "中国科技"]

# 元首信号（用于优先级①/③判定）
HEAD_SIGNALS = ["习近平", "国家主席", "特朗普", "美国总统", "普京", "泽连斯基", "马克龙",
                "朔尔茨", "英国首相", "莫迪", "金正恩", "石破茂", "元首", "总统", "主席",
                "首相", "Trump", "Xi", "Putin", "Zelensky", "Macron", "Modi"]


def classify_column(title, title_en="", summary=""):
    """返回六大栏目之一（以核心决策主体归属，不拆分复合新闻）"""
    text = f"{title or ''} {title_en or ''} {summary or ''}"
    t = title or ""
    has_cn = any(k in t for k in CN_LEADERS)
    has_us = any(k.lower() in text.lower() for k in US_LEADERS)

    # 中国强主体词（用于多步判定）
    CN_HEAD_STRONG = ["习近平", "国家主席", "中国外交部", "外交部发言人", "中国商务部",
                      "商务部新闻发言人", "王毅", "中国总理", "李强", "中方", "中国国防部",
                      "中国代表", "中国驻", "中国大使", "中国海警", "中国人民解放军"]

    # 0. 国际会议优先（特定多边会议关键词，如 G7/APEC/G20/慕安会）
    if any(k.lower() in text.lower() for k in CONFERENCE_KEYS):
        return "国际会议"

    # 0.4 俄乌战争特例（用户原则：俄乌冲突相关不归欧洲，归地区热点）
    #   标题主语是俄乌战争（Russia/Ukraine/Putin/Zelensky/Kyiv 等）→ 地区热点
    #   例外：欧盟/北约主语（EU force / EU sanctions / NATO / 欧洲对俄）→ 欧洲
    #   例外：特朗普/白宫直接行为 → 美国
    RU_UA_WAR_KEYS = ["俄乌", "乌克兰", "泽连斯基", "Zelensky", "Zelenskyy",
                      "俄罗斯", "普京", "Putin", "克里姆林宫", "Kremlin",
                      "Moscow", "莫斯科", "Kyiv", "Kiev", "基辅",
                      "Ukraine", "Ukrainian", "Russia", "Russian",
                      "顿涅茨克", "Donetsk", "卢甘斯克", "Luhansk",
                      "Russian forces", "Russian missile", "Russian drone",
                      "Ukrainian forces", "Ukrainian capital"]
    EU_NATO_RU_SUBJ = ["EU force", "EU sanctions", "EU 制裁", "欧盟对俄",
                       "European Union sanctions", "EU 牵头", "EU-led",
                       "Italy-led", "Italian-led", "British-led", "Germany-led",
                       "NATO ", "NATO秘书长", "NATO chief", "北约秘书长",
                       "北约东扩", "NATO expansion", "欧洲对俄",
                       "波兰支持", "波兰援乌", "欧盟对乌", "EU's ",
                       "European response", "Europe's response",
                       # EU 主导对俄/对乌行动（任意 EU + sanctions/announce/impose/approve）
                       "EU announces", "EU imposes", "EU approves", "EU adopts",
                       "EU unveils", "EU targets", "EU extends", "EU agrees",
                       "EU agrees new", "EU to sanction", "EU agrees on Russia",
                       "EU greenlights", "EU prepares"]
    is_ru_ua_war = any(k in t for k in RU_UA_WAR_KEYS)
    is_eu_nato_ru_subj = any(k in t for k in EU_NATO_RU_SUBJ)
    if is_ru_ua_war and not is_eu_nato_ru_subj:
        # 例外：特朗普/白宫直接行为 → 美国
        if any(k in t for k in ["特朗普", "Trump", "白宫", "美国总统"]):
            return "美国"
        return "地区热点"

    # 0.5 热点主语优先：标题开头是热点主体（伊朗/俄/朝等）→ 地区热点
    #    —— "伊朗对美国军队发动突袭导弹攻击" → 地区热点（伊朗是发起方）
    HOTSPOT_SUBJECT = ["伊朗", "以色列", "哈马斯", "真主党", "胡塞武装", "俄罗斯", "俄军",
                       "朝鲜", "金正恩", "沙特", "土耳其", "叙利亚", "也门", "黎巴嫩",
                       "巴基斯坦", "塔利班", "缅甸", "菲律宾", "印度", "莫迪", "乌克兰",
                       "泽连斯基", "普京", "中东", "俄乌"]
    _hotspot_subj = [k for k in HOTSPOT_SUBJECT if t.startswith(k)]
    if _hotspot_subj:
        # 例外：热点主体 + 特朗普/鲁比奥等美国强主体 → 美国（用户规则：涉及特朗普均放美国）
        _us_word_in_hotspot = any(k.lower() in text.lower() for k in ["特朗普", "Trump", "鲁比奥", "Rubio", "白宫", "美国总统"])
        if not _us_word_in_hotspot:
            return "地区热点"

    # 1. 美国强主体优先：特朗普/鲁比奥/白宫/美国官员等为核心决策主体
    #    —— "特朗普提议周一与伊朗谈判" → 美国；"沙特王储敦促特朗普" → 美国
    US_STRONG = ["特朗普", "Trump", "鲁比奥", "Rubio", "白宫", "美国总统", "美国国务卿",
                 "卢特尼克", "Lutnick", "贝森特", "Bessent", "格里尔", "Greer", "万斯", "Vance",
                 "赫格塞斯", "Hegseth", "美国贸易代表", "美国防部长", "美财政部长",
                 "习近平同", "与中国国家主席"]
    # 美方直接参与冲突（美军/美国+军事行动）→ 美国（用户规则：美方直接参与冲突议题）
    US_MILITARY = ["美军", "美国军队", "美国打击", "美国空袭", "美国袭击", "美国连夜",
                   "美国对", "美国向", "美国宣布", "美方打击", "美国国防部", "五角大楼"]
    if (any(k.lower() in text.lower() for k in US_STRONG) or any(k in t for k in US_MILITARY))             and not any(k in t for k in CN_HEAD_STRONG):
        # V1.6 例外：伊朗/霍尔木兹相关地缘冲突，非直接特朗普主体 → 地区热点
        # —— "美国连夜打击伊朗数十个目标" → 地区热点（冲突主体是美伊，不是特朗普个人）
        # —— "伊朗在霍尔木兹海峡袭击美军" → 地区热点
        # V1.7 修复：US 强主体（特朗普/鲁比奥/白宫等）已在此分支，例外不应再覆盖强主体决策行为
        # —— "鲁比奥绕行计划：世界能否摆脱霍尔木兹海峡咽喉" → 美国（鲁比奥决策归美方）
        # V1.7 修复：US 军事主体（美军/美国打击等）也优先于伊朗冲突例外
        # —— "美军对伊朗实施打击" → 美国（美军直接行为归美方）
        IRAN_CONFLICT_WORDS = ["伊朗", "霍尔木兹", "Hormuz", "美伊", "伊朗战争", "伊朗冲突"]
        is_iran_conflict = any(k in t or k.lower() in text.lower() for k in IRAN_CONFLICT_WORDS)
        is_us_strong_direct = any(k in t for k in US_STRONG)
        is_us_military_direct = any(k in t for k in US_MILITARY)
        is_trump_direct = any(k in t for k in ["特朗普", "Trump"])
        if is_iran_conflict and not is_trump_direct and not is_us_strong_direct and not is_us_military_direct:
            return "地区热点"
        return "美国"

    # 2. 中国强主体优先：习近平/外交部/商务部等中方主体为核心决策方
    #    —— "习近平同美国总统特朗普通电话" → 中国（中方主体在标题）
    if any(k in t for k in CN_HEAD_STRONG):
        return "中国"

    # 3. 地区热点主体优先（伊朗/俄/朝鲜/中东主体，无美国强主体）
    #    —— "伊朗对美国军队发动突袭导弹攻击" → 地区热点
    HOTSPOT_HEAD = ["伊朗", "以色列", "哈马斯", "真主党", "胡塞", "俄罗斯", "俄军", "普京",
                    "朝鲜", "金正恩", "沙特", "土耳其", "叙利亚", "也门", "黎巴嫩", "伊拉克",
                    "巴基斯坦", "阿富汗", "塔利班", "缅甸", "菲律宾", "印度", "莫迪", "日本",
                    "韩国", "加拿大", "巴西", "墨西哥", "澳大利亚", "新西兰", "非洲", "埃及",
                    "俄乌", "中东"]
    if any(k in t for k in HOTSPOT_HEAD):
        return "地区热点"

    # 4. 欧洲主体优先（欧盟/德国/法国等）—— 乌克兰/泽连斯基/俄乌已上提
    #    —— "欧盟拟对中国电动车加征关税" → 欧洲
    EU_HEAD = ["欧盟", "欧洲议会", "欧洲委员会", "欧盟委员会", "冯德莱恩", "德国", "朔尔茨",
               "法国", "马克龙", "英国", "斯塔默", "意大利", "西班牙", "葡萄牙", "荷兰",
               "比利时", "波兰", "北约", "匈牙利", "奥班", "瑞典", "挪威", "丹麦", "芬兰"]
    if any(k in t for k in EU_HEAD):
        return "欧洲"

    # 5. 美国行动优先：美方主体 + 行动词（制裁/关税/黑名单等）
    US_ACTION = ["制裁", "黑名单", "实体清单", "禁令", "禁止", "加征", "关税", "出口管制",
                 "调查", "列入", "宣布", "启动", "起诉", "限制", "封禁", "指控", "要求",
                 "施压", "威胁", "警告", "打击", "征收", "禁运", "下架", "撤销", "冻结"]
    if has_us and any(k in text for k in US_ACTION):
        return "美国"

    # 6. 中国主体（含泛涉华）
    if has_cn:
        return "中国"

    # 7. 美国
    if has_us:
        return "美国"

    # 8. 欧洲 / 地区热点 兜底
    if any(k.lower() in text.lower() for k in EU_LEADERS):
        return "欧洲"
    if any(k in text for k in HOTSPOT_KEYS):
        return "地区热点"

    # 3. 欧洲
    if any(k.lower() in text.lower() for k in EU_LEADERS):
        return "欧洲"

    # 4. 地区热点（主体明确：中东/俄乌/亚太非中美欧）
    if any(k in text for k in HOTSPOT_KEYS):
        return "地区热点"

    return "其他"


def column_priority(article):
    """栏目内优先级：①元首+涉华 ②仅涉华 ③仅元首 ④其余 → 返回排序键"""
    title = article.get("title", "") or ""
    title_en = article.get("title_en", "") or ""
    text = f"{title} {title_en}"
    has_head = any(k.lower() in text.lower() for k in HEAD_SIGNALS)
    has_cn = any(k.lower() in text.lower() for k in CN_SIGNALS)
    if has_head and has_cn:
        return 0  # ① 元首+涉华
    if has_cn:
        return 1  # ② 仅涉华
    if has_head:
        return 2  # ③ 仅元首
    return 3  # ④ 其余


def sort_by_column_priority(articles):
    """按栏目分组 + 组内优先级排序"""
    result = []
    for col in COLUMNS:
        col_items = [a for a in articles if a.get("column", classify_column(a.get("title",""), a.get("title_en",""))) == col]
        col_items.sort(key=lambda a: (column_priority(a), -(a.get("priority_score") or 0)))
        result.extend(col_items)
    return result


if __name__ == "__main__":
    # 自测
    tests = [
        "特朗普提议周一与伊朗开始新一轮谈判",
        "沙特王储敦促特朗普在美伊战争中优先对话",
        "鲁比奥绕行计划：世界能否摆脱霍尔木兹海峡咽喉",
        "伊朗对美国军队发动突袭导弹攻击",
        "习近平同美国总统特朗普通电话",
        "中国外交部就美国对华关税答记者问",
        "欧盟拟对中国电动车加征关税",
        "G7领导人峰会讨论全球贸易秩序",
        "美联储宣布维持利率不变",
    ]
    for t in tests:
        print(f"  {classify_column(t):6s} | {t}")
