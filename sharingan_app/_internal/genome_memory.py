#!/usr/bin/env python3
"""
Sharingan Genome Memory - ADN du système
Mémoire basée sur l'importance et les mutations, pas sur les conversations.
"""

import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

# Memory optimization system (will be imported when needed)
MEMORY_OPTIMIZATION_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.genome")

class GenePriority(Enum):
    CORE_FUNCTION = 100
    PERFORMANCE = 90
    SECURITY = 95
    FEATURE = 70
    CONVERSATION = 10
    EXPERIMENTAL = 30

class GeneCategory(Enum):
    CORE = "core"
    PERFORMANCE = "performance"
    SECURITY = "security"
    FEATURE = "feature"
    CONVERSATION = "conversation"
    EXPERIMENTAL = "experimental"
    KNOWLEDGE = "knowledge"

@dataclass
class Gene:
    key: str
    data: Dict[str, Any]
    category: str
    priority: int
    created_at: str
    updated_at: str
    success_rate: float = 0.0
    usage_count: int = 0
    mutations: int = 0
    tags: List[str] = field(default_factory=list)
    source: str = "unknown"

@dataclass
class Mutation:
    gene_key: str
    old_value: Any
    new_value: Any
    reason: str
    timestamp: str
    validated: bool = False

class GenomeMemory:
    """
    Système de mémoire ADN - apprend et évolue sans conversations.
    
    Principe: Comme l'ADN biologique
    - only les mutations importantes sont retenues
    - Priorité aux fonctions core et sécurité
    - Apprentissage par succès/échec
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).parent / "data"
        self.base_dir.mkdir(exist_ok=True)
        
        self.genome_file = self.base_dir / "genome_memory.json"
        self.mutations_file = self.base_dir / "genome_mutations.json"
        self.instincts_file = self.base_dir / "genome_instincts.json"
        
        self.genes: Dict[str, Gene] = {}
        self.mutations: List[Mutation] = []
        self.instincts: List[Dict] = []

        # Memory optimization will be initialized when needed

        self._load_all()
        
        self.priority_rules = {
            GeneCategory.CORE: 100,
            GeneCategory.SECURITY: 95,
            GeneCategory.PERFORMANCE: 90,
            GeneCategory.FEATURE: 70,
            GeneCategory.KNOWLEDGE: 50,
            GeneCategory.EXPERIMENTAL: 30,
            GeneCategory.CONVERSATION: 10,
        }
    
    def _load_all(self) -> None:
        self._load_genome()
        self._load_mutations()
        self._load_instincts()
    
    def _load_genome(self) -> None:
        if self.genome_file.exists():
            try:
                with open(self.genome_file, 'r') as f:
                    data = json.load(f)
                    for key, gene_data in data.items():
                        # Skip non-gene entries (capabilities, evolution_history, etc.)
                        if key in ["capabilities", "evolution_history"]:
                            continue
                        # Skip invalid gene formats
                        if not isinstance(gene_data, dict) or "key" not in gene_data or "data" not in gene_data:
                            continue
                        self.genes[key] = Gene(**gene_data)
                logger.info(f"Loaded {len(self.genes)} genes from genome")
            except Exception as e:
                logger.warning(f"Failed to load genome: {e}")
        else:
            logger.info("No genome file found, starting fresh")
    
    def _load_mutations(self) -> None:
        if self.mutations_file.exists():
            try:
                with open(self.mutations_file, 'r') as f:
                    self.mutations = [Mutation(**m) for m in json.load(f)]
                logger.info(f"Loaded {len(self.mutations)} mutations")
            except:
                self.mutations = []
    
    def _load_instincts(self) -> None:
        if self.instincts_file.exists():
            try:
                with open(self.instincts_file, 'r') as f:
                    self.instincts = json.load(f)
            except:
                self.instincts = []
    
    def _save_all(self) -> None:
        self._save_genome()
        self._save_mutations()
        self._save_instincts()
    
    def _save_genome(self) -> None:
        with open(self.genome_file, 'w') as f:
            json.dump({k: v.__dict__ for k, v in self.genes.items()}, f, indent=2, default=str)
    
    def _save_mutations(self) -> None:
        with open(self.mutations_file, 'w') as f:
            json.dump([m.__dict__ for m in self.mutations], f, indent=2, default=str)
    
    def _save_instincts(self) -> None:
        with open(self.instincts_file, 'w') as f:
            json.dump(self.instincts, f, indent=2)
    
    def mutate(self, key: str, data: Dict, category: str, 
               source: str = "system", tags: Optional[List[str]] = None) -> str:
        """
        Crée ou met à jour un gène (mutation).
        Si le gène existe déjà, c'est une mutation.
        """
        priority = self.priority_rules.get(GeneCategory(category), 50)
        now = datetime.now().isoformat()
        
        gene_key = f"{category}_{key}"
        
        if gene_key in self.genes:
            old_gene = self.genes[gene_key]
            mutation = Mutation(
                gene_key=gene_key,
                old_value=old_gene.data,
                new_value=data,
                reason=f"Mutation de {category}",
                timestamp=now
            )
            self.mutations.append(mutation)
            old_gene.mutations += 1
        
        gene = Gene(
            key=gene_key,
            data=data,
            category=category,
            priority=priority,
            created_at=now,
            updated_at=now,
            usage_count=0,
            mutations=self.genes.get(gene_key, Gene("", {}, "", 0, "", "")).mutations + 1,
            tags=tags or [],
            source=source
        )
        
        self.genes[gene_key] = gene
        self._save_all()
        
        return gene_key
    
    def record_success(self, gene_key: str) -> None:
        """Enregistre un succès pour un gène"""
        if gene_key in self.genes:
            gene = self.genes[gene_key]
            gene.usage_count += 1
            gene.success_rate = min(1.0, gene.success_rate + 0.05)
            gene.updated_at = datetime.now().isoformat()
            self._save_genome()
    
    def record_failure(self, gene_key: str) -> None:
        """Enregistre un échec pour un gène"""
        if gene_key in self.genes:
            gene = self.genes[gene_key]
            gene.usage_count += 1
            gene.success_rate = max(0.0, gene.success_rate - 0.1)
            gene.updated_at = datetime.now().isoformat()
            self._save_genome()
    
    def get_gene(self, key: str, category: str = "knowledge") -> Optional[Gene]:
        """Récupère un gène"""
        gene_key = f"{category}_{key}"
        return self.genes.get(gene_key)
    
    def find_genes(self, category: Optional[str] = None, 
                   min_priority: int = 0,
                   tags: Optional[List[str]] = None) -> List[Gene]:
        """Trouve des gènes par critères"""
        results = []
        for gene in self.genes.values():
            if category and gene.category != category:
                continue
            if gene.priority < min_priority:
                continue
            if tags and not any(t in gene.tags for t in tags):
                continue
            results.append(gene)
        return sorted(results, key=lambda g: g.priority, reverse=True)
    
    def get_best_genes(self, limit: int = 10) -> List[Gene]:
        """Récupère les meilleurs gènes (high priority, high success rate)"""
        genes = list(self.genes.values())
        genes.sort(key=lambda g: (g.priority, g.success_rate), reverse=True)
        return genes[:limit]

    def optimize_memory(self) -> Dict[str, Any]:
        """
        Run memory optimization on genome data
        Returns optimization statistics
        """
        stats = {
            'genes_before': len(self.genes),
            'old_genes_cleaned': 0,
            'memory_optimized': False,
            'timestamp': datetime.now().isoformat()
        }

        try:
            # Clean old genes with low success rate
            cutoff_time = time.time() - (90 * 24 * 60 * 60)  # 90 days
            genes_to_remove = []

            for gene_key, gene in self.genes.items():
                # Remove genes with very low success and few usages
                if (gene.success_rate < 0.1 and
                    gene.usage_count < 3 and
                    gene.created_at):
                    try:
                        gene_time = datetime.fromisoformat(gene.created_at).timestamp()
                        if gene_time < cutoff_time:
                            genes_to_remove.append(gene_key)
                            stats['old_genes_cleaned'] += 1
                    except (ValueError, AttributeError):
                        # Skip genes with invalid timestamps
                        continue

            # Remove old genes
            for gene_key in genes_to_remove:
                del self.genes[gene_key]

            # Save optimized genome
            if genes_to_remove:
                self._save_genome()

            stats['genes_after'] = len(self.genes)
            stats['memory_optimized'] = True

            logger.info(f"Genome memory optimized: {stats}")

        except Exception as e:
            logger.error(f"Genome memory optimization failed: {e}")
            stats['error'] = str(e)

        return stats
    
    def add_instinct(self, pattern: str, response: str, 
                     condition: Optional[str] = None) -> None:
        """Ajoute un instinct - réponse automatique à un pattern"""
        instinct = {
            "pattern": pattern,
            "response": response,
            "condition": condition,
            "trigger_count": 0,
            "success_rate": 0.5,
            "created_at": datetime.now().isoformat()
        }
        self.instincts.append(instinct)
        self._save_instincts()
    
    def match_instinct(self, input_text: str) -> Optional[Dict]:
        """Cherche un instinct qui match l'input"""
        input_lower = input_text.lower().strip()

        # Chercher d'abord les correspondances exactes
        for instinct in self.instincts:
            pattern_lower = instinct["pattern"].lower().strip()
            if pattern_lower == input_lower:
                instinct["trigger_count"] += 1
                self._save_instincts()
                return instinct

        # Puis les correspondances partielles
        for instinct in self.instincts:
            pattern_lower = instinct["pattern"].lower().strip()
            if pattern_lower in input_lower or input_lower in pattern_lower:
                instinct["trigger_count"] += 1
                self._save_instincts()
                return instinct

        return None
    
    def get_statistics(self) -> Dict:
        """Statistiques du genome"""
        categories = {}
        for gene in self.genes.values():
            if gene.category not in categories:
                categories[gene.category] = {"count": 0, "avg_success": 0, "total_usage": 0}
            categories[gene.category]["count"] += 1
            categories[gene.category]["total_usage"] += gene.usage_count
        
        for cat in categories:
            genes = self.find_genes(category=cat)
            if genes:
                categories[cat]["avg_success"] = sum(g.success_rate for g in genes) / len(genes)
        
        return {
            "total_genes": len(self.genes),
            "total_mutations": len(self.mutations),
            "total_instincts": len(self.instincts),
            "by_category": categories,
            "top_genes": [g.key for g in self.get_best_genes(5)]
        }
    
    def evolve(self) -> Dict:
        """Élimine les gènes faibles, garde les forts"""
        eliminated = []
        for key, gene in list(self.genes.items()):
            if gene.priority < 50 and gene.success_rate < 0.3 and gene.usage_count > 10:
                del self.genes[key]
                eliminated.append(key)
        
        if eliminated:
            logger.info(f"Evolution: eliminated {len(eliminated)} weak genes")
            self._save_all()
        
        return {"eliminated": eliminated, "surviving": len(self.genes)}


