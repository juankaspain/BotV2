// ==================== BOTV2 ADVANCED FEATURES v7.2.1 ====================
// 🚀 Command Palette & AI Insights System
// Author: Juan Carlos Garcia
// Date: 25 Enero 2026
// Version: 7.2.1 - Fixed InsightsPanel toggle
//
// Features:
// - Command Palette (Ctrl+K / Cmd+K)
// - Fuzzy Search Algorithm
// - Keyboard Navigation (Arrow Keys, Enter, Esc)
// - AI-powered Insights Panel with toggle() method
// - Real-time Suggestions
// - Context-aware Actions
// - Keyboard shortcut Ctrl+/ for Insights

console.log('🚀 Advanced Features v7.2.1 initializing...');

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
            {
                id: 'action-insights',
                title: 'Toggle AI Insights',
                description: 'Show/hide insights panel',
                icon: '💡',
                category: 'Actions',
                keywords: ['ai', 'smart', 'recommendations'],
                keys: ['Ctrl', '/'],
                action: () => { if (typeof InsightsPanel !== 'undefined' && InsightsPanel.toggle) InsightsPanel.toggle(); }
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
        console.log(`🧭 Navigating to: ${section}`);
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
Ctrl + / - Toggle Insights Panel
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
const InsightsPanel = (() => {
    let isVisible = false;
    let isInitialized = false;
    let panelElement = null;
    let insights = [];
    let isLoading = false;
    
    function init() {
        if (isInitialized) return;
        
        createPanel();
        bindKeyboardShortcut();
        isInitialized = true;
        
        console.log('✅ Insights Panel initialized');
    }
    
    function createPanel() {
        panelElement = document.createElement('div');
        panelElement.id = 'insights-panel';
        panelElement.className = 'insights-panel-overlay';
        panelElement.style.cssText = `
            position: fixed;
            top: 0;
            right: -400px;
            width: 400px;
            height: 100vh;
            background: var(--bg-secondary);
            border-left: 1px solid var(--border-default);
            box-shadow: -8px 0 24px rgba(0,0,0,0.3);
            z-index: 9998;
            transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
        `;
        
        panelElement.innerHTML = `
            <div class="insights-header" style="padding: 20px; border-bottom: 1px solid var(--border-default); display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20" style="color: var(--accent-primary)">
                        <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z"/>
                    </svg>
                    <div>
                        <div style="font-size: 16px; font-weight: 600; color: var(--text-primary);">AI Insights</div>
                        <div style="font-size: 11px; color: var(--text-muted);">Smart recommendations</div>
                    </div>
                </div>
                <button onclick="InsightsPanel.close()" style="background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 20px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 4px; transition: all 0.2s;" onmouseover="this.style.background='var(--bg-hover)';this.style.color='var(--text-primary)'" onmouseout="this.style.background='none';this.style.color='var(--text-muted)'">×</button>
            </div>
            <div id="insights-content" style="flex: 1; overflow-y: auto; padding: 20px;">
                <!-- Insights will be loaded here -->
            </div>
        `;
        
        document.body.appendChild(panelElement);
    }
    
    function bindKeyboardShortcut() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === '/') {
                e.preventDefault();
                toggle();
            }
        });
    }
    
    function toggle() {
        if (isVisible) {
            close();
        } else {
            open();
        }
    }
    
    function open() {
        if (!isInitialized) init();
        
        isVisible = true;
        panelElement.style.right = '0';
        
        if (insights.length === 0) {
            loadInsights();
        }
    }
    
    function close() {
        isVisible = false;
        panelElement.style.right = '-400px';
    }
    
    async function loadInsights() {
        isLoading = true;
        showLoading();
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Generate mock insights
        insights = generateMockInsights();
        
        isLoading = false;
        renderInsights();
    }
    
    function generateMockInsights() {
        return [
            {
                id: 'insight-1',
                type: 'Performance',
                title: 'Strong Momentum Detected',
                description: 'Portfolio up 8.5% in last 7 days. Current trend suggests continued growth potential.',
                icon: '📈',
                severity: 'success',
                confidence: 92,
                time: '2 min ago'
            },
            {
                id: 'insight-2',
                type: 'Risk Alert',
                title: 'Elevated Drawdown Risk',
                description: 'Current drawdown at -5.2%. Consider reducing position sizes or adjusting stop-loss levels.',
                icon: '⚠️',
                severity: 'warning',
                confidence: 87,
                time: '15 min ago'
            },
            {
                id: 'insight-3',
                type: 'Opportunity',
                title: 'Unused Capital Available',
                description: '€10,500 available for deployment. Market conditions favorable for additional positions.',
                icon: '💰',
                severity: 'info',
                confidence: 78,
                time: '1 hour ago'
            }
        ];
    }
    
    function showLoading() {
        const content = document.getElementById('insights-content');
        if (!content) return;
        
        content.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 16px;">
                <div style="width: 40px; height: 40px; border: 3px solid var(--border-default); border-top-color: var(--accent-primary); border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                <div style="color: var(--text-secondary); font-size: 14px;">Analyzing data...</div>
            </div>
        `;
    }
    
    function renderInsights() {
        const content = document.getElementById('insights-content');
        if (!content) return;
        
        if (insights.length === 0) {
            content.innerHTML = `
                <div style="text-align: center; padding: 60px 20px;">
                    <div style="font-size: 48px; margin-bottom: 16px;">🧐</div>
                    <div style="font-size: 18px; font-weight: 600; color: var(--text-primary); margin-bottom: 8px;">No Insights Available</div>
                    <div style="font-size: 14px; color: var(--text-secondary); line-height: 1.6;">
                        We're analyzing your portfolio. Check back soon for personalized recommendations.
                    </div>
                </div>
            `;
            return;
        }
        
        let html = '';
        
        insights.forEach(insight => {
            const colors = {
                success: { bg: 'rgba(63, 185, 80, 0.1)', border: 'var(--accent-success)', icon: 'var(--accent-success)' },
                warning: { bg: 'rgba(210, 153, 34, 0.1)', border: 'var(--accent-warning)', icon: 'var(--accent-warning)' },
                info: { bg: 'rgba(47, 129, 247, 0.1)', border: 'var(--accent-primary)', icon: 'var(--accent-primary)' },
                danger: { bg: 'rgba(248, 81, 73, 0.1)', border: 'var(--accent-danger)', icon: 'var(--accent-danger)' }
            };
            
            const style = colors[insight.severity] || colors.info;
            
            html += `
                <div style="background: ${style.bg}; border-left: 3px solid ${style.border}; border-radius: 8px; padding: 16px; margin-bottom: 16px; animation: fadeIn 0.3s ease-out;">
                    <div style="display: flex; align-items: start; gap: 12px; margin-bottom: 12px;">
                        <div style="font-size: 24px; color: ${style.icon};">${insight.icon}</div>
                        <div style="flex: 1;">
                            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 4px;">${insight.type}</div>
                            <div style="font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px;">${insight.title}</div>
                            <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">${insight.description}</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; font-size: 11px; color: var(--text-muted);">
                        <div style="display: flex; align-items: center; gap: 4px;">
                            <svg width="12" height="12" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                            </svg>
                            ${insight.time}
                        </div>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span>Confidence:</span>
                            <span style="font-weight: 600; color: var(--text-primary);">${insight.confidence}%</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        content.innerHTML = html;
    }
    
    function refresh() {
        loadInsights();
    }
    
    // Public API
    return {
        init,
        toggle,
        open,
        close,
        refresh,
        isVisible: () => isVisible
    };
})();

// ==================== INITIALIZATION ====================
const commandPalette = new CommandPalette();

// Initialize Insights Panel
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        InsightsPanel.init();
    });
} else {
    InsightsPanel.init();
}

// Global exports
window.CommandPalette = commandPalette;
window.InsightsPanel = InsightsPanel;
window.AdvancedFeatures = {
    commandPalette,
    insightsPanel: InsightsPanel,
    openCommandPalette: () => commandPalette.open(),
    toggleInsights: () => InsightsPanel.toggle()
};

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);

console.log('✅ Advanced Features v7.2.1 loaded and active');
console.log('💡 Press Ctrl/Cmd + K to open Command Palette');
console.log('💡 Press Ctrl + / to toggle Insights Panel');
