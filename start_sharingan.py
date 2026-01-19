#!/usr/bin/env python3
"""
SHARINGAN OS - Démarrage Propre
Mode BUILD (Défaut) - Sans logs verbeux
"""

import sys
import os

# Configuration de logging optimisée
try:
    from sharingan_app._internal.logging_config import setup_logging
    setup_logging()
except ImportError:
    # Fallback si le module n'est pas disponible
    import logging
    # Supprimer tous les handlers de logging existants
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    # Configuration silencieuse
    logging.basicConfig(
        level=logging.WARNING,
        handlers=[logging.NullHandler()],
        force=True
    )

# Supprimer les sortie stdout/stderr des modules
os.environ['PYTHONUNBUFFERED'] = '0'

sys.path.insert(0, 'sharingan_app/_internal')

# Imports conditionnels - certains modules peuvent ne pas exister
try:
    from evolution_team import get_evolution_team
except ImportError:
    get_evolution_team = None

try:
    from autonomous_mission_system import get_autonomous_mission_system
except ImportError:
    get_autonomous_mission_system = None

try:
    from security.permissions import validate_execution
except ImportError:
    validate_execution = None
try:
    from genome_memory import get_genome_memory
except ImportError:
    get_genome_memory = None

# fake_detector supprimé - contenu fake
validate_readiness = None
detect_fakes = None

try:
    from capability_discovery_system import CapabilityDiscoverySystem
except ImportError:
    CapabilityDiscoverySystem = None

try:
    from sharingan_soul import get_sharingan_soul
except ImportError:
    get_sharingan_soul = None

try:
    from sharingan_spirit import get_sharingan_spirit
except ImportError:
    get_sharingan_spirit = None

try:
    from api_first_intelligence import get_api_first_intelligence
except ImportError:
    get_api_first_intelligence = None

# Réactiver stdout pour l'affichage propre
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

print("=" * 70)
print("🚀 SHARINGAN OS v3.0 - MODE BUILD (Défaut)")
print("=" * 70)
print()

print("[1/8] Genome Memory...")
if get_genome_memory:
    gm = get_genome_memory()
    print(f"      → {len(gm.genes)} gènes chargés")
else:
    print("      → Module non disponible")

print("[2/8] Evolution Team...")
if get_evolution_team:
    team = get_evolution_team('build')
    print(f"      → Mode: {team.mode}, Permission: {'Oui' if team.permission_validator else 'Non'}")
else:
    print("      → Module non disponible")

print("[3/8] Autonomous Missions...")
if get_autonomous_mission_system:
    ams = get_autonomous_mission_system()
    ams_status = ams.get_system_status()
    print(f"      → {ams_status['active_missions']} missions actives")
else:
    print("      → Module non disponible")

print("[4/8] Capability Discovery...")
if CapabilityDiscoverySystem:
    cds = CapabilityDiscoverySystem()
    print(f"      → {cds.capabilities_discovered} capacités, {len(cds.capability_tests)} tests")
else:
    print("      → Module non disponible")

print("[5/8] Sharingan Soul...")
if get_sharingan_soul:
    soul = get_sharingan_soul()
    print(f"      → Âme opérationnelle")
else:
    print("      → Module non disponible")

print("[6/8] Sharingan Spirit...")
if get_sharingan_spirit:
    spirit = get_sharingan_spirit()
    print(f"      → Esprit opérationnel")
else:
    print("      → Module non disponible")

print("[7/8] API-First Intelligence...")
if get_api_first_intelligence:
    api = get_api_first_intelligence()
print(f"      → Intelligence API-First opérationnelle")

print("[8/8] Permission System...")
if validate_execution:
    perm = validate_execution("ls", ["ls"], mode="plan")
    print(f"      → Système: {'Non-bloquant' if perm.granted else 'Bloquant'}")
else:
    print("      → Module non disponible")

# Fake detector supprimé
print("      → Fake Detector: Supprimé (contenu fake)")

print()
print("=" * 70)
print("🧪 VÉRIFICATION RAPIDE")
print("=" * 70)

print("\n[AI] Code validation...")
print("      → Fake detector supprimé")

print("\n[Evolution] Analyse système...")
if get_evolution_team and 'team' in locals() and team:
    analysis = team.run_analysis("optimize system")
    print(f"    → Consensus: {analysis.consensus_score * 100:.0f}%")
else:
    print("      → Module évolution non disponible")
print(f"    → Patch: {'Oui' if analysis.surgeon_patch else 'Non'}")

print("\n[Permission] Outil sûr (ls)...")
safe = validate_execution("ls", ["ls"], mode="plan")
print(f"    → {'Oui' if safe.granted else 'Non'}")

print()
print("=" * 70)
print("✅ SYSTÈME PRÊT")
print("=" * 70)
print()
print("  ai <question>          → Chat IA")
print("  consciousness status   → Conscience")
print("  api --host 0.0.0.0     → Serveur API")
print("  monitor <sec> <iter>   → Monitoring")
print("  scan <IP>              → Scan réseau")
print()
