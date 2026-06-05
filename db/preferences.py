# db/preferences.py - Préférences utilisateur NOKIROVA 🎨

import sqlite3
import os

DB_FILE = "nokirova_memory.db"


def init_table_preferences():
    """Crée la table préférences si elle n'existe pas"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                cle TEXT PRIMARY KEY,
                valeur TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ init preferences : {e}")


def sauvegarder_preference(cle: str, valeur: str):
    """Sauvegarde une préférence"""
    try:
        init_table_preferences()
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            INSERT INTO preferences (cle, valeur)
            VALUES (?, ?)
            ON CONFLICT(cle) DO UPDATE SET valeur = excluded.valeur
        """, (cle, valeur))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ sauvegarder_preference : {e}")


def charger_preference(cle: str, defaut: str = "") -> str:
    """Charge une préférence"""
    try:
        init_table_preferences()
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "SELECT valeur FROM preferences WHERE cle = ?", (cle,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else defaut
    except Exception as e:
        print(f"⚠️ charger_preference : {e}")
        return defaut