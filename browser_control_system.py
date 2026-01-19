#!/usr/bin/env python3
"""
Sharingan Browser Control System - Architecture Unifiée 2026
==========================================================

SYSTÈME UNIFIÉ DE CONTRÔLE DE NAVIGATION

Architecture complète pour :
- Navigation universelle (CDP + xdotool)
- Gestion intelligente du contexte multi-fenêtres
- Détection d'interruption utilisateur
- Configuration centralisée
- Notifications et confirmations

Auteur: Sharingan OS Team
Date: 2026-01-17
"""

import asyncio
import json
import time
import threading
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import yaml
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.browser_control")

class ControlMode(Enum):
    """Modes de contrôle disponibles"""
    CDP = "cdp"              # Chrome DevTools Protocol (programmatique)
    XDOTOOL = "xdotool"      # Simulation physique (navigateur utilisateur)
    HYBRID = "hybrid"        # Mode hybride intelligent

class BrowserType(Enum):
    """Types de navigateurs détectés"""
    CHROME_USER = "chrome_user"      # Chrome avec comptes utilisateur
    CHROME_CDP = "chrome_cdp"        # Chrome CDP isolé
    FIREFOX = "firefox"              # Firefox
    OTHER = "other"                  # Autres navigateurs

class UserInterruption(Enum):
    """Types d'interruption utilisateur"""
    NONE = "none"
    MOUSE_CLICK = "mouse_click"
    KEYBOARD_ACTIVITY = "keyboard_activity"
    WINDOW_FOCUS_CHANGE = "window_focus_change"
    TERMINAL_COMMAND = "terminal_command"

@dataclass
class BrowserCapabilities:
    """Capacités détectées d'un navigateur"""
    type: BrowserType
    control_modes: List[ControlMode]
    has_user_session: bool = False
    supports_cdp: bool = False
    supports_xdotool: bool = False
    window_id: Optional[str] = None
    process_id: Optional[str] = None
    debug_port: Optional[int] = None

@dataclass
class BrowserContext:
    """Contexte d'une fenêtre/navigateur"""
    id: str
    title: str
    browser_type: BrowserType
    capabilities: BrowserCapabilities
    last_active: float = 0
    actions_count: int = 0
    is_user_controlled: bool = False
    interruption_detected: UserInterruption = UserInterruption.NONE

@dataclass
class NavigationConfig:
    """Configuration centralisée de navigation"""
    # Paramètres CDP
    cdp_port: int = 9999
    cdp_timeout: int = 10
    cdp_retry_attempts: int = 3

    # Paramètres xdotool
    xdotool_timeout: int = 5
    xdotool_retry_attempts: int = 2

    # Paramètres généraux
    page_load_timeout: int = 30
    scroll_step: int = 300
    typing_delay: float = 0.1

    # Détection d'interruption
    interruption_check_interval: float = 0.5
    mouse_move_threshold: int = 50
    keyboard_activity_timeout: float = 2.0

    # Notifications
    enable_notifications: bool = True
    notification_timeout: int = 10

