## 2026-08-31 09:23-09:45 (第二十二次运行)

### 执行摘要
- ⚠️ **源组丢失坑复发（第 8 次）**：fetch_us_official.py 白宫整组 14 条被覆盖丢失（59→32 条）→ 运行前备份 /tmp/us-official-backup-0831.json 恢复 62 条 + merge 今日国务院 3 条 → 6 源齐全（白宫14/国务院18/国防部23/财政部3/商务部1/USTR3）100% 中文化 0 导航残留
- ✅ 官方源新增 3 条：**国务院 ①冰岛8-29公投声明（8-30，80★，尊重主权决定/NATO 盟友，与 NYT 冰岛公投拒绝欧盟呼应）②马来西亚独立69周年贺词（8-30，75）③吉尔吉斯独立35周年贺词（8-31，75）**；**⚠️ 挪威国王哈拉尔五世逝世声明（8-28 逝世/8-29 发布）超窗口剔除**（严格 V2.11）；白宫 48h 无新（最新 8-28 霍尔木兹/太空学院已收录）
- ✅ WebFetch 采集 41 条新增（11 源全覆盖尝试）：路透 10/SCMP 5/NYT 5/BBC 5/WaPo 5/AP 4/Politico 4/CNN 3/半岛 3/卫报 1；**WSJ 0（反爬 JS-BLOCKED，WebSearch 线索 Amazon/Microsoft 支持 Gain AI Act 限英伟达对华出口为 8-27 超窗口，如实汇报）**；路透 /business 补抓命中**贝森特 G20 建议对华更多贸易壁垒 95★**；同事件去重：美伊拉腊克岛/约旦基地保留路透版（BBC/卫报/半岛/AP 跳过）、委内瑞拉 650 亿桶保留 BBC 版、冰岛公投保留 NYT 版+国务院官方版双收
- ✅ 交叉验证 3 组关键词：**无窗口内重大遗漏**——①长鑫 1260H 诉讼 8-29 已收录 ②厢式拖车双反终裁 264.48%（8-28 发布/8-31 生效）超窗口且无权威英文 8-30/31 报道 → 宁缺毋滥不收录 ③BIS 远程算力新规 8-28 已收录（今日无新进展）
- ✅ update-news.sh --auto 一次成功：307 条/8 天，8-31 组 44 条（41 媒体 + 3 官方，date 8-30:43 + 8-31:1）→ 飞书 1 条（date=8-31 吉尔吉斯，0 重复）→ commit 2aff1b2 **脚本 push 直连失败（第 9 次）→ 手动代理 push 成功**
- ✅ 校验全部通过：今日组 44 条（collectedAt≠今日 0 / date<昨天 0 / 跨组 URL 重复 0 / 组内重复 0）；官方源 3 条 0 缺中文 0 模板摘要；今日组 0 缺中文 0 缺摘要 0 模板摘要 0 导航残留；嵌入 JSON 解析成功；JS 语法正确；**线上 HTTP 200 且 md5 与本地完全一致（5b6beaee）**

### 本次关键发现
1. **今日主题：美伊军事升级多线聚焦**（美军打击拉腊克岛 92★ + IRGC 袭击约旦两基地 90★ + 贝森特每周新次级制裁 90★ + 军方警告赫格塞斯 90★ + 伊朗权力斗争分析 88★ + 伊朗燃料短缺/最高领袖呼吁团结）+ **中美经贸**（贝森特 G20 鼓动对华壁垒 95★ + G20 外交考验 88★）+ **委内瑞拉石油 650 亿桶协议多角度**（BBC 88/路透 25年 84/卫报辩护 82/WaPo 新殖民地 85）+ **冰岛公投拒绝欧盟 90★**（NYT + 国务院官方双收）+ 中尼洪灾 261 外国人失踪（路透 90★）+ 乌兹别克斯坦购歼-10CE 86 + 上海市长人选 85
2. **源组丢失坑第 8 次确认**：本次白宫整组丢失（curl 失败），备份恢复 + merge 仍是唯一保险；运行后必检 6 源
3. **超窗口严格剔除**：挪威国王逝世声明（8-29 发布）虽有重大性仍按 V2.11 剔除；厢式拖车双反（8-28 发布）超窗口不收录
4. **飞书去重查询 rc=4 网络失败（历史已知）**：本次仅 1 条 date=8-31 无重复风险，核对通过；若多条目时需人工核对入库数
5. **8-30 无自动化记录但 16:11 有实例更新**（318 条/8-30 组 38 条已定稿），今日 8-31 组正常生成 44 条

### 产出
- 本地: international-news.html (307条/8天，8-31 组 44 条)，commit 2aff1b2（代理 push 92eb2f8..2aff1b2）
- 飞书: 1 条已入库（date=8-31，吉尔吉斯贺词，无重复）
- ✅ 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html（HTTP 200，md5 5b6beaee557e58c20499f723918932f9 与本地一致）

### 待跟进
- [ ] fetch_us_official.py 源组丢失防护（第 8 次确认，超出"不修改脚本"范围，待用户确认）
- [ ] WSJ 反爬持续（8-30/31 双日 0 条），若有重大 WSJ 独家需 WebSearch + 高质量转载兜底

## 2026-08-28 09:23-09:45 (第二十次运行)

### 执行摘要
- ⚠️ **源组丢失坑复发（第 6 次）**：fetch_us_official.py 国务院 curl Connection reset（代理环境）→ 国务院 11 条整组被覆盖丢失、白宫 10→2、国防部 23→21 → 运行前备份 /tmp/us-official-backup-0828.json 恢复 51 条 + merge 今日白宫 2 条 → 54 条 6 源齐全 100% 中文化
- ✅ 官方源 3 条新：**白宫 ①安大略湖改名"美国湖"（Lake America，8-27，80，美加贸易战摩擦新信号，WebFetch 拿真实正文补中文）②莱维特完成白宫新闻秘书最后一天（8-27，80，重要人事）**；**国务院 ③副国务卿兰道会见日本外务副大臣船越（8-27，78，美日同盟+霍尔木兹）**；国防部最新 8-24 稀土（超窗口）/USTR 8-18（行程类）/商务部 7-16 均无 48h 新
- ✅ WebFetch 采集 48 条新增（11 源全覆盖）：SCMP 8/路透 7/BBC 5/卫报 5/NYT 5/CNN 4/半岛 4/WaPo 4/AP 4/WSJ 2/Politico 1；WSJ 反爬 → finwire.io（特朗普拒返 6 月伊 MoU 90）+ morningstar DJN（英伟达财报 962 亿/70% 指引 90）；Politico 用官方 URL（半导体新一轮关税 92，覆盖笔记本/游戏主机/服务器）；**超窗口剔除：WaPo 中国借美加贸易战渔利（8-25）/伊朗经济战分析（8-25）、卫报美制裁伊朗（8-24）、海地帮派（8-25）等**
- ✅ update-news.sh --auto 一次成功：243 条/6 天，8-28 组 51 条（48 媒体 + 3 官方）→ 飞书 2 条（date=8-28）→ commit a7fbeae **push 直连成功**（脚本偶发成功，代理仍为兜底）
- ✅ 校验全部通过：今日组 51 条（collectedAt≠今日 0 / date<昨天 0 / 跨组 URL 重复 0 / 组内重复 0）；官方源 3 条 0 缺中文 0 模板摘要；今日组 51/51 中文 0 缺摘要 0 模板摘要 0 导航残留；JS 语法正确；**线上 HTTP 200 且 md5 与本地完全一致（cfb90175）**；飞书核对 date=8-28 的 2 条（WSJ MoU+路透核演习）已入库
- ✅ 数据源文件补充 commit 74075c9（代理 push 成功）

### 本次关键发现
1. **今日主题：习特会前中美博弈多线**（特朗普暗示制裁涉伊中国银行 92★/中国高管随团访美贸易休战延期"几乎确定" 92★/王毅排除障碍 90★）+ **Politico 独家半导体新一轮全面关税 92★**（覆盖笔记本/游戏主机/数据中心服务器，AI 产业冲击）+ **英伟达财报 962 亿 +70% 指引 90** + **特朗普拒返 6 月伊朗 MoU 90**（油价飙升）+ 尼泊尔西藏山洪 359 死 1400 失踪（多源 88）+ 美韩日核导弹演习（85）
2. **同题合并正常拦截**：半岛"Hormuz 开放条件"与路透"伊朗为重开霍尔木兹设条件"标题相似度≥0.68 → 保留路透权威版（AUTHORITY_ORDER 生效），非数据丢失
3. **源组丢失坑第 6 次确认**：运行前备份是唯一保险；fetch 失败后立即检查源分布（本次国务院整组丢失）
4. **超窗口官方/媒体源严格剔除**：无论重要性（中国借美加贸易战渔利等 8-25 均剔除）
5. **update-news.sh 偶发直连 push 成功**（本次成功），但 7890 代理仍为可靠兜底（数据源 commit 走代理）

### 产出
- 本地: international-news.html (243条/6天，8-28 组 51 条)，commit a7fbeae + 74075c9
- 飞书: 2 条已入库（date=8-28）
- ✅ 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html（HTTP 200，md5 cfb90175 与本地一致）

### 待跟进
- [ ] fetch_us_official.py 源组丢失防护（第 6 次确认，超出"不修改脚本"范围，待用户确认）
- [ ] war.gov/USTR 反爬官方源错过 48h 窗口即丢失（8-24 稀土已丢，建议 9:30 采集时优先 WebFetch war.gov releases 页）

## 2026-08-27 09:23-09:45 (第十九次运行)

### 执行摘要
- ⚠️ **源组丢失坑复发（第 5 次）**：fetch_us_official.py 三源（白宫/国务院/财政部）curl 全 Connection refused（代理 7890 无服务）→ 白宫 7+国务院 9 整组被覆盖丢失（剩 28 条）→ 运行前备份 /tmp/us-official-backup-0827.json 恢复 46 条 6 源齐全；**无代理直连三源均 200 可用**
- ✅ 官方源采集（无代理 curl + WebFetch 手动补 5 条新）：**白宫 Bulk-Power 电力系统国家紧急状态（IEEPA，禁外国产电力设备，90 元首级）** + 牛肉进口配额公告（78）+ Abbey Gate 五周年（75）；**国务院 鲁比奥会见墨西哥外长（78）+ 极左恐怖组织制裁（Autistici/Inventati 等，80）**；财政部 8-26 公告与国务院极左制裁同事件（合并）；国防部最新 8-24 稀土/商务部 7-16/USTR 8-18 均过窗口；us-official.json 51 条 6 源齐全 100% 中文化
- ⚠️ **超窗口剔除（如实汇报）**：国务院 叙利亚 SST 撤销（8-24，重大）、伊朗"经济放逐"行动制裁（8-24，重大）、鲁比奥-德国通话（8-24）、白宫 Overdose/National Park Week 文告（8-24）
- ✅ WebFetch 采集 30 条新增（SCMP 8/路透 4/BBC 3/NYT 2/WSJ 1/彭博 1/CNN 2/半岛 2/Politico 1/WaPo 2/AP 2/卫报 2）；WSJ 反爬 → TradingView 转载（Anthropic 30T TAM/2T 估值）；OpenAI Jalapeño 芯片超越 Blackwell 用 financefeeds 英文原报 URL（source 标彭博社）；Reuters/BBC/SCMP/卫报 WebFetch 间歇失败但重试成功；Politico /world 404 → WebSearch 拿真实 URL
- ✅ update-news.sh --auto 一次成功：236 条/6天，8-27 组 35 条（30 媒体 + 5 官方）→ 飞书 5 条（date=8-27）→ commit 26d1be5 push 直接成功 → 数据源 commit 29a671d 推送成功
- ✅ 校验全部通过：今日组 35 条（collectedAt≠今日 0 / date<昨天 0 / 跨组 URL 重复 0 / 组内重复 0）；官方源 5 条 0 缺中文 0 模板摘要；今日组 0 缺中文 0 缺摘要 0 模板摘要 0 导航残留；JS 语法正确；**线上 HTTP 200 且 md5 与本地完全一致（1be05cf0）**

### 本次关键发现
1. **今日主题：中美博弈多线交织**（美查封中国黑客平台 QTFY 92 / 中国誓言报复涉伊制裁 92 / 美对伊制裁放行中国 90 / 中印 8 步协议 88 / 泽连斯基促华促和 88）+ **AI 芯片格局生变**（OpenAI Jalapeño 超英伟达 Blackwell 90 / Anthropic 30T TAM IPO 88 / 英伟达财报 88 / OpenAI 代理黑客 85）+ **白宫电力紧急状态**（90，涉华电力设备风险）
2. **源组丢失坑第 5 次确认**：备份恢复仍是唯一保险；本次代理全挂但无代理直连全通（白宫/国务院/财政部 200）
3. **WebFetch 间歇性失败**：Reuters/BBC/SCMP/卫报首次全 fetch failed → 重试成功；WSJ 反爬、Politico /world 404 为常态 → WebSearch 兜底
4. **8-26 超窗口官方源确认**：叙利亚撤销/伊朗经济放逐均 8-24 发布，严格按 V2.11 剔除不收录（无论重要性）

