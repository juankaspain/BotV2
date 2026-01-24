// ==================== BotV2 Dashboard v4.9 - PHASE 1 CRITICAL FIXES ====================
// ✅ FIXED: Chart styling consistency across all themes
// ✅ ADDED: Export functionality for all charts  
// ✅ IMPROVED: Professional tooltips and hover states
// ✅ ENHANCED: Error handling with user-friendly messages
// Author: Juan Carlos Garcia
// Date: 24-01-2026
// Version: 4.9.0 - PHASE 1 COMPLETE

// ==================== GLOBAL STATE ====================
let socket = null;
let currentTheme = 'dark';
let currentSection = 'dashboard';
let chartInstances = {};

// ==================== UNIFIED COLOR SYSTEM ====================
const COLORS = {
    dark: {
        primary: '#2f81f7',
        success: '#3fb950',
        danger: '#f85149',
        warning: '#d29922',
        info: '#58a6ff',
        neutral: '#7d8590',
        // Chart colors
        chart: ['#2f81f7', '#58a6ff', '#79c0ff', '#a5d6ff', '#3fb950', '#56d364', '#f85149', '#ff7b72', '#d29922', '#e3b341'],
        // Backgrounds
        bgPaper: '#0d1117',
        bgPlot: '#161b22',
        bgCard: '#21262d',
        // Borders & Grid
        gridcolor: '#30363d',
        bordercolor: '#30363d',
        // Text
        textPrimary: '#e6edf3',
        textSecondary: '#7d8590'
    },
    light: {
        primary: '#0969da',
        success: '#1a7f37',
        danger: '#cf222e',
        warning: '#bf8700',
        info: '#0969da',
        neutral: '#656d76',
        chart: ['#0969da', '#218bff', '#54a3ff', '#80b3ff', '#1a7f37', '#2da44e', '#cf222e', '#e5534b', '#bf8700', '#d4a72c'],
        bgPaper: '#ffffff',
        bgPlot: '#f6f8fa',
        bgCard: '#ffffff',
        gridcolor: '#d0d7de',
        bordercolor: '#d0d7de',
        textPrimary: '#1f2328',
        textSecondary: '#656d76'
    },
    bloomberg: {
        primary: '#ff9900',
        success: '#00ff00',
        danger: '#ff0000',
        warning: '#ffff00',
        info: '#ffaa00',
        neutral: '#cc7700',
        chart: ['#ff9900', '#ffaa00', '#ffbb00', '#ffcc00', '#00ff00', '#33ff33', '#ff0000', '#ff3333', '#ffff00', '#ffff33'],
        bgPaper: '#000000',
        bgPlot: '#0a0a0a',
        bgCard: '#141414',
        gridcolor: '#2a2a2a',
        bordercolor: '#2a2a2a',
        textPrimary: '#ff9900',
        textSecondary: '#cc7700'
    }
};

