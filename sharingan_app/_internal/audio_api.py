# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Audio Processing APIs for Sharingan OS Web Interface
Speech recognition, synthesis, forensic analysis
"""

import io
import json
import logging
import os
import sys
import base64
import time
from pathlib import Path
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify

# Get internal directory
_internal_dir = Path(__file__).parent
sys.path.insert(0, str(_internal_dir))

get_audio_manager = None
try:
    from audio_processing import get_audio_manager
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

logger = logging.getLogger("audio_api")

# Create blueprint for audio processing APIs
audio_bp = Blueprint('audio', __name__, url_prefix='/api/audio')

@audio_bp.route('/speech/recognize', methods=['POST'])
def api_speech_recognize():
    """Transcribe speech to text"""
    try:
        if not AUDIO_AVAILABLE:
            return jsonify({"error": "Audio processing not available"}), 503

        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({"error": "Missing audio data"}), 400

        audio_data = data['audio']
        language = data.get('language')
        model_size = data.get('model', 'base')

        manager = get_audio_manager()
        result = manager.process_audio(audio_data, 'recognize',
                                     language=language, model_size=model_size)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Speech recognition API error: {e}")
        return jsonify({"error": str(e)}), 500

@audio_bp.route('/speech/synthesize', methods=['POST'])
def api_speech_synthesize():
    """Convert text to speech"""
    try:
        if not AUDIO_AVAILABLE:
            return jsonify({"error": "Audio processing not available"}), 503

        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Missing text data"}), 400

        text = data['text']
        language = data.get('language', 'en')
        speaker = data.get('speaker', 'default')
        speed = data.get('speed', 1.0)

        manager = get_audio_manager()
        result = manager.process_audio(None, 'synthesize',
                                     text=text, language=language,
                                     speaker=speaker, speed=speed)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Speech synthesis API error: {e}")
        return jsonify({"error": str(e)}), 500

@audio_bp.route('/analyze', methods=['POST'])
def api_audio_analyze():
    """Analyze audio content forensically"""
    try:
        if not AUDIO_AVAILABLE:
            return jsonify({"error": "Audio processing not available"}), 503

        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({"error": "Missing audio data"}), 400

        audio_data = data['audio']
        analysis_type = data.get('type', 'full')

        manager = get_audio_manager()
        result = manager.process_audio(audio_data, 'analyze',
                                     analysis_type=analysis_type)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Audio analysis API error: {e}")
        return jsonify({"error": str(e)}), 500

@audio_bp.route('/keywords/detect', methods=['POST'])
def api_keyword_detection():
    """Detect keywords in audio"""
    try:
        if not AUDIO_AVAILABLE:
            return jsonify({"error": "Audio processing not available"}), 503

        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({"error": "Missing audio data"}), 400

        audio_data = data['audio']
        keywords = data.get('keywords', [])  # Optional custom keywords

        manager = get_audio_manager()
        result = manager.process_audio(audio_data, 'analyze',
                                     analysis_type='keywords')

        # Filter by custom keywords if provided
        if keywords and 'detected_keywords' in result:
            result['detected_keywords'] = [
                kw for kw in result['detected_keywords']
                if kw['keyword'].lower() in [k.lower() for k in keywords]
            ]

        return jsonify(result)

    except Exception as e:
        logger.error(f"Keyword detection API error: {e}")
        return jsonify({"error": str(e)}), 500

@audio_bp.route('/voice/identify', methods=['POST'])
def api_voice_identification():
    """Identify speakers in audio (future feature)"""
    try:
        if not AUDIO_AVAILABLE:
            return jsonify({"error": "Audio processing not available"}), 503

        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({"error": "Missing audio data"}), 400

        # Voice identification requires ML models for speaker diarization
        # Real implementation would need librosa, pyannote, or similar
        raise NotImplementedError("Voice identification requires ML models installation")

    except Exception as e:
        logger.error(f"Voice identification API error: {e}")
        return jsonify({"error": str(e)}), 500

@audio_bp.route('/effects/process', methods=['POST'])
def api_audio_effects():
    """Apply audio effects and processing"""
    try:
        if not AUDIO_AVAILABLE:
            return jsonify({"error": "Audio processing not available"}), 503

        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({"error": "Missing audio data"}), 400

        audio_data = data['audio']
        effects = data.get('effects', [])

        # Audio effects require signal processing libraries
        # Real implementation would need scipy, librosa, or similar
        raise NotImplementedError("Audio effects require signal processing libraries")

    except Exception as e:
        logger.error(f"Audio effects API error: {e}")
        return jsonify({"error": str(e)}), 500

@audio_bp.route('/conversation/transcribe', methods=['POST'])
def api_conversation_transcribe():
    """Transcribe multi-speaker conversation"""
    try:
        if not AUDIO_AVAILABLE:
            return jsonify({"error": "Audio processing not available"}), 503

        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({"error": "Missing audio data"}), 400

        audio_data = data['audio']

        # First, transcribe the entire audio
        manager = get_audio_manager()
        transcription = manager.process_audio(audio_data, 'recognize')

        # Then, analyze for multiple speakers (simplified)
        analysis = manager.process_audio(audio_data, 'analyze',
                                       analysis_type='basic')

        # Combine results
        result = {
            'full_transcription': transcription.get('text', ''),
            'speakers_detected': 1,  # Would use diarization
            'conversation_segments': [{
                'speaker': 'Speaker 1',
                'text': transcription.get('text', ''),
                'start_time': 0,
                'end_time': analysis.get('duration', 0)
            }],
            'confidence': transcription.get('confidence', 0),
            'duration': analysis.get('duration', 0)
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"Conversation transcription API error: {e}")
        return jsonify({"error": str(e)}), 500

@audio_bp.route('/stats', methods=['GET'])
def api_audio_stats():
    """Get audio processing system statistics"""
    try:
        if not AUDIO_AVAILABLE:
            return jsonify({"error": "Audio processing not available"}), 503

        manager = get_audio_manager()
        stats = manager.get_stats()

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Audio stats API error: {e}")
        return jsonify({"error": str(e)}), 500

@audio_bp.route('/engines', methods=['GET'])
def api_audio_engines():
    """Get available audio processing engines"""
    try:
        engines_info = {
            'speech_recognition': {
                'whisper': {
                    'available': AUDIO_AVAILABLE,
                    'models': ['tiny', 'base', 'small', 'medium', 'large'] if AUDIO_AVAILABLE else [],
                    'languages': ['en', 'fr', 'de', 'es', 'it', 'pt', 'zh', 'ja', 'ko'] if AUDIO_AVAILABLE else []
                }
            },
            'speech_synthesis': {
                'coqui_tts': {
                    'available': AUDIO_AVAILABLE,
                    'models': ['xtts_v2'] if AUDIO_AVAILABLE else [],
                    'languages': ['en', 'fr', 'de', 'es', 'it', 'pt', 'zh', 'ja', 'ko'] if AUDIO_AVAILABLE else [],
                    'speakers': ['default', 'male', 'female'] if AUDIO_AVAILABLE else []
                }
            },
            'audio_analysis': {
                'librosa': {
                    'available': AUDIO_AVAILABLE,
                    'features': ['spectrogram', 'mfcc', 'chroma', 'tempo', 'pitch'] if AUDIO_AVAILABLE else [],
                    'effects_detection': ['echo', 'noise', 'compression'] if AUDIO_AVAILABLE else []
                }
            },
            'supported_formats': ['wav', 'mp3', 'flac', 'ogg', 'm4a'],
            'max_file_size': '50MB',
            'sample_rates': [8000, 16000, 22050, 44100, 48000]
        }

        return jsonify(engines_info)

    except Exception as e:
        logger.error(f"Audio engines API error: {e}")
        return jsonify({"error": str(e)}), 500

@audio_bp.route('/test', methods=['POST'])
def api_audio_test():
    """Test audio processing with sample data"""
    try:
        if not AUDIO_AVAILABLE:
            return jsonify({"error": "Audio processing not available"}), 503

        # Test with a simple text-to-speech request
        manager = get_audio_manager()
        result = manager.process_audio(None, 'synthesize',
                                     text="Audio processing system is operational.",
                                     language='en')

        return jsonify({
            'message': 'Audio processing system test completed',
            'synthesis_available': 'audio_data' in result,
            'processing_time': result.get('processing_time', 0),
            'engines_status': {
                'whisper': AUDIO_AVAILABLE,
                'tts': AUDIO_AVAILABLE,
                'librosa': AUDIO_AVAILABLE
            }
        })

    except Exception as e:
        logger.error(f"Audio test API error: {e}")
        return jsonify({"error": str(e)}), 500

# Function to register blueprint
def register_audio_apis(app):
    """Register audio processing API blueprint with Flask app"""
    app.register_blueprint(audio_bp)
    logger.info("[AUDIO API] Audio processing APIs registered")

if __name__ == "__main__":
    print("[AUDIO PROCESSING API] Audio Processing API Routes")
    print("=" * 65)
    print("Routes disponibles :")
    print("POST /api/audio/speech/recognize     - Reconnaissance vocale")
    print("POST /api/audio/speech/synthesize     - Synthèse vocale")
    print("POST /api/audio/analyze               - Analyse audio")
    print("POST /api/audio/keywords/detect       - Détection mots-clés")
    print("POST /api/audio/voice/identify        - Identification voix")
    print("POST /api/audio/effects/process       - Effets audio")
    print("POST /api/audio/conversation/transcribe - Transcription conversation")
    print("GET  /api/audio/stats                 - Statistiques système")
    print("GET  /api/audio/engines               - Moteurs disponibles")
    print("POST /api/audio/test                  - Test système")