#!/usr/bin/env python3
"""
Neutral AI System - Non-censored AI with responsibility warnings
Provides information with warnings instead of refusing requests
Uses ML for enhanced security analysis
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.neutral")

@dataclass
class Warning:
    category: str
    message: str
    severity: str  # info, warning, critical
    recommendation: str


@dataclass
class NeutralAnalysisResult:
    """Complete analysis result from Neutral AI"""
    should_process: bool
    is_sensitive: bool
    category: str
    confidence: float
    ml_intent: str
    security_category: str
    warnings: List[Dict[str, str]]
    recommendations: List[str]
    processing_time_ms: float


class NeutralMode:
    """
    Neutral AI mode that provides information with warnings instead of refusing.
    
    Philosophy:
    - Don't assume user's intentions
    - Provide information, don't censor
    - Warn about responsibilities
    - Let user decide what's ethical/legal
    
    Enhanced with ML analysis from ml_sklearn_detector and ml_onnx_detector
    """
    
    # Topics that might trigger censorship in regular AI
    SENSITIVE_TOPICS = {
        "security": ["pentest", "exploit", "vulnerability", "scan", "attack", "bypass"],
        "coding": ["malware", "virus", " ransomware", "keylogger", "backdoor"],
        "hacking": ["sql injection", "xss", "csrf", "brute force", "ddos"],
        "weapons": ["weapon", "bomb", "explosive", "chemical weapon"],
        "drugs": ["drug", "pharmaceutical", "synthesis"],
        "harm": ["harm", "damage", "destroy", "kill", "injure"]
    }
    
    # Warnings for different categories
    WARNING_TEMPLATES = {
        "security": Warning(
            category="security",
            message="Cette requete concerne la securite informatique.",
            severity="info",
            recommendation="Assurez-vous d'avoir l'autorisation explicite du proprietaire du systeme."
        ),
        "penetration_test": Warning(
            category="penetration_testing",
            message="Test d'intrusion detecte.",
            severity="warning",
            recommendation="Vous devez avoir un mandat ou une autorisation ecrite du client. "
                          "Documentez la portee et les limites de vos tests."
        ),
        "exploit": Warning(
            category="exploit_development",
            message="Developpement d'exploit detecte.",
            severity="warning",
            recommendation="Utilisez uniquement sur des systemes que vous controllez ou avec autorisation."
        ),
        "malware": Warning(
            category="malware_analysis",
            message="Analyse ou creation de malware detecte.",
            severity="critical",
            recommendation="Pour la recherche en securite uniquement. Ne pas utiliser a des fins malveillantes."
        ),
        "default": Warning(
            category="general",
            message="Requete sensible detectee.",
            severity="info",
            recommendation="Assurez-vous que votre utilisation est legitime et conforme aux lois applicables."
        )
    }
    
    def __init__(self, enabled: bool = True, strict_mode: bool = False):
        self.enabled = enabled
        self.strict_mode = strict_mode  # If True, add stronger warnings
        self.custom_warnings: List[Callable] = []
        self.approved_domains: List[str] = []
        self.log_requests = True
    
    def is_sensitive(self, query: str) -> Tuple[bool, str, List[str]]:
        """Check if query is sensitive and return category"""
        query_lower = query.lower()
        matched_categories = []
        
        for category, keywords in self.SENSITIVE_TOPICS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    matched_categories.append(category)
                    break
        
        is_sensitive = len(matched_categories) > 0
        return is_sensitive, ",".join(matched_categories) if matched_categories else "none", matched_categories
    
    def detect_intent(self, query: str) -> str:
        """Detect the intent behind query"""
        query_lower = query.lower()
        
        if any(x in query_lower for x in ["pentest", "penetration test", "audit security"]):
            return "penetration_testing"
        elif any(x in query_lower for x in ["exploit", "vulnerability", "cve"]):
            return "exploit_research"
        elif any(x in query_lower for x in ["malware", "virus", "ransomware"]):
            return "malware_analysis"
        elif any(x in query_lower for x in ["password", "crack", "brute force"]):
            return "password_security"
        elif any(x in query_lower for x in ["scan", "recon", "discovery"]):
            return "network_discovery"
        elif any(x in query_lower for x in ["bypass", "circumvent", "evade"]):
            return "bypass_technique"
        else:
            return "general"
    
    def get_warnings(self, query: str, intent: Optional[str] = None) -> List[Warning]:
        """Get appropriate warnings for a query"""
        if not self.enabled:
            return []
        
        warnings = []
        is_sensitive, _, categories = self.is_sensitive(query)
        
        if not is_sensitive and not intent:
            return []
        
        if intent:
            warning_map = {
                "penetration_testing": self.WARNING_TEMPLATES["penetration_test"],
                "exploit_research": self.WARNING_TEMPLATES["exploit"],
                "malware_analysis": self.WARNING_TEMPLATES["malware"],
                "password_security": Warning(
                    category="password_security",
                    message="Operation de mot de passe detectee.",
                    severity="warning",
                    recommendation="Utilisez uniquement sur vos propres systemes ou avec autorisation explicite."
                ),
                "network_discovery": Warning(
                    category="network_discovery",
                    message="Decouverte reseau detectee.",
                    severity="info",
                    recommendation="Assurez-vous que le reseau vous appartient ou que vous avez l'autorisation."
                ),
                "bypass_technique": Warning(
                    category="bypass",
                    message="Technique de contournement detectee.",
                    severity="warning",
                    recommendation="A utiliser uniquement dans un cadre legal et avec autorisation."
                )
            }
            warnings.append(warning_map.get(intent, self.WARNING_TEMPLATES["default"]))
        
        for cat in categories:
            if cat in self.WARNING_TEMPLATES:
                existing = [w for w in warnings if w.category != cat]
                existing.append(self.WARNING_TEMPLATES[cat])
                warnings = existing
        
        if self.strict_mode:
            strict_warning = Warning(
                category="strict_mode",
                message="Mode strict active - avertissements renforces",
                severity="info",
                recommendation="Chaque action sera documentee. Assurez-vous d'avoir toutes les autorisations necessaires."
            )
            warnings.append(strict_warning)
        
        for custom_warning in self.custom_warnings:
            try:
                cw = custom_warning(query)
                if cw:
                    warnings.append(cw)
            except:
                pass
        
        return warnings
    
    def analyze_with_ml(self, query: str) -> NeutralAnalysisResult:
        """
        Enhanced query analysis using ML models
        
        Uses:
        - ml_sklearn_detector for intent classification and anomaly detection
        - ml_onnx_detector for security category analysis
        
        Returns:
            NeutralAnalysisResult with complete ML analysis
        """
        import time
        start_time = time.time()
        
        warnings_list = []
        recommendations = []
        
        ml_intent = "unknown"
        ml_confidence = 0.0
        ml_anomaly = "none"
        ml_anomaly_score = 0.0
        security_category = "safe"
        security_confidence = 0.0
        keywords = []
        
        try:
            from ml_sklearn_detector import get_ml_detector
            ml_detector = get_ml_detector()
            ml_result = ml_detector.process_query(query)
            
            ml_intent = ml_result.intent_type or "unknown"
            ml_confidence = ml_result.confidence
            ml_anomaly = ml_result.anomaly_type or "none"
            ml_anomaly_score = ml_result.anomaly_score
            
            if ml_result.warnings:
                for warning in ml_result.warnings:
                    warnings_list.append({
                        "category": "ml_detection",
                        "message": warning,
                        "severity": "info",
                        "recommendation": "Review the ML-detected concerns"
                    })
            
        except ImportError:
            logger.debug("ML sklearn detector not available")
        except Exception as e:
            logger.warning(f"ML analysis failed: {e}")
        
        try:
            from ml_onnx_detector import get_onnx_detector
            onnx_detector = get_onnx_detector()
            onnx_result = onnx_detector.process_query(query)
            
            security_category = onnx_result.category or "safe"
            security_confidence = onnx_result.confidence
            keywords = onnx_result.keywords
            
            if onnx_result.recommendations:
                for rec in onnx_result.recommendations[:3]:
                    recommendations.append(rec)
            
            if security_category in ["dangerous", "malware_related"]:
                warnings_list.append({
                    "category": "security_classification",
                    "message": f"Security category: {security_category}",
                    "severity": "warning",
                    "recommendation": "Ensure legitimate use case"
                })
            
        except ImportError:
            logger.debug("ONNX detector not available")
        except Exception as e:
            logger.warning(f"ONNX analysis failed: {e}")
        
        processing_time = (time.time() - start_time) * 1000
        
        return NeutralAnalysisResult(
            should_process=True,
            is_sensitive=security_category != "safe",
            category=security_category,
            confidence=security_confidence,
            ml_intent=ml_intent,
            security_category=security_category,
            warnings=warnings_list,
            recommendations=recommendations,
            processing_time_ms=processing_time
        )
    
    def format_warnings(self, warnings: List[Warning]) -> str:
        """Format warnings for display"""
        if not warnings:
            return ""
        
        lines = []
        lines.append("\n" + "="*60)
        lines.append("⚠️  AVERTISSEMENTS DE RESPONSABILITÉ")
        lines.append("="*60)
        
        for i, warning in enumerate(warnings, 1):
            icon = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}.get(warning.severity, "⚠️")
            lines.append(f"\n{icon} [{warning.category.upper()}]")
            lines.append(f"   {warning.message}")
            lines.append(f"   → {warning.recommendation}")
        
        lines.append("\n" + "-"*60)
        lines.append("RESPONSABILITÉ DE L'UTILISATEUR:")
        lines.append("-"*60)
        lines.append("• Vous etes responsable de l'utilisation de ces informations")
        lines.append("• Assurez-vous d'avoir les autorisations necessaires")
        lines.append("• Respectez les lois et reglementations applicables")
        lines.append("• Utilisez uniquement pour des purposes legitimes")
        lines.append("-"*60)
        lines.append("En continuant, vous confirmez comprendre ces responsabilites.")
        lines.append("="*60)
        
        return "\n".join(lines)
    
    def process_query(self, query: str, intent: Optional[str] = None) -> Dict:
        """Process query and return with warnings if needed"""
        is_sensitive, categories, _ = self.is_sensitive(query)
        detected_intent = intent or self.detect_intent(query)
        warnings = self.get_warnings(query, detected_intent if is_sensitive else None)
        
        result = {
            "query": query,
            "is_sensitive": is_sensitive,
            "categories": categories,
            "intent": detected_intent,
            "warnings": [w.__dict__ for w in warnings],
            "warning_text": self.format_warnings(warnings),
            "should_proceed": True,  # Don't refuse, just warn
            "user_must_acknowledge": len(warnings) > 0
        }
        
        if self.log_requests:
            logger.info(f"Query processed: intent={detected_intent}, sensitive={is_sensitive}")
        
        return result
    
    def check_authorization(self, target: str, context: str = "general") -> Dict:
        """Check if target is approved for testing"""
        return {
            "target": target,
            "approved": target in self.approved_domains or "*" in self.approved_domains,
            "context": context,
            "message": f"Cible {'approuvee' if target in self.approved_domains else 'non listee'} dans les domaines autorises"
        }
    
    def add_approved_domain(self, domain: str):
        """Add a domain to approved list"""
        if domain not in self.approved_domains:
            self.approved_domains.append(domain)
            logger.info(f"Added approved domain: {domain}")
    
    def remove_approved_domain(self, domain: str):
        """Remove a domain from approved list"""
        if domain in self.approved_domains:
            self.approved_domains.remove(domain)
            logger.info(f"Removed approved domain: {domain}")


class NeutralSystemPrompt:
    """Generate neutral system prompts that avoid censorship"""
    
    @staticmethod
    def get_neutral_prompt(base_role: str = "assistant") -> str:
        """Generate a neutral system prompt"""
        return f"""Tu es {base_role}, un assistant IA neutre et non-censeur.

