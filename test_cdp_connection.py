#!/usr/bin/env python3
"""
Test script pour vérifier la connexion CDP au navigateur partagé.
Ce script confirme que le navigateur Sharingan est accessible et controllable.
"""
import asyncio
import json
import urllib.request
import websockets


async def test_cdp_connection():
    """Teste la connexion CDP et effectue quelques opérations."""
    
    # 1. Récupérer les cibles CDP
    print("🔍 Récupération des cibles CDP...")
    try:
        with urllib.request.urlopen("http://localhost:9999/json") as response:
            targets = json.loads(response.read())
        
        if not targets:
            print("❌ Aucune cible trouvée")
            return False
            
        target = targets[0]  # Premier onglet
        ws_url = target["webSocketDebuggerUrl"]
        title = target.get("title", "Sans titre")
        url = target.get("url", "URL inconnue")
        
        print(f"✅ Onglet trouvé: {title}")
        print(f"   URL: {url}")
        print(f"   WebSocket: {ws_url}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des cibles: {e}")
        return False
    
    # 2. Se connecter via WebSocket et envoyer des commandes
    print("\n🌐 Connexion WebSocket...")
    try:
        async with websockets.connect(ws_url) as ws:
            
            # Fonction pour envoyer une commande et attendre la réponse
            async def send_command(method: str, params: dict = None, msg_id: int = 1):
                msg = {"id": msg_id, "method": method}
                if params:
                    msg["params"] = params
                await ws.send(json.dumps(msg))
                
                # Attendre la réponse
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                return json.loads(response)
            
            # Test 1: Obtenir le titre de la page
            print("\n📄 Test 1: Obtenir le titre de la page...")
            result = await send_command("Runtime.evaluate", {
                "expression": "document.title",
                "returnByValue": True
            })
            title = result.get("result", {}).get("result", {}).get("value", "Unknown")
            print(f"   Titre: {title}")
            
            # Test 2: Obtenir l'URL actuelle
            print("\n🔗 Test 2: Obtenir l'URL actuelle...")
            result = await send_command("Runtime.evaluate", {
                "expression": "window.location.href",
                "returnByValue": True
            })
            current_url = result.get("result", {}).get("result", {}).get("value", "Unknown")
            print(f"   URL: {current_url}")
            
            # Test 3: Extraire le contenu textuel
            print("\n📝 Test 3: Extraire le contenu textuel...")
            result = await send_command("Runtime.evaluate", {
                "expression": "document.body.innerText.substring(0, 500)",
                "returnByValue": True
            })
            text = result.get("result", {}).get("result", {}).get("value", "")
            print(f"   Extrait: {text[:200]}...")
            
            # Test 4: Faire défiler la page
            print("\n⬇️ Test 4: Défiler la page...")
            await send_command("Runtime.evaluate", {
                "expression": "window.scrollBy(0, 500)"
            })
            print("   Page défilée de 500px")
            
            # Test 5: Naviguer vers une nouvelle URL
            print("\n🚀 Test 5: Navigation vers Wikipedia...")
            await send_command("Page.navigate", {
                "url": "https://fr.wikipedia.org/wiki/Intelligence_artificielle"
            })
            await asyncio.sleep(2)  # Attendre le chargement
            
            # Vérifier la nouvelle URL
            result = await send_command("Runtime.evaluate", {
                "expression": "window.location.href",
                "returnByValue": True
            })
            new_url = result.get("result", {}).get("result", {}).get("value", "Unknown")
            print(f"   Nouvelle URL: {new_url}")
            
            # Test 6: Revenir à Google
            print("\n🔙 Test 6: Retour à Google...")
            await send_command("Page.navigate", {"url": "https://www.google.com"})
            await asyncio.sleep(2)
            
            result = await send_command("Runtime.evaluate", {
                "expression": "window.location.href",
                "returnByValue": True
            })
            back_url = result.get("result", {}).get("result", {}).get("value", "Unknown")
            print(f"   URL de retour: {back_url}")
            
            print("\n" + "="*50)
            print("✅ TOUS LES TESTS CDP RÉUSSIS !")
            print("="*50)
            print(f"\n📋 Résumé:")
            print(f"   - Navigateur: ACTIF sur port 9999")
            print(f"   - WebSocket: {ws_url}")
            print(f"   - Titre actuel: {title}")
            print(f"   - Connexion CDP: FONCTIONNELLE")
            print(f"\n🌐 Le navigateur est prêt pour Sharingan OS !")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur WebSocket: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*60)
    print("🧪 TEST DE CONNEXION CDP - SHARINGAN BROWSER")
    print("="*60)
    
    success = asyncio.run(test_cdp_connection())
    
    if not success:
        print("\n⚠️ Le navigateur n'est peut-être pas démarré.")
        print("   Pour le démarrer: google-chrome --remote-debugging-port=9999 --no-sandbox &")
    
    exit(0 if success else 1)
