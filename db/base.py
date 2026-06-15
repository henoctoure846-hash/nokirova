# db/base.py - Connexion DB MULTI-UTILISATEURS + AUTHENTIFICATION NOKIROVA 🌸

import sqlite3
import os
import threading
import bcrypt
from datetime import datetime

# Stockage du user_id en cours (par thread)
_current_user = threading.local()

# Dossier des bases utilisateurs
DB_FOLDER = "user_databases"
os.makedirs(DB_FOLDER, exist_ok=True)

DB_DEFAULT = "nokirova_memory.db"
USERS_DB = os.path.join(DB_FOLDER, "_users.db")


def set_user(user_id: str):
    """Définit le user_id actuel pour ce thread"""
    if user_id and len(user_id) > 3:
        _current_user.user_id = user_id
    else:
        _current_user.user_id = None


def get_user():
    """Récupère le user_id actuel"""
    return getattr(_current_user, 'user_id', None)


def get_db_file():
    """Retourne le fichier DB selon le user actuel"""
    user_id = get_user()
    if user_id:
        safe_id = "".join(c for c in user_id if c.isalnum() or c == '_')[:50]
        return os.path.join(DB_FOLDER, f"nokirova_{safe_id}.db")
    return DB_DEFAULT


def get_connexion():
    """Retourne une connexion à la base de l'utilisateur courant"""
    db_file = get_db_file()
    if not os.path.exists(db_file):
        _init_db_file(db_file)
    return sqlite3.connect(db_file)


# ═══════════════════════════════════════════
# 👤 GESTION DES UTILISATEURS (AUTH)
# ═══════════════════════════════════════════

def init_users_table():
    """Crée la table des utilisateurs si elle n'existe pas"""
    conn = sqlite3.connect(USERS_DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nom TEXT,
            prenom TEXT,
            date_inscription TEXT NOT NULL,
            derniere_connexion TEXT
        )
    """)
    conn.commit()
    conn.close()


def creer_utilisateur(email: str, password: str, nom: str = "", prenom: str = "") -> dict:
    """Crée un nouvel utilisateur"""
    init_users_table()

    conn = sqlite3.connect(USERS_DB)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = ?", (email.lower(),))
    if cur.fetchone():
        conn.close()
        return {"succes": False, "erreur": "Email déjà utilisé"}

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    now = datetime.now().isoformat()

    cur.execute("""
        INSERT INTO users (email, password_hash, nom, prenom, date_inscription)
        VALUES (?, ?, ?, ?, ?)
    """, (email.lower(), password_hash, nom, prenom, now))
    user_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Créer la base personnelle de l'utilisateur
    _init_user_database(str(user_id))

    return {"succes": True, "user_id": user_id, "email": email}


def verifier_utilisateur(email: str, password: str) -> dict:
    """Vérifie les identifiants"""
    init_users_table()

    conn = sqlite3.connect(USERS_DB)
    cur = conn.cursor()
    cur.execute("SELECT id, email, password_hash, nom, prenom FROM users WHERE email = ?", (email.lower(),))
    user = cur.fetchone()
    conn.close()

    if not user:
        return {"succes": False, "erreur": "Email ou mot de passe incorrect"}

    user_id, email_db, password_hash, nom, prenom = user

    if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
        # Mettre à jour dernière connexion
        conn = sqlite3.connect(USERS_DB)
        cur = conn.cursor()
        cur.execute("UPDATE users SET derniere_connexion = ? WHERE id = ?",
                    (datetime.now().isoformat(), user_id))
        conn.commit()
        conn.close()

        return {"succes": True, "user_id": user_id, "email": email_db, "nom": nom or "", "prenom": prenom or ""}

    return {"succes": False, "erreur": "Email ou mot de passe incorrect"}


def get_user_info(user_id: int) -> dict:
    """Récupère les infos d'un utilisateur"""
    init_users_table()
    conn = sqlite3.connect(USERS_DB)
    cur = conn.cursor()
    cur.execute("SELECT id, email, nom, prenom, date_inscription, derniere_connexion FROM users WHERE id = ?",
                (user_id,))
    user = cur.fetchone()
    conn.close()

    if user:
        return {
            "id": user[0],
            "email": user[1],
            "nom": user[2] or "",
            "prenom": user[3] or "",
            "date_inscription": user[4],
            "derniere_connexion": user[5]
        }
    return None


def _init_user_database(user_id: str):
    """Crée toutes les tables pour un nouvel utilisateur"""
    safe_id = "".join(c for c in user_id if c.isalnum() or c == '_')[:50]
    db_file = os.path.join(DB_FOLDER, f"nokirova_{safe_id}.db")
    _init_db_file(db_file)


def _init_db_file(db_file: str):
    """Crée toutes les tables dans le fichier DB donné"""
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            matiere TEXT,
            contenu TEXT,
            date_import TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            description TEXT,
            emoji TEXT,
            date_obtention TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS faiblesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matiere TEXT UNIQUE,
            niveau_difficulte INTEGER DEFAULT 0,
            derniere_pratique TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            contenu TEXT,
            matiere TEXT DEFAULT 'Général',
            couleur TEXT DEFAULT '#FFE66D',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recto TEXT NOT NULL,
            verso TEXT NOT NULL,
            matiere TEXT DEFAULT 'Général',
            nom_deck TEXT DEFAULT 'Mon Deck',
            nb_vus INTEGER DEFAULT 0,
            nb_reussis INTEGER DEFAULT 0,
            nb_rates INTEGER DEFAULT 0,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_derniere_revision TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pomodoro_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            duree INTEGER DEFAULT 25,
            completed INTEGER DEFAULT 1,
            type TEXT DEFAULT 'travail',
            matiere TEXT DEFAULT 'Général',
            date_session TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS securite (
            id INTEGER PRIMARY KEY,
            pin_hash TEXT,
            pin_actif INTEGER DEFAULT 0,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            description TEXT DEFAULT '',
            matiere TEXT DEFAULT 'Général',
            type_tache TEXT DEFAULT 'reviser',
            priorite TEXT DEFAULT 'normal',
            date_tache DATE NOT NULL,
            heure_debut TEXT DEFAULT '09:00',
            duree_minutes INTEGER DEFAULT 30,
            statut TEXT DEFAULT 'a_faire',
            recurrence TEXT DEFAULT 'aucune',
            cours_lie_id INTEGER DEFAULT NULL,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            cle TEXT PRIMARY KEY,
            valeur TEXT NOT NULL
        )
    """)

    cur.execute("SELECT id FROM utilisateur WHERE id = 1")
    if not cur.fetchone():
        cur.execute("INSERT INTO utilisateur (id) VALUES (1)")

    cur.execute("SELECT id FROM securite WHERE id = 1")
    if not cur.fetchone():
        cur.execute("INSERT INTO securite (id, pin_actif) VALUES (1, 0)")

    conn.commit()
    conn.close()
    print(f"✅ DB initialisée : {db_file}")


def init_db():
    """Init DB par défaut (compatibilité ancien code)"""
    _init_db_file(DB_DEFAULT)


def is_logged_in():
    """Vérifie si un utilisateur est connecté"""
    return get_user() is not None


def get_current_user_id():
    return get_user()


# Initialisation
init_users_table()