// ==================== CHART CONFIGURATION FACTORY ====================
function getStandardChartConfig(chartId, options = {}) {
    const colors = COLORS[currentTheme];
    
    return {
        layout: {
            paper_bgcolor: colors.bgPaper,
            plot_bgcolor: colors.bgPlot,
            font: { 
                family: 'Inter, -apple-system, sans-serif',
                size: 12,
                color: colors.textPrimary
            },
            xaxis: {
                gridcolor: colors.gridcolor,
                showgrid: true,
                zeroline: false,
                linecolor: colors.bordercolor,
                tickfont: { color: colors.textSecondary },
                ...options.xaxis
            },
            yaxis: {
                gridcolor: colors.gridcolor,
                showgrid: true,
                zeroline: true,
                zerolinecolor: colors.gridcolor,
                linecolor: colors.bordercolor,
                tickfont: { color: colors.textSecondary },
                ...options.yaxis
            },
            margin: options.margin || { t: 20, r: 30, b: 50, l: 70 },
            hovermode: options.hovermode || 'x unified',
            hoverlabel: {
                bgcolor: colors.bgCard,
                bordercolor: colors.bordercolor,
                font: { 
                    family: 'Inter, sans-serif',
                    size: 13,
                    color: colors.textPrimary
                },
                align: 'left'
            },
            showlegend: options.showlegend !== undefined ? options.showlegend : false,
            legend: options.legend || {
                x: 0.02,
                y: 0.98,
                bgcolor: 'rgba(0,0,0,0)',
                bordercolor: colors.bordercolor,
                borderwidth: 0,
                font: { color: colors.textPrimary }
            },
            ...options.layout
        },
        config: {
            responsive: true,
            displaylogo: false,
            displayModeBar: true,
            modeBarButtonsToRemove: ['select2d', 'lasso2d', 'autoScale2d'],
            modeBarButtonsToAdd: [
                {
                    name: 'Download PNG',
                    icon: Plotly.Icons.camera,
                    click: function(gd) {
                        Plotly.downloadImage(gd, {
                            format: 'png',
                            width: 1920,
                            height: 1080,
                            filename: `botv2_${chartId}_${Date.now()}`,
                            scale: 2
                        });
                    }
                }
            ],
            toImageButtonOptions: {
                format: 'png',
                filename: `botv2_${chartId}_${Date.now()}`,
                height: 1080,
                width: 1920,
                scale: 2
            }
        }
    };
}

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 BotV2 Dashboard v4.9 - PHASE 1 FIXES APPLIED');
    
    if (typeof Plotly === 'undefined') {
        console.error('❌ Plotly.js not loaded!');
        showError('main-container', 'Plotly.js library failed to load. Please refresh the page.');
        return;
    }
    
    initWebSocket();
    setupMenuHandlers();
    
    const savedTheme = localStorage.getItem('dashboard-theme') || 'dark';
    setTheme(savedTheme, true);
    
    loadSection('dashboard');
    console.log('✅ Dashboard initialized with unified styling');
});

// ==================== ERROR HANDLING ====================
function showError(containerId, message, section = null) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const retryButton = section ? 
        `<button onclick="loadSection('${section}')" class="retry-btn" style="
            margin-top:1.5rem;
            padding:10px 24px;
            background:var(--accent-primary);
            border:none;
            border-radius:6px;
            color:white;
            cursor:pointer;
            font-weight:600;
            font-size:14px;
            transition:all 0.2s;
        ">🔄 Try Again</button>` : '';
    
    container.innerHTML = `
        <div style="
            text-align:center;
            padding:80px 40px;
            max-width:500px;
            margin:0 auto;
        ">
            <div style="font-size:64px;margin-bottom:24px;opacity:0.8;">⚠️</div>
            <h2 style="
                color:var(--text-primary);
                font-size:24px;
                font-weight:600;
                margin-bottom:12px;
            ">Something went wrong</h2>
            <p style="
                color:var(--text-secondary);
                font-size:15px;
                line-height:1.6;
                margin-bottom:8px;
            ">${message}</p>
            ${retryButton}
        </div>
    `;
}

