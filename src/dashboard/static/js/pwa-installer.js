// ==================== PWA Installer v1.0 (DISABLED) ====================
// Temporarily disabled due to Service Worker scope issues
// Will be re-enabled after proper configuration

console.log('⚠️ PWA features temporarily disabled');
console.log('🔧 Service Worker configuration needs adjustment');
console.log('🚀 Dashboard functionality not affected');

// Uncomment when SW is properly configured:
/*
let deferredPrompt = null;

if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      });
      console.log('✅ Service Worker registered:', registration.scope);
    } catch (error) {
      console.error('❌ Service Worker registration failed:', error);
    }
  });
}

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  console.log('💾 PWA Install prompt available');
});

window.addEventListener('appinstalled', () => {
  console.log('✅ PWA installed successfully');
});
*/
