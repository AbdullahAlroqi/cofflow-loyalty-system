// PWA Installation and Service Worker Registration

let deferredPrompt;
let installButton;

// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    // أولًا: تصحيح المسار ليكون في الجذر
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('✅ Service Worker registered successfully:', registration.scope);
        
        // تسجيل Service Worker في وحدة التحكم للتصحيح
        console.info('🔍 PWA Debug: Service Worker scope:', registration.scope);
        
        // التحقق من تفعيل Service Worker
        if (registration.active) {
          console.info('🔍 PWA Debug: Service Worker is active');
        }
        
        // Check for updates periodically
        setInterval(() => {
          registration.update().then(() => {
            console.info('🔄 Service Worker update check completed');
          }).catch(err => {
            console.warn('⚠️ Service Worker update failed:', err);
          });
        }, 60000); // Check every minute
      })
      .catch((error) => {
        console.error('❌ Service Worker registration failed:', error);
        // إضافة تفاصيل أكثر للخطأ
        console.warn('⚠️ PWA Debug: Service Worker path: /sw.js');
        console.warn('⚠️ PWA Debug: Check console for HTTPS requirements');
      });
  });
}

// Handle PWA Install Prompt
window.addEventListener('beforeinstallprompt', (e) => {
  console.log('⬇️ PWA Install prompt triggered');
  // Prevent the mini-infobar from appearing on mobile
  e.preventDefault();
  // Stash the event so it can be triggered later
  deferredPrompt = e;
  // Show install button
  showInstallButton();
});

// Show Install Button
function showInstallButton() {
  installButton = document.getElementById('pwa-install-btn');
  if (installButton) {
    installButton.style.display = 'block';
    installButton.addEventListener('click', installPWA);
  } else {
    // Create install button if not exists
    createInstallButton();
  }
}

// Create Install Button
function createInstallButton() {
  const button = document.createElement('button');
  button.id = 'pwa-install-btn';
  button.className = 'pwa-install-button';
  button.innerHTML = '<i class="fas fa-download"></i> تثبيت التطبيق';
  button.addEventListener('click', installPWA);
  document.body.appendChild(button);
}

// Install PWA
async function installPWA() {
  if (!deferredPrompt) {
    return;
  }
  
  // Show the install prompt
  deferredPrompt.prompt();
  
  // Wait for the user to respond to the prompt
  const { outcome } = await deferredPrompt.userChoice;
  
  console.log(`User response to install prompt: ${outcome}`);
  
  if (outcome === 'accepted') {
    console.log('✅ User accepted the install prompt');
    hideInstallButton();
  } else {
    console.log('❌ User dismissed the install prompt');
  }
  
  // Clear the deferredPrompt
  deferredPrompt = null;
}

// Hide Install Button
function hideInstallButton() {
  if (installButton) {
    installButton.style.display = 'none';
  }
}

// Track PWA Installation
window.addEventListener('appinstalled', (evt) => {
  console.log('✅ PWA was installed successfully');
  hideInstallButton();
  
  // Send analytics or show thank you message
  showNotification('تم التثبيت بنجاح!', 'يمكنك الآن استخدام التطبيق من الشاشة الرئيسية');
});

// Check if app is running in standalone mode (installed)
function isStandalone() {
  return (window.matchMedia('(display-mode: standalone)').matches) || 
         (window.navigator.standalone) || 
         document.referrer.includes('android-app://');
}

// Show notification when running as PWA
if (isStandalone()) {
  console.log('🚀 Running as installed PWA');
  // Hide install button if already installed
  hideInstallButton();
}

// Show notification function
function showNotification(title, body) {
  if ('Notification' in window && Notification.permission === 'granted') {
    navigator.serviceWorker.ready.then((registration) => {
      registration.showNotification(title, {
        body: body,
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-72x72.png',
        vibrate: [200, 100, 200],
        dir: 'rtl',
        lang: 'ar'
      });
    });
  }
}

// Request notification permission
function requestNotificationPermission() {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission().then((permission) => {
      if (permission === 'granted') {
        console.log('✅ Notification permission granted');
      }
    });
  }
}

// Check for updates
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    console.log('🔄 New Service Worker activated, reloading page...');
    window.location.reload();
  });
}

// Online/Offline detection
window.addEventListener('online', () => {
  console.log('🌐 Back online');
  showStatusMessage('تم استعادة الاتصال بالإنترنت', 'success');
});

window.addEventListener('offline', () => {
  console.log('📵 Offline');
  showStatusMessage('لا يوجد اتصال بالإنترنت - الوضع غير متصل', 'warning');
});

// Show status message
function showStatusMessage(message, type) {
  const alert = document.createElement('div');
  alert.className = `alert alert-${type} alert-dismissible fade show pwa-status-alert`;
  alert.innerHTML = `
    <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  
  const container = document.querySelector('.container');
  if (container) {
    container.insertBefore(alert, container.firstChild);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
      alert.remove();
    }, 5000);
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  // Request notification permission after user interaction
  setTimeout(() => {
    if (isStandalone()) {
      requestNotificationPermission();
    }
  }, 5000);
});

// CSS for install button (injected)
const style = document.createElement('style');
style.textContent = `
  .pwa-install-button {
    position: fixed;
    bottom: 20px;
    left: 20px;
    background: linear-gradient(135deg, #8B4513 0%, #514f4b 100%);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 25px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(139, 69, 19, 0.4);
    z-index: 9999;
    transition: all 0.3s ease;
    display: none;
    font-family: 'Cairo', sans-serif;
  }
  
  .pwa-install-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(139, 69, 19, 0.6);
  }
  
  .pwa-install-button i {
    margin-left: 8px;
  }
  
  .pwa-status-alert {
    position: fixed;
    top: 80px;
    right: 20px;
    left: 20px;
    z-index: 9998;
    animation: slideDown 0.3s ease;
    max-width: 500px;
    margin: 0 auto;
  }
  
  @keyframes slideDown {
    from {
      transform: translateY(-100%);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
  
  @media (max-width: 768px) {
    .pwa-install-button {
      bottom: 10px;
      left: 10px;
      right: 10px;
      text-align: center;
      padding: 15px;
    }
  }
`;
document.head.appendChild(style);
