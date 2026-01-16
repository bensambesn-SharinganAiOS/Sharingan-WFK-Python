#!/usr/bin/env python3
"""
Instinct Layer - Genome-Powered Pre-Processing
Nouvelle couche qui vérifie les instincts AVANT tout traitement.
Approche additive : ne modifie rien, s'exécute en premier.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add _internal to path
_internal_dir = Path(__file__).parent
sys.path.insert(0, str(_internal_dir))

from genome_memory import get_genome_memory

class InstinctLayer:
    """
    Nouvelle couche additive - vérifie instincts avant traitement.
    
    Flux :
    1. Vérifier instinct pattern match
    2. Vérifier patterns d'échec connus
    3. Si match → retourner réponse instinctive
    4. Sinon → retourner None (continuer traitement normal)
    """
    
    def __init__(self):
        self.genome = get_genome_memory()
        self.enabled = True
    
    def check(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Vérifie si l'input déclenche un instinct.
        
        Returns:
            - Dict avec réponse instinctive si match
            - None si pas de match (continuer traitement normal)
        """
        if not self.enabled:
            return None
        
        query_lower = query.lower().strip()
        
        # 1. Vérifier instinct pattern match
        instinct_match = self.genome.match_instinct(query_lower)
        if instinct_match:
            return {
                "type": "instinct_response",
                "confidence": instinct_match.get('success_rate', 0.5),
                "response": instinct_match.get('response'),
                "source": "genome_pattern_match",
                "triggered_by": instinct_match.get('pattern'),
                "is_instinct": True
            }
        
        # 2. Vérifier patterns d'échec connus
        failure_genes = self.genome.find_genes(
            category="failure_patterns", 
            min_priority=50
        )
        
        for gene in failure_genes:
            if gene.key.lower() in query_lower:
                return {
                    "type": "failure_warning",
                    "confidence": gene.success_rate,
                    "warning": True,
                    "message": f"Approche '{gene.key}' a échoué {gene.usage_count}x avant",
                    "gene_key": gene.key,
                    "failure_data": gene.data,
                    "source": "genome_failure_memory",
                    "is_instinct": True
                }
        
        # 3. Pas de match → continuer traitement normal
        return None


def get_instinct_layer() -> InstinctLayer:
    """Singleton accessor"""
    return InstinctLayer()


def check_instinct(query: str) -> Optional[Dict[str, Any]]:
    """
    Fonction utilitaire simple.
    
    Usage:
        result = check_instinct("bonjour")
        if result:
            print(result['response'])
        else:
            # Traitement normal
            pass
    """
    layer = get_instinct_layer()
    return layer.check(query)


if __name__ == "__main__":
    print("=== INSTINCT LAYER TEST ===\n")
    
    layer = InstinctLayer()
    
    # Test 1: No instinct (should return None)
    print("Test 1: Query sans instinct")
    result = layer.check("，分析してください")  # Japanese
    print(f"  Result: {result}\n")
    
    # Test 2: Create a test instinct
    print("Test 2: Créer un instinct de test")
    layer.genome.add_instinct(
        pattern="test instinct",
        response="Instinct triggered successfully!",
        condition="test"
    )
    print("  Instinct created: 'test instinct'\n")
    
    # Test 3: Trigger the instinct
    print("Test 3: Déclencher l'instinct")
    result = layer.check("test instinct")
    print(f"  Result: {result}\n")
    
    # Test 4: Stats
    print("Test 4: Genome stats")
    stats = layer.genome.get_statistics()
    print(f"  Genes: {stats['total_genes']}")
    print(f"  Instincts: {stats['total_instincts']}")
    
    print("\n✓ Instinct Layer operational!")
