#
# File: src/services/stt_provider.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

import speech_recognition as sr

class STTProvider:
    @staticmethod
    def list_microphones():
        """Returns a list of available microphone names."""
        return sr.Microphone.list_microphone_names()

    def __init__(self, device_index=None):
        """Initializes the provider, optionally with a specific device index."""
        self.recognizer = sr.Recognizer()
        self.device_index = device_index
        
        print(f"Attempting to initialize microphone with device index: {self.device_index}")
        
        try:
            # Try to use the specified microphone
            self.microphone = sr.Microphone(device_index=self.device_index)
            # Perform a one-time energy level adjustment for better recognition
            with self.microphone as source:
                print("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source)
                print("Calibration complete.")
        except Exception as e:
            print(f"Could not use microphone index {self.device_index}: {e}.")
            print("Falling back to default microphone.")
            self.device_index = None
            try:
                # Fallback to default
                self.microphone = sr.Microphone()
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
            except Exception as e_default:
                print(f"FATAL: Could not open any microphone. STT will not work. Error: {e_default}")
                self.microphone = None # STT is completely disabled

    def listen_and_transcribe(self):
        """
        Listens for a single utterance from the microphone and returns the transcribed text.
        """
        if not self.microphone:
            print("No microphone available to listen.")
            return None

        try:
            with self.microphone as source:
                print("Listening for voice input...")
                # Increased timeout for better practical use
                audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            print("No speech detected within the timeout period.")
            return None
        except Exception as e:
            print(f"Error accessing microphone: {e}")
            return None

        print("Transcribing audio...")
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"Transcription successful: '{text}'")
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None