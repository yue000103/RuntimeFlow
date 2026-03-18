"""环境检测与校验"""

import platform
import subprocess

from runtimeflow.models import EnvironmentSnapshot

_IS_WINDOWS = platform.system() == "Windows"
_IS_LINUX = platform.system() == "Linux"

if _IS_WINDOWS:
    import ctypes
    import win32gui


def _ensure_dpi_awareness():
    """确保进程 DPI 感知一致，获取物理分辨率而非缩放值"""
    if not _IS_WINDOWS:
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-Monitor DPI Aware
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


_ensure_dpi_awareness()


def _capture_windows() -> EnvironmentSnapshot:
    """Windows 环境捕获"""
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    try:
        dpi_scale = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    except Exception:
        dpi_scale = 1.0

    hwnd = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(hwnd)
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)

    return EnvironmentSnapshot(
        platform=platform.platform(),
        screen_width=screen_width,
        screen_height=screen_height,
        dpi_scale=dpi_scale,
        window_title=window_title,
        window_x=left,
        window_y=top,
        window_width=right - left,
        window_height=bottom - top,
    )


def _capture_linux() -> EnvironmentSnapshot:
    """Linux 环境捕获（依赖 xdotool）"""
    import pyautogui
    screen_width, screen_height = pyautogui.size()

    # DPI: 尝试从 xrdb 获取
    dpi_scale = 1.0
    try:
        out = subprocess.check_output(["xrdb", "-query"], text=True, timeout=3)
        for line in out.splitlines():
            if "dpi" in line.lower():
                val = float(line.split(":")[-1].strip())
                dpi_scale = val / 96.0
                break
    except Exception:
        pass

    # 窗口信息: xdotool
    window_title = ""
    window_x, window_y, window_width, window_height = 0, 0, 0, 0
    try:
        wid = subprocess.check_output(
            ["xdotool", "getactivewindow"], text=True, timeout=3
        ).strip()
        window_title = subprocess.check_output(
            ["xdotool", "getwindowname", wid], text=True, timeout=3
        ).strip()
        geo = subprocess.check_output(
            ["xdotool", "getwindowgeometry", "--shell", wid], text=True, timeout=3
        )
        geo_vars = {}
        for line in geo.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                geo_vars[k.strip()] = int(v.strip())
        window_x = geo_vars.get("X", 0)
        window_y = geo_vars.get("Y", 0)
        window_width = geo_vars.get("WIDTH", 0)
        window_height = geo_vars.get("HEIGHT", 0)
    except Exception:
        pass

    return EnvironmentSnapshot(
        platform=platform.platform(),
        screen_width=screen_width,
        screen_height=screen_height,
        dpi_scale=dpi_scale,
        window_title=window_title,
        window_x=window_x,
        window_y=window_y,
        window_width=window_width,
        window_height=window_height,
    )


def capture_environment() -> EnvironmentSnapshot:
    """捕获当前桌面环境快照"""
    if _IS_WINDOWS:
        return _capture_windows()
    elif _IS_LINUX:
        return _capture_linux()
    else:
        raise RuntimeError(f"不支持的平台: {platform.system()}")


def validate_environment(snapshot: EnvironmentSnapshot) -> tuple[bool, list[str]]:
    """校验当前环境是否与快照一致
    Returns: (是否通过, 差异描述列表)
    """
    current = capture_environment()
    diffs = []

    if current.platform != snapshot.platform:
        diffs.append(f"平台不一致: 当前={current.platform}, 期望={snapshot.platform}")

    if current.screen_width != snapshot.screen_width or current.screen_height != snapshot.screen_height:
        diffs.append(
            f"分辨率不一致: 当前={current.screen_width}x{current.screen_height}, "
            f"期望={snapshot.screen_width}x{snapshot.screen_height}"
        )

    if current.dpi_scale != snapshot.dpi_scale:
        diffs.append(f"DPI不一致: 当前={current.dpi_scale}, 期望={snapshot.dpi_scale}")

    if current.window_title != snapshot.window_title:
        diffs.append(f"窗口标题不一致: 当前='{current.window_title}', 期望='{snapshot.window_title}'")

    tolerance = 5
    for attr, label in [
        ("window_x", "窗口X"), ("window_y", "窗口Y"),
        ("window_width", "窗口宽度"), ("window_height", "窗口高度"),
    ]:
        cur_val = getattr(current, attr)
        snap_val = getattr(snapshot, attr)
        if abs(cur_val - snap_val) > tolerance:
            diffs.append(f"{label}偏差过大: 当前={cur_val}, 期望={snap_val}, 容差=±{tolerance}px")

    return (len(diffs) == 0, diffs)
