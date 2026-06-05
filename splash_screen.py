# splash_screen.py - Écran de démarrage animé NOKIROVA ✨🌸

import customtkinter as ctk
import os
from PIL import Image

LOGO_PATH = "frontend/icon-512.png"

# Couleurs
VIOLET_PREMIUM = "#7B61FF"
VIOLET_LAVANDE = "#A855F7"
VERT_EMERAUDE = "#00C853"
VERT_PRINTEMPS = "#7ED321"
JAUNE_SOLEIL = "#FFD93D"
ROSE_SAKURA = "#FFC9DE"
BLANC = "#FFFFFF"
GRIS_TEXTE = "#374151"
NOIR_FOND = "#1A1B26"


class SplashScreen(ctk.CTkToplevel):
    """
    Splash screen animé qui s'affiche pendant 5 secondes
    avant l'app principale.
    """

    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)

        self.on_close_callback = on_close_callback
        self.parent = parent

        # Configuration fenêtre
        self.title("")
        self.overrideredirect(True)  # Pas de barre de titre
        self.attributes("-topmost", True)
        self.configure(fg_color=VIOLET_PREMIUM)

        # Taille et centrage
        self.largeur = 600
        self.hauteur = 500

        # Centrer sur l'écran
        ecran_w = self.winfo_screenwidth()
        ecran_h = self.winfo_screenheight()
        x = (ecran_w - self.largeur) // 2
        y = (ecran_h - self.hauteur) // 2
        self.geometry(f"{self.largeur}x{self.hauteur}+{x}+{y}")

        # Variables animation
        self.taille_logo_actuelle = 50
        self.taille_logo_max = 200
        self.logo_label = None
        self.logo_image = None

        self.texte_nokirova = ""
        self.texte_complet = "NOKIROVA"
        self.index_lettre = 0

        self.progression = 0
        self.progress_bar = None

        # Durée totale : 5 secondes (5000 ms)
        self.duree_totale_ms = 5000

        # Construction UI
        self._construire_ui()

        # Démarrer animations
        self.after(100, self._animer_logo_zoom)
        self.after(800, self._animer_texte_lettre_par_lettre)
        self.after(200, self._animer_barre_progression)

        # Fermeture automatique après 5 secondes
        self.after(self.duree_totale_ms, self._fermer)

    def _construire_ui(self):
        """Construit l'interface du splash"""

        # ── CADRE PRINCIPAL (avec dégradé via couleur unie) ──
        cadre_main = ctk.CTkFrame(
            self, fg_color=VIOLET_PREMIUM, corner_radius=0)
        cadre_main.pack(fill="both", expand=True)

        # ── ZONE LOGO (centrale, avec halo) ──
        self.zone_logo = ctk.CTkFrame(
            cadre_main, fg_color=VIOLET_LAVANDE,
            corner_radius=120, width=240, height=240)
        self.zone_logo.pack(pady=(50, 20))
        self.zone_logo.pack_propagate(False)

        # Logo (sera animé)
        try:
            if os.path.exists(LOGO_PATH):
                img = Image.open(LOGO_PATH)
                self.logo_image = ctk.CTkImage(
                    light_image=img, dark_image=img,
                    size=(self.taille_logo_actuelle,
                          self.taille_logo_actuelle))
                self.logo_label = ctk.CTkLabel(
                    self.zone_logo, image=self.logo_image, text="")
                self.logo_label.pack(expand=True)
            else:
                # Fallback si pas de logo
                self.logo_label = ctk.CTkLabel(
                    self.zone_logo, text="🌸",
                    font=ctk.CTkFont(size=120))
                self.logo_label.pack(expand=True)
        except Exception as e:
            print(f"⚠️ Logo splash : {e}")
            self.logo_label = ctk.CTkLabel(
                self.zone_logo, text="🌸",
                font=ctk.CTkFont(size=120))
            self.logo_label.pack(expand=True)

        # ── TITRE "NOKIROVA" (lettre par lettre) ──
        self.label_titre = ctk.CTkLabel(
            cadre_main, text="",
            font=ctk.CTkFont(
                family="Segoe UI", size=42, weight="bold"),
            text_color=BLANC)
        self.label_titre.pack(pady=(15, 5))

        # ── SOUS-TITRE ──
        ctk.CTkLabel(
            cadre_main, text="✨ Ton Prof Intelligent ✨",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=JAUNE_SOLEIL).pack(pady=(0, 30))

        # ── BARRE DE PROGRESSION ──
        cadre_progress = ctk.CTkFrame(
            cadre_main, fg_color="transparent")
        cadre_progress.pack(fill="x", padx=80)

        self.progress_bar = ctk.CTkProgressBar(
            cadre_progress,
            progress_color=JAUNE_SOLEIL,
            fg_color=VIOLET_LAVANDE,
            height=12, corner_radius=6)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x")

        # ── TEXTE "Chargement..." ──
        self.label_chargement = ctk.CTkLabel(
            cadre_main, text="⏳  Chargement...",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ROSE_SAKURA)
        self.label_chargement.pack(pady=(10, 0))

        # ── SIGNATURE EN BAS ──
        ctk.CTkLabel(
            cadre_main,
            text="✨  Created by Hénoc 🌸 2026  ✨",
            font=ctk.CTkFont(
                size=11, weight="bold", slant="italic"),
            text_color=JAUNE_SOLEIL).pack(side="bottom", pady=20)

    # ═══════════════════════════════════════════
    # 🎬 ANIMATIONS
    # ═══════════════════════════════════════════

    def _animer_logo_zoom(self):
        """Anime le logo en zoom progressif"""
        if not self.logo_label:
            return

        try:
            if self.taille_logo_actuelle < self.taille_logo_max:
                # Phase 1 : Zoom in
                self.taille_logo_actuelle += 8
                if self.taille_logo_actuelle > self.taille_logo_max:
                    self.taille_logo_actuelle = self.taille_logo_max

                if self.logo_image and os.path.exists(LOGO_PATH):
                    img = Image.open(LOGO_PATH)
                    self.logo_image = ctk.CTkImage(
                        light_image=img, dark_image=img,
                        size=(self.taille_logo_actuelle,
                              self.taille_logo_actuelle))
                    self.logo_label.configure(image=self.logo_image)

                # Continuer animation
                self.after(50, self._animer_logo_zoom)
            else:
                # Phase 2 : Pulse léger
                self._animer_pulse()
        except Exception as e:
            print(f"⚠️ Animation zoom : {e}")

    def _animer_pulse(self):
        """Effet de pulse léger sur le logo"""
        if not self.logo_label:
            return

        try:
            # Variation entre 190 et 210 px
            import math
            t = self.winfo_id() % 1000
            offset = int(math.sin(t * 0.01) * 10)
            taille = 200 + offset

            if self.logo_image and os.path.exists(LOGO_PATH):
                img = Image.open(LOGO_PATH)
                self.logo_image = ctk.CTkImage(
                    light_image=img, dark_image=img,
                    size=(taille, taille))
                self.logo_label.configure(image=self.logo_image)

            # Continuer le pulse
            self.after(100, self._animer_pulse)
        except Exception:
            pass

    def _animer_texte_lettre_par_lettre(self):
        """Affiche le texte NOKIROVA lettre par lettre"""
        try:
            if self.index_lettre < len(self.texte_complet):
                self.texte_nokirova += self.texte_complet[self.index_lettre]
                self.label_titre.configure(text=self.texte_nokirova)
                self.index_lettre += 1
                # Vitesse : 1 lettre toutes les 250ms
                self.after(250, self._animer_texte_lettre_par_lettre)
        except Exception as e:
            print(f"⚠️ Animation texte : {e}")

    def _animer_barre_progression(self):
        """Anime la barre de chargement sur 5 secondes"""
        try:
            self.progression += 0.02

            if self.progression > 1:
                self.progression = 1
                self.label_chargement.configure(
                    text="✅  Prêt !")

            self.progress_bar.set(self.progression)

            # MAJ texte selon progression
            if 0.3 <= self.progression < 0.6:
                self.label_chargement.configure(
                    text="🤖  Initialisation des IA...")
            elif 0.6 <= self.progression < 0.9:
                self.label_chargement.configure(
                    text="🎨  Préparation de l'interface...")

            if self.progression < 1:
                # Vitesse : 100ms par tick → 5000ms total
                self.after(100, self._animer_barre_progression)
        except Exception as e:
            print(f"⚠️ Animation progression : {e}")

    def _fermer(self):
        """Ferme le splash et lance le callback"""
        try:
            self.destroy()
        except Exception:
            pass

        if self.on_close_callback:
            try:
                self.on_close_callback()
            except Exception as e:
                print(f"⚠️ Callback splash : {e}")


def lancer_splash(parent, callback=None):
    """
    Lance le splash screen.
    parent : fenêtre Tk parente (cachée pendant le splash)
    callback : fonction à appeler après les 5 sec
    """
    splash = SplashScreen(parent, on_close_callback=callback)
    splash.focus_force()
    return splash