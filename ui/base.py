# ui/base.py - Utilitaires partagés NOKIROVA 🌸

import customtkinter as ctk
from tkinter import messagebox
import re
import os
from PIL import Image

import database as db
from export_pdf import exporter_en_pdf
from notifications import notification_xp, notification_badge, notification_succes

# ═══════════════════════════════════════════
# 🎨 PALETTE
# ═══════════════════════════════════════════
VERT_PRINTEMPS = "#7ED321"
VERT_HOVER = "#8BCF3F"
VERT_CLAIR = "#9FD93B"
VERT_EMERAUDE = "#00C853"
VERT_CORRECTION = "#00B248"
VERT_FOND_CORRECTION = "#E8F5E9"

JAUNE_SOLEIL = "#FFD93D"
JAUNE_CLAIR = "#FFE66D"
JAUNE_PALE = "#FFF3B0"
OR_MODERNE = "#FFB800"

BLEU_CIEL = "#7EC8FF"
BLEU_PALE = "#A5D8FF"
BLEU_TRES_PALE = "#D0EBFF"
BLEU_ROYAL = "#2962FF"

ROSE_SAKURA = "#FFC9DE"
ROSE_CLAIR = "#FFD6E8"
ROSE_PALE = "#FFE5EF"

VIOLET_LAVANDE = "#A855F7"
VIOLET_CLAIR = "#C084FC"
VIOLET_PALE = "#D8B4FE"
VIOLET_PREMIUM = "#7B61FF"

ORANGE_DORE = "#F59E0B"
ORANGE_CLAIR = "#FB923C"
ORANGE_PALE = "#FDBA74"

ROUGE = "#EF4444"
ROUGE_CLAIR = "#FCA5A5"
ROUGE_FOND = "#FEE2E2"

BLANC = "#FFFFFF"
BLANC_CASSE = "#FAFAFA"
GRIS_PERLE = "#F8F9FA"
GRIS_TEXTE = "#374151"
GRIS_DOUX = "#9CA3AF"

NOIR_FOND = "#1A1B26"
NOIR_CARTE = "#24283B"
GRIS_FONCE = "#414868"
BLANC_DOUX = "#C0CAF5"

LOGO_PATH = "frontend/icon-512.png"

TYPES_HISTORIQUE = {
    "question_libre": {"emoji": "💬", "label": "Question libre", "couleur": VIOLET_PALE},
    "resume": {"emoji": "📝", "label": "Résumé", "couleur": BLEU_TRES_PALE},
    "explication": {"emoji": "💡", "label": "Explication", "couleur": JAUNE_PALE},
    "qcm": {"emoji": "🎯", "label": "QCM", "couleur": ROSE_PALE},
    "questions": {"emoji": "❓", "label": "Questions cours", "couleur": ROSE_CLAIR},
    "examen": {"emoji": "📚", "label": "Examen", "couleur": ORANGE_PALE},
    "ocr": {"emoji": "📸", "label": "Scan image", "couleur": VERT_FOND_CORRECTION},
}

# ═══════════════════════════════════════════
# 🎨 THÈME ACTUEL (global)
# ═══════════════════════════════════════════
_theme_actuel = None


def get_theme_actuel():
    """Retourne le thème actuel"""
    global _theme_actuel
    if _theme_actuel is None:
        from ui.themes import get_theme, THEME_DEFAUT
        _theme_actuel = get_theme(THEME_DEFAUT)
    return _theme_actuel


def set_theme_actuel(theme: dict):
    """Définit le thème actuel"""
    global _theme_actuel
    _theme_actuel = theme


def separer_correction(texte_complet: str) -> tuple:
    if not texte_complet or "🔒" not in texte_complet:
        return texte_complet, ""
    blocs = re.split(r'═{20,}', texte_complet)
    questions = []
    corrections = []
    for bloc in blocs:
        if "🔒" in bloc:
            parts = bloc.split("🔒", 1)
            question_part = parts[0].strip()
            correction_part = "🔒" + parts[1].strip() if len(parts) > 1 else ""
            if question_part:
                questions.append(question_part)
            if correction_part:
                corrections.append(correction_part)
        else:
            if bloc.strip():
                questions.append(bloc.strip())
    separateur = "\n\n═══════════════════════════════════════\n\n"
    return separateur.join(questions), separateur.join(corrections)


