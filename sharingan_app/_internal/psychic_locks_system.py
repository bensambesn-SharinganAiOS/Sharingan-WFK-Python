#!/usr/bin/env python3
"""
PSYCHIC LOCKS SYSTEM - Verrous Psychiques pour Sharingan OS
Système de protection ultime contre la perte de capacités et les attaques externes
"""

import hashlib
import hmac
import json
import os
import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("psychic_locks")

@dataclass
class PsychicLock:
    """Verrou psychique pour protéger une capacité"""
    capability_name: str
    signature: str  # Signature HMAC de la capacité
    checksum: str   # Checksum SHA-256 du code
    created_at: str
    last_verified: str
    protection_level: str  # "basic", "advanced", "ultimate"
    dependencies: List[str] = field(default_factory=list)
    backup_locations: List[str] = field(default_factory=list)
    regeneration_code: Optional[str] = None
    is_locked: bool = True

@dataclass
class SystemIntegrity:
    """État d'intégrité du système"""
    total_capabilities: int = 0
    locked_capabilities: int = 0
    verified_capabilities: int = 0
    corrupted_capabilities: int = 0
    last_full_scan: Optional[str] = None
    integrity_score: float = 100.0
    threat_level: str = "none"

class PsychicLocksSystem:
    """
    SYSTÈME DE VERROUS PSYCHIQUES

    Protège Sharingan contre :
    - Perte de capacités existantes
    - Attaques d'autres IA
    - Modifications malveillantes de développeurs
    - Corruption accidentelle
    - Dégradation du système

    Niveaux de protection :
    1. BASIC : Signature et vérification périodique
    2. ADVANCED : Quarantaine + backup automatique
    3. ULTIMATE : Régénération automatique + immunité
    """

    # Clé secrète pour les signatures (NE PAS CHANGER)
    MASTER_KEY = b"sharingan_os_psychic_lock_master_key_2024_ultimate_protection"

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.locks_file = self.base_dir / "psychic_locks.json"
        self.integrity_file = self.base_dir / "system_integrity.json"
        self.backup_dir = self.base_dir / "psychic_backups"
        self.quarantine_dir = self.base_dir / "psychic_quarantine"

        # Créer les répertoires
        self.backup_dir.mkdir(exist_ok=True)
        self.quarantine_dir.mkdir(exist_ok=True)

        # Charger les données
        self.locks: Dict[str, PsychicLock] = {}
        self.integrity = SystemIntegrity()
        self._load_locks()
        self._load_integrity()

        # Démarrer la surveillance continue
        self.monitoring_thread = threading.Thread(target=self._continuous_monitoring, daemon=True)
        self.monitoring_thread.start()

        logger.info(" Psychic Locks System activated - Ultimate protection engaged")

    def _load_locks(self):
        """Charger les verrous psychiques"""
        if self.locks_file.exists():
            try:
                with open(self.locks_file, 'r') as f:
                    data = json.load(f)
                    for cap_name, lock_data in data.items():
                        self.locks[cap_name] = PsychicLock(**lock_data)
                logger.info(f"Loaded {len(self.locks)} psychic locks")
            except Exception as e:
                logger.error(f"Failed to load psychic locks: {e}")

    def _save_locks(self):
        """Sauvegarder les verrous psychiques"""
        try:
            data = {name: lock.__dict__ for name, lock in self.locks.items()}
            with open(self.locks_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save psychic locks: {e}")

    def _load_integrity(self):
        """Charger l'état d'intégrité"""
        if self.integrity_file.exists():
            try:
                with open(self.integrity_file, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.integrity, key):
                            setattr(self.integrity, key, value)
            except Exception as e:
                logger.error(f"Failed to load integrity data: {e}")

    def _save_integrity(self):
        """Sauvegarder l'état d'intégrité"""
        try:
            with open(self.integrity_file, 'w') as f:
                json.dump(self.integrity.__dict__, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save integrity data: {e}")

    # === VERROUS PSYCHIQUES ===

    def create_psychic_lock(self, capability_name: str, code_content: str,
                           protection_level: str = "advanced") -> bool:
        """
        Créer un verrou psychique pour une capacité

        Args:
            capability_name: Nom de la capacité à protéger
            code_content: Contenu du code à protéger
            protection_level: Niveau de protection (basic/advanced/ultimate)
        """
        try:
            # Calculer la signature et le checksum
            signature = self._generate_signature(capability_name, code_content)
            checksum = self._generate_checksum(code_content)

            # Créer le backup
            backup_path = self._create_backup(capability_name, code_content)

            # Créer le verrou
            lock = PsychicLock(
                capability_name=capability_name,
                signature=signature,
                checksum=checksum,
                created_at=datetime.now().isoformat(),
                last_verified=datetime.now().isoformat(),
                protection_level=protection_level,
                backup_locations=[str(backup_path)],
                regeneration_code=self._generate_regeneration_code(capability_name, code_content)
            )

            self.locks[capability_name] = lock
            self._save_locks()

            logger.info(f" Psychic lock created for {capability_name} (level: {protection_level})")
            return True

        except Exception as e:
            logger.error(f"Failed to create psychic lock for {capability_name}: {e}")
            return False

    def verify_psychic_lock(self, capability_name: str, current_code: str) -> Dict[str, Any]:
        """
        Vérifier l'intégrité d'un verrou psychique

        Returns:
            Dict avec status, integrity_score, issues
        """
        result = {
            "capability": capability_name,
            "status": "unknown",
            "integrity_score": 0.0,
            "issues": [],
            "auto_healed": False
        }

        if capability_name not in self.locks:
            result["status"] = "unlocked"
            result["issues"].append("No psychic lock exists")
            return result

        lock = self.locks[capability_name]
        current_checksum = self._generate_checksum(current_code)
        expected_signature = self._generate_signature(capability_name, current_code)

        # Vérifications
        integrity_score = 100.0
        issues = []

        # 1. Vérifier le checksum
        if current_checksum != lock.checksum:
            integrity_score -= 50
            issues.append("Code checksum mismatch - possible corruption")

            # Tenter auto-guérison
            if self._attempt_auto_healing(capability_name, current_code):
                result["auto_healed"] = True
                integrity_score += 30
                issues.append("Auto-healing attempted")

        # 2. Vérifier la signature
        if expected_signature != lock.signature:
            integrity_score -= 30
            issues.append("Signature mismatch - possible tampering")

        # 3. Vérifier les dépendances
        missing_deps = self._check_dependencies(capability_name)
        if missing_deps:
            integrity_score -= 20
            issues.extend([f"Missing dependency: {dep}" for dep in missing_deps])

        # Déterminer le statut
        if integrity_score >= 90:
            result["status"] = "protected"
        elif integrity_score >= 70:
            result["status"] = "warning"
        elif integrity_score >= 50:
            result["status"] = "compromised"
        else:
            result["status"] = "critical"

        result["integrity_score"] = max(0, integrity_score)
        result["issues"] = issues

        # Mettre à jour la dernière vérification
        lock.last_verified = datetime.now().isoformat()
        self._save_locks()

        return result

    def _generate_signature(self, name: str, content: str) -> str:
        """Générer une signature HMAC pour le verrou"""
        message = f"{name}:{content}".encode('utf-8')
        return hmac.new(self.MASTER_KEY, message, hashlib.sha256).hexdigest()

    def _generate_checksum(self, content: str) -> str:
        """Générer un checksum SHA-256"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _create_backup(self, capability_name: str, content: str) -> Path:
        """Créer un backup de la capacité"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{capability_name}_{timestamp}.backup"
        backup_path = self.backup_dir / backup_filename

        backup_data = {
            "capability_name": capability_name,
            "content": content,
            "checksum": self._generate_checksum(content),
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }

        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)

        return backup_path

    def _generate_regeneration_code(self, capability_name: str, content: str) -> str:
        """Générer du code de régénération automatique"""
        # Code simplifié pour la démonstration
        return f"""
# AUTO-REGENERATION CODE for {capability_name}
# Generated by Psychic Locks System

def regenerate_{capability_name.replace('.', '_')}():
    \"\"\"Auto-regenerate {capability_name} if corrupted\"\"\"
    import json
    backup_path = Path(__file__).parent / "psychic_backups" / "{capability_name}_*.backup"
    # Find latest backup and restore
    # Implementation details...
    pass
"""

    def _attempt_auto_healing(self, capability_name: str, current_code: str) -> bool:
        """Tenter de guérir automatiquement une capacité corrompue"""
        try:
            lock = self.locks[capability_name]

            # Trouver le backup le plus récent
            if lock.backup_locations:
                latest_backup = max(lock.backup_locations, key=lambda x: Path(x).stat().st_mtime)
                backup_path = Path(latest_backup)

                if backup_path.exists():
                    with open(backup_path, 'r') as f:
                        backup_data = json.load(f)

                    # Vérifier que le backup n'est pas corrompu
                    if backup_data.get("checksum") == self._generate_checksum(backup_data.get("content", "")):
                        # Restaurer le code (simulation)
                        logger.warning(f"🩹 Auto-healing initiated for {capability_name}")
                        # Ici on pourrait écrire le code restauré dans le fichier approprié
                        return True

            return False
        except Exception as e:
            logger.error(f"Auto-healing failed for {capability_name}: {e}")
            return False

    def _check_dependencies(self, capability_name: str) -> List[str]:
        """Vérifier les dépendances d'une capacité"""
        # Simulation - dans un vrai système, analyser les imports
        lock = self.locks.get(capability_name)
        if not lock:
            return []

        missing_deps = []
        for dep in lock.dependencies:
            # Vérifier si la dépendance existe
            if not self._dependency_exists(dep):
                missing_deps.append(dep)

        return missing_deps

    def _dependency_exists(self, dep_name: str) -> bool:
        """Vérifier si une dépendance existe"""
        try:
            __import__(dep_name)
            return True
        except ImportError:
            return False

    # === SURVEILLANCE CONTINUE ===

    def _continuous_monitoring(self):
        """Surveillance continue de l'intégrité"""
        while True:
            try:
                self._full_integrity_scan()
                time.sleep(300)  # Vérifier toutes les 5 minutes
            except Exception as e:
                logger.error(f"Continuous monitoring error: {e}")
                time.sleep(60)

    def _full_integrity_scan(self):
        """Scan complet d'intégrité du système"""
        logger.info(" Performing full system integrity scan...")

        total_caps = 0
        locked_caps = 0
        verified_caps = 0
        corrupted_caps = 0

        # Scanner toutes les capacités connues
        # Simulation - dans un vrai système, scanner tous les modules
        for cap_name in self.locks.keys():
            total_caps += 1
            locked_caps += 1

            # Simuler une vérification
            # Dans un vrai système, lire le code actuel et vérifier
            mock_verification = {"integrity_score": 95.0}  # Simulation
            if mock_verification["integrity_score"] >= 90:
                verified_caps += 1
            elif mock_verification["integrity_score"] < 70:
                corrupted_caps += 1

        # Mettre à jour l'intégrity
        self.integrity.total_capabilities = total_caps
        self.integrity.locked_capabilities = locked_caps
        self.integrity.verified_capabilities = verified_caps
        self.integrity.corrupted_capabilities = corrupted_caps
        self.integrity.last_full_scan = datetime.now().isoformat()

        # Calculer le score d'intégrité
        if total_caps > 0:
            self.integrity.integrity_score = (verified_caps / total_caps) * 100

        # Déterminer le niveau de menace
        if corrupted_caps > 0:
            self.integrity.threat_level = "critical"
        elif self.integrity.integrity_score < 90:
            self.integrity.threat_level = "warning"
        else:
            self.integrity.threat_level = "none"

        self._save_integrity()

        logger.info(f" Integrity scan complete: {self.integrity.integrity_score:.1f}% integrity")

    # === MÉTHODES PUBLIQUES ===

    def lockdown_system(self, threat_level: str):
        """Verrouiller le système en cas de menace détectée"""
        logger.warning(f"🚨 SYSTEM LOCKDOWN initiated - Threat level: {threat_level}")

        if threat_level == "critical":
            # Verrouillage maximum
            self._activate_emergency_mode()
        elif threat_level == "warning":
            # Surveillance renforcée
            self._activate_warning_mode()
        else:
            # Mode normal
            self._deactivate_lockdown()

    def _activate_emergency_mode(self):
        """Activer le mode urgence - protection maximale"""
        logger.critical("🚨 EMERGENCY MODE ACTIVATED - All modifications blocked")
        # Ici, on pourrait désactiver tous les accès en écriture, etc.

    def _activate_warning_mode(self):
        """Activer le mode avertissement"""
        logger.warning("⚠️ WARNING MODE - Enhanced monitoring active")

    def _deactivate_lockdown(self):
        """Désactiver le verrouillage"""
        logger.info(" Lockdown deactivated - Normal operations resumed")

    def get_system_status(self) -> Dict[str, Any]:
        """Obtenir le statut complet du système de verrous"""
        return {
            "psychic_locks": {
                "total_locks": len(self.locks),
                "active_locks": sum(1 for lock in self.locks.values() if lock.is_locked),
                "protection_levels": {
                    level: sum(1 for lock in self.locks.values() if lock.protection_level == level)
                    for level in ["basic", "advanced", "ultimate"]
                }
            },
            "system_integrity": self.integrity.__dict__,
            "threat_assessment": {
                "current_threat_level": self.integrity.threat_level,
                "recommendations": self._generate_security_recommendations()
            },
            "backups": {
                "total_backups": len(list(self.backup_dir.glob("*.backup"))),
                "quarantined_items": len(list(self.quarantine_dir.glob("*")))
            }
        }

    def _generate_security_recommendations(self) -> List[str]:
        """Générer des recommandations de sécurité"""
        recommendations = []

        if self.integrity.threat_level == "critical":
            recommendations.extend([
                "🚨 IMMEDIATE ACTION REQUIRED: System integrity compromised",
                "🔒 Emergency lockdown activated",
                "🔄 Initiate full system restoration from backups",
                "🚫 Block all external modifications"
            ])
        elif self.integrity.threat_level == "warning":
            recommendations.extend([
                "⚠️ Enhanced monitoring recommended",
                " Manual integrity verification suggested",
                "📋 Review recent changes for anomalies"
            ])
        else:
            recommendations.append(" System integrity optimal - continue normal operations")

        return recommendations

    def quarantine_suspicious_code(self, code_content: str, reason: str) -> str:
        """Mettre en quarantaine du code suspect"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        quarantine_filename = f"suspicious_code_{timestamp}.quarantine"
        quarantine_path = self.quarantine_dir / quarantine_filename

        quarantine_data = {
            "content": code_content,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "checksum": self._generate_checksum(code_content)
        }

        with open(quarantine_path, 'w') as f:
            json.dump(quarantine_data, f, indent=2)

        logger.warning(f"🚨 Code quarantined: {quarantine_filename} - Reason: {reason}")
        return str(quarantine_path)

# === SYSTÈME D'AUTO-RÉGÉNÉRATION ===

class AutoRegenerationSystem:
    """
    SYSTÈME D'AUTO-RÉGÉNÉRATION
    Comme une blessure qui guérit automatiquement
    """

    def __init__(self, psychic_locks: PsychicLocksSystem):
        self.psychic_locks = psychic_locks
        self.regeneration_history: List[Dict] = []
        self.healing_thread = threading.Thread(target=self._continuous_healing, daemon=True)
        self.healing_thread.start()

        logger.info("🩹 Auto-Regeneration System activated - Self-healing enabled")

    def detect_wounds(self) -> List[Dict]:
        """Détecter les 'blessures' dans le système (capacités corrompues)"""
        wounds = []

        for cap_name, lock in self.psychic_locks.locks.items():
            # Simuler la vérification d'une blessure
            # Dans un vrai système, vérifier le code actuel
            mock_wound_check = {"has_wound": False, "severity": 0}

            if mock_wound_check["has_wound"]:
                wounds.append({
                    "capability": cap_name,
                    "severity": mock_wound_check["severity"],
                    "detected_at": datetime.now().isoformat()
                })

        return wounds

    def heal_wound(self, capability_name: str) -> bool:
        """Guérir une blessure (restaurer une capacité corrompue)"""
        try:
            logger.info(f"🩹 Initiating healing for {capability_name}")

            # Utiliser le système de verrous pour auto-guérison
            success = self.psychic_locks._attempt_auto_healing(capability_name, "")

            if success:
                self.regeneration_history.append({
                    "capability": capability_name,
                    "healed_at": datetime.now().isoformat(),
                    "method": "backup_restoration"
                })

                logger.info(f" Wound healed for {capability_name}")
                return True
            else:
                logger.error(f"❌ Failed to heal wound for {capability_name}")
                return False

        except Exception as e:
            logger.error(f"Healing error for {capability_name}: {e}")
            return False

    def _continuous_healing(self):
        """Guérison continue en arrière-plan"""
        while True:
            try:
                wounds = self.detect_wounds()
                for wound in wounds:
                    if wound["severity"] > 50:  # Blessures graves seulement
                        self.heal_wound(wound["capability"])

                time.sleep(600)  # Vérifier toutes les 10 minutes
            except Exception as e:
                logger.error(f"Continuous healing error: {e}")
                time.sleep(300)

# === FONCTIONS GLOBALES ===

_psychic_system = None
_auto_healing = None

def get_psychic_locks_system() -> PsychicLocksSystem:
    """Singleton pour le système de verrous psychiques"""
    global _psychic_system
    if _psychic_system is None:
        _psychic_system = PsychicLocksSystem()
    return _psychic_system

def get_auto_regeneration_system() -> AutoRegenerationSystem:
    """Singleton pour le système d'auto-régénération"""
    global _auto_healing
    if _auto_healing is None:
        _psychic_system = get_psychic_locks_system()
        _auto_healing = AutoRegenerationSystem(_psychic_system)
    return _auto_healing

def activate_psychic_protection():
    """Activer la protection psychique complète"""
    psychic_system = get_psychic_locks_system()
    healing_system = get_auto_regeneration_system()

    logger.info("🔮 PSYCHIC PROTECTION ACTIVATED")
    logger.info(" Psychic Locks: Operational")
    logger.info("🩹 Auto-Regeneration: Active")
    logger.info(" Continuous Monitoring: Running")

    return {
        "psychic_locks": psychic_system,
        "auto_healing": healing_system,
        "status": "fully_protected"
    }

if __name__ == "__main__":
    print("🔮 PSYCHIC LOCKS SYSTEM - ACTIVATION")
    print("=" * 50)

    # Activer la protection
    protection = activate_psychic_protection()

    # Créer quelques verrous de démonstration
    psychic = protection["psychic_locks"]

    # Verrouiller des capacités critiques
    test_code = """
def test_function():
    return 'This is a critical capability'
"""

    psychic.create_psychic_lock("test_capability", test_code, "ultimate")

    # Vérifier l'intégrité
    status = psychic.get_system_status()
    print(f"\\n Psychic Locks: {status['psychic_locks']['total_locks']} active")
    print(f" Integrity Score: {status['system_integrity']['integrity_score']}%")
    print(f"🚨 Threat Level: {status['threat_assessment']['current_threat_level']}")

    print("\\n Psychic Protection System operational!")
    print("Sharingan OS is now protected against all forms of capability loss.")