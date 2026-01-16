#!/usr/bin/env python3
"""
Sharingan OS - Autonomy Setup Script
Cree un environnement Python totalement autonome et independant.
Auteur: Ben Sambe
"""

import os
import sys
import venv
import subprocess
import shutil
from pathlib import Path
import json

class AutonomySetup:
    """Setup pour l'autonomie 100% de Sharingan OS"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.sharingan_dir = self.base_dir / "sharingan_app" / "_internal"
        self.autonomy_dir = self.base_dir / "sharingan_autonomous"
        self.python_dir = self.autonomy_dir / "python"
        self.libs_dir = self.autonomy_dir / "libs"
        self.config_dir = self.autonomy_dir / "config"
        
        self.required_libs = [
            "requests>=2.31.0",
            "pyyaml>=6.0",
            "rich>=13.0",
            "loguru>=0.7.0",
            "click>=8.0",
            "typer>=0.9.0",
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
            "pydantic>=2.5.0",
            "sqlalchemy>=2.0.0",
            "pandas>=2.0.0",
            "numpy>=1.24.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "jinja2>=3.1.0",
            "aiohttp>=3.9.0",
            "asyncio>=3.4.3",
            "pathlib>=1.0.1",
            "dataclasses>=0.6",
            "typing-extensions>=4.8.0",
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.7.0",
            "pre-commit>=3.5.0",
            "setuptools>=69.0.0",
            "wheel>=0.42.0",
            "pip>=23.3.0"
        ]
        
        self.system_tools = [
            "curl", "wget", "git", "nano", "vim", "grep", "awk", "sed",
            "find", "locate", "tar", "gzip", "zip", "unzip", "ssh",
            "scp", "rsync", "ping", "traceroute", "netstat", "lsof",
            "ps", "top", "htop", "df", "du", "free", "uname", "whoami"
        ]
    
    def create_autonomy_structure(self):
        """Cree la structure de l'environnement autonome"""
        print("Creation de la structure autonome...")
        
        dirs = [
            self.autonomy_dir,
            self.python_dir,
            self.libs_dir,
            self.config_dir,
            self.autonomy_dir / "bin",
            self.autonomy_dir / "scripts",
            self.autonomy_dir / "tools",
            self.autonomy_dir / "data",
            self.autonomy_dir / "logs",
            self.autonomy_dir / "temp"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  OK: {dir_path}")
    
    def setup_python_environment(self):
        """Configure un environnement Python isole"""
        print("Configuration de l'environnement Python...")
        
        venv.create(self.python_dir, with_pip=True, clear=True)
        
        python_exe = self.python_dir / "bin" / "python3"
        pip_exe = self.python_dir / "bin" / "pip3"
        
        subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
        
        print("  Installation des bibliotheques...")
        for lib in self.required_libs:
            try:
                subprocess.run([str(pip_exe), "install", lib], check=True, capture_output=True)
                print(f"    OK: {lib}")
            except subprocess.CalledProcessError as e:
                print(f"    FAIL: {lib}: {e}")
        
        return python_exe, pip_exe
    
    def bundle_system_tools(self):
        """Integre les outils systeme essentiels"""
        print("Integration des outils systeme...")
        
        tools_dir = self.autonomy_dir / "tools"
        
        for tool in self.system_tools:
            tool_path = tools_dir / tool
            tool_script = f"""#!/bin/bash
# Wrapper autonome pour {tool}
export PATH="{self.python_dir}/bin:$PATH"
export PYTHONPATH="{self.sharingan_dir}"
{tool} "$@"
"""
            tool_path.write_text(tool_script)
            tool_path.chmod(0o755)
            print(f"  OK: {tool}")
    
    def create_autonomous_launcher(self):
        """Cree le lanceur autonome principal"""
        print("Creation du lanceur autonome...")
        
        launcher_path = self.autonomy_dir / "sharingan"
        launcher_script = f"""#!/bin/bash
# Sharingan OS - Lanceur Autonome
export SHARINGAN_HOME="{self.autonomy_dir}"
export SHARINGAN_PYTHON="{self.python_dir}/bin/python3"
export SHARINGAN_LIBS="{self.libs_dir}"
export SHARINGAN_CONFIG="{self.config_dir}"
export PYTHONPATH="{self.sharingan_dir}:$PYTHONPATH"
export PATH="{self.autonomy_dir}/tools:{self.python_dir}/bin:$PATH"

# Lancer Sharingan OS avec son Python
cd "{self.sharingan_dir}"
exec "$SHARINGAN_PYTHON" main.py "$@"
"""
        launcher_path.write_text(launcher_script)
        launcher_path.chmod(0o755)
        print(f"  OK: {launcher_path}")
    
    def create_autonomy_config(self):
        """Cree la configuration pour l'autonomie"""
        print("Creation de la configuration...")
        
        config = {
            "autonomy": {
                "version": "1.0.0",
                "mode": "standalone",
                "python_path": str(self.python_dir / "bin" / "python3"),
                "libraries_path": str(self.libs_dir),
                "config_path": str(self.config_dir),
                "data_path": str(self.autonomy_dir / "data"),
                "logs_path": str(self.autonomy_dir / "logs"),
                "tools_path": str(self.autonomy_dir / "tools")
            },
            "sharingan": {
                "home": str(self.autonomy_dir),
                "internal_dir": str(self.sharingan_dir),
                "autonomous_mode": True,
                "offline_first": True,
                "local_ai": True,
                "bundled_tools": True
            },
            "dependencies": {
                "python_version": "3.10+",
                "required_libs": self.required_libs,
                "system_tools": self.system_tools
            }
        }
        
        config_file = self.config_dir / "autonomy.json"
        config_file.write_text(json.dumps(config, indent=2))
        print(f"  OK: {config_file}")
    
    def copy_sharingan_files(self):
        """Copie les fichiers Sharingan essentiels"""
        print("Copie des fichiers Sharingan...")
        
        essential_files = [
            "sharingan_os.py",
            "autonomy_tests.py",
            "check_obligations.py",
            "fake_detector.py",
            "system_consciousness.py",
            "genome_memory.py",
            "tool_schemas.py",
            "__init__.py"
        ]
        
        for file_name in essential_files:
            src = self.sharingan_dir / file_name
            dst = self.autonomy_dir / "src" / file_name
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"  OK: {file_name}")
        
        providers_src = self.sharingan_dir / "providers"
        providers_dst = self.autonomy_dir / "src" / "providers"
        if providers_src.exists():
            shutil.copytree(providers_src, providers_dst, dirs_exist_ok=True)
            print(f"  OK: providers/")
    
    def create_package_script(self):
        """Cree le script de packaging"""
        print("Creation du script de packaging...")
        
        package_script = self.autonomy_dir / "package.py"
        script_content = '''#!/usr/bin/env python3
"""
Script pour creer un package autonome de Sharingan OS
"""

import tarfile
import gzip
import shutil
from pathlib import Path

def create_package():
    """Cree un package compresse de l'environnement autonome"""
    import os
    base_dir = Path(__file__).parent.parent
    package_name = "sharingan-os-autonomous.tar.gz"
    
    print("Creation du package autonome...")
    
    with tarfile.open(package_name, "w:gz") as tar:
        tar.add(base_dir, arcname="sharingan-os-autonomous")
    
    print(f"Package cree: {package_name}")
    print(f"Taille: {Path(package_name).stat().st_size / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    create_package()
'''
        package_script.write_text(script_content)
        package_script.chmod(0o755)
        print(f"  OK: {package_script}")
    
    def setup_complete(self):
        """Finalise le setup"""
        print("\nSetup de l'autonomie termine!")
        print(f"Repertoire autonome: {self.autonomy_dir}")
        print(f"Python isole: {self.python_dir}")
        print(f"Bibliotheques: {self.libs_dir}")
        print(f"Configuration: {self.config_dir}")
        print(f"Lanceur: {self.autonomy_dir / 'sharingan'}")
        
        print("\nInstructions:")
        print(f"1. cd {self.autonomy_dir}")
        print("2. ./sharingan --help")
        print("3. ./sharingan --status")
        print("4. ./sharingan --start")
        
        try:
            link_path = Path("/usr/local/bin/sharingan")
            if not link_path.exists():
                link_path.symlink_to(self.autonomy_dir / "sharingan")
                print(f"Lien global cree: {link_path}")
        except PermissionError:
            print("Permissions requises pour creer le lien global")
    
    def run_setup(self):
        """Execute le setup complet"""
        print("Demarrage du setup d'autonomie Sharingan OS...")
        
        try:
            self.create_autonomy_structure()
            self.setup_python_environment()
            self.bundle_system_tools()
            self.create_autonomous_launcher()
            self.create_autonomy_config()
            self.copy_sharingan_files()
            self.create_package_script()
            self.setup_complete()
            
            return True
            
        except Exception as e:
            print(f"Erreur lors du setup: {e}")
            return False


def main():
    """Point d'entree principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sharingan OS - Autonomy Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--force', action='store_true', help='Force la recreation')
    parser.add_argument('--package-only', action='store_true', help='Cree seulement le package')
    
    args = parser.parse_args()
    
    setup = AutonomySetup()
    
    if args.package_only:
        setup.create_package_script()
        print("Script de packaging cree")
    else:
        success = setup.run_setup()
        if success:
            print("\nSetup d'autonomie reussi!")
        else:
            print("\nSetup d'autonomie echoue!")
            sys.exit(1)


if __name__ == "__main__":
    main()
