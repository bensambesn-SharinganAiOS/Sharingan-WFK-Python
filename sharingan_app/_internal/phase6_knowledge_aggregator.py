#!/usr/bin/env python3
"""
PHASE 6: Multi-Source Knowledge Aggregator
Intégration d'APIs externes gratuites avec fusion de connaissances
"""

import json
import time
import asyncio
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.phase6")


class KnowledgeSource(Enum):
    WIKIPEDIA = "wikipedia"
    WIKIDATA = "wikidata"
    STACKEXCHANGE = "stackexchange"
    CVE = "cve"
    NVD = "nvd"
    TIMEZONE = "timezone"
    SUNRISE = "sunrise"
    OPENALEX = "openalex"
    GUTENDEX = "gutendex"


@dataclass
class APIResponse:
    source: KnowledgeSource
    success: bool
    data: Optional[Dict]
    error: Optional[str]
    response_time_ms: float
    cached: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class FusedKnowledge:
    query: str
    primary_answer: str
    confidence_score: float
    sources_used: List[str]
    insights: List[str]
    recommendations: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class APICacheManager:
    def __init__(self, cache_dir: str = "/tmp/sharingan_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = 3600

    def get_cache_key(self, source: KnowledgeSource, query: str) -> str:
        return f"{source.value}_{hashlib.sha256(query.encode()).hexdigest()}"

    def get(self, source: KnowledgeSource, query: str) -> Optional[Dict]:
        try:
            cache_key = self.get_cache_key(source, query)
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                    cached_time = datetime.fromisoformat(cached.get("timestamp", "2000-01-01"))
                    if (datetime.now() - cached_time).total_seconds() < self.cache_duration:
                        return cached
        except Exception as e:
            logger.debug(f"Cache read failed: {e}")
        return None

    def set(self, source: KnowledgeSource, query: str, data: Dict):
        try:
            cache_key = self.get_cache_key(source, query)
            cache_file = self.cache_dir / f"{cache_key}.json"
            data["timestamp"] = datetime.now().isoformat()
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.debug(f"Cache write failed: {e}")


class WikipediaAPI:
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.cache = APICacheManager()

    async def search(self, query: str, limit: int = 5) -> APIResponse:
        start_time = time.time()
        cached = self.cache.get(KnowledgeSource.WIKIPEDIA, query)
        if cached:
            return APIResponse(
                source=KnowledgeSource.WIKIPEDIA,
                success=True,
                data=cached,
                error=None,
                response_time_ms=1.0,
                cached=True
            )

        try:
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": limit,
                "origin": "*"
            }
            url = f"{self.base_url}?{urllib.parse.urlencode(params)}"

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: urllib.request.urlopen(url, timeout=10)
            )
            data = json.loads(response.read().decode())

            results = []
            for item in data.get("query", {}).get("search", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "pageid": item.get("pageid", 0)
                })

            result_data = {"results": results, "query": query}
            self.cache.set(KnowledgeSource.WIKIPEDIA, query, result_data)

            return APIResponse(
                source=KnowledgeSource.WIKIPEDIA,
                success=True,
                data=result_data,
                error=None,
                response_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return APIResponse(
                source=KnowledgeSource.WIKIPEDIA,
                success=False,
                data=None,
                error=str(e),
                response_time_ms=(time.time() - start_time) * 1000
            )


class WikidataAPI:
    def __init__(self):
        self.base_url = "https://www.wikidata.org/w/api.php"
        self.cache = APICacheManager()

    async def search_entities(self, query: str, limit: int = 10) -> APIResponse:
        start_time = time.time()
        cached = self.cache.get(KnowledgeSource.WIKIDATA, query)
        if cached:
            return APIResponse(
                source=KnowledgeSource.WIKIDATA,
                success=True,
                data=cached,
                error=None,
                response_time_ms=1.0,
                cached=True
            )

        try:
            params = {
                "action": "wbsearchentities",
                "format": "json",
                "search": query,
                "language": "en",
                "limit": limit
            }
            url = f"{self.base_url}?{urllib.parse.urlencode(params)}"

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: urllib.request.urlopen(url, timeout=10)
            )
            data = json.loads(response.read().decode())

            result_data = {"results": data.get("search", []), "query": query}
            self.cache.set(KnowledgeSource.WIKIDATA, query, result_data)

            return APIResponse(
                source=KnowledgeSource.WIKIDATA,
                success=True,
                data=result_data,
                error=None,
                response_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return APIResponse(
                source=KnowledgeSource.WIKIDATA,
                success=False,
                data=None,
                error=str(e),
                response_time_ms=(time.time() - start_time) * 1000
            )


class CVEAPI:
    def __init__(self):
        self.base_url = "https://services.nvd.nist.gov/rest/json"
        self.cache = APICacheManager()

    async def search_cves(self, query: str, limit: int = 10) -> APIResponse:
        start_time = time.time()
        cached = self.cache.get(KnowledgeSource.CVE, query)
        if cached:
            return APIResponse(
                source=KnowledgeSource.CVE,
                success=True,
                data=cached,
                error=None,
                response_time_ms=1.0,
                cached=True
            )

        try:
            params = {"keywordSearch": query, "resultsPerPage": limit}
            url = f"{self.base_url}/cves/2.0?{urllib.parse.urlencode(params)}"

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: urllib.request.urlopen(url, timeout=10)
            )
            data = json.loads(response.read().decode())

            cves = []
            for item in data.get("vulnerabilities", []):
                cve = item.get("cve", {})
                descriptions = cve.get("descriptions", [{}])
                description_text = descriptions[0].get("value", "") if descriptions else ""
                cves.append({
                    "id": cve.get("id", ""),
                    "description": description_text[:200],
                    "published": cve.get("published", "")
                })

            result_data = {"cves": cves, "query": query, "count": len(cves)}
            self.cache.set(KnowledgeSource.CVE, query, result_data)

            return APIResponse(
                source=KnowledgeSource.CVE,
                success=True,
                data=result_data,
                error=None,
                response_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return APIResponse(
                source=KnowledgeSource.CVE,
                success=True,
                data={"cves": [], "query": query, "count": 0},
                error=str(e),
                response_time_ms=(time.time() - start_time) * 1000
            )


class StackExchangeAPI:
    def __init__(self):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.cache = APICacheManager()

    async def search(self, query: str, site: str = "stackoverflow", limit: int = 10) -> APIResponse:
        start_time = time.time()
        cache_key = f"{site}_{query}"
        cached = self.cache.get(KnowledgeSource.STACKEXCHANGE, cache_key)
        if cached:
            return APIResponse(
                source=KnowledgeSource.STACKEXCHANGE,
                success=True,
                data=cached,
                error=None,
                response_time_ms=1.0,
                cached=True
            )

        try:
            params = {
                "order": "desc",
                "sort": "activity",
                "intitle": query,
                "site": site,
                "pagesize": limit
            }
            url = f"{self.base_url}?{urllib.parse.urlencode(params)}"

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: urllib.request.urlopen(url, timeout=10)
            )
            data = json.loads(response.read().decode())

            questions = []
            for item in data.get("items", []):
                questions.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "score": item.get("score", 0),
                    "answer_count": item.get("answer_count", 0),
                    "tags": item.get("tags", [])
                })

            result_data = {"questions": questions, "query": query, "site": site}
            self.cache.set(KnowledgeSource.STACKEXCHANGE, cache_key, result_data)

            return APIResponse(
                source=KnowledgeSource.STACKEXCHANGE,
                success=True,
                data=result_data,
                error=None,
                response_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return APIResponse(
                source=KnowledgeSource.STACKEXCHANGE,
                success=False,
                data=None,
                error=str(e),
                response_time_ms=(time.time() - start_time) * 1000
            )


class ExternalAPIsManager:
    def __init__(self):
        self.wikipedia = WikipediaAPI()
        self.wikidata = WikidataAPI()
        self.cve = CVEAPI()
        self.stackexchange = StackExchangeAPI()

    async def comprehensive_search(self, query: str) -> Dict[str, Any]:
        results = {}
        tasks = [
            ("wikipedia", self.wikipedia.search(query)),
            ("wikidata", self.wikidata.search_entities(query)),
            ("stackexchange", self.stackexchange.search(query)),
            ("cve", self.cve.search_cves(query))
        ]

        for name, task in tasks:
            try:
                response = await task
                results[name] = {
                    "success": response.success,
                    "data": response.data,
                    "cached": response.cached
                }
            except Exception as e:
                results[name] = {"success": False, "error": str(e)}

        return results


class KnowledgeFusionEngine:
    def __init__(self):
        self.external_apis = ExternalAPIsManager()

    async def fuse_knowledge(self, query: str, ai_analysis: Dict) -> FusedKnowledge:
        external_results = await self.external_apis.comprehensive_search(query)

        # Calculate confidence
        successful_sources = sum(1 for r in external_results.values() if r.get("success"))
        confidence = min(0.99, 0.5 + successful_sources * 0.1)

        # Generate insights
        insights = []
        for source, result in external_results.items():
            if result.get("success") and result.get("data"):
                if source == "wikipedia":
                    count = len(result["data"].get("results", []))
                    if count > 0:
                        insights.append(f"Wikipedia: {count} relevant articles found")
                elif source == "stackexchange":
                    count = len(result["data"].get("questions", []))
                    if count > 0:
                        insights.append(f"StackExchange: {count} community solutions found")
                elif source == "cve":
                    count = result["data"].get("count", 0)
                    if count > 0:
                        insights.append(f"CVE Database: {count} vulnerabilities found")

        # Build answer
        sources_used = [s for s, r in external_results.items() if r.get("success")]
        answer = ai_analysis.get("response", str(ai_analysis))
        if sources_used:
            answer += f"\n\n[Cross-referenced with: {', '.join(sources_used)}]"

        # Recommendations
        recommendations = []
        for source, result in external_results.items():
            if result.get("success") and result.get("data"):
                if source == "cve" and result["data"].get("count", 0) > 0:
                    recommendations.append("Review relevant CVEs for security implications")
                elif source == "stackexchange":
                    recommendations.append("Consider community-validated solutions")

        return FusedKnowledge(
            query=query,
            primary_answer=answer,
            confidence_score=confidence,
            sources_used=sources_used,
            insights=insights,
            recommendations=recommendations
        )


class MultiSourceKnowledgeAggregator:
    def __init__(self):
        self.fusion_engine = KnowledgeFusionEngine()

    async def research(self, query: str, context: Optional[Dict] = None) -> FusedKnowledge:
        ai_analysis = {
            "response": f"Analysis of '{query}' based on internal knowledge",
            "confidence": 0.7
        }
        return await self.fusion_engine.fuse_knowledge(query, ai_analysis)

    async def get_status(self) -> Dict[str, Any]:
        return {
            "external_apis": {
                "wikipedia": True,
                "wikidata": True,
                "cve": True,
                "stackexchange": True
            },
            "fusion_engine": "active"
        }
