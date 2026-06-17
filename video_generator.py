# video_generator.py - Création de vidéos éducatives 🎬🌸
# Compatible moviepy >= 2.0
import os
import re
import uuid
import requests
from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip, concatenate_videoclips, ImageSequenceClip
import edge_tts
import asyncio

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
    """Découpe le texte en segments exploitables"""
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
    """Génère un fichier audio pour un segment"""
    voix_code = VOIX.get(voix, VOIX["jeune_femme"])

    async def tache():
        communicate = edge_tts.Communicate(texte, voix_code)
        await communicate.save(nom_fichier)

    asyncio.run(tache())
    return nom_fichier


def _generer_image_pollinations(prompt, style_prompt, nom_fichier):
    """Génère une image via Pollinations.ai"""
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
    """Utilise Unsplash pour une image libre de droits"""
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
    """Crée une image style ardoise avec texte"""
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
    Retourne le chemin du fichier .mp4 ou None en cas d'erreur.
    """
    try:
        # Découpage
        segments = _decouper_script(cours)
        if not segments:
            return None

        # Paramètres de vitesse
        vitesse_map = {"lent": 1.4, "normal": 1.0, "rapide": 0.7}
        facteur = vitesse_map.get(vitesse, 1.0)

        # Préparer les scènes
        scenes = []
        audio_files = []
        for i, seg in enumerate(segments):
            img_file = os.path.join(TEMP_DIR, f"scene_{i}.png")
            audio_file = os.path.join(TEMP_DIR, f"audio_{i}.mp3")

            # Générer image selon style
            if STYLES[style]["source_image"] == "pollinations":
                _generer_image_pollinations(seg, STYLES[style]["style_prompt"], img_file)
            elif STYLES[style]["source_image"] == "unsplash":
                _generer_image_unsplash(seg, img_file)
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

            # Générer audio
            _generer_audio_segment(seg, voix, audio_file)
            audio_files.append(audio_file)

            # Clip audio
            audio_clip = AudioFileClip(audio_file)

            # Clip image compatible moviepy 2.x
            image_clip = ImageSequenceClip([img_file], durations=[audio_clip.duration * facteur])
            image_clip = image_clip.with_audio(audio_clip)
            scenes.append(image_clip)

        # Assemblage final
        video_final = os.path.join(OUTPUT_DIR, f"video_{uuid.uuid4().hex[:8]}.mp4")
        video = concatenate_videoclips(scenes, method="compose")
        video.write_videofile(video_final, fps=24)

        # Nettoyage
        for f in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, f))

        return video_final

    except Exception as e:
        print(f"❌ Erreur génération vidéo : {e}")
        return None