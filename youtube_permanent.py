#!/usr/bin/env python3
"""
Sharingan Browser - Session persistante en arriere-plan
Ce script lance le navigateur et permet de le controler a tout moment.
"""

import os
import sys
import time
import json
import signal
from sharingan_app._internal.browser_manager import get_browser_manager

# Fichier de controle
CONTROL_FILE = "/tmp/sharingan_browser_ctrl.json"
STATE_FILE = "/tmp/sharingan_browser_state.json"

def save_command(cmd):
    """Sauvegarde une commande pour execution."""
    with open(CONTROL_FILE, 'w') as f:
        json.dump({
            'command': cmd,
            'timestamp': time.time()
        }, f)

def read_result():
    """Lit le resultat de la dernière commande."""
    result_file = "/tmp/sharingan_browser_result.json"
    if os.path.exists(result_file):
        try:
            with open(result_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

def main():
    # Mode decide par les arguments
    if len(sys.argv) < 2:
        # Mode serveur: lance le navigateur et attend les commandes
        print("=" * 70)
        print("  🌍 SHARINGAN BROWSER - SERVEUR")
        print("=" * 70)
        print()
        
        bm = get_browser_manager()
        
        # URL YouTube avec recherche
        search_url = "https://www.youtube.com/results?search_query=aissatou+diop+fall+ngonalou+rewmi+adp+PublicSn"
        
        print("Lancement du navigateur YouTube...")
        result = bm.launch('youtube', search_url, browser='chrome', headless=False)
        print(f"  -> {result['status']}")
        print()
        
        # Effacer l'ancien fichier de controle
        if os.path.exists(CONTROL_FILE):
            os.remove(CONTROL_FILE)
        
        print("=" * 70)
        print("  NAVIGATEUR YOUTUBE OUVERT!")
        print("=" * 70)
        print()
        print("Le navigateur est actif et pret.")
        print()
        print("Pour le controler, execute dans un AUTRE terminal:")
        print("  python3 youtube_permanent.py navigate [url]")
        print("  python3 youtube_permanent.py scroll [bas/haut]")
        print("  python3 youtube_permanent.py screenshot")
        print("  python3 youtube_permanent.py info")
        print("  python3 youtube_permanent.py close")
        print()
        print("Ou en une seule commande:")
        print("  python3 -c \"from sharingan_app._internal.browser_manager import get_browser_manager; bm = get_browser_manager(); bm.navigate('https://google.com')\"")
        print()
        print("Le navigateur reste OUVERT. Appuie sur Ctrl+C pour fermer.")
        print()
        
        # Boucle principale - attend les commandes
        last_check = 0
        while True:
            try:
                # Verifier les commandes toutes les 2 secondes
                time.sleep(2)
                
                if os.path.exists(CONTROL_FILE):
                    with open(CONTROL_FILE, 'r') as f:
                        data = json.load(f)
                    
                    cmd = data.get('command', '')
                    os.remove(CONTROL_FILE)
                    
                    if cmd:
                        print(f"\n📥 Commande recue: {cmd}")
                        
                        # Executer la commande
                        if cmd == 'close':
                            print("Fermeture du navigateur...")
                            bm.close()
                            print("Navigateur ferme. Au revoir!")
                            break
                        
                        elif cmd.startswith('navigate '):
                            url = cmd.replace('navigate ', '').strip()
                            if url:
                                if not url.startswith('http'):
                                    url = 'https://' + url
                                print(f"Navigation vers {url}...")
                                result = bm.navigate(url)
                                if result['status'] == 'success':
                                    print(f"  -> OK: {result.get('title', '')}")
                        
                        elif cmd == 'screenshot':
                            path = f"/tmp/sharinganscreenshot_{int(time.time())}.png"
                            ss = bm.screenshot(path)
                            print(f"  -> Screenshot: {ss.get('path', '')}")
                        
                        elif cmd in ['info', 'page']:
                            info = bm.get_page_info()
                            print(f"  -> {info.get('title', 'N/A')}")
                            print(f"     {info.get('url', 'N/A')[:60]}...")
                        
                        elif cmd.startswith('scroll '):
                            parts = cmd.split()
                            direction = 'down' if 'bas' in cmd else 'up'
                            pixels = 500
                            print(f"  -> Scroll {direction}...")
                            bm.scroll(pixels, direction)
                        
                        else:
                            print(f"  -> Commande non reconnue: {cmd}")
                
            except (EOFError, KeyboardInterrupt):
                print("\n\nFermeture du navigateur...")
                bm.close()
                break
    
    else:
        # Mode client: envoyer une commande au serveur
        cmd = ' '.join(sys.argv[1:])
        
        bm = get_browser_manager()
        
        # Verifier si un navigateur existe
        result = bm.list()
        
        if result['total'] == 0 and cmd != 'launch':
            print("Aucun navigateur actif. Lancement de YouTube...")
            search_url = "https://www.youtube.com/results?search_query=aissatou+diop+fall+ngonalou+rewmi+adp+PublicSn"
            result = bm.launch('youtube', search_url, browser='chrome', headless=False)
            print(f"  -> {result['status']}")
            time.sleep(3)
        
        # Executer la commande
        if cmd == 'launch':
            search_url = "https://www.youtube.com/results?search_query=aissatou+diop+fall+ngonalou+rewmi+adp+PublicSn"
            result = bm.launch('youtube', search_url, browser='chrome', headless=False)
            print(f"Navigateur lance: {result['status']}")
        
        elif cmd == 'close':
            bm.close()
            print("Navigateur ferme.")
        
        elif cmd == 'list':
            result = bm.list()
            print(f"Navigateurs: {result['total']}")
            for b in result['browsers']:
                print(f"  - {b['name']}: {b['status']}")
        
        elif cmd.startswith('navigate '):
            url = cmd.replace('navigate ', '').strip()
            if url:
                if not url.startswith('http'):
                    url = 'https://' + url
                result = bm.navigate(url)
                if result['status'] == 'success':
                    print(f"OK: {result.get('title', 'N/A')}")
        
        elif cmd == 'screenshot':
            path = f"/tmp/sharinganscreenshot_{int(time.time())}.png"
            ss = bm.screenshot(path)
            print(f"Screenshot: {ss.get('path', 'N/A')}")
        
        elif cmd == 'info' or cmd == 'page':
            info = bm.get_page_info()
            print(f"Page: {info.get('title', 'N/A')}")
            print(f"URL: {info.get('url', 'N/A')}")
        
        elif cmd in ['scroll bas', 'scroll down', 'scroll_down']:
            bm.scroll(500, 'down')
            print("Scrolled vers le bas")
        
        elif cmd in ['scroll haut', 'scroll up', 'scroll_up']:
            bm.scroll(500, 'up')
            print("Scrolled vers le haut")
        
        else:
            print(f"Commande: {cmd}")
            print("Commandes disponibles: launch, close, list, navigate [url], screenshot, info, scroll [bas/haut]")


if __name__ == "__main__":
    main()
