// ==================== BotV2 Dashboard v4.0 - Enterprise Edition ====================
// Professional Single Page Application with enterprise-grade design
// Author: Juan Carlos Garcia
// Date: 22-01-2026
// Theme: Bloomberg Terminal + TradingView + Datadog inspired

// ==================== GLOBAL STATE ====================
let socket = null;
let currentTheme = 'dark';
let currentSection = 'dashboard';
let currentTimeFilter = '30d';
let chartInstances = {};
let dashboardData = {};

// Theme-specific Plotly configs
const plotlyThemes = {
    dark: {
        paper_bgcolor: 'rgba(10, 14, 26, 0)',
        plot_bgcolor: 'rgba(17, 24, 39, 0.5)',
        font: { color: '#f9fafb', family: 'Inter, sans-serif' },
        gridcolor: '#374151',
        linecolor: '#0ea5e9',
        fillcolor: 'rgba(14, 165, 233, 0.2)',
        markercolor: '#0ea5e9',
        successcolor: '#10b981',
        dangercolor: '#ef4444',
        warningcolor: '#f59e0b'
    },
    light: {
        paper_bgcolor: 'rgba(255, 255, 255, 0)',
        plot_bgcolor: 'rgba(249, 250, 251, 0.5)',
        font: { color: '#111827', family: 'Inter, sans-serif' },
        gridcolor: '#e5e7eb',
        linecolor: '#3b82f6',
        fillcolor: 'rgba(59, 130, 246, 0.2)',
        markercolor: '#3b82f6',
        successcolor: '#10b981',
        dangercolor: '#ef4444',
        warningcolor: '#f59e0b'
    },
    bloomberg: {
        paper_bgcolor: 'rgba(0, 0, 0, 0)',
        plot_bgcolor: 'rgba(10, 10, 10, 0.5)',
        font: { color: '#ff8800', family: 'Courier New, monospace' },
        gridcolor: '#333333',
        linecolor: '#ff8800',
        fillcolor: 'rgba(255, 136, 0, 0.2)',
        markercolor: '#ff8800',
        successcolor: '#00ff00',
        dangercolor: '#ff0000',
        warningcolor: '#ffff00'
    }
};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing BotV2 Dashboard v4.0 Enterprise Edition...');
    
    // Initialize WebSocket
    initWebSocket();
    
    // Setup menu click handlers
    setupMenuHandlers();
    
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('dashboard-theme') || 'dark';
    setTheme(savedTheme, true);
    
    // Load initial section (dashboard)
    loadSection('dashboard');
    
    // Start auto-refresh
    setInterval(() => refreshCurrentSection(), 30000);
    
    console.log('✅ Dashboard initialized successfully');
});

// ==================== MENU NAVIGATION ====================
function setupMenuHandlers() {
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            loadSection(section);
        });
    });
}

function loadSection(section) {
    console.log(`📋 Loading section: ${section}`);
    currentSection = section;
    
    // Update active menu item
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    const activeItem = document.querySelector(`[data-section="${section}"]`);
    if (activeItem) activeItem.classList.add('active');
    
    // Update page title with icon and badge
    const titles = {
        'dashboard': { icon: '📊', text: 'Dashboard', badge: 'Live' },
        'portfolio': { icon: '💰', text: 'Portfolio', badge: 'Pro' },
        'strategies': { icon: '🎯', text: 'Strategies', badge: 'AI' },
        'risk': { icon: '⚠️', text: 'Risk Analysis', badge: 'Pro' },
        'trades': { icon: '📈', text: 'Trade History', badge: 'Pro' },
        'settings': { icon: '⚙️', text: 'Settings', badge: 'Pro' }
    };
    
    const title = titles[section] || { icon: '', text: section, badge: 'Pro' };
    document.getElementById('page-title').innerHTML = `
        <span>${title.icon}</span>
        <span>${title.text}</span>
        <span class="page-badge">${title.badge}</span>
    `;
    
    // Fetch and render section content
    fetchSectionContent(section);
}

