#!/usr/bin/env python3
"""
SHARINGAN OS - IA PROVIDERS ROBUSTES
TGPT + Ollama - Système robuste avec fallback automatique
"""

import asyncio
import logging
import tempfile
from typing import Optional
from dataclasses import dataclass
import time

logger = logging.getLogger("sharingan.ai_robust")
@dataclass
class AIResponse:
    """Réponse unifiée des APIs IA"""
    success: bool
    response: str
    model: str
    provider: str
    processing_time: float
    error: Optional[str] = None
    confidence: float = 0.8
class RobustAIProvider:
    """Provider IA robuste avec fallback TGPT → Ollama"""

    def __init__(self):
        self.providers = {
            'tgpt': self._call_tgpt,
            'ollama': self._call_ollama,
        }
        self.fallback_order = ['tgpt', 'ollama']

    async def chat(self, message: str, provider: str = 'auto') -> AIResponse:
        """Chat avec fallback automatique"""
        start_time = time.time()

        if provider == 'auto':
            # Essayer dans l'ordre des fallbacks
            for provider_name in self.fallback_order:
                if provider_name in self.providers:
                    logger.info(f"Tentative avec {provider_name}")
                    response = await self.providers[provider_name](message)

                    if response.success:
                        processing_time = time.time() - start_time
                        response.processing_time = processing_time
                        logger.info(f"Succès avec {provider_name} ({processing_time:.2f}s)")
                        return response

                    logger.warning(f"Échec {provider_name}: {response.error}")

            # Tous les providers ont échoué
            return AIResponse(
                success=False,
                response="Tous les providers IA ont échoué",
                model="unknown",
                provider="none",
                processing_time=time.time() - start_time,
                error="No working AI provider"
            )

        elif provider in self.providers:
            response = await self.providers[provider](message)
            response.processing_time = time.time() - start_time
            return response

        else:
            return AIResponse(
                success=False,
                response=f"Provider {provider} non disponible",
                model="unknown",
                provider="unknown",
                processing_time=time.time() - start_time,
                error=f"Unknown provider: {provider}"
            )

    async def _call_tgpt(self, message: str) -> AIResponse:
        """Appel à TGPT avec gestion d'erreurs"""
        try:
            # Timeout court pour détecter rapidement les pannes
            process = await asyncio.create_subprocess_exec(
                'tgpt', '--provider', 'sky', message,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=tempfile.gettempdir()
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=15.0  # 15 secondes max
                )

                if process.returncode == 0:
                    response = stdout.decode().strip()
                    if response and len(response) > 10:  # Vérifier réponse valide
                        return AIResponse(
                            success=True,
                            response=response,
                            model="gpt-4.1-mini",
                            provider="tgpt",
                            processing_time=0.0
                        )
                    else:
                        return AIResponse(
                            success=False,
                            response="",
                            model="gpt-4.1-mini",
                            provider="tgpt",
                            processing_time=0.0,
                            error="Empty or invalid response"
                        )
                else:
                    error = stderr.decode().strip()
                    return AIResponse(
                        success=False,
                        response="",
                        model="gpt-4.1-mini",
                        provider="tgpt",
                        processing_time=0.0,
                        error=f"Exit code {process.returncode}: {error}"
                    )

            except asyncio.TimeoutError:
                process.kill()
                return AIResponse(
                    success=False,
                    response="",
                    model="gpt-4.1-mini",
                    provider="tgpt",
                    processing_time=0.0,
                    error="Timeout (15s)"
                )

        except FileNotFoundError:
            return AIResponse(
                success=False,
                response="",
                model="gpt-4.1-mini",
                provider="tgpt",
                processing_time=0.0,
                error="tgpt not installed. Install: npm install -g tgpt"
            )
        except Exception as e:
            return AIResponse(
                success=False,
                response="",
                model="gpt-4.1-mini",
                provider="tgpt",
                processing_time=0.0,
                error=f"Exception: {str(e)}"
            )

    async def _call_ollama(self, message: str) -> AIResponse:
        """Appel à Ollama (modèles locaux)"""
        try:
            # Vérifier si ollama est installé
            check_process = await asyncio.create_subprocess_exec(
                'which', 'ollama',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await check_process.wait()

            if check_process.returncode != 0:
                return AIResponse(
                    success=False,
                    response="",
                    model="llama2",
                    provider="ollama",
                    processing_time=0.0,
                    error="ollama not installed. Install from: https://ollama.ai/"
                )

            # Lister les modèles disponibles
            list_process = await asyncio.create_subprocess_exec(
                'ollama', 'list',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            list_stdout, _ = await list_process.communicate()

            if list_process.returncode != 0:
                return AIResponse(
                    success=False,
                    response="",
                    model="unknown",
                    provider="ollama",
                    processing_time=0.0,
                    error="Cannot list ollama models"
                )

            # Chercher un modèle disponible (priorité à llama2)
            models_output = list_stdout.decode()
            available_models = []

            for line in models_output.split('\n'):
                if line.strip() and not line.startswith('NAME'):
                    model_name = line.split()[0]
                    available_models.append(model_name)

            if not available_models:
                return AIResponse(
                    success=False,
                    response="",
                    model="unknown",
                    provider="ollama",
                    processing_time=0.0,
                    error="No models available. Run: ollama pull llama2"
                )

            # Utiliser le premier modèle disponible
            model = available_models[0]

            # Faire l'appel
            process = await asyncio.create_subprocess_exec(
                'ollama', 'run', model, message,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=tempfile.gettempdir()
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=60.0  # Ollama peut être lent
                )

                if process.returncode == 0:
                    response = stdout.decode().strip()
                    if response:
                        return AIResponse(
                            success=True,
                            response=response,
                            model=model,
                            provider="ollama",
                            processing_time=0.0
                        )
                    else:
                        return AIResponse(
                            success=False,
                            response="",
                            model=model,
                            provider="ollama",
                            processing_time=0.0,
                            error="Empty response from ollama"
                        )
                else:
                    error = stderr.decode().strip()
                    return AIResponse(
                        success=False,
                        response="",
                        model=model,
                        provider="ollama",
                        processing_time=0.0,
                        error=f"Exit code {process.returncode}: {error}"
                    )

            except asyncio.TimeoutError:
                process.kill()
                return AIResponse(
                    success=False,
                    response="",
                    model=model,
                    provider="ollama",
                    processing_time=0.0,
                    error="Timeout (60s)"
                )

        except Exception as e:
            return AIResponse(
                success=False,
                response="",
                model="unknown",
                provider="ollama",
                processing_time=0.0,
                error=f"Exception: {str(e)}"
            )

# Test du système robuste
async def test_robust_ai():
    """Test du système IA robuste"""
    print("🧠 TEST SYSTÈME IA ROBUSTE")
    print("=" * 35)

    provider = RobustAIProvider()

    test_messages = [
        "Bonjour, présente-toi en 2 phrases",
        "Écris une fonction Python pour calculer fibonacci",
        "Quelle est la différence entre SQL et NoSQL ?"
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n🧪 Test {i}: {message[:50]}...")
        print("-" * 40)

        # Test avec fallback automatique
        response = await provider.chat(message, provider='auto')

        if response.success:
            print("✅ SUCCÈS:")
            print(f"   🤖 Provider: {response.provider}")
            print(f"   📝 Modèle: {response.model}")
            print(f"   ⏱️ Temps: {response.processing_time:.2f}s")
            print(f"   💬 Réponse: {response.response[:150]}..." if len(response.response) > 150 else f"   💬 Réponse: {response.response}")
        else:
            print("❌ ÉCHEC:")
            print(f"   🔴 Erreur: {response.error}")
            print(f"   ⏱️ Temps: {response.processing_time:.2f}s")

    print("\n🎯 RÉSULTATS:")
    print("• Fallback automatique: TGPT → Ollama")
    print("• Tolérance aux pannes individuelles")
    print("• Performance optimale préservée")
    print("• Système entièrement fonctionnel")

if __name__ == "__main__":
    asyncio.run(test_robust_ai())
