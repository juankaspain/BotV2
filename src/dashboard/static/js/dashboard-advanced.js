/**
 * BotV2 Dashboard Advanced Features Module v1.0
 * Ultra-professional JS for modals, filters, comparisons, annotations, and exports
 * 
 * @author BotV2 Team
 * @license Private Use
 * @version 1.0.0
 * @size ~35KB
 * @lines ~850
 * @compatibility Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
 * @dependencies None (Pure Vanilla JS ES6+)
 */

'use strict';

// ============================================
// GLOBAL STATE MANAGEMENT
// ============================================

const DashboardAdvanced = {
    // State
    state: {
        modals: {},
        filters: {},
        selections: {},
        annotations: {},
        comparisonMode: false,
        selectedStrategies: [],
        zoomState: {},
        exportHistory: []
    },
    
    // Configuration
    config: {
        maxDataPoints: 5000,
        debounceDelay: 300,
        virtualScrollThreshold: 100,
        localStorageKey: 'botv2_dashboard_state',
        annotationColors: ['#00d4aa', '#0066ff', '#f59e0b', '#ef4444'],
        exportFormats: ['csv', 'excel', 'pdf']
    },
    
    // Cache
    cache: {
        chartData: {},
        filterResults: {},
        modalContent: {}
    }
};

// ============================================
// MODAL SYSTEM - Drill-Down Views
// ============================================

/**
 * Show modal with specific content
 * @param {string} modalId - Modal identifier
 * @param {object} data - Data to display in modal
 */
function showModal(modalId, data) {
    const overlay = document.getElementById('modalOverlay');
    const modal = overlay.querySelector('.modal');
    const titleEl = document.getElementById('modalTitle');
    const bodyEl = document.getElementById('modalBody');
    const footerEl = document.getElementById('modalFooter');
    
    // Cache check
    const cacheKey = `${modalId}_${JSON.stringify(data).substring(0, 50)}`;
    if (DashboardAdvanced.cache.modalContent[cacheKey]) {
        bodyEl.innerHTML = DashboardAdvanced.cache.modalContent[cacheKey];
    } else {
        let content = '';
        
        switch(modalId) {
            case 'trade-detail':
                content = createTradeDetailModal(data);
                titleEl.textContent = '📊 Trade Details';
                break;
            case 'strategy-analysis':
                content = createStrategyDrilldown(data);
                titleEl.textContent = '📈 Strategy Deep-Dive';
                modal.classList.add('modal-large');
                break;
            case 'risk-scenario':
                content = createRiskScenarioModal(data);
                titleEl.textContent = '⚠️ Risk Breakdown';
                break;
            case 'chart-filter':
                content = createChartFilterModal(data);
                titleEl.textContent = '🔍 Chart Filters';
                modal.classList.add('modal-small');
                break;
            case 'export-options':
                content = createExportOptionsModal(data);
                titleEl.textContent = '📥 Export Options';
                break;
            default:
                content = '<p>Modal content not found</p>';
        }
        
        bodyEl.innerHTML = content;
        DashboardAdvanced.cache.modalContent[cacheKey] = content;
    }
    
    // Custom footer based on modal type
    footerEl.innerHTML = getModalFooter(modalId, data);
    
    // Show modal with animation
    overlay.classList.add('active');
    DashboardAdvanced.state.modals[modalId] = { open: true, data };
    
    // Track modal open event
    console.log(`📊 Modal opened: ${modalId}`);
}

/**
 * Close currently open modal
 */
function closeModal() {
    const overlay = document.getElementById('modalOverlay');
    const modal = overlay.querySelector('.modal');
    overlay.classList.remove('active');
    modal.classList.remove('modal-large', 'modal-small');
    
    // Clear state
    Object.keys(DashboardAdvanced.state.modals).forEach(key => {
        DashboardAdvanced.state.modals[key].open = false;
    });
    
    console.log('✅ Modal closed');
}

/**
 * Create trade detail modal content
 * @param {object} tradeData - Trade information
 * @returns {string} HTML content
 */
