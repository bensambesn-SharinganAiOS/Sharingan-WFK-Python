# -*- coding: utf-8 -*-
"""
Computer Vision Integration for Sharingan OS
OCR, image recognition, screenshot analysis, object detection
"""

import os
import cv2
import numpy as np
import base64
import time
from PIL import Image
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import logging
import io

# Optional imports with fallbacks
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import paddleocr
    PADDLE_OCR_AVAILABLE = True
except ImportError:
    PADDLE_OCR_AVAILABLE = False

try:
    import torch
    import torchvision
    from torchvision.models.detection import fasterrcnn_resnet50_fpn
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

logger = logging.getLogger("computer_vision")

class OCRProcessor:
    """
    Advanced OCR processing with multiple engines
    """

    def __init__(self):
        self.engines = {}
        self.stats = {
            'total_processed': 0,
            'tesseract_used': 0,
            'paddle_used': 0,
            'accuracy_score': 0.0
        }

        # Initialize Tesseract
        if TESSERACT_AVAILABLE:
            try:
                pytesseract.get_tesseract_version()
                self.engines['tesseract'] = True
                logger.info("Tesseract OCR engine initialized")
            except Exception as e:
                logger.warning(f"Tesseract initialization failed: {e}")

        # Initialize PaddleOCR
        if PADDLE_OCR_AVAILABLE:
            try:
                self.paddle_ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang='en')
                self.engines['paddle'] = True
                logger.info("PaddleOCR engine initialized")
            except Exception as e:
                logger.warning(f"PaddleOCR initialization failed: {e}")

        if not self.engines:
            logger.warning("No OCR engines available!")

    def extract_text(self, image: Union[np.ndarray, Image.Image, str],
                    engine: str = 'auto',
                    lang: str = 'eng') -> Dict[str, Any]:
        """
        Extract text from image using specified or auto-selected engine

        Args:
            image: Image as numpy array, PIL Image, or file path
            engine: 'tesseract', 'paddle', or 'auto'
            lang: Language code for OCR

        Returns:
            {
                'text': extracted text,
                'confidence': confidence score,
                'engine': engine used,
                'bboxes': text bounding boxes,
                'processing_time': time taken
            }
        """
        start_time = time.time()

        # Convert image to numpy array
        if isinstance(image, str):
            # Load from file
            image = cv2.imread(image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif isinstance(image, Image.Image):
            image = np.array(image)

        if engine == 'auto':
            engine = self._select_best_engine(image)

        result = {
            'text': '',
            'confidence': 0.0,
            'engine': engine,
            'bboxes': [],
            'processing_time': 0.0,
            'success': False
        }

        try:
            if engine == 'tesseract' and self.engines.get('tesseract'):
                text_result = self._extract_tesseract(image, lang)
                result.update(text_result)
                self.stats['tesseract_used'] += 1

            elif engine == 'paddle' and self.engines.get('paddle'):
                text_result = self._extract_paddle(image)
                result.update(text_result)
                self.stats['paddle_used'] += 1

            else:
                result['error'] = f"Engine {engine} not available"

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"OCR extraction failed: {e}")

        result['processing_time'] = time.time() - start_time
        result['success'] = bool(result['text'].strip())
        self.stats['total_processed'] += 1

        return result

    def _extract_tesseract(self, image: np.ndarray, lang: str) -> Dict[str, Any]:
        """Extract text using Tesseract"""
        # Convert to PIL Image for tesseract
        pil_image = Image.fromarray(image)

        # Get text and confidence data
        data = pytesseract.image_to_data(pil_image, lang=lang, output_type=pytesseract.Output.DICT)

        # Extract text and filter by confidence
        text_parts = []
        bboxes = []
        confidences = []

        for i, confidence in enumerate(data['conf']):
            if int(confidence) > 30:  # Filter low confidence
                text = data['text'][i].strip()
                if text:
                    text_parts.append(text)
                    bboxes.append({
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })
                    confidences.append(int(confidence))

        final_text = ' '.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {
            'text': final_text,
            'confidence': avg_confidence / 100.0,  # Convert to 0-1 scale
            'bboxes': bboxes
        }

    def _extract_paddle(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text using PaddleOCR"""
        # PaddleOCR expects BGR format
        if len(image.shape) == 3 and image.shape[2] == 3:
            bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        else:
            bgr_image = image

        results = self.paddle_ocr.ocr(bgr_image, cls=True)

        text_parts = []
        bboxes = []
        confidences = []

        if results and results[0]:
            for line in results[0]:
                if len(line) >= 2:
                    bbox, (text, confidence) = line
                    if confidence > 0.3:  # Filter low confidence
                        text_parts.append(text)
                        bboxes.append({
                            'x': int(bbox[0][0]),
                            'y': int(bbox[0][1]),
                            'width': int(bbox[2][0] - bbox[0][0]),
                            'height': int(bbox[2][1] - bbox[0][1])
                        })
                        confidences.append(confidence)

        final_text = ' '.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {
            'text': final_text,
            'confidence': avg_confidence,
            'bboxes': bboxes
        }

    def _select_best_engine(self, image: np.ndarray) -> str:
        """Select best OCR engine based on image characteristics"""
        height, width = image.shape[:2]

        # For high resolution images, prefer PaddleOCR
        if width > 2000 or height > 2000:
            if self.engines.get('paddle'):
                return 'paddle'

        # For text-heavy images, prefer Tesseract
        # Simple heuristic: prefer Paddle for general use
        if self.engines.get('paddle'):
            return 'paddle'
        elif self.engines.get('tesseract'):
            return 'tesseract'

        return 'tesseract'  # fallback

    def get_stats(self) -> Dict[str, Any]:
        """Get OCR processing statistics"""
        return self.stats.copy()

class ImageAnalyzer:
    """
    Advanced image analysis and object detection
    """

    def __init__(self):
        self.object_detector = None
        self.stats = {
            'images_processed': 0,
            'objects_detected': 0,
            'faces_detected': 0,
            'text_regions': 0
        }

        # Initialize object detection model
        if PYTORCH_AVAILABLE:
            try:
                self.object_detector = fasterrcnn_resnet50_fpn(pretrained=True)
                self.object_detector.eval()
                logger.info("Object detection model initialized")
            except Exception as e:
                logger.warning(f"Object detection model failed: {e}")

    def analyze_image(self, image: Union[np.ndarray, Image.Image, str]) -> Dict[str, Any]:
        """
        Comprehensive image analysis

        Returns:
            {
                'dimensions': (width, height),
                'color_analysis': {...},
                'text_regions': [...],
                'objects': [...],
                'quality_score': float,
                'estimated_content': str
            }
        """
        start_time = time.time()

        # Convert to numpy array
        if isinstance(image, str):
            image = cv2.imread(image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif isinstance(image, Image.Image):
            image = np.array(image)

        result = {
            'dimensions': (image.shape[1], image.shape[0]),  # width, height
            'color_analysis': self._analyze_colors(image),
            'quality_score': self._assess_quality(image),
            'processing_time': 0.0
        }

        # Text detection and OCR
        ocr_result = self._detect_and_extract_text(image)
        result.update(ocr_result)

        # Object detection
        if self.object_detector:
            objects = self._detect_objects(image)
            result['objects'] = objects
            self.stats['objects_detected'] += len(objects)

        # Content estimation
        result['estimated_content'] = self._estimate_content(result)

        result['processing_time'] = time.time() - start_time
        self.stats['images_processed'] += 1

        return result

    def _analyze_colors(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color distribution and dominant colors"""
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

        # Calculate histograms
        hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
        hist_v = cv2.calcHist([hsv], [2], None, [256], [0, 256])

        # Find dominant colors (simplified)
        dominant_hue = np.argmax(hist_h)
        saturation_score = np.mean(hist_s) / 255.0
        brightness_score = np.mean(hist_v) / 255.0

        return {
            'dominant_hue': int(dominant_hue),
            'saturation_score': float(saturation_score),
            'brightness_score': float(brightness_score),
            'is_grayscale': saturation_score < 0.1,
            'is_dark': brightness_score < 0.3,
            'is_bright': brightness_score > 0.7
        }

    def _assess_quality(self, image: np.ndarray) -> float:
        """Assess image quality score (0-1)"""
        # Blur detection using Laplacian variance
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Normalize to 0-1 scale (rough heuristic)
        quality_score = min(1.0, laplacian_var / 500.0)

        return float(quality_score)

    def _detect_and_extract_text(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect text regions and extract content"""
        # Use OCR processor
        ocr_processor = OCRProcessor()
        ocr_result = ocr_processor.extract_text(image)

        return {
            'text_content': ocr_result.get('text', ''),
            'text_confidence': ocr_result.get('confidence', 0.0),
            'text_regions': ocr_result.get('bboxes', []),
            'text_engine': ocr_result.get('engine', 'none')
        }

    def _detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect objects in image using PyTorch model"""
        if not self.object_detector or not PYTORCH_AVAILABLE:
            return []

        try:
            # Prepare image for PyTorch
            transform = torchvision.transforms.Compose([
                torchvision.transforms.ToTensor(),
            ])

            pil_image = Image.fromarray(image)
            tensor_image = transform(pil_image).unsqueeze(0)

            # Run detection
            with torch.no_grad():
                predictions = self.object_detector(tensor_image)

            # Process results
            objects = []
            boxes = predictions[0]['boxes'].cpu().numpy()
            labels = predictions[0]['labels'].cpu().numpy()
            scores = predictions[0]['scores'].cpu().numpy()

            # COCO classes (simplified)
            coco_classes = [
                '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
                'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
                'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
                'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag',
                'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite',
                'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
                'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana',
                'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
                'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table',
                'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
                'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock',
                'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
            ]

            # Filter by confidence threshold
            threshold = 0.5
            high_conf_indices = scores > threshold

            for i in range(len(high_conf_indices)):
                if high_conf_indices[i]:
                    box = boxes[i]
                    label_idx = labels[i]
                    score = scores[i]

                    objects.append({
                        'label': coco_classes[label_idx] if label_idx < len(coco_classes) else f'class_{label_idx}',
                        'confidence': float(score),
                        'bbox': {
                            'x': int(box[0]),
                            'y': int(box[1]),
                            'width': int(box[2] - box[0]),
                            'height': int(box[3] - box[1])
                        }
                    })

            return objects

        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return []

    def _estimate_content(self, analysis: Dict[str, Any]) -> str:
        """Estimate image content type based on analysis"""
        content_hints = []

        # Text-based content
        if analysis.get('text_content'):
            content_hints.append("document/text")

        # Object-based content
        objects = analysis.get('objects', [])
        if objects:
            object_labels = [obj['label'] for obj in objects if obj['confidence'] > 0.7]
            if 'person' in object_labels:
                content_hints.append("people")
            if any(label in ['car', 'truck', 'bus'] for label in object_labels):
                content_hints.append("vehicles")
            if any(label in ['laptop', 'keyboard', 'monitor'] for label in object_labels):
                content_hints.append("computer")

        # Color-based content
        color_analysis = analysis.get('color_analysis', {})
        if color_analysis.get('is_grayscale'):
            content_hints.append("grayscale")
        if color_analysis.get('is_dark'):
            content_hints.append("dark/night")

        # Size-based content
        width, height = analysis.get('dimensions', (0, 0))
        if width > 2000 or height > 2000:
            content_hints.append("high_resolution")
        elif width < 500 or height < 500:
            content_hints.append("thumbnail")

        # Quality-based content
        quality = analysis.get('quality_score', 0)
        if quality < 0.3:
            content_hints.append("blurry")
        elif quality > 0.8:
            content_hints.append("sharp")

        if not content_hints:
            return "unknown"

        return ", ".join(content_hints)

class ScreenshotAnalyzer:
    """
    Specialized analyzer for browser screenshots
    """

    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.image_analyzer = ImageAnalyzer()

    def analyze_screenshot(self, screenshot_data: Union[str, bytes, np.ndarray]) -> Dict[str, Any]:
        """
        Analyze browser screenshot for UI elements, text content, and actionable items

        Args:
            screenshot_data: Base64 string, bytes, or numpy array

        Returns:
            Comprehensive analysis of screenshot content
        """
        # Convert screenshot data to image
        if isinstance(screenshot_data, str):
            # Base64 string
            if screenshot_data.startswith('data:image'):
                screenshot_data = screenshot_data.split(',')[1]
            image_data = base64.b64decode(screenshot_data)
            image = Image.open(io.BytesIO(image_data))
            image = np.array(image)
        elif isinstance(screenshot_data, bytes):
            image = Image.open(io.BytesIO(screenshot_data))
            image = np.array(image)
        else:
            image = screenshot_data

        # Basic image analysis
        analysis = self.image_analyzer.analyze_image(image)

        # UI-specific analysis
        ui_analysis = self._analyze_ui_elements(image)

        # Actionable elements detection
        actionable_elements = self._detect_actionable_elements(image, ui_analysis)

        # Content classification
        content_type = self._classify_screenshot_content(image, analysis, ui_analysis)

        result = {
            **analysis,
            'ui_elements': ui_analysis,
            'actionable_elements': actionable_elements,
            'content_type': content_type,
            'screenshot_analysis': True
        }

        return result

    def _analyze_ui_elements(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze UI elements in screenshot"""
        ui_elements = {
            'buttons': [],
            'inputs': [],
            'links': [],
            'navigation': False,
            'forms': [],
            'modals': []
        }

        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Edge detection to find potential UI elements
        edges = cv2.Canny(gray, 100, 200)

        # Find contours (potential UI elements)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Analyze contours for UI patterns
        height, width = image.shape[:2]

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 100:  # Too small
                continue

            x, y, w, h = cv2.boundingRect(contour)

            # Aspect ratio analysis for different UI elements
            aspect_ratio = w / h if h > 0 else 0

            # Button-like elements (roughly square, reasonable size)
            if 0.5 < aspect_ratio < 2.0 and 30 < w < 300 and 20 < h < 100:
                # Check if it looks like a button (color analysis)
                roi = image[y:y+h, x:x+w]
                if self._looks_like_button(roi):
                    ui_elements['buttons'].append({
                        'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                        'confidence': 0.8
                    })

            # Input-like elements (wide, thin rectangles)
            elif aspect_ratio > 3 and h < 50:
                ui_elements['inputs'].append({
                    'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                    'confidence': 0.7
                })

        # Detect navigation bars (usually at top)
        top_region = image[:int(height * 0.15), :]  # Top 15%
        if self._has_navigation_pattern(top_region):
            ui_elements['navigation'] = True

        return ui_elements

    def _looks_like_button(self, roi: np.ndarray) -> bool:
        """Check if ROI looks like a button"""
        # Simple heuristics: check for contrasting border and solid background
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)

            # Check saturation (buttons often have distinct colors)
            saturation = np.mean(hsv[:, :, 1])
            brightness = np.mean(hsv[:, :, 2])

            # Buttons typically have moderate saturation and brightness
            return 30 < saturation < 200 and 100 < brightness < 220

        except:
            return False

    def _has_navigation_pattern(self, region: np.ndarray) -> bool:
        """Check if region looks like a navigation bar"""
        try:
            # Look for horizontal lines or text patterns
            gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)

            # Edge detection
            edges = cv2.Canny(gray, 50, 150)

            # Count horizontal edges (typical in navigation)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50,
                                  minLineLength=50, maxLineGap=10)

            if lines is not None:
                horizontal_lines = [line for line in lines[0]
                                  if abs(line[1] - line[3]) < 5]  # Nearly horizontal
                return len(horizontal_lines) > 2

            return False

        except:
            return False

    def _detect_actionable_elements(self, image: np.ndarray, ui_analysis: Dict) -> List[Dict]:
        """Detect clickable/actionable elements"""
        actionable = []

        # Add detected buttons
        for button in ui_analysis.get('buttons', []):
            actionable.append({
                'type': 'button',
                'bbox': button['bbox'],
                'confidence': button['confidence'],
                'action': 'click'
            })

        # Add detected inputs
        for input_elem in ui_analysis.get('inputs', []):
            actionable.append({
                'type': 'input',
                'bbox': input_elem['bbox'],
                'confidence': input_elem['confidence'],
                'action': 'type'
            })

        # Look for common clickable patterns
        height, width = image.shape[:2]

        # Search buttons (magnifying glass icons, etc.)
        search_patterns = self._find_search_patterns(image)
        actionable.extend(search_patterns)

        # Login forms
        login_patterns = self._find_login_patterns(image)
        actionable.extend(login_patterns)

        return actionable

    def _find_search_patterns(self, image: np.ndarray) -> List[Dict]:
        """Find search-related elements"""
        # This is a simplified implementation
        # In a real system, this would use template matching or ML
        return []  # Placeholder

    def _find_login_patterns(self, image: np.ndarray) -> List[Dict]:
        """Find login form elements"""
        # This is a simplified implementation
        return []  # Placeholder

    def _classify_screenshot_content(self, image: np.ndarray, analysis: Dict, ui_analysis: Dict) -> str:
        """Classify the type of screenshot content"""
        classifications = []

        # Check for web page indicators
        if ui_analysis.get('navigation'):
            classifications.append("webpage")

        # Check for form elements
        if ui_analysis.get('inputs') or ui_analysis.get('buttons'):
            classifications.append("interactive")

        # Check text content
        text_content = analysis.get('text_content', '')
        if len(text_content) > 100:
            classifications.append("text-heavy")
        elif len(text_content) > 20:
            classifications.append("text-content")

        # Check for specific UI patterns
        if any(btn.get('confidence', 0) > 0.8 for btn in ui_analysis.get('buttons', [])):
            classifications.append("application")

        # Object-based classification
        objects = analysis.get('objects', [])
        if any(obj['label'] in ['person', 'face'] for obj in objects):
            classifications.append("people")
        elif any(obj['label'] in ['car', 'truck'] for obj in objects):
            classifications.append("vehicles")

        if not classifications:
            return "unknown"

        return ", ".join(classifications)

class ComputerVisionManager:
    """
    Main manager for all computer vision capabilities
    """

    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.image_analyzer = ImageAnalyzer()
        self.screenshot_analyzer = ScreenshotAnalyzer()

        self.stats = {
            'total_images_processed': 0,
            'ocr_requests': 0,
            'screenshot_analyses': 0,
            'object_detections': 0
        }

    def process_image(self, image_data: Union[str, bytes, np.ndarray],
                     analysis_type: str = 'full') -> Dict[str, Any]:
        """
        Process image with specified analysis type

        Args:
            image_data: Image data (file path, base64, bytes, or numpy array)
            analysis_type: 'ocr', 'objects', 'full', 'screenshot'

        Returns:
            Analysis results based on type
        """
        result = {
            'success': False,
            'analysis_type': analysis_type,
            'processing_time': 0.0
        }

        start_time = time.time()

        try:
            if analysis_type == 'ocr':
                ocr_result = self.ocr_processor.extract_text(image_data)
                result.update(ocr_result)
                self.stats['ocr_requests'] += 1

            elif analysis_type == 'objects':
                analysis = self.image_analyzer.analyze_image(image_data)
                result.update(analysis)
                self.stats['object_detections'] += len(analysis.get('objects', []))

            elif analysis_type == 'screenshot':
                screenshot_result = self.screenshot_analyzer.analyze_screenshot(image_data)
                result.update(screenshot_result)
                self.stats['screenshot_analyses'] += 1

            elif analysis_type == 'full':
                # Complete analysis
                analysis = self.image_analyzer.analyze_image(image_data)
                ocr_result = self.ocr_processor.extract_text(image_data)

                result.update(analysis)
                result['ocr'] = ocr_result

                self.stats['ocr_requests'] += 1
                self.stats['object_detections'] += len(analysis.get('objects', []))

            result['success'] = True

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Image processing failed: {e}")

        result['processing_time'] = time.time() - start_time
        self.stats['total_images_processed'] += 1

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get computer vision statistics"""
        return {
            **self.stats,
            'ocr_stats': self.ocr_processor.get_stats(),
            'engines_available': list(self.ocr_processor.engines.keys())
        }

# Global instance
_cv_manager = None

def get_cv_manager() -> ComputerVisionManager:
    """Get global computer vision manager instance"""
    global _cv_manager
    if _cv_manager is None:
        _cv_manager = ComputerVisionManager()
    return _cv_manager

# Convenience functions
def extract_text_from_image(image) -> Dict[str, Any]:
    """Extract text from image using best available OCR"""
    manager = get_cv_manager()
    return manager.process_image(image, 'ocr')

def analyze_image_content(image) -> Dict[str, Any]:
    """Complete image analysis"""
    manager = get_cv_manager()
    return manager.process_image(image, 'full')

def analyze_screenshot(screenshot) -> Dict[str, Any]:
    """Analyze browser screenshot for actionable elements"""
    manager = get_cv_manager()
    return manager.process_image(screenshot, 'screenshot')

if __name__ == "__main__":
    print("[COMPUTER VISION] Sharingan Computer Vision System")
    print("=" * 60)

    # Test basic functionality
    manager = get_cv_manager()

    print("Available OCR engines:", list(manager.ocr_processor.engines.keys()))
    print("PyTorch available:", PYTORCH_AVAILABLE)
    print("Tesseract available:", TESSERACT_AVAILABLE)
    print("PaddleOCR available:", PADDLE_OCR_AVAILABLE)

    print("\nComputer vision system ready!")
    print("Available functions:")
    print("- extract_text_from_image(image)")
    print("- analyze_image_content(image)")
    print("- analyze_screenshot(screenshot)")