### 产出
- 本地: international-news.html (236条/6天，8-27 组 35 条)，commit 26d1be5 + 29a671d
- 飞书: 5 条已入库（date=8-27）
- ✅ 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html（HTTP 200，md5 1be05cf0 与本地一致）

### 待跟进
- [ ] fetch_us_official.py 源组丢失防护（第 5 次确认，超出"不修改脚本"范围，待用户确认）
- [ ] war.gov/USTR 反爬官方源错过 48h 窗口即丢失（8-24 稀土已丢）

## 2026-08-24 09:23-09:45 (第十七次运行)

### 执行摘要
- ⚠️ **发现并发实例已先跑**：09:22 已有 update-news.sh 提交 957a7bf（240条/6天），8-24 组 73 条媒体（9源），但**缺 WSJ/AP/WaPo、无官方源、summary_zh 全空、含 17 条 date=8-22 超窗口** → 全面修复
- ✅ 官方源采集：fetch_us_official.py 白宫1/国务院1/财政部 Connection reset → ⚠️ **源组丢失坑复发（第 3 次）**：白宫 5→1、国务院 9→1 整组被覆盖 → 用运行前备份 /tmp/us-official-backup-0824.json 恢复 44 条 6 源齐全（白宫5/国务院9/国防部23/财政部3/商务部1/USTR3），**今日官方源实际 0 全新**（2 条重抓为已收录公告）；war.gov 最新 8-21、USTR 最新 8-18，均过 48h 窗口无新
- ✅ WebFetch 补采 3 条：WSJ 美加滑向贸易战（88，163 转载全文）+ WaPo 特朗普贸易策略极限（88，Yahoo 转载）+ AP 卡尼被特朗普考验（85，apnews 直连）；修正路透"经济D日"65→90、CNN 贝森特"经济诺曼底"65→90（涉华重大）；Politico 伊朗 act of war 与 AP 同事件 → AP 版跳过
- ✅ update-news.sh --auto 两次：首次 243 条 → 发现 18 条超窗口 → **webfetch/news-data 双端清理 date<8-23 共 17 条（并发实例的 8-22 旧稿）→ 重跑 226 条/6天，8-24 组 59 条**（date=8-23:55 / 8-24:4）→ git push 956d792 直接成功 → 数据源 commit fed8730 推送成功
- ✅ 校验全部通过：今日组 59 条（collectedAt≠今日 0 / date<昨天 0 / 跨组 URL 重复 0 / 组内重复 0）；官方源 20 条 0 缺中文 0 模板摘要；今日组 0 缺中文 0 缺摘要 0 模板摘要；JS 语法正确；**线上 HTTP 200 且 md5 与本地完全一致（5f3ed1de）**
- ✅ 飞书：date=8-24 仅 4 条且已入库（0 新增），8-23 的 55 条不入库（sync --today 历史既定行为）

### 本次关键发现
1. **并发实例半成品识别**：8-24 组 73 条 media 数据 summary_zh 全空（中文摘要存 summary 字段）、缺 3 源、含超窗口旧稿 → 重跑前必须校验今日组 date/源覆盖/字段
2. **源组丢失坑第 3 次确认**：fetch_us_official.py 单源 curl 失败（财政部 reset）→ 白宫/国务院整组被覆盖丢失 → 运行前备份是唯一保险，**本次备份救回 14 条**
3. **webfetch 超窗口条目不会自动过滤**：并发实例采集的 date=8-22 旧稿（17条）经 update-news.sh 直进今日组 → 必须双端清理（webfetch + news-data）后重跑
4. **11 源覆盖校验**：8-24 最终 11/11 源全覆盖（路透11/BBC7/SCMP8/卫报10/CNN5/NYT4/WSJ1/半岛7/Politico4/WaPo1/AP1）

### 产出
- 本地: international-news.html (226条/6天，8-24 组 59 条)，commit 956d792 + fed8730
- 飞书: date=8-24 的 4 条已在库（并发实例已同步），0 新增
- ✅ 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html（HTTP 200，md5 5f3ed1de 与本地一致）

### 待跟进
- [ ] 并发实例半成品防护：更新脚本前先校验今日组已有数据完整性（源覆盖/超窗口/字段）
- [ ] fetch_us_official.py 源组丢失防护（第 3 次确认，超出"不修改脚本"范围，待用户确认）
# 自动化任务执行记录：国际新闻看板每日刷新（9:30）

## 2026-08-21 09:19-10:10 (第十六次运行)

### 执行摘要
- ✅ 官方源采集：国务院 7 条新（含 **Qods Force/真主党走私网络制裁 90、厄瓜多尔可卡因网络 90、古巴 3 人 9 实体制裁 90、Min Zin 错误拘押认定（涉华重大）90、鲁比奥-加拿大外长会晤**、匈牙利国庆日贺词）；**白宫 curl Connection reset 失败 → 源组丢失坑复发（白宫 3 条整组被覆盖丢失）** → 用运行前备份 /tmp/us-official-backup-0821.json 合并恢复 + 补抓白宫 → **新增白宫 NSPM-17《国家航天运输政策》85（8-20 发布，无代理 curl 直连成功）**；war.gov WebFetch 抓到 2 条 48h 新（**战略资本 NSFF 关键矿产融资计划 80 + 美牙买加 SOFA 78**）；财政部/商务部/USTR 确认 48h 无新；us-official.json 43 条，6 源齐全（白宫4/国务院9/国防部23/财政部3/商务部1/USTR3），9 条新增 100% 中文化、0 导航残留、0 模板摘要
- ⚠️ **源组丢失坑复发（第 2 次）**：fetch_us_official.py 白宫 curl Connection reset → 白宫整组 3 条被覆盖丢失 → 合并恢复成功。**再次确认：每次运行后必检 us-official.json 6 源齐全；运行前 cp 备份是关键保险**
- ✅ WebFetch 采集 11/11 信源：新增 31 条（SCMP 8/BBC 4/AJ 4/Reuters 2/WSJ 2/NYT 2/Guardian 2/CNN 2/WaPo 2/AP 2/Politico 1）；Reuters/WSJ 反爬 → WebSearch 兜底（**贝森特"史上最严厉制裁"92 用 al-monitor 转载、特朗普"经济D日"92 用 wsj.com 播客 URL、美加关税削减 88 用 tradingview DJN 转载**）；去重跳过 2 条（BBC Carney/AP Instagram 判决 URL 已在历史）
- ✅ update-news.sh --auto 成功：**注意：后台启动时与前一实例并发（pid 锁拒绝重复执行，16929 主进程正常跑完）** → 264 条/8天 → HTML（8-21 组 39 条）→ **git push 直接成功 e00e8ad（连续第 2 次未清代理异常）** → 数据源 commit 778e6c3 推送成功
- ✅ 校验全部通过：今日组 39 条（collectedAt≠今日 0 / date<昨天 0 / 跨组 URL 重复 0 / 组内重复 0）；官方源 8 条 0 缺中文 0 模板摘要；今日组 0 缺中文 0 缺摘要；JS 语法正确；**线上 HTTP 200 且 md5 与本地完全一致（cf08a982）**
- ✅ 飞书核对：date=8-21 的 7 条全部入库（SCMP 3 + BBC 4，与本地完全一致）；**飞书 filter-json 匹配用纯日期失败（字段值是 datetime 格式 "2026-08-21T00:00:00.000+08:00"），改用 --sort-json 按新闻日期倒序 + 人工核对**

### 本次关键发现
1. **今日高分**：SCMP Min Zin 错误拘押 92（涉华）/ SCMP 美施压中国支持对伊经济行动 92 / Reuters 史上最严厉制裁 92 / WSJ 经济D日 92 / 国务院 Qods/厄瓜多尔/古巴制裁 90×3 / 白宫 NSPM-17 85 / SCMP 台 350 亿防务预算 88 / NYT 许家印无期 88 / AP 朝鲜导弹 88 / 王毅首尔 88
2. **今日主题：美对伊"经济D日"多源聚焦（6 源不同角度：SCMP 涉华/Reuters 制裁/WSJ 播客/Guardian 贸易伙伴/WaPo 盟友/AP 霍尔木兹核查）+ 美三连制裁（圣城旅/厄瓜多尔/古巴）+ Min Zin 错误拘押（官方+媒体双收录）+ 美加关税谈判 + 许家印宣判 + 朝鲜导弹**
3. **fetch_us_official.py 白宫源组丢失（第 2 次确认）**：脚本单源 curl 失败 → 该源整组被覆盖 → 运行前备份 + 合并恢复是标准动作；白宫失败时 `env -u http_proxy -u https_proxy curl` 直连 200
4. **update-news.sh 并发防护正常**：后台启动遇到锁（16929 前实例）自动拒绝，主进程不受影响跑完；后续用 `ps -p PID` 等待
5. **飞书日期筛选坑**：`--filter-json` 用纯日期 "2026-08-21" 匹配失败（字段存 datetime）；`--sort-json '[{"field":"新闻日期","desc":true}]'` 可倒序查最新

### 产出
- 本地: international-news.html (264条/8天)，commit e00e8ad + 778e6c3
- 飞书: 7 条已入库（date=8-21，SCMP 3 + BBC 4）
- ✅ 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html（HTTP 200，md5 cf08a982 与本地一致）

### 待跟进
- [ ] **update-news.sh git push**：连续 2 次脚本直接 push 成功（未清代理），历史上 8 次失败——7890 代理仍建议作为兜底通道
- [ ] 飞书 8-14 重复 44 条清理（历史遗留，继续待授权）
- [ ] fetch_us_official.py 源组丢失防护：单源失败保留旧数据（超出"不修改脚本"范围，待用户确认）

## 2026-08-20 09:11-09:40 (第十五次运行)

### 执行摘要
- ✅ 官方源采集：白宫 2 条新（**福特林肯车型生产回流美国、逐步淘汰中国进口 90 分涉华经贸重大** + 国民警卫队/后备役周文告 88 分，无代理 curl 直连详情页拿真实正文，agent 翻译补中文）；国务院 curl 407 → WebFetch 兜底确认 48h 内 3 条昨日已收 + 1 条副国务卿挪威会晤例行 readout 跳过；财政部 0/商务部 0（WebFetch 确认最新 7-16）/war.gov 0（最新 8-17 已收）/USTR 0（curl 直连确认最新 Iowa 行程类已跳过）；us-official.json 34 条，100% 中文化、0 导航残留、0 模板摘要
- ⚠️ **重大坑（第 1 次发现）**：环境变量 HTTP_PROXY=127.0.0.1:7890 全局存在，本次 7890 对 state.gov 返回 407 → fetch_us_official.py 国务院失败 → **脚本合并逻辑把 us-official.json 里国务院 3 条 + 昨日白宫 1 条整个覆盖丢失**（30 条无国务院）→ 修复：`git show 0245ecc:data/us-official.json` 恢复旧版 + merge 今日新增 2 条 → 34 条。**下次运行后必检 us-official.json 是否有国务院条目**（源分布应含"美国国务院"）
- ✅ WebFetch 采集 10/11 信源有效（WaPo 48h 无合格新条目=0 条，如实汇报）：新增 34 条（Reuters 5/BBC 4/SCMP 6/Guardian 4/CNN 2/NYT 3/WSJ 2/AJ 4/Politico 2/AP 2）；WSJ 反爬 → WebSearch 兜底（**OpenAI Q2 收入 67 亿美元仅 +18% 被 Anthropic 115 亿首次反超 92 分**，用 WSJ 官方播客页 URL；**特朗普 8-19 确认今年会晤金正恩、或在深圳 APEC 11 月 92 分**，用 CNA 转载 URL）；同事件去重：美加关税保留 BBC+Guardian 双角度、UAE 停贸选 NYT 版、金与正保留 Guardian 版、乌克兰防长保留 Reuters 版、宇树上市保留 BBC 版、美韩军演反应版全跳过
- ✅ update-news.sh --auto 首次成功：271 条/8天（8-12 组滚出窗口）→ HTML（8-20 组 36 条）→ **git push 直接成功 b634fa1（本次未清代理异常）** → 飞书 3 条（date=8-20 的 4 条 - 1 重复"Presidential Message"）
- ✅ 数据源文件补充 commit 5bc55c4 并推送成功（b634fa1..5bc55c4）
- ✅ 校验全部通过：今日组 36 条（collectedAt≠今日 0 / date<昨天 0 / URL 跨组重复 0 / 组内重复 0）；官方源 35 条 0 缺中文 0 模板摘要；今日组 0 缺中文 0 缺摘要 0 导航残留 0 模板摘要；JS 语法正确；**线上 HTTP 200 且 md5 与本地完全一致（a8ff9c80）**

