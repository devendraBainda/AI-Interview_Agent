# New TTS utility using multiple methods
import os
import tempfile
import subprocess
import platform
from config import Config

class TextToSpeech:
    def __init__(self):
        self.available_engines = self._detect_engines()
        print(f"🔊 Available TTS engines: {self.available_engines}")
    
    def _detect_engines(self):
        """Detect available TTS engines"""
        engines = []
        
        # Check for edge-tts (Microsoft Edge TTS)
        try:
            import edge_tts
            engines.append('edge-tts')
        except ImportError:
            pass
        
        # Check for pyttsx3 (cross-platform)
        try:
            import pyttsx3
            engines.append('pyttsx3')
        except ImportError:
            pass
        
        # Check for gTTS (Google TTS)
        try:
            import gtts
            engines.append('gtts')
        except ImportError:
            pass
        
        # System TTS (Windows/macOS/Linux)
        if platform.system() == "Windows":
            engines.append('windows-sapi')
        elif platform.system() == "Darwin":  # macOS
            engines.append('macos-say')
        elif platform.system() == "Linux":
            engines.append('linux-espeak')
        
        return engines
    
    async def speak_text_edge(self, text, voice="en-US-JennyNeural"):
        """Use Microsoft Edge TTS (best quality)"""
        try:
            import edge_tts
            import asyncio
            
            communicate = edge_tts.Communicate(text, voice)
            audio_data = b""
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            return audio_data
        except Exception as e:
            raise Exception(f"Edge TTS failed: {e}")
    
    def speak_text_pyttsx3(self, text):
        """Use pyttsx3 (cross-platform)"""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            
            # Set properties
            engine.setProperty('rate', 150)    # Speed
            engine.setProperty('volume', 0.8)  # Volume
            
            # Get voices and set to female if available
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_path = temp_file.name
            
            engine.save_to_file(text, temp_path)
            engine.runAndWait()
            
            # Read the audio file
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up
            os.remove(temp_path)
            
            return audio_data
            
        except Exception as e:
            raise Exception(f"pyttsx3 TTS failed: {e}")
    
    def speak_text_gtts(self, text, lang='en'):
        """Use Google TTS (requires internet)"""
        try:
            from gtts import gTTS
            import io
            
            tts = gTTS(text=text, lang=lang, slow=False)
            
            # Save to bytes
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.read()
            
        except Exception as e:
            raise Exception(f"Google TTS failed: {e}")
    
    def speak_text_system(self, text):
        """Use system TTS"""
        try:
            system = platform.system()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_path = temp_file.name
            
            if system == "Windows":
                # Use Windows SAPI
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                file_stream = win32com.client.Dispatch("SAPI.SpFileStream")
                file_stream.Open(temp_path, 3)
                speaker.AudioOutputStream = file_stream
                speaker.Speak(text)
                file_stream.Close()
                
            elif system == "Darwin":  # macOS
                # Use macOS say command
                subprocess.run(['say', '-o', temp_path, text], check=True)
                
            elif system == "Linux":
                # Use espeak
                subprocess.run(['espeak', '-w', temp_path, text], check=True)
            
            # Read the audio file
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up
            os.remove(temp_path)
            
            return audio_data
            
        except Exception as e:
            raise Exception(f"System TTS failed: {e}")
    
    def generate_speech(self, text, voice="en-US-JennyNeural"):
        """Generate speech using the best available method"""
        if not text or not text.strip():
            raise Exception("No text provided")
        
        # Try methods in order of preference
        for engine in self.available_engines:
            try:
                if engine == 'edge-tts':
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    audio_data = loop.run_until_complete(self.speak_text_edge(text, voice))
                    loop.close()
                    return audio_data
                    
                elif engine == 'pyttsx3':
                    return self.speak_text_pyttsx3(text)
                    
                elif engine == 'gtts':
                    return self.speak_text_gtts(text)
                    
                elif engine in ['windows-sapi', 'macos-say', 'linux-espeak']:
                    return self.speak_text_system(text)
                    
            except Exception as e:
                print(f"⚠️ {engine} failed: {e}")
                continue
        
        raise Exception("All TTS engines failed")

# Global TTS instance
tts_engine = TextToSpeech()
