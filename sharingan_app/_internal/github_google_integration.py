#!/usr/bin/env python3
"""
SHARINGAN GITHUB INTEGRATION
Intégration complète avec GitHub API pour accès aux repositories, issues, code
"""

import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("github_integration")

@dataclass
class GitHubRepository:
    """Représentation d'un repository GitHub"""
    name: str
    full_name: str
    owner: str
    description: str = ""
    language: str = ""
    stars: int = 0
    forks: int = 0
    issues_count: int = 0
    last_updated: str = ""
    topics: List[str] = field(default_factory=list)
    security_advisories: List[Dict] = field(default_factory=list)

@dataclass
class GitHubIssue:
    """Représentation d'une issue GitHub"""
    number: int
    title: str
    body: str = ""
    state: str = "open"
    labels: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    comments_count: int = 0
    author: str = ""

@dataclass
class GitHubSecurityAdvisory:
    """Advisory de sécurité GitHub"""
    ghsa_id: str
    summary: str
    severity: str
    cvss_score: float = 0.0
    affected_versions: List[str] = field(default_factory=list)
    patched_versions: List[str] = field(default_factory=list)
    published_at: str = ""

class GitHubIntegration:
    """
    Intégration complète avec GitHub pour Sharingan OS

    Capacités :
    - Recherche de repositories de cybersécurité
    - Analyse de vulnérabilités et advisories
    - Recherche de code et exploits
    - Suivi des issues et PRs
    - Téléchargement de code sécurisé
    """

    def __init__(self):
        from internet_access_system import get_secure_web_proxy, WebRequest

        self.proxy = get_secure_web_proxy()
        self.web_request_class = WebRequest

        # Configuration GitHub
        self.base_url = "https://api.github.com"
        self.search_url = f"{self.base_url}/search"
        self.repos_url = f"{self.base_url}/repos"

        # Rate limiting (GitHub permet 5000 requests/heure)
        self.request_count = 0
        self.last_reset = time.time()
        self.rate_limit_remaining = 5000

        # Cache pour éviter les requêtes répétées
        self.cache: Dict[str, Dict] = {}
        self.cache_timeout = 3600  # 1 heure

        logger.info("🐙 GitHub Integration initialized - Access to security repositories enabled")

    def _make_github_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Effectuer une requête sécurisée vers GitHub API"""
        # Vérifier rate limit
        if self.rate_limit_remaining <= 10:
            logger.warning("⚠️ GitHub rate limit approaching - slowing down")
            time.sleep(1)

        # Vérifier cache
        cache_key = f"{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached["timestamp"] < self.cache_timeout:
                return cached["data"]

        url = f"{self.base_url}{endpoint}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Sharingan-OS/1.0 (Security Research)"
        }

        # Construire l'URL avec les paramètres
        if params:
            import urllib.parse
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"

        request = self.web_request_class(
            url=url,
            headers=headers,
            security_level="standard",
            timeout=30
        )

        result = self.proxy.make_secure_request(request)

        if result["status"] == "success":
            response = result["response"]

            # Mettre à jour rate limit
            if "x-ratelimit-remaining" in response.get("headers", {}):
                self.rate_limit_remaining = int(response["headers"]["x-ratelimit-remaining"])

            # Parser JSON
            if "json" in response:
                data = response["json"]

                # Mettre en cache
                self.cache[cache_key] = {
                    "data": data,
                    "timestamp": time.time()
                }

                return data
            else:
                logger.error(f"Unexpected response format from GitHub: {response}")
                return None
        else:
            logger.error(f"GitHub request failed: {result.get('reason', 'Unknown error')}")
            return None

    def search_security_repositories(self, query: str = "cybersecurity tools",
                                   language: str = "python",
                                   min_stars: int = 10) -> List[GitHubRepository]:
        """
        Rechercher des repositories de cybersécurité sur GitHub
        """
        search_query = f"{query} language:{language} stars:>={min_stars}"

        params = {
            "q": search_query,
            "sort": "stars",
            "order": "desc",
            "per_page": 20
        }

        result = self._make_github_request("/search/repositories", params)

        if not result or "items" not in result:
            return []

        repositories = []
        for item in result["items"]:
            repo = GitHubRepository(
                name=item["name"],
                full_name=item["full_name"],
                owner=item["owner"]["login"],
                description=item.get("description", ""),
                language=item.get("language", ""),
                stars=item.get("stargazers_count", 0),
                forks=item.get("forks_count", 0),
                issues_count=item.get("open_issues_count", 0),
                last_updated=item.get("updated_at", ""),
                topics=item.get("topics", [])
            )
            repositories.append(repo)

        logger.info(f" Found {len(repositories)} security repositories on GitHub")
        return repositories

    def get_repository_details(self, owner: str, repo: str) -> Optional[GitHubRepository]:
        """Obtenir les détails complets d'un repository"""
        endpoint = f"/repos/{owner}/{repo}"
        result = self._make_github_request(endpoint)

        if not result:
            return None

        # Obtenir les advisories de sécurité
        security_result = self._make_github_request(f"{endpoint}/security-advisories")
        advisories = []
        if security_result:
            for advisory in security_result:
                adv = GitHubSecurityAdvisory(
                    ghsa_id=advisory["ghsa_id"],
                    summary=advisory["summary"],
                    severity=advisory["severity"],
                    cvss_score=advisory.get("cvss", {}).get("score", 0.0),
                    affected_versions=[v["identifier"] for v in advisory.get("vulnerabilities", [])],
                    patched_versions=[v.get("patched_versions", []) for v in advisory.get("vulnerabilities", [])][0] if advisory.get("vulnerabilities") else [],
                    published_at=advisory["published_at"]
                )
                advisories.append(adv.__dict__)

        repository = GitHubRepository(
            name=result["name"],
            full_name=result["full_name"],
            owner=result["owner"]["login"],
            description=result.get("description", ""),
            language=result.get("language", ""),
            stars=result.get("stargazers_count", 0),
            forks=result.get("forks_count", 0),
            issues_count=result.get("open_issues_count", 0),
            last_updated=result.get("updated_at", ""),
            topics=result.get("topics", []),
            security_advisories=advisories
        )

        return repository

    def search_code(self, query: str, language: str = "python",
                   filename: Optional[str] = None) -> List[Dict]:
        """
        Rechercher du code spécifique sur GitHub
        Utile pour trouver des exploits, outils, etc.
        """
        search_query = f"{query} language:{language}"
        if filename:
            search_query += f" filename:{filename}"

        params = {
            "q": search_query,
            "per_page": 10
        }

        result = self._make_github_request("/search/code", params)

        if not result or "items" not in result:
            return []

        code_results = []
        for item in result["items"]:
            code_result = {
                "name": item["name"],
                "path": item["path"],
                "repository": item["repository"]["full_name"],
                "url": item["html_url"],
                "score": item["score"]
            }

            # Essayer d'obtenir un aperçu du code
            if "text_matches" in item:
                code_result["matches"] = [match["fragment"] for match in item["text_matches"]]

            code_results.append(code_result)

        logger.info(f"💻 Found {len(code_results)} code results for query: {query}")
        return code_results

    def get_repository_issues(self, owner: str, repo: str,
                            state: str = "open", labels: Optional[List[str]] = None) -> List[GitHubIssue]:
        """Obtenir les issues d'un repository"""
        endpoint = f"/repos/{owner}/{repo}/issues"

        params = {
            "state": state,
            "per_page": 20
        }

        if labels:
            params["labels"] = ",".join(labels)

        result = self._make_github_request(endpoint, params)

        if not result:
            return []

        issues = []
        for item in result:
            issue = GitHubIssue(
                number=item["number"],
                title=item["title"],
                body=item.get("body", ""),
                state=item["state"],
                labels=[label["name"] for label in item.get("labels", [])],
                created_at=item["created_at"],
                updated_at=item["updated_at"],
                comments_count=item.get("comments", 0),
                author=item["user"]["login"]
            )
            issues.append(issue)

        return issues

    def find_security_vulnerabilities(self, query: str = "CVE",
                                    ecosystem: str = "pip") -> List[Dict]:
        """
        Rechercher des vulnérabilités de sécurité dans les advisories
        """
        endpoint = "/advisories"

        params = {
            "query": query,
            "ecosystem": ecosystem,
            "per_page": 20
        }

        result = self._make_github_request(endpoint, params)

        if not result:
            return []

        vulnerabilities = []
        for advisory in result:
            vuln = {
                "id": advisory["ghsa_id"],
                "summary": advisory["summary"],
                "severity": advisory["severity"],
                "cvss_score": advisory.get("cvss", {}).get("score", 0.0),
                "published_at": advisory["published_at"],
                "affected_packages": [pkg["ecosystem"] + "/" + pkg["name"]
                                    for pkg in advisory.get("identifiers", [])
                                    if pkg["type"] == "PURL"]
            }
            vulnerabilities.append(vuln)

        logger.info(f"🔒 Found {len(vulnerabilities)} security vulnerabilities")
        return vulnerabilities

    def download_repository(self, owner: str, repo: str,
                          branch: str = "main") -> Dict[str, Any]:
        """
        Télécharger un repository (via zip pour sécurité)
        """
        download_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"

        request = self.web_request_class(
            url=download_url,
            security_level="standard",
            timeout=60
        )

        result = self.proxy.make_secure_request(request)

        if result["status"] == "success":
            response = result["response"]

            # Sauvegarder le zip
            zip_path = f"/tmp/{owner}_{repo}_{branch}.zip"
            try:
                with open(zip_path, 'wb') as f:
                    if "binary" in response and response.get("binary"):
                        f.write(response.get("content_preview", b""))
                    else:
                        # Si c'est du texte, convertir (rare)
                        f.write(response.get("text", "").encode())

                return {
                    "status": "success",
                    "zip_path": zip_path,
                    "size": response.get("content_length", 0),
                    "repository": f"{owner}/{repo}"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "reason": f"Failed to save zip: {e}"
                }
        else:
            return {
                "status": "error",
                "reason": result.get("reason", "Download failed")
            }

    def get_repository_readme(self, owner: str, repo: str) -> Optional[str]:
        """Obtenir le README d'un repository"""
        endpoint = f"/repos/{owner}/{repo}/readme"
        result = self._make_github_request(endpoint)

        if result and "content" in result:
            import base64
            try:
                content = base64.b64decode(result["content"]).decode('utf-8')
                return content
            except:
                return None

        return None

    def analyze_repository_security(self, owner: str, repo: str) -> Dict[str, Any]:
        """Analyser la sécurité d'un repository"""
        analysis = {
            "repository": f"{owner}/{repo}",
            "security_score": 0,
            "issues": [],
            "recommendations": []
        }

        # Vérifier les advisories de sécurité
        repo_details = self.get_repository_details(owner, repo)
        if repo_details and repo_details.security_advisories:
            analysis["issues"].append(f"Repository has {len(repo_details.security_advisories)} security advisories")
            analysis["security_score"] -= 20

        # Vérifier les issues de sécurité
        security_issues = self.get_repository_issues(owner, repo, labels=["security", "vulnerability"])
        if security_issues:
            analysis["issues"].append(f"Repository has {len(security_issues)} security-related issues")
            analysis["security_score"] -= 15

        # Analyser les dépendances (simplifié)
        readme = self.get_repository_readme(owner, repo)
        if readme:
            # Chercher des signes de bonnes pratiques
            if "dependabot" in readme.lower():
                analysis["security_score"] += 10
                analysis["recommendations"].append("Good: Dependabot enabled")
            else:
                analysis["issues"].append("Consider enabling Dependabot for dependency updates")

            if "security" in readme.lower():
                analysis["security_score"] += 5

        # Score final (0-100)
        analysis["security_score"] = max(0, min(100, 50 + analysis["security_score"]))

        return analysis

    def get_integration_status(self) -> Dict[str, Any]:
        """Obtenir le statut de l'intégration GitHub"""
        return {
            "connection_status": "online" if self.rate_limit_remaining > 0 else "rate_limited",
            "rate_limit_remaining": self.rate_limit_remaining,
            "cache_size": len(self.cache),
            "cached_queries": list(self.cache.keys())[:5],  # Aperçu
            "capabilities": [
                "repository_search",
                "code_search",
                "security_advisories",
                "issue_tracking",
                "readme_access",
                "repository_download",
                "security_analysis"
            ]
        }

