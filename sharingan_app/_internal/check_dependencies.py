#!/usr/bin/env python3
"""
Sharingan OS - Dependency Checker
Vérifie les outils installés et les dépendances disponibles.

Ce script vérifie quels outils de sécurité sont installés
et documente les dépendances nécessaires.
"""

import subprocess
import shutil
import sys
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Tool:
    """Représentation d'un outil."""
    name: str
    description: str
    category: str
    required_for: List[str]
    apt_package: Optional[str] = None
    pip_package: Optional[str] = None
    install_cmd: Optional[str] = None


# Liste des outils avec leurs dépendances
TOOLS = [
    # Outils Réseau
    Tool(
        name="nmap",
        description="Network Mapper - Scanner de ports",
        category="Network",
        required_for=["nmap_scan"],
        apt_package="nmap",
        pip_package="python-nmap"
    ),
    Tool(
        name="masscan",
        description="Scanner de ports haute vitesse",
        category="Network",
        required_for=["masscan_scan"],
        apt_package="masscan"
    ),
    Tool(
        name="rustscan",
        description="Scanner rapide écrit en Rust",
        category="Network",
        required_for=["rust_scan"],
        install_cmd="cargo install rustscan"
    ),
    Tool(
        name="naabu",
        description="Scanner de ports en Go",
        category="Network",
        required_for=["naabu_scan"],
        install_cmd="go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"
    ),
    Tool(
        name="responder",
        description="LLMNR/NBT-NS/mDNS poisoner",
        category="Network",
        required_for=["responder"],
        install_cmd="git clone https://github.com/lgandx/Responder && cd Responder"
    ),
    Tool(
        name="bettercap",
        description="Framework MITM moderne",
        category="Network",
        required_for=["bettercap"],
        apt_package="bettercap"
    ),
    Tool(
        name="tshark",
        description="Analyseur de packets en ligne de commande",
        category="Network",
        required_for=["tshark_capture"],
        apt_package="tshark"
    ),
    Tool(
        name="scapy",
        description="Bibliothèque de manipulation de packets",
        category="Network",
        required_for=["scapy_sniff"],
        pip_package="scapy"
    ),

    # Outils Web
    Tool(
        name="gobuster",
        description="Directory/File brute force",
        category="Web",
        required_for=["gobuster_scan"],
        apt_package="gobuster"
    ),
    Tool(
        name="ffuf",
        description="Fuzzing tool rapide",
        category="Web",
        required_for=["ffuf_scan"],
        apt_package="ffuf"
    ),
    Tool(
        name="dirsearch",
        description="Directory scanner en Python",
        category="Web",
        required_for=["dirsearch"],
        pip_package="dirsearch"
    ),
    Tool(
        name="sqlmap",
        description="SQL Injection automation",
        category="Web",
        required_for=["sqlmap_scan"],
        apt_package="sqlmap"
    ),
    Tool(
        name="xsstrike",
        description="XSS Scanner",
        category="Web",
        required_for=["xsstrike_scan"],
        pip_package="xsstrike"
    ),
    Tool(
        name="commix",
        description="Command Injection Scanner",
        category="Web",
        required_for=["commix_scan"],
        install_cmd="git clone https://github.com/commixproject/commix"
    ),
    Tool(
        name="nikto",
        description="Scanner web complet",
        category="Web",
        required_for=["nikto_scan"],
        apt_package="nikto"
    ),
    Tool(
        name="nuclei",
        description="Scanner basé sur templates",
        category="Web",
        required_for=["nuclei_scan"],
        install_cmd="go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest"
    ),
    Tool(
        name="whatweb",
        description="Identification des technologies web",
        category="Web",
        required_for=["whatweb_scan"],
        apt_package="whatweb"
    ),

    # Outils Mot de Passe
    Tool(
        name="hashcat",
        description="Password Cracking GPU",
        category="Password",
        required_for=["hashcat_crack"],
        apt_package="hashcat"
    ),
    Tool(
        name="john",
        description="John the Ripper",
        category="Password",
        required_for=["john_crack"],
        apt_package="john"
    ),
    Tool(
        name="hydra",
        description="Online password cracking",
        category="Password",
        required_for=["hydra_scan"],
        apt_package="hydra"
    ),
    Tool(
        name="medusa",
        description="Online password cracking parallèle",
        category="Password",
        required_for=["medusa_scan"],
        apt_package="medusa"
    ),
    Tool(
        name="crunch",
        description="Générateur de wordlists",
        category="Password",
        required_for=["crunch_generate"],
        apt_package="crunch"
    ),
    Tool(
        name="cewl",
        description="Générateur de wordlists depuis site web",
        category="Password",
        required_for=["cewl_generate"],
        apt_package="cewl"
    ),

    # Outils Crypto
    Tool(
        name="RsaCtfTool",
        description="Attaques RSA",
        category="Crypto",
        required_for=["rsa_ctf_tool"],
        install_cmd="git clone https://github.com/Ganapati/RsaCtfTool"
    ),

    # Outils Forensics
    Tool(
        name="volatility3",
        description="Memory forensics",
        category="Forensics",
        required_for=["volatility_scan"],
        pip_package="volatility3"
    ),
    Tool(
        name="foremost",
        description="File carving",
        category="Forensics",
        required_for=["foremost_extract"],
        apt_package="foremost"
    ),
    Tool(
        name="testdisk",
        description="Récupération de fichiers",
        category="Forensics",
        required_for=["photorec_recover"],
        apt_package="testdisk"
    ),
    Tool(
        name="steghide",
        description="Stéganographie",
        category="Forensics",
        required_for=["steghide_extract"],
        apt_package="steghide"
    ),
    Tool(
        name="exiftool",
        description="Extraction de métadonnées",
        category="Forensics",
        required_for=["exiftool_extract"],
        apt_package="exiftool"
    ),
    Tool(
        name="yara",
        description="Détection de malware par signatures",
        category="Forensics",
        required_for=["yara_scan"],
        apt_package="yara"
    ),

    # Outils PrivEsc
    Tool(
        name="linpeas",
        description="Linux Privilege Escalation Awesome Script",
        category="PrivEsc",
        required_for=["linpeas_scan"],
        install_cmd="curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh -o linpeas.sh"
    ),
    Tool(
        name="winpeas",
        description="Windows Privilege Escalation Awesome Script",
        category="PrivEsc",
        required_for=["winpeas_scan"],
        install_cmd="curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/winpeas.exe -o winpeas.exe"
    ),
    Tool(
        name="Sharphound",
        description="BloodHound data collector for Windows",
        category="PrivEsc",
        required_for=["bloodhound_collect"],
        install_cmd="curl -L https://github.com/BloodHoundAD/SharpHound3/releases/latest/download/SharpHound.exe -o SharpHound.exe"
    ),

    # Outils Exploitation
    Tool(
        name="exploitdb",
        description="Exploit-DB database",
        category="Exploitation",
        required_for=["searchsploit"],
        apt_package="exploitdb"
    ),
    Tool(
        name="pwntools",
        description="Framework pour exploits CTF",
        category="Exploitation",
        required_for=["pwntools_template"],
        pip_package="pwntools"
    ),
    Tool(
        name="ROPgadget",
        description="Recherche de gadgets ROP",
        category="Exploitation",
        required_for=["rop_generator"],
        pip_package="ROPGadget"
    ),
    Tool(
        name="one_gadget",
        description="Trouver one-gadgets dans libc",
        category="Exploitation",
        required_for=["one_gadget"],
        install_cmd="gem install one_gadget"
    ),
    Tool(
        name="radare2",
        description="Reverse engineering framework",
        category="Exploitation",
        required_for=["radare2_analyze"],
        apt_package="radare2"
    ),

    # Outils Docker
    Tool(
        name="docker",
        description="Container management",
        category="Docker",
        required_for=["docker_ps", "docker_run", "docker_images"],
        apt_package="docker.io"
    ),
    Tool(
        name="trivy",
        description="Scanner de vulnérabilités containers",
        category="Docker",
        required_for=["trivy_scan"],
        install_cmd="curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh"
    ),
    Tool(
        name="hadolint",
        description="Linter pour Dockerfiles",
        category="Docker",
        required_for=["hadolint_scan"],
        install_cmd="curl -sSfL https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64 -o /usr/local/bin/hadolint"
    ),

    # Outils Cloud
    Tool(
        name="aws",
        description="AWS CLI",
        category="Cloud",
        required_for=["aws_enum"],
        install_cmd="curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip && unzip awscliv2.zip && ./aws/install"
    ),
    Tool(
        name="az",
        description="Azure CLI",
        category="Cloud",
        required_for=["az_cli_enum"],
        install_cmd="curl -sL https://aka.ms/InstallAzureCLIDeb | bash"
    ),
    Tool(
        name="gcloud",
        description="Google Cloud CLI",
        category="Cloud",
        required_for=["gcloud_enum"],
        install_cmd="curl https://sdk.cloud.google.com | bash"
    ),
    Tool(
        name="subfinder",
        description="Énumération de sous-domaines",
        category="OSINT",
        required_for=["subfinder_enum"],
        install_cmd="go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    ),
    Tool(
        name="amass",
        description="Énumération de sous-domaines",
        category="OSINT",
        required_for=["amass_enum"],
        apt_package="amass"
    ),
    Tool(
        name="theHarvester",
        description="Harvesting d'emails et sous-domaines",
        category="OSINT",
        required_for=["theharvester_scan"],
        pip_package="theHarvester"
    ),
    Tool(
        name="sherlock",
        description="Recherche de usernames sur réseaux sociaux",
        category="OSINT",
        required_for=["sherlock_search"],
        pip_package="sherlock"
    ),
    Tool(
        name="shodan",
        description="CLI Shodan",
        category="OSINT",
        required_for=["shodan_host", "shodan_search"],
        pip_package="shodan"
    ),
    Tool(
        name="censys",
        description="CLI Censys",
        category="OSINT",
        required_for=["censys_search"],
        pip_package="censys"
    ),

    # Outils Audit
    Tool(
        name="lynis",
        description="Audit de sécurité système",
        category="Audit",
        required_for=["lynis_audit"],
        apt_package="lynis"
    ),
    Tool(
        name="rkhunter",
        description="Détection de rootkits",
        category="Audit",
        required_for=["rkhunter_scan"],
        apt_package="rkhunter"
    ),
    Tool(
        name="openvas",
        description="Scanner de vulnérabilités",
        category="Audit",
        required_for=["openvas_scan"],
        apt_package="openvas"
    ),

    # Outils Browser
    Tool(
        name="selenium",
        description="Automation de navigateur",
        category="Browser",
        required_for=["browser_selenium", "browser_launch", "browser_navigate"],
        pip_package="selenium"
    ),
    Tool(
        name="webdriver-manager",
        description="Gestion automatique des WebDrivers",
        category="Browser",
        required_for=["browser_launch", "browser_navigate"],
        pip_package="webdriver-manager"
    ),
    Tool(
        name="geckodriver",
        description="Firefox WebDriver pour Selenium",
        category="Browser",
        required_for=["browser_launch", "browser_navigate"],
        apt_package="firefox-geckodriver"
    ),
    Tool(
        name="playwright",
        description="Automation de navigateur moderne",
        category="Browser",
        required_for=["browser_screenshot"],
        pip_package="playwright"
    ),
    Tool(
        name="requests",
        description="Requêtes HTTP",
        category="Browser",
        required_for=["python_requests"],
        pip_package="requests"
    ),
    Tool(
        name="mitmproxy",
        description="Proxy HTTP interactif",
        category="Browser",
        required_for=["mitmproxy_script"],
        pip_package="mitmproxy"
    ),
    Tool(
        name="xdotool",
        description="Outil d'automatisation X11 (list windows, get properties)",
        category="System",
        required_for=["system_screenshot", "list_windows"],
        apt_package="xdotool"
    ),
    Tool(
        name="scrot",
        description="Outil de capture d'écran (fallback pour maim)",
        category="System",
        required_for=["system_screenshot"],
        apt_package="scrot"
    ),
    Tool(
        name="maim",
        description="Capture d'écran avancée (recommandé)",
        category="System",
        required_for=["system_screenshot"],
        apt_package="maim"
    ),

    # Outils Audio/Video
    Tool(
        name="ffmpeg",
        description="Conversion et traitement média",
        category="AudioVideo",
        required_for=["extract_audio", "convert_media", "video_thumbnail"],
        apt_package="ffmpeg"
    ),
    Tool(
        name="espeak",
        description="Synthèse vocale",
        category="AudioVideo",
        required_for=["text_to_speech"],
        apt_package="espeak"
    ),
    Tool(
        name="whisper",
        description="Reconnaissance vocale par OpenAI",
        category="AudioVideo",
        required_for=["whisper_transcribe"],
        pip_package="openai-whisper"
    ),
    Tool(
        name="gtts",
        description="Google Text-to-Speech",
        category="AudioVideo",
        required_for=["google_tts"],
        pip_package="gTTS"
    ),

    # Outils CTF
    Tool(
        name="sshpass",
        description="Connexion SSH avec mot de passe",
        category="CTF",
        required_for=["bandit_connect"],
        apt_package="sshpass"
    ),
    Tool(
        name="pwndbg",
        description="Débogueur pour exploits",
        category="CTF",
        required_for=["pwntools_debug"],
        install_cmd="git clone https://github.com/pwndbg/pwndbg && cd pwndbg && ./setup.sh"
    ),

    # Outils Documentation
    Tool(
        name="openpyxl",
        description="Création de fichiers Excel",
        category="Documentation",
        required_for=["create_excel"],
        pip_package="openpyxl"
    ),
    Tool(
        name="python-docx",
        description="Création de fichiers Word",
        category="Documentation",
        required_for=["create_word"],
        pip_package="python-docx"
    ),
    Tool(
        name="reportlab",
        description="Création de fichiers PDF",
        category="Documentation",
        required_for=["create_pdf"],
        pip_package="reportlab"
    ),

    # Outils Divers
    Tool(
        name="git",
        description="Gestion de version",
        category="Misc",
        required_for=["git_clone"],
        apt_package="git"
    ),
    Tool(
        name="unzip",
        description="Extraction d'archives ZIP",
        category="Misc",
        required_for=["extract_archive"],
        apt_package="unzip"
    ),
    Tool(
        name="binwalk",
        description="Analyse de firmware et fichiers",
        category="Misc",
        required_for=["binwalk_extract"],
        install_cmd="git clone https://github.com/ReFirmLabs/binwalk && cd binwalk && python3 setup.py install"
    ),
]


def check_tool(tool_name: str) -> Tuple[bool, str]:
    """Vérifie si un outil est installé."""
    result = shutil.which(tool_name)
    if result:
        return True, result
    return False, ""


def check_python_package(package_name: str) -> Tuple[bool, str]:
    """Vérifie si un package Python est installé."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", f"import {package_name}; print({package_name}.__version__ if hasattr({package_name}, '__version__') else 'installed')"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, version
    except Exception:
        pass
    return False, ""


def analyze_tool_dependencies() -> Dict[str, Dict[str, str]]:
    """Analyse les dépendances des outils."""
    results = {
        "installed": {},
        "missing": {},
        "python_missing": {}
    }
    
    for tool in TOOLS:
        is_installed, path = check_tool(tool.name)
        
        if is_installed:
            results["installed"][tool.name] = {
                "description": tool.description,
                "category": tool.category,
                "path": path,
                "required_for": tool.required_for
            }
        else:
            results["missing"][tool.name] = {
                "description": tool.description,
                "category": tool.category,
                "required_for": tool.required_for,
                "install": f"apt install {tool.apt_package}" if tool.apt_package else 
                         f"pip install {tool.pip_package}" if tool.pip_package else
                         tool.install_cmd or "Manual installation required"
            }
        
        if tool.pip_package:
            package_name = tool.pip_package.split("[")[0]
            is_installed, version = check_python_package(package_name)
            if not is_installed:
                results["python_missing"][package_name] = {
                    "tool": tool.name,
                    "install": f"pip install {tool.pip_package}"
                }
    
    return results


def generate_report() -> Dict[str, Any]:
    """Génère un rapport complet des dépendances."""
    analysis = analyze_tool_dependencies()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "summary": {
            "total_tools": len(TOOLS),
            "installed": len(analysis["installed"]),
            "missing": len(analysis["missing"]),
            "python_missing": len(analysis["python_missing"])
        },
        "by_category": {},
        "missing_by_category": {},
        "recommendations": []
    }
    
    # Grouper par catégorie
    for name, info in analysis["installed"].items():
        cat = info["category"]
        if cat not in report["by_category"]:
            report["by_category"][cat] = []
        report["by_category"][cat].append({name: info})
    
    for name, info in analysis["missing"].items():
        cat = info["category"]
        if cat not in report["missing_by_category"]:
            report["missing_by_category"][cat] = []
        report["missing_by_category"][cat].append({name: info})
    
    # Recommandations
    missing_pct = len(analysis["missing"]) / len(TOOLS) * 100
    if missing_pct > 50:
        report["recommendations"].append(
            f"Plus de 50% des outils sont manquants. "
            "Certaines fonctionnalités seront limitées."
        )
    
    critical_tools = ["nmap", "gobuster", "sqlmap", "hydra", "john", "hashcat"]
    missing_critical = [t for t in critical_tools if t in analysis["missing"]]
    if missing_critical:
        report["recommendations"].append(
            f"Outils critiques manquants: {', '.join(missing_critical)}. "
            "Recommandés pour une utilisation complète."
        )
    
    return report


def print_report(report: Dict[str, Any]) -> None:
    """Affiche le rapport de manière formatée."""
    print("\n" + "=" * 70)
    print("SHARINGAN OS - RAPPORT DE DÉPENDANCES")
    print("=" * 70)
    print(f"Timestamp: {report['timestamp']}")
    print(f"Python: {report['python_version'].split()[0]}")
    
    print("\n--- RÉSUMÉ ---")
    summary = report["summary"]
    print(f"Total des outils documentés: {summary['total_tools']}")
    print(f"Installés: {summary['installed']} ({summary['installed']/summary['total_tools']*100:.1f}%)")
    print(f"Manquants: {summary['missing']} ({summary['missing']/summary['total_tools']*100:.1f}%)")
    print(f"Modules Python manquants: {summary['python_missing']}")
    
    if report["by_category"]:
        print("\n--- OUTILS INSTALLÉS PAR CATÉGORIE ---")
        for category, tools in sorted(report["by_category"].items()):
            count = len(tools)
            print(f"\n{category} ({count}):")
            for tool in tools:
                for name, info in tool.items():
                    print(f"  [OK] {name}")
    
    if report["missing_by_category"]:
        print("\n--- OUTILS MANQUANTS PAR CATÉGORIE ---")
        for category, tools in sorted(report["missing_by_category"].items()):
            count = len(tools)
            print(f"\n{category} ({count}):")
            for tool in tools:
                for name, info in tool.items():
                    install = info["install"][:60] + "..." if len(info["install"]) > 60 else info["install"]
                    print(f"  [MISSING] {name}")
                    print(f"           Install: {install}")
    
    if report["recommendations"]:
        print("\n--- RECOMMANDATIONS ---")
        for rec in report["recommendations"]:
            print(f"  * {rec}")
    
    print("\n" + "=" * 70)


def main():
    """Point d'entrée principal."""
    report = generate_report()
    print_report(report)
    
    # Retourner le code de sortie selon les outils manquants
    missing_pct = len(report["missing_by_category"]) / report["summary"]["total_tools"] * 100
    return 0 if missing_pct < 80 else 1


if __name__ == "__main__":
    sys.exit(main())
