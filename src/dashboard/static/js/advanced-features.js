// ============================================
// ADVANCED FEATURES MODULE
// Phase 2 Part 2: Advanced Interactivity
// ============================================

(function() {
    'use strict';
    
    // ====== STATE MANAGEMENT ======
    const AdvancedState = {
        modals: {
            currentModal: null,
            data: {}
        },
        filters: JSON.parse(localStorage.getItem('chartFilters') || '{}'),
        brushSelection: {},
        zoomSync: {
            enabled: false,
            syncedCharts: []
        },
        comparisonMode: {
            active: false,
            selectedStrategies: []
        },
        annotations: JSON.parse(localStorage.getItem('chartAnnotations') || '{}')
    };
    
    // ====== MODAL SYSTEM ======
    
    /**
     * Create modal backdrop and container
     */
    function createModalStructure() {
        if (document.getElementById('modalBackdrop')) return;
        
        const backdrop = document.createElement('div');
        backdrop.id = 'modalBackdrop';
        backdrop.className = 'modal-backdrop';
        backdrop.innerHTML = `
            <div class="modal-container" id="modalContainer">
                <div class="modal-header">
                    <h2 class="modal-title" id="modalTitle">Modal Title</h2>
                    <button class="modal-close" onclick="AdvancedFeatures.closeModal()">&times;</button>
                </div>
                <div class="modal-body" id="modalBody">Modal content</div>
                <div class="modal-footer" id="modalFooter"></div>
            </div>
        `;
        document.body.appendChild(backdrop);
        
        // Close on backdrop click
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) closeModal();
        });
        
        // Close on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && AdvancedState.modals.currentModal) {
                closeModal();
            }
        });
    }
    
    /**
     * Show modal with specified content
     */
    function showModal(title, bodyHTML, footerHTML = '') {
        createModalStructure();
        const backdrop = document.getElementById('modalBackdrop');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const modalFooter = document.getElementById('modalFooter');
        
        modalTitle.textContent = title;
        modalBody.innerHTML = bodyHTML;
        modalFooter.innerHTML = footerHTML;
        
        backdrop.classList.add('active');
        AdvancedState.modals.currentModal = title;
    }
    
    /**
     * Close current modal
     */
    function closeModal() {
        const backdrop = document.getElementById('modalBackdrop');
        if (backdrop) {
            backdrop.classList.remove('active');
            setTimeout(() => {
                backdrop.remove();
            }, 300);
        }
        AdvancedState.modals.currentModal = null;
    }
    
    /**
     * Show trade detail modal
     */
    function showTradeDetailModal(tradeData) {
        const bodyHTML = `
            <div class="trade-detail-grid">
                <div class="detail-section">
                    <h3>📊 Trade Information</h3>
                    <table class="detail-table">
                        <tr><th>Trade ID:</th><td><code>${tradeData.id || 'N/A'}</code></td></tr>
                        <tr><th>Strategy:</th><td><strong>${tradeData.strategy || 'Unknown'}</strong></td></tr>
                        <tr><th>Asset:</th><td>${tradeData.asset || 'N/A'}</td></tr>
                        <tr><th>Side:</th><td class="${tradeData.side === 'BUY' ? 'text-success' : 'text-danger'}">${tradeData.side || 'N/A'}</td></tr>
                        <tr><th>Quantity:</th><td>${tradeData.quantity || 0}</td></tr>
                    </table>
                </div>
                <div class="detail-section">
                    <h3>💰 Financial Details</h3>
                    <table class="detail-table">
                        <tr><th>Entry Price:</th><td>€${tradeData.entry_price?.toFixed(2) || '0.00'}</td></tr>
                        <tr><th>Exit Price:</th><td>€${tradeData.exit_price?.toFixed(2) || '0.00'}</td></tr>
                        <tr><th>P&L:</th><td class="${(tradeData.pnl || 0) >= 0 ? 'text-success' : 'text-danger'}"><strong>€${tradeData.pnl?.toFixed(2) || '0.00'}</strong></td></tr>
                        <tr><th>Fees:</th><td>€${tradeData.fees?.toFixed(2) || '0.00'}</td></tr>
                        <tr><th>Net P&L:</th><td class="${((tradeData.pnl || 0) - (tradeData.fees || 0)) >= 0 ? 'text-success' : 'text-danger'}"><strong>€${((tradeData.pnl || 0) - (tradeData.fees || 0)).toFixed(2)}</strong></td></tr>
                    </table>
                </div>
                <div class="detail-section full-width">
                    <h3>⏱️ Timing</h3>
                    <table class="detail-table">
                        <tr><th>Entry Time:</th><td>${tradeData.entry_time || 'N/A'}</td></tr>
                        <tr><th>Exit Time:</th><td>${tradeData.exit_time || 'N/A'}</td></tr>
                        <tr><th>Duration:</th><td>${tradeData.duration || 'N/A'}</td></tr>
                    </table>
                </div>
                <div class="detail-section full-width">
                    <h3>📝 Notes</h3>
                    <textarea class="trade-notes" placeholder="Add notes about this trade...">${tradeData.notes || ''}</textarea>
                </div>
            </div>
        `;
        
        const footerHTML = `
            <button class="btn btn-secondary" onclick="AdvancedFeatures.closeModal()">Close</button>
            <button class="btn btn-primary" onclick="AdvancedFeatures.exportTradeDetails('${tradeData.id}')">📥 Export</button>
        `;
        
        showModal(`Trade Details: ${tradeData.id}`, bodyHTML, footerHTML);
    }
    
    /**
     * Show strategy analysis modal
     */
    function showStrategyAnalysisModal(strategyData) {
        const bodyHTML = `
            <div class="strategy-analysis">
                <div class="metrics-row">
                    <div class="metric-box">
                        <div class="metric-label">Total Return</div>
                        <div class="metric-value ${strategyData.total_return >= 0 ? 'text-success' : 'text-danger'}">${strategyData.total_return?.toFixed(2)}%</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Win Rate</div>
                        <div class="metric-value">${strategyData.win_rate?.toFixed(1)}%</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Sharpe Ratio</div>
                        <div class="metric-value">${strategyData.sharpe_ratio?.toFixed(2)}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Max Drawdown</div>
                        <div class="metric-value text-danger">${strategyData.max_drawdown?.toFixed(2)}%</div>
                    </div>
                </div>
                <div class="chart-in-modal" id="strategyEquityCurve" style="height: 300px; margin: 20px 0;"></div>
                <div class="trade-list">
                    <h3>Recent Trades</h3>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Asset</th>
                                <th>Side</th>
                                <th>P&L</th>
                            </tr>
                        </thead>
                        <tbody id="strategyTradesTable">
                            <tr><td colspan="4" class="text-center">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        const footerHTML = `
            <button class="btn btn-secondary" onclick="AdvancedFeatures.closeModal()">Close</button>
            <button class="btn btn-primary" onclick="AdvancedFeatures.exportStrategyReport('${strategyData.name}')">📊 Full Report</button>
        `;
        
        showModal(`Strategy Analysis: ${strategyData.name}`, bodyHTML, footerHTML);
        
        // Render equity curve in modal
        setTimeout(() => {
            renderStrategyEquityCurve(strategyData);
            loadStrategyTrades(strategyData.name);
        }, 100);
    }
    
    function renderStrategyEquityCurve(strategyData) {
        const mockData = Array.from({length: 30}, (_, i) => ({
            x: new Date(2024, 0, i + 1),
            y: 3000 * (1 + (strategyData.total_return / 100) * (i / 30) + (Math.random() - 0.5) * 0.05)
        }));
        
        const trace = {
            x: mockData.map(d => d.x),
            y: mockData.map(d => d.y),
            type: 'scatter',
            mode: 'lines',
            line: { color: '#0066ff', width: 2 }
        };
        
        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            margin: { l: 50, r: 20, t: 10, b: 40 },
            xaxis: { gridcolor: 'rgba(255,255,255,0.1)' },
            yaxis: { gridcolor: 'rgba(255,255,255,0.1)', title: 'Equity (€)' },
            font: { color: '#e0e0e0' }
        };
        
        Plotly.newPlot('strategyEquityCurve', [trace], layout, { responsive: true, displayModeBar: false });
    }
    
    function loadStrategyTrades(strategyName) {
        // Mock trade data - replace with actual API call
        const mockTrades = [
            { date: '2024-01-20', asset: 'BTC', side: 'BUY', pnl: 125.50 },
            { date: '2024-01-19', asset: 'ETH', side: 'SELL', pnl: -45.20 },
            { date: '2024-01-18', asset: 'BTC', side: 'BUY', pnl: 89.30 }
        ];
        
        const tbody = document.getElementById('strategyTradesTable');
        if (tbody) {
            tbody.innerHTML = mockTrades.map(t => `
                <tr>
                    <td>${t.date}</td>
                    <td>${t.asset}</td>
                    <td class="${t.side === 'BUY' ? 'text-success' : 'text-danger'}">${t.side}</td>
                    <td class="${t.pnl >= 0 ? 'text-success' : 'text-danger'}">€${t.pnl.toFixed(2)}</td>
                </tr>
            `).join('');
        }
    }
    
    // ====== ADVANCED FILTERS ======
    
    /**
     * Apply filters to chart
     */
    function applyChartFilter(chartId, filters) {
        console.log(`Applying filters to ${chartId}:`, filters);
        AdvancedState.filters[chartId] = filters;
        localStorage.setItem('chartFilters', JSON.stringify(AdvancedState.filters));
        
        // Trigger chart update with filters
        if (window.AppState && window.AppState.data) {
            const filterEvent = new CustomEvent('chartFilterApplied', {
                detail: { chartId, filters }
            });
            document.dispatchEvent(filterEvent);
        }
        
        showToast('Filters applied successfully', 'success');
    }
    
    /**
     * Show filter modal for a chart
     */
    function showFilterModal(chartId) {
        const currentFilters = AdvancedState.filters[chartId] || {};
        
        const bodyHTML = `
            <div class="filter-form">
                <div class="form-group">
                    <label>Date Range</label>
                    <div class="date-range-selector">
                        <input type="date" id="filterStartDate" value="${currentFilters.startDate || ''}" class="filter-input">
                        <span>to</span>
                        <input type="date" id="filterEndDate" value="${currentFilters.endDate || ''}" class="filter-input">
                    </div>
                </div>
                <div class="form-group">
                    <label>Strategies</label>
                    <div class="checkbox-group" id="strategyCheckboxes">
                        <label><input type="checkbox" value="all" checked> All Strategies</label>
                        <label><input type="checkbox" value="momentum"> Momentum</label>
                        <label><input type="checkbox" value="meanrev"> Mean Reversion</label>
                        <label><input type="checkbox" value="arb"> Arbitrage</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Minimum Trade Size</label>
                    <input type="number" id="filterMinSize" value="${currentFilters.minSize || 0}" class="filter-input" placeholder="0">
                </div>
                <div class="form-group">
                    <label>Show Only</label>
                    <div class="radio-group">
                        <label><input type="radio" name="showOnly" value="all" checked> All Trades</label>
                        <label><input type="radio" name="showOnly" value="wins"> Winning Trades</label>
                        <label><input type="radio" name="showOnly" value="losses"> Losing Trades</label>
                    </div>
                </div>
            </div>
        `;
        
        const footerHTML = `
            <button class="btn btn-secondary" onclick="AdvancedFeatures.resetFilters('${chartId}')">Reset</button>
            <button class="btn btn-secondary" onclick="AdvancedFeatures.closeModal()">Cancel</button>
            <button class="btn btn-primary" onclick="AdvancedFeatures.saveFilters('${chartId}')">Apply Filters</button>
        `;
        
        showModal('Chart Filters', bodyHTML, footerHTML);
    }
    
    function saveFilters(chartId) {
        const filters = {
            startDate: document.getElementById('filterStartDate')?.value,
            endDate: document.getElementById('filterEndDate')?.value,
            minSize: parseFloat(document.getElementById('filterMinSize')?.value || 0),
            strategies: Array.from(document.querySelectorAll('#strategyCheckboxes input:checked')).map(cb => cb.value),
            showOnly: document.querySelector('input[name="showOnly"]:checked')?.value
        };
        
        applyChartFilter(chartId, filters);
        closeModal();
    }
    
    function resetFilters(chartId) {
        delete AdvancedState.filters[chartId];
        localStorage.setItem('chartFilters', JSON.stringify(AdvancedState.filters));
        closeModal();
        showToast('Filters reset', 'info');
    }
    
    // ====== BRUSH SELECTION & ZOOM SYNC ======
    
    /**
     * Enable brush selection on a chart
     */
    function enableBrushSelection(chartId) {
        const chartDiv = document.getElementById(chartId);
        if (!chartDiv) return;
        
        chartDiv.on('plotly_selected', function(eventData) {
            if (eventData && eventData.range) {
                const range = eventData.range.x;
                AdvancedState.brushSelection[chartId] = range;
                
                if (AdvancedState.zoomSync.enabled) {
                    syncZoomToCharts(range);
                }
                
                showToast(`Selection: ${new Date(range[0]).toLocaleDateString()} - ${new Date(range[1]).toLocaleDateString()}`, 'info');
            }
        });
    }
    
    /**
     * Sync zoom across multiple charts
     */
    function syncZoomToCharts(xRange) {
        const chartsToSync = AdvancedState.zoomSync.syncedCharts;
        
        chartsToSync.forEach(chartId => {
            const chartDiv = document.getElementById(chartId);
            if (chartDiv && chartDiv.data) {
                Plotly.relayout(chartId, {
                    'xaxis.range': xRange
                });
            }
        });
    }
    
    /**
     * Toggle zoom synchronization
     */
    function toggleZoomSync(chartIds) {
        AdvancedState.zoomSync.enabled = !AdvancedState.zoomSync.enabled;
        AdvancedState.zoomSync.syncedCharts = chartIds || ['equityChart', 'returnsChart', 'drawdownChart'];
        
        const status = AdvancedState.zoomSync.enabled ? 'enabled' : 'disabled';
        showToast(`Zoom sync ${status}`, 'info');
        
        // Enable brush on all synced charts
        if (AdvancedState.zoomSync.enabled) {
            chartIds.forEach(id => enableBrushSelection(id));
        }
    }
    
    /**
     * Reset zoom on chart
     */
    function resetChartZoom(chartId) {
        Plotly.relayout(chartId, {
            'xaxis.autorange': true,
            'yaxis.autorange': true
        });
        delete AdvancedState.brushSelection[chartId];
        showToast('Zoom reset', 'info');
    }
    
    // ====== COMPARISON MODE ======
    
    /**
     * Toggle comparison mode
     */
    function toggleComparisonMode() {
        AdvancedState.comparisonMode.active = !AdvancedState.comparisonMode.active;
        
        if (AdvancedState.comparisonMode.active) {
            showStrategySelector();
        } else {
            exitComparisonMode();
        }
    }
    
    function showStrategySelector() {
        const bodyHTML = `
            <div class="comparison-selector">
                <p>Select strategies to compare (2-5):</p>
                <div class="strategy-list" id="comparisonStrategyList">
                    <label><input type="checkbox" value="momentum_btc"> Momentum BTC</label>
                    <label><input type="checkbox" value="meanrev_eth"> Mean Reversion ETH</label>
                    <label><input type="checkbox" value="arb_multi"> Arbitrage Multi</label>
                    <label><input type="checkbox" value="trend_follow"> Trend Following</label>
                    <label><input type="checkbox" value="market_maker"> Market Making</label>
                </div>
                <div class="comparison-options">
                    <label><input type="checkbox" id="normalizeView"> Normalize to 100%</label>
                    <label><input type="checkbox" id="overlayMode" checked> Overlay Mode</label>
                </div>
            </div>
        `;
        
        const footerHTML = `
            <button class="btn btn-secondary" onclick="AdvancedFeatures.closeModal(); AdvancedFeatures.exitComparisonMode()">Cancel</button>
            <button class="btn btn-primary" onclick="AdvancedFeatures.startComparison()">Compare</button>
        `;
        
        showModal('Strategy Comparison', bodyHTML, footerHTML);
    }
    
    function startComparison() {
        const selectedStrategies = Array.from(
            document.querySelectorAll('#comparisonStrategyList input:checked')
        ).map(cb => cb.value);
        
        if (selectedStrategies.length < 2) {
            showToast('Please select at least 2 strategies', 'warning');
            return;
        }
        
        if (selectedStrategies.length > 5) {
            showToast('Maximum 5 strategies allowed', 'warning');
            return;
        }
        
        AdvancedState.comparisonMode.selectedStrategies = selectedStrategies;
        closeModal();
        
        renderComparisonCharts(selectedStrategies);
        showToast(`Comparing ${selectedStrategies.length} strategies`, 'success');
    }
    
    function renderComparisonCharts(strategies) {
        // Create comparison view
        const container = document.createElement('div');
        container.id = 'comparisonContainer';
        container.className = 'comparison-container';
        container.innerHTML = `
            <div class="comparison-header">
                <h2>📊 Strategy Comparison</h2>
                <button class="btn btn-secondary" onclick="AdvancedFeatures.exitComparisonMode()">Exit Comparison</button>
            </div>
            <div id="comparisonChartArea" style="height: 500px;"></div>
            <div class="comparison-metrics">
                <table class="data-table" id="comparisonMetricsTable"></table>
            </div>
        `;
        
        // Insert comparison view
        const contentArea = document.querySelector('.content-area');
        const currentPage = document.querySelector('.page.active');
        currentPage.style.display = 'none';
        contentArea.insertBefore(container, currentPage);
        
        // Render comparison chart
        setTimeout(() => {
            createComparisonChart(strategies);
            createComparisonTable(strategies);
        }, 100);
    }
    
    function createComparisonChart(strategies) {
        const traces = strategies.map((strategy, i) => {
            const mockEquity = Array.from({length: 30}, (_, j) => 
                3000 * (1 + (0.05 + i * 0.03) * (j / 30) + (Math.random() - 0.5) * 0.02)
            );
            const dates = Array.from({length: 30}, (_, j) => new Date(2024, 0, j + 1));
            
            return {
                x: dates,
                y: mockEquity,
                type: 'scatter',
                mode: 'lines',
                name: strategy.replace('_', ' ').toUpperCase(),
                line: { width: 3 }
            };
        });
        
        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#e0e0e0' },
            xaxis: { gridcolor: 'rgba(255,255,255,0.1)' },
            yaxis: { gridcolor: 'rgba(255,255,255,0.1)', title: 'Equity (€)' },
            legend: { x: 0, y: 1 },
            hovermode: 'x unified'
        };
        
        Plotly.newPlot('comparisonChartArea', traces, layout, { responsive: true });
    }
    
    function createComparisonTable(strategies) {
        const metrics = strategies.map(strategy => ({
            name: strategy,
            return: (Math.random() * 20 - 5).toFixed(2),
            sharpe: (Math.random() * 2 + 0.5).toFixed(2),
            maxDD: (-Math.random() * 15).toFixed(2),
            winRate: (Math.random() * 30 + 50).toFixed(1)
        }));
        
        const table = document.getElementById('comparisonMetricsTable');
        if (table) {
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Strategy</th>
                        <th>Return (%)</th>
                        <th>Sharpe</th>
                        <th>Max DD (%)</th>
                        <th>Win Rate (%)</th>
                    </tr>
                </thead>
                <tbody>
                    ${metrics.map(m => `
                        <tr>
                            <td><strong>${m.name.replace('_', ' ')}</strong></td>
                            <td class="${m.return >= 0 ? 'text-success' : 'text-danger'}">${m.return}%</td>
                            <td>${m.sharpe}</td>
                            <td class="text-danger">${m.maxDD}%</td>
                            <td>${m.winRate}%</td>
                        </tr>
                    `).join('')}
                </tbody>
            `;
        }
    }
    
    function exitComparisonMode() {
        const container = document.getElementById('comparisonContainer');
        if (container) container.remove();
        
        const currentPage = document.querySelector('.page.active');
        if (currentPage) currentPage.style.display = 'block';
        
        AdvancedState.comparisonMode.active = false;
        AdvancedState.comparisonMode.selectedStrategies = [];
    }
    
    // ====== EXPORT FUNCTIONS ======
    
    /**
     * Export data to CSV
     */
    function exportToCSV(data, filename) {
        if (!data || !Array.isArray(data) || data.length === 0) {
            showToast('No data to export', 'warning');
            return;
        }
        
        // Convert to CSV
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(h => JSON.stringify(row[h] || '')).join(','))
        ].join('\n');
        
        // Download
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${filename}_${Date.now()}.csv`;
        link.click();
        URL.revokeObjectURL(url);
        
        showToast('CSV exported successfully', 'success');
    }
    
    /**
     * Export trade details
     */
    function exportTradeDetails(tradeId) {
        // Mock trade data - replace with actual data
        const tradeData = [{
            trade_id: tradeId,
            strategy: 'Momentum BTC',
            asset: 'BTC',
            side: 'BUY',
            entry_price: 45000,
            exit_price: 46500,
            quantity: 0.5,
            pnl: 750,
            fees: 25,
            net_pnl: 725,
            entry_time: '2024-01-20 10:30:00',
            exit_time: '2024-01-20 14:45:00',
            duration: '4h 15m'
        }];
        
        exportToCSV(tradeData, `trade_${tradeId}`);
    }
    
    /**
     * Export strategy report
     */
    function exportStrategyReport(strategyName) {
        showToast('Generating strategy report...', 'info');
        
        // Mock strategy data
        const reportData = [
            { metric: 'Total Return', value: '12.5%' },
            { metric: 'Sharpe Ratio', value: '1.85' },
            { metric: 'Max Drawdown', value: '-8.3%' },
            { metric: 'Win Rate', value: '65.2%' },
            { metric: 'Total Trades', value: '127' },
            { metric: 'Avg Trade Duration', value: '6h 32m' }
        ];
        
        exportToCSV(reportData, `strategy_${strategyName}`);
    }
    
    // ====== CHART ANNOTATIONS ======
    
    /**
     * Add annotation to chart
     */
    function addChartAnnotation(chartId, annotation) {
        if (!AdvancedState.annotations[chartId]) {
            AdvancedState.annotations[chartId] = [];
        }
        
        AdvancedState.annotations[chartId].push(annotation);
        localStorage.setItem('chartAnnotations', JSON.stringify(AdvancedState.annotations));
        
        // Apply annotation to chart
        const chartDiv = document.getElementById(chartId);
        if (chartDiv && chartDiv.layout) {
            const currentAnnotations = chartDiv.layout.annotations || [];
            Plotly.relayout(chartId, {
                annotations: [...currentAnnotations, annotation]
            });
        }
        
        showToast('Annotation added', 'success');
    }
    
    /**
     * Show annotation editor
     */
    function showAnnotationEditor(chartId) {
        const bodyHTML = `
            <div class="annotation-editor">
                <div class="form-group">
                    <label>Annotation Text</label>
                    <input type="text" id="annotationText" class="filter-input" placeholder="Enter annotation text">
                </div>
                <div class="form-group">
                    <label>Date (X-axis)</label>
                    <input type="date" id="annotationDate" class="filter-input">
                </div>
                <div class="form-group">
                    <label>Value (Y-axis)</label>
                    <input type="number" id="annotationValue" class="filter-input" placeholder="Auto-detect if empty">
                </div>
                <div class="form-group">
                    <label>Color</label>
                    <select id="annotationColor" class="filter-input">
                        <option value="#0066ff">Blue</option>
                        <option value="#10b981">Green</option>
                        <option value="#ef4444">Red</option>
                        <option value="#f59e0b">Orange</option>
                    </select>
                </div>
            </div>
        `;
        
        const footerHTML = `
            <button class="btn btn-secondary" onclick="AdvancedFeatures.closeModal()">Cancel</button>
            <button class="btn btn-primary" onclick="AdvancedFeatures.saveAnnotation('${chartId}')">Add Annotation</button>
        `;
        
        showModal('Add Chart Annotation', bodyHTML, footerHTML);
    }
    
    function saveAnnotation(chartId) {
        const text = document.getElementById('annotationText')?.value;
        const date = document.getElementById('annotationDate')?.value;
        const value = document.getElementById('annotationValue')?.value;
        const color = document.getElementById('annotationColor')?.value;
        
        if (!text || !date) {
            showToast('Please fill required fields', 'warning');
            return;
        }
        
        const annotation = {
            x: date,
            y: value || null,
            text: text,
            showarrow: true,
            arrowhead: 2,
            arrowcolor: color,
            font: { color: color }
        };
        
        addChartAnnotation(chartId, annotation);
        closeModal();
    }
    
    // ====== UTILITY FUNCTIONS ======
    
    function showToast(message, type) {
        // Use existing toast function from main dashboard
        if (typeof window.showToast === 'function') {
            window.showToast(message, type);
        } else {
            console.log(`Toast [${type}]: ${message}`);
        }
    }
    
    // ====== PUBLIC API ======
    
    window.AdvancedFeatures = {
        // Modal functions
        showModal,
        closeModal,
        showTradeDetailModal,
        showStrategyAnalysisModal,
        
        // Filter functions
        showFilterModal,
        applyChartFilter,
        saveFilters,
        resetFilters,
        
        // Zoom & selection
        enableBrushSelection,
        toggleZoomSync,
        resetChartZoom,
        syncZoomToCharts,
        
        // Comparison mode
        toggleComparisonMode,
        startComparison,
        exitComparisonMode,
        
        // Export
        exportToCSV,
        exportTradeDetails,
        exportStrategyReport,
        
        // Annotations
        showAnnotationEditor,
        addChartAnnotation,
        saveAnnotation,
        
        // State access
        getState: () => AdvancedState
    };
    
    console.log('✅ Advanced Features Module Loaded');
    
})();
