# ocr_handler.py - Lecture d'images avec OCR 🔍

import pytesseract
from PIL import Image
import os

# IMPORTANT : Indique à Python où trouver Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def lire_image(chemin_image: str, langue: str = "fra") -> str:
    """
    Extrait le texte d'une image (cours, exercice, schéma).
    
    Args:
        chemin_image: Chemin vers l'image (.jpg, .png, .jpeg)
        langue: "fra" pour français, "eng" pour anglais
    
    Returns:
        Texte extrait
    """
    if not os.path.exists(chemin_image):
        return f"❌ Image introuvable : {chemin_image}"
    
    try:
        image = Image.open(chemin_image)
        texte = pytesseract.image_to_string(image, lang=langue)
        
        if not texte.strip():
            return "⚠️ Aucun texte détecté dans l'image. Essaie une image plus claire."
        
        return texte.strip()
    except Exception as e:
        return f"❌ Erreur OCR : {e}\n\n💡 Vérifie que Tesseract est bien installé dans C:\\Program Files\\Tesseract-OCR\\"


def lire_image_et_expliquer(chemin_image: str) -> str:
    """Lit une image puis demande à l'IA d'expliquer"""
    from ia_handler import expliquer_simplement
    
    texte = lire_image(chemin_image)
    if texte.startswith("❌") or texte.startswith("⚠️"):
        return texte
    
    explication = expliquer_simplement(texte)
    return f"📄 TEXTE DÉTECTÉ :\n{'='*50}\n{texte}\n\n{'='*50}\n\n💡 EXPLICATION :\n{explication}"


# TEST
if __name__ == "__main__":
    print("🔍 Module OCR prêt !")
    print("💡 Pour tester : place une image dans le projet et appelle lire_image('image.jpg')")