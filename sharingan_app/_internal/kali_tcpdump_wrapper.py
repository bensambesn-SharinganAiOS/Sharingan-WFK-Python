"""
tcpdump Wrapper for Sharingan OS
Real packet sniffer integration
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.tcpdump")

class TcpdumpResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 packets_captured: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.packets_captured = packets_captured
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'tcpdump'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    try:
        result = subprocess.run(['tcpdump', '--version'], capture_output=True, text=True, timeout=10)
        first_line = result.stdout.split('\n')[0]
        return first_line.strip()
    except Exception as e:
        return f"Error: {e}"

def list_interfaces() -> List[str]:
    try:
        result = subprocess.run(['tcpdump', '-D'], capture_output=True, text=True, timeout=10)
        interfaces = []
        for line in result.stdout.split('\n'):
            if re.match(r'^\d+\.', line):
                iface = line.split('.', 1)[1].strip().split()[0]
                interfaces.append(iface)
        return interfaces if interfaces else ['any']
    except Exception:
        return ['any']

def capture_packets(interface: str = "any", count: int = 10, timeout: int = 30,
                    filter_expr: str = None, promisc: bool = False) -> TcpdumpResult:
    cmd = ['tcpdump', '-i', interface, '-c', str(count), '-l']
    
    if promisc:
        cmd.append('-p')
    else:
        cmd.append('-nn')
    
    if filter_expr:
        cmd.extend(['-w', '/dev/stdout'])
        cmd.append(filter_expr)
    else:
        cmd.extend(['-q', '-tttt'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = result.stdout + result.stderr
        packets = 0
        for line in output.split('\n'):
            if re.match(r'^\d+:\d+:\d+\.\d+', line):
                packets += 1
        return TcpdumpResult(success=True, command=' '.join(cmd),
                            output=output[:2000], packets_captured=packets)
    except subprocess.TimeoutExpired:
        return TcpdumpResult(success=False, command=' '.join(cmd),
                            error="Capture timeout expired")
    except Exception as e:
        return TcpdumpResult(success=False, command=' '.join(cmd), error=str(e))

def capture_to_file(interface: str, output_file: str, count: int = 100,
                    filter_expr: str = None) -> TcpdumpResult:
    cmd = ['tcpdump', '-i', interface, '-w', output_file, '-c', str(count)]
    
    if filter_expr:
        cmd.append(filter_expr)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        return TcpdumpResult(success=result.returncode == 0,
                            command=' '.join(cmd), output=output)
    except Exception as e:
        return TcpdumpResult(success=False, command=' '.join(cmd), error=str(e))

def read_pcap(pcap_file: str, count: int = 20, filter_expr: str = None) -> TcpdumpResult:
    cmd = ['tcpdump', '-r', pcap_file, '-c', str(count), '-nn']
    
    if filter_expr:
        cmd.append(filter_expr)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        packets = len([l for l in output.split('\n') if l.strip()])
        return TcpdumpResult(success=True, command=' '.join(cmd),
                            output=output[:2000], packets_captured=packets)
    except Exception as e:
        return TcpdumpResult(success=False, command=' '.join(cmd), error=str(e))

def filter_packets(filter_expr: str, pcap_file: str = None, interface: str = "any",
                   count: int = 20) -> TcpdumpResult:
    if pcap_file:
        return read_pcap(pcap_file, count, filter_expr)
    else:
        return capture_packets(interface, count, filter_expr=filter_expr)

def get_help() -> str:
    try:
        result = subprocess.run(['tcpdump', '-h'], capture_output=True, text=True, timeout=10)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"

def get_filter_help() -> str:
    try:
        result = subprocess.run(['tcpdump', '--help'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}
    
    if 'interface' in query_lower or 'interfaces' in query_lower or 'iface' in query_lower:
        ifaces = list_interfaces()
        return {'action': 'interfaces', 'success': True, 'interfaces': ifaces}
    
    if 'capture' in query_lower or 'sniff' in query_lower or 'flairer' in query_lower:
        interface = "any"
        count = 10
        
        iface_match = re.search(r'(?:interface|iface|sur)\s*:?\s*(\w+)', query)
        if iface_match:
            interface = iface_match.group(1)
        
        count_match = re.search(r'(\d+)\s+(?:paquet|packets?)', query)
        if count_match:
            count = int(count_match.group(1))
        
        result = capture_packets(interface, count, timeout=30)
        return {'action': 'capture', 'success': result.success,
               'interface': interface, 'packets': result.packets_captured,
               'output': result.output[:500]}
    
    if 'read' in query_lower or 'lire' in query_lower or 'analyse.*pcap' in query_lower:
        pcap_match = re.search(r'(?:pcap|fichier|capture)\s*:?\s*(\S+)', query)
        if pcap_match:
            pcap_file = pcap_match.group(1)
            if os.path.exists(pcap_file):
                result = read_pcap(pcap_file)
                return {'action': 'read_pcap', 'success': result.success,
                       'file': pcap_file, 'packets': result.packets_captured,
                       'output': result.output[:500]}
            else:
                return {'action': 'read_pcap', 'success': False,
                       'error': f'File not found: {pcap_file}'}
        return {'action': 'read_pcap', 'success': False,
               'error': 'No pcap file specified', 'example': 'analyse capture.pcap'}
    
    if 'filter' in query_lower or 'filtre' in query_lower or 'tcp' in query_lower or 'udp' in query_lower:
        filter_expr = None
        
        tcp_match = re.search(r'tcp', query_lower)
        udp_match = re.search(r'udp', query_lower)
        port_match = re.search(r'port\s*(\d+)', query_lower)
        host_match = re.search(r'host\s+([a-zA-Z0-9.-]+)', query_lower)
        
        filters = []
        if tcp_match:
            filters.append('tcp')
        if udp_match:
            filters.append('udp')
        if port_match:
            filters.append(f'port {port_match.group(1)}')
        if host_match:
            filters.append(f'host {host_match.group(1)}')
        
        if filters:
            filter_expr = ' and '.join(filters)
        
        result = filter_packets(filter_expr or "tcp", interface="any", count=10)
        return {'action': 'filter', 'success': result.success,
               'filter': filter_expr, 'packets': result.packets_captured,
               'output': result.output[:500]}
    
    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}
    
    if 'info' in query_lower or 'informations' in query_lower:
        return {'action': 'info', 'success': True, 'version': get_version(),
               'interfaces': list_interfaces(),
               'note': 'Packet capture requires root privileges'}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'capture 20 packets ou analyse capture.pcap ou filtre tcp port 80'}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'tcpdump',
        'description': 'Packet analyzer and sniffer',
        'category': 'network',
        'supported_queries': [
            'quelle est la version de tcpdump',
            'liste les interfaces réseau',
            'capture 20 packets sur eth0',
            'analyse capture.pcap',
            'filtre tcp port 80',
            'aide tcpdump',
            'informations sur tcpdump'
        ],
        'warning': 'Packet capture requires root privileges.',
        'common_filters': ['tcp', 'udp', 'port 80', 'host example.com', 'port 22 and tcp']
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("tcpdump Wrapper - Available:", is_available())
        print("Version:", get_version())
        print("Interfaces:", list_interfaces())
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'interfaces':
        print(f"Interfaces: {list_interfaces()}")
    elif cmd == 'capture':
        result = capture_packets()
        print(f"Captured: {result.packets_captured} packets")
        print(result.output[:500])
    elif cmd == 'help':
        print(get_help())
