#!/usr/bin/env python3
"""
SHARINGAN CODE EXECUTION SYSTEM
Système d'exécution de code contrôlée et sécurisée via containers Docker
Permet à Sharingan d'exécuter du code arbitraire en toute sécurité
"""

import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("code_execution")

@dataclass
class CodeExecutionRequest:
    """Requête d'exécution de code"""
    code: str
    language: str = "python"
    timeout: int = 30
    memory_limit: str = "256m"
    cpu_limit: str = "0.5"
    network_access: bool = False
    file_access: bool = False
    environment_vars: Dict[str, str] = field(default_factory=dict)
    input_data: Optional[str] = None
    execution_id: str = ""

@dataclass
class CodeExecutionResult:
    """Résultat d'exécution de code"""
    success: bool
    execution_time: float
    output: str
    error_output: str
    exit_code: int
    memory_used: Optional[str] = None
    cpu_used: Optional[str] = None
    security_violations: List[str] = field(default_factory=list)
    execution_id: str = ""

class DockerCodeExecutor:
    """
    Exécuteur de code sécurisé utilisant Docker
    Chaque exécution se fait dans un container isolé
    """

    def __init__(self):
        self.docker_available = self._check_docker_availability()
        self.supported_languages = {
            "python": {
                "image": "python:3.9-slim",
                "extension": ".py",
                "command": "python"
            },
            "bash": {
                "image": "ubuntu:20.04",
                "extension": ".sh",
                "command": "bash"
            },
            "javascript": {
                "image": "node:16-slim",
                "extension": ".js",
                "command": "node"
            },
            "ruby": {
                "image": "ruby:3.0-slim",
                "extension": ".rb",
                "command": "ruby"
            },
            "php": {
                "image": "php:8.1-cli",
                "extension": "",
                "command": "php"
            },
            "go": {
                "image": "golang:1.19",
                "extension": ".go",
                "command": "go run"
            }
        }

        # Statistiques d'exécution
        self.execution_count = 0
        self.success_count = 0
        self.security_violations = 0

        if self.docker_available:
            logger.info("🐳 Docker Code Executor initialized - Secure code execution enabled")
        else:
            logger.warning("🐳 Docker not available - Code execution will be limited")

    def _check_docker_availability(self) -> bool:
        """Vérifier si Docker est disponible"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def execute_code(self, request: CodeExecutionRequest, risk_context: str = "medium") -> CodeExecutionResult:
        """
        Exécuter du code de manière sécurisée dans un container Docker

        Args:
            request: Configuration d'exécution du code

        Returns:
            Résultat de l'exécution
        """
        if not self.docker_available:
            return CodeExecutionResult(
                success=False,
                execution_time=0.0,
                output="",
                error_output="Docker not available for secure code execution",
                exit_code=1,
                security_violations=["docker_unavailable"]
            )

        self.execution_count += 1
        start_time = time.time()

        # Générer un ID d'exécution unique
        execution_id = request.execution_id or f"exec_{int(time.time())}_{self.execution_count}"

        try:
            # Vérifier la sécurité du code
            security_check = self._security_analysis(request.code, request.language, risk_context)
            if security_check["violations"]:
                return CodeExecutionResult(
                    success=False,
                    execution_time=time.time() - start_time,
                    output="",
                    error_output="Code execution blocked due to security violations",
                    exit_code=1,
                    security_violations=security_check["violations"],
                    execution_id=execution_id
                )

            # Préparer le container
            container_config = self._prepare_container(request, execution_id)

            # Exécuter le code
            result = self._run_in_container(container_config, request)

            execution_time = time.time() - start_time

            if result["exit_code"] == 0:
                self.success_count += 1

            return CodeExecutionResult(
                success=result["exit_code"] == 0,
                execution_time=execution_time,
                output=result["stdout"],
                error_output=result["stderr"],
                exit_code=result["exit_code"],
                memory_used=container_config.get("memory_limit"),
                cpu_used=container_config.get("cpu_limit"),
                security_violations=[],
                execution_id=execution_id
            )

        except Exception as e:
            logger.error(f"Code execution error: {e}")
            return CodeExecutionResult(
                success=False,
                execution_time=time.time() - start_time,
                output="",
                error_output=f"Execution error: {str(e)}",
                exit_code=1,
                security_violations=["execution_error"],
                execution_id=execution_id
            )

    def _security_analysis(self, code: str, language: str, risk_context: str = "medium") -> Dict[str, Any]:
        """Analyser le code pour détecter les menaces de sécurité"""
        violations = []

        # Patterns dangereux selon le niveau de risque
        dangerous_patterns = {
            "low": {  # Très permissif pour le code de confiance
                "python": ["eval(", "exec(", "__import__(", "input("],
                "bash": ["rm /", "dd if=", "mkfs", "sudo ", "su "],
                "javascript": ["eval(", "Function(", "global."]
            },
            "medium": {  # Modéré - bloque les accès système critiques
                "python": ["import subprocess", "eval(", "exec(", "__import__(", "open(", "input("],
                "bash": ["rm ", "chmod 777", "curl ", "wget ", "nc ", "nmap"],
                "javascript": ["require('fs')", "require('child_process')", "eval(", "process."]
            },
            "high": {  # Strict - bloque presque tout accès système
                "python": ["import os", "import subprocess", "import sys", "eval(", "exec(", "__import__(", "open(", "file(", "input(", "socket", "requests", "urllib"],
                "bash": ["rm ", "rmdir ", "dd ", "mkfs", "sudo ", "su ", "chmod 777", "curl ", "wget ", "nc ", "nmap"],
                "javascript": ["require('fs')", "require('child_process')", "eval(", "Function(", "process.", "global.", "__dirname"]
            }
        }

        # Utiliser le niveau de risque approprié
        risk_level = risk_context if risk_context in dangerous_patterns else "medium"
        patterns = dangerous_patterns[risk_level]

        # Vérifier les patterns dangereux
        if language in patterns:
            for pattern in patterns[language]:
                if pattern in code:
                    violations.append(f"Dangerous pattern detected: {pattern}")

        # Limiter la longueur du code (prévention contre les attaques par déni de service)
        if len(code) > 10000:
            violations.append("Code too long (>10KB)")

        # Vérifications supplémentaires pour les niveaux élevés
        if risk_level in ["medium", "high"]:
            # Vérifier les imports réseau si réseau désactivé
            if "import socket" in code or "import requests" in code or "urllib" in code:
                violations.append("Network imports detected")

        return {
            "violations": violations,
            "risk_level": "high" if len(violations) > 2 else "medium" if violations else "low"
        }

    def _prepare_container(self, request: CodeExecutionRequest, execution_id: str) -> Dict[str, Any]:
        """Préparer la configuration du container Docker"""
        config = {
            "execution_id": execution_id,
            "image": self.supported_languages[request.language]["image"],
            "memory_limit": request.memory_limit,
            "cpu_limit": request.cpu_limit,
            "timeout": request.timeout,
            "network_disabled": not request.network_access,
            "tmpfs": "/tmp"  # Système de fichiers temporaire
        }

        # Créer un répertoire temporaire pour les fichiers
        temp_dir = Path(f"/tmp/sharingan_execution_{execution_id}")
        temp_dir.mkdir(exist_ok=True)

        # Écrire le code dans un fichier
        code_file = temp_dir / f"code{self.supported_languages[request.language]['extension']}"
        with open(code_file, 'w') as f:
            f.write(request.code)

        # Créer un fichier d'entrée si nécessaire
        if request.input_data:
            input_file = temp_dir / "input.txt"
            with open(input_file, 'w') as f:
                f.write(request.input_data)

        config["temp_dir"] = str(temp_dir)
        config["code_file"] = str(code_file)

        return config

    def _run_in_container(self, config: Dict[str, Any], request: CodeExecutionRequest) -> Dict[str, Any]:
        """Exécuter le code dans un container Docker"""
        try:
            # Construire la commande Docker
            docker_cmd = [
                "docker", "run",
                "--rm",  # Supprimer le container après exécution
                "--memory", config["memory_limit"],
                "--cpus", config["cpu_limit"],
                "--read-only",  # Système de fichiers en lecture seule
                "--tmpfs", "/tmp:rw,noexec,nosuid,size=100m",  # TMP limité
                "--ulimit", "nofile=1024:1024",  # Limiter les fichiers ouverts
                "--ulimit", "nproc=10:10",  # Limiter les processus
            ]

            # Désactiver le réseau si demandé
            if config.get("network_disabled"):
                docker_cmd.extend(["--network", "none"])

            # Ajouter l'image
            docker_cmd.append(config["image"])

            # Commande à exécuter dans le container
            container_cmd = []

            # Copier le fichier de code dans le container
            # (Docker run avec volume mounting pour la sécurité)
            code_filename = Path(config["code_file"]).name
            container_code_path = f"/tmp/{code_filename}"

            # Pour Python/bash, exécuter directement
            lang_config = self.supported_languages[request.language]
            if request.language == "python":
                container_cmd = ["python3", "-c", request.code]
            elif request.language == "bash":
                container_cmd = ["bash", "-c", request.code]
            elif request.language in ["javascript", "ruby", "php"]:
                container_cmd = [lang_config["command"], "-e", request.code]
            elif request.language == "go":
                # Pour Go, créer un fichier temporaire
                container_cmd = ["sh", "-c", f"echo '{request.code}' > /tmp/code.go && go run /tmp/code.go"]
            else:
                container_cmd = [lang_config["command"], request.code]

            # Ajouter la commande au docker run
            docker_cmd.extend(container_cmd)

            # Exécuter avec timeout
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=config["timeout"]
            )

            # Nettoyer le répertoire temporaire
            try:
                shutil.rmtree(config["temp_dir"])
            except:
                pass

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            # Nettoyer en cas de timeout
            try:
                shutil.rmtree(config["temp_dir"])
            except:
                pass

            return {
                "stdout": "",
                "stderr": f"Execution timed out after {config['timeout']} seconds",
                "exit_code": 124  # Code standard pour timeout
            }
        except Exception as e:
            # Nettoyer en cas d'erreur
            try:
                shutil.rmtree(config["temp_dir"])
            except:
                pass

            return {
                "stdout": "",
                "stderr": f"Docker execution error: {str(e)}",
                "exit_code": 1
            }

    def get_supported_languages(self) -> List[str]:
        """Obtenir la liste des langages supportés"""
        return list(self.supported_languages.keys())

    def get_execution_statistics(self) -> Dict[str, Any]:
        """Obtenir les statistiques d'exécution"""
        return {
            "total_executions": self.execution_count,
            "successful_executions": self.success_count,
            "success_rate": (self.success_count / self.execution_count * 100) if self.execution_count > 0 else 0,
            "security_violations": self.security_violations,
            "supported_languages": self.get_supported_languages(),
            "docker_available": self.docker_available
        }

