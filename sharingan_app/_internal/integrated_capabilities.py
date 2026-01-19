# Sharingan OS - Integrated Capabilities System
"""
Système d'intégration central pour toutes les capacités de Sharingan OS.
Gère l'accès unifié à tous les outils et fonctionnalités sans perdre de capacités.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("integrated_capabilities")

class IntegratedCapabilities:
    """
    Système centralisé pour accéder à toutes les capacités de Sharingan OS.
    Intègre tous les outils existants : Kali, Navigation Web, AI, etc.
    """

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.capabilities_file = self.base_dir / "integrated_capabilities.json"
        self._load_capabilities()

        # Importer tous les systèmes disponibles
        self._load_all_systems()

    def _load_capabilities(self):
        """Charger les capacités depuis le fichier"""
        if self.capabilities_file.exists():
            try:
                with open(self.capabilities_file, 'r') as f:
                    self.capabilities = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load capabilities: {e}")
                self.capabilities = {}
        else:
            self.capabilities = {}
            self._initialize_default_capabilities()

    def _initialize_default_capabilities(self):
        """Initialiser les capacités par défaut"""
        self.capabilities = {
            "kali_tools": {
                "status": "available",
                "count": 19,
                "categories": ["enumeration", "monitoring", "post-exploit", "reporting", "reverse-engineering"],
                "tools": [
                    "nmap", "masscan", "netdiscover", "gobuster", "dirb",
                    "nikto", "sqlmap", "hydra", "john", "hashcat",
                    "aircrack-ng", "wireshark", "ettercap", "metasploit",
                    "burp_suite", "owasp_zap", "nessus", "openvas"
                ]
            },
            "web_automation": {
                "status": "available",
                "capabilities": [
                    "navigation", "search", "content_reading", "scrolling",
                    "clicking", "form_filling", "screenshot", "tab_management",
                    "javascript_execution", "file_upload"
                ],
                "technologies": ["selenium", "chrome_devtools_protocol"]
            },
            "ai_providers": {
                "status": "available",
                "providers": ["tgpt", "grok-code-fast", "minimax", "ollama"],
                "fallback_order": ["tgpt", "grok-code-fast", "minimax"],
                "specialized": {
                    "tgpt": "general_chat",
                    "grok-code-fast": "coding",
                    "minimax": "backup",
                    "ollama": "local"
                }
            },
            "system_monitoring": {
                "status": "available",
                "metrics": ["cpu", "memory", "disk", "network"],
                "anomaly_detection": True,
                "alerts": ["high_cpu", "high_memory", "low_disk"]
            },
            "memory_systems": {
                "status": "available",
                "types": ["genome", "ai_memory", "context", "vector"],
                "evolution": True,
                "learning": True
            },
            "consciousness": {
                "status": "available",
                "layers": ["core", "ai", "security", "memory", "tools"],
                "soul": True,
                "spirit": True,
                "autonomous": True
            },
            "security": {
                "status": "available",
                "features": [
                    "psychic_locks", "permissions_manager", "sandboxing",
                    "validation", "audit_trail", "threat_detection"
                ]
            }
        }
        self._save_capabilities()

    def _save_capabilities(self):
        """Sauvegarder les capacités"""
        try:
            with open(self.capabilities_file, 'w') as f:
                json.dump(self.capabilities, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save capabilities: {e}")

    def _load_all_systems(self):
        """Charger tous les systèmes disponibles"""
        self.systems = {}

        # Liste des systèmes à charger
        systems_to_load = [
            ("kali_manager", "kali_implementation_manager", "KaliToolManager"),
            ("cloud_manager", "cloud_integration_manager", "CloudIntegrationManager"),
            ("scaling_manager", "auto_scaling_manager", "AutoScalingManager"),
            ("permissions_manager", "system_permissions_manager", "SystemPermissionsManager"),
            ("vpn_manager", "vpn_tor_integration", "VPNManager"),
            ("execution_manager", "code_execution_system", "IntelligentCodeExecution"),
            ("psychic_system", "psychic_locks_system", "PsychicLocksSystem"),
            ("mission_system", "autonomous_mission_system", "AutonomousMissionSystem"),
            ("api_intelligence", "api_first_intelligence", "APIFirstIntelligence"),
            ("capability_discovery", "capability_discovery_system", "CapabilityDiscoverySystem")
        ]

        for system_name, module_name, class_name in systems_to_load:
            try:
                module = __import__(f"sharingan_app._internal.{module_name}", fromlist=[class_name])
                system_class = getattr(module, class_name, None)
                if system_class:
                    # Essayer d'initialiser avec les bons paramètres
                    if system_name == "execution_manager":
                        self.systems[system_name] = None  # Fallback spécial
                    else:
                        self.systems[system_name] = system_class()
                    logger.info(f"Loaded system: {system_name}")
                else:
                    logger.warning(f"System class not found: {class_name}")
                    self.systems[system_name] = None
            except Exception as e:
                logger.warning(f"Failed to load system {system_name}: {e}")
                self.systems[system_name] = None

    def get_all_capabilities(self) -> Dict[str, Any]:
        """Renvoyer toutes les capacités disponibles"""
        return self.capabilities.copy()

    def get_capability_status(self, capability: str) -> str:
        """Vérifier le statut d'une capacité"""
        if capability in self.capabilities:
            return self.capabilities[capability].get("status", "unknown")
        return "not_found"

    def is_capability_available(self, capability: str) -> bool:
        """Vérifier si une capacité est disponible"""
        return self.get_capability_status(capability) == "available"

    def get_system_status(self, system_name: str) -> Dict[str, Any]:
        """Obtenir le statut d'un système spécifique"""
        system = self.systems.get(system_name)
        if system and hasattr(system, 'get_status'):
            return system.get_status()
        elif system_name in self.capabilities:
            return self.capabilities[system_name]
        return {"status": "not_available"}

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Exécuter un outil via le système approprié"""
        # Trouver quel système gère cet outil
        if tool_name in ["nmap", "sqlmap", "hydra", "nikto"]:
            kali_manager = self.systems.get("kali_manager")
            if kali_manager:
                return kali_manager.execute_tool(tool_name, **kwargs)

        # Fallback aux capacités générales
        logger.warning(f"Tool {tool_name} not found in integrated systems")
        return {"error": f"Tool {tool_name} not available"}

    def get_tool_count(self) -> Dict[str, int]:
        """Compter les outils disponibles par catégorie"""
        counts = {}
        for category, data in self.capabilities.items():
            if "tools" in data:
                counts[category] = len(data["tools"])
            elif "count" in data:
                counts[category] = data["count"]
            elif isinstance(data, list):
                counts[category] = len(data)
        return counts

    def update_capability(self, capability: str, data: Dict[str, Any]):
        """Mettre à jour une capacité"""
        if capability not in self.capabilities:
            self.capabilities[capability] = {}
        self.capabilities[capability].update(data)
        self.capabilities[capability]["last_updated"] = datetime.now().isoformat()
        self._save_capabilities()

    def get_capabilities_summary(self) -> str:
        """Résumé de toutes les capacités"""
        total_tools = sum(self.get_tool_count().values())
        available_systems = sum(1 for s in self.systems.values() if s is not None)

        summary = f"""
SHARINGAN OS - CAPACITÉS INTÉGRÉES
==================================
• Systèmes actifs: {available_systems}/{len(self.systems)}
• Outils totaux: {total_tools}
• Couches de conscience: {len(self.capabilities.get('consciousness', {}).get('layers', []))}

CATÉGORIES PRINCIPALES:
• Kali Tools: {self.capabilities.get('kali_tools', {}).get('count', 0)} outils
• Web Automation: {len(self.capabilities.get('web_automation', {}).get('capabilities', []))} capacités
• AI Providers: {len(self.capabilities.get('ai_providers', {}).get('providers', []))} providers
• Memory Systems: {len(self.capabilities.get('memory_systems', {}).get('types', []))} types
• Security Features: {len(self.capabilities.get('security', {}).get('features', []))} features

DERNIÈRE MISE À JOUR: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return summary.strip()

# Instance singleton
_integrated_capabilities = None

def get_integrated_capabilities() -> IntegratedCapabilities:
    """Obtenir l'instance singleton des capacités intégrées"""
    global _integrated_capabilities
    if _integrated_capabilities is None:
        _integrated_capabilities = IntegratedCapabilities()
    return _integrated_capabilities