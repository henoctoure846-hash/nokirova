# mobile_app.py - NOKIROVA Mobile 🌸
# Version OPTIMISÉE - Scroll + Spinner + Clavier mobile

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
import threading

from ia_handler import demander_ia

KV = """
MDScreen:
    md_bg_color: 0.98, 0.98, 0.98, 1

    MDBoxLayout:
        orientation: "vertical"
        spacing: "12dp"
        padding: "16dp"

        # ── TITRE ──
        MDCard:
            size_hint_y: None
            height: "80dp"
            radius: [20]
            md_bg_color: 0.49, 0.83, 0.13, 1

            MDBoxLayout:
                padding: "10dp"

                MDLabel:
                    text: "🌸 NOKIROVA Mobile"
                    halign: "center"
                    font_style: "H5"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1

        # ── SPINNER DE CHARGEMENT ──
        MDBoxLayout:
            size_hint_y: None
            height: "40dp"
            padding: "8dp"

            MDSpinner:
                id: spinner
                size_hint: None, None
                size: "30dp", "30dp"
                pos_hint: {"center_x": 0.5, "center_y": 0.5}
                active: False
                color: 0.48, 0.38, 1, 1

            MDLabel:
                id: statut
                text: "✅ Prêt"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 0.78, 0.33, 1
                font_style: "Caption"

        # ── ZONE DE RÉPONSE (SCROLLABLE) ──
        MDCard:
            radius: [15]
            md_bg_color: 1, 1, 1, 1
            elevation: 3

            ScrollView:
                id: scroll_reponse
                do_scroll_x: False
                do_scroll_y: True

                MDLabel:
                    id: zone_reponse
                    text: "✨ La réponse de NOKIROVA apparaîtra ici...\\n\\n💡 Pose ta question en bas !"
                    halign: "left"
                    valign: "top"
                    theme_text_color: "Custom"
                    text_color: 0.22, 0.25, 0.32, 1
                    size_hint_y: None
                    height: self.texture_size[1]
                    text_size: self.width, None
                    padding: "16dp", "16dp"
                    markup: True

        # ── CHAMP DE QUESTION ──
        MDCard:
            size_hint_y: None
            height: "70dp"
            radius: [15]
            md_bg_color: 1, 1, 1, 1
            elevation: 2

            MDBoxLayout:
                orientation: "horizontal"
                padding: "10dp"
                spacing: "8dp"

                MDTextField:
                    id: champ_question
                    hint_text: "💬 Pose ta question..."
                    mode: "rectangle"
                    multiline: False
                    on_text_validate: app.envoyer_question()

                MDRaisedButton:
                    text: "🚀"
                    size_hint_x: None
                    width: "56dp"
                    md_bg_color: 0.48, 0.38, 1, 1
                    on_release: app.envoyer_question()
"""


class NokirovaMobileApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        self.root = Builder.load_string(KV)
        return self.root

    def envoyer_question(self):
        champ = self.root.ids.champ_question
        question = champ.text.strip()

        if not question:
            self.root.ids.zone_reponse.text = "⚠️ Tape une question d'abord !"
            return

        # Vider le champ
        champ.text = ""

        # Afficher chargement + spinner
        self.root.ids.zone_reponse.text = "⏳ NOKIROVA réfléchit... 🧠✨"
        self.root.ids.statut.text = "⏳ En cours..."
        self.root.ids.spinner.active = True

        threading.Thread(
            target=self._appeler_ia,
            args=(question,),
            daemon=True
        ).start()

    def _appeler_ia(self, question: str):
        try:
            reponse = demander_ia(question)
        except Exception as e:
            reponse = f"❌ Erreur : {str(e)}"

        Clock.schedule_once(
            lambda dt: self._afficher_reponse(reponse), 0
        )

    def _afficher_reponse(self, reponse: str):
        # Afficher la réponse
        self.root.ids.zone_reponse.text = reponse

        # Stopper le spinner
        self.root.ids.spinner.active = False
        self.root.ids.statut.text = "✅ Réponse reçue !"

        # Scroll automatique vers le haut de la réponse
        Clock.schedule_once(
            lambda dt: setattr(self.root.ids.scroll_reponse, 'scroll_y', 1), 0.1
        )


if __name__ == "__main__":
    NokirovaMobileApp().run()