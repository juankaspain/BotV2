// ==================== BotV2 Chart Mastery v7.1 ====================
// Advanced Chart Types & Annotation System
// Author: Juan Carlos Garcia
// Date: 24 Enero 2026

console.log('📊 Chart Mastery v7.1 initializing...');

// ==================== CHART LIBRARY ====================
const ChartMastery = {
    
    // ==================== 1. WIN/LOSS DISTRIBUTION ====================
    createWinLossDistribution: function(containerId, data) {
        const wins = data.wins || [];
        const losses = data.losses || [];
        
        const trace1 = {
            x: wins,
            type: 'histogram',
            name: 'Winning Trades',
            marker: {
                color: 'rgba(16, 185, 129, 0.7)',
                line: {
                    color: 'rgba(16, 185, 129, 1)',
                    width: 1
                }
            },
            opacity: 0.7,
            xbins: {
                size: (Math.max(...wins) - Math.min(...wins)) / 20
            }
        };
        
        const trace2 = {
            x: losses,
            type: 'histogram',
            name: 'Losing Trades',
            marker: {
                color: 'rgba(248, 81, 73, 0.7)',
                line: {
                    color: 'rgba(248, 81, 73, 1)',
                    width: 1
                }
            },
            opacity: 0.7,
            xbins: {
                size: (Math.max(...losses) - Math.min(...losses)) / 20
            }
        };
        
        const layout = {
            title: {
                text: 'Win/Loss Distribution',
                font: { size: 16, weight: 600, family: 'Inter' }
            },
            xaxis: {
                title: 'P&L (€)',
                gridcolor: 'rgba(255, 255, 255, 0.1)',
                zeroline: true,
                zerolinecolor: 'rgba(255, 255, 255, 0.3)',
                zerolinewidth: 2
            },
            yaxis: {
                title: 'Frequency',
                gridcolor: 'rgba(255, 255, 255, 0.1)'
            },
            barmode: 'overlay',
            bargap: 0.05,
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#e6edf3', family: 'Inter' },
            hovermode: 'closest',
            showlegend: true,
            legend: {
                x: 0.7,
                y: 0.95,
                bgcolor: 'rgba(22, 27, 34, 0.8)',
                bordercolor: 'rgba(48, 54, 61, 1)',
                borderwidth: 1
            },
            annotations: [{
                x: 0,
                y: 0,
                xref: 'x',
                yref: 'paper',
                text: 'Break-even',
                showarrow: true,
                arrowhead: 2,
                arrowsize: 1,
                arrowwidth: 2,
                arrowcolor: 'rgba(255, 255, 255, 0.5)',
                ax: 0,
                ay: -40,
                font: { size: 10, color: 'rgba(255, 255, 255, 0.7)' }
            }]
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d']
        };
        
        Plotly.newPlot(containerId, [trace1, trace2], layout, config);
        
        // Return stats
        return {
            winCount: wins.length,
            lossCount: losses.length,
            winRate: (wins.length / (wins.length + losses.length) * 100).toFixed(2),
            avgWin: (wins.reduce((a, b) => a + b, 0) / wins.length).toFixed(2),
            avgLoss: (losses.reduce((a, b) => a + b, 0) / losses.length).toFixed(2)
        };
    },
    
    // ==================== 2. CORRELATION MATRIX ====================
    createCorrelationMatrix: function(containerId, data) {
        const assets = data.assets || ['BTC', 'ETH', 'SPX', 'GOLD', 'EUR'];
        const correlations = data.correlations || [
            [1.0, 0.85, 0.45, 0.32, -0.15],
            [0.85, 1.0, 0.52, 0.28, -0.12],
            [0.45, 0.52, 1.0, 0.65, 0.23],
            [0.32, 0.28, 0.65, 1.0, 0.18],
            [-0.15, -0.12, 0.23, 0.18, 1.0]
        ];
        
        const trace = {
            z: correlations,
            x: assets,
            y: assets,
            type: 'heatmap',
            colorscale: [
                [0, 'rgb(248, 81, 73)'],      // Negative correlation
                [0.5, 'rgb(125, 133, 144)'],  // No correlation
                [1, 'rgb(16, 185, 129)']      // Positive correlation
            ],
            zmin: -1,
            zmax: 1,
            hoverongaps: false,
            hovertemplate: '<b>%{y} vs %{x}</b><br>Correlation: %{z:.3f}<extra></extra>',
            colorbar: {
                title: 'Correlation',
                titleside: 'right',
                tickmode: 'linear',
                tick0: -1,
                dtick: 0.5,
                thickness: 15,
                len: 0.7
            }
        };
        
        // Add text annotations
        const annotations = [];
        for (let i = 0; i < assets.length; i++) {
            for (let j = 0; j < assets.length; j++) {
                const textColor = Math.abs(correlations[i][j]) > 0.5 ? 'white' : '#e6edf3';
                annotations.push({
                    x: assets[j],
                    y: assets[i],
                    text: correlations[i][j].toFixed(2),
                    font: {
                        color: textColor,
                        size: 11,
                        weight: 600
                    },
                    showarrow: false
                });
            }
        }
        
        const layout = {
            title: {
                text: 'Asset Correlation Matrix',
                font: { size: 16, weight: 600, family: 'Inter' }
            },
            xaxis: {
                side: 'top',
                tickangle: -45
            },
            yaxis: {
                autorange: 'reversed'
            },
            annotations: annotations,
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#e6edf3', family: 'Inter' },
            margin: { t: 100, l: 80, r: 80, b: 80 }
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        };
        
        Plotly.newPlot(containerId, [trace], layout, config);
        
        // Return diversification score
        const avgCorrelation = correlations.flat()
            .filter((v, i) => i % (assets.length + 1) !== 0) // Exclude diagonal
            .reduce((a, b) => a + Math.abs(b), 0) / (assets.length * (assets.length - 1));
        
        return {
            avgCorrelation: avgCorrelation.toFixed(3),
            diversificationScore: ((1 - avgCorrelation) * 100).toFixed(1)
        };
    },
    
    // ==================== 3. RISK-RETURN SCATTER ====================
    createRiskReturnScatter: function(containerId, data) {
        const strategies = data.strategies || [];
        
        const trace = {
            x: strategies.map(s => s.risk),
            y: strategies.map(s => s.return),
            mode: 'markers+text',
            type: 'scatter',
            text: strategies.map(s => s.name),
            textposition: 'top center',
            textfont: {
                size: 10,
                color: '#e6edf3',
                weight: 600
            },
            marker: {
                size: strategies.map(s => (s.sharpe || 1) * 15),
                color: strategies.map(s => s.sharpe || 1),
                colorscale: [
                    [0, 'rgb(248, 81, 73)'],
                    [0.5, 'rgb(210, 153, 34)'],
                    [1, 'rgb(16, 185, 129)']
                ],
                showscale: true,
                colorbar: {
                    title: 'Sharpe Ratio',
                    thickness: 15,
                    len: 0.7
                },
                line: {
                    color: 'rgba(255, 255, 255, 0.3)',
                    width: 2
                },
                opacity: 0.8
            },
            hovertemplate: '<b>%{text}</b><br>' +
                          'Risk: %{x:.2f}%<br>' +
                          'Return: %{y:.2f}%<br>' +
                          '<extra></extra>'
        };
        
        // Efficient Frontier (simplified)
        const efficientX = [];
        const efficientY = [];
        for (let risk = 5; risk <= 30; risk += 0.5) {
            efficientX.push(risk);
            efficientY.push(Math.sqrt(risk) * 2 - risk * 0.1); // Simplified curve
        }
        
        const efficientFrontier = {
            x: efficientX,
            y: efficientY,
            mode: 'lines',
            name: 'Efficient Frontier',
            line: {
                color: 'rgba(47, 129, 247, 0.6)',
                width: 2,
                dash: 'dash'
            },
            hoverinfo: 'skip'
        };
        
        const layout = {
            title: {
                text: 'Risk-Return Analysis',
                font: { size: 16, weight: 600, family: 'Inter' }
            },
            xaxis: {
                title: 'Risk (Volatility %)',
                gridcolor: 'rgba(255, 255, 255, 0.1)',
                zeroline: false
            },
            yaxis: {
                title: 'Return (%)',
                gridcolor: 'rgba(255, 255, 255, 0.1)',
                zeroline: true,
                zerolinecolor: 'rgba(255, 255, 255, 0.3)',
                zerolinewidth: 2
            },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#e6edf3', family: 'Inter' },
            hovermode: 'closest',
            showlegend: true,
            legend: {
                x: 0.02,
                y: 0.98,
                bgcolor: 'rgba(22, 27, 34, 0.8)',
                bordercolor: 'rgba(48, 54, 61, 1)',
                borderwidth: 1
            }
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        };
        
        Plotly.newPlot(containerId, [efficientFrontier, trace], layout, config);
        
        // Return best strategy
        const bestStrategy = strategies.reduce((best, current) => 
            (current.sharpe || 0) > (best.sharpe || 0) ? current : best
        , strategies[0]);
        
        return {
            bestStrategy: bestStrategy.name,
            bestSharpe: bestStrategy.sharpe.toFixed(2),
            avgSharpe: (strategies.reduce((sum, s) => sum + (s.sharpe || 0), 0) / strategies.length).toFixed(2)
        };
    },
    
    // ==================== 4. TRADE DURATION BOX PLOT ====================
    createTradeDurationBoxPlot: function(containerId, data) {
        const winDurations = data.winDurations || [];
        const lossDurations = data.lossDurations || [];
        
        const trace1 = {
            y: winDurations,
            type: 'box',
            name: 'Winning Trades',
            marker: {
                color: 'rgba(16, 185, 129, 0.7)',
                outliercolor: 'rgba(16, 185, 129, 1)'
            },
            line: { color: 'rgba(16, 185, 129, 1)' },
            boxmean: 'sd',
            boxpoints: 'suspectedoutliers'
        };
        
        const trace2 = {
            y: lossDurations,
            type: 'box',
            name: 'Losing Trades',
            marker: {
                color: 'rgba(248, 81, 73, 0.7)',
                outliercolor: 'rgba(248, 81, 73, 1)'
            },
            line: { color: 'rgba(248, 81, 73, 1)' },
            boxmean: 'sd',
            boxpoints: 'suspectedoutliers'
        };
        
        const layout = {
            title: {
                text: 'Trade Duration Analysis',
                font: { size: 16, weight: 600, family: 'Inter' }
            },
            yaxis: {
                title: 'Duration (hours)',
                gridcolor: 'rgba(255, 255, 255, 0.1)',
                zeroline: false
            },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#e6edf3', family: 'Inter' },
            showlegend: true,
            legend: {
                x: 0.02,
                y: 0.98,
                bgcolor: 'rgba(22, 27, 34, 0.8)',
                bordercolor: 'rgba(48, 54, 61, 1)',
                borderwidth: 1
            }
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        };
        
        Plotly.newPlot(containerId, [trace1, trace2], layout, config);
        
        // Return statistics
        const median = arr => {
            const sorted = arr.slice().sort((a, b) => a - b);
            const mid = Math.floor(sorted.length / 2);
            return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
        };
        
        return {
            medianWinDuration: median(winDurations).toFixed(1),
            medianLossDuration: median(lossDurations).toFixed(1),
            optimalDuration: median([...winDurations, ...lossDurations]).toFixed(1)
        };
    },
    
    // ==================== 5. CHART ANNOTATIONS SYSTEM ====================
    addAnnotation: function(chartId, annotation) {
        const {
            x,
            y,
            text,
            type = 'point',  // point, line, range
            color = '#2f81f7',
            icon = '📍'
        } = annotation;
        
        const update = {
            'annotations[0]': {
                x: x,
                y: y,
                xref: 'x',
                yref: 'y',
                text: `${icon} ${text}`,
                showarrow: true,
                arrowhead: 2,
                arrowsize: 1,
                arrowwidth: 2,
                arrowcolor: color,
                ax: 0,
                ay: -40,
                font: {
                    size: 11,
                    color: '#e6edf3',
                    weight: 600
                },
                bgcolor: 'rgba(22, 27, 34, 0.9)',
                bordercolor: color,
                borderwidth: 2,
                borderpad: 4,
                opacity: 0.9
            }
        };
        
        Plotly.relayout(chartId, update);
    },
    
    addEventMarker: function(chartId, event) {
        const {
            date,
            title,
            description,
            type = 'neutral',  // success, warning, danger, neutral
            icon = '⚡'
        } = event;
        
        const colors = {
            success: '#10b981',
            warning: '#d29922',
            danger: '#f85149',
            neutral: '#2f81f7'
        };
        
        const shape = {
            type: 'line',
            x0: date,
            x1: date,
            y0: 0,
            y1: 1,
            yref: 'paper',
            line: {
                color: colors[type],
                width: 2,
                dash: 'dash'
            }
        };
        
        const annotation = {
            x: date,
            y: 1,
            yref: 'paper',
            text: `${icon} ${title}`,
            showarrow: true,
            arrowhead: 2,
            arrowcolor: colors[type],
            ax: 0,
            ay: -30,
            font: { size: 10, color: colors[type], weight: 600 },
            hovertext: description,
            hoverlabel: {
                bgcolor: 'rgba(22, 27, 34, 0.95)',
                bordercolor: colors[type],
                font: { size: 11 }
            }
        };
        
        Plotly.relayout(chartId, {
            shapes: [shape],
            annotations: [annotation]
        });
    },
    
    // ==================== 6. REAL COMPARISON OVERLAY ====================
    createComparisonChart: function(containerId, data) {
        const traces = [];
        const datasets = data.datasets || [];
        
        const colors = [
            '#2f81f7',
            '#10b981',
            '#d29922',
            '#f85149',
            '#8b5cf6'
        ];
        
        datasets.forEach((dataset, index) => {
            traces.push({
                x: dataset.dates,
                y: dataset.values,
                type: 'scatter',
                mode: 'lines',
                name: dataset.name,
                line: {
                    color: colors[index % colors.length],
                    width: 2
                },
                hovertemplate: `<b>${dataset.name}</b><br>` +
                              'Date: %{x|%Y-%m-%d}<br>' +
                              'Value: %{y:.2f}<br>' +
                              '<extra></extra>'
            });
        });
        
        const layout = {
            title: {
                text: data.title || 'Strategy Comparison',
                font: { size: 16, weight: 600, family: 'Inter' }
            },
            xaxis: {
                title: 'Date',
                gridcolor: 'rgba(255, 255, 255, 0.1)',
                type: 'date'
            },
            yaxis: {
                title: data.yAxisTitle || 'Value',
                gridcolor: 'rgba(255, 255, 255, 0.1)',
                zeroline: true,
                zerolinecolor: 'rgba(255, 255, 255, 0.3)',
                zerolinewidth: 2
            },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#e6edf3', family: 'Inter' },
            hovermode: 'x unified',
            showlegend: true,
            legend: {
                x: 0.02,
                y: 0.98,
                bgcolor: 'rgba(22, 27, 34, 0.8)',
                bordercolor: 'rgba(48, 54, 61, 1)',
                borderwidth: 1
            }
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToAdd: [{
                name: 'Toggle Relative',
                icon: Plotly.Icons.home,
                click: function(gd) {
                    // Toggle between absolute and relative values
                    console.log('Toggle relative view');
                }
            }]
        };
        
        Plotly.newPlot(containerId, traces, layout, config);
        
        // Return comparison stats
        const bestPerformer = datasets.reduce((best, current) => {
            const currentReturn = (current.values[current.values.length - 1] - current.values[0]) / current.values[0] * 100;
            const bestReturn = (best.values[best.values.length - 1] - best.values[0]) / best.values[0] * 100;
            return currentReturn > bestReturn ? current : best;
        }, datasets[0]);
        
        return {
            bestPerformer: bestPerformer.name,
            totalDatasets: datasets.length
        };
    },
    
    // ==================== CHART UTILITIES ====================
    updateChartTheme: function(chartId, theme) {
        const themes = {
            dark: {
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { color: '#e6edf3' }
            },
            light: {
                paper_bgcolor: '#ffffff',
                plot_bgcolor: '#f6f8fa',
                font: { color: '#1f2328' }
            },
            bloomberg: {
                paper_bgcolor: '#000000',
                plot_bgcolor: '#0a0a0a',
                font: { color: '#ff9900' }
            }
        };
        
        Plotly.relayout(chartId, themes[theme] || themes.dark);
    },
    
    exportChart: function(chartId, format = 'png') {
        const filename = `botv2-chart-${Date.now()}`;
        
        if (format === 'png') {
            Plotly.downloadImage(chartId, {
                format: 'png',
                width: 1200,
                height: 800,
                filename: filename
            });
        } else if (format === 'svg') {
            Plotly.downloadImage(chartId, {
                format: 'svg',
                width: 1200,
                height: 800,
                filename: filename
            });
        }
    }
};

// ==================== EXPORTS ====================
window.ChartMastery = ChartMastery;

console.log('✅ Chart Mastery v7.1 loaded with 6 chart types');
