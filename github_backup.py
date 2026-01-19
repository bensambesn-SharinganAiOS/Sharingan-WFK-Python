#!/usr/bin/env python3
"""
GitHub Backup System for Sharingan-WFK-Python
Automated backup to GitHub repository with token authentication
"""

import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any, Optional

class GitHubBackupSystem:
    """
    Système de backup automatisé vers GitHub
    Utilise des tokens d'accès personnels pour l'authentification
    """

    def __init__(self, token: Optional[str] = None, repo_url: Optional[str] = None):
        self.project_root = Path(__file__).parent
        self.token = token or os.getenv("GITHUB_TOKEN") or ""
        self.repo_url = repo_url or "https://github.com/your-username/Sharingan-WFK-Python.git"

        # Configuration du remote avec token
        self._configure_git()

    def _configure_git(self) -> None:
        """Configure git avec le token pour les opérations automatisées"""
        if self.token:
            # Créer l'URL avec le token intégré
            if "https://" in self.repo_url:
                # Extraire le domaine et le chemin du repo
                parts = self.repo_url.replace("https://", "").split("/")
                if len(parts) >= 2:
                    domain = parts[0]
                    repo_path = "/".join(parts[1:])
                    self.authenticated_url = f"https://{self.token}@{domain}/{repo_path}"

    def backup_to_github(self, commit_message: Optional[str] = None, branch: str = "main") -> bool:
        """
        Effectue un backup complet vers GitHub
        """
        if not self.token:
            print("❌ Erreur: Aucun token GitHub configuré")
            print("   Définissez GITHUB_TOKEN ou passez-le en paramètre")
            return False

        if not commit_message:
            commit_message = f"Automated backup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        try:
            # Aller dans le répertoire du projet
            os.chdir(self.project_root)

            # Vérifier l'état du repo
            result = subprocess.run(["git", "status", "--porcelain"],
                                  capture_output=True, text=True)

            if result.returncode != 0:
                print("❌ Erreur git status")
                return False

            has_changes = bool(result.stdout.strip())

            if has_changes:
                print("📝 Changements détectés, commit en cours...")

                # Add all changes
                subprocess.run(["git", "add", "."], check=True)

                # Commit
                subprocess.run(["git", "commit", "-m", commit_message], check=True)

                print(f"✅ Commit créé: {commit_message}")
            else:
                print("ℹ️ Aucun changement détecté")

            # Push vers GitHub
            print("🚀 Push vers GitHub...")

            # Utiliser l'URL authentifiée pour le push
            push_cmd = ["git", "push", self.authenticated_url, f"HEAD:{branch}"]

            result = subprocess.run(push_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Backup GitHub réussi!")
                print(f"   Branch: {branch}")
                print(f"   Repository: {self.repo_url.replace('https://', '').split('@')[0]}")
                return True
            else:
                print(f"❌ Erreur push: {result.stderr}")
                return False

        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur git: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur générale: {e}")
            return False

    def get_backup_status(self) -> Dict[str, Any]:
        """Vérifie le statut du backup GitHub"""
        try:
            os.chdir(self.project_root)

            # Dernier commit
            result = subprocess.run(["git", "log", "-1", "--oneline"],
                                  capture_output=True, text=True, check=True)

            last_commit = result.stdout.strip().split()[0] if result.stdout.strip() else "N/A"

            # Branch actuelle
            result = subprocess.run(["git", "branch", "--show-current"],
                                  capture_output=True, text=True, check=True)

            current_branch = result.stdout.strip()

            # Changements non committés
            result = subprocess.run(["git", "status", "--porcelain"],
                                  capture_output=True, text=True, check=True)

            has_uncommitted = bool(result.stdout.strip())

            return {
                "last_commit": last_commit,
                "current_branch": current_branch,
                "has_uncommitted_changes": has_uncommitted,
                "repo_configured": bool(self.token),
                "authenticated_url": bool(self.authenticated_url) if hasattr(self, 'authenticated_url') else False
            }

        except Exception as e:
            return {
                "error": str(e),
                "repo_configured": False
            }

def setup_github_backup(token: str, repo_url: Optional[str] = None) -> GitHubBackupSystem:
    """Configure et retourne un système de backup GitHub"""
    return GitHubBackupSystem(token=token, repo_url=repo_url)

def automated_backup(reason: str = "automated") -> bool:
    """Effectue un backup automatisé"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN non défini")
        return False

    backup_system = GitHubBackupSystem(token=token)
    commit_msg = f"Automated backup: {reason} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    return backup_system.backup_to_github(commit_msg)

# Test du système si appelé directement
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python github_backup.py <github_token> [repo_url]")
        print("Ou définir GITHUB_TOKEN en variable d'environnement")
        sys.exit(1)

    token = sys.argv[1] if len(sys.argv) > 1 else os.getenv("GITHUB_TOKEN")
    repo_url = sys.argv[2] if len(sys.argv) > 2 else None

    if not token:
        print("❌ Token GitHub requis")
        sys.exit(1)

    backup_system = setup_github_backup(token, repo_url)

    print("🔍 Vérification du statut...")
    status = backup_system.get_backup_status()
    print(f"   Repo configuré: {status.get('repo_configured', False)}")
    print(f"   Dernier commit: {status.get('last_commit', 'N/A')}")
    print(f"   Branch: {status.get('current_branch', 'N/A')}")
    print(f"   Changements non committés: {status.get('has_uncommitted_changes', False)}")

    print("\n🚀 Test de backup...")
    success = backup_system.backup_to_github("Test backup - Nouvelle configuration")

    if success:
        print("✅ Système de backup GitHub opérationnel!")
    else:
        print("❌ Échec du backup - Vérifiez la configuration")