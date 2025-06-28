#
# File: src/core/app_logic.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from src.services.ai_provider import AIProvider
from src.services.tts_provider import TTSProvider
from src.services.stt_provider import STTProvider
import datetime
import pygetwindow as gw

class CoreService(QObject):
    message_ready_for_ui = pyqtSignal(str)
    tts_status_updated = pyqtSignal(bool)
    is_listening_updated = pyqtSignal(bool)

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.is_on = True
        self.has_greeted = False
        self.tts_error_state = False
        self.initialize_services()
        self.proactive_timer = QTimer(self)
        self.proactive_timer.timeout.connect(self.trigger_proactive_event)
        self.update_timer_from_settings()

    def initialize_services(self):
        ai_config = self.settings.get('ai', {})
        self.ai_provider = AIProvider(ai_config=ai_config)

        # --- CORRECTED: Get ElevenLabs key from its new home ---
        elevenlabs_key = self.settings.get('ai', {}).get('elevenlabs_api_key', '')
        voice_id = self.settings.get('voice', {}).get('voice_id')
        self.tts_provider = TTSProvider(api_key=elevenlabs_key, voice_id=voice_id)

        mic_index = self.settings.get('audio_input', {}).get('mic_device_index')
        self.stt_provider = STTProvider(device_index=mic_index)

    # ... (the rest of the file is unchanged) ...
    def update_timer_from_settings(self):
        proactivity_settings = self.settings.get('proactivity', {})
        if self.is_on and proactivity_settings.get('enabled', False):
            frequency_ms = proactivity_settings.get('frequency_seconds', 60) * 1000
            self.proactive_timer.start(frequency_ms)
            print(f"Proactive timer (re)started. Will trigger every {frequency_ms / 1000} seconds.")
        else:
            self.proactive_timer.stop()
            print("Proactive timer stopped.")

    def update_settings(self, new_settings):
        print("Core service received settings update.")
        self.settings = new_settings
        self.tts_error_state = False
        self.tts_status_updated.emit(True)
        self.initialize_services()
        self.update_timer_from_settings()

    def set_state(self, is_on):
        self.is_on = is_on
        print(f"Companion state set to: {'On' if self.is_on else 'Off'}")
        self.update_timer_from_settings()
    
    def _get_active_window_context(self):
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                return f"The user is currently in an application with the window title: '{active_window.title}'."
        except Exception as e:
            print(f"Could not get active window: {e}")
        return "Could not determine the user's current application."
        
    def trigger_proactive_event(self):
        if not self.is_on: return
        print("\n--- Triggering Proactive Event ---")
        if not self.has_greeted:
            prompt = "Start with a brief, friendly greeting appropriate for the time of day. Then, based on the context (like the app they're using), offer a helpful tip or an encouraging thought."
            self.has_greeted = True
            print("First interaction: Sending greeting prompt.")
        else:
            prompt = "Based on the context I've provided in the system prompt (current app, time, etc.), offer a brief, relevant, and helpful tip, a fun fact, or an encouraging thought. Do NOT include a greeting like 'hello' or 'good morning'."
            print("Subsequent interaction: Sending direct prompt.")
        system_prompt = self.settings.get('ai_personality', {}).get('system_prompt', 'You are a helpful assistant.')
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_system_prompt = f"{system_prompt}\n\nCurrent date and time is: {now}."
        if self.settings.get('context_awareness', {}).get('enabled', False):
            window_context = self._get_active_window_context()
            print(f"Context awareness: {window_context}")
            full_system_prompt += f"\n\n{window_context}"
        self._get_and_process_ai_response(prompt, full_system_prompt)

    def handle_voice_input(self):
        if not self.is_on: return
        self.is_listening_updated.emit(True)
        transcribed_text = self.stt_provider.listen_and_transcribe()
        self.is_listening_updated.emit(False)
        if transcribed_text:
            self.process_user_message(transcribed_text)
        else:
            self.message_ready_for_ui.emit("Sorry, I didn't catch that. Please try again.")

    def process_user_message(self, user_text):
        if not self.is_on: return
        print(f"\n--- Processing User Message: '{user_text}' ---")
        system_prompt = self.settings.get('ai_personality', {}).get('system_prompt', 'You are a helpful assistant.')
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_system_prompt = f"{system_prompt}\n\nCurrent date and time is: {now}."
        self._get_and_process_ai_response(user_text, full_system_prompt)

    def _get_and_process_ai_response(self, user_prompt, system_prompt):
        ai_response = self.ai_provider.get_response(user_prompt, system_prompt)
        self.message_ready_for_ui.emit(ai_response)
        
        if self.settings.get('voice', {}).get('enabled', False) and not self.tts_error_state:
            success = self.tts_provider.speak(ai_response)
            if not success:
                self.tts_error_state = True
                self.tts_status_updated.emit(False)
        elif self.tts_error_state:
            print("[TTS-SIMULATION] TTS is temporarily disabled due to a previous error.")