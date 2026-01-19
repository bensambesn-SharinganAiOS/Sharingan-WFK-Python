#!/usr/bin/env python3
"""
SHARINGAN SYSTEM PERMISSIONS MANAGER
Gestion des permissions système avec sandboxing avancé
Permet à Sharingan d'accéder aux ressources système de manière contrôlée
"""

import sys
import os
import subprocess
import pwd
import grp
import stat
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("permissions")

class PermissionLevel(Enum):
    """Niveaux de permission système"""
    NONE = 0
    READONLY = 1
    BASIC = 2
    ELEVATED = 3
    ADMIN = 4
    ROOT = 5

    def __lt__(self, other):
        if isinstance(other, PermissionLevel):
            return self.value < other.value
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, PermissionLevel):
            return self.value <= other.value
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, PermissionLevel):
            return self.value > other.value
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, PermissionLevel):
            return self.value >= other.value
        return NotImplemented

class ResourceType(Enum):
    """Types de ressources système"""
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    PROCESS = "process"
    SYSTEM = "system"
    HARDWARE = "hardware"

@dataclass
class PermissionRequest:
    """Requête de permission"""
    resource_type: ResourceType
    action: str
    target: str
    permission_level: PermissionLevel
    justification: str = ""
    temporary: bool = True
    timeout: int = 300  # 5 minutes par défaut

@dataclass
class PermissionGrant:
    """Octroi de permission"""
    request: PermissionRequest
    granted: bool
    granted_level: PermissionLevel
    sandbox_id: Optional[str] = None
    restrictions: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=lambda: __import__('time').time())

