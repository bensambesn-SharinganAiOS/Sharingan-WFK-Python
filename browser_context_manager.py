#!/usr/bin/env python3
"""
Browser Context Manager - Sharingan OS
=====================================

Gestion intelligente et générique du contexte multi-fenêtres.
Remplace tous les gestionnaires spécialisés (window_context_manager.py, multi_window_interface.py, etc.)

Fonctionnalités:
- Détection automatique des fenêtres
- Gestion de contexte intelligent
- Basculement fluide
- Suivi d'activité
- Notifications utilisateur
"""

import subprocess
import time
import asyncio
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger("sharingan.browser_context")

class ContextType(Enum):
    """Types de contextes détectés"""
    BROWSER_CHROME = "browser_chrome"
    BROWSER_FIREFOX = "browser_firefox"
    BROWSER_YOUTUBE = "browser_youtube"
    BROWSER_FACEBOOK = "browser_facebook"
    BROWSER_GOOGLE = "browser_google"
    BROWSER_WIKIPEDIA = "browser_wikipedia"
    TERMINAL = "terminal"
    APPLICATION = "application"
    UNKNOWN = "unknown"

class ContextState(Enum):
    """États possibles d'un contexte"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    HIDDEN = "hidden"
    CLOSED = "closed"

@dataclass
class WindowInfo:
    """Informations sur une fenêtre"""
    id: str
    title: str
    class_name: str
    pid: Optional[int] = None
    geometry: Optional[str] = None
    state: ContextState = ContextState.INACTIVE

@dataclass
class BrowserContext:
    """Contexte de navigateur complet"""
    id: str
    title: str
    type: ContextType
    window_info: WindowInfo
    capabilities: List[str] = field(default_factory=list)
    last_active: float = 0
    actions_count: int = 0
    url: Optional[str] = None
    is_user_controlled: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_browser(self) -> bool:
        """Vérifie si c'est un contexte navigateur"""
        return self.type.value.startswith('browser_')

    @property
    def browser_name(self) -> Optional[str]:
        """Retourne le nom du navigateur"""
        if not self.is_browser:
            return None
        return self.type.value.replace('browser_', '')

class ContextEvent(Enum):
    """Événements de contexte"""
    CREATED = "created"
    ACTIVATED = "activated"
    DEACTIVATED = "deactivated"
    CLOSED = "closed"
    TITLE_CHANGED = "title_changed"
    URL_CHANGED = "url_changed"

class ContextEventHandler:
    """Gestionnaire d'événements de contexte"""

    def __init__(self):
        self.handlers: Dict[ContextEvent, List[Callable]] = {}

    def register(self, event: ContextEvent, handler: Callable):
        """Enregistre un gestionnaire d'événement"""
        if event not in self.handlers:
            self.handlers[event] = []
        self.handlers[event].append(handler)

    def unregister(self, event: ContextEvent, handler: Callable):
        """Désenregistre un gestionnaire"""
        if event in self.handlers:
            self.handlers[event].remove(handler)

    def emit(self, event: ContextEvent, context: BrowserContext, **kwargs):
        """Émet un événement"""
        if event in self.handlers:
            for handler in self.handlers[event]:
                try:
                    handler(context, **kwargs)
                except Exception as e:
                    logger.error(f"Erreur dans le gestionnaire d'événement {event}: {e}")

