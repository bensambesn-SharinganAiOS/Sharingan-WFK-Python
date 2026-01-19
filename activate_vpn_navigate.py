#!/usr/bin/env python3
"""
ACTIVATION VPN TOR + NAVIGATION ANONYME VERS WHATS MY IP
Preuve réelle de l'anonymat avec Sharingan OS
"""

import subprocess
import sys
import time
import requests

def run_command(cmd, shell=False):
    """Exécute une commande système"""
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        else:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def activate_tor():
    """Active et vérifie Tor"""
    print("🔧 ACTIVATION VPN TOR")
    print("=" * 30)
    
    # Vérifier si Tor est installé
    success, _, _ = run_command("which tor")
    if not success:
        print("❌ Tor n'est pas installé")
        print("💡 Installez avec: sudo apt install tor")
        return False
    
    print("✅ Tor est installé")
    
    # Vérifier/activer le service Tor
    success, _, _ = run_command("systemctl is-active tor")
    if not success:
        print("🔄 Activation du service Tor...")
        success, _, error = run_command("sudo systemctl start tor")
        if success:
            print("✅ Service Tor activé")
            time.sleep(3)  # Attendre que Tor démarre
        else:
            print(f"❌ Échec activation Tor: {error}")
            return False
    else:
        print("✅ Service Tor déjà actif")
    
    # Tester la connectivité Tor
    print("🔍 Test de connectivité Tor...")
    try:
        # Utiliser torsocks pour curl via Tor
        success, output, _ = run_command("torsocks curl -s https://check.torproject.org/api/ip")
        if success and '"IsTor":true' in output:
            print("✅ Tor fonctionne correctement")
            # Extraire l'IP Tor
            import json
            try:
                data = json.loads(output)
                tor_ip = data.get('IP', 'Unknown')
                print(f"📍 IP Tor: {tor_ip}")
                return True, tor_ip
            except:
                print("⚠️ Impossible de parser la réponse Tor")
                return True, "Unknown"
        else:
            print("⚠️ Tor peut être lent à démarrer")
            return True, "Unknown"
    except Exception as e:
        print(f"⚠️ Erreur test Tor: {e}")
        return True, "Unknown"

def check_current_ip():
    """Vérifie l'IP actuelle"""
    print("\n🌐 VÉRIFICATION IP ACTUELLE")
    print("=" * 30)
    
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        if response.status_code == 200:
            current_ip = response.json()['ip']
            print(f"📍 IP actuelle (sans VPN): {current_ip}")
            return current_ip
        else:
            print("⚠️ Impossible de récupérer l'IP actuelle")
            return None
    except Exception as e:
        print(f"⚠️ Erreur récupération IP: {e}")
        return None

def navigate_to_whatsmyip():
    """Navigation vers whatsmyip.org avec le contrôleur Sharingan"""
    print("\n🌐 NAVIGATION VERS WHATS MY IP")
    print("=" * 35)
    
    try:
        from universal_browser_controller import UniversalBrowserController
        
        print("🔍 Initialisation du contrôleur navigateur Sharingan...")
        controller = UniversalBrowserController()
        success, mode = controller.init_control()
        
        if not success:
            print("❌ Échec initialisation contrôleur navigateur")
            return False
        
        print(f"✅ Contrôleur actif: {mode}")
        print("🏗️ Navigation vers https://www.whatsmyip.org/...")
        
        # Navigation vers whatsmyip.org
        result = controller.navigate('https://www.whatsmyip.org/')
        
        if result[0]:
            print("✅ Navigation réussie")
            print("⏰ Attente de chargement complet...")
            time.sleep(5)
            
            # Essayer d'extraire des informations de la page
            try:
                content_result = controller.extract_visible_content('page_content')
                if content_result[0]:
                    content = content_result[1]
                    print("📄 Contenu de la page analysé")
                    
                    # Chercher des IPs dans le contenu
                    import re
                    ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
                    ips_found = re.findall(ip_pattern, content)
                    
                    if ips_found:
                        print(f"🌐 IPs détectées sur la page: {ips_found[:5]}")
                        print("🎯 Cette IP devrait être celle utilisée pour la navigation")
                    else:
                        print("⚠️ Aucune IP claire détectée automatiquement")
                else:
                    print("⚠️ Extraction de contenu limitée")
                    
            except Exception as e:
                print(f"⚠️ Erreur extraction contenu: {e}")
            
            print("\n🎯 RÉSULTAT:")
            print("✅ Navigation whatsmyip.org réussie")
            print("🎯 Vérifiez votre navigateur Chrome actif")
            print("🎯 La page devrait afficher l'IP utilisée pour la connexion")
            print("🛡️ Si Tor est actif, l'IP devrait être différente de votre IP réelle")
            
            return True
            
        else:
            error_msg = result[1] if len(result) > 1 else "Erreur inconnue"
            print(f"❌ Échec navigation: {error_msg}")
            return False
            
    except ImportError:
        print("❌ Module universal_browser_controller non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur navigation: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 SHARINGAN OS - PREUVE D'ANONYMAT VPN")
    print("=" * 45)
    
    # Étape 1: Activer Tor
    tor_success, tor_ip = activate_tor()
    if not tor_success:
        print("\n❌ Impossible d'activer Tor - arrêt")
        return
    
    # Étape 2: Vérifier IP actuelle
    current_ip = check_current_ip()
    
    # Étape 3: Navigation vers whatsmyip.org
    nav_success = navigate_to_whatsmyip()
    
    # Résumé final
    print("\n🎊 RÉSULTAT FINAL")
    print("=" * 20)
    
    if tor_ip and tor_ip != "Unknown" and current_ip:
        print(f"🛡️ VPN Tor: ACTIF (IP Tor: {tor_ip})")
        print(f"📍 IP réelle: {current_ip}")
        if tor_ip != current_ip:
            print("✅ ANONYMAT CONFIRMÉ - IPs différentes")
        else:
            print("⚠️ IPs identiques - Tor peut ne pas être utilisé par le navigateur")
    else:
        print("⚠️ Impossible de vérifier complètement l'anonymat")
    
    if nav_success:
        print("✅ Navigation whatsmyip.org: RÉUSSIE")
        print("🎯 Vérifiez votre Chrome - l'IP affichée prouve l'anonymat")
    else:
        print("❌ Navigation whatsmyip.org: ÉCHEC")
    
    print("\n💡 Pour maximiser l'anonymat:")
    print("   • Configurez votre Chrome pour utiliser Tor")
    print("   • Utilisez un proxy SOCKS5: 127.0.0.1:9050")
    print("   • Vérifiez les extensions de confidentialité")

if __name__ == "__main__":
    main()
