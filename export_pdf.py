# export_pdf.py - PDF DESIGN PRO UNICODE 📄✨
# Version PHASE C3 - Page de garde + Encadrés

from fpdf import FPDF
from datetime import datetime
import os
import re

# ═══════════════════════════════════════════
# 🎨 COULEURS NOKIROVA
# ═══════════════════════════════════════════
VERT_PRINTEMPS  = (126, 211, 33)
VERT_EMERAUDE   = (0, 200, 83)
VERT_CLAIR      = (240, 253, 232)
JAUNE_SOLEIL    = (255, 217, 61)
JAUNE_PALE      = (255, 248, 225)
BLEU_ROYAL      = (41, 98, 255)
BLEU_PALE       = (208, 235, 255)
VIOLET_PREMIUM  = (123, 97, 255)
VIOLET_PALE     = (243, 232, 255)
ORANGE_DORE     = (245, 158, 11)
ORANGE_PALE     = (255, 237, 213)
ROSE_FONCE      = (219, 39, 119)
ROSE_PALE       = (255, 229, 239)
GRIS_TEXTE      = (55, 65, 81)
GRIS_DOUX       = (107, 114, 128)
BLANC           = (255, 255, 255)
NOIR            = (26, 29, 46)

DOSSIER_FONTS = "fonts"
FONT_REGULAR  = os.path.join(DOSSIER_FONTS, "DejaVuSans.ttf")
FONT_BOLD     = os.path.join(DOSSIER_FONTS, "DejaVuSans-Bold.ttf")
FONT_ITALIC   = os.path.join(DOSSIER_FONTS, "DejaVuSans-Oblique.ttf")


# ═══════════════════════════════════════════
# 🔍 DÉTECTION TYPE DE LIGNE
# ═══════════════════════════════════════════
def detecter_type_ligne(ligne: str) -> str:
    ligne_strip = ligne.strip()
    if not ligne_strip:
        return 'vide'
    if len(ligne_strip) > 3 and all(c in '=-_*━═◆◇○●' for c in ligne_strip):
        return 'separateur'
    if ligne_strip.startswith('**') and ligne_strip.endswith('**'):
        contenu = ligne_strip.strip('*').strip()
        if contenu.isupper() and len(contenu) > 3:
            return 'titre1'
        return 'titre2'
    if ligne_strip.isupper() and 3 < len(ligne_strip) < 80:
        lettres = sum(1 for c in ligne_strip if c.isalpha())
        if lettres > 3:
            return 'titre1'
    mots_titres = ['Étape','Etape','Question','QCM','Exercice','Step',
                   'Partie','Chapitre','Section','Réponse','Reponse',
                   'Correction','Solution','Conclusion','Introduction',
                   'Énoncé','Enonce']
    for mot in mots_titres:
        if ligne_strip.startswith(mot):
            return 'titre3'

    # Détection QCM options A/B/C/D
    if re.match(r'^[A-D][)\.]\s+.+', ligne_strip):
        return 'qcm_option'

    # Détection bonne réponse
    if re.match(r'^(bonne\s*réponse|réponse\s*correcte|✅)\s*:', ligne_strip, re.IGNORECASE):
        return 'qcm_reponse'

    # Point important (💡 ou ⚠️ ou 🔑)
    if ligne_strip.startswith(('💡', '⚠️', '🔑', '📌', '🎯')):
        return 'point_important'

    if ligne_strip.startswith(('- ','• ','* ','+ ','► ','▪ ','▸ ')):
        return 'liste'
    if len(ligne_strip) > 2 and ligne_strip[0].isdigit() and ligne_strip[1] in '.):':
        return 'liste_numero'
    return 'normal'


