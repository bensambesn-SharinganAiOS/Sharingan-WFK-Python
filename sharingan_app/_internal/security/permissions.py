#!/usr/bin/env python3
"""
Sharingan Permission System - Validation explicite pour opérations dangereuses
Modes: PLAN (validation avant exécution) ou REALTIME (confirmation interactive)
"""

import os
import json
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.permissions")


class DangerLevel(Enum):
    """Niveau de danger des opérations"""
    SAFE = "safe"           # Lecture, calcul, analysis
    MODERATE = "moderate"   # Installation, modifications non-système
    HIGH = "high"           # Outils de scan, accès réseau
    CRITICAL = "critical"   # Exécution code, outils d'exploitation


class ExecutionMode(Enum):
    """Mode d'exécution"""
    PLAN = "plan"           # Validation avant exécution (batch)
    REALTIME = "realtime"   # Confirmation interactive


@dataclass
class PermissionRequest:
    """Demande de permission pour une opération"""
    tool: str
    command: List[str]
    danger_level: DangerLevel
    context: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    user_id: Optional[str] = None
    mission_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "tool": self.tool,
            "command": self.command,
            "danger_level": self.danger_level.value,
            "context": self.context,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "mission_id": self.mission_id
        }


@dataclass
class PermissionResult:
    """Résultat de la demande de permission"""
    granted: bool
    reason: str
    validation_mode: ExecutionMode
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    warning: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "granted": self.granted,
            "reason": self.reason,
            "validation_mode": self.validation_mode.value,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at,
            "conditions": self.conditions,
            "warning": self.warning
        }


class ToolClassifier:
    """Classification des outils par niveau de danger"""
    
    # Outils par niveau de danger
    SAFE_TOOLS = {
        "read", "cat", "head", "tail", "grep", "find", "ls", "pwd", "echo",
        "date", "whoami", "id", "uname", "free", "df", "history"
    }
    
    MODERATE_TOOLS = {
        "mkdir", "touch", "cp", "mv", "rm", "chmod", "chown", "apt-get",
        "pip", "npm", "git", "curl", "wget"
    }
    
    HIGH_TOOLS = {
        "nmap", "netdiscover", "masscan", "rustscan", "ping", "traceroute",
        "nikto", "dirb", "gobuster", "ffuf", "wfuzz", "enum4linux",
        "smbclient", "rpcclient", "nc", "netcat", "socat"
    }
    
    CRITICAL_TOOLS = {
        "sqlmap", "metasploit", "msfconsole", "hydra", "john", "hashcat",
        "aircrack-ng", "wifite", "bettercap", "ettercap", "responder",
        "mimikatz", "psexec", "wmiexec", "smbexec", "bloodhound"
    }
    
    @classmethod
    def classify(cls, tool: str) -> DangerLevel:
        """Classifier un outil par niveau de danger"""
        tool_lower = tool.lower()
        
        if tool_lower in cls.CRITICAL_TOOLS:
            return DangerLevel.CRITICAL
        elif tool_lower in cls.HIGH_TOOLS:
            return DangerLevel.HIGH
        elif tool_lower in cls.MODERATE_TOOLS:
            return DangerLevel.MODERATE
        else:
            return DangerLevel.SAFE
    
    @classmethod
    def requires_validation(cls, level: DangerLevel) -> bool:
        """Déterminer si le niveau nécessite une validation"""
        return level in [DangerLevel.HIGH, DangerLevel.CRITICAL]


