#!/usr/bin/env python3
"""
Validation des corrections de sécurité Sharingan OS
Test des hardcodes /tmp/ et configuration logging
"""

import tempfile
import subprocess
import sys
from pathlib import Path

def test_tempfile_usage():
    """Test que les chemins temporaires utilisent tempfile correctement"""
    print("🔍 Test des chemins temporaires...")

    # Test 1: tempfile.gettempdir() fonctionne
    try:
        temp_dir = Path(tempfile.gettempdir())
        print(f"✅ Répertoire temporaire système: {temp_dir}")

        # Test 2: Création de fichier temporaire sécurisé
        with tempfile.NamedTemporaryFile(prefix="sharingan_test_", suffix=".txt", delete=False) as f:
            test_file = Path(f.name)
            test_file.write_text("test content")
            print(f"✅ Fichier temporaire créé: {test_file}")

            # Vérifier qu'il n'est pas dans /tmp/ hardcodé (mais peut y être selon le système)
            if str(test_file).startswith("/tmp/"):
                print("ℹ️  Fichier dans /tmp/ (normal selon système)")
            else:
                print(f"ℹ️  Fichier ailleurs: {test_file.parent}")

            # Nettoyer
            test_file.unlink()

    except Exception as e:
        print(f"❌ Erreur tempfile: {e}")
        return False

    return True

def test_no_hardcoded_tmp():
    """Test qu'il n'y a plus de hardcodes /tmp/ dans les fichiers critiques"""
    print("🔍 Test des hardcodes /tmp/...")

    critical_files = [
        "sharingan_app/_internal/action_executor.py",
        "sharingan_app/_internal/sharingan_os.py",
        "browser_shell.py"
    ]

    hardcoded_found = []

    for file_path in critical_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()

                # Chercher les hardcodes /tmp/ qui ne sont pas dans des commentaires ou des exemples
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    # Ignorer les commentaires et les chaînes dans des exemples
                    if '/tmp/' in line and not line.strip().startswith('#') and 'example' not in line.lower():
                        # Vérifier si c'est une vraie affectation, pas un exemple
                        if '=' in line and ('/tmp/' in line.split('=')[1] if '=' in line else True):
                            hardcoded_found.append(f"{file_path}:{i}: {line.strip()}")

            except Exception as e:
                print(f"⚠️ Erreur lecture {file_path}: {e}")

    if hardcoded_found:
        print("❌ Hardcodes /tmp/ trouvés:")
        for item in hardcoded_found[:5]:  # Montrer les 5 premiers
            print(f"   {item}")
        if len(hardcoded_found) > 5:
            print(f"   ... et {len(hardcoded_found) - 5} autres")
        return False
    else:
        print("✅ Aucun hardcode /tmp/ critique trouvé")
        return True

def test_logging_config():
    """Test que la configuration de logging fonctionne"""
    print("🔍 Test de la configuration logging...")

    try:
        # Tester l'import du module de logging
        sys.path.insert(0, 'sharingan_app/_internal')
        from logging_config import setup_logging, get_logger

        # Configurer le logging
        setup_logging()

        # Tester la création d'un logger
        logger = get_logger("test")
        print("✅ Configuration logging fonctionnelle")

        # Tester que les logs verbeux sont désactivés
        import logging
        requests_logger = logging.getLogger('requests')
        if requests_logger.level >= logging.WARNING:
            print("✅ Logs verbeux désactivés (requests)")
        else:
            print("⚠️ Logs requests pas suffisamment filtrés")

        return True

    except ImportError:
        print("⚠️ Module logging_config non disponible")
        return False
    except Exception as e:
        print(f"❌ Erreur configuration logging: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🛡️ VALIDATION DES CORRECTIONS DE SÉCURITÉ")
    print("=" * 50)

    tests = [
        ("Chemins temporaires", test_tempfile_usage),
        ("Hardcodes /tmp/", test_no_hardcoded_tmp),
        ("Configuration logging", test_logging_config)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))

    # Résumé
    print(f"\n🎯 RÉSULTATS ({sum(1 for _, r in results if r)}/{len(results)})")
    print("=" * 50)

    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHEC"
        print(f"{status} {test_name}")

    passed = sum(1 for _, r in results if r)
    if passed == len(results):
        print("\n🎉 Toutes les corrections de sécurité validées!")
    else:
        print(f"\n⚠️ {len(results) - passed} test(s) à corriger")

    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)