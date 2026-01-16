#!/usr/bin/env python3
"""
Sharingan OS - Network Tools Wrappers
Wrappers Python pour tous les outils réseau Kali Linux
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import threading
import time

class NmapWrapper:
    """Wrapper Python pour Nmap"""

    def __init__(self):
        self.command = "nmap"
        self.name = "nmap"
        self.description = "Network Mapper - Advanced port scanner"

    def scan(self, target: str, options: str = "-sV -p-", **kwargs) -> Dict[str, Any]:
        """Effectue un scan Nmap"""
        cmd = [self.command, options, target]

        # Options supplémentaires
        if kwargs.get("aggressive"):
            cmd.insert(1, "-A")
        if kwargs.get("os_detection"):
            cmd.insert(1, "-O")
        if kwargs.get("script_scan"):
            cmd.insert(1, "--script=vuln")
        if kwargs.get("timing"):
            cmd.insert(1, f"-T{kwargs['timing']}")
        if kwargs.get("output_file"):
            cmd.extend(["-oN", kwargs["output_file"]])

        result = self._run_command(cmd, kwargs.get("timeout", 300))

        # Parser les résultats
        if result["success"]:
            result["parsed"] = self._parse_nmap_output(result["stdout"])

        return result

    def _parse_nmap_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Nmap"""
        parsed = {
            "hosts": [],
            "ports": [],
            "services": [],
            "os_detection": None
        }

        lines = output.split('\n')
        current_host = None

        for line in lines:
            line = line.strip()
            if "Nmap scan report for" in line:
                if current_host:
                    parsed["hosts"].append(current_host)
                current_host = {"address": line.split()[-1], "ports": [], "services": []}
            elif "/tcp" in line or "/udp" in line:
                if current_host:
                    port_info = self._parse_port_line(line)
                    if port_info:
                        current_host["ports"].append(port_info)
                        parsed["ports"].append(port_info)
            elif "Service detection performed" in line:
                continue
            elif "OS details:" in line:
                parsed["os_detection"] = line.replace("OS details:", "").strip()

        if current_host:
            parsed["hosts"].append(current_host)

        return parsed

    def _parse_port_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse une ligne de port Nmap"""
        try:
            parts = line.split()
            if len(parts) >= 3:
                port_protocol = parts[0].split('/')
                state = parts[1]
                service = parts[2]

                return {
                    "port": int(port_protocol[0]),
                    "protocol": port_protocol[1],
                    "state": state,
                    "service": service,
                    "version": " ".join(parts[3:]) if len(parts) > 3 else ""
                }
        except:
            pass
        return None

    def _run_command(self, cmd: List[str], timeout: int = 300) -> Dict[str, Any]:
        """Exécute une commande"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd),
                "execution_time": 0.0  # Would need to measure
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s",
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class MasscanWrapper:
    """Wrapper Python pour Masscan"""

    def __init__(self):
        self.command = "masscan"
        self.name = "masscan"
        self.description = "Mass IP port scanner"

    def scan(self, target: str, ports: str = "1-65535", rate: int = 1000, **kwargs) -> Dict[str, Any]:
        """Effectue un scan Masscan"""
        cmd = [
            self.command,
            target,
            "-p", ports,
            "--rate", str(rate)
        ]

        # Options supplémentaires
        if kwargs.get("output_file"):
            cmd.extend(["-oL", kwargs["output_file"]])
        if kwargs.get("exclude_file"):
            cmd.extend(["--excludefile", kwargs["exclude_file"]])
        if kwargs.get("source_ip"):
            cmd.extend(["--source-ip", kwargs["source_ip"]])

        result = self._run_command(cmd, kwargs.get("timeout", 600))

        if result["success"]:
            result["parsed"] = self._parse_masscan_output(result["stdout"])

        return result

    def _parse_masscan_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse la sortie Masscan"""
        results = []

        for line in output.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    results.append({
                        "timestamp": parts[0],
                        "ip": parts[1],
                        "port": int(parts[2]),
                        "protocol": parts[3] if len(parts) > 3 else "tcp"
                    })

        return results

    def _run_command(self, cmd: List[str], timeout: int = 600) -> Dict[str, Any]:
        """Exécute une commande"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s",
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class NetdiscoverWrapper:
    """Wrapper Python pour Netdiscover"""

    def __init__(self):
        self.command = "netdiscover"
        self.name = "netdiscover"
        self.description = "Network address discovery"

    def discover(self, range_ip: str = "192.168.1.0/24", **kwargs) -> Dict[str, Any]:
        """Effectue une découverte réseau"""
        cmd = [self.command, "-r", range_ip, "-P", "-s", "1"]

        # Options supplémentaires
        if kwargs.get("interface"):
            cmd.extend(["-i", kwargs["interface"]])
        if kwargs.get("passive"):
            cmd.remove("-s")
            cmd.remove("1")
        if kwargs.get("timeout"):
            cmd.extend(["-t", str(kwargs["timeout"])])
        if kwargs.get("output_file"):
            cmd.extend([">", kwargs["output_file"]])

        result = self._run_command(cmd, kwargs.get("timeout", 60))

        if result["success"]:
            result["parsed"] = self._parse_netdiscover_output(result["stdout"])

        return result

    def _parse_netdiscover_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse la sortie Netdiscover"""
        hosts = []

        for line in output.split('\n'):
            if '.' in line and ':' in line and not line.startswith(' '):
                parts = line.split()
                if len(parts) >= 2:
                    ip_mac = parts[0].split('/')
                    hosts.append({
                        "ip": ip_mac[0],
                        "mac": ip_mac[1] if len(ip_mac) > 1 else parts[1],
                        "vendor": " ".join(parts[2:]) if len(parts) > 2 else ""
                    })

        return hosts

    def _run_command(self, cmd: List[str], timeout: int = 60) -> Dict[str, Any]:
        """Exécute une commande"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s",
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class ArpScanWrapper:
    """Wrapper Python pour Arp-scan"""

    def __init__(self):
        self.command = "arp-scan"
        self.name = "arp-scan"
        self.description = "ARP network scanner"

    def scan(self, interface: str = "eth0", target: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Effectue un scan ARP"""
        cmd = [self.command, "--interface", interface]

        if target:
            cmd.append(target)
        else:
            cmd.append("--localnet")

        # Options supplémentaires
        if kwargs.get("verbose"):
            cmd.append("--verbose")
        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])
        if kwargs.get("vendor"):
            cmd.append("--vendor")

        result = self._run_command(cmd, kwargs.get("timeout", 30))

        if result["success"]:
            result["parsed"] = self._parse_arpscan_output(result["stdout"])

        return result

    def _parse_arpscan_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse la sortie Arp-scan"""
        hosts = []

        for line in output.split('\n'):
            line = line.strip()
            if '\t' in line and not line.startswith('Interface') and not line.startswith('Starting'):
                parts = line.split('\t')
                if len(parts) >= 3:
                    hosts.append({
                        "ip": parts[0],
                        "mac": parts[1],
                        "vendor": parts[2] if len(parts) > 2 else ""
                    })

        return hosts

    def _run_command(self, cmd: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Exécute une commande"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s",
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class Hping3Wrapper:
    """Wrapper Python pour Hping3"""

    def __init__(self):
        self.command = "hping3"
        self.name = "hping3"
        self.description = "TCP/IP packet assembler/analyzer"

    def scan(self, target: str, scan_type: str = "syn", ports: str = "1-100", **kwargs) -> Dict[str, Any]:
        """Effectue un scan avec Hping3"""
        cmd = [self.command, target]

        # Type de scan
        if scan_type == "syn":
            cmd.extend(["--scan", ports])
        elif scan_type == "ack":
            cmd.extend(["-A", "-p", ports])
        elif scan_type == "fin":
            cmd.extend(["-F", "-p", ports])
        elif scan_type == "xmas":
            cmd.extend(["-X", "-p", ports])

        # Options supplémentaires
        if kwargs.get("flood"):
            cmd.append("--flood")
        if kwargs.get("verbose"):
            cmd.append("-v")
        if kwargs.get("count"):
            cmd.extend(["-c", str(kwargs["count"])])
        if kwargs.get("interface"):
            cmd.extend(["-I", kwargs["interface"]])

        result = self._run_command(cmd, kwargs.get("timeout", 60))

        if result["success"]:
            result["parsed"] = self._parse_hping3_output(result["stdout"])

        return result

    def flood(self, target: str, **kwargs) -> Dict[str, Any]:
        """Effectue un flood avec Hping3"""
        cmd = [self.command, target, "--flood"]

        if kwargs.get("syn"):
            cmd.append("--syn")
        if kwargs.get("ack"):
            cmd.append("--ack")
        if kwargs.get("rst"):
            cmd.append("--rst")

        return self._run_command(cmd, kwargs.get("timeout", 30))

    def _parse_hping3_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Hping3"""
        parsed = {
            "packets": [],
            "statistics": {}
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            if "len=" in line and "ip=" in line:
                # Ligne de paquet
                parsed["packets"].append(line)
            elif "packets transmitted" in line:
                # Statistiques
                parts = line.split(',')
                for part in parts:
                    if "packets transmitted" in part:
                        parsed["statistics"]["transmitted"] = part.split()[0]
                    elif "packets received" in part:
                        parsed["statistics"]["received"] = part.split()[0]
                    elif "packet loss" in part:
                        parsed["statistics"]["loss"] = part.split()[0]

        return parsed

    def _run_command(self, cmd: List[str], timeout: int = 60) -> Dict[str, Any]:
        """Exécute une commande"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout}s",
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Gestionnaire unifié pour les outils réseau
class NetworkToolsManager:
    """Gestionnaire unifié des outils réseau"""

    def __init__(self):
        self.tools = {
            "nmap": NmapWrapper(),
            "masscan": MasscanWrapper(),
            "netdiscover": NetdiscoverWrapper(),
            "arp-scan": ArpScanWrapper(),
            "hping3": Hping3Wrapper()
        }

    def get_tool(self, name: str):
        """Récupère un outil par nom"""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """Liste tous les outils disponibles"""
        return list(self.tools.keys())

    def scan_network(self, target: str, method: str = "nmap", **kwargs) -> Dict[str, Any]:
        """Effectue un scan réseau avec l'outil spécifié"""
        tool = self.get_tool(method)
        if not tool:
            return {"error": f"Unknown scanning method: {method}"}

        if method == "nmap":
            return tool.scan(target, **kwargs)
        elif method == "masscan":
            return tool.scan(target, **kwargs)
        elif method == "netdiscover":
            return tool.discover(target, **kwargs)
        elif method == "arp-scan":
            return tool.scan(target=target, **kwargs)
        elif method == "hping3":
            return tool.scan(target, **kwargs)
        else:
            return {"error": f"Unsupported scan method: {method}"}

def main():
    """Test des wrappers réseau"""
    import argparse

    parser = argparse.ArgumentParser(description="Network Tools Wrappers")
    parser.add_argument("target", help="Target to scan")
    parser.add_argument("--tool", choices=["nmap", "masscan", "netdiscover", "arp-scan", "hping3"],
                       default="nmap", help="Tool to use")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    manager = NetworkToolsManager()

    print(f"🔍 Scanning {args.target} with {args.tool}...")

    result = manager.scan_network(args.target, args.tool, output_file=args.output)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        if result.get("success"):
            print("✅ Scan completed successfully")
            if "parsed" in result:
                parsed = result["parsed"]
                if "hosts" in parsed:
                    print(f"Found {len(parsed['hosts'])} hosts")
                elif "ports" in parsed:
                    print(f"Found {len(parsed['ports'])} open ports")
                else:
                    print(f"Results: {len(parsed) if isinstance(parsed, list) else 'N/A'} items")
        else:
            print(f"❌ Scan failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()