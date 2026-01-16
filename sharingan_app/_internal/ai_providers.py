#!/usr/bin/env python3
"""
AI Providers System - Hybrid routing with fallback
Combines tgpt (fast, free) + MiniMax (free API) with intelligent routing
"""

import subprocess
import json
import time
import os
import hashlib
import shutil
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.providers")

@dataclass
class ModelMetrics:
    """Performance metrics for a model"""
    model_name: str
    provider: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_tokens: int = 0
    total_time_ms: float = 0.0
    avg_response_time_ms: float = 0.0
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    error_types: Dict[str, int] = field(default_factory=dict)
    
    def record_call(self, success: bool, tokens: int, time_ms: float, error: Optional[str] = None):
        self.total_calls += 1
        self.total_time_ms += time_ms
        self.total_tokens += tokens
        if self.total_calls > 0:
            self.avg_response_time_ms = self.total_time_ms / self.total_calls
        
        if success:
            self.successful_calls += 1
            self.last_success = datetime.now().isoformat()
        else:
            self.failed_calls += 1
            self.last_failure = datetime.now().isoformat()
            if error:
                self.error_types[error] = self.error_types.get(error, 0) + 1
    
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return (self.successful_calls / self.total_calls) * 100
    
    def to_dict(self) -> Dict:
        return asdict(self)

class AIProvider:
    """Base class for AI providers"""
    
    def __init__(self, name: str, model: str, api_key: Optional[str] = None):
        self.name = name
        self.model = model
        self.api_key = api_key
        self.metrics = ModelMetrics(model_name=model, provider=name)
        self.available = False
    
    def is_available(self) -> bool:
        return self.available
    
    def chat(self, message: str, context: Optional[List[Dict]] = None) -> Dict:
        """Send chat message and get response"""
        start = time.time()
        try:
            result = self._execute_chat(message, context)
            elapsed = (time.time() - start) * 1000
            tokens = len(result.get("response", "").split()) * 4
            self.metrics.record_call(True, tokens, elapsed)
            return {
                "success": True,
                "response": result.get("response", ""),
                "model": self.model,
                "provider": self.name,
                "time_ms": elapsed
            }
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            self.metrics.record_call(False, 0, elapsed, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "model": self.model,
                "provider": self.name
            }
    
    def _execute_chat(self, message: str, context: Optional[List[Dict]] = None) -> Dict:
        raise NotImplementedError
    
    def get_metrics(self) -> Dict:
        return self.metrics.to_dict()

class TgptProvider(AIProvider):
    """tgpt - CLI wrapper for Phind/Grok API (primary, fast, free)"""
    
    def __init__(self):
        super().__init__("tgpt", "phind-grok")
        self._check_availability()
    
    def _check_availability(self):
        self.available = shutil.which("tgpt") is not None
    
    def _execute_chat(self, message: str, context: Optional[List[Dict]] = None) -> Dict:
        full_message = message
        if context:
            context_parts = []
            for msg in context[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")[:300]
                context_parts.append(f"[{role}]: {content}")
            if context_parts:
                context_str = "\n".join(reversed(context_parts))
                full_message = f"CONTEXTE PRÉCÉDENT:\n{context_str}\n\nQUESTION ACTUELLE: {message}"
        
        cmd = ["tgpt", "--model", "grok", "--quiet", full_message]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"tgpt failed: {result.stderr}")
        
        return {"response": result.stdout.strip()}

