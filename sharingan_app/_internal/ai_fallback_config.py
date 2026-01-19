# AI Fallback Providers Configuration
"""
Configuration for AI fallback providers
MiniMax, Grok, GLM as fallback to tgpt/ollama
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

class AIFallbackConfig:
    """
    Configuration manager for AI fallback providers
    """

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_file = self.base_dir / "ai_fallback_config.json"
        self.providers = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load fallback provider configuration"""
        default_config = {
            "gemini": {
                "enabled": True,  # Activé avec les clés fournies
                "api_keys": [
                    "AIzaSyAQ5Jq6doHAt3untxi3zD95n_TBoZft7wQ",  # adamabenousmanesambe@gmail.com
                    "AIzaSyA2vUDIH8m80nxYCOq15qOE5L61mJABPkU",  # bensambe.sn@gmail.com
                    "AIzaSyAtMBJMWn2saI2Yo7ljPyJOMEq0eaVFY8E",  # bensambe.org@gmail.com
                    "AIzaSyBLJmwuYDFay2kbRx3xwWz1i3pSXR11LWg"   # madamesambe@gmail.com
                ],
                "model": "gemini-flash-latest",  # Modèle gratuit disponible
                "priority": 1
            },
            "fallback_chain": ["opencode", "gemini", "ollama"],
            "timeout_per_provider": 15,
            "max_retries": 2
        }

        if self.config_file.exists():
            try:
                import json
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for key, value in loaded.items():
                        if key in default_config:
                            default_config[key].update(value)
            except Exception:
                pass

        return default_config

    def enable_provider(self, provider: str, api_key: str) -> bool:
        """Enable a fallback provider with API key"""
        if provider in self.providers:
            self.providers[provider]["enabled"] = True
            self.providers[provider]["api_key"] = api_key
            self._save_config()
            return True
        return False

    def disable_provider(self, provider: str) -> bool:
        """Disable a fallback provider"""
        if provider in self.providers:
            self.providers[provider]["enabled"] = False
            self.providers[provider]["api_key"] = ""
            self._save_config()
            return True
        return False

    def get_enabled_providers(self) -> Dict[str, Any]:
        """Get all enabled providers with their config"""
        return {k: v for k, v in self.providers.items()
                if isinstance(v, dict) and v.get("enabled", False)}

    def get_fallback_chain(self) -> list:
        """Get the configured fallback chain"""
        return self.providers.get("fallback_chain", ["tgpt", "ollama"])

    def _save_config(self):
        """Save configuration to file"""
        try:
            import json
            with open(self.config_file, 'w') as f:
                json.dump(self.providers, f, indent=2)
        except Exception:
            pass

# Instance globale
ai_fallback_config = AIFallbackConfig()

def setup_ai_fallbacks():
    """
    Setup function to configure AI fallbacks
    Call this to enable providers with real API keys
    """
    print("=== AI Fallback Configuration ===")
    print("Providers disponibles: MiniMax, Grok, GLM")
    print("Utilisez ai_fallback_config.enable_provider('provider', 'api_key')")
    print("Exemples:")
    print("  ai_fallback_config.enable_provider('minimax', 'your_minimax_key')")
    print("  ai_fallback_config.enable_provider('grok', 'your_grok_key')")
    print("  ai_fallback_config.enable_provider('glm', 'your_glm_key')")

if __name__ == "__main__":
    setup_ai_fallbacks()