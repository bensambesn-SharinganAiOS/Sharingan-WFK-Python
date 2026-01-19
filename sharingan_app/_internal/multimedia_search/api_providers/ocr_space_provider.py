#!/usr/bin/env python3
"""
API Provider for OCR.space - 25,000 requests/month free
"""

import aiohttp
import base64
from typing import Optional, Dict, Any
import logging

from .base_provider import BaseSearchProvider
from ..schemas import OCRResult, SearchEngine

logger = logging.getLogger("multimedia.ocrspace")


class OCRSpaceProvider(BaseSearchProvider):
    """OCR.space API provider - Free tier: 25,000 req/month"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "helloworld"
        self.base_url = "https://api.ocr.space/parse/image"
    
    async def extract_text(self, image_source: str, language: str = "eng") -> OCRResult:
        """Extract text from image using OCR.space"""
        try:
            payload = {
                "apikey": self.api_key,
                "language": language,
                "isoverlayrequired": False,
            }
            
            if image_source.startswith("http"):
                payload["url"] = image_source
            else:
                with open(image_source, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode()
                payload["base64image"] = image_data
            
            async with aiohttp.ClientSession() as session:
                files = None
                if not image_source.startswith("http"):
                    files = {
                        "file": ("image.jpg", open(image_source, "rb"), "image/jpeg")
                    }
                
                async with session.post(
                    self.base_url, 
                    data=payload if image_source.startswith("http") else None,
                    files=files if files else None
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("IsErroredOnProcessing") == False:
                            parsed = data.get("ParsedResults", [{}])[0]
                            text = parsed.get("ParsedText", "")
                            return OCRResult(
                                success=True,
                                text=text,
                                confidence=0.9,
                                language=language
                            )
                        else:
                            return OCRResult(
                                success=False,
                                text="",
                                confidence=0.0,
                                language=language,
                                error=str(data.get("ErrorMessage", []))
                            )
                    else:
                        return OCRResult(
                            success=False,
                            text="",
                            confidence=0.0,
                            language=language,
                            error=f"HTTP {response.status}"
                        )
        except Exception as e:
            logger.error(f"OCR.space error: {e}")
            return OCRResult(
                success=False,
                text="",
                confidence=0.0,
                language=language,
                error=str(e)
            )
    
    @property
    def name(self) -> str:
        return "ocr_space"
    
    @property
    def requires_api_key(self) -> bool:
        return False
