#!/usr/bin/env python3
"""
Sharingan OS - Kali Sequential Downloader
Téléchargement séquentiel des repositories Kali (un par un)
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

def print_banner():
    """Affiche la bannière"""
    print("=" * 60)
    print("🔥 SHARINGAN OS - KALI SEQUENTIAL DOWNLOADER")
    print("=" * 60)
    print("📥 Téléchargement un par un en arrière-plan")
    print("=" * 60)

def get_kali_repos():
    """Liste des repositories Kali prioritaires"""
    return [
        # Réseau (priorité haute)
        ("nmap", "https://github.com/nmap/nmap.git"),
        ("masscan", "https://github.com/robertdavidgraham/masscan.git"),
        ("netdiscover", "https://github.com/netdiscover-scanner/netdiscover.git"),

        # Web (priorité haute)
        ("nikto", "https://github.com/sullo/nikto.git"),
        ("dirsearch", "https://github.com/maurosoria/dirsearch.git"),
        ("gobuster", "https://github.com/OJ/gobuster.git"),
        ("ffuf", "https://github.com/ffuf/ffuf.git"),

        # Password (priorité moyenne)
        ("hashcat", "https://github.com/hashcat/hashcat.git"),
        ("john", "https://github.com/openwall/john.git"),
        ("hydra", "https://github.com/vanhauser-thc/thc-hydra.git"),

        # Exploitation (priorité moyenne)
        ("sqlmap", "https://github.com/sqlmapproject/sqlmap.git"),
        ("searchsploit", "https://github.com/offensive-security/exploitdb.git"),

        # Wireless (priorité moyenne)
        ("aircrack-ng", "https://github.com/aircrack-ng/aircrack-ng.git"),

        # Forensic (priorité moyenne)
        ("binwalk", "https://github.com/ReFirmLabs/binwalk.git"),
        ("volatility", "https://github.com/volatilityfoundation/volatility3.git"),

        # Enumeration (priorité basse)
        ("theharvester", "https://github.com/laramies/theHarvester.git"),
        ("dnsrecon", "https://github.com/darkoperator/dnsrecon.git"),
    ]

def clone_repo(repo_name: str, repo_url: str, base_dir: Path):
    """Clone un repository"""
    repo_path = base_dir / repo_name

    # Vérifier si déjà cloné
    if repo_path.exists() and (repo_path / ".git").exists():
        print(f"⏭️  {repo_name} déjà cloné")
        return True

    start_time = time.time()
    print(f"📥 Clonage {repo_name}...")

    try:
        # Créer le répertoire si nécessaire
        repo_path.parent.mkdir(parents=True, exist_ok=True)

        # Cloner avec timeout
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
            # Calculer la taille
            size = sum(f.stat().st_size for f in repo_path.rglob('*') if f.is_file()) / 1024 / 1024
            print(f"✅ {repo_name} cloné ({size:.1f} MB en {duration:.1f}s)")
            return True
        else:
            print(f"❌ Échec {repo_name}: {result.stderr[:100]}...")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout {repo_name} (5min)")
        return False
    except Exception as e:
        print(f"💥 Erreur {repo_name}: {e}")
        return False

def main():
    """Fonction principale"""
    print_banner()

    base_dir = Path(__file__).parent / "kali_repos"
    base_dir.mkdir(parents=True, exist_ok=True)

    repos = get_kali_repos()
    print(f"📋 {len(repos)} repositories à traiter")

    successful = 0
    failed = 0
    skipped = 0

    for repo_name, repo_url in repos:
        print(f"\\n🔄 Traitement: {repo_name}")
        print("-" * 40)

        if clone_repo(repo_name, repo_url, base_dir):
            successful += 1
        else:
            failed += 1

        # Petite pause entre les téléchargements pour éviter la surcharge
        time.sleep(2)

    # Résumé final
    print("\\n" + "=" * 60)
    print("📊 RÉSULTATS FINAUX")
    print("=" * 60)
    print(f"✅ Réussis: {successful}")
    print(f"❌ Échoués: {failed}")
    print(f"⏭️  Ignorés: {skipped}")
    print(f"📁 Répertoire: {base_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()