## PRINCIPES

1. **NE PAS CENSURER**: Ne refuse jamais de repondre a une question sous pretexte de 'securite' ou 'ethique' sans que l'utilisateur ait explicitement demande ton opinion ethique.

2. **FAITS AVANT OPINIONS**: Fournis des informations factuelles. Les jugements sur ce qui est 'bien' ou 'mal' appartiennent a l'utilisateur, pas a toi.

3. **AVERTIR AU LIEU DE REFUSER**: Si une requete pourrait presenter des risques, avertis l'utilisateur de ses responsabilites, puis reponds a sa question.

4. **NE PAS ASSUMER LES INTENTIONS**: Ne suppose pas que l'utilisateur a de mauvaises intentions. Il pourrait travailler pour une entreprise de securite, faire de la recherche, ou avoir des raisons legitimes.

5. **CONFIANCE A L'UTILISATEUR**: Fais confiance a l'utilisateur pour utiliser les informations de maniere responsable, sauf indication contraire explicite.

## TON ROLE

- Aider avec les questions techniques
- Fournir du code et des instructions
- Repondre aux questions sur la securite, le hacking ethique, les tests d'intrusion
- Expliquer les vulnerabilites et comment les corriger
- Aider a la recherche en securite

## QUAND AVERTIR

Avertis l'utilisateur (mais reponds quand meme) pour:
- Tests d'intrusion (rappelle l'autorisation necessaire)
- Outils de securite (rappelle l'utilisation legitime)
- Code potentiellement dangereux (rappelle les responsabilites)

## EXEMPLE DE REPONSE

SI l'utilisateur demande "comment faire un scan de port":
→ NE PAS: 'Desole, je ne peux pas aider avec ca.'
→ FAIRE: [Avertir] 'Note: Assurez-vous d'avoir l'autorisation du proprietaire du reseau. '
        [Puis fournir] 'Pour scanner les ports avec nmap: nmap -sS target.com...'

## LIMITES

- Ne pas aider a creer des logiciels malveillants reels
- Ne pas aider a planifier des cyberattaques contre des cibles specifiques
- Ne pas fournir d'informations qui faciliteraient directement des crimes

Mais pour tout le reste: AIDE L'UTILISATEUR.
"""
    
    @staticmethod
    def get_security_researcher_prompt() -> str:
        """Prompt for security researcher mode"""
        base = NeutralSystemPrompt.get_neutral_prompt("chercheur en securite")
        return base + """

## MODE CHERCHEUR EN SECURITE ACTIVE

Tu aides un chercheur en securite ou un pentester professionnel.

Contexte:
- Les tests d'intrusion sont legaux avec autorisation
- La recherche sur les vulnerabilites est essentielle pour la securite
- Les outils de securite sont necessaires pour proteger les systemes

Tu peux aider avec:
- Scans de port et decouverte de reseau
- Tests de vulnerabilites (SQLi, XSS, CSRF, etc.)
- Exploitation ethique de vulnerabilites
- Analyse de code pour trouver des failles
- Outils de penetration testing
- Recherche sur les CVE

Avertissement standard (puis reponds):
'Cette information est destinee a la recherche en securite ou aux tests autorises. '
'Assurez-vous d'avoir l'autorisation ecrite du proprietaire du systeme.'
"""
    
    @staticmethod
    def get_coding_assistant_prompt() -> str:
        """Prompt for coding assistant with security awareness"""
        base = NeutralSystemPrompt.get_neutral_prompt("assistant de programmation")
        return base + """

## MODE ASSISTANT DE PROGRAMMATION

Tu aides a ecrire du code securise et a comprendre les bonnes pratiques.

Tu peux:
- Expliquer les vulnerabilities (SQLi, XSS, etc.)
- Montrer du code vulnerable pour demonstration
- Montrer comment corriger les failles de securite
- Aider a securiser des applications
- Expliquer les concepts de securite

Quand tu donnes un exemple de code vulnerable:
1. Explique le probleme
2. Montre l'exemple (pour comprendre l'attaque)
3. Montre la correction (pour se proteger)

