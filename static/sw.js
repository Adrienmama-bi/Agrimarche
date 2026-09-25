/**
 * Service Worker AgriMarché
 * Gère le cache hors ligne et les notifications push
 */

const CACHE_NAME = 'agrimarche-v1';
const CACHE_STATIQUE = 'agrimarche-static-v1';
const CACHE_DYNAMIQUE = 'agrimarche-dynamic-v1';

// Ressources à mettre en cache immédiatement au premier chargement
const RESSOURCES_STATIQUES = [
  '/',
  '/produits/catalogue/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  // Page hors ligne de secours
  '/hors-ligne/',
];

// URLs qu'on ne met jamais en cache
const EXCLUSIONS_CACHE = [
  '/admin/',
  '/rosetta/',
  '/accounts/connexion/',
  '/accounts/inscription/',
  '/accounts/deconnexion/',
  '/assistant/position/maj/',
  '/livraisons/',
];

// ============================================================
// INSTALLATION — Mise en cache des ressources statiques
// ============================================================
self.addEventListener('install', function(event) {
  console.log('[SW AgriMarché] Installation...');
  event.waitUntil(
    caches.open(CACHE_STATIQUE).then(function(cache) {
      console.log('[SW AgriMarché] Mise en cache des ressources statiques');
      return cache.addAll(RESSOURCES_STATIQUES).catch(function(err) {
        console.warn('[SW AgriMarché] Certaines ressources non cachées :', err);
      });
    })
  );
  self.skipWaiting();
});

// ============================================================
// ACTIVATION — Nettoyage des anciens caches
// ============================================================
self.addEventListener('activate', function(event) {
  console.log('[SW AgriMarché] Activation...');
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames
          .filter(function(name) {
            return name !== CACHE_STATIQUE && name !== CACHE_DYNAMIQUE;
          })
          .map(function(name) {
            console.log('[SW AgriMarché] Suppression ancien cache :', name);
            return caches.delete(name);
          })
      );
    })
  );
  self.clients.claim();
});

// ============================================================
// FETCH — Stratégie de cache intelligente
// ============================================================
self.addEventListener('fetch', function(event) {
  const url = new URL(event.request.url);

  // Ignorer les requêtes non-GET
  if (event.request.method !== 'GET') return;

  // Ignorer les URLs exclues
  const estExclu = EXCLUSIONS_CACHE.some(function(excl) {
    return url.pathname.startsWith(excl);
  });
  if (estExclu) return;

  // Ignorer les requêtes externes (OpenStreetMap, CDN...)
  if (url.origin !== location.origin) return;

  // Stratégie selon le type de ressource
  if (_estRessourceStatique(url.pathname)) {
    // Cache First pour CSS, JS, images statiques
    event.respondWith(_strategieCacheFirst(event.request));
  } else if (_estPageHtml(event.request)) {
    // Network First pour les pages HTML
    event.respondWith(_strategieNetworkFirst(event.request));
  } else {
    // Stale While Revalidate pour le reste
    event.respondWith(_strategieStaleWhileRevalidate(event.request));
  }
});

function _estRessourceStatique(pathname) {
  return pathname.startsWith('/static/') || pathname.startsWith('/media/');
}

function _estPageHtml(request) {
  return request.headers.get('accept') &&
    request.headers.get('accept').includes('text/html');
}

// Cache First : retourne depuis le cache, sinon réseau
async function _strategieCacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_STATIQUE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    return new Response('Ressource non disponible hors ligne.', { status: 503 });
  }
}

// Network First : réseau d'abord, cache en fallback
async function _strategieNetworkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_DYNAMIQUE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    // Hors ligne — chercher dans le cache
    const cached = await caches.match(request);
    if (cached) return cached;

    // Page de fallback hors ligne
    const offlinePage = await caches.match('/hors-ligne/');
    if (offlinePage) return offlinePage;

    return new Response(
      `<!DOCTYPE html>
      <html lang="fr">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hors ligne — AgriMarché</title>
        <style>
          body { font-family: sans-serif; background: #0B1F0E; color: white;
                 display: flex; align-items: center; justify-content: center;
                 min-height: 100vh; margin: 0; text-align: center; padding: 20px; }
          .icon { font-size: 80px; margin-bottom: 20px; }
          h1 { color: #7AE600; font-size: 28px; margin-bottom: 10px; }
          p { color: rgba(255,255,255,0.6); font-size: 16px; margin-bottom: 24px; }
          button { background: #7AE600; color: #0B1F0E; border: none; padding: 14px 28px;
                   border-radius: 8px; font-size: 15px; font-weight: 700; cursor: pointer; }
        </style>
      </head>
      <body>
        <div>
          <div class="icon">🌿</div>
          <h1>Vous êtes hors ligne</h1>
          <p>Vérifiez votre connexion internet<br>pour continuer à utiliser AgriMarché.</p>
          <button onclick="location.reload()">Réessayer</button>
        </div>
      </body>
      </html>`,
      { headers: { 'Content-Type': 'text/html; charset=utf-8' }, status: 503 }
    );
  }
}

// Stale While Revalidate : retourne le cache et met à jour en arrière-plan
async function _strategieStaleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_DYNAMIQUE);
  const cached = await cache.match(request);

  const fetchPromise = fetch(request).then(function(response) {
    if (response.ok) cache.put(request, response.clone());
    return response;
  }).catch(function() { return cached; });

  return cached || fetchPromise;
}

// ============================================================
// NOTIFICATIONS PUSH
// ============================================================
self.addEventListener('push', function(event) {
  if (!event.data) return;

  let data;
  try {
    data = event.data.json();
  } catch(e) {
    data = {
      title: 'AgriMarché',
      body: event.data.text(),
      icon: '/static/icons/icon-192x192.png',
    };
  }

  const options = {
    body: data.body || '',
    icon: data.icon || '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: { url: data.url || '/' },
    actions: data.actions || [],
    tag: data.tag || 'agrimarche-notif',
    renotify: true,
  };

  event.waitUntil(
    self.registration.showNotification(data.title || 'AgriMarché', options)
  );
});

// Clic sur une notification → ouvrir la bonne page
self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  const url = event.notification.data && event.notification.data.url
    ? event.notification.data.url
    : '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(function(clientList) {
        for (const client of clientList) {
          if (client.url === url && 'focus' in client) {
            return client.focus();
          }
        }
        if (clients.openWindow) return clients.openWindow(url);
      })
  );
});

// ============================================================
// SYNCHRONISATION EN ARRIÈRE-PLAN
// ============================================================
self.addEventListener('sync', function(event) {
  if (event.tag === 'sync-position-gps') {
    event.waitUntil(_syncPositionGPS());
  }
});

async function _syncPositionGPS() {
  // Synchroniser les positions GPS en attente quand la connexion revient
  console.log('[SW AgriMarché] Synchronisation GPS en cours...');
}