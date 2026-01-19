# -*- coding: utf-8 -*-
"""
AI Providers Optimization System
Cache intelligent, batch processing, et optimisation coûts
"""

import time
import asyncio
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("ai_optimization")

class AIRequestCache:
    """
    Cache intelligent pour les requêtes AI
    Évite les appels répétés et optimise les coûts
    """

    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.stats = {
            'hits': 0,
            'misses': 0,
            'saved_cost': 0.0,
            'saved_tokens': 0
        }

    def get_cache_key(self, messages: List[Dict], **kwargs) -> str:
        """Génère une clé de cache basée sur le contenu"""
        import hashlib

        # Normaliser les messages pour le cache
        normalized = []
        for msg in messages:
            normalized.append({
                'role': msg.get('role'),
                'content': msg.get('content', '')[:500]  # Limiter la taille
            })

        # Ajouter les paramètres importants
        cache_data = {
            'messages': normalized,
            'temperature': kwargs.get('temperature', 0.7),
            'max_tokens': kwargs.get('max_tokens', 1000),
            'model': kwargs.get('model')
        }

        # Créer hash
        cache_str = str(sorted(cache_data.items()))
        return hashlib.sha256(cache_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Récupère du cache si disponible et valide"""
        if key in self.cache:
            entry = self.cache[key]
            current_time = time.time()

            # Vérifier TTL
            if current_time - entry['timestamp'] < entry['ttl']:
                self.stats['hits'] += 1
                entry['last_access'] = current_time
                return entry['response']
            else:
                # Expiré, supprimer
                del self.cache[key]

        self.stats['misses'] += 1
        return None

    def set(self, key: str, response: Dict[str, Any], ttl: int = 3600):
        """Stocke dans le cache"""
        self.cache[key] = {
            'response': response,
            'timestamp': time.time(),
            'last_access': time.time(),
            'ttl': ttl,
            'cost': response.get('cost', 0),
            'tokens': response.get('tokens_used', 0)
        }

        # Éviction LRU si nécessaire
        if len(self.cache) > self.max_size:
            # Supprimer l'entrée la moins récemment utilisée
            oldest_key = min(self.cache.keys(),
                           key=lambda k: self.cache[k]['last_access'])
            removed = self.cache.pop(oldest_key)
            self.stats['saved_cost'] += removed.get('cost', 0)
            self.stats['saved_tokens'] += removed.get('tokens', 0)

    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0

        return {
            'cache_size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': hit_rate,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'cost_saved': self.stats['saved_cost'],
            'tokens_saved': self.stats['saved_tokens']
        }

    def clear_expired(self):
        """Nettoie les entrées expirées"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry['timestamp'] > entry['ttl']
        ]

        for key in expired_keys:
            removed = self.cache.pop(key)
            self.stats['saved_cost'] += removed.get('cost', 0)
            self.stats['saved_tokens'] += removed.get('tokens', 0)

class BatchProcessor:
    """
    Traitement par lots pour optimiser les appels API
    Regroupe les requêtes similaires pour réduire les coûts
    """

    def __init__(self, batch_window: float = 0.5):
        self.batch_window = batch_window  # secondes
        self.pending_batches: Dict[str, List[Dict]] = {}
        self.batch_timer: Optional[threading.Timer] = None

    def add_to_batch(self, provider: str, request: Dict) -> asyncio.Future:
        """Ajoute une requête au lot et retourne une Future"""
        if provider not in self.pending_batches:
            self.pending_batches[provider] = []

        future = asyncio.Future()
        self.pending_batches[provider].append({
            'request': request,
            'future': future,
            'timestamp': time.time()
        })

        # Démarrer le timer si pas déjà actif
        if self.batch_timer is None:
            self.batch_timer = threading.Timer(self.batch_window, self._process_batches)
            self.batch_timer.start()

        return future

    def _process_batches(self):
        """Traite tous les lots en attente"""
        for provider, requests in self.pending_batches.items():
            if requests:
                self._process_provider_batch(provider, requests)

        self.pending_batches.clear()
        self.batch_timer = None

    def _process_provider_batch(self, provider: str, requests: List[Dict]):
        """Traite un lot pour un provider spécifique"""
        try:
            # NOTE: Cette fonction nécessite une vraie implémentation d'APIs AI
            # Pour l'instant, marquer toutes les requêtes comme échouées
            error_msg = f"Batch processing not implemented for {provider}"

            for request_data in requests:
                future = request_data['future']
                if not future.done():
                    future.set_exception(RuntimeError(error_msg))

        except Exception as e:
            logger.error(f"Batch processing error for {provider}: {e}")
            # En cas d'erreur, résoudre toutes les futures avec l'erreur
            for request_data in requests:
                if not request_data['future'].done():
                    request_data['future'].set_exception(e)