class PermissionValidator:
    """
    Système de validation des permissions.
    
    Deux modes:
    - PLAN: Valide à l'avance (batch planning)
    - REALTIME: Demande confirmation interactive
    """
    
    def __init__(self, mode: ExecutionMode = ExecutionMode.PLAN):
        self.mode = mode
        self.tool_classifier = ToolClassifier()
        self.approval_cache: Dict[str, PermissionResult] = {}
        self.audit_log: List[Dict] = []
        
        # Pré-approuvations (environment variable)
        self.pre_approved_tools = self._load_pre_approvals()
    
    def _load_pre_approvals(self) -> Dict[str, bool]:
        """Charger les pré-approbations depuis l'environnement"""
        env_approved = os.environ.get("SHARINGAN_PRE_APPROVED_TOOLS", "")
        return {tool.strip(): True for tool in env_approved.split(",") if tool.strip()}
    
    def validate(
        self,
        tool: str,
        command: List[str],
        context: Dict[str, Any],
        user_id: Optional[str] = None,
        mission_id: Optional[str] = None
    ) -> PermissionResult:
        """
        Valider une demande d'exécution d'outil.
        
        Args:
            tool: Nom de l'outil
            command: Commande complète
            context: Contexte de l'exécution
            user_id: ID de l'utilisateur (pour audit)
            mission_id: ID de la mission
        
        Returns:
            PermissionResult avec la décision
        """
        danger_level = self.tool_classifier.classify(tool)
        
        request = PermissionRequest(
            tool=tool,
            command=command,
            danger_level=danger_level,
            context=context,
            user_id=user_id,
            mission_id=mission_id
        )
        
        # Vérifier pré-approbation
        if tool in self.pre_approved_tools:
            result = PermissionResult(
                granted=True,
                reason=f"Pré-approuvé: {tool}",
                validation_mode=self.mode,
                approved_by="system_preapproval",
                conditions=["Pré-approuvé via SHARINGAN_PRE_APPROVED_TOOLS"]
            )
            self._log(request, result)
            return result
        
        # Outils sûrs - approbation automatique
        if danger_level == DangerLevel.SAFE:
            result = PermissionResult(
                granted=True,
                reason="Outil de niveau sûr",
                validation_mode=self.mode
            )
            self._log(request, result)
            return result
        
        # Vérifier cache pour HIGH/CRITICAL
        cache_key = f"{tool}:{':'.join(command)}"
        if cache_key in self.approval_cache:
            cached = self.approval_cache[cache_key]
            # Vérifier si pas expirée (24h)
            if self._is_cache_valid(cached):
                return cached
        
        # Nécessite validation
        if danger_level in [DangerLevel.HIGH, DangerLevel.CRITICAL]:
            if self.mode == ExecutionMode.PLAN:
                # Mode plan - ajouter à la liste de validation
                result = PermissionResult(
                    granted=False,
                    reason="Nécessite validation en mode PLAN",
                    validation_mode=self.mode,
                    warning=f"Outil {tool} de niveau {danger_level.value}"
                )
            else:
                # Mode realtime - demander confirmation interactive
                result = self._interactive_prompt(tool, command, danger_level, context)
        else:
            # MODERATE - approval simple
            result = PermissionResult(
                granted=True,
                reason="Outil de niveau modéré",
                validation_mode=self.mode
            )
        
        self._log(request, result)
        if danger_level in [DangerLevel.HIGH, DangerLevel.CRITICAL]:
            self.approval_cache[cache_key] = result
        
        return result
    
    def _interactive_prompt(
        self,
        tool: str,
        command: List[str],
        danger_level: DangerLevel,
        context: Dict[str, Any]
    ) -> PermissionResult:
        """
        Demande de confirmation interactive.
        
        Affiche un avertissement et demande confirmation.
        """
        print("\n" + "=" * 60)
        print("⚠️  DEMANDE DE PERMISSION - EXÉCUTION D'OUTIL")
        print("=" * 60)
        print(f"\nOutil: {tool}")
        print(f"Niveau de danger: {danger_level.value.upper()}")
        print(f"Commande: {' '.join(command)}")
        
        if context.get("mission_id"):
            print(f"Mission: {context['mission_id']}")
        
        if danger_level == DangerLevel.CRITICAL:
            print("\n🚨 ATTENTION: Cet outil est CRITIQUE")
            print("   Une mauvaise utilisation peut causer des dommages!")
            print("   Types de risques:")
            print("   - Exécution de code arbitraire")
            print("   - Accès non autorisé à des systèmes")
            print("   - Violation de lois applicables")
        elif danger_level == DangerLevel.HIGH:
            print("\n⚠️  ATTENTION: Cet outil est à haut risque")
            print("   Il peut être utilisé pour:")
            print("   - Scan de réseaux sans autorisation")
            print("   - Découverte de vulnérabilités")
        
        print("\n" + "-" * 60)
        print("Options:")
        print("  [o]ui - Approuver cette exécution")
        print("  [n]on - Refuser")
        print("  [a]pprouver tout - Approuver pour cette session")
        print("  [q]uitter - Annuler")
        print("-" * 60)
        
        choice = input("\nVotre choix: ").strip().lower()
        
        if choice == "o":
            return PermissionResult(
                granted=True,
                reason="Approuvé par l'utilisateur",
                validation_mode=self.mode,
                approved_by="interactive_user",
                approved_at=datetime.now().isoformat(),
                conditions=[f"Approved for: {' '.join(command)}"]
            )
        elif choice == "a":
            # Ajouter à pré-approuvés pour cette session
            self.pre_approved_tools[tool] = True
            return PermissionResult(
                granted=True,
                reason="Approuvé pour toute la session",
                validation_mode=self.mode,
                approved_by="interactive_user",
                approved_at=datetime.now().isoformat(),
                conditions=["Session-wide approval"]
            )
        elif choice == "n" or choice == "q":
            return PermissionResult(
                granted=False,
                reason="Refusé par l'utilisateur",
                validation_mode=self.mode
            )
        else:
            return PermissionResult(
                granted=False,
                reason="Choix invalide - refusé par défaut",
                validation_mode=self.mode
            )
    
    def _log(self, request: PermissionRequest, result: PermissionResult):
        """Logger pour audit"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "request": request.to_dict(),
            "result": result.to_dict()
        }
        self.audit_log.append(entry)
        
        # Logger aussi via logging standard
        if result.granted:
            logger.info(f"Permission granted: {request.tool} - {request.command}")
        else:
            logger.warning(f"Permission denied: {request.tool} - {request.command}")
    
    def _is_cache_valid(self, result: PermissionResult) -> bool:
        """Vérifier si le cache est encore valide (24h)"""
        if not result.approved_at:
            return False
        try:
            approved = datetime.fromisoformat(result.approved_at)
            elapsed = datetime.now() - approved
            return elapsed.total_seconds() < 86400  # 24h
        except (ValueError, TypeError):
            return False
    
    def get_audit_log(self) -> List[Dict]:
        """Renvoyer le journal d'audit"""
        return self.audit_log
    
    def export_audit_log(self, path: str):
        """Exporter le journal d'audit vers un fichier"""
        with open(path, 'w') as f:
            json.dump(self.audit_log, f, indent=2, default=str)


