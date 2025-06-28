#
# File: src/ui/overlay_window.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

from PyQt5.QtWidgets import QWidget, QMenu, QApplication, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont

class OverlayWindow(QWidget):
    state_toggled = pyqtSignal(bool)
    user_message_sent = pyqtSignal(str)
    voice_input_triggered = pyqtSignal()

    def __init__(self, settings, core_service):
        super().__init__()
        self.settings = settings
        self.core_service = core_service
        self.is_on = True
        self.is_chat_mode = False
        self.has_tts_error = False
        self.is_listening = False
        self.settings_window = None
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setGeometry(1600, 800, 100, 100)
        
        self.message_label = QLineEdit(self)
        self.message_label.setReadOnly(True)
        self.message_label.setStyleSheet("color: white; background-color: transparent; border: none; padding: 10px; font-size: 14px;")
        self.message_label.hide()

        self.input_field = QLineEdit(self)
        self.input_field.setStyleSheet("QLineEdit { background-color: rgba(0, 0, 0, 0.5); border: 1px solid rgba(255, 255, 255, 0.4); border-radius: 5px; color: white; font-size: 14px; padding: 5px; }")
        self.input_field.hide()
        self.input_field.returnPressed.connect(self._handle_user_input)

        # --- NEW: Microphone Icon Button ---
        self.mic_button = QPushButton("🎤", self)
        self.mic_button.setGeometry(65, 5, 30, 30) # Position top-right
        self.mic_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 15px;
            }
        """)
        self.mic_button.setCursor(Qt.PointingHandCursor)
        self.mic_button.clicked.connect(self.voice_input_triggered.emit) # Connect to existing signal

        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.hide_message)
        self.inactivity_timeout_ms = 15000

        self.old_pos = self.pos()

    def update_tts_status(self, is_ok):
        self.has_tts_error = not is_ok
        self.update()

    def update_listening_status(self, is_listening):
        self.is_listening = is_listening
        if is_listening:
            self.display_message("<i>Listening...</i>")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.is_chat_mode:
            chat_color = QColor(0, 20, 80, 220)
            painter.setBrush(QBrush(chat_color))
            painter.setPen(QPen(Qt.NoPen))
            painter.drawRoundedRect(self.rect(), 15.0, 15.0)
        else:
            text = "On"
            if not self.is_on:
                base_color = QColor(200, 40, 40)
                text = "Off"
            elif self.has_tts_error:
                base_color = QColor(220, 180, 0)
                text = "Warn"
            else:
                base_color = QColor(0, 80, 200)
            if self.underMouse():
                base_color.setAlpha(220)
            else:
                base_color.setAlpha(180)
            painter.setBrush(QBrush(base_color))
            painter.setPen(QPen(Qt.NoPen))
            painter.drawEllipse(self.rect())
            hole_rect = self.rect().adjusted(25, 25, -25, -25)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.drawEllipse(hole_rect)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.setPen(QPen(Qt.white))
            painter.setFont(QFont("Arial", 16, QFont.Bold))
            painter.drawText(self.rect(), Qt.AlignCenter, text)

    # --- REMOVED: mouseDoubleClickEvent is no longer needed ---

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if the click was outside the mic button's area
            if not self.mic_button.geometry().contains(event.pos()) or self.is_chat_mode:
                if not self.is_chat_mode:
                    self.display_manual_prompt()
                else:
                    self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.is_chat_mode:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
            
    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        toggle_action_text = "Turn Off" if self.is_on else "Turn On"
        toggle_action = context_menu.addAction(toggle_action_text)
        settings_action = context_menu.addAction("Settings")
        context_menu.addSeparator()
        quit_action = context_menu.addAction("Quit")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        if action == toggle_action:
            self.is_on = not self.is_on
            self.state_toggled.emit(self.is_on)
            self.update()
        elif action == settings_action:
            self.open_settings()
        elif action == quit_action:
            QApplication.instance().quit()

    def open_settings(self):
        if self.settings_window is None:
            from src.ui.settings_window import SettingsWindow
            self.settings_window = SettingsWindow(self.settings, self.core_service, self)
        self.settings_window.show()
        self.settings_window.activateWindow()

    def display_manual_prompt(self):
        self.display_message("What's on your mind?")

    def display_message(self, text):
        self.mic_button.hide() # Hide mic button in chat mode
        self.inactivity_timer.stop()
        self.is_chat_mode = True
        self.resize(350, 150)
        self.message_label.setText(text)
        self.message_label.setGeometry(5, 5, self.width() - 10, self.height() - 60)
        self.message_label.show()
        if not self.is_listening:
            self.input_field.setGeometry(10, self.height() - 45, self.width() - 20, 30)
            self.input_field.show()
            self.input_field.setFocus()
        else:
            self.input_field.hide()
        self.update()
        if not self.is_listening:
            self.inactivity_timer.start(self.inactivity_timeout_ms)

    def hide_message(self):
        self.mic_button.show() # Show mic button in idle mode
        self.is_chat_mode = False
        self.inactivity_timer.stop()
        self.input_field.hide()
        self.message_label.hide()
        self.resize(100, 100)
        self.update()

    def _handle_user_input(self):
        user_text = self.input_field.text().strip()
        if user_text:
            self.inactivity_timer.stop()
            self.user_message_sent.emit(user_text)
            self.input_field.clear()
            self.message_label.setText("<i>Thinking...</i>")
            self.inactivity_timer.start(self.inactivity_timeout_ms)