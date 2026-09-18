import sys
import os
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import re
import threading
import json
import traceback
import numpy as np
import sounddevice as sd
from google import genai
from google.genai import types

from ui import AlfraganusUI
from gestures.gesture_controller import GestureController
from memory.memory_manager import (
    load_memory, update_memory, format_memory_for_prompt
)

# Actions
from actions.open_app import open_app, close_app, focus_app, list_installed_apps
from actions.app_controller import get_open_apps, interact_with_app
from actions.computer_control import computer_control
from actions.computer_settings import computer_settings
from actions.screen_processor import screen_process
from actions.browser_control import browser_control
from actions.file_controller import file_controller
from actions.system_monitor import system_monitor
from actions.terminal_agent import terminal_execute
from actions.youtube_video import youtube_video
from actions.weather_report import weather_action
from agent.executor import execute_plan

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"
SETTINGS_PATH = BASE_DIR / "config" / "settings.json"
PROMPT_PATH = BASE_DIR / "core" / "prompt.txt"

LIVE_MODEL = "models/gemini-2.5-flash-native-audio-latest"
FALLBACK_MODEL = "models/gemini-3.8-live"
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024


def load_api_key() -> str:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def load_system_prompt() -> str:
    try:
        base_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        memory_str = format_memory_for_prompt()
        now = datetime.now()
        time_str = now.strftime("%A, %B %d, %Y ? %H:%M")
        return f"[HOZIRGI VAQT]\n{time_str}\n\n{base_prompt}\n\n{memory_str}"
    except Exception:
        return "Siz Alfraganus AI assistentsiz. Foydalanuvchining kompyuterini to'liq boshqarasiz."


