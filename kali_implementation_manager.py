#!/usr/bin/env python3
"""
Kali Tools Implementation Manager
Gère l'implémentation séquentielle des wrappers Kali restants
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kali_manager")

class KaliImplementationManager:
    """Gère l'implémentation des outils Kali de manière séquentielle"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.kali_dir = self.base_dir / "kali_repos"
        self.kali_dir.mkdir(exist_ok=True)
        self.status_file = self.base_dir / "kali_implementation_status.json"
        self._load_status()

    def _load_status(self):
        """Charge le statut d'implémentation"""
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                self.status = json.load(f)
        else:
            self.status = {
                "current_phase": 0,
                "completed_phases": [],
                "failed_phases": [],
                "last_updated": None
            }

    def _save_status(self):
        """Sauvegarde le statut"""
        self.status["last_updated"] = str(time.time())
        with open(self.status_file, 'w') as f:
            json.dump(self.status, f, indent=2)

    def get_next_phase(self) -> Dict[str, Any]:
        """Retourne la prochaine phase à implémenter"""
        phases = [
            {
                "id": "enum_phase1",
                "name": "Enumeration Tools Phase 1",
                "description": "dnsrecon, fierce, dnsenum",
                "tools": ["dnsrecon", "fierce", "dnsenum"],
                "commands": [
                    "pip install dnsrecon",
                    "git clone https://github.com/mschwager/fierce",
                    "apt update && apt install -y dnsenum"
                ]
            },
            {
                "id": "monitoring_phase1",
                "name": "Monitoring Tools Phase 1",
                "description": "tcpdump, ettercap, driftnet",
                "tools": ["tcpdump", "ettercap", "driftnet"],
                "commands": [
                    "apt update && apt install -y tcpdump",
                    "apt install -y ettercap-common ettercap-graphical",
                    "apt install -y driftnet"
                ]
            },
            {
                "id": "enum_phase2",
                "name": "theHarvester",
                "description": "theHarvester email/domain OSINT tool",
                "tools": ["theharvester"],
                "commands": [
                    "git clone https://github.com/laramies/theHarvester",
                    "cd theHarvester && pip install -r requirements.txt"
                ]
            },
            {
                "id": "monitoring_phase2",
                "name": "Wireshark",
                "description": "Network protocol analyzer",
                "tools": ["wireshark"],
                "commands": [
                    "apt install -y wireshark"
                ]
            },
            {
                "id": "post_exploit_phase1",
                "name": "Post-exploit Tools Phase 1",
                "description": "Empire and Covenant",
                "tools": ["empire", "covenant"],
                "commands": [
                    "git clone https://github.com/EmpireProject/Empire",
                    "git clone https://github.com/cobbr/Covenant"
                ]
            }
        ]

        # Trouver la prochaine phase non complétée
        for phase in phases:
            if phase["id"] not in self.status["completed_phases"] and phase["id"] not in self.status["failed_phases"]:
                return phase

        return {}

    def execute_phase_background(self, phase: Dict[str, Any]) -> bool:
        """Exécute une phase en arrière-plan"""
        try:
            logger.info(f"Démarrage de la phase: {phase['name']}")

            # Créer un script temporaire pour la phase
            script_content = f"""#!/bin/bash
echo "=== PHASE: {phase['name']} ==="
echo "Description: {phase['description']}"
echo "Tools: {', '.join(phase['tools'])}"
echo ""

set -e  # Arrêter en cas d'erreur

"""

            for cmd in phase["commands"]:
                script_content += f"""
echo "Exécution: {cmd}"
{cmd}
echo "✓ Commande réussie"
"""

            script_content += f"""
echo ""
echo "=== PHASE {phase['name']} TERMINÉE ==="
echo "Outils installés: {', '.join(phase['tools'])}"
"""

            # Écrire et exécuter le script
            script_path = self.base_dir / f"kali_phase_{phase['id']}.sh"
            with open(script_path, 'w') as f:
                f.write(script_content)

            os.chmod(script_path, 0o755)

            # Lancer en arrière-plan
            logger.info(f"Lancement en arrière-plan: {script_path}")
            process = subprocess.Popen(
                [str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.base_dir)
            )

            # Marquer comme en cours
            self.status["current_phase"] = phase["id"]
            self._save_status()

            return True

        except Exception as e:
            logger.error(f"Erreur lors du lancement de la phase {phase['id']}: {e}")
            self.status["failed_phases"].append(phase["id"])
            self._save_status()
            return False

    def check_phase_completion(self) -> Dict[str, Any]:
        """Vérifie si la phase actuelle est terminée"""
        current_phase = self.status.get("current_phase")
        if not current_phase:
            return {"status": "idle", "message": "Aucune phase en cours"}

        # Vérifier si le script existe encore (phase terminée)
        script_path = self.base_dir / f"kali_phase_{current_phase}.sh"
        if not script_path.exists():
            # Phase terminée avec succès
            self.status["completed_phases"].append(current_phase)
            self.status["current_phase"] = None
            self._save_status()

            phase_info = self._get_phase_info(current_phase)
            return {
                "status": "completed",
                "phase": current_phase,
                "message": f"Phase {phase_info['name']} terminée avec succès"
            }

        # Vérifier si le processus tourne encore
        try:
            result = subprocess.run(
                ["pgrep", "-f", f"kali_phase_{current_phase}"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return {
                    "status": "running",
                    "phase": current_phase,
                    "message": f"Phase {current_phase} en cours d'exécution"
                }
            else:
                # Processus terminé, vérifier le script
                if script_path.exists():
                    # Phase peut-être terminée ou échouée
                    return {
                        "status": "unknown",
                        "phase": current_phase,
                        "message": f"Phase {current_phase} - statut inconnu"
                    }
        except:
            pass

        return {"status": "idle", "message": "Statut indéterminé"}

    def _get_phase_info(self, phase_id: str) -> Dict[str, Any]:
        """Récupère les informations d'une phase"""
        phases_info = {
            "enum_phase1": {"name": "Enumeration Tools Phase 1", "tools": ["dnsrecon", "fierce", "dnsenum"]},
            "monitoring_phase1": {"name": "Monitoring Tools Phase 1", "tools": ["tcpdump", "ettercap", "driftnet"]},
            "enum_phase2": {"name": "theHarvester", "tools": ["theharvester"]},
            "monitoring_phase2": {"name": "Wireshark", "tools": ["wireshark"]},
            "post_exploit_phase1": {"name": "Post-exploit Tools Phase 1", "tools": ["empire", "covenant"]}
        }
        return phases_info.get(phase_id, {"name": phase_id, "tools": []})

    def get_status_report(self) -> Dict[str, Any]:
        """Rapport complet du statut d'implémentation"""
        next_phase = self.get_next_phase()
        current_status = self.check_phase_completion()

        return {
            "current_phase": self.status.get("current_phase"),
            "completed_phases": self.status["completed_phases"],
            "failed_phases": self.status["failed_phases"],
            "next_phase": next_phase["id"] if next_phase else None,
            "next_phase_name": next_phase["name"] if next_phase else None,
            "current_status": current_status,
            "total_completed": len(self.status["completed_phases"]),
            "total_failed": len(self.status["failed_phases"]),
            "last_updated": self.status.get("last_updated")
        }

    def start_next_phase_background(self) -> Dict[str, Any]:
        """Démarre la prochaine phase en arrière-plan"""
        # Vérifier d'abord le statut actuel
        current_status = self.check_phase_completion()
        if current_status["status"] == "running":
            return {
                "success": False,
                "message": f"Une phase est déjà en cours: {current_status['phase']}"
            }

        # Obtenir la prochaine phase
        next_phase = self.get_next_phase()
        if not next_phase:
            return {
                "success": False,
                "message": "Toutes les phases sont terminées ou ont échoué"
            }

        # Lancer la phase
        success = self.execute_phase_background(next_phase)
        if success:
            return {
                "success": True,
                "phase": next_phase["id"],
                "message": f"Phase {next_phase['name']} lancée en arrière-plan"
            }
        else:
            return {
                "success": False,
                "message": f"Échec du lancement de la phase {next_phase['id']}"
            }

# Fonction principale
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Kali Tools Implementation Manager")
    parser.add_argument("action", choices=["status", "start", "check", "next"],
                       help="Action à effectuer")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Mode verbose")

    args = parser.parse_args()

    manager = KaliImplementationManager()

    if args.action == "status":
        report = manager.get_status_report()
        print("=== KALI IMPLEMENTATION STATUS ===")
        print(f"Phases terminées: {report['total_completed']}")
        print(f"Phases échouées: {report['total_failed']}")
        print(f"Phase actuelle: {report['current_phase'] or 'Aucune'}")
        print(f"Prochaine phase: {report['next_phase_name'] or 'Aucune'}")
        print(f"Statut actuel: {report['current_status']['status']}")

    elif args.action == "start":
        result = manager.start_next_phase_background()
        if result["success"]:
            print(f"✅ {result['message']}")
            print("Le travail continue en arrière-plan. Vous pouvez travailler sur autre chose.")
        else:
            print(f"❌ {result['message']}")

    elif args.action == "check":
        status = manager.check_phase_completion()
        print(f"Statut: {status['status']}")
        print(f"Message: {status['message']}")

    elif args.action == "next":
        next_phase = manager.get_next_phase()
        if next_phase:
            print(f"Prochaine phase: {next_phase['id']}")
            print(f"Nom: {next_phase['name']}")
            print(f"Description: {next_phase['description']}")
            print(f"Outils: {', '.join(next_phase['tools'])}")
        else:
            print("Aucune phase suivante disponible")

if __name__ == "__main__":
    main()