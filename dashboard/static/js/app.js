/**
 * BotV2 Trading Dashboard - Unified JavaScript Application
 * Version: 2.0.0
 * 
 * This file consolidates all JavaScript functionality for the trading dashboard.
 * Modules: Core > API > UI > Charts > WebSocket > Bot Control > Monitoring
 */

'use strict';

/* ==========================================================================
   1. APPLICATION NAMESPACE & CONFIGURATION
   ========================================================================== */

const BotV2 = {
  // Configuration
  config: {
    apiBaseUrl: '/api',
    wsUrl: `ws://${window.location.host}/ws/monitor`,
    refreshInterval: 30000,
    statusInterval: 5000,
    maxLogEntries: 100,
    maxTradesDisplay: 50,
    chartMaxPoints: 100
  },

  // State management
  state: {
    isConnected: false,
    botStatus: 'stopped',
    charts: {},
    ws: null
  },

  // Initialize application
  init() {
    console.log('[BotV2] Initializing application...');
    this.setupCSRFToken();
    this.initModules();
    this.bindGlobalEvents();
    console.log('[BotV2] Application initialized');
  },

  // Setup CSRF token for API requests
  setupCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    if (token) {
      this.config.csrfToken = token.getAttribute('content');
    }
  },

  // Initialize modules based on current page
  initModules() {
    const page = document.body.dataset.page || 'dashboard';
    
    // Common modules
    this.UI.init();
    
    // Page-specific modules
    switch(page) {
      case 'dashboard':
        this.Dashboard.init();
        break;
      case 'control':
        this.Control.init();
        break;
      case 'monitoring':
        this.Monitoring.init();
        break;
    }
  },

  // Global event bindings
  bindGlobalEvents() {
    // Handle visibility change for reconnection
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && this.state.ws && this.state.ws.readyState !== WebSocket.OPEN) {
        this.WebSocket.connect();
      }
    });
  }
};

/* ==========================================================================
   2. API MODULE - Centralized API Communication
   ========================================================================== */

BotV2.API = {
  // Generic fetch wrapper with error handling
  async request(endpoint, options = {}) {
    const url = `${BotV2.config.apiBaseUrl}${endpoint}`;
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...(BotV2.config.csrfToken && { 'X-CSRF-Token': BotV2.config.csrfToken })
      }
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`[API] Request failed: ${endpoint}`, error);
      throw error;
    }
  },

  // GET request
  get(endpoint) {
    return this.request(endpoint);
  },

  // POST request
  post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Specific API methods
  getDashboard() { return this.get('/dashboard'); },
  getBotStatus() { return this.get('/bot/status'); },
  getMetrics() { return this.get('/metrics'); },
  controlBot(action) { return this.post(`/bot/${action}`); },
  closePosition(id) { return this.post(`/positions/${id}/close`); },
  closeAllPositions() { return this.post('/positions/close-all'); },
  cancelAllOrders() { return this.post('/orders/cancel-all'); },
  emergencyStop() { return this.post('/bot/emergency-stop'); },
  saveRiskParams(params) { return this.post('/trading/risk', params); }
};

/* ==========================================================================
   3. UI MODULE - Common UI Components & Utilities
   ========================================================================== */

BotV2.UI = {
  init() {
    this.initTooltips();
    this.initSidebar();
  },

  initTooltips() {
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined') {
      document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
        new bootstrap.Tooltip(el);
      });
    }
  },

  initSidebar() {
    const toggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (toggle && sidebar) {
      toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    }
  },

  // Toast notification system
  notify(message, type = 'info') {
    const icons = { success: 'check', error: 'times', warning: 'exclamation', info: 'info' };
    const alertClass = type === 'error' ? 'danger' : type;
    
    const toast = document.createElement('div');
    toast.className = `alert alert-${alertClass} position-fixed`;
    toast.style.cssText = 'top:20px;right:20px;z-index:9999;min-width:280px;animation:slideIn 0.3s ease';
    toast.innerHTML = `<i class="fas fa-${icons[type]}-circle me-2"></i>${this.escapeHtml(message)}`;
    
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  },

  // Update element text safely
  updateText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  },

  // Format currency
  formatCurrency(value) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value || 0);
  },

  // Format percentage
  formatPercent(value) {
    return `${value >= 0 ? '+' : ''}${(value || 0).toFixed(2)}%`;
  },

  // Escape HTML to prevent XSS
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },

  // Set loading state
  setLoading(container, isLoading) {
    if (isLoading) {
      container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    }
  }
};

