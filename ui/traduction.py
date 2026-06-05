# ui/traduction.py - Page Traduction NOKIROVA 🌍

import customtkinter as ctk
from tkinter import messagebox
import threading
import database as db
from ia_handler import demander_ia_brut
from ui.base import (
    VERT_EMERAUDE, VERT_HOVER, VERT_CLAIR, VERT_CORRECTION,
    VERT_FOND_CORRECTION,
    BLEU_ROYAL, BLEU_CIEL, BLEU_TRES_PALE,
    JAUNE_SOLEIL, JAUNE_PALE, OR_MODERNE,
    VIOLET_PREMIUM, VIOLET_LAVANDE, VIOLET_PALE,
    ROSE_SAKURA, ROSE_PALE,
    ORANGE_DORE, ORANGE_CLAIR,
    ROUGE,
    BLANC, GRIS_TEXTE, GRIS_DOUX, GRIS_PERLE
)
from notifications import notification_succes, notification_xp


# ═══════════════════════════════════════════
# 🌍 LANGUES DISPONIBLES
# ═══════════════════════════════════════════
LANGUES = {
    "Français": {"code": "FR", "drapeau": "🇫🇷"},
    "Anglais": {"code": "EN", "drapeau": "🇬🇧"},
    "Espagnol": {"code": "ES", "drapeau": "🇪🇸"},
    "Allemand": {"code": "DE", "drapeau": "🇩🇪"},
    "Italien": {"code": "IT", "drapeau": "🇮🇹"},
    "Portugais": {"code": "PT", "drapeau": "🇵🇹"},
    "Arabe": {"code": "AR", "drapeau": "🇸🇦"},
    "Chinois": {"code": "ZH", "drapeau": "🇨🇳"},
    "Japonais": {"code": "JA", "drapeau": "🇯🇵"},
    "Russe": {"code": "RU", "drapeau": "🇷🇺"},
    "Néerlandais": {"code": "NL", "drapeau": "🇳🇱"},
    "Coréen": {"code": "KO", "drapeau": "🇰🇷"},
}

PLACEHOLDER_SOURCE = "✍️ Tape ou colle ton texte ici..."
PLACEHOLDER_CIBLE = "🌍 La traduction apparaîtra ici..."


