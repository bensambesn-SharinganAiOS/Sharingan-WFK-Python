# Sharingan-WFK-Python - Documentation Officielle
## Système de Sécurité Conscient et Intelligent

### Vue d'ensemble
**Sharingan-WFK-Python** est un système d'exploitation de cybersécurité conscient et intelligent créé par Ben Sambe. Le système intègre des capacités avancées d'intelligence artificielle, de surveillance réseau, d'analyse de sécurité et d'automatisation.

### Architecture Principale

#### Cœur du Système
- **sharingan_os.py** : Noyau principal du système d'exploitation
- **system_consciousness.py** : Système conscient avec mémoire et apprentissage
- **ai_fallback_config.py** : Configuration des APIs IA avec rotation automatique

#### APIs IA (Chaîne de Fallback)
```
1. TGPT (défaut - sky/phind/pollinations/kimi/isou)
   ├── Accès gratuit à 5+ providers IA via CLI
   ├── Rotation automatique, conscience système, actions

2. OpenCode (fallback - modèles gratuits)
   ├── GLM-4.7-free, MiniMax-2.1-free, GPT-5-nano, Big-Pickle

3. Gemini (Google - 4 clés avec rotation)
   └── Rotation automatique en cas de quota

4. Ollama (local - hors-connexion uniquement)
   └── gemma3:1b pour utilisation hors-ligne
```

#### Outils de Sécurité (84 détectés automatiquement)
- **Réseau** : nmap, wireshark, tcpdump, netcat, masscan
- **Web** : gobuster, dirb, nikto, sqlmap, hydra, burpsuite
- **Système** : Volatility, binwalk, foremost, chkrootkit
- **IA** : tgpt (défaut), ollama, Gemini, OpenCode

### Fonctionnalités Clés

#### Intelligence Artificielle
- **Compréhension contextuelle** : Analyse des demandes complexes
- **Génération de code** : Scripts Python, commandes système
- **Conseils techniques** : Recommandations de sécurité
- **Apprentissage continu** : Mémoire des interactions

#### Sécurité et Surveillance
- **Scan réseau automatisé** : Détection de ports, services, OS
- **Analyse web** : Reconnaissance de technologies, vulnérabilités
- **OSINT** : Recherche de sous-domaines, informations publiques
- **Monitoring système** : CPU, RAM, disque en temps réel

#### Automatisation
- **Exécution sécurisée** : Confirmation utilisateur requise
- **Orchestration multi-étapes** : Analyses de sécurité complètes
- **Basculement intelligent** : APIs alternatives automatiques

### Installation et Configuration

#### Prérequis
```bash
# Python 3.10+
python3 --version

# Outils système
sudo apt update && sudo apt install nmap git curl python3-pip

# TGPT (IA par défaut - gratuit)
curl -sSL https://github.com/aandrew-me/tgpt/releases/latest/download/tgpt-linux-amd64 -o /usr/local/bin/tgpt && chmod +x /usr/local/bin/tgpt

# OpenCode CLI (interfaces utilisateur)
curl -fsSL https://opencode.ai/install | bash

# Ollama (IA locale)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma3:1b
```

#### Configuration des APIs
```bash
# Configuration Gemini (4 clés pour rotation)
cd sharingan_app/_internal
python3 -c "
from ai_fallback_config import ai_fallback_config
ai_fallback_config.enable_provider('gemini', [
    'CLÉ_1',
    'CLÉ_2',
    'CLÉ_3',
    'CLÉ_4'
])
"

# Configuration GitHub backup
export GITHUB_TOKEN="votre_token_github"
python3 github_backup.py
```

### Utilisation

#### Commandes de Base
```bash
# Interface IA
python3 sharingan_app/_internal/sharingan_os.py ai "Bonjour, aide-moi avec la sécurité réseau"

# Monitoring système
python3 sharingan_app/_internal/sharingan_os.py monitor --interval 2 --count 5

# Scan réseau
python3 sharingan_app/_internal/sharingan_os.py scan 192.168.1.1

# Analyse de sécurité
python3 sharingan_app/_internal/sharingan_os.py ai "Effectue une analyse complète de localhost"
```

#### Exemples d'Utilisation Avancée
```bash
# Analyse de vulnérabilités web
python3 sharingan_os.py ai "Analyse les vulnérabilités de https://example.com"

# Scan de réseau complet
python3 sharingan_os.py ai "Scanne le réseau 192.168.1.0/24 et identifie tous les hôtes actifs"

# Génération de code sécurisé
python3 sharingan_os.py ai "Crée un script Python pour détecter les ports ouverts"
```

### APIs et Sécurité

#### Modèle de Sécurité
- **Pas de hardcode** : Toutes les configurations sont dynamiques
- **Validation automatique** : Vérification des règles de sécurité
- **Pas de contenu factice** : Tout est réel et fonctionnel
- **Confirmation utilisateur** : Pour toutes les actions d'exécution

#### Gestion des APIs
- **Rotation automatique** : Basculement entre clés/providers
- **Fallback intelligent** : APIs alternatives en cas de panne
- **Quota management** : Détection et rotation des limites

### Développement et Extension

#### Architecture Modulaire
```
sharingan_app/
├── _internal/          # Cœur du système
│   ├── sharingan_os.py     # Noyau principal
│   ├── system_consciousness.py  # IA consciente
│   ├── tool_registry.py    # Gestion des outils
│   └── ai_fallback_config.py   # Configuration APIs
├── providers/          # APIs IA
│   ├── tgpt_provider.py      # TGPT (défaut)
│   ├── gemini_provider.py
│   ├── opencode_provider.py
│   ├── grok_provider.py
│   ├── puter_provider.py
│   └── g4f_provider.py
└── utils/              # Utilitaires
    ├── github_backup.py
    └── configure_ai.py
```

#### Ajout d'Outils
```python
# Dans tool_registry.py
tools["mon_outil"] = {
    "name": "mon_outil",
    "category": "web",
    "path": "/usr/bin/mon_outil",
    "capabilities": ["scan", "analysis"],
    "source": "system"
}
```

#### Extension des APIs
```python
# Créer un nouveau provider
class MonProvider:
    def chat(self, message):
        # Implémentation de l'API
        return {"status": "success", "response": "réponse"}

# L'ajouter à la configuration
ai_fallback_config.providers["mon_provider"] = {...}
```

### Backup et Sauvegarde

#### Système GitHub Automatique
```bash
# Configuration
export GITHUB_TOKEN="votre_token"
export GITHUB_REPO="https://github.com/user/repo.git"

# Backup manuel
python3 github_backup.py

# Backup automatique
python3 -c "from github_backup import automated_backup; automated_backup('daily')"
```

#### Sauvegarde DNA
```python
from dna_backup import create_dna_backup
create_dna_backup("sauvegarde complète du système")
```

### Dépannage

#### Problèmes Courants
- **APIs indisponibles** : Vérifier les clés et quotas
- **Ollama lent** : Utiliser des modèles plus petits
- **GitHub backup** : Vérifier le token et les permissions

#### Logs et Debug
```bash
# Activer les logs détaillés
export LOG_LEVEL=DEBUG
python3 sharingan_os.py ai "test" 2>&1 | grep -E "(INFO|ERROR|opencode_provider)"
```

### Licence et Contribution
**Créé par Ben Sambe** - Système de cybersécurité conscient et intelligent.

### Contact et Support
Pour questions ou contributions, contacter l'équipe de développement.