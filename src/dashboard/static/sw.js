// ==================== BotV2 Service Worker v1.0 ====================
// Professional PWA Service Worker with Offline Support
// Author: Juan Carlos Garcia
// Date: 24-01-2026

const CACHE_VERSION = 'botv2-v1.0';
const CACHE_STATIC = `${CACHE_VERSION}-static`;
const CACHE_DYNAMIC = `${CACHE_VERSION}-dynamic`;
const CACHE_API = `${CACHE_VERSION}-api`;

const STATIC_ASSETS = [
  '/',
  '/static/js/dashboard.js',
  '/static/manifest.json',
  'https://cdn.plot.ly/plotly-2.27.0.min.js',
  'https://cdn.socket.io/4.5.4/socket.io.min.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
];

const API_ROUTES = [
  '/api/section/',
  '/api/data/',
  '/api/status'
];

// ==================== INSTALL ====================
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker v1.0...');
  
  event.waitUntil(
    caches.open(CACHE_STATIC)
      .then(cache => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('[SW] Static assets cached successfully');
        return self.skipWaiting();
      })
      .catch(err => {
        console.error('[SW] Error caching static assets:', err);
      })
  );
});

// ==================== ACTIVATE ====================
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker v1.0...');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(name => name.startsWith('botv2-') && name !== CACHE_STATIC && name !== CACHE_DYNAMIC && name !== CACHE_API)
            .map(name => {
              console.log('[SW] Deleting old cache:', name);
              return caches.delete(name);
            })
        );
      })
      .then(() => {
        console.log('[SW] Service Worker activated');
        return self.clients.claim();
      })
  );
});

// ==================== FETCH STRATEGIES ====================

function isApiRequest(url) {
  return API_ROUTES.some(route => url.includes(route));
}

function isStaticAsset(url) {
  return url.includes('.js') || 
         url.includes('.css') || 
         url.includes('.woff') || 
         url.includes('.woff2') ||
         url.includes('cdn.plot.ly') ||
         url.includes('cdn.socket.io') ||
         url.includes('fonts.googleapis.com');
}

// Cache-first for static assets (fast loading)
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    console.log('[SW] Cache hit:', request.url);
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_STATIC);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.error('[SW] Fetch failed:', error);
    return new Response('Offline - Asset not cached', { status: 503 });
  }
}

// Network-first for API calls (fresh data priority)
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_API);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', request.url);
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    return new Response(JSON.stringify({
      error: 'Offline',
      message: 'No cached data available'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Stale-while-revalidate for dynamic content (balanced)
async function staleWhileRevalidateStrategy(request) {
  const cachedResponse = await caches.match(request);
  
  const fetchPromise = fetch(request)
    .then(networkResponse => {
      if (networkResponse.ok) {
        const cache = caches.open(CACHE_DYNAMIC);
        cache.then(c => c.put(request, networkResponse.clone()));
      }
      return networkResponse;
    })
    .catch(() => cachedResponse);
  
  return cachedResponse || fetchPromise;
}

// ==================== FETCH HANDLER ====================
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = request.url;
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip WebSocket connections
  if (url.includes('socket.io')) {
    return;
  }
  
  // Choose strategy based on request type
  if (isApiRequest(url)) {
    event.respondWith(networkFirstStrategy(request));
  } else if (isStaticAsset(url)) {
    event.respondWith(cacheFirstStrategy(request));
  } else {
    event.respondWith(staleWhileRevalidateStrategy(request));
  }
});

// ==================== BACKGROUND SYNC ====================
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync triggered:', event.tag);
  
  if (event.tag === 'sync-data') {
    event.waitUntil(
      fetch('/api/sync')
        .then(response => response.json())
        .then(data => {
          console.log('[SW] Background sync completed:', data);
        })
        .catch(error => {
          console.error('[SW] Background sync failed:', error);
        })
    );
  }
});

// ==================== PUSH NOTIFICATIONS ====================
self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'New update available',
    icon: '/static/icon-192.png',
    badge: '/static/badge-72.png',
    vibrate: [200, 100, 200],
    tag: 'botv2-notification',
    requireInteraction: false,
    actions: [
      { action: 'view', title: 'View' },
      { action: 'dismiss', title: 'Dismiss' }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('BotV2 Dashboard', options)
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

// ==================== MESSAGE HANDLER ====================
self.addEventListener('message', (event) => {
  console.log('[SW] Message received:', event.data);
  
  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(name => caches.delete(name))
        );
      })
    );
  }
});

// ==================== ERROR HANDLER ====================
self.addEventListener('error', (event) => {
  console.error('[SW] Error:', event.error);
});

self.addEventListener('unhandledrejection', (event) => {
  console.error('[SW] Unhandled promise rejection:', event.reason);
});

console.log('[SW] Service Worker v1.0 loaded');
