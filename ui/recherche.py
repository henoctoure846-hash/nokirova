# ui/recherche.py - Recherche dans les cours NOKIROVA 🌸

import customtkinter as ctk
from tkinter import messagebox
import re
import database as db
from ui.base import (VERT_EMERAUDE, VERT_HOVER, VERT_CLAIR, VERT_CORRECTION,
                     VERT_FOND_CORRECTION,
                     BLEU_ROYAL, BLEU_CIEL, BLEU_TRES_PALE,
                     VIOLET_PREMIUM,
                     ROUGE,
                     BLANC, GRIS_TEXTE, GRIS_DOUX)
from notifications import notification_succes


class RechercheMixin:

    # ═══════════════════════════════════════════
    # 🔍 RECHERCHE DANS LES COURS
    # ═══════════════════════════════════════════

    def afficher_recherche(self):
        self.vider_zone()
        self.afficher_titre("Recherche dans les cours", "🔍", VERT_EMERAUDE)

        # ── Info ──
        info = ctk.CTkFrame(
            self.zone_principale,
            fg_color=VERT_FOND_CORRECTION, corner_radius=12)
        info.pack(fill="x", pady=5)
        ctk.CTkLabel(
            info,
            text="🔍 Cherche un mot ou une phrase dans TOUS tes cours !\n"
                 "💡 Astuce : Ctrl+K pour ouvrir cette page rapidement",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=VERT_CORRECTION,
            justify="center").pack(pady=12)

        # ── Barre de recherche ──
        frame_search = ctk.CTkFrame(
            self.zone_principale,
            fg_color=VERT_CLAIR, corner_radius=14)
        frame_search.pack(fill="x", pady=10)

        ctk.CTkLabel(frame_search, text="🔎  Mot-clé :",
                     text_color=BLANC,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(
            side="left", padx=15, pady=15)

        self.entry_recherche = ctk.CTkEntry(
            frame_search, height=42,
            fg_color=BLANC, text_color=GRIS_TEXTE,
            placeholder_text="Ex: élasticité, microéconomie...",
            font=ctk.CTkFont(size=14), corner_radius=10,
            border_width=0)
        self.entry_recherche.pack(
            side="left", padx=10, pady=15, fill="x", expand=True)
        self.entry_recherche.bind(
            "<Return>", lambda e: self._lancer_recherche())

        ctk.CTkButton(
            frame_search, text="🔍  Chercher",
            command=self._lancer_recherche,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, corner_radius=10,
            height=42, width=130,
            font=ctk.CTkFont(size=13, weight="bold")).pack(
            side="left", padx=15, pady=15)

        # ── Filtre matière ──
        frame_filtre = ctk.CTkFrame(
            self.zone_principale,
            fg_color=BLEU_TRES_PALE, corner_radius=12)
        frame_filtre.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_filtre,
                     text="🎯  Filtrer par matière :",
                     text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=13, weight="bold")).pack(
            side="left", padx=15, pady=10)

        matieres = ["Toutes"] + db.lister_matieres_uniques()
        self._matiere_recherche = "Toutes"

        self.menu_matiere_recherche = ctk.CTkOptionMenu(
            frame_filtre, values=matieres,
            command=lambda v: setattr(self, '_matiere_recherche', v),
            fg_color=BLEU_ROYAL, text_color=BLANC,
            button_color=BLEU_CIEL, corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold"))
        self.menu_matiere_recherche.set("Toutes")
        self.menu_matiere_recherche.pack(side="left", padx=10, pady=10)

        # ── Zone résultats ──
        self.frame_resultats_recherche = ctk.CTkScrollableFrame(
            self.zone_principale, fg_color=BLANC,
            corner_radius=15, border_width=2, border_color=VERT_CLAIR)
        self.frame_resultats_recherche.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(
            self.frame_resultats_recherche,
            text="🔍  Tape un mot-clé ci-dessus et appuie sur Entrée !\n\n"
                 "💡 La recherche fouille dans TOUS tes cours importés.",
            font=ctk.CTkFont(size=14),
            text_color=GRIS_DOUX,
            justify="center").pack(pady=50)

    def _lancer_recherche(self):
        mot_cle = self.entry_recherche.get().strip()
        if not mot_cle or len(mot_cle) < 2:
            messagebox.showwarning("⚠️", "Tape au moins 2 caractères !")
            return

        # Vider résultats
        for widget in self.frame_resultats_recherche.winfo_children():
            widget.destroy()

        # Récupérer cours
        cours_list = db.lister_cours()
        if self._matiere_recherche != "Toutes":
            cours_list = db.filtrer_cours_par_matiere(self._matiere_recherche)

        if not cours_list:
            ctk.CTkLabel(
                self.frame_resultats_recherche,
                text="📭  Aucun cours dans la bibliothèque !\n\n"
                     "💡 Importe un cours d'abord.",
                font=ctk.CTkFont(size=14),
                text_color=GRIS_DOUX, justify="center").pack(pady=50)
            return

        # Chercher dans chaque cours
        resultats = []
        for cours in cours_list:
            id_cours, nom, matiere, date_import = cours
            info = db.info_cours(id_cours)
            if not info:
                continue
            contenu = info["contenu"] or ""
            if mot_cle.lower() in contenu.lower():
                positions = [
                    m.start() for m in re.finditer(
                        re.escape(mot_cle), contenu, re.IGNORECASE)]
                resultats.append({
                    "id": id_cours,
                    "nom": nom,
                    "matiere": matiere,
                    "contenu": contenu,
                    "positions": positions,
                    "nb_occurrences": len(positions)
                })

        # Afficher résultats
        if not resultats:
            ctk.CTkLabel(
                self.frame_resultats_recherche,
                text=f"❌  Aucun résultat pour '{mot_cle}'\n\n"
                     f"💡 Essaie un autre mot-clé !",
                font=ctk.CTkFont(size=14),
                text_color=ROUGE, justify="center").pack(pady=50)
            return

        # En-tête
        total_occ = sum(r["nb_occurrences"] for r in resultats)
        ctk.CTkLabel(
            self.frame_resultats_recherche,
            text=f"✅ {len(resultats)} cours trouvé(s)  •  "
                 f"{total_occ} occurrence(s) au total",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=VERT_CORRECTION).pack(pady=(10, 15))

        for res in resultats:
            self._creer_carte_resultat(res, mot_cle)

    def _creer_carte_resultat(self, res, mot_cle):
        carte = ctk.CTkFrame(
            self.frame_resultats_recherche,
            fg_color=VERT_FOND_CORRECTION,
            corner_radius=14, border_width=2, border_color=VERT_CLAIR)
        carte.pack(fill="x", padx=10, pady=6)

        # Header
        ligne1 = ctk.CTkFrame(carte, fg_color="transparent")
        ligne1.pack(fill="x", padx=15, pady=(12, 3))

        ctk.CTkLabel(ligne1, text=f"📄  {res['nom'][:50]}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=GRIS_TEXTE).pack(side="left")

        ctk.CTkLabel(ligne1,
                     text=f"🔍 {res['nb_occurrences']} occurrence(s)",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=VERT_CORRECTION).pack(side="right")

        ctk.CTkLabel(carte, text=f"🎯 {res['matiere']}",
                     font=ctk.CTkFont(size=11),
                     text_color=VIOLET_PREMIUM,
                     anchor="w").pack(anchor="w", padx=15, pady=(0, 5))

        # Aperçus (3 premiers contextes)
        for pos in res["positions"][:3]:
            debut = max(0, pos - 80)
            fin = min(len(res["contenu"]), pos + len(mot_cle) + 80)
            extrait = res["contenu"][debut:fin].replace('\n', ' ').strip()
            extrait = re.sub(r'\s+', ' ', extrait)
            extrait_surligne = self._surligner_mot_recherche(extrait, mot_cle)
            prefix = "..." if debut > 0 else ""
            suffix = "..." if fin < len(res["contenu"]) else ""

            ctk.CTkLabel(
                carte,
                text=f"{prefix}{extrait_surligne}{suffix}",
                font=ctk.CTkFont(size=11),
                text_color=GRIS_TEXTE,
                wraplength=750, justify="left", anchor="w").pack(
                anchor="w", padx=20, pady=2)

        if res["nb_occurrences"] > 3:
            ctk.CTkLabel(
                carte,
                text=f"+ {res['nb_occurrences'] - 3} autres occurrences...",
                font=ctk.CTkFont(size=10, slant="italic"),
                text_color=GRIS_DOUX).pack(anchor="w", padx=20, pady=2)

        # Bouton charger
        ctk.CTkButton(
            carte, text="📂  Charger ce cours",
            command=lambda r=res: self._charger_resultat_recherche(
                r["id"], r["nom"], r["matiere"]),
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, corner_radius=10, height=32,
            font=ctk.CTkFont(size=12, weight="bold")).pack(
            fill="x", padx=15, pady=(8, 12))

    def _charger_resultat_recherche(self, id_cours, nom, matiere):
        info = db.info_cours(id_cours)
        if info:
            self.cours_actuel = info["contenu"]
            self.nom_cours = info["nom"]
            self.matiere_detectee = info["matiere"]
            self.id_cours_actif = id_cours
            self.statut_label.configure(text=f"{matiere}\n{nom[:25]}")
            notification_succes(self, "Cours chargé !", f"📚 {nom[:30]}")