# db/tuteur_ia.py - Tuteur IA personnalisé NOKIROVA 🌸
# PHASE D4 - Apprentissage adaptatif

from datetime import datetime, timedelta
from db.base import get_connexion
from db.historique import lister_historique_complet, compter_par_type
from db.stats import get_stats


# ═══════════════════════════════════════════
# 🧠 ANALYSE DES POINTS FAIBLES
# ═══════════════════════════════════════════

def get_matiere_performance():
    """Analyse les performances par matière à partir de l'historique"""
    conn = get_connexion()
    cur = conn.cursor()

    cur.execute("""
        SELECT matiere, type, question, reponse
        FROM historique 
        WHERE matiere IS NOT NULL AND matiere != '' AND matiere != 'Général'
        ORDER BY date DESC
    """)
    rows = cur.fetchall()
    conn.close()

    performances = {}

    for matiere, type_action, question, reponse in rows:
        if matiere not in performances:
            performances[matiere] = {
                "questions": 0,
                "resumes": 0,
                "explications": 0,
                "qcms": 0,
                "total": 0
            }

        performances[matiere]["total"] += 1

        if type_action == "question_libre":
            performances[matiere]["questions"] += 1
        elif type_action == "resume":
            performances[matiere]["resumes"] += 1
        elif type_action == "explication":
            performances[matiere]["explications"] += 1
        elif type_action == "qcm":
            performances[matiere]["qcms"] += 1

    for matiere, data in performances.items():
        score = 0
        if data["questions"] > 0:
            score += min(30, data["questions"] * 3)
        if data["resumes"] > 0:
            score += 20
        if data["explications"] > 0:
            score += 20
        if data["qcms"] > 0:
            score += min(30, data["qcms"] * 5)
        data["score_maitrise"] = min(100, score)

        if data["score_maitrise"] < 30:
            data["niveau"] = "🔴 Débutant"
            data["conseil"] = "Commence par importer un cours sur cette matière"
        elif data["score_maitrise"] < 60:
            data["niveau"] = "🟡 Intermédiaire"
            data["conseil"] = "Fais des QCM pour tester tes connaissances"
        else:
            data["niveau"] = "🟢 Avancé"
            data["conseil"] = "Tu maîtrises bien ! Passe aux questions d'examen"

    return performances


def get_points_faibles(limit=3):
    """Retourne les matières avec le plus faible score de maîtrise"""
    perf = get_matiere_performance()

    actives = [(matiere, data["score_maitrise"], data["total"])
               for matiere, data in perf.items() if data["total"] >= 2]

    actives.sort(key=lambda x: x[1])

    result = []
    for matiere, score, total in actives[:limit]:
        data = perf[matiere]
        result.append({
            "matiere": matiere,
            "score": score,
            "niveau": data["niveau"],
            "conseil": data["conseil"],
            "questions_posees": data["questions"],
            "total_actions": total
        })

    return result


def get_meilleure_matiere():
    """Retourne la matière la mieux maîtrisée"""
    perf = get_matiere_performance()

    meilleure = None
    meilleur_score = -1

    for matiere, data in perf.items():
        if data["score_maitrise"] > meilleur_score and data["total"] >= 3:
            meilleur_score = data["score_maitrise"]
            meilleure = matiere

    return meilleure, meilleur_score


# ═══════════════════════════════════════════
# 📈 PROGRESSION ET STATS
# ═══════════════════════════════════════════

def get_progression_semaine():
    """Activité des 7 derniers jours"""
    conn = get_connexion()
    cur = conn.cursor()

    progression = []
    for i in range(6, -1, -1):
        date_jour = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        cur.execute("""
            SELECT COUNT(*) FROM historique 
            WHERE date(date) = ?
        """, (date_jour,))
        count = cur.fetchone()[0]
        progression.append({
            "date": date_jour,
            "activites": count
        })

    conn.close()
    return progression


def get_stats_par_type():
    """Statistiques par type d'activité"""
    return compter_par_type()


# ═══════════════════════════════════════════
# 🎯 RECOMMANDATIONS PERSONNALISÉES
# ═══════════════════════════════════════════

