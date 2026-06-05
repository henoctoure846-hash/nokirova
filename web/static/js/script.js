// ═══════════════════════════════════════════
// 🌸 NOKIROVA WEB - JAVASCRIPT PHASE 1
// ═══════════════════════════════════════════

console.log("🌸 NOKIROVA WEB chargée !");

// ═══════════════════════════════════════════
// 🧭 NAVIGATION (clic sur boutons sidebar)
// ═══════════════════════════════════════════

function naviguer(page) {
    console.log(`📍 Navigation vers : ${page}`);

    // Pour la PHASE 1, on affiche juste une alerte
    // Dans les prochaines phases, on chargera les vraies pages

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

    // Marquer le bouton actif
    document.querySelectorAll('.bouton-sidebar').forEach(btn => {
        btn.classList.remove('actif');
    });

    // Marquer le bouton cliqué comme actif
    event.target.classList.add('actif');

    // Pour l'instant, on affiche un message
    alert(`🚧 Page "${nomPage}" en construction !\n\n✨ Sera disponible dans la Phase 2 ! 🌸`);
}

// ═══════════════════════════════════════════
// 🎨 MODE JOUR/NUIT (placeholder)
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
    // Animation des cartes stats au chargement
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

    // Animation des cartes rapides
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
});

// ═══════════════════════════════════════════
// 🎯 LOG DE BIENVENUE
// ═══════════════════════════════════════════

console.log("%c🌸 NOKIROVA WEB - PHASE 1 ✨", "color: #7B61FF; font-size: 20px; font-weight: bold;");
console.log("%cCreated by Hénoc 🌸 2026", "color: #00C853; font-size: 14px; font-style: italic;");