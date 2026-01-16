#!/usr/bin/env python3
"""
Sharingan OS - PyInstaller Configuration
Configuration pour créer un répertoire portable autonome (pas un seul executable).
Support: Linux, Windows, Mac
Auteur: Ben Sambe
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform

class SharinganPyInstaller:
    """Configuration PyInstaller pour répertoire portable"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.sharingan_dir = self.base_dir / "sharingan_app" / "_internal"
        self.build_dir = self.base_dir / "build"
        self.dist_dir = self.base_dir / "dist"
        self.output_dir = self.base_dir / "Sharingan-OS-Portable"
        
        # Plateforme actuelle
        self.platform = platform.system().lower()
        
        # Nom de l'executable principal
        self.main_script = self.sharingan_dir / "main.py"
        self.exe_name = "sharingan"
        if self.platform == "windows":
            self.exe_name += ".exe"
    
    def create_spec_file(self):
        """Crée le fichier .spec pour PyInstaller"""
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
"""
Sharingan OS - PyInstaller Spec
Configuration pour répertoire portable autonome
"""

import sys
from pathlib import Path
import os

# Chemins
base_dir = Path(r"{self.base_dir}")
sharingan_dir = Path(r"{self.sharingan_dir}")
main_script = Path(r"{self.main_script}")

# Ajouter les chemins de Sharingan
sys.path.insert(0, str(sharingan_dir))
sys.path.insert(0, str(base_dir))

# Vérifier que le script principal existe
if not main_script.exists():
    # Chercher alternatives
    alternatives = [
        self.sharingan_dir / "_internal" / "main.py",
        self.sharingan_dir / "main.py",
        self.base_dir / "main.py"
    ]
    
    for alt in alternatives:
        if alt.exists():
            main_script = alt
            break
    else:
        raise FileNotFoundError(f"Script principal non trouvé: {main_script}")

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
    hooksconfig={{}},
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
    name="{self.exe_name}",
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
    name="Sharingan-OS-{self.platform.title()}",
)
'''
        
        spec_file = self.base_dir / "sharingan.spec"
        spec_file.write_text(spec_content)
        print(f"✅ Fichier .spec créé: {spec_file}")
        return spec_file
    
    def install_pyinstaller(self):
        """Installe PyInstaller si nécessaire"""
        try:
            import PyInstaller
            print("✅ PyInstaller déjà installé")
        except ImportError:
            print("📦 Installation de PyInstaller...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller installé")
    
    def build_portable(self):
        """Construit le répertoire portable"""
        print("🔨 Construction du répertoire portable...")
        
        # Nettoyer les builds précédents
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        
        # Créer le fichier .spec
        spec_file = self.create_spec_file()
        
        # Exécuter PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            str(spec_file),
            "--clean",
            "--noconfirm",
            "--distpath", str(self.dist_dir),
            "--workpath", str(self.build_dir)
        ]
        
        print(f"🚀 Exécution: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build réussi!")
            
            # Renommer/réorganiser le répertoire de sortie
            portable_dir = self.dist_dir / f"Sharingan-OS-{self.platform.title()}"
            if portable_dir.exists():
                if self.output_dir.exists():
                    shutil.rmtree(self.output_dir)
                shutil.move(str(portable_dir), str(self.output_dir))
                
                print(f"📁 Répertoire portable créé: {self.output_dir}")
                
                # Créer le lanceur
                self.create_launcher()
                
                # Créer la documentation
                self.create_readme()
                
                return True
        else:
            print(f"❌ Erreur de build: {result.stderr}")
            return False
    
    def create_launcher(self):
        """Crée le lanceur principal"""
        if self.platform == "windows":
            launcher_path = self.output_dir / "sharingan.bat"
            launcher_content = f"""@echo off
title Sharingan OS
echo ====================================
echo      Sharingan OS - Portable Mode  
echo ====================================
echo.

REM Set environment
set SHARINGAN_HOME=%~dp0
set PATH=%SHARINGAN_HOME%;%PATH%

REM Run Sharingan OS
{self.exe_name} %*

pause
"""
        else:
            launcher_path = self.output_dir / "sharingan"
            launcher_content = f"""#!/bin/bash
# Sharingan OS - Portable Launcher

echo "===================================="
echo "   Sharingan OS - Portable Mode"
echo "===================================="
echo

# Set environment
export SHARINGAN_HOME="$(dirname "$0")"
export PATH="$SHARINGAN_HOME:$PATH"

# Run Sharingan OS
exec "./{self.exe_name}" "$@"
"""
            launcher_path.chmod(0o755)
        
        launcher_path.write_text(launcher_content)
        print(f"✅ Lanceur créé: {launcher_path}")
    
    def create_readme(self):
        """Crée le README pour le répertoire portable"""
        readme_content = f"""# Sharingan OS - Portable Version

## Plateforme: {self.platform.title()}

## Démarrage

### Linux/Mac:
```bash
./sharingan
```

### Windows:
```cmd
sharingan.bat
```

## Commandes disponibles

```bash
./sharingan --help              # Aide
./sharingan --status            # Statut du système
./sharingan --start             # Démarrer Sharingan OS
./sharingan --stop              # Arrêter Sharingan OS
./sharingan --test              # Tests d'autonomie
./sharingan --check             # Vérification des obligations
./sharingan --ai "message"      # Chat IA
./sharingan --scan target       # Scan sécurité
./sharingan --tool tool_name    # Outil spécifique
```

## Structure du répertoire

```
Sharingan-OS-{self.platform.title()}/
├── {self.exe_name}              # Executable principal
├── sharingan                   # Lanceur (Linux/Mac)
├── sharingan.bat              # Lanceur (Windows)
├── _internal/                 # Modules Python de Sharingan
│   ├── sharingan_os.py
│   ├── fake_detector.py
│   ├── providers/
│   └── ...
├── lib/                       # Bibliothèques Python
├── data/                      # Données utilisateur
├── logs/                      # Logs
├── config/                    # Configuration
└── tools/                     # Outils système
```

## Configuration

Les fichiers de configuration sont dans:
- `config/`: Configuration principale
- `data/`: Données et mémoire
- `logs/`: Logs du système

## Autonomie

Ce répertoire portable est **100% autonome**:
- ✅ Python inclus
- ✅ Bibliothèques incluses
- ✅ Outils système intégrés
- ✅ Configuration locale
- ✅ Pas d'installation requise

## Multi-plateforme

Des versions sont disponibles pour:
- 🐧 Linux
- 🪟 Windows  
- 🍎 macOS

## Support

Pour plus d'informations:
- Documentation: `docs/`
- Tests: `./sharingan --test`
- Aide: `./sharingan --help`

---
**Sharingan OS v1.0 - Portable**
*Auteur: Ben Sambe*
"""
        
        readme_path = self.output_dir / "README.md"
        readme_path.write_text(readme_content)
        print(f"✅ README créé: {readme_path}")
    
    def create_build_script(self):
        """Crée le script de build automatisé"""
        build_script = self.base_dir / "build_portable.py"
        script_content = f'''#!/usr/bin/env python3
