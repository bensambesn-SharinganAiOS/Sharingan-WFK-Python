#!/usr/bin/env python3
"""
Sharingan OS - Configuration centralisée
Gère les chemins, logs, et configurations système
"""

import os
import tempfile
import platform
from pathlib import Path
from typing import Optional

class SharinganConfig:
    """Configuration centralisée pour Sharingan OS"""

    def __init__(self):
        self.system = platform.system().lower()
        self._temp_base = None
        self._cache_base = None
        self._logs_base = None

    @property
    def temp_dir(self) -> Path:
        """Répertoire temporaire sécurisé"""
        if self._temp_base is None:
            # Utiliser tempfile pour un répertoire temporaire sécurisé
            self._temp_base = Path(tempfile.gettempdir()) / "sharingan"
            self._temp_base.mkdir(exist_ok=True, mode=0o700)
        return self._temp_base

    @property
    def cache_dir(self) -> Path:
        """Répertoire de cache"""
        if self._cache_base is None:
            if self.system == "linux":
                self._cache_base = Path.home() / ".cache" / "sharingan"
            else:
                self._cache_base = self.temp_dir / "cache"
            self._cache_base.mkdir(exist_ok=True, parents=True, mode=0o700)
        return self._cache_base

    @property
    def logs_dir(self) -> Path:
        """Répertoire des logs"""
        if self._logs_base is None:
            if self.system == "linux":
                self._logs_base = Path("/var/log/sharingan")
                try:
                    self._logs_base.mkdir(exist_ok=True, parents=True, mode=0o755)
                except PermissionError:
                    # Fallback vers home si pas de permissions
                    self._logs_base = Path.home() / ".sharingan" / "logs"
                    self._logs_base.mkdir(exist_ok=True, parents=True, mode=0o700)
            else:
                self._logs_base = self.temp_dir / "logs"
                self._logs_base.mkdir(exist_ok=True, mode=0o700)
        return self._logs_base

    def get_temp_file(self, prefix: str = "sharingan", suffix: str = "") -> Path:
        """Génère un fichier temporaire sécurisé"""
        return Path(tempfile.NamedTemporaryFile(
            prefix=prefix,
            suffix=suffix,
            dir=self.temp_dir,
            delete=False
        ).name)

    def get_cache_file(self, filename: str) -> Path:
        """Génère un chemin de fichier cache"""
        return self.cache_dir / filename

    def get_log_file(self, filename: str) -> Path:
        """Génère un chemin de fichier log"""
        return self.logs_dir / filename

    def cleanup_temp_files(self, pattern: str = "*") -> int:
        """Nettoie les fichiers temporaires (usage avec précaution)"""
        count = 0
        for file in self.temp_dir.glob(pattern):
            if file.is_file():
                try:
                    file.unlink()
                    count += 1
                except Exception:
                    pass
        return count

# Instance globale
config = SharinganConfig()

# Chemins spécifiques pour compatibilité
def get_screenshot_path(filename: str = "screenshot.png") -> str:
    """Chemin pour les captures d'écran"""
    return str(config.get_temp_file("screenshot", ".png"))

def get_browser_cmd_path() -> str:
    """Chemin pour les commandes browser"""
    return str(config.get_temp_file("browser_cmd", ".txt"))

def get_browser_result_path() -> str:
    """Chemin pour les résultats browser"""
    return str(config.get_temp_file("browser_result", ".txt"))

def get_api_results_path() -> str:
    """Chemin pour les résultats d'API"""
    return str(config.get_temp_file("api_results", ".json"))

def get_multimedia_cache_path() -> str:
    """Chemin pour le cache multimedia"""
    return str(config.cache_dir / "multimedia")

def get_harvester_output_path() -> str:
    """Chemin pour les résultats theHarvester"""
    return str(config.get_temp_file("harvester", ".json"))