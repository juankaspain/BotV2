// ==================== BotV2 PWA Installer v1.0 ====================
// Progressive Web App installation and service worker registration
// Author: Juan Carlos Garcia
// Date: 24-01-2026
// Version: 1.0.0 - PRODUCTION READY

(function() {
    'use strict';

    const PWA_VERSION = '1.0.0';
    const LOG_PREFIX = '%c[PWA]%c';
    const LOG_STYLE_1 = 'background:#2f81f7;color:white;padding:2px 6px;border-radius:3px;font-weight:600';
    const LOG_STYLE_2 = 'color:#7d8590';

    // ==================== LOGGER ====================
    const Logger = {
        info: (msg, ...args) => {
            console.log(`${LOG_PREFIX} ${msg}`, LOG_STYLE_1, LOG_STYLE_2, ...args);
        },
        success: (msg, ...args) => {
            console.log(`${LOG_PREFIX} ✅ ${msg}`, LOG_STYLE_1, LOG_STYLE_2, ...args);
        },
        warn: (msg, ...args) => {
            console.warn(`${LOG_PREFIX} ⚠️ ${msg}`, LOG_STYLE_1, LOG_STYLE_2, ...args);
        },
        error: (msg, ...args) => {
            console.error(`${LOG_PREFIX} ❌ ${msg}`, LOG_STYLE_1, LOG_STYLE_2, ...args);
        }
    };

    // ==================== SERVICE WORKER REGISTRATION ====================
    async function registerServiceWorker() {
        if (!('serviceWorker' in navigator)) {
            Logger.warn('Service Worker not supported in this browser');
            return null;
        }

        try {
            // Check if already registered
            const registration = await navigator.serviceWorker.getRegistration();
            if (registration) {
                Logger.info('Service Worker already registered', {
                    scope: registration.scope,
                    active: !!registration.active
                });
                return registration;
            }

            // Register new service worker
            Logger.info('Registering Service Worker...');
            const newRegistration = await navigator.serviceWorker.register('/sw.js', {
                scope: '/'
            });

            Logger.success('Service Worker registered successfully', {
                scope: newRegistration.scope
            });

            // Handle updates
            newRegistration.addEventListener('updatefound', () => {
                const newWorker = newRegistration.installing;
                Logger.info('New Service Worker version found');

                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        Logger.info('New version available - Please refresh');
                        // Could show update notification here
                    }
                });
            });

            return newRegistration;
        } catch (error) {
            // Don't throw error if service worker is not available
            // This is expected in development without HTTPS
            Logger.warn('Service Worker registration skipped', error.message);
            return null;
        }
    }

    // ==================== PWA INSTALLATION ====================
    let deferredPrompt = null;

    function setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (e) => {
            // Prevent default mini-infobar
            e.preventDefault();
            deferredPrompt = e;

            Logger.info('PWA installation available');

            // Could show install button here
            // showInstallButton();
        });

        window.addEventListener('appinstalled', () => {
            Logger.success('PWA installed successfully');
            deferredPrompt = null;
        });
    }

    // ==================== PUBLIC API ====================
    window.PWAInstaller = {
        version: PWA_VERSION,

        async install() {
            if (!deferredPrompt) {
                Logger.warn('PWA installation not available');
                return false;
            }

            try {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;

                if (outcome === 'accepted') {
                    Logger.success('User accepted installation');
                    return true;
                } else {
                    Logger.info('User declined installation');
                    return false;
                }
            } catch (error) {
                Logger.error('Installation failed', error);
                return false;
            }
        },

        isInstallable() {
            return deferredPrompt !== null;
        },

        async unregisterServiceWorker() {
            if (!('serviceWorker' in navigator)) {
                return false;
            }

            const registration = await navigator.serviceWorker.getRegistration();
            if (registration) {
                await registration.unregister();
                Logger.info('Service Worker unregistered');
                return true;
            }
            return false;
        }
    };

    // ==================== INITIALIZATION ====================
    async function init() {
        Logger.info(`Initializing PWA Installer v${PWA_VERSION}`);

        // Setup installation prompt
        setupInstallPrompt();

        // Register service worker (optional - only in production with HTTPS)
        // await registerServiceWorker();

        Logger.success('PWA Installer ready');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
