# ui/notifications_page.py - Page Paramètres Notifications NOKIROVA 🔔

import customtkinter as ctk
from tkinter import messagebox
from notifications import (
    charger_params, sauvegarder_params, maj_param,
    notification_succes, notification_rappel,
    notification_motivation, notification_windows,
    PLYER_OK
)
from ui.base import (
    VERT_EMERAUDE, VERT_HOVER, VERT_CLAIR, VERT_CORRECTION,
    VERT_FOND_CORRECTION,
    BLEU_ROYAL, BLEU_CIEL, BLEU_TRES_PALE,
    JAUNE_SOLEIL, JAUNE_PALE, OR_MODERNE,
    VIOLET_PREMIUM, VIOLET_LAVANDE, VIOLET_PALE,
    ROSE_SAKURA, ROSE_PALE,
    ORANGE_DORE, ORANGE_CLAIR, ORANGE_PALE,
    ROUGE, ROUGE_CLAIR,
    BLANC, GRIS_TEXTE, GRIS_DOUX, GRIS_PERLE
)


class NotificationsPageMixin:

    # ═══════════════════════════════════════════
    # 🔔 PAGE NOTIFICATIONS
    # ═══════════════════════════════════════════

    def afficher_notifications_params(self):
        self.vider_zone()
        self.afficher_titre("Notifications", "🔔", VIOLET_PREMIUM)

        params = charger_params()

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
            text="🔔 Gère tes notifications pour rester motivé !\n"
                 "💡 Active les rappels pour ne plus oublier tes révisions.",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=VIOLET_PREMIUM,
            justify="center").pack(pady=12)

        # ── Vérif Plyer ──
        if not PLYER_OK:
            warn = ctk.CTkFrame(
                scroll, fg_color=ROUGE_CLAIR, corner_radius=12)
            warn.pack(fill="x", pady=8)
            ctk.CTkLabel(
                warn,
                text="⚠️  Plyer non installé\n"
                     "💡 pip install plyer (pour notifs Windows)",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=BLANC, justify="center").pack(pady=10)
        else:
            ok = ctk.CTkFrame(
                scroll, fg_color=VERT_FOND_CORRECTION, corner_radius=12)
            ok.pack(fill="x", pady=5)
            ctk.CTkLabel(
                ok,
                text="✅  Notifications Windows actives !",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=VERT_CORRECTION).pack(pady=8)

        # ── SECTION 1 : ACTIVATION ──
        self._creer_section_titre(scroll, "🔔  ACTIVATION GÉNÉRALE",
                                  VIOLET_PREMIUM)

        self._creer_switch(
            scroll, "🪟 Notifications Windows natives",
            "Affiche les vraies notifs Windows en arrière-plan",
            "notif_windows", params)

        self._creer_switch(
            scroll, "⏰ Rappels avant les tâches",
            "Sois prévenu(e) avant chaque tâche planifiée",
            "notif_rappels", params)

        self._creer_switch(
            scroll, "💪 Notifications de motivation",
            "Encouragements quand tu progresses",
            "notif_motivation", params)

        self._creer_switch(
            scroll, "🌅 Notification du matin",
            "Aperçu de ta journée à l'heure choisie",
            "notif_matin", params)

        # ── SECTION 2 : RÉGLAGES ──
        self._creer_section_titre(scroll, "⚙️  RÉGLAGES",
                                  ORANGE_DORE)

        # Heure du matin
        cadre_h = ctk.CTkFrame(scroll, fg_color=BLANC, corner_radius=12,
                               border_width=2, border_color=JAUNE_PALE)
        cadre_h.pack(fill="x", pady=5)

        ctk.CTkLabel(
            cadre_h, text="🌅  Heure de la notification du matin",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", padx=15, pady=(12, 2))

        ctk.CTkLabel(
            cadre_h, text="Format HH:MM (ex: 08:00)",
            font=ctk.CTkFont(size=11),
            text_color=GRIS_DOUX, anchor="w").pack(
            fill="x", padx=15, pady=(0, 5))

        frame_h = ctk.CTkFrame(cadre_h, fg_color="transparent")
        frame_h.pack(fill="x", padx=15, pady=(0, 12))

        ent_heure = ctk.CTkEntry(
            frame_h, height=38, width=120,
            font=ctk.CTkFont(size=14, weight="bold"))
        ent_heure.pack(side="left")
        ent_heure.insert(0, params.get("heure_matin", "08:00"))

        def sauv_heure():
            val = ent_heure.get().strip()
            try:
                from datetime import datetime
                datetime.strptime(val, "%H:%M")
                maj_param("heure_matin", val)
                notification_succes(
                    self, "Sauvegardé !", f"🌅 Heure : {val}")
            except Exception:
                messagebox.showwarning(
                    "⚠️", "Format invalide ! Ex: 08:00")

        ctk.CTkButton(
            frame_h, text="💾 Sauvegarder",
            command=sauv_heure,
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8).pack(side="left", padx=10)

        # Minutes avant tâche
        cadre_m = ctk.CTkFrame(scroll, fg_color=BLANC, corner_radius=12,
                               border_width=2, border_color=ORANGE_PALE)
        cadre_m.pack(fill="x", pady=5)

        ctk.CTkLabel(
            cadre_m, text="⏰  Minutes avant chaque tâche",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", padx=15, pady=(12, 2))

        ctk.CTkLabel(
            cadre_m, text="Combien de minutes avant être prévenu(e) ?",
            font=ctk.CTkFont(size=11),
            text_color=GRIS_DOUX, anchor="w").pack(
            fill="x", padx=15, pady=(0, 5))

        frame_m = ctk.CTkFrame(cadre_m, fg_color="transparent")
        frame_m.pack(fill="x", padx=15, pady=(0, 12))

        options_min = ["5 min", "10 min", "15 min", "30 min", "60 min"]
        val_actuelle = params.get("minutes_avant_tache", 10)
        defaut = f"{val_actuelle} min"
        if defaut not in options_min:
            defaut = "10 min"

        def changer_min(v):
            mins = int(v.replace(" min", ""))
            maj_param("minutes_avant_tache", mins)
            notification_succes(
                self, "Sauvegardé !", f"⏰ {mins} minutes avant")

        menu_min = ctk.CTkOptionMenu(
            frame_m, values=options_min, command=changer_min,
            fg_color=ORANGE_CLAIR, button_color=ORANGE_DORE,
            text_color=BLANC, height=38, width=150,
            font=ctk.CTkFont(size=13, weight="bold"))
        menu_min.set(defaut)
        menu_min.pack(side="left")

        # ── SECTION 3 : MODE NE PAS DÉRANGER ──
        self._creer_section_titre(scroll, "🔕  MODE SILENCE",
                                  ROUGE)

        self._creer_switch(
            scroll, "🔕 Mode 'Ne pas déranger'",
            "Désactive TOUTES les notifications temporairement",
            "ne_pas_deranger", params)

        # ── SECTION 4 : TESTS ──
        self._creer_section_titre(scroll, "🧪  TESTS",
                                  BLEU_ROYAL)

        cadre_test = ctk.CTkFrame(scroll, fg_color=BLEU_TRES_PALE,
                                  corner_radius=12)
        cadre_test.pack(fill="x", pady=5)

        ctk.CTkLabel(
            cadre_test,
            text="🧪  Teste tes notifications maintenant !",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=BLEU_ROYAL).pack(pady=(12, 5))

        # Boutons de test
        btns_test = ctk.CTkFrame(cadre_test, fg_color="transparent")
        btns_test.pack(fill="x", padx=15, pady=(5, 12))

        ctk.CTkButton(
            btns_test, text="⏰  Test Rappel",
            command=lambda: notification_rappel(
                self, "Test Rappel",
                "🎯 Voilà à quoi ressemble un rappel de tâche !"),
            fg_color=ORANGE_DORE, hover_color=OR_MODERNE,
            text_color=BLANC, height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8).pack(side="left", padx=3,
                                  expand=True, fill="x")

        ctk.CTkButton(
            btns_test, text="💪  Test Motivation",
            command=lambda: notification_motivation(
                self, "Tu es génial(e) !",
                "💎 Continue comme ça, tu vas y arriver !"),
            fg_color=VIOLET_PREMIUM, hover_color=VIOLET_LAVANDE,
            text_color=BLANC, height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8).pack(side="left", padx=3,
                                  expand=True, fill="x")

        ctk.CTkButton(
            btns_test, text="🪟  Test Windows",
            command=lambda: self._test_windows(),
            fg_color=BLEU_ROYAL, hover_color=BLEU_CIEL,
            text_color=BLANC, height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8).pack(side="left", padx=3,
                                  expand=True, fill="x")

        # ── SECTION 5 : RESET ──
        self._creer_section_titre(scroll, "🔄  RÉINITIALISATION",
                                  GRIS_DOUX)

        ctk.CTkButton(
            scroll, text="🔄  Réinitialiser les paramètres par défaut",
            command=self._reset_params,
            fg_color=GRIS_DOUX, hover_color=ROUGE_CLAIR,
            text_color=BLANC, height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10).pack(fill="x", pady=10)

        # Espace bas
        ctk.CTkLabel(scroll, text="", height=15).pack()

    # ═══════════════════════════════════════════
    # 🛠️ HELPERS
    # ═══════════════════════════════════════════

    def _creer_section_titre(self, parent, texte, couleur):
        cadre = ctk.CTkFrame(parent, fg_color=couleur, corner_radius=10)
        cadre.pack(fill="x", pady=(15, 5))
        ctk.CTkLabel(
            cadre, text=texte,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=BLANC).pack(pady=10)

    def _creer_switch(self, parent, titre, desc, cle_param, params):
        cadre = ctk.CTkFrame(parent, fg_color=BLANC, corner_radius=12,
                             border_width=2, border_color=VIOLET_PALE)
        cadre.pack(fill="x", pady=4)

        ligne = ctk.CTkFrame(cadre, fg_color="transparent")
        ligne.pack(fill="x", padx=15, pady=10)

        # Texte
        gauche = ctk.CTkFrame(ligne, fg_color="transparent")
        gauche.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            gauche, text=titre,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(fill="x")

        ctk.CTkLabel(
            gauche, text=desc,
            font=ctk.CTkFont(size=11),
            text_color=GRIS_DOUX, anchor="w").pack(fill="x")

        # Switch
        var = ctk.BooleanVar(value=params.get(cle_param, True))

        def changer():
            maj_param(cle_param, var.get())
            etat = "activé" if var.get() else "désactivé"
            notification_succes(
                self, "Modifié", f"🔔 {titre[:25]} {etat}")

        sw = ctk.CTkSwitch(
            ligne, text="", variable=var, command=changer,
            progress_color=VERT_EMERAUDE,
            button_color=BLANC, button_hover_color=GRIS_PERLE,
            width=50)
        sw.pack(side="right", padx=10)

    def _test_windows(self):
        """Teste les notifs Windows"""
        if not PLYER_OK:
            messagebox.showwarning(
                "⚠️", "Plyer non installé !\n"
                      "Tape : pip install plyer")
            return
        ok = notification_windows(
            "🌸 Test NOKIROVA",
            "Ta notification Windows fonctionne ! 🎉")
        if ok:
            notification_succes(
                self, "Envoyée !",
                "🪟 Regarde dans le coin Windows !")
        else:
            messagebox.showwarning(
                "⚠️", "Notif Windows désactivée ou bloquée.\n"
                      "Vérifie les paramètres Windows.")

    def _reset_params(self):
        if messagebox.askyesno(
                "🔄 Réinitialiser",
                "Remettre TOUS les paramètres par défaut ?\n"
                "(Notifications activées, 10 min, 08:00)"):
            from notifications import PARAMS_DEFAUT
            sauvegarder_params(PARAMS_DEFAUT.copy())
            notification_succes(
                self, "Réinitialisé !", "🔄 Paramètres par défaut")
            self.afficher_notifications_params()