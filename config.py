import os
import sys  
from enum import Enum

# Automatically add root folder
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

class LLMProvider(Enum):
    OLLAMA = "ollama"
    GEMINI = "gemini"
    OPENAI = "openai"

class Config:
    # LLM Configuration
    LLM_PROVIDER = LLMProvider.GEMINI  # Change this to switch providers --> OLLAMA, GEMINI, OPENAI
    
    # Ollama Settings
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Google Gemini Settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")
    GEMINI_MODEL = "gemini-1.5-flash"  # or "gemini-1.5-pro" for better quality
    
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
    OPENAI_MODEL = "gpt-4o-mini"  # or "gpt-4o" for better quality
    
    # Temperature settings for creativity
    TEMPERATURE = 0.7
    MAX_TOKENS = 2000
    
    # Whisper settings
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
    
    # TTS settings
    TTS_VOICE = os.getenv("TTS_VOICE", "en-US-JennyNeural")
    
    # Evaluation settings
    EVALUATION_TIMEOUT = int(os.getenv("EVALUATION_TIMEOUT", "30"))  # seconds
    
    # Interview settings
    QUESTION_TIMEOUT = int(os.getenv("QUESTION_TIMEOUT", "120"))  # seconds
    MAX_QUESTIONS = int(os.getenv("MAX_QUESTIONS", "10"))
    MIN_ANSWER_LENGTH = int(os.getenv("MIN_ANSWER_LENGTH", "10"))  # characters
    SKIP_KEYWORDS = os.getenv("SKIP_KEYWORDS", "skip,next question,move on").split(",")
    
    # Audio processing settings
    SILENCE_DURATION = float(os.getenv("SILENCE_DURATION", "5.0"))  # seconds
    SILENCE_THRESHOLD = float(os.getenv("SILENCE_THRESHOLD", "300"))  # RMS value
    MAX_RECORDING_TIME = float(os.getenv("MAX_RECORDING_TIME", "60.0"))  # seconds
    AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))  # Hz
    AUDIO_CHUNK_SIZE = int(os.getenv("AUDIO_CHUNK_SIZE", "1024"))  # bytes