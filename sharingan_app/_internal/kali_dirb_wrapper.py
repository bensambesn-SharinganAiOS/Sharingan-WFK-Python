"""
dirb Wrapper for Sharingan OS
Real directory busting tool integration
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.dirb")

class DirbResult:
    def __init__(self, success: bool, url: str = "", found_dirs: List[str] = None,
                 found_files: List[str] = None, total_found: int = 0,
                 output: str = "", error: Optional[str] = None):
        self.success = success
        self.url = url
        self.found_dirs = found_dirs or []
        self.found_files = found_files or []
        self.total_found = total_found
        self.output = output
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'dirb'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    try:
        result = subprocess.run(['dirb'], capture_output=True, text=True, timeout=10)
        for line in result.stdout.split('\n'):
            if 'DIRB v' in line:
                return line.strip()
        return result.stderr.strip().split('\n')[0]
    except Exception as e:
        return f"Error: {e}"

def scan_url(url: str, wordlist: str = None, extensions: str = None,
             output_file: str = None, timeout: int = 60) -> DirbResult:
    if not url.startswith('http'):
        url = 'http://' + url
    
    cmd = ['dirb', url]
    
    if wordlist:
        cmd.append(wordlist)
    elif not extensions:
        cmd.append('/usr/share/dirb/wordlists/common.txt')
    
    if extensions:
        cmd.extend(['-X', extensions])
    
    if output_file:
        cmd.extend(['-o', output_file])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        
        output = result.stdout + result.stderr
        found_dirs = []
        found_files = []
        
        for line in output.split('\n'):
            if '== ' in line and ('Directory:' in line or 'File:' in line):
                item = line.split('== ')[-1].strip()
                if ' (' in item:
                    status = item.split(' (')[1].strip(')')
                    path = item.split(' (')[0].strip()
                    if status.startswith('200') or status.startswith('301') or status.startswith('302'):
                        if '.' in os.path.basename(path):
                            found_files.append(path)
                        else:
                            found_dirs.append(path)
        
        return DirbResult(
            success=True,
            url=url,
            found_dirs=found_dirs,
            found_files=found_files,
            total_found=len(found_dirs) + len(found_files),
            output=output
        )
    except subprocess.TimeoutExpired:
        return DirbResult(success=False, url=url, output=output, error="Scan timed out")
    except Exception as e:
        return DirbResult(success=False, url=url, error=str(e))

def quick_scan(url: str, timeout: int = 30) -> DirbResult:
    return scan_url(url, timeout=timeout)

def scan_with_extensions(url: str, extensions: str = ".php,.html,.txt,.js,.css",
                         timeout: int = 60) -> DirbResult:
    return scan_url(url, extensions=extensions, timeout=timeout)

def scan_with_wordlist(url: str, wordlist_path: str, timeout: int = 120) -> DirbResult:
    if not os.path.exists(wordlist_path):
        return DirbResult(success=False, error=f"Wordlist not found: {wordlist_path}")
    return scan_url(url, wordlist=wordlist_path, timeout=timeout)

def get_common_wordlists() -> List[str]:
    wordlists = [
        '/usr/share/dirb/wordlists/common.txt',
        '/usr/share/dirb/wordlists/small.txt',
        '/usr/share/dirb/wordlists/big.txt',
        '/usr/share/wordlists/dirb/common.txt',
        '/usr/share/wordlists/dirb/small.txt',
        '/usr/share/wordlists/dirb/big.txt',
    ]
    available = []
    for wl in wordlists:
        if os.path.exists(wl):
            available.append(wl)
    return available

def analyze_target(url: str) -> Dict[str, Any]:
    if not url.startswith('http'):
        url = 'http://' + url
    
    return {
        'target': url,
        'wordlists': get_common_wordlists(),
        'extensions': ['.php', '.html', '.txt', '.js', '.css', '.asp', '.aspx', '.jsp', '.xml', '.log'],
        'default_wordlist': '/usr/share/dirb/wordlists/common.txt',
        'note': 'Use -X flag for extensions, custom wordlist for more thorough scans'
    }

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    # Extract target - supports localhost, IPs, domains
    target = None
    target_patterns = [
        r'de\s+(https?://[^\s]+)',
        r'sur\s+(https?://[^\s]+)',
        r'de\s+(localhost)',
        r'de\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
        r'de\s+([a-zA-Z0-9][a-zA-Z0-9.-]*)',
    ]
    
    for pattern in target_patterns:
        match = re.search(pattern, query_lower)
        if match:
            target = match.group(1)
            break
    
    if not target:
        return {'success': False, 'error': 'No target specified',
               'example': 'scan les répertoires de example.com'}
    
    if 'scan' in query_lower or 'scanne' in query_lower or 'trouve' in query_lower or 'liste' in query_lower or 'répertoires' in query_lower or 'dossiers' in query_lower:
        extensions = None
        ext_match = re.search(r'(?:with|avec|-X|extensions?)\s+([.,a-zA-Z0-9]+)', query)
        if ext_match:
            ext_str = ext_match.group(1).replace(',', '.')
            if not ext_str.startswith('.'):
                ext_str = '.' + ext_str
            extensions = ext_str
        
        wordlist = None
        wl_match = re.search(r'(?:wordlist|fichier)[\s\w]*([/\w]+\.txt)', query)
        if wl_match:
            wordlist = wl_match.group(1)
        
        result = scan_url(target, wordlist=wordlist, extensions=extensions, timeout=60)
        
        return {
            'action': 'directory_scan',
            'success': result.success,
            'url': target,
            'found_directories': result.found_dirs[:50],
            'found_files': result.found_files[:50],
            'total_found': result.total_found,
            'error': result.error
        }
    
    if 'rapide' in query_lower or 'quick' in query_lower:
        result = quick_scan(target)
        return {'action': 'quick_scan', 'success': result.success, 'url': target,
               'found': result.found_dirs + result.found_files, 'total': result.total_found}
    
    if 'extension' in query_lower or '.php' in query_lower or '.html' in query_lower:
        ext_match = re.search(r'(?:with|avec|extensions?)\s+([.,a-zA-Z0-9]+)', query)
        if ext_match:
            extensions = ext_match.group(1).replace(',', '.')
            if not extensions.startswith('.'):
                extensions = '.' + extensions
            result = scan_with_extensions(target, extensions)
            return {'action': 'extension_scan', 'success': result.success, 'url': target,
                   'extensions': extensions, 'found': result.found_dirs + result.found_files}
    
    if 'wordlist' in query_lower or 'fichier' in query_lower or 'liste' in query_lower:
        wordlists = get_common_wordlists()
        return {'action': 'wordlists', 'success': True, 'wordlists': wordlists,
               'current_target': target}
    
    if 'analyse' in query_lower or 'info' in query_lower:
        info = analyze_target(target)
        return {'action': 'analyze', 'success': True, 'target': target, 'info': info}
    
    result = quick_scan(target)
    return {'action': 'quick_scan', 'success': result.success, 'url': target,
           'found': result.found_dirs + result.found_files, 'total': result.total_found}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'dirb',
        'description': 'Directory busting and web content scanner',
        'category': 'enumeration',
        'supported_queries': [
            'scan les répertoires de example.com',
            'scan les dossiers de site.com',
            'trouve les fichiers de example.com',
            'scan rapide de example.com',
            'scan avec extensions .php .html de example.com',
            'analyse example.com'
        ],
        'common_extensions': ['.php', '.html', '.txt', '.js', '.css'],
        'default_wordlist': '/usr/share/dirb/wordlists/common.txt'
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("dirb Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)
    
    url = sys.argv[1]
    if not url.startswith('http'):
        url = 'http://' + url
    
    result = scan_url(url)
    print(f"Scan: {url}")
    print(f"Success: {result.success}")
    print(f"Found: {result.total_found} items")
    print(f"Dirs: {len(result.found_dirs)}, Files: {len(result.found_files)}")