function fetchSectionContent(section) {
    const container = document.getElementById('main-container');
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <div class="loading-text">Loading ${section}...</div>
        </div>
    `;
    
    // Fetch data from API
    fetch(`/api/section/${section}`)
        .then(response => response.json())
        .then(data => {
            renderSection(section, data);
        })
        .catch(error => {
            console.error('Error loading section:', error);
            container.innerHTML = `
                <div style="text-align: center; padding: 50px; color: var(--accent-danger);">
                    <h2>❌ Error Loading Section</h2>
                    <p>${error.message}</p>
                </div>
            `;
        });
}

function renderSection(section, data) {
    const container = document.getElementById('main-container');
    
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
        case 'settings':
            renderSettings(data);
            break;
        default:
            container.innerHTML = '<p>Section not found</p>';
    }
}

// ==================== SECTION RENDERERS ====================

function renderDashboard(data) {
    const container = document.getElementById('main-container');
    container.innerHTML = `
        <!-- Time Filters -->
        <div class="time-filters">
            <button class="time-filter-btn" onclick="setTimeFilter('24h')">24H</button>
            <button class="time-filter-btn" onclick="setTimeFilter('7d')">7D</button>
            <button class="time-filter-btn active" onclick="setTimeFilter('30d')">30D</button>
            <button class="time-filter-btn" onclick="setTimeFilter('90d')">90D</button>
            <button class="time-filter-btn" onclick="setTimeFilter('ytd')">YTD</button>
            <button class="time-filter-btn" onclick="setTimeFilter('all')">All</button>
        </div>

        <!-- KPI Metrics -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">💰 Portfolio Value</div>
                    <div class="kpi-icon">💎</div>
                </div>
                <div class="kpi-value">${data.overview.equity}</div>
                <div class="kpi-change ${data.overview.daily_change >= 0 ? 'positive' : 'negative'}">
                    <span>${data.overview.daily_change >= 0 ? '↑' : '↓'}</span>
                    <span>${data.overview.daily_change_pct}% today</span>
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">📊 Total P&L</div>
                    <div class="kpi-icon">📉</div>
                </div>
                <div class="kpi-value">${data.overview.total_pnl}</div>
                <div class="kpi-change ${data.overview.total_return >= 0 ? 'positive' : 'negative'}">
                    <span>${data.overview.total_return >= 0 ? '↑' : '↓'}</span>
                    <span>${data.overview.total_return}%</span>
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">🎯 Win Rate</div>
                    <div class="kpi-icon">🏆</div>
                </div>
                <div class="kpi-value">${data.overview.win_rate}%</div>
                <div class="kpi-change">
                    <span>${data.overview.total_trades} trades</span>
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">⚡ Sharpe Ratio</div>
                    <div class="kpi-icon">📈</div>
                </div>
                <div class="kpi-value">${data.overview.sharpe_ratio}</div>
                <div class="kpi-change">
                    <span>DD: ${data.overview.max_drawdown}%</span>
                </div>
            </div>
        </div>

        <!-- Charts Grid -->
        <div class="charts-grid">
            <!-- Equity Curve Chart -->
            <div class="chart-card full-width">
                <div class="chart-header">
                    <div class="chart-title">📊 Equity Curve</div>
                    <div class="chart-actions">
                        <button class="chart-btn" onclick="refreshChart('equity')">🔄 Refresh</button>
                        <button class="chart-btn" onclick="exportChart('equity')">📅 Export</button>
                    </div>
                </div>
                <div id="equity-chart" class="chart-container"></div>
            </div>

            <!-- Strategy Performance -->
            <div class="chart-card">
                <div class="chart-header">
                    <div class="chart-title">🎯 Strategy Returns</div>
                    <div class="chart-actions">
                        <button class="chart-btn" onclick="refreshChart('strategies')">🔄</button>
                    </div>
                </div>
                <div id="strategies-chart" class="chart-container"></div>
            </div>

            <!-- Risk Metrics -->
            <div class="chart-card">
                <div class="chart-header">
                    <div class="chart-title">⚠️ Risk Metrics</div>
                    <div class="chart-actions">
                        <button class="chart-btn" onclick="refreshChart('risk')">🔄</button>
                    </div>
                </div>
                <div id="risk-chart" class="chart-container"></div>
            </div>
        </div>
    `;
    
    // Render charts with slight delay for DOM
    setTimeout(() => {
        createEquityChart(data.equity);
        createStrategiesChart(data.strategies);
        createRiskChart(data.risk);
    }, 100);
}

function renderPortfolio(data) {
    const container = document.getElementById('main-container');
    
    let positionsHTML = data.positions.map(pos => `
        <tr>
            <td><strong>${pos.symbol}</strong></td>
            <td>${pos.quantity}</td>
            <td>€${pos.entry_price.toFixed(2)}</td>
            <td>€${pos.current_price.toFixed(2)}</td>
            <td class="${pos.pnl >= 0 ? 'kpi-change positive' : 'kpi-change negative'}">
                €${pos.pnl.toFixed(2)} (${pos.pnl_pct.toFixed(2)}%)
            </td>
            <td><strong>€${pos.value.toFixed(2)}</strong></td>
        </tr>
    `).join('');
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Total Value</div>
                    <div class="kpi-icon">💰</div>
                </div>
                <div class="kpi-value">€${data.summary.total_value.toFixed(2)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Cash Available</div>
                    <div class="kpi-icon">💵</div>
                </div>
                <div class="kpi-value">€${data.summary.cash.toFixed(2)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Total P&L</div>
                    <div class="kpi-icon">📈</div>
                </div>
                <div class="kpi-value ${data.summary.total_pnl >= 0 ? 'kpi-change positive' : 'kpi-change negative'}">
                    €${data.summary.total_pnl.toFixed(2)}
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Open Positions</div>
                    <div class="kpi-icon">📋</div>
                </div>
                <div class="kpi-value">${data.positions.length}</div>
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
                <tbody>
                    ${positionsHTML}
                </tbody>
            </table>
        </div>
    `;
}

