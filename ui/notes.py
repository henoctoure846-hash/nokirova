# ui/notes.py - Notes personnelles NOKIROVA 🌸

import customtkinter as ctk
from tkinter import messagebox
import database as db
from ui.base import (VERT_EMERAUDE, VERT_HOVER,
                     VIOLET_PREMIUM, VIOLET_LAVANDE, VIOLET_CLAIR, VIOLET_PALE,
                     ROSE_SAKURA, ROSE_CLAIR, ROSE_PALE,
                     BLANC, GRIS_TEXTE, GRIS_DOUX,
                     ROUGE, ROUGE_CLAIR,
                     OR_MODERNE, ORANGE_CLAIR)
from notifications import notification_succes
from export_pdf import exporter_en_pdf


class NotesMixin:

    # ═══════════════════════════════════════════
    # ✍️ NOTES PERSONNELLES
    # ═══════════════════════════════════════════

    def afficher_notes(self):
        self.vider_zone()
        self.afficher_titre("Mes Notes Personnelles", "✍️", VIOLET_LAVANDE)

        nb_notes = db.compter_notes()
        matieres_notes = db.lister_matieres_notes()

        # ── Stats ──
        carte_stats = ctk.CTkFrame(
            self.zone_principale,
            fg_color=ROSE_PALE, corner_radius=15, height=70)
        carte_stats.pack(fill="x", pady=(0, 10))
        carte_stats.pack_propagate(False)
        ctk.CTkLabel(carte_stats,
                     text=f"✍️ {nb_notes} note(s) enregistrée(s)",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=VIOLET_PREMIUM).pack(pady=22)

        # ── Contrôles ──
        frame_ctrl = ctk.CTkFrame(
            self.zone_principale,
            fg_color=ROSE_CLAIR, corner_radius=12)
        frame_ctrl.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_ctrl, text="🔍  Filtrer :",
                     text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=13, weight="bold")).pack(
            side="left", padx=15, pady=10)

        valeurs_filtre = ["Toutes"] + matieres_notes
        self.menu_filtre_notes = ctk.CTkOptionMenu(
            frame_ctrl, values=valeurs_filtre,
            command=self._filtrer_notes,
            fg_color=VIOLET_LAVANDE, text_color=BLANC,
            button_color=VIOLET_CLAIR, corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold"))
        self.menu_filtre_notes.set(self.filtre_notes)
        self.menu_filtre_notes.pack(side="left", padx=10, pady=10)

        self.entry_recherche_notes = ctk.CTkEntry(
            frame_ctrl,
            placeholder_text="🔎 Rechercher...",
            fg_color=BLANC, text_color=GRIS_TEXTE,
            font=ctk.CTkFont(size=12), corner_radius=10,
            width=180, height=32, border_color=VIOLET_PALE)
        self.entry_recherche_notes.pack(side="left", padx=10, pady=10)
        self.entry_recherche_notes.bind(
            "<Return>", lambda e: self._rechercher_notes())

        ctk.CTkButton(frame_ctrl, text="🔎",
                      command=self._rechercher_notes,
                      fg_color=VIOLET_PREMIUM, text_color=BLANC,
                      hover_color=VIOLET_LAVANDE,
                      corner_radius=10, height=32, width=40,
                      font=ctk.CTkFont(size=13)).pack(
            side="left", padx=2, pady=10)

        ctk.CTkButton(frame_ctrl, text="➕  Nouvelle note",
                      command=self._nouvelle_note,
                      fg_color=VERT_EMERAUDE, text_color=BLANC,
                      hover_color=VERT_HOVER,
                      corner_radius=10, height=32,
                      font=ctk.CTkFont(size=12, weight="bold")).pack(
            side="right", padx=15, pady=10)

        # ── Liste ──
        self.frame_liste_notes = ctk.CTkScrollableFrame(
            self.zone_principale, fg_color=BLANC,
            corner_radius=15, border_width=2,
            border_color=ROSE_SAKURA)
        self.frame_liste_notes.pack(fill="both", expand=True, pady=10)

        self._afficher_liste_notes()

    def _filtrer_notes(self, valeur):
        self.filtre_notes = valeur
        self._afficher_liste_notes()

    def _rechercher_notes(self):
        mot = self.entry_recherche_notes.get().strip()
        for widget in self.frame_liste_notes.winfo_children():
            widget.destroy()

        notes = db.rechercher_notes(mot) if mot else db.lister_notes(self.filtre_notes)

        if not notes:
            ctk.CTkLabel(
                self.frame_liste_notes,
                text=f"🔎 Aucune note trouvée pour '{mot}'\n\n"
                     f"💡 Essaie un autre mot-clé !",
                font=ctk.CTkFont(size=14),
                text_color=GRIS_DOUX, justify="center").pack(pady=50)
            return

        for note in notes:
            self._creer_carte_note(*note)

    def _afficher_liste_notes(self):
        for widget in self.frame_liste_notes.winfo_children():
            widget.destroy()

        notes = db.lister_notes(
            None if self.filtre_notes == "Toutes" else self.filtre_notes)

        if not notes:
            ctk.CTkLabel(
                self.frame_liste_notes,
                text="📭  Aucune note pour le moment\n\n"
                     "💡 Clique sur '➕ Nouvelle note' pour commencer !\n"
                     "✍️ Prends des notes sur tes cours, tes idées... 🌸",
                font=ctk.CTkFont(size=14),
                text_color=GRIS_DOUX, justify="center").pack(pady=50)
            return

        for note in notes:
            self._creer_carte_note(*note)

    def _creer_carte_note(self, id_n, titre, contenu,
                          matiere, couleur, date_creation, date_modif):
        carte = ctk.CTkFrame(
            self.frame_liste_notes, fg_color=couleur,
            corner_radius=16, border_width=2,
            border_color=ROSE_SAKURA)
        carte.pack(fill="x", padx=10, pady=6)

        # Ligne 1
        ligne1 = ctk.CTkFrame(carte, fg_color="transparent")
        ligne1.pack(fill="x", padx=15, pady=(12, 3))

        ctk.CTkLabel(ligne1, text=f"✍️  {titre[:50]}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=GRIS_TEXTE).pack(side="left")

        date_simple = date_modif.split('.')[0] if date_modif else "—"
        ctk.CTkLabel(ligne1, text=f"📅 {date_simple}",
                     font=ctk.CTkFont(size=11),
                     text_color=GRIS_DOUX).pack(side="right")

        ctk.CTkLabel(carte, text=f"🎯 {matiere}",
                     font=ctk.CTkFont(size=11),
                     text_color=VIOLET_PREMIUM,
                     anchor="w").pack(anchor="w", padx=15, pady=(0, 3))

        apercu = (contenu or "")[:100] + (
            "..." if len(contenu or "") > 100 else "")
        ctk.CTkLabel(carte, text=apercu,
                     font=ctk.CTkFont(size=12),
                     text_color=GRIS_TEXTE, wraplength=750,
                     justify="left", anchor="w").pack(
            anchor="w", padx=15, pady=(0, 8))

        # Boutons
        ligne_btns = ctk.CTkFrame(carte, fg_color="transparent")
        ligne_btns.pack(fill="x", padx=15, pady=(0, 12))

        ctk.CTkButton(ligne_btns, text="✏️  Modifier",
                      command=lambda i=id_n: self._modifier_note(i),
                      fg_color=VIOLET_PREMIUM,
                      hover_color=VIOLET_LAVANDE,
                      text_color=BLANC, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="left", padx=2, expand=True, fill="x")

        ctk.CTkButton(ligne_btns, text="💾  PDF",
                      command=lambda t=titre, c=contenu:
                      self._exporter_note_pdf(t, c),
                      fg_color=OR_MODERNE,
                      hover_color=ORANGE_CLAIR,
                      text_color=BLANC, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="left", padx=2, expand=True, fill="x")

        ctk.CTkButton(ligne_btns, text="🗑️  Supprimer",
                      command=lambda i=id_n, t=titre:
                      self._supprimer_note(i, t),
                      fg_color=ROUGE, hover_color=ROUGE_CLAIR,
                      text_color=BLANC, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="left", padx=2, expand=True, fill="x")

    def _nouvelle_note(self):
        self._ouvrir_editeur_note(None)

    def _modifier_note(self, id_note):
        self._ouvrir_editeur_note(id_note)

    def _ouvrir_editeur_note(self, id_note=None):
        self.vider_zone()
        note_existante = db.info_note(id_note) if id_note else None
        titre_page = "Modifier la note" if note_existante else "Nouvelle note"
        self.afficher_titre(titre_page, "✍️", VIOLET_LAVANDE)

        # Titre
        ctk.CTkLabel(self.zone_principale,
                     text="📌  Titre de la note :",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=GRIS_TEXTE).pack(anchor="w", pady=(5, 3))

        self.entry_titre_note = ctk.CTkEntry(
            self.zone_principale, height=44,
            fg_color=BLANC, text_color=GRIS_TEXTE,
            placeholder_text="Ex: Chapitre 3 - Elasticité...",
            font=ctk.CTkFont(size=14), corner_radius=12,
            border_width=2, border_color=VIOLET_PALE)
        self.entry_titre_note.pack(fill="x", pady=(0, 10))

        if note_existante:
            self.entry_titre_note.insert(0, note_existante["titre"])

        # Matière + Couleur
        frame_meta = ctk.CTkFrame(self.zone_principale, fg_color="transparent")
        frame_meta.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_meta, text="🎯  Matière :",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=GRIS_TEXTE).pack(side="left", padx=(0, 10))

        matieres_dispo = db.lister_matieres_uniques() or ["Général"]
        if "Général" not in matieres_dispo:
            matieres_dispo = ["Général"] + matieres_dispo

        self.menu_matiere_note = ctk.CTkOptionMenu(
            frame_meta, values=matieres_dispo,
            fg_color=VIOLET_LAVANDE, text_color=BLANC,
            button_color=VIOLET_CLAIR, corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold"))
        self.menu_matiere_note.set(
            note_existante["matiere"]
            if note_existante and note_existante["matiere"] in matieres_dispo
            else "Général")
        self.menu_matiere_note.pack(side="left", padx=5)

        ctk.CTkLabel(frame_meta, text="🎨  Couleur :",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=GRIS_TEXTE).pack(side="left", padx=(20, 10))

        COULEURS_NOTES = {
            "🟡 Jaune": "#FFE66D",
            "🟢 Vert": "#E8F5E9",
            "🔵 Bleu": "#D0EBFF",
            "🩷 Rose": "#FFE5EF",
            "🟣 Violet": "#D8B4FE",
            "🟠 Orange": "#FDBA74"}

        self._couleur_note_choisie = (
            note_existante["couleur"] if note_existante else "#FFE66D")

        self.menu_couleur_note = ctk.CTkOptionMenu(
            frame_meta,
            values=list(COULEURS_NOTES.keys()),
            command=lambda v: self._choisir_couleur_note(v, COULEURS_NOTES),
            fg_color=VIOLET_LAVANDE, text_color=BLANC,
            button_color=VIOLET_CLAIR, corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold"))

        label_couleur = next(
            (k for k, v in COULEURS_NOTES.items()
             if v == self._couleur_note_choisie), "🟡 Jaune")
        self.menu_couleur_note.set(label_couleur)
        self.menu_couleur_note.pack(side="left", padx=5)

        # Contenu
        ctk.CTkLabel(self.zone_principale,
                     text="📝  Contenu de la note :",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=GRIS_TEXTE).pack(anchor="w", pady=(10, 3))

        cadre_contenu = ctk.CTkFrame(
            self.zone_principale, fg_color=BLANC,
            corner_radius=15, border_width=2, border_color=VIOLET_PALE)
        cadre_contenu.pack(fill="both", expand=True, pady=5)

        self.zone_contenu_note = ctk.CTkTextbox(
            cadre_contenu, fg_color=BLANC, text_color=GRIS_TEXTE,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=12, border_width=0, wrap="word")
        self.zone_contenu_note.pack(
            fill="both", expand=True, padx=10, pady=10)

        if note_existante:
            self.zone_contenu_note.insert("0.0", note_existante["contenu"] or "")
        elif self.cours_actuel:
            self.zone_contenu_note.insert(
                "0.0",
                f"📚 Cours : {self.nom_cours}\n\n✍️ Mes notes :\n\n")

        # Boutons
        frame_btns = ctk.CTkFrame(self.zone_principale, fg_color="transparent")
        frame_btns.pack(fill="x", pady=10)

        ctk.CTkButton(frame_btns, text="❌  Annuler",
                      command=self.afficher_notes,
                      fg_color=GRIS_DOUX, hover_color=ROUGE_CLAIR,
                      text_color=BLANC, corner_radius=14,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      height=48).pack(
            side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(frame_btns, text="💾  Sauvegarder",
                      command=lambda: self._sauvegarder_note(id_note),
                      fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
                      text_color=BLANC, corner_radius=14,
                      font=ctk.CTkFont(size=15, weight="bold"),
                      height=48).pack(
            side="left", padx=5, expand=True, fill="x")

    def _choisir_couleur_note(self, label, couleurs_map):
        self._couleur_note_choisie = couleurs_map.get(label, "#FFE66D")

    def _sauvegarder_note(self, id_note=None):
        titre = self.entry_titre_note.get().strip()
        contenu = self.zone_contenu_note.get("0.0", "end").strip()
        matiere = self.menu_matiere_note.get()
        couleur = getattr(self, '_couleur_note_choisie', "#FFE66D")

        if not titre:
            messagebox.showwarning("⚠️", "Donne un titre à ta note !")
            return

        if id_note:
            db.modifier_note(id_note, titre, contenu, matiere, couleur)
            notification_succes(self, "Note modifiée !", f"✏️ {titre[:30]}")
        else:
            db.creer_note(titre, contenu, matiere, couleur)
            notification_succes(self, "Note créée !", f"✍️ {titre[:30]}")
            self._recompenser(3, "Note créée ! ✍️")

        self.afficher_notes()

    def _supprimer_note(self, id_note, titre):
        if messagebox.askyesno(
                "🗑️ Supprimer la note ?",
                f"Supprimer :\n\n✍️ {titre}\n\n⚠️ Action irréversible !"):
            db.supprimer_note(id_note)
            notification_succes(self, "Supprimée !", f"🗑️ {titre[:30]}")
            self._afficher_liste_notes()

    def _exporter_note_pdf(self, titre, contenu):
        if not contenu:
            messagebox.showwarning("⚠️", "La note est vide !")
            return

        from datetime import datetime
        date_simple = datetime.now().strftime('%d-%m-%Y')
        nom_fichier = (f"NOKIROVA_Note_"
                       f"{titre[:20].replace(' ', '_')}_{date_simple}.pdf")
        resultat = exporter_en_pdf(contenu, f"Note : {titre}", nom_fichier)

        if "Erreur" not in resultat and "❌" not in resultat:
            notification_succes(self, "PDF exporté !", f"📄 {titre[:20]}")
            messagebox.showinfo(
                "✅ PDF créé",
                f"📄 {nom_fichier}\n\n📁 {resultat}")
        else:
            messagebox.showerror("❌ Erreur", resultat)