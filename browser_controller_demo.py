#!/usr/bin/env python3
"""
CONTRÔLEUR NAVIGATEUR SHARINGAN OS
Contrôle précis et fiable du navigateur Chrome
"""

import subprocess
import time
import os

class BrowserController:
    """Contrôleur avancé du navigateur Chrome"""

    def __init__(self):
        self.window_id = None
        self.find_chrome_window()

    def find_chrome_window(self):
        """Trouve et active la fenêtre Chrome"""
        try:
            result = subprocess.run([
                'xdotool', 'search', '--name', 'Google Chrome'
            ], capture_output=True, text=True)

            if result.returncode == 0 and result.stdout.strip():
                self.window_id = result.stdout.strip().split('\n')[0]
                # Activer la fenêtre
                subprocess.run(['xdotool', 'windowactivate', self.window_id])
                time.sleep(0.5)
                print(f"✅ Fenêtre Chrome activée: {self.window_id}")
                return True
            else:
                print("❌ Fenêtre Chrome non trouvée")
                return False
        except Exception as e:
            print(f"❌ Erreur recherche fenêtre: {e}")
            return False

    def navigate_to_url(self, url):
        """Navigation vers une URL spécifique"""
        if not self.window_id:
            print("❌ Fenêtre Chrome non disponible")
            return False

        try:
            # Sélectionner la barre d'adresse
            subprocess.run(['xdotool', 'key', '--window', self.window_id, 'ctrl+l'])
            time.sleep(0.5)

            # Effacer le contenu existant
            subprocess.run(['xdotool', 'key', '--window', self.window_id, 'ctrl+a'])
            time.sleep(0.2)
            subprocess.run(['xdotool', 'key', '--window', self.window_id, 'Delete'])
            time.sleep(0.2)

            # Saisir la nouvelle URL
            subprocess.run(['xdotool', 'type', '--window', self.window_id, url])
            time.sleep(0.5)

            # Valider avec Enter
            subprocess.run(['xdotool', 'key', '--window', self.window_id, 'Return'])
            time.sleep(2)  # Attendre le chargement

            print(f"✅ Navigation vers {url} réussie")
            return True

        except Exception as e:
            print(f"❌ Erreur navigation: {e}")
            return False

    def search_on_page(self, query):
        """Recherche dans la page (Ctrl+F)"""
        if not self.window_id:
            return False

        try:
            subprocess.run(['xdotool', 'key', '--window', self.window_id, 'ctrl+f'])
            time.sleep(0.5)
            subprocess.run(['xdotool', 'type', '--window', self.window_id, query])
            time.sleep(0.5)
            print(f"✅ Recherche '{query}' effectuée dans la page")
            return True
        except Exception as e:
            print(f"❌ Erreur recherche: {e}")
            return False

    def take_screenshot(self, filename=None):
        """Capture d'écran de la fenêtre active"""
        if not filename:
            timestamp = int(time.time())
            filename = f"screenshot_browser_{timestamp}.png"

        try:
            # Capture de la fenêtre active uniquement
            subprocess.run(['scrot', '-u', filename])
            print(f"✅ Capture d'écran sauvegardée: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Erreur capture: {e}")
            return None

    def open_new_tab(self):
        """Ouvre un nouvel onglet"""
        if not self.window_id:
            return False

        try:
            subprocess.run(['xdotool', 'key', '--window', self.window_id, 'ctrl+t'])
            time.sleep(1)
            print("✅ Nouvel onglet ouvert")
            return True
        except Exception as e:
            print(f"❌ Erreur nouvel onglet: {e}")
            return False

def demo_controleur_navigateur():
    """Démonstration du contrôleur de navigateur"""

    print("🌐 DÉMONSTRATION CONTRÔLEUR NAVIGATEUR SHARINGAN OS")
    print("=" * 55)

    controller = BrowserController()

    if not controller.window_id:
        print("❌ Impossible de contrôler le navigateur - Chrome non trouvé")
        return

    # Séquence de démonstration
    actions = [
        ("Navigation vers GitHub", lambda: controller.navigate_to_url("https://github.com/search?q=sharingan+os&type=repositories")),
        ("Ouverture nouvel onglet", lambda: controller.open_new_tab()),
        ("Navigation vers OWASP", lambda: controller.navigate_to_url("https://owasp.org/www-project-top-ten/")),
        ("Recherche 'injection'", lambda: controller.search_on_page("injection")),
        ("Capture d'écran", lambda: controller.take_screenshot("demo_sharingan_browser.png"))
    ]

    print("🎯 SÉQUENCE D'ACTIONS AUTOMATISÉES:")
    print("-" * 40)

    for i, (description, action) in enumerate(actions, 1):
        print(f"{i}. {description}...")
        success = action()
        status = "✅" if success else "❌"
        print(f"   {status} {description}")
        time.sleep(1)  # Pause entre les actions

    print("\n" + "=" * 55)
    print("🎉 DÉMONSTRATION TERMINÉE !")
    print("Le contrôleur de navigateur Sharingan OS permet:")
    print("• Navigation précise vers des URLs spécifiques")
    print("• Recherche dans les pages web")
    print("• Gestion des onglets")
    print("• Captures d'écran automatisées")
    print("• Contrôle physique fiable via xdotool")
    print("=" * 55)

if __name__ == "__main__":
    demo_controleur_navigateur()