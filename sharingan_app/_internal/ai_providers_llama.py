#!/usr/bin/env python3
"""
Llama.cpp Provider - Local inference with Gemma 3 1B
Lightweight local model for offline/fast operations
"""

import subprocess
import json
import time
import os
import socket
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.providers.llama")

@dataclass
class LlamaMetrics:
    """Metrics for llama.cpp provider"""
    model_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_tokens: int = 0
    total_time_ms: float = 0.0
    avg_response_time_ms: float = 0.0
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    
    def record_call(self, success: bool, tokens: int, time_ms: float):
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
    
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return (self.successful_calls / self.total_calls) * 100


class LlamaCppProvider:
    """
    Local llama.cpp provider with Gemma 3 1B
    
    Usage:
    - Offline mode (no internet/API)
    - Fast simple tasks (factual, short answers)
    - Privacy-sensitive operations
    - When API is slow/unavailable
    
    Requirements:
    - llama.cpp installed: https://github.com/ggerganov/llama.cpp
    - Model: Gemma 3 1B (gguf format)
    - Server: llama-server -m gemma3-1b-it.gguf -c 2048 -port 8080
    """
    
    def __init__(self, 
                 model: str = "gemma3-1b-it.gguf",
                 api_base: str = "http://localhost:8080",
                 context_size: int = 2048,
                 temperature: float = 0.7,
                 max_tokens: int = 512):
        self.name = "llama.cpp"
        self.model = model
        self.api_base = api_base
        self.context_size = context_size
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.metrics = LlamaMetrics(model_name=model)
        self._check_availability()
    
    def _check_availability(self):
        """Check if llama.cpp server is running"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.api_base}/health", method="GET")
            with urllib.request.urlopen(req, timeout=2) as response:
                self.available = response.status == 200
        except Exception:
            self.available = False
            logger.warning(f"llama.cpp server not available at {self.api_base}")
    
    def is_available(self) -> bool:
        return self.available
    
    def _build_prompt(self, message: str, context: Optional[List[Dict]] = None) -> str:
        """Build prompt from message + context"""
        prompt_parts = []
        
        if context:
            for msg in context[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")[:500]
                if role == "user":
                    prompt_parts.append(f"<start_of_turn>user\n{content}<end_of_turn>")
                elif role == "assistant":
                    prompt_parts.append(f"<start_of_turn>model\n{content}<end_of_turn>")
                else:
                    prompt_parts.append(f"{content}")
        
        prompt_parts.append(f"<start_of_turn>user\n{message}<end_of_turn>")
        prompt_parts.append("<start_of_turn>model\n")
        
        return "\n".join(prompt_parts)
    
    def _execute_chat(self, message: str, context: Optional[List[Dict]] = None) -> Dict:
        """Execute chat via llama.cpp server"""
        import urllib.request
        import urllib.error
        
        prompt = self._build_prompt(message, context)
        
        payload = {
            "prompt": prompt,
            "n_predict": self.max_tokens,
            "temperature": self.temperature,
            "top_k": 40,
            "top_p": 0.95,
            "stop": ["<end_of_turn>", "<start_of_turn>"]
        }
        
        try:
            req = urllib.request.Request(
                f"{self.api_base}/completion",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            start = time.time()
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode())
                elapsed = (time.time() - start) * 1000
                
                content = data.get("content", "")
                tokens = len(content.split()) * 4
                self.metrics.record_call(True, tokens, elapsed)
                
                return {
                    "success": True,
                    "response": content.strip(),
                    "model": self.model,
                    "provider": "llama.cpp",
                    "time_ms": elapsed
                }
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            logger.error(f"llama.cpp HTTP {e.code}: {error_body[:200]}")
            self.metrics.record_call(False, 0, 0)
            return {
                "success": False,
                "error": f"llama.cpp error: {error_body[:200]}",
                "model": self.model,
                "provider": "llama.cpp"
            }
        except Exception as e:
            logger.error(f"llama.cpp error: {e}")
            self.metrics.record_call(False, 0, 0)
            return {
                "success": False,
                "error": str(e),
                "model": self.model,
                "provider": "llama.cpp"
            }
    
    def chat(self, message: str, context: Optional[List[Dict]] = None) -> Dict:
        """Send chat message and get response"""
        if not self.available:
            return {
                "success": False,
                "error": "llama.cpp server not available",
                "provider": "llama.cpp"
            }
        return self._execute_chat(message, context)
    
    def get_metrics(self) -> Dict:
        return {
            "model_name": self.model,
            "total_calls": self.metrics.total_calls,
            "successful_calls": self.metrics.successful_calls,
            "failed_calls": self.metrics.failed_calls,
            "success_rate": self.metrics.success_rate(),
            "avg_time_ms": self.metrics.avg_response_time_ms,
            "total_tokens": self.metrics.total_tokens
        }


def is_connected() -> bool:
    """Check if internet is available"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def should_use_local_model(query: str, available_providers: Dict[str, Any], 
                          offline_mode: bool = False) -> bool:
    """
    Determine if local llama.cpp should be used
    
    Conditions for local model:
    1. Offline mode explicitly enabled
    2. No API providers available
    3. Fast/simple query AND (offline OR speed priority)
    4. Privacy-sensitive keywords
    """
    q = query.lower().strip()
    
    # Explicit offline mode
    if offline_mode:
        return True
    
    # No API providers, fallback to local
    api_providers = ["tgpt", "grok-code-fast", "minimax", "openrouter"]
    has_api = any(p in available_providers for p in api_providers)
    if not has_api:
        return True
    
    # Privacy-sensitive queries
    privacy_keywords = ["password", "secret", "api key", "token", "private"]
    if any(k in q for k in privacy_keywords):
        return True
    
    # Simple/fast queries when offline
    if not is_connected():
        simple_patterns = ["what is", "define", "list", "who is", "explain"]
        if any(p in q for p in simple_patterns):
            return True
    
    return False


# Convenience function
def get_llama_provider() -> Optional[LlamaCppProvider]:
    """Get llama.cpp provider if available"""
    provider = LlamaCppProvider()
    if provider.is_available():
        return provider
    return None


if __name__ == "__main__":
    print("=== LLAMA.CPP PROVIDER TEST ===\n")
    
    provider = LlamaCppProvider()
    
    print(f"Available: {provider.is_available()}")
    print(f"API Base: {provider.api_base}")
    print(f"Model: {provider.model}")
    
    if provider.is_available():
        print("\n" + "-"*40)
        
        test_queries = [
            ("What is Python?", "simple"),
            ("Write a hello world function", "coding"),
            ("Explain TCP vs UDP", "analysis"),
        ]
        
        for query, qtype in test_queries:
            print(f"\nQuery ({qtype}): {query[:50]}...")
            result = provider.chat(query)
            
            if result.get("success"):
                print(f"  Time: {result.get('time_ms', 0):.0f}ms")
                print(f"  Response: {result.get('response', '')[:150]}...")
            else:
                print(f"  Error: {result.get('error')}")
        
        print("\n" + "-"*40)
        print("Metrics:", json.dumps(provider.get_metrics(), indent=2))
    else:
        print("\n[!] Start llama.cpp server first:")
        print("    llama-server -m gemma3-1b-it.gguf -c 2048 -port 8080")
