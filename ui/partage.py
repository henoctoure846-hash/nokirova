# ui/partage.py - Partage de cours NOKIROVA 🤝

import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
import json
import zipfile
import os
from datetime import datetime
from db.base import get_connexion
import database as db
from ui.base import (
    VERT_EMERAUDE, VERT_HOVER, VERT_CLAIR, VERT_CORRECTION,
    VERT_FOND_CORRECTION,
    BLEU_ROYAL, BLEU_CIEL, BLEU_TRES_PALE,
    JAUNE_SOLEIL, JAUNE_CLAIR, JAUNE_PALE, OR_MODERNE,
    VIOLET_PREMIUM, VIOLET_LAVANDE, VIOLET_PALE,
    ROSE_SAKURA, ROSE_PALE,
    ORANGE_DORE, ORANGE_CLAIR, ORANGE_PALE,
    ROUGE, ROUGE_CLAIR,
    BLANC, BLANC_CASSE, GRIS_TEXTE, GRIS_DOUX, GRIS_PERLE
)
from notifications import notification_succes


DOSSIER_PARTAGES = "partages"
CONFIG_PARTAGE = "nokirova_partage.json"


class PartageMixin:

    # ═══════════════════════════════════════════
    # 🛠️ UTILITAIRES
    # ═══════════════════════════════════════════

    def _init_partage(self):
        """Crée le dossier partages si nécessaire"""
        if not os.path.exists(DOSSIER_PARTAGES):
            os.makedirs(DOSSIER_PARTAGES)

    def _get_createur(self):
        """Récupère ou demande le nom du créateur"""
        # Vérifier si déjà configuré
        if os.path.exists(CONFIG_PARTAGE):
            try:
                with open(CONFIG_PARTAGE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    nom = config.get("createur", "")
                    if nom:
                        return nom
            except Exception:
                pass

        # Demander le nom
        nom = simpledialog.askstring(
            "👤 Ton pseudo",
            "Quel nom veux-tu mettre sur tes partages ?\n\n"
            "💡 Ce nom sera visible par tes amis quand\n"
            "ils importeront tes cours.\n\n"
            "(Tu peux le changer plus tard)",
            initialvalue="Étudiant NOKIROVA",
            parent=self)

        if nom and nom.strip():
            nom = nom.strip()
            self._sauv_createur(nom)
            return nom
        return None

    def _sauv_createur(self, nom):
        """Sauvegarde le nom du créateur"""
        try:
            with open(CONFIG_PARTAGE, 'w', encoding='utf-8') as f:
                json.dump({"createur": nom}, f, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde créateur : {e}")

    # ═══════════════════════════════════════════
    # 📤 EXPORT D'UN COURS
    # ═══════════════════════════════════════════

    def _exporter_cours_nokirova(self, id_cours):
        """Exporte un cours complet en fichier .nokirova"""
        info = db.info_cours(id_cours)
        if not info:
            messagebox.showerror("❌", "Cours introuvable !")
            return

        # Demander le nom du créateur
        createur = self._get_createur()
        if not createur:
            return

        # Collecter les données
        data = self._collecter_donnees(info, createur)

        # Préparer le nom de fichier
        self._init_partage()
        nom_propre = info["nom"][:30].replace(" ", "_")
        nom_propre = "".join(
            c for c in nom_propre if c.isalnum() or c in "_-")
        if not nom_propre:
            nom_propre = "cours"
        date_str = datetime.now().strftime("%Y%m%d")
        nom_fichier = f"{nom_propre}_{date_str}.nokirova"

        # Demander où sauvegarder
        chemin = filedialog.asksaveasfilename(
            initialdir=DOSSIER_PARTAGES,
            defaultextension=".nokirova",
            initialfile=nom_fichier,
            title="💾 Sauvegarder le partage",
            filetypes=[("Fichier NOKIROVA", "*.nokirova")])

        if not chemin:
            return

        # Écrire le fichier ZIP
        try:
            with zipfile.ZipFile(
                    chemin, 'w', zipfile.ZIP_DEFLATED) as zf:
                contenu_json = json.dumps(
                    data, ensure_ascii=False, indent=2)
                zf.writestr("cours.json", contenu_json)

            taille_ko = round(os.path.getsize(chemin) / 1024, 1)
            stats = data["stats"]

            notification_succes(
                self, "Exporté ! 🤝",
                f"📦 {os.path.basename(chemin)}")

            messagebox.showinfo(
                "✅ Partage créé !",
                f"📦 Fichier : {os.path.basename(chemin)}\n"
                f"💾 Taille : {taille_ko} Ko\n\n"
                f"📚 Cours : {info['nom'][:40]}\n"
                f"📝 {stats['nb_notes']} note(s) incluse(s)\n"
                f"🃏 {stats['nb_flashcards']} flashcard(s)\n"
                f"📜 {stats['nb_historique']} historique(s)\n\n"
                f"👤 Créateur : {createur}\n\n"
                f"💡 Envoie ce fichier à tes amis !")

            self._recompenser(15, "Cours partagé ! 🤝")

        except Exception as e:
            messagebox.showerror(
                "❌ Erreur", f"Export échoué :\n{str(e)}")

    def _collecter_donnees(self, info, createur):
        """Collecte cours + notes + flashcards + historique"""
        matiere = info["matiere"]
        conn = get_connexion()
        cur = conn.cursor()

        # Notes liées (même matière)
        cur.execute(
            "SELECT titre, contenu, matiere, couleur "
            "FROM notes WHERE matiere = ?", (matiere,))
        notes = [{"titre": r[0], "contenu": r[1],
                  "matiere": r[2], "couleur": r[3]}
                 for r in cur.fetchall()]

        # Flashcards liées (même matière)
        cur.execute(
            "SELECT recto, verso, matiere, nom_deck "
            "FROM flashcards WHERE matiere = ?", (matiere,))
        flashcards = [{"recto": r[0], "verso": r[1],
                       "matiere": r[2], "deck": r[3]}
                      for r in cur.fetchall()]

        # Historique lié (même matière)
        cur.execute(
            "SELECT type, question, reponse, matiere "
            "FROM historique WHERE matiere = ?", (matiere,))
        historique = [{"type": r[0], "question": r[1],
                       "reponse": r[2], "matiere": r[3]}
                      for r in cur.fetchall()]

        conn.close()

        return {
            "version": "1.0",
            "type": "cours_nokirova",
            "createur": createur,
            "date_export": datetime.now().strftime(
                "%Y-%m-%d %H:%M"),
            "cours": {
                "nom": info["nom"],
                "matiere": info["matiere"],
                "contenu": info["contenu"]
            },
            "notes_liees": notes,
            "flashcards_liees": flashcards,
            "historique_lie": historique,
            "stats": {
                "nb_notes": len(notes),
                "nb_flashcards": len(flashcards),
                "nb_historique": len(historique),
                "taille_cours": len(info["contenu"])
                if info["contenu"] else 0
            }
        }

    # ═══════════════════════════════════════════
    # 📥 IMPORT D'UN FICHIER .nokirova
    # ═══════════════════════════════════════════

    def afficher_import_partage(self):
        """Ouvre un fichier .nokirova et affiche l'aperçu"""
        self._init_partage()

        chemin = filedialog.askopenfilename(
            title="📥 Importer un cours partagé",
            initialdir=DOSSIER_PARTAGES
            if os.path.exists(DOSSIER_PARTAGES) else ".",
            filetypes=[
                ("Fichier NOKIROVA", "*.nokirova"),
                ("Tous", "*.*")])

        if not chemin:
            return

        # Lire le fichier ZIP
        try:
            with zipfile.ZipFile(chemin, 'r') as zf:
                with zf.open("cours.json") as f:
                    data = json.loads(f.read().decode('utf-8'))
        except zipfile.BadZipFile:
            messagebox.showerror(
                "❌ Erreur",
                "Ce fichier est corrompu ou n'est pas\n"
                "un vrai fichier .nokirova !")
            return
        except KeyError:
            messagebox.showerror(
                "❌ Erreur",
                "Fichier .nokirova invalide !\n"
                "(cours.json manquant)")
            return
        except Exception as e:
            messagebox.showerror(
                "❌ Erreur",
                f"Impossible de lire ce fichier :\n{str(e)}")
            return

        # Vérifier le format
        if data.get("type") != "cours_nokirova":
            messagebox.showerror(
                "❌ Format invalide",
                "Ce n'est pas un fichier NOKIROVA valide !")
            return

        # Afficher l'aperçu
        self._apercu_import(data)

    def _apercu_import(self, data):
        """Popup d'aperçu avec toutes les infos"""
        popup = ctk.CTkToplevel(self)
        popup.title("📥 Aperçu du cours partagé")
        popup.geometry("550x680")
        popup.configure(fg_color=BLANC)
        popup.transient(self)

        scroll = ctk.CTkScrollableFrame(
            popup, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        # En-tête
        ctk.CTkLabel(
            scroll, text="📥  Aperçu avant import",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=VIOLET_PREMIUM).pack(pady=(0, 12))

        cours = data.get("cours", {})
        stats = data.get("stats", {})

        # ── Carte info ──
        carte = ctk.CTkFrame(
            scroll, fg_color=VIOLET_PALE, corner_radius=14)
        carte.pack(fill="x", pady=5)

        infos = [
            ("👤  Créateur", data.get("createur", "Inconnu")),
            ("📅  Date", data.get("date_export", "—")),
            ("📚  Cours", cours.get("nom", "Sans nom")),
            ("🎯  Matière", cours.get("matiere", "—")),
            ("📊  Taille",
             f"{stats.get('taille_cours', 0):,} car."),
            ("📦  Version", data.get("version", "1.0")),
        ]

        for label, valeur in infos:
            ligne = ctk.CTkFrame(carte, fg_color="transparent")
            ligne.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(
                ligne, text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=BLANC, width=130,
                anchor="w").pack(side="left")
            ctk.CTkLabel(
                ligne, text=str(valeur)[:50],
                font=ctk.CTkFont(size=12),
                text_color=BLANC, anchor="w").pack(
                side="left", padx=10)

        # Espace fin carte
        ctk.CTkLabel(carte, text="", height=5).pack()

        # ── Contenu inclus ──
        inclus = ctk.CTkFrame(
            scroll, fg_color=VERT_FOND_CORRECTION,
            corner_radius=12)
        inclus.pack(fill="x", pady=8)

        ctk.CTkLabel(
            inclus, text="📦  CONTENU INCLUS",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=VERT_CORRECTION).pack(pady=(10, 5))

        items = [
            ("📚  1 cours complet", VERT_EMERAUDE),
            (f"📝  {stats.get('nb_notes', 0)} note(s)",
             VIOLET_PREMIUM),
            (f"🃏  {stats.get('nb_flashcards', 0)} flashcard(s)",
             BLEU_ROYAL),
            (f"📜  {stats.get('nb_historique', 0)} historique(s)",
             ORANGE_DORE),
        ]
        for texte, couleur in items:
            ctk.CTkLabel(
                inclus, text=texte,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=couleur).pack(pady=2)
        ctk.CTkLabel(inclus, text="", height=5).pack()

        # ── Aperçu du contenu ──
        ctk.CTkLabel(
            scroll, text="📄  APERÇU DU CONTENU",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", pady=(10, 3))

        apercu_frame = ctk.CTkFrame(
            scroll, fg_color=GRIS_PERLE, corner_radius=10)
        apercu_frame.pack(fill="x", pady=3)

        contenu_brut = cours.get("contenu", "")
        contenu_apercu = contenu_brut[:800]
        if len(contenu_brut) > 800:
            contenu_apercu += "\n\n[... suite tronquée ...]"

        ctk.CTkLabel(
            apercu_frame, text=contenu_apercu or "(vide)",
            font=ctk.CTkFont(size=11),
            text_color=GRIS_TEXTE,
            wraplength=480, justify="left",
            anchor="nw").pack(padx=12, pady=12, fill="x")

        # ── Boutons ──
        btns = ctk.CTkFrame(scroll, fg_color="transparent")
        btns.pack(fill="x", pady=15)

        ctk.CTkButton(
            btns, text="✅  IMPORTER TOUT",
            command=lambda: self._confirmer_import(data, popup),
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=12).pack(
            side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            btns, text="❌  Annuler",
            command=popup.destroy,
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=12).pack(
            side="left", padx=5, expand=True, fill="x")

        # Espace bas
        ctk.CTkLabel(scroll, text="", height=10).pack()

    # ═══════════════════════════════════════════
    # ✅ CONFIRMATION IMPORT
    # ═══════════════════════════════════════════

    def _confirmer_import(self, data, popup):
        """Importe toutes les données"""
        try:
            cours = data.get("cours", {})
            createur = data.get("createur", "Inconnu")
            matiere = cours.get("matiere", "📚 Général")

            # 1. Importer le cours (SQL direct pour garder la matière)
            nom_cours = f"{cours.get('nom', 'Cours')} [de {createur}]"
            conn = get_connexion()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO cours (nom, matiere, contenu) "
                "VALUES (?, ?, ?)",
                (nom_cours, matiere,
                 cours.get("contenu", "")))
            conn.commit()
            conn.close()

            # 2. Importer les notes
            nb_notes = 0
            for note in data.get("notes_liees", []):
                try:
                    db.creer_note(
                        note.get("titre", "Note importée"),
                        note.get("contenu", ""),
                        note.get("matiere", matiere),
                        note.get("couleur", "#FFE66D"))
                    nb_notes += 1
                except Exception:
                    pass

            # 3. Importer les flashcards
            nb_fc = 0
            for fc in data.get("flashcards_liees", []):
                try:
                    db.creer_flashcard(
                        fc.get("recto", "?"),
                        fc.get("verso", "?"),
                        fc.get("matiere", matiere),
                        fc.get("deck", "Importé"))
                    nb_fc += 1
                except Exception:
                    pass

            # 4. Importer l'historique
            nb_hist = 0
            for h in data.get("historique_lie", []):
                try:
                    db.sauvegarder_historique(
                        h.get("type", "question_libre"),
                        h.get("question", ""),
                        h.get("reponse", ""),
                        h.get("matiere", matiere))
                    nb_hist += 1
                except Exception:
                    pass

            popup.destroy()

            notification_succes(
                self, "Importé ! 📥",
                f"📚 {nom_cours[:30]}")

            messagebox.showinfo(
                "✅ Import réussi !",
                f"📚 Cours : {nom_cours[:40]}\n"
                f"🎯 Matière : {matiere}\n\n"
                f"📝 {nb_notes} note(s) importée(s)\n"
                f"🃏 {nb_fc} flashcard(s) importée(s)\n"
                f"📜 {nb_hist} historique(s) importé(s)\n\n"
                f"👤 Par : {createur}\n\n"
                f"💡 Va dans ta Bibliothèque pour le voir !")

            self._recompenser(20, "Cours importé ! 📥")

            # Actualiser la bibliothèque
            if hasattr(self, 'afficher_bibliotheque'):
                self.afficher_bibliotheque()

        except Exception as e:
            messagebox.showerror(
                "❌ Erreur", f"Import échoué :\n{str(e)}")