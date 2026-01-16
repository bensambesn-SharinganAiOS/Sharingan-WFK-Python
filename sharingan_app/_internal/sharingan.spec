# -*- mode: python ; coding: utf-8 -*-
"""
Sharingan OS - PyInstaller Spec
Configuration pour répertoire portable autonome
"""

import sys
from pathlib import Path
import os

# Chemins
base_dir = Path(r"/root/Projets/Sharingan-WFK-Python/sharingan_app/_internal")
sharingan_dir = Path(r"/root/Projets/Sharingan-WFK-Python/sharingan_app/_internal/sharingan_app/_internal")
main_script = Path(r"/root/Projets/Sharingan-WFK-Python/sharingan_app/_internal/sharingan_app/_internal/main.py")

# Ajouter les chemins de Sharingan
sys.path.insert(0, str(sharingan_dir))
sys.path.insert(0, str(base_dir))

# Analyse du script principal
a = Analysis(
    [str(main_script)],
    pathex=[str(sharingan_dir), str(base_dir)],
    binaries=[],
    datas=[
        # Inclure tous les fichiers Python de Sharingan
        (str(sharingan_dir / "*.py"), "sharingan"),
        (str(sharingan_dir / "providers" / "*.py"), "sharingan/providers"),
        (str(sharingan_dir / "config"), "sharingan/config"),
        (str(sharingan_dir / "docs"), "sharingan/docs"),
        (str(sharingan_dir / "src" / "**" / "*.py"), "sharingan/src"),
    ],
    hiddenimports=[
        # Core modules
        "sharingan_os",
        "fake_detector", 
        "check_obligations",
        "system_consciousness",
        "genome_memory",
        "tool_schemas",
        "ai_providers",
        "neutral_ai",
        "instinct_layer",
        "clarification_layer",
        "evolution_team",
        
        # Providers
        "providers.opencode_provider",
        "providers.tgpt_provider",
        "providers.minimax_provider",
        "providers.grok_provider",
        
        # AI/NLP modules
        "ai_memory_manager",
        "context_manager",
        "ai_providers",
        
        # External libraries
        "requests",
        "pyyaml",
        "rich",
        "loguru",
        "click",
        "typer",
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "jinja2",
        "aiohttp",
        "asyncio",
        "pathlib",
        "dataclasses",
        "typing",
        
        # System tools
        "subprocess",
        "json",
        "configparser",
        "argparse",
        "logging",
        "datetime",
        "pathlib",
        "os",
        "sys",
        "threading",
        "multiprocessing",
        "concurrent.futures",
        
        # Optional dependencies
        "nmap",
        "scapy",
        "cryptography",
        "hashlib",
        "secrets",
        "base64",
        "uuid",
        "socket",
        "ssl",
        "http.client",
        "urllib.request",
        "urllib.parse",
        "webbrowser",
        "email",
        "smtplib",
        "ftplib",
        
        # Database/Storage
        "sqlite3",
        "json",
        "pickle",
        "csv",
        "xml.etree.ElementTree",
        
        # Compression
        "zipfile",
        "tarfile",
        "gzip",
        "lzma",
        
        # Network
        "socket",
        "http.server",
        "socketserver",
        "asyncio",
        "aiohttp",
        "websockets",
        
        # Security/Crypto
        "cryptography",
        "hashlib",
        "hmac",
        "secrets",
        "ssl",
        
        # File operations
        "pathlib",
        "shutil",
        "tempfile",
        "glob",
        "fnmatch",
        
        # Process management
        "subprocess",
        "psutil",
        "multiprocessing",
        "threading",
        "concurrent.futures",
        
        # System info
        "platform",
        "sys",
        "os",
        "ctypes",
        "resource",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Créer le PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Créer l'executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="sharingan",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)

# Créer la collection (répertoire portable)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Sharingan-OS-Linux",
)
