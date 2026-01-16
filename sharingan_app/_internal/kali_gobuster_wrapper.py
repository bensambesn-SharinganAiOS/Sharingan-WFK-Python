"""
gobuster Wrapper for Sharingan OS
Real directory/file & DNS busting tool integration
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.gobuster")

class GobusterResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 files_found: int = 0, dirs_found: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.files_found = files_found
        self.dirs_found = dirs_found
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'gobuster'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    try:
        result = subprocess.run(['gobuster', 'version'], capture_output=True, text=True, timeout=10)
        first_line = result.stdout.split('\n')[0]
        return first_line.strip()
    except Exception as e:
        return f"Error: {e}"

def dir_scan(url: str, wordlist: Optional[str] = None, extensions: Optional[str] = None,
             threads: int = 10, timeout: int = 30) -> GobusterResult:
    cmd = ['gobuster', 'dir', '-u', url, '-t', str(threads)]
    
    if wordlist:
        cmd.extend(['-w', wordlist])
    else:
        cmd.extend(['-w', '/usr/share/wordlists/dirb/common.txt'])
    
    if extensions:
        cmd.extend(['-x', extensions])
    
    cmd.extend(['-o', '/dev/stdout'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout * 10)
        output = result.stdout + result.stderr
        dirs_count = output.count('Status:') or output.count('(Duration:')
        return GobusterResult(success=True, command=' '.join(cmd),
                             output=output[:3000], dirs_found=dirs_count)
    except subprocess.TimeoutExpired:
        return GobusterResult(success=False, command=' '.join(cmd),
                             error="Scan timeout expired")
    except Exception as e:
        return GobusterResult(success=False, command=' '.join(cmd), error=str(e))

def dns_scan(domain: str, wordlist: Optional[str] = None, subdomains: Optional[str] = None,
             threads: int = 10) -> GobusterResult:
    cmd = ['gobuster', 'dns', '-d', domain, '-t', str(threads)]
    
    if wordlist:
        cmd.extend(['-w', wordlist])
    elif subdomains:
        cmd.extend(['-w', subdomains])
    else:
        cmd.extend(['-w', '/usr/share/wordlists/subdomains.txt'])
    
    cmd.extend(['-o', '/dev/stdout'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        return GobusterResult(success=True, command=' '.join(cmd),
                             output=output[:3000])
    except subprocess.TimeoutExpired:
        return GobusterResult(success=False, command=' '.join(cmd),
                             error="Scan timeout expired")
    except Exception as e:
        return GobusterResult(success=False, command=' '.join(cmd), error=str(e))

def fuzz_scan(url: str, wordlist: Optional[str] = None, fuzz_type: str = "url",
              threads: int = 10) -> GobusterResult:
    cmd = ['gobuster', 'fuzz', '-u', url, '-t', str(threads)]
    
    if wordlist:
        cmd.extend(['-w', wordlist])
    else:
        cmd.extend(['-w', '/usr/share/wordlists/fuzz.txt'])
    
    cmd.extend(['-o', '/dev/stdout'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        return GobusterResult(success=True, command=' '.join(cmd),
                             output=output[:3000])
    except subprocess.TimeoutExpired:
        return GobusterResult(success=False, command=' '.join(cmd),
                             error="Scan timeout expired")
    except Exception as e:
        return GobusterResult(success=False, command=' '.join(cmd), error=str(e))

def get_common_wordlists() -> List[str]:
    return [
        '/usr/share/wordlists/dirb/common.txt',
        '/usr/share/wordlists/dirb/big.txt',
        '/usr/share/wordlists/dirb/small.txt',
        '/usr/share/wordlists/subdomains.txt',
        '/usr/share/wordlists/fuzz.txt'
    ]

def get_help() -> str:
    try:
        result = subprocess.run(['gobuster', '-h'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}
    
    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}
    
    if 'dir' in query_lower or 'directory' in query_lower or 'repertoire' in query_lower:
        url = None
        extensions = None
        
        url_match = re.search(r'(?:de|sur|of|on)\s+(https?://[^\s]+)', query)
        if url_match:
            url = url_match.group(1)
        
        if not url:
            url_match = re.search(r'(https?://[a-zA-Z0-9.-]+\.[a-z]{2,})', query)
            if url_match:
                url = url_match.group(1)
                if not url.startswith('http'):
                    url = 'http://' + url
        
        ext_match = re.search(r'extensions?\s*:?\s*([a-z,]+)', query)
        if ext_match:
            extensions = ext_match.group(1)
        
        if not url:
            return {'success': False, 'error': 'URL required',
                   'example': 'scan directories de http://example.com'}
        
        result = dir_scan(url, extensions=extensions)
        return {'action': 'dir_scan', 'success': result.success, 'url': url,
               'dirs_found': result.dirs_found, 'output': result.output[:500]}
    
    if 'dns' in query_lower or 'subdomain' in query_lower or 'sous-domaine' in query_lower:
        domain = None
        
        domain_match = re.search(r'(?:de|of|on)\s+([a-zA-Z0-9.-]+\.[a-z]{2,})', query)
        if domain_match:
            domain = domain_match.group(1)
        
        if not domain:
            return {'success': False, 'error': 'Domain required',
                   'example': 'scan subdomains de example.com'}
        
        result = dns_scan(domain)
        return {'action': 'dns_scan', 'success': result.success, 'domain': domain,
               'output': result.output[:500]}
    
    if 'fuzz' in query_lower or 'fuzzing' in query_lower:
        url = None
        
        url_match = re.search(r'(?:de|sur|of)\s+(https?://[^\s]+)', query)
        if url_match:
            url = url_match.group(1)
        
        if not url:
            return {'success': False, 'error': 'URL required for fuzzing',
                   'example': 'fuzz http://example.comFUZZ'}
        
        result = fuzz_scan(url)
        return {'action': 'fuzz_scan', 'success': result.success, 'url': url,
               'output': result.output[:500]}
    
    if 'info' in query_lower or 'informations' in query_lower:
        return {'action': 'info', 'success': True, 'version': get_version(),
               'modes': ['dir', 'dns', 'fuzz'],
               'note': 'Directory/file enumeration tool'}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'scan directories de example.com ou scan subdomains de example.com'}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'gobuster',
        'description': 'Directory/file & DNS busting tool',
        'category': 'web',
        'supported_queries': [
            'quelle est la version de gobuster',
            'scan directories de example.com',
            'scan directories de http://example.com:8080',
            'scan subdomains de example.com',
            'gobuster fuzz http://example.comFUZZ',
            'gobuster help',
            'informations sur gobuster'
        ],
        'warning': 'Active enumeration should only be performed with authorization.',
        'modes': ['dir', 'dns', 'fuzz'],
        'common_extensions': ['php', 'txt', 'log', 'bak', 'zip', 'tar.gz']
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("gobuster Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'dir':
        if len(sys.argv) > 2:
            result = dir_scan(sys.argv[2])
            print(f"URL: {sys.argv[2]}")
            print(f"Dirs found: {result.dirs_found}")
            print(result.output[:500])
    elif cmd == 'dns':
        if len(sys.argv) > 2:
            result = dns_scan(sys.argv[2])
            print(f"Domain: {sys.argv[2]}")
            print(result.output[:500])
    elif cmd == 'help':
        print(get_help())
