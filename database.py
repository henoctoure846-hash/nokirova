# database.py - La mémoire intelligente de NOKIROVA 🧠

import sqlite3
from datetime import datetime
import os

DB_FILE = "nokirova_memory.db"


def init_db():
    """Crée la base de données si elle n'existe pas"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    # Table des cours importés
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            matiere TEXT,
            contenu TEXT,
            date_import TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table de l'historique des questions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historique (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            question TEXT,
            reponse TEXT,
            matiere TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table des stats utilisateur (gamification)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS utilisateur (
            id INTEGER PRIMARY KEY,
            xp INTEGER DEFAULT 0,
            niveau INTEGER DEFAULT 1,
            streak INTEGER DEFAULT 0,
            derniere_connexion DATE,
            qcm_reussis INTEGER DEFAULT 0,
            qcm_rates INTEGER DEFAULT 0,
            cours_importes INTEGER DEFAULT 0,
            audios_crees INTEGER DEFAULT 0,
            questions_posees INTEGER DEFAULT 0
        )
    """)
    
    # Table des badges
    cur.execute("""
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            description TEXT,
            emoji TEXT,
            date_obtention TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table des faiblesses (matières où l'utilisateur rate)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS faiblesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matiere TEXT UNIQUE,
            niveau_difficulte INTEGER DEFAULT 0,
            derniere_pratique TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Créer l'utilisateur s'il n'existe pas
    cur.execute("SELECT id FROM utilisateur WHERE id = 1")
    if not cur.fetchone():
        cur.execute("INSERT INTO utilisateur (id) VALUES (1)")
    
    conn.commit()
    conn.close()
    print("✅ Base de données NOKIROVA initialisée !")


# ═══════════════════════════════════════════
# 📚 GESTION DES COURS
# ═══════════════════════════════════════════
def sauvegarder_cours(nom: str, contenu: str, matiere: str = "Auto-détection..."):
    """Sauvegarde un cours en mémoire avec détection auto de matière"""
    # Détection automatique de la matière
    try:
        from intelligence import detecter_matiere
        info = detecter_matiere(contenu)
        matiere = f"{info.get('emoji_matiere', '📚')} {info.get('matiere', 'Général')}"
    except Exception:
        matiere = "📚 Général"

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO cours (nom, matiere, contenu) VALUES (?, ?, ?)",
                (nom, matiere, contenu))
    conn.commit()
    conn.close()
    ajouter_xp(10)
    incrementer_stat("cours_importes")
    return matiere


def lister_cours():
    """Retourne la liste de tous les cours"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, nom, matiere, date_import FROM cours ORDER BY date_import DESC")
    cours = cur.fetchall()
    conn.close()
    return cours


def recuperer_cours(id_cours: int) -> str:
    """Récupère le contenu d'un cours"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT contenu FROM cours WHERE id = ?", (id_cours,))
    res = cur.fetchone()
    conn.close()
    return res[0] if res else ""


def supprimer_cours(id_cours: int):
    """Supprime un cours"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM cours WHERE id = ?", (id_cours,))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════
# 📜 HISTORIQUE
# ═══════════════════════════════════════════
def sauvegarder_historique(type_action: str, question: str, reponse: str, matiere: str = "Général"):
    """Sauvegarde une interaction"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO historique (type, question, reponse, matiere) VALUES (?, ?, ?, ?)",
                (type_action, question, reponse, matiere))
    conn.commit()
    conn.close()


def lister_historique(limite: int = 20):
    """Retourne les dernières interactions"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT type, question, reponse, matiere, date FROM historique ORDER BY date DESC LIMIT ?",
                (limite,))
    historique = cur.fetchall()
    conn.close()
    return historique


