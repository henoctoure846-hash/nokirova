# fix_db.py - Script de migration pour ajouter les colonnes manquantes
import sqlite3

DB_FILE = "nokirova_memory.db"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

print("🔧 Correction de la table pomodoro_sessions...")

# Vérifier les colonnes existantes
cur.execute("PRAGMA table_info(pomodoro_sessions)")
colonnes = [row[1] for row in cur.fetchall()]
print(f"Colonnes actuelles : {colonnes}")

# Ajouter 'type' si absente
if 'type' not in colonnes:
    try:
        cur.execute("ALTER TABLE pomodoro_sessions ADD COLUMN type TEXT DEFAULT 'travail'")
        print("✅ Colonne 'type' ajoutée")
    except Exception as e:
        print(f"⚠️ {e}")

# Ajouter 'completed' si absente
if 'completed' not in colonnes:
    try:
        cur.execute("ALTER TABLE pomodoro_sessions ADD COLUMN completed INTEGER DEFAULT 1")
        print("✅ Colonne 'completed' ajoutée")
    except Exception as e:
        print(f"⚠️ {e}")

# Ajouter 'duree' si absente
if 'duree' not in colonnes:
    try:
        cur.execute("ALTER TABLE pomodoro_sessions ADD COLUMN duree INTEGER DEFAULT 25")
        print("✅ Colonne 'duree' ajoutée")
    except Exception as e:
        print(f"⚠️ {e}")

# Ajouter 'matiere' si absente
if 'matiere' not in colonnes:
    try:
        cur.execute("ALTER TABLE pomodoro_sessions ADD COLUMN matiere TEXT DEFAULT 'Général'")
        print("✅ Colonne 'matiere' ajoutée")
    except Exception as e:
        print(f"⚠️ {e}")

# Mettre à jour les anciennes lignes pour qu'elles aient les bonnes valeurs
cur.execute("UPDATE pomodoro_sessions SET type='travail' WHERE type IS NULL")
cur.execute("UPDATE pomodoro_sessions SET completed=1 WHERE completed IS NULL")

conn.commit()

# Vérification finale
cur.execute("PRAGMA table_info(pomodoro_sessions)")
print(f"\n✅ Colonnes finales : {[row[1] for row in cur.fetchall()]}")

conn.close()
print("\n🎉 Migration terminée ! Tu peux relancer NOKIROVA.")