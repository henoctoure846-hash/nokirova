# ia_handler.py - Cerveau IA OPTIMISÉ ULTRA-RAPIDE 🧠⚡

from groq import Groq
import os

# Essayer d'importer config.py (local), sinon utiliser les variables d'environnement (Render)
try:
    from config import GROQ_API_KEY, GEMINI_API_KEY, MISTRAL_API_KEY
except ImportError:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

# ═══════════════════════════════════════════
# 🤖 CONFIGURATION DES IA
# ═══════════════════════════════════════════

# 1️⃣ GROQ
groq_client = None
try:
    if GROQ_API_KEY and GROQ_API_KEY != "":
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq prêt")
except Exception as e:
    print(f"⚠️ Groq indisponible : {e}")

# 2️⃣ GEMINI
gemini_client = None
try:
    if GEMINI_API_KEY and GEMINI_API_KEY != "":
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        gemini_client = genai.GenerativeModel('gemini-flash-latest')
        print("✅ Gemini prêt (backup)")
except Exception as e:
    print(f"⚠️ Gemini indisponible : {e}")

# 3️⃣ MISTRAL
mistral_client = None
try:
    if MISTRAL_API_KEY and MISTRAL_API_KEY != "":
        try:
            from mistralai.client import MistralClient

            mistral_client = MistralClient(api_key=MISTRAL_API_KEY)
            print("✅ Mistral prêt (backup)")
        except ImportError:
            try:
                import mistralai

                mistral_client = mistralai.Mistral(api_key=MISTRAL_API_KEY)
                print("✅ Mistral prêt (backup)")
            except Exception:
                pass
except Exception as e:
    print(f"⚠️ Mistral indisponible : {e}")

# ═══════════════════════════════════════════
# ⚡ MODÈLES PAR VITESSE
# ═══════════════════════════════════════════
MODELE_RAPIDE = "llama-3.1-8b-instant"  # ⚡⚡⚡ Ultra rapide
MODELE_QUALITE = "llama-3.3-70b-versatile"  # ⚡⚡ Plus puissant


# ═══════════════════════════════════════════
# 🔄 ROTATION AUTOMATIQUE
# ═══════════════════════════════════════════
def demander_ia_brut(prompt: str, temperature: float = 0.7, rapide: bool = False) -> str:
    """
    Essaie chaque IA dans l'ordre jusqu'à ce qu'une réponde.

    Args:
        prompt: La question
        temperature: Créativité (0.0-1.0)
        rapide: Si True, utilise le modèle rapide (pour les tâches simples)
    """
    erreurs = []
    modele = MODELE_RAPIDE if rapide else MODELE_QUALITE

    # 1️⃣ GROQ
    if groq_client:
        try:
            response = groq_client.chat.completions.create(
                model=modele,
                messages=[{"role": "user", "content": prompt}],  # type: ignore
                temperature=temperature,
                max_tokens=3000
            )
            return response.choices[0].message.content
        except Exception as e:
            erreurs.append(f"Groq: {str(e)[:100]}")
            print(f"⚠️ Groq échoué → Gemini")

    # 2️⃣ GEMINI
    if gemini_client:
        try:
            response = gemini_client.generate_content(prompt)
            return response.text
        except Exception as e:
            erreurs.append(f"Gemini: {str(e)[:100]}")
            print(f"⚠️ Gemini échoué → Mistral")

    # 3️⃣ MISTRAL
    if mistral_client:
        try:
            try:
                from mistralai.models.chat_completion import ChatMessage
                response = mistral_client.chat(
                    model="mistral-large-latest",
                    messages=[ChatMessage(role="user", content=prompt)],
                    temperature=temperature,
                    max_tokens=3000
                )
            except ImportError:
                response = mistral_client.chat.complete(
                    model="mistral-large-latest",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=3000
                )
            return response.choices[0].message.content
        except Exception as e:
            erreurs.append(f"Mistral: {str(e)[:100]}")

    return (
            f"❌ Désolé, toutes les IA sont momentanément indisponibles.\n\n"
            f"💡 Attends 5 minutes et réessaie.\n\n"
            f"Détails :\n" + "\n".join(erreurs)
    )


