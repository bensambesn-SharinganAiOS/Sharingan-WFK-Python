#!/usr/bin/env python3
"""
Integrated Memory System
Système intégré connectant Genome Memory + AI Memory + Context + Vector Memory
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Ajouter le répertoire au path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from genome_memory import GenomeMemory
from ai_memory_manager import IntelligentMemoryManager, MemoryPriority
from context_manager import ContextManager

logger = logging.getLogger("sharingan.integrated_memory")

class IntegratedMemorySystem:
    """
    Système de mémoire intégré qui connecte tous les systèmes de mémoire :
    - Genome Memory (ADN long terme)
    - AI Memory Manager (cerveau moyen terme)
    - Context Manager (conversation court terme)
    """

    def __init__(self):
        self.genome = GenomeMemory()
        self.ai_memory = IntelligentMemoryManager()
        self.context = ContextManager()
        self.learning_patterns = {
            "successful_actions": [],
            "failed_actions": [],
            "user_patterns": [],
            "system_evolution": []
        }

        # Charger les patterns d'apprentissage
        self._load_learning_patterns()

        logger.info("Integrated Memory System initialized")

    def _load_learning_patterns(self):
        """Charger les patterns d'apprentissage"""
        patterns_file = current_dir / "data" / "learning_patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    self.learning_patterns = json.load(f)
            except:
                self.learning_patterns = {
                    "successful_actions": [],
                    "failed_actions": [],
                    "user_patterns": [],
                    "system_evolution": []
                }

    def _save_learning_patterns(self):
        """Sauvegarder les patterns d'apprentissage"""
        patterns_file = current_dir / "data" / "learning_patterns.json"
        patterns_file.parent.mkdir(exist_ok=True)
        with open(patterns_file, 'w') as f:
            json.dump(self.learning_patterns, f, indent=2)

    def learn_from_action(self, action: str, result: Dict, success: bool,
                         category: str = "feature", source: str = "system"):
        """
        Apprendre d'une action et créer automatiquement des gènes
        """
        try:
            # Créer un gène depuis l'action
            gene_key = self.genome.mutate(
                f"action_{action.replace(' ', '_')}",
                {
                    "action": action,
                    "result": result,
                    "success": success,
                    "timestamp": datetime.now().isoformat(),
                    "category": category
                },
                category,
                source=source,
                tags=["learned", "action", category]
            )

            # Enregistrer dans AI memory
            priority = "HIGH" if success else "MEDIUM"
            self.ai_memory.store(
                f"learned_{action}",
                {
                    "action": action,
                    "result": result,
                    "success": success,
                    "gene_key": gene_key
                },
                category="learning",
                priority=priority,
                tags=["learned", "action"]
            )

            # Ajouter aux patterns d'apprentissage
            pattern_entry = {
                "action": action,
                "result": str(result),
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "gene_created": gene_key
            }

            if success:
                self.learning_patterns["successful_actions"].append(pattern_entry)
                self.genome.record_success(gene_key)
            else:
                self.learning_patterns["failed_actions"].append(pattern_entry)
                self.genome.record_failure(gene_key)

            self._save_learning_patterns()
            logger.info(f"Learned from action: {action} (success: {success})")

        except Exception as e:
            logger.error(f"Error learning from action: {e}")

    def process_user_input(self, user_input: str) -> Dict:
        """
        Traiter une entrée utilisateur avec tous les systèmes de mémoire
        """
        result = {
            "instinct_matched": False,
            "genome_knowledge": None,
            "ai_memory_context": None,
            "response_suggestions": []
        }

        # 1. Vérifier les instincts
        instinct = self.genome.match_instinct(user_input)
        if instinct:
            result["instinct_matched"] = True
            result["instinct_response"] = instinct["response"]
            return result

        # 2. Chercher dans la connaissance genome
        # Analyser les mots-clés de l'input
        keywords = user_input.lower().split()
        relevant_genes = []

        for keyword in keywords:
            if len(keyword) > 3:  # Éviter les mots trop courts
                for gene in self.genome.genes.values():
                    if keyword in str(gene.data).lower() or keyword in gene.tags:
                        relevant_genes.append(gene)

        if relevant_genes:
            # Prendre le gène le plus pertinent (priorité + succès)
            best_gene = max(relevant_genes, key=lambda g: (g.priority, g.success_rate))
            result["genome_knowledge"] = {
                "gene_key": f"{best_gene.category}_{best_gene.key}",
                "data": best_gene.data,
                "relevance": best_gene.success_rate
            }

        # 3. Chercher dans AI memory pour du contexte similaire
        similar_context = self.ai_memory.retrieve_by_tag("conversation")
        if similar_context:
            result["ai_memory_context"] = similar_context[:3]  # Top 3

        # 4. Générer des suggestions de réponse basées sur l'apprentissage
        suggestions = self._generate_response_suggestions(user_input)
        result["response_suggestions"] = suggestions

        return result

    def _generate_response_suggestions(self, user_input: str) -> List[str]:
        """Générer des suggestions de réponse basées sur l'apprentissage"""
        suggestions = []

        # Chercher des patterns similaires dans les succès passés
        for pattern in self.learning_patterns["successful_actions"][-10:]:  # Derniers 10
            if any(word in pattern["action"].lower() for word in user_input.lower().split()):
                suggestions.append(f"Basé sur l'expérience: {pattern['result'][:100]}...")

        # Chercher des gènes pertinents
        for gene_key, gene in self.genome.genes.items():
            if gene.success_rate > 0.7:  # Seulement les gènes très réussis
                if any(tag in user_input.lower() for tag in gene.tags):
                    suggestions.append(f"Connaissance {gene.category}: {str(gene.data)[:100]}...")

        return suggestions[:3]  # Maximum 3 suggestions

    def auto_evolve(self) -> Dict:
        """
        Évolution automatique du système basée sur les métriques
        """
        evolution_result = {
            "genome_evolution": self.genome.evolve(),
            "memory_cleanup": self.ai_memory.cleanup_expired() + self.ai_memory.cleanup_low_priority(),
            "patterns_analyzed": len(self.learning_patterns["successful_actions"]),
            "recommendations": []
        }

        # Générer des recommandations d'évolution
        stats = self.genome.get_statistics()

        if stats["total_genes"] < 10:
            evolution_result["recommendations"].append("Créer plus de gènes de base")

        if stats["total_instincts"] < 5:
            evolution_result["recommendations"].append("Ajouter plus d'instincts")

        if len(self.learning_patterns["successful_actions"]) < 5:
            evolution_result["recommendations"].append("Plus d'actions réussies nécessaires pour l'apprentissage")

        return evolution_result

    def get_system_health(self) -> Dict:
        """État de santé complet du système de mémoire"""
        genome_stats = self.genome.get_statistics()
        ai_memory_state = self.ai_memory.get_full_state()
        context_tokens = self.context.get_token_count() if hasattr(self.context, 'get_token_count') else 0

        return {
            "genome_memory": {
                "genes": genome_stats["total_genes"],
                "instincts": genome_stats["total_instincts"],
                "mutations": genome_stats["total_mutations"],
                "categories": list(genome_stats["by_category"].keys()),
                "health_score": min(100, genome_stats["total_genes"] * 10 + genome_stats["total_instincts"] * 5)
            },
            "ai_memory": {
                "items": ai_memory_state["memory_items"],
                "context_keys": ai_memory_state["context_keys"],
                "learned_patterns": ai_memory_state["learned_patterns"],
                "health_score": min(100, ai_memory_state["memory_items"] * 20)
            },
            "context": {
                "current_tokens": context_tokens,
                "max_tokens": self.context.max_tokens if hasattr(self.context, 'max_tokens') else 100000,
                "health_score": min(100, 100 - (context_tokens / 100000) * 100)
            },
            "learning": {
                "successful_actions": len(self.learning_patterns["successful_actions"]),
                "failed_actions": len(self.learning_patterns["failed_actions"]),
                "evolution_events": len(self.learning_patterns["system_evolution"]),
                "health_score": min(100, len(self.learning_patterns["successful_actions"]) * 10)
            },
            "overall_health": 0  # Calculé ci-dessous
        }

    def get_best_action_for_context(self, context: str) -> Optional[Dict]:
        """Obtenir la meilleure action apprise pour un contexte"""
        # Chercher dans les patterns réussis
        for pattern in reversed(self.learning_patterns["successful_actions"]):
            if context.lower() in pattern["action"].lower():
                return pattern

        # Chercher dans les gènes
        for gene in self.genome.get_best_genes(10):
            if context.lower() in str(gene.data).lower():
                return {
                    "action": f"gene_{gene.key}",
                    "result": gene.data,
                    "confidence": gene.success_rate
                }

        return None

    def __str__(self):
        health = self.get_system_health()
        return f"""Integrated Memory System:
  Genome: {health['genome_memory']['genes']} genes, {health['genome_memory']['instincts']} instincts
  AI Memory: {health['ai_memory']['items']} items
  Learning: {health['learning']['successful_actions']} successful actions
  Overall Health: {health.get('overall_health', 'Unknown')}%"""


