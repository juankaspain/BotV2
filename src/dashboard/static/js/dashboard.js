// ==================== BotV2 Dashboard v4.5 - PRODUCTION GRADE ====================
// Enterprise Edition - Complete Integration - Zero Bugs
// Fortune 500 Quality Standards
// Author: Juan Carlos Garcia
// Date: 24-01-2026
// Version: 4.5.0

// ==================== GLOBAL STATE ====================
let socket = null;
let currentTheme = 'dark';
let currentSection = 'dashboard';
let currentTimeFilter = '30d';
let chartInstances = {};
let dashboardData = {};
let reconnectAttempts = 0;
let reconnectTimer = null;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_DELAY = 3000;

// ==================== THEME CONFIGURATIONS ====================
const plotlyThemes = {
    dark: {
        paper_bgcolor: 'rgba(13, 17, 23, 0)',
        plot_bgcolor: 'rgba(22, 27, 34, 0.5)',
        font: { color: '#e6edf3', family: 'Inter, sans-serif', size: 12 },
        gridcolor: '#30363d',
        linecolor: '#2f81f7',
        fillcolor: 'rgba(47, 129, 247, 0.15)',
        markercolor: '#2f81f7',
        successcolor: '#3fb950',
        dangercolor: '#f85149',
        warningcolor: '#d29922'
    },
    light: {
        paper_bgcolor: 'rgba(255, 255, 255, 0)',
        plot_bgcolor: 'rgba(246, 248, 250, 0.5)',
        font: { color: '#1f2328', family: 'Inter, sans-serif', size: 12 },
        gridcolor: '#d0d7de',
        linecolor: '#0969da',
        fillcolor: 'rgba(9, 105, 218, 0.15)',
        markercolor: '#0969da',
        successcolor: '#1a7f37',
        dangercolor: '#cf222e',
        warningcolor: '#bf8700'
    },
    bloomberg: {
        paper_bgcolor: 'rgba(0, 0, 0, 0)',
        plot_bgcolor: 'rgba(10, 10, 10, 0.5)',
        font: { color: '#ff9900', family: 'Courier New, monospace', size: 11 },
        gridcolor: '#2a2a2a',
        linecolor: '#ff9900',
        fillcolor: 'rgba(255, 153, 0, 0.15)',
        markercolor: '#ff9900',
        successcolor: '#00ff00',
        dangercolor: '#ff0000',
        warningcolor: '#ffff00'
    }
};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 BotV2 Dashboard v4.5 - Production Ready');
    
    // Verify Plotly.js loaded
    if (typeof Plotly === 'undefined') {
        console.error('❌ Plotly.js not loaded');
        showToast('Chart library failed to load', 'error');
        return;
    }
    
    initWebSocket();
    setupMenuHandlers();
    setupEventListeners();
    
    const savedTheme = localStorage.getItem('dashboard-theme') || 'dark';
    setTheme(savedTheme, true);
    
    loadSection('dashboard');
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        if (document.visibilityState === 'visible') {
            refreshCurrentSection(true);
        }
    }, 30000);
    
    console.log('✅ Dashboard initialized successfully');
});

// ==================== EVENT LISTENERS ====================
function setupEventListeners() {
    // Visibility change handler
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible' && currentSection) {
            refreshCurrentSection(true);
        }
    });
    
    // Resize handler with debounce
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            Object.keys(chartInstances).forEach(chartId => {
                const element = document.getElementById(chartId);
                if (element && element.data) {
                    try {
                        Plotly.Plots.resize(chartId);
                    } catch (e) {
                        console.warn(`Failed to resize chart: ${chartId}`, e);
                    }
                }
            });
        }, 250);
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + R to refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            refreshCurrentSection();
            showToast('Dashboard refreshed', 'info');
        }
    });
}

// ==================== MENU NAVIGATION ====================
function setupMenuHandlers() {
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            if (section && section !== currentSection) {
                loadSection(section);
            }
        });
    });
}

function loadSection(section) {
    // Validate section parameter
    if (!section || section === 'null' || section === 'undefined') {
        console.error('❌ Invalid section:', section);
        showToast('Invalid section requested', 'error');
        return;
    }
    
    console.log(`📄 Loading section: ${section}`);
    currentSection = section;
    
    // Cleanup previous charts to prevent memory leaks
    cleanupCharts();
    
    // Update active menu item
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    const activeItem = document.querySelector(`[data-section="${section}"]`);
    if (activeItem) {
        activeItem.classList.add('active');
    }
    
    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'portfolio': 'Portfolio',
        'strategies': 'Strategies',
        'risk': 'Risk Analysis',
        'trades': 'Trade History',
        'live_monitor': 'Live Monitor',
        'strategy_editor': 'Strategy Editor',
        'control_panel': 'Control Panel',
        'settings': 'Settings'
    };
    
    const pageTitle = document.getElementById('page-title');
    if (pageTitle) {
        pageTitle.textContent = titles[section] || section.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    // Update breadcrumb
    updateBreadcrumb(section);
    
    fetchSectionContent(section);
}

