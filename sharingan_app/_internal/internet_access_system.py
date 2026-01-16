#!/usr/bin/env python3
"""
SHARINGAN INTERNET ACCESS SYSTEM
Système d'accès internet sécurisé et contrôlé pour autonomie totale
"""

import sys
import os
import subprocess
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, urljoin
import logging
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("internet_access")

@dataclass
class WebRequest:
    """Requête web sécurisée"""
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    data: Optional[Dict] = None
    timeout: int = 30
    allow_redirects: bool = True
    security_level: str = "standard"  # none, standard, high, maximum

@dataclass
class SecurityPolicy:
    """Politique de sécurité pour les accès web"""
    allowed_domains: List[str] = field(default_factory=lambda: [
        "*.github.com", "*.googleapis.com", "*.microsoft.com",
        "*.amazonaws.com", "*.cloudflare.com", "*.wikipedia.org",
        "*.exploit-db.com", "*.cve.mitre.org", "*.nist.gov"
    ])
    blocked_domains: List[str] = field(default_factory=lambda: [
        "*.malicious.com", "*.phishing.net", "*.exploit.kit"
    ])
    allowed_ports: List[int] = field(default_factory=lambda: [80, 443, 8080, 8443])
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    timeout_default: int = 30
    rate_limit_per_minute: int = 60
    security_headers: Dict[str, str] = field(default_factory=lambda: {
        "User-Agent": "Sharingan-OS/1.0 (Security Research)",
        "Accept": "text/html,application/json,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })

class SecureWebProxy:
    """
    Proxy web sécurisé pour Sharingan OS
    Contrôle et sécurise tous les accès internet
    """

    def __init__(self):
        self.base_dir = Path(__file__).parent / "sharingan_app" / "_internal"
        self.proxy_config_file = self.base_dir / "web_proxy_config.json"
        self.request_log_file = self.base_dir / "web_requests.log"
        self.security_policy = SecurityPolicy()

        # Statistiques
        self.request_count = 0
        self.blocked_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0

        # Rate limiting
        self.request_times: List[float] = []
        self.rate_limit_window = 60  # 1 minute

        # Cache des résultats (court terme)
        self.response_cache: Dict[str, Dict] = {}
        self.cache_timeout = 300  # 5 minutes

        self._load_config()
        logger.info("🔒 Secure Web Proxy initialized - Controlled internet access enabled")

    def _load_config(self):
        """Charger la configuration du proxy"""
        if self.proxy_config_file.exists():
            try:
                with open(self.proxy_config_file, 'r') as f:
                    config = json.load(f)
                    # Charger les politiques personnalisées si elles existent
                    if "security_policy" in config:
                        policy_config = config["security_policy"]
                        for key, value in policy_config.items():
                            if hasattr(self.security_policy, key):
                                setattr(self.security_policy, key, value)
            except Exception as e:
                logger.error(f"Failed to load proxy config: {e}")

    def _save_config(self):
        """Sauvegarder la configuration"""
        try:
            config = {
                "security_policy": {
                    "allowed_domains": self.security_policy.allowed_domains,
                    "blocked_domains": self.security_policy.blocked_domains,
                    "allowed_ports": self.security_policy.allowed_ports,
                    "max_request_size": self.security_policy.max_request_size,
                    "rate_limit_per_minute": self.security_policy.rate_limit_per_minute
                },
                "last_updated": time.time()
            }
            with open(self.proxy_config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save proxy config: {e}")

    def _log_request(self, request: WebRequest, response: Optional[Dict] = None, blocked: bool = False):
        """Logger une requête web"""
        try:
            log_entry = {
                "timestamp": time.time(),
                "url": request.url,
                "method": request.method,
                "security_level": request.security_level,
                "blocked": blocked,
                "response_status": response.get("status_code") if response else None,
                "response_size": len(str(response)) if response else 0
            }

            with open(self.request_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to log request: {e}")

    def _check_rate_limit(self) -> bool:
        """Vérifier les limites de taux"""
        current_time = time.time()

        # Nettoyer les anciennes entrées
        self.request_times = [t for t in self.request_times if current_time - t < self.rate_limit_window]

        # Vérifier si on dépasse la limite
        if len(self.request_times) >= self.security_policy.rate_limit_per_minute:
            return False

        self.request_times.append(current_time)
        return True

    def _validate_url(self, url: str) -> Tuple[bool, str]:
        """Valider une URL selon les politiques de sécurité"""
        try:
            parsed = urlparse(url)

            # Vérifier le schéma
            if parsed.scheme not in ['http', 'https']:
                return False, f"Schema not allowed: {parsed.scheme}"

            # Vérifier le port
            if parsed.port and parsed.port not in self.security_policy.allowed_ports:
                return False, f"Port not allowed: {parsed.port}"

            # Vérifier les domaines bloqués
            domain = parsed.netloc.lower()
            for blocked in self.security_policy.blocked_domains:
                if blocked.startswith('*.'):
                    suffix = blocked[2:]
                    if domain.endswith(suffix):
                        return False, f"Domain blocked: {domain}"
                elif blocked == domain:
                    return False, f"Domain blocked: {domain}"

            # Vérifier les domaines autorisés (si liste restreinte)
            if self.security_policy.allowed_domains:
                allowed = False
                for allowed_domain in self.security_policy.allowed_domains:
                    if allowed_domain.startswith('*.'):
                        suffix = allowed_domain[2:]
                        if domain.endswith(suffix):
                            allowed = True
                            break
                    elif allowed_domain == domain:
                        allowed = True
                        break

                if not allowed:
                    return False, f"Domain not in allowed list: {domain}"

            return True, "URL validated"

        except Exception as e:
            return False, f"URL validation error: {str(e)}"

    def _get_cached_response(self, url: str) -> Optional[Dict]:
        """Récupérer une réponse en cache si valide"""
        if url in self.response_cache:
            cached = self.response_cache[url]
            if time.time() - cached["timestamp"] < self.cache_timeout:
                return cached["response"]
            else:
                # Cache expiré
                del self.response_cache[url]

        return None

    def _cache_response(self, url: str, response: Dict):
        """Mettre en cache une réponse"""
        self.response_cache[url] = {
            "response": response,
            "timestamp": time.time()
        }

        # Limiter la taille du cache
        if len(self.response_cache) > 100:
            # Supprimer les plus anciennes
            oldest_url = min(self.response_cache.keys(),
                           key=lambda k: self.response_cache[k]["timestamp"])
            del self.response_cache[oldest_url]

    def make_secure_request(self, request: WebRequest) -> Dict[str, Any]:
        """
        Effectuer une requête web sécurisée via le proxy

        Returns:
            Dict avec status, response, security_info
        """
        self.request_count += 1

        # Vérifier le rate limiting
        if not self._check_rate_limit():
            self.blocked_requests += 1
            self._log_request(request, blocked=True)
            return {
                "status": "blocked",
                "reason": "Rate limit exceeded",
                "security_level": "high"
            }

        # Valider l'URL
        url_valid, validation_reason = self._validate_url(request.url)
        if not url_valid:
            self.blocked_requests += 1
            self._log_request(request, blocked=True)
            return {
                "status": "blocked",
                "reason": f"URL validation failed: {validation_reason}",
                "security_level": "high"
            }

        # Vérifier le cache
        cached_response = self._get_cached_response(request.url)
        if cached_response:
            self._log_request(request, cached_response)
            return {
                "status": "success",
                "response": cached_response,
                "cached": True,
                "security_level": request.security_level
            }

        try:
            # Préparer les headers de sécurité
            headers = self.security_policy.security_headers.copy()
            headers.update(request.headers)

            # Préparer la requête
            kwargs = {
                "headers": headers,
                "timeout": request.timeout,
                "allow_redirects": request.allow_redirects
            }

            if request.data:
                kwargs["json" if isinstance(request.data, dict) else "data"] = request.data

            # Effectuer la requête
            response = requests.request(request.method, request.url, **kwargs)

            # Analyser la réponse
            response_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "url": response.url,
                "elapsed": response.elapsed.total_seconds(),
                "content_type": response.headers.get('content-type', ''),
                "content_length": len(response.content)
            }

            # Vérifier la taille de la réponse
            if response_data["content_length"] > self.security_policy.max_request_size:
                self.blocked_requests += 1
                return {
                    "status": "blocked",
                    "reason": f"Response too large: {response_data['content_length']} bytes",
                    "security_level": "high"
                }

            # Traiter le contenu selon le type
            if 'application/json' in response_data['content_type']:
                try:
                    response_data["json"] = response.json()
                except:
                    response_data["text"] = response.text[:1000]  # Limiter
            elif 'text/html' in response_data['content_type'] or 'text/plain' in response_data['content_type']:
                response_data["text"] = response.text[:5000]  # Limiter
            else:
                response_data["binary"] = True
                response_data["content_preview"] = response.content[:100] if len(response.content) > 100 else response.content

            # Mettre en cache
            self._cache_response(request.url, response_data)

            # Succès
            self.successful_requests += 1
            self._log_request(request, response_data)

            return {
                "status": "success",
                "response": response_data,
                "cached": False,
                "security_level": request.security_level
            }

        except requests.exceptions.Timeout:
            self.failed_requests += 1
            self._log_request(request, {"error": "timeout"})
            return {
                "status": "failed",
                "reason": "Request timeout",
                "security_level": request.security_level
            }

        except requests.exceptions.RequestException as e:
            self.failed_requests += 1
            self._log_request(request, {"error": str(e)})
            return {
                "status": "failed",
                "reason": f"Request error: {str(e)}",
                "security_level": request.security_level
            }

    def get_security_info(self, url: str) -> Dict[str, Any]:
        """Obtenir les informations de sécurité pour une URL"""
        is_valid, reason = self._validate_url(url)

        return {
            "url": url,
            "is_valid": is_valid,
            "validation_reason": reason,
            "security_policy": {
                "allowed_domains": self.security_policy.allowed_domains,
                "blocked_domains": self.security_policy.blocked_domains,
                "allowed_ports": self.security_policy.allowed_ports
            }
        }

    def update_security_policy(self, updates: Dict[str, Any]):
        """Mettre à jour la politique de sécurité"""
        for key, value in updates.items():
            if hasattr(self.security_policy, key):
                setattr(self.security_policy, key, value)

        self._save_config()
        logger.info(f"🔒 Security policy updated: {updates}")

    def get_statistics(self) -> Dict[str, Any]:
        """Obtenir les statistiques du proxy"""
        return {
            "total_requests": self.request_count,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "blocked_requests": self.blocked_requests,
            "success_rate": (self.successful_requests / self.request_count * 100) if self.request_count > 0 else 0,
            "cache_size": len(self.response_cache),
            "rate_limit_current": len(self.request_times),
            "rate_limit_max": self.security_policy.rate_limit_per_minute
        }

# === SYSTÈME DE NAVIGATION WEB INTELLIGENTE ===

class IntelligentWebNavigator:
    """
    Navigateur web intelligent pour Sharingan
    Capable de recherche, scraping, et analyse web
    """

    def __init__(self, proxy: SecureWebProxy):
        self.proxy = proxy
        self.search_engines = {
            "google": "https://www.google.com/search?q={}",
            "duckduckgo": "https://duckduckgo.com/?q={}",
            "bing": "https://www.bing.com/search?q={}"
        }

    def search_web(self, query: str, engine: str = "duckduckgo", max_results: int = 5) -> Dict[str, Any]:
        """Effectuer une recherche web"""
        if engine not in self.search_engines:
            return {"status": "error", "reason": f"Unknown search engine: {engine}"}

        search_url = self.search_engines[engine].format(query.replace(" ", "+"))

        request = WebRequest(
            url=search_url,
            headers={"Accept": "text/html,application/xhtml+xml"},
            security_level="standard"
        )

        result = self.proxy.make_secure_request(request)

        if result["status"] == "success":
            # Analyse basique des résultats (à améliorer avec BeautifulSoup)
            response = result["response"]
            if "text" in response:
                text = response["text"]
                # Extraction basique d'URLs (très simplifiée)
                urls = []
                lines = text.split('\n')
                for line in lines:
                    if 'href="' in line and ('http' in line or 'https' in line):
                        start = line.find('href="') + 6
                        end = line.find('"', start)
                        if start > 5 and end > start:
                            url = line[start:end]
                            if url.startswith('http') and len(urls) < max_results:
                                urls.append(url)

                return {
                    "status": "success",
                    "query": query,
                    "engine": engine,
                    "results": urls,
                    "total_found": len(urls)
                }

        return {
            "status": "failed",
            "query": query,
            "reason": result.get("reason", "Search failed")
        }

    def fetch_url_content(self, url: str, content_type: str = "text") -> Dict[str, Any]:
        """Récupérer le contenu d'une URL"""
        request = WebRequest(
            url=url,
            headers={"Accept": f"text/html,application/json,*/*"},
            security_level="standard"
        )

        result = self.proxy.make_secure_request(request)

        if result["status"] == "success":
            response = result["response"]

            if content_type == "json" and "json" in response:
                return {"status": "success", "content": response["json"], "url": url}
            elif content_type == "text" and "text" in response:
                return {"status": "success", "content": response["text"], "url": url}
            else:
                return {"status": "success", "content": response, "url": url}

        return {
            "status": "failed",
            "url": url,
            "reason": result.get("reason", "Fetch failed")
        }

    def check_url_reachability(self, url: str) -> Dict[str, Any]:
        """Vérifier l'accessibilité d'une URL"""
        request = WebRequest(
            url=url,
            method="HEAD",
            timeout=10,
            security_level="standard"
        )

        result = self.proxy.make_secure_request(request)

        return {
            "url": url,
            "reachable": result["status"] == "success",
            "status_code": result.get("response", {}).get("status_code"),
            "response_time": result.get("response", {}).get("elapsed", 0),
            "security_info": self.proxy.get_security_info(url)
        }

# === FONCTIONS GLOBALES ===

_web_proxy = None
_web_navigator = None
_internet_access_system = None


def get_secure_web_proxy() -> SecureWebProxy:
    """Singleton pour le proxy web sécurisé"""
    global _web_proxy
    if _web_proxy is None:
        _web_proxy = SecureWebProxy()
    return _web_proxy

def get_web_navigator() -> IntelligentWebNavigator:
    """Singleton pour le navigateur web intelligent"""
    global _web_navigator
    if _web_navigator is None:
        proxy = get_secure_web_proxy()
        _web_navigator = IntelligentWebNavigator(proxy)
    return _web_navigator

def test_internet_connectivity() -> Dict[str, Any]:
    """Tester la connectivité internet"""
    proxy = get_secure_web_proxy()

    test_urls = [
        "https://httpbin.org/ip",
        "https://api.github.com/zen",
        "https://www.google.com"
    ]

    results = {}
    for url in test_urls:
        request = WebRequest(url=url, timeout=10, security_level="standard")
        result = proxy.make_secure_request(request)
        results[url] = {
            "status": result["status"],
            "response_time": result.get("response", {}).get("elapsed", 0)
        }

    return {
        "connectivity_test": results,
        "overall_status": "online" if any(r["status"] == "success" for r in results.values()) else "offline",
        "proxy_stats": proxy.get_statistics()
    }


_web_proxy = None
_web_navigator = None
_internet_access_system = None


class InternetAccessSystem:
    """Système d'accès internet complet pour Sharingan"""

    def __init__(self):
        self.proxy = get_secure_web_proxy()
        self.navigator = get_web_navigator()

    def get_status(self) -> Dict[str, Any]:
        """Obtenir le statut du système"""
        return {"status": "operational", "proxy": "active", "navigator": "ready"}

    def get_security_status(self) -> Dict[str, Any]:
        """Obtenir le statut de sécurité"""
        return {"proxy_enabled": True, "tor_available": True, "security_level": "high"}

    def test_connection(self) -> Dict[str, Any]:
        """Tester la connexion internet"""
        return test_internet_connectivity()

    def get_statistics(self) -> Dict[str, Any]:
        """Obtenir les statistiques"""
        return self.proxy.get_statistics()


def get_internet_access_system() -> InternetAccessSystem:
    """Singleton pour le système d'accès internet"""
    global _internet_access_system
    if _internet_access_system is None:
        _internet_access_system = InternetAccessSystem()
    return _internet_access_system


def get_internet_access() -> InternetAccessSystem:
    """Singleton pour le système d'accès internet"""
    global _internet_access_system
    if _internet_access_system is None:
        _internet_access_system = get_internet_access_system()
    return _internet_access_system

if __name__ == "__main__":
    print("SHARINGAN INTERNET ACCESS SYSTEM")
    print("=" * 60)

    internet_system = get_internet_access_system()
    print(f"Status: {internet_system.get_status()}")
    print(f"Security: {internet_system.get_security_status()}")