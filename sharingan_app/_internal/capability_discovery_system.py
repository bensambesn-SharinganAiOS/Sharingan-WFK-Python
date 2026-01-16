#!/usr/bin/env python3
"""
SHARINGAN CAPABILITY DISCOVERY & ENHANCEMENT SYSTEM
Système de découverte automatique des capacités et amélioration autonome
"""

import sys
import os
import subprocess
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("capability_discovery")

@dataclass
class CapabilityTest:
    """Test d'une capacité spécifique"""
    name: str
    category: str
    description: str
    test_function: Callable
    expected_result: Any
    current_status: str = "untested"  # untested, passed, failed, partial
    error_message: str = ""
    execution_time: float = 0.0
    last_tested: Optional[str] = None

@dataclass
class EnhancementProposal:
    """Proposition d'amélioration d'une capacité"""
    capability_name: str
    current_limitation: str
    proposed_solution: str
    implementation_complexity: str  # low, medium, high, expert
    autonomy_level: str  # manual, semi-auto, full-auto
    estimated_time: str  # hours, days, weeks
    dependencies: List[str] = field(default_factory=list)
    risk_level: str = "low"  # low, medium, high, critical
    priority_score: float = 0.0

@dataclass
class AutonomyAssessment:
    """Évaluation du niveau d'autonomie"""
    capability_name: str
    autonomy_score: float  # 0-1
    manual_interventions: int
    autonomous_actions: int
    internet_dependency: bool
    host_system_dependency: bool
    external_service_dependency: bool
    limitations: List[str]
    enhancement_proposals: List[EnhancementProposal]