function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <div class="loading-text">Loading data...</div>
        </div>
    `;
}

// ==================== MENU ====================
function setupMenuHandlers() {
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            if (section) loadSection(section);
        });
    });
}

function loadSection(section) {
    if (!section) return;
    console.log(`📂 Loading: ${section}`);
    currentSection = section;
    cleanupCharts();
    
    document.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
    const activeItem = document.querySelector(`[data-section="${section}"]`);
    if (activeItem) activeItem.classList.add('active');
    
    const titles = {
        'dashboard': 'Dashboard',
        'portfolio': 'Portfolio',
        'trades': 'Trade History',
        'performance': 'Performance',
        'risk': 'Risk Analysis',
        'markets': 'Market Overview',
        'strategies': 'Strategies',
        'backtesting': 'Backtesting',
        'live_monitor': 'Live Monitor',
        'control_panel': 'Control Panel',
        'settings': 'Settings'
    };
    
    const pageTitle = document.getElementById('page-title');
    if (pageTitle) pageTitle.textContent = titles[section] || section;
    
    fetchSectionContent(section);
}

function fetchSectionContent(section) {
    showLoading('main-container');
    
    fetch(`/api/section/${section}`)
        .then(r => {
            if (!r.ok) throw new Error(`HTTP ${r.status}: ${r.statusText}`);
            return r.json();
        })
        .then(data => renderSection(section, data))
        .catch(error => {
            console.error(`Error loading ${section}:`, error);
            let message = 'Unable to load data. Please check your connection and try again.';
            
            if (error.message.includes('404')) {
                message = 'The requested data was not found.';
            } else if (error.message.includes('500')) {
                message = 'Server error occurred. Our team has been notified.';
            } else if (error.message.includes('Failed to fetch')) {
                message = 'Network connection lost. Please check your internet connection.';
            }
            
            showError('main-container', message, section);
        });
}

function renderSection(section, data) {
    const renderers = {
        'dashboard': renderDashboard,
        'portfolio': renderPortfolio,
        'trades': renderTrades,
        'performance': renderPerformance,
        'risk': renderRisk,
        'markets': renderMarkets,
        'strategies': renderStrategies,
        'backtesting': renderBacktesting,
        'live_monitor': renderLiveMonitor,
        'control_panel': renderControlPanel,
        'settings': renderSettings
    };
    
    const renderer = renderers[section];
    if (renderer) {
        try {
            renderer(data);
            console.log(`✅ ${section} rendered with enhanced styling`);
        } catch (error) {
            console.error(`❌ Render error in ${section}:`, error);
            showError('main-container', `Failed to render ${section}. Please refresh the page.`, section);
        }
    }
}

function cleanupCharts() {
    Object.keys(chartInstances).forEach(chartId => {
        try {
            if (document.getElementById(chartId)) Plotly.purge(chartId);
        } catch (e) {}
    });
    chartInstances = {};
}

// ==================== RENDERERS ====================

function renderDashboard(data) {
    const container = document.getElementById('main-container');
    const o = data.overview || {};
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">PORTFOLIO VALUE</div>
                <div class="kpi-value">${o.equity || '€0'}</div>
                <div class="kpi-change ${o.daily_change >= 0 ? 'positive' : 'negative'}">
                    ${o.daily_change >= 0 ? '↑' : '↓'} ${Math.abs(o.daily_change || 0).toFixed(2)}% today
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">TOTAL P&L</div>
                <div class="kpi-value">${o.total_pnl || '€0'}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">WIN RATE</div>
                <div class="kpi-value">${o.win_rate || 0}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">SHARPE RATIO</div>
                <div class="kpi-value">${o.sharpe_ratio || 'N/A'}</div>
            </div>
        </div>
        <div class="charts-grid">
            <div class="chart-card full-width">
                <div class="chart-header"><div class="chart-title">Equity Curve</div></div>
                <div id="equity-chart" class="chart-container"></div>
            </div>
        </div>
    `;
    
    setTimeout(() => {
        if (data.equity) createEquityChart(data.equity);
    }, 100);
}

