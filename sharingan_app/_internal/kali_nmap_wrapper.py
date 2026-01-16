"""
nmap Wrapper for Sharingan OS
Real network scanner integration
"""

import subprocess
import re
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.nmap")

class NmapResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 hosts_found: int = 0, ports_found: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.hosts_found = hosts_found
        self.ports_found = ports_found
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'nmap'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    try:
        result = subprocess.run(['nmap', '--version'], capture_output=True, text=True, timeout=10)
        first_line = result.stdout.split('\n')[0]
        return first_line.strip()
    except Exception as e:
        return f"Error: {e}"

def quick_scan(target: str, ports: Optional[str] = None) -> NmapResult:
    cmd = ['nmap', '-sV', '-F']
    if ports:
        cmd.extend(['-p', ports])
    cmd.append(target)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        hosts = 0
        ports_count = 0
        if 'Nmap scan report' in output:
            hosts = output.count('Nmap scan report')
        ports_count = output.count('/tcp')
        return NmapResult(success=True, command=' '.join(cmd),
                         output=output[:3000], hosts_found=hosts, ports_found=ports_count)
    except Exception as e:
        return NmapResult(success=False, command=' '.join(cmd), error=str(e))

def full_scan(target: str, ports: Optional[str] = None) -> NmapResult:
    cmd = ['nmap', '-sV', '-sC', '-O']
    if ports:
        cmd.extend(['-p', ports])
    else:
        cmd.append('-p-')
    cmd.append(target)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        output = result.stdout + result.stderr
        hosts = output.count('Nmap scan report')
        ports_count = output.count('/tcp') + output.count('/udp')
        return NmapResult(success=True, command=' '.join(cmd),
                         output=output[:5000], hosts_found=hosts, ports_found=ports_count)
    except Exception as e:
        return NmapResult(success=False, command=' '.join(cmd), error=str(e))

def stealth_scan(target: str) -> NmapResult:
    cmd = ['nmap', '-sS', '-F', target]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        hosts = output.count('Nmap scan report')
        ports_count = output.count('/tcp')
        return NmapResult(success=True, command=' '.join(cmd),
                         output=output[:3000], hosts_found=hosts, ports_found=ports_count)
    except Exception as e:
        return NmapResult(success=False, command=' '.join(cmd), error=str(e))

def port_scan(target: str, port_range: Optional[str] = None) -> NmapResult:
    cmd = ['nmap']
    if port_range:
        cmd.extend(['-p', port_range])
    else:
        cmd.extend(['-p', '1-1000'])
    cmd.extend(['-sV', target])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        ports_count = output.count('/tcp') + output.count('/udp')
        return NmapResult(success=True, command=' '.join(cmd),
                         output=output[:3000], ports_found=ports_count)
    except Exception as e:
        return NmapResult(success=False, command=' '.join(cmd), error=str(e))

def os_detection(target: str) -> NmapResult:
    cmd = ['nmap', '-O', '--osscan-guess', target]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        return NmapResult(success=True, command=' '.join(cmd),
                         output=output[:3000], hosts_found=1 if 'Nmap scan report' in output else 0)
    except Exception as e:
        return NmapResult(success=False, command=' '.join(cmd), error=str(e))

def service_detection(target: str, port_range: Optional[str] = None) -> NmapResult:
    cmd = ['nmap', '-sV']
    if port_range:
        cmd.extend(['-p', port_range])
    cmd.append(target)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        ports_count = output.count('/tcp')
        return NmapResult(success=True, command=' '.join(cmd),
                         output=output[:3000], ports_found=ports_count)
    except Exception as e:
        return NmapResult(success=False, command=' '.join(cmd), error=str(e))

def ping_scan(target: str) -> NmapResult:
    cmd = ['nmap', '-sn', target]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        hosts = output.count('Nmap scan report')
        return NmapResult(success=True, command=' '.join(cmd),
                         output=output[:2000], hosts_found=hosts)
    except Exception as e:
        return NmapResult(success=False, command=' '.join(cmd), error=str(e))

def vuln_scan(target: str) -> NmapResult:
    cmd = ['nmap', '--script', 'vuln', target]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        output = result.stdout + result.stderr
        return NmapResult(success=True, command=' '.join(cmd),
                         output=output[:5000])
    except Exception as e:
        return NmapResult(success=False, command=' '.join(cmd), error=str(e))

def get_scan_types() -> List[str]:
    return [
        'sS', 'sT', 'sU', 'sN', 'sF', 'sX', 'sY', 'sZ',
        'sV', 'sC', 'O', 'A', 'PN', 'PE', 'PP', 'PY'
    ]

