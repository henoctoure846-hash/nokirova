# web/app.py - NOKIROVA WEB 🌸 PHASE 3 COMPLÈTE
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import sys
import os
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import database as db
    db.init_db()
    db.maj_streak()
    print("✅ Database initialisée")
except Exception as e:
    print(f"⚠️ Init DB : {e}")

# Init table planificateur
try:
    from db.planificateur import init_table_planificateur
    init_table_planificateur()
except Exception as e:
    print(f"⚠️ Init planning : {e}")

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# ═══════════════════════════════════════════
# 👤 MIDDLEWARE MULTI-UTILISATEURS
# ═══════════════════════════════════════════
@app.before_request
def detecter_utilisateur():
    """Détecte le user_id à chaque requête via header ou cookie"""
    from db.base import set_user
    # Priorité 1 : header X-User-Id
    user_id = request.headers.get('X-User-Id')
    # Priorité 2 : cookie
    if not user_id:
        user_id = request.cookies.get('nokirova_user_id')
    set_user(user_id)

session_data = {
    'cours_actuel': '',
    'nom_cours': 'Aucun cours chargé',
    'matiere_detectee': '',
    'messages_chat': [],
}

# ═══════════════════════════════════════════
# 🎨 PRÉFÉRENCES AUTO (injecté dans toutes les pages)
# ═══════════════════════════════════════════
@app.context_processor
def inject_preferences():
    """Charge les préférences DB et les injecte automatiquement
    dans CHAQUE template (pref_mode, pref_theme, pref_taille)"""
    try:
        from db.preferences import charger_preference
        return {
            'pref_mode': charger_preference('mode', 'clair'),
            'pref_theme': charger_preference('theme', 'printemps'),
            'pref_taille': charger_preference('taille', 'normal'),
        }
    except Exception:
        return {
            'pref_mode': 'clair',
            'pref_theme': 'printemps',
            'pref_taille': 'normal',
        }


def get_stats_safe():
    try:
        return db.get_stats()
    except Exception:
        return {"niveau": 1, "xp": 0, "streak_jours": 0, "cours_importes": 0}


def saluer():
    h = datetime.now().hour
    if h < 12: return "🌅 Bonjour"
    elif h < 18: return "☀️ Bon après-midi"
    else: return "🌙 Bonsoir"


def get_date_fr():
    jours = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]
    mois = ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
    n = datetime.now()
    return f"{jours[n.weekday()]} {n.day} {mois[n.month - 1]}"


def parser_qcm(texte):
    qcms = []
    try:
        blocs = re.split(r'QCM\s*N?°?\s*\d+', texte, flags=re.IGNORECASE)
        blocs = [b.strip() for b in blocs if b.strip()]
        for bloc in blocs:
            qcm = {}
            lignes = [l.strip() for l in bloc.split('\n') if l.strip()]
            question_lines, options, reponse, explication = [], [], '', ''
            mode = 'question'
            for ligne in lignes:
                m_opt = re.match(r'^([A-D])[)\.]\s*(.+)$', ligne, re.IGNORECASE)
                m_rep = re.search(r'(bonne\s*réponse|réponse\s*correcte|réponse)\s*:?\s*(.+)', ligne, re.IGNORECASE)
                m_exp = re.search(r'(explication|pourquoi)\s*:?\s*(.+)', ligne, re.IGNORECASE)
                if m_opt:
                    mode = 'options'
                    options.append({'lettre': m_opt.group(1).upper(), 'texte': m_opt.group(2).strip()})
                elif m_rep and mode in ('options','reponse'):
                    mode = 'reponse'; reponse = m_rep.group(2).strip()
                elif m_exp:
                    mode = 'explication'; explication = m_exp.group(2).strip()
                elif mode == 'question':
                    l = re.sub(r'^(question\s*:?\s*)', '', ligne, flags=re.IGNORECASE).strip()
                    if l: question_lines.append(l)
            qcm['question'] = ' '.join(question_lines).strip()
            qcm['options'] = options
            qcm['reponse'] = reponse
            qcm['explication'] = explication
            if qcm['question']: qcms.append(qcm)
    except Exception as e:
        print(f"⚠️ Parsing QCM : {e}")
    return qcms


def parser_questions(texte):
    items = []
    try:
        blocs = re.split(r'(?:Question|Q)\s*N?°?\s*\d+', texte, flags=re.IGNORECASE)
        blocs = [b.strip() for b in blocs if b.strip()]
        for bloc in blocs:
            lignes = [l.strip() for l in bloc.split('\n') if l.strip()]
            q_lines, r_lines, mode = [], [], 'q'
            for ligne in lignes:
                m_rep = re.search(r'(réponse|réponse\s*:)\s*:?\s*(.*)', ligne, re.IGNORECASE)
                if m_rep:
                    mode = 'r'
                    if m_rep.group(2).strip(): r_lines.append(m_rep.group(2).strip())
                elif mode == 'q':
                    l = re.sub(r'^(question\s*:?\s*)', '', ligne, flags=re.IGNORECASE).strip()
                    if l: q_lines.append(l)
                else: r_lines.append(ligne)
            q = ' '.join(q_lines).strip()
            r = ' '.join(r_lines).strip()
            if q: items.append({'question': q, 'reponse': r})
    except Exception as e:
        print(f"⚠️ Parsing Q : {e}")
    return items


