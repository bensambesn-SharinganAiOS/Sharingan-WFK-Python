#!/usr/bin/env python3
"""
CONVERSATION INTERACTIVE - SHARINGAN OS
Discussion continue avec Grok sur les capacités du système
"""

from universal_browser_controller import UniversalBrowserController
import time
import random

class SharinganOSConversation:
    def __init__(self):
        self.controller = UniversalBrowserController()
        self.conversation_topics = [
            "les APIs cloud intégrées comme OCR.space et SerpApi",
            "l'intelligence artificielle native avec MiniMax et GLM-4",
            "le contrôle physique du navigateur avec xdotool",
            "l'architecture API-First qui préserve les ressources",
            "les capacités de cybersécurité automatisée",
            "l'audit de sécurité intelligent avec scoring",
            "la reconnaissance visuelle sans traitement local",
            "l'intégration transparente avec les systèmes existants"
        ]
        self.discussed_topics = set()
        self.start_time = time.time()
        self.duration_minutes = 10

    def initialize(self):
        """Initialisation du système de conversation"""
        print("🎯 INITIALISATION CONVERSATION SHARINGAN OS")
        print("=" * 50)

        success, mode = self.controller.init_control()
        if not success:
            print("❌ Échec initialisation")
            return False

        print(f"✅ Système prêt: {mode}")
        print(f"⏰ Durée cible: {self.duration_minutes} minutes")
        print()
        return True

    def send_message(self, message):
        """Envoi d'un message dans l'interface chat"""
        print(f"📤 Envoi: {message[:60]}...")

        # Saisie du message
        result = self.controller.fill_form_field(
            'message_input',
            message,
            x_offset=200,
            y_offset=500
        )

        if result and result[0]:
            time.sleep(1)

            # Clic sur envoyer
            send_result = self.controller.click_specific_element(
                'send_button',
                x=600,
                y=510
            )

            if send_result and send_result[0]:
                print("✅ Message envoyé")
                return True

        print("❌ Échec envoi message")
        return False

    def read_response(self):
        """Lecture de la réponse de l'IA"""
        print("📖 Lecture réponse...")

        # Tentative de lecture OCR
        ocr_result = self.controller.read_text_from_screen()
        if ocr_result and ocr_result[0]:
            response_text = ocr_result[1]
            print(f"📄 Réponse détectée ({len(response_text)} chars)")
            return response_text[:200] + "..." if len(response_text) > 200 else response_text

        # Fallback: juste indiquer qu'on attend
        print("⏳ Réponse en cours de génération...")
        return None

    def generate_next_message(self, previous_response=None):
        """Génération du prochain message de conversation"""

        # Sélection d'un topic non discuté
        available_topics = [t for t in self.conversation_topics if t not in self.discussed_topics]

        if not available_topics:
            # Tous les topics discutés, recommencer ou conclure
            return random.choice([
                "C'est incroyable tout ce que Sharingan OS peut faire ! Et je ne t'ai pas encore parlé de l'audit cybersécurité automatisé avec scoring intelligent. Tu veux que je développe cet aspect ?",
                "Au fait, l'un des points forts de Sharingan OS c'est son architecture modulaire qui permet l'intégration transparente de nouvelles APIs. C'est vraiment pensé pour l'évolutivité !",
                "Je suis vraiment enthousiaste par ce projet. Sharingan OS représente l'avenir de la cybersécurité automatisée. Qu'est-ce qui t'intéresse le plus dans cette approche ?"
            ])

        next_topic = random.choice(available_topics)
        self.discussed_topics.add(next_topic)

        # Génération de message basé sur le topic
        messages = {
            "les APIs cloud intégrées comme OCR.space et SerpApi": [
                "Parlons des APIs cloud intégrées ! Sharingan OS utilise OCR.space pour la reconnaissance de texte (25K requêtes gratuites/mois), SerpApi pour la recherche d'images inversée Bing, et SearchAPI.io pour Yandex. Plus besoin de traitement local lourd avec nos 4GB RAM !",
                f"Les APIs cloud sont au cœur de Sharingan OS. On exploite OCR.space pour lire le texte à l'écran, SerpApi pour analyser les images, et toute une batterie de services fact-checking comme Google Fact Check Tools. C'est une puissance incroyable sans surcharge locale !"
            ],
            "l'intelligence artificielle native avec MiniMax et GLM-4": [
                f"L'IA native est impressionnante ! Sharingan OS intègre MiniMax pour les tâches complexes, GLM-4 pour la génération de langage avancée, et même tgpt pour les réponses rapides. Tout est orchestré via une architecture API-First intelligente.",
                f"L'intelligence artificielle de Sharingan OS est vraiment de pointe. On combine MiniMax pour l'analyse profonde, GLM-4 pour les tâches créatives, et OpenRouter pour le routage optimal. C'est une IA distribuée et évolutive !"
            ],
            "le contrôle physique du navigateur avec xdotool": [
                f"Le contrôle physique est une révolution ! Avec xdotool, Sharingan OS contrôle réellement le navigateur Chrome de l'utilisateur tout en préservant les sessions Gmail, Facebook, etc. C'est du vrai contrôle humain simulé !",
                f"Xdotool permet un contrôle physique incroyable. Sharingan OS peut scroller, cliquer, saisir du texte exactement comme un humain. Et le meilleur : les comptes utilisateur restent connectés. C'est de la cybersécurité réaliste !"
            ],
            "l'architecture API-First qui préserve les ressources": [
                f"L'architecture API-First est géniale ! Au lieu de tout traiter localement avec nos 4GB RAM limités, Sharingan OS délègue aux APIs cloud. OCR, IA, reconnaissance visuelle : tout est dans le cloud, rien ne pèse sur nos ressources !",
                f"API-First signifie puissance maximale avec ressources minimales. Sharingan OS ne stocke rien localement, exploite les APIs cloud pour tout : OCR, recherche d'images, fact-checking, IA. Nos 4GB RAM sont préservés pour l'essentiel !"
            ],
            "les capacités de cybersécurité automatisée": [
                f"La cybersécurité automatisée de Sharingan OS est incroyable ! Audit automatique avec scoring, détection de menaces, analyse de contenu suspect. Tout combiné avec les APIs de sécurité et l'IA native.",
                f"Sharingan OS révolutionne la cybersécurité. Audit automatique des sites, scoring de sécurité, détection de contenu malveillant, vérification factuelle. Tout piloté par IA et APIs spécialisées. C'est l'avenir de la sécurité !"
            ],
            "l'audit de sécurité intelligent avec scoring": [
                f"L'audit intelligent donne un score de sécurité sur 100 ! Sharingan OS analyse navigation, contenu, certificats SSL, menaces potentielles. Un vrai outil de cybersécurité professionnelle.",
                f"Le scoring de sécurité est sophistiqué : analyse des certificats, vérification du contenu, détection de menaces, évaluation des risques. Sharingan OS fournit un rapport complet avec recommandations. Idéal pour les audits !"
            ],
            "la reconnaissance visuelle sans traitement local": [
                f"La reconnaissance visuelle sans traitement local ? Génial ! Sharingan OS utilise SerpApi et SearchAPI pour analyser les images dans le cloud. Nos 4GB RAM ne sont pas sollicités pour l'analyse d'images complexe !",
                f"Reconnaissance visuelle cloud-native ! Sharingan OS envoie les captures d'écran aux APIs spécialisées (SerpApi, SearchAPI) pour analyse. Résultats instantanés sans traitement local lourd. Parfait pour nos contraintes matérielles !"
            ],
            "l'intégration transparente avec les systèmes existants": [
                f"L'intégration transparente est un gros plus ! Sharingan OS s'intègre parfaitement avec les systèmes existants sans les casser. APIs modulaires, architecture préservée, compatibilité ascendante. Un vrai système évolutif !",
                f"Sharingan OS respecte l'existant ! Intégration transparente avec les systèmes en place, APIs modulaires qui s'ajoutent sans casser, architecture qui évolue. C'est pensé pour durer et s'adapter !"
            ]
        }

        return random.choice(messages.get(next_topic, ["Intéressant ! Parlons d'autre chose dans Sharingan OS."]))

    def maintain_conversation(self):
        """Maintien de la conversation pendant la durée spécifiée"""
        print("🎬 DÉMARRAGE CONVERSATION INTERACTIVE")
        print("=" * 50)
        print("💬 Sujet: Partage des capacités de Sharingan OS")
        print(f"⏰ Durée: {self.duration_minutes} minutes")
        print()

        message_count = 0
        start_time = time.time()

        while time.time() - start_time < (self.duration_minutes * 60):
            elapsed_minutes = (time.time() - start_time) / 60
            print(f"⏰ Temps écoulé: {elapsed_minutes:.1f} minutes")

            # Génération du prochain message
            next_message = self.generate_next_message()

            # Envoi du message
            if self.send_message(next_message):
                message_count += 1
                print(f"📊 Messages envoyés: {message_count}")
            else:
                print("❌ Échec envoi, retry dans 5s...")
                time.sleep(5)
                continue

            # Attente réponse (plus longue pour laisser l'IA répondre)
            print("⏳ Attente réponse de Grok...")
            time.sleep(random.randint(8, 15))  # 8-15 secondes

            # Tentative de lecture réponse
            response = self.read_response()
            if response:
                print(f"🤖 Grok: {response}")
            else:
                print("🤖 Réponse en cours...")

            # Petite pause avant prochain message
            pause_time = random.randint(3, 7)
            print(f"⏸️ Pause de {pause_time}s avant prochain message...")
            time.sleep(pause_time)

            print("-" * 50)

        # Fin de conversation
        final_message = "Merci pour cette discussion passionnante sur Sharingan OS ! Ce système représente vraiment l'avenir de la cybersécurité automatisée avec son approche API-First et ses capacités d'IA intégrée. C'était un plaisir de partager ces innovations avec toi ! 🚀"
        self.send_message(final_message)

        total_time = time.time() - start_time
        print("\n🎊 CONVERSATION TERMINÉE !")
        print(f"📊 Statistiques:")
        print(f"   • Durée: {total_time/60:.1f} minutes")
        print(f"   • Messages: {message_count}")
        print(f"   • Topics couverts: {len(self.discussed_topics)}/{len(self.conversation_topics)}")
        print(f"   • Taux de réussite: {(message_count/(total_time/60)):.1f} messages/minute")

def main():
    conversation = SharinganOSConversation()

    if conversation.initialize():
        conversation.maintain_conversation()
    else:
        print("❌ Impossible d'initialiser la conversation")

if __name__ == "__main__":
    main()