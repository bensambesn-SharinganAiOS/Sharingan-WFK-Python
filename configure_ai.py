#!/usr/bin/env python3
"""
Configuration script for Sharingan AI providers
Configure Gemini API key and test connection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_fallback_config import ai_fallback_config
from gemini_provider import get_gemini_provider

def main():
    print("🔧 Configuration des APIs IA pour Sharingan")
    print("=" * 50)

    # Configuration Gemini
    print("\n🤖 Configuration Gemini (Google AI)")
    print("Obtenez une clé API sur: https://makersuite.google.com/app/apikey")

    api_key = input("Entrez votre clé API Gemini: ").strip()

    if not api_key:
        print("❌ Aucune clé API fournie.")
        return

    # Tester la clé API
    print("\n🔍 Test de la connexion à Gemini...")
    try:
        gemini = get_gemini_provider(api_key)
        if gemini.is_available():
            print("✅ Connexion Gemini réussie!")

            # Activer dans la configuration
            ai_fallback_config.enable_provider("gemini", api_key)
            print("✅ Gemini activé dans la configuration")

            # Test rapide
            print("\n🧪 Test rapide de génération...")
            test_response = gemini.chat("Bonjour, tu es prêt à aider ?")
            if test_response.get("status") == "success":
                print(f"✅ Réponse: {test_response['response'][:100]}...")
            else:
                print(f"⚠️ Test échoué: {test_response.get('error', 'Erreur inconnue')}")

        else:
            print("❌ Échec de connexion à Gemini. Vérifiez votre clé API.")

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

    print("\n📋 État des providers:")
    enabled = ai_fallback_config.get_enabled_providers()
    for provider, config in enabled.items():
        print(f"  ✅ {provider}: {config.get('model', 'unknown')}")

    print(f"\n🔄 Chaîne de fallback: {ai_fallback_config.get_fallback_chain()}")

    print("\n🎉 Configuration terminée!")
    print("Vous pouvez maintenant utiliser: python3 sharingan_os.py ai \"votre question\"")

if __name__ == "__main__":
    main()