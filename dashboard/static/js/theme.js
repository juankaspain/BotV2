/**
 * BotV2 Dashboard - Theme System
 * Manages light/dark theme switching with localStorage persistence
 * and system preference detection.
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
