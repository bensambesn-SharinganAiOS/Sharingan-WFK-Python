#!/usr/bin/env python3
"""
Unit tests for the permissions system.
Tests ToolClassifier, PermissionValidator, and SafeExecutor classes.
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "sharingan_app" / "_internal"))

import pytest

from security.permissions import (
    DangerLevel,
    ExecutionMode,
    ToolClassifier,
    PermissionValidator,
    SafeExecutor,
    PermissionRequest,
    PermissionResult,
    validate_execution,
    safe_execute,
)


class TestToolClassifier:
    """Tests for ToolClassifier class"""

    def test_classify_safe_tools(self):
        """Test classification of safe tools"""
        safe_tools = ["ls", "cat", "head", "tail", "grep", "find", "pwd", "echo", "date"]
        for tool in safe_tools:
            result = ToolClassifier.classify(tool)
            assert result == DangerLevel.SAFE, f"Tool {tool} should be classified as SAFE"

    def test_classify_moderate_tools(self):
        """Test classification of moderate tools"""
        moderate_tools = ["mkdir", "touch", "cp", "mv", "rm", "chmod", "git", "curl"]
        for tool in moderate_tools:
            result = ToolClassifier.classify(tool)
            assert result == DangerLevel.MODERATE, f"Tool {tool} should be classified as MODERATE"

    def test_classify_high_tools(self):
        """Test classification of high-risk tools"""
        high_tools = ["nmap", "netdiscover", "masscan", "gobuster", "ffuf", "nc", "netcat"]
        for tool in high_tools:
            result = ToolClassifier.classify(tool)
            assert result == DangerLevel.HIGH, f"Tool {tool} should be classified as HIGH"

    def test_classify_critical_tools(self):
        """Test classification of critical tools"""
        critical_tools = ["sqlmap", "metasploit", "msfconsole", "hydra", "john", "hashcat", "aircrack-ng"]
        for tool in critical_tools:
            result = ToolClassifier.classify(tool)
            assert result == DangerLevel.CRITICAL, f"Tool {tool} should be classified as CRITICAL"

    def test_classify_unknown_tool(self):
        """Test classification of unknown tool returns SAFE"""
        result = ToolClassifier.classify("unknown_tool_xyz")
        assert result == DangerLevel.SAFE

    def test_classify_case_insensitive(self):
        """Test classification is case insensitive"""
        assert ToolClassifier.classify("NMAP") == DangerLevel.HIGH
        assert ToolClassifier.classify("SQLMAP") == DangerLevel.CRITICAL
        assert ToolClassifier.classify("Ls") == DangerLevel.SAFE

    def test_requires_validation(self):
        """Test requires_validation method"""
        assert ToolClassifier.requires_validation(DangerLevel.SAFE) is False
        assert ToolClassifier.requires_validation(DangerLevel.MODERATE) is False
        assert ToolClassifier.requires_validation(DangerLevel.HIGH) is True
        assert ToolClassifier.requires_validation(DangerLevel.CRITICAL) is True


class TestPermissionRequest:
    """Tests for PermissionRequest dataclass"""

    def test_permission_request_creation(self):
        """Test PermissionRequest can be created with required fields"""
        request = PermissionRequest(
            tool="nmap",
            command=["nmap", "-sn", "localhost"],
            danger_level=DangerLevel.HIGH,
            context={"mission_id": "test_123"}
        )
        assert request.tool == "nmap"
        assert request.command == ["nmap", "-sn", "localhost"]
        assert request.danger_level == DangerLevel.HIGH
        assert request.context == {"mission_id": "test_123"}
        assert request.timestamp is not None

    def test_permission_request_to_dict(self):
        """Test PermissionRequest serialization"""
        request = PermissionRequest(
            tool="ls",
            command=["ls", "-la"],
            danger_level=DangerLevel.SAFE,
            context={}
        )
        result = request.to_dict()
        assert result["tool"] == "ls"
        assert result["danger_level"] == "safe"
        assert isinstance(result["timestamp"], str)


class TestPermissionValidator:
    """Tests for PermissionValidator class"""

    def test_validator_safe_tool_auto_approved(self):
        """Test that SAFE tools are auto-approved"""
        validator = PermissionValidator(mode=ExecutionMode.PLAN)
        result = validator.validate(
            tool="ls",
            command=["ls", "-la"],
            context={}
        )
        assert result.granted is True
        assert "Outil de niveau sûr" in result.reason

    def test_validator_moderate_tool_approved(self):
        """Test that MODERATE tools are approved"""
        validator = PermissionValidator(mode=ExecutionMode.PLAN)
        result = validator.validate(
            tool="git",
            command=["git", "status"],
            context={}
        )
        assert result.granted is True
        assert "Outil de niveau modéré" in result.reason

    def test_validator_high_tool_requires_approval_plan_mode(self):
        """Test that HIGH tools require approval in PLAN mode"""
        validator = PermissionValidator(mode=ExecutionMode.PLAN)
        result = validator.validate(
            tool="nmap",
            command=["nmap", "-sn", "localhost"],
            context={}
        )
        assert result.granted is False
        assert "Nécessite validation" in result.reason

    def test_validator_critical_tool_requires_approval_plan_mode(self):
        """Test that CRITICAL tools require approval in PLAN mode"""
        validator = PermissionValidator(mode=ExecutionMode.PLAN)
        result = validator.validate(
            tool="sqlmap",
            command=["sqlmap", "-u", "http://example.com"],
            context={}
        )
        assert result.granted is False
        assert "Nécessite validation" in result.reason

    def test_validator_pre_approved_tool(self):
        """Test that pre-approved tools are granted"""
        validator = PermissionValidator(mode=ExecutionMode.PLAN)
        validator.pre_approved_tools["nmap"] = True
        result = validator.validate(
            tool="nmap",
            command=["nmap", "-sn", "localhost"],
            context={}
        )
        assert result.granted is True
        assert "Pré-approuvé" in result.reason

    def test_validator_pre_approved_via_env(self):
        """Test pre-approval loading from environment"""
        with patch.dict("os.environ", {"SHARINGAN_PRE_APPROVED_TOOLS": "nmap,mkdir"}):
            validator = PermissionValidator(mode=ExecutionMode.PLAN)
            assert "nmap" in validator.pre_approved_tools
            assert "mkdir" in validator.pre_approved_tools

    def test_audit_log_populated(self):
        """Test that audit log is populated on validation"""
        validator = PermissionValidator(mode=ExecutionMode.PLAN)
        validator.validate(tool="ls", command=["ls"], context={})
        assert len(validator.audit_log) == 1
        assert validator.audit_log[0]["request"]["tool"] == "ls"

    def test_approval_cache_for_high_tools(self):
        """Test that HIGH/CRITICAL tool approvals are cached"""
        validator = PermissionValidator(mode=ExecutionMode.PLAN)
        validator.validate(tool="nmap", command=["nmap", "localhost"], context={})
        assert len(validator.approval_cache) == 1
        cache_key = list(validator.approval_cache.keys())[0]
        assert "nmap" in cache_key

    def test_get_audit_log(self):
        """Test get_audit_log returns audit entries"""
        validator = PermissionValidator(mode=ExecutionMode.PLAN)
        validator.validate(tool="cat", command=["cat", "file.txt"], context={})
        log = validator.get_audit_log()
        assert len(log) == 1

    def test_export_audit_log(self, tmp_path):
        """Test audit log can be exported to file"""
        validator = PermissionValidator(mode=ExecutionMode.PLAN)
        validator.validate(tool="ls", command=["ls"], context={})

        export_path = tmp_path / "audit_log.json"
        validator.export_audit_log(str(export_path))

        assert export_path.exists()
        import json
        with open(export_path) as f:
            data = json.load(f)
        assert len(data) == 1


class TestSafeExecutor:
    """Tests for SafeExecutor class"""

    def test_execute_safe_tool(self):
        """Test execution of safe tool"""
        executor = SafeExecutor(mode=ExecutionMode.PLAN)
        success, output, permission = executor.execute(
            command=["echo", "test"],
            context={}
        )
        assert success is True
        assert "test" in (output.stdout if hasattr(output, 'stdout') else str(output))
        assert permission.granted is True

    def test_execute_with_audit_trail(self):
        """Test that execution creates audit trail"""
        executor = SafeExecutor(mode=ExecutionMode.PLAN)
        executor.execute(command=["echo", "test"], context={})

        audit_log = executor.validator.get_audit_log()
        assert len(audit_log) == 1

    def test_execute_timeout(self):
        """Test execution timeout handling"""
        executor = SafeExecutor(mode=ExecutionMode.PLAN)
        success, output, permission = executor.execute(
            command=["sleep", "10"],
            context={},
            timeout=1
        )
        assert success is False
        assert output == "Timeout"

    def test_execute_nonexistent_command(self):
        """Test execution of nonexistent command"""
        executor = SafeExecutor(mode=ExecutionMode.PLAN)
        success, output, permission = executor.execute(
            command=["nonexistent_command_xyz_123"],
            context={}
        )
        assert success is False


class TestHelperFunctions:
    """Tests for module-level helper functions"""

    def test_validate_execution_plan_mode(self):
        """Test validate_execution helper in PLAN mode"""
        result = validate_execution(
            tool="ls",
            command=["ls", "-la"],
            context={},
            mode="plan"
        )
        assert result.granted is True
        assert result.validation_mode == ExecutionMode.PLAN

    def test_validate_execution_realtime_mode(self):
        """Test validate_execution helper in REALTIME mode"""
        with patch("builtins.input", return_value="n"):
            result = validate_execution(
                tool="nmap",
                command=["nmap", "localhost"],
                context={},
                mode="realtime"
            )
            assert result.granted is False

    def test_safe_execute_helper(self):
        """Test safe_execution helper function"""
        success, output, permission = safe_execute(
            command=["echo", "hello"],
            context={},
            mode="plan"
        )
        assert success is True
        assert permission.granted is True


class TestPermissionResult:
    """Tests for PermissionResult dataclass"""

    def test_permission_result_to_dict(self):
        """Test PermissionResult serialization"""
        result = PermissionResult(
            granted=True,
            reason="Test approved",
            validation_mode=ExecutionMode.PLAN,
            approved_by="test_user"
        )
        data = result.to_dict()
        assert data["granted"] is True
        assert data["reason"] == "Test approved"
        assert data["validation_mode"] == "plan"
        assert data["approved_by"] == "test_user"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
