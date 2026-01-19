#!/usr/bin/env python3
"""
Sharingan OS - Intelligent Memory Manager
Système de mémoire intelligent avec gestion temps réel + persistant
"""

import json
import os
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.memory")

class MemoryPriority(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    TEMPORARY = 1

class MemoryCategory(Enum):
    CONVERSATION = "conversation"
    ACTION = "action"
    RESULT = "result"
    ERROR = "error"
    CONFIG = "config"
    LEARNING = "learning"
    CONTEXT = "context"
    SYSTEM = "system"

class MemoryAction(Enum):
    KEEP = "keep"
    DELETE = "delete"
    ARCHIVE = "archive"
    UPGRADE = "upgrade"
    MERGE = "merge"

@dataclass
class MemoryItem:
    key: str
    data: Dict[str, Any]
    category: str
    priority: int
    created_at: str
    updated_at: str
    accessed_at: str
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    source: str = "unknown"
    action: str = "keep"
    ttl_seconds: Optional[int] = None
    merged_from: List[str] = field(default_factory=list)

class IntelligentMemoryManager:
    """
    Gestionnaire de mémoire intelligent pour Sharingan OS
    
    Caractéristiques:
    - Mémoire temps réel (vivante)
    - Mémoire persistante (historique)
    - Classification automatique
    - Nettoyage intelligent
    - Apprentissage continu
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.memory_file = self.data_dir / "ai_memory.json"
        self.history_file = self.data_dir / "memory_history.json"
        self.context_file = self.data_dir / "active_context.json"
        self.learned_file = self.data_dir / "learned_patterns.json"
        
        self.active_context: Dict[str, Any] = {}
        self.memory_cache: Dict[str, MemoryItem] = {}
        self.event_log: List[Dict] = []
        
        self._load_all()
        
        self.priority_rules = {
            "error": MemoryPriority.HIGH,
            "security": MemoryPriority.CRITICAL,
            "config": MemoryPriority.HIGH,
            "conversation": MemoryPriority.MEDIUM,
            "result": MemoryPriority.MEDIUM,
            "action": MemoryPriority.LOW,
            "temp": MemoryPriority.TEMPORARY,
        }
        
        self.auto_delete_after = {
            MemoryPriority.TEMPORARY: 300,
            MemoryPriority.LOW: 3600,
            MemoryPriority.MEDIUM: 86400,
            MemoryPriority.HIGH: 604800,
            MemoryPriority.CRITICAL: None,
        }
    
    def _load_all(self) -> None:
        """Charger toutes les données mémoire"""
        self._load_memory()
        self._load_history()
        self._load_context()
        self._load_learned()
    
    def _load_memory(self) -> None:
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    for key, item_data in data.items():
                        self.memory_cache[key] = MemoryItem(**item_data)
                logger.info(f"Loaded {len(self.memory_cache)} memory items")
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")
    
    def _load_history(self) -> None:
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []
    
    def _load_context(self) -> None:
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r') as f:
                    self.active_context = json.load(f)
            except:
                self.active_context = {}
    
    def _load_learned(self) -> None:
        if self.learned_file.exists():
            try:
                with open(self.learned_file, 'r') as f:
                    self.learned_patterns = json.load(f)
            except:
                self.learned_patterns = {"actions": [], "results": [], "errors": []}
        else:
            self.learned_patterns = {"actions": [], "results": [], "errors": []}
    
    def _save_all(self) -> None:
        """Sauvegarder toutes les données"""
        self._save_memory()
        self._save_history()
        self._save_context()
        self._save_learned()
    
    def _save_memory(self) -> None:
        data = {k: asdict(v) for k, v in self.memory_cache.items()}
        with open(self.memory_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_history(self) -> None:
        with open(self.history_file, 'w') as f:
            json.dump(self.history[-1000:], f, indent=2)
    
    def _save_context(self) -> None:
        with open(self.context_file, 'w') as f:
            json.dump(self.active_context, f, indent=2)
    
    def _save_learned(self) -> None:
        with open(self.learned_file, 'w') as f:
            json.dump(self.learned_patterns, f, indent=2)
    
    def store(self, key: str, data: Dict[str, Any], category: str = "conversation",
              priority: str = "MEDIUM", tags: Optional[List[str]] = None,
              source: str = "system", ttl_seconds: Optional[int] = None) -> bool:
        """Stocker un élément en mémoire"""
        try:
            priority_enum = MemoryPriority[priority] if isinstance(priority, str) else MemoryPriority.MEDIUM
            category_enum = category if isinstance(category, str) else "conversation"
            
            now = datetime.now().isoformat()
            item = MemoryItem(
                key=key,
                data=data,
                category=category_enum,
                priority=priority_enum.value,
                created_at=now,
                updated_at=now,
                accessed_at=now,
                access_count=1,
                tags=tags or [],
                source=source,
                ttl_seconds=ttl_seconds or self.auto_delete_after.get(priority_enum)
            )
            
            old_item = self.memory_cache.get(key)
            if old_item:
                item.created_at = old_item.created_at
                item.access_count = old_item.access_count + 1
                item.merged_from = old_item.merged_from + [key]
            
            self.memory_cache[key] = item
            self._log_event("store", key, category)
            self._save_memory()
            
            logger.info(f"Stored: {key} ({category}, priority={priority_enum.name})")
            return True
        except Exception as e:
            logger.error(f"Store failed: {e}")
            return False
    
    def retrieve(self, key: str, increment_access: bool = True) -> Optional[Dict[str, Any]]:
        """Récupérer un élément de mémoire"""
        item = self.memory_cache.get(key)
        if item:
            if increment_access:
                item.accessed_at = datetime.now().isoformat()
                item.access_count += 1
                self._save_memory()
            self._log_event("retrieve", key, item.category)
            return {
                "data": item.data,
                "category": item.category,
                "priority": item.priority,
                "created_at": item.created_at,
                "accessed_at": item.accessed_at,
                "access_count": item.access_count,
                "action": item.action
            }
        return None
    
    def retrieve_by_category(self, category: str) -> List[Dict]:
        """Récupérer tous les éléments d'une catégorie"""
        return [
            {"key": k, "data": v.data, "priority": v.priority, "accessed": v.accessed_at}
            for k, v in self.memory_cache.items()
            if v.category == category
        ]
    
    def retrieve_by_tag(self, tag: str) -> List[Dict]:
        """Récupérer tous les éléments avec un tag"""
        return [
            {"key": k, "data": v.data, "category": v.category}
            for k, v in self.memory_cache.items()
            if tag in v.tags
        ]
    
    def update_context(self, context_type: str, data: Dict[str, Any]) -> None:
        """Mettre à jour le contexte temps réel"""
        self.active_context[context_type] = {
            "data": data,
            "updated_at": datetime.now().isoformat()
        }
        self._save_context()
        logger.info(f"Context updated: {context_type}")
    
    def get_context(self, context_type: Optional[str] = None) -> Dict:
        """Récupérer le contexte temps réel"""
        if context_type:
            return self.active_context.get(context_type, {})
        return self.active_context
    
    def delete(self, key: str, archive_first: bool = True) -> bool:
        """Supprimer un élément de mémoire"""
        item = self.memory_cache.get(key)
        if item:
            if archive_first:
                self._archive_item(item)
            del self.memory_cache[key]
            self._save_memory()
            self._log_event("delete", key, item.category)
            logger.info(f"Deleted: {key}")
            return True
        return False
    
    def _archive_item(self, item: MemoryItem) -> None:
        """Archiver un élément avant suppression"""
        self.history.append({
            "key": item.key,
            "data": item.data,
            "category": item.category,
            "priority": item.priority,
            "created_at": item.created_at,
            "archived_at": datetime.now().isoformat(),
            "action": item.action
        })
    
    def cleanup_expired(self) -> int:
        """Nettoyer les éléments expirés"""
        now = time.time()
        expired_keys = []
        
        for key, item in self.memory_cache.items():
            if item.ttl_seconds:
                created_time = datetime.fromisoformat(item.created_at).timestamp()
                if now - created_time > item.ttl_seconds:
                    expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key, archive_first=True)
        
        count = len(expired_keys)
        if count > 0:
            logger.info(f"Cleaned up {count} expired items")
        return count
    
    def cleanup_low_priority(self, max_items: int = 100) -> int:
        """Nettoyer les éléments basse priorité si trop nombreux"""
        if len(self.memory_cache) <= max_items:
            return 0
        
        low_priority = [
            (k, v) for k, v in self.memory_cache.items()
            if v.priority <= MemoryPriority.LOW.value
        ]
        
        low_priority.sort(key=lambda x: (x[1].priority, x[1].accessed_at))
        
        to_delete = len(self.memory_cache) - max_items
        deleted = 0
        
        for key, item in low_priority:
            if deleted >= to_delete:
                break
            if item.priority == MemoryPriority.TEMPORARY.value:
                self.delete(key, archive_first=True)
                deleted += 1
        
        logger.info(f"Cleaned up {deleted} low priority items")
        return deleted
    
    def merge_similar(self, base_key: str, merge_keys: List[str]) -> bool:
        """Fusionner des éléments similaires"""
        base_item = self.memory_cache.get(base_key)
        if not base_item:
            return False
        
        for key in merge_keys:
            item = self.memory_cache.get(key)
            if item and item.category == base_item.category:
                base_item.merged_from.append(key)
                base_item.data["_merged"] = base_item.data.get("_merged", [])
                base_item.data["_merged"].append(item.data)
                self.delete(key, archive_first=False)
        
        base_item.updated_at = datetime.now().isoformat()
        self._save_memory()
        return True
    
    def analyze_and_recommend(self) -> Dict[str, Any]:
        """Analyser la mémoire et recommander des actions"""
        analysis = {
            "total_items": len(self.memory_cache),
            "by_category": {},
            "by_priority": {},
            "high_access": [],
            "old_items": [],
            "recommendations": []
        }
        
        for key, item in self.memory_cache.items():
            cat = item.category
            prio = item.priority
            analysis["by_category"][cat] = analysis["by_category"].get(cat, 0) + 1
            analysis["by_priority"][prio] = analysis["by_priority"].get(prio, 0) + 1
            
            if item.access_count > 10:
                analysis["high_access"].append({"key": key, "count": item.access_count})
            
            created = datetime.fromisoformat(item.created_at)
            if (datetime.now() - created).days > 7:
                analysis["old_items"].append({"key": key, "days": (datetime.now() - created).days})
        
        if len(self.memory_cache) > 200:
            analysis["recommendations"].append({"action": "cleanup_low_priority", "reason": "Too many items"})
        
        if analysis["old_items"]:
            analysis["recommendations"].append({"action": "archive_old", "reason": "Old items found"})
        
        if analysis["by_category"].get("error", 0) > 5:
            analysis["recommendations"].append({"action": "analyze_errors", "reason": "Many errors stored"})
        
        return analysis
    
    def learn_from_action(self, action: str, result: str, success: bool) -> None:
        """Apprendre d'une action"""
        entry = {
            "action": action,
            "result": result,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            self.learned_patterns["actions"].append(entry)
        else:
            self.learned_patterns["errors"].append(entry)
        
        self._save_learned()
    
    def get_best_action(self, context: str) -> Optional[Dict]:
        """Obtenir la meilleure action apprise pour un contexte"""
        for entry in reversed(self.learned_patterns.get("actions", [])):
            if context in entry.get("action", ""):
                return entry
        return None
    
    def _log_event(self, event_type: str, key: str, category: str) -> None:
        """Enregistrer un événement"""
        self.event_log.append({
            "type": event_type,
            "key": key,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.event_log) > 1000:
            self.event_log = self.event_log[-500:]
    
    def get_recent_events(self, limit: int = 50) -> List[Dict]:
        """Récupérer les événements récents"""
        return self.event_log[-limit:]
    
    def get_full_state(self) -> Dict:
        """Obtenir l'état complet de la mémoire"""
        return {
            "memory_items": len(self.memory_cache),
            "context_keys": len(self.active_context),
            "history_size": len(self.history),
            "learned_patterns": {
                "actions": len(self.learned_patterns.get("actions", [])),
                "errors": len(self.learned_patterns.get("errors", []))
            },
            "recent_events": len(self.event_log),
            "categories": list(set(v.category for v in self.memory_cache.values())),
            "analysis": self.analyze_and_recommend()
        }
    
    def clear_all(self, archive: bool = True) -> int:
        """Effacer toute la mémoire"""
        count = len(self.memory_cache)
        
        if archive:
            for key, item in list(self.memory_cache.items()):
                self._archive_item(item)
        
        self.memory_cache.clear()
        self._save_all()
        logger.info(f"Cleared all memory ({count} items)")
        return count


class SharedMemory:
    """Mémoire partagée entre tous les agents Akatsuki"""
    
    def __init__(self):
        self.manager = IntelligentMemoryManager()
        self.agents: Dict[str, Dict] = {}
    
    def register_agent(self, agent_name: str, capabilities: List[str]) -> None:
        """Enregistrer un agent"""
        self.agents[agent_name] = {
            "capabilities": capabilities,
            "last_seen": datetime.now().isoformat(),
            "tasks_completed": 0
        }
        self.manager.store(
            f"agent:{agent_name}",
            {"capabilities": capabilities, "status": "active"},
            category="system",
            priority="HIGH",
            tags=["agent", agent_name]
        )
    
    def agent完成任务(self, agent_name: str, task: str, result: Dict) -> None:
        """Un agent a terminé une tâche"""
        if agent_name in self.agents:
            self.agents[agent_name]["tasks_completed"] += 1
            self.agents[agent_name]["last_seen"] = datetime.now().isoformat()
        
        self.manager.store(
            f"task:{hashlib.sha256(f'{agent_name}:{task}'.encode()).hexdigest()}",
            {"agent": agent_name, "task": task, "result": result},
            category="action",
            priority="MEDIUM",
            tags=["task", agent_name]
        )
    
    def broadcast(self, message: str, importance: str = "MEDIUM") -> None:
        """Diffuser un message à tous les agents"""
        self.manager.store(
            f"broadcast:{datetime.now().timestamp()}",
            {"message": message, "importance": importance},
            category="context",
            priority=MemoryPriority[importance].value if importance in [e.name for e in MemoryPriority] else 3,
            tags=["broadcast"]
        )
    
    def get_agent_knowledge(self, agent_name: str) -> List[Dict]:
        """Obtenir tout ce qu'un agent doit savoir"""
        knowledge = []
        
        if agent_name in self.agents:
            knowledge.append({"type": "agent_info", "data": self.agents[agent_name]})
        
        knowledge.extend(self.manager.retrieve_by_tag(agent_name))
        knowledge.append({"type": "context", "data": self.manager.get_context()})
        
        recent = self.manager.get_recent_events(20)
        if recent:
            knowledge.append({"type": "recent_events", "data": recent})
        
        return knowledge


def get_memory_manager() -> IntelligentMemoryManager:
    """Obtenir l'instance du gestionnaire de mémoire"""
    return IntelligentMemoryManager()


def get_shared_memory() -> SharedMemory:
    """Obtenir l'instance de mémoire partagée"""
    return SharedMemory()


if __name__ == "__main__":
    print("=== Sharingan OS - Intelligent Memory Manager ===\n")
    
    mem = get_memory_manager()
    
    mem.store("test_key", {"value": "test_data"}, category="conversation", priority="MEDIUM", tags=["test"])
    
    result = mem.retrieve("test_key")
    print(f"Stored and retrieved: {result}")
    
    mem.update_context("current_task", {"task": "testing memory", "progress": 50})
    context = mem.get_context()
    print(f"Context: {context}")
    
    mem.store("error_1", {"error": "Something failed"}, category="error", priority="HIGH", tags=["error"])
    mem.store("error_2", {"error": "Another error"}, category="error", priority="HIGH", tags=["error"])
    
    analysis = mem.analyze_and_recommend()
    print(f"\nAnalysis: {json.dumps(analysis, indent=2, default=str)}")
    
    state = mem.get_full_state()
    print(f"\nFull State: {json.dumps(state, indent=2, default=str)}")
    
    mem.cleanup_expired()
    mem.cleanup_low_priority()
    
    print("\nMemory manager test completed!")
