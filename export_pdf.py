# export_pdf.py - PDF DESIGN PRO UNICODE 📄✨ (avec séparation Exercices/Corrections)

from fpdf import FPDF
from datetime import datetime
import os
import re

# ═══════════════════════════════════════════
# 🎨 COULEURS NOKIROVA
# ═══════════════════════════════════════════
VERT_PRINTEMPS = (126, 211, 33)
VERT_EMERAUDE = (0, 200, 83)
VERT_CLAIR = (240, 253, 232)

JAUNE_SOLEIL = (255, 217, 61)
JAUNE_PALE = (255, 248, 225)

BLEU_ROYAL = (41, 98, 255)
BLEU_PALE = (208, 235, 255)

VIOLET_PREMIUM = (123, 97, 255)
VIOLET_PALE = (243, 232, 255)

ORANGE_DORE = (245, 158, 11)
ORANGE_PALE = (255, 237, 213)

ROSE_FONCE = (219, 39, 119)
ROSE_PALE = (255, 229, 239)

GRIS_TEXTE = (55, 65, 81)
GRIS_DOUX = (107, 114, 128)
BLANC = (255, 255, 255)

DOSSIER_FONTS = "fonts"
FONT_REGULAR = os.path.join(DOSSIER_FONTS, "DejaVuSans.ttf")
FONT_BOLD = os.path.join(DOSSIER_FONTS, "DejaVuSans-Bold.ttf")
FONT_ITALIC = os.path.join(DOSSIER_FONTS, "DejaVuSans-Oblique.ttf")


# ═══════════════════════════════════════════
# 🔍 DÉTECTION DE TYPE DE LIGNE
# ═══════════════════════════════════════════
def detecter_type_ligne(ligne: str) -> str:
    """Détecte le type d'une ligne"""
    ligne_strip = ligne.strip()

    if not ligne_strip:
        return 'vide'

    # Séparateurs
    if len(ligne_strip) > 3 and all(c in '=-_*━═◆◇○●' for c in ligne_strip):
        return 'separateur'

    # Titres encadrés par **
    if ligne_strip.startswith('**') and ligne_strip.endswith('**'):
        contenu = ligne_strip.strip('*').strip()
        if contenu.isupper() and len(contenu) > 3:
            return 'titre1'
        return 'titre2'

    # Titres MAJUSCULES
    if ligne_strip.isupper() and 3 < len(ligne_strip) < 80:
        lettres = sum(1 for c in ligne_strip if c.isalpha())
        if lettres > 3:
            return 'titre1'

    # Mots-clés titres
    mots_titres = ['Étape', 'Etape', 'Question', 'QCM', 'Exercice', 'Step',
                   'Partie', 'Chapitre', 'Section', 'Réponse', 'Reponse',
                   'Correction', 'Solution', 'Conclusion', 'Introduction',
                   'Énoncé', 'Enonce']
    for mot in mots_titres:
        if ligne_strip.startswith(mot):
            return 'titre3'

    # Listes
    if ligne_strip.startswith(('- ', '• ', '* ', '+ ', '► ', '▪ ', '▸ ')):
        return 'liste'
    if len(ligne_strip) > 2 and ligne_strip[0].isdigit() and ligne_strip[1] in '.):':
        return 'liste_numero'

    return 'normal'