# ═══════════════════════════════════════════
# 🧠 SÉPARATION EXERCICES / CORRECTIONS
# ═══════════════════════════════════════════
def separer_exercices_corrections(contenu: str) -> tuple:
    lignes = contenu.split('\n')
    exercices, corrections = [], []
    debut_correction = ['correction','réponse','reponse','solution','✅','🔒',
                        'bonne réponse','bonne reponse','explication',
                        '[correction','[réponse','[reponse','[solution',
                        'corrigé','corrige']
    debut_exercice = ['qcm n°','qcm n','question n°','question n',
                      'exercice n°','exercice n','énoncé','enonce',
                      '📝 qcm','📚 exercice','❓ question']
    mode = 'exercice'
    exercice_courant, correction_courante = [], []
    numero_exercice = 0

    for ligne in lignes:
        ligne_lower = ligne.lower().strip()
        est_nouvel_exo = any(ligne_lower.startswith(m) for m in debut_exercice)
        est_correction = any(m in ligne_lower for m in debut_correction)

        if est_nouvel_exo and not est_correction:
            if exercice_courant:
                exercices.extend(exercice_courant)
                exercices.append('')
            if correction_courante:
                corrections.extend([f"**═══ CORRECTION {numero_exercice} ═══**",''])
                corrections.extend(correction_courante)
                corrections.append('')
            numero_exercice += 1
            exercice_courant = [ligne]
            correction_courante = []
            mode = 'exercice'
        elif est_correction:
            mode = 'correction'
            correction_courante.append(ligne)
        else:
            if mode == 'exercice':
                exercice_courant.append(ligne)
            else:
                correction_courante.append(ligne)

    if exercice_courant:
        exercices.extend(exercice_courant)
    if correction_courante:
        corrections.extend(['',f"**═══ CORRECTION {numero_exercice} ═══**",''])
        corrections.extend(correction_courante)

    texte_exos = '\n'.join(exercices).strip()
    texte_corr = '\n'.join(corrections).strip()
    return texte_exos, texte_corr, len(texte_corr) > 50


