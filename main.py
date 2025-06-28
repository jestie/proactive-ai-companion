#
# File: main.py
#
# ----- PASTE THIS ENTIRE BLOCK INTO YOUR FILE -----
#

import sys
from PyQt5.QtWidgets import QApplication

from src.core.settings_manager import load_settings
from src.core.app_logic import CoreService
from src.ui.overlay_window import OverlayWindow

def main():
    app = QApplication(sys.argv)
    
    settings = load_settings()
    if not settings:
        print("Could not load settings. Exiting.")
        sys.exit(1)

    core_service = CoreService(settings)
    
    overlay = OverlayWindow(settings, core_service)
    
    # --- Connect signals and slots ---
    overlay.state_toggled.connect(core_service.set_state)
    overlay.user_message_sent.connect(core_service.process_user_message)
    core_service.message_ready_for_ui.connect(overlay.display_message)
    core_service.tts_status_updated.connect(overlay.update_tts_status)
    
    # --- ADD THE NEW VOICE CONNECTIONS ---
    overlay.voice_input_triggered.connect(core_service.handle_voice_input)
    core_service.is_listening_updated.connect(overlay.update_listening_status)
    
    overlay.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()