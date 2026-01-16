"""
strings Wrapper for Sharingan OS
Real string extraction tool integration
"""

import subprocess
import re
import os
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("sharingan.strings")

class StringsResult:
    def __init__(self, success: bool, file: str, strings: List[str] = None, 
                 count: int = 0, output: str = "", error: Optional[str] = None):
        self.success = success
        self.file = file
        self.strings = strings or []
        self.count = count
        self.output = output
        self.error = error

def is_available() -> bool:
    """Check if strings is installed"""
    try:
        result = subprocess.run(['which', 'strings'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def extract_strings(file_path: str, min_length: int = 4, radix: str = None, 
                    all_data: bool = True) -> StringsResult:
    """Extract printable strings from a file"""
    if not os.path.exists(file_path):
        return StringsResult(success=False, file=file_path, error=f"File not found: {file_path}")
    
    cmd = ['strings', '-a' if all_data else '-d']
    
    if min_length > 4:
        cmd.extend(['-n', str(min_length)])
    
    if radix:
        cmd.extend(['-t', radix])
    
    cmd.append(file_path)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout
        
        strings_list = [line for line in output.split('\n') if line.strip()]
        
        return StringsResult(
            success=True,
            file=file_path,
            strings=strings_list,
            count=len(strings_list),
            output=output
        )
    except Exception as e:
        return StringsResult(success=False, file=file_path, output=str(e), error=str(e))

def extract_with_encoding(file_path: str, encoding: str = 's') -> StringsResult:
    """Extract strings with specific encoding"""
    if not os.path.exists(file_path):
        return StringsResult(success=False, file=file_path, error=f"File not found: {file_path}")
    
    cmd = ['strings', '-e', encoding, file_path]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout
        
        strings_list = [line for line in output.split('\n') if line.strip()]
        
        return StringsResult(
            success=True,
            file=file_path,
            strings=strings_list,
            count=len(strings_list),
            output=output
        )
    except Exception as e:
        return StringsResult(success=False, file=file_path, output=str(e), error=str(e))

def quick_strings(file_path: str, count: int = 20) -> StringsResult:
    """Get first N strings from a file"""
    result = extract_strings(file_path, min_length=4)
    
    if result.success:
        result.strings = result.strings[:count]
        result.count = len(result.strings)
        result.output = '\n'.join(result.strings)
    
    return result

def search_strings(file_path: str, pattern: str) -> StringsResult:
    """Search for a pattern in extracted strings"""
    result = extract_strings(file_path, min_length=4)
    
    if result.success:
        matching = [s for s in result.strings if pattern.lower() in s.lower()]
        return StringsResult(
            success=True,
            file=file_path,
            strings=matching,
            count=len(matching),
            output='\n'.join(matching)
        )
    
    return result

def analyze_binary(file_path: str) -> Dict[str, Any]:
    """Analyze a binary file and extract all relevant information"""
    result = extract_strings(file_path, min_length=4, radix='x')
    
    if not result.success:
        return {'success': False, 'error': result.error}
    
    analysis = {
        'file': file_path,
        'total_strings': result.count,
        'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
        'strings_per_kb': round(result.count / (os.path.getsize(file_path) / 1024), 2) if os.path.exists(file_path) else 0,
        'potential_urls': [],
        'potential_ips': [],
        'potential_paths': [],
        'potential_errors': [],
        'interesting_strings': []
    }
    
    for s in result.strings:
        s_lower = s.lower()
        
        if 'http://' in s_lower or 'https://' in s_lower:
            analysis['potential_urls'].append(s)
        elif re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', s):
            analysis['potential_ips'].append(s)
        elif '/' in s and ('/usr/' in s or '/etc/' in s or '/bin/' in s):
            analysis['potential_paths'].append(s)
        elif 'error' in s_lower or 'failed' in s_lower or 'exception' in s_lower:
            analysis['potential_errors'].append(s)
        
        if len(s) > 16:
            analysis['interesting_strings'].append(s)
    
    analysis['urls_count'] = len(analysis['potential_urls'])
    analysis['ips_count'] = len(analysis['potential_ips'])
    analysis['paths_count'] = len(analysis['potential_paths'])
    analysis['errors_count'] = len(analysis['potential_errors'])
    
    return analysis

def handle_nlp_query(query: str) -> Dict[str, Any]:
    """Handle natural language query for string operations"""
    query_lower = query.lower()
    
    file_match = re.search(r'(/[\w/.-]+\.\w+)', query)
    if file_match:
        file_path = file_match.group(1)
    else:
        file_match = re.search(r'([a-zA-Z0-9_-]+\.(bin|exe|so|dll|elf|dat|conf|log|txt))', query)
        if file_match:
            file_path = file_match.group(1)
        else:
            return {'success': False, 'error': 'No file specified', 
                   'example': 'extrais les chaînes de /bin/ls'}
    
    if 'analyse' in query_lower or 'analyze' in query_lower:
        analysis = analyze_binary(file_path)
        return {'action': 'analyze', 'success': analysis.get('success', False),
                'file': file_path, 'analysis': analysis}
    
    if 'cherche' in query_lower or 'search' in query_lower or 'trouve' in query_lower:
        pattern_match = re.search(r'(?:cherche|search|trouve)[\s\w]*["\']?([^"\']+)["\']?', query)
        pattern = pattern_match.group(1).strip() if pattern_match else ''
        if pattern:
            result = search_strings(file_path, pattern)
            return {'action': 'search', 'success': result.success, 'file': file_path,
                   'pattern': pattern, 'count': result.count, 'strings': result.strings[:50]}
        else:
            return {'success': False, 'error': 'No pattern specified'}
    
    if 'premier' in query_lower or 'première' in query_lower or 'first' in query_lower:
        count_match = re.search(r'(\d+)', query)
        count = int(count_match.group(1)) if count_match else 20
        result = quick_strings(file_path, count)
        return {'action': 'quick', 'success': result.success, 'file': file_path,
               'count': result.count, 'strings': result.strings}
    
    if 'url' in query_lower or 'ip' in query_lower:
        result = extract_strings(file_path, min_length=4)
        if result.success:
            urls = [s for s in result.strings if 'http://' in s.lower() or 'https://' in s.lower()]
            ips = [s for s in result.strings if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', s)]
            return {'action': 'extract', 'success': True, 'file': file_path,
                   'urls': urls[:20], 'ips': ips[:20], 'total_strings': result.count}
    
    result = extract_strings(file_path, min_length=4)
    return {'action': 'extract', 'success': result.success, 'file': file_path,
           'count': result.count, 'strings': result.strings[:50]}

def get_status() -> Dict[str, Any]:
    """Get strings wrapper status"""
    return {
        'available': is_available(),
        'name': 'strings',
        'description': 'Extract printable strings from files',
        'category': 'forensics',
        'supported_queries': [
            'extrais les chaînes de /bin/ls',
            'extrais les chaînes de executable.bin',
            'analyse le fichier binary.elf',
            'cherche "password" dans fichier.bin',
            'affiche les 10 premières chaînes de app.exe',
            'trouve les URLs dans le binaire',
            'strings -n 8 /etc/passwd'
        ],
        'options': ['min_length', 'radix', 'encoding', 'all_data']
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("strings Wrapper for Sharingan OS")
        print("Usage: python3 kali_strings_wrapper.py <file> [options]")
        print(f"Available: {is_available()}")
        print("\nOptions:")
        print("  -n <num>    Minimum string length (default: 4)")
        print("  -r <radix>  Radix (o, d, x)")
        print("  -a         Scan all data (default)")
        print("  -e <enc>   Encoding (s, S, b, l, B, L)")
        sys.exit(0)
    
    file_path = sys.argv[1]
    
    if file_path == '-n' or file_path.startswith('-'):
        print("Usage: python3 kali_strings_wrapper.py <file> [options]")
        sys.exit(1)
    
    min_length = 4
    radix = None
    encoding = None
    
    if '-n' in sys.argv:
        idx = sys.argv.index('-n')
        if len(sys.argv) > idx + 1:
            min_length = int(sys.argv[idx + 1])
    
    if '-r' in sys.argv:
        idx = sys.argv.index('-r')
        if len(sys.argv) > idx + 1:
            radix = sys.argv[idx + 1]
    
    if '-e' in sys.argv:
        idx = sys.argv.index('-e')
        if len(sys.argv) > idx + 1:
            encoding = sys.argv[idx + 1]
    
    print(f"File: {file_path}")
    print(f"Min length: {min_length}")
    print(f"Radix: {radix}")
    print(f"Encoding: {encoding}")
    print("-" * 60)
    
    if encoding:
        result = extract_with_encoding(file_path, encoding)
    else:
        result = extract_strings(file_path, min_length, radix)
    
    print(f"Success: {result.success}")
    print(f"Strings found: {result.count}")
    print(f"\nFirst 20 strings:")
    for s in result.strings[:20]:
        print(f"  {s}")
