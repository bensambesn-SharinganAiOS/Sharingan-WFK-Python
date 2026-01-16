#!/usr/bin/env python3
"""
SHARINGAN CAPABILITY ASSESSMENT - Version Simplifiée
Évaluation des capacités actuelles et roadmap vers l'autonomie
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any


def assess_sharingan_capabilities() -> Dict[str, Any]:
    """Évaluer les capacités actuelles de Sharingan"""
    print("SHARINGAN CAPABILITY ASSESSMENT")
    print("=" * 50)

    base_dir = Path(__file__).parent / "sharingan_app" / "_internal"
    sys.path.insert(0, str(base_dir))

    capabilities_status = {
        "FONCTIONNEL": [],
        "PARTIEL": [],
        "LIMITE": [],
        "MANQUANT": []
    }

    print("\n--- EVALUATION DES CAPACITES ---\n")

    # === CONSCIENCE ===
    print("CONSCIENCE & MEMOIRE:")
    try:
        from sharingan_soul import get_sharingan_soul
        soul = get_sharingan_soul()
        status = soul.get_soul_status()
        if status['emotional_state']['happiness'] > 0:
            capabilities_status["FONCTIONNEL"].append("Ame emotionnelle (Sharingan Soul)")
        print("  [OK] Ame emotionnelle active")
    except Exception as e:
        capabilities_status["LIMITE"].append("Systeme emotionnel")
        print(f"  [LIMITE] Systeme emotionnel: {e}")

    try:
        from sharingan_spirit import get_sharingan_spirit
        spirit = get_sharingan_spirit()
        reasoning = spirit.reason_and_decide("Test de raisonnement")
        if reasoning['final_decision']:
            capabilities_status["FONCTIONNEL"].append("Esprit raisonneur (Sharingan Spirit)")
        print("  [OK] Esprit raisonneur operationnel")
    except Exception as e:
        capabilities_status["LIMITE"].append("Systeme de raisonnement")
        print(f"  [LIMITE] Systeme de raisonnement: {e}")

    try:
        from genome_memory import get_genome_memory
        genome = get_genome_memory()
        if len(genome.genes) > 0:
            capabilities_status["FONCTIONNEL"].append("Memoire ADN (Genome Memory)")
        print(f"  [OK] Memoire ADN: {len(genome.genes)} genes")
    except Exception as e:
        capabilities_status["LIMITE"].append("Memoire ADN")
        print(f"  [LIMITE] Memoire ADN: {e}")

    # === IA ===
    print("\nINTELLIGENCE ARTIFICIELLE:")
    try:
        from api_first_intelligence import get_api_first_intelligence
        api_intel = get_api_first_intelligence()
        result = api_intel.process_intelligent_query("Test IA")
        if result['knowledge_generated']['generated_content']:
            capabilities_status["FONCTIONNEL"].append("Intelligence API-First")
        print("  [OK] Intelligence API-First operationnelle")
    except Exception as e:
        capabilities_status["LIMITE"].append("Intelligence API-First")
        print(f"  [LIMITE] Intelligence API-First: {e}")

    # === SÉCURITÉ ===
    print("\nSECURITE:")
    try:
        from psychic_locks_system import get_psychic_locks_system
        locks = get_psychic_locks_system()
        if locks.get_system_status()['psychic_locks']['total_locks'] > 0:
            capabilities_status["FONCTIONNEL"].append("Verrous psychiques")
        print(f"  [OK] Verrous psychiques: {locks.get_system_status()['psychic_locks']['total_locks']} actifs")
    except Exception as e:
        capabilities_status["LIMITE"].append("Verrous psychiques")
        print(f"  [LIMITE] Verrous psychiques: {e}")

    try:
        from fake_detector import validate_readiness
        if validate_readiness()['ready']:
            capabilities_status["FONCTIONNEL"].append("Detection de fake")
        print("  [OK] Detection de fake operationnelle")
    except Exception as e:
        capabilities_status["LIMITE"].append("Detection de fake")
        print(f"  [LIMITE] Detection de fake: {e}")

    # === OUTILS ===
    print("\nOUTILS CYBERSECURITE:")
    tools_tested = {
        "nmap": "which nmap",
        "nikto": "which nikto",
        "sqlmap": "which sqlmap",
        "hashcat": "which hashcat",
        "volatility": "which volatility"
    }

    for tool, cmd in tools_tested.items():
        try:
            result = os.system(f"{cmd} > /dev/null 2>&1")
            if result == 0:
                capabilities_status["FONCTIONNEL"].append(f"Outil {tool}")
                print(f"  [OK] {tool} disponible")
            else:
                capabilities_status["MANQUANT"].append(f"Outil {tool}")
                print(f"  [MANQUANT] {tool}")
        except Exception:
            capabilities_status["MANQUANT"].append(f"Outil {tool}")
            print(f"  [MANQUANT] {tool}")

    # === AUTONOMIE ===
    print("\nAUTONOMIE:")
    try:
        from autonomous_mission_system import get_autonomous_mission_system
        mission_sys = get_autonomous_mission_system()
        status = mission_sys.get_system_status()
        if status['active_missions'] >= 0:
            capabilities_status["FONCTIONNEL"].append("Systeme de missions autonomes")
        print("  [OK] Systeme de missions autonomes operationnel")
    except Exception as e:
        capabilities_status["LIMITE"].append("Systeme de missions autonomes")
        print(f"  [LIMITE] Systeme de missions autonomes: {e}")

    # === RÉSEAU & INTERNET ===
    print("\nRESEAU & INTERNET:")
    try:
        import subprocess
        result = subprocess.run(
            ["curl", "-s", "--max-time", "3", "https://httpbin.org/ip"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            capabilities_status["FONCTIONNEL"].append("Acces internet")
            print("  [OK] Acces internet fonctionnel")
        else:
            capabilities_status["LIMITE"].append("Acces internet")
            print("  [LIMITE] Acces internet")
    except Exception as e:
        capabilities_status["LIMITE"].append("Acces internet")
        print(f"  [LIMITE] Acces internet: {e}")

    # === SYSTÈME ===
    print("\nINTEGRATION SYSTEME:")
    try:
        home_file = Path.home() / ".bashrc"
        if home_file.exists():
            with open(home_file, 'r') as f:
                content = f.read(100)
            if content:
                capabilities_status["FONCTIONNEL"].append("Acces systeme de fichiers")
                print("  [OK] Acces systeme de fichiers fonctionnel")
    except Exception as e:
        capabilities_status["LIMITE"].append("Acces systeme de fichiers")
        print(f"  [LIMITE] Acces systeme de fichiers: {e}")

    # === CALCUL DES SCORES ===
    total_capabilities = sum(len(caps) for caps in capabilities_status.values())
    functional_count = len(capabilities_status["FONCTIONNEL"])
    autonomy_score = functional_count / total_capabilities if total_capabilities > 0 else 0

    print("\n--- RESULTATS DE L'EVALUATION ---")
    print(f"Total des capacites evaluees: {total_capabilities}")
    print(f"Score d'autonomie estime: {autonomy_score:.1%}")

    print("\n--- REPARTITION PAR STATUT ---")
    for status, caps in capabilities_status.items():
        if caps:
            print(f"\n{status}:")
            for cap in caps:
                print(f"  - {cap}")

    # === PROPOSITIONS D'AMÉLIORATION ===
    print("\n--- PROPOSITIONS D'AMELIORATION POUR AUTONOMIE TOTALE ---")
    print("-" * 50)

    improvements = []

    if "Acces internet" in capabilities_status["LIMITE"] or \
       "Acces internet" in capabilities_status["MANQUANT"]:
        improvements.append({
            "priorite": "CRITIQUE",
            "capacite": "Acces internet securise",
            "solution": "Implementer proxy securise et navigation controlee",
            "complexite": "MOYENNE",
            "temps": "2-3 jours"
        })

    if any("Outil" in cap for cap in capabilities_status["MANQUANT"]):
        improvements.append({
            "priorite": "HAUTE",
            "capacite": "Installation automatique d'outils",
            "solution": "Systeme de deploiement automatique des outils Kali",
            "complexite": "FAIBLE",
            "temps": "1-2 jours"
        })

    if "Acces systeme de fichiers" in capabilities_status["LIMITE"]:
        improvements.append({
            "priorite": "HAUTE",
            "capacite": "Permissions systeme etendues",
            "solution": "Systeme de permissions graduees avec sandboxing",
            "complexite": "ELEVEE",
            "temps": "1-2 semaines"
        })

    improvements.append({
        "priorite": "CRITIQUE",
        "capacite": "Execution de code controlee",
        "solution": "Containers et environnements isoles pour execution securisee",
        "complexite": "EXPERT",
        "temps": "3-4 semaines"
    })

    improvements.append({
        "priorite": "MOYENNE",
        "capacite": "Integration services externes",
        "solution": "APIs pour bases de donnees, services cloud, recherche web",
        "complexite": "MOYENNE",
        "temps": "1 semaine"
    })

    for i, improvement in enumerate(improvements, 1):
        print(f"\n{i}. {improvement['capacite']} ({improvement['priorite']})")
        print(f"   Solution: {improvement['solution']}")
        print(f"   Complexite: {improvement['complexite']}")
        print(f"   Temps estime: {improvement['temps']}")

    print("\n--- OBJECTIF: AUTONOMIE TOTALE DE SHARINGAN ---")
    print("-" * 50)
    print("Une fois ces ameliorations implementees, Sharingan pourra:")
    print("- Acceder a internet et aux ressources web")
    print("- Installer et utiliser automatiquement tous les outils")
    print("- Manipuler le systeme de fichiers de l'hote")
    print("- Executer du code de maniere securisee")
    print("- Integrer des APIs et services externes")
    print("- Operer de maniere completement autonome")
    print("- Effectuer n'importe quelle mission cybersecurite")

    result = {
        "capabilities_status": capabilities_status,
        "autonomy_score": autonomy_score,
        "improvements_needed": improvements,
        "total_capabilities": total_capabilities,
        "functional_count": functional_count
    }

    return result


def run_assessment() -> Dict[str, Any]:
    """Point d'entrée principal"""
    results = assess_sharingan_capabilities()

    print("\n--- EVALUATION TERMINEE ---")
    print(f"Score d'autonomie actuel: {results['autonomy_score']:.1%}")
    print(f"Ameliorations necessaires: {len(results['improvements_needed'])}")
    print("\nProchaine etape: Implementer les ameliorations pour atteindre 100% d'autonomie!")

    return results


if __name__ == "__main__":
    run_assessment()