### 本次关键发现
1. **今日高分**：SCMP 习近平访美 AI 会谈细节不确定 95（元首级）/ SCMP 中国公民 2024 大选选民欺诈 92 / WSJ OpenAI 被 Anthropic 反超 92 / WSJ 特朗普会晤金正恩·深圳 APEC 92 / 白宫福特林肯回流 90 / BBC 宇树科技上市 90 / SCMP 京东欧盟调查 90 / SCMP 黄岩岛监测站 90 / Guardian 金与正质疑 90 / NYT 蓝箭可回收火箭 90 / AJ 五角大楼北约忠诚问卷 90 / AJ 特朗普对伊"最严厉经济行动"90 / AJ 美债破 40 万亿 88
2. **环境变量代理双刃剑**：HTTP_PROXY=7890 全局存在；state.gov 走代理 407、无代理 200；白宫 WebFetch 404 但无代理 curl 200。下次 state.gov/白宫失败时先 `env -u http_proxy -u https_proxy curl` 测直连
3. **fetch_us_official.py 合并覆盖坑升级（第 2 种形态）**：上次是"重跑覆盖同 URL 字段"，本次是"某源 curl 失败导致该源整组从结果丢失"→ 每次运行后必查源分布完整性（白宫/国务院/财政部/国防部/商务部/USTR 应齐全），缺则 git show 恢复 + merge
4. **webfetch 手工条目字段固化**：34 条全含 title（英文原题）+ collectedAt=2026-08-20 09:30，V2.11 归档正常，36 条全进今日组
5. **WaPo 48h 窗口空窗**：8-19 仅王室/同事件新闻，8-18 及更早超窗口 → 0 条，如实汇报不硬凑

### 产出
- 本地: international-news.html (271条/8天)，commit b634fa1 + 5bc55c4
- 飞书: 3 条已入库（date=8-20）
- ✅ 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html（HTTP 200，md5 a8ff9c80 与本地一致）

### 待跟进
- [ ] **update-news.sh git push**：本次脚本 push 直接成功（未清代理），但历史上 8 次失败——仍建议改 `git -c http.proxy=http://127.0.0.1:7890 push`（待用户确认）
- [ ] 飞书 8-14 重复 44 条清理（历史遗留，继续待授权）
- [ ] fetch_us_official.py 源组丢失防护：建议脚本层在单源失败时保留旧数据（超出"不修改脚本"范围，待用户确认）

## 2026-08-19 09:20-09:45 (第十四次运行)

### 执行摘要
- ✅ 官方源采集：白宫 1（暴力犯罪降幅 9.3%，curl 列表抓到但 URL 404 → WebSearch 拿真实内容含 9.3%/18.1% 具体数据）/国务院 3（鲁比奥与阿联酋国安顾问通话/与哥伦比亚总统通话/指定 ICC 院长赤根智子+高级审判律师塞耶制裁，WebFetch 补全截断摘要）/财政部 0；反爬站点：war.gov 无 48h 新（最新 8-17 已收录）、USTR 8-18 Iowa 行程类无政策实质不收录、商务部无新；us-official.json 32 条，4 条新条目 agent 翻译补中文（处理 &#8217; HTML 实体匹配坑）→ 100% 中文化、0 导航残留、0 模板摘要
- ✅ WebFetch 采集 11/11 信源：新增 27 条（Reuters 8/BBC 3/SCMP 7/Guardian 1/NYT 2/Politico 1/AJ 3/WaPo 1/CNN 1）；WSJ 反爬 → WebSearch 兜底；Politico /world 404 → 主站+WebSearch 拿美加关税独家；**重大发现：中国 6 月减持美债 259 亿至 6334 亿美元创 2008 年来新低（TIC 8-17 数据，Reuters 报道用 Yahoo Finance 转载 URL 收录 90 分）**；同事件去重：美韩军演反应版全跳过、ICC 媒体版跳过（官方已收）、美加关税只收 Politico 版、30校审计 SCMP 版跳过（war.gov 已收）、驱逐舰 CNN 版 8-17 已收跳过
- ✅ update-news.sh --auto 首次成功：322 条/8天 → HTML（8-19 组 31 条）→ 飞书 4 条（date=8-19）→ commit 5a57fba
- ⚠️ **git push 第 8 次确认**：脚本清代理直连失败 → 手动 `git -c http.proxy=http://127.0.0.1:7890 push` 成功（5a57fba 由后续 26d54ca 一并推上，数据源 0245ecc 单独推）
- ⚠️ **超窗口条目拦截（V2.11 生效）**：校验发现 NYT 胡塞袭击沙特船只 date=8-17 < 昨天 8-18 违规 → 从 webfetch 剔除 1 条 → 重跑 update-news.sh → 8-19 组 30 条（date 8-18:26 / 8-19:4）→ commit 86c15c4 + 53c8a5b 推送成功
- ✅ 校验全部通过：今日组 30 条（collectedAt≠今日 0 / date<昨天 0 / URL 跨组重复 0 / 组内重复 0）；官方源 54 条 0 缺中文 0 模板摘要；今日组 0 模板摘要 0 缺中文 0 缺摘要；全量 0 导航残留；JS 语法正确；线上 HTTP 200 且 md5 与本地完全一致（9cdc86ed）
- ✅ 飞书 4 条已入库（date=8-19，SCMP 民主党制裁/蓝箭航天/培根 + BBC 叙利亚空袭），去重正常无误插

### 本次关键发现
1. **今日高分**：SCMP 习近平见厄瓜多尔总统抨击拉美干涉 92（元首级）/ Reuters 特朗普否认伊朗谈判·霍尔木兹仍关闭 92 / Politico 美加关税豁免待批 92 / Reuters 全球债市+中国减持美债创2008来新低 90 / SCMP 民主党批评放松香港制裁 90 / SCMP 王毅访首尔 90
2. **中国减持美债（6334 亿美元/2008 来最低）为今日经贸头号新闻**：TIC 6 月数据 8-17 发布，Reuters 报道无直连 URL → Yahoo Finance 转载 Reuters 全文 URL 收录，source 标路透社（延续第三方转载先例）
3. **V2.11 超窗口拦截流程已固化**：今日新增 webfetch 条目 date 必须 ∈ {昨天, 今天}；校验发现违规 → webfetch 剔除 → 重跑 update-news.sh → 校验 date<昨天=0（本次拦截 NYT 胡塞 date=8-17 1 条）
4. **git push 双保险确认（第 8 次）**：脚本清代理直连必失败；7890 代理可靠；且其他自动化任务的 commit 会连带推送国际看板更新（本次 5a57fba 由 26d54ca 推上），但数据源文件仍需单独 commit+push
5. **USTR 8-18 Iowa 条目确认无政策实质**（Greer 参观 Titan 轮胎厂+州博览会）→ 与 8-11 判断一致不收录

### 产出
- 本地: international-news.html (322条/8天)，commit 5a57fba + 0245ecc + 86c15c4 + 53c8a5b
- 飞书: 4 条已入库（date=8-19）
- ✅ 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html（HTTP 200，md5 9cdc86ed 与本地一致）

### 待跟进
- [ ] **update-news.sh git push 清代理**：第 8 次失败确认，建议改 `git -c http.proxy=http://127.0.0.1:7890 push`（超出"不修改脚本"范围，待用户确认）
- [ ] 飞书 8-14 重复 44 条清理（历史遗留，继续待授权）

## 2026-08-18 09:20-09:55 (第十三次运行)

### 执行摘要
- ✅ 官方源采集：白宫 2（林肯号文章/处方药降价，curl 直连）/国务院 0/财政部 0；反爬站点：war.gov 新增 2 条 48h 内（**30所高校科研安全审计 90 分涉华重大** + RTX 战斧 229 亿美元合同 78 分，WebFetch 抓详情页真实内容），商务部/USTR WebFetch 确认 48h 无新；us-official.json 30 条，白宫 2 条 agent 翻译补中文 → 100% 中文化、0 导航残留、0 模板摘要
- ✅ WebFetch 采集 11/11 信源：新增 23 条（Reuters 5/BBC 1/SCMP 4/Guardian 1/CNN 2/NYT 2/WSJ 2/AJ 3/Politico 1/AP 2）；WSJ 反爬 → WebSearch 确认真实 URL（**伊朗秘密升级计划 92 分** + 特朗普拉拢金正恩 85 分）；去重 8 条历史已收（Reuters 美韩军演/库什纳、BBC Burnham/Meta、SCMP 飞翼客机、NYT 人才竞争、WSJ 北极航线、AP 社交成瘾）→ 跳过
- ✅ update-news.sh --auto 成功：405 条/8天 → HTML（8-18 组 27 条）→ 飞书 1 条（date=8-18 半岛 liveblog）→ commit 38b19a0 + e13bf86
- ⚠️ **git push 第 7 次确认**：脚本清代理直连失败 → 手动 `git -c http.proxy=127.0.0.1:7890 push` 首试 Connection reset（网络波动）→ 等 8s 重试成功（2e72ec8..e13bf86）
- ✅ 校验全部通过：今日组 27 条（collectedAt≠今日 0 / 跨组 URL 重复 0 / 组内重复 0）；官方源 70 条 0 缺中文 0 模板摘要；今日组 0 模板摘要 0 缺中文 0 缺摘要；JS 语法正确；线上 HTTP 200 且 md5 与本地完全一致（0bbcfd9e）
- ✅ 8-18 组 27 条含 1 条 date=8-16（WSJ 伊朗秘密升级，迟到抓取归今日组符合规则）

### 本次关键发现
1. **今日高分**：NYT 英伟达 1050 亿俄亥俄数据中心 95 / WSJ 伊朗秘密升级 92 / Politico 习近平缺席联大 92 / 半岛 特朗普拒延长伊朗 MoU 90 / war.gov 30校审计 90 / SCMP 赫格塞斯或将离任 88 / Reuters 金正恩回应 85 / SCMP 台湾水下无人机 85 / WSJ 特朗普拉拢金正恩 85
2. **war.gov 反爬通道稳定**：Releases 页 WebFetch 可拿到 48h 内新条目（含具体时间"11 hours ago"），详情页 WebFetch 可拿真实正文 → 与 curl 直连互补
3. **习近平缺席联大（Politico 92 分）为今日独家重大涉华线索**：习特峰会前缺席联大，中美外交安排新信号
4. **同事件多源只收一版执行**：美韩军演削减（Reuters 版已在历史）→ BBC/CNN/AP/卫报反应版均跳过；特朗普威胁轰炸阿曼（BBC 版收录，CNN/AP/WSJ 版跳过）；中国经济放缓（SCMP 版收录，Guardian 版跳过）
5. **手动追加 webfetch 字段固化**：title（英文原题）+ collectedAt（抓取日）双字段齐全，V2.11 归档正常，23 条全进今日组

### 产出
- 本地: international-news.html (405条/8天)，commit 38b19a0 + e13bf86
- 飞书: 1 条已入库（date=8-18，历史既定行为：sync --today 按 date==today 筛选）
- ✅ 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html（HTTP 200，md5 0bbcfd9e 与本地一致）

### 待跟进
- [ ] **update-news.sh 1041 行 git push 清代理**：第 7 次失败确认（本次手动代理首试也 Connection reset，网络波动，重试成功），建议改 `git -c http.proxy=http://127.0.0.1:7890 push`（超出"不修改脚本"范围，待用户确认）
- [ ] 飞书 8-14 重复 44 条清理（历史遗留，继续待授权）

## 2026-08-17 17:45-18:05 (第十二次运行，同日二次刷新)