# ═══════════════════════════════════════════
# 🧠 ANALYSEUR INTELLIGENT : Sépare exercices et corrections
# ═══════════════════════════════════════════
def separer_exercices_corrections(contenu: str) -> tuple:
    """
    Analyse le contenu et sépare les exercices des corrections.
    Retourne (texte_exercices, texte_corrections, contient_corrections)
    """
    lignes = contenu.split('\n')
    exercices = []
    corrections = []

    # Mots-clés indiquant qu'on entre dans une correction
    debut_correction = [
        'correction', 'réponse', 'reponse', 'solution', '✅', '🔒',
        'bonne réponse', 'bonne reponse', 'explication',
        '[correction', '[réponse', '[reponse', '[solution',
        'corrigé', 'corrige'
    ]

    # Mots-clés indiquant qu'on entre dans un exercice
    debut_exercice = [
        'qcm n°', 'qcm n', 'question n°', 'question n',
        'exercice n°', 'exercice n', 'énoncé', 'enonce',
        '📝 qcm', '📚 exercice', '❓ question'
    ]

    mode = 'exercice'  # On commence en mode exercice
    exercice_courant_lignes = []
    correction_courante_lignes = []
    numero_exercice = 0

    for ligne in lignes:
        ligne_lower = ligne.lower().strip()

        # Détecter le début d'un nouvel exercice
        est_nouvel_exo = any(ligne_lower.startswith(mot) for mot in debut_exercice)
        # Détecter le début d'une correction
        est_correction = any(mot in ligne_lower for mot in debut_correction)

        if est_nouvel_exo and not est_correction:
            # On sauvegarde l'exercice/correction précédent s'il y en avait
            if exercice_courant_lignes:
                exercices.extend(exercice_courant_lignes)
                exercices.append('')
            if correction_courante_lignes:
                corrections.extend([f"**═══ CORRECTION DE L'EXERCICE {numero_exercice} ═══**", ''])
                corrections.extend(correction_courante_lignes)
                corrections.append('')

            # Nouvel exercice
            numero_exercice += 1
            exercice_courant_lignes = [ligne]
            correction_courante_lignes = []
            mode = 'exercice'

        elif est_correction:
            mode = 'correction'
            correction_courante_lignes.append(ligne)

        else:
            if mode == 'exercice':
                exercice_courant_lignes.append(ligne)
            else:
                correction_courante_lignes.append(ligne)

    # Sauvegarder le dernier exercice/correction
    if exercice_courant_lignes:
        exercices.extend(exercice_courant_lignes)
    if correction_courante_lignes:
        corrections.extend(['', f"**═══ CORRECTION DE L'EXERCICE {numero_exercice} ═══**", ''])
        corrections.extend(correction_courante_lignes)

    texte_exercices = '\n'.join(exercices).strip()
    texte_corrections = '\n'.join(corrections).strip()

    contient_corrections = len(texte_corrections) > 50

    return texte_exercices, texte_corrections, contient_corrections


# ═══════════════════════════════════════════
# 📄 CLASSE PDF
# ═══════════════════════════════════════════
class NokirovaPDF(FPDF):
    def __init__(self, est_correction=False):
        super().__init__()
        self.est_correction = est_correction
        self.add_font("DejaVu", "", FONT_REGULAR)
        self.add_font("DejaVu", "B", FONT_BOLD)
        self.add_font("DejaVu", "I", FONT_ITALIC)

    def header(self):
        """En-tête élégant"""
        if self.est_correction:
            # Header rose pour corrections
            self.set_fill_color(*ROSE_FONCE)
        else:
            # Header vert pour exercices
            self.set_fill_color(*VERT_PRINTEMPS)

        self.rect(0, 0, 210, 38, 'F')

        # Bande décorative
        if self.est_correction:
            self.set_fill_color(*VIOLET_PREMIUM)
        else:
            self.set_fill_color(*JAUNE_SOLEIL)
        self.rect(0, 38, 210, 3, 'F')

        # Logo
        self.set_font("DejaVu", 'B', 26)
        self.set_text_color(*BLANC)
        self.set_y(8)
        self.cell(0, 12, "🌸 NOKIROVA", align='C')

        # Sous-titre
        self.set_font("DejaVu", 'I', 10)
        self.set_y(22)
        if self.est_correction:
            self.cell(0, 6, "✅ CORRIGÉ - À consulter après avoir essayé ! ✅", align='C')
        else:
            self.cell(0, 6, "📝 EXERCICES - Essaie d'abord par toi-même ! 💪", align='C')

        self.ln(35)

    def footer(self):
        """Pied de page"""
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
        self.cell(0, 5, f"🌸 NOKIROVA  •  {type_doc}  •  Page {self.page_no()}  •  Généré le {date_str}", align='C')


# ═══════════════════════════════════════════
# 📝 FONCTIONS DE STYLE (TRÈS AÉRÉES)
# ═══════════════════════════════════════════
def ajouter_titre_principal(pdf, titre: str, couleur_accent=VIOLET_PREMIUM, couleur_fond=VIOLET_PALE):
    """Grand titre du document"""
    titre_propre = titre.strip()
    if not titre_propre:
        titre_propre = "Document NOKIROVA"

    pdf.ln(8)
    y_debut = pdf.get_y()

    pdf.set_fill_color(*couleur_fond)
    pdf.rect(15, y_debut, 180, 24, 'F')

    pdf.set_fill_color(*couleur_accent)
    pdf.rect(15, y_debut, 6, 24, 'F')

    pdf.set_xy(28, y_debut + 6)
    pdf.set_font("DejaVu", 'B', 21)
    pdf.set_text_color(*couleur_accent)
    pdf.cell(0, 12, titre_propre)

    pdf.ln(30)  # ESPACE AÉRÉ


