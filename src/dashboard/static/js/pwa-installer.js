// ==================== PWA Installer v1.0 ====================
// Handles PWA installation prompt and Service Worker registration
// Author: Juan Carlos Garcia
// Date: 24-01-2026

let deferredPrompt = null;
let swRegistration = null;

// ==================== SERVICE WORKER REGISTRATION ====================
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      swRegistration = await navigator.serviceWorker.register('/static/sw.js', {
        scope: '/'
      });
      
      console.log('✅ Service Worker registered:', swRegistration.scope);
      
      // Check for updates
      swRegistration.addEventListener('updatefound', () => {
        const newWorker = swRegistration.installing;
        console.log('🔄 Service Worker update found');
        
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // New SW installed, show update notification
            showUpdateNotification();
          }
        });
      });
      
      // Listen for messages from SW
      navigator.serviceWorker.addEventListener('message', (event) => {
        console.log('📨 Message from SW:', event.data);
      });
      
    } catch (error) {
      console.error('❌ Service Worker registration failed:', error);
    }
  });
}

// ==================== INSTALL PROMPT ====================
window.addEventListener('beforeinstallprompt', (e) => {
  console.log('💾 PWA Install prompt available');
  e.preventDefault();
  deferredPrompt = e;
  
  // Show custom install button (if exists)
  const installBtn = document.getElementById('pwa-install-btn');
  if (installBtn) {
    installBtn.style.display = 'block';
    installBtn.addEventListener('click', showInstallPrompt);
  }
  
  // Auto-show install banner after 30 seconds
  setTimeout(() => {
    if (deferredPrompt && !localStorage.getItem('pwa-dismissed')) {
      showInstallBanner();
    }
  }, 30000);
});

window.addEventListener('appinstalled', () => {
  console.log('✅ PWA installed successfully');
  deferredPrompt = null;
  
  // Hide install button
  const installBtn = document.getElementById('pwa-install-btn');
  if (installBtn) installBtn.style.display = 'none';
  
  // Show success toast
  if (typeof showToast === 'function') {
    showToast('BotV2 installed successfully! 🚀', 'success');
  }
});

// ==================== INSTALL FUNCTIONS ====================
function showInstallPrompt() {
  if (!deferredPrompt) {
    console.log('No install prompt available');
    return;
  }
  
  deferredPrompt.prompt();
  
  deferredPrompt.userChoice.then((choiceResult) => {
    if (choiceResult.outcome === 'accepted') {
      console.log('✅ User accepted PWA install');
    } else {
      console.log('❌ User dismissed PWA install');
      localStorage.setItem('pwa-dismissed', 'true');
    }
    deferredPrompt = null;
  });
}

function showInstallBanner() {
  const banner = document.createElement('div');
  banner.id = 'pwa-install-banner';
  banner.innerHTML = `
    <div style="
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: var(--bg-secondary);
      border: 1px solid var(--accent-primary);
      border-radius: 12px;
      padding: 16px 24px;
      box-shadow: var(--shadow-lg);
      z-index: 10000;
      display: flex;
      align-items: center;
      gap: 16px;
      max-width: 90%;
      animation: slideUp 0.3s ease;
    ">
      <div style="font-size: 24px;">🚀</div>
      <div style="flex: 1;">
        <div style="font-weight: 600; margin-bottom: 4px;">Install BotV2</div>
        <div style="font-size: 12px; color: var(--text-secondary);">Get quick access from your home screen</div>
      </div>
      <button onclick="installPWA()" style="
        padding: 8px 16px;
        background: var(--accent-primary);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
      ">Install</button>
      <button onclick="dismissInstallBanner()" style="
        padding: 8px;
        background: transparent;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        font-size: 20px;
      ">×</button>
    </div>
  `;
  
  document.body.appendChild(banner);
}

function dismissInstallBanner() {
  const banner = document.getElementById('pwa-install-banner');
  if (banner) banner.remove();
  localStorage.setItem('pwa-dismissed', 'true');
}

window.installPWA = showInstallPrompt;

// ==================== UPDATE NOTIFICATION ====================
function showUpdateNotification() {
  if (typeof showToast === 'function') {
    showToast('New version available! Refresh to update.', 'info');
  }
  
  // Show persistent update banner
  const updateBanner = document.createElement('div');
  updateBanner.innerHTML = `
    <div style="
      position: fixed;
      top: 70px;
      right: 24px;
      background: var(--accent-primary);
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      box-shadow: var(--shadow-lg);
      z-index: 10000;
      display: flex;
      align-items: center;
      gap: 12px;
    ">
      <span>New version available!</span>
      <button onclick="updatePWA()" style="
        padding: 6px 12px;
        background: white;
        color: var(--accent-primary);
        border: none;
        border-radius: 4px;
        font-weight: 600;
        cursor: pointer;
      ">Update</button>
    </div>
  `;
  
  document.body.appendChild(updateBanner);
}

window.updatePWA = function() {
  if (swRegistration && swRegistration.waiting) {
    swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
    window.location.reload();
  }
};

// ==================== OFFLINE/ONLINE STATUS ====================
window.addEventListener('online', () => {
  console.log('🌐 Back online');
  if (typeof showToast === 'function') {
    showToast('Connection restored', 'success');
  }
});

window.addEventListener('offline', () => {
  console.log('📡 Offline mode');
  if (typeof showToast === 'function') {
    showToast('You are offline. Some features may be limited.', 'warning');
  }
});

// ==================== STANDALONE DETECTION ====================
if (window.matchMedia('(display-mode: standalone)').matches) {
  console.log('✅ Running as PWA');
  document.documentElement.classList.add('pwa-mode');
} else {
  console.log('🌐 Running in browser');
}

console.log('✅ PWA Installer v1.0 loaded');
