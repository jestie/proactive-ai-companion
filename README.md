# Proactive AI Companion

A prototype for a cross-platform desktop application that provides a floating, proactive AI companion. This ambient assistant lives on your desktop, initiating conversations, providing context-aware suggestions, and responding to both text and voice commands.

![UI Mockup](httpsa://i.imgur.com/k6lP09r.png)

## ✨ Features

*   **Proactive Engagement:** The AI doesn't just wait; it initiates conversations based on timers and context.
*   **Context Awareness:** Knows which application you're using and can tailor its suggestions accordingly.
*   **Multi-Modal Interaction:**
    *   **Voice Output:** High-quality text-to-speech powered by ElevenLabs.
    *   **Voice Input:** Speech-to-text allows you to talk to your companion.
    *   **Text Chat:** A classic chat interface for typed commands.
*   **Flexible AI Backend:**
    *   Supports the OpenAI API.
    *   Supports local, private LLMs via an Ollama instance.
*   **Highly Configurable:** A full settings panel to manage AI providers, API keys, voice, microphone, and AI personality via a custom system prompt.
*   **Intuitive UI:** A stylish, draggable "doughnut" overlay that communicates its status (On, Off, TTS Error, Listening) with colors and icons.

## 🛠️ Technical Stack

*   **Frontend UI:** Python with PyQt5
*   **AI Services:** OpenAI API, Ollama
*   **Text-to-Speech:** ElevenLabs API
*   **Speech-to-Text:** Google Speech Recognition API (via `SpeechRecognition` library)
*   **System Interaction:** `PyGetWindow` for context awareness

## 🚀 Getting Started

Follow these instructions to get the Proactive AI Companion running on your local machine.

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
cd YOUR_REPOSITORY_NAME


###  2. Create and Activate a Virtual Environment
This keeps your project's dependencies isolated.

On Windows:
python -m venv venv
.\venv\Scripts\activate

On macOS / Linux:
python3 -m venv venv
source venv/bin/activate


### 3. Install Dependencies
pip install -r requirements.txt


### 4. Configure the Application
This is the most important step. You must provide your own API keys.
Copy the template file to create your personal configuration file. This file is safely ignored by Git and will not be uploaded.
Generated bash
# On Windows
copy config.template.json config.json

# On macOS / Linux
cp config.template.json config.json

Now, open the new config.json file and paste in your secret API keys from OpenAI and ElevenLabs.
Customize other settings like the voice_id or default system_prompt as desired.


### 5. Install FFmpeg (for Voice Output)
The ElevenLabs library requires FFmpeg to play audio.
Windows: Download the "essentials" build from gyan.dev/ffmpeg/builds/ and add its bin folder to your system's PATH.
macOS: brew install ffmpeg
Linux: sudo apt update && sudo apt install ffmpeg


### 6. Run the Application
python main.py