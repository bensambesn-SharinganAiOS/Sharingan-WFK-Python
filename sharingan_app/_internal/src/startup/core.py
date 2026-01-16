#!/usr/bin/env python3
"""
Sharingan OS - Startup Core System
Système de démarrage hybride complet (Python + Shell + IA + NLP + RAG + Actions)
Auteur: Ben Sambe
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

# Ajouter le répertoire au path
startup_dir = Path(__file__).parent.parent
sys.path.insert(0, str(startup_dir))

# Import des modules existants
FakeDetector = None
check_obligations = None
OpenCodeProvider = None
SharinganOS = None
SystemConsciousness = None
get_context_manager = None
get_memory_manager = None
get_genome_memory = None
get_all_tool_schemas = None
get_provider_manager = None

try:
    from fake_detector import FakeDetector, validate_readiness
except ImportError:
    pass

try:
    from check_obligations import check_obligations
except ImportError:
    pass

try:
    from providers.opencode_provider import OpenCodeProvider
except ImportError:
    pass

try:
    from sharingan_os import SharinganOS
except ImportError:
    pass

try:
    from system_consciousness import SystemConsciousness
except ImportError:
    pass

try:
    from context_manager import get_context_manager
except ImportError:
    pass

try:
    from ai_memory_manager import get_memory_manager
except ImportError:
    pass

try:
    from genome_memory import get_genome_memory
except ImportError:
    pass

try:
    from tool_schemas import get_all_tool_schemas
except ImportError:
    pass

try:
    from ai_providers import get_provider_manager
except ImportError:
    pass

logger = logging.getLogger("sharingan.startup")


@dataclass
class StartupStatus:
    """Statut du démarrage"""
    core_ready: bool = False
    ai_ready: bool = False
    nlp_ready: bool = False
    rag_ready: bool = False
    nlp_rag_ready: bool = False
    actions_ready: bool = False
    consciousness_ready: bool = False
    conscious_ready: bool = False
    tools_ready: bool = False
    kali_ready: bool = False
    fake_detector_ready: bool = False
    obligations_ready: bool = False
    overall_ready: bool = False
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class StartupCore:
    """
    Système de démarrage hybride complet.
    Combine Python, Shell, IA, NLP, RAG, Actions.
    """
    
    def __init__(self):
        self.status = StartupStatus()
        self.startup_dir = Path(__file__).parent.parent
        self.config_dir = self.startup_dir / "config"
        self.logs_dir = self.startup_dir / "logs"
        self.data_dir = self.startup_dir / "data"
        
        # Créer les répertoires
        self._create_directories()
        
        # Initialiser les composants
        self._initialize_components()
        
        logger.info("Startup Core initialized")
    
    def _create_directories(self):
        """Crée les répertoires nécessaires"""
        dirs = [
            self.config_dir,
            self.logs_dir,
            self.data_dir,
            self.startup_dir / "src",
            self.startup_dir / "src/ai",
            self.startup_dir / "src/ai/providers",
            self.startup_dir / "src/ai/nlp",
            self.startup_dir / "src/ai/rag",
            self.startup_dir / "src/ai/actions",
            self.startup_dir / "src/tools",
            self.startup_dir / "src/tools/kali",
            self.startup_dir / "scripts"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _initialize_components(self):
        """Initialise tous les composants hybrides"""
        try:
            # 1. Fake Detector
            self.fake_detector = FakeDetector()
            self.status.fake_detector_ready = True
            logger.info(" Fake Detector ready")
        except Exception as e:
            self.status.issues.append(f"FakeDetector error: {e}")
        
        try:
            # 2. Check Obligations
            obligations_result = check_obligations()
            self.status.obligations_ready = obligations_result.get("summary", {}).get("compliance_rate", "N/A") != "N/A"
            logger.info(" Check Obligations ready")
        except Exception as e:
            self.status.issues.append(f"Check Obligations error: {e}")
        
        try:
            # 3. OpenCode Provider
            self.opencode = OpenCodeProvider()
            self.status.actions_ready = True
            logger.info(" OpenCode Provider ready")
        except Exception as e:
            self.status.issues.append(f"OpenCode Provider error: {e}")
        
        try:
            # 4. Core Systems
            self.sharingan_os = SharinganOS()
            self.consciousness = SystemConsciousness()
            self.context = get_context_manager()
            self.memory = get_memory_manager()
            self.genome = get_genome_memory()
            self.tools = get_all_tool_schemas()
            
            self.status.core_ready = True
            self.status.consciousness_ready = True
            self.status.tools_ready = True
            logger.info(" Core systems ready")
        except Exception as e:
            self.status.issues.append(f"Core systems error: {e}")
        
        try:
            # 5. AI Manager (Hybrid)
            from ai_providers import get_provider_manager
            self.ai_manager = get_provider_manager()
            
            # Vérifier les 4 providers
            required_providers = ["tgpt", "minimax", "grok-code-fast-1", "opencode"]
            available_providers = list(self.ai_manager.providers.keys())
            
            self.status.ai_ready = all(p in available_providers for p in required_providers)
            
            if self.status.ai_ready:
                logger.info(f" AI Manager ready - Providers: {available_providers}")
            else:
                missing = [p for p in required_providers if p not in available_providers]
                self.status.issues.append(f"Missing AI providers: {missing}")
        except Exception as e:
            self.status.issues.append(f"AI Manager error: {e}")
        
        try:
            # 6. NLP/RAG System
            from nlp_rag_system import NLPRAGSystem
            self.nlp_rag = NLPRAGSystem()
            self.status.nlp_ready = True
            self.status.rag_ready = True
            logger.info(" NLP/RAG System ready")
        except Exception as e:
            self.status.issues.append(f"NLP/RAG System error: {e}")
        
        try:
            # 7. Action Orchestrator
            from action_orchestrator import ActionOrchestrator
            self.action_orchestrator = ActionOrchestrator()
            self.status.actions_ready = True
            logger.info(" Action Orchestrator ready")
        except Exception as e:
            self.status.issues.append(f"Action Orchestrator error: {e}")
        
        try:
            # 8. Kali Tools Integration
            from kali_integration import KaliToolsManager
            self.kali_tools = KaliToolsManager()
            self.status.kali_ready = True
            logger.info(" Kali Tools ready")
        except Exception as e:
            self.status.issues.append(f"Kali Tools error: {e}")
        
        # Déterminer le statut global
        self.status.overall_ready = (
            self.status.core_ready and
            self.status.ai_ready and
            self.status.nlp_ready and
            self.status.rag_ready and
            self.status.actions_ready and
            self.status.consciousness_ready and
            self.status.tools_ready and
            self.status.kali_ready and
            self.status.fake_detector_ready and
            self.status.obligations_ready
        )
        
        logger.info(f"Startup Core initialized - Ready: {self.status.overall_ready}")
    
    def get_status(self) -> Dict:
        """Obtenir le statut complet du démarrage"""
        return {
            "overall_ready": self.status.overall_ready,
            "components": {
                "core": self.status.core_ready,
                "ai": self.status.ai_ready,
                "nlp": self.status.nlp_rag_ready,
                "rag": self.status.rag_ready,
                "actions": self.status.actions_ready,
                "consciousness": self.status.conscious_ready,
                "tools": self.status.tools_ready,
                "kali": self.status.kali_ready,
                "fake_detector": self.status.fake_detector_ready,
                "obligations": self.status.obligations_ready
            },
            "issues": self.status.issues,
            "recommendations": self.status.recommendations,
            "timestamp": str(__import__("datetime").datetime.now())
        }
    
    def validate_startup(self) -> Dict:
        """Valide que tout est prêt pour le démarrage"""
        validation = {
            "timestamp": str(__import__("datetime").datetime.now()),
            "ready": self.status.overall_ready,
            "components": {},
            "issues": [],
            "recommendations": []
        }
        
        # Valider chaque composant
        for component, ready in self.status.__dict__.items():
            if component != "overall_ready":
                validation["components"][component] = ready
                if not ready:
                    validation["issues"].append(f"{component} not ready")
        
        # Ajouter les problèmes
        validation["issues"].extend(self.status.issues)
        
        # Recommandations
        if not self.status.ai_ready:
            validation["recommendations"].append("Install missing AI providers")
        if not self.status.kali_ready:
            validation["recommendations"].append("Install Kali tools or check PATH")
        if not self.status.nlp_rag_ready:
            validation["recommendations"].append("Install vector database for NLP/RAG")
        
        return validation
    
    def start_sharingan(self) -> Dict:
        """Démarrer Sharingan OS avec tous les composants hybrides"""
        logger.info(" Starting Sharingan OS with hybrid architecture...")
        
        if not self.status.overall_ready:
            logger.error("❌ System not ready for startup")
            return self.get_status()
        
        try:
            # 1. Démarrer la conscience partagée
            logger.info(" Starting shared consciousness...")
            self.consciousness.start_shared_mode()
            
            # 2. Démarrer le système NLP/RAG
            logger.info(" Starting NLP/RAG system...")
            self.nlp_rag.start()
            
            # 3. Démarrer l'orchestrateur d'actions
            logger.info("🤖 Starting action orchestrator...")
            self.action_orchestrator.start()
            
            # 4. Démarrer les outils Kali
            logger.info("🔧 Starting Kali tools integration...")
            self.kali_tools.start()
            
            # 5. Démarrer le système IA hybride
            logger.info("🤖 Starting hybrid AI manager...")
            self.ai_manager.start_hybrid_mode()
            
            logger.info("🎊 Sharingan OS started successfully!")
            return {
                "success": True,
                "message": "Sharingan OS started with hybrid architecture",
                "status": self.get_status()
            }
            
        except Exception as e:
            logger.error(f"❌ Startup failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": self.get_status()
            }
    
    def stop_sharingan(self) -> Dict:
        """Arrêter Sharingan OS proprement"""
        try:
            logger.info("🛑 Stopping all components...")
            
            # Arrêter les composants dans l'ordre inverse
            if hasattr(self, 'action_orchestrator'):
                self.action_orchestrator.stop()
            if hasattr(self, 'nlp_rag'):
                self.nlp_rag.stop()
            if hasattr(self, 'ai_manager'):
                self.ai_manager.stop_hybrid_mode()
            if hasattr(self, 'kali_tools'):
                self.kali_tools.stop()
            if hasattr(self, 'consciousness'):
                self.consciousness.stop_shared_mode()
            
            logger.info("🛑 Sharingan OS stopped")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"❌ Stop failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_hybrid_status(self) -> Dict:
        """Obtenir le statut du mode hybride"""
        return {
            "ai_providers": list(self.ai_manager.providers.keys()) if hasattr(self, 'ai_manager') else [],
            "nlp_rag_active": self.nlp_rag.is_active if hasattr(self, 'nlp_rag') else False,
            "actions_active": self.action_orchestrator.is_active if hasattr(self, 'action_orchestrator') else False,
            "consciousness_shared": self.consciousness.shared_mode if hasattr(self, 'consciousness') else False,
            "kali_tools_active": self.kali_tools.is_active if hasattr(self, 'kali_tools') else False
        }


def get_startup_core() -> StartupCore:
    """Get singleton instance"""
    return StartupCore()


def main():
    """Point d'entrée principal du démarrage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sharingan OS - Startup System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--start', action='store_true', help='Start Sharingan OS')
    parser.add_argument('--stop', action='store_true', help='Stop Sharingan OS')
    parser.add_argument('--status', action='store_true', help='Show startup status')
    parser.add_argument('--validate', action='store_true', help='Validate startup readiness')
    parser.add_argument('--hybrid', action='store_true', help='Show hybrid status')
    
    args = parser.parse_args()
    
    core = get_startup_core()
    
    if args.start:
        result = core.start_sharingan()
        print(json.dumps(result, indent=2, default=str))
    
    elif args.stop:
        result = core.stop_sharingan()
        print(json.dumps(result, indent=2, default=str))
    
    elif args.status:
        status = core.get_status()
        print(json.dumps(status, indent=2, default=str))
    
    elif args.validate:
        validation = core.validate_startup()
        print(json.dumps(validation, indent=2, default=str))
    
    elif args.hybrid:
        hybrid = core.get_hybrid_status()
        print(json.dumps(hybrid, indent=2, default=str))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()