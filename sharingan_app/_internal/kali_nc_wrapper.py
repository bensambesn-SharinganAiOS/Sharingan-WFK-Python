"""
netcat (nc) Wrapper for Sharingan OS
Real network utility integration
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger("sharingan.netcat")

class NetcatResult:
    def __init__(self, success: bool, command: str = "", output: str = "", 
                 error: Optional[str] = None, port: Optional[int] = None,
                 target: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.error = error
        self.port = port
        self.target = target

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'nc'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def port_scan(target: str, ports: str = "1-1024", timeout: int = 3) -> NetcatResult:
    cmd = ['nc', '-z', '-w', str(timeout), target, ports]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return NetcatResult(success=True, command=' '.join(cmd), output=result.stdout + result.stderr, target=target)
    except Exception as e:
        return NetcatResult(success=False, command=' '.join(cmd), error=str(e))

def banner_grab(target: str, port: int, timeout: int = 5) -> NetcatResult:
    cmd = ['nc', '-w', str(timeout), target, str(port)]
    try:
        result = subprocess.run(cmd, input='HEAD / HTTP/1.0\r\n\r\n', capture_output=True, text=True, timeout=10)
        return NetcatResult(success=True, command=' '.join(cmd), output=result.stdout, port=port, target=target)
    except Exception as e:
        return NetcatResult(success=False, command=' '.join(cmd), error=str(e))

def tcp_connect(target: str, port: int, data: Optional[str] = None, timeout: int = 5) -> NetcatResult:
    cmd = ['nc', '-w', str(timeout), target, str(port)]
    try:
        if data:
            result = subprocess.run(cmd, input=data, capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return NetcatResult(success=True, command=' '.join(cmd), output=result.stdout + result.stderr, port=port, target=target)
    except Exception as e:
        return NetcatResult(success=False, command=' '.join(cmd), error=str(e))

def listen(port: int, timeout: int = 5) -> NetcatResult:
    cmd = ['nc', '-l', '-p', str(port), '-w', str(timeout)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        return NetcatResult(success=True, command=' '.join(cmd), output=result.stdout, port=port)
    except Exception as e:
        return NetcatResult(success=False, command=' '.join(cmd), error=str(e))

def check_port(target: str, port: int, timeout: int = 3) -> Tuple[bool, str]:
    cmd = ['nc', '-z', '-w', str(timeout), target, str(port)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True, f"Port {port} is OPEN on {target}"
        return False, f"Port {port} is CLOSED on {target}"
    except Exception as e:
        return False, f"Error: {e}"

def check_service(target: str, port: int, timeout: int = 3) -> Dict[str, Any]:
    is_open, message = check_port(target, port, timeout)
    result = {'target': target, 'port': port, 'status': 'open' if is_open else 'closed', 'message': message}
    if is_open:
        banner = banner_grab(target, port, timeout)
        if banner.success and banner.output:
            result['banner'] = banner.output[:200]
    return result

def transfer_file(target: str, port: int, file_path: str, timeout: int = 30) -> NetcatResult:
    if not os.path.exists(file_path):
        return NetcatResult(success=False, error=f"File not found: {file_path}")
    cmd = ['nc', '-w', str(timeout), target, str(port)]
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
        result = subprocess.run(cmd, input=file_data, capture_output=True, text=True, timeout=timeout + 5)
        return NetcatResult(success=True, command=' '.join(cmd), output=f"File transferred: {len(file_data)} bytes", port=port, target=target)
    except Exception as e:
        return NetcatResult(success=False, command=' '.join(cmd), error=str(e))

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    target = None
    port = None
    
    # Better target pattern - supports localhost, IPs, domains
    target_match = re.search(r'(?:de|sur|at|to|of)\s+([a-zA-Z0-9][a-zA-Z0-9.-]*|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', query_lower)
    if target_match:
        target = target_match.group(1)
    
    # Port patterns
    port_match = re.search(r'port\s*:?\s*(\d+)', query_lower)
    if port_match:
        port = int(port_match.group(1))
    
    # Check for scan
    if 'scan' in query_lower or 'scanne' in query_lower:
        if not target:
            return {'success': False, 'error': 'No target specified', 'example': 'scan les ports de example.com'}
        ports = "1-1024"
        ports_match = re.search(r'(\d+-\d+)', query)
        if ports_match:
            ports = ports_match.group(1)
        result = port_scan(target, ports)
        return {'action': 'port_scan', 'success': result.success, 'target': target, 'ports_range': ports, 'output': result.output, 'error': result.error}
    
    # Check for port verification
    if ('port' in query_lower or 'check' in query_lower or 'vérifie' in query_lower or 'ouvre' in query_lower) and target:
        if not port:
            return {'success': False, 'error': 'Port not specified', 'example': 'vérifie le port 80 de example.com'}
        is_open, message = check_port(target, port)
        return {'action': 'check_port', 'success': True, 'target': target, 'port': port, 'status': 'open' if is_open else 'closed', 'message': message}
    
    # Check for banner/service
    if 'banner' in query_lower or 'service' in query_lower:
        if not target or not port:
            return {'success': False, 'error': 'Target and port required', 'example': 'banner de example.com port 80'}
        service = check_service(target, port)
        return {'action': 'service_check', 'success': True, 'service': service}
    
    # Check for connect
    if 'connect' in query_lower or 'connexion' in query_lower:
        if not target or not port:
            return {'success': False, 'error': 'Target and port required'}
        result = tcp_connect(target, port)
        return {'action': 'connect', 'success': result.success, 'target': target, 'port': port, 'output': result.output, 'error': result.error}
    
    # Check for listen
    if 'listen' in query_lower or 'écoute' in query_lower or 'écouter' in query_lower:
        if not port:
            port = 4444
        result = listen(port)
        return {'action': 'listen', 'success': result.success, 'port': port, 'output': result.output, 'error': result.error}
    
    # Check for file transfer
    if 'file' in query_lower or 'transfert' in query_lower:
        file_match = re.search(r'([/\w]+\.\w+)', query)
        if file_match:
            file_path = file_match.group(1)
            if target and port:
                result = transfer_file(target, port, file_path)
                return {'action': 'transfer', 'success': result.success, 'file': file_path, 'target': target, 'port': port, 'output': result.output, 'error': result.error}
            else:
                return {'success': False, 'error': 'Target and port required for transfer'}
        return {'success': False, 'error': 'No file specified'}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'scan les ports de example.com ou vérifie le port 80 de example.com'}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'nc',
        'description': 'Network utility (netcat)',
        'category': 'network',
        'supported_queries': [
            'scan les ports de example.com',
            'scan ports 1-100 de 192.168.1.1',
            'vérifie le port 80 de example.com',
            'port 22 de localhost est ouvert',
            'banner de example.com port 22',
            'connecte à example.com port 80',
            'écoute sur le port 4444'
        ],
        'common_ports': [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 5432, 8080]
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("netcat (nc) Wrapper for Sharingan OS")
        print(f"Available: {is_available()}")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == 'scan':
        target = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
        ports = sys.argv[3] if len(sys.argv) > 3 else '1-1024'
        result = port_scan(target, ports)
        print(f"Scan: {target}:{ports}")
        print(f"Success: {result.success}")
        print(f"Output: {result.output}")
    
    elif cmd == 'check':
        target = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 80
        is_open, message = check_port(target, port)
        print(f"Port {port} on {target}: {'OPEN' if is_open else 'CLOSED'}")
    
    elif cmd == 'listen':
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 4444
        result = listen(port)
        print(f"Listening on port {port}: {result.success}")
