# exercice_generator.py - Génération RAPIDE d'exercices 🎯⚡ (AMÉLIORÉ)

from ia_handler import demander_ia_brut


def generer_qcm(cours: str, nombre: int = 5) -> str:
    """Génère des QCM (rapide)"""
    prompt = f"""Tu es NOKIROVA, prof intelligent. Génère {nombre} QCM bien structurés à partir de ce cours.

FORMAT OBLIGATOIRE pour chaque QCM :

═══════════════════════════════════════
📝 QCM N°1
Question : ...

A) ...
B) ...
C) ...
D) ...

🔒 [CORRECTION]
✅ Bonne réponse : X
💡 Explication détaillée : ...
⚠️ Erreur courante : ...
═══════════════════════════════════════

Répète pour chaque QCM. Réponds en français. Sois très complet : chaque explication doit faire au moins 3 phrases.

COURS :
{cours}

QCM :"""
    return demander_ia_brut(prompt, rapide=False)


def generer_questions_cours(cours: str, nombre: int = 5) -> str:
    """Génère des questions de cours"""
    prompt = f"""Tu es NOKIROVA. Génère {nombre} questions de cours pédagogiques.

FORMAT OBLIGATOIRE :

═══════════════════════════════════════
❓ QUESTION N°1
...

🔒 [RÉPONSE]
📖 Réponse modèle :
...

💡 Explication simple :
...

🎯 À retenir :
...
═══════════════════════════════════════

Réponds en français. Sois très complet : chaque réponse doit comporter au moins 4 phrases d'explication.

COURS :
{cours}

QUESTIONS :"""
    return demander_ia_brut(prompt, rapide=False)


def generer_exercices_examen(cours: str, niveau: str = "intermediaire", nombre: int = 3) -> str:
    """Génère des exercices type examen"""
    niveaux = {
        "debutant": "🟢 NIVEAU DÉBUTANT (très simples, avec aide)",
        "intermediaire": "🟡 NIVEAU INTERMÉDIAIRE (cours normal)",
        "difficile": "🟠 NIVEAU DIFFICILE (examen réel)",
        "ultra_difficile": "🔴 NIVEAU ULTRA DIFFICILE (avec pièges)"
    }
    niveau_desc = niveaux.get(niveau, niveaux["intermediaire"])

    prompt = f"""Tu es NOKIROVA. Génère {nombre} exercices type examen.
NIVEAU : {niveau_desc}

FORMAT OBLIGATOIRE pour chaque exercice :

═══════════════════════════════════════
📚 EXERCICE N°1

📋 ÉNONCÉ :
...

🔒 [CORRECTION DÉTAILLÉE]

📝 Étape 1 : ...
📝 Étape 2 : ...
📝 Étape 3 : ...

✅ Résultat final : ...

💡 Astuces : ...

⚠️ Erreurs à éviter : ...
═══════════════════════════════════════

Réponds en français. Sois très complet : chaque correction doit détailler au moins 5 étapes.

COURS :
{cours}

EXERCICES :"""
    return demander_ia_brut(prompt, rapide=False)