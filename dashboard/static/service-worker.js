/**
 * Service Worker for BotV2 Dashboard
 * 
 * Provides offline support, caching, and performance optimization.
 * 
 * Caching Strategies:
 * - Static assets: Cache-First (HTML, CSS, JS, fonts)
 * - API calls: Network-First with fallback
 * - Images/Charts: Stale-While-Revalidate
 * 
 * Version: 3.2.0
 */

const CACHE_VERSION = 'v3.2.0';
const CACHE_PREFIX = 'dashboard';

const CACHE_NAMES = {
  static: `${CACHE_PREFIX}-static-${CACHE_VERSION}`,
  data: `${CACHE_PREFIX}-data-${CACHE_VERSION}`,
  images: `${CACHE_PREFIX}-images-${CACHE_VERSION}`
};

// Resources to pre-cache on install
const PRECACHE_RESOURCES = [
  '/',
  '/dashboard.html',
  '/static/css/styles.css',
  '/static/js/app.js',
  // CDN resources (Plotly, Socket.IO)
  'https://cdn.plot.ly/plotly-2.27.0.min.js',
  'https://cdn.socket.io/4.5.4/socket.io.min.js',
  // Google Fonts
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
  'https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&display=swap'
];

// API endpoints to cache (with network-first strategy)
const API_CACHE_PATTERNS = [
  /\/api\/portfolio/,
  /\/api\/trades/,
  /\/api\/strategies/,
  /\/api\/risk/,
  /\/api\/market/
];

// Max cache sizes (number of entries)
const MAX_CACHE_SIZES = {
  static: 50,
  data: 100,
  images: 30
};

// Cache expiration times (milliseconds)
const CACHE_EXPIRATION = {
  static: 7 * 24 * 60 * 60 * 1000,  // 7 days
  data: 1 * 60 * 60 * 1000,         // 1 hour
  images: 24 * 60 * 60 * 1000       // 24 hours
};

// ============================================
// INSTALL EVENT
// ============================================

self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker: Installing...', CACHE_VERSION);
  
  event.waitUntil(
    caches.open(CACHE_NAMES.static)
      .then((cache) => {
        console.log('📦 Service Worker: Pre-caching static resources');
        return cache.addAll(PRECACHE_RESOURCES.map(url => new Request(url, { cache: 'reload' })));
      })
      .then(() => {
        console.log('✅ Service Worker: Installation complete');
        // Skip waiting to activate immediately
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('❌ Service Worker: Installation failed', error);
      })
  );
});

// ============================================
// ACTIVATE EVENT
// ============================================

self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker: Activating...', CACHE_VERSION);
  
  event.waitUntil(
    // Clean up old caches
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              // Delete caches that don't match current version
              return cacheName.startsWith(CACHE_PREFIX) && 
                     !Object.values(CACHE_NAMES).includes(cacheName);
            })
            .map((cacheName) => {
              console.log('🗑️ Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            })
        );
      })
      .then(() => {
        console.log('✅ Service Worker: Activation complete');
        // Claim all clients immediately
        return self.clients.claim();
      })
  );
});

// ============================================
// FETCH EVENT
// ============================================

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip WebSocket connections
  if (url.protocol === 'ws:' || url.protocol === 'wss:') {
    return;
  }
  
  // Determine caching strategy based on request type
  if (isStaticAsset(url)) {
    // Cache-First for static assets
    event.respondWith(cacheFirst(request, CACHE_NAMES.static));
  } else if (isAPIRequest(url)) {
    // Network-First for API calls
    event.respondWith(networkFirst(request, CACHE_NAMES.data));
  } else if (isImageRequest(url)) {
    // Stale-While-Revalidate for images
    event.respondWith(staleWhileRevalidate(request, CACHE_NAMES.images));
  } else {
    // Default: Network with cache fallback
    event.respondWith(networkWithCacheFallback(request));
  }
});

// ============================================
// CACHING STRATEGIES
// ============================================

/**
 * Cache-First Strategy
 * Try cache first, fallback to network
 * Best for: Static assets that rarely change
 */
