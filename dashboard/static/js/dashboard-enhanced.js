/**
 * Dashboard Enhanced - V10.0 Visual Excellence
 * 
 * Features:
 * - Real-time statistics updates
 * - Interactive Chart.js charts
 * - Dark/Light theme toggle with persistence
 * - Mobile responsive animations
 * - WebSocket support for live data
 * - Smooth transitions and modern UI
 */

// ==========================
// Theme Management
// ==========================
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('dashboard-theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme(this.theme);
        this.setupToggle();
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.theme = theme;
        localStorage.setItem('dashboard-theme', theme);
        
        // Update toggle button icon
        const toggleBtn = document.querySelector('.theme-toggle');
        if (toggleBtn) {
            toggleBtn.innerHTML = theme === 'dark' ? '🌙' : '☀️';
        }
    }

    toggle() {
        const newTheme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    setupToggle() {
        const toggleBtn = document.querySelector('.theme-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }
    }
}

// ==========================
// Real-time Stats Manager
// ==========================
class StatsManager {
    constructor() {
        this.ws = null;
        this.updateInterval = null;
        this.stats = {};
    }

    init() {
        this.setupWebSocket();
        this.startPolling();
    }

    setupWebSocket() {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/stats`;

        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.updateStats(data);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                // Fallback to polling if WebSocket fails
                this.startPolling();
            };

            this.ws.onclose = () => {
                console.log('WebSocket closed, attempting reconnect...');
                setTimeout(() => this.setupWebSocket(), 5000);
            };
        } catch (error) {
            console.error('WebSocket not available, using polling');
            this.startPolling();
        }
    }

    startPolling() {
        if (this.updateInterval) return;
        
        this.updateInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                this.updateStats(data);
            } catch (error) {
                console.error('Failed to fetch stats:', error);
            }
        }, 5000); // Update every 5 seconds
    }

    updateStats(data) {
        this.stats = data;
        this.renderStats(data);
    }

    renderStats(data) {
        // Update stat cards with animation
        Object.keys(data).forEach(key => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element) {
                const oldValue = element.textContent;
                const newValue = data[key];
                
                if (oldValue !== newValue.toString()) {
                    element.classList.add('stat-updating');
                    element.textContent = newValue;
                    setTimeout(() => element.classList.remove('stat-updating'), 500);
                }
            }
        });
    }

    stop() {
        if (this.ws) {
            this.ws.close();
        }
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// ==========================
// Chart Manager
// ==========================
class ChartManager {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: '#4f46e5',
            success: '#10b981',
            warning: '#f59e0b',
            danger: '#ef4444',
            info: '#3b82f6'
        };
    }

    init() {
        this.createActivityChart();
        this.createPerformanceChart();
        this.createDistributionChart();
    }

    createActivityChart() {
        const ctx = document.getElementById('activityChart');
        if (!ctx) return;

        this.charts.activity = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Activity',
                    data: [],
                    borderColor: this.colors.primary,
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    createPerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;

        this.charts.performance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Performance',
                    data: [65, 59, 80, 81, 56, 55, 70],
                    backgroundColor: this.colors.success,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    createDistributionChart() {
        const ctx = document.getElementById('distributionChart');
        if (!ctx) return;

        this.charts.distribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Active', 'Pending', 'Completed', 'Failed'],
                datasets: [{
                    data: [300, 50, 100, 25],
                    backgroundColor: [
                        this.colors.success,
                        this.colors.warning,
                        this.colors.info,
                        this.colors.danger
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            usePointStyle: true
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    updateChart(chartName, newData) {
        const chart = this.charts[chartName];
        if (!chart) return;

        chart.data.datasets[0].data = newData;
        chart.update('smooth');
    }
}

// ==========================
// Mobile Responsive Handler
// ==========================
class MobileHandler {
    constructor() {
        this.breakpoint = 768;
        this.init();
    }

    init() {
        this.setupSidebar();
        this.setupTouchGestures();
        this.handleResize();
        window.addEventListener('resize', () => this.handleResize());
    }

    setupSidebar() {
        const toggle = document.querySelector('.sidebar-toggle');
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');

        if (toggle && sidebar) {
            toggle.addEventListener('click', () => {
                sidebar.classList.toggle('active');
                if (overlay) overlay.classList.toggle('active');
            });
        }

        if (overlay) {
            overlay.addEventListener('click', () => {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            });
        }
    }

    setupTouchGestures() {
        let startX = 0;
        let startY = 0;

        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            
            const diffX = endX - startX;
            const diffY = endY - startY;

            // Swipe right to open sidebar
            if (Math.abs(diffX) > Math.abs(diffY) && diffX > 50 && startX < 50) {
                const sidebar = document.querySelector('.sidebar');
                if (sidebar) sidebar.classList.add('active');
            }
        });
    }

    handleResize() {
        const isMobile = window.innerWidth < this.breakpoint;
        document.body.classList.toggle('mobile', isMobile);
        document.body.classList.toggle('desktop', !isMobile);
    }
}

// ==========================
// Animation Controller
// ==========================
class AnimationController {
    constructor() {
        this.observer = null;
        this.init();
    }

    init() {
        this.setupScrollAnimations();
        this.setupHoverEffects();
    }

    setupScrollAnimations() {
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, {
            threshold: 0.1
        });

        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            this.observer.observe(el);
        });
    }

    setupHoverEffects() {
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('mouseenter', (e) => {
                e.currentTarget.classList.add('hovered');
            });

            card.addEventListener('mouseleave', (e) => {
                e.currentTarget.classList.remove('hovered');
            });
        });
    }
}

// ==========================
// Dashboard Controller
// ==========================
class DashboardController {
    constructor() {
        this.themeManager = new ThemeManager();
        this.statsManager = new StatsManager();
        this.chartManager = new ChartManager();
        this.mobileHandler = new MobileHandler();
        this.animationController = new AnimationController();
    }

    init() {
        console.log('Dashboard Enhanced V10.0 Initialized');
        this.statsManager.init();
        
        // Initialize Chart.js if available
        if (typeof Chart !== 'undefined') {
            this.chartManager.init();
        } else {
            console.warn('Chart.js not loaded');
        }
    }

    destroy() {
        this.statsManager.stop();
        if (this.animationController.observer) {
            this.animationController.observer.disconnect();
        }
    }
}

// ==========================
// Initialize on DOM Ready
// ==========================
let dashboard = null;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        dashboard = new DashboardController();
        dashboard.init();
    });
} else {
    dashboard = new DashboardController();
    dashboard.init();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DashboardController, ThemeManager, StatsManager, ChartManager };
}
