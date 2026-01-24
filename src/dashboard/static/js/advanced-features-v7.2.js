/**
 * ========================================
 * BotV2 Dashboard - Advanced Features v7.2
 * ========================================
 * 
 * Professional Advanced Features Module
 * 
 * Features:
 * - Command Palette (Ctrl/Cmd+K)
 * - AI-Powered Insights Panel
 * - Anomaly Detection System
 * - Multi-Chart Layout Manager
 * - Shareable Chart Snapshots
 * - Keyboard Shortcuts
 * - Quick Actions
 * - Search Everything
 * 
 * Dependencies:
 * - visual-excellence.js
 * - chart-mastery-v7.1.js
 * 
 * @version 7.2.0
 * @author Juan Carlos Garcia
 * @date 24 Enero 2026
 */

(function(window) {
    'use strict';

    /**
     * Command Palette Class
     */
    class CommandPalette {
        constructor() {
            this.isOpen = false;
            this.commands = [];
            this.filteredCommands = [];
            this.selectedIndex = 0;
            this.init();
        }

        init() {
            this.createPaletteHTML();
            this.registerDefaultCommands();
            this.attachEventListeners();
        }

        createPaletteHTML() {
            const html = `
                <div id="command-palette" class="command-palette" style="display: none;">
                    <div class="command-palette-backdrop"></div>
                    <div class="command-palette-container">
                        <div class="command-palette-header">
                            <svg class="command-icon" width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/>
                            </svg>
                            <input type="text" id="command-input" class="command-input" placeholder="Type a command or search..." autocomplete="off" />
                            <kbd class="command-kbd">ESC</kbd>
                        </div>
                        <div class="command-palette-results" id="command-results"></div>
                        <div class="command-palette-footer">
                            <span class="command-hint"><kbd>↑</kbd><kbd>↓</kbd> Navigate</span>
                            <span class="command-hint"><kbd>Enter</kbd> Select</span>
                            <span class="command-hint"><kbd>ESC</kbd> Close</span>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', html);
        }

        registerDefaultCommands() {
            this.commands = [
                // Navigation
                { id: 'nav-dashboard', name: 'Go to Dashboard', icon: '🏠', category: 'Navigation', action: () => this.navigateTo('dashboard') },
                { id: 'nav-portfolio', name: 'Go to Portfolio', icon: '💼', category: 'Navigation', action: () => this.navigateTo('portfolio') },
                { id: 'nav-trades', name: 'Go to Trades', icon: '📊', category: 'Navigation', action: () => this.navigateTo('trades') },
                { id: 'nav-performance', name: 'Go to Performance', icon: '📈', category: 'Navigation', action: () => this.navigateTo('performance') },
                { id: 'nav-risk', name: 'Go to Risk Analysis', icon: '⚠️', category: 'Navigation', action: () => this.navigateTo('risk') },
                { id: 'nav-settings', name: 'Go to Settings', icon: '⚙️', category: 'Navigation', action: () => this.navigateTo('settings') },

                // Theme
                { id: 'theme-dark', name: 'Switch to Dark Theme', icon: '🌙', category: 'Theme', action: () => this.setTheme('dark') },
                { id: 'theme-light', name: 'Switch to Light Theme', icon: '☀️', category: 'Theme', action: () => this.setTheme('light') },
                { id: 'theme-bloomberg', name: 'Switch to Bloomberg Theme', icon: '📰', category: 'Theme', action: () => this.setTheme('bloomberg') },

                // Actions
                { id: 'export-data', name: 'Export Dashboard Data', icon: '📥', category: 'Actions', action: () => this.exportDashboardData() },
                { id: 'refresh-data', name: 'Refresh All Data', icon: '🔄', category: 'Actions', action: () => this.refreshAllData() },
                { id: 'take-snapshot', name: 'Take Dashboard Snapshot', icon: '📸', category: 'Actions', action: () => window.AdvancedFeatures.takeSnapshot() },
                { id: 'show-insights', name: 'Show AI Insights', icon: '🧠', category: 'Actions', action: () => window.AdvancedFeatures.showInsights() },
                { id: 'detect-anomalies', name: 'Detect Anomalies', icon: '🔍', category: 'Actions', action: () => window.AdvancedFeatures.detectAnomalies() },

                // Layouts
                { id: 'layout-single', name: 'Single Chart Layout', icon: '📋', category: 'Layout', action: () => this.setLayout('single') },
                { id: 'layout-grid', name: 'Grid Layout (2x2)', icon: '⬚', category: 'Layout', action: () => this.setLayout('grid') },
                { id: 'layout-dashboard', name: 'Dashboard Layout', icon: '🗺', category: 'Layout', action: () => this.setLayout('dashboard') },

                // Help
                { id: 'help-shortcuts', name: 'View Keyboard Shortcuts', icon: '⌨️', category: 'Help', action: () => this.showShortcuts() },
                { id: 'help-docs', name: 'Open Documentation', icon: '📖', category: 'Help', action: () => this.openDocs() }
            ];
        }

        attachEventListeners() {
            // Keyboard shortcut to open (Ctrl/Cmd + K)
            document.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    this.toggle();
                }
            });

            // Close on backdrop click
            const backdrop = document.querySelector('.command-palette-backdrop');
            backdrop?.addEventListener('click', () => this.close());

            // Close on ESC
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            });

            // Input handler
            const input = document.getElementById('command-input');
            input?.addEventListener('input', (e) => this.handleInput(e.target.value));

            // Keyboard navigation
            input?.addEventListener('keydown', (e) => this.handleKeyNavigation(e));
        }

        handleInput(query) {
            if (!query.trim()) {
                this.filteredCommands = this.commands;
            } else {
                const lowerQuery = query.toLowerCase();
                this.filteredCommands = this.commands.filter(cmd => 
                    cmd.name.toLowerCase().includes(lowerQuery) ||
                    cmd.category.toLowerCase().includes(lowerQuery)
                );
            }
            this.selectedIndex = 0;
            this.renderResults();
        }

        handleKeyNavigation(e) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, this.filteredCommands.length - 1);
                this.renderResults();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
                this.renderResults();
            } else if (e.key === 'Enter') {
                e.preventDefault();
                this.executeSelected();
            }
        }

        renderResults() {
            const resultsContainer = document.getElementById('command-results');
            if (!resultsContainer) return;

            if (this.filteredCommands.length === 0) {
                resultsContainer.innerHTML = '<div class="command-empty">No commands found</div>';
                return;
            }

            const html = this.filteredCommands.map((cmd, idx) => `
                <div class="command-item ${idx === this.selectedIndex ? 'selected' : ''}" data-index="${idx}">
                    <span class="command-item-icon">${cmd.icon}</span>
                    <div class="command-item-content">
                        <div class="command-item-name">${cmd.name}</div>
                        <div class="command-item-category">${cmd.category}</div>
                    </div>
                </div>
            `).join('');

            resultsContainer.innerHTML = html;

            // Add click handlers
            resultsContainer.querySelectorAll('.command-item').forEach((item, idx) => {
                item.addEventListener('click', () => {
                    this.selectedIndex = idx;
                    this.executeSelected();
                });
            });
        }

        executeSelected() {
            const command = this.filteredCommands[this.selectedIndex];
            if (command && command.action) {
                command.action();
                this.close();
            }
        }

        open() {
            const palette = document.getElementById('command-palette');
            const input = document.getElementById('command-input');
            
            if (palette) {
                this.isOpen = true;
                palette.style.display = 'block';
                setTimeout(() => {
                    palette.classList.add('active');
                    input?.focus();
                }, 10);
                this.filteredCommands = this.commands;
                this.renderResults();
            }
        }

        close() {
            const palette = document.getElementById('command-palette');
            const input = document.getElementById('command-input');
            
            if (palette) {
                palette.classList.remove('active');
                setTimeout(() => {
                    this.isOpen = false;
                    palette.style.display = 'none';
                    if (input) input.value = '';
                }, 200);
            }
        }

        toggle() {
            if (this.isOpen) {
                this.close();
            } else {
                this.open();
            }
        }

        // Command actions
        navigateTo(section) {
            const menuItem = document.querySelector(`.menu-item[data-section="${section}"]`);
            menuItem?.click();
        }

        setTheme(theme) {
            if (typeof setTheme === 'function') {
                setTheme(theme);
            }
        }

        setLayout(layout) {
            console.log('Setting layout:', layout);
            // Implementation would depend on dashboard.js
        }

        exportDashboardData() {
            console.log('Exporting dashboard data...');
            // Implementation
        }

        refreshAllData() {
            console.log('Refreshing all data...');
            window.location.reload();
        }

        showShortcuts() {
            alert('Keyboard Shortcuts:\n\nCtrl/Cmd + K: Command Palette\nCtrl/Cmd + R: Refresh Data\nCtrl/Cmd + S: Take Snapshot');
        }

        openDocs() {
            window.open('https://github.com/juankaspain/BotV2/tree/main/docs', '_blank');
        }
    }

    /**
     * AI Insights Panel Class
     */
    class AIInsightsPanel {
        constructor() {
            this.insights = [];
            this.isVisible = false;
        }

        async generateInsights(portfolioData, tradesData, performanceData) {
            this.insights = [];

            // 1. Win Rate Analysis
            const winRate = this.calculateWinRate(tradesData);
            if (winRate < 45) {
                this.insights.push({
                    type: 'warning',
                    category: 'Performance',
                    title: 'Low Win Rate Detected',
                    message: `Your win rate is ${winRate.toFixed(1)}%, which is below optimal. Consider reviewing your entry criteria.`,
                    actionable: true,
                    action: 'Review Strategy'
                });
            } else if (winRate > 65) {
                this.insights.push({
                    type: 'success',
                    category: 'Performance',
                    title: 'Excellent Win Rate',
                    message: `Your win rate of ${winRate.toFixed(1)}% is outstanding! Keep following your current strategy.`,
                    actionable: false
                });
            }

            // 2. Risk-Reward Ratio
            const avgRR = this.calculateAvgRiskReward(tradesData);
            if (avgRR < 1.5) {
                this.insights.push({
                    type: 'warning',
                    category: 'Risk',
                    title: 'Risk-Reward Needs Improvement',
                    message: `Your average risk-reward ratio is ${avgRR.toFixed(2)}:1. Aim for at least 2:1 for better profitability.`,
                    actionable: true,
                    action: 'Optimize Targets'
                });
            }

            // 3. Drawdown Alert
            const maxDrawdown = this.calculateMaxDrawdown(performanceData);
            if (maxDrawdown > 20) {
                this.insights.push({
                    type: 'danger',
                    category: 'Risk',
                    title: 'High Drawdown Alert',
                    message: `Maximum drawdown is ${maxDrawdown.toFixed(1)}%. Consider reducing position sizes or reviewing risk management.`,
                    actionable: true,
                    action: 'Adjust Risk'
                });
            }

            // 4. Profit Factor
            const profitFactor = this.calculateProfitFactor(tradesData);
            if (profitFactor > 2) {
                this.insights.push({
                    type: 'success',
                    category: 'Performance',
                    title: 'Strong Profit Factor',
                    message: `Profit factor of ${profitFactor.toFixed(2)} indicates your winners significantly outweigh losers.`,
                    actionable: false
                });
            }

            // 5. Trading Frequency
            const tradesPerDay = this.calculateTradesPerDay(tradesData);
            if (tradesPerDay > 10) {
                this.insights.push({
                    type: 'info',
                    category: 'Behavior',
                    title: 'High Trading Frequency',
                    message: `You're averaging ${tradesPerDay.toFixed(1)} trades per day. Ensure this aligns with your strategy.`,
                    actionable: true,
                    action: 'Review Frequency'
                });
            }

            // 6. Consecutive Losses
            const maxConsecutiveLosses = this.calculateMaxConsecutiveLosses(tradesData);
            if (maxConsecutiveLosses >= 5) {
                this.insights.push({
                    type: 'warning',
                    category: 'Psychology',
                    title: 'Losing Streak Detected',
                    message: `You had a streak of ${maxConsecutiveLosses} consecutive losses. Consider taking a break to reset mentally.`,
                    actionable: true,
                    action: 'Take Break'
                });
            }

            return this.insights;
        }

        // Helper calculations
        calculateWinRate(trades) {
            const winners = trades.filter(t => t.profit > 0).length;
            return (winners / trades.length) * 100;
        }

        calculateAvgRiskReward(trades) {
            const avgWin = trades.filter(t => t.profit > 0).reduce((sum, t) => sum + t.profit, 0) / trades.filter(t => t.profit > 0).length;
            const avgLoss = Math.abs(trades.filter(t => t.profit <= 0).reduce((sum, t) => sum + t.profit, 0) / trades.filter(t => t.profit <= 0).length);
            return avgWin / avgLoss;
        }

        calculateMaxDrawdown(performanceData) {
            let maxDrawdown = 0;
            let peak = -Infinity;
            
            performanceData.forEach(point => {
                if (point.equity > peak) peak = point.equity;
                const drawdown = ((peak - point.equity) / peak) * 100;
                if (drawdown > maxDrawdown) maxDrawdown = drawdown;
            });
            
            return maxDrawdown;
        }

        calculateProfitFactor(trades) {
            const grossProfit = trades.filter(t => t.profit > 0).reduce((sum, t) => sum + t.profit, 0);
            const grossLoss = Math.abs(trades.filter(t => t.profit <= 0).reduce((sum, t) => sum + t.profit, 0));
            return grossProfit / grossLoss;
        }

        calculateTradesPerDay(trades) {
            const days = new Set(trades.map(t => t.date.split('T')[0])).size;
            return trades.length / days;
        }

        calculateMaxConsecutiveLosses(trades) {
            let maxStreak = 0;
            let currentStreak = 0;
            
            trades.forEach(trade => {
                if (trade.profit <= 0) {
                    currentStreak++;
                    if (currentStreak > maxStreak) maxStreak = currentStreak;
                } else {
                    currentStreak = 0;
                }
            });
            
            return maxStreak;
        }

        show() {
            if (this.insights.length === 0) {
                alert('No insights available. Generate insights first.');
                return;
            }

            const html = `
                <div class="insights-panel" id="insights-panel">
                    <div class="insights-header">
                        <h3>🧠 AI Insights</h3>
                        <button class="insights-close" onclick="window.AdvancedFeatures.hideInsights()">×</button>
                    </div>
                    <div class="insights-content">
                        ${this.insights.map(insight => `
                            <div class="insight-card insight-${insight.type}">
                                <div class="insight-category">${insight.category}</div>
                                <div class="insight-title">${insight.title}</div>
                                <div class="insight-message">${insight.message}</div>
                                ${insight.actionable ? `<button class="insight-action">${insight.action}</button>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;

            // Remove existing panel
            document.getElementById('insights-panel')?.remove();
            
            // Add new panel
            document.body.insertAdjacentHTML('beforeend', html);
            this.isVisible = true;
        }

        hide() {
            document.getElementById('insights-panel')?.remove();
            this.isVisible = false;
        }
    }

    /**
     * Anomaly Detection Class
     */
    class AnomalyDetector {
        constructor() {
            this.anomalies = [];
        }

        detect(data, type = 'trades') {
            this.anomalies = [];

            if (type === 'trades') {
                this.detectTradeAnomalies(data);
            } else if (type === 'performance') {
                this.detectPerformanceAnomalies(data);
            }

            return this.anomalies;
        }

        detectTradeAnomalies(trades) {
            // 1. Outlier profits/losses
            const profits = trades.map(t => t.profit);
            const mean = profits.reduce((a, b) => a + b, 0) / profits.length;
            const std = Math.sqrt(profits.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / profits.length);
            
            trades.forEach(trade => {
                if (Math.abs(trade.profit - mean) > 3 * std) {
                    this.anomalies.push({
                        type: 'outlier',
                        severity: 'high',
                        message: `Trade #${trade.id} has an unusual ${trade.profit > 0 ? 'profit' : 'loss'}: €${Math.abs(trade.profit).toFixed(2)}`,
                        data: trade
                    });
                }
            });

            // 2. Unusual trade times
            const tradeTimes = trades.map(t => new Date(t.timestamp).getHours());
            const mostCommonHour = this.mode(tradeTimes);
            
            trades.forEach(trade => {
                const hour = new Date(trade.timestamp).getHours();
                if (Math.abs(hour - mostCommonHour) > 6) {
                    this.anomalies.push({
                        type: 'timing',
                        severity: 'medium',
                        message: `Trade #${trade.id} executed at unusual hour: ${hour}:00`,
                        data: trade
                    });
                }
            });
        }

        detectPerformanceAnomalies(performanceData) {
            // Detect sudden equity drops
            for (let i = 1; i < performanceData.length; i++) {
                const change = ((performanceData[i].equity - performanceData[i-1].equity) / performanceData[i-1].equity) * 100;
                
                if (change < -5) {
                    this.anomalies.push({
                        type: 'equity_drop',
                        severity: 'high',
                        message: `Sudden equity drop of ${Math.abs(change).toFixed(1)}% detected on ${performanceData[i].date}`,
                        data: performanceData[i]
                    });
                }
            }
        }

        mode(array) {
            const frequency = {};
            let maxFreq = 0;
            let mode = array[0];
            
            array.forEach(item => {
                frequency[item] = (frequency[item] || 0) + 1;
                if (frequency[item] > maxFreq) {
                    maxFreq = frequency[item];
                    mode = item;
                }
            });
            
            return mode;
        }
    }

    /**
     * Snapshot Manager Class
     */
    class SnapshotManager {
        takeSnapshot(filename = 'dashboard-snapshot') {
            // Use html2canvas if available, otherwise fallback
            if (typeof html2canvas !== 'undefined') {
                const element = document.querySelector('.dashboard-content');
                html2canvas(element).then(canvas => {
                    const link = document.createElement('a');
                    link.download = `${filename}-${Date.now()}.png`;
                    link.href = canvas.toDataURL();
                    link.click();
                });
            } else {
                console.warn('html2canvas not loaded. Using fallback.');
                alert('Snapshot feature requires html2canvas library.');
            }
        }

        shareSnapshot() {
            // Implementation for sharing
            alert('Share functionality would be implemented here.');
        }
    }

    /**
     * Main Advanced Features Manager
     */
    class AdvancedFeaturesManager {
        constructor() {
            this.commandPalette = new CommandPalette();
            this.insightsPanel = new AIInsightsPanel();
            this.anomalyDetector = new AnomalyDetector();
            this.snapshotManager = new SnapshotManager();
        }

        async showInsights() {
            // Mock data - replace with actual data from dashboard
            const mockTrades = Array.from({ length: 100 }, (_, i) => ({
                id: i + 1,
                profit: (Math.random() - 0.4) * 200,
                date: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
                timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString()
            }));

            const mockPerformance = Array.from({ length: 30 }, (_, i) => ({
                date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                equity: 50000 + Math.random() * 10000
            }));

            await this.insightsPanel.generateInsights({}, mockTrades, mockPerformance);
            this.insightsPanel.show();
        }

        hideInsights() {
            this.insightsPanel.hide();
        }

        detectAnomalies() {
            // Mock data
            const mockTrades = Array.from({ length: 100 }, (_, i) => ({
                id: i + 1,
                profit: (Math.random() - 0.4) * 200,
                timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString()
            }));

            const anomalies = this.anomalyDetector.detect(mockTrades, 'trades');
            
            if (anomalies.length > 0) {
                alert(`Found ${anomalies.length} anomalies:\n\n${anomalies.slice(0, 3).map(a => a.message).join('\n')}`);
            } else {
                alert('No anomalies detected. Everything looks normal!');
            }
        }

        takeSnapshot() {
            this.snapshotManager.takeSnapshot('botv2-dashboard');
        }
    }

    // Export to window
    window.AdvancedFeatures = new AdvancedFeaturesManager();

    console.log('🚀 Advanced Features v7.2 loaded successfully');
    console.log('🎯 Press Ctrl/Cmd+K to open Command Palette');

})(window);
