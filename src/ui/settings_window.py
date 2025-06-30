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
from src.services.tts_provider import TTSProvider
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
        tab = QWidget(); layout = QVBoxLayout(tab)
        provider_group = QGroupBox("AI Provider"); provider_layout = QFormLayout(provider_group)
        self.provider_selector = QComboBox(); self.provider_selector.addItems(["OpenAI", "Ollama"])
        provider_layout.addRow("Provider:", self.provider_selector); layout.addWidget(provider_group)
        ai_settings = self.settings.get('ai', {}); openai_settings = ai_settings.get('openai_settings', {}); ollama_settings = ai_settings.get('ollama_settings', {})
        self.openai_group = QGroupBox("OpenAI Settings"); openai_layout = QFormLayout(self.openai_group)
        self.openai_key_input = QLineEdit(openai_settings.get('api_key', ''))
        self.openai_key_input.setEchoMode(QLineEdit.Password); openai_layout.addRow("API Key:", self.openai_key_input); layout.addWidget(self.openai_group)
        self.ollama_group = QGroupBox("Ollama Settings"); ollama_layout = QFormLayout(self.ollama_group)
        self.ollama_host_input = QLineEdit(ollama_settings.get('host', 'http://localhost:11434'))
        self.ollama_model_input = QLineEdit(ollama_settings.get('model', 'llama3'))
        ollama_layout.addRow("Host:", self.ollama_host_input); ollama_layout.addRow("Model Name:", self.ollama_model_input); layout.addWidget(self.ollama_group)
        self.elevenlabs_group = QGroupBox("ElevenLabs TTS Settings"); eleven_layout = QFormLayout(self.elevenlabs_group)
        self.elevenlabs_key_input = QLineEdit(ai_settings.get('elevenlabs_api_key', ''))
        self.elevenlabs_key_input.setEchoMode(QLineEdit.Password); eleven_layout.addRow("API Key:", self.elevenlabs_key_input); layout.addWidget(self.elevenlabs_group)
        layout.addStretch(); self.tabs.addTab(tab, "AI & Services")
        self.provider_selector.currentTextChanged.connect(self.toggle_ai_settings_visibility)
        current_provider = ai_settings.get('provider', 'openai'); self.provider_selector.setCurrentText(current_provider.capitalize())
        self.toggle_ai_settings_visibility(self.provider_selector.currentText())

    def toggle_ai_settings_visibility(self, provider_name):
        is_ollama = provider_name.lower() == "ollama"
        self.ollama_group.setVisible(is_ollama)
        self.openai_group.setVisible(not is_ollama)
        self.elevenlabs_group.setVisible(True)

    def create_behavior_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab); pro_group = QGroupBox("Proactivity"); pro_layout = QFormLayout(pro_group)
        self.proactivity_enabled_checkbox = QCheckBox(); self.proactivity_enabled_checkbox.setChecked(self.settings.get('proactivity', {}).get('enabled', False))
        pro_layout.addRow("Enable Proactive Messages:", self.proactivity_enabled_checkbox)
        self.frequency_slider = QSlider(Qt.Horizontal); self.frequency_slider.setMinimum(1); self.frequency_slider.setMaximum(120)
        self.frequency_slider.setValue(self.settings.get('proactivity', {}).get('frequency_seconds', 60) // 30)
        self.frequency_label = QLabel(f"{self.settings.get('proactivity', {}).get('frequency_seconds', 60)} seconds")
        self.frequency_slider.valueChanged.connect(self.update_frequency_label)
        freq_v_layout = QVBoxLayout(); freq_v_layout.addWidget(self.frequency_slider); freq_v_layout.addWidget(self.frequency_label)
        pro_layout.addRow("Message Frequency:", freq_v_layout); layout.addWidget(pro_group)
        context_group = QGroupBox("Context Awareness"); context_layout = QFormLayout(context_group)
        self.context_enabled_checkbox = QCheckBox()
        self.context_enabled_checkbox.setChecked(self.settings.get('context_awareness', {}).get('enabled', False))
        context_layout.addRow("Enable Active Window Awareness:", self.context_enabled_checkbox)
        layout.addWidget(context_group); layout.addStretch(); self.tabs.addTab(tab, "Behavior")

    def update_frequency_label(self, value):
        seconds = value * 30; self.frequency_label.setText(f"{seconds} seconds")

    def create_audio_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        input_group = QGroupBox("Audio Input (Microphone)"); input_layout = QFormLayout(input_group)
        self.mic_selector = QComboBox()
        self.local_voices = [] 
        try:
            self.mic_selector.addItems(STTProvider.list_microphones())
            saved_index = self.settings.get('audio_input', {}).get('mic_device_index')
            if saved_index is not None and 0 <= saved_index < self.mic_selector.count(): self.mic_selector.setCurrentIndex(saved_index)
            elif self.mic_selector.count() > 0: self.mic_selector.setCurrentIndex(0)
        except Exception as e:
            self.mic_selector.addItem("Error"); self.mic_selector.setEnabled(False)
        input_layout.addRow("Input Device:", self.mic_selector)
        self.always_on_checkbox = QCheckBox(); self.always_on_checkbox.setChecked(self.settings.get('audio_input', {}).get('always_on_listening', False))
        input_layout.addRow('Enable "Always-On" Listening:', self.always_on_checkbox)
        layout.addWidget(input_group)
        output_group = QGroupBox("Audio Output (Text-to-Speech)"); output_layout = QFormLayout(output_group)
        self.voice_enabled_checkbox = QCheckBox(); self.voice_enabled_checkbox.setChecked(self.settings.get('voice',{}).get('enabled', False))
        output_layout.addRow("Enable Voice Output:", self.voice_enabled_checkbox)
        self.tts_provider_selector = QComboBox(); self.tts_provider_selector.addItems(["ElevenLabs", "Local"])
        output_layout.addRow("TTS Engine:", self.tts_provider_selector)
        self.elevenlabs_voice_id_input = QLineEdit(self.settings.get('voice',{}).get('elevenlabs_settings',{}).get('voice_id',''))
        self.elevenlabs_voice_id_label = QLabel("ElevenLabs Voice ID:")
        output_layout.addRow(self.elevenlabs_voice_id_label, self.elevenlabs_voice_id_input)
        self.local_voice_selector = QComboBox()
        self.local_voice_label = QLabel("Local Voice:")
        try:
            self.local_voices = TTSProvider.list_local_voices()
            voice_names = [v.name for v in self.local_voices]
            self.local_voice_selector.addItems(voice_names)
            saved_local_voice_id = self.settings.get('voice', {}).get('local_tts_settings', {}).get('voice_id')
            if saved_local_voice_id:
                for i, voice in enumerate(self.local_voices):
                    if voice.id == saved_local_voice_id: self.local_voice_selector.setCurrentIndex(i); break
        except Exception as e:
            self.local_voice_selector.addItem("Error"); self.local_voice_selector.setEnabled(False)
        output_layout.addRow(self.local_voice_label, self.local_voice_selector)
        self.tts_provider_selector.currentTextChanged.connect(self.toggle_tts_settings_visibility)
        self.toggle_tts_settings_visibility(self.settings.get('voice',{}).get('tts_provider', 'elevenlabs').capitalize())
        self.tts_provider_selector.setCurrentText(self.settings.get('voice',{}).get('tts_provider', 'elevenlabs').capitalize())
        layout.addWidget(output_group); layout.addStretch(); self.tabs.addTab(tab, "Audio")
        
    def toggle_tts_settings_visibility(self, provider_name):
        is_local = provider_name.lower() == "local"
        self.local_voice_label.setVisible(is_local); self.local_voice_selector.setVisible(is_local)
        self.elevenlabs_voice_id_label.setVisible(not is_local); self.elevenlabs_voice_id_input.setVisible(not is_local)

    def create_personality_tab(self):
        tab = QWidget(); layout = QFormLayout(tab); layout.addRow(QLabel("<b>AI Personality</b>"))
        layout.addRow(QLabel("Define the AI's core identity and rules.")); self.system_prompt_input = QTextEdit()
        self.system_prompt_input.setPlainText(self.settings.get('ai_personality',{}).get('system_prompt', ''))
        self.system_prompt_input.setAcceptRichText(False); self.system_prompt_input.setFixedHeight(150)
        layout.addRow(self.system_prompt_input); self.tabs.addTab(tab, "Personality")

    # --- REVISED and ROBUST save_and_close method ---
    def save_and_close(self):
        s = self.settings

        # Ensure all necessary nested dictionaries exist before writing to them
        s.setdefault('ai', {}).setdefault('openai_settings', {})
        s['ai'].setdefault('ollama_settings', {})
        s.setdefault('proactivity', {})
        s.setdefault('context_awareness', {})
        s.setdefault('voice', {}).setdefault('elevenlabs_settings', {})
        s['voice'].setdefault('local_tts_settings', {})
        s.setdefault('audio_input', {})
        s.setdefault('ai_personality', {})
        
        # Now we can safely assign values
        s['ai']['provider'] = self.provider_selector.currentText().lower()
        s['ai']['openai_settings']['api_key'] = self.openai_key_input.text()
        s['ai']['ollama_settings']['host'] = self.ollama_host_input.text()
        s['ai']['ollama_settings']['model'] = self.ollama_model_input.text()
        s['ai']['elevenlabs_api_key'] = self.elevenlabs_key_input.text()
        
        s['proactivity']['enabled'] = self.proactivity_enabled_checkbox.isChecked()
        s['proactivity']['frequency_seconds'] = self.frequency_slider.value() * 30
        
        s['context_awareness']['enabled'] = self.context_enabled_checkbox.isChecked()
        
        s['voice']['enabled'] = self.voice_enabled_checkbox.isChecked()
        s['voice']['tts_provider'] = self.tts_provider_selector.currentText().lower()
        s['voice']['elevenlabs_settings']['voice_id'] = self.elevenlabs_voice_id_input.text()
        
        selected_local_index = self.local_voice_selector.currentIndex()
        if self.local_voices and selected_local_index < len(self.local_voices):
            s['voice']['local_tts_settings']['voice_id'] = self.local_voices[selected_local_index].id
        
        s['audio_input']['mic_device_index'] = self.mic_selector.currentIndex() if self.mic_selector.isEnabled() else None
        s['audio_input']['always_on_listening'] = self.always_on_checkbox.isChecked()
        
        s['ai_personality']['system_prompt'] = self.system_prompt_input.toPlainText()
        
        save_settings(s)
        print("Settings saved successfully.")
        
        self.settings_updated.emit(s)
        self.accept()