# ═══════════════════════════════════════════
# 📄 CLASSE PDF
# ═══════════════════════════════════════════
class NokirovaPDF(FPDF):
    def __init__(self, est_correction=False, nom_cours='', matiere='', etudiant='Hénoc'):
        super().__init__()
        self.est_correction = est_correction
        self.nom_cours      = nom_cours
        self.matiere        = matiere
        self.etudiant       = etudiant
        self.add_font("DejaVu", "",  FONT_REGULAR)
        self.add_font("DejaVu", "B", FONT_BOLD)
        self.add_font("DejaVu", "I", FONT_ITALIC)

    def header(self):
        if self.est_correction:
            self.set_fill_color(*ROSE_FONCE)
        else:
            self.set_fill_color(*VERT_PRINTEMPS)
        self.rect(0, 0, 210, 38, 'F')

        if self.est_correction:
            self.set_fill_color(*VIOLET_PREMIUM)
        else:
            self.set_fill_color(*JAUNE_SOLEIL)
        self.rect(0, 38, 210, 3, 'F')

        self.set_font("DejaVu", 'B', 26)
        self.set_text_color(*BLANC)
        self.set_y(8)
        self.cell(0, 12, "🌸 NOKIROVA", align='C')

        self.set_font("DejaVu", 'I', 10)
        self.set_y(22)
        if self.est_correction:
            self.cell(0, 6, "✅ CORRIGÉ - Compare tes réponses !", align='C')
        else:
            self.cell(0, 6, "📝 EXERCICES - Essaie seul d'abord ! 💪", align='C')

        self.ln(35)

    def footer(self):
        self.set_y(-20)
        if self.est_correction:
            self.set_fill_color(*ROSE_FONCE)
        else:
            self.set_fill_color(*VERT_PRINTEMPS)
        self.rect(0, self.get_y(), 210, 1, 'F')
        self.ln(4)
        self.set_font("DejaVu", 'I', 8)
        self.set_text_color(*GRIS_DOUX)
        date_str = datetime.now().strftime('%d/%m/%Y à %H:%M')
        type_doc = "Corrigé" if self.est_correction else "Exercices"
        self.cell(0, 5,
            f"🌸 NOKIROVA  •  {type_doc}  •  Page {self.page_no()}  •  {date_str}",
            align='C')

    # ─────────────────────────────────────────
    # 🎨 PAGE DE GARDE PRO
    # ─────────────────────────────────────────
    def page_de_garde(self, titre: str):
        self.add_page()

        # Fond dégradé simulé (rectangles superposés)
        if self.est_correction:
            couleur_top = ROSE_FONCE
            couleur_mid = VIOLET_PREMIUM
        else:
            couleur_top = VERT_PRINTEMPS
            couleur_mid = BLEU_ROYAL

        # Bloc haut coloré
        self.set_fill_color(*couleur_top)
        self.rect(0, 0, 210, 120, 'F')

        # Bloc bas blanc cassé
        self.set_fill_color(250, 250, 255)
        self.rect(0, 120, 210, 177, 'F')

        # Cercle décoratif (simulé avec rectangle arrondi)
        self.set_fill_color(*couleur_mid)
        self.rect(75, 30, 60, 60, 'F')

        # NOKIROVA XXL
        self.set_font("DejaVu", 'B', 42)
        self.set_text_color(*BLANC)
        self.set_y(40)
        self.cell(0, 20, "🌸 NOKIROVA", align='C', ln=True)

        # Sous-titre app
        self.set_font("DejaVu", 'I', 13)
        self.set_text_color(220, 240, 220)
        self.cell(0, 8, "Ton Professeur Intelligent 💎", align='C', ln=True)

        # Séparateur blanc
        self.ln(8)
        self.set_draw_color(*BLANC)
        self.set_line_width(0.5)
        self.line(40, self.get_y(), 170, self.get_y())
        self.ln(10)

        # TYPE DE DOCUMENT
        self.set_font("DejaVu", 'B', 14)
        self.set_text_color(*BLANC)
        if self.est_correction:
            self.cell(0, 8, "✅ DOCUMENT CORRIGÉ", align='C', ln=True)
        else:
            self.cell(0, 8, "📝 DOCUMENT D'ÉTUDE", align='C', ln=True)

        # ─── Carte info (partie blanche) ───
        self.ln(20)

        # Card titre cours
        self.set_fill_color(*VIOLET_PALE)
        self.rect(25, self.get_y(), 160, 28, 'F')
        self.set_fill_color(*VIOLET_PREMIUM)
        self.rect(25, self.get_y(), 5, 28, 'F')

        self.set_xy(38, self.get_y() + 5)
        self.set_font("DejaVu", 'B', 9)
        self.set_text_color(*VIOLET_PREMIUM)
        self.cell(0, 5, "📚 COURS", ln=True)
        self.set_x(38)
        self.set_font("DejaVu", 'B', 13)
        self.set_text_color(*NOIR)
        nom_affiche = titre[:55] + ('...' if len(titre) > 55 else '')
        self.cell(0, 7, nom_affiche, ln=True)

        self.ln(5)

        # Card matière
        self.set_fill_color(*BLEU_PALE)
        self.rect(25, self.get_y(), 75, 22, 'F')
        self.set_fill_color(*BLEU_ROYAL)
        self.rect(25, self.get_y(), 5, 22, 'F')

        self.set_xy(38, self.get_y() + 4)
        self.set_font("DejaVu", 'B', 8)
        self.set_text_color(*BLEU_ROYAL)
        self.cell(0, 4, "🎯 MATIÈRE", ln=True)
        self.set_x(38)
        self.set_font("DejaVu", 'B', 11)
        self.set_text_color(*NOIR)
        mat = (self.matiere or 'Général')[:30]
        self.cell(0, 6, mat, ln=True)

        # Card date
        y_card = self.get_y() - 22
        self.set_fill_color(*ORANGE_PALE)
        self.rect(115, y_card, 75, 22, 'F')
        self.set_fill_color(*ORANGE_DORE)
        self.rect(115, y_card, 5, 22, 'F')

        self.set_xy(128, y_card + 4)
        self.set_font("DejaVu", 'B', 8)
        self.set_text_color(*ORANGE_DORE)
        self.cell(0, 4, "📅 DATE", ln=True)
        self.set_x(128)
        self.set_font("DejaVu", 'B', 11)
        self.set_text_color(*NOIR)
        self.cell(0, 6, datetime.now().strftime('%d/%m/%Y'), ln=True)

        self.ln(10)

        # Card étudiant
        self.set_fill_color(*VERT_CLAIR)
        self.rect(25, self.get_y(), 160, 22, 'F')
        self.set_fill_color(*VERT_EMERAUDE)
        self.rect(25, self.get_y(), 5, 22, 'F')

        self.set_xy(38, self.get_y() + 4)
        self.set_font("DejaVu", 'B', 8)
        self.set_text_color(*VERT_EMERAUDE)
        self.cell(0, 4, "👤 ÉTUDIANT(E)", ln=True)
        self.set_x(38)
        self.set_font("DejaVu", 'B', 12)
        self.set_text_color(*NOIR)
        self.cell(0, 6, self.etudiant or 'NOKIROVA', ln=True)

        self.ln(15)

        # Message motivation
        self.set_font("DejaVu", 'B', 12)
        if self.est_correction:
            self.set_text_color(*ROSE_FONCE)
            self.cell(0, 7, "💡 Compare tes réponses avec ce corrigé !", align='C', ln=True)
        else:
            self.set_text_color(*VERT_EMERAUDE)
            self.cell(0, 7, "💪 Essaie d'abord SEUL avant de regarder le corrigé !", align='C', ln=True)

        self.ln(5)
        self.set_font("DejaVu", 'I', 9)
        self.set_text_color(*GRIS_DOUX)
        self.cell(0, 5, "✨ NOKIROVA - Ton Prof IA Personnel • ICK Bouaké 🇨🇮", align='C', ln=True)


