#!/usr/bin/env python3
"""
Sharingan OS - Wireless Tools Wrappers
Wrappers Python pour tous les outils sans fil Kali Linux
"""

import subprocess
import sys
import os
import json
import re
import time
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import threading

class AircrackNgWrapper:
    """Wrapper Python pour Aircrack-ng"""

    def __init__(self):
        self.command = "aircrack-ng"
        self.name = "aircrack-ng"
        self.description = "Wireless network auditor"

    def crack_wep(self, capture_file: str, essid: str = None, **kwargs) -> Dict[str, Any]:
        """Crack WEP avec Aircrack-ng"""
        cmd = [self.command, capture_file]

        if essid:
            cmd.extend(["-e", essid])
        if kwargs.get("bssid"):
            cmd.extend(["-b", kwargs["bssid"]])
        if kwargs.get("output_file"):
            cmd.extend(["-l", kwargs["output_file"]])

        result = self._run_command(cmd, kwargs.get("timeout", 1800))

        if result["success"]:
            result["parsed"] = self._parse_aircrack_output(result["stdout"])

        return result

    def crack_wpa(self, capture_file: str, wordlist: str = "/usr/share/wordlists/rockyou.txt",
                  essid: str = None, **kwargs) -> Dict[str, Any]:
        """Crack WPA/WPA2 avec Aircrack-ng"""
        cmd = [self.command, "-w", wordlist, capture_file]

        if essid:
            cmd.extend(["-e", essid])
        if kwargs.get("bssid"):
            cmd.extend(["-b", kwargs["bssid"]])
        if kwargs.get("output_file"):
            cmd.extend(["-l", kwargs["output_file"]])

        result = self._run_command(cmd, kwargs.get("timeout", 3600))

        if result["success"]:
            result["parsed"] = self._parse_aircrack_output(result["stdout"])

        return result

    def _parse_aircrack_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Aircrack-ng"""
        parsed = {
            "key_found": False,
            "key": None,
            "essid": "",
            "bssid": "",
            "encryption": "",
            "tries": 0,
            "progress": ""
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            if "KEY FOUND!" in line:
                parsed["key_found"] = True
                # Extraire la clé
                match = re.search(r'\[ ([^\]]+) \]', line)
                if match:
                    parsed["key"] = match.group(1)

            elif "ESSID:" in line:
                parsed["essid"] = line.split(":", 1)[1].strip().strip('"')

            elif "BSSID:" in line:
                parsed["bssid"] = line.split(":", 1)[1].strip()

            elif "Encryption:" in line:
                parsed["encryption"] = line.split(":", 1)[1].strip()

            elif "Tried" in line and "keys" in line:
                match = re.search(r'Tried (\d+) keys', line)
                if match:
                    parsed["tries"] = int(match.group(1))

            elif "%" in line and any(x in line for x in ["KEY", "tested", "speed"]):
                parsed["progress"] = line

        return parsed

    def _run_command(self, cmd: List[str], timeout: int = 3600) -> Dict[str, Any]:
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

class AirodumpNgWrapper:
    """Wrapper Python pour Airodump-ng"""

    def __init__(self):
        self.command = "airodump-ng"
        self.name = "airodump-ng"
        self.description = "Packet capture and network discovery"

    def scan(self, interface: str, **kwargs) -> Dict[str, Any]:
        """Effectue un scan avec Airodump-ng"""
        cmd = [self.command, interface]

        if kwargs.get("channel"):
            cmd.extend(["--channel", str(kwargs["channel"])])
        if kwargs.get("bssid"):
            cmd.extend(["--bssid", kwargs["bssid"]])
        if kwargs.get("essid"):
            cmd.extend(["--essid", kwargs["essid"]])
        if kwargs.get("output_file"):
            cmd.extend(["--write", kwargs["output_file"]])
        if kwargs.get("write_interval"):
            cmd.extend(["--write-interval", str(kwargs["write_interval"])])

        # Airodump-ng fonctionne en continu, on le limite
        result = self._run_command(cmd, kwargs.get("timeout", 30))

        if result["success"]:
            result["parsed"] = self._parse_airodump_output(result["stdout"])

        return result

    def _parse_airodump_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Airodump-ng"""
        parsed = {
            "access_points": [],
            "clients": [],
            "interface": "",
            "channel": ""
        }

        lines = output.split('\n')
        parsing_aps = False
        parsing_clients = False

        for line in lines:
            line = line.strip()

            if "CH " in line and "ELAPSED" in line:
                # En-tête des APs
                parsing_aps = True
                parsing_clients = False
                continue
            elif "STATION" in line and "PWR" in line:
                # En-tête des clients
                parsing_aps = False
                parsing_clients = True
                continue
            elif not line or line.startswith("---"):
                continue

            if parsing_aps and line and not line.startswith("BSSID"):
                # Ligne AP: BSSID, PWR, Beacons, #Data, CH, MB, ENC, CIPHER, AUTH, ESSID
                parts = line.split()
                if len(parts) >= 11:
                    ap = {
                        "bssid": parts[0],
                        "pwr": int(parts[1]) if parts[1] != "-1" else None,
                        "beacons": int(parts[2]),
                        "data": int(parts[3]),
                        "ch": int(parts[4]),
                        "mb": parts[5],
                        "enc": parts[6],
                        "cipher": parts[7],
                        "auth": parts[8],
                        "essid": " ".join(parts[9:])
                    }
                    parsed["access_points"].append(ap)

            elif parsing_clients and line and not line.startswith("BSSID"):
                # Ligne client: BSSID, STATION, PWR, Rate, Lost, Frames, Probe
                parts = line.split()
                if len(parts) >= 6:
                    client = {
                        "bssid": parts[0],
                        "station": parts[1],
                        "pwr": int(parts[2]) if parts[2] != "-1" else None,
                        "rate": parts[3],
                        "lost": int(parts[4]),
                        "frames": int(parts[5]),
                        "probe": " ".join(parts[6:]) if len(parts) > 6 else ""
                    }
                    parsed["clients"].append(client)

        return parsed

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

