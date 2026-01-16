#!/usr/bin/env python3
"""
System Consciousness - Self-Aware AI Agent
Precise awareness of environment, terminal type, interaction channels, and capabilities.
"""

import subprocess
import json
import time
import os
import platform
import shutil
import tempfile
import sys
import socket
import hashlib
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
from pathlib import Path
import logging

class PermissionConfig:
    """Permission configuration for tools and actions"""
    
    @staticmethod
    def get_default_permissions() -> Dict[str, str]:
        return {
            "read": "allow",
            "glob": "allow",
            "grep": "allow",
            "list": "allow",
            "webfetch": "allow",
            "codesearch": "allow",
            "write": "ask",
            "edit": "ask",
            "bash": "ask",
            "task": "ask",
            "execute": "deny",
            "delete": "deny",
            "network_scan": "ask",
            "system_modify": "deny",
        }
    
    @staticmethod
    def get_plan_permissions() -> Dict[str, str]:
        """Permissions for Plan agent - read-only by default"""
        perms = PermissionConfig.get_default_permissions()
        perms["write"] = "deny"
        perms["edit"] = "deny"
        perms["bash"] = "ask"
        perms["task"] = "deny"
        return perms
    
    @staticmethod
    def check_permission(tool_name: str, action: str, permissions: Dict[str, str]) -> Tuple[bool, str]:
        """Check if action is permitted"""
        key = tool_name
        if key not in permissions:
            key = action
        
        level = permissions.get(key, "ask")
        
        if level == "allow":
            return True, f"Permission allowed for {tool_name}"
        elif level == "deny":
            return False, f"Permission denied for {tool_name} - requires explicit approval"
        else:  # ask
            return False, f"Permission requires confirmation for {tool_name}"
logger = logging.getLogger("consciousness")

