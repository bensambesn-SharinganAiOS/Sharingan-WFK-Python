#!/usr/bin/env python3
"""
Window Manager Simple - Sharingan OS
Gestion basique des fenêtres pour contrôle utilisateur
"""

import subprocess
import time

def run_cmd(cmd):
    """Exécute commande système"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip()
    except:
        return False, ''

class SimpleWindowManager:
    """Gestionnaire simple de fenêtres"""

    def __init__(self):
        self.selected_window = None

    def list_windows(self):
        """Liste les fenêtres"""
        print("📋 FENÊTRES OUVERTES:")
        try:
            success, output = run_cmd("wmctrl -l -x")
            if success:
                lines = output.strip().split('\n')
                for i, line in enumerate(lines, 1):
                    if line.strip():
                        parts = line.split(None, 3)
                        if len(parts) >= 4:
                            win_id, desktop, wm_class, title = parts[0], parts[1], parts[2], parts[3]
                            print(f"  {i}. [{win_id[:8]}] {title[:50]} - {wm_class}")
                return len(lines)
            else:
                print("  ❌ wmctrl non disponible")
                return 0
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            return 0

    def get_active(self):
        """Fenêtre active"""
        try:
            success, title = run_cmd("xdotool getactivewindow getwindowname")
            if success:
                print(f"🎯 ACTIVE: {title}")
                return title
            else:
                print("❌ Aucune fenêtre active")
                return None
        except:
            print("❌ Erreur récupération fenêtre active")
            return None

    def select_window(self):
        """Sélection manuelle"""
        count = self.list_windows()
        if count == 0:
            return False

        try:
            choice = int(input("Numéro de fenêtre: ")) - 1
            if 0 <= choice < count:
                # Pour simplifier, on utilise Alt+Tab pour naviguer
                print("🔄 Utilisez Alt+Tab pour sélectionner la fenêtre souhaitée")
                print("⏳ Attendez 3 secondes...")
                time.sleep(3)
                print("✅ Fenêtre sélectionnée")
                return True
            else:
                print("❌ Numéro invalide")
                return False
        except ValueError:
            print("❌ Entrée invalide")
            return False

    def scroll_down(self, steps=3):
        """Scroll vers le bas"""
        print(f"📜 Scroll DOWN x{steps}")
        for i in range(steps):
            run_cmd('xdotool click 5')
            time.sleep(0.2)
        print("✅ Scroll terminé")

    def scroll_up(self, steps=2):
        """Scroll vers le haut"""
        print(f"📜 Scroll UP x{steps}")
        for i in range(steps):
            run_cmd('xdotool click 4')
            time.sleep(0.2)
        print("✅ Scroll terminé")

    def click_comments(self):
        """Clic commentaires"""
        print("💬 Clic commentaires")
        run_cmd('xdotool mousemove_relative 150 80')
        time.sleep(0.3)
        run_cmd('xdotool click 1')
        print("✅ Clic effectué")

    def navigate(self, url=None):
        """Navigation"""
        if not url:
            url = input("URL: ")
        print(f"🔗 Navigation vers: {url}")

        # Ctrl+L
        run_cmd('xdotool key ctrl+l')
        time.sleep(0.5)

        # Effacer
        run_cmd('xdotool key ctrl+a')
        time.sleep(0.2)
        run_cmd('xdotool key Delete')
        time.sleep(0.2)

        # Taper URL
        run_cmd(f'xdotool type "{url}"')
        time.sleep(0.5)

        # Entrée
        run_cmd('xdotool key Return')
        print("✅ Navigation lancée")

def interactive_session():
    """Session interactive"""
    wm = SimpleWindowManager()

    print("🖼️ WINDOW MANAGER SIMPLE - SHARINGAN OS")
    print("=" * 45)
    print()

    actions = {
        '1': ('Lister fenêtres', lambda: wm.list_windows()),
        '2': ('Voir fenêtre active', lambda: wm.get_active()),
        '3': ('Sélectionner fenêtre', lambda: wm.select_window()),
        '4': ('Scroll down', lambda: wm.scroll_down(3)),
        '5': ('Scroll up', lambda: wm.scroll_up(2)),
        '6': ('Clic commentaires', lambda: wm.click_comments()),
        '7': ('Navigation', lambda: wm.navigate()),
        '8': ('Quitter', lambda: 'quit')
    }

    while True:
        print("\n🎯 ACTIONS DISPONIBLES:")
        for key, (desc, _) in actions.items():
            print(f"  {key}. {desc}")

        try:
            choice = input("\n👤 Choix: ").strip()

            if choice in actions:
                desc, action = actions[choice]
                print(f"\n🎬 {desc}...")

                result = action()
                if result == 'quit':
                    print("👋 Au revoir!")
                    break
            else:
                print("❌ Choix invalide")

        except KeyboardInterrupt:
            print("\n👋 Interruption - Au revoir!")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    interactive_session()