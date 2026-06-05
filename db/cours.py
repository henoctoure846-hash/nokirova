# db/cours.py - Gestion des cours NOKIROVA 🌸

from db.base import get_connexion
from db.stats import ajouter_xp, incrementer_stat


def sauvegarder_cours(nom: str, contenu: str, matiere: str = "Auto-détection..."):
    try:
        from intelligence import detecter_matiere
        info = detecter_matiere(contenu)
        matiere = f"{info.get('emoji_matiere', '📚')} {info.get('matiere', 'Général')}"
    except Exception:
        matiere = "📚 Général"

    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO cours (nom, matiere, contenu) VALUES (?, ?, ?)",
        (nom, matiere, contenu))
    conn.commit()
    conn.close()
    ajouter_xp(10)
    incrementer_stat("cours_importes")
    return matiere


def lister_cours():
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nom, matiere, date_import "
        "FROM cours ORDER BY date_import DESC")
    cours = cur.fetchall()
    conn.close()
    return cours


def recuperer_cours(id_cours: int) -> str:
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("SELECT contenu FROM cours WHERE id = ?", (id_cours,))
    res = cur.fetchone()
    conn.close()
    return res[0] if res else ""


def supprimer_cours(id_cours: int):
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("DELETE FROM cours WHERE id = ?", (id_cours,))
    conn.commit()
    conn.close()


def renommer_cours(id_cours: int, nouveau_nom: str):
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        "UPDATE cours SET nom = ? WHERE id = ?",
        (nouveau_nom, id_cours))
    conn.commit()
    conn.close()


def info_cours(id_cours: int) -> dict:
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nom, matiere, contenu, date_import "
        "FROM cours WHERE id = ?", (id_cours,))
    res = cur.fetchone()
    conn.close()
    if res:
        return {
            "id": res[0], "nom": res[1],
            "matiere": res[2], "contenu": res[3],
            "date_import": res[4],
            "taille": len(res[3]) if res[3] else 0
        }
    return {}


def compter_cours() -> int:
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM cours")
    nb = cur.fetchone()[0]
    conn.close()
    return nb


def lister_matieres_uniques():
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT matiere FROM cours ORDER BY matiere")
    matieres = [row[0] for row in cur.fetchall() if row[0]]
    conn.close()
    return matieres


def filtrer_cours_par_matiere(matiere: str):
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nom, matiere, date_import "
        "FROM cours WHERE matiere = ? "
        "ORDER BY date_import DESC", (matiere,))
    cours = cur.fetchall()
    conn.close()
    return cours


def rechercher_dans_cours(mot_cle: str, matiere: str = None) -> list:
    mot_cle = (mot_cle or "").strip()
    if not mot_cle:
        return []

    conn = get_connexion()
    cur = conn.cursor()
    like = f"%{mot_cle}%"

    if matiere and matiere != "Toutes":
        cur.execute("""
            SELECT id, nom, matiere, contenu, date_import
            FROM cours
            WHERE (LOWER(nom) LIKE LOWER(?)
            OR LOWER(contenu) LIKE LOWER(?))
            AND matiere = ?
            ORDER BY date_import DESC
        """, (like, like, matiere))
    else:
        cur.execute("""
            SELECT id, nom, matiere, contenu, date_import
            FROM cours
            WHERE LOWER(nom) LIKE LOWER(?)
            OR LOWER(contenu) LIKE LOWER(?)
            ORDER BY date_import DESC
        """, (like, like))

    lignes = cur.fetchall()
    conn.close()

    resultats = []
    mot_lower = mot_cle.lower()

    for id_cours, nom, matiere_cours, contenu, date_import in lignes:
        contenu = contenu or ""
        contenu_lower = contenu.lower()

        position = contenu_lower.find(mot_lower)
        if position == -1:
            position = 0

        debut = max(0, position - 120)
        fin = min(len(contenu), position + len(mot_cle) + 180)

        extrait = contenu[debut:fin].replace("\n", " ").strip()
        if debut > 0:
            extrait = "..." + extrait
        if fin < len(contenu):
            extrait = extrait + "..."

        nb_occurrences = contenu_lower.count(mot_lower)
        nb_occurrences += nom.lower().count(mot_lower)

        resultats.append((
            id_cours, nom, matiere_cours,
            extrait, nb_occurrences, date_import
        ))

    return resultats


def extraire_contexte(contenu: str, mot_cle: str,
                      nb_chars: int = 200) -> list:
    """Extrait les passages contenant le mot-clé avec contexte"""
    passages = []
    contenu_lower = contenu.lower()
    mot_lower = mot_cle.lower()
    pos = 0

    while True:
        idx = contenu_lower.find(mot_lower, pos)
        if idx == -1:
            break

        debut = max(0, idx - nb_chars // 2)
        fin = min(len(contenu), idx + len(mot_cle) + nb_chars // 2)
        passage = contenu[debut:fin].strip()

        if debut > 0:
            passage = "..." + passage
        if fin < len(contenu):
            passage = passage + "..."

        passages.append(passage)
        pos = idx + 1

        if len(passages) >= 5:
            break

    return passages