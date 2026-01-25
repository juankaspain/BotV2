// ==================== BOTV2 PERFORMANCE OPTIMIZER v1.0 ====================
// ⚡ Advanced Performance Optimization Patterns
// Author: Juan Carlos Garcia
// Date: 25 Enero 2026
//
// Features:
// - Debounce & Throttle with advanced options
// - Section Loading Cache with LRU eviction
// - Request Deduplication
// - Mutex Lock Pattern (prevent concurrent execution)
// - Prefetch & Predictive Loading
// - Lazy Loading Components
// - Performance Monitoring
// - Resource Waterfall Optimization

console.log('⚡ Performance Optimizer v1.0 initializing...');

// ==================== UTILITY FUNCTIONS ====================

/**
 * Debounce function with leading/trailing options
 * Delays execution until after wait milliseconds have elapsed since last call
 * 
 * @param {Function} callback - Function to debounce
 * @param {number} wait - Delay in milliseconds (default: 300ms)
 * @param {Object} options - Configuration options
 * @param {boolean} options.leading - Execute on leading edge (default: false)
 * @param {boolean} options.trailing - Execute on trailing edge (default: true)
 * @param {number} options.maxWait - Maximum time callback can be delayed
 * @returns {Function} Debounced function with cancel() and flush() methods
 * 
 * @example
 * const debouncedSearch = debounce(searchAPI, 500, { leading: false, trailing: true });
 * input.addEventListener('input', debouncedSearch);
 * // Cancel pending execution: debouncedSearch.cancel();
 * // Execute immediately: debouncedSearch.flush();
 */
function debounce(callback, wait = 300, options = {}) {
    const { leading = false, trailing = true, maxWait = null } = options;
    
    let timeoutId = null;
    let maxTimeoutId = null;
    let lastCallTime = 0;
    let lastInvokeTime = 0;
    let lastArgs = null;
    let lastThis = null;
    let result = null;
    
    function invokeCallback(time) {
        const args = lastArgs;
        const thisArg = lastThis;
        
        lastArgs = lastThis = null;
        lastInvokeTime = time;
        result = callback.apply(thisArg, args);
        return result;
    }
    
    function shouldInvoke(time) {
        const timeSinceLastCall = time - lastCallTime;
        const timeSinceLastInvoke = time - lastInvokeTime;
        
        return (
            lastCallTime === 0 ||
            timeSinceLastCall >= wait ||
            timeSinceLastCall < 0 ||
            (maxWait !== null && timeSinceLastInvoke >= maxWait)
        );
    }
    
    function leadingEdge(time) {
        lastInvokeTime = time;
        timeoutId = setTimeout(timerExpired, wait);
        return leading ? invokeCallback(time) : result;
    }
    
    function remainingWait(time) {
        const timeSinceLastCall = time - lastCallTime;
        const timeSinceLastInvoke = time - lastInvokeTime;
        const timeWaiting = wait - timeSinceLastCall;
        
        return maxWait !== null
            ? Math.min(timeWaiting, maxWait - timeSinceLastInvoke)
            : timeWaiting;
    }
    
    function timerExpired() {
        const time = Date.now();
        if (shouldInvoke(time)) {
            return trailingEdge(time);
        }
        timeoutId = setTimeout(timerExpired, remainingWait(time));
    }
    
    function trailingEdge(time) {
        timeoutId = null;
        
        if (trailing && lastArgs) {
            return invokeCallback(time);
        }
        lastArgs = lastThis = null;
        return result;
    }
    
    function cancel() {
        if (timeoutId !== null) {
            clearTimeout(timeoutId);
        }
        if (maxTimeoutId !== null) {
            clearTimeout(maxTimeoutId);
        }
        lastInvokeTime = 0;
        lastArgs = lastThis = timeoutId = maxTimeoutId = null;
    }
    
    function flush() {
        return timeoutId === null ? result : trailingEdge(Date.now());
    }
    
    function debounced(...args) {
        const time = Date.now();
        const isInvoking = shouldInvoke(time);
        
        lastArgs = args;
        lastThis = this;
        lastCallTime = time;
        
        if (isInvoking) {
            if (timeoutId === null) {
                return leadingEdge(lastCallTime);
            }
            if (maxWait !== null) {
                timeoutId = setTimeout(timerExpired, wait);
                return invokeCallback(lastCallTime);
            }
        }
        if (timeoutId === null) {
            timeoutId = setTimeout(timerExpired, wait);
        }
        return result;
    }
    
    debounced.cancel = cancel;
    debounced.flush = flush;
    
    return debounced;
}

