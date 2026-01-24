// ==================== BotV2 Dashboard Visual Excellence v7.0 ====================
// Iteration 1: Ultra Professional JavaScript Enhancements
// Author: Juan Carlos Garcia
// Date: 24 Enero 2026
// 
// Features:
// - KPI Sparklines with canvas rendering
// - Animated Number Counters
// - Page Transition System
// - Semantic Color System
// - Numeric Formatting Excellence (Intl.NumberFormat)
// - Gradient Overlays
// - Performance-based styling

console.log('🎨 Visual Excellence v7.0 initializing...');

// ==================== GLOBAL FORMATTERS ====================
const FORMATTERS = {
    currency: new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }),
    
    currencyCompact: new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR',
        notation: 'compact',
        compactDisplay: 'short',
        maximumFractionDigits: 1
    }),
    
    percentage: new Intl.NumberFormat('es-ES', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }),
    
    percentageCompact: new Intl.NumberFormat('es-ES', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }),
    
    number: new Intl.NumberFormat('es-ES', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }),
    
    compact: new Intl.NumberFormat('es-ES', {
        notation: 'compact',
        compactDisplay: 'short',
        maximumFractionDigits: 1
    }),
    
    ratio: new Intl.NumberFormat('es-ES', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 3
    })
};

// ==================== KPI SPARKLINE RENDERER ====================
class Sparkline {
    constructor(canvasId, data, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.warn(`Canvas ${canvasId} not found`);
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.data = data;
        this.options = {
            color: options.color || '#00d4aa',
            lineWidth: options.lineWidth || 1.5,
            fillOpacity: options.fillOpacity || 0.2,
            animate: options.animate !== undefined ? options.animate : true,
            duration: options.duration || 1000,
            showDots: options.showDots || false,
            ...options
        };
        
        this.setupCanvas();
        if (this.options.animate) {
            this.animateRender();
        } else {
            this.render();
        }
    }
    
    setupCanvas() {
        const rect = this.canvas.getBoundingClientRect();
        this.canvas.width = rect.width * window.devicePixelRatio;
        this.canvas.height = rect.height * window.devicePixelRatio;
        this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        this.width = rect.width;
        this.height = rect.height;
    }
    
