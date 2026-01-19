# -*- coding: utf-8 -*-
"""
Audio Processing System for Sharingan OS
Speech recognition, synthesis, forensic analysis, keyword detection
"""

import os
import io
import wave
import audioop
import struct
import numpy as np
import base64
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import logging
import time

# Optional imports with fallbacks
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import librosa
    import librosa.display
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

logger = logging.getLogger("audio_processing")

class SpeechRecognizer:
    """
    Advanced speech-to-text using Whisper
    """

    def __init__(self):
        self.models = {}
        self.stats = {
            'total_processed': 0,
            'total_duration': 0.0,
            'languages_detected': set(),
            'avg_confidence': 0.0
        }

        # Initialize available models
        if WHISPER_AVAILABLE:
            try:
                # Load base model for speed (can be upgraded to large)
                self.models['base'] = whisper.load_model("base")
                logger.info("Whisper base model loaded")
            except Exception as e:
                logger.warning(f"Whisper model loading failed: {e}")

    def transcribe_audio(self, audio_data: Union[str, bytes, np.ndarray],
                        language: Optional[str] = None,
                        model_size: str = "base") -> Dict[str, Any]:
        """
        Transcribe audio to text

        Args:
            audio_data: Audio as base64 string, bytes, or numpy array
            language: Language code (auto-detected if None)
            model_size: Model size ('tiny', 'base', 'small', 'medium', 'large')

        Returns:
            {
                'text': transcribed text,
                'language': detected language,
                'confidence': confidence score,
                'duration': audio duration,
                'segments': detailed segments,
                'processing_time': time taken
            }
        """
        start_time = time.time()

        if not WHISPER_AVAILABLE or model_size not in self.models:
            return {
                'text': '',
                'error': f'Whisper {model_size} model not available',
                'processing_time': time.time() - start_time
            }

        try:
            # Convert audio data to numpy array
            audio_array = self._prepare_audio_data(audio_data)

            # Load appropriate model if not already loaded
            if model_size not in self.models:
                self.models[model_size] = whisper.load_model(model_size)

            model = self.models[model_size]

            # Transcribe with options
            options = {
                'language': language,
                'task': 'transcribe',
                'fp16': False,  # Use FP32 for compatibility
                'verbose': False
            }

            result = model.transcribe(audio_array, **options)

            # Calculate confidence (average probability)
            confidence = np.mean([seg.get('avg_logprob', 0) for seg in result.get('segments', [])])
            confidence = max(0, min(1, confidence + 1))  # Normalize to 0-1

            # Update stats
            self.stats['total_processed'] += 1
            self.stats['total_duration'] += result.get('duration', 0)
            if result.get('language'):
                self.stats['languages_detected'].add(result['language'])

            response = {
                'text': result.get('text', '').strip(),
                'language': result.get('language'),
                'confidence': float(confidence),
                'duration': result.get('duration', 0),
                'segments': result.get('segments', []),
                'processing_time': time.time() - start_time
            }

            logger.info(f"Audio transcribed: {len(response['text'])} chars, {response['language']}, confidence: {confidence:.2f}")
            return response

        except Exception as e:
            logger.error(f"Speech recognition failed: {e}")
            return {
                'text': '',
                'error': str(e),
                'processing_time': time.time() - start_time
            }

    def _prepare_audio_data(self, audio_data: Union[str, bytes, np.ndarray]) -> np.ndarray:
        """Convert various audio formats to numpy array"""
        if isinstance(audio_data, str):
            # Base64 encoded audio
            if audio_data.startswith('data:audio'):
                audio_data = audio_data.split(',')[1]
            audio_bytes = base64.b64decode(audio_data)

            # Try to decode as WAV
            try:
                with io.BytesIO(audio_bytes) as buffer:
                    with wave.open(buffer, 'rb') as wav_file:
                        audio_array = np.frombuffer(wav_file.readframes(wav_file.getnframes()), dtype=np.int16)
                        audio_array = audio_array.astype(np.float32) / 32768.0  # Normalize to [-1, 1]
                        return audio_array
            except:
                # Fallback: assume raw PCM
                audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                audio_array = audio_array.astype(np.float32) / 32768.0
                return audio_array

        elif isinstance(audio_data, bytes):
            # Raw bytes - assume WAV or PCM
            try:
                with io.BytesIO(audio_data) as buffer:
                    with wave.open(buffer, 'rb') as wav_file:
                        audio_array = np.frombuffer(wav_file.readframes(wav_file.getnframes()), dtype=np.int16)
                        audio_array = audio_array.astype(np.float32) / 32768.0
                        return audio_array
            except:
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                audio_array = audio_array.astype(np.float32) / 32768.0
                return audio_array

        elif isinstance(audio_data, np.ndarray):
            # Already numpy array
            if audio_data.dtype != np.float32:
                audio_array = audio_data.astype(np.float32)
                if audio_array.max() > 1.0:
                    audio_array /= 32768.0  # Assume int16 range
            return audio_data

        raise ValueError("Unsupported audio data format")

