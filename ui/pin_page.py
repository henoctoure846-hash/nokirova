# ui/pin_page.py - Code PIN Sécurité NOKIROVA 🔒

import customtkinter as ctk
from tkinter import messagebox
import database as db
from ui.base import (VERT_EMERAUDE, VERT_HOVER, VERT_FOND_CORRECTION,
                     VERT_CORRECTION,
                     BLEU_ROYAL, BLEU_TRES_PALE,
                     VIOLET_PREMIUM, VIOLET_LAVANDE,
                     ROUGE, ROUGE_CLAIR, ROUGE_FOND,
                     JAUNE_PALE, ORANGE_DORE, ORANGE_CLAIR,
                     ROSE_PALE,
                     BLANC, BLANC_CASSE, GRIS_TEXTE, GRIS_DOUX, GRIS_PERLE)
from notifications import notification_succes


class PinPageMixin:

    # ═══════════════════════════════════════════
    # 🔒 PAGE SÉCURITÉ / CODE PIN
    # ═══════════════════════════════════════════

    def afficher_securite(self):
        self.vider_zone()
        self.afficher_titre("Sécurité & Code PIN", "🔒", VIOLET_PREMIUM)

        pin_actif = db.pin_existe()

        # ── Statut ──
        couleur_statut = VERT_FOND_CORRECTION if pin_actif else ROUGE_FOND
        emoji_statut = "✅" if pin_actif else "❌"
        texte_statut = "PIN ACTIVÉ" if pin_actif else "PIN DÉSACTIVÉ"
        couleur_texte = VERT_CORRECTION if pin_actif else ROUGE

        carte_statut = ctk.CTkFrame(
            self.zone_principale,
            fg_color=couleur_statut,
            corner_radius=15, height=70)
        carte_statut.pack(fill="x", pady=(0, 10))
        carte_statut.pack_propagate(False)

        ctk.CTkLabel(
            carte_statut,
            text=f"{emoji_statut}  STATUT : {texte_statut}",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=couleur_texte).pack(pady=22)

        # ── ZONE SCROLLABLE ──
        scroll = ctk.CTkScrollableFrame(
            self.zone_principale,
            fg_color=BLANC_CASSE, corner_radius=0)
        scroll.pack(fill="both", expand=True, pady=5)

        # ── Info ──
        info = ctk.CTkFrame(
            scroll, fg_color=BLEU_TRES_PALE, corner_radius=12)
        info.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(
            info,
            text="💡 Le PIN sera demandé à chaque ouverture\n"
                 "🔢 Minimum 4 chiffres  •  Maximum 8 chiffres",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=BLEU_ROYAL,
            justify="center").pack(pady=10)

        # ── Zone principale ──
        if pin_actif:
            self._afficher_zone_pin_actif(scroll)
        else:
            self._afficher_zone_creer_pin(scroll)

    def _afficher_zone_creer_pin(self, parent):
        """Zone pour créer un nouveau PIN"""

        carte = ctk.CTkFrame(
            parent, fg_color=JAUNE_PALE, corner_radius=16)
        carte.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(
            carte,
            text="🔐  CRÉER UN CODE PIN",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=ORANGE_DORE).pack(pady=(15, 8))

        # Frame 2 colonnes
        frame_inputs = ctk.CTkFrame(carte, fg_color="transparent")
        frame_inputs.pack(fill="x", padx=20, pady=5)
        frame_inputs.grid_columnconfigure(0, weight=1)
        frame_inputs.grid_columnconfigure(1, weight=1)

        # PIN
        frame_pin1 = ctk.CTkFrame(frame_inputs, fg_color="transparent")
        frame_pin1.grid(row=0, column=0, padx=5, sticky="ew")

        ctk.CTkLabel(
            frame_pin1,
            text="🔢  Nouveau PIN",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=GRIS_TEXTE).pack(anchor="w")

        self.entry_nouveau_pin = ctk.CTkEntry(
            frame_pin1, height=45,
            fg_color=BLANC, text_color=GRIS_TEXTE,
            placeholder_text="Ex: 1234",
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=10, border_width=2,
            border_color=ORANGE_DORE,
            show="●", justify="center")
        self.entry_nouveau_pin.pack(fill="x", pady=(3, 0))

        # Confirmation
        frame_pin2 = ctk.CTkFrame(frame_inputs, fg_color="transparent")
        frame_pin2.grid(row=0, column=1, padx=5, sticky="ew")

        ctk.CTkLabel(
            frame_pin2,
            text="🔢  Confirmer",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=GRIS_TEXTE).pack(anchor="w")

        self.entry_confirm_pin = ctk.CTkEntry(
            frame_pin2, height=45,
            fg_color=BLANC, text_color=GRIS_TEXTE,
            placeholder_text="Répète",
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=10, border_width=2,
            border_color=ORANGE_DORE,
            show="●", justify="center")
        self.entry_confirm_pin.pack(fill="x", pady=(3, 0))

        # ── Clavier virtuel ──
        ctk.CTkLabel(
            carte,
            text="⌨️  Clavier virtuel (cible : Nouveau PIN)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=GRIS_TEXTE).pack(pady=(15, 5))

        self._creer_clavier_pin(carte)

        # Bouton ACTIVER (BIEN VISIBLE)
        ctk.CTkButton(
            carte,
            text="✅  ACTIVER LE PIN",
            command=self._creer_pin,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, corner_radius=14,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=55, border_width=3,
            border_color=VERT_CORRECTION).pack(
            fill="x", padx=20, pady=(15, 20))

    def _afficher_zone_pin_actif(self, parent):
        """Zone quand le PIN est déjà actif"""

        # ── CHANGER PIN ──
        carte_changer = ctk.CTkFrame(
            parent, fg_color=JAUNE_PALE, corner_radius=16)
        carte_changer.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(
            carte_changer,
            text="🔄  CHANGER LE PIN",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ORANGE_DORE).pack(pady=(12, 8))

        # 3 inputs en grille
        frame_inputs = ctk.CTkFrame(carte_changer, fg_color="transparent")
        frame_inputs.pack(fill="x", padx=15, pady=5)
        frame_inputs.grid_columnconfigure(0, weight=1)
        frame_inputs.grid_columnconfigure(1, weight=1)
        frame_inputs.grid_columnconfigure(2, weight=1)

        # PIN actuel
        f1 = ctk.CTkFrame(frame_inputs, fg_color="transparent")
        f1.grid(row=0, column=0, padx=3, sticky="ew")
        ctk.CTkLabel(f1, text="PIN actuel",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=GRIS_TEXTE).pack(anchor="w")
        self.entry_pin_actuel = ctk.CTkEntry(
            f1, height=42, fg_color=BLANC,
            text_color=GRIS_TEXTE, placeholder_text="Actuel",
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10, border_width=2,
            border_color=ORANGE_DORE,
            show="●", justify="center")
        self.entry_pin_actuel.pack(fill="x", pady=(3, 0))

        # Nouveau
        f2 = ctk.CTkFrame(frame_inputs, fg_color="transparent")
        f2.grid(row=0, column=1, padx=3, sticky="ew")
        ctk.CTkLabel(f2, text="Nouveau PIN",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=GRIS_TEXTE).pack(anchor="w")
        self.entry_nouveau_pin = ctk.CTkEntry(
            f2, height=42, fg_color=BLANC,
            text_color=GRIS_TEXTE, placeholder_text="Nouveau",
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10, border_width=2,
            border_color=VERT_EMERAUDE,
            show="●", justify="center")
        self.entry_nouveau_pin.pack(fill="x", pady=(3, 0))

        # Confirmer
        f3 = ctk.CTkFrame(frame_inputs, fg_color="transparent")
        f3.grid(row=0, column=2, padx=3, sticky="ew")
        ctk.CTkLabel(f3, text="Confirmer",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=GRIS_TEXTE).pack(anchor="w")
        self.entry_confirm_pin = ctk.CTkEntry(
            f3, height=42, fg_color=BLANC,
            text_color=GRIS_TEXTE, placeholder_text="Confirmer",
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10, border_width=2,
            border_color=VERT_EMERAUDE,
            show="●", justify="center")
        self.entry_confirm_pin.pack(fill="x", pady=(3, 0))

        # Clavier
        ctk.CTkLabel(
            carte_changer,
            text="⌨️  Clavier (cible : Nouveau PIN)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=GRIS_TEXTE).pack(pady=(12, 5))

        self._creer_clavier_pin(carte_changer)

        ctk.CTkButton(
            carte_changer,
            text="🔄  CHANGER LE PIN",
            command=self._changer_pin,
            fg_color=ORANGE_DORE, hover_color=ORANGE_CLAIR,
            text_color=BLANC, corner_radius=14,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=48).pack(
            fill="x", padx=20, pady=(10, 15))

        # ── DÉSACTIVER PIN ──
        carte_suppr = ctk.CTkFrame(
            parent, fg_color=ROUGE_FOND, corner_radius=16)
        carte_suppr.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(
            carte_suppr,
            text="🗑️  DÉSACTIVER LE PIN",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ROUGE).pack(pady=(12, 3))

        ctk.CTkLabel(
            carte_suppr,
            text="⚠️ Entre ton PIN actuel pour désactiver",
            font=ctk.CTkFont(size=11),
            text_color=GRIS_TEXTE).pack(pady=(0, 8))

        self.entry_pin_suppr = ctk.CTkEntry(
            carte_suppr, height=45,
            fg_color=BLANC, text_color=GRIS_TEXTE,
            placeholder_text="Ton PIN actuel",
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10, border_width=2,
            border_color=ROUGE,
            show="●", justify="center")
        self.entry_pin_suppr.pack(
            fill="x", padx=20, pady=(5, 10))

        ctk.CTkButton(
            carte_suppr,
            text="🗑️  DÉSACTIVER LE PIN",
            command=self._supprimer_pin,
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, corner_radius=14,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45).pack(
            fill="x", padx=20, pady=(5, 15))

    def _creer_clavier_pin(self, parent):
        """Crée un clavier numérique virtuel compact"""
        frame_clavier = ctk.CTkFrame(parent, fg_color="transparent")
        frame_clavier.pack(pady=5)

        touches = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["⌫", "0", "✓"]
        ]

        for ligne in touches:
            frame_ligne = ctk.CTkFrame(
                frame_clavier, fg_color="transparent")
            frame_ligne.pack(pady=2)

            for touche in ligne:
                if touche == "⌫":
                    couleur = ROUGE
                    hover = ROUGE_CLAIR
                elif touche == "✓":
                    couleur = VERT_EMERAUDE
                    hover = VERT_HOVER
                else:
                    couleur = BLEU_ROYAL
                    hover = VIOLET_PREMIUM

                ctk.CTkButton(
                    frame_ligne,
                    text=touche,
                    command=lambda t=touche: self._touche_pin(t),
                    fg_color=couleur, hover_color=hover,
                    text_color=BLANC,
                    font=ctk.CTkFont(size=15, weight="bold"),
                    width=60, height=42,
                    corner_radius=8).pack(side="left", padx=2)

    def _touche_pin(self, touche: str):
        """Gère les touches du clavier virtuel"""
        try:
            entry = self.entry_nouveau_pin
        except AttributeError:
            return

        if touche == "⌫":
            valeur = entry.get()
            entry.delete(0, "end")
            entry.insert(0, valeur[:-1])
        elif touche == "✓":
            if db.pin_existe():
                self._changer_pin()
            else:
                self._creer_pin()
        else:
            valeur = entry.get()
            if len(valeur) < 8:
                entry.insert("end", touche)

    def _creer_pin(self):
        """Crée un nouveau PIN"""
        nouveau = self.entry_nouveau_pin.get().strip()
        confirm = self.entry_confirm_pin.get().strip()

        if not nouveau:
            messagebox.showwarning("⚠️", "Entre un PIN !")
            return

        if len(nouveau) < 4:
            messagebox.showwarning(
                "⚠️", "Le PIN doit avoir au moins 4 chiffres !")
            return

        if not nouveau.isdigit():
            messagebox.showwarning(
                "⚠️", "Le PIN doit contenir uniquement des chiffres !")
            return

        if nouveau != confirm:
            messagebox.showerror(
                "❌", "Les deux PIN ne correspondent pas !")
            return

        if db.set_pin(nouveau):
            notification_succes(self, "PIN activé !", "🔒 App sécurisée !")
            messagebox.showinfo(
                "✅ PIN activé !",
                f"🔒 Ton code PIN est activé !\n\n"
                f"⚠️ Note bien ton PIN : {'●' * len(nouveau)}\n"
                f"📝 ({len(nouveau)} chiffres)\n\n"
                f"Il sera demandé au prochain démarrage.")
            self.afficher_securite()
        else:
            messagebox.showerror("❌ Erreur", "Impossible d'activer le PIN !")

    def _changer_pin(self):
        """Change le PIN existant"""
        actuel = self.entry_pin_actuel.get().strip()
        nouveau = self.entry_nouveau_pin.get().strip()
        confirm = self.entry_confirm_pin.get().strip()

        if not actuel:
            messagebox.showwarning("⚠️", "Entre ton PIN actuel !")
            return

        if not db.verifier_pin(actuel):
            messagebox.showerror("❌", "PIN actuel incorrect !")
            return

        if len(nouveau) < 4:
            messagebox.showwarning(
                "⚠️", "Le nouveau PIN doit avoir au moins 4 chiffres !")
            return

        if not nouveau.isdigit():
            messagebox.showwarning(
                "⚠️", "Le PIN doit contenir uniquement des chiffres !")
            return

        if nouveau != confirm:
            messagebox.showerror(
                "❌", "Les deux nouveaux PIN ne correspondent pas !")
            return

        if db.set_pin(nouveau):
            notification_succes(self, "PIN changé !", "🔒 Nouveau PIN actif !")
            self.afficher_securite()
        else:
            messagebox.showerror("❌ Erreur", "Impossible de changer le PIN !")

    def _supprimer_pin(self):
        """Supprime le PIN"""
        pin = self.entry_pin_suppr.get().strip()

        if not pin:
            messagebox.showwarning("⚠️", "Entre ton PIN actuel !")
            return

        if not db.verifier_pin(pin):
            messagebox.showerror("❌", "PIN incorrect !")
            return

        if messagebox.askyesno(
                "🗑️ Désactiver le PIN ?",
                "⚠️ Tu vas désactiver la protection PIN.\n\n"
                "N'importe qui pourra ouvrir NOKIROVA !\n\n"
                "Tu confirmes ?"):
            if db.supprimer_pin():
                notification_succes(
                    self, "PIN désactivé !", "🔓 Protection retirée")
                self.afficher_securite()
            else:
                messagebox.showerror(
                    "❌ Erreur", "Impossible de désactiver le PIN !")

    # ═══════════════════════════════════════════
    # 🔒 ÉCRAN DE DÉVERROUILLAGE
    # ═══════════════════════════════════════════

    def afficher_ecran_deverrouillage(self):
        """Écran de saisie du PIN au démarrage"""
        self.vider_zone()

        # ── Fond ──
        fond = ctk.CTkFrame(
            self.zone_principale,
            fg_color=VIOLET_PREMIUM, corner_radius=20)
        fond.pack(fill="both", expand=True)

        # ── Logo + titre ──
        if self.logo_accueil:
            ctk.CTkLabel(
                fond, image=self.logo_accueil,
                text="").pack(pady=(30, 5))

        ctk.CTkLabel(
            fond,
            text="🌸 NOKIROVA",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=BLANC).pack()

        ctk.CTkLabel(
            fond,
            text="🔒 Application verrouillée",
            font=ctk.CTkFont(size=14),
            text_color=VIOLET_LAVANDE).pack(pady=(3, 15))

        # ── Carte PIN ──
        carte_pin = ctk.CTkFrame(
            fond, fg_color=BLANC, corner_radius=20)
        carte_pin.pack(padx=80, pady=5)

        ctk.CTkLabel(
            carte_pin,
            text="🔢  Entre ton code PIN",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=VIOLET_PREMIUM).pack(pady=(15, 8))

        self.entry_deverrouillage = ctk.CTkEntry(
            carte_pin, height=50, width=280,
            fg_color=GRIS_PERLE, text_color=GRIS_TEXTE,
            placeholder_text="● ● ● ●",
            font=ctk.CTkFont(size=22, weight="bold"),
            corner_radius=12, border_width=2,
            border_color=VIOLET_PREMIUM,
            show="●", justify="center")
        self.entry_deverrouillage.pack(padx=20, pady=(5, 10))
        self.entry_deverrouillage.bind(
            "<Return>", lambda e: self._valider_deverrouillage())

        # Clavier
        frame_clavier = ctk.CTkFrame(
            carte_pin, fg_color="transparent")
        frame_clavier.pack(padx=20, pady=5)

        touches = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["⌫", "0", "→"]
        ]

        for ligne in touches:
            frame_ligne = ctk.CTkFrame(
                frame_clavier, fg_color="transparent")
            frame_ligne.pack(pady=2)

            for touche in ligne:
                if touche == "⌫":
                    couleur = ROUGE
                    hover = ROUGE_CLAIR
                elif touche == "→":
                    couleur = VERT_EMERAUDE
                    hover = VERT_HOVER
                else:
                    couleur = VIOLET_PREMIUM
                    hover = VIOLET_LAVANDE

                ctk.CTkButton(
                    frame_ligne,
                    text=touche,
                    command=lambda t=touche: self._touche_deverrouillage(t),
                    fg_color=couleur, hover_color=hover,
                    text_color=BLANC,
                    font=ctk.CTkFont(size=15, weight="bold"),
                    width=70, height=45,
                    corner_radius=10).pack(side="left", padx=3)

        self.label_erreur_pin = ctk.CTkLabel(
            carte_pin, text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ROUGE)
        self.label_erreur_pin.pack(pady=(5, 15))

    def _touche_deverrouillage(self, touche: str):
        """Gère les touches du clavier de déverrouillage"""
        if touche == "⌫":
            valeur = self.entry_deverrouillage.get()
            self.entry_deverrouillage.delete(0, "end")
            self.entry_deverrouillage.insert(0, valeur[:-1])
        elif touche == "→":
            self._valider_deverrouillage()
        else:
            valeur = self.entry_deverrouillage.get()
            if len(valeur) < 8:
                self.entry_deverrouillage.insert("end", touche)

    def _valider_deverrouillage(self):
        """Vérifie le PIN et déverrouille"""
        pin = self.entry_deverrouillage.get().strip()

        if not pin:
            self.label_erreur_pin.configure(
                text="⚠️ Entre ton PIN !")
            return

        if db.verifier_pin(pin):
            self.label_erreur_pin.configure(
                text="✅ Correct !", text_color=VERT_EMERAUDE)
            self.after(500, self.afficher_accueil)
        else:
            self.label_erreur_pin.configure(
                text="❌ PIN incorrect ! Réessaie.",
                text_color=ROUGE)
            self.entry_deverrouillage.delete(0, "end")