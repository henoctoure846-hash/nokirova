# audio_generator.py - Crée des audios GRATUITS et ILLIMITÉS

import edge_tts
import asyncio
import os
from config import OUTPUT_FOLDER

# Voix françaises disponibles
VOIX_FR = {
    "homme": "fr-FR-HenriNeural",
    "femme": "fr-FR-DeniseNeural",
    "jeune_homme": "fr-FR-RemyMultilingualNeural",
    "jeune_femme": "fr-FR-VivienneMultilingualNeural"
}


async def _creer_audio_async(texte: str, nom_fichier: str, voix: str):
    """Création audio asynchrone (interne)"""
    chemin_sortie = os.path.join(OUTPUT_FOLDER, nom_fichier)
    voix_choisie = VOIX_FR.get(voix, VOIX_FR["femme"])
    
    communicate = edge_tts.Communicate(texte, voix_choisie)
    await communicate.save(chemin_sortie)
    
    return chemin_sortie


def generer_audio(texte: str, nom_fichier: str = "audio.mp3", voix: str = "femme") -> str:
    """
    Crée un fichier audio à partir d'un texte (GRATUIT ILLIMITÉ).
    
    Args:
        texte: Le texte à convertir en audio
        nom_fichier: Nom du fichier de sortie (ex: "cours1.mp3")
        voix: "homme", "femme", "jeune_homme", "jeune_femme"
    
    Returns:
        Chemin du fichier audio créé
    """
    try:
        chemin = asyncio.run(_creer_audio_async(texte, nom_fichier, voix))
        print(f"✅ Audio créé : {chemin}")
        return chemin
    except Exception as e:
        print(f"❌ Erreur audio : {e}")
        return ""


# TEST
if __name__ == "__main__":
    print("🎧 Test du générateur audio...")
    texte_test = "Bonjour ! Bienvenue dans NOKIROVA, ton professeur intelligent personnel."
    generer_audio(texte_test, "test_voix.mp3", "jeune_femme")
    print("✅ Vérifie le dossier 'outputs/' !")