# test_db.py
import database as db

db.init_db()

print("=" * 50)
print("📊 Stats :", db.get_stats())
print("=" * 50)
print("🍅 Stats Pomodoro :", db.get_stats_pomodoro())
print("=" * 50)
print("🃏 Nb flashcards :", db.compter_flashcards())
print("=" * 50)
print("📦 Decks :", db.lister_decks())
print("=" * 50)
print("📚 Nb cours :", db.compter_cours())
print("=" * 50)