async function cacheFirst(request, cacheName) {
  try {
    // Try to get from cache
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      // Check if cache entry is expired
      const cacheDate = new Date(cachedResponse.headers.get('sw-cached-date'));
      const now = Date.now();
      
      if (now - cacheDate.getTime() < CACHE_EXPIRATION.static) {
        console.log('📦 Cache hit:', request.url);
        return cachedResponse;
      }
    }
    
    // Fetch from network
    console.log('🌐 Network fetch:', request.url);
    const networkResponse = await fetch(request);
    
    // Cache the response
    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(cacheName);
      const responseToCache = networkResponse.clone();
      
      // Add cache date header
      const headers = new Headers(responseToCache.headers);
      headers.append('sw-cached-date', new Date().toISOString());
      
      const modifiedResponse = new Response(responseToCache.body, {
        status: responseToCache.status,
        statusText: responseToCache.statusText,
        headers: headers
      });
      
      cache.put(request, modifiedResponse);
      
      // Enforce cache size limits
      await enforceCacheLimit(cacheName, MAX_CACHE_SIZES.static);
    }
    
    return networkResponse;
  } catch (error) {
    console.error('❌ Cache-First failed:', error);
    
    // Try cache as last resort
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page
    return new Response('Offline - Please check your connection', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

/**
 * Network-First Strategy
 * Try network first, fallback to cache
 * Best for: API calls that need fresh data
 */
async function networkFirst(request, cacheName) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
      await enforceCacheLimit(cacheName, MAX_CACHE_SIZES.data);
    }
    
    return networkResponse;
  } catch (error) {
    console.warn('⚠️ Network failed, using cache:', request.url);
    
    // Fallback to cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      // Add header to indicate stale data
      const headers = new Headers(cachedResponse.headers);
      headers.append('sw-from-cache', 'true');
      
      return new Response(cachedResponse.body, {
        status: cachedResponse.status,
        statusText: cachedResponse.statusText,
        headers: headers
      });
    }
    
    // No cache available
    return new Response(JSON.stringify({
      error: 'No network connection and no cached data available'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * Stale-While-Revalidate Strategy
 * Serve from cache immediately, update cache in background
 * Best for: Images, charts, non-critical resources
 */
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  // Fetch from network in background
  const fetchPromise = fetch(request).then((networkResponse) => {
    if (networkResponse && networkResponse.status === 200) {
      cache.put(request, networkResponse.clone());
      enforceCacheLimit(cacheName, MAX_CACHE_SIZES.images);
    }
    return networkResponse;
  }).catch(() => cachedResponse);
  
  // Return cached response immediately if available
  return cachedResponse || fetchPromise;
}

/**
 * Network with Cache Fallback
 * Default strategy for unknown resources
 */
async function networkWithCacheFallback(request) {
  try {
    return await fetch(request);
  } catch (error) {
    const cachedResponse = await caches.match(request);
    return cachedResponse || new Response('Offline', { status: 503 });
  }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Check if request is for static asset
 */
function isStaticAsset(url) {
  return url.pathname.match(/\.(html|css|js|woff2?|ttf|eot|svg|ico)$/i) ||
         url.hostname.includes('cdn.') ||
         url.hostname.includes('fonts.googleapis.com');
}

/**
 * Check if request is for API
 */
function isAPIRequest(url) {
  return API_CACHE_PATTERNS.some(pattern => pattern.test(url.pathname));
}

/**
 * Check if request is for image
 */
function isImageRequest(url) {
  return url.pathname.match(/\.(png|jpg|jpeg|gif|webp)$/i);
}

/**
 * Enforce cache size limit (LRU eviction)
 */
async function enforceCacheLimit(cacheName, maxSize) {
  const cache = await caches.open(cacheName);
  const keys = await cache.keys();
  
  if (keys.length > maxSize) {
    // Delete oldest entries (FIFO for simplicity)
    const toDelete = keys.slice(0, keys.length - maxSize);
    await Promise.all(toDelete.map(key => cache.delete(key)));
    console.log(`🗑️ Evicted ${toDelete.length} entries from ${cacheName}`);
  }
}

/**
 * Clear all caches (for debugging)
 */
async function clearAllCaches() {
  const cacheNames = await caches.keys();
  await Promise.all(cacheNames.map(name => caches.delete(name)));
  console.log('🗑️ All caches cleared');
}

// ============================================
// MESSAGE HANDLERS
// ============================================

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    console.log('⏭️ Service Worker: Skip waiting');
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    console.log('🗑️ Service Worker: Clear cache requested');
    clearAllCaches().then(() => {
      event.ports[0].postMessage({ success: true });
    });
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_VERSION });
  }
});

// ============================================
// BACKGROUND SYNC
// ============================================

self.addEventListener('sync', (event) => {
  console.log('🔄 Background sync:', event.tag);
  
  if (event.tag === 'sync-portfolio') {
    event.waitUntil(syncPortfolioData());
  }
});

async function syncPortfolioData() {
  try {
    const response = await fetch('/api/portfolio');
    if (response.ok) {
      console.log('✅ Portfolio synced in background');
    }
  } catch (error) {
    console.error('❌ Background sync failed:', error);
  }
}

// ============================================
// PUSH NOTIFICATIONS (Optional)
// ============================================

self.addEventListener('push', (event) => {
  if (!event.data) return;
  
  const data = event.data.json();
  const options = {
    body: data.message,
    icon: '/static/images/icon-192.png',
    badge: '/static/images/badge-72.png',
    data: data,
    actions: [
      { action: 'view', title: 'View Dashboard' },
      { action: 'dismiss', title: 'Dismiss' }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

console.log('✅ Service Worker script loaded:', CACHE_VERSION);
