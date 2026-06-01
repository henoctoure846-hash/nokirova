# ocr_handler.py - OCR (local seulement)

import os

# Détecter environnement
EST_SERVEUR = (
        os.getenv("RENDER") is not None or
        os.getenv("RAILWAY_ENVIRONMENT") is not None or
        not os.path.exists(r'C:\Program Files\Tesseract-OCR\tesseract.exe')
)

TESSERACT_DISPONIBLE = False

if not EST_SERVEUR:
    try:
        import pytesseract
        from PIL import Image

        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        TESSERACT_DISPONIBLE = True
    except ImportError:
        pass


def lire_image(chemin_image: str, langue: str = "fra") -> str:
    if not TESSERACT_DISPONIBLE:
        return ("⚠️ Scanner non disponible sur la version en ligne.\n\n"
                "💡 Utilise NOKIROVA en local pour scanner des images.")

    if not os.path.exists(chemin_image):
        return f"❌ Image introuvable"

    try:
        image = Image.open(chemin_image)
        texte = pytesseract.image_to_string(image, lang=langue)
        return texte.strip() if texte.strip() else "⚠️ Aucun texte détecté"
    except Exception as e:
        return f"❌ Erreur OCR : {e}"


def lire_image_et_expliquer(chemin_image: str) -> str:
    if not TESSERACT_DISPONIBLE:
        return ("⚠️ Scanner d'images non disponible sur la version en ligne.\n\n"
                "💡 Solutions :\n"
                "✅ Utilise NOKIROVA en local sur ton PC\n"
                "✅ Tape directement ta question dans 💬 Chat\n"
                "✅ Importe ton cours en PDF/Word")

    from ia_handler import expliquer_simplement
    texte = lire_image(chemin_image)
    if texte.startswith("❌") or texte.startswith("⚠️"):
        return texte

    explication = expliquer_simplement(texte)
    return f"📄 TEXTE :\n{texte}\n\n💡 EXPLICATION :\n{explication}"