#!/usr/bin/env python3
"""
Sharingan Lightweight Metrics - Métriques sans ralentissement
Échantillonnage intelligent, pas de tracking constant.
"""

import os
import time
import random
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sharingan.metrics")

class MetricTrend(Enum):
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    UNKNOWN = "unknown"

class LightweightMetrics:
    """
    Métriques légères avec échantillonnage intelligent.
    
    Principe: only 1% du temps on mesure, le reste du temps on travaille.
    """
    
    SAMPLING_RATE = 0.01  # 1% du temps
    MAX_SAMPLES = 100     # Garder only les 100 derniers
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.last_sample_time = 0
        self.sample_interval = 1.0  # Max 1 sample/seconde
        self.enabled = True
    
    def sample(self) -> Optional[Dict]:
        """Échantillonne les métriques (très léger)"""
        if not self.enabled:
            return None
        
        now = time.time()
        if now - self.last_sample_time < self.sample_interval:
            return None
        
        if random.random() > self.SAMPLING_RATE:
            return None
        
        self.last_sample_time = now
        
        sample = {}
        
        try:
            sample["cpu_percent"] = self._get_cpu_percent()
            sample["memory_percent"] = self._get_memory_percent()
            sample["disk_usage"] = self._get_disk_usage()
            sample["open_files"] = self._get_open_files()
            sample["process_count"] = self._get_process_count()
        except Exception as e:
            logger.debug(f"Metric sample failed: {e}")
            return None
        
        for key, value in sample.items():
            if value is not None:
                self.metrics[key].append(value)
                if len(self.metrics[key]) > self.MAX_SAMPLES:
                    self.metrics[key] = self.metrics[key][-self.MAX_SAMPLES:]
        
        return sample
    
    def _get_cpu_percent(self) -> float:
        """CPU usage -lecture depuis /proc"""
        try:
            with open("/proc/loadavg", "r") as f:
                load = float(f.read().split()[0])
            return min(100.0, load * 25)
        except:
            return None
    
    def _get_memory_percent(self) -> float:
        """Memory usage - lecture depuis /proc/meminfo"""
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
            
            total = free = available = 0
            for line in lines:
                if line.startswith("MemTotal:"):
                    total = int(line.split()[1]) / 1024
                elif line.startswith("MemAvailable:"):
                    available = int(line.split()[1]) / 1024
                elif line.startswith("MemFree:"):
                    free = int(line.split()[1]) / 1024
            
            if total > 0:
                used = total - available
                return (used / total) * 100
        except:
            pass
        return None
    
    def _get_disk_usage(self) -> float:
        """Disk usage du répertoire courant"""
        try:
            stat = os.statvfs("/root/Projets/Sharingan-WFK-Python")
            used = (stat.f_blocks - stat.f_bfree) / stat.f_blocks
            return used * 100
        except:
            return None
    
    def _get_open_files(self) -> int:
        """Nombre de fichiers ouverts par ce processus"""
        try:
            pid = os.getpid()
            fd_dir = f"/proc/{pid}/fd"
            if os.path.exists(fd_dir):
                return len(os.listdir(fd_dir))
        except:
            pass
        return None
    
    def _get_process_count(self) -> int:
        """Nombre de processus du système"""
        try:
            return len(os.listdir("/proc"))
        except:
            return None
    
    def get_trend(self, metric: str) -> Dict:
        """Analyse la tendance d'une métrique"""
        data = self.metrics.get(metric, [])
        
        if len(data) < 5:
            return {"trend": "unknown", "value": data[-1] if data else None}
        
        recent = data[-10:] if len(data) >= 10 else data
        older = data[:-10] if len(data) > 10 else []
        
        if not older:
            return {"trend": "unknown", "value": data[-1]}
        
        avg_recent = sum(recent) / len(recent)
        avg_older = sum(older) / len(older)
        
        change = (avg_recent - avg_older) / max(avg_older, 1)
        
        if change > 0.1:
            trend = "increasing"
        elif change < -0.1:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "value": data[-1],
            "avg_recent": avg_recent,
            "avg_older": avg_older,
            "change_percent": change * 100
        }
    
    def get_health_report(self) -> Dict:
        """Rapport de santé du système"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "healthy": True,
            "metrics": {},
            "warnings": []
        }
        
        cpu_trend = self.get_trend("cpu_percent")
        mem_trend = self.get_trend("memory_percent")
        
        report["metrics"]["cpu"] = cpu_trend
        report["metrics"]["memory"] = mem_trend
        
        if cpu_trend.get("value", 0) > 80:
            report["warnings"].append("CPU usage élevé")
            report["healthy"] = False
        
        if mem_trend.get("trend") == "increasing" and mem_trend.get("change_percent", 0) > 20:
            report["warnings"].append("Mémoire en augmentation constante")
        
        if not self.metrics:
            report["warnings"].append("Pas assez de données pour analyse")
        
        return report
    
    def get_quick_stats(self) -> Dict:
        """Statistiques rapides (sans analyse)"""
        return {
            "samples_collected": sum(len(v) for v in self.metrics.values()),
            "enabled": self.enabled,
            "last_sample": self.last_sample_time,
            "metrics_tracked": list(self.metrics.keys())
        }
    
    def disable(self):
        """Désactive les métriques"""
        self.enabled = False
    
    def enable(self):
        """Active les métriques"""
        self.enabled = True


def get_lightweight_metrics() -> LightweightMetrics:
    return LightweightMetrics()


if __name__ == "__main__":
    print("=== LIGHTWEIGHT METRICS TEST ===\n")
    
    metrics = LightweightMetrics()
    
    print("1. Collecting samples (this may take a moment)...")
    start = time.time()
    samples = 0
    while time.time() - start < 3:
        s = metrics.sample()
        if s:
            samples += 1
            print(f"   Sample {samples}: CPU={s.get('cpu_percent', 0):.1f}%, MEM={s.get('memory_percent', 0):.1f}%")
        time.sleep(0.1)
    
    print(f"\n2. Stats collected: {metrics.get_quick_stats()}")
    
    print("\n3. Trends:")
    for metric in ["cpu_percent", "memory_percent"]:
        trend = metrics.get_trend(metric)
        print(f"   {metric}: {trend}")
    
    print("\n4. Health report:")
    report = metrics.get_health_report()
    print(f"   Healthy: {report['healthy']}")
    print(f"   Warnings: {report['warnings']}")
    
    print("\n✓ Lightweight metrics operational!")
