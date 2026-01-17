#!/usr/bin/env python3
"""
SharingAN Browser History - Système d'historique et traçabilité
================================================================

Ce module ajoute un système d'historique pour suivre:
- Actions de l'IA (navigations, lectures, recherches)
- Actions de l'utilisateur (utilisation manuelle)
- État du navigateur (URL, titre, timestamp)

L'historique permet une meilleure collaboration IA-utilisateur.

Usage:
    from browser_history import get_history, log_action, get_session_summary
    
    # Enregistrer une action
    await log_action("IA", "navigate", "https://google.com")
    
    # Obtenir l'historique
    history = get_history()
    
    # Obtenir le résumé de la session
    summary = get_session_summary()
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger("sharingan.browser.history")

# =============================================================================
# MODÈLES DE DONNÉES
# =============================================================================

@dataclass
class BrowserAction:
    """Représente une action dans le navigateur."""
    timestamp: str
    source: str  # "IA" ou "UTILISATEUR" ou "SYSTÈME"
    action_type: str  # "navigate", "read", "scroll", "search", etc.
    target: str  # URL, sélecteur, terme de recherche
    result: str  # "success", "error", "pending"
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "BrowserAction":
        return cls(**data)


@dataclass
class BrowserState:
    """Représente l'état du navigateur à un moment donné."""
    timestamp: str
    url: str
    title: str
    scroll_position: int
    actions_count: int
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "BrowserState":
        return cls(**data)


# =============================================================================
# SYSTÈME D'HISTORIQUE (SINGLETON)
# =============================================================================

