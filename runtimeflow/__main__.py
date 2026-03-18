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
    """在 WSL 中透明代理到 Windows 侧执行，优先使用 exe"""
    args = sys.argv[1:]

    # 优先尝试 runtimeflow.exe
    try:
        ret = subprocess.call(["runtimeflow.exe"] + args)
        sys.exit(ret)
    except FileNotFoundError:
        pass

    # 回退到 python.exe -m runtimeflow
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        win_path = subprocess.check_output(
            ["wslpath", "-w", project_dir], text=True
        ).strip()
    except Exception:
        print("错误: Windows 侧未找到 runtimeflow.exe 或 python.exe", file=sys.stderr)
        print("请确保 Windows PATH 中有 runtimeflow.exe 或 python.exe", file=sys.stderr)
        sys.exit(1)

    env = os.environ.copy()
    env["PYTHONPATH"] = win_path

    try:
        ret = subprocess.call(
            ["python.exe", "-m", "runtimeflow"] + args,
            env=env,
        )
        sys.exit(ret)
    except FileNotFoundError:
        print("错误: Windows 侧未找到 runtimeflow.exe 或 python.exe", file=sys.stderr)
        print("请确保 Windows PATH 中有 runtimeflow.exe 或 python.exe", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if _is_wsl():
        _wsl_proxy()
    else:
        from runtimeflow.cli import main
        main()
