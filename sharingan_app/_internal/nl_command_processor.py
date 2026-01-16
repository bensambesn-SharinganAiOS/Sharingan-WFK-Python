#!/usr/bin/env python3
"""
Natural Language Command Processor - SHARINGAN OS Core Interface
Optimal NLP parsing for cybersecurity commands
Uses regex patterns + ML intent classification + fallback AI
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from action_executor import ActionExecutor, ActionType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.nlcp")

# Import ML avec fallback gracieux
try:
    from ml_sklearn_detector import get_ml_detector
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    get_ml_detector = None
    logger.warning("ML dependencies not available - using regex only")


class CommandCategory(Enum):
    NETWORK_SCAN = "network_scan"
    RECONNAISSANCE = "reconnaissance"
    WEB_ATTACK = "web_attack"
    SYSTEM_INFO = "system_info"
    SECURITY_AUDIT = "security_audit"
    GENERAL = "general"
    UNKNOWN = "unknown"


class RiskLevel(Enum):
    SAFE = 1      # Lecture seule, sans modification
    LOW = 2       # Découverte d'informations
    MEDIUM = 3    # Scan actif
    HIGH = 4      # Tests de sécurité actifs
    CRITICAL = 5  # Exploitation, modifications


@dataclass
class ParsedCommand:
    raw_query: str
    category: CommandCategory
    risk_level: RiskLevel
    tool: str
    target: str
    flags: str
    final_command: str
    confidence: float
    requires_confirmation: bool
    warnings: List[str] = field(default_factory=list)
    intent_type: str = "unknown"


@dataclass
class ExecutionResult:
    success: bool
    command: str
    output: str
    errors: str
    execution_time_ms: float
    raw_result: Dict = field(default_factory=dict)


class NaturalLanguageCommandProcessor:
    """
    SHARINGAN OS - Natural Language Command Processor

    Interface principale pour interagir avec le système via langage naturel.

    Caractéristiques:
    - Parsing optimal avec patterns regex multi-niveaux
    - Classification ML pour intent detection
    - Fallback AI (tgpt) pour requêtes complexes
    - Gestion de risques avec confirmation
    - Mode interactif shell

    Exemples d'utilisation:
    - "scan les ports de example.com" → nmap -sV example.com
    - "qui est le owner de google.com" → whois google.com
    - "trouve les failles de ce site" → nikto -h target
    """

    def __init__(self):
        self.action_executor = ActionExecutor()
        self.ml_detector = None
        if ML_AVAILABLE and get_ml_detector:
            try:
                self.ml_detector = get_ml_detector()
            except Exception:
                pass
        self.history: List[ParsedCommand] = []
        self.session_id = None

        # Patterns regex optimisés pour français/anglais
        self._compile_patterns()

    def _compile_patterns(self):
        """Compiler tous les patterns regex pour performance"""

        # Target pattern: domain.com, localhost, or IP address
        target_pattern = r'([a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-z]{2,}|(?:localhost|127\.0\.0\.1|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))'

        # === NETWORK SCANNING ===
        self.scan_patterns = [
            # Français
            (re.compile(r'scan(?:ne)?\s+(?:les\s+)?ports?\s+(?:de|d\'|sur)\s+' + target_pattern, re.I),
             {"tool": "nmap", "flags": "-sV", "risk": RiskLevel.MEDIUM}),
            (re.compile(r'ports?\s+ouverts?\s+(?:de|sur|d\')\s+' + target_pattern, re.I),
             {"tool": "nmap", "flags": "-sV", "risk": RiskLevel.MEDIUM}),
            (re.compile(r'd[eé]couvre(?:r?)?\s+(?:les\s+)?(?:ports?|services?)\s+(?:de\s+)?' + target_pattern, re.I),
             {"tool": "nmap", "flags": "-sV -sC", "risk": RiskLevel.MEDIUM}),
            (re.compile(r'scan(?:ne)?\s+(?:rapide|fast)(?:\s+(?:de|d\'|of)\s+)?' + target_pattern, re.I),
             {"tool": "nmap", "flags": "-F", "risk": RiskLevel.LOW}),
            (re.compile(r'scan(?:ne)?\s+' + target_pattern, re.I),
             {"tool": "nmap", "flags": "-sV", "risk": RiskLevel.MEDIUM}),
            # Anglais
            (re.compile(r'scan\s+ports?\s+(?:of|on)?\s*' + target_pattern, re.I),
             {"tool": "nmap", "flags": "-sV", "risk": RiskLevel.MEDIUM}),
            (re.compile(r'nmap\s+(?:version|version\s+de)', re.I),
             {"tool": "nmap", "flags": "--version", "risk": RiskLevel.SAFE}),
            (re.compile(r'quelle\s+est\s+(?:la\s+)?version\s+(?:de\s+)?nmap', re.I),
             {"tool": "nmap", "flags": "--version", "risk": RiskLevel.SAFE}),
        ]

        # === RECONNAISSANCE ===
        self.recon_patterns = [
            # WHOIS - Français
            (re.compile(r'propri[eé]taire?\s+(?:de|d\'|du)?\s*' + target_pattern, re.I),
             {"tool": "whois", "risk": RiskLevel.SAFE}),
            (re.compile(r'enregistrement\s+(?:de|d\'|du)?\s*' + target_pattern, re.I),
             {"tool": "whois", "risk": RiskLevel.SAFE}),
            (re.compile(r'info(?:rmations?)?\s+(?:sur|de|d\')\s*' + target_pattern, re.I),
             {"tool": "whois", "risk": RiskLevel.SAFE}),
            # WHOIS - Anglais
            (re.compile(r'whois\s+' + target_pattern, re.I),
             {"tool": "whois", "risk": RiskLevel.SAFE}),
            (re.compile(r'owner\s+(?:of)?\s*' + target_pattern, re.I),
             {"tool": "whois", "risk": RiskLevel.SAFE}),
            # DNS
            (re.compile(r'addr(?:esse)?\s+ip\s+(?:de|d\'|of)?\s*' + target_pattern, re.I),
             {"tool": "dig", "risk": RiskLevel.SAFE}),
            (re.compile(r'trouve(?:r)?\s+(?:l[\']?\s+)?ip\s+(?:de|d\'|of)?\s*' + target_pattern, re.I),
             {"tool": "dig", "risk": RiskLevel.SAFE}),
            (re.compile(r'quelle\s+est\s+(?:l[\']?\s+)?ip\s+(?:de|d\'|of)?\s*' + target_pattern, re.I),
             {"tool": "dig", "risk": RiskLevel.SAFE}),
            (re.compile(r'ip\s+(?:de|d\'|of)?\s*' + target_pattern, re.I),
             {"tool": "dig", "risk": RiskLevel.SAFE}),
            (re.compile(r'dig\s+' + target_pattern, re.I),
             {"tool": "dig", "risk": RiskLevel.SAFE}),
            (re.compile(r'dns\s+(?:of|for)?\s*' + target_pattern, re.I),
             {"tool": "dig", "risk": RiskLevel.SAFE}),
            (re.compile(r'r[eé]solve(?:r)?\s*' + target_pattern, re.I),
             {"tool": "dig", "risk": RiskLevel.SAFE}),
        ]

        # === WEB TESTING ===
        self.web_patterns = [
            # Headers HTTP
            (re.compile(r'header(?:s)?\s+(?:http|web|site)?\s*(?:de|d\'|of)?\s*' + target_pattern, re.I),
             {"tool": "curl", "flags": "-sI", "risk": RiskLevel.SAFE}),
            (re.compile(r'curl\s+(?:https?://)?' + target_pattern, re.I),
             {"tool": "curl", "flags": "-sI", "risk": RiskLevel.SAFE}),
            (re.compile(r'test(?:e)?\s+(?:le\s+)?site\s+(?:de|d\'|of)?\s*' + target_pattern, re.I),
             {"tool": "curl", "flags": "-sI", "risk": RiskLevel.SAFE}),
            (re.compile(r'v[eé]rifie(?:r)?\s+(?:le\s+)?(?:site|serveur)\s+(?:de|d\'|of)?\s*' + target_pattern, re.I),
             {"tool": "curl", "flags": "-sI", "risk": RiskLevel.SAFE}),
            # Vulnerability Scan
            (re.compile(r'vuln[eé]rabilit[eés]*\s+(?:de|d\'|du|on|of)?\s*' + target_pattern, re.I),
             {"tool": "nikto", "risk": RiskLevel.HIGH}),
            (re.compile(r'failles?\s+(?:de|d\'|du|on|of)?\s*([a-zA-Z0-9.-]+\.[a-z]{2,})', re.I),
             {"tool": "nikto", "risk": RiskLevel.HIGH}),
            (re.compile(r'nikto\s+(?:https?://)?([a-zA-Z0-9.-]+\.[a-z]{2,})', re.I),
             {"tool": "nikto", "risk": RiskLevel.HIGH}),
             (re.compile(r'scan(?:ne)?\s+(?:le\s+)?site\s+(?:de|d\'|of)?\s*([a-zA-Z0-9.-]+\.[a-z]{2,})', re.I),
              {"tool": "nikto", "risk": RiskLevel.HIGH}),
            # Directory enumeration
            (re.compile(r'gobuster\s+(?:https?://)?([a-zA-Z0-9.-]+\.[a-z]{2,})', re.I),
             {"tool": "gobuster", "risk": RiskLevel.MEDIUM}),
            (re.compile(r'r[eé]pertoires?\s+(?:de|d\'|of)?\s*([a-zA-Z0-9.-]+\.[a-z]{2,})', re.I),
             {"tool": "gobuster", "risk": RiskLevel.MEDIUM}),
            (re.compile(r'scan(?:ne)?\s+(?:les?\s+)?(?:r[eé]pertoires?|directorios?|directories?)\s+(?:de|d\'|of)?\s*' + target_pattern, re.I),
             {"tool": "gobuster", "risk": RiskLevel.MEDIUM}),
            
            # Password/Wordlist generation
            (re.compile(r'crunch\s+(\d+)\s+(\d+)\s+([a-zA-Z0-9]+)', re.I),
             {"tool": "crunch", "risk": RiskLevel.SAFE}),
            (re.compile(r'crunch\s+(\d+)\s+(\d+)', re.I),
             {"tool": "crunch", "flags": "abcdefghijklmnopqrstuvwxyz0123456789", "risk": RiskLevel.SAFE}),
            (re.compile(r'wordlist\s+(\d+)\s*(?:à|a|to|-)\s*(\d+)', re.I),
             {"tool": "crunch", "risk": RiskLevel.SAFE}),
            (re.compile(r'g[eé]n[eè]re?\s+(?:une\s+)?wordlist', re.I),
             {"tool": "crunch", "flags": "8 12", "risk": RiskLevel.SAFE}),
            (re.compile(r'g[eé]n[eè]rateur\s+(?:de\s+)?mot(?:s)?\s+de\s+passe', re.I),
             {"tool": "crunch", "flags": "8 12", "risk": RiskLevel.SAFE}),
            (re.compile(r'cr[eé]e?\s+(?:une\s+)?wordlist', re.I),
             {"tool": "crunch", "flags": "8 12", "risk": RiskLevel.SAFE}),
            (re.compile(r'wordlist', re.I),
             {"tool": "crunch", "flags": "8 12", "risk": RiskLevel.SAFE}),
            
            # Hash identification
            (re.compile(r'hashid\s+version', re.I),
             {"tool": "hashid", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'(?:identify|identifie|quel type).*hash\s+([a-fA-F0-9\$:+/\.]{8,})', re.I),
             {"tool": "hashid", "action": "identify", "risk": RiskLevel.SAFE}),
            (re.compile(r'identify\s+([a-fA-F0-9\$:+/\.]{8,})', re.I),
             {"tool": "hashid", "action": "identify", "risk": RiskLevel.SAFE}),
            (re.compile(r'hashid\s+([a-fA-F0-9\$:+/\.]{8,})', re.I),
             {"tool": "hashid", "action": "identify", "risk": RiskLevel.SAFE}),
            
            # Hashcat
            (re.compile(r'crack(?:er)?\s+([a-fA-F0-9$:+/\.]{8,})', re.I),
             {"tool": "hashcat", "action": "crack", "risk": RiskLevel.HIGH}),
        ]

        # === EXPLOITS ===
        self.exploit_patterns = [
            (re.compile(r'searchsploit\s+([a-zA-Z0-9.-]+)', re.I),
             {"tool": "searchsploit", "risk": RiskLevel.SAFE}),
            (re.compile(r'exploi(?:t|tation)?\s+(?:de|d\'|of)?\s*([a-zA-Z0-9.-]+)', re.I),
             {"tool": "searchsploit", "risk": RiskLevel.SAFE}),
            (re.compile(r'cve\s+([0-9-]+)', re.I),
             {"tool": "searchsploit", "flags": "cve", "risk": RiskLevel.SAFE}),
        ]

        # === SYSTEM INFO ===
        self.system_patterns = [
            (re.compile(r'version\s+(?:de|d\'|du)?\s*(?:mon\s+)?syst[eè]me', re.I),
             {"tool": "uname", "flags": "-a", "risk": RiskLevel.SAFE}),
            (re.compile(r'uname', re.I),
             {"tool": "uname", "flags": "-a", "risk": RiskLevel.SAFE}),
            (re.compile(r'kernel', re.I),
             {"tool": "uname", "flags": "-r", "risk": RiskLevel.SAFE}),
            (re.compile(r'ports?\s+(?:ouvert|ecoute|listening)', re.I),
             {"tool": "netstat", "flags": "-tulpn", "risk": RiskLevel.SAFE}),
        ]

        # === PACKET CAPTURE & ANALYSIS ===
        self.packet_patterns = [
            # tcpdump - Packet sniffer
            (re.compile(r'tcpdump\s+version', re.I),
             {"tool": "tcpdump", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'tcpdump\s+interfaces?', re.I),
             {"tool": "tcpdump", "action": "interfaces", "risk": RiskLevel.SAFE}),
            (re.compile(r'tcpdump\s+capture', re.I),
             {"tool": "tcpdump", "action": "capture", "risk": RiskLevel.MEDIUM}),
            (re.compile(r'capture\s+(\d+)\s+(?:paquet|packets?)(?:\s+(?:sur|on|of)\s+(\w+))?', re.I),
             {"tool": "tcpdump", "action": "capture", "risk": RiskLevel.MEDIUM}),
            (re.compile(r'sniff(?:er)?\s+(?:les?\s+)?paquet', re.I),
             {"tool": "tcpdump", "action": "capture", "risk": RiskLevel.MEDIUM}),
            (re.compile(r'analyse\s+(?:le?\s+)?pcap\s+([a-zA-Z0-9._-]+)', re.I),
             {"tool": "tcpdump", "action": "read_pcap", "risk": RiskLevel.SAFE}),
            (re.compile(r'tcpdump\s+(?:help|aide)', re.I),
             {"tool": "tcpdump", "action": "help", "risk": RiskLevel.SAFE}),
            
            # wireshark/tshark - GUI/CLI analyzer
            (re.compile(r'wireshark\s+version', re.I),
             {"tool": "wireshark", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'wireshark\s+interfaces?', re.I),
             {"tool": "wireshark", "action": "interfaces", "risk": RiskLevel.SAFE}),
            (re.compile(r'wireshark\s+capture', re.I),
             {"tool": "wireshark", "action": "capture", "risk": RiskLevel.MEDIUM}),
            (re.compile(r'analyse.*pcap', re.I),
             {"tool": "wireshark", "action": "analyze", "risk": RiskLevel.SAFE}),
            (re.compile(r'wireshark\s+http\s+(?:requests?\s+)?(?:de|from)\s+([a-zA-Z0-9._-]+)', re.I),
             {"tool": "wireshark", "action": "http_requests", "risk": RiskLevel.SAFE}),
            (re.compile(r'dns\s+(?:queries?|requests?)\s+(?:de|from)\s+([a-zA-Z0-9._-]+)', re.I),
             {"tool": "wireshark", "action": "dns_queries", "risk": RiskLevel.SAFE}),
            (re.compile(r'wireshark\s+(?:help|aide)', re.I),
             {"tool": "wireshark", "action": "help", "risk": RiskLevel.SAFE}),
        ]

        # === KALI TOOLS WRAPPERS ===
        self.kali_patterns = [
            # macchanger
            (re.compile(r'macchanger\s+version', re.I),
             {"tool": "macchanger", "action": "version", "risk": RiskLevel.LOW}),
            (re.compile(r'macchanger\s+(?:help|aide)', re.I),
             {"tool": "macchanger", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'change(?:r)?\s+(?:mon\s+)?adresse\s+mac', re.I),
             {"tool": "macchanger", "action": "random", "risk": RiskLevel.HIGH}),
            
            # strings
            (re.compile(r'strings\s+(?:version|aide|help)', re.I),
             {"tool": "strings", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r"strings\s+([a-zA-Z0-9./_-]+)", re.I),
             {"tool": "strings", "action": "extract", "risk": RiskLevel.SAFE}),
            
            # netcat
            (re.compile(r'netcat\s+version', re.I),
             {"tool": "nc", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'nc\s+(?:--version|version|aide|help)', re.I),
             {"tool": "nc", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'netcat\s+(?:listen|listen on)\s+port\s+(\d+)', re.I),
             {"tool": "nc", "action": "listen", "risk": RiskLevel.MEDIUM}),
            (re.compile(r'scan(?:ne)?\s+les?\s+ports?\s+([a-zA-Z0-9.]+)', re.I),
             {"tool": "nc", "action": "scan", "risk": RiskLevel.LOW}),
            
            # crunch
            (re.compile(r'crunch\s+(?:version|aide|help)', re.I),
             {"tool": "crunch", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'crunch\s+(\d+)\s+(\d+)', re.I),
             {"tool": "crunch", "action": "generate", "risk": RiskLevel.SAFE}),
            (re.compile(r'g[eé]n[eè]re?\s+(?:une?\s+)?wordlist', re.I),
             {"tool": "crunch", "action": "generate", "risk": RiskLevel.SAFE}),
            
            # dirb
            (re.compile(r'dirb\s+(?:version|aide|help)', re.I),
             {"tool": "dirb", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'dirb\s+(?:scan\s+)?(?:https?://)?([a-zA-Z0-9.-]+\.[a-z]{2,})', re.I),
             {"tool": "dirb", "action": "scan", "risk": RiskLevel.MEDIUM}),
            (re.compile(r'scan\s+(?:les?\s+)?repertoires?\s+(?:de|of)\s+([a-zA-Z0-9.-]+\.[a-z]{2,})', re.I),
             {"tool": "dirb", "action": "scan", "risk": RiskLevel.MEDIUM}),
            
            # john
            (re.compile(r'john\s+(?:version|aide|help)', re.I),
             {"tool": "john", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'john\s+(?:--version|version)', re.I),
             {"tool": "john", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'crack(?:er)?\s+(?:le?\s+)?hash\s+([a-zA-Z0-9:]+)', re.I),
             {"tool": "john", "action": "crack", "risk": RiskLevel.HIGH}),
            (re.compile(r'crack\s+(?:this\s+)?hash\s+([a-fA-F0-9]+)', re.I),
             {"tool": "john", "action": "crack", "risk": RiskLevel.HIGH}),
            (re.compile(r'john\s+([a-zA-Z0-9./_-]+)', re.I),
             {"tool": "john", "action": "crack", "risk": RiskLevel.HIGH}),
            
            # hydra
            (re.compile(r'hydra\s+(?:version|aide|help)', re.I),
             {"tool": "hydra", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'hydra\s+--version', re.I),
             {"tool": "hydra", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'hydra\s+(?:protocols?|services?)', re.I),
             {"tool": "hydra", "action": "protocols", "risk": RiskLevel.SAFE}),
            (re.compile(r'test(?:er)?\s+([a-zA-Z0-9.-]+\.[a-z]{2,})\s+(?:with|avec)\s+(\w+)', re.I),
             {"tool": "hydra", "action": "brute", "risk": RiskLevel.CRITICAL}),
            (re.compile(r'test(?:er)?\s+(\w+)\s+(?:de|of|on)\s+([a-zA-Z0-9.-]+\.[a-z]{2,})', re.I),
             {"tool": "hydra", "action": "brute", "risk": RiskLevel.CRITICAL}),
            
            # ettercap
            (re.compile(r'ettercap\s+(?:version|aide|help)', re.I),
             {"tool": "ettercap", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'ettercap\s+--version', re.I),
             {"tool": "ettercap", "action": "version", "risk": RiskLevel.SAFE}),
            
            # hashid
            (re.compile(r'hashid\s+version', re.I),
             {"tool": "hashid", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'hashid\s+(?:version|aide|help)', re.I),
             {"tool": "hashid", "action": "help", "risk": RiskLevel.SAFE}),
            
            # hashcat
            (re.compile(r'hashcat\s+version', re.I),
             {"tool": "hashcat", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'hashcat\s+benchmark', re.I),
             {"tool": "hashcat", "action": "benchmark", "risk": RiskLevel.LOW}),
            (re.compile(r'hashcat\s+(?:aide|help)', re.I),
             {"tool": "hashcat", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'crack(?:er)?\s+([a-fA-F0-9$:+/\.]{8,})', re.I),
             {"tool": "hashcat", "action": "crack", "risk": RiskLevel.HIGH}),
            
            # xxd
            (re.compile(r'xxd\s+version', re.I),
             {"tool": "xxd", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'hex\s*(?:dump|afficher|affiche)\s+(?:de|of)?\s*(\S+)', re.I),
             {"tool": "xxd", "action": "hex_dump", "risk": RiskLevel.SAFE}),
            (re.compile(r'xxd\s+(\S+)', re.I),
             {"tool": "xxd", "action": "hex_dump", "risk": RiskLevel.SAFE}),
            
            # smbmap
            (re.compile(r'smbmap\s+version', re.I),
             {"tool": "smbmap", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'smbmap\s+(?:version|aide|help)', re.I),
             {"tool": "smbmap", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'list\s+(?:shares|partages?)\s+(?:de|of|on)\s+([a-zA-Z0-9.-]+)', re.I),
             {"tool": "smbmap", "action": "list_shares", "risk": RiskLevel.LOW}),
            (re.compile(r'smbmap\s+(-H|--host)\s+([a-zA-Z0-9.-]+)', re.I),
             {"tool": "smbmap", "action": "list_shares", "risk": RiskLevel.LOW}),
            
            # nikto
            (re.compile(r'nikto\s+version', re.I),
             {"tool": "nikto", "action": "version", "risk": RiskLevel.SAFE}),
            
            # gobuster
            (re.compile(r'gobuster\s+version', re.I),
             {"tool": "gobuster", "action": "version", "risk": RiskLevel.SAFE}),
            
            # cewl
            (re.compile(r'cewl\s+version', re.I),
             {"tool": "cewl", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'cewl\s+(?:version|aide|help)', re.I),
             {"tool": "cewl", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'generate\s+(?:wordlist|wordlist)\s+(?:de|from|of)\s+(https?://[^\s]+)', re.I),
             {"tool": "cewl", "action": "wordlist", "risk": RiskLevel.SAFE}),
            (re.compile(r'wordlist\s+(?:de|from|of)\s+(https?://[^\s]+)', re.I),
             {"tool": "cewl", "action": "wordlist", "risk": RiskLevel.SAFE}),
            
            # rpcclient
            (re.compile(r'rpcclient\s+version', re.I),
             {"tool": "rpcclient", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'rpcclient\s+(?:version|aide|help)', re.I),
             {"tool": "rpcclient", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'enum\s+(?:domains|domaines)\s+(?:de|of|on)\s+([a-zA-Z0-9.-]+)', re.I),
             {"tool": "rpcclient", "action": "enum_domains", "risk": RiskLevel.LOW}),
            (re.compile(r'enum\s+(?:users|utilisateurs)\s+(?:de|of|on)\s+([a-zA-Z0-9.-]+)', re.I),
             {"tool": "rpcclient", "action": "enum_users", "risk": RiskLevel.LOW}),
            (re.compile(r'enum\s+(?:shares|partages)\s+(?:de|of|on)\s+([a-zA-Z0-9.-]+)', re.I),
             {"tool": "rpcclient", "action": "enum_shares", "risk": RiskLevel.LOW}),

            # strace
            (re.compile(r'strace\s+version', re.I),
             {"tool": "strace", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'strace\s+(?:version|aide|help)', re.I),
             {"tool": "strace", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'trace\s+(?:the\s+)?program\s+(\S+)', re.I),
             {"tool": "strace", "action": "trace", "risk": RiskLevel.LOW}),
            (re.compile(r'strace\s+(\S+)', re.I),
             {"tool": "strace", "action": "trace", "risk": RiskLevel.LOW}),

            # sqlmap
            (re.compile(r'sqlmap\s+version', re.I),
             {"tool": "sqlmap", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'sqlmap\s+(?:version|aide|help)', re.I),
             {"tool": "sqlmap", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'(?:scan|test)\s+(?:sql\s+injection\s+)?(?:on\s+|of\s+)?(https?://[^\s]+)', re.I),
             {"tool": "sqlmap", "action": "scan", "risk": RiskLevel.HIGH}),
            (re.compile(r'sqlmap\s+(https?://[^\s]+)', re.I),
             {"tool": "sqlmap", "action": "scan", "risk": RiskLevel.HIGH}),
            (re.compile(r'enumerate\s+(?:databases?|bases?)\s+(?:of\s+|on\s+)?(https?://[^\s]+)', re.I),
             {"tool": "sqlmap", "action": "databases", "risk": RiskLevel.HIGH}),

            # netdiscover
            (re.compile(r'netdiscover\s+version', re.I),
             {"tool": "netdiscover", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'netdiscover\s+(?:version|aide|help)', re.I),
             {"tool": "netdiscover", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'scan\s+(?:network|réseau)\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})', re.I),
             {"tool": "netdiscover", "action": "scan", "risk": RiskLevel.LOW}),
            (re.compile(r'netdiscover\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})', re.I),
             {"tool": "netdiscover", "action": "scan", "risk": RiskLevel.LOW}),
            (re.compile(r'passive\s+(?:scan|discovery)', re.I),
             {"tool": "netdiscover", "action": "passive", "risk": RiskLevel.SAFE}),

            # dnsrecon
            (re.compile(r'dnsrecon\s+version', re.I),
             {"tool": "dnsrecon", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'dnsrecon\s+(?:version|aide|help)', re.I),
             {"tool": "dnsrecon", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'dnsrecon\s+(?:enumerate|scan)\s+([a-zA-Z0-9.-]+\.[a-z]{2,})', re.I),
             {"tool": "dnsrecon", "action": "enumerate", "risk": RiskLevel.LOW}),
            (re.compile(r'dnsrecon\s+([a-zA-Z0-9.-]+\.[a-z]{2,})', re.I),
             {"tool": "dnsrecon", "action": "enumerate", "risk": RiskLevel.LOW}),
            (re.compile(r'zone\s+transfer\s+(?:of\s+|on\s+)?([a-zA-Z0-9.-]+\.[a-z]{2,})', re.I),
             {"tool": "dnsrecon", "action": "zone_transfer", "risk": RiskLevel.LOW}),

            # ncat
            (re.compile(r'ncat\s+version', re.I),
             {"tool": "ncat", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'ncat\s+(?:version|aide|help)', re.I),
             {"tool": "ncat", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'listen\s+(?:on\s+)?port\s+(\d+)', re.I),
             {"tool": "ncat", "action": "listen", "risk": RiskLevel.MEDIUM}),
            (re.compile(r'connect\s+(?:to\s+)?([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(?:port\s+)?(\d+)', re.I),
             {"tool": "ncat", "action": "connect", "risk": RiskLevel.LOW}),
            (re.compile(r'scan\s+ports?\s+(?:of\s+|on\s+)?([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', re.I),
             {"tool": "ncat", "action": "scan", "risk": RiskLevel.LOW}),

            # fping
            (re.compile(r'fping\s+version', re.I),
             {"tool": "fping", "action": "version", "risk": RiskLevel.SAFE}),
            (re.compile(r'fping\s+(?:version|aide|help)', re.I),
             {"tool": "fping", "action": "help", "risk": RiskLevel.SAFE}),
            (re.compile(r'fping\s+(?:scan|discover)\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})', re.I),
             {"tool": "fping", "action": "scan", "risk": RiskLevel.LOW}),
            (re.compile(r'fping\s+ping\s+([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', re.I),
             {"tool": "fping", "action": "ping", "risk": RiskLevel.SAFE}),
            
            # ping (fping)
            (re.compile(r'^ping\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$', re.I),
             {"tool": "fping", "action": "ping", "risk": RiskLevel.SAFE}),
            
            # macchanger
            (re.compile(r'macchanger\s+version', re.I),
             {"tool": "macchanger", "action": "version", "risk": RiskLevel.LOW}),
            (re.compile(r'macchanger\s+(?:help|aide|random)', re.I),
             {"tool": "macchanger", "action": "random", "risk": RiskLevel.HIGH}),
            (re.compile(r'change(?:r)?\s+(?:my\s+)?mac\s*(?:address)?', re.I),
             {"tool": "macchanger", "action": "random", "risk": RiskLevel.HIGH}),
        ]

    def parse(self, query: str) -> ParsedCommand:
        """
        Parser une requête en langage naturel en commande exécutable

        Returns:
            ParsedCommand avec tous les détails
        """
        query_clean = query.strip()
        query_lower = query_clean.lower()

        warnings = []
        category = CommandCategory.UNKNOWN
        risk_level = RiskLevel.SAFE
        tool = "echo"
        target = "unknown"
        flags = ""
        confidence = 0.0
        requires_confirmation = False
        intent_type = "unknown"

        # === 1. ML Intent Classification ===
        intent_type = "unknown"
        confidence_ml = 0.0
        if self.ml_detector and hasattr(self.ml_detector, 'is_trained') and self.ml_detector.is_trained:
            try:
                ml_result = self.ml_detector.process_query(query_clean)
                intent_type = ml_result.intent_type or "unknown"
                confidence_ml = ml_result.confidence
                warnings.extend(ml_result.warnings)
            except Exception:
                pass

        # === 2. Regex Pattern Matching ===
        matched = False

        # Network Scanning
        for pattern, config in self.scan_patterns:
            match = pattern.search(query_lower)
            if match:
                category = CommandCategory.NETWORK_SCAN
                tool = config["tool"]
                flags = config.get("flags", "-sV")
                risk_level = config["risk"]
                target = match.group(1) if match.groups() else "unknown"
                confidence = 0.95
                matched = True
                break

        if not matched:
            for pattern, config in self.recon_patterns:
                match = pattern.search(query_lower)
                if match:
                    category = CommandCategory.RECONNAISSANCE
                    tool = config["tool"]
                    risk_level = config["risk"]
                    target = match.group(1) if match.groups() else "unknown"
                    confidence = 0.95
                    matched = True
                    break

        if not matched:
            for pattern, config in self.packet_patterns:
                match = pattern.search(query_lower)
                if match:
                    category = CommandCategory.NETWORK_SCAN
                    tool = config["tool"]
                    action = config.get("action", "capture")
                    risk_level = config["risk"]
                    target = match.group(1) if match.groups() else "unknown"
                    confidence = 0.95
                    matched = True
                    flags = f"--action {action}"
                    break

        if not matched:
            for pattern, config in self.kali_patterns:
                match = pattern.search(query_lower)
                if match:
                    category = CommandCategory.SECURITY_AUDIT
                    tool = config["tool"]
                    action = config.get("action", "help")
                    risk_level = config["risk"]
                    target = match.group(1) if match.groups() else "unknown"
                    confidence = 0.95
                    matched = True
                    flags = f"--action {action}"
                    break

        if not matched:
            for pattern, config in self.web_patterns:
                match = pattern.search(query_lower)
                if match:
                    category = CommandCategory.WEB_ATTACK
                    tool = config["tool"]
                    flags = config.get("flags", "")
                    risk_level = config["risk"]
                    target = match.group(1) if match.groups() else "unknown"
                    confidence = 0.95
                    matched = True
                    break

        if not matched:
            for pattern, config in self.exploit_patterns:
                match = pattern.search(query_lower)
                if match:
                    category = CommandCategory.SECURITY_AUDIT
                    tool = config["tool"]
                    flags = config.get("flags", "")
                    risk_level = config["risk"]
                    target = match.group(1) if match.groups() else "unknown"
                    confidence = 0.95
                    matched = True
                    break

        if not matched:
            for pattern, config in self.system_patterns:
                match = pattern.search(query_lower)
                if match:
                    category = CommandCategory.SYSTEM_INFO
                    tool = config["tool"]
                    flags = config.get("flags", "")
                    risk_level = config["risk"]
                    target = "localhost"
                    confidence = 0.90
                    matched = True
                    break

        # === 3. Fallback AI pour requêtes non reconnues ===
        if not matched:
            category = CommandCategory.GENERAL
            confidence = 0.3
            warnings.append("Commande non reconnue - exécution basique")

            # Essayer de deviner l'URL
            url_match = re.search(r'(https?://[^\s]+|[a-zA-Z0-9.-]+\.[a-z]{2,})', query_lower)
            if url_match:
                target = url_match.group(1)
                if not target.startswith("http"):
                    target = f"http://{target}"
                tool = "curl"
                flags = "-sI"
                confidence = 0.5

        # === 4. Construire la commande finale ===
        if tool == "nmap":
            if flags == "--version":
                final_command = "nmap --version"
            else:
                final_command = f"nmap {flags} {target}"
        elif tool == "whois":
            final_command = f"whois {target}"
        elif tool == "dig":
            final_command = f"dig {target}"
        elif tool == "curl":
            final_command = f"curl {flags} {target}"
        elif tool == "searchsploit":
            final_command = f"searchsploit {target}"
        elif tool == "uname":
            final_command = f"uname {flags}"
        elif tool == "netstat":
            final_command = f"netstat {flags}"
        elif tool in ["tcpdump", "wireshark"]:
            action_match = re.search(r'--action\s+(\w+)', flags)
            action = action_match.group(1) if action_match else "capture"
            final_command = f"python3 -m sharingan_app._internal.kali_{tool}_wrapper {action}"
            if target and target != "unknown":
                final_command += f" {target}"
        elif tool in ["macchanger", "strings", "nc", "crunch", "dirb", "john", "hydra", "ettercap",
                      "hashid", "hashcat", "nikto", "gobuster", "xxd", "smbmap", "cewl", "rpcclient", "strace",
                      "sqlmap", "netdiscover", "dnsrecon", "ncat", "fping"]:
            action_match = re.search(r'--action\s+(\w+)', flags)
            action = action_match.group(1) if action_match else "help"
            final_command = f"python3 -m sharingan_app._internal.kali_{tool}_wrapper {action}"
            if target and target != "unknown":
                final_command += f" {target}"
        else:
            final_command = f"echo '{query_clean}'"

        # === 5. Déterminer si confirmation requise ===
        requires_confirmation = risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]

        # === 6. Ajouter avertissements selon le risque ===
        if risk_level == RiskLevel.HIGH:
            warnings.append(f"Risque ÉLEVÉ: {tool} est un outil de test de sécurité")
            warnings.append("Assurez-vous d'avoir l'autorisation appropriée")
        elif risk_level == RiskLevel.MEDIUM:
            warnings.append(f"Risque MOYEN: {tool} effectue un scan actif")

        parsed = ParsedCommand(
            raw_query=query_clean,
            category=category,
            risk_level=risk_level,
            tool=tool,
            target=target,
            flags=flags,
            final_command=final_command,
            confidence=confidence,
            requires_confirmation=requires_confirmation,
            warnings=warnings,
            intent_type=intent_type
        )

        self.history.append(parsed)
        return parsed

    def execute(self, query: str, auto_confirm: bool = False) -> Dict[str, Any]:
        """
        Parser et exécuter une commande en langage naturel

        Args:
            query: Requête en langage naturel
            auto_confirm: Skip confirmation pour les commandes dangereuses

        Returns:
            Dict avec résultats complets
        """
        import time
        start_time = time.time()

        # Parser la requête
        parsed = self.parse(query)

        result = {
            "query": query,
            "parsed": {
                "category": parsed.category.value,
                "tool": parsed.tool,
                "target": parsed.target,
                "command": parsed.final_command,
                "confidence": parsed.confidence,
                "risk": parsed.risk_level.name,
                "intent": parsed.intent_type,
                "warnings": parsed.warnings
            },
            "execution": None,
            "success": False,
            "requires_confirmation": parsed.requires_confirmation,
            "execution_time_ms": 0
        }

        # Vérifier confirmation
        if parsed.requires_confirmation and not auto_confirm:
            result["status"] = "CONFIRMATION_REQUIRED"
            result["message"] = f"Commande risquée détectée: {parsed.final_command}"
            return result

        # Exécuter la commande
        try:
            exec_result = self.action_executor.execute_action(parsed.final_command, "nlcp")

            result["execution"] = {
                "success": exec_result.get("success", False),
                "output": exec_result.get("output", "")[:5000],
                "return_code": exec_result.get("return_code", -1)
            }
            result["success"] = exec_result.get("success", False)
            result["errors"] = exec_result.get("error", "")

        except Exception as e:
            result["errors"] = str(e)
            result["success"] = False

        result["execution_time_ms"] = (time.time() - start_time) * 1000

        return result

    def explain(self, query: str) -> str:
        """Expliquer ce qu'une commande va faire"""
        parsed = self.parse(query)

        risk_icons = {
            RiskLevel.SAFE: "🟢",
            RiskLevel.LOW: "🟡",
            RiskLevel.MEDIUM: "🟠",
            RiskLevel.HIGH: "🔴",
            RiskLevel.CRITICAL: "💀"
        }

        lines = [
            f"🌐 Query: {query}",
            f"",
            f"📋 Analyse:",
            f"   Commande: {parsed.final_command}",
            f"   Cible: {parsed.target}",
            f"   Outil: {parsed.tool}",
            f"   Catégorie: {parsed.category.value}",
            f"   Risque: {risk_icons[parsed.risk_level]} {parsed.risk_level.name}",
            f"   Confiance: {parsed.confidence:.0%}",
        ]

        if parsed.warnings:
            lines.append("")
            lines.append(f"⚠️  Avertissements:")
            for w in parsed.warnings:
                lines.append(f"   - {w}")

        if parsed.requires_confirmation:
            lines.append("")
            lines.append(f"❓ Confirmation requise pour cette commande risquée")

        return "\n".join(lines)

    def interactive_shell(self):
        """Lancer un shell interactif en langage naturel"""
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║     SHARINGAN OS - Natural Language Command Shell                ║
║                                                                   ║
║  Tapez vos commandes en langage naturel.                         ║
║  Exemples:                                                       ║
║    - "scan les ports de example.com"                             ║
║    - "qui est le propriétaire de google.com"                     ║
║    - "trouve l'IP de yahoo.com"                                  ║
║    - "affiche les headers de example.com"                        ║
║                                                                   ║
║  Commandes spéciales:                                            ║
║    /explain <query> - Expliquer sans exécuter                    ║
║    /history       - Historique des commandes                     ║
║    /exit          - Quitter                                      ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
        """)

        while True:
            try:
                query = input("🌐_sharingan> ").strip()

                if not query:
                    continue

                if query.lower() in ["/exit", "/quit", "exit", "quit"]:
                    print("\n👋 Au revoir!")
                    break

                if query.startswith("/"):
                    if query.startswith("/explain"):
                        explanation = self.explain(query[9:].strip())
                        print(f"\n{explanation}\n")
                    elif query == "/history":
                        print("\n📜 Historique:")
                        for i, cmd in enumerate(self.history[-10:], 1):
                            print(f"  {i}. [{cmd.category.value}] {cmd.final_command}")
                        print()
                    else:
                        print(f"Commande inconnue: {query}")
                    continue

                # Exécuter la commande
                result = self.execute(query)

                print(f"\n📋 Commande: {result['parsed']['command']}")
                print(f"   Cible: {result['parsed']['target']}")
                print(f"   Confiance: {result['parsed']['confidence']:.0%}")

                if result.get('requires_confirmation'):
                    print(f"\n⚠️  Cette commande nécessite une confirmation")
                    confirm = input("   Exécuter quand même? (oui/non): ").strip().lower()
                    if confirm in ["oui", "yes", "o", "y"]:
                        result = self.execute(query, auto_confirm=True)
                    else:
                        print("   Commande annulée")
                        continue

                if result.get('success'):
                    print(f"\n✅ Succès ({result['execution_time_ms']:.0f}ms)")
                    output = result.get('execution', {}).get('output', '')
                    for line in output.split('\n')[:20]:
                        print(f"   {line}")
                    if len(output.split('\n')) > 20:
                        print(f"   ... (tronqué)")
                else:
                    print(f"\n❌ Échec")
                    if result.get('errors'):
                        print(f"   Erreur: {result['errors']}")

                print()

            except KeyboardInterrupt:
                print("\n👋 Au revoir!")
                break
            except Exception as e:
                print(f"\n💥 Erreur: {e}\n")


def get_nl_processor() -> NaturalLanguageCommandProcessor:
    """Obtenir le processeur NLP singleton"""
    return NaturalLanguageCommandProcessor()


if __name__ == "__main__":
    processor = get_nl_processor()

    # Test rapide
    test_queries = [
        "scan les ports de example.com",
        "qui est le propriétaire de google.com",
        "trouve l'IP de yahoo.com",
        "affiche les headers HTTP de example.com",
        "quel est la version de ton système",
        "trouve les failles de ce site"
    ]

    print("="*70)
    print("🧪 SHARINGAN NLP Processor - Test")
    print("="*70)

    for query in test_queries:
        print(f"\n📝 Query: {query}")
        result = processor.execute(query)
        print(f"   Command: {result['parsed']['command']}")
        print(f"   Target: {result['parsed']['target']}")
        print(f"   Risk: {result['parsed']['risk']}")
        print(f"   Success: {result['success']}")

    print("\n" + "="*70)
    print("Pour lancer le shell interactif: python3 -m nl_command_processor --shell")
    print("="*70)
