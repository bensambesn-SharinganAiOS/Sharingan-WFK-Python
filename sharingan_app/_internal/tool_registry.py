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
                "system": {"count": 0, "description": "System"}
            }
        }
        
        # DÉCOUVERTE AUTOMATIQUE
        registry["tools"] = self._discover_all_tools()
        registry["last_scan"] = str(__import__("datetime").datetime.now().isoformat())
        
        return registry
    
    def _discover_all_tools(self) -> Dict[str, Dict]:
        tools = {}
        base = self.base_dir
        
        # 1. BIN (24 exécutables)
        bin_dir = base / "tools" / "bin"
        if bin_dir.exists():
            for f in sorted(bin_dir.iterdir()):
                if f.is_file() and os.access(f, os.X_OK):
                    tools[f.name] = {
                        "name": f.name,
                        "category": self._guess_category(f.name),
                        "path": str(f),
                        "capabilities": [self._guess_category(f.name)],
                        "source": "bin",
                        "size": f.stat().st_size
                    }
        
        # 2. OFFICIAL (99 scripts)
        official_dir = base / "tools" / "official"
        if official_dir.exists():
            for d in sorted(official_dir.iterdir()):
                tools[d.name] = {
                    "name": d.name,
                    "category": self._guess_category(d.name),
                    "path": str(d),
                    "capabilities": [self._guess_category(d.name)],
                    "source": "official"
                }
        
        # 3. SHARE (sqlmap)
        share_dir = base / "tools" / "share"
        if share_dir.exists():
            for f in share_dir.glob("sqlmap*.py"):
                name = f.stem
                tools[name] = {
                    "name": name,
                    "category": "web",
                    "path": str(f),
                    "capabilities": ["sql_injection"],
                    "source": "share"
                }
        
        # 4. SYSTÈME (tgpt, nmap)
        for tool in ["tgpt", "nmap"]:
            path = shutil.which(tool)
            if path:
                tools[tool] = {
                    "name": tool,
                    "category": "ai" if tool == "tgpt" else "network",
                    "path": path,
                    "capabilities": ["ai_chat"] if tool == "tgpt" else ["port_scan"],
                    "source": "system"
                }
        
        # 5. INTERNAL
        tools["sharingan_os"] = {
            "name": "sharingan_os",
            "category": "ai",
            "path": str(base / "sharingan_os.py"),
            "capabilities": ["all"],
            "source": "internal"
        }
        
        tools["netsentinel"] = {
            "name": "netsentinel",
            "category": "system",
            "path": str(base / "tools" / "network_monitor.py"),
            "capabilities": ["monitoring", "ids"],
            "source": "internal"
        }
        
        return tools
    
    def _guess_category(self, name: str) -> str:
        n = name.lower()
        if n in ["nmap", "masscan", "netdiscover", "rustscan", "naabu", "zmap"]: return "network"
        if n in ["gobuster", "ffuf", "dirsearch", "nikto", "wpscan", "sqlmap"]: return "web"
        if n in ["hashcat", "john", "crunch", "hydra", "medusa"]: return "password"
        if n in ["harvester", "sherlock", "spiderfoot", "amass", "subfinder"]: return "osint"
        if n in ["binwalk", "volatility", "exiftool", "foremost", "scapy"]: return "forensics"
        if n in ["aircrack", "wifite", "bettercap"]: return "wireless"
        if n in ["lynis", "rkhunter"]: return "audit"
        return "network"
    
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
