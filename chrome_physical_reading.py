#!/usr/bin/env python3
"""
Comportement Appris - Lecture Physique YouTube
Sharingan OS - Utilise xdotool pour contrôler Chrome existant
"""

import subprocess
import time
import random
import sys

def run_cmd(cmd):
    """Exécute une commande système"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip()
    except:
        return False, ''

def scroll_wheel(steps=1, direction='down'):
    """Scroll avec la molette"""
    button = 5 if direction == 'down' else 4  # 5=bas, 4=haut
    for _ in range(steps):
        success, _ = run_cmd(f'xdotool click {button}')
        if success:
            time.sleep(0.1 + random.random() * 0.2)  # Petit délai entre scrolls
        else:
            print("⚠️ Échec scroll")
            return False
    return True

def click_relative(x_offset, y_offset):
    """Clic relatif à la position actuelle"""
    success1, _ = run_cmd(f'xdotool mousemove_relative {x_offset} {y_offset}')
    if success1:
        time.sleep(0.3)
        success2, _ = run_cmd('xdotool click 1')
        time.sleep(0.5)
        return success2
    return False

def human_reading_sequence():
    """Séquence complète de lecture humaine"""
    print("🎯 Comportement appris: Lecture humaine physique")
    print("🔄 Utilise xdotool sur Chrome existant")
    print("📱 Assurez-vous que Chrome/YouTube est la fenêtre active")
    print("=" * 55)
    print()

    sequence = [
        {'action': 'scroll', 'steps': 6, 'pause': 4.5, 'desc': 'Long scroll initial'},
        {'action': 'scroll', 'steps': 4, 'pause': 3.2, 'desc': 'Scroll moyen'},
        {'action': 'click_comments', 'pause': 2.8, 'desc': 'Exploration commentaires'},
        {'action': 'scroll', 'steps': 5, 'pause': 4.1, 'desc': 'Scroll après commentaires'},
        {'action': 'scroll', 'steps': 3, 'pause': 2.9, 'desc': 'Scroll court'},
        {'action': 'click_comments', 'pause': 3.5, 'desc': 'Deuxième exploration'},
        {'action': 'scroll', 'steps': 7, 'pause': 4.8, 'desc': 'Long scroll final'},
        {'action': 'scroll', 'steps': 4, 'pause': 3.6, 'desc': 'Scroll de clôture'},
    ]

    total_scrolls = 0

    for i, step in enumerate(sequence, 1):
        print(f"[{i}/{len(sequence)}] ", end="")

        if step['action'] == 'scroll':
            steps = step['steps']
            desc = step['desc']
            print(f"📜 {desc} ({steps} étapes)")

            if scroll_wheel(steps):
                print("   ✅ Scroll réussi")
                total_scrolls += steps
            else:
                print("   ❌ Scroll échoué")

        elif step['action'] == 'click_comments':
            desc = step['desc']
            print(f"💬 {desc}")

            # Clic approximatif dans la zone commentaires (ajustable)
            if click_relative(150, 100):
                print("   ✅ Clic réussi")
            else:
                print("   ❌ Clic échoué")

        # Pause de lecture humaine
        pause = step['pause'] + random.random() * 1.5  # Variation naturelle
        print(f"   📖 Lecture: {pause:.1f}s")
        time.sleep(pause)

        # Pause inter-action naturelle
        inter_pause = 0.3 + random.random() * 0.7
        time.sleep(inter_pause)

    print()
    print("🎉 Séquence de lecture terminée !")
    print("📊 Résumé de la session:")
    print(f"   📜 Total scrolls: {total_scrolls} étapes de molette")
    print("   💬 Explorations commentaires: 2")
    print("   ⏱️ Durée totale: ~45 secondes")
    print("   🎭 Comportement: 100% humain")
    print("   🔄 Chrome: Maintenu ouvert avec vos comptes")

def main():
    print("🌍 LECTURE PHYSIQUE YOUTUBE - SHARINGAN OS")
    print("Contrôle physique du Chrome existant")
    print()

    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python3 chrome_physical_reading.py")
        print()
        print("Ce script applique le comportement de lecture humaine appris:")
        print("• Scrolls de molette réalistes (4-8 étapes)")
        print("• Pauses de lecture variables (2.5-6s)")
        print("• Clics dans la zone commentaires")
        print("• Comportement 100% humain")
        print()
        print("⚠️ Assurez-vous que Chrome/YouTube est la fenêtre active")
        return

    try:
        human_reading_sequence()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

if __name__ == "__main__":
    main()