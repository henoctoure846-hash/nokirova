# ia_handler.py - Cerveau IA Multi-Provider 🧠⚡
# Rotation automatique sur 7 IA gratuites (MIS À JOUR Juin 2026)

import os
import requests
from groq import Groq

# ═══════════════════════════════════════════
# 🔑 CHARGEMENT DES CLÉS
# ═══════════════════════════════════════════
try:
    from config import (
        GROQ_API_KEY, GEMINI_API_KEY, MISTRAL_API_KEY,
        CEREBRAS_API_KEY, OPENROUTER_API_KEY,
        TOGETHER_API_KEY, HUGGINGFACE_API_KEY
    )
except ImportError:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")


def _cle_valide(cle):
    return cle and "COLLE" not in cle and len(cle) > 10


# ═══════════════════════════════════════════
# 🤖 INITIALISATION DES CLIENTS
# ═══════════════════════════════════════════

# 1️⃣ GROQ
groq_client = None
try:
    if _cle_valide(GROQ_API_KEY):
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq prêt")
except Exception as e:
    print(f"⚠️ Groq indisponible : {e}")

# 2️⃣ GEMINI
gemini_client = None
try:
    if _cle_valide(GEMINI_API_KEY):
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_client = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini prêt")
except Exception as e:
    print(f"⚠️ Gemini indisponible : {e}")

# 3️⃣ MISTRAL
mistral_client = None
try:
    if _cle_valide(MISTRAL_API_KEY):
        try:
            from mistralai.client import MistralClient
            mistral_client = MistralClient(api_key=MISTRAL_API_KEY)
            print("✅ Mistral prêt")
        except ImportError:
            try:
                import mistralai
                mistral_client = mistralai.Mistral(api_key=MISTRAL_API_KEY)
                print("✅ Mistral prêt")
            except Exception:
                pass
except Exception as e:
    print(f"⚠️ Mistral indisponible : {e}")

# 4️⃣ CEREBRAS ⚡ (le plus rapide)
cerebras_client = None
try:
    if _cle_valide(CEREBRAS_API_KEY):
        from cerebras.cloud.sdk import Cerebras
        cerebras_client = Cerebras(api_key=CEREBRAS_API_KEY)
        print("✅ Cerebras prêt ⚡")
except Exception as e:
    print(f"⚠️ Cerebras indisponible : {e}")

# 5️⃣ OPENROUTER (via requests)
openrouter_ready = _cle_valide(OPENROUTER_API_KEY)
if openrouter_ready:
    print("✅ OpenRouter prêt 🌐")

# 6️⃣ TOGETHER
together_client = None
try:
    if _cle_valide(TOGETHER_API_KEY):
        from together import Together
        together_client = Together(api_key=TOGETHER_API_KEY)
        print("✅ Together prêt 🤝")
except Exception as e:
    print(f"⚠️ Together indisponible : {e}")

# 7️⃣ HUGGINGFACE (via requests)
huggingface_ready = _cle_valide(HUGGINGFACE_API_KEY)
if huggingface_ready:
    print("✅ HuggingFace prêt 🤗")


# ═══════════════════════════════════════════
# ⚡ MODÈLES (MIS À JOUR Juin 2026)
# ═══════════════════════════════════════════
MODELE_GROQ_RAPIDE = "llama-3.1-8b-instant"
MODELE_GROQ_QUALITE = "llama-3.3-70b-versatile"
MODELE_CEREBRAS = "llama3.1-8b"  # ✅ CORRIGÉ
MODELE_OPENROUTER = "meta-llama/llama-3.2-3b-instruct:free"  # ✅ CORRIGÉ
MODELE_TOGETHER = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
MODELE_HF = "mistralai/Mistral-7B-Instruct-v0.3"


