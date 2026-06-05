# ui/graphiques.py - Graphiques de progression NOKIROVA 🌸

import customtkinter as ctk
import database as db
from ui.base import (VERT_EMERAUDE, VERT_CORRECTION,
                     BLEU_ROYAL, BLEU_TRES_PALE,
                     VIOLET_PREMIUM, VIOLET_LAVANDE,
                     JAUNE_PALE, ORANGE_DORE, ORANGE_PALE,
                     ROUGE, ROSE_PALE,
                     BLANC, BLANC_CASSE, GRIS_TEXTE)


class GraphiquesMixin:

    # ═══════════════════════════════════════════
    # 📈 GRAPHIQUES DE PROGRESSION
    # ═══════════════════════════════════════════

    def afficher_graphiques(self):
        self.vider_zone()
        self.afficher_titre("Graphiques de progression", "📈", VIOLET_PREMIUM)

        stats = db.get_stats()
        try:
            stats_pomo = db.get_stats_pomodoro()
        except Exception:
            stats_pomo = {"total_sessions": 0, "total_minutes": 0}

        # ── Conteneur scrollable ──
        scroll = ctk.CTkScrollableFrame(
            self.zone_principale,
            fg_color=BLANC_CASSE, corner_radius=0)
        scroll.pack(fill="both", expand=True, pady=5)

        # ── BLOC 1 : Niveau / XP / Streak ──
        bloc_niveau = ctk.CTkFrame(
            scroll, fg_color=JAUNE_PALE, corner_radius=15)
        bloc_niveau.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(bloc_niveau, text="⭐  PROGRESSION GLOBALE",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=ORANGE_DORE).pack(pady=(15, 10))

        xp_actuel = stats["xp"] % 100
        self._creer_ligne_graphique(
            bloc_niveau,
            f"Niveau {stats['niveau']} ({xp_actuel}/100 XP)",
            xp_actuel, 100, VERT_EMERAUDE)
        self._creer_ligne_graphique(
            bloc_niveau,
            f"Streak ({stats['streak']} jours)",
            min(stats['streak'], 30), 30, ORANGE_DORE)

        ctk.CTkLabel(
            bloc_niveau,
            text=f"✨ Total : {stats['xp']} XP cumulés",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=GRIS_TEXTE).pack(pady=(5, 15))

        # ── BLOC 2 : Activité ──
        bloc_activite = ctk.CTkFrame(
            scroll, fg_color=BLEU_TRES_PALE, corner_radius=15)
        bloc_activite.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(bloc_activite, text="📊  STATISTIQUES D'ACTIVITÉ",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=BLEU_ROYAL).pack(pady=(15, 10))

        max_act = max(
            stats['cours_importes'],
            stats['questions_posees'],
            stats['audios_crees'], 10)

        self._creer_ligne_graphique(
            bloc_activite,
            f"📚 Cours importés ({stats['cours_importes']})",
            stats['cours_importes'], max_act, VERT_EMERAUDE)
        self._creer_ligne_graphique(
            bloc_activite,
            f"💬 Questions posées ({stats['questions_posees']})",
            stats['questions_posees'], max_act, VIOLET_PREMIUM)
        self._creer_ligne_graphique(
            bloc_activite,
            f"🎧 Audios créés ({stats['audios_crees']})",
            stats['audios_crees'], max_act, BLEU_ROYAL)

        ctk.CTkLabel(bloc_activite, text="", height=10).pack()

        # ── BLOC 3 : QCM ──
        bloc_qcm = ctk.CTkFrame(
            scroll, fg_color=ROSE_PALE, corner_radius=15)
        bloc_qcm.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(bloc_qcm, text="🎯  PERFORMANCE QCM",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=VIOLET_PREMIUM).pack(pady=(15, 10))

        qcm_reussis = stats.get('qcm_reussis', 0)
        qcm_rates = stats.get('qcm_rates', 0)
        qcm_total = qcm_reussis + qcm_rates
        taux_qcm = int((qcm_reussis / qcm_total) * 100) if qcm_total > 0 else 0

        self._creer_ligne_graphique(
            bloc_qcm, f"✅ Réussis ({qcm_reussis})",
            qcm_reussis, max(qcm_total, 1), VERT_EMERAUDE)
        self._creer_ligne_graphique(
            bloc_qcm, f"❌ Ratés ({qcm_rates})",
            qcm_rates, max(qcm_total, 1), ROUGE)
        self._creer_ligne_graphique(
            bloc_qcm, f"📊 Taux de réussite ({taux_qcm}%)",
            taux_qcm, 100,
            VERT_EMERAUDE if taux_qcm >= 70 else ORANGE_DORE)

        ctk.CTkLabel(bloc_qcm, text="", height=10).pack()

        # ── BLOC 4 : Flashcards ──
        bloc_flash = ctk.CTkFrame(
            scroll, fg_color=BLEU_TRES_PALE, corner_radius=15)
        bloc_flash.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(bloc_flash, text="🃏  PERFORMANCE FLASHCARDS",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=BLEU_ROYAL).pack(pady=(15, 10))

        try:
            nb_flash = db.compter_flashcards()
            decks = db.lister_decks()
            total_reussis_f = sum((d[3] or 0) for d in decks)
            total_vus_f = sum((d[4] or 0) for d in decks)
            taux_flash = int(
                (total_reussis_f / total_vus_f) * 100) if total_vus_f > 0 else 0
        except Exception:
            nb_flash, total_reussis_f, total_vus_f, taux_flash = 0, 0, 0, 0

        self._creer_ligne_graphique(
            bloc_flash, f"🃏 Cartes totales ({nb_flash})",
            nb_flash, max(nb_flash, 1), VIOLET_PREMIUM)
        self._creer_ligne_graphique(
            bloc_flash, f"✅ Réussites ({total_reussis_f})",
            total_reussis_f, max(total_vus_f, 1), VERT_EMERAUDE)
        self._creer_ligne_graphique(
            bloc_flash, f"📊 Taux de maîtrise ({taux_flash}%)",
            taux_flash, 100,
            VERT_EMERAUDE if taux_flash >= 70 else ORANGE_DORE)

        ctk.CTkLabel(bloc_flash, text="", height=10).pack()

        # ── BLOC 5 : Pomodoro ──
        bloc_pomo = ctk.CTkFrame(
            scroll, fg_color=ORANGE_PALE, corner_radius=15)
        bloc_pomo.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(bloc_pomo, text="🍅  POMODORO",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=ORANGE_DORE).pack(pady=(15, 10))

        nb_sessions = stats_pomo.get('total_sessions', 0)
        nb_minutes = stats_pomo.get('total_minutes', 0)
        nb_heures = nb_minutes // 60

        self._creer_ligne_graphique(
            bloc_pomo, f"🍅 Sessions ({nb_sessions})",
            nb_sessions, max(nb_sessions, 10), ROUGE)
        self._creer_ligne_graphique(
            bloc_pomo,
            f"⏱️ Minutes ({nb_minutes} min ≈ {nb_heures}h)",
            nb_minutes, max(nb_minutes, 60), ORANGE_DORE)

        ctk.CTkLabel(bloc_pomo, text="", height=10).pack()

        # ── Bouton actualiser ──
        self.creer_bouton_action(
            scroll, "🔄  Actualiser les graphiques",
            self.afficher_graphiques,
            VIOLET_PREMIUM, VIOLET_LAVANDE).pack(
            pady=15, fill="x", padx=5)