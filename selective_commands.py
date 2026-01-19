#!/usr/bin/env python3
"""
COMMANDES RAPIDES - ANONYMAT SÉLECTIF SHARINGAN OS
Utilisation pratique du système de proxy intelligent
"""

import sys
import subprocess
from sharingan_app._internal.selective_proxy_manager import SelectiveProxyManager

def main():
    if len(sys.argv) < 2:
        print("🛡️ SHARINGAN OS - COMMANDES ANONYMAT SÉLECTIF")
        print("=" * 50)
        print()
        print("📋 COMMANDES DISPONIBLES:")
        print("   status           → État réseau et anonymat")
        print("   browser          → Lance Chrome anonyme")
        print("   scan <target>    → Scan réseau anonyme")
        print("   run <command>    → Exécute commande avec détection auto")
        print("   anon <command>   → Force anonymat")
        print("   normal <command> → Force connexion normale")
        print()
        print("💡 EXEMPLES:")
        print("   python3 selective_commands.py status")
        print("   python3 selective_commands.py browser")
        print("   python3 selective_commands.py scan scanme.nmap.org")
        print("   python3 selective_commands.py run 'nmap -sV 192.168.1.1'")
        return

    manager = SelectiveProxyManager()
    command = sys.argv[1]

    if command == "status":
        print("🌐 ÉTAT RÉSEAU ET ANONYMAT:")
        from sharingan_app._internal.selective_proxy_manager import network_status
        network_status()

    elif command == "browser":
        print("🛡️ LANCEMENT CHROME ANONYME...")
        url = sys.argv[2] if len(sys.argv) > 2 else "https://www.whatsmyip.org/"
        process = manager.launch_browser_anon('google-chrome', url)
        if process:
            print(f"✅ Chrome lancé (PID: {process.pid})")
            print("💡 Vérifiez l'IP affichée - elle devrait être différente!")
            print("💡 Fermez Chrome pour terminer")
            process.wait()
        else:
            print("❌ Échec lancement Chrome")

    elif command == "scan":
        if len(sys.argv) < 3:
            print("❌ Usage: python3 selective_commands.py scan <target>")
            return

        target = sys.argv[2]
        print(f"🔍 SCAN ANONYME DE: {target}")

        # Nmap avec Tor
        cmd = f"torsocks nmap -sV --script vuln {target}"
        print(f"📋 Commande: {cmd}")

        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=60)
            print("📊 RÉSULTATS:")
            print(result.stdout)
            if result.stderr:
                print("⚠️ Erreurs:", result.stderr)
        except subprocess.TimeoutExpired:
            print("⏰ Timeout (scan peut être long)")

    elif command == "run":
        if len(sys.argv) < 3:
            print("❌ Usage: python3 selective_commands.py run '<command>'")
            return

        cmd_str = ' '.join(sys.argv[2:])
        print(f"🚀 EXÉCUTION AVEC DÉTECTION AUTO: {cmd_str}")

        # Exécution avec détection automatique
        process = manager.run_command(cmd_str.split()[0], cmd_str.split()[1:])

        # Attendre la fin
        try:
            process.wait(timeout=30)
            print("✅ Commande terminée")
        except subprocess.TimeoutExpired:
            print("⏰ Commande en cours d'exécution (timeout)")
            process.terminate()

    elif command == "anon":
        if len(sys.argv) < 3:
            print("❌ Usage: python3 selective_commands.py anon '<command>'")
            return

        cmd_str = ' '.join(sys.argv[2:])
        print(f"🛡️ EXÉCUTION FORCÉE ANONYME: {cmd_str}")

        process = manager.run_command(cmd_str.split()[0], cmd_str.split()[1:], force_anon=True)

        try:
            process.wait(timeout=30)
            print("✅ Commande anonyme terminée")
        except subprocess.TimeoutExpired:
            print("⏰ Commande anonyme en cours")
            process.terminate()

    elif command == "normal":
        if len(sys.argv) < 3:
            print("❌ Usage: python3 selective_commands.py normal '<command>'")
            return

        cmd_str = ' '.join(sys.argv[2:])
        print(f"🌐 EXÉCUTION FORCÉE NORMALE: {cmd_str}")

        process = manager.run_command(cmd_str.split()[0], cmd_str.split()[1:], force_normal=True)

        try:
            process.wait(timeout=30)
            print("✅ Commande normale terminée")
        except subprocess.TimeoutExpired:
            print("⏰ Commande normale en cours")
            process.terminate()

    else:
        print(f"❌ Commande inconnue: {command}")
        print("💡 Utilisez sans arguments pour voir l'aide")

if __name__ == "__main__":
    main()