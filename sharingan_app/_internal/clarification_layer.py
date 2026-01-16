#!/usr/bin/env python3
"""
Clarification Layer - Proactive Query Analysis & Intent Resolution
Prevents execution without user confirmation by analyzing intent and offering choices.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.clarification")

class QueryType(Enum):
    QUESTION = "question"
    ACTION = "action"
    AMBIGUOUS = "ambiguous"
    CONFIRMATION = "confirmation"

class ActionLevel(Enum):
    READ_ONLY = 1
    READ_WRITE = 2
    SYSTEM_MODIFY = 3
    DESTRUCTIVE = 4

@dataclass
class ClarificationRequest:
    original_query: str
    query_type: QueryType
    confidence: float
    suggested_approaches: List[Dict[str, Any]]
    requires_confirmation: bool
    user_preferences: Dict[str, Any]

@dataclass
class ClarificationResponse:
    should_execute: bool
    confirmed_approach: Optional[str]
    clarification_needed: bool
    message: str
    alternatives: List[str]

class ProactiveClarifier:
    """
    Analyzes queries and determines if user wants:
    1. Just information (explain how)
    2. Execution (do it now)
    3. Options (show choices)
    """
    
    QUESTION_INDICATORS = [
        "comment", "pourquoi", "comment", "explique", "decris", "decrire",
        "how", "why", "what is", "what are", "describe", "explain",
        "donne-moi", "donne moi", "dis-moi", "dis moi", "je veux savoir",
        "can you explain", "what does", "meaning of", "c'est quoi"
    ]
    
    ACTION_INDICATORS = [
        "fait", "fais", "execute", "cree", "creer", "genere", "generer",
        "make", "do", "create", "generate", "run", "execute", "install",
        "ajoute", "ajouter", "supprime", "supprimer", "modifie", "modifier",
        "configure", "deploy", "start", "stop"
    ]
    
    CONFIRMATION_PHRASES = [
        "oui", "yes", "ok", "d'accord", "ok go", "go ahead", "fait le",
        "execute", "vas-y", "aller", "allez", "je veux", "je confirme"
    ]
    
    def __init__(self, memory_manager=None):
        self.memory = memory_manager
        self.query_history: List[Dict] = []
        
    def analyze(self, query: str, context: Optional[Dict] = None) -> ClarificationRequest:
        """Analyze query to determine intent"""
        query_lower = query.lower().strip()
        
        query_type = self._classify_query(query_lower)
        confidence = self._calculate_confidence(query_lower, query_type)
        suggested_approaches = self._generate_approaches(query, query_type)
        requires_confirmation = self._needs_confirmation(query_type)
        user_preferences = self._get_user_preferences(context)
        
        logger.info(f"Query analysis: type={query_type.value}, confidence={confidence:.2f}")
        
        return ClarificationRequest(
            original_query=query,
            query_type=query_type,
            confidence=confidence,
            suggested_approaches=suggested_approaches,
            requires_confirmation=requires_confirmation,
            user_preferences=user_preferences
        )
    
    def _classify_query(self, query: str) -> QueryType:
        """Classify query as question, action, or ambiguous"""
        question_score = sum(1 for ind in self.QUESTION_INDICATORS if ind in query)
        action_score = sum(1 for ind in self.ACTION_INDICATORS if ind in query)
        
        if question_score > action_score:
            return QueryType.QUESTION
        elif action_score > question_score:
            return QueryType.ACTION
        elif re.search(r'\?', query):
            return QueryType.QUESTION
        elif len(query.split()) < 3:
            return QueryType.AMBIGUOUS
        else:
            return QueryType.AMBIGUOUS
    
    def _calculate_confidence(self, query: str, query_type: QueryType) -> float:
        """Calculate confidence score for classification"""
        base_confidence = 0.5
        
        if query_type == QueryType.QUESTION:
            base_confidence += sum(0.1 for ind in self.QUESTION_INDICATORS if ind in query)
        elif query_type == QueryType.ACTION:
            base_confidence += sum(0.1 for ind in self.ACTION_INDICATORS if ind in query)
        
        return min(0.95, base_confidence)
    
    def _generate_approaches(self, query: str, query_type: QueryType) -> List[Dict[str, Any]]:
        """Generate different approaches to handle the query"""
        approaches = []
        
        if query_type == QueryType.QUESTION:
            approaches = [
                {
                    "id": "explain",
                    "label": "Expliquer l'approche",
                    "description": "Je peux t'expliquer comment faire cela, étape par étape",
                    "action_type": "read_only",
                    "icon": "📖"
                },
                {
                    "id": "example",
                    "label": "Donner un exemple",
                    "description": "Je peux fournir un exemple concret de code ou commande",
                    "action_type": "read_only",
                    "icon": "💡"
                },
                {
                    "id": "execute_if_ready",
                    "label": "Executer directement",
                    "description": "Je peux executer cela maintenant si tu veux",
                    "action_type": "read_write",
                    "icon": "⚡"
                }
            ]
        elif query_type == QueryType.ACTION:
            approaches = [
                {
                    "id": "confirm_execute",
                    "label": "Confirmer et executer",
                    "description": "Confirme que tu veux que je le fasse maintenant",
                    "action_type": "read_write",
                    "icon": "✅"
                },
                {
                    "id": "preview_first",
                    "label": "Previsualiser d'abord",
                    "description": "Je peux montrer ce que je vais faire avant d'executer",
                    "action_type": "read_only",
                    "icon": "👁️"
                },
                {
                    "id": "explain_how",
                    "label": "Expliquer comment faire",
                    "description": "Je peux expliquer comment faire cela toi-meme",
                    "action_type": "read_only",
                    "icon": "📖"
                }
            ]
        else:
            approaches = [
                {
                    "id": "ask_clarification",
                    "label": "Demander clarification",
                    "description": "Je ne suis pas sur de comprendre, peux-tu preciser?",
                    "action_type": "read_only",
                    "icon": "❓"
                },
                {
                    "id": "list_options",
                    "label": "Lister les possibilites",
                    "description": "Je peux te montrer ce que je peux faire pour ta requete",
                    "action_type": "read_only",
                    "icon": "📋"
                }
            ]
        
        return approaches
    
    def _needs_confirmation(self, query_type: QueryType) -> bool:
        """Determine if user confirmation is needed"""
        return query_type == QueryType.ACTION
    
    def _get_user_preferences(self, context: Optional[Dict]) -> Dict:
        """Get user preferences from memory or context"""
        prefs = {
            "auto_execute": False,
            "always_preview": True,
            "prefer_explanation_first": True
        }
        
        if self.memory:
            stored_prefs = self.memory.retrieve("user:clarification_preferences")
            if stored_prefs:
                prefs.update(stored_prefs.get("data", {}))
        
        if context:
            if context.get("interactive"):
                prefs["always_preview"] = True
            if context.get("background"):
                prefs["auto_execute"] = False
        
        return prefs
    
    def format_clarification(self, request: ClarificationRequest) -> str:
        """Format clarification message for user"""
        lines = []
        
        if request.query_type == QueryType.QUESTION:
            lines.append("📝 **Question detectee**")
            lines.append(f"Je vois que tu veux savoir quelque chose.")
        elif request.query_type == QueryType.ACTION:
            lines.append("⚡ **Action demandee**")
            lines.append(f"Je detecte une action a executer.")
        else:
            lines.append("❓ **Requete ambiguë**")
            lines.append("Je ne suis pas sur de ce que tu veux faire.")
        
        lines.append("")
        lines.append("**Options disponibles:**")
        
        for i, approach in enumerate(request.suggested_approaches, 1):
            lines.append(f"{i}. {approach['icon']} **{approach['label']}**")
            lines.append(f"   → {approach['description']}")
        
        lines.append("")
        lines.append("**Reponds avec:**")
        lines.append(f"  - Le numero de ton choix (1-{len(request.suggested_approaches)})")
        lines.append("  - 'expliquer' pour juste comprendre")
        lines.append("  - 'executer' pour faire maintenant")
        
        return "\n".join(lines)
    
    def is_confirmation(self, response: str) -> Tuple[bool, str]:
        """Check if response is a confirmation"""
        response_lower = response.lower().strip()
        
        if response_lower in ["1", "2", "3"]:
            return True, f"choice_{response_lower}"
        
        if any(phrase in response_lower for phrase in self.CONFIRMATION_PHRASES):
            if any(w in response_lower for w in ["non", "no", "pas", "cancel", "annule"]):
                return True, "refused"
            return True, "confirmed"
        
        if "non" in response_lower or "pas" in response_lower or "cancel" in response_lower:
            return True, "refused"
        
        return False, ""
    
    def handle_response(self, request: ClarificationRequest, response: str) -> ClarificationResponse:
        """Handle user response to clarification"""
        is_confirm, confirm_type = self.is_confirmation(response)
        
        if not is_confirm:
            return ClarificationResponse(
                should_execute=False,
                confirmed_approach=None,
                clarification_needed=True,
                message="Je n'ai pas compris ta reponse. Veux-tu que j'execute, ou prefères-tu une explication?",
                alternatives=["Explique", "Execute", "1", "2", "3"]
            )
        
        if confirm_type == "refused":
            return ClarificationResponse(
                should_execute=False,
                confirmed_approach=None,
                clarification_needed=False,
                message="D'accord, je n'execute rien. Que veux-tu faire a la place?",
                alternatives=[]
            )
        
        if confirm_type.startswith("choice_"):
            choice_idx = int(confirm_type.split("_")[1]) - 1
            if 0 <= choice_idx < len(request.suggested_approaches):
                approach = request.suggested_approaches[choice_idx]
                
                if approach["action_type"] == "read_only":
                    return ClarificationResponse(
                        should_execute=False,
                        confirmed_approach=approach["id"],
                        clarification_needed=False,
                        message=f"OK, je vais {approach['label'].lower()}...",
                        alternatives=[]
                    )
                else:
                    return ClarificationResponse(
                        should_execute=True,
                        confirmed_approach=approach["id"],
                        clarification_needed=False,
                        message=f"OK, je confirme et {approach['label'].lower()}...",
                        alternatives=[]
                    )
        
        if confirm_type == "confirmed":
            return ClarificationResponse(
                should_execute=True,
                confirmed_approach="confirm_execute",
                clarification_needed=False,
                message="Parfait, j'execute maintenant...",
                alternatives=[]
            )
        
        return ClarificationResponse(
            should_execute=False,
            confirmed_approach=None,
            clarification_needed=True,
            message="Peux-tu preciser?",
            alternatives=[]
        )
    
    def log_query(self, query: str, request: ClarificationRequest, response: str) -> None:
        """Log query for learning"""
        entry = {
            "query": query,
            "type": request.query_type.value,
            "confidence": request.confidence,
            "user_response": response,
            "timestamp": datetime.now().isoformat()
        }
        self.query_history.append(entry)
        
        if len(self.query_history) > 100:
            self.query_history = self.query_history[-50:]
        
        if self.memory:
            self.memory.store(
                f"clarification:{datetime.now().timestamp()}",
                entry,
                category="learning",
                priority="LOW",
                tags=["clarification", request.query_type.value]
            )


def get_clarifier(memory_manager=None) -> ProactiveClarifier:
    """Get clarifier instance"""
    return ProactiveClarifier(memory_manager)


if __name__ == "__main__":
    print("=== CLARIFICATION LAYER TEST ===\n")
    
    clarifier = get_clarifier()
    
    test_queries = [
        "comment faire un scan nmap?",
        "execute un scan du reseau 192.168.1.0/24",
        "c'est quoi Sharingan?",
        "installe nmap",
        "aide moi"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        
        request = clarifier.analyze(query)
        print(clarifier.format_clarification(request))
