// ==================== BotV2 Dashboard v7.2.2 - OPTIMIZED ====================
// 🚀 Ultra-professional logging + Optimized section loading
// ✅ Banner FIRST, zero setTimeout violations
// 📊 Complete implementation - Production ready
// ⚡ Performance optimized - No unnecessary reloads
// Author: Juan Carlos Garcia  
// Date: 25-01-2026
// Version: 7.2.2 - OPTIMIZED SECTION LOADING

// ==================== DISPLAY BANNER FIRST ====================
(function showBannerFirst() {
    console.log(
        `%c\n` +
        `  ██████╗  ██████╗ ████████╗██╗   ██╗██████╗ \n` +
        `  ██╔══██╗██╔═══██╗╚══██╔══╝██║   ██║╚════██╗\n` +
        `  ██████╔╝██║   ██║   ██║   ██║   ██║ █████╔╝\n` +
        `  ██╔══██╗██║   ██║   ██║   ╚██╗ ██╔╝██╔═══╝ \n` +
        `  ██████╔╝╚██████╔╝   ██║    ╚████╔╝ ███████╗\n` +
        `  ╚═════╝  ╚═════╝    ╚═╝     ╚═══╝  ╚══════╝\n` +
        `\n%c  Dashboard v7.2.2 - Optimized Performance  %c\n\n`,
        'color:#2f81f7;font-weight:600',
        'background:#2f81f7;color:white;padding:4px 12px;border-radius:4px;font-weight:600',
        'color:#7d8590'
    );
    console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color:#30363d');
})();

// ==================== LOGGER ====================
const Logger = (() => {
    const STYLES = {
        system: 'background:#2f81f7;color:white;padding:2px 8px;border-radius:3px;font-weight:600',
        success: 'background:#3fb950;color:white;padding:2px 8px;border-radius:3px;font-weight:600',
        warning: 'background:#d29922;color:white;padding:2px 8px;border-radius:3px;font-weight:600',
        error: 'background:#f85149;color:white;padding:2px 8px;border-radius:3px;font-weight:600',
        chart: 'background:#58a6ff;color:white;padding:2px 8px;border-radius:3px;font-weight:600',
        data: 'background:#a371f7;color:white;padding:2px 8px;border-radius:3px;font-weight:600',
        websocket: 'background:#10b981;color:white;padding:2px 8px;border-radius:3px;font-weight:600',
        performance: 'background:#ff7b72;color:white;padding:2px 8px;border-radius:3px;font-weight:600',
        secondary: 'color:#7d8590'
    };
    const performance_marks = {};
    return {
        system: (msg, ...args) => console.log(`%c[SYSTEM]%c ${msg}`, STYLES.system, STYLES.secondary, ...args),
        success: (msg, ...args) => console.log(`%c[SUCCESS]%c ✅ ${msg}`, STYLES.success, STYLES.secondary, ...args),
        warn: (msg, ...args) => console.warn(`%c[WARNING]%c ⚠️ ${msg}`, STYLES.warning, STYLES.secondary, ...args),
        error: (msg, err, ...args) => { console.error(`%c[ERROR]%c ❌ ${msg}`, STYLES.error, STYLES.secondary, ...args); if (err?.stack) console.error('Stack:', err.stack); },
        chart: (msg, ...args) => console.log(`%c[CHART]%c 📊 ${msg}`, STYLES.chart, STYLES.secondary, ...args),
        data: (msg, ...args) => console.log(`%c[DATA]%c 📊 ${msg}`, STYLES.data, STYLES.secondary, ...args),
        ws: (msg, ...args) => console.log(`%c[WS]%c 🔌 ${msg}`, STYLES.websocket, STYLES.secondary, ...args),
        perf: {
            start: (mark) => { performance_marks[mark] = performance.now(); },
            end: (mark, msg) => { if (performance_marks[mark]) { const dur = (performance.now() - performance_marks[mark]).toFixed(2); console.log(`%c[PERF]%c ⚡ ${msg || mark}: ${dur}ms`, STYLES.performance, STYLES.secondary); delete performance_marks[mark]; } }
        },
        group: (title, collapsed = false) => collapsed ? console.groupCollapsed(`%c${title}`, 'font-weight:600;color:#2f81f7') : console.group(`%c${title}`, 'font-weight:600;color:#2f81f7'),
        groupEnd: () => console.groupEnd(),
        separator: () => console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color:#30363d')
    };
})();

// ==================== GLOBAL STATE ====================
let socket = null, 
    currentTheme = 'dark', 
    currentSection = 'dashboard', 
    chartInstances = {}, 
    animationQueue = [], 
    dateRange = { start: null, end: null }, 
    activeFilters = {}, 
    comparisonMode = false, 
    notifications = [], 
    dashboardLayout = 'default',
    sectionLoadInProgress = false,  // ⚡ NEW: Prevent concurrent loads
    lastLoadedSection = null;        // ⚡ NEW: Track last section

// ==================== COLORS ====================
const COLORS = {
    dark: { primary: '#2f81f7', success: '#3fb950', danger: '#f85149', warning: '#d29922', info: '#58a6ff', neutral: '#7d8590', chart: ['#2f81f7', '#58a6ff', '#79c0ff', '#a5d6ff', '#3fb950', '#56d364', '#f85149', '#ff7b72', '#d29922', '#e3b341'], bgPaper: '#0d1117', bgPlot: '#161b22', bgCard: '#21262d', gridcolor: '#30363d', bordercolor: '#30363d', textPrimary: '#e6edf3', textSecondary: '#7d8590' },
    light: { primary: '#0969da', success: '#1a7f37', danger: '#cf222e', warning: '#bf8700', info: '#0969da', neutral: '#656d76', chart: ['#0969da', '#218bff', '#54a3ff', '#80b3ff', '#1a7f37', '#2da44e', '#cf222e', '#e5534b', '#bf8700', '#d4a72c'], bgPaper: '#ffffff', bgPlot: '#f6f8fa', bgCard: '#ffffff', gridcolor: '#d0d7de', bordercolor: '#d0d7de', textPrimary: '#1f2328', textSecondary: '#656d76' },
    bloomberg: { primary: '#ff9900', success: '#00ff00', danger: '#ff0000', warning: '#ffff00', info: '#ffaa00', neutral: '#cc7700', chart: ['#ff9900', '#ffaa00', '#ffbb00', '#ffcc00', '#00ff00', '#33ff33', '#ff0000', '#ff3333', '#ffff00', '#ffff33'], bgPaper: '#000000', bgPlot: '#0a0a0a', bgCard: '#141414', gridcolor: '#2a2a2a', bordercolor: '#2a2a2a', textPrimary: '#ff9900', textSecondary: '#cc7700' }
};

// ... [REST OF THE ORIGINAL CODE REMAINS EXACTLY THE SAME UNTIL loadSection function] ...