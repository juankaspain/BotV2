/**
 * BotV2 Security Module
 * 
 * Provides frontend security features:
 * - CSRF token management
 * - XSS protection with DOMPurify
 * - Secure form submission
 * - Input validation
 * 
 * @version 1.0.0
 */

(function(window) {
    'use strict';
    
    /**
     * Security Manager
     */
    const Security = {
        /**
         * Initialize security features
         */
        init: function() {
            console.log('🔒 Initializing BotV2 Security...');
            
            this.setupCSRFProtection();
            this.setupXSSProtection();
            this.setupFormValidation();
            
            console.log('✅ Security initialized');
        },
        
        /**
         * Setup CSRF protection for all AJAX requests and forms
         */
        setupCSRFProtection: function() {
            const csrfToken = this.getCSRFToken();
            
            if (!csrfToken) {
                console.warn('⚠️ CSRF token not found');
                return;
            }
            
            // Add CSRF token to all AJAX requests
            if (window.jQuery) {
                $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        // Skip CSRF for safe methods
                        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                            xhr.setRequestHeader('X-CSRF-Token', csrfToken);
                        }
                    }
                });
                console.log('✅ CSRF protection enabled for jQuery AJAX');
            }
            
            // Add CSRF token to all fetch requests
            const originalFetch = window.fetch;
            window.fetch = function(url, options = {}) {
                options.headers = options.headers || {};
                
                // Add CSRF token for state-changing methods
                if (options.method && !/^(GET|HEAD|OPTIONS)$/i.test(options.method)) {
                    options.headers['X-CSRF-Token'] = csrfToken;
                }
                
                return originalFetch(url, options);
            };
            console.log('✅ CSRF protection enabled for fetch API');
            
            // Add CSRF token to all forms
            this.injectCSRFTokens();
        },
        
        /**
         * Get CSRF token from cookie or meta tag
         */
        getCSRFToken: function() {
            // Try cookie first
            const cookieToken = this.getCookie('csrf_token');
            if (cookieToken) {
                return cookieToken;
            }
            
            // Try meta tag
            const metaToken = document.querySelector('meta[name="csrf-token"]');
            if (metaToken) {
                return metaToken.getAttribute('content');
            }
            
            return null;
        },
        
        /**
         * Inject CSRF tokens into all forms
         */
        injectCSRFTokens: function() {
            const csrfToken = this.getCSRFToken();
            if (!csrfToken) return;
            
            document.querySelectorAll('form').forEach(form => {
                // Skip if already has CSRF token
                if (form.querySelector('input[name="csrf_token"]')) {
                    return;
                }
                
                // Skip for GET forms
                if (form.method.toUpperCase() === 'GET') {
                    return;
                }
                
                // Create hidden input with CSRF token
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'csrf_token';
                input.value = csrfToken;
                form.appendChild(input);
            });
            
            console.log('✅ CSRF tokens injected into forms');
        },
        
        /**
         * Setup XSS protection with DOMPurify
         */
        setupXSSProtection: function() {
            // Check if DOMPurify is loaded
            if (typeof DOMPurify === 'undefined') {
                console.warn('⚠️ DOMPurify not loaded - XSS protection limited');
                return;
            }
            
            // Configure DOMPurify
            this.domPurifyConfig = {
                ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'a', 'code', 'pre'],
                ALLOWED_ATTR: ['href', 'title', 'target'],
                ALLOW_DATA_ATTR: false,
                SAFE_FOR_JQUERY: true
            };
            
            console.log('✅ XSS protection configured with DOMPurify');
        },
        
        /**
         * Sanitize HTML content
         */
        sanitizeHTML: function(dirty) {
            if (typeof DOMPurify === 'undefined') {
                // Fallback: basic HTML escaping
                const div = document.createElement('div');
                div.textContent = dirty;
                return div.innerHTML;
            }
            
            return DOMPurify.sanitize(dirty, this.domPurifyConfig);
        },
        
        /**
         * Safely set innerHTML with sanitization
         */
        safeInnerHTML: function(element, html) {
            if (typeof element === 'string') {
                element = document.querySelector(element);
            }
            
            if (!element) {
                console.error('Element not found');
                return;
            }
            
            element.innerHTML = this.sanitizeHTML(html);
        },
        
        /**
         * Setup form validation
         */
        setupFormValidation: function() {
            document.querySelectorAll('form[data-validate]').forEach(form => {
                form.addEventListener('submit', (e) => {
                    if (!this.validateForm(form)) {
                        e.preventDefault();
                        return false;
                    }
                });
            });
            
            console.log('✅ Form validation enabled');
        },
        
        /**
         * Validate form inputs
         */
        validateForm: function(form) {
            let isValid = true;
            
            // Check required fields
            form.querySelectorAll('[required]').forEach(input => {
                if (!input.value.trim()) {
                    this.showFieldError(input, 'This field is required');
                    isValid = false;
                } else {
                    this.clearFieldError(input);
                }
            });
            
            // Check email fields
            form.querySelectorAll('input[type="email"]').forEach(input => {
                if (input.value && !this.isValidEmail(input.value)) {
                    this.showFieldError(input, 'Invalid email address');
                    isValid = false;
                }
            });
            
            return isValid;
        },
        
        /**
         * Show field validation error
         */
        showFieldError: function(input, message) {
            input.classList.add('is-invalid');
            
            let errorDiv = input.nextElementSibling;
            if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                input.parentNode.insertBefore(errorDiv, input.nextSibling);
            }
            
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        },
        
        /**
         * Clear field validation error
         */
        clearFieldError: function(input) {
            input.classList.remove('is-invalid');
            
            const errorDiv = input.nextElementSibling;
            if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                errorDiv.style.display = 'none';
            }
        },
        
        /**
         * Validate email format
         */
        isValidEmail: function(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        },
        
        /**
         * Get cookie value by name
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
         * Escape HTML entities
         */
        escapeHTML: function(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },
        
        /**
         * Check if string contains dangerous patterns
         */
        containsXSS: function(text) {
            const dangerousPatterns = [
                /<script/i,
                /javascript:/i,
                /onerror=/i,
                /onload=/i,
                /onclick=/i,
                /<iframe/i
            ];
            
            return dangerousPatterns.some(pattern => pattern.test(text));
        }
    };
    
    // Auto-initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => Security.init());
    } else {
        Security.init();
    }
    
    // Export to window
    window.BotV2Security = Security;
    
})(window);
