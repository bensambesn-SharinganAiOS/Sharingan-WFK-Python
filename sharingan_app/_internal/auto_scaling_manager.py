#!/usr/bin/env python3
"""
SHARINGAN AUTO-SCALING MANAGER
Gestion dynamique et auto-scaling des ressources
Permet à Sharingan de s'adapter automatiquement aux charges de travail
"""

import sys
import os
import time
import threading
import psutil
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auto_scaling")

class ScalingTrigger(Enum):
    """Déclencheurs de mise à l'échelle"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_LOAD = "network_load"
    TASK_QUEUE = "task_queue"
    TIME_BASED = "time_based"

class ScalingAction(Enum):
    """Actions de mise à l'échelle"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    OPTIMIZE = "optimize"

@dataclass
class ScalingRule:
    """Règle de mise à l'échelle"""
    trigger: ScalingTrigger
    threshold_high: float
    threshold_low: float
    action: ScalingAction
    cooldown_period: int = 300  # 5 minutes
    enabled: bool = True
    last_triggered: float = 0

@dataclass
class ResourceMetrics:
    """Métriques des ressources système"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_connections: int
    active_threads: int
    timestamp: float = field(default_factory=time.time)

@dataclass
class ScalingDecision:
    """Décision de mise à l'échelle"""
    action: ScalingAction
    reason: str
    confidence: float  # 0-1
    timestamp: float = field(default_factory=time.time)
    executed: bool = False

