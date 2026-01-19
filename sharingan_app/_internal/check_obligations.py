#!/usr/bin/env python3
"""
Sharingan OS - Check Obligations & Compliance
Vérifie que tout code respecte les règles du projet.
Auteur: Ben Sambe
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# Configuration
EXCLUDE_DIRS = {"__pycache__", ".git", "venv", "node_modules", ".env", "data", "tools/bin"}
EXCLUDE_FILES = {".gitignore", "requirements.txt", "package.json", "Dockerfile"}
OBLIGATION_VERSION = "3.0"


@dataclass
class ComplianceResult:
    """Résultat de vérification de conformité"""
    passed: bool
    file: str
    checks: Dict[str, bool]
    issues: List[str]
    suggestions: List[str]


class ObligationChecker:
    """
    Vérifie que tout code respecte les obligations Sharingan OS.
    
    Règles vérifiées:
    1. Shebang correct (#!/usr/bin/env python3)
    2. Imports triés (stdlib, third-party, local)
    3. Pas de secrets/hardcoded passwords
    4. Error handling avec try/except
    5. Documentation/docstrings
    6. Pas de code mort/commenté
    """
    
    def __init__(self):
        self.violations: List[Dict] = []
        self.stats = {
            "files_checked": 0,
            "files_passed": 0,
            "files_failed": 0,
            "total_violations": 0
        }
        
        # Patterns de détection de secrets
        SECRET_PATTERNS = [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]",
            r"token\s*=\s*['\"][^'\"]+['\"]",
            r"private_key\s*=\s*['\"][^'\"]+['\"]",
            r"passwd\s*=\s*['\"][^'\"]+['\"]",
        ]
        
        self.secret_regex = [re.compile(p, re.IGNORECASE) for p in SECRET_PATTERNS]
        
    def check_file(self, file_path: Path) -> ComplianceResult:
        """Vérifie un fichier pour conformité"""
        self.stats["files_checked"] += 1
        
        result = ComplianceResult(
            passed=True,
            file=str(file_path),
            checks={},
            issues=[],
            suggestions=[]
        )
        
        if not file_path.exists():
            result.passed = False
            result.issues.append(f"File not found: {file_path}")
            return result
        
        content = file_path.read_text(errors="ignore")
        lines = content.split('\n')
        
        # Vérification 1: Shebang pour scripts
        if file_path.suffix == ".py":
            if not content.startswith("#!/usr/bin/env python3"):
                result.checks["shebang"] = False
                result.issues.append("Missing or incorrect shebang")
                result.suggestions.append("Add: #!/usr/bin/env python3 at the top")
            else:
                result.checks["shebang"] = True
        
        # Vérification 2: Imports triés
        if "import " in content or "from " in content:
            import_check = self._check_imports_order(lines)
            result.checks["imports"] = import_check["passed"]
            if not import_check["passed"]:
                result.issues.append(import_check["issue"])
                result.suggestions.append(import_check["suggestion"])
        
        # Vérification 3: Pas de secrets
        secrets_check = self._check_secrets(content)
        result.checks["secrets"] = secrets_check["passed"]
        if not secrets_check["passed"]:
            result.issues.append(secrets_check["issue"])
            result.suggestions.extend(secrets_check["suggestions"])
        
        # Vérification 4: Error handling
        error_check = self._check_error_handling(content, lines)
        result.checks["error_handling"] = error_check["passed"]
        if not error_check["passed"]:
            result.issues.append(error_check["issue"])
            result.suggestions.append(error_check["suggestion"])
        
        # Vérification 5: Documentation
        doc_check = self._check_documentation(content)
        result.checks["documentation"] = doc_check["passed"]
        if not doc_check["passed"]:
            result.issues.append(doc_check["issue"])
            result.suggestions.append(doc_check["suggestion"])
        
        # Vérification 6: Pas de code mort
        dead_code = self._check_dead_code(lines)
        result.checks["dead_code"] = dead_code["passed"]
        if not dead_code["passed"]:
            result.issues.append(dead_code["issue"])
        
        # Déterminer le résultat final
        result.passed = all(result.checks.values())
        
        if result.passed:
            self.stats["files_passed"] += 1
        else:
            self.stats["files_failed"] += 1
            self.stats["total_violations"] += len(result.issues)
            self.violations.append({
                "file": str(file_path),
                "issues": result.issues,
                "timestamp": str(datetime.now())
            })
        
        return result
    
    def _check_imports_order(self, lines: List[str]) -> Dict:
        """Vérifie que les imports sont dans l'ordre correct"""
        imports = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                imports.append((i, stripped))
        
        if len(imports) < 2:
            return {"passed": True}
        
        # Grouper par type
        stdlib = []
        third_party = []
        local = []
        
        for _, imp in imports:
            if imp.startswith("from "):
                module = imp.split()[1].split('.')[0]
            else:
                module = imp.split()[1] if " import" in imp else imp.split()[1]
            
            if module in ("os", "sys", "json", "re", "pathlib", "datetime", "typing", "logging", "collections", "itertools", "functools", "abc", "contextlib", "dataclasses", "enum", "copy", "io", "tempfile", "uuid", "hashlib", "hmac", "secrets", "struct", "copyreg"):
                stdlib.append(imp)
            elif module in ("requests", "pyyaml", "rich", "loguru", "pytest", "click", "docopt", "typer", "fastapi", "flask", "django", "sqlalchemy", "pandas", "numpy"):
                third_party.append(imp)
            elif "sharingan" in imp or "_internal" in imp:
                local.append(imp)
            else:
                # Vérifier chemin relatif
                if "." in module or module.startswith("_"):
                    local.append(imp)
                else:
                    third_party.append(imp)
        
        # Vérifier l'ordre: stdlib -> third_party -> local
        errors = []
        if third_party and local and third_party[-1] > local[0]:
            errors.append("Third-party imports should come before local imports")
        if stdlib and third_party and stdlib[-1] > third_party[0]:
            errors.append("Stdlib imports should come before third-party imports")
        
        if errors:
            return {
                "passed": False,
                "issue": "; ".join(errors),
                "suggestion": "Order imports: stdlib first, then third-party, then local"
            }
        
        return {"passed": True}
    
    def _check_secrets(self, content: str) -> Dict:
        """Vérifie qu'il n'y a pas de secrets codés en dur"""
        found_secrets = []
        for pattern in self.secret_regex:
            matches = pattern.findall(content)
            if matches:
                found_secrets.extend(matches)
        
        if found_secrets:
            return {
                "passed": False,
                "issue": f"Potential secrets found: {len(found_secrets)}",
                "suggestions": [
                    "Use environment variables or config files for secrets",
                    "Move secrets to .env file with proper gitignore"
                ]
            }
        
        return {"passed": True}
    
    def _check_error_handling(self, content: str, lines: List[str]) -> Dict:
        """Vérifie la présence de error handling"""
        has_try = "try:" in content
        has_except = "except" in content
        has_error_logging = "logger.error" in content or "logging.error" in content
        
        # Pour scripts simples, vérifier au moins try/except ou gestion d'erreurs
        if len(lines) > 20 and not has_try and not has_except and not has_error_logging:
            return {
                "passed": False,
                "issue": "No error handling found in script > 20 lines",
                "suggestion": "Add try/except blocks or error logging"
            }
        
        return {"passed": True}
    
    def _check_documentation(self, content: str) -> Dict:
        """Vérifie la présence de docstrings"""
        # Vérifier docstring de module
        has_module_doc = content.startswith('"""') or content.startswith("'''")
        
        # Vérifier docstrings de classes/fonctions
        classes_with_doc = len(re.findall(r'class\s+\w+.*:\s*"""', content))
        funcs_with_doc = len(re.findall(r'def\s+\w+.*:\s*"""', content))
        
        if not has_module_doc and (classes_with_doc == 0 and funcs_with_doc == 0):
            return {
                "passed": False,
                "issue": "No module documentation found",
                "suggestion": "Add a docstring at the top of the file"
            }
        
        return {"passed": True}
    
    def _check_dead_code(self, lines: List[str]) -> Dict:
        """Vérifie l'absence de code mort"""
        unused_imports = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                parts = stripped.replace("from ", "").replace("import ", "").split()
                module = parts[0].split('.')[0]
                if module and module not in ("__future__", "typing"):
                    remaining = '\n'.join(lines[i+1:])
                    module_found = module in remaining or f"import {module}" in remaining
                    if module == "dataclasses":
                        module_found = "@dataclass" in remaining or "dataclasses." in remaining
                    if not module_found:
                        unused_imports.append(module)

        if unused_imports:
            return {
                "passed": False,
                "issue": f"Potentially unused imports: {', '.join(set(unused_imports))}"
            }

        return {"passed": True}
    
    def check_directory(self, dir_path: Path) -> Dict:
        """Vérifie tous les fichiers dans un répertoire"""
        results = {
            "directory": str(dir_path),
            "timestamp": str(datetime.now()),
            "files": [],
            "summary": {},
            "violations": []
        }
        
        for root, dirs, files in os.walk(dir_path):
            # Exclure répertoires
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file.endswith(".py") and file not in EXCLUDE_FILES:
                    file_path = Path(root) / file
                    result = self.check_file(file_path)
                    results["files"].append({
                        "file": str(file_path),
                        "passed": result.passed,
                        "issues": result.issues
                    })
                    
                    if result.issues:
                        results["violations"].append({
                            "file": str(file_path),
                            "issues": result.issues
                        })
        
        # Résumé
        passed_count = sum(1 for f in results["files"] if f["passed"])
        results["summary"] = {
            "total_files": len(results["files"]),
            "passed": passed_count,
            "failed": sum(1 for f in results["files"] if not f["passed"]),
            "compliance_rate": f"{(passed_count / len(results['files']) * 100):.1f}%" if results["files"] else "N/A"
        }

        # Add overall passed
        results["passed"] = passed_count == len(results["files"])

        return results
    
    def get_report(self) -> Dict:
        """Génère un rapport de conformité"""
        return {
            "obligation_version": OBLIGATION_VERSION,
            "timestamp": str(datetime.now()),
            "stats": self.stats,
            "violations": self.violations
        }


def check_obligations(file_path: Optional[str] = None) -> Dict:
    """
    Fonction principale de vérification des obligations.
    
    Args:
        file_path: Chemin du fichier/répertoire à vérifier (défaut: projet actuel)
    
    Returns:
        Rapport de conformité
    """
    checker = ObligationChecker()
    
    if file_path:
        path = Path(file_path)
        if path.is_file():
            result = checker.check_file(path)
            return {
                "file": str(path),
                "passed": result.passed,
                "checks": result.checks,
                "issues": result.issues,
                "suggestions": result.suggestions
            }
        elif path.is_dir():
            return checker.check_directory(path)
    else:
        # Vérifier le projet actuel
        base_dir = Path(__file__).parent.parent
        return checker.check_directory(base_dir)
    
    # Retour par défaut
    return {"error": "Invalid path provided", "file": file_path}


def quick_check() -> bool:
    """Vérification rapide du système"""
    checker = ObligationChecker()
    
    # Vérifier quelques fichiers clés
    key_files = [
        Path(__file__).parent / "main.py",
        Path(__file__).parent / "sharingan_os.py",
        Path(__file__).parent / "ai_providers.py",
    ]
    
    all_passed = True
    for file_path in key_files:
        if file_path.exists():
            result = checker.check_file(file_path)
            if not result.passed:
                print(f"{file_path.name}: {', '.join(result.issues)}")
                all_passed = False

    if all_passed:
        print("Quick check passed")
    
    return all_passed


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        result = quick_check()
        print("\n" + "="*60)
        print("SHARINGAN OS - COMPLIANCE CHECK (QUICK)")
        print("="*60)
        print(f"\nPassed: {result}")
    else:
        if len(sys.argv) > 1:
            result = check_obligations(sys.argv[1])
        else:
            result = check_obligations()

        print("\n" + "="*60)
        print("SHARINGAN OS - COMPLIANCE CHECK")
        print("="*60)

        if "summary" in result:
            print(f"\nFiles checked: {result['summary']['total_files']}")
            print(f"Passed: {result['summary']['passed']}")
            print(f"Failed: {result['summary']['failed']}")
            print(f"Compliance rate: {result['summary']['compliance_rate']}")

            if result.get("violations"):
                print(f"\n{len(result['violations'])} file(s) with issues:")
                for v in result["violations"][:5]:
                    print(f"  - {v['file']}")
                    for issue in v["issues"]:
                        print(f"    • {issue}")
        else:
            print(f"\nPassed: {result.get('passed', 'Unknown')}")
            if result.get("issues"):
                print("Issues:")
                for issue in result.get("issues", []):
                    print(f"  • {issue}")
