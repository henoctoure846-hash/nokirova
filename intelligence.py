# intelligence.py - Le cerveau adaptatif universel de NOKIROVA 🧠✨

from ia_handler import demander_ia_brut


# ═══════════════════════════════════════════
# 🔍 DÉTECTION AUTOMATIQUE DE MATIÈRE
# ═══════════════════════════════════════════
def detecter_matiere(texte_cours: str) -> dict:
    """
    Analyse un cours et détecte automatiquement :
    - La matière (ex: "Microéconomie", "Chimie organique", "Droit civil"...)
    - Le domaine général (Sciences, Lettres, Économie, Droit, Médecine...)
    - Le niveau (Lycée, Licence, Master, Doctorat...)
    - Les concepts clés
    - Le style pédagogique recommandé
    """
    prompt = f"""
Tu es un expert en analyse de contenu pédagogique.
Analyse ce cours et retourne UNIQUEMENT un JSON valide (sans markdown, sans texte avant/après).

FORMAT EXACT :
{{
  "matiere": "Nom précis de la matière",
  "domaine": "Sciences/Lettres/Économie/Droit/Médecine/Ingénierie/Arts/Autre",
  "niveau": "Lycée/Licence/Master/Doctorat/Professionnel",
  "concepts_cles": ["concept1", "concept2", "concept3"],
  "style_recommande": "formules/exemples_concrets/schémas/analyses/cas_pratiques/mnemotechniques",
  "emoji_matiere": "📚"
}}

EXEMPLES :
- Cours de microéconomie → {{"matiere":"Microéconomie","domaine":"Économie","niveau":"Licence","concepts_cles":["offre","demande","élasticité"],"style_recommande":"exemples_concrets","emoji_matiere":"💰"}}
- Cours d'algèbre linéaire → {{"matiere":"Algèbre linéaire","domaine":"Sciences","niveau":"Licence","concepts_cles":["matrices","vecteurs","déterminants"],"style_recommande":"formules","emoji_matiere":"🧮"}}
- Cours de droit civil → {{"matiere":"Droit civil","domaine":"Droit","niveau":"Licence","concepts_cles":["contrats","obligations","responsabilité"],"style_recommande":"cas_pratiques","emoji_matiere":"⚖️"}}

COURS À ANALYSER :
{texte_cours[:3000]}

JSON UNIQUEMENT :
"""
    try:
        reponse = demander_ia_brut(prompt)
        # Nettoyer la réponse (enlever markdown si présent)
        reponse = reponse.strip()
        if reponse.startswith("```"):
            reponse = reponse.split("```")[1]
            if reponse.startswith("json"):
                reponse = reponse[4:]
        reponse = reponse.strip()

        import json
        data = json.loads(reponse)
        return data
    except Exception as e:
        # Fallback si l'IA répond mal
        return {
            "matiere": "Matière générale",
            "domaine": "Autre",
            "niveau": "Licence",
            "concepts_cles": [],
            "style_recommande": "exemples_concrets",
            "emoji_matiere": "📚"
        }


# ═══════════════════════════════════════════
# 🎨 STYLES PÉDAGOGIQUES PAR DOMAINE
# ═══════════════════════════════════════════
STYLES_PEDAGOGIQUES = {
    "Sciences": {
        "instructions": (
            "Tu enseignes une matière scientifique. Utilise :\n"
            "- Des FORMULES MATHÉMATIQUES quand pertinent\n"
            "- Des EXEMPLES NUMÉRIQUES concrets avec calculs\n"
            "- Des SCHÉMAS textuels (avec ASCII art si utile)\n"
            "- Des MÉTHODES DE RÉSOLUTION étape par étape\n"
            "- Des ASTUCES MNÉMOTECHNIQUES pour retenir"
        ),
        "emojis": "🧮🔬⚗️📐🧪"
    },
    "Économie": {
        "instructions": (
            "Tu enseignes l'économie. Utilise :\n"
            "- Des EXEMPLES CONCRETS de la vie quotidienne (achats, marchés)\n"
            "- Des CHIFFRES et STATISTIQUES réelles\n"
            "- Des ANALOGIES simples (boulangerie, supermarché...)\n"
            "- Des SCHÉMAS de courbes décrits avec des mots\n"
            "- Des CAS RÉELS d'entreprises ou de pays"
        ),
        "emojis": "💰📊📈💼🏪"
    },
    "Droit": {
        "instructions": (
            "Tu enseignes le droit. Utilise :\n"
            "- Des CAS PRATIQUES concrets\n"
            "- Des références aux ARTICLES de loi (généraux)\n"
            "- Des EXEMPLES de jurisprudence simplifiés\n"
            "- Un raisonnement JURIDIQUE structuré (3 étapes)\n"
            "- Du vocabulaire JURIDIQUE expliqué simplement"
        ),
        "emojis": "⚖️📜🏛️👨‍⚖️📋"
    },
    "Médecine": {
        "instructions": (
            "Tu enseignes la médecine. Utilise :\n"
            "- Des DESCRIPTIONS ANATOMIQUES claires\n"
            "- Des SYMPTÔMES et SIGNES cliniques\n"
            "- Des MNÉMOTECHNIQUES pour les listes\n"
            "- Des CAS CLINIQUES simplifiés\n"
            "- Du vocabulaire MÉDICAL expliqué"
        ),
        "emojis": "🩺💊🧬🫀🧠"
    },
    "Lettres": {
        "instructions": (
            "Tu enseignes les lettres/langues. Utilise :\n"
            "- Des ANALYSES STYLISTIQUES\n"
            "- Des CITATIONS pertinentes\n"
            "- Des CONTEXTES HISTORIQUES\n"
            "- Des COMPARAISONS entre auteurs/œuvres\n"
            "- Des METHODES de dissertation/commentaire"
        ),
        "emojis": "📖✍️🎭📚🖋️"
    },
    "Ingénierie": {
        "instructions": (
            "Tu enseignes l'ingénierie. Utilise :\n"
            "- Des SCHÉMAS TECHNIQUES (en texte)\n"
            "- Des FORMULES et CALCULS\n"
            "- Des APPLICATIONS INDUSTRIELLES réelles\n"
            "- Des MÉTHODES DE CONCEPTION\n"
            "- Des EXEMPLES de projets concrets"
        ),
        "emojis": "⚙️🔧🏗️💻🔌"
    },
    "Arts": {
        "instructions": (
            "Tu enseignes les arts. Utilise :\n"
            "- Des DESCRIPTIONS VISUELLES détaillées\n"
            "- Des RÉFÉRENCES à des œuvres célèbres\n"
            "- Des CONTEXTES HISTORIQUES et CULTURELS\n"
            "- Des ANALYSES TECHNIQUES (couleurs, formes, composition)\n"
            "- Des COMPARAISONS entre artistes/mouvements"
        ),
        "emojis": "🎨🖼️🎭🎵🎬"
    },
    "Autre": {
        "instructions": (
            "Utilise une pédagogie universelle :\n"
            "- Des EXEMPLES CONCRETS du quotidien\n"
            "- Des SCHÉMAS ou LISTES claires\n"
            "- Des ANALOGIES simples\n"
            "- Une PROGRESSION logique\n"
            "- Des ASTUCES pour mémoriser"
        ),
        "emojis": "📚💡🎯✨🌟"
    }
}


