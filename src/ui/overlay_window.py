#
# File: src/ui/overlay_window.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

from PyQt5.QtWidgets import QWidget, QMenu, QApplication, QLineEdit, QPushButton, QTextBrowser, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QTimer, QSize
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
        
        self.setFixedSize(100, 100)
        self.move(1600, 800)

        self.chat_layout = QVBoxLayout(self)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.chat_layout)

        self.chat_history_view = QTextBrowser(self)
        self.chat_history_view.setReadOnly(True)
        self.chat_history_view.setOpenExternalLinks(True)
        self.chat_history_view.setStyleSheet("""
            QTextBrowser { background-color: transparent; border: none; color: white; font-size: 14px; }
            QScrollBar:vertical { border: none; background: rgba(0,0,0,0.3); width: 10px; margin: 0px 0px 0px 0px; }
            QScrollBar::handle:vertical { background: rgba(255,255,255,0.4); min-height: 20px; border-radius: 5px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)
        self.chat_history_view.hide()

        self.input_field = QLineEdit(self)
        self.input_field.setStyleSheet("QLineEdit { background-color: rgba(0, 0, 0, 0.5); border: 1px solid rgba(255, 255, 255, 0.4); border-radius: 5px; color: white; font-size: 14px; padding: 5px; }")
        self.input_field.hide()
        self.input_field.returnPressed.connect(self._handle_user_input)

        self.chat_layout.addWidget(self.chat_history_view)
        self.chat_layout.addWidget(self.input_field)

        self.mic_button = QPushButton("🎤", self)
        # We will position it dynamically in enter_chat_mode and hide_message
        self.mic_button.setCursor(Qt.PointingHandCursor)
        self.mic_button.clicked.connect(self.voice_input_triggered.emit)
        self.update_mic_style() # Set initial style

        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.hide_message)
        self.inactivity_timeout_ms = 45000

        self.old_pos = self.pos()

    # --- NEW METHOD to dynamically style the mic button ---
    def update_mic_style(self):
        if self.is_listening:
            # Red color when listening
            style = "color: red; background-color: rgba(255, 100, 100, 0.3); border-radius: 15px;"
        else:
            # Normal style
            style = "color: white; background-color: transparent; border: none;"
        
        self.mic_button.setStyleSheet(f"""
            QPushButton {{
                {style}
                font-size: 20px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 15px;
            }}
        """)

    def update_tts_status(self, is_ok):
        self.has_tts_error = not is_ok; self.update()

    def update_listening_status(self, is_listening):
        self.is_listening = is_listening
        self.update_mic_style() # Update the mic color
        if is_listening:
            self.append_message({'role': 'system', 'content': "<i>Listening...</i>"})
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.is_chat_mode:
            chat_color = QColor(0, 20, 80, 220); painter.setBrush(QBrush(chat_color))
            painter.setPen(QPen(Qt.NoPen)); painter.drawRoundedRect(self.rect(), 15.0, 15.0)
        else:
            text = "On"
            if not self.is_on: base_color = QColor(200, 40, 40); text = "Off"
            elif self.has_tts_error: base_color = QColor(220, 180, 0); text = "Warn"
            else: base_color = QColor(0, 80, 200)
            base_color.setAlpha(220 if self.underMouse() else 180)
            painter.setBrush(QBrush(base_color)); painter.setPen(QPen(Qt.NoPen))
            painter.drawEllipse(self.rect())
            hole_rect = self.rect().adjusted(25, 25, -25, -25)
            painter.setCompositionMode(QPainter.CompositionMode_Clear); painter.drawEllipse(hole_rect)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.setPen(QPen(Qt.white)); painter.setFont(QFont("Arial", 16, QFont.Bold))
            painter.drawText(self.rect(), Qt.AlignCenter, text)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.mic_button.geometry().contains(event.pos()) or self.is_chat_mode:
                if not self.is_chat_mode: self.display_manual_prompt()
                else: self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.is_chat_mode:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y()); self.old_pos = event.globalPos()
            
    def contextMenuEvent(self, event):
        context_menu = QMenu(self); toggle_action = context_menu.addAction("Turn Off" if self.is_on else "Turn On")
        settings_action = context_menu.addAction("Settings"); context_menu.addSeparator(); quit_action = context_menu.addAction("Quit")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        if action == toggle_action: self.is_on = not self.is_on; self.state_toggled.emit(self.is_on); self.update()
        elif action == settings_action: self.open_settings()
        elif action == quit_action: QApplication.instance().quit()

    def open_settings(self):
        if self.settings_window is None:
            from src.ui.settings_window import SettingsWindow
            self.settings_window = SettingsWindow(self.settings, self.core_service, self)
        self.settings_window.show(); self.settings_window.activateWindow()

    def clear_chat_display(self):
        self.chat_history_view.clear()

    def append_message(self, message_data):
        role = message_data.get('role'); content = message_data.get('content', '').replace('\n', '<br/>')
        if not self.is_chat_mode: self.enter_chat_mode()
        
        if role == 'assistant': html = f"<div style='color: #aaddff; padding-bottom: 8px;'><b>Companion:</b><br/>{content}</div>"
        elif role == 'user': html = f"<div style='color: #ffffff; padding-bottom: 8px;'><b>You:</b><br/>{content}</div>"
        else: html = f"<div style='color: #cccccc; padding-bottom: 8px;'><i>{content}</i></div>"
        
        self.chat_history_view.append(html)
        self.chat_history_view.verticalScrollBar().setValue(self.chat_history_view.verticalScrollBar().maximum())
        self.inactivity_timer.start(self.inactivity_timeout_ms)

    def display_manual_prompt(self):
        self.clear_chat_display(); self.append_message({'role': 'system', 'content': "What's on your mind?"})

    def enter_chat_mode(self):
        self.is_chat_mode = True
        self.setMinimumSize(QSize(380, 200)); self.setMaximumSize(QSize(16777215, 16777215))
        self.resize(380, 400)
        self.chat_history_view.show(); self.input_field.show()
        # --- Make mic visible and position it inside the chat window ---
        self.mic_button.setGeometry(self.width() - 40, 5, 30, 30)
        self.mic_button.show()
        self.input_field.setFocus(); self.update()

    def hide_message(self):
        self.is_chat_mode = False
        self.inactivity_timer.stop(); self.chat_history_view.hide(); self.input_field.hide()
        self.setFixedSize(100, 100)
        # --- Position mic correctly for doughnut mode ---
        self.mic_button.setGeometry(65, 5, 30, 30)
        self.mic_button.show()
        self.update()

    def _handle_user_input(self):
        user_text = self.input_field.text().strip()
        if user_text:
            self.inactivity_timer.stop(); self.append_message({'role': 'user', 'content': user_text})
            self.user_message_sent.emit(user_text)
            self.input_field.clear(); self.append_message({'role': 'system', 'content': "<i>Thinking...</i>"})