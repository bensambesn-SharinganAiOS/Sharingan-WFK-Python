#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Sharingan OS tests.
"""

import sys
from pathlib import Path
import pytest


def pytest_configure(config):
    """Configure pytest with custom markers and settings"""
    sys.path.insert(0, str(Path(__file__).parent.parent / "sharingan_app" / "_internal"))


@pytest.fixture(scope="session")
def project_root():
    """Provide project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def sharingan_internal_path(project_root):
    """Provide path to _internal directory"""
    return project_root / "sharingan_app" / "_internal"


@pytest.fixture
def mock_permission_validator():
    """Create a mock permission validator for testing"""
    class MockPermissionResult:
        granted = True
        reason = "Mock approved"
        validation_mode = type('ExecutionMode', (), {'PLAN': 'plan', 'REALTIME': 'realtime'})()
        conditions = []
        warning = None
        
        def to_dict(self):
            return {
                "granted": self.granted,
                "reason": self.reason,
                "validation_mode": self.validation_mode.PLAN,
                "conditions": self.conditions,
                "warning": self.warning
            }
    
    class MockValidator:
        def validate(self, tool, command, context, user_id=None, mission_id=None):
            return MockPermissionResult()
    
    return MockValidator()


@pytest.fixture
def sample_patch_json():
    """Provide a sample valid patch JSON"""
    return {
        "patches": [
            {
                "file": "test_file.py",
                "current": "# old code",
                "proposed": "# new code",
                "reason": "Test patch"
            }
        ]
    }


@pytest.fixture
def sample_dangerous_patch_json():
    """Provide a sample dangerous patch JSON"""
    return {
        "patches": [
            {
                "file": "test_file.py",
                "current": "",
                "proposed": "rm -rf /",
                "reason": "Dangerous test"
            }
        ]
    }


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        if "permissions" in item.name.lower():
            item.add_marker(pytest.mark.permissions)
        if "evolution" in item.name.lower():
            item.add_marker(pytest.mark.evolution)