class BrowserHistory:
    """
    Gestionnaire d'historique du navigateur.
    
    Suit toutes les actions de l'IA et de l'utilisateur,
    permettant une meilleure traçabilité et collaboration.
    
    Example:
        history = BrowserHistory()
        await history.log_action("IA", "navigate", "https://google.com")
        await history.log_action("UTILISATEUR", "scroll", "500")
        
        # Obtenir l'historique complet
        all_actions = history.get_all()
        
        # Obtenir le résumé
        summary = history.get_summary()
    """
    
    _instance: Optional["BrowserHistory"] = None
    
    def __new__(cls) -> "BrowserHistory":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._actions: List[BrowserAction] = []
        self._states: List[BrowserState] = []
        self._session_start: datetime = datetime.now()
        self._initialized = True
        
        # Configuration du logger
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure la journalisation des actions."""
        # Créer un fichier de log pour l'historique
        log_dir = Path("/root/Projets/Sharingan-WFK-Python/logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "browser_history.log"
        
        # Logger vers fichier et console
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    # =========================================================================
    # ENREGISTREMENT DES ACTIONS
    # =========================================================================
    
    async def log_action(
        self,
        source: str,
        action_type: str,
        target: str,
        result: str = "success",
        details: Optional[Dict] = None
    ) -> BrowserAction:
        """
        Enregistre une action dans l'historique.
        
        Args:
            source: Source de l'action ("IA", "UTILISATEUR", "SYSTÈME")
            action_type: Type d'action ("navigate", "read", "scroll", etc.)
            target: Cible de l'action (URL, sélecteur, terme)
            result: Résultat ("success", "error", "pending")
            details: Détails supplémentaires
            
        Returns:
            L'action créée
        """
        action = BrowserAction(
            timestamp=datetime.now().isoformat(),
            source=source,
            action_type=action_type,
            target=target,
            result=result,
            details=details or {}
        )
        
        self._actions.append(action)
        
        # Logger l'action
        logger.info(
            f"[{source}] {action_type}: {target} -> {result}"
        )
        
        return action
    
    async def log_navigate(self, url: str, result: str = "success") -> BrowserAction:
        """Enregistre une navigation."""
        return await self.log_action("IA", "navigate", url, result)
    
    async def log_read(self, selector: str, result: str = "success") -> BrowserAction:
        """Enregistre une lecture de contenu."""
        return await self.log_action("IA", "read", selector, result)
    
    async def log_search(self, query: str, result: str = "success") -> BrowserAction:
        """Enregistre une recherche."""
        return await self.log_action("IA", "search", query, result)
    
    async def log_scroll(self, pixels: int, result: str = "success") -> BrowserAction:
        """Enregistre un défilement."""
        return await self.log_action("IA", "scroll", f"{pixels}px", result)
    
    async def log_user_action(
        self,
        action_type: str,
        target: str,
        result: str = "success"
    ) -> BrowserAction:
        """Enregistre une action de l'utilisateur."""
        return await self.log_action("UTILISATEUR", action_type, target, result)
    
    async def log_system_event(
        self,
        event_type: str,
        details: str,
        result: str = "success"
    ) -> BrowserAction:
        """Enregistre un événement système."""
        return await self.log_action("SYSTÈME", event_type, details, result)
    
    # =========================================================================
    # ENREGISTREMENT DE L'ÉTAT
    # =========================================================================
    
    async def save_state(
        self,
        url: str,
        title: str,
        scroll_position: int = 0
    ) -> BrowserState:
        """
        Enregistre l'état actuel du navigateur.
        
        Args:
            url: URL actuelle
            title: Titre de la page
            scroll_position: Position de défilement
            
        Returns:
            L'état enregistré
        """
        state = BrowserState(
            timestamp=datetime.now().isoformat(),
            url=url,
            title=title,
            scroll_position=scroll_position,
            actions_count=len(self._actions)
        )
        
        self._states.append(state)
        
        # Garder seulement les 100 derniers états
        if len(self._states) > 100:
            self._states = self._states[-100:]
        
        return state
    
    # =========================================================================
    # CONSULTATION DE L'HISTORIQUE
    # =========================================================================
    
    def get_all(self) -> List[Dict]:
        """Obtient toutes les actions."""
        return [a.to_dict() for a in self._actions]
    
    def get_by_source(self, source: str) -> List[Dict]:
        """Obtient les actions d'une source spécifique."""
        return [a.to_dict() for a in self._actions if a.source == source]
    
    def get_by_type(self, action_type: str) -> List[Dict]:
        """Obtient les actions d'un type spécifique."""
        return [a.to_dict() for a in self._actions if a.action_type == action_type]
    
    def get_recent(self, count: int = 10) -> List[Dict]:
        """Obtient les N actions les plus récentes."""
        return [a.to_dict() for a in self._actions[-count:]]
    
    def get_all_states(self) -> List[Dict]:
        """Obtient tous les états enregistrés."""
        return [s.to_dict() for s in self._states]
    
    def get_latest_state(self) -> Optional[Dict]:
        """Obtient l'état le plus récent."""
        if self._states:
            return self._states[-1].to_dict()
        return None
    
    # =========================================================================
    # RÉSUMÉS ET STATISTIQUES
    # =========================================================================
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Génère un résumé de la session.
        
        Returns:
            Dictionnaire avec les statistiques de la session
        """
        ia_actions = [a for a in self._actions if a.source == "IA"]
        user_actions = [a for a in self._actions if a.source == "UTILISATEUR"]
        system_actions = [a for a in self._actions if a.source == "SYSTÈME"]
        
        # Compter par type
        type_counts: Dict[str, int] = {}
        for a in self._actions:
            type_counts[a.action_type] = type_counts.get(a.action_type, 0) + 1
        
        # Calculer la durée de la session
        session_duration = datetime.now() - self._session_start
        
        return {
            "session_start": self._session_start.isoformat(),
            "session_duration_seconds": session_duration.total_seconds(),
            "total_actions": len(self._actions),
            "ia_actions": len(ia_actions),
            "user_actions": len(user_actions),
            "system_actions": len(system_actions),
            "actions_by_type": type_counts,
            "last_url": self._states[-1].url if self._states else None,
            "last_action": self._actions[-1].to_dict() if self._actions else None
        }
    
    def get_ia_summary(self) -> Dict[str, Any]:
        """Génère un résumé des actions de l'IA."""
        ia_actions = [a for a in self._actions if a.source == "IA"]
        
        type_counts: Dict[str, int] = {}
        for a in ia_actions:
            type_counts[a.action_type] = type_counts.get(a.action_type, 0) + 1
        
        return {
            "total_actions": len(ia_actions),
            "actions_by_type": type_counts,
            "navigations": len([a for a in ia_actions if a.action_type == "navigate"]),
            "reads": len([a for a in ia_actions if a.action_type == "read"]),
            "searches": len([a for a in ia_actions if a.action_type == "search"]),
            "scrolls": len([a for a in ia_actions if a.action_type == "scroll"])
        }
    
    def get_user_activity(self) -> Dict[str, Any]:
        """Génère un résumé de l'activité utilisateur."""
        user_actions = [a for a in self._actions if a.source == "UTILISATEUR"]
        
        return {
            "total_actions": len(user_actions),
            "last_action": user_actions[-1].to_dict() if user_actions else None
        }
    
    # =========================================================================
    # EXPORT ET SAUVEGARDE
    # =========================================================================
    
    def export_json(self, filepath: Optional[str] = None) -> str:
        """
        Exporte l'historique au format JSON.
        
        Args:
            filepath: Chemin du fichier (optionnel)
            
        Returns:
            Le JSON généré
        """
        data = {
            "export_date": datetime.now().isoformat(),
            "session_start": self._session_start.isoformat(),
            "actions": self.get_all(),
            "states": self.get_all_states(),
            "summary": self.get_summary()
        }
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        if filepath:
            Path(filepath).write_text(json_str)
            logger.info(f"Historique exporté vers: {filepath}")
        
        return json_str
    
    def clear(self):
        """Efface l'historique (nouvelle session)."""
        self._actions.clear()
        self._states.clear()
        self._session_start = datetime.now()
        logger.info("Historique effacé - Nouvelle session")
    
    def get_action_count(self) -> int:
        """Retourne le nombre d'actions."""
        return len(self._actions)