class TraductionMixin:

    # ═══════════════════════════════════════════
    # 🌍 PAGE TRADUCTION
    # ═══════════════════════════════════════════

    def afficher_traduction(self):
        self.vider_zone()
        self.afficher_titre("Traduction Intelligente", "🌍", VIOLET_PREMIUM)

        # ── SCROLL PRINCIPAL ──
        scroll_main = ctk.CTkScrollableFrame(
            self.zone_principale,
            fg_color="transparent")
        scroll_main.pack(fill="both", expand=True)

        # ── Bandeau info ──
        info = ctk.CTkFrame(
            scroll_main, fg_color=VIOLET_PALE, corner_radius=12)
        info.pack(fill="x", pady=5)
        ctk.CTkLabel(
            info,
            text="🌍 Traduis n'importe quel texte en 12 langues !\n"
                 "💡 L'IA traduit intelligemment, même le vocabulaire technique.",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=VIOLET_PREMIUM,
            justify="center").pack(pady=12)

        # ── Sélecteurs de langues ──
        frame_langues = ctk.CTkFrame(
            scroll_main, fg_color=VIOLET_LAVANDE, corner_radius=14)
        frame_langues.pack(fill="x", pady=10)

        # Langue source
        col_source = ctk.CTkFrame(frame_langues, fg_color="transparent")
        col_source.pack(side="left", padx=15, pady=15, fill="x", expand=True)

        ctk.CTkLabel(
            col_source, text="📥  DE  :",
            text_color=BLANC,
            font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")

        langues_noms = [f"{LANGUES[n]['drapeau']} {n}" for n in LANGUES.keys()]
        self._langue_source = "Français"
        self.menu_langue_source = ctk.CTkOptionMenu(
            col_source, values=langues_noms,
            command=lambda v: self._changer_langue("source", v),
            fg_color=BLANC, text_color=GRIS_TEXTE,
            button_color=VIOLET_PREMIUM,
            button_hover_color=VIOLET_LAVANDE,
            corner_radius=10, height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            dropdown_font=ctk.CTkFont(size=12))
        self.menu_langue_source.set("🇫🇷 Français")
        self.menu_langue_source.pack(fill="x", pady=(5, 0))

        # Bouton inverser
        btn_inverser = ctk.CTkButton(
            frame_langues, text="🔄",
            command=self._inverser_langues,
            fg_color=JAUNE_SOLEIL, hover_color=OR_MODERNE,
            text_color=GRIS_TEXTE,
            font=ctk.CTkFont(size=20, weight="bold"),
            height=42, width=55, corner_radius=12)
        btn_inverser.pack(side="left", padx=5, pady=(30, 15))

        # Langue cible
        col_cible = ctk.CTkFrame(frame_langues, fg_color="transparent")
        col_cible.pack(side="left", padx=15, pady=15, fill="x", expand=True)

        ctk.CTkLabel(
            col_cible, text="📤  VERS  :",
            text_color=BLANC,
            font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")

        self._langue_cible = "Anglais"
        self.menu_langue_cible = ctk.CTkOptionMenu(
            col_cible, values=langues_noms,
            command=lambda v: self._changer_langue("cible", v),
            fg_color=BLANC, text_color=GRIS_TEXTE,
            button_color=VIOLET_PREMIUM,
            button_hover_color=VIOLET_LAVANDE,
            corner_radius=10, height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            dropdown_font=ctk.CTkFont(size=12))
        self.menu_langue_cible.set("🇬🇧 Anglais")
        self.menu_langue_cible.pack(fill="x", pady=(5, 0))

        # ── Boutons d'action en haut ──
        frame_actions = ctk.CTkFrame(scroll_main, fg_color="transparent")
        frame_actions.pack(fill="x", pady=8)

        ctk.CTkButton(
            frame_actions, text="📚  Charger un cours",
            command=self._charger_cours_traduction,
            fg_color=BLEU_ROYAL, hover_color=BLEU_CIEL,
            text_color=BLANC, corner_radius=10, height=38,
            font=ctk.CTkFont(size=12, weight="bold")).pack(
            side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            frame_actions, text="🗑️  Effacer",
            command=self._effacer_traduction,
            fg_color=ROUGE, hover_color=ORANGE_CLAIR,
            text_color=BLANC, corner_radius=10, height=38,
            font=ctk.CTkFont(size=12, weight="bold")).pack(
            side="left", padx=5, expand=True, fill="x")

        # ── Zone TEXTE SOURCE ──
        ctk.CTkLabel(
            scroll_main,
            text="✍️  TEXTE ORIGINAL",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", padx=5, pady=(8, 2))

        cadre_source = ctk.CTkFrame(
            scroll_main, fg_color=BLANC, corner_radius=14,
            border_width=2, border_color=VIOLET_PALE)
        cadre_source.pack(fill="x", pady=3)

        # ⚠️ HAUTEUR FIXE pour la zone source
        self.zone_texte_source = ctk.CTkTextbox(
            cadre_source, fg_color=BLANC, text_color=GRIS_DOUX,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            corner_radius=10, wrap="word", border_width=0,
            height=180)
        self.zone_texte_source.pack(
            fill="x", padx=10, pady=10)

        # Placeholder qui disparaît au clic
        self.zone_texte_source.insert("0.0", PLACEHOLDER_SOURCE)
        self._source_vide = True
        self.zone_texte_source.bind(
            "<FocusIn>", self._effacer_placeholder_source)
        self.zone_texte_source.bind(
            "<Button-1>", self._effacer_placeholder_source)

        # ── Bouton TRADUIRE (gros bouton central) ──
        self.btn_traduire = ctk.CTkButton(
            scroll_main,
            text="✨  TRADUIRE  ✨",
            command=self._lancer_traduction,
            fg_color=VIOLET_PREMIUM, hover_color=VIOLET_LAVANDE,
            text_color=BLANC, corner_radius=14, height=55,
            font=ctk.CTkFont(size=17, weight="bold"))
        self.btn_traduire.pack(fill="x", pady=12)

        # ── Zone TRADUCTION ──
        ctk.CTkLabel(
            scroll_main,
            text="🌍  TRADUCTION",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=VERT_CORRECTION, anchor="w").pack(
            fill="x", padx=5, pady=(8, 2))

        cadre_cible = ctk.CTkFrame(
            scroll_main, fg_color=VERT_FOND_CORRECTION,
            corner_radius=14, border_width=2, border_color=VERT_CLAIR)
        cadre_cible.pack(fill="x", pady=3)

        # ⚠️ HAUTEUR FIXE pour la zone cible
        self.zone_texte_cible = ctk.CTkTextbox(
            cadre_cible, fg_color=VERT_FOND_CORRECTION, text_color=GRIS_DOUX,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            corner_radius=10, wrap="word", border_width=0,
            height=180)
        self.zone_texte_cible.pack(
            fill="x", padx=10, pady=10)
        self.zone_texte_cible.insert("0.0", PLACEHOLDER_CIBLE)

        # ── Boutons résultat ──
        frame_resultat = ctk.CTkFrame(scroll_main, fg_color="transparent")
        frame_resultat.pack(fill="x", pady=10)

        ctk.CTkButton(
            frame_resultat, text="📋  Copier",
            command=self._copier_traduction,
            fg_color=BLEU_CIEL, hover_color=BLEU_ROYAL,
            text_color=BLANC, corner_radius=10, height=42,
            font=ctk.CTkFont(size=13, weight="bold")).pack(
            side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            frame_resultat, text="💾  Sauvegarder dans bibliothèque",
            command=self._sauvegarder_traduction,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, corner_radius=10, height=42,
            font=ctk.CTkFont(size=13, weight="bold")).pack(
            side="left", padx=5, expand=True, fill="x")

        # Espace en bas pour le scroll
        ctk.CTkLabel(scroll_main, text="", height=20).pack()

    # ═══════════════════════════════════════════
    # 🔧 MÉTHODES INTERNES
    # ═══════════════════════════════════════════

    def _effacer_placeholder_source(self, event=None):
        """Efface le placeholder au premier clic"""
        if self._source_vide:
            self.zone_texte_source.delete("0.0", "end")
            self.zone_texte_source.configure(text_color=GRIS_TEXTE)
            self._source_vide = False

    def _changer_langue(self, type_lang, valeur):
        """Extrait le nom de la langue depuis '🇫🇷 Français'"""
        nom = valeur.split(" ", 1)[1] if " " in valeur else valeur
        if type_lang == "source":
            self._langue_source = nom
        else:
            self._langue_cible = nom

    def _inverser_langues(self):
        """Inverse les langues source ↔ cible"""
        source = self._langue_source
        cible = self._langue_cible
        self._langue_source = cible
        self._langue_cible = source
        self.menu_langue_source.set(
            f"{LANGUES[cible]['drapeau']} {cible}")
        self.menu_langue_cible.set(
            f"{LANGUES[source]['drapeau']} {source}")

    def _effacer_traduction(self):
        """Vide les 2 zones de texte"""
        self.zone_texte_source.delete("0.0", "end")
        self.zone_texte_source.insert("0.0", PLACEHOLDER_SOURCE)
        self.zone_texte_source.configure(text_color=GRIS_DOUX)
        self._source_vide = True
        self.zone_texte_cible.delete("0.0", "end")
        self.zone_texte_cible.insert("0.0", PLACEHOLDER_CIBLE)
        self.zone_texte_cible.configure(text_color=GRIS_DOUX)

    def _charger_cours_traduction(self):
        """Charge un cours depuis la bibliothèque dans la zone source"""
        cours_list = db.lister_cours()
        if not cours_list:
            messagebox.showinfo(
                "📭", "Aucun cours dans la bibliothèque !\n"
                      "💡 Importe un cours d'abord.")
            return

        # Mini fenêtre de sélection
        popup = ctk.CTkToplevel(self)
        popup.title("📚 Choisir un cours")
        popup.geometry("500x400")
        popup.configure(fg_color=BLANC)

        ctk.CTkLabel(
            popup, text="📚  Choisis un cours à traduire",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=VIOLET_PREMIUM).pack(pady=15)

        scroll = ctk.CTkScrollableFrame(
            popup, fg_color=GRIS_PERLE, corner_radius=10)
        scroll.pack(fill="both", expand=True, padx=15, pady=10)

        for cours in cours_list:
            id_cours, nom, matiere, date_import = cours
            ctk.CTkButton(
                scroll,
                text=f"📄  {nom[:40]}\n🎯 {matiere}",
                command=lambda i=id_cours, n=nom: (
                    self._injecter_cours_source(i, n), popup.destroy()),
                fg_color=BLEU_TRES_PALE, hover_color=BLEU_CIEL,
                text_color=GRIS_TEXTE, corner_radius=10,
                height=55, anchor="w",
                font=ctk.CTkFont(size=12, weight="bold")).pack(
                fill="x", padx=5, pady=4)

    def _injecter_cours_source(self, id_cours, nom):
        """Injecte le contenu du cours dans la zone source"""
        info = db.info_cours(id_cours)
        if info:
            self.zone_texte_source.delete("0.0", "end")
            self.zone_texte_source.insert("0.0", info["contenu"])
            self.zone_texte_source.configure(text_color=GRIS_TEXTE)
            self._source_vide = False
            self._cours_traduit_id = id_cours
            self._cours_traduit_nom = nom
            self._cours_traduit_matiere = info["matiere"]
            notification_succes(self, "Cours chargé !", f"📚 {nom[:30]}")

    def _lancer_traduction(self):
        """Lance la traduction via l'IA"""
        # Vérifier si encore le placeholder
        if self._source_vide:
            messagebox.showwarning(
                "⚠️", "Tape un texte à traduire !\n"
                      "💡 Clique d'abord dans la zone de texte.")
            return

        texte = self.zone_texte_source.get("0.0", "end").strip()
        if not texte or len(texte) < 1:
            messagebox.showwarning(
                "⚠️", "La zone de texte est vide !")
            return

        if self._langue_source == self._langue_cible:
            messagebox.showwarning(
                "⚠️", "Les 2 langues sont identiques !\n"
                      "Choisis une autre langue cible.")
            return

        # Désactiver le bouton + message attente
        self.btn_traduire.configure(
            text="⏳  Traduction en cours...", state="disabled")
        self.zone_texte_cible.delete("0.0", "end")
        self.zone_texte_cible.configure(text_color=GRIS_TEXTE)
        self.zone_texte_cible.insert(
            "0.0", "⏳  L'IA traduit ton texte...\n\n"
                   "💡 Patience, ça peut prendre quelques secondes...")

        # Lancer dans un thread
        threading.Thread(
            target=self._traduire_thread,
            args=(texte,), daemon=True).start()

    def _traduire_thread(self, texte):
        """Thread de traduction"""
        try:
            prompt = f"""Tu es un traducteur professionnel expert.

MISSION : Traduis le texte suivant du {self._langue_source} vers le {self._langue_cible}.

RÈGLES STRICTES :
- Traduis FIDÈLEMENT le sens
- Garde le ton et le style original
- Respecte le vocabulaire technique (économie, sciences, etc.)
- Conserve la mise en forme (paragraphes, listes, titres)
- N'ajoute AUCUN commentaire, AUCUNE explication
- Réponds UNIQUEMENT avec la traduction

TEXTE À TRADUIRE :
{texte}

TRADUCTION EN {self._langue_cible.upper()} :"""

            traduction = demander_ia_brut(prompt, temperature=0.3)

            # Nettoyer la traduction
            traduction = traduction.strip()
            if traduction.startswith("```"):
                traduction = traduction.split("```")[1]
                if traduction.startswith(self._langue_cible.lower()):
                    traduction = traduction.split("\n", 1)[1]
            traduction = traduction.strip("`").strip()

            # Mettre à jour UI dans le thread principal
            self.after(0, lambda: self._afficher_traduction(traduction))

        except Exception as e:
            erreur = f"❌ Erreur de traduction : {str(e)}"
            self.after(0, lambda: self._afficher_traduction(erreur))

    def _afficher_traduction(self, traduction):
        """Affiche la traduction et réactive le bouton"""
        self.zone_texte_cible.delete("0.0", "end")
        self.zone_texte_cible.configure(text_color=GRIS_TEXTE)
        self.zone_texte_cible.insert("0.0", traduction)
        self.btn_traduire.configure(
            text="✨  TRADUIRE  ✨", state="normal")

        if "❌" not in traduction[:5]:
            self._recompenser(10, "Traduction réussie ! 🌍")
            notification_succes(
                self, "Traduction terminée !",
                f"🌍 {self._langue_source} → {self._langue_cible}")

    def _copier_traduction(self):
        """Copie la traduction dans le presse-papiers"""
        traduction = self.zone_texte_cible.get("0.0", "end").strip()
        if (not traduction or "apparaîtra ici" in traduction
                or "⏳" in traduction):
            messagebox.showwarning("⚠️", "Aucune traduction à copier !")
            return
        self.clipboard_clear()
        self.clipboard_append(traduction)
        self.update()
        notification_succes(
            self, "Copié !", "📋 Traduction dans le presse-papiers")

    def _sauvegarder_traduction(self):
        """Sauvegarde la traduction comme nouveau cours"""
        traduction = self.zone_texte_cible.get("0.0", "end").strip()
        if (not traduction or "apparaîtra ici" in traduction
                or "⏳" in traduction):
            messagebox.showwarning(
                "⚠️", "Aucune traduction à sauvegarder !")
            return

        # Récupérer infos du cours original (si chargé)
        nom_base = getattr(self, '_cours_traduit_nom', None)
        matiere = getattr(self, '_cours_traduit_matiere', None)

        code_langue = LANGUES[self._langue_cible]["code"]

        if nom_base:
            # Cours chargé depuis bibliothèque
            nom_final = f"{nom_base} [{code_langue}]"
        else:
            # Texte libre → nom générique
            from datetime import datetime
            date_simple = datetime.now().strftime('%d-%m %Hh%M')
            nom_final = f"Traduction_{code_langue}_{date_simple}"
            matiere = "🌍 Traduction"

        # Ajouter à la bibliothèque
        try:
            db.sauvegarder_cours(
                nom_final, traduction, matiere or "🌍 Traduction")
            notification_succes(
                self, "Sauvegardé !",
                f"📚 {nom_final[:30]}")
            messagebox.showinfo(
                "✅ Sauvegardé",
                f"📚 Traduction ajoutée à ta bibliothèque !\n\n"
                f"📄 Nom : {nom_final}\n"
                f"🎯 Matière : {matiere}")
            self._recompenser(5, "Cours sauvegardé ! 💾")
        except Exception as e:
            messagebox.showerror(
                "❌ Erreur",
                f"Impossible de sauvegarder :\n{str(e)}")