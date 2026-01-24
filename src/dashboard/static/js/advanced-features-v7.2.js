// ==================== BotV2 Dashboard Advanced Features v7.2 ====================
// Iteration 3: Command Palette + AI Insights + Advanced UX
// Author: Juan Carlos Garcia
// Date: 24 Enero 2026
//
// Features:
// - Command Palette (Ctrl+K) - VSCode-style navigation
// - Automated Insights Panel - AI-powered analysis
// - Anomaly Detection - Real-time alerts
// - Multi-Chart Layout Switcher - Dynamic layouts
// - Shareable Snapshots - URL state persistence
// - Quick Actions - Contextual shortcuts
// - Smart Search - Fuzzy matching

console.log('🚀 Advanced Features v7.2 initializing...');

// ==================== COMMAND PALETTE ====================
class CommandPalette {
    constructor() {
        this.isOpen = false;
        this.commands = [];
        this.filteredCommands = [];
        this.selectedIndex = 0;
        this.recentCommands = this.loadRecentCommands();
        
        this.init();
        this.registerDefaultCommands();
        this.setupKeyboardShortcuts();
    }
    
    init() {
        // Create palette HTML
        const paletteHTML = `
            <div id="command-palette-overlay" class="command-palette-overlay" style="display: none;">
                <div class="command-palette">
                    <div class="command-palette-header">
                        <svg class="command-icon" width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/>
                        </svg>
                        <input 
                            type="text" 
                            id="command-palette-input" 
                            class="command-palette-input" 
                            placeholder="Type a command or search..."
                            autocomplete="off"
                            spellcheck="false"
                        >
                        <kbd class="command-palette-kbd">ESC</kbd>
                    </div>
                    <div class="command-palette-body">
                        <div class="command-palette-section">
                            <div class="command-palette-section-title">Recent</div>
                            <div id="command-palette-recent" class="command-palette-list"></div>
                        </div>
                        <div class="command-palette-section">
                            <div class="command-palette-section-title">Commands</div>
                            <div id="command-palette-results" class="command-palette-list"></div>
                        </div>
                    </div>
                    <div class="command-palette-footer">
                        <span class="command-palette-hint">
                            <kbd>↑</kbd><kbd>↓</kbd> Navigate
                            <kbd>↵</kbd> Select
                            <kbd>ESC</kbd> Close
                        </span>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', paletteHTML);
        
        // Get references
        this.overlay = document.getElementById('command-palette-overlay');
        this.input = document.getElementById('command-palette-input');
        this.resultsContainer = document.getElementById('command-palette-results');
        this.recentContainer = document.getElementById('command-palette-recent');
        
        // Setup event listeners
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.close();
        });
    }
    
    registerDefaultCommands() {
        this.commands = [
            // Navigation
            { id: 'nav-dashboard', icon: '📊', title: 'Go to Dashboard', category: 'Navigation', action: () => loadSection('dashboard') },
            { id: 'nav-portfolio', icon: '💼', title: 'Go to Portfolio', category: 'Navigation', action: () => loadSection('portfolio') },
            { id: 'nav-trades', icon: '📈', title: 'Go to Trades', category: 'Navigation', action: () => loadSection('trades') },
            { id: 'nav-performance', icon: '📉', title: 'Go to Performance', category: 'Navigation', action: () => loadSection('performance') },
            { id: 'nav-risk', icon: '🛡️', title: 'Go to Risk Analysis', category: 'Navigation', action: () => loadSection('risk') },
            { id: 'nav-markets', icon: '🌍', title: 'Go to Market Overview', category: 'Navigation', action: () => loadSection('markets') },
            { id: 'nav-strategies', icon: '⚙️', title: 'Go to Strategies', category: 'Navigation', action: () => loadSection('strategies') },
            { id: 'nav-control', icon: '🎮', title: 'Go to Control Panel', category: 'Navigation', action: () => loadSection('control_panel') },
            
            // Themes
            { id: 'theme-dark', icon: '🌙', title: 'Switch to Dark Theme', category: 'Appearance', action: () => setTheme('dark') },
            { id: 'theme-light', icon: '☀️', title: 'Switch to Light Theme', category: 'Appearance', action: () => setTheme('light') },
            { id: 'theme-bloomberg', icon: '💻', title: 'Switch to Bloomberg Theme', category: 'Appearance', action: () => setTheme('bloomberg') },
            
            // Actions
            { id: 'refresh-data', icon: '🔄', title: 'Refresh Dashboard Data', category: 'Actions', action: () => window.location.reload() },
            { id: 'export-data', icon: '📥', title: 'Export Data to CSV', category: 'Actions', action: () => this.exportData() },
            { id: 'share-snapshot', icon: '📸', title: 'Create Shareable Snapshot', category: 'Actions', action: () => this.createSnapshot() },
            { id: 'toggle-insights', icon: '🧠', title: 'Toggle Insights Panel', category: 'Actions', action: () => InsightsPanel.toggle() },
            { id: 'toggle-fullscreen', icon: '⛶', title: 'Toggle Fullscreen', category: 'Actions', action: () => this.toggleFullscreen() },
            
            // Layout
            { id: 'layout-single', icon: '▪️', title: 'Single Chart Layout', category: 'Layout', action: () => LayoutSwitcher.setLayout('single') },
            { id: 'layout-double', icon: '▪️▪️', title: 'Double Chart Layout', category: 'Layout', action: () => LayoutSwitcher.setLayout('double') },
            { id: 'layout-grid', icon: '▦', title: 'Grid Layout', category: 'Layout', action: () => LayoutSwitcher.setLayout('grid') },
            { id: 'layout-wide', icon: '▬', title: 'Wide Layout', category: 'Layout', action: () => LayoutSwitcher.setLayout('wide') },
            
            // Help
            { id: 'help-shortcuts', icon: '⌨️', title: 'View Keyboard Shortcuts', category: 'Help', action: () => this.showShortcuts() },
            { id: 'help-docs', icon: '📚', title: 'Open Documentation', category: 'Help', action: () => window.open('/docs', '_blank') },
        ];
    }
    
    setupKeyboardShortcuts() {
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
        });
    }
    
    open() {
        this.isOpen = true;
        this.overlay.style.display = 'flex';
        this.input.value = '';
        this.input.focus();
        this.selectedIndex = 0;
        this.renderRecent();
        this.renderResults(this.commands);
        
        // Animation
        requestAnimationFrame(() => {
            this.overlay.classList.add('active');
        });
    }
    
    close() {
        this.isOpen = false;
        this.overlay.classList.remove('active');
        
        setTimeout(() => {
            this.overlay.style.display = 'none';
        }, 200);
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    handleInput(e) {
        const query = e.target.value.toLowerCase().trim();
        
        if (query === '') {
            this.filteredCommands = this.commands;
        } else {
            // Fuzzy search
            this.filteredCommands = this.commands.filter(cmd => {
                const titleMatch = this.fuzzyMatch(query, cmd.title.toLowerCase());
                const categoryMatch = this.fuzzyMatch(query, cmd.category.toLowerCase());
                return titleMatch || categoryMatch;
            }).sort((a, b) => {
                // Sort by relevance
                const aScore = this.fuzzyScore(query, a.title.toLowerCase());
                const bScore = this.fuzzyScore(query, b.title.toLowerCase());
                return bScore - aScore;
            });
        }
        
        this.selectedIndex = 0;
        this.renderResults(this.filteredCommands);
    }
    
    fuzzyMatch(query, text) {
        let queryIndex = 0;
        for (let i = 0; i < text.length && queryIndex < query.length; i++) {
            if (text[i] === query[queryIndex]) {
                queryIndex++;
            }
        }
        return queryIndex === query.length;
    }
    
    fuzzyScore(query, text) {
        let score = 0;
        let queryIndex = 0;
        
        for (let i = 0; i < text.length && queryIndex < query.length; i++) {
            if (text[i] === query[queryIndex]) {
                score += (text.length - i);
                queryIndex++;
            }
        }
        
        return score;
    }
    
    handleKeydown(e) {
        const commands = this.filteredCommands.length > 0 ? this.filteredCommands : this.commands;
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, commands.length - 1);
                this.renderResults(commands);
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
                this.renderResults(commands);
                break;
                
            case 'Enter':
                e.preventDefault();
                if (commands[this.selectedIndex]) {
                    this.executeCommand(commands[this.selectedIndex]);
                }
                break;
        }
    }
    
    executeCommand(command) {
        // Add to recent
        this.addToRecent(command);
        
        // Close palette
        this.close();
        
        // Execute action
        setTimeout(() => {
            try {
                command.action();
                console.log(`✅ Executed command: ${command.title}`);
            } catch (error) {
                console.error(`❌ Error executing command: ${command.title}`, error);
            }
        }, 100);
    }
    
    renderRecent() {
        if (this.recentCommands.length === 0) {
            this.recentContainer.parentElement.style.display = 'none';
            return;
        }
        
        this.recentContainer.parentElement.style.display = 'block';
        
        const html = this.recentCommands.slice(0, 5).map(cmd => `
            <div class="command-palette-item" data-command-id="${cmd.id}">
                <span class="command-icon-text">${cmd.icon}</span>
                <span class="command-title">${cmd.title}</span>
                <span class="command-category">${cmd.category}</span>
            </div>
        `).join('');
        
        this.recentContainer.innerHTML = html;
        
        // Add click listeners
        this.recentContainer.querySelectorAll('.command-palette-item').forEach(item => {
            item.addEventListener('click', () => {
                const cmdId = item.dataset.commandId;
                const cmd = this.commands.find(c => c.id === cmdId);
                if (cmd) this.executeCommand(cmd);
            });
        });
    }
    
    renderResults(commands) {
        if (commands.length === 0) {
            this.resultsContainer.innerHTML = `
                <div class="command-palette-empty">
                    <span>No commands found</span>
                </div>
            `;
            return;
        }
        
        const html = commands.map((cmd, index) => `
            <div class="command-palette-item ${index === this.selectedIndex ? 'selected' : ''}" 
                 data-command-id="${cmd.id}"
                 data-index="${index}">
                <span class="command-icon-text">${cmd.icon}</span>
                <span class="command-title">${cmd.title}</span>
                <span class="command-category">${cmd.category}</span>
            </div>
        `).join('');
        
        this.resultsContainer.innerHTML = html;
        
        // Scroll selected into view
        const selectedItem = this.resultsContainer.querySelector('.selected');
        if (selectedItem) {
            selectedItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
        
        // Add click listeners
        this.resultsContainer.querySelectorAll('.command-palette-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                this.selectedIndex = index;
                this.executeCommand(commands[index]);
            });
            
            item.addEventListener('mouseenter', () => {
                const index = parseInt(item.dataset.index);
                this.selectedIndex = index;
                this.renderResults(commands);
            });
        });
    }
    
    addToRecent(command) {
        // Remove if already exists
        this.recentCommands = this.recentCommands.filter(c => c.id !== command.id);
        
        // Add to front
        this.recentCommands.unshift(command);
        
        // Keep only 10 recent
        this.recentCommands = this.recentCommands.slice(0, 10);
        
        // Save to localStorage
        this.saveRecentCommands();
    }
    
    loadRecentCommands() {
        try {
            const recent = localStorage.getItem('commandPaletteRecent');
            return recent ? JSON.parse(recent) : [];
        } catch {
            return [];
        }
    }
    
    saveRecentCommands() {
        try {
            localStorage.setItem('commandPaletteRecent', JSON.stringify(this.recentCommands));
        } catch (error) {
            console.warn('Could not save recent commands:', error);
        }
    }
    
    // Utility actions
    exportData() {
        console.log('📥 Exporting data...');
        // Implementation would fetch current data and create CSV
        alert('Export feature coming soon!');
    }
    
    createSnapshot() {
        console.log('📸 Creating snapshot...');
        SnapshotManager.create();
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
    
    showShortcuts() {
        const shortcuts = [
            { keys: 'Ctrl+K / Cmd+K', description: 'Open Command Palette' },
            { keys: 'ESC', description: 'Close Palette' },
            { keys: '↑ / ↓', description: 'Navigate Commands' },
            { keys: 'Enter', description: 'Execute Command' },
            { keys: 'Ctrl+/', description: 'Toggle Insights' },
            { keys: 'F11', description: 'Toggle Fullscreen' },
        ];
        
        const html = shortcuts.map(s => `${s.keys} - ${s.description}`).join('\n');
        alert(`Keyboard Shortcuts:\n\n${html}`);
    }
}

// ==================== AUTOMATED INSIGHTS PANEL ====================
class InsightsPanel {
    constructor() {
        this.isOpen = false;
        this.insights = [];
        this.updateInterval = null;
        
        this.init();
    }
    
    init() {
        const panelHTML = `
            <div id="insights-panel" class="insights-panel" style="display: none;">
                <div class="insights-header">
                    <div class="insights-title">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                            <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/>
                        </svg>
                        <span>Smart Insights</span>
                        <span class="insights-badge" id="insights-count">0</span>
                    </div>
                    <button class="insights-close" onclick="InsightsPanel.close()">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                        </svg>
                    </button>
                </div>
                <div class="insights-body" id="insights-body">
                    <div class="insights-loading">
                        <div class="spinner"></div>
                        <p>Analyzing data...</p>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', panelHTML);
        this.panel = document.getElementById('insights-panel');
        this.body = document.getElementById('insights-body');
        this.countBadge = document.getElementById('insights-count');
        
        // Setup keyboard shortcut (Ctrl+/)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === '/') {
                e.preventDefault();
                this.toggle();
            }
        });
    }
    
    open() {
        this.isOpen = true;
        this.panel.style.display = 'block';
        
        requestAnimationFrame(() => {
            this.panel.classList.add('active');
        });
        
        // Generate insights
        this.generateInsights();
        
        // Auto-update every 30 seconds
        this.updateInterval = setInterval(() => this.generateInsights(), 30000);
    }
    
    close() {
        this.isOpen = false;
        this.panel.classList.remove('active');
        
        setTimeout(() => {
            this.panel.style.display = 'none';
        }, 300);
        
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    async generateInsights() {
        console.log('🧠 Generating insights...');
        
        // Simulate AI analysis (in production, this would call backend API)
        await this.simulateAnalysis();
        
        // Get current dashboard data (mock for now)
        const data = this.getMockData();
        
        // Generate insights
        this.insights = [];
        
        // Performance insights
        if (data.dailyReturn > 3) {
            this.insights.push({
                type: 'success',
                icon: '📈',
                title: 'Strong Performance',
                description: `Portfolio up ${data.dailyReturn.toFixed(1)}% today. Momentum is building.`,
                action: { text: 'View Performance', handler: () => loadSection('performance') }
            });
        } else if (data.dailyReturn < -3) {
            this.insights.push({
                type: 'warning',
                icon: '📉',
                title: 'Performance Alert',
                description: `Portfolio down ${Math.abs(data.dailyReturn).toFixed(1)}% today. Review risk exposure.`,
                action: { text: 'View Risk Analysis', handler: () => loadSection('risk') }
            });
        }
        
        // Drawdown insights
        if (data.drawdown > 10) {
            this.insights.push({
                type: 'danger',
                icon: '⚠️',
                title: 'High Drawdown',
                description: `Current drawdown at ${data.drawdown.toFixed(1)}%. Consider reducing exposure.`,
                action: { text: 'View Positions', handler: () => loadSection('portfolio') }
            });
        }
        
        // Opportunity insights
        if (data.unusedCapital > 5000) {
            this.insights.push({
                type: 'info',
                icon: '💡',
                title: 'Unused Capital',
                description: `€${data.unusedCapital.toLocaleString()} available for deployment.`,
                action: { text: 'View Markets', handler: () => loadSection('markets') }
            });
        }
        
        // Volatility insights
        if (data.volatility > 20) {
            this.insights.push({
                type: 'warning',
                icon: '🌊',
                title: 'High Volatility',
                description: 'Market volatility elevated. Adjust position sizing accordingly.',
                action: { text: 'View Risk Metrics', handler: () => loadSection('risk') }
            });
        }
        
        // Win rate insights
        if (data.winRate > 60) {
            this.insights.push({
                type: 'success',
                icon: '🎯',
                title: 'Excellent Win Rate',
                description: `Win rate at ${data.winRate.toFixed(0)}%. Strategy performing well.`,
                action: { text: 'View Trades', handler: () => loadSection('trades') }
            });
        }
        
        // Correlation insights
        if (data.correlation > 0.7) {
            this.insights.push({
                type: 'warning',
                icon: '🔗',
                title: 'High Correlation',
                description: 'Portfolio positions highly correlated. Consider diversification.',
                action: { text: 'View Portfolio', handler: () => loadSection('portfolio') }
            });
        }
        
        // Render insights
        this.render();
    }
    
    async simulateAnalysis() {
        return new Promise(resolve => setTimeout(resolve, 800));
    }
    
    getMockData() {
        // In production, this would get real dashboard data
        return {
            dailyReturn: (Math.random() - 0.5) * 10,
            drawdown: Math.random() * 15,
            unusedCapital: Math.random() * 20000,
            volatility: Math.random() * 30,
            winRate: 50 + Math.random() * 30,
            correlation: Math.random()
        };
    }
    
    render() {
        if (this.insights.length === 0) {
            this.body.innerHTML = `
                <div class="insights-empty">
                    <svg width="48" height="48" fill="currentColor" viewBox="0 0 20 20" opacity="0.3">
                        <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"/>
                    </svg>
                    <p>No insights at the moment</p>
                    <span>Everything looks good!</span>
                </div>
            `;
            this.countBadge.textContent = '0';
            return;
        }
        
        const html = this.insights.map(insight => `
            <div class="insight-card insight-${insight.type}">
                <div class="insight-icon">${insight.icon}</div>
                <div class="insight-content">
                    <div class="insight-title">${insight.title}</div>
                    <div class="insight-description">${insight.description}</div>
                    ${insight.action ? `
                        <button class="insight-action" onclick="(${insight.action.handler.toString()})()">
                            ${insight.action.text} →
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
        
        this.body.innerHTML = html;
        this.countBadge.textContent = this.insights.length;
    }
}

// ==================== ANOMALY DETECTOR ====================
class AnomalyDetector {
    constructor() {
        this.thresholds = {
            rapidDrawdown: 5,      // % in 5 minutes
            unusualVolume: 3,      // 3x average
            priceSpike: 10,        // % sudden change
            correlationBreak: 0.3  // correlation delta
        };
        
        this.history = [];
        this.alerts = [];
    }
    
    detect(data) {
        const anomalies = [];
        
        // Rapid drawdown detection
        if (this.detectRapidDrawdown(data)) {
            anomalies.push({
                type: 'rapid_drawdown',
                severity: 'high',
                message: 'Rapid drawdown detected',
                value: data.drawdown
            });
        }
        
        // Unusual volume
        if (this.detectUnusualVolume(data)) {
            anomalies.push({
                type: 'unusual_volume',
                severity: 'medium',
                message: 'Trading volume spike detected',
                value: data.volume
            });
        }
        
        // Price spike
        if (this.detectPriceSpike(data)) {
            anomalies.push({
                type: 'price_spike',
                severity: 'medium',
                message: 'Sudden price movement detected',
                value: data.priceChange
            });
        }
        
        // Store in history
        this.history.push({ timestamp: Date.now(), data, anomalies });
        
        // Keep only last 100 records
        if (this.history.length > 100) {
            this.history.shift();
        }
        
        // Trigger alerts if needed
        if (anomalies.length > 0) {
            this.triggerAlerts(anomalies);
        }
        
        return anomalies;
    }
    
    detectRapidDrawdown(data) {
        if (this.history.length < 5) return false;
        
        const recent = this.history.slice(-5);
        const initialValue = recent[0].data.portfolioValue;
        const currentValue = data.portfolioValue;
        const change = ((currentValue - initialValue) / initialValue) * 100;
        
        return change < -this.thresholds.rapidDrawdown;
    }
    
    detectUnusualVolume(data) {
        if (this.history.length < 10) return false;
        
        const avgVolume = this.history.slice(-10).reduce((sum, h) => sum + h.data.volume, 0) / 10;
        return data.volume > avgVolume * this.thresholds.unusualVolume;
    }
    
    detectPriceSpike(data) {
        if (this.history.length < 1) return false;
        
        const lastPrice = this.history[this.history.length - 1].data.price;
        const priceChange = Math.abs(((data.price - lastPrice) / lastPrice) * 100);
        
        return priceChange > this.thresholds.priceSpike;
    }
    
    triggerAlerts(anomalies) {
        anomalies.forEach(anomaly => {
            console.warn(`🚨 Anomaly detected: ${anomaly.message}`);
            
            // Show notification (if permission granted)
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('BotV2 Alert', {
                    body: anomaly.message,
                    icon: '/static/icon-192.png',
                    badge: '/static/badge-72.png'
                });
            }
            
            // Add to alerts list
            this.alerts.push({
                timestamp: new Date(),
                ...anomaly
            });
        });
    }
}

