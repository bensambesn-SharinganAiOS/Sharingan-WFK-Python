#!/usr/bin/env python3
"""
Window Context Manager - Sharingan OS
Gestion intelligente du contexte multi-fenêtres
Sélection, contrôle et navigation entre fenêtres
"""

import subprocess
import time
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class WindowContext:
    """Contexte d'une fenêtre"""
    id: str
    title: str
    type: str
    browser_type: Optional[str] = None
    url: Optional[str] = None
    last_active: float = 0
    actions_count: int = 0

class WindowContextManager:
    """Gestionnaire de contexte multi-fenêtres intelligent"""

    def __init__(self):
        self.contexts: Dict[str, WindowContext] = {}
        self.current_context: Optional[str] = None
        self.terminal_context = None
        self.auto_switch_enabled = True

        # Contexte spécial pour le terminal OC (interface utilisateur)
        self._init_terminal_context()

    def _init_terminal_context(self):
        """Initialise le contexte du terminal OC"""
        # Trouver le terminal OC
        try:
            result = subprocess.run(
                "ps aux | grep -E 'terminal|gnome-terminal' | grep -v grep | head -1",
                shell=True, capture_output=True, text=True
            )

            if result.returncode == 0:
                parts = result.stdout.strip().split()
                if len(parts) > 1:
                    pid = parts[1]
                    self.terminal_context = WindowContext(
                        id=f"terminal_{pid}",
                        title="OC Terminal",
                        type="terminal",
                        last_active=time.time()
                    )
                    print(f"✅ Terminal OC détecté: {self.terminal_context.id}")
        except:
            pass

    def scan_and_update_contexts(self) -> Dict:
        """Scan et mise à jour des contextes de fenêtres"""
        print("🔍 Scanning fenêtres et mise à jour contextes...")

        # Scan des fenêtres
        windows = self._scan_windows()

        # Mise à jour des contextes existants
        updated_contexts = []
        new_contexts = []

        for win in windows:
            win_id = win['id']
            win_title = win['title']
            win_type = win['type']

            if win_id in self.contexts:
                # Mise à jour contexte existant
                context = self.contexts[win_id]
                context.title = win_title
                context.last_active = time.time()
                updated_contexts.append(context)
            else:
                # Nouveau contexte
                context = WindowContext(
                    id=win_id,
                    title=win_title,
                    type=win_type,
                    last_active=time.time()
                )

                # Détection type de navigateur
                if 'youtube' in win_title.lower():
                    context.browser_type = 'youtube'
                elif 'facebook' in win_title.lower():
                    context.browser_type = 'facebook'
                elif 'chrome' in win_title.lower():
                    context.browser_type = 'chrome'
                elif 'firefox' in win_title.lower():
                    context.browser_type = 'firefox'

                self.contexts[win_id] = context
                new_contexts.append(context)

        # Nettoyage des contextes disparus
        current_win_ids = {win['id'] for win in windows}
        disappeared = [win_id for win_id in self.contexts.keys()
                      if win_id not in current_win_ids and
                      (not self.terminal_context or win_id != self.terminal_context.id)]

        for win_id in disappeared:
            print(f"🗑️ Fenêtre disparue: {self.contexts[win_id].title}")
            del self.contexts[win_id]

        return {
            'updated': updated_contexts,
            'new': new_contexts,
            'total': len(self.contexts)
        }

    def _scan_windows(self) -> List[Dict]:
        """Scan des fenêtres disponibles"""
        try:
            # Utilise wmctrl pour scanner
            result = subprocess.run(
                "wmctrl -l -x",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return self._scan_xdotool()

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

        except Exception as e:
            print(f"Erreur scan wmctrl: {e}")
            return self._scan_xdotool()

    def _scan_xdotool(self) -> List[Dict]:
        """Fallback avec xdotool"""
        try:
            result = subprocess.run(
                "xdotool search . getwindowname %@",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )

            windows = []
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        windows.append({
                            'id': f'window_{i}',
                            'title': line.strip(),
                            'type': 'unknown'
                        })

            return windows

        except Exception as e:
            print(f"Erreur scan xdotool: {e}")
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

    def select_context(self, context_description: str) -> bool:
        """Sélection d'un contexte par description"""
        print(f"🎯 Recherche contexte: {context_description}")

        # Recherche par mots-clés
        keywords = context_description.lower().split()

        candidates = []
        for win_id, context in self.contexts.items():
            title_lower = context.title.lower()
            type_lower = context.type.lower()

            # Score de matching
            score = 0
            for keyword in keywords:
                if keyword in title_lower or keyword in type_lower:
                    score += 1

            if score > 0:
                candidates.append((context, score))

        if not candidates:
            print(f"❌ Aucun contexte trouvé pour: {context_description}")
            return False

        # Sélection du meilleur candidat
        candidates.sort(key=lambda x: x[1], reverse=True)
        selected_context, score = candidates[0]

        print(f"✅ Contexte sélectionné: {selected_context.title} (score: {score})")

        # Activation de la fenêtre
        if self._activate_window(selected_context.id):
            self.current_context = selected_context.id
            selected_context.last_active = time.time()
            selected_context.actions_count += 1

            print(f"🎮 Contexte actif: {selected_context.title}")
            return True
        else:
            print("❌ Échec activation fenêtre")
            return False

    def _activate_window(self, window_id: str) -> bool:
        """Activation d'une fenêtre"""
        try:
            # Essai wmctrl
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

        except Exception as e:
            print(f"Erreur activation fenêtre: {e}")

        return False

    def execute_in_context(self, context_description: str, action: str, **params) -> Dict:
        """Exécution d'une action dans un contexte spécifique"""
        print(f"🎬 Action dans contexte '{context_description}': {action}")

        # Sélection du contexte
        if not self.select_context(context_description):
            return {'success': False, 'error': 'Contexte non trouvé'}

        # Exécution de l'action
        try:
            if action == 'scroll':
                return self._execute_scroll(**params)
            elif action == 'click':
                return self._execute_click(**params)
            elif action == 'navigate':
                return self._execute_navigate(**params)
            elif action == 'read':
                return self._execute_read(**params)
            else:
                return {'success': False, 'error': f'Action inconnue: {action}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _execute_scroll(self, direction='down', amount=1) -> Dict:
        """Scroll dans le contexte actif"""
        button = 5 if direction == 'down' else 4

        for _ in range(amount):
            result = subprocess.run(f'xdotool click {button}', shell=True, timeout=2)
            if result.returncode != 0:
                return {'success': False, 'error': 'Erreur scroll'}
            time.sleep(0.15)

        return {'success': True, 'action': 'scroll', 'direction': direction, 'amount': amount}

    def _execute_click(self, x=100, y=50) -> Dict:
        """Clic dans le contexte actif"""
        result1 = subprocess.run(f'xdotool mousemove {x} {y}', shell=True, timeout=2)
        if result1.returncode != 0:
            return {'success': False, 'error': 'Erreur déplacement'}

        time.sleep(0.2)
        result2 = subprocess.run('xdotool click 1', shell=True, timeout=2)

        if result2.returncode == 0:
            return {'success': True, 'action': 'click', 'position': f'{x},{y}'}
        else:
            return {'success': False, 'error': 'Erreur clic'}

    def _execute_navigate(self, url: str) -> Dict:
        """Navigation dans le contexte actif"""
        # Ctrl+L
        subprocess.run('xdotool key ctrl+l', shell=True, timeout=2)
        time.sleep(0.3)

        # Effacer
        subprocess.run('xdotool key ctrl+a', shell=True, timeout=2)
        time.sleep(0.2)
        subprocess.run('xdotool key Delete', shell=True, timeout=2)
        time.sleep(0.2)

        # Taper URL
        subprocess.run(f'xdotool type "{url}"', shell=True, timeout=3)
        time.sleep(0.3)

        # Entrée
        subprocess.run('xdotool key Return', shell=True, timeout=2)

        return {'success': True, 'action': 'navigate', 'url': url}

    def _execute_read(self) -> Dict:
        """Lecture dans le contexte actif (simulation)"""
        time.sleep(1.5)
        return {'success': True, 'action': 'read', 'content': 'Lecture simulée'}

    def switch_to_terminal(self) -> bool:
        """Basculement vers le terminal OC"""
        if self.terminal_context:
            print("🔄 Basculement vers terminal OC...")
            if self._activate_window(self.terminal_context.id):
                self.current_context = self.terminal_context.id
                self.terminal_context.last_active = time.time()
                print("✅ Terminal OC actif")
                return True
            else:
                print("❌ Échec basculement terminal")
                return False
        else:
            print("❌ Terminal OC non trouvé")
            return False

    def auto_context_message(self, message: str):
        """Envoi de message de confirmation à soi-même dans le terminal"""
        if self.switch_to_terminal():
            # Tape le message dans le terminal
            time.sleep(0.5)
            subprocess.run(f'xdotool type "echo \\"{message}\\""', shell=True, timeout=3)
            time.sleep(0.3)
            subprocess.run('xdotool key Return', shell=True, timeout=2)
            print(f"📝 Message auto: {message}")
            return True
        return False

    def get_context_status(self) -> Dict:
        """Statut des contextes"""
        contexts_list = []
        for win_id, context in self.contexts.items():
            contexts_list.append({
                'id': win_id,
                'title': context.title,
                'type': context.type,
                'browser_type': context.browser_type,
                'active': (win_id == self.current_context),
                'last_active': context.last_active,
                'actions_count': context.actions_count
            })

        return {
            'total_contexts': len(self.contexts),
            'current_context': self.current_context,
            'terminal_available': self.terminal_context is not None,
            'contexts': contexts_list
        }

def demo_multi_window_control():
    """Démo du contrôle multi-fenêtres"""
    print("🎭 DÉMO CONTRÔLE MULTI-FENÊTRES - SHARINGAN OS")
    print("=" * 55)
    print()

    wcm = WindowContextManager()

    # Scan initial
    print("1️⃣ SCAN INITIAL DES FENÊTRES:")
    scan_result = wcm.scan_and_update_contexts()
    print(f"   📊 Contextes totaux: {scan_result['total']}")
    print(f"   🆕 Nouveaux: {len(scan_result['new'])}")
    print(f"   🔄 Mis à jour: {len(scan_result['updated'])}")
    print()

    # Contrôle YouTube
    print("2️⃣ CONTRÔLE YOUTUBE:")
    result_yt = wcm.execute_in_context("youtube", "scroll", direction="down", amount=3)
    print(f"   {'✅' if result_yt['success'] else '❌'} {result_yt}")
    time.sleep(2)

    # Contrôle Facebook
    print("3️⃣ CONTRÔLE FACEBOOK:")
    result_fb = wcm.execute_in_context("facebook", "scroll", direction="down", amount=2)
    print(f"   {'✅' if result_fb['success'] else '❌'} {result_fb}")
    time.sleep(2)

    # Retour terminal avec message
    print("4️⃣ RETOUR TERMINAL AVEC CONFIRMATION:")
    message = "Navigation entre fenêtres YouTube et Facebook terminée avec succès"
    if wcm.auto_context_message(message):
        print("   ✅ Message de confirmation envoyé")
    else:
        print("   ❌ Échec envoi message")

    print()
    print("🎉 DÉMO TERMINÉE!")
    print("📊 STATUT FINAL:")
    status = wcm.get_context_status()
    print(f"   Contextes actifs: {status['total_contexts']}")
    print(f"   Terminal disponible: {status['terminal_available']}")

if __name__ == "__main__":
    demo_multi_window_control()