class SandboxEnvironment:
    """
    Environnement sandbox pour l'exécution contrôlée
    """
    def __init__(self, sandbox_id: str, permission_level: PermissionLevel):
        self.sandbox_id = sandbox_id
        self.permission_level = permission_level
        self.temp_dir = Path(f"/tmp/sharingan_sandbox_{sandbox_id}")
        self.allowed_paths: Set[Path] = set()
        self.blocked_commands: Set[str] = set()
        self.resource_limits = {}
        self.active = False

        self._setup_sandbox()

    def _setup_sandbox(self):
        """Configurer l'environnement sandbox"""
        # Créer répertoire temporaire
        self.temp_dir.mkdir(exist_ok=True)

        # Définir les limites selon le niveau de permission
        if self.permission_level == PermissionLevel.READONLY:
            self.allowed_paths = {Path("/etc/passwd"), Path("/proc/version")}
            self.blocked_commands = {"rm", "dd", "mkfs", "sudo", "su", "chmod", "chown"}
            self.resource_limits = {"cpu": 0.1, "memory": "64m", "disk": "10m"}

        elif self.permission_level == PermissionLevel.BASIC:
            self.allowed_paths = {Path.home(), Path("/tmp"), Path("/var/log")}
            self.blocked_commands = {"sudo", "su", "passwd", "usermod", "mount", "umount"}
            self.resource_limits = {"cpu": 0.5, "memory": "256m", "disk": "100m"}

        elif self.permission_level == PermissionLevel.ELEVATED:
            self.allowed_paths = {Path("/"), Path("/etc"), Path("/var"), Path("/usr")}
            self.blocked_commands = {"sudo", "su", "passwd", "shutdown", "reboot"}
            self.resource_limits = {"cpu": 1.0, "memory": "512m", "disk": "1g"}

        elif self.permission_level >= PermissionLevel.ADMIN:
            # Accès presque complet mais toujours sandboxé
            self.allowed_paths = {Path("/")}
            self.blocked_commands = {"shutdown", "reboot", "halt", "poweroff"}
            self.resource_limits = {"cpu": 2.0, "memory": "1g", "disk": "10g"}

    def validate_path_access(self, path: Path, write_access: bool = False) -> bool:
        """Valider l'accès à un chemin"""
        if not self.active:
            return False

        # Vérifier si le chemin est dans les chemins autorisés
        for allowed_path in self.allowed_paths:
            try:
                path.relative_to(allowed_path)
                if write_access and self.permission_level == PermissionLevel.READONLY:
                    return False
                return True
            except ValueError:
                continue

        return False

    def validate_command(self, command: str) -> bool:
        """Valider l'exécution d'une commande"""
        if not self.active:
            return False

        cmd_base = command.split()[0] if command else ""
        return cmd_base not in self.blocked_commands

    def execute_in_sandbox(self, command: str, cwd: Optional[Path] = None) -> Tuple[int, str, str]:
        """
        Exécuter une commande dans le sandbox

        Returns:
            (return_code, stdout, stderr)
        """
        if not self.active or not self.validate_command(command):
            return (1, "", "Command blocked by sandbox")

        try:
            # Préparer l'environnement
            env = os.environ.copy()
            env["SANDBOX_ID"] = self.sandbox_id
            env["SANDBOX_LEVEL"] = self.permission_level.name

            # Limites de ressources
            docker_limits = []
            if "memory" in self.resource_limits:
                docker_limits.extend(["--memory", self.resource_limits["memory"]])
            if "cpu" in self.resource_limits:
                docker_limits.extend(["--cpus", str(self.resource_limits["cpu"])])

            # Exécuter dans un container Docker pour isolation supplémentaire
            docker_cmd = [
                "docker", "run", "--rm",
                "--network", "none" if self.permission_level.value < 3 else "host",
                "--read-only",
                "--tmpfs", "/tmp",
                "-v", f"{self.temp_dir}:/sandbox",
                "-e", f"SANDBOX_ID={self.sandbox_id}",
                "-w", "/sandbox"
            ] + docker_limits + [
                "ubuntu:20.04",
                "bash", "-c", command
            ]

            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(cwd) if cwd else None,
                env=env
            )

            return (result.returncode, result.stdout, result.stderr)

        except subprocess.TimeoutExpired:
            return (124, "", "Command timed out")
        except Exception as e:
            return (1, "", f"Sandbox execution error: {str(e)}")

    def cleanup(self):
        """Nettoyer l'environnement sandbox"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            self.active = False
        except Exception as e:
            logger.error(f"Sandbox cleanup error: {e}")

class SystemPermissionsManager:
    """
    Gestionnaire de permissions système avec sandboxing
    """

    def __init__(self):
        self.current_user = os.getuid()
        self.current_groups = os.getgroups()
        self.is_root = self.current_user == 0

        # Sandboxes actives
        self.active_sandboxes: Dict[str, SandboxEnvironment] = {}

        # Historique des permissions
        self.permission_history: List[PermissionGrant] = []

        # Politiques de sécurité
        self.security_policies = self._load_security_policies()

        logger.info(f" System Permissions Manager initialized - User: {self.current_user}, Root: {self.is_root}")

    def _load_security_policies(self) -> Dict[str, Any]:
        """Charger les politiques de sécurité"""
        return {
            "max_concurrent_sandboxes": 5,
            "default_permission_level": PermissionLevel.BASIC,
            "require_justification": True,
            "auto_cleanup": True,
            "audit_all_access": True
        }

    def request_permission(self, request: PermissionRequest) -> PermissionGrant:
        """
        Demander une permission système

        Args:
            request: Requête de permission

        Returns:
            Octroi de permission
        """
        # Évaluer la requête
        evaluation = self._evaluate_permission_request(request)

        grant = PermissionGrant(
            request=request,
            granted=evaluation["granted"],
            granted_level=evaluation["level"],
            restrictions=evaluation["restrictions"]
        )

        if grant.granted:
            # Créer un sandbox si nécessaire
            if request.resource_type in [ResourceType.FILESYSTEM, ResourceType.PROCESS]:
                sandbox = self._create_sandbox_for_request(request)
                if sandbox:
                    grant.sandbox_id = sandbox.sandbox_id
                    self.active_sandboxes[sandbox.sandbox_id] = sandbox

        # Enregistrer dans l'historique
        self.permission_history.append(grant)

        logger.info(f"Permission {'granted' if grant.granted else 'denied'}: {request.action} on {request.target}")
        return grant

    def _evaluate_permission_request(self, request: PermissionRequest) -> Dict[str, Any]:
        """Évaluer une requête de permission"""
        restrictions = []

        # Vérifications de base
        if not request.justification and self.security_policies["require_justification"]:
            return {"granted": False, "level": PermissionLevel.NONE, "restrictions": ["Justification required"]}

        # Évaluation basée sur le type de ressource et l'action
        if request.resource_type == ResourceType.FILESYSTEM:
            return self._evaluate_filesystem_request(request)
        elif request.resource_type == ResourceType.NETWORK:
            return self._evaluate_network_request(request)
        elif request.resource_type == ResourceType.PROCESS:
            return self._evaluate_process_request(request)
        elif request.resource_type == ResourceType.SYSTEM:
            return self._evaluate_system_request(request)
        elif request.resource_type == ResourceType.HARDWARE:
            return self._evaluate_hardware_request(request)

        return {"granted": False, "level": PermissionLevel.NONE, "restrictions": ["Unknown resource type"]}

    def _evaluate_filesystem_request(self, request: PermissionRequest) -> Dict[str, Any]:
        """Évaluer une requête d'accès au système de fichiers"""
        target_path = Path(request.target)

        # Chemins sensibles
        sensitive_paths = ["/etc/shadow", "/etc/sudoers", "/root/.ssh", "/home/*/.ssh"]
        for sensitive in sensitive_paths:
            if target_path.match(sensitive):
                if request.permission_level < PermissionLevel.ADMIN:
                    return {"granted": False, "level": PermissionLevel.NONE, "restrictions": ["Access to sensitive file denied"]}

        # Écriture vs lecture
        if "write" in request.action.lower() or "modify" in request.action.lower():
            if request.permission_level < PermissionLevel.BASIC:
                return {"granted": False, "level": PermissionLevel.NONE, "restrictions": ["Write access denied"]}

        # Permission basée sur le niveau demandé
        max_allowed = self._get_max_allowed_level()
        granted_level = request.permission_level if request.permission_level.value <= max_allowed.value else max_allowed

        return {
            "granted": True,
            "level": granted_level,
            "restrictions": ["Read-only" if granted_level == PermissionLevel.READONLY else []]
        }

    def _evaluate_network_request(self, request: PermissionRequest) -> Dict[str, Any]:
        """Évaluer une requête d'accès réseau"""
        # Réseau généralement restreint
        if request.permission_level < PermissionLevel.ELEVATED:
            return {"granted": False, "level": PermissionLevel.NONE, "restrictions": ["Network access restricted"]}

        return {
            "granted": True,
            "level": min(request.permission_level, PermissionLevel.ELEVATED),
            "restrictions": ["Limited network access"]
        }

    def _evaluate_process_request(self, request: PermissionRequest) -> Dict[str, Any]:
        """Évaluer une requête d'accès aux processus"""
        if request.permission_level < PermissionLevel.BASIC:
            return {"granted": False, "level": PermissionLevel.NONE, "restrictions": ["Process access denied"]}

        return {
            "granted": True,
            "level": min(request.permission_level, PermissionLevel.ADMIN),
            "restrictions": ["Limited process manipulation"]
        }

    def _evaluate_system_request(self, request: PermissionRequest) -> Dict[str, Any]:
        """Évaluer une requête d'accès système"""
        # Accès système très restreint
        if request.permission_level < PermissionLevel.ADMIN:
            return {"granted": False, "level": PermissionLevel.NONE, "restrictions": ["System access denied"]}

        return {
            "granted": True,
            "level": min(request.permission_level, PermissionLevel.ADMIN),
            "restrictions": ["Limited system modifications"]
        }

    def _evaluate_hardware_request(self, request: PermissionRequest) -> Dict[str, Any]:
        """Évaluer une requête d'accès matériel"""
        # Accès matériel généralement refusé
        return {"granted": False, "level": PermissionLevel.NONE, "restrictions": ["Hardware access denied"]}

    def _get_max_allowed_level(self) -> PermissionLevel:
        """Obtenir le niveau de permission maximum autorisé"""
        if self.is_root:
            return PermissionLevel.ROOT
        elif self.current_user in [1000, 1001]:  # Utilisateurs standards
            return PermissionLevel.ELEVATED
        else:
            return PermissionLevel.BASIC

    def _create_sandbox_for_request(self, request: PermissionRequest) -> Optional[SandboxEnvironment]:
        """Créer un sandbox pour une requête"""
        if len(self.active_sandboxes) >= self.security_policies["max_concurrent_sandboxes"]:
            return None

        sandbox_id = f"sandbox_{int(__import__('time').time())}_{len(self.active_sandboxes)}"
        sandbox = SandboxEnvironment(sandbox_id, request.permission_level)
        sandbox.active = True

        return sandbox

    def execute_with_permission(self, command: str, permission_request: PermissionRequest) -> Tuple[int, str, str]:
        """
        Exécuter une commande avec les permissions appropriées

        Args:
            command: Commande à exécuter
            permission_request: Requête de permission

        Returns:
            (return_code, stdout, stderr)
        """
        # Demander la permission
        grant = self.request_permission(permission_request)

        if not grant.granted:
            return (1, "", f"Permission denied: {', '.join(grant.restrictions)}")

        # Exécuter dans le sandbox approprié
        if grant.sandbox_id and grant.sandbox_id in self.active_sandboxes:
            sandbox = self.active_sandboxes[grant.sandbox_id]
            return sandbox.execute_in_sandbox(command)

        # Exécution directe (pour les permissions élevées)
        try:
            result = subprocess.run(
                command.split(),  # SECURITY: Removed shell=True
                capture_output=True,
                text=True,
                timeout=30
            )
            return (result.returncode, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            return (124, "", "Command timed out")
        except Exception as e:
            return (1, "", f"Execution error: {str(e)}")

    def get_permission_statistics(self) -> Dict[str, Any]:
        """Obtenir les statistiques de permissions"""
        total_requests = len(self.permission_history)
        granted_requests = sum(1 for g in self.permission_history if g.granted)
        active_sandboxes = len(self.active_sandboxes)

        # Statistiques par type de ressource
        resource_stats = {}
        for grant in self.permission_history:
            resource = grant.request.resource_type.value
            if resource not in resource_stats:
                resource_stats[resource] = {"total": 0, "granted": 0}
            resource_stats[resource]["total"] += 1
            if grant.granted:
                resource_stats[resource]["granted"] += 1

        return {
            "total_requests": total_requests,
            "granted_requests": granted_requests,
            "grant_rate": (granted_requests / total_requests * 100) if total_requests > 0 else 0,
            "active_sandboxes": active_sandboxes,
            "resource_statistics": resource_stats,
            "current_user": self.current_user,
            "is_root": self.is_root
        }

    def cleanup_expired_permissions(self):
        """Nettoyer les permissions expirées"""
        current_time = __import__('time').time()
        expired = []

        for sandbox_id, sandbox in self.active_sandboxes.items():
            # Les sandboxes temporaires expirent après 30 minutes
            if current_time - sandbox.temp_dir.stat().st_ctime > 1800:
                expired.append(sandbox_id)

        for sandbox_id in expired:
            self.active_sandboxes[sandbox_id].cleanup()
            del self.active_sandboxes[sandbox_id]

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sandboxes")

# === FONCTIONS GLOBALES ===

_permissions_manager = None

def get_permissions_manager() -> SystemPermissionsManager:
    """Singleton pour le gestionnaire de permissions"""
    global _permissions_manager
    if _permissions_manager is None:
        _permissions_manager = SystemPermissionsManager()
    return _permissions_manager

def request_system_permission(resource_type: ResourceType, action: str, target: str,
                            permission_level: PermissionLevel, justification: str = "") -> PermissionGrant:
    """
    Demander une permission système

    Args:
        resource_type: Type de ressource
        action: Action demandée
        target: Cible de l'action
        permission_level: Niveau de permission demandé
        justification: Justification de la demande

    Returns:
        Octroi de permission
    """
    manager = get_permissions_manager()
    request = PermissionRequest(
        resource_type=resource_type,
        action=action,
        target=target,
        permission_level=permission_level,
        justification=justification
    )
    return manager.request_permission(request)

def execute_with_permissions(command: str, resource_type: ResourceType, action: str,
                           target: str, permission_level: PermissionLevel, justification: str = "") -> Tuple[int, str, str]:
    """
    Exécuter une commande avec vérification de permissions

    Args:
        command: Commande à exécuter
        resource_type: Type de ressource
        action: Action
        target: Cible
        permission_level: Niveau demandé
        justification: Justification

    Returns:
        (return_code, stdout, stderr)
    """
    manager = get_permissions_manager()
    request = PermissionRequest(
        resource_type=resource_type,
        action=action,
        target=target,
        permission_level=permission_level,
        justification=justification
    )
    return manager.execute_with_permission(command, request)

if __name__ == "__main__":
    print(" SHARINGAN SYSTEM PERMISSIONS MANAGER")
    print("=" * 60)

    manager = get_permissions_manager()

    # Statistiques
    stats = manager.get_permission_statistics()
    print("\n🔐 STATUT DES PERMISSIONS:")
    print(f"• Utilisateur actuel: {stats['current_user']}")
    print(f"• Accès root: {'✅' if stats['is_root'] else '❌'}")
    print(f"• Sandboxes actifs: {stats['active_sandboxes']}")
    print(f"• Requêtes totales: {stats['total_requests']}")
    print(f"• Taux d'acceptation: {stats['grant_rate']:.1f}%")
    # Test de permissions
    print("\n🧪 TESTS DE PERMISSIONS:")
    # Test lecture fichier de base
    grant1 = request_system_permission(
        ResourceType.FILESYSTEM, "read", "/etc/passwd",
        PermissionLevel.BASIC, "Test de lecture fichier système"
    )
    print(f"• Lecture /etc/passwd: {'✅' if grant1.granted else '❌'} (niveau: {grant1.granted_level.name})")

    # Test écriture (devrait échouer)
    grant2 = request_system_permission(
        ResourceType.FILESYSTEM, "write", "/etc/shadow",
        PermissionLevel.BASIC, "Test écriture fichier sensible"
    )
    print(f"• Écriture /etc/shadow: {'✅' if grant2.granted else '❌'} (niveau: {grant2.granted_level.name})")

    # Test accès réseau
    grant3 = request_system_permission(
        ResourceType.NETWORK, "connect", "8.8.8.8:53",
        PermissionLevel.ELEVATED, "Test connexion DNS"
    )
    print(f"• Accès réseau: {'✅' if grant3.granted else '❌'} (niveau: {grant3.granted_level.name})")

    print("\n📊 STATISTIQUES APRÈS TESTS:")
    stats_after = manager.get_permission_statistics()
    print(f"• Requêtes totales: {stats_after['total_requests']}")
    print(f"• Taux d'acceptation: {stats_after['grant_rate']:.1f}%")
    print("=" * 60)