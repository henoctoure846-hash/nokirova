# ui/planificateur.py - Page Planificateur NOKIROVA 📅

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
import calendar
import database as db
from ui.base import (
    VERT_EMERAUDE, VERT_HOVER, VERT_CLAIR, VERT_CORRECTION,
    VERT_FOND_CORRECTION,
    BLEU_ROYAL, BLEU_CIEL, BLEU_TRES_PALE, BLEU_PALE,
    JAUNE_SOLEIL, JAUNE_CLAIR, JAUNE_PALE, OR_MODERNE,
    VIOLET_PREMIUM, VIOLET_LAVANDE, VIOLET_PALE, VIOLET_CLAIR,
    ROSE_SAKURA, ROSE_PALE, ROSE_CLAIR,
    ORANGE_DORE, ORANGE_CLAIR, ORANGE_PALE,
    ROUGE, ROUGE_CLAIR, ROUGE_FOND,
    BLANC, BLANC_CASSE, GRIS_TEXTE, GRIS_DOUX, GRIS_PERLE
)
from notifications import notification_succes


JOURS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi",
            "Vendredi", "Samedi", "Dimanche"]
MOIS_FR = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
           "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]


class PlanificateurMixin:

    # ═══════════════════════════════════════════
    # 📅 PAGE PRINCIPALE
    # ═══════════════════════════════════════════

    def afficher_planificateur(self):
        self.vider_zone()
        self.afficher_titre("Planificateur d'Études", "📅", VIOLET_PREMIUM)

        # Init variables
        if not hasattr(self, '_plan_vue'):
            self._plan_vue = "jour"
        if not hasattr(self, '_plan_date'):
            self._plan_date = datetime.now()

        # ── SCROLL principal ──
        scroll = ctk.CTkScrollableFrame(
            self.zone_principale, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        self._plan_scroll = scroll

        # ── Stats rapides ──
        self._afficher_stats_planning(scroll)

        # ── Onglets vues + bouton ajouter ──
        self._afficher_barre_outils(scroll)

        # ── Navigation date ──
        self._afficher_navigation_date(scroll)

        # ── Contenu selon vue ──
        self._afficher_vue_actuelle(scroll)

    # ═══════════════════════════════════════════
    # 📊 STATS EN HAUT
    # ═══════════════════════════════════════════

    def _afficher_stats_planning(self, parent):
        stats = db.stats_planning()
        bandeau = ctk.CTkFrame(parent, fg_color="transparent")
        bandeau.pack(fill="x", pady=(0, 8))

        cartes = [
            ("🎯", f"{stats['aujourd_faites']}/{stats['aujourd_total']}",
             "Aujourd'hui", VERT_EMERAUDE),
            ("⏱️", f"{stats['temps_semaine_h']}h",
             "Cette semaine", BLEU_ROYAL),
            ("✅", f"{stats['pourcentage_reussi']}%",
             "Taux réussite", JAUNE_SOLEIL),
            ("🔴", str(stats['en_retard']),
             "En retard", ROUGE if stats['en_retard'] > 0 else VERT_CLAIR),
        ]

        for emoji, val, label, couleur in cartes:
            c = ctk.CTkFrame(bandeau, fg_color=couleur,
                             corner_radius=12, height=70)
            c.pack(side="left", padx=4, expand=True, fill="x")
            c.pack_propagate(False)
            ctk.CTkLabel(c, text=f"{emoji} {val}",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=BLANC).pack(pady=(12, 0))
            ctk.CTkLabel(c, text=label,
                         font=ctk.CTkFont(size=11),
                         text_color=BLANC).pack()

    # ═══════════════════════════════════════════
    # 🛠️ BARRE D'OUTILS
    # ═══════════════════════════════════════════

    def _afficher_barre_outils(self, parent):
        barre = ctk.CTkFrame(
            parent, fg_color=VIOLET_LAVANDE, corner_radius=14)
        barre.pack(fill="x", pady=8)

        # Onglets de vue
        onglets_frame = ctk.CTkFrame(barre, fg_color="transparent")
        onglets_frame.pack(side="left", padx=12, pady=12)

        vues = [("jour", "📆 Jour"), ("semaine", "📅 Semaine"),
                ("mois", "🗓️ Mois")]
        for code, label in vues:
            actif = self._plan_vue == code
            ctk.CTkButton(
                onglets_frame, text=label,
                command=lambda c=code: self._changer_vue(c),
                fg_color=BLANC if actif else VIOLET_PREMIUM,
                text_color=VIOLET_PREMIUM if actif else BLANC,
                hover_color=VIOLET_PALE,
                font=ctk.CTkFont(size=13, weight="bold"),
                height=38, width=110,
                corner_radius=10).pack(side="left", padx=3)

        # Boutons d'action
        actions = ctk.CTkFrame(barre, fg_color="transparent")
        actions.pack(side="right", padx=12, pady=12)

        ctk.CTkButton(
            actions, text="🤖  Générateur IA",
            command=self._ouvrir_generateur_ia,
            fg_color=ORANGE_DORE, hover_color=OR_MODERNE,
            text_color=BLANC,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=38, corner_radius=10).pack(side="left", padx=3)

        ctk.CTkButton(
            actions, text="➕  Nouvelle tâche",
            command=self._ouvrir_form_ajout,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38, corner_radius=10).pack(side="left", padx=3)

    def _changer_vue(self, vue):
        self._plan_vue = vue
        self._plan_date = datetime.now()
        self.afficher_planificateur()

    # ═══════════════════════════════════════════
    # ⬅️➡️ NAVIGATION DATE
    # ═══════════════════════════════════════════

    def _afficher_navigation_date(self, parent):
        nav = ctk.CTkFrame(parent, fg_color=VIOLET_PALE, corner_radius=12)
        nav.pack(fill="x", pady=5)

        ctk.CTkButton(
            nav, text="⬅️", command=self._date_precedente,
            fg_color=VIOLET_PREMIUM, hover_color=VIOLET_LAVANDE,
            text_color=BLANC, width=45, height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10).pack(side="left", padx=12, pady=8)

        # Texte central
        if self._plan_vue == "jour":
            jour_idx = self._plan_date.weekday()
            texte = (f"{JOURS_FR[jour_idx]} "
                     f"{self._plan_date.day} "
                     f"{MOIS_FR[self._plan_date.month - 1]} "
                     f"{self._plan_date.year}")
        elif self._plan_vue == "semaine":
            lundi = self._plan_date - timedelta(
                days=self._plan_date.weekday())
            dimanche = lundi + timedelta(days=6)
            texte = (f"Semaine du {lundi.day} "
                     f"{MOIS_FR[lundi.month - 1][:4]} "
                     f"au {dimanche.day} "
                     f"{MOIS_FR[dimanche.month - 1][:4]}")
        else:
            texte = (f"{MOIS_FR[self._plan_date.month - 1]} "
                     f"{self._plan_date.year}")

        ctk.CTkLabel(nav, text=texte,
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=VIOLET_PREMIUM).pack(
            side="left", expand=True, pady=8)

        ctk.CTkButton(
            nav, text="📍  Aujourd'hui",
            command=self._date_aujourd_hui,
            fg_color=JAUNE_SOLEIL, hover_color=OR_MODERNE,
            text_color=GRIS_TEXTE, height=36,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=10).pack(side="left", padx=5, pady=8)

        ctk.CTkButton(
            nav, text="➡️", command=self._date_suivante,
            fg_color=VIOLET_PREMIUM, hover_color=VIOLET_LAVANDE,
            text_color=BLANC, width=45, height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10).pack(side="right", padx=12, pady=8)

    def _date_precedente(self):
        if self._plan_vue == "jour":
            self._plan_date -= timedelta(days=1)
        elif self._plan_vue == "semaine":
            self._plan_date -= timedelta(days=7)
        else:
            m = self._plan_date.month - 1
            a = self._plan_date.year
            if m < 1:
                m, a = 12, a - 1
            self._plan_date = self._plan_date.replace(year=a, month=m, day=1)
        self.afficher_planificateur()

    def _date_suivante(self):
        if self._plan_vue == "jour":
            self._plan_date += timedelta(days=1)
        elif self._plan_vue == "semaine":
            self._plan_date += timedelta(days=7)
        else:
            m = self._plan_date.month + 1
            a = self._plan_date.year
            if m > 12:
                m, a = 1, a + 1
            self._plan_date = self._plan_date.replace(year=a, month=m, day=1)
        self.afficher_planificateur()

    def _date_aujourd_hui(self):
        self._plan_date = datetime.now()
        self.afficher_planificateur()

    # ═══════════════════════════════════════════
    # 🖼️ AFFICHAGE VUE ACTUELLE
    # ═══════════════════════════════════════════

    def _afficher_vue_actuelle(self, parent):
        if self._plan_vue == "jour":
            self._afficher_vue_jour(parent)
        elif self._plan_vue == "semaine":
            self._afficher_vue_semaine(parent)
        else:
            self._afficher_vue_mois(parent)

    # ─── VUE JOUR ───
    def _afficher_vue_jour(self, parent):
        date_str = self._plan_date.strftime("%Y-%m-%d")
        taches = db.lister_taches_jour(date_str)

        cadre = ctk.CTkFrame(parent, fg_color=BLANC, corner_radius=14,
                             border_width=2, border_color=VIOLET_PALE)
        cadre.pack(fill="x", pady=10)

        if not taches:
            ctk.CTkLabel(
                cadre,
                text="📭  Aucune tâche pour ce jour !\n\n"
                     "💡 Clique sur ➕ Nouvelle tâche pour en ajouter.",
                font=ctk.CTkFont(size=14),
                text_color=GRIS_DOUX, justify="center").pack(pady=40)
            return

        for tache in taches:
            self._creer_carte_tache(cadre, tache, mode="jour")

    # ─── VUE SEMAINE ───
    def _afficher_vue_semaine(self, parent):
        lundi = self._plan_date - timedelta(days=self._plan_date.weekday())
        date_str = lundi.strftime("%Y-%m-%d")
        toutes_taches = db.lister_taches_semaine(date_str)

        # Grouper par jour
        taches_par_jour = {i: [] for i in range(7)}
        for tache in toutes_taches:
            try:
                d = datetime.strptime(tache[6], "%Y-%m-%d")
                jour_idx = (d - lundi).days
                if 0 <= jour_idx < 7:
                    taches_par_jour[jour_idx].append(tache)
            except Exception:
                continue

        grille = ctk.CTkFrame(parent, fg_color="transparent")
        grille.pack(fill="both", expand=True, pady=8)

        for i in range(7):
            jour = lundi + timedelta(days=i)
            col = ctk.CTkFrame(
                grille, fg_color=BLANC, corner_radius=12,
                border_width=2,
                border_color=VERT_EMERAUDE if jour.date() ==
                datetime.now().date() else VIOLET_PALE)
            col.grid(row=0, column=i, padx=3, pady=3, sticky="nsew")
            grille.grid_columnconfigure(i, weight=1, uniform="jour")

            # En-tête jour
            entete = ctk.CTkFrame(
                col, fg_color=VIOLET_LAVANDE, corner_radius=10, height=55)
            entete.pack(fill="x", padx=4, pady=4)
            entete.pack_propagate(False)
            ctk.CTkLabel(
                entete, text=JOURS_FR[i][:3],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=BLANC).pack(pady=(8, 0))
            ctk.CTkLabel(
                entete, text=str(jour.day),
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=BLANC).pack()

            # Tâches du jour
            for tache in taches_par_jour[i]:
                self._creer_mini_carte_tache(col, tache)

            if not taches_par_jour[i]:
                ctk.CTkLabel(
                    col, text="—",
                    font=ctk.CTkFont(size=10),
                    text_color=GRIS_DOUX).pack(pady=10)

    # ─── VUE MOIS ───
    def _afficher_vue_mois(self, parent):
        annee = self._plan_date.year
        mois = self._plan_date.month
        toutes_taches = db.lister_taches_mois(annee, mois)

        # Grouper par jour
        taches_par_jour = {}
        for tache in toutes_taches:
            try:
                d = datetime.strptime(tache[6], "%Y-%m-%d").day
                if d not in taches_par_jour:
                    taches_par_jour[d] = []
                taches_par_jour[d].append(tache)
            except Exception:
                continue

        # Calendrier
        cal = calendar.Calendar(firstweekday=0)
        semaines = cal.monthdatescalendar(annee, mois)

        cadre = ctk.CTkFrame(parent, fg_color=BLANC, corner_radius=14,
                             border_width=2, border_color=VIOLET_PALE)
        cadre.pack(fill="both", expand=True, pady=8)

        # En-tête jours
        entete = ctk.CTkFrame(cadre, fg_color=VIOLET_LAVANDE, corner_radius=8)
        entete.pack(fill="x", padx=6, pady=6)
        for i, j in enumerate(["Lun", "Mar", "Mer", "Jeu",
                               "Ven", "Sam", "Dim"]):
            ctk.CTkLabel(
                entete, text=j,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=BLANC, width=100).grid(
                row=0, column=i, padx=2, pady=6, sticky="ew")
            entete.grid_columnconfigure(i, weight=1)

        # Grille des jours
        grille = ctk.CTkFrame(cadre, fg_color="transparent")
        grille.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        for r, semaine in enumerate(semaines):
            for c, jour in enumerate(semaine):
                est_mois = jour.month == mois
                est_today = jour == datetime.now().date()
                fg = (VERT_FOND_CORRECTION if est_today
                      else BLANC if est_mois else GRIS_PERLE)
                bd = VERT_EMERAUDE if est_today else VIOLET_PALE

                case = ctk.CTkFrame(
                    grille, fg_color=fg, corner_radius=8,
                    border_width=2 if est_today else 1,
                    border_color=bd, height=80)
                case.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
                case.grid_propagate(False)
                grille.grid_columnconfigure(c, weight=1, uniform="case")
                grille.grid_rowconfigure(r, weight=1)

                ctk.CTkLabel(
                    case, text=str(jour.day),
                    font=ctk.CTkFont(
                        size=12,
                        weight="bold" if est_today else "normal"),
                    text_color=GRIS_TEXTE if est_mois else GRIS_DOUX).pack(
                    anchor="nw", padx=5, pady=2)

                # Pastilles tâches (par couleur matière)
                if est_mois and jour.day in taches_par_jour:
                    p_frame = ctk.CTkFrame(case, fg_color="transparent")
                    p_frame.pack(anchor="nw", padx=5)
                    for t in taches_par_jour[jour.day][:3]:
                        coul = db.couleur_matiere(t[3])
                        ctk.CTkLabel(
                            p_frame, text="●",
                            font=ctk.CTkFont(size=14, weight="bold"),
                            text_color=coul, width=12).pack(
                            side="left", padx=0)
                    if len(taches_par_jour[jour.day]) > 3:
                        ctk.CTkLabel(
                            case,
                            text=f"+{len(taches_par_jour[jour.day]) - 3}",
                            font=ctk.CTkFont(size=9),
                            text_color=GRIS_DOUX).pack(anchor="nw", padx=5)

    # ═══════════════════════════════════════════
    # 🎴 CARTES DE TÂCHES
    # ═══════════════════════════════════════════

    def _creer_carte_tache(self, parent, tache, mode="jour"):
        (id_t, titre, desc, matiere, type_t, prio,
         date_t, heure, duree, statut, recur, cours_id) = tache

        type_info = db.TYPES_TACHES.get(type_t, db.TYPES_TACHES["reviser"])
        prio_info = db.PRIORITES.get(prio, db.PRIORITES["normal"])
        coul_mat = db.couleur_matiere(matiere)
        est_faite = statut == "faite"

        fg = VERT_FOND_CORRECTION if est_faite else BLANC

        carte = ctk.CTkFrame(
            parent, fg_color=fg, corner_radius=12,
            border_width=3, border_color=coul_mat)
        carte.pack(fill="x", padx=10, pady=5)

        # ── Ligne 1 : titre + heure ──
        l1 = ctk.CTkFrame(carte, fg_color="transparent")
        l1.pack(fill="x", padx=12, pady=(10, 3))

        # Checkbox
        emoji_check = "✅" if est_faite else "⬜"
        ctk.CTkButton(
            l1, text=emoji_check,
            command=lambda i=id_t, s=statut: self._toggle_statut(i, s),
            fg_color="transparent", hover_color=VERT_FOND_CORRECTION,
            text_color=VERT_EMERAUDE, width=35, height=30,
            font=ctk.CTkFont(size=20)).pack(side="left", padx=(0, 8))

        titre_texte = f"{type_info['emoji']}  {titre}"
        if est_faite:
            titre_texte += "  ✓"
        ctk.CTkLabel(
            l1, text=titre_texte,
            font=ctk.CTkFont(
                size=15,
                weight="bold",
                overstrike=est_faite),
            text_color=GRIS_DOUX if est_faite else GRIS_TEXTE,
            anchor="w").pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            l1, text=f"⏰ {heure} • {duree}min",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=BLEU_ROYAL).pack(side="right")

        # ── Ligne 2 : matière + priorité + récurrence ──
        l2 = ctk.CTkFrame(carte, fg_color="transparent")
        l2.pack(fill="x", padx=12, pady=2)

        ctk.CTkLabel(
            l2, text=f"🎯 {matiere}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=coul_mat).pack(side="left")

        ctk.CTkLabel(
            l2, text=f"  •  {prio_info['emoji']} {prio_info['label']}",
            font=ctk.CTkFont(size=11),
            text_color=prio_info['couleur']).pack(side="left")

        if recur != "aucune":
            ctk.CTkLabel(
                l2, text=f"  •  🔁 {recur}",
                font=ctk.CTkFont(size=10),
                text_color=VIOLET_PREMIUM).pack(side="left")

        # ── Description (si présente) ──
        if desc:
            ctk.CTkLabel(
                carte, text=f"📝 {desc[:120]}",
                font=ctk.CTkFont(size=11),
                text_color=GRIS_TEXTE,
                wraplength=700, justify="left", anchor="w").pack(
                anchor="w", padx=15, pady=(0, 3))

        # ── Boutons actions ──
        l3 = ctk.CTkFrame(carte, fg_color="transparent")
        l3.pack(fill="x", padx=12, pady=(5, 10))

        ctk.CTkButton(
            l3, text="▶️  Pomodoro",
            command=lambda: self._lancer_pomodoro_depuis_tache(matiere),
            fg_color=ORANGE_DORE, hover_color=OR_MODERNE,
            text_color=BLANC, height=30,
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=8).pack(side="left", padx=3, expand=True, fill="x")

        ctk.CTkButton(
            l3, text="✏️  Modifier",
            command=lambda i=id_t: self._ouvrir_form_modif(i),
            fg_color=BLEU_ROYAL, hover_color=BLEU_CIEL,
            text_color=BLANC, height=30,
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=8).pack(side="left", padx=3, expand=True, fill="x")

        ctk.CTkButton(
            l3, text="🗑️  Supprimer",
            command=lambda i=id_t: self._supprimer_tache(i),
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, height=30,
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=8).pack(side="left", padx=3, expand=True, fill="x")

    def _creer_mini_carte_tache(self, parent, tache):
        (id_t, titre, desc, matiere, type_t, prio,
         date_t, heure, duree, statut, recur, cours_id) = tache
        type_info = db.TYPES_TACHES.get(type_t, db.TYPES_TACHES["reviser"])
        coul_mat = db.couleur_matiere(matiere)
        est_faite = statut == "faite"

        fg = VERT_FOND_CORRECTION if est_faite else BLANC
        mini = ctk.CTkFrame(
            parent, fg_color=fg, corner_radius=8,
            border_width=2, border_color=coul_mat)
        mini.pack(fill="x", padx=4, pady=2)

        check = "✅" if est_faite else "⬜"
        ctk.CTkButton(
            mini, text=f"{check} {type_info['emoji']} {titre[:18]}",
            command=lambda i=id_t: self._ouvrir_form_modif(i),
            fg_color="transparent", hover_color=coul_mat,
            text_color=GRIS_TEXTE, anchor="w", height=28,
            font=ctk.CTkFont(size=10, weight="bold"),
            corner_radius=6).pack(fill="x", padx=2, pady=1)

        ctk.CTkLabel(
            mini, text=f"⏰ {heure}",
            font=ctk.CTkFont(size=9),
            text_color=BLEU_ROYAL).pack(pady=(0, 3))

    # ═══════════════════════════════════════════
    # 🎬 ACTIONS
    # ═══════════════════════════════════════════

    def _toggle_statut(self, tache_id, statut_actuel):
        if statut_actuel == "faite":
            db.marquer_tache_a_faire(tache_id)
        else:
            db.marquer_tache_faite(tache_id)
            self._recompenser(5, "Tâche accomplie ! 🎯")
        self.afficher_planificateur()

    def _supprimer_tache(self, tache_id):
        if messagebox.askyesno(
                "🗑️ Supprimer",
                "Supprimer cette tâche ?\n\n⚠️ Action irréversible."):
            db.supprimer_tache(tache_id)
            notification_succes(self, "Supprimée", "🗑️ Tâche supprimée")
            self.afficher_planificateur()

    def _lancer_pomodoro_depuis_tache(self, matiere):
        notification_succes(
            self, "Pomodoro lancé !", f"⏱️ Focus sur {matiere}")
        if hasattr(self, 'afficher_pomodoro'):
            self.afficher_pomodoro()

    # ═══════════════════════════════════════════
    # ➕ FORMULAIRE AJOUT
    # ═══════════════════════════════════════════

    def _ouvrir_form_ajout(self):
        self._ouvrir_form_tache(mode="ajout")

    def _ouvrir_form_modif(self, tache_id):
        self._ouvrir_form_tache(mode="modif", tache_id=tache_id)

    def _ouvrir_form_tache(self, mode="ajout", tache_id=None):
        popup = ctk.CTkToplevel(self)
        titre_popup = "➕ Nouvelle tâche" if mode == "ajout" else "✏️ Modifier tâche"
        popup.title(titre_popup)
        popup.geometry("550x650")
        popup.configure(fg_color=BLANC)
        popup.transient(self)

        # Charger infos si modif
        info = db.info_tache(tache_id) if tache_id else {}

        scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            scroll, text=titre_popup,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=VIOLET_PREMIUM).pack(pady=(0, 12))

        # Titre
        ctk.CTkLabel(scroll, text="📝 Titre de la tâche *",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", pady=(5, 2))
        ent_titre = ctk.CTkEntry(scroll, height=38,
                                 font=ctk.CTkFont(size=13))
        ent_titre.pack(fill="x", pady=(0, 8))
        ent_titre.insert(0, info.get("titre", ""))

        # Description
        ctk.CTkLabel(scroll, text="📄 Description (optionnelle)",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", pady=(5, 2))
        txt_desc = ctk.CTkTextbox(scroll, height=60,
                                  font=ctk.CTkFont(size=12))
        txt_desc.pack(fill="x", pady=(0, 8))
        if info.get("description"):
            txt_desc.insert("0.0", info["description"])

        # Matière
        ctk.CTkLabel(scroll, text="🎯 Matière",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", pady=(5, 2))
        ent_matiere = ctk.CTkEntry(scroll, height=38,
                                   placeholder_text="Ex: Microéconomie")
        ent_matiere.pack(fill="x", pady=(0, 8))
        ent_matiere.insert(0, info.get("matiere", "Général"))

        # Type
        ctk.CTkLabel(scroll, text="📚 Type de tâche",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", pady=(5, 2))
        types_options = [f"{db.TYPES_TACHES[k]['emoji']} {db.TYPES_TACHES[k]['label']}"
                         for k in db.TYPES_TACHES]
        types_keys = list(db.TYPES_TACHES.keys())
        menu_type = ctk.CTkOptionMenu(
            scroll, values=types_options, height=38,
            fg_color=BLEU_CIEL, button_color=BLEU_ROYAL)
        menu_type.pack(fill="x", pady=(0, 8))
        type_actuel = info.get("type_tache", "reviser")
        if type_actuel in types_keys:
            menu_type.set(types_options[types_keys.index(type_actuel)])

        # Priorité
        ctk.CTkLabel(scroll, text="🚨 Priorité",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", pady=(5, 2))
        prio_options = [f"{db.PRIORITES[k]['emoji']} {db.PRIORITES[k]['label']}"
                        for k in db.PRIORITES]
        prio_keys = list(db.PRIORITES.keys())
        menu_prio = ctk.CTkOptionMenu(
            scroll, values=prio_options, height=38,
            fg_color=ORANGE_CLAIR, button_color=ORANGE_DORE)
        menu_prio.pack(fill="x", pady=(0, 8))
        prio_actuelle = info.get("priorite", "normal")
        if prio_actuelle in prio_keys:
            menu_prio.set(prio_options[prio_keys.index(prio_actuelle)])

        # Date
        ctk.CTkLabel(scroll, text="📅 Date (AAAA-MM-JJ)",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", pady=(5, 2))
        ent_date = ctk.CTkEntry(scroll, height=38,
                                placeholder_text="2026-06-15")
        ent_date.pack(fill="x", pady=(0, 8))
        date_def = info.get("date_tache") or self._plan_date.strftime("%Y-%m-%d")
        ent_date.insert(0, date_def)

        # Heure
        l_hd = ctk.CTkFrame(scroll, fg_color="transparent")
        l_hd.pack(fill="x", pady=(5, 2))
        ctk.CTkLabel(l_hd, text="⏰ Heure (HH:MM)",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE).pack(side="left")
        ctk.CTkLabel(l_hd, text="⏱️ Durée (minutes)",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE).pack(side="right", padx=(0, 60))

        l_he = ctk.CTkFrame(scroll, fg_color="transparent")
        l_he.pack(fill="x", pady=(0, 8))
        ent_heure = ctk.CTkEntry(l_he, height=38, width=140,
                                 placeholder_text="14:00")
        ent_heure.pack(side="left")
        ent_heure.insert(0, info.get("heure_debut", "09:00"))
        ent_duree = ctk.CTkEntry(l_he, height=38, width=140,
                                 placeholder_text="30")
        ent_duree.pack(side="right")
        ent_duree.insert(0, str(info.get("duree_minutes", 30)))

        # Récurrence
        ctk.CTkLabel(scroll, text="🔁 Récurrence",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", pady=(5, 2))
        recur_options = ["Aucune", "Quotidienne", "Hebdomadaire", "Mensuelle"]
        recur_map = {"Aucune": "aucune", "Quotidienne": "quotidienne",
                     "Hebdomadaire": "hebdomadaire", "Mensuelle": "mensuelle"}
        menu_recur = ctk.CTkOptionMenu(
            scroll, values=recur_options, height=38,
            fg_color=VIOLET_LAVANDE, button_color=VIOLET_PREMIUM)
        menu_recur.pack(fill="x", pady=(0, 12))
        if mode == "modif":
            menu_recur.configure(state="disabled")

        # Boutons valider/annuler
        btns = ctk.CTkFrame(scroll, fg_color="transparent")
        btns.pack(fill="x", pady=10)

        def valider():
            titre = ent_titre.get().strip()
            if not titre:
                messagebox.showwarning("⚠️", "Titre obligatoire !")
                return
            date_v = ent_date.get().strip()
            try:
                datetime.strptime(date_v, "%Y-%m-%d")
            except Exception:
                messagebox.showwarning("⚠️", "Format date : AAAA-MM-JJ")
                return
            heure_v = ent_heure.get().strip() or "09:00"
            try:
                duree_v = int(ent_duree.get().strip() or "30")
            except Exception:
                duree_v = 30

            type_v = types_keys[types_options.index(menu_type.get())]
            prio_v = prio_keys[prio_options.index(menu_prio.get())]
            recur_v = recur_map[menu_recur.get()]
            desc_v = txt_desc.get("0.0", "end").strip()
            matiere_v = ent_matiere.get().strip() or "Général"

            if mode == "ajout":
                db.ajouter_tache(
                    titre=titre, date_tache=date_v,
                    heure_debut=heure_v, duree_minutes=duree_v,
                    matiere=matiere_v, type_tache=type_v,
                    priorite=prio_v, description=desc_v,
                    recurrence=recur_v)
                notification_succes(self, "Tâche ajoutée !",
                                    f"📅 {titre[:30]}")
                self._recompenser(3, "Tâche planifiée ! 📅")
            else:
                db.modifier_tache(
                    tache_id, titre=titre, description=desc_v,
                    matiere=matiere_v, type_tache=type_v,
                    priorite=prio_v, date_tache=date_v,
                    heure_debut=heure_v, duree_minutes=duree_v)
                notification_succes(self, "Modifiée !",
                                    f"✏️ {titre[:30]}")
            popup.destroy()
            self.afficher_planificateur()

        ctk.CTkButton(
            btns, text="✅  Valider", command=valider,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10).pack(
            side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            btns, text="❌  Annuler", command=popup.destroy,
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10).pack(
            side="left", padx=5, expand=True, fill="x")

    # ═══════════════════════════════════════════
    # 🤖 GÉNÉRATEUR IA
    # ═══════════════════════════════════════════

    def _ouvrir_generateur_ia(self):
        popup = ctk.CTkToplevel(self)
        popup.title("🤖 Générateur IA de planning")
        popup.geometry("500x450")
        popup.configure(fg_color=BLANC)
        popup.transient(self)

        ctk.CTkLabel(
            popup, text="🤖  Générateur IA de Planning",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=VIOLET_PREMIUM).pack(pady=15)

        ctk.CTkLabel(
            popup,
            text="💡 Décris tes objectifs et l'IA créera\n"
                 "un planning de révision optimal !",
            font=ctk.CTkFont(size=12),
            text_color=GRIS_TEXTE, justify="center").pack(pady=(0, 10))

        ctk.CTkLabel(popup, text="📝 Décris ta situation :",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE,
                     anchor="w").pack(fill="x", padx=20, pady=(5, 2))

        txt_demande = ctk.CTkTextbox(popup, height=120,
                                     font=ctk.CTkFont(size=12))
        txt_demande.pack(fill="x", padx=20, pady=(0, 10))
        txt_demande.insert(
            "0.0",
            "Ex: J'ai 3 examens dans 2 semaines : Microéco, "
            "Compta et Droit. Aide-moi à réviser 2h par jour.")

        info_label = ctk.CTkLabel(
            popup,
            text="🚧 Fonctionnalité avancée à venir !\n\n"
                 "Pour l'instant, ajoute tes tâches manuellement\n"
                 "avec le bouton ➕ Nouvelle tâche.",
            font=ctk.CTkFont(size=12),
            text_color=ORANGE_DORE, justify="center")
        info_label.pack(pady=15)

        ctk.CTkButton(
            popup, text="✅  Compris", command=popup.destroy,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10).pack(pady=10, padx=20, fill="x")