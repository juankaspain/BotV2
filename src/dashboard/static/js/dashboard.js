// ==================== BotV2 Dashboard v4.4 - Ultra Professional ====================
// Fortune 500 Enterprise Edition - Strategy Editor Integration
// Inspired by: Stripe Dashboard, AWS Console, GitHub Enterprise, Linear
// Author: Juan Carlos Garcia
// Date: 23-01-2026
// Version: 4.4

// ==================== GLOBAL STATE ====================
let socket = null;
let currentTheme = 'dark';
let currentSection = 'dashboard';
let currentTimeFilter = '30d';
let chartInstances = {};
let dashboardData = {};

// Theme-specific Plotly configs - Professional palette
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
    console.log('🚀 BotV2 Dashboard v4.4 - Strategy Editor Edition');
    
    initWebSocket();
    setupMenuHandlers();
    
    const savedTheme = localStorage.getItem('dashboard-theme') || 'dark';
    setTheme(savedTheme, true);
    
    loadSection('dashboard');
    setInterval(() => refreshCurrentSection(), 30000);
    
    console.log('✅ Dashboard initialized');
});

// ==================== MENU NAVIGATION ====================
function setupMenuHandlers() {
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            if (section) {  // ✅ Validate section exists
                loadSection(section);
            }
        });
    });
}

function loadSection(section) {
    // ✅ Validate section parameter
    if (!section || section === 'null' || section === 'undefined') {
        console.error('Invalid section:', section);
        return;
    }
    
    console.log(`Loading: ${section}`);
    currentSection = section;
    
    // Update active menu
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    const activeItem = document.querySelector(`[data-section="${section}"]`);
    if (activeItem) activeItem.classList.add('active');
    
    // Update page title - CLEAN TEXT ONLY
    const titles = {
        'dashboard': 'Dashboard',
        'portfolio': 'Portfolio',
        'strategies': 'Strategies',
        'risk': 'Risk Analysis',
        'trades': 'Trade History',
        'settings': 'Settings'
    };
    
    document.getElementById('page-title').textContent = titles[section] || section;
    
    fetchSectionContent(section);
}

function fetchSectionContent(section) {
    const container = document.getElementById('main-container');
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <div class="loading-text">Loading...</div>
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
            // ✅ Validate data before rendering
            if (!data) {
                throw new Error('Empty response from server');
            }
            renderSection(section, data);
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = `
                <div style="text-align: center; padding: 50px; color: var(--accent-danger);">
                    <h2>Error Loading Section</h2>
                    <p>${error.message}</p>
                    <button onclick="loadSection('${section}')" style="margin-top: 20px; padding: 10px 20px; background: var(--accent-primary); color: white; border: none; border-radius: 6px; cursor: pointer;">Retry</button>
                </div>
            `;
        });
}

function renderSection(section, data) {
    switch(section) {
        case 'dashboard': renderDashboard(data); break;
        case 'portfolio': renderPortfolio(data); break;
        case 'strategies': renderStrategies(data); break;
        case 'risk': renderRisk(data); break;
        case 'trades': renderTrades(data); break;
        case 'settings': renderSettings(data); break;
        default:
            console.error('Unknown section:', section);
    }
}

// ==================== SECTION RENDERERS - CLEAN ====================

function renderDashboard(data) {
    const container = document.getElementById('main-container');
    
    // ✅ Safe accessors with defaults
    const overview = data.overview || {};
    const equity = data.equity || { timestamps: [], equity: [] };
    
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

        <!-- KPI Cards - CLEAN TEXT ONLY -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Portfolio Value</div>
                <div class="kpi-value">${overview.equity || 'N/A'}</div>
                <div class="kpi-change ${(overview.daily_change || 0) >= 0 ? 'positive' : 'negative'}">
                    ${(overview.daily_change || 0) >= 0 ? '↑' : '↓'} ${overview.daily_change || 0}% today
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-title">Total P&L</div>
                <div class="kpi-value">${overview.total_pnl || 'N/A'}</div>
                <div class="kpi-change ${(overview.total_return || 0) >= 0 ? 'positive' : 'negative'}">
                    ${(overview.total_return || 0) >= 0 ? '↑' : '↓'} ${overview.total_return || 0}%
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-title">Win Rate</div>
                <div class="kpi-value">${overview.win_rate || 'N/A'}%</div>
                <div class="kpi-change">
                    ${overview.total_trades || 0} trades
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-title">Sharpe Ratio</div>
                <div class="kpi-value">${overview.sharpe_ratio || 'N/A'}</div>
                <div class="kpi-change">
                    DD: ${overview.max_drawdown || 'N/A'}%
                </div>
            </div>
        </div>

        <!-- Charts Grid - CLEAN TITLES -->
        <div class="charts-grid">
            <div class="chart-card full-width">
                <div class="chart-header">
                    <div class="chart-title">Equity Curve</div>
                    <div class="chart-actions">
                        <button class="chart-btn" onclick="refreshChart('equity')">Refresh</button>
                        <button class="chart-btn" onclick="exportChart('equity')">Export</button>
                    </div>
                </div>
                <div id="equity-chart" class="chart-container"></div>
            </div>

            <div class="chart-card">
                <div class="chart-header">
                    <div class="chart-title">Strategy Returns</div>
                    <div class="chart-actions">
                        <button class="chart-btn" onclick="refreshChart('strategies')">Refresh</button>
                    </div>
                </div>
                <div id="strategies-chart" class="chart-container"></div>
            </div>

            <div class="chart-card">
                <div class="chart-header">
                    <div class="chart-title">Risk Metrics</div>
                    <div class="chart-actions">
                        <button class="chart-btn" onclick="refreshChart('risk')">Refresh</button>
                    </div>
                </div>
                <div id="risk-chart" class="chart-container"></div>
            </div>
        </div>
    `;
    
    setTimeout(() => {
        if (equity.timestamps && equity.equity) {
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
    
    // ✅ Safe accessors
    const summary = data.summary || {};
    const positions = data.positions || [];
    
    let positionsHTML = positions.map(pos => `
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
    `).join('');
    
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
                <tbody>
                    ${positionsHTML || '<tr><td colspan="6">No positions</td></tr>'}
                </tbody>
            </table>
        </div>
    `;
}

