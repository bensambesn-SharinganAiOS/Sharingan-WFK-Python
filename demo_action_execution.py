#!/usr/bin/env python3
"""
Sharingan Action Demo - Demonstrates real action execution capabilities
Shows that Sharingan can execute real commands via ActionExecutor
"""

import sys
sys.path.insert(0, '.')

from sharingan_app._internal.action_executor import ActionExecutor
from sharingan_app._internal.vpn_tor_integration import VPNManager
from sharingan_app._internal.fake_detector import detect_fakes

def demo_vpn_info():
    """Show VPN/Tor information"""
    print("\n" + "="*60)
    print("🌐 VPN/TOR INTEGRATION DEMO")
    print("="*60)
    
    vpn = VPNManager()
    print(f"\nOpenVPN available: {vpn.openvpn_available}")
    print(f"WireGuard available: {vpn.wireguard_available}")
    
    if vpn.openvpn_available:
        print("\nTo connect to a VPN:")
        print("  1. Add OpenVPN config: vpn.add_openvpn_connection('myvpn', '/path/to/config.ovpn')")
        print("  2. Connect: vpn.connect('myvpn')")
    
    return vpn


def demo_action_execution():
    """Demonstrate real action execution"""
    print("\n" + "="*60)
    print("🎯 ACTION EXECUTION DEMO")
    print("="*60)
    
    executor = ActionExecutor()
    
    print(f"\nAvailable Kali tools:")
    for name, info in executor.kali_tools.items():
        print(f"  • {name}: {info['description']}")
    
    return executor


def execute_demo_actions(executor):
    """Execute demo actions"""
    print("\n" + "="*60)
    print("⚡ EXECUTING REAL ACTIONS")
    print("="*60)
    
    actions = [
        ("whois example.com", "WHOIS lookup for example.com"),
        ("nmap -sV localhost", "Quick port scan of localhost"),
    ]
    
    for action_desc, description in actions:
        print(f"\n--- {description} ---")
        print(f"Command: {action_desc}")
        
        result = executor.execute_action(action_desc, "demo")
        
        print(f"Success: {result['success']}")
        output = result.get('output', '')[:500]
        print(f"Output:\n{output}")
        
        # Check for fake content
        fake_check = detect_fakes(output, 'shell_output')
        print(f"Fake check: is_fake={fake_check.is_fake}")


def demo_vulnerability_scan_simulation():
    """Show how vulnerability scanning would work"""
    print("\n" + "="*60)
    print("🔍 VULNERABILITY SCAN CONCEPT (seneweb.com)")
    print("="*60)
    
    print("""
To perform a vulnerability scan on seneweb.com, the following tools can be used:

1. RECONNAISSANCE:
   whois seneweb.com          → Domain registration info
   dig seneweb.com            → DNS information
   nmap -sN seneweb.com       → Port discovery

2. SERVICE ENUMERATION:
   nmap -sV -sC seneweb.com   → Service version detection
   gobuster dir -u http://seneweb.com/ -w /usr/share/wordlists/dirb/common.txt

3. VULNERABILITY SCANNING:
   nikto -h seneweb.com       → Web server vulnerabilities
   searchsploit seneweb.com   → Search for known exploits

4. WEB APPLICATION:
   sqlmap -u "http://seneweb.com/page?id=1" --batch

NOTE: Always ensure you have AUTHORIZATION before scanning external systems.
Unauthorized scanning is illegal and unethical.
""")


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║          SHARINGAN OS - ACTION EXECUTION DEMO                ║
║                                                              ║
║  This demo shows that Sharingan can execute REAL actions    ║
║  through the ActionExecutor module.                          ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Demo VPN
    vpn = demo_vpn_info()
    
    # Demo Action Executor
    executor = demo_action_execution()
    
    # Execute real actions
    execute_demo_actions(executor)
    
    # Show vulnerability scan concept
    demo_vulnerability_scan_simulation()
    
    print("\n" + "="*60)
    print("✅ CONCLUSION")
    print("="*60)
    print("""
Sharingan OS is capable of executing REAL actions:

✅ Network scanning (nmap, masscan)
✅ Reconnaissance (whois, dig)
✅ Exploit searching (searchsploit)
✅ Directory enumeration (gobuster)
✅ Web vulnerability scanning (nikto)
✅ VPN/Tor management

The system uses subprocess.run() with shell=True to execute
these commands in real-time.

To use these capabilities programmatically:
  executor = ActionExecutor()
  result = executor.execute_action("nmap -sV target.com", "my_motivation")
""")


if __name__ == "__main__":
    main()
