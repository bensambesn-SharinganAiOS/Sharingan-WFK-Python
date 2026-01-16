#!/usr/bin/env python3
"""
Ollama Provider - Local inference with Ollama models
Lightweight local model for offline/fast operations
"""

import subprocess
import json
import time
import socket
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.providers.ollama")

OLLAMA_MODELS = {
    "tinyllama": {"size": "637 MB", "context": 2048, "speed": "fast"},
    "gemma:2b": {"size": "1.7 GB", "context": 4096, "speed": "medium"},
    "gemma3:1b": {"size": "800 MB", "context": 2048, "speed": "fast"},
    "llama3.2": {"size": "2.0 GB", "context": 4096, "speed": "medium"},
    "mistral": {"size": "4.1 GB", "context": 4096, "speed": "slow"},
}

@dataclass
class OllamaMetrics:
    """Metrics for Ollama provider"""
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


class OllamaProvider:
    """
    Ollama provider for local inference
    
    Usage:
    - Offline mode (no internet/API)
    - Fast simple tasks (factual, short answers)
    - Privacy-sensitive operations
    - When API is slow/unavailable
    
    Available models via Ollama:
    - tinyllama: 637MB, fastest, 2048 context
    - gemma:2b: 1.7GB, medium speed
    - gemma3:1b: 800MB, fast
    - llama3.2: 2.0GB, medium speed
    - mistral: 4.1GB, slower but powerful
    """
    
    def __init__(self, model: str = "tinyllama"):
        self.name = "ollama"
        self.model = model
        self.model_info = OLLAMA_MODELS.get(model, {
            "size": "unknown",
            "context": 2048,
            "speed": "medium"
        })
        self.metrics = OllamaMetrics(model_name=model)
        self._check_availability()
    
    def _check_availability(self):
        """Check if Ollama server is running"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.available = result.returncode == 0
            
            if self.available:
                self.available = self.model in result.stdout
                if not self.available:
                    logger.warning(f"Model {self.model} not found in Ollama")
                    logger.info(f"Available models: {result.stdout.strip()}")
            
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.available = False
            logger.warning(f"Ollama not available: {e}")
    
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
                    prompt_parts.append(f"<|im_start|>user\n{content}<|im_end|>")
                elif role == "assistant":
                    prompt_parts.append(f"<|im_start|>assistant\n{content}<|im_end|>")
                else:
                    prompt_parts.append(f"{content}")
        
        prompt_parts.append(f"<|im_start|>user\n{message}<|im_end|>")
        prompt_parts.append("<|im_start|>assistant\n")
        
        return "\n".join(prompt_parts)
    
    def _execute_chat(self, message: str, context: Optional[List[Dict]] = None) -> Dict:
        """Execute chat via Ollama CLI"""
        try:
            prompt = message
            if context:
                prompt = self._build_prompt(message, context)
            
            start = time.time()
            
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            elapsed = (time.time() - start) * 1000
            
            if result.returncode == 0:
                content = result.stdout.strip()
                tokens = len(content.split()) * 4
                self.metrics.record_call(True, tokens, elapsed)
                
                return {
                    "success": True,
                    "response": content,
                    "model": self.model,
                    "provider": "ollama",
                    "time_ms": elapsed
                }
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                logger.error(f"Ollama error: {error_msg}")
                self.metrics.record_call(False, 0, 0)
                
                return {
                    "success": False,
                    "error": error_msg,
                    "model": self.model,
                    "provider": "ollama"
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Ollama timeout")
            self.metrics.record_call(False, 0, 0)
            return {
                "success": False,
                "error": "Timeout",
                "model": self.model,
                "provider": "ollama"
            }
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            self.metrics.record_call(False, 0, 0)
            return {
                "success": False,
                "error": str(e),
                "model": self.model,
                "provider": "ollama"
            }
    
    def chat(self, message: str, context: Optional[List[Dict]] = None) -> Dict:
        """Send chat message and get response"""
        if not self.available:
            return {
                "success": False,
                "error": "Ollama server not available",
                "provider": "ollama"
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
            "total_tokens": self.metrics.total_tokens,
            "model_info": self.model_info
        }
    
    def list_models(self) -> Dict[str, Dict]:
        """List all available Ollama models"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                models = {}
                for line in result.stdout.strip().split('\n'):
                    if line and ':' in line:
                        parts = line.split(':')
                        name = parts[0].strip()
                        size = parts[1].strip() if len(parts) > 1 else "unknown"
                        models[name] = {
                            "size": size,
                            "available": True
                        }
                return models
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
        
        return {}


def is_connected() -> bool:
    """Check if internet is available"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def should_use_ollama(query: str, available_providers: Dict[str, Any],
                     offline_mode: bool = False) -> bool:
    """
    Determine if Ollama should be used
    
    Conditions for Ollama:
    1. Offline mode explicitly enabled
    2. No API providers available
    3. Fast/simple query AND (offline OR speed priority)
    4. Privacy-sensitive keywords
    """
    q = query.lower().strip()
    
    if offline_mode:
        return True
    
    api_providers = ["tgpt", "grok-code-fast", "minimax", "openrouter"]
    has_api = any(p in available_providers for p in api_providers)
    if not has_api:
        return True
    
    privacy_keywords = ["password", "secret", "api key", "token", "private"]
    if any(k in q for k in privacy_keywords):
        return True
    
    if not is_connected():
        simple_patterns = ["what is", "define", "list", "who is", "explain"]
        if any(p in q for p in simple_patterns):
            return True
    
    return False


def get_ollama_provider(model: str = "tinyllama") -> Optional[OllamaProvider]:
    """Get Ollama provider if available"""
    provider = OllamaProvider(model=model)
    if provider.is_available():
        return provider
    return None


if __name__ == "__main__":
    print("=== OLLAMA PROVIDER TEST ===\n")
    
    provider = OllamaProvider()
    
    print(f"Available: {provider.is_available()}")
    print(f"Model: {provider.model}")
    print(f"Model Info: {provider.model_info}")
    print(f"\nAvailable models:")
    
    models = provider.list_models()
    for name, info in models.items():
        print(f"  - {name}: {info['size']}")
    
    if provider.is_available():
        print("\n" + "-" * 40)
        
        test_queries = [
            ("What is Python?", "simple"),
            ("Write a hello world function", "coding"),
        ]
        
        for query, qtype in test_queries:
            print(f"\nQuery ({qtype}): {query}")
            result = provider.chat(query)
            
            if result.get("success"):
                print(f"  Time: {result.get('time_ms', 0):.0f}ms")
                print(f"  Response: {result.get('response', '')[:150]}...")
            else:
                print(f"  Error: {result.get('error')}")
        
        print("\n" + "-" * 40)
        print("Metrics:", json.dumps(provider.get_metrics(), indent=2))
    else:
        print("\n[!] Install/pull a model first:")
        print("    ollama pull tinyllama")
        print("    ollama pull gemma:2b")
