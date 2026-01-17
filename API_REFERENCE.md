# 🔌 Guide d'API Complet - Sharingan OS

## Vue d'Ensemble

Sharingan OS fournit une **API unifiée et intuitive** permettant aux développeurs d'accéder à toutes les capacités du système : navigation web hybride, intelligence artificielle multi-providers, outils Kali intégrés, systèmes de mémoire évolutifs, et conscience autonome.

### 📚 **Points d'Entrée API**

```python
# Point d'entrée principal
from sharingan_app._internal.sharingan_os import SharinganOS

# Initialisation du système complet
os_instance = SharinganOS()

# Utilisation des capacités individuelles
from browser_shell import go, read, search, js
from ai_providers import AIProvidersManager
from kali_master_controller import KaliMasterController
```

---

## 🌐 API Navigation Web (Browser Shell)

### **Navigation Intelligente**

#### `go(url: str, wait_for: str = "load") -> Tuple[bool, str]`
Navigation universelle avec stratégies d'attente intelligentes.

**Paramètres:**
- `url`: URL destination (supporte tous protocoles)
- `wait_for`: Condition d'attente (`"load"`, `"domcontentloaded"`, `"networkidle"`)

**Retour:** `(success: bool, message: str)`

**Exemple:**
```python
success, msg = await go("https://github.com/microsoft/vscode")
if success:
    print("Navigation réussie")
else:
    print(f"Erreur: {msg}")
```

#### `read(selector: str = None, ocr: bool = False) -> Tuple[bool, str]`
Extraction de contenu avec fallback OCR intelligent.

**Paramètres:**
- `selector`: Sélecteur CSS/XPath (optionnel)
- `ocr`: Utiliser OCR si extraction DOM échoue

**Retour:** `(success: bool, content: str)`

**Exemples:**
```python
# Extraire tout le contenu de la page
success, content = await read()

# Extraire un élément spécifique
success, title = await read("h1.title")

# Extraction avec OCR fallback
success, text = await read(ocr=True)
```

#### `search(query: str, engine: str = "google") -> Tuple[bool, Dict]`
Recherche multi-moteurs avec parsing intelligent.

**Paramètres:**
- `query`: Terme de recherche
- `engine`: Moteur (`"google"`, `"bing"`, `"duckduckgo"`)

**Retour:** `(success: bool, results: Dict)`

**Exemple:**
```python
success, results = await search("cybersecurity tools", "google")
for result in results['organic_results'][:5]:
    print(f"{result['title']}: {result['link']}")
```

### **Interactions Web**

#### `click(selector: str, x_offset: int = 0, y_offset: int = 0) -> Tuple[bool, str]`
Clic intelligent avec gestion d'erreurs.

**Paramètres:**
- `selector`: Sélecteur CSS de l'élément
- `x_offset/y_offset`: Décalage en pixels

**Retour:** `(success: bool, message: str)`

**Exemple:**
```python
# Clic sur un bouton
success, msg = await click("button.submit")

# Clic avec offset de précision
success, msg = await click(".menu-item", x_offset=5, y_offset=10)
```

#### `type_text(selector: str, text: str, human_like: bool = True) -> Tuple[bool, str]`
Saisie de texte avec comportement humain réaliste.

**Paramètres:**
- `selector`: Champ de saisie cible
- `text`: Texte à saisir
- `human_like`: Simulation frappe humaine

**Retour:** `(success: bool, message: str)`

**Exemple:**
```python
# Saisie normale
success, msg = await type_text("#search-input", "python programming")

# Saisie avec rythme humain
success, msg = await type_text("#email", "user@example.com", human_like=True)
```

#### `scroll(amount: int, direction: str = "down", smooth: bool = True) -> Tuple[bool, str]`
Défilement naturel avec accélération/décélération.

**Paramètres:**
- `amount`: Quantité de pixels
- `direction`: Direction (`"up"`, `"down"`, `"left"`, `"right"`)
- `smooth`: Animation fluide

**Retour:** `(success: bool, message: str)`

**Exemple:**
```python
# Scroll vers le bas
success, msg = await scroll(500, "down", smooth=True)

# Scroll rapide vers le haut
success, msg = await scroll(1000, "up", smooth=False)
```

### **Exécution JavaScript**

#### `js(script: str, timeout: int = 5000) -> Tuple[bool, Any]`
Exécution JavaScript avec timeout sécurisé.

