# db/tuteur_ia.py - Tuteur IA personnalisé NOKIROVA 🌸

from datetime import datetime, timedelta
from db.base import get_connexion
from db.stats import get_stats


def get_tuteur_dashboard():
    """Données complètes pour le dashboard tuteur IA"""
    stats = get_stats()

    return {
        "stats": {
            "niveau": stats.get("niveau", 1),
            "xp": stats.get("xp", 0),
            "streak": stats.get("streak", 0),
            "cours_importes": stats.get("cours_importes", 0),
            "questions_posees": stats.get("questions_posees", 0)
        },
        "points_faibles": [],
        "recommandations": [
            {
                "titre": "📚 Importer un cours",
                "message": "Commence par importer ton premier cours pour que je puisse t'aider !",
                "action": "Importer",
                "lien": "/import"
            }
        ],
        "conseil_perso": "🌟 Bienvenue sur NOKIROVA ! Importe ton premier cours et découvre toutes mes fonctionnalités."
    }


def generer_conseil_motivant():
    """Génère un conseil motivant"""
    return "🌟 Importe un cours pour commencer ton aventure avec NOKIROVA !"


def get_recommandations_jour():
    """Retourne les recommandations du jour"""
    return [
        {
            "titre": "🎯 Premier objectif",
            "message": "Importe ton premier cours et pose ta première question",
            "action": "Importer",
            "lien": "/import"
        }
    ]


def get_points_faibles():
    """Retourne les points faibles (vide au début)"""
    return []


def get_matiere_performance():
    """Analyse des performances par matière"""
    return {}


def get_progression_semaine():
    """Progression sur 7 jours"""
    return []