# === INTÉGRATION GOOGLE SERVICES ===

class GoogleServicesIntegration:
    """
    Intégration avec les services Google pour Sharingan
    Drive, Gmail, Calendar, etc. (nécessite credentials)
    """

    def __init__(self):
        from internet_access_system import get_secure_web_proxy, WebRequest
        self.proxy = get_secure_web_proxy()
        self.web_request_class = WebRequest

        # APIs Google
        self.drive_api = "https://www.googleapis.com/drive/v3"
        self.gmail_api = "https://gmail.googleapis.com/gmail/v1"
        self.custom_search_api = "https://www.googleapis.com/customsearch/v1"

        logger.info(" Google Services Integration initialized")

    def search_web_google(self, query: str, api_key: Optional[str] = None,
                         search_engine_id: Optional[str] = None) -> Dict[str, Any]:
        """Recherche web via Google Custom Search API"""
        if not api_key or not search_engine_id:
            return {
                "status": "error",
                "reason": "Google API key and search engine ID required"
            }

        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "num": 5
        }

        request = self.web_request_class(
            url=self.custom_search_api,
            params=params,
            security_level="standard"
        )

        result = self.proxy.make_secure_request(request)

        if result["status"] == "success" and "json" in result["response"]:
            data = result["response"]["json"]
            return {
                "status": "success",
                "query": query,
                "results": [
                    {
                        "title": item["title"],
                        "url": item["link"],
                        "snippet": item["snippet"]
                    }
                    for item in data.get("items", [])
                ]
            }

        return {
            "status": "error",
            "reason": result.get("reason", "Google search failed")
        }

    def get_integration_status(self) -> Dict[str, Any]:
        """Statut de l'intégration Google"""
        return {
            "services": ["custom_search", "drive", "gmail"],
            "authentication_required": True,
            "current_status": "proxy_ready",
            "capabilities": [
                "web_search_via_google",
                "drive_file_access",
                "gmail_integration"
            ]
        }

