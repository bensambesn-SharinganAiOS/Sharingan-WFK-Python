#!/usr/bin/env python3
"""
Gemini AI Provider for Sharingan OS
Google Gemini API integration with key rotation
"""

import os
import sys
import json
import requests
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GeminiProvider:
    """
    Provider for Google Gemini AI with automatic key rotation
    """

    def __init__(self, api_keys: Optional[List[str]] = None):
        self.api_keys = api_keys or [
            "AIzaSyAQ5Jq6doHAt3untxi3zD95n_TBoZft7wQ",  # adamabenousmanesambe@gmail.com
            "AIzaSyA2vUDIH8m80nxYCOq15qOE5L61mJABPkU",  # bensambe.sn@gmail.com
            "AIzaSyAtMBJMWn2saI2Yo7ljPyJOMEq0eaVFY8E",  # bensambe.org@gmail.com
            "AIzaSyBLJmwuYDFay2kbRx3xwWz1i3pSXR11LWg"   # madamesambe@gmail.com - clé fournie
        ]
        self.current_key_index = 0
        self.model = "gemini-flash-latest"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.last_error = None

    def _get_next_key(self) -> str:
        """Get next API key with rotation"""
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key

    def _call_gemini(self, prompt: str, api_key: str) -> Optional[str]:
        """Make API call to Gemini"""
        try:
            url = f"{self.base_url}/{self.model}:generateContent?key={api_key}"

            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                }
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and result["candidates"]:
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    self.last_error = "No content in Gemini response"
                    return None
            else:
                self.last_error = f"Gemini API error: {response.status_code} - {response.text}"
                return None

        except Exception as e:
            self.last_error = f"Gemini request failed: {str(e)}"
            return None

    def generate_response(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Generate AI response with automatic key rotation on failures
        """
        for attempt in range(max_retries):
            api_key = self._get_next_key()
            logger.info(f"Gemini attempt {attempt + 1}/{max_retries} with key index {self.current_key_index - 1}")

            response = self._call_gemini(prompt, api_key)
            if response:
                return response

            logger.warning(f"Gemini attempt {attempt + 1} failed: {self.last_error}")

        logger.error(f"All Gemini attempts failed. Last error: {self.last_error}")
        return None

    def is_available(self) -> bool:
        """Check if Gemini provider is available"""
        # Quick test call
        test_prompt = "Hello"
        response = self.generate_response(test_prompt, max_retries=1)
        return response is not None

    def get_status(self) -> Dict[str, Any]:
        """Get provider status"""
        return {
            "provider": "gemini",
            "model": self.model,
            "keys_available": len(self.api_keys),
            "last_error": self.last_error,
            "available": self.is_available()
        }


if __name__ == "__main__":
    # Test the provider
    provider = GeminiProvider()

    print("🔍 Testing Gemini Provider...")
    status = provider.get_status()
    print(f"Status: {json.dumps(status, indent=2)}")

    if status["available"]:
        print("\n🤖 Testing response generation...")
        response = provider.generate_response("What is the capital of France?")
        print(f"Response: {response}")
    else:
        print("❌ Gemini provider not available")