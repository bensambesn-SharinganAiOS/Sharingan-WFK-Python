#!/usr/bin/env python3
"""
Sharingan Browser - Processus persistant avec controle
Ce script lance Chrome et le garde ouvert avec un systeme de commandes simple.
"""

import sys
import os
import time
import json
import signal

sys.path.insert(0, '/root/Projets/Sharingan-WFK-Python')

from sharingan_app._internal.browser_controller import get_browser_controller

# Fichier de commande
CMD_FILE = "/tmp/sharingan_browser_cmd.txt"
RESULT_FILE = "/tmp/sharingan_browser_result.txt"

def write_result(result):
    with open(RESULT_FILE, 'w') as f:
        json.dump(result, f)

def read_command():
    if os.path.exists(CMD_FILE):
        with open(CMD_FILE, 'r') as f:
            cmd = f.read().strip()
        os.remove(CMD_FILE)
        return cmd
    return None

def main():
    print("=" * 70)
    print("  🌍 SHARINGAN BROWSER - PROCESSUS PERMANENT")
    print("=" * 70)
    print()
    
    # Creer le controller
    ctrl = get_browser_controller(browser='chrome', headless=False)
    
    # URL YouTube avec recherche
    search_url = "https://www.youtube.com/results?search_query=aissatou+diop+fall+ngonalou+rewmi+adp+PublicSn"
    
    print("Lancement de Chrome vers YouTube...")
    result = ctrl.launch_browser(search_url)
    print(f"  -> {result['status']}")
    
    if result['status'] != 'success':
        print(f"Erreur: {result}")
        return
    
    print()
    print("=" * 70)
    print("  NAVIGATEUR YOUTUBE OUVERT!")
    print("=" * 70)
    print()
    print("Le navigateur est actif sur ton ecran.")
    print()
    print("POUR LE CONTROLER, execute dans un AUTRE terminal:")
    print()
    print("  python3 browser_control.py info")
    print("  python3 browser_control.py navigate https://google.com")
    print("  python3 browser_control.py screenshot")
    print("  python3 browser_control.py scroll bas")
    print("  python3 browser_control.py close")
    print()
    print("Le navigateur RESTERA OUVERT jusqu'a 'close'")
    print()
    
    # Boucle principale - attend les commandes
    last_cmd_time = time.time()
    
    while True:
        try:
            time.sleep(1)
            
            cmd = read_command()
            
            if cmd:
                print(f"\n📥 Commande recue: {cmd}")
                last_cmd_time = time.time()
                
                # Executer la commande
                parts = cmd.split()
                action = parts[0] if parts else ""
                
                result = {"status": "error", "message": "Commande inconnu"}
                
                if action == "close":
                    ctrl.close_browser()
                    result = {"status": "success", "message": "Navigateur ferme"}
                    write_result(result)
                    print("Navigateur ferme. Au revoir!")
                    break
                
                elif action == "info":
                    try:
                        info = ctrl.get_page_info()
                        result = info
                    except:
                        result = {"status": "error", "message": "Navigateur ferme"}
                
                elif action == "screenshot":
                    path = f"/tmp/sharinganscreenshot_{int(time.time())}.png"
                    try:
                        ss = ctrl.take_screenshot(path)
                        result = {"status": "success", "path": path}
                    except:
                        result = {"status": "error", "message": "Erreur screenshot"}
                
                elif action == "navigate":
                    url = ' '.join(parts[1:])
                    if url:
                        if not url.startswith('http'):
                            url = 'https://' + url
                        try:
                            nav_result = ctrl.navigate(url)
                            result = nav_result
                        except:
                            result = {"status": "error", "message": "Erreur navigation"}
                
                elif action == "scroll":
                    direction = 'down' if 'bas' in cmd else 'up'
                    try:
                        ctrl.execute_js(f"window.scrollBy(0, {500 if direction == 'down' else -500});")
                        result = {"status": "success", "action": f"scroll {direction}"}
                    except:
                        result = {"status": "error", "message": "Erreur scroll"}
                
                elif action == "js":
                    script = ' '.join(parts[1:])
                    try:
                        js_result = ctrl.execute_js(script)
                        result = js_result
                    except:
                        result = {"status": "error", "message": "Erreur JS"}
                
                write_result(result)
                print(f"Resultat: {result.get('status', 'error')}")
            
            # Verifier si le navigateur est toujours actif
            if time.time() - last_cmd_time > 300:  # 5 minutes sans commande
                print("Aucune commande depuis 5 minutes. Fermeture...")
                try:
                    ctrl.close_browser()
                except:
                    pass
                break
                
        except (EOFError, KeyboardInterrupt):
            print("\n\nFermeture...")
            try:
                ctrl.close_browser()
            except:
                pass
            break

if __name__ == "__main__":
    main()
