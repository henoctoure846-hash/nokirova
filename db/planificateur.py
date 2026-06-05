# db/planificateur.py - Gestion du planificateur NOKIROVA 📅

from db.base import get_connexion
from datetime import datetime, timedelta


# ═══════════════════════════════════════════
# 🎨 COULEURS PAR MATIÈRE (auto-assignées)
# ═══════════════════════════════════════════
PALETTE_MATIERES = [
    "#7ED321",  # Vert printemps
    "#FFD93D",  # Jaune soleil
    "#7EC8FF",  # Bleu ciel
    "#FFC9DE",  # Rose sakura
    "#A855F7",  # Violet lavande
    "#F59E0B",  # Orange doré
    "#00C853",  # Vert émeraude
    "#7B61FF",  # Violet premium
    "#2962FF",  # Bleu royal
    "#FB923C",  # Orange clair
]


def couleur_matiere(matiere: str) -> str:
    """Retourne une couleur stable basée sur le nom de la matière"""
    if not matiere:
        return PALETTE_MATIERES[0]
    # Hash simple pour avoir toujours la même couleur pour une matière
    index = sum(ord(c) for c in matiere) % len(PALETTE_MATIERES)
    return PALETTE_MATIERES[index]


# ═══════════════════════════════════════════
# 🗂️ TYPES DE TÂCHES
# ═══════════════════════════════════════════
TYPES_TACHES = {
    "reviser": {"emoji": "📖", "label": "Réviser"},
    "exercices": {"emoji": "✍️", "label": "Exercices"},
    "qcm": {"emoji": "🎯", "label": "QCM / Test"},
    "examen": {"emoji": "📚", "label": "Examen"},
    "flashcards": {"emoji": "🃏", "label": "Flashcards"},
}

PRIORITES = {
    "urgent": {"emoji": "🔴", "label": "Urgent", "couleur": "#EF4444"},
    "normal": {"emoji": "🟡", "label": "Normal", "couleur": "#FFD93D"},
    "bonus": {"emoji": "🟢", "label": "Bonus", "couleur": "#7ED321"},
}


# ═══════════════════════════════════════════
# 🏗️ CRÉATION DE LA TABLE
# ═══════════════════════════════════════════
def init_table_planificateur():
    """Crée la table tasks si elle n'existe pas"""
    conn = get_connexion()
    cur = conn.cursor()
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
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════
# ➕ AJOUTER UNE TÂCHE
# ═══════════════════════════════════════════
def ajouter_tache(
        titre: str,
        date_tache: str,
        heure_debut: str = "09:00",
        duree_minutes: int = 30,
        matiere: str = "Général",
        type_tache: str = "reviser",
        priorite: str = "normal",
        description: str = "",
        recurrence: str = "aucune",
        cours_lie_id: int = None):
    """Ajoute une tâche au planificateur"""
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tasks
        (titre, description, matiere, type_tache, priorite,
         date_tache, heure_debut, duree_minutes, recurrence, cours_lie_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (titre, description, matiere, type_tache, priorite,
          date_tache, heure_debut, duree_minutes, recurrence, cours_lie_id))
    tache_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Si récurrence → créer les copies
    if recurrence != "aucune":
        _creer_recurrences(
            tache_id, titre, description, matiere, type_tache,
            priorite, date_tache, heure_debut, duree_minutes,
            recurrence, cours_lie_id)

    return tache_id


def _creer_recurrences(
        tache_origine_id, titre, description, matiere, type_tache,
        priorite, date_tache, heure_debut, duree_minutes,
        recurrence, cours_lie_id):
    """Crée les tâches récurrentes (8 semaines max)"""
    try:
        date_obj = datetime.strptime(date_tache, "%Y-%m-%d")
    except Exception:
        return

    if recurrence == "quotidienne":
        delta_jours = 1
        nb_copies = 30  # 30 jours
    elif recurrence == "hebdomadaire":
        delta_jours = 7
        nb_copies = 8  # 8 semaines
    elif recurrence == "mensuelle":
        delta_jours = 30
        nb_copies = 3  # 3 mois
    else:
        return

    conn = get_connexion()
    cur = conn.cursor()
    for i in range(1, nb_copies + 1):
        nouvelle_date = (date_obj + timedelta(days=delta_jours * i)
                         ).strftime("%Y-%m-%d")
        cur.execute("""
            INSERT INTO tasks
            (titre, description, matiere, type_tache, priorite,
             date_tache, heure_debut, duree_minutes, recurrence, cours_lie_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'aucune', ?)
        """, (titre, description, matiere, type_tache, priorite,
              nouvelle_date, heure_debut, duree_minutes, cours_lie_id))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════
