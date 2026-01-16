#!/usr/bin/env python3
"""
Sharingan OS - Kali Tools Cleanup & Restart
Nettoie et relance l'intégration Kali
"""

import os
import sys
import shutil
from pathlib import Path

def cleanup_kali_integration():
    """Nettoie l'intégration Kali existante"""
    base_dir = Path(__file__).parent
    kali_repos_dir = base_dir / "kali_repos"
    wrappers_dir = base_dir / "wrappers"

    print("🧹 Cleaning up Kali integration...")

    # Supprimer les répertoires problématiques
    dirs_to_clean = [kali_repos_dir, wrappers_dir]

    for dir_path in dirs_to_clean:
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"  ✅ Removed {dir_path}")
            except Exception as e:
                print(f"  ❌ Failed to remove {dir_path}: {e}")

    print("✅ Cleanup completed")

def restart_kali_bootstrap():
    """Relance le bootstrap Kali"""
    print("🔄 Restarting Kali bootstrap...")

    # Exécuter le bootstrap
    result = os.system("python3 kali_bootstrap.py")

    if result == 0:
        print("✅ Bootstrap restarted successfully")
    else:
        print("❌ Bootstrap restart failed")

def check_status():
    """Vérifie le statut après redémarrage"""
    print("\\n📊 Status after restart:")

    # Exécuter la commande status
    result = os.system("python3 kali_master_controller.py status")

def main():
    """Fonction principale"""
    print("🔧 Sharingan OS - Kali Tools Cleanup & Restart")
    print("=" * 50)

    cleanup_kali_integration()
    restart_kali_bootstrap()
    check_status()

    print("\\n✅ Kali integration cleanup and restart completed!")

if __name__ == "__main__":
    main()