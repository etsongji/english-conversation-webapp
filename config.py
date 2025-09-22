"""
Configuration module for English Conversation App
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Project directories
    BASE_DIR = Path(__file__).parent.absolute()
    CREDENTIALS_DIR = BASE_DIR / "credentials"
    CONVERSATIONS_DIR = BASE_DIR / "conversations"
    
    # Google Cloud configuration
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
        'GOOGLE_APPLICATION_CREDENTIALS', 
        str(CREDENTIALS_DIR / "google-credentials.json")
    )
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', 'speechtotext-472900')
    
    # Speech configuration
    SPEECH_LANGUAGE = os.getenv('SPEECH_LANGUAGE', 'en-US')
    AUDIO_SAMPLE_RATE = int(os.getenv('AUDIO_SAMPLE_RATE', '16000'))
    AUDIO_CHUNK_SIZE = int(os.getenv('AUDIO_CHUNK_SIZE', '1024'))
    
    # Text-to-Speech configuration
    TTS_LANGUAGE = os.getenv('TTS_LANGUAGE', 'en-US')
    TTS_VOICE = os.getenv('TTS_VOICE', 'en-US-Wavenet-D')
    TTS_SPEED = float(os.getenv('TTS_SPEED', '1.0'))
    TTS_PITCH = float(os.getenv('TTS_PITCH', '0.0'))
    
    # AI configuration
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai')  # 'openai' or 'ollama'
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Ollama configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')
    
    # Offline mode configuration (Whisper)
    OFFLINE_MODE = os.getenv('OFFLINE_MODE', 'false').lower() == 'true'
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')
    
    # UI Configuration
    WINDOW_WIDTH = int(os.getenv('WINDOW_WIDTH', '800'))
    WINDOW_HEIGHT = int(os.getenv('WINDOW_HEIGHT', '600'))
    THEME = os.getenv('THEME', 'light')  # 'light' or 'dark'
    
    # Audio settings
    VOICE_ACTIVATION_THRESHOLD = float(os.getenv('VOICE_ACTIVATION_THRESHOLD', '0.01'))
    SILENCE_THRESHOLD = float(os.getenv('SILENCE_THRESHOLD', '0.5'))  # seconds
    MAX_RECORDING_TIME = int(os.getenv('MAX_RECORDING_TIME', '30'))  # seconds
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = BASE_DIR / "app.log"
    
    @classmethod
    def validate_config(cls):
        """Validate configuration and check dependencies"""
        errors = []
        warnings = []
        
        # Check Google credentials
        if not os.path.exists(cls.GOOGLE_APPLICATION_CREDENTIALS):
            errors.append(f"Google credentials file not found: {cls.GOOGLE_APPLICATION_CREDENTIALS}")
        
        # Check AI configuration
        if cls.AI_PROVIDER == 'openai' and not cls.OPENAI_API_KEY:
            warnings.append("OpenAI API key not set. AI features will be limited.")
        
        # Check directories
        cls.CREDENTIALS_DIR.mkdir(exist_ok=True)
        cls.CONVERSATIONS_DIR.mkdir(exist_ok=True)
        
        return errors, warnings
    
    @classmethod
    def setup_logging(cls):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler()
            ]
        )

class AudioConfig:
    """Audio-specific configuration"""
    
    # PyAudio configuration
    FORMAT = None  # Will be set based on available formats
    CHANNELS = 1
    RATE = Config.AUDIO_SAMPLE_RATE
    CHUNK = Config.AUDIO_CHUNK_SIZE
    
    # Voice activity detection
    VAD_FRAME_DURATION = 30  # ms
    VAD_AGGRESSIVE = 1  # 0-3, higher = more aggressive
    
    # Audio processing
    NOISE_REDUCTION = True
    AUTO_GAIN_CONTROL = True
    
    @classmethod
    def get_audio_format(cls):
        """Get the best available audio format"""
        try:
            import pyaudio
            # Try different formats in order of preference
            formats = [
                pyaudio.paInt16,
                pyaudio.paInt24,
                pyaudio.paInt32,
                pyaudio.paFloat32
            ]
            
            for fmt in formats:
                try:
                    p = pyaudio.PyAudio()
                    if p.is_format_supported(
                        rate=cls.RATE,
                        input_device=None,
                        input_channels=cls.CHANNELS,
                        input_format=fmt
                    ):
                        cls.FORMAT = fmt
                        p.terminate()
                        return fmt
                    p.terminate()
                except:
                    continue
            
            # Default fallback
            cls.FORMAT = pyaudio.paInt16
            return pyaudio.paInt16
            
        except ImportError:
            return None

class UIConfig:
    """UI-specific configuration"""
    
    # Colors
    COLORS = {
        'light': {
            'bg': '#ffffff',
            'fg': '#000000',
            'accent': '#007acc',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'secondary': '#6c757d'
        },
        'dark': {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'accent': '#007acc',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'secondary': '#adb5bd'
        }
    }
    
    # Fonts
    FONTS = {
        'default': ('Segoe UI', 10),
        'heading': ('Segoe UI', 12, 'bold'),
        'monospace': ('Consolas', 9),
        'large': ('Segoe UI', 14)
    }
    
    # Widget sizes
    BUTTON_HEIGHT = 35
    TEXT_WIDGET_HEIGHT = 10
    PROGRESS_BAR_HEIGHT = 20
    
    @classmethod
    def get_colors(cls, theme=None):
        """Get color scheme for the specified theme"""
        theme = theme or Config.THEME
        return cls.COLORS.get(theme, cls.COLORS['light'])

# Initialize configuration
def initialize_config():
    """Initialize and validate configuration"""
    errors, warnings = Config.validate_config()
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(errors))
    
    if warnings:
        print("Configuration warnings:\n" + "\n".join(warnings))
    
    Config.setup_logging()
    AudioConfig.get_audio_format()
    
    return True

if __name__ == "__main__":
    # Test configuration
    try:
        initialize_config()
        print("Configuration validated successfully")
        print(f"Base directory: {Config.BASE_DIR}")
        print(f"Google project: {Config.GOOGLE_CLOUD_PROJECT}")
        print(f"Audio sample rate: {Config.AUDIO_SAMPLE_RATE}")
        print(f"AI provider: {Config.AI_PROVIDER}")
        print(f"Theme: {Config.THEME}")
        print(f"Google credentials: {Config.GOOGLE_APPLICATION_CREDENTIALS}")
    except Exception as e:
        print(f"Configuration error: {e}")