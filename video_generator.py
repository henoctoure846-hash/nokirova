# video_generator.py - Création de vidéos éducatives 🎬🌸
# Compatible moviepy >= 2.0, avec gestion d'erreurs améliorée
import os
import re
import uuid
import requests
from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip, concatenate_videoclips, ImageSequenceClip
import edge_tts
import asyncio
import traceback

# Dossiers
OUTPUT_DIR = "outputs"
TEMP_DIR = os.path.join(OUTPUT_DIR, "temp_video")
os.makedirs(TEMP_DIR, exist_ok=True)

# Styles disponibles
STYLES = {
    "bande_dessinee": {
        "fond": "bd",
        "police": "Comic Sans MS",
        "source_image": "pollinations",
        "style_prompt": "comic book style, educational, colorful"
    },
    "documentaire": {
        "fond": "photo",
        "police": "Georgia",
        "source_image": "unsplash",
        "style_prompt": "real photo, documentary, high quality"
    },
    "tableau": {
        "fond": "tableau",
        "police": "Caveat",
        "source_image": None,
        "style_prompt": None
    },
    "ardoise": {
        "fond": "ardoise",
        "police": "Caveat",
        "source_image": None,
        "style_prompt": None
    },
    "ecritures_animees": {
        "fond": "blanc",
        "police": "Caveat",
        "source_image": None,
        "style_prompt": None
    }
}

VOIX = {
    "homme": "fr-FR-HenriNeural",
    "femme": "fr-FR-DeniseNeural",
    "jeune_homme": "fr-FR-RemyMultilingualNeural",
    "jeune_femme": "fr-FR-VivienneMultilingualNeural"
}


def _decouper_script(texte):
    phrases = re.split(r'(?<=[.!?])\s+', texte)
    segments = []
    current = ""
    for p in phrases:
        if len(current) + len(p) < 200:
            current = (current + " " + p).strip()
        else:
            if current:
                segments.append(current)
            current = p
    if current:
        segments.append(current)
    return segments


def _generer_audio_segment(texte, voix, nom_fichier):
    voix_code = VOIX.get(voix, VOIX["jeune_femme"])

    async def tache():
        communicate = edge_tts.Communicate(texte, voix_code)
        await communicate.save(nom_fichier)

    asyncio.run(tache())
    return nom_fichier


def _generer_image_pollinations(prompt, style_prompt, nom_fichier):
    try:
        full_prompt = f"{prompt}, {style_prompt}"
        encoded = requests.utils.quote(full_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&nologo=true"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            with open(nom_fichier, 'wb') as f:
                f.write(response.content)
            return nom_fichier
    except Exception as e:
        print(f"⚠️ Pollinations échoué : {e}")
    return None


def _generer_image_unsplash(query, nom_fichier):
    try:
        url = f"https://source.unsplash.com/1280x720/?{query}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(nom_fichier, 'wb') as f:
                f.write(response.content)
            return nom_fichier
    except Exception as e:
        print(f"⚠️ Unsplash échoué : {e}")
    return None


def _generer_fond_ardoise(texte, police_nom, nom_fichier):
    img = Image.open("assets/ardoise.png") if os.path.exists("assets/ardoise.png") else Image.new('RGB', (1280, 720),
                                                                                                  (34, 139, 34))
    d = ImageDraw.Draw(img)
    try:
        font_path = os.path.join("assets", "fonts", f"{police_nom}.ttf")
        font = ImageFont.truetype(font_path, 40) if os.path.exists(font_path) else ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    lignes = texte.split('\n')
    y = 50
    for ligne in lignes:
        d.text((50, y), ligne, fill=(255, 255, 255), font=font)
        y += 50
    img.save(nom_fichier)
    return nom_fichier


def generer_video(cours, style="documentaire", vitesse="normal", voix="jeune_femme"):
    """
    Génère une vidéo éducative complète.
    Retourne le chemin du fichier .mp4 ou une chaîne d'erreur explicite.
    """
    try:
        print("🎬 Début de la génération vidéo...")
        segments = _decouper_script(cours)
        if not segments:
            return "❌ Le cours ne contient aucun texte exploitable."

        print(f"📝 {len(segments)} segments à traiter.")

        vitesse_map = {"lent": 1.4, "normal": 1.0, "rapide": 0.7}
        facteur = vitesse_map.get(vitesse, 1.0)

        scenes = []
        audio_files = []
        for i, seg in enumerate(segments):
            print(f"  🎞️ Traitement du segment {i+1}/{len(segments)}...")
            img_file = os.path.join(TEMP_DIR, f"scene_{i}.png")
            audio_file = os.path.join(TEMP_DIR, f"audio_{i}.mp3")

            # Génération image
            if STYLES[style]["source_image"] == "pollinations":
                res = _generer_image_pollinations(seg, STYLES[style]["style_prompt"], img_file)
                if not res:
                    # Fallback : image blanche avec texte
                    img = Image.new('RGB', (1280, 720), (255, 255, 255))
                    d = ImageDraw.Draw(img)
                    d.text((50, 300), seg, fill=(0, 0, 0))
                    img.save(img_file)
            elif STYLES[style]["source_image"] == "unsplash":
                res = _generer_image_unsplash(seg, img_file)
                if not res:
                    img = Image.new('RGB', (1280, 720), (255, 255, 255))
                    d = ImageDraw.Draw(img)
                    d.text((50, 300), seg, fill=(0, 0, 0))
                    img.save(img_file)
            else:
                fond = STYLES[style]["fond"]
                if fond == "ardoise":
                    _generer_fond_ardoise(seg, STYLES[style]["police"], img_file)
                else:
                    img = Image.new('RGB', (1280, 720), (255, 255, 255))
                    d = ImageDraw.Draw(img)
                    try:
                        font_path = os.path.join("assets", "fonts", f"{STYLES[style]['police']}.ttf")
                        font = ImageFont.truetype(font_path, 40) if os.path.exists(font_path) else ImageFont.load_default()
                    except:
                        font = ImageFont.load_default()
                    d.text((50, 300), seg, fill=(0, 0, 0), font=font)
                    img.save(img_file)

            # Génération audio
            try:
                _generer_audio_segment(seg, voix, audio_file)
                audio_files.append(audio_file)
            except Exception as e:
                print(f"  ⚠️ Erreur audio segment {i}: {e}")
                # On continue sans audio pour ce segment ? Mieux vaut retourner l'erreur
                return f"❌ Erreur lors de la génération audio du segment {i+1} : {e}"

            # Clip
            try:
                audio_clip = AudioFileClip(audio_file)
                image_clip = ImageSequenceClip([img_file], durations=[audio_clip.duration * facteur])
                image_clip = image_clip.with_audio(audio_clip)
                scenes.append(image_clip)
            except Exception as e:
                print(f"  ⚠️ Erreur création clip : {e}")
                return f"❌ Erreur lors de la création du clip {i+1} : {e}"

        if not scenes:
            return "❌ Aucune scène n'a pu être générée."

        print("🎥 Assemblage final...")
        video_final = os.path.join(OUTPUT_DIR, f"video_{uuid.uuid4().hex[:8]}.mp4")
        video = concatenate_videoclips(scenes, method="compose")
        video.write_videofile(video_final, fps=24)

        # Nettoyage
        for f in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, f))

        print(f"✅ Vidéo créée : {video_final}")
        return video_final

    except Exception as e:
        traceback.print_exc()
        return f"❌ Erreur génération vidéo : {e}"