class AireplayNgWrapper:
    """Wrapper Python pour Aireplay-ng"""

    def __init__(self):
        self.command = "aireplay-ng"
        self.name = "aireplay-ng"
        self.description = "Packet injection tool"

    def deauth(self, interface: str, bssid: str, client: str = None, **kwargs) -> Dict[str, Any]:
        """Effectue une attaque de déauthentification"""
        cmd = [self.command, "--deauth", "10", "-a", bssid, interface]

        if client:
            cmd.extend(["-c", client])
        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])

        result = self._run_command(cmd, kwargs.get("timeout", 60))

        if result["success"]:
            result["parsed"] = self._parse_aireplay_output(result["stdout"])

        return result

    def fake_auth(self, interface: str, bssid: str, **kwargs) -> Dict[str, Any]:
        """Effectue une authentification fake"""
        cmd = [self.command, "--fakeauth", "30", "-a", bssid, "-h", kwargs.get("client_mac", "00:11:22:33:44:55"), interface]

        if kwargs.get("essid"):
            cmd.extend(["-e", kwargs["essid"]])

        result = self._run_command(cmd, kwargs.get("timeout", 60))

        if result["success"]:
            result["parsed"] = self._parse_aireplay_output(result["stdout"])

        return result

    def arp_replay(self, interface: str, bssid: str, **kwargs) -> Dict[str, Any]:
        """Effectue une attaque ARP replay"""
        cmd = [self.command, "--arpreplay", "-b", bssid, "-h", kwargs.get("client_mac", "00:11:22:33:44:55"), interface]

        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])

        result = self._run_command(cmd, kwargs.get("timeout", 120))

        if result["success"]:
            result["parsed"] = self._parse_aireplay_output(result["stdout"])

        return result

    def _parse_aireplay_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Aireplay-ng"""
        parsed = {
            "packets_sent": 0,
            "status": "",
            "target_bssid": "",
            "target_station": ""
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            if "packets sent" in line:
                match = re.search(r'(\d+) packets sent', line)
                if match:
                    parsed["packets_sent"] = int(match.group(1))

            elif "DeAuth" in line or "authentication" in line.lower():
                parsed["status"] = line

            elif "BSSID:" in line:
                match = re.search(r'BSSID:\s*([^\s]+)', line)
                if match:
                    parsed["target_bssid"] = match.group(1)

            elif "STATION:" in line:
                match = re.search(r'STATION:\s*([^\s]+)', line)
                if match:
                    parsed["target_station"] = match.group(1)

        return parsed

    def _run_command(self, cmd: List[str], timeout: int = 120) -> Dict[str, Any]:
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

class ReaverWrapper:
    """Wrapper Python pour Reaver"""

    def __init__(self):
        self.command = "reaver"
        self.name = "reaver"
        self.description = "WiFi Protected Setup attack tool"

    def attack_wps(self, interface: str, bssid: str, **kwargs) -> Dict[str, Any]:
        """Effectue une attaque WPS avec Reaver"""
        cmd = [self.command, "-i", interface, "-b", bssid, "-vv"]

        if kwargs.get("channel"):
            cmd.extend(["-c", str(kwargs["channel"])])
        if kwargs.get("essid"):
            cmd.extend(["-e", kwargs["essid"]])
        if kwargs.get("pin"):
            cmd.extend(["-p", kwargs["pin"]])
        if kwargs.get("pixie_dust"):
            cmd.append("-K")
        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])

        result = self._run_command(cmd, kwargs.get("timeout", 3600))

        if result["success"]:
            result["parsed"] = self._parse_reaver_output(result["stdout"])

        return result

    def _parse_reaver_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Reaver"""
        parsed = {
            "wps_pin_found": False,
            "wps_pin": None,
            "wpa_psk": None,
            "essid": "",
            "bssid": "",
            "progress": "",
            "warnings": []
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            if "WPS PIN:" in line:
                match = re.search(r'WPS PIN:\s*(\d+)', line)
                if match:
                    parsed["wps_pin"] = match.group(1)
                    parsed["wps_pin_found"] = True

            elif "WPA PSK:" in line:
                match = re.search(r'WPA PSK:\s*([^\n]+)', line)
                if match:
                    parsed["wpa_psk"] = match.group(1).strip("'\"")

            elif "ESSID:" in line:
                match = re.search(r'ESSID:\s*([^\n]+)', line)
                if match:
                    parsed["essid"] = match.group(1).strip("'\"")

            elif "BSSID:" in line:
                match = re.search(r'BSSID:\s*([^\n]+)', line)
                if match:
                    parsed["bssid"] = match.group(1)

            elif "% complete" in line:
                parsed["progress"] = line

            elif "WARNING" in line.upper():
                parsed["warnings"].append(line)

        return parsed

    def _run_command(self, cmd: List[str], timeout: int = 3600) -> Dict[str, Any]:
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

class BullyWrapper:
    """Wrapper Python pour Bully"""

    def __init__(self):
        self.command = "bully"
        self.name = "bully"
        self.description = "WPS brute force attack tool"

    def attack_wps(self, interface: str, bssid: str, **kwargs) -> Dict[str, Any]:
        """Effectue une attaque WPS avec Bully"""
        cmd = [self.command, interface, "-b", bssid]

        if kwargs.get("channel"):
            cmd.extend(["-c", str(kwargs["channel"])])
        if kwargs.get("essid"):
            cmd.extend(["-e", kwargs["essid"]])
        if kwargs.get("pin"):
            cmd.extend(["-p", kwargs["pin"]])
        if kwargs.get("brute_force"):
            cmd.append("-B")
        if kwargs.get("pixie_dust"):
            cmd.append("-d")
        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])
        if kwargs.get("verbose"):
            cmd.append("-v")

        result = self._run_command(cmd, kwargs.get("timeout", 3600))

        if result["success"]:
            result["parsed"] = self._parse_bully_output(result["stdout"])

        return result

    def _parse_bully_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Bully"""
        parsed = {
            "wps_pin_found": False,
            "wps_pin": None,
            "wpa_psk": None,
            "essid": "",
            "bssid": "",
            "attempts": 0,
            "warnings": []
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            if "[+] PIN is" in line:
                match = re.search(r'PIN is (\d+)', line)
                if match:
                    parsed["wps_pin"] = match.group(1)
                    parsed["wps_pin_found"] = True

            elif "[+] PSK is" in line:
                match = re.search(r'PSK is "([^"]+)"', line)
                if match:
                    parsed["wpa_psk"] = match.group(1)

            elif "[+] ESSID is" in line:
                match = re.search(r'ESSID is "([^"]+)"', line)
                if match:
                    parsed["essid"] = match.group(1)

            elif "[+] BSSID is" in line:
                match = re.search(r'BSSID is ([^\s]+)', line)
                if match:
                    parsed["bssid"] = match.group(1)

            elif "[!] Warning:" in line:
                parsed["warnings"].append(line)

            elif "Trying PIN" in line:
                parsed["attempts"] += 1

        return parsed

    def _run_command(self, cmd: List[str], timeout: int = 3600) -> Dict[str, Any]:
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

class AiromonNgWrapper:
    """Wrapper Python pour Airomon-ng"""

    def __init__(self):
        self.command = "airomon-ng"
        self.name = "airomon-ng"
        self.description = "Airmon-ng wireless interface monitor mode"

    def start_monitor(self, interface: str, **kwargs) -> Dict[str, Any]:
        """Démarre le mode monitor"""
        cmd = [self.command, "start", interface]

        if kwargs.get("channel"):
            cmd.extend([str(kwargs["channel"])])
        if kwargs.get("output_file"):
            cmd.extend([">", kwargs["output_file"]])

        result = self._run_command(cmd, kwargs.get("timeout", 30))

        if result["success"]:
            result["parsed"] = self._parse_airomon_output(result["stdout"])

        return result

    def stop_monitor(self, interface: str, **kwargs) -> Dict[str, Any]:
        """Arrête le mode monitor"""
        cmd = [self.command, "stop", interface]

        result = self._run_command(cmd, kwargs.get("timeout", 30))

        if result["success"]:
            result["parsed"] = {"monitor_stopped": True}

        return result

    def check_kill(self, **kwargs) -> Dict[str, Any]:
        """Tue les processus qui interfèrent"""
        cmd = [self.command, "check", "kill"]

        result = self._run_command(cmd, kwargs.get("timeout", 30))

        if result["success"]:
            result["parsed"] = {"processes_killed": True}

        return result

    def _parse_airomon_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Airomon-ng"""
        parsed = {
            "monitor_interface": "",
            "original_interface": "",
            "channel": "",
            "processes_killed": []
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            if "monitor mode enabled on" in line:
                match = re.search(r'monitor mode enabled on ([^\s]+)', line)
                if match:
                    parsed["monitor_interface"] = match.group(1)

            elif "monitor mode disabled on" in line:
                match = re.search(r'monitor mode disabled on ([^\s]+)', line)
                if match:
                    parsed["original_interface"] = match.group(1)

            elif "PID" in line and "Name" in line:
                continue  # En-tête
            elif line and any(char.isdigit() for char in line.split()[0] if line.split()):
                # Ligne de processus: PID Name
                parts = line.split()
                if len(parts) >= 2:
                    parsed["processes_killed"].append({
                        "pid": parts[0],
                        "name": " ".join(parts[1:])
                    })

        return parsed

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

# Gestionnaire unifié pour les outils sans fil
class WirelessToolsManager:
    """Gestionnaire unifié des outils sans fil"""

    def __init__(self):
        self.tools = {
            "aircrack-ng": AircrackNgWrapper(),
            "airodump-ng": AirodumpNgWrapper(),
            "aireplay-ng": AireplayNgWrapper(),
            "reaver": ReaverWrapper(),
            "bully": BullyWrapper(),
            "airomon-ng": AiromonNgWrapper()
        }

    def get_tool(self, name: str):
        """Récupère un outil par nom"""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """Liste tous les outils disponibles"""
        return list(self.tools.keys())

    def wireless_attack(self, method: str, **kwargs) -> Dict[str, Any]:
        """Effectue une attaque sans fil avec l'outil spécifié"""
        tool = self.get_tool(method)
        if not tool:
            return {"error": f"Unknown wireless method: {method}"}

        if method == "aircrack-ng":
            attack_type = kwargs.get("attack_type", "wep")
            if attack_type == "wep":
                return tool.crack_wep(**kwargs)
            elif attack_type == "wpa":
                return tool.crack_wpa(**kwargs)
        elif method == "airodump-ng":
            return tool.scan(**kwargs)
        elif method == "aireplay-ng":
            attack_type = kwargs.get("attack_type", "deauth")
            if attack_type == "deauth":
                return tool.deauth(**kwargs)
            elif attack_type == "fake_auth":
                return tool.fake_auth(**kwargs)
            elif attack_type == "arp_replay":
                return tool.arp_replay(**kwargs)
        elif method == "reaver":
            return tool.attack_wps(**kwargs)
        elif method == "bully":
            return tool.attack_wps(**kwargs)
        elif method == "airomon-ng":
            action = kwargs.get("action", "start")
            if action == "start":
                return tool.start_monitor(**kwargs)
            elif action == "stop":
                return tool.stop_monitor(**kwargs)
            elif action == "check_kill":
                return tool.check_kill(**kwargs)
        else:
            return {"error": f"Unsupported wireless method: {method}"}

def main():
    """Test des wrappers sans fil"""
    import argparse

    parser = argparse.ArgumentParser(description="Wireless Tools Wrappers")
    parser.add_argument("--tool", choices=["aircrack-ng", "airodump-ng", "aireplay-ng", "reaver", "bully", "airomon-ng"],
                       default="airodump-ng", help="Tool to use")
    parser.add_argument("--interface", "-i", help="Wireless interface")
    parser.add_argument("--bssid", "-b", help="Target BSSID")
    parser.add_argument("--essid", "-e", help="Target ESSID")
    parser.add_argument("--capture-file", "-c", help="Capture file (.cap)")
    parser.add_argument("--wordlist", "-w", help="Wordlist for cracking")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    manager = WirelessToolsManager()

    print(f"📡 Running {args.tool}...")

    kwargs = {
        "interface": args.interface,
        "bssid": args.bssid,
        "essid": args.essid,
        "capture_file": args.capture_file,
        "wordlist": args.wordlist,
        "output_file": args.output
    }

    # Supprimer les None
    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    result = manager.wireless_attack(args.tool, **kwargs)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        if result.get("success"):
            print("✅ Wireless operation completed successfully")
            if "parsed" in result:
                parsed = result["parsed"]
                if "key_found" in parsed and parsed["key_found"]:
                    print(f"🎯 Key found: {parsed['key']}")
                elif "access_points" in parsed:
                    print(f"Found {len(parsed['access_points'])} access points")
                elif "packets_sent" in parsed:
                    print(f"Sent {parsed['packets_sent']} packets")
                elif "wps_pin_found" in parsed and parsed["wps_pin_found"]:
                    print(f"🎯 WPS PIN found: {parsed['wps_pin']}")
                elif "monitor_interface" in parsed:
                    print(f"Monitor mode enabled: {parsed['monitor_interface']}")
        else:
            print(f"❌ Wireless operation failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()