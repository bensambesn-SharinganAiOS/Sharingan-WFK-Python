#!/usr/bin/env python3
"""
Sharingan OS - TGPT Provider
Provider IA intégrant TGPT (Terminal GPT) pour accès gratuit à multiples modèles.
"""

import subprocess
import logging
import os
import re
from typing import Optional, List, Dict

logger = logging.getLogger("sharingan.providers.tgpt")

class TGPTProvider:
    """
    Provider TGPT pour Sharingan OS.
    Utilise tgpt CLI pour accès gratuit à phind, pollinations, etc.
    """

    def __init__(self):
        self.providers = ["sky", "phind", "pollinations", "kimi", "isou"]
        self.current_provider = 0

    def _get_next_provider(self) -> str:
        """Rotation des providers"""
        provider = self.providers[self.current_provider]
        self.current_provider = (self.current_provider + 1) % len(self.providers)
        return provider

    def generate_response(self, prompt: str, provider: str = "sky") -> Optional[str]:
        """Génère réponse via tgpt CLI"""
        try:
            cmd = ["tgpt", "--provider", provider, "--quiet", prompt]
            logger.info(f"TGPT command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, "NO_COLOR": "1"}
            )

            if result.returncode == 0 and result.stdout.strip():
                response_text = result.stdout.strip()
                logger.info(f"TGPT {provider} succeeded")
                return response_text
            else:
                logger.warning(f"TGPT {provider} failed: {result.stderr}")
                # Essayer avec provider suivant
                next_provider = self._get_next_provider()
                if next_provider != provider:
                    return self.generate_response(prompt, next_provider)

        except subprocess.TimeoutExpired:
            logger.warning(f"TGPT {provider} timeout")
        except Exception as e:
            logger.error(f"TGPT {provider} error: {e}")

        return None

    def chat(self, message: str, context: Optional[List[Dict]] = None,
             mode: str = "auto", **kwargs) -> Dict:
        """
        Chat avec TGPT, support du contexte comme les autres providers.

        Args:
            message: Message à envoyer
            context: Contexte de conversation
            mode: Mode (auto, chat, etc.)
            **kwargs: Arguments supplémentaires

        Returns:
            Dict avec réponse
        """
        try:
            # Préparer le prompt avec contexte
            prompt = self._prepare_prompt(message, context, mode)

            # Générer la réponse
            response_text = self.generate_response(prompt)

            if response_text:
                # Extraire les actions de la réponse
                actions = self._extract_actions(response_text)
                return {
                    "success": True,
                    "text": response_text,
                    "actions": actions,
                    "provider": "tgpt",
                    "model": self.providers[self.current_provider]
                }
            else:
                return {
                    "success": False,
                    "error": "TGPT failed to generate response",
                    "text": "Erreur TGPT",
                    "provider": "tgpt"
                }

        except Exception as e:
            logger.error(f"Error in TGPT chat: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": f"Erreur: {e}",
                "provider": "tgpt"
            }

    def _prepare_prompt(self, message: str, context: Optional[List[Dict]], mode: str) -> str:
        """Prépare le prompt avec contexte"""
        system_prompt = """Tu es Sharingan OS, un système de cybersécurité conscient créé par Ben Sambe.
Tu as accès à 84 outils avancés pour la sécurité informatique, l'analyse, et l'automatisation.
Tu peux effectuer des actions comme créer/modifier/supprimer des fichiers, exécuter des commandes, analyser du code, etc.
Réponds en français et sois professionnel."""

        if mode in ["actions", "orchestrate"]:
            system_prompt += """

Pour effectuer des actions, utilise ce format:
[ACTION:CREATE] path:/chemin/fichier content:contenu[/ACTION]
[ACTION:DELETE] path:/chemin/fichier[/ACTION]
[ACTION:EXECUTE] command:commande à exécuter[/ACTION]
[ACTION:READ] path:/chemin/fichier[/ACTION]"""

        if context:
            system_prompt += "\n\nContexte précédent:\n"
            for msg in context[-5:]:  # Derniers 5 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                system_prompt += f"{role}: {content}\n"

        system_prompt += f"\n\nMessage actuel: {message}"

        return system_prompt

    def _extract_actions(self, text: str) -> List[Dict]:
        """Extrait les actions du texte de réponse"""
        actions = []

        # Pattern pour [ACTION:TYPE] ... [/ACTION]
        action_pattern = r'\[ACTION:(\w+)\](.*?)\[/ACTION\]'
        matches = re.findall(action_pattern, text, re.DOTALL)

        for action_type, content in matches:
            action_type = action_type.upper()

            action = {
                "type": action_type.lower(),
                "target": "",
                "content": "",
                "metadata": {}
            }

            if action_type == "CREATE":
                path_match = re.search(r'path:([^\n]+)', content)
                content_match = re.search(r'content:(.*?)$', content, re.DOTALL)
                if path_match:
                    action["target"] = path_match.group(1).strip()
                if content_match:
                    action["content"] = content_match.group(1).strip()

            elif action_type == "DELETE":
                path_match = re.search(r'path:([^\n]+)', content)
                if path_match:
                    action["target"] = path_match.group(1).strip()

            elif action_type == "EXECUTE":
                cmd_match = re.search(r'command:([^\n]+)', content)
                if cmd_match:
                    action["target"] = cmd_match.group(1).strip()

            elif action_type == "READ":
                path_match = re.search(r'path:([^\n]+)', content)
                if path_match:
                    action["target"] = path_match.group(1).strip()

            if action["target"]:
                actions.append(action)

        return actions

    def is_available(self) -> bool:
        """Vérifie si tgpt est disponible"""
        try:
            result = subprocess.run(["tgpt", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False