class MiniMaxProvider(AIProvider):
    """MiniMax - Free API (backup, good for coding)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("minimax", "MiniMax-m2.1-free", api_key)
        self.api_base = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        self.available = True
    
    def _execute_chat(self, message: str, context: Optional[List[Dict]] = None) -> Dict:
        import urllib.request
        import urllib.error
        
        api_key = self.api_key or os.getenv("MINIMAX_API_KEY", "")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        messages = [{"role": "user", "content": message}]
        if context:
            for msg in context[-5:]:
                messages.insert(0, {"role": msg.get("role", "user"), "content": msg.get("content", "")[:500]})
        
        payload = {
            "model": "abab6.5s-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096
        }
        
        try:
            req = urllib.request.Request(
                self.api_base,
                data=json.dumps(payload).encode(),
                headers=headers,
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
                choice = data.get("choices", [{}])[0]
                return {"response": choice.get("message", {}).get("content", "")}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            logger.warning(f"MiniMax HTTP {e.code}: {error_body[:200]}")
            raise RuntimeError(f"MiniMax API error: {error_body[:200]}")


class GrokCodeFastProvider(AIProvider):
    """Grok Code Fast 1 - Free model from OpenCode Zen (fast coding)"""
    
    def __init__(self):
        super().__init__("grok-code-fast", "grok-code-fast-1")
        self._check_availability()
    
    def _check_availability(self):
        self.available = shutil.which("tgpt") is not None
    
    def _execute_chat(self, message: str, context: Optional[List[Dict]] = None) -> Dict:
        full_message = message
        if context:
            context_parts = []
            for msg in context[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")[:300]
                context_parts.append(f"[{role}]: {content}")
            if context_parts:
                context_str = "\n".join(reversed(context_parts))
                full_message = f"CONTEXTE PRÉCÉDENT:\n{context_str}\n\nQUESTION ACTUELLE: {message}"
        
        cmd = ["tgpt", "--model", "grok-code-fast", "--quiet", full_message]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Grok Code Fast failed: {result.stderr}")
        
        return {"response": result.stdout.strip()}


class HybridProviderManager:
    """
    Hybrid routing system combining tgpt + MiniMax + Grok Code Fast
    Strategy: Option 3 (routing) + Option 4 (fallback)
    
    3 Free Models:
    - tgpt: Phind/Grok (general purpose, fast)
    - minimax: MiniMax API (coding, analysis)
    - grok-code-fast: Grok Code Fast 1 (coding specialist)
    """
    
    ROUTING_RULES = {
        "fast": ["tgpt"],                    # Quick questions → tgpt
        "coding": ["grok-code-fast", "tgpt", "minimax"],  # Code → Grok Fast first
        "analysis": ["tgpt", "minimax"],     # Analysis → tgpt + MiniMax
        "creative": ["minimax", "tgpt"],     # Creative → MiniMax
        "default": ["tgpt", "grok-code-fast", "minimax"]  # Default → all in order
    }
    
    def __init__(self):
        self.providers: Dict[str, AIProvider] = {}
        self.fallback_order = ["tgpt", "grok-code-fast", "minimax"]
        self.current_strategy = "default"
        self._initialize_providers()
        self.lock = threading.Lock()
        self.parallel_results: List[Dict] = []
    
    def _initialize_providers(self):
        """Initialize available providers"""
        # tgpt - Phind/Grok (primary, general purpose)
        tgpt = TgptProvider()
        if tgpt.is_available():
            self.providers["tgpt"] = tgpt
            logger.info("tgpt provider initialized (primary - Phind/Grok)")
        
        # Grok Code Fast 1 - Coding specialist
        grok_fast = GrokCodeFastProvider()
        if grok_fast.is_available():
            self.providers["grok-code-fast"] = grok_fast
            logger.info("Grok Code Fast 1 initialized (coding specialist)")
        
        # MiniMax - API backup (good for coding/analysis)
        minimax = MiniMaxProvider()
        if minimax.is_available():
            self.providers["minimax"] = minimax
            logger.info("MiniMax provider initialized (API backup)")
    
    def detect_query_type(self, query: str) -> str:
        """Detect query type for intelligent routing"""
        q = query.lower()
        
        # Code-related queries
        if any(x in q for x in ["code", "function", "class", "python", "javascript", 
                                 "debug", "error", "syntax", "api", "implement"]):
            return "coding"
        
        # Analysis/Research queries
        if any(x in q for x in ["analyze", "explain", "compare", "why", "how works",
                                 "difference", "advantages", "disadvantages"]):
            return "analysis"
        
        # Creative queries
        if any(x in q for x in ["write", "create", "generate", "story", " poem",
                                 "design", "creative"]):
            return "creative"
        
        # Quick questions
        if any(x in q for x in ["what is", "who is", "define", "list"]):
            return "fast"
        
        return "default"
    
    def get_providers_for_query(self, query: str) -> List[str]:
        """Get ordered list of providers for a query"""
        query_type = self.detect_query_type(query)
        return self.ROUTING_RULES.get(query_type, self.ROUTING_RULES["default"])
    
    def chat_single(self, message: str, provider: str, 
                   context: Optional[List[Dict]] = None) -> Dict:
        """Chat with a single provider"""
        if provider not in self.providers:
            return {"success": False, "error": f"Provider {provider} not available"}
        
        return self.providers[provider].chat(message, context)
    
    def chat_parallel(self, message: str, providers: List[str],
                     context: Optional[List[Dict]] = None,
                     timeout_ms: int = 30000) -> List[Dict]:
        """Execute multiple providers in parallel and return all results"""
        results = []
        start = time.time()
        
        def call_provider(p):
            return self.providers[p].chat(message, context)
        
        threads = []
        for provider in providers:
            if provider in self.providers:
                t = threading.Thread(target=lambda: results.append(call_provider(provider)))
                t.start()
                threads.append(t)
        
        for t in threads:
            t.join(timeout=timeout_ms / 1000)
        
        return results
    
    def chat_hybrid(self, message: str, 
                   context: Optional[List[Dict]] = None,
                   mode: str = "auto") -> Dict:
        """
        Hybrid chat with intelligent routing + fallback
        
        Modes:
        - "auto": Auto-detect query type and route accordingly
        - "fast": tgpt only (quickest)
        - "parallel": Both providers, return best
        - "fallback": tgpt first, fallback to minimax
        - "coding": Both for code, compare results
        """
        query_type = self.detect_query_type(message)
        providers = self.get_providers_for_query(message)
        
        logger.info(f"Query type: {query_type}, providers: {providers}")
        
        if mode == "fast":
            # tgpt only (fastest)
            result = self.chat_single(message, "tgpt", context)
            result["strategy"] = "fast"
            result["providers_used"] = ["tgpt"]
            return result
        
        elif mode == "parallel":
            # Both in parallel, return all results
            results = self.chat_parallel(message, providers, context)
            successful = [r for r in results if r.get("success")]
            
            if not successful:
                return {"success": False, "error": "All providers failed"}
            
            # Return best (fastest successful)
            best = min(successful, key=lambda x: x.get("time_ms", 99999))
            best["strategy"] = "parallel"
            best["all_results"] = results
            best["providers_used"] = providers
            return best
        
        elif mode == "coding":
            # Both for code, compare and return best quality
            results = self.chat_parallel(message, ["tgpt", "minimax"], context)
            successful = [r for r in results if r.get("success")]
            
            if not successful:
                return {"success": False, "error": "All providers failed"}
            
            # For coding, MiniMax often better - prioritize it
            minimax_result = next((r for r in successful if r.get("provider") == "minimax"), None)
            tgpt_result = next((r for r in successful if r.get("provider") == "tgpt"), None)
            
            if minimax_result:
                minimax_result["strategy"] = "coding"
                minimax_result["comparison"] = {
                    "tgpt_time": tgpt_result.get("time_ms") if tgpt_result else None,
                    "minimax_time": minimax_result.get("time_ms")
                }
                minimax_result["providers_used"] = ["tgpt", "minimax"]
                return minimax_result
            
            return successful[0]
        
        else:  # fallback (default)
            # Try tgpt first, fallback to minimax
            result = self.chat_single(message, "tgpt", context)
            
            if result.get("success"):
                result["strategy"] = "fallback_primary"
                result["providers_used"] = ["tgpt"]
                return result
            
            # Fallback to minimax
            logger.info("tgpt failed, trying minimax...")
            result = self.chat_single(message, "minimax", context)
            result["strategy"] = "fallback_backup"
            result["providers_used"] = ["tgpt", "minimax"]
            return result
    
    def chat(self, message: str, provider: Optional[str] = None,
             context: Optional[List[Dict]] = None,
             mode: str = "auto") -> Dict:
        """
        Main chat interface
        
        Args:
            message: The message to send
            provider: Specific provider (overrides auto-detection)
            context: Conversation history
            mode: auto/fast/parallel/fallback/coding
        
        Returns:
            Dict with success, response, provider, time_ms, strategy
        """
        if provider:
            # Specific provider requested
            result = self.chat_single(message, provider, context)
            result["strategy"] = "specific"
            result["providers_used"] = [provider]
            return result
        
        # Use hybrid routing
        return self.chat_hybrid(message, context, mode)
    
    def get_metrics(self) -> Dict:
        """Get metrics for all providers"""
        return {
            name: provider.get_metrics()
            for name, provider in self.providers.items()
        }
    
    def get_status(self) -> Dict:
        """Get system status"""
        return {
            "providers": {
                name: {
                    "available": p.is_available(),
                    "model": p.model,
                    "calls": p.metrics.total_calls,
                    "success_rate": p.metrics.success_rate(),
                    "avg_time_ms": p.metrics.avg_response_time_ms
                }
                for name, p in self.providers.items()
            },
            "default_strategy": self.current_strategy,
            "routing_rules": self.ROUTING_RULES
        }


def get_provider_manager() -> HybridProviderManager:
    """Get provider manager singleton"""
    return HybridProviderManager()


def ai_chat(message: str, provider: Optional[str] = None,
            context: Optional[List[Dict]] = None,
            mode: str = "auto") -> Dict:
    """Convenience function for AI chat"""
    manager = get_provider_manager()
    return manager.chat(message, provider, context, mode)


if __name__ == "__main__":
    print("=== HYBRID AI PROVIDERS TEST ===\n")
    
    manager = get_provider_manager()
    
    print("Status:")
    status = manager.get_status()
    print(json.dumps(status, indent=2))
    
    print("\n" + "="*60)
    
    test_queries = [
        ("Quick question", "fast"),
        ("Write a Python function to calculate factorial", "coding"),
        ("Explain the difference between TCP and UDP", "analysis"),
        ("Create a creative story about AI", "creative"),
    ]
    
    for query, mode in test_queries:
        print(f"\nQuery: {query[:50]}...")
        print(f"Mode: {mode}")
        
        result = manager.chat(query, mode=mode)
        
        if result.get("success"):
            print(f"  Provider: {result.get('provider')}")
            print(f"  Strategy: {result.get('strategy')}")
            print(f"  Time: {result.get('time_ms', 0):.0f}ms")
            print(f"  Response: {result.get('response', '')[:100]}...")
        else:
            print(f"  Error: {result.get('error')}")
    
    print("\n" + "="*60)
    print("Metrics:")
    metrics = manager.get_metrics()
    print(json.dumps(metrics, indent=2))
