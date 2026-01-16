"""
sqlmap Wrapper for Sharingan OS
Automated SQL injection testing tool
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.sqlmap")


class SqlmapResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 vulnerabilities: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.vulnerabilities = vulnerabilities
        self.error = error


def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'sqlmap'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False


def get_version() -> str:
    try:
        result = subprocess.run(['sqlmap', '--version'], capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def scan_target(url: str, level: int = 1, risk: int = 1,
                dump: bool = False) -> SqlmapResult:
    cmd = ['sqlmap', '-u', url, '--batch', '--threads=4']

    if level > 1:
        cmd.extend(['--level', str(level)])
    if risk > 1:
        cmd.extend(['--risk', str(risk)])
    if dump:
        cmd.append('--dump')

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        vulns = output.lower().count('vulnerable') + output.lower().count(' Injection')
        return SqlmapResult(success=True, command=' '.join(cmd),
                          output=output[:5000], vulnerabilities=vulns)
    except subprocess.TimeoutExpired:
        return SqlmapResult(success=False, command=' '.join(cmd),
                           error="Scan timeout expired (5min)")
    except Exception as e:
        return SqlmapResult(success=False, command=' '.join(cmd), error=str(e))


def get_databases(url: str) -> SqlmapResult:
    cmd = ['sqlmap', '-u', url, '--batch', '--dbs']

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        return SqlmapResult(success=True, command=' '.join(cmd), output=output[:5000])
    except Exception as e:
        return SqlmapResult(success=False, command=' '.join(cmd), error=str(e))


def get_tables(url: str, database: str) -> SqlmapResult:
    cmd = ['sqlmap', '-u', url, '--batch', '-D', database, '--tables']

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        return SqlmapResult(success=True, command=' '.join(cmd), output=output[:5000])
    except Exception as e:
        return SqlmapResult(success=False, command=' '.join(cmd), error=str(e))


def get_help() -> str:
    try:
        result = subprocess.run(['sqlmap', '--help'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()

    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}

    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}

    if 'scan' in query_lower or 'test' in query_lower or 'vuln' in query_lower:
        url_match = re.search(r'(https?://[^\s\'"]+|www\.[^\s\'"]+)', query)
        if url_match:
            url = url_match.group(1)
            level = 3 if 'deep' in query_lower or 'complet' in query_lower else 1
            risk = 3 if 'aggressive' in query_lower else 1
            dump = 'dump' in query_lower or 'database' in query_lower

            result = scan_target(url, level=level, risk=risk, dump=dump)
            return {'action': 'scan', 'success': result.success,
                   'url': url, 'vulnerabilities': result.vulnerabilities,
                   'output': result.output[:500]}

        return {'action': 'scan', 'success': False,
               'error': 'URL required', 'example': 'scan http://example.com'}

    if 'databases' in query_lower or 'bases' in query_lower:
        url_match = re.search(r'(https?://[^\s\'"]+)', query)
        if url_match:
            url = url_match.group(1)
            result = get_databases(url)
            return {'action': 'databases', 'success': result.success,
                   'output': result.output[:500]}

    if 'tables' in query_lower:
        url_match = re.search(r'(https?://[^\s\'"]+)', query)
        db_match = re.search(r'(?:base|database|db)[:\s]+(\w+)', query)
        if url_match and db_match:
            url = url_match.group(1)
            database = db_match.group(1)
            result = get_tables(url, database)
            return {'action': 'tables', 'success': result.success,
                   'database': database, 'output': result.output[:500]}

    return {'success': False, 'error': 'Command not recognized',
           'example': 'scan http://example.com'}


def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'sqlmap',
        'description': 'Automated SQL injection tool',
        'category': 'web',
        'supported_queries': [
            'quelle est la version de sqlmap',
            'scan http://example.com',
            'sqlmap http://example.com',
            'test sql injection on http://example.com',
            'get databases of http://example.com',
            'sqlmap help'
        ],
        'warning': 'Only use on systems you own or have permission to test.',
        'features': ['scan URL', 'enumerate databases', 'dump tables', 'test injection']
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("sqlmap Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'scan':
        if len(sys.argv) > 2:
            result = scan_target(sys.argv[2])
            print(f"URL: {sys.argv[2]}")
            print(f"Vulnerabilities: {result.vulnerabilities}")
            print(result.output[:500])
    elif cmd == 'help':
        print(get_help())
