#!/usr/bin/env python3
"""
Sharingan OS - Action Orchestrator
Orchestrateur d'actions multi-étapes par IA avec validation.
Auteur: Ben Sambe
"""

import sys
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire parent au path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from fake_detector import FakeDetector, validate_readiness
    from check_obligations import check_obligations
    from opencode_provider import OpenCodeProvider
    from action_orchestrator import ActionOrchestrator
    from nlp_rag_system import NLPRAGSystem
    from hybrid_manager import HybridAIManager
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

logger = logging.getLogger("sharingan.actions")


@dataclass
class ActionRequest:
    """Requête d'action pour l'orchestrateur"""
    type: str
    target: str
    content: Optional[str] = None
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    command: Optional[str] = None
    pattern: Optional[str] = None
    metadata: Optional[Dict] = None
    priority: int = 1
    dependencies: List[str] = []


@dataclass
class ActionResult:
    """Résultat d'exécution d'action"""
    success: bool
    action_type: str
    target: str
    output: Optional[str] = None
    error: Optional[str] = None
    timestamp: str
    duration_ms: float


class ActionOrchestrator:
    """
    Orchestrateur d'actions multi-orchestrées par IA.
    Valide chaque action avant exécution.
    """
    
    def __init__(self):
        self.active = False
        self.action_queue = []
        self.action_history = []
        self.fake_detector = None
        self.nlp_rag = None
        self.ai_manager = None
        self.opencode = None
        
        # Initialiser les composants
        try:
            self.fake_detector = FakeDetector()
            self.nlp_rag = NLPRAGSystem()
            self.ai_manager = HybridAIManager()
            self.opencode = OpenCodeProvider()
            self.action_history = []
            logger.info("Action Orchestrator initialized")
        except ImportError as e:
            logger.error(f"Import error: {e}")
    
    def add_action(self, action: ActionRequest) -> str:
        """Ajoute une action à la queue"""
        action_id = f"action_{len(self.action_queue)}"
        self.action_queue.append(action)
        logger.info(f"Action queued: {action.type} on {action.target}")
        return action_id
    
    def add_actions(self, actions: List[ActionRequest]) -> List[str]:
        """Ajoute plusieurs actions à la queue"""
        action_ids = []
        for action in actions:
            action_id = self.add_action(action)
            action_ids.append(action_id)
        return action_ids
    
    def start(self):
        """Démarrer l'orchestrateur"""
        self.active = self.active or len(self.action_queue) > 0
        logger.info(f"Starting Action Orchestrator with {len(self.action_queue)} queued actions")
        
        # Démarrer le thread d'orchestration
        import threading
        self.orchestrator_thread = threading.Thread(target=self._orchestration_loop, daemon=True)
        self.orchestrator_thread.start()
    
    def stop(self):
        """Arrêter l'orchestrateur"""
        self.active = False
        if hasattr(self, 'orchestrator_thread'):
            self.orchestrator_thread.join(timeout=5)
        logger.info("Action Orchestrator stopped")
    
    def _orchestration_loop(self):
        """Boucle d'orchestration"""
        while self.active:
            try:
                if self.action_queue:
                    action = self.action_queue.pop(0)
                    self._execute_action(action)
                    self.action_history.append(action)
                else:
                    import time
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Orchestration error: {e}")
                time.sleep(5)
    
    def _execute_action(self, action: ActionRequest) -> ActionResult:
        """Exécute une action spécifique"""
        action_id = f"action_{len(self.action_history)}"
        start_time = datetime.now()
        
        try:
            # Valider l'action avec fake detector
            if self.fake_detector:
                fake_check = self.fake_detector.validate_ai_response(
                    f"{action.type} on {action.target}",
                    f"Executing {action.type} action"
                )
                if not fake_check[0]:
                    logger.warning(f"Fake detected in action {action_id}")
                    return ActionResult(
                        success=False,
                        action_type=action.type,
                        target=action.target,
                        error="Fake detected"
                    )
            
            # Exécuter l'action
            if action.type == "create":
                result = self._execute_create(action)
            elif action.type == "delete":
                result = self._execute_delete(action)
            elif action.type == "modify":
                result = self._execute_modify(action)
            elif action.type == "execute":
                result = self._execute_command(action)
            elif action.type == "read":
                result = self._execute_read(action)
            elif action.type == "search":
                result = self._execute_search(action)
            else:
                result = ActionResult(
                    success=False,
                    action_type=action.type,
                    target=action.target,
                    error=f"Unknown action type: {action.type}"
                )
            
            # Mettre à jour l'historique
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            result = ActionResult(
                success=result.success,
                action_type=action.type,
                target=action.target,
                output=result.get("output"),
                error=result.get("error"),
                timestamp=str(start_time),
                duration_ms=duration_ms
            )
            
            logger.info(f"Executed {action.type} on {action.target} ({result.success})")
            return result
            
        except Exception as e:
            logger.error(f"Action execution error: {e}")
            return ActionResult(
                success=False,
                action_type=action.type,
                target=action.target,
                error=str(e)
            )
    
    def _execute_create(self, action: ActionRequest) -> ActionResult:
        """Exécute une action de création"""
        path = action.target
        content = action.content or ""
        
        try:
            # Créer le répertoire parent
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Écrire le fichier
            file_path.write_text(content)
            
            return ActionResult(
                success=True,
                action_type="create",
                target=path,
                output=f"Created file: {path}"
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                action_type="create",
                target=path,
                error=str(e)
    
    def _execute_delete(self, action: ActionRequest) -> ActionResult:
        """Exécute une action de suppression"""
        path = action.target
        
        try:
            file_path = Path(path)
            if file_path.exists():
                if file_path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    file_path.unlink()
                
                return ActionResult(
                    success=True,
                    action_type="delete",
                    target=path,
                    output=f"Deleted: {path}"
                )
            else:
                return ActionResult(
                    success=False,
                    action_type="delete",
                    target=path,
                    error="File not found"
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                action_type="delete",
                target=path,
                error=str(e)
    
    def _execute_modify(self, action: ActionRequest) -> ActionResult:
        """Exécute une action de modification"""
        path = action.target
        old_content = action.old_content or ""
        new_content = action.new_content or ""
        
        try:
            file_path = Path(path)
            if file_path.exists():
                content = file_path.read_text()
                if old_content in content:
                    modified = content.replace(old_content, new_content)
                    file_path.write_text(modified)
                    return ActionResult(
                        success=True,
                        action_type="modify",
                        target=path,
                        output=f"Modified: {path}"
                    )
                else:
                    return ActionResult(
                        success=False,
                        action_type="modify",
                        target=path,
                        error="Old content not found"
                    )
            else:
                return ActionResult(
                    success=False,
                    action_type="modify",
                    target=path,
                    error="File not found"
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                action_type="modify",
                target=path,
                error=str(e)
    
    def _execute_command(self, action: ActionRequest) -> ActionResult:
        """Exécute une commande shell"""
        command = action.command
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return ActionResult(
                success=result.returncode == 0,
                action_type="execute",
                target=command,
                output=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                action_type="execute",
                target=command,
                error=str(e)
    
    def _execute_read(self, action: ActionRequest) -> ActionResult:
        """Lit un fichier"""
        path = action.target
        
        try:
            file_path = Path(path)
            if file_path.exists() and file_path.is_file():
                content = file_path.read_text()
                return ActionResult(
                    success=True,
                    action_type="read",
                    target=path,
                    content=content
                )
            else:
                return ActionResult(
                    success=False,
                    action_type="read",
                    target=path,
                    error="File not found"
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                action_type="read",
                target=path,
                error=str(e)
    
    def _execute_search(self, action: ActionRequest) -> ActionResult:
        """Recherche dans un fichier"""
        path = action.target
        pattern = action.pattern
        
        try:
            file_path = Path(path)
            if file_path.exists() and file_path.is_file():
                content = file_path.read_text()
                matches = []
                
                # Recherche simple
                if pattern in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line:
                            matches.append(f"Line {i+1}: {line.strip()}")
                
                return ActionResult(
                    success=len(matches) > 0,
                    action_type="search",
                    target=path,
                    matches=matches
                )
            else:
                return ActionResult(
                    success=False,
                    action_type="search",
                    target=path,
                    error="File not found"
                )
                
        except Exception as e:
            return ActionResult(
                success=False,
                action_type="search",
                target=path,
                error=str(e)
    
    def get_status(self) -> Dict:
        """Obtenir le statut de l'orchestrateur"""
        return {
            "active": self.active,
            "queue_size": len(self.action_queue),
            "history_count": len(self.action_history),
            "fake_detector_available": self.fake_detector is not None,
            "nlp_rag_ready": self.nlp_rag is not None,
            "ai_manager_ready": self.ai_manager is not None,
            "opencode_ready": self.opencode is not None,
            "ready": self.active
        }
    
    def get_action_history(self) -> List[Dict]:
        """Obtenir l'historique des actions"""
        return self.action_history


def get_action_orchestrator() -> ActionOrchestrator:
    """Get singleton instance"""
    return ActionOrchestrator()


__all__ = ["ActionOrchestrator", "get_action_orchestrator", "ActionResult", "ActionRequest"]


if __name__ == "__main__":
    main()
    
    # Test rapide
    orchestrator = get_action_orchestrator()
    
    # Test d'actions
    test_actions = [
        {"type": "create", "target": "/tmp/test.txt", "content": "Hello World"},
        {"type": "delete", "target": "/tmp/test.txt"},
        {"type": "execute", "command": "echo 'Hello World'"}
    ]
    
    print("Testing Action Orchestrator...")
    
    for action in test_actions:
        action_id = orchestrator.add_action(action)
        print(f"  - Added action: {action_id}")
    
    print(f"  - Total actions queued: {len(orchestrator.action_queue)}")
    
    # Démarrer pour tester
    orchestrator.start()
    import time
    time.sleep(2)
    
    # Arrêter
    orchestrator.stop()
    
    print(f"  - Actions executed: {len([a for a in orchestrator.action_history if a.get('success')])}")
    
    print("✅ Action Orchestrator test completed")