#!/usr/bin/env python3
"""
Sharingan OS - NLP/RAG System
Système NLP + RAG local pour autonomie complète.
Utilise vector search sur documentation + code local.
Auteur: Bensambe
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
import faiss
import pickle
from datetime import datetime

# Ajouter le répertoire parent au path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

logger = logging.getLogger("sharingan.nlp_rag")


@dataclass
class VectorMemory:
    """Mémoire vectorielle pour NLP/RAG"""
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.vectors = np.zeros((dimension,))
        self.metadata = {}
        self.index = {}
        self.last_updated = str(datetime.now())
    
    def add_vector(self, text: str, metadata: Optional[Dict] = None):
        """Ajoute un vecteur à la mémoire"""
        try:
            # Utiliser sentence transformers simples pour l'instantané
            words = text.lower().split()
            # Créer un vecteur simple (moyenne des embeddings)
            vector = np.mean([self._word_to_vector(word) for word in words if word])
            
            vector_id = len(self.vectors)
            self.vectors[vector_id % self.dimension] = vector
            self.index[vector_id] = text
            self.metadata[vector_id] = metadata or {}
            self.last_updated = str(datetime.now())
            
            return vector_id
        except Exception as e:
            logger.error(f"Error adding vector: {e}")
            return None
    
    def _word_to_vector(self, word: str) -> np.ndarray:
        """Convertir un mot en vecteur simple"""
        # Hash simple du mot
        hash_val = hash(word) % 1000
        return np.array([hash_val / 1000.0])
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Recherche les vecteurs les plus pertinents"""
        try:
            query_vec = self._word_to_vector(query)
            similarities = []
            
            for i, vector in enumerate(self.vectors):
                if np.linalg.norm(vector) > 0:
                    similarity = np.dot(query_vec, vector) / (np.linalg.norm(vector) * np.linalg.norm(vector))
                    similarities.append((self.index.get(i, f"Vector {i}"), similarity))
            
            # Trier par similarité
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []
    
    def get_vector(self, vector_id: int) -> Optional[np.ndarray]:
        """Obtenir un vecteur par ID"""
        if 0 <= vector_id < len(self.vectors):
            return self.vectors[vector_id]
        return None
    
    def get_status(self) -> Dict:
        """Obtenir le statut du système RAG"""
        return {
            "vector_memory": {
                "vectors_count": len(self.vectors),
                "dimension": self.vector_memory.dimension,
                "last_updated": self.vector_memory.last_updated
            },
            "rag_system": {
                "context_window": 5,
                "context_history_count": len(self.context_history),
                "knowledge_base_size": len(self.knowledge_base),
                "last_updated": self.last_updated
            },
            "index_size": len(self.vector_memory.index),
            "ready": True
        }
    
    def start(self):
        """Démarrer le système RAG"""
        logger.info("Starting NLP/RAG system...")
        logger.info(f"Vector memory: {len(self.vectors)} vectors")
        logger.info(f"Knowledge base: {len(self.knowledge_base)} items")
        logger.info("NLP/RAG system ready")
    
    def stop(self):
        """Arrêter le système RAG"""
        logger.info("Stopping NLP/RAG system...")
        self.vector_memory = None
        self.context_history = []
        self.knowledge_base = {}
        self.index = {}
        logger.info("NLP/RAG system stopped")
    
    def add_context(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Ajoute du contexte au RAG"""
        try:
            # Ajouter à la mémoire vectorielle
            vector_id = self.vector_memory.add_vector(content, metadata)
            
            # Mettre à jour l'index
            self.index[vector_id] = f"{role}: {content[:50]}..."
            
            # Garder les derniers messages
            if not hasattr(self, 'context_history'):
                self.context_history = []
            self.context_history.append({"role": role, "content": content, "timestamp": str(datetime.now())})
            
            # Limiter la taille de l'historique
            if len(self.context_history) > self.context_window:
                self.context_history = self.context_history[-self.context_window:]
            
            self.last_updated = str(datetime.now())
            
        except Exception as e:
            logger.error(f"Error adding context to RAG: {e}")
    
    def add_knowledge(self, key: str, data: Dict):
        """Ajoute à la base de connaissances locales"""
        self.knowledge_base[key] = data
        self.last_updated = str(datetime.now())
    
    def get_knowledge(self, key: str) -> Optional[Dict]:
        """Obtenir une connaissance de la base"""
        return self.knowledge_base.get(key)
    
    def get_status(self) -> Dict:
        """Obtenir le statut du système RAG"""
        return {
            "vector_memory": {
                "vectors_count": len(self.vector_memory.vectors),
                "dimension": self.vector_memory.dimension,
                "last_updated": self.vector_memory.last_updated
            },
            "rag_system": {
                "context_window": self.context_window,
                "context_history_count": len(self.context_history),
                "knowledge_base_size": len(self.knowledge_base),
                "last_updated": self.last_updated
            },
            "index_size": len(self.vector_memory.index),
            "ready": True
        }
    
    def get_context(self, query: str) -> Optional[str]:
        """Récupère le contexte pertinent pour une query"""
        try:
            # Recherche dans l'historique
            for msg in reversed(self.context_history):
                if query.lower() in msg["content"].lower():
                    return msg["content"]
            return None
        except Exception as e:
            return None


def get_nlp_rag_system() -> NLPRAGSystem:
    """Get singleton instance"""
    return NLPRAGSystem()


def get_vector_memory() -> VectorMemory:
    """Get singleton instance"""
    return VectorMemory()


def get_rag_system() -> NLPRAGSystem:
    """Get singleton instance"""
    return NLPRAGSystem()


__all__ = ["VectorMemory", "get_vector_memory", "get_rag_system", "NLPRAGSystem"]]