# Jarvis Mark X

Jarvis Mark X is a Python desktop voice assistant with a local Tkinter interface. It converts microphone input to text with Vosk, uses an OpenRouter model to identify the user's intent, and can speak answers through ElevenLabs.

> This project runs on Windows and uses keyboard automation for selected actions. Keep automation disabled unless you explicitly want it enabled.

## Features

- Voice input using an offline Vosk speech-recognition model
- Conversational replies using OpenRouter
- Animated desktop interface and ElevenLabs text-to-speech output
- Short-term conversation context and persistent user preferences
- Web search through SerpApi and browser-based weather lookup
- Optional Windows app launching and messaging automation
- Typed-command fallback when the Vosk model is unavailable

## Requirements

- Windows 10 or later
- Python 3.10 or later
- A microphone for voice input
- API keys for the features you want to enable

## Setup

1. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create your local environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

4. Edit `.env` and add the credentials required by your setup:

   ```dotenv
   OPENROUTER_API_KEY=your_openrouter_key
   ELEVEN_API_KEY=your_elevenlabs_key
   ELEVEN_VOICE_ID=your_voice_id
   SERPAPI_API_KEY=your_serpapi_key
   ```

5. Download a Vosk English model and extract it to the path configured by `VOSK_MODEL_PATH` (the default is `models/vosk-model-small-en-us-0.15`). The assistant falls back to typed input when this model is unavailable.

## Run

```powershell
python main.py
```

The desktop UI opens and starts listening for commands. Say or type `stop`, `mute`, `quit`, or `exit` to interrupt the current session.

## Configuration

All local configuration lives in `.env`. Start from `.env.example`.

| Variable | Purpose |
| --- | --- |
| `OPENROUTER_API_KEY` | Enables chat and intent recognition. |
| `OPENROUTER_MODEL` | OpenRouter model identifier. |
| `OPENROUTER_URL` | OpenRouter chat-completions endpoint. |
| `ELEVEN_API_KEY` | Enables spoken responses. |
| `ELEVEN_VOICE_ID` | ElevenLabs voice to use. |
| `SERPAPI_API_KEY` | Enables web-search answers. |
| `VOSK_MODEL_PATH` | Path to the local Vosk model. |
| `JARVIS_ALLOW_AUTOMATION` | Set to `1` only to enable app launching and message sending. Defaults to `0`. |

## Available actions

| Intent | What it does |
| --- | --- |
| Chat | Replies using the configured OpenRouter model. |
| Search | Searches the web with SerpApi and speaks a concise result. |
| Weather | Opens a Google weather search for the requested city. |
| Open app | Uses Windows Search to launch an application. Requires automation to be enabled. |
| Send message | Uses keyboard automation to send a message in a desktop messaging app. Requires automation to be enabled. |

## Project structure

```text
actions/       Intent handlers for search, weather, apps, and messages
core/          LLM system prompt
memory/        Runtime and long-term memory helpers
main.py        Application entry point and intent router
speech_to_text.py  Vosk microphone input
tts.py         ElevenLabs speech output
ui.py           Tkinter interface
```

## Safety and privacy

- Never commit `.env`; it contains private API keys and is ignored by Git.
- `JARVIS_ALLOW_AUTOMATION=0` is the safe default. Enable it only in a controlled desktop session.
- App launching and messaging use `pyautogui`, which controls the active Windows desktop. Keep the machine focused and do not use the computer while an automated action is running.
- Persistent memory is stored locally at `memory/memory.json` and is excluded from Git.

## License

No license has been added yet. Add one before distributing or reusing this project beyond your intended scope.
