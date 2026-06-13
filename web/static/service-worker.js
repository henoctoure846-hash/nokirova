// 🌸 NOKIROVA Service Worker
const CACHE = 'nokirova-v1';
const URLS = [
  '/',
  '/static/css/style.css',
  '/static/js/script.js',
  '/logo'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(URLS))
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    fetch(e.request).catch(() =>
      caches.match(e.request)
    )
  );
});