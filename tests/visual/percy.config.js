/**
 * Percy Visual Testing Configuration
 * BotV2 Dashboard - Phase 5: Excellence
 */

module.exports = {
  version: 2,
  snapshot: {
    // Viewport sizes for responsive testing
    widths: [375, 768, 1024, 1280, 1920],
    
    // Minimum height for full page captures
    minHeight: 1024,
    
    // CSS to inject before snapshot
    percyCSS: `
      /* Disable animations for stable snapshots */
      *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
      }
      
      /* Hide dynamic content */
      [data-percy="hide"],
      .percy-hide {
        visibility: hidden !important;
      }
      
      /* Stabilize loading states */
      .skeleton,
      .loader,
      .spinner {
        opacity: 1 !important;
        animation: none !important;
      }
    `,
    
    // Enable JavaScript for dynamic content
    enableJavaScript: true,
  },
  
  discovery: {
    // Wait for network idle
    networkIdleTimeout: 250,
    
    // Allowed hostnames
    allowedHostnames: [
      'localhost',
      '127.0.0.1',
    ],
  },
  
  // Snapshot options per page
  static: {
    // Dashboard pages to snapshot
    baseUrl: 'http://localhost:5000',
    files: '**/*.html',
    ignore: ['**/admin/**', '**/test/**'],
  },
};

/**
 * Page-specific configurations
 */
const pages = [
  {
    name: 'Dashboard - Overview',
    url: '/',
    waitForSelector: '.dashboard-grid',
  },
  {
    name: 'Dashboard - Positions',
    url: '/positions',
    waitForSelector: '.positions-table',
  },
  {
    name: 'Dashboard - Strategy',
    url: '/strategy',
    waitForSelector: '.strategy-editor',
  },
  {
    name: 'Dashboard - Settings',
    url: '/settings',
    waitForSelector: '.settings-form',
  },
  {
    name: 'Dashboard - Dark Theme',
    url: '/?theme=dark',
    waitForSelector: '[data-theme="dark"]',
  },
  {
    name: 'Dashboard - Light Theme',
    url: '/?theme=light',
    waitForSelector: '[data-theme="light"]',
  },
  {
    name: 'Dashboard - RTL',
    url: '/?dir=rtl',
    waitForSelector: '[dir="rtl"]',
  },
];

module.exports.pages = pages;
