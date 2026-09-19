import io
import os
import threading

import requests
import sounddevice as sd
import soundfile as sf

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency fallback
    def load_dotenv(*args, **kwargs):
        return False


load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "").strip()
VOICE_ID = os.getenv("ELEVEN_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb").strip()
ELEVEN_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech"
REQUEST_TIMEOUT = 20

stop_speaking_flag = threading.Event()


def edge_speak(text: str, ui=None, blocking=False):
    if not text or not text.strip():
        return

    finished_event = threading.Event()

    def _thread():
        if ui:
            ui.start_speaking()
        stop_speaking_flag.clear()

        try:
            if not ELEVEN_API_KEY:
                print("TTS disabled: ELEVEN_API_KEY is not set.")
                return

            url = f"{ELEVEN_TTS_URL}/{VOICE_ID}"
            headers = {
                "xi-api-key": ELEVEN_API_KEY,
                "Content-Type": "application/json",
            }
            payload = {
                "text": text.strip(),
                "voice_settings": {
                    "stability": 0.55,
                    "similarity_boost": 0.85,
                },
            }

            response = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            audio_data = io.BytesIO(response.content)
            data, samplerate = sf.read(audio_data, dtype="float32")

            channels = data.shape[1] if len(data.shape) > 1 else 1
            with sd.OutputStream(
                samplerate=samplerate,
                channels=channels,
                dtype="float32",
            ) as stream:
                block_size = 1024
                for start in range(0, len(data), block_size):
                    if stop_speaking_flag.is_set():
                        break
                    stream.write(data[start:start + block_size])

        except Exception as e:
            print("VOICE ERROR:", e)
        finally:
            if ui:
                ui.stop_speaking()
            finished_event.set()

    threading.Thread(target=_thread, daemon=True).start()

    if blocking:
        finished_event.wait()


def stop_speaking():
    stop_speaking_flag.set()
