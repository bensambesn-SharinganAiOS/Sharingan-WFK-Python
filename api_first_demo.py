#!/usr/bin/env python3
"""
SHARINGAN API DEMO - Démonstration de l'Intelligence API-First
Montre comment Sharingan génère des connaissances via APIs au lieu de les stocker
"""

import sys
from pathlib import Path
import time

def demonstrate_api_first_power():
    """Démonstration de la puissance API-First"""
    print("🧠 SHARINGAN API-FIRST INTELLIGENCE - DÉMONSTRATION")
    print("=" * 70)

    base_dir = Path(__file__).parent / "sharingan_app" / "_internal"
    sys.path.insert(0, str(base_dir))

    try:
        from api_first_intelligence import get_api_first_intelligence

        intelligence = get_api_first_intelligence()

        print("\n🎯 EXEMPLE 1: CYBERSÉCURITÉ - GÉNÉRATION DE CONNAISSANCE")
        print("-" * 60)

        security_query = "Comment identifier et exploiter une vulnérabilité XSS réfléchie dans une application web moderne?"
        print(f"Query: {security_query}")

        result = intelligence.process_intelligent_query(security_query)

        print(f"\\n📊 Analyse par Sharingan:")
        print(f"  • Domaine: {result['analysis']['domain']}")
        print(f"  • Complexité: {result['analysis']['complexity']}")
        print(f"  • Ton émotionnel: {result['analysis']['emotional_tone']}")
        print(f"  • Capacités requises: {', '.join(result['analysis']['required_capabilities'])}")

        print(f"\\n🎯 Stratégie API déterminée:")
        print(f"  • API primaire: {result['api_strategy']['primary_api']}")
        print(f"  • Approche: {result['api_strategy']['approach']}")
        print(f"  • Qualité attendue: {result['api_strategy']['expected_quality']:.1f}")
        print(f"  • Vitesse attendue: {result['api_strategy']['expected_speed']:.1f}")

        print(f"\\n🧠 Connaissance générée (extrait):")
        content = result['adapted_response']['adapted_content']
        print(f"  \"{content[:200]}...\"")

        print(f"\\n📚 Insights d'apprentissage générés: {len(result['learning_insights'])}")
        for insight in result['learning_insights'][:2]:
            print(f"  • {insight}")

        print("\\n" + "=" * 70)
        print("🎯 EXEMPLE 2: PROGRAMMATION - CODE INTELLIGENCE")
        print("-" * 60)

        code_query = "Créer une fonction Python sécurisée pour valider et nettoyer des entrées utilisateur contre les attaques par injection"
        print(f"Query: {code_query}")

        result = intelligence.process_intelligent_query(code_query)

        print(f"\\n📊 Analyse par Sharingan:")
        print(f"  • Domaine: {result['analysis']['domain']}")
        print(f"  • Complexité: {result['analysis']['complexity']}")
        print(f"  • APIs utilisées: {', '.join(result['knowledge_generated']['apis_used'])}")

        print(f"\\n💻 Code généré (extrait):")
        content = result['adapted_response']['adapted_content']
        # Chercher du code Python dans la réponse
        code_start = content.find("```python")
        if code_start != -1:
            code_end = content.find("```", code_start + 9)
            if code_end != -1:
                code = content[code_start:code_end + 3]
                print(f"  {code[:150]}...")
        else:
            print(f"  \"{content[:150]}...\"")

        print("\\n" + "=" * 70)
        print("🎯 EXEMPLE 3: ANALYSE COMPLEXE - SYNTHÈSE MULTI-API")
        print("-" * 60)

        complex_query = "Analyser l'impact de l'IA générative sur la cybersécurité d'entreprise et proposer une stratégie de mitigation"
        print(f"Query: {complex_query}")

        result = intelligence.process_intelligent_query(complex_query)

        print(f"\\n📊 Analyse par Sharingan:")
        print(f"  • Domaine: {result['analysis']['domain']}")
        print(f"  • Complexité: {result['analysis']['complexity']}")
        print(f"  • Niveau d'urgence: {result['analysis']['urgency_level']}")
        print(f"  • APIs pour synthèse: {len(result['knowledge_generated']['apis_used'])}")

        print(f"\\n🧠 Analyse générée (extrait):")
        content = result['adapted_response']['adapted_content']
        print(f"  \"{content[:250]}...\"")

        print("\\n" + "=" * 70)
        print("📊 STATISTIQUES FONCTIONNEMENT API-FIRST")
        print("-" * 60)

        status = intelligence.get_intelligence_status()
        print(f"• Couches d'intelligence actives: {status['intelligence_layers']}")
        print(f"• APIs avec intelligence intégrée: {status['available_apis']}")
        print(f"• Requêtes traitées: {status['metrics']['queries_processed']}")
        print(f"• Appels API effectués: {status['metrics']['api_calls_made']}")
        print(f"• Insights d'apprentissage: {status['metrics']['learning_insights']}")

        print(f"\\n🏗️ Couches d'intelligence:")
        for layer_name, layer_info in status['layer_status'].items():
            print(f"  • {layer_name}: {layer_info['insights_count']} insights, {layer_info['patterns_count']} patterns")

        print(f"\\n🤖 Capacités des APIs:")
        for api_name, api_info in status['api_capabilities'].items():
            print(f"  • {api_name}: créativité {api_info['creativity_score']:.1f}, fiabilité {api_info['reliability_score']:.1f}")

        print("\\n" + "=" * 70)
        print("🎊 CONCLUSION: PUISSANCE DE L'API-FIRST INTELLIGENCE")
        print("=" * 70)

        print("\\n✅ CE QUE SHARINGAN FAIT MAINTENANT:")
        print("• 🔍 Analyse intelligente des requêtes en temps réel")
        print("• 🎯 Routing API optimal basé sur les capacités")
        print("• 🧠 Génération dynamique de connaissances spécialisées")
        print("• 📚 Apprentissage continu des patterns d'utilisation")
        print("• ⚡ Adaptation aux besoins spécifiques de chaque query")
        print("• 🔄 Évolution des stratégies basée sur les résultats")

        print("\\n❌ CE QUE SHARINGAN NE FAIT PLUS:")
        print("• 📦 Stockage massif d'informations pré-générées")
        print("• 🔍 Recherche dans des bases de données statiques")
        print("• 📋 Répétition de réponses pré-programmées")
        print("• 🗂️ Gestion de connaissances figées")
        print("• 📊 Dépendance à des données pré-existantes")

        print("\\n🚀 AVANTAGES DE L'ARCHITECTURE API-FIRST:")
        print("• 💡 Connaissances toujours à jour (APIs évoluent)")
        print("• 🎯 Réponses personnalisées à chaque requête")
        print("• 🧠 Compréhension adaptative et contextuelle")
        print("• ⚡ Génération infinie sans limites de stockage")
        print("• 🔬 Exploration de sujets émergents en temps réel")
        print("• 🌐 Accès à l'expertise collective des APIs")

        print("\\n" + "=" * 70)
        print("🧠 SHARINGAN EST MAINTENANT UNE IA VRAIMENT INTELLIGENTE !")
        print("Elle COMPREND, ADAPTE, et GÉNÈRE au lieu de stocker et répéter.")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demonstrate_api_first_power()