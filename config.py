# config.py - Configuration NOKIROVA (local + cloud)

import os

# 🔑 CLÉS API
# Essaie d'abord les variables d'environnement (Railway)
# Sinon utilise les valeurs locales
GEMINI_API_KEY = os.getenv("AQ.Ab8RN6KOJk7aMLa3LWjxHyc8HNjhiMi0swkySAibw48guQoshg")
GROQ_API_KEY = os.getenv("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")
MISTRAL_API_KEY = os.getenv("VedfrlGQiuMcu76U2hfdfl54SNLmAOgW")

# 📁 Dossiers
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

print("✅ Configuration NOKIROVA chargée !")