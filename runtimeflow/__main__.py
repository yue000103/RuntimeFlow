"""python -m runtimeflow 入口

WSL 策略：不依赖用户 PATH 中有 python.exe / runtimeflow.exe，
而是主动在 /mnt/c/ 下搜索 Windows Python，自建 venv 并安装 runtimeflow。
"""

import sys
import os
import subprocess
import glob


def _is_wsl():
    """检测是否在 WSL 环境中运行"""
    try:
        with open("/proc/version") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False


# ── WSL 自举 ──────────────────────────────────────────────

_PYTHON_SEARCH = [
    "/mnt/c/Python3*/python.exe",
    "/mnt/c/Program Files/Python3*/python.exe",
    "/mnt/c/Users/*/AppData/Local/Programs/Python/Python3*/python.exe",
]


def _find_windows_python():
    """在 /mnt/c/ 下搜索 Windows Python（取最新版本）"""
    for pattern in _PYTHON_SEARCH:
        matches = sorted(glob.glob(pattern), reverse=True)
        for m in matches:
            if os.path.isfile(m):
                return m
    return None


def _find_windows_home():
    """查找 Windows 用户主目录"""
    skip = {"Public", "Default", "Default User", "All Users"}
    try:
        for name in os.listdir("/mnt/c/Users"):
            if name in skip:
                continue
            p = f"/mnt/c/Users/{name}"
            if os.path.isdir(p) and os.path.isdir(f"{p}/Desktop"):
                return p
    except OSError:
        pass
    return None


def _venv_paths():
    """返回 (venv_dir, venv_python, sentinel) 三元组"""
    home = _find_windows_home()
    if not home:
        return None, None, None
    venv = f"{home}/.runtimeflow/venv"
    return venv, f"{venv}/Scripts/python.exe", f"{venv}/.installed"


def _bootstrap_venv(venv_dir, venv_python):
    """首次运行：创建 Windows venv 并安装 runtimeflow"""
    host_py = _find_windows_python()
    if not host_py:
        print("错误: 未在 /mnt/c/ 下找到 Python", file=sys.stderr)
        print("请安装 Python: https://python.org/downloads/", file=sys.stderr)
        sys.exit(1)

    print(f"首次运行，正在创建 Windows 虚拟环境…")
    print(f"  Python : {host_py}")
    print(f"  Venv   : {venv_dir}")

    os.makedirs(venv_dir, exist_ok=True)

    # wslpath 转 Windows 路径给 python.exe 用
    win_venv = subprocess.check_output(
        ["wslpath", "-w", venv_dir], text=True
    ).strip()

    subprocess.check_call([host_py, "-m", "venv", win_venv])

    # 安装 runtimeflow
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    win_project = subprocess.check_output(
        ["wslpath", "-w", project_dir], text=True
    ).strip()

    print("正在安装 runtimeflow …")
    subprocess.check_call(
        [venv_python, "-m", "pip", "install", "--quiet", win_project]
    )

    # 写标记
    with open(f"{venv_dir}/.installed", "w") as f:
        f.write("ok\n")
    print("完成。\n")


def _wsl_proxy():
    """WSL 入口：自建 venv → 通过 venv python 执行"""
    venv_dir, venv_python, sentinel = _venv_paths()
    if not venv_dir:
        print("错误: 未找到 Windows 用户目录 (/mnt/c/Users/)", file=sys.stderr)
        sys.exit(1)

    if not (os.path.exists(sentinel) and os.path.exists(venv_python)):
        _bootstrap_venv(venv_dir, venv_python)

    sys.exit(subprocess.call(
        [venv_python, "-m", "runtimeflow"] + sys.argv[1:]
    ))


if __name__ == "__main__":
    if _is_wsl():
        _wsl_proxy()
    else:
        from runtimeflow.cli import main
        main()
