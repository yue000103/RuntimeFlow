"""python -m runtimeflow 入口"""

import sys
import os
import subprocess


def _is_wsl():
    """检测是否在 WSL 环境中运行"""
    try:
        with open("/proc/version") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False


def _wsl_proxy():
    """在 WSL 中透明代理到 Windows python.exe"""
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        win_path = subprocess.check_output(
            ["wslpath", "-w", project_dir], text=True
        ).strip()
    except Exception:
        print("错误: 无法转换 WSL 路径到 Windows 路径", file=sys.stderr)
        sys.exit(1)

    env = os.environ.copy()
    env["PYTHONPATH"] = win_path

    sys.exit(subprocess.call(
        ["python.exe", "-m", "runtimeflow"] + sys.argv[1:],
        env=env,
    ))


if __name__ == "__main__":
    if _is_wsl():
        _wsl_proxy()
    else:
        from runtimeflow.cli import main
        main()
