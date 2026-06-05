# db/__init__.py - Package DB NOKIROVA 🌸
# Ce fichier expose toutes les fonctions de database.py
# pour que le reste du projet continue à fonctionner sans changement

from db.base import (
    DB_FILE,
    init_db,
    get_connexion
)

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

from db.pomodoro import (
    enregistrer_session_pomodoro,
    sauvegarder_session_pomodoro,
    get_stats_pomodoro,
    lister_sessions_pomodoro
)

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

from db.graphiques import (
    get_stats_graphiques,
    get_progression_resume,
    get_repartition_matieres_cours,
    get_activite_7_derniers_jours
)

from db.pin import (
    set_pin,
    verifier_pin,
    pin_existe,
    supprimer_pin
)

# 🆕 PLANIFICATEUR (Phase 3.1)
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