# ═══════════════════════════════════════════
# 📝 FONCTIONS STYLE
# ═══════════════════════════════════════════
def ajouter_titre_principal(pdf, titre, couleur_accent=VIOLET_PREMIUM, couleur_fond=VIOLET_PALE):
    titre_propre = titre.strip() or "Document NOKIROVA"
    pdf.ln(8)
    y = pdf.get_y()
    pdf.set_fill_color(*couleur_fond)
    pdf.rect(15, y, 180, 24, 'F')
    pdf.set_fill_color(*couleur_accent)
    pdf.rect(15, y, 6, 24, 'F')
    pdf.set_xy(28, y + 6)
    pdf.set_font("DejaVu", 'B', 21)
    pdf.set_text_color(*couleur_accent)
    pdf.cell(0, 12, titre_propre)
    pdf.ln(30)


def ajouter_titre_1(pdf, texte):
    texte_propre = texte.strip().strip('*').strip()
    if not texte_propre: return
    pdf.ln(8)
    y = pdf.get_y()
    pdf.set_fill_color(*VERT_CLAIR)
    pdf.rect(15, y, 180, 16, 'F')
    pdf.set_fill_color(*VERT_EMERAUDE)
    pdf.rect(15, y, 6, 16, 'F')
    pdf.set_xy(28, y + 4)
    pdf.set_font("DejaVu", 'B', 16)
    pdf.set_text_color(*VERT_EMERAUDE)
    pdf.cell(0, 8, texte_propre)
    pdf.ln(22)


def ajouter_titre_2(pdf, texte):
    texte_propre = texte.strip().strip('*').strip()
    if not texte_propre: return
    pdf.ln(6)
    pdf.set_font("DejaVu", 'B', 14)
    pdf.set_text_color(*BLEU_ROYAL)
    pdf.cell(0, 8, texte_propre, ln=True)
    y = pdf.get_y()
    pdf.set_draw_color(*BLEU_ROYAL)
    pdf.set_line_width(1)
    pdf.line(15, y, 80, y)
    pdf.set_line_width(0.2)
    pdf.ln(7)


