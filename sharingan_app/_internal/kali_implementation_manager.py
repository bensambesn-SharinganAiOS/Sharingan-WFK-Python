#!/usr/bin/env python3
"""
SHARINGAN KALI IMPLEMENTATION MANAGER
Système de déploiement automatique des outils Kali Linux
Gère l'installation et l'intégration des 47+ outils manquants
"""

import sys
import os
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kali_manager")

@dataclass
class KaliTool:
    """Représentation d'un outil Kali"""
    name: str
    category: str
    description: str
    installation_method: str  # pip, git, apt, manual
    repository_url: Optional[str] = None
    package_name: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    installed: bool = False
    version: Optional[str] = None
    last_check: Optional[float] = None

@dataclass
class InstallationResult:
    """Résultat d'une installation d'outil"""
    success: bool
    tool_name: str
    method: str
    execution_time: float
    output: str
    error_output: str
    version: Optional[str] = None

class KaliToolManager:
    """
    Gestionnaire automatique des outils Kali
    Installe et maintient les outils de cybersécurité
    """

    def __init__(self):
        self.tools_db_path = Path("/root/Projets/Sharingan-WFK-Python/sharingan_app/_internal/kali_tools_db.json")
        self.tools_dir = Path("/root/Projets/Sharingan-WFK-Python/tools")
        self.tools_dir.mkdir(exist_ok=True)

        # Base de données complète des outils Kali
        self.tools_database = self._initialize_tools_database()
        self.installed_tools = self._load_installed_tools()

        # Statistiques
        self.installation_attempts = 0
        self.successful_installations = 0

    def _initialize_tools_database(self) -> Dict[str, KaliTool]:
        """Initialiser la base de données des outils Kali"""
        tools = {}

        # === ENUMERATION TOOLS ===
        enumeration_tools = [
            KaliTool(
                name="dnsrecon",
                category="enumeration",
                description="DNS enumeration tool",
                installation_method="pip",
                package_name="dnsrecon"
            ),
            KaliTool(
                name="fierce",
                category="enumeration",
                description="DNS reconnaissance tool",
                installation_method="git",
                repository_url="https://github.com/mschwager/fierce.git",
                dependencies=["python3", "python3-dnspython"]
            ),
            KaliTool(
                name="dnsenum",
                category="enumeration",
                description="DNS enumeration tool",
                installation_method="apt",
                package_name="dnsenum"
            ),
            KaliTool(
                name="theHarvester",
                category="enumeration",
                description="Email, domain and IP harvesting tool",
                installation_method="git",
                repository_url="https://github.com/laramies/theHarvester.git",
                dependencies=["python3", "python3-requests"]
            )
        ]

        # === MONITORING TOOLS ===
        monitoring_tools = [
            KaliTool(
                name="tcpdump",
                category="monitoring",
                description="Network packet analyzer",
                installation_method="apt",
                package_name="tcpdump"
            ),
            KaliTool(
                name="ettercap",
                category="monitoring",
                description="Network sniffer/interceptor",
                installation_method="apt",
                package_name="ettercap-graphical"
            ),
            KaliTool(
                name="driftnet",
                category="monitoring",
                description="Network image sniffer",
                installation_method="apt",
                package_name="driftnet"
            ),
            KaliTool(
                name="wireshark",
                category="monitoring",
                description="Network protocol analyzer",
                installation_method="apt",
                package_name="wireshark"
            )
        ]

        # === POST-EXPLOIT TOOLS ===
        post_exploit_tools = [
            KaliTool(
                name="Covenant",
                category="post-exploit",
                description="C2 framework (.NET)",
                installation_method="git",
                repository_url="https://github.com/cobbr/Covenant.git",
                dependencies=["dotnet-sdk-6.0"]
            ),
            KaliTool(
                name="Empire",
                category="post-exploit",
                description="Post-exploitation framework",
                installation_method="git",
                repository_url="https://github.com/EmpireProject/Empire.git",
                dependencies=["python3", "python3-pip"]
            ),
            KaliTool(
                name="Meterpreter",
                category="post-exploit",
                description="Metasploit payload",
                installation_method="metasploit",
                package_name="metasploit-framework"
            )
        ]

        # === REPORTING TOOLS ===
        reporting_tools = [
            KaliTool(
                name="faraday",
                category="reporting",
                description="Collaborative penetration testing tool",
                installation_method="git",
                repository_url="https://github.com/infobyte/faraday.git",
                dependencies=["python3", "python3-pip", "postgresql"]
            ),
            KaliTool(
                name="pipal",
                category="reporting",
                description="Password analysis tool",
                installation_method="git",
                repository_url="https://github.com/digininja/pipal.git",
                dependencies=["ruby"]
            ),
            KaliTool(
                name="Dradis",
                category="reporting",
                description="Collaboration and reporting framework",
                installation_method="git",
                repository_url="https://github.com/dradis/dradis-ce.git",
                dependencies=["ruby", "bundler", "nodejs", "postgresql"]
            )
        ]

        # === SOCIAL ENGINEERING ===
        social_tools = [
            KaliTool(
                name="king-phisher",
                category="social-engineering",
                description="Phishing campaign toolkit",
                installation_method="git",
                repository_url="https://github.com/rsmusllp/king-phisher.git",
                dependencies=["python3", "python3-gi"]
            ),
            KaliTool(
                name="Social-Engineer Toolkit",
                category="social-engineering",
                description="Social engineering toolkit",
                installation_method="git",
                repository_url="https://github.com/trustedsec/social-engineer-toolkit.git",
                dependencies=["python3", "python3-pip"]
            )
        ]

        # === VULNERABILITY SCANNERS ===
        vuln_scanners = [
            KaliTool(
                name="OpenVAS",
                category="vulnerability",
                description="Open Vulnerability Assessment System",
                installation_method="apt",
                package_name="openvas",
                dependencies=["postgresql", "redis-server"]
            )
        ]

        # === REVERSE ENGINEERING ===
        reverse_tools = [
            KaliTool(
                name="radare2",
                category="reverse-engineering",
                description="Reverse engineering framework",
                installation_method="apt",
                package_name="radare2"
            ),
            KaliTool(
                name="Ghidra",
                category="reverse-engineering",
                description="Software reverse engineering suite",
                installation_method="manual",
                repository_url="https://github.com/NationalSecurityAgency/ghidra/releases"
            )
        ]

        # Ajouter tous les outils à la base de données
        all_tools = (enumeration_tools + monitoring_tools + post_exploit_tools +
                    reporting_tools + social_tools + vuln_scanners + reverse_tools)

        for tool in all_tools:
            tools[tool.name] = tool

        return tools

    def _load_installed_tools(self) -> Dict[str, KaliTool]:
        """Charger la liste des outils installés"""
        if not self.tools_db_path.exists():
            return {}

        try:
            with open(self.tools_db_path, 'r') as f:
                data = json.load(f)

            installed = {}
            for name, tool_data in data.items():
                tool = KaliTool(**tool_data)
                if tool.installed:
                    installed[name] = tool

            return installed
        except Exception as e:
            logger.error(f"Error loading tools database: {e}")
            return {}

    def _save_tools_database(self):
        """Sauvegarder la base de données des outils"""
        try:
            data = {}
            for name, tool in self.tools_database.items():
                data[name] = {
                    "name": tool.name,
                    "category": tool.category,
                    "description": tool.description,
                    "installation_method": tool.installation_method,
                    "repository_url": tool.repository_url,
                    "package_name": tool.package_name,
                    "dependencies": tool.dependencies,
                    "installed": tool.installed,
                    "version": tool.version,
                    "last_check": tool.last_check
                }

            with open(self.tools_db_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving tools database: {e}")

    def install_tool(self, tool_name: str) -> InstallationResult:
        """
        Installer un outil Kali spécifique

        Args:
            tool_name: Nom de l'outil à installer

        Returns:
            Résultat de l'installation
        """
        if tool_name not in self.tools_database:
            return InstallationResult(
                success=False,
                tool_name=tool_name,
                method="unknown",
                execution_time=0.0,
                output="",
                error_output=f"Tool '{tool_name}' not found in database"
            )

        tool = self.tools_database[tool_name]
        self.installation_attempts += 1

        start_time = time.time()

        try:
            if tool.installation_method == "pip":
                result = self._install_via_pip(tool)
            elif tool.installation_method == "git":
                result = self._install_via_git(tool)
            elif tool.installation_method == "apt":
                result = self._install_via_apt(tool)
            elif tool.installation_method == "metasploit":
                result = self._install_metasploit_tool(tool)
            elif tool.installation_method == "manual":
                result = self._install_manually(tool)
            else:
                result = InstallationResult(
                    success=False,
                    tool_name=tool_name,
                    method=tool.installation_method,
                    execution_time=time.time() - start_time,
                    output="",
                    error_output=f"Unsupported installation method: {tool.installation_method}"
                )

            if result.success:
                self.successful_installations += 1
                tool.installed = True
                tool.version = result.version
                tool.last_check = time.time()
                self.installed_tools[tool_name] = tool
                self._save_tools_database()

            return result

        except Exception as e:
            return InstallationResult(
                success=False,
                tool_name=tool_name,
                method=tool.installation_method,
                execution_time=time.time() - start_time,
                output="",
                error_output=f"Installation error: {str(e)}"
            )

    def _install_via_pip(self, tool: KaliTool) -> InstallationResult:
        """Installer via pip"""
        try:
            cmd = [sys.executable, "-m", "pip", "install", tool.package_name or tool.name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            version = None
            if result.returncode == 0:
                # Essayer de récupérer la version
                version_cmd = [sys.executable, "-c", f"import {tool.name}; print({tool.name}.__version__ if hasattr({tool.name}, '__version__') else 'installed')"]
                version_result = subprocess.run(version_cmd, capture_output=True, text=True, timeout=10)
                if version_result.returncode == 0:
                    version = version_result.stdout.strip()

            return InstallationResult(
                success=result.returncode == 0,
                tool_name=tool.name,
                method="pip",
                execution_time=0.0,  # Sera défini par l'appelant
                output=result.stdout,
                error_output=result.stderr,
                version=version
            )
        except subprocess.TimeoutExpired:
            return InstallationResult(
                success=False,
                tool_name=tool.name,
                method="pip",
                execution_time=0.0,
                output="",
                error_output="Installation timed out"
            )

    def _install_via_git(self, tool: KaliTool) -> InstallationResult:
        """Installer via git clone"""
        try:
            if not tool.repository_url:
                return InstallationResult(
                    success=False,
                    tool_name=tool.name,
                    method="git",
                    execution_time=0.0,
                    output="",
                    error_output="No repository URL provided"
                )

            # Cloner dans le répertoire tools
            tool_dir = self.tools_dir / tool.name
            if tool_dir.exists():
                # Mettre à jour si existe
                cmd = ["git", "-C", str(tool_dir), "pull"]
            else:
                cmd = ["git", "clone", tool.repository_url, str(tool_dir)]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and tool_dir.exists():
                # Installer les dépendances si requirements.txt existe
                requirements_file = tool_dir / "requirements.txt"
                if requirements_file.exists():
                    pip_cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
                    pip_result = subprocess.run(pip_cmd, capture_output=True, text=True, timeout=300)
                    if pip_result.returncode != 0:
                        return InstallationResult(
                            success=False,
                            tool_name=tool.name,
                            method="git",
                            execution_time=0.0,
                            output=result.stdout,
                            error_output=f"Git clone successful but pip install failed: {pip_result.stderr}"
                        )

            return InstallationResult(
                success=result.returncode == 0,
                tool_name=tool.name,
                method="git",
                execution_time=0.0,
                output=result.stdout,
                error_output=result.stderr,
                version="latest"
            )
        except subprocess.TimeoutExpired:
            return InstallationResult(
                success=False,
                tool_name=tool.name,
                method="git",
                execution_time=0.0,
                output="",
                error_output="Git clone timed out"
            )

    def _install_via_apt(self, tool: KaliTool) -> InstallationResult:
        """Installer via apt"""
        try:
            package_name = tool.package_name or tool.name
            cmd = ["apt", "update", "&&", "apt", "install", "-y", package_name]

            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=600)  # SECURITY: Removed shell=True

            version = None
            if result.returncode == 0:
                # Récupérer la version
                version_cmd = ["dpkg", "-s", package_name]
                version_result = subprocess.run(version_cmd, capture_output=True, text=True, timeout=10)
                if version_result.returncode == 0:
                    for line in version_result.stdout.split('\n'):
                        if line.startswith('Version:'):
                            version = line.split(':', 1)[1].strip()
                            break

            return InstallationResult(
                success=result.returncode == 0,
                tool_name=tool.name,
                method="apt",
                execution_time=0.0,
                output=result.stdout,
                error_output=result.stderr,
                version=version
            )
        except subprocess.TimeoutExpired:
            return InstallationResult(
                success=False,
                tool_name=tool.name,
                method="apt",
                execution_time=0.0,
                output="",
                error_output="Apt install timed out"
            )

    def _install_metasploit_tool(self, tool: KaliTool) -> InstallationResult:
        """Installer un outil Metasploit"""
        try:
            # Vérifier si Metasploit est installé
            msf_cmd = ["msfconsole", "--version"]
            msf_result = subprocess.run(msf_cmd, capture_output=True, text=True, timeout=10)

            if msf_result.returncode != 0:
                return InstallationResult(
                    success=False,
                    tool_name=tool.name,
                    method="metasploit",
                    execution_time=0.0,
                    output="",
                    error_output="Metasploit framework not found"
                )

            # Pour Meterpreter, c'est inclus dans Metasploit
            return InstallationResult(
                success=True,
                tool_name=tool.name,
                method="metasploit",
                execution_time=0.0,
                output="Available through Metasploit framework",
                error_output="",
                version=msf_result.stdout.strip().split()[-1] if msf_result.stdout else "unknown"
            )
        except Exception as e:
            return InstallationResult(
                success=False,
                tool_name=tool.name,
                method="metasploit",
                execution_time=0.0,
                output="",
                error_output=str(e)
            )

    def _install_manually(self, tool: KaliTool) -> InstallationResult:
        """Installation manuelle (téléchargement requis)"""
        return InstallationResult(
            success=False,
            tool_name=tool.name,
            method="manual",
            execution_time=0.0,
            output="",
            error_output=f"Manual installation required. Please visit: {tool.repository_url}"
        )

    def batch_install_tools(self, tool_names: List[str]) -> List[InstallationResult]:
        """
        Installer plusieurs outils en batch

        Args:
            tool_names: Liste des noms d'outils à installer

        Returns:
            Liste des résultats d'installation
        """
        results = []
        for tool_name in tool_names:
            logger.info(f"Installing tool: {tool_name}")
            result = self.install_tool(tool_name)
            results.append(result)

            if result.success:
                logger.info(f" Successfully installed {tool_name}")
            else:
                logger.error(f"❌ Failed to install {tool_name}: {result.error_output}")

        return results

    def get_tools_by_category(self, category: str) -> List[KaliTool]:
        """Obtenir les outils d'une catégorie spécifique"""
        return [tool for tool in self.tools_database.values() if tool.category == category]

    def get_installation_statistics(self) -> Dict[str, Any]:
        """Obtenir les statistiques d'installation"""
        total_tools = len(self.tools_database)
        installed_tools = len(self.installed_tools)

        categories = {}
        for tool in self.tools_database.values():
            cat = tool.category
            if cat not in categories:
                categories[cat] = {"total": 0, "installed": 0}
            categories[cat]["total"] += 1
            if tool.installed:
                categories[cat]["installed"] += 1

        return {
            "total_tools": total_tools,
            "installed_tools": installed_tools,
            "installation_rate": (installed_tools / total_tools * 100) if total_tools > 0 else 0,
            "installation_attempts": self.installation_attempts,
            "successful_installations": self.successful_installations,
            "success_rate": (self.successful_installations / self.installation_attempts * 100) if self.installation_attempts > 0 else 0,
            "categories": categories
        }

    def check_tool_status(self, tool_name: str) -> Dict[str, Any]:
        """Vérifier le statut d'un outil"""
        if tool_name not in self.tools_database:
            return {"found": False, "error": "Tool not in database"}

        tool = self.tools_database[tool_name]

        # Vérifier l'installation réelle sur le système
        actual_installed = self._verify_tool_installation(tool)

        # Mettre à jour la base de données si nécessaire
        if actual_installed and not tool.installed:
            tool.installed = True
            tool.last_check = time.time()
            self.installed_tools[tool_name] = tool
            self._save_tools_database()
        elif not actual_installed and tool.installed:
            tool.installed = False
            if tool_name in self.installed_tools:
                del self.installed_tools[tool_name]
            self._save_tools_database()

        return {
            "found": True,
            "installed": tool.installed,
            "version": tool.version,
            "category": tool.category,
            "method": tool.installation_method,
            "last_check": tool.last_check,
            "verified": actual_installed
        }

    def _verify_tool_installation(self, tool: KaliTool) -> bool:
        """Vérifier si un outil est réellement installé sur le système"""
        try:
            if tool.installation_method == "pip":
                # Vérifier avec pip show
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "show", tool.package_name or tool.name],
                    capture_output=True, text=True, timeout=10
                )
                return result.returncode == 0

            elif tool.installation_method == "git":
                # Vérifier si le répertoire existe et contient des fichiers
                tool_dir = self.tools_dir / tool.name
                if tool_dir.exists():
                    # Vérifier s'il y a un exécutable ou script principal
                    return self._check_git_tool_executable(tool_dir, tool.name)
                return False

            elif tool.installation_method == "apt":
                # Vérifier avec dpkg
                result = subprocess.run(
                    ["dpkg", "-l", tool.package_name or tool.name],
                    capture_output=True, text=True, timeout=10
                )
                return result.returncode == 0 and "ii" in result.stdout

            elif tool.installation_method == "metasploit":
                # Vérifier Metasploit
                result = subprocess.run(
                    ["which", "msfconsole"],
                    capture_output=True, text=True, timeout=5
                )
                return result.returncode == 0

            elif tool.installation_method == "manual":
                # Pour les outils manuels, vérifier s'ils sont dans PATH
                result = subprocess.run(
                    ["which", tool.name],
                    capture_output=True, text=True, timeout=5
                )
                return result.returncode == 0

            return False

        except Exception:
            return False

    def _check_git_tool_executable(self, tool_dir: Path, tool_name: str) -> bool:
        """Vérifier si un outil git a un exécutable"""
        # Chercher des scripts exécutables courants
        common_executables = [
            f"{tool_name}.py", f"{tool_name}.sh", f"{tool_name}.rb",
            "main.py", "run.py", tool_name, "bin/" + tool_name
        ]

        for exe in common_executables:
            exe_path = tool_dir / exe
            if exe_path.exists() and exe_path.is_file():
                return True

        # Vérifier requirements.txt comme indicateur d'installation
        if (tool_dir / "requirements.txt").exists():
            return True

        return False

    def verify_all_tools(self) -> Dict[str, Any]:
        """Vérifier le statut de tous les outils"""
        verified_count = 0
        newly_found = 0

        for tool_name in self.tools_database:
            status = self.check_tool_status(tool_name)
            if status.get("verified", False):
                verified_count += 1
                if not status.get("installed", False):
                    newly_found += 1

        return {
            "total_tools": len(self.tools_database),
            "verified_installed": verified_count,
            "newly_discovered": newly_found,
            "verification_rate": (verified_count / len(self.tools_database) * 100) if self.tools_database else 0
        }