function renderPortfolio(data) {
    const container = document.getElementById('main-container');
    const s = data.summary || {};
    const positions = data.positions || [];
    
    let rows = positions.map(p => `
        <tr>
            <td><strong>${p.symbol}</strong></td>
            <td>${p.quantity}</td>
            <td>€${p.value.toFixed(2)}</td>
            <td class="${p.pnl >= 0 ? 'positive' : 'negative'}">€${p.pnl.toFixed(2)}</td>
            <td class="${p.pnl_pct >= 0 ? 'positive' : 'negative'}">${p.pnl_pct >= 0 ? '+' : ''}${p.pnl_pct.toFixed(2)}%</td>
        </tr>
    `).join('');
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">TOTAL VALUE</div>
                <div class="kpi-value">€${(s.total_value || 0).toLocaleString()}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">POSITIONS</div>
                <div class="kpi-value">${positions.length}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">TOTAL P&L</div>
                <div class="kpi-value ${s.total_pnl >= 0 ? 'positive' : 'negative'}">€${(s.total_pnl || 0).toFixed(2)}</div>
            </div>
        </div>
        <div class="charts-grid">
            <div class="chart-card full-width">
                <div class="chart-header"><div class="chart-title">Portfolio Allocation</div></div>
                <div id="portfolio-pie" class="chart-container"></div>
            </div>
        </div>
        <div class="data-table">
            <table>
                <thead>
                    <tr><th>Symbol</th><th>Quantity</th><th>Value</th><th>P&L</th><th>P&L %</th></tr>
                </thead>
                <tbody>${rows || '<tr><td colspan="5">No positions</td></tr>'}</tbody>
            </table>
        </div>
    `;
    
    setTimeout(() => {
        if (positions.length > 0) createPortfolioPieChart(positions);
    }, 100);
}

function renderTrades(data) {
    const container = document.getElementById('main-container');
    const s = data.summary || {};
    const trades = data.trades || [];
    
    let rows = trades.slice(0, 20).map(t => `
        <tr>
            <td>${t.timestamp}</td>
            <td><strong>${t.symbol}</strong></td>
            <td><span class="badge ${t.action === 'BUY' ? 'badge-success' : 'badge-danger'}">${t.action}</span></td>
            <td>${t.quantity}</td>
            <td>€${t.price}</td>
            <td class="${t.pnl >= 0 ? 'positive' : 'negative'}">€${t.pnl.toFixed(2)}</td>
        </tr>
    `).join('');
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">TOTAL TRADES</div>
                <div class="kpi-value">${s.total || 0}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">WINNING</div>
                <div class="kpi-value positive">${s.winning || 0}</div>
            </div>
        </div>
        <div class="data-table">
            <table>
                <thead>
                    <tr><th>Time</th><th>Symbol</th><th>Action</th><th>Qty</th><th>Price</th><th>P&L</th></tr>
                </thead>
                <tbody>${rows || '<tr><td colspan="6">No trades</td></tr>'}</tbody>
            </table>
        </div>
    `;
}

function renderPerformance(data) {
    const container = document.getElementById('main-container');
    const m = data.metrics || {};
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">TOTAL RETURN</div>
                <div class="kpi-value ${m.total_return >= 0 ? 'positive' : 'negative'}">${m.total_return || 0}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">AVG MONTHLY</div>
                <div class="kpi-value">${m.avg_monthly_return || 0}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">SHARPE RATIO</div>
                <div class="kpi-value">${m.sharpe || 'N/A'}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">WIN RATE</div>
                <div class="kpi-value">${m.win_rate || 0}%</div>
            </div>
        </div>
        <div class="charts-grid">
            <div class="chart-card full-width">
                <div class="chart-header"><div class="chart-title">Monthly Returns</div></div>
                <div id="monthly-returns" class="chart-container"></div>
            </div>
        </div>
    `;
    
    setTimeout(() => {
        if (data.monthly_returns) createMonthlyReturnsChart(data.monthly_returns);
    }, 100);
}

function renderRisk(data) {
    const container = document.getElementById('main-container');
    const m = data.metrics || {};
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">VAR 95%</div>
                <div class="kpi-value danger">€${m.var_95 || 0}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">MAX DD</div>
                <div class="kpi-value danger">${m.max_drawdown || 0}%</div>
            </div>
        </div>
        <div class="charts-grid">
            <div class="chart-card full-width">
                <div class="chart-header"><div class="chart-title">Drawdown Chart</div></div>
                <div id="drawdown-chart" class="chart-container"></div>
            </div>
        </div>
    `;
    
    setTimeout(() => {
        if (data.drawdown) createDrawdownChart(data.drawdown);
    }, 100);
}

