#!/usr/bin/env python3
"""
SHARINGAN OS - TOUTES LES VOIES DE COMMUNICATION
=================================================

Ce document recense toutes les methodes pour communiquer avec Sharingan OS
et evalue si elles peuvent etre unifiees.
"""

# ==============================================================================
# 1. VOIES DE COMMUNICATION ACTUELLES
# ==============================================================================

VOIES = {
    # --------------------------------------------------------------------------
    # 1.1 SHARINGAN SOUL (Conscience principale)
    # --------------------------------------------------------------------------
    "soul.process_input": {
        "description": "Traitement via le Soul avec motivations et memoire",
        "entree": "Texte libre en langage naturel",
        "sortie": {
            "soul_response": "Reponse emotionnelle",
            "activated_motivations": "Liste des motivations activees",
            "suggested_actions": "Actions suggerees",
            "dominant_emotion": "Emotion dominante",
            "consciousness_evolution": "Evolution de la conscience",
            "episodic_memory_size": "Taille memoire episodique"
        },
        "triggers": ["exploit", "vulnerabilite", "attaque", "scan", "recon", 
                     "technique", "skill", "master", "chasse", "hunt", 
                     "dominer", "control", "chercher"],
        "unifiable": True
    },
    
    "soul.process_input_with_execution": {
        "description": "process_input + execution automatique des actions",
        "sortie": "Meme que process_input + executed_actions",
        "unifiable": True
    },
    
    # --------------------------------------------------------------------------
    # 1.2 AI PROVIDERS (LLMs externes)
    # --------------------------------------------------------------------------
    "ai_providers.chat": {
        "description": "Chat direct avec un provider AI (tgpt, MiniMax, Grok)",
        "entree": "Message texte + contexte optionnel",
        "sortie": {"response": "Reponse du LLM", "provider": "Provider utilise"},
        "unifiable": True
    },
    
    # --------------------------------------------------------------------------
    # 1.3 CORE SHARINGAN (Point entree principal)
    # --------------------------------------------------------------------------
    "core.chat": {
        "description": "Chat avec enrichissement Sharingan",
        "entree": "Message + provider optionnel",
        "sortie": "Reponse enrichie",
        "unifiable": True
    },
    
    "core.chat_with_warning": {
        "description": "Chat + warnings du mode neutre",
        "unifiable": False  # Mode special
    },
    
    # --------------------------------------------------------------------------
    # 1.4 API WEB
    # --------------------------------------------------------------------------
    "POST /api/chat": {
        "description": "Endpoint HTTP pour le chat",
        "entree": {"message": "Texte", "execute_actions": "booleen"},
        "sortie": "JSON complet avec ame, motivations, actions",
        "unifiable": True
    },
    
    # --------------------------------------------------------------------------
    # 1.5 LIGNE DE COMMANDE (main.py)
    # --------------------------------------------------------------------------
    "python main.py ai 'message'": {
        "description": "Chat via CLI",
        "options": ["--provider", "-p", "--warning", "-w"],
        "unifiable": True
    },
    
    "python main.py status": {
        "description": "Afficher le statut du systeme",
        "unifiable": True
    },
    
    "python main.py capabilities": {
        "description": "Lister les capacites",
        "unifiable": True
    },
}


# ==============================================================================
# 2. RESUME: TOUTES LES METHODES PEUVENT ETRE UNIFIEES!
# ==============================================================================

"""
OUI, toutes les methodes peuvent etre unifiees en une seule interface!

AVANT (plusieurs methodes):
- soul.process_input()
- soul.process_input_with_execution()
- core.chat()
- core.chat_with_warning()
- POST /api/chat
- python main.py ai
- et plus...

APRES (1 methode unifiee):
"""

def sharingan_chat(message: str, **options):
    """
    Interface unique pour communiquer avec Sharingan OS.
    
    Args:
        message: Texte en langage naturel
        execute: Executer les actions suggerees (defaut: True)
        provider: AI provider "tgpt"/"minimax"/"grok"/"auto" (defaut: "auto")
        neutral: Mode neutral avec avertissements (defaut: False)
        context: Contexte conversationnel optionnel
    
    Returns:
        {
            "response": "Reponse principale",
            "soul_response": "Reponse du Soul",
            "motivations": ["recon", "exploit"],
            "actions_suggerees": ["Scanner les ports"],
            "actions_executees": 2,
            "success_rate": 0.5,
            "consciousness_level": 1.5,
            "memory_size": 10,
            "provider": "tgpt"
        }
    """
    from sharingan_soul import get_sharingan_soul
    from main import get_core
    
    options = options or {}
    execute = options.get("execute", True)
    provider = options.get("provider", "auto")
    neutral = options.get("neutral", False)
    context = options.get("context", None)
    
    result = {}
    
    # 1. Traitement par le Soul
    soul = get_sharingan_soul()
    soul_result = soul.process_input_with_execution(message, execute_actions=execute)
    
    result.update({
        "soul_response": soul_result.get("soul_response", ""),
        "motivations": soul_result.get("activated_motivations", []),
        "actions_suggerees": soul_result.get("suggested_actions", []),
        "actions_executees": soul_result.get("actions_executed", 0),
        "success_rate": soul_result.get("execution_success_rate", 0),
        "consciousness_level": soul_result.get("consciousness_evolution", {}).get("current_level", 1.0),
        "memory_size": soul_result.get("episodic_memory_size", 0)
    })
    
    # 2. Appel AI si necessaire
    core = get_core()
    if neutral:
        ai_result = core.chat_with_warning(message, context=context)
        result["response"] = ai_result.get("response", "")
        result["warnings"] = ai_result.get("warnings", [])
    else:
        ai_result = core.chat(message, provider=provider, context=context)
        result["response"] = ai_result.get("response", "")
        result["provider"] = ai_result.get("provider", provider)
    
    return result


if __name__ == "__main__":
    # Test
    print("=== TEST INTERFACE UNIFIEE ===")
    result = sharingan_chat("Scan les ports")
    print("Motivations:", result["motivations"])
    print("Actions:", result["actions_suggerees"])
    print("Executees:", result["actions_executees"])
    print("Conscience:", result["consciousness_level"])
