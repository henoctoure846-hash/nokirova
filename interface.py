# interface.py - NOKIROVA 🌸 Spring Educational UI - VERSION EMBELLIE

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os

from ia_handler import demander_ia, expliquer_simplement, creer_resume
from document_parser import lire_document
from audio_generator import generer_audio
from exercice_generator import generer_qcm, generer_questions_cours, generer_exercices_examen
from ocr_handler import lire_image_et_expliquer
from export_pdf import exporter_en_pdf
from notifications import notification_xp, notification_badge, notification_succes
import database as db

# Init DB
db.init_db()
db.maj_streak()

# Thème
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# ═══════════════════════════════════════════
# 🎨 PALETTE
# ═══════════════════════════════════════════
VERT_PRINTEMPS = "#7ED321"
VERT_HOVER = "#8BCF3F"
VERT_CLAIR = "#9FD93B"
VERT_EMERAUDE = "#00C853"

JAUNE_SOLEIL = "#FFD93D"
JAUNE_CLAIR = "#FFE66D"
JAUNE_PALE = "#FFF3B0"
OR_MODERNE = "#FFB800"

BLEU_CIEL = "#7EC8FF"
BLEU_PALE = "#A5D8FF"
BLEU_TRES_PALE = "#D0EBFF"
BLEU_ROYAL = "#2962FF"

ROSE_SAKURA = "#FFC9DE"
ROSE_CLAIR = "#FFD6E8"
ROSE_PALE = "#FFE5EF"

VIOLET_LAVANDE = "#A855F7"
VIOLET_CLAIR = "#C084FC"
VIOLET_PALE = "#D8B4FE"
VIOLET_PREMIUM = "#7B61FF"

ORANGE_DORE = "#F59E0B"
ORANGE_CLAIR = "#FB923C"
ORANGE_PALE = "#FDBA74"

BLANC = "#FFFFFF"
BLANC_CASSE = "#FAFAFA"
GRIS_PERLE = "#F8F9FA"
GRIS_TEXTE = "#374151"
GRIS_DOUX = "#9CA3AF"

# Thème sombre
NOIR_FOND = "#1A1B26"
NOIR_CARTE = "#24283B"
GRIS_FONCE = "#414868"
BLANC_DOUX = "#C0CAF5"


class NokirovaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🌸 NOKIROVA - Ton Prof Intelligent")
        self.geometry("1250x800")
        self.configure(fg_color=BLANC_CASSE)
        self.minsize(1050, 680)

        # Variables
        self.cours_actuel = ""
        self.nom_cours = "Aucun cours chargé"
        self.matiere_detectee = ""
        self.mode_sombre = False
        self.dernier_contenu = ""  # Pour export PDF

        self.creer_sidebar()
        self.creer_zone_principale()
        self.afficher_accueil()
        self.bind_raccourcis()

    def bind_raccourcis(self):
        """Raccourcis clavier"""
        self.bind("<Control-h>", lambda e: self.afficher_accueil())
        self.bind("<Control-i>", lambda e: self.afficher_import())
        self.bind("<Control-q>", lambda e: self.afficher_qcm())
        self.bind("<Control-r>", lambda e: self.afficher_resume())
        self.bind("<Control-d>", lambda e: self.toggle_mode_sombre())
        self.bind("<F1>", lambda e: self.afficher_aide())

    # ═══════════════════════════════════════════
    # 🌙 MODE JOUR/NUIT
    # ═══════════════════════════════════════════
    def toggle_mode_sombre(self):
        self.mode_sombre = not self.mode_sombre
        if self.mode_sombre:
            ctk.set_appearance_mode("dark")
            self.configure(fg_color=NOIR_FOND)
        else:
            ctk.set_appearance_mode("light")
            self.configure(fg_color=BLANC_CASSE)
        notification_succes(self, "Mode changé",
                            "🌙 Mode sombre activé" if self.mode_sombre else "☀️ Mode jour activé")

    # ═══════════════════════════════════════════
    # 🌿 SIDEBAR
    # ═══════════════════════════════════════════
    def creer_sidebar(self):
        self.sidebar = ctk.CTkScrollableFrame(self, width=280, fg_color=VERT_PRINTEMPS, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        # Logo avec halo
        halo = ctk.CTkFrame(self.sidebar, fg_color=JAUNE_CLAIR, corner_radius=20, height=120)
        halo.pack(fill="x", padx=10, pady=(15, 10))
        halo.pack_propagate(False)

        ctk.CTkLabel(halo, text="🌸 NOKIROVA",
                     font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                     text_color=GRIS_TEXTE).pack(pady=(18, 0))

        ctk.CTkLabel(halo, text="✨ Ton Prof Intelligent ✨",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=GRIS_TEXTE).pack()

        # Mode sombre
        btn_mode = ctk.CTkButton(halo, text="🌙 / ☀️",
                                 command=self.toggle_mode_sombre,
                                 fg_color="transparent", text_color=GRIS_TEXTE,
                                 hover_color=JAUNE_PALE,
                                 font=ctk.CTkFont(size=10), height=22,
                                 corner_radius=8)
        btn_mode.pack(pady=(2, 5))

        # Menu
        boutons = [
            ("🏠  Accueil", self.afficher_accueil, BLANC),
            ("🏆  Mon Profil", self.afficher_profil, JAUNE_CLAIR),
            ("📥  Importer un cours", self.afficher_import, BLEU_CIEL),
            ("📸  Scanner une image", self.afficher_ocr, VERT_CLAIR),
            ("📝  Résumé", self.afficher_resume, BLEU_PALE),
            ("💡  Explication simple", self.afficher_explication, JAUNE_CLAIR),
            ("🎯  QCM", self.afficher_qcm, ROSE_CLAIR),
            ("❓  Questions de cours", self.afficher_questions, ROSE_SAKURA),
            ("📚  Exercices examen", self.afficher_examen, ORANGE_CLAIR),
            ("🎧  Audio", self.afficher_audio, VIOLET_CLAIR),
            ("💬  Question libre", self.afficher_chat, VIOLET_LAVANDE),
            ("⌨️  Aide / Raccourcis", self.afficher_aide, ROSE_CLAIR),
        ]

        for texte, commande, couleur in boutons:
            btn = ctk.CTkButton(
                self.sidebar, text=texte, command=commande,
                fg_color=BLANC, text_color=GRIS_TEXTE,
                hover_color=couleur, anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                height=40, corner_radius=12, border_width=0
            )
            btn.pack(fill="x", padx=10, pady=3)

        # Statut cours
        carte_statut = ctk.CTkFrame(self.sidebar, fg_color=ROSE_PALE, corner_radius=15)
        carte_statut.pack(fill="x", padx=10, pady=15)

        ctk.CTkLabel(carte_statut, text="📚 COURS ACTUEL",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=GRIS_TEXTE).pack(pady=(10, 2))

        self.statut_label = ctk.CTkLabel(carte_statut, text=self.nom_cours,
                                         font=ctk.CTkFont(size=11),
                                         text_color=VIOLET_PREMIUM, wraplength=210)
        self.statut_label.pack(pady=(0, 10), padx=10)

    # ═══════════════════════════════════════════
    # ZONE PRINCIPALE
    # ═══════════════════════════════════════════
    def creer_zone_principale(self):
        self.zone_principale = ctk.CTkFrame(self, fg_color=BLANC_CASSE)
        self.zone_principale.pack(side="right", fill="both", expand=True, padx=25, pady=25)

    def vider_zone(self):
        for widget in self.zone_principale.winfo_children():
            widget.destroy()

    def afficher_titre(self, texte, emoji="🌸", couleur=VERT_EMERAUDE):
        carte_titre = ctk.CTkFrame(self.zone_principale, fg_color=couleur, corner_radius=18, height=75)
        carte_titre.pack(fill="x", pady=(0, 15))
        carte_titre.pack_propagate(False)

        ctk.CTkLabel(carte_titre, text=f"{emoji}  {texte}",
                     font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                     text_color=BLANC).pack(pady=18)

    def creer_zone_texte(self, hauteur=400):
        cadre = ctk.CTkFrame(self.zone_principale, fg_color=BLANC, corner_radius=18,
                             border_width=2, border_color=BLEU_TRES_PALE)
        cadre.pack(fill="both", expand=True, pady=10)

        zone = ctk.CTkTextbox(cadre, height=hauteur, fg_color=BLANC,
                              text_color=GRIS_TEXTE,
                              font=ctk.CTkFont(family="Segoe UI", size=14),
                              corner_radius=15, wrap="word", border_width=0)
        zone.pack(fill="both", expand=True, padx=15, pady=15)
        return zone

    def creer_bouton_action(self, parent, texte, commande, couleur=VERT_EMERAUDE, hover=VERT_HOVER):
        return ctk.CTkButton(
            parent, text=texte, command=commande,
            fg_color=couleur, text_color=BLANC, hover_color=hover,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            height=48, corner_radius=14
        )

    def creer_bouton_export(self, contenu: str, nom: str = "document"):
        """Crée un bouton pour exporter en PDF"""
        return ctk.CTkButton(
            self.zone_principale, text="💾  Exporter en PDF",
            command=lambda: self._exporter(contenu, nom),
            fg_color=OR_MODERNE, text_color=BLANC, hover_color=ORANGE_CLAIR,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38, corner_radius=12
        )

    def _exporter(self, contenu_widget, nom: str):
        """Exporte un widget en PDF avec NOMMAGE INTELLIGENT"""
        if hasattr(contenu_widget, 'get'):
            texte = contenu_widget.get("0.0", "end").strip()
        else:
            texte = str(contenu_widget)

        if not texte or "⚠️" in texte[:20]:
            messagebox.showwarning("⚠️", "Rien à exporter ! Génère du contenu d'abord.")
            return

        from datetime import datetime

        # 🧠 NOMMAGE INTELLIGENT
        date_simple = datetime.now().strftime('%d-%m-%Y')

        # Récupérer la matière (sans emoji)
        matiere_propre = "General"
        if self.matiere_detectee:
            # Enlever les emojis du début
            matiere_temp = self.matiere_detectee.strip()
            # Garder uniquement les lettres et espaces
            import re
            matiere_propre = re.sub(r'[^\w\sàâäéèêëïîôöùûüÿç-]', '', matiere_temp).strip()
            matiere_propre = matiere_propre.replace(' ', '_')[:30]
            if not matiere_propre:
                matiere_propre = "General"

        # Type de document
        types_nom = {
            "resume": "Resume",
            "explication": "Explication",
            "qcm": "QCM",
            "questions": "Questions",
            "examen": "Examen",
            "ocr": "Scan",
            "reponse": "Reponse_IA"
        }
        type_doc = types_nom.get(nom, nom.title())

        # Construire le nom final
        nom_fichier = f"NOKIROVA_{type_doc}_{matiere_propre}_{date_simple}.pdf"

        # Titre du document (pour la page de garde)
        titre_doc = f"{type_doc} - {matiere_propre.replace('_', ' ')}"

        resultat = exporter_en_pdf(texte, titre_doc, nom_fichier)

        if "Erreur" not in resultat and "❌" not in resultat:
            # Cas 1 : 2 PDFs (exos + corrections)
            if "2 PDFs créés" in resultat:
                notification_succes(self, "2 PDFs créés !", "📝 Exercices + ✅ Corrigé")
                messagebox.showinfo("✅ 2 PDFs créés",
                                    f"🎉 NOKIROVA a généré 2 fichiers :\n\n"
                                    f"📝 {type_doc} EXERCICES (pour t'entraîner)\n"
                                    f"✅ {type_doc} CORRECTION (à consulter après)\n\n"
                                    f"📁 Emplacement : dossier 'outputs/'\n\n"
                                    f"💪 Astuce : fais les exos AVANT de regarder le corrigé !")
            # Cas 2 : 1 PDF simple
            else:
                notification_succes(self, "PDF exporté !", f"📄 {type_doc}")
                messagebox.showinfo("✅ PDF créé",
                                    f"📄 Ton PDF a été créé !\n\n"
                                    f"📝 Nom : {nom_fichier}\n\n"
                                    f"📁 Emplacement :\n{resultat}\n\n"
                                    f"Double-clique pour l'ouvrir 📄")
        else:
            messagebox.showerror("❌ Erreur", resultat)

    def _recompenser(self, points: int, message: str = ""):
        """Donne XP + notification + vérifie badges"""
        ancien_niveau = db.get_stats()["niveau"]
        db.ajouter_xp(points)
        nouveau_niveau = db.get_stats()["niveau"]

        notification_xp(self, points, message)

        # Niveau up ?
        if nouveau_niveau > ancien_niveau:
            self.after(2500, lambda: notification_succes(
                self, f"NIVEAU {nouveau_niveau} !",
                f"🎉 Tu es maintenant {db.get_niveau_titre(nouveau_niveau)} !"))

        # Nouveaux badges ?
        nouveaux = db.verifier_badges()
        for i, badge in enumerate(nouveaux):
            self.after(3000 + i * 4000, lambda b=badge: notification_badge(
                self, b["emoji"], b["nom"], b["description"]))

    # ═══════════════════════════════════════════
    # 🏠 ACCUEIL
    # ═══════════════════════════════════════════
    def afficher_accueil(self):
        self.vider_zone()

        hero = ctk.CTkFrame(self.zone_principale, fg_color=BLEU_TRES_PALE, corner_radius=20, height=140)
        hero.pack(fill="x", pady=(0, 15))
        hero.pack_propagate(False)

        ctk.CTkLabel(hero, text="🌸 Bienvenue dans NOKIROVA !",
                     font=ctk.CTkFont(size=30, weight="bold"),
                     text_color=VIOLET_PREMIUM).pack(pady=(25, 5))

        ctk.CTkLabel(hero, text="✨ Ton professeur intelligent personnel ✨",
                     font=ctk.CTkFont(size=14),
                     text_color=GRIS_TEXTE).pack()

        # Mini stats
        stats = db.get_stats()
        mini_stats = ctk.CTkFrame(self.zone_principale, fg_color="transparent")
        mini_stats.pack(fill="x", pady=5)

        carte_xp = ctk.CTkFrame(mini_stats, fg_color=JAUNE_CLAIR, corner_radius=12, height=70)
        carte_xp.pack(side="left", padx=5, expand=True, fill="x")
        carte_xp.pack_propagate(False)
        ctk.CTkLabel(carte_xp, text=f"⭐ Niveau {stats['niveau']}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=GRIS_TEXTE).pack(pady=(12, 0))
        ctk.CTkLabel(carte_xp, text=f"{stats['xp']} XP",
                     font=ctk.CTkFont(size=12),
                     text_color=GRIS_TEXTE).pack()

        carte_streak = ctk.CTkFrame(mini_stats, fg_color=ORANGE_CLAIR, corner_radius=12, height=70)
        carte_streak.pack(side="left", padx=5, expand=True, fill="x")
        carte_streak.pack_propagate(False)
        ctk.CTkLabel(carte_streak, text=f"🔥 {stats['streak']} jour(s)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=BLANC).pack(pady=(12, 0))
        ctk.CTkLabel(carte_streak, text="Streak quotidien",
                     font=ctk.CTkFont(size=11),
                     text_color=BLANC).pack()

        carte_cours = ctk.CTkFrame(mini_stats, fg_color=VERT_CLAIR, corner_radius=12, height=70)
        carte_cours.pack(side="left", padx=5, expand=True, fill="x")
        carte_cours.pack_propagate(False)
        ctk.CTkLabel(carte_cours, text=f"📚 {stats['cours_importes']}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=BLANC).pack(pady=(12, 0))
        ctk.CTkLabel(carte_cours, text="Cours importés",
                     font=ctk.CTkFont(size=11),
                     text_color=BLANC).pack()

        # Cartes fonctionnalités
        grille = ctk.CTkFrame(self.zone_principale, fg_color="transparent")
        grille.pack(fill="x", pady=10)

        cartes_data = [
            ("📥", "Importer", BLEU_CIEL, self.afficher_import),
            ("📸", "Scanner", VERT_CLAIR, self.afficher_ocr),
            ("🎯", "QCM", ROSE_SAKURA, self.afficher_qcm),
            ("📚", "Examens", ORANGE_CLAIR, self.afficher_examen),
        ]

        for i, (emoji, titre, couleur, cmd) in enumerate(cartes_data):
            carte = ctk.CTkFrame(grille, fg_color=couleur, corner_radius=16, width=200, height=110)
            carte.grid(row=0, column=i, padx=6, pady=10, sticky="nsew")
            carte.pack_propagate(False)
            grille.grid_columnconfigure(i, weight=1)

            ctk.CTkLabel(carte, text=emoji, font=ctk.CTkFont(size=32)).pack(pady=(12, 2))
            ctk.CTkLabel(carte, text=titre, font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=GRIS_TEXTE).pack()
            btn = ctk.CTkButton(carte, text="→ Ouvrir", command=cmd,
                                fg_color=BLANC, text_color=GRIS_TEXTE,
                                hover_color=BLANC_CASSE, height=26,
                                font=ctk.CTkFont(size=11, weight="bold"),
                                corner_radius=10)
            btn.pack(pady=5)

        # Objectif
        objectif = ctk.CTkFrame(self.zone_principale, fg_color=JAUNE_PALE, corner_radius=16)
        objectif.pack(fill="x", pady=10)

        ctk.CTkLabel(objectif, text="🎯 OBJECTIF DU JOUR",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=ORANGE_DORE).pack(pady=(15, 5))

        ctk.CTkLabel(objectif,
                     text="💪 Importe un cours et fais au moins 5 QCM !\nTu vas y arriver ! 🌟",
                     font=ctk.CTkFont(size=13), text_color=GRIS_TEXTE).pack(pady=(0, 15))

        btn_start = self.creer_bouton_action(self.zone_principale,
                                             "🚀  COMMENCER MAINTENANT",
                                             self.afficher_import,
                                             VERT_EMERAUDE, VERT_HOVER)
        btn_start.pack(pady=10, fill="x")

    # ═══════════════════════════════════════════
    # ⌨️ AIDE / RACCOURCIS
    # ═══════════════════════════════════════════
    def afficher_aide(self):
        self.vider_zone()
        self.afficher_titre("Aide & Raccourcis", "⌨️", VIOLET_PREMIUM)

        aide = self.creer_zone_texte(500)
        aide.insert("0.0", """🌸 BIENVENUE DANS L'AIDE NOKIROVA 🌸

⌨️ RACCOURCIS CLAVIER :
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ctrl + H    →  Accueil
Ctrl + I    →  Importer un cours
Ctrl + R    →  Résumé
Ctrl + Q    →  QCM
Ctrl + D    →  Mode sombre / jour
F1          →  Cette page d'aide
━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 CONSEILS D'UTILISATION :

1️⃣ COMMENCE par importer un cours (PDF, Word, PPT)
   → NOKIROVA détecte automatiquement la matière !

2️⃣ DEMANDE un résumé pour avoir l'essentiel rapidement

3️⃣ TESTE-toi avec des QCM (commence par 5)

4️⃣ ENTRAÎNE-toi avec les exercices examen
   → 4 niveaux : Débutant → Ultra difficile

5️⃣ CRÉE des audios pour réviser en marchant 🎧

6️⃣ SCANNE tes cours en photo (📸) si tu n'as pas le PDF

7️⃣ POSE n'importe quelle question (💬) sur n'importe quel sujet

🎮 GAMIFICATION :
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• +10 XP par cours importé
• +5 XP par question posée
• +8 XP par audio créé
• +15 XP par image scannée
• +5 XP par résumé/explication
• +2 XP par QCM généré
• +5 XP par exercice examen
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 OBJECTIFS :
• Atteindre le niveau 10 (Expert ⭐)
• Atteindre le niveau 25 (Maître 👑)
• Streak de 7 jours (Inarrêtable 🚀)
• Streak de 30 jours (Légende 🏆)

💪 RAPPEL : Tu peux le faire !
Régularité > Intensité.
Mieux vaut 10 min/jour que 3h/semaine.

✨ Bonne révision avec NOKIROVA ! 🌸
""")

    # ═══════════════════════════════════════════
    # 🏆 PROFIL
    # ═══════════════════════════════════════════
    def afficher_profil(self):
        self.vider_zone()
        self.afficher_titre("Mon Profil", "🏆", VIOLET_PREMIUM)

        stats = db.get_stats()
        titre_niveau = db.get_niveau_titre(stats["niveau"])

        carte_niveau = ctk.CTkFrame(self.zone_principale, fg_color=JAUNE_PALE, corner_radius=18)
        carte_niveau.pack(fill="x", pady=8)

        ctk.CTkLabel(carte_niveau, text=titre_niveau,
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=ORANGE_DORE).pack(pady=(20, 5))

        ctk.CTkLabel(carte_niveau, text=f"⭐ Niveau {stats['niveau']}",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=GRIS_TEXTE).pack()

        ctk.CTkLabel(carte_niveau, text=f"✨ {stats['xp']} XP",
                     font=ctk.CTkFont(size=15),
                     text_color=GRIS_TEXTE).pack()

        xp_actuel = stats["xp"] % 100
        progress = ctk.CTkProgressBar(carte_niveau, progress_color=VERT_EMERAUDE,
                                      fg_color=BLANC, height=20, corner_radius=10)
        progress.set(xp_actuel / 100)
        progress.pack(pady=10, padx=30, fill="x")

        ctk.CTkLabel(carte_niveau,
                     text=f"🎯 {xp_actuel}/100 XP vers le niveau {stats['niveau'] + 1}",
                     font=ctk.CTkFont(size=12),
                     text_color=GRIS_TEXTE).pack(pady=(0, 15))

        carte_streak = ctk.CTkFrame(self.zone_principale, fg_color=ORANGE_CLAIR, corner_radius=15)
        carte_streak.pack(fill="x", pady=8)
        ctk.CTkLabel(carte_streak,
                     text=f"🔥 STREAK : {stats['streak']} jour(s) consécutif(s) !",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=BLANC).pack(pady=15)

        carte_stats = ctk.CTkFrame(self.zone_principale, fg_color=BLEU_TRES_PALE, corner_radius=15)
        carte_stats.pack(fill="x", pady=8)

        ctk.CTkLabel(carte_stats, text="📊 TES STATISTIQUES",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=BLEU_ROYAL).pack(pady=(15, 5))

        stats_texte = (
            f"📚 Cours importés : {stats['cours_importes']}\n"
            f"💬 Questions posées : {stats['questions_posees']}\n"
            f"🎧 Audios créés : {stats['audios_crees']}\n"
            f"🎯 QCM réussis : {stats['qcm_reussis']}"
        )
        ctk.CTkLabel(carte_stats, text=stats_texte,
                     font=ctk.CTkFont(size=13), text_color=GRIS_TEXTE,
                     justify="left").pack(pady=(0, 15))

        badges = db.lister_badges()
        carte_badges = ctk.CTkFrame(self.zone_principale, fg_color=ROSE_PALE, corner_radius=15)
        carte_badges.pack(fill="both", expand=True, pady=8)

        ctk.CTkLabel(carte_badges, text=f"🏆 BADGES DÉBLOQUÉS ({len(badges)})",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=VIOLET_PREMIUM).pack(pady=(15, 10))

        if badges:
            scrollable = ctk.CTkScrollableFrame(carte_badges, fg_color="transparent", height=130)
            scrollable.pack(fill="both", expand=True, padx=15, pady=(0, 15))

            for nom, desc, emoji, date in badges:
                badge_frame = ctk.CTkFrame(scrollable, fg_color=BLANC, corner_radius=10)
                badge_frame.pack(fill="x", pady=4)

                ctk.CTkLabel(badge_frame, text=f"{emoji}  {nom}",
                             font=ctk.CTkFont(size=14, weight="bold"),
                             text_color=GRIS_TEXTE).pack(anchor="w", padx=15, pady=(8, 0))
                ctk.CTkLabel(badge_frame, text=desc,
                             font=ctk.CTkFont(size=11),
                             text_color=GRIS_DOUX).pack(anchor="w", padx=15, pady=(0, 8))
        else:
            ctk.CTkLabel(carte_badges,
                         text="🎯 Continue à utiliser NOKIROVA pour débloquer des badges !",
                         font=ctk.CTkFont(size=13),
                         text_color=GRIS_TEXTE).pack(pady=20)

    # ═══════════════════════════════════════════
    # 📥 IMPORT
    # ═══════════════════════════════════════════
    def afficher_import(self):
        self.vider_zone()
        self.afficher_titre("Importer un cours", "📥", BLEU_ROYAL)

        info_card = ctk.CTkFrame(self.zone_principale, fg_color=BLEU_TRES_PALE, corner_radius=12)
        info_card.pack(fill="x", pady=5)

        ctk.CTkLabel(info_card,
                     text="📄 Formats : PDF • Word • PowerPoint • TXT\n"
                          "🔍 NOKIROVA détecte automatiquement la matière !",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=BLEU_ROYAL, justify="center").pack(pady=12)

        btn = self.creer_bouton_action(self.zone_principale, "📁  Choisir un fichier",
                                       self.charger_fichier, BLEU_ROYAL, BLEU_CIEL)
        btn.pack(pady=15, fill="x")

        self.zone_apercu = self.creer_zone_texte(400)
        self.zone_apercu.insert("0.0",
                                "📄 L'aperçu du cours apparaîtra ici après import...\n\n"
                                "💡 Astuce : utilise Ctrl+I pour ouvrir cette page rapidement !")

    def charger_fichier(self):
        chemin = filedialog.askopenfilename(
            title="Choisis ton cours",
            filetypes=[("Tous les supportés", "*.pdf *.docx *.pptx *.txt"),
                       ("PDF", "*.pdf"), ("Word", "*.docx"),
                       ("PowerPoint", "*.pptx"), ("Texte", "*.txt")]
        )
        if chemin:
            self.zone_apercu.delete("0.0", "end")
            self.zone_apercu.insert("0.0",
                                    "⏳ Lecture du fichier...\n🔍 Détection automatique de la matière...\n🧠 NOKIROVA analyse...")
            self.update()

            self.cours_actuel = lire_document(chemin)
            self.nom_cours = os.path.basename(chemin)

            def tache():
                matiere = db.sauvegarder_cours(self.nom_cours, self.cours_actuel)
                self.matiere_detectee = matiere
                self.statut_label.configure(text=f"{matiere}\n{self.nom_cours[:25]}")

                self.zone_apercu.delete("0.0", "end")
                self.zone_apercu.insert("0.0",
                                        f"✅ Cours chargé avec succès !\n\n"
                                        f"🎯 MATIÈRE DÉTECTÉE : {matiere}\n"
                                        f"📁 Fichier : {self.nom_cours}\n"
                                        f"📊 Taille : {len(self.cours_actuel)} caractères\n\n"
                                        f"═══ APERÇU DU CONTENU ═══\n\n{self.cours_actuel[:2000]}...")

                self._recompenser(10, f"Cours chargé : {matiere}")

            threading.Thread(target=tache, daemon=True).start()

    # ═══════════════════════════════════════════
    # 📸 OCR
    # ═══════════════════════════════════════════
    def afficher_ocr(self):
        self.vider_zone()
        self.afficher_titre("Scanner une image", "📸", VERT_EMERAUDE)

        info = ctk.CTkFrame(self.zone_principale, fg_color=VERT_CLAIR, corner_radius=12)
        info.pack(fill="x", pady=5)

        ctk.CTkLabel(info,
                     text="📸 Prends en photo un cours, un exercice...\n"
                          "NOKIROVA va LIRE et EXPLIQUER ! 🤖✨",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=BLANC, justify="center").pack(pady=12)

        btn = self.creer_bouton_action(self.zone_principale,
                                       "📁  Choisir une image",
                                       self._scanner_image,
                                       VERT_EMERAUDE, VERT_HOVER)
        btn.pack(pady=15, fill="x")

        self.zone_ocr = self.creer_zone_texte(380)
        self.zone_ocr.insert("0.0", "📸 Sélectionne une image ci-dessus...")

        btn_pdf = self.creer_bouton_export(self.zone_ocr, "ocr")
        btn_pdf.pack(pady=5)

    def _scanner_image(self):
        chemin = filedialog.askopenfilename(
            title="Choisis une image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")]
        )
        if chemin:
            self.zone_ocr.delete("0.0", "end")
            self.zone_ocr.insert("0.0", "⏳ Lecture... 🔍\n⏳ Analyse IA... 🧠")
            self.update()

            def tache():
                resultat = lire_image_et_expliquer(chemin)
                self.zone_ocr.delete("0.0", "end")
                self.zone_ocr.insert("0.0", resultat)
                self._recompenser(15, "Image scannée !")

            threading.Thread(target=tache, daemon=True).start()

    # ═══════════════════════════════════════════
    # 📝 RÉSUMÉ / 💡 EXPLICATION
    # ═══════════════════════════════════════════
    def afficher_resume(self):
        self.vider_zone()
        self.afficher_titre("Résumé du cours", "📝", BLEU_ROYAL)
        self._page_generation(creer_resume, "📝  Générer le résumé", BLEU_ROYAL, BLEU_CIEL, "resume")

    def afficher_explication(self):
        self.vider_zone()
        self.afficher_titre("Explication simplifiée", "💡", ORANGE_DORE)
        self._page_generation(expliquer_simplement, "💡  Expliquer simplement", ORANGE_DORE, ORANGE_CLAIR, "explication")

    def _page_generation(self, fonction, texte_btn, couleur, hover, nom_export):
        btn = self.creer_bouton_action(self.zone_principale, texte_btn,
                                       lambda: self._generer(fonction, self.zone_resultat),
                                       couleur, hover)
        btn.pack(pady=10, fill="x")

        self.zone_resultat = self.creer_zone_texte(380)
        if not self.cours_actuel:
            self.zone_resultat.insert("0.0", "⚠️ Importe d'abord un cours !")
        else:
            self.zone_resultat.insert("0.0",
                                      f"👆 Clique sur le bouton pour générer !\n\n📚 Cours chargé : {self.nom_cours}")

        btn_pdf = self.creer_bouton_export(self.zone_resultat, nom_export)
        btn_pdf.pack(pady=5)

    def _generer(self, fonction, zone_affichage):
        if not self.cours_actuel:
            messagebox.showwarning("⚠️", "Importe d'abord un cours !")
            return
        zone_affichage.delete("0.0", "end")
        zone_affichage.insert("0.0", "⏳ NOKIROVA réfléchit... 🧠✨")
        self.update()

        def tache():
            res = fonction(self.cours_actuel[:5000])
            zone_affichage.delete("0.0", "end")
            zone_affichage.insert("0.0", res)
            self._recompenser(5)

        threading.Thread(target=tache, daemon=True).start()

    # ═══════════════════════════════════════════
    # 🎯 QCM
    # ═══════════════════════════════════════════
    def afficher_qcm(self):
        self.vider_zone()
        self.afficher_titre("Générer des QCM", "🎯", VIOLET_PREMIUM)

        frame = ctk.CTkFrame(self.zone_principale, fg_color=ROSE_PALE, corner_radius=14)
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(frame, text="🎚️  Nombre :", text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=15, pady=15)

        self.nb_qcm = ctk.CTkSlider(frame, from_=1, to=20, number_of_steps=19,
                                    progress_color=VIOLET_LAVANDE, button_color=VIOLET_PREMIUM)
        self.nb_qcm.set(5)
        self.nb_qcm.pack(side="left", padx=10, pady=15, fill="x", expand=True)

        self.label_nb = ctk.CTkLabel(frame, text="5", text_color=VIOLET_PREMIUM,
                                     font=ctk.CTkFont(size=20, weight="bold"))
        self.label_nb.pack(side="left", padx=15)
        self.nb_qcm.configure(command=lambda v: self.label_nb.configure(text=str(int(v))))

        btn = self.creer_bouton_action(self.zone_principale, "🎯  Générer les QCM",
                                       self._generer_qcm, VIOLET_PREMIUM, VIOLET_LAVANDE)
        btn.pack(pady=15, fill="x")

        self.zone_qcm = self.creer_zone_texte(320)
        if not self.cours_actuel:
            self.zone_qcm.insert("0.0", "⚠️ Importe d'abord un cours !")

        btn_pdf = self.creer_bouton_export(self.zone_qcm, "qcm")
        btn_pdf.pack(pady=5)

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
            self.zone_qcm.delete("0.0", "end")
            self.zone_qcm.insert("0.0", res)
            self._recompenser(nb * 2, f"{nb} QCM générés !")

        threading.Thread(target=tache, daemon=True).start()

    # ═══════════════════════════════════════════
    # ❓ QUESTIONS
    # ═══════════════════════════════════════════
    def afficher_questions(self):
        self.vider_zone()
        self.afficher_titre("Questions de cours", "❓", VIOLET_LAVANDE)

        frame = ctk.CTkFrame(self.zone_principale, fg_color=ROSE_SAKURA, corner_radius=14)
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(frame, text="🎚️  Nombre :", text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=15, pady=15)

        self.nb_q = ctk.CTkSlider(frame, from_=1, to=15, number_of_steps=14,
                                  progress_color=VIOLET_LAVANDE, button_color=VIOLET_PREMIUM)
        self.nb_q.set(5)
        self.nb_q.pack(side="left", padx=10, pady=15, fill="x", expand=True)

        lbl = ctk.CTkLabel(frame, text="5", text_color=VIOLET_PREMIUM,
                           font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(side="left", padx=15)
        self.nb_q.configure(command=lambda v: lbl.configure(text=str(int(v))))

        btn = self.creer_bouton_action(self.zone_principale, "❓  Générer",
                                       self._gen_q, VIOLET_LAVANDE, VIOLET_PREMIUM)
        btn.pack(pady=15, fill="x")

        self.zone_q = self.creer_zone_texte(320)
        if not self.cours_actuel:
            self.zone_q.insert("0.0", "⚠️ Importe d'abord un cours !")

        btn_pdf = self.creer_bouton_export(self.zone_q, "questions")
        btn_pdf.pack(pady=5)

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
            self.zone_q.delete("0.0", "end")
            self.zone_q.insert("0.0", res)
            self._recompenser(nb * 2, f"{nb} questions générées !")

        threading.Thread(target=tache, daemon=True).start()

    # ═══════════════════════════════════════════
    # 📚 EXAMEN
    # ═══════════════════════════════════════════
    def afficher_examen(self):
        self.vider_zone()
        self.afficher_titre("Exercices type Examen", "📚", ORANGE_DORE)

        frame = ctk.CTkFrame(self.zone_principale, fg_color=JAUNE_PALE, corner_radius=14)
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(frame, text="🎓  Niveau :", text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=15, pady=15)

        self.niveau = ctk.CTkOptionMenu(
            frame,
            values=["🟢 Débutant", "🟡 Intermédiaire", "🟠 Difficile", "🔴 Ultra difficile"],
            fg_color=ORANGE_DORE, text_color=BLANC, button_color=ORANGE_CLAIR,
            button_hover_color=ORANGE_PALE,
            dropdown_fg_color=BLANC, dropdown_text_color=GRIS_TEXTE,
            font=ctk.CTkFont(size=13, weight="bold"), corner_radius=10
        )
        self.niveau.pack(side="left", padx=10, pady=15)

        ctk.CTkLabel(frame, text="📊  Nombre :", text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(20, 5))

        self.nb_ex = ctk.CTkOptionMenu(frame, values=["1", "2", "3", "5", "10"],
                                       fg_color=ORANGE_DORE, text_color=BLANC,
                                       button_color=ORANGE_CLAIR, corner_radius=10)
        self.nb_ex.set("3")
        self.nb_ex.pack(side="left", padx=10)

        btn = self.creer_bouton_action(self.zone_principale, "📚  Générer les exercices",
                                       self._gen_examen, ORANGE_DORE, ORANGE_CLAIR)
        btn.pack(pady=15, fill="x")

        self.zone_ex = self.creer_zone_texte(290)
        if not self.cours_actuel:
            self.zone_ex.insert("0.0", "⚠️ Importe d'abord un cours !")

        btn_pdf = self.creer_bouton_export(self.zone_ex, "examen")
        btn_pdf.pack(pady=5)

    def _gen_examen(self):
        if not self.cours_actuel:
            messagebox.showwarning("⚠️", "Importe d'abord un cours !")
            return
        niveaux_map = {
            "🟢 Débutant": "debutant", "🟡 Intermédiaire": "intermediaire",
            "🟠 Difficile": "difficile", "🔴 Ultra difficile": "ultra_difficile"
        }
        niveau = niveaux_map.get(self.niveau.get(), "intermediaire")
        nb = int(self.nb_ex.get())

        self.zone_ex.delete("0.0", "end")
        self.zone_ex.insert("0.0", f"⏳ Génération de {nb} exercices niveau {niveau}...")
        self.update()

        def tache():
            res = generer_exercices_examen(self.cours_actuel[:5000], niveau, nb)
            self.zone_ex.delete("0.0", "end")
            self.zone_ex.insert("0.0", res)
            self._recompenser(nb * 5, f"{nb} exercices générés !")

        threading.Thread(target=tache, daemon=True).start()

    # ═══════════════════════════════════════════
    # 🎧 AUDIO
    # ═══════════════════════════════════════════
    def afficher_audio(self):
        self.vider_zone()
        self.afficher_titre("Créer un audio", "🎧", VIOLET_PREMIUM)

        ctk.CTkLabel(self.zone_principale, text="✍️  Tape ton texte (ou utilise le cours) :",
                     text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), anchor="w")

        cadre_txt = ctk.CTkFrame(self.zone_principale, fg_color=BLANC, corner_radius=15,
                                 border_width=2, border_color=VIOLET_PALE)
        cadre_txt.pack(fill="x", pady=5)

        self.zone_texte_audio = ctk.CTkTextbox(cadre_txt, height=160, fg_color=BLANC,
                                               text_color=GRIS_TEXTE,
                                               font=ctk.CTkFont(size=14),
                                               corner_radius=12, border_width=0)
        self.zone_texte_audio.pack(fill="x", padx=10, pady=10)

        frame_voix = ctk.CTkFrame(self.zone_principale, fg_color=VIOLET_PALE, corner_radius=14)
        frame_voix.pack(fill="x", pady=10)

        ctk.CTkLabel(frame_voix, text="🎙️  Voix :", text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=15, pady=15)

        self.voix = ctk.CTkOptionMenu(frame_voix,
                                      values=["jeune_femme", "femme", "jeune_homme", "homme"],
                                      fg_color=VIOLET_PREMIUM, text_color=BLANC,
                                      button_color=VIOLET_LAVANDE, corner_radius=10)
        self.voix.pack(side="left", padx=10)

        frame_btns = ctk.CTkFrame(self.zone_principale, fg_color="transparent")
        frame_btns.pack(pady=15, fill="x")

        btn1 = self.creer_bouton_action(frame_btns, "📄  Utiliser le cours",
                                        self._remplir_avec_cours, BLEU_ROYAL, BLEU_CIEL)
        btn1.pack(side="left", padx=5, expand=True, fill="x")

        btn2 = self.creer_bouton_action(frame_btns, "🎧  Créer l'audio",
                                        self._creer_audio, VIOLET_PREMIUM, VIOLET_LAVANDE)
        btn2.pack(side="left", padx=5, expand=True, fill="x")

        self.label_audio = ctk.CTkLabel(self.zone_principale, text="",
                                        text_color=VERT_EMERAUDE,
                                        font=ctk.CTkFont(size=13, weight="bold"))
        self.label_audio.pack(pady=10)

    def _remplir_avec_cours(self):
        if not self.cours_actuel:
            messagebox.showwarning("⚠️", "Importe d'abord un cours !")
            return
        self.zone_texte_audio.delete("0.0", "end")
        self.zone_texte_audio.insert("0.0", self.cours_actuel[:2000])

    def _creer_audio(self):
        texte = self.zone_texte_audio.get("0.0", "end").strip()
        if not texte:
            messagebox.showwarning("⚠️", "Tape du texte d'abord !")
            return
        voix = self.voix.get()
        self.label_audio.configure(text="⏳ Création de l'audio...")
        self.update()

        def tache():
            chemin = generer_audio(texte, "nokirova_audio.mp3", voix)
            self.label_audio.configure(text=f"✅ Audio créé !")
            db.incrementer_stat("audios_crees")
            self._recompenser(8, "Audio créé !")
            messagebox.showinfo("✅ Audio créé",
                                f"📁 Emplacement :\n{chemin}\n\n🎧 Double-clique pour écouter !")

        threading.Thread(target=tache, daemon=True).start()

    # ═══════════════════════════════════════════
    # 💬 CHAT
    # ═══════════════════════════════════════════
    def afficher_chat(self):
        self.vider_zone()
        self.afficher_titre("Question libre à NOKIROVA", "💬", VIOLET_PREMIUM)

        ctk.CTkLabel(self.zone_principale, text="💭  Pose-moi N'IMPORTE QUELLE question :",
                     text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), anchor="w")

        self.question_entry = ctk.CTkEntry(self.zone_principale, height=50,
                                           fg_color=BLANC, text_color=GRIS_TEXTE,
                                           placeholder_text="Ex: Explique-moi l'élasticité-prix...",
                                           font=ctk.CTkFont(size=14), corner_radius=14,
                                           border_width=2, border_color=VIOLET_PALE)
        self.question_entry.pack(fill="x", pady=10)
        self.question_entry.bind("<Return>", lambda e: self._envoyer_question())

        btn = self.creer_bouton_action(self.zone_principale, "🚀  Envoyer",
                                       self._envoyer_question, VIOLET_PREMIUM, VIOLET_LAVANDE)
        btn.pack(pady=10, fill="x")

        self.zone_reponse = self.creer_zone_texte(310)
        self.zone_reponse.insert("0.0",
                                 "💡 Pose ta question ci-dessus puis appuie sur Entrée !")

        btn_pdf = self.creer_bouton_export(self.zone_reponse, "reponse")
        btn_pdf.pack(pady=5)

    def _envoyer_question(self):
        question = self.question_entry.get().strip()
        if not question:
            messagebox.showwarning("⚠️", "Tape une question !")
            return
        self.zone_reponse.delete("0.0", "end")
        self.zone_reponse.insert("0.0", "⏳ NOKIROVA réfléchit... 🧠✨")
        self.update()

        def tache():
            res = demander_ia(question)
            self.zone_reponse.delete("0.0", "end")
            self.zone_reponse.insert("0.0", res)
            db.incrementer_stat("questions_posees")
            db.sauvegarder_historique("question_libre", question, res)
            self._recompenser(5, "Question posée !")

        threading.Thread(target=tache, daemon=True).start()


# ═══════════════════════════════════════════
# 🚀 LANCEMENT
# ═══════════════════════════════════════════
if __name__ == "__main__":
    app = NokirovaApp()
    app.mainloop()