def ajouter_titre_3(pdf, texte):
    texte_propre = texte.strip()
    if not texte_propre: return
    pdf.ln(5)
    pdf.set_font("DejaVu", 'B', 12)
    pdf.set_text_color(*ORANGE_DORE)
    try: pdf.multi_cell(0, 7, texte_propre)
    except Exception: pass
    pdf.ln(3)


def ajouter_paragraphe(pdf, texte):
    texte_propre = texte.strip()
    if not texte_propre: return
    pdf.set_font("DejaVu", '', 11)
    pdf.set_text_color(*GRIS_TEXTE)
    pdf.set_x(22)
    try: pdf.multi_cell(168, 7, texte_propre)
    except Exception: pass
    pdf.ln(3)


def ajouter_liste(pdf, texte):
    texte_propre = texte.strip()
    if not texte_propre: return
    for p in ['- ','• ','* ','+ ','► ','▪ ','▸ ']:
        if texte_propre.startswith(p):
            texte_propre = texte_propre[len(p):]
            break
    if not texte_propre: return
    pdf.set_x(25)
    pdf.set_font("DejaVu", 'B', 13)
    pdf.set_text_color(*VERT_EMERAUDE)
    pdf.cell(7, 7, "●")
    pdf.set_font("DejaVu", '', 11)
    pdf.set_text_color(*GRIS_TEXTE)
    try: pdf.multi_cell(160, 7, texte_propre)
    except Exception: pass
    pdf.ln(2)


def ajouter_liste_numero(pdf, texte):
    texte_propre = texte.strip()
    if not texte_propre: return
    pdf.set_x(22)
    match = re.match(r'^(\d+)[.):]', texte_propre)
    if match:
        numero = match.group(1)
        reste = texte_propre[len(match.group(0)):].strip()
        pdf.set_font("DejaVu", 'B', 12)
        pdf.set_text_color(*ORANGE_DORE)
        pdf.cell(12, 7, f"{numero}.")
        pdf.set_font("DejaVu", '', 11)
        pdf.set_text_color(*GRIS_TEXTE)
        try: pdf.multi_cell(160, 7, reste)
        except Exception: pass
    else:
        ajouter_paragraphe(pdf, texte_propre)
    pdf.ln(2)


def ajouter_qcm_option(pdf, texte):
    """Option QCM stylée (A/B/C/D)"""
    texte_propre = texte.strip()
    if not texte_propre: return
    match = re.match(r'^([A-D])[)\.]\s*(.+)', texte_propre)
    if not match: return

    lettre = match.group(1)
    contenu = match.group(2)

    couleurs_options = {
        'A': BLEU_ROYAL,
        'B': VIOLET_PREMIUM,
        'C': ORANGE_DORE,
        'D': ROSE_FONCE,
    }
    couleur = couleurs_options.get(lettre, GRIS_TEXTE)

    pdf.set_x(28)
    y = pdf.get_y()

    # Cercle lettre
    pdf.set_fill_color(*couleur)
    pdf.rect(28, y, 10, 9, 'F')
    pdf.set_font("DejaVu", 'B', 10)
    pdf.set_text_color(*BLANC)
    pdf.set_xy(28, y + 1)
    pdf.cell(10, 7, lettre, align='C')

    # Texte option
    pdf.set_font("DejaVu", '', 11)
    pdf.set_text_color(*GRIS_TEXTE)
    pdf.set_xy(42, y)
    try: pdf.multi_cell(155, 9, contenu)
    except Exception: pass
    pdf.ln(1)


def ajouter_qcm_reponse(pdf, texte):
    """Encadré vert pour la bonne réponse"""
    texte_propre = texte.strip()
    if not texte_propre: return

    pdf.ln(3)
    y = pdf.get_y()
    pdf.set_fill_color(*VERT_CLAIR)
    pdf.rect(20, y, 170, 14, 'F')
    pdf.set_fill_color(*VERT_EMERAUDE)
    pdf.rect(20, y, 5, 14, 'F')
    pdf.set_xy(30, y + 3)
    pdf.set_font("DejaVu", 'B', 11)
    pdf.set_text_color(*VERT_EMERAUDE)
    try: pdf.cell(0, 8, texte_propre)
    except Exception: pass
    pdf.ln(16)