function renderStrategies(data) {
    const container = document.getElementById('main-container');
    
    let strategiesHTML = data.strategies.map(strat => `
        <tr>
            <td><strong>${strat.name}</strong></td>
            <td class="${strat.return >= 0 ? 'kpi-change positive' : 'kpi-change negative'}">
                ${strat.return.toFixed(2)}%
            </td>
            <td>${strat.sharpe.toFixed(2)}</td>
            <td>${strat.win_rate.toFixed(1)}%</td>
            <td>${strat.trades}</td>
            <td>
                <span class="badge ${strat.status === 'active' ? 'badge-success' : 'badge-warning'}">
                    ${strat.status}
                </span>
            </td>
        </tr>
    `).join('');
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Active Strategies</div>
                    <div class="kpi-icon">🎯</div>
                </div>
                <div class="kpi-value">${data.summary.active}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Best Performer</div>
                    <div class="kpi-icon">🏆</div>
                </div>
                <div class="kpi-value">${data.summary.best_strategy}</div>
                <div class="kpi-change positive">+${data.summary.best_return.toFixed(2)}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Avg Sharpe</div>
                    <div class="kpi-icon">⚡</div>
                </div>
                <div class="kpi-value">${data.summary.avg_sharpe.toFixed(2)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Total Trades</div>
                    <div class="kpi-icon">📊</div>
                </div>
                <div class="kpi-value">${data.summary.total_trades}</div>
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
                <tbody>
                    ${strategiesHTML}
                </tbody>
            </table>
        </div>
    `;
}

function renderRisk(data) {
    const container = document.getElementById('main-container');
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">VaR (95%)</div>
                    <div class="kpi-icon">⚠️</div>
                </div>
                <div class="kpi-value kpi-change negative">€${data.metrics.var_95.toFixed(2)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Max Drawdown</div>
                    <div class="kpi-icon">📉</div>
                </div>
                <div class="kpi-value kpi-change negative">${data.metrics.max_drawdown.toFixed(2)}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Volatility</div>
                    <div class="kpi-icon">🌊</div>
                </div>
                <div class="kpi-value">${data.metrics.volatility.toFixed(2)}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Sharpe Ratio</div>
                    <div class="kpi-icon">⚡</div>
                </div>
                <div class="kpi-value kpi-change positive">${data.metrics.sharpe.toFixed(2)}</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-card">
                <div class="chart-header">
                    <div class="chart-title">📉 Drawdown Chart</div>
                </div>
                <div id="drawdown-chart" class="chart-container"></div>
            </div>
            <div class="chart-card">
                <div class="chart-header">
                    <div class="chart-title">🌊 Volatility Over Time</div>
                </div>
                <div id="volatility-chart" class="chart-container"></div>
            </div>
        </div>
    `;
    
    setTimeout(() => {
        createDrawdownChart(data.drawdown);
        createVolatilityChart(data.volatility);
    }, 100);
}

function renderTrades(data) {
    const container = document.getElementById('main-container');
    
    let tradesHTML = data.trades.map(trade => `
        <tr>
            <td>${new Date(trade.timestamp).toLocaleString()}</td>
            <td>${trade.strategy}</td>
            <td><strong>${trade.symbol}</strong></td>
            <td>
                <span class="badge ${trade.action === 'BUY' ? 'badge-success' : 'badge-danger'}">
                    ${trade.action}
                </span>
            </td>
            <td>${trade.quantity}</td>
            <td>€${trade.price.toFixed(2)}</td>
            <td class="${trade.pnl >= 0 ? 'kpi-change positive' : 'kpi-change negative'}">
                €${trade.pnl.toFixed(2)}
            </td>
        </tr>
    `).join('');
    
    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Total Trades</div>
                    <div class="kpi-icon">📊</div>
                </div>
                <div class="kpi-value">${data.summary.total}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Winning Trades</div>
                    <div class="kpi-icon">🏆</div>
                </div>
                <div class="kpi-value kpi-change positive">${data.summary.winning}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Win Rate</div>
                    <div class="kpi-icon">🎯</div>
                </div>
                <div class="kpi-value">${data.summary.win_rate.toFixed(1)}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-title">Profit Factor</div>
                    <div class="kpi-icon">💰</div>
                </div>
                <div class="kpi-value">${data.summary.profit_factor.toFixed(2)}</div>
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
                <tbody>
                    ${tradesHTML}
                </tbody>
            </table>
        </div>
    `;
}

function renderSettings(data) {
    const container = document.getElementById('main-container');
    
    container.innerHTML = `
        <div class="data-table">
            <h3 style="padding: 20px; color: var(--text-primary); font-weight: 700;">⚙️ General Settings</h3>
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
                        <td><span class="badge ${data.settings.mode === 'paper' ? 'badge-warning' : 'badge-success'}">${data.settings.mode}</span></td>
                        <td>Current trading mode</td>
                    </tr>
                    <tr>
                        <td>Initial Capital</td>
                        <td>€${data.settings.initial_capital}</td>
                        <td>Starting portfolio value</td>
                    </tr>
                    <tr>
                        <td>Max Position Size</td>
                        <td>${data.settings.max_position_size}%</td>
                        <td>Maximum position as % of portfolio</td>
                    </tr>
                    <tr>
                        <td>Stop Loss</td>
                        <td>${data.settings.stop_loss}%</td>
                        <td>Default stop loss percentage</td>
                    </tr>
                    <tr>
                        <td>Risk Per Trade</td>
                        <td>${data.settings.risk_per_trade}%</td>
                        <td>Maximum risk per trade</td>
                    </tr>
                    <tr>
                        <td>Auto Refresh</td>
                        <td><span class="badge badge-success">${data.settings.auto_refresh ? 'Enabled' : 'Disabled'}</span></td>
                        <td>Automatic data refresh</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="data-table" style="margin-top: 24px;">
            <h3 style="padding: 20px; color: var(--text-primary); font-weight: 700;">💻 System Information</h3>
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
                        <td><span class="badge badge-info">${data.system.version}</span></td>
                    </tr>
                    <tr>
                        <td>Environment</td>
                        <td>${data.system.environment}</td>
                    </tr>
                    <tr>
                        <td>Uptime</td>
                        <td>${data.system.uptime}</td>
                    </tr>
                    <tr>
                        <td>Last Update</td>
                        <td>${data.system.last_update}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}

// ==================== CHART CREATORS - PROFESSIONAL ====================

function createEquityChart(data) {
    const theme = plotlyThemes[currentTheme];
    
    const trace = {
        x: data.timestamps,
        y: data.equity,
        type: 'scatter',
        mode: 'lines',
        name: 'Equity',
        line: { 
            color: theme.linecolor, 
            width: 3,
            shape: 'spline'
        },
        fill: 'tozeroy',
        fillcolor: theme.fillcolor,
        hovertemplate: '<b>%{y:€,.2f}</b><br>%{x}<extra></extra>'
    };
    
    const layout = {
        paper_bgcolor: theme.paper_bgcolor,
        plot_bgcolor: theme.plot_bgcolor,
        font: theme.font,
        xaxis: { 
            gridcolor: theme.gridcolor,
            showgrid: true,
            zeroline: false
        },
        yaxis: { 
            gridcolor: theme.gridcolor,
            tickprefix: '€',
            showgrid: true,
            zeroline: false
        },
        margin: { t: 20, r: 20, b: 40, l: 70 },
        showlegend: false,
        hovermode: 'x unified',
        transition: { duration: 500, easing: 'cubic-in-out' }
    };
    
    const config = { 
        responsive: true, 
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };
    
    Plotly.newPlot('equity-chart', [trace], layout, config);
}

function createStrategiesChart(data) {
    const theme = plotlyThemes[currentTheme];
    
    const colors = data.returns.map(v => v > 0 ? theme.successcolor : theme.dangercolor);
    
    const trace = {
        x: data.names,
        y: data.returns,
        type: 'bar',
        marker: { 
            color: colors,
            line: { width: 0 }
        },
        hovertemplate: '<b>%{x}</b><br>%{y:.2f}%<extra></extra>'
    };
    
    const layout = {
        paper_bgcolor: theme.paper_bgcolor,
        plot_bgcolor: theme.plot_bgcolor,
        font: theme.font,
        xaxis: { gridcolor: theme.gridcolor },
        yaxis: { 
            ticksuffix: '%', 
            gridcolor: theme.gridcolor,
            showgrid: true,
            zeroline: true,
            zerolinecolor: theme.gridcolor
        },
        margin: { t: 20, r: 20, b: 60, l: 60 },
        showlegend: false,
        transition: { duration: 500, easing: 'cubic-in-out' }
    };
    
    const config = { 
        responsive: true, 
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };
    
    Plotly.newPlot('strategies-chart', [trace], layout, config);
}

function createRiskChart(data) {
    const theme = plotlyThemes[currentTheme];
    
    const trace = {
        type: 'scatterpolar',
        r: data.values,
        theta: data.metrics,
        fill: 'toself',
        fillcolor: theme.fillcolor,
        line: { 
            color: theme.linecolor,
            width: 2
        },
        hovertemplate: '<b>%{theta}</b>: %{r:.2f}<extra></extra>'
    };
    
    const layout = {
        polar: {
            radialaxis: { 
                visible: true, 
                gridcolor: theme.gridcolor,
                showticklabels: true
            },
            angularaxis: { 
                gridcolor: theme.gridcolor
            },
            bgcolor: theme.plot_bgcolor
        },
        paper_bgcolor: theme.paper_bgcolor,
        font: theme.font,
        margin: { t: 20, r: 40, b: 20, l: 40 },
        showlegend: false,
        transition: { duration: 500, easing: 'cubic-in-out' }
    };
    
    const config = { 
        responsive: true, 
        displaylogo: false
    };
    
    Plotly.newPlot('risk-chart', [trace], layout, config);
}

function createDrawdownChart(data) {
    const theme = plotlyThemes[currentTheme];
    
    const trace = {
        x: data.timestamps,
        y: data.drawdown,
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy',
        fillcolor: 'rgba(239, 68, 68, 0.2)',
        line: { 
            color: theme.dangercolor, 
            width: 2,
            shape: 'spline'
        },
        hovertemplate: '<b>%{y:.2f}%</b><br>%{x}<extra></extra>'
    };
    
    const layout = {
        paper_bgcolor: theme.paper_bgcolor,
        plot_bgcolor: theme.plot_bgcolor,
        font: theme.font,
        xaxis: { gridcolor: theme.gridcolor },
        yaxis: { 
            gridcolor: theme.gridcolor, 
            ticksuffix: '%',
            showgrid: true
        },
        margin: { t: 20, r: 20, b: 40, l: 60 },
        showlegend: false,
        hovermode: 'x unified',
        transition: { duration: 500, easing: 'cubic-in-out' }
    };
    
    const config = { 
        responsive: true, 
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };
    
    Plotly.newPlot('drawdown-chart', [trace], layout, config);
}

function createVolatilityChart(data) {
    const theme = plotlyThemes[currentTheme];
    
    const trace = {
        x: data.timestamps,
        y: data.volatility,
        type: 'scatter',
        mode: 'lines',
        line: { 
            color: theme.warningcolor, 
            width: 3,
            shape: 'spline'
        },
        hovertemplate: '<b>%{y:.2f}%</b><br>%{x}<extra></extra>'
    };
    
    const layout = {
        paper_bgcolor: theme.paper_bgcolor,
        plot_bgcolor: theme.plot_bgcolor,
        font: theme.font,
        xaxis: { gridcolor: theme.gridcolor },
        yaxis: { 
            gridcolor: theme.gridcolor, 
            ticksuffix: '%',
            showgrid: true
        },
        margin: { t: 20, r: 20, b: 40, l: 60 },
        showlegend: false,
        hovermode: 'x unified',
        transition: { duration: 500, easing: 'cubic-in-out' }
    };
    
    const config = { 
        responsive: true, 
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };
    
    Plotly.newPlot('volatility-chart', [trace], layout, config);
}

// ==================== WEBSOCKET ====================

function initWebSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('✅ WebSocket connected');
        updateConnectionStatus(true);
        showToast('Connected to BotV2 Enterprise', 'success');
    });
    
    socket.on('disconnect', () => {
        console.log('❌ WebSocket disconnected');
        updateConnectionStatus(false);
        showToast('Disconnected from server', 'warning');
    });
    
    socket.on('update', (data) => {
        console.log('📊 Data update received');
        refreshCurrentSection();
    });
}