"""
Build Script for Sharingan OS Portable
"""

import sys
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

from pyinstaller_config import SharinganPyInstaller

def main():
    builder = SharinganPyInstaller()
    
    print("🔥 Construction de Sharingan OS Portable...")
    print(f"📁 Plateforme: {{builder.platform.title()}}")
    print(f"🐍 Python: {{sys.version}}")
    
    # Installer PyInstaller
    builder.install_pyinstaller()
    
    # Construire le répertoire portable
    success = builder.build_portable()
    
    if success:
        print("\\n🎊 Build réussi!")
        print(f"📂 Répertoire portable: {{builder.output_dir}}")
        print(f"💾 Taille: {{sum(f.stat().st_size for f in builder.output_dir.rglob('*') if f.is_file()) / 1024 / 1024:.1f}} MB")
        print("\\n📋 Utilisation:")
        print(f"   cd {{builder.output_dir}}")
        print("   ./sharingan --help")
    else:
        print("\\n❌ Build échoué!")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        build_script.write_text(script_content)
        build_script.chmod(0o755)
        print(f"✅ Script de build créé: {build_script}")
    
    def run_build(self):
        """Exécute le build complet"""
        print("🚀 Lancement du build portable...")
        
        # Installer PyInstaller
        self.install_pyinstaller()
        
        # Construire
        success = self.build_portable()
        
        if success:
            print(f"\n🎊 Build terminé avec succès!")
            print(f"📂 Répertoire: {self.output_dir}")
            
            # Afficher la taille
            total_size = sum(f.stat().st_size for f in self.output_dir.rglob('*') if f.is_file())
            print(f"💾 Taille totale: {total_size / 1024 / 1024:.1f} MB")
            
            # Instructions
            print(f"\n📋 Instructions:")
            print(f"   cd {self.output_dir}")
            print(f"   ./sharingan --help")
            
        return success


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sharingan OS - PyInstaller Build (Portable Directory)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--build', action='store_true', help='Construire le répertoire portable')
    parser.add_argument('--clean', action='store_true', help='Nettoyer les builds précédents')
    parser.add_argument('--spec-only', action='store_true', help='Créer seulement le fichier .spec')
    parser.add_argument('--install-deps', action='store_true', help='Installer les dépendances')
    
    args = parser.parse_args()
    
    builder = SharinganPyInstaller()
    
    if args.spec_only:
        builder.create_spec_file()
        print("📄 Fichier .spec créé")
    
    elif args.install_deps:
        builder.install_pyinstaller()
        print("✅ Dépendances installées")
    
    elif args.clean:
        if builder.build_dir.exists():
            shutil.rmtree(builder.build_dir)
        if builder.dist_dir.exists():
            shutil.rmtree(builder.dist_dir)
        if builder.output_dir.exists():
            shutil.rmtree(builder.output_dir)
        print("🧹 Nettoyage terminé")
    
    elif args.build:
        success = builder.run_build()
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()