#!/usr/bin/env python3
"""
Sharingan OS - Web Application Tools Wrappers
Wrappers Python pour tous les outils web Kali Linux
"""

import subprocess
import sys
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import requests
import urllib.parse

class NiktoWrapper:
    """Wrapper Python pour Nikto"""

    def __init__(self):
        self.command = "nikto"
        self.name = "nikto"
        self.description = "Web server scanner"

    def scan(self, url: str, **kwargs) -> Dict[str, Any]:
        """Effectue un scan Nikto"""
        cmd = [self.command, "-h", url]

        # Options supplémentaires
        if kwargs.get("port"):
            cmd.extend(["-p", str(kwargs["port"])])
        if kwargs.get("ssl"):
            cmd.append("-ssl")
        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])
        if kwargs.get("format"):
            cmd.extend(["-Format", kwargs["format"]])
        if kwargs.get("tuning"):
            cmd.extend(["-Tuning", kwargs["tuning"]])
        if kwargs.get("evasion"):
            cmd.extend(["-evasion", str(kwargs["evasion"])])

        result = self._run_command(cmd, kwargs.get("timeout", 600))

        if result["success"]:
            result["parsed"] = self._parse_nikto_output(result["stdout"])

        return result

    def _parse_nikto_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Nikto"""
        parsed = {
            "target": "",
            "server_info": {},
            "vulnerabilities": [],
            "items_checked": 0,
            "items_found": 0
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            if "Target IP:" in line:
                parsed["target"] = line.split(":", 1)[1].strip()
            elif "Target Hostname:" in line:
                parsed["target"] = line.split(":", 1)[1].strip()
            elif "Target Port:" in line:
                parsed["server_info"]["port"] = line.split(":", 1)[1].strip()
            elif "Server:" in line:
                parsed["server_info"]["server"] = line.split(":", 1)[1].strip()
            elif "+" in line and "vulnerable" in line.lower():
                parsed["vulnerabilities"].append({
                    "type": "vulnerability",
                    "description": line[1:].strip()
                })
            elif "+" in line:
                parsed["vulnerabilities"].append({
                    "type": "info",
                    "description": line[1:].strip()
                })
            elif "items checked:" in line.lower():
                match = re.search(r'(\d+) items checked', line, re.IGNORECASE)
                if match:
                    parsed["items_checked"] = int(match.group(1))
            elif "items found:" in line.lower():
                match = re.search(r'(\d+) items found', line, re.IGNORECASE)
                if match:
                    parsed["items_found"] = int(match.group(1))

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

class DirbWrapper:
    """Wrapper Python pour Dirb"""

    def __init__(self):
        self.command = "dirb"
        self.name = "dirb"
        self.description = "Web content scanner"

    def scan(self, url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt", **kwargs) -> Dict[str, Any]:
        """Effectue un scan Dirb"""
        cmd = [self.command, url, wordlist]

        # Options supplémentaires
        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])
        if kwargs.get("extensions"):
            cmd.extend(["-X", kwargs["extensions"]])
        if kwargs.get("recursive"):
            cmd.append("-r")
        if kwargs.get("case_sensitive"):
            cmd.append("-i")
        if kwargs.get("not_recursive"):
            cmd.append("-R")
        if kwargs.get("silent"):
            cmd.append("-S")

        result = self._run_command(cmd, kwargs.get("timeout", 300))

        if result["success"]:
            result["parsed"] = self._parse_dirb_output(result["stdout"])

        return result

    def _parse_dirb_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Dirb"""
        parsed = {
            "directories": [],
            "files": [],
            "code_stats": {}
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            # Ligne de résultat: + http://example.com/admin/ (CODE:200|SIZE:1234)
            if line.startswith('+') and 'CODE:' in line:
                match = re.search(r'\+ (.+?) \(CODE:(\d+)\|SIZE:(\d+)\)', line)
                if match:
                    url = match.group(1)
                    code = int(match.group(2))
                    size = int(match.group(3))

                    item = {
                        "url": url,
                        "code": code,
                        "size": size
                    }

                    # Compter par code
                    if code not in parsed["code_stats"]:
                        parsed["code_stats"][code] = 0
                    parsed["code_stats"][code] += 1

                    # Classifier
                    if url.endswith('/'):
                        parsed["directories"].append(item)
                    else:
                        parsed["files"].append(item)

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

class DirsearchWrapper:
    """Wrapper Python pour Dirsearch"""

    def __init__(self):
        self.command = "dirsearch"
        self.name = "dirsearch"
        self.description = "Web path discovery"

    def scan(self, url: str, **kwargs) -> Dict[str, Any]:
        """Effectue un scan Dirsearch"""
        cmd = [self.command, "-u", url]

        # Options supplémentaires
        if kwargs.get("wordlist"):
            cmd.extend(["-w", kwargs["wordlist"]])
        if kwargs.get("extensions"):
            cmd.extend(["-e", kwargs["extensions"]])
        if kwargs.get("threads"):
            cmd.extend(["-t", str(kwargs["threads"])])
        if kwargs.get("output_file"):
            cmd.extend(["--output", kwargs["output_file"]])
        if kwargs.get("json_output"):
            cmd.append("--json-report")
        if kwargs.get("recursive"):
            cmd.extend(["-r", str(kwargs["recursive"])])
        if kwargs.get("exclude_status"):
            cmd.extend(["--exclude-status", kwargs["exclude_status"]])

        result = self._run_command(cmd, kwargs.get("timeout", 600))

        if result["success"]:
            result["parsed"] = self._parse_dirsearch_output(result["stdout"])

        return result

    def _parse_dirsearch_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Dirsearch"""
        parsed = {
            "results": [],
            "statistics": {
                "total_requests": 0,
                "errors": 0,
                "duration": ""
            }
        }

        lines = output.split('\n')
        in_results = False

        for line in lines:
            line = line.strip()

            if line.startswith('[') and ']' in line and ('http' in line.lower() or '/' in line):
                # Ligne de résultat: [14:32:45] http://example.com/admin/ (200 OK)
                match = re.search(r'\[([^\]]+)\] (.+?) \((\d+) ([^\)]+)\)', line)
                if match:
                    timestamp = match.group(1)
                    url = match.group(2)
                    code = int(match.group(3))
                    status = match.group(4)

                    parsed["results"].append({
                        "timestamp": timestamp,
                        "url": url,
                        "code": code,
                        "status": status
                    })

            elif "Total requests:" in line:
                match = re.search(r'Total requests: (\d+)', line)
                if match:
                    parsed["statistics"]["total_requests"] = int(match.group(1))

            elif "Errors:" in line:
                match = re.search(r'Errors: (\d+)', line)
                if match:
                    parsed["statistics"]["errors"] = int(match.group(1))

            elif "Duration:" in line:
                match = re.search(r'Duration: ([^\n]+)', line)
                if match:
                    parsed["statistics"]["duration"] = match.group(1)

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

class GobusterWrapper:
    """Wrapper Python pour Gobuster"""

    def __init__(self):
        self.command = "gobuster"
        self.name = "gobuster"
        self.description = "Directory/file/dns busting tool"

    def dir_scan(self, url: str, wordlist: str, **kwargs) -> Dict[str, Any]:
        """Scan de répertoires avec Gobuster"""
        cmd = ["gobuster", "dir", "-u", url, "-w", wordlist]

        # Options supplémentaires
        if kwargs.get("extensions"):
            cmd.extend(["-x", kwargs["extensions"]])
        if kwargs.get("threads"):
            cmd.extend(["-t", str(kwargs["threads"])])
        if kwargs.get("timeout"):
            cmd.extend(["--timeout", str(kwargs["timeout"])])
        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])
        if kwargs.get("verbose"):
            cmd.append("-v")
        if kwargs.get("follow_redirect"):
            cmd.append("-f")
        if kwargs.get("status_codes"):
            cmd.extend(["-s", kwargs["status_codes"]])

        result = self._run_command(cmd, kwargs.get("timeout", 300))

        if result["success"]:
            result["parsed"] = self._parse_gobuster_dir_output(result["stdout"])

        return result

    def dns_scan(self, domain: str, wordlist: str, **kwargs) -> Dict[str, Any]:
        """Scan DNS avec Gobuster"""
        cmd = ["gobuster", "dns", "-d", domain, "-w", wordlist]

        # Options supplémentaires
        if kwargs.get("resolver"):
            cmd.extend(["-r", kwargs["resolver"]])
        if kwargs.get("threads"):
            cmd.extend(["-t", str(kwargs["threads"])])
        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])
        if kwargs.get("verbose"):
            cmd.append("-v")

        result = self._run_command(cmd, kwargs.get("timeout", 300))

        if result["success"]:
            result["parsed"] = self._parse_gobuster_dns_output(result["stdout"])

        return result

    def _parse_gobuster_dir_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie Gobuster dir"""
        parsed = {
            "directories": [],
            "files": [],
            "status_codes": {}
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            # Ligne de résultat: /admin/ (Status: 200) [Size: 1234]
            if '/' in line and '(Status:' in line:
                match = re.search(r'([^ ]+) \(Status: (\d+)\)(?: \[Size: (\d+)\])?', line)
                if match:
                    path = match.group(1)
                    code = int(match.group(2))
                    size = match.group(3)

                    item = {
                        "path": path,
                        "code": code,
                        "size": int(size) if size else None
                    }

                    # Compter par code
                    if code not in parsed["status_codes"]:
                        parsed["status_codes"][code] = 0
                    parsed["status_codes"][code] += 1

                    # Classifier
                    if path.endswith('/'):
                        parsed["directories"].append(item)
                    else:
                        parsed["files"].append(item)

        return parsed

    def _parse_gobuster_dns_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse la sortie Gobuster dns"""
        results = []

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            # Ligne de résultat: Found: mail.example.com
            if line.startswith('Found: '):
                subdomain = line.replace('Found: ', '').strip()
                results.append({
                    "subdomain": subdomain,
                    "type": "subdomain"
                })

        return results

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

class FFUFWrapper:
    """Wrapper Python pour FFUF"""

    def __init__(self):
        self.command = "ffuf"
        self.name = "ffuf"
        self.description = "Fast web fuzzer"

    def fuzz(self, url: str, wordlist: str, **kwargs) -> Dict[str, Any]:
        """Effectue un fuzzing avec FFUF"""
        cmd = [self.command, "-u", url, "-w", wordlist]

        # Options supplémentaires
        if kwargs.get("threads"):
            cmd.extend(["-t", str(kwargs["threads"])])
        if kwargs.get("timeout"):
            cmd.extend(["-timeout", str(kwargs["timeout"])])
        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])
        if kwargs.get("output_format"):
            cmd.extend(["-of", kwargs["output_format"]])
        if kwargs.get("match_codes"):
            cmd.extend(["-mc", kwargs["match_codes"]])
        if kwargs.get("filter_codes"):
            cmd.extend(["-fc", kwargs["filter_codes"]])
        if kwargs.get("verbose"):
            cmd.append("-v")
        if kwargs.get("follow_redirects"):
            cmd.append("-r")

        result = self._run_command(cmd, kwargs.get("timeout", 600))

        if result["success"]:
            result["parsed"] = self._parse_ffuf_output(result["stdout"])

        return result

    def _parse_ffuf_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie FFUF"""
        parsed = {
            "results": [],
            "statistics": {
                "total_requests": 0,
                "duration": "",
                "average_response_time": ""
            }
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            # Ligne de résultat: [Status: 200, Size: 1234, Words: 56, Lines: 12] http://example.com/admin/
            if line.startswith('[Status: ') and 'http' in line:
                match = re.search(r'\[Status: (\d+), Size: (\d+), Words: (\d+), Lines: (\d+)\] (.+)', line)
                if match:
                    status = int(match.group(1))
                    size = int(match.group(2))
                    words = int(match.group(3))
                    lines_count = int(match.group(4))
                    url = match.group(5)

                    parsed["results"].append({
                        "url": url,
                        "status": status,
                        "size": size,
                        "words": words,
                        "lines": lines_count
                    })

            elif ":: Progress:" in line:
                match = re.search(r':: Progress: \[(\d+)/(\d+)\]', line)
                if match:
                    parsed["statistics"]["progress"] = f"{match.group(1)}/{match.group(2)}"

            elif ":: Duration:" in line:
                match = re.search(r':: Duration: ([^\n]+)', line)
                if match:
                    parsed["statistics"]["duration"] = match.group(1)

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

class WhatWebWrapper:
    """Wrapper Python pour WhatWeb"""

    def __init__(self):
        self.command = "whatweb"
        self.name = "whatweb"
        self.description = "Web technology fingerprinting"

    def fingerprint(self, url: str, **kwargs) -> Dict[str, Any]:
        """Effectue un fingerprinting avec WhatWeb"""
        cmd = [self.command, url]

        # Options supplémentaires
        if kwargs.get("aggression"):
            cmd.extend(["--aggression", str(kwargs["aggression"])])
        if kwargs.get("max_threads"):
            cmd.extend(["--max-threads", str(kwargs["max_threads"])])
        if kwargs.get("output_file"):
            cmd.extend(["-o", kwargs["output_file"]])
        if kwargs.get("log_file"):
            cmd.extend(["-l", kwargs["log_file"]])
        if kwargs.get("verbose"):
            cmd.append("-v")
        if kwargs.get("debug"):
            cmd.append("--debug")

        result = self._run_command(cmd, kwargs.get("timeout", 120))

        if result["success"]:
            result["parsed"] = self._parse_whatweb_output(result["stdout"])

        return result

    def _parse_whatweb_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie WhatWeb"""
        parsed = {
            "url": "",
            "technologies": [],
            "plugins": {},
            "confidence": {}
        }

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            # Première ligne: URL
            if line.startswith('http') and not parsed["url"]:
                parsed["url"] = line.split()[0]

            # Lignes de technologies: [Tech][Confidence]
            elif '[' in line and ']' in line and line.count('[') >= 2:
                # Extraire les technologies entre crochets
                tech_matches = re.findall(r'\[([^\]]+)\]', line)
                for tech in tech_matches:
                    if tech not in ['200', '301', '302', '403', '404', '500']:  # Éviter les codes HTTP
                        parsed["technologies"].append(tech)

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

# Gestionnaire unifié pour les outils web
class WebToolsManager:
    """Gestionnaire unifié des outils web"""

    def __init__(self):
        self.tools = {
            "nikto": NiktoWrapper(),
            "dirb": DirbWrapper(),
            "dirsearch": DirsearchWrapper(),
            "gobuster": GobusterWrapper(),
            "ffuf": FFUFWrapper(),
            "whatweb": WhatWebWrapper()
        }

    def get_tool(self, name: str):
        """Récupère un outil par nom"""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """Liste tous les outils disponibles"""
        return list(self.tools.keys())

    def scan_web(self, url: str, method: str = "nikto", **kwargs) -> Dict[str, Any]:
        """Effectue un scan web avec l'outil spécifié"""
        tool = self.get_tool(method)
        if not tool:
            return {"error": f"Unknown web scanning method: {method}"}

        if method in ["nikto", "dirb", "dirsearch", "ffuf", "whatweb"]:
            return tool.scan(url, **kwargs)
        elif method == "gobuster":
            scan_type = kwargs.get("scan_type", "dir")
            if scan_type == "dir":
                return tool.dir_scan(url, **kwargs)
            elif scan_type == "dns":
                return tool.dns_scan(url, **kwargs)
            else:
                return {"error": f"Unsupported gobuster scan type: {scan_type}"}
        else:
            return {"error": f"Unsupported web scan method: {method}"}

def main():
    """Test des wrappers web"""
    import argparse

    parser = argparse.ArgumentParser(description="Web Application Tools Wrappers")
    parser.add_argument("url", help="URL to scan")
    parser.add_argument("--tool", choices=["nikto", "dirb", "dirsearch", "gobuster", "ffuf", "whatweb"],
                       default="nikto", help="Tool to use")
    parser.add_argument("--wordlist", help="Wordlist for directory scanning")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    manager = WebToolsManager()

    print(f"🌐 Scanning {args.url} with {args.tool}...")

    result = manager.scan_web(args.url, args.tool,
                            wordlist=args.wordlist,
                            output_file=args.output)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        if result.get("success"):
            print("✅ Web scan completed successfully")
            if "parsed" in result:
                parsed = result["parsed"]
                if "vulnerabilities" in parsed:
                    print(f"Found {len(parsed['vulnerabilities'])} items")
                elif "results" in parsed:
                    print(f"Found {len(parsed['results'])} results")
                elif "directories" in parsed:
                    print(f"Found {len(parsed['directories'])} directories, {len(parsed.get('files', []))} files")
                else:
                    print("Scan results parsed successfully")
        else:
            print(f"❌ Web scan failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()