# ui/videos_revision.py - Vidéos de révision NOKIROVA 🎬

import customtkinter as ctk
from tkinter import messagebox
import threading
import os
import random
import webbrowser
import asyncio
import json
import re
from datetime import datetime
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

DOSSIER_VIDEOS = "videos_revision"


# ═══════════════════════════════════════════
# 🎤 VOIX FRANÇAISES (TOUTES TESTÉES & VALIDES)
# ═══════════════════════════════════════════
VOIX_FR = {
    "🇫🇷 Denise (femme douce)": "fr-FR-DeniseNeural",
    "🇫🇷 ABDIAS (homme posé)": "fr-FR-HenriNeural",
    "🇫🇷 Eloise (jeune dynamique)": "fr-FR-EloiseNeural",
    "🇨🇦 Sylvie (canadienne)": "fr-CA-SylvieNeural",
    "🇨🇭 Ariane (suisse douce)": "fr-CH-ArianeNeural",
    "🇧🇪 Charline (belge claire)": "fr-BE-CharlineNeural",
    "🇫🇷 YVAN (homme jeune)": "fr-CA-AntoineNeural",
    "🇫🇷 HENOC (voix douce)": "fr-CH-FabriceNeural",
}


# ═══════════════════════════════════════════
# 🎛️ VITESSES DISPONIBLES
# ═══════════════════════════════════════════
VITESSES = {
    "🐢 Lent (0.75x)": {"rate": "-25%", "facteur": 1.33},
    "🚶 Normal (1.0x)": {"rate": "+0%", "facteur": 1.0},
    "🏃 Rapide (1.25x)": {"rate": "+25%", "facteur": 0.80},
    "⚡ Ultra rapide (1.5x)": {"rate": "+50%", "facteur": 0.67},
}


# ═══════════════════════════════════════════
# 🎨 4 STYLES VISUELS (aléatoires)
# ═══════════════════════════════════════════
STYLES_VIDEO = {
    "colore": {
        "nom": "🎨 Coloré NOKIROVA",
        "bg": "linear-gradient(135deg, #7B61FF 0%, #FFC9DE 100%)",
        "card": "#FFFFFF",
        "titre_color": "#7B61FF",
        "texte_color": "#374151",
        "accent": "#FFD93D",
    },
    "sobre": {
        "nom": "📚 Sobre académique",
        "bg": "#FAFAFA",
        "card": "#FFFFFF",
        "titre_color": "#1A1B26",
        "texte_color": "#374151",
        "accent": "#2962FF",
    },
    "sombre": {
        "nom": "🌙 Mode sombre",
        "bg": "#0F1419",
        "card": "#1A1B26",
        "titre_color": "#FFD93D",
        "texte_color": "#C0CAF5",
        "accent": "#7ED321",
    },
    "dynamique": {
        "nom": "🎮 Jeune dynamique",
        "bg": "linear-gradient(135deg, #00C853 0%, #FFD93D 50%, #F59E0B 100%)",
        "card": "#FFFFFF",
        "titre_color": "#EF4444",
        "texte_color": "#1A1B26",
        "accent": "#7B61FF",
    },
}


