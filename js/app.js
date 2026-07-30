// 全局状态
let newsData = {
    meta: {},
    news: []
};
let config = {};
let filteredNews = [];
let draggedRow = null;

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    // 优先使用内嵌数据（解决跨域和加载失败问题）
    await loadEmbeddedData();

    // 如果内嵌数据为空，尝试从API/文件加载
    if (!config.sources || config.sources.length === 0) {
        console.log('内嵌数据为空，尝试从文件加载...');
        await loadConfig();
    }

    if (!newsData.news || newsData.news.length === 0) {
        console.log('新闻数据为空，尝试从文件加载...');
        await loadData();
    }

    renderSources();
    renderTable();
    populateFilters();
    updateStatusBar();

    console.log(`✅ 数据加载完成: ${newsData.news.length} 条新闻, ${config.sources?.length || 0} 个信源`);
});

// 加载内嵌数据（最可靠的方式）
async function loadEmbeddedData() {
    try {
        // 方式1: 检查 window.NEWS_CONFIG / window.NEWS_DATA (当前生成格式)
        if (typeof window.NEWS_CONFIG !== 'undefined' && window.NEWS_CONFIG.sources) {
            config = window.NEWS_CONFIG;
            console.log('✅ 已加载内嵌配置数据 (window.NEWS_CONFIG):', config.sources.length, '个信源');
        }
        else if (typeof EMBEDDED_CONFIG !== 'undefined') {
            config = EMBEDDED_CONFIG;
            console.log('✅ 已加载内嵌配置数据 (EMBEDDED_CONFIG)');
        }

        // 新闻数据可能是数组或对象
        if (typeof window.NEWS_DATA !== 'undefined') {
            if (Array.isArray(window.NEWS_DATA)) {
                // window.NEWS_DATA 是纯数组
                newsData = { meta: window.NEWS_META || {}, news: window.NEWS_DATA };
            } else {
                // window.NEWS_DATA 是对象（含meta和news字段）
                newsData = window.NEWS_DATA;
            }
            filteredNews = [...(newsData.news || [])];
            console.log(`✅ 已加载内嵌新闻数据 (window.NEWS_DATA): ${(newsData.news || []).length} 条`);
        }
        else if (typeof EMBEDDED_NEWS_DATA !== 'undefined') {
            newsData = EMBEDDED_NEWS_DATA;
            filteredNews = [...(newsData.news || [])];
            console.log(`✅ 已加载内嵌新闻数据 (EMBEDDED_NEWS_DATA): ${(newsData.news || []).length} 条`);
        }
    } catch (error) {
        console.warn('⚠️ 内嵌数据加载失败，将尝试其他方式:', error);
    }
}

// 加载配置（备用方案）
async function loadConfig() {
    try {
        const response = await fetch('data/config.json');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        config = await response.json();
        console.log('✅ 从文件加载配置成功');
    } catch (error) {
        console.error('加载配置失败:', error);
        showToast('⚠️ 配置文件加载失败，使用默认配置', 'warning');
        // 使用最小化默认配置
        config = {
            sources: [
                { id: "default", name: "默认信源", url: "", type: "custom", language: "zh", enabled: true, todayCount: 0 }
            ],
            categories: ["中美关系", "经贸制裁", "人工智能竞争", "外交资讯", "国际政治", "芯片产业政策", "地区热点", "多边机制"]
        };
    }
}

// 加载数据（备用方案）
async function loadData() {
    try {
        const response = await fetch('data/news-data.json');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        newsData = await response.json();
        filteredNews = [...(newsData.news || [])];
        console.log(`✅ 从文件加载数据成功: ${(newsData.news || []).length} 条`);
    } catch (error) {
        console.error('加载数据失败:', error);
        // 保持空数据，不显示错误提示（避免干扰用户）
        newsData = { meta: {}, news: [] };
        filteredNews = [];
    }
}

// 保存数据
async function saveData() {
    try {
        newsData.meta.totalCount = newsData.news.length;
        newsData.meta.lastUpdated = new Date().toISOString();

        // 尝试调用后端API（如果存在）
        try {
            const response = await fetch('/api/save-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newsData)
            });

            if (response.ok) {
                updateStatusBar();
                showToast('✅ 数据已保存到服务器', 'success');
                return;
            }
        } catch (apiError) {
            console.log('后端API不可用，使用本地存储');
        }

        // 备用方案：使用localStorage + 下载文件
        localStorage.setItem('newsKnowledgeBase_data', JSON.stringify(newsData));
        localStorage.setItem('newsKnowledgeBase_config', JSON.stringify(config));

        updateStatusBar();
        showToast('✅ 数据已保存到浏览器本地存储', 'success');

    } catch (error) {
        console.error('保存数据失败:', error);
        showToast('⚠️ 数据保存失败，但数据仍在内存中可用', 'warning');
    }
}

