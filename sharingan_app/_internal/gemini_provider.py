# Google Gemini API provider for Sharingan-WFK-Python
"""
Google Gemini AI API integration
Provides access to Gemini models via Google AI API
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger("gemini_provider")

@dataclass
class GeminiConfig:
    api_keys: List[str]  # Liste de clés API pour rotation
    base_url: str = "https://generativelanguage.googleapis.com"
    model: str = "gemini-flash-latest"  # Modèle gratuit disponible

class GeminiProvider:
    """
    Google Gemini provider for AI chat and generation
    Uses Google's Generative AI API with key rotation
    """

    def __init__(self, api_keys: List[str], model: Optional[str] = None):
        # Utiliser le modèle fourni ou celui par défaut
        model_to_use = model if model else "gemini-flash-latest"
        self.config = GeminiConfig(api_keys=api_keys, model=model_to_use)
        self.available_keys = []  # Clés testées et fonctionnelles
        self.current_key_index = 0
        self._test_all_keys()

    def _test_all_keys(self):
        """Test toutes les clés API et garde celles qui fonctionnent"""
        self.available_keys = []
        for i, api_key in enumerate(self.config.api_keys):
            if self._test_single_key(api_key):
                self.available_keys.append(api_key)
                print(f"✅ Clé API {i+1} validée")
            else:
                print(f"❌ Clé API {i+1} rejetée")

        self.available = len(self.available_keys) > 0
        print(f"🔑 {len(self.available_keys)}/{len(self.config.api_keys)} clés API fonctionnelles")

    def _test_single_key(self, api_key: str) -> bool:
        """Test une seule clé API"""
        try:
            response = requests.post(
                f"{self.config.base_url}/v1beta/models/{self.config.model}:generateContent?key={api_key}",
                json={"contents": [{"parts": [{"text": "test"}]}]},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False

    def _get_current_key(self) -> str:
        """Obtenir la clé API actuelle avec rotation"""
        if not self.available_keys:
            raise ValueError("Aucune clé API disponible")
        return self.available_keys[self.current_key_index]

    def _rotate_key(self):
        """Passer à la clé suivante"""
        if len(self.available_keys) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.available_keys)
            logger.info(f"Rotation vers clé API {self.current_key_index + 1}")

    def is_available(self) -> bool:
        return self.available

    def chat(self, message: str, context: Optional[List[Dict]] = None, model: Optional[str] = None) -> Dict:
        """
        Send chat message to Gemini API with key rotation
        """
        if not self.available:
            return {"error": "Gemini API not available", "status": "error"}

        max_retries = len(self.available_keys)  # Essayer toutes les clés disponibles

        for attempt in range(max_retries):
            try:
                current_key = self._get_current_key()

                # Build contents array for Gemini format
                contents = []

                # Add context if provided (convert from OpenAI format to Gemini format)
                if context:
                    for msg in context:
                        contents.append({
                            "role": msg.get("role", "user"),
                            "parts": [{"text": msg.get("content", "")}]
                        })

                # Add current message
                contents.append({
                    "role": "user",
                    "parts": [{"text": message}]
                })

                payload = {
                    "contents": contents
                }

                response = requests.post(
                    f"{self.config.base_url}/v1beta/models/{model or self.config.model}:generateContent?key={current_key}",
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()

                    # Extract response from Gemini format
                    candidates = data.get("candidates", [])
                    if candidates:
                        content = candidates[0].get("content", {})
                        parts = content.get("parts", [])
                        if parts:
                            response_text = parts[0].get("text", "")

                            return {
                                "status": "success",
                                "response": response_text,
                                "model": model or self.config.model,
                                "provider": "gemini",
                                "usage": {},
                                "key_used": self.current_key_index + 1
                            }

                    return {
                        "status": "error",
                        "error": "No response generated",
                        "provider": "gemini"
                    }

                elif response.status_code in [429, 402]:  # Rate limit ou quota
                    logger.warning(f"Clé API {self.current_key_index + 1} limitée/quota épuisé, rotation...")
                    self._rotate_key()
                    continue  # Essayer la clé suivante

                else:
                    logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                    # Pour les erreurs autres que quota, essayer quand même la clé suivante
                    self._rotate_key()
                    continue

            except Exception as e:
                logger.error(f"Gemini API request error: {e}")
                self._rotate_key()
                continue

        # Toutes les clés ont échoué
        return {
            "status": "error",
            "error": f"Toutes les {len(self.available_keys)} clés API ont échoué",
            "provider": "gemini"
        }

    def get_available_models(self) -> List[str]:
        """
        Get list of available Gemini models
        """
        return [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro"
        ]

    def get_status(self) -> Dict:
        """Get provider status and key information"""
        return {
            "available": self.available,
            "total_keys": len(self.config.api_keys),
            "working_keys": len(self.available_keys),
            "current_key": self.current_key_index + 1 if self.available_keys else 0,
            "model": self.config.model
        }

def get_gemini_provider(api_keys: List[str]) -> GeminiProvider:
    """Factory function for Gemini provider with multiple keys"""
    return GeminiProvider(api_keys=api_keys)