"""
cewl Wrapper for Sharingan OS
Real wordlist generator from websites
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.cewl")

class CewlResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 words_count: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.words_count = words_count
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'cewl'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    try:
        result = subprocess.run(['cewl', '--version'], capture_output=True, text=True, timeout=10)
        first_line = result.stdout.split('\n')[0]
        return first_line.strip()
    except Exception as e:
        return f"Error: {e}"

def generate_wordlist(url: str, depth: int = 2, min_length: int = 3,
                      output_file: Optional[str] = None, count: Optional[int] = None) -> CewlResult:
    cmd = ['cewl', url, '-d', str(depth), '-m', str(min_length)]
    
    if output_file:
        cmd.extend(['-w', output_file])
    
    if count:
        cmd.extend(['-c'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        words_count = 0
        if 'Total words:' in output:
            for line in output.split('\n'):
                if 'Total words:' in line:
                    words_count = int(line.split(':')[1].strip())
                    break
        return CewlResult(success=True, command=' '.join(cmd),
                         output=output[:3000], words_count=words_count)
    except subprocess.TimeoutExpired:
        return CewlResult(success=False, command=' '.join(cmd),
                         error="Timeout expired")
    except Exception as e:
        return CewlResult(success=False, command=' '.join(cmd), error=str(e))

def generate_with_meta(url: str, depth: int = 2) -> CewlResult:
    cmd = ['cewl', url, '-d', str(depth), '--meta', '--meta_file', '/dev/stdout']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        return CewlResult(success=True, command=' '.join(cmd), output=output[:3000])
    except Exception as e:
        return CewlResult(success=False, command=' '.join(cmd), error=str(e))

def generate_with_emails(url: str, depth: int = 2) -> CewlResult:
    cmd = ['cewl', url, '-d', str(depth), '--email', '--email_file', '/dev/stdout']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        emails = []
        for line in output.split('\n'):
            if '@' in line:
                emails.append(line.strip())
        return CewlResult(success=True, command=' '.join(cmd),
                         output=output[:2000], words_count=len(emails))
    except Exception as e:
        return CewlResult(success=False, command=' '.join(cmd), error=str(e))

def get_help() -> str:
    try:
        result = subprocess.run(['cewl', '--help'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}
    
    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}
    
    if 'wordlist' in query_lower or 'génère' in query_lower or 'generate' in query_lower:
        url = None
        depth = 2
        min_length = 3
        
        url_match = re.search(r'(?:de|of|from)\s+(https?://[^\s]+)', query)
        if url_match:
            url = url_match.group(1)
        
        if not url:
            url_match = re.search(r'(https?://[a-zA-Z0-9.-]+\.[a-z]{2,})', query)
            if url_match:
                url = 'http://' + url_match.group(1)
        
        depth_match = re.search(r'(?:depth|profondeur)\s*:?\s*(\d+)', query)
        if depth_match:
            depth = int(depth_match.group(1))
        
        min_match = re.search(r'(?:min|minimum)\s*:?\s*(\d+)', query)
        if min_match:
            min_length = int(min_match.group(1))
        
        if not url:
            return {'success': False, 'error': 'URL required',
                   'example': 'generate wordlist de https://example.com'}
        
        result = generate_wordlist(url, depth, min_length)
        return {'action': 'wordlist', 'success': result.success,
               'url': url, 'words': result.words_count, 'output': result.output[:500]}
    
    if 'meta' in query_lower or 'metadata' in query_lower:
        url = None
        
        url_match = re.search(r'(?:de|of|from)\s+(https?://[^\s]+)', query)
        if url_match:
            url = url_match.group(1)
        
        if not url:
            return {'success': False, 'error': 'URL required'}
        
        result = generate_with_meta(url)
        return {'action': 'meta', 'success': result.success,
               'output': result.output[:500]}
    
    if 'email' in query_lower or 'emails' in query_lower:
        url = None
        
        url_match = re.search(r'(?:de|of|from)\s+(https?://[^\s]+)', query)
        if url_match:
            url = url_match.group(1)
        
        if not url:
            return {'success': False, 'error': 'URL required'}
        
        result = generate_with_emails(url)
        return {'action': 'emails', 'success': result.success,
               'emails': result.words_count, 'output': result.output[:500]}
    
    if 'info' in query_lower or 'informations' in query_lower:
        return {'action': 'info', 'success': True, 'version': get_version(),
               'note': 'Wordlist generator from website content'}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'generate wordlist de https://example.com'}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'cewl',
        'description': 'Wordlist generator from websites',
        'category': 'password',
        'supported_queries': [
            'quelle est la version de cewl',
            'generate wordlist de https://example.com',
            'cewl help',
            'wordlist de example.com depth 3',
            'extract emails de https://example.com',
            'informations sur cewl'
        ],
        'warning': 'Respect website terms of service when spidering.',
        'features': ['wordlist generation', 'meta data extraction', 'email extraction']
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("cewl Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'wordlist':
        if len(sys.argv) > 2:
            result = generate_wordlist(sys.argv[2])
            print(f"URL: {sys.argv[2]}")
            print(f"Words found: {result.words_count}")
            print(result.output[:500])
    elif cmd == 'help':
        print(get_help())
