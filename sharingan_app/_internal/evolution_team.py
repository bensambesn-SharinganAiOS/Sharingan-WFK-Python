#!/usr/bin/env python3
"""
Sharingan Evolution Team - Équipe de 3 AIs spécialisés
tgpt: Observateur (analyse globale)
grok_code: Chirurgien (modifications de code)
minimax: Stratégie (planification long terme)
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.evolution")

@dataclass
class EvolutionResult:
    observer_report: Dict = field(default_factory=dict)
    surgeon_patch: Optional[str] = None
    strategic_plan: Optional[Dict] = None
    consensus_score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    recommendations: List[str] = field(default_factory=list)

class EvolutionTeam:
    """
    Équipe d'évolution avec 3 AIs spécialisés.
    Chaque AI a un rôle précis dans l'amélioration du système.
    """
    
    ROLES = {
        "tgpt": {
            "name": "Observateur",
            "role": "Analyse globale et détection de patterns",
            "specialty": "Tendances, anomalies, état général",
            "output_type": "consciousness_report"
        },
        "grok_code": {
            "name": "Chirurgien",
            "role": "Modifications techniques et code",
            "specialty": "Refactoring, optimisations, bugfixes",
            "output_type": "code_patch"
        },
        "minimax": {
            "name": "Stratège",
            "role": "Planification et architecture",
            "specialty": "Vision long terme, évolution du système",
            "output_type": "evolution_plan"
        }
    }
    
    def __init__(self):
        self.ai_providers = None
        self._init_providers()
    
    def _init_providers(self):
        try:
            from ai_providers import get_provider_manager
            self.ai_providers = get_provider_manager()
            logger.info("Evolution team initialized with AI providers")
        except Exception as e:
            logger.warning(f"AI providers not available: {e}")
    
    def run_analysis(self, task: str) -> EvolutionResult:
        """
        Lance l'analyse complète du système par l'équipe.
        """
        result = EvolutionResult()
        
        if not self.ai_providers:
            result.recommendations.append("AI providers not available - running basic analysis")
            return self._basic_analysis(task)
        
        try:
            observer_result = self._query_observer(task)
            result.observer_report = observer_result
            
            if observer_result.get("issues"):
                surgeon_result = self._query_surgeon(observer_result["issues"])
                result.surgeon_patch = surgeon_result.get("patch")
            
            strategic_result = self._query_strategist(task, result.observer_report)
            result.strategic_plan = strategic_result
            
            result.consensus_score = self._calculate_consensus(result)
            result.recommendations = self._generate_recommendations(result)
            
        except Exception as e:
            logger.error(f"Evolution analysis failed: {e}")
            return self._basic_analysis(task)
        
        return result
    
    def _query_observer(self, task: str) -> Dict:
        """tgpt observe et analyse le système"""
        prompt = f"""
Tu es l'Observateur du système Sharingan. Analyse cette demande:

{task}

Analyse:
1. Quel est l'état actuel du système par rapport à cette demande?
2. Quelles sont les anomalies ou problèmes visibles?
3. Quels patterns détectes-tu?
4. Quelle est ta recommandation globale?

