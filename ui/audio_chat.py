# ui/audio_chat.py - Audio et Chat NOKIROVA 🌸

import customtkinter as ctk
from tkinter import messagebox
import threading
import database as db
from ui.base import (VERT_EMERAUDE, VERT_HOVER,
                     BLEU_ROYAL, BLEU_CIEL,
                     VIOLET_PREMIUM, VIOLET_LAVANDE, VIOLET_PALE,
                     BLANC, GRIS_TEXTE, OR_MODERNE, ORANGE_CLAIR)
from ia_handler import demander_ia
from audio_generator import generer_audio


class AudioChatMixin:

    # ═══════════════════════════════════════════
    # 🎧 AUDIO
    # ═══════════════════════════════════════════

    def afficher_audio(self):
        self.vider_zone()
        self.afficher_titre("Créer un audio", "🎧", VIOLET_PREMIUM)

        ctk.CTkLabel(
            self.zone_principale,
            text="✍️  Tape ton texte (ou utilise le cours) :",
            text_color=GRIS_TEXTE,
            font=ctk.CTkFont(size=14, weight="bold")).pack(
            pady=(10, 5), anchor="w")

        cadre_txt = ctk.CTkFrame(
            self.zone_principale, fg_color=BLANC,
            corner_radius=15, border_width=2, border_color=VIOLET_PALE)
        cadre_txt.pack(fill="x", pady=5)

        self.zone_texte_audio = ctk.CTkTextbox(
            cadre_txt, height=160, fg_color=BLANC,
            text_color=GRIS_TEXTE,
            font=ctk.CTkFont(size=14),
            corner_radius=12, border_width=0)
        self.zone_texte_audio.pack(fill="x", padx=10, pady=10)

        # ── Voix ──
        frame_voix = ctk.CTkFrame(
            self.zone_principale,
            fg_color=VIOLET_PALE, corner_radius=14)
        frame_voix.pack(fill="x", pady=10)

        ctk.CTkLabel(frame_voix, text="🎙️  Voix :",
                     text_color=GRIS_TEXTE,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(
            side="left", padx=15, pady=15)

        self.voix = ctk.CTkOptionMenu(
            frame_voix,
            values=["jeune_femme", "femme", "jeune_homme", "homme"],
            fg_color=VIOLET_PREMIUM, text_color=BLANC,
            button_color=VIOLET_LAVANDE, corner_radius=10)
        self.voix.pack(side="left", padx=10)

        # ── Boutons ──
        frame_btns = ctk.CTkFrame(self.zone_principale, fg_color="transparent")
        frame_btns.pack(pady=15, fill="x")

        self.creer_bouton_action(
            frame_btns, "📄  Utiliser le cours",
            self._remplir_avec_cours,
            BLEU_ROYAL, BLEU_CIEL).pack(
            side="left", padx=5, expand=True, fill="x")

        self.creer_bouton_action(
            frame_btns, "🎧  Créer l'audio",
            self._creer_audio,
            VIOLET_PREMIUM, VIOLET_LAVANDE).pack(
            side="left", padx=5, expand=True, fill="x")

        self.label_audio = ctk.CTkLabel(
            self.zone_principale, text="",
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

        self.label_audio.configure(text="⏳ Création de l'audio...")
        self.update()

        def tache():
            chemin = generer_audio(texte, "nokirova_audio.mp3", self.voix.get())
            self.label_audio.configure(text="✅ Audio créé !")
            db.incrementer_stat("audios_crees")
            self._recompenser(8, "Audio créé !")
            messagebox.showinfo(
                "✅ Audio créé",
                f"📁 Emplacement :\n{chemin}\n\n"
                f"🎧 Double-clique pour écouter !")

        threading.Thread(target=tache, daemon=True).start()

    # ═══════════════════════════════════════════
    # 💬 CHAT / QUESTION LIBRE
    # ═══════════════════════════════════════════

    def afficher_chat(self):
        self.vider_zone()
        self.afficher_titre("Question libre à NOKIROVA", "💬", VIOLET_PREMIUM)

        ctk.CTkLabel(
            self.zone_principale,
            text="💭  Pose-moi N'IMPORTE QUELLE question :",
            text_color=GRIS_TEXTE,
            font=ctk.CTkFont(size=14, weight="bold")).pack(
            pady=(10, 5), anchor="w")

        self.question_entry = ctk.CTkEntry(
            self.zone_principale, height=50,
            fg_color=BLANC, text_color=GRIS_TEXTE,
            placeholder_text="Ex: Explique-moi l'élasticité-prix...",
            font=ctk.CTkFont(size=14), corner_radius=14,
            border_width=2, border_color=VIOLET_PALE)
        self.question_entry.pack(fill="x", pady=10)
        self.question_entry.bind("<Return>", lambda e: self._envoyer_question())

        self.creer_bouton_action(
            self.zone_principale, "🚀  Envoyer",
            self._envoyer_question,
            VIOLET_PREMIUM, VIOLET_LAVANDE).pack(pady=10, fill="x")

        self.zone_reponse = self.creer_zone_texte(310)
        self.zone_reponse.insert(
            "0.0",
            "💡 Pose ta question ci-dessus puis appuie sur Entrée !")

        self.creer_bouton_export(self.zone_reponse, "reponse").pack(pady=5)

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
            db.sauvegarder_historique(
                "question_libre", question, res,
                self.matiere_detectee or "Général")
            self._recompenser(5, "Question posée !")

        threading.Thread(target=tache, daemon=True).start()