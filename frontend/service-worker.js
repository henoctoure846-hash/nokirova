// 🌸 NOKIROVA Service Worker

const CACHE_NAME = 'nokirova-v1';
const FILES_TO_CACHE = [
    '/',
    '/index.html',
    '/style.css',
    '/app.js',
    '/manifest.json'
];

// Installation
self.addEventListener('install', (event) => {
    console.log('🌸 NOKIROVA Service Worker : installation');
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(FILES_TO_CACHE);
        })
    );
    self.skipWaiting();
});

// Activation
self.addEventListener('activate', (event) => {
    console.log('🌸 NOKIROVA Service Worker : activation');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Récupération des fichiers
self.addEventListener('fetch', (event) => {
    // Ne pas cacher les requêtes API (elles vont sur Render)
    if (event.request.url.includes('/api/')) {
        return;
    }

    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});