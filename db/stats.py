# db/stats.py - Gamification, XP, Badges NOKIROVA 🌸

from datetime import datetime, date, timedelta
from db.base import get_connexion

# ═══════════════════════════════════════════
# 🎮 STATS UTILISATEUR
# ═══════════════════════════════════════════

def get_stats():
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("SELECT * FROM utilisateur WHERE id = 1")
    stats = cur.fetchone()
    conn.close()

    if not stats:
        return {
            "xp": 0,
            "niveau": 1,
            "streak": 0,
            "derniere_connexion": None,
            "qcm_reussis": 0,
            "qcm_rates": 0,
            "cours_importes": 0,
            "audios_crees": 0,
            "questions_posees": 0
        }

    return {
        "xp": stats[1],
        "niveau": stats[2],
        "streak": stats[3],
        "derniere_connexion": stats[4],
        "qcm_reussis": stats[5],
        "qcm_rates": stats[6],
        "cours_importes": stats[7],
        "audios_crees": stats[8],
        "questions_posees": stats[9]
    }


def ajouter_xp(points: int):
    conn = get_connexion()
    cur = conn.cursor()

    cur.execute(
        "UPDATE utilisateur SET xp = xp + ? WHERE id = 1",
        (points,)
    )

    cur.execute("SELECT xp FROM utilisateur WHERE id = 1")
    xp_total = cur.fetchone()[0]

    nouveau_niveau = (xp_total // 100) + 1
    cur.execute(
        "UPDATE utilisateur SET niveau = ? WHERE id = 1",
        (nouveau_niveau,)
    )

    conn.commit()
    conn.close()
    return nouveau_niveau


def incrementer_stat(nom_stat: str):
    colonnes_ok = {
        "qcm_reussis",
        "qcm_rates",
        "cours_importes",
        "audios_crees",
        "questions_posees"
    }

    if nom_stat not in colonnes_ok:
        print(f"⚠️ Stat inconnue ignorée : {nom_stat}")
        return

    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE utilisateur SET {nom_stat} = {nom_stat} + 1 WHERE id = 1"
    )
    conn.commit()
    conn.close()


def maj_streak():
    conn = get_connexion()
    cur = conn.cursor()

    cur.execute(
        "SELECT derniere_connexion, streak FROM utilisateur WHERE id = 1"
    )
    derniere, streak = cur.fetchone()

    aujourd_hui = datetime.now().date().isoformat()

    if derniere is None:
        nouveau_streak = 1
    elif derniere == aujourd_hui:
        nouveau_streak = streak
    else:
        hier = (date.today() - timedelta(days=1)).isoformat()
        nouveau_streak = streak + 1 if derniere == hier else 1

    cur.execute(
        "UPDATE utilisateur SET streak=?, derniere_connexion=? WHERE id=1",
        (nouveau_streak, aujourd_hui)
    )

    conn.commit()
    conn.close()
    return nouveau_streak


# ═══════════════════════════════════════════
# 🏆 BADGES
# ═══════════════════════════════════════════

BADGES_DISPONIBLES = [
    {"nom": "Premier Pas", "emoji": "👶",
     "description": "Importer ton premier cours",
     "condition": "cours_importes", "valeur": 1},

    {"nom": "Étudiant Assidu", "emoji": "📚",
     "description": "Importer 5 cours",
     "condition": "cours_importes", "valeur": 5},

    {"nom": "Bibliothécaire", "emoji": "🏛️",
     "description": "Importer 20 cours",
     "condition": "cours_importes", "valeur": 20},

    {"nom": "Curieux", "emoji": "🤔",
     "description": "Poser 10 questions",
     "condition": "questions_posees", "valeur": 10},

    {"nom": "Chercheur", "emoji": "🔍",
     "description": "Poser 50 questions",
     "condition": "questions_posees", "valeur": 50},

    {"nom": "Audiophile", "emoji": "🎧",
     "description": "Créer 5 audios",
     "condition": "audios_crees", "valeur": 5},

    {"nom": "Novice", "emoji": "🌱",
     "description": "Atteindre le niveau 5",
     "condition": "niveau", "valeur": 5},

    {"nom": "Expert", "emoji": "⭐",
     "description": "Atteindre le niveau 10",
     "condition": "niveau", "valeur": 10},

    {"nom": "Maître", "emoji": "👑",
     "description": "Atteindre le niveau 25",
     "condition": "niveau", "valeur": 25},

    {"nom": "Flamme", "emoji": "🔥",
     "description": "Streak de 3 jours",
     "condition": "streak", "valeur": 3},

    {"nom": "Inarrêtable", "emoji": "🚀",
     "description": "Streak de 7 jours",
     "condition": "streak", "valeur": 7},

    {"nom": "Légende", "emoji": "🏆",
     "description": "Streak de 30 jours",
     "condition": "streak", "valeur": 30},
]


def verifier_badges():
    stats = get_stats()

    conn = get_connexion()
    cur = conn.cursor()

    nouveaux_badges = []

    for badge in BADGES_DISPONIBLES:
        if stats.get(badge["condition"], 0) >= badge["valeur"]:
            cur.execute(
                "SELECT id FROM badges WHERE nom = ?",
                (badge["nom"],)
            )
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO badges (nom, description, emoji) "
                    "VALUES (?, ?, ?)",
                    (badge["nom"],
                     badge["description"],
                     badge["emoji"])
                )
                nouveaux_badges.append(badge)

    conn.commit()
    conn.close()
    return nouveaux_badges


def lister_badges():
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        "SELECT nom, description, emoji, date_obtention "
        "FROM badges ORDER BY date_obtention DESC"
    )
    badges = cur.fetchall()
    conn.close()
    return badges


def get_niveau_titre(niveau: int) -> str:
    if niveau < 3:
        return "🌱 Apprenti"
    elif niveau < 5:
        return "📖 Étudiant"
    elif niveau < 10:
        return "🎓 Studieux"
    elif niveau < 20:
        return "⭐ Expert"
    elif niveau < 30:
        return "🏆 Maître"
    else:
        return "👑 Légende"