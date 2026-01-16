"""
ettercap Wrapper for Sharingan OS
Real MITM attack tool integration
"""

import subprocess
import re
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger("sharingan.ettercap")

class EttercapResult:
    def __init__(self, success: bool, command: str = "", output: str = "", 
                 error: Optional[str] = None):
        self.success = success
        self.command = command
        self.output = output
        self.error = error

def is_available() -> bool:
    """Check if ettercap is installed"""
    try:
        result = subprocess.run(['which', 'ettercap'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_version() -> str:
    """Get ettercap version"""
    try:
        result = subprocess.run(['ettercap', '--version'], capture_output=True, text=True, timeout=10)
        return result.stdout.strip().split('\n')[0]
    except Exception as e:
        return f"Error: {e}"

def list_interfaces() -> List[str]:
    """List available network interfaces"""
    interfaces = []
    
    # Try using ip command
    try:
        result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True, timeout=10)
        for line in result.stdout.split('\n'):
            if ':' in line and not 'lo:' in line:
                iface = line.split(':')[1].strip().split('@')[0]
                if iface:
                    interfaces.append(iface)
    except:
        pass
    
    # Fallback to ettercap interfaces
    if not interfaces:
        try:
            result = subprocess.run(['ettercap', '-T', '-i', 'lo'], capture_output=True, text=True, timeout=5)
        except:
            pass
    
    return interfaces

def check_iface_promisc(iface: str) -> bool:
    """Check if interface is in promiscuous mode"""
    try:
        with open(f'/sys/class/net/{iface}/flags', 'r') as f:
            flags = int(f.read().strip(), 16)
            return flags & 0x100 == 0x100
    except:
        return False

def read_pcap(file_path: str, count: int = 100) -> EttercapResult:
    """Read and analyze a pcap file"""
    if not os.path.exists(file_path):
        return EttercapResult(success=False, error=f"File not found: {file_path}")
    
    cmd = ['ettercap', '-r', file_path, '-T', '-q']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        output_lines = result.stdout.split('\n')[:count]
        
        return EttercapResult(
            success=True,
            command=' '.join(cmd),
            output='\n'.join(output_lines)
        )
    except Exception as e:
        return EttercapResult(success=False, command=' '.join(cmd), error=str(e))

def mitm_info() -> Dict[str, Any]:
    """Get information about MITM attacks (educational)"""
    return {
        'description': 'Man-In-The-Middle attack information',
        'methods': {
            'arp': 'ARP spoofing - Poison ARP cache to intercept traffic',
            'dhcp': 'DHCP spoofing - Inject fake DHCP responses',
            'port': 'Port stealing - Steal port using ARP frames',
            'icmp': 'ICMP redirect - Send ICMP redirect messages',
            'none': 'No MITM - Passive sniffing only'
        },
        'defenses': [
            'Static ARP entries for critical hosts',
            'ARP monitoring tools (arpwatch, arpon)',
            '802.1X port-based authentication',
            'Encrypted communications (HTTPS, SSH, VPN)',
            'Dynamic ARP Inspection (DAI) on switches',
            'Use of static routes'
        ],
        'warning': 'MITM attacks require authorization. Illegal without permission.'
    }

def packet_info(pcap_file: str) -> Dict[str, Any]:
    """Extract basic info from pcap file"""
    if not os.path.exists(pcap_file):
        return {'success': False, 'error': f"File not found: {pcap_file}"}
    
    info = {
        'file': pcap_file,
        'size_bytes': os.path.getsize(pcap_file),
        'interfaces': list_interfaces(),
        'promiscuous_ifaces': [],
        'mitm_info': mitm_info()
    }
    
    for iface in info['interfaces']:
        if check_iface_promisc(iface):
            info['promiscuous_ifaces'].append(iface)
    
    return info

def capture_info(timeout: int = 5) -> Dict[str, Any]:
    """Get information about capture capabilities"""
    return {
        'tool': 'ettercap',
        'version': get_version(),
        'available': is_available(),
        'capabilities': [
            'Passive sniffing',
            'MITM attacks (ARP, DHCP, ICMP, Port)',
            'SSL/TLS MiTM',
            'Packet filtering',
            'Pcap file analysis',
            'Plugin support'
        ],
        'interfaces': list_interfaces(),
        'gui_modes': ['text', 'curses', 'gtk', 'daemon'],
        'note': 'ettercap requires root privileges for most operations'
    }

def handle_nlp_query(query: str) -> Dict[str, Any]:
    """Handle natural language query for ettercap operations"""
    query_lower = query.lower()
    
    if 'version' in query_lower or 'version' in query_lower:
        return {
            'action': 'version',
            'success': True,
            'output': get_version()
        }
    
    if 'interface' in query_lower or 'interface' in query_lower or 'iface' in query_lower:
        interfaces = list_interfaces()
        return {
            'action': 'list_interfaces',
            'success': True,
            'interfaces': interfaces,
            'count': len(interfaces)
        }
    
    if 'mitm' in query_lower or 'man in the middle' in query_lower or 'arp' in query_lower:
        return {
            'action': 'mitm_info',
            'success': True,
            'info': mitm_info()
        }
    
    if 'capture' in query_lower or 'sniff' in query_lower or 'sniffer' in query_lower:
        info = capture_info()
        return {
            'action': 'capture_info',
            'success': info.get('available', False),
            'info': info
        }
    
    if 'pcap' in query_lower or 'fichier' in query_lower or 'file' in query_lower:
        file_match = re.search(r'([/\w]+\.(pcap|cap|pcng))', query)
        if file_match:
            file_path = file_match.group(1)
            result = read_pcap(file_path)
            return {
                'action': 'read_pcap',
                'success': result.success,
                'file': file_path,
                'output': result.output,
                'error': result.error
            }
        return {
            'action': 'read_pcap',
            'success': False,
            'error': 'No pcap file specified',
            'example': 'analyse le fichier capture.pcap'
        }
    
    if 'protège' in query_lower or 'protect' in query_lower or 'défense' in query_lower or 'defense' in query_lower:
        return {
            'action': 'mitm_defense',
            'success': True,
            'defenses': mitm_info()['defenses']
        }
    
    if 'info' in query_lower or 'information' in query_lower:
        info = capture_info()
        return {
            'action': 'info',
            'success': True,
            'info': info
        }
    
    return {
        'success': False,
        'error': 'Command not recognized',
        'example': 'quelle est la version de ettercap ou liste les interfaces réseau'
    }

def get_status() -> Dict[str, Any]:
    """Get ettercap wrapper status"""
    return {
        'available': is_available(),
        'name': 'ettercap',
        'description': 'MITM attack tool and sniffer',
        'category': 'sniffing',
        'supported_queries': [
            'quelle est la version de ettercap',
            'liste les interfaces réseau',
            'comment fonctionne MITM',
            'comment se protéger des attaques MITM',
            'analyse le fichier capture.pcap',
            'informations sur ettercap'
        ],
        'mitm_methods': ['arp', 'dhcp', 'port', 'icmp', 'none'],
        'warning': 'MITM attacks require explicit authorization. Illegal otherwise.'
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("ettercap Wrapper for Sharingan OS")
        print(f"Available: {is_available()}")
        print("\nCommands:")
        print("  version                    - Show ettercap version")
        print("  interfaces                 - List network interfaces")
        print("  mitm                       - Show MITM information")
        print("  pcap <file>                - Read pcap file")
        print("  info                       - Show capture info")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == 'version':
        print(f"Version: {get_version()}")
    
    elif cmd == 'interfaces' or cmd == 'iface':
        interfaces = list_interfaces()
        print(f"Interfaces ({len(interfaces)}):")
        for iface in interfaces:
            print(f"  - {iface}")
    
    elif cmd == 'mitm':
        info = mitm_info()
        print(f"MITM Methods:")
        for method, desc in info['methods'].items():
            print(f"  {method}: {desc}")
        print(f"\nDefenses:")
        for defense in info['defenses']:
            print(f"  - {defense}")
    
    elif cmd == 'pcap':
        if len(sys.argv) > 2:
            result = read_pcap(sys.argv[2])
            print(f"Success: {result.success}")
            print(f"Output:\n{result.output}")
        else:
            print("Usage: ettercap_wrapper.py pcap <file>")
    
    elif cmd == 'info':
        info = capture_info()
        print(f"Tool: {info['tool']}")
        print(f"Version: {info['version']}")
        print(f"Available: {info['available']}")
        print(f"Capabilities: {info['capabilities']}")
        print(f"Interfaces: {info['interfaces']}")
        
    else:
        print(f"Unknown command: {cmd}")
        print("Available commands: version, interfaces, mitm, pcap, info")