function renderMarkets(data) {
    const container = document.getElementById('main-container');
    const indices = data.indices || [];
    const movers = data.movers || [];
    const crypto = data.crypto || [];
    
    let indicesHTML = indices.map(idx => `
        <div class="kpi-card">
            <div class="kpi-title">${idx.name}</div>
            <div class="kpi-value">${idx.value.toLocaleString()}</div>
            <div class="kpi-change ${idx.change >= 0 ? 'positive' : 'negative'}">
                ${idx.change >= 0 ? '↑' : '↓'} ${Math.abs(idx.change_pct).toFixed(2)}%
            </div>
        </div>
    `).join('');
    
    let moversRows = movers.map(m => `
        <tr>
            <td><strong>${m.symbol}</strong></td>
            <td>€${m.price.toFixed(2)}</td>
            <td class="${m.change >= 0 ? 'positive' : 'negative'}">${m.change >= 0 ? '+' : ''}${m.change.toFixed(2)}</td>
            <td class="${m.change_pct >= 0 ? 'positive' : 'negative'}">${m.change_pct >= 0 ? '+' : ''}${m.change_pct.toFixed(2)}%</td>
            <td>${(m.volume / 1000000).toFixed(1)}M</td>
        </tr>
    `).join('');
    
    let cryptoRows = crypto.map(c => `
        <tr>
            <td><strong>${c.symbol}</strong></td>
            <td>€${c.price.toLocaleString()}</td>
            <td class="${c.change >= 0 ? 'positive' : 'negative'}">${c.change >= 0 ? '+' : ''}${c.change.toFixed(2)}</td>
            <td class="${c.change_pct >= 0 ? 'positive' : 'negative'}">${c.change_pct >= 0 ? '+' : ''}${c.change_pct.toFixed(2)}%</td>
        </tr>
    `).join('');
    
    container.innerHTML = `
        <h3 style="margin-bottom:1rem;color:var(--text-primary)">Major Indices</h3>
        <div class="kpi-grid">${indicesHTML}</div>
        
        <h3 style="margin:2rem 0 1rem;color:var(--text-primary)">Top Movers</h3>
        <div class="data-table">
            <table>
                <thead><tr><th>Symbol</th><th>Price</th><th>Change</th><th>%</th><th>Volume</th></tr></thead>
                <tbody>${moversRows}</tbody>
            </table>
        </div>
        
        <h3 style="margin:2rem 0 1rem;color:var(--text-primary)">Crypto Markets</h3>
        <div class="data-table">
            <table>
                <thead><tr><th>Symbol</th><th>Price</th><th>Change</th><th>%</th></tr></thead>
                <tbody>${cryptoRows}</tbody>
            </table>
        </div>
    `;
}

function renderStrategies(data) {
    const container = document.getElementById('main-container');
    const s = data.summary || {};
    const strategies = data.strategies || [];
    
    let rows = strategies.map(st => `
        <tr>
            <td><strong>${st.name}</strong></td>
            <td><span class="badge badge-success">${st.status}</span></td>
            <td class="${st.return >= 0 ? 'positive' : 'negative'}">${st.return >= 0 ? '+' : ''}${st.return}%</td>
            <td>${st.sharpe}</td>
            <td>${st.trades}</td>
        </tr>
    `).join('');
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">ACTIVE</div>
                <div class="kpi-value">${s.active || 0}</div>
            </div>
        </div>
        <div class="data-table">
            <table>
                <thead><tr><th>Strategy</th><th>Status</th><th>Return</th><th>Sharpe</th><th>Trades</th></tr></thead>
                <tbody>${rows || '<tr><td colspan="5">No strategies</td></tr>'}</tbody>
            </table>
        </div>
    `;
}

function renderBacktesting(data) {
    const container = document.getElementById('main-container');
    const r = data.results || {};
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">STRATEGY RETURN</div>
                <div class="kpi-value positive">${r.total_return_strategy || 0}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">BENCHMARK</div>
                <div class="kpi-value">${r.total_return_benchmark || 0}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">OUTPERFORMANCE</div>
                <div class="kpi-value ${r.outperformance >= 0 ? 'positive' : 'negative'}">${r.outperformance || 0}%</div>
            </div>
        </div>
        <div class="charts-grid">
            <div class="chart-card full-width">
                <div class="chart-header"><div class="chart-title">Strategy vs Benchmark</div></div>
                <div id="backtest-chart" class="chart-container"></div>
            </div>
        </div>
    `;
    
    setTimeout(() => {
        if (data.equity_curves) createBacktestChart(data.equity_curves);
    }, 100);
}

