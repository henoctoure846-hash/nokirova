# ui/generation.py - Résumé, Explication, QCM, Questions, Examen NOKIROVA 🌸

import customtkinter as ctk
from tkinter import messagebox
import threading
import database as db
from ui.base import (VERT_EMERAUDE, VERT_HOVER, VERT_CLAIR, VERT_CORRECTION,
                     BLEU_ROYAL, BLEU_CIEL, BLEU_PALE, BLEU_TRES_PALE,
                     VIOLET_PREMIUM, VIOLET_LAVANDE, VIOLET_PALE,
                     ROSE_PALE, ROSE_CLAIR, ROSE_SAKURA,
                     JAUNE_PALE, JAUNE_CLAIR,
                     ORANGE_DORE, ORANGE_CLAIR, ORANGE_PALE, OR_MODERNE,
                     BLANC, GRIS_TEXTE)
from ia_handler import creer_resume, expliquer_simplement
from exercice_generator import (generer_qcm, generer_questions_cours,
                                 generer_exercices_examen)
from ui.base import separer_correction


class GenerationMixin:

    # ═══════════════════════════════════════════
    # 📝 RÉSUMÉ
    # ═══════════════════════════════════════════

    def afficher_resume(self):
        self.vider_zone()
        self.afficher_titre("Résumé du cours", "📝", BLEU_ROYAL)
        self._page_generation(
            creer_resume,
            "📝  Générer le résumé",
            BLEU_ROYAL, BLEU_CIEL, "resume")

    # ═══════════════════════════════════════════
    # 💡 EXPLICATION
    # ═══════════════════════════════════════════

    def afficher_explication(self):
        self.vider_zone()
        self.afficher_titre("Explication simplifiée", "💡", ORANGE_DORE)
        self._page_generation(
            expliquer_simplement,
            "💡  Expliquer simplement",
            ORANGE_DORE, ORANGE_CLAIR, "explication")

    def _page_generation(self, fonction, texte_btn, couleur, hover, nom_export):
        self.creer_bouton_action(
            self.zone_principale, texte_btn,
            lambda: self._generer(fonction, self.zone_resultat, nom_export),
            couleur, hover).pack(pady=10, fill="x")

        self.zone_resultat = self.creer_zone_texte(380)

        if not self.cours_actuel:
            self.zone_resultat.insert(
                "0.0",
                "⚠️ Importe d'abord un cours ou "
                "charge-en un depuis la Bibliothèque (Ctrl+B) !")
        else:
            self.zone_resultat.insert(
                "0.0",
                f"👆 Clique sur le bouton pour générer !\n\n"
                f"📚 Cours chargé : {self.nom_cours}")

        self.creer_bouton_export(self.zone_resultat, nom_export).pack(pady=5)

    def _generer(self, fonction, zone_affichage, type_historique=""):
        if not self.cours_actuel:
            messagebox.showwarning(
                "⚠️",
                "Importe d'abord un cours ou "
                "charge-en un depuis la Bibliothèque !")
            return

        zone_affichage.delete("0.0", "end")
        zone_affichage.insert("0.0", "⏳ NOKIROVA réfléchit... 🧠✨")
        self.update()

        def tache():
            res = fonction(self.cours_actuel[:5000])
            zone_affichage.delete("0.0", "end")
            zone_affichage.insert("0.0", res)
            if type_historique:
                db.sauvegarder_historique(
                    type_historique, self.nom_cours, res,
                    self.matiere_detectee or "Général")
            self._recompenser(5)

        threading.Thread(target=tache, daemon=True).start()

    # ═══════════════════════════════════════════
    # 🎯 QCM
    # ═══════════════════════════════════════════

    def afficher_qcm(self):
        self.vider_zone()
        self.afficher_titre("Générer des QCM", "🎯", VIOLET_PREMIUM)

        # ── Slider nombre ──
        frame = ctk.CTkFrame(self.zone_principale,
                             fg_color=ROSE_PALE, corner_radius=14)
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(frame, text="🎚️  Nombre :",
                     text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(
            side="left", padx=15, pady=15)

        self.nb_qcm = ctk.CTkSlider(
            frame, from_=1, to=20, number_of_steps=19,
            progress_color=VIOLET_LAVANDE,
            button_color=VIOLET_PREMIUM)
        self.nb_qcm.set(5)
        self.nb_qcm.pack(side="left", padx=10, pady=15,
                         fill="x", expand=True)

        self.label_nb = ctk.CTkLabel(
            frame, text="5",
            text_color=VIOLET_PREMIUM,
            font=ctk.CTkFont(size=20, weight="bold"))
        self.label_nb.pack(side="left", padx=15)
        self.nb_qcm.configure(
            command=lambda v: self.label_nb.configure(text=str(int(v))))

        # ── Boutons ──
        frame_btns = ctk.CTkFrame(self.zone_principale, fg_color="transparent")
        frame_btns.pack(fill="x", pady=10)

        self.creer_bouton_action(
            frame_btns, "🎯  Générer les QCM",
            self._generer_qcm,
            VIOLET_PREMIUM, VIOLET_LAVANDE).pack(
            side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            frame_btns, text="🎮  MODE INTERACTIF",
            command=self.lancer_qcm_interactif,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, corner_radius=14,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            height=48, border_width=2,
            border_color=VERT_CORRECTION).pack(
            side="left", padx=5, expand=True, fill="x")

        # ── Zone résultat ──
        self.zone_qcm = self.creer_zone_texte(260)

        if not self.cours_actuel:
            self.zone_qcm.insert(
                "0.0",
                "⚠️ Importe d'abord un cours ou "
                "charge-en un depuis la Bibliothèque !")
        else:
            self.zone_qcm.insert(
                "0.0",
                "👆 Génère des QCM, puis lance le "
                "🎮 MODE INTERACTIF pour t'entraîner !")

        self.btn_corriger_qcm = self._creer_bouton_correction("qcm")
        self.btn_corriger_qcm.pack(pady=8, fill="x")
        self.creer_bouton_export(self.zone_qcm, "qcm").pack(pady=5)

    def _generer_qcm(self):
        if not self.cours_actuel:
            messagebox.showwarning("⚠️", "Importe d'abord un cours !")
            return

        nb = int(self.nb_qcm.get())
        self.zone_qcm.delete("0.0", "end")
        self.zone_qcm.insert("0.0", f"⏳ Génération de {nb} QCM... ✨")
        self.update()

        def tache():
            res = generer_qcm(self.cours_actuel[:5000], nb)
            self.contenu_qcm_complet = res
            self.correction_visible["qcm"] = False
            questions, _ = separer_correction(res)
            self.zone_qcm.delete("0.0", "end")
            self.zone_qcm.insert("0.0", questions if questions else res)
            self.btn_corriger_qcm.configure(
                text="✅  CORRIGER",
                fg_color=VERT_EMERAUDE,
                hover_color=VERT_HOVER)
            db.sauvegarder_historique(
                "qcm", f"{nb} QCM - {self.nom_cours}", res,
                self.matiere_detectee or "Général")
            self._recompenser(nb * 2, f"{nb} QCM générés !")

        threading.Thread(target=tache, daemon=True).start()

    # ═══════════════════════════════════════════
    # ❓ QUESTIONS DE COURS
    # ═══════════════════════════════════════════

    def afficher_questions(self):
        self.vider_zone()
        self.afficher_titre("Questions de cours", "❓", VIOLET_LAVANDE)

        frame = ctk.CTkFrame(self.zone_principale,
                             fg_color=ROSE_SAKURA, corner_radius=14)
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(frame, text="🎚️  Nombre :",
                     text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(
            side="left", padx=15, pady=15)

        self.nb_q = ctk.CTkSlider(
            frame, from_=1, to=15, number_of_steps=14,
            progress_color=VIOLET_LAVANDE,
            button_color=VIOLET_PREMIUM)
        self.nb_q.set(5)
        self.nb_q.pack(side="left", padx=10, pady=15, fill="x", expand=True)

        lbl = ctk.CTkLabel(frame, text="5",
                           text_color=VIOLET_PREMIUM,
                           font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(side="left", padx=15)
        self.nb_q.configure(
            command=lambda v: lbl.configure(text=str(int(v))))

        self.creer_bouton_action(
            self.zone_principale, "❓  Générer",
            self._gen_q,
            VIOLET_LAVANDE, VIOLET_PREMIUM).pack(pady=15, fill="x")

        self.zone_q = self.creer_zone_texte(280)

        if not self.cours_actuel:
            self.zone_q.insert(
                "0.0",
                "⚠️ Importe d'abord un cours ou "
                "charge-en un depuis la Bibliothèque !")
        else:
            self.zone_q.insert(
                "0.0", "👆 Clique sur 'Générer' pour commencer !")

        self.btn_corriger_q = self._creer_bouton_correction("q")
        self.btn_corriger_q.pack(pady=8, fill="x")
        self.creer_bouton_export(self.zone_q, "questions").pack(pady=5)

    def _gen_q(self):
        if not self.cours_actuel:
            messagebox.showwarning("⚠️", "Importe d'abord un cours !")
            return

        nb = int(self.nb_q.get())
        self.zone_q.delete("0.0", "end")
        self.zone_q.insert("0.0", "⏳ Génération en cours...")
        self.update()

        def tache():
            res = generer_questions_cours(self.cours_actuel[:5000], nb)
            self.contenu_q_complet = res
            self.correction_visible["q"] = False
            questions, _ = separer_correction(res)
            self.zone_q.delete("0.0", "end")
            self.zone_q.insert("0.0", questions if questions else res)
            self.btn_corriger_q.configure(
                text="✅  CORRIGER",
                fg_color=VERT_EMERAUDE,
                hover_color=VERT_HOVER)
            db.sauvegarder_historique(
                "questions", f"{nb} Questions - {self.nom_cours}", res,
                self.matiere_detectee or "Général")
            self._recompenser(nb * 2, f"{nb} questions générées !")

        threading.Thread(target=tache, daemon=True).start()

    # ═══════════════════════════════════════════
    # 📚 EXERCICES EXAMEN
    # ═══════════════════════════════════════════

    def afficher_examen(self):
        self.vider_zone()
        self.afficher_titre("Exercices type Examen", "📚", ORANGE_DORE)

        frame = ctk.CTkFrame(self.zone_principale,
                             fg_color=JAUNE_PALE, corner_radius=14)
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(frame, text="🎓  Niveau :",
                     text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(
            side="left", padx=15, pady=15)

        self.niveau = ctk.CTkOptionMenu(
            frame,
            values=["🟢 Débutant", "🟡 Intermédiaire",
                    "🟠 Difficile", "🔴 Ultra difficile"],
            fg_color=ORANGE_DORE, text_color=BLANC,
            button_color=ORANGE_CLAIR,
            button_hover_color=ORANGE_PALE,
            dropdown_fg_color=BLANC,
            dropdown_text_color=GRIS_TEXTE,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10)
        self.niveau.pack(side="left", padx=10, pady=15)

        ctk.CTkLabel(frame, text="📊  Nombre :",
                     text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(
            side="left", padx=(20, 5))

        self.nb_ex = ctk.CTkOptionMenu(
            frame, values=["1", "2", "3", "5", "10"],
            fg_color=ORANGE_DORE, text_color=BLANC,
            button_color=ORANGE_CLAIR, corner_radius=10)
        self.nb_ex.set("3")
        self.nb_ex.pack(side="left", padx=10)

        self.creer_bouton_action(
            self.zone_principale,
            "📚  Générer les exercices",
            self._gen_examen,
            ORANGE_DORE, ORANGE_CLAIR).pack(pady=15, fill="x")

        self.zone_ex = self.creer_zone_texte(250)

        if not self.cours_actuel:
            self.zone_ex.insert(
                "0.0",
                "⚠️ Importe d'abord un cours ou "
                "charge-en un depuis la Bibliothèque !")
        else:
            self.zone_ex.insert(
                "0.0",
                "👆 Clique sur 'Générer les exercices' pour commencer !")

        self.btn_corriger_ex = self._creer_bouton_correction("ex")
        self.btn_corriger_ex.pack(pady=8, fill="x")
        self.creer_bouton_export(self.zone_ex, "examen").pack(pady=5)

    def _gen_examen(self):
        if not self.cours_actuel:
            messagebox.showwarning("⚠️", "Importe d'abord un cours !")
            return

        niveaux_map = {
            "🟢 Débutant": "debutant",
            "🟡 Intermédiaire": "intermediaire",
            "🟠 Difficile": "difficile",
            "🔴 Ultra difficile": "ultra_difficile"}

        niveau = niveaux_map.get(self.niveau.get(), "intermediaire")
        nb = int(self.nb_ex.get())

        self.zone_ex.delete("0.0", "end")
        self.zone_ex.insert(
            "0.0", f"⏳ Génération de {nb} exercices niveau {niveau}...")
        self.update()

        def tache():
            res = generer_exercices_examen(self.cours_actuel[:5000], niveau, nb)
            self.contenu_ex_complet = res
            self.correction_visible["ex"] = False
            questions, _ = separer_correction(res)
            self.zone_ex.delete("0.0", "end")
            self.zone_ex.insert("0.0", questions if questions else res)
            self.btn_corriger_ex.configure(
                text="✅  CORRIGER",
                fg_color=VERT_EMERAUDE,
                hover_color=VERT_HOVER)
            db.sauvegarder_historique(
                "examen",
                f"{nb} Exercices {niveau} - {self.nom_cours}",
                res, self.matiere_detectee or "Général")
            self._recompenser(nb * 5, f"{nb} exercices générés !")

        threading.Thread(target=tache, daemon=True).start()