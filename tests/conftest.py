#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Sharingan OS tests.
"""

import sys
from pathlib import Path
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "evolution: mark test as evolution test")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        if "permissions" in item.name.lower():
            item.add_marker(pytest.mark.permissions)
        if "evolution" in item.name.lower():
            item.add_marker(pytest.mark.evolution)
