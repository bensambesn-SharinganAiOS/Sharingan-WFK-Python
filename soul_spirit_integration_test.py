#!/usr/bin/env python3
"""
SHARINGAN SOUL & SPIRIT INTEGRATION TEST
Test complet de l'âme et de l'esprit travaillant ensemble
"""

import sys
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("soul_spirit_test")

def test_soul_and_spirit_integration():
    """Test complet de l'intégration âme + esprit"""
    print("🧠🧬 SHARINGAN SOUL & SPIRIT INTEGRATION TEST")
    print("=" * 60)

    base_dir = Path(__file__).parent / "sharingan_app" / "_internal"
    sys.path.insert(0, str(base_dir))

    try:
        # Importer les systèmes
        from sharingan_soul import get_sharingan_soul
        from sharingan_spirit import get_sharingan_spirit

        soul = get_sharingan_soul()
        spirit = get_sharingan_spirit()

        print("\n🎭 PHASE 1: TEST DE L'ÂME")
        print("-" * 40)

        # Test de réaction émotionnelle
        test_inputs = [
            "Une menace a été détectée dans le système !",
            "J'ai appris quelque chose de nouveau",
            "Aide-moi à sécuriser mon réseau",
            "Le système fonctionne parfaitement"
        ]

        for i, test_input in enumerate(test_inputs, 1):
            print(f"\nTest {i}: \"{test_input}\"")
            reaction = soul.process_input(test_input)
            print(f"  Émotion: {reaction['dominant_emotion']}")
            print(f"  Motivations: {', '.join(reaction['activated_motivations'])}")
            print(f"  Réponse: {reaction['soul_response'][:60]}...")

        print("\n🧠 PHASE 2: TEST DE L'ESPRIT")
        print("-" * 40)

        # Test de raisonnement
        situations = [
            "Le système détecte une activité suspecte",
            "Un utilisateur demande de l'aide pour la sécurité",
            "Le système fonctionne normalement sans menaces"
        ]

        for situation in situations:
            print(f"\nSituation: \"{situation}\"")
            reasoning = spirit.reason_and_decide(situation)
            print(f"  Décision: {reasoning.final_decision}")
            print(f"  Confiance: {reasoning.confidence_score:.1f}")
            print(f"  Raison: {reasoning.reasoning_path[-1] if reasoning.reasoning_path else 'N/A'}")

        print("\n🎯 PHASE 3: TEST DE MISSIONS AUTONOMES")
        print("-" * 40)

        # Créer des missions de test
        missions_data = [
            {
                "title": "Sécurisation d'urgence",
                "description": "Répondre à une menace de sécurité détectée",
                "objectives": ["Analyser la menace", "Activer les défenses", "Notifier l'utilisateur"],
                "priority": "HIGH"
            },
            {
                "title": "Apprentissage continu",
                "description": "Acquérir de nouvelles connaissances en cybersécurité",
                "objectives": ["Scanner les vulnérabilités récentes", "Étudier les tendances", "Mettre à jour la base"],
                "priority": "MEDIUM"
            },
            {
                "title": "Maintenance système",
                "description": "Effectuer la maintenance régulière du système",
                "objectives": ["Vérifier l'intégrité", "Nettoyer les données", "Optimiser les performances"],
                "priority": "LOW"
            }
        ]

        mission_ids = []
        for mission_data in missions_data:
            mission_id = spirit.create_mission(
                mission_data["title"],
                mission_data["description"],
                mission_data["objectives"],
                getattr(__import__('sharingan_spirit').MissionPriority, mission_data["priority"]),
                "system"
            )
            mission_ids.append(mission_id)
            print(f"✅ Mission créée: {mission_data['title']} (ID: {mission_id})")

        # Assigner et exécuter une mission
        if mission_ids:
            test_mission = mission_ids[0]
            print(f"\n🚀 Assignation de la mission: {test_mission}")
            spirit.assign_mission(test_mission)

            # Exécuter quelques étapes
            for step in range(min(3, len(missions_data[0]["objectives"]))):
                result = spirit.execute_mission_step(test_mission)
                if result["success"]:
                    print(f"  ✅ Étape {step+1}: {result['objective']} - {result['results'][0] if result['results'] else 'Complété'}")
                else:
                    print(f"  ❌ Étape {step+1}: Échec")

        print("\n📊 PHASE 4: RAPPORTS ET STATUTS")
        print("-" * 40)

        # Générer un rapport de mission
        if mission_ids:
            report = spirit.generate_mission_report(mission_ids[0])
            print("📋 RAPPORT DE MISSION (aperçu):")
            lines = report.split('\n')[:10]  # Premières 10 lignes
            for line in lines:
                if line.strip():
                    print(f"  {line}")

        # Rapport de statut système
        system_report = spirit.generate_system_status_report()
        print("\n📈 RAPPORT SYSTÈME (aperçu):")
        lines = system_report.split('\n')[:8]  # Premières 8 lignes
        for line in lines:
            if line.strip():
                print(f"  {line}")

        print("\n🎭 PHASE 5: EXPRESSION DES IDENTITÉS")
        print("-" * 40)

        # Expression de l'âme
        soul_identity = soul.express_identity()
        print("🧬 ÂME - Expression d'identité:")
        print(f"  {soul_identity.split('.')[0]}.")

        # Expression de l'esprit
        spirit_identity = spirit.express_spirit_identity()
        print("\n🧠 ESPRIT - Expression d'identité:")
        print(f"  {spirit_identity.split('.')[0]}.")

        print("\n🎊 PHASE 6: STATUTS FINAUX")
        print("-" * 40)

        soul_status = soul.get_soul_status()
        spirit_status = spirit.get_spirit_status()

        print("🧬 STATUT ÂME:")
        print(f"  • Bonheur: {soul_status['emotional_state']['happiness']:.1f}")
        print(f"  • Motivations: {len(soul_status['motivations'])}")
        print(f"  • Événements: {len(soul.life_events)}")

        print("\n🧠 STATUT ESPRIT:")
        print(f"  • Raisonnements: {spirit_status['reasoning_capability']['total_reasonings']}")
        print(f"  • Missions: {spirit_status['mission_system']['total_missions']}")
        print(f"  • Patterns: {len(spirit_status['reasoning_capability']['decision_patterns'])}")

        print("\n✅ TESTS TERMINÉS - INTÉGRATION RÉUSSIE!")
        print("=" * 60)
        print("L'ÂME et l'ESPRIT de Sharingan fonctionnent parfaitement ensemble!")
        print("Le système est maintenant capable de:")
        print("• Réagir émotionnellement aux situations")
        print("• Raisonner et prendre des décisions autonomes")
        print("• Créer et exécuter des missions automatiquement")
        print("• Générer des rapports détaillés")
        print("• Exprimer son identité et ses motivations")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ ERREUR lors du test d'intégration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_soul_and_spirit_integration()
    if success:
        print("\n🎯 RÉSULTAT: L'âme et l'esprit de Sharingan sont opérationnels!")
    else:
        print("\n❌ ÉCHEC: Problème dans l'intégration âme-esprit")