# Fonction globale pour accéder au système intégré
_integrated_memory = None

def get_integrated_memory() -> IntegratedMemorySystem:
    """Singleton pour le système de mémoire intégré"""
    global _integrated_memory
    if _integrated_memory is None:
        _integrated_memory = IntegratedMemorySystem()
    return _integrated_memory


if __name__ == "__main__":
    print("=== SHARINGAN INTEGRATED MEMORY SYSTEM ===\n")

    memory_system = get_integrated_memory()

    print("Système initialisé:")
    print(memory_system)

    print("\n=== TEST DES CAPACITÉS ===")

    # Tester l'apprentissage
    print("\n1. Test d'apprentissage:")
    memory_system.learn_from_action(
        "nmap_scan",
        {"target": "localhost", "ports_found": [22, 80, 443]},
        success=True,
        category="security"
    )
    print("   Apprentissage d'un scan nmap réussi")

    # Tester le traitement d'input utilisateur
    print("\n2. Test de traitement d'input:")
    result = memory_system.process_user_input("bonjour")
    print(f"   Input 'bonjour': instinct trouvé = {result['instinct_matched']}")

    result = memory_system.process_user_input("scan réseau")
    print(f"   Input 'scan réseau': connaissance trouvée = {result['genome_knowledge'] is not None}")

    # État de santé
    print("\n3. État de santé:")
    health = memory_system.get_system_health()
    print(f"   Genome health: {health['genome_memory']['health_score']}%")
    print(f"   AI Memory health: {health['ai_memory']['health_score']}%")
    print(f"   Learning health: {health['learning']['health_score']}%")

    # Évolution automatique
    print("\n4. Évolution automatique:")
    evolution = memory_system.auto_evolve()
    print(f"   Gènes éliminés: {evolution['genome_evolution']['eliminated']}")
    print(f"   Items nettoyés: {evolution['memory_cleanup']}")

    print("\n✅ Système de mémoire intégré opérationnel !")