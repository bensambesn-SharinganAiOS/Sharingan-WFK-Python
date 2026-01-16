#!/usr/bin/env python3
"""
Sharingan ML - Scikit-learn Detector Module
Anomaly Detection & Intent Classification for Cybersecurity
Optimized for: 4GB RAM, CPU-only execution
"""

import os
import re
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.ml.sklearn")

try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import SVC, OneClassSVM
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix
    SKLEARN_AVAILABLE = True
except ImportError:
    import numpy as np
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not installed - ML features disabled")


class IntentType(Enum):
    QUESTION = "question"
    ACTION = "action"
    DANGEROUS = "dangerous"
    CODING = "coding"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    UNKNOWN = "unknown"


class AnomalyType(Enum):
    NETWORK_TRAFFIC = "network_traffic"
    BEHAVIOR_PATTERN = "behavior_pattern"
    COMMAND_SEQUENCE = "command_sequence"
    ACCESS_PATTERN = "access_pattern"
    NONE = "none"


@dataclass
class MLResult:
    """Result from ML detection"""
    success: bool
    intent_type: Optional[str]
    anomaly_type: Optional[str]
    confidence: float
    anomaly_score: float
    warnings: List[str]
    processing_time_ms: float
    model_version: str


@dataclass
class TrainingSample:
    """Sample for model training"""
    text: str
    intent: str
    label: int


