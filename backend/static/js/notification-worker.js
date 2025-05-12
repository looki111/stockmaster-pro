/**
 * Service Worker for Push Notifications
 * Handles background notifications for StockMaster Pro
 */

// Cache name for offline support
const CACHE_NAME = 'stockmaster-cache-v1';

// Files to cache for offline access
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/images/logo.png',
  '/static/sounds/notification-soft.mp3',
  '/static/sounds/notification-order.mp3',
  '/static/sounds/notification-alert.mp3',
  '/static/sounds/notification-cash.mp3'
];

// Install event - cache assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - serve from cache if available
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});

// Push event - handle incoming push notifications
self.addEventListener('push', event => {
  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = {
        title: 'New Notification',
        message: event.data.text(),
        icon: '/static/images/logo.png',
        badge: '/static/images/badge.png',
        url: '/'
      };
    }
  }

  const title = data.title || 'StockMaster Pro';
  const options = {
    body: data.message || 'You have a new notification',
    icon: data.icon || '/static/images/logo.png',
    badge: data.badge || '/static/images/badge.png',
    data: {
      url: data.url || '/'
    },
    vibrate: [100, 50, 100],
    timestamp: data.timestamp || Date.now(),
    actions: [
      {
        action: 'view',
        title: 'View'
      },
      {
        action: 'close',
        title: 'Close'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Notification click event - handle notification clicks
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'close') {
    return;
  }

  // Default action is to open the app
  const urlToOpen = event.notification.data.url || '/';

  event.waitUntil(
    clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    })
    .then(windowClients => {
      // Check if there is already a window/tab open with the target URL
      for (let i = 0; i < windowClients.length; i++) {
        const client = windowClients[i];
        // If so, focus it
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus();
        }
      }
      // If not, open a new window/tab
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

// Sync event - handle background sync
self.addEventListener('sync', event => {
  if (event.tag === 'sync-notifications') {
    event.waitUntil(
      // Sync logic here
      fetch('/api/notifications/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include'
      })
      .then(response => response.json())
      .then(data => {
        if (data.notifications && data.notifications.length > 0) {
          return Promise.all(
            data.notifications.map(notification => {
              return self.registration.showNotification(
                notification.title, 
                {
                  body: notification.message,
                  icon: '/static/images/logo.png',
                  badge: '/static/images/badge.png',
                  data: {
                    url: notification.url || '/',
                    id: notification.id
                  }
                }
              );
            })
          );
        }
      })
    );
  }
});

// Message event - handle messages from the main thread
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
