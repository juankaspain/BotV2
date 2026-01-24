/**
 * Performance Integration Module
 * Quick integration guide for Dashboard v4.4
 * 
 * Author: Juan Carlos Garcia Arriero
 * Date: 2026-01-24
 */

'use strict';

// ============================================================================
// READY-TO-USE INTEGRATIONS
// ============================================================================

/**
 * Initialize all performance optimizations
 */
function initPerformanceOptimizations() {
    console.log('[Performance] Initializing optimizations...');
    
    // 1. Start performance monitoring
    if (window.PerformanceOptimizer) {
        window.PerformanceOptimizer.perfMonitor.start();
        
        // Show FPS counter in dev mode
        if (window.location.hostname === 'localhost') {
            showFPSCounter();
        }
    }
    
    // 2. Initialize virtual scrolling for tables
    initVirtualScrollingTables();
    
    // 3. Setup debounced refresh
    setupDebouncedRefresh();
    
    // 4. Setup lazy loading for charts
    setupLazyCharts();
    
    // 5. Optimize WebSocket updates
    optimizeWebSocketUpdates();
    
    console.log('[Performance] ✅ All optimizations initialized');
}

/**
 * Show FPS counter in corner (dev mode only)
 */
function showFPSCounter() {
    const counter = document.createElement('div');
    counter.id = 'fps-counter';
    counter.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        background: rgba(0,0,0,0.8);
        color: #0f0;
        padding: 8px 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 14px;
        z-index: 10000;
        pointer-events: none;
    `;
    document.body.appendChild(counter);
    
    setInterval(() => {
        const fps = window.PerformanceOptimizer.perfMonitor.getFPS();
        const color = fps >= 55 ? '#0f0' : fps >= 30 ? '#ff0' : '#f00';
        counter.style.color = color;
        counter.textContent = `${fps} FPS`;
    }, 500);
}

/**
 * Initialize virtual scrolling for trades and positions tables
 */
function initVirtualScrollingTables() {
    if (!window.PerformanceOptimizer) return;
    
    // Trades table
    const tradesContainer = document.getElementById('trades-table-container');
    if (tradesContainer) {
        window.tradesScroller = new window.PerformanceOptimizer.VirtualScroller(
            tradesContainer,
            {
                rowHeight: 45,
                overscanCount: 5,
                renderRow: (trade, index) => renderTradeRow(trade, index)
            }
        );
        console.log('[Performance] ✅ Virtual scrolling enabled for trades');
    }
    
    // Positions table
    const positionsContainer = document.getElementById('positions-table-container');
    if (positionsContainer) {
        window.positionsScroller = new window.PerformanceOptimizer.VirtualScroller(
            positionsContainer,
            {
                rowHeight: 50,
                overscanCount: 3,
                renderRow: (position, index) => renderPositionRow(position, index)
            }
        );
        console.log('[Performance] ✅ Virtual scrolling enabled for positions');
    }
}

/**
 * Render single trade row (optimized)
 */
function renderTradeRow(trade, index) {
    const pnlClass = trade.pnl >= 0 ? 'profit' : 'loss';
    const sideClass = trade.side.toLowerCase();
    
    return `
        <div class="trade-row ${pnlClass}" data-index="${index}">
            <span class="trade-time">${formatTime(trade.timestamp)}</span>
            <span class="trade-symbol">${trade.symbol}</span>
            <span class="trade-side ${sideClass}">${trade.side}</span>
            <span class="trade-price">${trade.price.toFixed(2)}</span>
            <span class="trade-quantity">${trade.quantity}</span>
            <span class="trade-pnl ${pnlClass}">${formatPnL(trade.pnl)}</span>
        </div>
    `;
}

/**
 * Render single position row (optimized)
 */
function renderPositionRow(position, index) {
    const pnlClass = position.unrealized_pnl >= 0 ? 'profit' : 'loss';
    
    return `
        <div class="position-row ${pnlClass}" data-index="${index}">
            <span class="position-symbol">${position.symbol}</span>
            <span class="position-side">${position.side}</span>
            <span class="position-quantity">${position.quantity}</span>
            <span class="position-entry">${position.entry_price.toFixed(2)}</span>
            <span class="position-current">${position.current_price.toFixed(2)}</span>
            <span class="position-pnl ${pnlClass}">${formatPnL(position.unrealized_pnl)}</span>
        </div>
    `;
}

/**
 * Setup debounced refresh for current section
 */
function setupDebouncedRefresh() {
    if (!window.PerformanceOptimizer) return;
    
    // Create debounced version of refresh function
    window.debouncedRefresh = window.PerformanceOptimizer.createDebouncedRefresh(
        () => {
            // Call original refresh logic
            if (typeof refreshCurrentSection === 'function') {
                refreshCurrentSection();
            }
        },
        300
    );
    
    console.log('[Performance] ✅ Debounced refresh enabled');
}

/**
 * Setup lazy loading for chart sections
 */
function setupLazyCharts() {
    if (!window.PerformanceOptimizer) return;
    
    const chartContainers = document.querySelectorAll('[data-lazy-chart]');
    
    chartContainers.forEach(container => {
        window.PerformanceOptimizer.lazyLoader.observe(container);
    });
    
    console.log(`[Performance] ✅ Lazy loading enabled for ${chartContainers.length} charts`);
}

/**
 * Optimize WebSocket updates with debouncing
 */
function optimizeWebSocketUpdates() {
    if (!window.socket || !window.PerformanceOptimizer) return;
    
    // Debounced handlers for high-frequency events
    const debouncedPriceUpdate = window.PerformanceOptimizer.throttle((data) => {
        updatePrices(data);
    }, 100);
    
    const debouncedPortfolioUpdate = window.PerformanceOptimizer.debounce((data) => {
        updatePortfolio(data);
    }, 500);
    
    // Replace direct handlers
    if (window.socket.on) {
        window.socket.on('price_update', debouncedPriceUpdate);
        window.socket.on('portfolio_update', debouncedPortfolioUpdate);
    }
    
    console.log('[Performance] ✅ WebSocket updates optimized');
}

// ============================================================================
// CHART OPTIMIZATION HELPERS
// ============================================================================

/**
 * Initialize optimized chart updates
 */
function initOptimizedCharts() {
    if (!window.PerformanceOptimizer) return;
    
    const optimizer = window.PerformanceOptimizer.chartOptimizer;
    
    // Register all existing charts
    if (window.chartInstances) {
        Object.entries(window.chartInstances).forEach(([id, chart]) => {
            optimizer.registerChart(id, chart);
        });
        console.log(`[Performance] ✅ Registered ${Object.keys(window.chartInstances).length} charts`);
    }
}

/**
 * Update chart with optimization
 */
function updateChartOptimized(chartId, newData, forceUpdate = false) {
    if (!window.PerformanceOptimizer) {
        // Fallback to direct update
        if (window.chartInstances && window.chartInstances[chartId]) {
            window.chartInstances[chartId].data.datasets[0].data = newData;
            window.chartInstances[chartId].update();
        }
        return;
    }
    
    const updated = window.PerformanceOptimizer.chartOptimizer.updateChart(
        chartId,
        newData,
        forceUpdate
    );
    
    if (!updated) {
        console.log(`[Performance] Skipped ${chartId} update (no significant change)`);
    }
    
    return updated;
}

// ============================================================================
// API OPTIMIZATION HELPERS
// ============================================================================

/**
 * Fetch with priority and queue management
 */
async function fetchOptimized(url, priority = 'normal') {
    if (!window.PerformanceOptimizer) {
        return fetch(url).then(r => r.json());
    }
    
    const priorityMap = {
        'high': window.PerformanceOptimizer.config.QUEUE.PRIORITY_HIGH,
        'normal': window.PerformanceOptimizer.config.QUEUE.PRIORITY_NORMAL,
        'low': window.PerformanceOptimizer.config.QUEUE.PRIORITY_LOW
    };
    
    return window.PerformanceOptimizer.optimizedFetch(
        url,
        {},
        priorityMap[priority] || priorityMap.normal
    );
}

/**
 * Batch fetch multiple endpoints with priorities
 */
async function fetchBatch(requests) {
    const promises = requests.map(({ url, priority }) => 
        fetchOptimized(url, priority)
    );
    
    return Promise.all(promises);
}

// ============================================================================
// DATA UPDATE HELPERS
// ============================================================================

/**
 * Update trades table with virtual scrolling
 */
function updateTradesTable(trades) {
    if (window.tradesScroller) {
        window.tradesScroller.setData(trades);
    } else {
        // Fallback to traditional rendering
        updateTradesTableTraditional(trades);
    }
}

/**
 * Update positions table with virtual scrolling
 */
function updatePositionsTable(positions) {
    if (window.positionsScroller) {
        window.positionsScroller.setData(positions);
    } else {
        // Fallback to traditional rendering
        updatePositionsTableTraditional(positions);
    }
}

// ============================================================================
// MIGRATION HELPERS
// ============================================================================

/**
 * Migrate existing refresh logic to use debouncing
 */
function migrateRefreshLogic() {
    // Replace direct setInterval with debounced version
    if (window.refreshInterval) {
        clearInterval(window.refreshInterval);
    }
    
    if (window.debouncedRefresh) {
        window.refreshInterval = setInterval(window.debouncedRefresh, 1000);
        console.log('[Performance] ✅ Migrated to debounced refresh');
    }
}

/**
 * Migrate chart updates to use caching
 */
function migrateChartUpdates() {
    // Store original update functions
    if (!window._originalChartUpdates) {
        window._originalChartUpdates = {};
        
        ['equity', 'pnl', 'correlation', 'drawdown'].forEach(chartId => {
            const updateFn = window[`update${chartId.charAt(0).toUpperCase() + chartId.slice(1)}Chart`];
            if (updateFn) {
                window._originalChartUpdates[chartId] = updateFn;
                
                // Replace with optimized version
                window[`update${chartId.charAt(0).toUpperCase() + chartId.slice(1)}Chart`] = function(data) {
                    updateChartOptimized(chartId, data);
                };
            }
        });
        
        console.log('[Performance] ✅ Migrated chart updates to use caching');
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
}

function formatPnL(value) {
    const prefix = value >= 0 ? '+' : '';
    return `${prefix}${value.toFixed(2)}`;
}

function updatePrices(data) {
    // Placeholder - implement actual price update logic
    console.log('[Performance] Price update:', data);
}

function updatePortfolio(data) {
    // Placeholder - implement actual portfolio update logic
    console.log('[Performance] Portfolio update:', data);
}

function updateTradesTableTraditional(trades) {
    // Fallback implementation
    console.warn('[Performance] Using traditional rendering (slow for 1000+ rows)');
}

function updatePositionsTableTraditional(positions) {
    // Fallback implementation
    console.warn('[Performance] Using traditional rendering (slow for 1000+ rows)');
}

// ============================================================================
// AUTO-INITIALIZATION
// ============================================================================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initPerformanceOptimizations();
        initOptimizedCharts();
        migrateRefreshLogic();
        migrateChartUpdates();
    });
} else {
    // DOM already loaded
    initPerformanceOptimizations();
    initOptimizedCharts();
    migrateRefreshLogic();
    migrateChartUpdates();
}

// Export functions for use in other modules
window.PerformanceIntegration = {
    initPerformanceOptimizations,
    initOptimizedCharts,
    updateChartOptimized,
    fetchOptimized,
    fetchBatch,
    updateTradesTable,
    updatePositionsTable,
    renderTradeRow,
    renderPositionRow
};

console.log('[Performance Integration] Module loaded successfully');
