# ui/accueil.py - Page Accueil NOKIROVA 🌸

import customtkinter as ctk
from datetime import datetime
import database as db
from ui.base import (BLANC_CASSE, BLEU_TRES_PALE, VIOLET_PREMIUM, GRIS_TEXTE,
                     JAUNE_CLAIR, JAUNE_PALE, ORANGE_CLAIR, VERT_CLAIR, BLANC,
                     ROSE_SAKURA, BLEU_CIEL, ORANGE_PALE, VERT_FOND_CORRECTION,
                     VIOLET_PALE, VIOLET_LAVANDE, VERT_EMERAUDE, VERT_HOVER,
                     ORANGE_DORE, GRIS_DOUX, ROUGE, BLEU_ROYAL)


JOURS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi",
            "Vendredi", "Samedi", "Dimanche"]
MOIS_FR = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
           "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]


class AccueilMixin:

    def afficher_accueil(self):
        self.vider_zone()

        # ── SCROLL PRINCIPAL ──
        scroll = ctk.CTkScrollableFrame(
            self.zone_principale, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # ── Hero ──
        hero = ctk.CTkFrame(scroll, fg_color=BLEU_TRES_PALE,
                            corner_radius=20, height=170)
        hero.pack(fill="x", pady=(0, 15))
        hero.pack_propagate(False)

        hero_content = ctk.CTkFrame(hero, fg_color="transparent")
        hero_content.pack(expand=True)

        if self.logo_accueil:
            ctk.CTkLabel(hero_content,
                         image=self.logo_accueil, text="").pack(
                side="left", padx=(0, 15), pady=20)

        texte_frame = ctk.CTkFrame(hero_content, fg_color="transparent")
        texte_frame.pack(side="left", pady=20)

        ctk.CTkLabel(texte_frame, text="Bienvenue dans NOKIROVA !",
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color=VIOLET_PREMIUM).pack(anchor="w")
        ctk.CTkLabel(texte_frame, text="✨ Ton professeur intelligent personnel ✨",
                     font=ctk.CTkFont(size=14),
                     text_color=GRIS_TEXTE).pack(anchor="w")

        # ── 🆕 CARTE "AUJOURD'HUI" (Phase 3.1) ──
        self._afficher_carte_aujourd_hui(scroll)

        # ── Mini stats ──
        stats = db.get_stats()
        mini_stats = ctk.CTkFrame(scroll, fg_color="transparent")
        mini_stats.pack(fill="x", pady=5)

        carte_xp = ctk.CTkFrame(mini_stats, fg_color=JAUNE_CLAIR,
                                corner_radius=12, height=70)
        carte_xp.pack(side="left", padx=5, expand=True, fill="x")
        carte_xp.pack_propagate(False)
        ctk.CTkLabel(carte_xp, text=f"⭐ Niveau {stats['niveau']}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=GRIS_TEXTE).pack(pady=(12, 0))
        ctk.CTkLabel(carte_xp, text=f"{stats['xp']} XP",
                     font=ctk.CTkFont(size=12),
                     text_color=GRIS_TEXTE).pack()

        carte_streak = ctk.CTkFrame(mini_stats, fg_color=ORANGE_CLAIR,
                                    corner_radius=12, height=70)
        carte_streak.pack(side="left", padx=5, expand=True, fill="x")
        carte_streak.pack_propagate(False)
        ctk.CTkLabel(carte_streak, text=f"🔥 {stats['streak']} jour(s)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=BLANC).pack(pady=(12, 0))
        ctk.CTkLabel(carte_streak, text="Streak quotidien",
                     font=ctk.CTkFont(size=11),
                     text_color=BLANC).pack()

        carte_cours = ctk.CTkFrame(mini_stats, fg_color=VERT_CLAIR,
                                   corner_radius=12, height=70)
        carte_cours.pack(side="left", padx=5, expand=True, fill="x")
        carte_cours.pack_propagate(False)
        ctk.CTkLabel(carte_cours, text=f"📚 {stats['cours_importes']}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=BLANC).pack(pady=(12, 0))
        ctk.CTkLabel(carte_cours, text="Cours importés",
                     font=ctk.CTkFont(size=11),
                     text_color=BLANC).pack()

        # ── Grille raccourcis ──
        grille = ctk.CTkFrame(scroll, fg_color="transparent")
        grille.pack(fill="x", pady=10)

        cartes_data = [
            ("📚", "Bibliothèque", VERT_CLAIR, self.afficher_bibliotheque),
            ("📅", "Planificateur", VIOLET_LAVANDE, self.afficher_planificateur),
            ("📸", "Scan Multi", VERT_EMERAUDE, self.afficher_scan_multipages),
            ("🎯", "QCM", ROSE_SAKURA, self.afficher_qcm),
            ("🃏", "Flashcards", BLEU_CIEL, self.afficher_flashcards),
            ("⏱️", "Pomodoro", ORANGE_PALE, self.afficher_pomodoro),
        ]

        for i, (emoji, titre, couleur, cmd) in enumerate(cartes_data):
            carte = ctk.CTkFrame(grille, fg_color=couleur,
                                 corner_radius=16, width=160, height=100)
            carte.grid(row=0, column=i, padx=4, pady=10, sticky="nsew")
            carte.pack_propagate(False)
            grille.grid_columnconfigure(i, weight=1)

            ctk.CTkLabel(carte, text=emoji,
                         font=ctk.CTkFont(size=28)).pack(pady=(10, 2))
            ctk.CTkLabel(carte, text=titre,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=GRIS_TEXTE).pack()
            ctk.CTkButton(carte, text="→ Ouvrir", command=cmd,
                          fg_color=BLANC, text_color=GRIS_TEXTE,
                          hover_color=BLANC_CASSE,
                          height=24, font=ctk.CTkFont(size=10, weight="bold"),
                          corner_radius=10).pack(pady=4)

        # ── Objectif du jour ──
        objectif = ctk.CTkFrame(scroll,
                                fg_color=JAUNE_PALE, corner_radius=16)
        objectif.pack(fill="x", pady=8)
        ctk.CTkLabel(objectif, text="🎯 OBJECTIF DU JOUR",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=ORANGE_DORE).pack(pady=(12, 3))
        ctk.CTkLabel(objectif,
                     text="💪 Importe un cours et fais au moins 5 QCM !\n"
                          "Tu vas y arriver ! 🌟",
                     font=ctk.CTkFont(size=13),
                     text_color=GRIS_TEXTE).pack(pady=(0, 12))

        # ── Bouton principal ──
        self.creer_bouton_action(
            scroll,
            "🚀  COMMENCER MAINTENANT",
            self.afficher_import,
            VERT_EMERAUDE, VERT_HOVER).pack(pady=8, fill="x")

    # ═══════════════════════════════════════════
    # 🌅 CARTE "AUJOURD'HUI" (Planificateur)
    # ═══════════════════════════════════════════

    def _afficher_carte_aujourd_hui(self, parent):
        """Affiche les tâches du jour sur l'accueil"""
        try:
            taches = db.lister_taches_jour()
            nb_retard = db.compter_taches_en_retard()
        except Exception:
            taches = []
            nb_retard = 0

        # Salutation selon l'heure
        h = datetime.now().hour
        if h < 12:
            salut = "🌅 Bonjour"
        elif h < 18:
            salut = "☀️ Bon après-midi"
        else:
            salut = "🌙 Bonsoir"

        aujourd = datetime.now()
        date_texte = (f"{JOURS_FR[aujourd.weekday()]} "
                      f"{aujourd.day} {MOIS_FR[aujourd.month - 1]}")

        # ── Cadre principal ──
        cadre = ctk.CTkFrame(parent, fg_color=VIOLET_PALE,
                             corner_radius=16,
                             border_width=2, border_color=VIOLET_LAVANDE)
        cadre.pack(fill="x", pady=8)

        # ── En-tête ──
        entete = ctk.CTkFrame(cadre, fg_color="transparent")
        entete.pack(fill="x", padx=15, pady=(12, 5))

        ctk.CTkLabel(
            entete, text=f"{salut} ! • {date_texte}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=VIOLET_PREMIUM).pack(side="left")

        # Pastille retard
        if nb_retard > 0:
            ctk.CTkLabel(
                entete, text=f"🔴  {nb_retard} en retard",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=ROUGE).pack(side="right")

        # ── Contenu ──
        if not taches:
            # Pas de tâches
            ctk.CTkLabel(
                cadre,
                text="📭  Aucune tâche prévue aujourd'hui !\n"
                     "💡 Clique sur 📅 Planificateur pour en ajouter.",
                font=ctk.CTkFont(size=12),
                text_color=GRIS_DOUX, justify="center").pack(pady=15)
        else:
            # Compter faites/total
            faites = sum(1 for t in taches if t[9] == "faite")
            total = len(taches)

            # Mini barre de progression
            progress_frame = ctk.CTkFrame(cadre, fg_color="transparent")
            progress_frame.pack(fill="x", padx=15, pady=(5, 10))

            ctk.CTkLabel(
                progress_frame,
                text=f"✅ {faites}/{total} tâches accomplies",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=VERT_EMERAUDE).pack(side="left")

            pct = (faites / total) if total > 0 else 0
            barre = ctk.CTkProgressBar(
                progress_frame, progress_color=VERT_EMERAUDE,
                fg_color=BLANC, height=10, corner_radius=5)
            barre.pack(side="right", padx=(10, 0),
                       fill="x", expand=True)
            barre.set(pct)

            # Liste des 3 prochaines tâches
            for tache in taches[:3]:
                (id_t, titre, desc, matiere, type_t, prio,
                 date_t, heure, duree, statut, recur, cours_id) = tache

                type_info = db.TYPES_TACHES.get(
                    type_t, db.TYPES_TACHES["reviser"])
                coul_mat = db.couleur_matiere(matiere)
                est_faite = statut == "faite"

                ligne = ctk.CTkFrame(
                    cadre,
                    fg_color=VERT_FOND_CORRECTION if est_faite else BLANC,
                    corner_radius=10,
                    border_width=2, border_color=coul_mat)
                ligne.pack(fill="x", padx=15, pady=3)

                check = "✅" if est_faite else "⬜"
                texte = (f"{check}  {type_info['emoji']} "
                         f"{titre[:35]}  •  ⏰ {heure}  "
                         f"({duree}min)")

                ctk.CTkLabel(
                    ligne, text=texte,
                    font=ctk.CTkFont(
                        size=12,
                        weight="bold",
                        overstrike=est_faite),
                    text_color=GRIS_DOUX if est_faite else GRIS_TEXTE,
                    anchor="w").pack(side="left", padx=10, pady=8)

                ctk.CTkLabel(
                    ligne, text=f"🎯 {matiere[:15]}",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=coul_mat).pack(side="right", padx=10)

            if len(taches) > 3:
                ctk.CTkLabel(
                    cadre,
                    text=f"+ {len(taches) - 3} autres tâches...",
                    font=ctk.CTkFont(size=10, slant="italic"),
                    text_color=GRIS_DOUX).pack(pady=(2, 5))

            # Bouton "Voir tout"
            ctk.CTkButton(
                cadre, text="📅  Voir mon planning complet",
                command=self.afficher_planificateur,
                fg_color=VIOLET_PREMIUM, hover_color=VIOLET_LAVANDE,
                text_color=BLANC, height=36,
                font=ctk.CTkFont(size=12, weight="bold"),
                corner_radius=10).pack(fill="x", padx=15, pady=(5, 12))