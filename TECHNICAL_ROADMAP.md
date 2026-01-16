# SHARINGAN OS - PLAN D'ACTION TECHNIQUE

## Niveau CRITIQUE - Sécurité & Autonomie

### 1.1 Permissions et Validation Utilisateur
```python
# Pattern à implémenter pour toute action risquée
class AutonomousPermission:
    """Gestion des permissions pour actions autonomes"""
    
    # Niveaux de permission
    AUTO_APPROVED = "auto_approved"      # Actions sûres
    USER_PROMPT = "user_prompt"          # Demander confirmation
    PRE_APPROVED = "pre_approved"        # Validé à l'avance
    BLOCKED = "blocked"                  # Interdit
    
    def check_action(self, action: str, context: Dict) -> PermissionResult:
        """Vérifier si l'action est permise"""
        if action in DANGEROUS_ACTIONS:
            if not self.has_preapproval(action):
                return PermissionResult(
                    status=self.USER_PROMPT,
                    message=f"Action '{action}' nécessite confirmation",
                    risk_level="HIGH"
                )
        return PermissionResult(status=self.AUTO_APPROVED)
```

### 1.2 Sandboxing pour Exécution Risquée
```python
# Isolated execution avec Docker/gVisor
class IsolatedExecutor:
    """Exécution dans environnement isolé"""
    
    def __init__(self, timeout: int = 30, memory_mb: int = 512):
        self.timeout = timeout
        self.memory_limit = memory_mb
    
    def execute_tool(self, command: str, sandbox: str = "docker") -> ExecResult:
        """Exécuter dans sandbox"""
        if sandbox == "docker":
            return self._run_docker(command)
        elif sandbox == "gvisor":
            return self._run_gvisor(command)
        return self._run_local(command)
```

### 1.3 Sécurité - Subprocess
```python
# Utiliser subprocess.run avec validation
def safe_execute(command: List[str], user: str = "nobody") -> Result:
    """Exécution sécurisée avec validation"""
    # 1. Valider la commande
    validated = validate_command(command)
    if not validated.safe:
        raise SecurityError(f"Commande non valide: {validated.reason}")
    
    # 2. Exécuter sans root si possible
    if user != "root" and requires_root(command):
        user = "nobody"
    
    # 3. Limits
    return subprocess.run(
        validated.args,
        timeout=30,
        capture_output=True,
        user=user
    )
```

---

## Niveau URGENT - Bugs & Tests

### 2.1 Tests Unitaires (pytest)
```python
# tests/test_capability_assessment.py
import pytest
from sharingan_capability_assessment import assess_sharingan_capabilities

def test_assessment_returns_dict():
    """Vérifier que l'évaluation retourne un dict"""
    result = assess_sharingan_capabilities()
    assert isinstance(result, dict)
    assert "autonomy_score" in result
    assert "capabilities_status" in result

def test_autonomy_score_range():
    """Score entre 0 et 1"""
    result = assess_sharingan_capabilities()
    assert 0 <= result["autonomy_score"] <= 1

def test_capabilities_status_structure():
    """Vérifier structure des statuts"""
    result = assess_sharingan_capabilities()
    required_keys = ["FONCTIONNEL", "PARTIEL", "LIMITE", "MANQUANT"]
    assert all(k in result["capabilities_status"] for k in required_keys)
```

### 2.2 GitHub Actions CI
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run flake8
        run: pip install flake8 && flake8 . --max-line-length=100 --ignore=E501
      - name: Run bandit
        run: pip install bandit && bandit -r sharingan_app/
  
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install mypy
        run: pip install mypy
      - name: Type check
        run: mypy sharingan_app/ --strict
  
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install pytest
        run: pip install pytest pytest-mock
      - name: Run tests
        run: pytest tests/ --cov=sharingan_app --cov-fail-under=80
```

---

## Niveau IMPORTANT - Qualité Code

### 3.1 Typage MyPy
```python
# sharingan_app/_internal/main.py - Exemple bien typé
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class SystemStatus:
    """Statut du système"""
    ready: bool
    components: List[str]
    version: str = "3.0.0"

class SharinganCore:
    """Core system integrateur"""
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        self.status: SystemStatus = SystemStatus(ready=False, components=[])
        self.logger: logging.Logger = logging.getLogger(__name__)
    
    def initialize(self) -> bool:
        """Initialiser le système"""
        try:
            self.status.ready = True
            self.logger.info("System initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Init failed: {e}")
            return False
    
    def get_status(self) -> SystemStatus:
        """Renvoyer le statut"""
        return self.status
```

### 3.2 Logging Structuré
```python
# logging_config.py
import logging
import json

class StructuredLogger:
    """Logger avec sortie JSON pour parsing"""
    
    @staticmethod
    def setup(level: int = logging.INFO) -> logging.Logger:
        handler = logging.StreamHandler()
        handler.setFormatter(json_log_formatter())
        
        logger = logging.getLogger("sharingan")
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger

def json_log_formatter() -> logging.Formatter:
    """Format JSON pour logs structurés"""
    return logging.Formatter(
        '{"time": "%(asctime)s", "level": "%(levelname)s", '
        '"logger": "%(name)s", "message": "%(message)s"}'
    )
