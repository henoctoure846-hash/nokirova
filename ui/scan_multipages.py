# ui/scan_multipages.py - Scan multi-pages NOKIROVA 📸📚

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from datetime import datetime
from PIL import Image
import database as db
from ui.base import (
    VERT_EMERAUDE, VERT_HOVER, VERT_CLAIR, VERT_CORRECTION,
    VERT_FOND_CORRECTION,
    BLEU_ROYAL, BLEU_CIEL, BLEU_TRES_PALE, BLEU_PALE,
    JAUNE_SOLEIL, JAUNE_CLAIR, JAUNE_PALE, OR_MODERNE,
    VIOLET_PREMIUM, VIOLET_LAVANDE, VIOLET_PALE,
    ROSE_SAKURA, ROSE_PALE,
    ORANGE_DORE, ORANGE_CLAIR, ORANGE_PALE,
    ROUGE, ROUGE_CLAIR,
    BLANC, BLANC_CASSE, GRIS_TEXTE, GRIS_DOUX, GRIS_PERLE
)
from notifications import notification_succes
from ocr_handler import lire_image, TESSERACT_DISPONIBLE


MAX_IMAGES = 50
FOND_GRIS = "#E5E7EB"


class ScanMultipagesMixin:

    # ═══════════════════════════════════════════
    # 📸 PAGE PRINCIPALE
    # ═══════════════════════════════════════════

    def afficher_scan_multipages(self):
        self.vider_zone()
        self.afficher_titre(
            "Scan Multi-pages", "📚", VERT_EMERAUDE)

        # Init liste images
        if not hasattr(self, '_scan_images'):
            self._scan_images = []
        if not hasattr(self, '_scan_texte_final'):
            self._scan_texte_final = ""

        # ── SCROLL principal avec FOND GRIS ──
        scroll = ctk.CTkScrollableFrame(
            self.zone_principale, fg_color=FOND_GRIS)
        scroll.pack(fill="both", expand=True)
        self._scan_scroll = scroll

        # ── Bandeau info ──
        info = ctk.CTkFrame(
            scroll, fg_color=VERT_CLAIR, corner_radius=12)
        info.pack(fill="x", pady=5)
        ctk.CTkLabel(
            info,
            text="📚 Scanne JUSQU'À 50 IMAGES en une fois !\n"
                 "🧠 NOKIROVA fusionne tout en UN SEUL cours intelligent.",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=BLANC, justify="center").pack(pady=12)

        # ── Vérif Tesseract ──
        if not TESSERACT_DISPONIBLE:
            warn = ctk.CTkFrame(
                scroll, fg_color=ROUGE_CLAIR, corner_radius=12)
            warn.pack(fill="x", pady=8)
            ctk.CTkLabel(
                warn,
                text="⚠️  Tesseract OCR non disponible !\n"
                     "💡 Installe Tesseract pour utiliser cette fonction.",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=BLANC, justify="center").pack(pady=10)
            return

        # ── Boutons d'action principaux ──
        actions = ctk.CTkFrame(scroll, fg_color="transparent")
        actions.pack(fill="x", pady=10)

        ctk.CTkButton(
            actions, text="📁  Ajouter des images",
            command=self._ajouter_images,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, corner_radius=12, height=45,
            font=ctk.CTkFont(size=14, weight="bold")).pack(
            side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            actions, text="🗑️  Tout effacer",
            command=self._effacer_toutes_images,
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, corner_radius=12, height=45,
            font=ctk.CTkFont(size=14, weight="bold")).pack(
            side="left", padx=5, expand=True, fill="x")

        # ── Compteur images ──
        nb = len(self._scan_images)
        couleur_compteur = (VERT_EMERAUDE if nb > 0
                            else GRIS_DOUX)
        self._scan_compteur = ctk.CTkLabel(
            scroll,
            text=f"📊 {nb}/{MAX_IMAGES} images sélectionnées",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=couleur_compteur)
        self._scan_compteur.pack(pady=8)

        # ── Liste des images (cadre) ──
        ctk.CTkLabel(
            scroll, text="📑  PAGES À SCANNER",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", padx=5, pady=(8, 2))

        cadre_liste = ctk.CTkFrame(
            scroll, fg_color=BLANC, corner_radius=14,
            border_width=2, border_color=VERT_CLAIR)
        cadre_liste.pack(fill="x", pady=3)

        self._scan_liste_frame = ctk.CTkFrame(
            cadre_liste, fg_color="transparent")
        self._scan_liste_frame.pack(fill="x", padx=10, pady=10)

        self._afficher_liste_images()

        # ── Barre de progression (cachée au départ) ──
        self._scan_progress_frame = ctk.CTkFrame(
            scroll, fg_color=BLEU_TRES_PALE, corner_radius=12)
        self._scan_progress_label = ctk.CTkLabel(
            self._scan_progress_frame,
            text="⏳  Préparation...",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=BLEU_ROYAL)
        self._scan_progress_label.pack(pady=(10, 5))
        self._scan_progress_bar = ctk.CTkProgressBar(
            self._scan_progress_frame,
            progress_color=VERT_EMERAUDE,
            fg_color=BLANC, height=18, corner_radius=9)
        self._scan_progress_bar.pack(
            fill="x", padx=20, pady=(0, 10))
        self._scan_progress_bar.set(0)

        # ── Bouton LANCER LE SCAN ──
        self.btn_lancer_scan = ctk.CTkButton(
            scroll, text="✨  LANCER LE SCAN ✨",
            command=self._lancer_scan_complet,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, corner_radius=14, height=55,
            font=ctk.CTkFont(size=17, weight="bold"))
        self.btn_lancer_scan.pack(fill="x", pady=12)

        # ── Zone résultat ──
        ctk.CTkLabel(
            scroll, text="📄  TEXTE EXTRAIT",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=VERT_CORRECTION, anchor="w").pack(
            fill="x", padx=5, pady=(8, 2))

        cadre_resultat = ctk.CTkFrame(
            scroll, fg_color=BLANC, corner_radius=14,
            border_width=2, border_color=VERT_CLAIR)
        cadre_resultat.pack(fill="x", pady=3)

        self.zone_scan_resultat = ctk.CTkTextbox(
            cadre_resultat, fg_color=BLANC, text_color=GRIS_TEXTE,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            corner_radius=10, wrap="word", border_width=0,
            height=250)
        self.zone_scan_resultat.pack(
            fill="x", padx=10, pady=10)
        self.zone_scan_resultat.insert(
            "0.0",
            "📚 Le texte extrait de toutes les pages\n"
            "    apparaîtra ici après le scan...")

        # ── Boutons résultat ──
        frame_res = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_res.pack(fill="x", pady=8)

        ctk.CTkButton(
            frame_res, text="🤖  Corriger avec IA",
            command=self._corriger_ia_scan,
            fg_color=VIOLET_PREMIUM, hover_color=VIOLET_LAVANDE,
            text_color=BLANC, corner_radius=10, height=40,
            font=ctk.CTkFont(size=12, weight="bold")).pack(
            side="left", padx=3, expand=True, fill="x")

        ctk.CTkButton(
            frame_res, text="💾  Sauvegarder cours",
            command=self._sauvegarder_scan_cours,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, corner_radius=10, height=40,
            font=ctk.CTkFont(size=12, weight="bold")).pack(
            side="left", padx=3, expand=True, fill="x")

        ctk.CTkButton(
            frame_res, text="📄  Export PDF",
            command=self._exporter_scan_pdf,
            fg_color=OR_MODERNE, hover_color=ORANGE_DORE,
            text_color=BLANC, corner_radius=10, height=40,
            font=ctk.CTkFont(size=12, weight="bold")).pack(
            side="left", padx=3, expand=True, fill="x")

        # Espace bas
        ctk.CTkLabel(scroll, text="", height=15).pack()

    # ═══════════════════════════════════════════
    # 📁 AJOUTER IMAGES
    # ═══════════════════════════════════════════

    def _ajouter_images(self):
        """Sélectionne plusieurs images via filedialog"""
        chemins = filedialog.askopenfilenames(
            title="Sélectionne tes images (Ctrl+clic pour plusieurs)",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("JPG", "*.jpg *.jpeg"),
                ("PNG", "*.png")])
        if not chemins:
            return

        # Vérifier la limite
        place_dispo = MAX_IMAGES - len(self._scan_images)
        if place_dispo <= 0:
            messagebox.showwarning(
                "⚠️ Limite atteinte",
                f"Tu as déjà {MAX_IMAGES} images !\n"
                "Supprime-en pour en ajouter d'autres.")
            return

        if len(chemins) > place_dispo:
            messagebox.showinfo(
                "ℹ️ Limite",
                f"Seulement {place_dispo} images ajoutées\n"
                f"(limite {MAX_IMAGES} max).")
            chemins = chemins[:place_dispo]

        # Ajouter à la liste
        for c in chemins:
            self._scan_images.append({
                "chemin": c,
                "nom": os.path.basename(c)
            })

        notification_succes(
            self, "Ajoutées !",
            f"📁 {len(chemins)} image(s) ajoutée(s)")
        self.afficher_scan_multipages()

    def _effacer_toutes_images(self):
        """Efface toute la liste"""
        if not self._scan_images:
            return
        if messagebox.askyesno(
                "🗑️ Confirmer",
                f"Effacer les {len(self._scan_images)} images ?"):
            self._scan_images = []
            self._scan_texte_final = ""
            notification_succes(
                self, "Effacé !", "🗑️ Liste vidée")
            self.afficher_scan_multipages()

    # ═══════════════════════════════════════════
    # 📑 AFFICHAGE LISTE
    # ═══════════════════════════════════════════

    def _afficher_liste_images(self):
        """Affiche la liste des images avec miniatures"""
        # Vider
        for w in self._scan_liste_frame.winfo_children():
            w.destroy()

        if not self._scan_images:
            ctk.CTkLabel(
                self._scan_liste_frame,
                text="📭  Aucune image sélectionnée.\n"
                     "💡 Clique sur 📁 Ajouter des images.",
                font=ctk.CTkFont(size=13),
                text_color=GRIS_DOUX, justify="center").pack(pady=25)
            return

        # Afficher chaque image
        for i, img_data in enumerate(self._scan_images):
            self._creer_ligne_image(i, img_data)

    def _creer_ligne_image(self, index, img_data):
        """Crée une ligne par image avec miniature"""
        ligne = ctk.CTkFrame(
            self._scan_liste_frame,
            fg_color=GRIS_PERLE, corner_radius=10,
            border_width=2, border_color=BLEU_CIEL)
        ligne.pack(fill="x", pady=3)

        # Numéro de page
        num_frame = ctk.CTkFrame(
            ligne, fg_color=VERT_EMERAUDE, corner_radius=8,
            width=55, height=55)
        num_frame.pack(side="left", padx=10, pady=8)
        num_frame.pack_propagate(False)
        ctk.CTkLabel(
            num_frame, text=f"#{index + 1}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=BLANC).pack(expand=True)

        # Miniature
        try:
            img = Image.open(img_data["chemin"])
            img.thumbnail((60, 60))
            mini = ctk.CTkImage(
                light_image=img, dark_image=img, size=(60, 60))
            ctk.CTkLabel(ligne, image=mini, text="").pack(
                side="left", padx=5, pady=8)
        except Exception:
            ctk.CTkLabel(
                ligne, text="🖼️",
                font=ctk.CTkFont(size=30)).pack(side="left", padx=10)

        # Nom du fichier
        ctk.CTkLabel(
            ligne, text=img_data["nom"][:45],
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(
            side="left", padx=10, fill="x", expand=True)

        # Boutons réorganisation
        btn_frame = ctk.CTkFrame(ligne, fg_color="transparent")
        btn_frame.pack(side="right", padx=8, pady=8)

        ctk.CTkButton(
            btn_frame, text="⬆️",
            command=lambda i=index: self._monter_image(i),
            fg_color=BLEU_ROYAL, hover_color=BLEU_CIEL,
            text_color=BLANC, width=35, height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=7).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame, text="⬇️",
            command=lambda i=index: self._descendre_image(i),
            fg_color=BLEU_ROYAL, hover_color=BLEU_CIEL,
            text_color=BLANC, width=35, height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=7).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame, text="🗑️",
            command=lambda i=index: self._supprimer_image(i),
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, width=35, height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=7).pack(side="left", padx=2)

    def _monter_image(self, index):
        if index > 0:
            self._scan_images[index], self._scan_images[index - 1] = \
                self._scan_images[index - 1], self._scan_images[index]
            self.afficher_scan_multipages()

    def _descendre_image(self, index):
        if index < len(self._scan_images) - 1:
            self._scan_images[index], self._scan_images[index + 1] = \
                self._scan_images[index + 1], self._scan_images[index]
            self.afficher_scan_multipages()

    def _supprimer_image(self, index):
        if 0 <= index < len(self._scan_images):
            self._scan_images.pop(index)
            self.afficher_scan_multipages()

    # ═══════════════════════════════════════════
    # ✨ LANCER LE SCAN
    # ═══════════════════════════════════════════

    def _lancer_scan_complet(self):
        """Lance l'OCR sur toutes les images"""
        if not self._scan_images:
            messagebox.showwarning(
                "⚠️", "Ajoute des images d'abord !")
            return

        # Afficher barre progression
        self._scan_progress_frame.pack(fill="x", pady=8)
        self._scan_progress_bar.set(0)
        self._scan_progress_label.configure(
            text="⏳  Démarrage...")
        self.btn_lancer_scan.configure(
            text="⏳  Scan en cours...", state="disabled")
        self.update()

        # Thread
        threading.Thread(
            target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        """Thread qui traite toutes les images"""
        try:
            total = len(self._scan_images)
            textes = []

            for i, img_data in enumerate(self._scan_images):
                # MAJ progression
                progress = (i + 1) / total
                msg = (f"⏳  Page {i + 1}/{total} : "
                       f"{img_data['nom'][:35]}")
                self.after(
                    0, lambda p=progress, m=msg:
                    self._maj_progression(p, m))

                # OCR
                try:
                    texte = lire_image(img_data["chemin"])
                    if texte and not texte.startswith(("❌", "⚠️")):
                        textes.append(
                            f"\n\n═══ PAGE {i + 1} : "
                            f"{img_data['nom']} ═══\n\n{texte}")
                    else:
                        textes.append(
                            f"\n\n═══ PAGE {i + 1} ═══\n\n"
                            f"⚠️ {texte}")
                except Exception as e:
                    textes.append(
                        f"\n\n═══ PAGE {i + 1} ═══\n\n"
                        f"❌ Erreur : {str(e)}")

            # Texte final
            self._scan_texte_final = "".join(textes).strip()

            # Affichage UI
            self.after(0, self._scan_termine)

        except Exception as e:
            self.after(
                0, lambda: self._scan_erreur(str(e)))

    def _maj_progression(self, valeur, message):
        """MAJ visuelle de la progression"""
        self._scan_progress_bar.set(valeur)
        self._scan_progress_label.configure(text=message)

    def _scan_termine(self):
        """Quand le scan est fini"""
        self._scan_progress_bar.set(1)
        self._scan_progress_label.configure(
            text="✅  Scan terminé !")
        self.btn_lancer_scan.configure(
            text="✨  LANCER LE SCAN ✨", state="normal")

        self.zone_scan_resultat.delete("0.0", "end")
        self.zone_scan_resultat.insert("0.0", self._scan_texte_final)

        nb_chars = len(self._scan_texte_final)
        notification_succes(
            self, "Scan terminé !",
            f"📚 {len(self._scan_images)} pages • {nb_chars} car.")
        self._recompenser(
            len(self._scan_images) * 5,
            "Scan multi-pages réussi ! 📸")

    def _scan_erreur(self, msg):
        """Erreur pendant le scan"""
        self._scan_progress_label.configure(
            text=f"❌  Erreur : {msg[:60]}")
        self.btn_lancer_scan.configure(
            text="✨  LANCER LE SCAN ✨", state="normal")
        messagebox.showerror("❌ Erreur", msg)

    # ═══════════════════════════════════════════
    # 🤖 CORRECTION IA
    # ═══════════════════════════════════════════

    def _corriger_ia_scan(self):
        """Demande à l'IA de corriger/améliorer le texte OCR"""
        texte = self.zone_scan_resultat.get("0.0", "end").strip()
        if (not texte or "apparaîtra ici" in texte or
                len(texte) < 20):
            messagebox.showwarning(
                "⚠️", "Lance d'abord un scan !")
            return

        if not messagebox.askyesno(
                "🤖 Correction IA",
                "L'IA va corriger le texte OCR :\n"
                "• Fautes de frappe corrigées\n"
                "• Mise en forme propre\n"
                "• Vocabulaire technique respecté\n\n"
                "Continuer ?"):
            return

        self.zone_scan_resultat.delete("0.0", "end")
        self.zone_scan_resultat.insert(
            "0.0",
            "🤖  L'IA corrige ton texte...\n\n"
            "💡 Patience, ça peut prendre 10-30 secondes...")
        self.update()

        threading.Thread(
            target=self._correction_ia_thread,
            args=(texte,), daemon=True).start()

    def _correction_ia_thread(self, texte):
        """Thread de correction IA"""
        try:
            from ia_handler import demander_ia_brut

            prompt = f"""Tu es un expert en correction de textes OCR.

MISSION : Corrige ce texte extrait par OCR (Reconnaissance optique).

RÈGLES :
- Corrige les fautes de frappe évidentes
- Ajoute la ponctuation manquante
- Garde la structure (titres, paragraphes, listes)
- Respecte le vocabulaire technique
- Conserve les marqueurs "═══ PAGE X ═══"
- NE RÉSUME PAS, ne raccourcis pas
- Réponds UNIQUEMENT avec le texte corrigé

TEXTE OCR :
{texte}

TEXTE CORRIGÉ :"""

            corrige = demander_ia_brut(prompt, temperature=0.2)
            corrige = corrige.strip()

            self._scan_texte_final = corrige
            self.after(0, lambda: self._afficher_correction(corrige))
        except Exception as e:
            self.after(
                0, lambda: self._afficher_correction(
                    f"❌ Erreur IA : {str(e)}"))

    def _afficher_correction(self, texte):
        """Affiche le texte corrigé"""
        self.zone_scan_resultat.delete("0.0", "end")
        self.zone_scan_resultat.insert("0.0", texte)
        if not texte.startswith("❌"):
            notification_succes(
                self, "Corrigé !", "🤖 Texte amélioré par IA")
            self._recompenser(10, "Correction IA réussie !")

    # ═══════════════════════════════════════════
    # 💾 SAUVEGARDER COMME COURS
    # ═══════════════════════════════════════════

    def _sauvegarder_scan_cours(self):
        """Sauvegarde le scan comme nouveau cours dans la bibliothèque"""
        texte = self.zone_scan_resultat.get("0.0", "end").strip()
        if (not texte or "apparaîtra ici" in texte or
                len(texte) < 20):
            messagebox.showwarning(
                "⚠️", "Lance d'abord un scan !")
            return

        # Nom auto
        date = datetime.now().strftime("%d-%m-%Y_%Hh%M")
        nb_pages = len(self._scan_images)
        nom = f"Scan_{nb_pages}pages_{date}"

        try:
            matiere = db.sauvegarder_cours(nom, texte)
            notification_succes(
                self, "Sauvegardé !",
                f"📚 {nom[:30]}")
            messagebox.showinfo(
                "✅ Cours créé",
                f"📚 Ajouté à ta bibliothèque !\n\n"
                f"📄 Nom : {nom}\n"
                f"🎯 Matière : {matiere}\n"
                f"📊 {nb_pages} pages • {len(texte)} car.")
            self._recompenser(15, "Cours scanné sauvegardé ! 💾")
        except Exception as e:
            messagebox.showerror("❌ Erreur", str(e))

    # ═══════════════════════════════════════════
    # 📄 EXPORT PDF
    # ═══════════════════════════════════════════

    def _exporter_scan_pdf(self):
        """Exporte le scan en PDF"""
        texte = self.zone_scan_resultat.get("0.0", "end").strip()
        if (not texte or "apparaîtra ici" in texte or
                len(texte) < 20):
            messagebox.showwarning(
                "⚠️", "Lance d'abord un scan !")
            return

        try:
            from export_pdf import exporter_en_pdf
            date = datetime.now().strftime("%d-%m-%Y")
            nb = len(self._scan_images)
            nom_fichier = f"NOKIROVA_Scan_{nb}pages_{date}.pdf"
            titre = f"Scan Multi-pages ({nb} pages)"

            resultat = exporter_en_pdf(texte, titre, nom_fichier)
            if "Erreur" not in resultat:
                notification_succes(
                    self, "PDF créé !", f"📄 {nom_fichier}")
                messagebox.showinfo(
                    "✅ PDF créé",
                    f"📄 {nom_fichier}\n📁 {resultat}")
            else:
                messagebox.showerror("❌ Erreur", resultat)
        except Exception as e:
            messagebox.showerror("❌ Erreur", str(e))