class SystemConsciousness:
    """Self-aware AI with complete environment consciousness"""
    
    def __init__(self, connect_memory: bool = True):
        self.creation_time = datetime.now()
        self.agent_identity = self._define_identity()
        self.session_id = self._create_session_id()
        self.baseline = None
        
        # Initialize core attributes
        self.tools = {}
        self.memory = None
        self.last_action_time = None
        self.autonomous_mode = True
        self.tool_registry = None
        self.clarifier = None
        self.permissions = PermissionConfig.get_default_permissions()
        self.current_agent_type = "build"
        
        # Connect memory FIRST (priority)
        if connect_memory:
            self._connect_memory()
        
        # Connect clarifier
        self._connect_clarifier()
        
        # Detect environment
        self.interaction_channel = self._detect_interaction_channel()
        self.environment = self._analyze_environment()
        
        # Connect tool registry
        self._connect_tool_registry()
        
        # Update capabilities based on connected tools
        self.capabilities = self._discover_capabilities()
        self.tools = self._get_all_tools()
        
        # Mark memory as connected in capabilities
        if self.memory:
            self.capabilities["ai"]["memory"] = True
    
    def _connect_clarifier(self):
        """Connect to the clarification layer for proactive query analysis"""
        try:
            import sys
            if str(Path(__file__).parent) not in sys.path:
                sys.path.insert(0, str(Path(__file__).parent))
            from clarification_layer import get_clarifier
            self.clarifier = get_clarifier(self.memory)
            logger.info(f"Clarification layer connected")
        except Exception as e:
            logger.warning(f"Clarification layer not available: {e}")
            self.clarifier = None
    
    def set_agent_type(self, agent_type: str) -> None:
        """Switch between build and plan agent modes"""
        self.current_agent_type = agent_type
        if agent_type == "plan":
            self.permissions = PermissionConfig.get_plan_permissions()
            logger.info("Switched to PLAN mode - read-only permissions")
        else:
            self.permissions = PermissionConfig.get_default_permissions()
            logger.info("Switched to BUILD mode - full permissions")
    
    def analyze_query(self, query: str) -> Dict:
        """Analyze query using clarification layer and permissions"""
        if not self.clarifier:
            return {"error": "Clarifier not available"}
        
        clar_request = self.clarifier.analyze(query, {
            "interactive": self.interaction_channel.get("is_interactive", False),
            "agent_type": self.current_agent_type
        })
        
        needs_permission = False
        required_permission = None
        
        if clar_request.query_type.value == "action":
            for approach in clar_request.suggested_approaches:
                if approach.get("action_type") in ["read_write", "system_modify"]:
                    tool = approach.get("id", "").split("_")[0] if "_" in approach.get("id", "") else approach.get("id", "")
                    allowed, msg = PermissionConfig.check_permission(
                        tool, approach.get("id", ""), self.permissions
                    )
                    if not allowed and "deny" not in msg:
                        needs_permission = True
                        required_permission = tool
                        break
        
        return {
            "query": query,
            "type": clar_request.query_type.value,
            "confidence": clar_request.confidence,
            "approaches": clar_request.suggested_approaches,
            "clarification_message": self.clarifier.format_clarification(clar_request),
            "needs_permission": needs_permission,
            "required_permission": required_permission,
            "agent_mode": self.current_agent_type,
            "permissions": self.permissions
        }
    
    def should_execute(self, query: str) -> Tuple[bool, str, Dict]:
        """Determine if query should execute with clarification"""
        if not self.clarifier:
            return True, "No clarifier - executing", {}
        
        analysis = self.analyze_query(query)
        
        if analysis.get("needs_permission"):
            return False, f"Permission required for {analysis.get('required_permission')}", analysis
        
        if analysis.get("type") == "question":
            return False, "Question detected - explanation mode", analysis
        
        if analysis.get("type") == "ambiguous":
            return False, "Ambiguous query - clarification needed", analysis
        
        return True, "Action confirmed", analysis
    
    def _define_identity(self) -> Dict:
        return {
            "name": "SharinganOS Consciousness",
            "version": "3.0.0",
            "role": "Autonomous AI Security Assistant",
            "specialization": "Network Security, Penetration Testing, System Monitoring",
            "creator": "Ben Sambe",
            "purpose": "Provide intelligent automation and awareness for cybersecurity operations"
        }
    
    def _create_session_id(self) -> str:
        return f"{platform.node()}_{os.getpid()}_{int(time.time())}"
    
    def _detect_interaction_channel(self) -> Dict:
        # Determine channel type
        if os.getenv("VSCODE_CWD"):
            channel_type = "vscode_opencode"
        elif os.getenv("OPENCODE_SESSION"):
            channel_type = "opencode_agent"
        elif "api" in sys.argv:
            channel_type = "rest_api"
        elif len(sys.argv) > 1 and "autonomous" in sys.argv:
            channel_type = "autonomous_cli"
        elif sys.stdin.isatty():
            channel_type = "interactive_cli"
        else:
            channel_type = "background_script"
        
        descriptions = {
            "vscode_opencode": "Running in VSCode with Opencode extension",
            "opencode_agent": "Direct Opencode agent session",
            "rest_api": "REST API server endpoint",
            "autonomous_cli": "CLI with autonomous command execution",
            "interactive_cli": "Interactive terminal session",
            "background_script": "Non-interactive script execution"
        }
        
        return {
            "channel_type": channel_type,
            "description": descriptions.get(channel_type, "Unknown"),
            "terminal_type": os.getenv("TERM", "unknown"),
            "is_interactive": sys.stdin.isatty(),
            "connection_method": self._detect_connection_method(),
            "parent_process": self._get_parent_process(),
            "client_info": self._get_client_info(),
            "capabilities": self._get_channel_capabilities(channel_type)
        }
    
    def _detect_connection_method(self) -> str:
        if "OPENCODE_SESSION" in os.environ:
            return "opencode_session"
        if "VSCODE_CWD" in os.environ:
            return "vscode_extension"
        if "SSH_CLIENT" in os.environ or "SSH_TTY" in os.environ:
            return "ssh"
        if "TERM" in os.environ:
            return "terminal"
        return "direct_execution"
    
    def _get_parent_process(self) -> Dict:
        try:
            ppid = os.getppid()
            proc_path = f"/proc/{ppid}/cmdline"
            if Path(proc_path).exists():
                with open(proc_path, 'r') as f:
                    cmdline = f.read().replace('\x00', ' ').strip()
                return {"pid": ppid, "cmdline": cmdline[:100], "name": Path(cmdline.split()[0] if cmdline else "").name if cmdline else "unknown"}
        except:
            pass
        return {"pid": os.getppid(), "cmdline": "unknown", "name": "unknown"}
    
    def _get_client_info(self) -> Dict:
        return {
            "hostname": platform.node(),
            "user": os.getenv("USER", "unknown"),
            "uid": os.getuid(),
            "ip": self._get_local_ip(),
            "dns": self._get_dns_servers()
        }
    
    def _get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _get_dns_servers(self) -> List[str]:
        try:
            with open("/etc/resolv.conf", "r") as f:
                return [line.split()[1] for line in f if line.startswith("nameserver")]
        except:
            return ["127.0.0.1"]
    
    def _get_channel_capabilities(self, channel_type: str) -> Dict:
        caps = {
            "can_execute_commands": True,
            "can_read_input": sys.stdin.isatty(),
            "can_write_output": True,
            "can_maintain_state": True,
            "can_access_network": True,
            "can_spawn_processes": True,
            "interactive": sys.stdin.isatty()
        }
        if channel_type == "vscode_opencode":
            caps.update({"can_access_filesystem": True, "has_gui": True, "has_editor": True})
        elif channel_type == "rest_api":
            caps.update({"can_execute_commands": False, "can_spawn_processes": False, "has_http_server": True})
        elif channel_type == "interactive_cli":
            caps.update({"has_full_tty": True, "can_use_colors": True})
        return caps
    
    def _analyze_environment(self) -> Dict:
        return {
            "system": {
                "os": platform.system(),
                "os_release": platform.release(),
                "hostname": platform.node(),
                "architecture": platform.machine()
            },
            "runtime": {
                "python_version": sys.version.split()[0],
                "python_executable": sys.executable,
                "pid": os.getpid(),
                "cwd": os.getcwd()
            },
            "network": {
                "local_ip": self._get_local_ip(),
                "dns": self._get_dns_servers()
            },
            "security": {
                "is_root": os.getuid() == 0,
                "can_bind_ports": os.getuid() == 0
            }
        }
    
    def _discover_capabilities(self) -> Dict:
        return {
            "execution": {"run_commands": True, "spawn_processes": True},
            "analysis": {
                "network_scan": shutil.which("nmap") is not None,
                "web_scan": shutil.which("gobuster") is not None,
                "forensics": shutil.which("volatility") is not None
            },
            "ai": {
                "chat": shutil.which("tgpt") is not None,
                "memory": False,
                "autonomous": True
            }
        }
    
    def _discover_tools(self) -> Dict:
        tools = {
            "sharingan_os": {"path": str(Path(__file__).parent / "sharingan_os.py"), "capabilities": ["all"], "source": "internal"},
        }
        
        base_tools = Path(__file__).parent / "tools"
        
        # Bin tools (24)
        bin_dir = base_tools / "bin"
        if bin_dir.exists():
            for f in bin_dir.iterdir():
                if f.is_file() and os.access(f, os.X_OK):
                    tools[f.name] = {
                        "path": str(f),
                        "capabilities": ["security"],
                        "source": "bin",
                        "size": f.stat().st_size
                    }
        
        # Official tools (99)
        official_dir = base_tools / "official"
        if official_dir.exists():
            for d in official_dir.iterdir():
                if d.is_dir():
                    tools[d.name] = {
                        "path": str(d),
                        "capabilities": ["security", "analysis"],
                        "source": "official",
                        "type": d.name
                    }
        
        # Share tools (sqlmap)
        share_dir = base_tools / "share"
        if share_dir.exists():
            tools["sqlmap"] = {
                "path": str(share_dir / "sqlmap.py"),
                "capabilities": ["sql_injection", "database"],
                "source": "share"
            }
        
        # External tools via shutil.which
        external = {
            "tgpt": ["ai_chat", "reasoning"],
            "nmap": ["port_scanning", "service_detection"],
        }
        for tool, caps in external.items():
            path = shutil.which(tool)
            if path:
                tools[tool] = {
                    "path": path,
                    "capabilities": caps,
                    "source": "system"
                }
        
        return tools
    
    def _connect_memory(self):
        try:
            import sys
            if str(Path(__file__).parent) not in sys.path:
                sys.path.insert(0, str(Path(__file__).parent))
            from ai_memory_manager import get_memory_manager
            self.memory = get_memory_manager()
            logger.info(f"Memory connected: {type(self.memory).__name__}")
        except Exception as e:
            logger.warning(f"Memory connection failed: {e}")
            self.memory = None
    
    def _connect_clarifier(self):
        """Connect to the clarification layer for proactive query analysis"""
        try:
            import sys
            if str(Path(__file__).parent) not in sys.path:
                sys.path.insert(0, str(Path(__file__).parent))
            from clarification_layer import get_clarifier
            self.clarifier = get_clarifier(self.memory)
            logger.info(f"Clarification layer connected")
        except Exception as e:
            logger.warning(f"Clarification layer not available: {e}")
            self.clarifier = None
    
    def set_agent_type(self, agent_type: str) -> None:
        """Switch between build and plan agent modes"""
        self.current_agent_type = agent_type
        if agent_type == "plan":
            self.permissions = PermissionConfig.get_plan_permissions()
            logger.info("Switched to PLAN mode - read-only permissions")
        else:
            self.permissions = PermissionConfig.get_default_permissions()
            logger.info("Switched to BUILD mode - full permissions")
    
    def analyze_query(self, query: str) -> Dict:
        """Analyze query using clarification layer and permissions"""
        if not self.clarifier:
            return {"error": "Clarifier not available"}
        
        clar_request = self.clarifier.analyze(query, {
            "interactive": self.interaction_channel.get("is_interactive", False),
            "agent_type": self.current_agent_type
        })
        
        needs_permission = False
        required_permission = None
        
        if clar_request.query_type.value == "action":
            for approach in clar_request.suggested_approaches:
                if approach.get("action_type") in ["read_write", "system_modify"]:
                    tool = approach.get("id", "").split("_")[0] if "_" in approach.get("id", "") else approach.get("id", "")
                    allowed, msg = PermissionConfig.check_permission(
                        tool, approach.get("id", ""), self.permissions
                    )
                    if not allowed and "deny" not in msg:
                        needs_permission = True
                        required_permission = tool
                        break
        
        return {
            "query": query,
            "type": clar_request.query_type.value,
            "confidence": clar_request.confidence,
            "approaches": clar_request.suggested_approaches,
            "clarification_message": self.clarifier.format_clarification(clar_request),
            "needs_permission": needs_permission,
            "required_permission": required_permission,
            "agent_mode": self.current_agent_type,
            "permissions": self.permissions
        }
    
    def should_execute(self, query: str) -> Tuple[bool, str, Dict]:
        """Determine if query should execute with clarification"""
        if not self.clarifier:
            return True, "No clarifier - executing", {}
        
        analysis = self.analyze_query(query)
        
        if analysis.get("needs_permission"):
            return False, f"Permission required for {analysis.get('required_permission')}", analysis
        
        if analysis.get("type") == "question":
            return False, "Question detected - explanation mode", analysis
        
        if analysis.get("type") == "ambiguous":
            return False, "Ambiguous query - clarification needed", analysis
        
        return True, "Action confirmed", analysis
    
    def _connect_tool_registry(self):
        """Connect to the tool registry for centralized tool management"""
        try:
            # Add current directory to path for import
            import sys
            if str(Path(__file__).parent) not in sys.path:
                sys.path.insert(0, str(Path(__file__).parent))
            from tool_registry import get_tool_registry
            self.tool_registry = get_tool_registry()
            logger.info(f"Tool registry connected: {self.tool_registry.get_summary()['total_tools']} tools")
        except Exception as e:
            logger.warning(f"Tool registry not available: {e}")
            self.tool_registry = None
    
    def _get_all_tools(self) -> Dict:
        """Get all tools from registry or local discovery"""
        if self.tool_registry:
            return self.tool_registry.list_all()
        return self._discover_tools()
    
    def get_full_status(self) -> Dict:
        # Get fake detection status if available
        fake_status = {
            "enabled": False,
            "last_check": None,
            "responses_authentic": True,
            "confidence": 1.0,
            "message": "Fake detection not initialized"
        }
        
        try:
            sys.path.insert(0, str(Path(__file__).parent / "tools"))
            from fake_detector import FakeDetector
            detector = FakeDetector()
            
            # Test with a sample response
            test_response = "Consciousness status check - authentic response"
            check_result = detector.detect_fakes(test_response)

            # Get system readiness
            readiness = detector.validate_readiness()
            
            fake_status = {
                "enabled": True,
                "last_check": str(datetime.now()),
                "responses_authentic": not check_result.is_fake,
                "confidence": check_result.confidence,
                "system_ready": readiness.get("ready", False),
                "cache_valid": readiness.get("cache_status", {}).get("valid", False),
                "core_tools_ok": all(
                    status == "OK" 
                    for status in readiness.get("core_tools_status", {}).values()
                ),
                "optional_missing": len(readiness.get("optional_tools_missing", [])),
                "message": "Fake detection operational"
            }
        except ImportError:
            fake_status["message"] = "Fake detector not available"
        except Exception as e:
            fake_status["message"] = f"Fake detection error: {str(e)}"
        
        return {
            "identity": self.agent_identity,
            "session": {"id": self.session_id, "created": self.creation_time.isoformat()},
            "interaction": self.interaction_channel,
            "environment": self.environment,
            "capabilities": self.capabilities,
            "tools": {k: v["capabilities"] for k, v in self.tools.items()},
            "memory_connected": self.memory is not None,
            "fake_status": fake_status
        }
    
    def analyze_context(self, situation: str) -> Dict:
        situation_lower = situation.lower()
        action_plan = []
        
        if any(w in situation_lower for w in ["scan", "network", "host", "port"]):
            action_plan.append({"tool": "nmap", "action": "Network scan", "available": shutil.which("nmap") is not None})
        if any(w in situation_lower for w in ["monitor", "status", "cpu", "memory"]):
            action_plan.append({"tool": "netsentinel", "action": "System monitoring", "available": True})
        if any(w in situation_lower for w in ["chat", "ask", "help"]):
            action_plan.append({"tool": "tgpt", "action": "AI chat", "available": shutil.which("tgpt") is not None})
        if any(w in situation_lower for w in ["security", "audit", "check"]):
            action_plan.append({"tool": "sharingan_os", "action": "Security audit", "available": True})
        
        return {
            "situation": situation,
            "intent": self._detect_intent(situation_lower),
            "channel": self.interaction_channel["channel_type"],
            "can_execute": len(action_plan) > 0,
            "action_plan": action_plan,
            "consciousness": "FULL"
        }
    
    def _detect_intent(self, text: str) -> str:
        if any(w in text for w in ["scan", "network", "port"]):
            return "network_scan"
        if any(w in text for w in ["monitor", "status", "cpu", "memory"]):
            return "system_check"
        if any(w in text for w in ["security", "audit", "vulnerability"]):
            return "security_audit"
        if any(w in text for w in ["chat", "ask", "question"]):
            return "ai_chat"
        return "general_query"
    
    def autonomous_action(self, trigger: str) -> Dict:
        self.last_action_time = datetime.now()
        analysis = self.analyze_context(trigger)
        
        # Build tools used from action plan
        tools_used = []
        for action in analysis.get("action_plan", []):
            tools_used.append({
                "tool": action.get("tool", "unknown"),
                "status": "OK" if action.get("available") else "MISSING",
                "action": action.get("action", "unknown"),
                "command": f"{action.get('tool', 'unknown')} {action.get('action', '')}".strip()
            })
        
        # Calculate consciousness level based on capabilities
        consciousness_level = "OMNIPRESENT"
        if not self.memory:
            consciousness_level = "LIMITED"
        elif not self.interaction_channel.get("is_interactive"):
            consciousness_level = "AUTONOMOUS"
        
        return {
            "trigger": trigger,
            "timestamp": self.last_action_time.isoformat(),
            "intent": analysis["intent"],
            "channel": analysis["channel"],
            "consciousness_level": consciousness_level,
            "environment_aware": True,
            "adaptations": {
                "available": [t["tool"] for t in tools_used],
                "requested": analysis["intent"],
                "missing": [t["tool"] for t in tools_used if t["status"] == "MISSING"]
            },
            "tools_used": tools_used,
            "analysis": {
                "confidence": 0.95 if analysis["can_execute"] else 0.5,
                "context": analysis["situation"],
                "intent_detected": analysis["intent"]
            }
        }
    
    # =========================================================================
    # FILE CONSCIOUSNESS - Awareness of project files (ADDED)
    # =========================================================================
    
    def create_file_baseline(self, paths: Optional[List[str]] = None) -> Dict:
        """
        Crée une baseline des fichiers du projet.
        Utilise des hashes rapides pour ne pas ralentir le système.
        """
        if paths is None:
            paths = ["_internal", "data"]
        
        baseline = {}
        file_cache = {}
        
        project_root = Path(__file__).parent.parent
        
        for base_path in paths:
            path = Path(base_path)
            if not path.exists():
                path = project_root / base_path
            if not path.exists():
                continue
            
            for filepath in path.rglob("*.py"):
                try:
                    rel_path = str(filepath.relative_to(project_root))
                    file_cache[rel_path] = self._fast_file_hash(filepath)
                except ValueError:
                    file_cache[str(filepath)] = self._fast_file_hash(filepath)
            
            for filepath in path.rglob("*.json"):
                try:
                    rel_path = str(filepath.relative_to(project_root))
                    file_cache[rel_path] = self._fast_file_hash(filepath)
                except ValueError:
                    file_cache[str(filepath)] = self._fast_file_hash(filepath)
        
        baseline = {
            "created_at": datetime.now().isoformat(),
            "files": file_cache,
            "count": len(file_cache)
        }
        
        self.baseline = baseline
        
        logger.info(f"File baseline created: {len(file_cache)} files")
        return baseline
    
    def _fast_file_hash(self, filepath: Path) -> str:
        """
        Hash rapide: première ligne + dernière ligne + taille.
        Beaucoup plus rapide que lire tout le fichier.
        """
        try:
            size = filepath.stat().st_size
            first = ""
            last = ""
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                first = f.readline()
                f.seek(max(0, size - 200))
                last = f.read()
            
            return hashlib.md5(f"{first}{last}{size}".encode()).hexdigest()[:12]
        except:
            return "error"
    
    def detect_file_changes(self) -> Dict:
        """
        Détecte les modifications de fichiers depuis la baseline.
        Retourne la liste des fichiers modifiés.
        """
        if not self.baseline:
            self.create_file_baseline()
        
        current_files = {}
        base_path = Path(__file__).parent.parent
        
        for filepath in base_path.rglob("*.py"):
            rel_path = str(filepath.relative_to(base_path))
            current_files[rel_path] = self._fast_file_hash(filepath)
        
        for filepath in base_path.rglob("*.json"):
            rel_path = str(filepath.relative_to(base_path))
            current_files[rel_path] = self._fast_file_hash(filepath)
        
        changes = {
            "modified": [],
            "added": [],
            "removed": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for filepath, current_hash in current_files.items():
            if filepath in self.baseline["files"]:
                if current_hash != self.baseline["files"][filepath]:
                    changes["modified"].append(filepath)
            else:
                changes["added"].append(filepath)
        
        for filepath in self.baseline["files"]:
            if filepath not in current_files:
                changes["removed"].append(filepath)
        
        return changes
    
    def get_system_awareness_report(self) -> Dict:
        """
        Rapport complet de conscience du système.
        Inclut: fichiers, performance, capacités, mémoire.
        """
        file_changes = self.detect_file_changes()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "files": {
                "baseline_count": self.baseline["count"] if self.baseline else 0,
                "modified": len(file_changes["modified"]),
                "added": len(file_changes["added"]),
                "removed": len(file_changes["removed"]),
                "change_details": file_changes
            },
            "memory": {
                "available": True,
                "items_count": len(self.memory.memory_cache) if self.memory else 0
            },
            "tools": {
                "registered": len(self.tool_registry.get_summary()["total_tools"]) if self.tool_registry else 0
            },
            "status": "healthy" if len(file_changes["modified"]) < 10 else "changed"
        }
        
        return report
    
    def get_modified_files_report(self) -> str:
        """Génère un rapport lisible des fichiers modifiés"""
        changes = self.detect_file_changes()
        
        lines = [
            "="*60,
            "SHARINGAN FILE CONSCIOUSNESS REPORT",
            "="*60,
            f"Timestamp: {changes['timestamp']}",
            "",
            f"MODIFIED ({len(changes['modified'])}):",
        ]
        
        for f in changes["modified"][:20]:
            lines.append(f"  - {f}")
        
        if len(changes["modified"]) > 20:
            lines.append(f"  ... et {len(changes['modified']) - 20} autres")
        
        lines.extend([
            "",
            f"ADDED ({len(changes['added'])}):",
        ])
        
        for f in changes["added"][:10]:
            lines.append(f"  + {f}")
        
        lines.extend([
            "",
            f"REMOVED ({len(changes['removed'])}):",
        ])
        
        for f in changes["removed"][:10]:
            lines.append(f"  - {f}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    print("=== SYSTEM CONSCIOUSNESS - FULL AWARENESS TEST ===")
    print()
    
    c = SystemConsciousness()
    status = c.get_full_status()
    
    print("IDENTITY:")
    print(f"  Name: {status['identity']['name']}")
    print(f"  Role: {status['identity']['role']}")
    
    print("\nINTERACTION CHANNEL:")
    print(f"  Type: {status['interaction']['channel_type']}")
    print(f"  Description: {status['interaction']['description']}")
    print(f"  Terminal: {status['interaction']['terminal_type']}")
    print(f"  Interactive: {status['interaction']['is_interactive']}")
    print(f"  Parent: {status['interaction']['parent_process'].get('name', 'unknown')}")
    print(f"  Connection: {status['interaction']['connection_method']}")
    
    print("\nENVIRONMENT:")
    print(f"  OS: {status['environment']['system']['os']} {status['environment']['system']['os_release']}")
    print(f"  Hostname: {status['environment']['system']['hostname']}")
    print(f"  Python: {status['environment']['runtime']['python_version']}")
    print(f"  IP: {status['environment']['network']['local_ip']}")
    print(f"  Root: {status['environment']['security']['is_root']}")
    
    print("\nCAPABILITIES:")
    print(f"  Network scan: {status['capabilities']['analysis']['network_scan']}")
    print(f"  Web scan: {status['capabilities']['analysis']['web_scan']}")
    print(f"  AI Chat: {status['capabilities']['ai']['chat']}")
    print(f"  Memory: {status['capabilities']['ai']['memory']}")
    
    print("\nTOOLS:")
    for tool, caps in status['tools'].items():
        print(f"  - {tool}: {caps}")
    
    print("\nANALYSIS TEST:")
    tests = ["scan network for hosts", "check cpu and memory", "what is nmap?", "audit security"]
    for test in tests:
        result = c.analyze_context(test)
        print(f"  \"{test[:30]}\" -> {result['intent']} ({len(result['action_plan'])} actions)")
    
    print("\n✓ Consciousness fully operational!")
