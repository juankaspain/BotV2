/**
 * ========================================
 * BotV2 Dashboard - Chart Mastery v7.1
 * ========================================
 * 
 * Advanced Trading Charts Module
 * 
 * Features:
 * - Win/Loss Distribution Histogram
 * - Correlation Matrix Heatmap
 * - Risk-Return Scatter Plot
 * - Trade Duration Box Plot
 * - Real vs Expected Comparison
 * - Chart Annotations System
 * - Multi-timeframe Comparison
 * 
 * Dependencies:
 * - Plotly.js 2.27.0+
 * - visual-excellence.js
 * 
 * @version 7.1.0
 * @author Juan Carlos Garcia
 * @date 24 Enero 2026
 */

(function(window) {
    'use strict';

    /**
     * Default Plotly layout for all charts
     */
    const DEFAULT_LAYOUT = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {
            family: 'Inter, sans-serif',
            size: 12,
            color: '#e6edf3'
        },
        margin: { t: 40, r: 20, b: 60, l: 60 },
        hoverlabel: {
            bgcolor: '#21262d',
            bordercolor: '#30363d',
            font: { family: 'Inter, sans-serif', size: 12 }
        },
        showlegend: true,
        legend: {
            orientation: 'h',
            yanchor: 'bottom',
            y: 1.02,
            xanchor: 'right',
            x: 1,
            bgcolor: 'rgba(0,0,0,0)'
        }
    };

    /**
     * Default Plotly config for all charts
     */
    const DEFAULT_CONFIG = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        toImageButtonOptions: {
            format: 'png',
            filename: 'botv2_chart',
            height: 800,
            width: 1200,
            scale: 2
        }
    };

    /**
     * Chart Mastery Class
     */
    class ChartMastery {
        constructor() {
            this.charts = new Map();
            this.theme = document.documentElement.getAttribute('data-theme') || 'dark';
            this.initThemeListener();
        }

        /**
         * Listen for theme changes
         */
        initThemeListener() {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName === 'data-theme') {
                        this.theme = document.documentElement.getAttribute('data-theme');
                        this.updateAllChartsTheme();
                    }
                });
            });

            observer.observe(document.documentElement, {
                attributes: true,
                attributeFilter: ['data-theme']
            });
        }

        /**
         * Update all charts when theme changes
         */
        updateAllChartsTheme() {
            this.charts.forEach((chartData, elementId) => {
                const element = document.getElementById(elementId);
                if (element && chartData.updateFn) {
                    chartData.updateFn();
                }
            });
        }

        /**
         * Get theme-aware colors
         */
        getThemeColors() {
            const colors = {
                dark: {
                    primary: '#2f81f7',
                    success: '#3fb950',
                    danger: '#f85149',
                    warning: '#d29922',
                    text: '#e6edf3',
                    textSecondary: '#7d8590',
                    bg: '#0d1117',
                    bgSecondary: '#161b22',
                    border: '#30363d',
                    grid: '#21262d'
                },
                light: {
                    primary: '#0969da',
                    success: '#1a7f37',
                    danger: '#cf222e',
                    warning: '#bf8700',
                    text: '#1f2328',
                    textSecondary: '#656d76',
                    bg: '#ffffff',
                    bgSecondary: '#f6f8fa',
                    border: '#d0d7de',
                    grid: '#e7ecf0'
                },
                bloomberg: {
                    primary: '#ff9900',
                    success: '#00ff00',
                    danger: '#ff0000',
                    warning: '#ffff00',
                    text: '#ff9900',
                    textSecondary: '#cc7700',
                    bg: '#000000',
                    bgSecondary: '#0a0a0a',
                    border: '#2a2a2a',
                    grid: '#1a1a1a'
                }
            };

            return colors[this.theme] || colors.dark;
        }

        /**
         * Get themed layout
         */
        getThemedLayout(customLayout = {}) {
            const colors = this.getThemeColors();
            return {
                ...DEFAULT_LAYOUT,
                font: { ...DEFAULT_LAYOUT.font, color: colors.text },
                xaxis: {
                    gridcolor: colors.grid,
                    zerolinecolor: colors.border,
                    color: colors.textSecondary,
                    ...customLayout.xaxis
                },
                yaxis: {
                    gridcolor: colors.grid,
                    zerolinecolor: colors.border,
                    color: colors.textSecondary,
                    ...customLayout.yaxis
                },
                ...customLayout
            };
        }

        /**
         * 1. Win/Loss Distribution Histogram
         */
        createWinLossDistribution(elementId, trades) {
            const colors = this.getThemeColors();
            
            const winningTrades = trades.filter(t => t.profit > 0).map(t => t.profit);
            const losingTrades = trades.filter(t => t.profit <= 0).map(t => t.profit);

            const trace1 = {
                x: winningTrades,
                type: 'histogram',
                name: 'Winning Trades',
                marker: {
                    color: colors.success,
                    opacity: 0.7,
                    line: { color: colors.success, width: 1 }
                },
                hovertemplate: 'Profit: %{x:.2f}<br>Count: %{y}<extra></extra>'
            };

            const trace2 = {
                x: losingTrades,
                type: 'histogram',
                name: 'Losing Trades',
                marker: {
                    color: colors.danger,
                    opacity: 0.7,
                    line: { color: colors.danger, width: 1 }
                },
                hovertemplate: 'Loss: %{x:.2f}<br>Count: %{y}<extra></extra>'
            };

            const layout = this.getThemedLayout({
                title: 'Win/Loss Distribution',
                xaxis: { title: 'Profit/Loss (€)' },
                yaxis: { title: 'Frequency' },
                barmode: 'overlay',
                bargap: 0.1
            });

            const updateFn = () => this.createWinLossDistribution(elementId, trades);
            this.charts.set(elementId, { updateFn });

            return Plotly.newPlot(elementId, [trace1, trace2], layout, DEFAULT_CONFIG);
        }

        /**
         * 2. Correlation Matrix Heatmap
         */
        createCorrelationMatrix(elementId, assets, returns) {
            const colors = this.getThemeColors();
            
            // Calculate correlation matrix
            const n = assets.length;
            const correlationMatrix = [];
            
            for (let i = 0; i < n; i++) {
                const row = [];
                for (let j = 0; j < n; j++) {
                    row.push(this.calculateCorrelation(returns[i], returns[j]));
                }
                correlationMatrix.push(row);
            }

            const trace = {
                z: correlationMatrix,
                x: assets,
                y: assets,
                type: 'heatmap',
                colorscale: [
                    [0, colors.danger],
                    [0.5, colors.bg],
                    [1, colors.success]
                ],
                zmin: -1,
                zmax: 1,
                hovertemplate: '%{y} vs %{x}<br>Correlation: %{z:.2f}<extra></extra>',
                colorbar: {
                    title: 'Correlation',
                    titleside: 'right'
                }
            };

            // Add annotations with correlation values
            const annotations = [];
            for (let i = 0; i < n; i++) {
                for (let j = 0; j < n; j++) {
                    annotations.push({
                        x: assets[j],
                        y: assets[i],
                        text: correlationMatrix[i][j].toFixed(2),
                        showarrow: false,
                        font: {
                            color: Math.abs(correlationMatrix[i][j]) > 0.5 ? '#ffffff' : colors.text,
                            size: 10
                        }
                    });
                }
            }

            const layout = this.getThemedLayout({
                title: 'Asset Correlation Matrix',
                annotations: annotations,
                xaxis: { side: 'bottom' },
                yaxis: { side: 'left' }
            });

            const updateFn = () => this.createCorrelationMatrix(elementId, assets, returns);
            this.charts.set(elementId, { updateFn });

            return Plotly.newPlot(elementId, [trace], layout, DEFAULT_CONFIG);
        }

        /**
         * Calculate Pearson correlation coefficient
         */
        calculateCorrelation(x, y) {
            const n = x.length;
            const sum_x = x.reduce((a, b) => a + b, 0);
            const sum_y = y.reduce((a, b) => a + b, 0);
            const sum_xy = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
            const sum_x2 = x.reduce((sum, xi) => sum + xi * xi, 0);
            const sum_y2 = y.reduce((sum, yi) => sum + yi * yi, 0);

            const numerator = n * sum_xy - sum_x * sum_y;
            const denominator = Math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y));

            return denominator === 0 ? 0 : numerator / denominator;
        }

        /**
         * 3. Risk-Return Scatter Plot
         */
        createRiskReturnScatter(elementId, strategies) {
            const colors = this.getThemeColors();

            const trace = {
                x: strategies.map(s => s.volatility),
                y: strategies.map(s => s.return),
                mode: 'markers+text',
                type: 'scatter',
                text: strategies.map(s => s.name),
                textposition: 'top center',
                textfont: { size: 10, color: colors.text },
                marker: {
                    size: strategies.map(s => s.sharpe * 10 + 10),
                    color: strategies.map(s => s.sharpe),
                    colorscale: [
                        [0, colors.danger],
                        [0.5, colors.warning],
                        [1, colors.success]
                    ],
                    showscale: true,
                    colorbar: {
                        title: 'Sharpe Ratio',
                        titleside: 'right'
                    },
                    line: { color: colors.border, width: 1 }
                },
                hovertemplate: '<b>%{text}</b><br>' +
                              'Risk (Volatility): %{x:.2f}%<br>' +
                              'Return: %{y:.2f}%<br>' +
                              '<extra></extra>'
            };

            const layout = this.getThemedLayout({
                title: 'Risk-Return Analysis',
                xaxis: { title: 'Risk (Volatility %)' },
                yaxis: { title: 'Return (%)' },
                showlegend: false
            });

            const updateFn = () => this.createRiskReturnScatter(elementId, strategies);
            this.charts.set(elementId, { updateFn });

            return Plotly.newPlot(elementId, [trace], layout, DEFAULT_CONFIG);
        }

        /**
         * 4. Trade Duration Box Plot
         */
        createTradeDurationBoxPlot(elementId, tradesByStrategy) {
            const colors = this.getThemeColors();

            const traces = Object.keys(tradesByStrategy).map((strategy, idx) => {
                const durations = tradesByStrategy[strategy].map(t => t.duration);
                
                return {
                    y: durations,
                    type: 'box',
                    name: strategy,
                    marker: { color: this.getColorByIndex(idx) },
                    boxmean: 'sd',
                    hovertemplate: '<b>' + strategy + '</b><br>' +
                                  'Duration: %{y} hours<br>' +
                                  '<extra></extra>'
                };
            });

            const layout = this.getThemedLayout({
                title: 'Trade Duration by Strategy',
                yaxis: { title: 'Duration (hours)' },
                xaxis: { title: 'Strategy' }
            });

            const updateFn = () => this.createTradeDurationBoxPlot(elementId, tradesByStrategy);
            this.charts.set(elementId, { updateFn });

            return Plotly.newPlot(elementId, traces, layout, DEFAULT_CONFIG);
        }

        /**
         * 5. Real vs Expected Comparison Overlay
         */
        createComparisonOverlay(elementId, dates, realData, expectedData, metric) {
            const colors = this.getThemeColors();

            const trace1 = {
                x: dates,
                y: realData,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Real ' + metric,
                line: { color: colors.primary, width: 2 },
                marker: { size: 6 },
                hovertemplate: '%{x}<br>Real: %{y:.2f}<extra></extra>'
            };

            const trace2 = {
                x: dates,
                y: expectedData,
                type: 'scatter',
                mode: 'lines',
                name: 'Expected ' + metric,
                line: { color: colors.warning, width: 2, dash: 'dash' },
                hovertemplate: '%{x}<br>Expected: %{y:.2f}<extra></extra>'
            };

            // Add shaded area showing difference
            const trace3 = {
                x: [...dates, ...dates.reverse()],
                y: [...realData, ...expectedData.reverse()],
                fill: 'toself',
                fillcolor: 'rgba(47, 129, 247, 0.1)',
                line: { color: 'transparent' },
                showlegend: false,
                hoverinfo: 'skip'
            };

            const layout = this.getThemedLayout({
                title: `Real vs Expected ${metric}`,
                xaxis: { title: 'Date' },
                yaxis: { title: metric }
            });

            const updateFn = () => this.createComparisonOverlay(elementId, dates, realData, expectedData, metric);
            this.charts.set(elementId, { updateFn });

            return Plotly.newPlot(elementId, [trace3, trace1, trace2], layout, DEFAULT_CONFIG);
        }

        /**
         * 6. Drawdown with Annotations
         */
        createDrawdownChart(elementId, dates, equity, drawdowns, events = []) {
            const colors = this.getThemeColors();

            const trace1 = {
                x: dates,
                y: equity,
                type: 'scatter',
                mode: 'lines',
                name: 'Equity',
                line: { color: colors.primary, width: 2 },
                yaxis: 'y1',
                hovertemplate: '%{x}<br>Equity: €%{y:,.2f}<extra></extra>'
            };

            const trace2 = {
                x: dates,
                y: drawdowns,
                type: 'scatter',
                mode: 'lines',
                name: 'Drawdown',
                fill: 'tozeroy',
                fillcolor: 'rgba(248, 81, 73, 0.2)',
                line: { color: colors.danger, width: 1 },
                yaxis: 'y2',
                hovertemplate: '%{x}<br>Drawdown: %{y:.2f}%<extra></extra>'
            };

            // Create annotations for important events
            const annotations = events.map(event => ({
                x: event.date,
                y: event.value,
                xref: 'x',
                yref: 'y1',
                text: event.label,
                showarrow: true,
                arrowhead: 2,
                arrowsize: 1,
                arrowwidth: 2,
                arrowcolor: colors.warning,
                ax: 0,
                ay: -40,
                bgcolor: colors.bgSecondary,
                bordercolor: colors.border,
                borderwidth: 1,
                borderpad: 4,
                font: { size: 10, color: colors.text }
            }));

            const layout = this.getThemedLayout({
                title: 'Equity Curve with Drawdown',
                xaxis: { title: 'Date' },
                yaxis: {
                    title: 'Equity (€)',
                    side: 'left'
                },
                yaxis2: {
                    title: 'Drawdown (%)',
                    overlaying: 'y',
                    side: 'right'
                },
                annotations: annotations
            });

            const updateFn = () => this.createDrawdownChart(elementId, dates, equity, drawdowns, events);
            this.charts.set(elementId, { updateFn });

            return Plotly.newPlot(elementId, [trace1, trace2], layout, DEFAULT_CONFIG);
        }

        /**
         * 7. Multi-Timeframe Comparison
         */
        createMultiTimeframeComparison(elementId, timeframes) {
            const colors = this.getThemeColors();

            const traces = timeframes.map((tf, idx) => ({
                x: tf.dates,
                y: tf.returns,
                type: 'scatter',
                mode: 'lines',
                name: tf.name,
                line: {
                    color: this.getColorByIndex(idx),
                    width: 2
                },
                hovertemplate: '<b>' + tf.name + '</b><br>' +
                              '%{x}<br>' +
                              'Return: %{y:.2f}%<br>' +
                              '<extra></extra>'
            }));

            const layout = this.getThemedLayout({
                title: 'Performance Across Timeframes',
                xaxis: { title: 'Date' },
                yaxis: { title: 'Cumulative Return (%)' }
            });

            const updateFn = () => this.createMultiTimeframeComparison(elementId, timeframes);
            this.charts.set(elementId, { updateFn });

            return Plotly.newPlot(elementId, traces, layout, DEFAULT_CONFIG);
        }

        /**
         * Helper: Get color by index
         */
        getColorByIndex(idx) {
            const colors = this.getThemeColors();
            const palette = [
                colors.primary,
                colors.success,
                colors.warning,
                colors.danger,
                '#8b5cf6',
                '#ec4899',
                '#06b6d4'
            ];
            return palette[idx % palette.length];
        }

        /**
         * Add custom annotation to any chart
         */
        addAnnotation(elementId, annotation) {
            const element = document.getElementById(elementId);
            if (!element) return;

            const colors = this.getThemeColors();
            const defaultAnnotation = {
                showarrow: true,
                arrowhead: 2,
                arrowcolor: colors.warning,
                bgcolor: colors.bgSecondary,
                bordercolor: colors.border,
                borderwidth: 1,
                font: { color: colors.text }
            };

            const update = {
                annotations: [{ ...defaultAnnotation, ...annotation }]
            };

            return Plotly.relayout(elementId, update);
        }

        /**
         * Remove all annotations from a chart
         */
        clearAnnotations(elementId) {
            return Plotly.relayout(elementId, { annotations: [] });
        }

        /**
         * Export chart as image
         */
        exportChart(elementId, filename = 'chart', format = 'png') {
            return Plotly.downloadImage(elementId, {
                format: format,
                filename: filename,
                height: 800,
                width: 1200,
                scale: 2
            });
        }

        /**
         * Destroy a chart
         */
        destroyChart(elementId) {
            this.charts.delete(elementId);
            return Plotly.purge(elementId);
        }

        /**
         * Destroy all charts
         */
        destroyAll() {
            this.charts.forEach((_, elementId) => {
                Plotly.purge(elementId);
            });
            this.charts.clear();
        }
    }

    // Export to window
    window.ChartMastery = new ChartMastery();

    console.log('📊 Chart Mastery v7.1 loaded successfully');

})(window);