def ajouter_titre_1(pdf, texte: str):
    """Grand titre de section - TRÈS AÉRÉ"""
    texte_propre = texte.strip().strip('*').strip()
    if not texte_propre:
        return

    pdf.ln(8)  # GROS espace avant
    y_debut = pdf.get_y()

    pdf.set_fill_color(*VERT_CLAIR)
    pdf.rect(15, y_debut, 180, 16, 'F')

    pdf.set_fill_color(*VERT_EMERAUDE)
    pdf.rect(15, y_debut, 6, 16, 'F')

    pdf.set_xy(28, y_debut + 4)
    pdf.set_font("DejaVu", 'B', 16)
    pdf.set_text_color(*VERT_EMERAUDE)
    pdf.cell(0, 8, texte_propre)

    pdf.ln(22)  # GROS espace après


def ajouter_titre_2(pdf, texte: str):
    """Sous-titre avec soulignement"""
    texte_propre = texte.strip().strip('*').strip()
    if not texte_propre:
        return

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


def ajouter_titre_3(pdf, texte: str):
    """Mini-titre orange"""
    texte_propre = texte.strip()
    if not texte_propre:
        return

    pdf.ln(5)
    pdf.set_font("DejaVu", 'B', 12)
    pdf.set_text_color(*ORANGE_DORE)
    try:
        pdf.multi_cell(0, 7, texte_propre)
    except Exception:
        pass
    pdf.ln(3)


def ajouter_paragraphe(pdf, texte: str):
    """Paragraphe TRÈS AÉRÉ avec interligne large"""
    texte_propre = texte.strip()
    if not texte_propre:
        return

    pdf.set_font("DejaVu", '', 11)
    pdf.set_text_color(*GRIS_TEXTE)
    pdf.set_x(22)
    try:
        pdf.multi_cell(168, 7, texte_propre)  # Interligne 7 au lieu de 6
    except Exception:
        pass
    pdf.ln(3)  # Plus d'espace entre paragraphes


def ajouter_liste(pdf, texte: str):
    """Élément de liste avec puce verte + AÉRÉ"""
    texte_propre = texte.strip()
    if not texte_propre:
        return

    for prefixe in ['- ', '• ', '* ', '+ ', '► ', '▪ ', '▸ ']:
        if texte_propre.startswith(prefixe):
            texte_propre = texte_propre[len(prefixe):]
            break

    if not texte_propre:
        return

    pdf.set_x(25)

    pdf.set_font("DejaVu", 'B', 13)
    pdf.set_text_color(*VERT_EMERAUDE)
    pdf.cell(7, 7, "●")

    pdf.set_font("DejaVu", '', 11)
    pdf.set_text_color(*GRIS_TEXTE)
    try:
        pdf.multi_cell(160, 7, texte_propre)
    except Exception:
        pass
    pdf.ln(2)


def ajouter_liste_numero(pdf, texte: str):
    """Liste numérotée AÉRÉE"""
    texte_propre = texte.strip()
    if not texte_propre:
        return

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
        try:
            pdf.multi_cell(160, 7, reste)
        except Exception:
            pass
    else:
        ajouter_paragraphe(pdf, texte_propre)
    pdf.ln(2)


