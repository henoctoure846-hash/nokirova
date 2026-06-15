# ocr_handler.py - OCR avec Gemini Vision (cloud) + fallback Tesseract

import os
import base64
import io
from PIL import Image

# Détection Tesseract (fallback local)
TESSERACT_DISPONIBLE = False
if os.path.exists(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
    try:
        import pytesseract

        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        TESSERACT_DISPONIBLE = True
    except ImportError:
        pass


def lire_image_avec_gemini(image_bytes, prompt="Transcris ce texte manuscrit en français :"):
    """Utilise Gemini Vision API (gratuit)"""
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Convertir bytes → base64
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    response = model.generate_content([
        prompt,
        {"mime_type": "image/jpeg", "data": image_b64}
    ])

    return response.text.strip()


def lire_image(chemin_image: str, langue: str = "fra") -> str:
    """OCR : Gemini d'abord, fallback Tesseract local"""

    if not os.path.exists(chemin_image):
        return f"❌ Image introuvable : {chemin_image}"

    # Lire l'image en bytes
    with open(chemin_image, 'rb') as f:
        image_bytes = f.read()

    # ESSAYER GEMINI (cloud, gratuit)
    try:
        texte = lire_image_avec_gemini(image_bytes)
        if texte and not texte.startswith("Erreur"):
            return texte
    except Exception as e:
        print(f"⚠️ Gemini OCR échoué : {e}")

    # FALLBACK : Tesseract local (si dispo)
    if TESSERACT_DISPONIBLE:
        try:
            image = Image.open(chemin_image)
            texte = pytesseract.image_to_string(image, lang=langue)
            if texte.strip():
                return texte.strip()
        except Exception as e:
            print(f"⚠️ Tesseract échoué : {e}")

    return ("❌ Impossible de lire l'image.\n\n"
            "💡 Solutions :\n"
            "• Vérifie ta connexion internet (Gemini)\n"
            "• Ou installe Tesseract sur ton PC\n"
            "• Tape ta question directement dans le chat")


def lire_image_et_expliquer(chemin_image: str) -> str:
    texte = lire_image(chemin_image)
    if texte.startswith("❌") or texte.startswith("⚠️"):
        return texte

    from ia_handler import expliquer_simplement
    explication = expliquer_simplement(texte[:3000])

    return f"📄 TEXTE EXTRAIT :\n{texte}\n\n💡 EXPLICATION IA :\n{explication}"