# === FONCTIONS GLOBALES ===

_kali_manager = None

def get_kali_manager() -> KaliToolManager:
    """Singleton pour le gestionnaire Kali"""
    global _kali_manager
    if _kali_manager is None:
        _kali_manager = KaliToolManager()
    return _kali_manager

def install_kali_tool(tool_name: str) -> InstallationResult:
    """
    Fonction principale pour installer un outil Kali

    Args:
        tool_name: Nom de l'outil à installer

    Returns:
        Résultat de l'installation
    """
    manager = get_kali_manager()
    return manager.install_tool(tool_name)

def batch_install_kali_tools(tool_names: List[str]) -> List[InstallationResult]:
    """
    Installer plusieurs outils Kali

    Args:
        tool_names: Liste des noms d'outils

    Returns:
        Liste des résultats
    """
    manager = get_kali_manager()
    return manager.batch_install_tools(tool_names)

if __name__ == "__main__":
    print("🛠️ SHARINGAN KALI IMPLEMENTATION MANAGER")
    print("=" * 60)

    manager = get_kali_manager()

    # Vérification de tous les outils installés
    print("\n🔍 VÉRIFICATION DES OUTILS INSTALLÉS...")
    verification = manager.verify_all_tools()
    print(f"• Outils vérifiés installés: {verification['verified_installed']}")
    print(f"• Nouveaux outils découverts: {verification['newly_discovered']}")
    print(f"• Taux de vérification: {verification['verification_rate']:.1f}%")
    # Statistiques après vérification
    stats = manager.get_installation_statistics()
    print("\n📊 STATUT APRÈS VÉRIFICATION:")
    print(f"• Outils totaux: {stats['total_tools']}")
    print(f"• Outils installés: {stats['installed_tools']}")
    print(f"• Taux d'installation: {stats['installation_rate']:.1f}%")
    print("\n📊 PAR CATÉGORIE:")
    for cat, cat_stats in stats['categories'].items():
        print(f"• {cat.capitalize()}: {cat_stats['installed']}/{cat_stats['total']}")

    # Test d'installation d'un outil léger si nécessaire
    if stats['installation_rate'] < 50:
        print("\n🧪 TEST D'INSTALLATION SUPPLÉMENTAIRE:")
        test_tool = "theHarvester"  # Outil git pour tester
        print(f"Installation de {test_tool}...")

        result = install_kali_tool(test_tool)

        print(f"• Succès: {'' if result.success else '❌'}")
        print(f"• Méthode: {result.method}")
        print(f"• Temps: {result.execution_time:.2f}s")
        if result.version:
            print(f"• Version: {result.version}")
        if result.error_output:
            print(f"• Erreur: {result.error_output[:100]}...")

        print("\n📈 STATISTIQUES FINAUX:")
        stats_final = manager.get_installation_statistics()
        print(f"• Outils installés: {stats_final['installed_tools']}")
        print(f"• Taux d'installation: {stats_final['installation_rate']:.1f}%")

    print("=" * 60)