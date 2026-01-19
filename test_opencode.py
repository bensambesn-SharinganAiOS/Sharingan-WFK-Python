#!/usr/bin/env python3
"""
Test script for OpenCode free AI provider
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from opencode_provider import get_opencode_provider

def test_opencode_provider():
    print("🔧 Test du provider OpenCode (APIs gratuites)")
    print("=" * 50)

    try:
        # Créer le provider OpenCode
        opencode = get_opencode_provider()

        print(f"✅ Provider créé")
        print(f"   Disponible: {opencode.is_available()}")

        if opencode.is_available():
            print("🎯 Test de génération avec modèles gratuits...")

            # Test de génération
            test_message = "Bonjour, peux-tu me dire quelle est la capitale de la France ?"
            response = opencode.chat(test_message)

            if response.get("status") == "success":
                print("✅ Réponse reçue :")
                print(f"   Modèle utilisé: {response.get('model', 'unknown')}")
                print(f"   Réponse: {response['response'][:200]}...")
                print("🎉 Provider OpenCode fonctionnel !")
            else:
                print(f"❌ Erreur: {response.get('error', 'Erreur inconnue')}")

            # Afficher les modèles disponibles
            print(f"\n📋 Modèles gratuits disponibles:")
            models = opencode.get_available_models()
            for i, model in enumerate(models[:8], 1):  # Afficher les 8 premiers
                print(f"   {i}. {model}")

        else:
            print("❌ OpenCode CLI non disponible ou modèles gratuits non accessibles")

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_opencode_provider()