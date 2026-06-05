# db/pomodoro.py - Gestion des sessions Pomodoro NOKIROVA 🌸

from db.base import get_connexion


def enregistrer_session_pomodoro(duree_minutes: int,
                                 type_session: str = "travail",
                                 matiere: str = "Général"):
    """Enregistre une session Pomodoro terminée"""
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO pomodoro_sessions
        (duree, completed, type, matiere, date_session)
        VALUES (?, 1, ?, ?, CURRENT_TIMESTAMP)
    """, (duree_minutes, type_session, matiere))
    conn.commit()
    conn.close()

    if type_session == "travail":
        from db.stats import ajouter_xp
        ajouter_xp(max(1, duree_minutes // 5))


def sauvegarder_session_pomodoro(duree_minutes: int,
                                 type_session: str = "travail",
                                 matiere: str = "Général"):
    """Alias pour compatibilité avec ancien code"""
    return enregistrer_session_pomodoro(
        duree_minutes, type_session, matiere)


def get_stats_pomodoro() -> dict:
    """Retourne les statistiques Pomodoro"""
    conn = get_connexion()
    cur = conn.cursor()

    # Total sessions
    cur.execute("""
        SELECT COUNT(*), COALESCE(SUM(duree), 0)
        FROM pomodoro_sessions
        WHERE type='travail' AND completed=1
    """)
    res = cur.fetchone()
    total_sessions = res[0] or 0
    total_minutes = res[1] or 0

    # Sessions aujourd'hui
    cur.execute("""
        SELECT COUNT(*), COALESCE(SUM(duree), 0)
        FROM pomodoro_sessions
        WHERE type='travail' AND completed=1
        AND DATE(date_session) = DATE('now')
    """)
    res_today = cur.fetchone()
    sessions_today = res_today[0] or 0
    minutes_today = res_today[1] or 0

    # Par matière
    cur.execute("""
        SELECT matiere, COUNT(*) as nb,
        COALESCE(SUM(duree), 0) as total_duree
        FROM pomodoro_sessions
        WHERE type='travail' AND completed=1
        GROUP BY matiere
        ORDER BY nb DESC
        LIMIT 5
    """)
    par_matiere = cur.fetchall()

    conn.close()

    return {
        "total_sessions": total_sessions,
        "sessions_completees": total_sessions,
        "total_minutes": total_minutes,
        "total_heures": round(total_minutes / 60, 1),
        "sessions_today": sessions_today,
        "minutes_today": minutes_today,
        "par_matiere": par_matiere
    }


def lister_sessions_pomodoro(limite: int = 30) -> list:
    """Liste les sessions Pomodoro récentes"""
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, duree, completed, matiere, date_session
        FROM pomodoro_sessions
        ORDER BY date_session DESC
        LIMIT ?
    """, (limite,))
    sessions = cur.fetchall()
    conn.close()
    return sessions