class SpeechSynthesizer:
    """
    Text-to-speech using Coqui TTS
    """

    def __init__(self):
        self.tts = None
        self.available_models = []
        self.stats = {
            'total_synthesized': 0,
            'total_chars': 0,
            'avg_processing_time': 0.0,
            'voices_used': set()
        }

        if TTS_AVAILABLE:
            try:
                # Initialize TTS with multi-speaker model
                self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
                self.available_models = TTS.list_models()
                logger.info("TTS initialized with XTTS v2 model")
            except Exception as e:
                logger.warning(f"TTS initialization failed: {e}")

    def synthesize_speech(self, text: str,
                         language: str = "en",
                         speaker: str = "default",
                         speed: float = 1.0) -> Dict[str, Any]:
        """
        Convert text to speech

        Args:
            text: Text to synthesize
            language: Language code
            speaker: Speaker voice
            speed: Speech speed (0.5-2.0)

        Returns:
            {
                'audio_data': base64 encoded audio,
                'duration': estimated duration,
                'format': audio format info,
                'processing_time': time taken
            }
        """
        start_time = time.time()

        if not TTS_AVAILABLE or not self.tts:
            return {
                'error': 'Text-to-speech not available',
                'processing_time': time.time() - start_time
            }

        try:
            # Generate speech
            wav = self.tts.tts(text=text, speaker=speaker, language=language)

            # Convert to bytes
            if SOUNDFILE_AVAILABLE:
                import soundfile as sf
                buffer = io.BytesIO()
                sf.write(buffer, wav, 22050, format='WAV')
                audio_bytes = buffer.getvalue()
            else:
                # Fallback: simple WAV encoding
                audio_bytes = self._encode_wav(wav)

            # Encode to base64
            audio_b64 = base64.b64encode(audio_bytes).decode()

            # Calculate duration
            duration = len(wav) / 22050  # Sample rate

            # Update stats
            self.stats['total_synthesized'] += 1
            self.stats['total_chars'] += len(text)
            self.stats['voices_used'].add(speaker)

            response = {
                'audio_data': f"data:audio/wav;base64,{audio_b64}",
                'duration': duration,
                'format': {
                    'sample_rate': 22050,
                    'channels': 1,
                    'encoding': 'wav'
                },
                'text_length': len(text),
                'processing_time': time.time() - start_time
            }

            logger.info(f"Speech synthesized: {len(text)} chars, {duration:.1f}s, speaker: {speaker}")
            return response

        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return {
                'error': str(e),
                'processing_time': time.time() - start_time
            }

    def _encode_wav(self, audio_array: np.ndarray) -> bytes:
        """Simple WAV encoding fallback"""
        # Convert to 16-bit PCM
        audio_int16 = (audio_array * 32767).astype(np.int16)

        # WAV header
        sample_rate = 22050
        num_channels = 1
        bytes_per_sample = 2
        data_size = len(audio_int16) * bytes_per_sample

        header = struct.pack('<4sI4s4sIHHIIHH4sI',
                            b'RIFF',
                            36 + data_size,
                            b'WAVE',
                            b'fmt ',
                            16,
                            1,  # PCM
                            num_channels,
                            sample_rate,
                            sample_rate * num_channels * bytes_per_sample,
                            num_channels * bytes_per_sample,
                            bytes_per_sample * 8,
                            b'data',
                            data_size)

        return header + audio_int16.tobytes()

