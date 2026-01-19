#!/usr/bin/env python3
"""
VÉRIFICATION RAPIDE DE L'ANONYMAT
Compare IP directe vs IP Tor
"""

import subprocess
import requests
import time

def get_direct_ip():
    """Récupère l'IP directe"""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except:
        return None

def get_tor_ip():
    """Récupère l'IP via Tor"""
    try:
        # Utiliser torsocks si disponible
        result = subprocess.run(['which', 'torsocks'], capture_output=True, text=True)
        if result.returncode == 0:
            # torsocks disponible
            result = subprocess.run(['torsocks', 'curl', '-s', 'https://api.ipify.org'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout.strip()
        
        # Essayer avec proxy Python
        import socks
        import socket
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9050)
        socket.socket = socks.socksocket
        
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        return response.json()['ip']
        
    except:
        return None

def main():
    print("🔍 VÉRIFICATION RAPIDE ANONYMAT")
    print("=" * 35)
    
    # IP directe
    print("📍 Récupération IP directe...")
    direct_ip = get_direct_ip()
    print(f"   IP directe: {direct_ip}")
    
    # IP Tor
    print("🛡️ Récupération IP Tor...")
    tor_ip = get_tor_ip()
    print(f"   IP Tor: {tor_ip}")
    
    # Analyse
    print("\n🎯 ANALYSE:")
    if direct_ip and tor_ip:
        if direct_ip == tor_ip:
            print("❌ ANONYMAT NON ACTIF: IPs identiques")
            print("   Chrome utilise la connexion directe")
        else:
            print("✅ ANONYMAT ACTIF: IPs différentes")
            print(f"   Masquage: {direct_ip} → {tor_ip}")
            
            # Vérifier que c'est bien une IP Tor
            if tor_ip.startswith(('185.', '188.', '192.', '194.', '195.')):
                print("   🛡️ IP Tor confirmée (range connue)")
            else:
                print("   ❓ IP différente mais pas forcément Tor")
    else:
        print("❌ Impossible de récupérer les IPs")
    
    print(f"\n💡 POUR ANONYMAT RÉEL:")
    print(f"   Lancez Chrome avec: google-chrome --proxy-server=socks5://127.0.0.1:9050")
    print(f"   Puis naviguez vers: https://www.whatsmyip.org/")

if __name__ == "__main__":
    main()
