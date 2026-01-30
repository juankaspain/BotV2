/**
 * Accessibility Audit Configuration
 * BotV2 Dashboard - Phase 5: Excellence
 * 
 * Uses axe-core for automated accessibility testing
 */

module.exports = {
  // axe-core configuration
  axe: {
    // WCAG 2.1 AA compliance
    runOnly: {
      type: 'tag',
      values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'],
    },
    
    // Rules configuration
    rules: {
      // Ensure color contrast meets WCAG AA
      'color-contrast': { enabled: true },
      
      // Ensure all images have alt text
      'image-alt': { enabled: true },
      
      // Ensure all form inputs have labels
      'label': { enabled: true },
      
      // Ensure page has landmark regions
      'region': { enabled: true },
      
      // Ensure links have discernible text
      'link-name': { enabled: true },
      
      // Ensure buttons have discernible text
      'button-name': { enabled: true },
      
      // Ensure valid ARIA usage
      'aria-valid-attr': { enabled: true },
      'aria-valid-attr-value': { enabled: true },
      
      // Ensure focus order is logical
      'focus-order-semantics': { enabled: true },
      
      // Ensure keyboard navigation
      'keyboard': { enabled: true },
    },
  },
  
  // Pages to audit
  pages: [
    {
      name: 'Dashboard Home',
      url: '/',
      context: '#main-content',
    },
    {
      name: 'Positions Page',
      url: '/positions',
      context: '#main-content',
    },
    {
      name: 'Strategy Editor',
      url: '/strategy',
      context: '#main-content',
    },
    {
      name: 'Settings Page',
      url: '/settings',
      context: '#main-content',
    },
  ],
  
  // Thresholds for pass/fail
  thresholds: {
    violations: 0,      // No violations allowed
    incomplete: 5,      // Max incomplete checks
    inapplicable: 100,  // Unlimited inapplicable
  },
  
  // Report configuration
  reports: {
    html: true,
    json: true,
    csv: false,
    outputDir: './reports/a11y',
  },
};

/**
 * Custom rules for trading dashboard
 */
const customRules = [
  {
    id: 'trading-live-regions',
    description: 'Ensure price updates use aria-live',
    selector: '[data-live-price]',
    check: (element) => {
      return element.hasAttribute('aria-live');
    },
  },
  {
    id: 'trading-action-buttons',
    description: 'Ensure trading action buttons have confirmation',
    selector: '.btn-trade, .btn-close-position',
    check: (element) => {
      return element.hasAttribute('aria-describedby') ||
             element.hasAttribute('data-confirm');
    },
  },
];

module.exports.customRules = customRules;