# ═══════════════════════════════════════════
# 🎮 GAMIFICATION
# ═══════════════════════════════════════════
def get_stats():
    """Retourne les stats de l'utilisateur"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM utilisateur WHERE id = 1")
    stats = cur.fetchone()
    conn.close()
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
    """Ajoute des XP et calcule le niveau"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE utilisateur SET xp = xp + ? WHERE id = 1", (points,))
    
    # Calcul du niveau (100 XP = 1 niveau)
    cur.execute("SELECT xp FROM utilisateur WHERE id = 1")
    xp_total = cur.fetchone()[0]
    nouveau_niveau = (xp_total // 100) + 1
    cur.execute("UPDATE utilisateur SET niveau = ? WHERE id = 1", (nouveau_niveau,))
    
    conn.commit()
    conn.close()
    
    # Vérifier les badges
    verifier_badges()
    return nouveau_niveau


def incrementer_stat(nom_stat: str):
    """Incrémente une statistique"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"UPDATE utilisateur SET {nom_stat} = {nom_stat} + 1 WHERE id = 1")
    conn.commit()
    conn.close()


def maj_streak():
    """Met à jour le streak quotidien"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT derniere_connexion, streak FROM utilisateur WHERE id = 1")
    derniere, streak = cur.fetchone()
    
    aujourd_hui = datetime.now().date().isoformat()
    
    if derniere is None:
        nouveau_streak = 1
    elif derniere == aujourd_hui:
        nouveau_streak = streak
    else:
        from datetime import date, timedelta
        hier = (date.today() - timedelta(days=1)).isoformat()
        if derniere == hier:
            nouveau_streak = streak + 1
        else:
            nouveau_streak = 1
    
    cur.execute("UPDATE utilisateur SET streak = ?, derniere_connexion = ? WHERE id = 1",
                (nouveau_streak, aujourd_hui))
    conn.commit()
    conn.close()
    return nouveau_streak


# ═══════════════════════════════════════════
# 🏆 BADGES
# ═══════════════════════════════════════════
BADGES_DISPONIBLES = [
    {"nom": "Premier Pas", "emoji": "👶", "description": "Importer ton premier cours", "condition": "cours_importes", "valeur": 1},
    {"nom": "Étudiant Assidu", "emoji": "📚", "description": "Importer 5 cours", "condition": "cours_importes", "valeur": 5},
    {"nom": "Bibliothécaire", "emoji": "🏛️", "description": "Importer 20 cours", "condition": "cours_importes", "valeur": 20},
    {"nom": "Curieux", "emoji": "🤔", "description": "Poser 10 questions", "condition": "questions_posees", "valeur": 10},
    {"nom": "Chercheur", "emoji": "🔍", "description": "Poser 50 questions", "condition": "questions_posees", "valeur": 50},
    {"nom": "Audiophile", "emoji": "🎧", "description": "Créer 5 audios", "condition": "audios_crees", "valeur": 5},
    {"nom": "Novice", "emoji": "🌱", "description": "Atteindre le niveau 5", "condition": "niveau", "valeur": 5},
    {"nom": "Expert", "emoji": "⭐", "description": "Atteindre le niveau 10", "condition": "niveau", "valeur": 10},
    {"nom": "Maître", "emoji": "👑", "description": "Atteindre le niveau 25", "condition": "niveau", "valeur": 25},
    {"nom": "Flamme", "emoji": "🔥", "description": "Streak de 3 jours", "condition": "streak", "valeur": 3},
    {"nom": "Inarrêtable", "emoji": "🚀", "description": "Streak de 7 jours", "condition": "streak", "valeur": 7},
    {"nom": "Légende", "emoji": "🏆", "description": "Streak de 30 jours", "condition": "streak", "valeur": 30},
]


def verifier_badges():
    """Vérifie et débloque les nouveaux badges"""
    stats = get_stats()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    nouveaux_badges = []
    for badge in BADGES_DISPONIBLES:
        if stats.get(badge["condition"], 0) >= badge["valeur"]:
            cur.execute("SELECT id FROM badges WHERE nom = ?", (badge["nom"],))
            if not cur.fetchone():
                cur.execute("INSERT INTO badges (nom, description, emoji) VALUES (?, ?, ?)",
                            (badge["nom"], badge["description"], badge["emoji"]))
                nouveaux_badges.append(badge)
    
    conn.commit()
    conn.close()
    return nouveaux_badges


def lister_badges():
    """Liste tous les badges débloqués"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT nom, description, emoji, date_obtention FROM badges ORDER BY date_obtention DESC")
    badges = cur.fetchall()
    conn.close()
    return badges


def get_niveau_titre(niveau: int) -> str:
    """Retourne le titre selon le niveau"""
    if niveau < 3: return "🌱 Apprenti"
    elif niveau < 5: return "📖 Étudiant"
    elif niveau < 10: return "🎓 Studieux"
    elif niveau < 20: return "⭐ Expert"
    elif niveau < 30: return "🏆 Maître"
    else: return "👑 Légende"


# Initialisation au démarrage
if __name__ == "__main__":
    init_db()
    print("✅ Database NOKIROVA prête !")
    print(f"📊 Stats : {get_stats()}")