class BrowserContextManager:
    """
    GESTIONNAIRE UNIFIÉ DE CONTEXTE MULTI-FENÊTRES

    Point central pour :
    - Détecter et suivre toutes les fenêtres
    - Gérer les contextes de manière intelligente
    - Basculer entre contextes
    - Notifier des changements
    - Maintenir l'état des sessions utilisateur
    """

    def __init__(self, config_path: Optional[str] = None):
        self.contexts: Dict[str, BrowserContext] = {}
        self.current_context_id: Optional[str] = None
        self.terminal_context_id: Optional[str] = None

        # Événements
        self.events = ContextEventHandler()
        self._setup_default_handlers()

        # Monitoring
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_scan_time = 0
        self.scan_interval = 1.0  # secondes

        # Cache pour éviter les scans répétés
        self._last_windows_snapshot: List[Dict] = []

        logger.info("🧠 BrowserContextManager initialisé")

    def _setup_default_handlers(self):
        """Configure les gestionnaires d'événements par défaut"""

        # Log les activations
        self.events.register(ContextEvent.ACTIVATED, lambda ctx, **kw:
            logger.info(f"🎯 Contexte activé: {ctx.title} ({ctx.type.value})"))

        # Log les fermetures
        self.events.register(ContextEvent.CLOSED, lambda ctx, **kw:
            logger.info(f"❌ Contexte fermé: {ctx.title}"))

        # Mise à jour du contexte actuel
        self.events.register(ContextEvent.ACTIVATED, self._on_context_activated)
        self.events.register(ContextEvent.CLOSED, self._on_context_closed)

    def _on_context_activated(self, context: BrowserContext, **kwargs):
        """Gestionnaire d'activation de contexte"""
        self.current_context_id = context.id
        context.last_active = time.time()
        context.actions_count += 1

    def _on_context_closed(self, context: BrowserContext, **kwargs):
        """Gestionnaire de fermeture de contexte"""
        if context.id in self.contexts:
            del self.contexts[context.id]

        if self.current_context_id == context.id:
            self.current_context_id = None

    # === DÉTECTION ET SCAN ===

    def start_monitoring(self):
        """Démarre le monitoring automatique des contextes"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("👀 Monitoring de contextes démarré")

    def stop_monitoring(self):
        """Arrête le monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

    def _monitoring_loop(self):
        """Boucle de monitoring en arrière-plan"""
        while self.monitoring:
            try:
                current_time = time.time()
                if current_time - self.last_scan_time >= self.scan_interval:
                    self.scan_and_update_contexts()
                    self.last_scan_time = current_time

                time.sleep(self.scan_interval)

            except Exception as e:
                logger.error(f"Erreur dans la boucle de monitoring: {e}")
                time.sleep(2)

    def scan_and_update_contexts(self) -> Dict[str, Any]:
        """
        Scan complet des fenêtres et mise à jour des contextes

        Returns:
            Statistiques du scan
        """
        try:
            # Scan des fenêtres
            windows = self._scan_windows()

            # Éviter les scans inutiles
            if windows == self._last_windows_snapshot:
                return {'status': 'unchanged', 'total_contexts': len(self.contexts)}

            self._last_windows_snapshot = windows

            # Statistiques
            stats = {
                'scanned_windows': len(windows),
                'updated_contexts': 0,
                'new_contexts': 0,
                'closed_contexts': 0,
                'total_contexts': 0
            }

            # Indexer par ID
            current_window_ids = {w['id'] for w in windows}

            # Mettre à jour les contextes existants
            for window in windows:
                win_id = window['id']

                if win_id in self.contexts:
                    # Mise à jour
                    self._update_existing_context(win_id, window)
                    stats['updated_contexts'] += 1
                else:
                    # Nouveau contexte
                    self._create_new_context(window)
                    stats['new_contexts'] += 1

            # Détecter les contextes fermés
            existing_ids = set(self.contexts.keys())
            closed_ids = existing_ids - current_window_ids

            # Exclure le terminal s'il est spécial
            if self.terminal_context_id and self.terminal_context_id in closed_ids:
                closed_ids.discard(self.terminal_context_id)

            for closed_id in closed_ids:
                context = self.contexts[closed_id]
                self.events.emit(ContextEvent.CLOSED, context)
                stats['closed_contexts'] += 1

            stats['total_contexts'] = len(self.contexts)

            logger.debug(f"📊 Scan terminé: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Erreur lors du scan: {e}")
            return {'status': 'error', 'error': str(e)}

    def _scan_windows(self) -> List[Dict[str, Any]]:
        """Scan des fenêtres disponibles via wmctrl"""
        windows = []

        try:
            # Utilise wmctrl pour lister les fenêtres
            result = subprocess.run(
                "wmctrl -l -x -p",  # -p pour inclure les PIDs
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                # Fallback avec xdotool
                return self._scan_windows_xdotool()

            # Parser le résultat wmctrl
            # Format: <window_id> <desktop> <wm_class> <host> <title>
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split(None, 4)
                    if len(parts) >= 5:
                        win_id, desktop, wm_class, host, title = parts[0], parts[1], parts[2], parts[3], parts[4]

                        # Créer les informations de fenêtre
                        window_info = WindowInfo(
                            id=win_id,
                            title=title,
                            class_name=wm_class,
                            pid=self._extract_pid_from_wmctrl(line)
                        )

                        windows.append({
                            'id': win_id,
                            'title': title,
                            'class': wm_class,
                            'pid': window_info.pid,
                            'window_info': window_info
                        })

        except subprocess.TimeoutExpired:
            logger.warning("Timeout lors du scan wmctrl")
            return self._scan_windows_xdotool()
        except Exception as e:
            logger.error(f"Erreur scan wmctrl: {e}")
            return self._scan_windows_xdotool()

        return windows

    def _scan_windows_xdotool(self) -> List[Dict[str, Any]]:
        """Scan de fallback avec xdotool"""
        windows = []

        try:
            result = subprocess.run(
                "xdotool search . getwindowname %@",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        win_id = f"xdotool_{i}"
                        windows.append({
                            'id': win_id,
                            'title': line.strip(),
                            'class': 'unknown',
                            'pid': None,
                            'window_info': WindowInfo(
                                id=win_id,
                                title=line.strip(),
                                class_name='unknown'
                            )
                        })

        except Exception as e:
            logger.error(f"Erreur scan xdotool: {e}")

        return windows

    def _extract_pid_from_wmctrl(self, line: str) -> Optional[int]:
        """Extrait le PID depuis la ligne wmctrl"""
        try:
            # wmctrl -p donne le PID dans une colonne supplémentaire
            parts = line.split()
            if len(parts) >= 5:
                # Le PID est généralement dans la 4ème colonne avec -p
                pid_str = parts[3]
                return int(pid_str)
        except (ValueError, IndexError):
            pass
        return None

    def _create_new_context(self, window_data: Dict):
        """Crée un nouveau contexte"""
        window_info = window_data['window_info']

        # Déterminer le type de contexte
        context_type = self._classify_context(
            window_info.title,
            window_data.get('class', ''),
            window_info.pid
        )

        # Créer le contexte
        context = BrowserContext(
            id=window_data['id'],
            title=window_info.title,
            type=context_type,
            window_info=window_info,
            last_active=time.time()
        )

        # Déterminer les capacités
        context.capabilities = self._determine_capabilities(context)

        # Contexte spécial pour le terminal
        if context.type == ContextType.TERMINAL and not self.terminal_context_id:
            self.terminal_context_id = context.id

        # Stocker le contexte
        self.contexts[context.id] = context

        # Émettre l'événement
        self.events.emit(ContextEvent.CREATED, context)

        logger.info(f"🆕 Nouveau contexte: {context.title} ({context.type.value})")

    def _update_existing_context(self, context_id: str, window_data: Dict):
        """Met à jour un contexte existant"""
        if context_id not in self.contexts:
            return

        context = self.contexts[context_id]
        window_info = window_data['window_info']

        # Vérifier les changements
        title_changed = context.title != window_info.title

        # Mettre à jour
        context.title = window_info.title
        context.window_info = window_info
        context.last_active = time.time()

        # Émettre les événements
        if title_changed:
            self.events.emit(ContextEvent.TITLE_CHANGED, context,
                           old_title=context.title, new_title=window_info.title)

    def _classify_context(self, title: str, class_name: str, pid: Optional[int]) -> ContextType:
        """Classifie un contexte basé sur ses propriétés"""
        title_lower = title.lower()
        class_lower = class_name.lower()

        # Terminaux
        if any(term in class_lower for term in ['terminal', 'xterm', 'gnome-terminal', 'konsole']):
            return ContextType.TERMINAL

        # Navigateurs Chrome/Chromium
        if any(browser in class_lower for browser in ['chrome', 'chromium', 'google-chrome']):
            if 'youtube' in title_lower:
                return ContextType.BROWSER_YOUTUBE
            elif 'facebook' in title_lower:
                return ContextType.BROWSER_FACEBOOK
            elif 'google' in title_lower:
                return ContextType.BROWSER_GOOGLE
            elif 'wikipedia' in title_lower:
                return ContextType.BROWSER_WIKIPEDIA
            else:
                return ContextType.BROWSER_CHROME

        # Firefox
        if 'firefox' in class_lower:
            return ContextType.BROWSER_FIREFOX

        # Applications génériques
        if class_lower and class_lower not in ['unknown', '']:
            return ContextType.APPLICATION

        return ContextType.UNKNOWN

    def _determine_capabilities(self, context: BrowserContext) -> List[str]:
        """Détermine les capacités d'un contexte"""
        capabilities = []

        if context.is_browser:
            capabilities.extend([
                'navigation',
                'scroll',
                'click',
                'type_text',
                'read_content',
                'take_screenshot'
            ])

            # Capacités spécifiques
            if context.type == ContextType.BROWSER_CHROME:
                capabilities.extend(['cdp_control', 'extensions'])
            elif context.type == ContextType.BROWSER_FIREFOX:
                capabilities.extend(['marionette_control'])

            # Capacités par site
            if context.type == ContextType.BROWSER_YOUTUBE:
                capabilities.extend(['play_video', 'read_comments', 'search_videos'])
            elif context.type == ContextType.BROWSER_FACEBOOK:
                capabilities.extend(['post_content', 'read_feed', 'send_messages'])
            elif context.type == ContextType.BROWSER_GOOGLE:
                capabilities.extend(['web_search', 'google_services'])

        elif context.type == ContextType.TERMINAL:
            capabilities.extend([
                'command_execution',
                'text_input',
                'file_operations'
            ])

        return capabilities

    # === GESTION DES CONTEXTES ===

    def get_context(self, context_id: str) -> Optional[BrowserContext]:
        """Récupère un contexte par ID"""
        return self.contexts.get(context_id)

    def get_current_context(self) -> Optional[BrowserContext]:
        """Récupère le contexte actuel"""
        if self.current_context_id:
            return self.contexts.get(self.current_context_id)
        return None

    def list_contexts(self, filter_type: Optional[ContextType] = None) -> List[BrowserContext]:
        """Liste tous les contextes (avec filtrage optionnel)"""
        contexts = list(self.contexts.values())

        if filter_type:
            contexts = [c for c in contexts if c.type == filter_type]

        return contexts

    def find_contexts_by_title(self, title_pattern: str) -> List[BrowserContext]:
        """Trouve des contextes par pattern de titre"""
        pattern_lower = title_pattern.lower()
        return [
            ctx for ctx in self.contexts.values()
            if pattern_lower in ctx.title.lower()
        ]

    def find_contexts_by_type(self, context_type: ContextType) -> List[BrowserContext]:
        """Trouve des contextes par type"""
        return [ctx for ctx in self.contexts.values() if ctx.type == context_type]

    def switch_to_context(self, context_id: str) -> bool:
        """
        Bascule vers un contexte spécifique

        Args:
            context_id: ID du contexte cible

        Returns:
            True si le basculement a réussi
        """
        if context_id not in self.contexts:
            logger.warning(f"Contexte {context_id} introuvable")
            return False

        context = self.contexts[context_id]

        # Activer la fenêtre
        if self._activate_window(context.window_info.id):
            # Émettre l'événement d'activation
            self.events.emit(ContextEvent.ACTIVATED, context)
            return True

        return False

    def switch_to_context_by_title(self, title_pattern: str) -> Optional[str]:
        """
        Bascule vers un contexte par pattern de titre

        Returns:
            ID du contexte activé ou None
        """
        candidates = self.find_contexts_by_title(title_pattern)

        if not candidates:
            return None

        # Sélectionner le meilleur candidat (plus récemment actif)
        candidates.sort(key=lambda c: c.last_active, reverse=True)
        target_context = candidates[0]

        if self.switch_to_context(target_context.id):
            return target_context.id

        return None

    def switch_to_terminal(self) -> bool:
        """Bascule vers le terminal OC"""
        if self.terminal_context_id:
            return self.switch_to_context(self.terminal_context_id)
        return False

    def _activate_window(self, window_id: str) -> bool:
        """Active une fenêtre spécifique"""
        try:
            # Essayer wmctrl d'abord
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

        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout lors de l'activation de {window_id}")
        except Exception as e:
            logger.error(f"Erreur lors de l'activation de {window_id}: {e}")

        return False

    # === NOTIFICATIONS ET UTILITAIRES ===

    def notify_user(self, message: str, context: Optional[BrowserContext] = None):
        """Notifie l'utilisateur via le terminal"""
        if self.switch_to_terminal():
            try:
                # Envoyer le message dans le terminal
                full_message = f"🔥 SHARINGAN: {message}"
                if context:
                    full_message += f" ({context.title})"

                subprocess.run(
                    f'xdotool type "echo \\"{full_message}\\"\\n"',
                    shell=True, timeout=3
                )

                logger.info(f"📢 Notification: {message}")

            except Exception as e:
                logger.error(f"Erreur de notification: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques des contextes"""
        total_contexts = len(self.contexts)
        browser_contexts = len([c for c in self.contexts.values() if c.is_browser])
        terminal_contexts = len([c for c in self.contexts.values() if c.type == ContextType.TERMINAL])

        # Activité récente
        now = time.time()
        recent_contexts = len([
            c for c in self.contexts.values()
            if now - c.last_active < 300  # 5 minutes
        ])

        return {
            'total_contexts': total_contexts,
            'browser_contexts': browser_contexts,
            'terminal_contexts': terminal_contexts,
            'recent_contexts': recent_contexts,
            'current_context': self.current_context_id,
            'terminal_context': self.terminal_context_id,
            'monitoring_active': self.monitoring
        }

    def cleanup_closed_contexts(self):
        """Nettoie les contextes fermés (appelée périodiquement)"""
        # Le monitoring gère déjà ça automatiquement
        pass

    # === MÉTHODES DE COMPATIBILITÉ ===

    def select_window(self, description: str) -> bool:
        """Méthode de compatibilité avec l'ancien système"""
        return self.switch_to_context_by_title(description) is not None

    def get_context_status(self) -> Dict:
        """Méthode de compatibilité - retourne un statut détaillé"""
        contexts_list = []
        for ctx in self.contexts.values():
            contexts_list.append({
                'id': ctx.id,
                'title': ctx.title,
                'type': ctx.type.value,
                'active': ctx.id == self.current_context_id,
                'browser_type': ctx.browser_name,
                'capabilities': ctx.capabilities,
                'last_active': ctx.last_active,
                'actions_count': ctx.actions_count
            })

        return {
            'total_contexts': len(self.contexts),
            'current_context': self.current_context_id,
            'terminal_available': self.terminal_context_id is not None,
            'contexts': contexts_list
        }

# === FONCTIONS UTILITAIRES GLOBALES ===

_context_manager: Optional[BrowserContextManager] = None

def get_context_manager() -> BrowserContextManager:
    """Singleton du gestionnaire de contexte"""
    global _context_manager
    if _context_manager is None:
        _context_manager = BrowserContextManager()
        _context_manager.start_monitoring()
    return _context_manager

async def init_context_system():
    """Initialise le système de contexte"""
    manager = get_context_manager()
    manager.scan_and_update_contexts()
    return manager

# API simplifiée
def list_contexts():
    """Liste simple des contextes"""
    manager = get_context_manager()
    return [ctx.title for ctx in manager.list_contexts()]

def switch_context(title_pattern: str):
    """Bascule simple vers un contexte"""
    manager = get_context_manager()
    return manager.switch_to_context_by_title(title_pattern)

def get_current_context():
    """Contexte actuel"""
    manager = get_context_manager()
    ctx = manager.get_current_context()
    return ctx.title if ctx else None

if __name__ == "__main__":
    # Test du système
    print("🧪 TEST DU BROWSER CONTEXT MANAGER")
    print("=" * 50)

    manager = BrowserContextManager()

    # Scan initial
    print("🔍 Scanning des contextes...")
    stats = manager.scan_and_update_contexts()
    print(f"📊 Résultats: {stats}")

    # Lister les contextes
    print("\n📋 CONTEXTES DÉTECTÉS:")
    contexts = manager.list_contexts()
    for ctx in contexts[:5]:  # Limiter l'affichage
        print(f"  • {ctx.title} ({ctx.type.value}) - {len(ctx.capabilities)} capacités")

    # Démarrer le monitoring
    print("\n👀 Démarrage du monitoring...")
    manager.start_monitoring()

    # Test de basculement
    print("\n🎯 Test de basculement:")
    terminal_switched = manager.switch_to_terminal()
    print(f"  Terminal: {'✅' if terminal_switched else '❌'}")

    # Statistiques finales
    print("\n📊 STATISTIQUES:")
    stats = manager.get_statistics()
    print(f"  Total: {stats['total_contexts']}")
    print(f"  Navigateurs: {stats['browser_contexts']}")
    print(f"  Terminaux: {stats['terminal_contexts']}")

    print("\n🎉 Test terminé!")

    # Garder le monitoring actif quelques secondes
    time.sleep(3)
    manager.stop_monitoring()