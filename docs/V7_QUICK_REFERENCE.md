# 🚀 BotV2 Dashboard v7.1 & v7.2 - Quick Reference Guide

## 📌 Overview

**Date**: 24 Enero 2026  
**Version**: 7.2.0  
**Status**: ✅ Production Ready

This guide provides a quick reference for developers working with Chart Mastery v7.1 and Advanced Features v7.2.

---

## 📈 Chart Mastery v7.1 - Quick API

### Available Charts

| Chart | Method | Use Case |
|-------|--------|----------|
| Win/Loss Distribution | `createWinLossDistribution()` | Visualize profit/loss patterns |
| Correlation Matrix | `createCorrelationMatrix()` | Asset correlation analysis |
| Risk-Return Scatter | `createRiskReturnScatter()` | Strategy comparison |
| Trade Duration Box Plot | `createTradeDurationBoxPlot()` | Duration analysis |
| Real vs Expected | `createComparisonOverlay()` | Performance vs forecast |
| Drawdown with Events | `createDrawdownChart()` | Equity + annotations |
| Multi-Timeframe | `createMultiTimeframeComparison()` | Period comparison |

### Basic Usage

```javascript
// 1. Win/Loss Distribution
const trades = [
  { profit: 150, ... },
  { profit: -75, ... },
  { profit: 200, ... }
];
ChartMastery.createWinLossDistribution('chart-id', trades);

// 2. Correlation Matrix
const assets = ['AAPL', 'MSFT', 'GOOGL'];
const returns = [
  [0.02, 0.01, -0.01, 0.03],  // AAPL returns
  [0.01, 0.02, 0.00, 0.02],   // MSFT returns
  [-0.01, 0.01, 0.02, 0.01]   // GOOGL returns
];
ChartMastery.createCorrelationMatrix('chart-id', assets, returns);

// 3. Risk-Return Scatter
const strategies = [
  { name: 'Strategy A', volatility: 15, return: 25, sharpe: 1.5 },
  { name: 'Strategy B', volatility: 20, return: 30, sharpe: 1.3 },
  { name: 'Strategy C', volatility: 10, return: 18, sharpe: 1.7 }
];
ChartMastery.createRiskReturnScatter('chart-id', strategies);

// 4. Trade Duration Box Plot
const tradesByStrategy = {
  'Momentum': [{ duration: 24 }, { duration: 48 }, ...],
  'Mean Reversion': [{ duration: 12 }, { duration: 18 }, ...],
  'Trend Following': [{ duration: 72 }, { duration: 96 }, ...]
};
ChartMastery.createTradeDurationBoxPlot('chart-id', tradesByStrategy);

// 5. Real vs Expected Comparison
const dates = ['2026-01-01', '2026-01-02', '2026-01-03'];
const realData = [100, 105, 103];
const expectedData = [100, 103, 106];
ChartMastery.createComparisonOverlay('chart-id', dates, realData, expectedData, 'Return');

// 6. Drawdown with Annotations
const events = [
  { date: '2026-01-15', value: 10500, label: 'Strategy Change' },
  { date: '2026-01-20', value: 11200, label: 'Max Equity' }
];
ChartMastery.createDrawdownChart('chart-id', dates, equity, drawdowns, events);

// 7. Multi-Timeframe Comparison
const timeframes = [
  { name: '1 Day', dates: [...], returns: [...] },
  { name: '1 Week', dates: [...], returns: [...] },
  { name: '1 Month', dates: [...], returns: [...] }
];
ChartMastery.createMultiTimeframeComparison('chart-id', timeframes);
```

### Chart Utilities

```javascript
// Add annotation to existing chart
ChartMastery.addAnnotation('chart-id', {
  x: '2026-01-24',
  y: 10500,
  text: 'Important Event',
  showarrow: true,
  arrowcolor: '#f85149'
});

// Clear all annotations
ChartMastery.clearAnnotations('chart-id');

// Export chart
ChartMastery.exportChart('chart-id', 'my-chart', 'png');

// Destroy chart
ChartMastery.destroyChart('chart-id');

// Destroy all charts
ChartMastery.destroyAll();
```

---

## 🌟 Advanced Features v7.2 - Quick API

### 1. Command Palette

