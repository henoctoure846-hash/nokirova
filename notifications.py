# notifications.py - Système complet de notifications 🔔 NOKIROVA

import customtkinter as ctk
import os
import json
from datetime import datetime

# ═══════════════════════════════════════════
# 📦 IMPORT PLYER (notifications Windows)
# ═══════════════════════════════════════════
PLYER_OK = False
try:
    from plyer import notification as plyer_notif
    PLYER_OK = True
    print("✅ Plyer notifications prêtes 🔔")
except Exception as e:
    print(f"⚠️ Plyer indisponible : {e}")


# ═══════════════════════════════════════════
# ⚙️ FICHIER DE PARAMÈTRES
# ═══════════════════════════════════════════
CONFIG_FILE = "nokirova_notif_config.json"

PARAMS_DEFAUT = {
    "notif_windows": True,
    "notif_rappels": True,
    "notif_motivation": True,
    "notif_matin": True,
    "heure_matin": "08:00",
    "minutes_avant_tache": 10,
    "son_actif": True,
    "ne_pas_deranger": False,
    "dernier_rappel_matin": "",
    "taches_deja_notifiees": []
}


def charger_params():
    """Charge les paramètres de notifications"""
    if not os.path.exists(CONFIG_FILE):
        sauvegarder_params(PARAMS_DEFAUT)
        return PARAMS_DEFAUT.copy()
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            params = json.load(f)
        # Compléter avec valeurs par défaut si manquantes
        for k, v in PARAMS_DEFAUT.items():
            if k not in params:
                params[k] = v
        return params
    except Exception:
        return PARAMS_DEFAUT.copy()