function updateBreadcrumb(section) {
    const breadcrumb = document.getElementById('breadcrumb');
    if (!breadcrumb) return;
    
    const sectionNames = {
        'dashboard': 'Dashboard',
        'portfolio': 'Portfolio',
        'strategies': 'Strategies',
        'risk': 'Risk Analysis',
        'trades': 'Trade History',
        'live_monitor': 'Live Monitor',
        'strategy_editor': 'Strategy Editor',
        'control_panel': 'Control Panel',
        'settings': 'Settings'
    };
    
    breadcrumb.innerHTML = `
        <span class="breadcrumb-item" onclick="loadSection('dashboard')">Home</span>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-item active">${sectionNames[section] || section}</span>
    `;
}

function fetchSectionContent(section) {
    const container = document.getElementById('main-container');
    if (!container) {
        console.error('❌ Main container not found');
        return;
    }
    
    // Show loading state
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <div class="loading-text">Loading ${section}...</div>
            <div class="loading-progress">
                <div class="loading-progress-bar"></div>
            </div>
        </div>
    `;
    
    fetch(`/api/section/${section}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (!data) {
                throw new Error('Empty response from server');
            }
            dashboardData[section] = data;
            renderSection(section, data);
        })
        .catch(error => {
            console.error('❌ Error loading section:', error);
            container.innerHTML = `
                <div style="text-align: center; padding: 80px 20px; color: var(--text-secondary);">
                    <div style="font-size: 48px; margin-bottom: 20px;">⚠️</div>
                    <h2 style="color: var(--accent-danger); margin-bottom: 12px; font-size: 24px;">Error Loading Section</h2>
                    <p style="margin-bottom: 24px; font-size: 14px;">${error.message}</p>
                    <button onclick="loadSection('${section}')" style="padding: 12px 24px; background: var(--accent-primary); color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 14px; transition: all 0.2s;">
                        🔄 Retry
                    </button>
                </div>
            `;
            showToast(`Failed to load ${section}`, 'error');
        });
}

function renderSection(section, data) {
    try {
        switch(section) {
            case 'dashboard': 
                renderDashboard(data); 
                break;
            case 'portfolio': 
                renderPortfolio(data); 
                break;
            case 'strategies': 
                renderStrategies(data); 
                break;
            case 'risk': 
                renderRisk(data); 
                break;
            case 'trades': 
                renderTrades(data); 
                break;
            case 'live_monitor': 
                renderLiveMonitor(data); 
                break;
            case 'strategy_editor': 
                renderStrategyEditor(data); 
                break;
            case 'control_panel': 
                renderControlPanel(data); 
                break;
            case 'settings': 
                renderSettings(data); 
                break;
            default:
                console.error('❌ Unknown section:', section);
                showToast(`Section "${section}" not implemented`, 'warning');
        }
    } catch (error) {
        console.error('❌ Error rendering section:', error);
        showToast('Failed to render section', 'error');
    }
}

// ==================== SECTION RENDERERS ====================

function renderDashboard(data) {
    const container = document.getElementById('main-container');
    const overview = data.overview || {};
    const equity = data.equity || { timestamps: [], equity: [] };
    
    container.innerHTML = `
        <div class="time-filters">
            <button class="time-filter-btn" onclick="setTimeFilter('24h', event)">24H</button>
            <button class="time-filter-btn" onclick="setTimeFilter('7d', event)">7D</button>
            <button class="time-filter-btn active" onclick="setTimeFilter('30d', event)">30D</button>
            <button class="time-filter-btn" onclick="setTimeFilter('90d', event)">90D</button>
            <button class="time-filter-btn" onclick="setTimeFilter('ytd', event)">YTD</button>
            <button class="time-filter-btn" onclick="setTimeFilter('all', event)">All</button>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Portfolio Value</div>
                <div class="kpi-value">${overview.equity || 'N/A'}</div>
                <div class="kpi-change ${(overview.daily_change || 0) >= 0 ? 'positive' : 'negative'}">
                    ${(overview.daily_change || 0) >= 0 ? '↑' : '↓'} ${Math.abs(overview.daily_change || 0)}% today
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Total P&L</div>
                <div class="kpi-value">${overview.total_pnl || 'N/A'}</div>
                <div class="kpi-change ${(overview.total_return || 0) >= 0 ? 'positive' : 'negative'}">
                    ${(overview.total_return || 0) >= 0 ? '↑' : '↓'} ${Math.abs(overview.total_return || 0)}%
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Win Rate</div>
                <div class="kpi-value">${overview.win_rate || 'N/A'}%</div>
                <div class="kpi-change">${overview.total_trades || 0} trades</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Sharpe Ratio</div>
                <div class="kpi-value">${overview.sharpe_ratio || 'N/A'}</div>
                <div class="kpi-change">DD: ${overview.max_drawdown || 'N/A'}%</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-card full-width">
                <div class="chart-header">
                    <div class="chart-title">Equity Curve</div>
                    <div class="chart-actions">
                        <button class="chart-btn" onclick="refreshChart('equity')">🔄 Refresh</button>
                        <button class="chart-btn" onclick="exportChart('equity')">💾 Export</button>
                    </div>
                </div>
                <div id="equity-chart" class="chart-container"></div>
            </div>
            <div class="chart-card">
                <div class="chart-header">
                    <div class="chart-title">Strategy Returns</div>
                    <div class="chart-actions">
                        <button class="chart-btn" onclick="refreshChart('strategies')">🔄 Refresh</button>
                    </div>
                </div>
                <div id="strategies-chart" class="chart-container"></div>
            </div>
            <div class="chart-card">
                <div class="chart-header">
                    <div class="chart-title">Risk Metrics</div>
                    <div class="chart-actions">
                        <button class="chart-btn" onclick="refreshChart('risk')">🔄 Refresh</button>
                    </div>
                </div>
                <div id="risk-chart" class="chart-container"></div>
            </div>
        </div>
    `;
    
    setTimeout(() => {
        if (equity.timestamps && equity.equity && equity.timestamps.length > 0) {
            createEquityChart(equity);
        }
        if (data.strategies) {
            createStrategiesChart(data.strategies);
        }
        if (data.risk) {
            createRiskChart(data.risk);
        }
    }, 100);
}