```javascript
// Open palette
CommandPalette.open();  // or press Ctrl+K

// Close palette
CommandPalette.close(); // or press Esc

// Register custom command
CommandPalette.register({
  id: 'export-data',
  label: 'Export All Data',
  category: 'data',
  keywords: ['export', 'download', 'csv'],
  shortcut: 'Ctrl+E',
  action: () => {
    // Your export logic
    console.log('Exporting data...');
  }
});

// Execute command programmatically
CommandPalette.execute('export-data');

// Get all commands
const commands = CommandPalette.getAllCommands();
```

**Default Commands:**
- Navigation: `Go to Dashboard`, `Go to Portfolio`, etc.
- Charts: `Refresh All Charts`, `Export Chart`, `Toggle Fullscreen`
- Data: `Apply Filters`, `Clear Filters`, `Export CSV`
- Settings: `Change Theme`, `Toggle Dark Mode`, `Customize Layout`
- Actions: `Start Bot`, `Stop Bot`, `Execute Trade`

**Keyboard Shortcuts:**
- `Ctrl+K` / `Cmd+K`: Open palette
- `Esc`: Close
- `↑↓`: Navigate
- `Enter`: Execute
- `Ctrl+1-9`: Quick actions

### 2. Insights Panel

```javascript
// Toggle panel
InsightsPanel.toggle();  // or press Ctrl+/

// Open panel
InsightsPanel.open();

// Close panel
InsightsPanel.close();

// Refresh insights
InsightsPanel.refresh();

// Add custom insight
InsightsPanel.addInsight({
  category: 'performance',  // performance, risk, opportunity
  severity: 'info',         // info, warning, critical
  title: 'Custom Insight',
  description: 'Your portfolio is performing well',
  action: 'Consider increasing allocation',
  timestamp: new Date().toISOString()
});

// Get all insights
const insights = InsightsPanel.getInsights();

// Clear insights
InsightsPanel.clearInsights();
```

**Insight Categories:**
- `performance`: Trading performance insights
- `risk`: Risk management alerts
- `opportunity`: Trading opportunities

**Severity Levels:**
- `info`: ℹ️ Informational (green)
- `warning`: ⚠️ Warning (yellow)
- `critical`: 🚨 Critical (red)

### 3. Anomaly Detection

```javascript
// Detect anomalies in data
const result = AnomalyDetector.detectAnomalies(data, {
  sensitivity: 'medium',  // low, medium, high
  types: ['volume', 'price', 'correlation'],
  threshold: 2.0  // Standard deviations
});

// Result structure:
// {
//   anomalies: [
//     { type: 'volume', timestamp: '...', value: 1500, expected: 1000, zscore: 3.2 },
//     { type: 'price', timestamp: '...', value: 150, expected: 145, zscore: 2.5 }
//   ],
//   score: 85,  // Anomaly score (0-100)
//   alerts: ['High volume detected', 'Price spike detected']
// }

// Check if anomaly exists
const hasAnomalies = AnomalyDetector.hasAnomalies(data);

// Get anomaly config
const config = AnomalyDetector.getConfig();

// Update config
AnomalyDetector.updateConfig({
  sensitivity: 'high',
  threshold: 1.5
});
```

### 4. Layout Manager

```javascript
// Available layouts
const layouts = [
  'default',      // Standard 2-column grid
  'focus',        // Single large chart
  'comparison',   // Side-by-side 2-chart
  'grid',         // 2x2 or 3x3 grid
  'professional'  // Bloomberg-style
];

// Set layout
LayoutManager.setLayout('focus');

// Save current layout
LayoutManager.saveLayout('my-custom-layout');

// Load saved layout
LayoutManager.loadLayout('my-custom-layout');

// Get current layout
const currentLayout = LayoutManager.getCurrentLayout();

// Get all saved layouts
const savedLayouts = LayoutManager.getSavedLayouts();

// Delete layout
LayoutManager.deleteLayout('my-custom-layout');

// Reset to default
LayoutManager.resetLayout();

// Custom layout configuration
LayoutManager.createCustomLayout({
  name: 'my-layout',
  grid: {
    columns: 3,
    rows: 2,
    gap: 16
  },
  charts: [
    { id: 'equity', position: { col: 1, row: 1, colspan: 2, rowspan: 1 } },
    { id: 'portfolio', position: { col: 3, row: 1, colspan: 1, rowspan: 2 } },
    { id: 'trades', position: { col: 1, row: 2, colspan: 2, rowspan: 1 } }
  ]
});
```