function renderStrategies(data) {
    const container = document.getElementById('main-container');
    
    // ✅ Safe accessors with validation
    const summary = data.summary || {};
    const strategies = Array.isArray(data.strategies) ? data.strategies : [];
    
    let strategiesHTML = strategies.length > 0 ? strategies.map(strat => `
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
    `).join('') : '<tr><td colspan="6">No strategies available</td></tr>';
    
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
                <tbody>
                    ${strategiesHTML}
                </tbody>
            </table>
        </div>
    `;
}

function renderRisk(data) {
    const container = document.getElementById('main-container');
    
    // ✅ Safe accessors
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
    
    // ✅ Safe accessors
    const summary = data.summary || {};
    const trades = Array.isArray(data.trades) ? data.trades : [];
    
    let tradesHTML = trades.length > 0 ? trades.map(trade => `
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
    `).join('') : '<tr><td colspan="7">No trades available</td></tr>';
    
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
                <tbody>
                    ${tradesHTML}
                </tbody>
            </table>
        </div>
    `;
}

function renderSettings(data) {
    const container = document.getElementById('main-container');
    
    // ✅ Safe accessors
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
                        <td><span class="badge badge-info">${system.version || '4.4'}</span></td>
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
                        <td>${system.last_update || 'N/A'}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}

// ==================== CHART CREATORS - PROFESSIONAL ====================

function createEquityChart(data) {
    if (!data || !data.timestamps || !data.equity) {
        console.warn('Invalid equity data');
        return;
    }
    
    const theme = plotlyThemes[currentTheme];
    
    const trace = {
        x: data.timestamps,
        y: data.equity,
        type: 'scatter',
        mode: 'lines',
        name: 'Equity',
        line: { 
            color: theme.linecolor, 
            width: 2
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
        margin: { t: 10, r: 20, b: 40, l: 70 },
        showlegend: false,
        hovermode: 'x unified'
    };
    
    const config = { 
        responsive: true, 
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };
    
    Plotly.newPlot('equity-chart', [trace], layout, config);
}

function createStrategiesChart(data) {
    if (!data || !data.names || !data.returns) {
        console.warn('Invalid strategies data');
        return;
    }
    
    const theme = plotlyThemes[currentTheme];
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
        yaxis: { 
            ticksuffix: '%', 
            gridcolor: theme.gridcolor,
            showgrid: true,
            zeroline: true
        },
        margin: { t: 10, r: 20, b: 60, l: 60 },
        showlegend: false
    };
    
    const config = { 
        responsive: true, 
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };
    
    Plotly.newPlot('strategies-chart', [trace], layout, config);
}

function createRiskChart(data) {
    if (!data || !data.values || !data.metrics) {
        console.warn('Invalid risk data');
        return;
    }
    
    const theme = plotlyThemes[currentTheme];
    
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
            radialaxis: { 
                visible: true, 
                gridcolor: theme.gridcolor
            },
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
}

function createDrawdownChart(data) {
    if (!data || !data.timestamps || !data.drawdown) return;
    
    const theme = plotlyThemes[currentTheme];
    
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
}

function createVolatilityChart(data) {
    if (!data || !data.timestamps || !data.volatility) return;
    
    const theme = plotlyThemes[currentTheme];
    
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
}

// ==================== WEBSOCKET ====================

function initWebSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('✅ WebSocket connected');
        updateConnectionStatus(true);
        showToast('Connected', 'success');
    });
    
    socket.on('disconnect', () => {
        console.log('❌ Disconnected');
        updateConnectionStatus(false);
        showToast('Disconnected', 'warning');
    });
    
    socket.on('update', (data) => {
        console.log('📊 Update received');
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

function setTheme(theme, skipToast = false) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('dashboard-theme', theme);
    
    document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
    const themeButtons = { 'dark': 0, 'light': 1, 'bloomberg': 2 };
    document.querySelectorAll('.theme-btn')[themeButtons[theme]]?.classList.add('active');
    
    refreshCurrentSection();
    
    if (!skipToast) {
        const names = { 'dark': 'Dark', 'light': 'Light', 'bloomberg': 'Terminal' };
        showToast(`Theme: ${names[theme]}`, 'info');
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
    if (currentSection) {
        loadSection(currentSection);
    }
}

function refreshChart(chartName) {
    showToast(`Refreshing ${chartName}...`, 'info');
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
        showToast(`Exporting ${chartName}...`, 'success');
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span style="font-weight: 500;">${message}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.2s ease reverse';
        setTimeout(() => toast.remove(), 200);
    }, 3000);
}

// ==================== RESIZE HANDLER ====================
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        document.querySelectorAll('[id$="-chart"]').forEach(el => {
            if (el.data) Plotly.Plots.resize(el.id);
        });
    }, 250);
});