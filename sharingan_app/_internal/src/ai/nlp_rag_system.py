# -*- coding: utf-8 -*-
"""
Sharingan OS - NLP/RAG System
Système NLP + RAG local pour autonomie complète.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

logger = logging.getLogger("sharingan.nlp_rag")


@dataclass
class VectorMemory:
    """Mémoire vectorielle pour NLP/RAG"""
    dimension: int = 1536

    def __post_init__(self):
        self.vectors = []
        self.metadata = {}
        self.index = {}
        self.last_updated = str(datetime.now())

    def add_vector(self, text: str, metadata: Optional[Dict] = None) -> Optional[int]:
        """Ajoute un vecteur à la mémoire"""
        try:
            vector_id = len(self.index)
            self.index[vector_id] = text
            self.metadata[vector_id] = metadata or {}
            self.last_updated = str(datetime.now())
            return vector_id
        except Exception:
            return None

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Recherche simple"""
        results = []
        for text_id, text in self.index.items():
            if query.lower() in text.lower():
                results.append((text, 0.9))
        return results[:top_k]


class NLPRAGSystem:
    """Système NLP/RAG principal"""

    def __init__(self):
        self.vector_memory = VectorMemory()
        self.context_history = []
        self.knowledge_base = {}
        self.context_window = 5
        self.last_updated = str(datetime.now())

    def add_context(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Ajoute du contexte"""
        vector_id = self.vector_memory.add_vector(content, metadata)
        if vector_id is not None:
            self.context_history.append({
                "role": role,
                "content": content,
                "timestamp": str(datetime.now())
            })
            if len(self.context_history) > self.context_window:
                self.context_history = self.context_history[-self.context_window:]
        self.last_updated = str(datetime.now())

    def get_status(self) -> Dict:
        """Statut du système"""
        return {
            "vector_memory": {
                "vectors_count": len(self.vector_memory.index),
                "dimension": self.vector_memory.dimension,
                "last_updated": self.vector_memory.last_updated
            },
            "rag_system": {
                "context_window": self.context_window,
                "context_history_count": len(self.context_history),
                "knowledge_base_size": len(self.knowledge_base),
                "last_updated": self.last_updated
            },
            "ready": True
        }


def get_nlp_rag_system() -> NLPRAGSystem:
    return NLPRAGSystem()


def get_vector_memory() -> VectorMemory:
    return VectorMemory()


def get_rag_system() -> NLPRAGSystem:
    return NLPRAGSystem()


__all__ = ["VectorMemory", "NLPRAGSystem", "get_vector_memory", "get_rag_system"]