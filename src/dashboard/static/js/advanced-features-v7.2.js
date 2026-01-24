// ==================== BOTV2 ADVANCED FEATURES v7.2 ====================
// 🚀 Command Palette & AI Insights System
// Author: Juan Carlos Garcia
// Date: 24 Enero 2026
//
// Features:
// - Command Palette (Ctrl+K / Cmd+K)
// - Fuzzy Search Algorithm
// - Keyboard Navigation (Arrow Keys, Enter, Esc)
// - AI-powered Insights Panel
// - Real-time Suggestions
// - Context-aware Actions

console.log('🚀 Advanced Features v7.2 initializing...');

// ==================== COMMAND PALETTE ====================
class CommandPalette {
    constructor() {
        this.isOpen = false;
        this.selectedIndex = 0;
        this.commands = [];
        this.filteredCommands = [];
        this.searchQuery = '';
        
        this.init();
    }
    
    init() {
        this.createOverlay();
        this.loadCommands();
        this.bindEvents();
        
        console.log('✅ Command Palette initialized');
    }
    
    createOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'command-palette-overlay';
        overlay.id = 'command-palette-overlay';
        
        overlay.innerHTML = `
            <div class="command-palette">
                <div class="command-palette-search">
                    <svg class="command-palette-search-icon" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/>
                    </svg>
                    <input 
                        type="text" 
                        class="command-palette-input" 
                        placeholder="Type a command or search..."
                        id="command-palette-input"
                        autocomplete="off"
                        spellcheck="false"
                    >
                    <div class="command-palette-shortcut">ESC</div>
                </div>
                <div class="command-palette-results" id="command-palette-results">
                    <!-- Results will be inserted here -->
                </div>
                <div class="command-palette-footer">
                    <div class="command-palette-footer-hints">
                        <div class="command-palette-footer-hint">
                            <span class="kbd">↑</span>
                            <span class="kbd">↓</span>
                            <span>Navigate</span>
                        </div>
                        <div class="command-palette-footer-hint">
                            <span class="kbd">Enter</span>
                            <span>Select</span>
                        </div>
                        <div class="command-palette-footer-hint">
                            <span class="kbd">Esc</span>
                            <span>Close</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        this.overlay = overlay;
        this.input = document.getElementById('command-palette-input');
        this.results = document.getElementById('command-palette-results');
    }
    
    loadCommands() {
        this.commands = [
            // Navigation
            {
                id: 'nav-dashboard',
                title: 'Go to Dashboard',
                description: 'View main dashboard overview',
                icon: '📊',
                category: 'Navigation',
                keywords: ['home', 'main', 'overview'],
                action: () => this.navigate('dashboard')
            },
            {
                id: 'nav-portfolio',
                title: 'Go to Portfolio',
                description: 'View portfolio allocation and performance',
                icon: '💼',
                category: 'Navigation',
                keywords: ['assets', 'holdings', 'positions'],
                action: () => this.navigate('portfolio')
            },
            {
                id: 'nav-trades',
                title: 'Go to Trades',
                description: 'View trade history and execution logs',
                icon: '📝',
                category: 'Navigation',
                keywords: ['orders', 'executions', 'history'],
                action: () => this.navigate('trades')
            },
            {
                id: 'nav-performance',
                title: 'Go to Performance',
                description: 'Analyze strategy performance metrics',
                icon: '📈',
                category: 'Navigation',
                keywords: ['metrics', 'stats', 'analytics'],
                action: () => this.navigate('performance')
            },
            {
                id: 'nav-risk',
                title: 'Go to Risk Analysis',
                description: 'View risk metrics and exposure',
                icon: '⚠️',
                category: 'Navigation',
                keywords: ['exposure', 'var', 'drawdown'],
                action: () => this.navigate('risk')
            },
            {
                id: 'nav-markets',
                title: 'Go to Market Overview',
                description: 'View market conditions and sentiment',
                icon: '🌐',
                category: 'Navigation',
                keywords: ['indices', 'sentiment', 'volatility'],
                action: () => this.navigate('markets')
            },
            {
                id: 'nav-strategies',
                title: 'Go to Strategies',
                description: 'Manage trading strategies',
                icon: '⚙️',
                category: 'Navigation',
                keywords: ['algorithms', 'bots', 'config'],
                action: () => this.navigate('strategies')
            },
            {
                id: 'nav-backtesting',
                title: 'Go to Backtesting',
                description: 'Run strategy backtests',
                icon: '⏱️',
                category: 'Navigation',
                keywords: ['historical', 'simulation', 'test'],
                action: () => this.navigate('backtesting')
            },
            
            // Actions
            {
                id: 'action-start-bot',
                title: 'Start Trading Bot',
                description: 'Activate automated trading',
                icon: '▶️',
                category: 'Actions',
                keywords: ['run', 'activate', 'enable'],
                badge: 'Pro',
                action: () => this.executeAction('start-bot')
            },
            {
                id: 'action-stop-bot',
                title: 'Stop Trading Bot',
                description: 'Pause automated trading',
                icon: '⏸️',
                category: 'Actions',
                keywords: ['pause', 'disable', 'halt'],
                badge: 'Pro',
                action: () => this.executeAction('stop-bot')
            },
            {
                id: 'action-refresh',
                title: 'Refresh Data',
                description: 'Reload current view',
                icon: '🔄',
                category: 'Actions',
                keywords: ['reload', 'update', 'sync'],
                keys: ['Ctrl', 'R'],
                action: () => this.executeAction('refresh')
            },
            {
                id: 'action-export',
                title: 'Export Data',
                description: 'Download data as CSV/JSON',
                icon: '📥',
                category: 'Actions',
                keywords: ['download', 'save', 'backup'],
                action: () => this.executeAction('export')
            },
            
            // Settings
            {
                id: 'theme-dark',
                title: 'Switch to Dark Theme',
                description: 'Enable dark mode',
                icon: '🌙',
                category: 'Settings',
                keywords: ['dark', 'night', 'black'],
                action: () => setTheme('dark')
            },
            {
                id: 'theme-light',
                title: 'Switch to Light Theme',
                description: 'Enable light mode',
                icon: '☀️',
                category: 'Settings',
                keywords: ['light', 'day', 'white'],
                action: () => setTheme('light')
            },
            {
                id: 'theme-bloomberg',
                title: 'Switch to Bloomberg Terminal',
                description: 'Enable terminal theme',
                icon: '💻',
                category: 'Settings',
                keywords: ['terminal', 'bloomberg', 'professional'],
                action: () => setTheme('bloomberg')
            },
            
            // Help
            {
                id: 'help-shortcuts',
                title: 'View Keyboard Shortcuts',
                description: 'See all available shortcuts',
                icon: '⌨️',
                category: 'Help',
                keywords: ['keys', 'commands', 'hotkeys'],
                action: () => this.showShortcuts()
            },
            {
                id: 'help-docs',
                title: 'Open Documentation',
                description: 'View user guide and API docs',
                icon: '📖',
                category: 'Help',
                keywords: ['manual', 'guide', 'reference'],
                action: () => this.openDocs()
            }
        ];
        
        this.filteredCommands = [...this.commands];
    }
    
    bindEvents() {
        // Global keyboard shortcut (Ctrl+K or Cmd+K)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.toggle();
            }
        });
        
        // Close on overlay click
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.close();
            }
        });
        
        // Search input
        this.input.addEventListener('input', (e) => {
            this.searchQuery = e.target.value;
            this.search();
        });
        
        // Keyboard navigation
        this.input.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    this.selectNext();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    this.selectPrevious();
                    break;
                case 'Enter':
                    e.preventDefault();
                    this.executeSelected();
                    break;
                case 'Escape':
                    e.preventDefault();
                    this.close();
                    break;
            }
        });
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        this.isOpen = true;
        this.overlay.classList.add('active');
        this.input.value = '';
        this.searchQuery = '';
        this.selectedIndex = 0;
        this.filteredCommands = [...this.commands];
        this.render();
        
        // Focus input after animation
        setTimeout(() => {
            this.input.focus();
        }, 100);
    }
    
    close() {
        this.isOpen = false;
        this.overlay.classList.remove('active');
    }
    
    search() {
        if (!this.searchQuery.trim()) {
            this.filteredCommands = [...this.commands];
        } else {
            this.filteredCommands = this.fuzzySearch(this.searchQuery);
        }
        
        this.selectedIndex = 0;
        this.render();
    }
    
    fuzzySearch(query) {
        const lowerQuery = query.toLowerCase();
        
        return this.commands
            .map(cmd => {
                // Calculate match score
                let score = 0;
                const title = cmd.title.toLowerCase();
                const description = cmd.description.toLowerCase();
                const keywords = cmd.keywords.join(' ').toLowerCase();
                
                // Exact title match: highest score
                if (title.includes(lowerQuery)) {
                    score += 100;
                }
                
                // Exact keyword match
                if (keywords.includes(lowerQuery)) {
                    score += 50;
                }
                
                // Description match
                if (description.includes(lowerQuery)) {
                    score += 25;
                }
                
                // Fuzzy match in title
                if (this.fuzzyMatch(title, lowerQuery)) {
                    score += 10;
                }
                
                return { ...cmd, score };
            })
            .filter(cmd => cmd.score > 0)
            .sort((a, b) => b.score - a.score);
    }
    
    fuzzyMatch(str, pattern) {
        let patternIdx = 0;
        let strIdx = 0;
        
        while (strIdx < str.length && patternIdx < pattern.length) {
            if (str[strIdx] === pattern[patternIdx]) {
                patternIdx++;
            }
            strIdx++;
        }
        
        return patternIdx === pattern.length;
    }
    
    highlightMatch(text, query) {
        if (!query) return text;
        
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    render() {
        if (this.filteredCommands.length === 0) {
            this.results.innerHTML = `
                <div class="command-palette-empty">
                    <div class="command-palette-empty-icon">🔍</div>
                    <div class="command-palette-empty-text">No commands found</div>
                </div>
            `;
            return;
        }
        
        // Group by category
        const grouped = {};
        this.filteredCommands.forEach(cmd => {
            if (!grouped[cmd.category]) {
                grouped[cmd.category] = [];
            }
            grouped[cmd.category].push(cmd);
        });
        
        let html = '';
        let globalIndex = 0;
        
        Object.keys(grouped).forEach(category => {
            html += `
                <div class="command-palette-section">
                    <div class="command-palette-section-title">${category}</div>
            `;
            
            grouped[category].forEach(cmd => {
                const isSelected = globalIndex === this.selectedIndex;
                const highlightedTitle = this.highlightMatch(cmd.title, this.searchQuery);
                
                html += `
                    <div class="command-palette-item ${isSelected ? 'selected' : ''}" data-index="${globalIndex}">
                        <div class="command-palette-item-icon">${cmd.icon}</div>
                        <div class="command-palette-item-content">
                            <div class="command-palette-item-title">
                                ${highlightedTitle}
                                ${cmd.badge ? `<span class="command-palette-item-badge">${cmd.badge}</span>` : ''}
                            </div>
                            <div class="command-palette-item-description">${cmd.description}</div>
                        </div>
                        ${cmd.keys ? `
                            <div class="command-palette-item-keys">
                                ${cmd.keys.map(k => `<span class="command-palette-key">${k}</span>`).join('')}
                            </div>
                        ` : ''}
                    </div>
                `;
                
                globalIndex++;
            });
            
            html += `</div>`;
        });
        
        this.results.innerHTML = html;
        
        // Bind click events
        this.results.querySelectorAll('.command-palette-item').forEach((item, index) => {
            item.addEventListener('click', () => {
                this.selectedIndex = parseInt(item.dataset.index);
                this.executeSelected();
            });
            
            item.addEventListener('mouseenter', () => {
                this.selectedIndex = parseInt(item.dataset.index);
                this.updateSelection();
            });
        });
        
        // Scroll selected into view
        this.scrollSelectedIntoView();
    }
    
    updateSelection() {
        this.results.querySelectorAll('.command-palette-item').forEach((item, index) => {
            const itemIndex = parseInt(item.dataset.index);
            if (itemIndex === this.selectedIndex) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
        
        this.scrollSelectedIntoView();
    }
    
    scrollSelectedIntoView() {
        const selected = this.results.querySelector('.command-palette-item.selected');
        if (selected) {
            selected.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }
    
    selectNext() {
        if (this.selectedIndex < this.filteredCommands.length - 1) {
            this.selectedIndex++;
            this.updateSelection();
        }
    }
    
    selectPrevious() {
        if (this.selectedIndex > 0) {
            this.selectedIndex--;
            this.updateSelection();
        }
    }
    
    executeSelected() {
        const cmd = this.filteredCommands[this.selectedIndex];
        if (cmd && cmd.action) {
            cmd.action();
            this.close();
        }
    }
    
    // Command actions
    navigate(section) {
        console.log(`🧭Navigating to: ${section}`);
        if (typeof loadSection === 'function') {
            loadSection(section);
        }
    }
    
    executeAction(action) {
        console.log(`⚡ Executing action: ${action}`);
        
        switch (action) {
            case 'start-bot':
                alert('🤖 Bot started! (Demo action)');
                break;
            case 'stop-bot':
                alert('⏸️ Bot stopped! (Demo action)');
                break;
            case 'refresh':
                location.reload();
                break;
            case 'export':
                alert('📥 Export feature coming soon!');
                break;
        }
    }
    
    showShortcuts() {
        alert(`
⌨️ Keyboard Shortcuts:

Ctrl/Cmd + K - Command Palette
Ctrl + R - Refresh
Esc - Close overlays
↑ ↓ - Navigate
Enter - Select
        `.trim());
    }
    
    openDocs() {
        window.open('https://github.com/juankaspain/BotV2/blob/main/README.md', '_blank');
    }
}

// ==================== AI INSIGHTS PANEL ====================
class InsightsPanel {
    constructor() {
        this.insights = [];
        this.isLoading = false;
        this.container = null;
        
        console.log('✅ Insights Panel initialized');
    }
    
    render(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.warn(`Container ${containerId} not found`);
            return;
        }
        
        const html = `
            <div class="insights-panel">
                <div class="insights-header">
                    <div class="insights-header-left">
                        <svg class="insights-icon" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z"/>
                        </svg>
                        <div class="insights-title">
                            Smart Insights
                            <span class="insights-badge" id="insights-count">0</span>
                        </div>
                    </div>
                    <div class="insights-actions">
                        <button class="insights-action-btn" onclick="window.AdvancedFeatures.refreshInsights()">
                            🔄 Refresh
                        </button>
                    </div>
                </div>
                <div class="insights-list" id="insights-list">
                    <!-- Insights will be inserted here -->
                </div>
            </div>
        `;
        
        this.container.innerHTML = html;
        this.listContainer = document.getElementById('insights-list');
        
        // Load initial insights
        this.loadInsights();
    }
    
    async loadInsights() {
        this.isLoading = true;
        this.showLoading();
        
        // Simulate API call
        await this.wait(1500);
        
        // Generate mock insights
        this.insights = this.generateMockInsights();
        
        this.isLoading = false;
        this.renderInsights();
    }
    
    generateMockInsights() {
        const insights = [];
        
        // Performance insights
        insights.push({
            id: 'insight-1',
            type: 'Performance',
            title: 'Strong Momentum Detected',
            description: 'Portfolio up 8.5% in last 7 days. Current trend suggests continued growth potential.',
            icon: '📈',
            severity: 'success',
            confidence: 92,
            time: '2 min ago',
            actions: [
                { label: 'View Details', icon: '🔍', action: 'view-performance' },
                { label: 'Share', icon: '📤', action: 'share' }
            ]
        });
        
        // Risk warning
        insights.push({
            id: 'insight-2',
            type: 'Risk Alert',
            title: 'Elevated Drawdown Risk',
            description: 'Current drawdown at -5.2%. Consider reducing position sizes or adjusting stop-loss levels.',
            icon: '⚠️',
            severity: 'warning',
            confidence: 87,
            time: '15 min ago',
            actions: [
                { label: 'View Risk', icon: '🔒', action: 'view-risk' },
                { label: 'Adjust', icon: '⚙️', action: 'adjust-risk' }
            ]
        });
        
        // Opportunity
        insights.push({
            id: 'insight-3',
            type: 'Opportunity',
            title: 'Unused Capital Available',
            description: '€10,500 available for deployment. Market conditions favorable for additional positions.',
            icon: '💰',
            severity: 'info',
            confidence: 78,
            time: '1 hour ago',
            actions: [
                { label: 'View Markets', icon: '🌐', action: 'view-markets' },
                { label: 'Deploy', icon: '🚀', action: 'deploy-capital' }
            ]
        });
        
        return insights;
    }
    
    showLoading() {
        this.listContainer.innerHTML = `
            <div class="insights-loading">
                <div class="insights-loading-spinner"></div>
                <div class="insights-loading-text">Analyzing data...</div>
            </div>
        `;
    }
    
    renderInsights() {
        if (this.insights.length === 0) {
            this.listContainer.innerHTML = `
                <div class="insights-empty">
                    <div class="insights-empty-icon">🧐</div>
                    <div class="insights-empty-title">No Insights Available</div>
                    <div class="insights-empty-description">
                        We're analyzing your portfolio. Check back soon for personalized recommendations.
                    </div>
                </div>
            `;
            return;
        }
        
        // Update count badge
        const countBadge = document.getElementById('insights-count');
        if (countBadge) {
            countBadge.textContent = this.insights.length;
        }
        
        let html = '';
        
        this.insights.forEach(insight => {
            const confidenceLevel = insight.confidence >= 85 ? 'high' : 
                                   insight.confidence >= 70 ? 'medium' : 'low';
            
            html += `
                <div class="insight-item insight-${insight.severity}">
                    <div class="insight-icon-container ${insight.severity}">
                        <span style="font-size: 20px;">${insight.icon}</span>
                    </div>
                    <div class="insight-content">
                        <div class="insight-type">${insight.type}</div>
                        <div class="insight-title">${insight.title}</div>
                        <div class="insight-description">${insight.description}</div>
                        <div class="insight-meta">
                            <div class="insight-time">
                                <svg width="14" height="14" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                                </svg>
                                ${insight.time}
                            </div>
                            <div class="insight-confidence">
                                <span>Confidence</span>
                                <div class="insight-confidence-bar">
                                    <div class="insight-confidence-fill ${confidenceLevel}" style="width: ${insight.confidence}%"></div>
                                </div>
                                <span>${insight.confidence}%</span>
                            </div>
                        </div>
                        ${insight.actions && insight.actions.length > 0 ? `
                            <div class="insight-actions">
                                ${insight.actions.map(action => `
                                    <button class="insight-action" onclick="window.AdvancedFeatures.executeInsightAction('${action.action}')">
                                        <span>${action.icon}</span>
                                        <span>${action.label}</span>
                                    </button>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        });
        
        this.listContainer.innerHTML = html;
    }
    
    executeAction(action) {
        console.log(`⚡ Executing insight action: ${action}`);
        
        switch (action) {
            case 'view-performance':
                if (typeof loadSection === 'function') loadSection('performance');
                break;
            case 'view-risk':
                if (typeof loadSection === 'function') loadSection('risk');
                break;
            case 'view-markets':
                if (typeof loadSection === 'function') loadSection('markets');
                break;
            case 'share':
                alert('📤 Share feature coming soon!');
                break;
            case 'adjust-risk':
                alert('⚙️ Risk adjustment panel coming soon!');
                break;
            case 'deploy-capital':
                alert('🚀 Capital deployment wizard coming soon!');
                break;
        }
    }
    
    refresh() {
        this.loadInsights();
    }
    
    wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// ==================== INITIALIZATION ====================
const commandPalette = new CommandPalette();
const insightsPanel = new InsightsPanel();

// Global exports
window.AdvancedFeatures = {
    commandPalette,
    insightsPanel,
    openCommandPalette: () => commandPalette.open(),
    refreshInsights: () => insightsPanel.refresh(),
    executeInsightAction: (action) => insightsPanel.executeAction(action)
};

// Auto-initialize insights panel if container exists
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const container = document.getElementById('insights-container');
        if (container) {
            insightsPanel.render('insights-container');
        }
    });
} else {
    const container = document.getElementById('insights-container');
    if (container) {
        insightsPanel.render('insights-container');
    }
}

console.log('✅ Advanced Features v7.2 loaded and active');
console.log('💡 Press Ctrl/Cmd + K to open Command Palette');