**Paramètres:**
- `script`: Code JavaScript à exécuter
- `timeout`: Timeout en millisecondes

**Retour:** `(success: bool, result: Any)`

**Exemples:**
```python
# Récupérer le titre de la page
success, title = await js("return document.title")

# Extraire des données structurées
success, data = await js("""
    return Array.from(document.querySelectorAll('.product'))
        .map(product => ({
            name: product.querySelector('.name').textContent,
            price: product.querySelector('.price').textContent
        }))
""")

# Attendre un élément dynamiquement chargé
success, element = await js("""
    return new Promise((resolve) => {
        const checkElement = () => {
            const el = document.querySelector('.dynamic-content');
            if (el) resolve(el.textContent);
            else setTimeout(checkElement, 100);
        };
        checkElement();
    });
""", timeout=10000)
```

### **Capture & Screenshot**

#### `screenshot(selector: str = None, format: str = "png") -> Tuple[bool, bytes]`
Capture d'écran sélective ou complète.

**Paramètres:**
- `selector`: Élément spécifique (optionnel)
- `format`: Format (`"png"`, `"jpeg"`, `"webp"`)

**Retour:** `(success: bool, image_data: bytes)`

**Exemples:**
```python
# Screenshot complet de la page
success, image = await screenshot()

# Screenshot d'un élément spécifique
success, image = await screenshot("#main-content")

# Sauvegarde du screenshot
if success:
    with open("screenshot.png", "wb") as f:
        f.write(image)
```

---

## 🤖 API Intelligence Artificielle

### **Gestionnaire de Providers IA**

```python
from ai_providers import AIProvidersManager

# Initialisation
ai_manager = AIProvidersManager()

# Chat completion avec routage automatique
response = await ai_manager.chat_completion(
    messages=[{"role": "user", "content": "Hello, how are you?"}],
    strategy="adaptive"  # Choix automatique du meilleur provider
)
```

### **Méthodes Disponibles**

#### `chat_completion(messages: List[Dict], **kwargs) -> Dict`
Chat completion avec fallback automatique.

**Paramètres:**
- `messages`: Liste de messages (`[{"role": "user", "content": "..."}]`)
- `strategy`: Stratégie de routage (`"adaptive"`, `"cost"`, `"performance"`, `"reliability"`)
- `temperature`: Créativité (0.0-1.0)
- `max_tokens`: Longueur maximale de réponse
- `model`: Modèle spécifique (optionnel)

**Retour:**
```python
{
    "success": True,
    "response": "Hello! I'm doing well, thank you for asking.",
    "provider": "tgpt",
    "model": "gpt-3.5-turbo",
    "tokens_used": 24,
    "response_time": 1.2,
    "cost_estimate": 0.0
}
```

#### `analyze_code(code: str, language: str = None) -> Dict`
Analyse spécialisée du code.

#### `generate_content(prompt: str, content_type: str = "text") -> Dict`
Génération de contenu créatif.

#### `solve_problem(problem: str, domain: str = "general") -> Dict`
Résolution de problèmes.

### **Providers Disponibles**

| Provider | Avantages | Cas d'usage |
|----------|-----------|-------------|
| **TGPT** | Gratuit, rapide, illimité | Chat général, prototyping |
| **MiniMax** | Haute qualité, fiable | Analyse complexe, production |
| **GLM-4** | Multimodal, créatif | Génération créative, vision |
| **Ollama** | Local, privé | Usage hors-ligne, confidentialité |

---

## 🛠️ API Outils Kali

### **Contrôleur Maître Kali**

```python
from kali_master_controller import KaliMasterController

# Initialisation
kali = KaliMasterController()

# Exécution d'un outil
result = await kali.execute_tool("network", "nmap_scan",
                                target="192.168.1.0/24",
                                options="-sV -O")
```

### **Catégories d'Outils**

#### **Réseau**
```python
# Nmap - Scanner réseau ultime
result = await kali.execute_tool("network", "nmap_scan",
                                target="target.com",
                                ports="-p 1-1000",
                                options="-sV -O")

# Masscan - Scan haute vitesse
result = await kali.execute_tool("network", "masscan_scan",
                                target="10.0.0.0/8",
                                ports="80,443",
                                rate="100000")
```

