# ui/pomodoro.py - Pomodoro Timer NOKIROVA 🌸 (ARRIÈRE-PLAN)

import customtkinter as ctk
from tkinter import messagebox
import os
import time
import database as db
from ui.base import (VERT_EMERAUDE, VERT_HOVER,
                     BLEU_ROYAL, BLEU_TRES_PALE,
                     JAUNE_SOLEIL, JAUNE_PALE, OR_MODERNE,
                     ORANGE_DORE, ORANGE_CLAIR, ORANGE_PALE,
                     ROUGE, ROUGE_CLAIR,
                     BLANC, GRIS_TEXTE, VIOLET_PREMIUM)


SON_POMODORO_FIN = "sounds/pomodoro_fin.mp3"


def jouer_son(chemin):
    """Joue un son MP3 (multi-méthodes)"""
    if not os.path.exists(chemin):
        print(f"⚠️ Son introuvable : {chemin}")
        return False
    try:
        # Méthode 1 : Windows winsound
        import winsound
        winsound.PlaySound(None, winsound.SND_PURGE)
        # Pour MP3, on utilise une autre méthode
        try:
            from playsound import playsound
            import threading
            threading.Thread(
                target=lambda: playsound(chemin),
                daemon=True).start()
            return True
        except Exception:
            pass

        # Méthode 2 : os.startfile (ouvre dans lecteur)
        try:
            os.startfile(chemin)
            return True
        except Exception:
            pass
    except Exception as e:
        print(f"⚠️ Son : {e}")
    return False


