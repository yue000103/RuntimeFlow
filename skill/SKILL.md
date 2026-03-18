---
name: runtimeflow
description: 桌面操作录制与回放工具。录制鼠标/键盘事件为可复用 skill，在相同环境下精确回放。支持 Windows 和 Linux。
metadata: {"openclaw":{"os":["win32","linux"],"requires":{"bins":["python"]},"emoji":"🖱️"}}
---

# RuntimeFlow

桌面操作录制与回放工具。将鼠标/键盘操作录制为 JSON skill 文件，在相同桌面环境下精确回放。支持 Windows 和 Linux（X11）。

## 平台要求

- **Windows**：
  - 方式 1：下载 runtimeflow.exe（无需安装 Python）
  - 方式 2：安装 Python 后 `pip install runtimeflow`

- **Linux（X11 图形会话）**：
  - 必须在 X11 桌面环境中运行（不支持 Wayland、无头服务器、纯 SSH 终端）
  - 需要 DISPLAY 环境变量
  - 需安装 xdotool：
    ```bash
    sudo apt install xdotool   # Debian/Ubuntu
    sudo pacman -S xdotool     # Arch
    sudo dnf install xdotool   # Fedora
    ```

- **WSL**：首次运行自动在 Windows 侧创建 venv 并安装 runtimeflow，无需手动配置。前提是 Windows 侧已安装 Python。

## 命令

**Windows exe 用户**：
```bash
runtimeflow.exe record <name>
runtimeflow.exe play <name>
runtimeflow.exe list
runtimeflow.exe info <name>
```

**Python 安装用户**：
```bash
python -m runtimeflow record <name>
# 或
runtimeflow record <name>
```

### 录制

```bash
python -m runtimeflow record <name>
```

- 3 秒倒计时后开始录制
- 用户执行桌面操作（鼠标移动/点击/滚轮、键盘输入）
- 按 F9 停止录制
- 自动保存到 `~/.runtimeflow/skills/`
- 命令会阻塞直到用户按 F9，这是正常行为

使用此命令前，务必告知用户：
1. 倒计时结束后开始录制
2. 按 F9 停止录制
3. 录制期间所有鼠标和键盘操作都会被捕获

### 回放

```bash
python -m runtimeflow play <name>
```

- 加载指定 skill
- 10 秒倒计时（用户需在此期间切换到目标窗口）
- 环境校验：分辨率、DPI、窗口标题必须与录制时一致
- 校验通过后精确回放所有事件
- 按 F10 可紧急中断回放

使用此命令前，务必告知用户：
1. 需要先打开并定位到录制时的同一窗口
2. 倒计时期间切换到目标窗口
3. 按 F10 可随时中断
4. 回放期间不要触碰鼠标和键盘

环境校验失败时，命令会输出具体差异（分辨率/DPI/窗口标题/窗口位置）。根据差异提示用户调整环境后重试。

### 列出所有 skill

```bash
python -m runtimeflow list
```

返回所有已保存 skill 的名称、事件数、时长和创建时间。

### 查看 skill 详情

```bash
python -m runtimeflow info <name>
```

返回指定 skill 的完整信息，包括环境快照（平台、分辨率、DPI、窗口信息）。

## 典型场景

- 用户想自动化重复的桌面操作（填表、点击流程等）：先 record，再 play
- 用户想查看有哪些已录制的操作：用 list
- 回放前想确认录制环境：用 info 查看环境快照
- 回放失败（环境不匹配）：根据错误信息指导用户调整窗口位置/分辨率

## 限制

- 支持 Windows、Linux（X11）和 WSL，不支持 macOS 和 Wayland
- 回放要求桌面环境与录制时完全一致（分辨率、DPI、窗口标题和位置）
- 不支持图像识别、智能适配或跨环境回放
