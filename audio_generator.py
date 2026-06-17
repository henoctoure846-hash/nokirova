# audio_generator.py - Crée des audios GRATUITS et ILLIMITÉS 🎧
# Ajout : nettoyage du texte et fonction de pré-écoute

import edge_tts
import asyncio
import os
import re

# ═══════════════════════════════════════════
# 📁 CONFIGURATION (compatible local + cloud)
# ═══════════════════════════════════════════
try:
    from config import OUTPUT_FOLDER
except ImportError:
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


def nettoyer_texte_audio(texte: str) -> str:
    """Nettoie le texte pour une lecture naturelle"""
    if not texte:
        return texte
    # Supprimer les marqueurs markdown
    texte = re.sub(r'\*\*(.+?)\*\*', r'\1', texte)
    texte = re.sub(r'\*(.+?)\*', r'\1', texte)
    texte = re.sub(r'`(.+?)`', r'\1', texte)
    # Supprimer les crochets
    texte = re.sub(r'[\[\]]', '', texte)
    # Supprimer les emojis complexes (hors ponctuation)
    texte = re.sub(r'[^\w\s.,!?;:()«»""''%°€$£¥@&+\-=<>/\\#\n]', '', texte)
    # Réduire les sauts de ligne multiples
    texte = re.sub(r'\n{3,}', '\n\n', texte)
    # Supprimer les espaces multiples
    texte = re.sub(r'[ \t]+', ' ', texte)
    return texte.strip()


def _voix_par_defaut(voix: str) -> str:
    return VOIX_FR.get(voix, VOIX_FR["femme"])


async def _creer_audio_async(texte: str, nom_fichier: str, voix: str):
    chemin_sortie = os.path.join(OUTPUT_FOLDER, nom_fichier)
    communicate = edge_tts.Communicate(texte, _voix_par_defaut(voix))
    await communicate.save(chemin_sortie)
    return chemin_sortie


def generer_audio(texte: str, nom_fichier: str = "audio.mp3", voix: str = "femme") -> str:
    texte = nettoyer_texte_audio(texte)
    if not texte:
        return ""
    if len(texte) > 5000:
        texte = texte[:5000]
    try:
        chemin = asyncio.run(_creer_audio_async(texte, nom_fichier, voix))
        print(f"✅ Audio créé : {chemin}")
        return chemin
    except Exception as e:
        print(f"❌ Erreur audio : {e}")
        return ""


def generer_audio_preview(texte: str, voix: str = "femme", duree: int = 15) -> str:
    """Génère un court extrait audio (défaut 15 secondes)"""
    texte = nettoyer_texte_audio(texte)
    if not texte:
        return ""
    # Estimer le nombre de caractères pour ~15 secondes (vitesse moyenne 150 mots/min, ~2.5 mots/seconde, ~15 caractères/seconde)
    nb_chars = min(len(texte), duree * 15)
    extrait = texte[:nb_chars]
    # Ajouter une fin de phrase propre
    if nb_chars < len(texte):
        dernier_point = extrait.rfind('.')
        if dernier_point > 0:
            extrait = extrait[:dernier_point+1]
    nom_fichier = f"preview_{voix}_{os.urandom(4).hex()}.mp3"
    try:
        chemin = asyncio.run(_creer_audio_async(extrait, nom_fichier, voix))
        return chemin
    except Exception as e:
        print(f"❌ Erreur preview : {e}")
        return ""


def lister_voix() -> dict:
    return VOIX_FR