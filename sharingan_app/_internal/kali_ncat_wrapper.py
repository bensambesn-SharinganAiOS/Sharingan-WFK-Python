"""
ncat Wrapper for Sharingan OS
Netcat modern replacement for data sniffing and connections
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.ncat")


class NcatResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.error = error


def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'ncat'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False


def get_version() -> str:
    try:
        result = subprocess.run(['ncat', '--version'], capture_output=True, text=True, timeout=10)
        first_line = result.stdout.split('\n')[0]
        return first_line.strip()
    except Exception as e:
        return f"Error: {e}"


def listen(port: int, protocol: str = "tcp", ssl: bool = False,
           exec_cmd: str = None) -> NcatResult:
    cmd = ['ncat', '-l', '-p', str(port)]

    if protocol == "udp":
        cmd.append('-u')
    if ssl:
        cmd.extend(['--ssl'])
    if exec_cmd:
        cmd.extend(['--exec', exec_cmd])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return NcatResult(success=True, command=' '.join(cmd), output=result.stdout)
    except Exception as e:
        return NcatResult(success=False, command=' '.join(cmd), error=str(e))


def connect(host: str, port: int, ssl: bool = False) -> NcatResult:
    cmd = [host, str(port)]
    if ssl:
        cmd.insert(0, '--ssl')

    try:
        result = subprocess.run(['ncat'] + cmd, capture_output=True, text=True, timeout=10)
        return NcatResult(success=True, command=' '.join(cmd), output=result.stdout)
    except Exception as e:
        return NcatResult(success=False, command=' '.join(cmd), error=str(e))


def scan_ports(host: str, ports: str = "1-1000") -> NcatResult:
    cmd = ['ncat', '-z', host, ports]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return NcatResult(success=True, command=' '.join(cmd), output=result.stdout)
    except Exception as e:
        return NcatResult(success=False, command=' '.join(cmd), error=str(e))


def get_help() -> str:
    try:
        result = subprocess.run(['ncat', '--help'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()

    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}

    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}

    if 'listen' in query_lower or 'ecoute' in query_lower or 'port' in query_lower:
        port_match = re.search(r'port\s+(\d+)', query)
        if port_match:
            port = int(port_match.group(1))
            ssl = 'ssl' in query_lower or 'tls' in query_lower
            result = listen(port=port, ssl=ssl)
            return {'action': 'listen', 'success': result.success,
                   'port': port, 'output': result.output}

        return {'action': 'listen', 'success': False,
               'error': 'Port required', 'example': 'listen port 4444'}

    if 'connect' in query_lower or 'connexion' in query_lower:
        host_match = re.search(r'([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', query)
        port_match = re.search(r'port\s+(\d+)', query)
        if host_match and port_match:
            host = host_match.group(1)
            port = int(port_match.group(1))
            ssl = 'ssl' in query_lower
            result = connect(host=host, port=port, ssl=ssl)
            return {'action': 'connect', 'success': result.success,
                   'host': host, 'port': port, 'output': result.output}

        return {'action': 'connect', 'success': False,
               'error': 'Host and port required', 'example': 'connect to 192.168.1.1 port 4444'}

    if 'scan' in query_lower or 'ports' in query_lower:
        host_match = re.search(r'([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', query)
        if host_match:
            host = host_match.group(1)
            ports = "1-1000"
            port_match = re.search(r'(\d+-\d+)', query)
            if port_match:
                ports = port_match.group(1)
            result = scan_ports(host=host, ports=ports)
            return {'action': 'scan', 'success': result.success,
                   'host': host, 'ports': ports, 'output': result.output}

        return {'action': 'scan', 'success': False,
               'error': 'Host required', 'example': 'scan ports of 192.168.1.1'}

    return {'success': False, 'error': 'Command not recognized',
           'example': 'listen port 4444'}


def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'ncat',
        'description': 'Netcat modern replacement',
        'category': 'network',
        'supported_queries': [
            'quelle est la version de ncat',
            'listen port 4444',
            'connect to 192.168.1.1 port 4444',
            'scan ports of example.com',
            'ncat help'
        ],
        'warning': 'Use for legitimate network administration and testing only.',
        'features': ['listen on port', 'connect to host', 'port scan', 'SSL support']
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("ncat Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'listen':
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 4444
        result = listen(port)
        print(f"Listening on port: {port}")
        print(result.output)
    elif cmd == 'connect':
        if len(sys.argv) > 3:
            result = connect(sys.argv[2], int(sys.argv[3]))
            print(f"Connecting to {sys.argv[2]}:{sys.argv[3]}")
            print(result.output)
    elif cmd == 'scan':
        host = sys.argv[2] if len(sys.argv) > 2 else "localhost"
        result = scan_ports(host)
        print(f"Scanning {host}")
        print(result.output)
    elif cmd == 'help':
        print(get_help())