# =============================================================================
# FONCTIONS DE COMMODITÉ
# =============================================================================

_history: Optional[BrowserHistory] = None


def get_history() -> BrowserHistory:
    """Obtient l'instance unique de l'historique."""
    global _history
    if _history is None:
        _history = BrowserHistory()
    return _history


async def log_ia_action(
    action_type: str,
    target: str,
    result: str = "success",
    details: Optional[Dict] = None
) -> BrowserAction:
    """Enregistre une action de l'IA."""
    return await get_history().log_action("IA", action_type, target, result, details)


async def log_user_action(
    action_type: str,
    target: str,
    result: str = "success"
) -> BrowserAction:
    """Enregistre une action de l'utilisateur."""
    return await get_history().log_user_action(action_type, target, result)


async def save_browser_state(
    url: str,
    title: str,
    scroll_position: int = 0
) -> BrowserState:
    """Enregistre l'état du navigateur."""
    return await get_history().save_state(url, title, scroll_position)


def get_all_actions() -> List[Dict]:
    """Obtient toutes les actions."""
    return get_history().get_all()


def get_recent_actions(count: int = 10) -> List[Dict]:
    """Obtient les actions récentes."""
    return get_history().get_recent(count)


def get_session_summary() -> Dict[str, Any]:
    """Obtient le résumé de la session."""
    return get_history().get_summary()


def export_history(filepath: str = "/root/Projets/Sharingan-WFK-Python/logs/browser_history.json") -> str:
    """Exporte l'historique."""
    return get_history().export_json(filepath)


# =============================================================================
# INTÉGRATION AVEC BROWSER_SHELL
# =============================================================================

async def log_and_execute(
    action_type: str,
    target: str,
    execute_func,
    *args,
    **kwargs
) -> Any:
    """
    Exécute une fonction et enregistre l'action.
    
    Usage:
        result = await log_and_execute(
            "navigate", "https://google.com",
            shell.go, "https://google.com"
        )
    """
    history = get_history()
    
    try:
        result = await execute_func(*args, **kwargs)
        await history.log_action("IA", action_type, target, "success")
        return result
    except Exception as e:
        await history.log_action("IA", action_type, target, "error", {"error": str(e)})
        raise


# =============================================================================
# POINT D'ENTRÉE - TEST
# =============================================================================

if __name__ == "__main__":
    async def test_history():
        print("="*60)
        print("🧪 TEST DU SYSTÈME D'HISTORIQUE")
        print("="*60)
        
        history = get_history()
        
        # Simuler des actions
        print("\n📝 Enregistrement d'actions...")
        
        await history.log_navigate("https://wikipedia.org", "success")
        await asyncio.sleep(0.1)
        await history.log_read("article", "success")
        await asyncio.sleep(0.1)
        await history.log_search("Python programming", "success")
        await asyncio.sleep(0.1)
        await history.log_scroll(500, "success")
        await asyncio.sleep(0.1)
        
        await history.log_user_action("scroll", "1000", "success")
        
        # Enregistrer l'état
        await history.save_state("https://wikipedia.org", "Wikipedia", 500)
        
        # Afficher l'historique
        print("\n📜 Historique des actions:")
        for action in history.get_all():
            print(f"   [{action['source']}] {action['action_type']}: {action['target']} -> {action['result']}")
        
        # Afficher le résumé
        print("\n📊 Résumé de la session:")
        summary = history.get_summary()
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        # Exporter
        print("\n💾 Export de l'historique...")
        json_export = history.export_json("/tmp/browser_history_test.json")
        print(f"   Exporté vers: /tmp/browser_history_test.json")
        print(f"   Taille: {len(json_export)} caractères")
        
        print("\n" + "="*60)
        print("✅ TEST TERMINÉ")
        print("="*60)
    
    asyncio.run(test_history())
