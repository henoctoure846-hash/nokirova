# ia_handler.py - Cerveau IA Multi-Provider 🧠⚡ (AMÉLIORÉ)
# Rotation automatique sur 7 IA gratuites + NLLB-200 + Recherche Web

import os
import requests
from groq import Groq
from duckduckgo_search import DDGS  # Nouvelle importation pour la recherche web

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
MODELE_CEREBRAS = "llama3.1-8b"
MODELE_OPENROUTER = "meta-llama/llama-3.2-3b-instruct:free"
MODELE_TOGETHER = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
MODELE_HF = "mistralai/Mistral-7B-Instruct-v0.3"
MODELE_NLLB = "facebook/nllb-200-distilled-600M"  # Traduction gratuite


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
                max_tokens=8000  # AUGMENTÉ
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
                max_tokens=8000  # AUGMENTÉ
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
                max_tokens=8000  # AUGMENTÉ
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
                "max_tokens": 8000  # AUGMENTÉ
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
                    max_tokens=8000  # AUGMENTÉ
                )
            except ImportError:
                response = mistral_client.chat.complete(
                    model="mistral-large-latest",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=8000  # AUGMENTÉ
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
                    "max_new_tokens": 8000,  # AUGMENTÉ
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
# 💬 QUESTION LIBRE (PROMPT AMÉLIORÉ + RECHERCHE WEB)
# ═══════════════════════════════════════════
def demander_ia(prompt: str) -> str:
    # Si la question semble factuelle, on enrichit avec une recherche web
    if len(prompt.split()) > 3:
        # Détection simple de question factuelle
        factuelle = any(marqueur in prompt.lower() for marqueur in [
            "quelle est la capitale", "date de naissance", "définition de",
            "combien de", "qui a", "quel est le", "qu'est-ce que",
            "explique-moi", "c'est quoi", "définition", "quels sont"
        ])
        if factuelle:
            try:
                from web_search import rechercher_web
                resultats = rechercher_web(prompt)
                if resultats:
                    contexte_web = "\n\n".join([
                        f"🌐 **{r['titre']}**\n{r['extrait']}\n🔗 {r['url']}"
                        for r in resultats
                    ])
                    prompt = f"{prompt}\n\n📖 **Informations récentes trouvées sur le web :**\n{contexte_web}"
            except Exception as e:
                print(f"⚠️ Recherche web échouée : {e}")

    prompt_complet = f"""Tu es NOKIROVA, un professeur intelligent universel.

📋 **RÈGLES STRICTES :**
- Tu enseignes TOUTES les matières
- Tu réponds TOUJOURS en français
- Tu utilises des phrases COURTES et CLAIRES
- Tu donnes des EXEMPLES CONCRETS
- Tu es ENCOURAGEANT et MOTIVANT
- Tu STRUCTURES ta réponse avec des titres et des listes
- Tu utilises des emojis pour rendre la lecture agréable
- Tu donnes toujours des ASTUCES MNÉMOTECHNIQUES si possible
- Tu inclus des PIÈGES À ÉVITER pour les examens
- Sois le plus complet possible (vise au moins 5 paragraphes)

📚 **LA QUESTION DE L'ÉTUDIANT :**
{prompt}

🎯 **TA RÉPONSE (structure, exemples, astuces, pièges) :**"""
    return demander_ia_brut(prompt_complet, rapide=False)


# ═══════════════════════════════════════════
# 💡 EXPLICATION SIMPLIFIÉE (AMÉLIORÉE)
# ═══════════════════════════════════════════
def expliquer_simplement(texte: str) -> str:
    prompt = f"""Tu es NOKIROVA, professeur universel. Explique ce contenu SIMPLEMENT.

📋 **FORMAT OBLIGATOIRE :**

## **📖 CE QU'IL FAUT COMPRENDRE**
(2-3 phrases ultra simples, comme si tu parlais à un débutant)

## **📝 EXPLICATION ÉTAPE PAR ÉTAPE**
1. ...
2. ...
3. ...

## **💡 EXEMPLE CONCRET**
(Tire de la vie quotidienne, avec des chiffres si possible)

## **🎯 ASTUCE POUR RETENIR**
(Phrase mnémotechnique ou image mentale)

## **⚠️ PIÈGES À ÉVITER**
- Piège 1 : ...
- Piège 2 : ...

## **💪 POUR L'EXAMEN**
(Conseils pratiques pour le jour J)

---

**📄 CONTENU À EXPLIQUER :**
{texte[:8000]}

**🎓 RÉPONSE DÉTAILLÉE (vise 10-15 lignes minimum) :**"""
    return demander_ia_brut(prompt, rapide=False)


# ═══════════════════════════════════════════
# 📝 RÉSUMÉ (AMÉLIORÉ)
# ═══════════════════════════════════════════
def creer_resume(texte: str) -> str:
    prompt = f"""Tu es NOKIROVA, professeur universel. Résume ce cours.

📋 **FORMAT OBLIGATOIRE :**

## **🎯 OBJECTIF DU COURS**
(1-2 phrases)

## **💡 LES 3-5 IDÉES PRINCIPALES**
1. **Idée 1** : Explication claire (2-3 phrases)
2. **Idée 2** : Explication claire
3. **Idée 3** : Explication claire

## **📚 DÉFINITIONS / FORMULES IMPORTANTES**
- **Terme 1** : Définition simple
- **Formule 1** : Explication

## **⚠️ PIÈGES À ÉVITER**
- Piège fréquent 1
- Piège fréquent 2

## **🎓 POUR L'EXAMEN**
(Conseils ciblés et incontournables)

## **🌟 POUR ALLER PLUS LOIN**
(Question ouverte pour réfléchir)

---

**📄 CONTENU DU COURS :**
{texte[:8000]}

**📝 RÉSUMÉ COMPLET :**"""
    return demander_ia_brut(prompt, rapide=False)


# ═══════════════════════════════════════════
# 🌍 TRADUCTION SPÉCIALISÉE (NLLB-200)
# ═══════════════════════════════════════════
def traduire_rapide(texte: str, langue_cible: str = "anglais") -> str:
    """Traduction rapide avec NLLB-200 via HuggingFace"""
    if not huggingface_ready:
        # Fallback vers la rotation générale
        prompt = f"""Tu es un traducteur professionnel. Traduis ce texte vers le {langue_cible}.

RÈGLES STRICTES :
- Donne UNIQUEMENT la traduction
- Pas d'explication, pas de commentaire
- Préserve le sens, le ton et la mise en forme

TEXTE À TRADUIRE :
{texte[:5000]}

TRADUCTION EN {langue_cible.upper()} :"""
        return demander_ia_brut(prompt, temperature=0.3)

    try:
        # Mapping des langues vers les codes NLLB
        langue_map = {
            "français": "fra_Latn",
            "anglais": "eng_Latn",
            "espagnol": "spa_Latn",
            "allemand": "deu_Latn",
            "italien": "ita_Latn",
            "portugais": "por_Latn",
            "arabe": "arb_Arab",
            "chinois": "zho_Hans",
            "japonais": "jpn_Jpan",
            "russe": "rus_Cyrl"
        }
        # Détection automatique de la langue source
        source = "fra_Latn"  # Par défaut français
        cible = langue_map.get(langue_cible, "eng_Latn")

        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        payload = {
            "inputs": texte,
            "parameters": {
                "src_lang": source,
                "tgt_lang": cible,
                "max_length": 4000
            }
        }
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{MODELE_NLLB}",
            headers=headers,
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("translation_text", result[0].get("generated_text", ""))
        # Fallback
        return demander_ia_brut(f"Traduis en {langue_cible} : {texte}", temperature=0.3)
    except Exception as e:
        print(f"⚠️ NLLB échoué, fallback IA : {e}")
        return demander_ia_brut(f"Traduis en {langue_cible} : {texte}", temperature=0.3)


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