    render(progress = 1) {
        const ctx = this.ctx;
        const { width, height } = this;
        const data = this.data;
        
        if (!data || data.length === 0) return;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Calculate scales
        const max = Math.max(...data);
        const min = Math.min(...data);
        const range = max - min || 1;
        const stepX = width / (data.length - 1);
        
        // Draw line
        ctx.beginPath();
        ctx.strokeStyle = this.options.color;
        ctx.lineWidth = this.options.lineWidth;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';
        
        const visiblePoints = Math.floor(data.length * progress);
        
        data.slice(0, visiblePoints).forEach((value, index) => {
            const x = index * stepX;
            const y = height - ((value - min) / range) * height;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
        
        // Fill area
        if (this.options.fillOpacity > 0 && visiblePoints > 1) {
            ctx.lineTo(stepX * (visiblePoints - 1), height);
            ctx.lineTo(0, height);
            ctx.closePath();
            
            const gradient = ctx.createLinearGradient(0, 0, 0, height);
            gradient.addColorStop(0, this.hexToRgba(this.options.color, this.options.fillOpacity));
            gradient.addColorStop(1, this.hexToRgba(this.options.color, 0));
            
            ctx.fillStyle = gradient;
            ctx.fill();
        }
        
        // Draw dots at data points
        if (this.options.showDots && visiblePoints > 0) {
            data.slice(0, visiblePoints).forEach((value, index) => {
                const x = index * stepX;
                const y = height - ((value - min) / range) * height;
                
                ctx.beginPath();
                ctx.arc(x, y, 2, 0, Math.PI * 2);
                ctx.fillStyle = this.options.color;
                ctx.fill();
            });
        }
    }
    
    animateRender() {
        const startTime = Date.now();
        const duration = this.options.duration;
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function (ease-out cubic)
            const eased = 1 - Math.pow(1 - progress, 3);
            
            this.render(eased);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    
    update(newData) {
        this.data = newData;
        if (this.options.animate) {
            this.animateRender();
        } else {
            this.render();
        }
    }
}

// ==================== ANIMATED NUMBER COUNTER ====================
function animateValue(element, start, end, duration = 1000, formatter = null) {
    if (!element) return;
    
    const range = end - start;
    const startTime = Date.now();
    
    // Add animating class
    element.classList.add('animating');
    
    const updateValue = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (ease-out cubic)
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = start + (range * eased);
        
        // Format value
        if (formatter) {
            element.textContent = formatter(current);
        } else {
            element.textContent = current.toFixed(2);
        }
        
        if (progress < 1) {
            requestAnimationFrame(updateValue);
        } else {
            element.classList.remove('animating');
        }
    };
    
    requestAnimationFrame(updateValue);
}

// ==================== PAGE TRANSITION SYSTEM ====================
class PageTransitionManager {
    constructor() {
        this.container = document.getElementById('main-container');
        this.isTransitioning = false;
    }
    
    async transitionTo(loadCallback) {
        if (this.isTransitioning || !this.container) return;
        
        this.isTransitioning = true;
        
        // Fade out
        this.container.classList.add('transitioning-out');
        await this.wait(300);
        
        // Load new content
        if (loadCallback) {
            await loadCallback();
        }
        
        // Prepare for fade in
        this.container.classList.remove('transitioning-out');
        this.container.classList.add('transitioning-in');
        
        // Small delay
        await this.wait(50);
        
        // Fade in
        this.container.classList.remove('transitioning-in');
        
        this.isTransitioning = false;
    }
    
    wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

const pageTransition = new PageTransitionManager();

// ==================== SEMANTIC COLOR SYSTEM ====================
const SEMANTIC_COLORS = {
    performance: {
        getColor: (value) => {
            if (value > 15) return { class: 'perf-excellent', color: '#10b981' };
            if (value > 5) return { class: 'perf-good', color: '#3fb950' };
            if (value > -5) return { class: 'perf-neutral', color: '#7d8590' };
            if (value > -15) return { class: 'perf-poor', color: '#f85149' };
            return { class: 'perf-critical', color: '#cf222e' };
        },
        getBadge: (value) => {
            if (value > 15) return 'badge-excellent';
            if (value > 5) return 'badge-good';
            if (value > -5) return 'badge-neutral';
            if (value > -15) return 'badge-poor';
            return 'badge-critical';
        },
        getGradient: (value) => {
            if (value > 5) return 'gradient-good';
            if (value < -5) return 'gradient-poor';
            if (value < -15) return 'gradient-critical';
            return '';
        }
    },
    
    risk: {
        getColor: (level) => {
            const levels = {
                'LOW': { class: 'risk-low', color: '#10b981', badge: 'badge-risk-low' },
                'MEDIUM': { class: 'risk-medium', color: '#d29922', badge: 'badge-risk-medium' },
                'HIGH': { class: 'risk-high', color: '#f85149', badge: 'badge-risk-high' },
                'EXTREME': { class: 'risk-extreme', color: '#cf222e', badge: 'badge-risk-extreme' }
            };
            return levels[level] || levels['MEDIUM'];
        }
    },
    
    status: {
        getColor: (status) => {
            const statuses = {
                'ACTIVE': { class: 'status-active', color: '#3fb950', badge: 'badge-active' },
                'RUNNING': { class: 'status-active', color: '#3fb950', badge: 'badge-active' },
                'PENDING': { class: 'status-pending', color: '#d29922', badge: 'badge-pending' },
                'INACTIVE': { class: 'status-inactive', color: '#7d8590', badge: 'badge-inactive' },
                'STOPPED': { class: 'status-inactive', color: '#7d8590', badge: 'badge-inactive' },
                'ERROR': { class: 'status-error', color: '#f85149', badge: 'badge-error' },
                'FAILED': { class: 'status-error', color: '#f85149', badge: 'badge-error' }
            };
            return statuses[status] || statuses['INACTIVE'];
        }
    },
    
    sentiment: {
        getTrend: (value) => {
            if (value > 3) return { class: 'bullish', icon: '↗', color: '#10b981' };
            if (value < -3) return { class: 'bearish', icon: '↘', color: '#f85149' };
            return { class: 'neutral', icon: '→', color: '#7d8590' };
        },
        getBadge: (value) => {
            if (value > 3) return 'badge-bullish';
            if (value < -3) return 'badge-bearish';
            return 'badge-sentiment-neutral';
        }
    }
};

// ==================== KPI CARD BUILDER ====================
function createEnhancedKPICard(data) {
    const {
        title,
        value,
        change,
        changePct,
        period = 'today',
        sparklineData = [],
        trend = null,
        format = 'currency',
        glassmorphic = false
    } = data;
    
    // Format values
    const formattedValue = formatValue(value, format);
    const formattedChange = formatValue(change, format);
    const formattedChangePct = FORMATTERS.percentageCompact.format(changePct / 100);
    
    // Determine colors and classes
    const perfColor = SEMANTIC_COLORS.performance.getColor(changePct);
    const changeClass = changePct >= 0 ? 'positive' : 'negative';
    const trendInfo = trend !== null ? SEMANTIC_COLORS.sentiment.getTrend(trend) : null;
    const gradientClass = SEMANTIC_COLORS.performance.getGradient(changePct);
    
    const sparklineId = `sparkline-${title.toLowerCase().replace(/\s+/g, '-')}`;
    
    return `
        <div class="kpi-card ${glassmorphic ? 'glassmorphic' : ''}" data-performance="${changePct}">
            ${gradientClass ? `<div class="gradient-overlay ${gradientClass}"></div>` : ''}
            
            <div class="kpi-header">
                <div class="kpi-title">${title}</div>
                ${trendInfo ? `<div class="kpi-trend-indicator ${trendInfo.class}">${trendInfo.icon}</div>` : ''}
            </div>
            
            <div class="kpi-value-row">
                <div class="kpi-value numeric" data-start="${value * 0.8}" data-end="${value}">
                    ${formattedValue}
                </div>
                ${sparklineData.length > 0 ? `
                    <div class="kpi-sparkline">
                        <canvas id="${sparklineId}" width="80" height="36"></canvas>
                    </div>
                ` : ''}
            </div>
            
            <div class="kpi-footer">
                <span class="kpi-change ${changeClass}">
                    ${changePct >= 0 ? '↑' : '↓'} ${formattedChange}
                </span>
                <span class="kpi-change-pct ${changeClass}">
                    ${changePct >= 0 ? '+' : ''}${formattedChangePct}
                </span>
                <span class="kpi-period">${period}</span>
            </div>
        </div>
    `;
}

// ==================== VALUE FORMATTER ====================
function formatValue(value, format) {
    if (value === null || value === undefined) return 'N/A';
    
    const absValue = Math.abs(value);
    const isCompact = absValue >= 1000000;
    
    switch (format) {
        case 'currency':
            return isCompact ? FORMATTERS.currencyCompact.format(value) : FORMATTERS.currency.format(value);
        
        case 'percentage':
            return FORMATTERS.percentage.format(value / 100);
        
        case 'number':
            return isCompact ? FORMATTERS.compact.format(value) : FORMATTERS.number.format(value);
        
        case 'ratio':
            return FORMATTERS.ratio.format(value);
        
        default:
            return value.toLocaleString('es-ES');
    }
}

// ==================== GRADIENT OVERLAY INJECTOR ====================
function applyPerformanceGradients() {
    document.querySelectorAll('.kpi-card[data-performance]').forEach(card => {
        const performance = parseFloat(card.dataset.performance);
        const gradientClass = SEMANTIC_COLORS.performance.getGradient(performance);
        
        if (gradientClass) {
            let overlay = card.querySelector('.gradient-overlay');
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.className = `gradient-overlay ${gradientClass}`;
                card.insertBefore(overlay, card.firstChild);
            } else {
                overlay.className = `gradient-overlay ${gradientClass}`;
            }
        }
    });
}

// ==================== SPARKLINE INITIALIZATION ====================
function initializeSparklines() {
    document.querySelectorAll('.kpi-sparkline canvas').forEach(canvas => {
        const sparklineData = []; // Would come from data attribute or API
        
        // Generate sample data for demo (replace with real data)
        for (let i = 0; i < 7; i++) {
            sparklineData.push(Math.random() * 100 + 50);
        }
        
        // Determine color based on trend
        const trend = sparklineData[sparklineData.length - 1] - sparklineData[0];
        const color = trend >= 0 ? '#10b981' : '#f85149';
        
        new Sparkline(canvas.id, sparklineData, {
            color: color,
            lineWidth: 2,
            fillOpacity: 0.2,
            animate: true,
            duration: 1000
        });
    });
}

// ==================== ANIMATED NUMBER UPDATES ====================
function animateKPIValues() {
    document.querySelectorAll('.kpi-value[data-start][data-end]').forEach(element => {
        const start = parseFloat(element.dataset.start);
        const end = parseFloat(element.dataset.end);
        const format = element.closest('.kpi-card').dataset.format || 'currency';
        
        animateValue(element, start, end, 1200, (value) => formatValue(value, format));
    });
}

// ==================== STAGGERED ANIMATION TRIGGER ====================
function triggerStaggeredAnimations(selector, animationClass = 'slide-up') {
    const elements = document.querySelectorAll(selector);
    
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.classList.add(animationClass);
            element.style.opacity = '';
            element.style.transform = '';
        }, index * 50);
    });
}

