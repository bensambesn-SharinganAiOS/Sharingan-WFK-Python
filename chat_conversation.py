#!/usr/bin/env python3
"""
CONVERSATION INTERACTIVE SIMPLIFIÉE - SHARINGAN OS
"""

from universal_browser_controller import UniversalBrowserController
import time
import random

def main():
    print("🎯 CONVERSATION INTERACTIVE SHARINGAN OS")
    print("=" * 45)

    controller = UniversalBrowserController()
    success, mode = controller.init_control()

    if not success:
        print("❌ Initialisation échouée")
        return

    print(f"✅ Mode: {mode}")
    print("⏰ Durée: 10 minutes")
    print()

    # Messages de conversation sur Sharingan OS
    messages = [
        "Salut ! Je développe Sharingan OS, un système incroyable qui combine IA et cybersécurité. Il contrôle le navigateur physiquement avec xdotool tout en utilisant des APIs cloud comme OCR.space !",
        "Ce qui est fascinant, c'est l'approche hybride : contrôle physique préserve les sessions utilisateur (Gmail, Facebook) + APIs cloud pour l'IA sans traitement local lourd.",
        "Sharingan OS intègre MiniMax, GLM-4, et tgpt pour l'intelligence artificielle. Tout est orchestré via une architecture API-First qui évolue automatiquement !",
        "Les APIs cloud sont au cœur : OCR.space pour lire le texte (25K req/mois gratuit), SerpApi pour reverse image search, et des providers IA multiples. Génial non ?",
        "La cybersécurité est révolutionnée : audit automatique avec scoring, détection de menaces, analyse factuelle avec Google Fact Check Tools. Un vrai outil pro !",
        "Plus besoin de ressources locales massives ! Sharingan OS délègue tout aux APIs cloud : OCR, IA, reconnaissance visuelle. Parfait pour nos 4GB RAM.",
        "L'architecture API-First est géniale : pas de stockage local, routage intelligent entre providers, évolutivité maximale. L'avenir de l'IA !",
        "Imagine : contrôle physique réaliste + IA cloud illimitée + sécurité automatisée. Sharingan OS représente vraiment l'avenir de la cybersécurité.",
        "Les tests sont impressionnants : navigation parfaite, interactions fluides, analyse IA instantanée. Tout fonctionne de manière transparente !",
        "Merci pour cette discussion ! Sharingan OS est prêt pour des missions critiques avec son approche innovante API-First + contrôle physique."
    ]

    start_time = time.time()
    message_count = 0

    while time.time() - start_time < 600:  # 10 minutes
        elapsed = time.time() - start_time
        print(f"⏰ {elapsed/60:.1f}min - Message {message_count + 1}")

        # Sélection d'un message
        if message_count < len(messages):
            message = messages[message_count]
        else:
            message = random.choice(messages)

        # Envoi du message
        print(f"📤 Envoi: {message[:50]}...")

        # Saisie
        result1 = controller.fill_form_field('message_input', message, x_offset=200, y_offset=500)
        print(f"   ✍️ Saisie: {'✅' if result1 and result1[0] else '❌'}")

        time.sleep(1)

        # Envoi
        result2 = controller.click_specific_element('send_button', x=600, y=510)
        print(f"   📤 Envoi: {'✅' if result2 and result2[0] else '❌'}")

        message_count += 1

        # Attente avant prochain message (20-40 secondes)
        wait_time = random.randint(20, 40)
        print(f"⏳ Attente {wait_time}s...")
        time.sleep(wait_time)

        print("-" * 45)

    print("
🎊 CONVERSATION TERMINÉE !"    print(f"📊 {message_count} messages envoyés en {elapsed/60:.1f} minutes")

if __name__ == "__main__":
    main()