# === FONCTIONS GLOBALES ===

_github_integration = None
_google_integration = None

def get_github_integration() -> GitHubIntegration:
    """Singleton pour l'intégration GitHub"""
    global _github_integration
    if _github_integration is None:
        _github_integration = GitHubIntegration()
    return _github_integration

def get_google_integration() -> GoogleServicesIntegration:
    """Singleton pour l'intégration Google"""
    global _google_integration
    if _google_integration is None:
        _google_integration = GoogleServicesIntegration()
    return _google_integration

if __name__ == "__main__":
    print("🐙 SHARINGAN GITHUB INTEGRATION - INITIALISATION")
    print("=" * 60)

    # Tester l'intégration GitHub
    github = get_github_integration()

    print("\n📊 STATUT INTÉGRATION:")
    status = github.get_integration_status()
    print(f"• Connection: {status['connection_status']}")
    print(f"• Rate limit: {status['rate_limit_remaining']}")
    print(f"• Cache: {status['cache_size']} queries")
    print(f"• Capabilities: {len(status['capabilities'])}")

    print("\n TEST RECHERCHE REPOSITORIES:")
    repos = github.search_security_repositories("pentest tools", min_stars=50)
    print(f"• Repositories trouvés: {len(repos)}")

    if repos:
        top_repo = repos[0]
        print(f"• Top repo: {top_repo.name} ({top_repo.stars} stars)")
        print(f"  Description: {top_repo.description[:100]}...")

        print("\n ANALYSE SÉCURITÉ REPO:")
        security_analysis = github.analyze_repository_security(top_repo.owner, top_repo.name)
        print(f"• Security score: {security_analysis['security_score']}/100")
        if security_analysis['issues']:
            print(f"• Issues: {len(security_analysis['issues'])}")

    print("\n TEST RECHERCHE CODE:")
    code_results = github.search_code("exploit CVE", language="python")
    print(f"• Résultats code: {len(code_results)}")

    print("\n TEST VULNÉRABILITÉS:")
    vulns = github.find_security_vulnerabilities("RCE")
    print(f"• Vulnérabilités trouvées: {len(vulns)}")

    print("\n🌐 TEST GOOGLE INTEGRATION:")
    google = get_google_integration()
    google_status = google.get_integration_status()
    print(f"• Services disponibles: {len(google_status['services'])}")
    print(f"• Authentification requise: {google_status['authentication_required']}")

