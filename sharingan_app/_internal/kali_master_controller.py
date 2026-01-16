#!/usr/bin/env python3
"""
Sharingan OS - Kali Tools Master Controller
Contrôleur principal pour tous les wrappers d'outils Kali Linux
Gère les téléchargements, installations et exécutions
"""

import os
import sys
import json
import time
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import concurrent.futures

# Ajouter le répertoire Sharingan au path
sharingan_dir = Path(__file__).parent
sys.path.insert(0, str(sharingan_dir))

class KaliMasterController:
    """Contrôleur maître de tous les outils Kali"""

    def __init__(self):
        self.base_dir = sharingan_dir
        self.repos_dir = self.base_dir / "kali_repos"
        self.wrappers_dir = self.base_dir / "wrappers"
        self.tools_config = self._load_tools_config()
        self.download_manager = KaliDownloadManager(self.repos_dir)
        self.wrapper_manager = KaliWrapperManager(self.wrappers_dir)

        # Créer les répertoires
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        self.wrappers_dir.mkdir(parents=True, exist_ok=True)

        # Démarrer les téléchargements en arrière-plan
        self.download_manager.start_background_downloads()

    def _load_tools_config(self) -> Dict[str, Any]:
        """Charge la configuration de tous les outils"""
        return {
            "network": {
                "nmap": {"repo": "https://github.com/nmap/nmap.git", "wrapper": "kali_network_wrappers.py"},
                "masscan": {"repo": "https://github.com/robertdavidgraham/masscan.git", "wrapper": "kali_network_wrappers.py"},
                "netdiscover": {"repo": "https://github.com/netdiscover-scanner/netdiscover.git", "wrapper": "kali_network_wrappers.py"},
                "arp-scan": {"repo": "https://github.com/royhills/arp-scan.git", "wrapper": "kali_network_wrappers.py"},
                "hping3": {"repo": "https://github.com/antirez/hping.git", "wrapper": "kali_network_wrappers.py"}
            },
            "web": {
                "nikto": {"repo": "https://github.com/sullo/nikto.git", "wrapper": "kali_web_wrappers.py"},
                "dirb": {"repo": "https://github.com/v0re/dirb.git", "wrapper": "kali_web_wrappers.py"},
                "dirsearch": {"repo": "https://github.com/maurosoria/dirsearch.git", "wrapper": "kali_web_wrappers.py"},
                "gobuster": {"repo": "https://github.com/OJ/gobuster.git", "wrapper": "kali_web_wrappers.py"},
                "ffuf": {"repo": "https://github.com/ffuf/ffuf.git", "wrapper": "kali_web_wrappers.py"},
                "wpscan": {"repo": "https://github.com/wpscanteam/wpscan.git", "wrapper": "kali_web_wrappers.py"},
                "whatweb": {"repo": "https://github.com/urbanadventurer/WhatWeb.git", "wrapper": "kali_web_wrappers.py"}
            },
            "password": {
                "hashcat": {"repo": "https://github.com/hashcat/hashcat.git", "wrapper": "kali_password_wrappers.py"},
                "john": {"repo": "https://github.com/openwall/john.git", "wrapper": "kali_password_wrappers.py"},
                "hydra": {"repo": "https://github.com/vanhauser-thc/thc-hydra.git", "wrapper": "kali_password_wrappers.py"},
                "medusa": {"repo": "https://github.com/jmk-foofus/medusa.git", "wrapper": "kali_password_wrappers.py"},
                "patator": {"repo": "https://github.com/lanjelot/patator.git", "wrapper": "kali_password_wrappers.py"},
                "crunch": {"repo": "https://github.com/crunchsec/crunch.git", "wrapper": "kali_password_wrappers.py"}
            },
            "wireless": {
                "aircrack-ng": {"repo": "https://github.com/aircrack-ng/aircrack-ng.git", "wrapper": "kali_wireless_wrappers.py"},
                "reaver": {"repo": "https://github.com/t6x/reaver-wps-fork-t6x.git", "wrapper": "kali_wireless_wrappers.py"},
                "bully": {"repo": "https://github.com/aanarchyy/bully.git", "wrapper": "kali_wireless_wrappers.py"}
            },
            "exploitation": {
                "metasploit": {"repo": "https://github.com/rapid7/metasploit-framework.git", "wrapper": "kali_exploitation_wrappers.py"},
                "sqlmap": {"repo": "https://github.com/sqlmapproject/sqlmap.git", "wrapper": "kali_exploitation_wrappers.py"},
                "searchsploit": {"repo": "https://github.com/offensive-security/exploitdb.git", "wrapper": "kali_exploitation_wrappers.py"}
            },
            "forensic": {
                "binwalk": {"repo": "https://github.com/ReFirmLabs/binwalk.git", "wrapper": "kali_forensic_wrappers.py"},
                "foremost": {"repo": "https://github.com/korczis/foremost.git", "wrapper": "kali_forensic_wrappers.py"},
                "volatility": {"repo": "https://github.com/volatilityfoundation/volatility3.git", "wrapper": "kali_forensic_wrappers.py"},
                "autopsy": {"repo": "https://github.com/sleuthkit/autopsy.git", "wrapper": "kali_forensic_wrappers.py"},
                "scalpel": {"repo": "https://github.com/machn1k/scalpel.git", "wrapper": "kali_forensic_wrappers.py"}
            },
            "enumeration": {
                "theharvester": {"repo": "https://github.com/laramies/theHarvester.git", "wrapper": "kali_enumeration_wrappers.py"},
                "dnsrecon": {"repo": "https://github.com/darkoperator/dnsrecon.git", "wrapper": "kali_enumeration_wrappers.py"},
                "dnsenum": {"repo": "https://github.com/fwaeytens/dnsenum.git", "wrapper": "kali_enumeration_wrappers.py"},
                "fierce": {"repo": "https://github.com/mschwager/fierce.git", "wrapper": "kali_enumeration_wrappers.py"},
                "recon-ng": {"repo": "https://github.com/lanmaster53/recon-ng.git", "wrapper": "kali_enumeration_wrappers.py"}
            },
            "social": {
                "setoolkit": {"repo": "https://github.com/trustedsec/social-engineer-toolkit.git", "wrapper": "kali_social_wrappers.py"},
                "king-phisher": {"repo": "https://github.com/rsmusllp/king-phisher.git", "wrapper": "kali_social_wrappers.py"},
                "gophish": {"repo": "https://github.com/gophish/gophish.git", "wrapper": "kali_social_wrappers.py"}
            },
            "reverse": {
                "radare2": {"repo": "https://github.com/radareorg/radare2.git", "wrapper": "kali_reverse_wrappers.py"},
                "gdb": {"repo": "https://github.com/bminor/binutils-gdb.git", "wrapper": "kali_reverse_wrappers.py"},
                "objdump": {"repo": "https://github.com/bminor/binutils-gdb.git", "wrapper": "kali_reverse_wrappers.py"},
                "strings": {"repo": "https://github.com/bminor/binutils-gdb.git", "wrapper": "kali_reverse_wrappers.py"},
                "ltrace": {"repo": "https://github.com/dkogan/ltrace.git", "wrapper": "kali_reverse_wrappers.py"},
                "strace": {"repo": "https://github.com/strace/strace.git", "wrapper": "kali_reverse_wrappers.py"}
            },
            "post_exploit": {
                "empire": {"repo": "https://github.com/EmpireProject/Empire.git", "wrapper": "kali_post_exploit_wrappers.py"},
                "covenant": {"repo": "https://github.com/cobbr/Covenant.git", "wrapper": "kali_post_exploit_wrappers.py"},
                "pupy": {"repo": "https://github.com/n1nj4sec/pupy.git", "wrapper": "kali_post_exploit_wrappers.py"},
                "quack": {"repo": "https://github.com/k0st/Quack.git", "wrapper": "kali_post_exploit_wrappers.py"}
            }
        }

    def get_all_tools(self) -> Dict[str, Any]:
        """Retourne tous les outils par catégorie"""
        return self.tools_config

    def get_tools_by_category(self, category: str) -> Dict[str, Any]:
        """Retourne les outils d'une catégorie"""
        return self.tools_config.get(category, {})

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Retourne les informations d'un outil"""
        for category, tools in self.tools_config.items():
            if tool_name in tools:
                info = tools[tool_name].copy()
                info["category"] = category
                info["installed"] = self._is_tool_installed(tool_name)
                info["repo_cloned"] = (self.repos_dir / tool_name).exists()
                info["wrapper_exists"] = (self.wrappers_dir / f"{tool_name}_wrapper.py").exists()
                return info
        return None

    def _is_tool_installed(self, tool_name: str) -> bool:
        """Vérifie si un outil est installé"""
        try:
            # Essayer de trouver la commande
            result = subprocess.run(
                ["which", tool_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def run_tool(self, tool_name: str, args: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """Exécute un outil via son wrapper"""
        tool_info = self.get_tool_info(tool_name)
        if not tool_info:
            return {"error": f"Unknown tool: {tool_name}"}

        wrapper_file = tool_info.get("wrapper")
        if not wrapper_file:
            return {"error": f"No wrapper available for {tool_name}"}

        # Importer le wrapper dynamiquement
        try:
            module_name = wrapper_file.replace(".py", "")
            module = __import__(module_name)

            # Trouver la classe wrapper (nom en PascalCase)
            class_name = tool_name.replace("-", "_").title() + "Wrapper"
            if hasattr(module, class_name):
                wrapper_class = getattr(module, class_name)
                wrapper = wrapper_class()

                # Exécuter l'outil
                if hasattr(wrapper, 'run'):
                    return wrapper.run(args or [], **kwargs)
                else:
                    return {"error": f"Wrapper {class_name} has no run method"}

            else:
                return {"error": f"Wrapper class {class_name} not found in {wrapper_file}"}

        except Exception as e:
            return {"error": f"Failed to load wrapper: {str(e)}"}

    def install_tool(self, tool_name: str) -> Dict[str, Any]:
        """Installe un outil Kali"""
        tool_info = self.get_tool_info(tool_name)
        if not tool_info:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            print(f"📦 Installing {tool_name}...")

            # Installer via apt si package disponible
            if "package_name" in tool_info:
                result = subprocess.run(
                    ["apt", "install", "-y", tool_info["package_name"]],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return {"success": True, "method": "apt", "message": f"{tool_name} installed successfully"}
                else:
                    return {"error": f"apt installation failed: {result.stderr}"}

            # Essayer d'installer depuis le repo cloné
            repo_path = self.repos_dir / tool_name
            if repo_path.exists():
                # Installation depuis source (basique)
                return {"success": True, "method": "source", "message": f"{tool_name} repo available at {repo_path}"}

            return {"error": f"No installation method available for {tool_name}"}

        except Exception as e:
            return {"error": str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut global de tous les outils"""
        status = {
            "categories": {},
            "total_tools": 0,
            "installed_tools": 0,
            "cloned_repos": 0,
            "available_wrappers": 0,
            "download_status": self.download_manager.get_status()
        }

        for category, tools in self.tools_config.items():
            category_status = {
                "tools": {},
                "total": len(tools),
                "installed": 0,
                "cloned": 0,
                "wrapped": 0
            }

            for tool_name, tool_info in tools.items():
                tool_status = {
                    "installed": self._is_tool_installed(tool_name),
                    "repo_cloned": (self.repos_dir / tool_name).exists(),
                    "wrapper_exists": (self.wrappers_dir / f"{tool_name}_wrapper.py").exists()
                }

                category_status["tools"][tool_name] = tool_status

                if tool_status["installed"]:
                    category_status["installed"] += 1
                if tool_status["repo_cloned"]:
                    category_status["cloned"] += 1
                if tool_status["wrapper_exists"]:
                    category_status["wrapped"] += 1

            status["categories"][category] = category_status
            status["total_tools"] += category_status["total"]
            status["installed_tools"] += category_status["installed"]
            status["cloned_repos"] += category_status["cloned"]
            status["available_wrappers"] += category_status["wrapped"]

        return status

    def create_missing_wrappers(self) -> Dict[str, Any]:
        """Crée tous les wrappers manquants"""
        results = {
            "created": [],
            "skipped": [],
            "errors": []
        }

        for category, tools in self.tools_config.items():
            for tool_name, tool_info in tools.items():
                wrapper_path = self.wrappers_dir / f"{tool_name}_wrapper.py"
                if not wrapper_path.exists():
                    try:
                        # Créer un wrapper basique
                        self.wrapper_manager.create_basic_wrapper(tool_name, tool_info)
                        results["created"].append(tool_name)
                    except Exception as e:
                        results["errors"].append(f"{tool_name}: {str(e)}")
                else:
                    results["skipped"].append(tool_name)

        return results

class KaliDownloadManager:
    """Gestionnaire de téléchargements des repositories"""

    def __init__(self, repos_dir: Path):
        self.repos_dir = repos_dir
        self.download_queue = []
        self.active_downloads = set()
        self.completed_downloads = {}
        self.max_concurrent = 1  # Un seul téléchargement à la fois

    def start_background_downloads(self):
        """Démarre les téléchargements en arrière-plan"""
        # Liste des repos prioritaires
        priority_repos = [
            ("nmap", "https://github.com/nmap/nmap.git"),
            ("metasploit", "https://github.com/rapid7/metasploit-framework.git"),
            ("hashcat", "https://github.com/hashcat/hashcat.git"),
            ("sqlmap", "https://github.com/sqlmapproject/sqlmap.git"),
            ("aircrack-ng", "https://github.com/aircrack-ng/aircrack-ng.git"),
            ("binwalk", "https://github.com/ReFirmLabs/binwalk.git"),
            ("volatility", "https://github.com/volatilityfoundation/volatility3.git"),
            ("theharvester", "https://github.com/laramies/theHarvester.git")
        ]

        for repo_name, repo_url in priority_repos:
            self.add_to_queue(repo_name, repo_url)

        # Démarrer le thread de traitement
        download_thread = threading.Thread(target=self._process_downloads, daemon=True)
        download_thread.start()

    def add_to_queue(self, repo_name: str, repo_url: str):
        """Ajoute un repo à la queue de téléchargement"""
        if repo_name not in self.completed_downloads and repo_name not in self.active_downloads:
            self.download_queue.append((repo_name, repo_url))

    def _process_downloads(self):
        """Traite la queue de téléchargements"""
        while True:
            # Limiter les téléchargements simultanés
            if len(self.active_downloads) >= self.max_concurrent:
                time.sleep(1)
                continue

            if not self.download_queue:
                time.sleep(5)  # Attendre de nouveaux éléments
                continue

            repo_name, repo_url = self.download_queue.pop(0)
            self.active_downloads.add(repo_name)

            # Lancer le téléchargement dans un thread séparé
            threading.Thread(
                target=self._download_repo,
                args=(repo_name, repo_url),
                daemon=True
            ).start()

    def _download_repo(self, repo_name: str, repo_url: str):
        """Télécharge un repository"""
        try:
            repo_path = self.repos_dir / repo_name
            repo_path.mkdir(exist_ok=True)

            start_time = time.time()

            # Cloner avec --depth 1 pour économiser l'espace
            cmd = ["git", "clone", "--depth", "1", repo_url, str(repo_path)]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            end_time = time.time()
            duration = end_time - start_time

            if result.returncode == 0:
                repo_size = sum(f.stat().st_size for f in repo_path.rglob('*') if f.is_file())
                self.completed_downloads[repo_name] = {
                    "status": "success",
                    "path": str(repo_path),
                    "size": repo_size,
                    "duration": duration
                }
                print(f"✅ Downloaded {repo_name} ({repo_size/1024/1024:.1f} MB in {duration:.1f}s)")
            else:
                self.completed_downloads[repo_name] = {
                    "status": "failed",
                    "error": result.stderr,
                    "duration": duration
                }
                print(f"❌ Failed to download {repo_name}: {result.stderr[:100]}...")

        except subprocess.TimeoutExpired:
            self.completed_downloads[repo_name] = {
                "status": "timeout",
                "error": "Download timeout"
            }
            print(f"⏰ Timeout downloading {repo_name}")
        except Exception as e:
            self.completed_downloads[repo_name] = {
                "status": "error",
                "error": str(e)
            }
            print(f"💥 Error downloading {repo_name}: {e}")
        finally:
            self.active_downloads.discard(repo_name)

    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut des téléchargements"""
        return {
            "active": list(self.active_downloads),
            "completed": len(self.completed_downloads),
            "queued": len(self.download_queue),
            "results": self.completed_downloads.copy()
        }

class KaliWrapperManager:
    """Gestionnaire des wrappers Python"""

    def __init__(self, wrappers_dir: Path):
        self.wrappers_dir = wrappers_dir

    def create_basic_wrapper(self, tool_name: str, tool_info: Dict[str, Any]):
        """Crée un wrapper basique pour un outil"""
        wrapper_content = f'''#!/usr/bin/env python3
"""
Basic wrapper for {tool_name}
Generated automatically by KaliWrapperManager
"""

import subprocess
import sys
from pathlib import Path

class {tool_name.title()}Wrapper:
    """Basic wrapper for {tool_name}"""

    def __init__(self):
        self.command = "{tool_name}"

    def run(self, args=None, **kwargs):
        """Run the tool with given arguments"""
        if args is None:
            args = []

        cmd = [self.command] + args

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=kwargs.get('timeout', 300)
            )

            return {{
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd)
            }}
        except subprocess.TimeoutExpired:
            return {{
                "success": False,
                "error": f"Command timed out after {{kwargs.get('timeout', 300)}}s"
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": str(e)
            }}

if __name__ == "__main__":
    wrapper = {tool_name.title()}Wrapper()
    result = wrapper.run(sys.argv[1:])

    if result.get("success"):
        if result.get("stdout"):
            print(result["stdout"])
    else:
        print(f"Error: {{result.get('error', 'Unknown error')}}")
        sys.exit(1)
'''

        wrapper_path = self.wrappers_dir / f"{tool_name}_wrapper.py"
        wrapper_path.write_text(wrapper_content)
        wrapper_path.chmod(0o755)

def main():
    """Interface principale du contrôleur Kali"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Sharingan OS - Kali Tools Master Controller",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("command", choices=[
        "status", "list", "run", "install", "create-wrappers", "download-status"
    ], help="Command to execute")

    parser.add_argument("--tool", help="Tool name for run/install commands")
    parser.add_argument("--category", help="Category for list command")
    parser.add_argument("--args", nargs="*", help="Arguments for tool execution")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    controller = KaliMasterController()

    if args.command == "status":
        status = controller.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"📊 Kali Tools Status:")
            print(f"  Total tools: {status['total_tools']}")
            print(f"  Installed: {status['installed_tools']}")
            print(f"  Repos cloned: {status['cloned_repos']}")
            print(f"  Wrappers: {status['available_wrappers']}")
            print(f"  Downloads active: {len(status['download_status']['active'])}")
            print(f"  Downloads completed: {status['download_status']['completed']}")

    elif args.command == "list":
        if args.category:
            tools = controller.get_tools_by_category(args.category)
            print(f"🔧 Tools in category '{args.category}':")
            for tool_name, tool_info in tools.items():
                status = "✓" if controller._is_tool_installed(tool_name) else "✗"
                print(f"  {status} {tool_name}")
        else:
            all_tools = controller.get_all_tools()
            for category, tools in all_tools.items():
                print(f"📁 {category.upper()}: {len(tools)} tools")
                for tool_name in tools.keys():
                    status = "✓" if controller._is_tool_installed(tool_name) else "✗"
                    print(f"    {status} {tool_name}")

    elif args.command == "run":
        if not args.tool:
            print("Error: --tool required for run command")
            sys.exit(1)

        result = controller.run_tool(args.tool, args.args or [])
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result.get("success"):
                print(f"✅ {args.tool} executed successfully")
                if result.get("stdout"):
                    print("Output:")
                    print(result["stdout"][:1000])  # Limiter la sortie
            else:
                print(f"❌ {args.tool} execution failed: {result.get('error', 'Unknown error')}")

    elif args.command == "install":
        if not args.tool:
            print("Error: --tool required for install command")
            sys.exit(1)

        result = controller.install_tool(args.tool)
        if result.get("success"):
            print(f"✅ {args.tool} installed successfully via {result.get('method')}")
        else:
            print(f"❌ Failed to install {args.tool}: {result.get('error')}")

    elif args.command == "create-wrappers":
        result = controller.create_missing_wrappers()
        print(f"📦 Created {len(result['created'])} wrappers")
        print(f"⏭️  Skipped {len(result['skipped'])} existing")
        if result['errors']:
            print(f"❌ {len(result['errors'])} errors")

    elif args.command == "download-status":
        status = controller.download_manager.get_status()
        print(f"📥 Download Status:")
        print(f"  Active: {', '.join(status['active']) if status['active'] else 'None'}")
        print(f"  Completed: {status['completed']}")
        print(f"  Queued: {status['queued']}")

if __name__ == "__main__":
    main()