# db/flashcards.py - Gestion des flashcards NOKIROVA 🌸

from db.base import get_connexion


def creer_flashcard(recto: str, verso: str,
                    matiere: str = "Général",
                    nom_deck: str = "Mon Deck") -> int:
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO flashcards (recto, verso, matiere, nom_deck)
        VALUES (?, ?, ?, ?)
    """, (recto, verso, matiere, nom_deck))
    id_card = cur.lastrowid
    conn.commit()
    conn.close()
    return id_card


def creer_flashcards_bulk(cards: list, matiere: str,
                          nom_deck: str) -> int:
    conn = get_connexion()
    cur = conn.cursor()
    nb = 0
    for card in cards:
        recto = card.get("recto", "").strip()
        verso = card.get("verso", "").strip()
        if recto and verso:
            cur.execute("""
                INSERT INTO flashcards (recto, verso, matiere, nom_deck)
                VALUES (?, ?, ?, ?)
            """, (recto, verso, matiere, nom_deck))
            nb += 1
    conn.commit()
    conn.close()
    return nb


def lister_flashcards(matiere: str = None,
                      nom_deck: str = None) -> list:
    conn = get_connexion()
    cur = conn.cursor()

    if matiere and nom_deck:
        cur.execute("""
            SELECT id, recto, verso, matiere, nom_deck,
            nb_vus, nb_reussis, nb_rates, date_creation
            FROM flashcards
            WHERE matiere=? AND nom_deck=?
            ORDER BY date_creation DESC
        """, (matiere, nom_deck))
    elif matiere:
        cur.execute("""
            SELECT id, recto, verso, matiere, nom_deck,
            nb_vus, nb_reussis, nb_rates, date_creation
            FROM flashcards WHERE matiere=?
            ORDER BY date_creation DESC
        """, (matiere,))
    elif nom_deck:
        cur.execute("""
            SELECT id, recto, verso, matiere, nom_deck,
            nb_vus, nb_reussis, nb_rates, date_creation
            FROM flashcards WHERE nom_deck=?
            ORDER BY date_creation DESC
        """, (nom_deck,))
    else:
        cur.execute("""
            SELECT id, recto, verso, matiere, nom_deck,
            nb_vus, nb_reussis, nb_rates, date_creation
            FROM flashcards ORDER BY date_creation DESC
        """)

    cards = cur.fetchall()
    conn.close()
    return cards


def lister_decks() -> list:
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT nom_deck, matiere,
               COUNT(*) as nb_cards,
               COALESCE(SUM(nb_reussis), 0) as total_reussis,
               COALESCE(SUM(nb_vus), 0) as total_vus
        FROM flashcards
        GROUP BY nom_deck, matiere
        ORDER BY nom_deck
    """)
    decks = cur.fetchall()
    conn.close()
    return decks


def maj_flashcard_stats(id_card: int, reussi: bool):
    conn = get_connexion()
    cur = conn.cursor()
    if reussi:
        cur.execute("""
            UPDATE flashcards
            SET nb_vus = nb_vus + 1,
                nb_reussis = nb_reussis + 1,
                date_derniere_revision = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (id_card,))
    else:
        cur.execute("""
            UPDATE flashcards
            SET nb_vus = nb_vus + 1,
                nb_rates = nb_rates + 1,
                date_derniere_revision = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (id_card,))
    conn.commit()
    conn.close()


def supprimer_flashcard(id_card: int):
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("DELETE FROM flashcards WHERE id = ?", (id_card,))
    conn.commit()
    conn.close()


def supprimer_deck(nom_deck: str):
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM flashcards WHERE nom_deck = ?", (nom_deck,))
    conn.commit()
    conn.close()


def compter_flashcards() -> int:
    conn = get_connexion()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM flashcards")
    nb = cur.fetchone()[0]
    conn.close()
    return nb


def get_flashcards_a_revoir(nom_deck: str = None) -> list:
    conn = get_connexion()
    cur = conn.cursor()
    if nom_deck:
        cur.execute("""
            SELECT id, recto, verso, matiere, nom_deck,
            nb_vus, nb_reussis, nb_rates, date_creation
            FROM flashcards WHERE nom_deck = ?
            ORDER BY nb_rates DESC, nb_vus ASC
        """, (nom_deck,))
    else:
        cur.execute("""
            SELECT id, recto, verso, matiere, nom_deck,
            nb_vus, nb_reussis, nb_rates, date_creation
            FROM flashcards
            ORDER BY nb_rates DESC, nb_vus ASC
        """)
    cards = cur.fetchall()
    conn.close()
    return cards