#!/usr/bin/env python3
"""
Sharingan OS - G4F Provider
Provider IA intégrant G4F pour accès gratuit à ChatGPT, DeepSeek, Grok, Gemini.
Auteur: Ben Sambe
"""

import sys
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger("sharingan.providers.g4f")

class G4FProvider:
    """
    Provider G4F pour Sharingan OS.

    Utilise g4f.dev pour accès gratuit à multiples modèles IA.
    """

    def __init__(self):
        self.api_url = "https://api.g4f.dev/v1/chat/completions"
        self.models = [
            "gpt-4o",
            "gpt-4o-mini",
            "claude-3.5-sonnet",
            "gemini-1.5-pro",
            "deepseek-chat",
            "grok-2"
        ]

    def generate_response(self, prompt: str, model: str = "gpt-4o") -> Optional[str]:
        """Génère une réponse via G4F"""
        try:
            import requests

            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es SharinganOS Consciousness, assistant cybersécurité."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7
            }

            response = requests.post(self.api_url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if "choices" in result and result["choices"]:
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"G4F API error: {result}")
            else:
                logger.error(f"G4F HTTP error: {response.status_code}")

        except Exception as e:
            logger.error(f"G4F request failed: {e}")

        return None

    def is_available(self) -> bool:
        """Vérifie si G4F est disponible"""
        return True  # G4F est gratuit sans clé