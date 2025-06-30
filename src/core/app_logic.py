#
# File: src/core/app_logic.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot
from src.services.ai_provider import AIProvider
from src.services.tts_provider import TTSProvider
from src.services.stt_provider import STTProvider
import datetime
import pygetwindow as gw
import logging

class CoreService(QObject):
    # ... (signals are unchanged) ...
    message_ready_for_ui = pyqtSignal(dict); new_conversation_started = pyqtSignal()
    tts_status_updated = pyqtSignal(bool); is_listening_updated = pyqtSignal(bool)

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.is_on = True; self.has_greeted = False; self.tts_error_state = False
        self.conversation_history = []
        self.tech_logger = logging.getLogger("technical"); self.conv_logger = logging.getLogger("conversation")
        self.initialize_services()
        self.proactive_timer = QTimer(self)
        self.proactive_timer.timeout.connect(self.trigger_proactive_event)
        self.update_timer_from_settings()
        self.manage_background_listener()

    def initialize_services(self):
        self.tech_logger.info("Initializing services...")
        ai_config = self.settings.get('ai', {})
        self.ai_provider = AIProvider(ai_config=ai_config)
        
        # --- UPDATED to pass correct config to the new TTS provider ---
        tts_config = self.settings.get('voice', {})
        elevenlabs_api_key = self.settings.get('ai', {}).get('elevenlabs_api_key', '')
        self.tts_provider = TTSProvider(tts_config=tts_config, elevenlabs_api_key=elevenlabs_api_key)

        mic_index = self.settings.get('audio_input', {}).get('mic_device_index')
        self.stt_provider = STTProvider(device_index=mic_index)

    # ... (the rest of your file is unchanged from the previous logging version) ...
    def manage_background_listener(self):
        is_always_on = self.settings.get('audio_input', {}).get('always_on_listening', False)
        if is_always_on and self.is_on: self.stt_provider.start_background_listening(self.process_user_message)
        else: self.stt_provider.stop_background_listening()
            
    def update_settings(self, new_settings):
        self.tech_logger.info("Core service applying settings update.")
        self.stt_provider.stop_background_listening()
        self.settings = new_settings; self.tts_error_state = False
        self.tts_status_updated.emit(True); self.initialize_services()
        self.update_timer_from_settings(); self.manage_background_listener()

    def update_timer_from_settings(self):
        proactivity_settings = self.settings.get('proactivity', {})
        if self.is_on and proactivity_settings.get('enabled', False):
            frequency_ms = proactivity_settings.get('frequency_seconds', 60) * 1000
            self.proactive_timer.start(frequency_ms)
            self.tech_logger.info(f"Proactive timer (re)started. Firing every {frequency_ms / 1000} seconds.")
        else:
            self.proactive_timer.stop(); self.tech_logger.info("Proactive timer stopped.")

    def set_state(self, is_on):
        self.is_on = is_on; self.tech_logger.info(f"Companion state set to: {'On' if self.is_on else 'Off'}")
        self.update_timer_from_settings(); self.manage_background_listener()
    
    def _get_active_window_context(self):
        try:
            active_window = gw.getActiveWindow()
            if active_window: return f"The user is currently in an application with the window title: '{active_window.title}'."
        except Exception as e: self.tech_logger.warning(f"Could not get active window: {e}")
        return "Could not determine the user's current application."
        
    def trigger_proactive_event(self):
        if not self.is_on: return
        self.tech_logger.info("Triggering New Proactive Conversation.")
        self.conversation_history.clear(); self.new_conversation_started.emit()
        self.conv_logger.info("--- Proactive Conversation Started ---")
        if not self.has_greeted:
            prompt = "Start with a brief, friendly greeting... offer a helpful tip or an encouraging thought."
            self.has_greeted = True; self.tech_logger.info("First interaction: Sending greeting prompt.")
        else:
            prompt = "Based on the context... offer a brief, relevant, and helpful tip... Do NOT include a greeting."
            self.tech_logger.info("Subsequent interaction: Sending direct prompt.")
        self._get_and_process_ai_response(prompt)
        
    def handle_voice_input(self):
        if not self.is_on: return
        if self.stt_provider.is_listening:
            self.tech_logger.info("Ignoring click-to-talk because 'Always-On' is active.")
            return
        self.is_listening_updated.emit(True)
        transcribed_text = self.stt_provider.listen_on_demand()
        self.is_listening_updated.emit(False)
        if transcribed_text: self.process_user_message(transcribed_text)
        else: self.message_ready_for_ui.emit({'role': 'assistant', 'content': "Sorry, I didn't catch that."})
            
    @pyqtSlot(str)
    def process_user_message(self, user_text):
        if not self.is_on: return
        self.tech_logger.info(f"Processing User Message: '{user_text}'")
        if not self.conversation_history:
            self.new_conversation_started.emit()
            self.conv_logger.info("--- User-Initiated Conversation Started ---")
        self.message_ready_for_ui.emit({'role': 'user', 'content': user_text})
        self._get_and_process_ai_response(user_text)

    def _get_and_process_ai_response(self, user_prompt):
        self.conv_logger.info(f"USER: {user_prompt}")
        self.conversation_history.append({'role': 'user', 'content': user_prompt})
        system_prompt_text = self.settings.get('ai_personality', {}).get('system_prompt', 'You are a helpful assistant.')
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_system_prompt = f"{system_prompt_text}\n\nCurrent date and time is: {now}."
        if self.settings.get('context_awareness', {}).get('enabled', False) and len(self.conversation_history) <= 1:
            window_context = self._get_active_window_context()
            self.tech_logger.info(f"Context awareness: {window_context}")
            full_system_prompt += f"\n\n{window_context}"
        messages_to_send = [{'role': 'system', 'content': full_system_prompt}] + self.conversation_history
        ai_response = self.ai_provider.get_response(messages_to_send)
        self.conv_logger.info(f"AI: {ai_response}")
        self.conversation_history.append({'role': 'assistant', 'content': ai_response})
        self.message_ready_for_ui.emit({'role': 'assistant', 'content': ai_response})
        if self.settings.get('voice', {}).get('enabled', False) and not self.tts_error_state:
            success = self.tts_provider.speak(ai_response)
            if not success: self.tts_error_state = True; self.tts_status_updated.emit(False)
        elif self.tts_error_state:
            self.tech_logger.info("[TTS Fallback] TTS temporarily disabled due to a previous error.")