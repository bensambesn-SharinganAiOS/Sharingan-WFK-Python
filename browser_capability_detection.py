#!/usr/bin/env python3
"""
Capability Detection System - Sharingan OS
=========================================

Système de détection automatique des capacités disponibles.
Remplace les détections hardcodées par un système intelligent.

Fonctionnalités:
- Détection automatique des navigateurs et capacités
- Évaluation des modes de contrôle disponibles
- Scoring et sélection intelligente
- Cache et optimisation des performances
"""

import subprocess
import requests
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger("sharingan.capability_detection")

class CapabilityType(Enum):
    """Types de capacités détectables"""
    CDP_CONTROL = "cdp_control"
    XDOTOOL_CONTROL = "xdotool_control"
    HYBRID_CONTROL = "hybrid_control"
    WINDOW_MANAGEMENT = "window_management"
    TERMINAL_ACCESS = "terminal_access"
    USER_SESSION_PRESERVED = "user_session_preserved"
    JAVASCRIPT_EXECUTION = "javascript_execution"
    SCREENSHOT_CAPABLE = "screenshot_capable"
    NETWORK_ACCESS = "network_access"

class DetectionMethod(Enum):
    """Méthodes de détection"""
    PORT_SCAN = "port_scan"
    PROCESS_SCAN = "process_scan"
    WINDOW_SCAN = "window_scan"
    API_TEST = "api_test"
    COMMAND_TEST = "command_test"

@dataclass
class CapabilityResult:
    """Résultat d'une détection de capacité"""
    capability: CapabilityType
    available: bool
    confidence: float  # 0.0 à 1.0
    method: DetectionMethod
    details: Optional[Dict[str, Any]] = None
    last_checked: float = 0

@dataclass
class BrowserProfile:
    """Profil complet d'un navigateur détecté"""
    name: str
    type: str
    capabilities: List[CapabilityResult]
    score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

    @property
    def is_available(self) -> bool:
        """Vérifie si le navigateur est disponible"""
        return any(cap.available for cap in self.capabilities)

    @property
    def best_control_mode(self) -> Optional[str]:
        """Retourne le meilleur mode de contrôle disponible"""
        control_modes = []
        for cap in self.capabilities:
            if cap.capability.value.endswith('_control') and cap.available:
                control_modes.append((cap.capability.value, cap.confidence))

        if control_modes:
            return max(control_modes, key=lambda x: x[1])[0]
        return None