**Layout Shortcuts:**
- `Ctrl+1`: Default layout
- `Ctrl+2`: Focus layout
- `Ctrl+3`: Comparison layout
- `Ctrl+4`: Grid layout
- `Ctrl+5`: Professional layout

### 5. Snapshot Manager

```javascript
// Create snapshot
const snapshot = await SnapshotManager.create({
  type: 'static',           // static or live
  sections: ['dashboard', 'portfolio'],
  includeCharts: true,
  includeData: false,
  password: 'optional-password',  // Optional
  expiresIn: 2592000000   // 30 days in ms
});

// Returns:
// {
//   id: 'abc123',
//   url: 'https://botv2.trading/snapshot/abc123',
//   qr: 'data:image/png;base64,...',  // QR code
//   expiresAt: '2026-02-23T10:00:00Z'
// }

// Share snapshot
SnapshotManager.share(snapshot.id, 'email', {
  to: 'user@example.com',
  subject: 'Trading Dashboard Snapshot',
  message: 'Check out my trading performance'
});

// Share via other methods
SnapshotManager.share(snapshot.id, 'slack');    // Slack
SnapshotManager.share(snapshot.id, 'teams');    // Microsoft Teams
SnapshotManager.share(snapshot.id, 'twitter');  // Twitter

// Get snapshot details
const details = await SnapshotManager.get(snapshot.id);

// List all snapshots
const snapshots = await SnapshotManager.list();

// Delete snapshot
await SnapshotManager.delete(snapshot.id);

// Generate PDF
const pdf = await SnapshotManager.toPDF(snapshot.id);

// Copy link to clipboard
SnapshotManager.copyLink(snapshot.id);
```

---

## 🎨 Theming

All v7.1 and v7.2 features automatically adapt to the active theme:

```javascript
// Themes: 'dark', 'light', 'bloomberg'

// Change theme programmatically
setTheme('dark');

// Get current theme
const theme = document.documentElement.getAttribute('data-theme');

// Listen for theme changes
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.attributeName === 'data-theme') {
      const newTheme = document.documentElement.getAttribute('data-theme');
      console.log('Theme changed to:', newTheme);
      // Your logic here
    }
  });
});

observer.observe(document.documentElement, {
  attributes: true,
  attributeFilter: ['data-theme']
});
```

---

## 🛡️ Error Handling

```javascript
// All async operations should be wrapped in try-catch

try {
  const snapshot = await SnapshotManager.create({ ... });
  console.log('Snapshot created:', snapshot.url);
} catch (error) {
  console.error('Failed to create snapshot:', error);
  // Show user-friendly error
  showNotification('Failed to create snapshot', 'error');
}

try {
  ChartMastery.createWinLossDistribution('chart-id', trades);
} catch (error) {
  console.error('Failed to create chart:', error);
  showEmptyState('chart-id', {
    icon: '⚠️',
    title: 'Chart Error',
    description: 'Unable to create chart. Please try again.'
  });
}
```

---

## 📦 Integration Example

Complete example integrating all v7.1 and v7.2 features:

```javascript
// Initialize dashboard section with v7 features
function renderAdvancedDashboard(data) {
  const container = document.getElementById('main-container');
  
  // Create HTML structure
  container.innerHTML = `
    <!-- Date Range & Filters -->
    ${createDateRangeSelector('dashboard')}
    ${createFilterPanel(filterOptions)}
    
    <!-- KPIs -->
    <div class="kpi-grid fade-in">
      ${createKPICards(data.kpis)}
    </div>
    
    <!-- Charts Grid -->
    <div class="charts-grid slide-up">
      <!-- Win/Loss Distribution -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">Win/Loss Distribution</div>
          ${createChartControls('winloss-chart')}
        </div>
        <div id="winloss-chart" class="chart-container"></div>
      </div>
      
      <!-- Correlation Matrix -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">Asset Correlation</div>
          ${createChartControls('correlation-chart')}
        </div>
        <div id="correlation-chart" class="chart-container"></div>
      </div>
      
      <!-- Risk-Return Scatter -->
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">Risk-Return Analysis</div>
          ${createChartControls('riskreturn-chart')}
        </div>
        <div id="riskreturn-chart" class="chart-container"></div>
      </div>
    </div>
  `;
  
  // Render charts after DOM is ready
  setTimeout(() => {
    // Chart Mastery v7.1 charts
    ChartMastery.createWinLossDistribution('winloss-chart', data.trades);
    ChartMastery.createCorrelationMatrix('correlation-chart', data.assets, data.returns);
    ChartMastery.createRiskReturnScatter('riskreturn-chart', data.strategies);
    
    // Refresh insights (v7.2)
    if (typeof InsightsPanel !== 'undefined') {
      InsightsPanel.refresh();
    }
    
    // Check for anomalies (v7.2)
    const anomalies = AnomalyDetector.detectAnomalies(data.trades);
    if (anomalies.anomalies.length > 0) {
      showNotification(`${anomalies.anomalies.length} anomalies detected`, 'warning');
    }
  }, 100);
}

// Register custom commands
if (typeof CommandPalette !== 'undefined') {
  CommandPalette.register({
    id: 'create-snapshot',
    label: 'Create Dashboard Snapshot',
    category: 'actions',
    keywords: ['snapshot', 'share', 'export'],
    action: async () => {
      try {
        const snapshot = await SnapshotManager.create({
          type: 'static',
          sections: ['dashboard']
        });
        SnapshotManager.copyLink(snapshot.id);
        showNotification('Snapshot created and link copied!', 'success');
      } catch (error) {
        showNotification('Failed to create snapshot', 'error');
      }
    }
  });
}
```

---

## 📊 Performance Tips

1. **Lazy Load Charts**: Only render visible charts
2. **Debounce Filters**: Wait 300ms before applying filters
3. **Cache Data**: Cache API responses for 60 seconds
4. **Cleanup**: Always destroy charts when switching sections
5. **Batch Updates**: Group multiple chart updates together

```javascript
// Good: Lazy loading
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      renderChart(entry.target.id);
      observer.unobserve(entry.target);
    }
  });
});

// Good: Debouncing
const debouncedFilter = debounce((value) => {
  applyFilter(value);
}, 300);

// Good: Cleanup
function cleanupCharts() {
  Object.keys(chartInstances).forEach(chartId => {
    ChartMastery.destroyChart(chartId);
  });
  chartInstances = {};
}
```

---

## 🔧 Debugging

```javascript
// Enable debug mode
window.DEBUG_MODE = true;

// Check feature availability
console.log('ChartMastery loaded:', typeof ChartMastery !== 'undefined');
console.log('CommandPalette loaded:', typeof CommandPalette !== 'undefined');
console.log('InsightsPanel loaded:', typeof InsightsPanel !== 'undefined');

// Get chart instance
const chartDiv = document.getElementById('my-chart');
if (chartDiv && chartDiv.data) {
  console.log('Chart data:', chartDiv.data);
  console.log('Chart layout:', chartDiv.layout);
}

// Monitor performance
performance.mark('chart-start');
ChartMastery.createWinLossDistribution('chart-id', trades);
performance.mark('chart-end');
performance.measure('chart-render', 'chart-start', 'chart-end');
const measure = performance.getEntriesByName('chart-render')[0];
console.log('Chart render time:', measure.duration, 'ms');
```

---

## 📚 Resources

- **Full Documentation**: `docs/V7_IMPLEMENTATION_COMPLETE.md`
- **API Reference**: `docs/API.md`
- **Testing Guide**: `docs/TESTING_GUIDE.md`
- **Changelog**: `CHANGELOG.md`
- **Issues**: [GitHub Issues](https://github.com/juankaspain/BotV2/issues)

---

## ❓ FAQ

**Q: How do I enable/disable features?**  
A: Configure in `settings.yaml` or environment variables.

**Q: Can I customize chart colors?**  
A: Yes, modify theme colors in CSS variables or create custom themes.

**Q: How do I add custom commands?**  
A: Use `CommandPalette.register()` method.

**Q: Are snapshots persistent?**  
A: Yes, for 30 days by default (configurable).

**Q: Can I use v7 features with v6 dashboard?**  
A: No, v7 features require v7.2 dashboard template.

---

**Last Updated**: 24 Enero 2026  
**Version**: 7.2.0  
**Author**: Juan Carlos Garcia
