"""
nikto Wrapper for Sharingan OS
Real web vulnerability scanner integration
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.nikto")

class NiktoResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 vulnerabilities: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.vulnerabilities = vulnerabilities
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'nikto'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    try:
        result = subprocess.run(['nikto', '-Version'], capture_output=True, text=True, timeout=10)
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Nikto' in line or 'version' in line.lower():
                return line.strip()
        return "Nikto " + lines[0].strip() if lines else "Unknown"
    except Exception as e:
        return f"Error: {e}"

def scan_target(host: str, port: Optional[int] = None, ssl: bool = False,
                timeout: int = 300) -> NiktoResult:
    cmd = ['nikto', '-h', host, '-t', str(timeout)]
    
    if port:
        cmd.extend(['-p', str(port)])
    if ssl:
        cmd.append('-ssl')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        output = result.stdout + result.stderr
        vuln_count = output.count('+')
        return NiktoResult(success=True, command=' '.join(cmd),
                          output=output[:5000], vulnerabilities=vuln_count)
    except subprocess.TimeoutExpired:
        return NiktoResult(success=False, command=' '.join(cmd),
                          error="Scan timeout expired")
    except Exception as e:
        return NiktoResult(success=False, command=' '.join(cmd), error=str(e))

def quick_scan(host: str, port: Optional[int] = None) -> NiktoResult:
    cmd = ['nikto', '-h', host, '-T', 'x5']
    
    if port:
        cmd.extend(['-p', str(port)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        vuln_count = output.count('+')
        return NiktoResult(success=True, command=' '.join(cmd),
                          output=output[:3000], vulnerabilities=vuln_count)
    except Exception as e:
        return NiktoResult(success=False, command=' '.join(cmd), error=str(e))

def list_plugins() -> List[str]:
    return [
        'apacheusers', 'auth', 'cgi', 'dictionary', 'domain', 'encoding',
        'error', 'filetype', 'generic', 'headers', 'mssql', 'mysql',
        'oracle', 'osvdb', 'outdated', 'passfiles', 'prefetch',
        'realip', 'robots', 'shellfiles', 'sitefiles', 'static',
        'subdomain', 'upload', 'wapiti', 'whois', 'wp-plugins'
    ]

def get_help() -> str:
    try:
        result = subprocess.run(['nikto', '-help'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}
    
    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}
    
    if 'scan' in query_lower or 'vuln' in query_lower or 'failles' in query_lower:
        host = None
        port = None
        ssl = False
        
        host_match = re.search(r'(?:de|sur|of|on|host|h)\s*:?\s*([a-zA-Z0-9.-]+\.[a-z]{2,})', query)
        if host_match:
            host = host_match.group(1)
        
        if not host:
            host_match = re.search(r'(https?://)?([a-zA-Z0-9.-]+\.[a-z]{2,})', query)
            if host_match:
                host = host_match.group(2)
                if host_match.group(1):
                    ssl = 'https' in host_match.group(1)
        
        port_match = re.search(r'port\s*:?\s*(\d+)', query)
        if port_match:
            port = int(port_match.group(1))
        
        if not host:
            return {'success': False, 'error': 'Target host required',
                   'example': 'scan vulnerabilites de example.com'}
        
        ssl = 'ssl' in query_lower or 'https' in query_lower
        
        if 'quick' in query_lower or 'rapide' in query_lower:
            result = quick_scan(host, port)
        else:
            result = scan_target(host, port, ssl)
        
        return {'action': 'scan', 'success': result.success, 'host': host,
               'port': port, 'vulnerabilities': result.vulnerabilities,
               'output': result.output[:500]}
    
    if 'plugins' in query_lower or 'options' in query_lower:
        return {'action': 'plugins', 'success': True, 'plugins': list_plugins()}
    
    if 'info' in query_lower or 'informations' in query_lower:
        return {'action': 'info', 'success': True, 'version': get_version(),
               'note': 'Web vulnerability scanner - may take several minutes'}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'scan vulnerabilites de example.com ou scan rapide de example.com:8080'}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'nikto',
        'description': 'Web vulnerability scanner',
        'category': 'web',
        'supported_queries': [
            'quelle est la version de nikto',
            'scan vulnerabilites de example.com',
            'scan rapide de example.com:8080',
            'scan ssl de example.com',
            'nikto help',
            'informations sur nikto'
        ],
        'warning': 'Active scanning may be detected by target. Use with authorization.',
        'scan_modes': ['quick', 'full', 'ssl'],
        'example_targets': ['example.com', 'localhost:8080', 'https://secure.example.com']
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("nikto Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'scan':
        if len(sys.argv) > 2:
            result = scan_target(sys.argv[2])
            print(f"Target: {sys.argv[2]}")
            print(f"Vulnerabilities found: {result.vulnerabilities}")
            print(result.output[:500])
    elif cmd == 'quick':
        if len(sys.argv) > 2:
            result = quick_scan(sys.argv[2])
            print(f"Quick scan: {sys.argv[2]}")
            print(f"Vulnerabilities found: {result.vulnerabilities}")
    elif cmd == 'help':
        print(get_help())
