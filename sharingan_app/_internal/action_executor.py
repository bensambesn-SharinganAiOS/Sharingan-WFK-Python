#!/usr/bin/env python3
"""
Action Executor - Bridge Sharingan Soul suggestions to real tool execution
Maps autonomous intentions to concrete actions using available tools
"""

import logging
import subprocess
import json
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
        action_lower = action_text.lower()
        
        if "port" in action_lower or "scan" in action_lower:
            if "nmap" in action_lower:
                return ActionType.SCAN, self._extract_target(action_text), {
                    "tool": "nmap",
                    "flags": "-sV -sC -O"
                }
            elif "masscan" in action_lower:
                return ActionType.SCAN, self._extract_target(action_text), {
                    "tool": "masscan",
                    "flags": "--rate 10000"
                }
            return ActionType.SCAN, self._extract_target(action_text), {
                "tool": "nmap",
                "flags": "-sV -sC"
            }
        
        if "informations" in action_lower or "recon" in action_lower:
            if "whois" in action_lower:
                return ActionType.RECON, self._extract_target(action_text), {
                    "tool": "whois",
                    "flags": ""
                }
            elif "dns" in action_lower:
                return ActionType.RECON, self._extract_target(action_text), {
                    "tool": "dig",
                    "flags": "+short"
                }
            return ActionType.RECON, self._extract_target(action_text), {
                "tool": "whois",
                "flags": ""
            }
        
        if "exploit" in action_lower or "vulnerability" in action_lower:
            if "searchsploit" in action_lower or "cve" in action_lower:
                return ActionType.EXPLOIT, self._extract_target(action_text), {
                    "tool": "searchsploit",
                    "flags": ""
                }
            return ActionType.EXPLOIT, self._extract_target(action_text), {
                "tool": "searchsploit",
                "flags": ""
            }
        
        if "web" in action_lower or "directory" in action_lower or "fichier" in action_lower:
            if "gobuster" in action_lower:
                return ActionType.ENUMERATION, self._extract_target(action_text), {
                    "tool": "gobuster",
                    "mode": "dir",
                    "wordlist": "/usr/share/wordlists/dirb/common.txt"
                }
            return ActionType.ENUMERATION, self._extract_target(action_text), {
                "tool": "gobuster",
                "mode": "dir",
                "wordlist": "/usr/share/wordlists/dirb/common.txt"
            }
        
        if "sql" in action_lower or "base de donnees" in action_lower:
            return ActionType.EXPLOIT, self._extract_target(action_text), {
                "tool": "sqlmap",
                "flags": "--batch --random-agent"
            }
        
        if "mot de passe" in action_lower or "brute" in action_lower:
            if "hydra" in action_lower:
                return ActionType.EXPLOIT, self._extract_target(action_text), {
                    "tool": "hydra",
                    "flags": "-l root -P /usr/share/wordlists/rockyou.txt"
                }
            return ActionType.EXPLOIT, self._extract_target(action_text), {
                "tool": "hydra",
                "flags": ""
            }
        
        return ActionType.ANALYSIS, self._extract_target(action_text), {}
    
    def _extract_target(self, action_text: str) -> str:
        """Extract target IP or hostname from action text"""
        import re
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        hostname_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        
        ip_match = re.search(ip_pattern, action_text)
        if ip_match:
            return ip_match.group()
        
        hostname_match = re.search(hostname_pattern, action_text)
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
    
    def _execute_analysis(self, target: str, params: Dict) -> Dict[str, Any]:
        """Execute general analysis"""
        cmd = f"echo 'Analysis of {target}: No specific tool matched'"
        return self._run_command(cmd, "analysis", target)
    
    def _run_command(self, cmd: str, action_type: str, target: str) -> Dict[str, Any]:
        """Run a command and return results"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
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