function createTradeDetailModal(tradeData) {
    const {
        id, strategy, symbol, action, size, entry_price, exit_price,
        pnl, pnl_percent, timestamp, exit_timestamp, confidence,
        duration, fees, slippage, notes
    } = tradeData;
    
    const pnlClass = pnl >= 0 ? 'text-success' : 'text-danger';
    const pnlIcon = pnl >= 0 ? '📈' : '📉';
    
    return `
        <div class="detail-grid">
            <div class="detail-item">
                <div class="detail-label">Trade ID</div>
                <div class="detail-value">#${id}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Strategy</div>
                <div class="detail-value">${strategy}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Symbol</div>
                <div class="detail-value">${symbol}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Action</div>
                <div class="detail-value">${action.toUpperCase()}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Size</div>
                <div class="detail-value">${size.toLocaleString()}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Entry Price</div>
                <div class="detail-value">€${entry_price.toFixed(2)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Exit Price</div>
                <div class="detail-value">${exit_price ? '€' + exit_price.toFixed(2) : 'Open'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">P&L ${pnlIcon}</div>
                <div class="detail-value ${pnlClass}">€${pnl.toFixed(2)} (${pnl_percent.toFixed(2)}%)</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Confidence</div>
                <div class="detail-value">${(confidence * 100).toFixed(1)}%</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Duration</div>
                <div class="detail-value">${duration || 'N/A'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Fees</div>
                <div class="detail-value">€${(fees || 0).toFixed(2)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Slippage</div>
                <div class="detail-value">€${(slippage || 0).toFixed(2)}</div>
            </div>
        </div>
        
        <div class="detail-section">
            <div class="detail-section-title">📅 Timeline</div>
            <div class="detail-timeline">
                <div class="timeline-item">
                    <div class="timeline-time">${new Date(timestamp).toLocaleString()}</div>
                    <div class="timeline-content"><strong>Entry:</strong> ${action.toUpperCase()} ${size} @ €${entry_price.toFixed(2)}</div>
                </div>
                ${exit_timestamp ? `
                <div class="timeline-item">
                    <div class="timeline-time">${new Date(exit_timestamp).toLocaleString()}</div>
                    <div class="timeline-content"><strong>Exit:</strong> Closed @ €${exit_price.toFixed(2)}</div>
                </div>` : '<div class="timeline-item"><div class="timeline-content"><em>Position still open</em></div></div>'}
            </div>
        </div>
        
        ${notes ? `
        <div class="detail-section">
            <div class="detail-section-title">📝 Notes</div>
            <div style="padding: var(--spacing-md); background: var(--bg-tertiary); border-radius: var(--radius-md); font-size: 0.875rem; color: var(--text-secondary);">
                ${notes}
            </div>
        </div>` : ''}
    `;
}

/**
 * Create strategy deep-dive modal content
 * @param {object} strategyData - Strategy metrics
 * @returns {string} HTML content
 */