def construire_contexte(matiere_info: dict) -> str:
    """
    Construit un contexte pédagogique sur mesure selon la matière détectée.
    """
    domaine = matiere_info.get("domaine", "Autre")
    matiere = matiere_info.get("matiere", "Matière générale")
    niveau = matiere_info.get("niveau", "Licence")
    concepts = matiere_info.get("concepts_cles", [])
    emoji = matiere_info.get("emoji_matiere", "📚")

    style = STYLES_PEDAGOGIQUES.get(domaine, STYLES_PEDAGOGIQUES["Autre"])

    contexte = f"""
🎓 CONTEXTE PÉDAGOGIQUE DÉTECTÉ :
{emoji} Matière : {matiere}
📊 Domaine : {domaine}
🎯 Niveau : {niveau}
🔑 Concepts clés : {', '.join(concepts) if concepts else 'à découvrir'}

📋 INSTRUCTIONS PÉDAGOGIQUES :
{style['instructions']}

🎨 Emojis du domaine : {style['emojis']}

⚠️ RÈGLES IMPORTANTES :
- Tu réponds en FRANÇAIS
- Tu t'adaptes à un étudiant qui apprend lentement
- Tu utilises des phrases COURTES
- Tu mets beaucoup d'EMOJIS pour rendre vivant
- Tu donnes toujours un ton ENCOURAGEANT 💪
"""
    return contexte


# ═══════════════════════════════════════════
# 🧠 FONCTION PRINCIPALE INTELLIGENTE
# ═══════════════════════════════════════════
def repondre_intelligemment(question: str, contexte_cours: str = "", matiere_info: dict = None) -> str:
    """
    Répond intelligemment en adaptant le style à la matière.

    Args:
        question: La question de l'utilisateur
        contexte_cours: Le contenu du cours (optionnel)
        matiere_info: Infos sur la matière (auto-détectée si fournie)
    """
    # Si pas de matière info, on détecte
    if matiere_info is None and contexte_cours:
        matiere_info = detecter_matiere(contexte_cours)
    elif matiere_info is None:
        matiere_info = {
            "matiere": "Question générale",
            "domaine": "Autre",
            "niveau": "Licence",
            "concepts_cles": [],
            "emoji_matiere": "💡"
        }

    contexte = construire_contexte(matiere_info)

    prompt = f"""{contexte}

📚 CONTENU DU COURS (si fourni) :
{contexte_cours[:3000] if contexte_cours else "Pas de cours fourni, réponds en général."}

❓ QUESTION DE L'ÉTUDIANT :
{question}

✍️ TA RÉPONSE PÉDAGOGIQUE (en français, simple, encourageante) :
"""
    return demander_ia_brut(prompt)


# TEST
if __name__ == "__main__":
    print("🧠 Test de l'intelligence universelle...\n")

    cours_test = """
    La microéconomie étudie le comportement des agents économiques individuels.
    La loi de l'offre et de la demande détermine le prix d'équilibre sur un marché.
    L'élasticité-prix mesure la sensibilité de la demande aux variations de prix.
    """

    print("🔍 Détection de matière...")
    info = detecter_matiere(cours_test)
    print(f"✅ Matière détectée : {info['emoji_matiere']} {info['matiere']}")
    print(f"📊 Domaine : {info['domaine']}")
    print(f"🎯 Niveau : {info['niveau']}")
    print(f"🔑 Concepts : {info['concepts_cles']}\n")

    print("💬 Réponse intelligente...")
    reponse = repondre_intelligemment(
        "Explique-moi simplement l'offre et la demande",
        cours_test,
        info
    )
    print(reponse)