def get_recommandations_jour():
    """Génère des recommandations basées sur l'activité récente"""
    stats = get_stats()
    points_faibles = get_points_faibles(2)
    historique_recent = lister_historique_complet(10)

    recommandations = []

    today = datetime.now().strftime('%Y-%m-%d')
    actif_aujourdhui = any(len(h) > 5 and h[5].startswith(today) for h in historique_recent)

    if not actif_aujourdhui and stats.get("streak", 0) > 0:
        recommandations.append({
            "type": "streak",
            "titre": "🔥 Ne perds pas ta streak !",
            "message": f"Connecte-toi aujourd'hui pour garder tes {stats.get('streak', 0)} jours d'affilée",
            "action": "Poser une question",
            "lien": "/chat"
        })

    if points_faibles:
        pire = points_faibles[0]
        recommandations.append({
            "type": "revision",
            "titre": f"📚 Réviser {pire['matiere']}",
            "message": pire["conseil"],
            "action": "Commencer",
            "lien": "/chat"
        })

    if len(historique_recent) < 5:
        recommandations.append({
            "type": "decouverte",
            "titre": "💡 Explore NOKIROVA",
            "message": "Importe un cours et teste les QCM pour progresser plus vite !",
            "action": "Importer un cours",
            "lien": "/import"
        })

    return recommandations


def generer_conseil_motivant():
    """Génère un conseil motivant personnalisé"""
    stats = get_stats()
    points_faibles = get_points_faibles(1)
    meilleure, score = get_meilleure_matiere()

    niveau = stats.get("niveau", 1)
    streak = stats.get("streak", 0)
    xp = stats.get("xp", 0)

    if niveau < 3:
        return f"🌱 **Bienvenue dans NOKIROVA !** Importe ton premier cours et je t'aiderai à tout comprendre. Tu es au niveau {niveau} pour l'instant."

    elif niveau < 7:
        prochain_niveau = 100 - (xp % 100)
        return f"📈 **Tu progresses bien !** Encore {prochain_niveau} XP pour passer au niveau {niveau + 1}. Continue comme ça !"

    elif niveau < 15:
        if points_faibles:
            return f"🎯 **Objectif du jour :** Concentre-toi sur {points_faibles[0]['matiere']}. {points_faibles[0]['conseil']}"
        else:
            return f"⚡ **Tu deviens un expert !** Essaie les examens complets pour te challenger."

    else:
        return f"🏆 **Niveau {niveau} - Légende !** Tu maîtrises NOKIROVA. Partage l'appli avec tes amis !"


# ═══════════════════════════════════════════
# 📊 DASHBOARD COMPLET POUR TUTEUR
# ═══════════════════════════════════════════

def get_tuteur_dashboard():
    """Données complètes pour afficher le tuteur IA"""
    stats = get_stats()
    points_faibles = get_points_faibles(3)
    progression = get_progression_semaine()
    recommandations = get_recommandations_jour()
    meilleure, score = get_meilleure_matiere()
    stats_par_type = get_stats_par_type()
    conseil = generer_conseil_motivant()

    xp_actuel = stats.get("xp", 0)
    xp_prochain = 100 - (xp_actuel % 100) if xp_actuel % 100 != 0 else 100
    niveau_actuel = stats.get("niveau", 1)

    return {
        "stats": {
            "niveau": niveau_actuel,
            "xp": xp_actuel,
            "xp_prochain_niveau": xp_prochain,
            "streak": stats.get("streak", 0),
            "pourcentage_niveau": (xp_actuel % 100) if xp_actuel % 100 != 0 else 100,
            "titre_niveau": get_titre_niveau(niveau_actuel)
        },
        "points_faibles": points_faibles,
        "progression_semaine": progression,
        "recommandations": recommandations,
        "meilleure_matiere": meilleure,
        "stats_par_type": dict(stats_par_type) if stats_par_type else {},
        "conseil_perso": conseil,
        "total_actions": sum(s[1] for s in stats_par_type) if stats_par_type else 0
    }


def get_titre_niveau(niveau):
    if niveau < 3:
        return "🌱 Apprenti"
    elif niveau < 7:
        return "📖 Étudiant"
    elif niveau < 12:
        return "🎓 Studieux"
    elif niveau < 20:
        return "⭐ Expert"
    elif niveau < 30:
        return "🏆 Maître"
    else:
        return "👑 Légende"