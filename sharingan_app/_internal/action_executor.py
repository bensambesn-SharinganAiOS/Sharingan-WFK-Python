#!/usr/bin/env python3
"""
Action Executor - Bridge Sharingan Soul suggestions to real tool execution
Maps autonomous intentions to concrete actions using available tools
"""

import logging
import subprocess
import json
import shlex
import tempfile
import asyncio
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("sharingan.action_executor")


class ActionType(Enum):
    RECON = "recon"
    EXPLOIT = "exploit"
    SCAN = "scan"
    ENUMERATION = "enumeration"
    ANALYSIS = "analysis"
    REPORT = "report"
    CLEANUP = "cleanup"
    BROWSER = "browser"


@dataclass
class ExecutedAction:
    action_type: str
    command: str
    target: Optional[str]
    result: Any
    success: bool
    output: str


class ActionExecutor:
    """
    Executes actions suggested by Sharingan Soul using available tools
    Bridges autonomous intentions to concrete execution
    """
    
    def __init__(self):
        self.execution_history: List[ExecutedAction] = []
        self.kali_tools = self._initialize_kali_tools()
        # Navigateur partagé entre les actions
        self._browser_controller = None
        self._browser_launched = False
        
    def _initialize_kali_tools(self) -> Dict[str, Dict]:
        """Initialize available Kali tools"""
        return {
            "nmap": {
                "path": "/usr/bin/nmap",
                "description": "Network scanner",
                "capabilities": ["port_scan", "service_detection", "os_detection"]
            },
            "masscan": {
                "path": "/usr/bin/masscan",
                "description": "High-speed port scanner",
                "capabilities": ["fast_scan", "port_scan"]
            },
            "searchsploit": {
                "path": "/usr/bin/searchsploit",
                "description": "Exploit database search",
                "capabilities": ["exploit_search", "vulnerability_lookup"]
            },
            "gobuster": {
                "path": "/usr/bin/gobuster",
                "description": "Directory/file scanner",
                "capabilities": ["dir_scan", "vhost_scan", "dns_scan"]
            },
            "sqlmap": {
                "path": "/usr/bin/sqlmap",
                "description": "SQL injection scanner",
                "capabilities": ["sql_injection", "database_dump"]
            },
            "nikto": {
                "path": "/usr/bin/nikto",
                "description": "Web server scanner",
                "capabilities": ["web_scan", "vuln_scan"]
            },
            "hydra": {
                "path": "/usr/bin/hydra",
                "description": "Password cracker",
                "capabilities": ["brute_force", "password_attack"]
            },
            "john": {
                "path": "/usr/bin/john",
                "description": "Password cracker",
                "capabilities": ["hash_cracking", "password_attack"]
            }
        }
    
    def analyze_action(self, action_text: str) -> tuple[ActionType, str, Dict[str, Any]]:
        """
        Analyze action text to determine type and parameters
        Returns: (action_type, target, parameters)
        """
        action_lower = action_text.lower().strip()
        action_original = action_text.strip()
        
        # NMAP - chercher la cible après les flags
        if action_lower.startswith("nmap"):
            parts = action_original.split()
            target = "localhost"  # défaut
            for i, part in enumerate(parts):
                if i == 0:
                    continue  # skip "nmap"
                if not part.startswith('-'):
                    target = part
                    break
            params = {"tool": "nmap"}
            if "-F" in action_original:
                params["flags"] = "-F"
            return ActionType.SCAN, target, params
        
        # WHOIS
        if action_lower.startswith("whois"):
            parts = action_original.split()
            target = parts[1] if len(parts) > 1 else "unknown"
            return ActionType.RECON, target, {"tool": "whois"}
        
        # DIG
        if action_lower.startswith("dig"):
            parts = action_original.split()
            target = parts[1] if len(parts) > 1 else "unknown"
            return ActionType.RECON, target, {"tool": "dig"}
        
        # CURL
        if action_lower.startswith("curl"):
            parts = action_original.split()
            # Chercher l'URL
            for part in parts:
                if part.startswith("http://") or part.startswith("https://"):
                    target = part.replace("http://", "").replace("https://", "").rstrip('/')
                    return ActionType.ANALYSIS, target, {"tool": "curl"}
            return ActionType.ANALYSIS, "unknown", {"tool": "curl"}
        
        # SEARCHSPLOIT / EXPLOIT
        if "searchsploit" in action_lower or action_lower.startswith("exploit "):
            parts = action_original.split()
            for i, part in enumerate(parts):
                if part in ["searchsploit", "exploit"]:
                    if i + 1 < len(parts):
                        return ActionType.EXPLOIT, parts[i + 1], {"tool": "searchsploit"}
            return ActionType.EXPLOIT, "general", {"tool": "searchsploit"}
        
        # GOBUSTER
        if "gobuster" in action_lower:
            target = "unknown"
            for part in action_original.split():
                if part.startswith("http://") or part.startswith("https://"):
                    target = part.replace("http://", "").replace("https://", "").rstrip('/')
                    break
            return ActionType.ENUMERATION, target, {"tool": "gobuster"}
        
        # ========== NAVIGATEUR - Commandes en langage naturel ==========
        browser_navigation_keywords = ["va sur", "navigue vers", "ouvre", "aller à", "ouvre la page"]
        browser_search_keywords = ["cherche", "recherche sur google", "cherche sur le web"]
        browser_read_keywords = ["lis", "lit la page", "lis l'article", "affiche le contenu"]
        browser_scroll_keywords = ["scroll", "défile", "descends", "monte"]
        browser_click_keywords = ["clic", "clique sur", "click sur"]
        browser_screenshot_keywords = ["capture", "screenshot", "prends une photo"]
        browser_tab_keywords = ["nouvel onglet", "nouveau onglet", "ouvre un nouvel onglet"]
        browser_upload_keywords = ["upload", "télécharge un fichier", "envoie un fichier"]
        browser_js_keywords = ["execute js", "exécute javascript", "javascript"]
        
        import re
        
        # Vérifier chaque catégorie de commande navigateur
        if any(kw in action_lower for kw in browser_navigation_keywords):
            url_match = re.search(r'https?://[^\s]+', action_original)
            url = url_match.group() if url_match else ""
            if url:
                return ActionType.BROWSER, url, {"browser_action": "navigate", "url": url}
            sites = {
                "google": "https://google.com", "youtube": "https://youtube.com",
                "github": "https://github.com", "bbc": "https://www.bbc.com/afrique",
                "facebook": "https://facebook.com", "twitter": "https://twitter.com"
            }
            for site, site_url in sites.items():
                if site in action_lower:
                    return ActionType.BROWSER, site, {"browser_action": "navigate", "url": site_url}
            return ActionType.BROWSER, "google.com", {"browser_action": "navigate", "url": "https://google.com"}
        
        if any(kw in action_lower for kw in browser_search_keywords):
            query = action_original
            for kw in ["cherche", "recherche", "sur google", "sur le web"]:
                query = query.replace(kw, "").strip()
            return ActionType.BROWSER, "search", {"browser_action": "search", "query": query}
        
        if any(kw in action_lower for kw in browser_read_keywords):
            url_match = re.search(r'https?://[^\s]+', action_original)
            url = url_match.group() if url_match else ""
            if url:
                return ActionType.BROWSER, url, {"browser_action": "read", "url": url}
            return ActionType.BROWSER, "current", {"browser_action": "read"}
        
        if any(kw in action_lower for kw in browser_scroll_keywords):
            pixels = 400
            if "haut" in action_lower or "monte" in action_lower:
                pixels = -400
            return ActionType.BROWSER, "page", {"browser_action": "scroll", "pixels": pixels}
        
        if any(kw in action_lower for kw in browser_click_keywords):
            return ActionType.BROWSER, "element", {"browser_action": "click"}
        
        if any(kw in action_lower for kw in browser_screenshot_keywords):
            path = str(Path(tempfile.gettempdir()) / "sharingan_screenshot.png")
            return ActionType.BROWSER, "screenshot", {"browser_action": "screenshot", "path": path}
        
        if any(kw in action_lower for kw in browser_tab_keywords):
            url_match = re.search(r'https?://[^\s]+', action_original)
            url = url_match.group() if url_match else "about:blank"
            return ActionType.BROWSER, url, {"browser_action": "new_tab", "url": url}
        
        if any(kw in action_lower for kw in browser_upload_keywords):
            file_match = re.search(r'/[^\s]+', action_original)
            file_path = file_match.group() if file_match else str(Path(tempfile.gettempdir()) / "test_image.jpg")
            return ActionType.BROWSER, "upload", {"browser_action": "upload", "file_path": file_path}
        
        if any(kw in action_lower for kw in browser_js_keywords):
            js_code = action_original
            for kw in ["execute", "exécute", "javascript", "js"]:
                js_code = js_code.replace(kw, "").strip()
            return ActionType.BROWSER, "js", {"browser_action": "execute_js", "script": js_code}
        
        # Fallback par analyse du contenu
        import re
        hostname_match = re.search(r'([a-zA-Z0-9.-]+\.[a-z]{2,})', action_original)
        target = hostname_match.group() if hostname_match else "unknown"
        
        return ActionType.ANALYSIS, target, {"original_cmd": action_original}
    
    def _extract_target(self, action_text: str) -> str:
        """
        Extract target hostname/IP from action text
        Handles formats like: 'nmap localhost', 'scan 192.168.1.1', 'whois example.com'
        """
        import re
        
        # Si la commande contient directement l'outil au début, extraire l'argument suivant
        if action_text.startswith("nmap "):
            parts = action_text.split()
            if len(parts) >= 2:
                return parts[1]
        elif action_text.startswith("whois "):
            parts = action_text.split()
            if len(parts) >= 2:
                return parts[1]
        elif action_text.startswith("dig "):
            parts = action_text.split()
            if len(parts) >= 2:
                return parts[1]
        elif action_text.startswith("searchsploit "):
            parts = action_text.split()
            if len(parts) >= 2:
                return parts[1]
        elif action_text.startswith("gobuster "):
            parts = action_text.split()
            for i, part in enumerate(parts):
                if part in ["-u", "--url"]:
                    if i + 1 < len(parts):
                        url = parts[i + 1]
                        return url.replace("http://", "").replace("https://", "").rstrip('/')
            return parts[-1] if parts else "unknown"
        
        # Sinon chercher un hostname ou IP dans le texte
        hostname_match = re.search(r'([a-zA-Z0-9.-]+\.[a-z]{2,}|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', action_text)
        if hostname_match:
            return hostname_match.group()
        
        return "localhost"
    
    def execute_action(self, action_text: str, motivation: str = "unknown") -> Dict[str, Any]:
        """
        Execute a single action based on the action text
        Returns execution result
        """
        action_type, target, params = self.analyze_action(action_text)
        
        logger.info(f"Executing action: {action_text}")
        logger.info(f"Action type: {action_type}, Target: {target}")
        
        if action_type == ActionType.SCAN:
            return self._execute_scan(target, params)
        elif action_type == ActionType.RECON:
            return self._execute_recon(target, params)
        elif action_type == ActionType.EXPLOIT:
            return self._execute_exploit(target, params)
        elif action_type == ActionType.ENUMERATION:
            return self._execute_enumeration(target, params)
        elif action_type == ActionType.BROWSER:
            return self._execute_browser(target, params)
        else:
            return self._execute_analysis(target, params)
    
    def _execute_scan(self, target: str, params: Dict) -> Dict[str, Any]:
        """Execute port scanning"""
        tool = params.get("tool", "nmap")
        flags = params.get("flags", "-sV -sC")
        
        if tool == "nmap":
            cmd = f"nmap {flags} {target}"
        elif tool == "masscan":
            cmd = f"masscan {flags} {target} -p0-65535"
        else:
            cmd = f"nmap {target}"
        
        return self._run_command(cmd, "scan", target)
    
    def _execute_recon(self, target: str, params: Dict) -> Dict[str, Any]:
        """Execute reconnaissance"""
        tool = params.get("tool", "whois")
        
        if tool == "whois":
            cmd = f"whois {target}"
        elif tool == "dig":
            cmd = f"dig {target}"
        else:
            cmd = f"whois {target}"
        
        return self._run_command(cmd, "recon", target)
    
    def _execute_exploit(self, target: str, params: Dict) -> Dict[str, Any]:
        """Execute exploit/vulnerability search"""
        tool = params.get("tool", "searchsploit")
        
        if tool == "searchsploit":
            cmd = f"searchsploit {target}"
        elif tool == "sqlmap":
            cmd = f"sqlmap -u {target} {params.get('flags', '--batch --random-agent')}"
        else:
            cmd = f"searchsploit {target}"
        
        return self._run_command(cmd, "exploit", target)
    
    def _execute_enumeration(self, target: str, params: Dict) -> Dict[str, Any]:
        """Execute enumeration"""
        tool = params.get("tool", "gobuster")
        
        if tool == "gobuster":
            mode = params.get("mode", "dir")
            wordlist = params.get("wordlist", "/usr/share/wordlists/dirb/common.txt")
            if mode == "dir":
                cmd = f"gobuster dir -u http://{target}/ -w {wordlist} -q"
            else:
                cmd = f"gobuster dir -u http://{target}/ -w {wordlist} -q"
        else:
            cmd = f"whois {target}"
        
        return self._run_command(cmd, "enumeration", target)
    
    def _execute_browser(self, target: str, params: Dict) -> Dict[str, Any]:
        """Execute browser automation action - USES SHARED CDP BROWSER"""
        browser_action = params.get("browser_action", "navigate")
        
        try:
            from sharingans_browser_shared import get_browser, ensure_browser_connected
            
            async def execute_browser_action():
                browser = get_browser()
                connected = await ensure_browser_connected(timeout=10.0)
                
                if not connected:
                    return {"status": "error", "message": "Failed to connect to shared browser on port 9999"}
                
                br = browser.br  # Utiliser br (propriété de BrowserAPI)
                result = {}
                
                if browser_action == "navigate":
                    url = params.get("url", "https://google.com")
                    success = await br.navigate(url)
                    result = {
                        "status": "success" if success else "error",
                        "action": "navigate",
                        "url": url,
                        "current_url": await br.get_url(),
                        "title": await br.get_title()
                    }
                
                elif browser_action == "search":
                    query = params.get("query", "")
                    await br.navigate("https://www.google.com")
                    await asyncio.sleep(1)
                    typed = await br.type_text(query, "input[name='q']")
                    if typed:
                        await br.press_key("Enter")
                    await asyncio.sleep(2)
                    result = {
                        "status": "success",
                        "action": "search",
                        "query": query,
                        "url": await br.get_url(),
                        "title": await br.get_title()
                    }
                
                elif browser_action == "read":
                    url = params.get("url", "")
                    if url:
                        await br.navigate(url)
                        await asyncio.sleep(3)
                    text = await br.get_text("article", max_length=2000)
                    result = {
                        "status": "success",
                        "action": "read",
                        "title": await br.get_title(),
                        "text": text,
                        "url": await br.get_url()
                    }
                
                elif browser_action == "scroll":
                    pixels = params.get("pixels", 400)
                    await br.scroll(0, pixels, times=3, delay=0.5)
                    result = {
                        "status": "success",
                        "action": "scroll",
                        "pixels": pixels * 3,
                        "url": await br.get_url()
                    }
                
                elif browser_action == "click":
                    selector = params.get("selector", "button, a")
                    success = await br.click(selector)
                    await asyncio.sleep(1)
                    result = {
                        "status": "success" if success else "error",
                        "action": "click",
                        "url": await br.get_url()
                    }
                
                elif browser_action == "screenshot":
                    path = params.get("path", str(Path(tempfile.gettempdir()) / "sharingan_screenshot.png"))
                    success = await br.get_screenshot(path)
                    result = {
                        "status": "success" if success else "error",
                        "action": "screenshot",
                        "path": path,
                        "url": await br.get_url()
                    }
                
                elif browser_action == "new_tab":
                    url = params.get("url", "about:blank")
                    await br.execute_js(f"window.open('{url}', '_blank')")
                    await asyncio.sleep(2)
                    result = {
                        "status": "success",
                        "action": "new_tab",
                        "url": url,
                        "current_url": await br.get_url()
                    }
                
                elif browser_action == "execute_js":
                    script = params.get("script", "return document.title")
                    js_result = await br.execute_js(script)
                    result = {
                        "status": "success",
                        "action": "execute_js",
                        "result": js_result,
                        "url": await br.get_url()
                    }
                
                else:
                    result = {"status": "error", "message": f"Unknown browser action: {browser_action}"}
                
                return result
            
            return asyncio.run(execute_browser_action())
            
        except ImportError:
            return {"status": "error", "message": "sharingans_browser_shared module not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _execute_analysis(self, target: str, params: Dict) -> Dict[str, Any]:
        """Execute general analysis - delegate to appropriate tool or run directly"""
        original_cmd = params.get("original_cmd", "")
        tool = params.get("tool", "")
        
        # Si on a une commande originale, l'exécuter directement
        if original_cmd:
            return self._run_command(original_cmd, "analysis", target)
        
        # Fallback par outil
        if tool == "curl":
            return self._run_command(f"curl -sI https://{target}", "analysis", target)
        
        cmd = f"echo 'Analysis of {target}'"
        return self._run_command(cmd, "analysis", target)
    
    def _run_command(self, cmd: str, action_type: str, target: str) -> Dict[str, Any]:
        """Run a command and return results"""
        try:
            # Validate command to prevent injection
            allowed_commands = ['nmap', 'nikto', 'dirb', 'gobuster', 'sqlmap', 'curl', 'wget', 'python3', 'pip']
            cmd_parts = shlex.split(cmd)
            if cmd_parts and cmd_parts[0] not in allowed_commands:
                raise ValueError(f"Command not allowed: {cmd_parts[0]}")

            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            executed = ExecutedAction(
                action_type=action_type,
                command=cmd,
                target=target,
                result=result.returncode,
                success=result.returncode == 0,
                output=result.stdout + result.stderr
            )
            self.execution_history.append(executed)
            
            return {
                "success": executed.success,
                "command": cmd,
                "output": executed.output[:2000],
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "command": cmd,
                "output": "Command timed out after 60 seconds",
                "error": "timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "command": cmd,
                "output": str(e),
                "error": "execution_error"
            }
    
    def execute_soul_suggestions(self, suggestions: List[str], 
                                 motivations: List[str]) -> Dict[str, Any]:
        """
        Execute all suggested actions from Sharingan Soul
        Returns combined results
        """
        results = []
        
        for i, suggestion in enumerate(suggestions):
            motivation = motivations[i] if i < len(motivations) else "unknown"
            result = self.execute_action(suggestion, motivation)
            results.append({
                "suggestion": suggestion,
                "motivation": motivation,
                "result": result
            })
        
        return {
            "actions_executed": len(results),
            "success_count": sum(1 for r in results if r["result"]["success"]),
            "results": results
        }
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get history of executed actions"""
        return [
            {
                "action_type": a.action_type,
                "command": a.command,
                "target": a.target,
                "success": a.success,
                "output": a.output[:200]
            }
            for a in self.execution_history
        ]


_action_executor: Optional[ActionExecutor] = None


def get_action_executor() -> ActionExecutor:
    """Get singleton ActionExecutor instance"""
    global _action_executor
    if _action_executor is None:
        _action_executor = ActionExecutor()
    return _action_executor


if __name__ == "__main__":
    executor = get_action_executor()
    
    test_actions = [
        "Scanner les ports avec Nmap",
        "Collecter des informations publiques",
        "Rechercher des exploits pour Apache"
    ]
    
    print("Testing Action Executor:")
    print("=" * 60)
    
    for action in test_actions:
        result = executor.execute_action(action)
        print(f"\nAction: {action}")
        print(f"Success: {result['success']}")
        print(f"Command: {result.get('command', 'N/A')}")
        print(f"Output: {result.get('output', 'N/A')[:100]}...")