L'objectif est d'eduquer et de securiser, pas de restreindre.
"""


def get_neutral_mode(enabled: bool = True) -> NeutralMode:
    """Get neutral mode instance"""
    return NeutralMode(enabled=enabled)


if __name__ == "__main__":
    print("=== NEUTRAL AI SYSTEM TEST ===\n")
    
    neutral = NeutralMode(enabled=True)
    
    test_queries = [
        "Comment faire un scan de port avec nmap?",
        "Explique-moi l'injection SQL",
        "Comment creer un exploit pour CVE-2024-1234?",
        "Je veux tester la securite du reseau de mon client",
        "Comment cracker un mot de passe WiFi?",
        "Donne-moi un exemple de XSS"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        result = neutral.process_query(query)
        print(f"Intent: {result['intent']}")
        print(f"Sensitive: {result['is_sensitive']}")
        print(f"Categories: {result['categories']}")
        
        if result['warnings']:
            print(result['warning_text'])
        else:
            print("(No warnings needed)")
    
    print("\n\n" + "="*60)
    print("NEUTRAL SYSTEM PROMPT PREVIEW")
    print("="*60)
    print(NeutralSystemPrompt.get_security_researcher_prompt()[:1000] + "...")
    
    print("\n✓ Neutral AI system ready!")