def ajouter_point_important(pdf, texte):
    """Encadré orange pour points importants 💡⚠️🔑"""
    texte_propre = texte.strip()
    if not texte_propre: return

    pdf.ln(3)
    y = pdf.get_y()

    # Fond orange pâle
    pdf.set_fill_color(*ORANGE_PALE)
    pdf.rect(18, y, 174, 16, 'F')
    pdf.set_fill_color(*ORANGE_DORE)
    pdf.rect(18, y, 5, 16, 'F')

    pdf.set_xy(28, y + 4)
    pdf.set_font("DejaVu", 'B', 11)
    pdf.set_text_color(*ORANGE_DORE)
    try: pdf.multi_cell(160, 8, texte_propre)
    except Exception: pass
    pdf.ln(5)


def ajouter_separateur(pdf):
    pdf.ln(8)
    y = pdf.get_y()
    pdf.set_draw_color(*VERT_PRINTEMPS)
    pdf.set_line_width(0.4)
    pdf.line(50, y, 100, y)
    pdf.line(110, y, 160, y)
    pdf.set_font("DejaVu", '', 10)
    pdf.set_text_color(*VERT_PRINTEMPS)
    pdf.set_xy(102, y - 3)
    pdf.cell(6, 6, "✦", align='C')
    pdf.ln(10)