# ═══════════════════════════════════════════
# 🔄 ROTATION AUTOMATIQUE SUR 7 IA
# ═══════════════════════════════════════════
def demander_ia_brut(prompt: str, temperature: float = 0.7, rapide: bool = False) -> str:
    erreurs = []

    # 1️⃣ CEREBRAS ⚡ (PRIORITÉ - le plus rapide)
    if cerebras_client:
        try:
            response = cerebras_client.chat.completions.create(
                model=MODELE_CEREBRAS,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=3000
            )
            return response.choices[0].message.content
        except Exception as e:
            erreurs.append(f"Cerebras: {str(e)[:80]}")
            print(f"⚠️ Cerebras échoué → Groq")

    # 2️⃣ GROQ
    if groq_client:
        try:
            modele = MODELE_GROQ_RAPIDE if rapide else MODELE_GROQ_QUALITE
            response = groq_client.chat.completions.create(
                model=modele,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=3000
            )
            return response.choices[0].message.content
        except Exception as e:
            erreurs.append(f"Groq: {str(e)[:80]}")
            print(f"⚠️ Groq échoué → Gemini")

    # 3️⃣ GEMINI
    if gemini_client:
        try:
            response = gemini_client.generate_content(prompt)
            return response.text
        except Exception as e:
            erreurs.append(f"Gemini: {str(e)[:80]}")
            print(f"⚠️ Gemini échoué → Together")

    # 4️⃣ TOGETHER
    if together_client:
        try:
            response = together_client.chat.completions.create(
                model=MODELE_TOGETHER,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=3000
            )
            return response.choices[0].message.content
        except Exception as e:
            erreurs.append(f"Together: {str(e)[:80]}")
            print(f"⚠️ Together échoué → OpenRouter")

    # 5️⃣ OPENROUTER
    if openrouter_ready:
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://nokirova.app",
                "X-Title": "NOKIROVA"
            }
            data = {
                "model": MODELE_OPENROUTER,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": 3000
            }
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers, json=data, timeout=60
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            erreurs.append(f"OpenRouter: {str(e)[:80]}")
            print(f"⚠️ OpenRouter échoué → Mistral")

    # 6️⃣ MISTRAL
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
            erreurs.append(f"Mistral: {str(e)[:80]}")
            print(f"⚠️ Mistral échoué → HuggingFace")

    # 7️⃣ HUGGINGFACE (dernier recours)
    if huggingface_ready:
        try:
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            data = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 2000,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
            r = requests.post(
                f"https://api-inference.huggingface.co/models/{MODELE_HF}",
                headers=headers, json=data, timeout=90
            )
            r.raise_for_status()
            result = r.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            return str(result)
        except Exception as e:
            erreurs.append(f"HuggingFace: {str(e)[:80]}")

    return (
        f"❌ Désolé, toutes les IA sont momentanément indisponibles.\n\n"
        f"💡 Attends 5 minutes et réessaie.\n\n"
        f"Détails :\n" + "\n".join(erreurs)
    )


# ═══════════════════════════════════════════
# 💬 QUESTION LIBRE
# ═══════════════════════════════════════════
def demander_ia(prompt: str) -> str:
    prompt_complet = f"""Tu es NOKIROVA, un professeur intelligent universel.
Tu enseignes TOUTES les matières. Tu réponds TOUJOURS en français.
Tu utilises des phrases courtes, beaucoup d'emojis, des exemples concrets.
Ton encourageant et motivant.

QUESTION : {prompt}

RÉPONSE :"""
    return demander_ia_brut(prompt_complet, rapide=False)


# ═══════════════════════════════════════════
# 💡 EXPLICATION SIMPLIFIÉE
# ═══════════════════════════════════════════
def expliquer_simplement(texte: str) -> str:
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
# 📝 RÉSUMÉ
# ═══════════════════════════════════════════
def creer_resume(texte: str) -> str:
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
# 🚀 DÉTECTION RAPIDE DE MATIÈRE
# ═══════════════════════════════════════════
def detecter_matiere_rapide(texte: str) -> dict:
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