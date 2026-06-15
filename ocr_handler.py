# ocr_handler.py - OCR avec Gemini Vision (cloud) + fallback Tesseract
# VERSION CORRIGÉE - Récupère la clé API depuis config ou os.getenv

import os
import base64
from PIL import Image


# ═══════════════════════════════════════════
# 🔑 CHARGEMENT DE LA CLÉ GEMINI
# ═══════════════════════════════════════════

def get_gemini_api_key():
    """Récupère la clé Gemini depuis config ou variables d'environnement"""
    try:
        from config import GEMINI_API_KEY
        if GEMINI_API_KEY and "COLLE" not in GEMINI_API_KEY and len(GEMINI_API_KEY) > 10:
            return GEMINI_API_KEY
    except ImportError:
        pass

    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key and "COLLE" not in api_key and len(api_key) > 10:
        return api_key

    return None


# ═══════════════════════════════════════════
# 📦 TESSERACT (fallback local)
# ═══════════════════════════════════════════

TESSERACT_DISPONIBLE = False
if os.path.exists(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
    try:
        import pytesseract

        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        TESSERACT_DISPONIBLE = True
    except ImportError:
        pass


# ═══════════════════════════════════════════
# 🧠 GEMINI VISION
# ═══════════════════════════════════════════

def lire_image_avec_gemini(image_bytes, prompt="Transcris ce texte manuscrit en français :"):
    """Utilise Gemini Vision API avec vérification de clé"""
    api_key = get_gemini_api_key()

    if not api_key:
        print("⚠️ Aucune clé Gemini trouvée")
        return None

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_b64}
        ])

        return response.text.strip()

    except Exception as e:
        print(f"⚠️ Gemini OCR échoué : {e}")
        return None


# ═══════════════════════════════════════════
# 📷 OCR PRINCIPAL
# ═══════════════════════════════════════════

def lire_image(chemin_image: str, langue: str = "fra") -> str:
    """OCR : Gemini d'abord, fallback Tesseract local"""

    if not os.path.exists(chemin_image):
        return f"❌ Image introuvable : {chemin_image}"

    with open(chemin_image, 'rb') as f:
        image_bytes = f.read()

    # 1️⃣ ESSAYER GEMINI
    try:
        texte = lire_image_avec_gemini(image_bytes)
        if texte and len(texte) > 10:
            return texte
    except Exception as e:
        print(f"⚠️ Gemini échoué : {e}")

    # 2️⃣ FALLBACK TESSERACT
    if TESSERACT_DISPONIBLE:
        try:
            image = Image.open(chemin_image)
            texte = pytesseract.image_to_string(image, lang=langue)
            if texte.strip() and len(texte.strip()) > 10:
                return texte.strip()
        except Exception as e:
            print(f"⚠️ Tesseract échoué : {e}")

    # 3️⃣ TOUT A ÉCHOUÉ
    return ("❌ Impossible de lire l'image.\n\n"
            "💡 Solutions :\n"
            "• Vérifie que ta clé GEMINI_API_KEY est configurée sur Render\n"
            "• Vérifie ta connexion internet\n"
            "• Ou tape ta question directement dans le chat")


def lire_image_et_expliquer(chemin_image: str) -> str:
    texte = lire_image(chemin_image)
    if texte.startswith("❌"):
        return texte

    from ia_handler import expliquer_simplement
    explication = expliquer_simplement(texte[:3000])

    return f"📄 **TEXTE EXTRAIT :**\n{texte}\n\n💡 **EXPLICATION IA :**\n{explication}"