# ═══════════════════════════════════════════
# 💬 QUESTION LIBRE
# ═══════════════════════════════════════════
def demander_ia(prompt: str) -> str:
    """Pose une question pédagogique générale (modèle qualité)"""
    prompt_complet = f"""Tu es NOKIROVA, un professeur intelligent universel.
Tu enseignes TOUTES les matières. Tu réponds TOUJOURS en français.
Tu utilises des phrases courtes, beaucoup d'emojis, des exemples concrets.
Ton encourageant et motivant.

QUESTION : {prompt}

RÉPONSE :"""

    return demander_ia_brut(prompt_complet, rapide=False)


# ═══════════════════════════════════════════
# 💡 EXPLICATION SIMPLIFIÉE (OPTIMISÉ)
# ═══════════════════════════════════════════
def expliquer_simplement(texte: str) -> str:
    """Explique un cours simplement (UNE seule requête)"""
    prompt = f"""Tu es NOKIROVA, prof intelligent universel. Explique ce contenu à un étudiant qui apprend lentement.

📋 FORMAT OBLIGATOIRE :

**CE QU'IL FAUT COMPRENDRE**
(2-3 phrases ultra simples)

**EXPLICATION ÉTAPE PAR ÉTAPE**
1. ...
2. ...
3. ...

**EXEMPLE CONCRET**
(de la vie quotidienne)

**ASTUCE POUR RETENIR**
(mnémotechnique)

**PIÈGES À ÉVITER**
- ...

**TU PEUX LE FAIRE !** (encouragement)

Utilise BEAUCOUP d'emojis 🎯📚💡, phrases COURTES, ton encourageant.

CONTENU :
{texte}

RÉPONSE :"""

    return demander_ia_brut(prompt, rapide=False)


# ═══════════════════════════════════════════
# 📝 RÉSUMÉ (OPTIMISÉ)
# ═══════════════════════════════════════════
def creer_resume(texte: str) -> str:
    """Crée un résumé structuré (UNE seule requête)"""
    prompt = f"""Tu es NOKIROVA, prof intelligent. Résume ce cours pour un étudiant qui révise.

📋 FORMAT OBLIGATOIRE :

**OBJECTIF DU COURS**
(1-2 phrases)

**LES 3-5 IDÉES PRINCIPALES**
1. ...
2. ...
3. ...

**DÉFINITIONS / FORMULES IMPORTANTES**
(à connaître par cœur)

**À RETENIR ABSOLUMENT**
- ...
- ...

**PIÈGES À ÉVITER**
- ...

**POUR L'EXAMEN**
(conseils ciblés)

Réponds en français, avec emojis, phrases courtes, ton encourageant.

COURS :
{texte}

RÉSUMÉ :"""

    return demander_ia_brut(prompt, rapide=False)


# ═══════════════════════════════════════════
# 🚀 DÉTECTION RAPIDE DE MATIÈRE (modèle 8B)
# ═══════════════════════════════════════════
def detecter_matiere_rapide(texte: str) -> dict:
    """Détection ULTRA-RAPIDE de matière (modèle 8B)"""
    prompt = f"""Analyse ce cours et retourne UNIQUEMENT un JSON valide (sans markdown).

Format :
{{"matiere":"nom","domaine":"Sciences/Économie/Droit/Médecine/Lettres/Ingénierie/Arts/Autre","niveau":"Lycée/Licence/Master","emoji_matiere":"📚"}}

COURS : {texte[:1500]}

JSON :"""

    reponse = demander_ia_brut(prompt, temperature=0.3, rapide=True)

    try:
        import json
        reponse = reponse.strip()
        if reponse.startswith("```"):
            reponse = reponse.split("```")[1]
            if reponse.startswith("json"):
                reponse = reponse[4:]
        reponse = reponse.strip()
        return json.loads(reponse)
    except Exception:
        return {
            "matiere": "Cours général",
            "domaine": "Autre",
            "niveau": "Licence",
            "emoji_matiere": "📚"
        }