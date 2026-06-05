# ui/import_ocr.py - Import et OCR NOKIROVA 🌸

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import database as db
from ui.base import (VERT_EMERAUDE, VERT_HOVER, VERT_CLAIR,
                     BLEU_ROYAL, BLEU_CIEL, BLEU_TRES_PALE,
                     BLANC, GRIS_TEXTE, OR_MODERNE, ORANGE_CLAIR)
from document_parser import lire_document
from ocr_handler import lire_image_et_expliquer


class ImportOCRMixin:

    # ═══════════════════════════════════════════
    # 📥 IMPORT
    # ═══════════════════════════════════════════

    def afficher_import(self):
        self.vider_zone()
        self.afficher_titre("Importer un cours", "📥", BLEU_ROYAL)

        info_card = ctk.CTkFrame(self.zone_principale,
                                 fg_color=BLEU_TRES_PALE, corner_radius=12)
        info_card.pack(fill="x", pady=5)
        ctk.CTkLabel(info_card,
                     text="📄 Formats : PDF • Word • PowerPoint • TXT\n"
                          "🔍 NOKIROVA détecte automatiquement la matière !\n"
                          "📚 Tous tes cours sont sauvegardés dans la Bibliothèque",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=BLEU_ROYAL,
                     justify="center").pack(pady=12)

        self.creer_bouton_action(
            self.zone_principale,
            "📁  Choisir un fichier",
            self.charger_fichier,
            BLEU_ROYAL, BLEU_CIEL).pack(pady=15, fill="x")

        self.zone_apercu = self.creer_zone_texte(400)
        self.zone_apercu.insert(
            "0.0",
            "📄 L'aperçu du cours apparaîtra ici après import...\n\n"
            "💡 Astuce : utilise Ctrl+I pour ouvrir cette page rapidement !\n"
            "📚 Tape Ctrl+B pour ouvrir la Bibliothèque !")

    def charger_fichier(self):
        chemin = filedialog.askopenfilename(
            title="Choisis ton cours",
            filetypes=[
                ("Tous les supportés", "*.pdf *.docx *.pptx *.txt"),
                ("PDF", "*.pdf"),
                ("Word", "*.docx"),
                ("PowerPoint", "*.pptx"),
                ("Texte", "*.txt")])

        if chemin:
            self.zone_apercu.delete("0.0", "end")
            self.zone_apercu.insert(
                "0.0",
                "⏳ Lecture du fichier...\n"
                "🔍 Détection automatique de la matière...\n"
                "🧠 NOKIROVA analyse...")
            self.update()

            self.cours_actuel = lire_document(chemin)
            self.nom_cours = os.path.basename(chemin)

            def tache():
                matiere = db.sauvegarder_cours(self.nom_cours, self.cours_actuel)
                self.matiere_detectee = matiere
                cours_list = db.lister_cours()
                if cours_list:
                    self.id_cours_actif = cours_list[0][0]
                self.statut_label.configure(
                    text=f"{matiere}\n{self.nom_cours[:25]}")
                self.zone_apercu.delete("0.0", "end")
                self.zone_apercu.insert(
                    "0.0",
                    f"✅ Cours chargé et sauvegardé dans la Bibliothèque !\n\n"
                    f"🎯 MATIÈRE DÉTECTÉE : {matiere}\n"
                    f"📁 Fichier : {self.nom_cours}\n"
                    f"📊 Taille : {len(self.cours_actuel)} caractères\n"
                    f"📄 Pages détectées : {self.cours_actuel.count('--- Page')}\n\n"
                    f"═══ CONTENU COMPLET DU COURS ═══\n\n"
                    f"{self.cours_actuel}")
                self._recompenser(10, f"Cours chargé : {matiere}")

            threading.Thread(target=tache, daemon=True).start()

    # ═══════════════════════════════════════════
    # 📸 OCR
    # ═══════════════════════════════════════════

    def afficher_ocr(self):
        self.vider_zone()
        self.afficher_titre("Scanner une image", "📸", VERT_EMERAUDE)

        info = ctk.CTkFrame(self.zone_principale,
                            fg_color=VERT_CLAIR, corner_radius=12)
        info.pack(fill="x", pady=5)
        ctk.CTkLabel(info,
                     text="📸 Prends en photo un cours, un exercice...\n"
                          "NOKIROVA va LIRE et EXPLIQUER ! 🤖✨",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=BLANC, justify="center").pack(pady=12)

        self.creer_bouton_action(
            self.zone_principale,
            "📁  Choisir une image",
            self._scanner_image,
            VERT_EMERAUDE, VERT_HOVER).pack(pady=15, fill="x")

        self.zone_ocr = self.creer_zone_texte(380)
        self.zone_ocr.insert("0.0", "📸 Sélectionne une image ci-dessus...")

        self.creer_bouton_export(self.zone_ocr, "ocr").pack(pady=5)

    def _scanner_image(self):
        chemin = filedialog.askopenfilename(
            title="Choisis une image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")])

        if chemin:
            self.zone_ocr.delete("0.0", "end")
            self.zone_ocr.insert("0.0", "⏳ Lecture... 🔍\n⏳ Analyse IA... 🧠")
            self.update()

            def tache():
                resultat = lire_image_et_expliquer(chemin)
                self.zone_ocr.delete("0.0", "end")
                self.zone_ocr.insert("0.0", resultat)
                db.sauvegarder_historique(
                    "ocr", "Image scannée", resultat,
                    self.matiere_detectee or "Général")
                self._recompenser(15, "Image scannée !")

            threading.Thread(target=tache, daemon=True).start()