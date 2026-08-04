# Ira 信息看板体系 - 项目记忆

## 项目总览
- **仓库**: github.com/Iranorawahaha/international-news-kb（单仓库承载国际+国内两个看板）
- **GitHub Pages**: https://iranorawahaha.github.io/international-news-kb/
- **定位**: 个人使用 + 向同事分享（华为公共及政府事务部）
- **认证**: Personal Access Token (repo 权限)；推送失败时检查 `$https_proxy` 环境变量

## 看板1: 国际新闻看板 (V1.2.3, 2026-08-01)
- **入口**: https://iranorawahaha.github.io/international-news-kb/
- **V1.2.3**: 彻底移除中文信源（BASIC_SOURCES=[]），11个英文信源全必选（路透/BBC/SCMP/卫报/CNN/NYT/WSJ/半岛/Politico/WaPo/AP）
- **V1.2.2**: 智能打分 `_calculate_priority_score`（默认55分，极高92/高78/元首95）、智能分类、黑名单25+关键词、5条过滤规则
- **V1.2.1**: 飞书去重修复（88→66条）；质量体系固化（is_garbage/clean/dedup/sort 4函数）
- **核心功能**: 7天数据保留(日期Tab) + 飞书Base永久存档 + 双语标题 + 元首级置顶 + 重要性5级 + 单文件HTML
- **飞书存档**: https://my.feishu.cn/base/A2fdb93HLamcKgslr2rcopjRnfd（表ID tblCocvO66XoPsm1，名称"新闻存档"）
- **更新**: `./update-news.sh`（6步：抓取→筛选→去重→排序→飞书归档→HTML生成→Git推送，3-5分钟；WebFetch步骤需在WorkBuddy中执行）
- **使用流程**: 基础采集(终端) → WebFetch补充(对话) → 整合 → 网页生成 → 飞书同步 → git push

## 看板2: 国内新闻看板（Ira 体系，每日9:30自动刷新）
- **入口**: https://iranorawahaha.github.io/international-news-kb/china-news.html
- **一键脚本**: `./refresh_china_news.sh`（3步：抓取 gov.cn 要闻+最新政策 → build_china.py 生成深红政务风单文件看板 → 部署+门户统计+git push）
- **数据**: data/china-news.json；生成: china-news.html（根目录+gh-pages副本）
- **自动化**: automation-1785577010192 每日 09:30 执行（模型 deepseek-v4-flash）
- **质量**: JUNK_KEYWORDS 黑名单过滤营销/文娱/明星八卦/养生内容；严禁修改信源/过滤规则/构建脚本

## 技术架构
- 前端: 单文件自包含 HTML（CSS+JS+数据内嵌，无外部依赖）
- 采集: Python 3.13.12 (/Users/xiaoxiao/.workbuddy/binaries/python/versions/3.13.12/bin/python3)
- 数据: JSON 按日期分组 {archive:{date:[...]}}；7天滚动窗口 + 飞书永久存档双轨制
- 版本控制: Git + GitHub Pages；根目录与 gh-pages/ 双同步

## 质量体系要点
- 唯一键: (title[:30], source)；同步前查询飞书已有记录去重
- 双层质量控制: 采集时过滤 + 整合时再过滤
- 双层排序: Python层 + JS渲染层
- URL完整性4道防线: WebFetch要求URL + validate_urls + 渲染原文链接列 + ≥95%覆盖率检查

## 用户偏好
- 关注: 中美关系 > 经贸制裁 > AI竞争 > 外交资讯
- 语言: 英文资讯双语保存；仅权威信源，禁自媒体/营销号
- 更新: 每日2次（9:30+17:00），手动控制时机

## 已解决问题
- GitHub Pages CSS/JS 404 → 单文件HTML架构
- 11条缺URL(42%) → URL保障机制(100%覆盖)
- 飞书22条重复 → 批量删除+同步前去重
- 中文信源低质(20条仅2可用) → 智能打分+黑名单(90%过滤)
- 版本混乱 → V1.0正式版统一

## 关键经验
1. WebFetch必须明确要求返回URL字段
2. 整合前检查关键字段完整性（尤其url）
3. 静态站优先单文件架构
4. 推送失败先查 $https_proxy 代理端口
5. 定期清理工作空间（历史备份/临时文件）
6. 黑名单关键词是质量生命线（导航页/营销/软文）

## 待优化
- 每日17:00自动邮件日报（用户延后配置）
- macOS LaunchAgent 定时提醒 / WorkBuddy Automation 半自动
- 修复不可用信源（4 URL失效+2 SSL+3反爬）
- 移动端PWA / RSS输出 / 多语言
