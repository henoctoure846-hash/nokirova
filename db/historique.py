# db/historique.py - Gestion de l'historique NOKIROVA 🌸

from db.base import get_connexion


def sauvegarder_historique(type_action: str, question: str,
                           reponse: str, matiere: str = "Général"):
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO historique (type, question, reponse, matiere) "
        "VALUES (?, ?, ?, ?)",
        (type_action, question, reponse, matiere))
    conn.commit()
    conn.close()


def lister_historique(limite: int = 20):
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        "SELECT type, question, reponse, matiere, date "
        "FROM historique ORDER BY date DESC LIMIT ?",
        (limite,))
    historique = cur.fetchall()
    conn.close()
    return historique


def lister_historique_complet(limite: int = 100):
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, type, question, reponse, matiere, date
        FROM historique ORDER BY date DESC LIMIT ?
    """, (limite,))
    historique = cur.fetchall()
    conn.close()
    return historique


def filtrer_historique_par_type(type_action: str, limite: int = 100):
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, type, question, reponse, matiere, date
        FROM historique WHERE type = ?
        ORDER BY date DESC LIMIT ?
    """, (type_action, limite))
    historique = cur.fetchall()
    conn.close()
    return historique


def info_historique(id_historique: int) -> dict:
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, type, question, reponse, matiere, date
        FROM historique WHERE id = ?
    """, (id_historique,))
    res = cur.fetchone()
    conn.close()
    if res:
        return {
            "id": res[0], "type": res[1],
            "question": res[2], "reponse": res[3],
            "matiere": res[4], "date": res[5]
        }
    return {}


def supprimer_historique(id_historique: int):
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("DELETE FROM historique WHERE id = ?", (id_historique,))
    conn.commit()
    conn.close()


def vider_historique():
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("DELETE FROM historique")
    conn.commit()
    conn.close()


def compter_historique() -> int:
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM historique")
    nb = cur.fetchone()[0]
    conn.close()
    return nb


def lister_types_historique():
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT type FROM historique ORDER BY type")
    types = [row[0] for row in cur.fetchall() if row[0]]
    conn.close()
    return types


def compter_par_type():
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT type, COUNT(*) FROM historique
        GROUP BY type ORDER BY COUNT(*) DESC
    """)
    stats = cur.fetchall()
    conn.close()
    return stats