// ═══════════════════════════════════════════
// 🌸 NOKIROVA Service Worker - PHASE C
// ═══════════════════════════════════════════

const CACHE = 'nokirova-v2';
const URLS = [
  '/',
  '/static/css/style.css',
  '/static/js/script.js',
  '/logo'
];

// ═══════════════════════════════════════════
// 📦 INSTALLATION + CACHE
// ═══════════════════════════════════════════

self.addEventListener('install', e => {
  console.log('🌸 NOKIROVA SW installé !');
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(URLS))
  );
  self.skipWaiting();
});

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
// 🌐 FETCH (cache + réseau)
// ═══════════════════════════════════════════

self.addEventListener('fetch', e => {
  e.respondWith(
    fetch(e.request).catch(() =>
      caches.match(e.request)
    )
  );
});

// ═══════════════════════════════════════════
// 🔔 RECEVOIR UNE NOTIFICATION PUSH
// ═══════════════════════════════════════════

self.addEventListener('push', e => {
  console.log('📬 Notification reçue !', e);

  let data = {
    title: '🌸 NOKIROVA',
    body: 'Ton professeur IA t\'attend ! 💪',
    icon: '/logo',
    badge: '/logo'
  };

  // Si le serveur envoie des données
  if (e.data) {
    try {
      data = e.data.json();
    } catch(err) {
      data.body = e.data.text();
    }
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

// ═══════════════════════════════════════════
// 👆 CLIC SUR UNE NOTIFICATION
// ═══════════════════════════════════════════

self.addEventListener('notificationclick', e => {
  console.log('👆 Notification cliquée !');
  e.notification.close();

  const url = e.notification.data?.url || '/';

  e.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(clientList => {
        // Si l'app est déjà ouverte → focus
        for (let client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.navigate(url);
            return client.focus();
          }
        }
        // Sinon → ouvrir l'app
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
  );
});

// ═══════════════════════════════════════════
// ⏰ NOTIFICATIONS PROGRAMMÉES (Background Sync)
// ═══════════════════════════════════════════

self.addEventListener('sync', e => {
  if (e.tag === 'rappel-etude') {
    e.waitUntil(envoyerRappel());
  }
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