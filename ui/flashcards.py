# ui/flashcards.py - Flashcards NOKIROVA 🌸

import customtkinter as ctk
from tkinter import messagebox, simpledialog
import threading
import re
import database as db
from ui.base import (VERT_EMERAUDE, VERT_HOVER, VERT_CLAIR, VERT_CORRECTION,
                     VERT_FOND_CORRECTION,
                     BLEU_ROYAL, BLEU_CIEL, BLEU_TRES_PALE, BLEU_PALE,
                     VIOLET_PREMIUM, VIOLET_LAVANDE,
                     ORANGE_DORE, ORANGE_CLAIR, ORANGE_PALE,
                     ROUGE, ROUGE_CLAIR,
                     BLANC, GRIS_TEXTE, GRIS_DOUX, GRIS_PERLE)
from notifications import notification_succes


class FlashcardsMixin:

    # ═══════════════════════════════════════════
    # 🃏 FLASHCARDS
    # ═══════════════════════════════════════════

    def afficher_flashcards(self):
        self.vider_zone()
        self.afficher_titre("Flashcards", "🃏", BLEU_ROYAL)

        nb_cards = db.compter_flashcards()
        decks = db.lister_decks()

        # ── Stats ──
        carte_stats = ctk.CTkFrame(
            self.zone_principale,
            fg_color=BLEU_TRES_PALE, corner_radius=15, height=70)
        carte_stats.pack(fill="x", pady=(0, 10))
        carte_stats.pack_propagate(False)
        ctk.CTkLabel(
            carte_stats,
            text=f"🃏 {nb_cards} carte(s)  •  📦 {len(decks)} deck(s)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=BLEU_ROYAL).pack(pady=22)

        # ── Actions ──
        frame_actions = ctk.CTkFrame(
            self.zone_principale,
            fg_color=BLEU_PALE, corner_radius=12)
        frame_actions.pack(fill="x", pady=5)

        ctk.CTkButton(
            frame_actions, text="🤖  Générer avec l'IA",
            command=self._generer_flashcards_ia,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, corner_radius=10, height=36,
            font=ctk.CTkFont(size=13, weight="bold")).pack(
            side="left", padx=15, pady=12, expand=True, fill="x")

        ctk.CTkButton(
            frame_actions, text="✏️  Créer manuellement",
            command=self._creer_flashcard_manuelle,
            fg_color=VIOLET_PREMIUM, hover_color=VIOLET_LAVANDE,
            text_color=BLANC, corner_radius=10, height=36,
            font=ctk.CTkFont(size=13, weight="bold")).pack(
            side="left", padx=5, pady=12, expand=True, fill="x")

        ctk.CTkButton(
            frame_actions, text="🔁  Réviser les ratées",
            command=self._reviser_ratees,
            fg_color=ORANGE_DORE, hover_color=ORANGE_CLAIR,
            text_color=BLANC, corner_radius=10, height=36,
            font=ctk.CTkFont(size=13, weight="bold")).pack(
            side="left", padx=5, pady=12, expand=True, fill="x")

        ctk.CTkButton(
            frame_actions, text="▶️  Réviser tout",
            command=self._reviser_tout,
            fg_color=BLEU_ROYAL, hover_color=BLEU_CIEL,
            text_color=BLANC, corner_radius=10, height=36,
            font=ctk.CTkFont(size=13, weight="bold")).pack(
            side="left", padx=5, pady=12, expand=True, fill="x")

        ctk.CTkButton(
            frame_actions, text="🗑️  Tout supprimer",
            command=self._supprimer_tout_flashcards,
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, corner_radius=10, height=36,
            font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="right", padx=15, pady=12)

        # ── Decks ──
        if decks:
            ctk.CTkLabel(
                self.zone_principale, text="📦  MES DECKS :",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=BLEU_ROYAL).pack(anchor="w", pady=(10, 5))

            self.frame_decks = ctk.CTkScrollableFrame(
                self.zone_principale, fg_color=BLANC,
                corner_radius=15, border_width=2,
                border_color=BLEU_CIEL, height=280)
            self.frame_decks.pack(fill="both", expand=True, pady=5)

            for deck in decks:
                self._creer_carte_deck(*deck)
        else:
            zone_vide = ctk.CTkFrame(
                self.zone_principale,
                fg_color=BLEU_TRES_PALE, corner_radius=15)
            zone_vide.pack(fill="both", expand=True, pady=10)
            ctk.CTkLabel(
                zone_vide,
                text="🃏  Aucune flashcard pour le moment !\n\n"
                     "🤖 Clique sur 'Générer avec l'IA' pour créer\n"
                     "    des flashcards depuis ton cours\n\n"
                     "✏️  Ou crée-les manuellement",
                font=ctk.CTkFont(size=14),
                text_color=BLEU_ROYAL, justify="center").pack(pady=50)

    def _creer_carte_deck(self, nom_deck, matiere, nb_cards,
                          total_reussis, total_vus):
        taux = int((total_reussis / total_vus) * 100) if (
                total_vus and total_vus > 0) else 0

        if taux >= 80:
            couleur_taux, emoji_taux = VERT_EMERAUDE, "🏆"
        elif taux >= 50:
            couleur_taux, emoji_taux = ORANGE_DORE, "💪"
        else:
            couleur_taux = ROUGE if total_vus > 0 else GRIS_DOUX
            emoji_taux = "📚" if total_vus > 0 else "🆕"

        carte = ctk.CTkFrame(
            self.frame_decks, fg_color=BLEU_TRES_PALE,
            corner_radius=14, border_width=2, border_color=BLEU_CIEL)
        carte.pack(fill="x", padx=10, pady=6)

        ligne1 = ctk.CTkFrame(carte, fg_color="transparent")
        ligne1.pack(fill="x", padx=15, pady=(12, 3))
        ctk.CTkLabel(ligne1, text=f"📦  {nom_deck}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=BLEU_ROYAL).pack(side="left")
        ctk.CTkLabel(ligne1,
                     text=f"{emoji_taux} {taux}% réussite",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=couleur_taux).pack(side="right")

        ligne2 = ctk.CTkFrame(carte, fg_color="transparent")
        ligne2.pack(fill="x", padx=15, pady=(0, 5))
        ctk.CTkLabel(ligne2, text=f"🎯 {matiere}",
                     font=ctk.CTkFont(size=11),
                     text_color=VIOLET_PREMIUM).pack(side="left")
        ctk.CTkLabel(ligne2,
                     text=f"🃏 {nb_cards} carte(s)  •  "
                          f"👁️ {total_vus or 0} vues",
                     font=ctk.CTkFont(size=11),
                     text_color=GRIS_DOUX).pack(side="right")

        if total_vus and total_vus > 0:
            progress = ctk.CTkProgressBar(
                carte, progress_color=couleur_taux,
                fg_color=BLANC, height=8, corner_radius=4)
            progress.set(taux / 100)
            progress.pack(fill="x", padx=15, pady=5)

        ligne3 = ctk.CTkFrame(carte, fg_color="transparent")
        ligne3.pack(fill="x", padx=15, pady=(5, 12))

        ctk.CTkButton(ligne3, text="▶️  Réviser",
                      command=lambda d=nom_deck: self._lancer_revision(d),
                      fg_color=BLEU_ROYAL, hover_color=BLEU_CIEL,
                      text_color=BLANC, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="left", padx=2, expand=True, fill="x")

        ctk.CTkButton(ligne3, text="👁️  Voir les cartes",
                      command=lambda d=nom_deck: self._voir_cartes_deck(d),
                      fg_color=VIOLET_PREMIUM, hover_color=VIOLET_LAVANDE,
                      text_color=BLANC, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="left", padx=2, expand=True, fill="x")

        ctk.CTkButton(ligne3, text="🗑️  Supprimer",
                      command=lambda d=nom_deck: self._supprimer_deck(d),
                      fg_color=ROUGE, hover_color=ROUGE_CLAIR,
                      text_color=BLANC, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="left", padx=2, expand=True, fill="x")

    def _generer_flashcards_ia(self):
        if not self.cours_actuel:
            messagebox.showwarning(
                "⚠️",
                "Importe d'abord un cours !\n\n"
                "Va dans 📥 Importer ou 📚 Bibliothèque")
            return

        nom_deck = simpledialog.askstring(
            "📦 Nom du deck",
            f"Donne un nom à ce deck de flashcards :\n\n"
            f"📚 Cours : {self.nom_cours[:30]}",
            initialvalue=f"Deck - {self.nom_cours[:20]}",
            parent=self)

        if not nom_deck or not nom_deck.strip():
            return
        nom_deck = nom_deck.strip()

        nb_str = simpledialog.askstring(
            "🃏 Nombre de flashcards",
            "Combien de flashcards générer ?\n\n(entre 5 et 20)",
            initialvalue="10", parent=self)

        try:
            nb = max(5, min(20, int(nb_str or "10")))
        except Exception:
            nb = 10

        self.vider_zone()
        self.afficher_titre("Génération en cours...", "🤖", VERT_EMERAUDE)

        carte_load = ctk.CTkFrame(
            self.zone_principale,
            fg_color=VERT_FOND_CORRECTION, corner_radius=15)
        carte_load.pack(fill="x", pady=20)

        self.label_generation = ctk.CTkLabel(
            carte_load,
            text=f"⏳ NOKIROVA génère {nb} flashcards...\n\n"
                 f"🧠 Analyse du cours en cours...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=VERT_CORRECTION)
        self.label_generation.pack(pady=30)
        self.update()

        def tache():
            try:
                from ia_handler import demander_ia_brut
                prompt = f"""Tu es NOKIROVA. Génère exactement {nb} flashcards pédagogiques depuis ce cours.

FORMAT OBLIGATOIRE (respecte exactement) :

CARTE 1
RECTO: [concept, terme ou question courte]
VERSO: [définition ou réponse complète]
---
CARTE 2
RECTO: [concept, terme ou question courte]
VERSO: [définition ou réponse complète]
---

Génère {nb} cartes. Sois précis et pédagogique. Réponds en français.

COURS :
{self.cours_actuel[:4000]}

FLASHCARDS :"""

                resultat = demander_ia_brut(prompt, rapide=False)
                cards = self._parser_flashcards(resultat)

                if not cards:
                    self.after(0, lambda: messagebox.showerror(
                        "❌ Erreur",
                        "Impossible de générer les flashcards.\n"
                        "Réessaie ou vérifie ton cours."))
                    self.after(0, self.afficher_flashcards)
                    return

                matiere = self.matiere_detectee or "Général"
                nb_cree = db.creer_flashcards_bulk(cards, matiere, nom_deck)
                self.after(0, lambda: self._fin_generation_flashcards(
                    nb_cree, nom_deck))

            except Exception as e:
                self.after(0, lambda: messagebox.showerror(
                    "❌ Erreur", f"Erreur : {e}"))
                self.after(0, self.afficher_flashcards)

        threading.Thread(target=tache, daemon=True).start()

    def _parser_flashcards(self, texte: str) -> list:
        cards = []
        blocs = re.split(r'---+', texte)
        for bloc in blocs:
            bloc = bloc.strip()
            if not bloc:
                continue
            recto_match = re.search(
                r'RECTO\s*:\s*(.+?)(?=VERSO|$)',
                bloc, re.DOTALL | re.IGNORECASE)
            verso_match = re.search(
                r'VERSO\s*:\s*(.+?)$',
                bloc, re.DOTALL | re.IGNORECASE)
            if recto_match and verso_match:
                recto = re.sub(r'\s+', ' ', recto_match.group(1)).strip()
                verso = re.sub(r'\s+', ' ', verso_match.group(1)).strip()
                recto = re.sub(
                    r'^CARTE\s*\d+\s*', '', recto,
                    flags=re.IGNORECASE).strip()
                if recto and verso and len(recto) > 3 and len(verso) > 3:
                    cards.append({
                        "recto": recto[:300],
                        "verso": verso[:500]})
        print(f"🃏 Flashcards parsées : {len(cards)}")
        return cards

    def _fin_generation_flashcards(self, nb_cree: int, nom_deck: str):
        notification_succes(self, f"{nb_cree} flashcards créées !", f"📦 {nom_deck}")
        self._recompenser(nb_cree * 2, f"{nb_cree} flashcards générées !")
        self.afficher_flashcards()

    def _creer_flashcard_manuelle(self):
        self.vider_zone()
        self.afficher_titre("Créer une flashcard", "✏️", VIOLET_PREMIUM)

        ctk.CTkLabel(self.zone_principale,
                     text="📦  Nom du deck :",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=GRIS_TEXTE).pack(anchor="w", pady=(5, 3))

        self.entry_deck_nom = ctk.CTkEntry(
            self.zone_principale, height=40,
            fg_color=BLANC, text_color=GRIS_TEXTE,
            placeholder_text="Ex: Économie Chapitre 3",
            font=ctk.CTkFont(size=13), corner_radius=12,
            border_width=2, border_color=VIOLET_LAVANDE)
        self.entry_deck_nom.pack(fill="x", pady=(0, 10))
        self.entry_deck_nom.insert(
            0, f"Deck - {self.nom_cours[:20]}"
            if self.cours_actuel else "Mon Deck")

        frame_2col = ctk.CTkFrame(self.zone_principale, fg_color="transparent")
        frame_2col.pack(fill="both", expand=True, pady=5)
        frame_2col.grid_columnconfigure(0, weight=1)
        frame_2col.grid_columnconfigure(1, weight=1)

        # Recto
        frame_recto = ctk.CTkFrame(
            frame_2col, fg_color=BLEU_TRES_PALE,
            corner_radius=15, border_width=2, border_color=BLEU_ROYAL)
        frame_recto.grid(row=0, column=0, padx=(0, 8), pady=5, sticky="nsew")

        ctk.CTkLabel(frame_recto,
                     text="🔵  RECTO (Question / Concept)",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=BLEU_ROYAL).pack(pady=(15, 5))

        self.zone_recto = ctk.CTkTextbox(
            frame_recto, fg_color=BLANC, text_color=GRIS_TEXTE,
            font=ctk.CTkFont(size=14), corner_radius=10,
            border_width=0, wrap="word", height=200)
        self.zone_recto.pack(
            fill="both", expand=True, padx=10, pady=(0, 15))

        # Verso
        frame_verso = ctk.CTkFrame(
            frame_2col, fg_color=VERT_FOND_CORRECTION,
            corner_radius=15, border_width=2, border_color=VERT_EMERAUDE)
        frame_verso.grid(row=0, column=1, padx=(8, 0), pady=5, sticky="nsew")

        ctk.CTkLabel(frame_verso,
                     text="🟢  VERSO (Réponse / Définition)",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=VERT_CORRECTION).pack(pady=(15, 5))

        self.zone_verso = ctk.CTkTextbox(
            frame_verso, fg_color=BLANC, text_color=GRIS_TEXTE,
            font=ctk.CTkFont(size=14), corner_radius=10,
            border_width=0, wrap="word", height=200)
        self.zone_verso.pack(
            fill="both", expand=True, padx=10, pady=(0, 15))

        # Boutons
        frame_btns = ctk.CTkFrame(self.zone_principale, fg_color="transparent")
        frame_btns.pack(fill="x", pady=10)

        ctk.CTkButton(frame_btns, text="❌  Annuler",
                      command=self.afficher_flashcards,
                      fg_color=GRIS_DOUX, hover_color=ROUGE_CLAIR,
                      text_color=BLANC, corner_radius=14,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      height=48).pack(
            side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(frame_btns, text="💾  Sauvegarder la carte",
                      command=self._sauvegarder_flashcard_manuelle,
                      fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
                      text_color=BLANC, corner_radius=14,
                      font=ctk.CTkFont(size=15, weight="bold"),
                      height=48).pack(
            side="left", padx=5, expand=True, fill="x")

    def _sauvegarder_flashcard_manuelle(self):
        recto = self.zone_recto.get("0.0", "end").strip()
        verso = self.zone_verso.get("0.0", "end").strip()
        nom_deck = self.entry_deck_nom.get().strip() or "Mon Deck"

        if not recto:
            messagebox.showwarning("⚠️", "Remplis le RECTO !")
            return
        if not verso:
            messagebox.showwarning("⚠️", "Remplis le VERSO !")
            return

        db.creer_flashcard(recto, verso,
                           self.matiere_detectee or "Général", nom_deck)
        notification_succes(self, "Carte créée !", "🃏 Flashcard ajoutée !")
        self._recompenser(2, "Flashcard créée !")
        self.afficher_flashcards()

    def _lancer_revision(self, nom_deck: str = None):
        cards = (db.lister_flashcards(nom_deck=nom_deck)
                 if nom_deck else db.lister_flashcards())

        if not cards:
            messagebox.showwarning("⚠️", "Aucune flashcard dans ce deck !")
            return

        import random
        cards_list = list(cards)
        random.shuffle(cards_list)

        self._cards_session = cards_list
        self._card_index = 0
        self._session_reussis = 0
        self._session_rates = 0
        self._verso_visible = False
        self._nom_deck_session = nom_deck or "Toutes les cartes"
        self._afficher_carte_revision()

    def _reviser_tout(self):
        self._lancer_revision(None)

    def _reviser_ratees(self):
        cards = db.get_flashcards_a_revoir()
        cards_ratees = [c for c in cards if c[7] > 0]
        if not cards_ratees:
            cards_ratees = [c for c in cards if c[5] == 0]

        if not cards_ratees:
            messagebox.showinfo(
                "✅ Parfait !",
                "Tu n'as aucune carte ratée !\n\n🏆 Tu maîtrises tout !")
            return

        self._cards_session = cards_ratees
        self._card_index = 0
        self._session_reussis = 0
        self._session_rates = 0
        self._verso_visible = False
        self._nom_deck_session = "Cartes à revoir"
        self._afficher_carte_revision()

    def _afficher_carte_revision(self):
        self.vider_zone()

        total = len(self._cards_session)
        actuel = self._card_index + 1
        card = self._cards_session[self._card_index]
        id_c, recto, verso, matiere, nom_deck, nb_vus, nb_reussis, nb_rates, date_c = card

        # ── Titre ──
        carte_titre = ctk.CTkFrame(
            self.zone_principale,
            fg_color=BLEU_ROYAL, corner_radius=18, height=80)
        carte_titre.pack(fill="x", pady=(0, 10))
        carte_titre.pack_propagate(False)

        ctk.CTkLabel(
            carte_titre,
            text=f"🃏  {self._nom_deck_session}  •  "
                 f"Carte {actuel}/{total}  •  "
                 f"✅{self._session_reussis} ❌{self._session_rates}",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=BLANC).pack(pady=25)

        # ── Progress ──
        progress = ctk.CTkProgressBar(
            self.zone_principale,
            progress_color=VERT_EMERAUDE,
            fg_color=GRIS_PERLE, height=10, corner_radius=5)
        progress.set(actuel / total)
        progress.pack(fill="x", padx=5, pady=5)

        # ── Recto ──
        carte_recto = ctk.CTkFrame(
            self.zone_principale, fg_color=BLEU_TRES_PALE,
            corner_radius=20, border_width=3, border_color=BLEU_ROYAL)
        carte_recto.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(carte_recto, text="🔵  QUESTION",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=BLEU_ROYAL).pack(pady=(18, 5))

        ctk.CTkLabel(carte_recto, text=recto,
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=GRIS_TEXTE,
                     wraplength=850, justify="center").pack(
            padx=30, pady=(0, 20))

        if nb_vus > 0:
            taux_c = int((nb_reussis / nb_vus) * 100)
            ctk.CTkLabel(
                carte_recto,
                text=f"📊 Cette carte : {nb_reussis}/{nb_vus} "
                     f"réussites ({taux_c}%)",
                font=ctk.CTkFont(size=11),
                text_color=GRIS_DOUX).pack(pady=(0, 12))

        # ── Verso ──
        self.frame_verso_zone = ctk.CTkFrame(
            self.zone_principale, fg_color="transparent")
        self.frame_verso_zone.pack(fill="both", expand=True, pady=5)

        if not self._verso_visible:
            ctk.CTkButton(
                self.frame_verso_zone,
                text="👁️  RÉVÉLER LA RÉPONSE",
                command=self._revealer_verso,
                fg_color=VIOLET_PREMIUM, hover_color=VIOLET_LAVANDE,
                text_color=BLANC, corner_radius=16,
                font=ctk.CTkFont(size=18, weight="bold"),
                height=70, border_width=3,
                border_color=VIOLET_LAVANDE).pack(
                fill="x", padx=20, pady=30)

            ctk.CTkLabel(
                self.frame_verso_zone,
                text="💡 Essaie de te souvenir de la réponse avant de révéler !",
                font=ctk.CTkFont(size=12, slant="italic"),
                text_color=GRIS_DOUX).pack(pady=5)
        else:
            carte_verso = ctk.CTkFrame(
                self.frame_verso_zone, fg_color=VERT_FOND_CORRECTION,
                corner_radius=20, border_width=3, border_color=VERT_EMERAUDE)
            carte_verso.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(carte_verso, text="🟢  RÉPONSE",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=VERT_CORRECTION).pack(pady=(18, 5))

            ctk.CTkLabel(carte_verso, text=verso,
                         font=ctk.CTkFont(size=16),
                         text_color=GRIS_TEXTE,
                         wraplength=850, justify="center").pack(
                padx=30, pady=(0, 20))

            frame_rep = ctk.CTkFrame(
                self.frame_verso_zone, fg_color="transparent")
            frame_rep.pack(fill="x", pady=15, padx=5)

            ctk.CTkButton(
                frame_rep, text="❌  Je ne savais pas",
                command=lambda: self._repondre_flashcard(id_c, False),
                fg_color=ROUGE, hover_color=ROUGE_CLAIR,
                text_color=BLANC, corner_radius=14,
                font=ctk.CTkFont(size=16, weight="bold"),
                height=60, border_width=2,
                border_color=ROUGE_CLAIR).pack(
                side="left", padx=5, expand=True, fill="x")

            ctk.CTkButton(
                frame_rep, text="✅  Je savais !",
                command=lambda: self._repondre_flashcard(id_c, True),
                fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
                text_color=BLANC, corner_radius=14,
                font=ctk.CTkFont(size=16, weight="bold"),
                height=60, border_width=2,
                border_color=VERT_CORRECTION).pack(
                side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            self.zone_principale, text="⏹️  Arrêter la session",
            command=self.afficher_flashcards,
            fg_color=GRIS_DOUX, hover_color=GRIS_TEXTE,
            text_color=BLANC, corner_radius=10, height=35,
            font=ctk.CTkFont(size=12)).pack(pady=8, fill="x")

    def _revealer_verso(self):
        self._verso_visible = True
        self._afficher_carte_revision()

    def _repondre_flashcard(self, id_card: int, reussi: bool):
        db.maj_flashcard_stats(id_card, reussi)
        if reussi:
            self._session_reussis += 1
        else:
            self._session_rates += 1

        self._verso_visible = False
        self._card_index += 1

        if self._card_index >= len(self._cards_session):
            self._afficher_bilan_flashcards()
        else:
            self._afficher_carte_revision()

    def _afficher_bilan_flashcards(self):
        self.vider_zone()

        total = len(self._cards_session)
        score = self._session_reussis
        pourcentage = (score / total) * 100 if total else 0

        if pourcentage >= 80:
            emoji_t, titre_t, couleur_t = "🏆", "EXCELLENT !", VERT_EMERAUDE
        elif pourcentage >= 60:
            emoji_t, titre_t, couleur_t = "🎯", "BIEN JOUÉ !", BLEU_ROYAL
        elif pourcentage >= 40:
            emoji_t, titre_t, couleur_t = "💪", "CONTINUE !", ORANGE_DORE
        else:
            emoji_t, titre_t, couleur_t = "📚", "RÉVISE ENCORE !", ROUGE

        self.afficher_titre(titre_t, emoji_t, couleur_t)

        # ── Score ──
        carte_score = ctk.CTkFrame(
            self.zone_principale, fg_color=BLEU_TRES_PALE,
            corner_radius=20, height=200)
        carte_score.pack(fill="x", pady=15)
        carte_score.pack_propagate(False)

        ctk.CTkLabel(carte_score,
                     text="🃏  RÉSULTAT DE LA SESSION",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=BLEU_ROYAL).pack(pady=(20, 5))

        ctk.CTkLabel(carte_score, text=f"{score} / {total}",
                     font=ctk.CTkFont(size=52, weight="bold"),
                     text_color=couleur_t).pack()

        ctk.CTkLabel(carte_score,
                     text=f"{pourcentage:.0f}% de cartes maîtrisées",
                     font=ctk.CTkFont(size=14),
                     text_color=GRIS_TEXTE).pack(pady=(5, 5))

        # ── Stats ──
        frame_stats = ctk.CTkFrame(
            self.zone_principale, fg_color=GRIS_PERLE, corner_radius=15)
        frame_stats.pack(fill="x", pady=10)

        ctk.CTkLabel(
            frame_stats,
            text=f"✅ Savais : {self._session_reussis}"
                 f"     ❌ Ne savais pas : {self._session_rates}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=GRIS_TEXTE).pack(pady=15)

        if self._session_rates > 0:
            msg = ctk.CTkFrame(
                self.zone_principale,
                fg_color=ORANGE_PALE, corner_radius=15)
            msg.pack(fill="x", pady=5)
            ctk.CTkLabel(
                msg,
                text=f"💡 Tu as {self._session_rates} carte(s) à retravailler.\n"
                     f"Clique sur '🔁 Réviser les ratées' pour te concentrer dessus !",
                font=ctk.CTkFont(size=13),
                text_color=GRIS_TEXTE, justify="center").pack(pady=12)

        # ── Boutons ──
        frame_btns = ctk.CTkFrame(self.zone_principale, fg_color="transparent")
        frame_btns.pack(fill="x", pady=15)

        self.creer_bouton_action(
            frame_btns, "🔄  Recommencer",
            lambda: self._lancer_revision(
                self._nom_deck_session
                if self._nom_deck_session != "Toutes les cartes"
                else None),
            VERT_EMERAUDE, VERT_HOVER).pack(
            side="left", padx=5, expand=True, fill="x")

        self.creer_bouton_action(
            frame_btns, "🔁  Réviser les ratées",
            self._reviser_ratees,
            ORANGE_DORE, ORANGE_CLAIR).pack(
            side="left", padx=5, expand=True, fill="x")

        self.creer_bouton_action(
            frame_btns, "⬅️  Retour aux decks",
            self.afficher_flashcards,
            BLEU_ROYAL, BLEU_CIEL).pack(
            side="left", padx=5, expand=True, fill="x")

        if score * 3 > 0:
            self._recompenser(score * 3, f"Flashcards : +{score * 3} XP !")

    def _voir_cartes_deck(self, nom_deck: str):
        self.vider_zone()
        self.afficher_titre(f"Deck : {nom_deck[:30]}", "🃏", BLEU_ROYAL)

        cards = db.lister_flashcards(nom_deck=nom_deck)

        self.creer_bouton_action(
            self.zone_principale, "⬅️  Retour aux decks",
            self.afficher_flashcards,
            BLEU_ROYAL, BLEU_CIEL).pack(pady=5, fill="x")

        frame_scroll = ctk.CTkScrollableFrame(
            self.zone_principale, fg_color=BLANC,
            corner_radius=15, border_width=2, border_color=BLEU_CIEL)
        frame_scroll.pack(fill="both", expand=True, pady=10)

        for card in cards:
            id_c, recto, verso, matiere, deck, nb_vus, nb_reussis, nb_rates, date_c = card

            carte = ctk.CTkFrame(
                frame_scroll, fg_color=BLEU_TRES_PALE,
                corner_radius=12, border_width=1, border_color=BLEU_CIEL)
            carte.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(carte, text=f"🔵 {recto[:80]}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=BLEU_ROYAL,
                         anchor="w", wraplength=700).pack(
                anchor="w", padx=15, pady=(10, 3))

            ctk.CTkLabel(carte, text=f"🟢 {verso[:100]}",
                         font=ctk.CTkFont(size=12),
                         text_color=VERT_CORRECTION,
                         anchor="w", wraplength=700).pack(
                anchor="w", padx=15, pady=(0, 5))

            taux_c = int((nb_reussis / nb_vus) * 100) if nb_vus > 0 else 0
            ligne_stats = ctk.CTkFrame(carte, fg_color="transparent")
            ligne_stats.pack(fill="x", padx=15, pady=(0, 8))

            ctk.CTkLabel(
                ligne_stats,
                text=f"👁️ {nb_vus} vues  •  ✅ {nb_reussis}"
                     f"  •  ❌ {nb_rates}  •  📊 {taux_c}%",
                font=ctk.CTkFont(size=10),
                text_color=GRIS_DOUX).pack(side="left")

            ctk.CTkButton(
                ligne_stats, text="🗑️",
                command=lambda i=id_c: self._supprimer_une_carte(i, nom_deck),
                fg_color=ROUGE, hover_color=ROUGE_CLAIR,
                text_color=BLANC, corner_radius=8,
                height=24, width=35,
                font=ctk.CTkFont(size=11)).pack(side="right")

    def _supprimer_une_carte(self, id_card: int, nom_deck: str):
        if messagebox.askyesno("🗑️ Supprimer ?", "Supprimer cette flashcard ?"):
            db.supprimer_flashcard(id_card)
            notification_succes(self, "Carte supprimée !", "🗑️")
            self._voir_cartes_deck(nom_deck)

    def _supprimer_deck(self, nom_deck: str):
        cards = db.lister_flashcards(nom_deck=nom_deck)
        if messagebox.askyesno(
                "🗑️ Supprimer le deck ?",
                f"Supprimer '{nom_deck}' ?\n\n"
                f"⚠️ {len(cards)} carte(s) seront supprimées !"):
            db.supprimer_deck(nom_deck)
            notification_succes(self, "Deck supprimé !", f"🗑️ {nom_deck}")
            self.afficher_flashcards()

    def _supprimer_tout_flashcards(self):
        nb = db.compter_flashcards()
        if nb == 0:
            messagebox.showinfo("ℹ️", "Aucune flashcard à supprimer !")
            return
        if messagebox.askyesno(
                "🗑️ Tout supprimer ?",
                f"⚠️ Supprimer les {nb} flashcards ?\n\nAction IRRÉVERSIBLE !"):
            import sqlite3
            conn = sqlite3.connect(db.DB_FILE)
            conn.execute("DELETE FROM flashcards")
            conn.commit()
            conn.close()
            notification_succes(self, "Tout supprimé !", "🗑️ Flashcards vidées")
            self.afficher_flashcards()