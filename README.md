# Proactive AI Companion

A desktop AI companion with proactive engagement, context awareness, and multi-modal voice interaction, built in Python and PyQt5. This application provides a floating, ambient UI that can initiate conversations, respond to text and voice, and provide context-aware assistance based on the user's active window.

 <!-- Or a real screenshot of your app! -->

## ✨ Features

- **Proactive Engagement:** The AI periodically starts conversations or offers relevant tips.
- **Multi-Modal Interaction:** Communicate via text or voice (click-to-talk and "always-on" modes).
- **Hybrid Voice System:** Supports high-quality cloud TTS (ElevenLabs) and a reliable, offline local system voice.
- **Configurable AI Brain:** Switch between cloud (OpenAI) and local (Ollama) AI providers.
- **Context Awareness:** AI suggestions are tailored to the application you're currently using.
- **Conversational Memory:** Remembers the last few turns of a conversation for natural follow-up.
- **Robust UI:** A draggable, animated doughnut overlay that provides clear visual feedback for its status (On, Off, TTS Error, Listening).
- **Comprehensive Settings Panel:** A full GUI to manage API keys, AI providers, voice preferences, proactive behavior, and microphone selection.
- **Resilient and Maintainable:** Gracefully handles API errors and provides detailed technical and conversational logs.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- `git`
- An active internet connection (for API access and dependency installation)
- A working microphone

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/jestie/proactive-ai-companion.git
    cd proactive-ai-companion
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    # On Windows
    python -m venv venv
    .\venv\Scripts\activate

    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **(Crucial) Configure the Application:**
    - The first time you run the app, it will automatically create a `config.json` file for you.
    - Open the newly created `config.json` file.
    - Add your secret API keys for **OpenAI** and **ElevenLabs**.
    - The application will not function correctly without these keys.

5.  **Run the application:**
    ```bash
    python main.py
    ```
    On first launch, right-click the overlay, go to **Settings**, and configure your AI provider, microphone, and voice preferences.

## ⚙️ Configuration

The `config.json` file allows for detailed customization:

- **`ai`**: Choose between `openai` and `ollama` providers and enter the relevant settings.
- **`proactivity`**: Enable/disable proactive messages and set their frequency.
- **`voice`**: Choose between `elevenlabs` and `local` TTS, and configure voice IDs.
- **`ai_personality`**: Write a custom system prompt to define your companion's character.
- **`context_awareness`**: Toggle whether the AI knows about your active application.
- **`audio_input`**: Select your microphone and toggle "Always-On" listening mode.

## 📝 Logging

The application generates two log files in the `logs/` directory for debugging and review:
- `technical.log`: Contains detailed information about application startup, API calls, and errors.
- `conversation.log`: Provides a clean, timestamped transcript of all conversations with the AI.