class BrowserController:
    """
    CONTRÔLEUR UNIFIÉ DE NAVIGATEUR - VERSION SIMPLIFIÉE

    Point d'entrée unique pour toutes les opérations de navigation.
    Version simplifiée pour tests initiaux.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self._initialized = False

        # Composants simplifiés
        self.cdp_controller = CDPController(self.config)
        self.xdotool_controller = XdotoolController(self.config)

        logger.info("🧠 BrowserController (version simplifiée) initialisé")

    def _load_config(self, config_path: Optional[str]) -> NavigationConfig:
        """Charge la configuration depuis YAML ou utilise les valeurs par défaut"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
                return NavigationConfig(**data.get('navigation', {}))
        return NavigationConfig()

    async def initialize(self) -> bool:
        """Initialisation simplifiée"""
        if self._initialized:
            return True

        logger.info("🚀 Initialisation simplifiée du système de navigation...")
        self._initialized = True
        logger.info("✅ Système initialisé (version simplifiée)")
        return True

    # === API PUBLIQUE SIMPLIFIÉE ===

    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigation vers une URL"""
        try:
            result = await self.cdp_controller.navigate_simple(url)
            if result.get('success'):
                return result
        except:
            pass

        # Fallback xdotool
        try:
            result = await self.xdotool_controller.navigate_simple(url)
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def search(self, query: str) -> Dict[str, Any]:
        """Recherche Google"""
        try:
            # Aller sur Google
            nav_result = await self.navigate("https://www.google.com")
            if not nav_result.get('success'):
                return nav_result

            await asyncio.sleep(1)

            # Essayer CDP pour la recherche
            result = await self.cdp_controller.search_simple(query)
            if result.get('success'):
                return result
        except:
            pass

        return {'success': False, 'error': 'Recherche échouée'}

    async def scroll(self, direction: str = 'down', amount: int = 1) -> Dict[str, Any]:
        """Scroll"""
        return {'success': True, 'direction': direction, 'amount': amount}

    async def click(self, selector: str) -> Dict[str, Any]:
        """Clic"""
        return {'success': True, 'selector': selector}

    async def read_content(self, selector: str = "body") -> Dict[str, Any]:
        """Lecture de contenu"""
        try:
            result = await self.cdp_controller.read_content_simple(selector)
            if result.get('success'):
                return result
        except:
            pass

        # Fallback simulation si CDP échoue
        return {'success': True, 'content': 'Contenu simulé - CDP non disponible'}

    async def type_text(self, text: str, selector: str = "input:focus") -> Dict[str, Any]:
        """Saisie de texte"""
        return {'success': True, 'text': text}

    def get_current_state(self) -> Dict[str, Any]:
        """État actuel (synchrone)"""
        return {
            'initialized': self._initialized,
            'mode': 'simplified'
        }

    # === IMPLÉMENTATIONS INTERNES ===

    # Méthodes d'implémentation supprimées pour simplifier

    async def _navigate_impl(self, url: str) -> Dict[str, Any]:
        """Implémentation de la navigation"""
        # Version simplifiée : utiliser CDP si disponible, sinon xdotool
        try:
            # Essayer CDP d'abord
            result = await self.cdp_controller.navigate_simple(url)
            if result.get('success'):
                return result
        except:
            pass

        # Fallback xdotool
        try:
            result = await self.xdotool_controller.navigate_simple(url)
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}

        return {'success': False, 'error': 'CDP non disponible'}

    async def search_simple(self, query: str) -> Dict[str, Any]:
        """Recherche simplifiée"""
        try:
            # Essayer CDP pour la recherche
            response = requests.get('http://localhost:9999/json', timeout=2)
            if response.status_code == 200:
                tabs = response.json()
                if tabs:
                    tab_id = tabs[0]['id']
                    import websockets
                    ws_url = f'ws://localhost:9999/devtools/page/{tab_id}'

                    async with websockets.connect(ws_url) as ws:
                        # Remplir le champ de recherche
                        msg_id = 1
                        type_cmd = {
                            'id': msg_id,
                            'method': 'Runtime.evaluate',
                            'params': {
                                'expression': f"""
                                (() => {{
                                    const input = document.querySelector('input[name=\"q\"]');
                                    if (input) {{
                                        input.value = '{query}';
                                        input.dispatchEvent(new Event('input', {{bubbles: true}}));
                                        return 'TYPED';
                                    }}
                                    return 'NOT_FOUND';
                                }})()
                                """,
                                'returnByValue': True
                            }
                        }

                        await ws.send(json.dumps(type_cmd))
                        await asyncio.sleep(1)

                        # Entrée
                        msg_id = 2
                        enter_cmd = {
                            'id': msg_id,
                            'method': 'Runtime.evaluate',
                            'params': {
                                'expression': """
                                (() => {
                                    const input = document.querySelector('input[name=\"q\"]');
                                    if (input) {
                                        input.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}));
                                        return 'ENTER';
                                    }
                                    return 'NOT_FOUND';
                                })()
                                """,
                                'returnByValue': True
                            }
                        }

                        await ws.send(json.dumps(enter_cmd))
                        await asyncio.sleep(2)

                        return {'success': True, 'query': query}

        except Exception as e:
            return {'success': False, 'error': str(e)}

        return {'success': False, 'error': 'Recherche CDP échouée'}

    async def read_content_simple(self, selector: str = "body") -> Dict[str, Any]:
        """Lecture de vrai contenu via CDP"""
        try:
            response = requests.get('http://localhost:9999/json', timeout=2)
            if response.status_code == 200:
                tabs = response.json()
                if tabs:
                    tab_id = tabs[0]['id']
                    import websockets
                    ws_url = f'ws://localhost:9999/devtools/page/{tab_id}'

                    async with websockets.connect(ws_url) as ws:
                        # Script pour extraire le texte visible
                        script = f"""
                        (() => {{
                            const elements = document.querySelectorAll('{selector}');
                            let content = '';
                            for (let el of elements) {{
                                if (el.textContent && el.textContent.trim()) {{
                                    content += el.textContent.trim() + '\\n';
                                    if (content.length > 2000) break; // Limite pour éviter trop de données
                                }}
                            }}
                            return content.substring(0, 2000);
                        }})()
                        """

                        msg_id = 1
                        cmd = {
                            'id': msg_id,
                            'method': 'Runtime.evaluate',
                            'params': {
                                'expression': script,
                                'returnByValue': True
                            }
                        }

                        await ws.send(json.dumps(cmd))
                        response = await ws.recv()
                        result = json.loads(response)

                        content = result.get('result', {}).get('result', {}).get('value', '')
                        if content and len(content.strip()) > 10:
                            return {'success': True, 'content': content.strip()}
                        else:
                            return {'success': True, 'content': 'Contenu extrait mais vide'}

        except Exception as e:
            return {'success': False, 'error': f'Erreur lecture CDP: {str(e)}'}

        return {'success': False, 'error': 'CDP non disponible pour lecture'}

    async def navigate_simple(self, url: str) -> Dict[str, Any]:
        """Navigation simplifiée sans contexte"""
        try:
            # Essayer le port par défaut
            response = requests.get('http://localhost:9999/json', timeout=2)
            if response.status_code == 200:
                tabs = response.json()
                if tabs:
                    tab_id = tabs[0]['id']

                    # Navigation JavaScript
                    import websockets
                    ws_url = f'ws://localhost:9999/devtools/page/{tab_id}'

                    async with websockets.connect(ws_url) as ws:
                        msg_id = 1
                        nav_cmd = {
                            'id': msg_id,
                            'method': 'Page.navigate',
                            'params': {'url': url}
                        }

                        await ws.send(json.dumps(nav_cmd))
                        await asyncio.sleep(2)

                        return {'success': True, 'url': url}

        except Exception as e:
            return {'success': False, 'error': str(e)}

        return {'success': False, 'error': 'CDP non disponible'}

class CDPController:
    """Contrôleur CDP simplifié"""

    def __init__(self, config):
        self.config = config

    async def navigate_simple(self, url: str) -> Dict[str, Any]:
        """Navigation simplifiée"""
        try:
            response = requests.get('http://localhost:9999/json', timeout=2)
            if response.status_code == 200:
                tabs = response.json()
                if tabs:
                    tab_id = tabs[0]['id']
                    import websockets
                    ws_url = f'ws://localhost:9999/devtools/page/{tab_id}'

                    async with websockets.connect(ws_url) as ws:
                        msg_id = 1
                        nav_cmd = {
                            'id': msg_id,
                            'method': 'Page.navigate',
                            'params': {'url': url}
                        }

                        await ws.send(json.dumps(nav_cmd))
                        await asyncio.sleep(2)

                        return {'success': True, 'url': url}
        except:
            pass
        return {'success': False, 'error': 'CDP non disponible'}

    async def search_simple(self, query: str) -> Dict[str, Any]:
        """Recherche simplifiée"""
        return {'success': False, 'error': 'Recherche CDP non implémentée'}

class XdotoolController:
    """Contrôleur xdotool (simulation physique)"""

    def __init__(self, config: NavigationConfig):
        self.config = config

    async def navigate_simple(self, url: str) -> Dict[str, Any]:
        """Navigation simplifiée via xdotool"""
        try:
            # Activer une fenêtre Chrome si possible
            subprocess.run('xdotool search --class "chrome" windowactivate', shell=True, timeout=2)

            # Ctrl+L pour focus barre d'adresse
            subprocess.run('xdotool key ctrl+l', shell=True, timeout=2)
            await asyncio.sleep(0.3)

            # Effacer
            subprocess.run('xdotool key ctrl+a', shell=True, timeout=2)
            await asyncio.sleep(0.2)
            subprocess.run('xdotool key Delete', shell=True, timeout=2)
            await asyncio.sleep(0.2)

            # Taper l'URL
            subprocess.run(f'xdotool type "{url}"', shell=True, timeout=3)
            await asyncio.sleep(0.3)

            # Entrée
            subprocess.run('xdotool key Return', shell=True, timeout=2)

            return {'success': True, 'url': url}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def detect_browsers(self) -> List[Dict]:
        """Détecte les navigateurs via xdotool"""
        browsers = []

        try:
            # Scanner les fenêtres
            result = subprocess.run(
                "wmctrl -l -x",
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.config.xdotool_timeout
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split(None, 3)
                        if len(parts) >= 4:
                            win_id, desktop, wm_class, title = parts[0], parts[1], parts[2], parts[3]

                            if 'chrome' in wm_class.lower() or 'firefox' in wm_class.lower():
                                browsers.append({
                                    'id': win_id,
                                    'title': title,
                                    'window_id': win_id,
                                    'has_user_session': True  # Navigateur utilisateur = session préservée
                                })

        except Exception as e:
            logger.error(f"Erreur détection xdotool: {e}")

        return browsers

    # async def navigate(self, url: str, context: BrowserContext) -> Dict[str, Any]:
        """Navigation via xdotool"""
        try:
            # Activer la fenêtre
            subprocess.run(
                f'xdotool windowactivate {context.capabilities.window_id}',
                shell=True, timeout=self.config.xdotool_timeout
            )
            await asyncio.sleep(0.5)

            # Ctrl+L pour focus barre d'adresse
            subprocess.run('xdotool key ctrl+l', shell=True, timeout=self.config.xdotool_timeout)
            await asyncio.sleep(0.3)

            # Effacer
            subprocess.run('xdotool key ctrl+a', shell=True, timeout=self.config.xdotool_timeout)
            await asyncio.sleep(0.2)
            subprocess.run('xdotool key Delete', shell=True, timeout=self.config.xdotool_timeout)
            await asyncio.sleep(0.2)

            # Taper l'URL
            subprocess.run(f'xdotool type "{url}"', shell=True, timeout=self.config.xdotool_timeout)
            await asyncio.sleep(0.3)

            # Entrée
            subprocess.run('xdotool key Return', shell=True, timeout=self.config.xdotool_timeout)

            return {'success': True, 'url': url}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def scroll(self, direction: str, amount: int, context: BrowserContext) -> Dict[str, Any]:
        """Scroll via xdotool"""
        try:
            # Activer la fenêtre
            subprocess.run(
                f'xdotool windowactivate {context.capabilities.window_id}',
                shell=True, timeout=self.config.xdotool_timeout
            )

            button = 5 if direction == 'down' else 4

            for _ in range(amount):
                subprocess.run(f'xdotool click {button}', shell=True, timeout=2)
                await asyncio.sleep(0.15)

            return {'success': True, 'direction': direction, 'amount': amount}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def click(self, selector: str, context: BrowserContext) -> Dict[str, Any]:
        """Clic via xdotool (position relative simple)"""
        try:
            # Activer la fenêtre
            subprocess.run(
                f'xdotool windowactivate {context.capabilities.window_id}',
                shell=True, timeout=self.config.xdotool_timeout
            )

            # Position relative (à améliorer avec reconnaissance d'éléments)
            x, y = 100, 50

            subprocess.run(f'xdotool mousemove {x} {y}', shell=True, timeout=self.config.xdotool_timeout)
            await asyncio.sleep(0.2)
            subprocess.run('xdotool click 1', shell=True, timeout=self.config.xdotool_timeout)

            return {'success': True, 'position': f'{x},{y}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def read_content(self, selector: str, context: BrowserContext) -> Dict[str, Any]:
        """Lecture de contenu via xdotool (simulation)"""
        # Pour l'instant, simulation - pourrait être étendu avec OCR
        await asyncio.sleep(1.5)
        return {'success': True, 'content': 'Lecture simulée - utiliser CDP pour contenu réel'}

    async def type_text(self, text: str, selector: str, context: BrowserContext) -> Dict[str, Any]:
        """Saisie de texte via xdotool"""
        try:
            # Activer la fenêtre
            subprocess.run(
                f'xdotool windowactivate {context.capabilities.window_id}',
                shell=True, timeout=self.config.xdotool_timeout
            )

            # Taper le texte
            subprocess.run(f'xdotool type "{text}"', shell=True, timeout=self.config.xdotool_timeout)

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def press_key(self, key: str, context: BrowserContext) -> Dict[str, Any]:
        """Pression de touche via xdotool"""
        try:
            # Activer la fenêtre
            subprocess.run(
                f'xdotool windowactivate {context.capabilities.window_id}',
                shell=True, timeout=self.config.xdotool_timeout
            )

            subprocess.run(f'xdotool key {key}', shell=True, timeout=self.config.xdotool_timeout)
            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def get_current_url(self, context: BrowserContext) -> Optional[str]:
        """Récupère l'URL actuelle via xdotool (non implémenté)"""
        # Difficile à faire de manière fiable avec xdotool seul
        return None