function updateConnectionStatus(connected) {
    const statusText = document.getElementById('connection-text');
    const statusDot = document.querySelector('.status-dot');
    
    if (connected) {
        statusText.textContent = 'Connected';
        statusDot.style.background = 'var(--accent-success)';
    } else {
        statusText.textContent = 'Disconnected';
        statusDot.style.background = 'var(--accent-danger)';
    }
}

// ==================== UI FUNCTIONS ====================

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('collapsed');
}

function setTheme(theme, skipToast = false) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('dashboard-theme', theme);
    
    // Update theme buttons
    document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
    const themeButtons = {
        'dark': 0,
        'light': 1,
        'bloomberg': 2
    };
    document.querySelectorAll('.theme-btn')[themeButtons[theme]]?.classList.add('active');
    
    // Refresh charts with new theme
    refreshCurrentSection();
    
    if (!skipToast) {
        const themeNames = {
            'dark': 'Dark Mode',
            'light': 'Light Mode',
            'bloomberg': 'Bloomberg Terminal'
        };
        showToast(`Theme: ${themeNames[theme]}`, 'info');
    }
}

function setTimeFilter(period) {
    currentTimeFilter = period;
    
    document.querySelectorAll('.time-filter-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    refreshCurrentSection();
    showToast(`Period: ${period.toUpperCase()}`, 'info');
}

function refreshCurrentSection() {
    loadSection(currentSection);
}

function refreshChart(chartName) {
    showToast(`Refreshing ${chartName} chart...`, 'info');
    refreshCurrentSection();
}

function exportChart(chartName) {
    const chartId = `${chartName}-chart`;
    const element = document.getElementById(chartId);
    if (element && element.data) {
        Plotly.downloadImage(chartId, {
            format: 'png',
            width: 1920,
            height: 1080,
            filename: `botv2-${chartName}-${Date.now()}`
        });
        showToast(`Exporting ${chartName} chart in ${currentTheme} theme...`, 'success');
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        info: '🟦',
        success: '✅',
        warning: '⚠️',
        error: '❌'
    };
    
    toast.innerHTML = `
        <span style="font-size: 20px;">${icons[type]}</span>
        <span style="font-weight: 600;">${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==================== WINDOW RESIZE - DEBOUNCED ====================
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        // Resize all Plotly charts
        document.querySelectorAll('[id$="-chart"]').forEach(el => {
            if (el.data) {
                Plotly.Plots.resize(el.id);
            }
        });
    }, 250);
});