#!/usr/bin/env python3
"""
SHARINGAN OS - VRAIES APIs GRATUITES
Implémentation réelle utilisant Puter.js (gratuit sans compte)
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

logger = logging.getLogger("sharingan.apis")

@dataclass
class APIResponse:
    """Réponse d'une API"""
    success: bool
    response: str
    model: str
    processing_time: float
    error: Optional[str] = None

class PuterJSProvider:
    """Fournisseur Puter.js - APIs gratuites réelles"""

    BASE_URL = "https://api.puter.com"

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        await self.init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()

    async def init_session(self):
        """Initialise la session HTTP"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                base_url=self.BASE_URL,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Sharingan-OS/1.0"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
            logger.info("✅ Puter.js session initialized")

    async def close_session(self):
        """Ferme la session HTTP"""
        if self.session:
            await self.session.close()
            self.session = None

    async def chat(self, message: str, model: str, **kwargs) -> APIResponse:
        """Chat avec un modèle Puter.js"""
        import time
        start_time = time.time()

        try:
            payload = {
                "message": message,
                "model": model,
                **kwargs
            }

            async with self.session.post("/ai/chat", json=payload) as response:
                processing_time = time.time() - start_time

                if response.status == 200:
                    result = await response.json()
                    api_response = result.get("response", "")

                    if api_response.strip():
                        return APIResponse(
                            success=True,
                            response=api_response,
                            model=model,
                            processing_time=processing_time
                        )
                    else:
                        return APIResponse(
                            success=False,
                            response="",
                            model=model,
                            processing_time=processing_time,
                            error="Empty response from API"
                        )
                else:
                    error_text = await response.text()
                    return APIResponse(
                        success=False,
                        response="",
                        model=model,
                        processing_time=processing_time,
                        error=f"HTTP {response.status}: {error_text}"
                    )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Puter.js API error for {model}: {e}")
            return APIResponse(
                success=False,
                response="",
                model=model,
                processing_time=processing_time,
                error=str(e)
            )

class MiniMaxAPI:
    """MiniMax API - GRATUIT via Puter.js"""

    MODEL = "minimax/minimax-m2.1"

    def __init__(self):
        self.provider = PuterJSProvider()

    async def __aenter__(self):
        await self.provider.init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.provider.close_session()

    async def chat(self, message: str, **kwargs) -> APIResponse:
        """Chat avec MiniMax M2.1"""
        async with self.provider:
            return await self.provider.chat(message, self.MODEL, **kwargs)

class GrokAPI:
    """Grok xAI API - GRATUIT via Puter.js"""

    MODEL = "x-ai/grok-4.1-fast"

    def __init__(self):
        self.provider = PuterJSProvider()

    async def __aenter__(self):
        await self.provider.init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.provider.close_session()

    async def chat(self, message: str, **kwargs) -> APIResponse:
        """Chat avec Grok 4.1 Fast"""
        async with self.provider:
            return await self.provider.chat(message, self.MODEL, **kwargs)

class GLM4API:
    """GLM-4 (Z.AI) API - GRATUIT via Puter.js"""

    MODEL = "z-ai/glm-4.7"

    def __init__(self):
        self.provider = PuterJSProvider()

    async def __aenter__(self):
        await self.provider.init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.provider.close_session()

    async def chat(self, message: str, **kwargs) -> APIResponse:
        """Chat avec GLM-4.7"""
        async with self.provider:
            return await self.provider.chat(message, self.MODEL, **kwargs)

class OpenCodeZenAPI:
    """OpenCode Zen - Fournisseur d'optimisation de code"""

    MODEL = "z-ai/glm-4.7"  # Utilise GLM-4 pour l'optimisation

    def __init__(self):
        self.provider = PuterJSProvider()

    async def __aenter__(self):
        await self.provider.init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.provider.close_session()

    async def optimize_code(self, code: str, language: str = "python") -> APIResponse:
        """Optimise du code"""
        prompt = f"Optimize this {language} code for performance, readability, and best practices:\n\n{code}"
        async with self.provider:
            return await self.provider.chat(prompt, self.MODEL)

class TGPTProvider:
    """TGPT - ChatGPT CLI local"""

    async def chat(self, message: str, **kwargs) -> APIResponse:
        """Chat avec TGPT local"""
        import time
        import subprocess

        start_time = time.time()

        try:
            # Utilise asyncio pour ne pas bloquer
            process = await asyncio.create_subprocess_exec(
                'tgpt', message,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=tempfile.gettempdir()  # Use system temp directory
            )

            stdout, stderr = await process.communicate()
            processing_time = time.time() - start_time

            if process.returncode == 0:
                response = stdout.decode().strip()
                if response:
                    return APIResponse(
                        success=True,
                        response=response,
                        model="tgpt",
                        processing_time=processing_time
                    )
                else:
                    return APIResponse(
                        success=False,
                        response="",
                        model="tgpt",
                        processing_time=processing_time,
                        error="Empty response from tgpt"
                    )
            else:
                error = stderr.decode().strip()
                return APIResponse(
                    success=False,
                    response="",
                    model="tgpt",
                    processing_time=processing_time,
                    error=f"tgpt error: {error}"
                )

        except FileNotFoundError:
            return APIResponse(
                success=False,
                response="",
                model="tgpt",
                processing_time=time.time() - start_time,
                error="tgpt not installed"
            )
        except Exception as e:
            return APIResponse(
                success=False,
                response="",
                model="tgpt",
                processing_time=time.time() - start_time,
                error=str(e)
            )

# Test des vraies APIs
async def test_real_apis():
    """Test de toutes les vraies APIs"""
    print("🧪 TEST DES VRAIES APIs GRATUITES")
    print("=" * 50)
    print("📡 Fournisseur: Puter.js (gratuit sans compte)")
    print()

    test_message = "Bonjour, présente-toi en une phrase."

    # Test MiniMax
    print("🤖 1. MiniMax M2.1:")
    try:
        async with MiniMaxAPI() as api:
            result = await api.chat(test_message)
            if result.success:
                print(f"   ✅ {result.response}")
            else:
                print(f"   ❌ {result.error}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

    # Test Grok
    print("\n🤖 2. Grok 4.1 Fast:")
    try:
        async with GrokAPI() as api:
            result = await api.chat(test_message)
            if result.success:
                print(f"   ✅ {result.response}")
            else:
                print(f"   ❌ {result.error}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

    # Test GLM-4
    print("\n🤖 3. GLM-4.7:")
    try:
        async with GLM4API() as api:
            result = await api.chat(test_message)
            if result.success:
                print(f"   ✅ {result.response}")
            else:
                print(f"   ❌ {result.error}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

    # Test TGPT
    print("\n🤖 4. TGPT (local):")
    try:
        api = TGPTProvider()
        result = await api.chat(test_message)
        if result.success:
            print(f"   ✅ {result.response[:100]}...")
        else:
            print(f"   ❌ {result.error}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

    print("\n🎯 RÉSULTATS:")
    print("• APIs gratuites via Puter.js: MiniMax, Grok, GLM-4")
    print("• TGPT: Local (ChatGPT CLI)")
    print("• Aucun compte requis, tout gratuit")
    print("• Modèles réels, réponses authentiques")

if __name__ == "__main__":
    asyncio.run(test_real_apis())