/**
 * Throttle function with leading/trailing options
 * Limits execution to once per specified time period
 * 
 * @param {Function} callback - Function to throttle
 * @param {number} wait - Time period in milliseconds (default: 300ms)
 * @param {Object} options - Configuration options
 * @param {boolean} options.leading - Execute on leading edge (default: true)
 * @param {boolean} options.trailing - Execute on trailing edge (default: true)
 * @returns {Function} Throttled function with cancel() method
 * 
 * @example
 * const throttledScroll = throttle(handleScroll, 100, { leading: true, trailing: false });
 * window.addEventListener('scroll', throttledScroll);
 */
function throttle(callback, wait = 300, options = {}) {
    const { leading = true, trailing = true } = options;
    return debounce(callback, wait, {
        leading,
        trailing,
        maxWait: wait
    });
}

// ==================== MUTEX LOCK PATTERN ====================

/**
 * Mutex (Mutual Exclusion) Lock for preventing concurrent function execution
 * Ensures only one instance of a function runs at a time
 * 
 * @example
 * const loadSectionLock = new MutexLock();
 * 
 * async function loadSection(section) {
 *   if (!await loadSectionLock.acquire()) {
 *     console.log('Section loading already in progress');
 *     return;
 *   }
 *   try {
 *     // Load section logic
 *   } finally {
 *     loadSectionLock.release();
 *   }
 * }
 */
class MutexLock {
    constructor() {
        this.locked = false;
        this.queue = [];
    }
    
    /**
     * Attempt to acquire the lock
     * @returns {Promise<boolean>} True if lock acquired, false if already locked
     */
    async acquire() {
        if (!this.locked) {
            this.locked = true;
            return true;
        }
        
        // Return false immediately if lock is held (non-blocking)
        return false;
    }
    
    /**
     * Release the lock
     */
    release() {
        this.locked = false;
        
        if (this.queue.length > 0) {
            const resolve = this.queue.shift();
            resolve();
        }
    }
    
    /**
     * Wait for lock to become available (blocking)
     * @returns {Promise<void>}
     */
    async waitForLock() {
        if (!this.locked) {
            this.locked = true;
            return;
        }
        
        return new Promise(resolve => {
            this.queue.push(() => {
                this.locked = true;
                resolve();
            });
        });
    }
    
    /**
     * Check if lock is currently held
     * @returns {boolean}
     */
    isLocked() {
        return this.locked;
    }
}

// ==================== SECTION CACHE WITH LRU EVICTION ====================

/**
 * LRU (Least Recently Used) Cache for section content
 * Automatically evicts least recently used items when capacity is reached
 */
class SectionCache {
    constructor(capacity = 10, ttl = 300000) { // 5 minutes TTL
        this.capacity = capacity;
        this.ttl = ttl; // Time to live in milliseconds
        this.cache = new Map();
        this.timestamps = new Map();
    }
    
    /**
     * Get cached section content
     * @param {string} key - Section identifier
     * @returns {any|null} Cached content or null if not found/expired
     */
    get(key) {
        if (!this.cache.has(key)) {
            return null;
        }
        
        // Check TTL
        const timestamp = this.timestamps.get(key);
        if (Date.now() - timestamp > this.ttl) {
            this.delete(key);
            return null;
        }
        
        // Move to end (most recently used)
        const value = this.cache.get(key);
        this.cache.delete(key);
        this.cache.set(key, value);
        this.timestamps.set(key, Date.now());
        
        console.log(`💾 Cache HIT: ${key}`);
        return value;
    }
    
    /**
     * Store section content in cache
     * @param {string} key - Section identifier
     * @param {any} value - Content to cache
     */
    set(key, value) {
        // Remove if exists (to update position)
        if (this.cache.has(key)) {
            this.cache.delete(key);
        }
        // Evict least recently used if at capacity
        else if (this.cache.size >= this.capacity) {
            const firstKey = this.cache.keys().next().value;
            this.delete(firstKey);
            console.log(`🗑️ Cache EVICT: ${firstKey}`);
        }
        
        this.cache.set(key, value);
        this.timestamps.set(key, Date.now());
        console.log(`💾 Cache SET: ${key}`);
    }
    
    /**
     * Delete cached section
     * @param {string} key - Section identifier
     */
    delete(key) {
        this.cache.delete(key);
        this.timestamps.delete(key);
    }
    
    /**
     * Clear entire cache
     */
    clear() {
        this.cache.clear();
        this.timestamps.clear();
        console.log('🗑️ Cache CLEARED');
    }
    
    /**
     * Get cache statistics
     * @returns {Object} Cache stats
     */
    stats() {
        return {
            size: this.cache.size,
            capacity: this.capacity,
            keys: Array.from(this.cache.keys())
        };
    }
}

// ==================== REQUEST DEDUPLICATION ====================

/**
 * Request Deduplication Manager
 * Prevents multiple identical requests from being sent concurrently
 */