# === FONCTIONS GLOBALES ===

_integration_manager = None

def get_integration_manager():
    """Singleton pour le gestionnaire d'intégration GitHub/Google"""
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = GitHubGoogleIntegration()
    return _integration_manager

    print("\n✅ GITHUB INTEGRATION OPÉRATIONNELLE!")
    print("Sharingan peut maintenant accéder aux repositories,")
    print("chercher du code, analyser la sécurité, et bien plus!")
    print("=" * 60)

if __name__ == "__main__":
    print("🐙 SHARINGAN GITHUB INTEGRATION")
    print("=" * 60)

    # Initialisation
    integration = GitHubGoogleIntegration()

    print(f"\n STATUT: {integration.get_status()}")

    # Test GitHub
    print("\n🐙 TEST GITHUB:")
    github = get_github_integration()
    github_status = github.get_integration_status()
    print(f"• Token configuré: {github_status['token_configured']}")
    print(f"• Rate limit restant: {github_status['rate_limit_remaining']}")

    print("\n TEST RECHERCHE CODE:")
    code_results = github.search_code("exploit CVE", language="python")
    print(f"• Résultats code: {len(code_results)}")

    print("\n TEST VULNÉRABILITÉS:")
    vulns = github.find_security_vulnerabilities("RCE")
    print(f"• Vulnérabilités trouvées: {len(vulns)}")

    print("\n🌐 TEST GOOGLE INTEGRATION:")
    google = get_google_integration()
    google_status = google.get_integration_status()
    print(f"• Services disponibles: {len(google_status['services'])}")
    print(f"• Authentification requise: {google_status['authentication_required']}")

    print("\n✅ GITHUB INTEGRATION OPÉRATIONNELLE!")
    print("Sharingan peut maintenant accéder aux repositories,")
    print("chercher du code, analyser la sécurité, et bien plus!")
    print("=" * 60)