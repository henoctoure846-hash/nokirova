# interface.py - NOKIROVA 🌸 VAGUE 3 FINALE

import customtkinter as ctk
import database as db
import os

# ── Initialisation ──
db.init_db()
db.maj_streak()

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# ── Import base ──
from ui.base import (
    BaseUI, BLANC_CASSE, NOIR_FOND,
    VERT_PRINTEMPS, VERT_EMERAUDE, VERT_HOVER, VERT_CLAIR,
    JAUNE_CLAIR, JAUNE_PALE, JAUNE_SOLEIL,
    BLEU_CIEL, BLEU_PALE, BLEU_ROYAL, BLEU_TRES_PALE,
    ROSE_SAKURA, ROSE_CLAIR, ROSE_PALE,
    VIOLET_LAVANDE, VIOLET_CLAIR, VIOLET_PALE, VIOLET_PREMIUM,
    ORANGE_CLAIR, ORANGE_PALE, ORANGE_DORE,
    BLANC, GRIS_TEXTE, GRIS_DOUX, GRIS_PERLE,
    ROUGE, ROUGE_CLAIR, ROUGE_FOND,
    LOGO_PATH
)

# ── Import arrière-plan ──
from ui.arriere_plan import ArriereplanMixin

# ── Import thèmes ──
from ui.themes import get_liste_themes, get_theme

# ── Import pages ──
from ui.accueil import AccueilMixin
from ui.aide_profil import AideProfilMixin
from ui.bibliotheque import BibliotequeMixin
from ui.historique import HistoriqueMixin
from ui.import_ocr import ImportOCRMixin
from ui.generation import GenerationMixin
from ui.qcm_interactif import QCMInteractifMixin
from ui.audio_chat import AudioChatMixin
from ui.notes import NotesMixin
from ui.flashcards import FlashcardsMixin
from ui.recherche import RechercheMixin
from ui.graphiques import GraphiquesMixin
from ui.pomodoro import PomodoroMixin
from ui.pin_page import PinPageMixin
from ui.traduction import TraductionMixin
from ui.planificateur import PlanificateurMixin
from ui.scan_multipages import ScanMultipagesMixin
from ui.notifications_page import NotificationsPageMixin
from ui.partage import PartageMixin
from ui.videos_revision import VideosRevisionMixin
from ui.sonneries_page import SonneriesPageMixin
from ui.lecteur_medias import LecteurMediasMixin

# ── Notifications auto ──
from notifications import verifier_notifications_auto

# ── Splash screen ──
from splash_screen import lancer_splash