def parser_qcm(texte_complet: str) -> list:
    if not texte_complet:
        print("⚠️ parser_qcm : texte vide")
        return []
    qcms = []
    blocs = re.split(r'(?=QCM\s*N[°o]?\s*\d+)', texte_complet, flags=re.IGNORECASE)
    print(f"🔍 parser_qcm : {len(blocs)} blocs détectés")
    for idx, bloc in enumerate(blocs):
        bloc = bloc.strip()
        if not bloc or len(bloc) < 50:
            continue
        if not re.search(r'QCM\s*N[°o]?\s*\d+', bloc, re.IGNORECASE):
            continue
        try:
            num_match = re.search(r'QCM\s*N[°o]?\s*(\d+)', bloc, re.IGNORECASE)
            numero = int(num_match.group(1)) if num_match else len(qcms) + 1
            q_match = re.search(r'Question\s*:\s*(.+?)(?=\n\s*A[\)\.])', bloc, re.DOTALL | re.IGNORECASE)
            if q_match:
                question = q_match.group(1).strip()
            else:
                fallback = re.search(
                    r'QCM\s*N[°o]?\s*\d+\s*\n?(.+?)(?=\n\s*A[\)\.])', bloc, re.DOTALL | re.IGNORECASE)
                question = fallback.group(1).strip() if fallback else ""
            question = re.sub(r'\s+', ' ', question).strip()
            options = {}
            for lettre in ['A', 'B', 'C', 'D']:
                if lettre == 'D':
                    pattern = rf'\n\s*{lettre}[\)\.\s]+(.+?)(?=\n\s*🔒|\n\s*\[CORRECTION|\Z)'
                else:
                    prochaine = chr(ord(lettre) + 1)
                    pattern = rf'\n\s*{lettre}[\)\.\s]+(.+?)(?=\n\s*{prochaine}[\)\.\s])'
                opt_match = re.search(pattern, bloc, re.DOTALL)
                if opt_match:
                    texte_opt = opt_match.group(1).strip()
                    texte_opt = re.sub(r'\s+', ' ', texte_opt)
                    options[lettre] = texte_opt[:250]
            br_match = re.search(r'[Bb]onne?\s*r[ée]ponse\s*:?\s*\(?([A-D])\)?', bloc)
            bonne_reponse = br_match.group(1).upper() if br_match else "A"
            exp_match = re.search(
                r'[Ee]xplication[^:]*:\s*(.+?)(?=⚠️|[Ee]rreur\s+courante|\Z)', bloc, re.DOTALL)
            explication = ""
            if exp_match:
                explication = re.sub(r'\s+', ' ', exp_match.group(1)).strip()
            err_match = re.search(r'[Ee]rreur\s*courante\s*:?\s*(.+?)(?=═|\Z)', bloc, re.DOTALL)
            erreur = ""
            if err_match:
                erreur = re.sub(r'\s+', ' ', err_match.group(1)).strip()
            if question and len(options) >= 2:
                qcms.append({
                    "numero": numero,
                    "question": question[:500],
                    "options": options,
                    "bonne_reponse": bonne_reponse,
                    "explication": explication[:600],
                    "erreur_courante": erreur[:300]
                })
                print(f"✅ QCM {numero} parsé : Q='{question[:40]}...', "
                      f"{len(options)} options, bonne={bonne_reponse}")
            else:
                print(f"⚠️ QCM {numero} ignoré : question={bool(question)}, options={len(options)}")
        except Exception as e:
            print(f"⚠️ Erreur parsing bloc {idx} : {e}")
            continue
    print(f"🎯 Total QCM parsés : {len(qcms)}")
    return qcms


