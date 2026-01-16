"""
hashcat Wrapper for Sharingan OS
Real password recovery utility integration
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.hashcat")

class HashcatResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 cracked: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.cracked = cracked
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'hashcat'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    try:
        result = subprocess.run(['hashcat', '--version'], capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def hash_info(hash_value: str) -> Dict[str, Any]:
    try:
        result = subprocess.run(['hashcat', '--identify', hash_value],
                               capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return {'success': True, 'output': output}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def benchmark(algorithms: Optional[List[str]] = None) -> HashcatResult:
    cmd = ['hashcat', '-b']
    if algorithms:
        cmd.extend(['-m', ','.join(algorithms)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        return HashcatResult(success=True, command=' '.join(cmd), output=output[:2000])
    except Exception as e:
        return HashcatResult(success=False, command=' '.join(cmd), error=str(e))

def attack_mask(hash_file: str, mask: str = '?a?a?a?a?a?a',
                threads: Optional[int] = None) -> HashcatResult:
    cmd = ['hashcat', '-m', '0', hash_file, mask, '--force']
    
    if threads:
        cmd.extend(['-t', str(threads)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        return HashcatResult(success=True, command=' '.join(cmd), output=output[:2000])
    except subprocess.TimeoutExpired:
        return HashcatResult(success=False, command=' '.join(cmd), error="Attack timeout")
    except Exception as e:
        return HashcatResult(success=False, command=' '.join(cmd), error=str(e))

def attack_wordlist(hash_file: str, wordlist: Optional[str] = None,
                    rules: Optional[str] = None) -> HashcatResult:
    cmd = ['hashcat', '-m', '0', hash_file]
    
    if wordlist:
        cmd.append(wordlist)
    else:
        cmd.append('/usr/share/wordlists/rockyou.txt')
    
    if rules:
        cmd.extend(['-r', rules])
    
    cmd.append('--force')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        return HashcatResult(success=True, command=' '.join(cmd), output=output[:2000])
    except subprocess.TimeoutExpired:
        return HashcatResult(success=False, command=' '.join(cmd), error="Attack timeout")
    except Exception as e:
        return HashcatResult(success=False, command=' '.join(cmd), error=str(e))

def list_attack_modes() -> List[str]:
    return [
        'straight', 'combinator', 'brute-force', 'wordlist',
        'hybrid', 'association', 'mask', 'prefix'
    ]

def list_hash_types() -> Dict[int, str]:
    return {
        0: 'MD5',
        10: 'MD5crypt',
        100: 'SHA1crypt',
        400: 'phpass',
        500: 'md5crypt',
        1000: 'SHA256',
        1400: 'SHA256crypt',
        1800: 'sha512crypt',
        3200: 'bcrypt',
        5500: 'NetNTLMv1',
        5600: 'NetNTLMv2',
        6100: 'Cisco PIX',
        6300: 'MD5(Unix)',
        6800: 'LastPass',
        7500: 'Kerberos 5',
        10000: 'Drupal7',
        10200: 'Cisco $9$',
        10900: 'PostgreSQL',
        11200: 'MySQL5+',
        11400: 'phpass',
        12400: 'Django',
        12500: 'RAR3',
        12600: 'ColdFusion',
        12800: 'MS SQL 2005',
        12900: 'MS SQL 2012',
        13200: '7z',
        13400: 'Keepass',
        13711: 'VeraCrypt',
        13800: 'Windows 8+',
        14400: 'sha1crypt',
        14700: 'Reflective DLL',
        14900: 'Exchange',
        15000: 'descrypt',
        15400: 'sha256crypt',
        17220: 'macOS v10.8+',
        17600: 'MD4',
        18200: 'Apache $apr1$',
        20000: 'MySQL4.1/5',
        27100: 'SQLite',
        28100: 'Android FDE',
        29100: 'Scrypt',
        31000: 'SHA3-512',
        37100: 'md5(phpBB3)',
        39100: 'md5(WordPress)',
        40100: 'md5($pass.$salt)',
        45300: 'md5(phpBB3)',
        45400: 'md5(WordPress)',
        47000: 'md5(md5(md5($pass)))',
        48100: 'md5($salt.md5($pass))',
        51000: 'md5($pass.$salt)',
        53000: 'md5($salt.$pass)',
        54200: 'md5($salt.$pass.$salt)',
    }

def get_help() -> str:
    try:
        result = subprocess.run(['hashcat', '--help'], capture_output=True, text=True, timeout=10)
        return result.stdout[:3000]
    except Exception as e:
        return f"Error: {e}"

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}
    
    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}
    
    if 'benchmark' in query_lower:
        result = benchmark()
        return {'action': 'benchmark', 'success': result.success,
               'output': result.output[:500]}
    
    if 'hash' in query_lower and 'type' in query_lower:
        hash_match = re.search(r'([a-fA-F0-9$:+/\.]{8,})', query)
        if hash_match:
            info = hash_info(hash_match.group(1))
            return {'action': 'identify', 'success': info['success'],
                   'hash': hash_match.group(1), 'output': info.get('output', '')}
        return {'action': 'identify', 'success': False,
               'error': 'No hash specified'}
    
    if 'crack' in query_lower or 'brute' in query_lower:
        hash_match = re.search(r'([a-fA-F0-9$:+/\.]{8,})', query)
        if hash_match:
            wordlist = None
            wordlist_match = re.search(r'wordlist\s*:?\s*(\S+)', query)
            if wordlist_match:
                wordlist = wordlist_match.group(1)
            
            result = attack_wordlist(hash_match.group(1), wordlist)
            return {'action': 'crack', 'success': result.success,
                   'hash': hash_match.group(1), 'output': result.output[:500]}
        
        return {'action': 'crack', 'success': False,
               'error': 'No hash specified',
               'example': 'crack 5d41402abc4b2a76b9719d911017c592'}
    
    if 'attack' in query_lower or 'modes' in query_lower:
        return {'action': 'modes', 'success': True,
               'attack_modes': list_attack_modes(),
               'hash_types': list_hash_types()}
    
    if 'info' in query_lower or 'informations' in query_lower:
        return {'action': 'info', 'success': True, 'version': get_version(),
               'note': 'Password recovery requires authorization'}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'crack 5d41402abc4b2a76b9719d911017c592'}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'hashcat',
        'description': 'Advanced password recovery utility',
        'category': 'password',
        'supported_queries': [
            'quelle est la version de hashcat',
            'hashcat benchmark',
            'crack 5d41402abc4b2a76b9719d911017c592',
            'hashcat attack modes',
            'hashcat help',
            'informations sur hashcat'
        ],
        'warning': 'Password cracking requires explicit authorization.',
        'attack_modes': list_attack_modes(),
        'example_hashes': [
            '5d41402abc4b2a76b9719d911017c592 (MD5)',
            'e10adc3949ba59abbe56e057f20f883e (MD5)'
        ]
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("hashcat Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'benchmark':
        result = benchmark()
        print(result.output[:500])
    elif cmd == 'help':
        print(get_help())