class RequestDeduplicator {
    constructor() {
        this.pendingRequests = new Map();
    }
    
    /**
     * Execute request with deduplication
     * @param {string} key - Unique request identifier
     * @param {Function} requestFn - Function that returns a Promise
     * @returns {Promise} Request result
     */
    async execute(key, requestFn) {
        // Return existing promise if request is pending
        if (this.pendingRequests.has(key)) {
            console.log(`🔄 Request DEDUPLICATED: ${key}`);
            return this.pendingRequests.get(key);
        }
        
        // Create new request
        const promise = requestFn()
            .finally(() => {
                // Remove from pending when complete
                this.pendingRequests.delete(key);
            });
        
        this.pendingRequests.set(key, promise);
        console.log(`🚀 Request STARTED: ${key}`);
        
        return promise;
    }
    
    /**
     * Cancel pending request
     * @param {string} key - Request identifier
     */
    cancel(key) {
        if (this.pendingRequests.has(key)) {
            this.pendingRequests.delete(key);
            console.log(`❌ Request CANCELLED: ${key}`);
        }
    }
    
    /**
     * Clear all pending requests
     */
    cancelAll() {
        this.pendingRequests.clear();
        console.log('❌ All requests CANCELLED');
    }
}

// ==================== ABORT CONTROLLER MANAGER ====================

/**
 * AbortController Manager for canceling fetch requests
 */
class AbortControllerManager {
    constructor() {
        this.controllers = new Map();
    }
    
    /**
     * Create and store AbortController
     * @param {string} key - Controller identifier
     * @returns {AbortController}
     */
    create(key) {
        // Abort existing controller for this key
        this.abort(key);
        
        const controller = new AbortController();
        this.controllers.set(key, controller);
        return controller;
    }
    
    /**
     * Get AbortController by key
     * @param {string} key - Controller identifier
     * @returns {AbortController|null}
     */
    get(key) {
        return this.controllers.get(key) || null;
    }
    
    /**
     * Abort request by key
     * @param {string} key - Controller identifier
     */
    abort(key) {
        const controller = this.controllers.get(key);
        if (controller) {
            controller.abort();
            this.controllers.delete(key);
            console.log(`❌ Fetch ABORTED: ${key}`);
        }
    }
    
    /**
     * Abort all requests
     */
    abortAll() {
        this.controllers.forEach((controller, key) => {
            controller.abort();
            console.log(`❌ Fetch ABORTED: ${key}`);
        });
        this.controllers.clear();
    }
}

// ==================== PREFETCH MANAGER ====================

/**
 * Prefetch Manager for predictive resource loading
 */
class PrefetchManager {
    constructor() {
        this.prefetchedData = new Map();
        this.prefetchInProgress = new Set();
    }
    
    /**
     * Prefetch data for future use
     * @param {string} key - Data identifier
     * @param {Function} fetchFn - Function that returns Promise
     */
    async prefetch(key, fetchFn) {
        if (this.prefetchedData.has(key) || this.prefetchInProgress.has(key)) {
            return;
        }
        
        this.prefetchInProgress.add(key);
        console.log(`🔍 Prefetching: ${key}`);
        
        try {
            const data = await fetchFn();
            this.prefetchedData.set(key, {
                data,
                timestamp: Date.now()
            });
            console.log(`✅ Prefetch SUCCESS: ${key}`);
        } catch (error) {
            console.error(`❌ Prefetch FAILED: ${key}`, error);
        } finally {
            this.prefetchInProgress.delete(key);
        }
    }
    
    /**
     * Get prefetched data
     * @param {string} key - Data identifier
     * @param {number} maxAge - Maximum age in milliseconds (default: 5 minutes)
     * @returns {any|null}
     */
    get(key, maxAge = 300000) {
        const cached = this.prefetchedData.get(key);
        if (!cached) return null;
        
        // Check if data is still fresh
        if (Date.now() - cached.timestamp > maxAge) {
            this.prefetchedData.delete(key);
            return null;
        }
        
        console.log(`💾 Prefetch HIT: ${key}`);
        return cached.data;
    }
    
    /**
     * Clear prefetched data
     */
    clear() {
        this.prefetchedData.clear();
    }
}

// ==================== PERFORMANCE MONITOR ====================

/**
 * Performance Monitor for tracking metrics
 */
class PerformanceMonitor {
    constructor() {
        this.marks = new Map();
        this.measures = [];
    }
    
    /**
     * Start performance measurement
     * @param {string} name - Measurement name
     */
    start(name) {
        this.marks.set(name, performance.now());
    }
    