class PomodoroMixin:

    # ═══════════════════════════════════════════
    # ⏱️ POMODORO (avec arrière-plan)
    # ═══════════════════════════════════════════

    def afficher_pomodoro(self):
        self.vider_zone()
        self.afficher_titre("Pomodoro Timer", "🍅", ORANGE_DORE)

        # ── Info ──
        info = ctk.CTkFrame(
            self.zone_principale,
            fg_color=ORANGE_PALE, corner_radius=12)
        info.pack(fill="x", pady=5)
        ctk.CTkLabel(
            info,
            text="🍅 Technique Pomodoro : 25 min de travail • 5 min de pause\n"
                 "✨ Le timer CONTINUE même si tu changes de page ou minimises !\n"
                 "🔔 +20 XP par session • Son et notif à la fin",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=BLANC, justify="center").pack(pady=10)

        # ── Si timer en cours, montrer juste l'état ──
        if self._pomo_en_cours or self._pomo_pause_active:
            self._afficher_timer_en_cours()
            return

        # ── Configuration ──
        frame_config = ctk.CTkFrame(
            self.zone_principale,
            fg_color=JAUNE_PALE, corner_radius=14)
        frame_config.pack(fill="x", pady=8)

        ctk.CTkLabel(frame_config, text="⚙️  CONFIGURATION",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=ORANGE_DORE).pack(pady=(12, 5))

        frame_durees = ctk.CTkFrame(frame_config, fg_color="transparent")
        frame_durees.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkLabel(frame_durees, text="⏱️ Travail :",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE).pack(side="left", padx=(0, 5))

        self.menu_duree_travail = ctk.CTkOptionMenu(
            frame_durees,
            values=["15", "20", "25", "30", "45", "50"],
            fg_color=ORANGE_DORE, text_color=BLANC,
            button_color=ORANGE_CLAIR, corner_radius=8, width=80,
            command=self._maj_duree_travail)
        self.menu_duree_travail.set("25")
        self.menu_duree_travail.pack(side="left", padx=5)

        ctk.CTkLabel(frame_durees, text="min",
                     text_color=GRIS_TEXTE).pack(side="left", padx=(0, 15))

        ctk.CTkLabel(frame_durees, text="☕ Pause :",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=GRIS_TEXTE).pack(side="left", padx=(0, 5))

        self.menu_duree_pause = ctk.CTkOptionMenu(
            frame_durees,
            values=["3", "5", "10", "15"],
            fg_color=VERT_EMERAUDE, text_color=BLANC,
            button_color=VERT_HOVER, corner_radius=8, width=80)
        self.menu_duree_pause.set("5")
        self.menu_duree_pause.pack(side="left", padx=5)

        ctk.CTkLabel(frame_durees, text="min",
                     text_color=GRIS_TEXTE).pack(side="left")

        # ── Timer ──
        carte_timer = ctk.CTkFrame(
            self.zone_principale,
            fg_color=ORANGE_DORE, corner_radius=20, height=220)
        carte_timer.pack(fill="x", pady=15)
        carte_timer.pack_propagate(False)

        self.label_phase_pomo = ctk.CTkLabel(
            carte_timer, text="🍅  PRÊT À TRAVAILLER",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=BLANC)
        self.label_phase_pomo.pack(pady=(25, 10))

        mins = self._pomo_restant // 60
        secs = self._pomo_restant % 60
        self.label_timer = ctk.CTkLabel(
            carte_timer,
            text=f"{mins:02d}:{secs:02d}",
            font=ctk.CTkFont(family="Segoe UI", size=72, weight="bold"),
            text_color=BLANC)
        self.label_timer.pack()

        self.progress_pomo = ctk.CTkProgressBar(
            carte_timer, progress_color=BLANC,
            fg_color=ORANGE_CLAIR, height=12, corner_radius=6)
        self.progress_pomo.set(0)
        self.progress_pomo.pack(fill="x", padx=40, pady=15)

        # ── Boutons contrôle ──
        frame_btns = ctk.CTkFrame(self.zone_principale, fg_color="transparent")
        frame_btns.pack(fill="x", pady=10)

        self.btn_start_pomo = ctk.CTkButton(
            frame_btns, text="▶️  DÉMARRER",
            command=self._demarrer_pomodoro,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, corner_radius=14, height=55,
            font=ctk.CTkFont(size=16, weight="bold"))
        self.btn_start_pomo.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_pause_pomo = ctk.CTkButton(
            frame_btns, text="⏸️  PAUSE",
            command=self._pause_pomodoro,
            fg_color=JAUNE_SOLEIL, hover_color=OR_MODERNE,
            text_color=GRIS_TEXTE, corner_radius=14, height=55,
            font=ctk.CTkFont(size=16, weight="bold"),
            state="disabled")
        self.btn_pause_pomo.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_reset_pomo = ctk.CTkButton(
            frame_btns, text="🔄  RESET",
            command=self._reset_pomodoro,
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, corner_radius=14, height=55,
            font=ctk.CTkFont(size=16, weight="bold"))
        self.btn_reset_pomo.pack(side="left", padx=5, expand=True, fill="x")

        # ── Stats ──
        try:
            stats_pomo = db.get_stats_pomodoro()
        except Exception:
            stats_pomo = {"total_sessions": 0, "total_minutes": 0}

        carte_stats = ctk.CTkFrame(
            self.zone_principale,
            fg_color=BLEU_TRES_PALE, corner_radius=15)
        carte_stats.pack(fill="x", pady=10)

        ctk.CTkLabel(
            carte_stats,
            text=f"📊  TES STATS POMODORO :  "
                 f"🍅 {stats_pomo.get('total_sessions', 0)} sessions  •  "
                 f"⏱️ {stats_pomo.get('total_minutes', 0)} min de travail",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=BLEU_ROYAL).pack(pady=15)

    # ═══════════════════════════════════════════
    # 🔄 AFFICHAGE QUAND TIMER EN COURS
    # ═══════════════════════════════════════════

    def _afficher_timer_en_cours(self):
        """Affiche un mode 'timer actif' quand on revient sur la page"""
        cadre = ctk.CTkFrame(
            self.zone_principale, fg_color=VIOLET_PREMIUM,
            corner_radius=20)
        cadre.pack(fill="both", expand=True, pady=20)

        emoji_phase = "⏸️" if self._pomo_pause_active else "🍅"
        texte_phase = ("EN PAUSE" if self._pomo_pause_active
                       else "TIMER EN COURS")

        ctk.CTkLabel(
            cadre, text=f"{emoji_phase}  {texte_phase}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=BLANC).pack(pady=(40, 15))

        mins = self._pomo_restant // 60
        secs = self._pomo_restant % 60
        self.label_timer_actif = ctk.CTkLabel(
            cadre, text=f"{mins:02d}:{secs:02d}",
            font=ctk.CTkFont(size=90, weight="bold"),
            text_color=BLANC)
        self.label_timer_actif.pack(pady=10)

        ctk.CTkLabel(
            cadre,
            text="💡 Le timer continue même si tu changes de page !\n"
                 "Tu seras notifié(e) à la fin avec un son.",
            font=ctk.CTkFont(size=12),
            text_color=BLANC, justify="center").pack(pady=15)

        # Boutons
        btns = ctk.CTkFrame(cadre, fg_color="transparent")
        btns.pack(pady=20)

        if self._pomo_pause_active:
            ctk.CTkButton(
                btns, text="▶️  REPRENDRE",
                command=self._demarrer_pomodoro,
                fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
                text_color=BLANC, corner_radius=12, height=50,
                width=180,
                font=ctk.CTkFont(size=14, weight="bold")).pack(
                side="left", padx=5)
        else:
            ctk.CTkButton(
                btns, text="⏸️  PAUSE",
                command=self._pause_pomodoro,
                fg_color=JAUNE_SOLEIL, hover_color=OR_MODERNE,
                text_color=GRIS_TEXTE, corner_radius=12, height=50,
                width=180,
                font=ctk.CTkFont(size=14, weight="bold")).pack(
                side="left", padx=5)

        ctk.CTkButton(
            btns, text="🛑  ARRÊTER",
            command=self._arreter_pomodoro,
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, corner_radius=12, height=50,
            width=180,
            font=ctk.CTkFont(size=14, weight="bold")).pack(
            side="left", padx=5)

    # ═══════════════════════════════════════════
    # ⏱️ LOGIQUE TIMER
    # ═══════════════════════════════════════════

    def _maj_duree_travail(self, valeur):
        if not self._pomo_en_cours:
            try:
                self._pomo_total = int(valeur) * 60
                self._pomo_restant = self._pomo_total
                mins = self._pomo_restant // 60
                self.label_timer.configure(text=f"{mins:02d}:00")
                self.progress_pomo.set(0)
            except Exception:
                pass

    def _demarrer_pomodoro(self):
        if self._pomo_pause_active:
            self._pomo_pause_active = False
            self._pomo_en_cours = True
            self.afficher_pomodoro()
            self._tick_pomodoro()
            return

        if self._pomo_en_cours:
            return

        try:
            self._pomo_total = int(self.menu_duree_travail.get()) * 60
        except Exception:
            self._pomo_total = 25 * 60

        self._pomo_restant = self._pomo_total
        self._pomo_en_cours = True
        self._pomo_pause_active = False
        self._pomo_phase = "travail"

        self._tick_pomodoro()

        from notifications import notification_succes
        notification_succes(
            self, "Pomodoro lancé !",
            f"🍅 {self._pomo_total // 60} min de travail")

    def _tick_pomodoro(self):
        """Décompte le timer - tourne TOUJOURS en arrière-plan"""
        if not self._pomo_en_cours or self._pomo_pause_active:
            return

        if self._pomo_restant <= 0:
            self._fin_session_pomodoro()
            return

        # MAJ visuelle SI on est sur la page Pomodoro
        try:
            mins = self._pomo_restant // 60
            secs = self._pomo_restant % 60
            texte_temps = f"{mins:02d}:{secs:02d}"

            if hasattr(self, 'label_timer'):
                try:
                    self.label_timer.configure(text=texte_temps)
                    progression = 1 - (self._pomo_restant / self._pomo_total)
                    self.progress_pomo.set(progression)
                except Exception:
                    pass

            if hasattr(self, 'label_timer_actif'):
                try:
                    self.label_timer_actif.configure(text=texte_temps)
                except Exception:
                    pass
        except Exception:
            pass

        self._pomo_restant -= 1
        # ⚡ Tick toutes les 1000ms (continue en arrière-plan)
        self._pomo_timer = self.after(1000, self._tick_pomodoro)

    def _pause_pomodoro(self):
        if self._pomo_timer:
            try:
                self.after_cancel(self._pomo_timer)
            except Exception:
                pass
            self._pomo_timer = None

        self._pomo_pause_active = True
        self._pomo_en_cours = False

        from notifications import notification_succes
        notification_succes(self, "Pause", "⏸️ Timer en pause")

        # Si on est sur la page, rafraîchir
        try:
            self.afficher_pomodoro()
        except Exception:
            pass

    def _reset_pomodoro(self):
        if self._pomo_timer:
            try:
                self.after_cancel(self._pomo_timer)
            except Exception:
                pass
            self._pomo_timer = None

        self._pomo_en_cours = False
        self._pomo_pause_active = False

        try:
            self._pomo_total = int(self.menu_duree_travail.get()) * 60
        except Exception:
            self._pomo_total = 25 * 60

        self._pomo_restant = self._pomo_total

        try:
            mins = self._pomo_restant // 60
            self.label_timer.configure(text=f"{mins:02d}:00")
            self.label_phase_pomo.configure(text="🍅  PRÊT À TRAVAILLER")
            self.progress_pomo.set(0)
            self.btn_start_pomo.configure(
                text="▶️  DÉMARRER", state="normal")
            self.btn_pause_pomo.configure(state="disabled")
        except Exception:
            pass

    def _arreter_pomodoro(self):
        """Arrête complètement le timer"""
        if not messagebox.askyesno(
                "🛑 Arrêter",
                "Arrêter le timer Pomodoro ?\n"
                "⚠️ Ta session ne sera pas comptée."):
            return

        if self._pomo_timer:
            try:
                self.after_cancel(self._pomo_timer)
            except Exception:
                pass
            self._pomo_timer = None

        self._pomo_en_cours = False
        self._pomo_pause_active = False
        self._pomo_restant = 25 * 60
        self._pomo_total = 25 * 60

        from notifications import notification_succes
        notification_succes(self, "Arrêté", "🛑 Timer arrêté")
        self.afficher_pomodoro()

    def _fin_session_pomodoro(self):
        """Fin de session : son + notif + sauvegarde"""
        if self._pomo_timer:
            try:
                self.after_cancel(self._pomo_timer)
            except Exception:
                pass
            self._pomo_timer = None

        self._pomo_en_cours = False

        # 🔊 JOUER LE SON
        jouer_son(SON_POMODORO_FIN)

        # 💾 SAUVEGARDER
        try:
            duree_min = self._pomo_total // 60
            db.enregistrer_session_pomodoro(duree_min)
        except Exception as e:
            print(f"⚠️ Sauvegarde pomodoro : {e}")

        # 🎁 XP
        self._recompenser(20, "🍅 Session Pomodoro terminée !")

        # 🔔 NOTIFICATIONS
        from notifications import notification_succes, notification_windows
        notification_succes(
            self, "Bravo !", "🍅 Session terminée ! +20 XP")
        notification_windows(
            "🍅 NOKIROVA - Session terminée !",
            f"Bravo ! Tu as terminé une session de "
            f"{self._pomo_total // 60} minutes !\n"
            f"⭐ +20 XP gagnés")

        # 📥 REVENIR SUR LA PAGE
        try:
            self.afficher_pomodoro()
        except Exception:
            pass

        # 🎯 POPUP FINALE
        try:
            duree_pause = self.menu_duree_pause.get()
        except Exception:
            duree_pause = "5"

        if messagebox.askyesno(
                "🍅 Session terminée !",
                f"🎉 Bravo ! Tu as terminé une session de "
                f"{self._pomo_total // 60} minutes !\n\n"
                f"⭐ +20 XP gagnés\n\n"
                f"☕ Veux-tu lancer une pause de "
                f"{duree_pause} minutes ?"):
            self._lancer_pause()

    def _lancer_pause(self):
        try:
            duree_pause = int(self.menu_duree_pause.get()) * 60
        except Exception:
            duree_pause = 5 * 60

        self._pomo_total = duree_pause
        self._pomo_restant = duree_pause
        self._pomo_en_cours = True
        self._pomo_pause_active = False

        from notifications import notification_succes
        notification_succes(
            self, "Pause lancée !",
            f"☕ {duree_pause // 60} min de pause")

        try:
            self.afficher_pomodoro()
        except Exception:
            pass

        self._tick_pomodoro()