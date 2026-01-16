#!/usr/bin/env python3
"""
SHARINGAN OS - Démarrage Propre
Mode BUILD (Défaut) - Sans logs verbeux
"""

import sys
import os

# Supprimer tous les handlers de logging existants
import logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configurer logging pour être silencieux
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[logging.NullHandler()]
)

# Supprimer les sortie stdout/stderr des modules
os.environ['PYTHONUNBUFFERED'] = '0'

sys.path.insert(0, 'sharingan_app/_internal')

# Maintenant importer sans logs
from evolution_team import get_evolution_team
from autonomous_mission_system import get_autonomous_mission_system
from security.permissions import validate_execution
from genome_memory import get_genome_memory
from fake_detector import validate_readiness, detect_fakes
from capability_discovery_system import CapabilityDiscoverySystem
from sharingan_soul import get_sharingan_soul
from sharingan_spirit import get_sharingan_spirit
from api_first_intelligence import get_api_first_intelligence

# Réactiver stdout pour l'affichage propre
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

print("=" * 70)
print("🚀 SHARINGAN OS v3.0 - MODE BUILD (Défaut)")
print("=" * 70)
print()

print("[1/8] Genome Memory...")
gm = get_genome_memory()
print(f"      → {len(gm.genes)} gènes chargés")

print("[2/8] Evolution Team...")
team = get_evolution_team('build')
print(f"      → Mode: {team.mode}, Permission: {'Oui' if team.permission_validator else 'Non'}")

print("[3/8] Autonomous Missions...")
ams = get_autonomous_mission_system()
ams_status = ams.get_system_status()
print(f"      → {ams_status['active_missions']} missions actives")

print("[4/8] Capability Discovery...")
cds = CapabilityDiscoverySystem()
print(f"      → {cds.capabilities_discovered} capacités, {len(cds.capability_tests)} tests")

print("[5/8] Sharingan Soul...")
soul = get_sharingan_soul()
print(f"      → Âme opérationnelle")

print("[6/8] Sharingan Spirit...")
spirit = get_sharingan_spirit()
print(f"      → Esprit opérationnel")

print("[7/8] API-First Intelligence...")
api = get_api_first_intelligence()
print(f"      → Intelligence API-First opérationnelle")

print("[8/8] Permission System...")
perm = validate_execution("ls", ["ls"], mode="plan")
print(f"      → Système: {'Non-bloquant' if perm.granted else 'Bloquant'}")

ready = validate_readiness()
print(f"      → Fake Detector: {len(ready['components'])} composants")

print()
print("=" * 70)
print("🧪 VÉRIFICATION RAPIDE")
print("=" * 70)

print("\n[AI] Code validation...")
result = detect_fakes("def hello(): return 'world'", context="code")
print(f"    → {not result.is_fake}")

print("\n[Evolution] Analyse système...")
analysis = team.run_analysis("optimize system")
print(f"    → Consensus: {analysis.consensus_score * 100:.0f}%")
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