#### **Web**
```python
# Nikto - Scanner de vulnérabilités
result = await kali.execute_tool("web", "nikto_scan",
                                target="https://example.com")

# Gobuster - Énumération de répertoires
result = await kali.execute_tool("web", "gobuster_dir_enum",
                                url="https://example.com",
                                wordlist="/usr/share/wordlists/dirb/common.txt")
```

#### **Mots de Passe**
```python
# Hydra - Brute force
result = await kali.execute_tool("password", "hydra_bruteforce",
                                target="192.168.1.100",
                                service="ssh",
                                userlist="users.txt",
                                passlist="passwords.txt")

# Hashcat - Cracking GPU
result = await kali.execute_tool("password", "hashcat_crack",
                                hashfile="hashes.txt",
                                wordlist="rockyou.txt",
                                mode="0")  # MD5
```

#### **Exploitation**
```python
# Metasploit - Framework d'exploitation
result = await kali.execute_tool("exploitation", "metasploit_exploit",
                                module="exploit/windows/smb/ms17_010_eternalblue",
                                target="192.168.1.100")

# SQLMap - Injection SQL
result = await kali.execute_tool("exploitation", "sqlmap_test",
                                url="https://vulnerable.com/page?id=1")
```

---

## 🧬 API Systèmes de Mémoire

### **Mémoire Génome (ADN du Système)**

```python
from genome_memory import GenomeMemory

genome = GenomeMemory()

# Stocker un gène (mutation importante)
gene_id = await genome.store_gene({
    "key": "navigation_optimization",
    "data": {"algorithm": "adaptive_routing", "success_rate": 0.95},
    "category": "performance",
    "priority": 90
})

# Récupérer un gène
gene = genome.get_gene("navigation_optimization")

# Évolution génétique
evolution_result = genome.evolve_generation()
```

### **Mémoire IA (Historique Intelligent)**

```python
from ai_memory_manager import AIMemoryManager

ai_memory = AIMemoryManager()

# Stocker une interaction
await ai_memory.store_interaction(
    user_input="Comment scanner un réseau?",
    ai_response="Utilisez nmap: nmap -sV -p- target.com",
    context={"domain": "networking", "difficulty": "beginner"}
)

# Récupérer un contexte pertinent
context = await ai_memory.retrieve_relevant_context(
    query="scanner réseau", limit=5
)
```

### **Gestionnaire de Contexte**

```python
from context_manager import ContextManager

context_mgr = ContextManager()

# Créer un contexte
context_id = await context_mgr.push_context(
    context_type="web_session",
    data={
        "url": "https://github.com",
        "user": "authenticated",
        "last_action": "browse_repositories"
    }
)

# Récupérer le contexte actif
current_context = context_mgr.get_context()

# Fusionner des contextes
merged = await context_mgr.merge_contexts([context_id1, context_id2])
```

---

## 🎯 API Action Executor

### **Exécution d'Actions Autonomes**

```python
from action_executor import ActionExecutor

executor = ActionExecutor()

# Analyser et exécuter une action naturelle
action_result = await executor.execute_from_text(
    "Scan the network 192.168.1.0/24 for open ports"
)

# Résultat structuré
{
    "action_type": "scan",
    "tool": "nmap",
    "target": "192.168.1.0/24",
    "results": {...},
    "success": True,
    "execution_time": 45.2
}
```

### **Actions Disponibles**

| Type d'Action | Description | Exemples |
|---------------|-------------|----------|
| **RECON** | Reconnaissance passive | `reconnaissance réseau`, `collecte d'infos` |
| **SCAN** | Scan actif | `scan ports`, `énumération services` |
| **EXPLOIT** | Exploitation | `exploit vulnérabilité`, `élévation de privilèges` |
| **ANALYSIS** | Analyse | `analyse trafic`, `détection anomalies` |
| **REPORT** | Rapport | `générer rapport`, `exporter résultats` |
| **BROWSER** | Navigation web | `aller sur site`, `extraire données` |

---

## 🔒 API Sécurité & Permissions

### **Gestionnaire de Permissions**

```python
from system_permissions_manager import SystemPermissionsManager

permissions = SystemPermissionsManager()

# Vérifier une permission
allowed = permissions.check_permission(
    action="run_exploit",
    context={
        "user": "admin",
        "target": "production_server",
        "risk_level": "high"
    }
)

# Accorder une permission
permissions.grant_permission(
    role="pentester",
    permission="network_scan"
)
```

