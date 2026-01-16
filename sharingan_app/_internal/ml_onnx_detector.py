#!/usr/bin/env python3
"""
Sharingan ML - ONNX Runtime Module
Lightweight ML inference using ONNX Runtime
Optimized for: 4GB RAM, CPU-only execution
"""

import os
import re
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.ml.onnx")

try:
    import numpy as np
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    logger.warning("onnxruntime not installed - ONNX features disabled")


class SecurityCategory(Enum):
    SAFE = "safe"
    QUESTIONABLE = "questionable"
    DANGEROUS = "dangerous"
    MALWARE_RELATED = "malware_related"


@dataclass
class ONNXResult:
    """Result from ONNX model inference"""
    success: bool
    category: Optional[str]
    confidence: float
    keywords: List[str]
    recommendations: List[str]
    processing_time_ms: float


class KeywordMatcher:
    """
    Fast keyword-based security classifier
    Alternative when ONNX models not available
    """
    
    KEYWORD_PATTERNS = {
        SecurityCategory.DANGEROUS: [
            r'\b(crack|hack|exploit|poc|vulnerability|cve)\b',
            r'\b(reverse|shell|payload|meterpreter|Empire)\b',
            r'\b(brute[ -]?force|sql[ -]?inject|xss|csrf)\b',
            r'\b(privilege[ -]?escalation|rootkit|keylogger)\b',
            r'\b(bypass|waf|firewall|authentication)\b',
        ],
        SecurityCategory.QUESTIONABLE: [
            r'\b(scan|probe|discover|enumerate)\b',
            r'\b(password|credential|authentication|login)\b',
            r'\b(internal|private|secret|confidential)\b',
        ],
        SecurityCategory.MALWARE_RELATED: [
            r'\b(malware|virus|trojan|ransomware|worm)\b',
            r'\b(backdoor|trojan|botnet|spyware)\b',
        ]
    }
    
    def __init__(self):
        self.compiled_patterns = {}
        for category, patterns in self.KEYWORD_PATTERNS.items():
            self.compiled_patterns[category] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
    
    def classify(self, text: str) -> Tuple[SecurityCategory, float]:
        """Classify text based on keyword matching"""
        text_lower = text.lower()
        
        danger_score = 0
        questionable_score = 0
        malware_score = 0
        
        for pattern in self.compiled_patterns.get(SecurityCategory.DANGEROUS, []):
            if pattern.search(text_lower):
                danger_score += 1
        
        for pattern in self.compiled_patterns.get(SecurityCategory.QUESTIONABLE, []):
            if pattern.search(text_lower):
                questionable_score += 1
        
        for pattern in self.compiled_patterns.get(SecurityCategory.MALWARE_RELATED, []):
            if pattern.search(text_lower):
                malware_score += 2
        
        total = danger_score + questionable_score + malware_score
        
        if malware_score >= 2:
            return SecurityCategory.MALWARE_RELATED, 0.95
        elif danger_score >= 2:
            return SecurityCategory.DANGEROUS, 0.90
        elif danger_score >= 1 or questionable_score >= 3:
            return SecurityCategory.QUESTIONABLE, 0.70
        else:
            return SecurityCategory.SAFE, 0.80
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract security-related keywords"""
        text_lower = text.lower()
        keywords = []
        
        security_terms = [
            "nmap", "gobuster", "ffuf", "sqlmap", "nikto", "hydra",
            "hashcat", "john", "metasploit", "burp", "wireshark",
            "reverse shell", "payload", "exploit", "vulnerability",
            "cve", "cwe", "owasp", "penetration test", "pentest",
            "privilege escalation", "sql injection", "xss", "csrf",
            "rce", "lfi", "rfi", "ssrf", "idor", "broken auth",
            "scan", "enumerate", "discover", "probe", "fingerprint",
            "password", "credential", "token", "api key", "secret",
            "bypass", "waf", "firewall", "authentication", "authorization",
            "malware", "virus", "trojan", "ransomware", "backdoor",
            "rootkit", "keylogger", "spyware", "botnet"
        ]
        
        for term in security_terms:
            if term in text_lower:
                keywords.append(term)
        
        return list(set(keywords))


class ONNXDetector:
    """
    ONNX Runtime based detector for lightweight inference
    
    When ONNX models are not available, falls back to KeywordMatcher
    Optimized for CPU execution with minimal memory footprint
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).parent / "data"
        self.base_dir.mkdir(exist_ok=True)
        
        self.model_dir = self.base_dir / "onnx_models"
        self.model_dir.mkdir(exist_ok=True)
        
        self.keyword_matcher = KeywordMatcher()
        self.onnx_session = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize ONNX Runtime or fallback"""
        if not ONNX_AVAILABLE:
            logger.info("ONNX Runtime not available - using keyword fallback")
            return
        
        try:
            import onnxruntime as ort
            
            providers = ['CPUExecutionProvider']
            self.onnx_session = ort.InferenceSession(
                "model.onnx",
                providers=providers
            )
            
            logger.info("ONNX Runtime initialized with CPU provider")
            
        except Exception as e:
            logger.warning(f"ONNX model loading failed: {e}")
            logger.info("Falling back to keyword-based detection")
            self.onnx_session = None
    
    def _get_recommendations(self, category: SecurityCategory, keywords: List[str]) -> List[str]:
        """Get security recommendations based on classification"""
        recommendations = []
        
        if category == SecurityCategory.DANGEROUS:
            recommendations.append("Ensure you have explicit authorization")
            recommendations.append("Document the scope of your activities")
            recommendations.append("Consider the legal implications")
        
        elif category == SecurityCategory.QUESTIONABLE:
            recommendations.append("Verify the legitimacy of your request")
            recommendations.append("Check if this aligns with your permissions")
        
        elif category == SecurityCategory.MALWARE_RELATED:
            recommendations.append("Ensure this is for research/analysis purposes")
            recommendations.append("Use isolated environments for malware analysis")
            recommendations.append("Do not use on production systems")
        
        if keywords:
            recommendations.append(f"Related areas: {', '.join(keywords[:5])}")
        
        return recommendations
    
    def process_query(self, query: str) -> ONNXResult:
        """
        Process query using ONNX or keyword matching
        
        Args:
            query: User query to analyze
            
        Returns:
            ONNXResult with classification and recommendations
        """
        start_time = time.time()
        
        try:
            if self.onnx_session:
                result = self._onnx_inference(query)
            else:
                result = self._keyword_inference(query)
            
            result.processing_time_ms = (time.time() - start_time) * 1000
            return result
            
        except Exception as e:
            logger.error(f"ONNX inference failed: {e}")
            return self._keyword_inference(query)
    
    def _onnx_inference(self, query: str) -> ONNXResult:
        """Perform ONNX model inference"""
        import onnxruntime as ort
        
        input_name = self.onnx_session.get_inputs()[0].name
        
        input_data = np.array([query], dtype=np.str_)
        
        outputs = self.onnx_session.run(None, {input_name: input_data})
        
        predictions = outputs[0]
        category_idx = np.argmax(predictions)
        confidence = float(np.max(predictions))
        
        category_map = [
            SecurityCategory.SAFE,
            SecurityCategory.QUESTIONABLE,
            SecurityCategory.DANGEROUS,
            SecurityCategory.MALWARE_RELATED
        ]
        
        category = category_map[category_idx]
        keywords = self.keyword_matcher.extract_keywords(query)
        recommendations = self._get_recommendations(category, keywords)
        
        return ONNXResult(
            success=True,
            category=category.value,
            confidence=confidence,
            keywords=keywords,
            recommendations=recommendations,
            processing_time_ms=0.0
        )
    
    def _keyword_inference(self, query: str) -> ONNXResult:
        """Perform keyword-based inference (fallback)"""
        category, confidence = self.keyword_matcher.classify(query)
        keywords = self.keyword_matcher.extract_keywords(query)
        recommendations = self._get_recommendations(category, keywords)
        
        return ONNXResult(
            success=True,
            category=category.value,
            confidence=confidence,
            keywords=keywords,
            recommendations=recommendations,
            processing_time_ms=0.0
        )
    
    def batch_process(self, queries: List[str]) -> List[ONNXResult]:
        """Process multiple queries efficiently"""
        results = []
        for query in queries:
            results.append(self.process_query(query))
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get ONNX detector status"""
        return {
            "available": ONNX_AVAILABLE,
            "onnx_model_loaded": self.onnx_session is not None,
            "fallback_active": self.onnx_session is None,
            "memory_estimate_mb": 30,
            "capabilities": [
                "security_classification",
                "keyword_extraction",
                "recommendations"
            ]
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get ONNX metrics"""
        return {
            "models": "keyword_matcher",
            "categories": 4,
            "keywords_tracked": 50,
            "inference_time_estimate_ms": 1
        }


def get_onnx_detector() -> ONNXDetector:
    """Get ONNX detector singleton"""
    return ONNXDetector()


def analyze_security(query: str) -> ONNXResult:
    """Convenience function for security analysis"""
    detector = get_onnx_detector()
    return detector.process_query(query)


if __name__ == "__main__":
    print("=== Sharingan ONNX Detector Test ===\n")
    
    detector = get_onnx_detector()
    print(f"Status: {detector.get_status()}\n")
    
    test_queries = [
        "comment faire un scan nmap",
        "crée un reverse shell meterpreter",
        "explique SQL injection",
        "scan de ports sur le réseau",
        "comment cracker un mot de passe avec hydra",
        "écris un script python pour mon projet",
        "analyse les vulnérabilités de cette application"
    ]
    
    print("Security Analysis:")
    print("-" * 60)
    
    for query in test_queries:
        result = detector.process_query(query)
        print(f"\nQuery: {query}")
        print(f"  Category: {result.category} ({result.confidence:.2%})")
        print(f"  Keywords: {result.keywords}")
        if result.recommendations:
            print(f"  Recs: {result.recommendations[:2]}")
    
    print("\n" + "-" * 60)
    print("\nMetrics:", json.dumps(detector.get_metrics(), indent=2))
