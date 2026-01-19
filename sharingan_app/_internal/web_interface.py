#!/usr/bin/env python3
"""Sharingan OS - Web Interface Module"""

import sys
import os
import json
import time
import threading
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit

_internal_dir = Path(__file__).parent
sys.path.insert(0, str(_internal_dir))

from sharingan_os import SharinganOS, sharingan
from ai_providers import get_provider_manager, ai_chat
from system_consciousness import SystemConsciousness
from clarification_layer import get_clarifier
from neutral_ai import get_neutral_mode, NeutralSystemPrompt
from tool_schemas import get_tool_schema, get_system_prompt_for_agent, get_all_tool_schemas
from lsp_diagnostics import get_diagnostic_manager
from context_manager import get_context_manager
from ai_memory_manager import get_memory_manager, get_shared_memory
from genome_memory import get_genome_memory
from enhanced_system_consciousness import get_enhanced_consciousness

import logging

logger = logging.getLogger("web_interface")


class SharinganWebInterface:
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.app = Flask(__name__)

        # Initialize Socket.IO with CORS support
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')

        self.setup_routes()
        self.setup_socket_events()

        # Register Genome APIs
        try:
            from genome_api import genome_bp
            self.app.register_blueprint(genome_bp)
            logger.info("[WEB] Genome APIs registered")
        except ImportError:
            logger.warning("[WEB] Genome APIs not available")

        # Register Computer Vision APIs
        try:
            from cv_api import cv_bp
            self.app.register_blueprint(cv_bp)
            logger.info("[WEB] Computer Vision APIs registered")
        except ImportError:
            logger.warning("[WEB] Computer Vision APIs not available")

        # Register Audio Processing APIs
        try:
            from audio_api import audio_bp
            self.app.register_blueprint(audio_bp)
            logger.info("[WEB] Audio Processing APIs registered")
        except ImportError:
            logger.warning("[WEB] Audio Processing APIs not available")

        # Start real-time metrics broadcasting
        self.start_metrics_broadcast()

        logger.info("[WEB] Web Interface with Socket.IO initialized")

    def setup_routes(self):
        """Setup basic Flask routes"""

        @self.app.route('/')
        def home():
            return self._get_main_html()

        @self.app.route('/dashboard')
        def dashboard():
            return self._get_main_html()

        @self.app.route('/chat')
        def chat():
            return self._get_main_html()

        @self.app.route('/api/status')
        def api_status():
            try:
                return jsonify({
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('/').percent,
                    "network_connections": len(psutil.net_connections()),
                    "timestamp": time.time()
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/api/test')
        def api_test():
            return jsonify({
                "message": "API Sharingan opérationnelle",
                "status": "ok",
                "timestamp": time.time()
            })

    def setup_socket_events(self):
        """Configure Socket.IO event handlers"""

        @self.socketio.on('connect')
        def handle_connect():
            logger.info("[WEB] Client connected")
            self.socketio.emit('system_log', {'message': 'Connected to Sharingan OS', 'type': 'success'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info("[WEB] Client disconnected")

        @self.socketio.on('request_metrics')
        def handle_request_metrics():
            """Send current system metrics to client"""
            metrics = self.get_system_metrics()
            self.socketio.emit('system_metrics', metrics)

        @self.socketio.on('request_activities')
        def handle_request_activities():
            """Send recent activities to client"""
            activities = self.get_recent_activities()
            self.socketio.emit('activities_update', activities)

    def start_metrics_broadcast(self):
        """Start broadcasting system metrics every 5 seconds"""

        def broadcast_metrics():
            while True:
                try:
                    metrics = self.get_system_metrics()
                    self.socketio.emit('system_metrics', metrics)

                    activities = self.get_recent_activities()
                    self.socketio.emit('activities_update', activities)

                    # Broadcast system logs
                    logs = self.get_recent_logs()
                    for log in logs:
                        self.socketio.emit('system_log', log)

                    time.sleep(5)  # Broadcast every 5 seconds

                except Exception as e:
                    logger.error(f"[WEB] Error broadcasting metrics: {e}")
                    time.sleep(5)

        # Start broadcast thread
        broadcast_thread = threading.Thread(target=broadcast_metrics, daemon=True)
        broadcast_thread.start()
        logger.info("[WEB] Metrics broadcasting thread started")

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent

            # Network connections (simplified)
            network_connections = len(psutil.net_connections())

            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'network_connections': network_connections,
                'timestamp': time.time()
            }

        except Exception as e:
            logger.error(f"[WEB] Error getting system metrics: {e}")
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'network_connections': 0,
                'timestamp': time.time(),
                'error': str(e)
            }

    def get_recent_activities(self) -> list:
        """Get recent system activities"""
        # Mock activities for now - in real implementation, this would come from system logs
        activities = [
            {
                'type': 'system',
                'icon': 'Activity',
                'text': 'Système démarré avec succès',
                'time': time.strftime('%H:%M:%S')
            },
            {
                'type': 'ai',
                'icon': 'Brain',
                'text': 'Soul consciousness level: 4.0',
                'time': time.strftime('%H:%M:%S')
            },
            {
                'type': 'genome',
                'icon': 'Database',
                'text': 'Genome evolution completed',
                'time': time.strftime('%H:%M:%S')
            }
        ]
        return activities

    def get_recent_logs(self) -> list:
        """Get recent system logs"""
        # Mock logs - in real implementation, this would come from logging system
        logs = [
            {'message': f'[{time.strftime("%H:%M:%S")}] System operational', 'type': 'info'},
            {'message': f'[{time.strftime("%H:%M:%S")}] AI providers loaded', 'type': 'success'}
        ]
        return logs

    def _get_main_html(self):
        """Return main HTML page (simplified for now)"""
        return """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sharingan OS - Interface Web</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .status { color: green; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Sharingan OS</h1>
        <p class="status">✅ Système Opérationnel</p>
        <p>Interface web en développement. Utilisez l'interface React sur le port 3737.</p>
    </div>

    <div>
        <h2>APIs Disponibles :</h2>
        <ul>
            <li><a href="/api/status">/api/status</a> - Métriques système</li>
            <li><a href="/api/genome/genes">/api/genome/genes</a> - Gènes Genome</li>
            <li><a href="/api/genome/evolution">/api/genome/evolution</a> - Statistiques évolution</li>
            <li><a href="/api/test">/api/test</a> - Test API</li>
        </ul>
    </div>
</body>
</html>"""

    def start(self):
        """Démarrer le serveur web avec Socket.IO"""
        logger.info(f"[WEB] Starting web server on {self.host}:{self.port}")
        self.socketio.run(self.app, host=self.host, port=self.port, debug=False, allow_unsafe_werkzeug=True)


_web_interface = None

def get_web_interface() -> SharinganWebInterface:
    """Obtenir l'instance singleton de l'interface web"""
    global _web_interface
    if _web_interface is None:
        _web_interface = SharinganWebInterface()
    return _web_interface


if __name__ == "__main__":
    print("[WEB] SHARINGAN WEB INTERFACE")
    print("=" * 60)
    print("Interface accessible sur: http://localhost:8080")
    print()
    interface = get_web_interface()
    try:
        interface.start()
    except KeyboardInterrupt:
        print("\n[STOP] Interface web arrêtée")
    except Exception as e:
        print(f"[ERROR] Erreur: {e}")