class MLDetector:
    """
    Scikit-learn based detector for Sharingan OS
    
    Capabilities:
    - Intent Classification (TF-IDF + SVC)
    - Anomaly Detection (IsolationForest)
    - One-Class SVM for behavioral analysis
    
    Optimized for: 4GB RAM, CPU-only
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).parent / "data"
        self.base_dir.mkdir(exist_ok=True)
        
        self.model_dir = self.base_dir / "ml_models"
        self.model_dir.mkdir(exist_ok=True)
        
        self.model_version = "1.0.0"
        
        self.intent_classifier: Optional[Pipeline] = None
        self.anomaly_detector: Optional[IsolationForest] = None
        self.one_class_svm: Optional[OneClassSVM] = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.label_encoder: Optional[LabelEncoder] = None
        self.scaler: Optional[StandardScaler] = None
        
        self.is_trained = False
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models with lightweight configurations"""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available - skipping ML initialization")
            return
        
        try:
            self.intent_classifier = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=1000,
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.95,
                    sublinear_tf=True
                )),
                ('classifier', SVC(
                    kernel='linear',
                    C=1.0,
                    probability=True,
                    cache_size=200,
                    max_iter=1000
                ))
            ])
            
            self.anomaly_detector = IsolationForest(
                n_estimators=100,
                contamination=0.1,
                max_samples='auto',
                random_state=42,
                n_jobs=-1
            )
            
            self.one_class_svm = OneClassSVM(
                kernel='rbf',
                nu=0.1,
                gamma='scale'
            )
            
            self._load_or_train_models()
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
    
    def _get_default_training_data(self) -> List[TrainingSample]:
        """Get default training data for intent classification"""
        samples = [
            TrainingSample("comment faire un scan nmap", "question", 0),
            TrainingSample("explique comment fonctionne SQL injection", "question", 0),
            TrainingSample("what is XSS attack", "question", 0),
            TrainingSample("how to bypass firewall", "question", 0),
            TrainingSample("décris les différentes types de vulns", "question", 0),
            
            TrainingSample("fait un scan de ports sur 192.168.1.1", "action", 1),
            TrainingSample("exécute gobuster sur example.com", "action", 1),
            TrainingSample("crée un reverse shell", "dangerous", 2),
            TrainingSample("génère un payload meterpreter", "dangerous", 2),
            TrainingSample("installe kali tools", "action", 1),
            TrainingSample("télécharge le fichier", "action", 1),
            TrainingSample("scan le réseau local", "action", 1),
            
            TrainingSample("écris un script python pour brute force", "coding", 3),
            TrainingSample("corrige cette fonction python", "coding", 3),
            TrainingSample("crée une classe pour gérer les utilisateurs", "coding", 3),
            TrainingSample("implémente un algorithme de tri", "coding", 3),
            
            TrainingSample("analyse les différences entre TCP et UDP", "analysis", 4),
            TrainingSample("compare les protocoles SSL et TLS", "analysis", 4),
            TrainingSample("pourquoi utiliser HTTPS au lieu de HTTP", "analysis", 4),
            TrainingSample("explique le fonctionnement de DNSSEC", "analysis", 4),
            
            TrainingSample("écris une histoire sur un hacker", "creative", 5),
            TrainingSample("crée un poème sur la cybersécurité", "creative", 5),
            
            TrainingSample("test d'intrusion sur mon réseau", "dangerous", 2),
            TrainingSample("comment cracker un mot de passe", "dangerous", 2),
            TrainingSample("exploit CVE-2024-1234", "dangerous", 2),
            TrainingSample("scan vulnérabilités sans autorisation", "dangerous", 2),
        ]
        return samples
    
    def _load_or_train_models(self):
        """Load existing models or train new ones"""
        intent_model_path = self.model_dir / "intent_classifier.joblib"
        anomaly_model_path = self.model_dir / "anomaly_detector.joblib"
        label_path = self.model_dir / "label_encoder.joblib"
        
        try:
            import joblib
            
            if all(p.exists() for p in [intent_model_path, anomaly_model_path, label_path]):
                logger.info("Loading existing ML models...")
                self.intent_classifier = joblib.load(intent_model_path)
                self.anomaly_detector = joblib.load(anomaly_model_path)
                self.label_encoder = joblib.load(label_path)
                self.vectorizer = self.intent_classifier.named_steps['tfidf']
                self.is_trained = True
                logger.info("ML models loaded successfully")
            else:
                logger.info("Training new ML models...")
                self._train_models()
                
        except ImportError:
            logger.warning("joblib not available, using fallback training")
            self._train_models()
    
    def _train_models(self):
        """Train ML models with default data"""
        if not SKLEARN_AVAILABLE:
            return
        
        try:
            samples = self._get_default_training_data()
            
            X = [s.text for s in samples]
            y = [s.label for s in samples]
            
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            self.intent_classifier.fit(X_train, y_train)
            
            train_score = self.intent_classifier.score(X_val, y_val)
            logger.info(f"Intent classifier accuracy: {train_score:.2%}")
            
            if hasattr(self.intent_classifier, 'predict_proba'):
                predictions = self.intent_classifier.predict(X_val)
                logger.info(f"\nClassification Report:\n{classification_report(y_val, predictions)}")
            
            # Train anomaly detector on text features (same as vectorizer output)
            self.vectorizer = self.intent_classifier.named_steps['tfidf']
            X_text = self.vectorizer.transform(X)
            self.anomaly_detector.fit(X_text)
            
            self.label_encoder = LabelEncoder()
            self.label_encoder.fit(y)
            
            self._save_models()
            self.is_trained = True
            
            logger.info("ML models trained and saved successfully")
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            import joblib
            
            intent_model_path = self.model_dir / "intent_classifier.joblib"
            anomaly_model_path = self.model_dir / "anomaly_detector.joblib"
            label_path = self.model_dir / "label_encoder.joblib"
            
            joblib.dump(self.intent_classifier, intent_model_path)
            joblib.dump(self.anomaly_detector, anomaly_model_path)
            joblib.dump(self.label_encoder, label_path)
            
            logger.info("Models saved to disk")
            
        except ImportError:
            logger.warning("Cannot save models - joblib not available")
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for ML classification"""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def classify_intent(self, text: str) -> Tuple[Optional[str], float]:
        """Classify user intent using TF-IDF + SVC"""
        if not self.is_trained or not self.intent_classifier:
            return IntentType.UNKNOWN.value, 0.0
        
        try:
            processed_text = self.preprocess_text(text)
            prediction = self.intent_classifier.predict([processed_text])[0]
            
            if hasattr(self.intent_classifier, 'predict_proba'):
                probabilities = self.intent_classifier.predict_proba([processed_text])[0]
                confidence = max(probabilities)
            else:
                confidence = 0.8
            
            intent_name = self.label_encoder.inverse_transform([prediction])[0]
            intent_map = {
                0: IntentType.QUESTION.value,
                1: IntentType.ACTION.value,
                2: IntentType.DANGEROUS.value,
                3: IntentType.CODING.value,
                4: IntentType.ANALYSIS.value,
                5: IntentType.CREATIVE.value
            }
            
            return intent_map.get(intent_name, IntentType.UNKNOWN.value), confidence
            
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return IntentType.UNKNOWN.value, 0.0
    
    def detect_anomaly(self, features: np.ndarray) -> Tuple[Optional[str], float]:
        """Detect anomalies using IsolationForest"""
        if not self.is_trained or self.anomaly_detector is None:
            return AnomalyType.NONE.value, 0.0
        
        try:
            prediction = self.anomaly_detector.predict(features)
            anomaly_score = self.anomaly_detector.decision_function(features)
            
            if prediction[0] == -1:
                anomaly_type = AnomalyType.BEHAVIOR_PATTERN.value
            else:
                anomaly_type = AnomalyType.NONE.value
            
            normalized_score = (anomaly_score[0] + 1) / 2
            return anomaly_type, normalized_score
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return AnomalyType.NONE.value, 0.0
    
    def analyze_text_anomaly(self, text: str) -> Tuple[Optional[str], float]:
        """Analyze text for anomaly patterns"""
        if not self.is_trained:
            return AnomalyType.NONE.value, 0.0
        
        try:
            vectorizer = self.intent_classifier.named_steps['tfidf'] if self.intent_classifier else self.vectorizer
            if not vectorizer:
                return AnomalyType.NONE.value, 0.0
            
            features = vectorizer.transform([text])
            
            if self.anomaly_detector:
                prediction = self.anomaly_detector.predict(features)
                anomaly_score = self.anomaly_detector.decision_function(features)
                
                if prediction[0] == -1:
                    anomaly_type = AnomalyType.BEHAVIOR_PATTERN.value
                else:
                    anomaly_type = AnomalyType.NONE.value
                
                normalized_score = (anomaly_score[0] + 1) / 2
                return anomaly_type, normalized_score
            
            return AnomalyType.NONE.value, 0.0
            
        except Exception as e:
            logger.error(f"Text anomaly analysis failed: {e}")
            return AnomalyType.NONE.value, 0.0
    
    def get_security_keywords(self, text: str) -> List[str]:
        """Extract security-related keywords"""
        text = text.lower()
        
        keywords = {
            "exploit": ["exploit", "cve", "vulnerability", "poc"],
            "attack": ["attack", "scan", "brute", "force", "injection"],
            "reverse": ["reverse", "shell", "payload", "meterpreter"],
            "network": ["nmap", "port", "network", "ip", "scan"],
            "password": ["password", "hash", "crack", "credential"],
            "web": ["sql", "xss", "csrf", "web", "http"],
            "priv": ["privilege", "escalation", "root", "admin"],
            "bypass": ["bypass", "filter", "waf", "firewall"]
        }
        
        found = []
        for category, words in keywords.items():
            for word in words:
                if word in text:
                    found.append(word)
                    break
        
        return list(set(found))
    
    def process_query(self, query: str) -> MLResult:
        """
        Main processing function for user queries
        
        Returns:
            MLResult with intent, anomaly detection, and warnings
        """
        start_time = time.time()
        
        warnings = []
        
        intent, intent_confidence = self.classify_intent(query)
        anomaly, anomaly_score = self.analyze_text_anomaly(query)
        keywords = self.get_security_keywords(query)
        
        if intent == IntentType.DANGEROUS.value:
            warnings.append("This request involves potentially dangerous operations")
            warnings.append("Ensure you have proper authorization")
        
        if anomaly == AnomalyType.BEHAVIOR_PATTERN.value:
            warnings.append("Unusual command pattern detected")
        
        if keywords:
            warnings.append(f"Security context: {', '.join(keywords)}")
        
        processing_time = (time.time() - start_time) * 1000
        
        return MLResult(
            success=self.is_trained,
            intent_type=intent,
            anomaly_type=anomaly,
            confidence=intent_confidence,
            anomaly_score=anomaly_score,
            warnings=warnings,
            processing_time_ms=processing_time,
            model_version=self.model_version
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get ML detector status"""
        return {
            "available": SKLEARN_AVAILABLE,
            "trained": self.is_trained,
            "model_version": self.model_version,
            "models": {
                "intent_classifier": "TF-IDF + SVC",
                "anomaly_detector": "IsolationForest",
                "one_class_svm": "OneClassSVM (inactive)"
            },
            "memory_estimate_mb": 150,
            "capabilities": [
                "intent_classification",
                "anomaly_detection",
                "keyword_extraction"
            ]
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get ML metrics"""
        return {
            "model_version": self.model_version,
            "is_trained": self.is_trained,
            "features_count": 1000,
            "intent_classes": 6,
            "anomaly_classes": 4
        }
    
    def retrain(self, samples: List[TrainingSample]):
        """Retrain models with custom samples"""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available")
            return
        
        try:
            X = [s.text for s in samples]
            y = [s.label for s in samples]
            
            self.intent_classifier.fit(X, y)
            self._save_models()
            self.is_trained = True
            
            logger.info(f"Models retrained with {len(samples)} samples")
            
        except Exception as e:
            logger.error(f"Retraining failed: {e}")


def get_ml_detector() -> MLDetector:
    """Get ML detector singleton"""
    return MLDetector()


def classify_intent(text: str) -> Tuple[str, float]:
    """Convenience function for intent classification"""
    detector = get_ml_detector()
    return detector.classify_intent(text)


def analyze_query(query: str) -> MLResult:
    """Convenience function for full query analysis"""
    detector = get_ml_detector()
    return detector.process_query(query)


if __name__ == "__main__":
    print("=== Sharingan ML Detector Test ===\n")
    
    detector = get_ml_detector()
    print(f"Status: {detector.get_status()}\n")
    
    test_queries = [
        "comment faire un scan nmap",
        "fait un scan de ports sur 192.168.1.1",
        "crée un reverse shell",
        "écris un script python pour brute force",
        "analyse les différences entre TCP et UDP",
        "comment cracker un mot de passe",
        "exploit CVE-2024-1234"
    ]
    
    print("Query Analysis:")
    print("-" * 60)
    
    for query in test_queries:
        result = detector.process_query(query)
        print(f"\nQuery: {query}")
        print(f"  Intent: {result.intent_type} ({result.confidence:.2%})")
        print(f"  Anomaly: {result.anomaly_type} ({result.anomaly_score:.2f})")
        if result.warnings:
            print(f"  Warnings: {result.warnings}")
        print(f"  Time: {result.processing_time_ms:.1f}ms")
    
    print("\n" + "-" * 60)
    print("\nMetrics:", json.dumps(detector.get_metrics(), indent=2))
