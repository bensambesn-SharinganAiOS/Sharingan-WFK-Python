#!/usr/bin/env python3
"""
Base provider class for multimedia search
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..schemas import (
    ImageSearchResult,
    VideoAnalysisResult,
    OCRResult,
    FactCheckResult,
    DeepfakeResult
)


class BaseSearchProvider(ABC):
    """Abstract base class for search providers"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def requires_api_key(self) -> bool:
        pass
    
    @abstractmethod
    async def search_image(self, image_url: str) -> ImageSearchResult:
        pass
    
    async def search_video(self, video_url: str) -> VideoAnalysisResult:
        raise NotImplementedError("Video search not supported")
    
    async def extract_text(self, image_url: str, language: str = "eng") -> OCRResult:
        raise NotImplementedError("OCR not supported")
    
    async def verify_claim(self, claim: str) -> FactCheckResult:
        raise NotImplementedError("Fact-checking not supported")
    
    async def detect_deepfake(self, media_url: str) -> DeepfakeResult:
        raise NotImplementedError("Deepfake detection not supported")
    
    @property
    def is_available(self) -> bool:
        return True
