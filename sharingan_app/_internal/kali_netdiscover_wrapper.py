"""
netdiscover Wrapper for Sharingan OS
Active/passive ARP reconnaissance tool
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.netdiscover")


class NetdiscoverResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 hosts_found: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.hosts_found = hosts_found
        self.error = error


def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'netdiscover'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False


def get_version() -> str:
    try:
        result = subprocess.run(['netdiscover', '-h'], capture_output=True, text=True, timeout=10)
        first_line = result.stdout.split('\n')[0]
        return first_line.strip()
    except Exception as e:
        return f"Error: {e}"


def scan_network(network: str = "192.168.1.0/24", passive: bool = False,
                 count: int = 3) -> NetdiscoverResult:
    cmd = ['netdiscover']

    if passive:
        cmd.extend(['-p'])
    else:
        cmd.extend(['-i', 'eth0', '-r', network, '-c', str(count)])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        hosts = output.count(':') + output.lower().count('host')
        return NetdiscoverResult(success=True, command=' '.join(cmd),
                                output=output[:3000], hosts_found=hosts)
    except subprocess.TimeoutExpired:
        return NetdiscoverResult(success=False, command=' '.join(cmd),
                                error="Scan timeout")
    except Exception as e:
        return NetdiscoverResult(success=False, command=' '.join(cmd), error=str(e))


def passive_scan(duration: int = 30) -> NetdiscoverResult:
    cmd = ['netdiscover', '-p', '-T', str(duration)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 10)
        output = result.stdout + result.stderr
        return NetdiscoverResult(success=True, command=' '.join(cmd),
                                output=output[:3000])
    except Exception as e:
        return NetdiscoverResult(success=False, command=' '.join(cmd), error=str(e))


def get_help() -> str:
    try:
        result = subprocess.run(['netdiscover', '-h'], capture_output=True, text=True, timeout=10)
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
        passive = 'passive' in query_lower or 'silencieu' in query_lower

        if net_match:
            network = net_match.group(1)
            count = 3 if 'quick' in query_lower else 5
            result = scan_network(network=network, passive=passive, count=count)
        else:
            result = scan_network(passive=passive)

        return {'action': 'scan', 'success': result.success,
               'network': result.command, 'hosts_found': result.hosts_found,
               'output': result.output[:500]}

    if 'passive' in query_lower:
        duration = 30
        dur_match = re.search(r'(\d+)\s*(?:seconde|second|s)', query)
        if dur_match:
            duration = int(dur_match.group(1))
        result = passive_scan(duration=duration)
        return {'action': 'passive_scan', 'success': result.success,
               'duration': duration, 'output': result.output[:500]}

    return {'success': False, 'error': 'Command not recognized',
           'example': 'scan network 192.168.1.0/24'}


def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'netdiscover',
        'description': 'ARP network discovery tool',
        'category': 'recon',
        'supported_queries': [
            'quelle est la version de netdiscover',
            'scan 192.168.1.0/24',
            'netdiscover passive',
            'trouve les hosts du réseau 192.168.1.0/24',
            'netdiscover help'
        ],
        'warning': 'Use for network reconnaissance on authorized networks.',
        'features': ['active scan', 'passive scan', 'ARP discovery']
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("netdiscover Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'scan':
        network = sys.argv[2] if len(sys.argv) > 2 else "192.168.1.0/24"
        result = scan_network(network)
        print(f"Network: {network}")
        print(f"Hosts found: {result.hosts_found}")
        print(result.output[:500])
    elif cmd == 'passive':
        result = passive_scan()
        print("Passive scan results:")
        print(result.output[:500])
    elif cmd == 'help':
        print(get_help())
