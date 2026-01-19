#!/usr/bin/env python3
"""
SHARINGAN OS - SELECTIVE PROXY MANAGER
Routeur intelligent pour anonymat sélectif par application/fenêtre
"""

import subprocess
import os
import time
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger("sharingan.proxy")

class SelectiveProxyManager:
    """Gestionnaire de proxy sélectif - Le vrai secret de l'anonymat efficace"""

    def __init__(self):
        self.tor_proxy = {
            'socks5': '127.0.0.1:9050',
            'http': '127.0.0.1:8118'  # Polipo si configuré
        }

        # Applications sensibles (anonymes par défaut)
        self.sensitive_apps = {
            'chrome', 'chromium', 'firefox', 'brave',
            'nmap', 'nikto', 'sqlmap', 'gobuster', 'dirbuster',
            'metasploit', 'burp', 'wireshark',
            'curl', 'wget', 'torify', 'torsocks'
        }

        # Applications système (jamais anonymes)
        self.system_apps = {
            'apt', 'apt-get', 'yum', 'dnf', 'pacman',
            'systemctl', 'service', 'ssh', 'scp',
            'python', 'pip', 'npm', 'node'
        }

        # Mots-clés pour détection automatique
        self.anon_keywords = [
            'scan', 'pentest', 'recon', 'anonymous', 'tor', 'proxy',
            'hack', 'exploit', 'vulnerability', 'attack', 'intrusion'
        ]

        self.system_keywords = [
            'update', 'upgrade', 'install', 'remove', 'apt', 'yum',
            'systemctl', 'service', 'local', 'localhost'
        ]

    def should_anonymize(self, command: str, args: List[str] = None) -> bool:
        """Détermine si une commande doit être anonymisée"""

        full_command = command + ' ' + ' '.join(args or [])
        full_lower = full_command.lower()

        # Vérifier le nom de l'application
        app_name = command.split('/')[-1] if '/' in command else command.split()[0]
        if app_name in self.sensitive_apps:
            return True
        elif app_name in self.system_apps:
            return False

        # Détection par mots-clés
        if any(keyword in full_lower for keyword in self.anon_keywords):
            return True

        if any(keyword in full_lower for keyword in self.system_keywords):
            return False

        # Par défaut, pas d'anonymat (pour performance)
        return False

    def run_command(self, command: str, args: List[str] = None,
                   force_anon: bool = False, force_normal: bool = False) -> subprocess.Popen:
        """Exécute une commande avec routage sélectif"""

        args = args or []
        should_anon = force_anon or (self.should_anonymize(command, args) and not force_normal)

        if should_anon:
            # Vérifier que Tor fonctionne
            if self._check_tor_status():
                print(f"🛡️ Exécution anonyme: {command} {' '.join(args)}")
                return self._run_with_tor(command, args)
            else:
                print(f"⚠️ Tor indisponible, exécution normale: {command} {' '.join(args)}")

        print(f"🌐 Exécution normale: {command} {' '.join(args)}")
        return subprocess.Popen([command] + args)

    def launch_browser_anon(self, browser: str = 'chrome', url: str = None) -> subprocess.Popen:
        """Lance un navigateur avec Tor"""

        if not self._check_tor_status():
            print("❌ Tor indisponible pour navigation anonyme")
            return None

        # Profil séparé pour anonymat
        profile_dir = f"/tmp/sharingan-{browser}-tor"
        os.makedirs(profile_dir, exist_ok=True)

        cmd = [browser,
               '--proxy-server=socks5://127.0.0.1:9050',
               '--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE 127.0.0.1',
               f'--user-data-dir={profile_dir}',
               '--incognito',
               '--no-first-run']

        if url:
            cmd.append(url)

        print(f"🛡️ Lancement {browser} anonyme...")
        return subprocess.Popen(cmd)

    def _run_with_tor(self, command: str, args: List[str]) -> subprocess.Popen:
        """Exécute une commande via Tor"""

        # Pour les outils réseau, utiliser torsocks
        if command in ['curl', 'wget', 'nmap', 'nikto']:
            return subprocess.Popen(['torsocks', command] + args)
        else:
            # Pour autres outils, essayer torsocks aussi
            try:
                return subprocess.Popen(['torsocks', command] + args)
            except FileNotFoundError:
                # Fallback sans torsocks (risqué)
                print("⚠️ torsocks non disponible, exécution directe")
                return subprocess.Popen([command] + args)

    def _check_tor_status(self) -> bool:
        """Vérifie si Tor fonctionne"""
        try:
            result = subprocess.run(
                ['torsocks', 'curl', '-s', 'https://check.torproject.org/api/ip'],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0 and '"IsTor":true' in result.stdout
        except:
            return False

    def get_network_status(self) -> Dict:
        """État du réseau et anonymat"""
        status = {
            'tor_active': self._check_tor_status(),
            'direct_ip': None,
            'tor_ip': None
        }

        # IP directe
        try:
            import requests
            response = requests.get('https://api.ipify.org', timeout=3)
            status['direct_ip'] = response.text.strip()
        except:
            pass

        # IP Tor
        if status['tor_active']:
            try:
                result = subprocess.run(
                    ['torsocks', 'curl', '-s', 'https://api.ipify.org'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    status['tor_ip'] = result.stdout.strip()
            except:
                pass

        return status

# Instance globale
proxy_manager = SelectiveProxyManager()

# Fonctions utilitaires
def run_anon(command: str, *args):
    """Exécute une commande anonymement"""
    return proxy_manager.run_command(command, list(args), force_anon=True)

def run_normal(command: str, *args):
    """Exécute une commande normalement"""
    return proxy_manager.run_command(command, list(args), force_normal=True)

def browser_anon(browser='chrome', url=None):
    """Lance un navigateur anonyme"""
    return proxy_manager.launch_browser_anon(browser, url)

def network_status():
    """Affiche l'état du réseau"""
    status = proxy_manager.get_network_status()

    print("🌐 ÉTAT RÉSEAU:")
    print(f"   Tor actif: {'✅' if status['tor_active'] else '❌'}")
    print(f"   IP directe: {status['direct_ip'] or 'N/A'}")
    print(f"   IP Tor: {status['tor_ip'] or 'N/A'}")

    if status['direct_ip'] and status['tor_ip'] and status['direct_ip'] != status['tor_ip']:
        print("   🛡️ Anonymat: ✅ ACTIF")
    elif status['tor_active']:
        print("   ⚠️ Anonymat: Tor actif mais IPs identiques")
    else:
        print("   ❌ Anonymat: Non disponible")

# Test rapide
if __name__ == "__main__":
    print("🛡️ TEST SELECTIVE PROXY MANAGER")
    print("=" * 40)

    # État réseau
    network_status()

    print("\n🧪 TESTS DE ROUTAGE:")

    # Test routage automatique
    test_commands = [
        ("nmap -sV scanme.nmap.org", "anonyme"),
        ("apt update", "normal"),
        ("curl https://api.ipify.org", "anonyme"),
        ("python --version", "normal")
    ]

    for cmd, expected in test_commands:
        parts = cmd.split()
        should_anon = proxy_manager.should_anonymize(cmd)
        result = "ANONYME" if should_anon else "NORMAL"
        status = "✅" if (should_anon and expected == "anonyme") or (not should_anon and expected == "normal") else "❌"
        print(f"   {status} {cmd} → {result}")