def parser_flashcards(texte):
    cards = []
    try:
        blocs = re.split(r'(?:Flashcard|Carte|Card)\s*N?°?\s*\d+', texte, flags=re.IGNORECASE)
        blocs = [b.strip() for b in blocs if b.strip()]
        for bloc in blocs:
            lignes = [l.strip() for l in bloc.split('\n') if l.strip()]
            recto_lines, verso_lines, mode = None, None, None
            recto_lines, verso_lines = [], []
            for ligne in lignes:
                m_r = re.match(r'^(recto|question|q)\s*:?\s*(.*)$', ligne, re.IGNORECASE)
                m_v = re.match(r'^(verso|réponse|reponse|r)\s*:?\s*(.*)$', ligne, re.IGNORECASE)
                if m_r:
                    mode = 'recto'
                    if m_r.group(2).strip(): recto_lines.append(m_r.group(2).strip())
                elif m_v:
                    mode = 'verso'
                    if m_v.group(2).strip(): verso_lines.append(m_v.group(2).strip())
                elif mode == 'recto': recto_lines.append(ligne)
                elif mode == 'verso': verso_lines.append(ligne)
            recto = ' '.join(recto_lines).strip()
            verso = ' '.join(verso_lines).strip()
            if recto and verso: cards.append({'recto': recto, 'verso': verso})
    except Exception as e:
        print(f"⚠️ Parsing FC : {e}")
    return cards


# ═══════════════════════════════════════════
# 🏠 PAGES
# ═══════════════════════════════════════════

@app.route('/')
def accueil():
    stats = get_stats_safe()
    return render_template('accueil.html', page_active='accueil', stats=stats,
                           salutation=saluer(), date_actuelle=get_date_fr(),
                           nom_cours=session_data.get('nom_cours'))

@app.route('/bienvenue')
def page_bienvenue():
    return render_template('bienvenue.html')

@app.route('/test')
def test(): return "✅ Flask fonctionne !"

@app.route('/import')
def page_import():
    return render_template('import.html', page_active='import', nom_cours=session_data.get('nom_cours'))

@app.route('/chat')
def page_chat():
    return render_template('chat.html', page_active='chat', nom_cours=session_data.get('nom_cours'))

@app.route('/resume')
def page_resume():
    return render_template('resume.html', page_active='resume',
                           cours_actuel=session_data.get('nom_cours'),
                           matiere=session_data.get('matiere_detectee'),
                           nom_cours=session_data.get('nom_cours'))

@app.route('/explication')
def page_explication():
    return render_template('explication.html', page_active='explication',
                           cours_actuel=session_data.get('nom_cours'),
                           nom_cours=session_data.get('nom_cours'))

@app.route('/qcm')
def page_qcm():
    return render_template('qcm.html', page_active='qcm', nom_cours=session_data.get('nom_cours'))

@app.route('/questions')
def page_questions():
    return render_template('questions.html', page_active='questions', nom_cours=session_data.get('nom_cours'))

@app.route('/examen')
def page_examen():
    return render_template('examen.html', page_active='examen', nom_cours=session_data.get('nom_cours'))

@app.route('/aide')
def page_aide():
    return render_template('aide.html', page_active='aide', nom_cours=session_data.get('nom_cours'))

@app.route('/bibliotheque')
def page_bibliotheque():
    return render_template('bibliotheque.html', page_active='bibliotheque', nom_cours=session_data.get('nom_cours'))

@app.route('/historique')
def page_historique():
    return render_template('historique.html', page_active='historique', nom_cours=session_data.get('nom_cours'))

@app.route('/recherche')
def page_recherche():
    return render_template('recherche.html', page_active='recherche', nom_cours=session_data.get('nom_cours'))

@app.route('/notes')
def page_notes():
    return render_template('notes.html', page_active='notes', nom_cours=session_data.get('nom_cours'))

@app.route('/flashcards')
def page_flashcards():
    return render_template('flashcards.html', page_active='flashcards', nom_cours=session_data.get('nom_cours'))

@app.route('/pomodoro')
def page_pomodoro():
    return render_template('pomodoro.html', page_active='pomodoro', nom_cours=session_data.get('nom_cours'))

@app.route('/audio')
def page_audio():
    return render_template('audio.html', page_active='audio', nom_cours=session_data.get('nom_cours'))

@app.route('/planificateur')
def page_planificateur():
    return render_template('planificateur.html', page_active='planificateur', nom_cours=session_data.get('nom_cours'))

@app.route('/graphiques')
def page_graphiques():
    return render_template('graphiques.html', page_active='graphiques', nom_cours=session_data.get('nom_cours'))


# ═══════════════════════════════════════════
# 🔌 APIs DE BASE
# ═══════════════════════════════════════════

@app.route('/api/statut-cours')
def api_statut_cours():
    cours = session_data.get('cours_actuel', '')
    nom = session_data.get('nom_cours', 'Aucun cours chargé')
    return jsonify({"cours_charge": bool(cours and nom != 'Aucun cours chargé'),
                    "nom_cours": nom, "matiere": session_data.get('matiere_detectee', '')})


@app.route('/api/import', methods=['POST'])
def api_import():
    try:
        if 'fichier' not in request.files:
            return jsonify({"succes": False, "erreur": "Aucun fichier"})
        fichier = request.files['fichier']
        if fichier.filename == '':
            return jsonify({"succes": False, "erreur": "Nom vide"})
        dossier = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
        os.makedirs(dossier, exist_ok=True)
        chemin = os.path.join(dossier, fichier.filename)
        fichier.save(chemin)
        from document_parser import lire_document
        contenu = lire_document(chemin)
        matiere = ""
        try:
            from intelligence import detecter_matiere
            info = detecter_matiere(contenu)
            matiere = f"{info.get('emoji_matiere','📚')} {info.get('matiere','Général')}"
        except Exception:
            matiere = "📚 Général"
        try: db.sauvegarder_cours(fichier.filename, contenu, matiere)
        except Exception as e: print(f"⚠️ DB : {e}")
        session_data['cours_actuel'] = contenu
        session_data['nom_cours'] = fichier.filename
        session_data['matiere_detectee'] = matiere
        return jsonify({"succes": True, "nom": fichier.filename, "matiere": matiere, "apercu": contenu[:3000]})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data = request.get_json()
        q = data.get('question', '').strip()
        if not q: return jsonify({"succes": False, "erreur": "Question vide"})
        from ia_handler import demander_ia
        rep = demander_ia(q)
        try: db.sauvegarder_historique("question_libre", q, rep)
        except Exception: pass
        return jsonify({"succes": True, "reponse": rep})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