// ==================== LAYOUT SWITCHER ====================
class LayoutSwitcher {
    constructor() {
        this.currentLayout = 'grid';
        this.layouts = ['single', 'double', 'grid', 'wide'];
    }
    
    setLayout(layout) {
        if (!this.layouts.includes(layout)) {
            console.error(`Invalid layout: ${layout}`);
            return;
        }
        
        this.currentLayout = layout;
        
        const chartsGrid = document.querySelector('.charts-grid');
        if (!chartsGrid) return;
        
        // Remove all layout classes
        chartsGrid.classList.remove('layout-single', 'layout-double', 'layout-grid', 'layout-wide');
        
        // Add new layout class
        chartsGrid.classList.add(`layout-${layout}`);
        
        // Save preference
        localStorage.setItem('dashboardLayout', layout);
        
        console.log(`📐 Layout changed to: ${layout}`);
        
        // Trigger chart resize (for Plotly)
        setTimeout(() => {
            if (typeof Plotly !== 'undefined') {
                document.querySelectorAll('.chart-container').forEach(container => {
                    Plotly.Plots.resize(container);
                });
            }
        }, 300);
    }
    
    loadSavedLayout() {
        const saved = localStorage.getItem('dashboardLayout');
        if (saved && this.layouts.includes(saved)) {
            this.setLayout(saved);
        }
    }
}

