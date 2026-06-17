// ═══════════════════════════════════════════
// 🌸 NOKIROVA WEB - JAVASCRIPT VERSION PROFESSIONNELLE
// ═══════════════════════════════════════════

console.log("🌸 NOKIROVA WEB - Version Professionnelle");

// ═══════════════════════════════════════════
// 🔔 SYSTÈME DE NOTIFICATIONS
// ═══════════════════════════════════════════

const MESSAGES_NOTIF = [
  { title: '📚 C\'est l\'heure d\'étudier !', body: 'Ouvre NOKIROVA et révise 10 min ! 💪', url: '/' },
  { title: '🎯 Objectif du jour !', body: 'Fais un QCM pour tester tes connaissances ! 🔥', url: '/qcm' },
  { title: '🌸 NOKIROVA t\'attend !', body: 'Tes flashcards sont prêtes ! On révise ? 😊', url: '/flashcards' },
  { title: '⏱️ Pomodoro time !', body: '25 minutes de focus = 1 succès de plus ! 💎', url: '/pomodoro' },
  { title: '📝 Résumé rapide ?', body: 'Fais résumer ton cours par l\'IA ! ✨', url: '/resume' },
  { title: '💬 Pose une question !', body: 'L\'IA est là pour t\'expliquer ! 🤖', url: '/chat' },
  { title: '🏆 Tu peux le faire !', body: 'Chaque minute d\'étude = un pas vers la réussite ! 🌟', url: '/' }
];

async function demanderPermissionNotifications() {
  if (!('Notification' in window)) return false;
  if (Notification.permission === 'granted') {
    activerNotifications();
    return true;
  }
  if (Notification.permission === 'denied') return false;

  const permission = await Notification.requestPermission();
  if (permission === 'granted') {
    afficherToast('🔔 Notifications activées !', 'success');
    activerNotifications();
    return true;
  }
  return false;
}

function envoyerNotification(title, body, url = '/') {
  if (Notification.permission !== 'granted') return;
  const notif = new Notification(title, { body: body, icon: '/logo', badge: '/logo' });
  notif.onclick = () => { window.focus(); window.location.href = url; notif.close(); };
  setTimeout(() => notif.close(), 8000);
}

function activerNotifications() {
  if (localStorage.getItem('notif_activees') === 'oui') {
    planifierProchainRappel();
    return;
  }
  localStorage.setItem('notif_activees', 'oui');
  setTimeout(() => {
    envoyerNotification('🎉 Notifications activées !', 'Tu recevras des rappels pour étudier ! 💪🌸', '/');
  }, 2000);
  planifierProchainRappel();
}

function planifierProchainRappel() {
  const INTERVALLE = 3 * 60 * 60 * 1000;
  const dernierRappel = parseInt(localStorage.getItem('dernier_rappel') || '0');
  const tempsRestant = Math.max(0, INTERVALLE - (Date.now() - dernierRappel));
  setTimeout(() => {
    envoyerRappelAleatoire();
    planifierProchainRappel();
  }, tempsRestant);
}

function envoyerRappelAleatoire() {
  if (Notification.permission !== 'granted') return;
  const msg = MESSAGES_NOTIF[Math.floor(Math.random() * MESSAGES_NOTIF.length)];
  envoyerNotification(msg.title, msg.body, msg.url);
  localStorage.setItem('dernier_rappel', Date.now().toString());
}

function notifierEvenement(type) {
  const evenements = {
    'pomodoro_fin': { title: '⏱️ Pomodoro terminé !', body: 'Bravo ! Prends une pause de 5 minutes ! 🎉', url: '/pomodoro' },
    'objectif_atteint': { title: '🏆 Objectif atteint !', body: 'Tu as étudié comme prévu ! Continue ! 💎', url: '/' },
    'nouveau_cours': { title: '📚 Nouveau cours importé !', body: 'Ton cours est prêt à être analysé par l\'IA ! ✨', url: '/bibliotheque' }
  };
  const evt = evenements[type];
  if (evt) envoyerNotification(evt.title, evt.body, evt.url);
}

// ═══════════════════════════════════════════
// 💬 SYSTÈME TOAST
// ═══════════════════════════════════════════

