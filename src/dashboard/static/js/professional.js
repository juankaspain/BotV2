/**
 * PROFESSIONAL DASHBOARD - INTERACTIVITY LAYER
 * Real-time updates, animations, and user interactions
 */

// Alpine.js State Management
function dashboardState() {
  return {
    // UI State
    darkMode: true,
    realtimeActive: true,
    connectionStatus: 'Conectando...',
    statusClass: 'connecting',
    
    // Data
    portfolioValue: 0,
    totalPnL: 0,
    winRate: 0,
    sharpeRatio: 0,
    maxDrawdown: 0,
    volatility: 0,
    
    // Time
    currentTime: '00:00:00',
    lastUpdate: '--:--:--',
    dataLatency: 0,
    
    // Methods
    init() {
      this.updateTime();
      this.initWebSocket();
      this.initCharts();
      this.loadInitialData();
      setInterval(() => this.updateTime(), 1000);
    },
    
    updateTime() {
      const now = new Date();
      this.currentTime = now.toLocaleTimeString('es-ES');
    },
    
    toggleTheme() {
      this.darkMode = !this.darkMode;
      document.body.classList.toggle('light-theme');
      localStorage.setItem('theme', this.darkMode ? 'dark' : 'light');
    },
    
    toggleRealtime() {
      this.realtimeActive = !this.realtimeActive;
      if (this.realtimeActive) {
        this.startRealtime();
      } else {
        this.stopRealtime();
      }
    },
    
    toggleFullscreen() {
      const elem = document.documentElement;
      if (elem.requestFullscreen) {
        elem.requestFullscreen();
      }
    },
    
    exportReport() {
      const report = this.generateReport();
      const blob = new Blob([report], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `BotV2_Report_${new Date().toISOString()}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    },
    
    initWebSocket() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const socket = io({
        reconnectionDelay: 1000,
        reconnection: true,
        reconnectionAttempts: Infinity,
        transports: ['websocket']
      });
      
      socket.on('connect', () => {
        this.connectionStatus = 'Conectado';
        this.statusClass = 'connected';
        console.log('✓ WebSocket connected');
      });
      
      socket.on('disconnect', () => {
        this.connectionStatus = 'Desconectado';
        this.statusClass = 'disconnected';
        console.warn('✗ WebSocket disconnected');
      });
      
      socket.on('portfolio_update', (data) => {
        this.updatePortfolioMetrics(data);
        this.updateCharts();
      });
      
      socket.on('trade_executed', (data) => {
        this.addTradeToTable(data);
        this.showNotification('Trade Executed', `${data.symbol} - ${data.action}`);
      });
      
      window.socket = socket;
    },
    
    loadInitialData() {
      fetch('/api/dashboard/metrics')
        .then(res => res.json())
        .then(data => {
          this.portfolioValue = data.portfolio_value || 0;
          this.totalPnL = data.total_pnl || 0;
          this.winRate = data.win_rate || 0;
          this.sharpeRatio = data.sharpe_ratio || 0;
          this.maxDrawdown = data.max_drawdown || 0;
          this.volatility = data.volatility || 0;
          this.updateKPICards();
          this.updateCharts();
        })
        .catch(err => console.error('Error loading data:', err));
    },
    
    updatePortfolioMetrics(data) {
      this.portfolioValue = data.portfolio_value || this.portfolioValue;
      this.totalPnL = data.total_pnl || this.totalPnL;
      this.winRate = data.win_rate || this.winRate;
      this.sharpeRatio = data.sharpe_ratio || this.sharpeRatio;
      this.maxDrawdown = data.max_drawdown || this.maxDrawdown;
      this.volatility = data.volatility || this.volatility;
      this.updateKPICards();
      this.lastUpdate = new Date().toLocaleTimeString('es-ES');
    },
    
    updateKPICards() {
      // Portfolio Value
      const portfolioElem = document.getElementById('portfolio-value');
      if (portfolioElem) {
        portfolioElem.textContent = this.formatCurrency(this.portfolioValue);
      }
      
      // P&L
      const pnlElem = document.getElementById('pnl-value');
      if (pnlElem) {
        pnlElem.textContent = this.formatCurrency(this.totalPnL);
      }
      
      // Win Rate
      const wrElem = document.getElementById('winrate-value');
      if (wrElem) {
        wrElem.textContent = this.formatPercent(this.winRate);
      }
      
      // Sharpe
      const sharpeElem = document.getElementById('sharpe-value');
      if (sharpeElem) {
        sharpeElem.textContent = this.sharpeRatio.toFixed(2);
      }
      
      // Max Drawdown
      const ddElem = document.getElementById('drawdown-value');
      if (ddElem) {
        ddElem.textContent = this.formatPercent(Math.abs(this.maxDrawdown));
      }
      
      // Volatility
      const volElem = document.getElementById('volatility-value');
      if (volElem) {
        volElem.textContent = this.formatPercent(this.volatility);
      }
    },
    
    initCharts() {
      // These will be initialized with actual data from backend
      this.initEquityChart();
      this.initReturnsChart();
      this.initDrawdownChart();
      this.initStrategyChart();
    },
    
    initEquityChart() {
      const equityChart = document.getElementById('equity-chart');
      if (!equityChart) return;
      
      const trace = {
        x: [],
        y: [],
        mode: 'lines',
        name: 'Equity',
        line: {
          color: '#00d4ff',
          width: 2
        },
        fill: 'tozeroy',
        fillcolor: 'rgba(0, 212, 255, 0.1)'
      };
      
      const layout = {
        title: '',
        xaxis: {
          color: '#b0b0b0',
          gridcolor: '#2a2f48',
          zeroline: false
        },
        yaxis: {
          color: '#b0b0b0',
          gridcolor: '#2a2f48',
          zeroline: false
        },
        plot_bgcolor: 'rgba(20, 24, 41, 0)',
        paper_bgcolor: 'rgba(20, 24, 41, 0)',
        margin: { l: 60, r: 30, t: 20, b: 40 },
        hovermode: 'x unified'
      };
      
      Plotly.newPlot(equityChart, [trace], layout, { responsive: true });
    },
    
    initReturnsChart() {
      const returnsChart = document.getElementById('returns-chart');
      if (!returnsChart) return;
      
      const trace = {
        x: [],
        y: [],
        type: 'bar',
        marker: {
          color: '#51cf66',
          opacity: 0.8
        }
      };
      
      const layout = {
        title: '',
        xaxis: { color: '#b0b0b0', gridcolor: '#2a2f48' },
        yaxis: { color: '#b0b0b0', gridcolor: '#2a2f48' },
        plot_bgcolor: 'rgba(20, 24, 41, 0)',
        paper_bgcolor: 'rgba(20, 24, 41, 0)',
        margin: { l: 50, r: 20, t: 20, b: 30 }
      };
      
      Plotly.newPlot(returnsChart, [trace], layout, { responsive: true });
    },
    
    initDrawdownChart() {
      const ddChart = document.getElementById('drawdown-chart');
      if (!ddChart) return;
      
      const trace = {
        x: [],
        y: [],
        mode: 'lines',
        name: 'Drawdown',
        line: {
          color: '#ff6b6b',
          width: 2
        },
        fill: 'tozeroy',
        fillcolor: 'rgba(255, 107, 107, 0.1)'
      };
      
      const layout = {
        title: '',
        xaxis: { color: '#b0b0b0', gridcolor: '#2a2f48' },
        yaxis: { color: '#b0b0b0', gridcolor: '#2a2f48' },
        plot_bgcolor: 'rgba(20, 24, 41, 0)',
        paper_bgcolor: 'rgba(20, 24, 41, 0)',
        margin: { l: 50, r: 20, t: 20, b: 30 }
      };
      
      Plotly.newPlot(ddChart, [trace], layout, { responsive: true });
    },
    
    initStrategyChart() {
      const stratChart = document.getElementById('strategies-chart');
      if (!stratChart) return;
      
      const trace = {
        x: [],
        y: [],
        type: 'bar',
        marker: {
          color: '#00d4ff'
        }
      };
      
      const layout = {
        title: '',
        xaxis: { color: '#b0b0b0' },
        yaxis: { color: '#b0b0b0', gridcolor: '#2a2f48' },
        plot_bgcolor: 'rgba(20, 24, 41, 0)',
        paper_bgcolor: 'rgba(20, 24, 41, 0)',
        margin: { l: 60, r: 30, t: 20, b: 80 }
      };
      
      Plotly.newPlot(stratChart, [trace], layout, { responsive: true });
    },
    
    updateCharts() {
      // Update charts with new data from API
      fetch('/api/dashboard/charts')
        .then(res => res.json())
        .then(data => {
          this.updateEquityChart(data.equity);
          this.updateReturnsChart(data.returns);
          this.updateDrawdownChart(data.drawdown);
          this.updateStrategyChart(data.strategies);
        })
        .catch(err => console.error('Error updating charts:', err));
    },
    
    updateEquityChart(data) {
      if (!data) return;
      const equityChart = document.getElementById('equity-chart');
      Plotly.restyle(equityChart, { x: [data.x], y: [data.y] });
    },
    
    updateReturnsChart(data) {
      if (!data) return;
      const returnsChart = document.getElementById('returns-chart');
      Plotly.restyle(returnsChart, { x: [data.x], y: [data.y] });
    },
    
    updateDrawdownChart(data) {
      if (!data) return;
      const ddChart = document.getElementById('drawdown-chart');
      Plotly.restyle(ddChart, { x: [data.x], y: [data.y] });
    },
    
    updateStrategyChart(data) {
      if (!data) return;
      const stratChart = document.getElementById('strategies-chart');
      Plotly.restyle(stratChart, { x: [data.x], y: [data.y] });
    },
    
    addTradeToTable(trade) {
      const tbody = document.getElementById('trades-tbody');
      const noData = tbody.querySelector('.no-data');
      if (noData) noData.remove();
      
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${new Date(trade.timestamp).toLocaleTimeString('es-ES')}</td>
        <td>${trade.strategy}</td>
        <td>${trade.symbol}</td>
        <td>${trade.action === 'BUY' ? '📈' : '📉'} ${trade.action}</td>
        <td>${this.formatCurrency(trade.amount)}</td>
        <td>${this.formatCurrency(trade.price)}</td>
        <td>${this.formatCurrency(trade.pnl)}</td>
        <td>${this.formatPercent(trade.pnl_percent)}</td>
        <td><span class="trade-status ${trade.status}">${trade.status}</span></td>
      `;
      
      tbody.insertBefore(row, tbody.firstChild);
      
      // Keep only last 50 trades
      while (tbody.children.length > 50) {
        tbody.removeChild(tbody.lastChild);
      }
    },
    
    refreshKPIs() {
      this.loadInitialData();
      this.showNotification('KPIs Refreshed', 'Data updated from server');
    },
    
    refreshTrades() {
      fetch('/api/dashboard/trades')
        .then(res => res.json())
        .then(trades => {
          const tbody = document.getElementById('trades-tbody');
          tbody.innerHTML = '';
          trades.forEach(trade => this.addTradeToTable(trade));
        });
    },
    
    changePeriod(event) {
      const period = event.target.value;
      this.updateCharts();
    },
    
    changeMetric(event) {
      const metric = event.target.value;
      this.updateStrategyChart();
    },
    
    startRealtime() {
      if (window.socket) {
        window.socket.emit('enable_realtime');
      }
    },
    
    stopRealtime() {
      if (window.socket) {
        window.socket.emit('disable_realtime');
      }
    },
    
    showNotification(title, message) {
      const alertsContainer = document.getElementById('alerts-container');
      if (!alertsContainer) return;
      
      const alert = document.createElement('div');
      alert.className = 'alert alert-info';
      alert.innerHTML = `
        <div class="alert-content">
          <strong>${title}</strong>
          <p>${message}</p>
        </div>
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
      `;
      
      alertsContainer.appendChild(alert);
      
      setTimeout(() => alert.remove(), 5000);
    },
    
    generateReport() {
      let csv = 'BotV2 Trading Report\n';
      csv += `Generated: ${new Date().toISOString()}\n\n`;
      csv += `Portfolio Value,${this.portfolioValue}\n`;
      csv += `Total P&L,${this.totalPnL}\n`;
      csv += `Win Rate,${this.winRate}%\n`;
      csv += `Sharpe Ratio,${this.sharpeRatio}\n`;
      csv += `Max Drawdown,${this.maxDrawdown}%\n`;
      csv += `Volatility,${this.volatility}%\n`;
      return csv;
    },
    
    formatCurrency(value) {
      return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value || 0);
    },
    
    formatPercent(value) {
      return ((value || 0) * 100).toFixed(2) + '%';
    }
  };
}

// Initialize dashboard on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 BotV2 Professional Dashboard initialized');
  
  // Check for saved theme preference
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    document.body.classList.add('light-theme');
  }
});
