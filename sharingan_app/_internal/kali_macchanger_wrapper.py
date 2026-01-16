"""
macchanger Wrapper for Sharingan OS
Real MAC address changer integration
"""

import subprocess
import re
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("sharingan.macchanger")

class MacChangeResult:
    def __init__(self, success: bool, device: str, original_mac: Optional[str] = None, 
                 new_mac: Optional[str] = None, output: str = "", error: Optional[str] = None):
        self.success = success
        self.device = device
        self.original_mac = original_mac
        self.new_mac = new_mac
        self.output = output
        self.error = error

def is_available() -> bool:
    try:
        result = subprocess.run(['which', 'macchanger'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_current_mac(device: str = "eth0") -> Optional[str]:
    try:
        result = subprocess.run(['cat', f'/sys/class/net/{device}/address'],
            capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None

def show_mac(device: str = "eth0") -> MacChangeResult:
    cmd = ['macchanger', '-s', device]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return MacChangeResult(success=True, device=device, output=result.stdout.strip())
        else:
            return MacChangeResult(success=False, device=device, output=result.stderr, error="Failed")
    except Exception as e:
        return MacChangeResult(success=False, device=device, output=str(e), error=str(e))

def random_mac(device: str = "eth0") -> MacChangeResult:
    cmd = ['macchanger', '-r', device]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout
        new_mac = None
        match = re.search(r'([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})', output)
        if match:
            new_mac = match.group(1)
        return MacChangeResult(success=result.returncode==0, device=device,
            original_mac=get_current_mac(device), new_mac=new_mac, output=output,
            error=result.stderr if result.returncode!=0 else None)
    except Exception as e:
        return MacChangeResult(success=False, device=device, output=str(e), error=str(e))

def vendor_mac(device: str = "eth0", same_kind: bool = True) -> MacChangeResult:
    cmd = ['macchanger', '-a' if same_kind else '-A', device]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout
        new_mac = None
        match = re.search(r'([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})', output)
        if match:
            new_mac = match.group(1)
        return MacChangeResult(success=result.returncode==0, device=device,
            original_mac=get_current_mac(device), new_mac=new_mac, output=output,
            error=result.stderr if result.returncode!=0 else None)
    except Exception as e:
        return MacChangeResult(success=False, device=device, output=str(e), error=str(e))

def permanent_mac(device: str = "eth0") -> MacChangeResult:
    cmd = ['macchanger', '-p', device]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return MacChangeResult(success=result.returncode==0, device=device,
            output=result.stdout, error=result.stderr if result.returncode!=0 else None)
    except Exception as e:
        return MacChangeResult(success=False, device=device, output=str(e), error=str(e))

def list_vendors() -> str:
    try:
        result = subprocess.run(['macchanger', '-l'], capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def handle_nlp_query(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    device = "eth0"
    device_match = re.search(r'(eth\d+|wlan\d+|ens\d+|enp\d+)', query)
    if device_match:
        device = device_match.group(1)
    
    if 'list' in query_lower or 'liste' in query_lower or 'vendors' in query_lower:
        return {'action': 'list_vendors', 'success': True, 'output': list_vendors()}
    
    if 'show' in query_lower or 'affiche' in query_lower or ('quel' in query_lower and 'mac' in query_lower):
        result = show_mac(device)
        return {'action': 'show', 'device': device, 'success': result.success, 'output': result.output}
    
    if 'random' in query_lower or 'aléatoire' in query_lower or 'hasard' in query_lower:
        result = random_mac(device)
        return {'action': 'random', 'device': device, 'success': result.success,
            'original_mac': result.original_mac, 'new_mac': result.new_mac, 'output': result.output}
    
    if 'vendor' in query_lower or 'fabricant' in query_lower:
        same_kind = 'same' in query_lower or 'même' in query_lower
        result = vendor_mac(device, same_kind)
        return {'action': 'vendor', 'device': device, 'success': result.success,
            'original_mac': result.original_mac, 'new_mac': result.new_mac, 'output': result.output}
    
    result = show_mac(device)
    return {'action': 'show', 'device': device, 'success': result.success, 'output': result.output}

def get_status() -> Dict[str, Any]:
    return {
        'available': is_available(),
        'name': 'macchanger',
        'description': 'MAC address changer',
        'category': 'network',
        'supported_queries': [
            'quelle est mon adresse MAC',
            'affiche le MAC de eth0',
            'change MAC aléatoire eth0',
            'MAC aléatoire wlan0',
            'MAC vendor eth0',
            'liste les vendors réseau'
        ],
        'devices': ['eth0', 'wlan0', 'ens3', 'enp0s3', 'enp3s0', 'wlp2s0']
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("macchanger Wrapper - Available:", is_available())
        sys.exit(0)
    
    cmd = sys.argv[1]
    device = sys.argv[2] if len(sys.argv) > 2 else 'enp3s0'
    
    if cmd == 'show':
        result = show_mac(device)
        print(f"Success: {result.success}\nOutput:\n{result.output}")
    elif cmd == 'random':
        result = random_mac(device)
        print(f"Success: {result.success}\nOriginal: {result.original_mac}\nNew: {result.new_mac}")
    elif cmd == 'list':
        print(list_vendors())