def sauvegarder_params(params):
    """Sauvegarde les paramètres"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(params, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️ Erreur sauvegarde params : {e}")
        return False


def maj_param(cle, valeur):
    """Met à jour un seul paramètre"""
    params = charger_params()
    params[cle] = valeur
    sauvegarder_params(params)


# ═══════════════════════════════════════════
# 🪟 NOTIFICATION WINDOWS NATIVE
# ═══════════════════════════════════════════
def notification_windows(titre: str, message: str, duree: int = 5):
    """
    Affiche une vraie notification Windows (via plyer).
    """
    params = charger_params()
    if not params.get("notif_windows", True):
        return False
    if params.get("ne_pas_deranger", False):
        return False
    if not PLYER_OK:
        return False
    try:
        plyer_notif.notify(
            title=titre,
            message=message,
            app_name="NOKIROVA",
            timeout=duree
        )
        return True
    except Exception as e:
        print(f"⚠️ Notif Windows échouée : {e}")
        return False


# ═══════════════════════════════════════════
# 🎁 POPUPS INTERNES (existants, conservés)
# ═══════════════════════════════════════════
def notification_xp(parent, points: int, message: str = ""):
    """Popup de récompense XP"""
    popup = ctk.CTkToplevel(parent)
    popup.title("")
    popup.geometry("350x120+800+50")
    popup.configure(fg_color="#FFD93D")
    popup.attributes("-topmost", True)
    popup.overrideredirect(True)
    popup.attributes("-alpha", 0.95)

    frame = ctk.CTkFrame(popup, fg_color="#FFD93D", corner_radius=15)
    frame.pack(fill="both", expand=True, padx=2, pady=2)

    ctk.CTkLabel(frame, text=f"🎁  +{points} XP !",
                 font=ctk.CTkFont(size=24, weight="bold"),
                 text_color="#374151").pack(pady=(15, 5))

    if message:
        ctk.CTkLabel(frame, text=message,
                     font=ctk.CTkFont(size=12),
                     text_color="#374151").pack()

    popup.after(2000, popup.destroy)


def notification_badge(parent, badge_emoji: str,
                       badge_nom: str, badge_desc: str):
    """Popup nouveau badge"""
    popup = ctk.CTkToplevel(parent)
    popup.title("")
    popup.geometry("400x180+700+100")
    popup.configure(fg_color="#A855F7")
    popup.attributes("-topmost", True)
    popup.overrideredirect(True)

    frame = ctk.CTkFrame(popup, fg_color="#A855F7", corner_radius=18)
    frame.pack(fill="both", expand=True, padx=2, pady=2)

    ctk.CTkLabel(frame, text="🏆 NOUVEAU BADGE !",
                 font=ctk.CTkFont(size=14, weight="bold"),
                 text_color="#FFFFFF").pack(pady=(15, 5))

    ctk.CTkLabel(frame, text=badge_emoji,
                 font=ctk.CTkFont(size=40)).pack()

    ctk.CTkLabel(frame, text=badge_nom,
                 font=ctk.CTkFont(size=18, weight="bold"),
                 text_color="#FFFFFF").pack(pady=(0, 2))

    ctk.CTkLabel(frame, text=badge_desc,
                 font=ctk.CTkFont(size=11),
                 text_color="#FFFFFF").pack(pady=(0, 15))

    # Notif Windows en plus
    notification_windows(
        f"🏆 Nouveau badge : {badge_nom}", badge_desc)

    popup.after(3500, popup.destroy)


def notification_succes(parent, titre: str, message: str):
    """Popup de succès générique"""
    popup = ctk.CTkToplevel(parent)
    popup.title("")
    popup.geometry("380x100+750+60")
    popup.configure(fg_color="#00C853")
    popup.attributes("-topmost", True)
    popup.overrideredirect(True)

    frame = ctk.CTkFrame(popup, fg_color="#00C853", corner_radius=15)
    frame.pack(fill="both", expand=True, padx=2, pady=2)

    ctk.CTkLabel(frame, text=f"✅ {titre}",
                 font=ctk.CTkFont(size=16, weight="bold"),
                 text_color="#FFFFFF").pack(pady=(15, 3))

    ctk.CTkLabel(frame, text=message,
                 font=ctk.CTkFont(size=11),
                 text_color="#FFFFFF").pack()

    popup.after(2500, popup.destroy)


# ═══════════════════════════════════════════
# 🔔 NOUVELLES NOTIFICATIONS (3.4)
# ═══════════════════════════════════════════

def notification_rappel(parent, titre: str, message: str):
    """Popup rappel de tâche (orange)"""
    popup = ctk.CTkToplevel(parent)
    popup.title("")
    popup.geometry("400x130+750+80")
    popup.configure(fg_color="#F59E0B")
    popup.attributes("-topmost", True)
    popup.overrideredirect(True)

    frame = ctk.CTkFrame(popup, fg_color="#F59E0B", corner_radius=15)
    frame.pack(fill="both", expand=True, padx=2, pady=2)

    ctk.CTkLabel(frame, text=f"⏰ {titre}",
                 font=ctk.CTkFont(size=16, weight="bold"),
                 text_color="#FFFFFF").pack(pady=(15, 5))

    ctk.CTkLabel(frame, text=message,
                 font=ctk.CTkFont(size=12),
                 text_color="#FFFFFF", wraplength=370).pack(pady=(0, 15))

    notification_windows(f"⏰ {titre}", message)
    popup.after(5000, popup.destroy)


def notification_motivation(parent, titre: str, message: str):
    """Popup motivation (violet)"""
    popup = ctk.CTkToplevel(parent)
    popup.title("")
    popup.geometry("400x130+750+80")
    popup.configure(fg_color="#7B61FF")
    popup.attributes("-topmost", True)
    popup.overrideredirect(True)

    frame = ctk.CTkFrame(popup, fg_color="#7B61FF", corner_radius=15)
    frame.pack(fill="both", expand=True, padx=2, pady=2)

    ctk.CTkLabel(frame, text=f"💪 {titre}",
                 font=ctk.CTkFont(size=16, weight="bold"),
                 text_color="#FFFFFF").pack(pady=(15, 5))

    ctk.CTkLabel(frame, text=message,
                 font=ctk.CTkFont(size=12),
                 text_color="#FFFFFF", wraplength=370).pack(pady=(0, 15))

    notification_windows(f"💪 {titre}", message)
    popup.after(4000, popup.destroy)


def notification_matin(parent, nb_taches: int):
    """Notification du matin avec les tâches du jour"""
    if nb_taches == 0:
        titre = "🌅 Bonne journée !"
        message = "Aucune tâche planifiée aujourd'hui.\n💡 Pense à en ajouter !"
    else:
        titre = f"🌅 Bonjour ! {nb_taches} tâche(s) aujourd'hui"
        message = f"📋 Ouvre ton planificateur pour voir tes objectifs."

    notification_motivation(parent, titre, message)


# ═══════════════════════════════════════════
# 🔍 VÉRIFICATEUR AUTO (timer arrière-plan)
# ═══════════════════════════════════════════

def verifier_notifications_auto(parent):
    """
    Vérifie s'il y a des notifications à envoyer.
    Appelée toutes les minutes par le timer de interface.py
    """
    try:
        import database as db
        params = charger_params()

        if params.get("ne_pas_deranger", False):
            return

        maintenant = datetime.now()
        h_now = maintenant.strftime("%H:%M")
        date_now = maintenant.strftime("%Y-%m-%d")

        # ── 1. NOTIFICATION DU MATIN ──
        if params.get("notif_matin", True):
            heure_matin = params.get("heure_matin", "08:00")
            dernier = params.get("dernier_rappel_matin", "")
            if h_now == heure_matin and dernier != date_now:
                try:
                    taches = db.lister_taches_jour()
                    notification_matin(parent, len(taches))
                    maj_param("dernier_rappel_matin", date_now)
                except Exception:
                    pass

        # ── 2. RAPPELS AVANT TÂCHES ──
        if params.get("notif_rappels", True):
            try:
                taches = db.lister_taches_jour()
                minutes_avant = params.get("minutes_avant_tache", 10)
                deja_notif = params.get("taches_deja_notifiees", [])
                nouveaux = []

                for tache in taches:
                    (id_t, titre, desc, matiere, type_t, prio,
                     date_t, heure, duree, statut,
                     recur, cours_id) = tache

                    if statut == "faite":
                        continue

                    # Construire le datetime de la tâche
                    try:
                        dt_tache = datetime.strptime(
                            f"{date_t} {heure}", "%Y-%m-%d %H:%M")
                    except Exception:
                        continue

                    # Diff en minutes
                    diff_min = (dt_tache - maintenant).total_seconds() / 60

                    # Clé unique pour éviter doublons
                    cle = f"{id_t}_{date_t}"

                    # Rappel "X minutes avant"
                    if 0 < diff_min <= minutes_avant and cle not in deja_notif:
                        notification_rappel(
                            parent,
                            f"Dans {int(diff_min)} min",
                            f"📚 {titre} • 🎯 {matiere}")
                        nouveaux.append(cle)

                    # Rappel "C'est l'heure !"
                    cle_heure = f"{id_t}_{date_t}_now"
                    if (-1 <= diff_min < 1 and
                            cle_heure not in deja_notif):
                        notification_rappel(
                            parent,
                            "C'est l'heure !",
                            f"⏰ {titre} commence maintenant\n"
                            f"🎯 {matiere} • ⏱️ {duree} min")
                        nouveaux.append(cle_heure)

                # Sauvegarder les notifs envoyées
                if nouveaux:
                    deja_notif.extend(nouveaux)
                    # Garder seulement les 100 dernières
                    if len(deja_notif) > 100:
                        deja_notif = deja_notif[-100:]
                    maj_param("taches_deja_notifiees", deja_notif)
            except Exception as e:
                print(f"⚠️ Erreur rappels : {e}")

    except Exception as e:
        print(f"⚠️ Erreur vérif notifs : {e}")