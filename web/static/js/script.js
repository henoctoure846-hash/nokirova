// ═══════════════════════════════════════════
// 🌸 NOKIROVA WEB - JAVASCRIPT PHASE C
// ═══════════════════════════════════════════

console.log("🌸 NOKIROVA WEB chargée !");

// ═══════════════════════════════════════════
// 🔔 SYSTÈME DE NOTIFICATIONS
// ═══════════════════════════════════════════

// Messages de motivation aléatoires
const MESSAGES_NOTIF = [
  { title: '📚 C\'est l\'heure d\'étudier !', body: 'Ouvre NOKIROVA et révise 10 min ! 💪', url: '/' },
  { title: '🎯 Objectif du jour !', body: 'Fais un QCM pour tester tes connaissances ! 🔥', url: '/qcm' },
  { title: '🌸 NOKIROVA t\'attend !', body: 'Tes flashcards sont prêtes ! On révise ? 😊', url: '/flashcards' },
  { title: '⏱️ Pomodoro time !', body: '25 minutes de focus = 1 succès de plus ! 💎', url: '/pomodoro' },
  { title: '📝 Résumé rapide ?', body: 'Fais résumer ton cours par l\'IA ! ✨', url: '/resume' },
  { title: '💬 Pose une question !', body: 'L\'IA est là pour t\'expliquer ! 🤖', url: '/chat' },
  { title: '🏆 Tu peux le faire !', body: 'Chaque minute d\'étude = un pas vers la réussite ! 🌟', url: '/' }
];

// ─────────────────────────────────────────
// Demander permission notifications
// ─────────────────────────────────────────

async function demanderPermissionNotifications() {
  // Vérifier si les notifications sont supportées
  if (!('Notification' in window)) {
    console.log('❌ Notifications non supportées');
    return false;
  }

  // Déjà accordée
  if (Notification.permission === 'granted') {
    console.log('✅ Permission déjà accordée');
    activerNotifications();
    return true;
  }

  // Déjà refusée
  if (Notification.permission === 'denied') {
    console.log('❌ Permission refusée');
    return false;
  }

  // Demander la permission
  const permission = await Notification.requestPermission();

  if (permission === 'granted') {
    console.log('✅ Permission accordée !');
    afficherToast('🔔 Notifications activées ! Tu recevras des rappels d\'étude 💪', 'success');
    activerNotifications();
    return true;
  } else {
    console.log('❌ Permission refusée par l\'utilisateur');
    afficherToast('😢 Sans notifications, pense à revenir étudier !', 'warning');
    return false;
  }
}

// ─────────────────────────────────────────
// Envoyer une notification locale
// ─────────────────────────────────────────

function envoyerNotification(title, body, url = '/') {
  if (Notification.permission !== 'granted') return;

  const notif = new Notification(title, {
    body: body,
    icon: '/logo',
    badge: '/logo',
    vibrate: [200, 100, 200],
    tag: 'nokirova-' + Date.now()
  });

  // Clic → ouvrir la page
  notif.onclick = () => {
    window.focus();
    window.location.href = url;
    notif.close();
  };

  // Fermer après 8 secondes
  setTimeout(() => notif.close(), 8000);
}

// ─────────────────────────────────────────
// Activer les rappels automatiques
// ─────────────────────────────────────────

function activerNotifications() {
  // Vérifier si déjà activé
  if (localStorage.getItem('notif_activees') === 'oui') {
    planifierProchainRappel();
    return;
  }

  localStorage.setItem('notif_activees', 'oui');

  // Notif de bienvenue immédiate
  setTimeout(() => {
    envoyerNotification(
      '🎉 Notifications activées !',
      'Tu recevras des rappels pour étudier ! 💪🌸',
      '/'
    );
  }, 2000);

  // Planifier le prochain rappel
  planifierProchainRappel();
}

// ─────────────────────────────────────────
// Planifier rappels automatiques
// ─────────────────────────────────────────

function planifierProchainRappel() {
  // Rappel toutes les 3 heures (en millisecondes)
  const INTERVALLE = 3 * 60 * 60 * 1000; // 3 heures

  // Calculer le temps jusqu'au prochain rappel
  const dernierRappel = parseInt(localStorage.getItem('dernier_rappel') || '0');
  const maintenant = Date.now();
  const tempsPasse = maintenant - dernierRappel;
  const tempsRestant = Math.max(0, INTERVALLE - tempsPasse);

  console.log(`⏰ Prochain rappel dans ${Math.round(tempsRestant/60000)} minutes`);

  setTimeout(() => {
    envoyerRappelAleatoire();
    planifierProchainRappel(); // Planifier le suivant
  }, tempsRestant);
}

