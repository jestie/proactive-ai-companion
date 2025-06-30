#
# File: main.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

import sys; import os; import logging
from PyQt5.QtWidgets import QApplication
from src.core.settings_manager import load_settings
from src.core.app_logic import CoreService
from src.ui.overlay_window import OverlayWindow

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir): os.makedirs(log_dir)
    tech_logger = logging.getLogger("technical"); tech_logger.setLevel(logging.INFO)
    tech_handler = logging.FileHandler(os.path.join(log_dir, "technical.log"), mode='a', encoding='utf-8')
    tech_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s'))
    tech_logger.addHandler(tech_handler)
    conv_logger = logging.getLogger("conversation"); conv_logger.setLevel(logging.INFO)
    conv_handler = logging.FileHandler(os.path.join(log_dir, "conversation.log"), mode='a', encoding='utf-8')
    conv_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    conv_logger.addHandler(conv_handler)
    tech_logger.info("="*50 + "\n" + " "*15 + "Application Starting Up..." + "\n" + "="*50)
    conv_logger.info("="*20 + " New Session Started " + "="*20)

def main():
    setup_logging()
    app = QApplication(sys.argv)
    settings = load_settings()
    if not settings:
        logging.getLogger("technical").critical("Could not load settings. Exiting.")
        sys.exit(1)
    core_service = CoreService(settings)
    overlay = OverlayWindow(settings, core_service)
    overlay.state_toggled.connect(core_service.set_state)
    overlay.user_message_sent.connect(core_service.process_user_message)
    overlay.voice_input_triggered.connect(core_service.handle_voice_input)
    core_service.message_ready_for_ui.connect(overlay.append_message)
    core_service.new_conversation_started.connect(overlay.clear_chat_display)
    core_service.tts_status_updated.connect(overlay.update_tts_status)
    core_service.is_listening_updated.connect(overlay.update_listening_status)
    overlay.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()