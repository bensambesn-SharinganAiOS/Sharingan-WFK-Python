#!/usr/bin/env python3
"""
Sharingan OS - Kali Tools Bootstrap
Script de démarrage pour initialiser tous les wrappers et téléchargements Kali
"""

import os
import sys
import time
import threading
import subprocess
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire Sharingan au path
sharingan_dir = Path(__file__).parent
sys.path.insert(0, str(sharingan_dir))

def print_banner():
    """Affiche la bannière"""
    print("=" * 70)
    print("🔥 SHARINGAN OS - KALI TOOLS BOOTSTRAP")
    print("=" * 70)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Working directory: {sharingan_dir}")
    print("=" * 70)

def start_master_controller():
    """Démarre le contrôleur maître Kali"""
    print("🚀 Starting Kali Master Controller...")
    try:
        from kali_master_controller import KaliMasterController
        controller = KaliMasterController()
        print("✅ Kali Master Controller started")
        return controller
    except Exception as e:
        print(f"❌ Failed to start Kali Master Controller: {e}")
        return None

def create_missing_wrapper_files():
    """Crée les fichiers wrapper manquants"""
    print("\\n📦 Creating missing wrapper files...")

    wrapper_files = [
        "kali_exploitation_wrappers.py",
        "kali_forensic_wrappers.py",
        "kali_enumeration_wrappers.py",
        "kali_social_wrappers.py",
        "kali_reverse_wrappers.py",
        "kali_post_exploit_wrappers.py",
        "kali_vuln_scanner_wrappers.py",
        "kali_reporting_wrappers.py",
        "kali_monitoring_wrappers.py"
    ]

    created = 0
    for wrapper_file in wrapper_files:
        wrapper_path = sharingan_dir / wrapper_file
        if not wrapper_path.exists():
            try:
                # Créer un fichier wrapper basique
                create_basic_wrapper_file(wrapper_file)
                created += 1
                print(f"  ✅ Created {wrapper_file}")
            except Exception as e:
                print(f"  ❌ Failed to create {wrapper_file}: {e}")
        else:
            print(f"  ⏭️  {wrapper_file} already exists")

    print(f"📊 Created {created} wrapper files")

def create_basic_wrapper_file(filename: str):
    """Crée un fichier wrapper basique"""
    category = filename.replace("kali_", "").replace("_wrappers.py", "")

    content = f'''#!/usr/bin/env python3
"""
Sharingan OS - Kali {category.title()} Tools Wrappers
Wrappers Python pour les outils {category} Kali Linux
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional, Any

# TODO: Implement specific wrappers for {category} tools
# This is a placeholder file that will be populated with actual tool wrappers

class BasicToolWrapper:
    """Wrapper basique pour outil {category}"""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.command = tool_name

    def run(self, args: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Exécute l'outil"""
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

# TODO: Add specific tool wrapper classes here
# Examples:
# class MetasploitWrapper(BasicToolWrapper):
#     def __init__(self):
#         super().__init__("msfconsole")
#
# class SqlmapWrapper(BasicToolWrapper):
#     def __init__(self):
#         super().__init__("sqlmap")

def get_{category}_tools_manager():
    """Get {category} tools manager instance"""
    return BasicToolWrapper("placeholder")

if __name__ == "__main__":
    print(f"⚠️  {filename} - Placeholder wrapper file")
    print("This file needs to be populated with actual tool implementations")
'''

    wrapper_path = sharingan_dir / filename
    wrapper_path.write_text(content)
    wrapper_path.chmod(0o755)

def start_background_downloads(controller):
    """Démarre les téléchargements en arrière-plan"""
    print("\\n🔄 Starting background repository downloads...")

    if controller:
        # Ajouter tous les repos à la queue
        tools_config = controller.get_all_tools()

        repos_added = 0
        for category, tools in tools_config.items():
            for tool_name, tool_info in tools.items():
                if "repo" in tool_info and tool_info["repo"]:
                    try:
                        controller.download_manager.add_to_queue(tool_name, tool_info["repo"])
                        repos_added += 1
                        print(f"  📥 Added {tool_name} to download queue")
                    except Exception as e:
                        print(f"  ❌ Failed to add {tool_name}: {e}")

        print(f"📊 Added {repos_added} repositories to download queue")
        print("Downloads will continue in background...")

        # Afficher le statut initial
        time.sleep(2)
        status = controller.download_manager.get_status()
        print(f"📈 Initial status: {status['completed']} completed, {len(status['active'])} active")

    else:
        print("❌ No controller available for downloads")