// ==================== PERFORMANCE-BASED THEME ====================
function applyPerformanceTheme(dailyReturn) {
    const root = document.documentElement;
    const perfColor = SEMANTIC_COLORS.performance.getColor(dailyReturn);
    
    root.style.setProperty('--accent-dynamic', perfColor.color);
    root.style.setProperty('--accent-glow', `${perfColor.color}33`);
}

// ==================== INITIALIZATION ====================
function initVisualExcellence() {
    console.log('🎨 Initializing Visual Excellence features...');
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    function init() {
        // Initialize sparklines
        setTimeout(initializeSparklines, 100);
        
        // Animate KPI values
        setTimeout(animateKPIValues, 200);
        
        // Apply performance gradients
        setTimeout(applyPerformanceGradients, 50);
        
        // Trigger staggered animations
        setTimeout(() => {
            triggerStaggeredAnimations('.kpi-card', 'slide-up');
            triggerStaggeredAnimations('.chart-card', 'slide-up');
        }, 300);
        
        console.log('✅ Visual Excellence initialized');
    }
}

// ==================== ENHANCED LOAD SECTION WRAPPER ====================
function loadSectionWithTransition(section) {
    pageTransition.transitionTo(() => {
        return new Promise((resolve) => {
            // Call original loadSection
            if (typeof loadSection === 'function') {
                loadSection(section);
            }
            
            // Wait for content to load
            setTimeout(() => {
                initVisualExcellence();
                resolve();
            }, 100);
        });
    });
}

// ==================== EXPORTS FOR GLOBAL USE ====================
window.VisualExcellence = {
    Sparkline,
    animateValue,
    formatValue,
    FORMATTERS,
    SEMANTIC_COLORS,
    createEnhancedKPICard,
    pageTransition,
    initVisualExcellence,
    loadSectionWithTransition
};

// Auto-initialize
initVisualExcellence();

// Listen for content updates
const observer = new MutationObserver((mutations) => {
    let shouldReinit = false;
    
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1 && (node.classList.contains('kpi-card') || node.querySelector('.kpi-card'))) {
                    shouldReinit = true;
                }
            });
        }
    });
    
    if (shouldReinit) {
        console.log('🔄 Re-initializing Visual Excellence...');
        setTimeout(initVisualExcellence, 100);
    }
});

if (document.getElementById('main-container')) {
    observer.observe(document.getElementById('main-container'), {
        childList: true,
        subtree: true
    });
}

console.log('✅ Visual Excellence v7.0 loaded and active');
