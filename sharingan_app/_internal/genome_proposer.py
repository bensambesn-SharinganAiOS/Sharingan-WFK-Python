#!/usr/bin/env python3
"""
Sharingan Genome Proposer - Système de propositions intelligentes
Propose des améliorations du système, l'utilisateur valide.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.proposer")

class ProposalType(Enum):
    PERFORMANCE = "performance"
    SECURITY = "security"
    FEATURE = "feature"
    REFACTORING = "refactoring"
    OPTIMIZATION = "optimization"
    BUGFIX = "bugfix"

class ProposalImpact(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Proposal:
    id: str
    type: str
    title: str
    reason: str
    solution: str
    impact: str
    confidence: float
    files_affected: List[str] = field(default_factory=list)
    code_change: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    validated: bool = False
    rejected: bool = False

class GenomeProposer:
    """
    Propose des améliorations intelligentes du système.
    L'utilisateur valide tout avant application.
    """
    
    def __init__(self):
        self.proposals: List[Proposal] = []
        self.evolution_history: List[Dict] = []
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self._load_history()
    
    def _load_history(self) -> None:
        history_file = self.data_dir / "evolution_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    self.evolution_history = json.load(f)
            except:
                self.evolution_history
    
    def _save_history(self) -> None:
        history_file = self.data_dir / "evolution_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.evolution_history, f, indent=2, default=str)
    
    def analyze_system(self, consciousness_report: Dict) -> List[Proposal]:
        """
        Analyse le système et génère des propositions.
        """
        proposals = []
        
        file_issues = self._analyze_files(consciousness_report)
        proposals.extend(file_issues)
        
        perf_issues = self._analyze_performance(consciousness_report)
        proposals.extend(perf_issues)
        
        capability_gaps = self._analyze_capabilities(consciousness_report)
        proposals.extend(capability_gaps)
        
        code_quality = self._analyze_code_quality()
        proposals.extend(code_quality)
        
        self.proposals = proposals
        return proposals
    
    def _analyze_files(self, report: Dict) -> List[Proposal]:
        proposals = []
        
        changes = report.get("files", {}).get("change_details", {})
        modified = changes.get("modified", [])
        
        if len(modified) > 5:
            proposals.append(Proposal(
                id=f"file_batch_{int(time.time())}",
                type=ProposalType.REFACTORING.value,
                title="Fichiers modifiés en lot",
                reason=f"{len(modified)} fichiers ont été modifiés - vérification de cohérence recommandée",
                solution="Vérifier que les modifications sont cohérentes entre elles",
                impact=ProposalImpact.HIGH.value,
                confidence=0.7,
                files_affected=modified[:10]
            ))
        
        return proposals
    
    def _analyze_performance(self, report: Dict) -> List[Proposal]:
        proposals = []
        
        memory_items = report.get("memory", {}).get("items_count", 0)
        
        if memory_items > 1000:
            proposals.append(Proposal(
                id=f"perf_mem_{int(time.time())}",
                type=ProposalType.OPTIMIZATION.value,
                title="Mémoire importante accumulée",
                reason=f"{memory_items} items en mémoire - certains peuvent être anciens",
                solution="Nettoyer les éléments de basse priorité (vieilles conversations, tests échoués)",
                impact=ProposalImpact.MEDIUM.value,
                confidence=0.85
            ))
        
        return proposals
    
    def _analyze_capabilities(self, report: Dict) -> List[Proposal]:
        proposals = []
        
        tools_count = report.get("tools", {}).get("registered", 0)
        
        if tools_count < 50:
            proposals.append(Proposal(
                id=f"cap_gap_{int(time.time())}",
                type=ProposalType.FEATURE.value,
                title="Capacités limitées détectées",
                reason=f"only {tools_count} outils enregistrés - le système peut en supporter plus",
                solution="Scanner le répertoire tools/ pour découvrir de nouveaux outils",
                impact=ProposalImpact.LOW.value,
                confidence=0.6
            ))
        
        return proposals
    
    def _analyze_code_quality(self) -> List[Proposal]:
        proposals = []
        
        base_path = Path(__file__).parent
        
        for pyfile in base_path.glob("*.py"):
            try:
                with open(pyfile, 'r') as f:
                    content = f.read()
                
                if content.count("# TODO") > 3:
                    rel_path = pyfile.name
                    proposals.append(Proposal(
                        id=f"todo_{pyfile.stem}_{int(time.time())}",
                        type=ProposalType.REFACTORING.value,
                        title=f"TODOs dans {pyfile.name}",
                        reason=f"{content.count('# TODO')} TODOs trouvés",
                        solution="Revoir et prioriser les tâches en attente",
                        impact=ProposalImpact.LOW.value,
                        confidence=0.9,
                        files_affected=[rel_path]
                    ))
            except Exception:
                pass
        
        return proposals
    
    def get_proposals_for_user(self) -> str:
        """Génère un rapport lisible des propositions"""
        if not self.proposals:
            return "Aucune proposition pour le moment."
        
        lines = [
            "="*60,
            "🧬 PROPOSITIONS D'ÉVOLUTION DU SYSTÈME",
            "="*60,
            f"Total: {len(self.proposals)} propositions",
            ""
        ]
        
        sorted_proposals = sorted(self.proposals, 
                                  key=lambda p: (p.impact == "high", p.confidence), 
                                  reverse=True)
        
        for i, p in enumerate(sorted_proposals, 1):
            emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(p.impact, "⚪")
            
            lines.extend([
                f"{i}. {emoji} [{p.type.upper()}] {p.title}",
                f"   Confiance: {p.confidence*100:.0f}% | Impact: {p.impact.upper()}",
                f"   Raison: {p.reason}",
                f"   Solution: {p.solution}",
                ""
            ])
        
        lines.extend([
            "="*60,
            "ACTIONS: [nombre] valider | [nombre] rejeter | [nombre] détails | q quitter",
            "="*60
        ])
        
        return "\n".join(lines)
    
    def validate_proposal(self, proposal_id: str) -> bool:
        """Marque une proposition comme validée par l'utilisateur"""
        for p in self.proposals:
            if p.id == proposal_id:
                p.validated = True
                self.evolution_history.append({
                    "proposal_id": p.id,
                    "title": p.title,
                    "validated_at": datetime.now().isoformat(),
                    "type": p.type
                })
                self._save_history()
                logger.info(f"Proposal validated: {p.title}")
                return True
        return False
    
    def reject_proposal(self, proposal_id: str) -> bool:
        """Marque une proposition comme rejetée"""
        for p in self.proposals:
            if p.id == proposal_id:
                p.rejected = True
                logger.info(f"Proposal rejected: {p.title}")
                return True
        return False
    
    def get_evolution_stats(self) -> Dict:
        """Statistiques d'évolution"""
        total = len(self.evolution_history)
        by_type = {}
        for ev in self.evolution_history:
            t = ev.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
        
        return {
            "total_evolutions": total,
            "by_type": by_type,
            "pending_proposals": len([p for p in self.proposals if not p.validated and not p.rejected])
        }


def get_genome_proposer() -> GenomeProposer:
    return GenomeProposer()


if __name__ == "__main__":
    print("=== GENOME PROPOSER TEST ===\n")
    
    proposer = GenomeProposer()
    
    print("1. Creating test proposals...")
    
    test_proposal = Proposal(
        id="test_001",
        type=ProposalType.PERFORMANCE.value,
        title="Test Proposal",
        reason="Testing the system",
        solution="Just a test",
        impact=ProposalImpact.MEDIUM.value,
        confidence=0.8,
        files_affected=["test.py"]
    )
    
    proposer.proposals.append(test_proposal)
    
    print("\n2. Displaying proposals:")
    print(proposer.get_proposals_for_user())
    
    print("\n3. Evolution stats:")
    print(json.dumps(proposer.get_evolution_stats(), indent=2))
    
    print("\n✓ Proposer operational!")