def create_installation_script():
    """Crée un script d'installation automatique"""
    print("\\n📜 Creating installation script...")

    install_script = sharingan_dir / "install_kali_tools.sh"
    script_content = '''#!/bin/bash
# Sharingan OS - Kali Tools Auto-Installer
# Installation automatique de tous les outils Kali

echo "🔥 Sharingan OS - Kali Tools Installation"
echo "========================================"

# Liste des outils à installer
KALI_TOOLS=(
    # Network
    "nmap"
    "masscan"
    "netdiscover"
    "arp-scan"
    "hping3"

    # Web
    "nikto"
    "dirb"
    "dirsearch"
    "gobuster"
    "ffuf"
    "wpscan"
    "whatweb"

    # Password
    "hashcat"
    "john"
    "hydra"
    "medusa"
    "patator"
    "crunch"

    # Wireless
    "aircrack-ng"
    "reaver"
    "bully"

    # Exploitation
    "metasploit-framework"
    "sqlmap"
    "exploitdb"

    # Forensic
    "binwalk"
    "foremost"
    "volatility"
    "autopsy"
    "scalpel"

    # Enumeration
    "theharvester"
    "dnsrecon"
    "dnsenum"
    "fierce"
    "recon-ng"

    # Social
    "set"
    "king-phisher"

    # Reverse Engineering
    "radare2"
    "gdb"
    "binutils"
    "ltrace"
    "strace"
)

echo "📦 Updating package list..."
apt update

echo "🔧 Installing Kali tools..."
INSTALLED=0
FAILED=0

for tool in "${KALI_TOOLS[@]}"; do
    echo "Installing $tool..."
    if apt install -y "$tool" >/dev/null 2>&1; then
        echo "  ✅ $tool installed"
        ((INSTALLED++))
    else
        echo "  ❌ $tool failed"
        ((FAILED++))
    fi
done

echo ""
echo "📊 Installation Summary:"
echo "  ✅ Installed: $INSTALLED"
echo "  ❌ Failed: $FAILED"
echo ""
echo "🎊 Kali tools installation completed!"
'''

    install_script.write_text(script_content)
    install_script.chmod(0o755)
    print(f"✅ Created installation script: {install_script}")

def show_status(controller):
    """Affiche le statut complet"""
    print("\\n📊 Current Status:")

    if controller:
        status = controller.get_status()
        print(f"  📦 Total tools: {status['total_tools']}")
        print(f"  ✅ Installed: {status['installed_tools']}")
        print(f"  🔄 Repos cloned: {status['cloned_repos']}")
        print(f"  📄 Wrappers: {status['available_wrappers']}")

        download_status = status['download_status']
        print(f"  📥 Downloads active: {len(download_status['active'])}")
        print(f"  📥 Downloads completed: {download_status['completed']}")
        print(f"  📥 Downloads queued: {download_status['queued']}")

        if download_status['active']:
            print(f"  🔄 Currently downloading: {', '.join(download_status['active'][:3])}")
    else:
        print("  ❌ Controller not available")

def main():
    """Fonction principale"""
    print_banner()

    # Créer les fichiers wrapper manquants
    create_missing_wrapper_files()

    # Créer le script d'installation
    create_installation_script()

    # Démarrer le contrôleur maître
    controller = start_master_controller()

    # Démarrer les téléchargements en arrière-plan
    start_background_downloads(controller)

    # Afficher le statut final
    show_status(controller)

    print("\\n" + "=" * 70)
    print("🎊 Kali Tools Bootstrap completed!")
    print("Background downloads and wrapper creation started.")
    print("Use 'python3 kali_master_controller.py status' to monitor progress.")
    print("=" * 70)

if __name__ == "__main__":
    main()