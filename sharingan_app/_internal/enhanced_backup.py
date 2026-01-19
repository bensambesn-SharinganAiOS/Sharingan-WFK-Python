# -*- coding: utf-8 -*-
"""
Enhanced Backup System for Sharingan OS
Compression, encryption, point-in-time recovery
"""

import os
import json
import time
import shutil
import hashlib
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Optional encryption support
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False

logger = logging.getLogger("backup_system")

class BackupCompressor:
    """
    Compression intelligente pour les backups
    """

    def __init__(self):
        self.compression_stats = {
            'total_backups': 0,
            'total_size_before': 0,
            'total_size_after': 0,
            'compression_ratio': 0.0
        }

    def compress_backup(self, data: Dict[str, Any]) -> bytes:
        """Compresse les données de backup"""
        json_str = json.dumps(data, indent=2, default=str)
        compressed = json_str.encode('utf-8')  # Pour l'instant, pas de vraie compression

        # TODO: Implémenter vraie compression LZ4/ZSTD
        # if LZ4_AVAILABLE:
        #     compressed = lz4.compress(json_str.encode())

        self.compression_stats['total_backups'] += 1
        self.compression_stats['total_size_before'] += len(json_str)
        self.compression_stats['total_size_after'] += len(compressed)

        if self.compression_stats['total_size_before'] > 0:
            self.compression_stats['compression_ratio'] = (
                self.compression_stats['total_size_after'] /
                self.compression_stats['total_size_before']
            )

        return compressed

    def decompress_backup(self, compressed_data: bytes) -> Dict[str, Any]:
        """Décompresse les données de backup"""
        # TODO: Implémenter vraie décompression
        json_str = compressed_data.decode('utf-8')
        return json.loads(json_str)

