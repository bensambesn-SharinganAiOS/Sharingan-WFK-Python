#!/usr/bin/env python3
"""
Window Manager Automatique - Sharingan OS
Contrôle automatique des fenêtres sans interface utilisateur
Utilisable par les IA et les scripts automatiques
"""

import subprocess
import time
import sys
import os

def run_cmd(cmd, timeout=5):
    """Exécute commande système avec timeout"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)

class AutomatedWindowManager:
    """Gestionnaire automatique de fenêtres pour IA"""

    def __init__(self):
        self.selected_window = None
        self.target_context = None  # Facebook, YouTube, etc.

    def get_active_window_info(self):
        """Récupère les infos de la fenêtre active"""
        try:
            # ID de la fenêtre active
            success_id, win_id = run_cmd("xdotool getactivewindow")
            if not success_id:
                return None

            # Nom de la fenêtre active
            success_name, win_name = run_cmd("xdotool getactivewindow getwindowname")
            if not success_name:
                return None

            return {
                'id': win_id.strip(),
                'name': win_name.strip(),
                'is_target': self._is_target_window(win_name) if self.target_context else False
            }
        except:
            return None

    def _is_target_window(self, window_name):
        """Vérifie si c'est la fenêtre cible"""
        if not self.target_context:
            return False

        name_lower = window_name.lower()
        target_lower = self.target_context.lower()

        return target_lower in name_lower

    def verify_target_active(self):
        """Vérifie que la fenêtre cible est active"""
        active = self.get_active_window_info()
        if not active:
            return False, "Aucune fenêtre active"

        if not active['is_target']:
            return False, f"Fenêtre active '{active['name']}' n'est pas {self.target_context}"

        return True, f"✅ {self.target_context} actif: {active['name']}"

    def ensure_target_active(self):
        """S'assure que la fenêtre cible est active"""
        # Vérification rapide
        is_active, msg = self.verify_target_active()
        if is_active:
            return True

        print(f"⚠️ {msg} - Activation en cours...")

        # Recherche et activation
        if self.target_context == "facebook":
            return self.select_facebook()
        elif self.target_context == "youtube":
            return self.select_youtube()
        else:
            win_id = self.find_window_by_name(self.target_context)
            if win_id:
                return self.activate_window(win_id)

        return False

    def find_window_by_name(self, name_pattern):
        """Trouve une fenêtre par nom"""
        try:
            success, output = run_cmd("wmctrl -l -x")
            if success:
                for line in output.strip().split('\n'):
                    if line.strip() and name_pattern.lower() in line.lower():
                        parts = line.split(None, 1)
                        if parts:
                            return parts[0]  # Window ID
        except:
            pass
        return None

    def activate_window(self, window_id):
        """Active une fenêtre"""
        # Essai wmctrl
        success, _ = run_cmd(f"wmctrl -i -a {window_id}")
        if success:
            time.sleep(0.5)
            return True

        # Fallback xdotool
        success, _ = run_cmd(f"xdotool windowactivate {window_id}")
        if success:
            time.sleep(0.5)
            return True

        return False

    def select_facebook(self):
        """Sélection automatique de Facebook"""
        self.target_context = "facebook"
        win_id = self.find_window_by_name("facebook")
        if win_id and self.activate_window(win_id):
            self.selected_window = win_id
            return True
        return False

    def select_youtube(self):
        """Sélection automatique de YouTube"""
        self.target_context = "youtube"
        win_id = self.find_window_by_name("youtube")
        if win_id and self.activate_window(win_id):
            self.selected_window = win_id
            return True
        return False

    def scroll_down(self, steps=1):
        """Scroll vers le bas avec vérification"""
        if not self.ensure_target_active():
            print(f"❌ Impossible d'activer {self.target_context}")
            return False

        print(f"📜 Scroll DOWN x{steps} sur {self.target_context}")
        for _ in range(steps):
            run_cmd('xdotool click 5')
            time.sleep(0.15)
        return True

    def scroll_up(self, steps=1):
        """Scroll vers le haut avec vérification"""
        if not self.ensure_target_active():
            print(f"❌ Impossible d'activer {self.target_context}")
            return False

        print(f"📜 Scroll UP x{steps} sur {self.target_context}")
        for _ in range(steps):
            run_cmd('xdotool click 4')
            time.sleep(0.15)
        return True

    def click_comments(self):
        """Clic sur commentaires avec vérification"""
        if not self.ensure_target_active():
            print(f"❌ Impossible d'activer {self.target_context}")
            return False

        print(f"💬 Clic commentaires sur {self.target_context}")
        run_cmd('xdotool mousemove_relative 150 80')
        time.sleep(0.3)
        run_cmd('xdotool click 1')
        return True

    def continuous_scroll_facebook(self, duration_seconds=None):
        """Scroll continu sur Facebook avec vérifications"""
        if not self.select_facebook():
            print("❌ Impossible de sélectionner Facebook")
            return False

        print("📘 SCROLL CONTINU FACEBOOK - MODE IA")
        print("====================================")
        print("Scroll automatique avec vérifications de fenêtre")
        print()

        scroll_count = 0
        start_time = time.time()
        last_check = 0

        try:
            while True:
                # Vérifier durée si spécifiée
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    break

                # Vérification périodique que Facebook est toujours actif (toutes les 10 scrolls)
                if scroll_count % 10 == 0:
                    is_active, msg = self.verify_target_active()
                    if not is_active:
                        print(f"⚠️ {msg} - Réactivation...")
                        if not self.ensure_target_active():
                            print("❌ Impossible de maintenir Facebook actif")
                            break

                # Scroll avec vérification
                success = self.scroll_down(1)
                if not success:
                    print("❌ Échec scroll - arrêt")
                    break

                scroll_count += 1

                # Affichage discret
                if scroll_count % 5 == 0:
                    print(f"📜 {scroll_count} scrolls...")

                # Pause variable
                pause = 1.5 + (scroll_count % 3) * 0.3
                time.sleep(pause)

        except KeyboardInterrupt:
            pass

        print(f"\n🎉 Scroll terminé: {scroll_count} actions")
        return True

    def continuous_scroll_youtube(self, duration_seconds=None):
        """Scroll continu sur YouTube avec vérifications"""
        if not self.select_youtube():
            print("❌ Impossible de sélectionner YouTube")
            return False

        print("🎥 SCROLL CONTINU YOUTUBE - MODE IA")
        print("===================================")
        print("Scroll automatique avec vérifications de fenêtre")
        print()

        scroll_count = 0
        start_time = time.time()

        try:
            while True:
                # Vérifier durée si spécifiée
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    break

                # Vérification périodique que YouTube est toujours actif (toutes les 10 scrolls)
                if scroll_count % 10 == 0:
                    is_active, msg = self.verify_target_active()
                    if not is_active:
                        print(f"⚠️ {msg} - Réactivation...")
                        if not self.ensure_target_active():
                            print("❌ Impossible de maintenir YouTube actif")
                            break

                # Scroll avec vérification
                success = self.scroll_down(1)
                if not success:
                    print("❌ Échec scroll - arrêt")
                    break

                scroll_count += 1

                # Affichage discret
                if scroll_count % 5 == 0:
                    print(f"📜 {scroll_count} scrolls...")

                # Pause variable
                pause = 1.5 + (scroll_count % 3) * 0.3
                time.sleep(pause)

        except KeyboardInterrupt:
            pass

        print(f"\n🎉 Scroll YouTube terminé: {scroll_count} actions")
        return True