### 执行摘要
- ✅ 官方源采集：白宫0/国务院2（加蓬+印尼独立日贺词，curl 直连）/财政部0；反爬站点（war.gov/USTR/商务部）WebFetch 确认 48h 无新（war.gov 最新 8-14、USTR 8-13 均过窗口）；us-official.json 28 条，2 条新贺词 agent 翻译补中文 → 100% 中文化、0 导航残留、0 模板摘要
- ✅ WebFetch 采集 11 信源：新增 29 条（Reuters 5/BBC 2/SCMP 4/NYT 6/WSJ 3/Guardian 2/CNN 2/AJ 2/Politico 1/AP 2）；WSJ 反爬 → WebSearch 验证 3 条 URL 真实（**恒力石化进口伊朗制裁原油 95 分**、北极航线常态化 88、AI 隐性支出 80）；卫报北极冰上丝路与 WSJ 北极航线同事件（卫报版今晨已收，仅收 WSJ 版）；Reuters 美韩军演削减/SCMP 白宫混乱独家/卫报冰上丝路 3 条 URL 已在历史（今晨或昨晚收录）→ 跳过
- ✅ update-news.sh --auto 成功：454 条/8天 → HTML（8-17 组 49 条 = 今晨 18 + 本次新增 31）→ 飞书 21 条入库（4 条重复过滤：After Hormuz/欧盟制裁/库什纳/俄罗斯七死）
- ⚠️ **git push 第 6 次确认**：脚本清代理直连失败 → 手动 `git -c http.proxy=127.0.0.1:7890 push` 成功（eae1168 + 357ad8a）
- ✅ 校验全部通过：今日组 49 条（collectedAt≠今日 0 / date<昨天 0 / URL 重复 0）；官方源 74 条 0 缺中文 0 模板摘要；JS 语法正确；线上 HTTP 200 且 md5 与本地完全一致（24996e71）
- ✅ 92 组 URL 重复经分析**全部为 8-12/8-13 组历史遗留**（组内 90 + 跨组 2），今日组无重复，按"昨日定稿不再改动"原则不处理

### 本次关键发现
1. **同日二次刷新可行**：上午 9:30 运行后，下午可追加采集增量（collectedAt 用本次抓取时间即可，V2.11 归档正常归当日组）
2. **同事件多源只收一版**：卫报北极冰上丝路 vs WSJ 北极航线（同事件不同角度，保留 WSJ 版）；Reuters/SCMP/CNN 江泽民百年诞辰多源，保留 Reuters 版
3. **webfetch 手工条目字段已固化**：title（英文原题）+ collectedAt（抓取日）双字段齐全，V2.11 归档 + 去重键均正常，本次 0 条被误弃
4. **历史遗留重复定位方法**：区分"跨组重复"（今日 vs 历史，危险）与"组内重复"（同组多条，历史遗留），今日组校验只看跨组
5. 8-17 今日高分：WSJ 恒力石化 95 / 英伟达 95（今晨）/ Reuters 江泽民 92 / NYT 中国AI 90 / Reuters 美韩军演 90

### 产出
- 本地: international-news.html (454条/8天)，commit eae1168 + 357ad8a
- 飞书: 21 条新增入库（date=8-17 筛选）
- ✅ 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html（HTTP 200，md5 24996e71 与本地一致）

### 待跟进
- [ ] **update-news.sh 1041 行 git push 清代理**：第 6 次失败确认，建议改 `git -c http.proxy=http://127.0.0.1:7890 push`（超出"不修改脚本"范围，待用户确认）
- [ ] 飞书 8-14 重复 44 条清理（历史遗留，继续待授权）
- [ ] 8-12/8-13 组 URL 重复 92 组（组内重复，历史遗留，量大，是否清理待用户决定）

## 2026-08-17 09:21-09:55 (第十一次运行)

### 执行摘要
- ✅ 官方源采集：白宫0/国务院1/财政部0（curl 直连）；反爬站点（war.gov/USTR/商务部）WebFetch 确认 48h 无新内容（war.gov 最新 8-14 过窗口）；us-official.json 27 条，国务院印尼独立日贺词 agent 翻译补中文 → 100% 中文化、0 导航残留、0 模板摘要
- ✅ WebFetch 采集 11 信源：新增 18 条（Reuters 6/BBC 2/SCMP 2/Guardian 1/NYT 3/WSJ 1/AJ 1/Politico 1/WaPo 1）；WSJ 反爬 → WebSearch 兜底（**英伟达缩减 OpenAI 数据中心担保 2500亿→1200亿 95分**，wsj.com 真实 URL）；Al Jazeera /news 404 → 用 WebSearch 拿 EXPLAINER 真实 URL；de minimis 裁定 8-13 超窗口不收
- ⚠️ **首次整合 bug（重要，下次必检）**：webfetch 手工追加条目缺 `collectedAt` 字段 → V2.11 归档规则 `_ac != today → continue` 全部跳过 → 今日组仅 1 条官方源 → **修复：给今日新增条目补 collectedAt=抓取日（2026-08-17 09:22）后重跑成功**
- ⚠️ **飞书 800030005 来源选项 bug**：手工采集用 `英国广播公司(BBC)`，飞书来源选项只有 `BBC`（SOURCE_MAPPING 无此映射）→ 统一改为 `BBC` 后 sync 成功（4 条 date=8-17 入库）
- ✅ update-news.sh --auto 最终成功：424 条/8天 → HTML（8-17 组 19 条）→ 飞书 4 条 → commit 942dd03/f2c1e7e/c3b5200
- ⚠️ **git push 第 5 次确认**：脚本 1041 行清代理直连失败（本次 1 次）→ 手动 `git -c http.proxy=127.0.0.1:7890 push` 成功（本次脚本第 3 次运行 push 意外成功，属网络波动，仍需代理兜底）
- ✏️ 修复 2 条白宫历史模板摘要（8-15 组：无人机 232 关税行政令/二战胜利文告，WebSearch 拿真实内容）→ 重新生成 HTML → commit 4d01cd3
- ✅ 校验全部通过：今日组 19 条（collectedAt≠今日 0 / date<昨天 0 / URL 重复 0）；官方源 0 缺中文 0 模板摘要；全量 0 模板摘要 0 导航残留；JS 语法正确；线上 HTTP 200 且 md5 与本地完全一致（e116eb43）
- ✅ 数据源文件（webfetch/us-official.json）补充 commit 8d4aacf 推送成功

### 本次关键发现
1. **webfetch 条目必须含 collectedAt 字段**（V2.11 归档依赖）：手工追加时若缺，`_ac != today` 全被丢弃，今日组只剩官方源。fetch_news_v3.py 生成的条目没有 collectedAt？需确认——本次 18 条手工追加全部缺 → 修复后重跑才进今日组。**下次手工追加 webfetch 时必须同时补 title（英文原题）和 collectedAt（抓取日）**
2. **飞书来源选项命名要精确**：`英国广播公司(BBC)` ≠ `BBC`（选项值），`华尔街日报`/`Politico`/`白宫`/`美国国务院` 等在选项内但 SOURCE_MAPPING 无映射（原值透传只要在选项内即可）；手工采集 source 必须用飞书已有选项值
3. **git push 双保险确认（第 5 次）**：脚本清代理直连失败率 ~80%，7890 代理是可靠通道；偶发脚本直连成功（网络波动）
4. **8-17 窗口特点**：昨日 8-16 运行后仅 15h，新增 18 条媒体+1 官方源；多源重复事件（美韩军演 5 源）保留 Reuters 版
5. **飞书 sync --today 按 date==today 筛选**（非归档组）：今日 19 条仅 4 条 date=8-17 入库飞书，15 条 date=8-16 不入库（历史既定行为，与昨日一致）

### 产出
- 本地: international-news.html (424条/8天)，commit 942dd03 + f2c1e7e + c3b5200 + 8d4aacf + 4d01cd3
- 飞书: 4 条已入库（date=8-17）
- ✅ 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html（HTTP 200，md5 e116eb43 与本地一致）

### 待跟进
- [ ] **update-news.sh 1041 行 git push 清代理**：第 5 次失败确认，建议改 `git -c http.proxy=http://127.0.0.1:7890 push`（超出"不修改脚本"范围，待用户确认）
- [ ] fetch_news_v3.py 是否生成 collectedAt：若否，未来自动化采集需注意 V2.11 归档依赖
- [ ] 飞书 8-14 重复 44 条清理（历史遗留，继续待授权）

## 2026-08-14 09:58-10:15 (日期归类修复专项)

### 用户明确指出（重要规则，必须绝对遵守）
- **X 日版面 = X-1 日 9:30 ~ X 日 9:30 之内抓取（更新）的全部内容**
- **X 日 9:30 之后抓到的新内容一律放 X+1 日版面**；昨日版面定稿后不再增加
- 例：无人机关税公告（8-14 今天抓到，即使页面发布日 8-13）→ 必须归 **8-14 版面**，不是 8-13！

### 上次运行的错误（已修复）
- 我把官方源 collectedAt 改成页面真实发布日 → 今天抓的 18 条官方源被归入 8-11/8-12/8-13 组（昨日版面）→ 违反用户规则

### 正确数据模型（已验证）
- **collectedAt = 抓取时间** → 决定版面归档组（今天抓的归今天组）
- **date = 页面真实发布日** → 条目的真实日期显示（≠归档组也允许）
- 前端按 archive key（归档组）分组，date 为显示字段

### 本次修复动作
1. 今天抓取的 18 条官方源（白宫7+国务院9 curl + war.gov 门罗 + USTR Yazaki）→ 从 8-11/8-12/8-13 组**移入 8-14 组**（date 保留真实发布日 8-11/8-12/8-13）
2. 8-14 组 50 条媒体 date 从 webfetch 反查恢复真实发布日（原被 V2.6 覆盖为 8-14）
3. us-official.json collectedAt 修正：今日 18 条 = 2026-08-14 09:20:00；历史条目从 git 0a3d15f 恢复原值；date 保留真实
4. 重新生成 HTML（提取 update-news.sh 841-939 行 GENERATE_HTML_V12 单独运行）
5. commit 61228fa → push（代理）→ 线上 HTTP 200 且 md5 与本地一致（e29c9cdd），8-14 组 68 条

### 下次运行必检
- 官方源 collectedAt 应为抓取日（fetch 脚本自动设），date 为页面真实发布日
- **若 fetch 脚本设置 collectedAt=当天，V2.6 会正确归当天组**（符合用户规则）；date 被 V2.6 覆盖为当天时按需恢复真实发布日（媒体从 webfetch 反查）
- 检查 8-14 组官方源是否被误归昨日组：若 us-official.json collectedAt ≠ 抓取日，则需修正

## 2026-08-14 09:20-10:10 (第九次运行)

### 执行摘要
- ✅ 官方源采集：白宫7/国务院9/财政部0（curl 直连）；WebFetch 补 war.gov 8-12 门罗主义重申（4573580）+ USTR 8-13 Yazaki 快速响应劳工机制；商务部 Cloudflare 拦截无新增；us-official.json 42 条，16 条英文 agent 翻译补中文（含 3 条模板摘要修正），**100% 中文化、0 导航残留、0 模板摘要**
- ✅ 重大发现（WebSearch 确认）：白宫 8-13 ①对进口无人机征收最高 100% 关税（232 条款、直指大疆、9/3 生效，95 分）②《大规模转运骗局》报告（点名 40+ 国、AI 侦探边境、400-3030 亿美元，92 分）——白宫 curl 列表抓到但模板摘要，用 WebSearch 真实内容修正
- ✅ WebFetch 采集 11/11 信源：新增 52 条（总 138 条含昨日窗口），URL 100%、双语 100%；Reuters /world 本次成功；WSJ 反爬 → WebSearch 兜底（Anthropic 2万亿IPO+60亿收购Decart 95分 + 关税休战90天 95分）；Al Jazeera /news 404 → liveblog URL 收录
- ✅ update-news.sh --auto 首次：375 条/8天 → 飞书 44 条（含错误 date 官方源）→ **git push 失败**
- ⚠️ **git push 根因确诊（重要）**：脚本 1041 行 `git -c http.proxy= push` 强制清代理直连，但直连 github（20.205.243.166:443）被墙超时；而 **127.0.0.1:7890 代理实际可用**（curl 走代理 200、curl 强制直连超时）→ 用 `git -c http.proxy=http://127.0.0.1:7890 push` 成功。**修复方向：脚本应保留代理而非清除**
- ⚠️ **V2.6 日期护栏 bug 复发（第3次）**：8-14 组 18 条官方源 date 被覆盖为抓取日 → 修复：把所有官方源 collectedAt 改为真实发布日（37 条）→ 重跑 update-news.sh → 官方源按真实日期归档（8-13:15 / 8-12:11 / 8-11:14，0 错位）✅
- ⚠️ **飞书同步二次失败**：①分类缺「台海」选项 → field-update 补（现 43 个）②第二次同步去重查询网络失败(rc=4)跳过 → **8-14 组 94 条 = 首次 44 + 二次 50 重复**（需授权 bitable scope 或 UI 清理 44 条）
- ✅ 重跑后：HTML 375 条/8天、0 模板摘要、0 缺中文、JS 语法正确、日期 9 按钮/栏目 7 按钮正常；数据源 commit da3b0b1 → **线上 HTTP 200 且 md5 与本地完全一致（c0beba08）**
- ✅ 数据源文件（us-official.json/news-webfetch.json）补充 commit da3b0b1 并推送成功（cddb592..da3b0b1）

