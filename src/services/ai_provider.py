#
# File: src/services/ai_provider.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

from openai import OpenAI
import requests
import json

class AIProvider:
    def __init__(self, ai_config):
        """Initializes based on the entire AI configuration block."""
        self.config = ai_config
        self.provider = self.config.get('provider', 'openai')
        self.openai_client = None

        if self.provider == 'openai':
            api_key = self.config.get('openai_settings', {}).get('api_key')
            if not api_key or api_key == "YOUR_NEW_OPENAI_API_KEY":
                print("Warning: OpenAI API key is missing.")
            else:
                self.openai_client = OpenAI(api_key=api_key)
                print("AI Provider initialized for OpenAI.")
        else:
            print(f"AI Provider initialized for Ollama (model: {self.config.get('ollama_settings', {}).get('model')}).")

    def get_response(self, user_prompt, system_prompt="You are a helpful assistant."):
        """Gets a response from the configured AI provider."""
        if self.provider == 'ollama':
            return self._call_ollama(user_prompt, system_prompt)
        elif self.openai_client:
            return self._call_openai(user_prompt, system_prompt)
        else:
            return "AI provider not configured. Please check your settings."

    def _call_openai(self, user_prompt, system_prompt):
        """Private method to call the OpenAI API."""
        print(f"System Prompt (OpenAI): '{system_prompt}'")
        print(f"User Prompt (OpenAI): '{user_prompt}'")
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return "I encountered an error with the OpenAI API."

    def _call_ollama(self, user_prompt, system_prompt):
        """Private method to call a local Ollama instance."""
        ollama_settings = self.config.get('ollama_settings', {})
        host = ollama_settings.get('host', 'http://localhost:11434')
        model = ollama_settings.get('model', 'llama3')
        
        print(f"System Prompt (Ollama): '{system_prompt}'")
        print(f"User Prompt (Ollama): '{user_prompt}'")
        
        try:
            response = requests.post(
                f"{host}/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "stream": False
                }
            )
            response.raise_for_status() # Raise an exception for bad status codes
            
            response_data = response.json()
            return response_data['message']['content'].strip()
            
        except requests.exceptions.ConnectionError:
            return f"Ollama connection failed. Is Ollama running at {host}?"
        except Exception as e:
            print(f"Error calling Ollama API: {e}")
            return "I encountered an error with the Ollama API."