function afficherToast(message, type = 'info') {
  const ancienToast = document.querySelector('.toast-nokirova');
  if (ancienToast) ancienToast.remove();

  const couleurs = {
    'success': 'linear-gradient(135deg, #00C853, #7ED321)',
    'error': 'linear-gradient(135deg, #EF4444, #DC2626)',
    'warning': 'linear-gradient(135deg, #F59E0B, #FFD93D)',
    'info': 'linear-gradient(135deg, #7B61FF, #2962FF)'
  };

  const toast = document.createElement('div');
  toast.className = 'toast-nokirova';
  toast.innerHTML = message;
  toast.style.cssText = `
    position: fixed; bottom: 30px; left: 50%;
    transform: translateX(-50%) translateY(100px);
    background: ${couleurs[type] || couleurs.info};
    color: white; padding: 14px 28px; border-radius: 50px;
    font-size: 14px; font-weight: 600; z-index: 99999;
    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
    transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    white-space: nowrap; max-width: 90vw; text-align: center;
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.style.transform = 'translateX(-50%) translateY(0)', 10);
  setTimeout(() => {
    toast.style.transform = 'translateX(-50%) translateY(100px)';
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

// ═══════════════════════════════════════════
// 📄 FONCTIONS PDF (vrai PDF)
// ═══════════════════════════════════════════

async function telechargerPDF(titre, contenu, options = {}) {
  // Appel à l'API PDF
  try {
    const response = await fetch('/api/export-pdf-qcm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        qcm_texte: contenu,
        titre: titre
      })
    });
    const data = await response.json();
    if (data.succes) {
      // Télécharger le fichier PDF
      const a = document.createElement('a');
      a.href = data.url;
      a.download = data.url.split('/').pop();
      a.click();
      afficherToast('📄 PDF généré avec succès !', 'success');
    } else {
      throw new Error(data.erreur || 'Erreur inconnue');
    }
  } catch (err) {
    afficherToast('⚠️ Erreur PDF : ' + err.message, 'error');
  }
}

// ═══════════════════════════════════════════
// 🌙 MODE JOUR/NUIT
// ═══════════════════════════════════════════

function toggleMode() {
  const html = document.documentElement;
  const modeActuel = html.getAttribute('data-mode') || 'clair';
  const nouveauMode = modeActuel === 'clair' ? 'sombre' : 'clair';
  html.setAttribute('data-mode', nouveauMode);
  localStorage.setItem('nokirova-mode', nouveauMode);
  fetch('/api/preferences/set', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cle: 'mode', valeur: nouveauMode })
  });
  afficherToast(nouveauMode === 'sombre' ? '🌙 Mode sombre activé' : '☀️ Mode clair activé', 'info');
}

// ═══════════════════════════════════════════
// 🔄 CHANGER D'UTILISATEUR
// ═══════════════════════════════════════════

function changerUtilisateur() {
  if (confirm('🔄 Veux-tu vraiment changer d\'utilisateur ?\n\n(Tes données restent sauvegardées)')) {
    localStorage.removeItem('nokirova_user');
    sessionStorage.clear();
    window.location.href = '/bienvenue';
  }
}

// ═══════════════════════════════════════════
// ✨ FORMATAGE MARKDOWN (pour rendu propre)
// ═══════════════════════════════════════════

function formaterMarkdown(texte) {
  if (!texte) return '';
  // Utilisation simple : convertir les sauts de ligne en <br>
  let html = texte.replace(/\n/g, '<br>');
  // Convertir **gras** en <strong>
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Convertir les listes simples
  html = html.replace(/^[•\-]\s/gm, '&nbsp;&nbsp;● ');
  return html;
}

// ═══════════════════════════════════════════
// ✨ ANIMATIONS AU CHARGEMENT
// ═══════════════════════════════════════════

document.addEventListener('DOMContentLoaded', function() {
  // Appliquer le mode sauvegardé
  const modeSauvegarde = localStorage.getItem('nokirova-mode');
  if (modeSauvegarde) {
    document.documentElement.setAttribute('data-mode', modeSauvegarde);
  }

  // Appliquer le thème sauvegardé
  const themeSauvegarde = localStorage.getItem('nokirova-theme');
  if (themeSauvegarde) {
    document.documentElement.setAttribute('data-theme', themeSauvegarde);
  }

  // Appliquer la taille sauvegardée
  const tailleSauvegarde = localStorage.getItem('nokirova-taille');
  if (tailleSauvegarde) {
    document.documentElement.setAttribute('data-taille', tailleSauvegarde);
  }

  // Animations des cartes
  const cartesStats = document.querySelectorAll('.carte-stat, .stat-card, .action-card, .db-stat-card');
  cartesStats.forEach((carte, index) => {
    carte.style.opacity = '0';
    carte.style.transform = 'translateY(20px)';
    carte.style.transition = 'all 0.5s ease';
    setTimeout(() => {
      carte.style.opacity = '1';
      carte.style.transform = 'translateY(0)';
    }, 100 + (index * 100));
  });

  // Demander permission notifications après 3 secondes
  setTimeout(() => {
    demanderPermissionNotifications();
  }, 3000);
});

// ═══════════════════════════════════════════
// 📋 COPIER TEXTE
// ═══════════════════════════════════════════

function copierTexte(texte) {
  navigator.clipboard.writeText(texte).then(() => {
    afficherToast('📋 Texte copié !', 'success');
  }).catch(() => {
    afficherToast('❌ Erreur copie', 'error');
  });
}

// ═══════════════════════════════════════════
// 🎯 LOG DE BIENVENUE
// ═══════════════════════════════════════════

console.log("%c🌸 NOKIROVA WEB - Version Professionnelle", "color: #7B61FF; font-size: 20px; font-weight: bold;");
console.log("%cCreated by Hénoc 🌸 2026", "color: #00C853; font-size: 14px; font-style: italic;");