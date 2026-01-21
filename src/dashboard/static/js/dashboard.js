/**
 * BotV2 Professional Dashboard JavaScript
 * Real-time updates via WebSocket
 * Advanced charting and interactions
 */

class Dashboard {
    constructor() {
        this.socket = null;
        this.charts = {};
        this.data = {};
        this.theme = localStorage.getItem('theme') || 'dark';
        
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing BotV2 Dashboard...');
        
        // Apply theme
        this.applyTheme();
        
        // Connect WebSocket
        this.connectWebSocket();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initial data fetch
        this.fetchInitialData();
        
        // Setup periodic refresh (fallback)
        setInterval(() => this.refreshData(), 30000); // 30 seconds
    }
    
    connectWebSocket() {
        console.log('🔌 Connecting to WebSocket...');
        
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('✅ WebSocket connected');
            this.updateConnectionStatus('connected');
        });
        
        this.socket.on('disconnect', () => {
            console.log('❌ WebSocket disconnected');
            this.updateConnectionStatus('disconnected');
        });
        
        this.socket.on('update', (data) => {
            console.log('🔄 Received update', data);
            this.handleUpdate(data);
        });
        
        this.socket.on('alert', (alert) => {
            console.log('🚨 Alert:', alert);
            this.showAlert(alert);
        });
        
        this.socket.on('error', (error) => {
            console.error('❌ Socket error:', error);
        });
    }
    
    updateConnectionStatus(status) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-text');
        
        statusDot.className = 'status-dot ' + status;
        
        const statusMessages = {
            'connected': 'Conectado',
            'connecting': 'Conectando...',
            'disconnected': 'Desconectado'
        };
        
        statusText.textContent = statusMessages[status] || status;
    }
    
    async fetchInitialData() {
        console.log('📊 Fetching initial data...');
        
        try {
            const [overview, equity, trades, strategies, risk, correlation, attribution] = await Promise.all([
                fetch('/api/overview').then(r => r.json()),
                fetch('/api/equity').then(r => r.json()),
                fetch('/api/trades').then(r => r.json()),
                fetch('/api/strategies').then(r => r.json()),
                fetch('/api/risk').then(r => r.json()),
                fetch('/api/correlation').then(r => r.json()),
                fetch('/api/attribution').then(r => r.json())
            ]);
            
            this.handleUpdate({
                overview,
                equity,
                trades,
                strategies,
                risk,
                correlation,
                attribution
            });
            
            console.log('✅ Initial data loaded');
        } catch (error) {
            console.error('❌ Error fetching data:', error);
            this.showAlert({
                level: 'danger',
                message: 'Error al cargar datos iniciales'
            });
        }
    }
    
    handleUpdate(data) {
        if (data.overview) {
            this.updateOverview(data.overview);
        }
        
        if (data.equity) {
            this.updateEquityChart(data.equity);
        }
        
        if (data.trades) {
            this.updateTradesTable(data.trades);
        }
        
        if (data.strategies) {
            this.updateStrategiesChart(data.strategies);
        }
        
        if (data.risk) {
            this.updateRiskMetrics(data.risk);
        }
        
        if (data.correlation) {
            this.updateCorrelationHeatmap(data.correlation);
        }
        
        if (data.attribution) {
            this.updateAttributionChart(data.attribution);
        }
        
        // Update timestamp
        document.getElementById('last-update').textContent = 
            `Last update: ${new Date().toLocaleTimeString()}`;
    }
    
    updateOverview(data) {
        // Equity
        document.getElementById('equity-value').textContent = 
            `€${this.formatNumber(data.equity)}`;
        
        const equityChange = document.getElementById('equity-change');
        equityChange.textContent = this.formatPercent(data.daily_change_pct);
        equityChange.className = 'metric-change ' + (data.daily_change_pct >= 0 ? 'positive' : 'negative');
        
        // P&L
        const totalReturn = data.total_return;
        const initialEquity = data.equity / (1 + totalReturn / 100);
        const pnl = data.equity - initialEquity;
        
        document.getElementById('pnl-value').textContent = 
            `€${this.formatNumber(pnl)}`;
        
        const pnlChange = document.getElementById('pnl-change');
        pnlChange.textContent = this.formatPercent(totalReturn);
        pnlChange.className = 'metric-change ' + (totalReturn >= 0 ? 'positive' : 'negative');
        
        // Win Rate
        document.getElementById('winrate-value').textContent = 
            `${data.win_rate.toFixed(1)}%`;
        document.getElementById('trades-count').textContent = 
            `${data.total_trades} trades`;
        
        // Sharpe
        const sharpe = data.sharpe_ratio;
        document.getElementById('sharpe-value').textContent = sharpe.toFixed(2);
        document.getElementById('sharpe-rating').textContent = this.getSharpeRating(sharpe);
        
        // Drawdown
        document.getElementById('drawdown-value').textContent = 
            `${Math.abs(data.max_drawdown).toFixed(2)}%`;
        document.getElementById('current-dd').textContent = 
            `Actual: ${Math.abs(data.max_drawdown).toFixed(2)}%`;
    }
    
    updateEquityChart(data) {
        const trace1 = {
            x: data.timestamps,
            y: data.equity,
            type: 'scatter',
            mode: 'lines',
            name: 'Equity',
            line: {
                color: '#00d4aa',
                width: 2
            },
            fill: 'tozeroy',
            fillcolor: 'rgba(0, 212, 170, 0.1)'
        };
        
        const trace2 = {
            x: data.timestamps,
            y: data.sma_20,
            type: 'scatter',
            mode: 'lines',
            name: 'SMA 20',
            line: {
                color: '#00a3ff',
                width: 1,
                dash: 'dot'
            }
        };
        
        const trace3 = {
            x: data.timestamps,
            y: data.sma_50,
            type: 'scatter',
            mode: 'lines',
            name: 'SMA 50',
            line: {
                color: '#ffa502',
                width: 1,
                dash: 'dot'
            }
        };
        
        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: {
                color: getComputedStyle(document.documentElement)
                    .getPropertyValue('--text-primary').trim()
            },
            xaxis: {
                gridcolor: getComputedStyle(document.documentElement)
                    .getPropertyValue('--border-color').trim(),
                showgrid: true
            },
            yaxis: {
                gridcolor: getComputedStyle(document.documentElement)
                    .getPropertyValue('--border-color').trim(),
                showgrid: true,
                tickprefix: '€'
            },
            margin: { t: 20, r: 20, b: 40, l: 60 },
            hovermode: 'x unified',
            showlegend: true,
            legend: {
                orientation: 'h',
                y: -0.2
            }
        };
        
        const config = {
            responsive: true,
            displayModeBar: false
        };
        
        Plotly.newPlot('equity-chart', [trace1, trace2, trace3], layout, config);
    }
    
    updateTradesTable(data) {
        const tbody = document.getElementById('trades-tbody');
        tbody.innerHTML = '';
        
        if (!data.trades || data.trades.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 2rem; color: var(--text-tertiary);">No hay trades aún</td></tr>';
            return;
        }
        
        // Show last 20 trades
        const trades = data.trades.slice(-20).reverse();
        
        trades.forEach(trade => {
            const row = document.createElement('tr');
            
            const pnlClass = trade.pnl >= 0 ? 'pnl-positive' : 'pnl-negative';
            const actionClass = trade.action.toLowerCase();
            
            row.innerHTML = `
                <td>${new Date(trade.timestamp).toLocaleString()}</td>
                <td>${trade.strategy}</td>
                <td>${trade.symbol}</td>
                <td><span class="trade-action ${actionClass}">${trade.action}</span></td>
                <td>${trade.size.toFixed(4)}</td>
                <td>€${trade.entry_price.toFixed(2)}</td>
                <td class="${pnlClass}">€${trade.pnl.toFixed(2)}</td>
                <td class="${pnlClass}">${trade.pnl_pct.toFixed(2)}%</td>
                <td>${(trade.confidence * 100).toFixed(0)}%</td>
            `;
            
            tbody.appendChild(row);
        });
    }
    
    updateStrategiesChart(data) {
        if (!data.strategies || data.strategies.length === 0) {
            return;
        }
        
        const strategies = data.strategies;
        const names = strategies.map(s => s.name);
        const returns = strategies.map(s => s.total_return);
        const colors = returns.map(r => r >= 0 ? '#26de81' : '#ff4757');
        
        const trace = {
            x: names,
            y: returns,
            type: 'bar',
            marker: {
                color: colors
            },
            text: returns.map(r => r.toFixed(2) + '%'),
            textposition: 'auto'
        };
        
        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: {
                color: getComputedStyle(document.documentElement)
                    .getPropertyValue('--text-primary').trim()
            },
            xaxis: {
                gridcolor: getComputedStyle(document.documentElement)
                    .getPropertyValue('--border-color').trim()
            },
            yaxis: {
                gridcolor: getComputedStyle(document.documentElement)
                    .getPropertyValue('--border-color').trim(),
                ticksuffix: '%'
            },
            margin: { t: 20, r: 20, b: 100, l: 60 }
        };
        
        const config = {
            responsive: true,
            displayModeBar: false
        };
        
        Plotly.newPlot('strategies-chart', [trace], layout, config);
    }
    
    updateRiskMetrics(data) {
        const container = document.getElementById('risk-metrics');
        container.innerHTML = '';
        
        const metrics = [
            { label: 'Sharpe Ratio', value: data.sharpe_ratio.toFixed(2) },
            { label: 'Sortino Ratio', value: data.sortino_ratio.toFixed(2) },
            { label: 'Calmar Ratio', value: data.calmar_ratio.toFixed(2) },
            { label: 'Max Drawdown', value: data.max_drawdown.toFixed(2) + '%' },
            { label: 'Current DD', value: data.current_drawdown.toFixed(2) + '%' },
            { label: 'Volatility', value: data.volatility.toFixed(2) + '%' },
            { label: 'VaR 95%', value: data.var_95.toFixed(2) + '%' },
            { label: 'CVaR 95%', value: data.cvar_95.toFixed(2) + '%' }
        ];
        
        metrics.forEach(metric => {
            const div = document.createElement('div');
            div.className = 'risk-metric';
            div.innerHTML = `
                <div class="risk-metric-label">${metric.label}</div>
                <div class="risk-metric-value">${metric.value}</div>
            `;
            container.appendChild(div);
        });
    }
    
    updateCorrelationHeatmap(data) {
        if (!data.strategies || data.strategies.length === 0) {
            return;
        }
        
        const trace = {
            z: data.matrix,
            x: data.strategies,
            y: data.strategies,
            type: 'heatmap',
            colorscale: [
                [0, '#ff4757'],
                [0.5, '#ffffff'],
                [1, '#26de81']
            ],
            zmin: -1,
            zmax: 1
        };
        
        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: {
                color: getComputedStyle(document.documentElement)
                    .getPropertyValue('--text-primary').trim(),
                size: 10
            },
            margin: { t: 20, r: 20, b: 100, l: 100 }
        };
        
        const config = {
            responsive: true,
            displayModeBar: false
        };
        
        Plotly.newPlot('correlation-heatmap', [trace], layout, config);
    }
    
    updateAttributionChart(data) {
        if (!data.attribution || data.attribution.length === 0) {
            return;
        }
        
        const attribution = data.attribution;
        const labels = attribution.map(a => a.strategy);
        const values = attribution.map(a => Math.abs(a.contribution_pct));
        
        const trace = {
            labels: labels,
            values: values,
            type: 'pie',
            hole: 0.4,
            marker: {
                colors: this.generateColors(labels.length)
            }
        };
        
        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: {
                color: getComputedStyle(document.documentElement)
                    .getPropertyValue('--text-primary').trim()
            },
            margin: { t: 20, r: 20, b: 20, l: 20 },
            showlegend: true,
            legend: {
                orientation: 'v',
                x: 1.1,
                y: 0.5
            }
        };
        
        const config = {
            responsive: true,
            displayModeBar: false
        };
        
        Plotly.newPlot('attribution-chart', [trace], layout, config);
    }
    
    showAlert(alert) {
        const alertsBar = document.getElementById('alerts-bar');
        
        const div = document.createElement('div');
        div.className = `alert ${alert.level || 'info'}`;
        div.innerHTML = `
            <span style="font-size: 1.25rem;">${this.getAlertIcon(alert.level)}</span>
            <span style="flex: 1;">${alert.message}</span>
            <span style="font-size: 0.75rem; color: var(--text-tertiary);">
                ${new Date(alert.timestamp).toLocaleTimeString()}
            </span>
        `;
        
        alertsBar.appendChild(div);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            div.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => div.remove(), 300);
        }, 10000);
    }
    
    setupEventListeners() {
        // Theme toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });
        
        // Export
        document.getElementById('export-btn').addEventListener('click', () => {
            this.exportReport();
        });
        
        // Fullscreen
        document.getElementById('fullscreen-btn').addEventListener('click', () => {
            this.toggleFullscreen();
        });
        
        // Refresh trades
        document.getElementById('refresh-trades').addEventListener('click', () => {
            this.refreshData();
        });
    }
    
    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('theme', this.theme);
        this.applyTheme();
        
        // Redraw charts with new theme
        this.fetchInitialData();
    }
    
    applyTheme() {
        const body = document.body;
        const icon = document.getElementById('theme-icon');
        
        if (this.theme === 'dark') {
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
            icon.textContent = '☾';
        } else {
            body.classList.remove('dark-theme');
            body.classList.add('light-theme');
            icon.textContent = '☀';
        }
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
    
    async exportReport() {
        try {
            const response = await fetch('/api/export/report?format=pdf');
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `botv2_report_${new Date().toISOString().split('T')[0]}.pdf`;
            a.click();
            
            this.showAlert({
                level: 'success',
                message: 'Reporte exportado exitosamente'
            });
        } catch (error) {
            console.error('Export error:', error);
            this.showAlert({
                level: 'danger',
                message: 'Error al exportar reporte'
            });
        }
    }
    
    async refreshData() {
        await this.fetchInitialData();
        this.showAlert({
            level: 'info',
            message: 'Datos actualizados'
        });
    }
    
    // Utility methods
    formatNumber(num) {
        return new Intl.NumberFormat('es-ES', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(num);
    }
    
    formatPercent(num) {
        return `${num >= 0 ? '+' : ''}${num.toFixed(2)}%`;
    }
    
    getSharpeRating(sharpe) {
        if (sharpe < 0) return 'Malo';
        if (sharpe < 1) return 'Aceptable';
        if (sharpe < 2) return 'Bueno';
        if (sharpe < 3) return 'Muy Bueno';
        return 'Excelente';
    }
    
    getAlertIcon(level) {
        const icons = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'danger': '🚨',
            'success': '✅'
        };
        return icons[level] || '🔔';
    }
    
    generateColors(count) {
        const colors = [
            '#00d4aa', '#00a3ff', '#ffa502', '#ff4757',
            '#26de81', '#a55eea', '#fd79a8', '#fdcb6e'
        ];
        return Array(count).fill(0).map((_, i) => colors[i % colors.length]);
    }
}

// Initialize dashboard when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.dashboard = new Dashboard();
    });
} else {
    window.dashboard = new Dashboard();
}
