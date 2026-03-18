"""RuntimeFlow 回放引擎"""

import threading
import time
from typing import List, Optional

import pyautogui
from pynput.keyboard import Controller as KeyboardController, Key, KeyCode
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Controller as MouseController, Button

from runtimeflow.models import Event, EventType


class Player:
    """事件回放引擎"""

    def __init__(self):
        self._playing = False
        self._stop_flag = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._mouse = MouseController()
        self._keyboard = KeyboardController()
        self._hotkey_listener: Optional[KeyboardListener] = None

    def play(self, events: List[Event], speed_ratio: float = 1.0) -> None:
        """按时间顺序回放事件列表"""
        if self._playing:
            return
        self._stop_flag.clear()
        pyautogui.FAILSAFE = True
        self._start_hotkey_listener()
        self._thread = threading.Thread(
            target=self._replay_loop,
            args=(events, speed_ratio),
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """紧急中断回放"""
        self._stop_flag.set()
        self._stop_hotkey_listener()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def is_playing(self) -> bool:
        """返回当前是否正在回放"""
        return self._playing

    # --- 内部方法 ---

    def _replay_loop(self, events: List[Event], speed_ratio: float) -> None:
        self._playing = True
        try:
            for i, event in enumerate(events):
                if self._stop_flag.is_set():
                    break
                self._dispatch(event)
                if i < len(events) - 1:
                    delay_ms = (events[i + 1].timestamp_ms - event.timestamp_ms) / speed_ratio
                    self._precise_wait(delay_ms)
        finally:
            self._playing = False
            self._stop_hotkey_listener()

    def _precise_wait(self, delay_ms: float) -> None:
        """混合等待策略：大间隔 sleep，最后几毫秒忙等待"""
        if delay_ms <= 0:
            return
        delay_s = delay_ms / 1000.0
        target = time.perf_counter() + delay_s
        sleep_until = target - 0.005  # 留 5ms 给忙等待
        while time.perf_counter() < sleep_until:
            if self._stop_flag.is_set():
                return
            remaining = sleep_until - time.perf_counter()
            time.sleep(min(remaining, 0.01))
        while time.perf_counter() < target:
            if self._stop_flag.is_set():
                return

    def _dispatch(self, event: Event) -> None:
        t = event.event_type
        if t == EventType.MOUSE_MOVE:
            pyautogui.moveTo(event.x, event.y)
        elif t == EventType.MOUSE_CLICK:
            btn = self._resolve_button(event.button)
            if event.pressed:
                self._mouse.press(btn)
            else:
                self._mouse.release(btn)
        elif t == EventType.MOUSE_SCROLL:
            self._mouse.scroll(event.dx or 0, event.dy or 0)
        elif t == EventType.KEY_PRESS:
            self._keyboard.press(self._resolve_key(event.key))
        elif t == EventType.KEY_RELEASE:
            self._keyboard.release(self._resolve_key(event.key))

    @staticmethod
    def _resolve_key(key_str: Optional[str]):
        """反序列化按键：Key.enter → pynput Key 枚举，单字符 → KeyCode"""
        if not key_str:
            return KeyCode.from_char(" ")
        if key_str.startswith("Key."):
            return getattr(Key, key_str[4:])
        return KeyCode.from_char(key_str)

    @staticmethod
    def _resolve_button(button_str: Optional[str]) -> Button:
        if not button_str:
            return Button.left
        if button_str.startswith("Button."):
            return getattr(Button, button_str[7:])
        return getattr(Button, button_str, Button.left)

    def _start_hotkey_listener(self) -> None:
        def on_press(key):
            if key == Key.f10:
                self.stop()
        self._hotkey_listener = KeyboardListener(on_press=on_press)
        self._hotkey_listener.start()

    def _stop_hotkey_listener(self) -> None:
        if self._hotkey_listener:
            self._hotkey_listener.stop()
            self._hotkey_listener = None