class SafeExecutor:
    """
    Exécuteur sûr avec validation des permissions.
    
    Wrapper autour de subprocess.run avec validation.
    """
    
    def __init__(self, mode: ExecutionMode = ExecutionMode.PLAN):
        self.validator = PermissionValidator(mode)
    
    def execute(
        self,
        command: List[str],
        context: Dict[str, Any] = None,
        user_id: str = None,
        mission_id: str = None,
        timeout: int = 30,
        capture_output: bool = True
    ) -> Tuple[bool, Any, PermissionResult]:
        """
        Exécuter une commande avec validation.
        
        Returns:
            Tuple (success, output, permission_result)
        """
        if context is None:
            context = {}
        
        tool = Path(command[0]).stem if command else "unknown"
        
        # Demander permission
        permission = self.validator.validate(
            tool=tool,
            command=command,
            context=context,
            user_id=user_id,
            mission_id=mission_id
        )
        
        if not permission.granted:
            logger.warning(f"Execution denied: {permission.reason}")
            return False, None, permission
        
        # Exécuter avec restrictions
        import subprocess
        try:
            result = subprocess.run(
                command,
                timeout=timeout,
                capture_output=capture_output,
                text=True
            )
            return result.returncode == 0, result, permission
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {' '.join(command)}")
            return False, "Timeout", permission
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return False, str(e), permission


# Instance globale par défaut
default_validator = PermissionValidator(mode=ExecutionMode.PLAN)
default_executor = SafeExecutor(mode=ExecutionMode.PLAN)


def validate_execution(
    tool: str,
    command: List[str],
    context: Dict[str, Any] = None,
    mode: str = "plan"
) -> PermissionResult:
    """Fonction helper pour valider une exécution"""
    exec_mode = ExecutionMode.PLAN if mode == "plan" else ExecutionMode.REALTIME
    validator = PermissionValidator(mode=exec_mode)
    return validator.validate(tool, command, context or {})


def safe_execute(
    command: List[str],
    context: Dict[str, Any] = None,
    mode: str = "plan"
) -> Tuple[bool, Any, PermissionResult]:
    """Fonction helper pour exécuter en sécurité"""
    exec_mode = ExecutionMode.PLAN if mode == "plan" else ExecutionMode.REALTIME
    executor = SafeExecutor(mode=exec_mode)
    return executor.execute(command, context or {})


if __name__ == "__main__":
    print("=== SHARINGAN PERMISSION SYSTEM TEST ===\n")
    
    # Test avec différents niveaux
    test_cases = [
        ("ls", ["ls", "-la"], "Outil sûr"),
        ("nmap", ["nmap", "-sS", "localhost"], "Scan réseau (HIGH)"),
        ("sqlmap", ["sqlmap", "-u", "http://example.com"], "Exploitation (CRITICAL)")
    ]
    
    for tool, cmd, desc in test_cases:
        print(f"\nTest: {desc}")
        print(f"Commande: {' '.join(cmd)}")
        
        result = validate_execution(tool, cmd, mode="plan")
        print(f"Résultat: {'APPROUVÉ' if result.granted else 'REFUSÉ'}")
        print(f"Raison: {result.reason}")
        if result.warning:
            print(f"Avertissement: {result.warning}")
