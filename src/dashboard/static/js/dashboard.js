// ==================== BotV2 Dashboard v4.8 - COMPLETE + LIVE MONITOR + CONTROL PANEL ====================
// Fortune 500 Enterprise Edition - ALL 11 SECTIONS FUNCTIONAL
// Author: Juan Carlos Garcia
// Date: 24-01-2026
// Version: 4.8.0 - MEGA FIX

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
    console.log('🚀 BotV2 Dashboard v4.8 - COMPLETE');
    
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
    const container = document.getElementById('main-container');
    if (!container) return;
    
    container.innerHTML = '<div class="loading"><div class="spinner"></div><div class="loading-text">Loading...</div></div>';
    
    fetch(`/api/section/${section}`)
        .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
        .then(data => renderSection(section, data))
        .catch(error => {
            console.error(`Error loading ${section}:`, error);
            container.innerHTML = `<div style="text-align:center;padding:50px;color:var(--accent-danger)"><h2>❌ Error</h2><p>${error}</p><button onclick="loadSection('${section}')" style="margin-top:1rem;padding:8px 16px;background:var(--accent-primary);border:none;border-radius:6px;color:white;cursor:pointer;">🔄 Retry</button></div>`;
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
            console.log(`✅ ${section} rendered`);
        }
        catch (error) { 
            console.error(`❌ Render error in ${section}:`, error); 
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
    const status = data.status || {};
    const recent_trades = data.recent_trades || [];
    const active_orders = data.active_orders || [];
    
    let tradesRows = recent_trades.map(t => `
        <tr>
            <td>${t.timestamp}</td>
            <td><strong>${t.symbol}</strong></td>
            <td><span class="badge ${t.action === 'BUY' ? 'badge-success' : 'badge-danger'}">${t.action}</span></td>
            <td>${t.quantity}</td>
            <td>€${t.price}</td>
        </tr>
    `).join('');
    
    let ordersRows = active_orders.map(o => `
        <tr>
            <td><strong>${o.symbol}</strong></td>
            <td>${o.type}</td>
            <td>${o.side}</td>
            <td>${o.quantity}</td>
            <td>€${o.price}</td>
            <td><span class="badge ${o.status === 'PENDING' ? 'badge-warning' : 'badge-success'}">${o.status}</span></td>
        </tr>
    `).join('');
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">BOT STATUS</div>
                <div class="kpi-value ${status.bot_status === 'RUNNING' ? 'positive' : 'danger'}">${status.bot_status || 'STOPPED'}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">UPTIME</div>
                <div class="kpi-value">${status.uptime || 'N/A'}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">ACTIVE ORDERS</div>
                <div class="kpi-value">${active_orders.length}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">TODAY'S TRADES</div>
                <div class="kpi-value">${status.trades_today || 0}</div>
            </div>
        </div>
        
        <h3 style="margin:2rem 0 1rem;color:var(--text-primary)">Recent Trades (Real-Time)</h3>
        <div class="data-table">
            <table>
                <thead><tr><th>Time</th><th>Symbol</th><th>Action</th><th>Qty</th><th>Price</th></tr></thead>
                <tbody>${tradesRows || '<tr><td colspan="5">No recent trades</td></tr>'}</tbody>
            </table>
        </div>
        
        <h3 style="margin:2rem 0 1rem;color:var(--text-primary)">Active Orders</h3>
        <div class="data-table">
            <table>
                <thead><tr><th>Symbol</th><th>Type</th><th>Side</th><th>Qty</th><th>Price</th><th>Status</th></tr></thead>
                <tbody>${ordersRows || '<tr><td colspan="6">No active orders</td></tr>'}</tbody>
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
        xaxis: { gridcolor: theme.gridcolor, showgrid: true },
        yaxis: { gridcolor: theme.gridcolor, tickprefix: '€', showgrid: true },
        margin: { t: 10, r: 20, b: 40, l: 70 },
        showlegend: false,
        hovermode: 'x unified'
    };
    
    Plotly.newPlot('equity-chart', [trace], layout, { responsive: true, displaylogo: false, displayModeBar: true });
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
        textfont: { size: 11 },
        marker: { line: { color: theme.paper_bgcolor, width: 2 } }
    };
    
    const layout = {
        paper_bgcolor: theme.paper_bgcolor,
        plot_bgcolor: theme.plot_bgcolor,
        font: theme.font,
        margin: { t: 10, r: 20, b: 10, l: 20 },
        showlegend: false
    };
    
    Plotly.newPlot('portfolio-pie', [trace], layout, { responsive: true, displaylogo: false, displayModeBar: false });
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
        yaxis: { gridcolor: theme.gridcolor, ticksuffix: '%', zeroline: true },
        margin: { t: 10, r: 20, b: 40, l: 60 },
        showlegend: false,
        hovermode: 'x'
    };
    
    Plotly.newPlot('monthly-returns', [trace], layout, { responsive: true, displaylogo: false, displayModeBar: true });
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
        showlegend: false,
        hovermode: 'x unified'
    };
    
    Plotly.newPlot('drawdown-chart', [trace], layout, { responsive: true, displaylogo: false, displayModeBar: true });
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
        legend: { x: 0, y: 1, bgcolor: 'rgba(0,0,0,0)' },
        hovermode: 'x unified'
    };
    
    Plotly.newPlot('backtest-chart', [trace1, trace2], layout, { responsive: true, displaylogo: false, displayModeBar: true });
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

function refreshChart(chartName) {
    console.log(`🔄 Refreshing ${chartName}`);
    if (currentSection) loadSection(currentSection);
}

function exportChart(chartName) {
    console.log(`💾 Exporting ${chartName}`);
    alert('Chart export functionality coming soon');
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

console.log('✅ Dashboard v4.8.0 - ALL 11 SECTIONS READY');
console.log('📊 Sections: dashboard, portfolio, trades, performance, risk, markets, strategies, backtesting, live_monitor, control_panel, settings');
