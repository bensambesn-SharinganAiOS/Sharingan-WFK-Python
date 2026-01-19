#!/usr/bin/env python3
"""
hashid Wrapper for Sharingan OS
Real hash type identification tool
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.hashid")

class HashidResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 hashes: Optional[List[str]] = None, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.hashes = hashes or []
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'hashid'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    try:
        result = subprocess.run(['hashid', '--version'], capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def identify_hash(hash_value: str, extended: bool = False) -> HashidResult:
    cmd = ['hashid']
    if extended:
        cmd.append('-e')
    cmd.append(hash_value)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        hashes = []
        for line in output.split('\n'):
            if '[+]' in line or '[!]' in line:
                hashes.append(line.strip())
        return HashidResult(success=True, command=' '.join(cmd),
                           output=output, hashes=hashes)
    except Exception as e:
        return HashidResult(success=False, command=' '.join(cmd), error=str(e))

def identify_hash_file(file_path: str, extended: bool = False) -> HashidResult:
    if not os.path.exists(file_path):
        return HashidResult(success=False, error=f"File not found: {file_path}")
    
    cmd = ['hashid', '-f']
    if extended:
        cmd.append('-e')
    cmd.append(file_path)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return HashidResult(success=True, command=' '.join(cmd), output=output)
    except Exception as e:
        return HashidResult(success=False, command=' '.join(cmd), error=str(e))

def get_help() -> str:
    try:
        result = subprocess.run(['hashid', '--help'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}
    
    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}
    
    if 'identify' in query_lower or 'identifie' in query_lower or 'quel type' in query_lower:
        extended = 'extended' in query_lower or '-e' in query_lower
        
        hash_match = re.search(r'([a-fA-F0-9$:+/\.]{8,})', query)
        if hash_match:
            hash_value = hash_match.group(1)
            result = identify_hash(hash_value, extended)
            return {'action': 'identify', 'success': result.success,
                   'hash': hash_value, 'types': result.hashes, 'output': result.output[:500]}
        
        file_match = re.search(r'(?:file|fichier)\s*:?\s*(\S+)', query)
        if file_match:
            file_path = file_match.group(1)
            result = identify_hash_file(file_path, extended)
            return {'action': 'identify_file', 'success': result.success,
                   'file': file_path, 'output': result.output[:500]}
        
        return {'action': 'identify', 'success': False,
               'error': 'No hash or file specified',
               'example': 'identify 5d41402abc4b2a76b9719d911017c592'}
    
    if 'info' in query_lower or 'informations' in query_lower:
        return {'action': 'info', 'success': True, 'version': get_version(),
               'note': 'Hash identification tool for security analysis'}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'identify 5d41402abc4b2a76b9719d911017c592'}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'hashid',
        'description': 'Hash type identification tool',
        'category': 'password',
        'supported_queries': [
            'quelle est la version de hashid',
            'identify 5d41402abc4b2a76b9719d911017c592',
            'quel type de hash est 5d41402abc4b2a76b9719d911017c592',
            'hashid help',
            'informations sur hashid'
        ],
        'warning': 'Use for security analysis only.',
        'example_hashes': [
            '5d41402abc4b2a76b9719d911017c592 (MD5)',
            'e10adc3949ba59abbe56e057f20f883e (MD5)',
            '21232f297a57a5a743894a0e4a801fc3 (MD5 admin)'
        ]
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("hashid Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'identify':
        if len(sys.argv) > 2:
            result = identify_hash(sys.argv[2])
            print(f"Hash: {sys.argv[2]}")
            for h in result.hashes:
                print(h)
    elif cmd == 'help':
        print(get_help())
