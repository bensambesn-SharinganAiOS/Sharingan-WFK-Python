#!/usr/bin/env python3
"""
SHARINGAN VPN/TOR INTEGRATION MODULE
Module de gestion des VPN et Tor pour anonymisation réseau
Intègre Tor Network, OpenVPN, WireGuard dans les workflows Sharingan
"""

import sys
import os
import time
import subprocess
import threading
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vpn_tor_integration")

class VPNProvider(Enum):
    """Fournisseurs VPN supportés"""
    OPENVPN = "openvpn"
    WIREGUARD = "wireguard"
    EXPRESSVPN = "expressvpn"
    NORDVPN = "nordvpn"
    MULLVAD = "mullvad"

class TorMode(Enum):
    """Modes Tor disponibles"""
    STANDARD = "standard"
    BRIDGE = "bridge"
    OBFS4 = "obfs4"
    MEEK = "meek"

@dataclass
class VPNConnection:
    """Connexion VPN"""
    provider: VPNProvider
    config_file: Optional[str] = None
    credentials: Optional[Dict[str, str]] = None
    server: Optional[str] = None
    country: Optional[str] = None
    active: bool = False
    connected_at: Optional[float] = None

@dataclass
class TorConnection:
    """Connexion Tor"""
    mode: TorMode
    bridges: List[str] = field(default_factory=list)
    control_port: int = 9051
    socks_port: int = 9050
    active: bool = False
    connected_at: Optional[float] = None

