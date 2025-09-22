"""
Google Cloud Speech and Text-to-Speech integration module
"""
import os
import io
import threading
import time
import logging
import wave
import numpy as np
from typing import Optional, Callable, Generator
from pathlib import Path

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("PyAudio not available. Audio recording will be disabled.")

try:
    from google.cloud import speech
    from google.cloud import texttospeech
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    print("Google Cloud libraries not available.")

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Whisper not available. Offline mode disabled.")

from config import Config, AudioConfig

logger = logging.getLogger(__name__)

class AudioRecorder:
    """Audio recording class using PyAudio"""
    
    def __init__(self):
        self.audio = None
        self.stream = None
        self.recording = False
        self.audio_data = []
        self.callback = None
        
        if PYAUDIO_AVAILABLE:
            self.audio = pyaudio.PyAudio()
            AudioConfig.get_audio_format()
    
    def start_recording(self, callback: Optional[Callable] = None):
        """Start recording audio"""
        if not PYAUDIO_AVAILABLE:
            raise RuntimeError("PyAudio not available")
        
        self.callback = callback
        self.recording = True
        self.audio_data = []
        
        try:
            self.stream = self.audio.open(
                format=AudioConfig.FORMAT,
                channels=AudioConfig.CHANNELS,
                rate=AudioConfig.RATE,
                input=True,
                frames_per_buffer=AudioConfig.CHUNK,
                stream_callback=self._audio_callback
            )
            self.stream.start_stream()
            logger.info("Recording started")
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.recording = False
            raise
    
    def stop_recording(self) -> bytes:
        """Stop recording and return audio data"""
        if not self.recording:
            return b''
        
        self.recording = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        # Convert to bytes
        audio_bytes = b''.join(self.audio_data)
        logger.info(f"Recording stopped. Audio data size: {len(audio_bytes)} bytes")
        return audio_bytes
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream"""
        if self.recording:
            self.audio_data.append(in_data)
            
            # Calculate audio level for visualization
            if self.callback:
                audio_level = self._calculate_audio_level(in_data)
                self.callback(audio_level)
        
        return (in_data, pyaudio.paContinue)
    
    def _calculate_audio_level(self, audio_data: bytes) -> float:
        """Calculate audio level (0.0 to 1.0)"""
        try:
            # Convert bytes to numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            # Calculate RMS
            rms = np.sqrt(np.mean(audio_np**2))
            # Normalize to 0-1 range
            return min(1.0, rms / 32767.0)
        except:
            return 0.0
    
    def save_audio(self, audio_data: bytes, filename: str):
        """Save audio data to WAV file"""
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(AudioConfig.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(AudioConfig.FORMAT))
                wf.setframerate(AudioConfig.RATE)
                wf.writeframes(audio_data)
            logger.info(f"Audio saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
    
    def cleanup(self):
        """Cleanup audio resources"""
        if self.stream:
            self.stream.close()
        if self.audio:
            self.audio.terminate()

class GoogleSpeechToText:
    """Google Cloud Speech-to-Text client"""
    
    def __init__(self):
        if not GOOGLE_CLOUD_AVAILABLE:
            raise RuntimeError("Google Cloud Speech library not available")
        
        try:
            self.client = speech.SpeechClient()
            self.config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=Config.AUDIO_SAMPLE_RATE,
                language_code=Config.SPEECH_LANGUAGE,
                enable_automatic_punctuation=True,
                enable_word_confidence=True,
                enable_word_time_offsets=True,
            )
            logger.info("Google Speech-to-Text client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Speech-to-Text client: {e}")
            raise
    
    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio data to text"""
        try:
            audio = speech.RecognitionAudio(content=audio_data)
            response = self.client.recognize(config=self.config, audio=audio)
            
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                confidence = response.results[0].alternatives[0].confidence
                logger.info(f"Transcription: '{transcript}' (confidence: {confidence:.2f})")
                return transcript
            else:
                logger.warning("No transcription results")
                return None
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
    
    def streaming_transcribe(self, audio_generator: Generator) -> Generator[str, None, None]:
        """Stream transcription results"""
        try:
            requests = (
                speech.StreamingRecognizeRequest(audio_content=chunk)
                for chunk in audio_generator
            )
            
            streaming_config = speech.StreamingRecognitionConfig(
                config=self.config,
                interim_results=True,
            )
            
            responses = self.client.streaming_recognize(
                config=streaming_config,
                requests=requests
            )
            
            for response in responses:
                for result in response.results:
                    if result.alternatives:
                        transcript = result.alternatives[0].transcript
                        yield transcript
                        
        except Exception as e:
            logger.error(f"Streaming transcription failed: {e}")