class CostOptimizer:
    """
    Optimisation automatique des coûts d'utilisation IA
    """

    def __init__(self):
        self.cost_history: List[Dict] = []
        self.budget_limits = {
            'daily': 5.0,    # $5 par jour
            'monthly': 100.0 # $100 par mois
        }
        self.current_spending = {
            'daily': 0.0,
            'monthly': 0.0,
            'last_reset_daily': time.time(),
            'last_reset_monthly': time.time()
        }

    def should_use_provider(self, provider: str, estimated_cost: float) -> bool:
        """Détermine si on peut utiliser un provider selon le budget"""
        self._update_spending()

        # Vérifier limites
        if self.current_spending['daily'] + estimated_cost > self.budget_limits['daily']:
            logger.warning(f"Daily budget limit reached for {provider}")
            return False

        if self.current_spending['monthly'] + estimated_cost > self.budget_limits['monthly']:
            logger.warning(f"Monthly budget limit reached for {provider}")
            return False

        return True

    def record_cost(self, provider: str, cost: float, tokens: int):
        """Enregistre un coût dépensé"""
        self.current_spending['daily'] += cost
        self.current_spending['monthly'] += cost

        self.cost_history.append({
            'provider': provider,
            'cost': cost,
            'tokens': tokens,
            'timestamp': datetime.now().isoformat()
        })

        # Garder seulement les 1000 dernières entrées
        if len(self.cost_history) > 1000:
            self.cost_history = self.cost_history[-1000:]

    def _update_spending(self):
        """Met à jour les compteurs de dépenses"""
        current_time = time.time()

        # Reset quotidien (toutes les 24h)
        if current_time - self.current_spending['last_reset_daily'] > 86400:
            self.current_spending['daily'] = 0.0
            self.current_spending['last_reset_daily'] = current_time

        # Reset mensuel (tous les 30 jours)
        if current_time - self.current_spending['last_reset_monthly'] > 2592000:
            self.current_spending['monthly'] = 0.0
            self.current_spending['last_reset_monthly'] = current_time

    def get_cost_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de coût"""
        total_cost = sum(entry['cost'] for entry in self.cost_history)
        total_tokens = sum(entry['tokens'] for entry in self.cost_history)

        provider_costs = {}
        for entry in self.cost_history:
            provider = entry['provider']
            if provider not in provider_costs:
                provider_costs[provider] = 0.0
            provider_costs[provider] += entry['cost']

        return {
            'total_cost': total_cost,
            'total_tokens': total_tokens,
            'avg_cost_per_token': total_cost / total_tokens if total_tokens > 0 else 0,
            'current_daily': self.current_spending['daily'],
            'current_monthly': self.current_spending['monthly'],
            'daily_limit': self.budget_limits['daily'],
            'monthly_limit': self.budget_limits['monthly'],
            'provider_breakdown': provider_costs,
            'history_size': len(self.cost_history)
        }

    def optimize_request(self, messages: List[Dict], provider: str) -> Dict[str, Any]:
        """Optimise une requête pour minimiser les coûts"""
        # Compter les tokens approximativement
        total_chars = sum(len(msg.get('content', '')) for msg in messages)
        estimated_tokens = total_chars // 4  # Approximation

        # Estimer le coût selon le provider
        cost_per_token = {
            'tgpt': 0.0,      # Gratuit
            'ollama': 0.0,    # Local
            'minimax': 0.002, # $0.002/token
            'glm4': 0.0015,   # $0.0015/token
        }.get(provider, 0.001)

        estimated_cost = estimated_tokens * cost_per_token

        return {
            'estimated_tokens': estimated_tokens,
            'estimated_cost': estimated_cost,
            'can_proceed': self.should_use_provider(provider, estimated_cost),
            'suggested_provider': self._suggest_alternative_provider(provider, estimated_cost)
        }

    def _suggest_alternative_provider(self, current_provider: str, estimated_cost: float) -> str:
        """Suggère un provider alternatif si le budget est dépassé"""
        if self.should_use_provider(current_provider, estimated_cost):
            return current_provider

        # Providers par ordre de coût croissant
        fallback_order = ['ollama', 'tgpt', 'glm4', 'minimax']

        for provider in fallback_order:
            if provider != current_provider and self.should_use_provider(provider, 0.001):
                return provider

        return current_provider  # Aucun autre disponible

class AIOptimizationManager:
    """
    Gestionnaire central des optimisations AI
    """

    def __init__(self):
        self.cache = AIRequestCache()
        self.batch_processor = BatchProcessor()
        self.cost_optimizer = CostOptimizer()

        # Statistiques globales
        self.stats = {
            'total_requests': 0,
            'cached_requests': 0,
            'batched_requests': 0,
            'cost_optimized': 0,
            'last_optimization': time.time()
        }

    def optimize_request(self, messages: List[Dict], provider: str, **kwargs) -> Dict[str, Any]:
        """
        Optimise complètement une requête AI
        """
        self.stats['total_requests'] += 1

        # 1. Vérifier le cache
        cache_key = self.cache.get_cache_key(messages, **kwargs)
        cached_response = self.cache.get(cache_key)

        if cached_response:
            self.stats['cached_requests'] += 1
            return {
                'response': cached_response,
                'source': 'cache',
                'cached': True
            }

        # 2. Optimisation coût
        cost_analysis = self.cost_optimizer.optimize_request(messages, provider)

        if not cost_analysis['can_proceed']:
            suggested_provider = cost_analysis['suggested_provider']
            if suggested_provider != provider:
                self.stats['cost_optimized'] += 1
                return {
                    'error': f"Budget dépassé pour {provider}",
                    'suggested_provider': suggested_provider,
                    'cost_analysis': cost_analysis
                }

        # 3. Batch processing (si applicable)
        if self._should_batch(messages):
            future = self.batch_processor.add_to_batch(provider, {
                'messages': messages,
                'provider': provider,
                **kwargs
            })
            self.stats['batched_requests'] += 1

            # Attendre le résultat du batch
            try:
                result = future.result(timeout=30)  # 30 secondes timeout
                self.cache.set(cache_key, result['response'])
                self.cost_optimizer.record_cost(
                    provider,
                    result.get('cost', 0),
                    result.get('tokens_used', 0)
                )
                return result
            except Exception as e:
                return {'error': f'Batch processing failed: {e}'}

        # 4. Requête normale (à implémenter selon le provider réel)
        return {
            'response': f"Mock response from {provider}",
            'source': 'direct',
            'cost_analysis': cost_analysis
        }

    def _should_batch(self, messages: List[Dict]) -> bool:
        """Détermine si une requête doit être traitée en batch"""
        # Pour l'instant, traiter en batch les requêtes courtes similaires
        if len(messages) == 1:
            content = messages[0].get('content', '')
            return len(content.split()) < 50  # Moins de 50 mots
        return False

    def run_optimization(self) -> Dict[str, Any]:
        """Exécute toutes les optimisations périodiques"""
        results = {
            'cache_cleaned': 0,
            'cost_reset': False,
            'timestamp': datetime.now().isoformat()
        }

        # Nettoyer cache expiré
        self.cache.clear_expired()
        results['cache_cleaned'] = len(self.cache.cache)

        # Reset coûts si nécessaire
        self.cost_optimizer._update_spending()
        results['cost_reset'] = True

        self.stats['last_optimization'] = time.time()

        return results

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Retourne toutes les statistiques d'optimisation"""
        return {
            'ai_stats': self.stats,
            'cache_stats': self.cache.get_stats(),
            'cost_stats': self.cost_optimizer.get_cost_stats(),
            'batch_active': len(self.batch_processor.pending_batches) > 0
        }

# Instance globale
_ai_optimizer = None

def get_ai_optimizer() -> AIOptimizationManager:
    """Get global AI optimizer instance"""
    global _ai_optimizer
    if _ai_optimizer is None:
        _ai_optimizer = AIOptimizationManager()
    return _ai_optimizer

if __name__ == "__main__":
    print("[AI OPTIMIZATION] Sharingan AI Optimization System")
    print("=" * 60)

    # Test du système
    optimizer = get_ai_optimizer()

    # Test cache
    messages = [{"role": "user", "content": "Hello world"}]
    key = optimizer.cache.get_cache_key(messages)
    optimizer.cache.set(key, {"response": "Hello back!"})

    cached = optimizer.cache.get(key)
    print(f"Cache test: {'PASSED' if cached else 'FAILED'}")

    # Test coût
    cost_stats = optimizer.cost_optimizer.get_cost_stats()
    print(f"Cost tracking initialized: {cost_stats['total_cost'] == 0.0}")

    print("\nAI optimization system ready!")