class NokirovaApp(
    ctk.CTk,
    BaseUI,
    ArriereplanMixin,
    AccueilMixin,
    AideProfilMixin,
    BibliotequeMixin,
    HistoriqueMixin,
    ImportOCRMixin,
    GenerationMixin,
    QCMInteractifMixin,
    AudioChatMixin,
    NotesMixin,
    FlashcardsMixin,
    RechercheMixin,
    GraphiquesMixin,
    PomodoroMixin,
    PinPageMixin,
    TraductionMixin,
    PlanificateurMixin,
    ScanMultipagesMixin,
    NotificationsPageMixin,
    PartageMixin,
    VideosRevisionMixin,
    SonneriesPageMixin,
    LecteurMediasMixin
):

    def __init__(self):
        super().__init__()

        self.title("🌸 NOKIROVA - Ton Prof Intelligent")
        self.geometry("1280x820")
        self.configure(fg_color=BLANC_CASSE)
        self.minsize(1100, 700)

        # ✅ MODE ARRIÈRE-PLAN INTELLIGENT
        self.protocol("WM_DELETE_WINDOW", self._fermer_proprement)

        # ── CACHER pendant splash ──
        self.withdraw()

        # ── Logos ──
        self.logo_sidebar = self._charger_logo(180)
        self.logo_petit = self._charger_logo(35)
        self.logo_accueil = self._charger_logo(70)

        # ── Variables cours ──
        self.cours_actuel = ""
        self.nom_cours = "Aucun cours chargé"
        self.matiere_detectee = ""
        self.id_cours_actif = None
        self.mode_sombre = False
        self.dernier_contenu = ""

        # ── Variables génération ──
        self.contenu_qcm_complet = ""
        self.contenu_q_complet = ""
        self.contenu_ex_complet = ""
        self.correction_visible = {"qcm": False, "q": False, "ex": False}

        # ── QCM interactif ──
        self.qcms_interactifs = []
        self.qcm_index = 0
        self.qcm_score = 0
        self.qcm_reponses = []

        # ── Filtres ──
        self.filtre_matiere = "Toutes"
        self.filtre_historique = "Tous"
        self.filtre_notes = "Toutes"
        self._types_map = {}

        # ── Flashcards ──
        self._cards_session = []
        self._card_index = 0
        self._session_reussis = 0
        self._session_rates = 0
        self._verso_visible = False
        self._nom_deck_session = ""

        # ── Pomodoro ──
        self._pomo_timer = None
        self._pomo_restant = 25 * 60
        self._pomo_total = 25 * 60
        self._pomo_en_cours = False
        self._pomo_pause_active = False

        # ── Navigation ──
        self._historique_pages = []
        self._page_actuelle = "afficher_accueil"
        self._boutons_sidebar = {}

        # ✅ Init fond écran
        self._init_arriere_plan()

        # ── Construction UI ──
        self.creer_sidebar()
        self.creer_zone_principale()

        # ── PIN ──
        if db.pin_existe():
            self.afficher_ecran_deverrouillage()
        else:
            self.afficher_accueil()

        self.bind_raccourcis()
        self._demarrer_timer_notifications()

        # ✅ Charger thème sauvegardé
        self.charger_theme_sauvegarde()

        # ✅ Splash
        lancer_splash(self, callback=self._afficher_apres_splash)

    # ═══════════════════════════════════════════
    # ✅ MODE ARRIÈRE-PLAN INTELLIGENT
    # ═══════════════════════════════════════════

    def _fermer_proprement(self):
        """
        Minimise l'app au lieu de la fermer
        → elle continue à tourner en arrière-plan
        """
        self.iconify()

    # ═══════════════════════════════════════════
    # ✅ SPLASH
    # ═══════════════════════════════════════════

    def _afficher_apres_splash(self):
        """Appelé après les 5 secondes du splash"""
        try:
            self.deiconify()
            self.lift()
            self.focus_force()
        except Exception as e:
            print(f"⚠️ Affichage app : {e}")

    # ═══════════════════════════════════════════
    # 🔔 TIMER NOTIFICATIONS AUTO
    # ═══════════════════════════════════════════

    def _demarrer_timer_notifications(self):
        try:
            verifier_notifications_auto(self)
        except Exception as e:
            print(f"⚠️ Timer notifs : {e}")
        self.after(60000, self._demarrer_timer_notifications)

    # ═══════════════════════════════════════════
    # 🎯 INDICATEUR PAGE ACTIVE
    # ═══════════════════════════════════════════

    def _maj_page_active(self, nom_fonction):
        """Met en évidence le bouton de la page actuelle"""
        self._page_actuelle = nom_fonction
        theme = get_theme(db.charger_preference("theme") or "🌸 Spring")
        for nom, btn in self._boutons_sidebar.items():
            if btn is None:
                continue
            try:
                if nom == nom_fonction:
                    btn.configure(
                        fg_color=theme["bouton_actif"],
                        text_color=BLANC,
                        border_width=2,
                        border_color=theme["bouton_hover"])
                else:
                    btn.configure(
                        fg_color=BLANC,
                        text_color=GRIS_TEXTE,
                        border_width=0)
            except Exception:
                pass

    def _wrap_afficher(self, fonction, nom):
        """Wrapper navigation + maj page active"""
        def wrapped():
            self._enregistrer_navigation(nom)
            self._maj_page_active(nom)
            getattr(self, nom)()
        return wrapped

    # ═══════════════════════════════════════════
    # ⌨️ RACCOURCIS
    # ═══════════════════════════════════════════

    def bind_raccourcis(self):
        self.bind("<Control-h>", lambda e: self.afficher_accueil())
        self.bind("<Control-i>", lambda e: self.afficher_import())
        self.bind("<Control-q>", lambda e: self.afficher_qcm())
        self.bind("<Control-r>", lambda e: self.afficher_resume())
        self.bind("<Control-d>", lambda e: self.toggle_mode_sombre())
        self.bind("<Control-b>", lambda e: self.afficher_bibliotheque())
        self.bind("<Control-l>", lambda e: self.afficher_historique())
        self.bind("<Control-n>", lambda e: self.afficher_notes())
        self.bind("<Control-f>", lambda e: self.afficher_flashcards())
        self.bind("<Control-p>", lambda e: self.afficher_pomodoro())
        self.bind("<Control-k>", lambda e: self.afficher_recherche())
        self.bind("<Control-g>", lambda e: self.afficher_graphiques())
        self.bind("<Control-s>", lambda e: self.afficher_securite())
        self.bind("<Control-j>", lambda e: self.afficher_planificateur())
        self.bind("<Control-m>", lambda e: self.afficher_scan_multipages())
        self.bind("<Control-u>", lambda e: self.afficher_notifications_params())
        self.bind("<Control-e>", lambda e: self.afficher_import_partage())
        self.bind("<Control-v>", lambda e: self.afficher_videos_revision())
        self.bind("<Control-y>", lambda e: self.afficher_sonneries())
        self.bind("<Control-x>", lambda e: self.afficher_lecteur_medias())
        self.bind("<Control-t>", lambda e: self.afficher_parametres())
        self.bind("<F1>", lambda e: self.afficher_aide())

    # ═══════════════════════════════════════════
    # 🏗️ SIDEBAR COMPLÈTE
    # ═══════════════════════════════════════════

    def creer_sidebar(self):
        """Sidebar PRO réorganisée par catégories"""
        self.sidebar = ctk.CTkScrollableFrame(
            self, width=290,
            fg_color=VERT_PRINTEMPS, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        # ── LOGO ──
        cadre_logo = ctk.CTkFrame(
            self.sidebar, fg_color=JAUNE_CLAIR, corner_radius=20)
        cadre_logo.pack(fill="x", padx=10, pady=(15, 10))

        if self.logo_sidebar:
            ctk.CTkLabel(
                cadre_logo, image=self.logo_sidebar, text="").pack(
                pady=(15, 10))

        ctk.CTkButton(
            cadre_logo, text="🌙 / ☀️  Mode",
            command=self.toggle_mode_sombre,
            fg_color="transparent", text_color=GRIS_TEXTE,
            hover_color=JAUNE_PALE,
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28, corner_radius=8).pack(pady=(2, 12))

        # ── SECTIONS ──
        sections = [
            {
                "titre": "📍  NAVIGATION",
                "couleur": VERT_EMERAUDE,
                "boutons": [
                    ("🏠  Accueil", "afficher_accueil"),
                    ("📚  Bibliothèque", "afficher_bibliotheque"),
                    ("🏆  Mon Profil", "afficher_profil"),
                    ("🔍  Recherche", "afficher_recherche"),
                    ("📜  Historique", "afficher_historique"),
                ]
            },
            {
                "titre": "📥  IMPORT & SCAN",
                "couleur": BLEU_ROYAL,
                "boutons": [
                    ("📥  Importer un cours", "afficher_import"),
                    ("📸  Scanner image", "afficher_ocr"),
                    ("📚  Scan Multi-pages", "afficher_scan_multipages"),
                ]
            },
            {
                "titre": "🧠  APPRENTISSAGE",
                "couleur": ROSE_SAKURA,
                "boutons": [
                    ("🎯  QCM", "afficher_qcm"),
                    ("❓  Questions de cours", "afficher_questions"),
                    ("📚  Exercices examen", "afficher_examen"),
                    ("🃏  Flashcards", "afficher_flashcards"),
                    ("📝  Résumé", "afficher_resume"),
                    ("💡  Explication simple", "afficher_explication"),
                ]
            },
            {
                "titre": "🤖  OUTILS IA",
                "couleur": VIOLET_PREMIUM,
                "boutons": [
                    ("💬  Question libre", "afficher_chat"),
                    ("🎧  Audio", "afficher_audio"),
                    ("🌍  Traduction", "afficher_traduction"),
                    ("🎬  Vidéos révision", "afficher_videos_revision"),
                    ("🎵  Mes Médias", "afficher_lecteur_medias"),
                ]
            },
            {
                "titre": "📅  PRODUCTIVITÉ",
                "couleur": ORANGE_DORE,
                "boutons": [
                    ("📅  Planificateur", "afficher_planificateur"),
                    ("⏱️  Pomodoro", "afficher_pomodoro"),
                    ("✍️  Mes Notes", "afficher_notes"),
                    ("🔔  Notifications", "afficher_notifications_params"),
                ]
            },
            {
                "titre": "📊  STATISTIQUES",
                "couleur": VIOLET_LAVANDE,
                "boutons": [
                    ("📈  Graphiques", "afficher_graphiques"),
                ]
            },
            {
                "titre": "⚙️  PARAMÈTRES",
                "couleur": GRIS_TEXTE,
                "boutons": [
                    ("🎨  Thèmes & Fond", "afficher_parametres"),
                    ("🔊  Sonneries", "afficher_sonneries"),
                    ("🔒  Sécurité PIN", "afficher_securite"),
                    ("🤝  Importer partage", "afficher_import_partage"),
                    ("⌨️  Aide / Raccourcis", "afficher_aide"),
                ]
            },
        ]

        for section in sections:
            self._creer_section_sidebar(
                section["titre"],
                section["couleur"],
                section["boutons"])

        # ── STATUT COURS ──
        carte_statut = ctk.CTkFrame(
            self.sidebar, fg_color=ROSE_PALE, corner_radius=15)
        carte_statut.pack(fill="x", padx=10, pady=(15, 5))

        ctk.CTkLabel(
            carte_statut, text="📚  COURS ACTUEL",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=GRIS_TEXTE).pack(pady=(10, 2))

        self.statut_label = ctk.CTkLabel(
            carte_statut, text=self.nom_cours,
            font=ctk.CTkFont(size=11),
            text_color=VIOLET_PREMIUM, wraplength=240)
        self.statut_label.pack(pady=(0, 10), padx=10)

        # ── SIGNATURE ──
        ctk.CTkLabel(
            self.sidebar,
            text="✨  Created by Hénoc 🌸 2026  ✨",
            font=ctk.CTkFont(size=10, weight="bold", slant="italic"),
            text_color=GRIS_TEXTE).pack(pady=(10, 15))

    def _creer_section_sidebar(self, titre, couleur, boutons):
        """Crée une section de la sidebar avec son titre coloré"""
        cadre_titre = ctk.CTkFrame(
            self.sidebar, fg_color=couleur,
            corner_radius=8, height=30)
        cadre_titre.pack(fill="x", padx=10, pady=(10, 3))
        cadre_titre.pack_propagate(False)

        ctk.CTkLabel(
            cadre_titre, text=titre,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=BLANC).pack(pady=6)

        for texte, nom_fonction in boutons:
            btn = ctk.CTkButton(
                self.sidebar, text=texte,
                command=self._wrap_afficher(None, nom_fonction),
                fg_color=BLANC, text_color=GRIS_TEXTE,
                hover_color=couleur, anchor="w",
                font=ctk.CTkFont(
                    family="Segoe UI", size=12, weight="bold"),
                height=36, corner_radius=10,
                border_width=0)
            btn.pack(fill="x", padx=10, pady=2)
            self._boutons_sidebar[nom_fonction] = btn

    # ═══════════════════════════════════════════
    # 🏗️ ZONE PRINCIPALE
    # ═══════════════════════════════════════════

    def creer_zone_principale(self):
        self.zone_principale = ctk.CTkFrame(
            self, fg_color=BLANC_CASSE)
        self.zone_principale.pack(
            side="right", fill="both", expand=True,
            padx=20, pady=20)

    # ═══════════════════════════════════════════
    # 🎨 PAGE PARAMÈTRES (THÈMES + FOND)
    # ═══════════════════════════════════════════

    def afficher_parametres(self):
        """Page Paramètres : Thèmes + Fond d'écran"""
        self.vider_zone()
        self._enregistrer_navigation("afficher_parametres")
        self._maj_page_active("afficher_parametres")
        self.afficher_titre("Paramètres", "⚙️")

        # Scroll
        scroll = ctk.CTkScrollableFrame(
            self.zone_principale, fg_color=BLANC_CASSE)
        scroll.pack(fill="both", expand=True)

        # ═══════════════════
        # 🎨 SECTION THÈMES
        # ═══════════════════
        cadre_themes = ctk.CTkFrame(
            scroll, fg_color=BLANC,
            corner_radius=18,
            border_width=2, border_color=VIOLET_PALE)
        cadre_themes.pack(fill="x", padx=10, pady=(10, 15))

        ctk.CTkLabel(
            cadre_themes,
            text="🎨  Choisir un thème",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=VIOLET_PREMIUM).pack(pady=(15, 5))

        ctk.CTkLabel(
            cadre_themes,
            text="Clique sur un thème pour l'appliquer instantanément ✨",
            font=ctk.CTkFont(size=12),
            text_color=GRIS_DOUX).pack(pady=(0, 15))

        # Grille de thèmes
        grille = ctk.CTkFrame(cadre_themes, fg_color="transparent")
        grille.pack(fill="x", padx=20, pady=(0, 20))

        themes_info = {
            "🌸 Spring": (VERT_EMERAUDE, VERT_HOVER),
            "🌙 Nuit": ("#7B61FF", "#A855F7"),
            "🌊 Océan": (BLEU_ROYAL, BLEU_CIEL),
            "🌺 Sakura": ("#E91E8C", "#FFC9DE"),
            "🍂 Automne": (ORANGE_DORE, ORANGE_CLAIR),
            "💜 Lavande": (VIOLET_LAVANDE, VIOLET_CLAIR),
        }

        col = 0
        row = 0
        for nom, (couleur, hover) in themes_info.items():
            btn = ctk.CTkButton(
                grille,
                text=nom,
                command=lambda n=nom: self.appliquer_theme(n),
                fg_color=couleur,
                hover_color=hover,
                text_color=BLANC,
                font=ctk.CTkFont(size=14, weight="bold"),
                height=55, corner_radius=14,
                width=180)
            btn.grid(
                row=row, column=col,
                padx=10, pady=8,
                sticky="ew")
            col += 1
            if col >= 3:
                col = 0
                row += 1

        # ═══════════════════════
        # 🖼️ SECTION FOND ÉCRAN
        # ═══════════════════════
        cadre_fond = ctk.CTkFrame(
            scroll, fg_color=BLANC,
            corner_radius=18,
            border_width=2, border_color=BLEU_TRES_PALE)
        cadre_fond.pack(fill="x", padx=10, pady=(0, 15))

        ctk.CTkLabel(
            cadre_fond,
            text="🖼️  Fond d'écran personnalisé",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=BLEU_ROYAL).pack(pady=(15, 5))

        ctk.CTkLabel(
            cadre_fond,
            text="Choisis une image de ta galerie comme fond d'écran 🖼️",
            font=ctk.CTkFont(size=12),
            text_color=GRIS_DOUX).pack(pady=(0, 10))

        # Aperçu statut fond actuel
        self._label_statut_fond = ctk.CTkLabel(
            cadre_fond,
            text=self._get_statut_fond(),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=VERT_EMERAUDE)
        self._label_statut_fond.pack(pady=(0, 15))

        # Slider opacité
        ctk.CTkLabel(
            cadre_fond,
            text="🌫️  Opacité du fond :",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=GRIS_TEXTE).pack(pady=(5, 2))

        self._slider_opacite = ctk.CTkSlider(
            cadre_fond,
            from_=0.1, to=0.9,
            width=300,
            progress_color=BLEU_ROYAL,
            button_color=BLEU_ROYAL)
        self._slider_opacite.set(
            getattr(self, '_fond_opacite', 0.3))
        self._slider_opacite.pack(pady=(0, 5))

        ctk.CTkLabel(
            cadre_fond,
            text="(Faible = transparent  |  Élevé = opaque)",
            font=ctk.CTkFont(size=10),
            text_color=GRIS_DOUX).pack(pady=(0, 10))

        # Switch flou
        self._switch_flou = ctk.CTkSwitch(
            cadre_fond,
            text="🌫️  Activer le flou",
            font=ctk.CTkFont(size=13),
            progress_color=BLEU_ROYAL)
        if getattr(self, '_fond_flou', False):
            self._switch_flou.select()
        self._switch_flou.pack(pady=(0, 15))

        # Boutons actions fond
        cadre_btn_fond = ctk.CTkFrame(
            cadre_fond, fg_color="transparent")
        cadre_btn_fond.pack(pady=(0, 20))

        ctk.CTkButton(
            cadre_btn_fond,
            text="📁  Choisir une image",
            command=self._choisir_et_appliquer_fond,
            fg_color=BLEU_ROYAL,
            hover_color=BLEU_CIEL,
            text_color=BLANC,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45, corner_radius=12,
            width=200).pack(side="left", padx=10)

        ctk.CTkButton(
            cadre_btn_fond,
            text="🗑️  Supprimer fond",
            command=self._supprimer_fond_et_maj,
            fg_color=ROUGE_FOND if hasattr(self, 'ROUGE_FOND')
            else "#FEE2E2",
            hover_color="#FCA5A5",
            text_color="#EF4444",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45, corner_radius=12,
            width=180).pack(side="left", padx=10)

    def _get_statut_fond(self) -> str:
        """Retourne le statut du fond actuel"""
        if getattr(self, '_fond_actif', False) and self._fond_chemin:
            nom = os.path.basename(self._fond_chemin)
            return f"✅ Fond actif : {nom}"
        return "❌ Aucun fond actif"

    def _choisir_et_appliquer_fond(self):
        """Ouvre galerie + applique fond"""
        chemin = self.choisir_image_fond()
        if chemin:
            opacite = self._slider_opacite.get()
            flou = bool(self._switch_flou.get())
            self._appliquer_fond(chemin, opacite, flou)
            # MAJ statut
            try:
                self._label_statut_fond.configure(
                    text=self._get_statut_fond())
            except Exception:
                pass

    def _supprimer_fond_et_maj(self):
        """Supprime fond + MAJ statut"""
        self.supprimer_fond_ecran()
        try:
            self._label_statut_fond.configure(
                text=self._get_statut_fond())
        except Exception:
            pass


if __name__ == "__main__":
    app = NokirovaApp()
    app.mainloop()