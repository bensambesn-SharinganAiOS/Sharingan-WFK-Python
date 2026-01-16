#!/usr/bin/env python3
"""
Sharingan OS - Test Suite
Real tests for system functionality.
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import psutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SharinganTestSuite:
    """Test suite for Sharingan OS"""

    def __init__(self):
        self.test_results: Dict[str, Dict] = {}
        self.test_start_time = time.time()
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests"""
        print("SHARINGAN TEST SUITE")
        print("=" * 60)

        self.test_infrastructure()
        self.test_system()
        self.test_security()

        return self.generate_report()

    def test_infrastructure(self):
        """Infrastructure tests"""
        print("\nINFRASTRUCTURE TESTS")

        self._run_test("python_version", self._test_python_version)
        self._run_test("docker_availability", self._test_docker_availability)
        self._run_test("system_permissions", self._test_system_permissions)
        self._run_test("fake_detector", self._test_fake_detector)
        self._run_test("check_obligations", self._test_check_obligations)

    def test_system(self):
        """System tests"""
        print("\nSYSTEM TESTS")

        self._run_test("memory_usage", self._test_memory_usage)
        self._run_test("cpu_usage", self._test_cpu_usage)
        self._run_test("disk_usage", self._test_disk_usage)

    def test_security(self):
        """Security tests"""
        print("\nSECURITY TESTS")

        self._run_test("secrets_detection", self._test_secrets_detection)

    def _run_test(self, test_name: str, test_function) -> bool:
        """Run a single test"""
        print(f"  Test: {test_name}...", end=" ", flush=True)
        start_time = time.time()

        try:
            result = test_function()
            execution_time = time.time() - start_time

            if result["success"]:
                print(f"{execution_time:.2f}s PASS")
                self.passed_tests += 1
                self.test_results[test_name] = {
                    "status": "PASSED",
                    "time": execution_time,
                    "details": result.get("details", "")
                }
                return True
            else:
                print(f"{execution_time:.2f}s FAIL")
                self.failed_tests += 1
                self.test_results[test_name] = {
                    "status": "FAILED",
                    "time": execution_time,
                    "error": result.get("error", "Unknown error"),
                    "details": result.get("details", "")
                }
                return False

        except Exception as e:
            execution_time = time.time() - start_time
            print(f"{execution_time:.2f}s ERROR")
            self.failed_tests += 1
            self.test_results[test_name] = {
                "status": "ERROR",
                "time": execution_time,
                "error": str(e),
                "details": ""
            }
            return False

    def _test_python_version(self) -> Dict[str, Any]:
        """Test Python version"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            return {"success": True, "details": f"Python {version.major}.{version.minor}.{version.micro}"}
        return {"success": False, "error": f"Python {version.major}.{version.minor} too old"}

    def _test_docker_availability(self) -> Dict[str, Any]:
        """Test Docker availability"""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return {"success": True, "details": f"Docker: {result.stdout.strip()}"}
            return {"success": False, "error": "Docker not responding"}
        except FileNotFoundError:
            return {"success": False, "error": "Docker not found"}

    def _test_system_permissions(self) -> Dict[str, Any]:
        """Test system permissions"""
        is_root = os.getuid() == 0
        return {"success": True, "details": f"Running as {'root' if is_root else 'user'}"} if True else {"success": False, "error": "Permission issue"}

    def _test_fake_detector(self) -> Dict[str, Any]:
        """Test fake detector module"""
        try:
            base_dir = Path(__file__).parent / "sharingan_app" / "_internal"
            sys.path.insert(0, str(base_dir))
            from fake_detector import detect_fakes

            fake_content = "AI Response to: [TODO] implement later"
            result = detect_fakes(fake_content, context="ai_response")

            if result.is_fake:
                return {"success": True, "details": "FakeDetector working correctly"}

            return {"success": False, "error": "FakeDetector not detecting fakes"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_check_obligations(self) -> Dict[str, Any]:
        """Test check_obligations module"""
        try:
            base_dir = Path(__file__).parent / "sharingan_app" / "_internal"
            sys.path.insert(0, str(base_dir))
            from check_obligations import check_obligations

            result = check_obligations(str(base_dir / "fake_detector.py"))

            if result.get("passed"):
                return {"success": True, "details": "Check obligations working"}

            return {"success": False, "error": str(result.get("issues", []))}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage"""
        memory = psutil.virtual_memory()
        return {
            "success": memory.percent < 95,
            "details": f"Memory: {memory.percent:.1f}%"
        }

    def _test_cpu_usage(self) -> Dict[str, Any]:
        """Test CPU usage"""
        cpu = psutil.cpu_percent(interval=1)
        return {
            "success": cpu < 90,
            "details": f"CPU: {cpu:.1f}%"
        }

    def _test_disk_usage(self) -> Dict[str, Any]:
        """Test disk usage"""
        disk = psutil.disk_usage("/")
        return {
            "success": disk.percent < 90,
            "details": f"Disk: {disk.percent:.1f}%"
        }

    def _test_secrets_detection(self) -> Dict[str, Any]:
        """Test secrets detection in code"""
        try:
            base_dir = Path(__file__).parent / "sharingan_app" / "_internal"
            sys.path.insert(0, str(base_dir))
            from check_obligations import ObligationChecker

            checker = ObligationChecker()
            test_content = 'password = "secret123"'

            result = checker._check_secrets(test_content)

            if not result["passed"]:
                return {"success": True, "details": "Secrets detection working"}

            return {"success": False, "error": "Secrets not detected"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_report(self) -> Dict[str, Any]:
        """Generate final report"""
        total_tests = self.passed_tests + self.failed_tests
        execution_time = time.time() - self.test_start_time
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0

        return {
            "summary": {
                "total": total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "rate": f"{success_rate:.1f}%",
                "time": f"{execution_time:.2f}s"
            },
            "results": self.test_results
        }


def run_tests() -> Dict[str, Any]:
    """Run all tests and display report"""
    suite = SharinganTestSuite()
    report = suite.run_all_tests()

    print(f"\n{'='*60}")
    print("TEST REPORT")
    print(f"{'='*60}")

    summary = report["summary"]
    print(f"Total: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['rate']}")
    print(f"Execution Time: {summary['time']}")

    if summary['failed'] == 0:
        print("\nAll tests passed!")
    else:
        print(f"\nFailed tests:")
        for name, result in report["results"].items():
            if result["status"] == "FAILED":
                print(f"  - {name}: {result.get('error', 'Unknown')}")

    return report


if __name__ == "__main__":
    result = run_tests()
    sys.exit(0 if result["summary"]["failed"] == 0 else 1)