def ajouter_separateur(pdf):
    """Séparateur décoratif AÉRÉ"""
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
# 📄 FONCTION GÉNÉRIQUE DE GÉNÉRATION PDF
# ═══════════════════════════════════════════
def _generer_pdf(contenu: str, titre: str, chemin: str, est_correction: bool = False) -> str:
    """Génère un PDF stylé à partir d'un contenu"""
    try:
        pdf = NokirovaPDF(est_correction=est_correction)
        pdf.set_margins(15, 43, 15)
        pdf.set_auto_page_break(auto=True, margin=28)
        pdf.add_page()

        # Titre principal (couleur différente pour correction)
        if est_correction:
            ajouter_titre_principal(pdf, titre, ROSE_FONCE, ROSE_PALE)
        else:
            ajouter_titre_principal(pdf, titre, VIOLET_PREMIUM, VIOLET_PALE)

        # Date
        pdf.set_font("DejaVu", 'I', 9)
        pdf.set_text_color(*GRIS_DOUX)
        date_str = datetime.now().strftime('%d/%m/%Y à %H:%M')
        pdf.cell(0, 5, f"📅 Document généré le {date_str}", align='C', ln=True)
        pdf.ln(6)

        # Message d'instruction
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

        # Contenu ligne par ligne
        lignes = contenu.split('\n')
        for ligne in lignes:
            type_ligne = detecter_type_ligne(ligne)

            try:
                if type_ligne == 'titre1':
                    ajouter_titre_1(pdf, ligne)
                elif type_ligne == 'titre2':
                    ajouter_titre_2(pdf, ligne)
                elif type_ligne == 'titre3':
                    ajouter_titre_3(pdf, ligne)
                elif type_ligne == 'liste':
                    ajouter_liste(pdf, ligne)
                elif type_ligne == 'liste_numero':
                    ajouter_liste_numero(pdf, ligne)
                elif type_ligne == 'separateur':
                    ajouter_separateur(pdf)
                elif type_ligne == 'vide':
                    pdf.ln(3)
                else:
                    ajouter_paragraphe(pdf, ligne)
            except Exception:
                continue

        # Footer décoratif
        pdf.ln(12)
        ajouter_separateur(pdf)

        pdf.set_font("DejaVu", 'B', 12)
        if est_correction:
            pdf.set_text_color(*ROSE_FONCE)
            pdf.cell(0, 7, "✅ Bien comparé tes réponses ? Bravo ! 🌟", align='C', ln=True)
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
# 🎯 FONCTION PRINCIPALE (EXPORT INTELLIGENT)
# ═══════════════════════════════════════════
def exporter_en_pdf(contenu: str, titre: str = "Document NOKIROVA", nom_fichier: str = "document.pdf") -> str:
    """
    Exporte un contenu en PDF.
    Si le contenu contient des corrections, génère 2 PDFs :
    - Un PDF avec les exercices seulement
    - Un PDF avec les corrections
    """
    try:
        # Vérifier les polices
        for font_path in [FONT_REGULAR, FONT_BOLD, FONT_ITALIC]:
            if not os.path.exists(font_path):
                return (
                    f"❌ Police manquante : {font_path}\n\n"
                    f"💡 Solution :\n"
                    f"1. Télécharge DejaVu Fonts\n"
                    f"2. Mets DejaVuSans.ttf, DejaVuSans-Bold.ttf, DejaVuSans-Oblique.ttf\n"
                    f"   dans le dossier NOKIROVA/fonts/"
                )

        os.makedirs("outputs", exist_ok=True)

        # Analyser le contenu : exercices ou pas ?
        texte_exos, texte_corr, contient_corrections = separer_exercices_corrections(contenu)

        # ═══ CAS 1 : Le contenu contient des exercices ET des corrections ═══
        if contient_corrections:
            # Nom de base sans extension
            base_nom = nom_fichier.replace('.pdf', '')

            chemin_exos = os.path.join("outputs", f"{base_nom}_EXERCICES.pdf")
            chemin_corr = os.path.join("outputs", f"{base_nom}_CORRECTION.pdf")

            # Générer PDF exercices
            res_exos = _generer_pdf(
                texte_exos,
                f"📝 {titre} - Exercices",
                chemin_exos,
                est_correction=False
            )

            # Générer PDF corrections
            res_corr = _generer_pdf(
                texte_corr,
                f"✅ {titre} - Corrigé",
                chemin_corr,
                est_correction=True
            )

            if "Erreur" in res_exos or "Erreur" in res_corr:
                return f"❌ Erreur lors de la génération"

            # Retourner les 2 chemins
            return f"📚 2 PDFs créés :\n• Exercices : {chemin_exos}\n• Corrigé : {chemin_corr}"

        # ═══ CAS 2 : Contenu simple (résumé, explication, etc.) ═══
        else:
            chemin = os.path.join("outputs", nom_fichier)
            return _generer_pdf(contenu, titre, chemin, est_correction=False)

    except Exception as e:
        return f"❌ Erreur : {e}"


# ═══════════════════════════════════════════
# 🧪 TEST
# ═══════════════════════════════════════════
if __name__ == "__main__":
    contenu_test = """
**EXERCICE 1**

Calcule la TVA d'un produit à 100€ avec un taux de 20%.

📝 Étape 1 : Identifier les données.
📝 Étape 2 : Appliquer la formule TVA = Prix × Taux.

🔒 [CORRECTION DÉTAILLÉE]

✅ Réponse : La TVA est de 20€.
💡 Explication : 100 × 0.20 = 20€

**EXERCICE 2**

Calcule l'intérêt simple d'un placement de 1000€ à 5% pendant 2 ans.

📝 Étape 1 : Formule = C × t × n
📝 Étape 2 : Appliquer les valeurs.

🔒 [CORRECTION DÉTAILLÉE]

✅ Réponse : L'intérêt est de 100€.
💡 Explication : 1000 × 0.05 × 2 = 100€
"""
    resultat = exporter_en_pdf(contenu_test, "Exercices Comptabilité", "test.pdf")
    print(resultat)