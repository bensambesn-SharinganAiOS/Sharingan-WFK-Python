#!/usr/bin/env python3
"""
Sharingan Browser Client - Envoie des commandes au serveur
Usage: python3 browser_client.py <commande> [arguments]
"""

import sys
import socket
import json

PORT = 19999

def send_command(cmd):
    """Envoie une commande au serveur et retourne le resultat."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', PORT))
        sock.sendall(cmd.encode())
        
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        
        sock.close()
        return json.loads(response.decode())
        
    except ConnectionRefusedError:
        return {"status": "error", "message": "Serveur non actif. Lancez 'python3 browser_server.py' d'abord"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 browser_client.py <commande> [arguments]")
        print()
        print("Commandes:")
        print("  info                     - Afficher les infos de la page")
        print("  navigate [url]           - Naviguer vers une URL")
        print("  screenshot               - Prendre une capture d'ecran")
        print("  scroll bas/haut          - Defiler dans la page")
        print("  js [script]              - Executer JavaScript")
        print("  fill [selector] [valeur] - Remplir un champ")
        print("  click [selector]         - Cliquer sur un element")
        print("  list                     - Lister les navigateurs")
        print("  close                    - Fermer le navigateur et le serveur")
        print()
        print("Exemples:")
        print("  python3 browser_client.py info")
        print("  python3 browser_client.py navigate https://google.com")
        print("  python3 browser_client.py screenshot")
        print("  python3 browser_client.py scroll bas")
        return
    
    cmd = ' '.join(sys.argv[1:])
    result = send_command(cmd)
    
    # Afficher le resultat de maniere lisible
    if result['status'] == 'success':
        if isinstance(result, dict) and len(result) <= 2:
            print(result.get('message', 'OK'))
        else:
            print(json.dumps(result, indent=2))
    else:
        print(f"Erreur: {result.get('message', result)}")

if __name__ == "__main__":
    main()