class VPNManager:
    """
    Gestionnaire de connexions VPN
    """

    def __init__(self):
        self.connections: Dict[str, VPNConnection] = {}
        self.active_connection: Optional[str] = None

        # Vérifier les outils disponibles
        self.openvpn_available = self._check_tool("openvpn")
        self.wireguard_available = self._check_tool("wg")

        logger.info(" VPN Manager initialized")

    def _check_tool(self, tool: str) -> bool:
        """Vérifier si un outil est disponible"""
        try:
            result = subprocess.run([tool, "--version" if tool != "wg" else "--help"],
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def add_openvpn_connection(self, name: str, config_file: str,
                             credentials: Optional[Dict[str, str]] = None) -> bool:
        """Ajouter une connexion OpenVPN"""
        if not self.openvpn_available:
            logger.error("OpenVPN not available")
            return False

        if not Path(config_file).exists():
            logger.error(f"Config file not found: {config_file}")
            return False

        connection = VPNConnection(
            provider=VPNProvider.OPENVPN,
            config_file=config_file,
            credentials=credentials
        )

        self.connections[name] = connection
        logger.info(f"OpenVPN connection '{name}' added")
        return True

    def add_wireguard_connection(self, name: str, config_file: str) -> bool:
        """Ajouter une connexion WireGuard"""
        if not self.wireguard_available:
            logger.error("WireGuard not available")
            return False

        if not Path(config_file).exists():
            logger.error(f"Config file not found: {config_file}")
            return False

        connection = VPNConnection(
            provider=VPNProvider.WIREGUARD,
            config_file=config_file
        )

        self.connections[name] = connection
        logger.info(f"WireGuard connection '{name}' added")
        return True

    def connect_vpn(self, name: str) -> bool:
        """Se connecter à un VPN"""
        if name not in self.connections:
            logger.error(f"Connection '{name}' not found")
            return False

        connection = self.connections[name]

        try:
            if connection.provider == VPNProvider.OPENVPN:
                return self._connect_openvpn(connection)
            elif connection.provider == VPNProvider.WIREGUARD:
                return self._connect_wireguard(connection)
            else:
                logger.error(f"Unsupported VPN provider: {connection.provider}")
                return False

        except Exception as e:
            logger.error(f"VPN connection failed: {e}")
            return False

    def _connect_openvpn(self, connection: VPNConnection) -> bool:
        """Connecter via OpenVPN"""
        cmd = ["sudo", "openvpn", "--config", connection.config_file]

        if connection.credentials:
            # Créer un fichier d'auth temporaire
            auth_file = f"/tmp/sharingan_vpn_auth_{int(time.time())}"
            with open(auth_file, 'w') as f:
                f.write(f"{connection.credentials.get('username', '')}\n")
                f.write(f"{connection.credentials.get('password', '')}\n")

            cmd.extend(["--auth-user-pass", auth_file])

            # Nettoyer le fichier d'auth après
            def cleanup_auth():
                time.sleep(5)
                try:
                    os.remove(auth_file)
                except:
                    pass

            threading.Thread(target=cleanup_auth, daemon=True).start()

        # Lancer OpenVPN en arrière-plan
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Attendre que la connexion s'établisse
        time.sleep(10)

        if process.poll() is None:  # Processus toujours actif
            connection.active = True
            connection.connected_at = time.time()
            self.active_connection = connection.config_file
            logger.info("OpenVPN connection established")
            return True
        else:
            logger.error("OpenVPN connection failed")
            return False

    def _connect_wireguard(self, connection: VPNConnection) -> bool:
        """Connecter via WireGuard"""
        try:
            # Activer l'interface WireGuard
            result = subprocess.run(["sudo", "wg-quick", "up", connection.config_file],
                                  capture_output=True, text=True, timeout=15)

            if result.returncode == 0:
                connection.active = True
                connection.connected_at = time.time()
                self.active_connection = connection.config_file
                logger.info("WireGuard connection established")
                return True
            else:
                logger.error(f"WireGuard connection failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("WireGuard connection timeout")
            return False

    def disconnect_vpn(self) -> bool:
        """Se déconnecter du VPN actif"""
        if not self.active_connection:
            logger.info("No active VPN connection")
            return True

        # Trouver la connexion active
        active_conn = None
        for name, conn in self.connections.items():
            if conn.config_file == self.active_connection:
                active_conn = conn
                break

        if not active_conn:
            logger.error("Active connection not found in connections list")
            return False

        try:
            if active_conn.provider == VPNProvider.OPENVPN:
                # Tuer le processus OpenVPN
                result = subprocess.run(["sudo", "pkill", "-f", "openvpn"],
                                      capture_output=True, timeout=10)
            elif active_conn.provider == VPNProvider.WIREGUARD:
                # Désactiver l'interface WireGuard
                result = subprocess.run(["sudo", "wg-quick", "down", active_conn.config_file],
                                      capture_output=True, timeout=10)

            if result.returncode == 0:
                active_conn.active = False
                self.active_connection = None
                logger.info("VPN disconnected successfully")
                return True
            else:
                logger.error("VPN disconnection failed")
                return False

        except Exception as e:
            logger.error(f"VPN disconnection error: {e}")
            return False

    def get_vpn_status(self) -> Dict[str, Any]:
        """Obtenir le statut des connexions VPN"""
        return {
            "connections": {
                name: {
                    "provider": conn.provider.value,
                    "active": conn.active,
                    "connected_at": conn.connected_at,
                    "server": conn.server,
                    "country": conn.country
                }
                for name, conn in self.connections.items()
            },
            "active_connection": self.active_connection,
            "tools_available": {
                "openvpn": self.openvpn_available,
                "wireguard": self.wireguard_available
            }
        }

class TorManager:
    """
    Gestionnaire de connexions Tor
    """

    def __init__(self):
        self.connection: Optional[TorConnection] = None
        self.tor_available = self._check_tor()
        self.torsocks_available = self._check_tool("torsocks")

        # Configuration Tor par défaut
        self.torrc_path = "/etc/tor/torrc"
        self.tor_data_dir = "/var/lib/tor"

        logger.info(" Tor Manager initialized")

    def _check_tor(self) -> bool:
        """Vérifier si Tor est disponible"""
        try:
            result = subprocess.run(["tor", "--version"], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def _check_tool(self, tool: str) -> bool:
        """Vérifier si un outil est disponible"""
        try:
            result = subprocess.run(["which", tool], capture_output=True, timeout=3)
            return result.returncode == 0
        except:
            return False

    def start_tor(self, mode: TorMode = TorMode.STANDARD,
                  bridges: Optional[List[str]] = None) -> bool:
        """Démarrer Tor"""
        if not self.tor_available:
            logger.error("Tor not available")
            return False

        try:
            # Arrêter Tor s'il est déjà en cours
            self.stop_tor()

            # Configuration selon le mode
            config = self._generate_tor_config(mode, bridges or [])

            # Écrire la configuration
            with open("/tmp/torrc_sharingan", 'w') as f:
                f.write(config)

            # Démarrer Tor
            cmd = ["tor", "-f", "/tmp/torrc_sharingan"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Attendre que Tor se connecte
            time.sleep(15)

            if process.poll() is None:  # Processus toujours actif
                self.connection = TorConnection(
                    mode=mode,
                    bridges=bridges or [],
                    active=True,
                    connected_at=time.time()
                )
                logger.info(f"Tor started in {mode.value} mode")
                return True
            else:
                logger.error("Tor failed to start")
                return False

        except Exception as e:
            logger.error(f"Tor start failed: {e}")
            return False

    def _generate_tor_config(self, mode: TorMode, bridges: List[str]) -> str:
        """Générer la configuration Tor"""
        config = """
# Sharingan Tor Configuration
DataDirectory /tmp/tor-data-sharingan
ControlPort 9051
CookieAuthentication 1
ExitPolicy reject *:*
"""

        if mode == TorMode.BRIDGE:
            config += "\nUseBridges 1\n"
            for bridge in bridges:
                config += f"Bridge {bridge}\n"

        elif mode == TorMode.OBFS4:
            config += """
UseBridges 1
ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy
"""
            for bridge in bridges:
                config += f"Bridge {bridge}\n"

        return config

    def stop_tor(self) -> bool:
        """Arrêter Tor"""
        try:
            result = subprocess.run(["sudo", "pkill", "-f", "tor"], capture_output=True, timeout=10)

            if self.connection:
                self.connection.active = False

            logger.info("Tor stopped")
            return True

        except Exception as e:
            logger.error(f"Tor stop failed: {e}")
            return False

    def check_tor_circuit(self) -> Dict[str, Any]:
        """Vérifier le circuit Tor"""
        if not self.connection or not self.connection.active:
            return {"status": "inactive"}

        try:
            # Utiliser stem pour vérifier le circuit si disponible
            import stem
            from stem import Signal
            from stem.control import Controller

            with Controller.from_port(port=self.connection.control_port) as controller:
                controller.authenticate()

                # Obtenir les circuits
                circuits = []
                for circ in controller.get_circuits():
                    path = []
                    for fingerprint, nickname in circ.path:
                        path.append(nickname)
                    circuits.append(path)

                return {
                    "status": "active",
                    "circuits": circuits,
                    "guards": len(controller.get_network_statuses())
                }

        except ImportError:
            # Fallback sans stem
            return {"status": "active", "circuits": "unknown (stem not available)"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def torify_command(self, command: str) -> Tuple[int, str, str]:
        """Exécuter une commande via Tor"""
        if not self.torsocks_available:
            return (1, "", "torsocks not available")

        if not self.connection or not self.connection.active:
            return (1, "", "Tor not active")

        try:
            full_cmd = f"torsocks {command}"
            result = subprocess.run(full_cmd.split(), capture_output=True, text=True, timeout=60)  # SECURITY: Removed shell=True

            return (result.returncode, result.stdout, result.stderr)

        except subprocess.TimeoutExpired:
            return (124, "", "Command timed out")
        except Exception as e:
            return (1, "", f"Error: {str(e)}")

    def get_tor_status(self) -> Dict[str, Any]:
        """Obtenir le statut de Tor"""
        circuit_info = self.check_tor_circuit()

        return {
            "available": self.tor_available,
            "torsocks_available": self.torsocks_available,
            "connection": {
                "active": self.connection.active if self.connection else False,
                "mode": self.connection.mode.value if self.connection else None,
                "connected_at": self.connection.connected_at if self.connection else None,
                "bridges": len(self.connection.bridges) if self.connection else 0
            } if self.connection else None,
            "circuit": circuit_info
        }

class VPNTorIntegration:
    """
    Intégration complète VPN/Tor pour Sharingan
    """

    def __init__(self):
        self.vpn_manager = VPNManager()
        self.tor_manager = TorManager()

        logger.info("🌐 VPN/Tor Integration initialized")

    def setup_openvpn_connection(self, name: str, config_file: str,
                               username: Optional[str] = None,
                               password: Optional[str] = None) -> bool:
        """Configurer une connexion OpenVPN"""
        credentials = None
        if username and password:
            credentials = {"username": username, "password": password}

        return self.vpn_manager.add_openvpn_connection(name, config_file, credentials)

    def setup_wireguard_connection(self, name: str, config_file: str) -> bool:
        """Configurer une connexion WireGuard"""
        return self.vpn_manager.add_wireguard_connection(name, config_file)

    def start_vpn(self, connection_name: str) -> bool:
        """Démarrer une connexion VPN"""
        return self.vpn_manager.connect_vpn(connection_name)

    def stop_vpn(self) -> bool:
        """Arrêter la connexion VPN"""
        return self.vpn_manager.disconnect_vpn()

    def start_tor(self, mode: TorMode = TorMode.STANDARD,
                  bridges: Optional[List[str]] = None) -> bool:
        """Démarrer Tor"""
        return self.tor_manager.start_tor(mode, bridges)

    def stop_tor(self) -> bool:
        """Arrêter Tor"""
        return self.tor_manager.stop_tor()

    def run_through_tor(self, command: str) -> Tuple[int, str, str]:
        """Exécuter une commande via Tor"""
        return self.tor_manager.torify_command(command)

    def get_network_status(self) -> Dict[str, Any]:
        """Obtenir le statut réseau complet"""
        return {
            "vpn": self.vpn_manager.get_vpn_status(),
            "tor": self.tor_manager.get_tor_status(),
            "timestamp": time.time()
        }

    def create_anonymized_workflow(self, target_command: str) -> Dict[str, Any]:
        """
        Créer un workflow d'anonymisation complet

        Args:
            target_command: Commande à exécuter de manière anonymisée

        Returns:
            Résultat du workflow
        """
        workflow_result = {
            "steps": [],
            "success": False,
            "target_command": target_command,
            "anonymization_level": "none"
        }

        try:
            # Étape 1: Démarrer Tor
            workflow_result["steps"].append({"step": "start_tor", "status": "running"})
            tor_started = self.start_tor()
            workflow_result["steps"][-1]["status"] = "success" if tor_started else "failed"

            if tor_started:
                workflow_result["anonymization_level"] = "tor"

                # Étape 2: Exécuter la commande via Tor
                workflow_result["steps"].append({"step": "execute_command", "status": "running"})
                returncode, stdout, stderr = self.run_through_tor(target_command)

                workflow_result["steps"][-1]["status"] = "success"
                workflow_result["command_result"] = {
                    "returncode": returncode,
                    "stdout": stdout,
                    "stderr": stderr
                }

                if returncode == 0:
                    workflow_result["success"] = True

                # Étape 3: Nettoyer (optionnel)
                workflow_result["steps"].append({"step": "cleanup", "status": "completed"})

        except Exception as e:
            workflow_result["error"] = str(e)
            logger.error(f"Anonymous workflow failed: {e}")

        return workflow_result

# === FONCTIONS GLOBALES ===

_vpn_tor_integration = None

def get_vpn_tor_integration() -> VPNTorIntegration:
    """Singleton pour l'intégration VPN/Tor"""
    global _vpn_tor_integration
    if _vpn_tor_integration is None:
        _vpn_tor_integration = VPNTorIntegration()
    return _vpn_tor_integration

if __name__ == "__main__":
    print("🌐 SHARINGAN VPN/TOR INTEGRATION")
    print("=" * 50)

    integration = get_vpn_tor_integration()

    print("🔍 STATUT ACTUEL:")

    # Statut VPN
    vpn_status = integration.vpn_manager.get_vpn_status()
    print(f"• OpenVPN disponible: {'✅' if vpn_status['tools_available']['openvpn'] else '❌'}")
    print(f"• WireGuard disponible: {'✅' if vpn_status['tools_available']['wireguard'] else '❌'}")
    print(f"• Connexions configurées: {len(vpn_status['connections'])}")

    # Statut Tor
    tor_status = integration.tor_manager.get_tor_status()
    print(f"• Tor disponible: {'✅' if tor_status['available'] else '❌'}")
    print(f"• Torsocks disponible: {'✅' if tor_status['torsocks_available'] else '❌'}")
    print(f"• Tor actif: {'✅' if tor_status.get('connection', {}).get('active') else '❌'}")

    print()
    print("🧪 TESTS D'INTÉGRATION:")

    # Test Tor si disponible
    if tor_status['available']:
        print("• Test Tor...")
        tor_started = integration.start_tor()
        print(f"  Démarrage Tor: {'✅' if tor_started else '❌'}")

        if tor_started:
            time.sleep(5)  # Attendre la connexion

            # Test commande via Tor
            print("  Test commande via Tor...")
            returncode, stdout, stderr = integration.run_through_tor("curl -s https://check.torproject.org | grep -o 'Congratulations'")
            if returncode == 0 and "Congratulations" in stdout:
                print("  ✅ Commande Tor réussie")
            else:
                print("  ❌ Commande Tor échouée")

            # Arrêter Tor
            integration.stop_tor()
            print("  ✅ Tor arrêté")

    print()
    print("💡 UTILISATION RECOMMANDÉE:")
    print("• Tor pour anonymisation réseau et accès .onion")
    print("• OpenVPN pour VPN commercial (NordVPN, ExpressVPN)")
    print("• WireGuard pour VPN auto-hébergé haute performance")
    print("• Combinaison Tor + VPN pour anonymisation maximale")

    print()
    print("🚀 EXEMPLE D'USAGE:")
    print("# Démarrer Tor")
    print("integration.start_tor()")
    print()
    print("# Exécuter une commande de manière anonymisée")
    print("result = integration.run_through_tor('nmap -sS target.com')")
    print()
    print("# Créer un workflow d'anonymisation complet")
    print("workflow = integration.create_anonymized_workflow('your_command_here')")

    print("=" * 50)