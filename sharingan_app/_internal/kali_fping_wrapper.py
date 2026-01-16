"""
fping Wrapper for Sharingan OS
Fast ping scanner for network discovery
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.fping")


class FpingResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 hosts_alive: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.hosts_alive = hosts_alive
        self.error = error


def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'fping'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False


def get_version() -> str:
    try:
        result = subprocess.run(['fping', '--version'], capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def scan_network(network: str = "192.168.1.0/24", count: int = 1,
                 timeout: int = 500) -> FpingResult:
    cmd = ['fping', '-a', '-g']

    if '/' in network:
        cmd.append(network)
    else:
        cmd.append(network)

    cmd.extend(['-c', str(count), '-t', str(timeout)])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        hosts = output.count('\n') + 1
        return FpingResult(success=True, command=' '.join(cmd),
                          output=output[:3000], hosts_alive=hosts)
    except subprocess.TimeoutExpired:
        return FpingResult(success=False, command=' '.join(cmd),
                          error="Scan timeout")
    except Exception as e:
        return FpingResult(success=False, command=' '.join(cmd), error=str(e))


def ping_host(host: str, count: int = 1) -> FpingResult:
    cmd = ['fping', '-a', host, '-c', str(count)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        alive = 'alive' in output.lower() or result.returncode == 0
        return FpingResult(success=True, command=' '.join(cmd),
                          output=output[:1000], hosts_alive=1 if alive else 0)
    except Exception as e:
        return FpingResult(success=False, command=' '.join(cmd), error=str(e))


def get_help() -> str:
    try:
        result = subprocess.run(['fping', '-h'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()

    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}

    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}

    if 'scan' in query_lower or 'discover' in query_lower or 'trouve' in query_lower:
        net_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})', query)
        if net_match:
            network = net_match.group(1)
            result = scan_network(network=network)
        else:
            result = scan_network()

        return {'action': 'scan', 'success': result.success,
               'network': result.command, 'hosts_alive': result.hosts_alive,
               'output': result.output[:500]}

    if 'ping' in query_lower or 'test' in query_lower or 'host' in query_lower:
        host_match = re.search(r'([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', query)
        if host_match:
            host = host_match.group(1)
            result = ping_host(host)
            return {'action': 'ping', 'success': result.success,
                   'host': host, 'alive': result.hosts_alive > 0,
                   'output': result.output}

        return {'action': 'ping', 'success': False,
               'error': 'Host required', 'example': 'ping 192.168.1.1'}

    return {'success': False, 'error': 'Command not recognized',
           'example': 'scan 192.168.1.0/24'}


def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'fping',
        'description': 'Fast ping scanner for network discovery',
        'category': 'recon',
        'supported_queries': [
            'quelle est la version de fping',
            'scan 192.168.1.0/24',
            'ping 192.168.1.1',
            'trouve les hosts actifs du réseau',
            'fping help'
        ],
        'warning': 'Use for network discovery on authorized networks.',
        'features': ['network scan', 'ping host', 'alive check']
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("fping Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'scan':
        network = sys.argv[2] if len(sys.argv) > 2 else "192.168.1.0/24"
        result = scan_network(network)
        print(f"Network: {network}")
        print(f"Hosts alive: {result.hosts_alive}")
        print(result.output[:500])
    elif cmd == 'ping':
        host = sys.argv[2] if len(sys.argv) > 2 else "localhost"
        result = ping_host(host)
        print(f"Host: {host}")
        print(f"Alive: {result.hosts_alive > 0}")
        print(result.output)
    elif cmd == 'help':
        print(get_help())