class VideosRevisionMixin:

    # ═══════════════════════════════════════════
    # 🎬 PAGE PRINCIPALE
    # ═══════════════════════════════════════════

    def afficher_videos_revision(self):
        self.vider_zone()
        self.afficher_titre(
            "Vidéos de révision", "🎬", VIOLET_PREMIUM)

        # Init dossier
        if not os.path.exists(DOSSIER_VIDEOS):
            os.makedirs(DOSSIER_VIDEOS)

        # Variables
        if not hasattr(self, '_video_cours_id'):
            self._video_cours_id = None
        if not hasattr(self, '_video_voix'):
            self._video_voix = list(VOIX_FR.keys())[0]
        if not hasattr(self, '_video_vitesse'):
            self._video_vitesse = "🚶 Normal (1.0x)"

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
            text="🎬 Transforme un cours en VIDÉO de révision !\n"
                 "🤖 L'IA crée les slides • 🎤 La voix off raconte\n"
                 "🌐 Ta vidéo s'ouvre dans le navigateur",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=VIOLET_PREMIUM,
            justify="center").pack(pady=12)

        # ── ÉTAPE 1 : Choisir un cours ──
        self._creer_section_video(
            scroll, "📚  ÉTAPE 1 : Choisir un cours",
            VIOLET_PREMIUM)

        cours_list = db.lister_cours()
        if not cours_list:
            cadre_vide = ctk.CTkFrame(
                scroll, fg_color=ROUGE_CLAIR, corner_radius=12)
            cadre_vide.pack(fill="x", pady=5)
            ctk.CTkLabel(
                cadre_vide,
                text="📭  Aucun cours dans la bibliothèque !\n"
                     "💡 Importe un cours d'abord.",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=BLANC, justify="center").pack(pady=12)
            return

        cours_options = [
            f"{c[1][:40]} • {c[2][:20]}"
            for c in cours_list]
        self._video_cours_map = {
            f"{c[1][:40]} • {c[2][:20]}": c[0] for c in cours_list}

        cadre_cours = ctk.CTkFrame(
            scroll, fg_color=BLANC, corner_radius=12,
            border_width=2, border_color=VIOLET_PALE)
        cadre_cours.pack(fill="x", pady=5)

        ctk.CTkLabel(
            cadre_cours, text="📄  Sélectionne ton cours :",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", padx=15, pady=(12, 3))

        menu_cours = ctk.CTkOptionMenu(
            cadre_cours, values=cours_options,
            command=self._choisir_cours_video,
            fg_color=VIOLET_LAVANDE, button_color=VIOLET_PREMIUM,
            text_color=BLANC, height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            dropdown_font=ctk.CTkFont(size=11))
        menu_cours.set(cours_options[0])
        menu_cours.pack(fill="x", padx=15, pady=(0, 12))
        self._video_cours_id = cours_list[0][0]

        # ── ÉTAPE 2 : Choisir la voix ──
        self._creer_section_video(
            scroll, "🎤  ÉTAPE 2 : Choisir la voix off",
            ORANGE_DORE)

        cadre_voix = ctk.CTkFrame(
            scroll, fg_color=BLANC, corner_radius=12,
            border_width=2, border_color=JAUNE_PALE)
        cadre_voix.pack(fill="x", pady=5)

        ctk.CTkLabel(
            cadre_voix, text="🎙️  Choisis ta voix préférée :",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", padx=15, pady=(12, 3))

        menu_voix = ctk.CTkOptionMenu(
            cadre_voix, values=list(VOIX_FR.keys()),
            command=lambda v: setattr(self, '_video_voix', v),
            fg_color=ORANGE_CLAIR, button_color=ORANGE_DORE,
            text_color=BLANC, height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            dropdown_font=ctk.CTkFont(size=11))
        menu_voix.set(self._video_voix)
        menu_voix.pack(fill="x", padx=15, pady=(0, 5))

        ctk.CTkButton(
            cadre_voix, text="🔊  Tester cette voix",
            command=self._tester_voix,
            fg_color=BLEU_ROYAL, hover_color=BLEU_CIEL,
            text_color=BLANC, height=35,
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=8).pack(
            fill="x", padx=15, pady=(0, 12))

        # ── ÉTAPE 3 : VITESSE ──
        self._creer_section_video(
            scroll, "🎛️  ÉTAPE 3 : Vitesse de la voix",
            VERT_EMERAUDE)

        cadre_vitesse = ctk.CTkFrame(
            scroll, fg_color=BLANC, corner_radius=12,
            border_width=2, border_color=VERT_CLAIR)
        cadre_vitesse.pack(fill="x", pady=5)

        ctk.CTkLabel(
            cadre_vitesse, text="⚡  À quelle vitesse parler ?",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(
            fill="x", padx=15, pady=(12, 3))

        ctk.CTkLabel(
            cadre_vitesse,
            text="💡 Lent = bien comprendre  •  "
                 "Rapide = réviser plus vite",
            font=ctk.CTkFont(size=10),
            text_color=GRIS_DOUX, anchor="w").pack(
            fill="x", padx=15, pady=(0, 5))

        menu_vitesse = ctk.CTkOptionMenu(
            cadre_vitesse, values=list(VITESSES.keys()),
            command=lambda v: setattr(self, '_video_vitesse', v),
            fg_color=VERT_EMERAUDE, button_color=VERT_HOVER,
            text_color=BLANC, height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            dropdown_font=ctk.CTkFont(size=11))
        menu_vitesse.set(self._video_vitesse)
        menu_vitesse.pack(fill="x", padx=15, pady=(0, 12))

        # ── ÉTAPE 4 : Style aléatoire ──
        self._creer_section_video(
            scroll, "🎨  ÉTAPE 4 : Style de la vidéo",
            BLEU_ROYAL)

        cadre_style = ctk.CTkFrame(
            scroll, fg_color=BLEU_TRES_PALE, corner_radius=12)
        cadre_style.pack(fill="x", pady=5)

        ctk.CTkLabel(
            cadre_style,
            text="🎲  Un style ALÉATOIRE sera choisi parmi :\n"
                 "🎨 Coloré NOKIROVA  •  📚 Sobre académique\n"
                 "🌙 Mode sombre  •  🎮 Jeune dynamique",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=BLEU_ROYAL,
            justify="center").pack(pady=15)

        # ── BOUTON GÉNÉRER ──
        self.btn_generer_video = ctk.CTkButton(
            scroll,
            text="🎬  GÉNÉRER LA VIDÉO  🎬",
            command=self._lancer_generation_video,
            fg_color=VIOLET_PREMIUM, hover_color=VIOLET_LAVANDE,
            text_color=BLANC, corner_radius=14, height=60,
            font=ctk.CTkFont(size=18, weight="bold"))
        self.btn_generer_video.pack(fill="x", pady=15)

        # ── Zone progression ──
        self._video_progress_frame = ctk.CTkFrame(
            scroll, fg_color=BLEU_TRES_PALE, corner_radius=12)
        self._video_progress_label = ctk.CTkLabel(
            self._video_progress_frame,
            text="⏳  Préparation...",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=BLEU_ROYAL)
        self._video_progress_label.pack(pady=(10, 5))
        self._video_progress_bar = ctk.CTkProgressBar(
            self._video_progress_frame,
            progress_color=VIOLET_PREMIUM,
            fg_color=BLANC, height=18, corner_radius=9)
        self._video_progress_bar.pack(
            fill="x", padx=20, pady=(0, 10))
        self._video_progress_bar.set(0)

        # ── Vidéos existantes ──
        self._creer_section_video(
            scroll, "📂  TES VIDÉOS CRÉÉES",
            VERT_EMERAUDE)
        self._afficher_videos_existantes(scroll)

        ctk.CTkLabel(scroll, text="", height=15).pack()

    # ═══════════════════════════════════════════
    # 🛠️ HELPERS UI
    # ═══════════════════════════════════════════

    def _creer_section_video(self, parent, texte, couleur):
        cadre = ctk.CTkFrame(parent, fg_color=couleur, corner_radius=10)
        cadre.pack(fill="x", pady=(15, 5))
        ctk.CTkLabel(
            cadre, text=texte,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=BLANC).pack(pady=10)

    def _choisir_cours_video(self, valeur):
        self._video_cours_id = self._video_cours_map.get(valeur)

    # ═══════════════════════════════════════════
    # 🔊 TEST VOIX
    # ═══════════════════════════════════════════

    def _tester_voix(self):
        notification_succes(
            self, "Test voix...", "🔊 Génération en cours...")
        threading.Thread(
            target=self._test_voix_thread, daemon=True).start()

    def _test_voix_thread(self):
        try:
            import edge_tts
            voix_id = VOIX_FR.get(
                self._video_voix, "fr-FR-DeniseNeural")
            vitesse_info = VITESSES.get(
                self._video_vitesse, VITESSES["🚶 Normal (1.0x)"])
            rate = vitesse_info["rate"]

            texte = ("Bonjour ! Je suis ta voix off NOKIROVA. "
                     "Je vais t'aider à réviser tes cours.")
            fichier = os.path.join(
                DOSSIER_VIDEOS, "_test_voix.mp3")

            async def gen():
                comm = edge_tts.Communicate(
                    texte, voix_id, rate=rate)
                await comm.save(fichier)

            asyncio.run(gen())

            if os.path.exists(fichier) and os.path.getsize(fichier) > 0:
                os.startfile(fichier)
            else:
                self.after(0, self._erreur_test_voix,
                           "Fichier audio vide")
        except Exception as exc:
            msg = str(exc)
            print(f"⚠️ Test voix : {msg}")
            self.after(0, self._erreur_test_voix, msg)

    def _erreur_test_voix(self, msg):
        messagebox.showerror(
            "❌ Erreur",
            f"Test voix échoué :\n{msg[:150]}\n\n"
            "💡 Vérifie ta connexion internet.")

    # ═══════════════════════════════════════════
    # 🎬 GÉNÉRATION VIDÉO
    # ═══════════════════════════════════════════

    def _lancer_generation_video(self):
        if not self._video_cours_id:
            messagebox.showwarning("⚠️", "Choisis un cours !")
            return

        info = db.info_cours(self._video_cours_id)
        if not info or not info.get("contenu"):
            messagebox.showwarning(
                "⚠️", "Cours vide ou introuvable !")
            return

        self._video_progress_frame.pack(fill="x", pady=10)
        self._video_progress_bar.set(0)
        self.btn_generer_video.configure(
            text="⏳  Génération en cours...", state="disabled")

        threading.Thread(
            target=self._generation_thread,
            args=(info,), daemon=True).start()

    def _maj_progress(self, valeur, message):
        self._video_progress_bar.set(valeur)
        self._video_progress_label.configure(text=message)

    def _generation_thread(self, info):
        try:
            # ÉTAPE 1 : Découper en slides
            self.after(0, self._maj_progress,
                       0.1, "🤖  L'IA découpe le cours en 8 slides...")
            slides = self._decouper_en_slides(info["contenu"])
            if not slides:
                self.after(0, self._erreur_video,
                           "Découpage impossible")
                return

            # ÉTAPE 2 : Générer audio
            nb = len(slides)
            voix_id = VOIX_FR.get(
                self._video_voix, "fr-FR-DeniseNeural")
            vitesse_info = VITESSES.get(
                self._video_vitesse, VITESSES["🚶 Normal (1.0x)"])
            rate = vitesse_info["rate"]
            facteur = vitesse_info["facteur"]

            nom_dossier = self._creer_nom_dossier(info["nom"])
            chemin_dossier = os.path.join(
                DOSSIER_VIDEOS, nom_dossier)
            os.makedirs(chemin_dossier, exist_ok=True)

            audios = []
            durees = []
            for i, slide in enumerate(slides):
                progress = 0.2 + (i / nb) * 0.6
                self.after(0, self._maj_progress, progress,
                           f"🎤  Audio slide {i + 1}/{nb}...")

                audio_file = os.path.join(
                    chemin_dossier, f"slide_{i + 1}.mp3")
                duree = self._generer_audio(
                    slide["texte_voix"], voix_id, audio_file,
                    rate, facteur)
                audios.append(f"slide_{i + 1}.mp3")
                durees.append(duree)

            # ÉTAPE 3 : Style aléatoire
            self.after(0, self._maj_progress,
                       0.85, "🎨  Création du diaporama...")
            style_code = random.choice(list(STYLES_VIDEO.keys()))
            style = STYLES_VIDEO[style_code]

            # ÉTAPE 4 : HTML
            html = self._creer_html_diaporama(
                info["nom"], info["matiere"],
                slides, audios, durees, style)
            html_file = os.path.join(
                chemin_dossier, "diaporama.html")
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html)

            # ÉTAPE 5 : Métadonnées
            meta = {
                "nom_cours": info["nom"],
                "matiere": info["matiere"],
                "voix": self._video_voix,
                "vitesse": self._video_vitesse,
                "style": style["nom"],
                "nb_slides": nb,
                "date_creation": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"),
            }
            with open(os.path.join(chemin_dossier, "meta.json"),
                      'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

            # ÉTAPE 6 : Ouvrir
            self.after(0, self._maj_progress,
                       1.0, "✅  Vidéo prête !")
            chemin_abs = os.path.abspath(html_file)
            webbrowser.open(f"file:///{chemin_abs}")

            self.after(0, self._fin_generation, meta)

        except Exception as exc:
            erreur = str(exc)
            print(f"⚠️ Erreur génération : {erreur}")
            self.after(0, self._erreur_video, erreur)

    def _fin_generation(self, meta):
        self.btn_generer_video.configure(
            text="🎬  GÉNÉRER LA VIDÉO  🎬", state="normal")
        notification_succes(
            self, "Vidéo créée ! 🎬",
            f"🌐 Ouverte dans le navigateur")
        self._recompenser(30, "Vidéo de révision ! 🎬")
        messagebox.showinfo(
            "✅ Vidéo créée !",
            f"🎬 Diaporama généré avec succès !\n\n"
            f"📚 Cours : {meta['nom_cours'][:40]}\n"
            f"🎤 Voix : {meta['voix']}\n"
            f"⚡ Vitesse : {meta['vitesse']}\n"
            f"🎨 Style : {meta['style']}\n"
            f"📊 {meta['nb_slides']} slides\n\n"
            f"🌐 La vidéo s'est ouverte dans ton navigateur !\n"
            f"💡 Clique sur ▶️ pour lancer la lecture auto.")
        self.afficher_videos_revision()

    def _erreur_video(self, msg):
        self.btn_generer_video.configure(
            text="🎬  GÉNÉRER LA VIDÉO  🎬", state="normal")
        self._video_progress_label.configure(
            text=f"❌  Erreur : {msg[:60]}")
        messagebox.showerror(
            "❌ Erreur", f"Génération échouée :\n{msg}")

    # ═══════════════════════════════════════════
    # 🤖 DÉCOUPAGE EN SLIDES (IA)
    # ═══════════════════════════════════════════

    def _decouper_en_slides(self, contenu):
        try:
            from ia_handler import demander_ia_brut

            prompt = f"""Tu es un expert pédagogique. Découpe ce cours en EXACTEMENT 8 slides pour une vidéo de révision.

RÈGLES STRICTES :
- 8 slides MAX (pas plus, pas moins)
- Chaque slide : 1 idée principale
- Titre court (5-8 mots)
- Texte du slide : 3-5 phrases simples
- Texte voix off : EXACTEMENT le même que le texte du slide

FORMAT JSON OBLIGATOIRE (réponds UNIQUEMENT en JSON valide) :
{{
  "slides": [
    {{
      "numero": 1,
      "titre": "Introduction",
      "texte_slide": "Texte affiché",
      "texte_voix": "Texte lu par la voix off"
    }}
  ]
}}

COURS À DÉCOUPER :
{contenu[:4000]}

JSON :"""

            reponse = demander_ia_brut(prompt, temperature=0.4)
            reponse = reponse.strip()
            if reponse.startswith("```"):
                reponse = reponse.split("```")[1]
                if reponse.startswith("json"):
                    reponse = reponse[4:]
            reponse = reponse.strip("`").strip()

            data = json.loads(reponse)
            slides = data.get("slides", [])

            if not slides or len(slides) < 3:
                return self._decoupage_fallback(contenu)

            return slides[:8]

        except Exception as exc:
            print(f"⚠️ Découpage IA échoué : {exc}")
            return self._decoupage_fallback(contenu)

    def _decoupage_fallback(self, contenu):
        paragraphes = [p.strip() for p in contenu.split("\n\n")
                       if p.strip() and len(p.strip()) > 50]
        if not paragraphes:
            paragraphes = [contenu[i:i + 400]
                           for i in range(0, len(contenu), 400)]

        nb = min(8, len(paragraphes))
        slides = []
        for i in range(nb):
            texte = paragraphes[i][:500]
            slides.append({
                "numero": i + 1,
                "titre": f"Partie {i + 1}",
                "texte_slide": texte,
                "texte_voix": texte
            })
        return slides

    # ═══════════════════════════════════════════
    # 🎤 GÉNÉRATION AUDIO (AVEC VITESSE)
    # ═══════════════════════════════════════════

    def _generer_audio(self, texte, voix_id, fichier_sortie,
                       rate="+0%", facteur=1.0):
        """Génère un MP3 avec edge-tts à la vitesse demandée"""
        try:
            import edge_tts

            async def gen():
                comm = edge_tts.Communicate(
                    texte, voix_id, rate=rate)
                await comm.save(fichier_sortie)

            asyncio.run(gen())

            # Durée ajustée selon la vitesse
            nb_mots = len(texte.split())
            duree_normale = max(3, int(nb_mots / 2.5))
            duree_finale = max(3, int(duree_normale * facteur))
            return duree_finale

        except Exception as exc:
            print(f"⚠️ Audio échoué : {exc}")
            return 5

    # ═══════════════════════════════════════════
    # 🎨 GÉNÉRATION HTML
    # ═══════════════════════════════════════════

    def _creer_nom_dossier(self, nom_cours):
        nom = re.sub(r'[^\w\s-]', '', nom_cours)
        nom = nom.replace(' ', '_')[:40]
        date = datetime.now().strftime("%Y%m%d_%H%M")
        return f"{nom}_{date}"

    def _creer_html_diaporama(self, nom, matiere, slides,
                              audios, durees, style):
        slides_html = ""
        for i, slide in enumerate(slides):
            actif = "active" if i == 0 else ""
            slides_html += f"""
            <div class="slide {actif}" data-duree="{durees[i]}" data-audio="{audios[i]}">
              <div class="slide-numero">Slide {i + 1} / {len(slides)}</div>
              <h2 class="slide-titre">{slide['titre']}</h2>
              <div class="slide-texte">{slide['texte_slide']}</div>
            </div>
            """

        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>🎬 {nom} - NOKIROVA</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: 'Segoe UI', sans-serif;
      background: {style['bg']};
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}
    .header {{
      color: white;
      text-align: center;
      margin-bottom: 20px;
      font-size: 24px;
      font-weight: bold;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }}
    .matiere {{
      color: white;
      font-size: 16px;
      margin-bottom: 30px;
      opacity: 0.9;
    }}
    .diaporama {{
      width: 90%;
      max-width: 900px;
      background: {style['card']};
      border-radius: 20px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      padding: 60px 50px;
      min-height: 450px;
      position: relative;
    }}
    .slide {{
      display: none;
      animation: fadeIn 0.6s ease-in;
    }}
    .slide.active {{ display: block; }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(20px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .slide-numero {{
      color: {style['accent']};
      font-size: 14px;
      font-weight: bold;
      margin-bottom: 15px;
    }}
    .slide-titre {{
      color: {style['titre_color']};
      font-size: 36px;
      font-weight: bold;
      margin-bottom: 25px;
      line-height: 1.2;
    }}
    .slide-texte {{
      color: {style['texte_color']};
      font-size: 20px;
      line-height: 1.6;
      white-space: pre-wrap;
    }}
    .controls {{
      display: flex;
      gap: 15px;
      margin-top: 30px;
      justify-content: center;
      flex-wrap: wrap;
    }}
    button {{
      background: {style['accent']};
      color: white;
      border: none;
      padding: 14px 28px;
      border-radius: 10px;
      font-size: 16px;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.3s;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }}
    button:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0,0,0,0.3);
    }}
    .progress-bar {{
      width: 90%;
      max-width: 900px;
      height: 6px;
      background: rgba(255,255,255,0.3);
      border-radius: 3px;
      margin-top: 20px;
      overflow: hidden;
    }}
    .progress-fill {{
      height: 100%;
      background: {style['accent']};
      width: 0%;
      transition: width 0.3s;
    }}
    .info {{
      color: white;
      margin-top: 15px;
      font-size: 14px;
      opacity: 0.8;
    }}
  </style>
</head>
<body>
  <div class="header">🎬  {nom}</div>
  <div class="matiere">🎯 {matiere} • Powered by NOKIROVA 🌸</div>

  <div class="diaporama">
    {slides_html}

    <div class="controls">
      <button onclick="precedent()">⬅️ Précédent</button>
      <button onclick="togglePlay()" id="btnPlay">▶️ Lecture auto</button>
      <button onclick="suivant()">Suivant ➡️</button>
    </div>
  </div>

  <div class="progress-bar">
    <div class="progress-fill" id="progress"></div>
  </div>
  <div class="info" id="info">Slide 1 sur {len(slides)}</div>

  <audio id="player" preload="auto"></audio>

  <script>
    let current = 0;
    const slides = document.querySelectorAll('.slide');
    const total = slides.length;
    const player = document.getElementById('player');
    const progress = document.getElementById('progress');
    const info = document.getElementById('info');
    const btnPlay = document.getElementById('btnPlay');
    let autoPlay = false;
    let timer = null;

    function afficher(idx) {{
      slides.forEach(s => s.classList.remove('active'));
      slides[idx].classList.add('active');
      progress.style.width = ((idx + 1) / total * 100) + '%';
      info.textContent = 'Slide ' + (idx + 1) + ' sur ' + total;

      if (autoPlay) {{
        const audio = slides[idx].dataset.audio;
        player.src = audio;
        player.play().catch(e => console.log('Audio:', e));

        const duree = parseInt(slides[idx].dataset.duree) * 1000;
        clearTimeout(timer);
        timer = setTimeout(() => {{
          if (current < total - 1) {{
            current++;
            afficher(current);
          }} else {{
            autoPlay = false;
            btnPlay.textContent = '▶️ Lecture auto';
          }}
        }}, duree + 500);
      }}
    }}

    function suivant() {{
      if (current < total - 1) {{
        current++;
        afficher(current);
      }}
    }}

    function precedent() {{
      if (current > 0) {{
        current--;
        afficher(current);
      }}
    }}

    function togglePlay() {{
      autoPlay = !autoPlay;
      btnPlay.textContent = autoPlay ? '⏸️ Pause' : '▶️ Lecture auto';
      if (autoPlay) {{
        afficher(current);
      }} else {{
        player.pause();
        clearTimeout(timer);
      }}
    }}

    document.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight') suivant();
      if (e.key === 'ArrowLeft') precedent();
      if (e.key === ' ') {{ e.preventDefault(); togglePlay(); }}
    }});

    afficher(0);
  </script>
