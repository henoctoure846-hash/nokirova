# sound_manager.py - Gestion centralisée des sons NOKIROVA 🔊

import os
import json
import threading

DOSSIER_SONS = "sounds"
CONFIG_SONS = "nokirova_sons_config.json"


# ═══════════════════════════════════════════
# 🎼 CATALOGUE DES ÉVÉNEMENTS
# ═══════════════════════════════════════════
EVENEMENTS = {
    "pomodoro_fin": {
        "label": "🍅 Fin de session Pomodoro",
        "fichier_defaut": "pomodoro_fin.mp3",
        "categorie": "🎵 Zen"
    },
    "notification": {
        "label": "🔔 Notification générale",
        "fichier_defaut": "notification.mp3",
        "categorie": "🔔 Notif"
    },
    "xp_gagne": {
        "label": "⭐ XP gagnés",
        "fichier_defaut": "xp_gagne.mp3",
        "categorie": "🎉 Motivant"
    },
    "badge_unlock": {
        "label": "🏆 Badge débloqué",
        "fichier_defaut": "badge_unlock.mp3",
        "categorie": "🎉 Motivant"
    },
    "succes": {
        "label": "✅ Action réussie",
        "fichier_defaut": "succes.mp3",
        "categorie": "🔔 Notif"
    },
    "rappel": {
        "label": "⏰ Rappel de tâche",
        "fichier_defaut": "rappel.mp3",
        "categorie": "🔔 Notif"
    },
    "qcm_bon": {
        "label": "🎯 Bonne réponse QCM",
        "fichier_defaut": "qcm_bon.mp3",
        "categorie": "🎉 Motivant"
    },
    "qcm_mauvais": {
        "label": "❌ Mauvaise réponse QCM",
        "fichier_defaut": "qcm_mauvais.mp3",
        "categorie": "🔔 Notif"
    },
    "clic": {
        "label": "👆 Clic bouton",
        "fichier_defaut": "clic.mp3",
        "categorie": "🔔 Notif"
    },
    "zen": {
        "label": "🧘 Son zen (méditation)",
        "fichier_defaut": "zen.mp3",
        "categorie": "🎵 Zen"
    },
}


# ═══════════════════════════════════════════
# ⚙️ PARAMÈTRES PAR DÉFAUT
# ═══════════════════════════════════════════
def _params_defaut():
    """Génère les paramètres par défaut"""
    params = {"sons_actifs": True}
    for cle, info in EVENEMENTS.items():
        params[f"son_{cle}"] = info["fichier_defaut"]
        params[f"actif_{cle}"] = True
    return params


# ═══════════════════════════════════════════
# 📥 CHARGEMENT / SAUVEGARDE
# ═══════════════════════════════════════════
def charger_config_sons() -> dict:
    """Charge la config des sons"""
    if not os.path.exists(CONFIG_SONS):
        params = _params_defaut()
        sauvegarder_config_sons(params)
        return params
    try:
        with open(CONFIG_SONS, 'r', encoding='utf-8') as f:
            params = json.load(f)
        # Compléter si manquant
        defaut = _params_defaut()
        for cle, val in defaut.items():
            if cle not in params:
                params[cle] = val
        return params
    except Exception:
        return _params_defaut()


def sauvegarder_config_sons(params: dict) -> bool:
    """Sauvegarde la config"""
    try:
        with open(CONFIG_SONS, 'w', encoding='utf-8') as f:
            json.dump(params, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️ Erreur sauvegarde sons : {e}")
        return False


def maj_param_son(cle: str, valeur):
    """Met à jour un seul paramètre"""
    params = charger_config_sons()
    params[cle] = valeur
    sauvegarder_config_sons(params)


# ═══════════════════════════════════════════
# 🔊 LECTURE DE SONS
# ═══════════════════════════════════════════
def jouer_son_fichier(chemin: str) -> bool:
    """Joue un fichier son (méthode robuste)"""
    if not chemin or not os.path.exists(chemin):
        return False

    try:
        # Méthode 1 : playsound
        try:
            from playsound import playsound
            threading.Thread(
                target=lambda: playsound(chemin, block=False),
                daemon=True).start()
            return True
        except Exception:
            pass

        # Méthode 2 : winsound (Windows, WAV uniquement)
        try:
            import winsound
            if chemin.lower().endswith('.wav'):
                winsound.PlaySound(
                    chemin,
                    winsound.SND_FILENAME | winsound.SND_ASYNC)
                return True
        except Exception:
            pass

        # Méthode 3 : fallback - juste un beep système
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_OK)
            return True
        except Exception:
            pass

    except Exception as e:
        print(f"⚠️ Lecture son : {e}")

    return False


def jouer_son_evenement(evenement: str) -> bool:
    """Joue le son associé à un événement"""
    params = charger_config_sons()

    # Vérifier si sons globaux actifs
    if not params.get("sons_actifs", True):
        return False

    # Vérifier si ce son spécifique est actif
    if not params.get(f"actif_{evenement}", True):
        return False

    # Récupérer le fichier
    fichier = params.get(
        f"son_{evenement}",
        EVENEMENTS.get(evenement, {}).get("fichier_defaut", ""))

    if not fichier:
        return False

    chemin = os.path.join(DOSSIER_SONS, fichier)
    return jouer_son_fichier(chemin)


# ═══════════════════════════════════════════
# 📂 UTILITAIRES
# ═══════════════════════════════════════════
def lister_sons_disponibles() -> list:
    """Liste tous les .mp3 / .wav présents dans sounds/"""
    if not os.path.exists(DOSSIER_SONS):
        return []
    try:
        fichiers = []
        for f in os.listdir(DOSSIER_SONS):
            if f.lower().endswith(('.mp3', '.wav')):
                fichiers.append(f)
        return sorted(fichiers)
    except Exception:
        return []


def son_existe(nom_fichier: str) -> bool:
    """Vérifie si un fichier son existe"""
    if not nom_fichier:
        return False
    return os.path.exists(os.path.join(DOSSIER_SONS, nom_fichier))


def init_dossier_sons():
    """Crée le dossier sounds/ si nécessaire"""
    if not os.path.exists(DOSSIER_SONS):
        os.makedirs(DOSSIER_SONS)


def get_chemin_son(nom_fichier: str) -> str:
    """Retourne le chemin complet d'un son"""
    return os.path.join(DOSSIER_SONS, nom_fichier)