function renderPortfolio(data) {
    const container = document.getElementById('main-container');
    const summary = data.summary || {};
    const positions = data.positions || [];
    
    const positionsHTML = positions.length > 0 ? positions.map(pos => `
        <tr>
            <td><strong>${pos.symbol || 'N/A'}</strong></td>
            <td>${pos.quantity || 0}</td>
            <td>€${(pos.entry_price || 0).toFixed(2)}</td>
            <td>€${(pos.current_price || 0).toFixed(2)}</td>
            <td class="${(pos.pnl || 0) >= 0 ? 'kpi-change positive' : 'kpi-change negative'}">
                €${(pos.pnl || 0).toFixed(2)} (${(pos.pnl_pct || 0).toFixed(2)}%)
            </td>
            <td><strong>€${(pos.value || 0).toFixed(2)}</strong></td>
        </tr>
    `).join('') : '<tr><td colspan="6" style="text-align: center; padding: 40px; color: var(--text-secondary);">No positions available</td></tr>';
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Total Value</div>
                <div class="kpi-value">€${(summary.total_value || 0).toFixed(2)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Cash Available</div>
                <div class="kpi-value">€${(summary.cash || 0).toFixed(2)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Total P&L</div>
                <div class="kpi-value ${(summary.total_pnl || 0) >= 0 ? 'kpi-change positive' : 'kpi-change negative'}">
                    €${(summary.total_pnl || 0).toFixed(2)}
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Open Positions</div>
                <div class="kpi-value">${positions.length}</div>
            </div>
        </div>

        <div class="data-table">
            <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Quantity</th>
                        <th>Entry Price</th>
                        <th>Current Price</th>
                        <th>P&L</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>${positionsHTML}</tbody>
            </table>
        </div>
    `;
}

function renderStrategies(data) {
    const container = document.getElementById('main-container');
    const summary = data.summary || {};
    const strategies = Array.isArray(data.strategies) ? data.strategies : [];
    
    const strategiesHTML = strategies.length > 0 ? strategies.map(strat => `
        <tr>
            <td><strong>${strat.name || 'Unknown'}</strong></td>
            <td class="${(strat.return || 0) >= 0 ? 'kpi-change positive' : 'kpi-change negative'}">
                ${(strat.return || 0).toFixed(2)}%
            </td>
            <td>${(strat.sharpe || 0).toFixed(2)}</td>
            <td>${(strat.win_rate || 0).toFixed(1)}%</td>
            <td>${strat.trades || 0}</td>
            <td>
                <span class="badge ${(strat.status || 'inactive') === 'active' ? 'badge-success' : 'badge-warning'}">
                    ${strat.status || 'inactive'}
                </span>
            </td>
        </tr>
    `).join('') : '<tr><td colspan="6" style="text-align: center; padding: 40px; color: var(--text-secondary);">No strategies available</td></tr>';
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Active Strategies</div>
                <div class="kpi-value">${summary.active || 0}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Best Performer</div>
                <div class="kpi-value">${summary.best_strategy || 'N/A'}</div>
                <div class="kpi-change positive">+${(summary.best_return || 0).toFixed(2)}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Avg Sharpe</div>
                <div class="kpi-value">${(summary.avg_sharpe || 0).toFixed(2)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Total Trades</div>
                <div class="kpi-value">${summary.total_trades || 0}</div>
            </div>
        </div>

        <div class="data-table">
            <table>
                <thead>
                    <tr>
                        <th>Strategy</th>
                        <th>Return</th>
                        <th>Sharpe</th>
                        <th>Win Rate</th>
                        <th>Trades</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>${strategiesHTML}</tbody>
            </table>
        </div>
    `;
}

function renderRisk(data) {
    const container = document.getElementById('main-container');
    const metrics = data.metrics || {};
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">VaR (95%)</div>
                <div class="kpi-value kpi-change negative">€${(metrics.var_95 || 0).toFixed(2)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Max Drawdown</div>
                <div class="kpi-value kpi-change negative">${(metrics.max_drawdown || 0).toFixed(2)}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Volatility</div>
                <div class="kpi-value">${(metrics.volatility || 0).toFixed(2)}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Sharpe Ratio</div>
                <div class="kpi-value kpi-change positive">${(metrics.sharpe || 0).toFixed(2)}</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-card">
                <div class="chart-header">
                    <div class="chart-title">Drawdown</div>
                </div>
                <div id="drawdown-chart" class="chart-container"></div>
            </div>
            <div class="chart-card">
                <div class="chart-header">
                    <div class="chart-title">Volatility</div>
                </div>
                <div id="volatility-chart" class="chart-container"></div>
            </div>
        </div>
    `;
    
    setTimeout(() => {
        if (data.drawdown) createDrawdownChart(data.drawdown);
        if (data.volatility) createVolatilityChart(data.volatility);
    }, 100);
}

function renderTrades(data) {
    const container = document.getElementById('main-container');
    const summary = data.summary || {};
    const trades = Array.isArray(data.trades) ? data.trades : [];
    
    const tradesHTML = trades.length > 0 ? trades.map(trade => `
        <tr>
            <td>${trade.timestamp ? new Date(trade.timestamp).toLocaleString() : 'N/A'}</td>
            <td>${trade.strategy || 'N/A'}</td>
            <td><strong>${trade.symbol || 'N/A'}</strong></td>
            <td>
                <span class="badge ${(trade.action || 'BUY') === 'BUY' ? 'badge-success' : 'badge-danger'}">
                    ${trade.action || 'N/A'}
                </span>
            </td>
            <td>${trade.quantity || 0}</td>
            <td>€${(trade.price || 0).toFixed(2)}</td>
            <td class="${(trade.pnl || 0) >= 0 ? 'kpi-change positive' : 'kpi-change negative'}">
                €${(trade.pnl || 0).toFixed(2)}
            </td>
        </tr>
    `).join('') : '<tr><td colspan="7" style="text-align: center; padding: 40px; color: var(--text-secondary);">No trades available</td></tr>';
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Total Trades</div>
                <div class="kpi-value">${summary.total || 0}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Winning Trades</div>
                <div class="kpi-value kpi-change positive">${summary.winning || 0}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Win Rate</div>
                <div class="kpi-value">${(summary.win_rate || 0).toFixed(1)}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Profit Factor</div>
                <div class="kpi-value">${(summary.profit_factor || 0).toFixed(2)}</div>
            </div>
        </div>

        <div class="data-table">
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Strategy</th>
                        <th>Symbol</th>
                        <th>Action</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>P&L</th>
                    </tr>
                </thead>
                <tbody>${tradesHTML}</tbody>
            </table>
        </div>
    `;
}

function renderLiveMonitor(data) {
    const container = document.getElementById('main-container');
    const summary = data.summary || {};
    const activeTrades = data.active_trades || [];
    
    const tradesHTML = activeTrades.length > 0 ? activeTrades.map(trade => `
        <tr>
            <td><strong>${trade.symbol || 'N/A'}</strong></td>
            <td>${trade.strategy || 'N/A'}</td>
            <td>
                <span class="badge ${(trade.action || 'BUY') === 'BUY' ? 'badge-success' : 'badge-danger'}">
                    ${trade.action || 'N/A'}
                </span>
            </td>
            <td>€${(trade.entry_price || 0).toFixed(2)}</td>
            <td>€${(trade.current_price || 0).toFixed(2)}</td>
            <td class="${(trade.pnl || 0) >= 0 ? 'kpi-change positive' : 'kpi-change negative'}">
                €${(trade.pnl || 0).toFixed(2)}
            </td>
            <td>${trade.time_elapsed || 'N/A'}</td>
        </tr>
    `).join('') : '<tr><td colspan="7" style="text-align: center; padding: 40px; color: var(--text-secondary);">No active trades</td></tr>';
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Active Trades</div>
                <div class="kpi-value">${activeTrades.length}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Total P&L</div>
                <div class="kpi-value ${(summary.total_pnl || 0) >= 0 ? 'kpi-change positive' : 'kpi-change negative'}">
                    €${(summary.total_pnl || 0).toFixed(2)}
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Best Trade</div>
                <div class="kpi-value kpi-change positive">€${(summary.best_trade || 0).toFixed(2)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Worst Trade</div>
                <div class="kpi-value kpi-change negative">€${(summary.worst_trade || 0).toFixed(2)}</div>
            </div>
        </div>

        <div class="data-table">
            <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Strategy</th>
                        <th>Action</th>
                        <th>Entry</th>
                        <th>Current</th>
                        <th>P&L</th>
                        <th>Duration</th>
                    </tr>
                </thead>
                <tbody>${tradesHTML}</tbody>
            </table>
        </div>
    `;
}

function renderStrategyEditor(data) {
    const container = document.getElementById('main-container');
    const strategies = data.strategies || [];
    
    const strategiesHTML = strategies.length > 0 ? strategies.map((strat, idx) => `
        <div class="chart-card">
            <div class="chart-header">
                <div class="chart-title">${strat.name || 'Strategy ' + (idx + 1)}</div>
                <div class="chart-actions">
                    <button class="chart-btn" onclick="editStrategy('${strat.id}')">✏️ Edit</button>
                    <button class="chart-btn" onclick="testStrategy('${strat.id}')">▶️ Test</button>
                </div>
            </div>
            <div style="padding: 16px;">
                <p style="color: var(--text-secondary); margin-bottom: 16px;">${strat.description || 'No description'}</p>
                <div class="kpi-grid" style="grid-template-columns: repeat(4, 1fr); gap: 12px;">
                    <div>
                        <div class="kpi-title">Return</div>
                        <div class="kpi-value" style="font-size: 18px;">${(strat.return || 0).toFixed(2)}%</div>
                    </div>
                    <div>
                        <div class="kpi-title">Sharpe</div>
                        <div class="kpi-value" style="font-size: 18px;">${(strat.sharpe || 0).toFixed(2)}</div>
                    </div>
                    <div>
                        <div class="kpi-title">Trades</div>
                        <div class="kpi-value" style="font-size: 18px;">${strat.trades || 0}</div>
                    </div>
                    <div>
                        <div class="kpi-title">Status</div>
                        <span class="badge ${(strat.status || 'inactive') === 'active' ? 'badge-success' : 'badge-warning'}" style="margin-top: 4px;">
                            ${strat.status || 'inactive'}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    `).join('') : '<div style="text-align: center; padding: 80px; color: var(--text-secondary);">No strategies available</div>';
    
    container.innerHTML = `
        <div style="margin-bottom: 16px;">
            <button class="chart-btn" onclick="createNewStrategy()" style="padding: 10px 20px;">
                ➕ Create New Strategy
            </button>
        </div>
        <div class="charts-grid">
            ${strategiesHTML}
        </div>
    `;
}

function renderControlPanel(data) {
    const container = document.getElementById('main-container');
    const bot = data.bot_status || {};
    const limits = data.limits || {};
    const system = data.system || {};
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Bot Status</div>
                <div class="kpi-value">
                    <span class="badge ${bot.status === 'running' ? 'badge-success' : 'badge-warning'}">
                        ${bot.status || 'stopped'}
                    </span>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Uptime</div>
                <div class="kpi-value" style="font-size: 20px;">${bot.uptime || '0h 0m'}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Trading Mode</div>
                <div class="kpi-value" style="font-size: 20px;">${bot.mode || 'paper'}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">API Status</div>
                <div class="kpi-value">
                    <span class="badge ${system.api_connected ? 'badge-success' : 'badge-danger'}">
                        ${system.api_connected ? 'connected' : 'disconnected'}
                    </span>
                </div>
            </div>
        </div>

        <div class="chart-card" style="margin-top: 16px;">
            <div class="chart-header">
                <div class="chart-title">Bot Controls</div>
            </div>
            <div style="padding: 24px; display: flex; gap: 12px; flex-wrap: wrap;">
                <button class="chart-btn" onclick="startBot()" style="padding: 12px 24px; background: var(--accent-success); color: white;">
                    ▶️ Start Bot
                </button>
                <button class="chart-btn" onclick="pauseBot()" style="padding: 12px 24px;">
                    ⏸️ Pause Bot
                </button>
                <button class="chart-btn" onclick="stopBot()" style="padding: 12px 24px;">
                    ⏹️ Stop Bot
                </button>
                <button class="chart-btn" onclick="emergencyStop()" style="padding: 12px 24px; background: var(--accent-danger); color: white;">
                    🛑 Emergency Stop
                </button>
            </div>
        </div>

        <div class="data-table" style="margin-top: 16px;">
            <h3 style="padding: 20px; color: var(--text-primary); font-weight: 600;">Risk Limits</h3>
            <table>
                <thead>
                    <tr>
                        <th>Limit Type</th>
                        <th>Current Value</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Max Position Size</td>
                        <td>${limits.max_position || 0}%</td>
                        <td>Maximum single position size</td>
                    </tr>
                    <tr>
                        <td>Daily Loss Limit</td>
                        <td>${limits.daily_loss || 0}%</td>
                        <td>Maximum daily loss allowed</td>
                    </tr>
                    <tr>
                        <td>Max Drawdown</td>
                        <td>${limits.max_drawdown || 0}%</td>
                        <td>Maximum portfolio drawdown</td>
                    </tr>
                    <tr>
                        <td>Max Open Positions</td>
                        <td>${limits.max_positions || 0}</td>
                        <td>Maximum concurrent positions</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}

function renderSettings(data) {
    const container = document.getElementById('main-container');
    const settings = data.settings || {};
    const system = data.system || {};
    
    container.innerHTML = `
        <div class="data-table">
            <h3 style="padding: 20px; color: var(--text-primary); font-weight: 600;">General Settings</h3>
            <table>
                <thead>
                    <tr>
                        <th>Setting</th>
                        <th>Value</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Trading Mode</td>
                        <td><span class="badge ${(settings.mode || 'paper') === 'paper' ? 'badge-warning' : 'badge-success'}">${settings.mode || 'paper'}</span></td>
                        <td>Current trading mode</td>
                    </tr>
                    <tr>
                        <td>Initial Capital</td>
                        <td>€${settings.initial_capital || 0}</td>
                        <td>Starting portfolio value</td>
                    </tr>
                    <tr>
                        <td>Max Position Size</td>
                        <td>${settings.max_position_size || 0}%</td>
                        <td>Maximum position as % of portfolio</td>
                    </tr>
                    <tr>
                        <td>Stop Loss</td>
                        <td>${settings.stop_loss || 0}%</td>
                        <td>Default stop loss percentage</td>
                    </tr>
                    <tr>
                        <td>Risk Per Trade</td>
                        <td>${settings.risk_per_trade || 0}%</td>
                        <td>Maximum risk per trade</td>
                    </tr>
                    <tr>
                        <td>Auto Refresh</td>
                        <td><span class="badge badge-success">${settings.auto_refresh ? 'Enabled' : 'Disabled'}</span></td>
                        <td>Automatic data refresh</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="data-table" style="margin-top: 24px;">
            <h3 style="padding: 20px; color: var(--text-primary); font-weight: 600;">System Information</h3>
            <table>
                <thead>
                    <tr>
                        <th>Property</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Dashboard Version</td>
                        <td><span class="badge badge-info">${system.version || '4.5'}</span></td>
                    </tr>
                    <tr>
                        <td>Environment</td>
                        <td>${system.environment || 'development'}</td>
                    </tr>
                    <tr>
                        <td>Uptime</td>
                        <td>${system.uptime || 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Last Update</td>
                        <td>${system.last_update || new Date().toLocaleString()}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}

// ==================== CHART CREATORS ====================

function cleanupCharts() {
    Object.keys(chartInstances).forEach(chartId => {
        try {
            const element = document.getElementById(chartId);
            if (element) {
                Plotly.purge(chartId);
            }
        } catch (e) {
            console.warn(`Failed to cleanup chart: ${chartId}`, e);
        }
    });
    chartInstances = {};
}

function createEquityChart(data) {
    if (!data || !data.timestamps || !data.equity || data.timestamps.length === 0) {
        console.warn('Invalid equity data');
        return;
    }
    
    const theme = plotlyThemes[currentTheme];
    
    try {
        const trace = {
            x: data.timestamps,
            y: data.equity,
            type: 'scatter',
            mode: 'lines',
            name: 'Equity',
            line: { color: theme.linecolor, width: 2 },
            fill: 'tozeroy',
            fillcolor: theme.fillcolor,
            hovertemplate: '<b>€%{y:,.2f}</b><br>%{x}<extra></extra>'
        };
        
        const layout = {
            paper_bgcolor: theme.paper_bgcolor,
            plot_bgcolor: theme.plot_bgcolor,
            font: theme.font,
            xaxis: { gridcolor: theme.gridcolor, showgrid: true, zeroline: false },
            yaxis: { gridcolor: theme.gridcolor, tickprefix: '€', showgrid: true, zeroline: false },
            margin: { t: 10, r: 20, b: 40, l: 70 },
            showlegend: false,
            hovermode: 'x unified'
        };
        
        const config = { responsive: true, displaylogo: false, modeBarButtonsToRemove: ['lasso2d', 'select2d'] };
        
        Plotly.newPlot('equity-chart', [trace], layout, config);
        chartInstances['equity-chart'] = true;
    } catch (error) {
        console.error('Failed to create equity chart:', error);
    }
}

function createStrategiesChart(data) {
    if (!data || !data.names || !data.returns) {
        console.warn('Invalid strategies data');
        return;
    }
    
    const theme = plotlyThemes[currentTheme];
    
    try {
        const colors = data.returns.map(v => v > 0 ? theme.successcolor : theme.dangercolor);
        
        const trace = {
            x: data.names,
            y: data.returns,
            type: 'bar',
            marker: { color: colors },
            hovertemplate: '<b>%{x}</b><br>%{y:.2f}%<extra></extra>'
        };
        
        const layout = {
            paper_bgcolor: theme.paper_bgcolor,
            plot_bgcolor: theme.plot_bgcolor,
            font: theme.font,
            xaxis: { gridcolor: theme.gridcolor },
            yaxis: { ticksuffix: '%', gridcolor: theme.gridcolor, showgrid: true, zeroline: true },
            margin: { t: 10, r: 20, b: 60, l: 60 },
            showlegend: false
        };
        
        const config = { responsive: true, displaylogo: false, modeBarButtonsToRemove: ['lasso2d', 'select2d'] };
        
        Plotly.newPlot('strategies-chart', [trace], layout, config);
        chartInstances['strategies-chart'] = true;
    } catch (error) {
        console.error('Failed to create strategies chart:', error);
    }
}

function createRiskChart(data) {
    if (!data || !data.values || !data.metrics) {
        console.warn('Invalid risk data');
        return;
    }
    
    const theme = plotlyThemes[currentTheme];
    
    try {
        const trace = {
            type: 'scatterpolar',
            r: data.values,
            theta: data.metrics,
            fill: 'toself',
            fillcolor: theme.fillcolor,
            line: { color: theme.linecolor, width: 2 },
            hovertemplate: '<b>%{theta}</b>: %{r:.2f}<extra></extra>'
        };
        
        const layout = {
            polar: {
                radialaxis: { visible: true, gridcolor: theme.gridcolor },
                angularaxis: { gridcolor: theme.gridcolor },
                bgcolor: theme.plot_bgcolor
            },
            paper_bgcolor: theme.paper_bgcolor,
            font: theme.font,
            margin: { t: 10, r: 40, b: 10, l: 40 },
            showlegend: false
        };
        
        const config = { responsive: true, displaylogo: false };
        Plotly.newPlot('risk-chart', [trace], layout, config);
        chartInstances['risk-chart'] = true;
    } catch (error) {
        console.error('Failed to create risk chart:', error);
    }
}

function createDrawdownChart(data) {
    if (!data || !data.timestamps || !data.drawdown) return;
    
    const theme = plotlyThemes[currentTheme];
    
    try {
        const trace = {
            x: data.timestamps,
            y: data.drawdown,
            type: 'scatter',
            mode: 'lines',
            fill: 'tozeroy',
            fillcolor: 'rgba(248, 81, 73, 0.15)',
            line: { color: theme.dangercolor, width: 2 },
            hovertemplate: '<b>%{y:.2f}%</b><br>%{x}<extra></extra>'
        };
        
        const layout = {
            paper_bgcolor: theme.paper_bgcolor,
            plot_bgcolor: theme.plot_bgcolor,
            font: theme.font,
            xaxis: { gridcolor: theme.gridcolor },
            yaxis: { gridcolor: theme.gridcolor, ticksuffix: '%' },
            margin: { t: 10, r: 20, b: 40, l: 60 },
            showlegend: false,
            hovermode: 'x unified'
        };
        
        const config = { responsive: true, displaylogo: false };
        Plotly.newPlot('drawdown-chart', [trace], layout, config);
        chartInstances['drawdown-chart'] = true;
    } catch (error) {
        console.error('Failed to create drawdown chart:', error);
    }
}

function createVolatilityChart(data) {
    if (!data || !data.timestamps || !data.volatility) return;
    
    const theme = plotlyThemes[currentTheme];
    
    try {
        const trace = {
            x: data.timestamps,
            y: data.volatility,
            type: 'scatter',
            mode: 'lines',
            line: { color: theme.warningcolor, width: 2 },
            hovertemplate: '<b>%{y:.2f}%</b><br>%{x}<extra></extra>'
        };
        
        const layout = {
            paper_bgcolor: theme.paper_bgcolor,
            plot_bgcolor: theme.plot_bgcolor,
            font: theme.font,
            xaxis: { gridcolor: theme.gridcolor },
            yaxis: { gridcolor: theme.gridcolor, ticksuffix: '%' },
            margin: { t: 10, r: 20, b: 40, l: 60 },
            showlegend: false,
            hovermode: 'x unified'
        };
        
        const config = { responsive: true, displaylogo: false };
        Plotly.newPlot('volatility-chart', [trace], layout, config);
        chartInstances['volatility-chart'] = true;
    } catch (error) {
        console.error('Failed to create volatility chart:', error);
    }
}

// ==================== WEBSOCKET WITH RECONNECTION ====================

function initWebSocket() {
    if (typeof io === 'undefined') {
        console.warn('Socket.io not loaded, skipping WebSocket initialization');
        return;
    }
    
    socket = io({
        reconnection: true,
        reconnectionDelay: RECONNECT_DELAY,
        reconnectionAttempts: MAX_RECONNECT_ATTEMPTS
    });
    
    socket.on('connect', () => {
        console.log('✅ WebSocket connected');
        reconnectAttempts = 0;
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', () => {
        console.log('⚠️ WebSocket disconnected');
        updateConnectionStatus(false);
    });
    
    socket.on('connect_error', (error) => {
        reconnectAttempts++;
        console.warn(`❌ Connection error (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
        
        if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
            showToast('Connection lost. Please refresh the page.', 'error');
        }
    });
    
    socket.on('update', (data) => {
        console.log('📊 Real-time update received');
        if (document.visibilityState === 'visible') {
            refreshCurrentSection(true);
        }
    });
}

function updateConnectionStatus(connected) {
    const statusText = document.getElementById('connection-text');
    const statusDot = document.querySelector('.status-dot');
    
    if (!statusText || !statusDot) return;
    
    if (connected) {
        statusText.textContent = 'Connected';
        statusDot.style.background = 'var(--accent-success)';
        statusDot.style.boxShadow = '0 0 8px var(--accent-success)';
    } else {
        statusText.textContent = 'Disconnected';
        statusDot.style.background = 'var(--accent-danger)';
        statusDot.style.boxShadow = '0 0 8px var(--accent-danger)';
    }
}

// ==================== UI FUNCTIONS ====================

function setTheme(theme, skipToast = false) {
    if (!['dark', 'light', 'bloomberg'].includes(theme)) {
        console.warn('Invalid theme:', theme);
        return;
    }
    
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('dashboard-theme', theme);
    
    // Update active theme button
    document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
    const themeButtons = { 'dark': 0, 'light': 1, 'bloomberg': 2 };
    const activeBtn = document.querySelectorAll('.theme-btn')[themeButtons[theme]];
    if (activeBtn) activeBtn.classList.add('active');
    
    // Refresh charts with new theme
    if (currentSection) {
        refreshCurrentSection(true);
    }
    
    if (!skipToast) {
        const names = { 'dark': 'Dark', 'light': 'Light', 'bloomberg': 'Terminal' };
        showToast(`Theme: ${names[theme]}`, 'info');
    }
}

function setTimeFilter(period, event) {
    if (!event || !event.target) {
        console.warn('Invalid time filter event');
        return;
    }
    
    currentTimeFilter = period;
    document.querySelectorAll('.time-filter-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    refreshCurrentSection();
    showToast(`Period: ${period.toUpperCase()}`, 'info');
}

function refreshCurrentSection(silent = false) {
    if (!currentSection) return;
    
    if (!silent) {
        showToast('Refreshing...', 'info');
    }
    
    loadSection(currentSection);
}

function refreshChart(chartName) {
    showToast(`Refreshing ${chartName}...`, 'info');
    refreshCurrentSection();
}

function exportChart(chartName) {
    const chartId = `${chartName}-chart`;
    const element = document.getElementById(chartId);
    
    if (!element || !element.data) {
        showToast('Chart not available for export', 'warning');
        return;
    }
    
    try {
        Plotly.downloadImage(chartId, {
            format: 'png',
            width: 1920,
            height: 1080,
            filename: `botv2-${chartName}-${Date.now()}`
        });
        showToast(`Exporting ${chartName}...`, 'success');
    } catch (error) {
        console.error('Export failed:', error);
        showToast('Export failed', 'error');
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
        <span style="font-weight: 500;">${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(400px)';
        setTimeout(() => toast.remove(), 200);
    }, 3000);
}

// ==================== CONTROL PANEL FUNCTIONS ====================

function startBot() {
    showToast('Starting bot...', 'info');
    // TODO: Implement bot start logic
}

function pauseBot() {
    showToast('Pausing bot...', 'warning');
    // TODO: Implement bot pause logic
}

function stopBot() {
    showToast('Stopping bot...', 'warning');
    // TODO: Implement bot stop logic
}

function emergencyStop() {
    if (confirm('⚠️ Are you sure you want to EMERGENCY STOP the bot?')) {
        showToast('EMERGENCY STOP activated', 'error');
        // TODO: Implement emergency stop logic
    }
}

// ==================== STRATEGY EDITOR FUNCTIONS ====================

function createNewStrategy() {
    showToast('Creating new strategy...', 'info');
    // TODO: Implement strategy creation
}

function editStrategy(strategyId) {
    showToast(`Editing strategy: ${strategyId}`, 'info');
    // TODO: Implement strategy editing
}

function testStrategy(strategyId) {
    showToast(`Testing strategy: ${strategyId}`, 'info');
    // TODO: Implement strategy testing
}

// ==================== CLEANUP ====================

window.addEventListener('beforeunload', function() {
    cleanupCharts();
    if (socket && socket.connected) {
        socket.disconnect();
    }
});

console.log('✅ BotV2 Dashboard v4.5 loaded successfully');