    /**
     * End performance measurement
     * @param {string} name - Measurement name
     * @param {boolean} log - Whether to log result (default: true)
     * @returns {number} Duration in milliseconds
     */
    end(name, log = true) {
        const startTime = this.marks.get(name);
        if (!startTime) {
            console.warn(`⚠️ Performance mark '${name}' not found`);
            return 0;
        }
        
        const duration = performance.now() - startTime;
        this.measures.push({
            name,
            duration,
            timestamp: Date.now()
        });
        
        this.marks.delete(name);
        
        if (log) {
            const color = duration < 100 ? '#3fb950' : duration < 500 ? '#d29922' : '#f85149';
            console.log(
                `%c⚡ PERF%c ${name}: ${duration.toFixed(2)}ms`,
                `background:${color};color:white;padding:2px 8px;border-radius:3px;font-weight:600`,
                'color:#7d8590'
            );
        }
        
        return duration;
    }
    
    /**
     * Get performance statistics
     * @param {string} name - Filter by name (optional)
     * @returns {Object} Performance stats
     */
    getStats(name = null) {
        const filtered = name
            ? this.measures.filter(m => m.name === name)
            : this.measures;
        
        if (filtered.length === 0) {
            return { count: 0, avg: 0, min: 0, max: 0 };
        }
        
        const durations = filtered.map(m => m.duration);
        return {
            count: durations.length,
            avg: durations.reduce((a, b) => a + b, 0) / durations.length,
            min: Math.min(...durations),
            max: Math.max(...durations)
        };
    }
    
    /**
     * Clear all measurements
     */
    clear() {
        this.marks.clear();
        this.measures = [];
    }
}

// ==================== LAZY COMPONENT LOADER ====================

/**
 * Lazy Component Loader with Intersection Observer
 */
class LazyComponentLoader {
    constructor(options = {}) {
        this.options = {
            root: null,
            rootMargin: '50px',
            threshold: 0.01,
            ...options
        };
        
        this.observer = new IntersectionObserver(
            this.handleIntersection.bind(this),
            this.options
        );
        
        this.components = new Map();
    }
    
    /**
     * Register component for lazy loading
     * @param {HTMLElement} element - DOM element
     * @param {Function} loadFn - Function to call when element is visible
     */
    observe(element, loadFn) {
        this.components.set(element, { loadFn, loaded: false });
        this.observer.observe(element);
    }
    
    /**
     * Handle intersection changes
     * @private
     */
    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const component = this.components.get(entry.target);
                if (component && !component.loaded) {
                    console.log('👁️ Lazy loading component:', entry.target.id);
                    component.loadFn();
                    component.loaded = true;
                    this.observer.unobserve(entry.target);
                }
            }
        });
    }
    
    /**
     * Disconnect observer
     */
    disconnect() {
        this.observer.disconnect();
        this.components.clear();
    }
}

// ==================== GLOBAL EXPORTS ====================

const PerformanceOptimizer = {
    // Utilities
    debounce,
    throttle,
    
    // Classes
    MutexLock,
    SectionCache,
    RequestDeduplicator,
    AbortControllerManager,
    PrefetchManager,
    PerformanceMonitor,
    LazyComponentLoader,
    
    // Global instances (singleton pattern)
    sectionCache: new SectionCache(10, 300000), // 10 sections, 5 min TTL
    requestDeduplicator: new RequestDeduplicator(),
    abortManager: new AbortControllerManager(),
    prefetchManager: new PrefetchManager(),
    perfMonitor: new PerformanceMonitor(),
    loadSectionLock: new MutexLock(),
    
    // Helper: Create optimized section loader
    createOptimizedSectionLoader(loadFn) {
        return async function(section) {
            const lockAcquired = await PerformanceOptimizer.loadSectionLock.acquire();
            
            if (!lockAcquired) {
                console.log('⚠️ Section load already in progress, skipping');
                return false;
            }
            
            try {
                // Check cache first
                const cached = PerformanceOptimizer.sectionCache.get(section);
                if (cached) {
                    console.log(`🚀 Loading section from cache: ${section}`);
                    return cached;
                }
                
                // Start performance tracking
                PerformanceOptimizer.perfMonitor.start(`load_${section}`);
                
                // Load section
                const result = await loadFn(section);
                
                // Cache result
                PerformanceOptimizer.sectionCache.set(section, result);
                
                // End performance tracking
                PerformanceOptimizer.perfMonitor.end(`load_${section}`);
                
                return result;
            } catch (error) {
                console.error(`❌ Error loading section ${section}:`, error);
                throw error;
            } finally {
                PerformanceOptimizer.loadSectionLock.release();
            }
        };
    }
};

// Export to window
window.PerformanceOptimizer = PerformanceOptimizer;

console.log('✅ Performance Optimizer loaded');
console.log('📊 Available optimizations:', Object.keys(PerformanceOptimizer));
