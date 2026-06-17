// ═══════════════════════════════════════════
// 🌸 NOKIROVA Service Worker – CORRIGÉ (cache pages désactivé)
// ═══════════════════════════════════════════

const CACHE = 'nokirova-v4';          // on change le nom pour forcer un cache propre
const STATIC_ASSETS = [               // on ne met QUE les ressources statiques en cache
  '/static/css/style.css',
  '/static/js/script.js',
  '/logo'
];

// ═══════════════════════════════════════════
// 📦 INSTALLATION – cache uniquement les statiques
// ═══════════════════════════════════════════
self.addEventListener('install', e => {
  console.log('🌸 NOKIROVA SW installé !');
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// ═══════════════════════════════════════════
// 🧹 ACTIVATION – nettoyage des anciens caches
// ═══════════════════════════════════════════
self.addEventListener('activate', e => {
  console.log('✅ NOKIROVA SW activé !');
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// ═══════════════════════════════════════════
// 🌐 FETCH – stratégie « réseau d’abord »
// ═══════════════════════════════════════════
self.addEventListener('fetch', e => {
  // Pour les fichiers statiques, essayer le cache puis le réseau
  if (e.request.url.includes('/static/') || e.request.url.endsWith('/logo')) {
    e.respondWith(
      caches.match(e.request).then(cachedResponse =>
        cachedResponse || fetch(e.request)
      )
    );
  } else {
    // Pour tout le reste (pages HTML, API…) → réseau uniquement
    e.respondWith(fetch(e.request));
  }
});

// ═══════════════════════════════════════════
// 🔔 PUSH NOTIFICATIONS (inchangé)
// ═══════════════════════════════════════════
self.addEventListener('push', e => {
  console.log('📬 Notification reçue !', e);
  let data = {
    title: '🌸 NOKIROVA',
    body: 'Ton professeur IA t\'attend ! 💪',
    icon: '/logo',
    badge: '/logo'
  };
  if (e.data) {
    try { data = e.data.json(); } catch(err) { data.body = e.data.text(); }
  }
  e.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: data.icon || '/logo',
      badge: data.badge || '/logo',
      vibrate: [200, 100, 200],
      tag: 'nokirova-notif',
      renotify: true,
      data: { url: data.url || '/' }
    })
  );
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  const url = e.notification.data?.url || '/';
  e.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(clientList => {
        for (let client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.navigate(url);
            return client.focus();
          }
        }
        if (clients.openWindow) return clients.openWindow(url);
      })
  );
});

self.addEventListener('sync', e => {
  if (e.tag === 'rappel-etude') e.waitUntil(envoyerRappel());
});

async function envoyerRappel() {
  const messages = [
    { title: '📚 C\'est l\'heure d\'étudier !', body: 'Ouvre NOKIROVA et révise 10 min ! 💪' },
    { title: '🎯 Objectif du jour !', body: 'Fais un QCM pour tester tes connaissances ! 🔥' },
    { title: '🌸 NOKIROVA t\'attend !', body: 'Tes flashcards sont prêtes ! On révise ? 😊' },
    { title: '⏱️ Pomodoro time !', body: '25 minutes de focus = 1 succès de plus ! 💎' },
    { title: '📝 Résumé rapide ?', body: 'Fais résumer ton cours par l\'IA ! ✨' }
  ];
  const msg = messages[Math.floor(Math.random() * messages.length)];
  return self.registration.showNotification(msg.title, {
    body: msg.body,
    icon: '/logo',
    badge: '/logo',
    vibrate: [200, 100, 200],
    tag: 'nokirova-rappel',
    data: { url: '/' }
  });
}