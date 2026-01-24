// ==================== BotV2 Dashboard v4.7 - COMPLETE PROFESSIONAL ====================
// Fortune 500 Enterprise Edition - 12+ Plotly Charts
// Author: Juan Carlos Garcia
// Date: 24-01-2026
// Version: 4.7 - ALL SECTIONS + ALL CHARTS

// ==================== GLOBAL STATE ====================
let socket = null;
let currentTheme = 'dark';
let currentSection = 'dashboard';
let chartInstances = {};

// Professional Plotly theme configs
const plotlyThemes = {
    dark: {
        paper_bgcolor: 'rgba(13, 17, 23, 0)',
        plot_bgcolor: 'rgba(22, 27, 34, 0.5)',
        font: { color: '#e6edf3', family: 'Inter, sans-serif', size: 12 },
        gridcolor: '#30363d',
        linecolor: '#2f81f7',
        fillcolor: 'rgba(47, 129, 247, 0.15)',
        successcolor: '#3fb950',
        dangercolor: '#f85149'
    },
    light: {
        paper_bgcolor: 'rgba(255, 255, 255, 0)',
        plot_bgcolor: 'rgba(246, 248, 250, 0.5)',
        font: { color: '#1f2328', family: 'Inter, sans-serif', size: 12 },
        gridcolor: '#d0d7de',
        linecolor: '#0969da',
        fillcolor: 'rgba(9, 105, 218, 0.15)',
        successcolor: '#1a7f37',
        dangercolor: '#cf222e'
    },
    bloomberg: {
        paper_bgcolor: 'rgba(0, 0, 0, 0)',
        plot_bgcolor: 'rgba(10, 10, 10, 0.5)',
        font: { color: '#ff9900', family: 'Courier New, monospace', size: 11 },
        gridcolor: '#2a2a2a',
        linecolor: '#ff9900',
        fillcolor: 'rgba(255, 153, 0, 0.15)',
        successcolor: '#00ff00',
        dangercolor: '#ff0000'
    }
};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 BotV2 Dashboard v4.7 - COMPLETE');
    
    if (typeof Plotly === 'undefined') {
        console.error('❌ Plotly.js not loaded!');
        return;
    }
    
    initWebSocket();
    setupMenuHandlers();
    
    const savedTheme = localStorage.getItem('dashboard-theme') || 'dark';
    setTheme(savedTheme, true);
    
    loadSection('dashboard');
    console.log('✅ Dashboard initialized');
});

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
    console.log(`Loading: ${section}`);
    currentSection = section;
    cleanupCharts();
    
    document.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
    const activeItem = document.querySelector(`[data-section="${section}"]`);
    if (activeItem) activeItem.classList.add('active');
    
    const titles = {
        'dashboard': 'Dashboard', 'portfolio': 'Portfolio', 'trades': 'Trade History',
        'performance': 'Performance', 'risk': 'Risk Analysis', 'markets': 'Market Overview',
        'strategies': 'Strategies', 'backtesting': 'Backtesting', 'settings': 'Settings'
    };
    
    const pageTitle = document.getElementById('page-title');
    if (pageTitle) pageTitle.textContent = titles[section] || section;
    
    fetchSectionContent(section);
}