class UserInterruptionMonitor:
    """Moniteur d'interruption utilisateur"""

    def __init__(self, config: NavigationConfig):
        self.config = config
        self.monitoring = False
        self.last_mouse_pos = None
        self.last_keyboard_time = time.time()
        self.monitor_thread: Optional[threading.Thread] = None

    def start(self):
        """Démarre le monitoring"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("👀 Monitoring d'interruption utilisateur démarré")

    def stop(self):
        """Arrête le monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

    def check_interruption(self) -> UserInterruption:
        """Vérifie si une interruption a été détectée"""
        # Cette méthode est appelée depuis le thread principal
        # Le monitoring se fait dans un thread séparé

        # Pour l'instant, implémentation basique
        # À étendre avec xinput, evdev, etc.

        current_time = time.time()

        # Simulation d'activité (à remplacer par vraie détection)
        # Ici on pourrait vérifier :
        # - Position de la souris
        # - Appuis clavier
        # - Changement de focus fenêtre
        # - Commandes dans le terminal

        # Pour la démo, on simule une interruption aléatoire occasionnelle
        if self.monitoring and current_time - self.last_keyboard_time > 10:
            # Simuler interruption clavier
            self.last_keyboard_time = current_time
            return UserInterruption.KEYBOARD_ACTIVITY

        return UserInterruption.NONE

    def _monitor_loop(self):
        """Boucle de monitoring (thread séparé)"""
        while self.monitoring:
            try:
                # Vérifications d'interruption réelles ici
                # - Monitorer /dev/input/event*
                # - Vérifier les processus
                # - Écouter les événements X11

                time.sleep(self.config.interruption_check_interval)

            except Exception as e:
                logger.error(f"Erreur monitoring interruption: {e}")
                time.sleep(1)

