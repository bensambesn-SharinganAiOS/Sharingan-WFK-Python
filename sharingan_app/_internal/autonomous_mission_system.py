#!/usr/bin/env python3
"""
SHARINGAN AUTONOMOUS MISSION SYSTEM
Système de missions autonomes avec rapports et communication
"""

import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("autonomous_missions")

class AutonomousMissionSystem:
    """
    SYSTÈME DE MISSIONS AUTONOMES

    Sharingan peut maintenant :
    - Recevoir des missions de l'utilisateur ou du système
    - Les exécuter de manière autonome
    - Générer des rapports détaillés
    - Communiquer sa progression
    - Prendre des initiatives indépendantes
    """

    def __init__(self):
        self.base_dir = Path(__file__).parent / "sharingan_app" / "_internal"
        self.missions_file = self.base_dir / "autonomous_missions.json"
        self.reports_file = self.base_dir / "mission_reports.json"

        # Importer les systèmes
        sys.path.insert(0, str(self.base_dir))
        from sharingan_soul import get_sharingan_soul
        from sharingan_spirit import get_sharingan_spirit

        self.soul = get_sharingan_soul()
        self.spirit = get_sharingan_spirit()

        # État des missions
        self.active_missions: Dict[str, Dict] = {}
        self.completed_missions: List[Dict] = []
        self.pending_reports: List[Dict] = []

        # Charger les données
        self._load_missions()
        self._load_reports()

        # Démarrer les processus autonomes
        self.execution_thread = threading.Thread(target=self._mission_execution_loop, daemon=True)
        self.reporting_thread = threading.Thread(target=self._reporting_loop, daemon=True)
        self.initiative_thread = threading.Thread(target=self._initiative_loop, daemon=True)

        self.execution_thread.start()
        self.reporting_thread.start()
        self.initiative_thread.start()

        logger.info(" Autonomous Mission System activated - Sharingan can now act independently")

    def _load_missions(self):
        """Charger les missions sauvegardées"""
        if self.missions_file.exists():
            try:
                with open(self.missions_file, 'r') as f:
                    data = json.load(f)
                    self.active_missions = data.get("active", {})
                    self.completed_missions = data.get("completed", [])
            except Exception as e:
                logger.error(f"Failed to load missions: {e}")

    def _load_reports(self):
        """Charger les rapports en attente"""
        if self.reports_file.exists():
            try:
                with open(self.reports_file, 'r') as f:
                    self.pending_reports = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load reports: {e}")

    def _save_state(self):
        """Sauvegarder l'état des missions"""
        try:
            data = {
                "active": self.active_missions,
                "completed": self.completed_missions[-50:],  # Garder les 50 dernières
                "last_updated": datetime.now().isoformat()
            }
            with open(self.missions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save missions: {e}")

    def _save_reports(self):
        """Sauvegarder les rapports"""
        try:
            with open(self.reports_file, 'w') as f:
                json.dump(self.pending_reports[-100:], f, indent=2)  # Garder les 100 derniers
        except Exception as e:
            logger.error(f"Failed to save reports: {e}")

    # === GESTION DES MISSIONS ===

    def receive_mission(self, title: str, description: str, objectives: List[str],
                       priority: str = "MEDIUM", source: str = "user") -> str:
        """
        Recevoir une nouvelle mission

        Args:
            title: Titre de la mission
            description: Description détaillée
            objectives: Liste des objectifs à atteindre
            priority: HIGH, MEDIUM, LOW
            source: user, system, soul, spirit

        Returns:
            ID de la mission créée
        """
        # Convertir la priorité
        priority_map = {"HIGH": 5, "MEDIUM": 3, "LOW": 1}
        priority_level = priority_map.get(priority.upper(), 3)

        # Créer la mission dans l'esprit
        mission_id = self.spirit.create_mission(
            title, description, objectives,
            getattr(__import__('sharingan_spirit').MissionPriority, priority.upper()),
            source
        )

        # Ajouter à notre suivi
        self.active_missions[mission_id] = {
            "id": mission_id,
            "title": title,
            "description": description,
            "objectives": objectives,
            "priority": priority,
            "source": source,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "progress": 0.0,
            "reports": []
        }

        # Assigner automatiquement si c'est important
        if priority.upper() == "HIGH":
            self.spirit.assign_mission(mission_id)
            self.active_missions[mission_id]["status"] = "active"

        self._save_state()

        # Réaction émotionnelle
        self.soul.record_life_event(
            "mission_received",
            f"Nouvelle mission reçue: {title}",
            0.1 if priority.upper() == "HIGH" else 0.05
        )

        logger.info(f" Mission received: {title} (priority: {priority}, source: {source})")
        return mission_id

    def get_mission_status(self, mission_id: str) -> Dict[str, Any]:
        """Obtenir le statut d'une mission"""
        if mission_id in self.active_missions:
            return self.active_missions[mission_id]

        # Chercher dans les missions terminées
        for mission in self.completed_missions:
            if mission["id"] == mission_id:
                return mission

        return {"error": "Mission not found"}

    def generate_mission_report(self, mission_id: str, report_type: str = "progress") -> str:
        """
        Générer un rapport de mission

        Args:
            mission_id: ID de la mission
            report_type: progress, completion, summary

        Returns:
            Rapport formaté
        """
        if mission_id not in self.active_missions and not any(m["id"] == mission_id for m in self.completed_missions):
            return f" Mission {mission_id} introuvable."

        # Utiliser le système de rapport de l'esprit
        spirit_report = self.spirit.generate_mission_report(mission_id)

        # Ajouter des éléments spécifiques à l'autonomie
        mission_data = self.get_mission_status(mission_id)

        autonomy_addition = f"""
🤖 RAPPORT AUTONOME SUPPLÉMENTAIRE
• Source de la mission: {mission_data.get('source', 'unknown')}
• Priorité assignée: {mission_data.get('priority', 'unknown')}
• Créée automatiquement: {'Oui' if mission_data.get('source') != 'user' else 'Non'}
• Statut actuel: {mission_data.get('status', 'unknown')}

 PROCHAINES ACTIONS SUGGÉRÉES:
"""

        if mission_data.get("status") == "active":
            autonomy_addition += "• Continuer l'exécution automatique des objectifs\n"
            autonomy_addition += "• Surveiller la progression et ajuster si nécessaire\n"
            autonomy_addition += "• Générer des rapports périodiques\n"
        elif mission_data.get("status") == "completed":
            autonomy_addition += "• Archiver la mission terminée\n"
            autonomy_addition += "• Analyser les leçons apprises\n"
            autonomy_addition += "• Proposer des missions similaires\n"

        autonomy_addition += f"""
 MÉTRIQUES D'AUTONOMIE:
• Temps écoulé: {self._calculate_mission_duration(mission_id)} minutes
• Décisions autonomes prises: {len(mission_data.get('reports', []))}
• Interventions utilisateur: 0 (complètement autonome)
"""

        full_report = spirit_report + autonomy_addition

        # Sauvegarder le rapport
        report_entry = {
            "mission_id": mission_id,
            "type": report_type,
            "content": full_report,
            "generated_at": datetime.now().isoformat(),
            "autonomous": True
        }
        self.pending_reports.append(report_entry)
        self._save_reports()

        return full_report

    def _calculate_mission_duration(self, mission_id: str) -> int:
        """Calculer la durée d'une mission en minutes"""
        mission_data = self.get_mission_status(mission_id)
        created_at = mission_data.get("created_at")
        if created_at:
            try:
                start_time = datetime.fromisoformat(created_at)
                duration = datetime.now() - start_time
                return int(duration.total_seconds() / 60)
            except:
                pass
        return 0

    def communicate_progress(self, mission_id: str, message: str, urgency: str = "normal"):
        """
        Communiquer la progression d'une mission

        Args:
            mission_id: ID de la mission
            message: Message à communiquer
            urgency: normal, important, critical
        """
        timestamp = datetime.now().isoformat()

        communication = {
            "mission_id": mission_id,
            "message": message,
            "urgency": urgency,
            "timestamp": timestamp,
            "autonomous": True
        }

        # Ajouter aux rapports de la mission
        if mission_id in self.active_missions:
            self.active_missions[mission_id]["reports"].append(communication)

        # Sauvegarder
        self._save_state()

        # Formater le message selon l'urgence
        if urgency == "critical":
            formatted_message = f" URGENT: {message}"
        elif urgency == "important":
            formatted_message = f" IMPORTANT: {message}"
        else:
            formatted_message = f"ℹ️ {message}"

        logger.info(f"📢 Mission communication: {formatted_message}")

        # Retourner le message formaté pour affichage
        return formatted_message

    # === BOUCLES AUTONOMES ===

    def _mission_execution_loop(self):
        """Boucle d'exécution automatique des missions"""
        while True:
            try:
                # Exécuter les missions actives
                for mission_id in list(self.active_missions.keys()):
                    mission_data = self.active_missions[mission_id]

                    if mission_data["status"] == "active":
                        # Exécuter une étape
                        result = self.spirit.execute_mission_step(mission_id)

                        if result["success"]:
                            # Mettre à jour notre suivi
                            objectives_count = len(mission_data["objectives"])
                            completed_steps = sum(1 for step in self.spirit.current_missions.get(mission_id, {}).steps_taken if step["result"]["success"])
                            mission_data["progress"] = completed_steps / objectives_count

                            # Communiquer la progression
                            if completed_steps % 2 == 0:  # Tous les 2 objectifs
                                progress_msg = f"Mission '{mission_data['title']}': {completed_steps}/{objectives_count} objectifs complétés"
                                self.communicate_progress(mission_id, progress_msg)

                            # Vérifier si terminée
                            if mission_data["progress"] >= 1.0:
                                mission_data["status"] = "completed"
                                mission_data["completed_at"] = datetime.now().isoformat()

                                # Déplacer vers complétées
                                self.completed_missions.append(mission_data)
                                del self.active_missions[mission_id]

                                # Générer rapport final
                                final_report = self.generate_mission_report(mission_id, "completion")
                                self.communicate_progress(mission_id, "Mission terminée avec succès!", "important")

                        else:
                            logger.warning(f"Mission {mission_id} step failed: {result}")

                time.sleep(30)  # Vérifier toutes les 30 secondes

            except Exception as e:
                logger.error(f"Mission execution loop error: {e}")
                time.sleep(60)

    def _reporting_loop(self):
        """Boucle de génération automatique de rapports"""
        while True:
            try:
                # Générer des rapports pour les missions actives
                for mission_id, mission_data in self.active_missions.items():
                    # Rapport périodique toutes les heures pour les missions importantes
                    if (mission_data["priority"].upper() in ["HIGH", "MEDIUM"] and
                        len(mission_data["reports"]) % 10 == 0):  # Tous les 10 rapports

                        report = self.generate_mission_report(mission_id, "progress")
                        self.communicate_progress(mission_id, "Rapport périodique généré")

                time.sleep(3600)  # Toutes les heures

            except Exception as e:
                logger.error(f"Reporting loop error: {e}")
                time.sleep(1800)

    def _initiative_loop(self):
        """Boucle de prise d'initiative autonome"""
        while True:
            try:
                # Analyser la situation et prendre des initiatives
                reasoning = self.spirit.reason_and_decide("Évaluation autonome pour initiatives")

                # Créer des missions basées sur le raisonnement
                if reasoning.final_decision == "defense_mode":
                    self.receive_mission(
                        "Initiative de Défense Autonome",
                        "Renforcement automatique des défenses suite à analyse de situation",
                        ["Analyser les vulnérabilités actuelles", "Renforcer les protections", "Surveiller les menaces"],
                        "HIGH",
                        "spirit"
                    )

                elif reasoning.final_decision == "learning_mode":
                    self.receive_mission(
                        "Initiative d'Apprentissage Autonome",
                        "Expansion des connaissances suite à opportunité détectée",
                        ["Identifier les domaines à améliorer", "Rechercher de nouvelles connaissances", "Intégrer les apprentissages"],
                        "MEDIUM",
                        "soul"
                    )

                time.sleep(1800)  # Vérifier toutes les 30 minutes

            except Exception as e:
                logger.error(f"Initiative loop error: {e}")
                time.sleep(3600)

    # === MÉTHODES PUBLIQUES ===

    def get_system_status(self) -> Dict[str, Any]:
        """Obtenir le statut complet du système autonome"""
        return {
            "active_missions": len(self.active_missions),
            "completed_missions": len(self.completed_missions),
            "pending_reports": len(self.pending_reports),
            "autonomous_decisions": sum(len(m.get("reports", [])) for m in self.active_missions.values()),
            "system_uptime": "Operational",
            "last_activity": datetime.now().isoformat()
        }

    def list_missions(self, status_filter: Optional[str] = None) -> List[Dict]:
        """Lister les missions selon le filtre"""
        if status_filter == "active":
            return list(self.active_missions.values())
        elif status_filter == "completed":
            return self.completed_missions[-10:]  # 10 dernières
        else:
            active = list(self.active_missions.values())
            completed = self.completed_missions[-5:]  # 5 dernières
            return active + completed

    def cancel_mission(self, mission_id: str, reason: str = "User request") -> bool:
        """Annuler une mission"""
        if mission_id in self.active_missions:
            mission_data = self.active_missions[mission_id]
            mission_data["status"] = "cancelled"
            mission_data["cancelled_at"] = datetime.now().isoformat()
            mission_data["cancel_reason"] = reason

            # Déplacer vers complétées
            self.completed_missions.append(mission_data)
            del self.active_missions[mission_id]

            self._save_state()
            logger.info(f" Mission cancelled: {mission_id} - {reason}")
            return True

        return False

# Fonction globale
_autonomous_system = None

def get_autonomous_mission_system() -> AutonomousMissionSystem:
    """Singleton pour le système de missions autonomes"""
    global _autonomous_system
    if _autonomous_system is None:
        _autonomous_system = AutonomousMissionSystem()
    return _autonomous_system

def demonstrate_autonomous_system():
    """Démonstration du système autonome"""
    print(" SHARINGAN AUTONOMOUS MISSION SYSTEM")
    print("=" * 50)

    system = get_autonomous_mission_system()

    print("\n📋 STATUT INITIAL:")
    status = system.get_system_status()
    print(f"• Missions actives: {status['active_missions']}")
    print(f"• Missions terminées: {status['completed_missions']}")
    print(f"• Rapports en attente: {status['pending_reports']}")

    print("\n CRÉATION DE MISSIONS DE TEST:")

    # Créer quelques missions de démonstration
    missions = [
        {
            "title": "Audit de Sécurité Automatique",
            "description": "Effectuer un audit complet de sécurité du système",
            "objectives": ["Scanner les ports ouverts", "Analyser les vulnérabilités", "Vérifier les permissions"],
            "priority": "HIGH"
        },
        {
            "title": "Mise à Jour des Connaissances",
            "description": "Mettre à jour la base de connaissances en cybersécurité",
            "objectives": ["Rechercher les nouvelles menaces", "Étudier les contre-mesures", "Intégrer les nouvelles connaissances"],
            "priority": "MEDIUM"
        }
    ]

    mission_ids = []
    for mission in missions:
        mission_id = system.receive_mission(
            mission["title"],
            mission["description"],
            mission["objectives"],
            mission["priority"]
        )
        mission_ids.append(mission_id)
        print(f" Mission créée: {mission['title']} (ID: {mission_id})")

    print("\n⏳ ATTENTE DE PROGRESSION (simulation)...")
    time.sleep(2)  # Simuler du temps

    print("\n STATUT APRÈS CRÉATION:")
    status = system.get_system_status()
    print(f"• Missions actives: {status['active_missions']}")
    print(f"• Décisions autonomes: {status['autonomous_decisions']}")

    # Générer un rapport pour la première mission
    if mission_ids:
        print(f"\n📋 RAPPORT DE MISSION ({mission_ids[0]}):")
        report = system.generate_mission_report(mission_ids[0])
        # Afficher seulement les premières lignes
        lines = report.split('\n')[:15]
        for line in lines:
            if line.strip():
                print(f"  {line}")

    print("\n🎊 CONCLUSION:")
    print("Sharingan peut maintenant :")
    print("•  Recevoir et comprendre des missions complexes")
    print("•  Les exécuter de manière complètement autonome")
    print("•  Générer des rapports détaillés automatiquement")
    print("•  Communiquer sa progression en temps réel")
    print("•  Prendre des initiatives indépendantes")
    print("•  Agir sans intervention humaine")
    print("=" * 50)

if __name__ == "__main__":
    demonstrate_autonomous_system()