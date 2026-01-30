/**
 * BotV2 Dashboard - Theme System v2.0
 * Manages light/dark theme switching with localStorage persistence,
 * system preference detection, and CSS variable utilities for charts.
 * 
 * NEW in v2.0:
 * - getChartColors(): Theme-aware colors for Chart.js
 * - getChartDefaults(): Reusable Chart.js configuration
 * - getCSSVariable(): Read CSS custom properties dynamically
 */

const ThemeManager = {
  STORAGE_KEY: 'botv2-theme',
  THEMES: { LIGHT: 'light', DARK: 'dark' },
  
  /**
   * Initialize theme system
   */
  init() {
    this.applyTheme(this.getTheme());
    this.bindEvents();
    this.watchSystemPreference();
  },
  
  /**
   * Get current theme from storage or system preference
   */
  getTheme() {
    const stored = localStorage.getItem(this.STORAGE_KEY);
    if (stored) return stored;
    
    // Check system preference
    if (window.matchMedia('(prefers-color-scheme: light)').matches) {
      return this.THEMES.LIGHT;
    }
    return this.THEMES.DARK;
  },
  
  /**
   * Set and persist theme
   */
  setTheme(theme) {
    localStorage.setItem(this.STORAGE_KEY, theme);
    this.applyTheme(theme);
  },
  
  /**
   * Apply theme to document
   */
  applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.classList.remove('light-theme', 'dark-theme');
    document.documentElement.classList.add(`${theme}-theme`);
    
    // Add transition class temporarily
    document.body.classList.add('theme-transition');
    setTimeout(() => document.body.classList.remove('theme-transition'), 300);
    
    // Dispatch event for other components
    window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
  },
  
  /**
   * Toggle between themes
   */
  toggle() {
    const current = this.getTheme();
    const next = current === this.THEMES.DARK ? this.THEMES.LIGHT : this.THEMES.DARK;
    this.setTheme(next);
    return next;
  },
  
  /**
   * Bind click events to theme toggle buttons
   */
  bindEvents() {
    document.querySelectorAll('.theme-toggle, [data-theme-toggle]').forEach(btn => {
      btn.addEventListener('click', () => this.toggle());
    });
  },
  
  /**
   * Watch for system preference changes
   */
  watchSystemPreference() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: light)');
    mediaQuery.addEventListener('change', (e) => {
      // Only auto-switch if user hasn't manually set a preference
      if (!localStorage.getItem(this.STORAGE_KEY)) {
        this.applyTheme(e.matches ? this.THEMES.LIGHT : this.THEMES.DARK);
      }
    });
  },

  // ============================================================================
  // NEW v2.0: CSS VARIABLE UTILITIES
  // ============================================================================

  /**
   * Get a CSS variable value from :root
   * @param {string} varName - CSS variable name (with or without --)
   * @returns {string} The computed CSS variable value
   * 
   * @example
   * getCSSVariable('--color-primary') // Returns '#5b8def'
   * getCSSVariable('color-primary')   // Also works without '--'
   */
  getCSSVariable(varName) {
    const name = varName.startsWith('--') ? varName : `--${varName}`;
    return getComputedStyle(document.documentElement)
      .getPropertyValue(name)
      .trim();
  },

  /**
   * Get theme-aware colors for Chart.js
   * Reads current theme CSS variables dynamically
   * 
   * @returns {Object} Color palette object with semantic colors
   * 
   * @example
   * const colors = ThemeManager.getChartColors();
   * backgroundColor: [colors.primary, colors.success, colors.warning]
   */
  getChartColors() {
    return {
      // Semantic colors
      primary: this.getCSSVariable('color-primary'),
      primaryDark: this.getCSSVariable('color-primary-dark'),
      primaryLight: this.getCSSVariable('color-primary-light'),
      
      success: this.getCSSVariable('color-success'),
      successDark: this.getCSSVariable('color-success-dark'),
      successLight: this.getCSSVariable('color-success-light'),
      
      warning: this.getCSSVariable('color-warning'),
      warningDark: this.getCSSVariable('color-warning-dark'),
      warningLight: this.getCSSVariable('color-warning-light'),
      
      danger: this.getCSSVariable('color-danger'),
      dangerDark: this.getCSSVariable('color-danger-dark'),
      dangerLight: this.getCSSVariable('color-danger-light'),
      
      info: this.getCSSVariable('color-info'),
      infoDark: this.getCSSVariable('color-info-dark'),
      infoLight: this.getCSSVariable('color-info-light'),
      
      // Text colors
      textPrimary: this.getCSSVariable('text-primary'),
      textSecondary: this.getCSSVariable('text-secondary'),
      textMuted: this.getCSSVariable('text-muted'),
      
      // Background colors
      bgCard: this.getCSSVariable('bg-card'),
      bgCardHover: this.getCSSVariable('bg-card-hover'),
      
      // Border colors
      borderColor: this.getCSSVariable('border-color'),
      borderColorLight: this.getCSSVariable('border-color-light'),

      // Utility: Get array of main colors (for pie/doughnut charts)
      palette: [
        this.getCSSVariable('color-primary'),
        this.getCSSVariable('color-success'),
        this.getCSSVariable('color-warning'),
        this.getCSSVariable('color-danger'),
        this.getCSSVariable('color-info'),
        '#eb459e', // Pink (not in CSS vars, optional)
        '#00d9ff'  // Cyan (not in CSS vars, optional)
      ]
    };
  },

  /**
   * Get Chart.js default configuration (theme-aware)
   * Use as base for all charts to maintain consistency
   * 
   * @param {string} type - Chart type: 'line', 'bar', 'doughnut', etc.
   * @returns {Object} Chart.js configuration object
   * 
   * @example
   * const config = ThemeManager.getChartDefaults('line');
   * config.data = { labels: [...], datasets: [...] };
   * new Chart(ctx, config);
   */
  getChartDefaults(type = 'line') {
    const colors = this.getChartColors();
    
    const baseConfig = {
      type: type,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          legend: {
            display: true,
            position: 'bottom',
            labels: {
              color: colors.textPrimary,
              padding: 15,
              font: {
                size: 12,
                family: "'Inter', sans-serif"
              },
              usePointStyle: true,
              pointStyle: 'circle'
            }
          },
          tooltip: {
            enabled: true,
            backgroundColor: colors.bgCard,
            titleColor: colors.textPrimary,
            bodyColor: colors.textSecondary,
            borderColor: colors.borderColor,
            borderWidth: 1,
            padding: 12,
            cornerRadius: 8,
            titleFont: {
              size: 13,
              weight: '600',
              family: "'Inter', sans-serif"
            },
            bodyFont: {
              size: 12,
              family: "'Inter', sans-serif"
            }
          }
        }
      }
    };

    // Type-specific configurations
    if (type === 'line' || type === 'bar') {
      baseConfig.options.scales = {
        x: {
          grid: {
            color: colors.borderColor,
            borderColor: colors.borderColorLight,
          },
          ticks: {
            color: colors.textSecondary,
            font: { size: 11 }
          }
        },
        y: {
          grid: {
            color: colors.borderColor,
            borderColor: colors.borderColorLight,
          },
          ticks: {
            color: colors.textSecondary,
            font: { size: 11 }
          }
        }
      };
    }

    return baseConfig;
  }
};

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
} else {
  ThemeManager.init();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ThemeManager;
}

// Also expose as window global for inline scripts
window.ThemeManager = ThemeManager;
