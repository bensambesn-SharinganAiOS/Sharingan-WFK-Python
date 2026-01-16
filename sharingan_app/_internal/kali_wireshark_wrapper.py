"""
wireshark Wrapper for Sharingan OS
GUI packet analyzer (uses tshark CLI for operations)
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.wireshark")

class WiresharkResult:
    def __init__(self, success: bool, command: str = "", output: str = "",
                 packets_count: int = 0, error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.packets_count = packets_count
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'wireshark'], capture_output=True, timeout=5)
        if result.returncode == 0:
            return True
        result = subprocess.run(['which', 'tshark'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    try:
        result = subprocess.run(['wireshark', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            result = subprocess.run(['tshark', '--version'], capture_output=True, text=True, timeout=10)
        first_line = result.stdout.split('\n')[0]
        return first_line.strip()
    except Exception as e:
        return f"Error: {e}"

def get_tshark_path() -> str:
    try:
        result = subprocess.run(['which', 'tshark'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return "tshark"

def list_interfaces() -> List[str]:
    try:
        result = subprocess.run([get_tshark_path(), '-D'], capture_output=True, text=True, timeout=10)
        interfaces = []
        for line in result.stdout.split('\n'):
            if re.match(r'^\d+\.', line):
                iface = line.split('.', 1)[1].strip().split()[0]
                interfaces.append(iface)
        return interfaces if interfaces else ['eth0', 'any']
    except Exception:
        return ['eth0', 'any']

def capture_packets(interface: str = "any", count: int = 100, timeout: int = 60,
                    filter_expr: Optional[str] = None) -> WiresharkResult:
    cmd = [get_tshark_path(), '-i', interface, '-c', str(count)]
    
    if filter_expr:
        cmd.extend(['-f', filter_expr])
    
    cmd.extend(['-T', 'fields', '-e', 'frame.time', '-e', 'ip.src', '-e', 'ip.dst',
                '-e', 'ip.proto', '-e', 'tcp.srcport', '-e', 'tcp.dstport',
                '-e', 'udp.srcport', '-e', 'udp.dstport', '-e', '_ws'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = result.stdout + result.stderr
        packets = len([l for l in output.split('\n') if l.strip()])
        return WiresharkResult(success=True, command=' '.join(cmd),
                              output=output[:3000], packets_count=packets)
    except subprocess.TimeoutExpired:
        return WiresharkResult(success=False, command=' '.join(cmd),
                              error="Capture timeout expired")
    except Exception as e:
        return WiresharkResult(success=False, command=' '.join(cmd), error=str(e))

def analyze_pcap(pcap_file: str, count: int = 50, filter_expr: Optional[str] = None) -> WiresharkResult:
    if not os.path.exists(pcap_file):
        return WiresharkResult(success=False, error=f"File not found: {pcap_file}")
    
    cmd = [get_tshark_path(), '-r', pcap_file, '-c', str(count)]
    
    if filter_expr:
        cmd.extend(['-Y', filter_expr])
    
    cmd.extend(['-T', 'fields', '-e', 'frame.time', '-e', 'ip.src', '-e', 'ip.dst',
                '-e', 'ip.proto', '-e', 'tcp.port', '-e', 'udp.port', '-e', '_ws.col.Info'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        packets = len([l for l in output.split('\n') if l.strip()])
        return WiresharkResult(success=True, command=' '.join(cmd),
                              output=output[:3000], packets_count=packets)
    except Exception as e:
        return WiresharkResult(success=False, command=' '.join(cmd), error=str(e))

def extract_conversations(pcap_file: str, protocol: str = "tcp") -> WiresharkResult:
    if not os.path.exists(pcap_file):
        return WiresharkResult(success=False, error=f"File not found: {pcap_file}")
    
    cmd = [get_tshark_path(), '-r', pcap_file, '-q', '-z', f'conv,{protocol}']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        return WiresharkResult(success=True, command=' '.join(cmd),
                              output=output[:3000])
    except Exception as e:
        return WiresharkResult(success=False, command=' '.join(cmd), error=str(e))

def extract_http_requests(pcap_file: str) -> WiresharkResult:
    if not os.path.exists(pcap_file):
        return WiresharkResult(success=False, error=f"File not found: {pcap_file}")
    
    cmd = [get_tshark_path(), '-r', pcap_file, '-Y', 'http.request',
           '-T', 'fields', '-e', 'frame.time', '-e', 'http.host', '-e', 'http.request.uri',
           '-e', 'http.request.method', '-e', 'http.user_agent']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        packets = len([l for l in output.split('\n') if l.strip()])
        return WiresharkResult(success=True, command=' '.join(cmd),
                              output=output[:3000], packets_count=packets)
    except Exception as e:
        return WiresharkResult(success=False, command=' '.join(cmd), error=str(e))

def extract_dns_queries(pcap_file: str) -> WiresharkResult:
    if not os.path.exists(pcap_file):
        return WiresharkResult(success=False, error=f"File not found: {pcap_file}")
    
    cmd = [get_tshark_path(), '-r', pcap_file, '-Y', 'dns',
           '-T', 'fields', '-e', 'frame.time', '-e', 'dns.qry.name',
           '-e', 'dns.qry.type', '-e', 'dns.a']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        packets = len([l for l in output.split('\n') if l.strip()])
        return WiresharkResult(success=True, command=' '.join(cmd),
                              output=output[:3000], packets_count=packets)
    except Exception as e:
        return WiresharkResult(success=False, command=' '.join(cmd), error=str(e))

def get_statistics(pcap_file: str) -> WiresharkResult:
    if not os.path.exists(pcap_file):
        return WiresharkResult(success=False, error=f"File not found: {pcap_file}")
    
    cmd = [get_tshark_path(), '-r', pcap_file, '-q', '-z', 'io,stat,1']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        return WiresharkResult(success=True, command=' '.join(cmd), output=output[:3000])
    except Exception as e:
        return WiresharkResult(success=False, command=' '.join(cmd), error=str(e))

def filter_packets(pcap_file: str, filter_expr: str, count: int = 50) -> WiresharkResult:
    if not os.path.exists(pcap_file):
        return WiresharkResult(success=False, error=f"File not found: {pcap_file}")
    
    cmd = [get_tshark_path(), '-r', pcap_file, '-Y', filter_expr, '-c', str(count)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        packets = len([l for l in output.split('\n') if l.strip()])
        return WiresharkResult(success=True, command=' '.join(cmd),
                              output=output[:3000], packets_count=packets)
    except Exception as e:
        return WiresharkResult(success=False, command=' '.join(cmd), error=str(e))

def get_help() -> str:
    try:
        result = subprocess.run([get_tshark_path(), '--help'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    
    if 'version' in query_lower:
        return {'action': 'version', 'success': True, 'output': get_version()}
    
    if 'interface' in query_lower or 'interfaces' in query_lower:
        ifaces = list_interfaces()
        return {'action': 'interfaces', 'success': True, 'interfaces': ifaces}
    
    if 'capture' in query_lower or 'sniff' in query_lower or 'flairer' in query_lower:
        interface = "any"
        count = 100
        
        iface_match = re.search(r'(?:interface|iface|sur)\s*:?\s*(\w+)', query)
        if iface_match:
            interface = iface_match.group(1)
        
        count_match = re.search(r'(\d+)\s+(?:paquet|packets?)', query)
        if count_match:
            count = int(count_match.group(1))
        
        result = capture_packets(interface, count, timeout=60)
        return {'action': 'capture', 'success': result.success,
               'interface': interface, 'packets': result.packets_count,
               'output': result.output[:500]}
    
    if 'analyze' in query_lower or 'analyse' in query_lower or 'read' in query_lower:
        pcap_match = re.search(r'(?:pcap|fichier|capture|file)\s*:?\s*(\S+)', query)
        if pcap_match:
            pcap_file = pcap_match.group(1)
            if os.path.exists(pcap_file):
                result = analyze_pcap(pcap_file)
                return {'action': 'analyze', 'success': result.success,
                       'file': pcap_file, 'packets': result.packets_count,
                       'output': result.output[:500]}
            else:
                return {'action': 'analyze', 'success': False,
                       'error': f'File not found: {pcap_file}'}
        return {'action': 'analyze', 'success': False,
               'error': 'No pcap file specified', 'example': 'analyse capture.pcap'}
    
    if 'http' in query_lower or 'requêtes http' in query_lower or 'http requests' in query_lower:
        pcap_match = re.search(r'(?:pcap|fichier|capture|file)\s*:?\s*(\S+)', query)
        if pcap_match:
            pcap_file = pcap_match.group(1)
            if os.path.exists(pcap_file):
                result = extract_http_requests(pcap_file)
                return {'action': 'http_requests', 'success': result.success,
                       'file': pcap_file, 'requests': result.packets_count,
                       'output': result.output[:500]}
            else:
                return {'action': 'http_requests', 'success': False,
                       'error': f'File not found: {pcap_file}'}
        return {'action': 'http_requests', 'success': False,
               'error': 'No pcap file specified'}
    
    if 'dns' in query_lower or 'dns queries' in query_lower or 'requêtes dns' in query_lower:
        pcap_match = re.search(r'(?:pcap|fichier|capture|file)\s*:?\s*(\S+)', query)
        if pcap_match:
            pcap_file = pcap_match.group(1)
            if os.path.exists(pcap_file):
                result = extract_dns_queries(pcap_file)
                return {'action': 'dns_queries', 'success': result.success,
                       'file': pcap_file, 'queries': result.packets_count,
                       'output': result.output[:500]}
            else:
                return {'action': 'dns_queries', 'success': False,
                       'error': f'File not found: {pcap_file}'}
        return {'action': 'dns_queries', 'success': False,
               'error': 'No pcap file specified'}
    
    if 'conversation' in query_lower or 'conversations' in query_lower or 'tcp sessions' in query_lower:
        protocol = 'tcp'
        if 'udp' in query_lower:
            protocol = 'udp'
        
        pcap_match = re.search(r'(?:pcap|fichier|capture|file)\s*:?\s*(\S+)', query)
        if pcap_match:
            pcap_file = pcap_match.group(1)
            if os.path.exists(pcap_file):
                result = extract_conversations(pcap_file, protocol)
                return {'action': 'conversations', 'success': result.success,
                       'file': pcap_file, 'protocol': protocol,
                       'output': result.output[:500]}
            else:
                return {'action': 'conversations', 'success': False,
                       'error': f'File not found: {pcap_file}'}
        return {'action': 'conversations', 'success': False,
               'error': 'No pcap file specified'}
    
    if 'statistics' in query_lower or 'stats' in query_lower or 'statistiques' in query_lower:
        pcap_match = re.search(r'(?:pcap|fichier|capture|file)\s*:?\s*(\S+)', query)
        if pcap_match:
            pcap_file = pcap_match.group(1)
            if os.path.exists(pcap_file):
                result = get_statistics(pcap_file)
                return {'action': 'statistics', 'success': result.success,
                       'file': pcap_file, 'output': result.output[:500]}
            else:
                return {'action': 'statistics', 'success': False,
                       'error': f'File not found: {pcap_file}'}
        return {'action': 'statistics', 'success': False,
               'error': 'No pcap file specified'}
    
    if 'filter' in query_lower or 'filtre' in query_lower or 'tcp' in query_lower or 'ip.addr' in query_lower:
        filter_expr = None
        
        tcp_match = re.search(r'tcp', query_lower)
        udp_match = re.search(r'udp', query_lower)
        port_match = re.search(r'port\s*(\d+)', query_lower)
        host_match = re.search(r'ip\.addr\s+([a-zA-Z0-9.-]+)', query_lower)
        
        filters = []
        if tcp_match:
            filters.append('tcp')
        if udp_match:
            filters.append('udp')
        if port_match:
            filters.append(f'port {port_match.group(1)}')
        if host_match:
            filters.append(f'ip.addr == {host_match.group(1)}')
        
        if filters:
            filter_expr = ' && '.join(filters)
        else:
            filter_expr = 'tcp'
        
        pcap_match = re.search(r'(?:pcap|fichier|capture|file)\s*:?\s*(\S+)', query)
        if pcap_match:
            pcap_file = pcap_match.group(1)
            if os.path.exists(pcap_file):
                result = filter_packets(pcap_file, filter_expr)
                return {'action': 'filter', 'success': result.success,
                       'file': pcap_file, 'filter': filter_expr,
                       'packets': result.packets_count, 'output': result.output[:500]}
        
        return {'action': 'filter', 'success': False,
               'error': 'No pcap file specified for filtering'}
    
    if 'help' in query_lower or 'aide' in query_lower:
        return {'action': 'help', 'success': True, 'output': get_help()}
    
    if 'info' in query_lower or 'informations' in query_lower:
        return {'action': 'info', 'success': True, 'version': get_version(),
               'interfaces': list_interfaces(),
               'note': 'Wireshark requires root for live capture, tshark for CLI'}
    
    return {'success': False, 'error': 'Command not recognized',
           'example': 'analyse capture.pcap ou http requests de capture.pcap ou statistics capture.pcap'}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'wireshark',
        'description': 'GUI packet analyzer (tshark CLI)',
        'category': 'network',
        'supported_queries': [
            'quelle est la version de wireshark',
            'liste les interfaces réseau',
            'capture 50 packets sur eth0',
            'analyse capture.pcap',
            'http requests de capture.pcap',
            'dns queries de capture.pcap',
            'conversations tcp de capture.pcap',
            'statistics de capture.pcap',
            'filtre tcp port 80 dans capture.pcap',
            'aide wireshark',
            'informations sur wireshark'
        ],
        'warning': 'Packet capture requires root privileges.',
        'features': ['pcap analysis', 'http extraction', 'dns queries', 'conversations', 'statistics']
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("wireshark Wrapper - Available:", is_available())
        print("Version:", get_version())
        print("Interfaces:", list_interfaces())
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'version':
        print(f"Version: {get_version()}")
    elif cmd == 'interfaces':
        print(f"Interfaces: {list_interfaces()}")
    elif cmd == 'help':
        print(get_help())