### 本次关键发现
1. **git push 的坑是双向的**：直连被墙（超时 75s），7890 代理可用。update-news.sh 1041 行清代理是历史方案（当时代理无服务），现在代理可用 → 用 `git -c http.proxy=http://127.0.0.1:7890 push` 可通。若脚本未来 push 失败，先测代理端口再决定
2. **V2.6 日期护栏 bug 复发机制**：fetch 脚本设置官方源 collectedAt=抓取日，V2.6 见 collectedAt==today 就把 date 覆盖为今天。**根治方法（已验证）**：把 us-official.json 所有官方源 collectedAt 改为真实发布日（date 一致），重跑即可。下次刷新后必检 8-14 组官方源 date
3. **WebFetch 对白宫模板摘要的修正通道**：us-official.json 中 summary 为 "Presidential Actions...BY THE PRESIDENT" 模板时，用 WebSearch 获取真实内容（无人机关税/转运骗局均如此修复）
4. **飞书分类选项又见新值「台海」**（43 个选项），field-update 已补；若再报 800030005 需检查新分类值
5. **飞书重复插入风险**：sync 去重查询失败时（rc=4 网络）跳过查重直接插入 → 必须核对入库数，或同步后检查 8-14 组记录数（应为 50 不是 94）
6. **Al Jazeera /news 404**：用 https://www.aljazeera.com/news/liveblog/2026/8/13/... 模式（liveblog URL）可收录

### 产出
- 本地: international-news.html (375条/8天)，commit cddb592 + da3b0b1
- 飞书: 8-14 组 94 条（含重复 44 条待清理）；官方源补同步待做
- ✅ 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html（HTTP 200，md5 c0beba08 与本地一致）

### 待跟进
- [ ] **飞书 8-14 组重复 44 条清理**：需授权 `lark-cli auth login --scope "bitable:app:readonly bitable:app base:record:retrieve"` 后 raw API 删（按归档日期 09:39 批次），或 UI 按归档时间排序手工删
- [ ] **飞书官方源补同步**：本次 26 条官方源按真实日期在 8-12/8-13 组，sync --today 只同步 8-14 → 官方源未入库飞书（需全量同步或按日期补，注意先查重）
- [ ] **update-news.sh 1041 行 git push 命令**：应保留 7890 代理（当前清代理直连必失败），此修改超出"不修改脚本"范围，待用户确认后改

## 2026-08-13 15:30-16:10 (第八次运行)

### 执行摘要
- ✅ 官方源采集：白宫7/国务院10/财政部0（curl 直连）；WebFetch 补 war.gov 8-12 两条（赫格塞斯巴拿马A3C反卡特尔联盟讲话 88分 + 美安哥拉防务合作委员会联合声明 82分）；USTR 8-11 仅 Iowa 行程类（无政策实质，不收）；商务部无 48h 新内容；us-official.json 41 条
- ⚠️ **fetch_us_official.py 二次运行覆盖坑（重要发现）**：第二次运行脚本时，6 条国务院条目被重新抓取覆盖（date 变 8-13 抓取日、summary 变"[官方信源]"模板、英文摘要清空）→ WebFetch 抓真实内容 + 翻译修正 6 条（date 回 8-11/8-12）；白宫7+国务院10 等 21 条英文 agent 翻译补中文 → 41 条 100% 中文化、0 导航残留、0 模板摘要
- ✅ WebFetch 采集 11/11 信源：追加 33 条（共 87 条，含 48h 旧窗口），URL 100%；**Reuters /world 全天 fetch failed（3次）**；WSJ 反爬 → WebSearch 确认两大元首级新闻收录：①特朗普延长美中关税休战 90 天至 11-10（95 分，cnnbc.com 第三方 URL）②美 BIS 启动中国 AI 远程租赁东南亚算力专项核查（92 分，malaysianow 转载 Bloomberg）
- ✅ update-news.sh --auto 成功：397 条/8天 → HTML → 本地 commit 7ec89da
- ⚠️ **飞书同步首次失败**：分类字段缺「中国」「中东」→ field-update 补 2 选项（现 42 个）→ 重跑成功 43 条入库（1 条重复过滤）
- ✅ 校验通过：官方源 8-13 组 0 缺中文（72 条官方源中 20 条缺中文均为 8-06/8-07/8-09 历史遗留即将滚出窗口）；**V2.6 日期护栏 bug 未复发（官方源日期与归档组 0 不匹配）**；0 模板摘要；0 导航残留；JS 语法正确；前端 8-13 组 44 条高分正确
- ⚠️ **git push 首次失败：代理 127.0.0.1:7890 未运行**（8 个常见端口全不通、直连 443 超时、SSH 无 key）→ 16:00 网络恢复后重推成功（da65b01..0a3d15f），线上 HTTP 200 且 md5 与本地完全一致
- ✅ 飞书核对：8-13 入库 43 条 = 本地 44 - 1 重复（N Korea ballistic missile 已在库），基本一致
- ✅ **最终线上验证通过**：https://iranorawahaha.github.io/international-news-kb/international-news.html（397 条/8天，8-13 组 44 条，md5 8cd980f7 与本地一致）

### 本次关键发现
1. **fetch_us_official.py 每次运行会重新抓取并覆盖同 URL 官方源条目**（摘要→模板、date→抓取日）：如需运行两次，第一次翻译修正的数据会被覆盖 → 修正翻译必须放最后，或运行后立即检查 date 是否=抓取日
2. **特朗普 8-12 签署行政令延长美中关税休战 90 天至 11-10**（美对华 30%、中方 10% 维持）——白宫 curl 抓取漏掉（行政令发布较晚/列表截断），靠 WebSearch 确认 + 第三方 cnnbc.com URL 收录
3. **BIS 专项核查中国 AI 企业远程租赁东南亚算力**（月之暗面 Kimi K3 泰国 GB300 训练）为 AI 芯片监管重大新闻（92 分），无权威英文 URL，用 malaysianow.net 转载收录
4. **今日分类全集新增「中国」「中东」**：飞书选项已补（42 个），后续无需再补
5. 8-13 组 44 条分布：美国24/中国2/中美关系3/台海2/经贸制裁2/科技2/地缘政治2/欧洲2/俄乌冲突3/中东1/军事安全1；高分：朱镕基逝世 95×3 源（BBC/NYT/WaPo 元首级）、关税休战 95、中美投资委员会停滞 92、BIS 算力核查 92、中印尼联合军演 90、莱维特离任 88×2

### 产出
- 本地: international-news.html (397条/8天)，commit 7ec89da + 0a3d15f
- 飞书: 8-13 组 43 条已入库
- ⚠️ 线上未更新（push 阻塞，待代理恢复）

### 待跟进
- [x] **git push 阻塞** → 已解决（16:00 网络恢复，da65b01..0a3d15f 推送成功，线上 md5 一致）
- [ ] 飞书 8-06/8-07/8-09 历史官方源 20 条缺中文（即将滚出窗口，可忽略）
- [ ] Reuters /world WebFetch 连续失败（fetch failed），下次需换 reuters.com 其他路径或备用通道
- [ ] fetch_us_official.py 二次运行覆盖坑：如需重跑脚本，翻译修正必须在最后进行（脚本每次运行会覆盖同 URL 条目的 date/summary）

## 2026-08-12 09:20-10:20 (第七次运行)

### 执行摘要
- ✅ 官方源采集：白宫5/国务院10/财政部0（curl 直连）；WebFetch 补 war.gov 8-10/8-11 共 5 条（金穹Hub/坚韧弓箭手帕劳演习/赫格塞斯访巴拿马/基地更名/美摩多域实弹）+ USTR 无 48h 新内容 + 商务部 Cloudflare 拦截；us-official.json 37 条，15 条英文 agent 翻译补中文，100% 中文化、0 导航残留、0 模板摘要
- ✅ WebFetch 采集 11/11 信源：54 条（WSJ 反爬仍失败 → WebSearch 确认 Nvidia 5000亿AI融资 finwire.io URL + Anthropic IPO wsj.com URL 收录，均为 95/92 高分），URL 100%
- ✅ update-news.sh --auto 成功：424 条 → git push (021db33) → 构建 built
- ⚠️ **飞书同步首次失败**：分类字段缺「军事安全」「地区热点」+ 历史遗留 6 分类（AI科技/国防安全/外交资讯/欧洲安全/科技产业/英国政治）→ field-update 全量补 8 选项 → 全量同步 116 条成功（8-11:78 + 8-12:43 + 历史缺口）
- ⚠️ **V2.6 日期护栏 bug（重要发现）**：update-news.sh V2.6 把 collectedAt=今天 的官方源强制归入今天组并覆盖 date（页面真实 8-10/8-11 → 8-12），破坏官方源真实日期归档 → 手动按 us-official.json 修正 20 条 + 清理超窗口条目 2 条 + 清理行政令摘要页面元数据（Presidential Actions/Executive Orders）→ 重新生成 HTML（422条/8天）→ push eada2e1 + 06c2837
- ✅ 校验全部通过：官方源 69 条 0 缺中文 0 模板摘要 0 日期错位；前端 0 导航残留 0 模板摘要；JS 语法正确；线上 HTTP 200 且与本地 md5 完全一致（422 条）
- ✅ 飞书核对：8-12 入库 43 条 = 本地 43 条（URL 全匹配）；8-11 本地 78 条全覆盖（74 条在飞书 8-11 组 + 4 条按真实日期 8-10 归档）

### 本次关键发现
1. **V2.6 日期护栏误伤官方源**：`_a['date'] = _today` 把官方源 date 覆盖为采集日。官方源 collectedAt≠date（页面真实发布日），V2.6 设计只针对媒体条目"迟到抓取归今天"，但官方源也匹配 collectedAt==today 条件 → 8-10/8-11 官方源全被挪到 8-12 组。**下次刷新后必须检查官方源 date 是否又被覆盖**（脚本未修复，属"不修改脚本"范围，靠人工终极防线兜底）
2. **飞书补分类选项注意**：历史遗留分类（AI科技/国防安全/外交资讯/欧洲安全/科技产业/英国政治）来自 8-03~8-05 旧数据，全量同步时会再次触发 800030005 → 本次已一次性补齐，后续无需再补
3. **webfetch 合并去重只看 webfetch 文件**：fetch_us_official.py 合并 us-official-webfetch.json 时，若某条目已在 news-data.json（昨日收录），今天再加入 webfetch 会导致飞书重复（war.gov 美摩多域 2 条）→ 合并前需查 news-data.json
4. **record-list/filter-json 均不返回 record_id**：lark-cli base 封装层剥离 record_id，raw API 缺 bitable scope 需授权 → 飞书字段级修正（改新闻日期/删重复）需用户授权 scope 或 UI 手工处理
5. **行政令摘要含页面元数据**：白宫 presidential-actions 页面 summary 抓取含 "Presidential Actions ... Executive Orders August 6, 2026" 头部 → 需正则清理

### 产出
- 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html (422条/8天，HTTP 200 md5 一致)
- 今日: 8-12 组 28 条 | 高分: WSJ 95(英伟达5000亿AI融资) / SCMP 92(美出口管制无战略收益) / WSJ 92(Anthropic IPO路演) / BBC 90(特朗普空军一号换机) / SCMP 90(Meta终止Manus AI交易) / 半岛88(美军向霍尔木兹封锁货船开火)
- 六大栏目: 美国192 / 地区热点156 / 中国34 / 其他23 / 欧洲17
- 飞书存档: https://my.feishu.cn/base/A2fdb93HLamcKgslr2rcopjRnfd (全量 1106 条，8-12:43 唯一)

### 待跟进
- [ ] **飞书 16 条官方源新闻日期仍为 8-12**（本地已修正为真实日期，飞书需授权 raw API bitable scope 后 record-batch-update 或 UI 手工改）
- [ ] **飞书 war.gov 美摩多域 1 条重复**（归档 8-11/8-12 各一条，需删 1 条）
- [ ] 8-05 组 61 条缺中文（历史遗留，明天滚出窗口）
- [ ] **V2.6 日期护栏 bug 需在脚本层修复**（当前靠人工兜底，下次刷新后必检官方源 date）

## 2026-08-11 09:20-09:55 (第六次运行)

