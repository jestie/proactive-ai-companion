#
# File: src/services/tts_provider.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

import pyttsx3
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import logging
import threading

class TTSProvider:
    @staticmethod
    def list_local_voices():
        """Returns a list of available local TTS voices."""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            engine.stop() # Necessary to release the engine
            return voices
        except Exception as e:
            logging.getLogger("technical").error(f"Could not list local voices: {e}")
            return []

    def __init__(self, tts_config, elevenlabs_api_key):
        self.logger = logging.getLogger("technical")
        self.config = tts_config
        self.provider = self.config.get('tts_provider', 'elevenlabs')
        self.elevenlabs_client = None
        self.local_engine = None

        if self.provider == 'elevenlabs':
            if not elevenlabs_api_key or "MYAPIKEY" in elevenlabs_api_key:
                self.logger.warning("ElevenLabs API key is missing. TTS will not work.")
            else:
                try:
                    self.elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)
                    self.logger.info("TTS Provider initialized for ElevenLabs.")
                except Exception as e:
                    self.logger.error(f"Failed to initialize ElevenLabs client: {e}")
        
        elif self.provider == 'local':
            try:
                self.local_engine = pyttsx3.init()
                local_voice_id = self.config.get('local_tts_settings', {}).get('voice_id')
                if local_voice_id:
                    self.local_engine.setProperty('voice', local_voice_id)
                self.logger.info("TTS Provider initialized for Local System Voice.")
            except Exception as e:
                self.logger.error(f"Failed to initialize local TTS engine: {e}")
                self.local_engine = None

    def speak(self, text):
        """Speaks text using the configured TTS engine."""
        if self.provider == 'elevenlabs' and self.elevenlabs_client:
            return self._speak_elevenlabs(text)
        elif self.provider == 'local' and self.local_engine:
            return self._speak_local(text)
        else:
            self.logger.warning(f"TTS provider '{self.provider}' not available or configured correctly. Skipping speech.")
            return True # Return true to not trigger a UI error

    def _speak_elevenlabs(self, text):
        sanitized_text = text.replace('"', '')
        self.logger.info(f"[TTS-ElevenLabs] Requesting audio for: '{sanitized_text}'")
        try:
            voice_id = self.config.get('elevenlabs_settings', {}).get('voice_id')
            audio = self.elevenlabs_client.text_to_speech.stream(
                text=sanitized_text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2" 
            )
            if audio:
                play(audio)
                return True
            else:
                self.logger.error("ElevenLabs TTS Error: Audio generation returned nothing.")
                return False
        except Exception as e:
            self.logger.error(f"Error calling ElevenLabs API: {e}")
            return False

    def _speak_local(self, text):
        self.logger.info(f"[TTS-Local] Speaking: '{text}'")
        try:
            # pyttsx3's runAndWait is blocking, so we run it in a thread
            # to avoid freezing the UI.
            def run_tts():
                self.local_engine.say(text)
                self.local_engine.runAndWait()

            tts_thread = threading.Thread(target=run_tts)
            tts_thread.start()
            return True
        except Exception as e:
            self.logger.error(f"Local TTS engine failed: {e}")
            return False