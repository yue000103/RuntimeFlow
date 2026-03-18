"""RuntimeFlow 录制引擎 — 捕获鼠标与键盘事件"""

import time
import threading
from typing import List

from pynput import mouse, keyboard

from runtimeflow.models import Event, EventType


class Recorder:

    def __init__(self) -> None:
        self._events: List[Event] = []
        self._lock = threading.Lock()
        self._recording = False
        self._start_time: float = 0.0
        self._mouse_listener: mouse.Listener | None = None
        self._keyboard_listener: keyboard.Listener | None = None
        self._last_move_time: float = 0.0
        self._pending_move: Event | None = None

    def _elapsed_ms(self) -> float:
        return (time.perf_counter() - self._start_time) * 1000

    def _on_move(self, x: int, y: int) -> None:
        if not self._recording:
            return
        now = self._elapsed_ms()
        evt = Event(EventType.MOUSE_MOVE, now, x=int(x), y=int(y))
        with self._lock:
            if not self._recording:
                return
            if now - self._last_move_time >= 50:
                if self._pending_move is not None:
                    self._events.append(self._pending_move)
                    self._pending_move = None
                self._events.append(evt)
                self._last_move_time = now
            else:
                self._pending_move = evt

    def _on_click(self, x: int, y: int, button, pressed: bool) -> None:
        if not self._recording:
            return
        with self._lock:
            if not self._recording:
                return
            if self._pending_move is not None:
                self._events.append(self._pending_move)
                self._pending_move = None
            self._events.append(Event(
                EventType.MOUSE_CLICK, self._elapsed_ms(),
                x=int(x), y=int(y), button=str(button), pressed=pressed,
            ))

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        if not self._recording:
            return
        with self._lock:
            if not self._recording:
                return
            if self._pending_move is not None:
                self._events.append(self._pending_move)
                self._pending_move = None
            self._events.append(Event(
                EventType.MOUSE_SCROLL, self._elapsed_ms(),
                x=int(x), y=int(y), dx=int(dx), dy=int(dy),
            ))

    @staticmethod
    def _serialize_key(key) -> str:
        """序列化按键：普通字符去引号，特殊键保留 Key.xxx 格式"""
        s = str(key)
        if s.startswith("'") and s.endswith("'"):
            return s[1:-1]
        return s

    def _on_press(self, key) -> None:
        if not self._recording:
            return
        if key == keyboard.Key.f9:
            self.stop()
            return
        with self._lock:
            if self._recording:
                self._events.append(Event(
                    EventType.KEY_PRESS, self._elapsed_ms(),
                    key=self._serialize_key(key),
                ))

    def _on_release(self, key) -> None:
        if not self._recording:
            return
        if key == keyboard.Key.f9:
            return
        with self._lock:
            if self._recording:
                self._events.append(Event(
                    EventType.KEY_RELEASE, self._elapsed_ms(),
                    key=self._serialize_key(key),
                ))

    def start(self) -> None:
        if self._recording:
            return
        self._events.clear()
        self._pending_move = None
        self._last_move_time = 0.0
        self._start_time = time.perf_counter()
        self._recording = True
        self._mouse_listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll,
        )
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._mouse_listener.start()
        self._keyboard_listener.start()

    def stop(self) -> None:
        if not self._recording:
            return
        self._recording = False
        with self._lock:
            if self._pending_move is not None:
                self._events.append(self._pending_move)
                self._pending_move = None
        if self._mouse_listener:
            self._mouse_listener.stop()
        if self._keyboard_listener:
            self._keyboard_listener.stop()

    def get_events(self) -> List[Event]:
        with self._lock:
            return list(self._events)

    def is_recording(self) -> bool:
        return self._recording