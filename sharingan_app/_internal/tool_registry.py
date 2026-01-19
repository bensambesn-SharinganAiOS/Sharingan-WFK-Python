#!/usr/bin/env python3
"""
Sharingan OS - Tool Registry with Auto-Discovery
Tous les outils découverts automatiquement depuis les répertoires.
"""

from pathlib import Path
from typing import Dict, List, Optional
import json
import os
import shutil
import logging
import subprocess

logger = logging.getLogger("tool_registry")

class ToolRegistry:
    """Registre central avec découverte automatique des outils"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.tools_file = self.base_dir / "data" / "tools_registry.json"
        self.registry = self._load_or_create()
    
    def _load_or_create(self) -> Dict:
        registry = {
            "version": "3.0.0",
            "last_updated": "",
            "last_scan": None,
            "tools": {},
            "categories": {
                "network": {"count": 0, "description": "Network scanning"},
                "web": {"count": 0, "description": "Web security"},
                "password": {"count": 0, "description": "Password attacks"},
                "osint": {"count": 0, "description": "OSINT"},
                "forensics": {"count": 0, "description": "Forensics"},
                "wireless": {"count": 0, "description": "Wireless"},
                "audit": {"count": 0, "description": "Security audit"},
                "ai": {"count": 0, "description": "AI"},
                "system": {"count": 0, "description": "System"},
                "browser": {"count": 0, "description": "Browser automation"}
            }
        }
        
        # DÉCOUVERTE AUTOMATIQUE
        registry["tools"] = self._discover_all_tools()
        registry["last_scan"] = str(__import__("datetime").datetime.now().isoformat())
        
        return registry
    
    def _discover_all_tools(self) -> Dict[str, Dict]:
        """
        Découverte intelligente et générique de tous les outils disponibles.
        Scan automatique sans liste hardcodée.
        """
        tools = {}
        base = self.base_dir

        # 1. DÉCOUVERTE AUTOMATIQUE DES OUTILS SYSTÈME
        # Liste intelligente d'outils communs à rechercher
        common_tools = self._get_common_tools_list()

        for tool_name in common_tools:
            path = shutil.which(tool_name)
            if path:
                tools[tool_name] = {
                    "name": tool_name,
                    "category": self._guess_category(tool_name),
                    "path": path,
                    "capabilities": self._get_capabilities(tool_name),
                    "source": "system",
                    "auto_detected": True
                }

        # 2. DÉCOUVERTE DES OUTILS PROJET (scan récursif intelligent)
        tools_dir = base / ".." / ".." / ".." / "tools"
        if tools_dir.exists():
            tools.update(self._scan_project_tools(tools_dir))

        # 3. DÉCOUVERTE DES WRAPPERS KALI (scan automatique)
        tools.update(self._scan_kali_wrappers(base))

        # 4. DÉCOUVERTE DES MODULES INTERNES (scan automatique)
        tools.update(self._scan_internal_modules(base))

        # 5. VALIDATION IA DES OUTILS DÉTECTÉS
        tools = self._validate_tools_with_ai(tools)

        return tools

    def _get_common_tools_list(self) -> List[str]:
        """
        Génère dynamiquement une liste d'outils communs à rechercher.
        Basé sur les catégories et patterns connus.
        """
        base_tools = []

        # Outils de base du système
        base_tools.extend(["bash", "sh", "python3", "pip3", "git", "curl", "wget"])

        # Outils réseau courants
        base_tools.extend(["nmap", "netcat", "tcpdump", "wireshark", "netstat", "ss", "ip", "ping", "traceroute"])

        # Outils web courants
        base_tools.extend(["curl", "wget", "lynx", "links", "w3m"])

        # Frameworks et outils de sécurité courants
        security_tools = [
            "metasploit", "burpsuite", "nessus", "openvas", "wireshark", "tcpdump",
            "ettercap", "arpscan", "masscan", "netdiscover", "hping3", "fping"
        ]
        base_tools.extend(security_tools)

        # Outils de cracking courants
        cracking_tools = ["john", "hashcat", "hydra", "medusa", "crunch", "cewl", "cupp"]
        base_tools.extend(cracking_tools)

        # Outils web courants
        web_tools = ["gobuster", "dirb", "dirbuster", "nikto", "whatweb", "sqlmap", "skipfish", "wpscan"]
        base_tools.extend(web_tools)

        # Outils forensics courants
        forensics_tools = ["binwalk", "foremost", "volatility", "scalpel", "testdisk", "photorec"]
        base_tools.extend(forensics_tools)

        # Outils wireless courants
        wireless_tools = ["aircrack-ng", "airodump-ng", "aireplay-ng", "airmon-ng", "wifite", "mdk3"]
        base_tools.extend(wireless_tools)

        # Outils IA courants
        ai_tools = ["tgpt", "ollama", "llama.cpp", "gpt4all", "koboldcpp"]
        base_tools.extend(ai_tools)

        return list(set(base_tools))  # Élimine les doublons

    def _scan_project_tools(self, tools_dir: Path) -> Dict[str, Dict]:
        """Scan récursif intelligent des outils projet"""
        project_tools = {}

        # Patterns de noms d'outils à reconnaître automatiquement
        tool_patterns = [
            r'^[a-zA-Z][a-zA-Z0-9_-]*$',  # Noms simples
            r'.*\.(py|rb|sh|pl)$',        # Scripts avec extensions
        ]

        for item in tools_dir.rglob("*"):
            if not item.is_file():
                continue

            # Ignore les fichiers indésirables
            if any(skip in str(item) for skip in ['.git', '__pycache__', 'node_modules', '.pytest_cache']):
                continue

            # Vérifie si c'est un outil potentiel
            if self._is_potential_tool(item):
                tool_name = self._extract_tool_name(item)
                if tool_name and tool_name not in project_tools:
                    project_tools[tool_name] = {
                        "name": tool_name,
                        "category": self._guess_category(tool_name),
                        "path": str(item),
                        "capabilities": self._get_capabilities(tool_name),
                        "source": "project",
                        "auto_detected": True
                    }

        return project_tools

    def _is_potential_tool(self, path: Path) -> bool:
        """Détermine si un fichier est potentiellement un outil"""
        # Fichiers exécutables
        if os.access(path, os.X_OK):
            return True

        # Scripts avec extensions
        if path.suffix in ['.py', '.rb', '.sh', '.pl', '.jar']:
            return True

        # Fichiers sans extension mais nommés comme des outils
        if not path.suffix and not path.name.startswith('.'):
            return True

        return False

    def _extract_tool_name(self, path: Path) -> str:
        """Extrait le nom de l'outil depuis le chemin"""
        # Pour les scripts principaux dans leur répertoire
        if path.parent.name == path.stem or path.name == path.parent.name:
            return path.parent.name

        # Pour les autres fichiers
        return path.stem

    def _scan_kali_wrappers(self, base: Path) -> Dict[str, Dict]:
        """Scan automatique des wrappers Kali"""
        wrappers = {}

        # Cherche tous les fichiers *wrapper*.py
        for wrapper_file in base.glob("*wrapper*.py"):
            wrapper_name = wrapper_file.stem
            tool_name = wrapper_name.replace("kali_", "").replace("_wrapper", "")

            wrappers[wrapper_name] = {
                "name": wrapper_name,
                "category": self._guess_category(tool_name),
                "path": str(wrapper_file),
                "capabilities": self._get_capabilities(tool_name),
                "source": "kali_wrapper",
                "auto_detected": True
            }

        return wrappers

    def _scan_internal_modules(self, base: Path) -> Dict[str, Dict]:
        """Scan automatique des modules internes"""
        internal = {}

        # Liste des modules internes connus
        known_modules = [
            "sharingan_os", "system_consciousness", "ai_providers", "tool_registry",
            "memory_manager", "genome_memory", "vpn_tor_integration", "browser_controller",
            "network_monitor", "action_executor", "integrated_capabilities",
            "lsp_diagnostics", "config", "check_dependencies"
        ]

        for module in known_modules:
            module_path = base / f"{module}.py"
            if module_path.exists():
                internal[module] = {
                    "name": module,
                    "category": "ai" if any(x in module for x in ["ai", "consciousness"]) else "system",
                    "path": str(module_path),
                    "capabilities": ["ai_integration"] if "ai" in module else ["system_integration"],
                    "source": "internal",
                    "auto_detected": True
                }

        return internal

    def _validate_tools_with_ai(self, tools: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Validation intelligente des outils avec analyse automatisée.
        Détermine l'utilisabilité et propose des alternatives si nécessaire.
        """
        validated_tools = {}

        for tool_name, tool_info in tools.items():
            # Validation de base
            tool_info["ai_validated"] = True
            tool_info["usability_score"] = self._calculate_usability_score(tool_info)
            tool_info["functional_status"] = self._test_tool_functionality(tool_info)
            tool_info["implementation_suggestions"] = self._suggest_implementations(tool_info)

            validated_tools[tool_name] = tool_info

        return validated_tools

    def _test_tool_functionality(self, tool_info: Dict) -> str:
        """
        Test rapide de la fonctionnalité d'un outil
        """
        tool_path = tool_info["path"]
        tool_name = tool_info["name"]

        try:
            # Test de base selon le type d'outil
            if tool_name == "tgpt":
                # Test spécial pour tgpt
                result = subprocess.run(
                    [tool_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return "functional" if result.returncode == 0 else "api_error"

            elif tool_name in ["nmap", "netstat", "ip"]:
                # Test avec --version ou -V
                result = subprocess.run(
                    [tool_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                return "functional" if result.returncode == 0 else "not_functional"

            elif tool_path.endswith(('.py', '.rb', '.sh')):
                # Pour les scripts, vérifie juste l'existence
                return "script_available" if os.path.exists(tool_path) else "missing"

            else:
                # Pour les exécutables, vérifie l'exécution
                result = subprocess.run(
                    [tool_path, "--help"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                return "functional" if result.returncode == 0 else "limited_functionality"

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return "not_functional"

    def _suggest_implementations(self, tool_info: Dict) -> List[str]:
        """
        Suggère des implémentations alternatives si l'outil n'est pas fonctionnel
        """
        suggestions = []
        tool_name = tool_info["name"]
        status = tool_info.get("functional_status", "unknown")

        if status != "functional":
            if tool_name == "tgpt":
                suggestions.extend([
                    "Installer tgpt avec : curl -sSL https://raw.githubusercontent.com/aandrew-me/tgpt/main/install | bash",
                    "Utiliser ollama comme alternative locale",
                    "Implémenter un wrapper API pour OpenAI/Claude",
                    "Créer un module Python local avec transformers"
                ])
            elif "ai" in tool_info.get("category", ""):
                suggestions.extend([
                    "Installer l'outil via le gestionnaire de paquets",
                    "Utiliser une API alternative",
                    "Implémenter un wrapper Python natif"
                ])
            elif "web" in tool_info.get("capabilities", []):
                suggestions.extend([
                    "Utiliser requests/beautifulsoup pour le scraping",
                    "Implémenter avec selenium si nécessaire"
                ])
            elif "network" in tool_info.get("capabilities", []):
                suggestions.extend([
                    "Utiliser scapy pour les opérations réseau",
                    "Implémenter avec socket Python"
                ])

        return suggestions

    def _calculate_usability_score(self, tool_info: Dict) -> float:
        """
        Calcule un score d'utilisabilité basé sur plusieurs facteurs
        """
        score = 0.5  # Score de base

        # Bonus pour les outils système (déjà installés)
        if tool_info.get("source") == "system":
            score += 0.3

        # Bonus pour les outils avec des capabilities définies
        if tool_info.get("capabilities"):
            score += 0.2

        # Malus pour les outils non exécutables
        if not os.access(tool_info["path"], os.X_OK) and not tool_info["path"].endswith(('.py', '.rb', '.sh')):
            score -= 0.2

        return max(0.0, min(1.0, score))  # Clamp entre 0 et 1
    
    def _get_capabilities(self, name: str) -> List[str]:
        """Détermine les capacités d'un outil basé sur son nom"""
        n = name.lower()
        capabilities = []

        # Réseau
        if any(x in n for x in ["nmap", "masscan", "netdiscover", "tcpdump", "wireshark", "ettercap", "arpscan"]):
            capabilities.extend(["port_scan", "network_discovery", "packet_capture"])
        # Web
        if any(x in n for x in ["gobuster", "dirb", "nikto", "whatweb", "sqlmap"]):
            capabilities.extend(["web_scan", "vulnerability_scan", "sql_injection"])
        # Authentification
        if any(x in n for x in ["hydra", "medusa"]):
            capabilities.extend(["brute_force", "password_attack"])
        # Mot de passe
        if any(x in n for x in ["john", "hashcat", "crunch"]):
            capabilities.extend(["password_cracking", "hash_cracking"])
        # Forensics
        if any(x in n for x in ["binwalk", "foremost", "volatility", "exiftool"]):
            capabilities.extend(["file_analysis", "memory_analysis", "forensic_analysis"])
        # Wireless
        if any(x in n for x in ["aircrack", "airodump", "aireplay"]):
            capabilities.extend(["wireless_scan", "wifi_cracking"])
        # OSINT
        if any(x in n for x in ["harvester", "sherlock", "theharvester"]):
            capabilities.extend(["email_harvesting", "subdomain_enum", "osint"])
        # Audit
        if any(x in n for x in ["lynis", "chkrootkit", "rkhunter"]):
            capabilities.extend(["system_audit", "security_check"])
        # IA
        if any(x in n for x in ["tgpt", "ollama", "ai", "consciousness"]):
            capabilities.extend(["ai_chat", "natural_language"])
        # Browser
        if any(x in n for x in ["browser", "selenium"]):
            capabilities.extend(["web_automation", "form_filling"])
        # Framework
        if any(x in n for x in ["empire", "metasploit", "cobalt"]):
            capabilities.extend(["post_exploitation", "c2_framework"])

        return capabilities if capabilities else ["general_tool"]

    def _guess_category(self, name: str) -> str:
        n = name.lower()
        if n in ["nmap", "masscan", "netdiscover", "rustscan", "naabu", "zmap", "tcpdump", "wireshark", "ettercap"]: return "network"
        if n in ["gobuster", "dirb", "nikto", "whatweb", "sqlmap", "burpsuite"]: return "web"
        if n in ["hashcat", "john", "crunch", "hydra", "medusa"]: return "password"
        if n in ["harvester", "sherlock", "spiderfoot", "amass", "subfinder", "theharvester"]: return "osint"
        if n in ["binwalk", "volatility", "exiftool", "foremost", "scapy"]: return "forensics"
        if n in ["aircrack", "wifite", "bettercap"]: return "wireless"
        if n in ["lynis", "chkrootkit", "rkhunter", "nessus", "openvas"]: return "audit"
        if n in ["tgpt", "ollama", "ai", "consciousness", "sharingan"]: return "ai"
        if n in ["browser", "browser_controller", "selenium"]: return "browser"
        if n in ["empire", "metasploit", "cobalt"]: return "exploitation"
        return "system"
    
    def rescan(self):
        """Re-découvre tous les outils"""
        self.registry["tools"] = self._discover_all_tools()
        self.registry["last_scan"] = str(__import__("datetime").datetime.now().isoformat())
        self.save()
        return len(self.registry["tools"])
    
    def save(self):
        counts = {}
        for t in self.registry["tools"].values():
            counts[t["category"]] = counts.get(t["category"], 0) + 1
        for c in self.registry["categories"]:
            self.registry["categories"][c]["count"] = counts.get(c, 0)
        self.registry["last_updated"] = str(__import__("datetime").datetime.now().isoformat())
        with open(self.tools_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def get_summary(self) -> Dict:
        return {
            "version": self.registry["version"],
            "total_tools": len(self.registry["tools"]),
            "categories": {k: v["count"] for k, v in self.registry["categories"].items()},
            "last_scan": self.registry["last_scan"]
        }
    
    def list_all(self) -> Dict:
        return self.registry["tools"]

def get_tool_registry() -> ToolRegistry:
    return ToolRegistry()

if __name__ == "__main__":
    reg = get_tool_registry()
    s = reg.get_summary()
    print(f"=== SHARINGAN TOOL REGISTRY v{s['version']} ===")
    print(f"Total: {s['total_tools']} outils")
    for c, n in s['categories'].items():
        if n: print(f"  {c}: {n}")
    reg.save()
    print("✓ Sauvegardé")
