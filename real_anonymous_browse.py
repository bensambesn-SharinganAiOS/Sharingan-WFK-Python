#!/usr/bin/env python3
"""
NAVIGATION RÉELLEMENT ANONYME - SOLUTION COMPLÈTE
Lance Chrome avec Tor et navigue anonymement
"""

import subprocess
import time
import os
import signal
import sys

def check_tor_status():
    """Vérifie que Tor fonctionne"""
    print("🔍 VÉRIFICATION TOR...")
    
    # Vérifier service
    result = subprocess.run(['systemctl', 'is-active', 'tor'], 
                          capture_output=True, text=True)
    if 'active' not in result.stdout:
        print("❌ Tor inactif - activation...")
        subprocess.run(['sudo', 'systemctl', 'start', 'tor'])
        time.sleep(5)
    
    # Tester connectivité
    try:
        result = subprocess.run(
            ['torsocks', 'curl', '-s', 'https://check.torproject.org/api/ip'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0 and '"IsTor":true' in result.stdout:
            print("✅ Tor opérationnel")
            return True
        else:
            print("❌ Tor ne fonctionne pas correctement")
            return False
    except:
        print("❌ Impossible de vérifier Tor")
        return False

def launch_chrome_with_tor():
    """Lance Chrome configuré pour utiliser Tor"""
    print("🚀 LANCEMENT CHROME AVEC TOR...")
    
    # Créer un profil Chrome séparé pour Tor
    tor_profile = "/tmp/sharingan-tor-chrome"
    os.makedirs(tor_profile, exist_ok=True)
    
    # Commande Chrome avec proxy Tor
    cmd = [
        "google-chrome",
        "--proxy-server=socks5://127.0.0.1:9050",
        "--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE 127.0.0.1",
        f"--user-data-dir={tor_profile}",
        "--incognito",
        "--no-first-run",
        "--disable-default-apps",
        "--disable-sync",
        "--disable-translate",
        "--hide-crash-restore-bubble",
        "--disable-background-timer-throttling",
        "--disable-renderer-backgrounding",
        "--disable-background-networking"
    ]
    
    print(f"📋 Commande: google-chrome --proxy-server=socks5://127.0.0.1:9050 ...")
    
    try:
        # Lancer Chrome
        process = subprocess.Popen(cmd)
        print(f"✅ Chrome lancé (PID: {process.pid})")
        
        # Attendre que Chrome démarre
        print("⏰ Attente démarrage Chrome...")
        time.sleep(8)
        
        return process
        
    except Exception as e:
        print(f"❌ Échec lancement Chrome: {e}")
        return None

def navigate_with_sharingan(url, chrome_pid):
    """Utilise Sharingan pour naviguer dans Chrome"""
    print(f"🌐 NAVIGATION SHARINGAN VERS: {url}")
    
    try:
        # Importer ici pour éviter les erreurs de modules
        sys.path.insert(0, '/root/Projets/Sharingan-WFK-Python')
        from universal_browser_controller import UniversalBrowserController
        
        controller = UniversalBrowserController()
        success, mode = controller.init_control()
        
        if success:
            print(f"✅ Sharingan connecté: {mode}")
            
            # Navigation
            result = controller.navigate(url)
            
            if result[0]:
                print("✅ Navigation réussie")
                print("⏰ Attente chargement complet...")
                time.sleep(10)  # Plus de temps pour le chargement
                
                # Essayer d'extraire du contenu
                try:
                    content_result = controller.extract_visible_content('page_content')
                    if content_result[0]:
                        content = content_result[1]
                        print(f"📄 Contenu extrait: {len(content)} caractères")
                        
                        # Chercher des IPs dans le contenu
                        import re
                        ips = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', content)
                        if ips:
                            print(f"🌐 IPs trouvées: {ips}")
                        else:
                            print("⚠️ Aucune IP trouvée dans le contenu extrait")
                    else:
                        print("⚠️ Extraction de contenu limitée")
                        
                except Exception as e:
                    print(f"⚠️ Erreur extraction: {e}")
                
                return True
                
            else:
                print(f"❌ Échec navigation: {result[1] if len(result) > 1 else 'Erreur'}")
                return False
                
        else:
            print("❌ Échec connexion Sharingan")
            return False
            
    except Exception as e:
        print(f"❌ Erreur Sharingan: {e}")
        return False

def cleanup_chrome(process):
    """Nettoie le processus Chrome"""
    if process:
        try:
            print("🧹 Fermeture Chrome...")
            process.terminate()
            process.wait(timeout=5)
            print("✅ Chrome fermé")
        except:
            try:
                process.kill()
                print("⚠️ Chrome forcé fermé")
            except:
                print("⚠️ Impossible de fermer Chrome")

def main():
    print("🚀 SHARINGAN OS - NAVIGATION ANONYME RÉELLE")
    print("=" * 55)
    
    # Étape 1: Vérifier Tor
    if not check_tor_status():
        print("❌ Impossible de configurer Tor - arrêt")
        return
    
    # Étape 2: Lancer Chrome avec Tor
    chrome_process = launch_chrome_with_tor()
    if not chrome_process:
        print("❌ Impossible de lancer Chrome - arrêt")
        return
    
    try:
        # Étape 3: Naviguer vers whatsmyip.org
        success = navigate_with_sharingan('https://www.whatsmyip.org/', chrome_process.pid)
        
        if success:
            print("\n🎯 RÉSULTAT:")
            print("✅ Navigation anonyme réussie")
            print("🎯 Vérifiez votre Chrome (nouvel onglet)")
            print("🎯 L'IP affichée devrait être l'IP Tor (194.26.192.46)")
            print("🎯 Si c'est 154.124.15.146, alors Chrome n'utilise pas Tor")
            
            # Attendre que l'utilisateur vérifie
            print("\n⏰ Chrome reste ouvert pour vos tests...")
            print("💡 Appuyez Ctrl+C quand vous avez terminé")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Fermeture...")
                
        else:
            print("❌ Échec de la navigation anonyme")
            
    finally:
        # Nettoyer
        cleanup_chrome(chrome_process)
        
        # Supprimer le profil temporaire
        import shutil
        try:
            shutil.rmtree("/tmp/sharingan-tor-chrome", ignore_errors=True)
            print("🧹 Profil Chrome nettoyé")
        except:
            pass

if __name__ == "__main__":
    main()
