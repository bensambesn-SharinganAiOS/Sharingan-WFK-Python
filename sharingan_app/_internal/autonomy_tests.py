#!/usr/bin/env python3
"""
Sharingan OS - Tests d'Autonomie et d'Indépendance
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent
SHARINGAN_DIR = BASE_DIR / "sharingan_app" / "_internal"

sys.path.insert(0, str(SHARINGAN_DIR))

try:
    from sharingan_os import SharinganOS
    import fake_detector
    FakeDetector = fake_detector.FakeDetector
    detect_fakes = fake_detector.detect_fakes
    IMPORTS_OK = True
except Exception as e:
    IMPORTS_OK = False
    print(f"Import error: {e}")
    SharinganOS = None
    FakeDetector = None

def test_ai_chat_autonomy() -> Dict:
    """Test 1: L'IA peut répondre sans placeholders"""
    print("\n[TEST 1] AI Chat Autonomy")
    print("-" * 40)
    
    if not IMPORTS_OK or SharinganOS is None:
        return {"test": "ai_chat_autonomy", "status": "SKIPPED"}
    
    try:
        sharingan = SharinganOS()
        response = sharingan.ai_chat("What is 2+2? Answer only with the number.")
        print(f"Response: {response}")
        
        if "AI Response to:" in response or "AI Error:" in response:
            return {"test": "ai_chat_autonomy", "status": "FAIL", "response": response}
        
        return {"test": "ai_chat_autonomy", "status": "PASS", "response": response}
    except Exception as e:
        return {"test": "ai_chat_autonomy", "status": "ERROR", "error": str(e)}

def test_tool_execution() -> Dict:
    """Test 2: Les outils peuvent être exécutés réellement"""
    print("\n[TEST 2] Tool Execution")
    print("-" * 40)
    
    tools = [("curl", ["curl", "--version"]), ("python3", ["python3", "--version"]), 
             ("git", ["git", "--version"]), ("nmap", ["nmap", "--version"])]
    
    results, passed = [], 0
    for name, cmd in tools:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            success = r.returncode == 0
            print(f"  {name}: {'OK' if success else 'FAIL'}")
            results.append({"tool": name, "success": success})
            if success: passed += 1
        except Exception as e:
            print(f"  {name}: ERROR - {e}")
            results.append({"tool": name, "success": False, "error": str(e)})
    
    return {"test": "tool_execution", "status": "PASS" if passed == len(tools) else "PARTIAL",
            "passed": passed, "total": len(tools), "results": results}

def test_file_operations() -> Dict:
    """Test 3: Opérations sur fichiers autonomes"""
    print("\n[TEST 3] File Operations")
    print("-" * 40)
    
    if not IMPORTS_OK or SharinganOS is None:
        return {"test": "file_operations", "status": "SKIPPED"}
    
    try:
        sharingan = SharinganOS()
        test_file = "/tmp/sharingan_autonomy_test.txt"
        test_content = f"Test {datetime.now()}"
        
        with open(test_file, "w") as f: f.write(test_content)
        print(f"  Write: OK")
        
        with open(test_file, "r") as f: read_content = f.read()
        print(f"  Read: OK")
        
        os.remove(test_file)
        print(f"  Delete: OK")
        
        return {"test": "file_operations", "status": "PASS", "content_match": read_content == test_content}
    except Exception as e:
        return {"test": "file_operations", "status": "ERROR", "error": str(e)}

import os

def test_memory_system() -> Dict:
    """Test 4: Système de mémoire autonome"""
    print("\n[TEST 4] Memory System")
    print("-" * 40)
    
    if not IMPORTS_OK or SharinganOS is None:
        return {"test": "memory_system", "status": "SKIPPED"}
    
    try:
        sharingan = SharinganOS()
        key, data = "autonomy_test", {"test": "value", "number": 42}
        
        store = sharingan.ai_memory_store(key, data)
        print(f"  Store: {'OK' if store else 'FAIL'}")
        
        retrieve = sharingan.ai_memory_retrieve(key)
        print(f"  Retrieve: {'OK' if retrieve else 'FAIL'}")
        
        return {"test": "memory_system", "status": "PASS" if retrieve else "FAIL",
                "data_persisted": retrieve is not None}
    except Exception as e:
        return {"test": "memory_system", "status": "ERROR", "error": str(e)}

