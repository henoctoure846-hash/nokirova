# ui/qcm_interactif.py - QCM Interactif NOKIROVA 🌸

import customtkinter as ctk
from tkinter import messagebox
import database as db
from ui.base import (VERT_EMERAUDE, VERT_HOVER, VERT_CLAIR, VERT_CORRECTION,
                     VERT_FOND_CORRECTION, BLEU_ROYAL, BLEU_CIEL, BLEU_TRES_PALE,
                     VIOLET_PREMIUM, VIOLET_LAVANDE, VIOLET_PALE,
                     JAUNE_CLAIR, JAUNE_SOLEIL, OR_MODERNE,
                     ORANGE_DORE, ORANGE_CLAIR,
                     ROUGE, ROUGE_CLAIR, ROUGE_FOND,
                     BLANC, BLANC_CASSE, GRIS_TEXTE, GRIS_PERLE,
                     parser_qcm)


class QCMInteractifMixin:

    # ═══════════════════════════════════════════
    # 🎮 QCM INTERACTIF
    # ═══════════════════════════════════════════

    def lancer_qcm_interactif(self):
        if not self.contenu_qcm_complet or len(self.contenu_qcm_complet) < 50:
            messagebox.showwarning(
                "⚠️", "Génère d'abord des QCM avec le bouton 🎯 !")
            return

        self.qcms_interactifs = parser_qcm(self.contenu_qcm_complet)

        if not self.qcms_interactifs:
            messagebox.showerror(
                "❌ Parsing échoué",
                "Impossible de parser les QCM.\n"
                "Régénère-les avec le bouton 🎯.")
            return

        self.qcm_index = 0
        self.qcm_score = 0
        self.qcm_reponses = []
        self.afficher_qcm_interactif()

    def afficher_qcm_interactif(self):
        self.vider_zone()

        total = len(self.qcms_interactifs)
        actuel = self.qcm_index + 1

        # ── Titre ──
        carte_titre = ctk.CTkFrame(self.zone_principale,
                                   fg_color=VIOLET_PREMIUM,
                                   corner_radius=18, height=85)
        carte_titre.pack(fill="x", pady=(0, 10))
        carte_titre.pack_propagate(False)

        ctk.CTkLabel(
            carte_titre,
            text=f"🎮  QCM Interactif  •  "
                 f"Question {actuel}/{total}  •  "
                 f"Score : {self.qcm_score}/{actuel - 1}",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=BLANC).pack(pady=28)

        # ── Progression ──
        progress = ctk.CTkProgressBar(
            self.zone_principale,
            progress_color=VERT_EMERAUDE,
            fg_color=GRIS_PERLE, height=12, corner_radius=6)
        progress.set(actuel / total)
        progress.pack(fill="x", padx=5, pady=5)

        # ── Zone scrollable ──
        zone_scroll = ctk.CTkScrollableFrame(
            self.zone_principale,
            fg_color=BLANC_CASSE, corner_radius=0)
        zone_scroll.pack(fill="both", expand=True, pady=5)

        qcm = self.qcms_interactifs[self.qcm_index]

        # ── Question ──
        carte_question = ctk.CTkFrame(
            zone_scroll, fg_color=BLEU_TRES_PALE,
            corner_radius=18, border_width=2, border_color=BLEU_ROYAL)
        carte_question.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(carte_question,
                     text=f"❓  QUESTION N°{qcm['numero']}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=BLEU_ROYAL).pack(pady=(15, 5))

        ctk.CTkLabel(carte_question,
                     text=qcm['question'],
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=GRIS_TEXTE,
                     wraplength=800, justify="left").pack(
            padx=20, pady=(0, 15))

        # ── Options ──
        self.frame_options = ctk.CTkFrame(zone_scroll, fg_color="transparent")
        self.frame_options.pack(fill="x", pady=10, padx=5)

        self.boutons_options = {}
        couleurs_options = [BLEU_CIEL, ROSE_CLAIR, JAUNE_CLAIR, ORANGE_PALE]

        # Import ici pour éviter les imports circulaires
        from ui.base import ROSE_CLAIR, ORANGE_PALE

        couleurs_options = [BLEU_CIEL, ROSE_CLAIR, JAUNE_CLAIR, ORANGE_PALE]

        for i, (lettre, texte) in enumerate(qcm['options'].items()):
            btn = ctk.CTkButton(
                self.frame_options,
                text=f"  {lettre})   {texte}",
                command=lambda l=lettre: self._repondre_qcm(l),
                fg_color=couleurs_options[i % 4],
                hover_color=VERT_CLAIR,
                text_color=GRIS_TEXTE,
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                height=55, corner_radius=14, anchor="w")
            btn.pack(fill="x", padx=10, pady=5)
            self.boutons_options[lettre] = btn

        # ── Feedback ──
        self.zone_feedback = ctk.CTkFrame(zone_scroll, fg_color="transparent")
        self.zone_feedback.pack(fill="x", pady=10, padx=5)

    def _repondre_qcm(self, lettre_choisie):
        qcm = self.qcms_interactifs[self.qcm_index]
        bonne = qcm['bonne_reponse']
        correct = (lettre_choisie == bonne)

        if correct:
            self.qcm_score += 1
            db.incrementer_stat("qcm_reussis")
        else:
            db.incrementer_stat("qcm_rates")

        self.qcm_reponses.append({
            "qcm": qcm,
            "choix": lettre_choisie,
            "correct": correct})

        # ── Colorer les boutons ──
        for lettre, btn in self.boutons_options.items():
            btn.configure(state="disabled")
            if lettre == bonne:
                btn.configure(
                    fg_color=VERT_EMERAUDE, text_color=BLANC,
                    text=f"  ✅ {lettre})   {qcm['options'][lettre]}  ✅")
            elif lettre == lettre_choisie and not correct:
                btn.configure(
                    fg_color=ROUGE, text_color=BLANC,
                    text=f"  ❌ {lettre})   {qcm['options'][lettre]}  ❌")

        # ── Feedback ──
        for widget in self.zone_feedback.winfo_children():
            widget.destroy()

        if correct:
            carte_feedback = ctk.CTkFrame(
                self.zone_feedback,
                fg_color=VERT_FOND_CORRECTION,
                corner_radius=15,
                border_width=2, border_color=VERT_EMERAUDE)
            carte_feedback.pack(fill="x", pady=5)
            ctk.CTkLabel(carte_feedback,
                         text="🎉  BRAVO ! Bonne réponse !",
                         font=ctk.CTkFont(size=18, weight="bold"),
                         text_color=VERT_CORRECTION).pack(pady=(15, 5))
        else:
            carte_feedback = ctk.CTkFrame(
                self.zone_feedback,
                fg_color=ROUGE_FOND,
                corner_radius=15,
                border_width=2, border_color=ROUGE)
            carte_feedback.pack(fill="x", pady=5)
            ctk.CTkLabel(
                carte_feedback,
                text=f"❌  Mauvaise réponse... "
                     f"La bonne réponse était : {bonne}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=ROUGE).pack(pady=(15, 5))

        if qcm['explication']:
            ctk.CTkLabel(carte_feedback,
                         text=f"💡 {qcm['explication']}",
                         font=ctk.CTkFont(size=13),
                         text_color=GRIS_TEXTE,
                         wraplength=800, justify="left").pack(
                padx=20, pady=(5, 10))

        if qcm['erreur_courante']:
            ctk.CTkLabel(carte_feedback,
                         text=f"⚠️ {qcm['erreur_courante']}",
                         font=ctk.CTkFont(size=12, slant="italic"),
                         text_color=ORANGE_DORE,
                         wraplength=800, justify="left").pack(
                padx=20, pady=(0, 15))

        # ── Bouton suivant ou bilan ──
        if self.qcm_index < len(self.qcms_interactifs) - 1:
            ctk.CTkButton(
                self.zone_feedback,
                text="▶️  QUESTION SUIVANTE",
                command=self._qcm_suivant,
                fg_color=VIOLET_PREMIUM,
                hover_color=VIOLET_LAVANDE,
                text_color=BLANC, corner_radius=14,
                font=ctk.CTkFont(size=16, weight="bold"),
                height=55, border_width=3,
                border_color=VIOLET_LAVANDE).pack(
                fill="x", padx=10, pady=15)
        else:
            ctk.CTkButton(
                self.zone_feedback,
                text="🏆  VOIR MON BILAN",
                command=self._afficher_bilan_qcm,
                fg_color=OR_MODERNE,
                hover_color=ORANGE_CLAIR,
                text_color=BLANC, corner_radius=14,
                font=ctk.CTkFont(size=16, weight="bold"),
                height=55, border_width=3,
                border_color=JAUNE_SOLEIL).pack(
                fill="x", padx=10, pady=15)

        self.update_idletasks()

    def _qcm_suivant(self):
        self.qcm_index += 1
        self.afficher_qcm_interactif()

    def _afficher_bilan_qcm(self):
        self.vider_zone()

        total = len(self.qcms_interactifs)
        score = self.qcm_score
        pourcentage = (score / total) * 100 if total else 0

        if pourcentage >= 80:
            emoji_titre, titre, couleur_titre = "🏆", "EXCELLENT !", VERT_EMERAUDE
        elif pourcentage >= 60:
            emoji_titre, titre, couleur_titre = "🎯", "BIEN JOUÉ !", BLEU_ROYAL
        elif pourcentage >= 40:
            emoji_titre, titre, couleur_titre = "💪", "CONTINUE TES EFFORTS !", ORANGE_DORE
        else:
            emoji_titre, titre, couleur_titre = "📚", "RÉVISE ENCORE !", ROUGE

        self.afficher_titre(titre, emoji_titre, couleur_titre)

        # ── Score ──
        carte_score = ctk.CTkFrame(
            self.zone_principale,
            fg_color=VERT_FOND_CORRECTION,
            corner_radius=20, height=180)
        carte_score.pack(fill="x", pady=15)
        carte_score.pack_propagate(False)

        ctk.CTkLabel(carte_score,
                     text="🎯  TON SCORE",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=GRIS_TEXTE).pack(pady=(20, 5))

        ctk.CTkLabel(carte_score,
                     text=f"{score} / {total}",
                     font=ctk.CTkFont(family="Segoe UI", size=48, weight="bold"),
                     text_color=VERT_CORRECTION).pack()

        ctk.CTkLabel(carte_score,
                     text=f"{pourcentage:.0f}% de bonnes réponses",
                     font=ctk.CTkFont(size=14),
                     text_color=GRIS_TEXTE).pack(pady=(5, 20))

        # ── Détail ──
        carte_detail = ctk.CTkScrollableFrame(
            self.zone_principale, fg_color=BLANC,
            corner_radius=15, border_width=2,
            border_color=VERT_CLAIR, height=250)
        carte_detail.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(carte_detail,
                     text="📋  DÉTAIL DES RÉPONSES",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=GRIS_TEXTE).pack(pady=10)

        for i, rep in enumerate(self.qcm_reponses):
            emoji = "✅" if rep['correct'] else "❌"
            couleur_fond = VERT_FOND_CORRECTION if rep['correct'] else ROUGE_FOND

            ligne = ctk.CTkFrame(carte_detail,
                                 fg_color=couleur_fond, corner_radius=10)
            ligne.pack(fill="x", padx=10, pady=3)

            ctk.CTkLabel(
                ligne,
                text=f"{emoji}  Q{i + 1} : "
                     f"{rep['qcm']['question'][:60]}...",
                font=ctk.CTkFont(size=12),
                text_color=GRIS_TEXTE, anchor="w").pack(
                side="left", padx=10, pady=8)

            ctk.CTkLabel(
                ligne,
                text=f"Tu as : {rep['choix']}  •  "
                     f"Bonne : {rep['qcm']['bonne_reponse']}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=VIOLET_PREMIUM).pack(side="right", padx=10)

        # ── Boutons ──
        frame_btns = ctk.CTkFrame(self.zone_principale, fg_color="transparent")
        frame_btns.pack(fill="x", pady=10)

        self.creer_bouton_action(
            frame_btns, "🔄  Recommencer",
            self.lancer_qcm_interactif,
            VERT_EMERAUDE, VERT_HOVER).pack(
            side="left", padx=5, expand=True, fill="x")

        self.creer_bouton_action(
            frame_btns, "⬅️  Retour aux QCM",
            self.afficher_qcm,
            VIOLET_PREMIUM, VIOLET_LAVANDE).pack(
            side="left", padx=5, expand=True, fill="x")

        if score * 5 > 0:
            self._recompenser(score * 5, f"QCM Interactif : +{score * 5} XP !")