# ?? Tool Declarations ????????????????????????????????????????????????????????
TOOL_DECLARATIONS = [
    {
        "name": "open_app",
        "description": "Opens or launches any application/program on Windows (Chrome, Telegram, Code, Notepad, Calc, etc.).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {"type": "STRING", "description": "Application name"}
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "close_app",
        "description": "Closes/terminates running application.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {"type": "STRING", "description": "Application name to close"}
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "focus_app",
        "description": "Brings an already opened application/window to the foreground and focuses it.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {"type": "STRING", "description": "Application name or window title to focus"}
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "list_installed_apps",
        "description": "Scans and lists installed applications, programs, and desktop shortcuts on the PC.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Optional search filter"}
            }
        }
    },
    {
        "name": "get_open_apps",
        "description": "Detects and returns all currently open/running applications and windows on the computer screen.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "device_controller",
        "description": "Controls phones and external devices: scan_network (finds phones, Smart TVs, router, IoT on Wi-Fi), bluetooth (lists Bluetooth devices), serial (Arduino/CNC ports), wake_on_lan, send_notification (sends push notification/message to phone via Telegram @al_pc_bot), send_screen_to_phone, open_phone_app, tap, type, battery.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "scan_network, bluetooth, serial, wake_on_lan, send_notification, send_screen_to_phone, open_phone_app, tap, type, battery, status"},
                "target": {"type": "STRING", "description": "Target device name, phone app name, or message text"},
                "text": {"type": "STRING", "description": "Additional text, coordinates, or message"},
                "ip": {"type": "STRING", "description": "Device IP address"},
                "mac": {"type": "STRING", "description": "Device MAC address for Wake-on-LAN"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "change_voice_persona",
        "description": "Changes AI voice tone/persona based on age or gender: yosh_yigit (young male), katta_erkak (mature male/Jarvis), kuchli_erkak (baritone male), ayol (warm female), yosh_qiz (young girl/female).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "persona": {"type": "STRING", "description": "Target voice persona: yosh_yigit, katta_erkak, kuchli_erkak, ayol, yosh_qiz, yosh, bola, qiz, etc."}
            },
            "required": ["persona"]
        }
    },
    {
        "name": "send_telegram_bot_message",
        "description": "Sends a message directly to the user's Telegram account/bot (@al_pc_bot) without needing the desktop app open.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "text": {"type": "STRING", "description": "Message text to send to user's Telegram"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "send_telegram_bot_screenshot",
        "description": "Takes a screenshot of the PC screen and sends it as a photo to the user's Telegram bot (@al_pc_bot).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "caption": {"type": "STRING", "description": "Caption for the screenshot"}
            }
        }
    },
    {
        "name": "send_telegram_message",
        "description": "Searches for a contact, user, group, or channel in Telegram and sends them a message or opens their chat.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "recipient": {"type": "STRING", "description": "Name or username of the recipient (e.g. Oxunjon Jo'yin, Akmal, etc.)"},
                "message": {"type": "STRING", "description": "Message text to send"}
            },
            "required": ["recipient"]
        }
    },
    {
        "name": "interact_with_app",
        "description": "Interacts with an open application window: open_chat (searches and opens contact/group/channel in Telegram or WhatsApp), send_message, type, search, save, new, close, hotkey.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {"type": "STRING", "description": "Target application name (Telegram, Chrome, Notepad, Code, etc.)"},
                "action": {"type": "STRING", "description": "open_chat, send_message, type, search, save, new, close, hotkey"},
                "text": {"type": "STRING", "description": "Name of contact/chat to open, or text to type/send/search"},
                "shortcut": {"type": "STRING", "description": "Keyboard shortcut (e.g. ctrl+s, ctrl+f)"}
            },
            "required": ["app_name", "action"]
        }
    },
    {
        "name": "mouse_control",
        "description": "Comprehensive mouse controller & position tracker: get_position (returns exact X,Y coordinates, screen area, active window title, pixel color), move (smooth movement), move_rel, click, double_click, triple_click, right_click, middle_click, mouse_down, mouse_up, drag, scroll, hover, circle_highlight, click_target (AI vision click).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "get_position, move, move_rel, click, double_click, triple_click, right_click, middle_click, mouse_down, mouse_up, drag, scroll, hover, circle_highlight, click_target"},
                "x": {"type": "INTEGER", "description": "Target X coordinate"},
                "y": {"type": "INTEGER", "description": "Target Y coordinate"},
                "dx": {"type": "INTEGER", "description": "Relative X movement"},
                "dy": {"type": "INTEGER", "description": "Relative Y movement"},
                "button": {"type": "STRING", "description": "left, right, or middle"},
                "clicks": {"type": "INTEGER", "description": "Number of clicks"},
                "direction": {"type": "STRING", "description": "up, down, left, right for scroll"},
                "amount": {"type": "INTEGER", "description": "Scroll amount"},
                "duration": {"type": "NUMBER", "description": "Duration of movement in seconds"},
                "target": {"type": "STRING", "description": "Description of UI element on screen to find and click"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "computer_control",
        "description": "Controls mouse and keyboard: click, right_click, double_click, move, drag, scroll, type, press, hotkey.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "click, right_click, double_click, move, drag, scroll, type, press, hotkey"},
                "x": {"type": "INTEGER", "description": "X coordinate on screen"},
                "y": {"type": "INTEGER", "description": "Y coordinate on screen"},
                "text": {"type": "STRING", "description": "Text to type"},
                "key": {"type": "STRING", "description": "Key to press like enter, esc, space, backspace, f5"},
                "shortcut": {"type": "STRING", "description": "Combination like ctrl+c, alt+tab, win+d, ctrl+v, ctrl+a"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "computer_settings",
        "description": "Controls Windows system settings: volume_up, volume_down, mute, unmute, brightness_up, brightness_down, set_brightness, lock, sleep, restart, shutdown, cancel_shutdown, show_desktop, task_manager.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "command": {"type": "STRING", "description": "Setting command name"},
                "value": {"type": "INTEGER", "description": "Optional numeric value"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "toggle_gesture_control",
        "description": "Enables or disables hand gesture mouse control via webcam (qo'l harakatlari bilan sichqonchani boshqarishni yoqish/o'chirish).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "enabled": {"type": "BOOLEAN", "description": "true to turn ON hand tracking, false to turn OFF"}
            },
            "required": ["enabled"]
        }
    },
    {
        "name": "screen_process",
        "description": "Captures screenshot and analyzes visual contents on screen (Gemini Vision) to answer questions about what is on screen.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Question or prompt regarding the screen"}
            }
        }
    },
    {
        "name": "screen_click",
        "description": "Visually observes the screen, finds the target button, icon, link, or text element with AI Vision, moves the mouse cursor to it and clicks (click, double_click, or right_click).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "target": {"type": "STRING", "description": "Description of the UI element/button/icon/text to click (e.g. 'Yuborish tugmasi', 'Play icon', 'Close button', 'Oxunjon')"},
                "click_type": {"type": "STRING", "description": "click, double_click, right_click"}
            },
            "required": ["target"]
        }
    },
    {
        "name": "screen_type",
        "description": "Visually locates an input field/search box on screen, clicks it, and types text into it.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "target": {"type": "STRING", "description": "Description of the input field or search bar on screen"},
                "text": {"type": "STRING", "description": "Text to type"}
            },
            "required": ["target", "text"]
        }
    },
    {
        "name": "browser_control",
        "description": "Browser automation and search: search_google, open_url, new_tab, close_tab, next_tab, prev_tab, refresh, scroll_down, scroll_up.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "Action name"},
                "query": {"type": "STRING", "description": "Search query"},
                "url": {"type": "STRING", "description": "URL to open"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "file_controller",
        "description": "File and directory operations: list_files, read_file, write_file, append_file, delete_file, make_dir, search_files.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "Action name"},
                "path": {"type": "STRING", "description": "File or directory path"},
                "content": {"type": "STRING", "description": "Content for writing"},
                "query": {"type": "STRING", "description": "Search pattern"}
            },
            "required": ["action", "path"]
        }
    },
    {
        "name": "system_monitor",
        "description": "Returns current CPU, RAM, Disk, Battery, and uptime telemetry.",
        "parameters": {"type": "OBJECT", "properties": {}}
    },
    {
        "name": "terminal_execute",
        "description": "Executes PowerShell / CMD terminal commands on the computer.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "command": {"type": "STRING", "description": "PowerShell command to execute"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "youtube_video",
        "description": "Searches and plays videos/music on YouTube.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "weather_action",
        "description": "Gets current weather for any city in Uzbekistan or worldwide.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "city": {"type": "STRING", "description": "City name"}
            }
        }
    },
    {
        "name": "phone_control",
        "description": "Full phone/smartphone control via ADB (USB & Wi-Fi), Windows Phone Link, or Gemini Vision: status, battery, open_app, close_app, tap, swipe, type_text, press_key, call, send_sms, screen_vision, connect_wifi, pair_wifi, phone_link, notify.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING",
                    "description": "Action name: status, battery, open_app, close_app, tap, swipe, type_text, press_key, call, send_sms, screen_vision, connect_wifi, pair_wifi, phone_link, notify"
                },
                "app_name": {
                    "type": "STRING",
                    "description": "App name on phone (e.g. YouTube, Telegram, WhatsApp, Instagram, Camera, Gallery, Chrome, Settings, Calculator, etc.)"
                },
                "text": {
                    "type": "STRING",
                    "description": "Text to type or message body"
                },
                "phone_number": {
                    "type": "STRING",
                    "description": "Phone number for call or SMS (e.g. +998901234567)"
                },
                "ip": {
                    "type": "STRING",
                    "description": "Phone Wi-Fi IP address (e.g. 192.168.1.50)"
                },
                "port": {
                    "type": "INTEGER",
                    "description": "ADB port, default 5555"
                },
                "pairing_code": {
                    "type": "STRING",
                    "description": "Wi-Fi pairing code for Android 11+"
                },
                "x": {
                    "type": "INTEGER",
                    "description": "X coordinate for screen tap"
                },
                "y": {
                    "type": "INTEGER",
                    "description": "Y coordinate for screen tap"
                },
                "direction": {
                    "type": "STRING",
                    "description": "Swipe direction: up, down, left, right"
                },
                "key": {
                    "type": "STRING",
                    "description": "Phone hardware key: home, back, power, volume_up, volume_down, recents"
                },
                "query": {
                    "type": "STRING",
                    "description": "Question or prompt for phone screen vision analysis"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "device_controller",
        "description": "Discovers and controls connected local devices: scan_network, bluetooth, serial/arduino/cnc, wake_on_lan, phone.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {"type": "STRING", "description": "scan_network, bluetooth, serial, wake_on_lan, phone"},
                "target": {"type": "STRING", "description": "Target IP, MAC, COM port or device name"},
                "text": {"type": "STRING", "description": "Optional payload or parameter"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "agent_task",
        "description": "Executes complex multi-step tasks by autonomous planning and step-by-step execution.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "task_goal": {"type": "STRING", "description": "Detailed description of the goal"}
            },
            "required": ["task_goal"]
        }
    }
]


