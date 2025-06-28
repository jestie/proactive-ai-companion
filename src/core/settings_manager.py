#
# File: src/core/settings_manager.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

import json
import os

CONFIG_FILE = 'config.json'

def load_settings():
    """Loads settings from config.json, ensuring UTF-8 encoding."""
    if os.path.exists(CONFIG_FILE):
        # --- ADD encoding="utf-8" TO FIX THE ERROR ---
        with open(CONFIG_FILE, 'r', encoding="utf-8") as f:
            return json.load(f)
    else:
        print(f"Warning: {CONFIG_FILE} not found. Using default settings.")
        return {}

def save_settings(settings):
    """Saves the given settings dictionary to config.json, ensuring UTF-8 encoding."""
    # --- ADD encoding="utf-8" TO FIX THE ERROR ---
    with open(CONFIG_FILE, 'w', encoding="utf-8") as f:
        # ensure_ascii=False allows special characters to be written correctly
        json.dump(settings, f, indent=2, ensure_ascii=False)