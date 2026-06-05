# ui/lecteur_medias.py - Lecteur audio/vidéo NOKIROVA 🎵

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import shutil
import webbrowser
import threading
import time
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


# Dossiers à scanner pour trouver les médias
DOSSIERS_AUDIOS = [".", "outputs", "audios"]
DOSSIER_VIDEOS = "videos_revision"

# Pygame (pour lecture audio)
PYGAME_OK = False
try:
    import pygame
    pygame.mixer.init()
    PYGAME_OK = True
    print("✅ Pygame mixer prêt 🎵")
except Exception as e:
    print(f"⚠️ Pygame indisponible : {e}")


class LecteurMediasMixin:

    # ═══════════════════════════════════════════
    # 🎵 PAGE LECTEUR MÉDIAS
    # ═══════════════════════════════════════════

    def afficher_lecteur_medias(self):
        self.vider_zone()
        self.afficher_titre("Mes Médias", "🎵", VIOLET_PREMIUM)

        # Init variables
        if not hasattr(self, '_lecteur_actuel'):
            self._lecteur_actuel = None
        if not hasattr(self, '_lecteur_en_lecture'):
            self._lecteur_en_lecture = False
        if not hasattr(self, '_lecteur_pause'):
            self._lecteur_pause = False
        if not hasattr(self, '_lecteur_volume'):
            self._lecteur_volume = 0.7

        # ── SCROLL ──
        scroll = ctk.CTkScrollableFrame(
            self.zone_principale, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # ── Bandeau info ──
        info = ctk.CTkFrame(
            scroll, fg_color=VIOLET_PALE, corner_radius=12)
        info.pack(fill="x", pady=5)
        ctk.CTkLabel(
            info,
            text="🎵 Lis tes audios et vidéos directement dans NOKIROVA !\n"
                 "▶️ Play/Pause • 🔊 Volume • 📊 Progression\n"
                 "📤 Exporte vers où tu veux • 🗑️ Supprime",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=VIOLET_PREMIUM,
            justify="center").pack(pady=12)

        # ── Vérif pygame ──
        if not PYGAME_OK:
            warn = ctk.CTkFrame(
                scroll, fg_color=ROUGE_CLAIR, corner_radius=12)
            warn.pack(fill="x", pady=8)
            ctk.CTkLabel(
                warn,
                text="⚠️  pygame non installé !\n"
                     "💡 pip install pygame",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=BLANC, justify="center").pack(pady=10)
            return

        # ═══════════════════════════════════════════
        # 🎧 LECTEUR ACTIF (si un audio est chargé)
        # ═══════════════════════════════════════════
        if self._lecteur_actuel:
            self._afficher_lecteur_actif(scroll)

        # ═══════════════════════════════════════════
        # 📂 AUDIOS DISPONIBLES
        # ═══════════════════════════════════════════
        self._creer_titre_section(
            scroll, "🎧  TES AUDIOS", VIOLET_PREMIUM)

        audios = self._lister_audios()
        if not audios:
            self._afficher_vide(
                scroll,
                "📭  Aucun audio trouvé.\n"
                "💡 Crée un audio depuis la page 🎧 Audio !")
        else:
            for audio in audios:
                self._creer_carte_audio(scroll, audio)

        # ═══════════════════════════════════════════
        # 🎬 VIDÉOS DISPONIBLES
        # ═══════════════════════════════════════════
        self._creer_titre_section(
            scroll, "🎬  TES VIDÉOS RÉVISION", ORANGE_DORE)

        videos = self._lister_videos()
        if not videos:
            self._afficher_vide(
                scroll,
                "📭  Aucune vidéo trouvée.\n"
                "💡 Crée une vidéo depuis 🎬 Vidéos révision !")
        else:
            for video in videos:
                self._creer_carte_video(scroll, video)

        # Espace bas
        ctk.CTkLabel(scroll, text="", height=15).pack()

    # ═══════════════════════════════════════════
    # 🎧 LECTEUR ACTIF
    # ═══════════════════════════════════════════

    def _afficher_lecteur_actif(self, parent):
        """Affiche le lecteur de l'audio en cours"""
        cadre = ctk.CTkFrame(
            parent, fg_color=VIOLET_PREMIUM, corner_radius=18,
            border_width=3, border_color=VIOLET_LAVANDE)
        cadre.pack(fill="x", pady=10)

        nom_audio = os.path.basename(self._lecteur_actuel)

        # En-tête
        ctk.CTkLabel(
            cadre, text="🎵  LECTURE EN COURS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=JAUNE_SOLEIL).pack(pady=(15, 5))

        ctk.CTkLabel(
            cadre, text=f"🎧  {nom_audio[:50]}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=BLANC).pack(pady=(0, 15))

        # Barre de progression
        try:
            duree_totale = self._get_duree_audio(self._lecteur_actuel)
        except Exception:
            duree_totale = 0

        if not hasattr(self, '_lecteur_progress_bar'):
            self._lecteur_progress_bar = None

        self._lecteur_progress_bar = ctk.CTkProgressBar(
            cadre, progress_color=JAUNE_SOLEIL,
            fg_color=VIOLET_LAVANDE, height=15, corner_radius=8)
        self._lecteur_progress_bar.set(0)
        self._lecteur_progress_bar.pack(
            fill="x", padx=25, pady=5)

        # Label temps
        self._lecteur_label_temps = ctk.CTkLabel(
            cadre, text="00:00 / 00:00",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=BLANC)
        self._lecteur_label_temps.pack(pady=(5, 10))

        # Boutons contrôle
        btns = ctk.CTkFrame(cadre, fg_color="transparent")
        btns.pack(pady=(5, 10))

        # Stop
        ctk.CTkButton(
            btns, text="⏹️", command=self._lecteur_stop,
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, width=55, height=55,
            font=ctk.CTkFont(size=20, weight="bold"),
            corner_radius=12).pack(side="left", padx=4)

        # Play / Pause
        emoji_play = "▶️" if self._lecteur_pause else "⏸️"
        self._lecteur_btn_play = ctk.CTkButton(
            btns, text=emoji_play, command=self._lecteur_play_pause,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, width=70, height=55,
            font=ctk.CTkFont(size=22, weight="bold"),
            corner_radius=12)
        self._lecteur_btn_play.pack(side="left", padx=4)

        # Volume
        ctk.CTkLabel(
            btns, text="🔊",
            font=ctk.CTkFont(size=18),
            text_color=BLANC).pack(side="left", padx=(15, 5))

        self._lecteur_slider_vol = ctk.CTkSlider(
            btns, from_=0, to=100,
            command=self._lecteur_changer_volume,
            progress_color=JAUNE_SOLEIL,
            button_color=BLANC,
            button_hover_color=JAUNE_PALE,
            width=120)
        self._lecteur_slider_vol.set(self._lecteur_volume * 100)
        self._lecteur_slider_vol.pack(side="left", padx=5)

        # Démarrer mise à jour
        self._maj_progression_lecteur()

    def _maj_progression_lecteur(self):
        """Met à jour la barre de progression"""
        if not self._lecteur_actuel:
            return
        if not PYGAME_OK:
            return

        try:
            if pygame.mixer.music.get_busy() and not self._lecteur_pause:
                pos_ms = pygame.mixer.music.get_pos()
                pos_sec = pos_ms / 1000

                duree = self._get_duree_audio(self._lecteur_actuel)

                if duree > 0:
                    pct = pos_sec / duree
                    if pct > 1:
                        pct = 1
                    try:
                        self._lecteur_progress_bar.set(pct)
                    except Exception:
                        pass

                # Formater le temps
                try:
                    pos_str = self._formater_temps(pos_sec)
                    duree_str = self._formater_temps(duree)
                    self._lecteur_label_temps.configure(
                        text=f"{pos_str} / {duree_str}")
                except Exception:
                    pass

                # Vérifier fin de lecture
                if duree > 0 and pos_sec >= duree:
                    self._lecteur_stop()
                    return
        except Exception as e:
            print(f"⚠️ MAJ progression : {e}")

        # Reprogrammer dans 500ms
        try:
            self.after(500, self._maj_progression_lecteur)
        except Exception:
            pass

    def _formater_temps(self, secondes):
        """Convertit secondes en MM:SS"""
        mins = int(secondes // 60)
        secs = int(secondes % 60)
        return f"{mins:02d}:{secs:02d}"

    def _get_duree_audio(self, chemin):
        """Récupère la durée d'un audio (approximative via taille)"""
        try:
            # pygame.mixer.Sound peut donner la durée
            son = pygame.mixer.Sound(chemin)
            duree = son.get_length()
            return duree
        except Exception:
            # Fallback : estimer via taille du fichier (mp3 ~ 128kbps)
            try:
                taille = os.path.getsize(chemin)
                # 128 kbps = 16 ko/s
                return taille / (16 * 1024)
            except Exception:
                return 0

    # ═══════════════════════════════════════════
    # 🎮 CONTRÔLES LECTEUR
    # ═══════════════════════════════════════════

    def _lire_audio(self, chemin):
        """Charge et lit un audio"""
        if not PYGAME_OK:
            messagebox.showerror(
                "❌", "pygame non disponible !")
            return

        if not os.path.exists(chemin):
            messagebox.showerror(
                "❌", f"Fichier introuvable :\n{chemin}")
            return

        try:
            # Arrêter lecture précédente
            pygame.mixer.music.stop()

            # Charger nouveau
            pygame.mixer.music.load(chemin)
            pygame.mixer.music.set_volume(self._lecteur_volume)
            pygame.mixer.music.play()

            self._lecteur_actuel = chemin
            self._lecteur_en_lecture = True
            self._lecteur_pause = False

            notification_succes(
                self, "Lecture", f"▶️ {os.path.basename(chemin)[:30]}")

            # Rafraîchir la page
            self.afficher_lecteur_medias()

        except Exception as e:
            messagebox.showerror(
                "❌ Erreur", f"Lecture échouée :\n{str(e)}")

    def _lecteur_play_pause(self):
        """Toggle play/pause"""
        if not PYGAME_OK or not self._lecteur_actuel:
            return

        try:
            if self._lecteur_pause:
                pygame.mixer.music.unpause()
                self._lecteur_pause = False
                self._lecteur_btn_play.configure(text="⏸️")
                self._maj_progression_lecteur()
            else:
                pygame.mixer.music.pause()
                self._lecteur_pause = True
                self._lecteur_btn_play.configure(text="▶️")
        except Exception as e:
            print(f"⚠️ Play/Pause : {e}")

    def _lecteur_stop(self):
        """Arrête la lecture"""
        if not PYGAME_OK:
            return

        try:
            pygame.mixer.music.stop()
            self._lecteur_actuel = None
            self._lecteur_en_lecture = False
            self._lecteur_pause = False

            notification_succes(self, "Arrêté", "⏹️ Lecture stoppée")
            self.afficher_lecteur_medias()
        except Exception as e:
            print(f"⚠️ Stop : {e}")

    def _lecteur_changer_volume(self, valeur):
        """Change le volume"""
        if not PYGAME_OK:
            return
        try:
            self._lecteur_volume = valeur / 100
            pygame.mixer.music.set_volume(self._lecteur_volume)
        except Exception:
            pass

    # ═══════════════════════════════════════════
    # 📂 LISTE FICHIERS
    # ═══════════════════════════════════════════

    def _lister_audios(self):
        """Liste tous les MP3 dans les dossiers connus"""
        audios = []
        deja_vus = set()

        for dossier in DOSSIERS_AUDIOS:
            if not os.path.exists(dossier):
                continue
            try:
                for f in os.listdir(dossier):
                    if f.lower().endswith(('.mp3', '.wav')):
                        chemin = os.path.join(dossier, f)
                        chemin_abs = os.path.abspath(chemin)

                        # Éviter doublons
                        if chemin_abs in deja_vus:
                            continue
                        deja_vus.add(chemin_abs)

                        # Ignorer les fichiers du dossier sounds/ et videos_revision/
                        if "sounds" in chemin_abs.lower():
                            continue
                        if "videos_revision" in chemin_abs.lower():
                            continue
                        if "_test_voix" in f:
                            continue

                        try:
                            taille = os.path.getsize(chemin)
                            audios.append({
                                "nom": f,
                                "chemin": chemin,
                                "taille_ko": round(taille / 1024, 1),
                                "dossier": dossier
                            })
                        except Exception:
                            pass
            except Exception:
                pass

        # Trier par date (plus récent en premier)
        try:
            audios.sort(
                key=lambda a: os.path.getmtime(a["chemin"]),
                reverse=True)
        except Exception:
            pass

        return audios

    def _lister_videos(self):
        """Liste les vidéos générées"""
        videos = []
        if not os.path.exists(DOSSIER_VIDEOS):
            return videos

        try:
            for d in os.listdir(DOSSIER_VIDEOS):
                chemin_dossier = os.path.join(DOSSIER_VIDEOS, d)
                if not os.path.isdir(chemin_dossier):
                    continue
                html_file = os.path.join(chemin_dossier, "diaporama.html")
                if os.path.exists(html_file):
                    import json
                    meta = {}
                    meta_file = os.path.join(chemin_dossier, "meta.json")
                    if os.path.exists(meta_file):
                        try:
                            with open(meta_file, 'r', encoding='utf-8') as f:
                                meta = json.load(f)
                        except Exception:
                            pass

                    videos.append({
                        "nom": meta.get("nom_cours", d),
                        "dossier": chemin_dossier,
                        "html": html_file,
                        "meta": meta
                    })
        except Exception:
            pass

        return videos

    # ═══════════════════════════════════════════
    # 🎴 CARTES
    # ═══════════════════════════════════════════

    def _creer_carte_audio(self, parent, audio):
        """Crée une carte pour un audio"""
        est_actif = (self._lecteur_actuel == audio["chemin"])

        carte = ctk.CTkFrame(
            parent,
            fg_color=VERT_FOND_CORRECTION if est_actif else BLANC,
            corner_radius=12,
            border_width=3 if est_actif else 2,
            border_color=VERT_EMERAUDE if est_actif else VIOLET_PALE)
        carte.pack(fill="x", pady=4)

        # Infos
        infos = ctk.CTkFrame(carte, fg_color="transparent")
        infos.pack(side="left", fill="x", expand=True, padx=15, pady=12)

        emoji = "🎵 ▶️" if est_actif else "🎵"
        ctk.CTkLabel(
            infos, text=f"{emoji}  {audio['nom'][:45]}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(fill="x")

        ctk.CTkLabel(
            infos,
            text=f"📁 {audio['dossier']}  •  💾 {audio['taille_ko']} Ko",
            font=ctk.CTkFont(size=10),
            text_color=GRIS_DOUX, anchor="w").pack(fill="x")

        # Boutons
        btns = ctk.CTkFrame(carte, fg_color="transparent")
        btns.pack(side="right", padx=8, pady=8)

        ctk.CTkButton(
            btns, text="▶️" if not est_actif else "⏹️",
            command=lambda a=audio: self._action_audio(a),
            fg_color=VERT_EMERAUDE if not est_actif else ROUGE,
            hover_color=VERT_HOVER if not est_actif else ROUGE_CLAIR,
            text_color=BLANC, width=50, height=35,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8).pack(side="left", padx=2)

        ctk.CTkButton(
            btns, text="📤",
            command=lambda a=audio: self._exporter_audio(a),
            fg_color=BLEU_ROYAL, hover_color=BLEU_CIEL,
            text_color=BLANC, width=45, height=35,
            font=ctk.CTkFont(size=14),
            corner_radius=8).pack(side="left", padx=2)

        ctk.CTkButton(
            btns, text="🗑️",
            command=lambda a=audio: self._supprimer_audio(a),
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, width=45, height=35,
            font=ctk.CTkFont(size=14),
            corner_radius=8).pack(side="left", padx=2)

    def _creer_carte_video(self, parent, video):
        """Crée une carte pour une vidéo"""
        carte = ctk.CTkFrame(
            parent, fg_color=BLANC,
            corner_radius=12, border_width=2,
            border_color=ORANGE_PALE)
        carte.pack(fill="x", pady=4)

        infos = ctk.CTkFrame(carte, fg_color="transparent")
        infos.pack(side="left", fill="x", expand=True, padx=15, pady=12)

        ctk.CTkLabel(
            infos, text=f"🎬  {video['nom'][:45]}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(fill="x")

        meta = video.get("meta", {})
        details = (
            f"🎤 {meta.get('voix', '?')[:25]}  •  "
            f"🎨 {meta.get('style', '?')[:20]}  •  "
            f"📊 {meta.get('nb_slides', '?')} slides")
        ctk.CTkLabel(
            infos, text=details,
            font=ctk.CTkFont(size=10),
            text_color=GRIS_DOUX, anchor="w").pack(fill="x")

        # Boutons
        btns = ctk.CTkFrame(carte, fg_color="transparent")
        btns.pack(side="right", padx=8, pady=8)

        ctk.CTkButton(
            btns, text="▶️ Ouvrir",
            command=lambda v=video: self._ouvrir_video(v),
            fg_color=ORANGE_DORE, hover_color=OR_MODERNE,
            text_color=BLANC, height=35, width=90,
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=8).pack(side="left", padx=2)

        ctk.CTkButton(
            btns, text="📤",
            command=lambda v=video: self._exporter_video(v),
            fg_color=BLEU_ROYAL, hover_color=BLEU_CIEL,
            text_color=BLANC, width=45, height=35,
            font=ctk.CTkFont(size=14),
            corner_radius=8).pack(side="left", padx=2)

        ctk.CTkButton(
            btns, text="🗑️",
            command=lambda v=video: self._supprimer_video_media(v),
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, width=45, height=35,
            font=ctk.CTkFont(size=14),
            corner_radius=8).pack(side="left", padx=2)

    # ═══════════════════════════════════════════
    # 🎬 ACTIONS
    # ═══════════════════════════════════════════

    def _action_audio(self, audio):
        """Lire ou arrêter un audio"""
        if self._lecteur_actuel == audio["chemin"]:
            self._lecteur_stop()
        else:
            self._lire_audio(audio["chemin"])

    def _exporter_audio(self, audio):
        """Exporte un audio vers où l'utilisateur veut"""
        destination = filedialog.asksaveasfilename(
            title="Exporter l'audio",
            initialfile=audio["nom"],
            defaultextension=".mp3",
            filetypes=[("MP3", "*.mp3"), ("WAV", "*.wav")])
        if destination:
            try:
                shutil.copy2(audio["chemin"], destination)
                notification_succes(
                    self, "Exporté !",
                    f"📤 {os.path.basename(destination)}")
                messagebox.showinfo(
                    "✅ Exporté",
                    f"📁 {destination}")
            except Exception as e:
                messagebox.showerror("❌", str(e))

    def _supprimer_audio(self, audio):
        """Supprime un audio"""
        if not messagebox.askyesno(
                "🗑️ Supprimer",
                f"Supprimer cet audio ?\n\n"
                f"📄 {audio['nom']}\n\n"
                f"⚠️ Action irréversible."):
            return
        try:
            # Arrêter si en lecture
            if self._lecteur_actuel == audio["chemin"]:
                self._lecteur_stop()

            os.remove(audio["chemin"])
            notification_succes(self, "Supprimé", "🗑️ Audio supprimé")
            self.afficher_lecteur_medias()
        except Exception as e:
            messagebox.showerror("❌", str(e))

    def _ouvrir_video(self, video):
        """Ouvre une vidéo dans le navigateur"""
        try:
            chemin_abs = os.path.abspath(video["html"])
            webbrowser.open(f"file:///{chemin_abs}")
            notification_succes(
                self, "Vidéo ouverte",
                "🌐 Dans le navigateur")
        except Exception as e:
            messagebox.showerror("❌", str(e))

    def _exporter_video(self, video):
        """Exporte une vidéo (zip du dossier)"""
        destination = filedialog.asksaveasfilename(
            title="Exporter la vidéo (ZIP)",
            initialfile=f"{video['nom'][:30]}.zip",
            defaultextension=".zip",
            filetypes=[("ZIP", "*.zip")])
        if destination:
            try:
                shutil.make_archive(
                    destination.replace(".zip", ""),
                    'zip', video["dossier"])
                notification_succes(
                    self, "Exporté !",
                    "📤 Vidéo exportée en ZIP")
                messagebox.showinfo(
                    "✅ Exporté",
                    f"📁 {destination}\n\n"
                    f"💡 Dézippe pour ouvrir 'diaporama.html'")
            except Exception as e:
                messagebox.showerror("❌", str(e))

    def _supprimer_video_media(self, video):
        """Supprime un dossier vidéo"""
        if not messagebox.askyesno(
                "🗑️ Supprimer",
                f"Supprimer cette vidéo ?\n\n"
                f"🎬 {video['nom']}\n\n"
                f"⚠️ Action irréversible."):
            return
        try:
            shutil.rmtree(video["dossier"])
            notification_succes(self, "Supprimée", "🗑️ Vidéo supprimée")
            self.afficher_lecteur_medias()
        except Exception as e:
            messagebox.showerror("❌", str(e))

    # ═══════════════════════════════════════════
    # 🛠️ HELPERS UI
    # ═══════════════════════════════════════════

    def _creer_titre_section(self, parent, texte, couleur):
        cadre = ctk.CTkFrame(parent, fg_color=couleur, corner_radius=10)
        cadre.pack(fill="x", pady=(15, 5))
        ctk.CTkLabel(
            cadre, text=texte,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=BLANC).pack(pady=10)

    def _afficher_vide(self, parent, message):
        cadre = ctk.CTkFrame(parent, fg_color=GRIS_PERLE, corner_radius=10)
        cadre.pack(fill="x", pady=5)
        ctk.CTkLabel(
            cadre, text=message,
            font=ctk.CTkFont(size=12),
            text_color=GRIS_DOUX, justify="center").pack(pady=20)