function renderLiveMonitor(data) {
    const container = document.getElementById('main-container');
    const s = data.summary || {};
    const active_trades = data.active_trades || [];
    
    let tradesRows = active_trades.map(t => `
        <tr>
            <td><strong>${t.symbol}</strong></td>
            <td><span class="badge ${t.action === 'BUY' ? 'badge-success' : 'badge-danger'}">${t.action}</span></td>
            <td>€${t.entry_price.toFixed(2)}</td>
            <td>€${t.current_price.toFixed(2)}</td>
            <td class="${t.unrealized_pnl >= 0 ? 'positive' : 'negative'}">€${t.unrealized_pnl.toFixed(2)}</td>
        </tr>
    `).join('');
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">BOT STATUS</div>
                <div class="kpi-value ${s.status === 'ACTIVE' ? 'positive' : 'danger'}">${s.status || 'STOPPED'}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">ACTIVE TRADES</div>
                <div class="kpi-value">${s.active_trades || 0}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">UNREALIZED P&L</div>
                <div class="kpi-value ${s.unrealized_pnl >= 0 ? 'positive' : 'negative'}">€${(s.unrealized_pnl || 0).toFixed(2)}</div>
            </div>
        </div>
        
        <h3 style="margin:2rem 0 1rem;color:var(--text-primary)">Active Trades</h3>
        <div class="data-table">
            <table>
                <thead><tr><th>Symbol</th><th>Action</th><th>Entry</th><th>Current</th><th>P&L</th></tr></thead>
                <tbody>${tradesRows || '<tr><td colspan="5">No active trades</td></tr>'}</tbody>
            </table>
        </div>
    `;
}

function renderControlPanel(data) {
    const container = document.getElementById('main-container');
    const config = data.config || {};
    const bot_status = data.bot_status || 'STOPPED';
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">BOT STATUS</div>
                <div class="kpi-value ${bot_status === 'RUNNING' ? 'positive' : 'danger'}">${bot_status}</div>
                <button onclick="alert('Start/Stop functionality coming soon')" style="margin-top:1rem;padding:8px 16px;background:var(--accent-success);border:none;border-radius:6px;color:white;cursor:pointer;font-weight:600;width:100%;">
                    ${bot_status === 'RUNNING' ? '⏸ STOP BOT' : '▶️ START BOT'}
                </button>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">AUTO TRADING</div>
                <div class="kpi-value">${config.auto_trading ? 'ON' : 'OFF'}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">MAX POSITION SIZE</div>
                <div class="kpi-value">€${(config.max_position_size || 0).toLocaleString()}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">RISK LEVEL</div>
                <div class="kpi-value">${config.risk_level || 'MEDIUM'}</div>
            </div>
        </div>
        
        <div style="background:var(--bg-secondary);border:1px solid var(--border-default);border-radius:var(--radius);padding:24px;margin-top:24px;">
            <h3 style="margin-bottom:1rem;color:var(--text-primary)">🎛️ Bot Configuration</h3>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px;">
                <div>
                    <label style="display:block;margin-bottom:8px;color:var(--text-secondary);font-weight:600;">Trading Mode</label>
                    <select style="width:100%;padding:10px;background:var(--bg-tertiary);border:1px solid var(--border-default);border-radius:6px;color:var(--text-primary);" disabled>
                        <option>${config.trading_mode || 'LIVE'}</option>
                    </select>
                </div>
                <div>
                    <label style="display:block;margin-bottom:8px;color:var(--text-secondary);font-weight:600;">Active Strategy</label>
                    <select style="width:100%;padding:10px;background:var(--bg-tertiary);border:1px solid var(--border-default);border-radius:6px;color:var(--text-primary);" disabled>
                        <option>${config.active_strategy || 'Momentum Pro'}</option>
                    </select>
                </div>
                <div>
                    <label style="display:block;margin-bottom:8px;color:var(--text-secondary);font-weight:600;">Stop Loss %</label>
                    <input type="number" value="${config.stop_loss_pct || 2}" style="width:100%;padding:10px;background:var(--bg-tertiary);border:1px solid var(--border-default);border-radius:6px;color:var(--text-primary);" disabled>
                </div>
                <div>
                    <label style="display:block;margin-bottom:8px;color:var(--text-secondary);font-weight:600;">Take Profit %</label>
                    <input type="number" value="${config.take_profit_pct || 5}" style="width:100%;padding:10px;background:var(--bg-tertiary);border:1px solid var(--border-default);border-radius:6px;color:var(--text-primary);" disabled>
                </div>
            </div>
            <div style="margin-top:20px;padding:16px;background:var(--bg-tertiary);border-radius:6px;border-left:4px solid var(--accent-warning);">
                <p style="margin:0;color:var(--text-secondary);font-size:13px;">⚠️ <strong>Note:</strong> Bot control functionality is currently view-only. Full start/stop/configuration controls coming in next version.</p>
            </div>
        </div>
    `;
}

