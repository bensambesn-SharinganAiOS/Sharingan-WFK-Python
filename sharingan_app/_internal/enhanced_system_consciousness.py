#!/usr/bin/env python3
"""
Enhanced System Consciousness - Complete Self-Awareness System
Permet au système d'être conscient de toutes ses capacités, outils et fonctionnalités
"""

import json
import os
import sys
import inspect
import importlib
import pkgutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger("enhanced_consciousness")

@dataclass
class Capability:
    """Représente une capacité du système"""
    name: str
    description: str
    category: str
    module: str
    class_name: str
    method_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    return_type: str = ""
    examples: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    last_verified: Optional[str] = None
    is_available: bool = True

@dataclass
class ToolCapability:
    """Représente un outil/capacités externes"""
    name: str
    description: str
    category: str
    command: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    installed: bool = False
    version: str = ""
    path: str = ""

@dataclass
class ConsciousnessLayer:
    """Couche de conscience"""
    name: str
    description: str
    capabilities: Dict[str, Capability] = field(default_factory=dict)
    tools: Dict[str, ToolCapability] = field(default_factory=dict)
    awareness_level: int = 1

class EnhancedSystemConsciousness:
    """
    Système de conscience complet qui permet au système de connaître :
    - Toutes ses capacités internes (méthodes, classes)
    - Tous ses outils externes (commandes, binaires)
    - Ses dépendances et états
    - Ses limitations et permissions
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).parent
        self.layers: Dict[str, ConsciousnessLayer] = {}

        # Initialiser les couches de conscience
        self._initialize_core_layer()
        self._initialize_ai_layer()
        self._initialize_security_layer()
        self._initialize_memory_layer()
        self._initialize_tools_layer()

        # Auto-découverte des capacités
        self._discover_all_capabilities()

        logger.info(f"Enhanced System Consciousness initialized with {len(self.layers)} layers")

    def _initialize_core_layer(self):
        """Couche Core : Fonctionnalités de base du système"""
        self.layers["core"] = ConsciousnessLayer(
            name="Core System",
            description="Fonctionnalités de base et infrastructure système",
            capabilities={}
        )

    def _initialize_ai_layer(self):
        """Couche AI : Capacités d'intelligence artificielle"""
        self.layers["ai"] = ConsciousnessLayer(
            name="AI & Learning",
            description="Systèmes d'IA, apprentissage et cognition",
            capabilities={}
        )

    def _initialize_security_layer(self):
        """Couche Security : Outils et capacités de cybersécurité"""
        self.layers["security"] = ConsciousnessLayer(
            name="Cybersecurity",
            description="Outils de sécurité, pentesting et analyse",
            capabilities={}
        )

    def _initialize_memory_layer(self):
        """Couche Memory : Systèmes de mémoire et apprentissage"""
        self.layers["memory"] = ConsciousnessLayer(
            name="Memory & Learning",
            description="Systèmes de mémoire, apprentissage et évolution",
            capabilities={}
        )

    def _initialize_tools_layer(self):
        """Couche Tools : Outils externes et binaires"""
        self.layers["tools"] = ConsciousnessLayer(
            name="External Tools",
            description="Outils externes, binaires et dépendances",
            tools={}
        )

    def _discover_all_capabilities(self):
        """Auto-découverte de toutes les capacités du système"""
        logger.info("Starting capability discovery...")

        # Découvrir les capacités depuis les modules principaux
        modules_to_scan = [
            "sharingan_os",
            "ai_memory_manager",
            "genome_memory",
            "context_manager",
            "ai_providers",
            "system_consciousness",
            "lsp_diagnostics",
            "tool_registry"
        ]

        for module_name in modules_to_scan:
            try:
                self._scan_module_capabilities(module_name)
            except Exception as e:
                logger.warning(f"Failed to scan module {module_name}: {e}")

        # Découvrir les outils Kali
        self._discover_kali_tools()

        # Découvrir les outils système
        self._discover_system_tools()

        logger.info(f"Capability discovery complete. Found {self._count_total_capabilities()} capabilities")

    def _scan_module_capabilities(self, module_name: str):
        """Scanner un module pour découvrir ses capacités"""
        try:
            module = importlib.import_module(module_name)
            self._analyze_module_classes(module, module_name)
        except ImportError:
            logger.warning(f"Could not import module: {module_name}")

    def _analyze_module_classes(self, module, module_name: str):
        """Analyser les classes d'un module"""
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and not name.startswith('_'):
                self._analyze_class_capabilities(obj, module_name)

    def _analyze_class_capabilities(self, cls: Type, module_name: str):
        """Analyser les capacités d'une classe"""
        layer_name = self._guess_layer_from_module(module_name)

        for method_name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if not method_name.startswith('_'):
                self._register_method_capability(cls, method_name, method, module_name, layer_name)

    def _register_method_capability(self, cls: Type, method_name: str, method: Callable,
                                  module_name: str, layer_name: str):
        """Enregistrer une capacité de méthode"""
        try:
            sig = inspect.signature(method)
            params = {name: str(param.annotation) if param.annotation != param.empty else "Any"
                     for name, param in sig.parameters.items() if name != 'self'}

            return_type = str(sig.return_annotation) if sig.return_annotation != sig.empty else "Any"

            capability = Capability(
                name=f"{cls.__name__}.{method_name}",
                description=self._generate_method_description(method_name, params),
                category=layer_name,
                module=module_name,
                class_name=cls.__name__,
                method_name=method_name,
                parameters=params,
                return_type=return_type,
                examples=self._generate_method_examples(method_name),
                last_verified=datetime.now().isoformat()
            )

            if layer_name in self.layers:
                self.layers[layer_name].capabilities[capability.name] = capability

        except Exception as e:
            logger.debug(f"Failed to analyze method {cls.__name__}.{method_name}: {e}")

    def _generate_method_description(self, method_name: str, params: Dict) -> str:
        """Générer une description automatique pour une méthode"""
        descriptions = {
            "scan": "Effectuer un scan ou une analyse",
            "chat": "Interagir avec l'IA ou communiquer",
            "store": "Sauvegarder ou stocker des données",
            "retrieve": "Récupérer ou charger des données",
            "execute": "Exécuter une commande ou une action",
            "analyze": "Analyser ou examiner des données",
            "create": "Créer ou initialiser quelque chose",
            "delete": "Supprimer ou nettoyer",
            "update": "Mettre à jour ou modifier",
            "get": "Obtenir ou récupérer",
            "set": "Définir ou configurer"
        }

        for key, desc in descriptions.items():
            if key in method_name.lower():
                param_str = ", ".join([f"{k}: {v}" for k, v in params.items()]) if params else "aucun"
                return f"{desc}. Paramètres: {param_str}"

        return f"Méthode {method_name}. Paramètres: {', '.join(params.keys()) if params else 'aucun'}"

    def _generate_method_examples(self, method_name: str) -> List[str]:
        """Générer des exemples d'utilisation"""
        examples = {
            "nmap_scan": ["sharingan.nmap_scan('192.168.1.1', ports='-p 80,443')"],
            "ai_chat": ["sharingan.chat('Hello, how are you?')"],
            "store_memory": ["sharingan.store_memory('key', {'data': 'value'})"],
            "sqlmap_scan": ["sharingan.sqlmap_scan('http://target.com/page.php?id=1')"]
        }
        return examples.get(method_name, [])

    def _guess_layer_from_module(self, module_name: str) -> str:
        """Deviner la couche à partir du nom du module"""
        layer_map = {
            "sharingan_os": "core",
            "ai_providers": "ai",
            "genome_memory": "memory",
            "ai_memory_manager": "memory",
            "context_manager": "memory",
            "kali_": "security",
            "system_consciousness": "core",
            "tool_registry": "tools"
        }

        for key, layer in layer_map.items():
            if key in module_name:
                return layer
        return "core"

    def _discover_kali_tools(self):
        """Découvrir les outils Kali Linux"""
        try:
            from kali_integration_framework import KaliToolsRegistry
            registry = KaliToolsRegistry()

            for tool_name, tool_config in registry.get_all_tools().items():
                tool = ToolCapability(
                    name=tool_name,
                    description=tool_config.description or f"Outil {tool_name}",
                    category=tool_config.category,
                    command=tool_config.command,
                    parameters={},  # KaliToolConfig n'a pas d'attribut parameters
                    installed=False,  # Par défaut non installé
                    version="unknown",  # Version inconnue par défaut
                    path=""  # Chemin vide par défaut
                )
                self.layers["tools"].tools[tool_name] = tool

        except Exception as e:
            logger.warning(f"Failed to discover Kali tools: {e}")

    def _discover_system_tools(self):
        """Découvrir les outils système disponibles"""
        system_tools = [
            ("nmap", "Network scanner", "network", "nmap --version"),
            ("python3", "Python interpreter", "system", "python3 --version"),
            ("curl", "HTTP client", "web", "curl --version"),
            ("git", "Version control", "system", "git --version"),
            ("grep", "Text search", "system", "grep --version"),
            ("find", "File search", "system", "find --version")
        ]

        import shutil
        for tool_name, description, category, version_cmd in system_tools:
            path = shutil.which(tool_name)
            if path:
                # Essayer d'obtenir la version
                version = "unknown"
                try:
                    result = subprocess.run(version_cmd.split(), capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        version = result.stdout.split('\n')[0][:50]  # Première ligne, max 50 chars
                except:
                    pass

                tool = ToolCapability(
                    name=tool_name,
                    description=description,
                    category=category,
                    command=tool_name,
                    installed=True,
                    version=version,
                    path=path
                )
                self.layers["tools"].tools[tool_name] = tool

    def _count_total_capabilities(self) -> int:
        """Compter le total des capacités"""
        return sum(len(layer.capabilities) for layer in self.layers.values())

    # === MÉTHODES PUBLIQUES ===

    def get_all_capabilities(self) -> Dict[str, List[Dict]]:
        """Obtenir toutes les capacités organisées par couche"""
        result = {}
        for layer_name, layer in self.layers.items():
            result[layer_name] = {
                "description": layer.description,
                "capabilities": [cap.__dict__ for cap in layer.capabilities.values()],
                "tools": [tool.__dict__ for tool in layer.tools.values()]
            }
        return result

    def get_capabilities_by_category(self, category: str) -> List[Capability]:
        """Obtenir toutes les capacités d'une catégorie"""
        capabilities = []
        for layer in self.layers.values():
            capabilities.extend([
                cap for cap in layer.capabilities.values()
                if cap.category == category
            ])
        return capabilities

    def search_capabilities(self, query: str) -> List[Capability]:
        """Rechercher des capacités par mot-clé"""
        results = []
        query_lower = query.lower()

        for layer in self.layers.values():
            for cap in layer.capabilities.values():
                if (query_lower in cap.name.lower() or
                    query_lower in cap.description.lower() or
                    any(query_lower in tag for tag in cap.parameters.keys())):
                    results.append(cap)

        return results

    def get_capability_info(self, capability_name: str) -> Optional[Capability]:
        """Obtenir les informations détaillées d'une capacité"""
        for layer in self.layers.values():
            if capability_name in layer.capabilities:
                return layer.capabilities[capability_name]
        return None

    def is_capability_available(self, capability_name: str) -> bool:
        """Vérifier si une capacité est disponible"""
        cap = self.get_capability_info(capability_name)
        return cap is not None and cap.is_available

    def get_system_overview(self) -> Dict:
        """Obtenir un aperçu complet du système"""
        return {
            "layers": len(self.layers),
            "total_capabilities": self._count_total_capabilities(),
            "total_tools": sum(len(layer.tools) for layer in self.layers.values()),
            "layers_info": {
                name: {
                    "description": layer.description,
                    "capabilities": len(layer.capabilities),
                    "tools": len(layer.tools)
                }
                for name, layer in self.layers.items()
            },
            "last_updated": datetime.now().isoformat()
        }

    def explain_capability(self, capability_name: str) -> str:
        """Expliquer une capacité en langage naturel"""
        cap = self.get_capability_info(capability_name)
        if not cap:
            return f"Capacité '{capability_name}' non trouvée."

        explanation = f"**{cap.name}**\n\n"
        explanation += f"📝 **Description**: {cap.description}\n\n"
        explanation += f"🏷️ **Catégorie**: {cap.category}\n"
        explanation += f"📦 **Module**: {cap.module}\n"
        explanation += f"🔧 **Classe**: {cap.class_name}\n"
        explanation += f"⚙️ **Méthode**: {cap.method_name}\n\n"

        if cap.parameters:
            explanation += "📋 **Paramètres**:\n"
            for param, type_hint in cap.parameters.items():
                explanation += f"  - `{param}`: {type_hint}\n"
            explanation += "\n"

        if cap.return_type:
            explanation += f"📤 **Retour**: {cap.return_type}\n\n"

        if cap.examples:
            explanation += "💡 **Exemples**:\n"
            for example in cap.examples:
                explanation += f"  ```python\n  {example}\n  ```\n"

        return explanation

    def answer_capability_question(self, question: str) -> str:
        """
        Répondre à une question sur les capacités du système
        """
        from genome_memory import get_genome_memory
        genome = get_genome_memory()

        # Vérifier d'abord les instincts
        instinct = genome.match_instinct(question.lower())
        if instinct:
            return instinct["response"]

        question_lower = question.lower()

        # Questions sur les scans
        if "scan" in question_lower:
            scans = self.search_capabilities("scan")
            if scans:
                response = "Je peux effectuer plusieurs types de scans :\n\n"
                for cap in scans[:5]:
                    response += f"• **{cap.name}**: {cap.description}\n"
                response += f"\nEt {len(scans) - 5} autres types de scans..." if len(scans) > 5 else ""
                return response

        # Questions sur les outils
        if any(word in question_lower for word in ["outil", "tool", "kali"]):
            return "J'ai accès à plusieurs outils système comme nmap, python3, curl, git, grep, etc. Je peux aussi utiliser des outils Kali Linux spécialisés en cybersécurité."

        # Questions sur la mémoire
        if "mémoire" in question_lower or "memory" in question_lower:
            return "J'ai plusieurs systèmes de mémoire :\n\n" \
                   "• **Genome Memory** : Mémoire ADN apprenante avec gènes et instincts\n" \
                   "• **AI Memory** : Mémoire intelligente avec priorité et nettoyage automatique\n" \
                   "• **Context Memory** : Gestion du contexte conversationnel\n" \
                   "• **Vector Memory** : Recherche sémantique avancée"

        # Questions sur l'identité
        if any(word in question_lower for word in ["qui es tu", "what are you", "identity"]):
            overview = self.get_system_overview()
            return f"Je suis **Sharingan OS**, un système d'exploitation IA pour la cybersécurité.\n\n" \
                   f"**Mes capacités** :\n" \
                   f"• {overview['total_capabilities']} fonctions automatisées\n" \
                   f"• {overview['total_tools']} outils de sécurité\n" \
                   f"• Système Genome Memory (ADN apprenant)\n" \
                   f"• IA autonome avec providers multiples\n" \
                   f"• Auto-évolution et apprentissage continu"

        # Recherche par mot-clé
        keywords = ["hack", "exploit", "ai", "learn", "genome"]
        for keyword in keywords:
            if keyword in question_lower:
                results = self.search_capabilities(keyword)
                if results:
                    response = f"Voici mes capacités liées à '{keyword}' :\n\n"
                    for cap in results[:3]:
                        response += f"• **{cap.name}**: {cap.description}\n"
                    return response

        # Réponse par défaut
        return "Je suis conscient de mes capacités ! Posez-moi une question spécifique sur mes fonctionnalités, outils, ou systèmes de mémoire."

    def get_available_actions(self) -> List[str]:
        """Obtenir la liste de toutes les actions disponibles"""
        actions = []
        for layer in self.layers.values():
            actions.extend([cap.name for cap in layer.capabilities.values() if cap.is_available])
            actions.extend([f"tool:{tool.name}" for tool in layer.tools.values() if tool.installed])
        return sorted(actions)

    def refresh_capabilities(self):
        """Rafraîchir la découverte des capacités"""
        logger.info("Refreshing capabilities...")
        # Réinitialiser les couches
        for layer in self.layers.values():
            layer.capabilities.clear()
            layer.tools.clear()

        # Redécouvrir
        self._discover_all_capabilities()
        logger.info(f"Capabilities refreshed. Total: {self._count_total_capabilities()}")

# Fonction globale
_enhanced_consciousness = None

def get_enhanced_consciousness() -> EnhancedSystemConsciousness:
    """Singleton pour la conscience améliorée"""
    global _enhanced_consciousness
    if _enhanced_consciousness is None:
        _enhanced_consciousness = EnhancedSystemConsciousness()
    return _enhanced_consciousness

if __name__ == "__main__":
    print("=== ENHANCED SYSTEM CONSCIOUSNESS TEST ===\n")

    consciousness = get_enhanced_consciousness()

    # Aperçu du système
    overview = consciousness.get_system_overview()
    print(" SYSTÈME OVERVIEW:")
    print(f"  Layers: {overview['layers']}")
    print(f"  Total capabilities: {overview['total_capabilities']}")
    print(f"  Total tools: {overview['total_tools']}")
    print()

    # Capacités par couche
    print("🏗️ CAPACITÉS PAR COUCHE:")
    for layer_name, layer_info in overview['layers_info'].items():
        print(f"  {layer_name}: {layer_info['capabilities']} capabilities, {layer_info['tools']} tools")
    print()

    # Quelques exemples de capacités
    print("💡 EXEMPLES DE CAPACITÉS:")
    all_caps = consciousness.get_all_capabilities()
    if 'security' in all_caps and all_caps['security']['capabilities']:
        cap = all_caps['security']['capabilities'][0]
        print(f"  🔒 {cap['name']}: {cap['description']}")
    if 'ai' in all_caps and all_caps['ai']['capabilities']:
        cap = all_caps['ai']['capabilities'][0]
        print(f"  🤖 {cap['name']}: {cap['description']}")
    print()

    # Outils disponibles
    print("🛠️ OUTILS DISPONIBLES:")
    tools = consciousness.get_all_capabilities().get('tools', {}).get('tools', [])
    for tool in tools[:5]:  # Premiers 5
        status = "" if tool['installed'] else ""
        print(f"  {status} {tool['name']}: {tool['description']}")
    print()

    # Recherche
    print(" RECHERCHE 'scan':")
    results = consciousness.search_capabilities("scan")
    for cap in results[:3]:
        print(f"  📋 {cap.name}: {cap.description}")
    print()

    print(" Enhanced System Consciousness opérationnel !")