class CapabilityDetector:
    """
    DÉTECTEUR INTELLIGENT DE CAPACITÉS

    Système centralisé pour :
    - Détecter automatiquement tous les navigateurs
    - Évaluer leurs capacités de contrôle
    - Sélectionner le meilleur mode pour chaque opération
    - Cacher les résultats pour optimiser les performances
    """

    def __init__(self, cache_timeout: int = 30):
        self.cache_timeout = cache_timeout  # secondes
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._detectors = {
            CapabilityType.CDP_CONTROL: self._detect_cdp_control,
            CapabilityType.XDOTOOL_CONTROL: self._detect_xdotool_control,
            CapabilityType.HYBRID_CONTROL: self._detect_hybrid_control,
            CapabilityType.WINDOW_MANAGEMENT: self._detect_window_management,
            CapabilityType.TERMINAL_ACCESS: self._detect_terminal_access,
            CapabilityType.USER_SESSION_PRESERVED: self._detect_user_session,
            CapabilityType.JAVASCRIPT_EXECUTION: self._detect_javascript_execution,
            CapabilityType.SCREENSHOT_CAPABLE: self._detect_screenshot_capability,
            CapabilityType.NETWORK_ACCESS: self._detect_network_access,
        }

        logger.info("🔍 CapabilityDetector initialisé")

    def _get_cached(self, key: str) -> Optional[Any]:
        """Récupère un résultat en cache"""
        if key in self._cache:
            timestamp, value = self._cache[key]
            if time.time() - timestamp < self.cache_timeout:
                return value
            else:
                del self._cache[key]
        return None

    def _set_cached(self, key: str, value: Any):
        """Met en cache un résultat"""
        self._cache[key] = (time.time(), value)

    async def detect_all_capabilities(self) -> Dict[str, BrowserProfile]:
        """
        Détection complète de tous les navigateurs et leurs capacités

        Returns:
            Dictionnaire nom -> profil de navigateur
        """
        logger.info("🔍 Détection complète des capacités...")

        # Détecter tous les navigateurs
        browsers = await self._detect_all_browsers()

        # Évaluer les capacités de chaque navigateur
        profiles = {}
        for browser_info in browsers:
            profile = await self._evaluate_browser_capabilities(browser_info)
            profiles[profile.name] = profile

        logger.info(f"📊 {len(profiles)} navigateurs profilés")
        return profiles

    async def _detect_all_browsers(self) -> List[Dict[str, Any]]:
        """Détecte tous les navigateurs disponibles"""
        browsers = []

        # 1. Détection CDP (navigateurs avec debugging)
        cdp_browsers = await self._detect_cdp_browsers()
        browsers.extend(cdp_browsers)

        # 2. Détection xdotool (navigateurs utilisateur)
        xdotool_browsers = await self._detect_xdotool_browsers()
        browsers.extend(xdotool_browsers)

        # 3. Fusionner les doublons
        browsers = self._merge_browser_detections(browsers)

        return browsers

    async def _detect_cdp_browsers(self) -> List[Dict[str, Any]]:
        """Détecte les navigateurs avec CDP actif"""
        browsers = []

        # Ports communs pour CDP
        common_ports = [9222, 9999, 9223, 9224]

        for port in common_ports:
            try:
                response = requests.get(f'http://localhost:{port}/json', timeout=2)
                if response.status_code == 200:
                    tabs = response.json()
                    if tabs:
                        # Analyser le premier onglet
                        tab = tabs[0]
                        browsers.append({
                            'name': f'cdp_port_{port}',
                            'type': 'cdp',
                            'port': port,
                            'title': tab.get('title', 'Chrome CDP'),
                            'url': tab.get('url', ''),
                            'tabs_count': len(tabs)
                        })
            except:
                pass

        return browsers

    async def _detect_xdotool_browsers(self) -> List[Dict[str, Any]]:
        """Détecte les navigateurs via xdotool"""
        browsers = []

        try:
            # Scanner les fenêtres
            result = subprocess.run(
                "wmctrl -l -x",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split(None, 3)
                        if len(parts) >= 4:
                            win_id, desktop, wm_class, title = parts[0], parts[1], parts[2], parts[3]

                            # Identifier les navigateurs
                            if any(browser in wm_class.lower() for browser in ['chrome', 'chromium', 'firefox']):
                                browser_type = 'chrome' if 'chrome' in wm_class.lower() else 'firefox'
                                browsers.append({
                                    'name': win_id,
                                    'type': 'user',
                                    'window_id': win_id,
                                    'wm_class': wm_class,
                                    'title': title,
                                    'browser_type': browser_type
                                })

        except Exception as e:
            logger.error(f"Erreur détection xdotool: {e}")

        return browsers

    def _merge_browser_detections(self, browsers: List[Dict]) -> List[Dict]:
        """Fusionne les détections de navigateurs pour éviter les doublons"""
        merged = []
        seen = set()

        for browser in browsers:
            key = (browser.get('window_id'), browser.get('port'))

            if key not in seen:
                seen.add(key)
                merged.append(browser)

        return merged

    async def _evaluate_browser_capabilities(self, browser_info: Dict[str, Any]) -> BrowserProfile:
        """Évalue toutes les capacités d'un navigateur"""
        name = browser_info['name']
        browser_type = browser_info['type']

        # Vérifier le cache
        cache_key = f"capabilities_{name}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        logger.debug(f"🔍 Évaluation des capacités de {name}...")

        # Tester chaque capacité
        capabilities = []
        for cap_type, detector in self._detectors.items():
            try:
                result = await detector(browser_info)
                if result:
                    capabilities.append(result)
            except Exception as e:
                logger.error(f"Erreur détection {cap_type.value}: {e}")

        # Calculer le score global
        score = sum(cap.confidence for cap in capabilities if cap.available) / len(capabilities) if capabilities else 0

        profile = BrowserProfile(
            name=name,
            type=browser_type,
            capabilities=capabilities,
            score=score,
            metadata=browser_info
        )

        # Mettre en cache
        self._set_cached(cache_key, profile)

        return profile

    # === DÉTECTEURS SPÉCIFIQUES ===

    async def _detect_cdp_control(self, browser_info: Dict) -> CapabilityResult:
        """Détecte la capacité de contrôle CDP"""
        if browser_info.get('type') == 'cdp':
            port = browser_info.get('port')
            if port:
                try:
                    # Tester la connexion CDP
                    response = requests.get(f'http://localhost:{port}/json', timeout=2)
                    if response.status_code == 200:
                        tabs = response.json()
                        return CapabilityResult(
                            capability=CapabilityType.CDP_CONTROL,
                            available=True,
                            confidence=0.9,
                            method=DetectionMethod.API_TEST,
                            details={'port': port, 'tabs': len(tabs)}
                        )
                except:
                    pass

        return CapabilityResult(
            capability=CapabilityType.CDP_CONTROL,
            available=False,
            confidence=0.0,
            method=DetectionMethod.API_TEST,
            details={}
        )

    async def _detect_xdotool_control(self, browser_info: Dict) -> CapabilityResult:
        """Détecte la capacité de contrôle xdotool"""
        window_id = browser_info.get('window_id')
        if window_id:
            try:
                # Tester l'activation de fenêtre
                result = subprocess.run(
                    f"xdotool windowactivate {window_id}",
                    shell=True, capture_output=True, timeout=2
                )

                available = result.returncode == 0
                confidence = 0.8 if available else 0.0

                return CapabilityResult(
                    capability=CapabilityType.XDOTOOL_CONTROL,
                    available=available,
                    confidence=confidence,
                    method=DetectionMethod.COMMAND_TEST,
                    details={'window_id': window_id}
                )
            except:
                pass

        return CapabilityResult(
            capability=CapabilityType.XDOTOOL_CONTROL,
            available=False,
            confidence=0.0,
            method=DetectionMethod.COMMAND_TEST
        )

    async def _detect_hybrid_control(self, browser_info: Dict) -> CapabilityResult:
        """Détecte la capacité de contrôle hybride"""
        # Nécessite les deux modes
        cdp_cap = await self._detect_cdp_control(browser_info)
        xdotool_cap = await self._detect_xdotool_control(browser_info)

        available = cdp_cap.available and xdotool_cap.available
        confidence = min(cdp_cap.confidence, xdotool_cap.confidence) if available else 0.0

        return CapabilityResult(
            capability=CapabilityType.HYBRID_CONTROL,
            available=available,
            confidence=confidence,
            method=DetectionMethod.API_TEST,
            details={'cdp_available': cdp_cap.available, 'xdotool_available': xdotool_cap.available}
        )

    async def _detect_window_management(self, browser_info: Dict) -> CapabilityResult:
        """Détecte la gestion de fenêtres"""
        try:
            # Tester wmctrl
            result = subprocess.run(
                "wmctrl -l",
                shell=True, capture_output=True, timeout=2
            )

            available = result.returncode == 0
            confidence = 0.9 if available else 0.0

            return CapabilityResult(
                capability=CapabilityType.WINDOW_MANAGEMENT,
                available=available,
                confidence=confidence,
                method=DetectionMethod.COMMAND_TEST,
                details={'windows_count': len(result.stdout.strip().splitlines()) if available else 0}
            )
        except:
            return CapabilityResult(
                capability=CapabilityType.WINDOW_MANAGEMENT,
                available=False,
                confidence=0.0,
                method=DetectionMethod.COMMAND_TEST
            )

    async def _detect_terminal_access(self, browser_info: Dict) -> CapabilityResult:
        """Détecte l'accès terminal"""
        try:
            result = subprocess.run(
                "ps aux | grep -E 'terminal|gnome-terminal' | grep -v grep | head -1",
                shell=True, capture_output=True, text=True, timeout=2
            )

            available = result.returncode == 0 and bool(result.stdout.strip())
            confidence = 0.8 if available else 0.0

            return CapabilityResult(
                capability=CapabilityType.TERMINAL_ACCESS,
                available=available,
                confidence=confidence,
                method=DetectionMethod.PROCESS_SCAN
            )
        except:
            return CapabilityResult(
                capability=CapabilityType.TERMINAL_ACCESS,
                available=False,
                confidence=0.0,
                method=DetectionMethod.PROCESS_SCAN
            )

    async def _detect_user_session(self, browser_info: Dict) -> CapabilityResult:
        """Détecte si la session utilisateur est préservée"""
        # Pour les navigateurs utilisateur (pas CDP), la session est préservée
        is_user_browser = browser_info.get('type') == 'user'

        return CapabilityResult(
            capability=CapabilityType.USER_SESSION_PRESERVED,
            available=is_user_browser,
            confidence=0.95 if is_user_browser else 0.0,
            method=DetectionMethod.PROCESS_SCAN,
            details={'is_user_browser': is_user_browser}
        )

    async def _detect_javascript_execution(self, browser_info: Dict) -> CapabilityResult:
        """Détecte l'exécution JavaScript"""
        # Disponible si CDP ou contrôle hybride
        cdp_cap = await self._detect_cdp_control(browser_info)

        return CapabilityResult(
            capability=CapabilityType.JAVASCRIPT_EXECUTION,
            available=cdp_cap.available,
            confidence=cdp_cap.confidence,
            method=DetectionMethod.API_TEST,
            details={'via_cdp': cdp_cap.available}
        )

    async def _detect_screenshot_capability(self, browser_info: Dict) -> CapabilityResult:
        """Détecte la capacité de capture d'écran"""
        try:
            # Tester si scrot ou import est disponible
            result1 = subprocess.run(
                "which scrot",
                shell=True, capture_output=True, timeout=2
            )

            result2 = subprocess.run(
                "which import",
                shell=True, capture_output=True, timeout=2
            )

            available = result1.returncode == 0 or result2.returncode == 0
            confidence = 0.9 if available else 0.0

            return CapabilityResult(
                capability=CapabilityType.SCREENSHOT_CAPABLE,
                available=available,
                confidence=confidence,
                method=DetectionMethod.COMMAND_TEST,
                details={'scrot': result1.returncode == 0, 'imagemagick': result2.returncode == 0}
            )
        except:
            return CapabilityResult(
                capability=CapabilityType.SCREENSHOT_CAPABLE,
                available=False,
                confidence=0.0,
                method=DetectionMethod.COMMAND_TEST
            )

    async def _detect_network_access(self, browser_info: Dict) -> CapabilityResult:
        """Détecte l'accès réseau"""
        try:
            # Test simple de connectivité
            response = requests.get('https://www.google.com', timeout=3)
            available = response.status_code == 200
            confidence = 0.95 if available else 0.0

            return CapabilityResult(
                capability=CapabilityType.NETWORK_ACCESS,
                available=available,
                confidence=confidence,
                method=DetectionMethod.API_TEST,
                details={'status_code': response.status_code if available else None}
            )
        except:
            return CapabilityResult(
                capability=CapabilityType.NETWORK_ACCESS,
                available=False,
                confidence=0.0,
                method=DetectionMethod.API_TEST
            )

    # === MÉTHODES UTILITAIRES ===

    def get_best_browser_for_operation(self, operation: str, profiles: Dict[str, BrowserProfile]) -> Optional[BrowserProfile]:
        """
        Sélectionne le meilleur navigateur pour une opération donnée

        Args:
            operation: Type d'opération (navigate, scroll, click, etc.)
            profiles: Profils de navigateurs disponibles

        Returns:
            Meilleur profil ou None
        """
        if not profiles:
            return None

        candidates = []

        for profile in profiles.values():
            if not profile.is_available:
                continue

            score = profile.score

            # Bonus selon l'opération
            if operation in ['navigate', 'search', 'read']:
                # Préférer CDP pour ces opérations
                if any(cap.capability == CapabilityType.CDP_CONTROL and cap.available for cap in profile.capabilities):
                    score += 0.3
            elif operation in ['scroll', 'click', 'type']:
                # Préférer xdotool pour les interactions physiques
                if any(cap.capability == CapabilityType.XDOTOOL_CONTROL and cap.available for cap in profile.capabilities):
                    score += 0.3

            candidates.append((profile, score))

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]

        return None

    def clear_cache(self):
        """Vide le cache des capacités"""
        self._cache.clear()
        logger.info("🗑️ Cache des capacités vidé")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Statistiques du cache"""
        return {
            'cached_items': len(self._cache),
            'cache_timeout': self.cache_timeout
        }

# === FONCTIONS UTILITAIRES ===

_capability_detector: Optional[CapabilityDetector] = None

def get_capability_detector() -> CapabilityDetector:
    """Singleton du détecteur de capacités"""
    global _capability_detector
    if _capability_detector is None:
        _capability_detector = CapabilityDetector()
    return _capability_detector

async def detect_capabilities():
    """Détection rapide des capacités"""
    detector = get_capability_detector()
    return await detector.detect_all_capabilities()

async def get_best_browser_for(operation: str):
    """Trouve le meilleur navigateur pour une opération"""
    profiles = await detect_capabilities()
    detector = get_capability_detector()
    return detector.get_best_browser_for_operation(operation, profiles)

if __name__ == "__main__":
    # Test du système de détection
    async def test_capability_detection():
        print("🧪 TEST DU SYSTÈME DE DÉTECTION DE CAPACITÉS")
        print("=" * 55)

        detector = CapabilityDetector()

        # Détection complète
        print("🔍 Détection des capacités...")
        profiles = await detector.detect_all_capabilities()

        print(f"📊 {len(profiles)} navigateurs détectés:")

        for name, profile in profiles.items():
            print(f"\n🌐 {name} ({profile.type}) - Score: {profile.score:.2f}")
            print(f"   Disponible: {'✅' if profile.is_available else '❌'}")

            if profile.capabilities:
                print("   Capacités:")
                for cap in profile.capabilities:
                    status = "✅" if cap.available else "❌"
                    confidence = f"{cap.confidence:.1f}"
                    print(f"     {status} {cap.capability.value} ({confidence}) - {cap.method.value}")

            if profile.best_control_mode:
                print(f"   Meilleur mode: {profile.best_control_mode}")

        # Test de sélection
        print("\n🎯 Test de sélection par opération:")
        operations = ['navigate', 'scroll', 'click', 'read']

        for op in operations:
            best = detector.get_best_browser_for_operation(op, profiles)
            if best:
                print(f"   {op}: {best.name} (score: {best.score:.2f})")
            else:
                print(f"   {op}: Aucun navigateur adapté")

        print("\n🎉 Test terminé!")

    asyncio.run(test_capability_detection())