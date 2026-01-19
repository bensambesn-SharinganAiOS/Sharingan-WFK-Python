#!/usr/bin/env python3
"""
Web Scraping providers for reverse image search - Free interfaces
"""

from typing import Optional
from ..schemas import ImageSearchResult, ImageMatch, SearchEngine


class TinEyeScraper:
    """TinEye reverse image search via web interface"""
    
    @property
    def name(self) -> str:
        return "tineye_web"
    
    async def search_image(self, image_url: str) -> ImageSearchResult:
        return ImageSearchResult(
            success=False,
            source_url=image_url,
            engine=SearchEngine.TINEYE,
            error="TinEye: Use https://www.tineye.com/search?url={image_url}"
        )


class YandexScraper:
    """Yandex Images reverse search via web interface"""
    
    @property
    def name(self) -> str:
        return "yandex_web"
    
    async def search_image(self, image_url: str) -> ImageSearchResult:
        return ImageSearchResult(
            success=False,
            source_url=image_url,
            engine=SearchEngine.YANDEX,
            error="Yandex: Use https://yandex.com/images/search?url={image_url}"
        )


class GoogleScraper:
    """Google Images/Lens via web interface"""
    
    @property
    def name(self) -> str:
        return "google_web"
    
    async def search_image(self, image_url: str) -> ImageSearchResult:
        return ImageSearchResult(
            success=False,
            source_url=image_url,
            engine=SearchEngine.GOOGLE,
            error="Google: Use https://lens.google.com/upload?url={image_url}"
        )
