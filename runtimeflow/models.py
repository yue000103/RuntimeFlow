"""RuntimeFlow 核心数据模型 — 所有模块的共享基础，请勿修改"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Any
import time


class EventType(Enum):
    """事件类型枚举"""
    MOUSE_MOVE = "mouse_move"
    MOUSE_CLICK = "mouse_click"
    MOUSE_SCROLL = "mouse_scroll"
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"


@dataclass
class Event:
    """单个输入事件"""
    event_type: EventType
    timestamp_ms: float          # 相对于录制开始的毫秒偏移
    x: Optional[int] = None     # 鼠标 x 坐标
    y: Optional[int] = None     # 鼠标 y 坐标
    button: Optional[str] = None # 鼠标按键名称
    pressed: Optional[bool] = None  # 按下=True / 抬起=False
    dx: Optional[int] = None    # 滚轮水平偏移
    dy: Optional[int] = None    # 滚轮垂直偏移
    key: Optional[str] = None   # 键盘按键名称

    def to_dict(self) -> dict:
        d = asdict(self)
        d["event_type"] = self.event_type.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Event":
        d = dict(d)
        d["event_type"] = EventType(d["event_type"])
        return cls(**d)


@dataclass
class EnvironmentSnapshot:
    """录制时的环境快照"""
    platform: str               # 系统平台 e.g. "Windows-11"
    screen_width: int           # 屏幕宽度
    screen_height: int          # 屏幕高度
    dpi_scale: float            # DPI 缩放比例
    window_title: str           # 前台窗口标题
    window_x: int               # 窗口左上角 x
    window_y: int               # 窗口左上角 y
    window_width: int           # 窗口宽度
    window_height: int          # 窗口高度

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "EnvironmentSnapshot":
        return cls(**d)


@dataclass
class Flow:
    """一次完整的录制流程"""
    name: str
    events: List[Event]
    environment: EnvironmentSnapshot
    created_at: str             # ISO 格式时间戳
    duration_ms: float          # 总时长（毫秒）
    event_count: int = 0

    def __post_init__(self):
        self.event_count = len(self.events)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "events": [e.to_dict() for e in self.events],
            "environment": self.environment.to_dict(),
            "created_at": self.created_at,
            "duration_ms": self.duration_ms,
            "event_count": self.event_count,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Flow":
        events = [Event.from_dict(e) for e in d["events"]]
        env = EnvironmentSnapshot.from_dict(d["environment"])
        return cls(
            name=d["name"],
            events=events,
            environment=env,
            created_at=d["created_at"],
            duration_ms=d["duration_ms"],
        )