/* ==========================================================================
   4. CHARTS MODULE - Chart.js Integration
   ========================================================================== */

BotV2.Charts = {
  // Default chart options for dark theme
  defaultOptions: {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 300 },
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#a0a0a0' } },
      y: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#a0a0a0' } }
    }
  },

  // Create line chart
  createLineChart(canvasId, label, color = '#4e73df') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label,
          data: [],
          borderColor: color,
          backgroundColor: `${color}20`,
          fill: true,
          tension: 0.4,
          pointRadius: 0
        }]
      },
      options: this.defaultOptions
    });
  },

  // Create doughnut chart
  createDoughnutChart(canvasId, labels, data, colors) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{ data, backgroundColor: colors }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#a0a0a0' } }
        }
      }
    });
  },

  // Update chart data
  updateChart(chart, labels, data) {
    if (!chart) return;
    chart.data.labels = labels;
    chart.data.datasets[0].data = data;
    chart.update('none');
  },

  // Add point to streaming chart
  addPoint(chart, label, value, maxPoints = 100) {
    if (!chart) return;
    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(value);
    if (chart.data.labels.length > maxPoints) {
      chart.data.labels.shift();
      chart.data.datasets[0].data.shift();
    }
    chart.update('none');
  }
};

/* ==========================================================================
   5. DASHBOARD MODULE - Main Dashboard Functionality
   ========================================================================== */

