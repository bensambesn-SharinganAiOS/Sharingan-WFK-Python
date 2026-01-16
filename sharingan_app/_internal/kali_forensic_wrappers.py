#!/usr/bin/env python3
"""
Sharingan OS - Kali Forensic Tools Wrappers
Wrappers Python pour tous les outils forensics Kali Linux
"""

import subprocess
import sys
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

class BinwalkWrapper:
    """Wrapper Python pour Binwalk"""

    def __init__(self):
        self.command = "binwalk"

    def analyze_file(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Analyse un fichier avec Binwalk"""
        cmd = [self.command, file_path]

        # Options supplémentaires
        if kwargs.get("extract"):
            cmd.append("-e")
        if kwargs.get("signature_scan"):
            cmd.append("-B")
        if kwargs.get("opcodes_scan"):
            cmd.append("-A")
        if kwargs.get("entropy_analysis"):
            cmd.append("-E")
        if kwargs.get("output_file"):
            cmd.extend(["-f", kwargs["output_file"]])
        if kwargs.get("verbose"):
            cmd.append("-v")

        result = self._run_command(cmd, kwargs.get("timeout", 300))

        if result["success"]:
            result["parsed"] = self._parse_binwalk_output(result["stdout"])

        return result

    def extract_files(self, file_path: str, output_dir: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Extrait les fichiers d'un firmware"""
        cmd = [self.command, "-e", file_path]

        if output_dir:
            cmd.extend(["-C", output_dir])

        result = self._run_command(cmd, kwargs.get("timeout", 600))

        if result["success"]:
            result["extraction_complete"] = True

        return result

    def _parse_binwalk_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Binwalk"""
        parsed = {
            "signatures": [],
            "entropy": {},
            "opcodes": {},
            "extracted_files": []
        }

        lines = output.split('\n')

        for line in lines:
            line = line.strip()

            # Ligne de signature: DECIMAL       HEXADECIMAL     DESCRIPTION
            if re.match(r'^\d+\s+0x[0-9A-F]+\s+.+', line):
                parts = line.split(None, 2)
                if len(parts) >= 3:
                    signature = {
                        "offset_decimal": int(parts[0]),
                        "offset_hex": parts[1],
                        "description": parts[2]
                    }
                    parsed["signatures"].append(signature)

            # Analyse d'entropie
            elif "Entropy:" in line:
                match = re.search(r'Entropy:\s*([\d.]+)', line)
                if match:
                    parsed["entropy"]["value"] = float(match.group(1))

        return parsed

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

class ForemostWrapper:
    """Wrapper Python pour Foremost"""

    def __init__(self):
        self.command = "foremost"

    def carve_files(self, image_file: str, output_dir: str, **kwargs) -> Dict[str, Any]:
        """Carve des fichiers depuis une image"""
        cmd = [self.command, "-i", image_file, "-o", output_dir]

        # Options supplémentaires
        if kwargs.get("config_file"):
            cmd.extend(["-c", kwargs["config_file"]])
        if kwargs.get("all_files"):
            cmd.append("-a")
        if kwargs.get("verbose"):
            cmd.append("-v")
        if kwargs.get("quick_mode"):
            cmd.append("-q")

        result = self._run_command(cmd, kwargs.get("timeout", 600))

        if result["success"]:
            result["parsed"] = self._parse_foremost_output(output_dir, result["stdout"])

        return result

    def _parse_foremost_output(self, output_dir: str, output: str) -> Dict[str, Any]:
        """Parse la sortie Foremost"""
        parsed = {
            "output_directory": output_dir,
            "audit_file": os.path.join(output_dir, "audit.txt"),
            "carved_files": {}
        }

        # Lire le fichier audit
        audit_file = parsed["audit_file"]
        if os.path.exists(audit_file):
            with open(audit_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Format: FILE: type offset length
                        match = re.search(r'FILE:\s+(\w+)\s+(\d+)\s+(\d+)', line)
                        if match:
                            file_type = match.group(1)
                            offset = int(match.group(2))
                            length = int(match.group(3))

                            if file_type not in parsed["carved_files"]:
                                parsed["carved_files"][file_type] = []

                            parsed["carved_files"][file_type].append({
                                "offset": offset,
                                "length": length
                            })

        # Compter les fichiers extraits
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file != "audit.txt":
                    file_path = os.path.join(root, file)
                    file_type = os.path.basename(root)
                    if file_type not in parsed["carved_files"]:
                        parsed["carved_files"][file_type] = []
                    parsed["carved_files"][file_type].append(file_path)

        return parsed

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

class VolatilityWrapper:
    """Wrapper Python pour Volatility"""

    def __init__(self):
        self.command = "volatility"

    def analyze_memory(self, memory_file: str, profile: str, plugin: str, **kwargs) -> Dict[str, Any]:
        """Analyse un fichier de mémoire"""
        cmd = [self.command, "-f", memory_file, "--profile", profile, plugin]

        # Options supplémentaires
        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])
        if kwargs.get("verbose"):
            cmd.append("-v")
        if kwargs.get("debug"):
            cmd.append("-d")

        result = self._run_command(cmd, kwargs.get("timeout", 300))

        if result["success"]:
            result["parsed"] = self._parse_volatility_output(result["stdout"], plugin)

        return result

    def list_plugins(self, **kwargs) -> Dict[str, Any]:
        """Liste les plugins disponibles"""
        cmd = [self.command, "--info"]

        result = self._run_command(cmd, kwargs.get("timeout", 60))

        if result["success"]:
            result["parsed"] = self._parse_volatility_plugins(result["stdout"])

        return result

    def identify_profile(self, memory_file: str, **kwargs) -> Dict[str, Any]:
        """Identifie le profil du fichier de mémoire"""
        cmd = [self.command, "-f", memory_file, "imageinfo"]

        result = self._run_command(cmd, kwargs.get("timeout", 120))

        if result["success"]:
            result["parsed"] = self._parse_volatility_profile(result["stdout"])

        return result

    def _parse_volatility_output(self, output: str, plugin: str) -> Dict[str, Any]:
        """Parse la sortie Volatility selon le plugin"""
        parsed = {
            "plugin": plugin,
            "data": []
        }

        lines = output.split('\n')

        # Parsing spécifique selon le plugin
        if plugin == "pslist":
            # Process list
            for line in lines:
                if re.match(r'^\d+\s+\w+', line):
                    parts = line.split()
                    if len(parts) >= 4:
                        process = {
                            "offset": parts[0],
                            "name": parts[1],
                            "pid": int(parts[2]),
                            "ppid": int(parts[3]),
                            "threads": int(parts[4]) if len(parts) > 4 else 0,
                            "handles": int(parts[5]) if len(parts) > 5 else 0,
                            "session": int(parts[6]) if len(parts) > 6 else 0,
                            "wow64": parts[7] if len(parts) > 7 else "",
                            "start_time": " ".join(parts[8:]) if len(parts) > 8 else ""
                        }
                        parsed["data"].append(process)

        elif plugin == "netscan":
            # Network connections
            for line in lines:
                if "TCP" in line or "UDP" in line:
                    parts = line.split()
                    if len(parts) >= 6:
                        connection = {
                            "protocol": parts[0],
                            "local_addr": parts[1],
                            "remote_addr": parts[2],
                            "state": parts[3],
                            "pid": int(parts[4]) if parts[4].isdigit() else 0,
                            "owner": parts[5] if len(parts) > 5 else "",
                            "created": " ".join(parts[6:]) if len(parts) > 6 else ""
                        }
                        parsed["data"].append(connection)

        else:
            # Parsing générique
            parsed["raw_output"] = output

        return parsed

    def _parse_volatility_plugins(self, output: str) -> List[str]:
        """Parse la liste des plugins"""
        plugins = []

        lines = output.split('\n')
        in_plugins = False

        for line in lines:
            line = line.strip()

            if "Supported Plugin Commands:" in line:
                in_plugins = True
                continue

            if in_plugins and line and not line.startswith('---'):
                plugin_match = re.match(r'^(\w+)', line)
                if plugin_match:
                    plugins.append(plugin_match.group(1))

        return plugins

    def _parse_volatility_profile(self, output: str) -> Dict[str, Any]:
        """Parse les informations de profil"""
        parsed = {
            "suggested_profiles": [],
            "image_info": {}
        }

        lines = output.split('\n')

        for line in lines:
            line = line.strip()

            if "Suggested Profile(s)" in line:
                continue
            elif "AS Layer" in line or "PAE type" in line or "DTB" in line:
                key_value = line.split(':', 1)
                if len(key_value) == 2:
                    parsed["image_info"][key_value[0].strip()] = key_value[1].strip()
            elif re.match(r'^\w+/\w+', line):
                # Profil suggéré
                parsed["suggested_profiles"].append(line.split()[0])

        return parsed

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

class AutopsyWrapper:
    """Wrapper Python pour Autopsy"""

    def __init__(self):
        self.command = "autopsy"

    def start_autopsy(self, case_dir: str = None, **kwargs) -> Dict[str, Any]:
        """Démarre Autopsy"""
        cmd = [self.command]

        if case_dir:
            cmd.extend(["--case", case_dir])

        # Autopsy est une interface graphique, on retourne les infos de lancement
        return {
            "success": True,
            "command": " ".join(cmd),
            "message": "Autopsy GUI started. Use --case option to specify case directory.",
            "gui": True
        }

class ScalpelWrapper:
    """Wrapper Python pour Scalpel"""

    def __init__(self):
        self.command = "scalpel"

    def carve_files(self, image_file: str, config_file: str = None, output_dir: str = None, **kwargs) -> Dict[str, Any]:
        """Carve des fichiers avec Scalpel"""
        cmd = [self.command]

        if config_file:
            cmd.extend(["-c", config_file])
        else:
            # Utiliser la config par défaut
            cmd.extend(["-c", "/etc/scalpel/scalpel.conf"])

        cmd.extend([image_file])

        if output_dir:
            cmd.extend(["-o", output_dir])

        result = self._run_command(cmd, kwargs.get("timeout", 600))

        if result["success"]:
            result["parsed"] = self._parse_scalpel_output(output_dir or "scalpel-output", result["stdout"])

        return result

    def _parse_scalpel_output(self, output_dir: str, output: str) -> Dict[str, Any]:
        """Parse la sortie Scalpel"""
        parsed = {
            "output_directory": output_dir,
            "carved_files": {}
        }

        # Analyser le répertoire de sortie
        if os.path.exists(output_dir):
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        file_type = os.path.basename(root)

                        if file_type not in parsed["carved_files"]:
                            parsed["carved_files"][file_type] = []

                        parsed["carved_files"][file_type].append(file_path)

        return parsed

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

# Gestionnaire unifié pour les outils forensics
class ForensicToolsManager:
    """Gestionnaire unifié des outils forensics"""

    def __init__(self):
        self.tools = {
            "binwalk": BinwalkWrapper(),
            "foremost": ForemostWrapper(),
            "volatility": VolatilityWrapper(),
            "autopsy": AutopsyWrapper(),
            "scalpel": ScalpelWrapper()
        }

    def get_tool(self, name: str):
        """Récupère un outil par nom"""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """Liste tous les outils disponibles"""
        return list(self.tools.keys())

    def analyze_file(self, file_path: str, tool: str = "binwalk", **kwargs) -> Dict[str, Any]:
        """Analyse un fichier avec l'outil spécifié"""
        tool_instance = self.get_tool(tool)
        if not tool_instance:
            return {"error": f"Unknown forensic tool: {tool}"}

        if tool == "binwalk":
            return tool_instance.analyze_file(file_path, **kwargs)
        elif tool == "volatility":
            profile = kwargs.get("profile", "Win7SP1x64")
            plugin = kwargs.get("plugin", "pslist")
            return tool_instance.analyze_memory(file_path, profile, plugin, **kwargs)
        else:
            return {"error": f"Unsupported analysis tool: {tool}"}

    def carve_files(self, image_file: str, tool: str = "foremost", **kwargs) -> Dict[str, Any]:
        """Carve des fichiers depuis une image"""
        tool_instance = self.get_tool(tool)
        if not tool_instance:
            return {"error": f"Unknown carving tool: {tool}"}

        if tool == "foremost":
            output_dir = kwargs.get("output_dir", f"foremost_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            return tool_instance.carve_files(image_file, output_dir, **kwargs)
        elif tool == "scalpel":
            output_dir = kwargs.get("output_dir", f"scalpel_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            return tool_instance.carve_files(image_file, None, output_dir, **kwargs)
        else:
            return {"error": f"Unsupported carving tool: {tool}"}

def get_forensic_tools_manager():
    """Get forensic tools manager instance"""
    return ForensicToolsManager()

def main():
    """Test des wrappers forensics"""
    import argparse

    parser = argparse.ArgumentParser(description="Forensic Tools Wrappers")
    parser.add_argument("--tool", choices=["binwalk", "foremost", "volatility", "autopsy", "scalpel"],
                       default="binwalk", help="Tool to use")
    parser.add_argument("--action", choices=["analyze", "carve", "start"], default="analyze",
                       help="Action to perform")
    parser.add_argument("target", help="Target file/image")
    parser.add_argument("--output", "-o", help="Output directory/file")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    manager = ForensicToolsManager()

    print(f"🔍 Running {args.tool} {args.action}...")

    result = {"error": "Unsupported action/tool combination"}

    if args.action == "analyze":
        result = manager.analyze_file(args.target, args.tool, output_file=args.output)
    elif args.action == "carve":
        result = manager.carve_files(args.target, args.tool, output_dir=args.output)
    elif args.action == "start" and args.tool == "autopsy":
        result = manager.get_tool("autopsy").start_autopsy(args.target if args.target != "none" else None)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        if result.get("success"):
            print("✅ Forensic operation completed successfully")
            if "parsed" in result:
                parsed = result["parsed"]
                if "signatures" in parsed:
                    print(f"Found {len(parsed['signatures'])} signatures")
                elif "carved_files" in parsed:
                    total_files = sum(len(files) for files in parsed["carved_files"].values())
                    print(f"Carved {total_files} files")
                elif "data" in parsed:
                    print(f"Found {len(parsed['data'])} items")
        else:
            print(f"❌ Forensic operation failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