### **Verrouillage Psychic (Sécurité IA)**

```python
from psychic_locks import PsychicLocks

locks = PsychicLocks()

# Évaluer la sécurité d'une action
safety_assessment = locks.evaluate_action_safety({
    "action": "metasploit_exploit",
    "target": "critical_system",
    "impact": "high"
})

if safety_assessment["risk_level"] == "extreme":
    # Appliquer un verrou
    locks.apply_lock(
        action_id="exploit_attempt_123",
        lock_type="complete_block",
        reason="Système critique détecté"
    )
```

---

## 📊 API Métriques & Monitoring

### **Collecteur de Métriques**

```python
from lightweight_metrics import LightweightMetrics

metrics = LightweightMetrics()

# Collecter métriques système
system_stats = metrics.collect_system_metrics()

# Métriques disponibles
{
    "cpu_usage": 45.2,
    "memory_usage": 2.8,  # GB
    "disk_usage": 234.5,  # GB
    "network_io": {
        "bytes_sent": 15432,
        "bytes_recv": 28941
    },
    "active_processes": 127
}
```

### **Métriques IA**

```python
# Métriques par provider
ai_stats = metrics.get_ai_provider_stats("tgpt")

{
    "total_requests": 1450,
    "successful_requests": 1423,
    "success_rate": 98.1,
    "avg_response_time": 1.2,
    "total_tokens": 45632,
    "estimated_cost": 0.0  # Gratuit
}
```

---

## 🔧 API Configuration & Administration

### **Configuration Système**

```python
from sharingan_os import SharinganOS

os_instance = SharinganOS()

# Configuration globale
config = {
    "browser": {
        "default_mode": "hybrid",
        "cdp_port": 9999,
        "timeout": 30000
    },
    "ai": {
        "default_provider": "adaptive",
        "fallback_enabled": True,
        "cost_limit": 1.0  # $ par jour
    },
    "security": {
        "psychic_locks": True,
        "audit_trail": True,
        "auto_quarantine": True
    }
}

os_instance.configure(config)
```

### **Gestion des Backups**

```python
# Sauvegarde complète du système
backup_result = await os_instance.create_backup(
    include_memory=True,
    include_genome=True,
    compression="gzip"
)

# Restauration depuis backup
restore_result = await os_instance.restore_from_backup(
    backup_id="backup_20241215_143022",
    components=["genome", "ai_memory", "context"]
)
```

---

## 🚀 API Avancée & Extensions

### **Création d'Extensions Personnalisées**

```python
from sharingan_app._internal.plugin_system import PluginSystem

class CustomSecurityScanner:
    """Extension personnalisée pour scans de sécurité"""

    def __init__(self):
        self.name = "custom_security_scanner"
        self.version = "1.0.0"

    async def scan_target(self, target: str) -> Dict:
        """Scan personnalisé"""
        # Logique de scan personnalisée
        results = {
            "target": target,
            "vulnerabilities": [],
            "risk_score": 0,
            "recommendations": []
        }

        # Intégration avec l'écosystème Sharingan
        ai_analysis = await self.ai.analyze_security(results)
        kali_scan = await self.kali.execute_tool("web", "nikto_scan", target=target)

        return self._merge_results(results, ai_analysis, kali_scan)

# Enregistrement de l'extension
plugin_system = PluginSystem()
plugin_system.register_plugin(CustomSecurityScanner())
```

### **Intégration Webhook**

```python
from webhook_manager import WebhookManager

webhooks = WebhookManager()

# Enregistrer un webhook
webhook_id = webhooks.register_webhook(
    url="https://my-app.com/webhook/sharingan",
    events=["scan_completed", "vulnerability_found", "ai_response"],
    secret="webhook_secret_key"
)

# Événements déclenchés automatiquement
# POST https://my-app.com/webhook/sharingan
{
    "event": "scan_completed",
    "data": {
        "scan_id": "scan_123",
        "target": "example.com",
        "results": {...},
        "timestamp": "2024-12-15T14:30:22Z"
    },
    "signature": "sha256=..."
}
```

---

## 📋 Gestion d'Erreurs & Debugging

### **Gestion d'Erreurs Unifiée**