class AlfraganusEngine:
    def __init__(self, ui: AlfraganusUI):
        self.ui = ui
        self.api_key = load_api_key()
        self.gesture = GestureController()
        self.session = None
        self.loop = None
        self.is_running = True

        self.audio_in_queue = None
        self.out_queue = None
        self._turn_done_event = None
        self.reconnect_requested = False

    def execute_tool_call(self, name: str, args: dict) -> str:
        if self.ui:
            self.ui.log(f"? {name}: {args}", "TOOL")

        try:
            if name == "open_app":
                return open_app(args.get("app_name", ""))
            elif name == "close_app":
                return close_app(args.get("app_name", ""))
            elif name == "focus_app":
                return focus_app(args.get("app_name", ""))
            elif name == "list_installed_apps":
                return list_installed_apps(args.get("query", ""))
            elif name == "get_open_apps":
                return get_open_apps()
            elif name == "send_telegram_bot_message":
                from actions.telegram_bot_bridge import send_bot_message
                return send_bot_message(args.get("text", ""))
            elif name == "send_telegram_bot_screenshot":
                from actions.telegram_bot_bridge import send_bot_screenshot
                return send_bot_screenshot(args.get("caption", "Kompyuter ekrani"))
            elif name == "send_telegram_message":
                from actions.telegram_controller import send_telegram_message
                return send_telegram_message(recipient=args.get("recipient", ""), message=args.get("message", ""))
            elif name == "phone_control":
                from actions.phone_controller import phone_controller
                return phone_controller(**args)
            elif name == "device_controller":
                from actions.device_controller import device_controller
                return device_controller(**args)
            elif name == "interact_with_app":
                return interact_with_app(**args)
            elif name == "mouse_control":
                from actions.mouse_controller import mouse_control
                return mouse_control(**args)
            elif name == "computer_control":
                return computer_control(**args)
            elif name == "computer_settings":
                return computer_settings(**args)
            elif name == "toggle_gesture_control":
                enabled = args.get("enabled", True)
                if enabled:
                    self.gesture.enable()
                else:
                    self.gesture.disable()
                if self.ui:
                    self.ui.update_gesture_ui(enabled)
                status_str = "yoqildi" if enabled else "o'chirildi"
                return f"Qo'l harakatlari orqali boshqaruv {status_str}."
            elif name == "screen_process":
                return screen_process(args.get("query", "Ekranda nima ko'rsatilgan?"))
            elif name == "screen_click":
                from actions.screen_processor import screen_click
                return screen_click(target=args.get("target", ""), click_type=args.get("click_type", "click"))
            elif name == "screen_type":
                from actions.screen_processor import screen_type
                return screen_type(target=args.get("target", ""), text=args.get("text", ""))
            elif name == "browser_control":
                return browser_control(**args)
            elif name == "file_controller":
                return file_controller(**args)
            elif name == "system_monitor":
                return system_monitor()
            elif name == "terminal_execute":
                return terminal_execute(args.get("command", ""))
            elif name == "youtube_video":
                return youtube_video(query=args.get("query", ""))
            elif name == "weather_action":
                return weather_action(city=args.get("city", "Toshkent"))
            elif name == "change_voice_persona":
                from actions.voice_persona import change_voice_persona
                res = change_voice_persona(args.get("persona", "katta_erkak"))
                self.reconnect_requested = True
                return res
            elif name == "agent_task":
                return execute_plan(args.get("task_goal", ""))
            else:
                return f"Noma'lum tool: {name}"
        except Exception as e:
            return f"Xatolik: {e}"

    def _build_config(self) -> types.LiveConnectConfig:
        voice = "Charon"
        try:
            if SETTINGS_PATH.exists():
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    voice = json.load(f).get("voice_name", "Charon")
        except Exception:
            pass

        return types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            output_audio_transcription={},
            input_audio_transcription={},
            system_instruction=load_system_prompt(),
            tools=[{"function_declarations": TOOL_DECLARATIONS}],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice
                    )
                )
            ),
            session_resumption=types.SessionResumptionConfig()
        )

    async def _send_realtime(self):
        while self.is_running:
            try:
                msg = await self.out_queue.get()
                if self.session:
                    await self.session.send_realtime_input(media=msg)
            except Exception:
                break

    async def _listen_audio(self):
        loop = asyncio.get_event_loop()

        def _callback(indata, frames, time_info, status):
            if not self.is_running:
                return
            if self.ui and (self.ui.mic_muted or self.ui.speaking):
                return
            if self.out_queue and self.loop:
                # Ovozni farqlash va shovqinni kamaytirish filtri
                audio_arr = np.frombuffer(indata, dtype=np.int16)
                pcm_data = indata.tobytes()
                msg = {"data": pcm_data, "mime_type": "audio/pcm"}
                self.loop.call_soon_threadsafe(
                    lambda m=msg: self.out_queue.put_nowait(m) if not self.out_queue.full() else None
                )

        stream = sd.InputStream(
            samplerate=SEND_SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=CHUNK_SIZE,
            callback=_callback
        )
        stream.start()

        try:
            while self.is_running:
                await asyncio.sleep(0.1)
        finally:
            stream.stop()
            stream.close()

    async def _receive_audio(self):
        out_buf = []
        in_buf = []

        try:
            while self.is_running:
                async for response in self.session.receive():
                    if response.server_content:
                        sc = response.server_content
                        if sc.output_transcription and sc.output_transcription.text:
                            txt = re.sub(r"<ctrl\d+>", "", sc.output_transcription.text).strip()
                            if txt and txt not in out_buf:
                                out_buf.append(txt)

                        if sc.model_turn:
                            for part in sc.model_turn.parts:
                                if part.inline_data and part.inline_data.data:
                                    if self._turn_done_event and self._turn_done_event.is_set():
                                        self._turn_done_event.clear()
                                    self.audio_in_queue.put_nowait(part.inline_data.data)
                                elif part.text and not sc.output_transcription:
                                    txt = re.sub(r"<ctrl\d+>", "", part.text).strip()
                                    if txt and not (txt.startswith("**") and txt.endswith("**")):
                                        out_buf.append(txt)

                        if sc.input_transcription and sc.input_transcription.text:
                            txt = re.sub(r"<ctrl\d+>", "", sc.input_transcription.text).strip()
                            if txt:
                                in_buf.append(txt)

                        if sc.turn_complete:
                            if self._turn_done_event:
                                self._turn_done_event.set()

                            full_in = " ".join(in_buf).strip()
                            if full_in and self.ui:
                                self.ui.log(f"Siz: {full_in}", "USER")
                            in_buf = []

                            full_out = " ".join(out_buf).strip()
                            if full_out and self.ui:
                                self.ui.log(f"Alfraganus: {full_out}", "AI")
                            out_buf = []

                            if self.reconnect_requested:
                                self.reconnect_requested = False
                                await asyncio.sleep(0.3)
                                raise ConnectionResetError("Ovoz profilini yangilash")

                    if response.tool_call:
                        fn_responses = []
                        for fc in response.tool_call.function_calls:
                            res = await asyncio.to_thread(self.execute_tool_call, fc.name, fc.args)
                            if self.ui:
                                self.ui.log(f"⚡ Natija: {res}", "RESULT")
                            fn_responses.append(
                                types.FunctionResponse(
                                    name=fc.name,
                                    id=fc.id,
                                    response={"result": res}
                                )
                            )
                        await self.session.send_tool_response(
                            function_responses=fn_responses
                        )
        except ConnectionResetError:
            raise
        except Exception as e:
            if self.ui:
                self.ui.log(f"Ulanish uzildi ({e})", "WARN")
            raise

    async def _play_audio(self):
        stream = sd.RawOutputStream(
            samplerate=RECEIVE_SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=CHUNK_SIZE
        )
        stream.start()

        try:
            while self.is_running:
                try:
                    chunk = await asyncio.wait_for(
                        self.audio_in_queue.get(),
                        timeout=0.2
                    )
                    if self.ui:
                        self.ui.set_speaking(True)
                    stream.write(chunk)
                except asyncio.TimeoutError:
                    if self.ui and self.ui.speaking:
                        self.ui.set_speaking(False)
        finally:
            if self.ui:
                self.ui.set_speaking(False)
            stream.stop()
            stream.close()

    async def run_loop(self):
        client = genai.Client(
            api_key=self.api_key,
            http_options={"api_version": "v1beta"}
        )

        active_model = LIVE_MODEL
        while self.is_running:
            try:
                if self.ui:
                    self.ui.log(f"Gemini Live ({active_model.split('/')[-1]}) serveriga ulanmoqda...", "SYSTEM")

                config = self._build_config()

                async with (
                    client.aio.live.connect(model=active_model, config=config) as session,
                    asyncio.TaskGroup() as tg,
                ):
                    self.session = session
                    self.loop = asyncio.get_event_loop()
                    self.audio_in_queue = asyncio.Queue()
                    self.out_queue = asyncio.Queue(maxsize=10)
                    self._turn_done_event = asyncio.Event()

                    if self.ui:
                        self.ui.log(f"? Gemini Live ({active_model.split('/')[-1]}) bilan aloqa o'rnatildi! Cheksiz rejim tayyor.", "SUCCESS")

                    tg.create_task(self._send_realtime())
                    tg.create_task(self._listen_audio())
                    tg.create_task(self._receive_audio())
                    tg.create_task(self._play_audio())

            except ConnectionResetError:
                if self.ui:
                    self.ui.log(f"Yangi ovoz sozlamalari qo'llanildi. Gemini Live ulanmoqda...", "SYSTEM")
                await asyncio.sleep(0.2)
            except Exception as e:
                # Switch to fallback if connection fails
                active_model = FALLBACK_MODEL if active_model == LIVE_MODEL else LIVE_MODEL
                if self.ui:
                    self.ui.log(f"Qayta ulanish ({e}). {active_model.split('/')[-1]} ga o'tilmoqda...", "RECONNECT")
                await asyncio.sleep(2)


