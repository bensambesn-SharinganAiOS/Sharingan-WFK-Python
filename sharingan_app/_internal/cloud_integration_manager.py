#!/usr/bin/env python3
"""
SHARINGAN CLOUD INTEGRATION MANAGER
Version simplifiée avec support GCP et GitHub
"""

import sys
import os
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cloud_integration")

class CloudProvider(Enum):
    """Fournisseurs cloud supportés"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    GITHUB = "github"

class ResourceType(Enum):
    """Types de ressources cloud"""
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORKING = "networking"
    AI_ML = "ai_ml"
    SECURITY = "security"
    CODE = "code"

@dataclass
class CloudResource:
    """Représentation d'une ressource cloud"""
    provider: CloudProvider
    resource_type: ResourceType
    resource_id: str
    name: str
    region: str
    status: str
    created_at: float
    cost_per_hour: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CloudOperation:
    """Opération cloud"""
    operation_id: str
    provider: CloudProvider
    action: str
    resource_type: ResourceType
    parameters: Dict[str, Any]
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=lambda: time.time())
    completed_at: Optional[float] = None

class GitHubIntegration:
    """
    Intégration GitHub comme fournisseur cloud de code
    """

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.api_base = "https://api.github.com"

        # Headers pour les requêtes API
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Sharingan-OS/1.0'
        }
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'

        self.configured = bool(self.token)

    def is_configured(self) -> bool:
        """Vérifier si l'intégration est configurée"""
        return self.configured

    def list_repositories(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lister les repositories"""
        if not self.configured:
            return []

        try:
            if username:
                url = f"{self.api_base}/users/{username}/repos"
            else:
                url = f"{self.api_base}/user/repos"

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            repos = []
            for repo in response.json():
                repos.append({
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'private': repo['private'],
                    'language': repo.get('language'),
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'updated_at': repo['updated_at'],
                    'url': repo['html_url']
                })

            return repos

        except Exception as e:
            logger.error(f"Error listing GitHub repositories: {e}")
            return []

    def search_code(self, query: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Rechercher du code sur GitHub"""
        if not self.configured:
            return []

        try:
            url = f"{self.api_base}/search/code"
            params = {'q': query}

            if language:
                params['q'] += f" language:{language}"

            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()

            results = []
            for item in response.json().get('items', []):
                results.append({
                    'name': item['name'],
                    'path': item['path'],
                    'repository': item['repository']['full_name'],
                    'url': item['html_url'],
                    'score': item['score']
                })

            return results

        except Exception as e:
            logger.error(f"Error searching GitHub code: {e}")
            return []

class GCPIntegration:
    """
    Intégration Google Cloud Platform
    """

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.configured = bool(self.project_id)

        # Token d'accès (si gcloud est disponible)
        self.gcloud_available = self._check_gcloud()

    def _check_gcloud(self) -> bool:
        """Vérifier si gcloud est disponible"""
        try:
            import subprocess
            result = subprocess.run(
                ["gcloud", "--version"],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def is_configured(self) -> bool:
        """Vérifier si l'intégration est configurée"""
        return self.configured and self.gcloud_available

    def list_compute_instances(self) -> List[Dict[str, Any]]:
        """Lister les instances Compute Engine"""
        if not self.is_configured():
            return []

        try:
            import subprocess
            # Utiliser gcloud pour lister les instances
            result = subprocess.run([
                "gcloud", "compute", "instances", "list",
                f"--project={self.project_id}",
                "--format=json"
            ], capture_output=True, text=True, timeout=15)

            if result.returncode == 0:
                instances_data = json.loads(result.stdout)
                instances = []

                for instance in instances_data:
                    instances.append({
                        'name': instance['name'],
                        'machine_type': instance['machineType'].split('/')[-1],
                        'status': instance['status'],
                        'zone': instance['zone'].split('/')[-1],
                        'external_ip': None,
                        'internal_ip': None
                    })

                    # Récupérer les IPs
                    for interface in instance.get('networkInterfaces', []):
                        for config in interface.get('accessConfigs', []):
                            if config.get('type') == 'ONE_TO_ONE_NAT':
                                instances[-1]['external_ip'] = config.get('natIP')
                        instances[-1]['internal_ip'] = interface.get('networkIP', '')

                return instances

        except Exception as e:
            logger.error(f"Error listing GCP instances: {e}")

        return []

class CloudIntegrationManager:
    """
    Gestionnaire d'intégration cloud simplifié
    """

    def __init__(self):
        # Intégrations cloud
        self.github = GitHubIntegration()
        self.gcp = GCPIntegration()

        # Opérations en cours
        self.operations: Dict[str, CloudOperation] = {}
        self.operation_counter = 0

        # Statistiques
        self.stats = {
            'operations_total': 0,
            'operations_successful': 0,
            'resources_active': 0,
            'costs_incurred': 0.0
        }

        logger.info(" Cloud Integration Manager initialized")

    def execute_cloud_operation(self, provider: CloudProvider, action: str,
                              resource_type: ResourceType, **kwargs) -> CloudOperation:
        """
        Exécuter une opération cloud
        """
        operation_id = f"cloud_op_{int(time.time())}_{self.operation_counter}"
        self.operation_counter += 1

        operation = CloudOperation(
            operation_id=operation_id,
            provider=provider,
            action=action,
            resource_type=resource_type,
            parameters=kwargs
        )

        self.operations[operation_id] = operation

        try:
            if provider == CloudProvider.GITHUB:
                result = self._execute_github_operation(operation)
            elif provider == CloudProvider.GCP:
                result = self._execute_gcp_operation(operation)
            else:
                result = None
                operation.error = "Unsupported cloud provider"

            operation.result = result
            operation.status = "completed" if result is not None else "failed"
            operation.completed_at = time.time()

            self.stats['operations_total'] += 1
            if operation.status == "completed":
                self.stats['operations_successful'] += 1

        except Exception as e:
            operation.error = str(e)
            operation.status = "failed"
            operation.completed_at = time.time()
            logger.error(f"Cloud operation failed: {e}")

        return operation

    def _execute_github_operation(self, operation: CloudOperation) -> Any:
        """Exécuter une opération GitHub"""
        if operation.action == "list_repos":
            return self.github.list_repositories(**operation.parameters)
        elif operation.action == "search_code":
            return self.github.search_code(**operation.parameters)
        else:
            raise ValueError(f"Unsupported GitHub action: {operation.action}")

    def _execute_gcp_operation(self, operation: CloudOperation) -> Any:
        """Exécuter une opération GCP"""
        if operation.action == "list_instances":
            return self.gcp.list_compute_instances()
        else:
            raise ValueError(f"Unsupported GCP action: {operation.action}")

    def get_operation_status(self, operation_id: str) -> Optional[CloudOperation]:
        """Obtenir le statut d'une opération"""
        return self.operations.get(operation_id)

    def get_cloud_resources(self, provider: Optional[CloudProvider] = None) -> List[CloudResource]:
        """Obtenir les ressources cloud actives"""
        resources = []

        # Ressources GitHub (repositories)
        if (provider is None or provider == CloudProvider.GITHUB) and self.github.is_configured():
            try:
                repos = self.github.list_repositories()
                for repo in repos[:5]:  # Limiter à 5 pour éviter surcharge
                    resources.append(CloudResource(
                        provider=CloudProvider.GITHUB,
                        resource_type=ResourceType.CODE,
                        resource_id=repo['full_name'],
                        name=repo['name'],
                        region="github.com",
                        status="active",
                        created_at=time.time(),
                        cost_per_hour=0.0,  # GitHub repositories sont gratuits
                        metadata={'language': repo.get('language'), 'stars': repo.get('stars', 0)}
                    ))
            except Exception as e:
                logger.warning(f"Error getting GitHub resources: {e}")

        # Ressources GCP
        if (provider is None or provider == CloudProvider.GCP) and self.gcp.is_configured():
            try:
                instances = self.gcp.list_compute_instances()
                for instance in instances:
                    if instance['status'] == 'RUNNING':
                        resources.append(CloudResource(
                            provider=CloudProvider.GCP,
                            resource_type=ResourceType.COMPUTE,
                            resource_id=instance['name'],
                            name=instance['name'],
                            region=instance['zone'],
                            status="running",
                            created_at=time.time(),
                            cost_per_hour=0.05,  # Estimation pour e2-micro
                            metadata={'machine_type': instance['machine_type']}
                        ))
            except Exception as e:
                logger.warning(f"Error getting GCP resources: {e}")

        return resources

    def get_integration_status(self) -> Dict[str, Any]:
        """Obtenir le statut des intégrations cloud"""
        return {
            "github_configured": self.github.is_configured(),
            "gcp_configured": self.gcp.is_configured(),
            "operations_total": self.stats['operations_total'],
            "operations_successful": self.stats['operations_successful'],
            "success_rate": (self.stats['operations_successful'] / self.stats['operations_total'] * 100) if self.stats['operations_total'] > 0 else 0,
            "resources_active": len(self.get_cloud_resources()),
            "costs_incurred": self.stats['costs_incurred']
        }

# === FONCTIONS GLOBALES ===

_cloud_manager = None

def get_cloud_manager() -> CloudIntegrationManager:
    """Singleton pour le gestionnaire cloud"""
    global _cloud_manager
    if _cloud_manager is None:
        _cloud_manager = CloudIntegrationManager()
    return _cloud_manager

def execute_cloud_operation(provider: str, action: str, resource_type: str, **kwargs) -> CloudOperation:
    """
    Fonction principale pour exécuter des opérations cloud
    """
    manager = get_cloud_manager()

    provider_enum = CloudProvider(provider.lower())
    resource_enum = ResourceType(resource_type.lower())

    return manager.execute_cloud_operation(provider_enum, action, resource_enum, **kwargs)

if __name__ == "__main__":
    print(" SHARINGAN CLOUD INTEGRATION MANAGER")
    print("=" * 60)

    manager = get_cloud_manager()

    # Statut des intégrations
    status = manager.get_integration_status()
    print("\n☁️ STATUT DES INTÉGRATIONS CLOUD:")
    print(f"• GitHub configuré: {'✅' if status['github_configured'] else '❌'}")
    print(f"• GCP configuré: {'✅' if status['gcp_configured'] else '❌'}")
    print(f"• Opérations réussies: {status['operations_successful']}/{status['operations_total']}")
    print(f"• Taux de réussite: {status['success_rate']:.1f}%")
    print(f"• Ressources actives: {status['resources_active']}")
    print(f"• Coûts encourus: ${status['costs_incurred']:.2f}")

    # Test des opérations de base
    print("\n🧪 TESTS D'OPÉRATIONS CLOUD:")
    if status['github_configured']:
        print("• Test GitHub - Liste des repos...")
        operation = execute_cloud_operation("github", "list_repos", "code")
        time.sleep(1)
        if operation.operation_id in manager.operations:
            op_status = manager.operations[operation.operation_id]
            print(f"  Statut: {op_status.status}")
            if op_status.result:
                print(f"  Repositories trouvés: {len(op_status.result)}")

        print("• Test GitHub - Recherche de code Python...")
        operation = execute_cloud_operation("github", "search_code", "code",
                                          query="print('hello world')", language="python")
        time.sleep(1)
        if operation.operation_id in manager.operations:
            op_status = manager.operations[operation.operation_id]
            print(f"  Statut: {op_status.status}")
            if op_status.result:
                print(f"  Résultats trouvés: {len(op_status.result)}")

    if status['gcp_configured']:
        print("• Test GCP - Liste des instances...")
        operation = execute_cloud_operation("gcp", "list_instances", "compute")
        time.sleep(1)
        if operation.operation_id in manager.operations:
            op_status = manager.operations[operation.operation_id]
            print(f"  Statut: {op_status.status}")
            if op_status.result:
                print(f"  Instances trouvées: {len(op_status.result)}")

    print("\n📊 STATUT FINAL:")
    final_status = manager.get_integration_status()
    print(f"• Ressources actives: {final_status['resources_active']}")
    print(f"• Taux de réussite: {final_status['success_rate']:.1f}%")
    print("=" * 60)