</body>
</html>"""
        return html

    # ═══════════════════════════════════════════
    # 📂 VIDÉOS EXISTANTES
    # ═══════════════════════════════════════════

    def _afficher_videos_existantes(self, parent):
        cadre = ctk.CTkFrame(
            parent, fg_color=BLANC, corner_radius=12,
            border_width=2, border_color=VERT_CLAIR)
        cadre.pack(fill="x", pady=5)

        if not os.path.exists(DOSSIER_VIDEOS):
            ctk.CTkLabel(
                cadre, text="📭  Aucune vidéo créée pour l'instant",
                font=ctk.CTkFont(size=12),
                text_color=GRIS_DOUX).pack(pady=20)
            return

        dossiers = [d for d in os.listdir(DOSSIER_VIDEOS)
                    if os.path.isdir(
                os.path.join(DOSSIER_VIDEOS, d))]

        if not dossiers:
            ctk.CTkLabel(
                cadre, text="📭  Aucune vidéo créée pour l'instant",
                font=ctk.CTkFont(size=12),
                text_color=GRIS_DOUX).pack(pady=20)
            return

        for dossier in sorted(dossiers, reverse=True)[:10]:
            self._creer_carte_video(cadre, dossier)

    def _creer_carte_video(self, parent, nom_dossier):
        chemin = os.path.join(DOSSIER_VIDEOS, nom_dossier)
        meta_file = os.path.join(chemin, "meta.json")
        html_file = os.path.join(chemin, "diaporama.html")

        if not os.path.exists(html_file):
            return

        meta = {}
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except Exception:
            pass

        ligne = ctk.CTkFrame(
            parent, fg_color=VERT_FOND_CORRECTION,
            corner_radius=10, border_width=2,
            border_color=VERT_CLAIR)
        ligne.pack(fill="x", padx=10, pady=4)

        infos = ctk.CTkFrame(ligne, fg_color="transparent")
        infos.pack(side="left", fill="x", expand=True,
                   padx=12, pady=8)

        ctk.CTkLabel(
            infos,
            text=f"🎬  {meta.get('nom_cours', nom_dossier)[:40]}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(fill="x")

        ctk.CTkLabel(
            infos,
            text=f"🎤 {meta.get('voix', '?')} • "
                 f"⚡ {meta.get('vitesse', 'Normal')} • "
                 f"🎨 {meta.get('style', '?')} • "
                 f"📊 {meta.get('nb_slides', '?')} slides",
            font=ctk.CTkFont(size=10),
            text_color=GRIS_DOUX, anchor="w").pack(fill="x")

        btns = ctk.CTkFrame(ligne, fg_color="transparent")
        btns.pack(side="right", padx=8, pady=8)

        ctk.CTkButton(
            btns, text="▶️ Ouvrir",
            command=lambda h=html_file: webbrowser.open(
                f"file:///{os.path.abspath(h)}"),
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC, height=32, width=90,
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=7).pack(side="left", padx=2)

        ctk.CTkButton(
            btns, text="🗑️",
            command=lambda c=chemin: self._supprimer_video(c),
            fg_color=ROUGE, hover_color=ROUGE_CLAIR,
            text_color=BLANC, height=32, width=45,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=7).pack(side="left", padx=2)

    def _supprimer_video(self, chemin):
        if messagebox.askyesno(
                "🗑️ Supprimer",
                "Supprimer cette vidéo ?\n⚠️ Irréversible !"):
            try:
                import shutil
                shutil.rmtree(chemin)
                notification_succes(
                    self, "Supprimée", "🗑️ Vidéo supprimée")
                self.afficher_videos_revision()
            except Exception as exc:
                messagebox.showerror("❌", str(exc))