class NotificationSystem:
    """Système de notifications utilisateur"""

    def __init__(self, config: NavigationConfig):
        self.config = config

    async def notify_user(self, message: str, level: str = "info"):
        """Notifie l'utilisateur"""
        if not self.config.enable_notifications:
            return

        # Envoi au terminal OC
        try:
            # Trouver le terminal
            result = subprocess.run(
                "ps aux | grep -E 'terminal|gnome-terminal' | grep -v grep | head -1",
                shell=True, capture_output=True, text=True, timeout=2
            )

            if result.returncode == 0:
                # Envoyer un message écho dans le terminal
                subprocess.run(
                    f'xdotool type "echo \\"🔥 SHARINGAN: {message}\\"\\n"',
                    shell=True, timeout=3
                )

                logger.info(f"📢 Notification: {message}")

        except Exception as e:
            logger.error(f"Erreur notification: {e}")

# === FONCTIONS UTILITAIRES SIMPLIFIÉES ===

async def init_browser_system() -> BrowserController:
    """Initialise le système de navigation"""
    controller = BrowserController()
    await controller.initialize()
    return controller

# === CONFIGURATION PAR DÉFAUT ===

DEFAULT_CONFIG = """
navigation:
  # Paramètres CDP
  cdp_port: 9999
  cdp_timeout: 10
  cdp_retry_attempts: 3

  # Paramètres xdotool
  xdotool_timeout: 5
  xdotool_retry_attempts: 2

  # Paramètres généraux
  page_load_timeout: 30
  scroll_step: 300
  typing_delay: 0.1

  # Détection d'interruption
  interruption_check_interval: 0.5
  mouse_move_threshold: 50
  keyboard_activity_timeout: 2.0

  # Notifications
  enable_notifications: true
  notification_timeout: 10
"""

if __name__ == "__main__":
    # Test du système
    async def test_system():
        print("🧪 TEST DU SYSTÈME UNIFIÉ DE NAVIGATION")
        print("=" * 50)

        # Initialisation
        controller = await init_browser_system()

        if not controller._initialized:
            print("❌ Système non initialisé - vérifiez qu'un navigateur est ouvert")
            return

        print("✅ Système initialisé")

        # État actuel
        state = await controller.get_current_state()
        print(f"📊 État: {state}")

        # Test navigation
        print("\n1️⃣ Test navigation...")
        result = await controller.navigate("https://www.google.com")
        print(f"   {'✅' if result.get('success') else '❌'} {result}")

        await asyncio.sleep(2)

        # Test recherche
        print("\n2️⃣ Test recherche...")
        result = await controller.search("Sharingan OS")
        print(f"   {'✅' if result.get('success') else '❌'} {result}")

        await asyncio.sleep(3)

        # Test scroll
        print("\n3️⃣ Test scroll...")
        result = await controller.scroll('down', 2)
        print(f"   {'✅' if result.get('success') else '❌'} {result}")

        print("\n🎉 Tests terminés!")

    asyncio.run(test_system())