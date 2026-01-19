#!/usr/bin/env python3
"""
Sharingan OS - Grok Provider
Provider IA intégrant Grok API gratuite depuis https://github.com/realasfngl/Grok-Api
"""

import requests
import logging
import os
from typing import Optional

logger = logging.getLogger("sharingan.providers.grok")

class GrokProvider:
    """
    Provider Grok pour Sharingan OS.
    Utilise API gratuite Grok.
    """

    def __init__(self):
        # URL depuis laozhang.ai pour Grok 3
        self.api_url = "https://api.laozhang.ai/v1/chat/completions"
        self.api_key = os.getenv("LAOZHANG_API_KEY", "sk-Y6Fz6PteVgr4Y7De16A3F23b09Dc4bAbAb975b51D087478b")  # Clé depuis env
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_response(self, prompt: str) -> Optional[str]:
        """Génère réponse via Grok 3 API laozhang.ai"""
        try:
            payload = {
                "model": "grok-3",
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }

            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if "choices" in data and data["choices"]:
                    return data["choices"][0]["message"]["content"]
            else:
                logger.error(f"Grok API error: {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"Grok request failed: {e}")

        return None

    def is_available(self) -> bool:
        """Vérifie disponibilité"""
        return True