### 执行摘要
- ✅ 官方源采集：白宫5/国务院9/财政部0（curl 直连）；WebFetch 补 war.gov 8-10 两条（Colby 马尼拉印太讲话/U.S.-摩洛哥多域实验中心）；USTR/商务部无 48h 内新内容；us-official.json 33 条，100% 中文化、0 导航残留、0 模板摘要（白宫5+国务院9 共 14 条英文由 agent 翻译补全，含黄岩岛声明 HTML 实体转义坑）
- ✅ WebFetch 采集 11/11 信源：112 条（保留昨日 48h 窗口 56 条 + 新增 56 条），URL 100%（WSJ 反爬用 WebSearch 确认苹果 CXMT 新闻，URL 用 finwire.io 真实转载链接；WSJ /world 多次 JS-BLOCKED，sitemap/RSS 均不可用）
- ✅ update-news.sh --auto 成功：440 条/8 天 → HTML → git push (6dbcbba) → 构建 built
- ⚠️ **飞书同步首次失败**：800030005 分类字段缺「国际」选项（今日 5 条 category=国际）→ field-update 补选项（type 必须用字符串 "select" 非数字 3）→ 重跑成功 40 条入库
- ✅ 飞书核对：8-11 入库 40 条 = 本地 8-11 组 40 条（完全一致，无误插无遗漏）
- ✅ 校验全部通过：官方源 68 条（news-data）0 缺中文 0 模板摘要；官方源按真实日期归档 0 不匹配；前端 440 条 0 模板摘要；今日 40 条 100% 中文化；JS 语法正确；线上 HTTP 200 且与本地 md5 完全一致
- ✅ sync_to_feishu.py 去重查询已修复（--format json + offset 分页），本次去重正常（飞书 883 条/539 唯一键）

### 本次关键发现
1. **飞书 field-update type 必须为字符串**："select"（数字 3 报 800010701 Invalid discriminator）
2. **今日 category 全集变化**：地缘政治/美国/科技/经贸/军事/国际——「国际」是新分类值，需补飞书选项
3. **WSJ 反爬升级**：本次 /world、/news/world、sitemap、RSS 全部失败（DataDome captcha），仅能靠 WebSearch 获知新闻内容；苹果 CXMT 为重大新闻（95分）用 finwire.io 转载 URL 收录
4. **黄岩岛国务院声明标题含 HTML 实体**（&#8217;/&#8220;），翻译匹配需先 html.unescape
5. 前端校验注意：嵌入数据模式为 `NEWS_DATA = {...}`（archive 结构），非数组；缺中文 128 条均为 8-04/8-05 历史遗留（即将滚出 7 天窗口），非本次问题

### 产出
- 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html (440条/8天)
- 今日: 8-11 组 40 条 | 高分: WSJ 95(苹果测试长鑫CXMT芯片,重大) / BBC 92(英伟达5000亿美元AI基建) / SCMP 92(中国加入巴西WTO诉美国强迫劳动关税) / 路透90(特朗普秘密航班) / 卫报90(特朗普要求伊朗赔偿) / 半岛90(特朗普称霍尔木兹已开放)
- 飞书存档: https://my.feishu.cn/base/A2fdb93HLamcKgslr2rcopjRnfd (8-11:40 条唯一)

### 待跟进
- [ ] 飞书 8-04/8-05 历史条目 128 条缺中文（即将滚出 7 天窗口，可忽略或补译）
- [ ] WSJ 反爬持续升级，未来或需固定第三方转载通道
- [ ] 今日 category「国际」已补飞书选项，确认后续不再报 800030005

## 2026-08-07 09:20-09:45 (第四次运行)

### 执行摘要
- ✅ 官方源采集：白宫8/国务院10/财政部0（curl 直连）；WebFetch 补商务部/国防部/USTR 均无 48h 内新内容（最新 8-05/8-03/7-24），保留已有 13 条 webfetch 合并；us-official.json 共 31 条
- ✅ 官方源中文化：白宫8+国务院10 共 18 条全英文 → 脚本翻译补全 title_zh/summary_zh（弯引号处理坑），31 条官方源 100% 中文化、0 导航残留、0 模板摘要
- ✅ WebFetch 采集 11/11 信源：80 条（WSJ 反爬仅 1 条真实URL、Politico 需用主站非 /news/world、AP 用 /hub/world-news），URL 100%
- ✅ update-news.sh --auto 成功：515 条/8天 → HTML → git push (4fda2d3) → 构建 built
- ✅ 校验全部通过：官方源 53 条 0 缺中文 0 模板摘要；官方源按真实发布日归档；嵌入 JSON 可解析 515 条；JS 语法正确；线上 HTTP 200 与本地完全一致
- ✅ 飞书核对：8-07 入库 3 条 = date=8-07 真实条目数（与本地一致，无误插）

### 本次关键发现
1. **飞书去重查询失败根因确认**：lark-cli 1.0.82 不再支持 `--format csv`（仅 markdown/json）→ sync_to_feishu.py `get_existing_unique_keys()` 一直失败。用 `--format json` + 分页 offset 人工核对成功（1707 条，字段: idx0=采集时间/idx1=摘要/idx2=元首级/idx3=url/idx4=新闻日期/idx8=中文标题/idx10=分类/idx11=来源）
2. **归档分组说明**：HTML 8-07 组 32 条含 27 条 date=8-06 媒体条目（URL 无日期模式如 scmp article/xxxx 导致"真实报道日期重分配"失效，归入采集日组）；**官方源全部按 date 正确归档**（各组 date 与归档 key 完全一致）。此为用户可见的已知行为，非本次错误
3. WSJ 反爬持续：仅获取 1 条确认真实 URL（live coverage 8-03）
4. Politico /news/world 404 → 用主站 https://www.politico.com/ 成功

### 产出
- 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html (515条/8天)
- 今日: 8-07 组 32 条 | 高分: SCMP 92(习特峰会前景,元首级) / CNN 92(习访美前制裁,元首级) / 路透88×3 / 多晶硅关税 88×4 / 霍尔木兹 88×5
- 飞书存档: https://my.feishu.cn/base/A2fdb93HLamcKgslr2rcopjRnfd (8-07:3 条新)

### 待跟进
- [ ] **飞书 8-03 重复 1293 条清理**（历史遗留，本次 8-07 全量核对仍确认存在）
- [ ] sync_to_feishu.py 去重查询修复方向已明确：--format csv 不被支持，应改 --format json 并解析嵌套结构
- [ ] 8-06 组 46 条 vs 本地 74 条：飞书增量同步滞后 28 条（URL 无日期模式条目 date=8-06 未入库 8-06 组？下次需核对）

## 2026-08-06 09:20-10:05 (第三次运行)

### 执行摘要
- ✅ 官方源采集：白宫9/国务院9/财政部0（curl 直连）；WebFetch 补国防部 2 条新条目（巴拿马运河演习/西半球联合特遣部队），us-official.json 共 31 条
- ✅ 官方源中文化：白宫9+国务院9 等 18 条全英文 → 手动翻译补全 title_zh/summary_zh（含历史4条），45 条官方源 100% 中文化、0 导航残留、0 模板摘要
- ✅ WebFetch 采集 11/11 信源：79 条（WSJ 反爬仅 4 条真实URL、Politico 6、WaPo 6、AP 7），URL 100%
- ✅ update-news.sh --auto 成功：451 条/8天 → HTML → git push (4039ec4) → 构建 built
- ✅ 补充官方源中文化后重新生成 HTML + git push (acdf86b)
- ✅ 线上验证通过：HTTP 200，451 条，日期Tab/栏目Tab 正常

### ⚠️ 本次发现的问题（已解决）
1. **飞书分类/来源字段缺选项**：分类缺 9 个（俄乌冲突/亚洲/欧洲/中国社会/军事国防/台海局势/媒体自由/科技主权/美国），来源缺 6 个（白宫/美国国务院/美国国防部/财政部/商务部/USTR）→ field-update 补齐后同步成功
2. **飞书 8-04/8-05 记录缺失**（0 条，昨日自动同步失败）：手动补同步 204 条（按 title[:30]+source 去重）→ 8-04:136 ✅ / 8-05:68 ✅ / 8-06:9 ✅（与本地完全一致）
3. **⚠️ 补同步批次1失败（12条旧分类值：地区热点/中国/军事安全等）**：补 CATEGORY_MAPPING 后重跑成功；但**重跑时 8-04 重复插入 150 条**（第二次以旧 keys2 去重漏判）→ record-delete 清理 150 条，最终 8-04:136 唯一 ✅
   - **教训：补同步必须每次重新拉取飞书全量唯一键；批处理建议 25 条/批避免网络超时**
4. **⚠️ 飞书 8-03 严重重复 1293 条**（历史遗留，本地仅 74 条）：未清理（超出本次刷新范围），**待跟进**
5. WSJ 反爬（需 JS）：用 WebSearch 获取 4 篇真实 URL（含社论/乌克兰安全保障/金属废料出口）

### 产出
- 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html (451条/8天)
- 今日: 8-06 组 37 条 | 高分: SCMP 92(习特会前对台军售,元首级) / AP 92(中国对美反制,元首级) / 路透88 / 伊朗-霍尔木兹多条 88
- 飞书存档: https://my.feishu.cn/base/A2fdb93HLamcKgslr2rcopjRnfd (8-04:136 / 8-05:68 / 8-06:9，唯一)

### 待跟进
- [ ] **飞书 8-03 重复 1293 条清理**（按 title[:30]+source 去重保留最早，预计删 1200+）
- [ ] sync_to_feishu.py 去重查询失败（csv validation error）根因修复
- [ ] update-news.sh 飞书步骤误报成功（exit 0 但实际失败）——需人工核对入库数
- [ ] 官方源 fetch_us_official.py 中文翻译缺失：白宫/国务院抓取后需 agent 补 title_zh

## 2026-08-03 09:20-09:40 (第二次运行)

### 执行摘要
- ✅ WebFetch 采集 11/11 信源成功，88 条（每信源 8 条），URL 100%
- ✅ data/news-webfetch.json 88 条（修复 JSON 中文引号问题后校验通过）
- ✅ update-news.sh --auto 执行成功：整合 90 条 → 253 条 / 4 天存档 → HTML → git push (0a23db4) → 构建 built
- ✅ 线上验证通过：https://iranorawahaha.github.io/international-news-kb/international-news.html（今日 90 条可见）
- ✅ 飞书同步手动补做完成：249 条 / 0 重复

### ⚠️ 本次发现的问题（已解决）
1. **手写 JSON 中文引号破坏文件**：title/summary 中的中文引用误写为 ASCII 引号导致 JSON 解析失败 → 用 Python 正则将字符串内部成对引号替换为弯引号修复。
2. **飞书"分类"字段缺 9 个选项**：移民危机/自然灾害/美国政治/社会/文化/环保/经济金融/安全/科技 不在 select 选项中，同步报 800030005 not_found。
   → `lark-cli base +field-update` 追加 9 个选项（现 17 个）后手动 record-batch-create 同步今日 90 条成功。
3. **sync_to_feishu.py 去重查询仍失败**（csv 解析 validation error，遗留问题）：改用 `--filter-json` 按新闻日期查询今日记录验证 90 条入库；
   全量 offset 分页 + (title[:30],source) 查重发现 2 组重复（basic 旧数据混入）→ record-delete 删除 2 条 → 249 条 / 0 重复。
4. **update-news.sh 飞书步骤误报成功**：sync 失败但 exit code 0，脚本仍显示"✅ 同步完成"。需人工核对飞书实际入库数。

### 产出
- 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html
- 今日 90 条 | 高分: SCMP 98(戴恩斯返京/习特峰会) / 路透95 / BBC95 / WSJ95 / 卫报95 / CNN95(美伊谈判) / 元首级 18 条
- 飞书存档: https://my.feishu.cn/base/A2fdb93HLamcKgslr2rcopjRnfd (249 条, 0 重复)

### 待跟进
- [ ] sync_to_feishu.py 去重查询失败的修复（建议改用 --filter-json 或修复 csv 解析；超出"不修改脚本"指令范围）
- [ ] record-list 无 page_token 字段，分页需用 --offset；去重脚本参数已摸清（--filter-json / --offset / --limit 200）
- [ ] 手动同步流程：field-update 补选项 → prepare 脚本转记录 → record-batch-create → 查重 → record-delete

## 2026-08-02 09:20-09:45 (首次运行)

### 执行摘要
- ✅ WebFetch 采集 11/11 信源成功（Politico 首 URL 404，重试主站成功）
- ✅ data/news-webfetch.json 写入 75 条（11 信源全覆盖，URL 100%）
- ✅ update-news.sh --auto 执行成功：整合去重 → 163 条 / 3 天存档 → HTML → git push (0c59ce4)
- ✅ GitHub Pages 构建健康检查通过，线上页面可访问
- ✅ 飞书同步修复并完成

