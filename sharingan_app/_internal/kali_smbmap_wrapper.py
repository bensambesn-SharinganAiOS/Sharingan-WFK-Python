"""
smbmap Wrapper for Sharingan OS
Real SMB enumeration tool integration
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.smbmap")

class SmbmapResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 shares_found: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.shares_found = shares_found
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'smbmap'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    try:
        result = subprocess.run(['smbmap', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
        return "smbmap installed"
    except Exception as e:
        return f"Error: {e}"

def list_shares(host: str, username: str = "guest", password: Optional[str] = "",
                port: int = 445) -> SmbmapResult:
    cmd = ['smbmap', '-H', host, '-u', username]
    
    if password:
        cmd.extend(['-p', password])
    if port != 445:
        cmd.extend(['-P', str(port)])
    
    cmd.append('-r')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        shares_count = output.count('[')
        return SmbmapResult(success=True, command=' '.join(cmd),
                           output=output[:3000], shares_found=shares_count)
    except Exception as e:
        return SmbmapResult(success=False, command=' '.join(cmd), error=str(e))

def list_files(host: str, share: str, path: str = "/",
               username: str = "guest", password: Optional[str] = "",
               port: int = 445) -> SmbmapResult:
    cmd = ['smbmap', '-H', host, '-u', username, '-s', share]
    
    if password:
        cmd.extend(['-p', password])
    if port != 445:
        cmd.extend(['-P', str(port)])
    
    cmd.extend(['-R', path])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        return SmbmapResult(success=True, command=' '.join(cmd),
                           output=output[:3000])
    except Exception as e:
        return SmbmapResult(success=False, command=' '.join(cmd), error=str(e))

def execute_command(host: str, command: str, share: str = "C$",
                    username: str = "administrator", password: Optional[str] = "",
                    port: int = 445) -> SmbmapResult:
    cmd = ['smbmap', '-H', host, '-u', username, '-s', share]
    
    if password:
        cmd.extend(['-p', password])
    if port != 445:
        cmd.extend(['-P', str(port)])
    
    cmd.extend(['-x', command])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        return SmbmapResult(success=True, command=' '.join(cmd),
                           output=output[:2000])
    except Exception as e:
        return SmbmapResult(success=False, command=' '.join(cmd), error=str(e))

def check_admin(host: str, username: str = "administrator", password: Optional[str] = "",
                port: int = 445) -> SmbmapResult:
    cmd = ['smbmap', '-H', host, '-u', username, '--admin']
    
    if password:
        cmd.extend(['-p', password])
    if port != 445:
        cmd.extend(['-P', str(port)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        return SmbmapResult(success=True, command=' '.join(cmd), output=output[:2000])
    except Exception as e:
        return SmbmapResult(success=False, command=' '.join(cmd), error=str(e))

def get_help() -> str:
    try:
        result = subprocess.run(['smbmap', '-h'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}
    
    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}
    
    if 'list' in query_lower and ('shares' in query_lower or 'partages' in query_lower):
        host = None
        username = "guest"
        
        host_match = re.search(r'(?:de|of|on|host)\s*:?\s*([a-zA-Z0-9.-]+)', query)
        if host_match:
            host = host_match.group(1)
        
        user_match = re.search(r'(?:user|utilisateur|username)\s*:?\s*(\w+)', query)
        if user_match:
            username = user_match.group(1)
        
        if not host:
            return {'success': False, 'error': 'Host required',
                   'example': 'list shares de 192.168.1.10'}
        
        result = list_shares(host, username)
        return {'action': 'list_shares', 'success': result.success,
               'host': host, 'username': username,
               'shares': result.shares_found, 'output': result.output[:500]}
    
    if 'files' in query_lower or 'fichiers' in query_lower or 'directory' in query_lower:
        host = None
        share = "C$"
        path = "/"
        username = "guest"
        
        host_match = re.search(r'(?:de|of|on|host)\s*:?\s*([a-zA-Z0-9.-]+)', query)
        if host_match:
            host = host_match.group(1)
        
        share_match = re.search(r'(?:share|partage)\s*:?\s*(\w+)', query)
        if share_match:
            share = share_match.group(1)
        
        if not host:
            return {'success': False, 'error': 'Host required',
                   'example': 'list files de 192.168.1.10'}
        
        result = list_files(host, share, path, username)
        return {'action': 'list_files', 'success': result.success,
               'host': host, 'share': share,
               'output': result.output[:500]}
    
    if 'exec' in query_lower or 'execute' in query_lower or 'command' in query_lower:
        host = None
        command = None
        username = "administrator"
        
        host_match = re.search(r'(?:de|of|on|host)\s*:?\s*([a-zA-Z0-9.-]+)', query)
        if host_match:
            host = host_match.group(1)
        
        cmd_match = re.search(r'(?:command|cmd|commande)\s*:?\s*(["\'])(.+?)\1', query)
        if cmd_match:
            command = cmd_match.group(2)
        else:
            cmd_match = re.search(r'execute\s+(\w+)', query)
            if cmd_match:
                command = cmd_match.group(1)
        
        if not host:
            return {'success': False, 'error': 'Host required'}
        if not command:
            return {'success': False, 'error': 'Command required',
                   'example': 'exec "whoami" de 192.168.1.10'}
        
        result = execute_command(host, command, username=username)
        return {'action': 'execute', 'success': result.success,
               'host': host, 'command': command,
               'output': result.output[:500]}
    
    if 'admin' in query_lower or 'privileges' in query_lower:
        host = None
        username = "administrator"
        
        host_match = re.search(r'(?:de|of|on|host)\s*:?\s*([a-zA-Z0-9.-]+)', query)
        if host_match:
            host = host_match.group(1)
        
        if not host:
            return {'success': False, 'error': 'Host required',
                   'example': 'check admin de 192.168.1.10'}
        
        result = check_admin(host, username)
        return {'action': 'check_admin', 'success': result.success,
               'host': host, 'output': result.output[:500]}
    
    if 'info' in query_lower or 'informations' in query_lower:
        return {'action': 'info', 'success': True, 'version': get_version(),
               'note': 'SMB enumeration - requires network access'}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'list shares de 192.168.1.10'}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'smbmap',
        'description': 'SMB enumeration tool',
        'category': 'network',
        'supported_queries': [
            'quelle est la version de smbmap',
            'list shares de 192.168.1.10',
            'list files de 192.168.1.10',
            'exec "whoami" de 192.168.1.10',
            'check admin de 192.168.1.10',
            'smbmap help',
            'informations sur smbmap'
        ],
        'warning': 'SMB enumeration should only be performed with authorization.',
        'features': ['list shares', 'list files', 'execute command', 'check admin']
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("smbmap Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'shares':
        if len(sys.argv) > 2:
            result = list_shares(sys.argv[2])
            print(f"Host: {sys.argv[2]}")
            print(f"Shares found: {result.shares_found}")
            print(result.output[:500])
    elif cmd == 'help':
        print(get_help())