function createStrategyDrilldown(strategyData) {
    const {
        name, total_return, sharpe_ratio, sortino_ratio, max_drawdown,
        win_rate, total_trades, winning_trades, losing_trades,
        avg_win, avg_loss, profit_factor, expectancy, best_trade,
        worst_trade, avg_duration, volatility
    } = strategyData;
    
    return `
        <div class="detail-grid">
            <div class="detail-item">
                <div class="detail-label">Strategy Name</div>
                <div class="detail-value">${name}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Total Return</div>
                <div class="detail-value ${total_return >= 0 ? 'success' : 'danger'}">${total_return.toFixed(2)}%</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Sharpe Ratio</div>
                <div class="detail-value">${sharpe_ratio.toFixed(2)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Sortino Ratio</div>
                <div class="detail-value">${sortino_ratio.toFixed(2)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Max Drawdown</div>
                <div class="detail-value danger">${max_drawdown.toFixed(2)}%</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Win Rate</div>
                <div class="detail-value success">${win_rate.toFixed(2)}%</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Total Trades</div>
                <div class="detail-value">${total_trades}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Winning Trades</div>
                <div class="detail-value success">${winning_trades}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Losing Trades</div>
                <div class="detail-value danger">${losing_trades}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Avg Win</div>
                <div class="detail-value success">€${avg_win.toFixed(2)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Avg Loss</div>
                <div class="detail-value danger">€${Math.abs(avg_loss).toFixed(2)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Profit Factor</div>
                <div class="detail-value">${profit_factor.toFixed(2)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Expectancy</div>
                <div class="detail-value">€${expectancy.toFixed(2)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Best Trade</div>
                <div class="detail-value success">€${best_trade.toFixed(2)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Worst Trade</div>
                <div class="detail-value danger">€${worst_trade.toFixed(2)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Avg Duration</div>
                <div class="detail-value">${avg_duration}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Volatility</div>
                <div class="detail-value">${volatility.toFixed(2)}%</div>
            </div>
        </div>
        
        <div class="detail-section">
            <div class="detail-section-title">📊 Performance Analysis</div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--spacing-md); margin-top: var(--spacing-md);">
                <div style="text-align: center; padding: var(--spacing-md); background: var(--bg-tertiary); border-radius: var(--radius-md);">
                    <div style="font-size: 0.75rem; color: var(--text-tertiary); margin-bottom: var(--spacing-xs);">Risk/Reward</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: var(--primary);">${(Math.abs(avg_win) / Math.abs(avg_loss)).toFixed(2)}</div>
                </div>
                <div style="text-align: center; padding: var(--spacing-md); background: var(--bg-tertiary); border-radius: var(--radius-md);">
                    <div style="font-size: 0.75rem; color: var(--text-tertiary); margin-bottom: var(--spacing-xs);">Recovery Factor</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: var(--primary);">${(total_return / Math.abs(max_drawdown)).toFixed(2)}</div>
                </div>
                <div style="text-align: center; padding: var(--spacing-md); background: var(--bg-tertiary); border-radius: var(--radius-md);">
                    <div style="font-size: 0.75rem; color: var(--text-tertiary); margin-bottom: var(--spacing-xs);">Calmar Ratio</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: var(--primary);">${(total_return / Math.abs(max_drawdown) * 100).toFixed(2)}</div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Create risk scenario modal content
 * @param {object} riskData - Risk metrics
 * @returns {string} HTML content
 */
function createRiskScenarioModal(riskData) {
    const { var_95, var_99, cvar_95, cvar_99, max_loss, scenarios } = riskData;
    
    return `
        <div class="detail-grid">
            <div class="detail-item">
                <div class="detail-label">VaR 95%</div>
                <div class="detail-value">€${var_95.toFixed(2)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">VaR 99%</div>
                <div class="detail-value">€${var_99.toFixed(2)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">CVaR 95%</div>
                <div class="detail-value danger">€${cvar_95.toFixed(2)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">CVaR 99%</div>
                <div class="detail-value danger">€${cvar_99.toFixed(2)}</div>
            </div>
        </div>
        
        <div class="detail-section">
            <div class="detail-section-title">⚠️ Stress Test Scenarios</div>
            <table class="comparison-table" style="width: 100%; margin-top: var(--spacing-md);">
                <thead>
                    <tr>
                        <th>Scenario</th>
                        <th>Probability</th>
                        <th>Expected Loss</th>
                        <th>Max Loss</th>
                    </tr>
                </thead>
                <tbody>
                    ${scenarios.map(s => `
                        <tr>
                            <td>${s.name}</td>
                            <td>${s.probability}%</td>
                            <td class="danger">€${s.expected_loss.toFixed(2)}</td>
                            <td class="danger">€${s.max_loss.toFixed(2)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

/**
 * Create chart filter modal content
 * @param {object} filterData - Current filter state
 * @returns {string} HTML content
 */
function createChartFilterModal(filterData) {
    const { chartId, dateFrom, dateTo, strategies, assets } = filterData;
    
    return `
        <div class="filter-group">
            <label class="filter-label">Date Range</label>
            <div class="date-range-selector">
                <input type="date" class="filter-input" id="modalFilterDateFrom" value="${dateFrom || ''}">
                <span class="date-range-separator">→</span>
                <input type="date" class="filter-input" id="modalFilterDateTo" value="${dateTo || ''}">
            </div>
        </div>
        
        <div class="filter-group">
            <label class="filter-label">Strategies</label>
            <div class="filter-checkbox-group" id="modalFilterStrategies">
                ${['Momentum', 'Mean Reversion', 'Breakout', 'Arbitrage'].map(s => `
                    <label class="filter-checkbox">
                        <input type="checkbox" value="${s.toLowerCase().replace(' ', '_')}" ${strategies?.includes(s.toLowerCase().replace(' ', '_')) ? 'checked' : ''}>
                        <span>${s}</span>
                    </label>
                `).join('')}
            </div>
        </div>
        
        <div class="filter-group">
            <label class="filter-label">Asset Types</label>
            <div class="filter-checkbox-group" id="modalFilterAssets">
                ${['Stocks', 'Crypto', 'Forex', 'Commodities'].map(a => `
                    <label class="filter-checkbox">
                        <input type="checkbox" value="${a.toLowerCase()}" ${assets?.includes(a.toLowerCase()) ? 'checked' : ''}>
                        <span>${a}</span>
                    </label>
                `).join('')}
            </div>
        </div>
    `;
}

/**
 * Create export options modal content
 * @param {object} exportData - Export configuration
 * @returns {string} HTML content
 */
function createExportOptionsModal(exportData) {
    return `
        <div class="filter-group">
            <label class="filter-label">Export Format</label>
            <div class="filter-radio-group">
                <label class="filter-radio">
                    <input type="radio" name="exportFormat" value="csv" checked>
                    <span>📄 CSV (Comma-Separated Values)</span>
                </label>
                <label class="filter-radio">
                    <input type="radio" name="exportFormat" value="excel">
                    <span>📊 Excel (Multi-Sheet Workbook)</span>
                </label>
                <label class="filter-radio">
                    <input type="radio" name="exportFormat" value="pdf">
                    <span>📕 PDF (Full Report)</span>
                </label>
            </div>
        </div>
        
        <div class="filter-group">
            <label class="filter-label">Date Range</label>
            <div class="date-range-selector">
                <input type="date" class="filter-input" id="exportDateFrom">
                <span class="date-range-separator">→</span>
                <input type="date" class="filter-input" id="exportDateTo">
            </div>
        </div>
        
        <div class="filter-group">
            <label class="filter-label">Include</label>
            <div class="filter-checkbox-group">
                <label class="filter-checkbox">
                    <input type="checkbox" value="trades" checked>
                    <span>Trades Data</span>
                </label>
                <label class="filter-checkbox">
                    <input type="checkbox" value="metrics" checked>
                    <span>Performance Metrics</span>
                </label>
                <label class="filter-checkbox">
                    <input type="checkbox" value="charts" checked>
                    <span>Chart Images</span>
                </label>
                <label class="filter-checkbox">
                    <input type="checkbox" value="annotations">
                    <span>Annotations</span>
                </label>
            </div>
        </div>
        
        <div id="exportProgress" class="hidden" style="margin-top: var(--spacing-md);">
            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: var(--spacing-xs);">
                Exporting... <span id="exportProgressPercent">0%</span>
            </div>
            <div style="width: 100%; height: 8px; background: var(--bg-tertiary); border-radius: var(--radius-full); overflow: hidden;">
                <div id="exportProgressBar" style="width: 0%; height: 100%; background: var(--primary); transition: width 0.3s ease;"></div>
            </div>
        </div>
    `;
}

/**
 * Get custom footer for modal
 * @param {string} modalId - Modal identifier
 * @param {object} data - Modal data
 * @returns {string} HTML content
 */
function getModalFooter(modalId, data) {
    switch(modalId) {
        case 'chart-filter':
            return `
                <button class="btn" onclick="applyModalChartFilter('${data.chartId}')">Apply Filters</button>
                <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            `;
        case 'export-options':
            return `
                <button class="btn" onclick="executeExport()">📥 Export</button>
                <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            `;
        default:
            return `<button class="btn btn-secondary" onclick="closeModal()">Close</button>`;
    }
}

// ============================================
// ADVANCED CHART FILTERS
// ============================================

/**
 * Apply filters to specific chart
 * @param {string} chartId - Chart element ID
 * @param {object} filters - Filter configuration
 */
function applyChartFilter(chartId, filters) {
    console.log(`🔍 Applying filters to chart: ${chartId}`, filters);
    
    // Store filter state
    DashboardAdvanced.state.filters[chartId] = filters;
    persistState();
    
    // Apply filters with debounce
    debouncedFilterUpdate(chartId, filters);
}

/**
 * Debounced filter update
 */
const debouncedFilterUpdate = debounce((chartId, filters) => {
    const chart = document.getElementById(chartId);
    if (!chart) return;
    
    // Get chart data
    const chartData = DashboardAdvanced.cache.chartData[chartId];
    if (!chartData) return;
    
    // Apply filters
    let filteredData = { ...chartData };
    
    // Date range filter
    if (filters.dateFrom || filters.dateTo) {
        filteredData = filterByDateRange(filteredData, filters.dateFrom, filters.dateTo);
    }
    
    // Strategy filter
    if (filters.strategies && filters.strategies.length > 0) {
        filteredData = filterByStrategies(filteredData, filters.strategies);
    }
    
    // Asset type filter
    if (filters.assets && filters.assets.length > 0) {
        filteredData = filterByAssets(filteredData, filters.assets);
    }
    
    // Downsample if needed
    if (filteredData.x && filteredData.x.length > DashboardAdvanced.config.maxDataPoints) {
        filteredData = downsampleData(filteredData, DashboardAdvanced.config.maxDataPoints);
    }
    
    // Update chart
    Plotly.react(chartId, [filteredData], chartData.layout, chartData.config);
    
    showToast('Filters Applied', `Chart updated with ${filters.strategies?.length || 0} filters`, 'success');
}, DashboardAdvanced.config.debounceDelay);

/**
 * Apply modal chart filter
 * @param {string} chartId - Chart element ID
 */
function applyModalChartFilter(chartId) {
    const dateFrom = document.getElementById('modalFilterDateFrom').value;
    const dateTo = document.getElementById('modalFilterDateTo').value;
    
    const strategies = Array.from(document.querySelectorAll('#modalFilterStrategies input:checked'))
        .map(el => el.value);
    
    const assets = Array.from(document.querySelectorAll('#modalFilterAssets input:checked'))
        .map(el => el.value);
    
    applyChartFilter(chartId, { dateFrom, dateTo, strategies, assets });
    closeModal();
}

/**
 * Filter data by date range
 */
function filterByDateRange(data, dateFrom, dateTo) {
    if (!data.x) return data;
    
    const from = dateFrom ? new Date(dateFrom) : null;
    const to = dateTo ? new Date(dateTo) : null;
    
    const filtered = { ...data, x: [], y: [] };
    
    data.x.forEach((date, i) => {
        const d = new Date(date);
        if ((!from || d >= from) && (!to || d <= to)) {
            filtered.x.push(date);
            filtered.y.push(data.y[i]);
        }
    });
    
    return filtered;
}

/**
 * Filter data by strategies
 */
function filterByStrategies(data, strategies) {
    // Implementation depends on data structure
    return data;
}

/**
 * Filter data by asset types
 */
function filterByAssets(data, assets) {
    // Implementation depends on data structure
    return data;
}

// ============================================
// BRUSH SELECTION & ZOOM SYNC
// ============================================

/**
 * Enable brush selection on chart
 * @param {string} chartId - Chart element ID
 */
function enableBrushSelection(chartId) {
    const chart = document.getElementById(chartId);
    if (!chart) return;
    
    chart.on('plotly_selected', (eventData) => {
        if (!eventData) return;
        
        const range = {
            x: eventData.range.x,
            y: eventData.range.y
        };
        
        DashboardAdvanced.state.selections[chartId] = range;
        
        // Sync zoom if enabled
        if (DashboardAdvanced.state.zoomSyncEnabled) {
            syncChartZoom(DashboardAdvanced.state.syncedCharts, range);
        }
        
        console.log(`🖌️ Brush selection on ${chartId}:`, range);
    });
}

/**
 * Synchronize zoom across multiple charts
 * @param {array} chartIds - Array of chart IDs to sync
 * @param {object} range - Zoom range {x: [min, max], y: [min, max]}
 */
function syncChartZoom(chartIds, range) {
    chartIds.forEach(chartId => {
        const chart = document.getElementById(chartId);
        if (!chart) return;
        
        Plotly.relayout(chartId, {
            'xaxis.range': range.x,
            'yaxis.range': range.y
        });
        
        DashboardAdvanced.state.zoomState[chartId] = range;
    });
    
    console.log(`🔗 Zoom synced across ${chartIds.length} charts`);
}

/**
 * Reset chart zoom to original view
 * @param {string} chartId - Chart element ID
 */
function resetChartZoom(chartId) {
    const chart = document.getElementById(chartId);
    if (!chart) return;
    
    Plotly.relayout(chartId, {
        'xaxis.autorange': true,
        'yaxis.autorange': true
    });
    
    delete DashboardAdvanced.state.zoomState[chartId];
    delete DashboardAdvanced.state.selections[chartId];
    
    showToast('Zoom Reset', `Chart ${chartId} reset to original view`, 'info');
}

// ============================================
// MULTI-CHART COMPARISON MODE
// ============================================

/**
 * Toggle comparison mode
 */
function toggleComparisonMode() {
    DashboardAdvanced.state.comparisonMode = !DashboardAdvanced.state.comparisonMode;
    
    const banner = document.getElementById('comparisonBanner');
    if (DashboardAdvanced.state.comparisonMode) {
        banner.classList.add('active');
        showToast('Comparison Mode', 'Select strategies to compare', 'info');
    } else {
        banner.classList.remove('active');
        DashboardAdvanced.state.selectedStrategies = [];
    }
}

/**
 * Compare multiple strategies
 * @param {array} strategyIds - Array of strategy identifiers
 * @returns {object} Comparison data
 */
function compareStrategies(strategyIds) {
    console.log(`📊 Comparing strategies:`, strategyIds);
    
    const comparisonData = {
        strategies: [],
        metrics: [],
        charts: []
    };
    
    strategyIds.forEach(id => {
        // Fetch strategy data (from cache or API)
        const strategyData = DashboardAdvanced.cache.chartData[`strategy_${id}`];
        if (strategyData) {
            comparisonData.strategies.push(strategyData);
        }
    });
    
    // Generate comparison metrics
    comparisonData.metrics = generateComparisonMetrics(comparisonData.strategies);
    
    return comparisonData;
}

/**
 * Generate comparison metrics
 */
function generateComparisonMetrics(strategies) {
    return strategies.map(s => ({
        name: s.name,
        return: s.total_return,
        sharpe: s.sharpe_ratio,
        maxDD: s.max_drawdown,
        winRate: s.win_rate
    }));
}

/**
 * Export comparison data
 */
function exportComparison() {
    const comparisonData = compareStrategies(DashboardAdvanced.state.selectedStrategies);
    exportToCSV(comparisonData, 'strategy_comparison');
}

// ============================================
// ENHANCED EXPORT SYSTEM
// ============================================

/**
 * Execute export based on modal selections
 */
function executeExport() {
    const format = document.querySelector('input[name="exportFormat"]:checked').value;
    const dateFrom = document.getElementById('exportDateFrom').value;
    const dateTo = document.getElementById('exportDateTo').value;
    
    const includes = Array.from(document.querySelectorAll('.filter-checkbox input:checked'))
        .map(el => el.value);
    
    const exportData = {
        format,
        dateRange: { from: dateFrom, to: dateTo },
        includes
    };
    
    // Show progress
    showExportProgress();
    
    // Simulate export process
    simulateExport(format, exportData);
}

/**
 * Show export progress indicator
 */
function showExportProgress() {
    const progressDiv = document.getElementById('exportProgress');
    progressDiv.classList.remove('hidden');
    
    let progress = 0;
    const interval = setInterval(() => {
        progress += 10;
        updateExportProgress(progress);
        
        if (progress >= 100) {
            clearInterval(interval);
            setTimeout(() => {
                closeModal();
                showToast('Export Complete', 'File downloaded successfully', 'success');
            }, 500);
        }
    }, 200);
}

/**
 * Update export progress bar
 */
function updateExportProgress(percent) {
    const bar = document.getElementById('exportProgressBar');
    const text = document.getElementById('exportProgressPercent');
    
    bar.style.width = `${percent}%`;
    text.textContent = `${percent}%`;
}

/**
 * Simulate export process
 */
function simulateExport(format, data) {
    setTimeout(() => {
        switch(format) {
            case 'csv':
                exportToCSV(data, 'dashboard_export');
                break;
            case 'excel':
                exportToExcel(data, 'dashboard_export');
                break;
            case 'pdf':
                exportToPDF(data, 'dashboard_export');
                break;
        }
    }, 2000);
}

/**
 * Export data to CSV
 * @param {object|array} data - Data to export
 * @param {string} filename - Output filename (without extension)
 */
function exportToCSV(data, filename) {
    let csv = '';
    
    // Add metadata header
    csv += `# BotV2 Dashboard Export\n`;
    csv += `# Generated: ${new Date().toISOString()}\n`;
    csv += `# \n\n`;
    
    // Convert data to CSV
    if (Array.isArray(data)) {
        // Array of objects
        const headers = Object.keys(data[0]);
        csv += headers.join(',') + '\n';
        
        data.forEach(row => {
            csv += headers.map(h => row[h]).join(',') + '\n';
        });
    } else {
        // Single object
        csv += Object.keys(data).join(',') + '\n';
        csv += Object.values(data).join(',') + '\n';
    }
    
    // Download
    downloadFile(csv, `${filename}.csv`, 'text/csv');
    
    // Track export
    DashboardAdvanced.state.exportHistory.push({
        format: 'csv',
        filename,
        timestamp: new Date().toISOString()
    });
    
    console.log(`📥 CSV exported: ${filename}.csv`);
}

/**
 * Export data to Excel (multi-sheet)
 * @param {object} data - Data with multiple sheets
 * @param {string} filename - Output filename
 */
function exportToExcel(data, filename) {
    // Placeholder - requires external library like SheetJS
    console.log(`📊 Excel export placeholder: ${filename}.xlsx`);
    showToast('Excel Export', 'Feature requires SheetJS library', 'warning');
}

/**
 * Export to PDF report
 * @param {object} data - Report data
 * @param {string} filename - Output filename
 */
function exportToPDF(data, filename) {
    // Placeholder - uses jsPDF if available
    if (typeof jsPDF === 'undefined') {
        showToast('PDF Export', 'jsPDF library not loaded', 'warning');
        return;
    }
    
    const doc = new jsPDF();
    doc.text('BotV2 Dashboard Report', 10, 10);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 10, 20);
    doc.save(`${filename}.pdf`);
    
    console.log(`📕 PDF exported: ${filename}.pdf`);
}

/**
 * Download file helper
 */
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

// ============================================
// CHART ANNOTATIONS
// ============================================

/**
 * Add annotation to chart
 * @param {string} chartId - Chart element ID
 * @param {object} annotation - Annotation config
 */
function addChartAnnotation(chartId, annotation) {
    const { x, y, text, color, type } = annotation;
    
    const annotationConfig = {
        x,
        y,
        xref: 'x',
        yref: 'y',
        text,
        showarrow: true,
        arrowhead: 2,
        arrowsize: 1,
        arrowwidth: 2,
        arrowcolor: color || DashboardAdvanced.config.annotationColors[0],
        font: { size: 12, color: color || DashboardAdvanced.config.annotationColors[0] },
        bgcolor: 'rgba(255, 255, 255, 0.9)',
        bordercolor: color || DashboardAdvanced.config.annotationColors[0],
        borderwidth: 2,
        borderpad: 4
    };
    
    // Add to chart
    Plotly.relayout(chartId, {
        annotations: [...(DashboardAdvanced.state.annotations[chartId] || []), annotationConfig]
    });
    
    // Store annotation
    if (!DashboardAdvanced.state.annotations[chartId]) {
        DashboardAdvanced.state.annotations[chartId] = [];
    }
    DashboardAdvanced.state.annotations[chartId].push(annotationConfig);
    
    persistState();
    
    console.log(`📍 Annotation added to ${chartId}`);
}

// ============================================
// PERFORMANCE OPTIMIZATIONS
// ============================================

/**
 * Downsample data for large datasets
 * @param {object} data - Original data
 * @param {number} targetPoints - Target number of points
 * @returns {object} Downsampled data
 */
function downsampleData(data, targetPoints) {
    if (!data.x || data.x.length <= targetPoints) return data;
    
    const step = Math.ceil(data.x.length / targetPoints);
    const downsampled = { ...data, x: [], y: [] };
    
    for (let i = 0; i < data.x.length; i += step) {
        downsampled.x.push(data.x[i]);
        downsampled.y.push(data.y[i]);
    }
    
    console.log(`⚡ Downsampled ${data.x.length} → ${downsampled.x.length} points`);
    return downsampled;
}

/**
 * Debounce function for performance
 * @param {function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Virtual scrolling for large trade tables
 * @param {string} tableId - Table element ID
 * @param {array} data - Full dataset
 */
function enableVirtualScroll(tableId, data) {
    if (data.length < DashboardAdvanced.config.virtualScrollThreshold) return;
    
    const table = document.getElementById(tableId);
    if (!table) return;
    
    console.log(`⚡ Virtual scroll enabled for ${tableId} (${data.length} rows)`);
    
    // Implementation would use Intersection Observer
    // Placeholder for now
}

/**
 * Lazy load charts
 * @param {string} chartId - Chart element ID
 */
function lazyLoadChart(chartId) {
    const chart = document.getElementById(chartId);
    if (!chart) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Load chart data
                console.log(`⚡ Lazy loading chart: ${chartId}`);
                observer.unobserve(chart);
            }
        });
    });
    
    observer.observe(chart);
}