class AudioAnalyzer:
    """
    Forensic audio analysis using Librosa
    """

    def __init__(self):
        self.stats = {
            'total_analyzed': 0,
            'anomalies_detected': 0,
            'keywords_found': 0,
            'duration_processed': 0.0
        }

    def analyze_audio(self, audio_data: Union[str, bytes, np.ndarray],
                     analysis_type: str = "full") -> Dict[str, Any]:
        """
        Comprehensive audio analysis

        Args:
            analysis_type: 'basic', 'forensic', 'keywords', 'full'

        Returns:
            Analysis results based on type
        """
        start_time = time.time()

        if not LIBROSA_AVAILABLE:
            return {
                'error': 'Audio analysis not available',
                'processing_time': time.time() - start_time
            }

        try:
            # Load audio
            y, sr = self._load_audio(audio_data)

            result = {
                'duration': len(y) / sr,
                'sample_rate': sr,
                'channels': 1 if len(y.shape) == 1 else y.shape[0],
                'processing_time': 0.0
            }

            if analysis_type in ['basic', 'full']:
                result.update(self._basic_analysis(y, sr))

            if analysis_type in ['forensic', 'full']:
                result.update(self._forensic_analysis(y, sr))

            if analysis_type in ['keywords', 'full']:
                result.update(self._keyword_detection(y, sr))

            # Update stats
            self.stats['total_analyzed'] += 1
            self.stats['duration_processed'] += result['duration']

            result['processing_time'] = time.time() - start_time
            return result

        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {
                'error': str(e),
                'processing_time': time.time() - start_time
            }

    def _load_audio(self, audio_data: Union[str, bytes, np.ndarray]) -> Tuple[np.ndarray, int]:
        """Load audio data into librosa format"""
        if isinstance(audio_data, str):
            # Base64 encoded audio
            if audio_data.startswith('data:audio'):
                audio_data = audio_data.split(',')[1]
            audio_bytes = base64.b64decode(audio_data)

            # Try to load with soundfile first
            if SOUNDFILE_AVAILABLE:
                with io.BytesIO(audio_bytes) as buffer:
                    y, sr = sf.read(buffer)
                    if len(y.shape) > 1:
                        y = y.mean(axis=1)  # Convert to mono
                    return y, sr
            else:
                # Fallback: assume raw PCM 16-bit
                y = np.frombuffer(audio_bytes, dtype=np.int16)
                y = y.astype(np.float32) / 32768.0
                return y, 22050  # Assume 22kHz

        elif isinstance(audio_data, bytes):
            # Same as string handling
            return self._load_audio(audio_data.decode('latin-1'))

        elif isinstance(audio_data, np.ndarray):
            return audio_data, 22050  # Assume 22kHz

        raise ValueError("Unsupported audio format")

    def _basic_analysis(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Basic audio analysis"""
        # RMS energy
        rms = librosa.feature.rms(y=y)[0]
        avg_energy = np.mean(rms)

        # Spectral centroid
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        avg_centroid = np.mean(centroid)

        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        avg_zcr = np.mean(zcr)

        # Tempo estimation
        tempo, _ = librosa.beat.tempo(y=y, sr=sr)

        # Pitch estimation
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        avg_pitch = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0

        return {
            'avg_energy': float(avg_energy),
            'avg_centroid': float(avg_centroid),
            'avg_zcr': float(avg_zcr),
            'tempo': float(tempo),
            'avg_pitch': float(avg_pitch),
            'is_speech': self._detect_speech(y, sr),
            'quality_score': self._assess_quality(y, sr)
        }

    def _forensic_analysis(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Forensic audio analysis"""
        # Check for compression artifacts
        compression_artifacts = self._detect_compression(y)

        # Check for editing artifacts
        editing_artifacts = self._detect_editing(y, sr)

        # Audio fingerprinting (simplified)
        fingerprint = self._generate_fingerprint(y, sr)

        # Noise analysis
        noise_level = self._analyze_noise(y)

        # Echo detection
        echo_detected = self._detect_echo(y, sr)

        return {
            'compression_artifacts': compression_artifacts,
            'editing_artifacts': editing_artifacts,
            'fingerprint': fingerprint,
            'noise_level': noise_level,
            'echo_detected': echo_detected,
            'estimated_authenticity': self._estimate_authenticity(
                compression_artifacts, editing_artifacts, echo_detected
            )
        }

    def _keyword_detection(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Keyword detection in audio - Placeholder for future ML implementation"""
        # NOTE: Real implementation would require speech-to-text + keyword spotting ML models
        # For now, return empty results instead of fake detections

        keywords = {
            'help': ['help', 'aide', 'assist'],
            'security': ['security', 'sécurité', 'safe', 'protégé'],
            'alert': ['alert', 'alerte', 'warning', 'attention'],
            'access': ['access', 'accès', 'login', 'connexion'],
            'error': ['error', 'erreur', 'fail', 'échec']
        }

        # Return empty results - no fake keyword detection
        return {
            'detected_keywords': [],
            'total_keywords': 0,
            'keyword_categories': list(keywords.keys()),
            'note': 'Keyword detection requires ML models (speech-to-text + keyword spotting)'
        }

    def _detect_speech(self, y: np.ndarray, sr: int) -> bool:
        """Simple speech detection"""
        # Calculate voice activity detection features
        rms = librosa.feature.rms(y=y)[0]
        avg_rms = np.mean(rms)

        # Speech typically has moderate energy and pitch
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_confidence = np.mean(magnitudes[magnitudes > 0])

        return avg_rms > 0.01 and pitch_confidence > 0.1

    def _assess_quality(self, y: np.ndarray, sr: int) -> float:
        """Assess audio quality (0-1)"""
        # Signal-to-noise ratio approximation
        signal_power = np.mean(y ** 2)
        noise_power = np.var(y) * 0.1  # Estimate noise
        snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 0

        # Normalize to 0-1
        quality = min(1.0, max(0.0, (snr + 20) / 40))  # Assume -20dB to +20dB range

        return float(quality)

    def _detect_compression(self, y: np.ndarray) -> List[str]:
        """Detect compression artifacts"""
        artifacts = []

        # Check for MP3-like artifacts (simplified)
        # Real implementation would analyze frequency domain
        if len(y) > 1000:
            # Check for quantization noise patterns
            diff = np.abs(np.diff(y))
            if np.mean(diff) > np.std(diff) * 2:
                artifacts.append("quantization_noise")

        return artifacts

    def _detect_editing(self, y: np.ndarray, sr: int) -> List[str]:
        """Detect audio editing artifacts"""
        artifacts = []

        # Check for abrupt changes (cuts)
        diff = np.abs(np.diff(y))
        threshold = np.std(y) * 3
        cuts = np.sum(diff > threshold)

        if cuts > len(y) * 0.001:  # More than 0.1% cuts
            artifacts.append("abrupt_cuts")

        # Check for silence gaps (potential edits)
        rms = librosa.feature.rms(y=y)[0]
        silence_frames = np.sum(rms < 0.001)

        if silence_frames > len(rms) * 0.05:  # More than 5% silence
            artifacts.append("unusual_silence")

        return artifacts

    def _generate_fingerprint(self, y: np.ndarray, sr: int) -> str:
        """Generate audio fingerprint (simplified)"""
        # Real fingerprinting would use algorithms like Echoprint
        # This is just a hash of spectral features
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        fingerprint = hashlib.sha256(str(centroid).encode()).hexdigest()[:16]
        return fingerprint

    def _analyze_noise(self, y: np.ndarray) -> float:
        """Analyze noise level"""
        # Estimate noise floor
        noise_level = np.std(y) * 0.1  # Rough estimate
        return float(noise_level)

    def _detect_echo(self, y: np.ndarray, sr: int) -> bool:
        """Detect echo/reverb effects"""
        # Simplified echo detection
        # Real implementation would use autocorrelation
        autocorr = np.correlate(y, y, mode='full')
        max_corr = np.max(np.abs(autocorr[len(autocorr)//2 + 1:]))

        # If strong correlation at delays, likely echo
        return max_corr > np.std(y) * len(y) * 0.1

    def _estimate_authenticity(self, compression: List[str],
                              editing: List[str], echo: bool) -> float:
        """Estimate audio authenticity (0-1)"""
        # Start with high authenticity
        score = 1.0

        # Penalize for each artifact
        score -= len(compression) * 0.1
        score -= len(editing) * 0.15
        if echo:
            score -= 0.2

        return max(0.0, min(1.0, score))

class AudioProcessingManager:
    """
    Main manager for all audio processing capabilities
    """

    def __init__(self):
        self.speech_recognizer = SpeechRecognizer()
        self.speech_synthesizer = SpeechSynthesizer()
        self.audio_analyzer = AudioAnalyzer()

        self.stats = {
            'total_requests': 0,
            'speech_recognized': 0,
            'speech_synthesized': 0,
            'audio_analyzed': 0
        }

    def process_audio(self, audio_data: Union[str, bytes, np.ndarray],
                     operation: str = 'recognize',
                     **kwargs) -> Dict[str, Any]:
        """
        Main audio processing interface

        Args:
            audio_data: Audio data in various formats
            operation: 'recognize', 'synthesize', 'analyze'
            **kwargs: Operation-specific parameters

        Returns:
            Processing results
        """
        self.stats['total_requests'] += 1
        result = {'operation': operation, 'success': False}

        try:
            if operation == 'recognize':
                result.update(self.speech_recognizer.transcribe_audio(audio_data, **kwargs))
                if 'text' in result and result['text']:
                    self.stats['speech_recognized'] += 1

            elif operation == 'synthesize':
                text = kwargs.get('text', '')
                if text:
                    result.update(self.speech_synthesizer.synthesize_speech(text, **kwargs))
                    if 'audio_data' in result:
                        self.stats['speech_synthesized'] += 1

            elif operation == 'analyze':
                result.update(self.audio_analyzer.analyze_audio(audio_data, **kwargs))
                if 'duration' in result:
                    self.stats['audio_analyzed'] += 1

            result['success'] = True

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Audio processing failed: {e}")

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get audio processing statistics"""
        return {
            **self.stats,
            'speech_recognizer_stats': self.speech_recognizer.stats,
            'speech_synthesizer_stats': self.speech_synthesizer.stats,
            'audio_analyzer_stats': self.audio_analyzer.stats,
            'available_engines': {
                'whisper': WHISPER_AVAILABLE,
                'tts': TTS_AVAILABLE,
                'librosa': LIBROSA_AVAILABLE,
                'soundfile': SOUNDFILE_AVAILABLE
            }
        }

# Global instance
_audio_manager = None

def get_audio_manager() -> AudioProcessingManager:
    """Get global audio processing manager instance"""
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioProcessingManager()
    return _audio_manager

# Convenience functions
def recognize_speech(audio_data, **kwargs) -> Dict[str, Any]:
    """Recognize speech in audio"""
    manager = get_audio_manager()
    return manager.process_audio(audio_data, 'recognize', **kwargs)

def synthesize_speech(text: str, **kwargs) -> Dict[str, Any]:
    """Synthesize speech from text"""
    manager = get_audio_manager()
    return manager.process_audio(None, 'synthesize', text=text, **kwargs)

def analyze_audio(audio_data, **kwargs) -> Dict[str, Any]:
    """Analyze audio content"""
    manager = get_audio_manager()
    return manager.process_audio(audio_data, 'analyze', **kwargs)

if __name__ == "__main__":
    print("[AUDIO PROCESSING] Sharingan Audio Processing System")
    print("=" * 60)

    # Test system
    manager = get_audio_manager()

    print("Available engines:")
    print(f"  Whisper (Speech Recognition): {WHISPER_AVAILABLE}")
    print(f"  Coqui TTS (Speech Synthesis): {TTS_AVAILABLE}")
    print(f"  Librosa (Audio Analysis): {LIBROSA_AVAILABLE}")
    print(f"  SoundFile (Audio I/O): {SOUNDFILE_AVAILABLE}")

    # Test synthesis (if available)
    if TTS_AVAILABLE:
        print("\nTesting speech synthesis...")
        result = synthesize_speech("Hello, this is Sharingan OS speaking.")
        if result.get('success'):
            print("✅ Speech synthesis successful")
        else:
            print(f"❌ Speech synthesis failed: {result.get('error')}")

    print("\nAudio processing system ready!")
    print("Available functions:")
    print("- recognize_speech(audio_data)")
    print("- synthesize_speech(text)")
    print("- analyze_audio(audio_data)")