@app.route('/api/resume', methods=['POST'])
def api_resume():
    try:
        cours = session_data.get('cours_actuel', '')
        if not cours: return jsonify({"succes": False, "erreur": "Aucun cours chargé"})
        from ia_handler import creer_resume
        r = creer_resume(cours[:5000])
        try: db.sauvegarder_historique("resume", session_data.get('nom_cours'), r)
        except Exception: pass
        return jsonify({"succes": True, "resume": r})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


@app.route('/api/explication', methods=['POST'])
def api_explication():
    try:
        cours = session_data.get('cours_actuel', '')
        if not cours: return jsonify({"succes": False, "erreur": "Aucun cours chargé"})
        from ia_handler import expliquer_simplement
        e_ = expliquer_simplement(cours[:5000])
        try: db.sauvegarder_historique("explication", session_data.get('nom_cours'), e_)
        except Exception: pass
        return jsonify({"succes": True, "explication": e_})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


@app.route('/api/qcm', methods=['POST'])
def api_qcm():
    try:
        cours = session_data.get('cours_actuel', '')
        if not cours: return jsonify({"succes": False, "erreur": "Aucun cours chargé"})
        nombre = max(3, min(20, int(request.get_json().get('nombre', 5))))
        prompt = f"""Tu es un professeur. Génère exactement {nombre} QCM.

Format OBLIGATOIRE :

QCM N°1
Question : [question]
A) [A]
B) [B]
C) [C]
D) [D]
Bonne réponse : [lettre) texte]
Explication : [explication]

Cours :
{cours[:4000]}

Génère :"""
        from ia_handler import demander_ia_brut
        texte = demander_ia_brut(prompt)
        parse = parser_qcm(texte)
        try: db.sauvegarder_historique("qcm", session_data.get('nom_cours'), texte)
        except Exception: pass
        return jsonify({"succes": True, "qcm": texte, "qcm_parse": parse, "nombre": nombre})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


@app.route('/api/questions', methods=['POST'])
def api_questions():
    try:
        cours = session_data.get('cours_actuel', '')
        if not cours: return jsonify({"succes": False, "erreur": "Aucun cours chargé"})
        nombre = max(3, min(15, int(request.get_json().get('nombre', 5))))
        prompt = f"""Tu es un professeur. Génère {nombre} questions ouvertes.

Format :

Question 1
[question]
Réponse : [réponse détaillée]

Cours :
{cours[:4000]}"""
        from ia_handler import demander_ia_brut
        texte = demander_ia_brut(prompt)
        parse = parser_questions(texte)
        try: db.sauvegarder_historique("questions", session_data.get('nom_cours'), texte)
        except Exception: pass
        return jsonify({"succes": True, "texte": texte, "parse": parse, "nombre": nombre})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


@app.route('/api/examen', methods=['POST'])
def api_examen():
    try:
        cours = session_data.get('cours_actuel', '')
        if not cours: return jsonify({"succes": False, "erreur": "Aucun cours chargé"})
        data = request.get_json()
        nombre = max(1, min(10, int(data.get('nombre', 3))))
        niveau = data.get('niveau', 'moyen')
        ntxt = {'facile':'FACILE','moyen':'MOYEN','difficile':'DIFFICILE'}.get(niveau,'MOYEN')
        prompt = f"""Génère {nombre} exercices type EXAMEN ({ntxt}).

═══════════════════════════════
📝 EXERCICE N°1
═══════════════════════════════
ÉNONCÉ : [énoncé]
QUESTIONS :
1) [Q]
─────────────────────────────
✅ CORRIGÉ :
─────────────────────────────
1) [Réponse]
💡 POINTS CLÉS : [points]

Cours :
{cours[:4000]}"""
        from ia_handler import demander_ia_brut
        texte = demander_ia_brut(prompt)
        try: db.sauvegarder_historique("examen", session_data.get('nom_cours'), texte)
        except Exception: pass
        return jsonify({"succes": True, "texte": texte, "nombre": nombre, "niveau": niveau})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


# ═══════════════════════════════════════════
# 📚 APIs BIBLIOTHÈQUE
# ═══════════════════════════════════════════

@app.route('/api/cours/liste')
def api_cours_liste():
    try:
        from db.cours import lister_cours
        cours = lister_cours()
        return jsonify({"succes": True, "cours":[{"id":c[0],"nom":c[1],"matiere":c[2],"date_import":c[3]} for c in cours]})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e), "cours": []})

@app.route('/api/cours/charger/<int:id_cours>', methods=['POST'])
def api_cours_charger(id_cours):
    try:
        from db.cours import info_cours
        info = info_cours(id_cours)
        if not info: return jsonify({"succes": False, "erreur": "Cours introuvable"})
        session_data['cours_actuel'] = info.get('contenu', '')
        session_data['nom_cours'] = info.get('nom', '')
        session_data['matiere_detectee'] = info.get('matiere', '')
        return jsonify({"succes": True, "nom": info.get('nom', '')})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})

@app.route('/api/cours/supprimer/<int:id_cours>', methods=['DELETE'])
def api_cours_supprimer(id_cours):
    try:
        from db.cours import supprimer_cours
        supprimer_cours(id_cours)
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


# ═══════════════════════════════════════════
# 📜 APIs HISTORIQUE
# ═══════════════════════════════════════════

