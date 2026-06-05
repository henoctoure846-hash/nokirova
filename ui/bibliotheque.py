# ui/bibliotheque.py - Bibliothèque de cours NOKIROVA 🌸

import customtkinter as ctk
from tkinter import simpledialog, messagebox
import database as db
from ui.base import (VERT_EMERAUDE, VERT_HOVER, VERT_CLAIR, VERT_FOND_CORRECTION,
                     BLEU_ROYAL, BLEU_CIEL, VIOLET_PREMIUM, VIOLET_LAVANDE,
                     ROSE_PALE,
                     BLANC, GRIS_TEXTE, GRIS_DOUX, GRIS_PERLE,
                     ROUGE, ROUGE_CLAIR, OR_MODERNE, ORANGE_CLAIR)
from notifications import notification_succes


class BibliotequeMixin:

    # ═══════════════════════════════════════════
    # 📚 BIBLIOTHÈQUE
    # ═══════════════════════════════════════════

    def afficher_bibliotheque(self):
        self.vider_zone()
        self.afficher_titre("Bibliothèque de cours", "📚", VERT_EMERAUDE)

        nb_cours = db.compter_cours()
        matieres = db.lister_matieres_uniques()

        # ── Stats ──
        carte_stats = ctk.CTkFrame(self.zone_principale,
                                   fg_color=VERT_CLAIR, corner_radius=15, height=70)
        carte_stats.pack(fill="x", pady=(0, 10))
        carte_stats.pack_propagate(False)
        ctk.CTkLabel(carte_stats,
                     text=f"📚 {nb_cours} cours  •  🎯 {len(matieres)} matière(s) différentes",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=BLANC).pack(pady=22)

        # ── Bouton Import partage ──
        cadre_import = ctk.CTkFrame(
            self.zone_principale, fg_color=VIOLET_PALE_HEX(),
            corner_radius=12)
        cadre_import.pack(fill="x", pady=5)
        ctk.CTkButton(
            cadre_import,
            text="📥  Importer un cours partagé (.nokirova)",
            command=self.afficher_import_partage,
            fg_color=VIOLET_PREMIUM, hover_color=VIOLET_LAVANDE,
            text_color=BLANC, corner_radius=10, height=40,
            font=ctk.CTkFont(size=13, weight="bold")).pack(
            fill="x", padx=10, pady=10)

        # ── Filtres ──
        frame_filtre = ctk.CTkFrame(self.zone_principale,
                                    fg_color=VERT_FOND_CORRECTION, corner_radius=12)
        frame_filtre.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_filtre, text="🔍  Filtrer :",
                     text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=13, weight="bold")).pack(
            side="left", padx=15, pady=10)

        valeurs_filtre = ["Toutes"] + matieres if matieres else ["Toutes"]
        self.menu_filtre = ctk.CTkOptionMenu(
            frame_filtre, values=valeurs_filtre,
            command=self._filtrer_bibliotheque,
            fg_color=VERT_EMERAUDE, text_color=BLANC,
            button_color=VERT_HOVER, corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold"))
        self.menu_filtre.set(self.filtre_matiere)
        self.menu_filtre.pack(side="left", padx=10, pady=10)

        ctk.CTkButton(frame_filtre, text="🔄  Actualiser",
                      command=self.afficher_bibliotheque,
                      fg_color=BLEU_ROYAL, text_color=BLANC,
                      hover_color=BLEU_CIEL, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="right", padx=15, pady=10)

        # ── Liste ──
        self.liste_cours_frame = ctk.CTkScrollableFrame(
            self.zone_principale, fg_color=BLANC,
            corner_radius=15, border_width=2, border_color=VERT_CLAIR)
        self.liste_cours_frame.pack(fill="both", expand=True, pady=10)

        self._afficher_liste_cours()

    def _filtrer_bibliotheque(self, valeur):
        self.filtre_matiere = valeur
        self._afficher_liste_cours()

    def _afficher_liste_cours(self):
        for widget in self.liste_cours_frame.winfo_children():
            widget.destroy()

        cours_list = (db.lister_cours() if self.filtre_matiere == "Toutes"
                      else db.filtrer_cours_par_matiere(self.filtre_matiere))

        if not cours_list:
            ctk.CTkLabel(self.liste_cours_frame,
                         text="📭  Aucun cours pour le moment\n\n"
                              "💡 Importe ton premier cours via '📥 Importer un cours'",
                         font=ctk.CTkFont(size=14),
                         text_color=GRIS_DOUX, justify="center").pack(pady=50)
            return

        for cours in cours_list:
            id_cours, nom, matiere, date_import = cours
            self._creer_carte_cours(id_cours, nom, matiere, date_import)

    def _creer_carte_cours(self, id_cours, nom, matiere, date_import):
        actif = (id_cours == self.id_cours_actif)

        carte = ctk.CTkFrame(self.liste_cours_frame,
                             fg_color=VERT_FOND_CORRECTION if actif else GRIS_PERLE,
                             corner_radius=14,
                             border_width=2 if actif else 1,
                             border_color=VERT_EMERAUDE if actif else VERT_CLAIR)
        carte.pack(fill="x", padx=10, pady=6)

        # Ligne 1
        ligne1 = ctk.CTkFrame(carte, fg_color="transparent")
        ligne1.pack(fill="x", padx=15, pady=(12, 5))

        emoji_actif = "✅ " if actif else ""
        ctk.CTkLabel(ligne1,
                     text=f"{emoji_actif}📄  {nom[:50]}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=GRIS_TEXTE, anchor="w").pack(
            side="left", fill="x", expand=True)

        # Ligne 2
        ligne2 = ctk.CTkFrame(carte, fg_color="transparent")
        ligne2.pack(fill="x", padx=15, pady=(0, 5))

        ctk.CTkLabel(ligne2, text=f"🎯 {matiere}",
                     font=ctk.CTkFont(size=11),
                     text_color=VIOLET_PREMIUM, anchor="w").pack(side="left")

        date_simple = date_import.split('.')[0] if date_import else "—"
        ctk.CTkLabel(ligne2, text=f"📅 {date_simple}",
                     font=ctk.CTkFont(size=11),
                     text_color=GRIS_DOUX, anchor="e").pack(side="right")

        # Ligne 3 - Boutons (4 maintenant avec Partager)
        ligne3 = ctk.CTkFrame(carte, fg_color="transparent")
        ligne3.pack(fill="x", padx=15, pady=(5, 12))

        ctk.CTkButton(ligne3, text="📂  Charger",
                      command=lambda i=id_cours, n=nom, m=matiere:
                      self._charger_cours_biblio(i, n, m),
                      fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
                      text_color=BLANC, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="left", padx=2, expand=True, fill="x")

        ctk.CTkButton(ligne3, text="🤝  Partager",
                      command=lambda i=id_cours:
                      self._exporter_cours_nokirova(i),
                      fg_color=VIOLET_PREMIUM, hover_color=VIOLET_LAVANDE,
                      text_color=BLANC, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="left", padx=2, expand=True, fill="x")

        ctk.CTkButton(ligne3, text="✏️  Renommer",
                      command=lambda i=id_cours, n=nom:
                      self._renommer_cours(i, n),
                      fg_color=BLEU_ROYAL, hover_color=BLEU_CIEL,
                      text_color=BLANC, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="left", padx=2, expand=True, fill="x")

        ctk.CTkButton(ligne3, text="🗑️  Supprimer",
                      command=lambda i=id_cours, n=nom:
                      self._supprimer_cours(i, n),
                      fg_color=ROUGE, hover_color=ROUGE_CLAIR,
                      text_color=BLANC, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="left", padx=2, expand=True, fill="x")

    def _charger_cours_biblio(self, id_cours, nom, matiere):
        info = db.info_cours(id_cours)
        if info:
            self.cours_actuel = info["contenu"]
            self.nom_cours = info["nom"]
            self.matiere_detectee = info["matiere"]
            self.id_cours_actif = id_cours
            self.statut_label.configure(text=f"{matiere}\n{nom[:25]}")
            notification_succes(self, "Cours chargé !", f"📚 {nom[:30]}")
            self._afficher_liste_cours()

    def _renommer_cours(self, id_cours, ancien_nom):
        nouveau_nom = simpledialog.askstring(
            "✏️ Renommer le cours",
            f"Nouveau nom pour :\n{ancien_nom}\n",
            initialvalue=ancien_nom, parent=self)
        if nouveau_nom and nouveau_nom.strip():
            db.renommer_cours(id_cours, nouveau_nom.strip())
            notification_succes(self, "Renommé !", f"✏️ {nouveau_nom[:30]}")
            self._afficher_liste_cours()

    def _supprimer_cours(self, id_cours, nom):
        if messagebox.askyesno(
                "🗑️ Supprimer le cours ?",
                f"Es-tu sûr de vouloir supprimer :\n\n📄 {nom}\n\n"
                f"⚠️ Cette action est irréversible !"):
            db.supprimer_cours(id_cours)
            if self.id_cours_actif == id_cours:
                self.cours_actuel = ""
                self.nom_cours = "Aucun cours chargé"
                self.id_cours_actif = None
                self.statut_label.configure(text="Aucun cours chargé")
            notification_succes(self, "Supprimé !", f"🗑️ {nom[:30]}")
            self.afficher_bibliotheque()


def VIOLET_PALE_HEX():
    """Couleur violet pâle pour le cadre import"""
    return "#D8B4FE"