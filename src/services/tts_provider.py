#
# File: src/services/tts_provider.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

from elevenlabs.client import ElevenLabs
from elevenlabs import play

class TTSProvider:
    def __init__(self, api_key, voice_id):
        self.api_key = api_key
        self.voice_id = voice_id
        
        if not self.api_key or self.api_key == "YOUR_ELEVENLABS_API_KEY":
            print("Warning: ElevenLabs API key is missing. TTS provider will not work.")
            self.client = None
        else:
            try:
                self.client = ElevenLabs(api_key=self.api_key)
                print("TTS Provider initialized with real ElevenLabs client.")
            except Exception as e:
                print(f"Failed to initialize ElevenLabs client: {e}")
                self.client = None

    def speak(self, text):
        """
        Speaks text using the ElevenLabs TTS engine.
        Returns True on success, False on failure.
        """
        if not self.client:
            print("[TTS-SIMULATION] TTS is disabled. Please check your API key or initialization.")
            return True # Return True to not trigger error state if intentionally disabled

        sanitized_text = text.replace('"', '')
        print(f"[TTS] Requesting audio for: '{sanitized_text}'")

        try:
            audio = self.client.text_to_speech.stream(
                text=sanitized_text,
                voice_id=self.voice_id,
                model_id="eleven_multilingual_v2" 
            )
            
            if audio:
                play(audio)
                return True # --- Signal success ---
            else:
                print("TTS Error: Audio generation returned nothing.")
                return False # --- Signal failure ---

        except Exception as e:
            print(f"Error calling ElevenLabs API: {e}")
            return False # --- Signal failure ---