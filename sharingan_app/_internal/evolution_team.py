#!/usr/bin/env python3
"""
Sharingan Evolution Team - Équipe de 3 AIs spécialisés
tgpt: Observateur (analyse globale)
grok_code: Chirurgien (modifications de code)
minimax: Stratégie (planification long terme)

MODES D'EXÉCUTION:
- BUILD: Mode par défaut - Toutes capacités, validation requise (non-bloquant)
- PLAN: Validation avant exécution (batch)
- REALTIME: Confirmation interactive

SECURITY: Tous les patches AI nécessitent validation explicite
via le système de permissions avant application.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.evolution")


@dataclass
class EvolutionResult:
    """Résultat d'une analyse d'évolution"""
    observer_report: Dict = field(default_factory=dict)
    surgeon_patch: Optional[str] = None
    strategic_plan: Optional[Dict] = None
    consensus_score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    recommendations: List[str] = field(default_factory=list)
    permission_status: Optional[Dict] = None


@dataclass
class PatchApplicationResult:
    """Résultat de l'application d'un patch"""
    applied: bool = False
    permission: Optional[Dict] = None
    files_modified: List[str] = field(default_factory=list)
    backup_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    patch_text: Optional[str] = None


class EvolutionTeam:
    """
    Équipe d'évolution avec 3 AIs spécialisés.

    Modes:
    - BUILD (défaut): Capacités complètes, validation non-bloquante
    - PLAN: Validation avant exécution (batch)
    - REALTIME: Confirmation interactive

    SECURITY: Intégration avec le système de permissions pour validation
    des patches AI avant toute application.
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

    def __init__(self, mode: str = "build"):
        """
        Initialiser l'équipe d'évolution.

        Args:
            mode: build (défaut), plan, ou realtime
        """
        self.mode = mode.lower()
        self.ai_providers = None
        self._init_providers()
        self._init_permission_system()
        self._init_dangerous_patterns()

    def _init_permission_system(self):
        """Initialiser le système de permissions"""
        try:
            from security.permissions import (
                PermissionValidator,
                ExecutionMode,
                PermissionResult
            )
            
            mode_map = {
                "build": ExecutionMode.PLAN,  # BUILD utilise PLAN (validation non-bloquante)
                "plan": ExecutionMode.PLAN,
                "realtime": ExecutionMode.REALTIME
            }
            
            exec_mode = mode_map.get(self.mode, ExecutionMode.PLAN)
            self.permission_validator = PermissionValidator(mode=exec_mode)
            self.permission_result_class = PermissionResult
            
            logger.info(f"EvolutionTeam initialized in {self.mode.upper()} mode with permission system")
            
        except ImportError as e:
            logger.warning(f"Permission system not available: {e}")
            self.permission_validator = None
    
    def _init_dangerous_patterns(self):
        """Patterns dangereux à détecter dans les patches"""
        self.dangerous_patterns = [
            (r"rm\s+-rf\s+", "Suppression récursive"),
            (r"chmod\s+777", "Permissions trop larges"),
            (r">\s*/dev/null", "Redirection vers null"),
            (r"&\s*;\s*rm", "Chain command with rm"),
            (r"curl\s+.*\|\s*sh", "Pipe curl vers shell"),
            (r"wget\s+.*\|\s*sh", "Pipe wget vers shell"),
            (r"base64\s*-d.*\|", "Base64 decode and pipe"),
        ]
    
    def _init_providers(self):
        """Initialiser les providers AI"""
        try:
            from ai_providers import get_provider_manager
            self.ai_providers = get_provider_manager()
            logger.info("Evolution team initialized with AI providers")
        except Exception as e:
            logger.warning(f"AI providers not available: {e}")
    
    def run_analysis(self, task: str, require_approval: bool = False) -> EvolutionResult:
        """
        Lancer l'analyse complète du système par l'équipe.
        
        Args:
            task: Tâche d'analyse
            require_approval: Si True, demande approval pour les patches (mode BUILD)
        
        Returns:
            EvolutionResult avec rapport, patch, et plan
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
                
                # En mode BUILD avec require_approval, préparer la validation
                if result.surgeon_patch and require_approval and self.mode == "build":
                    result.permission_status = self._prepare_patch_validation(
                        result.surgeon_patch,
                        {"task": task}
                    )
            
            strategic_result = self._query_strategist(task, result.observer_report)
            result.strategic_plan = strategic_result
            
            result.consensus_score = self._calculate_consensus(result)
            result.recommendations = self._generate_recommendations(result)
            
        except Exception as e:
            logger.error(f"Evolution analysis failed: {e}")
            return self._basic_analysis(task)
        
        return result
    
    def _prepare_patch_validation(self, patch_text: str, context: Dict) -> Dict:
        """Préparer la validation d'un patch en mode BUILD"""
        if not self.permission_validator:
            return {"available": False, "reason": "Permission system unavailable"}
        
        permission = self.permission_validator.validate(
            tool="ai_patch_builder",
            command=["apply_patch", "build_mode"],
            context=context,
            user_id=context.get("user_id"),
            mission_id=context.get("mission_id")
        )
        
        return {
            "available": True,
            "granted": permission.granted,
            "reason": permission.reason,
            "validation_mode": permission.validation_mode.value,
            "conditions": permission.conditions,
            "warning": permission.warning
        }
    
    def _query_observer(self, task: str) -> Dict:
        """tgpt observe et analyse le système"""
        prompt = f"""
Tu es l'Observateur du système Sharingan. Analyse cette demande:

{task}

Fournis un rapport d'observation avec:
1. Problèmes identifiés (issues[])
2. Patterns détectés (patterns[])
3. Recommandation courte (recommendation)
4. Score de confiance (confidence_score 0-1)
"""
        
        try:
            response = self.ai_providers.chat_single(prompt, "tgpt")
            if response.get("success"):
                return {
                    "issues": [response["response"][:500]],
                    "patterns": [],
                    "recommendation": response["response"][:200],
                    "confidence_score": 0.7
                }
        except Exception as e:
            logger.warning(f"Observer query failed: {e}")
        
        return {"issues": [f"Task: {task}"], "patterns": [], "confidence_score": 0.5}
    
    def _query_surgeon(self, issues: List[str]) -> Dict:
        """
        grok_code propose des modifications de code
        
        SECURITY: Le patch est généré mais n'est JAMAIS appliqué directement.
        Validation requise via apply_patch() avec permission.
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

IMPORTANT: Ne propose jamais de commandes dangereuses comme:
- rm -rf
- chmod 777
- curl | sh

Réponds en JSON avec: {{"patches": [{{"file": "", "current": "", "proposed": "", "reason": ""}}]}}
"""
        
        try:
            if not self.ai_providers:
                return {
                    "patch": None,
                    "success": False,
                    "validation_status": "SIMULATION_MODE",
                    "warning": "AI providers not available"
                }
            
            response = self.ai_providers.chat_single(prompt, "grok-code-fast")
            if response.get("success"):
                patch_text = response["response"]
                
                # Valider le patch (JSON + patterns dangereux)
                validation = self._validate_patch(patch_text)
                
                if validation["valid"]:
                    return {
                        "patch": patch_text,
                        "success": True,
                        "validation_status": "validated",
                        "patches_count": validation.get("count", 1),
                        "dangerous_patterns": validation.get("patterns_found", [])
                    }
                else:
                    return {
                        "patch": patch_text,
                        "success": False,
                        "validation_status": "invalid",
                        "validation_errors": validation.get("errors", [])
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
        3. Pas de patterns dangereux
        """
        validation = {
            "valid": False,
            "errors": [],
            "count": 0,
            "patterns_found": []
        }
        
        if not patch_text:
            validation["errors"].append("Empty patch")
            return validation
        
        # Vérifier patterns dangereux
        for pattern, description in self.dangerous_patterns:
            if re.search(pattern, patch_text, re.IGNORECASE):
                validation["patterns_found"].append(description)
                validation["errors"].append(f"Dangerous pattern: {description}")
        
        # Parser JSON
        try:
            data = json.loads(patch_text)
            patches = data.get("patches", data if isinstance(data, list) else [])
            validation["count"] = len(patches)
            
            # Vérifier structure
            required_keys = ["file", "current", "proposed", "reason"]
            for i, patch in enumerate(patches):
                for key in required_keys:
                    if key not in patch:
                        validation["errors"].append(f"Patch {i}: missing '{key}'")
                        
        except json.JSONDecodeError as e:
            validation["errors"].append(f"Invalid JSON: {e}")
        
        validation["valid"] = len(validation["errors"]) == 0
        return validation
    
    def _query_strategist(self, task: str, observer_report: Dict) -> Dict:
        """minimax planifie l'évolution"""
        prompt = f"""
Tu es le Stratégiste du système Sharingan. Planifie l'évolution du système.

Tâche: {task}
Analyse: {observer_report}

Planifie en JSON avec:
- short_term: [] (actions immédiates)
- medium_term: [] (développement)
- long_term: [] (vision)
- dependencies: [] (dépendances)
"""
        
        try:
            response = self.ai_providers.chat_single(prompt, "minimax")
            if response.get("success"):
                try:
                    return json.loads(response["response"])
                except json.JSONDecodeError:
                    return {"short_term": [response["response"][:500]]}
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
        
        return min(score, 1.0)
    
    def _generate_recommendations(self, result: EvolutionResult) -> List[str]:
        """Génère des recommandations basées sur les résultats"""
        recs = []
        
        if result.consensus_score > 0.8:
            recs.append("Strong consensus - proceed with implementation")
        elif result.consensus_score < 0.5:
            recs.append("Low confidence - manual review recommended")
        
        if result.surgeon_patch:
            recs.append("Code modifications proposed - review required before application")
        
        if result.strategic_plan:
            recs.append(f"Strategic plan available: {len(result.strategic_plan.get('short_term', []))} short-term actions")
        
        return recs
    
    def _basic_analysis(self, task: str) -> EvolutionResult:
        """Analyse basique sans AIs"""
        return EvolutionResult(
            observer_report={
                "issues": [f"Task: {task}"],
                "patterns": [],
                "recommendation": "AI providers not available",
                "confidence_score": 0.3
            },
            recommendations=["AI providers required for full analysis"]
        )
    
    def apply_patch(self, patch_text: str, context: Dict[str, Any] = None) -> PatchApplicationResult:
        """
        Appliquer un patch avec validation de permission.
        
        En mode BUILD (défaut):
        - Vérifie permission (non-bloquant)
        - Crée backup avant modification
        - Valide le patch JSON
        - Détecte patterns dangereux
        
        Args:
            patch_text: Le patch JSON généré par le chirurgien
            context: Contexte (user_id, mission_id, etc.)
        
        Returns:
            PatchApplicationResult avec résultat de l'application
        """
        if context is None:
            context = {}
        
        result = PatchApplicationResult(patch_text=patch_text[:500] if patch_text else None)
        
        # Validation permission
        if self.permission_validator:
            permission = self.permission_validator.validate(
                tool="ai_patch_applier",
                command=["apply_patch", self.mode],
                context={
                    **context,
                    "patch_size": len(patch_text) if patch_text else 0
                },
                user_id=context.get("user_id"),
                mission_id=context.get("mission_id")
            )
            
            result.permission = permission.to_dict() if hasattr(permission, 'to_dict') else {
                "granted": permission.granted,
                "reason": permission.reason
            }
            
            if not permission.granted:
                result.errors.append(f"Permission denied: {permission.reason}")
                logger.warning(f"Patch blocked: {permission.reason}")
                return result
        else:
            result.permission = {"granted": True, "reason": "No validation (dev mode)"}
        
        # Appliquer le patch
        try:
            data = json.loads(patch_text)
            patches = data.get("patches", data if isinstance(data, list) else [])
            
            for patch in patches:
                file_path = patch.get("file")
                if not file_path:
                    result.errors.append("Missing file path")
                    continue
                
                # Vérifier chemin sûr
                safe_path = Path(file_path).resolve()
                base_path = Path(__file__).parent.parent.parent
                
                if not str(safe_path).startswith(str(base_path)):
                    result.errors.append(f"Unsafe path: {file_path}")
                    continue
                
                # Lire original
                if safe_path.exists():
                    with open(safe_path, 'r') as f:
                        original = f.read()
                else:
                    original = ""
                
                # Créer backup
                backup = safe_path.with_suffix(safe_path.suffix + ".backup")
                with open(backup, 'w') as f:
                    f.write(original)
                result.backup_files.append(str(backup))
                
                # Appliquer
                current = patch.get("current", "")
                proposed = patch.get("proposed", "")
                
                if current:
                    new_content = original.replace(current, proposed)
                else:
                    new_content = original + proposed
                
                with open(safe_path, 'w') as f:
                    f.write(new_content)
                
                result.files_modified.append(str(safe_path))
            
            result.applied = len(result.files_modified) > 0 and len(result.errors) == 0
            
        except json.JSONDecodeError as e:
            result.errors.append(f"Invalid JSON: {e}")
        except Exception as e:
            result.errors.append(str(e))
        
        return result
    
    def get_status(self) -> Dict:
        """Statut de l'équipe"""
        return {
            "mode": self.mode,
            "roles": self.ROLES,
            "providers_available": self.ai_providers is not None,
            "providers": list(self.ai_providers.providers.keys()) if self.ai_providers else [],
            "permission_system": self.permission_validator is not None
        }
    
    def display_result(self, result: EvolutionResult) -> str:
        """Affiche le résultat de manière lisible"""
        lines = [
            "=" * 60,
            "EVOLUTION TEAM - RAPPORT",
            "=" * 60,
            f"Timestamp: {result.timestamp}",
            f"Consensus Score: {result.consensus_score * 100:.0f}%",
        ]
        
        if result.permission_status:
            lines.extend([
                "",
                "PERMISSION STATUS (BUILD MODE):",
                f"  Available: {result.permission_status.get('available', False)}",
                f"  Granted: {result.permission_status.get('granted', False)}",
            ])
        
        if result.observer_report:
            lines.extend([
                "",
                "OBSERVATEUR (tgpt):",
                f"  Issues: {len(result.observer_report.get('issues', []))}",
                f"  Confidence: {result.observer_report.get('confidence_score', 0) * 100:.0f}%",
            ])
        
        if result.surgeon_patch:
            lines.extend([
                "",
                "CHIRURGIEN (grok-code-fast):",
                "  Patch generated - apply via apply_patch()",
                "  Permission required before application",
            ])
        
        if result.strategic_plan:
            st = result.strategic_plan.get('short_term', [])
            mt = result.strategic_plan.get('medium_term', [])
            lt = result.strategic_plan.get('long_term', [])
            lines.extend([
                "",
                "STRATEGIST (minimax):",
                f"  Short-term: {len(st)} actions",
                f"  Medium-term: {len(mt)} actions",
                f"  Long-term: {len(lt)} actions",
            ])
        
        lines.extend(["", "RECOMMENDATIONS:"])
        for rec in result.recommendations:
            lines.append(f"  - {rec}")
        
        return "\n".join(lines)


def get_evolution_team(mode: str = "build") -> EvolutionTeam:
    """
    Factory function pour créer une équipe d'évolution.
    
    Args:
        mode: build (défaut), plan, ou realtime
    """
    return EvolutionTeam(mode=mode)


if __name__ == "__main__":
    print("=== EVOLUTION TEAM TEST ===\n")
    
    # Test en mode BUILD (défaut)
    team = EvolutionTeam(mode="build")
    
    print("1. Team status:")
    status = team.get_status()
    print(f"   Mode: {status['mode']}")
    print(f"   Providers: {status['providers']}")
    print(f"   Permission system: {status['permission_system']}")
    
    print("\n2. Running analysis on 'improve memory system'...")
    result = team.run_analysis("improve memory system", require_approval=True)
    
    print("\n3. Result:")
    print(team.display_result(result))
    
    if result.surgeon_patch:
        print("\n4. Patch generated - attempting application...")
        apply_result = team.apply_patch(result.surgeon_patch, {"user_id": "test"})
        print(f"   Applied: {apply_result.applied}")
        print(f"   Files modified: {apply_result.files_modified}")
        print(f"   Backup files: {apply_result.backup_files}")
        print(f"   Errors: {apply_result.errors}")
    
    print("\n✓ Evolution team operational in BUILD mode!")
