/**
 * BotV2 Security Module
 * 
 * Provides client-side security features:
 * - CSRF token management
 * - XSS protection with DOMPurify
 * - Input sanitization
 * - Secure form handling
 */

// ==================== CSRF PROTECTION ====================

const Security = {
    /**
     * Get CSRF token from cookie
     */
    getCookie: function(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(';').shift();
        }
        return null;
    },

    /**
     * Get CSRF token from meta tag or cookie
     */
    getCSRFToken: function() {
        // Try meta tag first
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }
        
        // Fallback to cookie
        return this.getCookie('csrf_token');
    },

    /**
     * Setup CSRF protection for all AJAX requests
     */
    setupCSRFProtection: function() {
        const csrfToken = this.getCSRFToken();
        
        if (!csrfToken) {
            console.warn('⚠️ CSRF token not found');
            return;
        }

        // Setup for jQuery AJAX (if available)
        if (typeof $ !== 'undefined' && $.ajaxSetup) {
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    // Only add CSRF token for state-changing requests
                    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                        xhr.setRequestHeader('X-CSRF-Token', csrfToken);
                    }
                }
            });
            console.log('✅ CSRF protection enabled (jQuery)');
        }

        // Setup for fetch API
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            // Add CSRF token for state-changing requests
            if (options.method && !/^(GET|HEAD|OPTIONS)$/i.test(options.method)) {
                options.headers = options.headers || {};
                options.headers['X-CSRF-Token'] = csrfToken;
            }
            return originalFetch(url, options);
        };
        console.log('✅ CSRF protection enabled (fetch)');

        // Add CSRF token to all forms
        this.addCSRFToForms(csrfToken);
    },

    /**
     * Add CSRF token to all forms
     */
    addCSRFToForms: function(token) {
        document.querySelectorAll('form').forEach(form => {
            // Skip if already has CSRF token
            if (form.querySelector('input[name="csrf_token"]')) {
                return;
            }

            // Create hidden input
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrf_token';
            input.value = token;
            form.appendChild(input);
        });
        console.log(`✅ CSRF tokens added to ${document.querySelectorAll('form').length} forms`);
    },

    // ==================== XSS PROTECTION ====================

    /**
     * Sanitize HTML using DOMPurify
     */
    sanitizeHTML: function(dirty) {
        if (typeof DOMPurify === 'undefined') {
            console.warn('⚠️ DOMPurify not loaded, using basic escaping');
            return this.escapeHTML(dirty);
        }

        const config = {
            ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 'code', 'pre', 'span'],
            ALLOWED_ATTR: ['href', 'title', 'target', 'class'],
            ALLOW_DATA_ATTR: false,
            SAFE_FOR_JQUERY: true,
            RETURN_TRUSTED_TYPE: false
        };

        return DOMPurify.sanitize(dirty, config);
    },

    /**
     * Basic HTML escaping (fallback if DOMPurify not available)
     */
    escapeHTML: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Safely set HTML content
     */
    setHTML: function(element, html) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (!element) return;

        element.innerHTML = this.sanitizeHTML(html);
    },

    /**
     * Validate and sanitize URL
     */
    sanitizeURL: function(url) {
        // Only allow http, https, and mailto protocols
        const allowedProtocols = ['http:', 'https:', 'mailto:'];
        
        try {
            const parsed = new URL(url, window.location.origin);
            if (allowedProtocols.includes(parsed.protocol)) {
                return parsed.href;
            }
        } catch (e) {
            // Invalid URL
        }
        
        // Return empty string for invalid URLs
        return '';
    },

    // ==================== INPUT VALIDATION ====================

    /**
     * Validate email format
     */
    validateEmail: function(email) {
        const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return regex.test(email);
    },

    /**
     * Validate password strength
     */
    validatePassword: function(password, minLength = 8) {
        if (password.length < minLength) {
            return { valid: false, message: `Password must be at least ${minLength} characters` };
        }

        // Check for common weak passwords
        const weakPasswords = ['password', '12345678', 'admin', 'qwerty', 'letmein'];
        if (weakPasswords.includes(password.toLowerCase())) {
            return { valid: false, message: 'Password is too common' };
        }

        return { valid: true, message: 'Password is valid' };
    },

    /**
     * Check for dangerous input patterns
     */
    checkDangerousInput: function(input) {
        const dangerousPatterns = [
            /<script/i,
            /javascript:/i,
            /onerror=/i,
            /onload=/i,
            /onclick=/i,
            /eval\(/i,
            /expression\(/i
        ];

        for (const pattern of dangerousPatterns) {
            if (pattern.test(input)) {
                console.warn('⚠️ Dangerous pattern detected in input');
                return true;
            }
        }

        return false;
    },

    // ==================== SECURE FORM HANDLING ====================

    /**
     * Setup secure form submission
     */
    setupSecureForms: function() {
        document.querySelectorAll('form[data-secure="true"]').forEach(form => {
            form.addEventListener('submit', (e) => {
                // Validate all inputs
                const inputs = form.querySelectorAll('input[type="text"], textarea');
                for (const input of inputs) {
                    if (this.checkDangerousInput(input.value)) {
                        e.preventDefault();
                        alert('Input contains potentially dangerous content');
                        return false;
                    }
                }
            });
        });
    },

    /**
     * Sanitize form data before submission
     */
    sanitizeFormData: function(formData) {
        const sanitized = {};
        for (const [key, value] of Object.entries(formData)) {
            if (typeof value === 'string') {
                // Remove dangerous patterns but keep safe HTML
                sanitized[key] = this.sanitizeHTML(value);
            } else {
                sanitized[key] = value;
            }
        }
        return sanitized;
    },

    // ==================== CONTENT SECURITY POLICY ====================

    /**
     * Check if running under secure context (HTTPS)
     */
    isSecureContext: function() {
        return window.isSecureContext;
    },

    /**
     * Log security warnings
     */
    logSecurityWarning: function(message) {
        console.warn(`🔒 Security Warning: ${message}`);
    },

    // ==================== INITIALIZATION ====================

    /**
     * Initialize all security features
     */
    init: function() {
        console.log('🔒 Initializing BotV2 Security Module...');

        // Setup CSRF protection
        this.setupCSRFProtection();

        // Setup secure forms
        this.setupSecureForms();

        // Check secure context
        if (!this.isSecureContext() && window.location.hostname !== 'localhost') {
            this.logSecurityWarning('Not running in secure context (HTTPS)');
        }

        // Check if DOMPurify is loaded
        if (typeof DOMPurify === 'undefined') {
            this.logSecurityWarning('DOMPurify not loaded - using basic XSS protection');
        } else {
            console.log('✅ DOMPurify loaded for XSS protection');
        }

        console.log('✅ Security module initialized');
    }
};

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Security.init());
} else {
    Security.init();
}

// Export for use in other modules
window.BotV2Security = Security;
