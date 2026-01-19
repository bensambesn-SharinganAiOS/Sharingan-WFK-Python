#!/usr/bin/env python3
"""
Interface Autonome Multi-Fenêtres - Sharingan OS
Contrôle complet de plusieurs fenêtres avec contexte intelligent
"""

import subprocess
import time
import random
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class WindowContext:
    """Contexte d'une fenêtre"""
    id: str
    title: str
    type: str
    browser_type: Optional[str] = None
    last_active: float = 0
    actions_count: int = 0

class IntegratedWindowManager:
    """Gestionnaire intégré de fenêtres multi-contextes"""

    def __init__(self):
        self.contexts: Dict[str, WindowContext] = {}
        self.current_context: Optional[str] = None
        self.terminal_context = None
        self._init_terminal_context()

    def _init_terminal_context(self):
        """Initialise le contexte terminal OC"""
        try:
            result = subprocess.run(
                "ps aux | grep -E 'terminal|gnome-terminal' | grep -v grep | head -1",
                shell=True, capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                pid = result.stdout.strip().split()[1]
                self.terminal_context = WindowContext(
                    id=f"terminal_{pid}",
                    title="Terminal OC",
                    type="terminal"
                )
        except:
            pass

    def run_cmd(self, cmd):
        """Exécute commande système"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            return result.returncode == 0, result.stdout.strip()
        except:
            return False, ''

    def scan_windows(self) -> List[Dict]:
        """Scan des fenêtres"""
        try:
            result = subprocess.run(
                "wmctrl -l -x",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return []

            windows = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split(None, 3)
                    if len(parts) >= 4:
                        win_id, desktop, wm_class, title = parts[0], parts[1], parts[2], parts[3]
                        win_type = self._classify_window(wm_class, title)

                        windows.append({
                            'id': win_id,
                            'title': title,
                            'type': win_type,
                            'class': wm_class
                        })

            return windows
        except:
            return []

    def _classify_window(self, wm_class: str, title: str) -> str:
        """Classification des fenêtres"""
        wm_lower = wm_class.lower()
        title_lower = title.lower()

        if 'chrome' in wm_lower or 'chromium' in wm_lower:
            return 'browser_chrome'
        elif 'firefox' in wm_lower:
            return 'browser_firefox'
        elif 'terminal' in wm_lower or 'xterm' in wm_lower:
            return 'terminal'
        elif 'youtube' in title_lower:
            return 'browser_youtube'
        elif 'facebook' in title_lower:
            return 'browser_facebook'
        else:
            return 'application'

    def update_contexts(self):
        """Met à jour les contextes de fenêtres"""
        windows = self.scan_windows()

        # Mise à jour contextes existants
        for win in windows:
            win_id = win['id']
            if win_id in self.contexts:
                self.contexts[win_id].title = win['title']
                self.contexts[win_id].last_active = time.time()
            else:
                context = WindowContext(
                    id=win_id,
                    title=win['title'],
                    type=win['type'],
                    last_active=time.time()
                )
                if 'youtube' in win['title'].lower():
                    context.browser_type = 'youtube'
                elif 'facebook' in win['title'].lower():
                    context.browser_type = 'facebook'
                self.contexts[win_id] = context

        # Nettoyage disparus
        current_ids = {win['id'] for win in windows}
        disappeared = [win_id for win_id in self.contexts.keys()
                      if win_id not in current_ids and
                      (not self.terminal_context or win_id != self.terminal_context.id)]
        for win_id in disappeared:
            del self.contexts[win_id]

        return len(self.contexts)

    def select_context(self, description: str) -> bool:
        """Sélectionne un contexte par description"""
        candidates = []
        for win_id, context in self.contexts.items():
            title_lower = context.title.lower()
            type_lower = context.type.lower()

            score = sum(1 for keyword in description.lower().split()
                       if keyword in title_lower or keyword in type_lower)

            if score > 0:
                candidates.append((context, score))

        if not candidates:
            return False

        candidates.sort(key=lambda x: x[1], reverse=True)
        selected_context = candidates[0][0]

        # Activation
        success = self._activate_window(selected_context.id)
        if success:
            self.current_context = selected_context.id
            selected_context.last_active = time.time()
            selected_context.actions_count += 1
        return success

    def _activate_window(self, window_id: str) -> bool:
        """Active une fenêtre"""
        try:
            result = subprocess.run(
                f"wmctrl -i -a {window_id}",
                shell=True,
                capture_output=True,
                timeout=3
            )
            if result.returncode == 0:
                time.sleep(0.5)
                return True

            # Fallback xdotool
            result2 = subprocess.run(
                f"xdotool windowactivate {window_id}",
                shell=True,
                capture_output=True,
                timeout=3
            )
            if result2.returncode == 0:
                time.sleep(0.5)
                return True

        except:
            pass
        return False

    def execute_action(self, context_desc: str, action: str, **params) -> Dict:
        """Exécute une action dans un contexte"""
        if not self.select_context(context_desc):
            return {'success': False, 'error': 'Contexte non trouvé'}

        try:
            if action == 'scroll':
                return self._scroll(**params)
            elif action == 'click':
                return self._click(**params)
            elif action == 'navigate':
                return self._navigate(**params)
            else:
                return {'success': False, 'error': f'Action inconnue: {action}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _scroll(self, direction='down', amount=1) -> Dict:
        """Scroll"""
        button = 5 if direction == 'down' else 4
        for _ in range(amount):
            subprocess.run(f'xdotool click {button}', shell=True, timeout=2)
            time.sleep(0.15)
        return {'success': True, 'action': 'scroll', 'direction': direction, 'amount': amount}

    def _click(self, x=100, y=50) -> Dict:
        """Clic"""
        subprocess.run(f'xdotool mousemove {x} {y}', shell=True, timeout=2)
        time.sleep(0.2)
        result = subprocess.run('xdotool click 1', shell=True, capture_output=True, timeout=2)
        return {
            'success': result.returncode == 0,
            'action': 'click',
            'position': f'{x},{y}'
        }

    def _navigate(self, url: str) -> Dict:
        """Navigation"""
        subprocess.run('xdotool key ctrl+l', shell=True, timeout=2)
        time.sleep(0.3)
        subprocess.run('xdotool key ctrl+a', shell=True, timeout=2)
        time.sleep(0.2)
        subprocess.run('xdotool key Delete', shell=True, timeout=2)
        time.sleep(0.2)
        subprocess.run(f'xdotool type "{url}"', shell=True, timeout=3)
        time.sleep(0.3)
        subprocess.run('xdotool key Return', shell=True, timeout=2)
        return {'success': True, 'action': 'navigate', 'url': url}

    def switch_to_terminal(self) -> bool:
        """Bascule vers terminal"""
        if self.terminal_context and self._activate_window(self.terminal_context.id):
            self.current_context = self.terminal_context.id
            message = f"Navigation fenêtres terminée - {int(time.time())}"
            subprocess.run(f'xdotool type "echo \\"{message}\\"\\n"', shell=True, timeout=3)
            return True
        return False

    def get_status(self) -> Dict:
        """Statut des contextes"""
        return {
            'total_contexts': len(self.contexts),
            'current_context': self.current_context,
            'terminal_available': self.terminal_context is not None,
            'contexts': [
                {
                    'id': ctx.id,
                    'title': ctx.title,
                    'type': ctx.type,
                    'browser_type': ctx.browser_type,
                    'active': ctx.id == self.current_context,
                    'actions_count': ctx.actions_count
                }
                for ctx in self.contexts.values()
            ]
        }

def interactive_multi_window():
    """Interface interactive multi-fenêtres"""
    print("🎪 SHARINGAN OS - CONTRÔLE MULTI-FENÊTRES")
    print("Gestion intelligente de contexte")
    print("=" * 45)
    print()

    wm = IntegratedWindowManager()

    # Scan initial
    print("🔍 Initialisation...")
    total = wm.update_contexts()
    print(f"✅ {total} contextes détectés")
    print()

    while True:
        print("\n🎯 COMMANDES:")
        print("  list     - Lister contextes")
        print("  status   - Statut détaillé")
        print("  youtube  - Contrôler YouTube")
        print("  facebook - Contrôler Facebook")
        print("  control  - Contrôle personnalisé")
        print("  terminal - Retour terminal OC")
        print("  demo     - Démo automatique")
        print("  quit     - Quitter")

        try:
            cmd = input("\n👤 Commande: ").strip().lower()

            if cmd == 'list':
                status = wm.get_status()
                print(f"\n📋 CONTEXTES ({status['total_contexts']}):")
                for ctx in status['contexts']:
                    active = " ⭐ ACTIVE" if ctx['active'] else ""
                    browser = f" ({ctx['browser_type']})" if ctx['browser_type'] else ""
                    print(f"  • {ctx['title'][:50]}{browser}{active}")

            elif cmd == 'status':
                status = wm.get_status()
                print(f"\n📊 STATUT:")
                print(f"   Contextes: {status['total_contexts']}")
                print(f"   Terminal: {'✅' if status['terminal_available'] else '❌'}")
                print(f"   Actif: {status['current_context'] or 'Aucun'}")

            elif cmd == 'youtube':
                print("\n🎥 YOUTUBE:")
                action = input("Action (scroll/commentaires/navigate): ").strip().lower()

                if action == 'scroll':
                    result = wm.execute_action('youtube', 'scroll', direction='down', amount=3)
                elif action == 'commentaires':
                    result = wm.execute_action('youtube', 'click', x=150, y=80)
                elif action == 'navigate':
                    url = input("URL YouTube: ").strip()
                    result = wm.execute_action('youtube', 'navigate', url=url)
                else:
                    print("❌ Action inconnue")
                    continue

                print(f"{'✅' if result['success'] else '❌'} {result}")

            elif cmd == 'facebook':
                print("\n📘 FACEBOOK:")
                action = input("Action (scroll/publications/navigate): ").strip().lower()

                if action == 'scroll':
                    result = wm.execute_action('facebook', 'scroll', direction='down', amount=2)
                elif action == 'publications':
                    result = wm.execute_action('facebook', 'click', x=200, y=150)
                elif action == 'navigate':
                    url = input("URL Facebook: ").strip()
                    result = wm.execute_action('facebook', 'navigate', url=url)
                else:
                    print("❌ Action inconnue")
                    continue

                print(f"{'✅' if result['success'] else '❌'} {result}")

            elif cmd == 'control':
                print("\n🎮 CONTRÔLE PERSONNALISÉ:")
                context = input("Contexte: ").strip()
                action = input("Action (scroll/click/navigate): ").strip().lower()

                if action == 'scroll':
                    direction = input("Direction (down/up): ").strip().lower() or 'down'
                    amount = int(input("Quantité: ") or 1)
                    result = wm.execute_action(context, 'scroll', direction=direction, amount=amount)
                elif action == 'click':
                    x = int(input("X: ") or 100)
                    y = int(input("Y: ") or 50)
                    result = wm.execute_action(context, 'click', x=x, y=y)
                elif action == 'navigate':
                    url = input("URL: ").strip()
                    result = wm.execute_action(context, 'navigate', url=url)
                else:
                    print("❌ Action inconnue")
                    continue

                print(f"{'✅' if result['success'] else '❌'} {result}")

            elif cmd == 'terminal':
                print("\n💻 RETOUR TERMINAL:")
                if wm.switch_to_terminal():
                    print("✅ Terminal actif avec message de confirmation")
                else:
                    print("❌ Échec retour terminal")

            elif cmd == 'demo':
                print("\n🎭 DÉMO MULTI-FENÊTRES:")
                print("YouTube → Facebook → Terminal")

                # YouTube
                print("1️⃣ YouTube...")
                yt_result = wm.execute_action('youtube', 'scroll', direction='down', amount=2)
                print(f"   {'✅' if yt_result['success'] else '❌'} Scroll YouTube")

                time.sleep(2)

                # Facebook
                print("2️⃣ Facebook...")
                fb_result = wm.execute_action('facebook', 'scroll', direction='down', amount=2)
                print(f"   {'✅' if fb_result['success'] else '❌'} Scroll Facebook")

                time.sleep(2)

                # Terminal
                print("3️⃣ Terminal...")
                if wm.switch_to_terminal():
                    print("   ✅ Retour terminal avec confirmation")
                else:
                    print("   ❌ Échec terminal")

                print("🎉 Demo terminée!")

            elif cmd == 'quit':
                print("👋 Au revoir!")
                break

            else:
                print("❌ Commande inconnue")

        except KeyboardInterrupt:
            print("\n👋 Interruption - Au revoir!")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")

def main():
    try:
        interactive_multi_window()
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    main()