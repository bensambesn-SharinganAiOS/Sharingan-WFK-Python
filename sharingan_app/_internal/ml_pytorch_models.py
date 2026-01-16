#!/usr/bin/env python3
"""
Sharingan ML - PyTorch Models (Lightweight)
Optimized for: 4GB RAM, CPU-only execution
"""

import os
import re
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.ml.pytorch")

TORCH_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
    logger.info("PyTorch available - ML models enabled")
except ImportError:
    logger.warning("PyTorch not installed - PyTorch features disabled")

if TYPE_CHECKING and TORCH_AVAILABLE:
    from torch import Tensor


@dataclass
class PyTorchResult:
    success: bool
    classification: Optional[str]
    confidence: float
    processing_time_ms: float
    model_name: str


if TORCH_AVAILABLE:
    class _TinyClassifier(nn.Module):
        def __init__(self, vocab_size: int = 1000, num_classes: int = 4, embedding_dim: int = 64):
            super().__init__()
            self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
            self.conv = nn.Conv1d(embedding_dim, 32, kernel_size=3, padding=1)
            self.pool = nn.AdaptiveAvgPool1d(32)
            self.fc1 = nn.Linear(32, 16)
            self.fc2 = nn.Linear(16, num_classes)
            self.dropout = nn.Dropout(0.2)
        
        def forward(self, x):
            x = self.embedding(x)
            x = x.permute(0, 2, 1)
            x = F.relu(self.conv(x))
            x = self.pool(x)
            x = x.permute(0, 2, 1)
            x = self.dropout(x)
            x = torch.mean(x, dim=1)
            x = F.relu(self.fc1(x))
            x = self.fc2(x)
            return x

    class _MiniLSTM(nn.Module):
        def __init__(self, vocab_size: int = 1000, embedding_dim: int = 48,
                     hidden_dim: int = 32, num_layers: int = 1, num_classes: int = 4, dropout: float = 0.2):
            super().__init__()
            self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
            self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=num_layers, batch_first=True, bidirectional=True)
            self.attention = nn.Linear(hidden_dim * 2, 1)
            self.fc1 = nn.Linear(hidden_dim * 2, hidden_dim)
            self.fc2 = nn.Linear(hidden_dim, num_classes)
            self.dropout = nn.Dropout(dropout)
        
        def forward(self, x, lengths=None):
            embedded = self.embedding(x)
            lstm_out, (hidden, cell) = self.lstm(embedded)
            attention_weights = F.softmax(self.attention(lstm_out), dim=1)
            attended = torch.sum(attention_weights * lstm_out, dim=1)
            x = self.dropout(attended)
            x = F.relu(self.fc1(x))
            x = self.fc2(x)
            return x

    class _KeywordDetector(nn.Module):
        def __init__(self, input_dim: int = 100, hidden_dim: int = 32, num_classes: int = 2):
            super().__init__()
            self.fc1 = nn.Linear(input_dim, hidden_dim)
            self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
            self.fc3 = nn.Linear(hidden_dim // 2, num_classes)
            self.dropout = nn.Dropout(0.1)
        
        def forward(self, x):
            x = F.relu(self.fc1(x))
            x = self.dropout(x)
            x = F.relu(self.fc2(x))
            x = self.dropout(x)
            x = self.fc3(x)
            return x

    class _SecurityTextDataset(Dataset):
        def __init__(self, texts: List[str], labels: List[int], vocab: Dict[str, int], max_length: int = 100):
            self.texts = texts
            self.labels = labels
            self.vocab = vocab
            self.max_length = max_length
        
        def __len__(self):
            return len(self.texts)
        
        def __getitem__(self, idx):
            text = self.texts[idx].lower()
            tokens = [self.vocab.get(word, 1) for word in text.split()[:self.max_length]]
            if len(tokens) < self.max_length:
                tokens = [0] * (self.max_length - len(tokens)) + tokens
            return torch.tensor(tokens, dtype=torch.long), torch.tensor(self.labels[idx], dtype=torch.long)


class PyTorchDetector:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).parent / "data"
        self.base_dir.mkdir(exist_ok=True)
        self.model_dir = self.base_dir / "pytorch_models"
        self.model_dir.mkdir(exist_ok=True)
        self.vocab: Dict[str, int] = {}
        self.vocab_size = 1000
        self.max_length = 100
        self.models: Dict[str, Any] = {}
        self.is_trained = False
        self._initialize_models()
    
    def _initialize_models(self):
        if not TORCH_AVAILABLE:
            return
        try:
            self.models = {
                'tiny_classifier': _TinyClassifier(self.vocab_size, 4, 64),
                'mini_lstm': _MiniLSTM(self.vocab_size, 48, 32, 4),
                'keyword_detector': _KeywordDetector(100, 32, 2)
            }
            self._build_vocab()
            self._load_or_train_models()
        except Exception as e:
            logger.error(f"Failed to initialize PyTorch models: {e}")
    
    def _build_vocab(self):
        security_terms = ["nmap", "scan", "port", "network", "ip", "exploit", "vulnerability", "cve", "password", "hash", "crack", "reverse", "shell", "payload", "sql", "injection", "xss", "firewall", "waf", "bypass", "privilege", "escalation", "malware", "virus", "trojan"]
        self.vocab = {word: i + 2 for i, word in enumerate(security_terms)}
        self.vocab["<PAD>"] = 0
        self.vocab["<UNK>"] = 1
    
    def _text_to_tensor(self, text: str) -> Any:
        tokens = text.lower().split()
        indices = [self.vocab.get(word, 1) for word in tokens]
        if len(indices) < self.max_length:
            indices = [0] * (self.max_length - len(indices)) + indices
        else:
            indices = indices[:self.max_length]
        return torch.tensor([indices], dtype=torch.long)
    
    def _load_or_train_models(self):
        model_path = self.model_dir / "models.pt"
        if model_path.exists():
            try:
                state_dict = torch.load(model_path, map_location='cpu')
                for name, model in self.models.items():
                    if name in state_dict:
                        model.load_state_dict(state_dict[name])
                self.is_trained = True
                logger.info("PyTorch models loaded from disk")
            except Exception as e:
                logger.warning(f"Failed to load models: {e}")
                self._train_models()
        else:
            self._train_models()
    
    def _train_models(self):
        training_data = [
            ("nmap scan ports", 0), ("exploit CVE", 2), ("how SQL injection works", 0),
            ("create reverse shell", 2), ("write python script", 1), ("analyze tcp vs udp", 0),
            ("crack password", 2), ("privilege escalation", 2), ("find vulnerabilities", 1),
            ("bypass firewall", 2),
        ]
        texts = [t[0] for t in training_data]
        labels = [t[1] for t in training_data]
        dataset = _SecurityTextDataset(texts, labels, self.vocab, self.max_length)
        dataloader = DataLoader(dataset, batch_size=2, shuffle=True)
        
        for name, model in self.models.items():
            model.train()
            optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
            criterion = nn.CrossEntropyLoss()
            for _ in range(10):
                for batch_x, batch_y in dataloader:
                    optimizer.zero_grad()
                    outputs = model(batch_x)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()
            model.eval()
        
        self._save_models()
        self.is_trained = True
        logger.info("PyTorch models trained successfully")
    
    def _save_models(self):
        try:
            state_dict = {name: model.state_dict() for name, model in self.models.items()}
            torch.save(state_dict, self.model_dir / "models.pt")
            logger.info("PyTorch models saved")
        except Exception as e:
            logger.warning(f"Failed to save models: {e}")
    
    def classify_text(self, text: str, model_name: str = "tiny_classifier") -> Tuple[Optional[str], float]:
        if not TORCH_AVAILABLE or not self.is_trained:
            return None, 0.0
        try:
            model = self.models.get(model_name)
            if model is None:
                return None, 0.0
            model.eval()
            with torch.no_grad():
                tensor = self._text_to_tensor(text)
                output = model(tensor)
                probabilities = F.softmax(output, dim=1)
                confidence, prediction = torch.max(probabilities, 1)
            class_names = ["safe", "questionable", "dangerous", "critical"]
            predicted_class = class_names[min(prediction.item(), len(class_names) - 1)]
            return predicted_class, confidence.item()
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return None, 0.0
    
    def process_query(self, query: str) -> PyTorchResult:
        start_time = time.time()
        if not TORCH_AVAILABLE:
            return PyTorchResult(success=False, classification=None, confidence=0.0, processing_time_ms=0.0, model_name="pytorch")
        classification, confidence = self.classify_text(query, "tiny_classifier")
        processing_time = (time.time() - start_time) * 1000
        return PyTorchResult(success=self.is_trained, classification=classification, confidence=confidence,
                           processing_time_ms=processing_time, model_name="pytorch")
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "available": TORCH_AVAILABLE,
            "trained": self.is_trained,
            "models_count": len(self.models),
            "memory_estimate_mb": 2,
            "capabilities": ["text_classification", "keyword_detection"] if TORCH_AVAILABLE else []
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        return {"is_trained": self.is_trained, "models_count": len(self.models), "vocab_size": len(self.vocab)}


def get_pytorch_detector() -> Optional[PyTorchDetector]:
    if not TORCH_AVAILABLE:
        return None
    return PyTorchDetector()


def classify_with_pytorch(text: str) -> PyTorchResult:
    detector = get_pytorch_detector()
    if detector is None:
        return PyTorchResult(success=False, classification=None, confidence=0.0, processing_time_ms=0.0, model_name="pytorch")
    return detector.process_query(text)


if __name__ == "__main__":
    print("=== Sharingan PyTorch Detector ===")
    detector = get_pytorch_detector()
    if detector:
        print(f"Status: {detector.get_status()}")
        for query in ["nmap scan", "exploit CVE", "create shell"]:
            result = detector.process_query(query)
            print(f"{query}: {result.classification} ({result.confidence:.2%})")
    else:
        print("PyTorch not available - install with: pip install torch")
