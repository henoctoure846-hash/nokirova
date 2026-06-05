# ui/themes.py - Système de thèmes NOKIROVA 🎨

# ═══════════════════════════════════════════
# 🎨 DÉFINITION DES 6 THÈMES
# ═══════════════════════════════════════════

THEMES = {

    "🌸 Spring": {
        "nom": "🌸 Spring",
        "description": "Vert printemps & Jaune soleil",
        "sidebar": "#7ED321",
        "sidebar_titre": "#FFE66D",
        "bouton_actif": "#00C853",
        "bouton_hover": "#8BCF3F",
        "fond_app": "#FAFAFA",
        "fond_carte": "#FFFFFF",
        "texte_principal": "#374151",
        "texte_secondaire": "#9CA3AF",
        "accent1": "#FFD93D",
        "accent2": "#FFC9DE",
        "titre_page": "#00C853",
        "progress": "#7ED321",
        "mode_ctk": "light",
    },

    "🌙 Nuit": {
        "nom": "🌙 Nuit",
        "description": "Mode sombre élégant",
        "sidebar": "#1A1B26",
        "sidebar_titre": "#24283B",
        "bouton_actif": "#7B61FF",
        "bouton_hover": "#A855F7",
        "fond_app": "#1A1B26",
        "fond_carte": "#24283B",
        "texte_principal": "#C0CAF5",
        "texte_secondaire": "#414868",
        "accent1": "#FFD93D",
        "accent2": "#7B61FF",
        "titre_page": "#7B61FF",
        "progress": "#A855F7",
        "mode_ctk": "dark",
    },

    "🌊 Océan": {
        "nom": "🌊 Océan",
        "description": "Bleu profond & Ciel azur",
        "sidebar": "#2962FF",
        "sidebar_titre": "#A5D8FF",
        "bouton_actif": "#0288D1",
        "bouton_hover": "#7EC8FF",
        "fond_app": "#F0F7FF",
        "fond_carte": "#FFFFFF",
        "texte_principal": "#1A237E",
        "texte_secondaire": "#5C6BC0",
        "accent1": "#7EC8FF",
        "accent2": "#D0EBFF",
        "titre_page": "#2962FF",
        "progress": "#0288D1",
        "mode_ctk": "light",
    },

    "🌺 Sakura": {
        "nom": "🌺 Sakura",
        "description": "Rose doux & Violet lavande",
        "sidebar": "#F06292",
        "sidebar_titre": "#FFE5EF",
        "bouton_actif": "#E91E8C",
        "bouton_hover": "#FFC9DE",
        "fond_app": "#FFF5F8",
        "fond_carte": "#FFFFFF",
        "texte_principal": "#880E4F",
        "texte_secondaire": "#F48FB1",
        "accent1": "#FFC9DE",
        "accent2": "#A855F7",
        "titre_page": "#E91E8C",
        "progress": "#F06292",
        "mode_ctk": "light",
    },

    "🍂 Automne": {
        "nom": "🍂 Automne",
        "description": "Orange chaud & Brun doré",
        "sidebar": "#F59E0B",
        "sidebar_titre": "#FFF3B0",
        "bouton_actif": "#D97706",
        "bouton_hover": "#FDBA74",
        "fond_app": "#FFFBF0",
        "fond_carte": "#FFFFFF",
        "texte_principal": "#78350F",
        "texte_secondaire": "#D97706",
        "accent1": "#FDBA74",
        "accent2": "#FCD34D",
        "titre_page": "#D97706",
        "progress": "#F59E0B",
        "mode_ctk": "light",
    },

    "💜 Lavande": {
        "nom": "💜 Lavande",
        "description": "Violet doux & Lilas",
        "sidebar": "#7B61FF",
        "sidebar_titre": "#D8B4FE",
        "bouton_actif": "#6D28D9",
        "bouton_hover": "#A855F7",
        "fond_app": "#FAF5FF",
        "fond_carte": "#FFFFFF",
        "texte_principal": "#4C1D95",
        "texte_secondaire": "#7C3AED",
        "accent1": "#D8B4FE",
        "accent2": "#FFC9DE",
        "titre_page": "#7B61FF",
        "progress": "#A855F7",
        "mode_ctk": "light",
    },
}

# Thème par défaut
THEME_DEFAUT = "🌸 Spring"


def get_theme(nom: str) -> dict:
    """Retourne un thème par son nom"""
    return THEMES.get(nom, THEMES[THEME_DEFAUT])


def get_liste_themes() -> list:
    """Retourne la liste des noms de thèmes"""
    return list(THEMES.keys())