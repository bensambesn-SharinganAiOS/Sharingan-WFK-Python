"""
hydra Wrapper for Sharingan OS
Real brute force login tool integration
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.hydra")

class HydraResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 found: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.found = found
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'hydra'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    try:
        result = subprocess.run(['hydra'], capture_output=True, text=True, timeout=10)
        for line in result.stderr.split('\n'):
            if 'Hydra v' in line:
                return line.strip()
        return result.stderr.split('\n')[0]
    except Exception as e:
        return f"Error: {e}"

def list_protocols() -> List[str]:
    return [
        'ftp', 'ssh', 'telnet', 'http', 'https', 'http-post-form',
        'smtp', 'smtps', 'pop3', 'pop3s', 'imap', 'imaps',
        'mysql', 'mssql', 'oracle', 'postgres', 'rdp', 'vnc',
        'cisco', 'snmp', 'socks5', 'ldap', 'redis', 'mongodb',
        'sshkey', 'svn', 'teamspeak', 'xmpp', 'irc', 'memcached'
    ]

def get_protocol_help(protocol: str) -> str:
    try:
        result = subprocess.run(['hydra', '-U', protocol], capture_output=True, text=True, timeout=10)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"

def quick_check(target: str, protocol: str, login: str, password: str,
                port: int = None, timeout: int = 30) -> HydraResult:
    cmd = ['hydra', '-l', login, '-p', password, '-f', '-t', '1', target, protocol]
    if port:
        cmd.extend(['-s', str(port)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = result.stdout + result.stderr
        found = 1 if 'password:' in output.lower() or ('login:' in output.lower() and result.returncode == 0) else 0
        return HydraResult(success=True, command=' '.join(cmd), output=output, found=found)
    except Exception as e:
        return HydraResult(success=False, command=' '.join(cmd), error=str(e))

def brute_force(target: str, protocol: str, userlist: str = None, passwordlist: str = None,
                port: int = None, threads: int = 4, timeout: int = 60) -> HydraResult:
    cmd = ['hydra', '-t', str(threads), '-f']
    if userlist:
        cmd.extend(['-L', userlist])
    else:
        cmd.extend(['-l', 'admin'])
    if passwordlist:
        cmd.extend(['-P', passwordlist])
    else:
        cmd.extend(['-P', '/usr/share/wordlists/rockyou.txt'])
    if port:
        cmd.extend(['-s', str(port)])
    cmd.append(target)
    cmd.append(protocol)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = result.stdout + result.stderr
        found = 0
        for line in output.split('\n'):
            if 'password:' in line.lower() and 'login:' in line.lower():
                found += 1
        return HydraResult(success=True, command=' '.join(cmd), output=output[:1000], found=found)
    except subprocess.TimeoutExpired:
        return HydraResult(success=False, command=' '.join(cmd), error="Timeout expired")
    except Exception as e:
        return HydraResult(success=False, command=' '.join(cmd), error=str(e))

def test_default_creds(target: str, protocol: str, port: int = None,
                       common_creds: List[tuple] = None) -> HydraResult:
    if common_creds is None:
        common_creds = [
            ('admin', 'admin'), ('admin', 'password'),
            ('root', 'root'), ('root', 'toor'),
            ('administrator', 'administrator'), ('user', 'user'),
            ('guest', 'guest'),
        ]
    
    found_creds = []
    for login, password in common_creds:
        result = quick_check(target, protocol, login, password, port, timeout=10)
        if result.found > 0:
            found_creds.append((login, password))
    
    output = f"Tested {len(common_creds)} credentials\n"
    if found_creds:
        output += f"Found {len(found_creds)} working:\n"
        for login, password in found_creds:
            output += f"  {login}:{password}\n"
    else:
        output += "No default credentials found"
    
    return HydraResult(success=True, command="default_creds_test", output=output, found=len(found_creds))

def password_strength_analysis(password: str) -> Dict[str, Any]:
    score = 0
    feedback = []
    length = len(password)
    
    if length >= 8:
        score += 1
    else:
        feedback.append("Too short (minimum 8 characters)")
    
    if length >= 12:
        score += 2
    elif length >= 16:
        score += 3
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|<,./>?]', password)
    
    if has_upper:
        score += 1
    else:
        feedback.append("Add uppercase letters")
    if has_lower:
        score += 1
    else:
        feedback.append("Add lowercase letters")
    if has_digit:
        score += 1
    else:
        feedback.append("Add numbers")
    if has_special:
        score += 2
    else:
        feedback.append("Add special characters")
    
    common_patterns = ['123', 'abc', 'qwerty', 'password', 'admin', 'letme']
    for pattern in common_patterns:
        if pattern in password.lower():
            score -= 2
            feedback.append(f"Remove common pattern '{pattern}'")
    
    score = max(0, min(score, 10))
    strength = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong'][min(score, 5)]
    
    return {
        'password': password[:2] + '*' * (len(password) - 2) if len(password) > 2 else '***',
        'length': length,
        'score': score,
        'max_score': 10,
        'strength': strength,
        'feedback': feedback
    }

def estimate_crack_time(password: str) -> str:
    charset_size = 0
    if any(c.isupper() for c in password):
        charset_size += 26
    if any(c.islower() for c in password):
        charset_size += 26
    if any(c.isdigit() for c in password):
        charset_size += 10
    if re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|<,./>?]', password):
        charset_size += 32
    
    if charset_size == 0:
        return "Unknown"
    
    combinations = charset_size ** len(password)
    guesses_per_second = 10**9
    seconds = combinations / guesses_per_second
    
    if seconds < 0.001:
        return "Instant"
    elif seconds < 1:
        return f"{seconds * 1000:.0f} ms"
    elif seconds < 60:
        return f"{seconds:.1f} sec"
    elif seconds < 3600:
        return f"{seconds / 60:.1f} min"
    elif seconds < 86400:
        return f"{seconds / 3600:.1f} hours"
    elif seconds < 2592000:
        return f"{seconds / 86400:.1f} days"
    elif seconds < 31536000:
        return f"{seconds / 2592000:.1f} months"
    elif seconds < 3153600000:
        return f"{seconds / 31536000:.1f} years"
    else:
        return f"{seconds / 3153600000:.0f} million years"

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}
    
    if 'protocol' in query_lower or 'service' in query_lower or 'protocole' in query_lower:
        return {'action': 'protocols', 'success': True, 'protocols': list_protocols()[:15], 'total': len(list_protocols())}
    
    if 'help' in query_lower or 'aide' in query_lower:
        proto_match = re.search(r'(ssh|ftp|http|smtp|pop3|imap|mysql|postgres|rdp|vnc|telnet|cisco|snmp)', query)
        if proto_match:
            help_text = get_protocol_help(proto_match.group(1))
            return {'action': 'protocol_help', 'success': True, 'protocol': proto_match.group(1), 'help': help_text[:500]}
        return {'action': 'protocols', 'success': True, 'protocols': list_protocols()}
    
    if 'test' in query_lower or 'crack' in query_lower or 'brute' in query_lower or 'teste' in query_lower:
        target = None
        protocol = None
        port = None
        
        target_match = re.search(r'(?:de|sur|at|of)\s+([a-zA-Z0-9.-]+\.[a-z]{2,}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', query)
        if target_match:
            target = target_match.group(1)
        
        proto_match = re.search(r'(ssh|ftp|http|smtp|pop3|imap|mysql|postgres|rdp|vnc|telnet|cisco-enable|cisco)', query)
        if proto_match:
            protocol = proto_match.group(1)
        
        port_match = re.search(r'(?:port|poste)\s*:?\s*(\d+)', query)
        if port_match:
            port = int(port_match.group(1))
        
        if not target or not protocol:
            return {'success': False, 'error': 'Target and protocol required',
                   'example': 'test ssh de example.com'}
        
        if 'default' in query_lower or 'défaut' in query_lower:
            result = test_default_creds(target, protocol, port)
            return {'action': 'default_creds', 'success': result.success, 'target': target,
                   'protocol': protocol, 'found': result.found, 'output': result.output}
        
        result = brute_force(target, protocol, port=port, timeout=30)
        return {'action': 'brute_force', 'success': result.success, 'target': target,
               'protocol': protocol, 'found': result.found, 'output': result.output[:500]}
    
    if 'password' in query_lower or 'mot de passe' in query_lower or 'passe' in query_lower:
        # Fixed pattern - capture everything after "mot de passe" or "password"
        pwd_match = re.search(r'(?:mot de passe|password|passe)[\s:=-]+([^\s]+)', query)
        if pwd_match:
            password = pwd_match.group(1).strip('\'"')
        else:
            # Try finding any word that looks like a password
            words = query.split()
            for i, word in enumerate(words):
                if word in ['password', 'passe', 'mdp']:
                    if i + 1 < len(words):
                        password = words[i + 1].strip('\'"')
                        break
            else:
                return {'action': 'password_analysis', 'success': False, 'error': 'No password specified'}
        
        analysis = password_strength_analysis(password)
        crack_time = estimate_crack_time(password)
        return {'action': 'password_analysis', 'success': True, 'analysis': analysis, 'crack_time': crack_time}
    
    if 'crack' in query_lower or 'combien de temps' in query_lower:
        # Extract password from crack time query
        pwd_match = re.search(r'(?:pour|cracker)\s+([^\s]+)', query)
        if pwd_match:
            password = pwd_match.group(1).strip('\'".,!')
            analysis = password_strength_analysis(password)
            crack_time = estimate_crack_time(password)
            return {'action': 'crack_time', 'success': True, 'analysis': analysis, 'crack_time': crack_time}
        return {'action': 'crack_time', 'success': False, 'error': 'No password specified'}
    
    if 'info' in query_lower or 'informations' in query_lower:
        return {'action': 'info', 'success': True, 'version': get_version(),
               'protocols_count': len(list_protocols()),
               'note': 'Brute force requires authorization'}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'test ssh de example.com ou analyse mot de passe secret123'}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'hydra',
        'description': 'THC Hydra - Password brute force tool',
        'category': 'password',
        'supported_queries': [
            'quelle est la version de hydra',
            'liste les protocoles supportés',
            'aide pour ssh',
            'test ssh de example.com',
            'analyse le mot de passe TestPassword123!',
            'combien de temps pour cracker password123',
            'informations sur hydra'
        ],
        'warning': 'Brute force attacks require explicit authorization.',
        'common_protocols': ['ssh', 'ftp', 'http-post-form', 'mysql', 'postgres', 'rdp', 'vnc', 'telnet']
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("hydra Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'protocols':
        print(f"Protocols ({len(list_protocols())}):")
        for p in list_protocols():
            print(f"  - {p}")
    elif cmd == 'analyze':
        if len(sys.argv) > 2:
            password = sys.argv[2]
            analysis = password_strength_analysis(password)
            print(f"Password: {analysis['password']}")
            print(f"Strength: {analysis['strength']}")
            print(f"Crack time: {estimate_crack_time(password)}")
