# New LLM Manager to handle multiple providers
import google.generativeai as genai
import openai
import requests
import json
from config import Config, LLMProvider

class LLMManager:
    def __init__(self):
        self.provider = Config.LLM_PROVIDER
        self._setup_client()
    
    def _setup_client(self):
        """Initialize the appropriate LLM client"""
        if self.provider == LLMProvider.GEMINI:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.client = genai.GenerativeModel(Config.GEMINI_MODEL)
            print(f"✅ Gemini {Config.GEMINI_MODEL} initialized")
            
        elif self.provider == LLMProvider.OPENAI:
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            print(f"✅ OpenAI {Config.OPENAI_MODEL} initialized")
            
        elif self.provider == LLMProvider.OLLAMA:
            self.client = None  # Ollama uses direct HTTP requests
            print(f"✅ Ollama {Config.OLLAMA_MODEL} initialized")
    
    def generate_response(self, prompt, system_prompt=None):
        """Generate response using the configured LLM provider"""
        try:
            if self.provider == LLMProvider.GEMINI:
                return self._generate_gemini(prompt, system_prompt)
            elif self.provider == LLMProvider.OPENAI:
                return self._generate_openai(prompt, system_prompt)
            elif self.provider == LLMProvider.ANTHROPIC:
                return self._generate_anthropic(prompt, system_prompt)
            elif self.provider == LLMProvider.GROQ:
                return self._generate_groq(prompt, system_prompt)
            elif self.provider == LLMProvider.OLLAMA:
                return self._generate_ollama(prompt, system_prompt)
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return f"Error generating response: {str(e)}"
    
    def _generate_gemini(self, prompt, system_prompt=None):
        """Generate response using Google Gemini"""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        response = self.client.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=Config.TEMPERATURE,
                max_output_tokens=Config.MAX_TOKENS,
            )
        )
        return response.text
    
    def _generate_openai(self, prompt, system_prompt=None):
        """Generate response using OpenAI"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=messages,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
        return response.choices[0].message.content
    
    def _generate_anthropic(self, prompt, system_prompt=None):
        """Generate response using Anthropic Claude"""
        response = self.client.messages.create(
            model=Config.ANTHROPIC_MODEL,
            max_tokens=Config.MAX_TOKENS,
            temperature=Config.TEMPERATURE,
            system=system_prompt or "You are a helpful AI assistant.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def _generate_groq(self, prompt, system_prompt=None):
        """Generate response using Groq"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=messages,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
        return response.choices[0].message.content
    
    def _generate_ollama(self, prompt, system_prompt=None):
        """Generate response using Ollama (existing implementation)"""
        url = f"{Config.OLLAMA_BASE_URL}/api/generate"
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        payload = {
            "model": Config.OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": Config.TEMPERATURE,
                "num_predict": Config.MAX_TOKENS
            }
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise Exception(f"Ollama API error: {response.status_code}")

# Global LLM instance
llm_manager = LLMManager()
