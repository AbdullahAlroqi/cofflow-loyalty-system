const CACHE_NAME = 'cofflow-v1.0.0';
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
];

// Install Event - Cache resources
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching files');
        return cache.addAll(urlsToCache.map(url => new Request(url, { cache: 'reload' })))
          .catch(err => {
            console.warn('Service Worker: Some resources failed to cache', err);
          });
      })
      .then(() => self.skipWaiting())
  );
});

// Activate Event - Clean old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Deleting old cache', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event - Network First, falling back to cache
self.addEventListener('fetch', (event) => {
  const { request } = event;
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // For API calls and dynamic content, use network first strategy
  if (request.url.includes('/api/') || 
      request.url.includes('/admin/') || 
      request.url.includes('/employee/') || 
      request.url.includes('/customer/') ||
      request.url.includes('/login') ||
      request.url.includes('/logout')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Clone response before caching
          const responseClone = response.clone();
          if (response.status === 200) {
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // If network fails, try cache
          return caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // Return offline page for navigation requests
            if (request.mode === 'navigate') {
              return caches.match('/');
            }
          });
        })
    );
    return;
  }

  // For static assets, use cache first strategy
  event.respondWith(
    caches.match(request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(request).then((response) => {
          // Don't cache non-successful responses
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }
          // Clone and cache the response
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseToCache);
          });
          return response;
        });
      })
      .catch(() => {
        // Return a fallback for images
        if (request.destination === 'image') {
          return new Response(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">☕</text></svg>',
            { headers: { 'Content-Type': 'image/svg+xml' } }
          );
        }
      })
  );
});

// Background Sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Syncing data...');
  if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});

async function syncData() {
  // Implement your sync logic here
  console.log('Service Worker: Data synced');
}

// Push Notifications
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push notification received');
  
  let notificationData = {};
  
  // محاولة تحليل البيانات المستلمة كـ JSON
  try {
    if (event.data) {
      notificationData = event.data.json();
    }
  } catch (e) {
    console.error('Service Worker: Push notification JSON parsing error', e);
    // إذا لم يكن من الممكن تحليل البيانات كـ JSON، استخدم النص العادي
    notificationData = {
      title: 'COFFLOW',
      body: event.data ? event.data.text() : 'إشعار جديد من COFFLOW',
      type: 'default'
    };
  }
  
  // تكوين خيارات الإشعار
  const options = {
    body: notificationData.body || 'إشعار جديد من COFFLOW',
    icon: notificationData.image || '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    image: notificationData.image || null,
    vibrate: [200, 100, 200, 100, 200],
    tag: `cofflow-notification-${notificationData.id || Date.now()}`,
    data: notificationData,
    requireInteraction: true,
    actions: [],
    dir: 'rtl',
    lang: 'ar',
    renotify: true
  };
  
  // إضافة إجراءات بناءً على نوع الإشعار
  if (notificationData.type === 'promotion') {
    options.actions = [
      {
        action: 'view-promotion',
        title: 'عرض العرض'
      },
      {
        action: 'dismiss',
        title: 'إغلاق'
      }
    ];
    // إضافة لون خاص للعروض
    options.badge = '/static/icons/promo-badge.png';
  } else if (notificationData.type === 'alert') {
    options.actions = [
      {
        action: 'view-alert',
        title: 'عرض التفاصيل'
      }
    ];
    // إعادة الإشعار للتنبيهات الهامة
    options.renotify = true;
    options.requireInteraction = true;
  }
  
  // إظهار الإشعار
  event.waitUntil(
    self.registration.showNotification(notificationData.title || 'COFFLOW', options)
      .then(() => {
        console.log('Service Worker: Push notification displayed');
        // إرسال تأكيد للخادم بأن الإشعار تم عرضه
        if (notificationData.id) {
          return fetch('/api/notifications/confirm-delivery', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notification_id: notificationData.id })
          }).catch(err => console.warn('Failed to confirm notification delivery', err));
        }
      })
  );
});

// Notification Click
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification clicked', event.notification.tag);
  
  // إغلاق الإشعار
  event.notification.close();
  
  const notificationData = event.notification.data || {};
  let urlToOpen = '/';
  
  // التعامل مع الإجراء المحدد
  if (event.action === 'view-promotion' && notificationData.action) {
    urlToOpen = notificationData.action;
  } else if (event.action === 'view-alert' && notificationData.action) {
    urlToOpen = notificationData.action;
  } else if (!event.action && notificationData.action) {
    // إذا تم النقر على الإشعار نفسه وليس على زر
    urlToOpen = notificationData.action;
  }
  
  event.waitUntil(
    // التحقق من فتح نافذة موجودة مسبقًا
    clients.matchAll({ type: 'window' })
      .then(windowClients => {
        // إذا كانت هناك نافذة مفتوحة، استخدمها
        for (let i = 0; i < windowClients.length; i++) {
          const client = windowClients[i];
          if (client.url.includes(self.registration.scope) && 'focus' in client) {
            // التركيز على النافذة الموجودة
            return client.focus().then(focusedClient => {
              if (focusedClient && urlToOpen !== '/') {
                // توجيه النافذة إلى الرابط المطلوب
                return focusedClient.navigate(urlToOpen);
              }
            });
          }
        }
        
        // إذا لم تكن هناك نوافذ مفتوحة، افتح نافذة جديدة
        return clients.openWindow(urlToOpen);
      })
      .then(() => {
        // إرسال تأكيد بأن المستخدم قد نقر على الإشعار
        if (notificationData.id) {
          return fetch('/api/notifications/mark-read', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              notification_id: notificationData.id,
              action: event.action || 'click'
            })
          }).catch(err => console.warn('Failed to mark notification as read', err));
        }
      })
  );
});

// إغلاق الإشعار
self.addEventListener('notificationclose', (event) => {
  console.log('Service Worker: Notification closed', event.notification.tag);
  
  const notificationData = event.notification.data || {};
  
  // إذا كان هناك معرف للإشعار، قم بتحديث الخادم
  if (notificationData.id) {
    fetch('/api/notifications/dismissed', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notification_id: notificationData.id })
    }).catch(err => console.warn('Failed to report notification dismiss', err));
  }
});
