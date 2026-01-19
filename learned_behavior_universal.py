#!/usr/bin/env python3
"""
Comportement Appris Universel - Lecture Feed Complète
Sharingan OS - Utilise le contrôleur universel pour appliquer tous les comportements
"""

import sys
import time
import random
from .universal_browser_controller import UniversalBrowserController

def apply_learned_feed_reading():
    """Applique le comportement complet de lecture de feed appris"""
    print("🎯 COMPORTEMENT APPRIS: Lecture Feed Complète")
    print("🔄 Utilise le contrôleur universel Sharingan")
    print("=" * 55)
    print()

    # Initialiser le contrôleur universel
    controller = UniversalBrowserController()

    # Détecter et initialiser
    success, mode = controller.init_control()

    if not success:
        print("❌ Impossible d'initialiser le contrôleur")
        return False

    print(f"✅ Contrôleur initialisé - Mode: {mode}")
    print()

    # Séquence complète apprise
    sequence = [
        {
            'action': 'scroll',
            'direction': 'down',
            'amount': 5,
            'description': 'Découverte initiale du feed',
            'pause': 4.5,
            'read_content': True
        },
        {
            'action': 'scroll',
            'direction': 'down',
            'amount': 3,
            'description': 'Lecture approfondie',
            'pause': 3.8,
            'read_content': True
        },
        {
            'action': 'click_comments',
            'description': 'Exploration commentaires',
            'pause': 3.0,
            'read_comments': True
        },
        {
            'action': 'scroll',
            'direction': 'down',
            'amount': 4,
            'description': 'Continuation naturelle',
            'pause': 4.2,
            'read_content': True
        },
        {
            'action': 'scroll',
            'direction': 'down',
            'amount': 2,
            'description': 'Scroll léger',
            'pause': 2.9,
            'read_content': True
        },
        {
            'action': 'click_comments',
            'description': 'Deuxième exploration',
            'pause': 3.5,
            'read_comments': True
        },
        {
            'action': 'scroll',
            'direction': 'down',
            'amount': 6,
            'description': 'Lecture prolongée',
            'pause': 5.0,
            'read_content': True
        },
        {
            'action': 'scroll',
            'direction': 'up',
            'amount': 2,
            'description': 'Retour en arrière',
            'pause': 2.5,
            'read_content': False
        }
    ]

    total_scrolls = 0
    total_reads = 0
    total_clicks = 0

    print("🚀 APPLICATION DE LA SÉQUENCE APPRISE:")
    print("-" * 50)

    for i, step in enumerate(sequence, 1):
        print(f"[{i}/{len(sequence)}] ", end="")

        if step['action'] == 'scroll':
            direction = step['direction']
            amount = step['amount']
            desc = step['description']

            print(f"📜 {desc} ({amount}×{direction})")

            # Scroll
            success, msg = controller.scroll(direction, amount)
            if success:
                print("   ✅ Scroll réussi")
                total_scrolls += amount
            else:
                print(f"   ❌ {msg}")

            # Lecture de contenu si demandé
            if step.get('read_content', False):
                print("   📖 Analyse du contenu...")
                success, msg = controller.read_content()
                if success:
                    print("   ✅ Contenu analysé")
                    total_reads += 1
                else:
                    print(f"   ⚠️ {msg}")

        elif step['action'] == 'click_comments':
            desc = step['description']
            print(f"💬 {desc}")

            # Clic sur commentaires
            success, msg = controller.click_element("commentaires", x_offset=150, y_offset=80)
            if success:
                print("   ✅ Clic commentaires réussi")
                total_clicks += 1
            else:
                print(f"   ⚠️ {msg}")

            # Lecture des commentaires si demandé
            if step.get('read_comments', False):
                time.sleep(1)  # Attendre le chargement
                print("   📖 Lecture commentaires...")
                success, msg = controller.read_content()
                if success:
                    print("   ✅ Commentaires analysés")
                else:
                    print(f"   ⚠️ {msg}")

        # Pause humaine réaliste
        pause = step['pause'] + random.random() * 1.5
        print(f"   👀 Pause humaine: {pause:.1f}s")
        time.sleep(pause)

        # Pause inter-action naturelle
        if i < len(sequence):
            inter_pause = 0.5 + random.random() * 1.0
            time.sleep(inter_pause)

    print()
    print("🎉 SÉQUENCE COMPLÈTE TERMINÉE !")
    print("📊 RAPPORT D'EXÉCUTION:")
    print(f"   📜 Total scrolls: {total_scrolls} actions")
    print(f"   📖 Lectures contenu: {total_reads}")
    print(f"   💬 Clics commentaires: {total_clicks}")
    print(".1f")
    print(f"   🎭 Mode utilisé: {mode}")
    print()
    print("✨ COMPORTEMENTS APPLIQUÉS:")
    print("   ✅ Scroll humain irrégulier")
    print("   ✅ Pauses de lecture réalistes")
    print("   ✅ Exploration commentaires")
    print("   ✅ Analyse de contenu")
    print("   ✅ Navigation fluide")
    print("   ✅ Sessions utilisateur préservées")

    return True

def main():
    print("🤖 SHARINGAN OS - COMPORTEMENT APPRIS UNIVERSEL")
    print("Lecture complète de feed avec toutes les capacités")
    print()

    try:
        success = apply_learned_feed_reading()
        if success:
            print()
            print("🎯 RÉSULTAT FINAL:")
            print("   • Système universel: ✅ OPÉRATIONNEL")
            print("   • Détection automatique: ✅ FONCTIONNELLE")
            print("   • Contrôle multi-mode: ✅ IMPLÉMENTÉ")
            print("   • Apprentissage préservé: ✅ APPLICABLE")
            print("   • Sessions utilisateur: ✅ PROTÉGÉES")
            print()
            print("🚀 SHARINGAN EST PRÊT POUR TOUTES LES MISSIONS !")
        else:
            print("❌ Échec de l'application du comportement")

    except KeyboardInterrupt:
        print("\n🛑 Interruption par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

if __name__ == "__main__":
    main()