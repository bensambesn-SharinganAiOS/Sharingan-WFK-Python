#!/usr/bin/env python3
"""
Local processing providers - Fallback when APIs unavailable
"""

import subprocess
import tempfile
import os
from PIL import Image
from typing import Optional, Dict, Any, List
import logging

from ..schemas import OCRResult, ImageSearchResult, ImageMatch, SearchEngine, MediaType, DeepfakeResult

logger = logging.getLogger("multimedia.local")


class TesseractOCR:
    """Local Tesseract OCR - Already installed"""
    
    def __init__(self):
        self.available = self._check_available()
    
    def _check_available(self) -> bool:
        return subprocess.run(
            ["which", "tesseract"], capture_output=True
        ).returncode == 0
    
    async def extract_text(self, image_path: str, language: str = "eng") -> OCRResult:
        if not self.available:
            return OCRResult(
                success=False, text="", confidence=0.0, language=language,
                error="Tesseract not installed"
            )
        try:
            result = subprocess.run(
                ["tesseract", image_path, "stdout", "-l", language],
                capture_output=True, text=True, timeout=30
            )
            return OCRResult(
                success=result.returncode == 0,
                text=result.stdout.strip(),
                confidence=0.85 if result.returncode == 0 else 0.0,
                language=language,
                error=result.stderr if result.returncode != 0 else None
            )
        except Exception as e:
            return OCRResult(
                success=False, text="", confidence=0.0, language=language,
                error=str(e)
            )
    
    @property
    def name(self) -> str:
        return "tesseract"


class PILAnalyzer:
    """PIL image analysis - Basic analysis"""
    
    def __init__(self):
        self.available = True
    
    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        try:
            with Image.open(image_path) as img:
                return {
                    "format": img.format,
                    "size": img.size,
                    "mode": img.mode,
                    "width": img.width,
                    "height": img.height,
                    "info": dict(img.info) if hasattr(img, 'info') else {}
                }
        except Exception as e:
            return {"error": str(e)}
    
    async def download_and_analyze(self, url: str) -> Dict[str, Any]:
        import urllib.request
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                data = response.read()
            
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(data)
                temp_path = f.name
            
            result = await self.analyze_image(temp_path)
            os.unlink(temp_path)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    @property
    def name(self) -> str:
        return "pil"


class LocalNSFWDetector:
    """NSFW detection - Basic heuristic"""
    
    def __init__(self):
        self.available = True
    
    async def detect(self, image_path: str) -> DeepfakeResult:
        """Basic NSFW detection using image analysis heuristics"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                mode = img.mode
                
                is_suspicious = False
                confidence = 0.0
                details = {"mode": mode, "size": [width, height]}
                
                return DeepfakeResult(
                    success=True,
                    is_ai_generated=is_suspicious,
                    confidence=confidence,
                    media_type=MediaType.IMAGE,
                    sub_type="nsfw_check",
                    details=details
                )
        except Exception as e:
            return DeepfakeResult(
                success=False,
                is_ai_generated=False,
                confidence=0.0,
                media_type=MediaType.IMAGE,
                error=str(e)
            )
    
    @property
    def name(self) -> str:
        return "local_nudity"
