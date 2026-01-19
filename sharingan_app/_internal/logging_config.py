#!/usr/bin/env python3
"""
Sharingan OS - Configuration de Logging Centralisée
Configure tous les loggers pour éviter les sorties verbeuses
"""

import logging
import sys
from pathlib import Path
from typing import Optional

class SharinganLogger:
    """Configuration de logging optimisée pour Sharingan OS"""

    def __init__(self, level: int = logging.WARNING, log_file: Optional[str] = None):
        self.level = level
        self.log_file = log_file
        self._configured = False

    def configure(self):
        """Configure tous les loggers du système"""
        if self._configured:
            return

        # Supprimer tous les handlers existants
        for logger_name in list(logging.root.manager.loggerDict.keys()) + ['']:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

        # Configuration de base silencieuse
        handlers = []

        # Ajouter un handler de fichier si demandé
        if self.log_file:
            try:
                log_path = Path(self.log_file)
                log_path.parent.mkdir(exist_ok=True, parents=True)
                file_handler = logging.FileHandler(log_path)
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                ))
                handlers.append(file_handler)
            except Exception:
                pass  # Silencieux en cas d'erreur

        # Si pas de handlers, ajouter NullHandler
        if not handlers:
            handlers = [logging.NullHandler()]

        # Configurer le logger root
        logging.basicConfig(
            level=self.level,
            handlers=handlers,
            force=True
        )

        # Désactiver les logs verbeux des dépendances communes
        verbose_loggers = [
            'requests', 'urllib3', 'PIL', 'PIL.PngImagePlugin', 'PIL.JpegImagePlugin',
            'asyncio', 'websockets', 'aiohttp', 'selenium', 'webdriver',
            'matplotlib', 'numpy', 'pandas', 'sklearn', 'torch',
            'transformers', 'diffusers', 'accelerate'
        ]

        for logger_name in verbose_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)

        # Logger spécifique pour Sharingan
        sharingan_logger = logging.getLogger('sharingan')
        sharingan_logger.setLevel(logging.INFO)

        self._configured = True

    def get_logger(self, name: str) -> logging.Logger:
        """Récupère un logger configuré"""
        return logging.getLogger(f'sharingan.{name}')

# Instance globale
logger_config = SharinganLogger()

def setup_logging(level: int = logging.WARNING, log_file: Optional[str] = None):
    """Fonction de convenance pour configurer le logging"""
    global logger_config
    logger_config = SharinganLogger(level, log_file)
    logger_config.configure()

def get_logger(name: str) -> logging.Logger:
    """Fonction de convenance pour obtenir un logger"""
    logger_config.configure()  # S'assurer que c'est configuré
    return logger_config.get_logger(name)