class GoogleTextToSpeech:
    """Google Cloud Text-to-Speech client"""
    
    def __init__(self):
        if not GOOGLE_CLOUD_AVAILABLE:
            raise RuntimeError("Google Cloud Text-to-Speech library not available")
        
        try:
            self.client = texttospeech.TextToSpeechClient()
            self.voice = texttospeech.VoiceSelectionParams(
                language_code=Config.TTS_LANGUAGE,
                name=Config.TTS_VOICE,
            )
            self.audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=Config.TTS_SPEED,
                pitch=Config.TTS_PITCH,
            )
            logger.info("Google Text-to-Speech client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Text-to-Speech client: {e}")
            raise
    
    def synthesize_speech(self, text: str) -> Optional[bytes]:
        """Convert text to speech"""
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )
            
            logger.info(f"Text-to-speech synthesis completed for: '{text[:50]}...'")
            return response.audio_content
        except Exception as e:
            logger.error(f"Text-to-speech synthesis failed: {e}")
            return None
    
    def play_audio(self, audio_data: bytes):
        """Play audio data"""
        try:
            # Save to temporary file and play
            temp_file = Path.cwd() / "temp_audio.mp3"
            with open(temp_file, "wb") as f:
                f.write(audio_data)
            
            # Play using system command
            if os.name == 'nt':  # Windows
                os.system(f'start "" "{temp_file}"')
            else:  # Linux/Mac
                os.system(f'mpg123 "{temp_file}"')
            
            # Clean up after a delay
            threading.Timer(3.0, lambda: temp_file.unlink(missing_ok=True)).start()
            
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")

class WhisperSpeechToText:
    """Offline speech-to-text using Whisper"""
    
    def __init__(self, model_name: str = "base"):
        if not WHISPER_AVAILABLE:
            raise RuntimeError("Whisper not available")
        
        try:
            self.model = whisper.load_model(model_name)
            logger.info(f"Whisper model '{model_name}' loaded")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe_audio_file(self, audio_file: str) -> Optional[str]:
        """Transcribe audio file using Whisper"""
        try:
            result = self.model.transcribe(audio_file)
            text = result["text"].strip()
            logger.info(f"Whisper transcription: '{text}'")
            return text
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return None
    
    def transcribe_audio_data(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio data using Whisper"""
        try:
            # Save to temporary file
            temp_file = Path.cwd() / "temp_audio.wav"
            
            with wave.open(str(temp_file), 'wb') as wf:
                wf.setnchannels(AudioConfig.CHANNELS)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(AudioConfig.RATE)
                wf.writeframes(audio_data)
            
            # Transcribe
            result = self.transcribe_audio_file(str(temp_file))
            
            # Cleanup
            temp_file.unlink(missing_ok=True)
            
            return result
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return None

class SpeechService:
    """Unified speech service combining all speech functionality"""
    
    def __init__(self):
        self.recorder = AudioRecorder() if PYAUDIO_AVAILABLE else None
        self.google_stt = None
        self.google_tts = None
        self.whisper_stt = None
        self.offline_mode = Config.OFFLINE_MODE
        
        # Initialize services based on availability
        if GOOGLE_CLOUD_AVAILABLE and not self.offline_mode:
            try:
                self.google_stt = GoogleSpeechToText()
                self.google_tts = GoogleTextToSpeech()
                logger.info("Google Cloud services initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Google services: {e}")
                self.offline_mode = True
        
        if self.offline_mode and WHISPER_AVAILABLE:
            try:
                self.whisper_stt = WhisperSpeechToText(Config.WHISPER_MODEL)
                logger.info("Whisper offline mode initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Whisper: {e}")
    
    def is_available(self) -> bool:
        """Check if speech services are available"""
        return (self.google_stt is not None) or (self.whisper_stt is not None)
    
    def start_recording(self, callback: Optional[Callable] = None):
        """Start audio recording"""
        if self.recorder:
            self.recorder.start_recording(callback)
        else:
            raise RuntimeError("Audio recorder not available")
    
    def stop_recording_and_transcribe(self) -> Optional[str]:
        """Stop recording and transcribe the audio"""
        if not self.recorder:
            return None
        
        audio_data = self.recorder.stop_recording()
        if not audio_data:
            return None
        
        # Transcribe using available service
        if self.google_stt and not self.offline_mode:
            return self.google_stt.transcribe_audio(audio_data)
        elif self.whisper_stt:
            return self.whisper_stt.transcribe_audio_data(audio_data)
        else:
            logger.error("No transcription service available")
            return None
    
    def text_to_speech(self, text: str) -> bool:
        """Convert text to speech and play it"""
        if self.google_tts and not self.offline_mode:
            audio_data = self.google_tts.synthesize_speech(text)
            if audio_data:
                self.google_tts.play_audio(audio_data)
                return True
        
        # Fallback to system TTS (basic)
        try:
            if os.name == 'nt':  # Windows
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                return True
        except ImportError:
            logger.warning("No TTS service available")
        
        return False
    
    def cleanup(self):
        """Cleanup all resources"""
        if self.recorder:
            self.recorder.cleanup()

# Test functions
def test_speech_services():
    """Test speech services functionality"""
    print("Testing Speech Services...")
    
    service = SpeechService()
    
    if not service.is_available():
        print("❌ No speech services available")
        return False
    
    print("✅ Speech services initialized")
    
    # Test TTS
    print("Testing Text-to-Speech...")
    if service.text_to_speech("Hello, this is a test of the text to speech system."):
        print("✅ Text-to-Speech working")
    else:
        print("❌ Text-to-Speech failed")
    
    print("Speech services test completed")
    return True

if __name__ == "__main__":
    # Run tests
    test_speech_services()