```

### 3.3 Gestion d'Erreurs Centralisée
```python
# exceptions.py
from enum import Enum

class SharinganError(Exception):
    """Erreur de base avec classification"""
    
    def __init__(self, message: str, error_type: str, recoverable: bool):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.recoverable = recoverable

class ErrorType(Enum):
    """Classification des erreurs"""
    AUTH = "authentication"
    PERMISSION = "permission"
    NETWORK = "network"
    EXECUTION = "execution"
    VALIDATION = "validation"
    UNKNOWN = "unknown"

def handle_error(error: Exception) -> Dict[str, Any]:
    """Centraliser le traitement d'erreur"""
    if isinstance(error, SharinganError):
        return {
            "type": error.error_type,
            "message": error.message,
            "recoverable": error.recoverable,
            "user_message": get_user_message(error)
        }
    return {
        "type": ErrorType.UNKNOWN,
        "message": str(error),
        "recoverable": False,
        "user_message": "Erreur inattendue"
    }
```

---

## Niveau MOYEN - Architecture

### 4.1 Structure Proposée
```
sharingan_app/
├── _internal/
│   ├── core/              # Logique métier
│   │   ├── __init__.py
│   │   ├── sharingan_os.py
│   │   └── consciousness.py
│   │
│   ├── ai/                # Providers AI
│   │   ├── __init__.py
│   │   ├── base_provider.py
│   │   ├── tgpt_provider.py
│   │   └── minimax_provider.py
│   │
│   ├── tools/             # Wrappers externes
│   │   ├── __init__.py
│   │   ├── nmap_wrapper.py
│   │   └── execution/
│   │       ├── sandbox.py
│   │       └── safe_subprocess.py
│   │
│   ├── persistence/       # Stockage
│   │   ├── __init__.py
│   │   ├── genome_store.py
│   │   └── migration.py
│   │
│   └── security/          # Sécurité
│       ├── __init__.py
│       ├── permissions.py
│       └── audit.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── config/
│   ├── logging.yaml
│   └── api_keys.env.example
│
└── pyproject.toml
```

---

## Niveau MOYEN - Dépendances

### 5.1 pyproject.toml
```toml
[project]
name = "sharingan-os"
version = "3.0.0"
description = "AI-Powered Cybersecurity Operating System"
requires-python = ">=3.10"
dependencies = [
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    "dataclasses-json>=0.6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.5.0",
    "flake8>=6.1.0",
    "black>=23.9.0",
    "bandit>=1.7.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=sharingan_app --cov-fail-under=80"

[tool.mypy]
python_version = "3.10"
warn_return_any = true
strict_optional = true
```

---

## NIVEAU MOYEN - Observabilité

### 6.1 Métriques Prometheus
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Compteurs
queries_total = Counter(
    'sharingan_queries_total',
    'Total queries processed',
    ['provider', 'status']
)

# Histogramme latence
query_duration = Histogram(
    'sharingan_query_duration_seconds',
    'Query duration',
    ['provider'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

# Gauge autonomie
autonomy_score = Gauge(
    'sharingan_autonomy_score',
    'Current autonomy score'
)

def record_query(provider: str, success: bool, duration: float):
    """Enregistrer métrique de requête"""
    queries_total.labels(
        provider=provider,
        status="success" if success else "error"
    ).inc()
    query_duration.labels(provider=provider).observe(duration)
```

---

## NIVEAU MOYEN - Gouvernance Prompts

### 7.1 Formalisation Prompt
```python
# prompts/registry.py
from typing import Protocol, Dict, Any
from pydantic import BaseModel

class PromptTemplate(BaseModel):
    """Template de prompt versionné"""
    name: str
    version: str
    template: str
    description: str
    parameters: Dict[str, Any]
    
    def render(self, **kwargs) -> str:
        """Générer le prompt final"""
        return self.template.format(**kwargs)

class PromptRegistry:
    """Gestion des prompts avec versioning"""
    
    def __init__(self, prompts_dir: str = "prompts/"):
        self.prompts_dir = Path(prompts_dir)
        self._load_prompts()
    
    def validate_output(self, prompt: str, output: str) -> ValidationResult:
        """Valider la sortie du modèle"""
        # Parser JSON si attendu
        # Vérifier hallucinations avec cross-check
        # Tester patches proposés
        pass
```

---

## TODO LIST - Priorités Immédiates

### Phase 1: Sécurité (Cette semaine)
- [ ] Créer `security/permissions.py` avec validation utilisateur
- [ ] Implémenter `tools/execution/sandbox.py` avec Docker
- [ ] Ajouter bandit au CI
- [ ] Créer SECURITY.md expliquant les limites

### Phase 2: Tests & CI (Semaine prochaine)
- [ ] Ajouter `tests/unit/test_capability_assessment.py`
- [ ] Configurer GitHub Actions CI
- [ ] Atteindre 80% coverage modules critiques

### Phase 3: Qualité (Mois prochain)
- [ ] Ajouter types mypy aux fonctions publiques
- [ ] Configurer black/isort
- [ ] Uniformiser logging

### Phase 4: Architecture (Q1 2026)
- [ ] Réorganiser en couches (core/ai/tools/persistence)
- [ ] Créer pyproject.toml avec dépendances verrouillées
- [ ] Ajouter métriques Prometheus
