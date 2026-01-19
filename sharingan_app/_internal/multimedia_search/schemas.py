#!/usr/bin/env python3
"""
Schemas for multimedia search results
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"


class SearchEngine(Enum):
    GOOGLE = "google"
    YANDEX = "yandex"
    BING = "bing"
    TINEYE = "tineye"
    REVERSE_IMAGE_SEARCHER = "reverseimagesearcher"


class FactCheckRating(Enum):
    TRUE = "TRUE"
    MOSTLY_TRUE = "MOSTLY_TRUE"
    PARTIALLY_TRUE = "PARTIALLY_TRUE"
    MISSING_CONTEXT = "MISSING_CONTEXT"
    PARTIALLY_FALSE = "PARTIALLY_FALSE"
    MOSTLY_FALSE = "MOSTLY_FALSE"
    FALSE = "FALSE"
    UNVERIFIED = "UNVERIFIED"


@dataclass
class ImageMatch:
    url: str
    title: Optional[str] = None
    source: Optional[str] = None
    snippet: Optional[str] = None
    thumbnail_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    match_score: Optional[float] = None
    date_found: Optional[str] = None


@dataclass
class ImageSearchResult:
    success: bool
    source_url: str
    engine: SearchEngine
    matches: List[ImageMatch] = field(default_factory=list)
    first_occurrence: Optional[str] = None
    similar_images: List[str] = field(default_factory=list)
    objects_detected: List[str] = field(default_factory=list)
    text_extracted: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoMetadata:
    duration_seconds: float
    width: int
    height: int
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    fps: Optional[float] = None
    format: Optional[str] = None
    file_size: Optional[int] = None


@dataclass
class VideoScene:
    start_time: float
    end_time: float
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    keyframe_url: Optional[str] = None


@dataclass
class VideoAnalysisResult:
    success: bool
    source_url: str
    metadata: Optional[VideoMetadata] = None
    transcription: Optional[str] = None
    scenes: List[VideoScene] = field(default_factory=list)
    keyframes: List[str] = field(default_factory=list)
    objects_detected: List[str] = field(default_factory=list)
    audio_transcript: Optional[str] = None
    error: Optional[str] = None
    metadata_ext: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OCRResult:
    success: bool
    text: str
    confidence: float
    language: str
    blocks: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class FactCheckSource:
    url: str
    title: Optional[str] = None
    claim_review: Optional[str] = None
    verdict: Optional[FactCheckRating] = None
    publish_date: Optional[str] = None


@dataclass
class FactCheckResult:
    success: bool
    claim: str
    rating: Optional[FactCheckRating] = None
    sources: List[FactCheckSource] = field(default_factory=list)
    related_claims: List[str] = field(default_factory=list)
    confidence: float = 0.0
    error: Optional[str] = None


@dataclass
class DeepfakeResult:
    success: bool
    is_ai_generated: bool
    confidence: float
    media_type: MediaType
    sub_type: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class MediaSearchConfig:
    image_engines: List[SearchEngine] = field(default_factory=lambda: [
        SearchEngine.GOOGLE, 
        SearchEngine.YANDEX, 
        SearchEngine.BING
    ])
    max_results: int = 10
    ocr_language: str = "eng"
    ocr_engine: str = "auto"
    extract_keyframes: bool = True
    extract_transcription: bool = True
    scene_detection_threshold: float = 0.3
    fact_check_sources: List[str] = field(default_factory=lambda: ["google"])
    deepfake_detectors: List[str] = field(default_factory=lambda: ["nonescape"])
    serpapi_key: Optional[str] = None
    searchapi_key: Optional[str] = None
    ocrspace_key: Optional[str] = None
    google_factcheck_key: Optional[str] = None


@dataclass
class MultimediaSearchResponse:
    query_url: str
    media_type: MediaType
    image_results: Dict[str, ImageSearchResult] = field(default_factory=dict)
    video_results: Optional[VideoAnalysisResult] = None
    ocr_result: Optional[OCRResult] = None
    fact_check_result: Optional[FactCheckResult] = None
    deepfake_result: Optional[DeepfakeResult] = None
    raw_response: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            from datetime import datetime
            self.timestamp = datetime.now().isoformat()
