"""
rpcclient Wrapper for Sharingan OS
Real RPC client for Windows domains
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.rpcclient")

class RpcclientResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'rpcclient'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    try:
        result = subprocess.run(['rpcclient', '--version'], capture_output=True, text=True, timeout=10)
        first_line = result.stdout.split('\n')[0]
        return first_line.strip()
    except Exception as e:
        return f"Error: {e}"

def enum_domains(host: str, username: str = "", password: str = "") -> RpcclientResult:
    cmd = ['rpcclient', '-U', f'{username}%{password}', host]
    cmd.extend(['--command', 'enumdomains'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return RpcclientResult(success=True, command=' '.join(cmd), output=output[:2000])
    except Exception as e:
        return RpcclientResult(success=False, command=' '.join(cmd), error=str(e))

def enum_users(host: str, username: str = "", password: str = "") -> RpcclientResult:
    cmd = ['rpcclient', '-U', f'{username}%{password}', host]
    cmd.extend(['--command', 'queryusers'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return RpcclientResult(success=True, command=' '.join(cmd), output=output[:2000])
    except Exception as e:
        return RpcclientResult(success=False, command=' '.join(cmd), error=str(e))

def enum_shares(host: str, username: str = "", password: str = "") -> RpcclientResult:
    cmd = ['rpcclient', '-U', f'{username}%{password}', host]
    cmd.extend(['--command', 'netshareenumall'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return RpcclientResult(success=True, command=' '.join(cmd), output=output[:2000])
    except Exception as e:
        return RpcclientResult(success=False, command=' '.join(cmd), error=str(e))

def get_domainsid(host: str, username: str = "", password: str = "") -> RpcclientResult:
    cmd = ['rpcclient', '-U', f'{username}%{password}', host]
    cmd.extend(['--command', 'getdompwinfo'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return RpcclientResult(success=True, command=' '.join(cmd), output=output[:2000])
    except Exception as e:
        return RpcclientResult(success=False, command=' '.join(cmd), error=str(e))

def query_user(host: str, username: str = "", password: str = "", target_user: str = "") -> RpcclientResult:
    cmd = ['rpcclient', '-U', f'{username}%{password}', host]
    cmd.extend(['--command', f'queryuser {target_user}'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return RpcclientResult(success=True, command=' '.join(cmd), output=output[:2000])
    except Exception as e:
        return RpcclientResult(success=False, command=' '.join(cmd), error=str(e))

def execute_command(host: str, command: str, username: str = "", password: str = "") -> RpcclientResult:
    cmd = ['rpcclient', '-U', f'{username}%{password}', host]
    cmd.extend(['--command', f'shell {command}'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return RpcclientResult(success=True, command=' '.join(cmd), output=output[:2000])
    except Exception as e:
        return RpcclientResult(success=False, command=' '.join(cmd), error=str(e))

def get_help() -> str:
    try:
        result = subprocess.run(['rpcclient', '--help'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}
    
    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}
    
    if 'domains' in query_lower or 'domaines' in query_lower:
        host = None
        username = ""
        
        host_match = re.search(r'(?:de|of|on|host)\s*:?\s*([a-zA-Z0-9.-]+)', query)
        if host_match:
            host = host_match.group(1)
        
        if not host:
            return {'success': False, 'error': 'Host required',
                   'example': 'enum domains de 192.168.1.10'}
        
        result = enum_domains(host, username)
        return {'action': 'enum_domains', 'success': result.success,
               'host': host, 'output': result.output[:500]}
    
    if 'users' in query_lower or 'utilisateurs' in query_lower:
        host = None
        username = ""
        
        host_match = re.search(r'(?:de|of|on|host)\s*:?\s*([a-zA-Z0-9.-]+)', query)
        if host_match:
            host = host_match.group(1)
        
        if not host:
            return {'success': False, 'error': 'Host required',
                   'example': 'enum users de 192.168.1.10'}
        
        result = enum_users(host, username)
        return {'action': 'enum_users', 'success': result.success,
               'host': host, 'output': result.output[:500]}
    
    if 'shares' in query_lower or 'partages' in query_lower:
        host = None
        username = ""
        
        host_match = re.search(r'(?:de|of|on|host)\s*:?\s*([a-zA-Z0-9.-]+)', query)
        if host_match:
            host = host_match.group(1)
        
        if not host:
            return {'success': False, 'error': 'Host required',
                   'example': 'enum shares de 192.168.1.10'}
        
        result = enum_shares(host, username)
        return {'action': 'enum_shares', 'success': result.success,
               'host': host, 'output': result.output[:500]}
    
    if 'query' in query_lower and 'user' in query_lower:
        host = None
        target_user = None
        username = ""
        
        host_match = re.search(r'(?:de|of|on|host)\s*:?\s*([a-zA-Z0-9.-]+)', query)
        if host_match:
            host = host_match.group(1)
        
        user_match = re.search(r'(?:user|utilisateur)\s*:?\s*(\w+)', query)
        if user_match:
            target_user = user_match.group(1)
        
        if not host:
            return {'success': False, 'error': 'Host required'}
        if not target_user:
            return {'success': False, 'error': 'Target user required',
                   'example': 'query user administrator de 192.168.1.10'}
        
        result = query_user(host, username, password="", target_user=target_user)
        return {'action': 'query_user', 'success': result.success,
               'host': host, 'user': target_user, 'output': result.output[:500]}
    
    if 'info' in query_lower or 'informations' in query_lower:
        return {'action': 'info', 'success': True, 'version': get_version(),
               'note': 'RPC client for Windows domains'}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'enum domains de 192.168.1.10'}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'rpcclient',
        'description': 'RPC client for Windows domains',
        'category': 'network',
        'supported_queries': [
            'quelle est la version de rpcclient',
            'enum domains de 192.168.1.10',
            'enum users de 192.168.1.10',
            'enum shares de 192.168.1.10',
            'query user administrator de 192.168.1.10',
            'rpcclient help',
            'informations sur rpcclient'
        ],
        'warning': 'SMB enumeration requires proper authentication.',
        'features': ['enum domains', 'enum users', 'enum shares', 'query user']
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("rpcclient Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'domains':
        if len(sys.argv) > 2:
            result = enum_domains(sys.argv[2])
            print(f"Host: {sys.argv[2]}")
            print(result.output[:500])
    elif cmd == 'help':
        print(get_help())