Réponds en JSON avec: issues[], patterns[], recommendation, confidence_score
"""
        
        try:
            response = self.ai_providers.chat_single(task, "tgpt")
            if response.get("success"):
                return self._parse_observer_response(response["response"])
        except Exception as e:
            logger.warning(f"Observer query failed: {e}")
        
        return {"issues": [], "patterns": [], "recommendation": "Analyse basique"}
    
    def _parse_observer_response(self, response: str) -> Dict:
        """Parse la réponse de l'observateur"""
        try:
            import re
            json_match = re.search(r'\{[^{}]+\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return {"issues": [response], "patterns": [], "recommendation": response[:200]}
    
    def _query_surgeon(self, issues: List[str]) -> Dict:
        """
        grok_code propose des modifications de code
        
        WARNING: Patch généré par AI - N'APPLIQUER JAMAIS directement sans:
        1. Validation JSON
        2. Tests unitaires
        3. Review humaine
        4. Sandbox/testing avant production
        """
        if not issues:
            return {"patch": None, "success": False, "validation_status": "no_issues"}
        
        prompt = f"""
Tu es le Chirurgien du système Sharingan. Propose des modifications de code pour ces problèmes:

{issues}

Pour chaque problème:
1. Fichier à modifier
2. Code actuel (avec numéro de ligne)
3. Code proposé
4. Raison de la modification

Réponds en JSON avec: patches[{file, current, proposed, reason}]
"""
        
        try:
            if not self.ai_providers:
                return {
                    "patch": None,
                    "success": False,
                    "validation_status": "SIMULATION_MODE - no providers",
                    "warning": "AI providers not available"
                }
            
            response = self.ai_providers.chat_single(prompt, "grok-code-fast")
            if response.get("success"):
                patch_text = response["response"]
                
                # VALIDATION DU PATCH
                validation_result = self._validate_patch(patch_text)
                
                if validation_result["valid"]:
                    return {
                        "patch": patch_text,
                        "success": True,
                        "validation_status": "validated",
                        "patches_count": validation_result.get("count", 1)
                    }
                else:
                    return {
                        "patch": patch_text,
                        "success": False,
                        "validation_status": "invalid",
                        "validation_errors": validation_result.get("errors", [])
                    }
        except Exception as e:
            logger.warning(f"Surgeon query failed: {e}")
        
        return {"patch": None, "success": False, "validation_status": "error"}
    
    def _validate_patch(self, patch_text: str) -> Dict:
        """
        Valider un patch généré par AI.
        
        Vérifications:
        1. Format JSON valide
        2. Structure attendue (file, current, proposed, reason)
        3. Pas de patterns dangereux (rm -rf, chmod 777, etc.)
        """
        import re
        
        validation = {
            "valid": False,
            "errors": [],
            "count": 0
        }
        
        if not patch_text:
            validation["errors"].append("Empty patch")
            return validation
        
        # Vérifier patterns dangereux
        dangerous_patterns = [
            r"rm\s+-rf\s+/",
            r"chmod\s+777",
            r">\s*\/dev\/null",
            r"&\s*;\s*rm",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, patch_text, re.IGNORECASE):
                validation["errors"].append(f"Dangerous pattern detected: {pattern}")
        
        # Essayer de parser JSON
        try:
            import json
            data = json.loads(patch_text)
            
            if isinstance(data, dict) and "patches" in data:
                patches = data["patches"]
            elif isinstance(data, list):
                patches = data
            else:
                validation["errors"].append("Unexpected JSON structure")
                return validation
            
            validation["count"] = len(patches)
            
            # Vérifier structure de chaque patch
            required_fields = ["file", "current", "proposed", "reason"]
            for i, patch in enumerate(patches):
                for field in required_fields:
                    if field not in patch:
                        validation["errors"].append(f"Patch {i}: missing field '{field}'")
            
        except json.JSONDecodeError as e:
            validation["errors"].append(f"Invalid JSON: {e}")
        
        validation["valid"] = len(validation["errors"]) == 0
        return validation
    
    def _query_strategist(self, task: str, observer_report: Dict) -> Dict:
        """minimax planifie l'évolution"""
        prompt = f"""
Tu es le Stratégiste du système Sharingan. Planifie l'évolution du système.

Tâche: {task}
Analyse de l'Observateur: {observer_report}

Planifie:
1. Court terme (ce qui peut être fait maintenant)
2. Moyen terme (ce qui nécessite du développement)
3. Long terme (vision d'évolution)
4. Dépendances entre les étapes

Réponds en JSON avec: short_term[], medium_term[], long_term[], dependencies[]
"""
        
        try:
            response = self.ai_providers.chat_single(prompt, "minimax")
            if response.get("success"):
                try:
                    return json.loads(response["response"])
                except:
                    return {"plan": response["response"][:500]}
        except Exception as e:
            logger.warning(f"Strategist query failed: {e}")
        
        return {"short_term": [], "medium_term": [], "long_term": []}
    
    def _calculate_consensus(self, result: EvolutionResult) -> float:
        """Calcule un score de consensus entre les AIs"""
        if not result.observer_report:
            return 0.0
        
        score = 0.5
        
        if result.observer_report.get("confidence_score", 0) > 0.7:
            score += 0.2
        
        if result.surgeon_patch:
            score += 0.15
        
        if result.strategic_plan:
            score += 0.15
        
        return min(1.0, score)
    
    def _generate_recommendations(self, result: EvolutionResult) -> List[str]:
        """Génère des recommandations basées sur les résultats"""
        recs = []
        
        if result.consensus_score > 0.8:
            recs.append("Haute confiance dans l'analyse - actions recommandées")
        elif result.consensus_score > 0.5:
            recs.append("Confiance modérée - vérifier les détails avant action")
        else:
            recs.append("Faible confiance - analyse supplémentaire recommandée")
        
        if result.surgeon_patch:
            recs.append("Modifications de code proposées - validation utilisateur requise")
        
        if result.strategic_plan:
            recs.append("Plan stratégique disponible - réviser les priorités")
        
        return recs
    
    def _basic_analysis(self, task: str) -> EvolutionResult:
        """Analyse basique sans AIs"""
        return EvolutionResult(
            observer_report={
                "issues": [f"Task identified: {task}"],
                "patterns": [],
                "recommendation": "Basic analysis - AI providers not available",
                "confidence_score": 0.3
            },
            recommendations=["AI providers required for full analysis"]
        )
    
    def get_team_status(self) -> Dict:
        """Statut de l'équipe"""
        return {
            "roles": self.ROLES,
            "providers_available": self.ai_providers is not None,
            "providers": list(self.ai_providers.providers.keys()) if self.ai_providers else []
        }
    
    def display_result(self, result: EvolutionResult) -> str:
        """Affiche le résultat de manière lisible"""
        lines = [
            "="*60,
            "🧬 ÉQUIPE D'ÉVOLUTION - RAPPORT",
            "="*60,
            f"Timestamp: {result.timestamp}",
            f"Score de consensus: {result.consensus_score*100:.0f}%",
            "",
            "👁️ OBSERVATEUR (tgpt):",
            f"  Recommandation: {result.observer_report.get('recommendation', 'N/A')}",
            f"  Confiance: {result.observer_report.get('confidence_score', 0)*100:.0f}%",
            f"  Problèmes détectés: {len(result.observer_report.get('issues', []))}",
            "",
        ]
        
        if result.surgeon_patch:
            lines.extend([
                "🔧 CHIRURGIEN (grok-code-fast):",
                f"  Modifications proposées: Oui",
                "  [Code disponible pour review]",
                "",
            ])
        
        if result.strategic_plan:
            lines.extend([
                "♟️ STRATÈGE (minimax):",
                f"  Court terme: {len(result.strategic_plan.get('short_term', []))} actions",
                f"  Moyen terme: {len(result.strategic_plan.get('medium_term', []))} actions",
                f"  Long terme: {len(result.strategic_plan.get('long_term', []))} actions",
                "",
            ])
        
        lines.extend([
            "="*60,
            "RECOMMANDATIONS:",
        ])
        
        for rec in result.recommendations:
            lines.append(f"  • {rec}")
        
        lines.append("="*60)
        
        return "\n".join(lines)


def get_evolution_team() -> EvolutionTeam:
    return EvolutionTeam()


if __name__ == "__main__":
    print("=== EVOLUTION TEAM TEST ===\n")
    
    team = EvolutionTeam()
    
    print("1. Team status:")
    status = team.get_team_status()
    print(f"   Providers: {status['providers']}")
    
    print("\n2. Running analysis on 'improve memory system'...")
    result = team.run_analysis("improve memory system")
    
    print("\n3. Result:")
    print(team.display_result(result))
    
    print("\n✓ Evolution team operational!")
