# ui/historique.py - Historique NOKIROVA 🌸

import customtkinter as ctk
from tkinter import messagebox
import database as db
from ui.base import (ORANGE_DORE, ORANGE_CLAIR, ORANGE_PALE, OR_MODERNE,
                     VIOLET_PREMIUM, VIOLET_LAVANDE,
                     JAUNE_PALE, BLEU_ROYAL, BLEU_CIEL,
                     VERT_EMERAUDE, VERT_HOVER,
                     ROUGE, ROUGE_CLAIR, ROUGE_FOND,
                     BLANC, GRIS_TEXTE, GRIS_DOUX,
                     TYPES_HISTORIQUE)
from notifications import notification_succes


class HistoriqueMixin:

    # ═══════════════════════════════════════════
    # 📜 HISTORIQUE
    # ═══════════════════════════════════════════

    def afficher_historique(self):
        self.vider_zone()
        self.afficher_titre("Historique", "📜", ORANGE_DORE)

        nb_total = db.compter_historique()

        # ── Stats ──
        carte_stats = ctk.CTkFrame(self.zone_principale,
                                   fg_color=JAUNE_PALE, corner_radius=15, height=70)
        carte_stats.pack(fill="x", pady=(0, 10))
        carte_stats.pack_propagate(False)
        ctk.CTkLabel(carte_stats,
                     text=f"📜 {nb_total} contenu(s) dans l'historique",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=ORANGE_DORE).pack(pady=22)

        # ── Contrôles ──
        frame_controles = ctk.CTkFrame(self.zone_principale,
                                       fg_color=ORANGE_PALE, corner_radius=12)
        frame_controles.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_controles, text="🔍  Filtrer :",
                     text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=13, weight="bold")).pack(
            side="left", padx=15, pady=10)

        types_dispo = db.lister_types_historique()
        labels_types = ["Tous"] + [
            TYPES_HISTORIQUE.get(t, {}).get("label", t) for t in types_dispo]

        self._types_map = {"Tous": "Tous"}
        for t in types_dispo:
            label = TYPES_HISTORIQUE.get(t, {}).get("label", t)
            self._types_map[label] = t

        self.menu_filtre_histo = ctk.CTkOptionMenu(
            frame_controles, values=labels_types,
            command=self._filtrer_historique,
            fg_color=ORANGE_DORE, text_color=BLANC,
            button_color=ORANGE_CLAIR, corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold"))
        self.menu_filtre_histo.set(self.filtre_historique)
        self.menu_filtre_histo.pack(side="left", padx=10, pady=10)

        ctk.CTkButton(frame_controles, text="🗑️  Tout vider",
                      command=self._vider_historique_confirm,
                      fg_color=ROUGE, text_color=BLANC,
                      hover_color=ROUGE_CLAIR, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="right", padx=15, pady=10)

        ctk.CTkButton(frame_controles, text="🔄",
                      command=self.afficher_historique,
                      fg_color=BLEU_ROYAL, text_color=BLANC,
                      hover_color=BLEU_CIEL, corner_radius=10,
                      height=30, width=40,
                      font=ctk.CTkFont(size=13, weight="bold")).pack(
            side="right", padx=5, pady=10)

        # ── Liste ──
        self.frame_liste_histo = ctk.CTkScrollableFrame(
            self.zone_principale, fg_color=BLANC,
            corner_radius=15, border_width=2, border_color=ORANGE_PALE)
        self.frame_liste_histo.pack(fill="both", expand=True, pady=10)

        self._afficher_liste_historique()

    def _filtrer_historique(self, valeur_label):
        self.filtre_historique = valeur_label
        self._afficher_liste_historique()

    def _afficher_liste_historique(self):
        for widget in self.frame_liste_histo.winfo_children():
            widget.destroy()

        type_filtre = self._types_map.get(self.filtre_historique, "Tous")
        historique = (db.lister_historique_complet(100) if type_filtre == "Tous"
                      else db.filtrer_historique_par_type(type_filtre, 100))

        if not historique:
            ctk.CTkLabel(self.frame_liste_histo,
                         text="📭  Aucun historique pour le moment\n\n"
                              "💡 Génère des résumés, QCM, ou pose des questions !\n"
                              "Tout sera sauvegardé ici automatiquement 🌸",
                         font=ctk.CTkFont(size=14),
                         text_color=GRIS_DOUX, justify="center").pack(pady=50)
            return

        for entree in historique:
            id_h, type_h, question_h, reponse_h, matiere_h, date_h = entree
            self._creer_carte_historique(
                id_h, type_h, question_h, reponse_h, matiere_h, date_h)

    def _creer_carte_historique(self, id_h, type_h, question_h,
                                reponse_h, matiere_h, date_h):
        info_type = TYPES_HISTORIQUE.get(
            type_h, {"emoji": "📄", "label": type_h, "couleur": "#F8F9FA"})

        carte = ctk.CTkFrame(self.frame_liste_histo,
                             fg_color=info_type["couleur"],
                             corner_radius=14,
                             border_width=1, border_color=ORANGE_PALE)
        carte.pack(fill="x", padx=10, pady=6)

        # Ligne 1
        ligne1 = ctk.CTkFrame(carte, fg_color="transparent")
        ligne1.pack(fill="x", padx=15, pady=(12, 3))

        ctk.CTkLabel(ligne1,
                     text=f"{info_type['emoji']}  {info_type['label']}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=ORANGE_DORE).pack(side="left")

        date_simple = date_h.split('.')[0] if date_h else "—"
        ctk.CTkLabel(ligne1, text=f"📅 {date_simple}",
                     font=ctk.CTkFont(size=11),
                     text_color=GRIS_DOUX).pack(side="right")

        if matiere_h:
            ctk.CTkLabel(carte, text=f"🎯 {matiere_h}",
                         font=ctk.CTkFont(size=11),
                         text_color=VIOLET_PREMIUM,
                         anchor="w").pack(anchor="w", padx=15, pady=(0, 3))

        apercu = (question_h or "")[:120]
        if len(question_h or "") > 120:
            apercu += "..."

        ctk.CTkLabel(carte, text=apercu,
                     font=ctk.CTkFont(size=12),
                     text_color=GRIS_TEXTE, wraplength=750,
                     justify="left", anchor="w").pack(
            anchor="w", padx=15, pady=(0, 8))

        # Boutons
        ligne_btns = ctk.CTkFrame(carte, fg_color="transparent")
        ligne_btns.pack(fill="x", padx=15, pady=(0, 12))

        ctk.CTkButton(ligne_btns, text="👁️  Voir",
                      command=lambda i=id_h: self._voir_historique(i),
                      fg_color=VIOLET_PREMIUM, hover_color=VIOLET_LAVANDE,
                      text_color=BLANC, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="left", padx=2, expand=True, fill="x")

        ctk.CTkButton(ligne_btns, text="🔄  Recharger",
                      command=lambda i=id_h: self._recharger_historique(i),
                      fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
                      text_color=BLANC, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="left", padx=2, expand=True, fill="x")

        ctk.CTkButton(ligne_btns, text="🗑️  Supprimer",
                      command=lambda i=id_h: self._supprimer_entree_historique(i),
                      fg_color=ROUGE, hover_color=ROUGE_CLAIR,
                      text_color=BLANC, corner_radius=10, height=30,
                      font=ctk.CTkFont(size=11, weight="bold")).pack(
            side="left", padx=2, expand=True, fill="x")

    def _voir_historique(self, id_h):
        info = db.info_historique(id_h)
        if not info:
            return

        self.vider_zone()
        info_type = TYPES_HISTORIQUE.get(
            info["type"],
            {"emoji": "📄", "label": info["type"], "couleur": "#F8F9FA"})

        self.afficher_titre(
            f"{info_type['label']} - {info['date'].split('.')[0]}",
            info_type["emoji"], ORANGE_DORE)

        carte_info = ctk.CTkFrame(self.zone_principale,
                                  fg_color=JAUNE_PALE, corner_radius=12)
        carte_info.pack(fill="x", pady=5)
        ctk.CTkLabel(carte_info,
                     text=f"🎯 {info['matiere']}  •  📅 {info['date'].split('.')[0]}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=ORANGE_DORE).pack(pady=10)

        zone = self.creer_zone_texte(380)
        contenu_affiche = f"📋 CONTENU :\n\n{info['reponse']}"
        if info.get("question") and info["question"] != info["reponse"]:
            contenu_affiche = (f"❓ TITRE/QUESTION :\n{info['question']}\n\n"
                               f"{'─' * 50}\n\n📋 CONTENU :\n\n{info['reponse']}")
        zone.insert("0.0", contenu_affiche)

        frame_btns = ctk.CTkFrame(self.zone_principale, fg_color="transparent")
        frame_btns.pack(fill="x", pady=5)

        self.creer_bouton_action(
            frame_btns, "⬅️  Retour à l'historique",
            self.afficher_historique,
            ORANGE_DORE, ORANGE_CLAIR).pack(
            side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(frame_btns, text="💾  Exporter PDF",
                      command=lambda: self._exporter(zone, info["type"]),
                      fg_color=OR_MODERNE, text_color=BLANC,
                      hover_color=ORANGE_CLAIR, corner_radius=14,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      height=48).pack(side="left", padx=5, expand=True, fill="x")

    def _recharger_historique(self, id_h):
        info = db.info_historique(id_h)
        if not info:
            return

        type_h = info["type"]
        reponse = info["reponse"]

        if type_h == "resume":
            self.afficher_resume()
            self.after(200, lambda: self._injecter_contenu(self.zone_resultat, reponse))
        elif type_h == "explication":
            self.afficher_explication()
            self.after(200, lambda: self._injecter_contenu(self.zone_resultat, reponse))
        elif type_h == "qcm":
            self.contenu_qcm_complet = reponse
            self.afficher_qcm()
            self.after(200, lambda: self._injecter_contenu(self.zone_qcm, reponse))
        elif type_h == "questions":
            self.contenu_q_complet = reponse
            self.afficher_questions()
            self.after(200, lambda: self._injecter_contenu(self.zone_q, reponse))
        elif type_h == "examen":
            self.contenu_ex_complet = reponse
            self.afficher_examen()
            self.after(200, lambda: self._injecter_contenu(self.zone_ex, reponse))
        elif type_h == "question_libre":
            self.afficher_chat()
            self.after(200, lambda: self._injecter_contenu(self.zone_reponse, reponse))
        elif type_h == "ocr":
            self.afficher_ocr()
            self.after(200, lambda: self._injecter_contenu(self.zone_ocr, reponse))
        else:
            self._voir_historique(id_h)
            return

        notification_succes(self, "Rechargé !", "✅ Contenu restauré !")

    def _supprimer_entree_historique(self, id_h):
        if messagebox.askyesno("🗑️ Supprimer ?",
                               "Supprimer cette entrée de l'historique ?"):
            db.supprimer_historique(id_h)
            notification_succes(self, "Supprimé !", "🗑️ Entrée supprimée")
            self._afficher_liste_historique()

    def _vider_historique_confirm(self):
        nb = db.compter_historique()
        if messagebox.askyesno(
                "🗑️ Vider TOUT l'historique ?",
                f"⚠️ Tu vas supprimer {nb} entrée(s) !\n\n"
                f"Cette action est IRRÉVERSIBLE !"):
            db.vider_historique()
            notification_succes(self, "Historique vidé !", "🗑️ Tout supprimé")
            self.afficher_historique()