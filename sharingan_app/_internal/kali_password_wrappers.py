#!/usr/bin/env python3
"""
Sharingan OS - Password Cracking Tools Wrappers
Wrappers Python pour tous les outils de mot de passe Kali Linux
"""

import subprocess
import sys
import os
import json
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import threading

class HashcatWrapper:
    """Wrapper Python pour Hashcat"""

    def __init__(self):
        self.command = "hashcat"
        self.name = "hashcat"
        self.description = "Advanced password recovery"

    def crack(self, hash_file: str, wordlist: str = "/usr/share/wordlists/rockyou.txt",
              hash_type: int = 0, **kwargs) -> Dict[str, Any]:
        """Effectue un cracking avec Hashcat"""
        cmd = [self.command, "-m", str(hash_type), hash_file, wordlist]

        # Options supplémentaires
        if kwargs.get("attack_mode"):
            cmd.extend(["-a", str(kwargs["attack_mode"])])
        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])
        if kwargs.get("potfile_path"):
            cmd.extend(["--potfile-path", kwargs["potfile_path"]])
        if kwargs.get("status"):
            cmd.append("--status")
        if kwargs.get("force"):
            cmd.append("--force")
        if kwargs.get("quiet"):
            cmd.append("--quiet")

        result = self._run_command(cmd, kwargs.get("timeout", 3600))

        if result["success"]:
            result["parsed"] = self._parse_hashcat_output(result["stdout"])

        return result

    def benchmark(self, hash_type: int = 0, **kwargs) -> Dict[str, Any]:
        """Effectue un benchmark Hashcat"""
        cmd = [self.command, "-b", "-m", str(hash_type)]

        if kwargs.get("device"):
            cmd.extend(["-d", str(kwargs["device"])])
        if kwargs.get("workload_profile"):
            cmd.extend(["-w", str(kwargs["workload_profile"])])

        result = self._run_command(cmd, kwargs.get("timeout", 300))

        if result["success"]:
            result["parsed"] = self._parse_hashcat_benchmark(result["stdout"])

        return result

    def _parse_hashcat_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Hashcat"""
        parsed = {
            "status": "",
            "progress": "",
            "speed": "",
            "recovered": 0,
            "total": 0,
            "time_remaining": "",
            "cracked_hashes": []
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            if "Status........:" in line:
                parsed["status"] = line.split(":", 1)[1].strip()
            elif "Progress.........:" in line:
                parsed["progress"] = line.split(":", 1)[1].strip()
            elif "Speed...........:" in line:
                parsed["speed"] = line.split(":", 1)[1].strip()
            elif "Recovered........:" in line:
                recovered_match = re.search(r'(\d+)/(\d+)', line.split(":", 1)[1].strip())
                if recovered_match:
                    parsed["recovered"] = int(recovered_match.group(1))
                    parsed["total"] = int(recovered_match.group(2))
            elif "Time.Estimated..:" in line:
                parsed["time_remaining"] = line.split(":", 1)[1].strip()
            elif ":" in line and len(line.split(":")) >= 2:
                # Ligne de hash cracké: hash:password
                parts = line.split(":", 1)
                if len(parts) == 2:
                    parsed["cracked_hashes"].append({
                        "hash": parts[0],
                        "password": parts[1]
                    })

        return parsed

    def _parse_hashcat_benchmark(self, output: str) -> Dict[str, Any]:
        """Parse la sortie benchmark Hashcat"""
        parsed = {
            "device": "",
            "hashtype": "",
            "speed": "",
            "exec_runtime": "",
            "power_consumption": ""
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            if "Device...........:" in line:
                parsed["device"] = line.split(":", 1)[1].strip()
            elif "Hash.Type.........:" in line:
                parsed["hashtype"] = line.split(":", 1)[1].strip()
            elif "Speed.#*...........:" in line:
                parsed["speed"] = line.split(":", 1)[1].strip()
            elif "Exec.Runtime......:" in line:
                parsed["exec_runtime"] = line.split(":", 1)[1].strip()
            elif "Power.Consumption.:" in line:
                parsed["power_consumption"] = line.split(":", 1)[1].strip()

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

class JohnWrapper:
    """Wrapper Python pour John the Ripper"""

    def __init__(self):
        self.command = "john"
        self.name = "john"
        self.description = "John the Ripper password cracker"

    def crack(self, hash_file: str, **kwargs) -> Dict[str, Any]:
        """Effectue un cracking avec John"""
        cmd = [self.command, hash_file]

        # Options supplémentaires
        if kwargs.get("wordlist"):
            cmd.extend(["--wordlist", kwargs["wordlist"]])
        if kwargs.get("format"):
            cmd.extend(["--format", kwargs["format"]])
        if kwargs.get("session"):
            cmd.extend(["--session", kwargs["session"]])
        if kwargs.get("fork"):
            cmd.extend(["--fork", str(kwargs["fork"])])
        if kwargs.get("verbose"):
            cmd.append("--verbose")

        result = self._run_command(cmd, kwargs.get("timeout", 3600))

        if result["success"]:
            result["parsed"] = self._parse_john_output(result["stdout"])

        return result

    def show_cracked(self, hash_file: str, **kwargs) -> Dict[str, Any]:
        """Affiche les mots de passe crackés"""
        cmd = [self.command, "--show", hash_file]

        result = self._run_command(cmd, kwargs.get("timeout", 60))

        if result["success"]:
            result["parsed"] = self._parse_john_show(result["stdout"])

        return result

    def _parse_john_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie John"""
        parsed = {
            "loaded": 0,
            "guesses": 0,
            "progress": "",
            "cracked_hashes": []
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            if "Loaded" in line and "password hash" in line:
                match = re.search(r'(\d+) password hash', line)
                if match:
                    parsed["loaded"] = int(match.group(1))

            elif "guesses:" in line:
                match = re.search(r'(\d+) guesses', line)
                if match:
                    parsed["guesses"] = int(match.group(1))

            elif ":" in line and len(line.split(":")) >= 2:
                # Ligne de hash cracké: user:password
                parts = line.split(":", 1)
                if len(parts) == 2 and parts[1]:
                    parsed["cracked_hashes"].append({
                        "user": parts[0],
                        "password": parts[1]
                    })

        return parsed

    def _parse_john_show(self, output: str) -> List[Dict[str, Any]]:
        """Parse la sortie john --show"""
        cracked = []

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            if ":" in line and len(line.split(":")) >= 2:
                parts = line.split(":", 1)
                if len(parts) == 2 and parts[1]:
                    cracked.append({
                        "user": parts[0],
                        "password": parts[1]
                    })

        return cracked

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

class HydraWrapper:
    """Wrapper Python pour Hydra"""

    def __init__(self):
        self.command = "hydra"
        self.name = "hydra"
        self.description = "Network login cracker"

    def crack(self, target: str, service: str, login_file: Optional[str] = None,
              password_file: Optional[str] = None, login: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Effectue un cracking avec Hydra"""
        cmd = [self.command, "-t", "4", "-f"]

        # Service
        if service == "http-post-form":
            cmd.extend(["-l", login or "admin", "-P", password_file or "/usr/share/wordlists/rockyou.txt"])
            cmd.extend([f"{service}://{target}", kwargs.get("form_path", "/login")])
            cmd.extend(["username=^USER^&password=^PASS^", kwargs.get("form_condition", "F=invalid")])
        elif service in ["ssh", "ftp", "telnet", "smtp", "pop3", "imap"]:
            cmd.extend(["-l", login or "admin", "-P", password_file or "/usr/share/wordlists/rockyou.txt"])
            cmd.extend([f"{service}://{target}"])
        else:
            return {"error": f"Unsupported service: {service}"}

        # Options supplémentaires
        if kwargs.get("tasks"):
            cmd.extend(["-t", str(kwargs["tasks"])])
        if kwargs.get("verbose"):
            cmd.extend(["-v", "-V"])
        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])

        result = self._run_command(cmd, kwargs.get("timeout", 3600))

        if result["success"]:
            result["parsed"] = self._parse_hydra_output(result["stdout"])

        return result

    def _parse_hydra_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Hydra"""
        parsed = {
            "hosts": 0,
            "login_attempts": 0,
            "successes": 0,
            "valid_credentials": []
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            if "hosts:" in line:
                match = re.search(r'(\d+) hosts', line)
                if match:
                    parsed["hosts"] = int(match.group(1))

            elif "login attempts:" in line:
                match = re.search(r'(\d+) login attempts', line)
                if match:
                    parsed["login_attempts"] = int(match.group(1))

            elif "successes:" in line:
                match = re.search(r'(\d+) successes', line)
                if match:
                    parsed["successes"] = int(match.group(1))

            elif "[http-post-form]" in line and "login:" in line and "password:" in line:
                # Ligne de succès: [http-post-form] host: ip login: user password: pass
                match = re.search(r'host:\s*([^\s]+).*login:\s*([^\s]+).*password:\s*([^\s]+)', line)
                if match:
                    parsed["valid_credentials"].append({
                        "host": match.group(1),
                        "login": match.group(2),
                        "password": match.group(3)
                    })

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

class MedusaWrapper:
    """Wrapper Python pour Medusa"""

    def __init__(self):
        self.command = "medusa"
        self.name = "medusa"
        self.description = "Modular login brute-forcer"

    def crack(self, host: str, user: str = None, password_file: str = None,
              module: str = "ssh", **kwargs) -> Dict[str, Any]:
        """Effectue un cracking avec Medusa"""

        # Utilisation de valeurs sécurisées depuis l'environnement
        if user is None:
            user = os.environ.get('MEDUSA_DEFAULT_USER', 'admin')
        if password_file is None:
            password_file = os.environ.get('MEDUSA_DEFAULT_PASSWORDLIST', '/usr/share/wordlists/rockyou.txt')

        # Validation des inputs
        if not host:
            return {"success": False, "error": "Host required"}
        if not os.path.isfile(password_file) or not os.access(password_file, os.R_OK):
            return {"success": False, "error": f"Invalid or inaccessible password file: {password_file}"}
        cmd = [
            self.command,
            "-h", host,
            "-u", user,
            "-P", password_file,
            "-M", module
        ]

        # Options supplémentaires
        if kwargs.get("threads"):
            cmd.extend(["-t", str(kwargs["threads"])])
        if kwargs.get("output_file"):
            cmd.extend(["-O", kwargs["output_file"]])
        if kwargs.get("verbose"):
            cmd.extend(["-v", "6"])
        if kwargs.get("brute"):
            cmd.append("-b")

        result = self._run_command(cmd, kwargs.get("timeout", 1800))

        if result["success"]:
            result["parsed"] = self._parse_medusa_output(result["stdout"])

        return result

    def _parse_medusa_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Medusa"""
        parsed = {
            "success": False,
            "credentials": None,
            "attempts": 0,
            "errors": 0
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            if "SUCCESS" in line:
                parsed["success"] = True
                # Extraire les credentials
                match = re.search(r'SUCCESS.*\[([^]]+)\]', line)
                if match:
                    parsed["credentials"] = match.group(1)

            elif "attempts:" in line:
                match = re.search(r'(\d+) attempts', line)
                if match:
                    parsed["attempts"] = int(match.group(1))

            elif "ERROR:" in line:
                parsed["errors"] += 1

        return parsed

    def _run_command(self, cmd: List[str], timeout: int = 1800) -> Dict[str, Any]:
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

class PatatorWrapper:
    """Wrapper Python pour Patator"""

    def __init__(self):
        self.command = "patator"
        self.name = "patator"
        self.description = "Multi-purpose brute-forcer"

    def brute_force(self, module: str, target: str, **kwargs) -> Dict[str, Any]:
        """Effectue un brute force avec Patator"""
        cmd = [self.command, module, f"url={target}"]

        # Configuration selon le module
        if module == "http_fuzz":
            cmd.extend([
                "method=POST",
                "body=username=admin&password=FILE0",
                f"0={kwargs.get('password_file', '/usr/share/wordlists/rockyou.txt')}",
                "follow=0",
                "-x", "ignore:fgrep='invalid'"
            ])
        elif module == "ftp_login":
            cmd.extend([
                "user=root",
                f"password=FILE0",
                f"0={kwargs.get('password_file', '/usr/share/wordlists/rockyou.txt')}"
            ])
        elif module == "ssh_login":
            cmd.extend([
                "user=root",
                f"password=FILE0",
                f"0={kwargs.get('password_file', '/usr/share/wordlists/rockyou.txt')}"
            ])

        # Options générales
        if kwargs.get("threads"):
            cmd.extend(["-x", f"threads={kwargs['threads']}"])
        if kwargs.get("output_file"):
            cmd.extend(["-l", kwargs["output_file"]])
        if kwargs.get("verbose"):
            cmd.append("-v")

        result = self._run_command(cmd, kwargs.get("timeout", 1800))

        if result["success"]:
            result["parsed"] = self._parse_patator_output(result["stdout"])

        return result

    def _parse_patator_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Patator"""
        parsed = {
            "successful_attempts": [],
            "failed_attempts": 0,
            "total_attempts": 0
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            if "INFO" in line and "hits:" in line:
                match = re.search(r'hits:\s*(\d+)', line)
                if match:
                    parsed["total_attempts"] = int(match.group(1))

            elif "successful" in line.lower():
                parsed["successful_attempts"].append(line)

        return parsed

    def _run_command(self, cmd: List[str], timeout: int = 1800) -> Dict[str, Any]:
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

class CrunchWrapper:
    """Wrapper Python pour Crunch"""

    def __init__(self):
        self.command = "crunch"
        self.name = "crunch"
        self.description = "Wordlist generator"

    def generate(self, min_length: int, max_length: int, charset: str = "abcdefghijklmnopqrstuvwxyz",
                **kwargs) -> Dict[str, Any]:
        """Génère une wordlist avec Crunch"""
        cmd = [self.command, str(min_length), str(max_length), charset]

        # Options supplémentaires
        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])
        if kwargs.get("pattern"):
            cmd.extend(["-t", kwargs["pattern"]])
        if kwargs.get("start_block"):
            cmd.extend(["-s", kwargs["start_block"]])
        if kwargs.get("count"):
            cmd.extend(["-c", str(kwargs["count"])])
        if kwargs.get("invert"):
            cmd.append("-i")

        result = self._run_command(cmd, kwargs.get("timeout", 600))

        if result["success"]:
            result["parsed"] = self._parse_crunch_output(result["stdout"])

        return result

    def _parse_crunch_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Crunch"""
        parsed = {
            "generated_words": 0,
            "charset": "",
            "pattern": "",
            "sample_words": []
        }

        lines = output.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()

            if "Crunch will now generate" in line:
                match = re.search(r'generate (\d+) words', line)
                if match:
                    parsed["generated_words"] = int(match.group(1))

            elif "charset:" in line:
                parsed["charset"] = line.split(":", 1)[1].strip()

            elif "pattern:" in line:
                parsed["pattern"] = line.split(":", 1)[1].strip()

            # Collecter quelques mots d'exemple
            if i > 10 and len(parsed["sample_words"]) < 10 and line and not line.startswith("Crunch"):
                parsed["sample_words"].append(line)

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

# Gestionnaire unifié pour les outils de mot de passe
class PasswordToolsManager:
    """Gestionnaire unifié des outils de mot de passe"""

    def __init__(self):
        self.tools = {
            "hashcat": HashcatWrapper(),
            "john": JohnWrapper(),
            "hydra": HydraWrapper(),
            "medusa": MedusaWrapper(),
            "patator": PatatorWrapper(),
            "crunch": CrunchWrapper()
        }

    def get_tool(self, name: str):
        """Récupère un outil par nom"""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """Liste tous les outils disponibles"""
        return list(self.tools.keys())

    def crack_passwords(self, method: str, **kwargs) -> Dict[str, Any]:
        """Effectue un cracking avec l'outil spécifié"""
        tool = self.get_tool(method)
        if not tool:
            return {"error": f"Unknown password cracking method: {method}"}

        if method == "hashcat":
            return tool.crack(**kwargs)
        elif method == "john":
            return tool.crack(**kwargs)
        elif method == "hydra":
            return tool.crack(**kwargs)
        elif method == "medusa":
            return tool.crack(**kwargs)
        elif method == "patator":
            return tool.brute_force(**kwargs)
        elif method == "crunch":
            return tool.generate(**kwargs)
        else:
            return {"error": f"Unsupported password cracking method: {method}"}

def main():
    """Test des wrappers de mot de passe"""
    import argparse

    parser = argparse.ArgumentParser(description="Password Cracking Tools Wrappers")
    parser.add_argument("--tool", choices=["hashcat", "john", "hydra", "medusa", "patator", "crunch"],
                       default="hashcat", help="Tool to use")
    parser.add_argument("--hash-file", help="Hash file (for hashcat/john)")
    parser.add_argument("--target", help="Target (for hydra/medusa)")
    parser.add_argument("--wordlist", help="Wordlist file")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    manager = PasswordToolsManager()

    print(f"🔐 Running {args.tool}...")

    if args.tool in ["hashcat", "john"]:
        if not args.hash_file:
            print("Error: --hash-file required for hashcat/john")
            sys.exit(1)
        result = manager.crack_passwords(args.tool, hash_file=args.hash_file,
                                       wordlist=args.wordlist, output_file=args.output)
    elif args.tool in ["hydra", "medusa"]:
        if not args.target:
            print("Error: --target required for hydra/medusa")
            sys.exit(1)
        result = manager.crack_passwords(args.tool, target=args.target,
                                       password_file=args.wordlist, output_file=args.output)
    elif args.tool == "patator":
        result = manager.crack_passwords(args.tool, module="http_fuzz",
                                       target=args.target or "http://example.com/login",
                                       password_file=args.wordlist)
    elif args.tool == "crunch":
        result = manager.crack_passwords(args.tool, min_length=6, max_length=8,
                                       output_file=args.output)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        if result.get("success"):
            print("✅ Password cracking completed")
            if "parsed" in result:
                parsed = result["parsed"]
                if "cracked_hashes" in parsed:
                    print(f"Cracked {len(parsed['cracked_hashes'])} passwords")
                elif "success" in parsed:
                    print(f"Success: {parsed['success']}")
                elif "generated_words" in parsed:
                    print(f"Generated {parsed['generated_words']} words")
        else:
            print(f"❌ Password cracking failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()