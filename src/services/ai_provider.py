#
# File: src/services/ai_provider.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

from openai import OpenAI
import requests
import json
import logging

class AIProvider:
    def __init__(self, ai_config):
        self.logger = logging.getLogger("technical")
        self.config = ai_config
        self.provider = self.config.get('provider', 'openai')
        self.openai_client = None

        if self.provider == 'openai':
            api_key = self.config.get('openai_settings', {}).get('api_key')
            if not api_key or "MYAPIKEY" in api_key: # More robust placeholder check
                self.logger.warning("OpenAI API key is missing or is a placeholder.")
            else:
                self.openai_client = OpenAI(api_key=api_key)
                self.logger.info("AI Provider initialized for OpenAI.")
        else:
            self.logger.info(f"AI Provider initialized for Ollama (model: {self.config.get('ollama_settings', {}).get('model')}).")

    def get_response(self, message_history):
        if self.provider == 'ollama':
            return self._call_ollama(message_history)
        elif self.openai_client:
            return self._call_openai(message_history)
        else:
            self.logger.error("AI provider not configured or key is missing.")
            return "AI provider not configured. Please check your settings."

    def _call_openai(self, message_history):
        self.logger.info(f"Sending message history to OpenAI ({len(message_history)} messages)...")
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=message_history
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Error calling OpenAI API: {e}")
            return "I encountered an error with the OpenAI API."

    def _call_ollama(self, message_history):
        ollama_settings = self.config.get('ollama_settings', {})
        host = ollama_settings.get('host', 'http://localhost:11434')
        model = ollama_settings.get('model', 'llama3')
        
        self.logger.info(f"Sending message history to Ollama ({len(message_history)} messages)...")
        
        try:
            response = requests.post(
                f"{host}/api/chat",
                json={"model": model, "messages": message_history, "stream": False}
            )
            response.raise_for_status()
            response_data = response.json()
            return response_data['message']['content'].strip()
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Ollama connection failed at {host}.")
            return f"Ollama connection failed. Is Ollama running at {host}?"
        except Exception as e:
            self.logger.error(f"Error calling Ollama API: {e}")
            return "I encountered an error with the Ollama API."