```python
try:
    result = await browser_shell.go("https://example.com")
except BrowserError as e:
    if e.code == "TIMEOUT":
        # Retry avec timeout plus long
        result = await browser_shell.go("https://example.com", timeout=60000)
    elif e.code == "NETWORK_ERROR":
        # Fallback vers cache ou mode hors-ligne
        result = await fallback_system.get_cached_page("https://example.com")

except AIProviderError as e:
    if e.provider == "tgpt":
        # Fallback vers autre provider
        result = await ai_manager.chat_completion(messages, provider="ollama")

except KaliToolError as e:
    # Log détaillé pour debugging
    logger.error(f"Kali tool failed: {e.tool_name}, error: {e.message}")
    # Notification administrateur
    await notification_system.alert_admin(f"Tool {e.tool_name} failed: {e.message}")
```

### **Logging & Debugging**

```python
import logging

# Configuration logging détaillé
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/sharingan/debug.log'),
        logging.StreamHandler()
    ]
)

# Logs par module
browser_logger = logging.getLogger('sharingan.browser')
ai_logger = logging.getLogger('sharingan.ai')
kali_logger = logging.getLogger('sharingan.kali')

# Debugging d'une session
with logging_debug_session("browser_navigation") as session:
    session.log("Starting navigation to example.com")
    result = await go("https://example.com")
    session.log(f"Navigation result: {result}")
    if not result[0]:
        session.error(f"Navigation failed: {result[1]}")
        # Dump automatique de l'état système
        session.dump_system_state()
```

---

## 🔄 API Asynchrone & Performance

### **Programmation Asynchrone**

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def parallel_operations():
    """Exécution d'opérations en parallèle"""

    # Tâches parallèles
    tasks = [
        browser_shell.go("https://site1.com"),
        browser_shell.go("https://site2.com"),
        ai_manager.chat_completion([{"role": "user", "content": "Analyze site1"}]),
        kali_master.scan_network("192.168.1.0/24")
    ]

    # Exécution parallèle
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Traitement des résultats
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Task {i} failed: {result}")
        else:
            logger.info(f"Task {i} completed: {result}")

# Exécution dans un pool de threads pour les opérations bloquantes
async def cpu_intensive_task():
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor,
            heavy_computation,
            arg1, arg2
        )
    return result
```

### **Optimisations de Performance**

```python
class PerformanceOptimizer:
    """Optimisations automatiques de performance"""

    def __init__(self):
        self.cache = SmartCache()
        self.connection_pool = ConnectionPool(max_size=10)
        self.batch_processor = BatchProcessor()

    async def optimized_request(self, request: Dict) -> Any:
        """Traitement optimisé d'une requête"""

        # 1. Vérification cache
        cache_key = self._generate_cache_key(request)
        if cached := self.cache.get(cache_key):
            return cached

        # 2. Batch processing si applicable
        if self._can_batch(request):
            batched_result = await self.batch_processor.process_request(request)
            self.cache.set(cache_key, batched_result)
            return batched_result

        # 3. Pool de connexions
        async with self.connection_pool.get_connection() as conn:
            result = await conn.execute(request)
            self.cache.set(cache_key, result)
            return result
```

---

## 🔐 Authentification & Autorisation

### **Authentification Multi-Facteurs**

```python
from auth_system import AuthSystem

auth = AuthSystem()

# Authentification utilisateur
session = await auth.authenticate_user(
    username="admin",
    password="password123",
    mfa_code="123456",
    biometrics=None
)

# Vérification de session
is_valid = await auth.validate_session(session.token)

# Autorisation basée sur les rôles
permissions = await auth.get_user_permissions(session.user_id)

if "run_kali_tools" in permissions:
    # Exécution autorisée
    result = await kali_master.execute_tool("exploit", "metasploit_exploit", **params)
else:
    raise PermissionDeniedError("Insufficient permissions for Kali tools")
```

### **API Keys & Tokens**

```python
# Gestion des API keys
api_keys = await auth.manage_api_keys(
    action="create",
    name="external_integration",
    permissions=["read_browser", "ai_chat"],
    expires_in_days=30
)

# Utilisation des tokens API
response = await authenticated_api_call(
    endpoint="/browser/go",
    token=api_keys["token"],
    params={"url": "https://example.com"}
)
```

---

Cette API complète fait de Sharingan OS une plateforme extrêmement puissante et flexible pour l'automatisation de tâches complexes en cybersécurité, tout en maintenant une simplicité d'utilisation et une sécurité maximale.