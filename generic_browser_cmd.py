# Commande Navigateur Générique - Sharingan OS
# Script pour envoyer des commandes au démon navigateur générique

import json
import time
import sys
import os

CMD_FILE = "/tmp/generic_browser_cmd.txt"
RESULT_FILE = "/tmp/generic_browser_result.txt"
STATUS_FILE = "/tmp/generic_browser_status.txt"

def send_command(cmd_type, params=None):
    """Envoie une commande au démon"""
    if params is None:
        params = {}

    cmd_data = {
        "type": cmd_type,
        "params": params,
        "timestamp": time.time()
    }

    # Écrire la commande
    try:
        with open(CMD_FILE, 'w') as f:
            json.dump(cmd_data, f)
    except Exception as e:
        print(f"❌ Erreur écriture commande: {e}")
        return None

    print(f"📨 Commande envoyée: {cmd_type}")
    print(f"   Paramètres: {params}")

    # Attendre le résultat
    print("⏳ Attente du résultat...")
    timeout = 10
    start_time = time.time()

    while time.time() - start_time < timeout:
        if os.path.exists(RESULT_FILE):
            try:
                with open(RESULT_FILE, 'r') as f:
                    result = json.load(f)
                os.remove(RESULT_FILE)
                print("✅ Résultat reçu:")
                print(f"   {result}")
                return result
            except Exception as e:
                print(f"❌ Erreur lecture résultat: {e}")
                break
        time.sleep(0.5)

    print("⏰ Timeout - pas de résultat reçu")
    return None

def get_status():
    """Obtient le statut du démon"""
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, 'r') as f:
                status = json.load(f)
            print("📊 Statut du démon:")
            print(f"   {status}")
            return status
        except Exception as e:
            print(f"❌ Erreur lecture statut: {e}")
    else:
        print("❌ Fichier de statut non trouvé")
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generic_browser_cmd.py <commande> [paramètres]")
        print()
        print("Commandes disponibles:")
        print("  status                    - Obtenir le statut du démon")
        print("  scroll <pixels> [direction] - Scroll (défaut: 300px down)")
        print("  navigate <url>            - Naviguer vers une URL")
        print("  click <selector>          - Cliquer sur un élément CSS")
        print("  fill <selector> <value>   - Remplir un champ")
        print("  stop                      - Arrêter le démon")
        print()
        print("Exemples:")
        print("  python3 generic_browser_cmd.py status")
        print("  python3 generic_browser_cmd.py scroll 500")
        print("  python3 generic_browser_cmd.py scroll 300 up")
        print("  python3 generic_browser_cmd.py navigate https://example.com")
        return

    command = sys.argv[1]

    if command == "status":
        get_status()

    elif command == "scroll":
        pixels = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        direction = sys.argv[3] if len(sys.argv) > 3 else "down"
        send_command("scroll", {"pixels": pixels, "direction": direction})

    elif command == "navigate":
        if len(sys.argv) < 3:
            print("❌ URL requise pour la navigation")
            return
        url = sys.argv[2]
        send_command("navigate", {"url": url})

    elif command == "click":
        if len(sys.argv) < 3:
            print("❌ Sélecteur CSS requis pour le clic")
            return
        selector = sys.argv[2]
        send_command("click", {"selector": selector})

    elif command == "fill":
        if len(sys.argv) < 4:
            print("❌ Sélecteur CSS et valeur requis pour le remplissage")
            return
        selector = sys.argv[2]
        value = sys.argv[3]
        send_command("fill", {"selector": selector, "value": value})

    elif command == "stop":
        result = send_command("stop")
        if result and result.get("status") == "success":
            print("🛑 Commande d'arrêt envoyée - le démon va s'arrêter")

    else:
        print(f"❌ Commande inconnue: {command}")

if __name__ == "__main__":
    main()