class AutoScalingManager:
    """
    Gestionnaire d'auto-scaling intelligent pour Sharingan
    """

    def __init__(self):
        self.scaling_rules: Dict[str, ScalingRule] = {}
        self.metrics_history: List[ResourceMetrics] = []
        self.scaling_decisions: List[ScalingDecision] = []
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None

        # Métriques actuelles
        self.current_metrics = self._collect_metrics()

        # Règles par défaut
        self._setup_default_rules()

        logger.info(" Auto-Scaling Manager initialized")

    def _setup_default_rules(self):
        """Configurer les règles de mise à l'échelle par défaut"""
        default_rules = [
            ScalingRule(
                trigger=ScalingTrigger.CPU_USAGE,
                threshold_high=80.0,
                threshold_low=30.0,
                action=ScalingAction.OPTIMIZE,
                cooldown_period=300
            ),
            ScalingRule(
                trigger=ScalingTrigger.MEMORY_USAGE,
                threshold_high=85.0,
                threshold_low=40.0,
                action=ScalingAction.OPTIMIZE,
                cooldown_period=300
            ),
            ScalingRule(
                trigger=ScalingTrigger.DISK_USAGE,
                threshold_high=90.0,
                threshold_low=50.0,
                action=ScalingAction.OPTIMIZE,
                cooldown_period=600
            ),
            ScalingRule(
                trigger=ScalingTrigger.TASK_QUEUE,
                threshold_high=10.0,  # Plus de 10 tâches en attente
                threshold_low=2.0,
                action=ScalingAction.SCALE_OUT,
                cooldown_period=600
            )
        ]

        for i, rule in enumerate(default_rules):
            self.scaling_rules[f"rule_{i}"] = rule

    def _collect_metrics(self) -> ResourceMetrics:
        """Collecter les métriques système actuelles"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_connections()

            metrics = ResourceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                network_connections=len(network),
                active_threads=threading.active_count()
            )

            # Garder l'historique (dernières 100 mesures)
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 100:
                self.metrics_history.pop(0)

            return metrics

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return ResourceMetrics(0, 0, 0, 0, 0)

    def start_monitoring(self):
        """Démarrer la surveillance continue"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()

        logger.info(" Auto-scaling monitoring started")

    def stop_monitoring(self):
        """Arrêter la surveillance"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info(" Auto-scaling monitoring stopped")

    def _monitoring_loop(self):
        """Boucle de surveillance continue"""
        while self.monitoring_active:
            try:
                # Collecter les métriques
                self.current_metrics = self._collect_metrics()

                # Évaluer les règles de mise à l'échelle
                decisions = self._evaluate_scaling_rules()

                # Exécuter les décisions
                for decision in decisions:
                    if not decision.executed:
                        self._execute_scaling_decision(decision)

                # Attendre avant la prochaine mesure
                time.sleep(30)  # Toutes les 30 secondes

            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(60)  # Attendre plus longtemps en cas d'erreur

    def _evaluate_scaling_rules(self) -> List[ScalingDecision]:
        """Évaluer toutes les règles de mise à l'échelle"""
        decisions = []

        for rule_name, rule in self.scaling_rules.items():
            if not rule.enabled:
                continue

            # Vérifier le cooldown
            if time.time() - rule.last_triggered < rule.cooldown_period:
                continue

            decision = self._evaluate_single_rule(rule)
            if decision:
                decisions.append(decision)
                rule.last_triggered = time.time()

        return decisions

    def _evaluate_single_rule(self, rule: ScalingRule) -> Optional[ScalingDecision]:
        """Évaluer une seule règle"""
        metrics = self.current_metrics

        # Obtenir la valeur actuelle selon le trigger
        current_value = self._get_metric_value(rule.trigger, metrics)

        # Décider de l'action
        if current_value >= rule.threshold_high:
            # Seuil haut dépassé - action nécessaire
            action = rule.action
            reason = f"{rule.trigger.value} too high: {current_value:.1f} >= {rule.threshold_high}"
            confidence = min(1.0, (current_value - rule.threshold_high) / rule.threshold_high + 0.5)

        elif current_value <= rule.threshold_low:
            # Seuil bas dépassé - optimisation possible
            if rule.action == ScalingAction.OPTIMIZE:
                action = ScalingAction.OPTIMIZE
                reason = f"{rule.trigger.value} low: {current_value:.1f} <= {rule.threshold_low}"
                confidence = min(1.0, (rule.threshold_low - current_value) / rule.threshold_low + 0.5)
            else:
                return None
        else:
            return None

        return ScalingDecision(
            action=action,
            reason=reason,
            confidence=confidence
        )

    def _get_metric_value(self, trigger: ScalingTrigger, metrics: ResourceMetrics) -> float:
        """Obtenir la valeur d'une métrique selon le trigger"""
        if trigger == ScalingTrigger.CPU_USAGE:
            return metrics.cpu_percent
        elif trigger == ScalingTrigger.MEMORY_USAGE:
            return metrics.memory_percent
        elif trigger == ScalingTrigger.DISK_USAGE:
            return metrics.disk_percent
        elif trigger == ScalingTrigger.NETWORK_LOAD:
            return metrics.network_connections
        elif trigger == ScalingTrigger.TASK_QUEUE:
            # Simuler une file de tâches (à intégrer avec le vrai système)
            return len(threading.enumerate())  # Nombre de threads comme proxy
        elif trigger == ScalingTrigger.TIME_BASED:
            return time.time() % 86400  # Secondes depuis minuit
        else:
            return 0

    def _execute_scaling_decision(self, decision: ScalingDecision):
        """Exécuter une décision de mise à l'échelle"""
        try:
            if decision.action == ScalingAction.OPTIMIZE:
                self._optimize_resources(decision)
            elif decision.action == ScalingAction.SCALE_UP:
                self._scale_up_resources(decision)
            elif decision.action == ScalingAction.SCALE_DOWN:
                self._scale_down_resources(decision)
            elif decision.action == ScalingAction.SCALE_OUT:
                self._scale_out_resources(decision)
            elif decision.action == ScalingAction.SCALE_IN:
                self._scale_in_resources(decision)

            decision.executed = True
            logger.info(f"Executed scaling action: {decision.action.value} - {decision.reason}")

        except Exception as e:
            logger.error(f"Error executing scaling decision: {e}")

    def _optimize_resources(self, decision: ScalingDecision):
        """Optimiser l'utilisation des ressources"""
        # Nettoyer la mémoire cache
        try:
            os.system("sync && echo 3 > /proc/sys/vm/drop_caches")
        except:
            pass

        # Optimiser les processus Python
        import gc
        gc.collect()

        logger.info("🧹 Resources optimized")

    def _scale_up_resources(self, decision: ScalingDecision):
        """Augmenter les ressources (CPU/Memory)"""
        # Pour l'instant, juste logger - dans un vrai système, cela pourrait
        # impliquer de changer les limites Docker ou d'ajouter des instances
        logger.info(" Scaling up resources")

    def _scale_down_resources(self, decision: ScalingDecision):
        """Réduire les ressources"""
        logger.info(" Scaling down resources")

    def _scale_out_resources(self, decision: ScalingDecision):
        """Ajouter des instances (horizontal scaling)"""
        # Intégrer avec le cloud manager pour créer de nouvelles instances
        try:
            from sharingan_app._internal.cloud_integration_manager import get_cloud_manager
            cloud = get_cloud_manager()

            # Créer une nouvelle instance EC2 par exemple
            operation = cloud.execute_cloud_operation(
                "aws", "launch_instance", "compute",
                instance_type="t2.micro"
            )

            logger.info(f" Scaled out: new instance requested (op: {operation.operation_id})")

        except Exception as e:
            logger.warning(f"Could not scale out: {e}")

    def _scale_in_resources(self, decision: ScalingDecision):
        """Réduire le nombre d'instances"""
        logger.info("🔄 Scaling in resources")

    def add_scaling_rule(self, name: str, rule: ScalingRule):
        """Ajouter une règle de mise à l'échelle personnalisée"""
        self.scaling_rules[name] = rule
        logger.info(f"Added scaling rule: {name}")

    def remove_scaling_rule(self, name: str):
        """Supprimer une règle de mise à l'échelle"""
        if name in self.scaling_rules:
            del self.scaling_rules[name]
            logger.info(f"Removed scaling rule: {name}")

    def get_scaling_status(self) -> Dict[str, Any]:
        """Obtenir le statut de l'auto-scaling"""
        return {
            "monitoring_active": self.monitoring_active,
            "rules_count": len(self.scaling_rules),
            "decisions_count": len(self.scaling_decisions),
            "current_metrics": {
                "cpu_percent": self.current_metrics.cpu_percent,
                "memory_percent": self.current_metrics.memory_percent,
                "disk_percent": self.current_metrics.disk_percent,
                "active_threads": self.current_metrics.active_threads
            },
            "recent_decisions": [
                {
                    "action": d.action.value,
                    "reason": d.reason,
                    "confidence": d.confidence,
                    "executed": d.executed
                }
                for d in self.scaling_decisions[-5:]  # Dernières 5 décisions
            ]
        }

    def predict_scaling_needs(self, future_minutes: int = 60) -> Dict[str, Any]:
        """Prédire les besoins de mise à l'échelle"""
        if len(self.metrics_history) < 10:
            return {"error": "Not enough historical data"}

        # Analyse simple des tendances
        recent_cpu = [m.cpu_percent for m in self.metrics_history[-10:]]
        recent_memory = [m.memory_percent for m in self.metrics_history[-10:]]

        cpu_trend = (recent_cpu[-1] - recent_cpu[0]) / len(recent_cpu)
        memory_trend = (recent_memory[-1] - recent_memory[0]) / len(recent_memory)

        predictions = {
            "cpu_trend_per_minute": cpu_trend,
            "memory_trend_per_minute": memory_trend,
            "predicted_cpu_in_60min": recent_cpu[-1] + (cpu_trend * future_minutes),
            "predicted_memory_in_60min": recent_memory[-1] + (memory_trend * future_minutes),
            "recommendations": []
        }

        # Recommandations basées sur les prédictions
        if predictions["predicted_cpu_in_60min"] > 80:
            predictions["recommendations"].append("Consider scaling up CPU resources")
        if predictions["predicted_memory_in_60min"] > 85:
            predictions["recommendations"].append("Consider scaling up memory resources")

        return predictions