# 📋 LISTER LES TÂCHES
# ═══════════════════════════════════════════
def lister_taches_jour(date_str: str = None):
    """Liste les tâches d'un jour donné (par défaut: aujourd'hui)"""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, titre, description, matiere, type_tache, priorite,
               date_tache, heure_debut, duree_minutes, statut,
               recurrence, cours_lie_id
        FROM tasks
        WHERE date_tache = ?
        ORDER BY heure_debut ASC
    """, (date_str,))
    taches = cur.fetchall()
    conn.close()
    return taches


def lister_taches_semaine(date_debut: str = None):
    """Liste les tâches d'une semaine (lundi → dimanche)"""
    if not date_debut:
        aujourd = datetime.now()
        lundi = aujourd - timedelta(days=aujourd.weekday())
        date_debut = lundi.strftime("%Y-%m-%d")
    date_debut_obj = datetime.strptime(date_debut, "%Y-%m-%d")
    date_fin_obj = date_debut_obj + timedelta(days=6)
    date_fin = date_fin_obj.strftime("%Y-%m-%d")
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, titre, description, matiere, type_tache, priorite,
               date_tache, heure_debut, duree_minutes, statut,
               recurrence, cours_lie_id
        FROM tasks
        WHERE date_tache BETWEEN ? AND ?
        ORDER BY date_tache ASC, heure_debut ASC
    """, (date_debut, date_fin))
    taches = cur.fetchall()
    conn.close()
    return taches


def lister_taches_mois(annee: int = None, mois: int = None):
    """Liste les tâches d'un mois"""
    if not annee or not mois:
        now = datetime.now()
        annee, mois = now.year, now.month
    date_debut = f"{annee:04d}-{mois:02d}-01"
    if mois == 12:
        date_fin = f"{annee + 1:04d}-01-01"
    else:
        date_fin = f"{annee:04d}-{mois + 1:02d}-01"
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, titre, description, matiere, type_tache, priorite,
               date_tache, heure_debut, duree_minutes, statut,
               recurrence, cours_lie_id
        FROM tasks
        WHERE date_tache >= ? AND date_tache < ?
        ORDER BY date_tache ASC, heure_debut ASC
    """, (date_debut, date_fin))
    taches = cur.fetchall()
    conn.close()
    return taches


# ═══════════════════════════════════════════
# ✅ ACTIONS SUR LES TÂCHES
# ═══════════════════════════════════════════
def marquer_tache_faite(tache_id: int):
    """Marque une tâche comme terminée"""
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET statut = 'faite' WHERE id = ?",
                (tache_id,))
    conn.commit()
    conn.close()


def marquer_tache_a_faire(tache_id: int):
    """Remet une tâche en mode 'à faire'"""
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET statut = 'a_faire' WHERE id = ?",
                (tache_id,))
    conn.commit()
    conn.close()


def supprimer_tache(tache_id: int):
    """Supprime une tâche"""
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (tache_id,))
    conn.commit()
    conn.close()


def modifier_tache(tache_id: int, **kwargs):
    """Modifie une tâche (champs au choix)"""
    if not kwargs:
        return
    champs_autorises = {
        "titre", "description", "matiere", "type_tache",
        "priorite", "date_tache", "heure_debut",
        "duree_minutes", "statut"
    }
    updates = []
    valeurs = []
    for k, v in kwargs.items():
        if k in champs_autorises:
            updates.append(f"{k} = ?")
            valeurs.append(v)
    if not updates:
        return
    valeurs.append(tache_id)
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", valeurs)
    conn.commit()
    conn.close()


def info_tache(tache_id: int) -> dict:
    """Info complète d'une tâche"""
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, titre, description, matiere, type_tache, priorite,
               date_tache, heure_debut, duree_minutes, statut,
               recurrence, cours_lie_id
        FROM tasks WHERE id = ?
    """, (tache_id,))
    res = cur.fetchone()
    conn.close()
    if not res:
        return {}
    return {
        "id": res[0], "titre": res[1], "description": res[2],
        "matiere": res[3], "type_tache": res[4], "priorite": res[5],
        "date_tache": res[6], "heure_debut": res[7],
        "duree_minutes": res[8], "statut": res[9],
        "recurrence": res[10], "cours_lie_id": res[11]
    }


# ═══════════════════════════════════════════
# 📊 STATISTIQUES
# ═══════════════════════════════════════════
def stats_planning() -> dict:
    """Statistiques globales du planificateur"""
    conn = get_connexion()
    cur = conn.cursor()

    # Total taches
    cur.execute("SELECT COUNT(*) FROM tasks")
    total = cur.fetchone()[0]

    # Taches faites
    cur.execute("SELECT COUNT(*) FROM tasks WHERE statut = 'faite'")
    faites = cur.fetchone()[0]

    # Taches à faire
    cur.execute("SELECT COUNT(*) FROM tasks WHERE statut = 'a_faire'")
    a_faire = cur.fetchone()[0]

    # Taches en retard (avant aujourd'hui et pas faites)
    aujourd = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        SELECT COUNT(*) FROM tasks
        WHERE date_tache < ? AND statut = 'a_faire'
    """, (aujourd,))
    en_retard = cur.fetchone()[0]

    # Taches aujourd'hui
    cur.execute("""
        SELECT COUNT(*) FROM tasks WHERE date_tache = ?
    """, (aujourd,))
    aujourd_total = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM tasks
        WHERE date_tache = ? AND statut = 'faite'
    """, (aujourd,))
    aujourd_faites = cur.fetchone()[0]

    # Temps total prévu cette semaine
    aujourd_obj = datetime.now()
    lundi = aujourd_obj - timedelta(days=aujourd_obj.weekday())
    dimanche = lundi + timedelta(days=6)
    cur.execute("""
        SELECT COALESCE(SUM(duree_minutes), 0) FROM tasks
        WHERE date_tache BETWEEN ? AND ?
    """, (lundi.strftime("%Y-%m-%d"), dimanche.strftime("%Y-%m-%d")))
    temps_semaine = cur.fetchone()[0]

    # Matière la plus travaillée
    cur.execute("""
        SELECT matiere, COUNT(*) as nb FROM tasks
        WHERE statut = 'faite'
        GROUP BY matiere
        ORDER BY nb DESC
        LIMIT 1
    """)
    res_matiere = cur.fetchone()
    matiere_top = res_matiere[0] if res_matiere else "—"

    conn.close()

    pct = round((faites / total * 100), 1) if total > 0 else 0

    return {
        "total": total,
        "faites": faites,
        "a_faire": a_faire,
        "en_retard": en_retard,
        "aujourd_total": aujourd_total,
        "aujourd_faites": aujourd_faites,
        "temps_semaine_min": temps_semaine,
        "temps_semaine_h": round(temps_semaine / 60, 1),
        "matiere_top": matiere_top,
        "pourcentage_reussi": pct,
    }


def compter_taches_en_retard() -> int:
    """Retourne le nombre de tâches en retard (pour pastille)"""
    aujourd = datetime.now().strftime("%Y-%m-%d")
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM tasks
        WHERE date_tache < ? AND statut = 'a_faire'
    """, (aujourd,))
    nb = cur.fetchone()[0]
    conn.close()
    return nb


def get_taches_aujourd_hui():
    """Raccourci : tâches d'aujourd'hui"""
    return lister_taches_jour()


# ═══════════════════════════════════════════
# 🔍 LISTER MATIÈRES UTILISÉES
# ═══════════════════════════════════════════
def lister_matieres_planning():
    """Liste les matières uniques utilisées dans le planning"""
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT matiere FROM tasks ORDER BY matiere")
    matieres = [row[0] for row in cur.fetchall() if row[0]]
    conn.close()
    return matieres


# ═══════════════════════════════════════════
# 🧹 NETTOYAGE AUTO (option futur)
# ═══════════════════════════════════════════
def supprimer_taches_anciennes(jours: int = 90):
    """Supprime les tâches faites de plus de X jours"""
    date_limite = (datetime.now() - timedelta(days=jours)
                   ).strftime("%Y-%m-%d")
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM tasks
        WHERE date_tache < ? AND statut = 'faite'
    """, (date_limite,))
    nb = cur.rowcount
    conn.commit()
    conn.close()
    return nb