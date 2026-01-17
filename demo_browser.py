#!/usr/bin/env python3
"""
Démonstration de l'intégration Sharingan Browser
Montre comment Sharingan OS peut contrôler le navigateur via langage naturel
en réutilisant le navigateur partagé sur le port 9999.
"""
import asyncio
import sys
sys.path.insert(0, '/root/Projets/Sharingan-WFK-Python')

from sharingan_app._internal.action_executor import get_action_executor


def test_sharingan_browser():
    """Test des commandes navigateur en langage naturel via Sharingan."""
    
    executor = get_action_executor()
    
    print("=" * 60)
    print("🧪 DÉMONSTRATION - SHARINGAN BROWSER VIA LANGAGE NATUREL")
    print("=" * 60)
    print("\n🌐 Le navigateur partagé (port 9999) va être utilisé pour")
    print("   exécuter des commandes en langage naturel.\n")
    
    test_commands = [
        ("Navigue vers Wikipedia", "Test navigation vers site connu"),
        ("Cherche intelligence artificielle sur Google", "Test recherche Google"),
        ("Lis la page", "Test lecture du contenu"),
        ("Défile vers le bas", "Test défilement"),
    ]
    
    results = []
    
    for i, (command, description) in enumerate(test_commands, 1):
        print(f"\n{'─' * 60}")
        print(f"📝 Commande {i}: \"{command}\"")
        print(f"   Description: {description}")
        print("-" * 60)
        
        try:
            result = executor.execute_action(command)
            results.append((command, result))
            
            status = result.get("status", "unknown")
            print(f"   Status: {status}")
            
            if "url" in result:
                print(f"   URL: {result['url']}")
            if "title" in result:
                print(f"   Titre: {result['title']}")
            if "text" in result:
                text = result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
                print(f"   Contenu: {text}")
            if "pixels" in result:
                print(f"   Défilé: {result['pixels']}px")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            results.append((command, {"status": "error", "message": str(e)}))
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    
    success_count = sum(1 for _, r in results if r.get("status") == "success")
    print(f"Commandes exécutées: {len(results)}")
    print(f"Succès: {success_count}")
    print(f"Échecs: {len(results) - success_count}")
    
    print("\n🌐 Navigateur toujours actif sur: http://localhost:9999")
    print("   Vous pouvez l'utiliser manuellement simultanément!")
    
    return results


async def test_direct_cdp():
    """Test direct des fonctions CDP de commodité."""
    from sharingans_browser_shared import (
        get_browser, navigate, get_text, scroll, 
        get_url, get_title, ensure_browser_connected
    )
    
    print("\n" + "=" * 60)
    print("🧪 TEST DIRECT - FONCTIONS CDP DE COMMODITÉ")
    print("=" * 60)
    
    await ensure_browser_connected()
    
    print(f"\nURL actuelle: {await get_url()}")
    print(f"Titre: {await get_title()}")
    
    print("\nTest de navigation vers BBC...")
    await navigate("https://www.bbc.com/afrique")
    await asyncio.sleep(2)
    
    print(f"Nouveau titre: {await get_title()}")
    
    print("\nTest de défilement...")
    await scroll(0, 300)
    
    print("\nTest d'extraction de texte...")
    text = await get_text("h1")
    print(f"H1 trouvé: {text[:100] if text else 'Aucun'}")
    
    print("\n✅ Tests directs terminés")


async def main():
    """Point d'entrée principal."""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║           SHARINGAN BROWSER - INTÉGRATION DÉMO             ║
    ╠════════════════════════════════════════════════════════════╣
    ║  Ce script démontre l'intégration du navigateur partagé   ║
    ║  dans Sharingan OS pour le contrôle via langage naturel.  ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Test 1: Via ActionExecutor (langage naturel)
    print("\n[1/2] Test via ActionExecutor (langage naturel)...")
    try:
        test_sharingan_browser()
    except Exception as e:
        print(f"   ⚠️ ActionExecutor: {e}")
    
    # Test 2: Fonctions directes CDP
    print("\n[2/2] Test des fonctions CDP directes...")
    try:
        await test_direct_cdp()
    except Exception as e:
        print(f"   ⚠️ CDP direct: {e}")
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║  Navigateur toujours actif sur: http://localhost:9999     ║
    ║  Utilisez-le manuellement pendant que Sharingan travaille!║
    ╚════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    asyncio.run(main())
