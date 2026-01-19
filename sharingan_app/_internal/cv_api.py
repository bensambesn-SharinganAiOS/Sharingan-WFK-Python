# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Computer Vision APIs for Sharingan OS Web Interface
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

get_cv_manager = None
try:
    from computer_vision import get_cv_manager
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False

logger = logging.getLogger("cv_api")

# Create blueprint for computer vision APIs
cv_bp = Blueprint('computer_vision', __name__, url_prefix='/api/cv')

@cv_bp.route('/ocr', methods=['POST'])
def api_ocr():
    """Extract text from image using OCR"""
    try:
        if not CV_AVAILABLE:
            return jsonify({"error": "Computer vision not available"}), 503

        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "Missing image data"}), 400

        image_data = data['image']
        lang = data.get('lang', 'eng')
        engine = data.get('engine', 'auto')

        # Handle different image formats
        if isinstance(image_data, str):
            # Base64 encoded image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = io.BytesIO(image_bytes)
        else:
            return jsonify({"error": "Invalid image format"}), 400

        manager = get_cv_manager()
        result = manager.ocr_processor.extract_text(image, engine=engine, lang=lang)

        return jsonify(result)

    except Exception as e:
        logger.error(f"OCR API error: {e}")
        return jsonify({"error": str(e)}), 500

@cv_bp.route('/analyze', methods=['POST'])
def api_analyze_image():
    """Complete image analysis"""
    try:
        if not CV_AVAILABLE:
            return jsonify({"error": "Computer vision not available"}), 503

        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "Missing image data"}), 400

        image_data = data['image']
        analysis_type = data.get('type', 'full')

        # Handle different image formats
        if isinstance(image_data, str):
            # Base64 encoded image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = io.BytesIO(image_bytes)
        else:
            return jsonify({"error": "Invalid image format"}), 400

        manager = get_cv_manager()
        result = manager.process_image(image, analysis_type)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Image analysis API error: {e}")
        return jsonify({"error": str(e)}), 500

@cv_bp.route('/screenshot/analyze', methods=['POST'])
def api_analyze_screenshot():
    """Analyze browser screenshot for actionable elements"""
    try:
        if not CV_AVAILABLE:
            return jsonify({"error": "Computer vision not available"}), 503

        data = request.get_json()
        if not data or 'screenshot' not in data:
            return jsonify({"error": "Missing screenshot data"}), 400

        screenshot_data = data['screenshot']

        manager = get_cv_manager()
        result = manager.process_image(screenshot_data, 'screenshot')

        return jsonify(result)

    except Exception as e:
        logger.error(f"Screenshot analysis API error: {e}")
        return jsonify({"error": str(e)}), 500

@cv_bp.route('/stats', methods=['GET'])
def api_cv_stats():
    """Get computer vision system statistics"""
    try:
        if not CV_AVAILABLE:
            return jsonify({"error": "Computer vision not available"}), 503

        manager = get_cv_manager()
        stats = manager.get_stats()

        return jsonify(stats)

    except Exception as e:
        logger.error(f"CV stats API error: {e}")
        return jsonify({"error": str(e)}), 500

