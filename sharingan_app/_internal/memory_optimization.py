# -*- coding: utf-8 -*-
"""
Sharingan Memory Optimization System
Compression, caching, and performance enhancements for all memory systems
"""

import os
import lzma
import pickle
import hashlib
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from functools import lru_cache
import logging

# Optional imports with fallbacks
try:
    import lz4.frame as lz4
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False

try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

logger = logging.getLogger("memory_optimization")

class MemoryCompressor:
    """
    Multi-format compression for memory optimization
    Supports LZ4, Zstandard, LZMA with automatic format selection
    """

    def __init__(self):
        self.compression_stats = {
            'total_compressed': 0,
            'total_original': 0,
            'compression_ratio': 0.0,
            'compression_time': 0.0
        }

    def compress_data(self, data: Any, method: str = 'auto') -> Tuple[bytes, str]:
        """
        Compress data using optimal method
        Returns: (compressed_data, method_used)
        """
        if method == 'auto':
            method = self._select_best_method(data)

        start_time = time.time()

        if method == 'lz4' and LZ4_AVAILABLE:
            compressed = lz4.compress(pickle.dumps(data))
        elif method == 'zstd' and ZSTD_AVAILABLE:
            compressor = zstd.ZstdCompressor()
            compressed = compressor.compress(pickle.dumps(data))
        else:
            # Fallback to LZMA (always available)
            compressed = lzma.compress(pickle.dumps(data))
            method = 'lzma'

        compression_time = time.time() - start_time

        # Update stats
        original_size = len(pickle.dumps(data))
        compressed_size = len(compressed)
        self.compression_stats['total_compressed'] += compressed_size
        self.compression_stats['total_original'] += original_size
        self.compression_stats['compression_time'] += compression_time

        if self.compression_stats['total_original'] > 0:
            self.compression_stats['compression_ratio'] = (
                self.compression_stats['total_compressed'] /
                self.compression_stats['total_original']
            )

        logger.debug(f"Compressed {original_size} bytes to {compressed_size} bytes using {method}")
        return compressed, method

    def decompress_data(self, compressed_data: bytes, method: str) -> Any:
        """Decompress data using specified method"""
        if method == 'lz4' and LZ4_AVAILABLE:
            decompressed = lz4.decompress(compressed_data)
        elif method == 'zstd' and ZSTD_AVAILABLE:
            decompressor = zstd.ZstdDecompressor()
            decompressed = decompressor.decompress(compressed_data)
        else:
            # Fallback to LZMA
            decompressed = lzma.decompress(compressed_data)

        return pickle.loads(decompressed)

    def _select_best_method(self, data: Any) -> str:
        """Select best compression method based on data characteristics"""
        data_size = len(pickle.dumps(data))

        # For small data, LZMA is often better
        if data_size < 1024:  # < 1KB
            return 'lzma'

        # For medium data, LZ4 is fastest
        if data_size < 1024 * 1024:  # < 1MB
            return 'lz4' if LZ4_AVAILABLE else 'lzma'

        # For large data, Zstandard provides best compression
        return 'zstd' if ZSTD_AVAILABLE else 'lz4' if LZ4_AVAILABLE else 'lzma'

    def get_stats(self) -> Dict[str, Any]:
        """Get compression statistics"""
        return self.compression_stats.copy()

