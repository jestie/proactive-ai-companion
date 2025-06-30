#
# File: src/services/stt_provider.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

import speech_recognition as sr
import threading
import queue
import logging

class STTProvider:
    @staticmethod
    def list_microphones():
        return sr.Microphone.list_microphone_names()

    def __init__(self, device_index=None):
        self.logger = logging.getLogger("technical")
        self.recognizer = sr.Recognizer()
        self.device_index = device_index
        self.microphone = None
        self.stop_listening_func = None
        self.is_listening = False
        
        self.recognizer.energy_threshold = 3000
        self.recognizer.dynamic_energy_threshold = False
        
        try:
            self.microphone = sr.Microphone(device_index=self.device_index)
            with self.microphone as source:
                self.logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.logger.info(f"Calibration complete. Energy threshold set to: {self.recognizer.energy_threshold}")
        except Exception as e:
            self.logger.critical(f"Could not open microphone with index {self.device_index}. STT will not work. Error: {e}")

    def start_background_listening(self, callback):
        if self.is_listening or not self.microphone: return
        self.is_listening = True
        self.stop_listening_func = self.recognizer.listen_in_background(
            self.microphone,
            lambda r, a: self._process_audio_thread(r, a, callback),
            phrase_time_limit=10
        )
        self.logger.info("Started 'Always-On' background listening.")

    def stop_background_listening(self):
        if self.stop_listening_func:
            self.stop_listening_func(wait_for_stop=False)
            self.stop_listening_func = None
            self.is_listening = False
            self.logger.info("Stopped 'Always-On' background listening.")

    def _process_audio_thread(self, recognizer, audio, callback):
        self.logger.info("Audio detected by background listener, processing...")
        try:
            text = recognizer.recognize_google(audio)
            self.logger.info(f"Background transcription successful: '{text}'")
            callback(text)
        except sr.UnknownValueError:
            self.logger.warning("Background listener could not understand the audio.")
        except sr.RequestError as e:
            self.logger.error(f"Background listener API request failed: {e}")

    def listen_on_demand(self):
        if not self.microphone:
            self.logger.error("On-demand listening failed: No microphone available.")
            return None
        try:
            with self.microphone as source:
                self.logger.info("Listening on-demand for voice input...")
                audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=15)
            self.logger.info("Transcribing on-demand audio...")
            text = self.recognizer.recognize_google(audio)
            self.logger.info(f"On-demand transcription successful: '{text}'")
            return text
        except sr.WaitTimeoutError:
            self.logger.info("On-demand listener: No speech detected.")
            return None
        except sr.UnknownValueError:
            self.logger.warning("On-demand listener could not understand the audio.")
            return None
        except sr.RequestError as e:
            self.logger.error(f"On-demand listener API request failed: {e}")
            return None