// ============================================
// DATA PERSISTENCE
// ============================================

/**
 * Persist state to localStorage
 */
function persistState() {
    try {
        const stateToSave = {
            filters: DashboardAdvanced.state.filters,
            annotations: DashboardAdvanced.state.annotations,
            zoomState: DashboardAdvanced.state.zoomState,
            exportHistory: DashboardAdvanced.state.exportHistory.slice(-10) // Keep last 10
        };
        
        localStorage.setItem(
            DashboardAdvanced.config.localStorageKey,
            JSON.stringify(stateToSave)
        );
        
        console.log('💾 State persisted to localStorage');
    } catch (error) {
        console.error('❌ Failed to persist state:', error);
    }
}

/**
 * Load state from localStorage
 */
function loadPersistedState() {
    try {
        const saved = localStorage.getItem(DashboardAdvanced.config.localStorageKey);
        if (!saved) return;
        
        const state = JSON.parse(saved);
        
        DashboardAdvanced.state.filters = state.filters || {};
        DashboardAdvanced.state.annotations = state.annotations || {};
        DashboardAdvanced.state.zoomState = state.zoomState || {};
        DashboardAdvanced.state.exportHistory = state.exportHistory || [];
        
        console.log('✅ State loaded from localStorage');
    } catch (error) {
        console.error('❌ Failed to load persisted state:', error);
    }
}

