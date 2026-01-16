"""
dnsrecon Wrapper for Sharingan OS
DNS enumeration and reconnaissance tool
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.dnsrecon")


class DnsreconResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 records_found: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.records_found = records_found
        self.error = error


def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'dnsrecon'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False


def get_version() -> str:
    try:
        result = subprocess.run(['dnsrecon', '--version'], capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def enumerate_domain(domain: str, type: str = "std") -> DnsreconResult:
    cmd = ['dnsrecon', '-d', domain, '-t', type]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        records = output.lower().count('record') + output.count('[')
        return DnsreconResult(success=True, command=' '.join(cmd),
                             output=output[:5000], records_found=records)
    except subprocess.TimeoutExpired:
        return DnsreconResult(success=False, command=' '.join(cmd),
                             error="Enumeration timeout")
    except Exception as e:
        return DnsreconResult(success=False, command=' '.join(cmd), error=str(e))


def brute_force(domain: str, wordlist: str = None) -> DnsreconResult:
    cmd = ['dnsrecon', '-d', domain, '-t', 'brt']
    if wordlist:
        cmd.extend(['-w', wordlist])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        return DnsreconResult(success=True, command=' '.join(cmd),
                             output=output[:5000])
    except Exception as e:
        return DnsreconResult(success=False, command=' '.join(cmd), error=str(e))


def reverse_lookup(ip_range: str) -> DnsreconResult:
    cmd = ['dnsrecon', '-r', ip_range]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        return DnsreconResult(success=True, command=' '.join(cmd),
                             output=output[:5000])
    except Exception as e:
        return DnsreconResult(success=False, command=' '.join(cmd), error=str(e))


def zone_transfer(domain: str) -> DnsreconResult:
    cmd = ['dnsrecon', '-d', domain, '-t', 'axfr']

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        success = 'AXFR' in output or 'zone transfer' in output.lower()
        return DnsreconResult(success=success, command=' '.join(cmd),
                             output=output[:5000])
    except Exception as e:
        return DnsreconResult(success=False, command=' '.join(cmd), error=str(e))


def get_help() -> str:
    try:
        result = subprocess.run(['dnsrecon', '-h'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()

    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}

    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}

    if 'enum' in query_lower or 'scan' in query_lower or 'trouve' in query_lower:
        domain_match = re.search(r'([a-zA-Z0-9.-]+\.[a-z]{2,})', query)
        if domain_match:
            domain = domain_match.group(1)

            if 'zone transfer' in query_lower or 'axfr' in query_lower:
                result = zone_transfer(domain)
                return {'action': 'zone_transfer', 'success': result.success,
                       'domain': domain, 'output': result.output[:500]}

            if 'brute' in query_lower or 'force' in query_lower:
                result = brute_force(domain)
                return {'action': 'brute', 'success': result.success,
                       'domain': domain, 'output': result.output[:500]}

            result = enumerate_domain(domain)
            return {'action': 'enumerate', 'success': result.success,
                   'domain': domain, 'records_found': result.records_found,
                   'output': result.output[:500]}

        return {'action': 'enumerate', 'success': False,
               'error': 'Domain required', 'example': 'enumerate example.com'}

    if 'reverse' in query_lower or 'ip' in query_lower:
        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})', query)
        if ip_match:
            ip_range = ip_match.group(1)
            result = reverse_lookup(ip_range)
            return {'action': 'reverse', 'success': result.success,
                   'range': ip_range, 'output': result.output[:500]}

    if 'zone transfer' in query_lower:
        domain_match = re.search(r'([a-zA-Z0-9.-]+\.[a-z]{2,})', query)
        if domain_match:
            domain = domain_match.group(1)
            result = zone_transfer(domain)
            return {'action': 'zone_transfer', 'success': result.success,
                   'domain': domain, 'output': result.output[:500]}

    return {'success': False, 'error': 'Command not recognized',
           'example': 'enumerate example.com'}


def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'dnsrecon',
        'description': 'DNS enumeration and reconnaissance',
        'category': 'recon',
        'supported_queries': [
            'quelle est la version de dnsrecon',
            'enumerate example.com',
            'dnsrecon example.com',
            'zone transfer example.com',
            'brute force subdomains example.com',
            'dnsrecon help'
        ],
        'warning': 'Use for authorized reconnaissance only.',
        'features': ['enumerate records', 'brute force', 'zone transfer', 'reverse lookup']
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("dnsrecon Wrapper - Available:", is_available())
        print("Version:", get_version())
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'enumerate':
        if len(sys.argv) > 2:
            domain = sys.argv[2]
            result = enumerate_domain(domain)
            print(f"Domain: {domain}")
            print(f"Records found: {result.records_found}")
            print(result.output[:500])
    elif cmd == 'zone_transfer':
        if len(sys.argv) > 2:
            domain = sys.argv[2]
            result = zone_transfer(domain)
            print(f"Domain: {domain}")
            print(result.output[:500])
    elif cmd == 'help':
        print(get_help())
