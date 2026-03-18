# RuntimeFlow — 架构记忆

## 项目是什么

Windows 桌面操作录制与回放工具。录制鼠标/键盘事件，存为可复用的 skill（JSON），在相同环境下高精度回放。
不做 AI、不做视觉识别、不做跨环境适配。本质是：动作录制器 + Flow 播放器 + Skill 存储器。

版本：0.1.0（MVP 已完成）
Python 3.12 | Windows Only

## 项目结构

```
RuntimeFlow/
├── runtimeflow/
│   ├── models.py        # 核心数据模型：Event, EventType, EnvironmentSnapshot, Flow
│   ├── recorder.py      # 录制引擎：pynput 捕获事件，F9 停止，50ms 鼠标节流
│   ├── player.py        # 回放引擎：精确计时回放，F10 中断，混合等待策略
│   ├── environment.py   # 环境快照与校验：分辨率/DPI/窗口位置，±5px 容差
│   ├── storage.py       # JSON 持久化：skills/ 目录，时间戳版本命名
│   ├── cli.py           # Click CLI：record / play / list / info 四个命令
│   ├── __init__.py
│   └── __main__.py      # python -m runtimeflow 入口
├── skills/              # skill 存储目录（JSON 文件）
├── 最小MVP.md           # 产品需求文档
├── chat_dev_a.md        # 开发者A聊天记录（录制引擎）
├── chat_dev_b.md        # 开发者B聊天记录（回放引擎）
├── chat_dev_c.md        # 开发者C聊天记录（环境+存储+CLI）
└── requirements.txt     # pynput, pyautogui, pywin32, click
```

## 架构分层

```
CLI (cli.py)  →  用户交互层，Click 框架
    ↓
Recorder / Player / Storage  →  核心引擎层
    ↓
Environment  →  环境安全层（回放前校验）
    ↓
Models  →  数据基础层（Event, Flow, EnvironmentSnapshot）
```

## 核心设计决策

1. **事件模型**：统一 Event dataclass，5 种 EventType（MOUSE_MOVE/CLICK/SCROLL, KEY_PRESS/RELEASE），timestamp_ms 为相对录制起点的毫秒偏移
2. **录制节流**：鼠标移动 50ms 内只保留最后一次，点击/滚轮事件会先 flush pending move
3. **回放计时**：`time.perf_counter()` 精确计时，大间隔 sleep + 最后 5ms 忙等待的混合策略
4. **环境强校验**：平台/分辨率/DPI/窗口标题必须完全一致，窗口位置允许 ±5px，不通过直接拒绝回放
5. **存储格式**：`{name}_{YYYYMMDD_HHMMSS}.json`，load 时取同名最新文件
6. **线程安全**：Recorder 用 threading.Lock 保护事件列表，Player 用 threading.Event 做 stop flag

## CLI 用法

```bash
python -m runtimeflow record <name>   # 3秒倒计时后开始录制，F9 停止
python -m runtimeflow play <name>     # 环境校验 → 3秒倒计时 → 回放，F10 中断
python -m runtimeflow list            # 列出所有 skill
python -m runtimeflow info <name>     # 查看 skill 详情
```

## 依赖

- pynput：键鼠监听与控制
- pyautogui：鼠标移动回放（moveTo）+ FAILSAFE
- pywin32：获取前台窗口信息（win32gui）
- click：CLI 框架

## 开发历史

项目由架构师设计，分配给 3 个开发者并行实现（2026-03-17）：
- 开发者A → recorder.py
- 开发者B → player.py
- 开发者C → environment.py + storage.py + cli.py

models.py 由架构师预先定义，作为所有模块的共享契约。

## MVP 边界（明确不做）

不做图像识别、元素识别、OCR、页面状态判断、异常分支处理、位置漂移纠偏、跨环境适配、智能决策。

## 当前状态

MVP 功能完整，所有模块已实现并通过验证。skills/ 目录为空（尚未有实际录制的 skill）。