// ==================== SNAPSHOT MANAGER ====================
class SnapshotManager {
    static create() {
        const state = {
            section: document.querySelector('.menu-item.active')?.dataset.section || 'dashboard',
            theme: document.documentElement.getAttribute('data-theme') || 'dark',
            layout: LayoutSwitcher.currentLayout,
            filters: this.getCurrentFilters(),
            timestamp: Date.now()
        };
        
        // Encode state to base64
        const encoded = btoa(JSON.stringify(state));
        
        // Create shareable URL
        const url = `${window.location.origin}${window.location.pathname}?snapshot=${encoded}`;
        
        // Copy to clipboard
        this.copyToClipboard(url);
        
        // Show notification
        this.showNotification('📸 Snapshot created and copied to clipboard!');
        
        console.log('📸 Snapshot URL:', url);
    }
    
    static restore(encoded) {
        try {
            const state = JSON.parse(atob(encoded));
            
            console.log('🔄 Restoring snapshot:', state);
            
            // Restore theme
            if (state.theme) {
                setTheme(state.theme);
            }
            
            // Restore layout
            if (state.layout && typeof LayoutSwitcher !== 'undefined') {
                LayoutSwitcher.setLayout(state.layout);
            }
            
            // Restore section
            if (state.section && typeof loadSection === 'function') {
                loadSection(state.section);
            }
            
            // Restore filters
            if (state.filters) {
                this.applyFilters(state.filters);
            }
            
            this.showNotification('✅ Snapshot restored!');
        } catch (error) {
            console.error('Error restoring snapshot:', error);
            this.showNotification('❌ Invalid snapshot');
        }
    }
    
