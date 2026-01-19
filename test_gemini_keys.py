#!/usr/bin/env python3
"""
Test script for Gemini API key rotation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gemini_provider import get_gemini_provider

def test_gemini_keys():
    print("🔧 Test des clés API Gemini avec rotation")
    print("=" * 50)

    # Clés API fournies
    api_keys = [
        "AIzaSyAQ5Jq6doHAt3untxi3zD95n_TBoZft7wQ",  # adamabenousmanesambe@gmail.com
        "AIzaSyA2vUDIH8m80nxYCOq15qOE5L61mJABPkU",  # bensambe.sn@gmail.com
        "AIzaSyAtMBJMWn2saI2Yo7ljPyJOMEq0eaVFY8E",  # bensambe.org@gmail.com
        "AIzaSyBLJmwuYDFay2kbRx3xwWz1i3pSXR11LWg"   # madamesambe@gmail.com
    ]

    print(f"📋 Test de {len(api_keys)} clés API...")

    try:
        # Créer le provider avec toutes les clés
        gemini = get_gemini_provider(api_keys)

        # Afficher le statut
        status = gemini.get_status()
        print(f"✅ Provider créé: {status}")

        if gemini.is_available():
            print("🎯 Test de génération avec rotation automatique...")

            # Test de génération
            test_message = "Bonjour Gemini, peux-tu me dire quelle est la capitale de la France ?"
            response = gemini.chat(test_message)

            if response.get("status") == "success":
                print("✅ Réponse reçue :")
                print(f"   Clé utilisée: {response.get('key_used', 'N/A')}")
                print(f"   Réponse: {response['response'][:150]}...")
                print("🎉 Système de rotation fonctionnel !")
            else:
                print(f"❌ Erreur: {response.get('error', 'Erreur inconnue')}")
        else:
            print("❌ Aucune clé API ne fonctionne")

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

    print("\n📋 Clés testées:")
    for i, key in enumerate(api_keys, 1):
        masked_key = key[:20] + "..." + key[-10:] if len(key) > 30 else key
        print(f"   {i}. {masked_key}")

if __name__ == "__main__":
    test_gemini_keys()