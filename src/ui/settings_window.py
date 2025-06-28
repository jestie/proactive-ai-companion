#
# File: src/ui/settings_window.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QWidget, QFormLayout, 
                             QLineEdit, QCheckBox, QSlider, QLabel, QPushButton, QTextEdit,
                             QGroupBox, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from src.core.settings_manager import save_settings
from src.services.stt_provider import STTProvider
import copy

class SettingsWindow(QDialog):
    settings_updated = pyqtSignal(dict)

    def __init__(self, settings, core_service, parent=None):
        super().__init__(parent)
        self.settings = copy.deepcopy(settings)
        self.core_service = core_service

        self.setWindowTitle("Proactive AI Companion - Settings")
        self.setGeometry(300, 300, 480, 520)
        
        self.settings_updated.connect(self.core_service.update_settings)

        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.create_ai_provider_tab()
        self.create_behavior_tab()
        self.create_audio_tab()
        self.create_personality_tab()

        self.save_button = QPushButton("Save & Close")
        self.save_button.clicked.connect(self.save_and_close)
        main_layout.addWidget(self.save_button)

    def create_ai_provider_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        provider_group = QGroupBox("AI Provider")
        provider_layout = QFormLayout(provider_group)
        self.provider_selector = QComboBox()
        self.provider_selector.addItems(["OpenAI", "Ollama"])
        provider_layout.addRow("Provider:", self.provider_selector)
        layout.addWidget(provider_group)

        # --- Gracefully get settings, even if keys are missing from old configs ---
        ai_settings = self.settings.get('ai', {})
        openai_settings = ai_settings.get('openai_settings', {})
        ollama_settings = ai_settings.get('ollama_settings', {})
        # Handle old api_keys structure for backward compatibility
        old_openai_key = self.settings.get('api_keys', {}).get('openai', '')
        old_eleven_key = self.settings.get('api_keys', {}).get('elevenlabs', '')


        self.openai_group = QGroupBox("OpenAI Settings")
        openai_layout = QFormLayout(self.openai_group)
        self.openai_key_input = QLineEdit(openai_settings.get('api_key', old_openai_key))
        self.openai_key_input.setEchoMode(QLineEdit.Password)
        openai_layout.addRow("API Key:", self.openai_key_input)
        layout.addWidget(self.openai_group)

        self.ollama_group = QGroupBox("Ollama Settings")
        ollama_layout = QFormLayout(self.ollama_group)
        self.ollama_host_input = QLineEdit(ollama_settings.get('host', 'http://localhost:11434'))
        self.ollama_model_input = QLineEdit(ollama_settings.get('model', 'llama3'))
        ollama_layout.addRow("Host:", self.ollama_host_input)
        ollama_layout.addRow("Model Name:", self.ollama_model_input)
        layout.addWidget(self.ollama_group)
        
        # --- NEW: Dedicated ElevenLabs Section ---
        self.elevenlabs_group = QGroupBox("ElevenLabs TTS Settings")
        eleven_layout = QFormLayout(self.elevenlabs_group)
        self.elevenlabs_key_input = QLineEdit(old_eleven_key) # Gets key from old config
        self.elevenlabs_key_input.setEchoMode(QLineEdit.Password)
        eleven_layout.addRow("API Key:", self.elevenlabs_key_input)
        layout.addWidget(self.elevenlabs_group)

        layout.addStretch()
        self.tabs.addTab(tab, "AI & Services") # Renamed tab

        self.provider_selector.currentTextChanged.connect(self.toggle_ai_settings_visibility)
        current_provider = ai_settings.get('provider', 'openai')
        self.provider_selector.setCurrentText(current_provider.capitalize())
        self.toggle_ai_settings_visibility(self.provider_selector.currentText())

    def toggle_ai_settings_visibility(self, provider_name):
        is_ollama = provider_name.lower() == "ollama"
        self.ollama_group.setVisible(is_ollama)
        self.openai_group.setVisible(not is_ollama)
        # ElevenLabs is always visible as it's a separate service
        self.elevenlabs_group.setVisible(True)

    # ... (other create_... tabs are unchanged) ...
    def create_behavior_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        pro_group = QGroupBox("Proactivity")
        pro_layout = QFormLayout(pro_group)
        self.proactivity_enabled_checkbox = QCheckBox()
        self.proactivity_enabled_checkbox.setChecked(self.settings.get('proactivity', {}).get('enabled', False))
        pro_layout.addRow("Enable Proactive Messages:", self.proactivity_enabled_checkbox)
        self.frequency_slider = QSlider(Qt.Horizontal)
        self.frequency_slider.setMinimum(1)
        self.frequency_slider.setMaximum(120)
        self.frequency_slider.setValue(self.settings.get('proactivity', {}).get('frequency_seconds', 60) // 30)
        self.frequency_label = QLabel(f"{self.settings.get('proactivity', {}).get('frequency_seconds', 60)} seconds")
        self.frequency_slider.valueChanged.connect(self.update_frequency_label)
        freq_v_layout = QVBoxLayout()
        freq_v_layout.addWidget(self.frequency_slider)
        freq_v_layout.addWidget(self.frequency_label)
        pro_layout.addRow("Message Frequency:", freq_v_layout)
        layout.addWidget(pro_group)
        context_group = QGroupBox("Context Awareness")
        context_layout = QFormLayout(context_group)
        self.context_enabled_checkbox = QCheckBox()
        self.context_enabled_checkbox.setChecked(self.settings.get('context_awareness', {}).get('enabled', False))
        context_layout.addRow("Enable Active Window Awareness:", self.context_enabled_checkbox)
        layout.addWidget(context_group)
        layout.addStretch()
        self.tabs.addTab(tab, "Behavior")

    def update_frequency_label(self, value):
        seconds = value * 30
        self.frequency_label.setText(f"{seconds} seconds")

    def create_audio_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        input_group = QGroupBox("Audio Input (Microphone)")
        input_layout = QFormLayout(input_group)
        self.mic_selector = QComboBox()
        try:
            mic_names = STTProvider.list_microphones()
            self.mic_selector.addItems(mic_names)
            saved_index = self.settings.get('audio_input', {}).get('mic_device_index')
            if saved_index is not None and 0 <= saved_index < self.mic_selector.count():
                self.mic_selector.setCurrentIndex(saved_index)
            elif self.mic_selector.count() > 0:
                self.mic_selector.setCurrentIndex(0)
        except Exception as e:
            print(f"Could not list microphones for settings panel: {e}")
            self.mic_selector.addItem("Error: Could not list mics")
            self.mic_selector.setEnabled(False)
        input_layout.addRow("Input Device:", self.mic_selector)
        layout.addWidget(input_group)
        output_group = QGroupBox("Audio Output (Text-to-Speech)")
        output_layout = QFormLayout(output_group)
        self.voice_enabled_checkbox = QCheckBox()
        self.voice_enabled_checkbox.setChecked(self.settings.get('voice',{}).get('enabled', False))
        output_layout.addRow("Enable Voice Output:", self.voice_enabled_checkbox)
        self.voice_id_input = QLineEdit(self.settings.get('voice',{}).get('voice_id', ''))
        output_layout.addRow("ElevenLabs Voice ID:", self.voice_id_input)
        layout.addWidget(output_group)
        layout.addStretch()
        self.tabs.addTab(tab, "Audio")
        
    def create_personality_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.addRow(QLabel("<b>AI Personality</b>"))
        layout.addRow(QLabel("Define the AI's core identity and rules."))
        self.system_prompt_input = QTextEdit()
        self.system_prompt_input.setPlainText(self.settings.get('ai_personality',{}).get('system_prompt', ''))
        self.system_prompt_input.setAcceptRichText(False)
        self.system_prompt_input.setFixedHeight(150)
        layout.addRow(self.system_prompt_input)
        self.tabs.addTab(tab, "Personality")

    def save_and_close(self):
        # --- Build the new settings structure from scratch to avoid KeyErrors ---
        # Start with the existing settings to preserve other keys
        new_settings = self.settings 
        
        # Create the 'ai' block if it doesn't exist
        if 'ai' not in new_settings:
            new_settings['ai'] = {'openai_settings': {}, 'ollama_settings': {}}
            
        new_settings['ai']['provider'] = self.provider_selector.currentText().lower()
        new_settings['ai']['openai_settings']['api_key'] = self.openai_key_input.text()
        new_settings['ai']['ollama_settings']['host'] = self.ollama_host_input.text()
        new_settings['ai']['ollama_settings']['model'] = self.ollama_model_input.text()
        
        # We'll store the ElevenLabs key here now for consistency.
        new_settings['ai']['elevenlabs_api_key'] = self.elevenlabs_key_input.text()

        # Remove the old, redundant api_keys block if it exists
        if 'api_keys' in new_settings:
            del new_settings['api_keys']

        # --- Save other settings as before ---
        new_settings['proactivity']['enabled'] = self.proactivity_enabled_checkbox.isChecked()
        new_settings['proactivity']['frequency_seconds'] = self.frequency_slider.value() * 30
        new_settings['context_awareness']['enabled'] = self.context_enabled_checkbox.isChecked()
        new_settings['voice']['enabled'] = self.voice_enabled_checkbox.isChecked()
        new_settings['voice']['voice_id'] = self.voice_id_input.text()
        new_settings['audio_input']['mic_device_index'] = self.mic_selector.currentIndex() if self.mic_selector.isEnabled() else None
        new_settings['ai_personality']['system_prompt'] = self.system_prompt_input.toPlainText()

        # Update the internal settings object before saving and emitting
        self.settings = new_settings

        save_settings(self.settings)
        print("Settings saved to config.json.")
        
        self.settings_updated.emit(self.settings)
        self.accept()