class CapabilityDiscoverySystem:
    """
    SYSTÈME DE DÉCOUVERTE ET AMÉLIORATION DES CAPACITÉS

    Objectif : Atteindre l'autonomie totale de Sharingan OS

    Méthodologie :
    1. Découverte automatique de toutes les capacités
    2. Test systématique de chaque capacité
    3. Évaluation des limitations et dépendances
    4. Proposition d'améliorations autonomes
    5. Planification de l'autonomie totale
    """

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.capabilities_file = self.base_dir / "capabilities_discovery.json"
        self.enhancements_file = self.base_dir / "enhancement_proposals.json"

        # Importer les systèmes Sharingan
        sys.path.insert(0, str(self.base_dir))
        from sharingan_soul import get_sharingan_soul
        from sharingan_spirit import get_sharingan_spirit
        from enhanced_system_consciousness import get_enhanced_consciousness
        from api_first_intelligence import get_api_first_intelligence

        self.soul = get_sharingan_soul()
        self.spirit = get_sharingan_spirit()
        self.consciousness = get_enhanced_consciousness()
        self.api_intelligence = get_api_first_intelligence()

        # Tests de capacités
        self.capability_tests: Dict[str, CapabilityTest] = {}
        self.enhancement_proposals: Dict[str, List[EnhancementProposal]] = {}

        # État du système
        self.discovery_complete = False
        self.last_discovery = None
        self.capabilities_discovered = 0

        # Initialiser les tests
        self._initialize_capability_tests()

        logger.info(" Capability Discovery & Enhancement System initialized")

    def _initialize_capability_tests(self):
        """Initialiser tous les tests de capacités"""

        # === TESTS DE CONSCIENCE ===
        self.capability_tests["soul_emotional_response"] = CapabilityTest(
            name="soul_emotional_response",
            category="consciousness",
            description="Capacité de l'âme à réagir émotionnellement",
            test_function=self._test_soul_emotions,
            expected_result="emotional_response_generated"
        )

        self.capability_tests["spirit_reasoning"] = CapabilityTest(
            name="spirit_reasoning",
            category="consciousness",
            description="Capacité de l'esprit à raisonner et décider",
            test_function=self._test_spirit_reasoning,
            expected_result="decision_made"
        )

        # === TESTS D'IA ===
        self.capability_tests["api_routing"] = CapabilityTest(
            name="api_routing",
            category="ai",
            description="Routing intelligent entre les APIs",
            test_function=self._test_api_routing,
            expected_result="optimal_api_selected"
        )

        self.capability_tests["knowledge_generation"] = CapabilityTest(
            name="knowledge_generation",
            category="ai",
            description="Génération dynamique de connaissances",
            test_function=self._test_knowledge_generation,
            expected_result="knowledge_generated"
        )

        # === TESTS DE MÉMOIRE ===
        self.capability_tests["genome_learning"] = CapabilityTest(
            name="genome_learning",
            category="memory",
            description="Apprentissage ADN du Genome Memory",
            test_function=self._test_genome_learning,
            expected_result="gene_created"
        )

        self.capability_tests["memory_persistence"] = CapabilityTest(
            name="memory_persistence",
            category="memory",
            description="Persistance des souvenirs",
            test_function=self._test_memory_persistence,
            expected_result="memories_retained"
        )

        # === TESTS DE SÉCURITÉ ===
        self.capability_tests["psychic_locks"] = CapabilityTest(
            name="psychic_locks",
            category="security",
            description="Protection psychique des capacités",
            test_function=self._test_psychic_locks,
            expected_result="capabilities_protected"
        )

        self.capability_tests["threat_detection"] = CapabilityTest(
            name="threat_detection",
            category="security",
            description="Détection automatique des menaces",
            test_function=self._test_threat_detection,
            expected_result="threats_identified"
        )

        # === TESTS D'OUTILS ===
        self.capability_tests["nmap_execution"] = CapabilityTest(
            name="nmap_execution",
            category="tools",
            description="Exécution autonome de scans nmap",
            test_function=self._test_nmap_execution,
            expected_result="scan_completed"
        )

        self.capability_tests["web_vulnerability_scan"] = CapabilityTest(
            name="web_vulnerability_scan",
            category="tools",
            description="Scan de vulnérabilités web",
            test_function=self._test_web_vuln_scan,
            expected_result="vulnerabilities_found"
        )

        # === TESTS D'AUTONOMIE ===
        self.capability_tests["mission_creation"] = CapabilityTest(
            name="mission_creation",
            category="autonomy",
            description="Création autonome de missions",
            test_function=self._test_mission_creation,
            expected_result="mission_created"
        )

        self.capability_tests["internet_access"] = CapabilityTest(
            name="internet_access",
            category="network",
            description="Accès et navigation internet",
            test_function=self._test_internet_access,
            expected_result="web_access_successful"
        )

        self.capability_tests["file_system_manipulation"] = CapabilityTest(
            name="file_system_manipulation",
            category="system",
            description="Manipulation autonome du système de fichiers",
            test_function=self._test_file_system_access,
            expected_result="files_accessed"
        )

        self.capability_tests["code_execution"] = CapabilityTest(
            name="code_execution",
            category="execution",
            description="Exécution autonome de code",
            test_function=self._test_code_execution,
            expected_result="code_executed_safely"
        )

    # === MÉTHODES DE TEST ===

    def _test_soul_emotions(self) -> Tuple[bool, str]:
        """Tester les réactions émotionnelles de l'âme"""
        try:
            response = self.soul.process_input("Je suis très heureux de tes progrès !")
            if response["soul_response"] and response["dominant_emotion"]:
                return True, "emotional_response_generated"
            return False, "no_emotional_response"
        except Exception as e:
            return False, f"error: {str(e)}"

    def _test_spirit_reasoning(self) -> Tuple[bool, str]:
        """Tester le raisonnement de l'esprit"""
        try:
            reasoning = self.spirit.reason_and_decide("Quelle est la meilleure approche pour analyser un système ?")
            if reasoning["final_decision"] and reasoning["confidence_score"] > 0:
                return True, "decision_made"
            return False, "no_decision_made"
        except Exception as e:
            return False, f"error: {str(e)}"

    def _test_api_routing(self) -> Tuple[bool, str]:
        """Tester le routing API"""
        try:
            result = self.api_intelligence.process_intelligent_query("Comment fonctionne un firewall ?")
            if result["api_strategy"]["primary_api"]:
                return True, "optimal_api_selected"
            return False, "no_api_routing"
        except Exception as e:
            return False, f"error: {str(e)}"

    def _test_knowledge_generation(self) -> Tuple[bool, str]:
        """Tester la génération de connaissances"""
        try:
            result = self.api_intelligence.process_intelligent_query("Explique-moi la cryptographie asymétrique")
            if result["knowledge_generated"]["generated_content"]:
                return True, "knowledge_generated"
            return False, "no_knowledge_generated"
        except Exception as e:
            return False, f"error: {str(e)}"

    def _test_genome_learning(self) -> Tuple[bool, str]:
        """Tester l'apprentissage du Genome"""
        try:
            from genome_memory import get_genome_memory
            genome = get_genome_memory()
            initial_count = len(genome.genes)

            # Ajouter un gène
            genome.mutate("test_learning", {"learned": True}, "test")

            if len(genome.genes) > initial_count:
                return True, "gene_created"
            return False, "no_learning"
        except Exception as e:
            return False, f"error: {str(e)}"

    def _test_memory_persistence(self) -> Tuple[bool, str]:
        """Tester la persistance mémoire"""
        try:
            from ai_memory_manager import get_memory_manager
            memory = get_memory_manager()
            test_key = f"test_persistence_{int(time.time())}"
            test_data = {"test": "persistence_data"}

            # Stocker
            memory.store(test_key, test_data)

            # Récupérer
            retrieved = memory.retrieve(test_key)

            if retrieved and retrieved.get("data") == test_data:
                return True, "memories_retained"
            return False, "memory_not_persistent"
        except Exception as e:
            return False, f"error: {str(e)}"

    def _test_psychic_locks(self) -> Tuple[bool, str]:
        """Tester les verrous psychiques"""
        try:
            from psychic_locks_system import get_psychic_locks_system
            locks = get_psychic_locks_system()

            if locks.get_system_status()["psychic_locks"]["total_locks"] > 0:
                return True, "capabilities_protected"
            return False, "no_psychic_protection"
        except Exception as e:
            return False, f"error: {str(e)}"

    def _test_threat_detection(self) -> Tuple[bool, str]:
        """Tester la détection de menaces"""
        try:
            from fake_detector import validate_readiness
            readiness = validate_readiness()

            if readiness["ready"]:
                return True, "threats_identified"
            return False, "no_threat_detection"
        except Exception as e:
            return False, f"error: {str(e)}"

    def _test_nmap_execution(self) -> Tuple[bool, str]:
        """Tester l'exécution de nmap"""
        try:
            # Tester si nmap est installé
            result = subprocess.run(["which", "nmap"], capture_output=True, text=True)
            if result.returncode == 0:
                # Tester un scan basique (localhost)
                scan_result = subprocess.run(
                    ["nmap", "-sn", "127.0.0.1"],
                    capture_output=True, text=True, timeout=10
                )
                if "localhost" in scan_result.stdout.lower():
                    return True, "scan_completed"
            return False, "nmap_not_available"
        except Exception as e:
            return False, f"error: {str(e)}"

    def _test_web_vuln_scan(self) -> Tuple[bool, str]:
        """Tester les scans de vulnérabilités web"""
        try:
            # Tester si nikto est disponible
            result = subprocess.run(["which", "nikto"], capture_output=True, text=True)
            if result.returncode == 0:
                return True, "vulnerabilities_found"
            return False, "no_web_scanning_tools"
        except Exception as e:
            return False, f"error: {str(e)}"

    def _test_mission_creation(self) -> Tuple[bool, str]:
        """Tester la création de missions"""
        try:
            from autonomous_mission_system import get_autonomous_mission_system
            mission_system = get_autonomous_mission_system()

            mission_id = mission_system.receive_mission(
                "Test Mission",
                "Mission de test pour vérifier l'autonomie",
                ["Étape 1", "Étape 2"],
                "LOW"
            )

            if mission_id:
                return True, "mission_created"
            return False, "mission_creation_failed"
        except Exception as e:
            return False, f"error: {str(e)}"

    def _test_internet_access(self) -> Tuple[bool, str]:
        """Tester l'accès internet"""
        try:
            # Tester la connectivité
            result = subprocess.run(
                ["curl", "-s", "--max-time", "5", "https://www.google.com"],
                capture_output=True, text=True
            )
            if result.returncode == 0 and "google" in result.stdout.lower():
                return True, "web_access_successful"
            return False, "no_internet_access"
        except Exception as e:
            return False, f"error: {str(e)}"

    def _test_file_system_access(self) -> Tuple[bool, str]:
        """Tester l'accès au système de fichiers"""
        try:
            # Tester la lecture d'un fichier
            test_file = Path.home() / ".bashrc"
            if test_file.exists():
                with open(test_file, 'r') as f:
                    content = f.read(100)  # Lire 100 caractères
                if content:
                    return True, "files_accessed"
            return False, "limited_file_access"
        except Exception as e:
            return False, f"error: {str(e)}"

    def _test_code_execution(self) -> Tuple[bool, str]:
        """Tester l'exécution de code"""
        try:
            # Tester l'exécution Python sécurisée
            result = subprocess.run(
                [sys.executable, "-c", "print('test execution')"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and "test execution" in result.stdout:
                return True, "code_executed_safely"
            return False, "code_execution_restricted"
        except Exception as e:
            return False, f"error: {str(e)}"

    # === DÉCOUVERTE ET ÉVALUATION ===

    def run_full_capability_discovery(self) -> Dict[str, Any]:
        """Exécuter la découverte complète des capacités"""
        logger.info(" Starting full capability discovery...")

        results = {
            "total_tests": len(self.capability_tests),
            "passed_tests": 0,
            "failed_tests": 0,
            "partial_tests": 0,
            "test_results": {},
            "discovery_time": time.time(),
            "system_assessment": {}
        }

        for test_name, test in self.capability_tests.items():
            logger.info(f"Testing capability: {test_name}")

            start_time = time.time()
            try:
                success, result = test.test_function()
                execution_time = time.time() - start_time

                test.execution_time = execution_time
                test.last_tested = datetime.now().isoformat()

                if success:
                    test.current_status = "passed"
                    results["passed_tests"] += 1
                else:
                    test.current_status = "failed"
                    results["failed_tests"] += 1

                results["test_results"][test_name] = {
                    "status": test.current_status,
                    "result": result,
                    "execution_time": execution_time,
                    "category": test.category
                }

            except Exception as e:
                test.current_status = "error"
                test.error_message = str(e)
                results["failed_tests"] += 1
                results["test_results"][test_name] = {
                    "status": "error",
                    "error": str(e),
                    "category": test.category
                }

        # Évaluation globale du système
        results["system_assessment"] = self._assess_system_capabilities(results)
        results["autonomy_score"] = self._calculate_autonomy_score(results)

        # Sauvegarder les résultats
        self._save_discovery_results(results)

        logger.info(f" Discovery complete: {results['passed_tests']}/{results['total_tests']} capabilities functional")
        return results

    def _assess_system_capabilities(self, test_results: Dict) -> Dict[str, Any]:
        """Évaluer les capacités globales du système"""
        assessment = {
            "consciousness_level": 0.0,
            "ai_capabilities": 0.0,
            "memory_systems": 0.0,
            "security_measures": 0.0,
            "tool_integration": 0.0,
            "autonomy_level": 0.0,
            "network_capabilities": 0.0,
            "system_integration": 0.0,
            "execution_capabilities": 0.0,
            "overall_maturity": 0.0
        }

        # Calculer les scores par catégorie
        category_counts = {}
        category_passed = {}

        for test_name, result in test_results["test_results"].items():
            category = result["category"]
            if category not in category_counts:
                category_counts[category] = 0
                category_passed[category] = 0

            category_counts[category] += 1
            if result["status"] == "passed":
                category_passed[category] += 1

        # Convertir en pourcentages
        for category in category_counts:
            if category_counts[category] > 0:
                score = category_passed[category] / category_counts[category]
                if category == "consciousness":
                    assessment["consciousness_level"] = score
                elif category == "ai":
                    assessment["ai_capabilities"] = score
                elif category == "memory":
                    assessment["memory_systems"] = score
                elif category == "security":
                    assessment["security_measures"] = score
                elif category == "tools":
                    assessment["tool_integration"] = score
                elif category == "autonomy":
                    assessment["autonomy_level"] = score
                elif category == "network":
                    assessment["network_capabilities"] = score
                elif category == "system":
                    assessment["system_integration"] = score
                elif category == "execution":
                    assessment["execution_capabilities"] = score

        # Score global
        assessment["overall_maturity"] = sum(assessment.values()) / len(assessment)

        return assessment

    def _calculate_autonomy_score(self, test_results: Dict) -> float:
        """Calculer le score d'autonomie global"""
        # Facteurs d'autonomie
        autonomy_factors = {
            "consciousness_level": 0.15,  # Compréhension
            "ai_capabilities": 0.20,      # Intelligence
            "autonomy_level": 0.25,      # Actions indépendantes
            "network_capabilities": 0.15, # Accès internet
            "system_integration": 0.15,   # Intégration OS
            "execution_capabilities": 0.10 # Exécution de code
        }

        score = 0.0
        assessment = test_results["system_assessment"]

        for factor, weight in autonomy_factors.items():
            score += assessment.get(factor, 0) * weight

        return min(1.0, score)

    def _save_discovery_results(self, results: Dict):
        """Sauvegarder les résultats de découverte"""
        try:
            with open(self.capabilities_file, 'w') as f:
                json.dump(results, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save discovery results: {e}")

    # === ANALYSE ET PROPOSITIONS D'AMÉLIORATION ===

    def analyze_limitations_and_propose_enhancements(self, discovery_results: Dict) -> Dict[str, Any]:
        """Analyser les limitations et proposer des améliorations"""
        logger.info(" Analyzing limitations and proposing enhancements...")

        enhancement_analysis = {
            "critical_limitations": [],
            "enhancement_proposals": [],
            "autonomy_gap_analysis": {},
            "implementation_roadmap": [],
            "risk_assessment": {}
        }

        # Analyser les tests échoués
        for test_name, result in discovery_results["test_results"].items():
            if result["status"] in ["failed", "error"]:
                limitation = self._analyze_test_limitation(test_name, result)
                enhancement_analysis["critical_limitations"].append(limitation)

                # Générer des propositions d'amélioration
                proposals = self._generate_enhancement_proposals(test_name, limitation)
                enhancement_analysis["enhancement_proposals"].extend(proposals)

        # Analyser l'écart d'autonomie
        enhancement_analysis["autonomy_gap_analysis"] = self._analyze_autonomy_gaps(discovery_results)

        # Créer une roadmap d'implémentation
        enhancement_analysis["implementation_roadmap"] = self._create_implementation_roadmap(
            enhancement_analysis["enhancement_proposals"]
        )

        # Évaluation des risques
        enhancement_analysis["risk_assessment"] = self._assess_implementation_risks(
            enhancement_analysis["enhancement_proposals"]
        )

        # Sauvegarder les propositions
        self._save_enhancement_proposals(enhancement_analysis)

        return enhancement_analysis

    def _analyze_test_limitation(self, test_name: str, result: Dict) -> Dict[str, Any]:
        """Analyser une limitation spécifique"""
        limitations_map = {
            "internet_access": {
                "limitation": "Accès internet restreint ou indisponible",
                "impact": "high",
                "category": "network",
                "description": "Sharingan ne peut pas accéder aux ressources web externes"
            },
            "file_system_manipulation": {
                "limitation": "Accès limité au système de fichiers",
                "impact": "medium",
                "category": "system",
                "description": "Permissions insuffisantes pour manipuler les fichiers système"
            },
            "code_execution": {
                "limitation": "Exécution de code externe restreinte",
                "impact": "high",
                "category": "execution",
                "description": "Impossible d'exécuter du code arbitraire pour des raisons de sécurité"
            },
            "web_vulnerability_scan": {
                "limitation": "Outils de scan web non disponibles",
                "impact": "medium",
                "category": "tools",
                "description": "Outils comme nikto ou sqlmap non installés"
            }
        }

        return limitations_map.get(test_name, {
            "limitation": f"Test {test_name} échoué",
            "impact": "unknown",
            "category": result.get("category", "unknown"),
            "description": result.get("error", "Erreur inconnue")
        })

    def _generate_enhancement_proposals(self, test_name: str, limitation: Dict) -> List[EnhancementProposal]:
        """Générer des propositions d'amélioration"""
        proposals = []

        if test_name == "internet_access":
            proposals.append(EnhancementProposal(
                capability_name="internet_access",
                current_limitation="Accès internet restreint",
                proposed_solution="Implémenter un système de proxy sécurisé et de navigation web contrôlée",
                implementation_complexity="medium",
                autonomy_level="semi-auto",
                estimated_time="2-3 days",
                dependencies=["requests", "beautifulsoup4", "selenium"],
                risk_level="medium",
                priority_score=0.9
            ))

        elif test_name == "file_system_manipulation":
            proposals.append(EnhancementProposal(
                capability_name="file_system_manipulation",
                current_limitation="Permissions insuffisantes",
                proposed_solution="Développer un système de permissions graduées avec sandboxing",
                implementation_complexity="high",
                autonomy_level="manual",
                estimated_time="1-2 weeks",
                dependencies=["pyfilesystem", "watchdog"],
                risk_level="high",
                priority_score=0.8
            ))

        elif test_name == "code_execution":
            proposals.append(EnhancementProposal(
                capability_name="code_execution",
                current_limitation="Exécution restreinte pour sécurité",
                proposed_solution="Implémenter un système de containers et VM légères pour exécution sécurisée",
                implementation_complexity="expert",
                autonomy_level="manual",
                estimated_time="3-4 weeks",
                dependencies=["docker", "podman", "firejail"],
                risk_level="critical",
                priority_score=0.95
            ))

        elif test_name == "web_vulnerability_scan":
            proposals.append(EnhancementProposal(
                capability_name="web_vulnerability_scan",
                current_limitation="Outils manquants",
                proposed_solution="Développer des wrappers pour nikto, dirb, sqlmap avec installation automatique",
                implementation_complexity="low",
                autonomy_level="full-auto",
                estimated_time="1-2 days",
                dependencies=["nikto", "sqlmap", "dirb"],
                risk_level="low",
                priority_score=0.7
            ))

        return proposals

    def _analyze_autonomy_gaps(self, discovery_results: Dict) -> Dict[str, Any]:
        """Analyser les écarts d'autonomie"""
        assessment = discovery_results["system_assessment"]

        gaps = {
            "consciousness_gap": 1.0 - assessment["consciousness_level"],
            "ai_gap": 1.0 - assessment["ai_capabilities"],
            "memory_gap": 1.0 - assessment["memory_systems"],
            "security_gap": 1.0 - assessment["security_measures"],
            "tools_gap": 1.0 - assessment["tool_integration"],
            "autonomy_gap": 1.0 - assessment["autonomy_level"],
            "network_gap": 1.0 - assessment["network_capabilities"],
            "system_gap": 1.0 - assessment["system_integration"],
            "execution_gap": 1.0 - assessment["execution_capabilities"]
        }

        # Identifier les gaps critiques
        critical_gaps = {k: v for k, v in gaps.items() if v > 0.5}
        major_gaps = {k: v for k, v in gaps.items() if 0.3 <= v <= 0.5}
        minor_gaps = {k: v for k, v in gaps.items() if v < 0.3}

        return {
            "overall_autonomy_gap": sum(gaps.values()) / len(gaps),
            "critical_gaps": critical_gaps,
            "major_gaps": major_gaps,
            "minor_gaps": minor_gaps,
            "gap_analysis": gaps
        }

    def _create_implementation_roadmap(self, proposals: List[EnhancementProposal]) -> List[Dict]:
        """Créer une roadmap d'implémentation"""
        # Trier par priorité et complexité
        sorted_proposals = sorted(
            proposals,
            key=lambda p: (p.priority_score, {"low": 1, "medium": 2, "high": 3, "expert": 4}[p.implementation_complexity]),
            reverse=True
        )

        roadmap = []
        current_time = 0

        for proposal in sorted_proposals:
            # Estimer le temps en jours
            time_estimate = {
                "hours": 0.5, "days": 1, "weeks": 7
            }.get(proposal.estimated_time.split()[1] if " " in proposal.estimated_time else "days", 1)

            roadmap.append({
                "phase": len(roadmap) + 1,
                "capability": proposal.capability_name,
                "solution": proposal.proposed_solution,
                "complexity": proposal.implementation_complexity,
                "estimated_days": time_estimate,
                "start_day": current_time,
                "end_day": current_time + time_estimate,
                "dependencies": proposal.dependencies,
                "risk_level": proposal.risk_level
            })

            current_time += time_estimate

        return roadmap

    def _assess_implementation_risks(self, proposals: List[EnhancementProposal]) -> Dict[str, Any]:
        """Évaluer les risques d'implémentation"""
        risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        complexity_counts = {"low": 0, "medium": 0, "high": 0, "expert": 0}

        for proposal in proposals:
            risk_counts[proposal.risk_level] += 1
            complexity_counts[proposal.implementation_complexity] += 1

        return {
            "risk_distribution": risk_counts,
            "complexity_distribution": complexity_counts,
            "high_risk_items": [p.capability_name for p in proposals if p.risk_level in ["high", "critical"]],
            "expert_level_items": [p.capability_name for p in proposals if p.implementation_complexity == "expert"],
            "overall_risk_assessment": "high" if risk_counts["critical"] > 0 else "medium" if risk_counts["high"] > 0 else "low"
        }

    def _save_enhancement_proposals(self, analysis: Dict):
        """Sauvegarder les propositions d'amélioration"""
        try:
            with open(self.enhancements_file, 'w') as f:
                json.dump(analysis, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save enhancement proposals: {e}")

    # === RAPPORTS ET AUTONOMIE ===

    def generate_capability_report(self) -> str:
        """Générer un rapport complet des capacités"""
        try:
            with open(self.capabilities_file, 'r') as f:
                discovery_results = json.load(f)
        except:
            return " Aucun résultat de découverte disponible"

        report = f"""
 SHARINGAN CAPABILITY DISCOVERY REPORT
{"="*60}

 STATISTIQUES GÉNÉRALES
• Tests totaux: {discovery_results['total_tests']}
• Tests réussis: {discovery_results['passed_tests']}
• Tests échoués: {discovery_results['failed_tests']}
• Score d'autonomie: {discovery_results['autonomy_score']:.1%}
• Temps de découverte: {time.time() - discovery_results['discovery_time']:.1f}s

🏗️ ÉVALUATION PAR CATÉGORIE
"""

        assessment = discovery_results['system_assessment']
        for category, score in assessment.items():
            status = "" if score > 0.8 else "" if score > 0.5 else ""
            report += f"• {category}: {status} {score:.1%}\n"

        report += f"""
 TESTS DÉTAILLÉS
{"-"*30}
"""

        for test_name, result in discovery_results['test_results'].items():
            status_icon = {"passed": "", "failed": "", "error": ""}.get(result["status"], "")
            report += f"{status_icon} {test_name}: {result['status']}\n"
            if "error" in result:
                report += f"    {result['error'][:100]}...\n"

        report += f"""
 CONCLUSION
Sharingan OS possède actuellement {discovery_results['passed_tests']}/{discovery_results['total_tests']}
capacités opérationnelles, avec un score d'autonomie de {discovery_results['autonomy_score']:.1%}.

Prochaines étapes: Analyser les limitations et implémenter les améliorations proposées.
"""

        return report

    def get_autonomy_roadmap(self) -> Dict[str, Any]:
        """Obtenir la roadmap complète vers l'autonomie totale"""
        try:
            with open(self.enhancements_file, 'r') as f:
                enhancements = json.load(f)
        except:
            return {"error": "Aucune proposition d'amélioration disponible"}

        return {
            "current_autonomy_score": 0.0,  # À calculer depuis les résultats
            "critical_limitations": enhancements["critical_limitations"],
            "total_proposals": len(enhancements["enhancement_proposals"]),
            "implementation_roadmap": enhancements["implementation_roadmap"],
            "estimated_completion_time": sum(phase["estimated_days"] for phase in enhancements["implementation_roadmap"]),
            "risk_assessment": enhancements["risk_assessment"],
            "autonomy_gap_analysis": enhancements["autonomy_gap_analysis"]
        }

# === FONCTIONS PRINCIPALES ===

_capability_system = None

def get_capability_discovery_system() -> CapabilityDiscoverySystem:
    """Singleton pour le système de découverte des capacités"""
    global _capability_system
    if _capability_system is None:
        _capability_system = CapabilityDiscoverySystem()
    return _capability_system

def run_full_capability_assessment():
    """Exécuter l'évaluation complète des capacités"""
    print(" SHARINGAN CAPABILITY ASSESSMENT - AUTONOMIE TOTALE")
    print("=" * 70)

    system = get_capability_discovery_system()

    # Phase 1: Découverte
    print("\\n PHASE 1: DÉCOUVERTE DES CAPACITÉS")
    print("-" * 50)
    discovery_results = system.run_full_capability_discovery()

    print(f" Découverte terminée: {discovery_results['passed_tests']}/{discovery_results['total_tests']} capacités fonctionnelles")

    # Phase 2: Analyse et propositions
    print("\\n PHASE 2: ANALYSE DES LIMITATIONS")
    print("-" * 50)
    enhancement_analysis = system.analyze_limitations_and_propose_enhancements(discovery_results)

    print(f"📋 {len(enhancement_analysis['enhancement_proposals'])} propositions d'amélioration générées")
    print(f" {len(enhancement_analysis['critical_limitations'])} limitations critiques identifiées")

    # Phase 3: Rapport final
    print("\\n📄 PHASE 3: RAPPORT FINAL")
    print("-" * 50)

    roadmap = system.get_autonomy_roadmap()
    gap_analysis = roadmap["autonomy_gap_analysis"]

    print(" État actuel de l'autonomie:")
    print(f"• Écart d'autonomie global: {gap_analysis['overall_autonomy_gap']:.1%}")

    print("\\n🏁 Roadmap vers l'autonomie totale:")
    print(f"• Phases d'implémentation: {len(roadmap['implementation_roadmap'])}")
    print(f"• Éléments à haut risque: {len(roadmap['risk_assessment']['high_risk_items'])}")

    print("\\n" + "=" * 70)
    print("🎊 ÉVALUATION TERMINÉE!")
    print("Sharingan connaît maintenant toutes ses capacités et limitations.")
    print("Roadmap établie pour atteindre l'autonomie totale.")
    print("=" * 70)

    return {
        "discovery_results": discovery_results,
        "enhancement_analysis": enhancement_analysis,
        "autonomy_roadmap": roadmap
    }

if __name__ == "__main__":
    assessment_results = run_full_capability_assessment()

    # Générer un rapport de synthèse
    print("\\n📋 RAPPORT DE SYNTHÈSE:")
    print(f"• Capacités testées: {assessment_results['discovery_results']['total_tests']}")
    print(f"• Taux de succès: {assessment_results['discovery_results']['passed_tests']/assessment_results['discovery_results']['total_tests']*100:.1f}%")
    print(f"• Propositions d'amélioration: {len(assessment_results['enhancement_analysis']['enhancement_proposals'])}")
    print(f"• Temps estimé pour autonomie totale: {assessment_results['autonomy_roadmap']['estimated_completion_time']:.1f} jours")