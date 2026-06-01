# audio_generator.py - Crée des audios GRATUITS et ILLIMITÉS 🎧

import edge_tts
import asyncio
import os

# ═══════════════════════════════════════════
# 📁 CONFIGURATION (compatible local + cloud)
# ═══════════════════════════════════════════
try:
    # En local : utilise config.py
    from config import OUTPUT_FOLDER
except ImportError:
    # Sur Render : utilise les variables d'environnement
    OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "outputs")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ═══════════════════════════════════════════
# 🎙️ VOIX FRANÇAISES DISPONIBLES
# ═══════════════════════════════════════════
VOIX_FR = {
    "homme": "fr-FR-HenriNeural",
    "femme": "fr-FR-DeniseNeural",
    "jeune_homme": "fr-FR-RemyMultilingualNeural",
    "jeune_femme": "fr-FR-VivienneMultilingualNeural"
}


# ═══════════════════════════════════════════
# 🔊 CRÉATION AUDIO (asynchrone)
# ═══════════════════════════════════════════
async def _creer_audio_async(texte: str, nom_fichier: str, voix: str):
    """Création audio asynchrone (interne)"""
    chemin_sortie = os.path.join(OUTPUT_FOLDER, nom_fichier)
    voix_choisie = VOIX_FR.get(voix, VOIX_FR["femme"])

    communicate = edge_tts.Communicate(texte, voix_choisie)
    await communicate.save(chemin_sortie)

    return chemin_sortie


# ═══════════════════════════════════════════
# 🎵 FONCTION PRINCIPALE
# ═══════════════════════════════════════════
def generer_audio(texte: str, nom_fichier: str = "audio.mp3", voix: str = "femme") -> str:
    """
    Crée un fichier audio à partir d'un texte (GRATUIT ILLIMITÉ).

    Args:
        texte: Le texte à convertir en audio
        nom_fichier: Nom du fichier de sortie (ex: "cours1.mp3")
        voix: "homme", "femme", "jeune_homme", "jeune_femme"

    Returns:
        Chemin du fichier audio créé (ou "" en cas d'erreur)
    """
    try:
        # Vérifier que le texte n'est pas vide
        if not texte or not texte.strip():
            print("⚠️ Texte vide, impossible de créer l'audio")
            return ""

        # Limiter la longueur (Edge-TTS a une limite)
        if len(texte) > 5000:
            texte = texte[:5000]
            print(f"⚠️ Texte tronqué à 5000 caractères")

        # Créer l'audio
        chemin = asyncio.run(_creer_audio_async(texte, nom_fichier, voix))
        print(f"✅ Audio créé : {chemin}")
        return chemin

    except Exception as e:
        print(f"❌ Erreur audio : {e}")
        return ""


# ═══════════════════════════════════════════
# 📋 LISTER LES VOIX DISPONIBLES
# ═══════════════════════════════════════════
def lister_voix() -> dict:
    """Retourne la liste des voix françaises disponibles"""
    return VOIX_FR


# ═══════════════════════════════════════════
# 🧪 TEST RAPIDE
# ═══════════════════════════════════════════
if __name__ == "__main__":
    print("🎧 Test du générateur audio NOKIROVA...")
    print(f"📁 Dossier de sortie : {OUTPUT_FOLDER}")
    print(f"🎙️ Voix disponibles : {list(VOIX_FR.keys())}")
    print()

    texte_test = (
        "Bonjour ! Bienvenue dans NOKIROVA, "
        "ton professeur intelligent personnel. "
        "Je suis là pour t'aider à réussir tes examens !"
    )

    chemin = generer_audio(texte_test, "test_voix.mp3", "jeune_femme")

    if chemin:
        print(f"\n✅ Test réussi !")
        print(f"📂 Va dans le dossier '{OUTPUT_FOLDER}/' pour écouter test_voix.mp3")
    else:
        print("\n❌ Test échoué")