def get_genome_memory() -> GenomeMemory:
    """Singleton genome memory"""
    return GenomeMemory()


if __name__ == "__main__":
    print("=== SHARINGAN GENOME MEMORY TEST ===\n")
    
    genome = GenomeMemory()
    
    print(f"Genes loaded: {len(genome.genes)}")
    print(f"Mutations: {len(genome.mutations)}")
    print(f"Instincts: {len(genome.instincts)}")
    
    print("\n1. Testing mutation:")
    key = genome.mutate("test_gene", {"test": "value"}, "experimental", source="test")
    print(f"   Created gene: {key}")
    
    print("\n2. Testing success recording:")
    genome.record_success(key)
    gene = genome.get_gene("test_gene", "experimental")
    if gene:
        print(f"   Success rate: {gene.success_rate}")
    else:
        print("   Gene not found")
    
    print("\n3. Testing instinct:")
    genome.add_instinct("hello", "Hello! I'm Sharingan.", condition="greeting")
    match = genome.match_instinct("hello there")
    print(f"   Instinct matched: {match['response'] if match else 'None'}")
    
    print("\n4. Statistics:")
    stats = genome.get_statistics()
    print(f"   Total genes: {stats['total_genes']}")
    print(f"   By category: {stats['by_category']}")
    
    print("\n✓ Genome memory operational!")