def start_app():
    try:
        ui = AlfraganusUI()
        engine = AlfraganusEngine(ui)

        def on_gesture_toggle(enabled):
            if enabled:
                engine.gesture.enable()
            else:
                engine.gesture.disable()

        ui.on_gesture_toggle = on_gesture_toggle
        engine.gesture.set_frame_callback(ui.update_camera_frame)
        engine.gesture.start()
        engine.gesture.enable()
        ui.update_gesture_ui(True)

        # Start Telegram Bot Bridge
        from actions.telegram_bot_bridge import TelegramBotListener
        bot_listener = TelegramBotListener(engine)
        bot_listener.start()
        if ui:
            ui.log("Telegram Bot (@al_pc_bot) masofaviy boshqaruvi ulandi.", "TELEGRAM")

        def _async_worker():
            while engine.is_running:
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(engine.run_loop())
                except Exception as ex:
                    print("Async worker error:", ex)
                    time.sleep(2)

        t = threading.Thread(target=_async_worker, daemon=True)
        t.start()

        ui.run()
        engine.is_running = False
        engine.gesture.stop()
        bot_listener.stop()
    except Exception as e:
        import traceback
        err_str = traceback.format_exc()
        print("Fatal error in start_app:\n", err_str)
        try:
            with open("crash_log.txt", "a", encoding="utf-8") as f:
                f.write(f"\n[{datetime.now()}] {err_str}\n")
        except Exception:
            pass


if __name__ == "__main__":
    start_app()
