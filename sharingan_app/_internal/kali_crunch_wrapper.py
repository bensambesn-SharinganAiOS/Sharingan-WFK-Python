"""
Crunch Wrapper for Sharingan OS
Lightweight wordlist generator integration
"""

import subprocess
import re
from typing import Dict, Any, List, Optional, IO
from dataclasses import dataclass
from enum import Enum
import logging
import os
import tempfile

logger = logging.getLogger("sharingan.crunch")

class CrunchPattern(Enum):
    NUMERIC = "numeric"
    ALPHA_LOWER = "alpha_lower"
    ALPHA_UPPER = "alpha_upper"
    ALPHA_MIXED = "alpha_mixed"
    ALPHANUMERIC = "alphanumeric"
    CUSTOM = "custom"

@dataclass
class CrunchResult:
    success: bool
    output_file: Optional[str]
    line_count: int
    size_bytes: int
    command: str
    error: Optional[str] = None

def is_available() -> bool:
    """Check if crunch is installed"""
    try:
        result = subprocess.run(['which', 'crunch'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def generate_wordlist(
    min_length: int = 8,
    max_length: int = 12,
    charset: str = "abcdefghijklmnopqrstuvwxyz0123456789",
    output_file: Optional[str] = None,
    quiet: bool = False
) -> CrunchResult:
    """
    Generate wordlist using crunch
    
    Args:
        min_length: Minimum password length
        max_length: Maximum password length
        charset: Character set to use
        output_file: Output file path (or None for stdout)
        quiet: Suppress output
    
    Returns:
        CrunchResult with generation details
    """
    cmd = ['crunch', str(min_length), str(max_length), charset]
    
    if output_file:
        cmd.extend(['-o', output_file])
    elif quiet:
        cmd.append('-q')
    
    try:
        if output_file:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0 and os.path.exists(output_file):
                size = os.path.getsize(output_file)
                with open(output_file, 'r') as f:
                    line_count = sum(1 for _ in f)
                
                return CrunchResult(
                    success=True,
                    output_file=output_file,
                    line_count=line_count,
                    size_bytes=size,
                    command=' '.join(cmd)
                )
            else:
                return CrunchResult(
                    success=False,
                    output_file=None,
                    line_count=0,
                    size_bytes=0,
                    command=' '.join(cmd),
                    error=result.stderr or "Generation failed"
                )
        else:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            return CrunchResult(
                success=True,
                output_file=None,
                line_count=0,
                size_bytes=0,
                command=' '.join(cmd)
            )
            
    except subprocess.TimeoutExpired:
        return CrunchResult(
            success=False,
            output_file=None,
            line_count=0,
            size_bytes=0,
            command=' '.join(cmd),
            error="Generation timed out"
        )
    except Exception as e:
        logger.error(f"Crunch generation failed: {e}")
        return CrunchResult(
            success=False,
            output_file=None,
            line_count=0,
            size_bytes=0,
            command=' '.join(cmd),
            error=str(e)
        )

def quick_numeric_wordlist(length: int = 4, output_file: Optional[str] = None) -> CrunchResult:
    """Generate numeric wordlist (PIN codes)"""
    return generate_wordlist(length, length, "0123456789", output_file)

def quick_alpha_lower_wordlist(min_len: int, max_len: int, output_file: Optional[str] = None) -> CrunchResult:
    """Generate lowercase alphabetic wordlist"""
    return generate_wordlist(min_len, max_len, "abcdefghijklmnopqrstuvwxyz", output_file)

def quick_alphanumeric_wordlist(min_len: int, max_len: int, output_file: Optional[str] = None) -> CrunchResult:
    """Generate alphanumeric wordlist"""
    return generate_wordlist(min_len, max_len, "abcdefghijklmnopqrstuvwxyz0123456789", output_file)

def parse_charset_from_query(query: str) -> str:
    """Extract charset from natural language query"""
    query_lower = query.lower()
    
    charset_map = {
        'numérique': '0123456789',
        'numbers': '0123456789',
        'digits': '0123456789',
        'chiffres': '0123456789',
        'minuscule': 'abcdefghijklmnopqrstuvwxyz',
        'lowercase': 'abcdefghijklmnopqrstuvwxyz',
        'majuscule': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'uppercase': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'alphanumérique': 'abcdefghijklmnopqrstuvwxyz0123456789',
        'alphanumeric': 'abcdefghijklmnopqrstuvwxyz0123456789',
        'mixte': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
        'mixed': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
        'spécial': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*',
        'special': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*',
    }
    
    for key, charset in charset_map.items():
        if key in query_lower:
            return charset
    
    return "abcdefghijklmnopqrstuvwxyz0123456789"

def parse_length_from_query(query: str) -> tuple:
    """Extract min/max length from natural language query"""
    query_lower = query.lower()
    
    length_patterns = [
        (r'(\d+)\s*(?:à|a|to|-)\s*(\d+)\s*(?:caractères|chars|caracteres|digits|chiffres)', 2),
        (r'(\d+)\s*(?:à|a|to|-)\s*(\d+)', 2),
        (r'(\d+)\s*(?:caractères|chars|caracteres|digits|chiffres)', 1),
        (r'longueur\s*(\d+)\s*(?:à|a|to|-)\s*(\d+)', 2),
        (r'(\d+)\s*et\s*(\d+)', 2),
    ]
    
    for pattern, group_count in length_patterns:
        match = re.search(pattern, query_lower)
        if match:
            if group_count == 2:
                return int(match.group(1)), int(match.group(2))
            else:
                length = int(match.group(1))
                return length, length
    
    return 8, 12

def handle_nlp_query(query: str) -> Dict[str, Any]:
    """Handle natural language query for wordlist generation"""
    min_len, max_len = parse_length_from_query(query)
    charset = parse_charset_from_query(query)
    
    output_file = None
    if 'sauve' in query.lower() or 'fichier' in query.lower() or 'output' in query.lower():
        output_file = tempfile.mktemp(suffix='.txt')
    
    result = generate_wordlist(min_len, max_len, charset, output_file)
    
    return {
        'success': result.success,
        'command': result.command,
        'min_length': min_len,
        'max_length': max_len,
        'charset': charset,
        'output_file': result.output_file,
        'line_count': result.line_count,
        'size_bytes': result.size_bytes,
        'error': result.error
    }

def get_status() -> Dict[str, Any]:
    """Get crunch wrapper status"""
    return {
        'available': is_available(),
        'name': 'crunch',
        'description': 'Wordlist generator',
        'category': 'password',
        'supported_queries': [
            'génère une wordlist de 8 à 12 caractères',
            'crunch 8 12 abcdefgh',
            'crée une wordlist numérique de 4 chiffres',
            'générateur de mots de passe',
            'wordlist alphanumeric 6-8'
        ]
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Crunch Wrapper for Sharingan OS")
        print("Usage: python3 kali_crunch_wrapper.py <min> <max> [charset]")
        print(f"Available: {is_available()}")
        print("\nExamples:")
        print("  python3 kali_crunch_wrapper.py 8 12 abcdefgh")
        print("  python3 kali_crunch_wrapper.py 4 4 0123456789")
        sys.exit(0)
    
    if len(sys.argv) >= 3:
        min_len = int(sys.argv[1])
        max_len = int(sys.argv[2])
        charset = sys.argv[3] if len(sys.argv) > 3 else "abcdefghijklmnopqrstuvwxyz0123456789"
        
        print(f"Generating wordlist: {min_len}-{max_len} chars with charset: {charset}")
        result = generate_wordlist(min_len, max_len, charset)
        
        print(f"\n{'='*60}")
        print(f"Success: {result.success}")
        print(f"Command: {result.command}")
        if result.output_file:
            print(f"Output: {result.output_file}")
            print(f"Lines: {result.line_count}")
            print(f"Size: {result.size_bytes} bytes")
        if result.error:
            print(f"Error: {result.error}")
        print(f"{'='*60}")
    else:
        print("Usage: python3 kali_crunch_wrapper.py <min> <max> [charset]")