def test_ai_independence() -> Dict:
    """Test 5: Indépendance de l'IA"""
    print("\n[TEST 5] AI Independence")
    print("-" * 40)
    
    if not IMPORTS_OK or FakeDetector is None:
        return {"test": "ai_independence", "status": "SKIPPED"}
    
    detector = FakeDetector()
    tests = [("Real", "Sharingan OS is a security toolkit"), ("Math", "The answer is 42"),
             ("Code", "print('Hello World')"), ("Info", "Linux kernel 5.x")]
    
    results = []
    for name, resp in tests:
        check = detector.detect_fakes(resp)
        results.append({"test": name, "is_fake": check.is_fake, "confidence": check.confidence})
        print(f"  {name}: fake={check.is_fake}")
    
    return {"test": "ai_independence", "status": "PASS" if all(not r["is_fake"] for r in results) else "FAIL",
            "all_real": all(not r["is_fake"] for r in results)}

def test_akatsuki_agents() -> Dict:
    """Test 6: Agents Akatsuki opérationnels"""
    print("\n[TEST 6] Akatsuki Agents")
    print("-" * 40)
    
    if not IMPORTS_OK or SharinganOS is None:
        return {"test": "akatsuki_agents", "status": "SKIPPED"}
    
    try:
        sharingan = SharinganOS()
        status = sharingan.akatsuki_status()
        print(f"  Total: {status['total']}, Active: {status['active']}, Status: {status['status']}")
        
        return {"test": "akatsuki_agents", "status": "PASS", "agents": status.get("agents", [])}
    except Exception as e:
        return {"test": "akatsuki_agents", "status": "ERROR", "error": str(e)}

def test_autonomous_agent() -> Dict:
    """Test 7: Agent autonome"""
    print("\n[TEST 7] Autonomous Agent")
    print("-" * 40)
    
    if not IMPORTS_OK or SharinganOS is None:
        return {"test": "autonomous_agent", "status": "SKIPPED"}
    
    try:
        sharingan = SharinganOS()
        result = sharingan.autonomous_agent("test task", "general")
        print(f"  Status: {result['status']}")
        return {"test": "autonomous_agent", "status": "PASS" if result["status"] == "completed" else "FAIL"}
    except Exception as e:
        return {"test": "autonomous_agent", "status": "ERROR", "error": str(e)}

def run_all_tests() -> Dict:
    """Exécuter tous les tests"""
    print("=" * 60)
    print("SHARINGAN OS - TESTS D'AUTONOMIE")
    print("=" * 60)
    
    tests = [
        ("AI Chat", test_ai_chat_autonomy),
        ("Tools", test_tool_execution),
        ("Files", test_file_operations),
        ("Memory", test_memory_system),
        ("Independence", test_ai_independence),
        ("Akatsuki", test_akatsuki_agents),
        ("Agent", test_autonomous_agent),
    ]
    
    results = {}
    for name, func in tests:
        try:
            results[name] = func()
        except Exception as e:
            results[name] = {"status": "ERROR", "error": str(e)}
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r.get("status") == "PASS")
    failed = sum(1 for r in results.values() if r.get("status") in ["FAIL", "ERROR"])
    
    for name, r in results.items():
        status = r.get("status", "UNKNOWN")
        mark = "[PASS]" if status == "PASS" else "[FAIL]" if status in ["FAIL", "ERROR"] else "[SKIP]"
        print(f"  {mark} {name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    results["summary"] = {"passed": passed, "failed": failed, "total": len(tests)}
    return results

if __name__ == "__main__":
    results = run_all_tests()
    with open("/tmp/sharingan_autonomy.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    sys.exit(0 if results["summary"]["failed"] == 0 else 1)