@app.route('/api/historique/liste')
def api_historique_liste():
    try:
        from db.historique import lister_historique_complet
        items = lister_historique_complet(200)
        return jsonify({"succes": True, "items":[{"id":i[0],"type":i[1],"question":i[2] or '',"reponse":i[3] or '',"matiere":i[4] or '',"date":i[5] or ''} for i in items]})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e), "items": []})

@app.route('/api/historique/supprimer/<int:id_h>', methods=['DELETE'])
def api_historique_supprimer(id_h):
    try:
        from db.historique import supprimer_historique
        supprimer_historique(id_h)
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})

@app.route('/api/historique/vider', methods=['DELETE'])
def api_historique_vider():
    try:
        from db.historique import vider_historique
        vider_historique()
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


# ═══════════════════════════════════════════
# 🔍 RECHERCHE
# ═══════════════════════════════════════════

@app.route('/api/recherche', methods=['POST'])
def api_recherche():
    try:
        mot = (request.get_json().get('mot') or '').strip()
        if not mot: return jsonify({"succes": False, "erreur": "Mot-clé vide"})
        from db.cours import rechercher_dans_cours
        res = rechercher_dans_cours(mot)
        return jsonify({"succes": True, "resultats":[{"id":r[0],"nom":r[1],"matiere":r[2],"extrait":r[3],"nb_occurrences":r[4],"date_import":r[5]} for r in res]})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e), "resultats": []})


# ═══════════════════════════════════════════
# ✍️ NOTES
# ═══════════════════════════════════════════

@app.route('/api/notes/liste')
def api_notes_liste():
    try:
        from db.notes import lister_notes
        notes = lister_notes()
        return jsonify({"succes": True, "notes":[{"id":n[0],"titre":n[1],"contenu":n[2],"matiere":n[3],"couleur":n[4],"date_creation":n[5],"date_modification":n[6]} for n in notes]})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e), "notes": []})

@app.route('/api/notes/creer', methods=['POST'])
def api_notes_creer():
    try:
        d = request.get_json()
        from db.notes import creer_note
        id_n = creer_note(titre=d.get('titre',''), contenu=d.get('contenu',''),
                          matiere=d.get('matiere','Général'), couleur=d.get('couleur','#FFE66D'))
        return jsonify({"succes": True, "id": id_n})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})

@app.route('/api/notes/modifier/<int:id_n>', methods=['POST'])
def api_notes_modifier(id_n):
    try:
        d = request.get_json()
        from db.notes import modifier_note
        modifier_note(id_note=id_n, titre=d.get('titre',''), contenu=d.get('contenu',''),
                      matiere=d.get('matiere','Général'), couleur=d.get('couleur','#FFE66D'))
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})

@app.route('/api/notes/supprimer/<int:id_n>', methods=['DELETE'])
def api_notes_supprimer(id_n):
    try:
        from db.notes import supprimer_note
        supprimer_note(id_n)
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


# ═══════════════════════════════════════════
# 🃏 FLASHCARDS
# ═══════════════════════════════════════════

@app.route('/api/flashcards/generer', methods=['POST'])
def api_flashcards_generer():
    try:
        cours = session_data.get('cours_actuel', '')
        if not cours: return jsonify({"succes": False, "erreur": "Aucun cours chargé"})
        nombre = max(5, min(30, int(request.get_json().get('nombre', 10))))
        prompt = f"""Génère {nombre} flashcards (recto/verso).

Format STRICT :

Flashcard N°1
Recto : [question/concept]
Verso : [réponse claire]

Cours :
{cours[:4000]}"""
        from ia_handler import demander_ia_brut
        texte = demander_ia_brut(prompt)
        cards = parser_flashcards(texte)
        if not cards: return jsonify({"succes": False, "erreur": "Aucune flashcard générée"})
        from db.flashcards import creer_flashcards_bulk
        nom = session_data.get('nom_cours','Deck').replace('.pdf','').replace('.docx','').replace('.pptx','')[:40]
        mat = session_data.get('matiere_detectee','📚 Général')
        nb = creer_flashcards_bulk(cards, mat, nom)
        try: db.sauvegarder_historique("flashcards", session_data.get('nom_cours'), f"{nb} flashcards")
        except Exception: pass
        return jsonify({"succes": True, "nb": nb, "deck": nom})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})

@app.route('/api/flashcards/decks')
def api_flashcards_decks():
    try:
        from db.flashcards import lister_decks
        return jsonify({"succes": True, "decks":[{"nom":d[0],"matiere":d[1],"nb":d[2],"reussis":d[3],"vus":d[4]} for d in lister_decks()]})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e), "decks": []})

@app.route('/api/flashcards/deck/<nom_deck>')
def api_flashcards_deck(nom_deck):
    try:
        from db.flashcards import lister_flashcards
        cards = lister_flashcards(nom_deck=nom_deck)
        return jsonify({"succes": True, "cards":[{"id":c[0],"recto":c[1],"verso":c[2]} for c in cards]})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e), "cards": []})

@app.route('/api/flashcards/stats', methods=['POST'])
def api_flashcards_stats_route():
    try:
        d = request.get_json()
        from db.flashcards import maj_flashcard_stats
        maj_flashcard_stats(int(d.get('id')), bool(d.get('reussi')))
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})

@app.route('/api/flashcards/deck/supprimer', methods=['POST'])
def api_flashcards_deck_sup():
    try:
        from db.flashcards import supprimer_deck
        supprimer_deck(request.get_json().get('nom',''))
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


# ═══════════════════════════════════════════
# ⏱️ POMODORO
# ═══════════════════════════════════════════

