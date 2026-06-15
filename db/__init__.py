# db/__init__.py - Package DB NOKIROVA 🌸
# Ce fichier expose toutes les fonctions pour que le reste du projet fonctionne

# ═══════════════════════════════════════════
# 📦 BASE
# ═══════════════════════════════════════════

from db.base import (
    DB_FILE,
    init_db,
    get_connexion,
    get_user,
    set_user,
    is_logged_in,
    get_current_user_id
)

# ═══════════════════════════════════════════
# 📚 COURS
# ═══════════════════════════════════════════

from db.cours import (
    sauvegarder_cours,
    lister_cours,
    recuperer_cours,
    supprimer_cours,
    renommer_cours,
    info_cours,
    compter_cours,
    lister_matieres_uniques,
    filtrer_cours_par_matiere,
    rechercher_dans_cours,
    extraire_contexte
)

# ═══════════════════════════════════════════
# 📜 HISTORIQUE
# ═══════════════════════════════════════════

from db.historique import (
    sauvegarder_historique,
    lister_historique,
    lister_historique_complet,
    filtrer_historique_par_type,
    info_historique,
    supprimer_historique,
    vider_historique,
    compter_historique,
    lister_types_historique,
    compter_par_type
)

# ═══════════════════════════════════════════
# ✍️ NOTES
# ═══════════════════════════════════════════

from db.notes import (
    creer_note,
    modifier_note,
    supprimer_note,
    lister_notes,
    info_note,
    compter_notes,
    lister_matieres_notes,
    rechercher_notes
)

# ═══════════════════════════════════════════
# 🃏 FLASHCARDS
# ═══════════════════════════════════════════

from db.flashcards import (
    creer_flashcard,
    creer_flashcards_bulk,
    lister_flashcards,
    lister_decks,
    maj_flashcard_stats,
    supprimer_flashcard,
    supprimer_deck,
    compter_flashcards,
    get_flashcards_a_revoir
)

# ═══════════════════════════════════════════
# ⏱️ POMODORO
# ═══════════════════════════════════════════

from db.pomodoro import (
    enregistrer_session_pomodoro,
    sauvegarder_session_pomodoro,
    get_stats_pomodoro,
    lister_sessions_pomodoro
)

# ═══════════════════════════════════════════
# 🎮 STATS & BADGES
# ═══════════════════════════════════════════

from db.stats import (
    get_stats,
    ajouter_xp,
    incrementer_stat,
    maj_streak,
    verifier_badges,
    lister_badges,
    get_niveau_titre,
    BADGES_DISPONIBLES
)

# ═══════════════════════════════════════════
# 📊 GRAPHIQUES
# ═══════════════════════════════════════════

from db.graphiques import (
    get_stats_graphiques,
    get_progression_resume,
    get_repartition_matieres_cours,
    get_activite_7_derniers_jours
)

# ═══════════════════════════════════════════
# 🔒 PIN SÉCURITÉ
# ═══════════════════════════════════════════

from db.pin import (
    set_pin,
    verifier_pin,
    pin_existe,
    supprimer_pin
)

# ═══════════════════════════════════════════
# 📅 PLANIFICATEUR
# ═══════════════════════════════════════════

from db.planificateur import (
    init_table_planificateur,
    ajouter_tache,
    lister_taches_jour,
    lister_taches_semaine,
    lister_taches_mois,
    marquer_tache_faite,
    marquer_tache_a_faire,
    supprimer_tache,
    modifier_tache,
    info_tache,
    stats_planning,
    compter_taches_en_retard,
    get_taches_aujourd_hui,
    lister_matieres_planning,
    supprimer_taches_anciennes,
    couleur_matiere,
    TYPES_TACHES,
    PRIORITES,
    PALETTE_MATIERES
)

# ═══════════════════════════════════════════
# ✅ TODO LIST (Phase G)
# ═══════════════════════════════════════════

try:
    from db.todo import (
        ajouter_tache_todo,
        lister_taches_todo,
        toggle_tache_todo,
        supprimer_tache_todo,
        compter_taches_todo
    )
except ImportError:
    # Fallback si le fichier n'existe pas encore
    def ajouter_tache_todo(texte): return None
    def lister_taches_todo(): return []
    def toggle_tache_todo(id_t): return None
    def supprimer_tache_todo(id_t): return None
    def compter_taches_todo(): return 0

# ═══════════════════════════════════════════
# 🧠 TUTEUR IA (Phase D4)
# ═══════════════════════════════════════════

try:
    from db.tuteur_ia import (
        get_tuteur_dashboard,
        generer_conseil_motivant,
        get_recommandations_jour,
        get_points_faibles,
        get_matiere_performance,
        get_progression_semaine
    )
except ImportError:
    # Fallback si le fichier n'existe pas encore
    def get_tuteur_dashboard(): return {"stats": {}, "points_faibles": [], "recommandations": [], "conseil_perso": "Bienvenue sur NOKIROVA ! Importe ton premier cours."}
    def generer_conseil_motivant(): return "🌟 Importe un cours pour commencer !"
    def get_recommandations_jour(): return []
    def get_points_faibles(): return []
    def get_matiere_performance(): return {}
    def get_progression_semaine(): return []