// 手动下载数据文件（供用户备份）
function downloadDataBackup() {
    try {
        const dataStr = JSON.stringify(newsData, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `news-data-backup-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showToast('✅ 数据备份文件已下载', 'success');
    } catch (error) {
        showToast('❌ 下载失败: ' + error.message, 'error');
    }
}

// 渲染信源列表
function renderSources() {
    const grid = document.getElementById('sourcesGrid');
    if (!config.sources) return;

    grid.innerHTML = config.sources.map(source => `
        <div class="source-card" data-source-id="${source.id}">
            <div class="source-name">${source.name}</div>
            <div class="source-info">
                <span class="language-tag">${source.language === 'zh' ? '中文' : '英文'}</span>
                <span class="source-count ${source.todayCount > 0 ? '' : 'zero'}">
                    今日: ${source.todayCount || 0}
                </span>
            </div>
        </div>
    `).join('');
}

// 分类英文→中文映射表
const CATEGORY_MAP = {
    'us-china': '中美关系',
    'trade-sanctions': '经贸制裁',
    'ai-tech': 'AI/芯片/通信',
    'diplomacy': '中国外交',
    'geopolitics': '地缘政治',
    'regional-asia': '亚太地区',
    'regional-europe': '欧洲事务',
    'regional-others': '其他地区',
    'consulate-news': '使领馆动态',
    // 兼容旧中文分类
    '中美关系': '中美关系',
    '经贸制裁': '经贸制裁',
    '人工智能竞争': 'AI/芯片/通信',
    '外交资讯': '中国外交',
    '国际政治': '地缘政治',
    '芯片产业政策': 'AI/芯片/通信',
    '地区热点': '其他地区',
    '多边机制': '国际组织'
};

// 国家关键词映射（用于自动提取涉及国家）
const COUNTRY_KEYWORDS = {
    '美国': ['美国', '美利坚', '华盛顿', '白宫', '特朗普', '拜登', '五角大楼', '国会山'],
    '中国': ['中国', '北京', '中方', '华为', '商务部', '外交部', '习近平'],
    '俄罗斯': ['俄罗斯', '俄方', '莫斯科', '普京', '克里姆林宫'],
    '伊朗': ['伊朗', '德黑兰', '伊朗革命卫队'],
    '以色列': ['以色列', '特拉维夫', '内塔尼亚胡'],
    '沙特阿拉伯': ['沙特', '利雅得'],
    '日本': ['日本', '东京', '岸田'],
    '韩国': ['韩国', '首尔', '尹锡悦'],
    '朝鲜': ['朝鲜', '平壤', '金正恩'],
    '印度': ['印度', '新德里', '莫迪'],
    '英国': ['英国', '伦敦', '唐宁街'],
    '法国': ['法国', '巴黎', '马克龙'],
    '德国': ['德国', '柏林', '朔尔茨'],
    '欧盟': ['欧盟', '布鲁塞尔', '欧洲委员会'],
    '乌克兰': ['乌克兰', '基辅', '泽连斯基'],
    '伊拉克': ['伊拉克', '巴格达'],
    '联合国': ['联合国', '安理会']
};

// 获取中文分类名称
function getCategoryName(category) {
    return CATEGORY_MAP[category] || category;
}

// 从文本中自动提取涉及的国家/地区
function extractCountries(item) {
    // 如果已有countries字段，直接使用
    if (item.countries && Array.isArray(item.countries) && item.countries.length > 0) {
        return item.countries;
    }

    const text = `${item.title || ''} ${item.summary || ''} ${(item.keywords || []).join(' ')}`;
    const countries = new Set();

    for (const [country, keywords] of Object.entries(COUNTRY_KEYWORDS)) {
        if (keywords.some(kw => text.includes(kw))) {
            countries.add(country);
        }
    }

    return Array.from(countries);
}

// 渲染新闻表格
function renderTable() {
    const tbody = document.getElementById('newsTableBody');
    const emptyState = document.getElementById('emptyState');

    if (filteredNews.length === 0) {
        tbody.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';
    tbody.innerHTML = filteredNews.map((item, index) => {
        // 字段兼容性处理
        const dateValue = item.date || item.publishTime || item.crawlTime;
        const urlValue = item.url || item.sourceUrl || item.link;
        const countries = extractCountries(item);
        const categoryName = getCategoryName(item.category);

        return `
        <tr draggable="true" data-index="${index}" data-id="${item.id}">
            <td class="col-sort">⇅</td>
            <td>${formatDate(dateValue)}</td>
            <td class="title-cell">${escapeHtml(item.title)}</td>
            <td>${escapeHtml(item.source)}</td>
            <td class="summary-cell">${escapeHtml(item.summary)}</td>
            <td class="tags-cell">
                ${countries.map(c => `<span class="tag">${escapeHtml(c)}</span>`).join('')}
            </td>
            <td><span class="tag">${escapeHtml(categoryName)}</span></td>
            <td class="tags-cell">
                ${(item.keywords || []).map(k => `<span class="tag">${escapeHtml(k)}</span>`).join('')}
            </td>
            <td class="link-cell">
                ${urlValue ? `<a href="${escapeHtml(urlValue)}" target="_blank">查看原文</a>` : '-'}
            </td>
            <td><span class="tag importance-${getImportanceClass(item.importance)}">${item.importance || '中'}</span></td>
            <td class="action-cell">
                <button class="btn-delete" onclick="deleteNews('${item.id}')" title="删除">🗑️</button>
            </td>
        </tr>
    `}).join('');

    initDragAndDrop();
}

// 初始化拖拽排序
function initDragAndDrop() {
    const rows = document.querySelectorAll('#newsTableBody tr[draggable="true"]');

    rows.forEach(row => {
        row.addEventListener('dragstart', handleDragStart);
        row.addEventListener('dragover', handleDragOver);
        row.addEventListener('drop', handleDrop);
        row.addEventListener('dragend', handleDragEnd);
    });
}

function handleDragStart(e) {
    draggedRow = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

function handleDrop(e) {
    e.preventDefault();
    if (draggedRow !== this) {
        const fromIndex = parseInt(draggedRow.dataset.index);
        const toIndex = parseInt(this.dataset.index);

        // 重新排序数组
        const [movedItem] = filteredNews.splice(fromIndex, 1);
        filteredNews.splice(toIndex, 0, movedItem);

        // 同步到原始数据
        newsData.news = [...filteredNews];

        renderTable();
        saveData();
        showToast('排序已更新', 'success');
    }
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    draggedRow = null;
}

// 删除新闻
async function deleteNews(id) {
    if (!confirm('确定要删除这条新闻吗？')) return;

    newsData.news = newsData.news.filter(item => item.id !== id);
    filteredNews = filteredNews.filter(item => item.id !== id);

    renderTable();
    await saveData();
    showToast('删除成功', 'success');
}

// 填充筛选选项
function populateFilters() {
    const categorySelect = document.getElementById('filterCategory');
    const sourceSelect = document.getElementById('filterSource');
    const exportCategory = document.getElementById('exportCategory');

    // 分类选项（使用中文显示）
    if (config.categories) {
        // 获取所有实际使用的分类并去重
        const usedCategories = [...new Set(filteredNews.map(n => n.category))];
        categorySelect.innerHTML = '<option value="">全部分类</option>' +
            usedCategories.map(cat => `<option value="${cat}">${getCategoryName(cat)}</option>`).join('');

        exportCategory.innerHTML = config.categories.map(cat =>
            `<option value="${cat}">${getCategoryName(cat)}</option>`
        ).join('');
    }

    // 信源选项
    if (config.sources) {
        sourceSelect.innerHTML = '<option value="">全部信源</option>' +
            config.sources.map(s => `<option value="${s.name}">${s.name}</option>`).join('');
    }
}

// 应用筛选
function applyFilters() {
    const dateFilter = document.getElementById('filterDate').value;
    const categoryFilter = document.getElementById('filterCategory').value;
    const sourceFilter = document.getElementById('filterSource').value;
    const importanceFilter = document.getElementById('filterImportance').value;
    const keywordFilter = document.getElementById('filterKeyword').value.toLowerCase();

    filteredNews = newsData.news.filter(item => {
        if (dateFilter && item.date !== dateFilter) return false;
        if (categoryFilter && item.category !== categoryFilter) return false;
        if (sourceFilter && item.source !== sourceFilter) return false;
        if (importanceFilter && item.importance !== importanceFilter) return false;
        if (keywordFilter) {
            const searchFields = [item.title, item.summary, item.keywords?.join(' '), item.countries?.join(' ')].join(' ').toLowerCase();
            if (!searchFields.includes(keywordFilter)) return false;
        }
        return true;
    });

    renderTable();
}

// 更新状态栏
function updateStatusBar() {
    document.getElementById('lastRefreshTime').textContent =
        newsData.meta.lastFetchTime ? formatDateTime(newsData.meta.lastFetchTime) : '--';
    document.getElementById('totalCount').textContent = newsData.news.length || 0;
    document.getElementById('newCount').textContent = newsData.meta.lastFetchNewCount || 0;
}

// 显示进度条
function showProgress(show) {
    const container = document.getElementById('progressContainer');
    container.style.display = show ? 'flex' : 'none';
}

function updateProgress(percent, text) {
    document.getElementById('progressBar').style.width = `${percent}%`;
    document.getElementById('progressText').textContent = text || `${percent}%`;
}

// 模态框控制
function showModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function showQuickEntryModal() {
    showModal('quickEntryModal');
    document.getElementById('quickEntryUrl').value = '';
    document.getElementById('parseResult').style.display = 'none';
}

function showBatchImportModal() {
    showModal('batchImportModal');
    document.getElementById('batchImportData').value = '';
}

function showExportModal() {
    showModal('exportModal');
    // 设置默认日期范围
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('exportDateFrom').value = today;
    document.getElementById('exportDateTo').value = today;
}

function showAddSourceModal() {
    showModal('addSourceModal');
    document.getElementById('sourceName').value = '';
    document.getElementById('sourceUrl').value = '';
}

// 显示提示消息
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 刷新数据（离线模式：提示用户运行抓取脚本）
async function refreshData() {
    showProgress(true);
    updateProgress(0, '正在准备采集...');

    try {
        // 方案1: 尝试调用后端API（如果服务器在运行）
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000); // 3秒超时

        try {
            const response = await fetch('/api/refresh', {
                method: 'POST',
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (response.ok) {
                // API可用，使用SSE流式响应
                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const text = decoder.decode(value);
                    const lines = text.split('\n').filter(line => line.trim());

                    for (const line of lines) {
                        try {
                            const data = JSON.parse(line);
                            if (data.type === 'progress') {
                                updateProgress(data.percent, data.message);
                            } else if (data.type === 'complete') {
                                newsData = data.data;
                                filteredNews = [...newsData.news];
                                renderSources();
                                renderTable();
                                updateStatusBar();
                                showProgress(false);
                                showToast(`✅ 刷新完成！新增 ${data.newCount} 条新闻`, 'success');
                                return; // 成功，直接返回
                            } else if (data.type === 'error') {
                                throw new Error(data.message);
                            }
                        } catch (e) {
                            // 忽略非JSON行
                        }
                    }
                }
            } else {
                throw new Error(`服务器返回错误: ${response.status}`);
            }
        } catch (apiError) {
            clearTimeout(timeoutId);

            // API不可用或超时，切换到离线模式
            console.log('后端API不可用，切换到离线模式:', apiError.message);

            // 显示操作指引
            showProgress(false);

            const userChoice = confirm(
                '🔄 数据刷新需要运行抓取脚本\n\n' +
                '请选择操作方式：\n\n' +
                '✅ 点击【确定】查看详细操作说明\n' +
                '❌ 点击【取消】稍后再说'
            );

            if (userChoice) {
                // 打开操作说明
                showRefreshGuide();
            } else {
                showToast('ℹ️ 可稍后手动刷新数据', 'info');
            }

            return;
        }
    } catch (error) {
        console.error('刷新过程出错:', error);
        showProgress(false);
        showToast('刷新失败: ' + error.message, 'error');
    }
}

// 显示刷新操作指南
function showRefreshGuide() {
    const guideHTML = `
        <div style="max-width:800px;margin:20px auto;font-family:-apple-system,sans-serif;line-height:1.8;">
            <h2 style="color:#2563eb;border-bottom:2px solid #2563eb;padding-bottom:10px;">
                📰 新闻数据抓取指南
            </h2>

            <div style="background:#eff6ff;border-left:4px solid #2563eb;padding:15px;margin:15px 0;">
                <h3 style="margin-top:0;color:#1e40af;">🎯 方式一：一键抓取（推荐）</h3>
                <p>在终端中运行以下命令：</p>
                <pre style="background:#1e293b;color:#e2e8f0;padding:15px;border-radius:8px;overflow-x:auto;">cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50
python3 scripts/fetch_news.py</pre>
                <p>等待抓取完成后，<strong>刷新本页面</strong>即可看到最新数据。</p>
            </div>

            <div style="background:#f0fdf4;border-left:4px solid #22c55e;padding:15px;margin:15px 0;">
                <h3 style="margin-top:0;color:#166534;">⏰ 方式二：设置每日自动抓取</h3>
                <p>编辑系统定时任务（crontab）：</p>
                <pre style="background:#1e293b;color:#e2e8f0;padding:15px;border-radius:8px;overflow-x:auto;"># 每天早上8点自动抓取新闻
0 8 * * * cd /Users/xiaoxiao/WorkBuddy/2026-07-29-17-06-50 && /usr/bin/python3 scripts/fetch_news.py >> logs/cron.log 2>&1</pre>
                <p>这样每天早上打开页面就能看到最新新闻！</p>
            </div>

            <div style="background:#fefce8;border-left:4px solid #eab308;padding:15px;margin:15px 0;">
                <h3 style="margin-top:0;color:#854d0e;">💡 方式三：快速更新单个信源</h3>
                <pre style="background:#1e293b;color:#e2e8f0;padding:15px;border-radius:8px;overflow-x:auto;"># 只抓取路透社
python3 scripts/fetch_news.py --source reuters

# 只抓取BBC
python3 scripts/fetch_news.py --source bbc

# 抓取所有英文媒体
python3 scripts/fetch_news.py --lang en</pre>
            </div>

            <div style="background:#fafafa;border-radius:8px;padding:15px;margin-top:20px;">
                <h3 style="margin-top:0;">📊 当前数据状态</h3>
                <p><strong>总新闻数:</strong> ${newsData.news?.length || 0} 条</p>
                <p><strong>上次更新:</strong> ${newsData.meta?.lastUpdated || '未知'}</p>
                <p><strong>数据文件位置:</strong> <code>data/news-data.json</code></p>
            </div>

            <button onclick="this.parentElement.remove()" style="
                margin-top:20px;
                padding:10px 30px;
                background:#2563eb;
                color:white;
                border:none;
                border-radius:6px;
                cursor:pointer;
                font-size:16px;
            ">关闭指南</button>
        </div>
    `;

    // 创建模态窗口显示指南
    const modal = document.createElement('div');
    modal.id = 'refresh-guide-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.7);
        z-index: 10000;
        overflow-y: auto;
        padding: 20px;
    `;
    modal.innerHTML = guideHTML;
    document.body.appendChild(modal);

    // 点击背景关闭
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// 解析并添加新闻（快速录入）
async function parseAndAddUrl(url) {
    try {
        const response = await fetch('/api/parse-url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        if (!response.ok) throw new Error('解析失败');

        const parsed = await response.json();
        return parsed;
    } catch (error) {
        console.error('URL解析失败:', error);
        throw error;
    }
}

async function parseAndAddNews() {
    const url = document.getElementById('quickEntryUrl').value.trim();
    if (!url) {
        showToast('请输入新闻链接', 'error');
        return;
    }

    try {
        showToast('正在解析链接...', 'info');
        const parsed = await parseAndAddUrl(url);

        // 显示预览
        document.getElementById('parsedContent').innerHTML = `
            <p><strong>标题：</strong>${escapeHtml(parsed.title)}</p>
            <p><strong>来源：</strong>${escapeHtml(parsed.source)}</p>
            <p><strong>摘要：</strong>${escapeHtml(parsed.summary)}</p>
            <p><strong>日期：</strong>${parsed.date || '--'}</p>
        `;
        document.getElementById('parseResult').style.display = 'block';

        // 自动添加到数据库
        parsed.id = generateId();
        parsed.date = parsed.date || new Date().toISOString().split('T')[0];
        parsed.importance = parsed.importance || '中';

        newsData.news.unshift(parsed);
        filteredNews = [parsed, ...filteredNews];

        await saveData();
        renderTable();
        closeModal('quickEntryModal');
        showToast('新闻已成功添加！', 'success');
    } catch (error) {
        showToast('解析失败：' + error.message + '，请检查链接是否正确', 'error');
    }
}

// 批量导入
async function batchImport() {
    const data = document.getElementById('batchImportData').value.trim();
    if (!data) {
        showToast('请输入要导入的数据', 'error');
        return;
    }

    try {
        const lines = data.split('\n').filter(line => line.trim());
        let imported = 0;

        for (const line of lines) {
            // 支持制表符或 | 分隔
            const fields = line.split(/\t|\|/).map(f => f.trim());
            if (fields.length >= 3) {
                const newsItem = {
                    id: generateId(),
                    date: fields[0] || new Date().toISOString().split('T')[0],
                    title: fields[1],
                    source: fields[2],
                    summary: fields[3] || '',
                    countries: fields[4] ? fields[4].split(',').map(s => s.trim()) : [],
                    category: fields[5] || '',
                    keywords: fields[6] ? fields[6].split(',').map(s => s.trim()) : [],
                    url: fields[7] || '',
                    importance: fields[8] || '中',
                    createdAt: new Date().toISOString()
                };

                newsData.news.unshift(newsItem);
                imported++;
            }
        }

        filteredNews = [...newsData.news];
        await saveData();
        renderTable();
        closeModal('batchImportModal');
        showToast(`成功导入 ${imported} 条新闻`, 'success');
    } catch (error) {
        showToast('导入失败：' + error.message, 'error');
    }
}

// 批量导出
function exportData() {
    const dateFrom = document.getElementById('exportDateFrom').value;
    const dateTo = document.getElementById('exportDateTo').value;
    const categories = Array.from(document.getElementById('exportCategory').selectedOptions).map(o => o.value);
    const format = document.getElementById('exportFormat').value;

    // 筛选数据
    let exportList = newsData.news.filter(item => {
        if (dateFrom && item.date < dateFrom) return false;
        if (dateTo && item.date > dateTo) return false;
        if (categories.length && !categories.includes(item.category)) return false;
        return true;
    });

    if (exportList.length === 0) {
        showToast('没有符合条件的数据可导出', 'error');
        return;
    }

    let content, filename, type;

    switch (format) {
        case 'json':
            content = JSON.stringify(exportList, null, 2);
            filename = `国际新闻知识库_${dateFrom}_${dateTo}.json`;
            type = 'application/json';
            break;
        case 'csv':
            content = convertToCSV(exportList);
            filename = `国际新闻知识库_${dateFrom}_${dateTo}.csv`;
            type = 'text/csv';
            break;
        case 'excel':
            // 简化处理：导出为CSV格式（实际Excel需要库支持）
            content = convertToCSV(exportList);
            filename = `国际新闻知识库_${dateFrom}_${dateTo}.csv`;
            type = 'text/csv';
            showToast('提示：已导出为CSV格式，可用Excel打开', 'info');
            break;
    }

    downloadFile(content, filename, type);
    closeModal('exportModal');
    showToast(`成功导出 ${exportList.length} 条记录`, 'success');
}

// 新增信源
async function addNewSource() {
    const name = document.getElementById('sourceName').value.trim();
    const url = document.getElementById('sourceUrl').value.trim();

    if (!name || !url) {
        showToast('请填写完整的信源信息', 'error');
        return;
    }

    const newSource = {
        id: 'custom_' + Date.now(),
        name,
        url,
        type: 'custom',
        language: 'zh',
        enabled: true,
        priority: config.sources.length + 1,
        auth: null,
        lastFetch: null,
        todayCount: 0
    };

    config.sources.push(newSource);
    renderSources();
    closeModal('addSourceModal');
    showToast(`信源"${name}"已添加`, 'success');
}

// 工具函数
function generateId() {
    return 'news_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function formatDate(dateStr) {
    if (!dateStr) return '--';
    const date = new Date(dateStr);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

function formatDateTime(isoStr) {
    if (!isoStr) return '--';
    const date = new Date(isoStr);
    return `${formatDate(isoStr)} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getImportanceClass(importance) {
    switch (importance) {
        case '高': return 'high';
        case '中': return 'medium';
        case '低': return 'low';
        default: return 'medium';
    }
}

function convertToCSV(data) {
    const headers = ['日期', '标题', '媒体来源', '摘要', '涉及国家/地区', '主题分类', '关键词', '出处链接', '重要程度'];
    const rows = data.map(item => [
        item.date,
        `"${(item.title || '').replace(/"/g, '""')}"`,
        item.source,
        `"${(item.summary || '').replace(/"/g, '""')}"`,
        (item.countries || []).join(';'),
        item.category,
        (item.keywords || []).join(';'),
        item.url,
        item.importance
    ].join(','));

    return '\uFEFF' + headers.join(',') + '\n' + rows.join('\n'); // BOM for Excel compatibility
}

function downloadFile(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// 点击模态框外部关闭
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
});

// 键盘快捷键
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }
});