@app.route('/api/pomodoro/session', methods=['POST'])
def api_pomodoro_session():
    try:
        d = request.get_json()
        from db.pomodoro import enregistrer_session_pomodoro
        enregistrer_session_pomodoro(int(d.get('duree', 25)), d.get('type','travail'), d.get('matiere','Général'))
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})

@app.route('/api/pomodoro/stats')
def api_pomodoro_stats():
    try:
        from db.pomodoro import get_stats_pomodoro
        return jsonify({"succes": True, "stats": get_stats_pomodoro()})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e), "stats": {}})

@app.route('/api/pomodoro/sessions')
def api_pomodoro_sessions():
    try:
        from db.pomodoro import lister_sessions_pomodoro
        sess = lister_sessions_pomodoro(30)
        return jsonify({"succes": True, "sessions":[{"id":s[0],"duree":s[1],"completed":s[2],"matiere":s[3] or 'Général',"date":s[4] or ''} for s in sess]})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e), "sessions": []})


# ═══════════════════════════════════════════
# 🎧 AUDIO
# ═══════════════════════════════════════════

@app.route('/api/audio/generer', methods=['POST'])
def api_audio_generer():
    try:
        cours = session_data.get('cours_actuel', '')
        if not cours: return jsonify({"succes": False, "erreur": "Aucun cours chargé"})
        data = request.get_json()
        voix = data.get('voix', 'femme')
        type_c = data.get('type_contenu', 'cours')

        # Choisir le texte selon type
        if type_c == 'resume':
            from ia_handler import creer_resume
            texte = creer_resume(cours[:4000])
        elif type_c == 'explication':
            from ia_handler import expliquer_simplement
            texte = expliquer_simplement(cours[:4000])
        else:
            texte = cours[:4000]

        # Générer audio
        from audio_generator import generer_audio
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        nom_fic = f"audio_{type_c}_{ts}.mp3"
        chemin = generer_audio(texte, nom_fic, voix)
        if not chemin: return jsonify({"succes": False, "erreur": "Erreur génération audio"})

        try: db.sauvegarder_historique("audio", session_data.get('nom_cours'), f"Audio {type_c} - voix {voix}")
        except Exception: pass

        return jsonify({"succes": True, "url": f"/audio_file/{nom_fic}", "nom": nom_fic})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


@app.route('/audio_file/<nom>')
def audio_file(nom):
    dossier = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs')
    return send_from_directory(dossier, nom)


# ═══════════════════════════════════════════
# 📅 PLANIFICATEUR
# ═══════════════════════════════════════════

@app.route('/api/planificateur/taches')
def api_plan_taches():
    try:
        from db.planificateur import lister_taches_jour, lister_taches_semaine, lister_taches_mois
        periode = request.args.get('periode', 'jour')
        if periode == 'jour': taches = lister_taches_jour()
        elif periode == 'semaine': taches = lister_taches_semaine()
        else: taches = lister_taches_mois()
        result = [{"id":t[0],"titre":t[1],"description":t[2],"matiere":t[3],"type_tache":t[4],
                   "priorite":t[5],"date_tache":t[6],"heure_debut":t[7],"duree_minutes":t[8],
                   "statut":t[9],"recurrence":t[10]} for t in taches]
        return jsonify({"succes": True, "taches": result})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e), "taches": []})

@app.route('/api/planificateur/ajouter', methods=['POST'])
def api_plan_ajouter():
    try:
        d = request.get_json()
        from db.planificateur import ajouter_tache
        id_t = ajouter_tache(
            titre=d.get('titre',''), date_tache=d.get('date_tache'),
            heure_debut=d.get('heure_debut','09:00'),
            duree_minutes=int(d.get('duree_minutes', 30)),
            matiere=d.get('matiere','Général'),
            type_tache=d.get('type_tache','reviser'),
            priorite=d.get('priorite','normal'),
            recurrence=d.get('recurrence','aucune')
        )
        return jsonify({"succes": True, "id": id_t})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})

@app.route('/api/planificateur/statut/<int:id_t>', methods=['POST'])
def api_plan_statut(id_t):
    try:
        from db.planificateur import marquer_tache_faite, marquer_tache_a_faire
        if request.get_json().get('statut') == 'faite':
            marquer_tache_faite(id_t)
        else:
            marquer_tache_a_faire(id_t)
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})

@app.route('/api/planificateur/supprimer/<int:id_t>', methods=['DELETE'])
def api_plan_supprimer(id_t):
    try:
        from db.planificateur import supprimer_tache
        supprimer_tache(id_t)
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})

@app.route('/api/planificateur/stats')
def api_plan_stats():
    try:
        from db.planificateur import stats_planning
        return jsonify({"succes": True, "stats": stats_planning()})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e), "stats": {}})


# ═══════════════════════════════════════════
# 📊 GRAPHIQUES
# ═══════════════════════════════════════════

@app.route('/api/graphiques/data')
def api_graphiques_data():
    try:
        from db.graphiques import get_stats_graphiques, get_progression_resume
        return jsonify({"succes": True, "data": get_stats_graphiques(), "resume": get_progression_resume()})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


# ═══════════════════════════════════════════
# 📚 CONTENU COURS (pour traduction)
# ═══════════════════════════════════════════

@app.route('/api/cours/contenu')
def api_cours_contenu():
    cours = session_data.get('cours_actuel', '')
    return jsonify({"succes": bool(cours), "contenu": cours})


# ═══════════════════════════════════════════
# 🌍 TRADUCTION
# ═══════════════════════════════════════════

@app.route('/traduction')
def page_traduction():
    return render_template('traduction.html', page_active='traduction',
                           nom_cours=session_data.get('nom_cours'))