### ⚠️ 本次发现的问题（已解决）
1. **飞书来源字段缺选项**：`华尔街日报`、`Politico` 不在飞书"来源"select 字段选项中，导致同步失败。
   → 用 `lark-cli base +field-update` 追加 2 个选项后同步成功（163 条）。
2. **飞书表大量重复**：表内累积 568 条记录（仅 161 组唯一）。
   → 根因：sync_to_feishu.py 去重查询 `get_existing_unique_keys()` 失败（lark-cli record-list csv 解析问题），导致每次全量插入。
   → 处置：写脚本按 (title[:30], source) 分组、保留最早、批量删除 407 条重复 → 161 条 / 0 重复。
   → 注意：脚本去重逻辑缺陷仍在，下次同步前应先人工确认去重查询是否恢复，或同步后检查表内重复数。

### 产出
- 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html
- 今日 77 条 | 高分: 美联社98(伊朗威胁) / SCMP 97(戴恩斯访华, 元首级) / 卫报95 / CNN95 / WSJ95
- 飞书存档: https://my.feishu.cn/base/A2fdb93HLamcKgslr2rcopjRnfd (161 条, 0 重复)

### 待跟进
- [ ] sync_to_feishu.py 去重查询失败的修复（超出"不修改脚本"指令范围，暂未处理）
- [ ] Politico 使用 https://www.politico.com/news/world 可能 404，采集时直接试主站

## 2026-08-10 09:20-10:30 (第五次运行)

### 执行摘要
- ✅ 官方源采集：白宫5/国务院9/财政部0（curl 直连）；WebFetch 补 war.gov 8-07 三条（Sila电池$1.4B/Niron无稀土磁体$150M/Sunrise钪矿$400M）+ USTR 8-07 关键矿产定价基准 → us-official.json 31 条，100% 中文化、0 导航残留、0 模板摘要
- ✅ WebFetch 采集 11/11 信源：65 条（WSJ 6 真实URL、Politico 主站+politico.eu 修正URL、WaPo 仅 2-3 条 48h 内、AP 用 /hub/world-news），URL 100%
- ⚠️ **并发执行冲突（重要教训）**：自动化系统与 agent 并行执行 update-news.sh，系统重试时 `rm -f news-webfetch.json` 导致数据丢失，产生 381 条不完整版本 push 覆盖线上 → 用 `git checkout 10dd563 --` 恢复 447 条完整版 + 重建 webfetch（从 news-data 反向提取 62 条）+ 重建 us-official（从 news-data 拷回中文）→ 重跑成功 447 条
- ✅ 最终：445 条/8天（删 2 条新华网坏数据 + 修正 4 条白宫 summary_en 残留），git push 4f7d760，线上 HTTP 200 且与本地 md5 完全一致
- ✅ 飞书：800030005 分类缺 5 选项（国际政治/外交/经贸制裁/经贸/军事）+ 来源缺 1（新华网）→ field-update 补齐；全表清理 1370 条重复 → 539 条唯一；8-10 组 74 条唯一（完整覆盖本地 56 条 + 系统并行采集 18 条）
- ✅ 校验全部通过：官方源 66 条 0 缺中文 0 模板摘要；官方源按真实日期归档 100% 匹配；前端 0 模板摘要 0 导航残留；JS 语法正确

### 本次关键发现
1. **系统自动重试会并发执行 update-news.sh**：重试命令含 `rm -f data/news-webfetch.json` 前缀，会删掉已采集数据 → 每次跑完 update 后立即检查 git log / news-data.json 是否被并发覆盖
2. **恢复完整数据的捷径**：news-data.json 与 international-news.html 在 git 中 → `git checkout <完整commit> -- data/news-data.json international-news.html gh-pages/international-news.html index.html gh-pages/index.html` 可一键恢复；webfetch 可从 news-data.json 按 source∈11媒体+date 反向提取重建
3. **系统 V2.5.2 并行提交**（96b2201）：移除中文信源 + 8/10 重抓 57 篇外媒，其数据已并入最终版本；飞书 8-10 组 74 条 = 本地 56 + 系统采集 18
4. **field-update 是 full PUT 语义**：payload 必须去掉 id 字段（800010701 Unrecognized key 'id'）；options 需全量提交
5. **record-list --format json 结构**：data.data 二维数组 + data.fields 列名（0归档日期/1摘要/2重要性/3原文链接/4新闻日期/5是否元首级/6英文标题/7优先级分数/8中文标题/9关键词/10分类/11来源）；飞书"中文标题"字段可能是英文（sync 写入逻辑），核对用 URL 级比对更可靠
6. **WSJ/Politico/AP 采集通道**：WSJ /world 可抓真实URL；Politico 用主站 + politico.eu 修正；AP 用 /hub/world-news
7. 8-08/8-09 组仅 8/2 条（周末无刷新，日期组少），8-10 组 56 条（含重分配）

### 产出
- 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html (445条/8天)
- 今日: 8-10 组 56 条 | 高分 20 条（88+）：内塔尼亚胡拒加沙计划(90×多源) / 特朗普"半谈判"伊朗(90) / 中国高超音速航母杀手(90) / 中国反制升级(88) / 伊朗-霍尔木兹多条(88)
- 飞书存档: https://my.feishu.cn/base/A2fdb93HLamcKgslr2rcopjRnfd (539 条唯一，8-10:74)

### 待跟进
- [x] 飞书 8-03 重复 1293 条 → **本次已清理**（全表 539 唯一）
- [x] sync_to_feishu.py 去重查询失败 → **2026-08-11 已修复**（改用 --format json 分页解析，commit 88f0a21）
- [x] 系统并发执行 update 的防护 → **2026-08-11 已修复**（update-news.sh 增加 pid 锁 .update-news.lock，commit 88f0a21）

## 2026-08-11 09:20-09:40 (脚本改进，非刷新运行)

### 执行摘要
- ✅ 修复 sync_to_feishu.py 去重查询：`get_existing_unique_keys` 从 `--format csv`（lark-cli 1.0.82 不支持）改为 `--format json` + offset 分页 + 动态列映射（fields.index 定位中文标题/来源）+ 网络抖动重试 3 次
- ✅ 验证：查询成功 883 条记录 / 539 组唯一键（与人工核对一致）；完整 dry-run 445 输入 → 340 重复过滤 → 105 新增预览（去重流程打通）
- ✅ update-news.sh 增加 pid 锁（.update-news.lock）：活跃锁拒绝执行、残留锁自动清理、EXIT/INT/TERM trap 释放；测试通过
- ✅ .gitignore 增加 .update-news.lock；git push 88f0a21
- 说明：dry-run 显示"新增 105 条"为键不匹配预估（本地 title 双语 vs 飞书记录格式差异），实际同步由 update 每日 --today 增量执行，风险低

### 产出
- commit 88f0a21（3 files changed: sync_to_feishu.py / update-news.sh / .gitignore）

## 2026-08-16 09:55-11:30 (第十次运行，V2.11 修复专项)

### 执行摘要
- ✅ 官方源采集：白宫 0 条（今日无新公告，8-14 为窗口外正常过滤）、国务院 2 条（刚果/列支敦士登国庆日贺词，从 news-data 反查补中文）、财政部 0、商务部 0、国防部 0、USTR 0（WebFetch 确认 48h 无新）；us-official.json 28 条，100% 中文化、0 导航残留、0 模板摘要
- ✅ WebFetch 采集 11/11 信源：新增 19 条（剔除 4 条 date=8-14 的 SCMP 超窗口条目 + 6 条 URL 重复跳过），含重大发现：路透 35 国 AI 选边站（95分，tbsnews 转载 URL）、WSJ 苹果禁购中国存储芯片（95分，tradingview DJN 转载 URL）、AP 美军撤走亚洲最后一艘航母（90分）
- ⚠️ **V2.11 去重 bug 根因（重要）**：手工追加的 webfetch 条目缺 `title` 字段（只有 title_en/title_zh）→ 去重键 `(title[:30], source)` 变成 `('', source)` → 同 source 多条互相碰撞误删 7 条（俄袭基辅/塔利班/印尼地震/列支敦士登/哥伦比亚关税/埃尔多安/也门）→ 修复：给缺 title 的条目补 `title=title_en`（44 条）→ 重跑后 17 条全保留 ✅
- ✅ update-news.sh --auto 第二次运行成功：414 条/8天 → HTML → 飞书 3 条 → git commit 43304c5 → **脚本 push 仍失败（清代理直连被墙）→ 手动 `git -c http.proxy=127.0.0.1:7890 push` 成功**
- ✅ 校验全部通过：今日组 17 条（collectedAt≠今日 0、date<昨天 0、URL重复 0）；官方源 2 条 0 缺中文 0 模板摘要；全量 0 导航残留 0 模板摘要；JS 语法正确；线上 HTTP 200 且 md5 与本地完全一致（ecdefec4）
- ✅ 数据源文件（webfetch/us-official.json）补充 commit 6689871 并推送成功

### 本次关键发现
1. **webfetch 条目必须含 title 字段**（fetch_news_v3.py 生成的条目有 title=英文原题；手工追加时若只写 title_en 会导致去重键碰撞误删）——V2.11 去重 bug 第 1 次发现，已修复数据，脚本无需改
2. **今日窗口=8-15 23:32~8-16 9:30**：昨晚 23:32 已有一次更新（8-15 定稿 404 条），今日新增仅 15 条媒体 + 2 条官方源；date=8-14 的 SCMP 4 条（台海训练/花旗/中芯/AI治理）因超窗口剔除
3. **git push 双保险确认**：脚本 1041 行清代理直连必失败（本次 3 次），7890 代理可用（2.2s 响应）→ 手动代理 push 是可靠通道，待用户确认改脚本
4. 白宫 /news/ 直连 WebFetch 404 但走代理 curl 200（正常页面）；今日白宫最新公告为 8-14（无 8-15/16 新内容）

### 产出
- 本地: international-news.html (414条/8天)，commit 43304c5 + 6689871
- 飞书: 今日 3 条已入库（2 国庆日 + 1 其他）
- ✅ 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html（HTTP 200，md5 ecdefec4 与本地一致）

### 待跟进
- [ ] **update-news.sh 1041 行 git push 清代理**：第 4 次失败确认，建议改 `git -c http.proxy=http://127.0.0.1:7890 push`（超出"不修改脚本"范围，待用户确认）
- [ ] 飞书 8-14 重复 44 条清理（历史遗留，继续待授权）
## 2026-08-26 09:23-09:55 (第十八次运行)

### 执行摘要
- ⚠️ **源组丢失坑复发（第 4 次）**：fetch_us_official.py 国务院 curl 407（代理）失败 → 国务院 9 条整组被覆盖丢失、白宫 5→2、国防部 23→21 → 运行前备份 /tmp/us-official-backup-0826.json 恢复 44 条 + merge 今日白宫 2 条 → 46 条 6 源齐全
- ✅ 官方源采集：白宫 2 条新（**8-25 特朗普"终结加拿大搭便车"88 分元首级**（涉华关联：加拿大是除中国外唯一选择报复的国家，加宣布新增 276 亿对美关税）+ 多莉·帕顿降半旗 75 分）；war.gov 稀土 7.5 亿（8-24）→ **因 date=8-24 超窗口（<8-25 昨天）按 V2.11 规则剔除重跑**（8-25 采集漏收，今日补采已过窗口）；财政部/USTR/商务部 48h 无新
- ✅ WebFetch 采集：35 条新增（路透6/BBC5/SCMP6/NYT5/卫报1/CNN2/半岛2/WaPo4/AP3/彭博1）；WSJ/Politico 反爬 0 条如实汇报；**Bloomberg 独家"美拟习特会前对华加征 7.5% 产能过剩关税"95 分元首级**（用 Yahoo Finance 转载 URL，source 标彭博社，延续第三方转载先例）
- ✅ update-news.sh --auto 两次：首次 238 条 → 发现 war.gov 稀土超窗口 → 数据源双端剔除 → 重跑 237 条 → 8-26 组 36 条
- ✅ 校验全部通过：今日组 36 条（collectedAt≠今日 0 / date<昨天 0 / 跨组 URL 重复 0 / 组内重复 0）；缺中文 0；官方源 2 条 0 缺中文 0 模板摘要；JS 语法正确；**线上 HTTP 200 且 md5 与本地完全一致（04f4bab0）**
- ✅ 飞书：date=8-26 的 6 条已入库（首次同步 6 条新增，重跑 6 条全去重跳过）；git push 3 次全走 7890 代理（60ab4f0/2a2d736/6d4e08a/a1244cc）

