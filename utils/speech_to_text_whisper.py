# utils/speech_to_text_whisper.py - WebM/Opus compatible version

import whisper
import numpy as np
import io
import os
import tempfile
import time

try:
    import whisper
    WHISPER_AVAILABLE = True
    print("✅ Whisper imported successfully")
except ImportError as e:
    WHISPER_AVAILABLE = False
    print(f"❌ Whisper not available: {e}")

# Try to import audio processing libraries
try:
    import librosa
    LIBROSA_AVAILABLE = True
    print("✅ Librosa available for audio format conversion")
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️ Librosa not available - limited audio format support")

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
    print("✅ SoundFile available")
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("⚠️ SoundFile not available")

class WebMCompatibleSpeechToText:
    """
    Speech-to-text that handles WebM/Opus audio from browser MediaRecorder
    """
    
    def __init__(self, model_name="base"):
        self.model = None
        self.model_name = model_name
        
        if not WHISPER_AVAILABLE:
            print("⚠️ Whisper not available - speech-to-text disabled")
            return
            
        try:
            print(f"🔄 Loading Whisper model: {model_name}")
            self.model = whisper.load_model(model_name, device="cpu")
            print(f"✅ Whisper model '{model_name}' loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load Whisper model: {e}")
            self.model = None

    def detect_audio_format(self, audio_bytes):
        """Detect the audio format from the first few bytes"""
        if len(audio_bytes) < 12:
            return "unknown"
        
        # Check for different audio format signatures
        header = audio_bytes[:12]
        
        if header[:4] == b'RIFF' and header[8:12] == b'WAVE':
            return "wav"
        elif header[:4] == b'\x1a\x45\xdf\xa3':  # EBML header (WebM)
            return "webm"
        elif header[:3] == b'ID3' or header[:2] == b'\xff\xfb':
            return "mp3"
        elif header[:4] == b'OggS':
            return "ogg"
        elif header[:4] == b'fLaC':
            return "flac"
        else:
            return "unknown"

    def transcribe_audio_data(self, audio_bytes):
        """
        Transcribe audio data from any format supported by browser
        """
        if not self.model:
            raise Exception("Whisper model not loaded")
        
        print(f"🎯 Processing audio data in memory ({len(audio_bytes)} bytes)")
        
        # Detect audio format
        audio_format = self.detect_audio_format(audio_bytes)
        print(f"🔍 Detected audio format: {audio_format}")
        
        try:
            # Method 1: Try librosa (handles most formats including WebM)
            if LIBROSA_AVAILABLE:
                audio_np = self._load_with_librosa(audio_bytes)
                if audio_np is not None:
                    return self._transcribe_numpy_array(audio_np)
            
            # Method 2: Try temporary file approach (fallback)
            audio_np = self._load_with_temp_file(audio_bytes)
            if audio_np is not None:
                return self._transcribe_numpy_array(audio_np)
            
            # Method 3: Last resort - try to process as raw audio
            print("⚠️ Trying raw audio processing as last resort...")
            return self._try_raw_audio_processing(audio_bytes)
            
        except Exception as e:
            print(f"❌ All transcription methods failed: {e}")
            raise Exception(f"Could not process audio format '{audio_format}': {e}")
    
    def _load_with_librosa(self, audio_bytes):
        """Load audio using librosa (handles WebM, MP3, etc.)"""
        try:
            print("🎵 Trying librosa for audio loading...")
            
            # Create temporary file for librosa to read
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            try:
                # Load with librosa
                audio_np, sample_rate = librosa.load(temp_path, sr=None)
                print(f"✅ Librosa loaded audio: shape={audio_np.shape}, sr={sample_rate}")
                
                # Resample to 16kHz if needed (Whisper expects 16kHz)
                if sample_rate != 16000:
                    audio_np = librosa.resample(audio_np, orig_sr=sample_rate, target_sr=16000)
                    print(f"🔄 Resampled from {sample_rate}Hz to 16000Hz")
                
                return audio_np
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Librosa method failed: {e}")
            return None
    
    def _load_with_temp_file(self, audio_bytes):
        """Load audio using temporary file with multiple format attempts"""
        try:
            print("📁 Trying temporary file method...")
            
            # Try different extensions
            extensions = [".webm", ".ogg", ".mp3", ".wav", ".m4a"]
            
            for ext in extensions:
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                        temp_file.write(audio_bytes)
                        temp_path = temp_file.name
                    
                    print(f"🧪 Trying extension: {ext}")
                    
                    # Try to load with librosa
                    if LIBROSA_AVAILABLE:
                        audio_np, sr = librosa.load(temp_path, sr=16000)
                        print(f"✅ Success with {ext}: shape={audio_np.shape}")
                        
                        # Clean up
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                        
                        return audio_np
                    
                    # Clean up if failed
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
                except Exception as e:
                    print(f"⚠️ Extension {ext} failed: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"⚠️ Temporary file method failed: {e}")
            return None
    
    def _try_raw_audio_processing(self, audio_bytes):
        """Last resort: try to interpret as raw audio data"""
        try:
            print("🔧 Trying raw audio interpretation...")
            
            # Try different interpretations
            interpretations = [
                (np.int16, 32768.0),
                (np.int32, 2147483648.0),
                (np.float32, 1.0),
            ]
            
            for dtype, scale in interpretations:
                try:
                    # Skip if not enough data
                    if len(audio_bytes) < 1000:
                        continue
                    
                    # Try to interpret as this data type
                    audio_np = np.frombuffer(audio_bytes, dtype=dtype).astype(np.float32)
                    
                    if dtype != np.float32:
                        audio_np = audio_np / scale
                    
                    # Check if data looks reasonable
                    if len(audio_np) > 1000 and np.max(np.abs(audio_np)) > 0.001:
                        print(f"✅ Raw interpretation successful: {dtype}, shape={audio_np.shape}")
                        return self._transcribe_numpy_array(audio_np)
                
                except Exception as e:
                    print(f"⚠️ Raw interpretation {dtype} failed: {e}")
                    continue
            
            return ""
            
        except Exception as e:
            print(f"⚠️ Raw audio processing failed: {e}")
            return ""
    
    def _transcribe_numpy_array(self, audio_np):
        """Transcribe numpy audio array using Whisper (same as working example)"""
        try:
            print(f"📐 Processing audio array: shape={audio_np.shape}")
            
            # Check audio length
            if len(audio_np) < 1000:  # Less than ~0.06 seconds at 16kHz
                print("⚠️ Audio too short")
                return ""
            
            duration = len(audio_np) / 16000  # Assuming 16kHz
            print(f"📏 Audio duration: {duration:.2f} seconds")
            
            # Use the same processing as the working example
            audio_padded = whisper.pad_or_trim(audio_np)
            print("✅ Audio padded/trimmed")
            
            # Create mel spectrogram
            mel = whisper.log_mel_spectrogram(audio_padded).to(self.model.device)
            print("✅ Mel spectrogram created")
            
            # Detect language (same as working example)
            _, probs = self.model.detect_language(mel)
            language = max(probs, key=probs.get)
            print(f"🌍 Detected language: {language}")
            
            # Decode audio (same as working example)
            print("🤖 Starting Whisper decode...")
            result = whisper.decode(
                self.model, 
                mel, 
                whisper.DecodingOptions(
                    language=language, 
                    fp16=False
                )
            )
            
            transcription = result.text.strip()
            print(f"✅ Transcription successful: '{transcription}'")
            
            # Clean up transcription
            if transcription:
                transcription = self._clean_transcription(transcription)
                print(f"🧹 Cleaned transcription: '{transcription}'")
            
            return transcription
            
        except Exception as e:
            print(f"❌ Numpy array transcription failed: {e}")
            raise
    
    def transcribe_audio(self, audio_file_path):
        """Transcribe from file path (fallback method)"""
        print(f"📁 Reading audio file: {audio_file_path}")
        
        if not os.path.exists(audio_file_path):
            raise Exception(f"Audio file not found: {audio_file_path}")
        
        # Read file into memory
        with open(audio_file_path, 'rb') as f:
            audio_bytes = f.read()
        
        print(f"📦 Read {len(audio_bytes)} bytes from file")
        
        # Process in memory
        return self.transcribe_audio_data(audio_bytes)
    
    def _clean_transcription(self, text):
        """Clean up transcription result"""
        if not text:
            return ""
        
        # Remove common noise words/artifacts
        noise_words = [
            "you", "uh", "um", "ah", "er", "hmm", "mm",
            "thank you", "thanks", "bye", "hello", "hi",
            "okay", "ok"
        ]
        
        text = text.strip()
        
        # Filter out very short or noise-only responses
        words = text.lower().split()
        clean_words = [w.strip(".,!?") for w in words]
        
        if len(text) < 3 or all(word in noise_words for word in clean_words):
            print("🔇 Detected only noise/artifacts")
            return ""
        
        # Basic cleanup
        text = " ".join(text.split())  # Normalize whitespace
        
        return text

# Legacy wrapper for compatibility
class SpeechToText(WebMCompatibleSpeechToText):
    """Legacy wrapper to maintain compatibility"""
    pass

# Factory function
def create_speech_to_text(model_name="base", enhanced=True):
    """Create SpeechToText instance with WebM compatibility"""
    print(f"🏭 Creating WebM-compatible speech-to-text instance: model={model_name}")
    return WebMCompatibleSpeechToText(model_name)

# Installation check
def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking audio processing dependencies...")
    
    if not LIBROSA_AVAILABLE:
        print("⚠️ librosa not installed. Install with: pip install librosa")
        print("   This is needed for WebM/Opus audio format support")
    
    if not SOUNDFILE_AVAILABLE:
        print("⚠️ soundfile not installed. Install with: pip install soundfile")
        print("   This provides additional audio format support")
    
    if LIBROSA_AVAILABLE and SOUNDFILE_AVAILABLE:
        print("✅ All audio dependencies available")
    else:
        print("📦 For full compatibility, install: pip install librosa soundfile")

if __name__ == "__main__":
    check_dependencies()