@app.route('/api/traduction', methods=['POST'])
def api_traduction():
    try:
        d = request.get_json()
        texte = (d.get('texte') or '').strip()
        l_source = d.get('langue_source', 'auto')
        l_cible = d.get('langue_cible', 'anglais')

        if not texte:
            return jsonify({"succes": False, "erreur": "Texte vide"})

        if l_source == 'auto':
            instruction_source = "Détecte la langue source automatiquement"
        else:
            instruction_source = f"Le texte est en {l_source}"

        prompt = f"""Tu es un traducteur professionnel expert.
{instruction_source}.
Traduis ce texte vers le {l_cible}.

RÈGLES STRICTES :
- Donne UNIQUEMENT la traduction
- Pas d'explication, pas de commentaire
- Préserve le sens, le ton et la mise en forme
- Si c'est du contenu éducatif, garde la précision technique

TEXTE À TRADUIRE :
{texte[:5000]}

TRADUCTION EN {l_cible.upper()} :"""

        from ia_handler import demander_ia_brut
        traduction = demander_ia_brut(prompt, temperature=0.3)

        try:
            db.sauvegarder_historique("traduction", f"{l_source} → {l_cible}", traduction)
        except Exception:
            pass

        return jsonify({"succes": True, "traduction": traduction.strip()})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


# ═══════════════════════════════════════════
# 📸 OCR (Scanner image)
# ═══════════════════════════════════════════

@app.route('/ocr')
def page_ocr():
    return render_template('ocr.html', page_active='ocr',
                           nom_cours=session_data.get('nom_cours'))


@app.route('/api/ocr', methods=['POST'])
def api_ocr():
    try:
        if 'fichier' not in request.files:
            return jsonify({"succes": False, "erreur": "Aucune image"})
        fichier = request.files['fichier']
        langue = request.form.get('langue', 'fra')
        expliquer_aussi = request.form.get('expliquer', 'false').lower() == 'true'

        dossier = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
        os.makedirs(dossier, exist_ok=True)
        chemin = os.path.join(dossier, 'ocr_temp_' + fichier.filename)
        fichier.save(chemin)

        from ocr_handler import lire_image
        texte = lire_image(chemin, langue)

        explication = ''
        if expliquer_aussi and texte and not texte.startswith('❌') and not texte.startswith('⚠️'):
            try:
                from ia_handler import expliquer_simplement
                explication = expliquer_simplement(texte[:3000])
            except Exception:
                pass

        try:
            db.sauvegarder_historique("ocr", fichier.filename, texte[:500])
        except Exception:
            pass

        # Nettoyer le fichier temp
        try: os.remove(chemin)
        except Exception: pass

        return jsonify({"succes": True, "texte": texte, "explication": explication})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


# ═══════════════════════════════════════════
# 🤝 PARTAGE (export/import .nokirova)
# ═══════════════════════════════════════════

@app.route('/partage')
def page_partage():
    return render_template('partage.html', page_active='partage',
                           nom_cours=session_data.get('nom_cours'))


@app.route('/api/partage/exporter', methods=['POST'])
def api_partage_exporter():
    try:
        import zipfile
        import json
        import io
        from db.cours import info_cours
        from db.base import get_connexion

        d = request.get_json()
        id_cours = int(d.get('id_cours'))
        createur = d.get('createur', 'Anonyme')

        info = info_cours(id_cours)
        if not info:
            return jsonify({"succes": False, "erreur": "Cours introuvable"}), 404

        matiere = info.get('matiere', '')
        conn = get_connexion()
        cur = conn.cursor()

        cur.execute("SELECT titre, contenu, matiere, couleur FROM notes WHERE matiere = ?", (matiere,))
        notes = [{"titre":r[0],"contenu":r[1],"matiere":r[2],"couleur":r[3]} for r in cur.fetchall()]

        cur.execute("SELECT recto, verso, matiere, nom_deck FROM flashcards WHERE matiere = ?", (matiere,))
        flashcards = [{"recto":r[0],"verso":r[1],"matiere":r[2],"deck":r[3]} for r in cur.fetchall()]

        cur.execute("SELECT type, question, reponse, matiere FROM historique WHERE matiere = ?", (matiere,))
        historique = [{"type":r[0],"question":r[1],"reponse":r[2],"matiere":r[3]} for r in cur.fetchall()]
        conn.close()

        data = {
            "version": "1.0",
            "type": "cours_nokirova",
            "createur": createur,
            "date_export": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "cours": {"nom": info["nom"], "matiere": matiere, "contenu": info["contenu"]},
            "notes_liees": notes,
            "flashcards_liees": flashcards,
            "historique_lie": historique,
            "stats": {
                "nb_notes": len(notes), "nb_flashcards": len(flashcards),
                "nb_historique": len(historique),
                "taille_cours": len(info["contenu"]) if info["contenu"] else 0
            }
        }

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("cours.json", json.dumps(data, ensure_ascii=False, indent=2))
        buf.seek(0)

        from flask import send_file
        return send_file(buf, mimetype='application/zip', as_attachment=True,
                         download_name=f'cours_NOKIROVA.nokirova')
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


@app.route('/api/partage/apercu', methods=['POST'])
def api_partage_apercu():
    try:
        import zipfile
        import json

        if 'fichier' not in request.files:
            return jsonify({"succes": False, "erreur": "Aucun fichier"})

        fichier = request.files['fichier']
        with zipfile.ZipFile(fichier, 'r') as zf:
            with zf.open("cours.json") as f:
                data = json.loads(f.read().decode('utf-8'))

        if data.get("type") != "cours_nokirova":
            return jsonify({"succes": False, "erreur": "Format invalide"})

        return jsonify({"succes": True, "data": data})
    except Exception as e:
        return jsonify({"succes": False, "erreur": "Fichier corrompu ou invalide : " + str(e)})