    static getCurrentFilters() {
        // Placeholder - would get actual filter state
        return {
            dateRange: 'last_7_days',
            strategy: 'all',
            symbol: 'all'
        };
    }
    
    static applyFilters(filters) {
        // Placeholder - would apply filters to dashboard
        console.log('Applying filters:', filters);
    }
    
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
        } catch (err) {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    }
    
    static showNotification(message) {
        // Simple notification (could be enhanced with a proper toast component)
        const notification = document.createElement('div');
        notification.className = 'snapshot-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-tertiary);
            color: var(--text-primary);
            padding: 12px 20px;
            border-radius: 8px;
            border: 1px solid var(--border-default);
            box-shadow: var(--shadow-lg);
            z-index: 10000;
            animation: slideInRight 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// ==================== INITIALIZATION ====================
function initAdvancedFeatures() {
    console.log('🚀 Initializing Advanced Features v7.2...');
    
    // Initialize Command Palette
    window.CommandPalette = new CommandPalette();
    
    // Initialize Insights Panel
    window.InsightsPanel = new InsightsPanel();
    
    // Initialize Anomaly Detector
    window.AnomalyDetector = new AnomalyDetector();
    
    // Initialize Layout Switcher
    window.LayoutSwitcher = new LayoutSwitcher();
    LayoutSwitcher.loadSavedLayout();
    
    // Check for snapshot in URL
    const urlParams = new URLSearchParams(window.location.search);
    const snapshotParam = urlParams.get('snapshot');
    if (snapshotParam) {
        SnapshotManager.restore(snapshotParam);
    }
    
    console.log('✅ Advanced Features v7.2 initialized');
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAdvancedFeatures);
} else {
    initAdvancedFeatures();
}

// Export for global use
window.AdvancedFeatures = {
    CommandPalette,
    InsightsPanel,
    AnomalyDetector,
    LayoutSwitcher,
    SnapshotManager,
    init: initAdvancedFeatures
};

console.log('✅ Advanced Features v7.2 module loaded');
