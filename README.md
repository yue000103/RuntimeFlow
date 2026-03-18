# RuntimeFlow

桌面操作录制与回放工具。将鼠标/键盘操作录制为 JSON skill 文件，在相同桌面环境下精确回放。

## 支持平台

| 平台 | 状态 | 备注 |
|------|------|------|
| Windows | ✅ | 支持 exe 独立运行或 pip 安装 |
| Linux (X11) | ✅ | 需要 X11 图形会话 + xdotool |
| WSL | ✅ | 自动代理到 Windows 侧执行 |
| macOS | ❌ | 不支持 |
| Wayland | ❌ | 不支持 |

## 安装

### Windows

**方式 1：下载 exe（推荐，无需 Python）**

从 Releases 下载 `runtimeflow.exe`，放入 PATH 目录即可。

**方式 2：pip 安装**

```bash
pip install runtimeflow
```

### Linux (X11)

```bash
# 安装 xdotool
sudo apt install xdotool   # Debian/Ubuntu
sudo pacman -S xdotool     # Arch
sudo dnf install xdotool   # Fedora

# 安装 RuntimeFlow
pip install runtimeflow
```

必须在 X11 图形桌面环境中运行，需要 `DISPLAY` 环境变量。

### WSL

```bash
pip install runtimeflow
```

WSL 下会自动代理到 Windows 侧执行（优先使用 `runtimeflow.exe`，其次 `python.exe`）。

## 使用

```bash
# 录制操作（F9 停止）
runtimeflow record <name>

# 回放操作（F10 中断）
runtimeflow play <name>

# 列出所有 skill
runtimeflow list

# 查看 skill 详情
runtimeflow info <name>
```

也可以用 `python -m runtimeflow` 代替 `runtimeflow`。

## 打包 exe

```bash
pip install pyinstaller
python build_exe.py
```

生成 `dist/runtimeflow.exe`。

## 常见问题

**Linux 上报错 xdotool not found**
安装 xdotool：`sudo apt install xdotool`

**Wayland 环境无法使用**
RuntimeFlow 依赖 X11 协议，Wayland 不支持。可尝试在 Xwayland 兼容模式下运行，但不保证稳定。

**WSL 代理失败**
确保 Windows 侧 PATH 中有 `runtimeflow.exe` 或 `python.exe`（且已安装 RuntimeFlow 依赖）。

**回放时环境校验失败**
回放要求分辨率、DPI、窗口标题与录制时完全一致，窗口位置允许 ±5px 偏差。根据错误提示调整环境后重试。

## OpenClaw Skill

本项目可作为 [OpenClaw](https://github.com/anthropics/openclaw) skill 使用，配置见 `skill/SKILL.md`。