def main():
    """Fonction principale pour usage IA"""
    if len(sys.argv) < 2:
        print("Usage: python3 automated_window_manager.py <commande> [params]")
        print()
        print("Commandes:")
        print("  facebook_scroll [duration_seconds]  - Scroll continu Facebook")
        print("  youtube_scroll [duration_seconds]   - Scroll continu YouTube")
        print("  facebook_click_comments             - Clic commentaires Facebook")
        print("  youtube_click_comments              - Clic commentaires YouTube")
        print("  check_active                        - Vérifier fenêtre active")
        print()
        print("Exemples:")
        print("  python3 automated_window_manager.py facebook_scroll")
        print("  python3 automated_window_manager.py facebook_scroll 30")
        return

    wm = AutomatedWindowManager()
    command = sys.argv[1]

    if command == "facebook_scroll":
        wm.target_context = "facebook"
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else None
        wm.continuous_scroll_facebook(duration)

    elif command == "youtube_scroll":
        wm.target_context = "youtube"
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else None
        wm.continuous_scroll_youtube(duration)

    elif command == "facebook_click_comments":
        wm.target_context = "facebook"
        if wm.ensure_target_active():
            wm.click_comments()
            print("✅ Commentaires Facebook cliqués")
        else:
            print("❌ Impossible d'activer Facebook")

    elif command == "youtube_click_comments":
        wm.target_context = "youtube"
        if wm.ensure_target_active():
            wm.click_comments()
            print("✅ Commentaires YouTube cliqués")
        else:
            print("❌ Impossible d'activer YouTube")

    elif command == "check_active":
        active = wm.get_active_window_info()
        if active:
            target_status = " (CIBLE)" if active['is_target'] and wm.target_context else ""
            print(f"🎯 Active: {active['name']}{target_status}")
        else:
            print("❌ Aucune fenêtre active")

    else:
        print(f"❌ Commande inconnue: {command}")

if __name__ == "__main__":
    main()