// ─────────────────────────────────────────
// Envoyer un rappel aléatoire
// ─────────────────────────────────────────

function envoyerRappelAleatoire() {
  if (Notification.permission !== 'granted') return;

  const msg = MESSAGES_NOTIF[Math.floor(Math.random() * MESSAGES_NOTIF.length)];
  envoyerNotification(msg.title, msg.body, msg.url);
  localStorage.setItem('dernier_rappel', Date.now().toString());
  console.log('📬 Rappel envoyé !', msg.title);
}

// ─────────────────────────────────────────
// Notification spéciale (utilisée par Pomodoro etc.)
// ─────────────────────────────────────────

function notifierEvenement(type) {
  const evenements = {
    'pomodoro_fin': {
      title: '⏱️ Pomodoro terminé !',
      body: 'Bravo ! Prends une pause de 5 minutes ! 🎉',
      url: '/pomodoro'
    },
    'flashcard_rappel': {
      title: '🃏 Révise tes flashcards !',
      body: 'Tu n\'as pas révisé aujourd\'hui ! 😊',
      url: '/flashcards'
    },
    'objectif_atteint': {
      title: '🏆 Objectif atteint !',
      body: 'Tu as étudié comme prévu ! Continue ! 💎',
      url: '/'
    },
    'nouveau_cours': {
      title: '📚 Nouveau cours importé !',
      body: 'Ton cours est prêt à être analysé par l\'IA ! ✨',
      url: '/bibliotheque'
    }
  };

  const evt = evenements[type];
  if (evt) {
    envoyerNotification(evt.title, evt.body, evt.url);
  }
}

// ═══════════════════════════════════════════
// 🧭 NAVIGATION (clic sur boutons sidebar)
// ═══════════════════════════════════════════

function naviguer(page) {
    console.log(`📍 Navigation vers : ${page}`);

    const pagesDisponibles = {
        'accueil': '🏠 Accueil',
        'bibliotheque': '📚 Bibliothèque',
        'profil': '🏆 Mon Profil',
        'recherche': '🔍 Recherche',
        'historique': '📜 Historique',
        'import': '📥 Importer un cours',
        'ocr': '📸 Scanner image',
        'scan_multi': '📚 Scan Multi-pages',
        'qcm': '🎯 QCM',
        'questions': '❓ Questions de cours',
        'examen': '📚 Exercices examen',
        'flashcards': '🃏 Flashcards',
        'resume': '📝 Résumé',
        'explication': '💡 Explication simple',
        'chat': '💬 Chat IA',
        'audio': '🎧 Audio',
        'traduction': '🌍 Traduction',
        'videos': '🎬 Vidéos révision',
        'medias': '🎵 Mes Médias',
        'planificateur': '📅 Planificateur',
        'pomodoro': '⏱️ Pomodoro',
        'notes': '✍️ Mes Notes',
        'notifications': '🔔 Notifications',
        'graphiques': '📈 Graphiques',
        'themes': '🎨 Thèmes',
        'sonneries': '🔊 Sonneries',
        'pin': '🔒 Sécurité PIN',
        'partage': '🤝 Importer partage',
        'aide': '⌨️ Aide'
    };

    if (page === 'accueil') {
        window.location.href = '/';
        return;
    }

    const nomPage = pagesDisponibles[page] || page;

    document.querySelectorAll('.bouton-sidebar').forEach(btn => {
        btn.classList.remove('actif');
    });

    event.target.classList.add('actif');

    alert(`🚧 Page "${nomPage}" en construction !\n\n✨ Sera disponible dans la Phase 2 ! 🌸`);
}

// ═══════════════════════════════════════════
// 🎨 MODE JOUR/NUIT
// ═══════════════════════════════════════════

document.addEventListener('DOMContentLoaded', function() {
    const boutonMode = document.querySelector('.bouton-mode');
    if (boutonMode) {
        boutonMode.addEventListener('click', function() {
            alert('🌙 Mode jour/nuit bientôt disponible !');
        });
    }
});

// ═══════════════════════════════════════════
// ✨ ANIMATIONS AU CHARGEMENT
// ═══════════════════════════════════════════