@app.route('/api/partage/importer', methods=['POST'])
def api_partage_importer():
    try:
        from db.base import get_connexion
        from db.notes import creer_note
        from db.flashcards import creer_flashcard

        data = request.get_json().get('data', {})
        cours = data.get('cours', {})
        createur = data.get('createur', 'Inconnu')
        matiere = cours.get('matiere', '📚 Général')
        nom_cours = f"{cours.get('nom','Cours')} [de {createur}]"

        # Cours
        conn = get_connexion()
        cur = conn.cursor()
        cur.execute("INSERT INTO cours (nom, matiere, contenu) VALUES (?, ?, ?)",
                    (nom_cours, matiere, cours.get('contenu', '')))
        conn.commit()
        conn.close()

        # Notes
        nb_notes = 0
        for n in data.get('notes_liees', []):
            try:
                creer_note(n.get('titre','Note'), n.get('contenu',''),
                           n.get('matiere',matiere), n.get('couleur','#FFE66D'))
                nb_notes += 1
            except Exception: pass

        # Flashcards
        nb_fc = 0
        for fc in data.get('flashcards_liees', []):
            try:
                creer_flashcard(fc.get('recto','?'), fc.get('verso','?'),
                                fc.get('matiere',matiere), fc.get('deck','Importé'))
                nb_fc += 1
            except Exception: pass

        # Historique
        nb_hist = 0
        for h in data.get('historique_lie', []):
            try:
                db.sauvegarder_historique(h.get('type','question_libre'),
                                          h.get('question',''), h.get('reponse',''),
                                          h.get('matiere',matiere))
                nb_hist += 1
            except Exception: pass

        return jsonify({"succes": True, "nom": nom_cours, "nb_notes": nb_notes,
                        "nb_fc": nb_fc, "nb_hist": nb_hist})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


# ═══════════════════════════════════════════
# 🖼️ LOGO
# ═══════════════════════════════════════════

@app.route('/logo')
def logo():
    dossier = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
    return send_from_directory(dossier, 'icon-512.png')

# ═══════════════════════════════════════════
# 🎨 PRÉFÉRENCES (THÈMES + SONNERIES)
# ═══════════════════════════════════════════

@app.route('/themes')
def page_themes():
    return render_template('themes.html', page_active='themes',
                           nom_cours=session_data.get('nom_cours'))


@app.route('/sonneries')
def page_sonneries():
    return render_template('sonneries.html', page_active='sonneries',
                           nom_cours=session_data.get('nom_cours'))


@app.route('/api/preferences/get')
def api_pref_get():
    try:
        from db.preferences import charger_preference
        prefs = {
            'mode': charger_preference('mode', 'clair'),
            'theme': charger_preference('theme', 'printemps'),
            'taille': charger_preference('taille', 'normal'),
            'sonnerie': charger_preference('sonnerie', 'bell'),
            'volume': charger_preference('volume', '80'),
        }
        return jsonify({"succes": True, "preferences": prefs})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e), "preferences": {}})


@app.route('/api/preferences/set', methods=['POST'])
def api_pref_set():
    try:
        d = request.get_json()
        from db.preferences import sauvegarder_preference
        sauvegarder_preference(d.get('cle'), str(d.get('valeur', '')))
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


@app.route('/api/preferences/reset', methods=['POST'])
def api_pref_reset():
    try:
        from db.preferences import sauvegarder_preference
        sauvegarder_preference('mode', 'clair')
        sauvegarder_preference('theme', 'printemps')
        sauvegarder_preference('taille', 'normal')
        sauvegarder_preference('sonnerie', 'bell')
        sauvegarder_preference('volume', '80')
        return jsonify({"succes": True})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


# ═══════════════════════════════════════════
# 🔒 PIN SÉCURITÉ
# ═══════════════════════════════════════════

@app.route('/pin')
def page_pin():
    return render_template('pin.html', page_active='pin',
                           nom_cours=session_data.get('nom_cours'))


@app.route('/api/pin/statut')
def api_pin_statut():
    try:
        from db.pin import pin_existe
        return jsonify({"succes": True, "actif": pin_existe()})
    except Exception as e:
        return jsonify({"succes": False, "actif": False, "erreur": str(e)})


@app.route('/api/pin/set', methods=['POST'])
def api_pin_set():
    try:
        pin = (request.get_json().get('pin') or '').strip()
        if len(pin) < 4 or len(pin) > 8 or not pin.isdigit():
            return jsonify({"succes": False, "erreur": "PIN doit être 4-8 chiffres"})
        from db.pin import set_pin
        if set_pin(pin):
            return jsonify({"succes": True})
        return jsonify({"succes": False, "erreur": "Erreur enregistrement"})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


@app.route('/api/pin/changer', methods=['POST'])
def api_pin_changer():
    try:
        d = request.get_json()
        ancien = d.get('ancien', '')
        nouveau = d.get('nouveau', '')
        from db.pin import verifier_pin, set_pin
        if not verifier_pin(ancien):
            return jsonify({"succes": False, "erreur": "Ancien PIN incorrect"})
        if len(nouveau) < 4 or not nouveau.isdigit():
            return jsonify({"succes": False, "erreur": "Nouveau PIN invalide"})
        if set_pin(nouveau):
            return jsonify({"succes": True})
        return jsonify({"succes": False, "erreur": "Erreur"})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


@app.route('/api/pin/supprimer', methods=['POST'])
def api_pin_supprimer():
    try:
        pin = (request.get_json().get('pin') or '').strip()
        from db.pin import verifier_pin, supprimer_pin
        if not verifier_pin(pin):
            return jsonify({"succes": False, "erreur": "PIN incorrect"})
        if supprimer_pin():
            return jsonify({"succes": True})
        return jsonify({"succes": False, "erreur": "Erreur suppression"})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