def get_help() -> str:
    try:
        result = subprocess.run(['nmap', '--help'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}
    
    if 'quick' in query_lower or 'rapide' in query_lower or 'fast' in query_lower:
        target = None
        target_match = re.search(r'(?:de|sur|of|on)\s+([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', query)
        if target_match:
            target = target_match.group(1)
        if not target:
            target_match = re.search(r'([a-zA-Z0-9.-]+\.[a-z]{2,})', query)
            if target_match:
                target = target_match.group(1)
        if not target:
            return {'success': False, 'error': 'Target required', 'example': 'scan rapide example.com'}
        result = quick_scan(target)
        return {'action': 'quick_scan', 'success': result.success, 'target': target,
               'hosts': result.hosts_found, 'ports': result.ports_found, 'output': result.output[:500]}
    
    if 'stealth' in query_lower or 'silencieux' in query_lower or 'sS' in query_lower:
        target = None
        target_match = re.search(r'(?:de|sur|of|on)\s+([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', query)
        if target_match:
            target = target_match.group(1)
        if not target:
            return {'success': False, 'error': 'Target required'}
        result = stealth_scan(target)
        return {'action': 'stealth_scan', 'success': result.success, 'target': target,
               'output': result.output[:500]}
    
    if 'port' in query_lower or 'ports' in query_lower or 'ports ouverts' in query_lower:
        target = None
        port_range = None
        
        target_match = re.search(r'(?:de|sur|of|on)\s+([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', query)
        if target_match:
            target = target_match.group(1)
        
        port_match = re.search(r'port[s]?\s*:?\s*([\d,-]+)', query)
        if port_match:
            port_range = port_match.group(1)
        
        if not target:
            return {'success': False, 'error': 'Target required', 'example': 'scan ports de example.com'}
        result = port_scan(target, port_range)
        return {'action': 'port_scan', 'success': result.success, 'target': target,
               'ports': result.ports_found, 'output': result.output[:500]}
    
    if 'os' in query_lower or 'os detection' in query_lower or 'système' in query_lower:
        target = None
        target_match = re.search(r'(?:de|sur|of|on)\s+([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', query)
        if target_match:
            target = target_match.group(1)
        if not target:
            return {'success': False, 'error': 'Target required'}
        result = os_detection(target)
        return {'action': 'os_detection', 'success': result.success, 'target': target,
               'output': result.output[:500]}
    
    if 'service' in query_lower or 'version' in query_lower or 'version detection' in query_lower:
        target = None
        port_range = None
        
        target_match = re.search(r'(?:de|sur|of|on)\s+([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', query)
        if target_match:
            target = target_match.group(1)
        
        port_match = re.search(r'port[s]?\s*:?\s*([\d,-]+)', query)
        if port_match:
            port_range = port_match.group(1)
        
        if not target:
            return {'success': False, 'error': 'Target required'}
        result = service_detection(target, port_range)
        return {'action': 'service_detection', 'success': result.success, 'target': target,
               'ports': result.ports_found, 'output': result.output[:500]}
    
    if 'ping' in query_lower or 'discover' in query_lower or 'découverte' in query_lower:
        target = None
        target_match = re.search(r'(?:de|sur|of|on)\s+([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', query)
        if target_match:
            target = target_match.group(1)
        if not target:
            return {'success': False, 'error': 'Target required'}
        result = ping_scan(target)
        return {'action': 'ping_scan', 'success': result.success, 'target': target,
               'hosts': result.hosts_found, 'output': result.output[:500]}
    
    if 'vuln' in query_lower or 'vulnerability' in query_lower or 'failles' in query_lower:
        target = None
        target_match = re.search(r'(?:de|sur|of|on)\s+([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', query)
        if target_match:
            target = target_match.group(1)
        if not target:
            return {'success': False, 'error': 'Target required'}
        result = vuln_scan(target)
        return {'action': 'vuln_scan', 'success': result.success, 'target': target,
               'output': result.output[:500]}
    
    if 'full' in query_lower or 'complet' in query_lower or 'comprehensive' in query_lower:
        target = None
        target_match = re.search(r'(?:de|sur|of|on)\s+([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', query)
        if target_match:
            target = target_match.group(1)
        if not target:
            return {'success': False, 'error': 'Target required'}
        result = full_scan(target)
        return {'action': 'full_scan', 'success': result.success, 'target': target,
               'hosts': result.hosts_found, 'ports': result.ports_found, 'output': result.output[:500]}
    
    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}
    
    if 'info' in query_lower or 'informations' in query_lower:
        return {'action': 'info', 'success': True, 'version': get_version(),
               'scan_types': get_scan_types(),
               'note': 'Active scanning may be detected by target'}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'scan ports de example.com ou scan rapide google.com'}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'nmap',
        'description': 'Network scanner and port mapper',
        'category': 'network',
        'supported_queries': [
            'quelle est la version de nmap',
            'scan rapide de example.com',
            'scan les ports de example.com',
            'scan stealth de example.com',
            'détection OS de example.com',
            'détection de services de example.com',
            'ping scan de example.com',
            'scan vulnérabilités de example.com',
            'scan complet de example.com',
            'aide nmap',
            'informations sur nmap'
        ],
        'warning': 'Active scanning should only be performed with authorization.',
        'scan_modes': ['quick', 'stealth', 'port', 'os', 'service', 'ping', 'vuln', 'full']
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("nmap Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'quick':
        if len(sys.argv) > 2:
            result = quick_scan(sys.argv[2])
            print(f"Hosts: {result.hosts_found}, Ports: {result.ports_found}")
            print(result.output[:500])
    elif cmd == 'ports':
        if len(sys.argv) > 2:
            result = port_scan(sys.argv[2])
            print(f"Ports found: {result.ports_found}")
            print(result.output[:500])
    elif cmd == 'help':
        print(get_help())