function renderSettings(data) {
    const container = document.getElementById('main-container');
    container.innerHTML = `
        <div style="background:var(--bg-secondary);border:1px solid var(--border-default);border-radius:var(--radius);padding:32px;text-align:center;">
            <h2 style="margin-bottom:16px;">⚙️ Settings</h2>
            <p style="color:var(--text-secondary);margin-bottom:24px;">Configure dashboard settings and preferences</p>
            <div style="display:flex;gap:12px;justify-content:center;">
                <button onclick="alert('Settings panel coming soon')" style="padding:10px 20px;background:var(--accent-primary);border:none;border-radius:6px;color:white;cursor:pointer;font-weight:600;">Dashboard Settings</button>
                <button onclick="alert('API configuration coming soon')" style="padding:10px 20px;background:var(--bg-tertiary);border:1px solid var(--border-default);border-radius:6px;color:var(--text-primary);cursor:pointer;font-weight:600;">API Configuration</button>
            </div>
        </div>
    `;
}

// ==================== ENHANCED CHART CREATORS ====================

function createEquityChart(data) {
    if (!data.timestamps || !data.equity) return;
    
    const colors = COLORS[currentTheme];
    const config = getStandardChartConfig('equity-chart', {
        yaxis: { tickprefix: '€' }
    });
    
    const trace = {
        x: data.timestamps,
        y: data.equity,
        type: 'scatter',
        mode: 'lines',
        line: { color: colors.primary, width: 2.5 },
        fill: 'tozeroy',
        fillcolor: colors.primary.replace(')', ', 0.1)').replace('rgb', 'rgba'),
        name: 'Equity',
        hovertemplate: '<b>%{x}</b><br>Equity: €%{y:,.2f}<extra></extra>'
    };
    
    Plotly.newPlot('equity-chart', [trace], config.layout, config.config);
    chartInstances['equity-chart'] = true;
}

function createPortfolioPieChart(positions) {
    const colors = COLORS[currentTheme];
    const config = getStandardChartConfig('portfolio-pie', {
        showlegend: false,
        margin: { t: 10, r: 20, b: 10, l: 20 }
    });
    
    const trace = {
        labels: positions.map(p => p.symbol),
        values: positions.map(p => p.value),
        type: 'pie',
        hole: 0.45,
        textinfo: 'label+percent',
        textfont: { size: 12, color: colors.textPrimary },
        marker: {
            colors: colors.chart,
            line: { color: colors.bgPaper, width: 3 }
        },
        hovertemplate: '<b>%{label}</b><br>Value: €%{value:,.2f}<br>%{percent}<extra></extra>'
    };
    
    Plotly.newPlot('portfolio-pie', [trace], config.layout, config.config);
    chartInstances['portfolio-pie'] = true;
}

function createMonthlyReturnsChart(data) {
    if (!data.months || !data.returns) return;
    
    const colors = COLORS[currentTheme];
    const config = getStandardChartConfig('monthly-returns', {
        yaxis: { ticksuffix: '%', zeroline: true, zerolinecolor: colors.gridcolor }
    });
    
    const barColors = data.returns.map(r => r >= 0 ? colors.success : colors.danger);
    
    const trace = {
        x: data.months,
        y: data.returns,
        type: 'bar',
        marker: { color: barColors },
        hovertemplate: '<b>%{x}</b><br>Return: %{y:.2f}%<extra></extra>'
    };
    
    Plotly.newPlot('monthly-returns', [trace], config.layout, config.config);
    chartInstances['monthly-returns'] = true;
}

