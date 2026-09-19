import re
import time

import pyautogui

from tts import edge_speak

REQUIRED_PARAMS = ["receiver", "message_text"]

PLATFORM_ALIASES = {
    "WhatsApp": ["whatsapp", "whats app", "watsapp", "whatsup", "what's app"],
    "Telegram": ["telegram"],
    "Signal": ["signal"],
    "Discord": ["discord"],
    "Messenger": ["messenger", "facebook messenger", "fb messenger"],
}


def _clean_text(value: str | None, limit: int) -> str:
    if not value:
        return ""
    return value.replace("\n", " ").replace("\r", " ").strip()[:limit]


def _compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _normalize_platform(raw_platform: str, raw_receiver: str) -> tuple[str, str]:
    """
    Returns (platform, receiver). If platform includes accidental trailing receiver
    text (e.g. 'whatsappdost singh'), normalize platform and recover receiver when possible.
    """
    receiver = _clean_text(raw_receiver, 80)
    platform_input = _clean_text(raw_platform, 80)
    if not platform_input:
        return "WhatsApp", receiver

    platform_lower = platform_input.lower()
    platform_compact = _compact(platform_input)

    for canonical, aliases in PLATFORM_ALIASES.items():
        for alias in aliases:
            alias_compact = _compact(alias)

            if platform_compact == alias_compact:
                return canonical, receiver

            if platform_compact.startswith(alias_compact):
                # If receiver is missing and user said e.g. "whatsapp dost singh",
                # recover the remainder as receiver.
                if not receiver and platform_lower.startswith(alias):
                    remainder = platform_input[len(alias):].strip(" :-,")
                    if remainder:
                        receiver = _clean_text(remainder, 80)
                return canonical, receiver

    return _clean_text(platform_input, 40), receiver

def send_message(parameters: dict, response: str | None = None, player=None, session_memory=None) -> bool:
    """
    Send a message via Windows app (WhatsApp, Telegram, etc.)

    Multi-step support: asks for missing parameters using temporary memory.

    Expected parameters:
        - receiver (str)
        - message_text (str)
        - platform (str, optional, default: "WhatsApp")
    """

    if session_memory is None:
        msg = "Session memory missing, cannot proceed."
        if player:
            player.write_log(msg)
        edge_speak(msg, player)
        return False

    if parameters:
        session_memory.update_parameters(parameters)

    for param in REQUIRED_PARAMS:
        value = session_memory.get_parameter(param)
        if not value:
        
            session_memory.set_current_question(param)
            question_text = ""
            if param == "receiver":
                question_text = "Sir, who should I send the message to?"
            elif param == "message_text":
                question_text = "Sir, what should I say?"
            else:
                question_text = f"Sir, please provide {param}."

            if player:
                player.write_log(f"AI: {question_text}")
            edge_speak(question_text, player)
            return False  

    receiver_raw = session_memory.get_parameter("receiver")
    platform_raw = session_memory.get_parameter("platform")
    message_text = _clean_text(session_memory.get_parameter("message_text"), 1000)
    platform, receiver = _normalize_platform(platform_raw, receiver_raw)

    if not receiver:
        session_memory.set_current_question("receiver")
        question_text = "Sir, who should I send the message to?"
        if player:
            player.write_log(f"AI: {question_text}")
        edge_speak(question_text, player)
        return False

    if response:
        if player:
            player.write_log(response)
        edge_speak(response, player)

    try:
        pyautogui.PAUSE = 0.1

        pyautogui.press("win")
        time.sleep(0.3)
        pyautogui.write(platform, interval=0.03)
        pyautogui.press("enter")
        time.sleep(0.6)

        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.2)
        pyautogui.write(receiver, interval=0.03)
        time.sleep(0.2)
        pyautogui.press("enter")
        time.sleep(0.2)

        pyautogui.write(message_text, interval=0.03)
        pyautogui.press("enter")

        session_memory.clear_current_question()
        session_memory.clear_pending_intent()
        session_memory.update_parameters({})  

        # -----------------------------
        # Log success
        # -----------------------------
        success_msg = f"Sir, I attempted to send your message to {receiver} via {platform}."
        if player:
            player.write_log(success_msg)
        edge_speak(success_msg, player)

        return True

    except Exception as e:
        msg = f"Sir, I failed to send the message. ({e})"
        if player:
            player.write_log(msg)
        edge_speak(msg, player)
        return False