document.addEventListener('DOMContentLoaded', function() {

    // ─── Animations cartes stats ───
    const cartesStats = document.querySelectorAll('.carte-stat');
    cartesStats.forEach((carte, index) => {
        carte.style.opacity = '0';
        carte.style.transform = 'translateY(20px)';
        carte.style.transition = 'all 0.5s ease';
        setTimeout(() => {
            carte.style.opacity = '1';
            carte.style.transform = 'translateY(0)';
        }, 100 + (index * 150));
    });

    // ─── Animations cartes rapides ───
    const cartesRapides = document.querySelectorAll('.carte-rapide');
    cartesRapides.forEach((carte, index) => {
        carte.style.opacity = '0';
        carte.style.transform = 'scale(0.9)';
        carte.style.transition = 'all 0.4s ease';
        setTimeout(() => {
            carte.style.opacity = '1';
            carte.style.transform = 'scale(1)';
        }, 500 + (index * 100));
    });

    // ─── Demander permission notifications ───
    // On attend 3 secondes après chargement
    setTimeout(() => {
        demanderPermissionNotifications();
    }, 3000);

    // ─── Si notifs déjà activées → planifier rappels ───
    if (localStorage.getItem('notif_activees') === 'oui') {
        planifierProchainRappel();
    }
});

// ═══════════════════════════════════════════
// 💬 SYSTÈME TOAST (réutilisé partout)
// ═══════════════════════════════════════════

function afficherToast(message, type = 'info') {
    // Supprimer ancien toast
    const ancienToast = document.querySelector('.toast-nokirova');
    if (ancienToast) ancienToast.remove();

    // Couleurs par type
    const couleurs = {
        'success': 'linear-gradient(135deg, #00C853, #7ED321)',
        'error': 'linear-gradient(135deg, #EF4444, #FF6B9D)',
        'warning': 'linear-gradient(135deg, #F59E0B, #FFD93D)',
        'info': 'linear-gradient(135deg, #7B61FF, #2962FF)'
    };

    const toast = document.createElement('div');
    toast.className = 'toast-nokirova';
    toast.innerHTML = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%) translateY(100px);
        background: ${couleurs[type] || couleurs.info};
        color: white;
        padding: 14px 28px;
        border-radius: 50px;
        font-size: 14px;
        font-weight: 600;
        z-index: 99999;
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
        transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        white-space: nowrap;
        max-width: 90vw;
        text-align: center;
    `;

    document.body.appendChild(toast);

    // Animer entrée
    setTimeout(() => {
        toast.style.transform = 'translateX(-50%) translateY(0)';
    }, 10);

    // Animer sortie après 3.5s
    setTimeout(() => {
        toast.style.transform = 'translateX(-50%) translateY(100px)';
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}
 // 📷 SCANNER COPIE MANUSCRITE - Phase D3
const btnScan = document.getElementById('btnScan');
if (btnScan) {
    btnScan.addEventListener('click', () => {
        // Créer input file caché
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.capture = 'environment'; // Ouvre camera sur mobile

        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            // Afficher message utilisateur
            ajouterMessage("📷 J'envoie ma copie à scanner...", 'user');

            // Formulaire pour OCR
            const formData = new FormData();
            formData.append('fichier', file);
            formData.append('langue', 'fra');
            formData.append('expliquer', 'true');

            try {
                const response = await fetch('/api/ocr', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (data.succes && data.texte) {
                    ajouterMessage(`📄 Texte extrait :\n\n${data.texte.substring(0, 500)}${data.texte.length > 500 ? '...' : ''}`, 'ia');

                    if (data.explication) {
                        ajouterMessage(`💡 Explication IA :\n\n${data.explication}`, 'ia');
                        lireVoix(data.explication);
                    } else {
                        // Envoyer à l'IA pour correction
                        envoyerMessage(`Corrige cette copie :\n${data.texte}`);
                    }
                } else {
                    ajouterMessage(`❌ Erreur OCR : ${data.erreur || 'Inconnue'}`, 'ia');
                }
            } catch (err) {
                ajouterMessage(`❌ Erreur : ${err.message}`, 'ia');
            }
        };

        input.click();
    });
}
// ═══════════════════════════════════════════
// 🎯 LOG DE BIENVENUE
// ═══════════════════════════════════════════

console.log("%c🌸 NOKIROVA WEB - PHASE C ✨", "color: #7B61FF; font-size: 20px; font-weight: bold;");
console.log("%cCreated by Hénoc 🌸 2026", "color: #00C853; font-size: 14px; font-style: italic;");