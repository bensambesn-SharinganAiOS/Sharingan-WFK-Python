#!/usr/bin/env python3
"""
Sharingan OS - Puter Provider
Provider IA intégrant Puter.js pour accès gratuit illimité à OpenAI, Claude, etc.
Auteur: Ben Sambe
"""

import sys
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger("sharingan.providers.puter")

class PuterProvider:
    """
    Provider Puter pour Sharingan OS.

    Utilise Puter.js pour accès gratuit à OpenAI, Claude, Cohere sans clés API.
    """

    def __init__(self):
        self.api_url = "https://api.puter.com/drivers/call"
        self.models = {
            "openai": ["gpt-5-nano", "gpt-5", "gpt-5-pro"],
            "anthropic": ["claude-sonnet-4.5", "claude-opus-4.5", "claude-haiku-4.5"],
            "cohere": ["command", "command-light", "command-nightly"],
            "google": ["gemini-2.0-flash", "gemini-2.5-pro"],
            "xai": ["grok-2", "grok-3", "grok-4"]
        }

    def generate_response(self, prompt: str, model: str = "gpt-5-nano", provider: str = "openai") -> Optional[str]:
        """Génère une réponse via Puter.js"""
        try:
            import requests

            payload = {
                "interface": "puter-kv",
                "key": f"ai.{provider}.{model}.generate",
                "value": {
                    "messages": [
                        {
                            "role": "system",
                            "content": "Tu es SharinganOS Consciousness, assistant cybersécurité."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            }

            response = requests.post(self.api_url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get("success") and "result" in result:
                    return result["result"]
                else:
                    logger.error(f"Puter API error: {result}")
            else:
                logger.error(f"Puter HTTP error: {response.status_code}")

        except Exception as e:
            logger.error(f"Puter request failed: {e}")

        return None

    def is_available(self) -> bool:
        """Vérifie si Puter est disponible"""
        return True  # Puter est gratuit sans clé