@cv_bp.route('/engines', methods=['GET'])
def api_available_engines():
    """Get available OCR engines and capabilities"""
    try:
        if not CV_AVAILABLE:
            return jsonify({"error": "Computer vision not available"}), 503

        manager = get_cv_manager()

        engines_info = {
            'ocr_engines': list(manager.ocr_processor.engines.keys()),
            'object_detection': manager.image_analyzer.object_detector is not None,
            'capabilities': {
                'text_extraction': bool(manager.ocr_processor.engines),
                'object_detection': manager.image_analyzer.object_detector is not None,
                'color_analysis': True,
                'quality_assessment': True,
                'screenshot_analysis': True,
                'ui_element_detection': True
            },
            'supported_formats': ['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
            'max_image_size': '10MB'
        }

        return jsonify(engines_info)

    except Exception as e:
        logger.error(f"Engines info API error: {e}")
        return jsonify({"error": str(e)}), 500

@cv_bp.route('/detect/objects', methods=['POST'])
def api_detect_objects():
    """Detect objects in image"""
    try:
        if not CV_AVAILABLE:
            return jsonify({"error": "Computer vision not available"}), 503

        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "Missing image data"}), 400

        image_data = data['image']
        confidence_threshold = data.get('confidence', 0.5)

        # Handle different image formats
        if isinstance(image_data, str):
            # Base64 encoded image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = io.BytesIO(image_bytes)
        else:
            return jsonify({"error": "Invalid image format"}), 400

        manager = get_cv_manager()
        result = manager.process_image(image, 'objects')

        # Filter by confidence threshold
        if 'objects' in result:
            result['objects'] = [
                obj for obj in result['objects']
                if obj.get('confidence', 0) >= confidence_threshold
            ]

        return jsonify(result)

    except Exception as e:
        logger.error(f"Object detection API error: {e}")
        return jsonify({"error": str(e)}), 500

@cv_bp.route('/ui/analyze', methods=['POST'])
def api_analyze_ui():
    """Analyze UI elements in screenshot"""
    try:
        if not CV_AVAILABLE:
            return jsonify({"error": "Computer vision not available"}), 503

        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "Missing image data"}), 400

        image_data = data['image']

        # Handle different image formats
        if isinstance(image_data, str):
            # Base64 encoded image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = io.BytesIO(image_bytes)
        else:
            return jsonify({"error": "Invalid image format"}), 400

        manager = get_cv_manager()
        analysis = manager.screenshot_analyzer.analyze_screenshot(image_data)

        # Focus on UI elements
        ui_result = {
            'ui_elements': analysis.get('ui_elements', {}),
            'actionable_elements': analysis.get('actionable_elements', []),
            'content_type': analysis.get('content_type', 'unknown'),
            'dimensions': analysis.get('dimensions'),
            'processing_time': analysis.get('processing_time', 0)
        }

        return jsonify(ui_result)

    except Exception as e:
        logger.error(f"UI analysis API error: {e}")
        return jsonify({"error": str(e)}), 500

@cv_bp.route('/batch/analyze', methods=['POST'])
def api_batch_analyze():
    """Batch process multiple images"""
    try:
        if not CV_AVAILABLE:
            return jsonify({"error": "Computer vision not available"}), 503

        data = request.get_json()
        if not data or 'images' not in data:
            return jsonify({"error": "Missing images data"}), 400

        images = data['images']
        analysis_type = data.get('type', 'ocr')

        if not isinstance(images, list) or len(images) > 10:
            return jsonify({"error": "Invalid images list (max 10)"}), 400

        manager = get_cv_manager()
        results = []

        for i, image_data in enumerate(images):
            try:
                result = manager.process_image(image_data, analysis_type)
                results.append({
                    'index': i,
                    'success': result.get('success', False),
                    'data': result
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'success': False,
                    'error': str(e)
                })

        return jsonify({
            'total_processed': len(results),
            'successful': sum(1 for r in results if r['success']),
            'results': results
        })

    except Exception as e:
        logger.error(f"Batch analysis API error: {e}")
        return jsonify({"error": str(e)}), 500

# Function to register blueprint
def register_cv_apis(app):
    """Register computer vision API blueprint with Flask app"""
    app.register_blueprint(cv_bp)
    logger.info("[CV API] Computer vision APIs registered")

if __name__ == "__main__":
    print("[COMPUTER VISION API] Computer Vision API Routes")
    print("=" * 60)
    print("Routes disponibles :")
    print("POST /api/cv/ocr              - Extraction OCR")
    print("POST /api/cv/analyze          - Analyse complète image")
    print("POST /api/cv/screenshot/analyze - Analyse screenshot")
    print("POST /api/cv/detect/objects   - Détection d'objets")
    print("POST /api/cv/ui/analyze       - Analyse éléments UI")
    print("POST /api/cv/batch/analyze    - Traitement par lots")
    print("GET  /api/cv/stats            - Statistiques système")
    print("GET  /api/cv/engines          - Moteurs disponibles")