class BaseUI:
    """
    Classe de base avec tous les utilitaires partagés.
    NokirovaApp hérite de cette classe.
    """

    def _charger_logo(self, taille):
        try:
            if os.path.exists(LOGO_PATH):
                img = Image.open(LOGO_PATH)
                return ctk.CTkImage(light_image=img, dark_image=img,
                                    size=(taille, taille))
        except Exception as e:
            print(f"⚠️ Logo non chargé : {e}")
        return None

    # ═══════════════════════════════════════════
    # 🎨 SYSTÈME DE THÈMES
    # ═══════════════════════════════════════════

    def appliquer_theme(self, nom_theme: str):
        """Applique un thème sur toute l'application"""
        from ui.themes import get_theme
        import database as db

        theme = get_theme(nom_theme)
        set_theme_actuel(theme)

        # Sauvegarder le choix
        try:
            db.sauvegarder_preference("theme", nom_theme)
        except Exception:
            pass

        # Changer mode CTK (light/dark)
        try:
            ctk.set_appearance_mode(theme["mode_ctk"])
        except Exception:
            pass

        # Appliquer couleurs principales
        try:
            self.configure(fg_color=theme["fond_app"])
        except Exception:
            pass

        # Recharger la sidebar avec nouvelles couleurs
        try:
            self._recharger_sidebar_theme(theme)
        except Exception as e:
            print(f"⚠️ Sidebar theme : {e}")

        # Notification
        notification_succes(
            self, "Thème appliqué !",
            f"{theme['nom']} - {theme['description']}")

        # Recharger page actuelle
        try:
            page = getattr(self, '_page_actuelle', 'afficher_accueil')
            if hasattr(self, page):
                getattr(self, page)()
        except Exception:
            pass

    def _recharger_sidebar_theme(self, theme: dict):
        """Recharge la sidebar avec les couleurs du thème"""
        try:
            # Sidebar principale
            self.sidebar.configure(fg_color=theme["sidebar"])

            # Tous les boutons de la sidebar
            for nom, btn in self._boutons_sidebar.items():
                if btn is None:
                    continue
                try:
                    if nom == getattr(self, '_page_actuelle', ''):
                        btn.configure(
                            fg_color=theme["bouton_actif"],
                            text_color=BLANC)
                    else:
                        btn.configure(
                            fg_color=theme["fond_carte"],
                            text_color=theme["texte_principal"])
                except Exception:
                    pass
        except Exception as e:
            print(f"⚠️ Reload sidebar : {e}")

    def charger_theme_sauvegarde(self):
        """Charge le thème sauvegardé au démarrage"""
        try:
            nom = db.charger_preference("theme")
            if nom:
                self.after(200, lambda: self.appliquer_theme(nom))
        except Exception:
            pass

    # ═══════════════════════════════════════════
    # 🌙 MODE SOMBRE
    # ═══════════════════════════════════════════

    def toggle_mode_sombre(self):
        self.mode_sombre = not self.mode_sombre
        if self.mode_sombre:
            ctk.set_appearance_mode("dark")
            self.configure(fg_color=NOIR_FOND)
        else:
            ctk.set_appearance_mode("light")
            self.configure(fg_color=BLANC_CASSE)
        notification_succes(self, "Mode changé",
                            "🌙 Mode sombre activé" if self.mode_sombre
                            else "☀️ Mode jour activé")

    # ═══════════════════════════════════════════
    # 🏗️ UTILITAIRES UI
    # ═══════════════════════════════════════════

    def vider_zone(self):
        for widget in self.zone_principale.winfo_children():
            widget.destroy()

    def _enregistrer_navigation(self, nom_page):
        """Mémorise la page actuelle pour le bouton retour"""
        if not hasattr(self, '_historique_pages'):
            self._historique_pages = []
        if (not self._historique_pages or
                self._historique_pages[-1] != nom_page):
            self._historique_pages.append(nom_page)
            if len(self._historique_pages) > 20:
                self._historique_pages = self._historique_pages[-20:]
        self._page_actuelle = nom_page

    def _retour_page(self):
        """Revient à la page précédente"""
        if (not hasattr(self, '_historique_pages') or
                len(self._historique_pages) < 2):
            self.afficher_accueil()
            return
        self._historique_pages.pop()
        page_precedente = self._historique_pages.pop()
        if hasattr(self, page_precedente):
            try:
                getattr(self, page_precedente)()
            except Exception:
                self.afficher_accueil()
        else:
            self.afficher_accueil()

    def afficher_titre(self, texte, emoji="🌸", couleur=None):
        """Affiche le titre AVEC flèche de retour à gauche"""
        # Utiliser couleur du thème si pas spécifiée
        if couleur is None:
            theme = get_theme_actuel()
            couleur = theme.get("titre_page", VERT_EMERAUDE)

        carte_titre = ctk.CTkFrame(
            self.zone_principale, fg_color=couleur,
            corner_radius=18, height=75)
        carte_titre.pack(fill="x", pady=(0, 15))
        carte_titre.pack_propagate(False)

        ctk.CTkButton(
            carte_titre, text="◀",
            command=self._retour_page,
            fg_color=BLANC, hover_color=GRIS_PERLE,
            text_color=couleur,
            font=ctk.CTkFont(size=20, weight="bold"),
            width=55, height=45, corner_radius=12).pack(
            side="left", padx=15, pady=15)

        ctk.CTkLabel(
            carte_titre,
            text=f"{emoji}  {texte}",
            font=ctk.CTkFont(
                family="Segoe UI", size=24, weight="bold"),
            text_color=BLANC).pack(
            side="left", expand=True, pady=18)

        ctk.CTkLabel(carte_titre, text="", width=55).pack(
            side="right", padx=15)

    def creer_zone_texte(self, hauteur=400):
        cadre = ctk.CTkFrame(
            self.zone_principale, fg_color=BLANC,
            corner_radius=18,
            border_width=2, border_color=BLEU_TRES_PALE)
        cadre.pack(fill="both", expand=True, pady=10)
        zone = ctk.CTkTextbox(
            cadre, height=hauteur, fg_color=BLANC,
            text_color=GRIS_TEXTE,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=15, wrap="word", border_width=0)
        zone.pack(fill="both", expand=True, padx=15, pady=15)
        return zone

    def creer_bouton_action(self, parent, texte, commande,
                            couleur=None, hover=None):
        if couleur is None:
            theme = get_theme_actuel()
            couleur = theme.get("bouton_actif", VERT_EMERAUDE)
        if hover is None:
            theme = get_theme_actuel()
            hover = theme.get("bouton_hover", VERT_HOVER)
        return ctk.CTkButton(
            parent, text=texte, command=commande,
            fg_color=couleur, text_color=BLANC, hover_color=hover,
            font=ctk.CTkFont(
                family="Segoe UI", size=15, weight="bold"),
            height=48, corner_radius=14)

    def creer_bouton_export(self, contenu, nom: str = "document"):
        return ctk.CTkButton(
            self.zone_principale, text="💾  Exporter en PDF",
            command=lambda: self._exporter(contenu, nom),
            fg_color=OR_MODERNE, text_color=BLANC,
            hover_color=ORANGE_CLAIR,
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38, corner_radius=12)

    def _exporter(self, contenu_widget, nom: str):
        if hasattr(contenu_widget, 'get'):
            texte = contenu_widget.get("0.0", "end").strip()
        else:
            texte = str(contenu_widget)
        if not texte or "⚠️" in texte[:20]:
            messagebox.showwarning(
                "⚠️", "Rien à exporter ! Génère du contenu d'abord.")
            return
        from datetime import datetime
        date_simple = datetime.now().strftime('%d-%m-%Y')
        matiere_propre = "General"
        if self.matiere_detectee:
            matiere_temp = self.matiere_detectee.strip()
            matiere_propre = re.sub(
                r'[^\w\sàâäéèêëïîôöùûüÿç-]', '', matiere_temp).strip()
            matiere_propre = matiere_propre.replace(' ', '_')[:30]
            if not matiere_propre:
                matiere_propre = "General"
        types_nom = {
            "resume": "Resume", "explication": "Explication",
            "qcm": "QCM", "questions": "Questions",
            "examen": "Examen", "ocr": "Scan", "reponse": "Reponse_IA"
        }
        type_doc = types_nom.get(nom, nom.title())
        nom_fichier = f"NOKIROVA_{type_doc}_{matiere_propre}_{date_simple}.pdf"
        titre_doc = f"{type_doc} - {matiere_propre.replace('_', ' ')}"
        resultat = exporter_en_pdf(texte, titre_doc, nom_fichier)
        if "Erreur" not in resultat and "❌" not in resultat:
            if "2 PDFs créés" in resultat:
                notification_succes(self, "2 PDFs créés !",
                                    "📝 Exercices + ✅ Corrigé")
                messagebox.showinfo("✅ 2 PDFs créés",
                                    "📁 dossier 'outputs/'")
            else:
                notification_succes(self, "PDF exporté !",
                                    f"📄 {type_doc}")
                messagebox.showinfo(
                    "✅ PDF créé",
                    f"📄 {nom_fichier}\n\n📁 {resultat}")
        else:
            messagebox.showerror("❌ Erreur", resultat)

    def _recompenser(self, points: int, message: str = ""):
        ancien_niveau = db.get_stats()["niveau"]
        db.ajouter_xp(points)
        nouveau_niveau = db.get_stats()["niveau"]
        notification_xp(self, points, message)
        if nouveau_niveau > ancien_niveau:
            self.after(2500, lambda: notification_succes(
                self, f"NIVEAU {nouveau_niveau} !",
                f"🎉 Tu es maintenant "
                f"{db.get_niveau_titre(nouveau_niveau)} !"))
        nouveaux = db.verifier_badges()
        for i, badge in enumerate(nouveaux):
            self.after(3000 + i * 4000,
                       lambda b=badge: notification_badge(
                           self, b["emoji"], b["nom"], b["description"]))

    def _creer_bouton_correction(self, type_zone: str):
        btn = ctk.CTkButton(
            self.zone_principale, text="✅  CORRIGER",
            fg_color=VERT_EMERAUDE, hover_color=VERT_HOVER,
            text_color=BLANC,
            font=ctk.CTkFont(
                family="Segoe UI", size=15, weight="bold"),
            height=44, corner_radius=14,
            border_width=2, border_color=VERT_CORRECTION)
        btn.configure(
            command=lambda: self._toggle_correction(type_zone, btn))
        return btn

    def _toggle_correction(self, type_zone: str, btn):
        if type_zone == "qcm":
            zone = self.zone_qcm
            contenu_complet = self.contenu_qcm_complet
        elif type_zone == "q":
            zone = self.zone_q
            contenu_complet = self.contenu_q_complet
        elif type_zone == "ex":
            zone = self.zone_ex
            contenu_complet = self.contenu_ex_complet
        else:
            return
        if not contenu_complet:
            messagebox.showwarning(
                "⚠️", "Génère d'abord des questions !")
            return
        questions, corrections = separer_correction(contenu_complet)
        self.correction_visible[type_zone] = \
            not self.correction_visible[type_zone]
        zone.delete("0.0", "end")
        if self.correction_visible[type_zone]:
            zone.insert("0.0",
                        f"{questions}\n\n{'🟢' * 30}\n"
                        f"✅ CORRECTION COMPLÈTE ✅\n"
                        f"{'🟢' * 30}\n\n{corrections}")
            btn.configure(text="🔒  CACHER LA CORRECTION",
                          fg_color=VERT_CORRECTION,
                          hover_color=VERT_EMERAUDE)
        else:
            zone.insert("0.0", questions)
            btn.configure(text="✅  CORRIGER",
                          fg_color=VERT_EMERAUDE,
                          hover_color=VERT_HOVER)

    def _surligner_mot_recherche(self, texte: str, mot_cle: str) -> str:
        pattern = re.compile(re.escape(mot_cle), re.IGNORECASE)
        return pattern.sub(f"[{mot_cle.upper()}]", texte)

    def _injecter_contenu(self, zone, contenu):
        try:
            zone.delete("0.0", "end")
            zone.insert("0.0", contenu)
        except Exception as e:
            print(f"⚠️ Injection contenu : {e}")

    def _creer_ligne_graphique(self, parent, label, valeur,
                               max_valeur, couleur):
        ligne = ctk.CTkFrame(
            parent, fg_color=BLANC, corner_radius=12, height=70)
        ligne.pack(fill="x", padx=15, pady=6)
        ligne.pack_propagate(False)
        top = ctk.CTkFrame(ligne, fg_color="transparent", height=28)
        top.pack(fill="x", padx=12, pady=(10, 2))
        top.pack_propagate(False)
        ctk.CTkLabel(
            top, text=str(label)[:50],
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=GRIS_TEXTE, anchor="w").pack(
            side="left", fill="x", expand=True)
        ctk.CTkLabel(
            top, text=str(valeur),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=couleur).pack(side="right")
        barre = ctk.CTkProgressBar(
            ligne, progress_color=couleur,
            fg_color=GRIS_PERLE, height=14, corner_radius=7)
        barre.pack(fill="x", padx=12, pady=(2, 10))
        ratio = (valeur / max_valeur) if max_valeur > 0 else 0
        barre.set(max(ratio, 0.03))