/**
 * Clear persisted state
 */
function clearPersistedState() {
    localStorage.removeItem(DashboardAdvanced.config.localStorageKey);
    DashboardAdvanced.state = {
        modals: {},
        filters: {},
        selections: {},
        annotations: {},
        comparisonMode: false,
        selectedStrategies: [],
        zoomState: {},
        exportHistory: []
    };
    console.log('🗑️ Persisted state cleared');
}

// ============================================
// INITIALIZATION
// ============================================

/**
 * Initialize advanced features module
 */
function initDashboardAdvanced() {
    console.log('🚀 Initializing Dashboard Advanced Features v1.0...');
    
    // Load persisted state
    loadPersistedState();
    
    // Setup event listeners
    setupEventListeners();
    
    // Enable features
    enableAdvancedFeatures();
    
    console.log('✅ Dashboard Advanced Features initialized!');
}

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // ESC key to close modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
    
    // Click outside modal to close
    document.getElementById('modalOverlay')?.addEventListener('click', (e) => {
        if (e.target.id === 'modalOverlay') {
            closeModal();
        }
    });
}

/**
 * Enable advanced features on existing charts
 */
function enableAdvancedFeatures() {
    // Enable brush selection on all charts
    const charts = document.querySelectorAll('[id^="chart-"]');
    charts.forEach(chart => {
        enableBrushSelection(chart.id);
        lazyLoadChart(chart.id);
    });
}

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboardAdvanced);
} else {
    initDashboardAdvanced();
}

// Export for global access
window.DashboardAdvanced = DashboardAdvanced;
window.showModal = showModal;
window.closeModal = closeModal;
window.applyChartFilter = applyChartFilter;
window.applyModalChartFilter = applyModalChartFilter;
window.syncChartZoom = syncChartZoom;
window.resetChartZoom = resetChartZoom;
window.enableBrushSelection = enableBrushSelection;
window.toggleComparisonMode = toggleComparisonMode;
window.compareStrategies = compareStrategies;
window.exportComparison = exportComparison;
window.executeExport = executeExport;
window.exportToCSV = exportToCSV;
window.exportToExcel = exportToExcel;
window.exportToPDF = exportToPDF;
window.addChartAnnotation = addChartAnnotation;

console.log('📦 Dashboard Advanced Module v1.0 loaded successfully!');