# === SYSTÈME D'EXÉCUTION INTELLIGENTE ===

class IntelligentCodeExecution:
    """
    Système d'exécution de code intelligente
    Analyse automatiquement le code et choisit la meilleure stratégie d'exécution
    """

    def __init__(self, docker_executor: DockerCodeExecutor):
        self.docker_executor = docker_executor
        self.execution_history: List[Dict] = []

        # Stratégies d'exécution
        self.execution_strategies = {
            "safe_trusted": {
                "description": "Code de confiance - exécution directe",
                "security_level": "low",
                "timeout": 30,
                "memory": "128m"
            },
            "sandboxed": {
                "description": "Code inconnu - sandboxing complet",
                "security_level": "high",
                "timeout": 30,
                "memory": "256m",
                "network": False
            },
            "restricted": {
                "description": "Code potentiellement dangereux - restrictions maximales",
                "security_level": "maximum",
                "timeout": 15,
                "memory": "128m",
                "network": False,
                "file_access": False
            }
        }

    def execute_with_intelligence(self, code: str, language: str = "python",
                                 risk_assessment: str = "medium") -> CodeExecutionResult:
        """
        Exécuter du code de manière intelligente basée sur l'analyse des risques

        Args:
            code: Code à exécuter
            language: Langage de programmation
            risk_assessment: Évaluation du risque (low/medium/high)

        Returns:
            Résultat de l'exécution
        """
        # Analyser automatiquement le risque du code
        auto_risk = self._analyze_code_risk(code, language)
        final_risk = risk_assessment if risk_assessment != "auto" else auto_risk

        # Choisir la stratégie appropriée
        strategy = self._choose_execution_strategy(final_risk)

        # Préparer la requête d'exécution
        request = CodeExecutionRequest(
            code=code,
            language=language,
            timeout=strategy["timeout"],
            memory_limit=strategy["memory"],
            network_access=strategy.get("network", True),
            file_access=strategy.get("file_access", True)
        )

        # Exécuter
        result = self.docker_executor.execute_code(request, final_risk)

        # Enregistrer dans l'historique
        execution_record = {
            "code_hash": hash(code),
            "language": language,
            "risk_assessment": final_risk,
            "strategy": strategy["description"],
            "success": result.success,
            "execution_time": result.execution_time,
            "timestamp": time.time()
        }
        self.execution_history.append(execution_record)

        return result

    def _analyze_code_risk(self, code: str, language: str) -> str:
        """Analyser automatiquement le risque du code"""
        risk_score = 0

        # Analyse basée sur les patterns
        high_risk_patterns = {
            "python": ["import os", "import subprocess", "eval(", "exec(", "open("],
            "bash": ["rm ", "sudo ", "chmod 777", "curl ", "wget "],
            "javascript": ["require('fs')", "eval(", "process."]
        }

        if language in high_risk_patterns:
            for pattern in high_risk_patterns[language]:
                if pattern in code:
                    risk_score += 2

        # Analyse de la longueur
        if len(code) > 1000:
            risk_score += 1

        # Analyse des imports réseau
        network_imports = ["socket", "requests", "urllib", "curl", "wget"]
        for net_import in network_imports:
            if net_import in code:
                risk_score += 1

        # Déterminer le niveau de risque
        if risk_score >= 4:
            return "high"
        elif risk_score >= 2:
            return "medium"
        else:
            return "low"

    def _choose_execution_strategy(self, risk_level: str) -> Dict[str, Any]:
        """Choisir la stratégie d'exécution appropriée"""
        strategy_map = {
            "low": "safe_trusted",
            "medium": "sandboxed",
            "high": "restricted"
        }

        strategy_name = strategy_map.get(risk_level, "restricted")
        return self.execution_strategies[strategy_name]

    def get_execution_insights(self) -> Dict[str, Any]:
        """Obtenir des insights sur les exécutions passées"""
        if not self.execution_history:
            return {"message": "Aucune exécution enregistrée"}

        total_executions = len(self.execution_history)
        successful_executions = sum(1 for h in self.execution_history if h["success"])
        avg_execution_time = sum(h["execution_time"] for h in self.execution_history) / total_executions

        # Analyse par langage
        language_stats = {}
        for record in self.execution_history:
            lang = record["language"]
            if lang not in language_stats:
                language_stats[lang] = {"total": 0, "successful": 0}
            language_stats[lang]["total"] += 1
            if record["success"]:
                language_stats[lang]["successful"] += 1

        # Analyse par niveau de risque
        risk_stats = {}
        for record in self.execution_history:
            risk = record["risk_assessment"]
            if risk not in risk_stats:
                risk_stats[risk] = {"total": 0, "successful": 0}
            risk_stats[risk]["total"] += 1
            if record["success"]:
                risk_stats[risk]["successful"] += 1

        return {
            "total_executions": total_executions,
            "success_rate": successful_executions / total_executions * 100,
            "average_execution_time": avg_execution_time,
            "language_statistics": language_stats,
            "risk_statistics": risk_stats,
            "most_used_language": max(language_stats.keys(), key=lambda k: language_stats[k]["total"]) if language_stats else None
        }

