# ui/arriere_plan.py - Fond d'écran personnalisé NOKIROVA 🖼️

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import json
from PIL import Image, ImageTk, ImageFilter, ImageEnhance

# ═══════════════════════════════════════════
# 📁 FICHIER DE CONFIG FOND
# ═══════════════════════════════════════════
CONFIG_FOND = "outputs/fond_ecran.json"


def _sauvegarder_config_fond(chemin: str, opacite: float, flou: bool):
    """Sauvegarde la config du fond d'écran"""
    try:
        os.makedirs("outputs", exist_ok=True)
        with open(CONFIG_FOND, "w", encoding="utf-8") as f:
            json.dump({
                "chemin": chemin,
                "opacite": opacite,
                "flou": flou
            }, f)
    except Exception as e:
        print(f"⚠️ Sauvegarde fond : {e}")


def charger_config_fond() -> dict:
    """Charge la config du fond d'écran"""
    try:
        if os.path.exists(CONFIG_FOND):
            with open(CONFIG_FOND, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Chargement fond : {e}")
    return {"chemin": "", "opacite": 0.3, "flou": False}


def supprimer_fond():
    """Supprime la config du fond"""
    try:
        if os.path.exists(CONFIG_FOND):
            os.remove(CONFIG_FOND)
    except Exception as e:
        print(f"⚠️ Suppression fond : {e}")


class ArriereplanMixin:
    """
    Mixin pour gérer le fond d'écran personnalisé.
    NokirovaApp hérite de cette classe.
    """

    def _init_arriere_plan(self):
        """Initialise les variables du fond d'écran"""
        self._fond_image_tk = None
        self._fond_label = None
        self._fond_actif = False
        self._fond_chemin = ""
        self._fond_opacite = 0.3
        self._fond_flou = False

        # Charger config sauvegardée
        config = charger_config_fond()
        if config.get("chemin") and os.path.exists(config["chemin"]):
            self._fond_chemin = config["chemin"]
            self._fond_opacite = config.get("opacite", 0.3)
            self._fond_flou = config.get("flou", False)
            self.after(500, self._appliquer_fond_sauvegarde)

    def _appliquer_fond_sauvegarde(self):
        """Applique le fond sauvegardé au démarrage"""
        try:
            self._appliquer_fond(
                self._fond_chemin,
                self._fond_opacite,
                self._fond_flou
            )
        except Exception as e:
            print(f"⚠️ Fond sauvegardé : {e}")

    def choisir_image_fond(self, callback_preview=None):
        """Ouvre le sélecteur de fichier pour choisir une image"""
        chemin = filedialog.askopenfilename(
            title="🖼️ Choisir une image de fond",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("Tous", "*.*")
            ]
        )
        if chemin:
            self._fond_chemin = chemin
            if callback_preview:
                callback_preview(chemin)
            return chemin
        return None

    def _appliquer_fond(self, chemin: str, opacite: float = 0.3,
                        flou: bool = False):
        """Applique l'image de fond sur l'app"""
        try:
            if not chemin or not os.path.exists(chemin):
                return

            # Ouvrir et redimensionner
            img = Image.open(chemin).convert("RGBA")
            w = self.winfo_width() or 1280
            h = self.winfo_height() or 820
            img = img.resize((w, h), Image.LANCZOS)

            # Appliquer flou si activé
            if flou:
                img = img.filter(ImageFilter.GaussianBlur(radius=8))

            # Appliquer opacité
            r, g, b, a = img.split()
            a = ImageEnhance.Brightness(a).enhance(opacite)
            img.putalpha(a)

            # Créer image blanche de fond + coller image par dessus
            fond_blanc = Image.new("RGBA", (w, h), (255, 255, 255, 255))
            fond_blanc.paste(img, (0, 0), img)
            fond_final = fond_blanc.convert("RGB")

            # Convertir pour tkinter
            self._fond_image_tk = ImageTk.PhotoImage(fond_final)

            # Supprimer ancien label si existe
            if self._fond_label:
                try:
                    self._fond_label.destroy()
                except Exception:
                    pass

            # Créer label fond (derrière tout)
            self._fond_label = ctk.CTkLabel(
                self, image=self._fond_image_tk, text="")
            self._fond_label.place(x=0, y=0, relwidth=1, relheight=1)
            self._fond_label.lower()  # Mettre EN DESSOUS de tout

            self._fond_actif = True
            self._fond_chemin = chemin
            self._fond_opacite = opacite
            self._fond_flou = flou

            # Sauvegarder config
            _sauvegarder_config_fond(chemin, opacite, flou)

            # Redimensionner si fenêtre change
            self.bind("<Configure>", self._on_resize_fond)

        except Exception as e:
            print(f"⚠️ Appliquer fond : {e}")
            messagebox.showerror(
                "❌ Erreur",
                f"Impossible de charger cette image.\n{e}")

    def supprimer_fond_ecran(self):
        """Supprime le fond d'écran"""
        try:
            if self._fond_label:
                self._fond_label.destroy()
                self._fond_label = None
            self._fond_actif = False
            self._fond_chemin = ""
            self._fond_image_tk = None
            supprimer_fond()
            # Unbind resize
            try:
                self.unbind("<Configure>")
            except Exception:
                pass
        except Exception as e:
            print(f"⚠️ Suppression fond : {e}")

    def _on_resize_fond(self, event=None):
        """Redimensionne le fond quand la fenêtre change"""
        if not self._fond_actif or not self._fond_chemin:
            return
        try:
            # Eviter trop d'appels
            if hasattr(self, '_resize_after'):
                self.after_cancel(self._resize_after)
            self._resize_after = self.after(
                300,
                lambda: self._appliquer_fond(
                    self._fond_chemin,
                    self._fond_opacite,
                    self._fond_flou
                )
            )
        except Exception:
            pass