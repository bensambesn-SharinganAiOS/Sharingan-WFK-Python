#!/usr/bin/env python3
"""
Sharingan OS - Fake Detector & Readiness Validator
Detects fake outputs, placeholders, and validates system readiness.
Auteur: Ben Sambe
"""

import re
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Patterns de détection de fakes
FAKE_PATTERNS = {
    "placeholder": [
        r"AI Response to:",
        r"AI Error:",
        r"\[PLACEHOLDER\]",
        r"\[TODO\]",
        r"\[FIXME\]",
        r"\<TBD\>",
        r"\<TODO\>",
        r"Not implemented yet",
        r"To be implemented",
        r"Coming soon",
    ],
    "vague_response": [
        r"I can't help with that",
        r"I'm not able to",
        r"As an AI language model",
        r"I apologize, but I cannot",
        r"I'm sorry, but I can't",
    ],
    "incomplete": [
        r"\.\.\.",
        r"\[?\]",
        r"etc\.?",
        r"and so on",
    ],
    "shell_fake": [
        r"Command not found",
        r"command not found",
        r"No such file or directory",
        r"permission denied",
        r"command failed",
    ]
}


@dataclass
class FakeResult:
    """Résultat de détection de fake"""
    is_fake: bool
    fake_type: Optional[str]
    confidence: float
    details: str
    suggestions: List[str]


class FakeDetector:
    """
    Détecte les outputs fake, placeholders et réponses incomplètes.
    Garantit que le système ne renvoie pas de fausses données.
    """
    
    def __init__(self):
        self.detection_history: List[Dict] = []
        
    def detect_fakes(self, content: str, context: str = "general") -> FakeResult:
        """
        Détecte si le contenu est un fake/placeholder.
        
        Args:
            content: Contenu à analyser
            context: Contexte (ai_response, shell_output, code, etc.)
        
        Returns:
            FakeResult avec détection
        """
        if not content or len(content.strip()) == 0:
            return FakeResult(
                is_fake=True,
                fake_type="empty",
                confidence=1.0,
                details="Content is empty",
                suggestions=["Provide actual content"]
            )
        
        # Vérifier chaque catégorie de fake
        for category, patterns in FAKE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return FakeResult(
                        is_fake=True,
                        fake_type=category,
                        confidence=0.9,
                        details=f"Detected fake pattern: {pattern}",
                        suggestions=[
                            f"Remove or replace {pattern}",
                            "Provide actual data instead of placeholder"
                        ]
                    )
        
        # Vérifier les réponses trop vagues
        if self._is_vague_response(content):
            return FakeResult(
                is_fake=True,
                fake_type="vague",
                confidence=0.7,
                details="Response is too vague or non-committal",
                suggestions=["Provide specific, actionable information"]
            )
        
        # Détection de shell fake
        if context == "shell_output":
            if self._is_shell_fake(content):
                return FakeResult(
                    is_fake=True,
                    fake_type="shell_error",
                    confidence=0.8,
                    details="Shell output indicates failure",
                    suggestions=["Fix the underlying command or script"]
                )
        
        return FakeResult(
            is_fake=False,
            fake_type=None,
            confidence=1.0,
            details="Content appears genuine",
            suggestions=[]
        )
    
    def _is_vague_response(self, content: str) -> bool:
        """Vérifie si la réponse est trop vague"""
        vague_indicators = [
            content.lower().startswith("it depends"),
            content.lower().startswith("maybe"),
            content.lower().startswith("possibly"),
            "could be" in content.lower() and len(content) < 50,
        ]
        return any(vague_indicators)
    
    def _is_shell_fake(self, content: str) -> bool:
        """Vérifie si l'output shell est un fake/erreur"""
        error_indicators = [
            "command not found" in content.lower(),
            "no such file" in content.lower(),
            "failed" in content.lower() and "error" in content.lower(),
            "permission denied" in content.lower(),
        ]
        return any(error_indicators)
    
    def validate_ai_response(self, response: str, query: str) -> Tuple[bool, str]:
        """
        Valide qu'une réponse IA est authentique.
        
        Returns:
            (is_valid, message)
        """
        result = self.detect_fakes(response, context="ai_response")
        
        if result.is_fake:
            return False, f"Fake detected: {result.details}"
        
        # Vérifier pertinence
        if self._is_unrelated(response, query):
            return False, "Response appears unrelated to query"
        
        return True, "Response is valid"
    
    def _is_unrelated(self, response: str, query: str) -> bool:
        """Vérifie si la réponse est sans rapport avec la query"""
        # Extraire mots-clés de la query
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        response_words = set(re.findall(r'\b\w+\b', response.lower()))
        
        # Si moins de 20% de mots en commun et query longue
        if len(query_words) > 5:
            overlap = len(query_words & response_words)
            if overlap / len(query_words) < 0.2:
                return True
        return False
    
    def validate_readiness(self) -> Dict:
        """
        Valide que le système Sharingan est prêt à fonctionner.
        
        Returns:
            Dict avec status de chaque composant
        """
        results = {
            "ready": True,
            "components": {},
            "issues": [],
            "timestamp": str(__import__("datetime").datetime.now())
        }
        
        # Vérifier Python
        results["components"]["python"] = {
            "status": "ok" if sys.version_info >= (3, 10) else "old",
            "version": sys.version
        }
        
        # Vérifier modules essentiels
        essential_modules = [
            ("sharingan_os", "Core OS"),
            ("ai_providers", "AI Providers"),
            ("system_consciousness", "Consciousness"),
            ("context_manager", "Context"),
            ("genome_memory", "Genome Memory"),
        ]
        
        for module_name, description in essential_modules:
            try:
                __import__(module_name)
                results["components"][module_name] = {
                    "status": "ok",
                    "description": description
                }
            except ImportError as e:
                results["components"][module_name] = {
                    "status": "missing",
                    "description": description,
                    "error": str(e)
                }
                results["ready"] = False
                results["issues"].append(f"Missing module: {module_name}")
        
        return results


def detect_fakes(content: str, context: str = "general") -> FakeResult:
    """Fonction helper pour détection rapide de fakes"""
    detector = FakeDetector()
    return detector.detect_fakes(content, context)


def validate_readiness() -> Dict:
    """Fonction helper pour valider la préparation du système"""
    detector = FakeDetector()
    return detector.validate_readiness()


# Alias pour imports
__all__ = ["FakeDetector", "detect_fakes", "validate_readiness", "FakeResult"]
