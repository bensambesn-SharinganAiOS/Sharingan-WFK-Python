# GitHub Copilot Instructions

## Configuration

### VS Code
1. Installer l'extension "GitHub Copilot"
2. Se connecter avec son compte GitHub
3. Activer Copilot dans les paramètres

### JetBrains
1. Installer le plugin "GitHub Copilot"
2. Se connecter avec son compte GitHub

### CLI
```bash
npm install -g @githubnext/github-copilot-cli
```

## Project Context

**Sharingan OS** - AI-Powered Cybersecurity Operating System

### Langages principaux
- Python 3.10+
- JavaScript/HTML/CSS

### Stack technique
- AI: tgpt, MiniMax, GLM-4, OpenRouter
- Memory: Genome Memory, AI Memory Manager
- Security: Kali Tools (100+), VPN/Tor integration
- Web: Flask/FastAPI interfaces

### Conventions de code

#### Python
-snake_case pour fonctions/variables
- PascalCase pour les classes
- SCREAMING_SNAKE pour les constantes
- Type hints obligatoires
- Docstrings pour toutes les fonctions publiques
- 4-space indent, 100-char line limit

#### Imports
```python
# stdlib first
import os
import sys
from typing import Dict, List

# third-party
import requests
from dataclasses import dataclass

# local
from sharingan_os import SharinganOS
```

### Outils disponibles

| Catégorie | Outils |
|-----------|--------|
| Network | nmap, masscan, rustscan, netdiscover |
| Web | gobuster, ffuf, sqlmap, nikto |
| Password | hashcat, john, hydra, medusa |
| OSINT | theHarvester, sherlock, spiderfoot |

### Fichiers clés
- `sharingan_app/_internal/main.py` - Point d'entrée principal
- `sharingan_app/_internal/sharingan_os.py` - Core OS
- `sharingan_app/_internal/fake_detector.py` - Détection faux contenus
- `sharingan_app/_internal/check_obligations.py` - Validation code

### Commandes utiles
```bash
# Tests
pytest

# Lint
flake8 . --max-line-length=100

# Type check
python -m mypy --strict
```

## Instructions spécifiques Copilot

### Ne pas générer
- Code malveillant ou d'exploitation
- Contenu fake/démonstration sans implémentation réelle
- Secrets ou tokens hardcodés

### Préférer
- Solutions complètes avec tests
- Type hints et docstrings
- Utilisation des wrappers existants (kali_*, tool_*)
- Validation avec check_obligations.py

### Structure recommandée
```
sharingan_app/_internal/
├── core/          # Fonctions principales
├── tools/         # Wrappers d'outils externes
├── data/          # Fichiers de données
└── tests/         # Tests unitaires
```