class MultiLevelCache:
    """
    Multi-level caching system: RAM -> Disk -> Network
    Automatic promotion/demotion of data
    """

    def __init__(self, cache_dir: str = "~/.sharingan/cache"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # RAM cache (fastest)
        self.ram_cache: Dict[str, Dict[str, Any]] = {}
        self.ram_max_size = 100  # Max items in RAM

        # Disk cache (persistent)
        self.disk_cache_file = self.cache_dir / "memory_cache.pkl"
        self.disk_cache: Dict[str, Dict[str, Any]] = self._load_disk_cache()
        self.disk_max_size = 1000  # Max items on disk

        # Compression for disk storage
        self.compressor = MemoryCompressor()

        # Cache statistics
        self.stats = {
            'ram_hits': 0,
            'ram_misses': 0,
            'disk_hits': 0,
            'disk_misses': 0,
            'total_requests': 0
        }

        logger.info(f"Multi-level cache initialized with RAM:{self.ram_max_size}, Disk:{self.disk_max_size}")

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache with automatic promotion"""
        self.stats['total_requests'] += 1

        # Check RAM cache first
        if key in self.ram_cache:
            self.stats['ram_hits'] += 1
            item = self.ram_cache[key]
            item['last_access'] = time.time()
            self._save_disk_cache()  # Update disk with fresh access time
            return item['data']

        # Check disk cache
        if key in self.disk_cache:
            self.stats['disk_hits'] += 1
            item = self.disk_cache[key]

            # Promote to RAM cache
            if len(self.ram_cache) < self.ram_max_size:
                self.ram_cache[key] = item.copy()
                self.ram_cache[key]['last_access'] = time.time()

            return item['data']

        # Cache miss
        self.stats['ram_misses'] += 1
        self.stats['disk_misses'] += 1
        return None

    def set(self, key: str, data: Any, ttl: int = 3600) -> None:
        """Set item in cache with TTL"""
        cache_item = {
            'data': data,
            'timestamp': time.time(),
            'last_access': time.time(),
            'ttl': ttl,
            'access_count': 0
        }

        # Always store in RAM if space available
        if len(self.ram_cache) < self.ram_max_size:
            self.ram_cache[key] = cache_item

        # Always store compressed on disk
        self.disk_cache[key] = cache_item
        self._save_disk_cache()

        # Cleanup if needed
        self._cleanup_if_needed()

    def delete(self, key: str) -> bool:
        """Delete item from all cache levels"""
        deleted = False

        if key in self.ram_cache:
            del self.ram_cache[key]
            deleted = True

        if key in self.disk_cache:
            del self.disk_cache[key]
            deleted = True
            self._save_disk_cache()

        return deleted

    def clear(self) -> None:
        """Clear all caches"""
        self.ram_cache.clear()
        self.disk_cache.clear()
        self._save_disk_cache()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        ram_hit_rate = self.stats['ram_hits'] / max(1, self.stats['total_requests'])
        disk_hit_rate = (self.stats['ram_hits'] + self.stats['disk_hits']) / max(1, self.stats['total_requests'])

        return {
            'ram_cache_size': len(self.ram_cache),
            'disk_cache_size': len(self.disk_cache),
            'ram_hit_rate': ram_hit_rate,
            'disk_hit_rate': disk_hit_rate,
            'total_requests': self.stats['total_requests'],
            'ram_hits': self.stats['ram_hits'],
            'disk_hits': self.stats['disk_hits']
        }

    def _load_disk_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load compressed disk cache"""
        if self.disk_cache_file.exists():
            try:
                with open(self.disk_cache_file, 'rb') as f:
                    compressed_data = f.read()
                    if compressed_data:
                        return self.compressor.decompress_data(compressed_data, 'lzma')
            except Exception as e:
                logger.error(f"Failed to load disk cache: {e}")

        return {}

    def _save_disk_cache(self) -> None:
        """Save compressed disk cache"""
        try:
            compressed_data, _ = self.compressor.compress_data(self.disk_cache, 'lzma')
            with open(self.disk_cache_file, 'wb') as f:
                f.write(compressed_data)
        except Exception as e:
            logger.error(f"Failed to save disk cache: {e}")

    def _cleanup_if_needed(self) -> None:
        """Cleanup expired and LRU items"""
        current_time = time.time()

        # Remove expired items from RAM
        expired_ram = [
            key for key, item in self.ram_cache.items()
            if current_time - item['timestamp'] > item['ttl']
        ]
        for key in expired_ram:
            del self.ram_cache[key]

        # Remove expired items from disk
        expired_disk = [
            key for key, item in self.disk_cache.items()
            if current_time - item['timestamp'] > item['ttl']
        ]
        for key in expired_disk:
            del self.disk_cache[key]

        # LRU eviction for RAM if still over limit
        if len(self.ram_cache) > self.ram_max_size:
            # Sort by last access time (oldest first)
            sorted_items = sorted(
                self.ram_cache.items(),
                key=lambda x: x[1]['last_access']
            )
            # Remove oldest items
            items_to_remove = len(self.ram_cache) - self.ram_max_size
            for key, _ in sorted_items[:items_to_remove]:
                del self.ram_cache[key]

        # LRU eviction for disk if still over limit
        if len(self.disk_cache) > self.disk_max_size:
            sorted_items = sorted(
                self.disk_cache.items(),
                key=lambda x: x[1]['last_access']
            )
            items_to_remove = len(self.disk_cache) - self.disk_max_size
            for key, _ in sorted_items[:items_to_remove]:
                del self.disk_cache[key]

            self._save_disk_cache()

class GenomeOptimizer:
    """
    Genome Memory specific optimizations
    """

    def __init__(self, genome_memory):
        self.genome = genome_memory
        self.compressor = MemoryCompressor()
        self.cache = MultiLevelCache()
        self.last_optimization = time.time()
        self.optimization_interval = 3600  # 1 hour

    def optimize_genome(self) -> Dict[str, Any]:
        """Run complete genome optimization"""
        results = {
            'compression_savings': 0,
            'cache_hits': 0,
            'old_genes_cleaned': 0,
            'fragments_defragmented': 0,
            'timestamp': datetime.now().isoformat()
        }

        # Compress old genes
        results['compression_savings'] = self._compress_old_genes()

        # Optimize cache
        cache_stats = self.cache.get_stats()
        results['cache_hits'] = cache_stats['ram_hits'] + cache_stats['disk_hits']

        # Clean old genes
        results['old_genes_cleaned'] = self._clean_old_genes()

        # Defragment memory
        results['fragments_defragmented'] = self._defragment_memory()

        self.last_optimization = time.time()

        logger.info(f"Genome optimization completed: {results}")
        return results

    def _compress_old_genes(self) -> int:
        """Compress genes older than 30 days"""
        cutoff_time = time.time() - (30 * 24 * 60 * 60)  # 30 days ago
        savings = 0

        for gene_key, gene in self.genome.genes.items():
            if gene.created_at:
                gene_time = datetime.fromisoformat(gene.created_at).timestamp()
                if gene_time < cutoff_time and not hasattr(gene, '_compressed'):
                    # Compress gene data
                    compressed_data, method = self.compressor.compress_data(gene.data)
                    gene._original_data = gene.data
                    gene.data = {'_compressed': True, '_data': compressed_data, '_method': method}
                    gene._compressed = True
                    savings += len(compressed_data)

        self.genome._save_genome()
        return savings

    def _clean_old_genes(self) -> int:
        """Remove genes with very low success rate and no recent usage"""
        cutoff_time = time.time() - (90 * 24 * 60 * 60)  # 90 days ago
        cleaned = 0

        genes_to_remove = []
        for gene_key, gene in self.genome.genes.items():
            if (gene.success_rate < 0.1 and
                gene.usage_count < 5 and
                gene.created_at):
                gene_time = datetime.fromisoformat(gene.created_at).timestamp()
                if gene_time < cutoff_time:
                    genes_to_remove.append(gene_key)
                    cleaned += 1

        for gene_key in genes_to_remove:
            del self.genome.genes[gene_key]

        if genes_to_remove:
            self.genome._save_genome()

        return cleaned

    def _defragment_memory(self) -> int:
        """Defragment memory by reorganizing data structures"""
        # Reorganize genes by category for better access patterns
        categories = {}
        for gene_key, gene in self.genome.genes.items():
            cat = gene.category
            if cat not in categories:
                categories[cat] = {}
            categories[cat][gene_key] = gene

        # Rebuild genes dict in optimized order
        optimized_genes = {}
        for category in sorted(categories.keys()):
            for gene_key in sorted(categories[category].keys(),
                                 key=lambda k: categories[category][k].priority,
                                 reverse=True):
                optimized_genes[gene_key] = categories[category][gene_key]

        self.genome.genes = optimized_genes
        self.genome._save_genome()

        return len(categories)  # Number of categories optimized

    def get_gene_cached(self, key: str, category: str = "knowledge") -> Optional[Any]:
        """Get gene with caching optimization"""
        cache_key = f"gene_{category}_{key}"

        # Check cache first
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Get from genome
        gene = self.genome.get_gene(key, category)
        if gene:
            # Cache for 1 hour
            self.cache.set(cache_key, gene, ttl=3600)
            return gene

        return None

class MemoryDefragmenter:
    """
    Automatic memory defragmentation and optimization
    """

    def __init__(self):
        self.defragmentation_stats = {
            'last_defrag': time.time(),
            'fragments_removed': 0,
            'memory_freed': 0,
            'optimization_runs': 0
        }

    def run_defragmentation(self) -> Dict[str, Any]:
        """Run memory defragmentation"""
        # Force garbage collection
        import gc
        collected = gc.collect()

        # Update stats
        self.defragmentation_stats['last_defrag'] = time.time()
        self.defragmentation_stats['fragments_removed'] += collected
        self.defragmentation_stats['optimization_runs'] += 1

        return {
            'objects_collected': collected,
            'memory_freed': 'unknown',  # Would need psutil for actual memory measurement
            'timestamp': datetime.now().isoformat()
        }

class MemoryOptimizationManager:
    """
    Central manager for all memory optimizations
    """

    def __init__(self):
        self.compressor = MemoryCompressor()
        self.cache = MultiLevelCache()
        self.defragmenter = MemoryDefragmenter()

        # Optimization scheduling
        self.optimization_thread = None
        self.running = False
        self.optimization_interval = 3600  # 1 hour

    def start_optimization_daemon(self):
        """Start background optimization daemon"""
        if self.optimization_thread and self.optimization_thread.is_alive():
            return

        self.running = True
        self.optimization_thread = threading.Thread(
            target=self._optimization_loop,
            daemon=True
        )
        self.optimization_thread.start()
        logger.info("Memory optimization daemon started")

    def stop_optimization_daemon(self):
        """Stop background optimization"""
        self.running = False
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5)
        logger.info("Memory optimization daemon stopped")

    def run_full_optimization(self) -> Dict[str, Any]:
        """Run complete memory optimization suite"""
        results = {
            'compression_stats': self.compressor.get_stats(),
            'cache_stats': self.cache.get_stats(),
            'defragmentation': self.defragmenter.run_defragmentation(),
            'timestamp': datetime.now().isoformat()
        }

        logger.info(f"Full memory optimization completed: {results}")
        return results

    def _optimization_loop(self):
        """Background optimization loop"""
        while self.running:
            try:
                self.run_full_optimization()
                time.sleep(self.optimization_interval)
            except Exception as e:
                logger.error(f"Memory optimization error: {e}")
                time.sleep(60)  # Wait 1 minute before retry

    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status"""
        return {
            'daemon_running': self.running,
            'last_optimization': time.time(),
            'cache_stats': self.cache.get_stats(),
            'compression_stats': self.compressor.get_stats(),
            'defragmentation_stats': self.defragmenter.defragmentation_stats
        }

# Global instances
_memory_optimizer = None

def get_memory_optimizer() -> MemoryOptimizationManager:
    """Get global memory optimizer instance"""
    global _memory_optimizer
    if _memory_optimizer is None:
        _memory_optimizer = MemoryOptimizationManager()
    return _memory_optimizer

# Convenience functions
def compress_memory_data(data: Any) -> Tuple[bytes, str]:
    """Compress any memory data"""
    optimizer = get_memory_optimizer()
    return optimizer.compressor.compress_data(data)

def get_cached_data(key: str) -> Optional[Any]:
    """Get data from multi-level cache"""
    optimizer = get_memory_optimizer()
    return optimizer.cache.get(key)

def set_cached_data(key: str, data: Any, ttl: int = 3600):
    """Set data in multi-level cache"""
    optimizer = get_memory_optimizer()
    optimizer.cache.set(key, data, ttl)

if __name__ == "__main__":
    print("[MEMORY OPTIMIZATION] Sharingan Memory Optimization System")
    print("=" * 60)

    # Test compression
    test_data = {"test": "data", "numbers": list(range(1000))}
    compressed, method = compress_memory_data(test_data)
    print(f"Compressed {len(str(test_data))} chars to {len(compressed)} bytes using {method}")

    # Test cache
    set_cached_data("test_key", test_data)
    cached = get_cached_data("test_key")
    print(f"Cache test: {'PASSED' if cached == test_data else 'FAILED'}")

    print("\nOptimization system ready!")