### 本次关键发现
1. **源组丢失坑第 4 次确认**：备份恢复仍是唯一保险；国务院 curl 407 时先 `env -u http_proxy curl` 测直连
2. **war.gov 8-24 稀土公告漏采教训**：8-25 采集漏收（反爬），8-26 补采时 date=8-24 超窗口 → 严格按 V2.11 剔除，**反爬站点官方源也需 48h 内及时采集，错过窗口即丢失**
3. **今日主题：美三线经济战**（对华 7.5% 关税临近上限 / 对加 50% 关税+加拿大报复 / 对伊"经济放逐"次级制裁）+ 习特会前中美博弈（一轨半对话）+ 台湾 AI 服务器走私案 + 南海建设
4. **今日高分**：彭博 7.5% 对华关税 95★ / SCMP 一轨半对话 90★ / BBC 中国抨击对伊制裁 90 / NYT 中国反击 90 / 卫报 AI 服务器走私 90 / 白宫加拿大搭便车 88★ / Reuters 南海建设 88 / WaPo 中国渔利 88

### 产出
- 本地: international-news.html (237条/6天，8-26 组 36 条)，commit 60ab4f0/2a2d736/6d4e08a/a1244cc
- 飞书: 6 条已入库（date=8-26）
- ✅ 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html（HTTP 200，md5 04f4bab0 与本地一致）

### 待跟进
- [ ] war.gov/USTR 等反爬官方源漏采窗口问题：错过 48h 即丢失，建议后续在 9:30 采集时优先 WebFetch war.gov releases 页
- [ ] fetch_us_official.py 源组丢失防护（第 4 次确认，超出"不修改脚本"范围，待用户确认）

## 2026-08-29 09:23-09:45 (第二十一次运行)

### 执行摘要
- ⚠️ **源组丢失坑复发（第 7 次）**：fetch_us_official.py 白宫 12→2、国务院 12→3、国防部 23→21 整组被覆盖 → 运行前备份 /tmp/us-official-backup-0829.json 恢复 + merge 今日 5 条 → 59 条 6 源齐全（白宫14/国务院15/国防部23/财政部3/商务部1/USTR3）100% 中文化 0 导航残留
- ✅ 官方源新增 5 条：**白宫 ①美军中央司令部确认美控制霍尔木兹海峡非伊朗（8-28，88★，约1500艘商船7.5亿桶原油/伊朗石油出口为零）②设立美国航天学院总统委员会行政令（8-28，75）**；**国务院 ③制裁伊朗国家银行迪拜分行经理+香港公司（8-28，90★，经济放逐行动延续，E.O.13224/13902）④撤销伊拉克裔国民签证（获拜登"国际勇气女性奖"、FBI恐怖观察名单，8-28，75）⑤鲁比奥祝贺摩尔多瓦国庆日（8-29，75）**；国防部/USTR/商务部/财政部 48h 无新
- ✅ WebFetch 采集 41 条新增（11 源全覆盖尝试）：路透 10/SCMP 7/NYT 6/半岛 5/BBC 4/WaPo 3/AP 3/卫报 2/CNN 1；**WSJ 0（Nvidia 暂停收入分成 8-27、AI 热潮支撑经济 8-27 均超窗口剔除，如实汇报）+ Politico 0（Cloudflare 拦截，8-28 半导体关税已收录）**；Reuters 中国黑客收回说法用 Yahoo 转载 URL（88★）；同事件多源去重：委内瑞拉石油保留 Reuters 版（BBC/AP/卫报跳过）、冰岛公投保留 Reuters 版、尼泊尔洪水保留 AP 版
- ✅ update-news.sh --auto 一次成功：279 条/6 天，8-29 组 45 条（35 媒体 date=8-28 + 10 条 date=8-29）→ 飞书 10 条（date=8-29，0 重复）→ commit 9e4179e **push 直连成功** → 数据源 commit d7428a5（代理推送）
- ✅ 校验全部通过：今日组 45 条（collectedAt≠今日 0 / date<昨天 0 / 跨组 URL 重复 0 / 组内重复 0）；官方源 15 条 0 缺中文 0 模板摘要 0 摘要过短；今日组 45/45 中文 0 缺摘要 0 模板摘要 0 导航残留；JS 语法正确；**线上 HTTP 200 且 md5 与本地完全一致（2985b1c7）**

### 本次关键发现
1. **今日主题：美伊战争六个月多线聚焦**（美军确认控制霍尔木兹 88★ + 国务院制裁伊朗金融生命线 90★ + 美财政部制裁香港公司 Kameng Trading 92★ + 埃及银行制裁 85 + IRGC 宣称管控海峡 88）+ **中美关系**（美收回"中国黑客攻击"说法 88★ + 习特峰会筹备 92★ + 乌兹别克斯坦 AI 阵营试探 88★）+ **AI 科技**（Anthropic 五角大楼胜诉 90★ + 阿联酋 AI 强国 88★ + Meta/Instagram 成瘾判决 82）+ 委内瑞拉石油协议 90★
2. **源组丢失坑第 7 次确认**：备份恢复仍是唯一保险；本次白宫/国务院/国防部三源同时被覆盖（curl 失败整组丢失），备份合并后 59 条完好
3. **超窗口严格剔除**：WSJ Nvidia 暂停收入分成（8-27）与 AI 热潮经济文章（8-27）虽重要但 date<8-28 按 V2.11 剔除；CNN Anthropic 版（8-27）改用 AP 版（8-28）收录
4. **飞书 sync --today 按 date==today 筛选**：今日 45 条仅 10 条 date=8-29 入库（35 条 date=8-28 不入库，历史既定行为）
5. **Politico 连续 Cloudflare 拦截**：/world 与主站均 Just a moment 验证页；8-28 半导体关税 92★ 已收录故今日无遗漏风险

### 产出
- 本地: international-news.html (279条/6天，8-29 组 45 条)，commit 9e4179e + d7428a5
- 飞书: 10 条已入库（date=8-29）
- ✅ 线上: https://iranorawahaha.github.io/international-news-kb/international-news.html（HTTP 200，md5 2985b1c7 与本地一致）

### 待跟进
- [ ] fetch_us_official.py 源组丢失防护（第 7 次确认，超出"不修改脚本"范围，待用户确认）
- [ ] Politico 反爬加剧：连续 2 日 Cloudflare 拦截，WebSearch 兜底；若未来有 Politico 独家重大新闻需及时 WebSearch

## 2026-08-29 10:00-10:05 (第二十一次运行·补充修订)

### 同事补充 2 条遗漏新闻（重要教训）
- **长鑫存储起诉美国国防部（Reuters，8-28，95★）**：CXMT 在哥伦比亚特区地区法院起诉，要求撤销 1260H"中国军事企业清单"认定，称 DRAM 纯民用商业；6-8 被重新列入（2 月曾短暂移除），YMTC/药明/阿里已先例诉讼 → 用 newsx.com 转载 URL（reuters 直连不可达）
- **The Information：特朗普政府起草新 AI 出口管制规则堵中国远程算力（8-28，92★）**：BIS 起草规则堵中国经泰国/新加坡第三国数据中心远程租用美 AI 芯片算力漏洞（现行管制只覆盖物理芯片），最早 9 月征求意见，将取代拜登 AI Diffusion Rule；触发点=月之暗面 Kimi K3 泰国 GB300 蒸馏指控 → 用 tomshardware 转载 URL（The Information 付费墙）
- 重跑 update-news.sh：281 条/6 天，8-29 组 47 条，四项归档校验 0 违规，commit beb05d7 + f0716cf，线上 md5 三方一致（0f56d210）

### ⚠️ 机制改良（防同类遗漏，2026-08-29 新增流程步骤）
**遗漏根因**：① The Information/SemiAnalysis 不在 11 必选源（AI 独家媒体天然漏采）② Reuters /world 单次抓取只见置顶（CXMT 起诉在 business 频道）③ "AI 出口管制/远程算力"主题多次靠人工补（8-13 BIS 算力核查、8-29 新规都是 WebSearch 补录）
**新增每日交叉验证步骤（更新脚本后必做）**：官方源+WebFetch 完成后，用 3 组固定关键词 WebSearch 兜底：
1. `China AI chips export controls 1260H CXMT YMTC`（涉华芯片/清单）
2. `US China tariffs sanctions announcement`（中美经贸）
3. `AI export control remote access compute China`（AI 远程算力）
命中 date∈{昨天,今天} 的重大新闻立即补录 webfetch（collectedAt=抓取日）→ 重跑
**补充源**：The Information 列入"重点主题补充源"（AI 芯片/出口管制主题必查，WebSearch 转载确认）；Reuters 重大日补抓 /technology /business 频道

## 2026-08-29 10:30-10:50 (第二十一次运行·转载标注机制专项)

### 用户反馈：看板转载链接问题
- 用户点进长鑫存储起诉国防部条目，发现链接指向 world.newsx.com（信源清单以外）而非 reuters.com → 要求"换高质量转载+标注"
- **根因**：Reuters 官方 URL 反爬完全封锁（WebSearch 全被屏蔽、构造 reuters.com 链接 404、site: 搜索无果）→ 当时沿用历史"WSJ 反爬第三方转载"先例，但 newsx.com 是低质聚合站且未标注，source 标"路透社"误导用户
- **用户决策**：换高质量转载 + 明确标注（不误导为官方原文直链）

### 修复动作（V2.12 转载标注机制）
1. **数据层**：webfetch/news-data 增加 `repost_from` 字段（标注转载来源+原因）——长鑫条(NewsX 全文转载)/Yahoo条(Yahoo News 转载)/The Information条(Tom's Hardware 报道)
2. **模板层**：scripts/intl_template_v15.html 新增 `.repost-tag` CSS + 链接列渲染 `item.repost_from ? <span class="repost-tag" title="⚠️ 转载来源">转载</span>`
3. **脚本层**：update-news.sh 696 行字段白名单加 `repost_from`（官方源终极防线透传）
4. ⚠️ **发现去重坑**：deduplicate_articles 保留 archive 旧版本（无 repost_from），丢弃 webfetch 新版（有标注）→ 直接改 news-data.json + 单独跑 GENERATE_HTML_V12 段（不重跑全量 update）才生效
5. commit d7f574d 推送成功，线上 md5 95034241 与本地一致（CDN 首查旧版、二次才命中新版，历史已知）

### 转载 URL 收录纪律（V2.12 固化）
- 官方源反爬拿不到官网 URL 时：可选转载必须为**知名平台/专业媒体**（Yahoo News/Tom's Hardware/finwire.io 等），**禁用低质聚合站**（newsx.com/esaa.org.eg 等）
- 转载条目必须加 `repost_from` 字段 + 前端"转载"标签，source 仍标原作者
- 拿不到合格转载 → 宁缺毋滥不收录

## 2026-08-29 10:40-11:00 (第二十一次运行·官网 URL 方法论专项)

### 用户关键洞察：为什么委内瑞拉条能拿到 reuters.com 官网 URL？
- 用户发现：委内瑞拉石油条 URL https://www.reuters.com/business/energy/us-enters-into-oil-agreement-with-venezuela-trump-says-2026-08-28/ 是官网直链，但长鑫条是转载站 → 问方法能否复制
- **方法论确认（V2.13 核心）**：
  - ✅ **WebFetch 直接抓路透分类页（/world、/business、/technology、/legal）= 正确通道**，页面内嵌文章链接就是官网 URL（委内瑞拉条、长鑫条均如此拿到）
  - ❌ **WebSearch = 错误通道**（反爬源在搜索中被屏蔽，只返回 newsx/esaa 等转载站）
- 实操验证：WebFetch https://www.reuters.com/business/ → 第 1 条就是长鑫官网报道 https://www.reuters.com/world/cxmt-sues-pentagon-over-inclusion-list-companies-tied-chinas-military-2026-08-29/ → WebFetch 验证页面真实（标题 Chipmaker CXMT sues Pentagon...，作者 Che Pan/Mrinmay Dey，发布日期 8-29）

### 修复动作
- 长鑫条 URL 替换为官网原文 + 移除 repost_from 标注 + date 改 8-29 → 直接改 news-data/webfetch + 单独跑 GENERATE_HTML_V12 → commit 317eb73 推送成功，线上 md5 f88f895b 一致，旧 newsx URL 清零
- 自动化 prompt 升级 V2.13：加入"官网 URL 获取方法论"（WebFetch 分类页为正道、WebSearch 仅作线索）+ 转载纪律中"发现官网 URL 立即替换"

### 经验固化
- **取官网 URL 的正确姿势**：WebFetch 信源官网频道页（页面链接=官网）> WebSearch（被反爬屏蔽）
- 交叉验证的 WebSearch 只用于"发现线索"，URL 一律回官网分类页取
