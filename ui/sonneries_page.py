# ui/sonneries_page.py - Page Sonneries NOKIROVA 🔊

import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import shutil
import sound_manager as sm
from ui.base import (
    VERT_EMERAUDE, VERT_HOVER, VERT_CLAIR, VERT_CORRECTION,
    VERT_FOND_CORRECTION,
    BLEU_ROYAL, BLEU_CIEL, BLEU_TRES_PALE,
    JAUNE_SOLEIL, JAUNE_PALE, OR_MODERNE,
    VIOLET_PREMIUM, VIOLET_LAVANDE, VIOLET_PALE,
    ROSE_SAKURA, ROSE_PALE,
    ORANGE_DORE, ORANGE_CLAIR, ORANGE_PALE,
    ROUGE, ROUGE_CLAIR,
    BLANC, BLANC_CASSE, GRIS_TEXTE, GRIS_DOUX, GRIS_PERLE
)
from notifications import notification_succes


# Couleurs par catégorie de son
COULEURS_CATEGORIES = {
    "🎵 Zen": VIOLET_PALE,
    "🔔 Notif": BLEU_TRES_PALE,
    "🎉 Motivant": JAUNE_PALE,
}


class SonneriesPageMixin:

    # ═══════════════════════════════════════════
    # 🔊 PAGE SONNERIES
    # ═══════════════════════════════════════════

    def afficher_sonneries(self):
        self.vider_zone()
        self.afficher_titre("Sonneries", "🔊", VIOLET_PREMIUM)

        sm.init_dossier_sons()
        params = sm.charger_config_sons()

        # ── SCROLL ──
        scroll = ctk.CTkScrollableFrame(
            self.zone_principale, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # ── Bandeau info ──
        info = ctk.CTkFrame(
            scroll, fg_color=VIOLET_PALE, corner_radius=12)
        info.pack(fill="x", pady=5)
        ctk.CTkLabel(
            info,
            text="🔊 Personnalise les sons de NOKIROVA !\n"
                 "💡 Active/désactive chaque son • Teste avant de valider\n"
                 "📁 Mets tes .mp3 dans le dossier 'sounds/'",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=VIOLET_PREMIUM,
            justify="center").pack(pady=12)

        # ═══════════════════════════════════════════
        # 🔘 SWITCH GLOBAL
        # ═══════════════════════════════════════════
        cadre_global = ctk.CTkFrame(
            scroll, fg_color=VERT_EMERAUDE, corner_radius=12)
        cadre_global.pack(fill="x", pady=5)

        ligne_global = ctk.CTkFrame(
            cadre_global, fg_color="transparent")
        ligne_global.pack(fill="x", padx=15, pady=12)

        ctk.CTkLabel(
            ligne_global, text="🔊  Sons activés (général)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=BLANC).pack(side="left")

        var_global = ctk.BooleanVar(value=params.get("sons_actifs", True))

        def changer_global():
            sm.maj_param_son("sons_actifs", var_global.get())
            etat = "activés" if var_global.get() else "désactivés"
            notification_succes(
                self, "Sons modifiés", f"🔊 Sons {etat}")

        sw_global = ctk.CTkSwitch(
            ligne_global, text="", variable=var_global,
            command=changer_global,
            progress_color=BLANC,
            button_color=VERT_EMERAUDE,
            button_hover_color=VERT_HOVER,
            width=50)
        sw_global.pack(side="right")

        # ═══════════════════════════════════════════
        # 📥 BOUTON IMPORTER SES SONS
        # ═══════════════════════════════════════════
        cadre_import = ctk.CTkFrame(
            scroll, fg_color=BLEU_TRES_PALE, corner_radius=12)
        cadre_import.pack(fill="x", pady=8)

        ctk.CTkLabel(
            cadre_import,
            text="📁  Importe tes propres sons (.mp3 ou .wav)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=BLEU_ROYAL).pack(pady=(10, 5))

        ctk.CTkButton(
            cadre_import, text="➕  Importer un fichier son",
            command=self._importer_son,
            fg_color=BLEU_ROYAL, hover_color=BLEU_CIEL,
            text_color=BLANC, height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8).pack(
            fill="x", padx=15, pady=(0, 12))

        # ═══════════════════════════════════════════
        # 📊 STATISTIQUES DOSSIER SOUNDS/
        # ═══════════════════════════════════════════
        sons_dispo = sm.lister_sons_disponibles()
        cadre_stats = ctk.CTkFrame(
            scroll, fg_color=GRIS_PERLE, corner_radius=10)
        cadre_stats.pack(fill="x", pady=5)

        ctk.CTkLabel(
            cadre_stats,
            text=f"📂  {len(sons_dispo)} fichier(s) son dans le dossier",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=GRIS_TEXTE).pack(pady=10)

        # ═══════════════════════════════════════════
        # 🎼 LISTE DES ÉVÉNEMENTS
        # ═══════════════════════════════════════════
        # Grouper par catégorie
        categories = {}
        for cle, info in sm.EVENEMENTS.items():
            cat = info["categorie"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((cle, info))

        # Afficher chaque catégorie
        for cat, evenements in categories.items():
            # Titre catégorie
            cadre_cat = ctk.CTkFrame(
                scroll, fg_color=VIOLET_LAVANDE,
                corner_radius=10, height=35)
            cadre_cat.pack(fill="x", pady=(15, 5))
            cadre_cat.pack_propagate(False)

            ctk.CTkLabel(
                cadre_cat, text=cat.upper(),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=BLANC).pack(pady=8)

            # Événements de cette catégorie
            for cle_event, info_event in evenements:
                self._creer_carte_evenement(
                    scroll, cle_event, info_event, params, sons_dispo)

        # ═══════════════════════════════════════════
        # 🔄 RESET
        # ═══════════════════════════════════════════
        ctk.CTkButton(
            scroll, text="🔄  Réinitialiser tous les sons par défaut",
            command=self._reset_sons,
            fg_color=GRIS_DOUX, hover_color=ROUGE_CLAIR,
            text_color=BLANC, height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10).pack(fill="x", pady=15)

        # Espace bas
        ctk.CTkLabel(scroll, text="", height=15).pack()

    # ═══════════════════════════════════════════
    # 🎴 CARTE PAR ÉVÉNEMENT
    # ═══════════════════════════════════════════

    def _creer_carte_evenement(self, parent, cle, info, params, sons_dispo):
        """Crée une carte pour un événement sonore"""
        couleur_cat = COULEURS_CATEGORIES.get(info["categorie"], BLANC)

        carte = ctk.CTkFrame(
            parent, fg_color=BLANC, corner_radius=12,
            border_width=2, border_color=couleur_cat)
        carte.pack(fill="x", pady=4)

        # ── Ligne 1 : label + switch ──
        ligne1 = ctk.CTkFrame(carte, fg_color="transparent")
        ligne1.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            ligne1, text=info["label"],
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(
            side="left", fill="x", expand=True)

        # Switch actif/inactif
        var_actif = ctk.BooleanVar(
            value=params.get(f"actif_{cle}", True))

        def changer_actif():
            sm.maj_param_son(f"actif_{cle}", var_actif.get())

        ctk.CTkSwitch(
            ligne1, text="", variable=var_actif,
            command=changer_actif,
            progress_color=VERT_EMERAUDE,
            button_color=BLANC,
            button_hover_color=GRIS_PERLE,
            width=50).pack(side="right")

        # ── Ligne 2 : choix fichier + boutons ──
        ligne2 = ctk.CTkFrame(carte, fg_color="transparent")
        ligne2.pack(fill="x", padx=15, pady=(0, 10))

        son_actuel = params.get(f"son_{cle}", info["fichier_defaut"])

        # Vérifier existence
        existe = sm.son_existe(son_actuel)
        emoji_etat = "✅" if existe else "⚠️"

        # Menu déroulant pour choisir le son
        options_sons = ["[Aucun]"]
        if sons_dispo:
            options_sons += sons_dispo

        def changer_son(valeur):
            if valeur == "[Aucun]":
                sm.maj_param_son(f"son_{cle}", "")
            else:
                sm.maj_param_son(f"son_{cle}", valeur)
            self.afficher_sonneries()

        menu_son = ctk.CTkOptionMenu(
            ligne2, values=options_sons,
            command=changer_son,
            fg_color=couleur_cat,
            button_color=VIOLET_PREMIUM,
            text_color=GRIS_TEXTE,
            height=32, width=200,
            font=ctk.CTkFont(size=11),
            dropdown_font=ctk.CTkFont(size=11))

        if son_actuel and son_actuel in sons_dispo:
            menu_son.set(son_actuel)
        else:
            menu_son.set("[Aucun]")
        menu_son.pack(side="left", padx=(0, 5))

        # Status (existe ou non)
        ctk.CTkLabel(
            ligne2, text=emoji_etat,
            font=ctk.CTkFont(size=14)).pack(
            side="left", padx=5)

        # Bouton TEST
        ctk.CTkButton(
            ligne2, text="🔊 Tester",
            command=lambda c=cle: self._tester_son(c),
            fg_color=BLEU_ROYAL, hover_color=BLEU_CIEL,
            text_color=BLANC, height=32, width=80,
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=8).pack(side="right", padx=2)

    # ═══════════════════════════════════════════
    # 🎬 ACTIONS
    # ═══════════════════════════════════════════

    def _tester_son(self, cle_evenement):
        """Teste le son d'un événement"""
        params = sm.charger_config_sons()
        fichier = params.get(f"son_{cle_evenement}", "")

        if not fichier:
            messagebox.showinfo(
                "ℹ️", "Aucun son sélectionné pour cet événement.")
            return

        chemin = sm.get_chemin_son(fichier)

        if not os.path.exists(chemin):
            messagebox.showwarning(
                "⚠️ Fichier manquant",
                f"Le fichier '{fichier}' n'existe pas dans 'sounds/'\n\n"
                "💡 Télécharge-le ou importe-en un autre.")
            return

        # Tenter de jouer
        ok = sm.jouer_son_fichier(chemin)
        if ok:
            notification_succes(
                self, "🔊 Lecture", f"🎵 {fichier}")
        else:
            messagebox.showwarning(
                "⚠️", "Impossible de lire ce son.\n"
                      "💡 Vérifie le format (.mp3 recommandé)")

    def _importer_son(self):
        """Importe un fichier son depuis le PC"""
        chemin = filedialog.askopenfilename(
            title="Choisis un fichier son",
            filetypes=[
                ("Audio", "*.mp3 *.wav"),
                ("MP3", "*.mp3"),
                ("WAV", "*.wav")])

        if not chemin:
            return

        sm.init_dossier_sons()
        nom_fichier = os.path.basename(chemin)
        chemin_dest = os.path.join(sm.DOSSIER_SONS, nom_fichier)

        # Vérifier si existe déjà
        if os.path.exists(chemin_dest):
            if not messagebox.askyesno(
                    "⚠️ Existe déjà",
                    f"Le fichier '{nom_fichier}' existe déjà.\n"
                    "Le remplacer ?"):
                return

        try:
            shutil.copy2(chemin, chemin_dest)
            notification_succes(
                self, "Importé !", f"🎵 {nom_fichier}")
            messagebox.showinfo(
                "✅ Importé !",
                f"🎵 {nom_fichier}\n\n"
                f"📁 Disponible dans le menu déroulant\n"
                f"de chaque événement !")
            self.afficher_sonneries()
        except Exception as e:
            messagebox.showerror(
                "❌ Erreur", f"Import échoué :\n{str(e)}")

    def _reset_sons(self):
        """Réinitialise tous les paramètres son"""
        if messagebox.askyesno(
                "🔄 Réinitialiser",
                "Remettre TOUS les sons par défaut ?\n"
                "(Tous activés, fichiers par défaut)"):
            sm.sauvegarder_config_sons(sm._params_defaut())
            notification_succes(
                self, "Réinitialisé !", "🔄 Sons par défaut")
            self.afficher_sonneries()