# === FONCTIONS GLOBALES ===

_auto_scaling_manager = None

def get_auto_scaling_manager() -> AutoScalingManager:
    """Singleton pour le gestionnaire d'auto-scaling"""
    global _auto_scaling_manager
    if _auto_scaling_manager is None:
        _auto_scaling_manager = AutoScalingManager()
    return _auto_scaling_manager

def start_auto_scaling():
    """Démarrer l'auto-scaling"""
    manager = get_auto_scaling_manager()
    manager.start_monitoring()

def stop_auto_scaling():
    """Arrêter l'auto-scaling"""
    manager = get_auto_scaling_manager()
    manager.stop_monitoring()

if __name__ == "__main__":
    print(" SHARINGAN AUTO-SCALING MANAGER")
    print("=" * 60)

    manager = get_auto_scaling_manager()

    print(" STATUT ACTUEL:")
    status = manager.get_scaling_status()
    print(f"• Surveillance active: {'✅' if status['monitoring_active'] else '❌'}")
    print(f"• Règles configurées: {status['rules_count']}")
    print(f"• Décisions prises: {status['decisions_count']}")

    print("\n📈 MÉTRIQUES ACTUELLES:")
    metrics = status['current_metrics']
    print(f"• CPU: {metrics['cpu_percent']:.1f}%")
    print(f"• Mémoire: {metrics['memory_percent']:.1f}%")
    print(f"• Disque: {metrics['disk_percent']:.1f}%")
    print(f"• Threads actifs: {metrics['active_threads']}")

    print("\n🔮 PRÉDICTIONS (60 minutes):")
    predictions = manager.predict_scaling_needs()
    if "error" not in predictions:
        print(".2f")
        print(".2f")
        print("Recommandations:")
        for rec in predictions.get("recommendations", []):
            print(f"  • {rec}")
    else:
        print(f"Erreur: {predictions['error']}")

    print("\n DÉMARRAGE DE L'AUTO-SCALING...")
    start_auto_scaling()
    print("✅ Auto-scaling opérationnel en arrière-plan")

    print("\n💡 L'auto-scaling surveille maintenant les ressources")
    print("et prendra automatiquement des décisions d'optimisation.")
    print("=" * 60)