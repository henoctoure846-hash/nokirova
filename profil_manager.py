# profil_manager.py - Gestion du profil utilisateur NOKIROVA 👤

import os
import json
import shutil
from datetime import datetime

DOSSIER_PROFIL = "profil"
FICHIER_PROFIL = "profil/profil.json"
PHOTO_PROFIL = "profil/photo.png"


# ═══════════════════════════════════════════
# 📋 PROFIL PAR DÉFAUT
# ═══════════════════════════════════════════
PROFIL_DEFAUT = {
    "nom_complet": "",
    "email": "",
    "numero": "",
    "universite": "",
    "annee_etude": "",
    "date_naissance": "",
    "bio": "",
    "photo_path": "",
    "date_creation": "",
    "date_modification": ""
}


# ═══════════════════════════════════════════
# 🛠️ INIT
# ═══════════════════════════════════════════
def init_profil():
    """Crée le dossier profil et le fichier JSON si nécessaire"""
    if not os.path.exists(DOSSIER_PROFIL):
        os.makedirs(DOSSIER_PROFIL)
    if not os.path.exists(FICHIER_PROFIL):
        profil = PROFIL_DEFAUT.copy()
        profil["date_creation"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M")
        sauvegarder_profil(profil)


# ═══════════════════════════════════════════
# 📥 CHARGEMENT
# ═══════════════════════════════════════════
def charger_profil() -> dict:
    """Charge le profil depuis le JSON"""
    init_profil()
    try:
        with open(FICHIER_PROFIL, 'r', encoding='utf-8') as f:
            profil = json.load(f)
        # Compléter les champs manquants
        for cle, val in PROFIL_DEFAUT.items():
            if cle not in profil:
                profil[cle] = val
        return profil
    except Exception as e:
        print(f"⚠️ Erreur chargement profil : {e}")
        return PROFIL_DEFAUT.copy()


# ═══════════════════════════════════════════
# 💾 SAUVEGARDE
# ═══════════════════════════════════════════
def sauvegarder_profil(profil: dict) -> bool:
    """Sauvegarde le profil dans le JSON"""
    try:
        if not os.path.exists(DOSSIER_PROFIL):
            os.makedirs(DOSSIER_PROFIL)
        profil["date_modification"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M")
        with open(FICHIER_PROFIL, 'w', encoding='utf-8') as f:
            json.dump(profil, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"⚠️ Erreur sauvegarde profil : {e}")
        return False


# ═══════════════════════════════════════════
# 📷 GESTION PHOTO
# ═══════════════════════════════════════════
def sauvegarder_photo_depuis_pc(chemin_source: str) -> str:
    """Copie une photo depuis le PC vers le dossier profil"""
    try:
        if not os.path.exists(chemin_source):
            return ""
        if not os.path.exists(DOSSIER_PROFIL):
            os.makedirs(DOSSIER_PROFIL)

        # Garder l'extension d'origine
        ext = os.path.splitext(chemin_source)[1].lower()
        if ext not in [".png", ".jpg", ".jpeg", ".bmp"]:
            ext = ".png"

        chemin_dest = os.path.join(DOSSIER_PROFIL, f"photo{ext}")

        # Supprimer ancienne photo si différente extension
        for ancienne_ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            ancien = os.path.join(
                DOSSIER_PROFIL, f"photo{ancienne_ext}")
            if (os.path.exists(ancien) and
                    ancien != chemin_dest):
                try:
                    os.remove(ancien)
                except Exception:
                    pass

        shutil.copy2(chemin_source, chemin_dest)

        # Mettre à jour le profil
        profil = charger_profil()
        profil["photo_path"] = chemin_dest
        sauvegarder_profil(profil)

        return chemin_dest
    except Exception as e:
        print(f"⚠️ Erreur copie photo : {e}")
        return ""


def prendre_photo_webcam() -> str:
    """Ouvre la webcam et permet de prendre une photo"""
    try:
        import cv2

        if not os.path.exists(DOSSIER_PROFIL):
            os.makedirs(DOSSIER_PROFIL)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("⚠️ Webcam non détectée")
            return ""

        print("📷 Webcam ouverte ! ESPACE = photo, ESC = annuler")

        chemin_dest = os.path.join(DOSSIER_PROFIL, "photo.png")
        photo_prise = False

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Ajouter texte sur l'image
            cv2.putText(
                frame, "ESPACE = Photo  |  ESC = Annuler",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 0), 2)
            cv2.putText(
                frame, "NOKIROVA - Photo de profil",
                (10, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 2)

            cv2.imshow("NOKIROVA - Webcam", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == 32:  # SPACE
                cv2.imwrite(chemin_dest, frame)
                photo_prise = True
                break

        cap.release()
        cv2.destroyAllWindows()

        if photo_prise:
            # Supprimer autres formats
            for ext in [".jpg", ".jpeg", ".bmp"]:
                ancien = os.path.join(
                    DOSSIER_PROFIL, f"photo{ext}")
                if os.path.exists(ancien):
                    try:
                        os.remove(ancien)
                    except Exception:
                        pass

            # Mettre à jour profil
            profil = charger_profil()
            profil["photo_path"] = chemin_dest
            sauvegarder_profil(profil)
            return chemin_dest

        return ""
    except ImportError:
        print("⚠️ opencv-python non installé")
        return ""
    except Exception as e:
        print(f"⚠️ Erreur webcam : {e}")
        return ""


def get_photo_path() -> str:
    """Retourne le chemin de la photo actuelle (s'il existe)"""
    profil = charger_profil()
    chemin = profil.get("photo_path", "")
    if chemin and os.path.exists(chemin):
        return chemin
    # Chercher dans le dossier
    for ext in [".png", ".jpg", ".jpeg", ".bmp"]:
        chemin = os.path.join(DOSSIER_PROFIL, f"photo{ext}")
        if os.path.exists(chemin):
            return chemin
    return ""


def supprimer_photo() -> bool:
    """Supprime la photo de profil"""
    try:
        for ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            chemin = os.path.join(
                DOSSIER_PROFIL, f"photo{ext}")
            if os.path.exists(chemin):
                os.remove(chemin)
        profil = charger_profil()
        profil["photo_path"] = ""
        sauvegarder_profil(profil)
        return True
    except Exception as e:
        print(f"⚠️ Erreur suppression photo : {e}")
        return False


# ═══════════════════════════════════════════
# 📊 UTILITAIRES
# ═══════════════════════════════════════════
def profil_est_rempli() -> bool:
    """Vérifie si le profil a au moins le nom rempli"""
    profil = charger_profil()
    return bool(profil.get("nom_complet", "").strip())


def get_nom_affichage() -> str:
    """Retourne le nom à afficher (ou défaut)"""
    profil = charger_profil()
    nom = profil.get("nom_complet", "").strip()
    return nom if nom else "Étudiant NOKIROVA"