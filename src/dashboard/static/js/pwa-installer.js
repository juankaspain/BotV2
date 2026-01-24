// ==================== PWA Installer v1.1 - ENABLED ====================
// ✅ Service Worker now at root: /sw.js (scope='/')
// Professional PWA installation handler
// Author: Juan Carlos Garcia
// Date: 24-01-2026

let deferredPrompt = null;

// ==================== SERVICE WORKER REGISTRATION ====================
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      });
      
      console.log('✅ Service Worker registered successfully');
      console.log('Scope:', registration.scope);
      console.log('State:', registration.installing ? 'installing' : registration.waiting ? 'waiting' : registration.active ? 'active' : 'unknown');
      
      // Check for updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        console.log('🔄 Service Worker update found');
        
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            console.log('✅ New Service Worker installed - refresh to activate');
          }
        });
      });
      
    } catch (error) {
      console.error('❌ Service Worker registration failed:', error);
      console.error('Error details:', {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
    }
  });
}

// ==================== INSTALL PROMPT HANDLER ====================
window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent Chrome 67 and earlier from automatically showing the prompt
  e.preventDefault();
  // Stash the event so it can be triggered later
  deferredPrompt = e;
  console.log('💾 PWA Install prompt available');
  console.log('User can now install the app');
});

// ==================== APP INSTALLED HANDLER ====================
window.addEventListener('appinstalled', () => {
  console.log('✅ PWA installed successfully');
  deferredPrompt = null;
});

// ==================== INSTALL FUNCTION ====================
// Can be called from UI button: installPWA()
window.installPWA = async function() {
  if (!deferredPrompt) {
    console.warn('⚠️ Install prompt not available');
    return false;
  }
  
  try {
    // Show the install prompt
    deferredPrompt.prompt();
    
    // Wait for the user to respond to the prompt
    const { outcome } = await deferredPrompt.userChoice;
    console.log(`User response: ${outcome}`);
    
    // Clear the deferredPrompt
    deferredPrompt = null;
    
    return outcome === 'accepted';
  } catch (error) {
    console.error('❌ PWA installation failed:', error);
    return false;
  }
};

// ==================== CHECK PWA STATUS ====================
window.isPWAInstalled = function() {
  // Check if running in standalone mode (installed PWA)
  return window.matchMedia('(display-mode: standalone)').matches || 
         window.navigator.standalone === true;
};

// ==================== STARTUP LOG ====================
console.log('🚀 PWA Installer v1.1 loaded');
console.log('PWA Installed:', window.isPWAInstalled());
console.log('Service Worker Support:', 'serviceWorker' in navigator);

// Log status after 2 seconds
setTimeout(() => {
  if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
    console.log('✅ Service Worker is controlling the page');
    console.log('Scope:', navigator.serviceWorker.controller.scriptURL);
  } else {
    console.log('⚠️ Service Worker not yet controlling the page');
  }
}, 2000);
