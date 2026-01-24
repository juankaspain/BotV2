// ==================== BotV2 Advanced Features v7.2 ====================
// Automated Insights | Anomaly Detection | Command Palette | Layout Switcher
// Author: Juan Carlos Garcia
// Date: 24 Enero 2026

console.log('🚀 Advanced Features v7.2 initializing...');

// ==================== ADVANCED FEATURES LIBRARY ====================
const AdvancedFeatures = {
    
    // ==================== 1. AUTOMATED INSIGHTS PANEL ====================
    InsightsPanel: {
        container: null,
        insights: [],
        
        init: function(containerId) {
            this.container = document.getElementById(containerId);
            if (!this.container) {
                console.warn(`Insights container ${containerId} not found`);
                return;
            }
            
            this.render();
        },
        
        addInsight: function(insight) {
            const {
                type,        // 'success', 'warning', 'danger', 'info'
                title,
                message,
                metric = null,
                action = null,
                icon = '🧠',
                priority = 'medium'  // 'high', 'medium', 'low'
            } = insight;
            
            const timestamp = Date.now();
            
            this.insights.unshift({
                id: `insight-${timestamp}`,
                type,
                title,
                message,
                metric,
                action,
                icon,
                priority,
                timestamp,
                dismissed: false
            });
            
            // Keep only last 10 insights
            if (this.insights.length > 10) {
                this.insights = this.insights.slice(0, 10);
            }
            
            this.render();
        },
        
        analyzeData: function(data) {
            const insights = [];
            
            // 1. Momentum Analysis
            if (data.dailyReturn > 5) {
                insights.push({
                    type: 'success',
                    title: 'Strong Momentum Detected',
                    message: `Portfolio up ${data.dailyReturn.toFixed(2)}% in last 24h. Consider taking profits.`,
                    metric: `+${data.dailyReturn.toFixed(2)}%`,
                    action: { label: 'View Performance', url: '#performance' },
                    icon: '📈',
                    priority: 'high'
                });
            } else if (data.dailyReturn < -5) {
                insights.push({
                    type: 'danger',
                    title: 'Significant Drawdown Alert',
                    message: `Portfolio down ${Math.abs(data.dailyReturn).toFixed(2)}% today. Review risk exposure.`,
                    metric: `${data.dailyReturn.toFixed(2)}%`,
                    action: { label: 'View Risk Analysis', url: '#risk' },
                    icon: '⚠️',
                    priority: 'high'
                });
            }
            
            // 2. Drawdown Analysis
            if (data.currentDrawdown && Math.abs(data.currentDrawdown) > 10) {
                insights.push({
                    type: 'warning',
                    title: 'Maximum Drawdown Threshold',
                    message: `Current drawdown at ${Math.abs(data.currentDrawdown).toFixed(1)}%. Approaching risk limit.`,
                    metric: `${data.currentDrawdown.toFixed(1)}%`,
                    action: { label: 'Adjust Position Size', url: '#control' },
                    icon: '🚨',
                    priority: 'high'
                });
            }
            
            // 3. Win Rate Analysis
            if (data.winRate && data.winRate > 70) {
                insights.push({
                    type: 'success',
                    title: 'Exceptional Win Rate',
                    message: `Current strategy achieving ${data.winRate.toFixed(1)}% win rate. Performance above target.`,
                    metric: `${data.winRate.toFixed(1)}%`,
                    action: { label: 'View Trades', url: '#trades' },
                    icon: '🎯',
                    priority: 'medium'
                });
            } else if (data.winRate && data.winRate < 40) {
                insights.push({
                    type: 'warning',
                    title: 'Low Win Rate Detected',
                    message: `Win rate at ${data.winRate.toFixed(1)}%. Strategy may need adjustment.`,
                    metric: `${data.winRate.toFixed(1)}%`,
                    action: { label: 'Review Strategy', url: '#strategies' },
                    icon: '🔴',
                    priority: 'medium'
                });
            }
            
            // 4. Unused Capital
            if (data.availableCapital && data.availableCapital > data.totalCapital * 0.3) {
                const unused = (data.availableCapital / data.totalCapital * 100).toFixed(1);
                insights.push({
                    type: 'info',
                    title: 'Unused Capital Opportunity',
                    message: `${unused}% of capital is idle. Consider deploying for diversification.`,
                    metric: `€${data.availableCapital.toLocaleString()}`,
                    action: { label: 'View Markets', url: '#markets' },
                    icon: '💰',
                    priority: 'low'
                });
            }
            
            // 5. Sharpe Ratio Analysis
            if (data.sharpeRatio && data.sharpeRatio > 2) {
                insights.push({
                    type: 'success',
                    title: 'Excellent Risk-Adjusted Returns',
                    message: `Sharpe Ratio of ${data.sharpeRatio.toFixed(2)} indicates superior performance.`,
                    metric: data.sharpeRatio.toFixed(2),
                    action: { label: 'View Analytics', url: '#performance' },
                    icon: '⭐',
                    priority: 'medium'
                });
            }
            
            // Add all generated insights
            insights.forEach(insight => this.addInsight(insight));
        },
        
        render: function() {
            if (!this.container) return;
            
            const activeInsights = this.insights.filter(i => !i.dismissed);
            
            if (activeInsights.length === 0) {
                this.container.innerHTML = `
                    <div class="insights-empty">
                        <div class="insights-empty-icon">📊</div>
                        <div class="insights-empty-title">No insights available</div>
                        <div class="insights-empty-description">Insights will appear here as we analyze your trading data</div>
                    </div>
                `;
                return;
            }
            
            const html = `
                <div class="insights-header">
                    <h3 class="insights-title">
                        <span class="insights-icon">🧠</span>
                        Smart Insights
                        <span class="insights-count">${activeInsights.length}</span>
                    </h3>
                </div>
                <div class="insights-list">
                    ${activeInsights.map(insight => this.renderInsight(insight)).join('')}
                </div>
            `;
            
            this.container.innerHTML = html;
            
            // Attach event listeners
            this.attachEventListeners();
        },
        
        renderInsight: function(insight) {
            const typeColors = {
                success: 'var(--accent-success)',
                warning: 'var(--accent-warning)',
                danger: 'var(--accent-danger)',
                info: 'var(--accent-primary)'
            };
            
            const priorityClass = `insight-priority-${insight.priority}`;
            
            return `
                <div class="insight-card ${priorityClass}" data-insight-id="${insight.id}" data-type="${insight.type}">
                    <div class="insight-icon" style="color: ${typeColors[insight.type]}">
                        ${insight.icon}
                    </div>
                    <div class="insight-content">
                        <div class="insight-header-row">
                            <h4 class="insight-title">${insight.title}</h4>
                            ${insight.metric ? `<span class="insight-metric" style="color: ${typeColors[insight.type]}">${insight.metric}</span>` : ''}
                        </div>
                        <p class="insight-message">${insight.message}</p>
                        <div class="insight-footer">
                            ${insight.action ? `
                                <a href="${insight.action.url}" class="insight-action">
                                    ${insight.action.label} →
                                </a>
                            ` : ''}
                            <button class="insight-dismiss" data-insight-id="${insight.id}" title="Dismiss">
                                ✕
                            </button>
                        </div>
                    </div>
                </div>
            `;
        },
        
        attachEventListeners: function() {
            document.querySelectorAll('.insight-dismiss').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const insightId = e.target.dataset.insightId;
                    this.dismissInsight(insightId);
                });
            });
        },
        
        dismissInsight: function(insightId) {
            const insight = this.insights.find(i => i.id === insightId);
            if (insight) {
                insight.dismissed = true;
                this.render();
            }
        }
    },
    
    // ==================== 2. ANOMALY DETECTION ====================
    AnomalyDetector: {
        thresholds: {
            volumeSpike: 3,        // 3x average
            priceJump: 5,          // 5% in 1 minute
            drawdownRapid: 3,      // 3% in 5 minutes
            correlationBreak: 0.5  // Correlation change > 0.5
        },
        
        detectAnomalies: function(data) {
            const anomalies = [];
            
            // 1. Volume Spike Detection
            if (data.currentVolume > data.avgVolume * this.thresholds.volumeSpike) {
                anomalies.push({
                    type: 'volume_spike',
                    severity: 'warning',
                    message: `Unusual volume spike detected: ${(data.currentVolume / data.avgVolume).toFixed(1)}x average`,
                    value: data.currentVolume,
                    timestamp: Date.now()
                });
            }
            
            // 2. Rapid Price Movement
            if (Math.abs(data.priceChange1m) > this.thresholds.priceJump) {
                anomalies.push({
                    type: 'price_jump',
                    severity: 'danger',
                    message: `Rapid price movement: ${data.priceChange1m.toFixed(2)}% in 1 minute`,
                    value: data.priceChange1m,
                    timestamp: Date.now()
                });
            }
            
            // 3. Rapid Drawdown
            if (data.drawdown5m && Math.abs(data.drawdown5m) > this.thresholds.drawdownRapid) {
                anomalies.push({
                    type: 'rapid_drawdown',
                    severity: 'danger',
                    message: `Rapid drawdown: ${Math.abs(data.drawdown5m).toFixed(2)}% in 5 minutes`,
                    value: data.drawdown5m,
                    timestamp: Date.now()
                });
            }
            
            // 4. Correlation Breakdown
            if (data.correlationChange && Math.abs(data.correlationChange) > this.thresholds.correlationBreak) {
                anomalies.push({
                    type: 'correlation_break',
                    severity: 'warning',
                    message: `Asset correlation breakdown detected: ${(data.correlationChange * 100).toFixed(0)}% change`,
                    value: data.correlationChange,
                    timestamp: Date.now()
                });
            }
            
            return anomalies;
        },
        
        alertAnomaly: function(anomaly) {
            // Add to insights panel
            AdvancedFeatures.InsightsPanel.addInsight({
                type: anomaly.severity === 'danger' ? 'danger' : 'warning',
                title: 'Anomaly Detected',
                message: anomaly.message,
                metric: anomaly.value.toFixed(2),
                action: { label: 'Investigate', url: '#monitoring' },
                icon: '⚡',
                priority: 'high'
            });
            
            // Play alert sound (optional)
            if (anomaly.severity === 'danger') {
                this.playAlertSound();
            }
        },
        
        playAlertSound: function() {
            // Optional: Play browser notification sound
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('BotV2 Alert', {
                    body: 'Anomaly detected in your trading activity',
                    icon: '/static/icon.png',
                    badge: '/static/badge.png'
                });
            }
        }
    },
    
    // ==================== 3. COMMAND PALETTE (Ctrl+K) ====================
    CommandPalette: {
        isOpen: false,
        commands: [],
        filteredCommands: [],
        selectedIndex: 0,
        
        init: function() {
            this.registerDefaultCommands();
            this.attachKeyboardListeners();
            this.createPaletteElement();
        },
        
        registerDefaultCommands: function() {
            this.commands = [
                // Navigation
                { id: 'nav-dashboard', label: 'Go to Dashboard', icon: '🏠', action: () => this.navigate('dashboard') },
                { id: 'nav-portfolio', label: 'Go to Portfolio', icon: '💼', action: () => this.navigate('portfolio') },
                { id: 'nav-trades', label: 'Go to Trades', icon: '📊', action: () => this.navigate('trades') },
                { id: 'nav-performance', label: 'Go to Performance', icon: '📈', action: () => this.navigate('performance') },
                { id: 'nav-risk', label: 'Go to Risk Analysis', icon: '🛑', action: () => this.navigate('risk') },
                { id: 'nav-markets', label: 'Go to Markets', icon: '🌍', action: () => this.navigate('markets') },
                { id: 'nav-strategies', label: 'Go to Strategies', icon: '🧠', action: () => this.navigate('strategies') },
                { id: 'nav-backtesting', label: 'Go to Backtesting', icon: '⏱️', action: () => this.navigate('backtesting') },
                
                // Actions
                { id: 'action-refresh', label: 'Refresh Dashboard', icon: '🔄', action: () => location.reload() },
                { id: 'action-export', label: 'Export Data', icon: '📥', action: () => this.exportData() },
                { id: 'action-print', label: 'Print Dashboard', icon: '🖨️', action: () => window.print() },
                
                // Theme
                { id: 'theme-dark', label: 'Switch to Dark Theme', icon: '🌙', action: () => setTheme('dark') },
                { id: 'theme-light', label: 'Switch to Light Theme', icon: '☀️', action: () => setTheme('light') },
                { id: 'theme-bloomberg', label: 'Switch to Bloomberg Theme', icon: '💻', action: () => setTheme('bloomberg') },
                
                // Charts
                { id: 'chart-export', label: 'Export Current Chart', icon: '📷', action: () => this.exportChart() },
                { id: 'chart-fullscreen', label: 'Toggle Chart Fullscreen', icon: '⛶️', action: () => this.toggleFullscreen() },
                
                // Help
                { id: 'help-shortcuts', label: 'View Keyboard Shortcuts', icon: '⌨️', action: () => this.showShortcuts() },
                { id: 'help-docs', label: 'Open Documentation', icon: '📖', action: () => window.open('/docs', '_blank') }
            ];
        },
        
        attachKeyboardListeners: function() {
            document.addEventListener('keydown', (e) => {
                // Ctrl+K or Cmd+K to open
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    this.toggle();
                }
                
                // ESC to close
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
                
                // Arrow navigation
                if (this.isOpen) {
                    if (e.key === 'ArrowDown') {
                        e.preventDefault();
                        this.selectNext();
                    } else if (e.key === 'ArrowUp') {
                        e.preventDefault();
                        this.selectPrevious();
                    } else if (e.key === 'Enter') {
                        e.preventDefault();
                        this.executeSelected();
                    }
                }
            });
        },
        
        createPaletteElement: function() {
            const html = `
                <div id="command-palette" class="command-palette" style="display: none;">
                    <div class="command-palette-overlay"></div>
                    <div class="command-palette-container">
                        <div class="command-palette-input-wrapper">
                            <span class="command-palette-icon">🔍</span>
                            <input 
                                type="text" 
                                id="command-palette-input" 
                                class="command-palette-input" 
                                placeholder="Type a command or search..."
                                autocomplete="off"
                                spellcheck="false"
                            />
                            <kbd class="command-palette-hint">ESC</kbd>
                        </div>
                        <div id="command-palette-results" class="command-palette-results"></div>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', html);
            
            // Attach input listener
            const input = document.getElementById('command-palette-input');
            input.addEventListener('input', (e) => this.filterCommands(e.target.value));
            
            // Attach overlay click listener
            document.querySelector('.command-palette-overlay').addEventListener('click', () => this.close());
        },
        
        toggle: function() {
            if (this.isOpen) {
                this.close();
            } else {
                this.open();
            }
        },
        
        open: function() {
            this.isOpen = true;
            document.getElementById('command-palette').style.display = 'block';
            document.getElementById('command-palette-input').focus();
            this.filterCommands('');
        },
        
        close: function() {
            this.isOpen = false;
            document.getElementById('command-palette').style.display = 'none';
            document.getElementById('command-palette-input').value = '';
            this.selectedIndex = 0;
        },
        
        filterCommands: function(query) {
            const lowerQuery = query.toLowerCase();
            
            this.filteredCommands = this.commands.filter(cmd => 
                cmd.label.toLowerCase().includes(lowerQuery)
            );
            
            this.selectedIndex = 0;
            this.renderResults();
        },
        
        renderResults: function() {
            const resultsContainer = document.getElementById('command-palette-results');
            
            if (this.filteredCommands.length === 0) {
                resultsContainer.innerHTML = `
                    <div class="command-palette-empty">
                        <div class="command-palette-empty-icon">🔍</div>
                        <div class="command-palette-empty-text">No commands found</div>
                    </div>
                `;
                return;
            }
            
            const html = this.filteredCommands.map((cmd, index) => `
                <div class="command-palette-item ${index === this.selectedIndex ? 'selected' : ''}" 
                     data-command-id="${cmd.id}"
                     onclick="AdvancedFeatures.CommandPalette.executeCommand('${cmd.id}')">
                    <span class="command-palette-item-icon">${cmd.icon}</span>
                    <span class="command-palette-item-label">${cmd.label}</span>
                </div>
            `).join('');
            
            resultsContainer.innerHTML = html;
        },
        
        selectNext: function() {
            this.selectedIndex = Math.min(this.selectedIndex + 1, this.filteredCommands.length - 1);
            this.renderResults();
        },
        
        selectPrevious: function() {
            this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
            this.renderResults();
        },
        
        executeSelected: function() {
            if (this.filteredCommands.length > 0) {
                const cmd = this.filteredCommands[this.selectedIndex];
                this.executeCommand(cmd.id);
            }
        },
        
        executeCommand: function(commandId) {
            const cmd = this.commands.find(c => c.id === commandId);
            if (cmd) {
                cmd.action();
                this.close();
            }
        },
        
        navigate: function(section) {
            if (typeof loadSection === 'function') {
                loadSection(section);
            } else {
                console.log(`Navigate to: ${section}`);
            }
        },
        
        exportData: function() {
            console.log('Export data functionality');
        },
        
        exportChart: function() {
            if (window.ChartMastery) {
                ChartMastery.exportChart(document.querySelector('.chart-container').id, 'png');
            }
        },
        
        toggleFullscreen: function() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        },
        
        showShortcuts: function() {
            alert('Keyboard Shortcuts:\n\nCtrl+K: Command Palette\nESC: Close\nArrows: Navigate\nEnter: Execute');
        }
    },
    
    // ==================== 4. MULTI-CHART LAYOUT SWITCHER ====================
    LayoutSwitcher: {
        currentLayout: 'grid',
        
        layouts: {
            single: { cols: 1, rows: 1 },
            double: { cols: 2, rows: 1 },
            triple: { cols: 3, rows: 1 },
            grid: { cols: 2, rows: 2 },
            wide: { cols: 1, rows: 'auto' }
        },
        
        init: function(containerId) {
            this.container = document.getElementById(containerId);
            this.createSwitcher();
        },
        
        createSwitcher: function() {
            const html = `
                <div class="layout-switcher">
                    <button class="layout-btn" data-layout="single" title="Single Chart">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <rect x="2" y="2" width="12" height="12" rx="1"/>
                        </svg>
                    </button>
                    <button class="layout-btn" data-layout="double" title="Double Chart">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <rect x="2" y="2" width="5" height="12" rx="1"/>
                            <rect x="9" y="2" width="5" height="12" rx="1"/>
                        </svg>
                    </button>
                    <button class="layout-btn active" data-layout="grid" title="Grid Layout">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <rect x="2" y="2" width="5" height="5" rx="1"/>
                            <rect x="9" y="2" width="5" height="5" rx="1"/>
                            <rect x="2" y="9" width="5" height="5" rx="1"/>
                            <rect x="9" y="9" width="5" height="5" rx="1"/>
                        </svg>
                    </button>
                    <button class="layout-btn" data-layout="wide" title="Wide Layout">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <rect x="2" y="2" width="12" height="3" rx="1"/>
                            <rect x="2" y="7" width="12" height="3" rx="1"/>
                            <rect x="2" y="12" width="12" height="2" rx="1"/>
                        </svg>
                    </button>
                </div>
            `;
            
            // Insert into topbar or designated container
            const topbar = document.querySelector('.topbar-right');
            if (topbar) {
                topbar.insertAdjacentHTML('afterbegin', html);
            }
            
            this.attachListeners();
        },
        
        attachListeners: function() {
            document.querySelectorAll('.layout-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const layout = e.currentTarget.dataset.layout;
                    this.switchLayout(layout);
                });
            });
        },
        
        switchLayout: function(layoutName) {
            this.currentLayout = layoutName;
            const layout = this.layouts[layoutName];
            
            // Update charts grid
            const chartsGrid = document.querySelector('.charts-grid');
            if (chartsGrid) {
                chartsGrid.style.gridTemplateColumns = `repeat(${layout.cols}, 1fr)`;
                
                if (layout.rows !== 'auto') {
                    chartsGrid.style.gridTemplateRows = `repeat(${layout.rows}, 1fr)`;
                } else {
                    chartsGrid.style.gridTemplateRows = 'auto';
                }
            }
            
            // Update active button
            document.querySelectorAll('.layout-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.layout === layoutName);
            });
            
            // Save preference
            localStorage.setItem('dashboard-layout', layoutName);
        },
        
        loadSavedLayout: function() {
            const saved = localStorage.getItem('dashboard-layout');
            if (saved && this.layouts[saved]) {
                this.switchLayout(saved);
            }
        }
    },
    
    // ==================== 5. SHAREABLE SNAPSHOTS ====================
    Snapshots: {
        captureState: function() {
            const state = {
                section: document.getElementById('page-title')?.textContent,
                theme: document.documentElement.getAttribute('data-theme'),
                layout: AdvancedFeatures.LayoutSwitcher.currentLayout,
                filters: this.getCurrentFilters(),
                dateRange: this.getCurrentDateRange(),
                timestamp: Date.now()
            };
            
            return state;
        },
        
        getCurrentFilters: function() {
            // Placeholder - implement based on actual filters
            return {};
        },
        
        getCurrentDateRange: function() {
            // Placeholder - implement based on actual date range
            return { start: null, end: null };
        },
        
        createShareableLink: function() {
            const state = this.captureState();
            const encoded = btoa(JSON.stringify(state));
            const url = `${window.location.origin}${window.location.pathname}?snapshot=${encoded}`;
            
            return url;
        },
        
        copyToClipboard: function() {
            const url = this.createShareableLink();
            
            navigator.clipboard.writeText(url).then(() => {
                // Show success notification
                if (window.VisualExcellence) {
                    console.log('Snapshot URL copied to clipboard');
                }
            });
            
            return url;
        },
        
        restoreFromURL: function() {
            const params = new URLSearchParams(window.location.search);
            const snapshot = params.get('snapshot');
            
            if (snapshot) {
                try {
                    const state = JSON.parse(atob(snapshot));
                    this.restoreState(state);
                } catch (e) {
                    console.error('Failed to restore snapshot:', e);
                }
            }
        },
        
        restoreState: function(state) {
            // Restore theme
            if (state.theme && typeof setTheme === 'function') {
                setTheme(state.theme);
            }
            
            // Restore layout
            if (state.layout) {
                AdvancedFeatures.LayoutSwitcher.switchLayout(state.layout);
            }
            
            // Restore section
            if (state.section && typeof loadSection === 'function') {
                // Extract section from title
                const section = state.section.toLowerCase().replace(/\s+/g, '_');
                loadSection(section);
            }
        }
    },
    
    // ==================== INITIALIZATION ====================
    init: function() {
        console.log('🚀 Initializing Advanced Features...');
        
        // Initialize Command Palette
        this.CommandPalette.init();
        
        // Initialize Layout Switcher
        this.LayoutSwitcher.init('charts-grid');
        this.LayoutSwitcher.loadSavedLayout();
        
        // Restore snapshot if present
        this.Snapshots.restoreFromURL();
        
        console.log('✅ Advanced Features v7.2 initialized');
    }
};

// ==================== AUTO-INITIALIZE ====================
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => AdvancedFeatures.init());
} else {
    AdvancedFeatures.init();
}

// ==================== EXPORTS ====================
window.AdvancedFeatures = AdvancedFeatures;

console.log('✅ Advanced Features v7.2 loaded successfully');