# ═══════════════════════════════════════════
# 🎬 VIDÉOS RÉVISION (page simple iframe YouTube)
# ═══════════════════════════════════════════

@app.route('/videos')
def page_videos():
    return render_template('videos.html', page_active='videos',
                           nom_cours=session_data.get('nom_cours'))


# ═══════════════════════════════════════════
# 🎵 MES MÉDIAS (fichiers audio générés)
# ═══════════════════════════════════════════

@app.route('/medias')
def page_medias():
    return render_template('medias.html', page_active='medias',
                           nom_cours=session_data.get('nom_cours'))


@app.route('/api/medias/liste')
def api_medias_liste():
    try:
        dossier = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs')
        os.makedirs(dossier, exist_ok=True)
        fichiers = []
        for f in os.listdir(dossier):
            if f.endswith('.mp3') or f.endswith('.wav'):
                chemin = os.path.join(dossier, f)
                taille = round(os.path.getsize(chemin) / 1024, 1)
                date_mod = datetime.fromtimestamp(os.path.getmtime(chemin)).strftime('%d/%m/%Y %H:%M')
                fichiers.append({"nom": f, "taille": taille, "date": date_mod})
        # Tri par date desc
        fichiers.sort(key=lambda x: x['date'], reverse=True)
        return jsonify({"succes": True, "fichiers": fichiers})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e), "fichiers": []})


@app.route('/api/medias/supprimer', methods=['POST'])
def api_medias_supprimer():
    try:
        nom = request.get_json().get('nom', '')
        # Sécurité : pas de path traversal
        nom = os.path.basename(nom)
        dossier = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs')
        chemin = os.path.join(dossier, nom)
        if os.path.exists(chemin):
            os.remove(chemin)
            return jsonify({"succes": True})
        return jsonify({"succes": False, "erreur": "Fichier introuvable"})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})

# ═══════════════════════════════════════════
# 👤 PROFIL COMPLET (API)
# ═══════════════════════════════════════════

@app.route('/profil')
def page_profil_v2():
    stats = get_stats_safe()
    try:
        import profil_manager as pm
        profil = pm.charger_profil()
    except Exception:
        profil = {}
    try:
        titre_niveau = db.get_niveau_titre(stats.get('niveau', 1))
    except Exception:
        titre_niveau = '🌱 Apprenti'
    return render_template('profil.html', page_active='profil',
                           stats=stats, profil=profil,
                           titre_niveau=titre_niveau,
                           nom_cours=session_data.get('nom_cours'))


@app.route('/api/profil/info')
def api_profil_info():
    try:
        stats = get_stats_safe()
        try:
            import profil_manager as pm
            profil = pm.charger_profil()
            # Ajouter URL photo si elle existe
            try:
                photo_path = pm.get_photo_path()
                if photo_path and os.path.exists(photo_path):
                    profil['photo_url'] = '/profil_photo'
            except Exception:
                pass
        except Exception:
            profil = {}
        try:
            from db.pomodoro import get_stats_pomodoro
            pomo = get_stats_pomodoro()
        except Exception:
            pomo = {}
        try:
            badges_raw = db.lister_badges()
            badges = [{"nom":b[0],"desc":b[1],"emoji":b[2],"date":b[3]} for b in badges_raw]
        except Exception:
            badges = []
        return jsonify({"succes": True, "profil": profil, "stats": stats,
                        "pomodoro": pomo, "badges": badges})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


@app.route('/api/profil/save', methods=['POST'])
def api_profil_save():
    try:
        d = request.get_json()
        try:
            import profil_manager as pm
            profil = pm.charger_profil()
            for k in ['nom_complet','email','numero','universite','annee_etude','date_naissance','bio']:
                profil[k] = d.get(k, '')
            if pm.sauvegarder_profil(profil):
                return jsonify({"succes": True})
        except Exception as e:
            return jsonify({"succes": False, "erreur": str(e)})
        return jsonify({"succes": False, "erreur": "profil_manager indisponible"})
    except Exception as e:
        return jsonify({"succes": False, "erreur": str(e)})


@app.route('/profil_photo')
def profil_photo():
    try:
        import profil_manager as pm
        chemin = pm.get_photo_path()
        if chemin and os.path.exists(chemin):
            from flask import send_file
            return send_file(chemin)
    except Exception:
        pass
    return '', 404


# ═══════════════════════════════════════════
# 🚀 LANCEMENT
# ═══════════════════════════════════════════

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print("\n" + "=" * 60)
    print("🌸 NOKIROVA WEB - PHASE 3 COMPLÈTE")
    print(f"🚀 Port : {port}")
    print("=" * 60 + "\n")
    app.run(host='0.0.0.0', port=port, debug=debug)


    @app.route('/api/ocr', methods=['POST'])
    def api_ocr():
        data = request.get_json()
        image_b64 = data.get('image', '')

        # Extraire le base64
        if ',' in image_b64:
            image_b64 = image_b64.split(',')[1]

        # === Option A : Gemini (recommandé, simple) ===
        # import google.generativeai as genai
        # model = genai.GenerativeModel('gemini-1.5-flash')
        # response = model.generate_content([
        #     "Transcris ce texte manuscrit en français :",
        #     {"mime_type": "image/png", "data": image_b64}
        # ])
        # return jsonify({"succes": True, "texte": response.text})

        # === Option B : Tesseract (gratuit, offline) ===
        # import pytesseract
        # from PIL import Image
        # import io, base64
        # image = Image.open(io.BytesIO(base64.b64decode(image_b64)))
        # texte = pytesseract.image_to_string(image, lang='fra')
        # return jsonify({"succes": True, "texte": texte})

        return jsonify({"succes": True, "texte": "Texte de test (implémenter l'OCR)"})