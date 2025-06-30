#
# File: src/core/settings_manager.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

import json
import os

CONFIG_FILE = 'config.json'

def get_default_config():
    """Returns a dictionary containing the default application settings."""
    return {
        "ai": {
            "provider": "openai",
            "openai_settings": {
                "api_key": "YOUR_OPENAI_API_KEY_HERE"
            },
            "ollama_settings": {
                "host": "http://localhost:11434",
                "model": "llama3"
            },
            "elevenlabs_api_key": "YOUR_ELEVENLABS_API_KEY_HERE"
        },
        "proactivity": {
            "enabled": True,
            "frequency_seconds": 60,
            "inactivity_timeout_seconds": 180
        },
        "voice": {
            "enabled": True,
            "voice_id": "21m00Tcm4TlvDq8ikWAM"
        },
        "ui": {
            "theme": "dark",
            "always_on_top": True
        },
        "ai_personality": {
            "system_prompt": "You are a helpful and concise desktop assistant named Companion."
        },
        "context_awareness": {
            "enabled": True
        },
        "audio_input": {
            "mic_device_index": None,
            "always_on_listening": False
        }
    }

def load_settings():
    """
    Loads settings from config.json. If the file doesn't exist,
    it creates it with default settings.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: config.json is corrupted. Backing up and creating a new one.")
            os.rename(CONFIG_FILE, f"{CONFIG_FILE}.corrupted.bak")
            # Fall through to create a new default config
    
    # --- If file doesn't exist or was corrupted, create it ---
    print(f"'{CONFIG_FILE}' not found or was invalid. Creating a new one with default settings.")
    default_settings = get_default_config()
    save_settings(default_settings)
    return default_settings

def save_settings(settings):
    """Saves the given settings dictionary to config.json, ensuring UTF-8 encoding."""
    with open(CONFIG_FILE, 'w', encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)