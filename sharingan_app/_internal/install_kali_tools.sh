#!/bin/bash
# Sharingan OS - Kali Tools Auto-Installer
# Installation automatique de tous les outils Kali

echo "🔥 Sharingan OS - Kali Tools Installation"
echo "========================================"

# Liste des outils à installer
KALI_TOOLS=(
    # Network
    "nmap"
    "masscan"
    "netdiscover"
    "arp-scan"
    "hping3"

    # Web
    "nikto"
    "dirb"
    "dirsearch"
    "gobuster"
    "ffuf"
    "wpscan"
    "whatweb"

    # Password
    "hashcat"
    "john"
    "hydra"
    "medusa"
    "patator"
    "crunch"

    # Wireless
    "aircrack-ng"
    "reaver"
    "bully"

    # Exploitation
    "metasploit-framework"
    "sqlmap"
    "exploitdb"

    # Forensic
    "binwalk"
    "foremost"
    "volatility"
    "autopsy"
    "scalpel"

    # Enumeration
    "theharvester"
    "dnsrecon"
    "dnsenum"
    "fierce"
    "recon-ng"

    # Social
    "set"
    "king-phisher"

    # Reverse Engineering
    "radare2"
    "gdb"
    "binutils"
    "ltrace"
    "strace"
)

echo "📦 Updating package list..."
apt update

echo "🔧 Installing Kali tools..."
INSTALLED=0
FAILED=0

for tool in "${KALI_TOOLS[@]}"; do
    echo "Installing $tool..."
    if apt install -y "$tool" >/dev/null 2>&1; then
        echo "  ✅ $tool installed"
        ((INSTALLED++))
    else
        echo "  ❌ $tool failed"
        ((FAILED++))
    fi
done

echo ""
echo "📊 Installation Summary:"
echo "  ✅ Installed: $INSTALLED"
echo "  ❌ Failed: $FAILED"
echo ""
echo "🎊 Kali tools installation completed!"
