# ui/aide_profil.py - Pages Aide et Profil NOKIROVA 🌸 (V2 COMPLET)

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from PIL import Image
import database as db
import profil_manager as pm
from ui.base import (VIOLET_PREMIUM, VIOLET_LAVANDE, VIOLET_PALE, VIOLET_CLAIR,
                     JAUNE_PALE, JAUNE_CLAIR, ORANGE_DORE, ORANGE_CLAIR,
                     BLEU_TRES_PALE, BLEU_ROYAL, BLEU_CIEL,
                     ROSE_PALE, ROSE_SAKURA,
                     VERT_EMERAUDE, VERT_HOVER, VERT_CLAIR,
                     VERT_FOND_CORRECTION,
                     ROUGE, ROUGE_CLAIR,
                     BLANC, GRIS_TEXTE, GRIS_DOUX, GRIS_PERLE,
                     OR_MODERNE)
from notifications import notification_succes


class AideProfilMixin:

    # ═══════════════════════════════════════════
    # ⌨️ AIDE
    # ═══════════════════════════════════════════

    def afficher_aide(self):
        self.vider_zone()
        self.afficher_titre("Aide & Raccourcis", "⌨️", VIOLET_PREMIUM)
        aide = self.creer_zone_texte(500)
        aide.insert("0.0", """🌸 BIENVENUE DANS L'AIDE NOKIROVA 🌸

⌨️ RACCOURCIS CLAVIER :
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ctrl + H    →  Accueil
Ctrl + B    →  Bibliothèque
Ctrl + L    →  Historique
Ctrl + N    →  Mes Notes
Ctrl + F    →  Flashcards
Ctrl + P    →  Pomodoro
Ctrl + K    →  Recherche
Ctrl + G    →  Graphiques
Ctrl + J    →  Planificateur
Ctrl + M    →  Scan Multi-pages
Ctrl + U    →  Notifications
Ctrl + V    →  Vidéos révision
Ctrl + E    →  Importer partage
Ctrl + I    →  Importer un cours
Ctrl + R    →  Résumé
Ctrl + Q    →  QCM
Ctrl + S    →  Sécurité PIN
Ctrl + D    →  Mode sombre / jour
F1          →  Cette page d'aide
━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️ POMODORO :
- Configure travail / pause / pause longue
- Lance le timer et travaille !
- Le timer CONTINUE même si tu changes de page
- Son + notification Windows à la fin
- XP bonus à chaque session terminée

🔍 RECHERCHE :
- Cherche dans TOUS tes cours
- Filtre par matière

📅 PLANIFICATEUR :
- 3 vues : Jour / Semaine / Mois
- Tâches récurrentes
- Couleurs par matière
- Rappels automatiques

📚 SCAN MULTI-PAGES :
- Jusqu'à 50 images d'un coup
- OCR intelligent
- Correction IA automatique

🌍 TRADUCTION :
- 12 langues disponibles
- Traduction intelligente avec contexte

🎬 VIDÉOS RÉVISION :
- 7 voix IA au choix
- 4 styles aléatoires
- 4 vitesses (lent → ultra rapide)
- Diaporama HTML interactif

🤝 PARTAGE DE COURS :
- Exporte en .nokirova
- Inclus notes, flashcards, historique
- Partage facilement avec tes amis

🔔 NOTIFICATIONS :
- Rappels automatiques de tâches
- Notifications Windows natives
- Mode "Ne pas déranger"

✨ Bonne révision avec NOKIROVA ! 🌸
""")

    # ═══════════════════════════════════════════
    # 🏆 PROFIL COMPLET
    # ═══════════════════════════════════════════

    def afficher_profil(self):
        self.vider_zone()
        self.afficher_titre("Mon Profil", "🏆", VIOLET_PREMIUM)

        # ── SCROLL principal ──
        scroll = ctk.CTkScrollableFrame(
            self.zone_principale, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # Charger le profil
        profil = pm.charger_profil()
        stats = db.get_stats()
        titre_niveau = db.get_niveau_titre(stats["niveau"])

        # ═══════════════════════════════════════════
        # 👤 CARTE PROFIL HAUT (photo + nom)
        # ═══════════════════════════════════════════
        carte_top = ctk.CTkFrame(
            scroll, fg_color=VIOLET_PALE, corner_radius=20)
        carte_top.pack(fill="x", pady=(0, 10))

        contenu_top = ctk.CTkFrame(
            carte_top, fg_color="transparent")
        contenu_top.pack(pady=20, padx=20)

        # ── Photo de profil ──
        photo_path = pm.get_photo_path()
        cadre_photo = ctk.CTkFrame(
            contenu_top, fg_color=BLANC,
            corner_radius=70, width=140, height=140)
        cadre_photo.pack(side="left", padx=(0, 20))
        cadre_photo.pack_propagate(False)

        if photo_path and os.path.exists(photo_path):
            try:
                img = Image.open(photo_path)
                img.thumbnail((130, 130))
                photo = ctk.CTkImage(
                    light_image=img, dark_image=img, size=(130, 130))
                ctk.CTkLabel(
                    cadre_photo, image=photo, text="").pack(
                    pady=5, padx=5)
            except Exception:
                ctk.CTkLabel(
                    cadre_photo, text="👤",
                    font=ctk.CTkFont(size=70)).pack(expand=True)
        else:
            ctk.CTkLabel(
                cadre_photo, text="👤",
                font=ctk.CTkFont(size=70)).pack(expand=True)

        # ── Infos à droite ──
        infos = ctk.CTkFrame(
            contenu_top, fg_color="transparent")
        infos.pack(side="left", fill="x", expand=True)

        nom = profil.get("nom_complet", "").strip() or "Étudiant NOKIROVA"
        ctk.CTkLabel(
            infos, text=nom,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=VIOLET_PREMIUM, anchor="w").pack(
            fill="x", pady=(5, 2))

        ctk.CTkLabel(
            infos, text=titre_niveau,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ORANGE_DORE, anchor="w").pack(
            fill="x", pady=2)

        ctk.CTkLabel(
            infos,
            text=f"⭐ Niveau {stats['niveau']}  •  ✨ {stats['xp']} XP",
            font=ctk.CTkFont(size=13),
            text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", pady=2)

        if profil.get("universite"):
            ctk.CTkLabel(
                infos, text=f"🎓 {profil['universite']}",
                font=ctk.CTkFont(size=12),
                text_color=GRIS_TEXTE, anchor="w").pack(
                fill="x", pady=2)

        # Bouton MODIFIER
        ctk.CTkButton(
            infos, text="✏️  Modifier mon profil",
            command=self._ouvrir_form_profil,
            fg_color=VIOLET_PREMIUM, hover_color=VIOLET_LAVANDE,
            text_color=BLANC, corner_radius=10, height=36,
            font=ctk.CTkFont(size=12, weight="bold")).pack(
            fill="x", pady=(10, 0))

        # ═══════════════════════════════════════════
        # 📊 BARRE NIVEAU
        # ═══════════════════════════════════════════
        carte_xp = ctk.CTkFrame(
            scroll, fg_color=JAUNE_PALE, corner_radius=15)
        carte_xp.pack(fill="x", pady=8)

        xp_actuel = stats["xp"] % 100
        progress = ctk.CTkProgressBar(
            carte_xp, progress_color=VERT_EMERAUDE,
            fg_color=BLANC, height=20, corner_radius=10)
        progress.set(xp_actuel / 100)
        progress.pack(pady=12, padx=20, fill="x")

        ctk.CTkLabel(
            carte_xp,
            text=f"🎯 {xp_actuel}/100 XP vers le niveau "
                 f"{stats['niveau'] + 1}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=GRIS_TEXTE).pack(pady=(0, 12))

        # ═══════════════════════════════════════════
        # 📝 INFOS PERSONNELLES (si remplies)
        # ═══════════════════════════════════════════
        infos_data = [
            ("📧  Email", profil.get("email")),
            ("📱  Téléphone", profil.get("numero")),
            ("🎓  Université", profil.get("universite")),
            ("📅  Année d'étude", profil.get("annee_etude")),
            ("🎂  Date naissance", profil.get("date_naissance")),
        ]

        infos_remplies = [
            (lab, val) for lab, val in infos_data if val and val.strip()]

        if infos_remplies:
            ctk.CTkLabel(
                scroll, text="📝  INFORMATIONS PERSONNELLES",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=VIOLET_PREMIUM, anchor="w").pack(
                fill="x", pady=(15, 5))

            cadre_infos = ctk.CTkFrame(
                scroll, fg_color=BLANC, corner_radius=12,
                border_width=2, border_color=VIOLET_PALE)
            cadre_infos.pack(fill="x", pady=5)

            for label, valeur in infos_remplies:
                ligne = ctk.CTkFrame(
                    cadre_infos, fg_color="transparent")
                ligne.pack(fill="x", padx=15, pady=6)

                ctk.CTkLabel(
                    ligne, text=label,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=GRIS_TEXTE, anchor="w",
                    width=180).pack(side="left")

                ctk.CTkLabel(
                    ligne, text=valeur,
                    font=ctk.CTkFont(size=12),
                    text_color=VIOLET_PREMIUM, anchor="w").pack(
                    side="left", padx=10)

        # ═══════════════════════════════════════════
        # 💭 BIO (si remplie)
        # ═══════════════════════════════════════════
        bio = profil.get("bio", "").strip()
        if bio:
            ctk.CTkLabel(
                scroll, text="💭  À PROPOS DE MOI",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=VIOLET_PREMIUM, anchor="w").pack(
                fill="x", pady=(15, 5))

            cadre_bio = ctk.CTkFrame(
                scroll, fg_color=ROSE_PALE, corner_radius=12)
            cadre_bio.pack(fill="x", pady=5)

            ctk.CTkLabel(
                cadre_bio, text=bio,
                font=ctk.CTkFont(size=13, slant="italic"),
                text_color=GRIS_TEXTE,
                wraplength=700, justify="left").pack(
                padx=20, pady=15)

        # ═══════════════════════════════════════════
        # 🔥 STREAK
        # ═══════════════════════════════════════════
        carte_streak = ctk.CTkFrame(
            scroll, fg_color=ORANGE_CLAIR, corner_radius=15)
        carte_streak.pack(fill="x", pady=8)
        ctk.CTkLabel(
            carte_streak,
            text=f"🔥 STREAK : {stats['streak']} jour(s) consécutif(s) !",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=BLANC).pack(pady=15)

        # ═══════════════════════════════════════════
        # 📊 STATISTIQUES
        # ═══════════════════════════════════════════
        ctk.CTkLabel(
            scroll, text="📊  TES STATISTIQUES",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=BLEU_ROYAL, anchor="w").pack(
            fill="x", pady=(15, 5))

        carte_stats = ctk.CTkFrame(
            scroll, fg_color=BLEU_TRES_PALE, corner_radius=15)
        carte_stats.pack(fill="x", pady=5)

        try:
            stats_pomo = db.get_stats_pomodoro()
        except Exception:
            stats_pomo = {"total_sessions": 0, "total_minutes": 0}

        ctk.CTkLabel(
            carte_stats,
            text=f"📚 Cours importés : {stats['cours_importes']}\n"
                 f"💬 Questions posées : {stats['questions_posees']}\n"
                 f"🎧 Audios créés : {stats['audios_crees']}\n"
                 f"🎯 QCM réussis : {stats['qcm_reussis']}\n"
                 f"🍅 Sessions Pomodoro : {stats_pomo['total_sessions']}\n"
                 f"⏱️ Minutes de travail : {stats_pomo['total_minutes']}",
            font=ctk.CTkFont(size=13),
            text_color=GRIS_TEXTE,
            justify="left").pack(pady=15, padx=20)

        # ═══════════════════════════════════════════
        # 🏆 BADGES
        # ═══════════════════════════════════════════
        badges = db.lister_badges()
        ctk.CTkLabel(
            scroll, text=f"🏆  BADGES DÉBLOQUÉS ({len(badges)})",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=VIOLET_PREMIUM, anchor="w").pack(
            fill="x", pady=(15, 5))

        carte_badges = ctk.CTkFrame(
            scroll, fg_color=ROSE_PALE, corner_radius=15)
        carte_badges.pack(fill="x", pady=5)

        if badges:
            for nom, desc, emoji, date in badges:
                badge_frame = ctk.CTkFrame(
                    carte_badges, fg_color=BLANC,
                    corner_radius=10)
                badge_frame.pack(fill="x", padx=15, pady=4)
                ctk.CTkLabel(
                    badge_frame, text=f"{emoji}  {nom}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=GRIS_TEXTE).pack(
                    anchor="w", padx=15, pady=(8, 0))
                ctk.CTkLabel(
                    badge_frame, text=desc,
                    font=ctk.CTkFont(size=11),
                    text_color=GRIS_DOUX).pack(
                    anchor="w", padx=15, pady=(0, 8))
            ctk.CTkLabel(carte_badges, text="", height=5).pack()
        else:
            ctk.CTkLabel(
                carte_badges,
                text="🎯 Continue à utiliser NOKIROVA pour\n"
                     "débloquer des badges !",
                font=ctk.CTkFont(size=13),
                text_color=GRIS_TEXTE,
                justify="center").pack(pady=20)

        # Espace bas
        ctk.CTkLabel(scroll, text="", height=10).pack()

    # ═══════════════════════════════════════════
    # ✏️ FORMULAIRE DE MODIFICATION
    # ═══════════════════════════════════════════

    def _ouvrir_form_profil(self):
        """Popup formulaire pour modifier le profil"""
        profil = pm.charger_profil()

        popup = ctk.CTkToplevel(self)
        popup.title("✏️ Modifier mon profil")
        popup.geometry("600x700")
        popup.configure(fg_color=BLANC)
        popup.transient(self)

        scroll = ctk.CTkScrollableFrame(
            popup, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            scroll, text="✏️  Modifier mon profil",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=VIOLET_PREMIUM).pack(pady=(0, 12))

        # ═══════════════════════════════════════════
        # 📷 SECTION PHOTO
        # ═══════════════════════════════════════════
        cadre_photo = ctk.CTkFrame(
            scroll, fg_color=VIOLET_PALE, corner_radius=12)
        cadre_photo.pack(fill="x", pady=8)

        ctk.CTkLabel(
            cadre_photo, text="📷  PHOTO DE PROFIL",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=VIOLET_PREMIUM).pack(pady=(12, 8))

        # Aperçu photo actuelle
        photo_path = pm.get_photo_path()
        if photo_path and os.path.exists(photo_path):
            try:
                img = Image.open(photo_path)
                img.thumbnail((100, 100))
                photo = ctk.CTkImage(
                    light_image=img, dark_image=img, size=(100, 100))
                ctk.CTkLabel(
                    cadre_photo, image=photo, text="").pack(pady=5)
            except Exception:
                ctk.CTkLabel(
                    cadre_photo, text="👤",
                    font=ctk.CTkFont(size=60)).pack(pady=5)
        else:
            ctk.CTkLabel(
                cadre_photo, text="👤",
                font=ctk.CTkFont(size=60)).pack(pady=5)

        # Boutons photo
        btns_photo = ctk.CTkFrame(
            cadre_photo, fg_color="transparent")
        btns_photo.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(
            btns_photo, text="📁  Depuis PC",
            command=lambda: self._photo_depuis_pc(popup),
            fg_color=BLEU_ROYAL, hover_color=BLEU_CIEL,
            text_color=BLANC, height=35,
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=8).pack(
            side="left", padx=2, expand=True, fill="x")

        ctk.CTkButton(
            btns_photo, text="📷  Webcam",
            command=lambda: self._photo_webcam(popup),
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, height=35,
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=8).pack(
            side="left", padx=2, expand=True, fill="x")

        ctk.CTkButton(
            btns_photo, text="🗑️  Supprimer",
            command=lambda: self._supprimer_photo(popup),
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, height=35,
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=8).pack(
            side="left", padx=2, expand=True, fill="x")

        # ═══════════════════════════════════════════
        # 📝 CHAMPS PROFIL
        # ═══════════════════════════════════════════
        champs = {}

        def creer_champ(label, cle, placeholder="", multiline=False):
            ctk.CTkLabel(
                scroll, text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=GRIS_TEXTE, anchor="w").pack(
                fill="x", pady=(8, 2))
            if multiline:
                widget = ctk.CTkTextbox(
                    scroll, height=80,
                    font=ctk.CTkFont(size=12))
                widget.pack(fill="x", pady=(0, 5))
                if profil.get(cle):
                    widget.insert("0.0", profil[cle])
            else:
                widget = ctk.CTkEntry(
                    scroll, height=38, placeholder_text=placeholder,
                    font=ctk.CTkFont(size=13))
                widget.pack(fill="x", pady=(0, 5))
                if profil.get(cle):
                    widget.insert(0, profil[cle])
            champs[cle] = widget

        creer_champ(
            "👤  Nom complet *",
            "nom_complet", "Hénoc TOURÉ")
        creer_champ(
            "📧  Email",
            "email", "henoc@example.com")
        creer_champ(
            "📱  Numéro de téléphone",
            "numero", "+228 90 12 34 56")
        creer_champ(
            "🎓  Université",
            "universite", "Université de Lomé")
        creer_champ(
            "📅  Année d'étude",
            "annee_etude", "Licence 2 - Économie")
        creer_champ(
            "🎂  Date de naissance",
            "date_naissance", "15/03/2003")
        creer_champ(
            "💭  Bio (à propos de toi)",
            "bio", "", multiline=True)

        # ═══════════════════════════════════════════
        # 💾 BOUTONS VALIDER / ANNULER
        # ═══════════════════════════════════════════
        def sauvegarder():
            nom = champs["nom_complet"].get().strip()
            if not nom:
                messagebox.showwarning(
                    "⚠️", "Le nom complet est obligatoire !")
                return

            nouveau_profil = pm.charger_profil()
            nouveau_profil["nom_complet"] = nom
            nouveau_profil["email"] = champs["email"].get().strip()
            nouveau_profil["numero"] = champs["numero"].get().strip()
            nouveau_profil["universite"] = champs["universite"].get().strip()
            nouveau_profil["annee_etude"] = champs["annee_etude"].get().strip()
            nouveau_profil["date_naissance"] = champs["date_naissance"].get().strip()
            nouveau_profil["bio"] = champs["bio"].get("0.0", "end").strip()

            if pm.sauvegarder_profil(nouveau_profil):
                notification_succes(
                    self, "Sauvegardé !",
                    f"👤 Profil de {nom} mis à jour")
                popup.destroy()
                self.afficher_profil()
                self._recompenser(5, "Profil mis à jour ! 👤")
            else:
                messagebox.showerror(
                    "❌", "Erreur lors de la sauvegarde !")

        btns = ctk.CTkFrame(scroll, fg_color="transparent")
        btns.pack(fill="x", pady=15)

        ctk.CTkButton(
            btns, text="💾  SAUVEGARDER",
            command=sauvegarder,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=12).pack(
            side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            btns, text="❌  Annuler",
            command=popup.destroy,
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=12).pack(
            side="left", padx=5, expand=True, fill="x")

    # ═══════════════════════════════════════════
    # 📷 ACTIONS PHOTO
    # ═══════════════════════════════════════════

    def _photo_depuis_pc(self, popup):
        chemin = filedialog.askopenfilename(
            title="Choisis une photo",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.bmp"),
                ("PNG", "*.png"),
                ("JPG", "*.jpg *.jpeg")])
        if chemin:
            resultat = pm.sauvegarder_photo_depuis_pc(chemin)
            if resultat:
                notification_succes(
                    self, "Photo OK !", "📷 Photo enregistrée")
                popup.destroy()
                self._ouvrir_form_profil()
            else:
                messagebox.showerror(
                    "❌", "Impossible de charger la photo")

    def _photo_webcam(self, popup):
        if not messagebox.askyesno(
                "📷 Webcam",
                "Ouvrir la webcam ?\n\n"
                "💡 Une fenêtre va s'ouvrir.\n"
                "ESPACE = prendre la photo\n"
                "ESC = annuler"):
            return

        popup.withdraw()  # Cacher temporairement le popup
        resultat = pm.prendre_photo_webcam()
        popup.deiconify()  # Réafficher

        if resultat:
            notification_succes(
                self, "Photo prise !", "📷 Photo webcam enregistrée")
            popup.destroy()
            self._ouvrir_form_profil()
        else:
            messagebox.showwarning(
                "⚠️", "Photo non prise.\n"
                      "💡 Vérifie que ta webcam fonctionne.")

    def _supprimer_photo(self, popup):
        if messagebox.askyesno(
                "🗑️ Supprimer",
                "Supprimer la photo de profil ?"):
            if pm.supprimer_photo():
                notification_succes(
                    self, "Supprimée", "🗑️ Photo supprimée")
                popup.destroy()
                self._ouvrir_form_profil()