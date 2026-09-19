import json
import os
import queue
import sys
import threading
import time

import sounddevice as sd
import vosk

MODEL_PATH = os.getenv("VOSK_MODEL_PATH", os.path.join("models", "vosk-model-small-en-us-0.15"))
_model = None
_model_load_error = None

q = queue.Queue()
stop_listening_flag = threading.Event()


def _get_model():
    global _model, _model_load_error
    if _model is not None:
        return _model
    if _model_load_error is not None:
        return None

    try:
        _model = vosk.Model(MODEL_PATH)
    except Exception as e:
        _model_load_error = str(e)
        print(f"STT WARNING: failed to load Vosk model from '{MODEL_PATH}': {e}")
        return None

    return _model


def callback(indata, frames, time_info, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def record_voice(prompt="I'm listening, sir..."):
    """
    Blocking call, returns the first recognized sentence.
    Falls back to keyboard input if Vosk model is unavailable.
    """
    print(prompt)

    model = _get_model()
    if model is None:
        try:
            typed = input("Type command (Vosk model missing): ").strip()
            if typed:
                print("You:", typed)
            return typed
        except EOFError:
            time.sleep(0.15)
            return ""

    rec = vosk.KaldiRecognizer(model, 16000)
    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        while not stop_listening_flag.is_set():
            try:
                data = q.get(timeout=0.1)
            except queue.Empty:
                continue
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text.strip():
                    print("You:", text)
                    return text
    return ""
