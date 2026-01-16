#!/usr/bin/env python3
"""
Sharingan OS - Kali ISO Tools Integration
Extract and install tools from Kali Linux ISO (if available)
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict

ISO_PATH = "/home/user/save/kali-linux-2025.3-live-amd64.iso"
MOUNT_POINT = "/mnt/iso"
INSTALL_DIR = Path(__file__).parent.parent / "tools" / "bin"

TOOLS_TO_EXTRACT = {
    "binwalk": "binwalk",
    "rkhunter": "rkhunter",
    "lynis": "lynis",
    "nmap": "nmap",
    "gobuster": "gobuster",
    "ffuf": "ffuf",
    "sqlmap": "sqlmap",
    "hashcat": "hashcat",
    "john": "john",
    "crunch": "crunch",
    "masscan": "masscan",
    "netdiscover": "netdiscover",
    "Responder": "responder",
    "theHarvester": "theHarvester",
    "sherlock": "sherlock",
    "volatility": "volatility3",
}

def is_iso_mounted() -> bool:
    """Check if ISO is already mounted"""
    return os.path.ismount(MOUNT_POINT)

def mount_iso() -> bool:
    """Mount Kali ISO"""
    if is_iso_mounted():
        return True
    
    os.makedirs(MOUNT_POINT, exist_ok=True)
    result = subprocess.run(
        ["mount", "-o", "loop", ISO_PATH, MOUNT_POINT],
        capture_output=True, text=True
    )
    return result.returncode == 0

def umount_iso() -> bool:
    """Unmount Kali ISO"""
    if is_iso_mounted():
        result = subprocess.run(["umount", MOUNT_POINT], capture_output=True, text=True)
        return result.returncode == 0
    return True

def extract_from_squashfs(tool_name: str) -> bool:
    """Extract tool from squashfs (if possible)"""
    squashfs_path = f"{MOUNT_POINT}/live/filesystem.squashfs"
    
    if not os.path.exists(squashfs_path):
        return False
    
    output_dir = INSTALL_DIR / tool_name
    os.makedirs(output_dir, exist_ok=True)
    
    result = subprocess.run(
        ["unsquashfs", "-d", str(output_dir), "-e", f"usr/bin/{tool_name}", squashfs_path],
        capture_output=True, text=True
    )
    
    return (output_dir / "usr" / "bin" / tool_name).exists()

def extract_deb_package(deb_path: str, output_dir: Path) -> bool:
    """Extract .deb package"""
    os.makedirs(output_dir, exist_ok=True)
    
    result = subprocess.run(
        ["dpkg-deb", "-x", deb_path, str(output_dir)],
        capture_output=True, text=True
    )
    
    return result.returncode == 0

def find_tool_in_pool(tool_name: str) -> Optional[str]:
    """Find tool package in ISO pool"""
    for root, dirs, files in os.walk(f"{MOUNT_POINT}/pool"):
        for f in files:
            if f"{tool_name.lower()}_" in f.lower() or f"-{tool_name.lower()}_" in f.lower():
                return os.path.join(root, f)
    return None

def install_from_system(tool_name: str) -> bool:
    """Install tool from system if available"""
    result = subprocess.run(
        ["apt-get", "install", "-y", tool_name],
        capture_output=True, text=True
    )
    return result.returncode == 0

def download_and_install(tool_name: str) -> bool:
    """Download and install tool from internet"""
    print(f"Downloading {tool_name}...")
    
    download_urls = {
        "binwalk": "https://github.com/ReFirmLabs/binwalk/archive/master.zip",
        "sherlock": "https://github.com/sherlock-project/sherlock/archive/master.zip",
        "theHarvester": "https://github.com/laramies/theHarvester/archive/master.zip",
        "responder": "https://github.com/lgandx/Responder/archive/master.zip",
        "volatility": "https://github.com/volatilityfoundation/volatility3/archive/master.zip",
    }
    
    if tool_name not in download_urls:
        return False
    
    url = download_urls[tool_name]
    temp_dir = f"/tmp/{tool_name}_install"
    
    os.makedirs(temp_dir, exist_ok=True)
    
    result = subprocess.run(
        ["wget", "-q", url, "-O", f"{temp_dir}/{tool_name}.zip"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        return False
    
    subprocess.run(
        ["unzip", "-q", f"{temp_dir}/{tool_name}.zip", "-d", temp_dir],
        capture_output=True
    )
    
    target_dir = INSTALL_DIR / tool_name.lower()
    shutil.move(f"{temp_dir}/{tool_name}-master", target_dir)
    
    return target_dir.exists()

def integrate_tool(tool_name: str) -> Dict:
    """Integrate a single tool into the project"""
    result = {
        "tool": tool_name,
        "source": None,
        "installed": False,
        "path": None
    }
    
    tool_path = INSTALL_DIR / tool_name.lower()
    
    if tool_path.exists():
        result["installed"] = True
        result["path"] = str(tool_path)
        return result
    
    sources_tried = []
    
    if is_iso_mounted():
        sources_tried.append("iso_squashfs")
        if extract_from_squashfs(tool_name.lower()):
            result["source"] = "iso_squashfs"
            result["installed"] = True
            result["path"] = str(tool_path)
            return result
        
        sources_tried.append("iso_pool")
        deb_path = find_tool_in_pool(tool_name)
        if deb_path and extract_deb_package(deb_path, tool_path):
            result["source"] = "iso_pool"
            result["installed"] = True
            result["path"] = str(tool_path)
            return result
    
    sources_tried.append("system")
    if install_from_system(tool_name):
        result["source"] = "system"
        result["installed"] = True
        return result
    
    sources_tried.append("download")
    if download_and_install(tool_name):
        result["source"] = "download"
        result["installed"] = True
        result["path"] = str(tool_path)
        return result
    
    result["sources_tried"] = sources_tried
    return result

def integrate_all_tools() -> Dict:
    """Integrate all missing tools"""
    results = {
        "iso_mounted": is_iso_mounted(),
        "tools": {},
        "summary": {
            "total": len(TOOLS_TO_EXTRACT),
            "installed": 0,
            "failed": 0
        }
    }
    
    if not results["iso_mounted"]:
        if not mount_iso():
            print("[WARN] Could not mount Kali ISO")
    
    for tool_name in TOOLS_TO_EXTRACT:
        tool_result = integrate_tool(tool_name)
        results["tools"][tool_name] = tool_result
        
        if tool_result["installed"]:
            results["summary"]["installed"] += 1
            print(f"[OK] {tool_name}: installed from {tool_result.get('source', 'unknown')}")
        else:
            results["summary"]["failed"] += 1
            print(f"[FAIL] {tool_name}: failed (tried: {tool_result.get('sources_tried', [])})")
    
    umount_iso()
    
    return results

def create_tool_wrapper(tool_name: str, tool_path: str) -> str:
    """Create a Python wrapper for a tool"""
    wrapper = f'''#!/usr/bin/env python3
"""
{tool_name} wrapper for Sharingan OS
"""

import subprocess
import sys
from pathlib import Path

TOOL_PATH = Path(__file__).parent / "{tool_name.lower()}"

def main():
    cmd = [str(TOOL_PATH)] + sys.argv[1:]
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    exit(main())
'''
    wrapper_path = INSTALL_DIR / f"{tool_name.lower()}_wrapper.py"
    with open(wrapper_path, 'w') as f:
        f.write(wrapper)
    return str(wrapper_path)

if __name__ == "__main__":
    print("=" * 60)
    print("  Sharingan OS - Kali Tools Integration")
    print("=" * 60)
    
    if not os.path.exists(ISO_PATH):
        print(f"[WARN] ISO not found at {ISO_PATH}")
        print("Will try to install tools from system or download...")
    
    results = integrate_all_tools()
    
    print(f"\n{'=' * 60}")
    print(f"  Summary: {results['summary']['installed']}/{results['summary']['total']} tools installed")
    print(f"{'=' * 60}")
