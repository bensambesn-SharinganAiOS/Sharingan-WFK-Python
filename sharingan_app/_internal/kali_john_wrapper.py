"""
john (John the Ripper) Wrapper for Sharingan OS
Real password cracking tool integration
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging
import glob

logger = logging.getLogger("sharingan.john")

class JohnResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 cracked: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.cracked = cracked
        self.error = error

def is_available() -> bool:
    """Check if john is installed"""
    try:
        result = subprocess.run(['which', 'john'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    """Get john version info"""
    try:
        result = subprocess.run(['john'], capture_output=True, text=True, timeout=5)
        if 'John the Ripper' in result.stdout:
            for line in result.stdout.split('\n'):
                if 'version' in line.lower() or 'John' in line:
                    return line.strip()
        if 'Created directory' in result.stderr:
            return "John the Ripper (community edition)"
    except Exception as e:
        return f"Error: {e}"
    return "John the Ripper"

def list_formats() -> List[str]:
    """List supported hash formats"""
    try:
        result = subprocess.run(['john', '--list=formats'], capture_output=True, text=True, timeout=30)
        formats = result.stdout.strip().split('\n')
        return [f.strip() for f in formats if f.strip()]
    except Exception as e:
        return []

def list_wordlists() -> List[str]:
    """List available wordlists"""
    wordlists = []
    
    # Common locations
    locations = [
        '/usr/share/john/*.lst',
        '/usr/share/wordlists/*.txt',
        '/usr/share/wordlists/*.lst',
        '/usr/share/seclists/Passwords/*.txt',
        '/usr/share/seclists/Usernames/*.txt',
    ]
    
    for pattern in locations:
        wordlists.extend(glob.glob(pattern))
    
    return sorted(set(wordlists))

def get_default_wordlist() -> str:
    """Get default wordlist path"""
    defaults = [
        '/usr/share/john/password.lst',
        '/usr/share/wordlists/rockyou.txt',
        '/usr/share/wordlists/common.txt',
    ]
    for w in defaults:
        if os.path.exists(w):
            return w
    return ''

def crack_hash_file(hash_file: str, wordlist: str = None, format_: str = None,
                    timeout: int = 60) -> JohnResult:
    """Attempt to crack hashes from a file"""
    if not os.path.exists(hash_file):
        return JohnResult(success=False, error=f"Hash file not found: {hash_file}")
    
    cmd = ['john']
    
    if format_:
        cmd.extend(['--format=' + format_])
    
    if wordlist:
        cmd.extend(['--wordlist=' + wordlist])
    else:
        wordlist = get_default_wordlist()
        if wordlist:
            cmd.extend(['--wordlist=' + wordlist])
    
    cmd.append(hash_file)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        
        output = result.stdout + result.stderr
        cracked = 0
        
        # Count cracked passwords
        for line in output.split('\n'):
            if 'guessed' in line.lower() or 'cracked' in line.lower():
                match = re.search(r'(\d+)', line)
                if match:
                    cracked = int(match.group(1))
        
        return JohnResult(
            success=True,
            command=' '.join(cmd),
            output=output,
            cracked=cracked
        )
    except subprocess.TimeoutExpired:
        return JohnResult(success=False, command=' '.join(cmd), error="Timeout expired")
    except Exception as e:
        return JohnResult(success=False, command=' '.join(cmd), error=str(e))

def show_cracked(hash_file: str) -> JohnResult:
    """Show already cracked passwords"""
    cmd = ['john', '--show', hash_file]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        cracked = 0
        for line in result.stdout.split('\n'):
            if line.strip() and ':' in line:
                cracked += 1
        
        return JohnResult(
            success=True,
            command=' '.join(cmd),
            output=result.stdout,
            cracked=cracked
        )
    except Exception as e:
        return JohnResult(success=False, command=' '.join(cmd), error=str(e))

def identify_hash_type(hash_value: str) -> Dict[str, Any]:
    """Identify possible hash type"""
    hash_clean = hash_value.strip()
    
    identifications = []
    
    if len(hash_clean) == 32:
        identifications.append({'type': 'MD5', 'confidence': 'high'})
        identifications.append({'type': 'MD5(Unix)', 'confidence': 'medium'})
    elif len(hash_clean) == 40:
        identifications.append({'type': 'SHA-1', 'confidence': 'high'})
    elif len(hash_clean) == 56:
        identifications.append({'type': 'SHA-224', 'confidence': 'medium'})
    elif len(hash_clean) == 64:
        identifications.append({'type': 'SHA-256', 'confidence': 'high'})
    elif len(hash_clean) == 96:
        identifications.append({'type': 'SHA-384', 'confidence': 'medium'})
    elif len(hash_clean) == 128:
        identifications.append({'type': 'SHA-512', 'confidence': 'high'})
    elif hash_clean.startswith('$1$'):
        identifications.append({'type': 'MD5(Unix)', 'confidence': 'high'})
    elif hash_clean.startswith('$2a$') or hash_clean.startswith('$2b$'):
        identifications.append({'type': 'Bcrypt', 'confidence': 'high'})
    elif hash_clean.startswith('$5$'):
        identifications.append({'type': 'SHA-256(Unix)', 'confidence': 'high'})
    elif hash_clean.startswith('$6$'):
        identifications.append({'type': 'SHA-512(Unix)', 'confidence': 'high'})
    else:
        identifications.append({'type': 'Unknown', 'confidence': 'low'})
    
    return {
        'hash': hash_value,
        'length': len(hash_clean),
        'identifications': identifications
    }

def strength_check(password: str) -> Dict[str, Any]:
    """Check password strength"""
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Too short (minimum 8 characters)")
    
    if len(password) >= 12:
        score += 1
    
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Add uppercase letters")
    
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Add lowercase letters")
    
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Add numbers")
    
    special = re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|<,./>?]', password)
    if special:
        score += 1
    else:
        feedback.append("Add special characters")
    
    strength = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'][max(0, min(score, 5) - 1)]
    
    return {
        'password': password[:2] + '*' * (len(password) - 2) if len(password) > 2 else '***',
        'length': len(password),
        'score': score,
        'strength': strength,
        'feedback': feedback
    }

def handle_nlp_query(query: str) -> Dict[str, Any]:
    """Handle natural language query for john operations"""
    query_lower = query.lower()
    
    if 'version' in query_lower or 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}
    
    if 'format' in query_lower or 'formats' in query_lower:
        formats = list_formats()
        return {'action': 'formats', 'success': True, 'formats': formats[:20], 'total': len(formats)}
    
    if 'wordlist' in query_lower or 'liste' in query_lower or 'list' in query_lower:
        wordlists = list_wordlists()
        default = get_default_wordlist()
        return {'action': 'wordlists', 'success': True, 'wordlists': wordlists[:10],
               'default': default, 'total': len(wordlists)}
    
    if 'crack' in query_lower or 'craquer' in query_lower or 'crack' in query_lower:
        file_match = re.search(r'([/\w]+\.(txt|pwd|hash|lst))', query)
        if file_match:
            hash_file = file_match.group(1)
            format_ = None
            fmt_match = re.search(r'(?:format|format:|-format|--format=)([a-zA-Z0-9]+)', query)
            if fmt_match:
                format_ = fmt_match.group(1)
            
            wordlist = None
            wl_match = re.search(r'(?:wordlist|liste)[\s\w]*([/\w]+\.txt)', query)
            if wl_match:
                wordlist = wl_match.group(1)
            
            result = crack_hash_file(hash_file, wordlist, format_)
            return {'action': 'crack', 'success': result.success, 'file': hash_file,
                   'cracked': result.cracked, 'output': result.output[:500], 'error': result.error}
        
        return {'action': 'crack', 'success': False, 'error': 'No hash file specified',
               'example': 'crack le fichier hashes.txt'}
    
    if 'show' in query_lower or 'affiche' in query_lower or 'affiche' in query_lower:
        file_match = re.search(r'([/\w]+\.(txt|pwd|hash))', query)
        if file_match:
            hash_file = file_match.group(1)
            result = show_cracked(hash_file)
            return {'action': 'show', 'success': result.success, 'file': hash_file,
                   'cracked': result.cracked, 'output': result.output}
        
        return {'action': 'show', 'success': False, 'error': 'No file specified'}
    
    if 'identify' in query_lower or 'quel type' in query_lower or 'type de hash' in query_lower:
        hash_match = re.search(r'([a-fA-F0-9$]{20,128})', query)
        if hash_match:
            hash_val = hash_match.group(1)
            result = identify_hash_type(hash_val)
            return {'action': 'identify', 'success': True, 'hash_info': result}
        
        return {'action': 'identify', 'success': False, 'error': 'No hash found',
               'example': 'quel type de hash est 5d41402abc4b2a76b9719d911017c592'}
    
    if 'strength' in query_lower or 'force' in query_lower or 'robustesse' in query_lower:
        pwd_match = re.search(r'(?:mot de passe|password|passe)[\s\w]*["\']?([^"\']+)["\']?', query)
        if pwd_match:
            pwd = pwd_match.group(1).strip()
            result = strength_check(pwd)
            return {'action': 'strength', 'success': True, 'analysis': result}
        
        return {'action': 'strength', 'success': False, 'error': 'No password specified'}
    
    if 'info' in query_lower or 'informations' in query_lower:
        formats = list_formats()
        wordlists = list_wordlists()
        return {'action': 'info', 'success': True, 'formats_count': len(formats),
               'wordlists_count': len(wordlists), 'default_wordlist': get_default_wordlist()}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'crack hashes.txt ou quel type de hash est <hash>'}

def get_status() -> Dict[str, Any]:
    """Get john wrapper status"""
    return {
        'available': is_available(),
        'name': 'john',
        'description': 'John the Ripper - Password cracker',
        'category': 'password',
        'supported_queries': [
            'quelle est la version de john',
            'liste les formats supportés',
            'liste les wordlists',
            'crack le fichier hashes.txt',
            'crack hashes.txt avec wordlist rockyou.txt',
            'affiche les mots de passe crackés de hashes.txt',
            'quel type de hash est 5d41402abc4b2a76b9719d911017c592',
            'force du mot de passe secret123',
            'informations sur john'
        ],
        'default_wordlist': get_default_wordlist(),
        'note': 'Password cracking requires authorized access to hash files'
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("john Wrapper for Sharingan OS")
        print(f"Available: {is_available()}")
        print(f"Version: {get_version()}")
        print("\nUsage:")
        print("  python3 kali_john_wrapper.py crack <hash_file>")
        print("  python3 kali_john_wrapper.py show <hash_file>")
        print("  python3 kali_john_wrapper.py identify <hash>")
        print("  python3 kali_john_wrapper.py strength <password>")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == 'version':
        print(f"Version: {get_version()}")
    
    elif cmd == 'formats':
        formats = list_formats()
        print(f"Formats ({len(formats)}):")
        for f in formats[:10]:
            print(f"  - {f}")
    
    elif cmd == 'wordlists':
        wordlists = list_wordlists()
        print(f"Wordlists ({len(wordlists)}):")
        for w in wordlists[:10]:
            print(f"  - {w}")
    
    elif cmd == 'crack':
        if len(sys.argv) > 2:
            result = crack_hash_file(sys.argv[2])
            print(f"Success: {result.success}")
            print(f"Cracked: {result.cracked}")
            print(f"Output:\n{result.output[:500]}")
        else:
            print("Usage: john_wrapper.py crack <hash_file>")
    
    elif cmd == 'identify':
        if len(sys.argv) > 2:
            info = identify_hash_type(sys.argv[2])
            print(f"Hash: {info['hash']}")
            print(f"Length: {info['length']}")
            print("Possible types:")
            for ident in info['identifications']:
                print(f"  - {ident['type']} ({ident['confidence']} confidence)")
        else:
            print("Usage: john_wrapper.py identify <hash>")
    
    elif cmd == 'strength':
        if len(sys.argv) > 2:
            result = strength_check(sys.argv[2])
            print(f"Password: {result['password']}")
            print(f"Strength: {result['strength']} (score: {result['score']}/6)")
            if result['feedback']:
                print("Suggestions:")
                for f in result['feedback']:
                    print(f"  - {f}")
        else:
            print("Usage: john_wrapper.py strength <password>")