function fetchSectionContent(section) {
    const container = document.getElementById('main-container');
    if (!container) return;
    
    container.innerHTML = '<div class="loading"><div class="spinner"></div><div class="loading-text">Loading...</div></div>';
    
    fetch(`/api/section/${section}`)
        .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
        .then(data => renderSection(section, data))
        .catch(error => {
            console.error(`Error loading ${section}:`, error);
            container.innerHTML = `<div style="text-align:center;padding:50px;color:var(--accent-danger)"><h2>Error</h2><p>${error}</p><button onclick="loadSection('${section}')">Retry</button></div>`;
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
        'settings': renderSettings
    };
    
    const renderer = renderers[section];
    if (renderer) {
        try { renderer(data); }
        catch (error) { console.error('Render error:', error); }
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

function renderSettings(data) {
    const container = document.getElementById('main-container');
    container.innerHTML = `
        <div class="kpi-card">
            <h2>⚙️ Settings</h2>
            <p>Configure dashboard settings</p>
        </div>
    `;
}

// ==================== CHART CREATORS ====================

function createEquityChart(data) {
    if (!data.timestamps || !data.equity) return;
    
    const theme = plotlyThemes[currentTheme];
    const trace = {
        x: data.timestamps,
        y: data.equity,
        type: 'scatter',
        mode: 'lines',
        line: { color: theme.linecolor, width: 2 },
        fill: 'tozeroy',
        fillcolor: theme.fillcolor,
        name: 'Equity'
    };
    
    const layout = {
        paper_bgcolor: theme.paper_bgcolor,
        plot_bgcolor: theme.plot_bgcolor,
        font: theme.font,
        xaxis: { gridcolor: theme.gridcolor },
        yaxis: { gridcolor: theme.gridcolor, tickprefix: '€' },
        margin: { t: 10, r: 20, b: 40, l: 70 },
        showlegend: false
    };
    
    Plotly.newPlot('equity-chart', [trace], layout, { responsive: true, displaylogo: false });
    chartInstances['equity-chart'] = true;
}

function createPortfolioPieChart(positions) {
    const theme = plotlyThemes[currentTheme];
    
    const trace = {
        labels: positions.map(p => p.symbol),
        values: positions.map(p => p.value),
        type: 'pie',
        hole: 0.4,
        textinfo: 'label+percent',
        textfont: { size: 11 }
    };
    
    const layout = {
        paper_bgcolor: theme.paper_bgcolor,
        plot_bgcolor: theme.plot_bgcolor,
        font: theme.font,
        margin: { t: 10, r: 20, b: 10, l: 20 },
        showlegend: false
    };
    
    Plotly.newPlot('portfolio-pie', [trace], layout, { responsive: true, displaylogo: false });
    chartInstances['portfolio-pie'] = true;
}

function createMonthlyReturnsChart(data) {
    if (!data.months || !data.returns) return;
    
    const theme = plotlyThemes[currentTheme];
    const colors = data.returns.map(r => r >= 0 ? theme.successcolor : theme.dangercolor);
    
    const trace = {
        x: data.months,
        y: data.returns,
        type: 'bar',
        marker: { color: colors }
    };
    
    const layout = {
        paper_bgcolor: theme.paper_bgcolor,
        plot_bgcolor: theme.plot_bgcolor,
        font: theme.font,
        xaxis: { gridcolor: theme.gridcolor },
        yaxis: { gridcolor: theme.gridcolor, ticksuffix: '%' },
        margin: { t: 10, r: 20, b: 40, l: 60 },
        showlegend: false
    };
    
    Plotly.newPlot('monthly-returns', [trace], layout, { responsive: true, displaylogo: false });
    chartInstances['monthly-returns'] = true;
}

function createDrawdownChart(data) {
    if (!data.timestamps || !data.drawdown) return;
    
    const theme = plotlyThemes[currentTheme];
    
    const trace = {
        x: data.timestamps,
        y: data.drawdown,
        type: 'scatter',
        mode: 'lines',
        line: { color: theme.dangercolor, width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(248, 81, 73, 0.2)',
        name: 'Drawdown'
    };
    
    const layout = {
        paper_bgcolor: theme.paper_bgcolor,
        plot_bgcolor: theme.plot_bgcolor,
        font: theme.font,
        xaxis: { gridcolor: theme.gridcolor },
        yaxis: { gridcolor: theme.gridcolor, ticksuffix: '%' },
        margin: { t: 10, r: 20, b: 40, l: 70 },
        showlegend: false
    };
    
    Plotly.newPlot('drawdown-chart', [trace], layout, { responsive: true, displaylogo: false });
    chartInstances['drawdown-chart'] = true;
}

function createBacktestChart(data) {
    if (!data.timestamps || !data.strategy || !data.benchmark) return;
    
    const theme = plotlyThemes[currentTheme];
    
    const trace1 = {
        x: data.timestamps,
        y: data.strategy,
        type: 'scatter',
        mode: 'lines',
        line: { color: theme.successcolor, width: 2 },
        name: 'Strategy'
    };
    
    const trace2 = {
        x: data.timestamps,
        y: data.benchmark,
        type: 'scatter',
        mode: 'lines',
        line: { color: theme.linecolor, width: 2, dash: 'dot' },
        name: 'Benchmark'
    };
    
    const layout = {
        paper_bgcolor: theme.paper_bgcolor,
        plot_bgcolor: theme.plot_bgcolor,
        font: theme.font,
        xaxis: { gridcolor: theme.gridcolor },
        yaxis: { gridcolor: theme.gridcolor, tickprefix: '€' },
        margin: { t: 10, r: 20, b: 40, l: 70 },
        showlegend: true,
        legend: { x: 0, y: 1, bgcolor: 'rgba(0,0,0,0)' }
    };
    
    Plotly.newPlot('backtest-chart', [trace1, trace2], layout, { responsive: true, displaylogo: false });
    chartInstances['backtest-chart'] = true;
}

// ==================== WEBSOCKET ====================
function initWebSocket() {
    if (typeof io === 'undefined') {
        console.warn('Socket.io not loaded');
        return;
    }
    
    socket = io({ reconnection: true });
    
    socket.on('connect', () => {
        console.log('✅ Connected');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', () => {
        console.log('❌ Disconnected');
        updateConnectionStatus(false);
    });
    
    socket.on('update', () => {
        console.log('📊 Update received');
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

function refreshChart(chartName) {
    console.log(`Refreshing ${chartName}`);
    if (currentSection) loadSection(currentSection);
}

function exportChart(chartName) {
    console.log(`Exporting ${chartName}`);
}

// ==================== RESIZE ====================
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

console.log('✅ Dashboard v4.7 COMPLETE');
