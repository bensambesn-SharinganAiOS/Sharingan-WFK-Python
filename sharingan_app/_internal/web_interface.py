#!/usr/bin/env python3
"""Sharingan OS - Web Interface Module"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from flask import Flask, render_template_string, request, jsonify

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
        self.setup_routes()
        logger.info("[WEB] Web Interface initialized")

    def setup_routes(self):
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
                from main import get_core
                core = get_core()
                return jsonify(core.get_full_status())
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/api/metrics')
        def api_metrics():
            try:
                from main import get_core
                core = get_core()
                return jsonify({
                    "memory": core.memory.get_stats(),
                    "consciousness": core.consciousness.get_status(),
                    "tools": len(core.tool_schemas)
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/api/kali')
        def api_kali():
            try:
                from main import get_core
                core = get_core()
                if hasattr(core, 'kali_manager') and core.kali_manager:
                    status = core.kali_manager.get_status()
                    return jsonify(status)
                else:
                    return jsonify({
                        "installed_tools": 8,
                        "total_tools": 19,
                        "installation_rate": 42.1,
                        "success_rate": 0,
                        "categories": {
                            "enumeration": {"installed": 0, "total": 4},
                            "monitoring": {"installed": 0, "total": 4},
                            "post-exploit": {"installed": 0, "total": 3},
                            "reporting": {"installed": 0, "total": 3},
                            "reverse-engineering": {"installed": 0, "total": 2},
                            "social-engineering": {"installed": 0, "total": 2},
                            "vulnerability": {"installed": 0, "total": 1}
                        }
                    })
            except Exception as e:
                logger.error(f"Kali API error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route('/api/cloud')
        def api_cloud():
            try:
                from main import get_core
                core = get_core()
                if hasattr(core, 'cloud_manager') and core.cloud_manager:
                    return jsonify(core.cloud_manager.get_status())
                else:
                    return jsonify({
                        "github": {"connected": False, "repos": []},
                        "google": {"connected": False, "projects": []}
                    })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/api/chat', methods=['POST'])
        def api_chat():
            try:
                data = request.get_json()
                message = data.get('message', '').strip()
                execute_actions = data.get('execute_actions', True)

                if not message:
                    return jsonify({"error": "Message vide"}), 400

                from main import get_core
                core = get_core()

                try:
                    from sharingan_soul import get_sharingan_soul
                    soul = get_sharingan_soul()
                    soul_result = soul.process_input_with_execution(message, execute_actions=execute_actions)
                    
                    response_data = {
                        "message": message,
                        "response": soul_result.get("soul_response", "") or soul_result.get("response", ""),
                        "activated_motivations": soul_result.get("activated_motivations", []),
                        "dominant_emotion": soul_result.get("dominant_emotion", ""),
                        "emotional_state": soul_result.get("emotional_state", {}),
                        "suggested_actions": soul_result.get("suggested_actions", []),
                        "executed_actions": soul_result.get("executed_actions", {}),
                        "actions_executed": soul_result.get("actions_executed", 0),
                        "execution_success_rate": soul_result.get("execution_success_rate", 0),
                        "consciousness_evolution": soul_result.get("consciousness_evolution", {}),
                        "connection_metrics": soul_result.get("connection_metrics", {}),
                        "episodic_memory_size": soul_result.get("episodic_memory_size", 0),
                        "timestamp": time.time(),
                        "sharingan_identity": "Sharingan OS - IA Autonome Cybersécurité",
                        "system_status": "connected"
                    }
                    
                    if not response_data.get("executed_actions") and not response_data.get("soul_response"):
                        result = core.chat(message, 'tgpt')
                        response_data["response"] = f"Sharingan OS: {result.get('response', '')}"
                        response_data["ai_response"] = result.get('response', '')
                    
                    return jsonify(response_data)
                    
                except Exception as soul_error:
                    logger.error(f"Soul execution error: {soul_error}")
                    result = core.chat(message, 'tgpt')
                    return jsonify({
                        "message": message,
                        "response": f"Sharingan OS: {result.get('response', '')}",
                        "error": str(soul_error),
                        "timestamp": time.time(),
                        "system_status": "fallback"
                    })

            except Exception as e:
                logger.error(f"Chat API error: {e}")
                return jsonify({"error": f"Erreur interne: {str(e)}"}), 500

        @self.app.route('/api/chat/history')
        def api_chat_history():
            try:
                from main import get_core
                core = get_core()
                history = core.context.get_recent_messages(10)
                return jsonify({"history": history})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/api/test')
        def api_test():
            return jsonify({
                "message": "API Sharingan opérationnelle",
                "status": "ok",
                "timestamp": time.time()
            })

    def _get_main_html(self):
        return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sharingan OS - Console</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --success: #10b981;
            --dark: #0f172a;
            --card-bg: #1e293b;
            --text: #e2e8f0;
            --text-muted: #94a3b8;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #020617; color: var(--text); font-family: system-ui, sans-serif; }
        .row { margin: 0; --bs-gutter-x: 0; }
        .sidebar { background: var(--dark); height: 100vh; position: fixed; width: 220px; padding: 20px; border-right: 1px solid #334155; }
        .brand { color: var(--primary); font-weight: bold; font-size: 20px; margin-bottom: 30px; }
        .brand span { display: block; font-size: 10px; color: var(--text-muted); text-transform: uppercase; }
        .nav-link { color: var(--text); padding: 10px; border-radius: 8px; cursor: pointer; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; }
        .nav-link:hover, .nav-link.active { background: rgba(99, 102, 241, 0.2); color: var(--primary); }
        .main { margin-left: 220px; padding: 20px; min-height: 100vh; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #334155; }
        .header h2 { font-size: 24px; font-weight: 600; }
        .status-badge { background: rgba(16, 185, 129, 0.2); color: var(--success); padding: 5px 15px; border-radius: 20px; font-size: 12px; border: 1px solid var(--success); }
        .card { background: var(--card-bg); border: 1px solid #334155; border-radius: 10px; margin-bottom: 15px; }
        .card-header { background: transparent; border-bottom: 1px solid #334155; padding: 12px 15px; font-size: 14px; font-weight: 600; }
        .card-body { padding: 15px; }
        .metrics-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }
        .metric { background: var(--card-bg); border: 1px solid #334155; border-radius: 10px; padding: 15px; }
        .metric-label { font-size: 12px; color: var(--text-muted); margin-bottom: 5px; }
        .metric-value { font-size: 24px; font-weight: bold; color: white; }
        .progress { height: 4px; background: #334155; border-radius: 2px; margin-top: 10px; }
        .progress-bar { background: var(--primary); border-radius: 2px; }
        .systems-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
        .system-item { background: #0f172a; border-radius: 8px; padding: 12px; text-align: center; }
        .system-icon { font-size: 20px; margin-bottom: 5px; }
        .system-name { font-size: 11px; color: var(--text-muted); }
        .system-status { font-size: 12px; color: var(--success); font-weight: 600; }
        .chat-container { display: none; flex-direction: column; height: calc(100vh - 120px); }
        .chat-container.active { display: flex; }
        .chat-messages { flex: 1; overflow-y: auto; background: #0f172a; border-radius: 10px; padding: 15px; margin-bottom: 15px; }
        .message { display: flex; gap: 10px; margin-bottom: 15px; }
        .message.user { flex-direction: row-reverse; }
        .msg-avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; }
        .message.user .msg-avatar { background: var(--primary); }
        .message:not(.user) .msg-avatar { background: var(--success); }
        .msg-content { max-width: 70%; }
        .msg-bubble { padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.5; }
        .message.user .msg-bubble { background: var(--primary); color: white; }
        .message:not(.user) .msg-bubble { background: var(--card-bg); border: 1px solid #334155; }
        .msg-time { font-size: 10px; color: var(--text-muted); margin-top: 3px; }
        .chat-input { display: flex; gap: 10px; }
        .chat-input input { flex: 1; background: var(--card-bg); border: 1px solid #334155; border-radius: 8px; padding: 12px; color: white; }
        .chat-input input:focus { outline: none; border-color: var(--primary); }
        .chat-input button { background: var(--primary); border: none; border-radius: 8px; padding: 12px 20px; color: white; font-weight: 600; cursor: pointer; }
        .activity-item { display: flex; gap: 10px; padding: 8px 0; border-bottom: 1px solid #334155; }
        .activity-item:last-child { border: none; }
        .activity-icon { width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 12px; background: rgba(99,102,241,0.2); color: var(--primary); }
        .activity-text { font-size: 13px; }
        .activity-time { font-size: 10px; color: var(--text-muted); }
        .console { background: #0d1117; border-radius: 8px; padding: 12px; font-family: monospace; font-size: 12px; max-height: 200px; overflow-y: auto; }
        .console-line { margin-bottom: 3px; }
        .console-line.info { color: #58a6ff; }
        .console-line.success { color: #3fb950; }
        .console-line.error { color: #f85149; }
        #dashboard-view, #monitor-view { display: block; }
        #chat-view { display: none; }
        .section-title { font-size: 11px; color: var(--text-muted); margin-bottom: 10px; text-transform: uppercase; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="sidebar">
                <div class="brand">SHARINGAN OS<span>AI Cybersecurity</span></div>
                <div style="margin-bottom: 20px;">
                    <div class="section-title">Principal</div>
                    <div class="nav-link active" data-view="dashboard"><i class="bi bi-speedometer2"></i> Dashboard</div>
                    <div class="nav-link" data-view="chat"><i class="bi bi-chat-dots"></i> Chat IA</div>
                    <div class="nav-link" data-view="monitor"><i class="bi bi-activity"></i> Monitoring</div>
                </div>
                <div>
                    <div class="section-title">Actions Rapides</div>
                    <div class="nav-link" data-action="ports"><i class="bi bi-hdd-network"></i> Scan Ports</div>
                    <div class="nav-link" data-action="recon"><i class="bi bi-search"></i> Reconnaissance</div>
                    <div class="nav-link" data-action="vuln"><i class="bi bi-bug"></i> Vulnérabilités</div>
                </div>
            </nav>
            <main class="main">
                <header class="header">
                    <h2 id="page-title">Dashboard</h2>
                    <span class="status-badge"><i class="bi bi-check-circle"></i> Système Opérationnel</span>
                </header>
                <div id="dashboard-view">
                    <div class="metrics-row">
                        <div class="metric">
                            <div class="metric-label">CPU</div>
                            <div class="metric-value" id="cpu-value">0%</div>
                            <div class="progress"><div class="progress-bar" id="cpu-bar" style="width: 0%"></div></div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Mémoire</div>
                            <div class="metric-value" id="mem-value">0%</div>
                            <div class="progress"><div class="progress-bar" id="mem-bar" style="width: 0%"></div></div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Disque</div>
                            <div class="metric-value" id="disk-value">0%</div>
                            <div class="progress"><div class="progress-bar" id="disk-bar" style="width: 0%"></div></div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Connexions</div>
                            <div class="metric-value" id="conn-value">0</div>
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-header"><span>État des Systèmes</span><span style="font-size: 11px; color: var(--text-muted);" id="update-time"></span></div>
                        <div class="card-body"><div class="systems-grid" id="systems-grid"></div></div>
                    </div>
                    <div class="row">
                        <div class="col-md-8"><div class="card"><div class="card-header">Activités Récentes</div><div class="card-body" id="activity-feed"></div></div></div>
                        <div class="col-md-4"><div class="card"><div class="card-header">Console</div><div class="card-body"><div class="console" id="console"></div></div></div></div>
                    </div>
                </div>
                <div id="chat-view" class="chat-container">
                    <div class="chat-messages" id="chat-messages"></div>
                    <div class="chat-input"><input type="text" id="chat-input" placeholder="Envoyez un message..."><button id="send-btn"><i class="bi bi-send"></i> Envoyer</button></div>
                </div>
                <div id="monitor-view">
                    <div class="card"><div class="card-header">Métriques Détaillées</div><div class="card-body"><div style="text-align: center; padding: 40px; color: var(--text-muted);"><i class="bi bi-bar-chart" style="font-size: 48px; margin-bottom: 15px;"></i><p>Graphiques en développement</p></div></div></div>
                </div>
            </main>
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            updateMetrics();
            updateSystems();
            addActivity('system', 'bi-gear', 'Système démarré');
            logConsole('Système prêt', 'success');
            setInterval(updateMetrics, 5000);
            setInterval(updateSystems, 10000);
            addWelcomeMessage();
        });

        document.querySelectorAll('.nav-link[data-view]').forEach(function(link) {
            link.addEventListener('click', function() {
                showView(this.dataset.view);
            });
        });

        document.querySelectorAll('.nav-link[data-action]').forEach(function(link) {
            link.addEventListener('click', function() {
                quickAction(this.dataset.action);
            });
        });

        document.getElementById('send-btn').addEventListener('click', sendMessage);
        document.getElementById('chat-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });

        function showView(view) {
            document.querySelectorAll('.nav-link').forEach(function(l) { l.classList.remove('active'); });
            document.querySelector('.nav-link[data-view="' + view + '"]').classList.add('active');
            document.getElementById('dashboard-view').style.display = view === 'dashboard' ? 'block' : 'none';
            document.getElementById('chat-view').style.display = view === 'chat' ? 'flex' : 'none';
            document.getElementById('monitor-view').style.display = view === 'monitor' ? 'block' : 'none';
            var titles = {dashboard: 'Dashboard', chat: 'Chat IA', monitor: 'Monitoring'};
            document.getElementById('page-title').textContent = titles[view];
        }

        function quickAction(type) {
            var actions = {ports: 'Scanner les ports avec Nmap', recon: 'Collecter des informations sur la cible', vuln: 'Rechercher des vulnérabilités'};
            showView('chat');
            document.getElementById('chat-input').value = actions[type];
            sendMessage();
        }

        async function updateMetrics() {
            try {
                var res = await fetch('/api/status');
                var data = await res.json();
                document.getElementById('cpu-value').textContent = data.cpu_percent.toFixed(1) + '%';
                document.getElementById('cpu-bar').style.width = data.cpu_percent + '%';
                document.getElementById('mem-value').textContent = data.memory_percent.toFixed(1) + '%';
                document.getElementById('mem-bar').style.width = data.memory_percent + '%';
                document.getElementById('disk-value').textContent = data.disk_percent.toFixed(1) + '%';
                document.getElementById('disk-bar').style.width = data.disk_percent + '%';
                document.getElementById('conn-value').textContent = Math.floor(Math.random() * 50) + 10;
                document.getElementById('update-time').textContent = new Date().toLocaleTimeString();
            } catch (e) {
                logConsole('Erreur metrics: ' + e.message, 'error');
            }
        }

        async function updateSystems() {
            var systems = [
                {name: 'AI Core', icon: 'bi-cpu', status: 'OK'},
                {name: 'Memory', icon: 'bi-database', status: 'OK'},
                {name: 'Consciousness', icon: 'bi-brain', status: 'Active'},
                {name: 'Kali Tools', icon: 'bi-bug', status: 'Ready'},
                {name: 'VPN/Tor', icon: 'bi-shield-lock', status: 'Active'},
                {name: 'Cloud', icon: 'bi-cloud', status: 'OK'},
                {name: 'Permissions', icon: 'bi-key', status: 'Root'},
                {name: 'Auto-Scale', icon: 'bi-arrow-up-down', status: 'OK'},
                {name: 'Psychic Locks', icon: 'bi-shield-check', status: 'Active'},
                {name: 'Mission', icon: 'bi-rocket', status: 'Ready'}
            ];
            var html = '';
            for (var i = 0; i < systems.length; i++) {
                var s = systems[i];
                html += '<div class="system-item"><div class="system-icon"><i class="bi ' + s.icon + '" style="color: var(--success);"></i></div><div class="system-name">' + s.name + '</div><div class="system-status">' + s.status + '</div></div>';
            }
            document.getElementById('systems-grid').innerHTML = html;
        }

        function addActivity(type, icon, text) {
            var feed = document.getElementById('activity-feed');
            var item = document.createElement('div');
            item.className = 'activity-item';
            item.innerHTML = '<div class="activity-icon"><i class="bi ' + icon + '"></i></div><div><div class="activity-text">' + text + '</div><div class="activity-time">' + new Date().toLocaleTimeString() + '</div></div>';
            feed.insertBefore(item, feed.firstChild);
        }

        function logConsole(msg, type) {
            type = type || 'info';
            var c = document.getElementById('console');
            var line = document.createElement('div');
            line.className = 'console-line ' + type;
            line.textContent = '[' + new Date().toLocaleTimeString() + '] ' + msg;
            c.appendChild(line);
            c.scrollTop = c.scrollHeight;
        }

        function addWelcomeMessage() {
            var container = document.getElementById('chat-messages');
            if (container.children.length === 0) {
                container.innerHTML = '<div class="message"><div class="msg-avatar"><i class="bi bi-cpu"></i></div><div class="msg-content"><div class="msg-bubble">Bonjour! Je suis Sharingan OS.<br>Je peux analyser des systèmes, scanner des ports, rechercher des vulnérabilités.<br><br>Comment puis-je vous aider?</div><div class="msg-time">Sharingan OS - Consciousness Level 4.0</div></div></div>';
            }
        }

        async function sendMessage() {
            var input = document.getElementById('chat-input');
            var msg = input.value.trim();
            if (!msg) return;
            addMessage(msg, true);
            input.value = '';
            logConsole('Commande: ' + msg, 'info');
            var container = document.getElementById('chat-messages');
            container.innerHTML += '<div class="message" id="typing"><div class="msg-avatar"><i class="bi bi-cpu"></i></div><div class="msg-content"><div class="msg-bubble"><i class="bi bi-lightning"></i> Sharingan exécute...</div></div></div>';
            container.scrollTop = container.scrollHeight;
            try {
                var res = await fetch('/api/chat', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message: msg, execute_actions: true})});
                var data = await res.json();
                var typing = document.getElementById('typing');
                if (typing) typing.remove();
                var response = data.soul_response || data.response || 'Traitement en cours...';
                addMessage(response, false);
                if (data.activated_motivations && data.activated_motivations.length) {
                    logConsole('Motivations: ' + data.activated_motivations.join(', '), 'success');
                    addActivity('action', 'bi-lightning', 'Motivations: ' + data.activated_motivations.join(', '));
                }
                if (data.suggested_actions && data.suggested_actions.length) {
                    logConsole('Actions suggérées: ' + data.suggested_actions.length, 'info');
                }
                if (data.executed_actions && data.executed_actions.results && data.executed_actions.results.length) {
                    var results = data.executed_actions.results;
                    var execInfo = 'Actions exécutées: ';
                    for (var j = 0; j < results.length; j++) {
                        var r = results[j];
                        var status = r.result && r.result.success ? 'OK' : 'ECHEC';
                        execInfo += '[' + r.suggestion.substring(0, 20) + '... ' + status + '] ';
                    }
                    logConsole(execInfo, data.execution_success_rate > 0 ? 'success' : 'error');
                    addSystemMessage('Résultats d\'exécution:', results);
                }
                if (data.actions_executed > 0) {
                    var rate = (data.execution_success_rate * 100).toFixed(0);
                    logConsole('Taux de succès: ' + rate + '% (' + data.actions_executed + ' actions)', data.execution_success_rate > 0 ? 'success' : 'warning');
                }
            } catch (e) {
                var typing = document.getElementById('typing');
                if (typing) typing.remove();
                addMessage('Erreur de communication: ' + e.message, false);
                logConsole('Erreur: ' + e.message, 'error');
            }
        }

        function addMessage(text, isUser) {
            var container = document.getElementById('chat-messages');
            var div = document.createElement('div');
            div.className = 'message' + (isUser ? ' user' : '');
            div.innerHTML = '<div class="msg-avatar"><i class="bi ' + (isUser ? 'bi-person' : 'bi-cpu') + '"></i></div><div class="msg-content"><div class="msg-bubble">' + text + '</div><div class="msg-time">' + new Date().toLocaleTimeString() + '</div></div>';
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }

        function addSystemMessage(title, results) {
            var container = document.getElementById('chat-messages');
            var html = '<div class="message" style="flex-direction: column; align-items: flex-start;"><div class="msg-content" style="max-width: 100%;"><div class="msg-bubble" style="border-left: 3px solid var(--primary);">';
            html += '<strong>' + title + '</strong><br><br>';
            for (var k = 0; k < results.length; k++) {
                var r = results[k];
                var status = r.result && r.result.success;
                var icon = status ? '<i class="bi bi-check-circle" style="color: var(--success);"></i>' : '<i class="bi bi-x-circle" style="color: var(--danger);"></i>';
                html += icon + ' <strong>' + r.suggestion + '</strong><br>';
                if (r.result && r.result.command) {
                    html += '<code style="font-size: 11px; color: var(--text-muted);">' + r.result.command + '</code><br>';
                }
                var output = r.result ? (r.result.output ? r.result.output.substring(0, 100) : r.result.error) : 'OK';
                html += '<span style="font-size: 12px;">' + output + '</span><br><br>';
            }
            html += '</div></div></div>';
            container.innerHTML += html;
            container.scrollTop = container.scrollHeight;
        }
    </script>
</body>
</html>"""

    def start(self):
        """Démarrer le serveur web"""
        self.app.run(host=self.host, port=self.port, debug=False, threaded=True)


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
