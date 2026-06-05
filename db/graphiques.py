# db/graphiques.py - Statistiques avancées NOKIROVA 🌸

import sqlite3
from datetime import datetime, date, timedelta
from db.base import get_connexion
from db.stats import get_stats


def get_stats_graphiques() -> dict:
    """Retourne toutes les données pour les graphiques"""
    conn = get_connexion()
    cur = conn.cursor()

    stats = get_stats()

    # Activité par type
    cur.execute("""
        SELECT type, COUNT(*) FROM historique
        GROUP BY type ORDER BY COUNT(*) DESC
    """)
    activite_par_type = dict(cur.fetchall())

    # Flashcards stats
    cur.execute("""
        SELECT COALESCE(SUM(nb_reussis), 0),
               COALESCE(SUM(nb_rates), 0),
               COALESCE(SUM(nb_vus), 0)
        FROM flashcards
    """)
    res_fc = cur.fetchone()
    fc_reussis = res_fc[0] or 0
    fc_rates = res_fc[1] or 0
    fc_vus = res_fc[2] or 0

    # Activité 7 derniers jours
    cur.execute("""
        SELECT DATE(date), COUNT(*) FROM historique
        WHERE date >= DATE('now', '-7 days')
        GROUP BY DATE(date)
        ORDER BY DATE(date)
    """)
    activite_7j = dict(cur.fetchall())

    # Pomodoro 7 derniers jours
    cur.execute("""
        SELECT DATE(date_session),
               COALESCE(SUM(duree), 0)
        FROM pomodoro_sessions
        WHERE date_session >= DATE('now', '-7 days')
        AND type='travail'
        GROUP BY DATE(date_session)
        ORDER BY DATE(date_session)
    """)
    pomodoro_7j = dict(cur.fetchall())

    # Cours par matière
    cur.execute("""
        SELECT matiere, COUNT(*) FROM cours
        GROUP BY matiere ORDER BY COUNT(*) DESC
    """)
    cours_par_matiere = dict(cur.fetchall())

    conn.close()

    # Construire jours 7 derniers
    jours = []
    activite_jours = []
    pomodoro_jours = []

    for i in range(6, -1, -1):
        jour = (date.today() - timedelta(days=i)).isoformat()
        jour_court = (date.today() - timedelta(days=i)).strftime('%d/%m')
        jours.append(jour_court)
        activite_jours.append(activite_7j.get(jour, 0))
        pomodoro_jours.append(pomodoro_7j.get(jour, 0))

    return {
        "stats": stats,
        "activite_par_type": activite_par_type,
        "fc_reussis": fc_reussis,
        "fc_rates": fc_rates,
        "fc_vus": fc_vus,
        "jours": jours,
        "activite_jours": activite_jours,
        "pomodoro_jours": pomodoro_jours,
        "cours_par_matiere": cours_par_matiere,
    }


def get_progression_resume() -> dict:
    stats = get_stats()

    conn = get_connexion()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM cours")
    nb_cours = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM historique")
    nb_historique = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM notes")
    nb_notes = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM flashcards")
    nb_flashcards = cur.fetchone()[0]

    cur.execute("""
        SELECT COALESCE(SUM(nb_reussis), 0),
               COALESCE(SUM(nb_vus), 0)
        FROM flashcards
    """)
    flash_reussis, flash_vus = cur.fetchone()

    try:
        cur.execute("""
            SELECT COUNT(*) FROM pomodoro_sessions
            WHERE completed = 1
        """)
        sessions_pomodoro = cur.fetchone()[0]

        cur.execute("""
            SELECT COALESCE(SUM(duree), 0)
            FROM pomodoro_sessions WHERE completed = 1
        """)
        minutes_pomodoro = cur.fetchone()[0]
    except sqlite3.OperationalError:
        sessions_pomodoro = 0
        minutes_pomodoro = 0

    conn.close()

    qcm_total = stats["qcm_reussis"] + stats["qcm_rates"]
    taux_qcm = int(
        (stats["qcm_reussis"] / qcm_total) * 100
    ) if qcm_total > 0 else 0

    taux_flashcards = int(
        (flash_reussis / flash_vus) * 100
    ) if flash_vus > 0 else 0

    return {
        "xp": stats["xp"],
        "niveau": stats["niveau"],
        "streak": stats["streak"],
        "qcm_reussis": stats["qcm_reussis"],
        "qcm_rates": stats["qcm_rates"],
        "qcm_total": qcm_total,
        "taux_qcm": taux_qcm,
        "nb_cours": nb_cours,
        "nb_historique": nb_historique,
        "nb_notes": nb_notes,
        "nb_flashcards": nb_flashcards,
        "taux_flashcards": taux_flashcards,
        "sessions_pomodoro": sessions_pomodoro,
        "minutes_pomodoro": minutes_pomodoro
    }


def get_repartition_matieres_cours(limite: int = 8) -> list:
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT matiere, COUNT(*) as total
        FROM cours
        GROUP BY matiere
        ORDER BY total DESC
        LIMIT ?
    """, (limite,))
    data = cur.fetchall()
    conn.close()
    return data


def get_activite_7_derniers_jours() -> list:
    aujourd_hui = datetime.now().date()
    debut = aujourd_hui - timedelta(days=6)

    jours = {}
    for i in range(7):
        jour = debut + timedelta(days=i)
        jours[jour.isoformat()] = 0

    conn = get_connexion()
    cur = conn.cursor()

    tables = [
        ("historique", "date"),
        ("cours", "date_import"),
        ("notes", "date_modification"),
    ]

    for table, colonne in tables:
        try:
            cur.execute(f"""
                SELECT substr({colonne}, 1, 10) as jour,
                       COUNT(*)
                FROM {table}
                WHERE substr({colonne}, 1, 10) >= ?
                GROUP BY substr({colonne}, 1, 10)
            """, (debut.isoformat(),))
            for jour, total in cur.fetchall():
                if jour in jours:
                    jours[jour] += total
        except sqlite3.OperationalError:
            pass

    try:
        cur.execute("""
            SELECT substr(date_session, 1, 10) as jour,
                   COUNT(*)
            FROM pomodoro_sessions
            WHERE substr(date_session, 1, 10) >= ?
            GROUP BY substr(date_session, 1, 10)
        """, (debut.isoformat(),))
        for jour, total in cur.fetchall():
            if jour in jours:
                jours[jour] += total
    except sqlite3.OperationalError:
        pass

    conn.close()

    resultat = []
    for jour_iso, total in jours.items():
        jour_obj = datetime.strptime(jour_iso, "%Y-%m-%d")
        resultat.append((jour_obj.strftime("%d/%m"), total))

    return resultat