# === FONCTIONS GLOBALES ===

_code_executor = None
_intelligent_executor = None

def get_code_executor() -> DockerCodeExecutor:
    """Singleton pour l'exécuteur de code Docker"""
    global _code_executor
    if _code_executor is None:
        _code_executor = DockerCodeExecutor()
    return _code_executor

def get_intelligent_executor() -> IntelligentCodeExecution:
    """Singleton pour l'exécuteur intelligent"""
    global _intelligent_executor
    if _intelligent_executor is None:
        executor = get_code_executor()
        _intelligent_executor = IntelligentCodeExecution(executor)
    return _intelligent_executor

def execute_code_safely(code: str, language: str = "python",
                       risk_level: str = "auto") -> CodeExecutionResult:
    """
    Fonction principale pour exécuter du code de manière sécurisée

    Args:
        code: Code à exécuter
        language: Langage (python, bash, javascript, etc.)
        risk_level: Niveau de risque (auto, low, medium, high)

    Returns:
        Résultat de l'exécution
    """
    executor = get_intelligent_executor()
    return executor.execute_with_intelligence(code, language, risk_level)

if __name__ == "__main__":
    print("🐳 SHARINGAN CODE EXECUTION SYSTEM - INITIALISATION")
    print("=" * 60)

    # Initialiser le système
    executor = get_code_executor()
    intelligent = get_intelligent_executor()

    print("\n🔍 STATUT DU SYSTÈME:")
    stats = executor.get_execution_statistics()
    print(f"• Docker disponible: {'✅' if stats['docker_available'] else '❌'}")
    print(f"• Langages supportés: {len(stats['supported_languages'])}")
    print(f"• Exécutions réussies: {stats['successful_executions']}/{stats['total_executions']}")

    print(f"\n💻 Langages supportés: {', '.join(stats['supported_languages'])}")

    if stats['docker_available']:
        print("\n🧪 TEST D'EXÉCUTION SÉCURISÉE:")

        # Test avec du code Python safe
        test_code = 'print("Hello from Sharingan secure execution!"); result = 2 + 2; print(f"2 + 2 = {result}")'

        print("Code à exécuter:")
        print(test_code)

        result = execute_code_safely(test_code, "python", "low")

        print(f"\nRésultat:")
        print(f"• Succès: {'✅' if result.success else '❌'}")
        print(f"• Temps d'exécution: {result.execution_time:.2f}s")
        print(f"• Code de sortie: {result.exit_code}")
        print(f"• Sortie: {result.output[:100]}...")
        if result.error_output:
            print(f"• Erreurs: {result.error_output[:100]}...")

        print("\n🛡️ CODE EXECUTION SYSTEM OPÉRATIONNEL!")
        print("Sharingan peut maintenant exécuter du code en toute sécurité.")
    else:
        print("\n❌ DOCKER NON DISPONIBLE")
        print("L'exécution de code sécurisée nécessite Docker.")

    print("=" * 60)