#!/usr/bin/env python3
"""
Sharingan OS - Auto-Détection des Outils
==========================================
Détection dynamique de tous les outils disponibles sur le système
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger("sharingan.tool_detector")


@dataclass
class DetectedTool:
    """Outil détecté sur le système"""
    name: str
    path: str
    category: str
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    installed: bool = True
    error: str = ""


class ToolAutoDetector:
    """
    Détection automatique de tous les outils disponibles sur le système
    """
    
    # Catégories d'outils avec leurs noms possibles
    TOOL_CATEGORIES = {
        "network_scanner": [
            "nmap", "masscan", "netdiscover", "arp-scan", "netcat", "nc",
            "fping", "hping3", "nbtscan", "rustscan"
        ],
        "web_scanner": [
            "gobuster", "dirsearch", "dirb", "wfuzz", "ffuf", "nikto",
            "whatweb", "wafw00f", "dalfox", "gf"
        ],
        "vulnerability_scanner": [
            "openvas", "nessus", "nexpose", "nikto", "wpscan",
            "joomscan", "droopescan", "cmsmap", "testlink"
        ],
        "exploitation": [
            "msfconsole", "msfvenom", "searchsploit", "metasploit",
            "exploitdb", "sqlmap", "commix", "jboss-autopwn"
        ],
        "password_cracking": [
            "hydra", "john", "hashcat", "crunch", "cewl",
            "hashidentifier", "johnny", "ophcrack"
        ],
        "wifi": [
            "aircrack-ng", "airmon-ng", "airodump-ng", "aireplay-ng",
            "kismet", "wifite", "fern-wifi-cracker"
        ],
        "forensic": [
            "volatility", "autopsy", "binwalk", "foremost",
            "scalpel", "bulk_extractor", "yara"
        ],
        "recon": [
            "theharvester", "maltego", "recon-ng", "dnsrecon",
            "whois", "dig", "nslookup", "host"
        ],
        "reverse_engineering": [
            "radare2", "ghidra", "objdump", "nm", "strace",
            "ltrace", "hopper", "ida"
        ],
        "social_engineering": [
            "setoolkit", "gophish", "king-phisher", "social-engineer-toolkit"
        ],
        "reporting": [
            "dradis", "faraday", "pwndoc", "cherrytree"
        ],
        "ai_ml": [
            "tgpt", "grok-code-fast", "minimax", "ollama",
            "lm-studio", "llama", "chatgpt"
        ],
        "system": [
            "python", "python3", "pip", "pip3", "git", "apt",
            "curl", "wget", "hostname", "uname", "whoami",
            "bash", "sh", "sudo"
        ],
        "utils": [
            "jq", "yq", "tmux", "vim", "nano", "grep", "awk",
            "sed", "find", "xargs", "sort", "uniq", "cut"
        ]
    }
    
    def __init__(self):
        self.detected_tools: Dict[str, DetectedTool] = {}
        self.scan_time: Optional[datetime] = None
        self.categories_found: List[str] = []
    
    def _get_tool_path(self, tool_name: str) -> Optional[str]:
        """Récupérer le chemin d'un outil avec shutil.which"""
        return shutil.which(tool_name)
    
    def _get_tool_description(self, tool_name: str, category: str) -> str:
        """Obtenir une description pour un outil"""
        descriptions = {
            "nmap": "Network Mapper - Scanner de ports et services",
            "masscan": "Mass IP/Port Scanner - Scanner haute vitesse",
            "netdiscover": "Network Discovery - Découverte de réseau",
            "gobuster": "Directory/File Scanner - Énumération web",
            "sqlmap": "SQL Injection Tool - Injection SQL automatique",
            "nikto": "Web Server Scanner - Scanner de vulnérabilités web",
            "hydra": "Password Cracker - Cassage de mots de passe",
            "john": "John the Ripper - Cassage de mots de passe",
            "hashcat": "Password Recovery - Récupération de mots de passe",
            "searchsploit": "Exploit Database - Base de données d'exploits",
            "aircrack-ng": "WiFi Security - Outils de sécurité WiFi",
            "volatility": "Memory Forensics - Analyse de mémoire",
            "theharvester": "OSINT Tool - Reconnaissance emails/sous-domaines",
            "gobuster": "Directory Buster - Force brute de répertoires",
            "tgpt": "AI Assistant - Assistant IA basé sur Grok",
            "msfconsole": "Metasploit Framework - Framework d'exploitation",
            "git": "Version Control - Contrôle de version",
            "python": "Python Interpreter - Langage de programmation",
            "pip": "Python Package Manager - Gestionnaire de paquets Python",
        }
        return descriptions.get(tool_name, f"{tool_name.capitalize()} - Outil de sécurité")
    
    def _get_tool_capabilities(self, tool_name: str, category: str) -> List[str]:
        """Obtenir les capacités d'un outil"""
        capabilities_map = {
            "nmap": ["port_scan", "service_detection", "os_detection", "script_scan", "network_map"],
            "masscan": ["fast_scan", "port_scan", "rate_limit"],
            "gobuster": ["dir_scan", "vhost_scan", "dns_scan", "fuzzing"],
            "sqlmap": ["sql_injection", "database_dump", "os_shell", "file_read"],
            "nikto": ["web_scan", "vuln_scan", "header_analysis"],
            "hydra": ["brute_force", "ssh", "ftp", "http", "smb", "telnet"],
            "john": ["hash_cracking", "password_recovery", "rule_based"],
            "searchsploit": ["exploit_search", "cve_lookup", "path_disclosure"],
            "theharvester": ["email_harvest", "subdomain_enum", "host_enum"],
            "aircrack-ng": ["wifi_crack", "handshake_capture", "monitor_mode"],
            "volatility": ["memory_dump", "process_analysis", "malware_detection"],
            "tgpt": ["ai_chat", "code_generation", "reasoning"],
            "msfconsole": ["exploit", "payload", "post_exploitation", "auxiliary"],
            "git": ["clone", "init", "commit", "push", "pull"],
            "python": ["script_execution", "package_install", "development"],
        }
        return capabilities_map.get(tool_name, [f"{category}_tool"])
    
    def _get_tool_category(self, tool_name: str) -> str:
        """Déterminer la catégorie d'un outil"""
        for category, tools in self.TOOL_CATEGORIES.items():
            if tool_name in tools:
                return category
        return "unknown"
    
    def detect_tool(self, tool_name: str) -> DetectedTool:
        """Détecter un outil spécifique"""
        path = self._get_tool_path(tool_name)
        category = self._get_tool_category(tool_name)
        
        if path:
            return DetectedTool(
                name=tool_name,
                path=path,
                category=category,
                description=self._get_tool_description(tool_name, category),
                capabilities=self._get_tool_capabilities(tool_name, category),
                installed=True
            )
        else:
            return DetectedTool(
                name=tool_name,
                path="",
                category=category,
                description=self._get_tool_description(tool_name, category),
                installed=False,
                error="Outil non trouvé sur le système"
            )
    
    def scan_category(self, category: str, tools: List[str]) -> Dict[str, DetectedTool]:
        """Scanner une catégorie d'outils"""
        results = {}
        for tool in tools:
            detected = self.detect_tool(tool)
            results[tool] = detected
            if detected.installed and category not in self.categories_found:
                self.categories_found.append(category)
        return results
    
    def scan_all(self) -> Dict[str, DetectedTool]:
        """Scanner tous les outils de sécurité"""
        self.detected_tools = {}
        self.categories_found = []
        
        for category, tools in self.TOOL_CATEGORIES.items():
            category_tools = self.scan_category(category, tools)
            self.detected_tools.update(category_tools)
        
        self.scan_time = datetime.now()
        
        # Log résultats
        installed_count = sum(1 for t in self.detected_tools.values() if t.installed)
        logger.info(f"Outils détectés: {installed_count}/{len(self.detected_tools)}")
        logger.info(f"Catégories: {', '.join(self.categories_found)}")
        
        return self.detected_tools
    
    def get_installed_tools(self) -> Dict[str, DetectedTool]:
        """Récupérer uniquement les outils installés"""
        return {name: tool for name, tool in self.detected_tools.items() 
                if tool.installed}
    
    def get_by_category(self, category: str) -> Dict[str, DetectedTool]:
        """Récupérer les outils d'une catégorie"""
        return {name: tool for name, tool in self.detected_tools.items() 
                if tool.category == category and tool.installed}
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtenir un résumé de la détection"""
        installed = self.get_installed_tools()
        
        by_category = {}
        for tool in installed.values():
            if tool.category not in by_category:
                by_category[tool.category] = []
            by_category[tool.category].append(tool.name)
        
        return {
            "scan_time": self.scan_time.isoformat() if self.scan_time else None,
            "total_scanned": len(self.detected_tools),
            "total_installed": len(installed),
            "categories_found": self.categories_found,
            "tools_by_category": by_category,
            "not_installed": [name for name, tool in self.detected_tools.items() 
                             if not tool.installed]
        }
    
    def to_json(self) -> str:
        """Exporter en JSON"""
        import json
        data = {
            "scan_time": self.scan_time.isoformat() if self.scan_time else None,
            "tools": {
                name: {
                    "name": tool.name,
                    "path": tool.path,
                    "category": tool.category,
                    "description": tool.description,
                    "capabilities": tool.capabilities,
                    "installed": tool.installed
                }
                for name, tool in self.detected_tools.items()
            }
        }
        return json.dumps(data, indent=2)
    
    def print_report(self):
        """Imprimer un rapport de détection"""
        summary = self.get_summary()
        installed = self.get_installed_tools()
        
        print("\n" + "="*60)
        print("       RAPPORT DE DÉTECTION D'OUTILS")
        print("="*60)
        print(f"\n📅 Scan du: {summary['scan_time']}")
        print(f"✅ Outils installés: {summary['total_installed']}/{summary['total_scanned']}")
        print(f"📂 Catégories: {', '.join(summary['categories_found'])}")
        
        print("\n" + "-"*60)
        print("OUTILS INSTALLÉS PAR CATÉGORIE:")
        print("-"*60)
        
        for category, tools in sorted(summary['tools_by_category'].items()):
            icon = self._get_category_icon(category)
            print(f"\n{icon} {category.upper().replace('_', ' ')} ({len(tools)})")
            for tool in sorted(tools):
                path = self.detected_tools[tool].path
                print(f"   • {tool}: {path}")
        
        if summary['not_installed']:
            print("\n" + "-"*60)
            print("OUTILS NON INSTALLÉS:")
            print("-"*60)
            for tool in sorted(summary['not_installed']):
                print(f"   • {tool}")
        
        print("\n" + "="*60)
    
    def _get_category_icon(self, category: str) -> str:
        """Icône pour chaque catégorie"""
        icons = {
            "network_scanner": "🌐",
            "web_scanner": "🕸️",
            "vulnerability_scanner": "🔍",
            "exploitation": "💥",
            "password_cracking": "🔓",
            "wifi": "📶",
            "forensic": "🔎",
            "recon": "🎯",
            "reverse_engineering": "⚙️",
            "social_engineering": "🎭",
            "reporting": "📊",
            "ai_ml": "🤖",
            "system": "💻",
            "utils": "🛠️",
            "unknown": "❓"
        }
        return icons.get(category, "📦")


# Instance singleton
_detector = None

def get_tool_detector() -> ToolAutoDetector:
    """Obtenir l'instance singleton"""
    global _detector
    if _detector is None:
        _detector = ToolAutoDetector()
    return _detector


def detect_all_tools() -> Dict[str, DetectedTool]:
    """Fonction便捷 pour détecter tous les outils"""
    detector = get_tool_detector()
    return detector.scan_all()


if __name__ == "__main__":
    print("=== DÉTECTION AUTOMATIQUE DES OUTILS ===\n")
    
    detector = get_tool_detector()
    
    # Scanner tous les outils
    print("🔍 Scan en cours...")
    tools = detector.scan_all()
    
    # Afficher le rapport
    detector.print_report()
    
    # Enregistrer les résultats
    print("\n💾 Sauvegarde des résultats...")
    with open("/tmp/detected_tools.json", "w") as f:
        f.write(detector.to_json())
    print("   Fichier: /tmp/detected_tools.json")