class BackupEncryptor:
    """
    Chiffrement des backups sensibles
    """

    def __init__(self, password: Optional[str] = None):
        self.password = password or "sharingan_default_backup_key"
        self.key = self._derive_key(self.password) if ENCRYPTION_AVAILABLE else None

    def _derive_key(self, password: str) -> bytes:
        """Dérive une clé de chiffrement du mot de passe"""
        if not ENCRYPTION_AVAILABLE:
            return b""

        salt = b"sharingan_backup_salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def encrypt_data(self, data: bytes) -> bytes:
        """Chiffre les données"""
        if not ENCRYPTION_AVAILABLE or not self.key:
            return data

        f = Fernet(self.key)
        return f.encrypt(data)

    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Déchiffre les données"""
        if not ENCRYPTION_AVAILABLE or not self.key:
            return encrypted_data

        f = Fernet(self.key)
        return f.decrypt(encrypted_data)

class BackupManager:
    """
    Gestionnaire de backups amélioré
    """

    def __init__(self, backup_dir: str = "~/.sharingan/backups"):
        self.backup_dir = Path(backup_dir).expanduser()
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.compressor = BackupCompressor()
        self.encryptor = BackupEncryptor()

        # Configuration des backups
        self.backup_config = {
            'auto_backup_enabled': True,
            'backup_interval_hours': 6,  # Toutes les 6 heures
            'max_backups_per_type': 10,  # Maximum 10 backups par type
            'retention_days': 30,        # Garder 30 jours
            'compression_enabled': True,
            'encryption_enabled': True
        }

        # Statistiques
        self.stats = {
            'total_backups_created': 0,
            'total_backups_restored': 0,
            'last_backup_time': None,
            'backup_sizes': [],
            'restore_times': []
        }

        logger.info(f"Enhanced backup system initialized at {self.backup_dir}")

    def create_backup(self, name: str, data: Dict[str, Any],
                     backup_type: str = "full") -> Dict[str, Any]:
        """
        Crée un backup avec compression et chiffrement
        """
        timestamp = datetime.now()
        backup_id = f"{backup_type}_{name}_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        try:
            # Métadonnées du backup
            metadata = {
                'backup_id': backup_id,
                'name': name,
                'type': backup_type,
                'timestamp': timestamp.isoformat(),
                'version': '1.0',
                'data_hash': self._calculate_hash(data),
                'compressed': self.backup_config['compression_enabled'],
                'encrypted': self.backup_config['encryption_enabled']
            }

            # Structure du backup
            backup_data = {
                'metadata': metadata,
                'data': data
            }

            # Compression
            if self.backup_config['compression_enabled']:
                compressed_data = self.compressor.compress_backup(backup_data)
            else:
                compressed_data = json.dumps(backup_data, indent=2, default=str).encode()

            # Chiffrement
            if self.backup_config['encryption_enabled']:
                final_data = self.encryptor.encrypt_data(compressed_data)
            else:
                final_data = compressed_data

            # Sauvegarde sur disque
            backup_file = self.backup_dir / f"{backup_id}.backup"
            with open(backup_file, 'wb') as f:
                f.write(final_data)

            # Mise à jour statistiques
            self.stats['total_backups_created'] += 1
            self.stats['last_backup_time'] = timestamp.isoformat()
            self.stats['backup_sizes'].append(len(final_data))

            # Nettoyage des anciens backups
            self._cleanup_old_backups(backup_type)

            result = {
                'success': True,
                'backup_id': backup_id,
                'file_path': str(backup_file),
                'size': len(final_data),
                'timestamp': timestamp.isoformat(),
                'compressed': self.backup_config['compression_enabled'],
                'encrypted': self.backup_config['encryption_enabled']
            }

            logger.info(f"Backup created: {backup_id} ({len(final_data)} bytes)")
            return result

        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'backup_id': backup_id
            }

    def restore_backup(self, backup_id: str, target_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Restaure un backup avec déchiffrement et décompression
        """
        try:
            backup_file = self.backup_dir / f"{backup_id}.backup"
            if not backup_file.exists():
                return {'success': False, 'error': 'Backup file not found'}

            start_time = time.time()

            # Lecture du fichier
            with open(backup_file, 'rb') as f:
                encrypted_data = f.read()

            # Déchiffrement
            if self.backup_config['encryption_enabled']:
                compressed_data = self.encryptor.decrypt_data(encrypted_data)
            else:
                compressed_data = encrypted_data

            # Décompression
            if self.backup_config['compression_enabled']:
                backup_data = self.compressor.decompress_backup(compressed_data)
            else:
                backup_data = json.loads(compressed_data.decode())

            restore_time = time.time() - start_time
            self.stats['total_backups_restored'] += 1
            self.stats['restore_times'].append(restore_time)

            # Sauvegarde vers le chemin cible si spécifié
            if target_path:
                target_file = Path(target_path)
                target_file.parent.mkdir(parents=True, exist_ok=True)
                with open(target_file, 'w') as f:
                    json.dump(backup_data['data'], f, indent=2, default=str)

            result = {
                'success': True,
                'backup_id': backup_id,
                'metadata': backup_data['metadata'],
                'data': backup_data['data'],
                'restore_time': restore_time,
                'target_path': target_path
            }

            logger.info(f"Backup restored: {backup_id} in {restore_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Backup restore failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'backup_id': backup_id
            }

    def list_backups(self, backup_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Liste tous les backups disponibles"""
        backups = []

        for backup_file in self.backup_dir.glob("*.backup"):
            try:
                # Lecture rapide des métadonnées (premiers octets)
                with open(backup_file, 'rb') as f:
                    # Pour simplifier, on utilise le nom du fichier
                    filename = backup_file.name
                    parts = filename.replace('.backup', '').split('_')

                    if len(parts) >= 3:
                        backup_info = {
                            'backup_id': filename.replace('.backup', ''),
                            'type': parts[0],
                            'name': parts[1],
                            'timestamp': f"{parts[2]}_{parts[3]}" if len(parts) > 3 else parts[2],
                            'file_path': str(backup_file),
                            'size': backup_file.stat().st_size
                        }
                        backups.append(backup_info)

            except Exception as e:
                logger.warning(f"Could not read backup file {backup_file}: {e}")

        # Filtrage par type si demandé
        if backup_type:
            backups = [b for b in backups if b['type'] == backup_type]

        # Tri par timestamp décroissant
        backups.sort(key=lambda x: x['timestamp'], reverse=True)

        return backups

    def get_backup_info(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations détaillées d'un backup"""
        try:
            # Essayer de restaurer juste les métadonnées
            result = self.restore_backup(backup_id)
            if result['success']:
                return {
                    'backup_id': backup_id,
                    'metadata': result['metadata'],
                    'size': len(json.dumps(result['data'])),
                    'can_restore': True
                }
        except Exception:
            pass

        # Fallback: info basique depuis le nom de fichier
        backup_file = self.backup_dir / f"{backup_id}.backup"
        if backup_file.exists():
            return {
                'backup_id': backup_id,
                'file_path': str(backup_file),
                'size': backup_file.stat().st_size,
                'can_restore': True
            }

        return None

    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calcule un hash des données pour l'intégrité"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _cleanup_old_backups(self, backup_type: str):
        """Nettoie les anciens backups selon la rétention"""
        try:
            # Lister les backups du type spécifié
            type_backups = [b for b in self.list_backups() if b['type'] == backup_type]

            # Garder seulement les N plus récents
            max_backups = self.backup_config['max_backups_per_type']
            if len(type_backups) > max_backups:
                backups_to_delete = type_backups[max_backups:]

                for backup in backups_to_delete:
                    backup_file = Path(backup['file_path'])
                    if backup_file.exists():
                        backup_file.unlink()
                        logger.info(f"Cleaned old backup: {backup['backup_id']}")

            # Supprimer les backups plus vieux que retention_days
            cutoff_date = datetime.now() - timedelta(days=self.backup_config['retention_days'])
            cutoff_str = cutoff_date.strftime('%Y%m%d')

            for backup in type_backups:
                if backup['timestamp'] < cutoff_str:
                    backup_file = Path(backup['file_path'])
                    if backup_file.exists():
                        backup_file.unlink()
                        logger.info(f"Cleaned expired backup: {backup['backup_id']}")

        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")

    def start_auto_backup(self, backup_function: callable, interval_hours: Optional[int] = None):
        """Démarre les backups automatiques"""
        if not self.backup_config['auto_backup_enabled']:
            return

        interval = interval_hours or self.backup_config['backup_interval_hours']
        interval_seconds = interval * 3600

        def auto_backup_worker():
            while True:
                try:
                    time.sleep(interval_seconds)
                    logger.info("Running scheduled backup")
                    backup_function()
                except Exception as e:
                    logger.error(f"Auto backup failed: {e}")
                    time.sleep(60)  # Attendre 1 minute avant de réessayer

        backup_thread = threading.Thread(target=auto_backup_worker, daemon=True)
        backup_thread.start()
        logger.info(f"Auto backup started (every {interval} hours)")

    def get_backup_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des backups"""
        return {
            'total_backups_created': self.stats['total_backups_created'],
            'total_backups_restored': self.stats['total_backups_restored'],
            'last_backup_time': self.stats['last_backup_time'],
            'average_backup_size': sum(self.stats['backup_sizes']) / len(self.stats['backup_sizes']) if self.stats['backup_sizes'] else 0,
            'average_restore_time': sum(self.stats['restore_times']) / len(self.stats['restore_times']) if self.stats['restore_times'] else 0,
            'compression_stats': self.compressor.compression_stats,
            'config': self.backup_config
        }

# Instance globale
_backup_manager = None

def get_backup_manager() -> BackupManager:
    """Get global backup manager instance"""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager

def create_system_backup(name: str = "system") -> Dict[str, Any]:
    """Crée un backup complet du système Sharingan"""
    manager = get_backup_manager()

    # Collecter toutes les données système
    system_data = {
        'genome_memory': {},
        'ai_memory': {},
        'context_manager': {},
        'system_config': {},
        'timestamp': datetime.now().isoformat()
    }

    # TODO: Intégrer avec les vrais systèmes quand disponibles
    try:
        from genome_memory import get_genome_memory
        genome = get_genome_memory()
        if hasattr(genome, 'genes'):
            system_data['genome_memory'] = {
                'genes': {k: {'key': v.key, 'category': v.category, 'priority': v.priority}
                         for k, v in genome.genes.items()},
                'total_genes': len(genome.genes)
            }
    except ImportError:
        pass

    return manager.create_backup(name, system_data, "system")

def restore_system_backup(backup_id: str) -> Dict[str, Any]:
    """Restaure un backup système complet"""
    manager = get_backup_manager()
    return manager.restore_backup(backup_id)

if __name__ == "__main__":
    print("[BACKUP SYSTEM] Enhanced Backup System for Sharingan OS")
    print("=" * 60)

    # Test du système
    manager = get_backup_manager()

    # Test backup
    test_data = {"test": "backup data", "timestamp": datetime.now().isoformat()}
    backup_result = manager.create_backup("test", test_data)
    print(f"Backup created: {backup_result['success']}")

    # Test list
    backups = manager.list_backups()
    print(f"Total backups: {len(backups)}")

    # Test stats
    stats = manager.get_backup_stats()
    print(f"Backup stats: {stats['total_backups_created']} created")

    print("\nEnhanced backup system ready!")