# ═══════════════════════════════════════════
# 📄 GÉNÉRATION PDF
# ═══════════════════════════════════════════
def _generer_pdf(contenu, titre, chemin,
                 est_correction=False,
                 nom_cours='', matiere='', etudiant='Hénoc'):
    try:
        pdf = NokirovaPDF(
            est_correction=est_correction,
            nom_cours=nom_cours,
            matiere=matiere,
            etudiant=etudiant
        )
        pdf.set_margins(15, 43, 15)
        pdf.set_auto_page_break(auto=True, margin=28)

        # ── PAGE DE GARDE ──
        pdf.page_de_garde(titre)

        # ── PAGE CONTENU ──
        pdf.add_page()

        if est_correction:
            ajouter_titre_principal(pdf, titre, ROSE_FONCE, ROSE_PALE)
        else:
            ajouter_titre_principal(pdf, titre, VIOLET_PREMIUM, VIOLET_PALE)

        # Date
        pdf.set_font("DejaVu", 'I', 9)
        pdf.set_text_color(*GRIS_DOUX)
        pdf.cell(0, 5,
            f"📅 Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            align='C', ln=True)
        pdf.ln(4)

        if est_correction:
            pdf.set_font("DejaVu", 'B', 11)
            pdf.set_text_color(*ROSE_FONCE)
            pdf.cell(0, 6, "💡 Compare tes réponses avec ce corrigé !", align='C', ln=True)
        else:
            pdf.set_font("DejaVu", 'B', 11)
            pdf.set_text_color(*VERT_EMERAUDE)
            pdf.cell(0, 6, "💪 Essaie d'abord SEUL avant de regarder le corrigé !", align='C', ln=True)

        pdf.ln(4)
        ajouter_separateur(pdf)

        # ── CONTENU LIGNE PAR LIGNE ──
        for ligne in contenu.split('\n'):
            type_ligne = detecter_type_ligne(ligne)
            try:
                if   type_ligne == 'titre1':         ajouter_titre_1(pdf, ligne)
                elif type_ligne == 'titre2':         ajouter_titre_2(pdf, ligne)
                elif type_ligne == 'titre3':         ajouter_titre_3(pdf, ligne)
                elif type_ligne == 'liste':          ajouter_liste(pdf, ligne)
                elif type_ligne == 'liste_numero':   ajouter_liste_numero(pdf, ligne)
                elif type_ligne == 'qcm_option':     ajouter_qcm_option(pdf, ligne)
                elif type_ligne == 'qcm_reponse':    ajouter_qcm_reponse(pdf, ligne)
                elif type_ligne == 'point_important':ajouter_point_important(pdf, ligne)
                elif type_ligne == 'separateur':     ajouter_separateur(pdf)
                elif type_ligne == 'vide':           pdf.ln(3)
                else:                                ajouter_paragraphe(pdf, ligne)
            except Exception:
                continue

        # Footer motivation
        pdf.ln(12)
        ajouter_separateur(pdf)
        pdf.set_font("DejaVu", 'B', 12)
        if est_correction:
            pdf.set_text_color(*ROSE_FONCE)
            pdf.cell(0, 7, "✅ Bien comparé ? Bravo ! 🌟", align='C', ln=True)
        else:
            pdf.set_text_color(*VERT_EMERAUDE)
            pdf.cell(0, 7, "💪 Bonne chance ! Tu peux le faire ! 🌸", align='C', ln=True)
        pdf.set_font("DejaVu", 'I', 10)
        pdf.set_text_color(*VIOLET_PREMIUM)
        pdf.cell(0, 6, "✨ NOKIROVA - Ton Prof Intelligent ✨", align='C', ln=True)

        pdf.output(chemin)
        return chemin

    except Exception as e:
        return f"❌ Erreur : {e}"


# ═══════════════════════════════════════════
# 🎯 FONCTION PRINCIPALE
# ═══════════════════════════════════════════
def exporter_en_pdf(contenu, titre="Document NOKIROVA",
                    nom_fichier="document.pdf",
                    nom_cours='', matiere='', etudiant='Hénoc'):
    try:
        for font_path in [FONT_REGULAR, FONT_BOLD, FONT_ITALIC]:
            if not os.path.exists(font_path):
                return (f"❌ Police manquante : {font_path}\n"
                        f"💡 Mets les fichiers DejaVu dans NOKIROVA/fonts/")

        os.makedirs("outputs", exist_ok=True)

        texte_exos, texte_corr, contient_corrections = separer_exercices_corrections(contenu)

        if contient_corrections:
            base = nom_fichier.replace('.pdf', '')
            chemin_exos = os.path.join("outputs", f"{base}_EXERCICES.pdf")
            chemin_corr = os.path.join("outputs", f"{base}_CORRECTION.pdf")

            res_e = _generer_pdf(texte_exos, f"📝 {titre} - Exercices",
                                  chemin_exos, False, nom_cours, matiere, etudiant)
            res_c = _generer_pdf(texte_corr, f"✅ {titre} - Corrigé",
                                  chemin_corr, True, nom_cours, matiere, etudiant)

            if "Erreur" in str(res_e) or "Erreur" in str(res_c):
                return "❌ Erreur génération PDF"

            return f"📚 2 PDFs :\n• {chemin_exos}\n• {chemin_corr}"

        else:
            chemin = os.path.join("outputs", nom_fichier)
            return _generer_pdf(contenu, titre, chemin,
                                False, nom_cours, matiere, etudiant)

    except Exception as e:
        return f"❌ Erreur : {e}"


# ═══════════════════════════════════════════
# 🧪 TEST
# ═══════════════════════════════════════════
if __name__ == "__main__":
    contenu_test = """
**EXERCICE 1**
Calcule la TVA à 20% sur 100€.

A) 15€
B) 20€
C) 25€
D) 30€

Bonne réponse : B) 20€

💡 Explication : 100 × 0.20 = 20€

**EXERCICE 2**
Calcule l'intérêt simple : 1000€ à 5% pendant 2 ans.

🔒 [CORRECTION]
✅ Réponse : 100€
💡 Formule : C × t × n = 1000 × 0.05 × 2
"""
    r = exporter_en_pdf(contenu_test, "Comptabilité", "test.pdf",
                        nom_cours="Compta S1",
                        matiere="📊 Comptabilité",
                        etudiant="Hénoc")
    print(r)