BotV2.Dashboard = {
  charts: {},
  refreshTimer: null,

  init() {
    this.initCharts();
    this.loadData();
    this.startAutoRefresh();
    this.bindEvents();
  },

  initCharts() {
    this.charts.performance = BotV2.Charts.createLineChart('performance-chart', 'Portfolio Value');
    this.charts.allocation = BotV2.Charts.createDoughnutChart(
      'allocation-chart',
      ['BTC', 'ETH', 'USDT', 'Other'],
      [40, 30, 20, 10],
      ['#f7931a', '#627eea', '#26a17b', '#4e73df']
    );
  },

  async loadData() {
    try {
      const data = await BotV2.API.getDashboard();
      this.updateStats(data.stats);
      this.updatePerformanceChart(data.performance);
      this.updatePositions(data.positions);
      this.updateTrades(data.trades);
    } catch (error) {
      console.error('[Dashboard] Load failed:', error);
    }
  },

  updateStats(stats) {
    if (!stats) return;
    BotV2.UI.updateText('total-balance', BotV2.UI.formatCurrency(stats.balance));
    BotV2.UI.updateText('balance-change', BotV2.UI.formatPercent(stats.balanceChange));
    BotV2.UI.updateText('daily-pnl', BotV2.UI.formatCurrency(stats.dailyPnl));
    BotV2.UI.updateText('daily-trades', `${stats.dailyTrades || 0} trades`);
    BotV2.UI.updateText('win-rate', `${stats.winRate || 0}%`);
    BotV2.UI.updateText('bot-status', stats.botStatus || 'Offline');
    BotV2.UI.updateText('bot-uptime', stats.uptime || '--');
  },

  updatePerformanceChart(perf) {
    if (perf && this.charts.performance) {
      BotV2.Charts.updateChart(this.charts.performance, perf.labels, perf.values);
    }
  },

  updatePositions(positions) {
    const tbody = document.getElementById('positions-body');
    if (!tbody) return;
    
    if (!positions || !positions.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No open positions</td></tr>';
      return;
    }

    tbody.innerHTML = positions.map(p => `
      <tr>
        <td><strong>${BotV2.UI.escapeHtml(p.symbol)}</strong></td>
        <td class="${p.side === 'long' ? 'text-success' : 'text-danger'}">${p.side.toUpperCase()}</td>
        <td>${p.size}</td>
        <td>${BotV2.UI.formatCurrency(p.entry)}</td>
        <td class="${p.pnl >= 0 ? 'text-success' : 'text-danger'}">${BotV2.UI.formatCurrency(p.pnl)}</td>
        <td><button class="btn btn-sm btn-outline-danger" onclick="BotV2.Dashboard.closePosition('${p.id}')">Close</button></td>
      </tr>
    `).join('');

    BotV2.UI.updateText('position-count', positions.length);
  },

  updateTrades(trades) {
    const tbody = document.getElementById('trades-body');
    if (!tbody) return;
    
    if (!trades || !trades.length) {
      tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No recent trades</td></tr>';
      return;
    }

    tbody.innerHTML = trades.slice(0, 10).map(t => `
      <tr>
        <td>${new Date(t.time).toLocaleTimeString()}</td>
        <td>${BotV2.UI.escapeHtml(t.symbol)}</td>
        <td>${t.type}</td>
        <td class="${t.pnl >= 0 ? 'text-success' : 'text-danger'}">${BotV2.UI.formatCurrency(t.pnl)}</td>
      </tr>
    `).join('');
  },

  async closePosition(id) {
    if (!confirm('Close this position?')) return;
    try {
      await BotV2.API.closePosition(id);
      BotV2.UI.notify('Position closed', 'success');
      this.loadData();
    } catch (error) {
      BotV2.UI.notify('Failed to close position', 'error');
    }
  },

  startAutoRefresh() {
    this.refreshTimer = setInterval(() => this.loadData(), BotV2.config.refreshInterval);
  },

  bindEvents() {
    document.querySelectorAll('[data-period]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('[data-period]').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.loadData();
      });
    });
  }

  // ============================================
  // CONTROL MODULE - Bot control operations
  // ============================================
  Control: {
    // Toggle bot running state
    async toggleBot() {
      const btn = document.getElementById('toggle-bot');
      if (!btn) return;
      
      const isRunning = btn.classList.contains('btn-danger');
      const action = isRunning ? 'stop' : 'start';
      
      try {
        BotV2.UI.setLoading(btn, true);
        const response = await BotV2.API.request(`/api/bot/${action}`, 'POST');
        
        if (response.status === 'success') {
          this.updateBotStatus(!isRunning);
          BotV2.UI.notify(`Bot ${action}ed successfully`, 'success');
        }
      } catch (error) {
        BotV2.UI.notify(`Failed to ${action} bot`, 'error');
      } finally {
        BotV2.UI.setLoading(btn, false);
      }
    },

    // Update bot status display
    updateBotStatus(isRunning) {
      const btn = document.getElementById('toggle-bot');
      const statusBadge = document.getElementById('bot-status');
      
      if (btn) {
        btn.innerHTML = isRunning ? 
          '<i class="fas fa-stop me-2"></i>Stop Bot' : 
          '<i class="fas fa-play me-2"></i>Start Bot';
        btn.classList.toggle('btn-danger', isRunning);
        btn.classList.toggle('btn-success', !isRunning);
      }
      
      if (statusBadge) {
        statusBadge.textContent = isRunning ? 'Running' : 'Stopped';
        statusBadge.classList.toggle('bg-success', isRunning);
        statusBadge.classList.toggle('bg-secondary', !isRunning);
      }
    },

    // Update trading parameters
    async updateSettings(formData) {
      try {
        const response = await BotV2.API.request('/api/settings', 'POST', formData);
        if (response.status === 'success') {
          BotV2.UI.notify('Settings updated successfully', 'success');
          return true;
        }
      } catch (error) {
        BotV2.UI.notify('Failed to update settings', 'error');
      }
      return false;
    },

    // Emergency stop
    async emergencyStop() {
      if (!confirm('Are you sure you want to emergency stop and close all positions?')) return;
      
      try {
        await BotV2.API.request('/api/bot/emergency-stop', 'POST');
        this.updateBotStatus(false);
        BotV2.UI.notify('Emergency stop executed', 'warning');
        BotV2.Dashboard.loadData();
      } catch (error) {
        BotV2.UI.notify('Emergency stop failed', 'error');
      }
    },

    // Bind control events
    bindEvents() {
      // Toggle bot button
      document.getElementById('toggle-bot')?.addEventListener('click', () => this.toggleBot());
      
      // Emergency stop button
      document.getElementById('emergency-stop')?.addEventListener('click', () => this.emergencyStop());
      
      // Settings form
      document.getElementById('settings-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = Object.fromEntries(new FormData(e.target));
        await this.updateSettings(formData);
      });
    }
  },

  // ============================================
  // MONITORING MODULE - System monitoring
  // ============================================
  Monitoring: {
    charts: {},
    
    // Initialize monitoring charts
    init() {
      this.initPnLChart();
      this.initEquityChart();
      this.loadData();
      this.startAutoRefresh();
      this.bindEvents();
    },

    // Initialize P&L chart
    initPnLChart() {
      const ctx = document.getElementById('pnl-chart');
      if (!ctx) return;
      
      this.charts.pnl = BotV2.Charts.createLine(ctx, {
        label: 'Daily P&L',
        borderColor: BotV2.config.chartColors.primary,
        fill: true,
        backgroundColor: BotV2.config.chartColors.primary + '20'
      });
    },

    // Initialize equity chart
    initEquityChart() {
      const ctx = document.getElementById('equity-chart');
      if (!ctx) return;
      
      this.charts.equity = BotV2.Charts.createLine(ctx, {
        label: 'Equity',
        borderColor: BotV2.config.chartColors.success,
        fill: true,
        backgroundColor: BotV2.config.chartColors.success + '20'
      });
    },

    // Load monitoring data
    async loadData() {
      try {
        const [performance, metrics] = await Promise.all([
          BotV2.API.get('/api/performance'),
          BotV2.API.get('/api/metrics')
        ]);
        
        this.updateCharts(performance);
        this.updateMetrics(metrics);
      } catch (error) {
        console.error('Failed to load monitoring data:', error);
      }
    },

    // Update charts with new data
    updateCharts(data) {
      if (data.pnl && this.charts.pnl) {
        BotV2.Charts.updateChart(
          this.charts.pnl,
          data.pnl.labels,
          data.pnl.values
        );
      }
      
      if (data.equity && this.charts.equity) {
        BotV2.Charts.updateChart(
          this.charts.equity,
          data.equity.labels,
          data.equity.values
        );
      }
    },

    // Update system metrics display
    updateMetrics(metrics) {
      if (!metrics) return;
      
      BotV2.UI.updateText('cpu-usage', `${metrics.cpu || 0}%`);
      BotV2.UI.updateText('memory-usage', `${metrics.memory || 0}%`);
      BotV2.UI.updateText('api-latency', `${metrics.latency || 0}ms`);
      BotV2.UI.updateText('uptime', metrics.uptime || '0h');
    },

    // Auto refresh
    startAutoRefresh() {
      this.refreshTimer = setInterval(() => this.loadData(), BotV2.config.refreshInterval);
    },

    // Bind events
    bindEvents() {
      // Refresh button
      document.getElementById('refresh-monitoring')?.addEventListener('click', () => {
        this.loadData();
        BotV2.UI.notify('Monitoring data refreshed', 'info');
      });
    }
  },

  // ============================================
  // WEBSOCKET MODULE - Real-time updates
  // ============================================
  WebSocket: {
    socket: null,
    reconnectAttempts: 0,
    maxReconnectAttempts: 5,
    
    // Initialize WebSocket connection
    init() {
      this.connect();
    },

    // Connect to WebSocket server
    connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws`;
      
      try {
        this.socket = new window.WebSocket(wsUrl);
        this.bindSocketEvents();
      } catch (error) {
        console.error('WebSocket connection failed:', error);
        this.scheduleReconnect();
      }
    },

    // Bind WebSocket events
    bindSocketEvents() {
      if (!this.socket) return;
      
      this.socket.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        BotV2.UI.updateText('connection-status', 'Connected');
      };
      
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
      
      this.socket.onclose = () => {
        console.log('WebSocket disconnected');
        BotV2.UI.updateText('connection-status', 'Disconnected');
        this.scheduleReconnect();
      };
      
      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    },

    // Handle incoming messages
    handleMessage(data) {
      switch (data.type) {
        case 'price_update':
          this.handlePriceUpdate(data.payload);
          break;
        case 'trade_executed':
          this.handleTradeExecuted(data.payload);
          break;
        case 'position_update':
          this.handlePositionUpdate(data.payload);
          break;
        case 'alert':
          BotV2.UI.notify(data.payload.message, data.payload.level);
          break;
        default:
          console.log('Unknown message type:', data.type);
      }
    },

    // Handle price updates
    handlePriceUpdate(payload) {
      BotV2.UI.updateText('current-price', BotV2.UI.formatCurrency(payload.price));
      
      if (BotV2.Dashboard.charts.price) {
        BotV2.Charts.addPoint(
          BotV2.Dashboard.charts.price,
          payload.time,
          payload.price
        );
      }
    },

    // Handle trade executed
    handleTradeExecuted(payload) {
      BotV2.UI.notify(`Trade executed: ${payload.symbol} ${payload.side}`, 'success');
      BotV2.Dashboard.loadData();
    },

    // Handle position update
    handlePositionUpdate(payload) {
      BotV2.UI.updateText('total-pnl', BotV2.UI.formatCurrency(payload.totalPnl));
      BotV2.UI.updateText('open-positions', payload.count);
    },

    // Schedule reconnection
    scheduleReconnect() {
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
        BotV2.UI.notify('Connection lost. Please refresh the page.', 'error');
        return;
      }
      
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      
      setTimeout(() => this.connect(), delay);
    },

    // Send message through WebSocket
    send(type, payload) {
      if (this.socket?.readyState === window.WebSocket.OPEN) {
        this.socket.send(JSON.stringify({ type, payload }));
      }
    },

    // Disconnect WebSocket
    disconnect() {
      if (this.socket) {
        this.socket.close();
        this.socket = null;
      }
    }
  },

  // ============================================
  // INITIALIZATION - Application bootstrap
  // ============================================
  
  // Initialize application based on current page
  init() {
    console.log('BotV2 Dashboard initializing...');
    
    // Detect current page and initialize appropriate modules
    const path = window.location.pathname;
    
    // Always initialize UI utilities
    this.UI.init?.();
    
    // Initialize page-specific modules
    if (path.includes('/dashboard') || path === '/') {
      this.Dashboard.init();
      this.WebSocket.init();
    } else if (path.includes('/control')) {
      this.Control.bindEvents();
      this.WebSocket.init();
    } else if (path.includes('/monitoring')) {
      this.Monitoring.init();
      this.WebSocket.init();
    }
    
    // Global event listeners
    this.bindGlobalEvents();
    
    console.log('BotV2 Dashboard initialized successfully');
  },

  // Bind global event listeners
  bindGlobalEvents() {
    // Dark mode toggle
    document.getElementById('dark-mode-toggle')?.addEventListener('click', () => {
      document.body.classList.toggle('dark-mode');
      localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
    });
    
    // Restore dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
      document.body.classList.add('dark-mode');
    }
    
    // Handle page visibility changes (pause updates when tab is hidden)
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        console.log('Page hidden, pausing updates');
      } else {
        console.log('Page visible, resuming updates');
        // Refresh data when page becomes visible
        this.Dashboard.loadData?.();
      }
    });
    
    // Handle window unload
    window.addEventListener('beforeunload', () => {
      this.WebSocket.disconnect();
    });
  }
};

// ============================================
// AUTO-INITIALIZATION ON DOM READY
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  BotV2.init();
});

// Export for module systems (if needed)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = BotV2;
}
};
