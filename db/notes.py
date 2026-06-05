# db/notes.py - Gestion des notes NOKIROVA 🌸

from db.base import get_connexion


def creer_note(titre: str, contenu: str,
               matiere: str = "Général",
               couleur: str = "#FFE66D") -> int:
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO notes (titre, contenu, matiere, couleur) "
        "VALUES (?, ?, ?, ?)",
        (titre, contenu, matiere, couleur))
    id_note = cur.lastrowid
    conn.commit()
    conn.close()
    return id_note


def modifier_note(id_note: int, titre: str, contenu: str,
                  matiere: str, couleur: str):
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        UPDATE notes
        SET titre=?, contenu=?, matiere=?, couleur=?,
        date_modification=CURRENT_TIMESTAMP
        WHERE id=?
    """, (titre, contenu, matiere, couleur, id_note))
    conn.commit()
    conn.close()


def supprimer_note(id_note: int):
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id = ?", (id_note,))
    conn.commit()
    conn.close()


def lister_notes(matiere: str = None) -> list:
    conn = get_connexion()
    cur = conn.cursor()
    if matiere and matiere != "Toutes":
        cur.execute("""
            SELECT id, titre, contenu, matiere, couleur,
            date_creation, date_modification
            FROM notes WHERE matiere=?
            ORDER BY date_modification DESC
        """, (matiere,))
    else:
        cur.execute("""
            SELECT id, titre, contenu, matiere, couleur,
            date_creation, date_modification
            FROM notes ORDER BY date_modification DESC
        """)
    notes = cur.fetchall()
    conn.close()
    return notes


def info_note(id_note: int) -> dict:
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, titre, contenu, matiere, couleur,
        date_creation, date_modification
        FROM notes WHERE id=?
    """, (id_note,))
    res = cur.fetchone()
    conn.close()
    if res:
        return {
            "id": res[0], "titre": res[1],
            "contenu": res[2], "matiere": res[3],
            "couleur": res[4], "date_creation": res[5],
            "date_modification": res[6]
        }
    return {}


def compter_notes() -> int:
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM notes")
    nb = cur.fetchone()[0]
    conn.close()
    return nb


def lister_matieres_notes() -> list:
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT matiere FROM notes ORDER BY matiere")
    matieres = [row[0] for row in cur.fetchall() if row[0]]
    conn.close()
    return matieres


def rechercher_notes(mot_cle: str) -> list:
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, titre, contenu, matiere, couleur,
        date_creation, date_modification
        FROM notes WHERE titre LIKE ? OR contenu LIKE ?
        ORDER BY date_modification DESC
    """, (f"%{mot_cle}%", f"%{mot_cle}%"))
    notes = cur.fetchall()
    conn.close()
    return notes