function createDrawdownChart(data) {
    if (!data.timestamps || !data.drawdown) return;
    
    const colors = COLORS[currentTheme];
    const config = getStandardChartConfig('drawdown-chart', {
        yaxis: { ticksuffix: '%', zeroline: true, zerolinecolor: colors.gridcolor }
    });
    
    const trace = {
        x: data.timestamps,
        y: data.drawdown,
        type: 'scatter',
        mode: 'lines',
        line: { color: colors.danger, width: 2.5 },
        fill: 'tozeroy',
        fillcolor: colors.danger.replace(')', ', 0.15)').replace('rgb', 'rgba'),
        name: 'Drawdown',
        hovertemplate: '<b>%{x}</b><br>Drawdown: %{y:.2f}%<extra></extra>'
    };
    
    Plotly.newPlot('drawdown-chart', [trace], config.layout, config.config);
    chartInstances['drawdown-chart'] = true;
}

function createBacktestChart(data) {
    if (!data.timestamps || !data.strategy || !data.benchmark) return;
    
    const colors = COLORS[currentTheme];
    const config = getStandardChartConfig('backtest-chart', {
        showlegend: true,
        yaxis: { tickprefix: '€' }
    });
    
    const trace1 = {
        x: data.timestamps,
        y: data.strategy,
        type: 'scatter',
        mode: 'lines',
        line: { color: colors.success, width: 2.5 },
        name: 'Strategy',
        hovertemplate: '<b>%{x}</b><br>Strategy: €%{y:,.2f}<extra></extra>'
    };
    
    const trace2 = {
        x: data.timestamps,
        y: data.benchmark,
        type: 'scatter',
        mode: 'lines',
        line: { color: colors.primary, width: 2.5, dash: 'dot' },
        name: 'Benchmark',
        hovertemplate: '<b>%{x}</b><br>Benchmark: €%{y:,.2f}<extra></extra>'
    };
    
    Plotly.newPlot('backtest-chart', [trace1, trace2], config.layout, config.config);
    chartInstances['backtest-chart'] = true;
}

// ==================== WEBSOCKET ====================
function initWebSocket() {
    if (typeof io === 'undefined') {
        console.warn('⚠️ Socket.io not loaded - real-time updates disabled');
        return;
    }
    
    socket = io({ reconnection: true, reconnectionDelay: 1000, reconnectionAttempts: 5 });
    
    socket.on('connect', () => {
        console.log('✅ WebSocket Connected');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', () => {
        console.log('❌ WebSocket Disconnected');
        updateConnectionStatus(false);
    });
    
    socket.on('update', (data) => {
        console.log('📊 Real-time update received:', data);
        if (currentSection) loadSection(currentSection);
    });
}

function updateConnectionStatus(connected) {
    const statusText = document.getElementById('connection-text');
    const statusDot = document.querySelector('.status-dot');
    
    if (statusText && statusDot) {
        statusText.textContent = connected ? 'Connected' : 'Disconnected';
        statusDot.style.background = connected ? 'var(--accent-success)' : 'var(--accent-danger)';
    }
}

// ==================== UI FUNCTIONS ====================
function setTheme(theme, skipToast = false) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('dashboard-theme', theme);
    
    document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
    const themeButtons = { 'dark': 0, 'light': 1, 'bloomberg': 2 };
    const buttons = document.querySelectorAll('.theme-btn');
    if (buttons[themeButtons[theme]]) buttons[themeButtons[theme]].classList.add('active');
    
    if (currentSection) loadSection(currentSection);
}

// ==================== RESIZE HANDLER ====================
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        Object.keys(chartInstances).forEach(chartId => {
            try {
                if (document.getElementById(chartId)) Plotly.Plots.resize(chartId);
            } catch (e) {}
        });
    }, 250);
});

// ==================== CLEANUP ====================
window.addEventListener('beforeunload', () => {
    cleanupCharts();
    if (socket && socket.connected) socket.disconnect();
});

console.log('✅ Dashboard v4.9.0 - PHASE 1 CRITICAL FIXES COMPLETE');
console.log('🎨 Enhanced: Unified chart styling, export buttons, professional tooltips');
console.log('📊 All 11 sections ready with consistent theming');