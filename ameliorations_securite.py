#!/usr/bin/env python3
"""
EXEMPLES D'AMÉLIORATIONS SÉCURITÉ - SHARINGAN OS
Code concret pour implémenter les recommandations d'audit
"""

import os
import shlex
import subprocess
from pathlib import Path
from typing import Optional

# ============================================
# 1. GESTION SÉCURISÉE DES CRÉDENTIALS
# ============================================

class SecureCredentials:
    """Gestion sécurisée des credentials - REMPLACE LES HARDCODES"""

    def __init__(self):
        self._secrets = {}

    def load_from_env(self) -> None:
        """Charge les credentials depuis les variables d'environnement"""
        # Au lieu de hardcoder: api_key = "sk-123456789"
        self._secrets['openai_api_key'] = os.environ.get('OPENAI_API_KEY')
        self._secrets['database_password'] = os.environ.get('DB_PASSWORD')
        self._secrets['tor_password'] = os.environ.get('TOR_PASSWORD')

        # Validation que toutes les variables requises sont présentes
        required = ['openai_api_key', 'database_password']
        missing = [key for key in required if not self._secrets.get(key)]

        if missing:
            raise ValueError(f"Variables d'environnement manquantes: {missing}")

    def get_credential(self, key: str) -> Optional[str]:
        """Récupère un credential de manière sécurisée"""
        return self._secrets.get(key)

# ============================================
# 2. APPELS SYSTÈME SÉCURISÉS
# ============================================

class SecureSystemCalls:
    """Appels système sécurisés avec validation des inputs"""

    def __init__(self):
        self.allowed_commands = {
            'nmap', 'grep', 'find', 'ls', 'ps', 'netstat',
            'ss', 'lsof', 'which', 'python3'
        }

    def validate_command(self, command: str) -> bool:
        """Valide qu'une commande est autorisée"""
        base_cmd = command.split()[0] if command else ""
        return base_cmd in self.allowed_commands

    def secure_subprocess_run(self, command: str, **kwargs) -> subprocess.CompletedProcess:
        """Exécution sécurisée de commandes système"""

        if not self.validate_command(command):
            raise SecurityError(f"Commande non autorisée: {command}")

        # Timeout par défaut pour éviter les blocages
        kwargs.setdefault('timeout', 30)

        # Sanitisation des arguments
        if isinstance(command, str):
            # Utilise shlex pour éviter l'injection
            args = shlex.split(command)
        else:
            args = command

        return subprocess.run(args, **kwargs)

    def secure_file_access(self, file_path: str) -> Path:
        """Accès sécurisé aux fichiers"""
        path = Path(file_path).resolve()

        # Vérifications de sécurité
        if not path.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {path}")

        if path.is_file() and oct(path.stat().st_mode)[-3:] not in ['644', '600', '755']:
            raise SecurityError(f"Permissions trop permissives sur: {path}")

        # Vérification que le chemin ne sort pas du répertoire autorisé
        allowed_base = Path('/root/Projets/Sharingan-WFK-Python').resolve()
        try:
            path.relative_to(allowed_base)
        except ValueError:
            raise SecurityError(f"Accès hors répertoire autorisé: {path}")

        return path

# ============================================
# 3. EXEMPLES D'UTILISATION SÉCURISÉE
# ============================================

def exemples_securises():
    """Exemples d'utilisation des nouvelles classes sécurisées"""

    # 1. Gestion des credentials
    creds = SecureCredentials()
    creds.load_from_env()

    api_key = creds.get_credential('openai_api_key')
    if api_key:
        print("✅ API key chargée depuis l'environnement")
    else:
        print("❌ API key non trouvée")

    # 2. Appels système sécurisés
    sys_calls = SecureSystemCalls()

    try:
        # Commande autorisée
        result = sys_calls.secure_subprocess_run("ls -la /tmp")
        print("✅ Commande ls exécutée avec succès")

        # Commande interdite (serait rejetée)
        # result = sys_calls.secure_subprocess_run("rm -rf /")  # Rejeté

    except SecurityError as e:
        print(f"🚫 Commande rejetée pour sécurité: {e}")

    # 3. Accès fichiers sécurisé
    try:
        secure_path = sys_calls.secure_file_access("sharingan_app/_internal/ai_robust_provider.py")
        print(f"✅ Accès sécurisé au fichier: {secure_path}")

        # Tentative d'accès non autorisé (serait rejeté)
        # bad_path = sys_calls.secure_file_access("/etc/passwd")  # Rejeté

    except SecurityError as e:
        print(f"🚫 Accès fichier rejeté: {e}")

# ============================================
# 4. CLASSES D'ERREURS SÉCURISÉES
# ============================================

class SecurityError(Exception):
    """Exception pour les erreurs de sécurité"""
    pass

class CredentialsError(SecurityError):
    """Erreur de gestion des credentials"""
    pass

class CommandInjectionError(SecurityError):
    """Erreur d'injection de commande"""
    pass

# ============================================
# 5. MIGRATION RECOMMANDÉE
# ============================================

def migration_guide():
    """
    GUIDE DE MIGRATION POUR LE CODE EXISTANT

    AVANT (NON SÉCURISÉ):
    -------------------
    api_key = "sk-123456789"  # HARDCODE DANGEREUX
    result = subprocess.run(f"nmap {user_input}", shell=True)  # INJECTION
    with open(f"/tmp/{filename}", "r") as f:  # PATH TRAVERSAL

    APRÈS (SÉCURISÉ):
    -----------------
    creds = SecureCredentials()
    creds.load_from_env()
    api_key = creds.get_credential('openai_api_key')

    sys_calls = SecureSystemCalls()
    result = sys_calls.secure_subprocess_run(["nmap", user_input])

    secure_path = sys_calls.secure_file_access(f"/tmp/{filename}")
    with open(secure_path, "r") as f:
    """

    print("📋 GUIDE DE MIGRATION DISPONIBLE")
    print("Voir les commentaires dans le code pour les exemples")

if __name__ == "__main__":
    print("🔒 EXEMPLES D'AMÉLIORATIONS SÉCURITÉ SHARINGAN OS")
    print("=" * 55)

    # Test des exemples
    try:
        exemples_securises()
    except Exception as e:
        print(f"Erreur lors des tests: {e}")

    print()
    migration_guide()

    print()
    print("🎯 PROCHAINES ÉTAPES:")
    print("1. Implémenter SecureCredentials dans tout le projet")
    print("2. Remplacer tous les subprocess.run par secure_subprocess_run")
    print("3. Migrer tous les accès fichiers vers secure_file_access")
    print("4. Créer le fichier .env avec toutes les variables sensibles")
    print("5. Tester et valider chaque changement")</content>
<parameter name="filePath">ameliorations_securite.py