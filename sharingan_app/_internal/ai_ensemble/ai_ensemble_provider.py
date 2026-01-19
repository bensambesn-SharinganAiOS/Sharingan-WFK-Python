#!/usr/bin/env python3
"""
SHARINGAN OS - AI ENSEMBLE PROVIDER
Intelligent routing between multiple AI providers with fallback
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time

logger = logging.getLogger("sharingan.ai_ensemble")

@dataclass
class EnsembleResponse:
    """Response from AI Ensemble"""
    success: bool
    response: str
    provider_used: str
    model: str
    processing_time: float
    providers_tried: List[str]
    error: Optional[str] = None

class AIEnsembleProvider:
    """
    AI Ensemble - Intelligent routing between providers
    Uses RobustAIProvider for automatic fallback
    """

    def __init__(self):
        self.robust_provider = None
        self._load_robust_provider()

    def _load_robust_provider(self):
        """Load the robust AI provider"""
        try:
            # Import relatif depuis le répertoire parent
            import importlib.util
            import os
            robust_path = os.path.join(os.path.dirname(__file__), '..', 'ai_robust_provider.py')
            spec = importlib.util.spec_from_file_location("ai_robust_provider", robust_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.robust_provider = module.RobustAIProvider()
                logger.info("✅ AI Ensemble loaded with RobustAIProvider")
            else:
                raise ImportError("Cannot load module spec")
        except Exception as e:
            logger.error(f"❌ Cannot load RobustAIProvider: {e}")
            self.robust_provider = None

    def is_available(self) -> bool:
        """Check if ensemble is available"""
        return self.robust_provider is not None

    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> EnsembleResponse:
        """Chat with intelligent provider routing"""
        if not self.is_available():
            return EnsembleResponse(
                success=False,
                response="AI Ensemble not available",
                provider_used="none",
                model="unknown",
                processing_time=0.0,
                providers_tried=[],
                error="RobustAIProvider not loaded"
            )

        start_time = time.time()

        try:
            # Use robust provider with auto fallback
            response = await self.robust_provider.chat(message, provider='auto')

            processing_time = time.time() - start_time

            if response.success:
                return EnsembleResponse(
                    success=True,
                    response=response.response,
                    provider_used=response.provider,
                    model=response.model,
                    processing_time=processing_time,
                    providers_tried=[response.provider],
                    error=None
                )
            else:
                return EnsembleResponse(
                    success=False,
                    response="All AI providers failed",
                    provider_used="none",
                    model="unknown",
                    processing_time=processing_time,
                    providers_tried=self.robust_provider.fallback_order,
                    error=response.error
                )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"AI Ensemble error: {e}")
            return EnsembleResponse(
                success=False,
                response="AI Ensemble internal error",
                provider_used="none",
                model="unknown",
                processing_time=processing_time,
                providers_tried=[],
                error=str(e)
            )

    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers in ensemble"""
        if not self.is_available():
            return {"status": "unavailable", "error": "RobustAIProvider not loaded"}

        return {
            "status": "available",
            "fallback_order": self.robust_provider.fallback_order,
            "providers": {
                "tgpt": "Available (Sky provider - GPT-4.1-mini)",
                "ollama": "Available (Local models)"
            }
        }