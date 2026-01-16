"""
xxd Wrapper for Sharingan OS
Real hex dump and conversion tool integration
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.xxd")

class XxdResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 lines: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.lines = lines
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'xxd'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    try:
        result = subprocess.run(['xxd', '--version'], capture_output=True, text=True, timeout=10)
        first_line = result.stdout.split('\n')[0]
        return first_line.strip()
    except Exception as e:
        return f"Error: {e}"

def hex_dump(file_path: str, length: Optional[int] = None, offset: Optional[int] = None,
             columns: int = 16) -> XxdResult:
    if not os.path.exists(file_path):
        return XxdResult(success=False, error=f"File not found: {file_path}")
    
    cmd = ['xxd']
    
    if length:
        cmd.extend(['-l', str(length)])
    if offset:
        cmd.extend(['-s', str(offset)])
    if columns != 16:
        cmd.extend(['-c', str(columns)])
    
    cmd.append(file_path)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        lines = len(output.split('\n'))
        return XxdResult(success=True, command=' '.join(cmd),
                        output=output[:2000], lines=lines)
    except Exception as e:
        return XxdResult(success=False, command=' '.join(cmd), error=str(e))

def hex_create(data: str, output_file: Optional[str] = None) -> XxdResult:
    cmd = ['xxd', '-p']
    
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate(input=data)
        
        if proc.returncode != 0:
            return XxdResult(success=False, command=' '.join(cmd),
                           error=stderr)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(stdout)
            return XxdResult(success=True, command=' '.join(cmd),
                           output=f"Written to {output_file}", lines=1)
        
        return XxdResult(success=True, command=' '.join(cmd), output=stdout[:1000])
    except Exception as e:
        return XxdResult(success=False, command=' '.join(cmd), error=str(e))

def reverse_hex(hex_string: str, output_file: Optional[str] = None) -> XxdResult:
    cmd = ['xxd', '-r', '-p']
    
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate(input=hex_string)
        
        if proc.returncode != 0:
            return XxdResult(success=False, command=' '.join(cmd),
                           error=stderr)
        
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(stdout.encode())
            return XxdResult(success=True, command=' '.join(cmd),
                           output=f"Written to {output_file}")
        
        return XxdResult(success=True, command=' '.join(cmd), output=stdout[:1000])
    except Exception as e:
        return XxdResult(success=False, command=' '.join(cmd), error=str(e))

def binary_diff(file1: str, file2: str) -> XxdResult:
    if not os.path.exists(file1):
        return XxdResult(success=False, error=f"File not found: {file1}")
    if not os.path.exists(file2):
        return XxdResult(success=False, error=f"File not found: {file2}")
    
    cmd = ['xxd', file1]
    cmd2 = ['xxd', file2]
    
    try:
        result1 = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=30)
        
        diff_cmd = ['diff', '-u']
        proc = subprocess.Popen(diff_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate(input=result1.stdout + result2.stdout)
        
        return XxdResult(success=True, command='xxd diff',
                        output=stdout[:2000] if stdout else "Files are identical")
    except Exception as e:
        return XxdResult(success=False, error=str(e))

def get_help() -> str:
    try:
        result = subprocess.run(['xxd', '--help'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}
    
    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}
    
    if 'hex dump' in query_lower or 'hexdump' in query_lower or 'affiche' in query_lower:
        file_match = re.search(r'(?:file|fichier|du\s+fichier)\s*:?\s*(\S+)', query)
        if file_match:
            file_path = file_match.group(1)
            result = hex_dump(file_path)
            return {'action': 'hex_dump', 'success': result.success,
                   'file': file_path, 'lines': result.lines, 'output': result.output[:500]}
        
        file_match = re.search(r'(\S+\.(bin|dat|exe|elf|img|png|jpg|hex))', query)
        if file_match:
            file_path = file_match.group(1)
            result = hex_dump(file_path)
            return {'action': 'hex_dump', 'success': result.success,
                   'file': file_path, 'lines': result.lines, 'output': result.output[:500]}
        
        return {'action': 'hex_dump', 'success': False,
               'error': 'No file specified', 'example': 'hex dump de fichier.bin'}
    
    if 'hex' in query_lower and ('create' in query_lower or 'convert' in query_lower or 'convertir' in query_lower):
        data_match = re.search(r'(?:data|données|texte)\s*:?\s*(\S+)', query)
        if data_match:
            result = hex_create(data_match.group(1))
            return {'action': 'hex_create', 'success': result.success,
                   'output': result.output}
        
        text_match = re.search(r'["\']([^"\']+)["\']', query)
        if text_match:
            result = hex_create(text_match.group(1))
            return {'action': 'hex_create', 'success': result.success,
                   'output': result.output}
        
        return {'action': 'hex_create', 'success': False,
               'error': 'No text specified'}
    
    if 'reverse' in query_lower or 'decompile' in query_lower or 'binary' in query_lower:
        hex_match = re.search(r'([a-fA-F0-9\s]+)', query)
        if hex_match:
            result = reverse_hex(hex_match.group(1).replace(' ', ''))
            return {'action': 'reverse_hex', 'success': result.success,
                   'output': result.output[:500]}
        
        return {'action': 'reverse_hex', 'success': False,
               'error': 'No hex string specified'}
    
    if 'diff' in query_lower or 'compare' in query_lower or 'comparer' in query_lower:
        file1_match = re.search(r'(?:file1|fichier1)\s*:?\s*(\S+)', query)
        file2_match = re.search(r'(?:file2|fichier2)\s*:?\s*(\S+)', query)
        
        if file1_match and file2_match:
            result = binary_diff(file1_match.group(1), file2_match.group(1))
            return {'action': 'binary_diff', 'success': result.success,
                   'output': result.output[:500]}
        
        return {'action': 'binary_diff', 'success': False,
               'error': 'Two files required', 'example': 'diff file1.bin file2.bin'}
    
    if 'info' in query_lower or 'informations' in query_lower:
        return {'action': 'info', 'success': True, 'version': get_version(),
               'note': 'Hex dump and binary analysis tool'}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'hex dump de fichier.bin'}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'xxd',
        'description': 'Hex dump and binary analysis tool',
        'category': 'forensics',
        'supported_queries': [
            'quelle est la version de xxd',
            'hex dump de fichier.bin',
            'xxd help',
            'hex create "hello world"',
            'reverse hex 48656c6c6f',
            'diff file1.bin file2.bin',
            'informations sur xxd'
        ],
        'warning': 'Use for legitimate security analysis only.',
        'features': ['hex dump', 'hex create', 'reverse hex', 'binary diff']
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("xxd Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'hexdump':
        if len(sys.argv) > 2:
            result = hex_dump(sys.argv[2])
            print(f"File: {sys.argv[2]}")
            print(f"Lines: {result.lines}")
            print(result.output[:500])
    elif cmd == 'help':
        print(get_help())
